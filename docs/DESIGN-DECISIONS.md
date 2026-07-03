# PHI-Weaver — Design Decisions & System Record

**Purpose:** the *why* behind PHI-Weaver — the key design decisions and their rationale, plus a
snapshot of the system as built. Companion docs: `OVERVIEW.md` (what it can do),
`MODULARITY-PLAN.md` (the refactor), `PLUGIN-ARCHITECTURE.md` (long-term direction),
`ADDING-A-MODULE.md` (how to extend). Session-by-session history lives in
`11-CLAUDE-AI/SESSION-LOGS/`.

Keep this current: when a real design choice is made or reversed, add/adjust an entry.

---

## System as built (snapshot: 2026-07-03)

- **Engine** — importable package `phiweaver/`: `lookup/` (UniProt, ontology validation,
  phenotype→PHIPO), `tracking/` (SQLite DB + namespaced migrations + repository + reporting),
  `pipeline/` (orchestration), `pdf/` (conversion), `common/` (shared envelope), `registry.py`
  (skill registry), `curation_examples.py` (example-library index). Run from repo root
  (`python3 -m phiweaver.…`), stdlib-only, install optional.
- **Skills (6)** — `paper-triage → uniprot-lookup → genotype-creation → phenotype-annotation
  (via phipo-mapping) → curation-qc`; enumerated in `skills/REGISTRY.md`.
- **Curation-example library** — `07-Standards/curation-examples/`: flat, tag-classified worked
  examples with a generated `INDEX.md` (`phiweaver.curation_examples`).
- **Content vault** — numbered Obsidian folders; literature lives in external storage
  (`PHI_LITERATURE_ROOT`, default `../PHI-Canto-Literature/`).
- **Tracking DB** — SQLite, canonical home `11-CLAUDE-AI/db/phi_canto_tracking.db`.
- **Operational material** — `11-CLAUDE-AI/`: session logs, `vault-ops/` tools, guides, and
  compatibility shims at old paths.
- **Safety net** — `phiweaver.smoke` (7 checks) + 69 network-free unit tests gate every change.

---

## Decisions

Each entry: **context → decision → why → alternatives → status.**

### D1 — Two layers: importable engine vs content vault
The repo mixes a tool engine and Obsidian content. **Decision:** keep them separate — a
tool-agnostic `phiweaver/` package (importable, testable) and a content vault (notes) with
literature externalised. **Why:** engine and data evolve independently; the engine can be reused
against different content. **Alternatives:** one intertwined tree (rejected — untestable, not
portable). **Status:** done (modularity P1–P7).

### D2 — One module contract + a shared envelope
New capabilities must plug in predictably. **Decision:** a module = a skill (workflow) + an
optional deterministic tool + tests, wired by machine-readable frontmatter and a generated
registry. Every tool returns a structured result with `status`, payload, and **provenance**;
`--json`; exit `0/1`; **injectable I/O** so tests run offline. **Why:** independent testability
and discoverability; a clean seam for future modules. **Status:** done (P2); the basis for the
plug-in direction (D6).

### D3 — Run-from-root, stdlib-only, zero-setup
**Decision:** the core depends only on the Python standard library and runs from the repo root;
`pip install -e .` is optional (PEP 668 blocks it on some machines). **Why:** a domain scientist
should be able to run it with no environment fuss; keeps the core light. **Status:** done. Heavy
dependencies (vision/ML, a local model) are pushed behind the plug-in boundary (D6), never into
the core.

### D4 — Never guess
**Decision:** tools never invent identifiers or terms; ambiguity and "not found" are explicit
statuses. UniProt accessions are resolved, ontology IDs verified to exist and be non-obsolete,
phenotype phrases mapped only to real PHIPO terms (else `no_match`), interaction counts taken
only from explicit note structure. **Why:** scientific accuracy; a wrong draft is worse than an
incomplete one. **Status:** enforced throughout; central to trust in the drafts and examples.

### D5 — SQLite tracking DB: canonical location + namespaced migrations
**Decision:** one fixed DB home (`11-CLAUDE-AI/db/…`), resolved via `repo_root()` regardless of
working directory; schema evolves through a namespaced, versioned migration runner (a module
adds tables under its own namespace without editing core). **Why:** every consumer reads/writes
the same DB; modules can extend the schema cleanly. **Status:** done (P5 + the 2026-07-02
path fix).

### D6 — North star: a plug-in host, plugins out-of-process
The valuable future modules (figure/image → phenotype; phenotype → PHIPO) are built
independently and carry heavy, conflicting dependencies. **Decision:** PHI-Weaver becomes a host;
plugins run **out-of-process** (subprocess/container) and speak the shared envelope; a manifest
declares their I/O types; a conformance harness gates them before incorporation. **Why:** the
process boundary isolates each plugin's dependencies from the stdlib-only core; the envelope is
the ABI. **Alternatives:** in-process imported plugins (rejected — one dependency environment
breaks with the first ML plugin). **Status:** designed (`PLUGIN-ARCHITECTURE.md`), not built.

### D7 — Deployment: light core orchestrates GPU work on ROGER
**Decision:** a CPU-light portable orchestrator (Linux server / WSL2 / Docker) dispatches heavy
work (a **local AI** and vision modules) to the ROGER GPU cluster as containers (Docker/Apptainer
parity); reasoning stages call a pluggable inference backend (local model, or cloud Claude for
dev); model identity is recorded in provenance for reproducibility. **Why:** the core needs no
GPU and stays portable; batch/agentic runs become feasible. **Status:** designed, deferred.

### D8 — Start simple; defer heavy infrastructure
**Decision:** treat D6/D7 as the destination, not the first step; do the simplest thing that works
and add complexity only when a concrete need forces it (containers/HPC/plugin framework will need
collaborator or research-computing help). **Why:** the maintainer is a domain scientist, not a
software engineer; premature infrastructure is cost without payoff. **Status:** standing
principle.

### D9 — Vault deprioritised; decouple engine from it
**Decision:** the Obsidian folder scheme is a human-curator convenience, not the source of
modularity (that lives in `phiweaver/` + the registry); the engine must not depend on vault
layout. Removed the dead vault-ops coupling from the pipeline — the engine now references
`11-CLAUDE-AI/` only for the tracking DB and session logs. **Why:** the orchestrator must run
headless (server/cluster) with no vault present. **Status:** done for the coupling; folder
cosmetics left as-is (acceptable/justifiable for their purpose).

### D10 — Curation examples: a validated, tag-classified library used by retrieval
**Decision:** worked curations live as flat markdown files under `07-Standards/curation-examples/`,
classified by **multi-value tags** (not per-class subfolders), with a generated `INDEX.md`
(all-examples table + browse-by-topic). An example is a **draft** until a curator sets
`status: validated`; only validated examples are used as references. phiweaver **retrieves**
matching examples as in-context few-shot references — this is retrieval, **not** model training.
**Why:** an example is usually multi-class (effector + gene-deletion + interaction), so folders
would force a false single home and break tag-overlap retrieval; the validated gate matters
because a wrong example propagates its mistakes. **Alternatives:** folder-per-class (rejected —
multi-class overlap); JSON schema now (deferred — no machine consumer yet). **Status:** scaffold
built (generator + template + tags + index); examples to be produced by curating real papers.

### D11 — Deliberately deferred / not done
- **Full vault renumbering** — low value; numbering gaps left cosmetic.
- **JSON curation-record schema** — only once a machine consumer exists (AI few-shot / gold-
  standard QC tests); it should mirror PHI-Canto's annotation model.
- **`physical-interaction` scope** — confirm it is in PHI-Canto's phenotype scope before building
  an example for it.
- **`04-Literature/`** — kept as a migration signpost; the live workflow uses external storage.
- **Direct PHI-Canto submission / automated entity recognition** — genuine future capability.
