---
name: curation-qc
description: Quality-check a draft curation for completeness, accuracy, and provenance before human review. Use before marking any curation ready for a curator.
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
7. Compile a QC report: pass items, issues, and open questions.

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
