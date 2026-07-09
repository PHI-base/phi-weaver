#!/usr/bin/env python3
"""
phiweaver.canto.coverage — a completeness lint for a draft's `canto` block.

The referential-integrity check in the renderers catches *dangling references* (the block points
at something undefined). It cannot catch *omissions* — a metagenotype (or annotation) described in
the paper's prose but never carried into the block leaves no broken pointer. This lint adds the
complementary signal: a genotype that the block defines but barely uses.

Two advisory signals (never errors — a mutant tested only in vitro legitimately has single-species
phenotypes and no metagenotype):

- **unused** — a genotype referenced by *nothing*: not a metagenotype, not an annotation feature,
  not a `compared_to_control`. Almost always a missing metagenotype/annotation, or removable.
- **not-in-metagenotype** — a pathogen genotype used somewhere (e.g. as a control comparator or a
  single-species phenotype) but in no metagenotype. Confirm it is single-species-only, not a
  dropped interaction (this is the class that hid the complementation-control omissions).

Surfaced to stderr by the entry-queue CLI at generation time. Pure stdlib.
"""

from __future__ import annotations

from pathlib import Path
from typing import List

from phiweaver.canto.record import _s, extract_record


def coverage_warnings(canto: dict) -> List[str]:
    """Return advisory coverage warnings for a `canto` block (empty list = clean)."""
    genotypes = canto.get("genotypes") or []
    metas = canto.get("metagenotypes") or []
    anns = canto.get("annotations") or []

    meta_path = {_s(m.get("pathogen_genotype")) for m in metas}
    meta_host = {_s(m.get("host_genotype")) for m in metas}
    meta_all = meta_path | meta_host

    # anything an annotation points at: its feature, plus each compared_to_control value
    # (values may bundle several names separated by ';')
    ann_refs = set()
    for a in anns:
        ann_refs.add(_s(a.get("feature")))
        for e in a.get("extensions") or []:
            if _s(e.get("relation")) == "compared_to_control":
                for part in _s(e.get("value")).split(";"):
                    if part.strip():
                        ann_refs.add(part.strip())

    host_names = set(meta_host)
    for g in genotypes:
        if "host" in _s(g.get("role")).lower():
            host_names.add(_s(g.get("name")))

    warnings: List[str] = []
    for g in genotypes:
        nm, role = _s(g.get("name")), _s(g.get("role")) or "?"
        if not nm:
            continue
        if nm in host_names:
            if nm not in meta_host and nm not in ann_refs:
                warnings.append(f"host genotype '{nm}' is referenced by nothing "
                                f"(defined but in no metagenotype)")
            continue
        referenced = nm in meta_all or nm in ann_refs
        if not referenced:
            warnings.append(f"genotype '{nm}' ({role}) is referenced by nothing — no metagenotype, "
                            f"annotation, or control; likely a missing metagenotype/annotation, or "
                            f"removable")
        elif nm not in meta_path:
            warnings.append(f"pathogen genotype '{nm}' ({role}) is in no metagenotype — confirm it "
                            f"is single-species-only, not a dropped interaction")
    return warnings


def coverage_for_draft(draft_path) -> List[str]:
    """Read a draft and return its coverage warnings ([] if no `canto` block or clean)."""
    rec = extract_record(Path(draft_path).read_text(encoding="utf-8")) or {}
    return coverage_warnings(rec.get("canto") or {})
