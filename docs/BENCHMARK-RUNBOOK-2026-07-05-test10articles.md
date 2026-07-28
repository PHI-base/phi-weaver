---
created: 2026-07-05
type: documentation
tags: [docs]
project: PHI-Weaver
---

# Benchmark runbook — test run, 10 already-curated articles (2026-07-05)

**Historical — one dated run.** Kept as the record of the 2026-07-05 test; the reusable
procedure lives in `skills/benchmark/SKILL.md`. See [`README.md`](README.md).

A short, concrete runbook for a **first benchmark**: curate 10 papers with phiweaver,
score them by hand on the Excel scorecard, and produce a shareable report.

- **Papers**: 10 articles you have **already curated in PHI-Canto** (the gold standards).
- **Control set**: **none** for this run (option 1). The gold-standard example library is
  small (5 examples), so retrieval-leakage risk is low. All 10 papers form a single group;
  state in the report that no held-out control split was used. Add a control set later, once
  the example library is bigger (see `docs/BACKLOG.md` and the `benchmark` skill).
- Full reference: the **`benchmark`** skill and `07-Standards/curation-benchmarking/README.md`.

## Model choice (record it; keep it constant)
The model is **part of what you are measuring** — an accuracy number is only meaningful attached
to a specific model. For this task (precision extraction + ontology reasoning under a strict
no-hallucination rule), more capable models generally help; roughly **Fable 5** (most capable) >
**Opus 4.8** > **Sonnet** (fast/cheaper).
- **Use one model for all 10 papers.** Mixing models across the batch confounds the result — you
  won't know whether a divergence was the paper or the model.
- **Benchmark the model you will actually curate with.** If production would realistically be
  Sonnet, benchmark Sonnet; otherwise the number overstates real-world quality.
- **Record it.** Set the model at session start (`/model`) and keep it fixed; `benchmark_report`
  records it as provenance.
- **This run:** use **Fable 5** to establish the quality ceiling (best phiweaver can currently do).
- **Optional second pass:** re-run the same 10 papers on Opus / Sonnet and compare accuracy vs
  cost — model then becomes a comparison axis (like biocurators in the recuration idea).

## Before you start (one-time)
1. **Paper PDFs in place** — put the 10 paper PDFs in the literature folder
   (`../PHI-Canto-Literature/active/`, or wherever `PHI_LITERATURE_ROOT` points). phiweaver
   needs the **papers**, not the PHI-Canto exports.
2. **Sandbox ready** — the blind benchmark session needs `bubblewrap`
   (`sudo apt-get install bubblewrap`). Without it the session refuses to start. (Backlog:
   "Activate the benchmark sandbox allowlist" — confirm this is done.)
3. **No leakage** — none of the 10 papers' **own** gold standards should be a retrievable file
   in `07-Standards/curation-examples/`. If one is, move it out and rerun
   `python3 -m phiweaver.curation_examples` before benchmarking that paper.

## The run
1. **Launch a blind, sandboxed session** (network limited to UniProt + EBI OLS; PHI-base /
   PHI-Canto / GitHub unreachable):
   ```
   claude --settings 07-Standards/curation-benchmarking/benchmark-sandbox.settings.json
   ```
2. **Draft all 10** — in that session, invoke the **`benchmark`** skill with the 10 papers.
   phiweaver drafts each one blind (paper + UniProt/OLS only, every ontology ID validated) and
   writes a draft `.md` with the machine-readable `auto_check` block. Your PHI-Canto curations
   are never given to it as input.
3. **Prefill a scorecard per paper** (objective column auto-filled; reviewer column left blank):
   ```
   python3 07-Standards/curation-benchmarking/fill_scorecard.py active/*-phiweaver-DRAFT.md
   ```
   → one `*-scorecard-PREFILLED.xlsx` next to each draft.

## Drafting multiple papers — isolate one paper per context
Curating several papers in a single Claude context risks **entity bleed-through**: genes,
hosts, strains, or figure numbers from one paper leaking into another's draft. Keeping paper
text in scratchpad files controls context *size* but not this cross-contamination. The only
hard guarantee is **isolation** — one paper per context so the others' entities are physically
absent while drafting:
- **Preferred: one sub-agent per paper.** Spawn a fresh agent per paper, given *only* that one
  PDF + the pipeline; it drafts, validates every ID, writes the `.md` to `active/`, and returns
  a summary. Zero jumbling; the main session stays lean. Run them **sequentially** (one lands
  before the next starts) so drafts are checkpointed to disk as you go.
- **Alternative: `/clear` between papers.** Same isolation, manual — but `/clear` also wipes the
  session setup, so each restart needs a one-line re-brief.
- **Cost note:** isolation is the heavier path — each cold agent re-reads the setup (skills,
  template, ID rules), so total tokens and wall-clock are higher than one continuous pass. Worth
  it when correctness matters (it usually does for curation); skippable only when the papers are
  so different that confusion is implausible.
- Keep a small `active/BATCH-PROGRESS.md` (done vs pending) so a reset or a new session can pick
  up cleanly.

## Score by hand (the manual step)
4. Open each `*-scorecard-PREFILLED.xlsx`. For every item pick **Correct / Needs improvement /
   Incorrect / Not applicable** from the dropdown by comparing phiweaver's draft to your
   known-correct PHI-Canto curation. Fill the **Completeness** block (curatable items in the
   paper vs how many phiweaver captured). Accuracy and completeness % compute automatically.
   **phiweaver does not score itself — the ratings are yours.**

## Report
5. Roll up and build the report:
   ```
   python3 -m phiweaver.batch_summary active/*-phiweaver-DRAFT.md --out BATCH-REVIEW.md --csv batch.csv
   python3 07-Standards/curation-benchmarking/scorecards_to_csv.py active/*-scorecard-PREFILLED.xlsx --out scores.csv
   python3 -m phiweaver.benchmark_report scores.csv --out benchmark-report.html
   ```
   `benchmark-report.html` is a self-contained page (headline accuracy + completeness, per-paper
   bars, an item × paper heatmap, and "where to improve" per item) that opens in any browser —
   the shareable result. With no control set, every paper is in the single `curated` group.

## Gotchas
- **Close each scorecard `.xlsx` in Excel** before re-running the fill/export scripts — an open
  file is locked and the write fails.
- The scoring in step 4 is the **only** manual part; everything else is a command.
- `fill_scorecard.py`, `scorecards_to_csv.py`, and `benchmark_report` need `openpyxl`
  (`pip install --user openpyxl`).
