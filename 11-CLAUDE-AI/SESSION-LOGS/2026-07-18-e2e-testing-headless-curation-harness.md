---
created: 2026-07-18
type: session-log
tags: [status/complete]
project: E2E testing — concept, headless curation harness, test-vs-production
summary: Clarified E2E vs smoke/unit, built + verified scripts/e2e/ (headless blind draft → deterministic ID-overlap score, 16/16 on FgKnr4), and settled how to use it for real batch curation.
---

# Session: E2E testing — from a terminology question to a working headless curation harness

A question-driven, mostly conceptual session that ended in a small, verified build. Started from
"what is N-to-N testing?", which turned out to be **"end to end"** misheard — and cascaded into:
what E2E means for weaver, whether the pipeline actually runs E2E, building the missing piece,
running it for real, and deciding how (and whether) to use it for production curation.

## Objectives
- Answer "what is N-to-N / E2E testing, and is it worth pursuing for weaver?"
- Determine whether the curation pipeline can actually run end to end.
- If the gap is real, build and **verify** the missing piece on a gold-standard paper.
- Decide how E2E should (and shouldn't) be used for curating new papers.

## Work done

### Concept: E2E vs smoke vs unit, run vs test
- "N to N" ≈ "end to end" (phonetic). Drew the ladder: **unit** (one function) → **smoke**
  (`phiweaver.smoke`, is it alive) → **E2E** (does the real flow make the right product).
- Key distinction surfaced by the user: telling Claude "curate paper X" is an end-to-end **run**;
  it's a **test** only when a harness launches it unattended and reduces it to a pass/fail against
  a known answer. And a **gold standard is only half** of an E2E test — the answer key; the
  automated *producer* is the other half.

### Diagnosis: the pipeline runs mechanically, not intelligently
- `phiweaver/pipeline/curation_pipeline.py` is a deterministic **file-mover** (PDF→markdown→file);
  it has **no model call**. The reasoning step (paper → `…-phiweaver-DRAFT.md`) is done by a
  human + Claude driving the skills — the manual hole in the middle.
- Ran the mechanical pipeline E2E on a throwaway copy (temp `PHI_LITERATURE_ROOT`): convert →
  track → complete all worked; smoke 8/8 green. Cleaned up the repo side-effects it wrote
  (session log, Article-Registry, gitignored tracking DB rows).

### Built: `scripts/e2e/` — the "wrapped" draft step (commit 54de438)
- **`e2e-curate.sh <paper.md> <gold.md>`** — launches a headless, blind-sandboxed `claude -p` to
  curate one paper, prefills the scorecard, then scores. ~55 lines.
- **`score_against_gold.py`** — stdlib-only precision/recall/F1 over PHIPO/GO/PHIDO/FYPO/PECO/
  UniProtKB ids; exit code = pass/fail on overall F1. ~90 lines. **ID-overlap only** — explicitly
  *not* curation nuance (genotypes, evidence codes, extensions, annotation-type attachment).

### Ran it for real — blind + sandboxed on PMID39787257 (FgKnr4)
- Result: **16/16 ids, overall F1 1.00** (PHIPO/GO/PHIDO/UniProtKB all perfect), from an input PDF
  that converted to only ~850 words (abstract + captions).
- **Two things the run surfaced and we fixed:**
  1. **Blind sandbox needs `socat` as well as `bubblewrap`** — the benchmark profile sets
     `failIfUnavailable: true`, so it refused to start until `sudo apt install socat`. **This bites
     the `benchmark` skill too.** (Also: an *unsandboxed* nested `claude -p` from inside a Claude
     Code session is blocked by the auto-mode classifier; the sandboxed variant is allowed.)
  2. **Scorer was format-sensitive** — the draft wrote `UniProtKB:**A0A1C3YKU0**` (markdown bold),
     so the regex missed 2 ids and reported a false 0.93. Hardened `extract_ids` to strip emphasis
     markers; raw draft then scored 16/16. (Good reminder: run the thing, don't trust the first number.)
- Leakage controlled: hid the paper's own gold example + practice notes on-disk during drafting,
  scored against a staged private copy, restored everything after.

### Decided: test vs real curation
- The drafting **engine** is production-usable; the **script** is test-shaped (needs a gold, ends by
  scoring). For **real curation at small volume, use the Claude CLI directly** — it already is the
  agent that runs the skills; run it **un-sandboxed** so it can use the example library + PHI-base.
  Output is a **review-ready draft, not an auto-submission**.
- **Batch ~10 papers over days without hitting usage limits:** drop-folder, not a scheduler —
  inbox → outbox, "done = draft is in the outbox", a fixed few per day, resumable; **no rate-limit
  code**. Capture the instruction once as a small `batch-curate` skill for consistency (deferred).

### FAQ + conventions
- First made a standalone `docs/E2E-TESTING-FAQ.md`; user corrected → **fold into the existing
  `docs/FAQ.md`**. Appended 3 E2E entries under "Project & tooling" (commit 0b92dcd). Saved this as
  a durable rule: **"make a FAQ" = append to `docs/FAQ.md`, never a new file.**
- Committed the user's pre-existing `table-of-contents` block additions to 4 vault docs (0e596f5).

## Key decisions
- **E2E is worth pursuing, but the plumbing wasn't the risk** — the missing piece was the model/draft
  step made unattended ("wrapping"). The headless `claude -p` wrapper is that piece; it's tiny
  (~145 lines) because every heavy component (skills, sandbox profile, scorecard, batch summary)
  already existed.
- **The deterministic scorer is the CI-able floor, not the benchmark** — ID overlap only; the human
  scorecard + judge-in-design own curation nuance.
- **Production curation ≠ the test harness** — use the CLI un-sandboxed; drafts stay human-reviewed
  and human-entered into PHI-Canto.
- **"Make a FAQ" appends to `docs/FAQ.md`** (feedback memory).

## State / open threads
- **All pushed to `origin/main`** through `0e596f5` (3 new commits: `54de438` scripts, `0b92dcd`
  FAQ, `0e596f5` TOC blocks). Working tree clean of tracked changes.
- `scripts/e2e/` committed; **blind sandbox now requires `socat`** (installed on this machine).
- Local tracking DB carries two stray sessions (11, 12) from the mechanical-pipeline test — harmless,
  gitignored, not in the repo.
- **Deferred (not built):** a `batch-curate` skill and/or a production `curate` subcommand wired into
  `curation_pipeline.py` — the CLI covers the need for now.
- Memories written: `e2e-curation-test-harness`, `faq-append-existing`.
