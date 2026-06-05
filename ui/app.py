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
from export import to_json_str

STATUS_OPTS   = ["queued", "in_progress", "curated", "reviewed", "published"]
PROTEIN_TYPES = ["effector", "resistance", "virulence", "other"]
ALLELE_TYPES  = ["deletion", "substitution", "insertion", "wild type", "unknown", "other"]
EXPRESSION    = ["null", "decreased", "wild type product level", "increased", "not assayed"]
EV_CODES      = ["IMP", "IDA", "IGI", "IPI", "IEP", "IBA", "IC", "ND"]
CONVERTER     = Path(__file__).parent.parent / "11-CLAUDE-AI" / "pdf-convert-skill" / "pdf-convert.py"

_STATUS_COLOR = {
    "queued":      ("#F1F5F9", "#475569"),
    "in_progress": ("#FEF9C3", "#854D0E"),
    "curated":     ("#DCFCE7", "#166534"),
    "reviewed":    ("#DBEAFE", "#1D4ED8"),
    "published":   ("#1F3478", "#FFFFFF"),
}

CSS = """
<style>
/* ── Remove sidebar entirely ── */
[data-testid="stSidebar"],
[data-testid="collapsedControl"] { display: none !important; }

/* ── Layout ── */
.main .block-container {
    padding-top: 1.25rem;
    padding-left: 2.5rem;
    padding-right: 2.5rem;
    max-width: 1300px;
}

/* ── App header ── */
.app-header {
    display: flex;
    align-items: baseline;
    gap: 0.9rem;
    padding-bottom: 0.75rem;
    margin-bottom: 0;
}
.app-name {
    font-size: 1.3rem;
    font-weight: 800;
    letter-spacing: -0.04em;
    color: #1F3478;
}
.app-name em { font-style: normal; color: #3B82F6; }
.app-divider { color: #CBD5E1; }
.app-sub {
    font-size: 0.72rem;
    font-weight: 600;
    color: #94A3B8;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

/* ── Tabs: underline style ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 0;
    background: transparent;
    border-radius: 0;
    border-bottom: 1px solid #E2E8F0;
    padding: 0;
    margin-bottom: 2rem;
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    border-radius: 0;
    padding: 0.6rem 1.2rem;
    font-size: 0.875rem;
    font-weight: 500;
    color: #64748B;
    border: none;
    border-bottom: 2px solid transparent;
    margin-bottom: -1px;
}
.stTabs [aria-selected="true"] {
    background: transparent !important;
    color: #1F3478 !important;
    font-weight: 600;
    border-bottom: 2px solid #1F3478 !important;
}
.stTabs [data-baseweb="tab-highlight"],
.stTabs [data-baseweb="tab-border"] { display: none; }

/* ── KPI cards ── */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 0.875rem;
    margin-bottom: 2rem;
}
.kpi-card {
    background: #fff;
    border: 1px solid #E2E8F0;
    border-radius: 10px;
    padding: 1rem 1.25rem;
    box-shadow: 0 1px 3px rgba(15,23,42,.05);
}
.kpi-value {
    font-size: 2rem;
    font-weight: 700;
    color: #1F3478;
    line-height: 1;
    letter-spacing: -0.03em;
}
.kpi-label {
    font-size: 0.72rem;
    font-weight: 600;
    color: #94A3B8;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    margin-top: 0.3rem;
}

/* ── Pipeline ── */
.pipeline {
    display: flex;
    align-items: stretch;
    gap: 0;
    margin-bottom: 2rem;
    border: 1px solid #E2E8F0;
    border-radius: 10px;
    overflow: hidden;
}
.pipe-stage {
    flex: 1;
    padding: 0.9rem 0.75rem;
    text-align: center;
    background: #fff;
    border-right: 1px solid #E2E8F0;
    position: relative;
}
.pipe-stage:last-child { border-right: none; }
.pipe-stage.has-items { background: #F8FAFF; }
.pipe-n {
    font-size: 1.6rem;
    font-weight: 700;
    color: #1F3478;
    line-height: 1;
    letter-spacing: -0.03em;
}
.pipe-n.zero { color: #CBD5E1; }
.pipe-label {
    font-size: 0.68rem;
    font-weight: 600;
    color: #94A3B8;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    margin-top: 0.3rem;
}

/* ── Section labels ── */
.section-title {
    font-size: 0.72rem;
    font-weight: 700;
    color: #94A3B8;
    text-transform: uppercase;
    letter-spacing: 0.09em;
    margin-bottom: 0.75rem;
    display: block;
}

/* ── Attention list ── */
.attn-item {
    display: flex;
    align-items: flex-start;
    gap: 0.75rem;
    padding: 0.65rem 0;
    border-bottom: 1px solid #F1F5F9;
}
.attn-item:last-child { border-bottom: none; padding-bottom: 0; }
.attn-text { flex: 1; min-width: 0; }
.attn-title {
    font-size: 0.875rem;
    font-weight: 500;
    color: #1E293B;
    line-height: 1.3;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.attn-meta { font-size: 0.72rem; color: #94A3B8; margin-top: 0.1rem; }

/* ── Activity list ── */
.activity-item {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 0.55rem 0;
    border-bottom: 1px solid #F1F5F9;
    font-size: 0.84rem;
}
.activity-item:last-child { border-bottom: none; }
.activity-date { color: #94A3B8; font-size: 0.75rem; flex-shrink: 0; width: 88px; }
.activity-nums { display: flex; gap: 0.75rem; margin-left: auto; flex-shrink: 0; }
.activity-chip {
    font-size: 0.72rem;
    color: #64748B;
    background: #F1F5F9;
    padding: 0.15rem 0.5rem;
    border-radius: 4px;
    font-weight: 500;
}

/* ── Article count bar ── */
.art-summary {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 1rem;
    flex-wrap: wrap;
}
.art-total {
    font-size: 0.8rem;
    font-weight: 600;
    color: #334155;
    margin-right: 0.25rem;
}
.art-chip {
    font-size: 0.72rem;
    padding: 0.2rem 0.55rem;
    border-radius: 5px;
    font-weight: 600;
    cursor: pointer;
}

/* ── Status badges ── */
.badge {
    display: inline-flex;
    align-items: center;
    padding: 0.18rem 0.6rem;
    border-radius: 5px;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.02em;
    white-space: nowrap;
    flex-shrink: 0;
}

/* ── Process stepper ── */
.proc-stepper {
    display: flex;
    align-items: center;
    padding: 0.875rem 1.5rem;
    margin-bottom: 1.75rem;
    background: #F8FAFC;
    border-radius: 10px;
    border: 1px solid #E2E8F0;
}
.proc-step { display: flex; align-items: center; gap: 0.45rem; white-space: nowrap; }
.step-num {
    width: 24px; height: 24px;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.68rem; font-weight: 700; flex-shrink: 0;
}
.step-pending .step-num { background: #E2E8F0; color: #94A3B8; }
.step-active  .step-num { background: #1F3478; color: #FFF; }
.step-done    .step-num { background: #059669; color: #FFF; }
.step-label { font-size: 0.8rem; font-weight: 500; }
.step-pending .step-label { color: #94A3B8; }
.step-active  .step-label { color: #1F3478; font-weight: 700; }
.step-done    .step-label { color: #059669; }
.proc-conn { flex: 1; height: 1px; background: #E2E8F0; margin: 0 0.75rem; }
.proc-conn.done { background: #059669; }

/* ── Model picker (in-page) ── */
.model-row {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.75rem 1rem;
    background: #F8FAFC;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    margin-bottom: 1rem;
}
.model-label {
    font-size: 0.72rem;
    font-weight: 700;
    color: #64748B;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    white-space: nowrap;
}
.model-unavailable { font-size: 0.78rem; color: #D97706; font-weight: 500; }

/* ── Session stat cards ── */
.stat-row {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 0.875rem;
    margin-bottom: 1.75rem;
}
.stat-card {
    background: #fff;
    border: 1px solid #E2E8F0;
    border-radius: 10px;
    padding: 0.875rem 1.1rem;
    box-shadow: 0 1px 3px rgba(15,23,42,.04);
}
.stat-val { font-size: 1.6rem; font-weight: 700; color: #1F3478; letter-spacing: -0.03em; line-height: 1; }
.stat-lbl { font-size: 0.7rem; font-weight: 600; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.07em; margin-top: 0.25rem; }

/* ── Card containers ── */
.content-card {
    background: #fff;
    border: 1px solid #E2E8F0;
    border-radius: 10px;
    padding: 1.25rem;
    box-shadow: 0 1px 3px rgba(15,23,42,.04);
    margin-bottom: 1rem;
}

/* ── Typography ── */
h1 { font-size: 1.4rem !important; font-weight: 700 !important; letter-spacing: -0.025em !important; color: #0F172A !important; margin-bottom: 1.25rem !important; }
h2 { font-size: 1rem !important; font-weight: 600 !important; color: #1E293B !important; }
h3 { font-size: 0.9rem !important; font-weight: 600 !important; color: #334155 !important; }

/* ── Forms ── */
[data-testid="stForm"] { border: 1px solid #E2E8F0; border-radius: 10px; padding: 1.2rem 1.2rem 0.6rem; background: #FAFBFF; }
[data-testid="stExpander"] { border: 1px solid #E2E8F0 !important; border-radius: 8px !important; }

/* ── Divider ── */
hr { border: none; border-top: 1px solid #F1F5F9; margin: 1.5rem 0; }
</style>
"""


# ── Helpers ────────────────────────────────────────────────────────────────────

@st.cache_data(ttl=30)
def list_models() -> list[str]:
    return _list_models()


def badge_html(status: str) -> str:
    bg, fg = _STATUS_COLOR.get(status, ("#F1F5F9", "#475569"))
    return f'<span class="badge" style="background:{bg};color:{fg}">{status.replace("_"," ")}</span>'


def kpi(value, label: str) -> str:
    return (f'<div class="kpi-card">'
            f'<div class="kpi-value">{value}</div>'
            f'<div class="kpi-label">{label}</div>'
            f'</div>')


def convert_pdf(pdf_bytes: bytes, filename: str) -> str:
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
    for k in ("proc_stage", "proc_markdown", "proc_extracted",
              "proc_filename", "proc_saved_id", "proc_model", "proc_pipeline"):
        st.session_state.pop(k, None)


def stepper_html(stage: str) -> str:
    steps = ["Upload", "Review", "Saved"]
    idx   = {"upload": 0, "review": 1, "done": 2}.get(stage, 0)
    parts = ['<div class="proc-stepper">']
    for i, label in enumerate(steps):
        cls  = "step-done" if i < idx else ("step-active" if i == idx else "step-pending")
        icon = "✓" if i < idx else str(i + 1)
        parts.append(f'<div class="proc-step {cls}">'
                     f'<span class="step-num">{icon}</span>'
                     f'<span class="step-label">{label}</span></div>')
        if i < len(steps) - 1:
            parts.append(f'<div class="proc-conn {"done" if i < idx else ""}"></div>')
    parts.append("</div>")
    return "".join(parts)


def _model_picker():
    """Inline model picker used inside Process Paper."""
    available = list_models()
    ml, mr, _ = st.columns([1, 3, 4])
    ml.markdown('<div class="model-label" style="padding-top:0.45rem">Model</div>',
                unsafe_allow_html=True)
    if available:
        mr.selectbox("model", available, key="selected_model", label_visibility="collapsed")
    else:
        mr.markdown('<span class="model-unavailable">API unreachable — check bridge</span>',
                    unsafe_allow_html=True)
    if _:
        pass
    # refresh button
    with ml:
        pass
    if st.button("↺", key="refresh_models", help="Refresh model list"):
        st.cache_data.clear()
        st.rerun()


def _df_editor(df, key, column_config, editable_cols=None):
    disabled = [c for c in df.columns if editable_cols is not None and c not in editable_cols]
    return st.data_editor(df, column_config=column_config, disabled=disabled,
                          hide_index=True, width="stretch", num_rows="dynamic", key=key)


# ── Review sub-sections (unchanged logic, same as before) ─────────────────────

def _review_article(data):
    art = data.setdefault("article", {})
    c1, c2 = st.columns([3, 1])
    art["title"]    = c1.text_input("Title", value=art.get("title") or "")
    art["pub_year"] = c2.number_input("Year", value=int(art.get("pub_year") or date.today().year),
                                      min_value=1990, max_value=2030, step=1)
    c3, c4, c5, c6 = st.columns(4)
    art["authors"] = c3.text_input("Authors", value=art.get("authors") or "")
    art["journal"] = c4.text_input("Journal", value=art.get("journal") or "")
    art["pmid"]    = c5.text_input("PMID",    value=art.get("pmid") or "")
    art["doi"]     = c6.text_input("DOI",     value=art.get("doi") or "")


def _review_organisms(data):
    orgs = data.setdefault("organisms", {"pathogens": [], "hosts": []})
    cl, cr = st.columns(2)
    with cl:
        st.markdown("**Pathogens**")
        for i, p in enumerate(orgs.get("pathogens", [])):
            a, b = st.columns([2, 1])
            p["name"]     = a.text_input("Name",     value=p.get("name") or "",    key=f"pn_{i}")
            p["taxon_id"] = b.number_input("Taxon",  value=int(p.get("taxon_id") or 0), min_value=0, step=1, key=f"pt_{i}")
            raw = st.text_input("Strains", value=", ".join(p.get("strains") or []), key=f"ps_{i}")
            p["strains"] = [s.strip() for s in raw.split(",") if s.strip()]
    with cr:
        st.markdown("**Hosts**")
        for i, h in enumerate(orgs.get("hosts", [])):
            a, b = st.columns([2, 1])
            h["name"]     = a.text_input("Name",     value=h.get("name") or "",    key=f"hn_{i}")
            h["taxon_id"] = b.number_input("Taxon",  value=int(h.get("taxon_id") or 0), min_value=0, step=1, key=f"ht_{i}")
            raw = st.text_input("Strains", value=", ".join(h.get("strains") or []), key=f"hs_{i}")
            h["strains"] = [s.strip() for s in raw.split(",") if s.strip()]


def _review_genes(data):
    genes = data.get("genes", [])
    if not genes:
        st.caption("No genes extracted.")
        return
    df = pd.DataFrame([{
        "gene_name": g.get("gene_name"), "systematic_id": g.get("systematic_id"),
        "uniprot_accession": g.get("uniprot_accession"), "organism_name": g.get("organism_name"),
        "taxon_id": g.get("taxon_id"), "product": g.get("product"),
        "is_effector": g.get("is_effector", False),
    } for g in genes])
    edited = _df_editor(df, "genes_ed", {
        "gene_name":         st.column_config.TextColumn("Gene"),
        "systematic_id":     st.column_config.TextColumn("Systematic ID"),
        "uniprot_accession": st.column_config.TextColumn("UniProt"),
        "organism_name":     st.column_config.TextColumn("Organism"),
        "taxon_id":          st.column_config.NumberColumn("Taxon ID", width="small"),
        "product":           st.column_config.TextColumn("Product", width="large"),
        "is_effector":       st.column_config.CheckboxColumn("Effector?"),
    }, editable_cols=list(df.columns))
    for i, row in edited.iterrows():
        if i < len(data["genes"]):
            data["genes"][i].update(row.to_dict())
    go_all = [{"gene": g.get("gene_name"), **a}
               for g in genes for a in g.get("go_annotations", [])]
    if go_all:
        st.markdown("**GO annotations**")
        st.dataframe(pd.DataFrame(go_all), width="stretch", hide_index=True)


def _review_alleles(data):
    alleles = data.get("alleles", [])
    if not alleles:
        st.caption("No alleles extracted.")
        return
    df = pd.DataFrame([{
        "id": a.get("id"), "gene_name": a.get("gene_name"),
        "systematic_id": a.get("gene_systematic_id"), "name": a.get("name"),
        "type": a.get("type", "unknown"), "description": a.get("description"),
        "expression": a.get("expression"),
    } for a in alleles])
    edited = _df_editor(df, "alleles_ed", {
        "id": None,
        "gene_name":     st.column_config.TextColumn("Gene"),
        "systematic_id": st.column_config.TextColumn("Systematic ID"),
        "name":          st.column_config.TextColumn("Allele name"),
        "type":          st.column_config.SelectboxColumn("Type", options=ALLELE_TYPES),
        "description":   st.column_config.TextColumn("Description"),
        "expression":    st.column_config.SelectboxColumn("Expression", options=EXPRESSION),
    }, editable_cols=["gene_name", "systematic_id", "name", "type", "description", "expression"])
    for i, row in edited.iterrows():
        if i < len(data["alleles"]):
            data["alleles"][i].update({
                "gene_name": row["gene_name"], "gene_systematic_id": row["systematic_id"],
                "name": row["name"], "type": row["type"],
                "description": row["description"], "expression": row["expression"],
            })


def _review_genotypes(data):
    for section, label in [("pathogen_genotypes", "Pathogen genotypes"),
                            ("host_genotypes",     "Host genotypes")]:
        genos = data.get(section, [])
        st.markdown(f"**{label}** ({len(genos)})")
        if not genos:
            st.caption("None extracted.")
            continue
        df = pd.DataFrame([{
            "id": g.get("id"), "label": g.get("label"),
            "organism": g.get("organism_name"), "strain": g.get("strain"),
            "alleles": ", ".join(g.get("allele_ids", [])),
            "background": g.get("background", ""), "is_wild_type": g.get("is_wild_type", False),
        } for g in genos])
        _df_editor(df, f"{section}_ed", {
            "id": None,
            "label":       st.column_config.TextColumn("Label"),
            "organism":    st.column_config.TextColumn("Organism"),
            "strain":      st.column_config.TextColumn("Strain"),
            "alleles":     st.column_config.TextColumn("Allele IDs"),
            "background":  st.column_config.TextColumn("Background"),
            "is_wild_type":st.column_config.CheckboxColumn("Wild type?"),
        }, editable_cols=["label", "organism", "strain", "background", "is_wild_type"])
        for g in genos:
            anns = g.get("phenotype_annotations", [])
            if anns:
                with st.expander(f"Phenotypes — {g.get('label', g['id'])} ({len(anns)})"):
                    st.dataframe(pd.DataFrame(anns), width="stretch", hide_index=True)
        st.markdown("&nbsp;")


def _review_metagenotypes(data):
    mgs = data.get("metagenotypes", [])
    if not mgs:
        st.caption("No metagenotypes extracted.")
        return
    for mg in mgs:
        label = (f"{'[control]  ' if mg.get('is_control') else ''}"
                 f"{mg['id']}  ·  {mg.get('pathogen_genotype_id')} × {mg.get('host_genotype_id')}")
        with st.expander(label, expanded=not mg.get("is_control")):
            ia = mg.get("interaction_annotations", [])
            da = mg.get("disease_annotations", [])
            if ia:
                st.markdown("*Interaction phenotypes*")
                _df_editor(pd.DataFrame(ia), f"ia_{mg['id']}", {
                    "phipo_term":        st.column_config.TextColumn("PHIPO term", width="large"),
                    "evidence_code":     st.column_config.SelectboxColumn("Evidence", options=EV_CODES),
                    "host_tissue":       st.column_config.TextColumn("Tissue"),
                    "host_tissue_bto":   st.column_config.TextColumn("BTO ID"),
                    "infective_ability": st.column_config.TextColumn("Infective ability"),
                    "conditions":        st.column_config.ListColumn("Conditions"),
                    "figure":            st.column_config.TextColumn("Figure"),
                    "comment":           st.column_config.TextColumn("Comment"),
                    "compared_to_control_id": None,
                }, editable_cols=["phipo_term", "evidence_code", "host_tissue",
                                   "host_tissue_bto", "infective_ability", "figure", "comment"])
            if da:
                st.markdown("*Disease annotations*")
                _df_editor(pd.DataFrame(da), f"da_{mg['id']}", {
                    "disease_name":    st.column_config.TextColumn("Disease (PHIDO)", width="large"),
                    "host_tissue":     st.column_config.TextColumn("Tissue"),
                    "host_tissue_bto": st.column_config.TextColumn("BTO ID"),
                    "figure":          st.column_config.TextColumn("Figure"),
                }, editable_cols=["disease_name", "host_tissue", "host_tissue_bto", "figure"])
            if not ia and not da:
                st.caption("No annotations.")


# ── Pages ──────────────────────────────────────────────────────────────────────

def page_dashboard():
    st.title("Dashboard")

    # KPI row
    total_articles = int(q("SELECT COUNT(*) n FROM articles").iloc[0]["n"])
    total_proteins = int(q("SELECT COUNT(*) n FROM proteins").iloc[0]["n"])
    total_sessions = int(q("SELECT COUNT(*) n FROM curation_sessions").iloc[0]["n"])
    hours_raw      = q("SELECT SUM(session_duration_hours) h FROM curation_sessions").iloc[0]["h"]
    total_hours    = round(hours_raw or 0, 1)

    st.markdown(
        f'<div class="kpi-grid">'
        f'{kpi(total_articles, "Articles")}'
        f'{kpi(total_proteins, "Proteins")}'
        f'{kpi(total_sessions, "Sessions")}'
        f'{kpi(total_hours, "Hours logged")}'
        f'</div>',
        unsafe_allow_html=True,
    )

    # Pipeline
    st.markdown('<span class="section-title">Article pipeline</span>', unsafe_allow_html=True)
    counts_df = q("SELECT status, COUNT(*) n FROM articles GROUP BY status")
    counts    = dict(zip(counts_df["status"], counts_df["n"]))
    stages    = [(s, counts.get(s, 0)) for s in STATUS_OPTS]
    pipe_html = '<div class="pipeline">'
    for s, n in stages:
        has = "has-items" if n > 0 else ""
        pipe_html += (f'<div class="pipe-stage {has}">'
                      f'<div class="pipe-n {"zero" if n == 0 else ""}">{n}</div>'
                      f'<div class="pipe-label">{s.replace("_", " ")}</div>'
                      f'</div>')
    pipe_html += "</div>"
    st.markdown(pipe_html, unsafe_allow_html=True)

    # Two-column lower section
    col_l, col_r = st.columns(2, gap="large")

    with col_l:
        st.markdown('<span class="section-title">Needs attention</span>', unsafe_allow_html=True)
        pending = q("""
            SELECT title, status, journal, pub_year, authors
            FROM articles WHERE status IN ('queued','in_progress')
            ORDER BY CASE status WHEN 'in_progress' THEN 1 ELSE 2 END, pub_year DESC
        """)
        if pending.empty:
            st.caption("Nothing pending — all clear.")
        else:
            html = ""
            for _, r in pending.iterrows():
                meta_parts = [p for p in [r.get("authors", ""), r.get("journal", ""),
                               str(r.get("pub_year", "")) if r.get("pub_year") else ""] if p]
                meta = " · ".join(meta_parts[:2])
                html += (f'<div class="attn-item">'
                         f'{badge_html(r["status"])}'
                         f'<div class="attn-text">'
                         f'<div class="attn-title">{r["title"][:70]}{"…" if len(r["title"]) > 70 else ""}</div>'
                         f'<div class="attn-meta">{meta}</div>'
                         f'</div></div>')
            st.markdown(html, unsafe_allow_html=True)

    with col_r:
        st.markdown('<span class="section-title">Recent activity</span>', unsafe_allow_html=True)
        recent = q("""
            SELECT session_date, proteins_curated, interactions_added,
                   ROUND(session_duration_hours, 1) as hours, notes
            FROM curation_sessions ORDER BY created_date DESC LIMIT 6
        """)
        if recent.empty:
            st.caption("No sessions recorded yet.")
        else:
            html = ""
            for _, r in recent.iterrows():
                notes_preview = (str(r.get("notes") or "")[:40] + "…") if r.get("notes") else "—"
                html += (f'<div class="activity-item">'
                         f'<span class="activity-date">{r["session_date"]}</span>'
                         f'<span style="font-size:0.82rem;color:#334155;flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{notes_preview}</span>'
                         f'<span class="activity-nums">'
                         f'<span class="activity-chip">{int(r["proteins"] or 0)}p</span>'
                         f'<span class="activity-chip">{int(r["interactions"] or 0)}i</span>'
                         f'<span class="activity-chip">{r["hours"] or 0}h</span>'
                         f'</span></div>')
            st.markdown(html, unsafe_allow_html=True)


def page_process():
    stage = st.session_state.get("proc_stage", "upload")
    st.markdown(stepper_html(stage), unsafe_allow_html=True)

    # ── Upload ──────────────────────────────────────────────────────────────
    if stage == "upload":
        st.title("Process paper")
        st.caption("Upload a PDF to convert and extract PHI-Canto curation data.")

        uploaded = st.file_uploader("", type="pdf", label_visibility="collapsed")

        if not uploaded:
            return

        st.markdown(f"**{uploaded.name}** &nbsp;·&nbsp; {uploaded.size / 1024:.0f} KB",
                    unsafe_allow_html=True)
        st.markdown("&nbsp;")

        pipeline = st.radio(
            "Extraction pipeline",
            ["PDF → Markdown → AI", "PDF → Direct text → AI"],
            horizontal=True,
            help="Markdown handles complex multi-column layouts. Direct is faster and may suit some models better.",
        )

        st.markdown("&nbsp;")

        # Model picker — inline, no sidebar needed
        available = list_models()
        mc1, mc2, mc3 = st.columns([1, 3, 6])
        mc1.markdown('<p style="font-size:0.75rem;font-weight:700;color:#64748B;text-transform:uppercase;letter-spacing:.06em;padding-top:.55rem;margin:0">Model</p>',
                     unsafe_allow_html=True)
        if available:
            mc2.selectbox("model_sel", available, key="selected_model", label_visibility="collapsed")
        else:
            mc2.markdown('<span style="font-size:0.8rem;color:#D97706;padding-top:.4rem;display:block">API unreachable</span>',
                         unsafe_allow_html=True)
        if mc3.button("↺ Refresh models", key="refresh_models"):
            st.cache_data.clear()
            st.rerun()

        model = st.session_state.get("selected_model")
        if not model:
            st.warning("No model available — check the API connection above.")
            return

        st.markdown("&nbsp;")
        if st.button("Process paper", type="primary"):
            pdf_bytes = uploaded.read()
            try:
                with st.status("Processing…", expanded=True) as status:
                    if pipeline.startswith("PDF → Markdown"):
                        st.write("Converting PDF to markdown…")
                        text = convert_pdf(pdf_bytes, uploaded.name)
                    else:
                        st.write("Extracting text from PDF…")
                        text = pdf_to_text(pdf_bytes)

                    st.write(f"Extracting PHI-Canto data with {model}…")
                    extracted = ai_extract(text, model=model)
                    status.update(label="Done — review the extracted data below.",
                                  state="complete", expanded=False)

                st.session_state.update({
                    "proc_markdown":  text,
                    "proc_extracted": extracted,
                    "proc_filename":  uploaded.name,
                    "proc_model":     model,
                    "proc_pipeline":  pipeline,
                    "proc_stage":     "review",
                })
                st.rerun()
            except RuntimeError as e:
                st.error(str(e))

    # ── Review ──────────────────────────────────────────────────────────────
    elif stage == "review":
        data  = st.session_state.proc_extracted
        fname = st.session_state.get("proc_filename", "paper.pdf")

        n_genes = len(data.get("genes", []))
        n_alleles = len(data.get("alleles", []))
        n_pg  = len(data.get("pathogen_genotypes", []))
        n_mg  = len(data.get("metagenotypes", []))

        st.title("Review extraction")
        st.caption(
            f"{n_genes} gene{'s' if n_genes != 1 else ''} · "
            f"{n_alleles} allele{'s' if n_alleles != 1 else ''} · "
            f"{n_pg} pathogen genotype{'s' if n_pg != 1 else ''} · "
            f"{n_mg} metagenotype{'s' if n_mg != 1 else ''}"
        )

        tabs = st.tabs(["Article", "Organisms", "Genes", "Alleles",
                         "Genotypes", "Metagenotypes", "Notes"])
        with tabs[0]: _review_article(data)
        with tabs[1]: _review_organisms(data)
        with tabs[2]: _review_genes(data)
        with tabs[3]: _review_alleles(data)
        with tabs[4]: _review_genotypes(data)
        with tabs[5]: _review_metagenotypes(data)
        with tabs[6]:
            data["curation_notes"] = st.text_area(
                "Curation notes", value=data.get("curation_notes") or "", height=120,
            )

        st.markdown("&nbsp;")
        c_save, c_export, c_md, _, c_back = st.columns([2, 2, 2, 1, 1])

        if c_save.button("Save to database", type="primary", use_container_width=True):
            try:
                article_id = save_extraction(
                    data, fname,
                    st.session_state.get("proc_model", ""),
                    st.session_state.get("proc_pipeline", ""),
                )
                st.session_state.proc_saved_id = article_id
                st.session_state.proc_stage    = "done"
                st.rerun()
            except Exception as e:
                st.error(f"Save failed: {e}")

        c_export.download_button(
            "Export for PHI-Canto",
            to_json_str(data),
            file_name=Path(fname).stem + "_phi_canto.json",
            mime="application/json",
            use_container_width=True,
            help="Canto-compatible JSON — upload at /phi_weaver/import in your Canto instance.",
        )

        c_md.download_button(
            "Download markdown",
            st.session_state.get("proc_markdown", ""),
            file_name=Path(fname).stem + ".md",
            mime="text/markdown",
            use_container_width=True,
        )

        if c_back.button("← Back", use_container_width=True):
            proc_reset()
            st.rerun()

    # ── Done ────────────────────────────────────────────────────────────────
    elif stage == "done":
        st.title("Saved")
        st.success(
            f"Article saved (ID {st.session_state.get('proc_saved_id')}). "
            "Go to **Articles** to track its curation status, or export the JSON "
            "and upload it to PHI-Canto."
        )
        st.markdown("&nbsp;")
        if st.button("Process another paper", type="primary"):
            proc_reset()
            st.rerun()


def page_articles():
    st.title("Articles")

    # Status summary
    counts_df = q("SELECT status, COUNT(*) n FROM articles GROUP BY status")
    counts    = dict(zip(counts_df["status"], counts_df["n"]))
    total     = sum(counts.values())

    if total > 0:
        chips = "".join(
            f'<span class="art-chip badge" style="background:{_STATUS_COLOR[s][0]};color:{_STATUS_COLOR[s][1]}">'
            f'{counts.get(s, 0)} {s.replace("_", " ")}</span>'
            for s in STATUS_OPTS if counts.get(s, 0) > 0
        )
        st.markdown(
            f'<div class="art-summary"><span class="art-total">{total} articles</span>{chips}</div>',
            unsafe_allow_html=True,
        )

    # Add article form
    with st.expander("Add article manually"):
        with st.form("add_article", clear_on_submit=True):
            title = st.text_input("Title *")
            c1, c2, c3, c4 = st.columns(4)
            pmid    = c1.text_input("PMID")
            year    = c2.number_input("Year", 1990, 2030, value=date.today().year, step=1)
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

    # Filter
    status_filter = st.segmented_control(
        "Filter", ["All"] + [s.replace("_", " ").title() for s in STATUS_OPTS],
        default="All"
    )
    filter_val = None if status_filter == "All" else status_filter.lower().replace(" ", "_")

    sql    = "SELECT id, title, pmid, journal, pub_year as year, authors, status, priority FROM articles"
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
        (articles["status"] != edited["status"]) |
        (articles["priority"] != edited["priority"])
    ]
    if not changed.empty:
        for i, row in changed.iterrows():
            run("UPDATE articles SET status=?, priority=?, updated_date=CURRENT_TIMESTAMP WHERE id=?",
                (edited.at[i, "status"], edited.at[i, "priority"], row["id"]))
        st.toast(f"Saved {len(changed)} change(s).", icon="✅")
        st.rerun()


def page_proteins():
    st.title("Proteins")

    # Quick stats
    total_p  = int(q("SELECT COUNT(*) n FROM proteins").iloc[0]["n"])
    eff_p    = int(q("SELECT COUNT(*) n FROM proteins WHERE protein_type='effector'").iloc[0]["n"])
    species_n = int(q("SELECT COUNT(DISTINCT species_id) n FROM proteins").iloc[0]["n"])
    st.markdown(
        f'<div class="kpi-grid" style="grid-template-columns:repeat(3,1fr);max-width:500px">'
        f'{kpi(total_p, "Total proteins")}'
        f'{kpi(eff_p, "Effectors")}'
        f'{kpi(species_n, "Species")}'
        f'</div>',
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns([3, 2, 1])
    search         = c1.text_input("", placeholder="Search gene name, function, ID…", label_visibility="collapsed")
    species_opts   = q("SELECT DISTINCT name FROM species ORDER BY name")["name"].tolist()
    species_filter = c2.selectbox("", ["All species"] + species_opts, label_visibility="collapsed")
    type_filter    = c3.selectbox("", ["All"] + PROTEIN_TYPES, label_visibility="collapsed")

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
    st.caption(f"{len(proteins)} of {total_p} protein{'s' if total_p != 1 else ''}")


def page_sessions():
    st.title("Sessions")

    # Running totals first — give context before the form
    totals = q("""SELECT SUM(proteins_curated) p, SUM(interactions_added) i,
                         ROUND(SUM(session_duration_hours), 1) h,
                         COUNT(*) n
                  FROM curation_sessions""").iloc[0]

    st.markdown(
        f'<div class="stat-row">'
        f'<div class="stat-card"><div class="stat-val">{int(totals["p"] or 0)}</div>'
        f'<div class="stat-lbl">Proteins curated</div></div>'
        f'<div class="stat-card"><div class="stat-val">{int(totals["i"] or 0)}</div>'
        f'<div class="stat-lbl">Interactions added</div></div>'
        f'<div class="stat-card"><div class="stat-val">{totals["h"] or 0}</div>'
        f'<div class="stat-lbl">Hours logged</div></div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # Log form
    with st.form("log_session", clear_on_submit=True):
        st.markdown('<span class="section-title">Log today\'s session</span>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        proteins     = c1.number_input("Proteins curated",  min_value=0, value=0, step=1)
        interactions = c2.number_input("Interactions added", min_value=0, value=0, step=1)
        hours        = c3.number_input("Hours",             min_value=0.0, step=0.5, value=1.0)
        notes = st.text_area("Notes", placeholder="What did you work on today?")
        if st.form_submit_button("Log session", type="primary"):
            run("""INSERT INTO curation_sessions
                   (session_date, curator, proteins_curated, interactions_added,
                    session_duration_hours, notes)
                   VALUES (?, 'curator', ?, ?, ?, ?)""",
                (date.today(), proteins, interactions, hours, notes or None))
            st.success("Session logged.")
            st.rerun()

    # History
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('<span class="section-title">History</span>', unsafe_allow_html=True)
    sessions = q("""SELECT session_date as date, proteins_curated as proteins,
                           interactions_added as interactions,
                           ROUND(session_duration_hours, 1) as hours, notes
                    FROM curation_sessions ORDER BY created_date DESC""")
    if sessions.empty:
        st.caption("No sessions recorded yet.")
    else:
        st.dataframe(sessions, width="stretch", hide_index=True)


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    st.set_page_config(
        page_title="PHI-Weaver",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    st.markdown(CSS, unsafe_allow_html=True)

    # Brand header
    st.markdown(
        '<div class="app-header">'
        '<span class="app-name">PHI<em>-Weaver</em></span>'
        '<span class="app-divider">·</span>'
        '<span class="app-sub">PHI-base curation assistant</span>'
        '</div>',
        unsafe_allow_html=True,
    )

    tabs = st.tabs(["Dashboard", "Process Paper", "Articles", "Proteins", "Sessions"])
    with tabs[0]: page_dashboard()
    with tabs[1]: page_process()
    with tabs[2]: page_articles()
    with tabs[3]: page_proteins()
    with tabs[4]: page_sessions()


if __name__ == "__main__":
    main()
