#!/usr/bin/env python3
"""
phiweaver.vault_names — guard against duplicate Markdown note basenames.

Obsidian's graph view (and the quick-switcher, and ``[[wikilinks]]``) label a note by its
*basename*, ignoring the folder. Two notes with the same basename therefore collide: they
render as indistinguishable graph nodes and make an ``[[link]]`` target ambiguous. This
check enforces the naming convention in ``AGENTS.md`` — every explorable note has a
vault-unique, descriptive basename — while exempting the fixed-name convention files a tool
or platform requires verbatim (``SKILL.md``, ``README.md``) and known intentional markers.

Usage (from the repo root):
    python3 -m phiweaver.vault_names           # report duplicate basenames
    python3 -m phiweaver.vault_names --check    # exit 1 if any non-exempt duplicate exists

Exit code: 0 if clean, 1 if a non-exempt duplicate basename is found.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path

from phiweaver import repo_root

# Directories that are not part of the explorable vault.
_SKIP_DIRS = {".git", ".obsidian", ".trash", "archive", "__pycache__",
              ".devcontainer", "node_modules", ".claude"}

# Basenames allowed to repeat: fixed-name convention files required verbatim by a tool or
# platform, plus known intentional markers. Keep this SHORT and justified — every entry is a
# graph-view collision we have chosen to accept.
EXEMPT_BASENAMES = {
    "README.md",                        # GitHub / directory convention
    "SKILL.md",                         # required by the skill loader (one per skills/<name>/)
    "MIGRATED-TO-EXTERNAL-STORAGE.md",  # tombstone marker for relocated content
}


def _iter_markdown(root: Path):
    """Yield every explorable .md file under root (excluding non-vault dirs)."""
    for p in root.rglob("*.md"):
        if any(part in _SKIP_DIRS for part in p.relative_to(root).parts):
            continue
        yield p


def duplicate_basenames(root: Path) -> dict[str, list[Path]]:
    """Non-exempt basenames that occur more than once, mapped to their paths."""
    by_name: dict[str, list[Path]] = defaultdict(list)
    for p in _iter_markdown(root):
        if p.name in EXEMPT_BASENAMES:
            continue
        by_name[p.name].append(p)
    return {name: paths for name, paths in by_name.items() if len(paths) > 1}


def check(root: Path) -> list[str]:
    """Return one problem string per colliding basename (empty list = clean)."""
    problems = []
    for name, paths in sorted(duplicate_basenames(root).items()):
        rels = ", ".join(sorted(str(p.relative_to(root)) for p in paths))
        problems.append(f"duplicate note basename {name!r}: {rels}")
    return problems


def main(argv=None) -> int:
    p = argparse.ArgumentParser(
        description="Guard against duplicate note basenames (Obsidian graph-view clarity).")
    p.add_argument("--check", action="store_true",
                   help="exit 1 if any non-exempt duplicate basename exists")
    p.parse_args(argv)

    root = repo_root()
    problems = check(root)
    if problems:
        print(f"❌ {len(problems)} duplicate note basename(s) — these collide in Obsidian's graph:")
        for prob in problems:
            print(f"   - {prob}")
        print("\nGive each a vault-unique, descriptive name (for a folder index, prefix the "
              "folder's subject), or add a justified exemption to EXEMPT_BASENAMES. See the "
              "naming convention in AGENTS.md.")
        return 1
    print("✅ no duplicate note basenames (exempting SKILL.md / README.md / markers).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
