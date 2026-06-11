---
created: 2026-06-11
session_id: 2026-06-11-modularity-assessment
project: Modularity Assessment
type: architecture
tags: [architecture, modularity, refactor, planning]
duration: ~1 session
participants: [Claude Fable 5, martin2urban]
---

# Session Log: Modularity Assessment

**Date**: 2026-06-11
**Project**: PHI-Weaver — architecture
**Session Type**: Evaluation / planning (no code changes)
**Primary Goal**: Evaluate how modular the vault is — can parts be updated/tested
independently, and can future specialised curation modules be plugged in — and capture a
plan.

## ✅ What was done

- Mapped both layers: the **content vault** (numbered Obsidian folders + external
  literature storage) and the **tooling engine** (`scripts/`, `skills/`, `11-CLAUDE-AI/`,
  `docs/`, `AGENTS.md`).
- Inspected the real coupling: `sys.path` glue at 4+ sites, tests in `scripts/tests/`
  reaching into `11-CLAUDE-AI/db/`, prose-only (and inconsistent) skill→script links,
  DB schema/queries/printing bundled in one class with no migrations.
- Wrote the assessment + a phased migration plan to **`docs/MODULARITY-PLAN.md`**.
- **User decision**: capture as a plan doc, do **not** change code yet.

## 📋 Findings (summary)

**Already modular:** the `scripts/` pattern (deterministic, injected I/O, provenance
envelope, offline tests); tool-agnostic `skills/`; externalised overridable storage; a
test + smoke-test foundation.

**Gaps:** `11-CLAUDE-AI/` is a grab-bag of unrelated concerns under a vendor-specific name;
no importable package / `pyproject.toml` (sys.path hacks instead); tests not co-located;
skill→tool links prose-only with `uniprot-lookup` missing its `query_uniprot.py` reference;
the DB layer has no migration path and mixes data access with printing.

## 🗺️ Plan (in `docs/MODULARITY-PLAN.md`)

Make "module = skill + deterministic script + tests + provenance envelope" an explicit,
enforced contract on top of a real `phiweaver/` package. Seven phases, one PR each, all
behaviour-preserving and gated by the smoke test:

- P1 package + `pyproject.toml` (kills sys.path hacks) · P2 module contract + skill
  frontmatter + generated registry · P3 co-locate tests under one root · P4 split
  `11-CLAUDE-AI/` (engine vs agent-operational) · P5 extensible DB (schema + migrations +
  repository + CLI) · P6 fix `uniprot-lookup`→script linkage · P7 tidy content-folder
  numbering (double `07-`).
- P1–P3 give most of the "update/test parts independently" benefit; P4–P5 unlock new
  specialised modules; P6–P7 are safe quick wins that can land anytime.

## 🔜 Next

- Awaiting go-ahead on a phase. Suggested first: **P6 + P7** (quick wins) or **P1** (the
  foundational package change).

---

*Assessment + planning only; no code or curation content changed.*
