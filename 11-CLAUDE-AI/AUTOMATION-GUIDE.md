# PHI-Canto Automation Guide

> ℹ️ Project rules and conventions live in **[AGENTS.md](../AGENTS.md)** (the source of
> truth). This guide is the deep operational reference for the automation tools.

Complete automation for your curation workflow - from PDF to finished annotation.

## 🚀 Quick Start

### New Paper (Full Automation)
```bash
# Run from the repo root - automatically copy, convert, and set up new PDF
python3 11-CLAUDE-AI/curation_pipeline.py auto-process ~/Downloads/paper.pdf
```

### Process Existing PDF
```bash
# If PDF is already in 00-Inbox/To-curate/
python3 curation_pipeline.py process-pdf paper.pdf
```

### Complete Curation
```bash
# When finished - moves to Literature folder with logging
python3 curation_pipeline.py complete-paper paper.pdf "Added 3 effectors, 5 interactions"
```

## 🛠️ Available Tools

### 1. Master Pipeline (`curation_pipeline.py`)
**Complete workflow automation** - handles the entire process:

| Command | Purpose | Example |
|---------|---------|---------|
| `auto-process` | Full automation: copy + convert + setup | `python3 curation_pipeline.py auto-process paper.pdf` |
| `new-paper` | Copy PDF to vault and process | `python3 curation_pipeline.py new-paper paper.pdf` |
| `process-pdf` | Convert existing PDF in To-curate | `python3 curation_pipeline.py process-pdf paper.pdf` |
| `complete-paper` | Move finished work to Literature | `python3 curation_pipeline.py complete-paper paper.pdf "summary"` |

### 2. Session Management (`workflow_helper.py`)
**Track your daily work** with integrated database logging:

```bash
cd 11-CLAUDE-AI/db

# Start session
python3 workflow_helper.py start-session "Fusarium effectors"

# End session with metrics
python3 workflow_helper.py end-session "Fusarium effectors" "Added FgTPP1 analysis" 3 5 2.0
#                                        project             summary            proteins interactions hours

# Check progress
python3 workflow_helper.py status
python3 workflow_helper.py gaps
```

### 3. PDF Conversion (`pdf-convert.py`)
**Professional PDF to Markdown** with academic formatting:

```bash
# Run from wherever the PDF is (the pipeline normally handles this for you)
python3 11-CLAUDE-AI/pdf-convert-skill/pdf-convert.py paper.pdf

# Creates:
# - paper_converted.md (full markdown)
# - paper_converted_report.json (quality report)
# - media/ folder (extracted images)
```

### 4. Database Integration (`daily_curation.py`)
**Track progress and analytics**:

```bash
cd 11-CLAUDE-AI/db

# Log session manually
python3 daily_curation.py log 3 5 2.0  # proteins, interactions, hours

# Show progress
python3 daily_curation.py progress
python3 daily_curation.py gaps
python3 daily_curation.py help
```

### 5. File Organization (`obsidian_reorganise.py`)
**Auto-organize files** with WikiLink updates:

```bash
cd 11-CLAUDE-AI

# Preview changes (always run first!)
python3 obsidian_reorganise.py --config reorganise-config-OBS-PHI-Canto.yaml

# Execute moves (Obsidian must be open)
python3 obsidian_reorganise.py --config reorganise-config-OBS-PHI-Canto.yaml --execute
```

## 📋 Complete Workflows

### Workflow 1: Brand New Paper

```bash
# Step 1: Full automation
cd 11-CLAUDE-AI
python3 curation_pipeline.py auto-process ~/Downloads/new-paper.pdf

# Step 2: Start session tracking
cd db
python3 workflow_helper.py start-session "New Paper Analysis"

# Step 3: Do your curation work in Obsidian/PHI-Canto
# [Manual work here]

# Step 4: End session with metrics
python3 workflow_helper.py end-session "New Paper Analysis" "Completed annotation" 4 8 3.5

# Step 5: Complete and archive
cd ..
python3 curation_pipeline.py complete-paper new-paper.pdf "Added 4 proteins, 8 interactions"
```

### Workflow 2: Process Existing PDF

```bash
# If PDF is already in 00-Inbox/To-curate/
cd 11-CLAUDE-AI

# Step 1: Process existing PDF
python3 curation_pipeline.py process-pdf existing-paper.pdf

# Step 2: Continue with session tracking as above...
```

### Workflow 3: Daily Progress Check

```bash
cd 11-CLAUDE-AI/db

# Check what you've accomplished
python3 daily_curation.py progress

# Find gaps needing attention
python3 daily_curation.py gaps

# Show recent work with timestamps
python3 show_recent.py
```

## 🔧 Configuration

### Database Setup
Located in `11-CLAUDE-AI/db/`:
- `phi_canto_tracking.db` - SQLite database (no server needed)
- Tracks articles, proteins, sessions, progress over time
- Automatic timestamp tracking (YYYY-MM-DD HH:MM:SS)

### File Organization Rules
Configure in `reorganise-config-OBS-PHI-Canto.yaml`:
- Automatic file placement based on content patterns
- Updates WikiLinks when moving files
- Keeps vault organized without manual effort

### PDF Conversion Settings
Configure in `pdf-convert-skill/pdf-convert-config.json`:
- Academic formatting options
- Caption extraction settings
- Image classification rules

## ⚡ Quick Commands Reference

| Task | Command |
|------|---------|
| **New PDF** | `python3 curation_pipeline.py auto-process paper.pdf` |
| **Start work** | `python3 workflow_helper.py start-session "Project"` |
| **End work** | `python3 workflow_helper.py end-session "Project" "Summary" 3 5 2.0` |
| **Check progress** | `python3 daily_curation.py progress` |
| **Complete paper** | `python3 curation_pipeline.py complete-paper paper.pdf "Summary"` |
| **Organize files** | `python3 obsidian_reorganise.py --config config.yaml --execute` |

## 🎯 Benefits

### Time Savings
- ✅ **Instant PDF processing**: No manual conversion or image extraction
- ✅ **Automatic file organization**: Files go to the right places automatically
- ✅ **Integrated session logging**: One command updates markdown AND database
- ✅ **Progress analytics**: See your productivity trends over time

### Quality Assurance
- ✅ **Professional PDF conversion**: Academic formatting with caption extraction
- ✅ **Consistent file structure**: Automated organization prevents messy folders
- ✅ **Database tracking**: Never lose track of which papers are done
- ✅ **Session history**: Complete audit trail of all work

### Integration
- ✅ **Obsidian native**: All outputs are Obsidian-compatible markdown
- ✅ **Git integration**: All changes can be committed to local version control
- ✅ **PHI-Canto ready**: Processed papers are ready for immediate annotation
- ✅ **Vault coherent**: Maintains existing folder structure and linking

## 🚨 Important Notes

### Prerequisites
1. **Python dependencies**: `PyMuPDF` for PDF processing
2. **Obsidian open**: File organization requires Obsidian to be open on this vault
3. **WSL environment**: Optimized for WSL2 filesystem permissions

### File Placement Strategy
Literature content lives in **external storage** (outside the repo); only the tools live
in the repo. See `docs/STORAGE-CONFIGURATION.md` (override with `PHI_LITERATURE_ROOT`).
```
../PHI-Canto-Literature/active/     ← PDFs being processed (external storage)
../PHI-Canto-Literature/completed/  ← Completed curations (external storage)
../PHI-Canto-Literature/media/      ← Extracted images
11-CLAUDE-AI/                       ← All automation scripts (in the repo)
```

### Database Integration
- **Automatic**: Session logging integrates with existing SQLite database
- **Optional**: Scripts work with or without database (graceful fallback)
- **Persistent**: All progress tracked with precise timestamps

This automation system transforms your curation workflow from manual file juggling to streamlined, tracked, professional processing. Each tool works independently or as part of the complete pipeline.