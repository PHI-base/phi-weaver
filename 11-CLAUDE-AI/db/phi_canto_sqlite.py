#!/usr/bin/env python3
"""Compatibility shim — code moved into the phiweaver/ package in P1
(see docs/MODULARITY-PLAN.md). Prefer `python3 -m phiweaver.tracking.phi_canto_sqlite`; this is kept so existing
documented commands keep working."""
import pathlib
import runpy
import sys

_here = pathlib.Path(__file__).resolve()
for _parent in _here.parents:                 # add repo root when phiweaver isn't installed
    if (_parent / "AGENTS.md").exists():
        sys.path.insert(0, str(_parent))
        break
runpy.run_module("phiweaver.tracking.phi_canto_sqlite", run_name="__main__", alter_sys=True)
