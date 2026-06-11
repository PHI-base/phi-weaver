#!/usr/bin/env python3
"""
phiweaver.smoke — fresh-checkout sanity check for PHI-Weaver.

Answers one question: "I just cloned this repo — does the core tooling actually work
here?" It exercises the things most likely to break on a fresh checkout (import graph,
repo-root autodetection, storage bootstrap, DB schema, offline tools) and runs the
unit-test suite, all **network-free and with no install required** — the optional deps
(`requests`, PyMuPDF) are only needed for live lookups / PDF conversion, not for this.

Usage (from the repo root):
    python3 -m phiweaver.smoke            # human checklist, exit 0/1
    python3 -m phiweaver.smoke --quiet    # only the final summary + failures
    python3 scripts/smoke_test.py         # compatibility shim, same thing

Exit code: 0 if every check passes, 1 otherwise.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from phiweaver import repo_root

REPO_ROOT = repo_root()


@contextlib.contextmanager
def _quiet():
    """Swallow stdout from chatty library calls so the checklist stays readable."""
    with contextlib.redirect_stdout(io.StringIO()):
        yield


# ------------------------------------------------------------------- the checks

def check_repo_layout():
    """The files/folders the tooling assumes exist are present."""
    expected = [
        "AGENTS.md", "CLAUDE.md", "README.md", "pyproject.toml", "skills",
        "phiweaver/lookup/query_uniprot.py",
        "phiweaver/lookup/validate_ontology_ids.py",
        "phiweaver/tracking/phi_canto_sqlite.py",
        "phiweaver/pipeline/curation_pipeline.py",
    ]
    missing = [p for p in expected if not (REPO_ROOT / p).exists()]
    if missing:
        raise AssertionError(f"missing expected paths: {', '.join(missing)}")


def check_imports():
    """Every core module imports with only the standard library available."""
    from phiweaver.pipeline import curation_pipeline      # noqa: F401
    from phiweaver.tracking import phi_canto_sqlite        # noqa: F401
    from phiweaver.tracking import session_logger          # noqa: F401
    from phiweaver.lookup import query_uniprot             # noqa: F401
    from phiweaver.lookup import validate_ontology_ids     # noqa: F401


def check_pipeline_root_and_storage():
    """Pipeline auto-detects the repo root and bootstraps storage folders."""
    from phiweaver.pipeline import curation_pipeline
    with tempfile.TemporaryDirectory() as d:
        os.environ["PHI_LITERATURE_ROOT"] = d
        try:
            with _quiet():
                pipe = curation_pipeline.CurationPipeline()
            if pipe.vault_root != REPO_ROOT:
                raise AssertionError(
                    f"repo-root autodetect wrong: {pipe.vault_root} != {REPO_ROOT}")
            if pipe.external_storage != Path(d).resolve():
                raise AssertionError("PHI_LITERATURE_ROOT override not honoured")
            with _quiet():
                pipe.ensure_storage()
            for sub in ("active", "completed", "media"):
                if not (Path(d) / sub).is_dir():
                    raise AssertionError(f"ensure_storage() did not create {sub}/")
        finally:
            os.environ.pop("PHI_LITERATURE_ROOT", None)


def check_db_schema():
    """A fresh SQLite tracking DB can be created and queried from scratch."""
    from phiweaver.tracking import phi_canto_sqlite
    with tempfile.TemporaryDirectory() as d:
        db = phi_canto_sqlite.PHICantoSQLite(db_path=str(Path(d) / "smoke.db"))
        with _quiet():
            if not db.connect():
                raise AssertionError("could not connect to a fresh SQLite DB")
            if not db.create_schema():
                raise AssertionError("create_schema() failed on a fresh DB")
            db.cursor.execute(
                "INSERT INTO species (name, type) VALUES ('Test sp.', 'pathogen')")
            db.connection.commit()
            n = db.cursor.execute("SELECT COUNT(*) FROM species").fetchone()[0]
            db.disconnect()
        if n != 1:
            raise AssertionError(f"expected 1 species row, got {n}")


def check_offline_tooling():
    """The deterministic tools behave correctly without any network."""
    from phiweaver.lookup import validate_ontology_ids as v
    if not v.check_format("PHIPO:0000001")[1]:
        raise AssertionError("valid PHIPO ID rejected by format check")
    if v.check_format("GO:123")[1]:
        raise AssertionError("malformed GO ID accepted by format check")
    r = v.OntologyValidator(http_get=_no_network).validate("GO:0008150", online=False)
    if not r.ok or r.existence != "not_checked":
        raise AssertionError("offline validation did not short-circuit cleanly")

    from phiweaver.lookup import query_uniprot as qu
    if qu._build_query("FgTPP1", None, 5518) != "(gene:FgTPP1) AND organism_id:5518":
        raise AssertionError("query_uniprot query builder changed unexpectedly")


def _no_network(url, params):
    raise AssertionError("smoke test must not hit the network")


def check_unit_tests():
    """The bundled unit-test suite passes (run from the repo root)."""
    proc = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests"],
        cwd=str(REPO_ROOT), capture_output=True, text=True)
    if proc.returncode != 0:
        tail = (proc.stderr or proc.stdout).strip().splitlines()[-15:]
        raise AssertionError("unit tests failed:\n    " + "\n    ".join(tail))


CHECKS = [
    ("repo layout", check_repo_layout),
    ("module imports (stdlib only)", check_imports),
    ("pipeline root + storage bootstrap", check_pipeline_root_and_storage),
    ("DB schema create + query", check_db_schema),
    ("offline tools", check_offline_tooling),
    ("unit-test suite", check_unit_tests),
]


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Fresh-checkout smoke test for PHI-Weaver.")
    p.add_argument("--quiet", action="store_true",
                   help="print only the summary and any failures")
    args = p.parse_args(argv)

    if not args.quiet:
        print(f"PHI-Weaver smoke test  (repo: {REPO_ROOT})\n")

    failures = []
    for name, fn in CHECKS:
        try:
            fn()
        except Exception as exc:  # noqa: BLE001 - report any failure, keep going
            failures.append((name, exc))
            print(f"❌ {name}\n    {exc}")
        else:
            if not args.quiet:
                print(f"✅ {name}")

    print()
    if failures:
        print(f"SMOKE TEST FAILED — {len(failures)}/{len(CHECKS)} check(s) failed.")
        return 1
    print(f"SMOKE TEST PASSED — all {len(CHECKS)} checks green. Fresh checkout is healthy.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
