---
name: genotype-creation
description: Create pathogen or host genotypes (alleles, complementation, multi-allele, expression levels) for a PHI-Canto curation, following PHI-base conventions. Use when a paper's mutants/strains need genotypes before phenotype annotation.
backing_script: null
tests: null
inputs:
  - gene/allele identity + UniProtKB accession (from uniprot-lookup)
  - mutation type and expression level described in the paper
  - strain background, if any
outputs:
  - single- or multi-allele genotype(s) with allele type + expression level
  - complementation / control genotypes where the experiment uses them
  - background mutations recorded separately
  - explicit note where the paper is ambiguous (no invented alleles)
---

# Genotype Creation

## Purpose
Turn the mutants, complements and strains described in a paper into correctly-typed
PHI-Canto genotypes, so phenotypes can be annotated against them. Detailed field-by-field
conventions live in `06-Training/Quick-Reference-Genotype-Creation.md`.

## When to use
- After entities are resolved (uniprot-lookup) and before phenotype-annotation, whenever a
  paper reports gene knockouts, point mutations, overexpression, complementation, or
  multi-gene mutants.

## Workflow
1. For each manipulated gene, identify the mutation type from the paper: deletion,
   substitution, insertion, wild type, or other.
2. Set the expression level to match the experiment: null (knockout), decreased
   (knockdown / partial), wild type product level, increased (overexpression), or not
   assayed.
3. Create each single allele. For a complementation, create the deletion (expression null)
   and the complementing construct (wild type product level) as separate alleles.
4. Combine alleles into a multi-allele genotype for double/triple mutants or complemented
   strains.
5. Record strain background mutations in the background field, not in the strain name.
6. Where the paper does not state a detail (e.g. expression level), mark it "not assayed"
   or flag the ambiguity — never invent an allele or level.

## Expected outputs
- Single- and/or multi-allele genotype(s), each allele with its type and expression level.
- Complementation and control genotypes where the experiment uses them.
- Background mutations recorded separately.
- Explicit notes where the paper is ambiguous.

## Quality-control checks
- Allele type and expression level are supported by the paper's text/figures.
- Wild type at normal expression is not annotated with phenotypes (controls / metagenotypes
  only).
- Multi-allele genotypes combine the correct singles; backgrounds attached correctly.
- Gene identity ties to a UniProtKB accession (see uniprot-lookup).

## Human review
- Genotypes are a draft. A curator confirms allele types, expression levels and
  combinations in PHI-Canto before annotation; flag any ambiguous or assumed field.
