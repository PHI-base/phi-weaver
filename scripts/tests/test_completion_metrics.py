#!/usr/bin/env python3
"""Tests for real completion metrics: the DB primitive (phi_canto_sqlite.record_completion
/ get_completion_metrics) and the content-derived metrics (curation_pipeline).

Uses a temp SQLite DB and temp files — no network, no shared state.
"""

import io
import contextlib
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
for d in (REPO / "11-CLAUDE-AI", REPO / "11-CLAUDE-AI" / "db", REPO / "scripts"):
    sys.path.insert(0, str(d))

import phi_canto_sqlite as pcs       # noqa: E402
import curation_pipeline as cp       # noqa: E402


def fresh_db(tmp):
    db = pcs.PHICantoSQLite(db_path=str(Path(tmp) / "t.db"))
    with contextlib.redirect_stdout(io.StringIO()):
        db.connect()
        db.create_schema()
    return db


class RecordCompletionTests(unittest.TestCase):
    def test_creates_article_when_none_exists_and_links_session(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = fresh_db(tmp)
            res = db.record_completion(
                base_name="Smith-2024", summary="curated effectors",
                proteins_curated=3, interactions_added=5, experiments_annotated=8,
                session_duration_hours=2.5)
            self.assertTrue(res["article_created"])
            self.assertEqual(res["status"], "curated")

            art = db.cursor.execute(
                "SELECT status, title FROM articles WHERE id = ?",
                (res["article_id"],)).fetchone()
            self.assertEqual(art["status"], "curated")

            sess = db.cursor.execute(
                "SELECT article_id, proteins_curated, interactions_added,"
                " experiments_annotated FROM curation_sessions WHERE id = ?",
                (res["session_id"],)).fetchone()
            self.assertEqual(sess["article_id"], res["article_id"])  # linked!
            self.assertEqual(sess["proteins_curated"], 3)
            self.assertEqual(sess["interactions_added"], 5)
            self.assertEqual(sess["experiments_annotated"], 8)
            db.disconnect()

    def test_updates_existing_article_status_without_duplicating(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = fresh_db(tmp)
            db.cursor.execute(
                "INSERT INTO articles (pmid, title, status) VALUES "
                "('39000001', 'Existing paper', 'in_progress')")
            db.connection.commit()

            res = db.record_completion(
                base_name="Existing paper", summary="done", pmid="39000001",
                proteins_curated=1)
            self.assertFalse(res["article_created"])

            n = db.cursor.execute("SELECT COUNT(*) FROM articles").fetchone()[0]
            self.assertEqual(n, 1)  # matched, not duplicated
            status = db.cursor.execute(
                "SELECT status FROM articles WHERE pmid = '39000001'").fetchone()[0]
            self.assertEqual(status, "curated")
            db.disconnect()

    def test_matches_by_note_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = fresh_db(tmp)
            db.cursor.execute(
                "INSERT INTO articles (title, status, obsidian_note_path) VALUES "
                "('Paper X', 'queued', 'completed/PaperX-Curation-Notes.md')")
            db.connection.commit()
            res = db.record_completion(
                base_name="anything", summary="done",
                note_path="completed/PaperX-Curation-Notes.md")
            self.assertFalse(res["article_created"])
            self.assertEqual(db.cursor.execute("SELECT COUNT(*) FROM articles")
                             .fetchone()[0], 1)
            db.disconnect()

    def test_completion_metrics_report_aggregates_linked_sessions(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = fresh_db(tmp)
            db.record_completion(base_name="A", summary="s", proteins_curated=2,
                                 interactions_added=4)
            db.record_completion(base_name="B", summary="s", proteins_curated=1,
                                 experiments_annotated=9)
            with contextlib.redirect_stdout(io.StringIO()):
                rows = db.get_completion_metrics()
            titles = {r["title"]: r for r in rows}
            self.assertEqual(titles["A"]["proteins"], 2)
            self.assertEqual(titles["A"]["interactions"], 4)
            self.assertEqual(titles["B"]["experiments"], 9)
            # queued/in_progress articles must not appear
            db.cursor.execute("INSERT INTO articles (title, status) VALUES ('C', 'queued')")
            db.connection.commit()
            with contextlib.redirect_stdout(io.StringIO()):
                rows2 = db.get_completion_metrics()
            self.assertNotIn("C", {r["title"] for r in rows2})
            db.disconnect()


class DeriveMetricsTests(unittest.TestCase):
    def test_counts_distinct_identifiers_in_notes(self):
        with tempfile.TemporaryDirectory() as tmp:
            notes = Path(tmp) / "notes.md"
            notes.write_text(
                "Effector FGSG_11164 (UniProtKB:P12345) shows PHIPO:0000022 and "
                "GO:0009405. Also FGSG_08454 and the same GO:0009405 again, plus "
                "UniProtKB:P12345 repeated.", encoding="utf-8")
            m = cp.derive_completion_metrics(notes)
            self.assertEqual(m["uniprot"], 1)          # P12345 de-duped
            self.assertEqual(m["locus_tags"], 2)       # FGSG_11164, FGSG_08454
            self.assertEqual(m["ontology_terms"], 2)   # PHIPO:0000022, GO:0009405
            self.assertEqual(m["proteins"], 3)         # 1 accession + 2 locus tags
            self.assertIn("ontology term", m["summary"])

    def test_missing_file_returns_zeros(self):
        m = cp.derive_completion_metrics(Path("/no/such/file.md"))
        self.assertEqual(
            (m["uniprot"], m["locus_tags"], m["ontology_terms"], m["proteins"]),
            (0, 0, 0, 0))


if __name__ == "__main__":
    unittest.main()
