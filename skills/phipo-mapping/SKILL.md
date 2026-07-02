---
name: phipo-mapping
description: Map described pathogen/host/interaction phenotypes to PHIPO ontology terms, with evidence and confidence. Use when annotating phenotypes for a curation.
backing_script:
  - phiweaver/lookup/map_phenotype.py
  - phiweaver/lookup/validate_ontology_ids.py
tests:
  - tests/test_map_phenotype.py
  - tests/test_validate_ontology_ids.py
inputs:
  - figure caption / results text (from the converted paper)
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
1. Read the figure captions and results text of the converted paper (`*_converted.md`,
   produced by the PDF converter). Figure captions are a dense source of phenotypes.
2. Identify each phenotype description verbatim, with its location. Deciding what *is* a
   phenotype is your judgement — the tools below do not do that step for you.
3. Decide whether it is a single-species (pathogen or host) or interaction phenotype.
4. Map each phrase to candidate PHIPO terms with the backing tool — it searches PHIPO via
   the EBI Ontology Lookup Service and returns real term IDs, never invented ones:
   `python3 -m phiweaver.lookup.map_phenotype "reduced virulence"`
   (a phrase with no hit is reported as `no_match`, not mapped to a guess).
5. Verify the chosen term ID exists and is current (not obsolete):
   `python3 -m phiweaver.lookup.validate_ontology_ids PHIPO:XXXXXXX`.
6. Propose the best term(s) with rationale and confidence. If none fit well, say so and
   describe the gap rather than forcing a term.

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
