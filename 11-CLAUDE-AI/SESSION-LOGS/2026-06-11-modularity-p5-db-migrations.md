---
created: 2026-06-11
session_id: 2026-06-11-modularity-p5-db-migrations
project: Modularity P5 — DB migrations
type: refactor
tags: [modularity, refactor, database, migrations, repository, tests]
duration: ~1 session
participants: [Claude Fable 5, martin2urban]
---

# Session Log: Modularity P5 — DB migration layer

**Date**: 2026-06-11
**Project**: PHI-Weaver — modularity refactor (see `docs/MODULARITY-PLAN.md`)
**Session Type**: Refactor (behaviour-preserving) + new tooling
**Primary Goal**: P5 — a versioned schema-migration layer so specialised modules can extend
the tracking DB without editing core, plus a data-returning query layer.

## ✅ Done

### Migration runner — `phiweaver/tracking/migrations.py`
- **Namespaced, versioned** runner: each namespace (`core` + any module) has its own
  ordered migration list and its own applied-version counter, recorded in a
  `schema_migrations` table — so module migrations never collide with core's numbering.
- The original schema is now the **`core` v1 baseline** (kept as `CREATE … IF NOT EXISTS`,
  so it is safe to (re)apply on a DB that predates the system).
- `run_migrations(conn, registry=None)` applies all pending per namespace, committing each;
  idempotent. `register_migrations(namespace, migrations)` lets a module add migrations
  **without editing core**.

### Data-returning query layer — `phiweaver/tracking/repository.py`
- Pure functions (`completion_metrics`, `article_status`, `effector_proteins`,
  `curation_progress`) that take a connection and **return rows, no printing** — so the
  query layer is testable without capturing stdout.

### `phi_canto_sqlite.py` refactor (behaviour-preserving)
- `create_schema()` now just calls `migrations.run_migrations()` (idempotent; prints a
  status line; still returns True/False).
- The four `get_*`/`find_*` methods now get their data from `repository` and keep their
  printing. `record_completion` unchanged.

### Tests (+9 → 48 total)
- `tests/test_migrations.py` — baseline applies + version recorded, idempotent rerun,
  **a module adds a migration in its own namespace without touching core**, `register_*`
  updates the global registry, pre-existing DB upgrades and preserves data.
- `tests/test_repository.py` — the data-returning queries, asserted **without stdout capture**.
- `tests/test_completion_metrics.py` — report test now uses `repository.completion_metrics`
  (dropped the `redirect_stdout`).

## ✅ Verification
- `python3 -m unittest discover -s tests` → **48 passing**; smoke **7/7**.
- Confirmed: fresh DB → core v1; rerun applies 0; **pre-existing DB (no `schema_migrations`)
  upgrades to v1 with data preserved**. Real CLIs (`curation_pipeline help`,
  `daily_curation completed` on the real DB) still work via the shims.

### Docs
- `11-CLAUDE-AI/db/README.md` — migrations + repository section.
- `docs/ADDING-A-MODULE.md` — "needs its own DB tables?" → register a namespace.
- `docs/MODULARITY-PLAN.md` — P5 marked done.

## 🔜 Next
- Remaining: **P4** (split `11-CLAUDE-AI/` — engine vs agent-operational) and **P7**
  (folder-taxonomy quick win). P1, P2, P3, P5, P6 done.

---

*Behaviour-preserving refactor + migration tooling; no curation content changed.*
