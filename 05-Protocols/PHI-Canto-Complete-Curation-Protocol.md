---
created: 2026-04-20
type: protocol
tags: [curation, phi-canto, workflow]
project: PHI-Canto
---

# PHI-Canto Complete Curation Protocol

## Overview

Complete step-by-step protocol for curating pathogen-host interaction data in PHI-Canto. This protocol covers the entire workflow from literature identification to session submission.

## Session Initiation

### 1. Finding and Starting a Curation Session

1. Navigate to PHI-Canto interface
2. Enter **PubMed ID** in search box (PMID: prefix optional)
3. Click "Start curating" and confirm curator details:
   - Name
   - Email address  
   - ORCID (optional)
4. Session URL is preserved - curation can be completed over multiple sessions

### 2. Session Reassignment (if needed)
- Use "Reassign paper" button to delegate to first author or lab member
- Can reassign after starting using "Reassign" button in upper right

## Gene and Organism Management

### 3. Adding Genes via UniProtKB

**Critical**: Use UniProtKB accession numbers for gene disambiguation.

#### UniProtKB Lookup Process:
1. **Identify reference proteome** for organism
   - Search at <https://www.uniprot.org/help/reference_proteome>
   - If no reference proteome exists, use strain studied

2. **Locate gene of interest** using:
   - Author gene name/primary name + species (e.g. "Tri5 Fusarium graminearum")
   - Locus ID + species (e.g. "FGRRES_03537 Fusarium graminearum")
   - Protein description (e.g. "Trichodiene synthase")
   - BLAST protein sequence against UniProtKB

3. **Select correct entry**:
   - Use **'Entry'** accession number (column 1), NOT 'Entry name'
   - Prefer 'Reviewed entries' when multiple options exist
   - Filter using left-hand 'Reviewed entries' filter

#### Non-gene Papers
For papers without gene-specific information:
- Check "This paper does not contain any gene-specific information"
- Select appropriate reason from dropdown
- Complete session with "Continue" → "Finish"

### 4. Adding Host Organisms (no genes specified)
- Use organism picker below gene entry field
- Search by scientific name, common name, or NCBI Taxonomy ID

### 5. Strain Management

For every organism, add experimental strains:
- **Strain definition**: Any taxonomic classifier more specific than species (subspecies, varieties, pathovars, cultivars, strains)

#### Strain Entry Methods:
- **Select from list**: Type to filter, use mouse/arrow keys + Enter/Tab
- **Add custom strain**: Type name → click "Add strain" or hit Enter (highlighted in orange)
- **Unknown strain**: Use button when publication doesn't specify strain

**Important**: Background mutations should NOT be in strain name unless conventional - specify via 'Background' field in genotype creation.

## Genotype Creation and Management

### 6. Single-Allele Genotypes

#### Quick Creation:
- **Deletion**: Use "Deletion" button shortcut
- **Other types**: Use "Other genotype..." button

#### Allele Details Required:
1. **Allele name** (optional): e.g. "TRI5-1-499"
   - Wild type/deletion get default names
   - Autocomplete suggests existing alleles
2. **Allele type**: Choose from dropdown, use 'unknown' or 'other' for complex cases
3. **Allele description**: Required for partial deletion/substitution
   - Number positions from ATG 'A' (protein-coding genes)
   - Promoter mutations use hyphen prefix (e.g. "-150")
4. **Expression level**: Relative to wild-type
   - Choose "Not assayed" if product level not measured
5. **Background alleles**: Add via "Add/edit background" option

### 7. Multi-Locus Genotypes

1. Create all constituent single alleles first
2. Select 2+ alleles using checkboxes  
3. Click "Combine selected genotypes"
4. New multi-allele genotype appears in separate table

#### Wild-Type Usage Rules:
- **Normal expression**: Don't annotate with phenotype unless needed as experimental control
- **Altered expression**: Include in genotypes only if over/under-expressed
- **Control metagenotypes**: Can use wild-type with normal expression

### 8. Genotype Management Options

Mouse over any genotype to access:
- **Start phenotype annotation**: Begin curation workflow
- **View annotations**: See details and existing annotations
- **Edit details**: Modify genotype information, add/remove alleles
- **Copy and edit**: Create new genotype with amendments
- **Add/edit background**: Specify background alleles
- **Delete**: Remove genotype (disabled if has annotations)

## Metagenotype Creation

### 9. Metagenotype Assembly

**Definition**: Combination of pathogen genotype + host genotype = pathogen-host interaction genotype

#### Creation Process:
1. Access via "Metagenotype Management" link
2. Select pathogen and host organisms (if multiple present)
3. Choose one pathogen genotype (radio button)
4. Choose one host genotype (radio button)
5. Click "Make metagenotype"

#### Host Strain Selection:
- Hosts with no alleles show strain list (wild-type genotypes)
- Select strain using radio button
- Strain info embedded in metagenotype

### 10. Control Metagenotypes

**Critical**: Create control metagenotype BEFORE experimental metagenotype
- Contains control genotypes (usually wild-type)
- Required for phenotype disambiguation
- Link experimental to control via annotation extensions
- Exception: Some experiments (e.g. empty vector controls) may not allow control creation

## Annotation Workflows

### 11. Phenotype Curation

#### Starting Phenotype Annotations:

**Single-species phenotypes:**
- Via Genotype Management: "Start pathogen/host phenotype annotation"
- Via Single allele workflow: Select gene → "Single allele phenotype"

**Pathogen-host interaction phenotypes:**
- Via Metagenotype Management: "Annotate pathogen-host interaction phenotype" or "Annotate gene-for-gene phenotype"

#### PHIPO Term Selection:
1. **Search strategy**: Type descriptive text, choose from autocomplete
2. **Broad → specific**: Start with broader terms, refine iteratively  
3. **Read definitions**: Ensure term accurately describes experiment
4. **Term hierarchy**: Use most specific term available
5. **Request new terms**: "Suggest a new child term" if needed

#### Evidence and Conditions:
1. **Evidence code**: Select from dropdown menu
2. **Experimental conditions** (optional but recommended):
   - Medium type (minimal vs rich)
   - Growth format (agar vs liquid)
   - Delivery mechanism
   - Chemical additions/exclusions
   - Temperature conditions
   - Select from autocomplete or add custom (displayed in red pending review)

#### Annotation Extensions:
Add extensions for specificity:

**Single-species phenotypes:**
- **Penetrance**: Proportion showing phenotype (qualitative/quantitative)
- **Severity**: Qualitative extent of expression  
- **Assayed feature**: Specific gene/RNA/protein used in assay

**Pathogen-host interaction phenotypes:**
- **Host tissue infected**: BRENDA Tissue Ontology terms
- **Infective ability**: High-level pathogenicity/virulence change
- **Compared to control genotype**: Link to control metagenotype
- **Outcome of interaction**: Disease presence/absence

**Gene-for-gene phenotypes:**
- **Host tissue infected**: Tissue type specification
- **Compared to control genotype**: Control metagenotype link
- **Gene-for-gene interaction**: Resistance gene, effector recognition, compatibility
- **Inverse gene-for-gene interaction**: Susceptibility gene, necrotrophic effector

### 12. Disease Name Curation

#### Application Criteria:
- Metagenotypes with wild-type genes
- Disease present (susceptible host + compatible pathogen)
- Natural host-pathogen combination (not model host)
- Annotate tissue where disease normally observed

#### PHIDO Term Selection:
1. Search using disease name or broader terms
2. Read definitions for accuracy
3. Use most specific term available
4. Request new terms if needed

#### Disease Extensions:
- **Host tissue infected**: Specify anatomical location using BRENDA terms

### 13. Physical Interaction Curation

#### Interaction Setup:
1. Select species for each interacting partner
2. Choose genes for both partners
3. Select interaction type/evidence code
4. Note directionality requirements

#### Directionality Guidelines:

**Asymmetric interactions** (curate in one direction):
- Affinity Capture methods: A affinity captures B
- Far Western: A captures B
- FRET: A is donor to B
- Two-hybrid: A binds activation domain construct with B
- Protein-peptide/RNA: A binds to peptide/RNA B

**Symmetric interactions** (enter once, either direction):
- Co-crystal Structure: A co-crystallizes with B
- Co-fractionation/purification: A co-fractionates/purifies with B
- Reconstituted Complex: A forms complex with B
- PCA: A interacts with B

### 14. Effector Curation Requirements

**Critical**: For pathogen effectors in pathogen-host interactions:

1. **Required GO annotation**: Annotate pathogen gene with:
   - "effector-mediated modulation of host process by symbiont" (GO:0140418)
   - Or child terms

2. **Optional molecular function**: If known, annotate with:
   - Specific GO Molecular Function term
   - Must include 'part_of' annotation extension linking to GO:0140418

## Quality Control and Finalization

### 15. Annotation Review and Management

#### Edit/Copy/Delete Functions:
- **Edit**: Modify existing annotations
- **Transfer**: Copy phenotype to other genotypes/metagenotypes
- **Copy and edit**: Create new annotation with modifications
- **Delete**: Remove annotation

#### Multiple Condition Handling:
- Same phenotype, different conditions: Use "Copy and edit"
- Multiple tissues: Separate annotations unless simultaneous
- Extensions NOT occurring together: Create separate annotations

### 16. Session Documentation

#### Required Information:
1. **Figure/Table numbers**: Prefix with "Figure"/"Table", use "S" for supplementary
2. **Annotation comments**: Additional details not covered by evidence codes
   - Comments NOT displayed on PHI-base website
   - Used by approval team for session checking

### 17. Session Submission

#### Standard Submission:
1. Navigate to Curation Summary page
2. Click "Submit to curators" button
3. Add optional comments/questions for curators
4. Click "Finish" (NO further changes possible after this)

#### No Experimental Data Submission:
1. Check "No experimental results to add?" checkbox
2. Select reason from dropdown
3. Complete submission process

## Best Practices and Guidelines

### Data Quality Standards
- Only curate experimentally supported information from the specific paper
- Use most specific ontology terms available
- Include experimental conditions key to the experiment
- Avoid contaminated/non-meaningful interactions
- Ensure accurate directionality for physical interactions

### Session Management
- Sessions preserved at stable URLs - complete over multiple sessions if needed
- Use "Contact curators" link for questions/assistance
- Read help documentation via '?' icons throughout interface

### Post-Submission
- View annotations remains available
- Contact curation team for changes after submission
- Session enters approval workflow with PHI-base experts

## Troubleshooting

### Common Issues
- **UniProt entry not found**: Check typos, entry vs entry name, UniProtKB vs UniParc
- **Can't delete genotype**: Remove annotations first
- **Wrong interaction direction**: Delete and restart from correct gene
- **Missing terms**: Request new terms via "Suggest new child term"

### Contact Information
- General questions: contact@phi-base.org
- Session-specific issues: Use "Contact curators" link in interface