#!/usr/bin/env python3
"""Tests for the data-returning query layer (phiweaver.tracking.repository).

The point of the repository: these return data and DO NOT print, so the query layer is
testable without capturing stdout.
"""

import sqlite3
import tempfile
import unittest
from pathlib import Path

from phiweaver.tracking import migrations, repository


def _db(tmp):
    conn = sqlite3.connect(str(Path(tmp) / "t.db"))
    migrations.run_migrations(conn)
    return conn


class RepositoryTests(unittest.TestCase):
    def test_completion_metrics_returns_only_curated_plus(self):
        with tempfile.TemporaryDirectory() as tmp:
            conn = _db(tmp)
            conn.executescript(
                "INSERT INTO articles (id, title, status) VALUES "
                " (1, 'Done', 'curated'), (2, 'WIP', 'in_progress');"
                "INSERT INTO curation_sessions (session_date, curator, article_id,"
                " proteins_curated, interactions_added) VALUES"
                " ('2026-06-11', 'c', 1, 3, 5);")
            conn.commit()
            rows = repository.completion_metrics(conn)   # no stdout capture needed
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["title"], "Done")
            self.assertEqual(rows[0]["proteins"], 3)
            self.assertEqual(rows[0]["interactions"], 5)

    def test_article_status_groups_by_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            conn = _db(tmp)
            conn.executescript(
                "INSERT INTO articles (title, status) VALUES"
                " ('a', 'queued'), ('b', 'queued'), ('c', 'curated');")
            conn.commit()
            by_status = {r["status"]: r["article_count"]
                         for r in repository.article_status(conn)}
            self.assertEqual(by_status, {"queued": 2, "curated": 1})

    def test_effector_proteins_filter(self):
        with tempfile.TemporaryDirectory() as tmp:
            conn = _db(tmp)
            conn.executescript(
                "INSERT INTO species (id, name, type) VALUES"
                " (1, 'Fusarium graminearum', 'pathogen'), (2, 'Botrytis', 'pathogen');"
                "INSERT INTO proteins (gene_id, species_id, protein_type) VALUES"
                " ('FG1', 1, 'effector'), ('BO1', 2, 'effector'), ('FG2', 1, 'other');")
            conn.commit()
            all_eff = repository.effector_proteins(conn)
            self.assertEqual({r["gene_id"] for r in all_eff}, {"FG1", "BO1"})
            fus = repository.effector_proteins(conn, species_pattern="Fusarium")
            self.assertEqual({r["gene_id"] for r in fus}, {"FG1"})

    def test_curation_progress_returns_recent_sessions(self):
        with tempfile.TemporaryDirectory() as tmp:
            conn = _db(tmp)
            conn.execute(
                "INSERT INTO curation_sessions (session_date, curator, proteins_curated)"
                " VALUES (DATE('now'), 'c', 4)")
            conn.commit()
            rows = repository.curation_progress(conn, days=7)
            self.assertEqual(rows[0]["total_proteins"], 4)


if __name__ == "__main__":
    unittest.main()
