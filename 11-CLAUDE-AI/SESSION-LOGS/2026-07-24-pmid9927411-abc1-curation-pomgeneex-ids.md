---
created: 2026-07-24
type: session-log
tags: [status/complete]
project: PMID:9927411 ABC1 curation via the PDF route + PomGeneEx IDs + two renderer/converter gaps it exposed
summary: Curated PMID:9927411 (Urban 1999, M. grisea ABC1) from the Europe PMC PDF — no XML exists for it — and reading the panels found Table II carries no mutant data at all, so the paper's headline "no drug hypersensitivity" claim rests on an author assertion; the curation exposed two engine gaps (PDF converter emitted no figures roster; entry_queue parked RNA-level annotations as termless) and prompted vendoring the seven PomGeneEx IDs, reversing the 2026-07-16 terms-only ruling. Six commits pushed. Also: `git stash` is now documented as unsafe on the z: mount after a `stash pop` half-wrote the index.
---

# Session: a 1999 scanned paper, and the three things it broke

Curating **PMID:9927411** — Martin's own first-author paper — turned out to be a good stress test
precisely because it is *old*. No Europe PMC XML, scanned print figures, tables the text extractor
flattens, and a headline claim whose supporting data is not actually in the table it cites.

## Objectives
- Curate PMID:9927411 into a PHI-Weaver draft **with figure inspection** ("with images").
- Fix whatever the curation exposed.

## Work done

### 1. The curation (work products in external `active/`, not committed)

**Route: PDF.** Europe PMC has no full text for this article — `/PMC1171144/fullTextXML` returns
**404** — so the free PDF (`?pdf=render`, 927 KB, 10 pp.) is the only machine-readable source.
Real text layer, no OCR needed. `source_route=pdf` recorded in the tracking DB.

Outputs: `PMID9927411-Mgrisea-ABC1-phiweaver-DRAFT.md`, the entry queue (`.md` + `.docx`),
converted markdown + report + 8 extracted images. **1 gene, 2 alleles, 9 metagenotypes,
11 enter-ready annotations, 2 parked, 17 flags.** Ledger `complete: true` — 6/8 figures
inspected, 2 declined with stated reasons.

Gene resolved to **UniProtKB:O13407** by cross-reference to the paper's own **EMBL:AF032443**;
length matches the paper's deduced 1619 aa exactly. TrEMBL, and it carries **no Function (CC)
annotation at all**, so nothing functional is citable from UniProtKB.

### 2. What reading the panels actually changed

This is the part that justifies the "with images" cost.

- **Table II shows no mutant data.** Its title promises Guy11 *and* AM25 *and* TF7-3131; the
  Results cite it for "no difference in drug sensitivities between abc1 mutants and Guy11".
  The printed table has **two numeric columns, EC₅₀ and MIC, and no per-strain columns** — every
  value is a wild-type reference concentration. That negative result is one of the paper's two
  headline claims (it's what separates Abc1 from Pdr5/Cdr1), and its supporting data is
  effectively "not shown". **All 13 candidate drug annotations parked.** Invisible at caption
  level; only visible on the rendered page.
- **Table I contradicts its own summary sentence.** Text: "we could not detect any significant
  difference". Conidiation: Guy11 **32 ± 10**, AM25 **70 ± 19** (×10⁴/ml) — ~2× with
  non-overlapping SDs, and **no statistical test is reported anywhere in the paper**.
  `PHIPO:0000080 normal asexual sporulation` **held**, not entered.
- **Figure 6 decided the term.** Table I gives a frequency (65% → 4% infection hyphae); the
  panels show the *extent* collapses too — a packed epidermal cell in wild type (6B) vs
  appressoria with nothing emanating (6C) and one sparse hypha in the rare success (6D). That is
  why `PHIPO:0000118` (decreased growth **after penetration**) fits and a penetration-failure
  term does not; 6A confirms melanised appressoria do form.
- **Figure 7B proves the allele is not a null**, and mislabels it. Guy11+CYH is a saturated blob,
  TF7-3131+CYH a faint but clearly *present* band — normal basal, crippled induction. Modelling
  `abc1-1` as null would misstate the paper's central claim. Its caption calls TF7-3131
  "*abc1-2Δ*"; it is *abc1-1*. Logged as a source error.
- **Tables I and II had to be re-read from pages rendered at 170 dpi** — the converter flattened
  them and lost the columns. Table I's "Appressorium formation >95%" row exists *only* in the
  rendered page.

**Also flagged, and the first thing a curator should read: this paper has no complementation
control.** AM30 is a *transformation* control (intact ABC1 + ectopic vector). What substitutes is
two independent alleles at the same locus plus co-segregation — strong for 1999, but a modern
requirement would bite. The growth-confound check, by contrast, **passes cleanly**: the mutants
grow, conidiate, attach and form appressoria normally, so the in-host defect is specific.

### 3. Three engine gaps the curation exposed

- **PDF converter emitted no `figures` roster** (`1ddfaec`, +4 tests). The JATS converter always
  has; the PDF side never did, so `figure_ledger` had nothing to audit a PDF-route ledger
  against — `missing`/`unknown`/`not_openable` were silently empty and `total_figures` fell back
  to counting the draft's own entries. **The draft got to define its own denominator.** An image
  whose caption can't be resolved now keeps its filename as the label rather than being dropped.
- **`entry_queue` parked RNA/protein-level annotations as termless** (`94e5e99`, +2 tests).
  `_park_reason` treated a blank `term_id` as "no ontology term resolved" for everything but
  `physical_interaction` — wrong for `wt_rna_expression`, whose term is a controlled phrase. A
  solid, figure-verified annotation was reported as carrying a defect it did not have. Passing the
  check wasn't enough on its own: with no table to render into it matched no section and
  **vanished** from the queue, which is worse than parked. Added **F6**; advisories F6 → F7.
- **PomGeneEx IDs vendored** (`5597729`, +6 tests). Curator supplied the seven IDs
  (`PomGeneEx:0000011`–`0000017`), **reversing the terms-only ruling of 2026-07-16**. Vendored as
  `data/pomgeneex.obo`, prefix registered in `validate_ontology_ids` resolving offline like
  `FYPO_EXT`. Prefix matching is now case-insensitive but reports canonical spelling, so
  `pomgeneex:0000011` round-trips rather than being shouted back as `POMGENEEX`.
  **Provenance limit recorded in three places:** no public PomGeneEx artifact was found, so the
  IDs are curator-supplied and unverified — the *phrases* have independent backing (Canto UI
  screenshot, 2026-07-11), the ID↔phrase *pairing* does not. RNA only; `PomGeneExProt` has no IDs.

### 4. QC fixes to the draft

- **ISS → TAS** on `GO:0140359`. ISS is inadmissible per team conventions #245/#246 (and is
  admin-only in this Canto config). TAS is itself borderline here — the "traceable statement" is
  the authors' own sequence analysis in the same paper — so it stays **held**, with dropping it
  offered as the cheaper option.
- **`wt_rna_expression`** given the controlled qualifier, then the ID.
- Flagged the free-text coverslip condition, and made the passing growth-confound check explicit
  rather than leaving it implied.

### 5. Documentation: stop the docs contradicting each other

- **`git stash` is unsafe on the z: mount** (`cee7afe`). `stash pop` applied the working tree then
  died with `fatal: Unable to write index`, after which `git status` reported **every tracked file
  as deleted**. Nothing was lost — commits intact, stash entry still present (`pop` drops only on
  success), all files on disk — and a plain `git reset` fixed it. The rule that matters is
  recorded: **never `git reset --hard` here**, because the tree looks catastrophic at exactly the
  moment the working tree holds the only copy of the un-stashed work. Use a scratch branch.
- **Commit-trailer instruction removed** (`b6b740a`). `HANDOFF.md` told agents to add a Claude
  co-author trailer the owner does not want, so an agent following the repo's own docs produced
  commits that then had to be stripped. Stated positively in **AGENTS.md §5** rather than merely
  deleted — a harness that adds the trailer by default needs an explicit "don't", not silence.
- **`HANDOFF.md` stops duplicating git rules** (`5eca842`). It kept its own copy and drifted from
  §5 **twice** — the trailer, then a branch/`--ff-only`-merge/delete dance where §5 says commit
  straight to `main`. Picking a winner line-by-line would have left the duplication that caused
  both, so the section now points at §5. The one useful detail it held — that
  `chmod .git/config.lock failed` is a **benign warning** — moved into §5, sharpened to
  distinguish it from the `fatal:` that means the index write really did fail.

## Commits (all pushed to `origin/main`)

| Commit | What |
| --- | --- |
| `5597729` | Carry PomGeneEx IDs on RNA-level qualifiers |
| `1ddfaec` | Emit a figures roster from the PDF converter |
| `94e5e99` | Stop parking RNA/protein-level annotations as termless |
| `cee7afe` | Warn against git stash on the z: mount |
| `b6b740a` | Drop the commit-trailer instruction |
| `5eca842` | Stop duplicating git rules in HANDOFF.md |

Green gate throughout: **suite 475 → 487**, smoke **8/8**.

## Open items
- ⏰ **Re-confirm the PomGeneEx ID↔phrase pairing in Canto.** It is flagged in three places but
  only stops being a caveat once someone has looked.
- ❓ **PMID:9927411 is very likely already in PHI-base** (foundational 1999 rice-blast paper). No
  lookup was done; reconcile before entering anything — especially the taxon decision and the
  allele type.
- ❓ **Taxon conflict**: O13407 is filed under *Pyricularia grisea* (taxid 148305) but Guy11 is a
  rice isolate — now *P. oryzae* (taxid 318829). Accession is right, species label is 1999-era.
  No `MGG_` ortholog was asserted, because none could be confirmed.
- ❓ **No complementation control in the paper** — curator ruling needed before entry.
- 🔧 **Ontology gaps logged**: no PECO for sakuranetin (the rice phytoalexin — the most
  interesting inducer in Figure 7A) or for 60 hours post inoculation; no PHIPO "normal growth on
  X" for 8 of the 13 tested compounds; no live term for spore attachment (PHIPO:0000184 obsolete).
- 🔧 `PomGeneExProt` protein-level IDs still unrecorded.
