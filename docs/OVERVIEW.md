---
created: 2026-06-11
type: documentation
tags: [docs]
project: PHI-Weaver
---

# PHI-Weaver — One-Page Overview

**What it is:** an AI-assisted biocuration toolkit for the **PHI-base / PHI-Canto**
pathogen–host interaction databases. It turns published papers into structured,
PHI-Canto-ready annotation **drafts** and tracks curation progress — always as *draft
curator assistance*, never a replacement for an expert curator.

---

## What it can do today

| Capability | How | Backed by |
|---|---|---|
| **Convert papers** (PDF or JATS XML → clean markdown, images + captions) | `python3 -m phiweaver.pipeline.curation_pipeline process-paper` | `phiweaver/pdf/`, `phiweaver/jats/` |
| **Triage a paper** for curatable PHI content (scope verdict + candidate items) | `paper-triage` skill | reasoning + converter |
| **Resolve genes/proteins** to a UniProtKB accession + evidence-backed function | `uniprot-lookup` skill | `phiweaver/lookup/query_uniprot.py` |
| **Create genotypes** (alleles, complementation, multi-allele, expression level) | `genotype-creation` skill | reasoning + PHI-Canto conventions |
| **Map phenotypes** to real PHIPO terms (never invented; `no_match` if none fit) | `phipo-mapping` skill | `phiweaver/lookup/map_phenotype.py` (EBI OLS) |
| **Annotate phenotypes** (type, term, evidence code, conditions, extensions) | `phenotype-annotation` skill | via phipo-mapping + validator |
| **Validate ontology IDs** (PHIPO/GO/PHIDO/MOD/UniProtKB: format + exists + non-obsolete) | `phiweaver/lookup/validate_ontology_ids.py` | EBI OLS (GO/PHIPO/MOD) + bundled `phido.obo` (PHIDO) |
| **QC a draft curation** before human review | `curation-qc` skill | the validator + lookups |
| **Track progress + real completion metrics** (status→curated; protein & interaction counts derived from the notes) | `curation_pipeline.py complete-paper`, `daily_curation.py` | SQLite DB |
| **Reuse validated examples** (worked curations, tag-classified, retrieved as references) | `python3 -m phiweaver.curation_examples` → `07-Standards/curation-examples/` | markdown + generated index |
| **Import a gold-standard curation** (a completed PHI-Canto session → validated example) | `gold-standard-import` skill | `07-Standards/curation-examples/` |
| **Benchmark curation quality** (blind, scored vs gold standards; shareable HTML report) | `benchmark` skill → scorecards → `benchmark_report` | `07-Standards/curation-benchmarking/` |
| **Session logging + dev timeline** | `phiweaver/tracking/session_logger.py`, `11-CLAUDE-AI/vault-ops/` | SQLite + markdown |
| **Verify the toolkit is healthy** (fresh checkout / Codespace) | `python3 -m phiweaver.smoke` | — |

Guardrails are enforced throughout: never invent identifiers/terms; check UniProtKB first;
verify ontology terms exist and aren't obsolete; separate evidence / interpretation /
speculation; preserve provenance. (See `AGENTS.md`.)

## Current architecture

Two clean layers:

- **Content vault** — Obsidian notes in numbered folders (`05-Protocols`, `06-Training`,
  `07-Standards`, `08-Wiki`, …). Literature/media live **outside** the repo
  (`PHI_LITERATURE_ROOT`, default `../PHI-Canto-Literature/`; a `demo-literature/` folder
  in Codespaces). Keeps the engine lean and content portable.
- **Tooling engine** — deterministic, testable tools:
  - `phiweaver/` — the importable engine package: `lookup/` (UniProt, ontology validation,
    phenotype→PHIPO), `tracking/` (SQLite DB + migrations + repository), `pipeline/`
    (orchestration), `pdf/` (conversion), `common/` (shared envelope), `registry.py` (skill
    registry), `curation_examples.py` (example-library index). Run from the repo root
    (`python3 -m phiweaver.…`), stdlib-only; install optional. `scripts/` keeps thin
    compatibility shims for the old command paths.
  - `skills/` — one folder per reusable workflow (`SKILL.md`), **tool-agnostic** (Claude
    Code via `CLAUDE.md`, OpenCode natively); the **6 skills** are enumerated in
    `skills/REGISTRY.md`.
  - `07-Standards/curation-examples/` — the validated **curation-example library** (worked
    examples, tag-classified, with a generated `INDEX.md`) that phiweaver retrieves
    references from when drafting a similar case.
  - `11-CLAUDE-AI/` — Claude/vault-operational material: session logs, `vault-ops/` (dev
    timeline generators + the Obsidian reorganiser), operational guides, the tracking DB,
    and compatibility shims.
  - `AGENTS.md` is the single source of truth; `CLAUDE.md` is a thin bridge; `docs/` holds
    the deep references (`ADDING-A-MODULE.md`, `DESIGN-DECISIONS.md`, `PLUGIN-ARCHITECTURE.md`).

**Data flow:** `PDF → convert → triage → entity/UniProt lookup → genotype creation →
phenotype mapping (PHIPO) + validation → phenotype annotation → QC → tracking DB
(completion metrics) → curator review → PHI-Canto`.

**Safety net:** `phiweaver.smoke` (7 checks) + the unit suite (69 tests) gate every change
and run on Codespace build, so parts can be updated with confidence.

## Future improvement possibilities

- **Structural (modularity):** ✅ **complete** — the importable `phiweaver/` package (P1),
  the module contract + registry (P2), co-located tests (P3), the `11-CLAUDE-AI/` split (P4,
  extended 2026-07 into `vault-ops/` + engine decoupling), the DB migration layer (P5),
  skill→tool links (P6), and the folder-prefix tidy (P7) all landed. See
  `docs/MODULARITY-PLAN.md` and `docs/DESIGN-DECISIONS.md`.
- **Curation examples:** the validated-example library is scaffolded; the next step is
  producing the first worked examples by curating real papers (phiweaver drafts →
  human-validated).
- **Plug-in host + local AI (a direction, not built):** PHI-Weaver as a host for
  independently-developed modules (figure→phenotype, phenotype→PHIPO), run out-of-process
  with a local AI on the ROGER GPU cluster and a light portable core. See
  `docs/PLUGIN-ARCHITECTURE.md`.
- **Capability (genuinely future):** automate entity recognition / ontology suggestion ·
  direct PHI-Canto submission · richer completion analytics.

None of these are blockers — the toolkit is functional now.
