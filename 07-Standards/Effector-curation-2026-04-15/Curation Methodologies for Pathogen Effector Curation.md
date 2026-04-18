---
title: Curation Methodologies for Pathogen Effector Curation
aliases: [Effector Curation Guidelines, PHI-base Effector Curation]
tags: [PHI-base, biocuration, effectors, ontology, GO, pathogen-host, SOP]
type: resource
status: active
created: 2026-04-15
updated: 2026-04-15
related: [[PHI-base]], [[PHI-Canto]], [[GO Annotation]], [[Biocuration Standards]]
---

```table-of-contents
```




# Curation Methodologies for Pathogen Effector Curation

This document outlines the specialised protocols, terminology, and best practices required for accurate curation of pathogen effector genes in [[PHI-base]], with emphasis on genotype-phenotype relationships, [[GO Annotation]], and pathogen-host interactions.

---

## 1. Effector GO Annotation

### 1.1 Mandatory Effector GO Biological Process Term
- Every effector entry must include a GO biological process term beginning with:  
  **"effector-mediated …"**
- This acts as a primary effector tag for identification within [[PHI-base]].

### 1.2 Additional GO Terms
Where supported by experimental evidence:

- **Biological process**, e.g.  
  - secretion by cell  
- **Cellular component**, e.g.  
  - host cell nucleus  
  - host cell cytoplasm  

> Only include GO terms explicitly supported by experimental data (e.g. localisation assays, secretion experiments).

---

## 2. Pathogen Genotypes

Use controlled, standardised genotype descriptions.

### 2.1 Wild Type (WT)
- Unmodified strain.

### 2.2 Disruption / Deletion / Knockdown
Gene expression reduced or eliminated via:
- Split-marker gene deletion  
- CRISPR-Cas9  
- RNA interference (RNAi)

### 2.3 Complementation
- Restoration of gene function by re-introducing the wild-type allele (typically ectopic).

**Example:**  
Sp1Δ–Sp1 transformant  
→ **Genotype label:** Complement (Ectopic)

### 2.4 Overexpression
- Increased expression (e.g. CaMV 35S promoter).

### 2.5 GFP Fusion Lines
- GFP-tagged proteins for localisation/expression studies.

### 2.6 Overexpression of GFP-Tagged Protein
- Combined GFP-tag + overexpression.

**Example:**  
Swap70-GFP transformant  
→ see [[PHI-Canto]] (PMID:30049706)

### 2.7 Signal Peptide Deletions
- Used to test secretion/localisation.

### 2.8 Amino Acid Substitutions
- Site-directed mutations.

**Example:**  
Ire1(aaS896A) [Ectopic]

---

## 3. Metagenotypes (Pathogen-Host Combinations)

- Correctly link:
  - Pathogen genotype  
  - Host species  
  - Host cultivar  

Accurate metagenotype assignment is essential for:
- biological interpretation  
- downstream data reuse  
- FAIR data integration  

---

## 4. Pathogen Phenotype

- Only record if **different from wild type**.
- Many effector mutants show **no detectable phenotype**.

---

## 5. Pathogen-Host Interaction Phenotypes

Standard comparative framework:

1. Wild-type pathogen × host  
2. Effector mutant × host  
3. Complement strain × host  

→ Enables clear attribution of phenotype to gene function.

---

## 6. Wild-Type RNA Expression Levels

Typical annotation:
- **"RNA level increased"**
- Often extended:
  - "during response to host"

> Only curate when supported by expression data (e.g. RT-qPCR, RNA-seq).

---

## 7. Disease Name

- Must correspond to:
  - Wild-type pathogen  
  - Natural host  

> Do not assign disease names based on mutants or artificial systems.

---

## Summary

Accurate effector curation depends on:

- Effector-specific GO tagging  
- Precise genotype + metagenotype assignment  
- Conservative phenotype recording  
- Clear separation of:
  - pathogen phenotypes  
  - pathogen-host interaction phenotypes  

---

## Notes
- Align with [[Biocuration Standards]] and FAIR principles  
- Designed for integration with [[PHI-Canto]] workflows  
- Supports downstream AI/RAG applications
