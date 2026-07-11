#!/usr/bin/env python3
"""Network-free tests for phiweaver.article_tokens (temp files, stdlib only)."""

import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from phiweaver import article_tokens as at


def _asst(model, usage, blob_text):
    """One transcript line as Claude Code writes it: assistant msg with usage."""
    return json.dumps({
        "type": "assistant",
        "message": {"model": model, "usage": usage,
                    "content": [{"type": "text", "text": blob_text}]},
    })


def _usage(inp=0, out=0, cw=0, cr=0):
    return {"input_tokens": inp, "output_tokens": out,
            "cache_creation_input_tokens": cw, "cache_read_input_tokens": cr}


class AttributionTest(unittest.TestCase):
    def setUp(self):
        self.articles = [at.Article(pmid="111", label="Paper A"),
                         at.Article(pmid="222", label="Paper B")]

    def _turns(self, lines):
        d = tempfile.mkdtemp()
        p = Path(d) / "s.jsonl"
        p.write_text("\n".join(lines), encoding="utf-8")
        return at.load_turns(p)

    def test_direct_vs_shared_split(self):
        turns = self._turns([
            _asst("claude-opus-4-8", _usage(inp=100, out=50, cr=1000), "loading ontologies"),      # shared (no pmid)
            _asst("claude-opus-4-8", _usage(inp=10, out=200, cr=2000), "curating PMID 111 now"),    # -> 111
            _asst("claude-opus-4-8", _usage(inp=10, out=300, cr=3000), "now paper 222 phenotype"),  # -> 222
            _asst("claude-opus-4-8", _usage(inp=5, out=5, cr=500), "compare 111 and 222 controls"),  # both -> shared
        ])
        attr = at.attribute(turns, self.articles)
        # direct work = input+output+cache_creation for the single-owner turns
        self.assertEqual(attr.direct["111"], 10 + 200)
        self.assertEqual(attr.direct["222"], 10 + 300)
        # shared work = setup turn + the two-article turn
        self.assertEqual(attr.shared_work, (100 + 50) + (5 + 5))
        # every turn's cache-read is overhead
        self.assertEqual(attr.reread_total, 1000 + 2000 + 3000 + 500)
        self.assertEqual(attr.matched_turns, 2)
        self.assertEqual(attr.unmatched_turns, 2)

    def test_equal_overhead_split_and_totals(self):
        turns = self._turns([
            _asst("claude-opus-4-8", _usage(out=100, cr=1000), "setup"),
            _asst("claude-opus-4-8", _usage(out=200, cr=1000), "PMID 111 work"),
            _asst("claude-opus-4-8", _usage(out=300, cr=1000), "PMID 222 work"),
        ])
        attr = at.attribute(turns, self.articles)
        rows = at.build_rows(attr)
        overhead = attr.overhead  # 100 shared work + 3000 reread = 3100
        self.assertEqual(overhead, 3100)
        for r in rows:
            self.assertEqual(r.overhead_share, round(3100 / 2))  # 1/N split
        by_pmid = {r.article.pmid: r for r in rows}
        self.assertEqual(by_pmid["111"].direct, 200)
        self.assertEqual(by_pmid["111"].total, 200 + round(3100 / 2))

    def test_weighted_split_favours_heavier_paper(self):
        turns = self._turns([
            _asst("m", _usage(out=100, cr=900), "setup"),
            _asst("m", _usage(out=100, cr=0), "PMID 111"),
            _asst("m", _usage(out=300, cr=0), "PMID 222"),
        ])
        attr = at.attribute(turns, self.articles)
        rows = {r.article.pmid: r for r in at.build_rows(attr, weight_by_direct=True)}
        # overhead=1000; 222 did 3x the direct work of 111, so gets the bigger share
        self.assertGreater(rows["222"].overhead_share, rows["111"].overhead_share)
        self.assertEqual(rows["111"].overhead_share + rows["222"].overhead_share
                         in (999, 1000, 1001), True)  # rounding-tolerant

    def test_draft_stem_is_a_reference_key(self):
        art = at.Article(pmid="999", draft_stem="fgtpp1-effector-phiweaver-draft")
        turns = self._turns([
            _asst("m", _usage(out=42), 'wrote {"file_path": "active/FgTPP1-effector-phiweaver-DRAFT.md"}'),
        ])
        attr = at.attribute(turns, [art])
        self.assertEqual(attr.direct["999"], 42)  # matched by filename even without PMID


class MetadataTest(unittest.TestCase):
    def test_articles_from_drafts_reads_meta(self):
        d = tempfile.mkdtemp()
        p = Path(d) / "x-phiweaver-DRAFT.md"
        p.write_text('```json\n{"meta": {"pmid": "38234567", "paper": "FgTPP1 paper",'
                     ' "model": "claude-opus-4-8"}}\n```\n', encoding="utf-8")
        arts = at.articles_from_drafts([str(p)])
        self.assertEqual(arts[0].pmid, "38234567")
        self.assertEqual(arts[0].model, "claude-opus-4-8")
        self.assertEqual(arts[0].draft_stem, "x-phiweaver-DRAFT")

    def test_enrich_from_db_fills_citation(self):
        d = tempfile.mkdtemp()
        db = Path(d) / "t.db"
        con = sqlite3.connect(str(db))
        con.execute("CREATE TABLE articles (pmid TEXT, title TEXT, authors TEXT, pub_year INT)")
        con.execute("INSERT INTO articles VALUES ('38234567','FgTPP1 effector','Smith et al.',2024)")
        con.commit(); con.close()
        art = at.Article(pmid="38234567")
        at.enrich_from_db([art], db)
        self.assertEqual(art.first_author, "Smith")
        self.assertEqual(art.year, "2024")
        self.assertEqual(art.citation, "Smith 2024")

    def test_enrich_is_noop_without_db(self):
        art = at.Article(pmid="1", label="Paper")
        at.enrich_from_db([art], Path("/no/such/file.db"))  # must not raise
        self.assertEqual(art.citation, "Paper")


if __name__ == "__main__":
    unittest.main()
