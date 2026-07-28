---
created: 2026-07-25
type: session-log
tags: [status/complete]
project: PHI-Canto transport decision (D18) + PHI-base duplicate check at triage + full backlog triage + a profiled gate fix
summary: Started as "design a Playwright-assisted PHI-Canto entry plan" and ended by rejecting browser automation on measured arithmetic (D18). On the way, found the routes doc named the wrong script — `canto_load.pl` cannot create sessions; `canto_add.pl --sessions-from-json` can, and carries genes/alleles/genotypes but not metagenotypes or annotations — which changes Route 2 from "the durable target" to "a scaffold on top of Route 1, permanently". Built `phibase_index.py` so triage asks whether PHI-base already holds a paper (the trigger paper was already PHI:132). Triaged all 31 open backlog items: closed 3 as already-shipped, undid a duplicate entry I had created the day before, promoted open work hidden inside a closed item. Finally profiled the slow gate: the backlog blamed ontology parsing, but the real cost was `git_commit()` shelling out per render — 57.5s → 34.0s. Six commits pushed.
---

# Session: the plan that argued itself out of existence

## Recap

Asked for a **Playwright-assisted PHI-Canto entry plan**; ended by **rejecting browser automation** — the premises didn't survive checking. **The routes doc named the wrong script:** `canto_load.pl` loads **reference data only and cannot create a session**; the real route is **`canto_add.pl --sessions-from-json`** — and it carries session/genes/alleles/genotypes but **NOT metagenotypes or annotations**, so Route 2 is a *scaffold on top of* Route 1 and **the entry queue is permanent, not an interim MVP**. (Also: `canto_export.pl` is one-way out, `pombase-import.pl` targets **Chado**, `canto_merge.pl` merges *people*.) Error corrected in **3 files** (`4167dab`). The proposed "Stage 1" was **already shipped**. The curator proposed the strongest Route 3 — **supervised one-step prefill** (curator drives, bot fills one screen, never commits); it survives the brittleness objection *and* preserves "entry **is** validation", and still lost on arithmetic: ~30–40 min/paper of entry vs **60–100 h to build → break-even ≈ 150–250 papers**, and **typing isn't the bottleneck** (accession resolution, hand-scoring, PHIPO gaps, evidence rulings are). Recorded as **D18** + FAQ + backlog (`f5ce6f5`), *including the rejected design* so a revival doesn't rebuild the worse autonomous version, the two hazards (**bind the term ID not the label**; **automation complacency launders machine error as curator approval**) and a **falsifiable reversal test**. **Built `phibase_index.py`** (`ff0b27c`, 20 tests, network-free): triage step 1 now asks whether PHI-base already holds the paper — the 2026-07-24 trigger paper **is PHI:132**, and its record gives pathogen **taxid 318829** *M. oryzae*, the taxon the draft got wrong. Pinned to **`phi-base_v4-19_2026-03-25.csv`** (24,122 records / **5,994 PMIDs**) from PHI-base/data; reports accession + gene + taxon + host + phenotype as a **cross-check, not a bare flag**. Four live-data quirks handled: the CSV **repeats its header as row 1**, the PMID column was **renamed** (`PMID`→`Literature_ID`), case-variant `Literature_source`, and **one PMID with 709 records** (truncate + summarise). Record link **probed not guessed** (http-only; test pins the scheme); a miss **never claims "uncurated"** (releases exclude live PHI-Canto sessions; 61 records cite no PMID). **Triaged all 31 open backlog items:** closed **3** already-shipped (both token items + PMC/JATS, `a411880`/`a8553b4`), **undid a duplicate entry I created the day before** — a **stale *title* on a closed item manufactures duplicate work**, worse than a stale checkbox — and **promoted open work hidden inside an `[x]` entry** (PPR preprints + author-manuscript check). Verified-and-left-open: `CITATION.cff` omissions are *deliberate*, YAML parses, `gh api` now reports **MIT/public**. Finding: **five entries are ~two emails** (James ×3, Hsin-Yu ×2) and unblock a sixth. **30 open / 16 done.** Finally **profiled the slow gate** (`cf3e375`): the backlog blamed ontology re-parsing, but **no test spawns a subprocess** so `lru_cache` already parses each `.obo` once (**~0.2 s for all of it**) — `cProfile` found **7.49 s of 8.17 s** in `test_entry_queue` going to **`git_commit()` → `subprocess.run`, 20× at ~330 ms** on the 9p mount. `@lru_cache` on `common.git_commit` → **suite 22.1 s → 12.1 s, gate 57.5 s → 34.0 s (~41%)**, 8/8 green, suite **490 → 517**, `tests/test_common.py` pins the call count. **Lesson: profile before optimising a guess — the item was wrong by 30× and in the wrong place.** Open: the **server-access ask to James was never sent**; it now decides only *how much* the curator clicks. All pushed through `cf3e375`.


The ask was a work plan for Playwright-assisted biocuration entry into PHI-Canto. Answering it
honestly meant checking the premises first, and the premises did not survive: one document named the
wrong script, one proposed stage was already built, and the arithmetic said the automation wasn't
worth building at all. What came out instead was a recorded decision, one small tool that pays for
itself immediately, and a much shorter backlog.

## Objectives
- Critically assess a proposed roadmap for Playwright-assisted PHI-Canto data entry.
- Fix whatever the assessment exposed; record the decision so it isn't re-litigated.
- Then: triage the backlog, and take the easy wins it turned up.

## Work done

### 1. The Canto transport assessment → D18

**Three findings killed the roadmap as written.**

- **Its "Stage 1" was already shipped** — the entry queue, the `canto` blocks, `--validate`,
  `canto_config`. Building it would have redone 2026-07-07/08.
- **`docs/CANTO-SUBMISSION-ROUTES.md` named the wrong script.** It said an admin runs
  `canto_load.pl` to create sessions. Verified against the sources: `canto_load.pl` loads
  **reference data only** (genes, organisms, strains, ontologies, PubMed XML) and *cannot create a
  session*. The real route is **`canto_add.pl --sessions-from-json <file> <curator_email>
  <default_taxonid>`**, format documented on the pombase/canto wiki.
- **That import format stops where the work starts.** It covers session/publication, genes, alleles,
  genotypes (incl. diploids) and notes — **not metagenotypes, not annotations**. So Route 2 builds
  the scaffold and Route 1 is *permanent*, not an interim MVP. Also corrected: `canto_export.pl` is
  one-way out, `pombase-import.pl` targets Chado (downstream, not back into Canto), and
  `canto_merge.pl` merges *people*, not sessions.

**Then the curator proposed the strongest form of Route 3** — supervised one-step prefill: the
curator drives, Playwright fills one wizard screen, the curator clicks every Next and the final
Finish, the bot never commits. That shape *does* survive the brittleness objection (a broken selector
degrades to typing) and it preserves the "biocurator entry **is** the validation step" model that
bulk import would destroy. It was worth taking seriously, and it still lost on the numbers.

**The arithmetic (D18).** ~1 min per annotation → ~30–40 min of mechanical entry per paper; prefill
might halve it, against **60–100 h** to build. **Break-even ≈ 150–250 papers.** And the stronger
argument: **typing is not the bottleneck** — the live blockers are accession resolution, hand-scoring,
PHIPO gaps and evidence rulings, all judgement. The entry queue already took the big win by removing
the *"what do I enter next"* thinking; Route 3 competes for the residual keystrokes.

Recorded as **D18** in `DESIGN-DECISIONS.md` (siblings D14/D16 cover the Route-1 renderers), with the
backlog item as working summary and a FAQ entry as the lookup. Deliberately recorded *the rejected
design in detail*, so a revival doesn't rebuild the worse autonomous version, plus the two hazards
found while designing it: **bind the term ID, not the label** (Canto's autocompletes are
server-backed; verify the bound ID or you get a plausible sibling term) and **automation complacency
degrades provenance** (after ~30 correct fills a reviewer rubber-stamps, and a machine error ships
with a human's approval attached). D18 states a **reversal test** — hundreds of papers of recurring
throughput, or a measured baseline — so it can be overturned by evidence rather than argument.

### 2. `phibase_index.py` — does PHI-base already hold this paper?

The 2026-07-24 curation of PMID:9927411 never asked. It should have: the paper is **PHI:132**
(ABC1, O13407) and the established record gives the pathogen as **taxid 318829** *M. oryzae* — the
taxon the draft got wrong (it used *P. grisea*, 148305).

`python3 -m phiweaver.lookup.phibase_index <PMID>` indexes a pinned release from
[PHI-base/data](https://github.com/PHI-base/data) and reports the accession, gene, pathogen taxon,
host, phenotype and a verified record link — a **cross-check**, not a bare duplicate flag. Runs as
**step 1 of `paper-triage`**, before conversion. Pinned to `phi-base_v4-19_2026-03-25.csv`:
24,122 records, **5,994 distinct PMIDs**.

**Four things the live data forced**, none of which a design-on-paper version would have caught:
- the CSV **repeats its header as its first data row** (a naive parse yields a phantom record whose
  every field is a column name, and a phantom PMID of `"PMID"`);
- the PMID column was **renamed** — `PMID` up to v4-08, `Literature_ID` since — so both spellings
  are accepted;
- `Literature_source` has case variants (`Pubmed`/`PubMed`/`pubmed`);
- **one PMID carries 709 records** (a genome-scale *F. graminearum* paper), so the first draft would
  have printed ~4,000 lines; hits now list 5 and summarise the rest.

The record link (`http://www.phi-base.org/searchFacet.htm?queryTerm=PHI:132`) was **probed, not
guessed** — and is http-only, since https doesn't answer. A test pins the scheme. A miss never claims
a paper is uncurated: releases exclude in-progress PHI-Canto sessions and 61 v4-19 records cite no
PubMed ID, both printed with every miss. 20 tests, network-free via an injectable `fetch` — one
initially hit the network and was caught in the verbose output.

### 3. Backlog triage — read all 31, checked each claim against the code

- **Closed 3 as already delivered**, all the same failure: every follow-up struck through as done,
  no box ticked. **Per-article token attribution** (SKILL step 7 + `CANONICAL_DB`), **persisted token
  history** (`article_token_costs`, `PRICES`, `--history`, registry section, `daily_curation tokens`),
  and the **PMC/JATS** item (shipped in `ebd73af` three days after being written).
- **Undid my own duplicate.** The PMC work already had a thorough `[x]` entry whose *title* wrongly
  said part (a) was outstanding. I read the title, believed it, and opened-and-closed a second entry
  for the same work — which also silently dropped two open questions the older entry recorded. Fixed
  the title, removed the duplicate. **A stale title on a closed item is worse than a stale
  checkbox: it manufactures duplicate work.**
- **Promoted open work out of hiding.** That closed entry contained "**Still open:** … `source=PPR`
  preprints … and the author-manuscript check". Open work inside an `[x]` entry is invisible to
  anyone scanning checkboxes; it now has its own item.
- **Verified and correctly left open:** `CITATION.cff`'s omissions are *deliberate and documented*,
  the YAML parses, and `gh api` reports `license: MIT, visibility: public` — so that item's alarming
  premise (public, no license, all rights reserved) is resolved and only external parts remain.
- **Triage finding:** five entries — the three Canto-config follow-ups for James, Hsin-Yu's D1–D4
  clarifications, and the term-design line — are **~two emails, not five projects**, and they unblock
  a sixth item that is explicitly sequenced after the ruling.

**30 open / 16 done** (from 31/13).

### 4. The slow gate: a misdiagnosis, corrected by profiling

The backlog blamed the ~45 s gate on re-parsing the bundled `.obo` files "per test process, across
30 test modules". **Measured, that premise is wrong:** no test file spawns a subprocess, so
`unittest discover` runs in **one** process where the existing `lru_cache(maxsize=1)` already parses
each ontology exactly once — and it's cheap (`phipo-base.obo`: 61 ms read + 28 ms parse, 1327 terms;
**~0.2 s for all of it**). A disk cache would have saved nothing and added an mtime-invalidation bug
surface.

`cProfile` found the real cost: `test_entry_queue` spent **7.49 s of 8.17 s** in
`render_entry_queue` → `provenance_line` → **`git_commit()` → `subprocess.run`**, 20 times at
~330 ms each. Shelling out to git costs ~330 ms on the `z:` 9p mount, and every rendered entry queue
asks once.

Fixed with `@lru_cache(maxsize=1)` on `common.git_commit` — a process cannot meaningfully change
commit underneath its own provenance stamp, and a `None` (git absent, or the 5 s timeout tripped) is
now paid once instead of per render; `cache_clear()` covers a long-lived process that commits.

**Unit suite 22.1 s → ~12.1 s; full `smoke` gate 57.5 s → 34.0 s (~41%), 8/8 green.** The win exceeds
`test_entry_queue` alone because other modules render provenance stamps too. `tests/test_common.py`
(7 tests) pins the call count, so removing the decorator fails the suite rather than silently costing
10 s again. Suite **490 → 517**; HANDOFF's stale timings corrected.

## Commits (all pushed to `origin/main`)
| Commit | What |
| --- | --- |
| `4167dab` | Fix the Canto session-import script named in Route 2 (3 files carried the error) |
| `ff0b27c` | Check at triage whether PHI-base already holds the paper (`phibase_index.py`, 20 tests) |
| `a411880` | Close the PMC/JATS backlog item, shipped a month ago |
| `a8553b4` | Triage the backlog: close 2 done items, undo a duplicate entry |
| `f5ce6f5` | Record the PHI-Canto transport decision as D18 |
| `cf3e375` | Cache `git_commit()`; the slow gate was never the ontology parsing |

## Open items
- **Still the pivotal input:** server/admin access to canto.phi-base.org. It now decides only *how
  much* the curator clicks (whether Route 2 can import the scaffold), not whether the approach works.
  Needs James; the ask was never sent.
- **The ~two emails** identified in triage: James (private repos going public → a fresh clone falls
  back to pombase defaults that are wrong in both directions; the review-note feedback; whether
  `qc_do_not_manually_annotate` is missing from the config) and Hsin-Yu (D1–D4 clarifications; where
  the term-*design* line should sit). Cheapest movement on the board.
- **Deferred by choice** in `phibase_index`: auto-diffing a draft's `canto` block against the matched
  PHI-base record. The fields are surfaced for a curator to reconcile; nothing compares them.
- **Treat every performance claim in the backlog as a hypothesis.** §4 named a plausible culprit
  without measuring and was wrong by 30×. The 9p tax it blamed *is* real — it lands on process spawns
  and imports, not on parsing.
- Unchanged from before: the two accession blockers (URA5, FleQ/GcbB), hand-scoring the 10
  scorecards, gold-standard depth.
