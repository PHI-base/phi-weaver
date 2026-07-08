---
name: canto-entry-queue
description: Turn a phiweaver curation draft into a concise, table-driven PHI-Canto "entry queue" — a click-list a biocurator works through top to bottom in canto.phi-base.org, with uncertain items parked so they can't be entered by accident. Use when a curator wants the practical entry format rather than the fuller worksheet.
backing_script:
  - phiweaver/canto/entry_queue.py
tests:
  - tests/test_entry_queue.py
inputs:
  - a phiweaver draft (.md) whose ```json block contains a populated `canto` object
outputs:
  - one Markdown entry queue per draft — setup tables (genes/alleles/genotypes/host/metagenotypes) then annotation tables (GO / physical interaction / pathogen / interaction / disease), a parked-items safety section, and summary counts
---

# Canto entry queue

## Purpose
A concise companion to the `canto-worksheet` skill for **live** curation. Where the worksheet is
an ordered narrative checklist, the entry queue strips prose to the minimum a biocurator needs
while transcribing into **PHI-Canto** (<https://canto.phi-base.org/>): short tables, `enter` /
`hold` status, `☐` tick boxes, and one row per PHI-Canto entry action. It is **Route 1** of the
submission plan (`docs/CANTO-ROUTE1-BUILD-SPEC.md`), same input as the worksheet — the draft's
structured `canto` block — but optimised for speed and safety at the keyboard.

Deterministic: the same `canto` block always renders the same queue; nothing is invented. Spec:
`PHI-Canto-Literature/active/Worksheet prompt-2026-07-08.md` (curator request).

## When to use
- A draft's `canto` block is populated and a curator wants the practical entry format to work
  through during a live PHI-Canto session (rather than the fuller `canto-worksheet` output).
- Both outputs can coexist for the same draft — the worksheet as the worked record, the queue as
  the click-list.

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

## Expected outputs
- A short header (citation, system, status, model/tool, date).
- Setup tables A–E and annotation tables F1–F5, each row one Canto entry action with a `☐`.
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
