---
created: 2026-07-05
session_id: 2026-07-05-benchmark-drafting-10-papers
project: Benchmark drafting run — 10 curation drafts via isolated sub-agents
type: curation run (+ workflow docs)
tags: [benchmarking, curation, sub-agents, context-isolation, recuration, runbook, fable5]
duration: ~1 session
participants: [Claude Fable 5, martin2urban]
---

# Session Log: benchmark drafting — 10 papers via isolated sub-agents

**Date**: 2026-07-05
**Project**: PHI-Weaver — produce phiweaver curation drafts for a benchmark run, plus design/doc
work (recuration-comparison, benchmark runbook). Drafting done one isolated sub-agent per paper
to prevent cross-paper entity bleed-through.
**Session Type**: Curation run + docs. 4 commits on `main` (NOT yet pushed); 10 drafts in external
`active/` (not committed).

## ✅ Shipped

### Docs/design — 4 commits on `main` (⚠ NOT pushed — `main` is 4 ahead of `origin/main`)
- **`0ed1009` recuration-comparison workflow** → added to `docs/BACKLOG.md` (future goal). Recurate
  biocurator-curated PHI-Canto articles with phiweaver and **diff** the two (neutral, deterministic
  — not self-scoring; human adjudicates only divergences) to compare biocurators vs phiweaver for
  fine-tuning / training. Pieces: `recuration-import` skill, comparison-matrix template,
  `compare_recuration.py`, cross-biocurator aggregation. Two open decisions noted (aggregation home
  = tracking DB vs Excel; gold-standard papers scored vs ordinary papers diffed).
- **`67cb550` benchmark runbook** → `docs/BENCHMARK-RUNBOOK-2026-07-05-test10articles.md`. Step-by-step
  for the 10-paper test: blind/sandboxed drafting via the `benchmark` skill, `fill_scorecard.py`
  prefill, manual scoring, report. **Option 1 chosen: no control split** (small example library →
  low leakage risk; single group).
- **`b280263` runbook model-choice note** — model is part of what the benchmark measures: use ONE
  model for all papers, benchmark the model you'll actually curate with, record it. Fable 5 for the
  ceiling; optional Opus/Sonnet second pass as an accuracy-vs-cost axis.
- **`7959dec` runbook isolation note** — multi-paper drafting risks entity bleed-through; isolate one
  sub-agent per paper (preferred) or `/clear` between papers; token/latency cost noted.

### Curation drafts — 10 papers (in external `active/`, NOT committed)
All drafted on **Fable 5**, each in its own **fresh general-purpose sub-agent** (only its one PDF +
the pipeline), so no cross-paper contamination. Each is `status: draft` with the machine-readable
`auto_check`+flags block; every ontology ID validated, none invented. Files:
`<PMID>-...-phiweaver-DRAFT.md`. Progress tracker: `active/BATCH-PROGRESS.md`.

| PMID | System | IDs | Flags |
| --- | --- | --- | --- |
| 1537802 | P. syringae pv. tomato avrPto × tomato Pto (gene-for-gene) | 6/6 | 5 |
| 1541525 | Cryptococcus neoformans URA5 × mouse (virulence) | 3/3 | 5 |
| 41295150 | Colletotrichum gloeosporioides CgHat1 × mulberry | 10/10 | 8 |
| 41229162 | P. syringae pv. tabaci FleQ/GcbB × tobacco (c-di-GMP) | 6/6 used | 7 |
| 41205159 | Colletotrichum siamense/graminicola NsdD × rubber/maize | 10/10 | 8 |
| 41170998 | Candida albicans Efg1 × mouse (hyphal morphogenesis) | 14/14 | 6 |
| 41156765 | Ceratocystis fimbriata CfSec22 × sweet potato | 17/17 | 6 |
| 41051314 | Candida albicans Rad53 × Galleria/mouse (overexpression) | used pass | 7 |
| 41134853 | Fusarium graminearum TRAPPIII × wheat (autophagy) | used pass | 6 |
| 41020836 | Fusarium pseudograminearum TOX2 × wheat | 8/8 | 7 |

(PMID:1799694 van Kan 1991 was dropped by the curator — scanned PDF, no text layer.)

### Data-quality catches by phiweaver (credit side)
- **Wrong PMID** on the Rad53 paper: filename `4101314` (impossible for 2025) → **corrected to
  41051314** (curator-confirmed); draft content, source PDF, and tracker all renamed/updated.
- **Obsolete PHIDO** term flagged (TRAPPIII: used PHIDO:0000162, flagged PHIDO:0000163 obsolete).
- **Paper cites wrong accession** (NsdD: wrong RefSeq for CgrnsdD) — flagged, ortholog offered.
- **Paper-internal contradictions** flagged (TOX2 conidiation "lost" vs reduced; SDS vs H2O2).
- Consistent **effector-trap avoidance** (Rad53, TRAPPIII, NsdD, TOX2 — no spurious GO:0140418),
  correct phenotype **direction** (negative regulators, overexpression), **attribution discipline**
  (Rad53: didn't curate prior-work deletion phenotypes), and **negative-result handling** (Efg1:
  didn't fabricate phenotypes for T208 mutants that phenocopied WT).

## 🔬 Cross-cutting benchmark signal (the point of the run)
Two recurring phiweaver weaknesses — the concrete improvement targets:
1. **UniProtKB accession resolution** — the #1 gap; nearly every paper (TrEMBL-only, wrong strain,
   ambiguous, REST fallback, or NO entry: FleQ/GcbB, one TRAPPIII subunit). Worst on older papers
   and non-model strains. Candidate fix: locus-tag → UniProt resolution + strain handling.
2. **PHIPO coverage for non-infection phenotypes** — `map_phenotype` returned nothing for bacterial
   motility/biofilm/c-di-GMP, autophagy, DON/mycotoxin production, host phytoalexin, CaCl2. Infection
   /virulence + stress terms map fine; specialist terms don't.

## ⚙️ Workflow established this session
- **One isolated sub-agent per paper** (fresh general-purpose, `model: fable`), given only its PDF +
  the pipeline (paper-triage → uniprot-lookup → genotype/phenotype → validate_ontology_ids), writing
  the DRAFT to `active/` and returning a summary. Parallel is safe (isolation is per-agent context).
- Agents sometimes go **idle without a summary message** → read the draft file directly to report.
- One agent hit the **account session limit** mid-cleanup but had already written a complete draft.
- `active/BATCH-PROGRESS.md` tracks done/pending (checkpoint for `/clear` or a new session).

## ➡️ How to proceed next (user hit token limit here)
1. **PUSH the 4 commits**: `main` is 4 ahead of `origin/main` — run `! git push origin main`
   (harness safety gate blocks the agent from pushing to the default branch). Commits: 0ed1009,
   67cb550, b280263, 7959dec.
2. **Prefill scorecards** for all 10 drafts:
   `python3 07-Standards/curation-benchmarking/fill_scorecard.py /mnt/z/PHI-Canto-Literature/active/*-phiweaver-DRAFT.md`
   → one `*-scorecard-PREFILLED.xlsx` per draft (objective column filled; reviewer column blank).
3. **Score by hand** each scorecard against your PHI-Canto curation (Correct / Needs improvement /
   Incorrect / N/A) + completeness block. Settle the flags first — **accession decisions** especially.
4. **Report**: `scorecards_to_csv.py active/*-scorecard-PREFILLED.xlsx --out scores.csv` then
   `python3 -m phiweaver.benchmark_report scores.csv --out benchmark-report.html`.
5. **Caveats on the numbers**: this was **NOT a blind/sandboxed run** (drafted in an open session by
   the curator's choice) — for a defensible number, redo drafting under
   `--settings 07-Standards/curation-benchmarking/benchmark-sandbox.settings.json` (bubblewrap is now
   installed). Every draft carries curator flags to resolve before scoring.
6. **Drafts are uncommitted** in external `active/` by policy (unpublished curation). Only wrapped,
   curator-validated examples belong in the repo (`07-Standards/curation-examples/`).

## Notes
- Green gate not re-run this session (no engine-code changes; only docs + external drafts).
- Backlog item "Activate the benchmark sandbox allowlist": **bubblewrap now installed** (`/usr/bin/bwrap`);
  still needs the one-time reachability test before a scored run.
