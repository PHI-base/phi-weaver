# Curation-example tags — controlled vocabulary

Use **only** these values in example frontmatter, so retrieval stays consistent (phiweaver
matches a new paper to examples by these tags). When a real case needs a new value, add it
here first with a one-line meaning — don't invent ad-hoc tags in the examples.

## `topics` — the curation case type (an example may have several)
- `gene-deletion` — knockout / deletion mutant
- `overexpression` — increased-expression construct
- `complementation` — deletion plus reintroduced wild-type
- `effector` — pathogen effector (needs GO:0140418 on the gene annotation)
- `gene-for-gene` — R-gene / avirulence recognition
- `diploid` — diploid pathogen or host; allele zygosity matters
- `physical-interaction` — protein–protein / molecular interaction (confirm PHI-Canto scope)
- `chemical-sensitivity` — resistance / sensitivity to a compound
- `secondary-metabolite` — mycotoxin / secondary-metabolite phenotype

## `annotation_types` — PHI-Canto's own annotation types (the coverage target)

These are the **exact** annotation types PHI-Canto records (see the sessions-with-type list at
`canto.phi-base.org/tools/sessions_with_type_list`). Tag an example with every type it actually
contains, using these names verbatim, so the coverage tracker in `INDEX.md` and any
benchmarking compare like-for-like with PHI-Canto. The count is how many PHI-Canto sessions
carry that type (a rough prevalence, so gold-standard coverage can be prioritised by frequency).

- `molecular_function` — GO MF gene annotation (223)
- `biological_process` — GO BP gene annotation (263)
- `cellular_component` — GO CC gene annotation (152)
- `pathogen_phenotype` — single-species pathogen phenotype (281)
- `host_phenotype` — single-species host phenotype (17)
- `pathogen_host_interaction_phenotype` — metagenotype (pathogen × host) phenotype (333)
- `gene_for_gene_phenotype` — R-gene / avirulence recognition metagenotype (58)
- `disease_name` — PHIDO disease-name annotation (339)
- `physical_interaction` — protein–protein / molecular interaction (99)
- `wt_rna_expression` — wild-type RNA expression level (95)
- `wt_protein_expression` — wild-type protein expression level (4)
- `post_translational_modification` — PTM annotation (14)

## `evidence`
- `gene deletion`, `complementation`, `overexpression`, `point mutation`,
  `biochemical`, `microscopy`, `growth assay`, `expression analysis`

## Free text (not controlled)
- `pathogen`, `host` — species names (e.g. *Fusarium graminearum*, *Triticum aestivum*).
- `source` — `PMID:...` or `DOI:...`.
- `reviewed_by`, `reviewed_date` — set when a curator validates the example.
