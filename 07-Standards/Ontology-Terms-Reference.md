---
created: 2026-04-20
type: reference
tags: [ontology, standards, phi-canto]
project: PHI-Canto
---

# PHI-Canto Ontology Terms Reference Guide

## Overview

Quick reference guide for ontologies and controlled vocabularies used in PHI-Canto curation. Essential for consistent annotation across the community.

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
> (Source: Hsin-Yun Chang review, 2026-07-15; see `docs/CURATION-LESSONS.md` L6.)

### Source & browsing
- Ontology (OBO / GitHub): **<https://github.com/PHI-base/phi-eco>**
- Like PHIDO, PHI-ECO is **PHI-base-local** — not hosted on EBI OLS, so validate **offline** against
  the repo's ontology file (the plan is to vendor it as we did `phido.obo`; see the backlog).

### Requesting new PECO terms (curator workflow)
New terms are drafted in a Google-Sheet **"PHI-ECO term creator"**, then loaded into the ontology
with **ROBOT** (needs Java); the ontology maintainer (James Seager) does the load. The curator fills
**one row per new term** with these columns:
- **Condition name · Definition · Subclass of** (the parent term) **· Created by · Creation date**
- **Contributor id:** use `changh` for Hsin-Yun Chang — kept consistent across PHIPO / PHI-ECO so
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

*This reference guide should be used alongside the complete PHI-Canto documentation for comprehensive curation support.*