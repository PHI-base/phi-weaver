---
name: phenotype-annotation
description: Build complete PHI-Canto phenotype annotations (annotation type, PHIPO term, evidence code, conditions, extensions) for a genotype or interaction. Use after genotypes exist; delegates PHIPO term selection to the phipo-mapping skill.
backing_script: null
tests: null
inputs:
  - genotype or metagenotype (from genotype-creation)
  - phenotype description + source location (figure/table)
  - experimental method + conditions
outputs:
  - annotation type (single-species / interaction / gene-for-gene)
  - verified PHIPO term (via phipo-mapping) + evidence code
  - relevant conditions and extensions (tissue, severity, penetrance, control link)
  - figure/table reference; explicit "no good term/evidence" where applicable
---

# Phenotype Annotation

## Purpose
Assemble a complete, review-ready phenotype annotation: the right annotation type, a
verified PHIPO term, the correct evidence code, and only the meaningful conditions and
extensions. Detailed field-by-field conventions live in
`06-Training/Quick-Reference-Phenotype-Annotation.md`. This skill covers the whole
annotation; choosing the PHIPO term itself is delegated to the phipo-mapping skill.

## When to use
- After genotype-creation, whenever a phenotype (single-species or interaction) needs to be
  recorded against a genotype or metagenotype.

## Workflow
1. Decide the annotation type: single-species (pathogen or host alone), interaction
   (pathogen–host together), or gene-for-gene. For gene-for-gene / effector–host cases
   (guard/decoy model, effector GO tagging, R-gene extensions, inverse/NETS), use the
   `gene-for-gene` skill.
2. Select the PHIPO term via the phipo-mapping skill
   (`python3 -m phiweaver.lookup.map_phenotype "<phenotype phrase>"`), reading definitions
   rather than names and preferring the most specific term. Verify the chosen ID with
   `python3 -m phiweaver.lookup.validate_ontology_ids PHIPO:XXXXXXX`.
   For an **interaction** phenotype the primary term must be a **measured/observed** phenotype
   (e.g. `PHIPO:0000365` decreased pathogen growth within host) — an **interpretation** like
   "reduced virulence" is **not** the primary term (do not use `PHIPO:0000015` as primary); it
   goes in the annotation extension (curator convention, 2026-07-15; conventions doc).
3. Choose the evidence code that matches the experimental method (direct assay, inferred
   from mutant, microscopy, growth assay, expression analysis, …).
4. Add only meaningful conditions (medium, temperature, chemical, delivery); do not
   over-specify standard conditions or details already implied by the term.
5. Add extensions — single-species (penetrance, severity, assayed feature) or interaction
   (host tissue, infective ability, control genotype, outcome).
6. Attach the figure/table reference and any clarifying comment.
7. If no term fits or the evidence is unclear, say so explicitly rather than forcing a term
   or code.

## Expected outputs
- Annotation type.
- Verified PHIPO term ID + label, with an evidence code.
- Meaningful conditions and extensions only.
- Figure/table reference; explicit "no good match" where applicable.

## Quality-control checks
- The PHIPO term's definition matches the observation; the most specific term is used; the
  ID is verified current (see phipo-mapping / validate_ontology_ids).
- The evidence code matches the experimental method.
- Interaction phenotypes link a control genotype/metagenotype where one exists.
- Effector genes carry GO:0140418 on the gene annotation where applicable.

## Human review
- Every annotation is a draft suggestion; a curator confirms term, evidence, conditions and
  extensions in PHI-Canto before submission. Flag low-confidence or "no match" cases
  prominently.
