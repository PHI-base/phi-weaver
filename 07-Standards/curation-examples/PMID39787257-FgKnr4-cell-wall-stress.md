---
type: curation-example
status: validated
topics:
  - gene-deletion
  - chemical-sensitivity
annotation_types:
  - biological_process
  - pathogen_phenotype
  - pathogen_host_interaction_phenotype
  - disease_name
evidence:
  - gene deletion
  - microscopy
  - growth assay
pathogen: Fusarium graminearum; Zymoseptoria tritici
host: Triticum aestivum
source: "PMID:39787257"
reviewed_by: Hsin-Yu Chang
reviewed_date: 2026-07-04
---

# PMID:39787257 — Knr4/Smi1 (FgKnr4, ZtKnr4) cell-wall-stress & pathogenesis — GOLD STANDARD

> **Validated gold-standard curation**, imported from the PHI-Canto community-curation session
> [02e545aba274d209](https://canto.phi-base.org/curs/02e545aba274d209/ro) (read-only), curated by
> **Hsin-Yu Chang** (PHI-Canto v1862). Content kept in PHI-Canto's own structure (per the example
> policy — only the frontmatter above is required for the library).

## Publication
- **PMID:39787257** — *A conserved fungal Knr4/Smi1 protein is crucial for maintaining cell wall
  stress tolerance and host plant pathogenesis.* Kroll E, Bayon C, Rudd J, Armer VJ,
  Magaji-Umashankar A, Ames R, Urban M, Brown NA, Hammond-Kosack K. 2025.
- **Pathogens**: *Fusarium graminearum* (PH-1) and *Zymoseptoria tritici* (IPO323).
- **Host**: *Triticum aestivum* (wheat; cv. Bobwhite for *F. graminearum*, cv. Riband for
  *Z. tritici*).
- A single conserved gene, curated in parallel in two pathogen–wheat systems.

## Genes
- **F. graminearum**: `FGRAMPH1_01T23707` (**FgKnr4**), UniProtKB:A0A1C3YKU0.
- **Z. tritici**: `MYCGRDRAFT_105330` (**ZtKnr4**), UniProtKB:F9XI26.
- Host *T. aestivum*: no genes annotated.

## GO annotations (biological process)
| Species | Gene | Term ID | Term name | Evidence | Figure |
| --- | --- | --- | --- | --- | --- |
| F. graminearum | FGRAMPH1_01T23707 | GO:0032995 | regulation of fungal-type cell wall biogenesis | IMP | Fig 6B, 6C |
| Z. tritici | MYCGRDRAFT_105330 | GO:0032995 | regulation of fungal-type cell wall biogenesis | EXP | Fig 9B |
| F. graminearum | FGRAMPH1_01T23707 | GO:0007346 | regulation of mitotic cell cycle | EXP | Fig 7C |

Existing low-throughput annotations carried over (from PHI-base taxa 229533 *F. graminearum*,
336722 *Z. tritici*): FGRAMPH1_01T23707 (A0A1C3YKU0) → GO:0007346 (EXP) and GO:0032995 (IMP);
MYCGRDRAFT_105330 (F9XI26) → GO:0032995 (EXP).

## Pathogen phenotype annotations (single-species; deletion mutants)
| Species (strain) | Genotype | Term ID | Term name | Evidence | Figure | Extension |
| --- | --- | --- | --- | --- | --- | --- |
| F. graminearum (PH-1) | *FgKnr4Δ* | PHIPO:0001095 | abnormal localization of chitin in cell | Microscopy | 6B | observed_organ conidium |
| F. graminearum (PH-1) | *FgKnr4Δ* | PHIPO:0000379 | abnormal cell wall organization | Microscopy | 6C | observed_organ conidium |
| F. graminearum (PH-1) | *FgKnr4Δ* | PHIPO:0000943 | sensitive to hydrogen peroxide | Cell growth assay + H₂O₂ | 6A | — |
| F. graminearum (PH-1) | *FgKnr4Δ* | PHIPO:0001020 | sensitive to calcofluor white | Cell growth assay + calcofluor white | 6A | — |
| F. graminearum (PH-1) | *FgKnr4Δ* | PHIPO:0000978 | sensitive to sodium chloride | Cell growth assay + NaCl | 6A | — |
| F. graminearum (PH-1) | *FgKnr4Δ* | PHIPO:0000398 | sensitive to benomyl | Cell growth assay + benomyl (PDB, 0.5 µM) | 7B, 7C | — |
| Z. tritici (IPO323) | *ZtKnr4Δ* | PHIPO:0001020 | sensitive to calcofluor white | Cell growth assay + calcofluor white | 9B | — |
| Z. tritici (IPO323) | *ZtKnr4Δ* | PHIPO:0001446 | reduced hyphal branching | Cell growth assay | 9C | — |

## Pathogen–host interaction phenotype annotations (metagenotype: pathogen genotype × host)
| Pathogen genotype | Host genotype | Term ID | Term name | Evidence | Conditions | Figure | Extension |
| --- | --- | --- | --- | --- | --- | --- | --- |
| *FgKnr4Δ* (F. graminearum PH-1) | wild type *T. aestivum* (cv. Bobwhite) | PHIPO:0000365 | decreased pathogen growth within host | Macroscopic observation (quantitative) | 15 dpi | Fig 5 | infects_tissue spike; compared_to_control *FgKnr4+*[WT level]; infective_ability reduced virulence |
| *ZtKnr4Δ* (Z. tritici IPO323) | wild type *T. aestivum* (cv. Riband) | PHIPO:0000365 | decreased pathogen growth within host | Macroscopic observation (qualitative) | 20 dpi | Fig 9A | infects_tissue leaf; compared_to_control *Ztknr4+*[WT level]; infective_ability reduced virulence |

## Disease name annotations
> ⚠ Both PHIDO IDs used in this session are now **obsolete** in current PHIDO (each has a
> replacement — see the validation note). They are recorded here **as curated** for the gold
> standard; use the replacement ID when curating new papers.

| Pathogen genotype (control) | Host genotype | Term ID (as curated) | Term name | Figure |
| --- | --- | --- | --- | --- |
| *FgKnr4+*[WT level] (F. graminearum PH-1) | wild type *T. aestivum* (cv. Bobwhite) | PHIDO:0000163 | fusarium head blight *(obsolete → PHIDO:0000162)* | Fig 5 |
| *Ztknr4+*[WT level] (Z. tritici IPO323) | wild type *T. aestivum* (cv. Riband) | PHIDO:0000331 | Septoria tritici blotch *(obsolete → PHIDO:0000329)* | Fig 9A |

## phiweaver validation note
`validate_ontology_ids` (2026-07-04): 12/14 IDs pass. The 2 GO terms (both biological_process)
and 8 PHIPO terms exist and are non-obsolete (via EBI OLS); both UniProtKB accessions are
format-valid (existence via `query_uniprot.py`). The 2 **PHIDO disease-name terms are obsolete**
(caught offline against the bundled PHIDO ontology):
- **PHIDO:0000163** "fusarium head blight" → replaced_by **PHIDO:0000162** "Fusarium ear blight"
  (exact synonym "Fusarium head blight").
- **PHIDO:0000331** "Septoria tritici blotch" → replaced_by **PHIDO:0000329** "Septoria leaf
  blotch" (exact synonym "Septoria tritici blotch").

They are kept as originally curated (a faithful gold standard), with the current replacements
flagged above so new curation uses the live IDs.
