---
created: 2026-06-11
session_id: 2026-06-11-ontology-id-validation
project: Ontology-ID Validation Tool
type: automation
tags: [scripts, biocuration, ontology, qc, phipo, testing]
duration: ~1 session
participants: [Claude Fable 5, martin2urban]
---

# Session Log: Ontology-ID Validation Tool

**Date**: 2026-06-11
**Project**: PHI-Weaver — biocuration tooling
**Session Type**: Automation / quality tooling
**Primary Goal**: Pick up a recommended biocuration improvement from the 2026-06-10 session — **ontology-ID validation (PHIPO/GO/UniProtKB)**

## 🎯 Session Objectives

1. Carry Claude memories across the `PHI-Curation-Framework` → `phi-weaver` path move and clean up the stale old project dir (housekeeping)
2. Implement ontology-ID validation as a deterministic, testable `scripts/` helper, matching the existing `query_uniprot.py` pattern
3. Wire it into the skills that require term verification

## ✅ Tasks Completed

### 1. Memory migration housekeeping
- Copied the three memory files into `~/.claude/projects/-mnt-z-phi-weaver/memory/` using **content copy** (`cp -r SRC/. DST/`) — the originally-suggested `cp -r SRC/memory DST/memory` would have nested into `memory/memory/` because the new session had already created the dir.
- Updated two memories whose facts were now stale: local working dir is now `/mnt/z/phi-weaver` (was `/mnt/z/PHI-Curation-Framework`) in `wsl-git-config-chmod.md` and `repo-renamed-phi-weaver.md`.
- Deleted the obsolete `~/.claude/projects/-mnt-z-PHI-Curation-Framework/` dir (old memory copy + session transcripts) at the user's request.

### 2. New tool: `scripts/validate_ontology_ids.py`
Deterministic validator for the IDs a curation depends on, in two stages:
- **Format (offline, always):** anchored regex per prefix — `GO`/`PHIPO`/`PHIDO` = 7-digit; UniProtKB = the canonical accession regex (with optional `-N` isoform).
- **Existence / obsolescence (online, OBO only):** EBI **Ontology Lookup Service** (`ols4/api/terms?obo_id=…&ontology=…`); reads `is_obsolete` + `label`.
- UniProtKB is **format-checked only** (existence is `query_uniprot.py`'s job) → status `format_checked_only`.
- Mirrors `query_uniprot.py` exactly: injectable `http_get`, lazy `requests`, tiny SQLite cache, UTC-stamped provenance, `0/1` exit codes.
- **Never guesses:** bad format is reported not "corrected"; a term OLS doesn't return is `not_found`; **obsolete = fail** (skills require non-obsolete terms).
- CLI extras: `--file` extracts + validates every ID in a draft curation; `--format-only` (offline); `--json`; `--no-cache` / `--cache`.

### 3. Tests — `scripts/tests/test_validate_ontology_ids.py`
- 16 new network-free tests (injected HTTP getter): ID formats, exists/obsolete/not-found, format-invalid + unknown-prefix short-circuit **without** touching the network, UniProt format-checked-only, offline mode, HTTP error, wrong-term-returned, cache-hit, free-text extraction.
- Full suite: **25 tests pass** (16 new + 9 existing UniProt).

### 4. Live verification (the bit tests can't cover)
- Confirmed all four OLS paths against the real service: `exists` (GO:0008150, PHIPO:0000001), `obsolete` (GO:0009405 "pathogenesis" — actually obsolete in current GO), `not_found` (GO:0000000), `format_invalid`.

### 5. Wiring + hygiene
- Documented the tool in `scripts/README.md`.
- Referenced it from `skills/curation-qc/SKILL.md` (step 2, `--file` whole-draft check) and `skills/phipo-mapping/SKILL.md` (step 4, per-term check).
- Fixed a latent gap: `scripts/.cache/` was **not** actually gitignored (the UniProt README claimed it was) — added it; both caches now ignored.

### 6. New tool: `scripts/smoke_test.py` (fresh-checkout sanity check)
- One command to answer "I just cloned this — does the tooling work here?". **Network-free, zero pip installs** (optional deps are only for live lookups / PDF conversion).
- Six checks: repo layout · all core modules import with **stdlib only** · pipeline auto-detects repo root + bootstraps `active/completed/media` storage (via a temp `PHI_LITERATURE_ROOT`) · fresh SQLite tracking DB creates schema + accepts a row · offline scripts behave · the unit-test suite passes. Exit `0/1`; `--quiet` for summary only.
- Verified both directions: all green on a normal run **and** with `requests`/PyMuPDF blocked (simulated bare checkout); confirmed a forced check failure exits `1`.
- Wired into docs: `scripts/README.md` section + a "1b. Verify the checkout" step in `docs/DEMO-CODESPACES.md`.
- Fixed a latent gap: `requirements.txt` listed only PyMuPDF though the UniProt README told users `pip install -r requirements.txt` brings in `requests` — added `requests>=2.28` with comments on what each dep is actually for.

### 7. Real completion metrics in the tracking DB
- **Problem:** `complete_paper_workflow` logged a session with hardcoded `proteins=0, interactions=0`, never linked it to the article, and never flipped the article to `curated` — so "completion metrics" were fake zeros.
- **DB primitive:** `PHICantoSQLite.record_completion()` — in one transaction, finds the article (pmid → note_path → title, creating a minimal row if none exists), flips it to `curated`, and inserts a **article-linked** (`article_id`) `curation_sessions` row with the real counts. Plus `get_completion_metrics()` aggregating per curated article.
- **Content-derived metrics:** `curation_pipeline.derive_completion_metrics()` counts the identifiers actually present in the curation notes — distinct UniProtKB accessions, fungal locus tags (`FGSG_…`), and ontology terms — reusing `validate_ontology_ids.extract_ids` so it stays consistent with the QC tool. Explicit CLI counts win; otherwise these fill in.
- **Wiring:** `complete-paper` now takes optional `[proteins] [interactions] [experiments] [hours]`, writes to the **canonical DB path** (`11-CLAUDE-AI/db/phi_canto_tracking.db`, anchored regardless of CWD), and prints what it recorded. New `daily_curation.py completed` report.
- **Verified end-to-end** against a temp storage root + temp DB (1 accession + 2 locus tags → 3 proteins, 2 ontology terms → article created + curated + linked session) and against the real DB (`completed` shows the existing curated FgTPP1 article's metrics). Fixed the Python 3.12 date-adapter deprecation by storing ISO date strings.
- 6 new tests (article create/update/match-by-note-path, report aggregation + status filter, deriver counting + missing-file). Full suite **31 passing**.

## 📝 Key Decisions

- **OLS over per-ontology APIs**: one REST service resolves PHIPO/GO/PHIDO uniformly and exposes `is_obsolete` directly. UniProt existence intentionally left to `query_uniprot.py` rather than duplicated.
- **`not_checked` passes**: in `--format-only` mode a valid-syntax OBO ID returns exit 0 (the user opted out of the online check); only positive problems (format-invalid / not-found / obsolete / unknown-prefix / error) fail.
- **Obsolete = hard fail**, carrying the term label so a curator can find a replacement.

## 💡 Insights / Gotchas

- GO:0009405 ("pathogenesis"), used in the DB sample data and a natural test term, is now **obsolete** in GO — the validator flagged it immediately, which is exactly the class of error this tool exists to catch.
- The `cp -r SRC/memory DST/memory` nesting trap: when the destination dir already exists, copy the *contents* (`SRC/.`), not the folder.

## 🔜 Recommendations for Future Sessions

- **All three deeper-biocuration items from 2026-06-10 are now done** (ontology-ID validation §2, smoke test §6, completion metrics §7).
- Consider having `curation-qc` shell out to `validate_ontology_ids.py --file` automatically as part of its report generation.
- The interactions count still can't be reliably content-derived (needs explicit entry) — a future improvement could parse interaction statements.
- ~~Run `smoke_test.py` from the devcontainer `postCreateCommand`~~ — **done**: added as the final, non-blocking (`|| echo`) `postCreateCommand` step in `.devcontainer/devcontainer.json`, so a Codespace self-verifies on build.
- Optional: split the large `11-CLAUDE-AI/` folder (touches timeline-script paths — do as its own tested effort).

## Files

- New: `scripts/validate_ontology_ids.py`, `scripts/tests/test_validate_ontology_ids.py`, `scripts/smoke_test.py`, `scripts/tests/test_completion_metrics.py`
- Edited: `scripts/README.md`, `skills/curation-qc/SKILL.md`, `skills/phipo-mapping/SKILL.md`, `.gitignore`, `requirements.txt`, `docs/DEMO-CODESPACES.md`, `.devcontainer/devcontainer.json`, `11-CLAUDE-AI/curation_pipeline.py`, `11-CLAUDE-AI/db/phi_canto_sqlite.py`, `11-CLAUDE-AI/db/daily_curation.py`, `11-CLAUDE-AI/AUTOMATION-GUIDE.md`, `11-CLAUDE-AI/db/README.md`

---

*Additive tooling session; no curation content was annotated. Not yet committed at log time.*
