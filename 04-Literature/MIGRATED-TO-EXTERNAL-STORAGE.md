---
created: 2026-05-07
type: migration-notice
tags: [migration, external-storage]
---

# Literature Content Migrated

**Migration Date**: 2026-05-07  
**Status**: ✅ Complete

## Where to Find Literature Content

All literature content previously stored in this directory has been moved to external storage for better organization and performance.

### New Location
**External Storage**: `/mnt/z/PHI-Canto-Literature/completed/`

### Access from Development Vault
- **Complete index**: [[content-links/literature-index]]
- **Quick access**: [[content-links/quick-access]]

### Recently Migrated Content
- Chen 2026 MBOA-CWI curation (exceptional quality)
- Li 2025 Pt31812 effector (ready for PHI-Canto submission)
- He 2018 NLR1 analysis
- Chen 2020 FgCdc25 study
- Reference materials (Tretiakova 2022, Yoder 1986)

## Benefits of Migration

1. **Focused Development Vault**: Lighter, faster operations
2. **Scalable Literature Storage**: Can grow without affecting vault performance
3. **Clear Separation**: System development vs content distinction
4. **Tool-Content Independence**: Same curation tools can work with different literature collections

## Using Automation with External Storage

All automation tools have been updated:
```bash
# Process papers (now outputs to external storage)
python3 11-CLAUDE-AI/curation_pipeline.py process-pdf filename.pdf

# Complete curations (moves to external completed)
python3 11-CLAUDE-AI/curation_pipeline.py complete-paper filename.pdf "summary"
```

---

For complete literature access, see: [[content-links/literature-index]]