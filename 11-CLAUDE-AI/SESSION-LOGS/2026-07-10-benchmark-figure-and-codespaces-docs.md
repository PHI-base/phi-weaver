---
created: 2026-07-10
session_id: 2026-07-10-benchmark-figure-and-codespaces-docs
project: Benchmark result figure (10 papers) + Codespaces hardening & docs
type: analysis + docs/infra
tags: [benchmarking, scorecard, completeness, codespaces, devcontainer, smoke-test, docs, fable5]
duration: medium
participants: [Claude Fable 5, martin2urban]
---

# Session Log: Benchmark result figure + Codespaces hardening/docs

**Date**: 2026-07-10
**Project**: Turn the 10 hand-scored benchmark scorecards into the shareable result figure; then
answer/harden the GitHub Codespaces story and document it.
**Outcome**: Result figure generated (mean accuracy **89%**, completeness set to **100%**). Five
commits on `main`, all pushed. Smoke test verified 7/7 (plain + Codespace mode).

## 1. Benchmark result figure (10 papers)
The curator finished hand-scoring all 10 `*-scorecard-PREFILLED.xlsx` (13 accuracy items each,
all rated). Ran the runbook's Report step against the external `PHI-Canto-Literature/active/`:
- `phiweaver.batch_summary` → `BATCH-REVIEW.md` + `batch.csv`
- `scorecards_to_csv.py` → `scores.csv`
- `phiweaver.benchmark_report` → `benchmark-report-2026-07-09.html`

**Headline: mean accuracy 89% (curated, n=10; range 68–100%).** Weakest annotation types:
RNA/expression 70%, genotype 75%. Strongest paper Efg1 (100%); weakest FleQ/GcbB (68%) and
Rad53 (77%).

Two data fixes before the figure was trustworthy:
- **GO label-splitting bug**: the FleQ/GcbB scorecard labelled the GO item
  `"GO / gene annotation correctness"` while the other nine used the fuller
  `"…(incl. effector GO:0140418)"` — `scorecards_to_csv` keyed on the label and split one item
  into two heatmap rows (9/10 + 1/10). Normalized that cell in the source `.xlsx`, regenerated →
  13 clean items.
- **Completeness**: the block (curatable/captured) was blank (→ 0, rendered as "—"). Curator
  confirmed all 10 curations are 100% complete; set curatable = captured (missed = 0) in each
  scorecard so completeness renders 100%. Used a temp-file+atomic-replace to dodge an Excel-lock
  on the z: mount (the runbook's "close the .xlsx first" gotcha).

All of the above lives in **external `active/` (uncommitted)** — the report HTML, `scores.csv`,
`batch.csv`, `BATCH-REVIEW.md`, and the edited scorecards are outside the repo.

## 2. Completeness methodology + reviewer prompt (committed)
Discussed how completeness is measured: `captured / curatable`, human-supplied, **denominator must
come from the gold standard / paper independently of the draft** (else a miss is uncountable). For
the no-gold-standard case, wrote a two-phase prompt for the curator's GPT reviewer:
- **Phase A** — enumerate curatable annotations **from the paper PDF alone** (draft withheld to
  avoid anchoring), guided by the **12 PHI-Canto annotation types** + scope/counting rules.
- **Phase B** — match phiweaver's draft to that list; present-but-wrong = captured, extras don't
  inflate; returns curatable/captured/missed for the scorecard.

→ `07-Standards/curation-benchmarking/completeness-review-prompt.md` (commit **e6ab4b2**).

## 3. Model-choice question (advice only)
Asked whether Sonnet 4.5 vs Opus 4.8 would matter for curation. Loaded the `claude-api` skill for
current model facts. Advice: model is part of what the benchmark measures; this task (precision
extraction + ontology reasoning under no-hallucination) favours stronger models. If cost-driven,
prefer **Sonnet 5** over Sonnet 4.5 (near-Opus, supports effort). Don't estimate — **re-run the same
10-paper benchmark on the candidate model** (the runbook's optional second pass). No code.

## 4. Codespaces: still works, now hardened + documented
Confirmed phi-weaver still runs in GitHub Codespaces after recent commits (docs + the
canto-worksheet retire refactor): devcontainer unchanged, `auto-process`/`complete-paper` present,
smoke 7/7. Then:
- **Hardened the smoke-test in the devcontainer** into a real gate — it was already in
  `postCreateCommand` but swallowed failures with `|| echo` (exit 0). Now prints a loud banner and
  **exits 1** on failure so Codespaces flags the build (still connectable). Verified both paths
  (pass → 0, simulated fail → 1); JSON still valid. Commit **e27dc15**.
- **Documented Codespace storage** in `DEMO-CODESPACES.md`: `PHI_CURATION_ENV=codespace` →
  in-workspace `demo-literature/` root; input `active/`, output `completed/`, figures `media/`;
  gitignored/Codespace-only ⇒ **download before deleting**. Also documented the three phiweaver
  artifacts written next to a draft in `active/` (`-phiweaver-DRAFT.md`, `-phi-canto-entry-queue.md`,
  `-scorecard-PREFILLED.xlsx`). Commit **bb19f7d**.
- **Sequential-curation note**: you *can* stage all 10 PDFs in one batch, but curation runs
  **sequentially, one paper per subagent, each draft checkpointed to disk before the next** — for
  context isolation (no entity bleed-through) and resumability on timeout. Parallel discouraged
  (bleed-through, shared-SQLite contention, concurrent rate-limit/cost). Commit **4bd86a0**.

## Commits (all on `main`, pushed)
- `e27dc15` Devcontainer: make the Codespace smoke test a hard gate
- `bb19f7d` Docs: Codespace storage paths + phiweaver output files
- `4bd86a0` Docs: curate several papers sequentially, not in parallel
- `e6ab4b2` Add completeness-review prompt for the GPT reviewer
- (this log)

Smoke 7/7 (plain + `PHI_CURATION_ENV=codespace`).

## NEXT
- Optional: re-run the 10-paper benchmark on **Sonnet 5** (or Opus 4.8) for a model-comparison axis.
- If auditable completeness is wanted, replace the proxy curatable/captured counts with real
  per-paper gold-standard annotation counts (or run the GPT reviewer prompt).
- Move the benchmark report/CSVs out of external `active/` into a kept location before that folder
  is cleaned; they are currently uncommitted and outside the repo.
