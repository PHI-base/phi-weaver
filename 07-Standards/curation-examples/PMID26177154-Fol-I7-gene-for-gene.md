---
type: curation-example
status: validated
topics:
  - effector
  - gene-for-gene
annotation_types:
  - gene-annotation
  - interaction-phenotype
evidence:
  - gene deletion
  - overexpression
pathogen: Fusarium oxysporum f. sp. lycopersici
host: Solanum lycopersicum
source: "PMID:26177154"
reviewed_by: Hsin-Yu Chang
reviewed_date: 2026-07-03
---

# PMID:26177154 — Fol effectors × tomato *I-7* (gene-for-gene) — GOLD STANDARD

> **Validated gold-standard curation**, imported from the PHI-Canto community-curation session
> [077ec02bbb46ec45](https://canto.phi-base.org/curs/077ec02bbb46ec45/ro) (read-only), curated by
> **Hsin-Yu Chang** (PHI-Canto v1862). Content kept in PHI-Canto's own structure (per the example
> policy — only the frontmatter above is required for the library).

## Publication
- **PMID:26177154** — *Identification of I-7 expands the repertoire of genes for resistance to
  Fusarium wilt in tomato to three resistance gene classes.* Gonzalez-Cendales Y, Catanzariti AM,
  Baker B, McGrath DJ, Jones DA. 2016.
- **Pathogen**: *Fusarium oxysporum* f. sp. *lycopersici* (races 1/3, isolate Fol007).
- **Host**: *Solanum lycopersicum* (cvs Tristar [carries *I-7*], Moneymaker, M82).

## Genes
- **Pathogen effectors**: `AVR1`, `AVR2` (= `six1`, UniProtKB Q709D8), `AVR3`, `SIX3`.
- **Host**: `A0A3Q7INH0_SOLLC` (the **I-7** immune receptor); `LES1_20t00001` (**EDS1**).

## GO annotations
| Species | Gene | Term ID | Term name | Evidence | Figure | Extension |
| --- | --- | --- | --- | --- | --- | --- |
| F. oxysporum | six1 (AVR2) | GO:0140404 | effector-mediated perturbation of host innate immune response by symbiont | EXP | Fig 2 | with_host_species *S. lycopersicum* |
| F. oxysporum | AVR1 | GO:0140404 | (as above) | EXP | Fig 2 | — |
| F. oxysporum | SIX3 | GO:0140404 | (as above) | EXP | Fig 2 | — |
| S. lycopersicum | A0A3Q7INH0 (I-7) | GO:0140376 | innate immune receptor activity | EXP | — | — |
| S. lycopersicum | A0A3Q7INH0 (I-7) | GO:0002220 | innate immune response activating cell surface receptor signaling pathway | EXP | — | — |
| S. lycopersicum | LES1_20t00001 (EDS1) | GO:0106093 | EDS1 disease-resistance complex | TAS | — | — |
| F. oxysporum | six1 (Q709D8) | GO:0140404 | (as above) — existing low-throughput annotation | EXP | — | — |

## Gene-for-gene phenotype annotations (metagenotype: pathogen genotype × host genotype)
All by Macroscopic observation (quantitative); extension `gene_for_gene_interaction` +
`infects_tissue whole plant` unless noted.

| Pathogen genotype | Host genotype | Term | Figure | Interaction |
| --- | --- | --- | --- | --- |
| AVR3+ (race 3) WT | *I-7+* (Tristar) | PHIPO:0001199 disease absent | Fig 2 | incompatible (effector recognised) |
| AVR3+ (race 3) WT | Moneymaker (no *I-7*) | PHIPO:0001200 disease present | Fig 2 | compatible |
| AVR3+ (race 3) WT | M82 | PHIPO:0001200 disease present | Fig 2 | compatible |
| AVR3+ (race 3) WT | *I-7+* transformant (Tristar *I-7* → M82) [Ectopic] | PHIPO:0001199 disease absent | Fig 2 | incompatible |
| AVR3+ (race 3) WT | *I-7+* transformant (Tristar *I-7* → MM) [Ectopic] | PHIPO:0001199 disease absent | Fig 2 | incompatible |
| AVR1+ AVR2+ AVR3+ (race 1) WT | Moneymaker | PHIPO:0001200 disease present | Fig S4 | compatible |
| AVR1+ AVR2+ AVR3+ (race 1) | *I-7+* (Tristar) | PHIPO:0001199 disease absent | Fig S4 | incompatible |
| AVR1+ AVR2+ AVR3+ (race 1) | *I-7+* transformant (Tristar → MM) [Ectopic] | PHIPO:0001199 disease absent | Fig S4 | incompatible |
| AVR2+ AVR3+ (Fol007) WT | Moneymaker | PHIPO:0001200 disease present | Fig S5 | compatible |
| AVR2+ AVR3+ (Fol007) | *I-7+* (Tristar) | PHIPO:0001199 disease absent | Fig S5 | incompatible |
| AVR2+ AVR3+ (Fol007) | *I-7+* transformant (Tristar → MM) [Ectopic] | PHIPO:0001199 disease absent | Fig S5 | incompatible |
| AVR3+ (race 3) WT | *eds1Δ / eds1Δ* *I-7+* (Tristar) | PHIPO:0001200 disease present | Fig 4 | *has_severity* high — EDS1 loss restores susceptibility |
| AVR3+ (race 3) WT | *EDS1+ / eds1Δ* *I-7+* (Tristar) | PHIPO:0001200 disease present | Fig 4 | *has_severity* medium |

## Disease name annotation
| Pathogen genotype | Host genotype | Term ID | Term name | Figure |
| --- | --- | --- | --- | --- |
| AVR1+ AVR2+ AVR3+ (race 1) WT | Moneymaker | PHIDO:0000164 | Fusarium wilt | Fig 2 |

## phiweaver validation note
`validate_ontology_ids` (2026-07-04): all 7 ontology IDs exist and are non-obsolete (7/7).
The GO and PHIPO terms resolve online via EBI OLS; **PHIDO:0000164** (Fusarium wilt) resolves
offline against the bundled PHIDO ontology (`phiweaver/lookup/data/phido.obo`, vendored from
github.com/PHI-base/phido) — OLS4 does not host PHIDO. (Superseded the earlier note that PHIDO
could not be verified; that tooling gap is now closed.)
