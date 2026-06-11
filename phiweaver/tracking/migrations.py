#!/usr/bin/env python3
"""
phiweaver.tracking.migrations — a tiny, namespaced schema-migration runner.

Lets the tracking DB schema evolve over time, and lets **specialised modules add their own
migrations without editing core**: each namespace (``"core"`` plus any module namespace)
has its own ordered migration list and its own applied-version counter, recorded in a
``schema_migrations`` table. So module migrations never collide with core's numbering.

A migration is a ``(description, sql_or_callable)`` pair, where the second item is either a
SQL script (run with ``executescript``) or a ``callable(conn)``. Migrations are append-only:
add new ones to the end of a namespace's list; never renumber or rewrite an applied one.

Usage:
    from phiweaver.tracking import migrations
    migrations.register_migrations("mymodule", [("add foo table", "CREATE TABLE foo(...)")])
    migrations.run_migrations(conn)        # applies all pending, for every namespace
"""

from __future__ import annotations

import sqlite3
from typing import Callable, Dict, List, Tuple, Union

Migration = Tuple[str, Union[str, Callable[[sqlite3.Connection], None]]]

# The v1 baseline — the original tracking schema (CREATE ... IF NOT EXISTS, so it is safe to
# (re)apply on a database that predates the migration system; its tables already exist).
BASELINE_SCHEMA = """
CREATE TABLE IF NOT EXISTS species (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type TEXT CHECK(type IN ('host', 'pathogen')) NOT NULL,
    taxonomy_id INTEGER,
    common_name TEXT,
    notes TEXT,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pmid TEXT UNIQUE,
    doi TEXT,
    title TEXT NOT NULL,
    journal TEXT,
    pub_year INTEGER,
    authors TEXT,
    status TEXT CHECK(status IN ('queued', 'in_progress', 'curated', 'reviewed', 'published')) DEFAULT 'queued',
    curator TEXT,
    priority TEXT CHECK(priority IN ('low', 'medium', 'high')) DEFAULT 'medium',
    obsidian_note_path TEXT,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS proteins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    gene_id TEXT,
    uniprot_id TEXT,
    species_id INTEGER,
    name TEXT,
    gene_name TEXT,
    function_summary TEXT,
    protein_type TEXT CHECK(protein_type IN ('effector', 'resistance', 'virulence', 'other')),
    obsidian_note_path TEXT,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (species_id) REFERENCES species(id)
);

CREATE TABLE IF NOT EXISTS curation_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_date DATE NOT NULL,
    curator TEXT NOT NULL,
    article_id INTEGER,
    session_duration_hours REAL,
    proteins_curated INTEGER DEFAULT 0,
    interactions_added INTEGER DEFAULT 0,
    experiments_annotated INTEGER DEFAULT 0,
    notes TEXT,
    obsidian_session_log TEXT,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (article_id) REFERENCES articles(id)
);

CREATE TABLE IF NOT EXISTS protein_article_mentions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    protein_id INTEGER,
    article_id INTEGER,
    mention_context TEXT,
    experimental_evidence TEXT CHECK(experimental_evidence IN ('complementation', 'knockout', 'overexpression', 'biochemical', 'other')),
    curated INTEGER DEFAULT 0,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (protein_id) REFERENCES proteins(id),
    FOREIGN KEY (article_id) REFERENCES articles(id),
    UNIQUE(protein_id, article_id)
);

CREATE INDEX IF NOT EXISTS idx_articles_status ON articles(status);
CREATE INDEX IF NOT EXISTS idx_proteins_species ON proteins(species_id);
CREATE INDEX IF NOT EXISTS idx_sessions_curator_date ON curation_sessions(curator, session_date);
"""

CORE_MIGRATIONS: List[Migration] = [
    ("v1 baseline tracking schema", BASELINE_SCHEMA),
]

# namespace -> ordered migration list. Modules append their own namespaces.
_REGISTRY: Dict[str, List[Migration]] = {}


def register_migrations(namespace: str, migrations: List[Migration]) -> None:
    """Register (or replace) the migration list for a namespace. Call at import time."""
    _REGISTRY[namespace] = list(migrations)


register_migrations("core", CORE_MIGRATIONS)


def _ensure_table(conn: sqlite3.Connection) -> None:
    conn.execute(
        "CREATE TABLE IF NOT EXISTS schema_migrations ("
        " namespace TEXT PRIMARY KEY, version INTEGER NOT NULL,"
        " updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")


def current_version(conn: sqlite3.Connection, namespace: str) -> int:
    """How many migrations of ``namespace`` have been applied (0 if none/unknown)."""
    try:
        row = conn.execute(
            "SELECT version FROM schema_migrations WHERE namespace = ?",
            (namespace,)).fetchone()
    except sqlite3.OperationalError:
        return 0
    return int(row[0]) if row else 0


def run_migrations(conn: sqlite3.Connection, registry: Dict[str, List[Migration]] = None
                   ) -> Dict[str, int]:
    """Apply every pending migration, per namespace. Returns {namespace: applied_count}.

    Idempotent: re-running applies nothing once a DB is current. Each migration commits on
    success, so a failure leaves earlier migrations applied and recorded.
    """
    registry = _REGISTRY if registry is None else registry
    _ensure_table(conn)
    applied: Dict[str, int] = {}
    for namespace, migrations in registry.items():
        version = current_version(conn, namespace)
        count = 0
        for index in range(version, len(migrations)):
            _description, body = migrations[index]
            if callable(body):
                body(conn)
            else:
                conn.executescript(body)
            new_version = index + 1
            cur = conn.execute(
                "UPDATE schema_migrations SET version = ?, updated_at = CURRENT_TIMESTAMP"
                " WHERE namespace = ?", (new_version, namespace))
            if cur.rowcount == 0:
                conn.execute(
                    "INSERT INTO schema_migrations (namespace, version) VALUES (?, ?)",
                    (namespace, new_version))
            conn.commit()
            count += 1
        applied[namespace] = count
    return applied
