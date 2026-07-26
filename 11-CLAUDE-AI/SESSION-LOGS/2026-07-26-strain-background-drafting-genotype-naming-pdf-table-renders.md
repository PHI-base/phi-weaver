---
created: 2026-07-26
type: session-log
tags: [status/complete]
project: Strain/background drafting + genotype naming enforced, then PDF tables captured as page renders
summary: Three backlog items closed by the same method — a ruling existed, nothing enforced it, so each got a schema field, a drafting rule and a lint. Strain/background became real draft fields with a four-case lint; PMID:9927411 lints clean while the other nine drafts flag 50 gaps, deliberately not backfilled because deriving a parent strain from a genotype name is the guess D19 refused. Genotypes were then renamed by allele across 22 structural references, and `paper_label` was added when the rename would otherwise have cost the curator the tie to Table I. The afternoon ran the PDF-table item through brainstorm → spec → plan → 6-task subagent execution: the root cause was **not** the extraction path but the caption regex accepting Arabic numerals only, so a paper numbering tables `I`/`II` reported zero and read as "no tables". `find_tables()` was measured at zero on that PDF and rejected on evidence. Two defects were caught that no unit test could — a hand-synced regex fragment that had drifted, and a config regression that broke the CLI outright. The in-body flat-text marker was built, found never to fire in production, fixed, then **withdrawn** on the curator's call: with the pointer working, 2 of 3 markers named the wrong page. 15 commits pushed.
---

# Session: the ruling exists, but nothing checks it

Three items in a row turned out to have the same shape. A curator ruling was on record, the
documentation was correct, and **nothing in the code or the drafting workflow enforced it** — so
drafts quietly disagreed with the standard they were written against. The fix each time was the
same three pieces: a field in the schema, a rule in the drafting skill, and a lint that fails when
the two drift apart.

The afternoon's PDF work looked different but ended in the same place: a feature is only real if
something checks it, and three separate checks agreed the flat-text marker worked while it had
never once fired.

## Objectives
- Work the backlog in order, closing whatever was unblocked.
- Where a ruling exists but nothing enforces it, close that gap rather than re-stating the ruling.

## Work done

### 1. Strain and background become real draft fields (`08acebf`)

The entry queue had read `strain` and `background` off genotypes since the 2026-07-25 ruling, but
**nothing defined or wrote them**: the fields were absent from `_TEMPLATE.md`, so PMID:9927411 had
been populated by hand and the other nine drafts rendered an empty strain column. Table A2 asks
Canto's first-screen question — a strain per organism, before any genotype can be created — and
could not pre-fill the answer.

Schema, drafting skill and a lint (`coverage.strain_background_warnings`) covering four cases: a
wild type with no `strain`, a mutant with no `background`, a mutant carrying a `strain` (the
isolate-label error the ruling exists to prevent), and any genotype setting both. It rides the
entry-queue CLI's existing stderr channel, so it fires on every generation rather than needing to
be remembered.

**Validated against curated data:** PMID:9927411 — the reference draft — lints **clean**; the other
nine flag **50 gaps**.

**Those 50 were deliberately not backfilled.** Filling them means reading each paper for the parent
strain, and deriving them from genotype names (`wild type PH-1` → strain `PH-1`) is exactly the
guess D19 already refused. The lint names each gap so a drafting pass can close it per paper.

**A stale line fixed in passing:** the skill's `#157` background vocabulary still read
`<gene>delta`, superseded by `<gene>modified` the day before — in the very file that writes the
value.

**Curator ruling, prompted by running the lint:** host **near-isogenic lines** (`tomato 76R
(Pto/Pto)`, `wheat Lr42-NIL`) trip the mutant test on their alleles. Ruled: **a NIL's parent
cultivar is a `background`** — a NIL is defined by its allele, and a *natural* allele is still an
allele. The lint's existing behaviour was already right, so **no code changed**; what was missing
was the written rule. *Corollary:* `wheat Lr42-NIL` records **no allele**, so it lints as a wild
type — the `AM30` shape again, except here the missing `Lr42` allele is the paper's entire subject.

### 2. Genotypes named by their allele, and a check that they are (`0dd2d5d`)

Same shape: the ruling said a mutant is named by its allele, it appeared only as a clause inside
the strain section, nothing checked it, and PMID:9927411 — the reference draft for this shape —
still called its mutants `AM25` and `TF7-3131`.

**The rename covered 22 structural references** (genotype `name`, metagenotype `name` and
`pathogen_genotype`, annotation `feature`). **Free text was deliberately left alone:** `conditions`
and `hold_reason` quote Table I's own rows ("Guy11 32 ± 10, AM25 70 ± 19"), so renaming there would
cut the tie to the paper. No `compared_to_control` value referenced either genotype.

**That tie is why `paper_label` exists.** The paper's figures and tables say `AM25`; a queue row
reading only `abc1-2Δ` cannot be reconciled with Table I — correct for Canto, useless at the bench.
The queue now prints `abc1-2Δ *(paper: AM25)*`. Without it this change would have traded one defect
for a worse one.

**The lint (`genotype_naming_warnings`) is the deterministic form of the rule**: a mutant's name
should contain one of its alleles' stems. Matching on the stem *or* the whole allele lets every
real shape pass — strain-prefixed (`Pta6605 ΔfleQ`), complementation (`SdhC1Δ-C` ← `SdhC1(ectopic)`),
multi-allele — and a genotype is flagged only when **no** allele matches, so an accidental
short-stem match is a miss rather than a false accusation. **Calibrated against all 14 drafts: 3
flags over ~50 mutant genotypes.** One false positive found that way (`Pt-Agro Pt31812(FL)-OE`,
where the name repeats the allele's bracket verbatim) is fixed and pinned by a test.

**Left open:** `Pta7375 WT` (PMID:41229162) is named a wild type but carries alleles — a second
isolate's wild-type strain modelled as an allele-bearing genotype. A modelling question, not a
rename.

### 3. PDF tables: brainstorm → spec → plan → subagent execution

The backlog item said the converter flattens tables and loses their columns, and proposed two
options. **Both premises turned out wrong.**

**The root cause was the caption regex, not the extraction path.** `^\s*(figure|fig\.?|table)\s*(\d+)`
accepts Arabic numerals only; the paper numbers its tables **Table I / Table II**. The converter
found 22 figure captions and **zero** table captions — it did not believe the paper had tables at
all — and reported `tables_found: 0`, which reads as "no tables" rather than "extraction failed".
**That silence is why the defect survived a full curation.**

**`find_tables()` was measured, not assumed:** zero tables across all ten pages (PyMuPDF 1.27.2).
The backlog guessed "unreliable on 1990s layouts"; the measurement is stronger. Rejected on
evidence.

**Whole-page renders, not caption-anchored crops** — a boundary heuristic that clips a row would
reproduce the exact defect being fixed. Curator decisions: a faithful image per table, whole page at
170 dpi, flattened text kept.

**Two defects were caught that no unit test could:**
- A shared `CAPTION_NUMBER` fragment was **duplicated into two modules with the trailing `\b` in
  only one** — my error in the plan. The extractor (the copy wired into the live pipeline)
  manufactured phantom tables from prose: `Table Legend is described…` → table `L`. Now
  single-sourced so it cannot drift again.
- `__init__` did `config or defaults`, so a caller-supplied config **replaced** the defaults; the
  new `table_render_dpi` key then broke the CLI and pipeline outright. Invisible to tests because
  every test constructs `PDFConvertSkill()` with no config.

**Verified on the real paper.** Table I renders legibly and its **"Appressorium formation (%) >95
>95 >95"** row — dropped entirely from the flattened text — is visible with all three strain
columns. Table II confirms the backlog's own claim: its columns are `Compound | EC50 | MIC` with
**no per-strain columns**, while its title names Guy11, AM25 and TF7-3131.

**Fact correction:** the paper has **three** tables, not two — `III` is the strains table in
Methods. Both the backlog and the spec had said two.

### 4. The marker that never fired, and why it was withdrawn (`f10ca71`)

The in-body warning marking flattened table text as unreliable **never fired in production**. Both
body generators append a whole page or section as *one* list element, and `CAPTION_BLOCK_RE.match()`
only matches at position 0, so a caption mid-page was never seen.

**Three separate checks said it worked, and all three were wrong the same way.** The unit tests
hand-fed a pre-split list with the caption as its own element; the wiring tests used synthetic pages
containing *only* a caption; my own end-to-end check did the same. Each put the caption at position
0 by construction. **A test that builds its input to match the implementation's assumption cannot
falsify that assumption** — the whole-branch review found it by reading the call sites instead.

**Fixing it showed the design was wrong rather than vindicating it.** With the pointer working, **2
of 3 markers on PMID:9927411 named the wrong page** (`Table II` → `Table-p9.png`; it is on page 7),
because the per-table page reference resolves through the over-detected caption list. A confident
pointer to the wrong page is worse than no pointer.

**Withdrawn on the curator's call**, in answer to "are we overengineering?" — **yes, and precisely
at the pointer**: it needed entry resolution, which needed correct detection, for a caution flag a
generic sentence would have carried. The regex de-duplication from the same fix wave was kept.

## Decisions
- **A NIL's parent cultivar is a `background`** (Martin Urban) — a natural allele is still an allele.
- **Caption over-detection deferred**, then **re-characterised**: it was called cosmetic, and the
  marker fix proved that wrong. It is only cosmetic again now the marker is gone.
- **The flat-text marker is withdrawn**, not deferred — component 4 of the spec is not delivered,
  and both the spec and backlog say so.

## Open items
- **Caption over-detection**: `Table N` matches anywhere in the text, so in-text references become
  captions — 11 mentions → 10 captions → 5 renders where 3 tables exist. Two spurious PNGs and
  inflated counts. **Why the obvious fix is wrong is recorded**: requiring punctuation after the
  number would break `Table S1 Primers used…`, and a missed table is invisible where a spurious one
  is obvious.
- **50 strain/background gaps** across the nine other drafts — needs the papers, not code.
- **`AM30` has a background but no allele**; `wheat Lr42-NIL` records no allele either.
- **`Pta7375 WT`** carries alleles while named a wild type — modelling question for the curator.
- Unchanged: the ~two emails to James and Hsin-Yun, still the cheapest movement on the board.

## Lessons
- **A ruling that nothing enforces is a ruling that drafts will disagree with.** Three items this
  session had correct documentation and non-conforming data.
- **Verify against the shape the caller actually passes.** Every marker test was written against a
  convenient input shape rather than the real one, and all of them passed.
- **Measure before choosing.** `find_tables()` and the "PDF is a legacy path" assumption were both
  wrong — the corpus is **17 PDFs against 2 JATS files**, so the PDF route is the main road.
- **The pointer was the overengineering, not the feature.** Value sat in detection, rendering and
  honest counting; the precise cross-reference introduced a dependency chain and a failure mode.

## Commits
15, `08acebf` → `f10ca71`, all pushed. Suite **537 → 591**; smoke 8/8 throughout.
