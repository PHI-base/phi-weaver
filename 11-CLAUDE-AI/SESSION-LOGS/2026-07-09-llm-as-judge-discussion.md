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
4. **legitimate ambiguity**;
5. the **reference itself is wrong** — the human gold standard / curator made a mistake and the judge
   caught it (see the 2026-07-09 follow-up below — this bucket was added later; the original list
   wrongly assumed the human reference is ground truth).
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

## Follow-up (2026-07-09): giving the judge the curation-example library
A later question asked whether making the **curation-example library + registries** available to an
external model (e.g. GPT-5.5) would make the judge easier to set up. It helps, but only with one of
the four buckets. Supplying the examples + `TAGS.md` controlled vocabulary + `07-Standards` docs
directly attacks the **convention-gap** bucket (#2) — it turns a naïve outsider into a
convention-aware reviewer, which *is* the "anchor the judge with the scorecard rubric + PHI-base
conventions" step named above. It's **cheap** precisely because the library is already portable
markdown with structured frontmatter (OKF-shaped), so the files drop straight into the judge's
context with no conversion. **But it does not**: (a) remove the ground-truthing requirement — a
context-fed judge is better-calibrated, not validated, and its scores still can't be trusted until
measured against human score-vs-gold; (b) fix hallucination/misread (#3) or legitimate ambiguity
(#4); or (c) come free on **leakage** — the library *contains gold standards*, so never feed the
judge the gold-standard example of the very paper under test; give it same-annotation-type/topic
examples only. Net: library access moves the judge from *naïve* to *convention-aware*, not from
*unvalidated* to *trusted*. Strongest for the low-bar pre-review-critic use; for a paper that has a
gold standard, that gold standard is still a stronger anchor than the judge's reference-free opinion.

## Follow-up (2026-07-09): the "gold standard" is a strong reference, not ground truth
Curator's point: biocurators also make mistakes, so when the judge critiques a human gold standard,
"the human was wrong" is a real possibility, not an edge case. This corrects a hidden assumption in
this note — that gold = fixed external truth. It doesn't; "gold standard" means *best available
human-expert reference*, and inter-curator agreement is known to be imperfect. Consequences:

- **Adds bucket #5 above** (the reference itself is wrong), which applies whether the judge is grading
  a *draft* or a *gold standard*. The human curator is another estimator with its own error profile,
  not an oracle sitting outside the system.
- **Corrects the calibration step.** Earlier framing ("run the judge on gold-standard papers and see
  if it matches what we know is right") quietly assumes human = truth. The honest version: when judge
  and human disagree, a person **adjudicates**, and we count how often *each* was right — the gold
  standard is allowed to lose. So calibration measures a two-way disagreement, not judge-vs-oracle.
- **Doubles the judge's value.** Besides QC-ing new drafts, it can **audit the existing gold-standard
  library** — a judge-flagged error that turns out real *improves the reference set*. Repositions the
  judge from "must prove itself against the human" to "an independent estimator whose disagreements
  with the human are informative both ways." This strengthens the case for the tool.
- **Keep the asymmetry (don't over-rotate).** Their errors are *different*, not equal. The human holds
  PHI-base convention knowledge the LLM lacks, so on convention-heavy calls the human is usually still
  the stronger signal; the LLM's edge is consistency/tirelessness — catching *omissions* and mechanical
  slips a curator misses from being too close. Decorrelated errors are exactly why cross-checking works.
- **Procedural rule, not a hierarchy.** When the judge flags a gold standard, neither auto-overrule the
  human nor auto-dismiss the judge — a human adjudicates and the gold standard may lose. That is how the
  library improves instead of ossifying around early errors.

Deeper framing: there is no infallible ground truth in curation — every signal (drafting agent, human
curator, second curator, LLM judge, deterministic checks) is an imperfect estimator. The sound move is
to **triangulate** and investigate disagreements, not to crown one signal as truth.

## Two honest uses, different bars
- **Pre-review critic** (flags candidate issues for the human): low bar — even ~60% precision saves
  time; false positives are cheap because the human adjudicates anyway. Adoptable readily.
- **Benchmark scorer reported to a team**: high bar — must be ground-truthed first, reported
  alongside human scores, never as the sole number.

## Status
Parked by curator decision (2026-07-09). Backlog item added under "Curation workflow" in
`docs/BACKLOG.md`. Related but distinct from the existing **Recuration-comparison** backlog item
(biocurator vs phiweaver neutral diff) and from D12 (independent human scorer).
