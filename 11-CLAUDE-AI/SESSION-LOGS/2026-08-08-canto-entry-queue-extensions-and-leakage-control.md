---
created: 2026-08-08
type: session-log
tags: [status/complete]
project: PMID:39787257 entry-queue request → leakage-safe E2E detour → two real entry-queue bugs found and fixed
summary: "Curate in sandbox PMID:39787257" turned out to mean the entry-queue file, not a re-run of the E2E benchmark harness — but not before building real leakage control for that harness (fresh clean paper conversion, every answer-bearing file for the PMID physically moved aside) that the user then didn't need. Generating the entry queue surfaced two real bugs. (1) Annotation extensions (observed_organ, infects_tissue, infective_ability) silently dropped everywhere except compared_to_control/interactor — fixed (commit 89a0548, pushed). (2) The evidence-code check itself was checking every annotation type's evidence string against one wrong, generic vocabulary instead of that type's own PHI-Canto-configured list — a user correction after I'd initially, wrongly, told them "Macroscopic observation (...)" wasn't a real code, when it is. Fixed in canto_config.py + entry_queue.py, per-type now, 92 tests green — not yet committed. A parallel fix for missing strain/background fields on the draft was applied, then explicitly reverted at the user's request.
---

# Session: entry-queue request, a leakage-control detour, and a real bug in the queue renderer

## Recap

Asked to "curate in sandbox PMID:39787257." That PMID turned out to be the exact paper the E2E
harness (`scripts/e2e/`) was verified against on 2026-07-18 (16/16 ids, F1 1.00) — gold standard
and a matching drafted `canto` block already existed in the repo/literature tree. Read "sandbox"
as "re-run the blind, sandboxed E2E test harness," and built real leakage control for it: the
first paper.md candidate turned out to itself be a curation record (leaking gene identities), so
converted a fresh clean paper-only markdown from the raw PDF, staged a private gold copy, and
physically moved aside every answer-bearing file for this PMID (gold-standard example, two prior
curation-record drafts, the GOLD-standards PDF) before launching. The user rejected the harness
run twice, then clarified: no score needed, just the entry-queue file. Restored everything,
generated the queue directly from the existing validated draft. That surfaced two real bugs in the
rendering/validation stack. First, annotation extensions were silently dropped — fixed, tested,
committed, pushed (`89a0548`). Second, and more serious: asked what an evidence-code ⚠ warning
meant, answered confidently that the string wasn't a real PHI-Canto code — **and was wrong**. The
user pushed back with a fact check (it's both a real Canto evidence value and shown on the PHI-base
website); tracing it down found the checker was validating every annotation type's evidence string
against one generic, wrong vocabulary instead of that type's own configured list. Fixed properly in
`canto_config.py` + `entry_queue.py`, not yet committed. A related fix (missing
`strain`/`background` on the draft's genotypes) was applied and then explicitly reverted when the
user said not to.

## Objectives
- Work out what "curate in sandbox PMID:39787257" actually meant.
- If it meant the E2E test harness, run it leakage-safe.
- If it meant a real deliverable, produce the PHI-Canto entry-queue file.
- Answer the user's questions about what the queue's ⚠ markers and coverage warnings mean, and fix
  what turns out to be a real bug rather than just explaining it away.

## Work done

### 1. Diagnosed "sandbox" as the E2E harness, then found the input was contaminated
`docs/FAQ.md` and the 2026-07-18 session log confirmed PMID:39787257 (FgKnr4) is the harness's own
verification paper. Checked `bwrap`/`socat` present. First attempt used
`PHI-Canto-Literature/completed/2026-05-17-39787257-FgKnr4-practice.md` as `paper.md` — on
inspection its frontmatter reads `type: curation-record`, `status/in-progress`, and its body lists
"Priority genes for curation." That is a leak, not paper text. `archive/PMID39787257-Kroll-2025-
PHI-Canto-Curation.md` (another old curation draft) and the gold-standard example itself were also
answer-bearing and on disk, readable by the blind agent regardless of the network sandbox — the
sandbox's `filesystem.allowWrite` only restricts writes, reads are unrestricted.

### 2. Built real leakage control (both runs later rejected by the user)
Converted `archive/PMID39787257-Kroll-2025.pdf` fresh via `pdf-convert.py` into scratch — 34 pages,
18,171 words, verified clean (abstract/intro/methods/results, no curation content), a much fuller
conversion than the ~850-word abstract-only one from the original 2026-07-18 verification run.
Staged a private copy of the gold-standard markdown, then physically `mv`'d aside all four
answer-bearing files (gold-standard example, both practice/curation-record drafts, the GOLD-
standards PDF) into a scratch holding dir. Two attempts to run `scripts/e2e/e2e-curate.sh` with the
clean paper + staged gold were both interrupted/rejected by the user.

### 3. The actual ask: just the entry-queue file
User: "i don't need the score, i just need the entry queue file." Restored all four moved-aside
files (WSL `/mnt/z` chmod-on-preserve warnings during `mv`, content unaffected — the same class of
`/mnt/z` permission quirk as the git-config chmod issue). The existing
`PMID39787257-FgKnr4-phiweaver-DRAFT.md`
(from the 2026-07-18 verification run) already carried a fully populated `canto` block matching
gold 16/16, so ran `python3 -m phiweaver.canto.entry_queue` on it directly — no re-drafting needed.
Produced `PMID39787257-FgKnr4-phi-canto-entry-queue.md`/`.docx` in
`/mnt/z/PHI-Canto-Literature/e2e-test/` (outside the repo, not git-tracked). 2 genes enter-ready,
15 annotations enter-ready, 0 parked; 6 coverage advisories on stderr (see §5).

### 4. Explained the ⚠ evidence-string marker — **wrongly**, corrected in §7
User asked what `⚠ Macroscopic observation (quantitative observation)` meant on the F3 rows.
Traced to `entry_queue.py`'s evidence-code check and reported it as working as designed: every
evidence string checked against `canto_config.evidence_codes` (82 codes, from `evidence_types:` in
`canto_base.yaml`); that list has no "macroscopic observation" entry, so — I said — the string
genuinely wasn't a Canto code, and recommended `Cell growth assay` as the closest real substitute.
**This was wrong**, and confidently so: I verified the string's absence from *a* list without
checking whether that was the *right* list. See §7 for what actually governs the field and why
the check itself was broken, not just this one example.

### 5. Found and fixed a real bug: annotation extensions were silently dropped
User noticed the queue had no extensions at all, despite the draft's `canto` block carrying
`observed_organ: conidium` (2 pathogen-phenotype rows) and `infects_tissue`/`infective_ability` (2
interaction rows). Traced to `entry_queue.py`: only `compared_to_control` (→ `Compared with`,
`interaction` shape) and `interactor` (→ `Interactor B`, `physical` shape) were ever extracted from
`extensions`; every other relation was dropped with **no** advisory either — unlike a bad evidence
string, nothing surfaced it. The smoking gun: `_fmt_extensions()` was already written in
`phiweaver/canto/record.py` and already imported into `entry_queue.py`, but never actually called
anywhere — dead code, presumably intended to be wired in and never was.

**Fix** (`89a0548`, pushed `c6bf441..89a0548`):
- New `_extensions_cell(a, exclude=...)` helper wired into every annotation shape's row builder
  except `physical` (whose only extension, `interactor`, already has its own column).
- New `Extensions` column, last in each affected table — matches the curation-example library's
  own convention (Extension trails Figure there too).
- Module docstring updated to document the behaviour and what it fixes, referencing PMID:39787257
  as the regression case.
- 4 new tests in `tests/test_entry_queue.py` (`ExtensionsColumnTests`): a pathogen-phenotype
  extension renders; an interaction extension renders alongside (not duplicating)
  `compared_to_control`; no-extensions renders `—` not a blank cell; `physical` still has no
  generic Extensions column.
- Verified: 57/57 `test_entry_queue.py` (53 existing + 4 new), 73/73 combined with
  `test_export_docx.py` (its table renderer is column-agnostic — confirmed no changes needed
  there). Regenerated the real PMID:39787257 queue and confirmed `observed_organ=conidium` and
  `infects_tissue=.../infective_ability=...` now appear.
- Committed and pushed on explicit request ("commit and push").

### 6. Strain/background coverage warnings — explained, fixed, then reverted
User asked what the six `strain_background_warnings` advisories meant and to fix them too.
Explained `phiweaver.canto.coverage.strain_background_warnings()` and the underlying curator ruling
(2026-07-25, `07-Standards/PHI-Canto-Curation-Conventions.md` "Strains and cultivars — wild type
only"): a wild-type genotype carries `strain`, an allele-bearing genotype carries `background`
(parent strain + endogenous copy's status), never both; Canto's own UI needs a strain per organism
before any genotype can be created. Edited `PMID39787257-FgKnr4-phiweaver-DRAFT.md` (prose +
`canto.genotypes`) to add `background: "PH-1; endogenous FgKnr4 {present,absent}"` /
`"IPO323; endogenous ZtKnr4 {present,absent}"` on the four pathogen genotypes and
`strain: "Bobwhite"`/`"Riband"` on the two host wild-type genotypes, then regenerated the queue —
all six warnings cleared, A2/C/D tables picked up the new fields correctly. User then said "do not
do this perhaps if necessary," so **reverted** both the prose and the JSON block back to their
original content and regenerated the queue/docx back to the original (warnings-present) state.
Confirmed this whole exchange touched only the external, non-git-tracked draft file in
`/mnt/z/PHI-Canto-Literature/e2e-test/` — nothing in the repo needed undoing.

### 7. User caught a wrong answer: evidence codes were checked against the wrong vocabulary
User: "i am not sure why: Macroscopic observation (qualitative observation) is not acceptable it
is both an evidence in PHI-canto and also displayed on the PHIbase 5 website." Re-verified from
scratch instead of defending §4. `grep -i macroscopic` across both config files found the exact
strings in `canto_base.yaml` **and** `canto_deploy.yaml` — but not under the `evidence_types:` key
`_evidence_codes()` reads (that key is a *different*, coarser catalog: short GO-style codes like
`IMP`/`IDA` plus a partial assay list, used nowhere as a per-type dropdown). The real, authoritative
source is `available_annotation_type_list` in `canto_deploy.yaml` (public, committed,
PHI-base/canto-config) — **every annotation type declares its own `evidence_codes:` list**: the
three GO types allow only `IDA`/`IGI`/`IMP`/`IPI`/`EXP`/`TAS`; `pathogen_phenotype`,
`host_phenotype`, `pathogen_host_interaction_phenotype` and `gene_for_gene_phenotype` share a
~20-code assay vocabulary that **does** include both `Macroscopic observation (qualitative
observation)` and `(quantitative observation)`; `physical_interaction` has its own PSI-MI-style
set; `post_translational_modification` allows only `IDA`; the two expression types allow a handful
each; `disease_name` has no evidence field at all. Confirmed the existing test suite baked in the
same wrong assumption: `EvidenceCodeFlaggingTests.INVALID = "Penetration assay"` ("not a code," the
comment said) is in fact a valid `pathogen_phenotype` code in the real config — an independent
second instance of the identical bug, caught by running the corrected check against it.

**Fix (uncommitted at end of session):**
- `phiweaver/lookup/canto_config.py`: new `annotation_type_configs` property (`available_
  annotation_type_list` keyed by `name`) and `evidence_codes_for(annotation_type)` method — the
  real per-type list. `evidence_codes` (the old generic catalog) kept, docstring corrected to say
  plainly it is not what governs any type's dropdown. `validate_evidence_code` now requires an
  `annotation_type` argument; CLI gained `--annotation-type` (required with `--check-evidence`,
  optional to scope `--list evidence`).
- `phiweaver/canto/entry_queue.py`: `_evidence_codes()` → `_evidence_codes_for(annotation_type)`
  (`lru_cache`d per type); `_evidence(a)` and `_bad_evidence()` now key off each annotation's own
  `annotation_type`. `_bad_evidence` groups by **(text, type)** since the same string can be valid
  for one type and not another. The F5 advisory table gained an **Annotation type** column so a
  curator isn't left guessing which dropdown a flagged string was checked against. Module docstring
  rewritten to describe the per-type reality and name PMID:39787257 as the caught case.
- Tests: `tests/test_canto_config.py` — `validate_evidence_code` calls updated with a type arg;
  two new tests (`evidence_codes_for` discriminates by type — `IEA` valid generically but not for
  `molecular_function`; `Macroscopic observation (...)` valid for `pathogen_host_interaction_
  phenotype` but not `molecular_function`; `disease_name` has none). `tests/test_entry_queue.py` —
  `EvidenceCodeFlaggingTests.INVALID` changed to `"Disease severity index"` (genuinely invalid
  everywhere, generic and per-type); split the old "machine independent" test into one that still
  checks the generic catalog is base-vs-deploy-identical and a new
  `test_evidence_is_checked_per_annotation_type_not_globally`; fixed two tests that referenced the
  removed `_evidence_codes` name; fixed the near-match regression test (it had accidentally started
  asserting a *real* code produces no near match, once that code became correctly recognised as
  valid).
- Verified: `test_canto_config.py` + `test_entry_queue.py` + `test_export_docx.py` = 92/92 green;
  full repo suite 626/626 (one unrelated failure along the way — this session's own
  `Session-Logs-INDEX.md` row exceeded the 40-word cap `phiweaver.session_index` enforces; shortened
  it, see the entry for this session). Regenerated the real PMID:39787257 queue: both `Macroscopic
  observation (...)` rows in F3 lost their `⚠`, and the F5 advisory section is gone entirely (no
  bad evidence strings left in this draft).
- **Not committed** — code, tests, and the regenerated queue/docx are all in place but the user
  had not yet said to commit by the end of this session.

## Decisions
- **"Sandbox" was ambiguous and worth resolving by investigation, not by asking** — the paper's own
  history (FAQ + 2026-07-18 log) made "re-run the verified E2E harness" the reasonable first read;
  the user's later correction ("just need the entry queue file") showed the simpler, more direct
  path was actually wanted, but the leakage-control build-out wasn't wasted effort — it surfaced
  that two on-disk files were themselves undisclosed curation records, a real hygiene gap in the
  literature tree independent of this session's outcome.
- **Fix the extensions bug rather than just explain it** — user said "fix now"; scope was kept to
  wiring in an already-written, already-imported helper plus a column, not inventing new
  extension-rendering logic.
- **Did not backfill strain/background on this draft** — applied then reverted at the user's
  request. Unlike the 2026-07-26 session's reason for *not* backfilling elsewhere (deriving a
  parent strain from a genotype name would be a guess D19 refused), the values here were not
  guessed — PH-1/IPO323/Bobwhite/Riband are explicit in the paper and the gold standard — so the
  revert reflects the user's preference for this exchange, not a data-quality objection.
- **Re-verified from the source config rather than defending the first answer.** When corrected,
  the response was to `grep` both YAML files directly and trace exactly which key `_evidence_codes`
  actually read, rather than re-asserting the original claim or hedging. The wrong answer traced to
  a real, pre-existing, previously-untested architectural assumption (one global evidence-code
  list), not a one-off slip — worth fixing at the source, not just correcting the one example.

## Open items
- **The two stray curation-record files in `PHI-Canto-Literature/`** (`completed/2026-05-17-
  39787257-FgKnr4-practice.md`, `archive/PMID39787257-Kroll-2025-PHI-Canto-Curation.md`) sit
  alongside the gold-standard example with no labelling that distinguishes "paper text" from
  "someone's prior curation attempt" — this is exactly what makes ad hoc leakage control necessary
  every time this PMID (or similarly duplicated papers) is used for a blind run. Worth a
  triage/labelling pass if the E2E harness is going to be re-run regularly.
- **`PMID39787257-FgKnr4-phiweaver-DRAFT.md` still has no `background`/`strain` fields** — the six
  coverage warnings are back; fixing them (with the exact values worked out in §6, not guessed) is
  available whenever wanted.
- **`_fmt_extensions()`'s output format** (`relation=value`, space-free, `·`-joined) matches the raw
  relation names the curation-example library already uses in its own Extension columns — not
  Canto's fancy "Canto display text" (e.g. "observed in organ"). Deliberately kept simple/consistent
  with existing convention rather than adding a new label-lookup layer; revisit only if a curator
  finds the raw relation names unclear at the keyboard.
- **The evidence-code fix is uncommitted.** `canto_config.py`, `entry_queue.py`, and both test
  files carry real, tested, uncommitted changes — needs `git add`/`commit`/`push` on request.
- **Other consumers of `canto_config.validate_evidence_code`/`.evidence_codes` were not audited
  beyond this repo's own tests** — the signature change (now requires `annotation_type`) is a
  breaking API change for any caller outside `entry_queue.py`/the test suite; none found by `grep`,
  but worth a second look if a new module starts using evidence-code validation.

## Lessons
- **A network sandbox restricts writes, not reads** — `benchmark-sandbox.settings.json`'s
  `filesystem.allowWrite` is the only filesystem control; leakage control for a blind run still has
  to be done by hand (move the answer off disk), exactly as the 2026-07-18 session already noted
  but easy to reach for the settings file alone and assume it's enough.
- **A file's name/location doesn't guarantee its content type** — `*-practice.md` in `completed/`
  and a `*-PHI-Canto-Curation.md` in `archive/` both read, at a glance, like they could be paper
  text or reference material; both were actually curation records. Worth opening and checking
  frontmatter `type:` before trusting a file as a blind-run input.
- **Dead code that's already imported is an easy miss** — `_fmt_extensions` being imported but never
  called was the exact shape of bug that silent-drop bugs take: no error, no warning, just data
  that quietly never reaches the output. `grep` for actual call sites, not just imports, when
  auditing "is X actually used."
- **Applying a fix and then being told to revert it is cheap when the data lives outside git** —
  the strain/background edit and its revert never touched a tracked file, so there was no commit to
  undo, only the working file and its regenerated derivatives.
- **Verifying "is X in the list" is only half the check — "is it the right list" is the other
  half.** The first evidence-code answer failed exactly there: `_evidence_codes()` was checked
  successfully, correctly, and against the wrong thing. A user's outside knowledge (a real field
  they'd seen on the PHI-base website) is exactly the kind of fact offline config-reading can't
  substitute for — worth treating a domain-expert correction as a reason to re-derive from source,
  not just re-run the same check more carefully.
- **A wrong assumption baked into a test's own fixture data hides itself.**
  `EvidenceCodeFlaggingTests.INVALID = "Penetration assay"  # ... not a code` had been green for
  weeks because the test only proved *some* string got flagged, never that the string was actually
  supposed to be invalid. Fixing the real bug is what surfaced the test was quietly wrong too.

## Commits
- `89a0548` — Render annotation extensions in the canto entry queue, not just compared_to_control
  (pushed: `c6bf441..89a0548`)
- Evidence-code per-type fix (`canto_config.py`, `entry_queue.py`, `test_canto_config.py`,
  `test_entry_queue.py`) — **not yet committed**.

92/92 across `test_canto_config.py` + `test_entry_queue.py` + `test_export_docx.py`; 626/626 full
repo suite (after fixing this session's own index-row cap violation).
