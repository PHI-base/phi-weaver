---
created: 2026-04-20
type: training
tags: [onboarding, curator-training, phi-canto]
project: PHI-Canto
---

# PHI-Canto Curator Onboarding Guide

## Welcome to PHI-Canto Curation

This guide provides essential knowledge for new curators joining the PHI-base community curation effort.

## What is PHI-Canto?

PHI-Canto is the community curation platform for **PHI-base** (Pathogen-Host Interactions database), enabling researchers to contribute their experimental findings about pathogen-host interactions directly to the database.

### Key Concepts

**PHI-base**: Database of experimentally verified pathogen-host interactions
**Curation**: Process of extracting and standardizing data from research publications
**Community Curation**: Authors and researchers contribute data about their own work
**Quality Assurance**: Expert review process before data publication

## Fundamental Curation Concepts

### 1. Gene Identification with UniProtKB

**Why UniProtKB?** Ensures consistent gene identification across different organisms and strains.

#### Learning UniProtKB Navigation:
1. **Reference Proteome Concept**: Standard protein set for each organism
2. **Entry vs Entry Name**: Always use 'Entry' (accession) numbers
3. **Reviewed vs Unreviewed**: Prefer reviewed entries when available
4. **BLAST Search**: When direct name search fails

**Practice Exercise**: Look up well-known effector genes in your research area.

### 2. Strain Management

**Strain Definition**: Any taxonomic specification below species level
- Subspecies, varieties, cultivars, pathovars, laboratory strains

**Key Principle**: Background mutations separate from strain names
- Strain: "F. graminearum PH-1"  
- Background alleles: Specified in genotype background field

### 3. Genotype vs Metagenotype

**Genotype**: Genetic makeup of single organism (pathogen OR host)
**Metagenotype**: Combined genotype of pathogen-host interaction

**Example**:
- Pathogen genotype: *tri5*Δ strain
- Host genotype: Wild-type wheat
- Metagenotype: *tri5*Δ pathogen × wild-type wheat interaction

### 4. Control Experiments

**Critical Concept**: Always identify and curate control conditions
- Wild-type pathogen × wild-type host (control metagenotype)
- Mutant pathogen × wild-type host (experimental metagenotype)
- Links between control and experimental via annotation extensions

## Ontology Systems

### PHIPO (Pathogen-Host Interaction Phenotype Ontology)

**Two Main Branches**:
1. **Single-species**: Pathogen or host phenotypes in isolation
2. **Pathogen-host interaction**: Outcomes of interactions

**Examples**:
- Single-species: "decreased hyphal growth", "resistance to voriconazole"
- Interaction: "absence of pathogen growth on host surface", "stunted host growth during colonization"

**Best Practice**: Start with broad terms, navigate to specific terms through hierarchy.

### PHIDO (PHI-base Disease Ontology)

**Purpose**: Standardized infectious disease terminology
**Application**: Annotate diseases on wild-type pathogen-host interactions
**Requirement**: Natural host (not model organism)

### Gene Ontology (GO)

**Three Branches**:
1. **Molecular Function**: What protein does (catalytic/binding activity)
2. **Biological Process**: Series of molecular events
3. **Cellular Component**: Subcellular locations and complexes

**Effector Requirement**: Must annotate with "effector-mediated modulation of host process by symbiont" (GO:0140418)

## Annotation Types and When to Use

### Gene Annotations
- **GO terms**: Function, process, localization
- **Physical interactions**: Co-IP, two-hybrid, etc.
- **Protein modifications**: Phosphorylation, ubiquitination

### Genotype Annotations (Single Organism)
- **Pathogen phenotypes**: Growth, morphology, stress resistance
- **Host phenotypes**: Defense responses, susceptibility markers

### Metagenotype Annotations (Interactions)
- **Interaction phenotypes**: Disease symptoms, compatibility outcomes
- **Disease names**: Specific infectious diseases  
- **Gene-for-gene**: R-gene/effector recognition systems

## Evidence and Experimental Conditions

### Evidence Codes
**Principle**: Match evidence code to experimental method used
**Examples**:
- Direct assay: Growth curves, microscopy observation
- Inferred from mutant phenotype: Gene knockout studies
- Physical interaction evidence: Co-IP, two-hybrid, pull-down

### Experimental Conditions
**Include When Relevant**:
- Growth medium (minimal vs rich)
- Temperature conditions
- Chemical treatments
- Delivery methods (infiltration, inoculation)

**Don't Over-Specify**: Include conditions key to experiment interpretation

## Common Curation Scenarios

### Scenario 1: Effector Gene Study
1. **Gene annotation**: GO molecular function + effector process (GO:0140418)
2. **Pathogen phenotype**: Growth/morphology on artificial media
3. **Interaction phenotype**: Disease symptoms on host plants
4. **Controls**: Wild-type pathogen behavior

### Scenario 2: Host Resistance Gene
1. **Gene annotation**: GO annotations for resistance protein
2. **Host phenotype**: Defense responses in isolated host
3. **Interaction phenotype**: Disease resistance in pathogen challenge
4. **Gene-for-gene**: If specific effector recognition demonstrated

### Scenario 3: Two-Hybrid Interaction Screen
1. **Physical interaction**: Protein-protein binding
2. **Evidence**: Two-hybrid (note directionality)
3. **Controls**: Negative controls and empty vector results

## Quality Standards

### What TO Curate
- Experimentally demonstrated results from the specific paper
- Direct measurements and observations
- Properly controlled experiments
- Biologically meaningful interactions

### What NOT to Curate
- Information from other papers (even if related)
- Speculation or discussion
- Known contaminants (ribosomal proteins in MS)
- Background information not experimentally verified

### Accuracy Principles
- Read ontology term definitions, don't rely on names alone
- Use most specific terms available
- Ensure experimental evidence matches evidence code
- Verify strain and genotype details

## Getting Help

### Built-in Help
- **'?' icons**: Context-sensitive help throughout interface
- **Term definitions**: Always displayed when selecting ontology terms
- **Autocomplete**: Suggests existing terms and annotations

### Human Support
- **"Contact curators" link**: Available throughout curation interface
- **Email**: contact@phi-base.org for general questions
- **Session comments**: Add questions in submission comments

### Common Questions
1. **"Can't find my gene in UniProt"**: Try BLAST search or contact UniProt
2. **"Term doesn't fit my experiment"**: Request new term via "Suggest new child term"
3. **"Unsure about evidence code"**: Describe experiment in comments, ask for guidance

## Practice Sessions

### Recommended Learning Path

1. **Week 1**: Complete 1-2 simple papers (single gene, clear phenotype)
2. **Week 2**: Practice complex genotypes and metagenotypes  
3. **Week 3**: Work with interaction phenotypes and disease annotations
4. **Week 4**: Handle physical interactions and effector studies

### Practice Papers (If Available)
- Start with papers from your own research area
- Choose papers with clear experimental designs
- Begin with single-gene studies before multi-gene interactions

## Session Management

### Best Practices
- **Save frequently**: Session URLs preserved automatically
- **Work in stages**: Complete over multiple sessions if complex
- **Review before submission**: Check all annotations for accuracy
- **Document thoroughly**: Use figure/table numbers and comments

### Before First Submission
- **Double-check gene accessions**: Ensure correct UniProt entries
- **Verify ontology terms**: Read definitions carefully
- **Check experimental evidence**: Matches what was actually done
- **Review controls**: Proper control annotations included

## Community Contribution

### Why Community Curation Matters
- **Author expertise**: Original researchers best understand their experiments
- **Scalability**: Community effort handles volume of literature
- **Accuracy**: Direct author involvement reduces interpretation errors
- **Timeliness**: Faster data availability than traditional curation

### Your Role
- **Contribute high-quality annotations** for your research area
- **Follow standards consistently** to maintain database quality
- **Provide feedback** on tools and ontology terms
- **Support training** of new curators in your field

## Resources and References

### Online Documentation
- PHI-Canto full documentation: <https://canto.phi-base.org/docs/index>
- PHIPO ontology browser: Use OBO Foundry links
- UniProt help: <https://www.uniprot.org/help/>
- GO documentation: <http://geneontology.org/>

### Training Materials in This Vault
- [[PHI-Canto-Complete-Curation-Protocol]]: Detailed step-by-step procedures
- [[UniProtKB-Gene-Identification-Guide]]: Detailed gene lookup procedures
- [[Ontology-Terms-Reference]]: Quick reference for common terms

### Further Learning
- BioGRID interaction evidence: <https://wiki.thebiogrid.org/doku.php/experimental_systems>
- BRENDA Tissue Ontology: <https://brenda-enzymes.org/ontology.php?ontology_id=3>
- Gene Ontology guidelines: <http://geneontology.org/docs/go-annotation-policies/>

---

*Welcome to the PHI-base community curation team! Your contributions help advance understanding of pathogen-host interactions worldwide.*