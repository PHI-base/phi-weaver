---
created: 2026-07-12
type: training
tags: [training]
project: PHI-Canto
---

# Reviewing PHI-Weaver Drafts — a guide for collaborating biocurators

*You receive PHI-Weaver drafts and enter the curation into PHI-Canto yourself. This guide explains what the draft contains, how to work through it, and — most importantly — how to read the flags that tell you where the tool stopped and your judgement takes over. It assumes you already know PHI-Canto curation; it does not teach the biology or the tool's internals.*

---

## The one rule

A PHI-Weaver draft is a set of **suggestions produced by an AI**, not a finished curation. Every gene, allele, genotype, term, and evidence code in it is a proposal for you to confirm, correct, or reject before it enters PHI-Canto. You own every annotation you submit. The tool is built so that it never invents an accession, an ontology term, or an evidence code — when it is unsure, it flags the item and holds it back rather than guessing — but that guarantee only works if you treat the flagged items as decisions waiting for you, not as an oversight to skip past.

## What you receive

For each paper you will typically get two markdown files that share a name stem:

- a **draft** (`…-phiweaver-DRAFT.md`) — the fuller working record of the curation, with the reasoning and evidence behind each item;
- an **entry queue** (`…-phi-canto-entry-queue.md`) — a condensed, table-driven click-list that mirrors PHI-Canto's exact entry order.

**Work from the entry queue.** It is laid out to be followed top to bottom with PHI-Canto open beside it, ticking each row as you enter it. Keep the draft open as the reference you consult when you need the evidence behind a row — for example when you are deciding whether to accept a proposed phenotype term.

## Where the files live

Input papers and output drafts are exchanged through a **shared Google Drive folder** (`PHI-Canto-Literature`), synced with Google Drive for Desktop so you work from your normal file explorer — no repository checkout needed. It has three sub-folders:

- **`active/` — drop input here.** Put the paper PDF you want curated into `active/`. This is also where the converted markdown and extracted figures for a paper in progress appear.
- **`completed/` — collect output here.** When a paper is drafted, its `…-phiweaver-DRAFT.md` and `…-phi-canto-entry-queue.md` (the two files described above) are placed in `completed/`, alongside the original PDF. This is the folder you review from.
- **`media/`** — extracted images and figures the drafts reference.

A file may take a moment to appear after it is added, while Google Drive finishes syncing it to your machine. If a paper you expect isn't there yet, give the sync a minute before asking. You only ever read from and write papers into this Drive folder; nothing about the tool itself needs to be installed on your side.

**See:** `docs/STORAGE-CONFIGURATION.md` ("Storage on Google Drive") for the one-time setup and the exact folder path.

## How the entry queue is laid out

Every entry queue opens with a header line naming the paper and the biological system, for example:

> `System: Candida albicans -> Mus musculus (disseminated candidiasis / in-vivo filamentation) · Status: draft · Model/tool: Fable 5 · Date: 2026-07-05`

`Status: draft` is a reminder that nothing here has been reviewed yet — that is your job. The body then follows PHI-Canto's own sequence, in lettered sections you enter in order:

- **A. Enter genes first** — each gene with its species and an "Add-gene identifier". The rightmost column reads either **`enter`** (the gene is resolved and ready) or **`hold`**.
- **B. Create alleles**, **C. Create pathogen genotypes**, **D. Create host genotype**, **E. Create metagenotypes** — the pathogen and host constructs, with a `Use` column marking each as `control`, `host`, or `experimental`.
- **F. Annotation entry queue** — the annotations themselves, split into five tables: **F1 GO**, **F2 Physical interaction**, **F3 Pathogen phenotype**, **F4 Pathogen–host interaction phenotype**, and **F5 Disease**. Each row carries the subject, the proposed term with its ontology ID, an evidence summary, and the figure or table it comes from.
- **G. Parked items — do not enter yet** — everything the tool declined to put in an entry table. Read this section carefully; it is covered in detail below.
- **Queue summary** — a count of enter-ready genes and annotations against held genes and parked items, so you can see at a glance how much of the paper is ready.

Each entry row begins with a tick box (`☐`). Tick it as you enter the item into PHI-Canto so you can put the guide down and pick it up without losing your place.

## Reading a ready gene versus a held gene

The gene table is where a paper is decided. Compare two real cases.

In a clean draft, the gene resolves:

> `☐ | EFG1 | Candida albicans | UniProtKB:Q59X67 | enter`

The accession is present and the status is `enter`. You add the gene to PHI-Canto and continue.

In a blocked draft, it does not:

> `☐ | fleQ | Pseudomonas syringae pv. tabaci | unresolved | hold`

The identifier is `unresolved` and the status is `hold`. A held gene has a consequence that propagates through the whole paper: **everything that depends on it is parked.** Its alleles, its genotypes, its metagenotypes, and every annotation on them move to Section G rather than into the entry tables. This is deliberate — an annotation entered against an unresolved gene would be anchored to nothing — but it means a paper with a held gene can look almost empty in Sections A–F and very full in Section G. The FleQ/GcbB paper is the extreme case: two held genes, one enter-ready annotation, and forty-two parked items. That is not a failed draft; it is the tool telling you the single thing that unblocks the paper is resolving those two accessions.

## The annotation tables (F1–F5)

Within the F tables the rows are ready to enter, but "ready" still means "ready for your confirmation." Read the evidence summary and the figure reference against your own reading of the paper before you accept a term. A few things the tool deliberately surfaces for you rather than deciding on its own:

- **Negative and no-change results.** A phenotype row may be a deliberate negative — for example a phosphomimetic allele annotated as `normal hyphal growth — PHIPO:0001210` with the note "NEGATIVE result — curator policy on recording no-change." Whether and how to record no-change results is a curation-policy call that is yours, not the tool's.
- **Gene-dosage and control subtleties.** A reintegrant control annotated with "modest haploinsufficiency (gene-dosage effect only)" is flagging a judgement about how to treat the control.
- **Alternative terms.** A disease row may propose a term and then list alternatives, for example "alt narrower: PHIDO:0000458 invasive candidiasis." You pick the granularity that fits.
- **The `Compared with` column** in the interaction-phenotype table (F4) records the control the phenotype was scored against — check it matches how you would frame the comparison.

## Section G — the part that most needs you

The parked section is the tool's safety filter. An item is parked when entering it would require a judgement or a piece of information the tool refused to guess. **A parked item is a decision waiting for you, not a mistake to ignore.** A `⚠` symbol marks items that need particular attention. The "Why parked" column tells you the reason; these are the common ones and what each asks of you:

- **`unresolved UniProtKB accession`** — the tool could not resolve the gene to a single accession. Sometimes there is genuinely no UniProt entry (the FleQ example notes the Pta6605 proteome is not indexed in UniProt); sometimes there are several candidates and the tool refuses to pick (the URA5 example lists 25 TrEMBL candidates and names four plausible ones, but leaves the serotype-D match to you). **Action: resolve the accession yourself, then the whole cascade below it can be entered.** Where the tool names a reference ortholog from another species, note its explicit warning — for example "do NOT use as the Pta entity" — that ortholog is a hint for finding the right accession, not the accession to enter.
- **`gene is held` / `uses a held allele` / `depends on a held genotype`** — these are the cascade. They are parked only because something upstream is held; once you resolve the gene, they become enterable as written.
- **`interpretive molecular-function (no direct assay)`** — a molecular-function claim inferred from homology or role rather than demonstrated in this paper (for example a transcription-factor activity with "no direct assay"). **Action: decide whether the evidence supports entering it.**
- **`no ontology term resolved`** — the tool found a real phenotype in the paper but no matching ontology term, so it parked it rather than approximate. For example a "biofilm-formation defect" flagged with "pick term at entry." **Action: choose the term at entry using your expertise.**
- **Notes that read "curator may refine"** — the tool entered a defensible general term but is telling you a more specific one may be justified, as with a disease annotation where "organ pathology not characterised."

## Reading the queue summary

The closing summary quantifies the state of the paper:

> `Enter-ready genes: 1 · held genes: 0`
> `Enter-ready annotations: 12 · parked items: 2`
> `Unresolved blockers (held genes): none`

Read the blockers line first. "none" means the paper is ready to enter end to end and your review is a check of the proposed terms and evidence. A named blocker (`Unresolved blockers (held genes): fleQ, gcbB`) means the paper cannot be meaningfully entered until you resolve those accessions — start there rather than working through the parked cascade item by item.

## Provenance

Each file ends with a one-line footer recording the model and the exact version of the tool that produced it (`phiweaver · <model> · commit <hash> · date`). You do not need to act on it, but it is what lets a draft be traced back to precisely what generated it if a question arises later. The `Model/tool` field in the header carries the same purpose.

## When a draft is wrong

Expect to correct things — that is the design, not a failure. Enter your corrected version into PHI-Canto; the draft has no authority over your judgement. Where you find a systematic problem — a term the tool keeps proposing wrongly, a convention it misses, a recurring mis-resolution — report it by opening an issue at <https://github.com/PHI-base/phi-weaver/issues>, because those corrections are exactly what improves later drafts. A one-line note ("it keeps proposing the general disease term where the paper supports the systemic one") is enough to act on. Individual accession resolutions you make are worth reporting there too, since a resolved gene often recurs across papers. Include the PMID so the correction can be traced to the draft it came from.

---

*Companion references: `06-Training/PHI-Canto-Curator-Onboarding.md`, the `Quick-Reference-*` cards in this folder, and `05-Protocols/PHI-Canto-Complete-Curation-Protocol.md`. Worked examples cited above: the Efg1 paper (PMID:41170998) as a clean queue and the FleQ/GcbB paper (PMID:41229162) as a fully-blocked one.*
