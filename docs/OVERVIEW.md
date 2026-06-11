# PHI-Weaver — One-Page Overview

**What it is:** an AI-assisted biocuration toolkit for the **PHI-base / PHI-Canto**
pathogen–host interaction databases. It turns published papers into structured,
PHI-Canto-ready annotation **drafts** and tracks curation progress — always as *draft
curator assistance*, never a replacement for an expert curator.

---

## What it can do today

| Capability | How | Backed by |
|---|---|---|
| **Convert papers** (PDF → clean markdown, images + captions) | `curation_pipeline.py process-pdf` | `phiweaver/pdf/` |
| **Triage a paper** for curatable PHI content (scope verdict + candidate items) | `paper-triage` skill | reasoning + converter |
| **Resolve genes/proteins** to a UniProtKB accession + evidence-backed function | `uniprot-lookup` skill | `phiweaver/lookup/query_uniprot.py` |
| **Map phenotypes** to PHIPO terms (no invented IDs) | `phipo-mapping` skill | OLS |
| **Validate ontology IDs** (PHIPO/GO/PHIDO/UniProtKB: format + exists + non-obsolete) | `phiweaver/lookup/validate_ontology_ids.py` | EBI OLS |
| **QC a draft curation** before human review | `curation-qc` skill | the validator + lookups |
| **Track progress + real completion metrics** (status→curated, article-linked counts) | `curation_pipeline.py complete-paper`, `daily_curation.py` | SQLite DB |
| **Session logging + dev timeline** | `phiweaver/tracking/session_logger.py`, timeline scripts | SQLite + markdown |
| **Verify the toolkit is healthy** (fresh checkout / Codespace) | `python3 -m phiweaver.smoke` | — |

Guardrails are enforced throughout: never invent identifiers/terms; check UniProtKB first;
verify ontology terms exist and aren't obsolete; separate evidence / interpretation /
speculation; preserve provenance. (See `AGENTS.md`.)

---

## Current architecture

Two clean layers:

- **Content vault** — Obsidian notes in numbered folders (`05-Protocols`, `06-Training`,
  `07-Standards`, `08-Wiki`, …). Literature/media live **outside** the repo
  (`PHI_LITERATURE_ROOT`, default `../PHI-Canto-Literature/`; a `demo-literature/` folder
  in Codespaces). Keeps the engine lean and content portable.
- **Tooling engine** — deterministic, testable tools:
  - `scripts/` — standalone tools with a shared envelope (`--json`, status, provenance,
    exit codes, injectable I/O) and **network-free tests** (`tests/`, 48 passing).
  - `phiweaver/` — the importable engine package: `lookup/` (UniProt, ontology validation),
    `tracking/` (SQLite DB + migrations + repository), `pipeline/` (orchestration), `pdf/`
    (conversion), `common/` (shared envelope), `registry.py`. Run from the repo root
    (`python3 -m phiweaver.…`); install optional.
  - `skills/` — one folder per reusable workflow (`SKILL.md`), **tool-agnostic** (Claude
    Code via `CLAUDE.md`, OpenCode natively); enumerated in `skills/REGISTRY.md`.
  - `11-CLAUDE-AI/` — Claude-operational material: session logs, the dev timeline + its
    generators, operational guides, and compatibility shims.
  - `AGENTS.md` is the single source of truth; `CLAUDE.md` is a thin bridge; `docs/` holds
    deep references (incl. `ADDING-A-MODULE.md`).

**Data flow:** `PDF → convert → triage → entity/UniProt lookup → ontology mapping +
validation → QC → tracking DB (completion metrics) → curator review → PHI-Canto`.

**Safety net:** `phiweaver.smoke` (7 checks) + the unit suite (48 tests) gate every change
and run on Codespace build, so parts can be updated with confidence.

---

## Future improvement possibilities

- **Structural (modularity):** ✅ **complete** — the importable `phiweaver/` package
  (P1), the enforced module contract + registry (P2), co-located tests (P3), the
  `11-CLAUDE-AI/` split (P4), the DB migration layer (P5), skill→tool links (P6), and the
  folder-prefix tidy (P7) all landed. See `docs/MODULARITY-PLAN.md` and
  `docs/ADDING-A-MODULE.md`.
- **Capability (genuinely future):** parse **interaction** counts from notes (currently
  explicit-only) · automate entity recognition / ontology suggestion · direct PHI-Canto
  submission · richer completion analytics.

None of these are blockers — the toolkit is functional now.
