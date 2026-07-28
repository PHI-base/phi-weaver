---
created: 2026-07-03
session_id: 2026-07-03-examples-benchmarking-batch
project: Curation examples + benchmarking + batch drafting
type: feature (drafting/review workflow)
tags: [curation-examples, benchmarking, scorecard, batch, flags, phipo, drafting]
duration: ~1 session
participants: [Claude Fable 5, martin2urban]
---

# Session Log: curation-example library, benchmarking scorecard, batch drafting

## Recap

8 commits: validated curation-example library (`curation_examples.py`, flat + tags, draft→validated, retrieval-not-training); `docs/DESIGN-DECISIONS.md` (D1–D12) + refreshed OVERVIEW; benchmarking Excel scorecard (rubric + scoring + completeness; phiweaver pre-checks objective column, human scores, must not self-score) + `make_scorecard.py`; `fill_scorecard.py` prefill from a draft's `auto_check` block; structured `triage`+`flags` in drafts + `batch_summary.py` review dashboard. Drafted Zhang-2024 (Pi05910/StGOX4, full-Results read) + triaged Miltenburg (scope). Later: imported the **first validated gold-standard example** (PMID:26177154 Fol/I-7 gene-for-gene) from a PHI-Canto PDF; found the **PHIDO validation gap**; added `docs/BACKLOG.md`; built the **gold-standard-import skill** (7 skills). Smoke 7/7, 76 tests. **NEXT: fix PHIDO gap; generate ~8–12 gold-standard examples; format convergence.**


**Date**: 2026-07-03
**Project**: PHI-Weaver — the human-in-the-loop drafting → review → example loop.
**Session Type**: Feature. 8 commits, all merged to `main` and pushed; green throughout.

## ✅ Shipped (8 commits on `main`)
1. **`7152383` curation-example library** — `07-Standards/curation-examples/`: `_TEMPLATE.md`,
   `TAGS.md` (controlled vocab), generated `INDEX.md`, and `phiweaver/curation_examples.py`
   (+7 tests). **Flat folder + multi-value tags** (not per-class subfolders — examples are
   multi-class); browse-by-topic via the generated index; **draft → validated** gate; it's
   **retrieval, not model training**.
2. **`e187c55` `docs/DESIGN-DECISIONS.md`** — the "why" record (D1–D12) + system snapshot.
3. **`0cbdd55`** — refreshed `docs/OVERVIEW.md` (6 skills, 76 tests now, example library).
4. **`1e1eef8` + `f591ece` benchmarking scorecard** — `07-Standards/curation-benchmarking/`:
   an Excel scorecard (Guide / per-paper Scorecard / Summary) with a rubric, a scoring rule,
   and a **completeness (recall)** dimension; `make_scorecard.py` (openpyxl); README. **phiweaver
   pre-checks the objective column, a human scores the judgement; phiweaver must NOT grade its
   own drafts** (circular). `.xlsx` tracked via a gitignore negation.
5. **`6156d8e` scorecard prefill** — `fill_scorecard.py` reads a draft's machine-readable
   `auto_check` block and pre-fills the scorecard header + auto-check column (single or batch),
   leaving reviewer ratings blank. Fails gracefully if the `.xlsx` is open in Excel.
6. **`ebdf133`** — DESIGN-DECISIONS D11 updated (structured-record first slice landed) + D12
   (benchmarking scorecard).
7. **`5bb7b53` structured flags + batch summary** — drafts carry `triage` + `flags`
   (category/detail) in their json block instead of asking questions mid-run;
   `phiweaver/batch_summary.py` (stdlib, +tests) rolls a batch into one review dashboard
   (papers most-in-need-first, auto-check signal, flags grouped by category) + CSV.

## 🧪 Batch drafting (real papers, external `active/` — NOT committed)
- Surveyed `active/`; most papers already curated. **Le-2025/Pt31812 already curated**
  (`completed/Li-2025-Pt31812`) → skipped. Genuinely uncurated: Zhang 2024, Miltenburg 2022.
- **Zhang 2024** (`Zhang-2024-Pi05910-phiweaver-DRAFT.md`) — *P. infestans* RXLR effector
  **Pi05910** binds/inhibits/destabilises host glycolate oxidase **StGOX4** (avirulence on potato
  Longshu 12). Drafted with real tool calls (UniProt not_found → flagged, not invented; PHIPO
  terms mapped + validated), then **reviewed with a full main-text Results read**: added the NES
  variant (nuclear localisation required → loss of virulence), resolved the R-gene (**none
  identified**), pulled genome accessions (StGOX4 PGSC…, NbGOX4 Niben…), host phenotypes
  (StGOX4 OE = resistance, NbGOX4 VIGS = susceptibility) that **have no clean PHIPO match**.
  A prefilled scorecard + a batch-summary dashboard were generated from it.
- **Miltenburg 2022** — BioID interactome; triaged **scope_uncertain** (the physical-interaction
  scope question), not drafted.

## 🗂️ Key decisions / clarifications
- **Batch fails safe**: never-guess ⇒ unresolved items become **flags**, never fabricated data;
  the scorecard **completeness** column measures the omissions. Mid-run questions → flags handled
  at review, not answered during drafting.
- **Gold-standard examples**: keep the **PHI-Canto content** (HTML/converted), just add the
  curation-example **frontmatter** wrapper — the library only needs the frontmatter; do NOT
  retype into the template body.

## ✅ Gold-standard example + import tooling (later in session)
- **First validated gold-standard example**: PMID:26177154 (*F. oxysporum* AVR effectors × tomato
  *I-7*, gene-for-gene), imported from PHI-Canto session 077ec02bbb46ec45 (curator Hsin-Yu Chang).
  Saved as PDF → text via `fitz` → structured → **wrapped in curation-example frontmatter keeping
  PHI-Canto's structure** (`status: validated`) → index regenerated. Library = 1 validated
  example. (`8f186cf`) The read-only Canto URL couldn't be fetched (annotations load via JS).
- **PHIDO validation gap found**: `validate_ontology_ids` lists PHIDO but OLS4 doesn't host it, so
  PHIDO:0000164 falsely returns `not_found`. Logged.
- **`docs/BACKLOG.md`** created as the durable to-do (harness task tools are session-scoped):
  PHIDO gap, format convergence, physical-interaction scope. (`e9c5a43`)
- **`gold-standard-import` skill** built (registry now 7 skills) — names the PHI-Canto-export →
  validated-example workflow (extract, validate IDs, wrap frontmatter, register). (`92ba5b2`)
- Guidance given: target **~8–12 gold-standard examples**, one per canonical case type,
  benchmark-driven growth (coverage, not volume; quality > quantity).

## ✅ Verification
Smoke **7/7**, **76 tests**, **7 skills**, **1 validated example**. Tree clean apart from
`.obsidian/` editor state; drafts + scorecards + source PDFs live in external `active/`.

## ⏭️ NEXT
1. **Fix the PHIDO validation gap** (mark PHIDO format-checked-only, like UniProtKB) — `docs/BACKLOG.md`.
2. **Generate ~8–12 gold-standard examples** across canonical case types (start with
   gene-deletion→virulence, effector, overexpression, host resistance); grow benchmark-driven.
3. **Format convergence** — align phiweaver's draft shape with PHI-Canto's so drafts and gold
   standards compare like-for-like.
4. Decide the **physical-interaction scope**; optional Zhang UniProt mapping + supplementary read.

---

*Human-in-the-loop drafting + gold-standard-import workflow; per-paper work products stay in
external `active/`. See `docs/DESIGN-DECISIONS.md`, `docs/BACKLOG.md`.*
