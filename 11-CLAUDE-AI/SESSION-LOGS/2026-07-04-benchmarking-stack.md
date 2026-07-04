---
created: 2026-07-04
session_id: 2026-07-04-benchmarking-stack
project: Benchmarking stack + blind-benchmark integrity + reporting
type: feature (benchmarking)
tags: [benchmarking, scorecard, sandbox, integrity, report, skill, phikestrel]
duration: ~1 session (continued from 2026-07-03)
participants: [Claude Fable 5, martin2urban]
---

# Session Log: benchmarking stack, integrity controls, and the HTML report

**Date**: 2026-07-04
**Project**: PHI-Weaver — finish the benchmark-against-gold-standards pipeline end to end.
**Session Type**: Feature. 9 commits, all merged to `main` and pushed; green throughout.

## ✅ Shipped (9 commits on `main`)
- **`2b69a12` + `2c45caa` benchmark integrity policy** — blind drafting, no leakage, held-out
  control set. PHI-base web access **denied** via `.claude/settings.json` WebFetch rules
  (`*.phi-base.org` etc.; `.claude/` is gitignored, so it's local). Named the PHI-base **GitHub
  data repos** as a leakage source that can't be cleanly domain-denied.
- **`07f28d2` benchmark sandbox profile** — `benchmark-sandbox.settings.json`: an opt-in
  `--settings` profile that runs Claude sandboxed with the **network allowlisted to UniProt +
  EBI OLS only** (rest.uniprot.org, www.ebi.ac.uk), `failIfUnavailable: true`. The airtight control
  (covers website *and* GitHub). Needs `bubblewrap` (**now installed** by the user).
- **`c6d77ed` benchmark skill** — the named blind/leakage-free/scored procedure (registry now
  **8 skills**), with QC checks enforcing sandboxed + no-leakage + not-self-scored.
- **`2dbe3eb` benchmark_report** — `phiweaver/benchmark_report.py` (stdlib): a self-contained HTML
  report from a scores CSV (headline tiles, per-paper accuracy+completeness bars, item×paper
  ratings heatmap with text labels, average accuracy per item, curated-vs-control) + a synthetic
  sample + tests.
- **`77f0586` scorecards_to_csv bridge** — reads the human-filled scorecards (ratings col D +
  completeness) → the scores CSV. Pipeline now complete: scorecards → CSV → HTML.
- **`cd8f30d` quickstart + discoverability** — a "Quickstart — running a benchmark" atop the
  benchmarking README, and OVERVIEW lists the benchmark + gold-standard-import capabilities.
- **`75a61d1` report provenance** — the HTML now records generation **date** (auto), **model**
  (`--model`), **source file** (auto), and **curation tokens** (optional `tokens` column + total).
  Honest: phiweaver does NOT measure tokens — they are supplied.
- **`b6167ed` backlog** — automatic per-paper token logging during drafting (future).

## 🧭 The benchmarking pipeline (now complete)
`benchmark` skill (blind, sandboxed) → draft each paper (paper + UniProt/OLS only) →
`fill_scorecard.py` prefill → **human scores vs gold standard** → `scorecards_to_csv.py` →
`phiweaver.benchmark_report` → shareable HTML (+ `batch_summary` flag dashboard). Integrity:
the sandbox allowlist + the documented blind/no-leakage/control-set policy.

## 🐣 Side thread — phikestrel (new, separate project)
Advised on and scaffolded a **new** project split from phi-weaver: **phikestrel**
(https://github.com/martin2urban/phikestrel) — the plug-in / **pipe-based** host running curation
modules with a **local AI on ROGER**. Wrote the setup/dev guide to `/mnt/z/phikestrel-SETUP.md`
(move into that repo as README) and seeded its Claude project memory
(`~/.claude/projects/-mnt-z-phikestrel/memory/`). It is developed in its own repo/environment,
not here. Honest split recorded: core framework + plugins are autonomously buildable; ROGER
deployment is supervised (needs the cluster + research-computing).

## ✅ Verification
Smoke **7/7**, **81 tests**, **8 skills**, **1 validated gold-standard example**. Tree clean apart
from `.obsidian/` editor state; drafts/scorecards/source PDFs live in external `active/`.

## ⏭️ NEXT
1. **Run a real benchmark** once curation starts: activate the sandbox profile (bwrap is installed
   — do the one-time test), then invoke the `benchmark` skill on the already-curated papers.
2. Backlog: **PHIDO validation fix**, **automatic token logging**, more gold-standard examples
   (~8–12), format convergence, physical-interaction scope. See `docs/BACKLOG.md`.
3. **phikestrel** development proceeds in its own repo (Phase 0 scaffold → framework, PR-per-task).

---

*Human-in-the-loop benchmarking; scoring stays human by design. See `docs/DESIGN-DECISIONS.md`
(D12), `07-Standards/curation-benchmarking/README.md`, `docs/BACKLOG.md`.*
