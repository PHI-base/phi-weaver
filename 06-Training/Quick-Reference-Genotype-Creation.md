---
created: 2026-04-21
type: quick-reference
tags: [genotype, alleles, reference-card]
project: PHI-Canto
---

# Genotype Creation - Quick Reference

## 🧬 Single Allele Creation

### Quick Buttons
| Button | Use For | Result |
|--------|---------|--------|
| **Deletion** | Gene knockouts | Auto-creates deletion genotype |
| **Other genotype...** | All other types | Opens allele creation form |

### Allele Form Fields
1. **Allele name**: Optional (e.g., tri5-1, avr1Δ)
2. **Allele type**: deletion, substitution, insertion, wild type, other
3. **Description**: Details for partial deletion/substitution  
4. **Expression**: null, decreased, wild type, increased, not assayed

## 🔄 Complementation Workflow

### Step-by-Step
1. **Create deletion**: Click gene → "Other genotype..."
   - Type: `deletion`
   - Expression: `null`
2. **Create complement**: Same gene → "Other genotype..."  
   - Type: `wild type` or `other`
   - Expression: `wild type product level`
   - Description: `complementing construct on [plasmid]`
3. **Combine**: ☑️ Tick both alleles → "Combine selected genotypes"

### Result
Multi-allele genotype: *gene*Δ + *gene*<sup>+</sup> (complemented)

## 🎯 Multi-Allele Genotypes

### Process
1. **Create all singles first** → Each appears in table
2. **Select multiple** → ☑️ Tick 2+ alleles  
3. **Combine** → Click "Combine selected genotypes"
4. **Result** → New genotype in bottom table

## ⚙️ Genotype Management

### Mouse-over Actions
| Action | Purpose |
|--------|---------|
| **Start phenotype annotation** | Begin curation workflow |
| **View annotations** | See existing data |
| **Edit details** | Modify genotype info |
| **Copy and edit** | Create variant genotype |
| **Add/edit background** | Specify background mutations |
| **Delete** | Remove (if no annotations) |

## 🏷️ Expression Levels

| Level | When to Use |
|-------|-------------|
| **null** | Deletions, knockouts |
| **decreased** | Knockdown, partial function |
| **wild type product level** | Normal expression |
| **increased** | Overexpression constructs |
| **not assayed** | Expression not measured |

## 📋 Common Scenarios

### Knockout Study
```
Gene → "Deletion" button → Auto-creates geneΔ
```

### Overexpression  
```
Gene → "Other genotype..." → Type: wild type
Expression: increased → Description: overexpression construct
```

### Point Mutation
```
Gene → "Other genotype..." → Type: substitution  
Description: A123T → Expression: decreased/wild type/increased
```

### Double Mutant
```
Create gene1Δ → Create gene2Δ → ☑️ Both → Combine
```

## 🚨 Important Rules

### Wild-Type Usage
- **Don't annotate** normal expression wild-type with phenotypes
- **Use in metagenotypes** for experimental controls only
- **Include in multi-allele** only if over/under-expressed

### Background Mutations
- **Separate from strain name** → Use "Background" field  
- **Auto-combines** in multi-allele genotypes
- **Edit** via "Add/edit background" option

## 🎪 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| **Can't delete genotype** | Remove annotations first |
| **Wrong allele type** | Use "Edit details" |
| **Missing background** | Use "Add/edit background" |
| **Need variant** | Use "Copy and edit" |

## 📍 Navigation

**From curation summary**: "Pathogen/Host genotype management"  
**Between genotypes**: Table view with action buttons
**Back to summary**: Breadcrumb navigation

---
*Master genotype creation for efficient PHI-Canto curation workflows*