---
name: paper-triage
description: Assess whether a paper contains curatable pathogen–host interaction data for PHI-base/PHI-Canto and outline what could be curated. Use when a new paper/PDF enters the pipeline.
backing_script:
  - phiweaver/lookup/phibase_index.py
tests:
  - tests/test_phibase_index.py
inputs:
  - paper / PDF
  - the paper's PMID (for the already-curated check)
outputs:
  - already-curated-in-PHI-base flag (PHI accession + established pathogen/host/gene, or an explicit miss)
  - scope verdict + reason
  - pathogen/host list with organisms
  - candidate genes/proteins + evidence type
  - candidate phenotype/disease items
  - open questions / missing information
---

# Paper Triage

## Purpose
Decide whether a paper is in scope for PHI-base curation and summarise its curatable
content, so curator time goes to high-value papers.

## When to use
- On any new paper/PDF added to the active pipeline, before deep curation.

## Workflow
1. **Ask whether PHI-base already holds the paper — before spending any drafting effort:**

       python3 -m phiweaver.lookup.phibase_index <PMID>

   A hit reports the PHI accession plus the record's established gene, pathogen taxon, host
   and phenotype. **An existing curated entry wins over a fresh draft**: reconcile against
   those fields rather than re-drafting, and say so in the verdict. This matters most where
   a draft is weakest — on PMID:9927411 the established record gives the pathogen as taxid
   **318829** (*Magnaporthe oryzae*) where the draft had used *Pyricularia grisea* (148305).

   A miss is **not** proof the paper is uncurated: releases exclude in-progress PHI-Canto
   sessions, and a few records cite no PubMed ID. Report it as "not in release X", never as
   "uncurated". (First run downloads the release, ~17 MB, and caches it; `--refresh`
   re-fetches. Set `PHIBASE_CACHE` to keep the cache off a slow network mount.)
2. Convert/read the paper — run the pipeline's converter, which dispatches on file extension
   (`python3 -m phiweaver.pipeline.curation_pipeline process-paper <file>`), or call one
   directly: `python3 -m phiweaver.pdf.pdf_convert <file.pdf>` /
   `python3 -m phiweaver.jats.jats_convert <file.xml>`. See `docs/PDF-CONVERTER-USAGE.md`.
   **Prefer JATS XML where both exist** — sections, tables, figure/reference cross-references
   and the italics on gene names are declared rather than inferred from layout, and there is no
   OCR step. But check the converter's `graphics_absent` warning: JATS names image files it
   usually does not ship, so figure content may be **captions only**. If a triage judgement
   needs the panel itself, say so rather than inferring it from the caption.
3. Identify pathogen(s) and host(s), and whether an interaction phenotype is studied.
4. Identify genes/proteins with experimental evidence (knockout, complementation,
   overexpression, biochemical, etc.).
5. Note interaction outcomes (gain/loss of virulence, resistance, disease phenotype).
6. Classify: in-scope / partially in-scope / out-of-scope, with a one-line reason. If step 1
   found a hit, the verdict must say so and name the PHI accession.
7. List candidate curation items (genes, phenotypes, metagenotypes) — as candidates,
   not confirmed annotations.

## Scope rules — what we do NOT curate
Team-settled exclusions (see `07-Standards/PHI-Canto-Curation-Conventions.md`; source:
PHI-base/curation closed issues, collected 2026-07-12):
- **Natural-variant-only papers** — no engineered gene modification and no clear WT control to
  compare against (out of scope even for chemistry). (`#115`, `#181`)
- **Interspecies complementation** — a pathogen genotype cannot hold two species, so expressing
  one species' variant in another (e.g. Mg CYP51 in *S. cerevisiae*) is not curatable. (`#117`)
- **Non-pathogenic model organisms** as the sole subject (e.g. *S. cerevisiae* chemistry
  phenotypes with no pathogen). (`#115`)
- **Chemistry papers** are in scope only when they contain **lab-engineered** gene modification
  (substitution, overexpression); keep them Tier-1 (title's take-home message). (`#115`)
- **Papers with no gene-specific data are still approved** (as an empty session) so they aren't
  re-triaged for curation later — flag as "approve, no annotations", not "uncuratable". (`#112`)

## Expected outputs
- Scope verdict + reason.
- Pathogen/host list with organisms.
- Candidate genes/proteins with the evidence type seen.
- Candidate phenotype/disease items.
- Open questions / missing information.

## Quality-control checks
- The already-curated check was run, and its result is recorded either way — a hit with its
  PHI accession, or an explicit "not in release X". Silence is not a pass.
- Every candidate ties to a specific figure/table/section.
- Evidence type is stated, not assumed.
- No accessions or ontology terms invented at triage (defer to uniprot-lookup /
  phipo-mapping).

## Human review
- The scope verdict and candidate list are a draft recommendation; a curator decides
  whether and what to curate.
