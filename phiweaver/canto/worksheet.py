#!/usr/bin/env python3
"""
phiweaver.canto.worksheet — render a phiweaver draft into a PHI-Canto entry worksheet.

Route 1 of the PHI-Canto submission plan (docs/CANTO-ROUTE1-BUILD-SPEC.md). A draft's
machine-readable ```json block carries a structured `canto` object (genes / alleles / genotypes /
metagenotypes / annotations; see the curation-example template). This renders it into an ordered
**Markdown checklist** that mirrors Canto's entry sequence, so a biocurator opens
canto.phi-base.org and the worksheet side by side and enters each item top to bottom.

The ordering is deliberate — Canto enforces the dependencies (no genotype before its allele, no
metagenotype before both genotypes). Entering the worksheet into PHI-Canto **is** the validation
step: the curator applies judgement and Canto's controlled vocabularies at the point of entry, so
nothing reaches the biocurator queue unreviewed. Terms are never invented — a `canto` annotation
with no `term_id`, and every `flags` entry, is surfaced as a ⚠ to resolve before submission.

Pure stdlib; emits markdown.

Usage (from the repo root):
    python3 -m phiweaver.canto.worksheet /path/active/PMID..-phiweaver-DRAFT.md
    python3 -m phiweaver.canto.worksheet drafts/*.md            # one worksheet each
    python3 -m phiweaver.canto.worksheet draft.md --out sheet.md
    python3 -m phiweaver.canto.worksheet draft.md --stdout
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import List

_JSON_BLOCK = re.compile(r"```json\s*(.*?)```", re.DOTALL)


def extract_record(md_text: str):
    """Parse the first ```json ... ``` block in a draft, or return None."""
    m = _JSON_BLOCK.search(md_text)
    if not m:
        return None
    return json.loads(m.group(1))


def _s(v) -> str:
    return str(v or "").strip()


def _readable(annotation_type: str) -> str:
    t = _s(annotation_type).replace("_", " ")
    return t[:1].upper() + t[1:] if t else "(annotation)"


def _fmt_extensions(exts) -> str:
    parts = []
    for e in exts or []:
        rel, val = _s(e.get("relation")), _s(e.get("value"))
        if rel and val:
            parts.append(f"{rel}={val}")
        elif rel or val:
            parts.append(rel or val)
    return " · ".join(parts)


def _annotation_line(a: dict) -> str:
    term_id, term_name = _s(a.get("term_id")), _s(a.get("term_name"))
    if term_id:
        head = f"{term_name} — {term_id}" if term_name else term_id
    else:
        head = f"⚠ {term_name or '(term)'} — NO TERM, resolve before entry"
    tail = []
    if _s(a.get("evidence")):
        tail.append(f"ev: {_s(a.get('evidence'))}")
    ext = _fmt_extensions(a.get("extensions"))
    if ext:
        tail.append(f"ext: {ext}")
    if _s(a.get("conditions")):
        tail.append(_s(a.get("conditions")))
    if _s(a.get("note")):
        tail.append(f"note: {_s(a.get('note'))}")
    if _s(a.get("figure")):
        tail.append(_s(a.get("figure")))
    return f"- [ ] {head}" + ((" — " + " — ".join(tail)) if tail else "")


def _group_annotations(annotations):
    """Group by (feature_type, feature, annotation_type), preserving first-seen order."""
    order, groups = {}, []
    for a in annotations or []:
        key = (_s(a.get("feature_type")), _s(a.get("feature")), _s(a.get("annotation_type")))
        if key not in order:
            order[key] = len(groups)
            groups.append((key, []))
        groups[order[key]][1].append(a)
    return groups


def render_worksheet(rec: dict) -> str:
    """Render a full draft record (meta + flags + canto block) into a Markdown worksheet."""
    meta = rec.get("meta") or {}
    canto = rec.get("canto") or {}
    flags = [f for f in (rec.get("flags") or []) if isinstance(f, dict)]
    pmid = _s(meta.get("pmid"))

    out: List[str] = []
    title = f"PHI-Canto entry worksheet — PMID:{pmid}" if pmid else "PHI-Canto entry worksheet"
    out.append(f"# {title}")
    if _s(meta.get("paper")):
        out.append(_s(meta.get("paper")))
    prov = " · ".join(
        ([f"System: {_s(meta.get('system'))}"] if _s(meta.get("system")) else [])
        + ([f"Model: {_s(meta.get('model'))}"] if _s(meta.get("model")) else [])
        + ([f"Draft date: {_s(meta.get('date'))}"] if _s(meta.get("date")) else []))
    if prov:
        out.append("")
        out.append(prov)
    out.append("")
    out.append("> Enter each item into canto.phi-base.org top to bottom, ticking as you go — "
               "entering it into Canto is the validation step. UniProtKB accession = the add-gene "
               "identifier.")
    if flags:
        out.append(f">")
        out.append(f"> ⚠ **{len(flags)} flag(s) to resolve before/while entering** — see the end.")
    out.append("")

    # 1. Genes
    out += ["## 1. Genes  (Curation ▸ add gene)", ""]
    genes = canto.get("genes") or []
    if genes:
        for g in genes:
            locus = f" (locus {_s(g.get('locus'))})" if _s(g.get("locus")) else ""
            acc = _s(g.get("uniprot"))
            acc_str = f"UniProtKB:{acc}" if acc else "⚠ no accession — resolve"
            out.append(f"- [ ] {_s(g.get('name'))} — {_s(g.get('organism'))} — {acc_str}{locus}")
            if _s(g.get("note")):
                out.append(f"      note: {_s(g.get('note'))}")
    else:
        out.append("_(none)_")
    out.append("")

    # 2. Alleles
    out += ["## 2. Alleles", ""]
    alleles = canto.get("alleles") or []
    if alleles:
        for a in alleles:
            out.append(f"- [ ] {_s(a.get('name'))} — gene {_s(a.get('gene'))} — "
                       f"{_s(a.get('type')) or '?'} — expression {_s(a.get('expression')) or '?'}")
    else:
        out.append("_(none)_")
    out.append("")

    # 3. Genotypes
    out += ["## 3. Genotypes", ""]
    genotypes = canto.get("genotypes") or []
    if genotypes:
        for g in genotypes:
            al = ", ".join(_s(x) for x in (g.get("alleles") or []) if _s(x)) or "wild type"
            role = f" — {_s(g.get('role'))}" if _s(g.get("role")) else ""
            out.append(f"- [ ] {_s(g.get('name'))} — {_s(g.get('organism'))} — alleles: {al}{role}")
    else:
        out.append("_(none)_")
    out.append("")

    # 4. Metagenotypes
    out += ["## 4. Metagenotypes  (pathogen genotype × host genotype)", ""]
    metas = canto.get("metagenotypes") or []
    if metas:
        for m in metas:
            role = _s(m.get("role")).upper().replace("_", " ")
            out.append(f"- [ ] {_s(m.get('name'))} — {_s(m.get('pathogen_genotype'))} × "
                       f"{_s(m.get('host_genotype'))}" + (f" — {role}" if role else ""))
    else:
        out.append("_(none)_")
    out.append("")

    # 5. Annotations
    out += ["## 5. Annotations", ""]
    groups = _group_annotations(canto.get("annotations"))
    if groups:
        for (ftype, feature, atype), items in groups:
            out.append(f"### {_readable(atype)} — {ftype} `{feature}`")
            for a in items:
                out.append(_annotation_line(a))
            out.append("")
    else:
        out.append("_(none)_")
        out.append("")

    # 6. Submit
    out += ["## 6. Submit", "",
            "- [ ] all ⚠ flags resolved",
            "- [ ] submit session for approval (biocurator review)", ""]

    # Flags (detail)
    if flags:
        out += ["## Flags to resolve", ""]
        for f in flags:
            out.append(f"- **[{_s(f.get('category')) or 'other'}]** {_s(f.get('detail'))}")
        out.append("")

    return "\n".join(out).rstrip() + "\n"


def default_out(draft_path) -> Path:
    p = Path(draft_path)
    stem = p.stem.replace("-phiweaver-DRAFT", "").replace("-DRAFT", "")
    return p.with_name(f"{stem}-canto-worksheet.md")


def worksheet_for_draft(draft_path) -> str:
    rec = extract_record(Path(draft_path).read_text(encoding="utf-8"))
    if rec is None:
        raise SystemExit(f"no ```json block found in {draft_path}")
    if not rec.get("canto"):
        raise SystemExit(
            f"{draft_path} has no `canto` block — it predates the structured schema; "
            "populate the canto block first (see docs/CANTO-ROUTE1-BUILD-SPEC.md)")
    return render_worksheet(rec)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="Render phiweaver draft(s) into PHI-Canto entry worksheet(s).")
    ap.add_argument("drafts", nargs="+", help="draft .md file(s) with a ```json `canto` block")
    ap.add_argument("--out", help="output path (single draft only)")
    ap.add_argument("--stdout", action="store_true", help="print to stdout instead of writing files")
    args = ap.parse_args(argv)
    if args.out and len(args.drafts) != 1:
        ap.error("--out is only valid with a single draft")

    for d in args.drafts:
        md = worksheet_for_draft(d)
        if args.stdout:
            print(md)
            continue
        out = Path(args.out) if args.out else default_out(d)
        out.write_text(md, encoding="utf-8")
        print("wrote", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
