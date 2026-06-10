---
created: 2026-04-21
type: quick-reference
tags: [ontology, phipo, go, phido, reference-card]
project: PHI-Canto
---

# Common Ontology Terms - Quick Reference

## 🧪 PHIPO: Single-Species Phenotypes

### Pathogen Growth & Morphology
- `increased/decreased hyphal growth`
- `abnormal/normal hyphal morphology`
- `sexual spores absent/present`
- `asexual spores absent/present`
- `increased/decreased sporulation`

### Stress Response
- `resistance to [compound]`
- `sensitivity to [compound]`  
- `normal growth on [compound]`
- `temperature sensitivity`
- `osmotic stress sensitivity`

### Pathogenicity
- `loss of pathogenicity`
- `reduced virulence`
- `normal pathogenicity`
- `increased virulence`

### Host Defense
- `presence/absence of hypersensitive response`
- `increased/decreased defense gene expression`
- `cell death response present/absent`
- `presence/absence of effector-independent host hypersensitive response`

## ⚔️ PHIPO: Interaction Phenotypes

### Pathogenicity Changes
- `loss/reduction of pathogenicity`
- `increased pathogenicity`
- `normal pathogenicity`
- `abolished/reduced pathogen penetration into host`
- `absence/presence of pathogen growth on host surface`

### Host Response in Interaction
- `stunted host growth during pathogen colonization`
- `normal host growth during pathogen colonization`
- `host hypersensitive response present/absent`
- `increased/decreased host susceptibility to pathogen`

### Colonization Patterns  
- `reduced pathogen growth in host`
- `normal pathogen growth in host`
- `delayed pathogen infection process`
- `normal pathogen infection process`

## 🧬 Gene Ontology (GO) Terms

### Molecular Function (Required for Effectors)
- `effector-mediated modulation of host process by symbiont` (GO:0140418) ⭐
- `hydrolase activity` (GO:0016787)
- `peptidase activity` (GO:0008233)
- `carbohydrate binding` (GO:0030246)
- `protein binding` (GO:0005515)
- `protein kinase activity` (GO:0004672)

### Biological Process
- `pathogenesis` (GO:0009405)
- `adhesion to host` (GO:0044659)
- `entry into host` (GO:0030260)
- `defense response to fungus` (GO:0050832)
- `defense response to bacterium` (GO:0042742)
- `hypersensitive response` (GO:0009626)

### Cellular Component
- `extracellular region` (GO:0005576) - Secreted proteins
- `cell wall` (GO:0005618)
- `plasma membrane` (GO:0005886)
- `nucleus` (GO:0005634)
- `cytoplasm` (GO:0005737)

## 🦠 PHIDO: Disease Terms

### Fungal Diseases
- `anthracnose` - Dark lesions on tissues
- `blight` - Rapid tissue death and browning
- `canker` - Localized dead areas on woody stems
- `leaf spot` - Discrete spots on leaf tissue  
- `powdery mildew` - White fungal growth on surfaces
- `root rot` - Decay of root tissues
- `rust` - Pustules with rust-colored spores
- `wilt` - Loss of turgor, drooping

### Bacterial Diseases
- `bacterial blight` - Water-soaked lesions
- `bacterial canker` - Sunken areas on stems
- `bacterial leaf spot` - Water-soaked leaf spots
- `bacterial soft rot` - Tissue maceration
- `bacterial wilt` - Vascular blockage

## 🌿 BRENDA: Host Tissues

### Plant Organs
- `leaf` (BTO:0000713)
- `root` (BTO:0001199) 
- `stem` (BTO:0001225)
- `inflorescence` (BTO:0000628) - For ear blight, head scab
- `fruit` (BTO:0000645)
- `seed` (BTO:0001203)

### Tissue Types
- `vascular tissue` (BTO:0001493)
- `epidermis` (BTO:0000578)
- `mesophyll` (BTO:0000858)

## 🔬 Physical Interaction Evidence

### Asymmetric (Directional)
- `Affinity Capture-MS` - A captures B (mass spec)
- `Affinity Capture-Western` - A captures B (Western)
- `Two-hybrid` - A (DNA-binding) with B (activation)
- `Far Western` - A captures B (overlay)
- `Protein-peptide` - A binds peptide B

### Symmetric (Non-directional)
- `Co-purification` - A co-purifies with B
- `Co-fractionation` - A co-fractionates with B
- `Co-crystal Structure` - A co-crystallizes with B
- `PCA` - A interacts with B

## 🚀 Quick Search Tips

### PHIPO Strategy
1. **Start broad**: "growth" → "hyphal growth" → specific type
2. **Try synonyms**: "resistance" = "tolerance" = "sensitivity"
3. **Check definitions**: Names can be misleading

### GO Strategy  
1. **Function first**: What does the protein do?
2. **Process second**: What pathway is it in?
3. **Location last**: Where is it found?

### Disease Strategy
1. **Symptom-based**: "blight", "spot", "rot"
2. **Pathogen-based**: "bacterial", "fungal"
3. **Organ-specific**: "leaf blight", "root rot"

## ⭐ Essential Reminders

### For Effectors
**MUST include**: GO:0140418 effector process annotation

### For Diseases
**Requirements**: Wild-type interaction, natural host, disease present

### For Controls
**Best practice**: Create control metagenotype first, link via extensions

---
*Keep these terms handy for rapid annotation without constant ontology browsing*