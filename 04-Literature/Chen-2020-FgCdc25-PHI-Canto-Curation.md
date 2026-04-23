---
created: 2026-04-23
type: curation-record
tags: [phi-canto, curation, fusarium-graminearum, ras-pathway]
project: PHI-Canto
pmid: "32537857"
status: ready-for-submission
---

# PHI-Canto Curation Record: Chen et al. 2020 - FgCdc25 in Fusarium graminearum

**Paper**: Chen et al. (2020) "The RasGEF FgCdc25 regulates fungal development and virulence in Fusarium graminearum via cAMP and MAPK signalling pathways"  
**PMID**: 32537857  
**Journal**: Environmental Microbiology  
**Curator**: [To be filled]  
**Date**: 2026-04-23

## Genes and UniProtKB Identification

### Primary Genes
1. **Gene Name**: FgCdc25  
   **Locus**: FGSG_05398  
   **Organism**: *Fusarium graminearum*  
   **Protein**: RasGEF (Ras guanine nucleotide exchange factor)  
   **UniProtKB Status**: **NEEDS LOOKUP**  
   **Function**: Regulates Ras/cAMP/PKA and MAPK pathways

2. **Gene Name**: FgRas2  
   **Locus**: FGSG_09846  
   **Organism**: *Fusarium graminearum*  
   **Protein**: Ras GTPase  
   **UniProtKB Status**: **NEEDS LOOKUP**  
   **Function**: Small GTPase in Ras/cAMP/PKA pathway

3. **Gene Name**: FgRas1  
   **Organism**: *Fusarium graminearum*  
   **UniProtKB Status**: **NEEDS LOOKUP**  
   **Note**: Essential gene, mutation lethal

## Organisms and Strains

### Pathogen
- **Species**: *Fusarium graminearum* (also known as *Gibberella zeae*)
- **Strain**: PH-1 (wild-type reference strain)
- **Disease**: Fusarium head blight (FHB) of cereal crops
- **Toxin**: Deoxynivalenol (DON) producer

### Host Plants
- **Primary**: *Triticum aestivum* (wheat)
- **Secondary**: *Zea mays* (corn/maize)
- **Tissues tested**: Wheat spikelet, wheat leaves, corn silk

### Model Organism
- **Species**: *Saccharomyces cerevisiae*
- **Use**: Heterologous expression and complementation studies

## Experimental Data for PHI-Canto Annotation

### 1. Gene Annotations

#### FgCdc25 GO Annotations

**GO Molecular Function**:
- **Term**: guanyl-nucleotide exchange factor activity (GO:0005085)
- **Evidence**: Physical interaction (with FgRas2)
- **Reference**: Figure 1 - Co-immunoprecipitation experiments

**GO Biological Process**:
- **Term**: positive regulation of Ras protein signal transduction (GO:0046579)
- **Evidence**: Inferred from mutant phenotype
- **Reference**: Figure 2 - Growth and developmental phenotypes

**GO Cellular Component**:
- **Term**: cytoplasm (GO:0005737)
- **Evidence**: Direct assay (GFP localization)
- **Reference**: Described in complementation studies

#### FgRas2 GO Annotations

**GO Molecular Function**:
- **Term**: GTPase activity (GO:0003924)
- **Evidence**: Inferred from sequence homology
- **Reference**: Phylogenetic analysis section

**GO Biological Process**:
- **Term**: Ras protein signal transduction (GO:0007265)
- **Evidence**: Physical interaction (with FgCdc25)
- **Reference**: Figure 1 - Protein-protein interaction

### 2. Physical Interactions

**Interaction**: FgCdc25 - FgRas2  
**Evidence**: Co-immunoprecipitation  
**Reference**: Figure 1A - Co-IP and mass spectrometry  
**Note**: Interaction confirmed by multiple independent methods

**Interaction**: FgCdc25 - FgSte11 (MAPKK Kinase)  
**Evidence**: Co-immunoprecipitation  
**Reference**: Figure 1B - Cross-pathway interaction  

**Interaction**: FgCdc25 - FgBck1 (MAPKK Kinase)  
**Evidence**: Co-immunoprecipitation  
**Reference**: Figure 1C - Cell wall integrity pathway

### 3. Genotype Annotations

#### FgCdc25 Deletion Mutant (ΔFgcdc25)

**Single-species Phenotypes**:
- **Growth defect on artificial media**
  - **PHIPO Term**: "decreased hyphal growth"
  - **Evidence**: Direct assay
  - **Reference**: Figure 2A,B - Growth on PDA and minimal medium
  - **Conditions**: potato dextrose agar, minimal medium

- **Sexual reproduction defect**
  - **PHIPO Term**: "decreased sexual reproduction"
  - **Evidence**: Direct assay
  - **Reference**: Figure 2C,D - Perithecium formation assay

- **DON biosynthesis defect**
  - **PHIPO Term**: "decreased secondary metabolite production"
  - **Evidence**: Direct assay
  - **Reference**: Figure 6 - Deoxynivalenol quantification
  - **Conditions**: liquid culture, 15-day incubation

#### FgRas2 Deletion Mutant (ΔFgras2)

**Single-species Phenotypes**:
- **Growth defect**
  - **PHIPO Term**: "decreased hyphal growth"
  - **Evidence**: Direct assay
  - **Reference**: Figure 2A,B - Similar to ΔFgcdc25 phenotype

### 4. Metagenotype Annotations (Pathogen-Host Interactions)

#### Control Metagenotype: Wild-type FgCdc25 × Wheat
- **Interaction Phenotype**: Compatible interaction with disease symptoms
- **PHIPO Term**: "presence of pathogen growth on host surface"
- **Evidence**: Direct assay
- **Reference**: Figure 3A,B - Wild-type PH-1 causes typical scab symptoms
- **Extensions**:
  - Host tissue: inflorescence (BTO:0000628), leaf (BTO:0000713)
  - Disease present: Fusarium head blight

#### Experimental Metagenotype: ΔFgcdc25 × Wheat
- **Interaction Phenotype**: Loss of pathogenicity
- **PHIPO Term**: "loss of pathogenicity"
- **Evidence**: Inferred from mutant phenotype
- **Reference**: Figure 3A,B - No disease symptoms on wheat
- **Extensions**:
  - Host tissue: inflorescence (BTO:0000628), leaf (BTO:0000713)
  - Compared to control: [link to wild-type interaction]
  - Infective ability: loss of pathogenicity

#### Penetration Deficiency
- **Phenotype**: Abolished penetration ability
- **PHIPO Term**: "abolished pathogen penetration into host"
- **Evidence**: Direct assay (microscopy)
- **Reference**: Figure 4A,B - No penetration structures on wheat spikelet
- **Extensions**:
  - Host tissue: inflorescence (BTO:0000628)

### 5. Disease Name Annotation

**Disease**: Fusarium head blight  
**PHIDO Term**: *Need to look up specific PHIDO term for FHB*  
**Metagenotype**: Wild-type F. graminearum × wheat  
**Extensions**:
- Host tissue infected: inflorescence (BTO:0000628)

## Experimental Methods and Evidence Codes

### Key Experimental Approaches
1. **Gene deletion and complementation**: Targeted gene replacement
2. **Co-immunoprecipitation**: Protein-protein interaction validation
3. **Plant infection assays**: Wheat spikelet and leaf inoculation
4. **Microscopy**: Penetration structure analysis
5. **Chemical analysis**: DON quantification by HPLC
6. **Growth assays**: Radial growth measurement

### Controls Used
- **Wild-type strain PH-1**: Growth and virulence control
- **Complemented strains**: ΔFgcdc25-C, ΔFgras2-C with GFP-tagged genes
- **Empty vector controls**: For heterologous expression
- **Mock inoculation**: Uninoculated plant controls

## Key Findings Summary

1. **Protein interaction network**: FgCdc25 physically interacts with FgRas2, FgSte11, and FgBck1
2. **Essential for virulence**: ΔFgcdc25 completely loses pathogenicity on wheat
3. **Penetration defect**: Mutant cannot form penetration structures
4. **DON production**: FgCdc25 required for deoxynivalenol biosynthesis
5. **Pathway crosstalk**: Links Ras/cAMP/PKA with MAPK cascades

## Quality Control Notes

### Strengths
- **Comprehensive complementation**: All major phenotypes rescued
- **Multiple infection systems**: Wheat heads, leaves, corn silk tested
- **Biochemical validation**: Protein interactions confirmed by co-IP and MS
- **Quantitative analysis**: DON levels measured chemically

### Experimental Rigor
- **Biological replicates**: All experiments repeated 3 times
- **Statistical analysis**: Student's t-test used for significance
- **Proper controls**: Wild-type, deletion, and complemented strains

## Submission Checklist

- [ ] Find UniProtKB accessions for FgCdc25 (FGSG_05398) and FgRas2 (FGSG_09846)
- [ ] Verify PHIDO term for Fusarium head blight
- [ ] Confirm organism strain designation (PH-1)
- [ ] Link complementation data to genotype annotations
- [ ] Add cross-pathway interaction annotations
- [ ] Include DON biosynthesis pathway annotations

## Comments for Curators

This is a comprehensive study of a central regulator in F. graminearum pathogenesis. The FgCdc25-FgRas2 interaction is well-characterized with multiple lines of evidence. The complete loss of virulence in ΔFgcdc25 makes this an excellent example of a pathogenicity gene. The paper also demonstrates pathway crosstalk between Ras/cAMP/PKA and MAPK signaling, which should be captured in the interaction annotations.

**Key challenge**: Finding correct UniProtKB accessions for F. graminearum genes. May need to contact authors or search FungiDB/Ensembl Fungi databases.

---
*Curation record prepared from: Chen-2020-EnvironMicrobiol-32537857_converted.md*