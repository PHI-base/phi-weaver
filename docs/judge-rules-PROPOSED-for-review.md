# Proposed judge rules — PENDING CURATOR REVIEW (not yet authoritative)

These rules were suggested for the LLM-judge core primer (from a ChatGPT review of the
handover bundle). They encode **biological-judgement / scope conventions**, so — per the
LLM-judge design note (`11-CLAUDE-AI/SESSION-LOGS/2026-07-09-llm-as-judge-discussion.md`) — a
wrong rule baked into the primer would make the judge *systematically* wrong (the
convention-gap failure mode we are trying to reduce). They are therefore **held here for
Martin's confirmation** and are **NOT included** in the generated judge bundle
(`scripts/build_judge_handover.py` does not read this file). Once you approve/correct a rule,
move it into `07-Standards/judge-core-primer.md` and regenerate.

Two of these (natural strains, mechanistic side phenotypes) may be over-generalised from a
single benchmark paper (PMID:41229162). Treat them as hypotheses to confirm across the
10-paper set, not settled rules.

---

## Proposed rule 5 — Natural strains / genetic background — ✅ APPROVED 2026-07-09, moved to core
Curator decisions (2026-07-09):
- **Entity identity:** reference-proteome accessions accepted (now core operating rule 9).
- **Causal attribution:** option **(b)** — faithful recording; accept a curation that records
  the candidate allele + notes the natural background, and flag only *overstated* sole-cause
  attribution. Do NOT demand an isogenic line. (now core operating rule 10).
- **Partial rescue:** softened to a two-sided flag (additional determinants OR dosage /
  ectopic-expression artifact). (in core operating rule 10).

Original proposed wording (superseded):
> For natural strains, model the strain as a **natural genetic background**. Candidate natural
> alleles may be recorded, but do not represent the strain as if only those candidate genes
> differ unless the paper demonstrates an **isogenic background**. If restoration or
> allele-swap experiments only **partially** rescue the phenotype, flag **possible additional
> genetic determinants**.

**Accepted convention (confirmed by Martin 2026-07-09) — reference-proteome accessions:**
Every curation needs a UniProtKB accession, and UniProt often lists only the **reference
proteome**. Canto therefore maps a natural-strain gene to the **reference gene/accession** even
though the isolate's protein may differ. This is accepted. **The judge must NOT flag a
reference-proteome accession as wrong for a natural strain.** (The isolate's sequence
difference, where defined, is recorded as the *allele* against that reference gene — see rule 6.)
This is broader than natural strains and is a candidate to become a core-primer entity-resolution
rule, pending Martin's OK on placement.

**Status / questions for Martin:**
- ENTITY IDENTITY (above): resolved — reference accessions accepted.
- CAUSAL ATTRIBUTION (separate, still open): for a natural strain that is NOT isogenic, should
  the judge (a) require an allele-swap / near-isogenic line before allowing sole-cause language
  for the candidate gene, or (b) simply require the curation to record the candidate allele +
  note the natural background, and only flag *overstated* sole-cause claims? Given "we accept"
  the reference-mapping imperfection, (b) may match practice better than demanding isogenic proof.
- Is "partial rescue ⇒ flag additional determinants" always right, or are there accepted cases
  (e.g. dosage, ectopic expression) where partial rescue is expected and not a red flag?

## Proposed rule 6 — Allele consequence vs expression level — ✅ APPROVED 2026-07-09, moved to core
> Field labels confirmed by Martin ("Expression" = abundance; "Allele type" = consequence).
> Now authoritative in `07-Standards/judge-core-primer.md` (operating rule 6). Retained here
> only as a record; no longer pending.

## Proposed rule 7 — Phenotype observations / term requests — ✅ APPROVED 2026-07-09 (one default to confirm), moved to core
Curator decision (2026-07-09): reject the "sweep to supporting notes" framing. Faithful
recording instead — **if no suitable PHIPO term exists, a valid curation records the phenotype
with a note that a new PHIPO term should possibly be requested**; the judge must accept that as
valid, not flag it as an error or omission. Now core operating rule 11.

**Resolved 2026-07-09:** purely molecular readouts (e.g. c-di-GMP level, in-vitro enzyme
activity, localisation-only microscopy) are modelled as an **annotation extension / qualifier or
condition** on the phenotype annotation they inform — not a standalone phenotype and not a PHIPO
term request. If they inform no annotation, they are supporting evidence. Rule 11 in the core
primer now reflects this; nothing left pending.

Original proposed wording (superseded):
> Motility, biofilm, growth, toxin level, c-di-GMP level, enzyme activity, expression change,
> microscopy signal, and similar mechanistic observations should **not automatically** become
> PHI-Canto entry items. Enter them only if a suitable **annotation type and ontology term are
> confirmed**; otherwise keep them as **supporting notes**.
