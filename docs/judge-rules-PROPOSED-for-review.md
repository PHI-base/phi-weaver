# Proposed judge rules — PENDING CURATOR REVIEW (not yet authoritative)

These three rules were suggested for the LLM-judge core primer (from a ChatGPT review of the
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

## Proposed rule 5 — Natural strains / genetic background
> For natural strains, model the strain as a **natural genetic background**. Candidate natural
> alleles may be recorded, but do not represent the strain as if only those candidate genes
> differ unless the paper demonstrates an **isogenic background**. If restoration or
> allele-swap experiments only **partially** rescue the phenotype, flag **possible additional
> genetic determinants**.

**Status / questions for Martin:**
- This aligns with the `genotype-creation` skill's treatment of background. Confirm the exact
  threshold: what counts as "demonstrates an isogenic background"?
- Is "partial rescue ⇒ flag additional determinants" always right, or are there accepted cases
  (e.g. dosage) where partial rescue is expected and not a red flag?

## Proposed rule 6 — Allele consequence vs expression level
> **Expression level** should only describe transcript/protein abundance or construct-driven
> expression. Do **not** use expression fields to describe **protein consequence**. Frameshift,
> nonsense mutation, truncation, domain loss, amino-acid substitution, insertion, deletion, or
> fusion are **allele / protein consequences**, not expression levels.

**Status / questions for Martin:**
- This is standard PHI-Canto genotype modelling (see `genotype-creation`) and I'm fairly
  confident it's correct as stated. Included here only because it's a judgement rule.
- Confirm the field vocabulary the judge should name (does PHI-Canto's UI call these "expression
  level" and "allele type" exactly?). If confirmed, this can likely move straight into the core.

## Proposed rule 7 — Mechanistic side phenotypes (⚠ needs the most calibration)
> Motility, biofilm, growth, toxin level, c-di-GMP level, enzyme activity, expression change,
> microscopy signal, and similar mechanistic observations should **not automatically** become
> PHI-Canto entry items. Enter them only if a suitable **annotation type and ontology term are
> confirmed**; otherwise keep them as **supporting notes**.

**Status / questions for Martin — I'd push back on the wording:**
- Several items in that list — **reduced/altered growth, virulence, mycotoxin / toxin
  production** — genuinely **are** curatable pathogen phenotypes with PHIPO terms. As written,
  this rule risks the judge wrongly demoting *legitimate* annotations to "supporting notes."
- Please redraw the line: which of {motility, biofilm, growth, toxin level, c-di-GMP, enzyme
  activity, expression change, microscopy} are **curatable phenotypes** in PHI-Canto vs which
  are genuinely **mechanistic side assays** that should stay as supporting notes? The rule
  should name the curatable ones as *in scope*, not sweep them all out.
