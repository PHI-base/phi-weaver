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

## `annotation_types`
- `single-species-phenotype` — pathogen OR host alone
- `interaction-phenotype` — pathogen–host together (metagenotype)
- `gene-annotation` — gene-level GO annotation (e.g. effector GO:0140418)

## `evidence`
- `gene deletion`, `complementation`, `overexpression`, `point mutation`,
  `biochemical`, `microscopy`, `growth assay`, `expression analysis`

## Free text (not controlled)
- `pathogen`, `host` — species names (e.g. *Fusarium graminearum*, *Triticum aestivum*).
- `source` — `PMID:...` or `DOI:...`.
- `reviewed_by`, `reviewed_date` — set when a curator validates the example.
