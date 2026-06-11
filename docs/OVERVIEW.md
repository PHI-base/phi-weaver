# PHI-Weaver — One-Page Overview

**What it is:** an AI-assisted biocuration toolkit for the **PHI-base / PHI-Canto**
pathogen–host interaction databases. It turns published papers into structured,
PHI-Canto-ready annotation **drafts** and tracks curation progress — always as *draft
curator assistance*, never a replacement for an expert curator.

---

## What it can do today

| Capability | How | Backed by |
|---|---|---|
| **Convert papers** (PDF → clean markdown, images + captions) | `curation_pipeline.py process-pdf` | `pdf-convert-skill/` |
| **Triage a paper** for curatable PHI content (scope verdict + candidate items) | `paper-triage` skill | reasoning + converter |
| **Resolve genes/proteins** to a UniProtKB accession + evidence-backed function | `uniprot-lookup` skill | `scripts/query_uniprot.py` |
| **Map phenotypes** to PHIPO terms (no invented IDs) | `phipo-mapping` skill | OLS |
| **Validate ontology IDs** (PHIPO/GO/PHIDO/UniProtKB: format + exists + non-obsolete) | `scripts/validate_ontology_ids.py` | EBI OLS |
| **QC a draft curation** before human review | `curation-qc` skill | the validator + lookups |
| **Track progress + real completion metrics** (status→curated, article-linked counts) | `curation_pipeline.py complete-paper`, `daily_curation.py` | SQLite DB |
| **Session logging + dev timeline** | `db/session_logger.py`, timeline scripts | SQLite + markdown |
| **Verify the toolkit is healthy** (fresh checkout / Codespace) | `scripts/smoke_test.py` | — |

Guardrails are enforced throughout: never invent identifiers/terms; check UniProtKB first;
verify ontology terms exist and aren't obsolete; separate evidence / interpretation /
speculation; preserve provenance. (See `AGENTS.md`.)

---

## Current architecture

Two clean layers:

- **Content vault** — Obsidian notes in numbered folders (`05-Protocols`, `06-Training`,
  `07-Standards`, `07-Wiki`, …). Literature/media live **outside** the repo
  (`PHI_LITERATURE_ROOT`, default `../PHI-Canto-Literature/`; a `demo-literature/` folder
  in Codespaces). Keeps the engine lean and content portable.
- **Tooling engine** — deterministic, testable tools:
  - `scripts/` — standalone tools with a shared envelope (`--json`, status, provenance,
    exit codes, injectable I/O) and **network-free tests** (`scripts/tests/`, 31 passing).
  - `skills/` — one folder per reusable workflow (`SKILL.md`), **tool-agnostic** (Claude
    Code via `CLAUDE.md`, OpenCode natively).
  - `11-CLAUDE-AI/` — the pipeline orchestrator, the SQLite tracking DB (`db/`), the PDF
    converter, timeline generators, and session logs.
  - `AGENTS.md` is the single source of truth; `CLAUDE.md` is a thin bridge; `docs/` holds
    deep references.

**Data flow:** `PDF → convert → triage → entity/UniProt lookup → ontology mapping +
validation → QC → tracking DB (completion metrics) → curator review → PHI-Canto`.

**Safety net:** `smoke_test.py` (6 checks) + the unit suite gate every change and run on
Codespace build, so parts can be updated with confidence.

---

## Future improvement possibilities

From `docs/MODULARITY-PLAN.md` (phased, behaviour-preserving, each gated by the smoke test):

- **Structural (modularity):** P1 importable `phiweaver/` package + `pyproject.toml`
  (removes `sys.path` glue) · P2 an explicit **module contract** so specialised curation
  modules plug in by convention · P3 co-located tests · P4 split the grab-bag
  `11-CLAUDE-AI/` · P5 a DB **migration** layer so modules can extend the schema.
- **Capability:** parse **interaction** counts from notes (currently explicit-only) ·
  automate entity recognition / ontology suggestion · direct PHI-Canto submission · richer
  completion analytics.
- **Quick wins:** P7 tidy the duplicate `07-` folder prefix.

None of these are blockers — the toolkit is functional now.
