---
created: 2026-04-21
type: quick-reference
tags: [phenotype, phipo, annotation, reference-card]
project: PHI-Canto
---

# Phenotype Annotation - Quick Reference

## 🎯 Annotation Types

| Type | Scope | Examples |
|------|-------|----------|
| **Single-species** | Pathogen OR host alone | decreased growth, resistance to compound |
| **Interaction** | Pathogen-host together | loss of pathogenicity, stunted host growth |
| **Gene-for-gene** | R-gene/effector recognition | compatible/incompatible interaction |

## 🔍 PHIPO Term Search

### Search Strategy
1. **Start broad**: "growth" → "hyphal growth" → "decreased hyphal growth"
2. **Read definitions**: Don't rely on term names alone
3. **Navigate hierarchy**: Browse child terms for specificity
4. **Request new**: "Suggest new child term" if needed

### Quick Term Categories
| Category | Examples |
|----------|----------|
| **Growth** | increased/decreased hyphal growth, sporulation |
| **Resistance** | resistance/sensitivity to [compound] |
| **Pathogenicity** | loss/reduction of pathogenicity |
| **Host response** | hypersensitive response present/absent |

## ⚡ Annotation Workflow

### Start Points
| From | Action | For |
|------|--------|-----|
| **Genotype table** | "Start phenotype annotation" | Single-species |
| **Gene list** | "Single allele phenotype" | Quick single gene |
| **Metagenotype table** | "Annotate interaction phenotype" | Interactions |

### Steps
1. **Select PHIPO term** → Read definition → Confirm
2. **Choose evidence code** → Match experimental method
3. **Add conditions** → Key experimental parameters only
4. **Add extensions** → Tissue, severity, controls
5. **Add figure/table** → Reference numbers
6. **Add comments** → Additional details
7. **Confirm** → Review and save

## 🧪 Common Evidence Codes

| Code | When to Use |
|------|-------------|
| **Direct assay** | Direct measurement/observation |
| **Inferred from mutant** | Phenotype from gene knockout/mutation |
| **Expression analysis** | RNA/protein level changes |
| **Microscopy** | Visual observation of structures |
| **Growth assay** | Plate/liquid culture measurements |

## 🌡️ Experimental Conditions

### Add When Relevant
- **Medium**: minimal vs rich, solid vs liquid
- **Temperature**: high/low vs standard
- **Chemicals**: salt stress, antifungals, nutrients
- **Delivery**: spray, infiltration, wound inoculation

### Don't Over-Specify
- Standard growth conditions
- Details already in PHIPO term
- Non-essential variations

## 🔧 Annotation Extensions

### Single-Species Extensions
| Extension | Purpose |
|-----------|---------|
| **Penetrance** | Proportion showing phenotype |
| **Severity** | Extent of phenotype expression |
| **Assayed feature** | Specific gene/protein measured |

### Interaction Extensions
| Extension | Purpose |
|-----------|---------|
| **Host tissue** | Infection location (BRENDA terms) |
| **Infective ability** | Pathogenicity/virulence change |
| **Control genotype** | Link to control metagenotype |
| **Outcome** | Disease present/absent |

## 🎪 Quick Actions

### Edit/Manage Annotations
| Action | Purpose |
|--------|---------|
| **Edit** | Modify existing annotation |
| **Transfer** | Copy to other genotypes |
| **Copy and edit** | Create variant annotation |
| **Delete** | Remove annotation |

### Multiple Conditions
- **Same phenotype, different conditions**: Use "Copy and edit"
- **Different tissues**: Separate annotations unless simultaneous
- **Controls vs experimental**: Link via "Compared to control" extension

## 🚨 Quality Checks

### Before Confirming
- [ ] PHIPO term definition matches observation
- [ ] Evidence code matches experimental method  
- [ ] Most specific term selected
- [ ] Figure/table reference included
- [ ] Control experiments linked (if applicable)

### Common Mistakes
- Using term names without reading definitions
- Wrong evidence code for method
- Missing tissue specifications for diseases
- Forgetting control genotype links

## 📍 Essential Links

### For Effectors (Required)
**Gene annotation**: Must include GO:0140418 "effector-mediated modulation of host process"

### For Controls
**Metagenotype**: Create control metagenotype first, then link via extensions

## 💡 Pro Tips

- **Read definitions first** - PHIPO names can be misleading
- **Start with controls** - Create control metagenotypes before experimental
- **Use hierarchy** - Navigate from broad to specific terms
- **Link everything** - Use extensions to connect related annotations
- **Document thoroughly** - Include figure references and comments

---
*Accurate phenotype annotation is the core of PHI-base data quality*