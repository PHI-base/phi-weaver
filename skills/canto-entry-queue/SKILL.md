---
name: canto-entry-queue
description: Turn a phiweaver curation draft into a concise, table-driven PHI-Canto "entry queue" — a click-list a biocurator works through top to bottom in canto.phi-base.org, with uncertain items parked so they can't be entered by accident. This is the single Route-1 output; use when a draft's `canto` block is ready for a curator to enter into PHI-Canto.
backing_script:
  - phiweaver/canto/entry_queue.py
  - phiweaver/export/docx.py
tests:
  - tests/test_entry_queue.py
  - tests/test_export_docx.py
inputs:
  - a phiweaver draft (.md) whose ```json block contains a populated `canto` object
outputs:
  - one Markdown entry queue per draft — setup tables (genes/alleles/genotypes/host/metagenotypes) then annotation tables (GO / physical interaction / pathogen / interaction / disease), a parked-items safety section, and summary counts
  - a Word **.docx** copy of the entry queue alongside the .md; by default both are written — pass `--no-docx` for markdown only, or `--no-md` for the Word file only
---

# Canto entry queue

## Purpose
The single **Route 1** output (`docs/CANTO-ROUTE1-BUILD-SPEC.md`) for **live** curation. The entry
queue strips a draft's structured `canto` block to the minimum a biocurator needs while
transcribing into **PHI-Canto** (<https://canto.phi-base.org/>): short tables, `enter` / `hold`
status, `☐` tick boxes, and one row per PHI-Canto entry action — optimised for speed and safety at
the keyboard.

Deterministic: the same `canto` block always renders the same queue; nothing is invented. Spec:
`PHI-Canto-Literature/active/Worksheet prompt-2026-07-08.md` (curator request).

## When to use
- A draft's `canto` block is populated and a curator is ready to enter it into PHI-Canto during a
  live session — the queue is the click-list they work through at the keyboard.

## The held-gene cascade (the core rule)
A gene with **no `uniprot` accession is held** (`hold`), because PHI-Canto's add-gene step needs
an identifier. Everything that depends on it is then moved to the **parked** section, never an
entry table: its alleles, any genotype using them, any metagenotype using those genotypes, and
any annotation on a held feature. This makes the parked section a safety filter — uncertain items
cannot be entered by accident.

Also parked automatically: annotations with **no ontology term** (except physical interactions,
whose PSI-MI evidence is chosen in Canto); **interpretive molecular-function** terms whose
evidence self-declares no direct assay (inferred from rescue/genetics/homology); and any
**dangling reference** — an allele/genotype/metagenotype/annotation that points at an undefined
gene/allele/genotype/feature (a referential-integrity check, so a hand-edited block can't slip a
broken row into an entry table). With `--validate`, ontology IDs are checked online and
**obsolete / not-found** terms are parked too (default stays offline and deterministic).

## Workflow
1. Populate/repair the draft's `canto` block (see `genotype-creation`, `phenotype-annotation`,
   `gene-for-gene`, and the curation-example template).
2. Run `python3 -m phiweaver.canto.entry_queue <draft.md>` (from the repo root). Batch multiple
   drafts, or use `--stdout` to preview / `--out` for a custom path.
3. The queue writes `<stem>-phi-canto-entry-queue.md` and prints summary counts (enter-ready
   genes, held genes, enter-ready annotations, parked items).
4. In PHI-Canto, work the tables top to bottom: **A** genes → **B** alleles → **C** pathogen
   genotypes → **D** host genotype → **E** metagenotypes → **F** annotations (GO / physical
   interaction / pathogen phenotype / interaction phenotype / disease) → **G** resolve parked
   items before entering any of them.

## Source provenance (required in every draft's `meta` block)
The queue prints a **`Curated from:`** line above the first table, from three `meta` fields:

- **`source_route`** — one of `pdf`, `jats-publisher`, `jats-europepmc`
  (`phiweaver.source_routes`). Omitted, it is inferred from `source_file`'s extension.
- **`source_file`** — the artefact actually read.
- **`figures_inspected`** — `true`/`false`. Overrides the route's default, because a
  publisher XML whose images were fetched separately is no longer captions-only.

## Figure-inspection ledger (`figure_inspection`, top-level in the json block)
`figures_inspected: true` is an **assertion nothing verifies**. Record instead one entry per
figure — `{label, file, inspected, read, supports/weakens, note}` — where **`read` is what you
actually saw in the panel**. An entry with `inspected: true` and an empty `read` counts as *not*
inspected: ticking a box is not looking at a figure. Declining a figure is fine when nothing
depends on it, but say so in `note`.

Audit it with `python3 -m phiweaver.figure_ledger <draft.md>` (add `--record` to write coverage
to the tracking DB, `--strict` to fail a build). The queue then prints **`Figures inspected:
n/N`**, and any annotation citing an un-inspected figure lands in **F6 — enterable, but
caption-only** (an advisory, *not* the parked table: a caption-based claim may still be right,
it is just weaker).

**Policy: decline by default, inspect on cause.** Text and captions carry the annotation set —
on PMID:39852455, inspecting six panels changed **zero** term selections. Curate from text and
captions, then mark an annotation `needs_figure: true` (with `needs_figure_reason`) only when
one of three causes applies: the claim is **qualitative** and only the panel can confirm it;
**magnitude decides** the annotation rather than describing it; or it is the paper's
**take-home message**. Only `needs_figure` annotations are hard requirements — everything else
citing an un-inspected figure is reported as information, so routine declines never read as
warnings.

**Plan the spend first: `--needed`.** Reading figures costs tokens — a vision model bills an
image at roughly `width × height / 750`. On PMID:39852455 six panels cost ~3,550 tokens against
~10,900 for the parsed text, about +33%. `--needed` lists only the figures the **annotations
actually cite**, with the estimated cost of the ones still unread, so selective reading is a
decision rather than a guess:

```
📖 Figure 7   ~1121 tokens   cited by: GO:0010508, GO:0032995
Still to read: 1 figure(s), ~1121 tokens.
Not cited by any annotation: Figure 2 (~524 tokens saved by declining them).
```

Inspect what the annotations rest on; decline the rest **with a reason** in `note`.

This catches real errors. On PMID:39852455 the draft declared "no annotation depends on
Figure 7"; the audit showed `GO:0010508` and `GO:0032995` both cite it, and inspecting it
revealed the transcript data run *opposite* to the naive reading of `positive regulation of
autophagy` — a qualification that would otherwise have shipped unnoticed.

Record these: the route decides what evidence a draft could rest on. A publisher JATS names
image files it does not ship, so figures are captions only, and a draft written that way can
misjudge the evidence — on PMID:39852455 a cell-wall-thickness measurement read as a marginal
`p < 0.05` from its caption but is a rescued ~2-fold effect in the panel, and a branching claim
read as quantified when it never was. The same values are stored in the tracking DB
(`phiweaver.tracking.ingest_provenance`), so `captions_only_articles()` lists the drafts worth
revisiting if the paper later becomes open access.

## Expected outputs
- A short header (citation, system, status, model/tool, date) **and the `Curated from:` line**.
- Setup tables A–E, then one annotation table per PHI-Canto annotation type, headed with the
  label the web interface itself shows (`GO molecular function`, `pathogen phenotype`,
  `pathogen-host interaction phenotype`, `protein modification`, `disease name`, …). Sections
  are numbered F1, F2, … over the types the paper actually has — empty ones are omitted — so
  the numbers shift between papers and nothing should cite them. Each row is one Canto entry
  action with a `☐`.
- A parked-items table (item / why parked / action needed) as the safety filter.
- A queue summary with the counts and the list of unresolved blockers (held genes).

## Quality-control checks
- Every allele/genotype/metagenotype/annotation in an entry table resolves to a defined,
  non-held parent (enforced by the cascade).
- No annotation depends on a held gene; blank-term and interpretive-MF items are parked.
- Table cells escape `|` and collapse newlines, so the output cannot corrupt into an unreadable
  table.
- A **coverage lint** (`phiweaver.canto.coverage`) prints stderr advisories at generation time for
  genotypes the block defines but barely uses — *unused* (referenced by nothing) or *in no
  metagenotype* — the signal that catches a metagenotype dropped in the prose→block translation.

## Human review
The queue is a transcription aid, not an authority: entering each row into PHI-Canto **is** the
validation step, where the curator applies Canto's controlled vocabularies and judgement. Parked
items must be resolved by a curator before entry — the queue never invents an accession, term, or
evidence code.
