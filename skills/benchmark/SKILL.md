---
name: benchmark
description: Benchmark phiweaver's curation quality against already-curated papers (gold standards), blind and leakage-free, and produce team-reportable results. Use to score phiweaver on papers you have curated in PHI-Canto.
backing_script:
  - 07-Standards/curation-benchmarking/fill_scorecard.py
  - phiweaver/batch_summary.py
  - phiweaver/article_tokens.py
tests:
  - tests/test_batch_summary.py
  - tests/test_article_tokens.py
inputs:
  - a set of already-curated papers (each with a gold-standard PHI-Canto curation) to score
  - the curation-example library (checked so a paper's own gold standard is not retrievable)
outputs:
  - one prefilled, human-scored scorecard per paper
  - a batch review dashboard + CSV (accuracy, completeness, flags)
  - a per-article token table (tokens per PMID + shared-overhead split), for the session log
  - a report comparing the curated papers against a held-out gold-standard control set
---

# Benchmark

## Purpose
Measure phiweaver's curation quality **honestly** against papers a curator has already done
(gold standards), and produce a defensible number to report to a team. The whole value is that
the number is trustworthy, so the procedure **enforces blind drafting, no leakage, and
independent human scoring** — see `07-Standards/curation-benchmarking/README.md`.

## When to use
- When scoring phiweaver on a set of already-curated papers to report accuracy + completeness.

## Workflow
1. **Run blind + sandboxed.** Start the session with the network allowlist so phiweaver cannot
   reach PHI-base / PHI-Canto (website *or* GitHub):
   `claude --settings 07-Standards/curation-benchmarking/benchmark-sandbox.settings.json`
   (needs `bubblewrap`; the session refuses to start if the sandbox can't run). The gold-standard
   curation is **never given to phiweaver as input**.
2. **Prevent leakage.** For each paper, confirm its **own** gold standard is not a retrievable
   example in `07-Standards/curation-examples/` (temporarily remove it and regenerate the index if
   so). Otherwise phiweaver just retrieves the answer and the score is meaningless.
3. **Draft each paper** with the normal curation skills — paper-triage → uniprot-lookup →
   genotype-creation → phenotype-annotation (via phipo-mapping) → curation-qc — producing a draft
   with the machine-readable `auto_check` + `flags` block. Only the paper + UniProt + EBI OLS are
   used; every ontology ID is validated.
4. **Prefill the scorecard:**
   `python3 07-Standards/curation-benchmarking/fill_scorecard.py <draft>` — the objective column
   is filled; the reviewer-rating column stays blank.
5. **Score against the gold standard (human).** Rate each item Correct / Needs improvement /
   Incorrect / N/A by **comparing the draft to the known-correct curation**, and fill the
   completeness block (curatable items vs captured). **phiweaver does not score its own draft.**
6. **Roll up the batch:**
   `python3 -m phiweaver.batch_summary <drafts> --out BATCH-REVIEW.md --csv batch.csv`.
7. **Record per-article token cost:**
   `python3 -m phiweaver.article_tokens --drafts <drafts> --cost --out BATCH-TOKENS.md`
   (any batch of drafts, not only benchmarks). It reads the batch PMIDs from the draft `meta`
   blocks, attributes each turn to a paper via the per-paper draft/PMID references already in the
   session transcript, and splits the shared setup + context re-read as overhead (equal `1/N`, or
   `--weight-by-direct`). Paste the resulting table into the session log so each batch records
   which model curated it and what each paper cost. (Cache-read is session-cumulative, so it is
   counted as shared overhead, not charged to one paper.)
8. **Report** the human-reviewed curated papers alongside a **held-out gold-standard control set**
   (papers whose gold standard was never in the library), so the team can see how the numbers
   hold on unseen truth.

## Expected outputs
- One prefilled, human-scored scorecard per paper.
- A batch review dashboard + CSV (accuracy, completeness, flags by category).
- A per-article token table (tokens per PMID + shared-overhead split + model), pasted into the
  session log.
- A benchmark report: curated papers vs the held-out control set.

## Quality-control checks
- The session was **sandboxed / blind** — the allowlist profile was used and PHI-base is
  unreachable (confirm; do not proceed unsandboxed).
- Each paper's **own gold standard was excluded** from retrieval (no leakage).
- The gold standard was used **only at scoring**, never as drafting input.
- **phiweaver did not grade its own drafts** — the ratings are the human's.
- Every ontology ID validated (GO/PHIPO via OLS, PHIDO offline against the bundled ontology).

## Human review
- Scoring is the human curator's judgement against the gold standard — that is the benchmark.
  Flag low-confidence items. The reported numbers are only as trustworthy as the blind +
  no-leakage discipline, so state in the report that the protocol was followed.
