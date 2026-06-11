---
created: 2026-06-11
session_id: 2026-06-11-modularity-p6-p7
project: Modularity P6 + P7
type: refactor
tags: [modularity, skills, refactor, planning]
duration: ~1 session
participants: [Claude Fable 5, martin2urban]
---

# Session Log: Modularity Plan — P6 (+ P7 start)

**Date**: 2026-06-11
**Project**: PHI-Weaver — modularity refactor (see `docs/MODULARITY-PLAN.md`)
**Session Type**: Refactor (quick wins)
**Primary Goal**: Execute the two safe quick wins from the modularity plan — P6 (skill→tool
linkage) and P7 (content-folder taxonomy).

## ✅ Done — P6: skill → backing-tool linkage

Made every backed skill name its tool explicitly (previously prose-only / missing):

- **`skills/uniprot-lookup/SKILL.md`** — workflow step 2 now names the backing script
  `python3 scripts/query_uniprot.py --gene <NAME> --organism <TAXID>` (the gap the
  2026-06-11 assessment flagged: it never referenced `query_uniprot.py`), noting the
  reviewed-first / `ambiguous` / provenance behaviour.
- **`skills/paper-triage/SKILL.md`** — step 1's vague "PDF-convert tooling" is now the
  concrete commands (`curation_pipeline.py process-pdf` / `pdf-convert.py`) + a pointer to
  `docs/PDF-CONVERTER-USAGE.md`.
- `curation-qc` and `phipo-mapping` already referenced their scripts (from the
  2026-06-11 tooling session) — left as-is.

Result: all four skills now point at their backing tooling. (Changes uncommitted at log
time: `skills/uniprot-lookup/SKILL.md`, `skills/paper-triage/SKILL.md`.)

## ⏸️ Paused — P7: content-folder taxonomy

P7 = resolve the duplicate `07-` prefix (`07-Standards` + `07-Wiki`) and decide
numbered-pipeline vs semantic names. Began assessing the **rename blast radius** (how many
docs/scripts/notes reference each numbered folder, and whether the Obsidian CLI is needed
to keep WikiLinks intact) — **paused at user request before any rename**.

Renaming content-vault folders is riskier than P6: it touches WikiLinks across notes and
references in docs/config, and per `CLAUDE.md` should ideally go through the Obsidian CLI
with the vault active. To resume, first complete the reference scan, then pick the minimal
fix (e.g. `07-Wiki` → free number to break the collision) vs a fuller renumber/semantic
rename.

## 🔜 Next

- Decide P7 direction and execute (with WikiLink safety), or defer.
- Commit P6 (two skill edits) when ready.
- Remaining modularity phases: P1 (package + `pyproject.toml`), P2 (module contract),
  P3 (test relocation), P4 (split `11-CLAUDE-AI/`), P5 (DB migrations).

---

*Quick-win refactor session; P6 complete, P7 paused pre-rename. No curation content changed.*
