---
name: paper-triage
description: Assess whether a paper contains curatable pathogen–host interaction data for PHI-base/PHI-Canto and outline what could be curated. Use when a new paper/PDF enters the pipeline.
---

# Paper Triage

## Purpose
Decide whether a paper is in scope for PHI-base curation and summarise its curatable
content, so curator time goes to high-value papers.

## When to use
- On any new paper/PDF added to the active pipeline, before deep curation.

## Workflow
1. Convert/read the paper — for a PDF, run the pipeline's converter
   (`python3 11-CLAUDE-AI/curation_pipeline.py process-pdf <file>`, or
   `11-CLAUDE-AI/pdf-convert-skill/pdf-convert.py` directly). See `docs/PDF-CONVERTER-USAGE.md`.
2. Identify pathogen(s) and host(s), and whether an interaction phenotype is studied.
3. Identify genes/proteins with experimental evidence (knockout, complementation,
   overexpression, biochemical, etc.).
4. Note interaction outcomes (gain/loss of virulence, resistance, disease phenotype).
5. Classify: in-scope / partially in-scope / out-of-scope, with a one-line reason.
6. List candidate curation items (genes, phenotypes, metagenotypes) — as candidates,
   not confirmed annotations.

## Expected outputs
- Scope verdict + reason.
- Pathogen/host list with organisms.
- Candidate genes/proteins with the evidence type seen.
- Candidate phenotype/disease items.
- Open questions / missing information.

## Quality-control checks
- Every candidate ties to a specific figure/table/section.
- Evidence type is stated, not assumed.
- No accessions or ontology terms invented at triage (defer to uniprot-lookup /
  phipo-mapping).

## Human review
- The scope verdict and candidate list are a draft recommendation; a curator decides
  whether and what to curate.
