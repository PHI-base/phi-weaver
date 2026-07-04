---
type: curation-example
status: validated
topics:
  - effector
  - gene-for-gene
  - physical-interaction
  - overexpression
annotation_types:
  - molecular_function
  - biological_process
  - pathogen_host_interaction_phenotype
  - gene_for_gene_phenotype
  - physical_interaction
  - wt_protein_expression
  - disease_name
evidence:
  - biochemical
  - overexpression
  - gene deletion
pathogen: Magnaporthe oryzae
host: Oryza sativa
source: "PMID:37177781"
reviewed_by: Hsin-Yu Chang
reviewed_date: 2026-07-04
---

# PMID:37177781 — AvrPi9 effector × rice E3 ligase OsRGLG5 — GOLD STANDARD

> **Validated gold-standard curation**, imported from the PHI-Canto community-curation session
> [cb26f7722454cfbe](https://canto.phi-base.org/curs/cb26f7722454cfbe/ro) (read-only), curated by
> **Hsin-Yu Chang** (PHI-Canto v1862). Content kept in PHI-Canto's own structure (per the example
> policy — only the frontmatter above is required for the library). This is the library's
> reference example for the **wt_protein_expression** annotation type (wild-type protein level).

## Publication
- **PMID:37177781** — *The E3 ubiquitin ligase OsRGLG5 targeted by the Magnaporthe oryzae effector
  AvrPi9 confers basal resistance against rice blast.* Liu Z, Qiu J, Shen Z, Wang C, Jiang N,
  Shi H, Kou Y. 2023.
- **Pathogen**: *Magnaporthe oryzae* (isolates R01-1, KJ201).
- **Host**: *Oryza sativa* (cv. Taipei 309; TP309-Pi9 carries the *Pi9* resistance gene).
- The effector **AvrPi9** and the host E3 ubiquitin ligase **OsRGLG5** target each other for
  degradation; OsRGLG5 confers basal resistance to rice blast.

## Genes / proteins
- **M. oryzae**: `MGG_12655` (**AvrPi9**), UniProtKB:G4NJP7; NCBI taxon 318829.
- **O. sativa** (host; taxon 4530): `Os06g0608800` (**OsRGLG5**, E3 ubiquitin ligase),
  UniProtKB:Q69V56.

## GO annotations
### Molecular function
| Species | Gene | Term ID | Term name | Evidence | Figure |
| --- | --- | --- | --- | --- | --- |
| O. sativa | Os06g0608800 | GO:0004842 | ubiquitin-protein transferase activity | EXP | Fig 3A |

### Biological process
| Species | Gene | Term ID | Term name | Evidence | Figure |
| --- | --- | --- | --- | --- | --- |
| M. oryzae | MGG_12655 | GO:0140404 | effector-mediated perturbation of host innate immune response by symbiont | EXP | — |
| O. sativa | Os06g0608800 | GO:0050832 | defense response to fungus | EXP | — |

## Pathogen–host interaction phenotype (metagenotype: pathogen genotype × host genotype)
All by Macroscopic observation; `ctrl` context noted where given.
| Pathogen genotype | Host genotype | Term ID | Term name | Figure | Key extension |
| --- | --- | --- | --- | --- | --- |
| *AvrPi9+*[Ectopic] · M. oryzae (R01-1) | wild type *O. sativa* (Taipei 309) | PHIPO:0000368 | increased pathogen growth within host | 1 | pathogen gene expressed by transgenic host; + wild-type pathogen; infects_tissue seedling |
| *AvrPi9+*[Ectopic] · M. oryzae (KJ201) | wild type *O. sativa* (Taipei 309) | PHIPO:0000368 | increased pathogen growth within host | 1 | pathogen gene expressed by transgenic host; + wild-type pathogen; infects_tissue seedling |
| *AvrPi9+*[Ectopic] · M. oryzae (R01-1) | wild type *O. sativa* (Taipei 309) | PHIPO:0001192 | decreased level of host defense-induced reactive oxygen species | 1G | pathogen gene expressed by transgenic host; + PTI inducer chitin; infects_tissue seedling |
| wild type · M. oryzae (R01-1) | *Rglg5Δ* · O. sativa (Taipei 309) | PHIPO:0000368 | increased pathogen growth within host | 5A, 5B | 7 dpi; infects_tissue seedling |
| wild type · M. oryzae (KJ201) | *Rglg5Δ* · O. sativa (Taipei 309) | PHIPO:0000368 | increased pathogen growth within host | 5C, 5D | 7 dpi; infects_tissue seedling |
| wild type · M. oryzae (R01-1) | *Rglg5-OE* transformant (overexpression)[Ectopic] · O. sativa | PHIPO:0000365 | decreased pathogen growth within host | 5E, 5F | 7 dpi; infects_tissue seedling |
| wild type · M. oryzae (KJ201) | *Rglg5-OE* transformant (overexpression)[Ectopic] · O. sativa | PHIPO:0000365 | decreased pathogen growth within host | 5G, 5H | 7 dpi; infects_tissue seedling |

## Gene-for-gene phenotype (metagenotype)
| Pathogen genotype | Host genotype | Term ID | Term name | Figure | Interaction |
| --- | --- | --- | --- | --- | --- |
| wild type · M. oryzae (R01-1, *AvrPi9−*) | *Rglg5Δ* · O. sativa (TP309-Pi9) | PHIPO:0000954 | presence of pathogen growth within host | 6A–F | gene_for_gene_interaction compatible (no recognisable effector); infects_tissue leaf |
| wild type · M. oryzae (KJ201, *AvrPi9*) | *Rglg5Δ* · O. sativa (TP309-Pi9) | PHIPO:0000952 | abolished pathogen growth within host | 6G–H | gene_for_gene_interaction incompatible (effector recognised); infects_tissue leaf |

## Physical interaction annotations
| Interactor A | Taxon A | Evidence | Interactor B | Taxon B | Figure |
| --- | --- | --- | --- | --- | --- |
| MGG_12655 | 318829 (*M. oryzae*) | Two-hybrid (binds activation-domain construct with) | Os06g0608800 | 4530 (*O. sativa*) | 2A |
| MGG_12655 | 318829 | PCA (interacts with) | Os06g0608800 | 4530 | 2B |
| MGG_12655 | 318829 | Co-purification | Os06g0608800 | 4530 | 2C |

## Wild-type protein level annotations  ⭐ (reference example for this type)
| Species | Gene | Level | Evidence | Figure | Comment |
| --- | --- | --- | --- | --- | --- |
| M. oryzae | MGG_12655 | protein level decreased | Western blot | 3 | OsRGLG5 targets AvrPi9 for ubiquitination and degradation |
| O. sativa | Os06g0608800 | protein level decreased | Western blot | 4 | AvrPi9 affects the stability of OsRGLG5 |

## Disease name annotation
| Pathogen genotype | Host genotype | Term ID | Term name |
| --- | --- | --- | --- |
| *AvrPi9+*[WT level] · M. oryzae (KJ201) | wild type *O. sativa* (Taipei 309) | PHIDO:0000315 | rice blast |

## phiweaver validation note
`validate_ontology_ids` (2026-07-04): all 11 ontology IDs pass (11/11). The 3 GO terms and 5
PHIPO terms exist and are non-obsolete (via EBI OLS); **PHIDO:0000315 "rice blast"** exists
(offline, bundled PHIDO ontology); the 2 UniProtKB accessions (G4NJP7, Q69V56) are format-valid
(existence via `query_uniprot.py`). The wild-type protein-level annotations carry a level
qualifier ("protein level decreased"), not an ontology ID.
