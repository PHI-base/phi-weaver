---
created: 2026-04-20
type: reference
tags: [ontology, standards, phi-canto]
project: PHI-Canto
---

# PHI-Canto Ontology Terms Reference Guide

## Overview

Quick reference guide for ontologies and controlled vocabularies used in PHI-Canto curation. Essential for consistent annotation across the community.

> For the full map of where ontology material lives (tools, bundled data, gap ledger, term-request workflow), see **[Ontology-INDEX.md](Ontology-INDEX.md)**.

## PHIPO (Pathogen-Host Interaction Phenotype Ontology)

### Structure and Organization

**Primary Branches:**
1. **Single-species phenotypes** - Observable traits of pathogen OR host in isolation
2. **Pathogen-host interaction phenotypes** - Observable outcomes of interactions

### Common Single-Species Phenotype Categories

#### Pathogen Phenotypes
**Growth and Morphology:**
- `increased/decreased hyphal growth`
- `abnormal/normal hyphal morphology` 
- `sexual spores absent/present`
- `asexual spores absent/present`
- `increased/decreased sporulation`

**Stress Response:**
- `resistance/sensitivity to [compound]`
- `normal growth on [compound]`
- `temperature sensitivity`
- `osmotic stress sensitivity`

**Metabolic:**
- `loss of pathogenicity`
- `reduced virulence`
- `altered secondary metabolite production`

#### Host Phenotypes
**Defense Responses:**
- `presence/absence of hypersensitive response`
- `increased/decreased defense gene expression`
- `cell death response present/absent`

**Susceptibility Markers:**
- `increased/decreased susceptibility to pathogen`
- `presence/absence of disease resistance`

### Common Interaction Phenotype Categories

#### Pathogenicity/Virulence Changes
- `loss/reduction of pathogenicity`
- `increased pathogenicity`
- `abolished/reduced pathogen penetration into host`
- `absence/presence of pathogen growth on host surface`

#### Host Response During Interaction
- `stunted host growth during pathogen colonization`
- `normal host growth during pathogen colonization`
- `host hypersensitive response present/absent`

#### Colonization Patterns
- `reduced pathogen growth in host`
- `normal pathogen growth in host`
- `delayed pathogen infection process`

### PHIPO Term Selection Best Practices

1. **Start broad, refine specific**: Search "growth" → "hyphal growth" → "decreased hyphal growth"
2. **Read definitions carefully**: Term names can be misleading
3. **Use hierarchy navigation**: Browse child terms from broader categories
4. **Request new terms**: When existing terms don't fit your observation

## PHIDO (PHI-base Disease Ontology)

### Disease Annotation Principles

**When to Annotate Diseases:**
- Wild-type pathogen × natural host interactions
- Disease present (not resistant interactions)
- Natural host-pathogen combinations (not model organisms)

### Common Disease Categories

#### Fungal Diseases
- `anthracnose` - Dark lesions on stems, leaves, fruits
- `blight` - Rapid tissue death and browning
- `canker` - Localized dead areas on woody stems
- `leaf spot` - Discrete spots on leaf tissue
- `powdery mildew` - White fungal growth on surfaces
- `root rot` - Decay of root tissues
- `rust` - Pustules with rust-colored spores
- `smut` - Dark spore masses replacing host tissue
- `wilt` - Loss of turgor, drooping

#### Bacterial Diseases
- `bacterial blight` - Water-soaked lesions, tissue death
- `bacterial canker` - Sunken areas on stems/branches
- `bacterial leaf spot` - Water-soaked spots on leaves
- `bacterial soft rot` - Tissue maceration and decay
- `bacterial wilt` - Vascular blockage causing wilting

#### Viral Diseases
- `mosaic` - Mottled light/dark green patterns
- `yellowing` - Chlorosis and yellow coloration
- `stunting` - Reduced growth and size
- `ringspot` - Circular spots or rings on leaves

### Disease-Tissue Relationships

Common host tissues (BRENDA Tissue Ontology terms):
- `leaf` (BTO:0000713)
- `root` (BTO:0001199) 
- `stem` (BTO:0001225)
- `inflorescence` (BTO:0000628) - For ear blight, head scab
- `fruit` (BTO:0000645)
- `seed` (BTO:0001203)

## Gene Ontology (GO) Terms

### Molecular Function (MF) - What the gene product does

#### Common Effector Functions
- `hydrolase activity` (GO:0016787) - Breakdown of bonds
- `peptidase activity` (GO:0008233) - Protein cleavage  
- `carbohydrate binding` (GO:0030246) - Sugar interaction
- `protein binding` (GO:0005515) - Protein interactions

#### Resistance Gene Functions
- `protein kinase activity` (GO:0004672) - Phosphorylation activity
- `nucleotide binding` (GO:0000166) - ATP/GTP binding
- `DNA binding` (GO:0003677) - Transcription factors

### Biological Process (BP) - What biological process the gene product is involved in

#### **Required for Effectors:**
- `effector-mediated modulation of host process by symbiont` (GO:0140418)
  - Or more specific child terms

#### Common Pathogen Processes
- `pathogenesis` (GO:0009405) - General pathogenicity
- `adhesion to host` (GO:0044659) - Attachment
- `entry into host` (GO:0030260) - Penetration/invasion
- `evasion of host defenses` (GO:0044413) - Immune suppression

#### Common Host Processes  
- `defense response to fungus` (GO:0050832)
- `defense response to bacterium` (GO:0042742)
- `hypersensitive response` (GO:0009626)
- `innate immune response` (GO:0045087)

### Cellular Component (CC) - Where the gene product is located

#### Secretion and Localization
- `extracellular region` (GO:0005576) - Secreted proteins
- `cell wall` (GO:0005618) - Cell wall associated
- `plasma membrane` (GO:0005886) - Membrane proteins
- `nucleus` (GO:0005634) - Nuclear proteins
- `cytoplasm` (GO:0005737) - Cytoplasmic proteins

## BRENDA Tissue Ontology

### Plant Anatomical Structures

**Vegetative Organs:**
- `leaf` (BTO:0000713)
- `root` (BTO:0001199)
- `stem` (BTO:0001225)
- `shoot` (BTO:0001208)

**Reproductive Organs:**
- `inflorescence` (BTO:0000628) - Flowering structure
- `flower` (BTO:0000645)
- `fruit` (BTO:0000645)
- `seed` (BTO:0001203)

**Tissue Types:**
- `vascular tissue` (BTO:0001493) - Transport tissues
- `epidermis` (BTO:0000578) - Outer layer
- `mesophyll` (BTO:0000858) - Leaf interior

## Physical Interaction Evidence Codes

### Asymmetric Evidence (Directional)

**Affinity Capture Methods:**
- `Affinity Capture-MS` - A affinity captures B, detected by mass spec
- `Affinity Capture-Western` - A captures B, detected by Western blot
- `Affinity Capture-RNA` - A captures B RNA

**Other Directional:**
- `Two-hybrid` - A (DNA-binding domain) with B (activation domain)
- `Far Western` - A captures B in overlay assay
- `FRET` - A is fluorescence donor to B
- `Protein-peptide` - A binds to peptide B
- `Protein-RNA` - A binds to RNA B

### Symmetric Evidence (Non-directional)

- `Co-purification` - A co-purifies with B
- `Co-fractionation` - A co-fractionates with B  
- `Co-crystal Structure` - A co-crystallizes with B
- `Reconstituted Complex` - A forms complex with B
- `PCA` (Protein Complementation Assay) - A interacts with B

## Experimental Conditions — PHI-ECO (PECO)

**PHI-ECO** is the **PHI-base experimental-conditions ontology** — the controlled vocabulary for the
**Condition** field of a PHI-Canto annotation (growth media, temperature, chemical treatments, and
the inoculation / effector-delivery method). Term prefix **`PECO:`**.

> **Curation rule:** condition entries must be **PECO terms**. Free-text conditions (e.g.
> "PDA, 25 °C, 5 d") do **not** pass final approval — map each to a PECO term, or request a new one.
> (Source: Hsin-Yu Chang review, 2026-07-15; see `docs/CURATION-LESSONS.md` L6.)
>
> **Tooling:** map a condition phrase to a PECO term with
> `python3 -m phiweaver.lookup.map_condition "<phrase>"` (offline over the bundled ontology; never
> invents), then verify with `validate_ontology_ids`. PHI-ECO is **qualitative** (`rich medium`,
> `standard temperature`, delivery mechanisms, `+ wounding`) — it has no "PDA"/"25 °C" term, so map
> the qualitative condition and keep numeric specifics in the annotation comment.

### Source & browsing
- Ontology (OBO / GitHub): **<https://github.com/PHI-base/phi-eco>**
- Like PHIDO, PHI-ECO is **PHI-base-local** — not on EBI OLS. It is **vendored offline** at
  `phiweaver/lookup/data/phi-eco.obo`, and `validate_ontology_ids` now checks `PECO:` IDs against
  it (`✅ PECO:0005028 … via bundled phi-eco.obo`).
- **⚠ Prefix collision:** the OLS ontology named `peco` is the *unrelated* Planteome **Plant
  Experimental Conditions Ontology**. PHI-base PECO terms are **only** in the bundled file — never
  validate them against OLS (they will falsely return not_found or match a different term).

### Requesting new PECO terms (curator workflow)
New terms are drafted in a Google-Sheet **"PHI-ECO term creator"**, then loaded into the ontology
with **ROBOT** (needs Java); the ontology maintainer (James Seager) does the load. The curator fills
**one row per new term** with these columns:
- **Condition name · Definition · Subclass of** (the parent term) **· Created by · Creation date**
- **Contributor id:** use `changh` for Hsin-Yu Chang — kept consistent across PHIPO / PHI-ECO so
  contributions track across ontologies.
- **Naming rule:** put a **space after `+`** in chemical-medium term names — e.g. `+ wortmannin`,
  not `+wortmannin`.
- Term-creator spreadsheet: <https://docs.google.com/spreadsheets/d/1GXazqAmvsfqB03wj_T-5aA6a3-kn1gcQjYZMHiosUYE/edit>
- "How to use the PHI-ECO term creator" doc: <https://docs.google.com/document/d/1LHXq6akcJnj_XfvjcFPyuLy3KrNBe5MsGhsmiVHHSFE/edit>
- ROBOT: <https://robot.obolibrary.org/>

### Example PECO terms — effector-delivery mechanisms
| PECO ID | Term | Definition (abridged) |
| --- | --- | --- |
| PECO:0005028 | delivery mechanism: agrobacterium | gene products transiently expressed via agrobacterium-mediated delivery into the host |
| PECO:0005235 | delivery mechanism: heterologous organism | gene products expressed in the host via a heterologous-organism delivery system |
| PECO:0005239 | delivery mechanism: pathogen inoculation | a pathogen is inoculated onto a host |
| PECO:0005242 | delivery mechanism: pathogen mycelium inoculation | pathogen mycelium inoculated onto a host |
| PECO:0005244 | delivery mechanism: pathogen point inoculation | pathogen point-inoculated onto a small, specific region of host tissue |
| PECO:0005241 | delivery mechanism: pathogen spore inoculation | pathogen spores inoculated onto a host |
| PECO:0005243 | delivery mechanism: pathogen spray inoculation | pathogen spray-inoculated over a large area of host tissue |
| PECO:0005271 | delivery mechanism: culture infiltration | gene products infiltrated into the host |
| PECO:0005272 | delivery mechanism: pathogen gene expressed by transgenic host | pathogen gene products transiently or stably expressed in the host |

### Informal condition categories (map each to a PECO term before annotating)

### Growth Conditions
- `minimal medium` - Defined nutrient medium
- `rich medium` - Complex nutrient medium  
- `solid medium` - Agar plates
- `liquid medium` - Broth culture

### Temperature Conditions
- `standard temperature` - Normal growth temperature
- `high temperature` - Heat stress conditions
- `low temperature` - Cold stress conditions

### Chemical Treatments
- `salt stress` - NaCl or other salt addition
- `oxidative stress` - H2O2, paraquat treatment
- `antifungal treatment` - Specific antifungal compounds

### Infection/Delivery Methods
- `spray inoculation` - Foliar spray application
- `infiltration` - Pressure/vacuum infiltration
- `wound inoculation` - Through wounds or cuts
- `soil inoculation` - Root infection via soil

## Quality Control Guidelines

### Term Selection Checklist
- [ ] Definition matches experimental observation
- [ ] Most specific term available selected
- [ ] Correct ontology branch used (single-species vs interaction)
- [ ] Evidence code matches experimental method
- [ ] Experimental conditions captured accurately

### Common Mistakes to Avoid
- Using term names without reading definitions
- Mixing single-species and interaction phenotypes
- Wrong directionality in physical interactions
- Over-specifying experimental conditions
- Missing required GO annotations for effectors

### When to Request New Terms
- No existing term adequately describes observation
- Available terms too broad for your specific case
- Definition doesn't match experimental results
- Need more specific child term

## Resources for Term Browsing

### Online Browsers
- **PHIPO**: Via OBO Foundry links (<https://obofoundry.org/ontology/phipo>)
- **Gene Ontology**: AmiGO browser (<http://amigo.geneontology.org/>)
- **BRENDA Tissue**: <https://brenda-enzymes.org/ontology.php?ontology_id=3>

### Search Strategies
1. **Broad keywords first**: "growth", "resistance", "interaction"
2. **Synonym searching**: Try multiple related terms
3. **Hierarchy browsing**: Navigate parent/child relationships
4. **Definition scanning**: Read carefully before selecting

---

## Annotation-extension relations (PHI-Canto config, not an ontology)

A PHIPO phenotype annotation can carry **extensions** — `relation → value` qualifiers.
The legal relations and the value type each accepts are **PHI-Canto configuration**, not
an OLS ontology, so they are validated **offline** against a vendored copy of
`phipo_extensions.tsv` by `phiweaver/lookup/extension_config.py` (source: PHI-base/config,
private — see `phiweaver/lookup/data/README.md`). Do **not** invent relations: use only the
attested set below. Run `python3 -m phiweaver.lookup.extension_config` to print the live list,
or `... infective_ability=PHIPO:0000015` to check one pair.

| Relation | Value type | Notes |
|---|---|---|
| `alteration_in_archetype` | free text | |
| `assayed_using` | GeneID | assayed protein/RNA; add **two** GeneIDs for binding pairs |
| `compared_to_control` | MetagenotypeID | links a mutant metagenotype to its WT control |
| `gene_for_gene_interaction` | `PHIPO_EXT:` term | annotation type `gene_for_gene_phenotype` |
| `inverse_gene_for_gene` | `PHIPO_EXT:` term | annotation type `gene_for_gene_phenotype` |
| `has_penetrance` | `FYPO_EXT:` term or numeric (e.g. `75%`) | proportion of population showing the phenotype |
| `has_severity` | `FYPO_EXT:` term | |
| **`infective_ability`** | **PHIPO term under `PHIPO:0001179`** | the *interpretation* of a pathogen–host interaction (e.g. `PHIPO:0000015` reduced virulence). Annotation type `pathogen_host_interaction_phenotype`. |
| `interaction_outcome` | PHIPO term under `PHIPO:0001198` | outcome of interaction. Annotation type `pathogen_host_interaction_phenotype`. |
| `infects_tissue` | BTO term | host tissue infected |
| `observed_organ` | BTO term (allowed roots listed in config) | organ where phenotype was observed |
| `with_host_peptide` | free text | UniProtKB accession + residue range, e.g. `P12345 (100-200)` |

**Key rule for interaction phenotypes:** the primary term is the *measured* phenotype
(e.g. `PHIPO:0000365` decreased pathogen growth within host); the *interpretation*
"reduced virulence" goes in `infective_ability` **as the term ID `PHIPO:0000015`**, never
as bare text. See the interaction-phenotype section of
`PHI-Canto-Curation-Conventions.md`. What is **not** yet validated offline: that a
term-typed value is a genuine *descendant* of the range root, and the per-primary-term
subset constraints in the config's `domain ID` column — deeper checks left to the curator.

**Extensions on other annotation types.** GO and disease-name annotations have their own
(smaller) extension configs, also vendored and checked offline
(`extension_config --config go` / `--config phido`):

- **GO annotations** (`phibase_go_extensions.tsv`): `has_input` (a protein ID or free text,
  e.g. "binds"), `with_host_species` / `with_symbiont_species` (an NCBI taxon ID). These
  values are IDs/text, **not** ontology branches.
- **Disease-name (PHIDO) annotations** (`phido_extensions.tsv`): `infects_tissue → BTO`
  (host tissue), same as on phenotypes.

Neither is used by current drafts yet. The relations themselves are defined (with prose
definitions) in `phipo_extension_relations.obo` — a **reference** file, not a validation
source (it is incomplete vs `phipo_extensions.tsv`). See `phiweaver/lookup/data/README.md`.

**Extension value terms are validated offline.** Both come from *separate* small ontologies, each
vendored and resolved by `validate_ontology_ids` (existence + obsolescence, like PHIDO/PECO):

- **`PHIPO_EXT:`** — gene-for-gene values (`gene_for_gene_interaction` / `inverse_gene_for_gene`);
  `phipo_ext.obo` from the public `PHI-base/phipo_ext` repo. Not part of PHIPO.
- **`FYPO_EXT:`** — penetrance/severity values (`has_penetrance` / `has_severity` → `high` / `medium`
  / `low` / `complete`); `fypo_extension.obo` from `PHI-base/canto`. The config's `FYPO_EXT:1000001`
  / `1000002` are grouping/gate roots (not annotation values); a curator picks a qualitative value or
  gives a percentage.

---

*This reference guide should be used alongside the complete PHI-Canto documentation for comprehensive curation support.*