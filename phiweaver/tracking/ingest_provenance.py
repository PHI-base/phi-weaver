#!/usr/bin/env python3
"""
phiweaver.tracking.ingest_provenance — record how each article reached the curation.

Stores the ingest route alongside the article in the tracking DB, using the shared
vocabulary in :mod:`phiweaver.source_routes` so the database and the curation outputs
(draft header, PHI-Canto entry queue) cannot disagree about the same paper.

Why it belongs in the database and not only in a markdown header: the route determines
what evidence a draft could possibly rest on. Once a corpus is curated by mixed routes,
"which of these drafts were written without seeing the figures?" becomes a question you
want to answer with a query, not by reopening every file — for example before trusting a
batch of drafts, or when a paper that was captions-only later becomes open access and is
worth revisiting.

Usage:
    from phiweaver.tracking import ingest_provenance
    ingest_provenance.record(conn, pmid="39852455", route="jats-europepmc",
                             source_file="PMC11767236.xml", figures_inspected=True)
    ingest_provenance.captions_only_articles(conn)   # drafts written without figures
"""

from __future__ import annotations

import sqlite3
from typing import List, Optional

from phiweaver.source_routes import figures_available, normalise_route

# Append-only. Adds ingest provenance to `articles`; nullable so existing rows stay valid
# (an article curated before this existed genuinely has no recorded route, and must read
# as unknown rather than be back-filled with a guess).
_INGEST_PROVENANCE_V1_SQL = """
ALTER TABLE articles ADD COLUMN source_route TEXT;
ALTER TABLE articles ADD COLUMN source_file TEXT;
ALTER TABLE articles ADD COLUMN figures_available INTEGER;
"""


def _register_migration() -> None:
    """Register this module's schema migrations once (idempotent)."""
    from phiweaver.tracking import migrations
    migrations.register_migrations("ingest_provenance", [
        ("v1 article ingest-route columns", _INGEST_PROVENANCE_V1_SQL),
    ])


_register_migration()


def record(conn: sqlite3.Connection, pmid: str = "", route: str = "",
           source_file: str = "", figures_inspected: Optional[bool] = None,
           note_path: str = "", title: str = "") -> bool:
    """Attach the ingest route to an article row. Returns True if a row was updated.

    The article is located by PMID, then note path, then title — the same order
    ``phi_canto_sqlite`` uses. No row is created here: provenance annotates an article the
    pipeline has already registered, and inventing a row to hang it on would put a
    half-empty article into the curation queue.
    """
    route = normalise_route(route)
    available = figures_available(route, figures_inspected) if route else None

    article_id = None
    for column, value in (("pmid", pmid), ("obsidian_note_path", note_path),
                          ("title", title)):
        if not value:
            continue
        row = conn.execute(
            f"SELECT id FROM articles WHERE {column} = ?", (value,)).fetchone()
        if row:
            article_id = row[0]
            break

    if article_id is None:
        return False

    conn.execute(
        "UPDATE articles SET source_route = ?, source_file = ?, figures_available = ?,"
        " updated_date = CURRENT_TIMESTAMP WHERE id = ?",
        (route or None, source_file or None,
         None if available is None else int(available), article_id))
    conn.commit()
    return True


def route_counts(conn: sqlite3.Connection) -> List[sqlite3.Row]:
    """How many articles came in by each route (unrecorded rows group as NULL)."""
    conn.row_factory = sqlite3.Row
    return conn.execute(
        "SELECT source_route, COUNT(*) AS article_count,"
        "       SUM(COALESCE(figures_available, 0)) AS with_figures"
        " FROM articles GROUP BY source_route ORDER BY article_count DESC").fetchall()


def captions_only_articles(conn: sqlite3.Connection) -> List[sqlite3.Row]:
    """Articles curated from a source whose figures were never readable.

    The revisit list: if such a paper is open access, re-acquiring it with figures can
    change the annotations, as it did for PMID:39852455.
    """
    conn.row_factory = sqlite3.Row
    return conn.execute(
        "SELECT pmid, title, source_route, source_file, status FROM articles"
        " WHERE figures_available = 0 ORDER BY updated_date DESC").fetchall()
