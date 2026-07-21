#!/usr/bin/env python3
"""
map_phenotype.py — deterministic phenotype-phrase → PHIPO term search for PHI-Weaver.

Given a phenotype description (typically a phrase a curator lifted from a paper's figure
caption or results text), search the Pathogen–Host Interaction Phenotype Ontology (PHIPO)
and return the candidate terms that actually exist — with their real PHIPO IDs and labels.
It NEVER invents an ID: a phrase with no PHIPO hit is reported as "no_match", not mapped to
a guessed term.

This is the deterministic half of the caption → phenotype → PHIPO workflow (see the
phipo-mapping skill). Deciding which phrases in a caption *are* phenotypes is a reasoning
step done by the curator/agent; this tool maps a given phrase to real candidate terms, and
the companion validate_ontology_ids.py confirms the chosen ID is current.

**Offline by design** (2026-07-17; was EBI OLS). Searches the bundled `data/phipo-base.obo`
— no network. Three reasons, in order of weight:

1. **OLS search hides deprecated terms**, so a concept that once existed returns a clean
   `no_match` and looks like a virgin gap. That is exactly how PHI-base/phipo#452 was
   written unaware that PHIPO:0000503 already existed and had been obsoleted. Here obsolete
   terms are *in the file*: excluded from suggestions by default (a curator cannot annotate
   to one), but surfaced by ``--include-obsolete`` for gap analysis.
2. **The benchmark sandbox.** A bundled file needs no network during a scored run, so the
   allowlist stays default-deny with no PHIPO exception. This matters because
   `github.com/PHI-base` hosts *both* the phipo ontology **and** the curated data repos (=
   the answer key), so "ontology yes, data no" cannot be expressed at the domain level.
   PHIPO is a tool, not an answer.
3. Deterministic and fast: no network flake, no cache staleness, same result every run.

**Which file, and why it matters.** `phipo-base.obo` is the *release artifact* — what OLS
serves and (approximately) what PHI-Canto has loaded. It answers the question a curator
actually has: *can I annotate this?* The working file `phipo-edit.owl` (in a clone of
PHI-base/phipo) is **deliberately not used here**: it contains **unreleased** terms that
PHI-Canto does not have, so suggesting one would be a bug that looks like a feature. Use the
edit file for gap analysis only — see `skills/ontology-term-request/SKILL.md` step 5.

The cost is search quality: OLS is Solr-backed with stemming; the scorer here is exact >
substring > token overlap. Acceptable — lesson L7 establishes OLS's ranking is untrustworthy
anyway (it confidently returned a within-host term for an in-vitro phrase), so a human reads
every candidate regardless: favour recall (a generous ``--rows``) over clever ranking.

Design rules (see AGENTS.md, phipo-mapping / curation-qc skills):
- Never guess: only terms present in the bundled ontology are returned; "no_match" is
  explicit, never a fabricated ID.
- Obsolete terms are excluded from suggestions (curation requires current terms).
- Record provenance: source file, ontology release, UTC timestamp.
- The exit code reflects whether the *search ran*, not whether it found a match: 0 unless a
  query errored (a clean "no_match" is exit 0). The per-query `status` carries the result.

CLI:
    python3 -m phiweaver.lookup.map_phenotype "reduced virulence"
    python3 -m phiweaver.lookup.map_phenotype --file phenotype-phrases.txt --json
    python3 -m phiweaver.lookup.map_phenotype "abnormal conidiation" --rows 10
    python3 -m phiweaver.lookup.map_phenotype "deoxynivalenol absent" --include-obsolete
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import List, Optional

from phiweaver.common import utc_now
from phiweaver.lookup import gap_log, term_context, text_score
from phiweaver.lookup.text_score import tokens as _tokens  # re-exported: tests/callers use it

PHIPO_OBO_PATH = Path(__file__).resolve().parent / "data" / "phipo-base.obo"
PHIPO_PREFIX = "PHIPO:"
DEFAULT_ROWS = 5
# Minimum IDF-coverage score for a term to count as a candidate; below it, `no_match`.
# Tuned empirically (2026-07-17) against real curation phrases vs. prose/junk:
#   true matches            35–100  ("increased sensitivity to hydrogen peroxide" = 35, lowest)
#   junk / running prose     0–12.7 (shares only generic vocabulary: "to", "host", "pathogen")
#   a genuine wording gap    14.1   ("abnormal conidiation" — PHIPO says "asexual spores" and
#                                    has no "conidiation" token at all; BACKLOG tracks it)
# 20.0 sits in the wide gap between junk and true matches, and correctly leaves the wording
# gap unmatched — which is the point: `no_match` is what --log-gaps and gap detection key on,
# so it must stay reachable. See build_idf() for why an unweighted score cannot separate these.
MIN_SCORE = 20.0

_SYN_RE = re.compile(r'"([^"]*)"')


class PhenotypeSearchError(RuntimeError):
    """Raised when the bundled ontology cannot be read or parsed."""


# --- Annotation usage, from PHIPO's own `subset:` tags -----------------------------
#
# A PHIPO term can exist, be non-obsolete, and *still* be unusable as a phenotype
# annotation. PHI-Canto refuses two categories, and PHIPO marks both in the ontology
# file itself (174 tagged terms in the 2026-03-12 release):
#
#   qc_do_not_annotate (67) / qc_do_not_manually_annotate (56)
#       High-level grouping terms — "pathogenicity phenotype", "tissue phenotype",
#       "single species phenotype". Real terms, but too general to annotate to.
#   qc_extension_only (13)
#       Terms that are legal only as an annotation *extension value*, never as the
#       primary term: "reduced virulence", "loss of pathogenicity", "increased
#       virulence", "unaffected pathogenicity". These are among the most common
#       phrases in PHI-base papers, which is exactly why mislabelling them matters —
#       `reduced virulence` belongs in `infective_ability → PHIPO:0000015`, not in the
#       phenotype slot.
#
# **Why the tags and not `canto_config`.** PHI-Canto's `ontology_namespace_config`
# carries the equivalent list, but it lives in `canto_deploy.yaml`, which is gitignored
# (private repo — see data/README.md). Driving the filter from a file that is present on
# one machine and absent on another would make the same phrase return different
# candidates for different curators, which is unacceptable for reproducible curation.
# PHIPO's own subset tags ship with the committed ontology, so they are the same
# everywhere. `canto_config.do_not_annotate_subsets` remains the cross-check.
#
# NOTE (open question for PHI-base): PHI-Canto's config names GO's spellings —
# `gocheck_do_not_annotate` / `gocheck_do_not_manually_annotate` — plus
# `qc_do_not_annotate`, but NOT PHIPO's `qc_do_not_manually_annotate`. We exclude the
# latter here because PHI-Canto is a manual curation tool and 56 PHIPO terms carry it.
# Worth confirming with James/Hsin-Yu that the config omission is an oversight.
DO_NOT_ANNOTATE_SUBSETS = frozenset({
    "qc_do_not_annotate",
    "qc_do_not_manually_annotate",
    "gocheck_do_not_annotate",
    "gocheck_do_not_manually_annotate",
    "canto_root_subset",
})
EXTENSION_ONLY_SUBSETS = frozenset({"qc_extension_only"})

USAGE_PRIMARY = "primary"                # annotatable as the phenotype term
USAGE_EXTENSION_ONLY = "extension_only"  # legal only as an extension value
USAGE_GROUPING = "grouping"              # too general / not annotatable at all


def usage_of(subsets) -> str:
    """Classify a term by what PHI-Canto will let a curator do with it."""
    s = set(subsets or ())
    if s & DO_NOT_ANNOTATE_SUBSETS:
        return USAGE_GROUPING
    if s & EXTENSION_ONLY_SUBSETS:
        return USAGE_EXTENSION_ONLY
    return USAGE_PRIMARY


@dataclass(frozen=True)
class Term:
    obo_id: str
    name: str
    synonyms: tuple
    obsolete: bool = False
    subsets: tuple = ()

    @property
    def usage(self) -> str:
        return usage_of(self.subsets)


@dataclass
class Candidate:
    obo_id: str
    label: Optional[str]
    exact: bool               # phrase equals the term's label or an exact synonym
    score: float = 0.0
    obsolete: bool = False    # only ever True when --include-obsolete was passed
    usage: str = USAGE_PRIMARY


@dataclass
class PhenotypeMapping:
    query: str
    status: str                       # matched | no_match | error
    candidates: List[Candidate]
    source: Optional[str]
    retrieved_at: Optional[str]
    release: Optional[str] = None     # the ontology's data-version
    error: Optional[str] = None
    # Grouping terms that scored but were withheld as non-annotatable. Reported, never
    # silently dropped: a phrase whose only matches are grouping terms would otherwise
    # come back as a bare no_match and read as an ontology gap — the phantom-gap failure
    # this module exists to avoid (lessons L2/L8, phipo#452).
    withheld: List[Candidate] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        """The search completed without error. A clean 'no_match' is not a failure —
        never-guess means an honest empty result is success, not an error."""
        return self.status in ("matched", "no_match")

    def to_dict(self) -> dict:
        d = asdict(self)                 # nested Candidate dataclasses become dicts too
        d["ok"] = self.ok
        return d


def load_terms(path: Path = PHIPO_OBO_PATH) -> List[Term]:
    """Parse phipo-base.obo into PHIPO terms, **including obsolete ones**.

    Obsolete terms are kept here and filtered at search time: excluding them at parse would
    reproduce the OLS blind spot this module exists to remove (see the module docstring).
    """
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise PhenotypeSearchError(f"cannot read bundled PHIPO ontology {path}: {exc}")

    terms: List[Term] = []
    in_term = False
    cur: dict = {}

    def flush():
        oid = cur.get("id", "")
        name = cur.get("name", "")
        if not oid.startswith(PHIPO_PREFIX):
            return                       # keep PHIPO only (drop any imported PATO/GO/etc.)
        # PHIPO marks obsoletion two ways: an `is_obsolete: true` line, and an "obsolete "
        # label prefix. Some terms carry only the label form, so check both.
        obsolete = bool(cur.get("obsolete")) or name.lower().startswith("obsolete ")
        terms.append(Term(oid, name, tuple(cur.get("syn", [])), obsolete,
                          tuple(cur.get("subset", []))))

    for line in raw.splitlines():
        line = line.strip()
        if line.startswith("[") and line.endswith("]"):
            if in_term and cur:
                flush()
            in_term, cur = (line == "[Term]"), {}
        elif not in_term:
            continue
        elif line.startswith("id:"):
            cur["id"] = line[3:].strip()
        elif line.startswith("name:"):
            cur["name"] = line[5:].strip()
        elif line.startswith("is_obsolete:"):
            cur["obsolete"] = line.split(":", 1)[1].strip().lower() == "true"
        elif line.startswith("subset:"):
            cur.setdefault("subset", []).append(line.split(":", 1)[1].strip())
        elif line.startswith("synonym:"):
            m = _SYN_RE.search(line)
            if m:
                cur.setdefault("syn", []).append(m.group(1))
    if in_term and cur:
        flush()
    return terms


def read_release(path: Path = PHIPO_OBO_PATH) -> Optional[str]:
    """The ontology's `data-version` line — provenance for what was actually searched."""
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.startswith("data-version:"):
                return line.split(":", 1)[1].strip()
            if line.startswith("[Term]"):
                break                     # header is over; no data-version present
    except OSError:
        return None
    return None


def _texts(term: Term) -> tuple:
    return (term.name, *term.synonyms)


def build_idf(terms: List[Term]) -> dict:
    """IDF over every label + synonym in the ontology. See text_score.build_idf for why."""
    return text_score.build_idf(_texts(t) for t in terms)


def _max_idf(idf: dict) -> float:
    return text_score.max_idf(idf)


def _score(phrase: str, term: Term, idf: dict) -> float:
    return text_score.score(phrase, _texts(term), idf)


def _is_exact(phrase: str, term: Term) -> bool:
    return text_score.is_exact(phrase, _texts(term))


class PhenotypeMapper:
    """Searches the bundled PHIPO release. Terms are loaded once and reused."""

    def __init__(self, terms: Optional[List[Term]] = None,
                 path: Path = PHIPO_OBO_PATH):
        self.path = path
        self._terms = terms
        self._idf: Optional[dict] = None
        self._release: Optional[str] = None if terms is not None else read_release(path)

    @property
    def terms(self) -> List[Term]:
        if self._terms is None:
            self._terms = load_terms(self.path)
        return self._terms

    @property
    def idf(self) -> dict:
        if self._idf is None:
            self._idf = build_idf(self.terms)
        return self._idf

    def map(self, phrase: str, rows: int = DEFAULT_ROWS,
            include_obsolete: bool = False,
            min_score: float = MIN_SCORE,
            include_grouping: bool = False) -> PhenotypeMapping:
        phrase = (phrase or "").strip()
        src = str(self.path)
        if not phrase:
            return PhenotypeMapping(phrase, "no_match", [], src, None,
                                    self._release, "empty query")
        try:
            terms, idf = self.terms, self.idf
        except PhenotypeSearchError as exc:
            return PhenotypeMapping(phrase, "error", [], src, utc_now(),
                                    self._release, str(exc))
        candidates, withheld = _search(phrase, terms, idf, rows, include_obsolete,
                                       min_score, include_grouping)
        status = "matched" if candidates else "no_match"
        return PhenotypeMapping(phrase, status, candidates, src, utc_now(),
                                self._release, withheld=withheld)


def _search(phrase: str, terms: List[Term], idf: dict, rows: int = DEFAULT_ROWS,
            include_obsolete: bool = False,
            min_score: float = MIN_SCORE,
            include_grouping: bool = False) -> tuple:
    """Score every term, keep the best `rows` above `min_score`. Exact first, then by score.

    Returns `(candidates, withheld)`.

    Three exclusions, each treated differently on purpose:

    * **Obsolete** — dropped unless `include_obsolete`. A curator cannot annotate to an
      obsolete term, so suggesting one is wrong; a *gap* analysis needs to see them (the
      #452 lesson), which is what the flag is for.
    * **Grouping** (`qc_do_not_annotate` &c.) — moved to `withheld` rather than dropped,
      unless `include_grouping`. They must stay visible: a phrase whose only matches are
      grouping terms would otherwise return a bare `no_match`, which reads as an ontology
      gap and invites a duplicate term request.
    * **Extension-only** (`qc_extension_only`) — **kept as candidates and labelled**, not
      filtered. "Reduced virulence" really is PHIPO:0000015; it just belongs in
      `infective_ability → …` rather than the phenotype slot. Hiding it would turn the
      single most common PHI-base phrase into a false gap.
    """
    scored = []
    withheld = []
    for t in terms:
        if t.obsolete and not include_obsolete:
            continue
        s = _score(phrase, t, idf)
        if s < min_score:
            continue
        if t.usage == USAGE_GROUPING and not include_grouping:
            withheld.append((s, t))
        else:
            scored.append((s, t))

    def _rank(pair):
        # Exact first, then score desc, then id — deterministic for equal scores.
        return (not _is_exact(phrase, pair[1]), -pair[0], pair[1].obo_id)

    def _mk(pair):
        s, t = pair
        return Candidate(obo_id=t.obo_id, label=t.name, exact=_is_exact(phrase, t),
                         score=round(s, 2), obsolete=t.obsolete, usage=t.usage)

    scored.sort(key=_rank)
    withheld.sort(key=_rank)
    return [_mk(p) for p in scored[:rows]], [_mk(p) for p in withheld[:rows]]


def read_phrases(path: str) -> List[str]:
    """Read one phenotype phrase per line; skip blank lines and ``#`` comments."""
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    return [ln.strip() for ln in lines if ln.strip() and not ln.strip().startswith("#")]


def _append_withheld(lines: List[str], r: PhenotypeMapping) -> None:
    """Show grouping terms that matched but are not annotatable.

    Stated explicitly so a curator can tell "PHIPO has nothing for this" (a real gap,
    worth a term request) from "PHIPO has only a parent term for this" (not a gap — the
    concept exists, it is just too general, and requesting a term would duplicate it).
    """
    if not r.withheld:
        return
    lines.append("    — matched only as non-annotatable grouping term(s); NOT a gap:")
    for c in r.withheld:
        lines.append(f"        ({c.obo_id}  {c.label or ''})")


def format_human(results: List[PhenotypeMapping]) -> str:
    lines: List[str] = []
    for r in results:
        if r.status == "error":
            lines.append(f"⚠️  {r.query}  [error]")
            if r.error:
                lines.append(f"    {r.error}")
            continue
        if r.status == "no_match":
            lines.append(f"❌ {r.query}  [no PHIPO match]")
            _append_withheld(lines, r)
            continue
        rel = f" {r.release}" if r.release else ""
        lines.append(f"✅ {r.query}  (offline via phipo-base.obo{rel})")
        for c in r.candidates:
            mark = "★" if c.exact else "•"
            note = ""
            if c.obsolete:
                note = "  ⚠️ OBSOLETE — not annotatable; gap-analysis only"
            elif c.usage == USAGE_EXTENSION_ONLY:
                note = ("  ⚠️ EXTENSION VALUE ONLY — not a primary phenotype term; "
                        "use it as an annotation extension (e.g. infective_ability → …)")
            elif c.usage == USAGE_GROUPING:
                note = "  ⚠️ GROUPING TERM — too general to annotate to"
            lines.append(f"    {mark} {c.obo_id}  {c.label or ''}{note}")
        _append_withheld(lines, r)
    matched = sum(1 for r in results if r.status == "matched")
    lines.append("")
    lines.append(f"{matched}/{len(results)} phrase(s) matched at least one PHIPO term. "
                 "Suggestions only — a curator confirms the term; verify the chosen ID "
                 "with `python3 -m phiweaver.lookup.validate_ontology_ids`.")
    return "\n".join(lines)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(
        description="Map phenotype phrases to candidate PHIPO terms, offline against the "
                    "bundled phipo-base.obo release. Never invents IDs; unmatched phrases "
                    "are reported as no_match.")
    p.add_argument("phrases", nargs="*",
                   help='phenotype description(s), e.g. "reduced virulence"')
    p.add_argument("--file", help="read one phenotype phrase per line from a file")
    p.add_argument("--rows", type=int, default=DEFAULT_ROWS,
                   help=f"max candidate terms per phrase (default {DEFAULT_ROWS}). The "
                        "offline scorer is cruder than OLS's; favour recall over ranking.")
    p.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    p.add_argument("--include-obsolete", action="store_true",
                   help="also return obsolete terms, flagged. NOT for annotation — a curator "
                        "cannot use an obsolete term. This is for gap analysis: OLS hides "
                        "deprecated terms, so a concept that was obsoleted looks like a "
                        "virgin gap (phipo#452 / PHIPO:0000503). See the "
                        "ontology-term-request skill, step 5.")
    p.add_argument("--include-grouping", action="store_true",
                   help="also return high-level grouping terms (PHIPO's "
                        "qc_do_not_annotate / qc_do_not_manually_annotate subsets) as "
                        "normal candidates. NOT for annotation — PHI-Canto rejects them "
                        "as too general. By default they are listed separately so that a "
                        "parent-only match is not mistaken for an ontology gap.")
    p.add_argument("--ontology", default=str(PHIPO_OBO_PATH),
                   help="path to the PHIPO .obo to search (default: the bundled release)")
    p.add_argument("--log-gaps", action="store_true",
                   help="append each no_match to the ontology gap ledger. Use only after "
                        "retrying alternate wordings — an un-retried miss is often a wording "
                        "gap, not a term gap (see the phipo-mapping skill).")
    p.add_argument("--pmid", help="with --log-gaps: the paper that needed the term")
    p.add_argument("--context", help="with --log-gaps: where in the paper, and what was measured")
    p.add_argument("--assay-context", choices=term_context.ASSAY_CONTEXTS,
                   help="where the phenotype was measured. With 'free-living', in-host terms "
                        "are flagged as contextually wrong — a match the search cannot know "
                        "is unusable (see term_context.py, PHI-base/phipo#452).")
    args = p.parse_args(argv)

    phrases: List[str] = list(args.phrases)
    if args.file:
        try:
            phrases.extend(read_phrases(args.file))
        except OSError as exc:
            p.error(f"cannot read --file: {exc}")
    if not phrases:
        p.error("provide one or more phenotype phrases, or --file")

    mapper = PhenotypeMapper(path=Path(args.ontology))
    results = [mapper.map(ph, rows=args.rows, include_obsolete=args.include_obsolete,
                          include_grouping=args.include_grouping)
               for ph in phrases]

    reviews = [term_context.review(r.candidates, args.assay_context)
               if (args.assay_context and r.candidates) else None
               for r in results]

    if args.log_gaps:
        # Only no_match is auto-recorded. A context-wrong result is *not* auto-recorded as a
        # gap: deciding the surviving candidates are irrelevant needs to know what the paper
        # measured, so --assay-context warns and a curator records the gap deliberately.
        for r in results:
            if r.status == "no_match" and r.query:
                gap_log.record("PHIPO", r.query, pmid=args.pmid, context=args.context)

    if args.json:
        payload = []
        for r, rev in zip(results, reviews):
            d = r.to_dict()
            if rev:
                d["assay_context"] = args.assay_context
                d["candidates"] = term_context.annotate_dicts(r.candidates,
                                                              args.assay_context)
                d["usable_candidates"] = len(rev.usable)
            payload.append(d)
        print(json.dumps(payload, indent=2))
    else:
        print(format_human(results))
        for r, rev in zip(results, reviews):
            if rev and (warning := term_context.format_warning(r.query, rev)):
                print(warning)
    # Exit reflects whether the search ran, not whether it matched: only errors fail.
    return 0 if all(r.ok for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
