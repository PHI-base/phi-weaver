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
  - a `strain` on every wild type, a `background` on every mutant (never both)
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
6. **Set `strain` or `background` on every genotype** — see "Strain and background" below. A
   wild type gets `strain`; a mutant gets `background`; never both.
7. Where the paper does not state a detail (e.g. expression level), mark it "not assayed"
   or flag the ambiguity — never invent an allele or level.

## Naming & data standardisation (curator convention, 2026-07-15)
From `07-Standards/PHI-Canto-Curation-Conventions.md` (Hsin-Yun Chang review of PMID:42089373):
- **Gene symbol without species prefix** — `SdhA`, not `FpSdhA`.
- **Deletion genotypes use the Δ-suffix** — `SdhAΔ`, not `ΔFpSdhA` (double mutant `SdhC1&2Δ`;
  complement `SdhC2Δ-C`).

## Name a mutant by its allele, never by the paper's isolate label
Curator ruling 2026-07-25 (`07-Standards/PHI-Canto-Curation-Conventions.md`). A paper calls its
mutants `AM25`, `TF7-3131`, `FOA-01-11-2` — collection labels that mean nothing outside it. The
genotype is named by the **allele**: `AM25` is the `abc1-2Δ` genotype. A strain prefix is fine
where it disambiguates (`Pta6605 ΔfleQ`), as long as the allele is in the name.

**Get this right when the genotype is created.** The name is a foreign key: metagenotype names
build on it and every annotation's `feature` points at it, so a later rename is a cascading pass
over the whole block, not a text edit. `python3 -m phiweaver.canto.entry_queue <draft.md>` reports
a mutant naming none of its alleles.

## Controlled genotype labels
Use standardized labels so genotype names read consistently across curations (from the
PHI-base curator methodology, `06-Training/Gene-for-Gene-Curation-Methodology.md`). Applies to
**both** pathogen and host genotypes:

- Wild type — `WT`.
- Deletion / disruption / knockdown — CRISPR-Cas9, RNAi, split-marker; gene silencing prefixes
  the silenced gene with `si` (e.g. `siSec5`).
- Complementation — `Complement (Ectopic)`.
- Overexpression — `gene-OE`.
- GFP fusion — `gene-GFP` (and overexpression + GFP tag combines the two).
- Signal-peptide deletion — e.g. `Kwl1ΔSP`; domain deletion — e.g. `XopACΔLRR`.
- Amino-acid substitution — e.g. `Ire1(aaS896A)[Ectopic]`.
- Non-functional allele — e.g. `avrLm1(non-func)(unknown)[WT level]`.
- Insertion / disruption line — e.g. `rlp23-1(disruption)[Null]`.

Assign pathogen **strains** and host **cultivars** accurately — cultivar identity encodes
R-gene presence/absence, which is critical for gene-for-gene cases (see the `gene-for-gene`
skill).

## Strain and background (curator ruling, 2026-07-25)
From `07-Standards/PHI-Canto-Curation-Conventions.md` ("Strains and cultivars — wild type only",
Martin Urban on PMID:9927411). PHI-Canto's genotype tables carry a **Strain** and a **Background**
column, and Canto requires at least one strain per organism *before any genotype can be created* —
so these are entry blockers, not decoration.

**Only a wild type carries a strain; a mutant is named by its allele and carries a background
instead.** The two fields are complementary and never both set:

| | `strain` | `background` |
|---|---|---|
| wild type | the strain / cultivar (`Guy11`, `Sariceltic`) | — |
| mutant | — | parent strain + endogenous-copy status (`Guy11; endogenous ABC1 absent`) |

Write both into the draft's `canto` block as fields on each genotype (schema:
`07-Standards/curation-examples/_TEMPLATE.md`); the entry queue's table A2 pre-fills the strain
step from them.

- **Do not put the isolate label in `strain` because the paper uses it as a name.** `AM25` and
  `TF7-3131` are mutant *genotypes*; their strain cell stays empty and `Guy11` is their background.
- **A near-isogenic line follows the mutant rule** (ruling 2026-07-26): it carries an allele, so its
  parent cultivar is a `background` and it gets no `strain` — a *natural* allele is still an allele.
  `tomato 76R (Pto/Pto)` takes its recurrent parent as background; a plain cultivar with nothing
  introgressed (`soybean cv. Centennial`) stays a wild type with a `strain`. On the host side this
  is where R-gene presence/absence lives, so losing the parentage breaks the gene-for-gene pair.
- **`background` also marks a mutant the draft records no allele for.** An ectopic insertion in a
  wild-type parent (`AM30`) looks wild type from its allele list alone — the background is the
  second signal, and the entry queue renders `⚠ no allele recorded` so the missing allele is
  caught rather than the genotype being entered as a wild type.
- Combine the parent strain and the endogenous copy's status in the one `background` field, using
  the `#157` vocabulary below.
- If the paper does not name the parent strain, leave the field empty and flag it — do not guess.

## Team-settled allele conventions
From `07-Standards/PHI-Canto-Curation-Conventions.md` (source: PHI-base/curation closed
issues, collected 2026-07-12):

- **`transformant` is decided by ORIGIN, not method.** Use allele type `transformant` only when
  an allele comes from **strain A and is introduced into strain B**. A same-strain
  mutate-and-reintroduce is *not* a transformant — use the mutation-based type, or
  `ectopic expression` for random/plasmid integration. (`#157`)
- **Transformant naming:** name `<gene> transformant` (auto-filled by PHI-Canto); description
  `<strain>-<gene>(<allele>)` (give the AA change if known, not for a plain WT transgene); and
  **record the endogenous copy's status in the background field** — `endogenous <gene> present`,
  `endogenous <gene> absent` (naturally absent), or `<gene>modified` (changed by the researchers;
  replaced `<gene>delta` on 2026-07-25 so the form also fits an insertion or substitution).
  (`#157`)
- **Deletion + substitution in one allele** → allele type `partial deletion and amino acid
  change`. (`#16`)
- **Never emit `Unknown` expression level** — it was retired; use `not assayed` or
  `overexpression` as the paper supports. (`#70`)
- **Do not push signal-peptide removal to background** — the assay still targets the processed
  WT protein. (`#77`)

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
- Every genotype carries **either** `strain` (wild type) **or** `background` (mutant), never both
  and never neither — `python3 -m phiweaver.canto.entry_queue <draft.md>` reports the gaps on
  stderr.
- Gene identity ties to a UniProtKB accession (see uniprot-lookup).

## Human review
- Genotypes are a draft. A curator confirms allele types, expression levels and
  combinations in PHI-Canto before annotation; flag any ambiguous or assumed field.
