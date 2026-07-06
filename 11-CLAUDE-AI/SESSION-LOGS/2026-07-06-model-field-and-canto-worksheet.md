---
created: 2026-07-06
session_id: 2026-07-06-model-field-and-canto-worksheet
project: Benchmark model-field provenance + PHI-Canto submission (Route 1 worksheet, Phases 1–3)
type: engine + docs
tags: [benchmarking, provenance, phi-canto, submission, worksheet, skill, fable5]
duration: ~1 session
participants: [Claude Fable 5, martin2urban]
---

# Session Log: model-field provenance + PHI-Canto entry worksheet (Route 1)

**Date**: 2026-07-06
**Project**: PHI-Weaver — (1) thread the drafting **model** through the benchmark stack so
provenance travels with the data; (2) scope how to get phiweaver drafts into **PHI-Canto**
(no write API) and build the recommended Route 1 (assisted-entry worksheet) through Phase 3.
**Session Type**: engine + docs. 6 commits on `main`, all pushed.

## ✅ Shipped (6 commits on `main`, pushed to origin)

### Benchmark run continuation
- Resumed the 2026-07-05 next-steps. **Push was already done** (`main` == `origin/main`).
  **Prefilled all 10 scorecards** from the drafts (`fill_scorecard.py`). Explained the scorecard's
  Reviewer-rating vs Points columns (D = human word; E = derived number: Correct=1, Needs
  improvement=0.5, Incorrect=0, N/A excluded — E feeds the SUM/accuracy formulas). User: leave as is.

### `4d5e95c` — model field through the benchmark stack
The drafting model is part of what a benchmark measures but lived only in session-log prose.
Now travels with the data: draft `meta.model`; a **Model** header row in the scorecard template
(relabelled row 9, moved Reviewer to the blank row 10 — no formula/dropdown shift);
`fill_scorecard.py` fills it; `scorecards_to_csv.py` emits a `model` column; `benchmark_report.py`
treats `model` as a reserved column and **auto-derives the provenance-footer model from the CSV**
(explicit `--model` still overrides). +3 regression tests. Added `"model": "Fable 5"` to all 10
drafts; regenerated **9/10** scorecards (PMID:1537802 was open in Excel → still needs a rerun).
All 10 drafts were curated with **Fable 5**.

### `5f62bba` — PHI-Canto submission routes assessed → `docs/CANTO-SUBMISSION-ROUTES.md`
Confirmed via web: PHI-Canto is a Canto instance; **no public write API**; `canto_load.pl` is a
**server-side** admin script. Three routes documented — (1) assisted-entry worksheet [web login
only], (2) Canto session JSON + `canto_load.pl` [needs server access], (3) browser automation
[brittle, not advised]. Recommendation: **Route 1 now, Route 2 if server access, avoid 3**. Pivotal
open decision: server/admin access to canto.phi-base.org vs web login only.

### `81e310d` — Route 1 build spec → `docs/CANTO-ROUTE1-BUILD-SPEC.md` (+ backlog pointer)
Full scope with a worked TOX2 worksheet sample. **Key framing: biocurator entry into PHI-Canto
*is* the validation step** — no separate review gate, the human is unavoidably in the loop, AI
drafts reach the queue only through a curator's entry. Recommends a structured `canto` block +
deterministic renderer.

### `604681b` — Phase 1: structured `canto` block in the draft schema
Added a machine-readable `canto` object to `_TEMPLATE.md` (genes [uniprot accession = Canto
add-gene id], alleles, genotypes, metagenotypes, annotations with `{relation,value}` extensions),
in Canto's entry order. Proved it by populating the **TOX2 draft (PMID:41020836)** as the reference
instance (external, uncommitted): JSON parses; all metagenotype/annotation features resolve; the
two term-gapped phenotypes (DON, CaCl2) stayed in `flags`, not invented. Existing readers
(`fill_scorecard`, `batch_summary`) ignore the new key.

### `e1b09fa` — Phase 2: deterministic worksheet renderer
`phiweaver/canto/worksheet.py` renders the `canto` block into an ordered Markdown checklist
(genes → alleles → genotypes → metagenotypes → annotations → submit). Extensions joined with `·`
so a value's own `;` stays unambiguous; missing-term annotations + all flags surfaced as ⚠. Pure
stdlib; one worksheet per draft (or `--stdout`). **11 network-free tests.**

### `bffcf8a` — Phase 3: register the `canto-worksheet` skill
`skills/canto-worksheet/SKILL.md` (backed by `worksheet.py`, tested by `test_canto_worksheet.py`);
regenerated `skills/REGISTRY.md` (**9 skills**). Documents the Route 1 workflow + validation model.

## 🧪 Green gate
Smoke **7/7**; unit tests **108** (was 94 at session start; +3 model, +11 worksheet). Registry
contract check green.

## ➡️ How to proceed next
1. **Phase 4** — back-fill the `canto` block for the other **9 drafts** (TOX2 done), then
   `python3 -m phiweaver.canto.worksheet /mnt/z/PHI-Canto-Literature/active/*-phiweaver-DRAFT.md`
   to generate all worksheets. Per-draft LLM work (read prose → structured block); external/uncommitted.
2. **Regenerate the PMID:1537802 scorecard** once it's closed in Excel (model row was added to the
   draft; the prefilled `.xlsx` couldn't be rewritten while open).
3. **Benchmark scoring** (curator) still pending: hand-score the 10 prefilled scorecards, resolve
   draft flags (accessions especially), then `scorecards_to_csv.py` → `benchmark_report`.
4. **Canto Route decision** — if PHI-base has server access to canto.phi-base.org, scope Route 2
   (session JSON + `canto_load.pl`); otherwise Route 1 worksheet is the path.

## Notes
- Per-paper work products (drafts, scorecards, worksheets) stay in external `active/`, uncommitted;
  only engine/docs/skills go in the repo.
- WSL z: mount: every branch op prints `chmod .git/config.lock … Operation not permitted` — benign;
  merges/pushes succeed. Direct push to `main` worked this session (no safety-gate block hit).
