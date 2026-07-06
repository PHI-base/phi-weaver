---
name: canto-worksheet
description: Turn a phiweaver curation draft into an ordered PHI-Canto entry worksheet a biocurator transcribes into canto.phi-base.org to submit the paper for review. Use when a draft is ready for a curator to enter into PHI-Canto.
backing_script:
  - phiweaver/canto/worksheet.py
tests:
  - tests/test_canto_worksheet.py
inputs:
  - a phiweaver draft (.md) whose ```json block contains a populated `canto` object
outputs:
  - one Markdown entry worksheet per draft — an ordered, dependency-respecting checklist mirroring Canto's entry steps, with curator flags surfaced
---

# Canto worksheet

## Purpose
Get a phiweaver draft into **PHI-Canto** (<https://canto.phi-base.org/>) without a write API.
The draft's structured `canto` block is rendered into an ordered Markdown checklist that a
biocurator works through top to bottom, entering each item into the Canto web tool. This is
**Route 1** of the submission plan (`docs/CANTO-ROUTE1-BUILD-SPEC.md`); it needs only a curator
web login — no server access.

## Validation model
**Entering the worksheet into PHI-Canto is itself the validation step.** As the curator
transcribes each item, they apply their judgement and Canto's controlled vocabularies /
autocompletes / dependency constraints force verification, so any draft error surfaces at entry.
The worksheet is a transcription aid, never an auto-submitter — the human is unavoidably in the
loop, and AI drafts reach the biocurator queue only *through* a curator's entry. Nothing is
invented: an annotation with no term, and every `flags` entry, is shown as a ⚠ to resolve.

## When to use
- When a draft has a populated `canto` block and a curator is ready to enter it into PHI-Canto.

## Workflow
1. **Confirm the draft has a `canto` block.** If it predates the structured schema, populate it
   first (see the `canto` fields in `07-Standards/curation-examples/_TEMPLATE.md`).
2. **Generate the worksheet** (from the repo root):
   `python3 -m phiweaver.canto.worksheet <draft.md>` → writes `<paper>-canto-worksheet.md` beside
   the draft (or `--stdout`; `--out` for a single custom path; accepts multiple drafts).
3. **Enter into Canto**, following the worksheet order (Canto enforces the dependencies):
   genes → alleles → genotypes → metagenotypes → annotations. The **UniProtKB accession** is the
   add-gene identifier; term ID + name are given so the autocomplete finds the term; extensions
   are `relation=value`.
4. **Resolve the ⚠ flags** as you go (accessions, term choices, scope questions) — these are the
   curator's calls; the worksheet lists them at the end.
5. **Submit the session for approval** once every item is entered and flags are settled.

## Expected outputs
- One Markdown worksheet per draft: six sections (genes, alleles, genotypes, metagenotypes,
  annotations, submit) in Canto's entry order, plus a flags-to-resolve list.

## Quality-control checks
- Every gene carries a **UniProtKB accession** (Canto's add-gene id); a missing one shows ⚠.
- Ontology terms show **ID + name**; an annotation with no term_id is a ⚠, not an invented term.
- Metagenotypes reference genotypes that appear earlier in the worksheet (the renderer preserves
  Canto's dependency order).
- All draft `flags` appear in the flags-to-resolve list.

## Human review
- The biocurator's entry into PHI-Canto **is** the review — apply judgement per item, reconcile
  the flags, and do not submit until the paper's curation is correct in Canto.
