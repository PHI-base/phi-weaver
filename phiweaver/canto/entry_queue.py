#!/usr/bin/env python3
"""
phiweaver.canto.entry_queue — render a phiweaver draft into a PHI-Canto **entry queue**.

A concise, table-driven "click-list": the single Route-1 output. It strips a draft's `canto`
block to the minimum a biocurator needs while transcribing into canto.phi-base.org, and adds a
**safety filter**: anything that must not be entered yet (unresolved accession, missing ontology
term, interpretive molecular-function claim, or an item that depends on a held gene) is moved to a
*parked* section instead of an entry table.

Input: the draft's ```json ``canto`` block (genes / alleles / genotypes /
metagenotypes / annotations). Deterministic — same block in, same queue out; nothing is invented.
Spec: ``PHI-Canto-Literature/active/Worksheet prompt-2026-07-08.md`` (curator request).

Held-gene cascade (the core rule): a gene with no ``uniprot`` accession is **held**; its alleles,
any genotype using them, any metagenotype using those genotypes, and any annotation on a held
feature are all parked, never entered.

Annotations may also carry an explicit ``"hold": true`` (with ``"hold_reason"``) to park an item
by the curator's structured decision — the preferred signal for interpretive/uncertain claims —
and a ``"note"`` field for caveats kept out of the lean entry tables. When ``hold`` is absent the
renderer falls back to a heuristic that parks interpretive molecular-function claims.

Section and column labels follow PHI-Canto's own (D19), captured from a saved session page
(2026-07-25) rather than guessed: `Term name` and `Term ID` are separate columns, `Conditions` is
plural, the figure column is `Figure`.

**One column is deliberately NOT Canto's wording.** Canto's phenotype tables head that column
`Evidence code`, because the field takes a controlled code from `canto_config`'s `evidence_codes`.
A phiweaver draft carries a prose *summary* of the evidence ("growth assay", "disease index"), so
this queue says **`Evidence summary`** — labelling prose as a code would tell the curator the cell
is ready to paste into a controlled field when it is not. The exception is `Physical interaction`,
whose evidence genuinely is a code there (Co-purification / PCA / Two-hybrid), so that column *is*
`Evidence code`. Canto's `Comment` column and its genotype `Strain` / `Background` columns have no
counterpart here: `note` is deliberately kept out of the lean queue (D14), and the draft schema has
no strain/background fields — the genotype `name` currently carries the strain (e.g. `Guy11`).

Pure stdlib; emits markdown.

Usage (from the repo root):
    python3 -m phiweaver.canto.entry_queue /path/active/PMID..-phiweaver-DRAFT.md
    python3 -m phiweaver.canto.entry_queue drafts/*.md          # one queue each
    python3 -m phiweaver.canto.entry_queue draft.md --out queue.md
    python3 -m phiweaver.canto.entry_queue draft.md --stdout
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from phiweaver.figure_ledger import audit as audit_figures
from phiweaver.figure_ledger import summary_line as figure_summary_line
from phiweaver.source_routes import describe_source

from phiweaver.common import provenance_line
from phiweaver.canto.record import extract_record, _s, _fmt_extensions

_STATUS_RE = re.compile(r"^status:\s*(.+?)\s*$", re.MULTILINE)

GO_ASPECTS = {"molecular_function", "biological_process", "cellular_component"}
# an interpretive molecular-function claim self-declares that no direct assay was done
_INTERPRETIVE = ("interpret", "homology-infer", "not demonstrated", "not assayed",
                 "no direct", "no in-vitro", "no in vitro", "indirect", "inferred from")


def _cell(v) -> str:
    """Table-cell-safe text: escape pipes and collapse newlines (never corrupt the table)."""
    return " ".join(_s(v).replace("|", "\\|").split())


def _term(a: dict) -> str:
    tid, tname = _s(a.get("term_id")), _s(a.get("term_name"))
    if tid:
        return _cell(f"{tname} — {tid}" if tname else tid)
    return _cell(f"⚠ {tname or '(unresolved)'}")


def _term_name(a: dict) -> str:
    """The term's name for PHI-Canto's `Term name` column; ⚠ when nothing resolved."""
    tname = _s(a.get("term_name"))
    return _cell(tname) if _s(a.get("term_id")) or tname else "⚠ (unresolved)"


def _term_id(a: dict) -> str:
    """The term's ID for PHI-Canto's `Term ID` column."""
    return _cell(a.get("term_id")) or "—"


def _heading(display_name: str) -> str:
    """PHI-Canto's `display_name` as the UI actually renders it — first letter capitalised.

    The config stores most names lower-case (`pathogen phenotype`) but the session page shows
    `Pathogen phenotype`. Capitalising here rather than in ANNOTATION_SECTIONS keeps that table a
    verbatim copy of the config, so the drift test stays a plain equality check.
    """
    return display_name[:1].upper() + display_name[1:]


def _compared_with(a: dict) -> str:
    vals = [_s(e.get("value")) for e in (a.get("extensions") or [])
            if _s(e.get("relation")) == "compared_to_control"]
    return _cell("; ".join(v for v in vals if v))


def _truthy(v) -> bool:
    return v is True or _s(v).lower() in ("true", "yes", "1")


def _is_interpretive_mf(a: dict) -> bool:
    """Fallback heuristic (used only when an annotation lacks an explicit `hold` flag): a
    molecular-function claim whose evidence self-declares that no direct assay was done."""
    if _s(a.get("annotation_type")) != "molecular_function":
        return False
    ev = _s(a.get("evidence")).lower()
    return any(k in ev for k in _INTERPRETIVE)


def _classify(canto: dict):
    """Held-gene cascade + referential-integrity check + pathogen/host genotype split.

    Returns ``exclude``: a {(kind, name): reason} map of alleles/genotypes/metagenotypes that must
    not be entered — either because they are **held** (descend from an accession-less gene) or
    because they carry a **dangling reference** (point at an undefined gene/allele/genotype). Both
    are surfaced as parked items; entering nothing that fails a QC check is the whole point.
    """
    genes = canto.get("genes") or []
    alleles = canto.get("alleles") or []
    genotypes = canto.get("genotypes") or []
    metas = canto.get("metagenotypes") or []

    gene_names = {_s(g.get("name")) for g in genes}
    allele_names = {_s(a.get("name")) for a in alleles}
    genotype_names = {_s(g.get("name")) for g in genotypes}
    meta_names = {_s(m.get("name")) for m in metas}
    held_genes = {_s(g.get("name")) for g in genes if not _s(g.get("uniprot"))}

    exclude: Dict[Tuple[str, str], str] = {}
    for a in alleles:
        nm, gene = _s(a.get("name")), _s(a.get("gene"))
        if gene not in gene_names:
            exclude[("allele", nm)] = f"references undefined gene '{gene}'"
        elif gene in held_genes:
            exclude[("allele", nm)] = "gene is held (unresolved accession)"
    for g in genotypes:
        nm = _s(g.get("name"))
        gal = [_s(x) for x in (g.get("alleles") or []) if _s(x)]
        undef = [al for al in gal if al not in allele_names]
        held = [al for al in gal if ("allele", al) in exclude]
        if undef:
            exclude[("genotype", nm)] = f"references undefined allele(s): {', '.join(undef)}"
        elif held:
            exclude[("genotype", nm)] = "uses a held allele"
    for m in metas:
        nm = _s(m.get("name"))
        refs = [_s(m.get("pathogen_genotype")), _s(m.get("host_genotype"))]
        undef = [x for x in refs if x not in genotype_names]
        held = [x for x in refs if ("genotype", x) in exclude]
        if undef:
            exclude[("metagenotype", nm)] = f"references undefined genotype(s): {', '.join(undef)}"
        elif held:
            exclude[("metagenotype", nm)] = "depends on a held genotype"

    # pathogen vs host genotype: by how each is referenced in metagenotypes (robust, no guessing)
    host_names, path_names = set(), set()
    for m in metas:
        host_names.add(_s(m.get("host_genotype")))
        path_names.add(_s(m.get("pathogen_genotype")))
    return dict(gene_names=gene_names, allele_names=allele_names,
                genotype_names=genotype_names, meta_names=meta_names,
                held_genes=held_genes, exclude=exclude,
                host_names=host_names, path_names=path_names)


# Annotation types whose "term" is a controlled qualifier phrase rather than an ontology ID.
# The RNA/protein-level types draw on the seven PomGeneEx phrases (RNA level increased /
# decreased / unchanged / constant / fluctuates, RNA present, RNA absent) and a draft is
# explicitly not required to carry their numeric IDs — see
# 06-Training/Gene-for-Gene-Curation-Methodology.md §9. Without this, a solid expression
# annotation is parked as "no ontology term resolved", which reads as a defect it does not have.
_QUALIFIER_PHRASE_TYPES = {"wt_rna_expression", "wt_protein_expression"}


# PHI-Canto's twelve annotation types, in the order its own config lists them, labelled with the
# `display_name` the web interface shows — so the queue's headings read like the screen the curator
# is typing into. `shape` picks the column set below.
#
# Hardcoded rather than read from `canto_config` at render time, deliberately: the deploy config is
# gitignored (it comes from the private PHI-base/config repo), so config-driven headings would
# differ between a machine that has the file and a fresh clone that falls back to pombase's base —
# handing two curators differently-shaped queues for the same paper. Same reasoning that keeps
# `map_phenotype`'s subset filter on the committed ontology rather than the deploy file.
# `tests/test_entry_queue.py` checks this list against the live config whenever the deploy file
# *is* present, so an upstream rename or a new type fails a test instead of drifting silently.
ANNOTATION_SECTIONS = (
    ("molecular_function",                  "GO molecular function",               "go"),
    ("biological_process",                  "GO biological process",               "go"),
    ("cellular_component",                  "GO cellular component",               "go"),
    ("host_phenotype",                      "host phenotype",                      "host_phenotype"),
    ("pathogen_phenotype",                  "pathogen phenotype",                  "phenotype"),
    ("pathogen_host_interaction_phenotype", "pathogen-host interaction phenotype", "interaction"),
    ("gene_for_gene_phenotype",             "gene-for-gene phenotype",             "interaction"),
    ("post_translational_modification",     "protein modification",                "modification"),
    ("physical_interaction",                "physical interaction",                "physical"),
    ("wt_rna_expression",                   "Wild-type RNA level",                 "level"),
    ("wt_protein_expression",               "Wild-type protein level",             "level"),
    ("disease_name",                        "disease name",                        "disease"),
)

# Column headers per shape. Splitting GO into its three aspects and RNA/protein into two lets the
# old "Annotation type" column go — the heading now carries what the column used to.
# Column labels follow the session page's own tables (captured from a saved PHI-Canto session,
# 2026-07-25): `Term name` and `Term ID` are two columns there, not one cell; `Conditions` is
# plural; the figure column is just `Figure`. `Evidence summary` is deliberately NOT renamed to
# Canto's `Evidence code` — see the note in the module docstring.
_ANNOTATION_HEADERS = {
    "go":             ["Tick", "Gene", "Term name", "Term ID", "Evidence summary", "Figure"],
    "host_phenotype": ["Tick", "Host genotype", "Term name", "Term ID", "Evidence summary",
                       "Conditions", "Figure"],
    "phenotype":      ["Tick", "Genotype", "Term name", "Term ID", "Evidence summary",
                       "Conditions", "Figure"],
    "interaction":    ["Tick", "Metagenotype", "Term name", "Term ID", "Compared with",
                       "Evidence summary", "Figure"],
    "modification":   ["Tick", "Gene", "Term name", "Term ID", "Evidence summary", "Conditions",
                       "Figure"],
    "physical":       ["Tick", "Interactor A", "Interactor B", "Term name", "Evidence code",
                       "Figure", "Status"],
    "level":          ["Tick", "Gene", "Level qualifier", "Evidence summary", "Conditions",
                       "Figure"],
    "disease":        ["Tick", "Metagenotype", "Term name", "Term ID", "Comment"],
}


def _interactor(a: dict) -> str:
    """The `interactor` extension value(s) of a physical-interaction annotation."""
    return _cell("; ".join(_s(e.get("value")) for e in (a.get("extensions") or [])
                           if _s(e.get("relation")) == "interactor"))


# One row builder per shape. Signatures match so the renderer can dispatch on `shape` alone.
_ANNOTATION_ROWS = {
    "go": lambda a: ["☐", _cell(a.get("feature")), _term_name(a), _term_id(a),
                     _cell(a.get("evidence")), _cell(a.get("figure"))],
    "host_phenotype": lambda a: ["☐", _cell(a.get("feature")), _term_name(a), _term_id(a),
                                 _cell(a.get("evidence")), _cell(a.get("conditions")),
                                 _cell(a.get("figure"))],
    "phenotype": lambda a: ["☐", _cell(a.get("feature")), _term_name(a), _term_id(a),
                            _cell(a.get("evidence")), _cell(a.get("conditions")),
                            _cell(a.get("figure"))],
    "interaction": lambda a: ["☐", _cell(a.get("feature")), _term_name(a), _term_id(a),
                              _compared_with(a) or "—", _cell(a.get("evidence")),
                              _cell(a.get("figure"))],
    # No "pick the term at entry" fallback here, unlike physical interaction: PI is exempt from
    # the term requirement because it genuinely has no ontology term (the evidence method carries
    # it), whereas a protein-modification annotation *does* take a PSI-MOD term, so a term-less
    # one is correctly parked by _park_reason and never reaches this row builder.
    "modification": lambda a: ["☐", _cell(a.get("feature")), _term_name(a), _term_id(a),
                               _cell(a.get("evidence")), _cell(a.get("conditions")),
                               _cell(a.get("figure"))],
    # Canto's physical-interaction table is Interactor A / Interactor B, and its evidence field
    # really is a controlled code here (Co-purification / PCA / Two-hybrid), so the label is exact.
    "physical": lambda a: ["☐", _cell(a.get("feature")), _interactor(a) or "—",
                           _term_name(a) if _s(a.get("term_id")) else "pick PSI-MI at entry",
                           _cell(a.get("evidence")), _cell(a.get("figure")), "enter"],
    "level": lambda a: ["☐", _cell(a.get("feature")), _cell(a.get("term_name")),
                        _cell(a.get("evidence")), _cell(a.get("conditions")),
                        _cell(a.get("figure"))],
    "disease": lambda a: ["☐", _cell(a.get("feature")), _term_name(a), _term_id(a),
                          _cell(a.get("conditions") or a.get("figure"))],
}


def _strains_section(canto: dict, cl: dict) -> List[str]:
    """Table A2 — one row per organism, prompting Canto's required *Adding strains* step.

    PHI-Canto requires "one or more 'experimental strains' for every organism" in the session
    *before* genotypes can be created, and its notion of strain is broad: subspecies, varieties,
    pathovars, **cultivars** and strains proper.

    **Only wild-type genotypes contribute a strain** (curator ruling, 2026-07-25 — see
    `07-Standards/PHI-Canto-Curation-Conventions.md`, "Strains and cultivars"). A mutant is named by
    its allele, not by the isolate label the paper gives it: on PMID:9927411 `Guy11` is the strain,
    while `AM25` and `TF7-3131` are the `abc1Δ` and `abc1-1` **genotypes** and carry no strain. So
    allele-bearing genotypes are excluded from this table entirely rather than offered as strains.

    A genotype's optional `strain` field is used verbatim when present. When it is absent the cell
    stays unset and the wild-type genotype names are shown beside it, because splitting a strain out
    of a name like `WT Oryza sativa Sariceltic` would be guessing at curated data.
    """
    organisms: Dict[str, dict] = {}

    def _entry(org: str, role: str = "") -> dict:
        e = organisms.setdefault(org, {"role": role, "strains": [], "wild_type": []})
        if role and not e["role"]:
            e["role"] = role
        return e

    for g in canto.get("genes") or []:
        if _s(g.get("organism")):
            _entry(_s(g.get("organism")), "pathogen")
    for g in canto.get("genotypes") or []:
        org, name = _s(g.get("organism")), _s(g.get("name"))
        if not org:
            continue
        # Role from how the genotype is used in metagenotypes, never from the species name.
        role = ("host" if name in cl["host_names"]
                else "pathogen" if name in cl["path_names"] else "")
        e = _entry(org, role)
        # A genotype carrying alleles is a mutant: per the ruling it contributes no strain.
        if [x for x in (g.get("alleles") or []) if _s(x)]:
            continue
        strain = _s(g.get("strain"))
        if strain and strain not in e["strains"]:
            e["strains"].append(strain)
        elif not strain and name:
            e["wild_type"].append(name)
    if not organisms:
        return []
    rows = [["☐", _cell(org), _cell(d["role"] or "—"),
             _cell("; ".join(d["strains"])) if d["strains"] else "— set in Canto",
             _cell("; ".join(d["wild_type"]) or ("(from the strain field)" if d["strains"] else "—"))]
            for org, d in organisms.items()]
    return (["### A2. Strains — one or more per organism, before any genotype", "",
             "*Canto's \"strain\" covers subspecies, varieties, pathovars, cultivars and strains "
             "proper. Use the strain picker under each organism, **Add strain** for one not in the "
             "list, or **Unknown strain** if the paper does not say. **Wild types only** — a mutant "
             "is named by its allele and carries no strain, so mutant genotypes are not listed "
             "here. Where the strain cell is unset the draft carries no `strain` field; the "
             "allele-free genotype names are shown to recognise it from, not as the strain itself "
             "— and a control that merely has no alleles listed (an ectopic-integration "
             "transformant, say) appears among them, so confirm which is the true wild type.*",
             ""]
            + _table(["Tick", "Organism", "Role", "Strain / cultivar",
                      "Wild-type genotype in the draft"], rows)
            + [""])


def _park_reason(a: dict, cl: dict, bad_terms: Optional[Dict[str, str]] = None) -> str:
    """Why an annotation is parked, or '' if it is enter-ready."""
    ft, fx = _s(a.get("feature_type")), _s(a.get("feature"))
    names = {"gene": cl["gene_names"], "genotype": cl["genotype_names"],
             "metagenotype": cl["meta_names"]}.get(ft)
    if names is not None and fx not in names:
        return f"annotation subject '{fx}' is not defined in the setup sections"
    if ft == "gene" and fx in cl["held_genes"]:
        return "depends on a held gene (unresolved accession)"
    if (ft, fx) in cl["exclude"]:
        return cl["exclude"][(ft, fx)]
    if _truthy(a.get("hold")):  # explicit park signal — the curator's structured decision
        return _s(a.get("hold_reason")) or "held by curator (hold flag)"
    tid, atype = _s(a.get("term_id")), _s(a.get("annotation_type"))
    if not tid:
        if atype == "physical_interaction":
            return ""  # PI has no ontology term by design; evidence method carries it
        if atype in _QUALIFIER_PHRASE_TYPES and _s(a.get("term_name")):
            return ""  # the controlled qualifier phrase IS the term; numeric ID not required
        return "no ontology term resolved"
    if bad_terms and tid in bad_terms:
        return f"ontology ID {bad_terms[tid]} (--validate)"
    if _is_interpretive_mf(a):  # fallback for drafts without an explicit hold flag
        return "interpretive molecular-function (no direct assay)"
    return ""


def _validate_terms(canto: dict) -> Dict[str, str]:
    """Opt-in ontology check: return {term_id: bad-status} for obsolete/not-found/invalid IDs.

    Online for GO/PHIPO, offline for PHIDO. Network errors are treated as pass (not parked), so a
    connectivity blip never hides an otherwise-enterable annotation.
    """
    from phiweaver.lookup.validate_ontology_ids import OntologyValidator
    validator = OntologyValidator()
    bad: Dict[str, str] = {}
    seen = set()
    for a in canto.get("annotations") or []:
        tid = _s(a.get("term_id"))
        if not tid or tid in seen:
            continue
        seen.add(tid)
        try:
            res = validator.validate(tid, online=True)
        except Exception:
            continue
        if res.existence in ("obsolete", "not_found", "format_invalid", "unknown_prefix"):
            bad[tid] = res.existence
    return bad


def _table(header: List[str], rows: List[List[str]]) -> List[str]:
    out = ["| " + " | ".join(header) + " |",
           "| " + " | ".join("---" for _ in header) + " |"]
    for r in rows:
        out.append("| " + " | ".join(r) + " |")
    if not rows:
        out.append("| " + " | ".join("_(none)_" if i == 0 else "" for i in range(len(header))) + " |")
    return out


def render_entry_queue(rec: dict, status: Optional[str] = None,
                       validate: bool = False) -> Tuple[str, Dict[str, int]]:
    """Render the entry queue; also return summary counts for the CLI validation report.

    ``status`` is the draft's frontmatter status (defaults to draft-not-validated). When
    ``validate`` is set, ontology IDs are checked online and obsolete/not-found terms are parked.
    """
    meta = rec.get("meta") or {}
    canto = rec.get("canto") or {}
    cl = _classify(canto)
    bad_terms = _validate_terms(canto) if validate else {}
    pmid = _s(meta.get("pmid"))
    parked: List[Tuple[str, str, str]] = []  # (item, why, action)

    out: List[str] = []
    out.append(f"# PHI-Canto entry queue — PMID:{pmid}" if pmid else "# PHI-Canto entry queue")
    for line in (_s(meta.get("paper")),):
        if line:
            out.append(line)
    status_txt = _s(status) or _s(meta.get("status")) or "draft (not validated)"
    hdr = " · ".join(x for x in [
        f"System: {_s(meta.get('system'))}" if _s(meta.get("system")) else "",
        f"Status: {status_txt}",
        f"Model/tool: {_s(meta.get('model')) or 'phiweaver'}",
        f"Date: {_s(meta.get('date'))}" if _s(meta.get("date")) else "",
    ] if x)
    out += ["", hdr, ""]

    # Provenance of the source artefact, before any table — a curator working the queue
    # needs to know whether the draft's figure claims were read or inferred.
    source_line = describe_source(meta)
    if source_line:
        out += [source_line, ""]

    # Figure-inspection coverage, derived from the draft's ledger rather than from its
    # `figures_inspected` boolean, which is an assertion nothing verifies.
    figure_audit = audit_figures(rec)
    figure_line = figure_summary_line(figure_audit)
    if figure_line:
        out += [figure_line, ""]

    # --- A. Genes and strains ---
    # Both are one step in Canto: the strain picker sits below each pathogen and host on the
    # gene-entry page (docs/getting_started, anchors #adding_genes_and_organisms and
    # #adding_strains are the same page), so A carries two tables rather than earning a letter each.
    out += ["## A. Enter genes and strains", "", "### A1. Genes", ""]
    grows = []
    for g in canto.get("genes") or []:
        name, org, acc = _s(g.get("name")), _s(g.get("organism")), _s(g.get("uniprot"))
        if acc:
            grows.append(["☐", _cell(name), _cell(org), _cell(f"UniProtKB:{acc}"), "enter"])
        else:
            grows.append(["☐", _cell(name), _cell(org), "unresolved", "hold"])
            parked.append((f"gene {name}", "unresolved UniProtKB accession",
                           _cell(_s(g.get("note")) or "resolve accession before add-gene")))
    out += _table(["Tick", "Gene name", "Species", "Add-gene identifier", "Status"], grows) + [""]
    out += _strains_section(canto, cl)

    # --- B. Alleles ---
    out += ["## B. Create alleles", ""]
    arows = []
    for a in canto.get("alleles") or []:
        name = _s(a.get("name"))
        if ("allele", name) in cl["exclude"]:
            reason = cl["exclude"][("allele", name)]
            parked.append((f"allele {name}", _cell(reason),
                           "fix the canto block" if "undefined" in reason else "enter after gene resolved"))
            continue
        arows.append(["☐", _cell(name), _cell(_s(a.get("gene"))), _cell(_s(a.get("type")) or "?"),
                      _cell(_s(a.get("expression")) or "?")])
    out += _table(["Tick", "Allele name", "Gene", "Allele type", "Expression"], arows) + [""]

    # --- C. Pathogen genotypes / D. Host genotypes ---
    path_rows, host_rows = [], []
    for g in canto.get("genotypes") or []:
        name = _s(g.get("name"))
        al = ", ".join(_s(x) for x in (g.get("alleles") or []) if _s(x)) or "wild type"
        use = _cell(_s(g.get("role")) or "experimental")
        if ("genotype", name) in cl["exclude"]:
            reason = cl["exclude"][("genotype", name)]
            parked.append((f"genotype {name}", _cell(reason),
                           "fix the canto block" if "undefined" in reason else "enter after gene resolved"))
            continue
        if name in cl["host_names"] and name not in cl["path_names"]:
            host_rows.append(["☐", _cell(name), _cell(_s(g.get("organism"))), _cell(al), use])
        else:
            path_rows.append(["☐", _cell(name), _cell(al), use])
    out += ["## C. Create pathogen genotypes", ""]
    out += _table(["Tick", "Genotype name", "Alleles", "Use"], path_rows) + [""]
    out += ["## D. Create host genotype", ""]
    out += _table(["Tick", "Host genotype", "Species", "Alleles / cultivar", "Use"], host_rows) + [""]

    # --- E. Metagenotypes ---
    out += ["## E. Create metagenotypes", ""]
    mrows = []
    for m in canto.get("metagenotypes") or []:
        name = _s(m.get("name"))
        if ("metagenotype", name) in cl["exclude"]:
            reason = cl["exclude"][("metagenotype", name)]
            parked.append((f"metagenotype {name}", _cell(reason),
                           "fix the canto block" if "undefined" in reason else "enter after gene resolved"))
            continue
        mrows.append(["☐", _cell(name), _cell(_s(m.get("pathogen_genotype"))),
                      _cell(_s(m.get("host_genotype"))), _cell(_s(m.get("role")) or "experimental")])
    out += _table(["Tick", "Metagenotype", "Pathogen genotype", "Host genotype", "Use"], mrows) + [""]

    # --- F. Annotation entry queue (split by type; parked ones filtered out) ---
    anns = canto.get("annotations") or []
    enter = []
    for a in anns:
        why = _park_reason(a, cl, bad_terms)
        if why:
            label = f"{_s(a.get('annotation_type')).replace('_',' ')} on {_s(a.get('feature'))}: {_term(a)}"
            parked.append((_cell(label), _cell(why),
                           _cell("pick term at entry" if "no ontology" in why
                                 else "curator decision")))
        else:
            enter.append(a)

    def _of(*types):
        return [a for a in enter if _s(a.get("annotation_type")) in types]

    # --- F. Annotation entry queue: one section per PHI-Canto annotation type ---
    # Sections follow ANNOTATION_SECTIONS (PHI-Canto's own order and display names) and are
    # numbered over the sections actually rendered, so a curator reads F1, F2, F3… with no gaps.
    out += ["## F. Annotation entry queue", ""]
    rendered_types: set = set()
    n = 0
    for atype, display, shape in ANNOTATION_SECTIONS:
        rows = [_ANNOTATION_ROWS[shape](a) for a in _of(atype)]
        if not rows:
            continue          # empty sections are omitted; the UI's full menu is not a checklist
        rendered_types.add(atype)
        n += 1
        out += [f"### F{n}. {_heading(display)}", ""]
        if shape == "level":
            out += ["*The level qualifier is a controlled phrase, not an ontology ID — pick the "
                    "matching term in Canto.*", ""]
        out += _table(_ANNOTATION_HEADERS[shape], rows) + [""]

    # Backstop: an enter-ready annotation whose type has no section above would otherwise pass
    # _park_reason, match nothing, and vanish — enter-ready and invisible is the one outcome
    # worse than parked. `host_phenotype` and `post_translational_modification` did exactly that
    # until 2026-07-25. Rather than only adding those two, anything unrecognised is now parked
    # with a reason, so a 13th PHI-Canto type fails loudly instead of silently.
    for a in enter:
        atype = _s(a.get("annotation_type"))
        if atype in rendered_types:
            continue
        parked.append((_cell(f"{atype.replace('_', ' ')} on {_s(a.get('feature'))}: {_term(a)}"),
                       _cell(f"no entry-queue section for annotation type '{atype}'"),
                       "enter by hand in Canto; then report this gap"))

    # --- Figure-evidence advisories ---
    # Deliberately NOT the parked table: parked means "do not enter", and an annotation
    # resting on a caption may still be correct. Only annotations the drafter marked
    # `needs_figure` appear here — under decline-by-default, curating from text and
    # captions is the normal path, so routine declines must not fill this section.
    uninspected = figure_audit.get("annotations_on_uninspected", [])
    if uninspected:
        out += [f"### F{n + 1}. Figure evidence — marked needs_figure, but not inspected", "",
                "*These annotations were judged to need their panel read — the claim is "
                "qualitative, magnitude decides it, or it is the paper's take-home "
                "message — and the figure was not inspected. Enterable, but weaker than "
                "intended.*", ""]
        out += _table(
            ["Annotation", "Cites", "Why it needs the figure", "Status"],
            [[_cell(f"{i['term_name'] or i['term_id']} on {i['feature']}"),
              _cell(i["figure"]), _cell(i.get("why_needed") or "—"),
              _cell(i["reason"])] for i in uninspected]) + [""]

    # --- G. Parked items ---
    out += ["## G. Parked items — do not enter yet", ""]
    prows = [[item, why, action] for (item, why, action) in parked]
    out += _table(["Item", "Why parked", "Action needed"], prows) + [""]

    # --- summary / blockers ---
    counts = dict(
        genes_enter=sum(1 for g in canto.get("genes") or [] if _s(g.get("uniprot"))),
        genes_held=len(cl["held_genes"]),
        annotations_enter=len(enter),
        parked=len(parked),
    )
    blockers = sorted(cl["held_genes"])
    out += ["## Queue summary", "",
            f"- Enter-ready genes: **{counts['genes_enter']}**  ·  held genes: **{counts['genes_held']}**",
            f"- Enter-ready annotations: **{counts['annotations_enter']}**  ·  parked items: **{counts['parked']}**",
            ("- Unresolved blockers (held genes): " + (", ".join(blockers) if blockers else "none")),
            "", "> Park = safety filter: resolve each parked item before entering it. "
            "Nothing here invents an accession, term, or evidence code.", ""]

    # Provenance footer — pins the framework commit + model + date behind this output.
    out += ["---", "",
            f"_{provenance_line(_s(meta.get('model')) or None, _s(meta.get('date')) or None)}_"]

    return "\n".join(out).rstrip() + "\n", counts


def default_out(draft_path) -> Path:
    p = Path(draft_path)
    stem = p.stem.replace("-phiweaver-DRAFT", "").replace("-DRAFT", "")
    return p.with_name(f"{stem}-phi-canto-entry-queue.md")


def _frontmatter_status(text: str) -> Optional[str]:
    """Return the YAML frontmatter ``status:`` value from a draft, or None."""
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    block = text[:end] if end != -1 else text
    m = _STATUS_RE.search(block)
    return m.group(1).strip() if m else None


def queue_for_draft(draft_path, validate: bool = False) -> Tuple[str, Dict[str, int]]:
    text = Path(draft_path).read_text(encoding="utf-8")
    rec = extract_record(text)
    if rec is None:
        raise SystemExit(f"no ```json block found in {draft_path}")
    if not rec.get("canto"):
        raise SystemExit(
            f"{draft_path} has no `canto` block — populate it first "
            "(see docs/CANTO-ROUTE1-BUILD-SPEC.md)")
    return render_entry_queue(rec, status=_frontmatter_status(text), validate=validate)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="Render phiweaver draft(s) into PHI-Canto entry queue(s).")
    ap.add_argument("drafts", nargs="+", help="draft .md file(s) with a ```json `canto` block")
    ap.add_argument("--out", help="output path (single draft only)")
    ap.add_argument("--stdout", action="store_true", help="print to stdout instead of writing files")
    ap.add_argument("--no-docx", action="store_true",
                    help="do not write the Word .docx (produce only the .md)")
    ap.add_argument("--no-md", action="store_true",
                    help="do not write the .md (produce only the .docx)")
    ap.add_argument("--validate", action="store_true",
                    help="check ontology IDs online and park obsolete/not-found terms (needs network)")
    args = ap.parse_args(argv)
    if args.out and len(args.drafts) != 1:
        ap.error("--out is only valid with a single draft")
    if args.no_md and args.no_docx:
        ap.error("--no-md and --no-docx together would write nothing")

    from phiweaver.canto.coverage import coverage_for_draft
    for d in args.drafts:
        md, counts = queue_for_draft(d, validate=args.validate)
        if args.stdout:
            print(md)
        else:
            out = Path(args.out) if args.out else default_out(d)
            written = []
            if not args.no_md:
                out.write_text(md, encoding="utf-8")
                written.append(str(out))
            if not args.no_docx:
                from phiweaver.export.docx import write_docx
                written.append(str(write_docx(md, out.with_suffix(".docx"))))
            print(f"wrote {', '.join(written)}  —  genes: {counts['genes_enter']} enter / "
                  f"{counts['genes_held']} held; annotations: {counts['annotations_enter']} enter; "
                  f"parked: {counts['parked']}")
        for w in coverage_for_draft(d):
            print(f"  ⚠ coverage [{Path(d).name}]: {w}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
