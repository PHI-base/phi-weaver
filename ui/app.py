#!/usr/bin/env python3
import sys
import subprocess
import tempfile
from pathlib import Path
from datetime import date

import streamlit as st
import pandas as pd
import sqlite3

ROOT = Path(__file__).parent.parent
DB_PATH = ROOT / "11-CLAUDE-AI" / "mysql-setup" / "phi_canto_tracking.db"
CONVERTER = ROOT / "11-CLAUDE-AI" / "pdf-convert-skill" / "pdf-convert.py"

STATUS_OPTS = ["queued", "in_progress", "curated", "reviewed", "published"]
PROTEIN_TYPES = ["effector", "resistance", "virulence", "other"]
EXP_EVIDENCE = ["complementation", "knockout", "overexpression", "biochemical", "other"]

_STATUS_COLOR = {
    "queued":      ("#E8EAF6", "#3949AB"),
    "in_progress": ("#FEF3C7", "#92400E"),
    "curated":     ("#DBEAFE", "#1E40AF"),
    "reviewed":    ("#EDE9FE", "#5B21B6"),
    "published":   ("#1F3478", "#FFFFFF"),
}

CSS = """
<style>
/* Sidebar — PHI-base navy gradient */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1F3478 0%, #2B3A8C 100%);
}
[data-testid="stSidebar"] * { color: #D6DCEF !important; }
[data-testid="stSidebar"] .stRadio > div > label {
    border-radius: 6px;
    padding: 0.4rem 0.6rem;
    transition: background 0.15s;
}
[data-testid="stSidebar"] .stRadio > div > label:hover {
    background: rgba(255,255,255,0.1);
}

/* Page headings */
h1 { font-weight: 700; letter-spacing: -0.02em; }
h2 { font-weight: 600; }
h3 { font-weight: 600; }

/* Metric cards */
[data-testid="stMetric"] {
    background: #EEF0F8;
    border-radius: 10px;
    padding: 1rem 1.2rem;
    border: 1px solid #C7CDE8;
}
[data-testid="stMetricValue"] { color: #1F3478; font-weight: 700; }

/* Pipeline stage cards */
.stage-card {
    background: #EEF0F8;
    border: 1px solid #C7CDE8;
    border-radius: 10px;
    padding: 1.1rem 0.8rem;
    text-align: center;
}
.stage-count { font-size: 2rem; font-weight: 700; color: #1F3478; line-height: 1; }
.stage-label {
    font-size: 0.72rem;
    color: #6B7280;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    margin-top: 0.35rem;
}

/* Status badge */
.badge {
    display: inline-block;
    padding: 0.18rem 0.65rem;
    border-radius: 9999px;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.03em;
}

/* Article attention list */
.attention-row {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    padding: 0.45rem 0;
    border-bottom: 1px solid #D6DCEF;
    font-size: 0.88rem;
}
.attention-row:last-child { border-bottom: none; }

/* Divider */
hr { border-color: #D6DCEF; margin: 1.2rem 0; }

/* Expander */
[data-testid="stExpander"] {
    border: 1px solid #C7CDE8 !important;
    border-radius: 8px !important;
}

/* Form */
[data-testid="stForm"] {
    border: 1px solid #C7CDE8;
    border-radius: 10px;
    padding: 1.2rem 1.2rem 0.5rem;
}

/* Sidebar brand */
.brand { font-size: 1.25rem; font-weight: 700; letter-spacing: -0.01em; }
.brand-sub { font-size: 0.78rem; opacity: 0.6; margin-top: -0.2rem; }
</style>
"""


def get_db():
    if "conn" not in st.session_state:
        conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
        conn.row_factory = sqlite3.Row
        st.session_state.conn = conn
    return st.session_state.conn


def q(sql, params=()):
    return pd.read_sql_query(sql, get_db(), params=params)


def run(sql, params=()):
    conn = get_db()
    conn.execute(sql, params)
    conn.commit()


def badge_html(status):
    bg, fg = _STATUS_COLOR.get(status, ("#E2E8F0", "#475569"))
    label = status.replace("_", " ")
    return f'<span class="badge" style="background:{bg};color:{fg}">{label}</span>'


# ── Pages ──────────────────────────────────────────────────────────────────────

def page_dashboard():
    st.title("Dashboard")

    total_articles = q("SELECT COUNT(*) n FROM articles").iloc[0]["n"]
    total_proteins = q("SELECT COUNT(*) n FROM proteins").iloc[0]["n"]
    total_sessions = q("SELECT COUNT(*) n FROM curation_sessions").iloc[0]["n"]
    hours_val = q("SELECT SUM(session_duration_hours) h FROM curation_sessions").iloc[0]["h"]
    total_hours = round(hours_val or 0, 1)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Articles", total_articles)
    c2.metric("Proteins", total_proteins)
    c3.metric("Sessions", total_sessions)
    c4.metric("Hours logged", total_hours)

    st.markdown("<hr>", unsafe_allow_html=True)

    # Pipeline
    st.subheader("Article pipeline")
    counts_df = q("SELECT status, COUNT(*) n FROM articles GROUP BY status")
    counts = dict(zip(counts_df["status"], counts_df["n"]))
    cols = st.columns(len(STATUS_OPTS))
    for col, s in zip(cols, STATUS_OPTS):
        col.markdown(
            f'<div class="stage-card">'
            f'<div class="stage-count">{counts.get(s, 0)}</div>'
            f'<div class="stage-label">{s.replace("_", " ")}</div>'
            f"</div>",
            unsafe_allow_html=True,
        )

    st.markdown("&nbsp;")

    left, right = st.columns(2)

    with left:
        st.subheader("Recent sessions")
        recent = q("""
            SELECT session_date as date,
                   proteins_curated  as proteins,
                   interactions_added as interactions,
                   ROUND(session_duration_hours, 1) as hours
            FROM curation_sessions
            ORDER BY created_date DESC LIMIT 6
        """)
        if recent.empty:
            st.caption("No sessions recorded yet.")
        else:
            st.dataframe(recent, width="stretch", hide_index=True)

    with right:
        st.subheader("Needs attention")
        pending = q("""
            SELECT title, status FROM articles
            WHERE status IN ('queued','in_progress')
            ORDER BY CASE status WHEN 'in_progress' THEN 1 ELSE 2 END, pub_year DESC
        """)
        if pending.empty:
            st.caption("All clear.")
        else:
            rows_html = "".join(
                f'<div class="attention-row">{badge_html(r["status"])}'
                f'<span>{r["title"][:60]}{"…" if len(r["title"]) > 60 else ""}</span></div>'
                for _, r in pending.iterrows()
            )
            st.markdown(rows_html, unsafe_allow_html=True)


def page_articles():
    st.title("Articles")

    with st.expander("Add article"):
        with st.form("add_article", clear_on_submit=True):
            title = st.text_input("Title *")
            c1, c2 = st.columns(2)
            pmid = c1.text_input("PMID")
            year = c2.number_input("Year", 1990, 2030, value=date.today().year, step=1)
            c3, c4 = st.columns(2)
            journal = c3.text_input("Journal")
            authors = c4.text_input("Authors")
            if st.form_submit_button("Add article", type="primary"):
                if not title:
                    st.error("Title is required.")
                else:
                    run(
                        "INSERT INTO articles (pmid,title,journal,pub_year,authors,status,curator)"
                        " VALUES (?,?,?,?,?,'queued','curator')",
                        (pmid or None, title, journal or None, year, authors or None),
                    )
                    st.success("Article added.")
                    st.rerun()

    st.markdown("&nbsp;")

    status_filter = st.segmented_control(
        "Filter", ["All"] + [s.replace("_", " ").title() for s in STATUS_OPTS],
        default="All"
    )
    filter_val = None if status_filter == "All" else status_filter.lower().replace(" ", "_")

    sql = """
        SELECT id, title, pmid, journal, pub_year as year,
               authors, status, priority
        FROM articles
    """
    params: tuple = ()
    if filter_val:
        sql += " WHERE status = ?"
        params = (filter_val,)
    sql += " ORDER BY CASE status WHEN 'in_progress' THEN 1 WHEN 'queued' THEN 2 ELSE 3 END, year DESC"

    articles = q(sql, params)

    if articles.empty:
        st.caption("No articles found.")
        return

    edited = st.data_editor(
        articles,
        column_config={
            "id": None,
            "title": st.column_config.TextColumn("Title", width="large"),
            "pmid": st.column_config.TextColumn("PMID", width="small"),
            "journal": st.column_config.TextColumn("Journal"),
            "year": st.column_config.NumberColumn("Year", width="small"),
            "authors": st.column_config.TextColumn("Authors"),
            "status": st.column_config.SelectboxColumn("Status", options=STATUS_OPTS, width="medium"),
            "priority": st.column_config.SelectboxColumn("Priority", options=["low","medium","high"], width="small"),
        },
        disabled=["title", "pmid", "journal", "year", "authors"],
        hide_index=True,
        width="stretch",
    )

    changed = articles[
        (articles["status"] != edited["status"]) |
        (articles["priority"] != edited["priority"])
    ]
    if not changed.empty:
        for i, row in changed.iterrows():
            run(
                "UPDATE articles SET status=?, priority=?, updated_date=CURRENT_TIMESTAMP WHERE id=?",
                (edited.at[i, "status"], edited.at[i, "priority"], row["id"]),
            )
        st.toast(f"Saved {len(changed)} change(s).", icon="✅")
        st.rerun()


def page_proteins():
    st.title("Proteins")

    c1, c2, c3 = st.columns([3, 2, 1])
    search = c1.text_input("Search", placeholder="gene name, function, ID…", label_visibility="collapsed")
    species_opts = q("SELECT DISTINCT name FROM species ORDER BY name")["name"].tolist()
    species_filter = c2.selectbox("Species", ["All species"] + species_opts, label_visibility="collapsed")
    type_filter = c3.selectbox("Type", ["All"] + PROTEIN_TYPES, label_visibility="collapsed")

    sql = """
        SELECT p.gene_id, p.gene_name, s.name as species,
               p.protein_type as type, p.uniprot_id,
               p.function_summary as function
        FROM proteins p JOIN species s ON p.species_id = s.id
        WHERE 1=1
    """
    params = []
    if search:
        sql += " AND (p.gene_name LIKE ? OR p.function_summary LIKE ? OR p.gene_id LIKE ?)"
        params += [f"%{search}%", f"%{search}%", f"%{search}%"]
    if species_filter != "All species":
        sql += " AND s.name = ?"
        params.append(species_filter)
    if type_filter != "All":
        sql += " AND p.protein_type = ?"
        params.append(type_filter)
    sql += " ORDER BY s.name, p.gene_id"

    proteins = q(sql, params)

    if proteins.empty:
        st.caption("No proteins match.")
        return

    st.dataframe(
        proteins,
        width="stretch",
        hide_index=True,
        column_config={
            "gene_id":  st.column_config.TextColumn("Gene ID"),
            "gene_name":st.column_config.TextColumn("Name"),
            "species":  st.column_config.TextColumn("Species"),
            "type":     st.column_config.TextColumn("Type", width="small"),
            "uniprot_id":st.column_config.TextColumn("UniProt", width="small"),
            "function": st.column_config.TextColumn("Function", width="large"),
        },
    )
    st.caption(f"{len(proteins)} protein{'s' if len(proteins) != 1 else ''}")


def page_sessions():
    st.title("Sessions")

    with st.form("log_session", clear_on_submit=True):
        st.subheader("Log session")
        c1, c2, c3 = st.columns(3)
        proteins  = c1.number_input("Proteins curated", min_value=0, value=0, step=1)
        interactions = c2.number_input("Interactions added", min_value=0, value=0, step=1)
        hours = c3.number_input("Hours", min_value=0.0, step=0.5, value=1.0)
        notes = st.text_area("Notes", placeholder="What did you work on today?")
        if st.form_submit_button("Log session", type="primary"):
            run(
                """INSERT INTO curation_sessions
                   (session_date, curator, proteins_curated, interactions_added,
                    session_duration_hours, notes)
                   VALUES (?, 'curator', ?, ?, ?, ?)""",
                (date.today(), proteins, interactions, hours, notes or None),
            )
            st.success("Session logged.")
            st.rerun()

    st.markdown("<hr>", unsafe_allow_html=True)
    st.subheader("History")

    sessions = q("""
        SELECT session_date as date, curator,
               proteins_curated as proteins, interactions_added as interactions,
               ROUND(session_duration_hours, 1) as hours, notes
        FROM curation_sessions ORDER BY created_date DESC
    """)

    if sessions.empty:
        st.caption("No sessions yet.")
        return

    st.dataframe(sessions, width="stretch", hide_index=True)

    st.markdown("&nbsp;")
    totals = q("""
        SELECT SUM(proteins_curated) p, SUM(interactions_added) i,
               ROUND(SUM(session_duration_hours), 1) h
        FROM curation_sessions
    """).iloc[0]
    c1, c2, c3 = st.columns(3)
    c1.metric("Total proteins curated", int(totals["p"] or 0))
    c2.metric("Total interactions", int(totals["i"] or 0))
    c3.metric("Total hours", totals["h"] or 0)


def page_converter():
    st.title("PDF Converter")
    st.caption("Convert academic PDFs to structured Obsidian markdown.")

    uploaded = st.file_uploader("Upload PDF", type="pdf", label_visibility="collapsed")
    if not uploaded:
        return

    st.markdown(f"**{uploaded.name}** — {uploaded.size / 1024:.0f} KB")

    if st.button("Convert to markdown", type="primary"):
        with st.spinner("Converting…"):
            with tempfile.TemporaryDirectory() as tmp:
                pdf_path = Path(tmp) / uploaded.name
                out_dir  = Path(tmp) / "out"
                out_dir.mkdir()
                pdf_path.write_bytes(uploaded.read())

                result = subprocess.run(
                    [sys.executable, str(CONVERTER), str(pdf_path),
                     "--output-dir", str(out_dir), "--no-index"],
                    capture_output=True, text=True,
                )

                md_files = list(out_dir.glob("*.md"))

                if md_files:
                    content = md_files[0].read_text(encoding="utf-8")
                    st.success(f"Done — {len(content):,} characters")
                    st.download_button(
                        "⬇ Download markdown",
                        content,
                        file_name=md_files[0].name,
                        mime="text/markdown",
                        type="primary",
                    )
                    with st.expander("Preview (first 4 000 chars)"):
                        preview = content[:4000]
                        if len(content) > 4000:
                            preview += "\n\n*…truncated*"
                        st.markdown(preview)
                else:
                    st.error("Conversion failed.")
                    if result.stderr:
                        with st.expander("Error details"):
                            st.code(result.stderr)


# ── Main ───────────────────────────────────────────────────────────────────────

PAGES = {
    "🏠  Dashboard":     page_dashboard,
    "📚  Articles":      page_articles,
    "🧬  Proteins":      page_proteins,
    "📋  Sessions":      page_sessions,
    "📄  PDF Converter": page_converter,
}


def main():
    st.set_page_config(
        page_title="PHI-Weaver",
        page_icon="🧬",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(CSS, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown('<div class="brand">🧬 PHI-Weaver</div>', unsafe_allow_html=True)
        st.markdown('<div class="brand-sub">PHI-base curation system</div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        page = st.radio("nav", list(PAGES.keys()), label_visibility="collapsed")

    PAGES[page]()


if __name__ == "__main__":
    main()
