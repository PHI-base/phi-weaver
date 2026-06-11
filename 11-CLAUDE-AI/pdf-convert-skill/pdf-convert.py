#!/usr/bin/env python3
"""Compatibility shim — the PDF converter moved into phiweaver/pdf/ in P4
(see docs/MODULARITY-PLAN.md). Prefer `python3 -m phiweaver.pdf.pdf_convert`; this is
kept so existing documented commands keep working."""
import pathlib
import runpy
import sys

_here = pathlib.Path(__file__).resolve()
for _parent in _here.parents:                 # add repo root when phiweaver isn't installed
    if (_parent / "AGENTS.md").exists():
        sys.path.insert(0, str(_parent))
        break
runpy.run_module("phiweaver.pdf.pdf_convert", run_name="__main__", alter_sys=True)
