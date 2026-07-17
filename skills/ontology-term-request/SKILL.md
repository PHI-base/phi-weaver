---
name: ontology-term-request
description: Turn ontology gaps met during curation into evidence-backed term or synonym requests for PHIPO / PHI-ECO (PECO) / PHIDO. Use when a phenotype or condition has no usable term, or periodically to triage the accumulated gap ledger. Gathers evidence for the ontology editors; never designs terms.
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
  - the tracker URL recorded back against the gap once filed
---

# Ontology Term Request

## Purpose
Curation is the best available detector of ontology gaps: it meets them on real papers, with
the evidence already in hand. This skill turns that into requests the PHIPO / PHI-ECO / PHIDO
editors can act on, and — just as importantly — filters out the misses that are *not* gaps.

**Scope: evidence, not design.** Produce "here is a need, here is what is missing, here are the
papers that needed it". Do **not** propose a term's parent, write its formal definition, or
place it in the hierarchy — that is the editors' expertise, and this project does not assert
in-silico conclusions as fact (the same principle behind the team's ISS rejection).

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

5. **Name the closest existing term and why it fails.** A request without this reads as "I
   couldn't find one" and will bounce. There are two failure shapes, both real:
   - **wrong context** — `PHIPO:0000234` *pathogen deoxynivalenol within host absent* exists,
     but is within-host and cannot describe an in-vitro assay;
   - **missing granularity in an otherwise-present branch** — the free-living DON branch has
     `decreased` (`PHIPO:0001445`) and `increased`, but no `absent`.

   PHI-base/phipo#452 is the worked example: it names both, and that is why it is a good request.

6. **Check it isn't already filed**, then record the gap with its evidence:
   ```
   python3 -m phiweaver.lookup.gap_log report
   python3 -m phiweaver.lookup.gap_log record PHIPO "<phrase>" --pmid <PMID> \
     --context "<where in the paper; what was measured; closest term + why it fails>"
   ```

7. **Draft the request** for a human to file, following #452: what is missing, the closest
   existing term(s) and why each fails, the paper evidence (PMID + figure/table + the actual
   measurement), and how many papers have hit it. Ranked frequency comes from `gap_log report`
   — a gap several papers needed is a far stronger case than one paper's, and it is the
   argument an editor responds to.

8. **After a human files it**, record the URL so it stops resurfacing as a new candidate:
   ```
   python3 -m phiweaver.lookup.gap_log record PHIPO "<same phrase>" \
     --filed https://github.com/PHI-base/phipo/issues/NNN
   ```

## Expected outputs
- Either a recorded gap/synonym event with evidence, or a reasoned "not a gap" and which of
  the three cases it was.
- For a genuine gap: a drafted request naming the closest existing term, why it fails, and the
  papers that needed it.
- Never: a proposed parent, definition, or hierarchy placement.

## Quality-control checks
- Alternate wordings were retried before the gap was recorded.
- Every surviving candidate was read against the paper, not assumed to fit.
- The closest existing term is named, with the reason it fails.
- Evidence cites PMID + location + what was measured.
- `gap_log report` was checked for an existing filing.

## Human review
- Every request is drafted for a curator to file, never filed automatically: a request is a
  claim on the ontology team's attention, and a wrong one costs more than a missing one.
- The ledger gathers evidence; the curator decides what is worth filing; the ontology editors
  decide what gets built.
- The ledger **under-counts**: it records what curation happened to meet, and context-wrong
  matches only surface if someone declared the assay context. A quiet report means nobody has
  looked lately, not that the ontology is complete.
