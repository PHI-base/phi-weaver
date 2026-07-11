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


class PersistenceTest(unittest.TestCase):
    def setUp(self):
        self.articles = [at.Article(pmid="111", label="Paper A"),
                         at.Article(pmid="222", label="Paper B")]

    def _batch(self, model, session_name):
        """Attribute a 2-paper batch from a transcript file named <session>.jsonl."""
        d = tempfile.mkdtemp()
        p = Path(d) / f"{session_name}.jsonl"
        p.write_text("\n".join([
            _asst(model, _usage(out=100, cr=1000), "setup ontologies"),
            _asst(model, _usage(out=200, cr=1000), "PMID 111 phenotype"),
            _asst(model, _usage(out=300, cr=1000), "PMID 222 phenotype"),
        ]), encoding="utf-8")
        turns = at.load_turns(p)
        attr = at.attribute(turns, self.articles)
        return at.build_rows(attr), attr, p

    def test_record_persists_raw_components_not_allocated_total(self):
        db = Path(tempfile.mkdtemp()) / "t.db"
        rows, attr, tpath = self._batch("claude-opus-4-8", "sessA")
        n = at.record_to_db(rows, attr, db, tpath)
        self.assertEqual(n, 2)
        hist = at.token_history(db, "111")
        self.assertEqual(len(hist), 1)
        row = hist[0]
        self.assertEqual(row["direct_tokens"], 200)          # raw own-work stored
        self.assertEqual(row["overhead_total"], attr.overhead)  # raw overhead stored
        self.assertEqual(row["n_articles"], 2)
        self.assertEqual(row["overhead_share"], round(attr.overhead / 2))  # derived on read

    def test_rerun_same_transcript_upserts_no_duplicate(self):
        db = Path(tempfile.mkdtemp()) / "t.db"
        rows, attr, tpath = self._batch("claude-opus-4-8", "sessA")
        at.record_to_db(rows, attr, db, tpath)
        at.record_to_db(rows, attr, db, tpath)  # idempotent
        self.assertEqual(len(at.token_history(db, "111")), 1)
        self.assertEqual(len(at.token_history(db)), 2)  # 2 articles, one row each

    def test_recuration_with_another_model_is_a_new_row(self):
        db = Path(tempfile.mkdtemp()) / "t.db"
        r1, a1, t1 = self._batch("claude-opus-4-8", "sessOLD")
        at.record_to_db(r1, a1, db, t1)
        r2, a2, t2 = self._batch("claude-fable-5", "sessNEW")   # recurate, new session+model
        at.record_to_db(r2, a2, db, t2)
        hist = at.token_history(db, "111")
        self.assertEqual(len(hist), 2)  # both curations preserved side by side
        self.assertEqual({h["model"] for h in hist},
                         {"claude-opus-4-8", "claude-fable-5"})

    def test_history_empty_before_record(self):
        db = Path(tempfile.mkdtemp()) / "t.db"
        self.assertEqual(at.token_history(db), [])
        self.assertIn("No stored measurements", at.render_history([], None))


if __name__ == "__main__":
    unittest.main()
