---
created: 2026-07-17
type: session-log
tags: [status/complete]
project: PHIPO PR workflow + offline PHIPO lookup + species-neutrality
---

# Session: PHIPO term-request PRs, offline PHIPO lookup, species-neutrality

Second session of 2026-07-17 (follows the GO-ruling / gap-ledger / context-guard log).

## Objectives
- Act on James Seager's two emails: stop filing PHIPO term-request *issues*, open *PRs* against
  `phipo-edit.owl` for pattern-extension terms.
- Then, driven by the user's questions: can weaver suggest missing PHIPO terms during curation?
  Should PHIPO lookup go local? Fix the scorer. Apply curator rulings on two open issues.

## Work done

### PHIPO term-request as a PR — issue #452 → phipo#454 (commit d48cb36)
- Cloned **PHI-base/phipo** to `/mnt/z/Computer/GITHUBrepositories/phipo`. Direct clone onto `/mnt/z`
  fails (git tries to set `core.filemode=false`, chmod on `.git/config.lock` fails) — **clone on the
  native fs, copy across, then edit `.git/config` directly**. PRs target **`master`**; CI runs the
  full ODK QC, so **no local `robot`/ODK needed**.
- **The finding that reshaped the request:** the term #452 asked for (free-living "absent DON")
  **already existed** as `PHIPO:0000503`, obsoleted in the 2019 refactor and never re-created. OLS
  *search* hides deprecated terms, so #452 was written blind to it. It is an **oversight, not a
  decision** — pyocyanin (`PHIPO:0001033`) and gliotoxin (`PHIPO:0001105`) both kept their "absent
  from cell" terms under `PHIPO:0001034`; DON's were re-created in 2025 but "absent" was missed.
- Opened **[phipo#454](https://github.com/PHI-base/phipo/pull/454)** adding `PHIPO:0001456`
  "deoxynivalenol absent from cell", patterned verbatim on `PHIPO:0001033`. CI green, mergeable,
  awaiting James. `created_by: martin2urban`. Left for James: the ID (no personal range in
  `phipo-idranges.owl`) and whether `PHIPO:0000503` should get a `replaced_by` pointer.
- **The general lesson (`obsolete-terms-are-fossils` memory + skill step 5):** before calling a
  missing sibling a gap, look for an **obsoleted** term with that meaning, then run the
  **parallel-terms test** — if the sibling concepts kept the dimension it's an oversight (fill it);
  if they all dropped it, that was a decision and re-creating it silently reopens it.

### Backlog groundwork for the PR workflow (commits ba937d4, 7709ce7, 3b58834)
- Skill extended with **two routes**: pattern extension → PR; everything else → evidence-only issue.
- **Open question for Hsin-Yun (backlog):** PHIPO's own `CONTRIBUTING.md` asks requesters for
  "label, definition, references, position in hierarchy" — so the skill's "evidence, not design"
  guardrail is *stricter than the ontology team's own rule*. Not resolved; for her.
- **New backlog item:** curator-triggered term-**design** proposals → GitHub issue (the case the
  two-route skill does not cover — an explicit trigger makes the output a *proposal*, not an
  assertion, so the guardrail survives). Sequenced after the design-scope ruling.

### Offline PHIPO lookup (commits 79f0754, f9b7890)
- **Vendored `phipo-base.obo`** (release 2026-03-12, 1327 terms / 210 obsolete). Both
  `map_phenotype` and `validate_ontology_ids` now resolve `PHIPO:` **offline**; **OLS dropped for
  PHIPO, kept for GO**. Verified it is not a downgrade — OLS served the same release (`PHIPO:0001455`,
  created June, absent from both). Four-edit change in `validate_ontology_ids` thanks to the existing
  `_validate_offline` helper — modularity paying off.
- **Two files, never conflated:** `phipo-base.obo` = the **release** (what a curator can annotate);
  `phipo-edit.owl` = the **working file** (unreleased terms, gap analysis only). Enforced by a test:
  `PHIPO:0001456` (our own PR term) correctly validates **not_found**.
- Wins: `--include-obsolete` surfaces deprecated terms flagged (reproduces the whole #452
  investigation in one call); every search prints the `data-version`; the benchmark sandbox needs
  **no PHIPO exception** (a bundled file needs no network — and `github.com/PHI-base` hosts *both* the
  ontology and the answer-key data repos, so "ontology yes, data no" can't be a domain rule).
  **PHIPO is a tool, not an answer.**

### The scorer could not return `no_match` — a real bug (commits f9b7890, d08946e)
- The scorer first borrowed from `map_condition` (exact > substring > Jaccard) let one shared
  **generic** token carry a match ("to" is in 39% of PHIPO labels), and its label-inside-query tier
  let the one-word label "phenotype" match any query containing that word. **`no_match` was
  unreachable — and `no_match` is what gap detection and `--log-gaps` key on**, so gap detection was
  silently broken.
- Fixed with **IDF weighting** (score = how much of the query's *information* a term covers) +
  `MIN_SCORE`, tuned empirically: true matches 35–100, prose/junk 0–12.7. Extracted to shared
  **`text_score.py`**. `map_condition` had the same bug in milder form (PECO is a flatter corpus) and
  is now fixed too — its `★` also wrongly meant "ranked first", now "exact". Both thresholds tuned
  independently, both landed on 20.0, kept as separate constants.

### PHIPO is species-neutral — L8, and a false gap corrected (commits 5b0957f, b18e0a7)
- Curator point, verified against the file (its header: *"Ontology of species-neutral phenotypes…"*):
  `conidiation`, `conidia`, `appressorium`, `haustorium`, `sclerotium`, `mycelium`, `ascospore`,
  `urediniospore` have **zero** primary-label hits. PHIPO says `asexual spores`, `hyphae`,
  `pathogen penetration structure`. The species vocabulary lives in **EXACT synonyms** (35 `conidi*`),
  so the search still finds it; only the process noun `conidiation` is absent outright.
- **Two systematic retries before ever calling a gap:** species-specific → species-neutral, and
  process noun → entity noun (for presence/absence PHIPO models the **entity** — `asexual spores
  absent` — never the process; the process form carries only quality + timing, no free-living
  absence). **Curator ruling (L8): the entity being absent covers the process having failed — not
  distinct phenotypes.**
- **This closed a phantom gap:** "Complete loss of conidiation (free-living)" sat in the backlog as a
  real coverage gap; `PHIPO:0000061` "asexual spores absent" (free-living, synonym "conidia absent")
  is exactly it. Closed by the curator.
- Writing the FAQ **caught my own wrong claim** ("process form only for timing" — `abnormal`/`normal
  asexual sporulation` also exist) and fixed it in all four docs.

### Docs: FAQ entries + "one fact, one home" (commits 9319c8a, e7d3605, 196dbea, 9ac12b2)
- Added FAQ entries: PHIPO lookup source; species-neutrality + which retries first; can weaver help
  develop PHIPO. Corrected **L2**'s stale status ("skill note open" → the fold-in had landed) and
  re-verified L2 against the now-offline scorer.
- **Meta, prompted by the user noticing fixes take longer:** measured this session — 636 lines code /
  578 docs, and correcting one wrong claim meant editing four files. The cost is **duplication, not
  tangled code** (modularity is working — see the 4-edit validate change). Tightened L8 + the FAQ
  entries **back to pointers**, canonical detail in the skill — but only after grepping to confirm the
  skill actually held every fact first (the release-specific caveat lived *only* in L8 and had to move
  before the cut).

### Curator rulings on two open issues (no commits — draft edits, then partly reverted)
- **phi-weaver#4 (strain):** Hsin-Yu confirmed annotate with experimental **strain 2035**, keep
  `K3V6Z9` (CS3096 reference-genome ortholog) as the accession — a clean instance of judge-core-primer
  rule 9. Resolved the draft's `needs_accession` flag; **closed the issue**. (Draft edit kept.)
- **phi-weaver#6 (DON + CaCl₂):** ruling (2) CaCl₂ → `PHIPO:0001303` "sensitive to osmotic stress" +
  `PECO:0000261 "+ CaCl₂"` is clean. **Ruling (1) DON → `PHIPO:0000219` "…within host" trips the L7
  context guard** — the DON here was measured **in vitro** (TBI medium, ELISA), and a free-living term
  (`PHIPO:0001445`) fits; posted a context question on #6. **User then dropped the topic** (will delete
  the comment manually) and asked to drop the draft-fixing action → **reverted both #6 draft edits**;
  kept only the #4 resolution.

## Key decisions
- PHIPO term requests: **pattern extension → PR; everything else → evidence-only issue.** A missing
  sibling can be an oversight *or* a decision — the parallel-terms test tells them apart, and an
  obsoleted-but-not-recreated term is invisible to OLS search.
- PHIPO lookup is **offline** against the release artifact, never the edit file. OLS kept for GO only.
- Scorer must keep **`no_match` reachable** — it is the load-bearing signal for gap detection; IDF
  weighting, not token overlap.
- Docs discipline: **one fact, one home** (skill = canonical, ledger = intake+provenance, FAQ =
  lookup) — but verify the home holds the fact before removing a duplicate.

## State / open threads
- **phipo#454** — CI green, mergeable, awaiting James (ID + `replaced_by` decisions).
- **Design-scope question** — for Hsin-Yun (backlog): how much term design may a request carry.
- **phi-weaver#6 ruling (1)** — DON context question posted then being withdrawn by the user; draft
  edits reverted; paper's DON flag back to `needs_term_choice`.
- **phi-weaver#4** — closed; draft strain flag resolved.
- 283 tests green. 13 commits on `main` (`d48cb36`…`9ac12b2`), not pushed this session.
