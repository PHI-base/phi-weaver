---
created: 2026-06-10
session_id: 2026-06-10-phi-weaver-sync-restructure
project: PHI-Weaver Sync, Restructure & Rebrand
type: infrastructure
tags: [git-workflow, repository, restructure, sqlite, codespaces, rebrand]
duration: ~1 session
participants: [Claude Fable 5, martin2urban]
---

# Session Log: PHI-Weaver Sync, Restructure & Rebrand

**Date**: 2026-06-10
**Project**: PHI-Weaver (formerly PHI-Curation-Framework)
**Session Type**: Infrastructure, cleanup & rebranding
**Primary Goal**: Sync with the renamed/moved GitHub remote, then clean up and modernise the repository structure

## 🎯 Session Objectives

1. Pull colleague's GitHub changes safely over a month-old, churned working tree
2. Stop recurring CRLF line-ending churn
3. Repoint the remote after the repo was renamed/moved to the PHI-base org
4. Fix the broken hardcoded storage paths and make the pipeline portable (incl. Codespaces)
5. Clean up structural inconsistencies and stale artifacts
6. Remove MySQL leftovers (SQLite-only system) and rename the misnamed folder
7. Rebrand the project to PHI-Weaver

## ✅ Tasks Completed

### 1. Repository sync
- Pulled 9 commits from `origin/main` over 96 local uncommitted changes (mostly CRLF churn — 93 files, only ~20 real inserted lines)
- Committed a pre-pull snapshot so nothing was lost, then resolved 7 modify/delete conflicts by honoring the remote's deletions (legacy MySQL files + stale `00-Inbox/` notes)
- Added `.gitattributes` (`* text=auto eol=lf`, binary protections) and renormalized — stops the phantom line-ending diffs on every pull

### 2. Remote rename → PHI-base org
- Repo was renamed/moved from `martin2urban/PHI-Curation-Framework` to **`PHI-base/phi-weaver`**
- Repointed `origin` by editing `.git/config` directly (the `z:` Windows mount blocks `git config`'s lock-file chmod — documented in memory)
- Updated the Git policy in `CLAUDE.md`: from "local-only, never push" to **push allowed** (it's now a shared org repo)

### 3. Storage portability + Codespaces support
- `curation_pipeline.py` was hardcoded to the wrong vault (`/mnt/z/OBS-PHI-Canto`); now **auto-detects the repo root** from `__file__`
- Storage root resolution: `PHI_LITERATURE_ROOT` env override → Codespaces in-workspace default (`PHI_CURATION_ENV=codespace`) → sibling `PHI-Canto-Literature/`
- Added `ensure_storage()` so input/output folders are created on a fresh checkout
- Fixed misleading status messages that printed stale folder names
- New colleague docs: `STORAGE-CONFIGURATION.md` and `DEMO-CODESPACES.md` (zero-setup Codespaces curation walkthrough), linked from README

### 4. Structure cleanup (Batch A)
- Deleted empty `Untitled.md` files (root + `04-Literature/`)
- Fixed `CLAUDE.md` directory docs: replaced the nonexistent `08-QA/` with the real `07-Wiki/`
- Archived the pre-launch `GITHUB-REPOSITORY-PLAN.md` to `archive/` with a historical banner

### 5. MySQL removal + folder rename (Batch B)
- Deleted MySQL-specific files (`install-mysql.sh`, `01-database-schema.sql`, `02-sample-data.sql`)
- Rewrote the DB README around the actual SQLite tooling; fixed misleading "install MySQL" lines
- Renamed `11-CLAUDE-AI/mysql-setup/` → **`11-CLAUDE-AI/db/`** and updated all active references (pipeline `sys.path`, `quick_demo.sh`, `CLAUDE.md`, `README.md`, `AUTOMATION-GUIDE.md`, `07-Wiki/` docs, `.gitignore`); verified `HAS_DB = True` and a `db/` script runs
- `phi_canto_tracking.db` stopped being tracked (matches `.gitignore` intent; recreated by `phi_canto_sqlite.py`)

### 6. Content relocation + README pass + docs/ move (Batch C)
- Moved the FgKnr4 practice curation (`.md` + 256K PDF, PMID 39787257) out of the repo to external `completed/`; fixed the migration stub's "need to identify location" placeholder
- README accuracy pass: real folder diagram, clone/Issues URLs → `PHI-base/phi-weaver`, removed bogus `--init` flag, fixed a broken schema-file link
- Moved `STORAGE-CONFIGURATION.md`, `DEMO-CODESPACES.md`, `PDF-CONVERTER-USAGE.md` into `docs/` (root now just `README.md` + `CLAUDE.md`)

### 7. Rebrand to PHI-Weaver
- README title/prose → PHI-Weaver
- `.devcontainer/` display names → PHI-Weaver, repo refs → `PHI-base/phi-weaver`, and **fixed broken `/workspaces/PHI-Curation-Framework/` paths → `/workspaces/phi-weaver/`** (a real Codespaces bug)
- `docs/STORAGE-CONFIGURATION.md` diagram now shows `phi-weaver/`
- SESSION-LOGS and DEVELOPMENT-TIMELINE left unchanged (historical record)

## 📝 Key Decisions

- **Local folder not renamed**: stays `/mnt/z/PHI-Curation-Framework`; a future fresh clone will create a `phi-weaver/` folder automatically. The pipeline auto-detects its root, so the folder name doesn't affect functionality.
- **Historical records preserved**: session logs + timeline keep the old name; rewriting them would falsify history (one documents the original naming decision).
- **DB untracking**: aligning with the existing `.gitignore` intent improves privacy on a now-public org repo.

## 💡 Insights / Gotchas

- `z:` Windows mount blocks `git config` lock-file chmod → edit `.git/config` directly; `sed -i` works but warns harmlessly.
- The DB integration import bug was already fixed by the pulled commits.

## 🔜 Recommendations for Future Sessions

- **Deeper biocuration improvements** (from the structure analysis): ontology-ID validation (PHIPO/GO/UniProtKB), real completion metrics into the tracking DB, a smoke test.
- **Optional**: split the 53-file `11-CLAUDE-AI/` (touches timeline-script paths — do as its own tested effort).
- **Optional**: re-clone as `phi-weaver/` for cosmetic folder-name consistency.

## Commits (origin `8db78e3` → `c622ea1`)

Pre-pull snapshot · merge · `.gitattributes` · Git policy update · storage portability + Codespaces · Batch A cleanup · MySQL removal · `mysql-setup`→`db` rename · README accuracy pass · Batch C relocation · `docs/` move + README rebrand · full PHI-Weaver rebrand

---

*Session focused on infrastructure and repository hygiene; no curation content was annotated.*
