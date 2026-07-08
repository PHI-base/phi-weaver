---
created: 2026-07-07
session_id: 2026-07-07-gene-for-gene-and-entry-queue
project: Gene-for-gene curation skill + PHI-Canto entry-queue (Route 1, Phase 4) + accession resolution
type: engine + docs + content
tags: [phi-canto, gene-for-gene, entry-queue, worksheet, skill, schema, benchmarking, fable5, opus48]
duration: ~1 session (spans 2026-07-07 → 2026-07-08)
participants: [Claude Opus 4.8, martin2urban]
---

# Session Log: gene-for-gene skill + PHI-Canto entry-queue + Phase 4 completion

**Date**: 2026-07-07 → 2026-07-08
**Project**: PHI-Weaver — finish Phase 4 (canto blocks + worksheets for all 10 benchmark drafts),
add a curator-authored **gene-for-gene** skill, build a concise **entry-queue** output for
PHI-Canto, and start resolving the accession blockers.
**Session Type**: engine + docs (4 commits on `main`, pushed) + substantial external `active/`
content work (uncommitted by unpublished-curation policy).

## ✅ Shipped — repo (commits on `main`, pushed to origin)

### `d12d7bc` — gene-for-gene curation skill + curator methodology reference
Incorporated a biocurator methodology doc (H-Y Chang) as a **dedicated skill**
`skills/gene-for-gene/` (guard/decoy vs direct recognition; mandatory `effector-mediated` GO for
*bona fide* effectors only — explicit non-effector boundary; R-gene presence/absence + delivery
extensions; WT/mutant/complement comparative set; inverse gene-for-gene/NETS). Reference doc →
`06-Training/Gene-for-Gene-Curation-Methodology.md`. The cross-cutting **controlled genotype-label
vocabulary** went into `genotype-creation` (its natural home, not siloed); `phenotype-annotation`
cross-links to the new skill. REGISTRY → 10 skills.

### `1caeeda` — DESIGN-DECISIONS D13
Recorded the "why": curator methodology as a registry-enforced skill; concern-split; and that
applying it caught a real error (see avrPto revision below), validating biocurator-entry-is-validation.

### `1c0e50e` — canto-entry-queue: concise deterministic PHI-Canto click-list
New skill + module `phiweaver/canto/entry_queue.py`: renders a draft's `canto` block into a
table-driven **entry queue** (setup A–E, annotations F1–F5, parked G, summary counts) — the
practical format for live transcription, alongside the fuller worksheet. Chosen (with the user) as
a **deterministic reformat**, not a runtime LLM prompt, so it can never invent an accession/term.
**Safety filter (core rule):** a gene with no accession is *held* and the hold cascades to its
alleles/genotypes/metagenotypes/annotations — all parked. Also parked: dangling references
(referential-integrity check), term-less annotations, interpretive molecular-function claims.
**Schema (optional, backward-compatible):** annotations may carry `hold`/`hold_reason` (explicit
park signal — preferred over prose-sniffing) and `note` (curator caveats kept out of the lean
queue, surfaced in the worksheet); documented in `_TEMPLATE.md`. `--validate` opt-in checks
ontology IDs online (default offline/deterministic); header reads the real frontmatter status.
REGISTRY → 11 skills; smoke 7/7, 128 tests.

### This commit — session log + DESIGN-DECISIONS D14
This log (+ INDEX row) and D14 (entry-queue design decision).

## 📁 External `active/` content work (uncommitted by policy)

- **Phase 4 completed (10/10).** Back-filled the `canto` block + generated worksheets for the
  remaining 7 drafts (Rad53, TRAPPIII, CfSec22, Efg1, NsdD, FleQ/GcbB, CgHat1); referential
  integrity verified each. Tracker: `PHASE4-CANTO-WORKSHEET-PROGRESS.md`.
- **avrPto/Pto (PMID:1537802) revised against the gene-for-gene methodology** — the new skill
  caught a genuine error: `bacterial speck` disease-name was on an **artificial multicopy-plasmid
  genotype**; moved it to a new WT parental metagenotype (DC3000 WT × 76S) per §11. Added R-gene
  presence/absence + delivery-mechanism extensions (§8/§7); recognition-model flag (guard = Pto/Prf,
  not curatable from this 1992 paper — §1); optional Pto host-receptor GO flag (§2.3). 6→9 flags.
- **Entry queues generated for all 10 papers**; added an **entry-readiness column** to the tracker
  (3 ready, 4 ready\*, 1 partial, 2 blocked).
- **CgHat1 (PMID:41295150) accession RESOLVED** via `uniprot-lookup` → **A0A8H4CVH4** (same-species
  *C. gloeosporioides* HAT1, TrEMBL; studied EQB43824.1/Cg-14 not in UniProt; L2FYG8 rejected as
  *C. fructicola*; curator BLAST-confirm noted). Unblocked its cascade ⛔ → ⚠ ready\*.
- **Misc**: `PHASE4-COMPLEXITY-RANKING.md` (papers ranked by curation complexity); recovered a
  corrupted `BATCH-PROGRESS.md` table into `BATCH-PROGRESS.xlsx` (deleted the corrupted `.md`).

## 🧪 Green gate
`python3 -m phiweaver.smoke` → 7/7; `python3 -m unittest discover -s tests` → 128 tests OK.
REGISTRY current (11 skills).

## ➡️ How to proceed next
- **Accession blockers remaining**: URA5 (ambiguous single accession — likely next) and FleQ/GcbB
  (bacterial; no UniProt entries for the Pta6605 proteome — hardest).
- Optional: back-fill `hold`/`note` on the interpretive-MF / long-condition annotations so they
  park by explicit signal instead of the heuristic fallback.
- Still open (pre-existing): curator hand-scoring of the 10 benchmark scorecards →
  `scorecards_to_csv` → `benchmark_report`; Canto Route decision (server access → Route 2?).

## Notes
- Model: **Opus 4.8** this session (previous drafting was Fable 5; drafts retain `model: Fable 5`).
- Repo now has two complementary Route-1 outputs per draft: `canto-worksheet` (worked record) and
  `canto-entry-queue` (lean click-list). Both deterministic, both from the same `canto` block.
