from pathlib import Path
import sqlite3
import pandas as pd
import streamlit as st

ROOT = Path(__file__).parent.parent
DB_PATH = ROOT / "11-CLAUDE-AI" / "mysql-setup" / "phi_canto_tracking.db"


def get_db() -> sqlite3.Connection:
    if "conn" not in st.session_state:
        conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
        conn.row_factory = sqlite3.Row
        st.session_state.conn = conn
    return st.session_state.conn


def q(sql: str, params: tuple = ()) -> pd.DataFrame:
    return pd.read_sql_query(sql, get_db(), params=params)


def run(sql: str, params: tuple = ()) -> None:
    conn = get_db()
    conn.execute(sql, params)
    conn.commit()


def get_or_create_species(name: str, species_type: str) -> int:
    conn = get_db()
    row = conn.execute("SELECT id FROM species WHERE name = ?", (name,)).fetchone()
    if row:
        return row[0]
    conn.execute("INSERT INTO species (name, type) VALUES (?, ?)", (name, species_type))
    conn.commit()
    return conn.execute("SELECT last_insert_rowid()").fetchone()[0]


def save_extraction(data: dict) -> int:
    """Persist AI-extracted article + proteins. Returns article_id."""
    conn = get_db()
    art = data.get("article", {})

    existing = conn.execute(
        "SELECT id FROM articles WHERE pmid = ? AND pmid IS NOT NULL",
        (art.get("pmid"),),
    ).fetchone()

    if existing:
        article_id = existing[0]
        conn.execute(
            """UPDATE articles SET title=?, journal=?, pub_year=?, authors=?, doi=?,
               updated_date=CURRENT_TIMESTAMP WHERE id=?""",
            (art.get("title"), art.get("journal"), art.get("pub_year"),
             art.get("authors"), art.get("doi"), article_id),
        )
    else:
        conn.execute(
            """INSERT INTO articles (pmid, doi, title, journal, pub_year, authors, status, curator)
               VALUES (?, ?, ?, ?, ?, ?, 'queued', 'curator')""",
            (art.get("pmid"), art.get("doi"), art.get("title"),
             art.get("journal"), art.get("pub_year"), art.get("authors")),
        )
        conn.commit()
        article_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

    for pathogen in data.get("pathogens", []):
        get_or_create_species(pathogen["name"], "pathogen")

    for host in data.get("hosts", []):
        get_or_create_species(host["name"], "host")

    for p in data.get("proteins", []):
        species_name = p.get("species", "")
        species_id = get_or_create_species(species_name, "pathogen") if species_name else None
        conn.execute(
            """INSERT INTO proteins
               (gene_id, gene_name, species_id, name, function_summary, protein_type, uniprot_id)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (p.get("gene_id"), p.get("gene_name"), species_id,
             p.get("gene_name"), p.get("function_summary"),
             p.get("protein_type", "other"), p.get("uniprot_id")),
        )

    conn.commit()
    return article_id
