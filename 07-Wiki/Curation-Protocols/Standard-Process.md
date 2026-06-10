---
created: 2026-04-18
type: protocol
tags: [protocol, curation, standards]
---

# 📋 Standard PHI-Canto Curation Process

Comprehensive protocol for curating pathogen-host interaction literature.

## 🎯 Overview

The PHI-Canto curation process transforms published literature into structured database entries documenting pathogen-host interactions, protein functions, and experimental evidence.

## 📚 Phase 1: Literature Acquisition

### 1.1 Article Selection
- **Source**: PubMed, journal alerts, recommendations
- **Criteria**: Contains pathogen-host interactions with experimental evidence
- **Priority**: Recent publications (last 2 years) > high-impact journals > specific pathogen focus

### 1.2 Initial Assessment
- [ ] Abstract review for pathogen-host content
- [ ] Full text accessibility check
- [ ] Duplicate check against existing database
- [ ] Priority assignment (high/medium/low)

### 1.3 Database Entry
```bash
# Add article to tracking database
python3 daily_curation.py add [PMID] "Article Title" "Journal" [Year]
```

## 🔬 Phase 2: Literature Analysis

### 2.1 Article Review
- [ ] **Pathogen identification**: Species, strain, taxonomy
- [ ] **Host identification**: Species, tissue/organ, experimental system
- [ ] **Interaction type**: Parasitism, mutualism, commensalism, pathogenesis
- [ ] **Experimental approach**: Molecular, biochemical, genetic, phenotypic

### 2.2 Create Article Note
1. Use [[07-Wiki/Templates/Article-Template|Article Template]]
2. Fill in article metadata (PMID, DOI, journal, authors)
3. Document pathogen-host system details
4. Initial status: `queued` → `in_progress`

### 2.3 Protein/Gene Identification
- [ ] List all proteins/genes mentioned
- [ ] Identify systematic gene IDs (e.g., FGSG_xxxxx)
- [ ] Note functional annotations
- [ ] Check for existing database entries

## 🧬 Phase 3: Protein Characterization

### 3.1 For Each Protein
- [ ] **Gene ID**: Systematic identifier from genome annotation
- [ ] **Gene Name**: Common name or symbol
- [ ] **Protein Function**: Based on experimental evidence
- [ ] **Role in Pathogenesis**: Effector, virulence factor, resistance gene, etc.
- [ ] **UniProt Search**: Find accession number if available

### 3.2 Cross-Reference Validation
- [ ] Check UniProt for existing entries
- [ ] Verify gene IDs against genome databases
- [ ] Search for orthologs in related species
- [ ] Link to existing PHI-base entries

### 3.3 Database Updates
```bash
# Log protein curation work
python3 session_logger.py quick "Project Name" "Characterized X proteins" [protein_count] [interactions] [hours]
```

## 🧪 Phase 4: Evidence Documentation

### 4.1 Experimental Evidence Types

**Strong Evidence** (High confidence):
- 🧪 **Complementation**: Restores wild-type phenotype
- ✂️ **Gene deletion/knockout**: Loss-of-function phenotype
- 📈 **Overexpression**: Gain-of-function or enhanced phenotype
- ⚗️ **Direct biochemical**: Purified protein functional assays

**Supporting Evidence** (Medium confidence):
- 🔬 **Genetic analysis**: Mutant analysis, allele studies
- 📊 **Expression analysis**: qRT-PCR, RNA-seq, proteomics
- 🎯 **Localization**: Subcellular localization studies
- 🤝 **Interaction studies**: Y2H, co-immunoprecipitation

**Weak Evidence** (Low confidence):
- 📈 **Correlation studies**: Expression correlates with phenotype
- 💻 **Computational prediction**: Homology, domain analysis
- 📚 **Literature inference**: Based on related proteins

### 4.2 Evidence Documentation
For each protein-phenotype relationship:
- [ ] **Method**: Experimental approach used
- [ ] **Result**: Observed phenotype or activity
- [ ] **Controls**: Appropriate negative/positive controls
- [ ] **Quantification**: Statistical significance, effect size
- [ ] **Reproducibility**: Multiple experiments, independent studies

## 📊 Phase 5: Database Population

### 5.1 Protein Entries
```python
# Add proteins to database
db.add_protein(
    gene_id="FGSG_12345",
    species_id=1,  # Fusarium graminearum
    name="Effector protein description", 
    gene_name="EffectorName",
    function_summary="Brief functional description",
    protein_type="effector"
)
```

### 5.2 Protein-Article Relationships
- [ ] Link each protein to the article
- [ ] Specify evidence type (complementation, knockout, etc.)
- [ ] Add context description
- [ ] Mark curation status

### 5.3 Update Article Status
```bash
# Update article status in database
python3 daily_curation.py status [PMID] curated
```

## ✅ Phase 6: Quality Assurance

### 6.1 Internal Review
- [ ] **Completeness**: All relevant proteins documented
- [ ] **Accuracy**: Gene IDs, protein names, functions correct
- [ ] **Evidence**: Experimental support clearly documented
- [ ] **Consistency**: Follows established naming conventions

### 6.2 Cross-Validation
- [ ] **Species check**: Taxonomy IDs correct
- [ ] **Gene ID validation**: Against genome databases
- [ ] **UniProt verification**: Accession numbers valid
- [ ] **Literature links**: PMID, DOI accessible

### 6.3 Final Documentation
- [ ] Complete article note with all findings
- [ ] Update database with final status: `curated` → `reviewed`
- [ ] Generate session log with summary
- [ ] Update [[07-Wiki/Article-Registry|Article Registry]]

## 🎯 Quality Standards

### Minimum Requirements
- ✅ At least one protein with experimental evidence
- ✅ Clear pathogen-host system identification
- ✅ Gene ID or UniProt accession when available
- ✅ Evidence type classification
- ✅ Experimental method documentation

### Best Practices
- 🎯 Focus on novel findings and interactions
- 🔗 Cross-reference with existing database entries
- 📝 Clear, concise functional descriptions
- 🧪 Prioritize direct experimental evidence
- 📊 Include quantitative data when available

## 🛠️ Tools and Resources

### Database Tools
```bash
python3 daily_curation.py progress    # Check pipeline status
python3 daily_curation.py gaps       # Find missing data
python3 show_recent.py               # Recent activity overview
python3 generate_article_registry.py # Update wiki dashboard
```

### External Resources
- **PubMed**: Literature search and PMID lookup
- **UniProt**: Protein sequence and functional annotation
- **PHI-base**: Existing pathogen-host interaction data
- **NCBI Taxonomy**: Species and strain identification
- **Genome databases**: Gene ID verification (FungiDB, etc.)

### Obsidian Features
- **Templates**: Standardized article curation format
- **Links**: Connect articles, proteins, and species
- **Tags**: Organize by status, project, evidence type
- **Graph view**: Visualize relationships between entities

## 📈 Productivity Tracking

### Session Logging
Each curation session should be logged with:
```bash
python3 session_logger.py quick "Project" "Work description" [proteins] [interactions] [hours]
```

### Progress Metrics
- **Articles per week**: Target 2-3 articles depending on complexity
- **Proteins per session**: Average 2-4 proteins per article
- **Interactions per protein**: 1-3 depending on experimental evidence
- **Quality score**: Based on evidence strength and completeness

### Workflow Optimization
- **Batch processing**: Group similar articles or species
- **Template reuse**: Leverage existing curation for related work
- **Cross-validation**: Check new entries against existing database
- **Regular reviews**: Weekly assessment of curation quality and progress

---

## 📞 Help and Support

- **Templates**: [[07-Wiki/Templates/Article-Template|Article Template]]
- **Registry**: [[07-Wiki/Article-Registry|Article Registry Dashboard]]
- **Tools**: `11-CLAUDE-AI/db/` directory
- **Session logs**: `11-CLAUDE-AI/SESSION-LOGS/` for historical context

**Questions or issues?** Document in session notes and review during next curation session.