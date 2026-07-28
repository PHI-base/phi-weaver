---
created: 2026-07-25
type: session-log
tags: [status/complete]
project: Entry queue restructured to mirror PHI-Canto's UI (D19) + two curator rulings on strains and backgrounds
summary: Second session of 2026-07-25. A request to "make the queue look more like the web interface" turned into three bug fixes. Section F became one table per PHI-Canto annotation type using its own display names — which exposed that `host_phenotype` and `post_translational_modification`, 2 of the 12 types, had no section and **vanished** from the queue entirely. A saved session page supplied the real rendered column labels (the tables are JS-built, so a static fetch only sees the shell) and confirmed the config order is the render order. Validating the evidence column found that **5 of 8 evidence strings on PMID:9927411 are not valid PHI-Canto codes**, and that nothing in weaver calls `validate_evidence_code`. Then the docs revealed *Adding strains* is a **required** step the queue never prompted for, so table A2 was added; two curator rulings settled the model (wild types carry a strain, mutants carry a `Background` holding the parent strain plus the endogenous copy's status) and PMID:9927411 was populated as the reference draft. Seven commits pushed; suite 517 → 537.
---

# Session: the restyle that was three bug fixes

## Recap

Second session of the day. **"Make it look more like the web interface"** turned into **three bug fixes.** **Section F → one table per PHI-Canto annotation type** using its own `display_name`s from `canto_config`, empty sections omitted, numbering over those rendered (`857381d`). **That exposed data loss:** the old five-table grouping had **no section for `host_phenotype` or `post_translational_modification`** — 2 of the 12 types — so both were enter-ready, passed `_park_reason`, matched no table and **vanished from the queue**, the exact failure the F6 comment already named ("enter-ready and invisible is the one outcome worse than parked"). Verified by rendering *before* changing anything; both types have gold standards (PMID:23498959 carries both). **The durable fix is the backstop, not the two new tables:** an annotation whose type has no section is now parked with a reason, so a 13th type fails loudly. Display names **hardcoded, not read live** — the deploy config is gitignored, so config-driven headings would differ between this machine and a fresh clone; a test compares against the live config *when present* and skips otherwise. **The curator saved the session page into `active/`**, which gave the **rendered** tables a static fetch cannot reach (Canto builds them client-side — correcting the HANDOFF note: the page fetches, the tables don't). It **confirmed the config order IS the render order**, and corrected two things: the UI **capitalises the first letter** (`Pathogen phenotype`) and columns are **`Term name` + `Term ID`** separately, `Conditions` plural, `Figure` (`e5c9adb`). **Checking one column found another bug:** the drafted evidence values *looked* like Canto codes, so they were validated — **5 of 8 on PMID:9927411 are NOT valid `evidence_codes`** (`Penetration assay`, `Microscopy (cellular)`, `Macroscopic observation (…)`, …) while `Cell growth assay`/`Northern assay` are. Column therefore **stays `Evidence summary`**, not Canto's `Evidence code` (physical interaction excepted, its evidence genuinely being a code). **Root gap: nothing in weaver calls `validate_evidence_code`** — 82 codes parsed, validator unused, same shape as the annotation-type gap closed 2026-07-21. **Open.** **The docs then revealed *Adding strains* is REQUIRED** — one or more per **every** organism before any genotype, "strain" covering pathovars and **cultivars** — and the queue never prompted for it, so a curator could reach the genotype stage and be blocked. **Table A2** added (`32959a4`), one row per organism, role from **metagenotype use not the species name**, placed *inside* A because Canto's strain picker is on the **same page** as gene entry (two anchors, one page) — which also avoided renumbering C–G, landmarks for a dozen tests. **Two curator rulings:** (1) **only a wild type carries a strain; a mutant is named by its allele** — `Guy11` = strain, `AM25`/`TF7-3131` = the `abc1-2Δ`/`abc1-1` genotypes (`3f88ac8`); then **`AM30` proved "has alleles" insufficient** (an insertion mutant in Guy11 that the draft listed with *no* alleles, so it was still offered as a strain), resolved by (2) **a mutant's parent strain goes in `Background`** (`f5fa906`) — A2 now excludes on alleles **or** background, genotype tables gained Canto's `Strain`/`Background` columns, and a background with no allele renders **`⚠ no allele recorded`** rather than the previously wrong `wild type`. **A conflict was flagged not papered over**, then resolved: `#157` says background records the **endogenous copy's status**, the ruling said **parent strain** → **one field carries both**, and `#157`'s third form changed `<gene>delta` → **`<gene>modified`**, which matters because `delta` cannot describe an insertion mutant (`e82d64b`). **PMID:9927411 populated as the reference draft** (`0f261d7`): backgrounds for all three mutants, strain/cultivar for the four wild types, so A2 pre-fills; allele respelled **`abc1-2Δ`** across **12 occurrences** (prose tables and notes, not just JSON), JSON re-parsed and referential integrity re-checked; queue + docx regenerated. Recorded in **D19** + `PHI-Canto-Curation-Conventions.md` ("Strains and cultivars — wild type only"). Suite **517 → 537**, smoke 8/8. Open: evidence-code validation; genotype names still isolate labels (renaming cascades into metagenotypes + every annotation `feature`); AM30's missing allele; nothing yet *writes* strain/background during drafting. All pushed through `0f261d7`.


"Make it look more like the web interface and the headers in there" sounded cosmetic. Aligning the
entry queue to PHI-Canto's actual UI meant finding out what that UI says — and each time the real
labels arrived, they exposed something the queue was getting wrong rather than merely wording
differently.

## Objectives
- Restyle the entry queue's sections to match PHI-Canto's own headers.
- Follow wherever the real labels disagree with what weaver assumed.

## Work done

### 1. Section F: one table per annotation type (D19)

**The authoritative source was the config, not a guess.** `canto_config` already parses PHI-Canto's
`available_annotation_type_list`, which carries a `display_name` per type — `GO molecular function`,
`pathogen-host interaction phenotype`, `protein modification`, `Wild-type RNA level`, … So section F
went from five hand-grouped tables (`F1. GO annotations`, `F3. Pathogen phenotype`, …) to **one
section per type in the config's order**, empty ones omitted and numbering running over those
actually rendered.

**The bug this exposed.** The old grouping had **no section for `host_phenotype` or
`post_translational_modification`** — 2 of the 12 types. Both were enter-ready, passed
`_park_reason`, matched no table and **disappeared from the queue**, which is exactly the failure
the F6 comment already named: *"enter-ready and invisible is the one outcome worse than parked."*
Verified by rendering before changing anything — a `host_phenotype` annotation with a resolvable
subject produced no output at all. Both types have gold-standard examples (PMID:23498959 carries
both), so real curations hit it.

**The durable fix is the backstop, not the two new sections.** Any enter-ready annotation whose type
has no section is now parked with `no entry-queue section for annotation type '<x>'`, so a 13th type
fails loudly instead of vanishing. Adding only the two missing tables would have left the trap.

Display names are **hardcoded, not read from `canto_config` at render time**: the deploy config is
gitignored, so config-driven headings would differ between this machine and a fresh clone — two
curators, two shapes of queue for one paper. The cost is drift, paid back by a test that compares
against the live config **when the deploy file is present** and skips when it is not.

### 2. The saved session page, and the evidence-code find

`WebFetch` reached the read-only session URL (correcting the HANDOFF note — the *page* fetches, its
**tables do not**, because Canto builds them client-side). The Help docs gave workflow terminology;
then the curator saved the gene page into `active/`, which finally gave the **rendered** tables.

It **confirmed** the section set and order exactly — the config order *is* the render order — and
corrected two details: the UI **capitalises the first letter** (`Pathogen phenotype` where the config
stores `pathogen phenotype`, applied at render time so `ANNOTATION_SECTIONS` stays a verbatim copy),
and the columns are **`Term name` + `Term ID` as two columns**, `Conditions` plural, `Figure`.

**One column deliberately keeps weaver's wording, and checking why found a bug.** Canto heads that
column `Evidence code`; the drafted values *looked* like codes, so they were validated against the
config's 82 `evidence_codes` rather than trusted. On PMID:9927411 **5 of 8 distinct evidence strings
are not valid codes** (`Penetration assay`, `Microscopy (cellular)`, `Macroscopic observation
(quantitative observation)`, `Asexual sporulation assay`, and one more) while `Cell growth assay` and
`Northern assay` are. So the column stays **`Evidence summary`** — labelling prose as a code would
tell a curator a cell is ready to paste into a controlled field when it is not. `Physical
interaction` is the exception, its evidence genuinely being a code there.

**The underlying gap: nothing in weaver calls `validate_evidence_code`.** The only grep hit in the
repo was the docstring written minutes earlier. `canto_config` parses all 82 codes and exposes a
validator that no drafting or QC path uses — the same shape as the annotation-type gap closed on
2026-07-21. **Left open.**

### 3. Table A2: the required strain step the queue never had

The docs revealed *Adding strains* is **required**: one or more experimental strains for **every**
organism before any genotype can be created, with "strain" covering subspecies, varieties, pathovars,
**cultivars** and strains proper. The queue had no prompt for it, so a curator could reach the
genotype stage and be blocked.

A2 lists one row per organism with its pathogen/host role, derived from **metagenotype use, not the
species name**. It sits inside section A rather than earning a letter because Canto's strain picker is
on the *same page* as gene entry (`#adding_genes_and_organisms` and `#adding_strains` are two anchors
on one page) — which also avoids renumbering C–G, used as landmarks by a dozen tests and the reviewer
guide.

### 4. Two curator rulings, and what they broke

**Ruling 1 — only a wild type carries a strain; a mutant is named by its allele.** `Guy11` is the
strain; `AM25` and `TF7-3131` are the `abc1-2Δ` and `abc1-1` **genotypes** and carry no strain.
A2 now excludes allele-bearing genotypes entirely.

**Then `AM30` proved the test insufficient.** It is an insertion mutant in wild-type Guy11, but the
draft listed it with *no alleles*, so it was still being offered as a strain candidate beside Guy11.
"Has alleles" cannot decide wild type on its own.

**Ruling 2 — a mutant's parent strain goes in `Background`**, which resolved it: A2 now excludes on
alleles **or** a background. Genotype tables gained Canto's `Strain` and `Background` columns, and a
genotype with a background but no allele renders **`⚠ no allele recorded`** instead of the previously
wrong `wild type` — that is a mutant whose allele the draft failed to capture, exactly AM30's ectopic
insertion.

**A conflict was flagged rather than papered over**, then resolved by the curator: the team's `#157`
rule says a background field records the **endogenous copy's status**, while the ruling put the
**parent strain** there. Answer: **one field carries both**, and `#157`'s third form changed from
`<gene>delta` to **`<gene>modified`** — which matters, because `delta` could not describe an
insertion mutant like TF7-3131. Both written into
`07-Standards/PHI-Canto-Curation-Conventions.md`.

### 5. PMID:9927411 populated as the reference draft

Backgrounds for all three mutants (`Guy11; endogenous ABC1 absent` / `Guy11; ABC1modified` /
`Guy11; endogenous ABC1 present`) and strain/cultivar for the four wild types (`Guy11`, `Sariceltic`,
`CO-39`, `Golden Promise`), so A2 pre-fills for all three organisms. The allele `abc1-2delta` was
respelled **`abc1-2Δ`** — **12 occurrences**, in the prose tables and curator notes as well as the
JSON — per the Δ-suffix convention. JSON re-parsed and referential integrity re-checked afterwards.
Queue + docx regenerated.

## Commits (all pushed to `origin/main`)
| Commit | What |
| --- | --- |
| `857381d` | Section F mirrors PHI-Canto: one table per annotation type (+ the vanishing-types fix) |
| `e5c9adb` | Match PHI-Canto's column labels and capitalisation |
| `32959a4` | Add table A2: the strain step the queue never prompted |
| `3f88ac8` | Strains: wild type only, per the curator ruling |
| `f5fa906` | Add Background: a mutant's parent strain, per the curator ruling |
| `e82d64b` | Background carries parent strain plus endogenous status |
| `0f261d7` | Record PMID:9927411 as the reference draft for strain/background |

## Open items
- **Nothing validates evidence strings against `canto_config.evidence_codes`** — 5 of 8 wrong on one
  paper, and the validator exists unused. Needs a decision: park the annotation, or flag it in the
  queue? The most concrete remaining UI mismatch.
- **Genotype names still use isolate labels.** By ruling 1, `AM25` should be the `abc1-2Δ` genotype.
  Renaming cascades into metagenotype names and every annotation's `feature`, so it wants one
  deliberate pass.
- **`AM30` has a background but no allele** (`⚠ no allele recorded`). Its ectopic vector integration
  is a real allele the draft never captured; `#157` points at allele type `ectopic expression`.
- **Nothing yet *writes* `strain` / `background` during drafting** — PMID:9927411 was populated by
  hand. The other nine benchmark drafts still render `—`.
- **Setup section headings A–E keep weaver's imperative wording** ("Create pathogen genotypes") rather
  than the session page's record wording ("Genotypes from this publication"). Deliberate: the queue is
  a worklist, not a report. Revisit only if a curator disagrees.
- Carried over: the server-access ask to James is still unsent; the ~two emails from the earlier
  triage remain the cheapest movement on the board.
