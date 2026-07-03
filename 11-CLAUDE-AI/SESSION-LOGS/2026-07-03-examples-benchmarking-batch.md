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

## ✅ Verification
Smoke **7/7**, **76 tests** (was 62). Tree clean apart from `.obsidian/` editor state; drafts +
scorecards live in external `active/`.

## ⏭️ NEXT (continue soon)
1. **Convert the user's PHI-Canto gold-standard HTML into a frontmatter-wrapped `.md` example**
   in `07-Standards/curation-examples/` (user to point at the HTML file), then regenerate the
   index. Clarify `_TEMPLATE.md`/README that the body may be the real PHI-Canto curation and only
   the frontmatter is required.
2. **Format convergence** (design question): phiweaver drafts use the template body shape while
   gold standards use PHI-Canto's — converge them (toward PHI-Canto's structure) so retrieval /
   benchmarking compare like-for-like.
3. Optional: UniProt mapping for Zhang from the genome IDs; read Zhang supplementary S1–S7.

---

*Human-in-the-loop drafting workflow; no curation content auto-committed. See
`docs/DESIGN-DECISIONS.md` (D10 examples, D12 benchmarking).*
