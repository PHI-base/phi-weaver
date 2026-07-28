"""Tests for phiweaver.session_index — the session-log index row cap."""

import tempfile
import unittest
from pathlib import Path

from phiweaver import repo_root, session_index

HEADER = """---
created: 2026-04-11
type: index
---

# Session Logs Index

| Date       | File | Project | Summary |
| ---------- | ---- | ------- | ------- |
"""


def _index(root: Path, *rows: str) -> Path:
    path = root / session_index.INDEX_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(HEADER + "".join(rows), encoding="utf-8")
    return path


def _row(date: str, slug: str, words: int) -> str:
    return f"| {date} | [[{slug}]] | Proj | {' word' * words} |\n"


class SessionIndexCheckTests(unittest.TestCase):

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def test_rows_within_cap_are_clean(self):
        _index(self.root,
               _row("2026-07-01", "a", session_index.MAX_WORDS),
               _row("2026-07-02", "b", 5))
        self.assertEqual(session_index.check(self.root), [])

    def test_row_over_cap_is_reported_once_with_line_and_date(self):
        _index(self.root,
               _row("2026-07-01", "a", 5),
               _row("2026-07-02", "b", session_index.MAX_WORDS + 1))
        problems = session_index.check(self.root)
        self.assertEqual(len(problems), 1)
        self.assertIn("2026-07-02", problems[0])
        self.assertIn(f"{session_index.MAX_WORDS + 1} words", problems[0])

    def test_non_row_lines_are_ignored(self):
        """Header, separator and prose lines must not be mistaken for session rows."""
        _index(self.root, "\nSome prose about the index that runs on well past forty words. "
                          + "filler " * 60 + "\n")
        self.assertEqual(session_index.check(self.root), [])

    def test_missing_index_is_a_problem_not_a_crash(self):
        problems = session_index.check(self.root)
        self.assertEqual(len(problems), 1)
        self.assertIn("not found", problems[0])

    def test_real_repo_index_is_within_cap(self):
        """Guards the actual index — this is the check smoke runs."""
        self.assertEqual(session_index.check(repo_root()), [])


class ShortenedRowTests(unittest.TestCase):
    """A truncated row (ending in the ellipsis) must itself satisfy the cap."""

    def test_ellipsis_counts_toward_the_cap(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            body = " ".join(["word"] * (session_index.MAX_WORDS - 1)) + " …"
            _index(root, f"| 2026-07-01 | [[a]] | Proj | {body} |\n")
            self.assertEqual(session_index.check(root), [])


if __name__ == "__main__":
    unittest.main()
