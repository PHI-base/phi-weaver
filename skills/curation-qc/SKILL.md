---
name: curation-qc
description: Quality-check a draft curation for completeness, accuracy, and provenance before human review. Use before marking any curation ready for a curator.
backing_script:
  - phiweaver/lookup/validate_ontology_ids.py
  - phiweaver/lookup/query_uniprot.py
tests: tests/test_validate_ontology_ids.py
inputs:
  - draft curation (file or notes)
outputs:
  - QC report (pass / fail / needs-attention per check)
  - ranked list of unresolved issues and missing data
  - "draft — not validated" marker
---

# Curation QC

## Purpose
Run a consistency and accuracy check over a draft curation so the curator receives a
clean, provenance-complete draft.

## When to use
- Before a draft curation is handed to a curator or marked "ready for review".

## Workflow
1. Check every gene/protein has a verified UniProtKB accession (see `uniprot-lookup`).
2. Check every ontology term (PHIPO/GO/PHIDO) ID exists and is non-obsolete. Run
   `python3 scripts/validate_ontology_ids.py --file <draft>` to validate every ID in the
   draft at once (or pass IDs directly); obsolete and not-found terms fail the check.
3. Check each annotation has: evidence type, source location (figure/table), and
   experimental conditions where relevant.
4. Check pathogen and host organisms/strains are specified.
5. Check provenance is recorded: input file, commands, assumptions, outputs, uncertainties.
6. Check evidence / interpretation / speculation are separated and labelled.
7. Check team-settled convention violations (see
   `07-Standards/PHI-Canto-Curation-Conventions.md`; source: PHI-base/curation closed issues,
   collected 2026-07-12):
   - **No PHIPO_EXT term used as a primary annotation term** — PHIPO_EXT is extension-only, in
     the `gene_for_gene_interaction` extension; the primary term must be a PHIPO term. Using it
     as a primary term is a curation error. (`#249`)
   - **No `Unknown` expression level** on any allele — must be `not assayed` / `overexpression` /
     a real level. (`#70`)
   - **No `ISS` evidence code** on GO annotations (rejected by the team; use experimental codes
     or TAS). (`#246`, `#245`)
   - **Disease name only on natural host + visible disease** — not on non-natural hosts or where
     no disease is observed. (`#49`)
   - **Growth-secondary phenotypes are justified or flagged** — for any phenotype annotated on a
     genotype that is also severely growth-/fitness-impaired, check it is either shown to be
     growth-independent (mutant grows normally, readout biomass-normalised, or complementation
     rescues) or carries an explicit "may be pleiotropic / growth-secondary" comment and a flag;
     and that no specific GO function is asserted from a growth-confounded phenotype alone.
     (phiweaver working convention, pending team confirmation — see the "Phenotype interpretation"
     section of the conventions doc.)
8. Compile a QC report: pass items, issues, and open questions.

## Expected outputs
- QC report listing each check as pass / fail / needs-attention.
- A ranked list of unresolved issues and missing data.
- A clear "draft — not validated" marker on the curation.

## Quality-control checks
- No invented identifiers or terms slipped through (all verifiable).
- Nothing stated as fact without a source.
- Uncertainties are surfaced, not hidden.

## Human review
- QC prepares a curation; it does not approve one. A curator must validate before any
  submission to PHI-base. Unresolved issues block "validated" status.
