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

`strain_background_warnings` covers the same shape for Canto's two genotype-table columns. The
curator's 2026-07-25 ruling makes `strain` and `background` complementary — a wild type carries a
strain, a mutant carries a background, never both — so a genotype missing its field is an omission
nothing else reveals. It bites at entry, not just on paper: Canto requires a strain per organism
before any genotype can be created, so an unset strain stalls the curator on the first screen.

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


def strain_background_warnings(canto: dict) -> List[str]:
    """Return warnings for genotypes whose `strain` / `background` fields don't follow the ruling.

    Wild type → `strain`; mutant → `background`; never both. A genotype counts as a mutant if it
    has alleles *or* a background — the same two-signal test table A2 uses, because an ectopic
    insertion in a wild-type parent (AM30, PMID:9927411) carries no allele and would otherwise
    read as a wild type.
    """
    warnings: List[str] = []
    for g in canto.get("genotypes") or []:
        nm = _s(g.get("name"))
        if not nm:
            continue
        strain, background = _s(g.get("strain")), _s(g.get("background"))
        is_mutant = bool([x for x in (g.get("alleles") or []) if _s(x)]) or bool(background)
        if strain and background:
            warnings.append(f"genotype '{nm}' sets both 'strain' ({strain}) and 'background' "
                            f"({background}) — they are complementary; a wild type carries a "
                            f"strain, a mutant a background")
        elif is_mutant and strain:
            warnings.append(f"genotype '{nm}' has alleles but sets 'strain' ({strain}) — a mutant "
                            f"is named by its allele; its parent strain belongs in 'background'")
        elif is_mutant and not background:
            warnings.append(f"genotype '{nm}' is a mutant with no 'background' — record its parent "
                            f"strain plus the endogenous copy's status, or flag it if the paper "
                            f"does not say")
        elif not is_mutant and not strain:
            warnings.append(f"genotype '{nm}' is a wild type with no 'strain' — Canto needs a "
                            f"strain/cultivar per organism before any genotype can be created, "
                            f"so table A2 cannot pre-fill it")
    return warnings


def _naming_stem(s: str) -> str:
    """Reduce a name to a comparable stem: no case, no Δ, no punctuation."""
    s = s.lower().replace("δ", "").replace("∆", "").replace("delta", "")
    return "".join(ch for ch in s if ch.isalnum())


def _allele_stem(allele: str) -> str:
    """An allele's gene stem — its parenthesised qualifier dropped.

    Allele names use brackets for the *qualifier* (`SdhC1(ectopic)`, `FpTox2(reintroduced)`,
    `Ztknr4+[WT level]`), which the genotype name has no reason to repeat. Genotype names use
    them for genotype *content* (`tomato 76R (Pto/Pto)`), so this strips them from the allele
    side only.
    """
    out, depth = [], 0
    for ch in allele:
        if ch in "([":
            depth += 1
        elif ch in ")]":
            depth = max(0, depth - 1)
        elif depth == 0:
            out.append(ch)
    return _naming_stem("".join(out))


def genotype_naming_warnings(canto: dict) -> List[str]:
    """Flag mutant genotypes named by an isolate label instead of by their allele.

    Curator ruling 2026-07-25: a mutant is named by its **allele**, not by whatever isolate label
    the paper gives it (`AM25` is the `abc1-2Δ` genotype). The deterministic form of that rule is
    that a mutant's name should contain one of its alleles' gene stems — which holds for every
    shape the drafts use, including strain-prefixed names (`Pta6605 ΔfleQ`), complementation
    (`SdhC1Δ-C` ← `SdhC1(ectopic)`) and multi-allele genotypes.

    Deliberately conservative: a genotype is flagged only when **no** allele matches, so a short
    stem that matches by accident yields a miss rather than a false accusation.
    """
    warnings: List[str] = []
    for g in canto.get("genotypes") or []:
        nm = _s(g.get("name"))
        alleles = [_s(x) for x in (g.get("alleles") or []) if _s(x)]
        if not nm or not alleles:
            continue
        name_stem = _naming_stem(nm)
        # Match on either form: the stem (for `SdhC1Δ-C` ← `SdhC1(ectopic)`, where the name has no
        # reason to carry the qualifier) or the whole allele (for `Pt-Agro Pt31812(FL)-OE`, where
        # the name repeats it verbatim and stripping the bracket would break the match).
        stems = [st for a in alleles for st in (_allele_stem(a), _naming_stem(a)) if st]
        if stems and not any(st in name_stem for st in stems):
            warnings.append(f"genotype '{nm}' names none of its alleles ({', '.join(alleles)}) — a "
                            f"mutant is named by its allele, not by the paper's isolate label; "
                            f"renaming also touches its metagenotypes and every annotation feature")
    return warnings


def coverage_for_draft(draft_path) -> List[str]:
    """Read a draft and return its coverage warnings ([] if no `canto` block or clean)."""
    rec = extract_record(Path(draft_path).read_text(encoding="utf-8")) or {}
    canto = rec.get("canto") or {}
    return (coverage_warnings(canto) + strain_background_warnings(canto)
            + genotype_naming_warnings(canto))
