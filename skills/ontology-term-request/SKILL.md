---
name: ontology-term-request
description: Turn ontology gaps met during curation into evidence-backed term or synonym requests for PHIPO / PHI-ECO (PECO) / PHIDO. Use when a phenotype or condition has no usable term, or periodically to triage the accumulated gap ledger. Gathers evidence for the ontology editors; designs a term only when an existing sibling set already fixes every field, and then as a PR.
backing_script:
  - phiweaver/lookup/gap_log.py
  - phiweaver/lookup/term_context.py
  - phiweaver/lookup/map_phenotype.py
  - phiweaver/lookup/map_condition.py
tests:
  - tests/test_gap_log.py
  - tests/test_term_context.py
inputs:
  - a phenotype/condition phrase that failed to map, with its PMID and where in the paper
  - the assay context (free-living / in-host) for phenotype phrases
  - or: no input, to triage the accumulated ledger periodically
outputs:
  - a recorded gap event (docs/ontology-gaps.jsonl), or a reasoned decision that it is not a gap
  - a drafted term or synonym request, evidence-backed, for a human to file
  - or, for a pattern extension: a drafted PR against phipo-edit.owl for a human to push
  - the tracker URL recorded back against the gap once filed
---

# Ontology Term Request

## Purpose
Curation is the best available detector of ontology gaps: it meets them on real papers, with
the evidence already in hand. This skill turns that into requests the PHIPO / PHI-ECO / PHIDO
editors can act on, and — just as importantly — filters out the misses that are *not* gaps.

## Two routes: issue or PR
Which one depends on **one test: does an existing sibling set already fix every field?**

**Pattern extension → PR.** A missing dimension in a live sibling set (the set has `decreased`
and `increased`, not `absent`) has no degrees of freedom left: the parent is the siblings'
parent, the definition is a sibling's definition with one word swapped, the label and namespace
follow. That is **copying a human's earlier decision, not making a new one**, and it is the case
James Seager explicitly asked for as a PR against `phipo-edit.owl` (see
[[phipo-local-clone]] — PRs target `master`; **CI runs the full ODK QC on the PR, so no local
`robot`/ODK install is needed** — confirmed green on PR #454, 2026-07-17; start from the wording
of the existing definition). **Step 5 is mandatory before any PR** — it is what distinguishes a
pattern with a hole from a pattern a human deliberately shaped.

**Everything else → issue, evidence only.** A gap needing a new branch, a new parent, or a
judgement about where it sits: produce "here is a need, here is what is missing, here are the
papers that needed it", and do **not** propose the parent, definition or placement. That is the
editors' expertise, and this project does not assert in-silico conclusions as fact (the same
principle behind the team's ISS rejection).

> **Open question — tracked in `docs/BACKLOG.md` ("How much term *design* should a request
> carry?", Curation workflow).** PHIPO's own `CONTRIBUTING.md` asks requesters to suggest
> "label (name), definition, references, position in hierarchy" — so this skill's evidence-only
> line is *stricter than PHIPO's house rule*. For Hsin-Yun; supersede the routes above when she
> answers. The default below works meanwhile.

## When to use
- During curation, when a phenotype or condition has no usable term.
- Periodically, to triage the accumulated ledger: `gap_log report`.

## Three misses that are not gaps
Filing these burns credibility with the ontology team and gets real requests ignored. Rule
them out **before** recording anything.

1. **A wording gap.** The term exists; the phrasing didn't find it. Lesson L2: a DON phrase
   returned `no_match` and looked like a gap, but retrying "level of X" / "abnormal X
   biosynthesis" found the term. Always retry alternate wordings first. A retry that succeeds
   is a **synonym** request, not a term request — cheaper to get accepted, and it fixes the
   search for everyone.
2. **A granularity miss in PHI-ECO.** PECO is deliberately qualitative: "potato dextrose agar
   at 25 °C" correctly maps to `rich medium`, with the numerics staying in the annotation
   comment (lesson L6). A qualitative term that fits is not a gap.
3. **An already-filed gap.** Check `gap_log report` — filed gaps carry their tracker URL. Chase
   the existing issue; do not open a second one.

## Workflow

1. **Establish the phrase and its context.** Take the phenotype/condition verbatim, with its
   PMID and location (figure, table, section) and what was actually measured. For a phenotype,
   decide the assay context: `free-living` (in-vitro culture) or `in-host` (in planta).

2. **Search, declaring the context** — this is the step that catches the gap kind a plain
   search hides:
   ```
   python3 -m phiweaver.lookup.map_phenotype "<phrase>" --assay-context free-living
   python3 -m phiweaver.lookup.map_condition "<phrase>"        # PECO, offline
   ```
   `no_match` is the obvious gap signal. The dangerous one is a **context-wrong match**: the
   search returns a term that is lexically right and contextually impossible, with nothing
   marking it. `--assay-context free-living` flags in-host terms; PHIPO states context in the
   label (`within host`, `on host surface`).

3. **Judge the surviving candidates yourself.** This is the crux, and no tool does it: a search
   pads its result with terms that merely share a word. Searching "absent DON" for a free-living
   assay returns `PHIPO:0000939 asexual spore lysis absent` — host-free, so not flagged, and
   irrelevant. **A surviving candidate is not a fitting candidate.** Read each one against what
   the paper measured.

4. **Retry alternate wordings** before concluding anything (see "not gaps", #1). If a retry
   finds a fitting term, record a wording gap and stop:
   ```
   python3 -m phiweaver.lookup.gap_log record PHIPO "<phrase that missed>" \
     --outcome synonym --matched-term PHIPO:XXXXXXX --matched-via "<wording that worked>" \
     --pmid <PMID>
   ```

5. **Look for an obsoleted term with the same meaning.** A concept that once existed and was
   deprecated is invisible to OLS's search, so it returns a clean `no_match` and looks like a
   virgin gap. Since 2026-07-17 PHIPO resolves offline, so **the tool can show you**:
   ```
   python3 -m phiweaver.lookup.map_phenotype "<phrase>" --include-obsolete --rows 10
   ```
   Obsolete hits come back flagged `⚠️ OBSOLETE — not annotatable; gap-analysis only`, and the
   same result conveniently lists the **parallel terms** you need for the test below.

   For the **unreleased** last mile — a term merged to `master` but not yet in a release, which
   the bundled file cannot know about — grep the clone
   (`/mnt/z/Computer/GITHUBrepositories/phipo`, `git pull` first):
   ```
   grep -i "<chemical/phenotype>" src/ontology/phipo-edit.owl | grep "rdfs:label"
   ```
   This is the "already added, don't file twice" check — **not** a source of suggestions: an
   edit-file term is one PHI-Canto does not have, so a curator cannot annotate to it.

   **An obsolete term is a fossil of a past decision, and the file usually does not say which
   decision.** PHIPO's obsolete terms frequently carry no `replaced_by` or `consider` pointer, so
   deprecation alone tells you nothing about *why*. Resolve it with the **parallel-terms test**:

   - **Do the parallel terms still carry the dimension?** (other toxins, other substances, the
     generic parent) → the concept is live, this one was **missed** → safe to fill by following
     the pattern.
   - **Did they all lose it too?** → that was a deliberate **modelling decision**, and re-creating
     the term silently reopens it *while looking exactly like routine pattern-filling*. Do not
     PR it. File an issue asking why.

   Worked example (#452 → PR #454): free-living "absent DON" recorded as a clean gap, but
   `PHIPO:0000503` *deoxynivalenol absent from cell* existed and had been obsoleted in the 2019
   refactor. The parallel terms settled it — `PHIPO:0001033` (pyocyanin) and `PHIPO:0001105`
   (gliotoxin) both still live under `PHIPO:0001034` *substance absent from cell*, while DON's
   `decreased`/`increased` were re-created in 2025 and `absent` was simply missed. Oversight, not
   decision → PR. **Had pyocyanin and gliotoxin also lost theirs, the identical-looking PR would
   have been wrong.**

6. **Name the closest existing term and why it fails.** A request without this reads as "I
   couldn't find one" and will bounce. There are three failure shapes, all real:
   - **wrong context** — `PHIPO:0000234` *pathogen deoxynivalenol within host absent* exists,
     but is within-host and cannot describe an in-vitro assay;
   - **missing granularity in an otherwise-present branch** — DON had `decreased`
     (`PHIPO:0001445`) and `increased` (`PHIPO:0001447`), but no `absent`;
   - **obsoleted and never re-created** — the closest term is deprecated (step 5). Say so
     explicitly and name it; it is the strongest evidence a request can carry, and the editors
     cannot see it from OLS either.

   PHI-base/phipo#452 is the worked example of the first two; PR #454 adds the third.

7. **Check it isn't already filed**, then record the gap with its evidence:
   ```
   python3 -m phiweaver.lookup.gap_log report
   python3 -m phiweaver.lookup.gap_log record PHIPO "<phrase>" --pmid <PMID> \
     --context "<where in the paper; what was measured; closest term + why it fails>"
   ```

8. **Draft the request** — issue or PR, decided by the test in "Two routes" above. Either way it
   carries: what is missing, the closest existing term(s) and why each fails (including a
   deprecated one, step 5), the paper evidence (PMID + figure/table + the actual measurement),
   and how many papers have hit it. Ranked frequency comes from `gap_log report` — a gap several
   papers needed is a far stronger case than one paper's, and it is the argument an editor
   responds to.

9. **After a human files/pushes it**, record the URL so it stops resurfacing as a new candidate:
   ```
   python3 -m phiweaver.lookup.gap_log record PHIPO "<same phrase>" \
     --filed https://github.com/PHI-base/phipo/issues/NNN     # or /pull/NNN
   ```

## Expected outputs
- Either a recorded gap/synonym event with evidence, or a reasoned "not a gap" and which of
  the three cases it was.
- For a genuine gap: a drafted request naming the closest existing term, why it fails, and the
  papers that needed it.
- For a **pattern extension**: a PR against `master` whose every field is traceable to a named
  sibling term, plus the step-5 evidence that the hole is an oversight.
- Never: a proposed parent, definition, or hierarchy placement **outside** a pattern extension.

## Quality-control checks
- Alternate wordings were retried before the gap was recorded.
- Every surviving candidate was read against the paper, not assumed to fit.
- **`phipo-edit.owl` was grepped for an obsoleted term with the same meaning** — OLS would not
  have shown one.
- **If one exists: the parallel-terms test was run**, and the request says which way it came out.
  A PR is only justified when the parallel terms kept the dimension.
- The closest existing term is named, with the reason it fails — including if it is deprecated.
- For a PR: every field cites the sibling term it was copied from; no field was invented.
- Evidence cites PMID + location + what was measured.
- `gap_log report` was checked for an existing filing.

## Human review
- Every request is drafted for a curator to file, never filed automatically: a request is a
  claim on the ontology team's attention, and a wrong one costs more than a missing one. **A PR
  is a bigger claim than an issue, not a smaller one** — it asserts the answer, so the bar for
  opening one is the step-5 evidence, not merely a plausible-looking pattern.
- The ledger gathers evidence; the curator decides what is worth filing; the ontology editors
  decide what gets built.
- The ledger **under-counts**: it records what curation happened to meet, and context-wrong
  matches only surface if someone declared the assay context. A quiet report means nobody has
  looked lately, not that the ontology is complete.
