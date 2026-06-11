---
created: 2026-06-11
session_id: 2026-06-11-modularity-p2-contract
project: Modularity P2 — module contract
type: refactor
tags: [modularity, refactor, skills, registry, contract, tests]
duration: ~1 session
participants: [Claude Fable 5, martin2urban]
---

# Session Log: Modularity P2 — module contract

**Date**: 2026-06-11
**Project**: PHI-Weaver — modularity refactor (see `docs/MODULARITY-PLAN.md`)
**Session Type**: Refactor (behaviour-preserving) + new tooling
**Primary Goal**: P2 — make "module = skill + deterministic tool + tests + envelope" an
explicit, enforced contract so specialised curation modules plug in by convention.

## ✅ Done

### Shared envelope — `phiweaver/common/`
- New `phiweaver/common/__init__.py`: `utc_now()`, `make_getter(user_agent)` (lazy
  `requests`), `ResponseCache` (SQLite, now with an optional `meta` dict).
- Refactored **both lookup tools** to use it, removing their duplicated `_now` /
  `_requests_get` / `Cache`. Kept `_now`/`_requests_get`/`Cache` module aliases for
  backward compatibility (tests reference `qu.Cache` etc.). Behaviour-preserving — 31
  pre-existing tests still pass.

### Machine-readable skill frontmatter
- Added `backing_script`, `tests`, `inputs`, `outputs` to all 4 skills
  (`uniprot-lookup`, `phipo-mapping`, `curation-qc`, `paper-triage`). `paper-triage` is
  `backing_script: null` (reasoning-only); `curation-qc` lists two backing scripts.

### Registry + enforcement — `phiweaver/registry.py`
- Dependency-free frontmatter parser (scalar / `null` / block-list).
- Generates `skills/REGISTRY.md` (enumerable index: skill, when-to-use, backing tools,
  tests). `--check` validates the contract (required fields present; declared
  backing_script/tests files exist) **and** that REGISTRY.md is current; exit 0/1.
- Wired into the smoke test as a 7th check ("skill contract + registry").

### Docs
- `docs/ADDING-A-MODULE.md` — the new-module checklist (the contract + 6 steps).
- `phiweaver/README.md` — documents `common/` + `registry`; `docs/MODULARITY-PLAN.md` P2
  marked done.

## ✅ Verification
- `python3 -m unittest discover -s tests` → **39 passing** (8 new in `tests/test_registry.py`,
  incl. an integration test guarding that the committed REGISTRY.md stays current + valid).
- `python3 -m phiweaver.smoke` → **7/7** (also via the `scripts/smoke_test.py` shim).
- Negative check confirmed: drifting REGISTRY.md makes `--check` exit 1.

## 📝 Notes
- The contract check is now enforced two ways: the smoke test and `registry --check` (CI-ready).
- `ResponseCache` schema gained a `meta` column; cache files are gitignored/disposable, so
  no migration needed.

## 🔜 Next
- P4 (split `11-CLAUDE-AI/` — engine vs agent-operational), P5 (DB migration layer),
  P7 (folder taxonomy). P1, P2, P3, P6 done.

---

*Behaviour-preserving refactor + contract tooling; no curation content changed.*
