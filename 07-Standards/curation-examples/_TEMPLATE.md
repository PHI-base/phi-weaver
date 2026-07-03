---
type: curation-example
status: draft
topics:
  - gene-deletion
annotation_types:
  - interaction-phenotype
evidence:
  - gene deletion
pathogen: <Genus species>
host: <Genus species>
source: PMID:00000000
reviewed_by: <curator>
reviewed_date: <YYYY-MM-DD>
---

# <Short title> — worked curation example

> Draft produced by phiweaver; becomes a validated gold-standard once a curator reviews it
> and sets `status: validated`. Tag values must come from `TAGS.md` — add a new tag there
> first if a real case needs one. Copy this file (drop the leading `_`) to start an example.

## Paper
- **Source**: PMID / DOI, title.
- **Pathogen–host system**: pathogen → host.

## Entities (genes / proteins)
- `<gene>` — UniProtKB:`<accession>` — function + evidence. (resolved via `uniprot-lookup`)

## Genotypes
- `<allele / genotype>` — allele type, expression level. (`genotype-creation`)

## Metagenotypes (interactions)
- `<pathogen genotype>` × `<host genotype>` — note control vs experimental.

## Annotations
| Feature | PHIPO / GO term | Evidence code | Conditions / extensions | Figure |
| --- | --- | --- | --- | --- |
| `<phenotype>` | PHIPO:XXXXXXX (label) | `<evidence>` | ... | Fig N |

- Phenotype terms found via `map_phenotype`; every ID verified current via
  `validate_ontology_ids`. Effector genes carry GO:0140418 on the gene annotation.

## Provenance / notes
- Where each fact came from (figure/table/section); anything ambiguous flagged for the
  curator. No invented identifiers or terms.

## phiweaver auto-check (machine-readable — pre-fills the benchmarking scorecard)

phiweaver fills this block with the results of its deterministic checks (ID validity, term
existence/obsolescence). `07-Standards/curation-benchmarking/fill_scorecard.py` reads it to
pre-fill the scorecard's header and auto-check column; the reviewer's ratings stay blank.
Keys map to the scorecard's item rows; leave a value empty to skip that row.

```json
{
  "meta": {"date": "", "pmid": "", "paper": "", "system": "", "draft_by": "phiweaver"},
  "auto_check": {
    "uniprot_id": "",
    "species_strain_cultivar": "",
    "go_gene_annotation": "",
    "genotype": "",
    "metagenotype_control": "",
    "pathogen_phenotype": "",
    "host_phenotype": "",
    "interaction_phenotype": "",
    "evidence_code": "",
    "conditions_extensions": "",
    "disease_name": "",
    "rna_expression_level": "",
    "physical_interaction": ""
  }
}
```
