#!/usr/bin/env python3
"""
phiweaver.session_index — keep the session-log index short enough to read at session start.

``AGENTS.md`` tells every session to read ``11-CLAUDE-AI/SESSION-LOGS/Session-Logs-INDEX.md``
first, and specifies each log's row there as a **one-line prose recap**. Nothing enforced that,
and the rows grew steadily — by 2026-07 a single "one-line" row ran to 645 words, and the index
as a whole to ~6,000. Because the index is loaded before any work starts, that growth is a tax
on every future session, and it compounds: each session appends one more row.

This module enforces the cap that was already written down. The full recap belongs in the log
itself (a ``## Recap`` section, or the body); the index row is the pointer that helps you decide
which log to open.

Usage (from the repo root):
    python3 -m phiweaver.session_index            # report over-long rows
    python3 -m phiweaver.session_index --check    # exit 1 if any row is over the cap

Exit code: 0 if clean, 1 if any row exceeds the cap.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from phiweaver import repo_root

INDEX_PATH = "11-CLAUDE-AI/SESSION-LOGS/Session-Logs-INDEX.md"

# Words per row. Generous for "one line"; the point is to bound growth, not to win bytes.
MAX_WORDS = 40

_DATE_RE = re.compile(r"20\d\d-\d\d-\d\d")


def _rows(text: str):
    """Yield (line_number, date, summary_cell) for each session row in the index table."""
    for n, line in enumerate(text.splitlines(), start=1):
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 4 or not _DATE_RE.match(cells[0]):
            continue
        yield n, cells[0], cells[-1]


def check(root: Path) -> list[str]:
    """Return a problem string per row over the cap (empty list means clean)."""
    index = root / INDEX_PATH
    if not index.exists():
        return [f"{INDEX_PATH} not found"]
    problems = []
    for line_no, date, summary in _rows(index.read_text(encoding="utf-8")):
        words = len(summary.split())
        if words > MAX_WORDS:
            problems.append(
                f"{INDEX_PATH}:{line_no} ({date}) summary is {words} words, "
                f"cap is {MAX_WORDS} — move the detail into the log and shorten the row"
            )
    return problems


def main(argv=None) -> int:
    p = argparse.ArgumentParser(
        description="Check that Session-Logs-INDEX.md rows stay within the word cap.")
    p.add_argument("--check", action="store_true",
                   help="exit 1 if any row exceeds the cap (CI / smoke)")
    args = p.parse_args(argv)

    root = repo_root()
    problems = check(root)
    if problems:
        print(f"❌ {len(problems)} index row(s) over the {MAX_WORDS}-word cap:")
        for prob in problems:
            print(f"   {prob}")
        return 1 if args.check else 0

    total = sum(1 for _ in _rows((root / INDEX_PATH).read_text(encoding="utf-8")))
    print(f"✅ all {total} index rows within the {MAX_WORDS}-word cap.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
