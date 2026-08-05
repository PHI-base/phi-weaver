#!/usr/bin/env python3
"""Refresh the vendored ontology `.obo` files from their upstream GitHub repos.

The bundled ontologies under ``data/`` are what `map_phenotype` and `validate_ontology_ids`
resolve against **offline** (see ``data/README.md`` for why each one is vendored). Going
local costs one thing: nothing self-updates. This tool is that update, in one command —
cheap enough to run on a whim (before a curation batch, after a PHIPO release notice) and a
no-op when upstream has not moved.

Deliberately dumb: fetch, compare, write, run the two test modules. No scheduling, no
staleness heuristic, no network access from any code path a curator's normal run touches.

Two guards, because this writes over good data:
- **Plausibility.** A fetched file must parse as OBO and keep at least
  ``MIN_TERM_RATIO`` of the terms it is replacing, so a 404 page or a truncated
  download is rejected rather than vendored.
- **Visibility.** Every file's before/after (``data-version``, term count, digest) is
  printed, so the change is shown and not merely made. ``--dry-run`` shows it without
  writing.

**Do not run inside a scored benchmark run.** This is the one moment PHIPO legitimately
comes from ``github.com/PHI-base``, which also hosts the curated data repos — the answer
key. Under the benchmark sandbox's default-deny allowlist the fetch simply fails, which is
the intended outcome, not a bug to work around.

Usage::

    python3 -m phiweaver.lookup.refresh_ontologies                 # all, then tests
    python3 -m phiweaver.lookup.refresh_ontologies --dry-run       # report only
    python3 -m phiweaver.lookup.refresh_ontologies --only phipo-base.obo
"""

import argparse
import hashlib
import subprocess  # nosec - fixed argv, no shell
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, List, Optional, Sequence, Tuple

import phiweaver

DATA_DIR = Path(__file__).resolve().parent / "data"
USER_AGENT = "PHI-Weaver-refresh-ontologies/1.0 (https://github.com/PHI-base/phi-weaver)"
TIMEOUT = 60
# A fetched file replacing an existing one must keep at least this share of its terms.
# Guards against vendoring a truncated download or an error page over a good bundle.
MIN_TERM_RATIO = 0.5
# The offline resolvers that read these files. `test_map_phenotype` covers PHIPO search,
# `test_validate_ontology_ids` covers every bundled `[Term]`-block ontology.
TEST_MODULES = ("tests.test_map_phenotype", "tests.test_validate_ontology_ids")


@dataclass(frozen=True)
class Source:
    """A vendored file and the upstream artifact it is a copy of."""

    filename: str
    url: str


# Release artifacts committed to their repo roots — never the working/edit files, and never
# `phipo.obo` (it inlines GO/CHEBI imports). See data/README.md for the reasoning per file.
SOURCES: Tuple[Source, ...] = (
    Source("phipo-base.obo",
           "https://raw.githubusercontent.com/PHI-base/phipo/master/phipo-base.obo"),
    Source("phido.obo",
           "https://raw.githubusercontent.com/PHI-base/phido/master/phido.obo"),
    Source("phi-eco.obo",
           "https://raw.githubusercontent.com/PHI-base/phi-eco/master/phi-eco.obo"),
    Source("phipo_ext.obo",
           "https://raw.githubusercontent.com/PHI-base/phipo_ext/master/phipo_ext.obo"),
    Source("fypo_extension.obo",
           "https://raw.githubusercontent.com/PHI-base/canto/master/t/data/fypo_extension.obo"),
)

# Bundled files this tool cannot touch, and why — reported so their absence from the run is
# explicit rather than an apparent oversight.
UNSOURCED = {
    "pomgeneex.obo": "hand-written from curator-supplied IDs (2026-07-24); no upstream "
                     "release artifact exists",
    "phipo_extensions.tsv": "public PHI-base/canto-config, but TSV-shaped, not [Term]-block "
                            "OBO — this tool's plausibility check doesn't apply; refresh via "
                            "the curl recipe in data/README.md",
    "phibase_go_extensions.tsv": "public PHI-base/canto-config, but TSV-shaped, not [Term]-block "
                                 "OBO — refresh via the curl recipe in data/README.md",
    "phido_extensions.tsv": "public PHI-base/canto-config, but TSV-shaped, not [Term]-block "
                            "OBO — refresh via the curl recipe in data/README.md",
    "phipo_extension_relations.obo": "public PHI-base/canto-config, but [Typedef]-shaped, not "
                                     "[Term]-block OBO — refresh via the curl recipe in "
                                     "data/README.md",
}


@dataclass(frozen=True)
class Bundle:
    """What a bundle *is*, in the terms a curator judges a refresh by."""

    release: Optional[str]   # the `data-version` line, when the ontology carries one
    terms: int
    digest: str              # short sha256, so files without a data-version still compare

    def describe(self) -> str:
        return "{}, {} terms, {}".format(self.release or "no data-version",
                                        self.terms, self.digest)


def describe(text: str) -> Bundle:
    """Summarise OBO text. Header-only scan for the release; `[Term]` count for size."""
    release = None
    for line in text.splitlines():
        if line.startswith("data-version:"):
            release = line.split(":", 1)[1].strip()
            break
        if line.startswith("[Term]"):
            break                     # header is over; no data-version present
    terms = sum(1 for line in text.splitlines() if line.strip() == "[Term]")
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]
    return Bundle(release=release, terms=terms, digest=digest)


def _default_fetch(url: str) -> bytes:
    import urllib.request

    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:  # nosec - fixed host
        return resp.read()


def implausible(new: Bundle, old: Optional[Bundle]) -> Optional[str]:
    """Reason to refuse this fetch, or None. Cheap sanity, not validation — the tests do that."""
    if new.terms == 0:
        return "no [Term] blocks — not an OBO file (a 404 page? an empty response?)"
    if old is not None and new.terms < old.terms * MIN_TERM_RATIO:
        return ("{} terms would replace {} — lost more than {:.0%}, looks truncated"
                .format(new.terms, old.terms, 1 - MIN_TERM_RATIO))
    return None


@dataclass
class Result:
    """One file's outcome. `status` drives both the report and the exit code."""

    filename: str
    status: str              # unchanged | updated | would-update | new | rejected | error
    old: Optional[Bundle] = None
    new: Optional[Bundle] = None
    message: str = ""

    @property
    def failed(self) -> bool:
        return self.status in ("rejected", "error")


def refresh_one(source: Source, fetch: Callable[[str], bytes] = _default_fetch,
                data_dir: Path = DATA_DIR, dry_run: bool = False) -> Result:
    """Fetch one ontology and vendor it if it moved and looks sane."""
    path = data_dir / source.filename
    current = path.read_text(encoding="utf-8") if path.exists() else None
    old = describe(current) if current is not None else None

    try:
        raw = fetch(source.url)
    except Exception as exc:                      # noqa: BLE001 - any transport failure
        # Under the benchmark sandbox this is the expected, correct outcome.
        return Result(source.filename, "error", old=old,
                      message="fetch failed: {}: {}".format(type(exc).__name__, exc))

    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        return Result(source.filename, "rejected", old=old,
                      message="not UTF-8 text: {}".format(exc))

    if text == current:
        return Result(source.filename, "unchanged", old=old, new=old)

    new = describe(text)
    if (reason := implausible(new, old)) is not None:
        return Result(source.filename, "rejected", old=old, new=new, message=reason)

    if dry_run:
        return Result(source.filename, "would-update", old=old, new=new)

    path.write_text(text, encoding="utf-8")
    return Result(source.filename, "new" if old is None else "updated", old=old, new=new)


def refresh(sources: Sequence[Source] = SOURCES,
            fetch: Callable[[str], bytes] = _default_fetch,
            data_dir: Path = DATA_DIR, dry_run: bool = False) -> List[Result]:
    return [refresh_one(s, fetch=fetch, data_dir=data_dir, dry_run=dry_run) for s in sources]


def format_report(results: Sequence[Result], include_skipped: bool = True) -> str:
    """One line per file; before → after only where something actually differs.

    `include_skipped` names the files this tool cannot fetch — worth saying on a full run,
    noise when the caller asked for one file with `--only`.
    """
    lines = []
    for r in results:
        if r.status == "unchanged":
            lines.append("  = {:<22} unchanged ({})".format(
                r.filename, r.old.describe() if r.old else "absent"))
        elif r.status in ("updated", "would-update", "new"):
            verb = {"updated": "updated", "would-update": "would update",
                    "new": "vendored (was absent)"}[r.status]
            lines.append("  + {:<22} {}".format(r.filename, verb))
            if r.old:
                lines.append("      from: {}".format(r.old.describe()))
            lines.append("      to:   {}".format(r.new.describe() if r.new else "?"))
        else:
            lines.append("  ! {:<22} {}: {}".format(r.filename, r.status, r.message))
    if include_skipped:
        for filename, why in sorted(UNSOURCED.items()):
            lines.append("  · {:<22} skipped — {}".format(filename, why))
    return "\n".join(lines)


def run_tests(modules: Sequence[str] = TEST_MODULES) -> int:
    """Run the offline resolvers' tests, from the repo root so `tests.` imports resolve."""
    cmd = [sys.executable, "-m", "unittest", *modules]
    print("\nverifying: {}".format(" ".join(cmd)))
    return subprocess.call(cmd, cwd=str(phiweaver.repo_root()))  # nosec - fixed argv


def main(argv=None) -> int:
    p = argparse.ArgumentParser(
        description="Refresh the vendored ontology .obo files from upstream.",
        epilog="Do not run inside a scored benchmark run — this reaches github.com/PHI-base, "
               "which also hosts the curated answer key.")
    p.add_argument("--only", action="append", metavar="FILENAME",
                   help="refresh just this bundled file (repeatable)")
    p.add_argument("--dry-run", action="store_true",
                   help="report what would change; write nothing")
    p.add_argument("--no-tests", action="store_true",
                   help="skip the verification test run")
    p.add_argument("--list", action="store_true",
                   help="list the refreshable files and their upstream URLs, then exit")
    args = p.parse_args(argv)

    if args.list:
        for s in SOURCES:
            print("{:<22} {}".format(s.filename, s.url))
        for filename, why in sorted(UNSOURCED.items()):
            print("{:<22} (not refreshable — {})".format(filename, why))
        return 0

    sources = SOURCES
    if args.only:
        known = {s.filename: s for s in SOURCES}
        unknown = [f for f in args.only if f not in known]
        if unknown:
            p.error("not refreshable: {} (see --list)".format(", ".join(unknown)))
        sources = tuple(known[f] for f in args.only)

    print("Fetching {} ontolog{} from github.com/PHI-base — not for use inside a scored "
          "benchmark run.".format(len(sources), "y" if len(sources) == 1 else "ies"))
    results = refresh(sources, dry_run=args.dry_run)
    print(format_report(results, include_skipped=not args.only))

    failures = [r for r in results if r.failed]
    changed = [r for r in results if r.status in ("updated", "new")]
    would = [r for r in results if r.status == "would-update"]

    if args.dry_run:
        print("\n{} file(s) would change; nothing written.".format(len(would)))
        return 1 if failures else 0

    if not changed:
        # The common, cheap case: upstream has not released. Say so plainly — an unchanged
        # `data-version` means there is no new term a curator could annotate to yet.
        print("\nNothing moved — no upstream release since the bundled copies.")
        return 1 if failures else 0

    print("\n{} file(s) updated. Record the new date/release in "
          "phiweaver/lookup/data/README.md and commit.".format(len(changed)))
    if args.no_tests:
        return 1 if failures else 0
    rc = run_tests()
    if rc != 0:
        print("TESTS FAILED — the refreshed bundle broke a resolver. Do not commit; "
              "`git checkout -- phiweaver/lookup/data/` to restore.")
    return 1 if (failures or rc != 0) else 0


if __name__ == "__main__":
    raise SystemExit(main())
