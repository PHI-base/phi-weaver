---
type: curation-example
status: validated
topics:
  - effector
  - physical-interaction
  - overexpression
annotation_types:
  - molecular_function
  - biological_process
  - cellular_component
  - host_phenotype
  - gene_for_gene_phenotype
  - post_translational_modification
  - physical_interaction
  - disease_name
evidence:
  - biochemical
  - overexpression
pathogen: Xanthomonas oryzae
host: Oryza sativa
source: "PMID:23498959"
reviewed_by: Hsin-Yu Chang; Martin Urban
reviewed_date: 2026-07-04
---

# PMID:23498959 — creD effector × rice RLCK185 phosphorylation relay — GOLD STANDARD

> **Validated gold-standard curation**, imported from the PHI-Canto community-curation session
> [af2783b6ac77f4c3](https://canto.phi-base.org/curs/af2783b6ac77f4c3/ro) (read-only), curated by
> **Hsin-Yu Chang** (with the disease-name annotation by **Martin Urban**), PHI-Canto v1862.
> Content kept in PHI-Canto's own structure (per the example policy — only the frontmatter above
> is required for the library). This is the library's reference example for the
> **post_translational_modification** annotation type (PSI-MOD phosphorylation).

## Publication
- **PMID:23498959** — *A receptor-like cytoplasmic kinase targeted by a plant pathogen effector is
  directly phosphorylated by the chitin receptor and mediates rice immunity.* Yamaguchi K, Yamada
  K, Ishikawa K, Yoshimura S, Hayashi N, Uchihashi K, Ishihama N, Kishi-Kaboshi M, Takahashi A,
  Tsuge S, Ochiai H, Tada Y, Shimamoto K, Yoshioka H, Kawasaki T. 2013.
- **Pathogen**: *Xanthomonas oryzae* (MAFF311018).
- **Host**: *Oryza sativa* (cv. Nipponbare).
- The chitin receptor CERK1 phosphorylates the receptor-like cytoplasmic kinase RLCK185; the
  *X. oryzae* effector creD (Xoo1488) is targeted to RLCK185 and blocks that phosphorylation.

## Genes / proteins
- **X. oryzae**: `creD` (= locus **Xoo1488**), the effector; NCBI taxon 347.
- **O. sativa** (host; taxon 4530): `CERK1` (UniProtKB:A0A0P0XII1, chitin receptor),
  `RLCK185` (UniProtKB:Q6I5Q6), `Os01g0936100` (= **RLCK55**), `MPK3`, `MPK6`.

## GO annotations
### Molecular function
| Species | Gene | Term ID | Term name | Evidence | Figure |
| --- | --- | --- | --- | --- | --- |
| O. sativa | CERK1 | GO:0106310 | protein serine kinase activity | EXP | Fig 5 |
| O. sativa | RLCK185 | GO:0004672 | protein kinase activity | EXP | Fig 7C |
| O. sativa | CERK1 | GO:0008061 | chitin binding | TAS | — |
| O. sativa | CERK1 | GO:0038187 | pattern recognition receptor activity | EXP | — |
| O. sativa | MPK3 | GO:0004707 | MAP kinase activity | EXP | Fig 6 |
| O. sativa | MPK6 | GO:0004707 | MAP kinase activity | EXP | Fig 6 |

### Biological process
| Species | Gene | Term ID | Term name | Evidence | Figure |
| --- | --- | --- | --- | --- | --- |
| O. sativa | CERK1 | GO:0002768 | immune response-regulating cell surface receptor signaling pathway | EXP | Fig 3 |
| O. sativa | RLCK185 | GO:0002768 | immune response-regulating cell surface receptor signaling pathway | EXP | Fig 3 |
| X. oryzae | creD | GO:0140404 | effector-mediated perturbation of host innate immune response by symbiont | EXP | — |

### Cellular component
| Species | Gene | Term ID | Term name | Evidence | Figure |
| --- | --- | --- | --- | --- | --- |
| O. sativa | RLCK185 | GO:0005886 | plasma membrane | IDA | Fig 2 |
| O. sativa | CERK1 | GO:0005886 | plasma membrane | IDA | Fig 4 |

## Host phenotype (single-species)
All conditions include the PTI inducer **chitin**.
| Species (strain) | Genotype | Term ID | Term name | Evidence | Figure | Extension |
| --- | --- | --- | --- | --- | --- | --- |
| O. sativa (Nipponbare) | *RLCK185*(RNAi)[Knockdown] | PHIPO:0000946 | decreased cellular reactive oxygen species level | Substance quantification | 3I | — |
| O. sativa (Nipponbare) | *RLCK55*(RNAi)[Knockdown] (Os01g0936100) | PHIPO:0000946 | decreased cellular reactive oxygen species level | Substance quantification | 3I | — |
| O. sativa (Nipponbare) | *RLCK185*(RNAi)[Knockdown] | PHIPO:0001120 | decreased protein phosphorylation | Western blot | 6E | assayed_using MPK3 |
| O. sativa (Nipponbare) | *RLCK185*(RNAi)[Knockdown] | PHIPO:0001120 | decreased protein phosphorylation | Western blot | 6G | assayed_using MPK6 |
| O. sativa (Nipponbare) | *RLCK185* transformant (overexpression)[Ectopic] | PHIPO:0001119 | abnormal protein phosphorylation | Western blot | 6B | assayed_using MPK3 |
| O. sativa (Nipponbare) | *RLCK185* transformant (overexpression)[Ectopic] | PHIPO:0001119 | abnormal protein phosphorylation | Western blot | 6D | assayed_using MPK6 |

## Gene-for-gene phenotype (metagenotype: pathogen genotype × host genotype)
| Pathogen genotype | Host genotype | Term ID | Term name | Evidence | Figure | Extension / comment |
| --- | --- | --- | --- | --- | --- | --- |
| *Xoo1488* transformant (overexpression)[Ectopic] · X. oryzae (MAFF311018) | *RLCK185+*[WT level] · O. sativa (Nipponbare) | PHIPO:0001284 | decreased host protein phosphorylation with pathogen | Western blot (+ chitin) | 7 | assayed_using RLCK185; Xoo1488 inhibits CERK1-mediated phosphorylation of RLCK185 |

## Protein modification annotations  ⭐ (reference example for this type; PSI-MOD)
| Species | Gene | Term ID | Term name | Evidence | Figure | Extension |
| --- | --- | --- | --- | --- | --- | --- |
| O. sativa | RLCK185 | MOD:00696 | phosphorylated residue | IDA | 5 | added_by CERK1 |
| X. oryzae | creD | MOD:00696 | phosphorylated residue | IDA | 7C | added_by RLCK185 |
| O. sativa | CERK1 | MOD:00696 | phosphorylated residue | IDA | 5B | added_by CERK1 |
| O. sativa | RLCK185 | MOD:00696 | phosphorylated residue | IDA | 7C | added_by RLCK185 |
| O. sativa | MPK3 | MOD:00696 | phosphorylated residue | IDA | 6A | increased_during defense response to symbiont (+ chitin) |
| O. sativa | MPK6 | MOD:00696 | phosphorylated residue | IDA | 6A | increased_during defense response to symbiont (+ chitin) |

## Physical interaction annotations
| Interactor A | Taxon A | Evidence | Interactor B | Taxon B | Figure |
| --- | --- | --- | --- | --- | --- |
| creD | 347 (*X. oryzae*) | Two-hybrid (binds activation-domain construct with) | RLCK185 | 4530 (*O. sativa*) | 2A |
| creD | 347 | Two-hybrid (binds activation-domain construct with) | Os01g0936100 (RLCK55) | 4530 | 2A |
| RLCK185 | 4530 | Two-hybrid (binds activation-domain construct with) | CERK1 | 4530 | 4A |
| RLCK185 | 4530 | Co-purification | CERK1 | 4530 | 4B |
| RLCK185 | 4530 | PCA (interacts with) | CERK1 | 4530 | 4C |
| creD | 347 | PCA (interacts with) | RLCK185 | 4530 | 7E |

## Disease name annotation
| Pathogen genotype | Host genotype | Term ID | Term name | Curator |
| --- | --- | --- | --- | --- |
| *Xoo1488+*[WT level] · X. oryzae (MAFF311018) | wild type *O. sativa* | PHIDO:0000024 | bacterial blight | Martin Urban |

## phiweaver validation note
`validate_ontology_ids` (2026-07-04): all 16 ontology IDs pass (16/16). The 8 GO terms (across
MF/BP/CC) and 4 PHIPO terms exist and are non-obsolete (via EBI OLS); **MOD:00696 "phosphorylated
residue"** (PSI-MOD) exists and is non-obsolete (via OLS — MOD support added while curating this
example); **PHIDO:0000024 "bacterial blight"** exists (offline, bundled PHIDO ontology); the 2
UniProtKB accessions (A0A0P0XII1, Q6I5Q6) are format-valid (existence via `query_uniprot.py`).
