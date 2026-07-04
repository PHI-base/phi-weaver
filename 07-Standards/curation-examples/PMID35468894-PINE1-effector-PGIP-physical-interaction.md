---
type: curation-example
status: validated
topics:
  - effector
  - physical-interaction
  - gene-deletion
  - overexpression
  - complementation
annotation_types:
  - molecular_function
  - biological_process
  - cellular_component
  - host_phenotype
  - pathogen_phenotype
  - pathogen_host_interaction_phenotype
  - physical_interaction
  - wt_rna_expression
  - disease_name
evidence:
  - gene deletion
  - complementation
  - overexpression
  - growth assay
  - biochemical
  - expression analysis
pathogen: Sclerotinia sclerotiorum; Botrytis cinerea
host: Arabidopsis thaliana; Pisum sativum
source: "PMID:35468894"
reviewed_by: Melina Velasquez; Alayne Cuzick
reviewed_date: 2026-07-04
---

# PMID:35468894 — PINE1 effector inactivates plant PGIP (physical interaction) — GOLD STANDARD

> **Validated gold-standard curation**, imported from the PHI-Canto community-curation session
> [010b2ec99d0d70e8](https://canto.phi-base.org/curs/010b2ec99d0d70e8/ro) (read-only), curated by
> **Melina Velasquez** and **Alayne Cuzick** (PHI-Canto v1862). Content kept in PHI-Canto's own
> structure (per the example policy — only the frontmatter above is required for the library).
> This is the library's reference example for the **physical_interaction** annotation type, and
> confirms that protein–protein interactions are in PHI-Canto scope.

## Publication
- **PMID:35468894** — *A fungal extracellular effector inactivates plant
  polygalacturonase-inhibiting protein.* Wei W, Xu L, Peng H, Zhu W, Tanaka K, Cheng J,
  Sanguinet KA, Vandemark G, Chen W. 2022.
- **Pathogens**: *Sclerotinia sclerotiorum* (isolate WMA1); *Botrytis cinerea* (B05.10).
- **Hosts**: *Arabidopsis thaliana* (ecotype Columbia-0); *Pisum sativum* (cv. Guido).
- The effector **PINE1** binds and inactivates the host PGIP (polygalacturonase-inhibiting
  protein), relieving inhibition of the fungal polygalacturonase PG1 (sspg1d).

## Genes / proteins
- **S. sclerotiorum**: `PINE1` (UniProtKB:A0A1D9QD76), `sspg1d` = **PG1** (UniProtKB:Q8NKE6),
  `PG3`, `SS1G_04177`.
- **B. cinerea**: `BCIN_04g02570` (a PINE1 orthologue).
- **A. thaliana** (host): `PGIP1` (UniProtKB:Q9M5J9), `PGIP2` (UniProtKB:Q9M5J8), `FUC1`,
  `At2g35790`.
- *P. sativum*: no genes annotated. (*Arabidopsis lyrata* `ARALYDRAFT_894894` is listed in the
  session but carries no annotations.)

## GO annotations
### Molecular function
| Species | Gene | Term ID | Term name | Evidence | Figure |
| --- | --- | --- | --- | --- | --- |
| S. sclerotiorum | sspg1d | GO:0004650 | polygalacturonase activity | IDA | Fig 4A, 4B |
| A. thaliana | PGIP1 | GO:0090353 | polygalacturonase inhibitor activity | IDA | Fig 4A, 4B, 4C |
| A. thaliana | PGIP2 | GO:0090353 | polygalacturonase inhibitor activity | TAS | — |

### Biological process
| Species | Gene | Term ID | Term name | Evidence | Figure |
| --- | --- | --- | --- | --- | --- |
| S. sclerotiorum | PINE1 | GO:0140590 | effector-mediated suppression of host defense response | EXP | Fig 6 |
| A. thaliana | PGIP1 | GO:0050832 | defense response to fungus | IDA | Fig 4C, 4D |

### Cellular component
| Species | Gene | Term ID | Term name | Evidence | Figure |
| --- | --- | --- | --- | --- | --- |
| A. thaliana | PGIP1 | GO:0048046 | apoplast | IDA | Fig S9E |
| A. thaliana | PGIP1 | GO:0005737 | cytoplasm | IDA | Fig S9E |

Existing low-throughput annotation carried over: PINE1 (A0A1D9QD76) → GO:0005576 extracellular
region (EXP).

## Host phenotype (single-species)
| Species (strain) | Genotype | Term ID | Term name | Evidence | Figure | Extension |
| --- | --- | --- | --- | --- | --- | --- |
| A. thaliana (Col-0) | *PGIP1* transformant (3×Flag)[Overexpression] | PHIPO:0001223 | normal organism morphology | Macroscopic observation (qualitative) | S9F | observed_organ rosette |

## Pathogen phenotype (single-species)
| Species (strain) | Genotype | Term ID | Term name | Evidence | Figure |
| --- | --- | --- | --- | --- | --- |
| S. sclerotiorum (WMA1) | *PINE1Δ* | PHIPO:0001210 | normal hyphal growth | Cell growth assay | S1C |
| S. sclerotiorum (WMA1) | *PG1Δ* (sspg1d) | PHIPO:0001210 | normal hyphal growth | Cell growth assay | S5C |
| S. sclerotiorum (WMA1) | *PG1Δ* (sspg1d) | PHIPO:0000080 | normal asexual sporulation | Asexual sporulation assay | S5D |
| S. sclerotiorum (WMA1) | *PG1Δ* (sspg1d) | PHIPO:0001212 | decreased hyphal growth | Cell growth assay (+ polygalacturonic acid) | S5C |

## Physical interaction annotations  ⭐ (reference example for this type)
| Interactor A | Taxon A | Evidence | Interactor B | Taxon B | Figure |
| --- | --- | --- | --- | --- | --- |
| PGIP1 | 3702 (*A. thaliana*) | Co-purification | sspg1d (PG1) | 5180 (*S. sclerotiorum*) | 2C |
| PGIP1 | 3702 | PCA (interacts with) | sspg1d (PG1) | 5180 | 2B |
| PGIP1 | 3702 | Two-hybrid (binds activation-domain construct with) | PINE1 | 5180 | 1B |
| PGIP1 | 3702 | PCA (interacts with) | PINE1 | 5180 | 1C |
| BCIN_04g02570 | 40559 (*B. cinerea*) | PCA (interacts with) | PGIP1 | 3702 | 7D |

## Pathogen–host interaction phenotype (metagenotype: pathogen genotype × host genotype)
All by Macroscopic observation; 2 days post inoculation unless noted. `ctrl` = compared_to_control.
| Pathogen genotype | Host genotype | Term ID | Term name | Figure | Key extension |
| --- | --- | --- | --- | --- | --- |
| *PINE1+*[WT level] · S. sclerotiorum (WMA1) | wild type *P. sativum* (cv. Guido) | PHIPO:0000954 | presence of pathogen growth within host | 1A | infects_tissue leaf |
| *PINE1Δ* · S. sclerotiorum | wild type *P. sativum* | PHIPO:0000365 | decreased pathogen growth within host | 1A | reduced virulence; ctrl *PINE1+* |
| *PINE1Δ-PINE* transformant (ectopic complement)[Ectopic] · S. sclerotiorum | wild type *P. sativum* | PHIPO:0000954 | presence of pathogen growth within host | 1A, 1B | unaffected pathogenicity; ctrl *PINE1+* |
| *PG1+*[WT level] · S. sclerotiorum | wild type *P. sativum* | PHIPO:0000951 | pathogen growth within host phenotype | 2A | infects_tissue leaf |
| *PG1Δ* · S. sclerotiorum | wild type *P. sativum* | PHIPO:0000365 | decreased pathogen growth within host | 2A | reduced virulence; ctrl *PG1+* |
| *PG1Δ-PG1* transformant (ectopic complement)[Ectopic] · S. sclerotiorum | wild type *P. sativum* | PHIPO:0000954 | presence of pathogen growth within host | 2A | unaffected pathogenicity; ctrl *PG1+ PINE1+* |
| *PINE1+*[WT level] · S. sclerotiorum | wild type *P. sativum* | PHIPO:0000365 | decreased pathogen growth within host | 4C | with_host_peptide Q9M5J9; interaction_outcome disease present |
| *PINE1Δ* · S. sclerotiorum | wild type *P. sativum* | PHIPO:0000952 | abolished pathogen growth within host | 4C | with_host_peptide Q9M5J9; interaction_outcome disease absent |
| *PINE1Δ* · S. sclerotiorum | wild type *P. sativum* | PHIPO:0000481 | absence of pathogen-associated host lesions | 4C, 4D | + polygalacturonase inhibitor; with_host_peptide AtPGIP; reduced virulence; ctrl *PINE1+* |
| *PG1+ PINE1+*[WT level] · S. sclerotiorum | wild type *P. sativum* | PHIPO:0000954 | presence of pathogen growth within host | 4C, 4D | infects_tissue leaf |
| *PINE1Δ* · S. sclerotiorum | *A. thaliana* (Col-0) *PGIP1* transformant[Overexpression]{35S} | PHIPO:0000365 | decreased pathogen growth within host | 6, 7 | reduced virulence; infects_tissue leaf |
| *PG1Δ* · S. sclerotiorum | *A. thaliana* (Col-0) *PGIP1* transformant[Overexpression] | PHIPO:0000365 | decreased pathogen growth within host | 6 | reduced virulence; infects_tissue leaf |
| *PG1+ PINE1+*[WT level] · S. sclerotiorum | *A. thaliana* (Col-0) | PHIPO:0000954 | presence of pathogen growth within host | 6 | infects_tissue leaf |
| wild type · S. sclerotiorum | *A. thaliana* (Col-0) *PGIP1* transformant[Overexpression] | PHIPO:0000365 | decreased pathogen growth within host | 6 | ctrl *PG1+ PINE1+* |
| wild type · S. sclerotiorum | *A. thaliana* (Col-0) *PGIP1* transformant[Overexpression] | PHIPO:0000954 | presence of pathogen growth within host | 7 | infects_tissue leaf |
| *PINE1-GFP*(GFP tag)[Overexpression]{35S} · S. sclerotiorum | *A. thaliana* (Col-0) | PHIPO:0000368 | increased pathogen growth within host | 6 | + wild-type pathogen; increased virulence; ctrl *PG1+ PINE1+* |
| *PINE1+*[Overexpression] · S. sclerotiorum (bkg GFP tag) | wild type *A. thaliana* (Col-0) | PHIPO:0001005 | normal host morphology during pathogen invasion | S9F | pathogen gene expressed by transgenic host; infects_tissue rosette |
| *PINE1+[Overexpression] PG1Δ* · S. sclerotiorum | *A. thaliana* (Col-0) | PHIPO:0000365 | decreased pathogen growth within host | 6 | has_severity medium |
| *PINE1Δ* · B. cinerea (B05.10) | *A. thaliana* (Col-0) *PGIP1+*[WT level] | PHIPO:0000365 | decreased pathogen growth within host | 7 | infects_tissue leaf |

## Wild-type RNA level annotations
| Species | Gene | Level | Evidence | Figure | Extension |
| --- | --- | --- | --- | --- | --- |
| S. sclerotiorum | PINE1 | RNA level increased | Quantitative PCR | S4 | during response to host |
| S. sclerotiorum | sspg1d (PG1) | RNA level increased | Quantitative PCR | S4 | during response to host |
| S. sclerotiorum | PG3 | RNA level increased | Quantitative PCR | S4 | during response to host |

## Disease name annotation
| Pathogen genotype | Host genotype | Term ID | Term name | Figure | Extension |
| --- | --- | --- | --- | --- | --- |
| *PINE1+*[WT level] · S. sclerotiorum (WMA1) | wild type *P. sativum* (cv. Guido) | PHIDO:0000393 | white mold | 1a | infects_tissue leaf |

## phiweaver validation note
`validate_ontology_ids` (2026-07-04): all 23 ontology IDs pass (23/23). The 7 GO terms (across
MF/BP/CC) and 11 PHIPO terms exist and are non-obsolete (via EBI OLS); **PHIDO:0000393 "white
mold"** exists and is non-obsolete (offline, bundled PHIDO ontology); the 4 UniProtKB accessions
(A0A1D9QD76, Q8NKE6, Q9M5J8, Q9M5J9) are format-valid (existence via `query_uniprot.py`).
