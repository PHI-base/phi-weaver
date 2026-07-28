---
created: 2026-06-11
session_id: 2026-06-11-modularity-p4-p7
project: Modularity P4 + P7
type: refactor
tags: [modularity, refactor, pdf, folders, cleanup]
duration: ~1 session
participants: [Claude Fable 5, martin2urban]
---

# Session Log: Modularity P4 (split 11-CLAUDE-AI/) + P7 (folder taxonomy)

## Recap

P4: moved the PDF converter into `phiweaver/pdf/` (shim at old path), dropped the stray JSON, added `11-CLAUDE-AI/README.md` (operational role); obsidian_reorganise + timeline generators kept as vault-operational. P7: renamed `07-Wiki`→`08-Wiki` (broke the duplicate `07-` prefix) + updated refs. All modularity phases P1–P7 now done.


**Date**: 2026-06-11
**Project**: PHI-Weaver — modularity refactor (see `docs/MODULARITY-PLAN.md`)
**Session Type**: Refactor (behaviour-preserving) — the final two phases.

## ✅ P4 — split `11-CLAUDE-AI/`

- **Moved the PDF-conversion engine** into the package: `pdf-convert.py` → `phiweaver/pdf/pdf_convert.py`,
  plus `enhanced_caption_extractor.py`, `pdf-convert-config.json`, `PDF-CONVERT-SKILL.md`,
  and a `phiweaver/pdf/__init__.py`. Fixed the lazy caption-extractor import to
  `phiweaver.pdf.enhanced_caption_extractor`. Left a **shim** at
  `11-CLAUDE-AI/pdf-convert-skill/pdf-convert.py`, so `convert-pdf.sh`,
  `convert-for-curation.py`, and the pipeline keep working unchanged.
- **Dropped** the stray `11-CLAUDE-AI/Chen-2020-…_converted_report.json`.
- Added **`11-CLAUDE-AI/README.md`** documenting the folder's now-operational role (session
  logs, dev timeline + generators, operational guides, compat shims) vs the `phiweaver/`
  engine.
- **Scoping decision** (recorded): `obsidian_reorganise.py` + the timeline generators stay
  in `11-CLAUDE-AI/` as **vault-operational** tooling tied to this vault's layout/session
  logs — they're not curation engine. The curation engine (lookup/tracking/pipeline/**pdf**)
  is now all under `phiweaver/`.
- Verified: `python3 -m phiweaver.pdf.pdf_convert --help` and the shim path both run (fitz
  available locally); smoke 7/7; 48 tests green.

## ✅ P7 — content-folder taxonomy

- Renamed **`07-Wiki` → `08-Wiki`** to break the duplicate `07-` prefix (was `07-Standards`
  + `07-Wiki`). `08` was free.
- Updated **all path references** (`07-Wiki` → `08-Wiki`) across code/docs/config and the
  folder's own contents: `phiweaver/tracking/generate_article_registry.py` (writes to
  `08-Wiki/Article-Registry.md`), `content-links/literature-index.md`, `README.md`,
  `docs/OVERVIEW.md`, and the notes inside the folder. **Session logs left untouched**
  (historical record). Obsidian resolves `[[links]]` by basename, and no inbound links used
  the path, so no links broke.
- A fuller semantic renumbering was judged low-value and **deferred**.

## 📝 Docs refreshed
- `docs/OVERVIEW.md` brought current (package layout, `phiweaver.smoke` 7 checks / 48 tests,
  modularity phases marked complete).
- `docs/MODULARITY-PLAN.md`: P4 + P7 marked done; gap #7 noted resolved.
- `docs/PDF-CONVERTER-USAGE.md`, `skills/paper-triage/SKILL.md` point to
  `python3 -m phiweaver.pdf.pdf_convert` (shim still works).

## ✅ Verification
- Smoke **7/7**, **48 tests**, registry `--check` clean, PDF converter runs via module +
  shim. No data touched (the tracking DB and `08-Wiki/Article-Registry.md` left as-is).

## 🎉 Plan status
**All modularity phases (P1–P7) are now complete.** `docs/MODULARITY-PLAN.md` is fully
checked off. Remaining future work is capability-level (interaction parsing, entity
recognition, direct PHI-Canto submission), not structural.

---

*Behaviour-preserving cleanup; no curation content changed.*
