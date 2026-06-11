---
created: 2026-06-11
session_id: 2026-06-11-modularity-p1-package
project: Modularity P1 — phiweaver package
type: refactor
tags: [modularity, refactor, package, pyproject, tests]
duration: ~1 session
participants: [Claude Fable 5, martin2urban]
---

# Session Log: Modularity P1 — `phiweaver/` package

**Date**: 2026-06-11
**Project**: PHI-Weaver — modularity refactor (see `docs/MODULARITY-PLAN.md`)
**Session Type**: Foundational refactor (behaviour-preserving)
**Primary Goal**: P1 — stand up an importable `phiweaver/` package and remove the scattered
`sys.path` glue, so parts can be updated/tested independently.

## ✅ Done

### Decision (PEP 668)
Local env is externally-managed, so `pip install -e .` is blocked without a venv/flag.
**User chose "run-from-root, install optional"**: the package is importable by running from
the repo root; `pip install -e .` is provided but nothing depends on it.

### Package
- Created **`phiweaver/`** with subpackages `lookup/`, `tracking/`, `pipeline/`, plus
  `smoke.py` and a package `README.md`.
- `phiweaver/__init__.py` exposes **`repo_root()`** (nearest ancestor with `AGENTS.md`) —
  replaces fragile `parents[N]` indexing in the pipeline + session logger.
- Added **`pyproject.toml`** (install optional; `[live]` extra for requests/PyMuPDF;
  console scripts `phiweaver-uniprot|validate|pipeline|smoke`).

### Moves (git-tracked renames, history preserved)
- `scripts/{query_uniprot,validate_ontology_ids}.py` → `phiweaver/lookup/`
- `11-CLAUDE-AI/curation_pipeline.py` → `phiweaver/pipeline/`
- all 8 `11-CLAUDE-AI/db/*.py` → `phiweaver/tracking/`
- `scripts/smoke_test.py` → `phiweaver/smoke.py`
- `scripts/tests/*` → **`tests/`** (this also completes **P3** — one discovery root)

### Imports + glue removed
- All flat cross-imports (`from phi_canto_sqlite import …` etc.) rewritten to absolute
  `phiweaver.…` imports.
- **Zero `sys.path` hacks remain in the engine or tests.** The only `sys.path` users are
  the compatibility shims (by design).

### Backward compatibility (thin shims)
- 11 shims at the old documented paths (`scripts/…`, `11-CLAUDE-AI/…`,
  `11-CLAUDE-AI/db/…`) that bootstrap the repo root and `runpy.run_module(...)` the package
  module as `__main__`. Old commands and exit codes are preserved.

### Verification
- `python3 -m unittest discover -s tests` → **31 passing**; `python3 -m phiweaver.smoke` →
  **6/6**. Both also pass via the shim paths (`python3 scripts/smoke_test.py`).
- CLI entry points checked via both `-m` and shim forms; exit codes preserved;
  `daily_curation completed` reads the real DB when run from the db dir.

### Docs / config
- `AGENTS.md` (§1, §4) updated to the package + run-from-root model.
- `scripts/README.md` reduced to a shim pointer; new `phiweaver/README.md`.
- `.devcontainer/devcontainer.json`: added optional, non-blocking `pip install -e .`.
- `docs/MODULARITY-PLAN.md`: P1 and P3 marked done.

## 📝 Notes / Gotchas
- `quick_demo.sh` prints `python3 db/…` commands — they resolve to the shims, so still work.
- DB file stays at `11-CLAUDE-AI/db/phi_canto_tracking.db` (gitignored, user data); the
  relative-default-path fragility in `daily_curation`/`session_logger` is unchanged
  (defer to P5).
- Some command examples in `README.md` / `AUTOMATION-GUIDE.md` still show old paths; they
  work via shims. Modernising them to `-m phiweaver.…` can be a later doc pass.

## 🔜 Next
- P2 (module contract + skill frontmatter + registry), P4 (split `11-CLAUDE-AI/`),
  P5 (DB migrations), P7 (folder taxonomy). P6 + P3 already done.

---

*Behaviour-preserving foundational refactor; no curation content changed.*
