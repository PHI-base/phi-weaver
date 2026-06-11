#!/usr/bin/env python3
"""
phiweaver.tracking.repository — pure, data-returning queries over the tracking DB.

Each function takes a ``sqlite3.Connection`` and returns rows; **none print**. This is the
query layer, separated from presentation so it can be unit-tested without capturing stdout.
The CLI / `PHICantoSQLite` methods call these and handle display.
"""

from __future__ import annotations

import sqlite3
from typing import List, Optional


def _rows(conn: sqlite3.Connection):
    """Use dict-like rows regardless of how the connection was created."""
    conn.row_factory = sqlite3.Row
    return conn.cursor()


def curation_progress(conn: sqlite3.Connection, days: int = 30) -> List[sqlite3.Row]:
    """Per day/curator session totals over the last ``days`` days."""
    cur = _rows(conn)
    cur.execute(
        "SELECT DATE(session_date) AS date, curator,"
        "       COUNT(*) AS sessions,"
        "       SUM(proteins_curated) AS total_proteins,"
        "       SUM(interactions_added) AS total_interactions,"
        "       SUM(session_duration_hours) AS total_hours"
        " FROM curation_sessions"
        " WHERE session_date >= DATE('now', ?)"
        " GROUP BY DATE(session_date), curator"
        " ORDER BY session_date DESC",
        (f"-{int(days)} days",))
    return cur.fetchall()


def article_status(conn: sqlite3.Connection) -> List[sqlite3.Row]:
    """Article counts and protein-mention counts grouped by workflow status."""
    cur = _rows(conn)
    cur.execute(
        "SELECT a.status, COUNT(a.id) AS article_count,"
        "       COUNT(pam.id) AS total_protein_mentions"
        " FROM articles a"
        " LEFT JOIN protein_article_mentions pam ON a.id = pam.article_id"
        " GROUP BY a.status"
        " ORDER BY CASE a.status WHEN 'queued' THEN 1 WHEN 'in_progress' THEN 2"
        "          WHEN 'curated' THEN 3 WHEN 'reviewed' THEN 4 WHEN 'published' THEN 5 END")
    return cur.fetchall()


def effector_proteins(conn: sqlite3.Connection,
                      species_pattern: Optional[str] = None) -> List[sqlite3.Row]:
    """Effector proteins, optionally filtered by a species-name LIKE pattern."""
    cur = _rows(conn)
    query = ("SELECT p.gene_id, p.name, p.gene_name, s.name AS species_name,"
             "       p.function_summary"
             " FROM proteins p JOIN species s ON p.species_id = s.id"
             " WHERE p.protein_type = 'effector'")
    params: list = []
    if species_pattern:
        query += " AND s.name LIKE ?"
        params.append(f"%{species_pattern}%")
    query += " ORDER BY s.name, p.gene_id"
    cur.execute(query, params)
    return cur.fetchall()


def completion_metrics(conn: sqlite3.Connection) -> List[sqlite3.Row]:
    """Per-article completion metrics, aggregated from article-linked sessions, for
    articles that have reached 'curated' or beyond."""
    cur = _rows(conn)
    cur.execute(
        "SELECT a.id, a.title, a.pmid, a.status, a.updated_date,"
        "       COUNT(cs.id) AS sessions,"
        "       COALESCE(SUM(cs.proteins_curated), 0) AS proteins,"
        "       COALESCE(SUM(cs.interactions_added), 0) AS interactions,"
        "       COALESCE(SUM(cs.experiments_annotated), 0) AS experiments,"
        "       COALESCE(SUM(cs.session_duration_hours), 0) AS hours"
        " FROM articles a"
        " LEFT JOIN curation_sessions cs ON cs.article_id = a.id"
        " WHERE a.status IN ('curated', 'reviewed', 'published')"
        " GROUP BY a.id"
        " ORDER BY a.updated_date DESC")
    return cur.fetchall()
