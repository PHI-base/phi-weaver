---
created: 2026-05-07
type: migration-notice
tags: [migration, external-storage, active-work]
---

# Active Work Migrated

**Migration Date**: 2026-05-07  
**Status**: ✅ Complete

## Where to Find Active Curation Work

All active curation work previously in this directory has been moved to external storage.

### New Location
**External Storage**: `/mnt/z/PHI-Canto-Literature/active/`

### Current Active Work
```bash
# View work queue
ls ../PHI-Canto-Literature/active/

# Recently migrated items:
# - Le 2025 Puccinia triticina effector (converted, awaiting curation)
# - Miltenburg 2022 proximity biotinylation study  
# - Zhang 2024 molecular plant pathology
# - Chen 2026 annotation records
```

## Updated Workflow

The curation pipeline now processes papers directly in external storage:

```bash
# Add new paper to work queue
cp ~/Downloads/paper.pdf ../PHI-Canto-Literature/active/

# Process it
python3 11-CLAUDE-AI/curation_pipeline.py process-pdf paper.pdf

# When complete, moves to completed/
python3 11-CLAUDE-AI/curation_pipeline.py complete-paper paper.pdf "Summary"
```

## Benefits for Active Work

1. **Scalable Queue**: Work queue can grow without slowing vault operations
2. **Better Organization**: Clear separation between tools and content
3. **Shared Access**: Multiple curators can work with same content collection
4. **Performance**: Faster vault operations for tool development

---

For complete workflow guide, see: [[content-links/quick-access]]