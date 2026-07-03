#!/usr/bin/env python3
"""Network-free tests for phiweaver.batch_summary (temp files, stdlib only)."""

import csv
import tempfile
import unittest
from pathlib import Path

from phiweaver import batch_summary as bs

DRAFT_A = '''---
type: curation-example
---
body text
```json
{"meta": {"paper": "Paper A", "pmid": "111"}, "triage": "in_scope",
 "auto_check": {"go": "OK: exists & current", "uniprot": "NOT resolved"},
 "flags": [{"category": "needs_accession", "detail": "gene X not in UniProt"},
           {"category": "scope_question", "detail": "physical interaction"}]}
```
'''

DRAFT_B = '''---
type: curation-example
---
```json
{"meta": {"paper": "Paper B"}, "triage": "needs_human_decision",
 "flags": [{"category": "scope_question", "detail": "BioID interactome"}]}
```
'''

NO_BLOCK = "---\ntype: triage-note\n---\njust prose, no json block\n"


def write(tmp, files):
    d = Path(tmp)
    for name, content in files.items():
        (d / name).write_text(content, encoding="utf-8")
    return [str(d / n) for n in files]


class ExtractTests(unittest.TestCase):
    def test_extracts_block(self):
        rec = bs.extract_record(DRAFT_A)
        self.assertEqual(rec["triage"], "in_scope")
        self.assertEqual(len(rec["flags"]), 2)

    def test_no_block_returns_none(self):
        self.assertIsNone(bs.extract_record(NO_BLOCK))


class LoadTests(unittest.TestCase):
    def test_loads_and_skips(self):
        with tempfile.TemporaryDirectory() as tmp:
            paths = write(tmp, {"a.md": DRAFT_A, "b.md": DRAFT_B, "c.md": NO_BLOCK})
            drafts, skipped = bs.load_drafts(paths)
            self.assertEqual(len(drafts), 2)
            self.assertEqual(len(skipped), 1)

    def test_sorted_most_attention_first(self):
        with tempfile.TemporaryDirectory() as tmp:
            paths = write(tmp, {"a.md": DRAFT_A, "b.md": DRAFT_B})
            drafts, _ = bs.load_drafts(paths)
            # needs_human_decision (B) sorts before in_scope (A)
            self.assertEqual(drafts[0].paper, "Paper B")
            self.assertEqual(drafts[1].paper, "Paper A")

    def test_auto_check_signal(self):
        with tempfile.TemporaryDirectory() as tmp:
            paths = write(tmp, {"a.md": DRAFT_A})
            (d,), _ = bs.load_drafts(paths)
            self.assertEqual((d.auto_ok, d.auto_attn), (1, 1))  # OK: ... vs NOT ...


class RenderTests(unittest.TestCase):
    def test_markdown_has_rollup_and_triage(self):
        with tempfile.TemporaryDirectory() as tmp:
            paths = write(tmp, {"a.md": DRAFT_A, "b.md": DRAFT_B, "c.md": NO_BLOCK})
            drafts, skipped = bs.load_drafts(paths)
            md = bs.render_markdown(drafts, skipped)
            self.assertIn("Paper A", md)
            self.assertIn("Paper B", md)
            self.assertIn("### scope_question (2)", md)   # A + B both flag scope
            self.assertIn("### needs_accession (1)", md)
            self.assertIn("needs_human_decision: 1", md)
            self.assertIn("Skipped", md)                  # NO_BLOCK reported

    def test_csv(self):
        with tempfile.TemporaryDirectory() as tmp:
            paths = write(tmp, {"a.md": DRAFT_A})
            drafts, _ = bs.load_drafts(paths)
            out = Path(tmp) / "s.csv"
            bs.write_csv(drafts, str(out))
            rows = list(csv.DictReader(out.open(encoding="utf-8")))
            self.assertEqual(rows[0]["paper"], "Paper A")
            self.assertEqual(rows[0]["flag_count"], "2")


if __name__ == "__main__":
    unittest.main()
