---
name: gene-for-gene
description: Curate gene-for-gene and effector–host interactions (guard/decoy vs direct recognition, effector GO tagging, R-gene extensions, inverse gene-for-gene/NETS). Use when a paper reports an avirulence/effector gene recognised by a host resistance gene, or an effector acting on a host target.
backing_script: null
tests: null
inputs:
  - resolved pathogen effector/Avr gene and, where known, the host R gene and/or host target (from uniprot-lookup)
  - the recognition model the paper supports (direct AVR–R, or guard/decoy via a host target)
  - host cultivars with their R-gene presence/absence
  - delivery mechanism (native infection, Agrobacterium, transgenic host expression)
outputs:
  - effector gene GO annotation(s) led by an `effector-mediated …` term, plus host-target / R-gene GO where evidenced
  - gene-for-gene interaction phenotype(s) on metagenotypes, with R-gene presence/absence and heterologous-system extensions
  - the WT / effector-mutant / complement comparative set, and an explicit note for inverse (NETS) or guard-model cases
---

# Gene-for-gene curation

## Purpose
Turn an avirulence/effector-vs-resistance paper into review-ready PHI-Canto annotations that
capture the recognition model correctly — direct AVR–R **or** the guard/decoy model where the
effector acts on a host target that an R protein monitors. Full reference:
`06-Training/Gene-for-Gene-Curation-Methodology.md` (curator methodology, H-Y Chang).

This skill is the gene-for-gene layer on top of the general workflow: entities come from
**uniprot-lookup**, alleles/genotypes from **genotype-creation** (which owns the controlled
genotype-label vocabulary), PHIPO terms from **phipo-mapping**, and the assembled annotation
from **phenotype-annotation**. Use it when the annotation type is gene-for-gene.

## When to use
- A pathogen *Avr*/effector gene is recognised (directly or indirectly) by a host *R* gene.
- An effector is shown to target a host protein, with or without an R-protein guard.
- Inverse cases: an effector–host interaction that causes **susceptibility** rather than
  resistance (e.g. necrotrophic effector / NETS).

## Model first: direct vs guard/decoy
Decide which model the evidence supports before modelling entities:

- **Direct recognition (classic):** effector → R protein → immunity. Model the effector and
  the R protein; the interaction is the recognition itself.
- **Guard/decoy (common):** effector → **host target** → R protein detects the modification →
  immunity. Model the effector, the **host target** (a first-class entity — often defence
  signalling, vesicle trafficking, transcription, or hormone signalling), and the R protein.
  Do not collapse the host target into the R protein.

Record which model the paper supports; if the mechanism is unresolved, say so rather than
forcing a direct AVR–R relationship.

## Workflow
1. **Effector GO tagging (mandatory for effectors).** Every curated effector carries a GO
   Biological Process term beginning `effector-mediated …` (e.g. GO:0140418) as its primary
   identifier. Add `secretion by cell` (BP) and `host cell nucleus` / `host cell cytoplasm`
   (CC) **only** where experimentally evidenced.
   - **Boundary:** this rule is for *bona fide* effectors. Do **not** apply `effector-mediated`
     GO terms to transcription factors, kinases, or other non-effector genes just because they
     affect virulence (phiweaver has correctly refused this for e.g. NsdD, Rad53, TRAPPIII).
2. **Host-protein GO** (guard model): curate `innate immune receptor activity` (MF) /
   `innate immune response` (BP) for the R protein, and the host target's own function, only
   where the experiment shows it.
3. **Genotypes** via genotype-creation, using the controlled labels (`gene-OE`, `gene-GFP`,
   `ΔSP`, `ΔLRR`, `aaS…[Ectopic]`, `(non-func)…[WT level]`, `si…`, `[Null]`). Assign
   pathogen **strains** and host **cultivars** accurately — cultivar identity encodes R-gene
   presence/absence.
4. **Metagenotypes:** link pathogen genotype × host species × host cultivar. The comparative
   set for causal attribution is **WT pathogen × host**, **effector-mutant × host**, and
   **complement × host**.
5. **Gene-for-gene phenotype annotation:** pick the PHIPO term (phipo-mapping) and add
   extensions — R-gene **presence/absence** (e.g. `Rlm4, Rlm6` present vs no R gene), and any
   **heterologous system** used (e.g. `heterologous species: Arabidopsis thaliana`).
6. **Delivery mechanism:** record how the effector was introduced (native infection,
   Agrobacterium-mediated, or transgenic-host expression) as metadata — it changes
   interpretation.
7. **Disease name:** assign only from the **wild-type pathogen on its natural host** — never
   from mutants or artificial/heterologous systems.
8. **Inverse gene-for-gene (NETS):** where the effector–R interaction yields susceptibility
   (e.g. Tsn1–SnToxA, programmed cell death → NE-triggered susceptibility), annotate the
   susceptibility outcome and flag the mechanism explicitly for the curator.

## Expected outputs
- Effector gene annotation led by an `effector-mediated …` GO term (+ evidenced BP/CC terms).
- R-protein / host-target GO where evidenced (guard model).
- Gene-for-gene interaction phenotype(s) on metagenotypes, with R-gene presence/absence and
  heterologous-system extensions, and the WT/mutant/complement comparative set.
- Disease name from WT × natural host only.
- Explicit model call (direct vs guard/decoy) and a flag for inverse/NETS or unresolved cases.

## Quality-control checks
- The recognition model (direct vs guard/decoy) is stated and matches the evidence; the host
  target is modelled as its own entity in guard cases.
- Effectors carry an `effector-mediated …` GO term; non-effectors do **not**.
- Host cultivars are specified and their R-gene status is captured in the annotation.
- Pathogen phenotypes are recorded only where different from WT (many effector mutants show
  none); interaction phenotypes link the comparative control metagenotype.
- Disease name derives only from WT pathogen × natural host.

## Human review
Every annotation is a draft suggestion. A curator confirms the model, terms, evidence,
cultivar/R-gene assignments and extensions in PHI-Canto before submission. Flag guard-model
host targets, inverse (NETS) mechanisms, and any unresolved recognition mechanism prominently.
