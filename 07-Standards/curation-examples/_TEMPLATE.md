---
type: curation-example
status: draft
topics:
  - gene-deletion
annotation_types:
  - pathogen_host_interaction_phenotype
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
`auto_check` keys map to the scorecard's item rows (empty = skip). `triage` and `flags`
(category + detail) let **unattended batch drafting record what needs the curator instead of
asking** — `python3 -m phiweaver.batch_summary <drafts>` rolls them up into one review
dashboard. Flag categories: `needs_pmid`, `needs_accession`, `needs_term_choice`,
`needs_genotype_modelling`, `needs_evidence_code`, `scope_question`, `completeness_gap`, `other`.
Triage: `in_scope` | `partial` | `scope_uncertain` | `needs_human_decision` | `out_of_scope`.

The `canto` block is the **structured, machine-readable curation** that
`phiweaver.canto.entry_queue` renders into a PHI-Canto entry queue (Route 1; see
`docs/CANTO-ROUTE1-BUILD-SPEC.md`). It mirrors Canto's entry order and controlled fields:
- `genes` — `name`, `uniprot` (accession only, e.g. `K3V6Z9` — this **is** Canto's add-gene
  identifier), `organism`, optional `locus`, `note`.
- `alleles` — `name`, `gene`, `type` (deletion / point mutation / wild type / …), `expression`
  (null / wild-type level / overexpression / …).
- `genotypes` — `name`, `organism`, `alleles` (list of allele names; empty for wild type),
  optional `role` (`control` | `experimental`). Host wild-type genotypes are listed here too.
  Plus Canto's two genotype-table columns, which are **complementary and never both set**
  (curator ruling 2026-07-25, `PHI-Canto-Curation-Conventions.md` "Strains and cultivars"):
  - `strain` — **wild types only**: the strain, cultivar, pathovar or variety (`Guy11`,
    `Sariceltic`). This is what the entry queue's table A2 pre-fills, and Canto requires a strain
    per organism before any genotype can be created.
  - `background` — **mutants only**: the parent wild-type strain *plus* the endogenous copy's
    status, in one field (`Guy11; endogenous ABC1 absent`, `Guy11; ABC1modified`). Set it even
    when the draft records no allele — it is the second signal that a genotype is not wild type
    (an ectopic insertion in a wild-type parent looks wild type without it).
- `metagenotypes` — `name`, `pathogen_genotype`, `host_genotype` (genotype names), `role`
  (`experimental` | `control` | `complementation_control`).
- `annotations` — `feature_type` (`gene` | `genotype` | `metagenotype`), `feature` (its name),
  `annotation_type` (a PHI-Canto type from `TAGS.md`), `term_id`, `term_name`, `evidence`,
  `extensions` (list of `{relation, value}`, e.g. `infects_tissue`, `infective_ability`,
  `compared_to_control`), `conditions` (**short** experimental condition only — medium, temp,
  chemical, tissue), `figure`, and two optional fields:
  - `note` — curator caveats / term-choice / "confirm" prose. Kept **out** of the concise
    entry-queue tables (`canto-entry-queue`) — caveat context only, never an entry row. Put long
    prose here, not in `conditions`.
  - `hold` (`true`/`false`) + `hold_reason` — an **explicit park signal**: mark an interpretive
    or uncertain annotation (e.g. a molecular-function term inferred from rescue/genetics with no
    direct assay) so the entry queue parks it by the curator's decision rather than by guessing
    from the evidence prose. Absent `hold`, the queue falls back to a heuristic for interpretive
    molecular-function terms.
Terms reuse the IDs already validated in `auto_check`; a missing term stays a `flags` entry, never
invented (the entry queue parks it as an item to resolve before entry).

```json
{
  "meta": {"date": "", "pmid": "", "paper": "", "system": "", "draft_by": "phiweaver", "model": ""},
  "triage": "in_scope",
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
  },
  "flags": [
    {"category": "needs_pmid", "detail": "example — replace with the real flags for this paper"}
  ],
  "canto": {
    "genes": [{"name": "", "uniprot": "", "organism": "", "locus": "", "note": ""}],
    "alleles": [{"name": "", "gene": "", "type": "", "expression": ""}],
    "genotypes": [{"name": "", "organism": "", "alleles": [], "role": "", "strain": "", "background": ""}],
    "metagenotypes": [{"name": "", "pathogen_genotype": "", "host_genotype": "", "role": ""}],
    "annotations": [{"feature_type": "", "feature": "", "annotation_type": "", "term_id": "", "term_name": "", "evidence": "", "extensions": [{"relation": "", "value": ""}], "conditions": "", "note": "", "hold": false, "hold_reason": "", "figure": ""}]
  }
}
```
