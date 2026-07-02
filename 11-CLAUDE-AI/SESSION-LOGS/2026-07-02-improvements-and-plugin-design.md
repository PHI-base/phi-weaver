---
created: 2026-07-02
session_id: 2026-07-02-improvements-and-plugin-design
project: Curation-tooling improvements + plug-in design
type: mixed (feature, refactor, cleanup, design)
tags: [modularity, skills, phipo, metrics, cleanup, plugin-architecture, decoupling]
duration: ~1 session
participants: [Claude Fable 5, martin2urban]
---

# Session Log: post-modularity improvements + plug-in architecture design

**Date**: 2026-07-02
**Project**: PHI-Weaver — outstanding-work cleanup, a new curation capability, and the
long-term direction.
**Session Type**: Mixed. Eight commits, each behaviour-preserving and green-gated; all merged
to `main` and pushed.

## 🧭 Assessment + direction (design discussion)
- Reviewed outstanding work and prioritised it (Group A cleanups → real curation value →
  structural tidy → future).
- Long discussion on the long-term aim: PHI-Weaver as a **plug-in host** for
  independently-developed modules (figure/image → phenotype; phenotype → PHIPO), run with a
  **local AI on ROGER** (GPU cluster), with a light portable core on a Linux server / WSL2 /
  Docker. Wrote **`docs/PLUGIN-ARCHITECTURE.md`** (strawman, no code): out-of-process plugins
  over the shared envelope, Apptainer/Docker parity, an inference-backend abstraction, a
  conformance test harness, and a **"start simple"** section (the destination is not the first
  step). Vault deprioritised vs engine portability.
- Saved two memories: `phiweaver-longterm-architecture`, `user-is-domain-scientist`.

## ✅ Shipped (8 commits on `main`)
1. **`0e3fd9f` Group A cleanups** — fixed `MODULARITY-PLAN.md` status/P6 drift; reorganiser
   `vault_path` → `/mnt/z/phi-weaver`; pipeline calls `python3 -m phiweaver.pdf.pdf_convert`
   (with PYTHONPATH) instead of the P4 shim; `08-Wiki/README` + registry generator stale
   commands → `python3 -m phiweaver.tracking.*`.
2. **`e2d1c0a`** — `docs/PLUGIN-ARCHITECTURE.md` design doc.
3. **`158f49c` caption → phenotype → PHIPO module** — new
   `phiweaver/lookup/map_phenotype.py` (searches PHIPO via EBI OLS, real IDs only,
   PHIPO-only filter dropping imported PATO, obsolete excluded, exact-match ranking, full
   envelope) + 12 network-free tests; wired into the `phipo-mapping` skill (caption-first
   workflow); `.gitignore` fixed to ignore `phiweaver/**/.cache/`.
4. **`eb8aff4` tracking-DB path fix** — `PHICantoSQLite` default now resolves to the
   canonical `11-CLAUDE-AI/db/phi_canto_tracking.db` via `repo_root()`, not a cwd-relative
   name. Fixes the registry generator's stray-DB / "no such table" symptom.
5. **`fca4493` reorganiser config** — Obsidian exe `.com` → `.exe`; removed the stale `08-QA`
   rule (the reorganiser can only move within the vault, not to the external companion).
6. **`f28d84a` two new skills** — promoted the task-shaped `06-Training` quick-references to
   reasoning-only skills: `genotype-creation`, `phenotype-annotation` (delegates term
   selection to `phipo-mapping`). Registry now lists **6 skills**; the set covers the whole
   chain: paper-triage → uniprot-lookup → genotype-creation → phenotype-annotation (via
   phipo-mapping) → curation-qc.
7. **`bbb19f9` interaction counts** — `derive_completion_metrics` now counts explicit
   interaction entries under an "Interactions" heading (non-empty, non-placeholder bullets);
   `complete_paper_workflow` uses the derived count instead of hardcoded 0. Deterministic and
   conservative; never inferred from prose.
8. **`3ae84b4` split 11-CLAUDE-AI grab-bag** — moved the loose vault-operational scripts into
   **`11-CLAUDE-AI/vault-ops/`** (timeline generators + Obsidian reorganiser + config; fixed
   their repo-root resolution to `parents[2]`). **Decoupled the engine**: removed the dead
   `self.reorganizer` refs from the pipeline — the engine now reaches into `11-CLAUDE-AI/`
   only for the tracking DB and session logs. Updated all affected guides/READMEs; shims,
   `db/`, `SESSION-LOGS/` stay put; historical logs untouched.

## 🗂️ Decisions (no change)
- **`04-Literature/`** left as-is — it is now just a migration signpost; the live workflow
  uses external storage. Its references elsewhere are stale/sample, not live. (Stale refs
  noted but not cleaned, per user "leave as is".)
- **Vault folder structure** judged acceptable and justifiable *for a human curator's
  workspace* (it should not mirror the code modules; that lives in `phiweaver/` + the skill
  registry). One soft spot noted: curation protocols duplicated across `05-Protocols` and
  `08-Wiki/Curation-Protocols/`. Numbering gaps + the `11-` label are cosmetic, left alone.

## ✅ Verification
- **Smoke 7/7**, **62 unit tests** green (grew from 48: +12 map_phenotype, +2 interaction),
  registry `--check` clean. Live checks: `map_phenotype` against OLS (real PHIPO IDs +
  honest no_match), the map→validate chain, and the moved timeline script resolving
  SESSION-LOGS from any cwd. Branches all merged + pushed + deleted; tree clean apart from
  `.obsidian/workspace.json` (editor state).

## ⏭️ Next
- Deferred future work only: the plug-in host + local-AI-on-ROGER architecture
  (`docs/PLUGIN-ARCHITECTURE.md`) — later, likely with collaborator / research-computing
  help.
- Suggested first real exercise: run the caption → phenotype → PHIPO flow on an actual
  paper's captions.

---

*Behaviour-preserving throughout; no curation content changed.*
