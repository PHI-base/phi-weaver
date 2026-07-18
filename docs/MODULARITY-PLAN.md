---
created: 2026-06-11
type: documentation
tags: [docs]
project: PHI-Weaver
---

# PHI-Weaver Modularity & Refactor Plan

**Status:** ✅ complete — all phases P1–P7 landed 2026-06-11 · **Created:** 2026-06-11

A plan to make PHI-Weaver's parts independently **updatable and testable**, and to let
**specialised curation modules** be plugged in later by following one contract. This is a
**behaviour-preserving** restructure: nothing about curation output changes — only where
code lives and how the pieces find each other. Every phase is staged behind the existing
`scripts/smoke_test.py` and the unit suite.

> Captured from the 2026-06-11 structure evaluation. Implement in the phase order below;
> each phase is its own reviewable PR.

---

## 1. Where we are today

The repo has two layers:

- **Content vault** — numbered Obsidian folders (`00-Inbox` … `11-CLAUDE-AI`),
  `content-links/`, and external literature storage (`../PHI-Canto-Literature/`, override
  `PHI_LITERATURE_ROOT`).
- **Tooling engine** — `scripts/`, `skills/`, `11-CLAUDE-AI/` (pipeline, `db/`,
  `pdf-convert-skill/`, timeline generators), `docs/`, with `AGENTS.md` as the source of
  truth and `CLAUDE.md` as a thin bridge.

### What is already modular (keep, build on)
- **`scripts/` is a strong module pattern**: deterministic tools, injected I/O, a
  JSON + provenance + exit-code envelope, network-free tests. The template to extend.
- **`skills/` are cleanly separated and tool-agnostic** (Claude Code via `CLAUDE.md`,
  OpenCode natively) — a real plug-in seam.
- **Content is externalised and overridable** — engine and data evolve independently.
- **A test + smoke-test foundation exists** — the precondition for safe per-part updates.
- **Paths derive from `__file__`**; `AGENTS.md` is a single source of truth.

### Gaps that block modularity
1. **`11-CLAUDE-AI/` is a grab-bag** (15 top-level entries) mixing the orchestrator, the DB
   package, PDF conversion, timeline generators, session logs, docs, and a stray JSON
   report — unrelated concerns, different cadences, in a Claude-specific folder that holds
   tool-agnostic engine code.
2. **No package boundary**: modules find each other through scattered `sys.path`
   manipulation (4+ sites); no `pyproject.toml`, no defined import surface; tests reach
   across trees.
3. **Tests are centralised in `scripts/tests/` but cover code elsewhere** (`11-CLAUDE-AI/db`),
   not co-located, discovery hardcoded to one path.
4. **Skill→script links are prose-only and inconsistent** — `uniprot-lookup` never
   references its backing `query_uniprot.py`; no machine-readable contract.
5. **The DB layer resists extension**: `phi_canto_sqlite.py` bundles schema + sample data +
   queries + `print()`; `create_schema()` is `CREATE IF NOT EXISTS` only — **no migrations**,
   so a module needing new tables/columns can't evolve the schema cleanly.
6. **Aspirational vs actual architecture diverge**: the documented 6-module pipeline has no
   matching code seams.
7. **Content-folder taxonomy drift**: there were two `07-` prefixes (`07-Standards` and the
   old `07-Wiki`). **Resolved in P7** — `07-Wiki` → `08-Wiki`.

---

## 2. Target shape

### 2a. An importable package
Replace `sys.path` glue with a real package installed via `pip install -e .`:

```
phiweaver/
  __init__.py
  lookup/            # query_uniprot.py, validate_ontology_ids.py
  pipeline/          # curation_pipeline.py (orchestration only)
  tracking/          # db: schema, migrations, repository, reporting
  pdf/               # pdf-convert
  common/            # shared: provenance envelope, HTTP-getter injection, cache
pyproject.toml       # package metadata + console_scripts entry points
tests/               # mirrors phiweaver/ ; one discovery root
```

Claude-specific / operational material (session logs, automation guide, timeline tools)
moves out of the engine into an `agent/` (or stays in `docs/`), so the engine package is
genuinely tool-agnostic — matching `AGENTS.md`.

### 2b. The module contract (how a specialised module plugs in)
A **module = a skill + a deterministic script + co-located tests**, all wired by a small,
machine-readable contract. Standardise what `query_uniprot.py` / `validate_ontology_ids.py`
already do:

- **I/O envelope** (the module interface):
  - structured result with a `status` field, the payload, and **provenance** (source,
    cache hit/miss, UTC timestamp);
  - `--json` for machine output, human summary otherwise;
  - exit `0` on success / `1` on failure;
  - **injectable I/O** (HTTP getter / DB handle) so tests are deterministic and offline;
  - **never guess** — ambiguity and "not found" are explicit statuses, not invented data.
- **Skill frontmatter** declares the wiring, e.g.:
  ```yaml
  ---
  name: <skill>
  description: <when to use>
  backing_script: phiweaver/lookup/<tool>.py   # or null for reasoning-only skills
  inputs: [ ... ]
  outputs: [ ... ]
  tests: tests/lookup/test_<tool>.py
  ---
  ```
- **A generated registry** (`skills/REGISTRY.md` or a JSON manifest, produced by a script)
  so an agent or human can enumerate available modules and their backing tools/tests.

New specialised curation tasks then ship as: one skill folder + one script under the right
subpackage + one test file, following the envelope. Independently testable, independently
shippable, discoverable via the registry.

---

## 3. Phased migration (each phase = one PR, behind the smoke test)

| Phase | Goal | Key moves | Risk | Done when |
|------|------|-----------|------|-----------|
| **P1** ✅ done (2026-06-11) | Package + metadata | Added `pyproject.toml`; created `phiweaver/` (`lookup/`, `tracking/`, `pipeline/`) and moved the lookup tools + db modules + pipeline + smoke test in; thin shims at old paths. **Chosen: run-from-root, install optional** (PEP 668 blocks `pip install -e .` locally). | Med (import paths) | ✅ Engine + tests have **zero `sys.path` hacks** (only shims do, by design); smoke 6/6 + 31 tests green run-from-root; `pip install -e .` works where allowed |
| **P2** ✅ done (2026-06-11) | Module contract | `phiweaver/common/` holds the shared envelope (`utc_now`, `make_getter`, `ResponseCache`), used by both lookup tools; skill frontmatter (`backing_script`/`tests`/`inputs`/`outputs`) on all 4 skills; `phiweaver/registry.py` generates `skills/REGISTRY.md` and enforces the contract (`--check`, also a smoke check); `docs/ADDING-A-MODULE.md` checklist | Low | ✅ Every skill declares its wiring; registry generates + is enforced; new-module checklist documented; 39 tests + 7-check smoke green |
| **P3** ✅ done with P1 | Test relocation | Tests moved to top-level `tests/`; smoke + discovery run from repo root (`-s tests`) | Low | ✅ One discovery root; no cross-tree `sys.path` in tests |
| **P4** ✅ done (2026-06-11) | Split `11-CLAUDE-AI/` | PDF-conversion engine → `phiweaver/pdf/` (shim left at old path); dropped the stray converted-report JSON; added `11-CLAUDE-AI/README.md` documenting the folder's operational role. Scoped: `obsidian_reorganise.py` + timeline generators stay as vault-operational tooling with their data (not curation engine). | Med (many refs) | ✅ The curation engine (lookup/tracking/pipeline/**pdf**) is all under `phiweaver/`; `11-CLAUDE-AI/` is documented as Claude-operational; docs/refs updated; smoke 7/7 |
| **P5** ✅ done (2026-06-11) | Extensible DB | `phiweaver/tracking/migrations.py` (namespaced versioned runner; baseline = core v1) + `repository.py` (data-returning queries); `create_schema()` now just runs migrations; query methods delegate to the repository | Med | ✅ A module registers migrations under its own namespace without editing core; repository queries unit-tested without stdout capture; pre-existing DBs upgrade without data loss; 48 tests + smoke green |
| **P6** ✅ done (2026-06-11) | Fix skill→tool linkage | Reference `query_uniprot.py` from `uniprot-lookup`; backfill any other gaps | Low | ✅ Every backed skill names its script; covered by the registry check |
| **P7** ✅ done (2026-06-11) | Content taxonomy | Renamed `07-Wiki` → `08-Wiki` to break the duplicate `07-` prefix; updated all path references (code/docs/config + folder contents); session logs left as historical record. (A fuller semantic renumbering was judged low-value and deferred.) | Low | ✅ No duplicate folder prefixes; references updated; smoke 7/7 |

**Recommended sequencing:** P6 (+ P7) are safe quick wins and can land first or anytime.
P1→P3 deliver most of the "update/test parts independently" benefit. P4→P5 are what
specifically unlock *new specialised modules*. Do P1 before P4/P5.

---

## 4. Guardrails

- **Behaviour-preserving**: no change to curation outputs; if any behaviour must change,
  call it out explicitly in that PR.
- **Green gate every phase**: `python3 scripts/smoke_test.py` + `python3 -m unittest
  discover` must pass before and after.
- **No mass reformatting**; follow `AGENTS.md` §4 coding standards.
- **Respect file-safety rules** (`AGENTS.md` §5): show moves/deletions; keep the DB and
  literature out of git.
- **One phase per PR**, small and reviewable; update affected docs in the same PR.

---

## 5. Open questions
- Final name/location for agent-operational material (`agent/` vs `docs/` vs keep a slim
  `11-CLAUDE-AI/` for session logs only).
- Registry format: human `REGISTRY.md`, machine `registry.json`, or both (generated).
- Migration runner: hand-rolled (a `schema_version` table + ordered SQL) vs a small
  dependency — prefer hand-rolled to keep the zero-setup, stdlib-only promise.
- Whether to keep the numbered content-folder scheme at all.
