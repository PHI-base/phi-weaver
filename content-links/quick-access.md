---
created: 2026-05-07
type: reference
tags: [quick-access, external-storage]
---

# Quick Access to External Literature

Fast references for accessing external storage content during development.

## 🔧 Development Commands

```bash
# View all completed curations
ls ../PHI-Canto-Literature/completed/

# Check current work queue  
ls ../PHI-Canto-Literature/active/

# Process new paper
python3 11-CLAUDE-AI/curation_pipeline.py process-pdf filename.pdf

# Complete curation
python3 11-CLAUDE-AI/curation_pipeline.py complete-paper filename.pdf "Summary"
```

## 📚 Recent Papers (Quick Links)

### High-Priority PHI-Canto Ready
- **Li 2025 Pt31812**: `../PHI-Canto-Literature/completed/Li-2025-Pt31812-PHI-Canto-Curation.md`

### In Progress
- **Active queue**: `../PHI-Canto-Literature/active/`

## 🖼️ Media Access

```bash
# All media files
ls ../PHI-Canto-Literature/media/

# Specific paper media
ls ../PHI-Canto-Literature/media/Chen-2020*/
```

## 📁 Directory Navigation

```bash
# Quick navigation aliases (add to .bashrc)
alias philit="cd /mnt/z/PHI-Canto-Literature"
alias phicomp="cd /mnt/z/PHI-Canto-Literature/completed"  
alias phiact="cd /mnt/z/PHI-Canto-Literature/active"
alias phimedia="cd /mnt/z/PHI-Canto-Literature/media"

# Usage
phicomp  # Jump to completed literature
phiact   # Jump to active work
```

## 🚀 Workflow Examples

### Start New Curation
```bash
# Copy PDF to active work
cp ~/Downloads/paper.pdf ../PHI-Canto-Literature/active/

# Process it  
python3 11-CLAUDE-AI/curation_pipeline.py process-pdf paper.pdf
```

### Complete Curation
```bash
# Move to completed with summary
python3 11-CLAUDE-AI/curation_pipeline.py complete-paper paper.pdf "Curation summary here"

# Check result
ls ../PHI-Canto-Literature/completed/ | grep paper
```

---
*Quick access guide for external storage system*