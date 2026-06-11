---
created: 2026-05-07
type: index
tags: [content-links, literature, external-storage]
---

# Literature Index - External Storage References

**External Storage Location**: `/mnt/z/PHI-Canto-Literature/`

This index provides references to literature content stored in external storage, keeping the main vault focused on system development.

## Directory Structure

```
PHI-Canto-Literature/
├── completed/          # Finished curations (moved from 04-Literature/)
├── active/            # Work in progress (moved from 00-Inbox/To-curate/)  
├── media/             # Images and figures (moved from 03-Media/)
├── archive/           # Historical materials
└── work-queue/        # Queued for future curation
```

## Completed Curations

### High-Priority PHI-Canto Ready


#### Li 2025 - Pt31812 Effector  
- **Location**: `../PHI-Canto-Literature/completed/Li-2025-Pt31812-PHI-Canto-Curation.md`
- **PMID**: 40756215
- **Status**: ✅ Ready for submission (UniProtKB: A0A180GLK7)
- **Quality**: Classic avirulence-resistance gene interaction

### Research Papers

#### He 2018 - NLR1 Analysis
- **Location**: `../PHI-Canto-Literature/completed/He-2018-NLR1.pdf`
- **Curation**: `../PHI-Canto-Literature/completed/He-2018-NLR1-Curation-Notes.md`
- **Status**: ✅ Completed

#### Chen 2020 - Environmental Microbiology
- **Location**: `../PHI-Canto-Literature/completed/Chen-2020-EnvironMicrobiol-32537857_converted.md`
- **Curation**: `../PHI-Canto-Literature/completed/Chen-2020-FgCdc25-PHI-Canto-Curation.md`
- **Status**: ✅ F. graminearum Cdc25 analysis

### Reference Materials

#### Standards and Nomenclature
- **Tretiakova 2022**: `../PHI-Canto-Literature/completed/Tretiakova-2022.pdf`
- **Yoder 1986**: `../PHI-Canto-Literature/completed/Yoder-1986-GeneticNomenclaturePlantPathogenicFungi.pdf`

## Active Work Queue

### Currently Processing

#### Rust Effector Studies
- **Location**: `../PHI-Canto-Literature/active/40756215-Le-2025-PuccTritiEffecotr_converted.md`
- **Status**: ⚠️ Conversion complete, awaiting curation



## Media Collections

### Organized by Paper
- **Chen 2020**: `../PHI-Canto-Literature/media/Chen-2020-EnvironMicrobiol-32537857/`
- **Tretiakova 2022**: `../PHI-Canto-Literature/media/Tretiakova-2022/`
- **General images**: `../PHI-Canto-Literature/media/` (various PNG files)

## Access Instructions

### From Development Vault
```bash
# View completed literature
ls ../PHI-Canto-Literature/completed/

# Check active work
ls ../PHI-Canto-Literature/active/

# Browse media files
ls ../PHI-Canto-Literature/media/
```

### Using Automation Tools
The curation pipeline has been updated to use external storage:
```bash
# Process new paper (now outputs to external storage)
python3 11-CLAUDE-AI/curation_pipeline.py process-pdf filename.pdf

# Complete curation (moves to external completed folder)
python3 11-CLAUDE-AI/curation_pipeline.py complete-paper filename.pdf "Summary"
```

## Migration Status

**Completed**: 2026-05-07

### ✅ Migrated Content
- All completed literature (04-Literature/ → completed/)
- Active work items (00-Inbox/To-curate/ → active/)
- Media collections (03-Media/ → media/)
- Automation scripts updated for external storage

### 🔧 Updated Tools
- `curation_pipeline.py` - Now uses external storage paths
- File organization workflows updated
- Reference system created in development vault

### 📁 Vault Structure (Post-Migration)
```
phi-weaver/ (Development Repo)
├── 11-CLAUDE-AI/          # Tools, automation, sessions
├── 05-Protocols/          # Curation protocols
├── 06-Training/           # Training materials
├── 07-Standards/          # Reference standards
├── 08-Wiki/               # Protocols, registries, templates
├── skills/                # Reusable agent task workflows
├── content-links/         # External storage references
├── AGENTS.md              # Source of truth for agent instructions
├── CLAUDE.md              # Bridge → AGENTS.md
└── docs/                  # Storage config, demo, setup notes

PHI-Canto-Literature/ (External Storage)
├── completed/            # All finished curations
├── active/              # Current work items
├── media/               # Images and figures
├── archive/             # Historical content
└── work-queue/          # Future work
```

## Benefits Achieved

1. **Focused Development Vault**: Lean, tool-focused, faster operations
2. **Scalable Content Storage**: Can grow without affecting vault performance
3. **Clear Separation**: System development vs content storage
4. **Flexible Deployment**: Curation system can work with different content collections
5. **Better Collaboration**: Teams can share tools while maintaining separate content

## Next Steps

1. Test automation workflows with new structure
2. Update any remaining scripts that reference old paths
3. Consider archiving older content to reduce active storage
4. Set up content backup strategy for external storage

---

*External storage migration completed: 2026-05-07*  
*Development vault remains focused on PHI-Canto system development*