#!/usr/bin/env python3
"""
phiweaver.canto.record — shared helpers for reading a draft's structured `canto` block.

A phiweaver draft carries a machine-readable ```json block with a `canto` object (genes / alleles /
genotypes / metagenotypes / annotations; see the curation-example template). These small,
renderer-agnostic helpers parse and normalise it, and are reused by the Route-1 entry-queue
renderer (`phiweaver.canto.entry_queue`) and the coverage lint (`phiweaver.canto.coverage`).

Pure stdlib.
"""

from __future__ import annotations

import json
import re

_JSON_BLOCK = re.compile(r"```json\s*(.*?)```", re.DOTALL)


def extract_record(md_text: str):
    """Parse the first ```json ... ``` block in a draft, or return None."""
    m = _JSON_BLOCK.search(md_text)
    if not m:
        return None
    return json.loads(m.group(1))


def _s(v) -> str:
    return str(v or "").strip()


def _fmt_extensions(exts) -> str:
    parts = []
    for e in exts or []:
        rel, val = _s(e.get("relation")), _s(e.get("value"))
        if rel and val:
            parts.append(f"{rel}={val}")
        elif rel or val:
            parts.append(rel or val)
    return " · ".join(parts)
