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

    # --- A. Genes ---
    out += ["## A. Enter genes first", ""]
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

    out += ["## F. Annotation entry queue", "", "### F1. GO annotations", ""]
    go_rows = [["☐", _cell(a.get("feature")), _cell(_s(a.get("annotation_type")).replace("_", " ")),
                _term(a), _cell(a.get("evidence")), _cell(a.get("figure"))]
               for a in enter if _s(a.get("annotation_type")) in GO_ASPECTS]
    out += _table(["Tick", "Subject", "Annotation type", "Term", "Evidence summary", "Figure/table"], go_rows) + [""]

    out += ["### F2. Physical interaction annotations", ""]
    pi_rows = []
    for a in _of("physical_interaction"):
        interactor = _cell("; ".join(_s(e.get("value")) for e in (a.get("extensions") or [])
                                     if _s(e.get("relation")) == "interactor"))
        pi_rows.append(["☐", _cell(a.get("feature")), interactor or "—",
                        _term(a) if _s(a.get("term_id")) else "pick PSI-MI at entry",
                        _cell(a.get("evidence")), _cell(a.get("figure")), "enter"])
    out += _table(["Tick", "Subject", "Interactor", "Interaction term", "Evidence method", "Figure/table", "Status"], pi_rows) + [""]

    out += ["### F3. Pathogen phenotype annotations", ""]
    pp_rows = [["☐", _cell(a.get("feature")), _term(a), _cell(a.get("evidence")),
                _cell(a.get("conditions")), _cell(a.get("figure"))] for a in _of("pathogen_phenotype")]
    out += _table(["Tick", "Genotype", "PHIPO term", "Evidence summary", "Condition", "Figure/table"], pp_rows) + [""]

    out += ["### F4. Pathogen–host interaction phenotype annotations", ""]
    ip_rows = [["☐", _cell(a.get("feature")), _term(a), _compared_with(a) or "—",
                _cell(a.get("evidence")), _cell(a.get("figure"))]
               for a in _of("pathogen_host_interaction_phenotype", "gene_for_gene_phenotype")]
    out += _table(["Tick", "Metagenotype", "PHIPO term", "Compared with", "Evidence summary", "Figure/table"], ip_rows) + [""]

    out += ["### F5. Disease annotation", ""]
    dz_rows = [["☐", _cell(a.get("feature")), _cell(a.get("term_name")), _cell(a.get("term_id")),
                _cell(a.get("conditions") or a.get("figure"))] for a in _of("disease_name")]
    out += _table(["Tick", "Metagenotype", "Disease term", "Disease ontology ID", "Note"], dz_rows) + [""]

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
    ap.add_argument("--validate", action="store_true",
                    help="check ontology IDs online and park obsolete/not-found terms (needs network)")
    args = ap.parse_args(argv)
    if args.out and len(args.drafts) != 1:
        ap.error("--out is only valid with a single draft")

    from phiweaver.canto.coverage import coverage_for_draft
    for d in args.drafts:
        md, counts = queue_for_draft(d, validate=args.validate)
        if args.stdout:
            print(md)
        else:
            out = Path(args.out) if args.out else default_out(d)
            out.write_text(md, encoding="utf-8")
            print(f"wrote {out}  —  genes: {counts['genes_enter']} enter / {counts['genes_held']} held; "
                  f"annotations: {counts['annotations_enter']} enter; parked: {counts['parked']}")
        for w in coverage_for_draft(d):
            print(f"  ⚠ coverage [{Path(d).name}]: {w}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
