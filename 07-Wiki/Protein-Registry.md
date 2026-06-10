---
created: 2026-04-18
type: registry
tags: [status/active, registry, proteins]
---

# 🧬 Protein Registry

Central registry of all proteins tracked in the PHI-Canto database.

*Note: This is a static template. For auto-generated content, use:*
```bash
python3 generate_protein_registry.py
```

## Quick Stats
- **Total Proteins**: [Auto-generated]
- **Species Coverage**: [Auto-generated]  
- **With UniProt IDs**: [Auto-generated]
- **Effector Proteins**: [Auto-generated]

## By Species
### Fusarium graminearum
- [[02-Projects/Fusarium-effectors/proteins/FgTPP1|FgTPP1]] (FGSG_11164)
- [[02-Projects/Fusarium-effectors/proteins/FgSCP|FgSCP]] (FGSG_08454)
- [[02-Projects/Fusarium-effectors/proteins/Fg62|Fg62]] (FGSG_01831)
- More...

## Quick Actions
- [[07-Wiki/Templates/Protein-Template|New Protein Template]]
- [[07-Wiki/Article-Registry|Article Registry]]
- [[07-Wiki/Curation-Protocols/Standard-Process|Curation Protocol]]

## Database Commands
```bash
python3 daily_curation.py gaps    # Find proteins missing UniProt IDs
python3 show_recent.py           # Recent protein activity
```

*For full auto-generated registry, implement protein registry generator.*