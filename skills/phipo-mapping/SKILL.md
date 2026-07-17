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
   **Declare where the phenotype was measured** — `--assay-context free-living` (in-vitro
   culture) or `--assay-context in-host` (in planta). PHIPO states context in the label
   (`within host`, `on host surface`), and a free-living assay cannot use an in-host term:
   `absent DON` in culture matches `PHIPO:0000234` *pathogen deoxynivalenol within host
   absent*, which is a confident, wrong answer. Without the flag nothing marks it.
5. **Read the surviving candidates against the paper.** A search pads its result with terms
   that merely share a word — the same `absent DON` search returns `PHIPO:0000939 asexual
   spore lysis absent`, which is host-free (so unflagged) and irrelevant. A candidate that
   survives the context check has not thereby been shown to fit.
6. Verify the chosen term ID exists and is current (not obsolete):
   `python3 -m phiweaver.lookup.validate_ontology_ids PHIPO:XXXXXXX`.
7. Propose the best term(s) with rationale and confidence. If none fit well, say so and
   describe the gap rather than forcing a term. Retry alternate wordings ("level of X",
   "abnormal X biosynthesis") before calling anything a gap — lesson L2 — then hand it to
   the `ontology-term-request` skill, which records it with its evidence.

## Expected outputs
- Verbatim phenotype text + source location.
- Phenotype category (pathogen / host / interaction).
- Candidate PHIPO term ID(s) + label, each with rationale and confidence.
- An explicit "no good match" where applicable.

## Quality-control checks
- Every proposed term ID is verified to exist and be non-obsolete.
- The term's meaning matches the phenotype (no over-/under-specification).
- The term's **context** matches the assay: no in-host term for a free-living phenotype.
- Source evidence is attached; interpretation is labelled as such.

## Human review
- All PHIPO mappings are suggestions. A curator must confirm term choice before it enters
  a submitted annotation; flag low-confidence or "no match" cases prominently.
