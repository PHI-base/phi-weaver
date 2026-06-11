---
name: phipo-mapping
description: Map described pathogen/host/interaction phenotypes to PHIPO ontology terms, with evidence and confidence. Use when annotating phenotypes for a curation.
backing_script: phiweaver/lookup/validate_ontology_ids.py
tests: tests/test_validate_ontology_ids.py
inputs:
  - phenotype description + source location
  - phenotype category (pathogen / host / interaction)
outputs:
  - candidate PHIPO term ID(s) + label
  - rationale + confidence per candidate
  - explicit "no good match" where applicable
---

# PHIPO Mapping

## Purpose
Suggest PHIPO (Pathogen–Host Interaction Phenotype Ontology) terms for phenotypes
described in a paper, without inventing term IDs.

## When to use
- When a phenotype, infective-ability change, or interaction outcome needs an ontology term.

## Workflow
1. Extract the phenotype description verbatim from the source (with its location).
2. Decide whether it is a single-species (pathogen or host) or interaction phenotype.
3. Search PHIPO for candidate terms matching the description.
4. Verify each candidate term ID exists and is current (not obsolete) in the ontology:
   `python3 scripts/validate_ontology_ids.py PHIPO:XXXXXXX` (checks existence + obsolescence
   via the EBI Ontology Lookup Service; never invent or "correct" an ID).
5. Propose the best term(s) with rationale. If none fit well, say so and describe the
   gap rather than forcing a term.

## Expected outputs
- Verbatim phenotype text + source location.
- Phenotype category (pathogen / host / interaction).
- Candidate PHIPO term ID(s) + label, each with rationale and confidence.
- An explicit "no good match" where applicable.

## Quality-control checks
- Every proposed term ID is verified to exist and be non-obsolete.
- The term's meaning matches the phenotype (no over-/under-specification).
- Source evidence is attached; interpretation is labelled as such.

## Human review
- All PHIPO mappings are suggestions. A curator must confirm term choice before it enters
  a submitted annotation; flag low-confidence or "no match" cases prominently.
