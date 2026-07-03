#!/usr/bin/env python3
"""
phiweaver.batch_summary — roll up phiweaver draft flags into a review dashboard.

Batch drafting is unattended: instead of asking the curator questions mid-run, each draft
records what it could not resolve as **structured flags** (category + detail) plus a **triage**
verdict, inside its machine-readable ```json block (see the curation-example template). This
scans a set of draft files and writes one **batch review** listing every paper — most in need of
attention first — with its triage, an objective auto-check signal, and its flags, then rolls the
flags up by category so the curator can work through them (and even batch the review, e.g. "all
accessions at once").

Pure stdlib; emits markdown (and optional CSV).

Usage (from the repo root):
    python3 -m phiweaver.batch_summary /path/active/*-phiweaver-DRAFT.md
    python3 -m phiweaver.batch_summary drafts/*.md --out BATCH-REVIEW.md --csv batch.csv
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from pathlib import Path
from typing import List, Optional

_JSON_BLOCK = re.compile(r"```json\s*(.*?)```", re.DOTALL)

# canonical flag categories (roll-up order); unknown categories are kept and appended
FLAG_CATEGORIES = [
    "needs_pmid", "needs_accession", "needs_term_choice", "needs_genotype_modelling",
    "needs_evidence_code", "scope_question", "completeness_gap", "other",
]
# triage verdicts, most-attention-first
TRIAGE_ORDER = {
    "needs_human_decision": 0, "scope_uncertain": 1, "partial": 2,
    "in_scope": 3, "out_of_scope": 4, "unspecified": 5,
}


def extract_record(md_text: str):
    """Parse the first ```json ... ``` block in a draft, or return None."""
    m = _JSON_BLOCK.search(md_text)
    if not m:
        return None
    return json.loads(m.group(1))


class DraftSummary:
    def __init__(self, path, rec: dict):
        self.path = Path(path)
        self.name = self.path.stem
        meta = rec.get("meta") or {}
        self.paper = meta.get("paper") or self.name
        self.pmid = meta.get("pmid") or ""
        self.triage = rec.get("triage") or "unspecified"
        self.flags = [f for f in (rec.get("flags") or []) if isinstance(f, dict)]
        vals = [str(v) for v in (rec.get("auto_check") or {}).values() if v]
        self.auto_ok = sum(1 for v in vals if v.lower().startswith("ok"))
        self.auto_attn = sum(1 for v in vals if v.upper().startswith(("FLAG", "NOT")))

    @property
    def categories(self) -> Counter:
        return Counter(f.get("category", "other") for f in self.flags)

    def sort_key(self):
        return (TRIAGE_ORDER.get(self.triage, 5), -len(self.flags), self.name)


def load_drafts(paths) -> List[DraftSummary]:
    out, skipped = [], []
    for p in paths:
        rec = extract_record(Path(p).read_text(encoding="utf-8"))
        if rec is None:
            skipped.append(str(p))
            continue
        out.append(DraftSummary(p, rec))
    out.sort(key=lambda d: d.sort_key())
    return out, skipped


def _ordered_categories(seen) -> List[str]:
    known = [c for c in FLAG_CATEGORIES if c in seen]
    extra = sorted(c for c in seen if c not in FLAG_CATEGORIES)
    return known + extra


def render_markdown(drafts: List[DraftSummary], skipped=None) -> str:
    out = [
        "# Batch review",
        "",
        f"**{len(drafts)} draft(s)**, most in need of attention first. *Auto* is phiweaver's "
        "objective pre-check (ok = verified; attn = FLAG/NOT, needs a human). *Flags* are curator "
        "actions recorded during unattended drafting — nothing was asked mid-run.",
        "",
        "| # | Paper | Triage | Auto ok/attn | Flags | Categories |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for i, d in enumerate(drafts, 1):
        cats = ", ".join(_ordered_categories(d.categories)) or "—"
        out.append(f"| {i} | {d.paper} | {d.triage} | {d.auto_ok}/{d.auto_attn} | "
                   f"{len(d.flags)} | {cats} |")
    out.append("")

    # roll-up by category across all papers
    all_cats = Counter()
    for d in drafts:
        all_cats.update(d.categories)
    if all_cats:
        out += ["## Flags by category (across the batch)", ""]
        for cat in _ordered_categories(all_cats):
            out.append(f"### {cat} ({all_cats[cat]})")
            for d in drafts:
                for f in d.flags:
                    if f.get("category", "other") == cat:
                        out.append(f"- **{d.name}** — {f.get('detail', '').strip()}")
            out.append("")

    # triage tally
    tri = Counter(d.triage for d in drafts)
    out += ["## Triage", ""]
    for t in sorted(tri, key=lambda x: TRIAGE_ORDER.get(x, 5)):
        out.append(f"- {t}: {tri[t]}")
    out.append("")

    if skipped:
        out += ["## Skipped (no machine-readable draft block)", ""]
        out += [f"- {s}" for s in skipped] + [""]
    return "\n".join(out)


def write_csv(drafts: List[DraftSummary], path):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["paper", "pmid", "triage", "auto_ok", "auto_attn", "flag_count", "categories"])
        for d in drafts:
            w.writerow([d.paper, d.pmid, d.triage, d.auto_ok, d.auto_attn, len(d.flags),
                        "; ".join(_ordered_categories(d.categories))])


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="Roll up phiweaver draft flags into a batch review dashboard.")
    ap.add_argument("drafts", nargs="+", help="draft .md file(s) with a ```json block")
    ap.add_argument("--out", help="write the markdown review here (default: stdout)")
    ap.add_argument("--csv", help="also write a CSV summary here")
    args = ap.parse_args(argv)

    drafts, skipped = load_drafts(args.drafts)
    md = render_markdown(drafts, skipped)
    if args.out:
        Path(args.out).write_text(md, encoding="utf-8")
        print(f"wrote {args.out} ({len(drafts)} draft(s))")
    else:
        print(md)
    if args.csv:
        write_csv(drafts, args.csv)
        print(f"wrote {args.csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
