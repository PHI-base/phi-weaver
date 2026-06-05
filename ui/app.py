#!/usr/bin/env python3
import os
import sys
import subprocess
import tempfile
from pathlib import Path
from datetime import date

import streamlit as st
import pandas as pd

from db import get_db, q, run, save_extraction
from extract import extract as ai_extract, list_models as _list_models, pdf_to_text

STATUS_OPTS   = ["queued", "in_progress", "curated", "reviewed", "published"]
PROTEIN_TYPES = ["effector", "resistance", "virulence", "other"]
CONVERTER     = Path(__file__).parent.parent / "11-CLAUDE-AI" / "pdf-convert-skill" / "pdf-convert.py"

_STATUS_COLOR = {
    "queued":      ("#E8EAF6", "#3949AB"),
    "in_progress": ("#FEF3C7", "#92400E"),
    "curated":     ("#DBEAFE", "#1E40AF"),
    "reviewed":    ("#EDE9FE", "#5B21B6"),
    "published":   ("#1F3478", "#FFFFFF"),
}

CSS = """
<style>
/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1F3478 0%, #2B3A8C 100%);
    min-width: 200px !important;
    max-width: 200px !important;
}
[data-testid="stSidebar"] * { color: #D6DCEF !important; }
[data-testid="stSidebar"] .stSelectbox > div { background: rgba(255,255,255,0.1) !important; }

/* ── Tab bar ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    background: #EEF0F8;
    border-radius: 12px;
    padding: 4px 6px;
    margin-bottom: 1.8rem;
    border: 1px solid #C7CDE8;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    padding: 0.45rem 1.1rem;
    font-size: 0.84rem;
    font-weight: 500;
    color: #6B7280;
    border: none;
    background: transparent;
}
.stTabs [aria-selected="true"] {
    background: #1F3478 !important;
    color: #FFFFFF !important;
    font-weight: 600;
}
.stTabs [data-baseweb="tab-highlight"] { display: none; }
.stTabs [data-baseweb="tab-border"]    { display: none; }

/* ── Process stepper ── */
.proc-stepper {
    display: flex; align-items: center;
    padding: 1rem 1.5rem; margin-bottom: 1.8rem;
    background: #EEF0F8; border-radius: 12px; border: 1px solid #C7CDE8;
}
.proc-step { display: flex; align-items: center; gap: 0.45rem; white-space: nowrap; }
.step-num {
    width: 26px; height: 26px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.72rem; font-weight: 700; flex-shrink: 0;
}
.step-pending .step-num { background: #E5E7EB; color: #9CA3AF; }
.step-active  .step-num { background: #1F3478; color: #FFF; }
.step-done    .step-num { background: #3949AB; color: #FFF; }
.step-label { font-size: 0.82rem; font-weight: 500; }
.step-pending .step-label { color: #9CA3AF; }
.step-active  .step-label { color: #1F3478; font-weight: 700; }
.step-done    .step-label { color: #3949AB; }
.proc-conn { flex: 1; height: 2px; background: #E5E7EB; margin: 0 0.8rem; }
.proc-conn.done { background: #3949AB; }

/* ── Misc ── */
h1 { font-weight: 700; letter-spacing: -0.02em; }
h2, h3 { font-weight: 600; }
[data-testid="stMetric"] {
    background: #EEF0F8; border-radius: 10px;
    padding: 1rem 1.2rem; border: 1px solid #C7CDE8;
}
[data-testid="stMetricValue"] { color: #1F3478; font-weight: 700; }
.stage-card {
    background: #EEF0F8; border: 1px solid #C7CDE8;
    border-radius: 10px; padding: 1.1rem 0.8rem; text-align: center;
}
.stage-count { font-size: 2rem; font-weight: 700; color: #1F3478; line-height: 1; }
.stage-label { font-size: 0.72rem; color: #6B7280; text-transform: uppercase;
               letter-spacing: 0.07em; margin-top: 0.35rem; }
.badge { display: inline-block; padding: 0.18rem 0.65rem; border-radius: 9999px;
         font-size: 0.72rem; font-weight: 600; letter-spacing: 0.03em; }
.attention-row { display: flex; align-items: center; gap: 0.6rem; padding: 0.45rem 0;
                 border-bottom: 1px solid #D6DCEF; font-size: 0.88rem; }
.attention-row:last-child { border-bottom: none; }
hr { border-color: #D6DCEF; margin: 1.2rem 0; }
[data-testid="stExpander"]  { border: 1px solid #C7CDE8 !important; border-radius: 8px !important; }
[data-testid="stForm"]      { border: 1px solid #C7CDE8; border-radius: 10px; padding: 1.2rem 1.2rem 0.5rem; }
.brand     { font-size: 1.1rem; font-weight: 700; letter-spacing: -0.01em; }
.brand-sub { font-size: 0.72rem; opacity: 0.6; margin-top: -0.1rem; }
</style>
"""


# ── Helpers ────────────────────────────────────────────────────────────────────

@st.cache_data(ttl=30)
def list_models() -> list[str]:
    return _list_models()


def badge_html(status):
    bg, fg = _STATUS_COLOR.get(status, ("#E2E8F0", "#475569"))
    return f'<span class="badge" style="background:{bg};color:{fg}">{status.replace("_"," ")}</span>'


def convert_pdf(pdf_bytes: bytes, filename: str) -> str:
    """Run pdf-convert.py on uploaded bytes; return markdown text."""
    with tempfile.TemporaryDirectory() as tmp:
        pdf_path = Path(tmp) / filename
        out_dir  = Path(tmp) / "out"
        out_dir.mkdir()
        pdf_path.write_bytes(pdf_bytes)
        result = subprocess.run(
            [sys.executable, str(CONVERTER), str(pdf_path),
             "--output-dir", str(out_dir), "--no-index"],
            capture_output=True, text=True,
        )
        md_files = list(out_dir.glob("*.md"))
        if not md_files:
            raise RuntimeError(result.stderr[:400] or "Converter produced no output.")
        return md_files[0].read_text(encoding="utf-8")


def proc_reset():
    for k in ("proc_stage", "proc_markdown", "proc_extracted", "proc_filename"):
        st.session_state.pop(k, None)


def stepper_html(stage: str) -> str:
    steps = ["Upload", "Review", "Saved"]
    idx   = {"upload": 0, "review": 1, "done": 2}.get(stage, 0)
    parts = ['<div class="proc-stepper">']
    for i, label in enumerate(steps):
        cls  = "step-done" if i < idx else ("step-active" if i == idx else "step-pending")
        icon = "✓" if i < idx else str(i + 1)
        parts.append(f'<div class="proc-step {cls}"><span class="step-num">{icon}</span>'
                     f'<span class="step-label">{label}</span></div>')
        if i < len(steps) - 1:
            parts.append(f'<div class="proc-conn {"done" if i < idx else ""}"></div>')
    parts.append("</div>")
    return "".join(parts)


# ── Pages ──────────────────────────────────────────────────────────────────────

def page_dashboard():
    st.title("Dashboard")
    st.caption("Upload a paper → extract & review → mark article done in Articles → log in Sessions.")
    st.markdown("&nbsp;")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Articles",     q("SELECT COUNT(*) n FROM articles").iloc[0]["n"])
    c2.metric("Proteins",     q("SELECT COUNT(*) n FROM proteins").iloc[0]["n"])
    c3.metric("Sessions",     q("SELECT COUNT(*) n FROM curation_sessions").iloc[0]["n"])
    hours = q("SELECT SUM(session_duration_hours) h FROM curation_sessions").iloc[0]["h"]
    c4.metric("Hours logged", round(hours or 0, 1))

    st.markdown("<hr>", unsafe_allow_html=True)
    st.subheader("Article pipeline")
    counts = dict(zip(*[q("SELECT status, COUNT(*) n FROM articles GROUP BY status")[c]
                         for c in ["status", "n"]]))
    for col, s in zip(st.columns(len(STATUS_OPTS)), STATUS_OPTS):
        col.markdown(f'<div class="stage-card"><div class="stage-count">{counts.get(s, 0)}</div>'
                     f'<div class="stage-label">{s.replace("_"," ")}</div></div>',
                     unsafe_allow_html=True)
    st.markdown("&nbsp;")

    left, right = st.columns(2)
    with left:
        st.subheader("Recent sessions")
        recent = q("""SELECT session_date as date, proteins_curated as proteins,
                             interactions_added as interactions,
                             ROUND(session_duration_hours,1) as hours
                      FROM curation_sessions ORDER BY created_date DESC LIMIT 6""")
        st.dataframe(recent, width="stretch", hide_index=True) if not recent.empty \
            else st.caption("No sessions yet.")
    with right:
        st.subheader("Needs attention")
        pending = q("""SELECT title, status FROM articles WHERE status IN ('queued','in_progress')
                       ORDER BY CASE status WHEN 'in_progress' THEN 1 ELSE 2 END, pub_year DESC""")
        if pending.empty:
            st.caption("All clear.")
        else:
            st.markdown("".join(
                f'<div class="attention-row">{badge_html(r["status"])}'
                f'<span>{r["title"][:65]}{"…" if len(r["title"])>65 else ""}</span></div>'
                for _, r in pending.iterrows()
            ), unsafe_allow_html=True)


def page_process():
    stage = st.session_state.get("proc_stage", "upload")
    st.markdown(stepper_html(stage), unsafe_allow_html=True)

    model = st.session_state.get("selected_model")

    # ── Step 1: Upload ──────────────────────────────────────────────────────────
    if stage == "upload":
        st.subheader("Upload paper")
        uploaded = st.file_uploader("PDF", type="pdf", label_visibility="collapsed")

        if uploaded:
            st.markdown(f"**{uploaded.name}** — {uploaded.size / 1024:.0f} KB")
            st.markdown("&nbsp;")

            pipeline = st.radio(
                "Extraction pipeline",
                ["PDF → Markdown → AI", "PDF → Direct text → AI"],
                horizontal=True,
                help="Markdown pipeline handles complex layouts better. Direct is faster and may work better with some models.",
            )

            if not model:
                st.warning("Select a model in the sidebar before processing.")
                return

            if st.button("Process paper", type="primary"):
                pdf_bytes = uploaded.read()
                try:
                    with st.status("Processing…", expanded=True) as status:
                        if pipeline.startswith("PDF → Markdown"):
                            st.write("Converting PDF to markdown…")
                            text = convert_pdf(pdf_bytes, uploaded.name)
                            st.session_state.proc_markdown = text
                        else:
                            st.write("Extracting text directly from PDF…")
                            text = pdf_to_text(pdf_bytes)
                            st.session_state.proc_markdown = None

                        st.write(f"Extracting curation data with {model}…")
                        extracted = ai_extract(text, model=model)

                        status.update(label="Done — review below.", state="complete", expanded=False)

                    st.session_state.proc_markdown  = st.session_state.get("proc_markdown") or text
                    st.session_state.proc_extracted = extracted
                    st.session_state.proc_filename  = uploaded.name
                    st.session_state.proc_stage     = "review"
                    st.rerun()

                except RuntimeError as e:
                    st.error(str(e))

    # ── Step 2: Review ──────────────────────────────────────────────────────────
    elif stage == "review":
        data = st.session_state.proc_extracted
        fname = st.session_state.get("proc_filename", "paper.pdf")
        st.subheader("Review extracted data")
        st.caption("Edit any field before saving. The data below was extracted from the converted markdown.")

        # Article
        with st.expander("Article metadata", expanded=True):
            art = data.get("article", {})
            c1, c2 = st.columns([3, 1])
            art["title"]    = c1.text_input("Title",   value=art.get("title") or "")
            art["pub_year"] = c2.number_input("Year",  value=int(art.get("pub_year") or date.today().year),
                                              min_value=1990, max_value=2030, step=1)
            c3, c4, c5 = st.columns(3)
            art["authors"]  = c3.text_input("Authors", value=art.get("authors") or "")
            art["journal"]  = c4.text_input("Journal", value=art.get("journal") or "")
            art["pmid"]     = c5.text_input("PMID",    value=art.get("pmid") or "")

        # Species
        with st.expander("Species", expanded=True):
            sp_l, sp_r = st.columns(2)
            with sp_l:
                st.markdown("**Pathogens**")
                for i, p in enumerate(data.get("pathogens", [])):
                    p["name"] = st.text_input(f"Pathogen {i+1}", value=p["name"], key=f"path_{i}")
            with sp_r:
                st.markdown("**Hosts**")
                for i, h in enumerate(data.get("hosts", [])):
                    h["name"] = st.text_input(f"Host {i+1}", value=h["name"], key=f"host_{i}")

        # Proteins
        with st.expander(f"Proteins ({len(data.get('proteins', []))} found)", expanded=True):
            proteins = data.get("proteins", [])
            if proteins:
                df = pd.DataFrame(proteins).reindex(
                    columns=["gene_name", "gene_id", "species", "protein_type", "function_summary", "uniprot_id"]
                )
                edited = st.data_editor(
                    df,
                    column_config={
                        "gene_name":       st.column_config.TextColumn("Gene"),
                        "gene_id":         st.column_config.TextColumn("Locus tag"),
                        "species":         st.column_config.TextColumn("Species"),
                        "protein_type":    st.column_config.SelectboxColumn("Type", options=PROTEIN_TYPES),
                        "function_summary":st.column_config.TextColumn("Function", width="large"),
                        "uniprot_id":      st.column_config.TextColumn("UniProt"),
                    },
                    width="stretch", hide_index=True, num_rows="dynamic",
                )
                data["proteins"] = edited.to_dict("records")
            else:
                st.caption("No proteins detected.")

        # Curation notes
        data["curation_notes"] = st.text_area("Curation notes",
                                               value=data.get("curation_notes") or "", height=80)

        st.markdown("&nbsp;")
        col_save, col_md, col_back = st.columns([2, 2, 1])

        if col_save.button("Save to database", type="primary", use_container_width=True):
            try:
                article_id = save_extraction(data)
                st.session_state.proc_saved_id = article_id
                st.session_state.proc_stage    = "done"
                st.rerun()
            except Exception as e:
                st.error(f"Save failed: {e}")

        md_text = st.session_state.get("proc_markdown", "")
        col_md.download_button("⬇ Download markdown", md_text,
                               file_name=Path(fname).stem + ".md",
                               mime="text/markdown", use_container_width=True)

        if col_back.button("← Back", use_container_width=True):
            proc_reset()
            st.rerun()

    # ── Step 3: Done ────────────────────────────────────────────────────────────
    elif stage == "done":
        article_id = st.session_state.get("proc_saved_id")
        st.success(f"Saved — article ID {article_id}. Head to **Articles** to update its status as you curate.")
        st.markdown("&nbsp;")
        if st.button("Process another paper", type="primary"):
            proc_reset()
            st.rerun()


def page_articles():
    st.title("Articles")

    with st.expander("Add article manually"):
        with st.form("add_article", clear_on_submit=True):
            title = st.text_input("Title *")
            c1, c2 = st.columns(2)
            pmid  = c1.text_input("PMID")
            year  = c2.number_input("Year", 1990, 2030, value=date.today().year, step=1)
            c3, c4 = st.columns(2)
            journal = c3.text_input("Journal")
            authors = c4.text_input("Authors")
            if st.form_submit_button("Add", type="primary"):
                if not title:
                    st.error("Title is required.")
                else:
                    run("INSERT INTO articles (pmid,title,journal,pub_year,authors,status,curator)"
                        " VALUES (?,?,?,?,?,'queued','curator')",
                        (pmid or None, title, journal or None, year, authors or None))
                    st.success("Article added.")
                    st.rerun()

    st.markdown("&nbsp;")
    status_filter = st.segmented_control(
        "Filter", ["All"] + [s.replace("_", " ").title() for s in STATUS_OPTS], default="All"
    )
    filter_val = None if status_filter == "All" else status_filter.lower().replace(" ", "_")

    sql = "SELECT id, title, pmid, journal, pub_year as year, authors, status, priority FROM articles"
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
            "id":      None,
            "title":   st.column_config.TextColumn("Title", width="large"),
            "pmid":    st.column_config.TextColumn("PMID", width="small"),
            "journal": st.column_config.TextColumn("Journal"),
            "year":    st.column_config.NumberColumn("Year", width="small"),
            "authors": st.column_config.TextColumn("Authors"),
            "status":  st.column_config.SelectboxColumn("Status", options=STATUS_OPTS, width="medium"),
            "priority":st.column_config.SelectboxColumn("Priority", options=["low","medium","high"], width="small"),
        },
        disabled=["title", "pmid", "journal", "year", "authors"],
        hide_index=True, width="stretch",
    )

    changed = articles[
        (articles["status"] != edited["status"]) | (articles["priority"] != edited["priority"])
    ]
    if not changed.empty:
        for i, row in changed.iterrows():
            run("UPDATE articles SET status=?, priority=?, updated_date=CURRENT_TIMESTAMP WHERE id=?",
                (edited.at[i, "status"], edited.at[i, "priority"], row["id"]))
        st.toast(f"Saved {len(changed)} change(s).", icon="✅")
        st.rerun()


def page_proteins():
    st.title("Proteins")

    c1, c2, c3 = st.columns([3, 2, 1])
    search = c1.text_input("Search", placeholder="gene name, function, ID…", label_visibility="collapsed")
    species_opts = q("SELECT DISTINCT name FROM species ORDER BY name")["name"].tolist()
    species_filter = c2.selectbox("Species", ["All species"] + species_opts, label_visibility="collapsed")
    type_filter    = c3.selectbox("Type", ["All"] + PROTEIN_TYPES, label_visibility="collapsed")

    sql = """SELECT p.gene_id, p.gene_name, s.name as species,
                    p.protein_type as type, p.uniprot_id,
                    p.function_summary as function
             FROM proteins p JOIN species s ON p.species_id = s.id WHERE 1=1"""
    params = []
    if search:
        sql += " AND (p.gene_name LIKE ? OR p.function_summary LIKE ? OR p.gene_id LIKE ?)"
        params += [f"%{search}%"] * 3
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

    st.dataframe(proteins, width="stretch", hide_index=True,
                 column_config={
                     "gene_id":   st.column_config.TextColumn("Gene ID"),
                     "gene_name": st.column_config.TextColumn("Name"),
                     "species":   st.column_config.TextColumn("Species"),
                     "type":      st.column_config.TextColumn("Type", width="small"),
                     "uniprot_id":st.column_config.TextColumn("UniProt", width="small"),
                     "function":  st.column_config.TextColumn("Function", width="large"),
                 })
    st.caption(f"{len(proteins)} protein{'s' if len(proteins) != 1 else ''}")


def page_sessions():
    st.title("Sessions")

    with st.form("log_session", clear_on_submit=True):
        st.subheader("Log session")
        c1, c2, c3 = st.columns(3)
        proteins     = c1.number_input("Proteins curated",  min_value=0, value=0, step=1)
        interactions = c2.number_input("Interactions added", min_value=0, value=0, step=1)
        hours        = c3.number_input("Hours", min_value=0.0, step=0.5, value=1.0)
        notes = st.text_area("Notes", placeholder="What did you work on today?")
        if st.form_submit_button("Log session", type="primary"):
            run("""INSERT INTO curation_sessions
                   (session_date, curator, proteins_curated, interactions_added,
                    session_duration_hours, notes)
                   VALUES (?, 'curator', ?, ?, ?, ?)""",
                (date.today(), proteins, interactions, hours, notes or None))
            st.success("Session logged.")
            st.rerun()

    st.markdown("<hr>", unsafe_allow_html=True)
    st.subheader("History")
    sessions = q("""SELECT session_date as date, curator, proteins_curated as proteins,
                           interactions_added as interactions,
                           ROUND(session_duration_hours,1) as hours, notes
                    FROM curation_sessions ORDER BY created_date DESC""")
    if sessions.empty:
        st.caption("No sessions yet.")
        return

    st.dataframe(sessions, width="stretch", hide_index=True)
    st.markdown("&nbsp;")
    totals = q("""SELECT SUM(proteins_curated) p, SUM(interactions_added) i,
                         ROUND(SUM(session_duration_hours),1) h
                  FROM curation_sessions""").iloc[0]
    c1, c2, c3 = st.columns(3)
    c1.metric("Total proteins curated", int(totals["p"] or 0))
    c2.metric("Total interactions",     int(totals["i"] or 0))
    c3.metric("Total hours",            totals["h"] or 0)


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    st.set_page_config(
        page_title="PHI-Weaver",
        page_icon="🧬",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    st.markdown(CSS, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown('<div class="brand">🧬 PHI-Weaver</div>', unsafe_allow_html=True)
        st.markdown('<div class="brand-sub">PHI-base curation</div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        ml, mr = st.columns([3, 1])
        ml.markdown('<div style="font-size:0.72rem;opacity:0.7">AI MODEL</div>', unsafe_allow_html=True)
        if mr.button("↺", help="Refresh", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

        available = list_models()
        if available:
            st.selectbox("model", available, key="selected_model", label_visibility="collapsed")
        else:
            st.markdown('<div style="font-size:0.72rem;color:#F59E0B">⚠ API unreachable</div>',
                        unsafe_allow_html=True)

    tabs = st.tabs(["🏠  Dashboard", "🔬  Process Paper", "📚  Articles", "🧬  Proteins", "📋  Sessions"])
    with tabs[0]: page_dashboard()
    with tabs[1]: page_process()
    with tabs[2]: page_articles()
    with tabs[3]: page_proteins()
    with tabs[4]: page_sessions()


if __name__ == "__main__":
    main()
