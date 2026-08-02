---
created: 2026-08-02
type: session-log
tags: [status/complete]
project: Export constraint recorded before building, three FAQ answers, and a WT-control question that exposed a provenance bug
summary: A docs-only session that mostly decided what *not* to build. Four "should weaver do X" questions (export its ontology knowledge to another LLM, adopt Graphiti/Neo4j, become self-evolving, be called a "semantic agentic system") each resolved to a recorded constraint rather than code — D20 pins any future export as a named profile of the existing handover builder, with a gitignore-exclusion invariant so `canto_deploy.yaml` can never be republished. Verified rather than assumed twice: `phipo_ext.owl` and the bundled `.obo` are the same 47 terms and 15 obsolete with identical ID sets, and the upstream `.obo` is **byte-identical** to the vendored copy, so nothing has drifted since 2026-07-16. The afternoon's question — does weaver always create a WT control metagenotype? — answered **no**: the convention is settled (`#78`/`#79`) but `phenotype-annotation/SKILL.md:80` says *link where one exists* rather than create, and nothing checks the omission. Filed `phi-weaver#9` to Hsin-Yu Chang. The curator then corrected a premise: the FgKnr4 example cited as a counter-example **was never approved**, which exposed a systematic bug — `gold-standard-import` defines `reviewed_by` as the *session* curator, conflating it with example sign-off, across all five `status: validated` examples. Frontmatter deliberately left untouched pending a curator ruling. 3 commits.
---

# Session: decide the shape, don't build the thing

## Recap

Four questions arrived in the same shape — *could weaver do X?* — where X was a real capability
with a plausible case: export its ontology knowledge to another model, adopt a temporal knowledge
graph, become self-evolving, be described as a semantic agentic system. **None of them produced
code.** Three produced a recorded constraint or a documented answer; one produced a GitHub issue.
That was the right outcome each time, because in every case the artefact had **zero consumers** and
the cost of building early was a second half-maintained copy of something weaver already has.

The afternoon inverted it. A narrow factual question — does weaver always generate a WT control
metagenotype? — turned out to have a real gap behind it, and chasing that gap surfaced a
**provenance bug in the example library** that is larger than the question that found it.

## Objectives
- Answer the standing "should weaver do X" questions without building anything speculative.
- Where the answer is "not yet", record the constraint so the eventual build can't clutter the repo.
- Verify claims about bundled data rather than reasoning from format conventions.

## Work done

### 1. PHIPO_EXT: already bundled, and the `.owl` adds nothing (no commit — verification only)

Asked whether weaver needs `phipo_ext` supplied. It does not: `phiweaver/lookup/data/phipo_ext.obo`
(47 terms, 15 obsolete, vendored 2026-07-16) is wired into `validate_ontology_ids` and is one of the
five sources `refresh_ontologies` can re-pull.

A follow-up asked about `phipo_ext.owl` on the same upstream. **Compared rather than assumed:**
fetched both, and the ID sets are identical in both directions (47/47), deprecated counts match
(15/15), and the ontology headers agree. The OWL's axiom inventory is `owl:Class` ×47,
`rdfs:subClassOf` ×31, `inSubset` ×34, `hasExactSynonym` ×5, `deprecated` ×15 — every one of which
OBO represents natively. No equivalence classes, property chains or logical definitions exist to be
lost, so the lossy-serialisation worry doesn't apply here. **Bonus finding:** the upstream `.obo` is
**byte-identical** to the bundled copy, so nothing has drifted since vendoring.

Distinct from the `phipo-base.obo` / `phipo-edit.owl` rule, which is a *content* difference
(unreleased terms). `phipo_ext` has no edit/release split, so the `.owl` is purely the other
serialisation.

### 2. D20 — the export's shape, recorded before anything is built (`940d23f`)

The ask was for a stable system for eventually handing weaver's ontology knowledge to another LLM,
explicitly without cluttering weaver. **The stable artefact is a constraint, not a tool.**

D20 pins any such export as a **named profile in `scripts/build_judge_handover.py`'s `FILES` list**,
sourced from `phiweaver/lookup/data/README.md` — already the ontology-access record, and current as
a side effect of `refresh_ontologies`, so a profile pointing at it cannot drift. Four constraints:
no new source of truth; profile not script (a second builder sharing ~90% of its logic is the
duplication **D16** already corrected once); generated artifacts only; and **no gitignored path in
any profile**, since `canto_deploy.yaml` is private and this repo is public — enforceable by a test
rather than by memory.

Status is **not built — constraint only**, with the trigger recorded as *a real consumer, not a
hunch*. Backlog row under Tooling, FAQ entry beside the existing judge-handover question.

### 3. Two FAQ answers: self-evolving, and what to call it (`6053599`, `747e44d`)

**Self-evolving** — weaver already is, declaratively, and `LEARNING-SYSTEM.md` documents the closed
loop. The receipt: the Δ-suffix ruling (L4) was never coded as a lint, yet every draft on or after
it complies while pre-L4 drafts read `ΔfleQ`. Not being weight-updating is load-bearing, not a gap:
reversibility, cited provenance and git history are what a tool feeding a public database needs. Of
the four human gates, the one worth raising is per-term ontology ratification → per-**pattern**.
**The binding constraint is ground truth, not architecture** — the only true fitness signal is a
curator entering a draft into PHI-Canto (D13), submission is manual by design (D18), so evolution
rate is capped by curator throughput.

**Naming** — "semantic" overclaims: that word signals RDF/OWL reasoning, and weaver does lexical
matching and ID validation over OBO, having just been shown not to consume the OWL at all.
"Agentic" misattributes: weaver is the skills, conventions, examples and deterministic tools an
agent *reads*, so **agent scaffolding** is the term for the artefact — and "agentic" now implies
autonomy, exactly what the whitepaper says weaver is not. Keep **AI-assisted biocuration toolkit**;
for one distinctive phrase lead with **declarative (non-parametric) learning**.

### 4. Graphiti / Neo4j — answered, deliberately not built (no commit)

Ontologies are genuinely graph-shaped (1327 PHIPO terms, 1173 `is_a` edges) and sibling-grid
analysis is real graph querying. **But graph queries are not a graph database at this scale** — that
is a dict built at parse time, stdlib, offline, deterministic. Graphiti breaks four things in order:
the benchmark sandbox (LLM + embedding calls per episode against a default-deny allowlist),
determinism, D3/D8, and **manufactured consensus** — a temporal graph fed from weaver's own drafts
is precisely mining its own output. Its headline bi-temporal feature is already served better by the
append-only ledger plus git. A D6 plugin candidate at most, and the one genuinely graph-shaped use
case (multi-hop queries across PHI-base's interaction records) is a separate tool, not weaver.

### 5. Does weaver always create a WT control metagenotype? No — and nothing checks it

The convention is settled and correctly documented
(`07-Standards/PHI-Canto-Curation-Conventions.md:194`, citing `#78`/`#79`): **no** WT control for
single-species pathogen phenotypes; **yes** for metagenotype annotations, one per phenotype, linked
via `compared to control`. Three gaps between that and "always":

1. **The drafting instruction is weaker than the convention.** `phenotype-annotation/SKILL.md:80`
   reads *"Interaction phenotypes link a control genotype/metagenotype **where one exists**"* —
   link-if-present, not create. An agent following the skill has no instruction to construct one.
2. **Nothing enforces it, and the omission is invisible.** `coverage.py` reads `compared_to_control`
   only as evidence a genotype *is* referenced; it never asserts an interaction annotation *has* a
   control. Its own docstring says it cannot catch omissions — the same class that hid the
   complementation-control problems it was later built for.
3. **Whether the control is itself annotated is unsettled** — see below.

Filed **[phi-weaver#9](https://github.com/PHI-base/phi-weaver/issues/9)** to Hsin-Yu Chang, matching
the house style of `#8`. Deliberately split: the SKILL.md/coverage gap is *not* a curator question
(the team ruled in 2020), so it stays a weaver backlog item.

The issue body was then revised by the curator-side author — dropping a bullet and the closing
rationale, adding a `#affecting-weaver-drafts` tag. **The edit had not saved to GitHub**; applied it
via `gh issue edit` and verified live. The tag is body text, not a repo label (which does not exist).

### 6. The FgKnr4 example is not approved — and the bug is systematic

The issue originally cited `PMID39787257-FgKnr4-cell-wall-stress.md:70-71` as a counter-example: it
carries no WT annotation row, the control appearing only as `compared_to_control *FgKnr4+*[WT
level]`, against the Cuzick framework's *"compared to control AE **+ WT metagenotypes**"*.

**The curator's correction: that example was never approved.** An unapproved example is not evidence
about what PHI-Canto expects, so removing it was right and the backlog note that treated it as a
contradiction was wrong.

But the file asserts approval explicitly — `status: validated`, `reviewed_by: Hsin-Yu Chang`,
`reviewed_date: 2026-07-04`, a header reading "**Validated gold-standard curation**", and ✅ in
`Curation-Examples-INDEX.md`. **The mechanism is a conflated field:**
`skills/gold-standard-import/SKILL.md:49` defines `reviewed_by` as *"the PHI-Canto curator"* — whoever
curated the **session**, which is a different act from reviewing the **example**. All five examples
carry `status: validated`. The skill's own rules are right and undercut by the field name: `:65`
says `validated` is "only for a genuinely curator-reviewed curation", `:71` says import as `draft`
and flip only after review.

**Frontmatter deliberately not edited.** It is a provenance record, and two different corrections
apply depending on whether the *session* or only the *example sign-off* is what didn't happen.
Logged under BACKLOG "Curation workflow" with the proposed fix: split `curated_by` (factual,
safe to auto-fill) from `reviewed_by` (set only when sign-off happened).

## Decisions
- **D20 recorded**: exports are a profile of the existing builder; no second builder, no parallel
  doc, no gitignored path. Not built — the trigger is a real consumer.
- **Answer, don't build** for Graphiti/Neo4j and the export: both had zero consumers.
- **Keep "AI-assisted biocuration toolkit"**; reject "semantic" and "agentic" as the primary label.
- **Issue #9 cites only the framework** — an unapproved example is not evidence, so the FgKnr4
  contradiction stays an internal note.
- **Do not edit example provenance without a curator ruling.**

## Open items
- **`phi-weaver#9`** awaiting Hsin-Yu Chang.
- **`reviewed_by` across all five examples** — needs a curator ruling on which correction applies;
  propagates into drafting retrieval *and* the judge bundle.
- **The weaver-side drafting fix** (SKILL.md:80 create-and-link + a `coverage.py` warning) — blocked
  on #9, which decides what "create" means.
- **Graphiti/Neo4j answer not captured** in the FAQ; would sit beside the OKF entry.
- **`#affecting-weaver-drafts`** is body text, not a GitHub label.
- **`docs/BACKLOG.md` uncommitted** at time of writing (three edits: the #9 row, its correction after
  the curator's note, and the provenance item).
- `00-Inbox/for-weaver/Schemas/` still untracked — predates this session.

## Lessons
- **An unapproved artefact is not evidence.** The FgKnr4 file looked authoritative — validated
  status, named reviewer, ✅ in the index, shipped in the judge bundle — and none of that survived
  one sentence from the curator. Check provenance *before* citing an internal artefact against an
  external standard.
- **A field name can launder one act as another.** `reviewed_by` meaning "session curator" reads as
  "approved this example" everywhere it appears. The rules around it were correct; the name defeated
  them. Where two acts can be confused, name both fields.
- **Verify serialisations rather than reasoning about them.** Comparing `.owl` to `.obo` cost two
  commands, settled the question definitively, and incidentally proved zero upstream drift — which
  no amount of reasoning about format lossiness would have shown.
- **The index-row cap can be evaded.** `session_index.check` measures `cells[-1]`, so a summary
  containing `|` (in a code span or table fragment) is only measured from its last pipe onward. The
  2026-07-26 row runs to hundreds of words and passes. Worth noting because `FAQ.md` cites this
  check as the example of enforcement working.

## Commits
- `940d23f` — Decide the shape of a knowledge export before building one (D20 + backlog + FAQ)
- `6053599` — Answer the self-evolving question where it will be asked (FAQ)
- `747e44d` — Settle what weaver is called, and what it is not (FAQ)

Docs-only throughout; no code changed, so no new tests. Smoke green at 9/9 after each change.
