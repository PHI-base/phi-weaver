---
created: 2026-07-17
type: session-log
tags: [status/complete]
project: GO evidence ruling + ontology gap ledger + wrong-context guard
---

# Session: GO evidence ruling, ontology gap ledger, PHIPO wrong-context guard

## Objectives
- Assess Hsin-Yu's answer on `phi-weaver#8` (GO evidence code when a paper has no biochemistry)
  and fold the ruling in.
- Then: can phiweaver help *develop* PHIPO / PHI-ECO, rather than only consume them?

## Work done

### GO evidence codes — ruling on `phi-weaver#8` (commit 816e592)
- Hsin-Yu approved **TAS**, but the caveat is the real content: the justification is that the
  **authors explicitly state the function** and it matters to the experimental design — **not**
  that UniProt carries the term. Most UniProt GO is pipeline prediction (InterPro2GO, IEA) with
  no author behind it, so bulk transfer would dress a prediction as an author statement. Her
  opening line ("UniProt is a good source for GO annotations") reads, in isolation, like the
  opposite; the reply confirmed the stricter reading so the quotable sentence is the right one.
- Second rule: **no biochemistry ≠ no MF term.** Annotate the MF by TAS where it clears that bar
  **and** the processes the deletions demonstrate by IMP — complementary, not alternatives. For
  PMID:42089373: `GO:0000104` + growth/conidiation/DON by IMP.
- **The ruling reversed L3's proposal**, which had been to drop the textbook MF and annotate only
  the deletions. L3 now records the outcome, not the proposal.
- Filed the confirmation as [phi-weaver#8 comment](https://github.com/PHI-base/phi-weaver/issues/8#issuecomment-5000892037).
- Deliberately left out of the reply: the ISO question (kept the confirmation clean) → backlog.
- Noted but not touched: `07-Standards/judge-core-primer.md:43` tells the judge not to score an MF
  as experimentally supported without direct testing. Still correct (TAS isn't experimental), but a
  judge reading only that line might penalise a legitimate MF-by-TAS. Possible clarifying clause.

### Can weaver help develop the ontologies? → gap ledger (commit 881b49c)
- Premise: curation is the best gap detector — it meets gaps on real papers with evidence in hand.
  Each miss was reported into a draft and forgotten, so **frequency** (the argument an editor
  responds to) was invisible.
- **`phiweaver/lookup/gap_log.py`** — append-only JSONL ledger (`docs/ontology-gaps.jsonl`) +
  ranked report. Ranks by **distinct papers**, not raw events. Enforces the gap/synonym split
  (a retry that finds a term is a **wording gap** → cheaper synonym request, per L2). `filed` field
  stops an already-submitted request resurfacing. Seeded with the real #452 gap only — L2's wording
  gap was **not** seeded: the lesson records the retry pattern but not the phrase that missed, and
  inventing one would be fabricated evidence.
- Chose JSONL over the tracking DB: git is the backstop and the other ledgers (BACKLOG,
  CURATION-LESSONS) are git-visible append-only files. Mappers stay pure — logging is opt-in at the
  CLI boundary (`--log-gaps --pmid --context`), since `map()` doesn't know the PMID.

### Two design claims falsified while building (both corrected in code, not papered over)
1. **`no_match` is NOT the gap signal.** The one real gap on record (#452) isn't a `no_match` —
   "absent DON" matches `PHIPO:0000234` *within host absent* happily.
2. **"every candidate is context-wrong" does NOT detect it either.** Live, the same search returns
   `PHIPO:0000939 asexual spore lysis absent` — noise off the word "absent", irrelevant to DON, but
   host-free, so it reads as usable and masks the gap. The auto-logging built on this was **removed**;
   `--log-gaps` records only `no_match`. `all_mismatched` survives only to word the warning.
- Also over-claimed earlier and corrected: "every free-text condition is a PECO gap candidate" is
  wrong — PDA → `rich medium` is correct by design (PHI-ECO is qualitative, L6). PECO `no_match`
  fires only for genuinely absent concepts ("xylem sap"), so PECO volume is lower than predicted.

### The wrong-context guard — `term_context.py` (commit 881b49c)
- **The real curation risk:** a search returns a term that is lexically right and contextually
  impossible, with nothing marking it. A curator sees a confident match and can annotate it.
- Catchable because **PHIPO states context in the label**. The DON branch splits cleanly:
  in-host `PHIPO:0000233/0000234` vs free-living `PHIPO:0001445/0001447` — and the free-living side
  has no "absent" term, which *is* #452. Same split on growth.
- **Verified the rule before relying on it:** "host-free", "axenic", "free-living" all return
  `no_match`, so no PHIPO label negates the word → a bare `\bhost\b` is safe. Re-check if that
  changes (→ backlog: silent staleness).
- Flags **one direction only** (in-host term for a free-living assay). The reverse isn't a
  contradiction — neutral terms are legitimate in planta, and flagging them would be noise curators
  learn to ignore.
- The warning names the **surviving** candidates ("a search result can share a word without sharing
  a meaning"), because that's where the judgement is. Tool flags; human judges.
- Wired into `phipo-mapping` (steps 4–5 + a context QC check); new **`ontology-term-request`** skill
  (11 skills; registry regenerated). Skill scope: **evidence, not design** — no proposed parents,
  definitions, or hierarchy placement, per the same principle as the ISS rejection.

### Lessons + backlog
- **L7** added: a confident PHIPO match can be contextually impossible (commit 54c387f), then
  **corrected** (commit 696012f) to separate the two claims by strength — the label rule and the
  #452 failure are *verified live*; the binary `free-living`/`in-host` split is **weaver's proposal,
  pending curator confirmation**. The original status overstated a design call as a finding, against
  the ledger's own freeform-source guardrail (`note` = intake, not authority; cf. L1's wording).
  Applied to **skills only**, deliberately not the conventions doc.
- Filed [phipo#453](https://github.com/PHI-base/phipo/issues/453) asking, in plain English, whether
  the in-host/free-living split is even two-way (detached leaf? host extract / xylem sap? host cell
  culture?), whether a canonical branch list exists, and whether "on host surface" is a third
  context. **Blocks L7.**
- Backlog: #453 + ISO → "Waiting for response"; the host-rule staleness → Tooling/bugs; the
  ontology-gaps section now points at the ledger and notes it **under-counts** (complements, does not
  replace, the hand-curated list). Noted the recurring shape: #452 and the free-living conidiation
  item are the same failure.

## Git
Pushed to `main`: `881b49c` (ledger + guard), `816e592` (GO/TAS conventions + L3), `54c387f` (L7),
`696012f` (L7 status correction). 251 tests + 7/7 smoke green.

**Process note:** splitting `CURATION-LESSONS.md` across two commits corrupted it — an Edit removed
L7 *and* the trailing newline, so `cat >>` fused L7 onto L6's row (1960-char line). Caught by
`grep "^| L7"` returning nothing and git reporting a *modified* rather than *added* line; reset from
git and redone. The stripped newline had already landed in the GO commit as a spurious
`\ No newline at end of file`, so that commit was amended (`612069c` → `816e592`) before pushing.
**Root cause:** two unrelated pieces of work in one append-only file. Commit docs work when it's
done.

## Open / next
1. **`phipo#453`** — awaiting answer; supersede L7 and widen `term_context.py` if a third context is
   needed.
2. **`phipo#452`** — still awaiting ontology-team action.
3. **ISO evidence code** — Hsin-Yu raised it; not filed. Backlog has the argument (ISO is stricter
   than ISS: `with/from`, experimentally-supported ortholog, no chaining).
4. **Host-rule self-check** — silent staleness; needs an online check or a skill step.
5. **Sdh draft** — likely missing `GO:0000104` by TAS under the new ruling. **User: no need to fix.**
6. Optional: clarifying clause in `judge-core-primer.md:43` so MF-by-TAS isn't penalised.
