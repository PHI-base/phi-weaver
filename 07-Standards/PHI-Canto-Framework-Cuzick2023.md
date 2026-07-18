---
created: 2026-07-15
type: standards
tags: [standards]
project: PHI-Canto
---

# PHI-Canto curation framework — Cuzick et al. 2023 (reference extract)

**Authoritative published source for the curation model this project implements.** This is
a curation-relevant extract, not the paper. The PDF itself lives outside this repo (in the
`OBS-MU-ResearchLab` vault) and is **deliberately not committed** — do not copy it here.

> Cuzick A, Seager J, Wood V, **Urban M**, Rutherford K, Hammond-Kosack KE. *A framework for
> community curation of interspecies interactions literature.* **eLife** 2023;12:e84658.
> DOI: [10.7554/eLife.84658](https://doi.org/10.7554/eLife.84658) · PMID: **37401199** ·
> CC-BY (free to quote with attribution). Martin Urban is a co-author.

This paper defines PHI-Canto, the metagenotype concept, PHIPO, and the annotation-extension
model that [[PHI-Canto-Curation-Conventions]] and [[Ontology-Terms-Reference]] encode, and
that `phiweaver/lookup/extension_config.py` validates. Where the config files were
reverse-engineered, this is the primary source that **confirms and explains** them.

## Core concepts

- **Metagenotype** — the key new idea: a multispecies genotype = a pathogen genotype **+** a
  host genotype, created after both single-species genotypes exist. Phenotypes capturing
  changes in pathogenicity/virulence are annotated on the *metagenotype*. A metagenotype must
  include ≥1 named pathogen gene of interest; the host part may be just the wild-type host
  species/strain if no host gene is referenced.
- **Pathogenicity vs virulence** — pathogenicity = the pathogen's ability to *cause* disease
  (altered by pathogen changes); virulence = the *severity* of disease once caused (can
  depend on the host). This distinction underlies the `infective_ability` value set below.
- **Pre-compositional PHIPO** — terms are pre-composed from other ontologies so the curator
  picks one term, e.g. `resistance to penicillin` (PHIPO:0000692) rather than composing
  `increased resistance to chemical` + `penicillin` (CHEBI). PHIPO is species-neutral, in
  OBO/OWL on OBO Foundry.

## Annotation types by biological feature (Table 1)

Three annotatable biological features, each with its own annotation types:

| Feature | Annotation types | Primary value |
|---|---|---|
| **Gene** | GO annotation (MF/BP/CC), Wild-type expression, protein modification, physical interaction | GO / PSI-MOD / BioGRID |
| **Genotype** (pathogen or host) | Single-species phenotype (Pathogen / Host phenotype) | PHIPO single-species branch |
| **Metagenotype** | Pathogen–host interaction phenotype · Gene-for-gene phenotype · Disease name | PHIPO PHI branch / PHIDO |

## Annotation extensions (AEs) — the model behind `extension_config.py`

PHI-Canto uses **44 AE relations — 9 unique to PHI-base, 35 shared with PomBase.** AEs add
qualifying detail to a primary annotation. The paper is the authoritative source for the
relations and their value types encoded in `phipo_extensions.tsv` / `phibase_go_extensions.tsv`
/ `phido_extensions.tsv`. Notable confirmations of the reverse-engineered config:

- **`extent of infectivity`** (config relation **`infective_ability`**) — a **PHIPO term**;
  applies only to pathogen–host interaction phenotypes. This is the AE that carries "reduced
  virulence". See [[PHI-Canto-Framework-Cuzick2023#Annotation-extension value lists]].
- **`outcome of interaction`** (`interaction_outcome`) — a PHIPO term; PHI phenotypes only.
- **`gene-for-gene interaction`** / **`inverse gene-for-gene interaction`** — **PHIPO_EXT**
  terms; gene-for-gene phenotypes only.
- **`compared to control metagenotype`** (`compared_to_control`) — a Metagenotype (a WT
  control created in the same session). Introduced specifically so an altered metagenotype's
  phenotype is informative.
- **`host tissue infected`** / **`observed in organ`** — BRENDA Tissue (BTO). `observed in
  organ` is restricted to `BTO:0001489`, `BTO:0001494`, `BTO:0001461` **and descendants** —
  this exactly matches the `observed_organ` range in `phipo_extensions.tsv`.
- **`with host species`** / **`with symbiont species`** — NCBI Taxonomy IDs (the GO-config
  `taxon_id` ranges).
- **penetrance / severity** — qualitative (low/normal/high/…) or quantitative (%).

### Annotation-extension value lists (Appendix 1)

The paper enumerates the actual allowed values — the *child terms* under each term-typed AE
gate. This is the authoritative list weaver was previously guessing:

- **`extent of infectivity` (`infective_ability`, under PHIPO:0001179):**
  `loss of pathogenicity`, `unaffected pathogenicity`, `reduced virulence`,
  `increased virulence`; for mutualism: `mutualism present`, `mutualism absent`,
  `loss of mutualism` (formerly "enhanced antagonism"). These are the **nine legacy
  high-level terms** carried forward from PHI-base 4.
- **`outcome of interaction` (`interaction_outcome`, under PHIPO:0001198):**
  `disease present`, `disease absent`.
- **`gene-for-gene` / `inverse gene-for-gene` (PHIPO_EXT):** a fixed set of ~11 compound
  strings encoding *(i) compatibility of the interaction, (ii) functional status of the
  pathogen effector, (iii) functional status of the host R/S gene* — e.g. *"incompatible
  interaction, recognizable pathogen effector present, functional host resistance gene
  present"*, … , *"metagenotype outcome overcome by external condition"*. → This partly
  answers the open PHIPO_EXT gap in [[docs/BACKLOG]]: the value **labels** are now known
  (the term **IDs** still are not).

## Controlled vocabularies & ontologies used

- **PHIPO** — pathogen–host interaction + single-species phenotypes (pre-compositional).
- **PHIPO_EXT** — extension-only terms (gene-for-gene). Never a primary term.
- **FYPO_EXT** — wild-type RNA/protein level annotations; penetrance/severity units.
- **BTO** (BRENDA Tissue) — infected/observed tissue.
- **PHIDO** — PHI-base disease names (a placeholder CV, plant/human/animal/invertebrate).
- **PHI-ECO** — experimental conditions, incl. `delivery mechanism: …` terms; free text
  allowed then curator-reviewed.
- **ECO** — experimental evidence codes; PHI-specific codes submitted to ECO. Examples:
  `cell growth assay evidence` (ECO:0001563), `qualitative macroscopy evidence` (ECO:0006342),
  `microscopy evidence` (ECO:0001098).
- **GO** — gene product function; **effector** curation uses `effector-mediated modulation of
  host process by symbiont` (**GO:0140418**) or a descendant (e.g. GO:0052034), created with
  the GO Consortium; effector activities can add MF terms (e.g. enzyme inhibitor GO:0004857).
- **PSI-MOD** (protein modifications), **BioGRID** (physical/genetic interaction types).

## Ten trial-curation publications (Table 2) — candidate gold-standard set

Each was curated to develop the framework; each maps to an annotation pattern with a worked
example in Appendix 1. Useful as a validated example library:

| PMID | Interaction | Pattern illustrated |
|---|---|---|
| 28715477 | Bacteria–human | unaffected pathogenicity |
| 28720735 | Fungal–human (antifungal target) | altered pathogenicity/virulence |
| 30459352 | Secondary-metabolite virulence | altered pathogenicity/virulence |
| 29020037 | Early-acting virulence protein | altered pathogenicity/virulence; in vitro pathogen phenotype |
| 16517760 | Mutualism | mutualism (loss of mutualism) |
| 31804478 | First host target of effector | a pathogen effector; GO effector BP/MF |
| 30220500 | Receptor decoys | a pathogen effector |
| 20601497 | R–Avr interaction | gene-for-gene interaction; in vivo host phenotype |
| 22241993 | Necrotrophic effector SnTox1 | inverse gene-for-gene |
| 22314539 | Antifungal resistance (cyp51C) | in vitro pathogen chemistry phenotype |

## Key curation problems & solutions (Table 3)

- **Species strain** — UniProtKB sequence is from a reference strain; PHI-Canto keeps a
  selectable curated strain list (NCBI dropped strain-level taxIDs).
- **Delivery mechanism** — captured as `delivery mechanism: …` PHI-ECO terms.
- **Physical interaction across species** — Canto's physical-interaction module adapted to
  two species (pathogen effector ↔ first host target).
- **Pathogen effector** — no phenotype term fit "effector"; new GO BP terms created instead.
- **Wild-type control phenotypes** — new `compared to control` AE + WT metagenotypes.
- **Chemistry** — pre-composed PHIPO terms with ChEBI chemical names (PomBase model).
- **Nine legacy PHI-base 4 terms** — kept as PHI-base 5 tags via mapping.

## Related in this repo

- [[Ontology-Terms-Reference]] — the ontologies + the attested extension-relations table.
- [[PHI-Canto-Curation-Conventions]] — the working conventions (interaction primary term,
  `infective_ability` rule, WT controls, gene-for-gene / PHIPO_EXT).
- `phiweaver/lookup/extension_config.py` + `data/README.md` — offline validation of the AE
  relations this paper defines.
- `05-Protocols/PHI-Canto-Complete-Curation-Protocol.md` and
  `00-Inbox/NEW-INFO/Supplementary Text 1 PHI-Canto documentation …md` — the paper's
  Supplementary Text 1 (PHI-Canto user documentation).
