---
created: 2026-04-20
type: reference
tags: [uniprot, gene-identification, standards]
project: PHI-Canto
---

# UniProtKB Gene Identification Guide for PHI-Canto

## Overview

Comprehensive guide for identifying and validating genes using UniProtKB for PHI-Canto curation. Proper gene identification is critical for database integration and cross-referencing.

## Why UniProtKB for PHI-Canto?

### Database Integration Benefits
- **Standardization**: Consistent gene identifiers across different strains/studies
- **Cross-referencing**: Links to other databases (NCBI, Ensembl, etc.)
- **Disambiguation**: Handles cases where same name used for different proteins
- **Strain integration**: Maps strain-specific genes to reference sequences

### UniProtKB Structure
- **Swiss-Prot**: Manually reviewed, high-quality annotations
- **TrEMBL**: Computationally annotated, larger coverage
- **Reference Proteomes**: Representative protein sets for organisms

## Step-by-Step Gene Identification

### Step 1: Identify Reference Proteome

**Why Reference Proteomes?**
- PHI-base uses reference proteomes to standardize gene entries
- Allows integration of data from different strains at gene level
- Strain-specific information captured in genotype annotations

#### Finding Reference Proteomes:
1. Navigate to <https://www.uniprot.org/help/reference_proteome>
2. Search by organism name (scientific or common)
3. Look for "Reference proteome" label
4. Note proteome ID (e.g., UP000001875 for *Fusarium graminearum*)

#### If No Reference Proteome:
- Use the strain actually studied in the paper
- Note this choice in curation comments
- Consider requesting reference proteome designation

### Step 2: Gene Search Strategies

#### Strategy 1: Gene Name Search
**Format**: `[gene name] [species name]`
**Examples**:
- `Tri5 Fusarium graminearum`
- `AVR-Pik Magnaporthe oryzae`
- `NPR1 Arabidopsis thaliana`

**Tips**:
- Try both official and common gene names
- Include organism name to avoid cross-species matches
- Use quotation marks for exact phrases if needed

#### Strategy 2: Locus Tag Search  
**Format**: `[locus_tag] [species name]`
**Examples**:
- `FGRRES_03537 Fusarium graminearum`
- `MGG_05269 Magnaporthe oryzae`

**When to Use**:
- Gene has no standard name
- Paper only provides genomic identifiers
- Multiple genes with similar names exist

#### Strategy 3: Protein Description Search
**Format**: `[protein function] [species name]`
**Examples**:
- `trichodiene synthase Fusarium graminearum`
- `cutinase Fusarium solani`
- `polygalacturonase Botrytis cinerea`

#### Strategy 4: Protein Sequence BLAST
**When to Use**:
- Above searches fail to find gene
- Need to verify sequence identity
- Working with newly sequenced organisms

**Process**:
1. Navigate to <https://www.uniprot.org/blast/>
2. Paste protein sequence from paper/GenBank
3. Select database: "UniProtKB Swiss-Prot" or "UniProtKB TrEMBL"
4. Adjust parameters if needed (default usually sufficient)
5. Submit and review results

### Step 3: Entry Validation and Selection

#### Critical Distinctions
**Entry vs Entry Name**:
- **Entry** (accession): P12345, Q9XYZ1 - USE THIS for PHI-Canto
- **Entry name**: TRI5_FUSGR, CUTB_FUSSO - DON'T use this

#### Selection Criteria (in order of preference)

1. **Reviewed entries** (Swiss-Prot) from reference proteome
2. **Reviewed entries** from studied strain
3. **Unreviewed entries** (TrEMBL) from reference proteome  
4. **Unreviewed entries** from studied strain

#### Filtering Results
**Use left-hand filters**:
- **Reviewed**: Check to show only Swiss-Prot entries
- **Model organisms**: If applicable
- **Proteome**: Filter by specific proteome ID

### Step 4: Entry Verification

#### Information to Verify
1. **Gene name matches**: Check gene names/synonyms match paper
2. **Species/strain**: Confirm correct organism
3. **Protein function**: Verify description matches expected function
4. **Sequence length**: Reasonable size for protein type

#### Red Flags
- Very short sequences (<50 amino acids) unless expected
- Generic descriptions ("hypothetical protein" when specific function known)
- Wrong species despite name match
- Massive size differences from expected

### Step 5: Handling Special Cases

#### Multiple Entries for Same Gene
**Causes**:
- Different strains
- Alternative splice forms
- Gene duplications
- Database redundancy

**Resolution Strategy**:
1. Prefer reference proteome entry
2. Check if entries are truly different genes or duplicates
3. Select most complete annotation
4. Use sequence identity to verify

#### Gene Not Found in UniProtKB
**Troubleshooting Steps**:
1. **Check spelling**: Verify gene names, species names
2. **Try synonyms**: Search alternative gene names
3. **Relaxed search**: Search without species restriction
4. **BLAST search**: Use protein sequence if available
5. **Contact resources**:
   - Paper authors for clarification
   - UniProt for assistance adding entry
   - PHI-base curators for guidance

#### Working with Recent Publications
- New genes may not be in UniProtKB yet
- Check if submitted to GenBank/EMBL
- Contact authors for UniProt submission
- May need to wait for database updates

## Organism-Specific Considerations

### Fungal Pathogens
**Common Issues**:
- Multiple strains with different gene IDs
- Sexual/asexual naming systems
- Recent taxonomic reclassifications

**Resources**:
- FungiDB for additional gene information
- Ensembl Fungi for genomic context
- Species-specific databases (e.g., AspGD, CGD)

### Bacterial Pathogens  
**Common Issues**:
- Strain designation critical for pathogenicity
- Plasmid-encoded genes
- Type III secretion system effectors

**Resources**:
- NCBI RefSeq for bacterial genomes
- Species-specific databases (e.g., PseudoCAP)

### Plant Hosts
**Common Issues**:
- Large gene families (R-genes, PR proteins)
- Allelic variants
- Tissue-specific expression variants

**Resources**:
- TAIR for Arabidopsis
- Plant Ensembl
- Species-specific databases

## Quality Control Checklist

### Before Submitting to PHI-Canto
- [ ] Entry accession number copied correctly (no typos)
- [ ] Verified Entry vs Entry Name distinction
- [ ] Confirmed species/strain match
- [ ] Checked gene name/function alignment
- [ ] Noted if non-reference proteome used

### Documentation
- [ ] Record search strategy used
- [ ] Note any ambiguities or uncertainties
- [ ] Document strain differences if relevant
- [ ] Include rationale for entry selection

## Common Error Patterns

### Accession Number Errors
- **Wrong format**: Using entry names instead of accession numbers
- **Typos**: Confusing O (letter) with 0 (number)
- **Database confusion**: Using UniParc instead of UniProtKB IDs

### Species/Strain Confusion  
- **Related species**: Selecting from wrong species with similar names
- **Strain specificity**: Missing strain-specific genes
- **Taxonomic changes**: Using outdated species names

### Function Mismatches
- **Homolog confusion**: Selecting functionally different homologs
- **Domain confusion**: Selecting proteins with similar domains but different functions

## Troubleshooting Resources

### UniProt Help Resources
- **General help**: <https://www.uniprot.org/help/>
- **Search syntax**: <https://www.uniprot.org/help/text-search>
- **BLAST help**: <https://www.uniprot.org/help/sequence-annotation>

### Contact Information
- **UniProt feedback**: <https://www.uniprot.org/contact>
- **PHI-base support**: contact@phi-base.org
- **Paper authors**: Often most direct route for new genes

### Alternative Approaches
If UniProtKB search fails:
1. **NCBI Protein**: Search and cross-reference to UniProt
2. **Species databases**: Check organism-specific resources
3. **Literature mining**: Review citing papers for additional identifiers
4. **Homology search**: Find functionally similar proteins in related species

## Examples and Case Studies

### Case Study 1: Well-Known Effector
**Gene**: AVR-Pik from *Magnaporthe oryzae*
**Search strategy**: "AVR-Pik Magnaporthe oryzae"
**Result**: Q0WYB1 (reviewed entry)
**Validation**: Confirmed avirulence protein function, correct species

### Case Study 2: Metabolic Gene
**Gene**: Tri5 from *Fusarium graminearum*  
**Search strategy**: "Tri5 Fusarium graminearum"
**Alternative**: "trichodiene synthase Fusarium graminearum"
**Result**: O42614 (reviewed entry)
**Validation**: Confirmed trichodiene synthase activity, reference proteome

### Case Study 3: New Gene Requiring BLAST
**Situation**: Novel effector, only protein sequence available
**Approach**: BLAST search against UniProtKB
**Result**: High similarity to known effectors, selected best match
**Documentation**: Noted sequence similarity score and coverage

---

*Accurate gene identification is the foundation of high-quality PHI-base curation. When in doubt, contact the curation team for assistance.*