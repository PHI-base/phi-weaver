#!/usr/bin/env python3
"""Tests for the schema-migration runner (phiweaver.tracking.migrations). Temp DBs only."""

import sqlite3
import tempfile
import unittest
from pathlib import Path

from phiweaver.tracking import migrations


def _conn(tmp):
    return sqlite3.connect(str(Path(tmp) / "t.db"))


def _tables(conn):
    return {r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'")}


class MigrationRunnerTests(unittest.TestCase):
    def test_baseline_creates_tables_and_records_version(self):
        with tempfile.TemporaryDirectory() as tmp:
            conn = _conn(tmp)
            applied = migrations.run_migrations(conn)
            self.assertEqual(applied["core"], 1)
            self.assertEqual(migrations.current_version(conn, "core"), 1)
            self.assertTrue({"species", "articles", "curation_sessions",
                             "schema_migrations"} <= _tables(conn))

    def test_idempotent_rerun_applies_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            conn = _conn(tmp)
            migrations.run_migrations(conn)
            self.assertEqual(migrations.run_migrations(conn)["core"], 0)

    def test_module_adds_migration_without_editing_core(self):
        # The headline P5 property: a module's namespace has its own version counter and
        # applies independently of core. Uses a local registry — no global mutation.
        registry = {
            "core": migrations.CORE_MIGRATIONS,
            "demo_module": [("add demo table", "CREATE TABLE demo (id INTEGER)")],
        }
        with tempfile.TemporaryDirectory() as tmp:
            conn = _conn(tmp)
            applied = migrations.run_migrations(conn, registry=registry)
            self.assertEqual(applied, {"core": 1, "demo_module": 1})
            self.assertIn("demo", _tables(conn))
            self.assertEqual(migrations.current_version(conn, "demo_module"), 1)
            # adding the module later (core already at v1) only applies the module's
            conn2 = _conn(tmp)  # same file
            self.assertEqual(migrations.run_migrations(conn2, registry=registry),
                             {"core": 0, "demo_module": 0})

    def test_register_migrations_updates_global_registry(self):
        saved = dict(migrations._REGISTRY)
        try:
            migrations.register_migrations("tmp_ns", [("noop", "SELECT 1")])
            self.assertIn("tmp_ns", migrations._REGISTRY)
        finally:
            migrations._REGISTRY.clear()
            migrations._REGISTRY.update(saved)

    def test_preexisting_db_upgrades_and_preserves_data(self):
        with tempfile.TemporaryDirectory() as tmp:
            conn = _conn(tmp)
            conn.executescript(migrations.BASELINE_SCHEMA)  # old-style, no schema_migrations
            conn.execute("INSERT INTO species (name, type) VALUES ('X', 'pathogen')")
            conn.commit()
            self.assertEqual(migrations.current_version(conn, "core"), 0)
            migrations.run_migrations(conn)
            self.assertEqual(migrations.current_version(conn, "core"), 1)
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM species").fetchone()[0], 1)


if __name__ == "__main__":
    unittest.main()
