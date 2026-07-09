---
created: 2026-07-09
session_id: 2026-07-09-llm-as-judge-discussion
project: LLM-as-judge / independent-reviewer idea for benchmarking (discussion only — parked)
type: discussion / design note
tags: [benchmarking, llm-as-judge, reviewer, qc, ground-truth, calibration, parked, fable5]
duration: short discussion, no code
participants: [Claude Fable 5, martin2urban]
---

# Session Log: LLM-as-judge as a benchmarking / reviewer stage — discussion (parked)

**Date**: 2026-07-09
**Project**: Should PHI-Weaver add a separate QC / reviewer stage (an independent LLM judge) so it
does not self-validate its curation drafts?
**Outcome**: Discussion only. **Not progressing further for now** (curator's decision). This note
records the reasoning so it can be picked up later.

## How it came about
The curator gave **GPT-5.5** the publication, the phiweaver-generated curation draft, the PHI-Canto
entry queue, and the scorecard, and asked whether it agreed with phiweaver's curation. GPT-5.5
suggested improvements in several places and **scored lower than the curator would have**. That
prompted the question of using an LLM as a judge / benchmarking tool.

## What we already do (so the idea isn't fully new)
- **D12** already mandates an *independent* scorer: "phiweaver must not score its own drafts, or the
  benchmark is circular and meaningless." The scorecard pre-fills only mechanical checks; a **human**
  scores judgement.
- The **human curator is the validation gate** (§2 AGENTS.md; D13 — biocurator entry into PHI-Canto
  *is* the validation step). phiweaver never marks its own work "validated."
- `curation-qc` deterministic checks (ID validity, UniProt) are already genuinely independent — a
  script can't rationalise a choice it didn't make. The *reasoning* checklist part is currently run
  by the same drafting agent = weak self-review.

## The key distinction (why GPT scoring "low" is ambiguous)
What was run with GPT-5.5 is **reference-free judging**: the judge formed its *own* opinion of the
correct curation from the paper, then graded phiweaver against that. That is weaker than the
existing **gold-standard** benchmark, where truth is fixed and external. A general LLM doesn't know
PHI-base conventions (gene-for-gene recognition model, controlled genotype-label vocabulary, when a
disease name is assignable, PHIPO usage), so a lower score can mean any of:
1. it caught a **real error** the curator is too close to see (the payoff);
2. a **convention gap** — it penalised something correct-by-PHI-base-convention;
3. a **hallucination / misread** — it invented an issue;
4. **legitimate ambiguity**.
These have opposite implications and are currently mixed into one number.

## ⚠️ The point to stress: the judge must itself be ground-truthed
An LLM judge is **not** automatically trustworthy just because it's a different model. Its errors are
correlated with the drafter's for a same-model self-review, and for a cross-model judge it still lacks
PHI-base calibration. **Before any LLM-judge score is reported or trusted, the judge has to be
validated against ground truth** — run it on papers with a trusted human score-vs-gold and measure how
often it agrees (a small confusion matrix). This is the LLM-judge equivalent of the blind / no-leakage
discipline the `benchmark` skill already enforces on phiweaver. A judge that doesn't track human
scoring is a nitpick generator, not a benchmark. Cross-model (GPT judging Claude-generated drafts) is
good for decorrelating errors and should be preserved; the judge's model id must be recorded in
provenance (D7) because scores are only reproducible against a named model.

## Highest-leverage next step (when resumed)
Adjudicate the **GPT-5.5-vs-curator disagreements on this one paper**, item by item, into the four
buckets above. The ratio (mostly 1–2 = worth developing; mostly 3 = untrustworthy) answers whether
LLM-as-judge is viable here — one afternoon's work, more informative than running ten more papers.
Then, if it holds: anchor the judge with the scorecard rubric + PHI-base conventions, ground-truth it
against gold standards, and report its scores **alongside** (never instead of) the human's.

## Two honest uses, different bars
- **Pre-review critic** (flags candidate issues for the human): low bar — even ~60% precision saves
  time; false positives are cheap because the human adjudicates anyway. Adoptable readily.
- **Benchmark scorer reported to a team**: high bar — must be ground-truthed first, reported
  alongside human scores, never as the sole number.

## Status
Parked by curator decision (2026-07-09). Backlog item added under "Curation workflow" in
`docs/BACKLOG.md`. Related but distinct from the existing **Recuration-comparison** backlog item
(biocurator vs phiweaver neutral diff) and from D12 (independent human scorer).
