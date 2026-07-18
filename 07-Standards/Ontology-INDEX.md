---
created: 2026-07-18
type: index
tags: [ontology, index, phipo, phido, peco, go]
project: PHI-Canto
---

# Ontology — Index

A **map of pointers**, not a content page. Ontology material in PHI-Weaver lives in
several homes with different cadences (a reference guide, a cheatsheet, deterministic
tools, vendored data, a gap ledger). This page says what each is and where it lives, so
you can land anywhere and find the rest. **Nothing here is duplicated** — edit the target,
not this index. The tooling rows mirror `skills/REGISTRY.md` (generated); if they drift,
the registry is authoritative.

Ontologies in scope: **PHIPO** (phenotype), **PHIDO** (disease), **GO**, **BRENDA tissue
(BTO)**, **PSI-MOD**, **PHI-ECO / PECO** (experimental conditions), plus the PHI-base
extension ontologies **PHIPO_EXT** and **FYPO_EXT** (annotation-extension values, *not*
part of PHIPO). See [[phi-eco-conditions-ontology]] for PECO background.

---

## Reference & conventions (human-authored)

| File | What it is |
| --- | --- |
| `07-Standards/Ontology-Terms-Reference.md` | The canonical reference guide — structure, common terms, selection best-practices, and QC checklist for PHIPO / PHIDO / GO / BTO / PECO, plus PHI-Canto annotation-extension relations. Start here. |
| `06-Training/Quick-Reference-Common-Ontology-Terms.md` | One-page cheatsheet of the most-used terms (training aid; a subset of the reference guide). |
| `07-Standards/PHI-Canto-Curation-Conventions.md` | Broader curation conventions that ontology annotation sits inside (evidence codes, extensions). |

## Tooling (deterministic modules under `phiweaver/lookup/`)

Each is offline-testable and follows the module I/O envelope. Backed skills are enumerated
in `skills/REGISTRY.md`; see `docs/ADDING-A-MODULE.md` for the contract.

| Tool | Does | Skill |
| --- | --- | --- |
| `validate_ontology_ids.py` | Validate ontology IDs — offline format check, then existence/obsolescence via OLS4 (GO/PHIPO/MOD/BTO) or bundled OBO (PHIDO/PECO/PHIPO_EXT/FYPO_EXT). | `curation-qc` |
| `map_phenotype.py` | Deterministic phenotype-phrase → PHIPO term search. | `phipo-mapping` |
| `map_condition.py` | Deterministic condition-phrase → PECO (PHI-ECO) term search. | `phenotype-annotation` |
| `term_context.py` | Flag PHIPO candidates whose context (free-living vs in-host) contradicts the assay. | `ontology-term-request` |
| `gap_log.py` | Append-only ledger writer for ontology gaps met during curation. | `ontology-term-request` |

## Bundled ontology data (vendored, offline)

`phiweaver/lookup/data/` — local copies of ontologies not served by OLS4, so validation and
mapping work offline. Vendored from `github.com/PHI-base/{phido,phi-eco,phipo_ext}` and
PHI-base/canto. See that folder's `README.md` for provenance and refresh steps.

- `phipo-base.obo`, `phido.obo`, `phi-eco.obo`, `phipo_ext.obo`, `fypo_extension.obo`
- `*_extensions.tsv` / `phipo_extension_relations.obo` — PHI-base extension mappings

> NB the OLS ontology named "peco" is the unrelated Planteome ontology — PHI-base PECO
> terms live **only** in the bundled `phi-eco.obo`.

## Gaps & term requests (the ontology-development loop)

| Where | What |
| --- | --- |
| `docs/ontology-gaps.jsonl` | Append-only ledger of gaps met during curation (phrase, context, PMID, outcome, tracker URL once filed). |
| `skills/ontology-term-request/` | Turns a gap into an evidence-backed term/synonym request — or, when a sibling set already fixes every field, a drafted PR against `phipo-edit.owl`. |

Species-neutrality and obsolete-term caveats before calling something a gap:
[[phipo-is-species-neutral]], [[obsolete-terms-are-fossils]].

## The ontologies themselves (external / upstream)

- PHIPO — `github.com/PHI-base/phipo` · local clone: [[phipo-local-clone]] (PRs target `master`)
- PHIDO — `github.com/PHI-base/phido`
- PHI-ECO (PECO) — `github.com/PHI-base/phi-eco`
- Browsing: OLS4 (`ebi.ac.uk/ols4`) for GO/PHIPO/BTO/MOD; QuickGO for GO.
