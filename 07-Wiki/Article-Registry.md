---
created: 2026-04-18
type: registry
tags: [status/active, registry]
auto_generated: true
last_updated: 2026-04-18 14:42:58
---

# 📚 Article Registry Dashboard

*Auto-generated from database on 2026-04-18 at 14:42:58*

## 📊 Pipeline Overview

**Total Articles**: 3

- ⚪ **Queued**: 1 articles (33.3%)
- 🟡 **In_Progress**: 1 articles (33.3%)
- 🟢 **Curated**: 1 articles (33.3%)
- 🔵 **Reviewed**: 0 articles (0.0%)
- 🟣 **Published**: 0 articles (0.0%)

## 👥 Curator Assignments

- **martin.urban**: 2 total (1 active)

## 📈 Recent Activity (Last 7 Days)

- **7** curation sessions
- **13** proteins curated
- **21** interactions added

## 📄 Article Pipeline

| Status | Title | PMID | Curator | Proteins | Updated |
|--------|-------|------|---------|----------|----------|
| 🟡 | [[04-Literature/FgSCP-characterization-2024|Characterization of FgSCP effector protein in whea...]] | [38456789](https://pubmed.ncbi.nlm.nih.gov/38456789) | martin.urban | FgTPP1, FgSCP | 2026-04-18 |
| ⚪ | [[04-Literature/Fg62-transcription-targets|Fg62 effector targets host transcription factors]] | [37123456](https://pubmed.ncbi.nlm.nih.gov/37123456) | Unassigned | Fg62 | 2026-04-18 |
| 🟢 | [[04-Literature/FgTPP1-effector-2024|FgTPP1 effector manipulates host immunity in Fusar...]] | [38234567](https://pubmed.ncbi.nlm.nih.gov/38234567) | martin.urban | FgTPP1 | 2026-04-18 |

## 🕒 Recent Curation Activity

- **2026-04-18 13:42:58** | martin.urban | 1 proteins, 1 interactions
  *Quick session update: Testing auto-wiki updates...*
- **2026-04-18 13:08:49** | martin.urban | 1 proteins, 3 interactions
  *Quick session update: Updated FgNls1 protein characterization...*
- **2026-04-18 13:06:59** | martin.urban | 1 proteins, 2 interactions
  *Quick session update: Tested integrated session logging system...*
- **2026-04-18 13:01:53** | martin.urban | 2 proteins, 3 interactions
  *Testing database integration...*
- **2026-04-18 13:00:58** | martin.urban | 3 proteins, 5 interactions
  *Literature review and initial protein characterization for FgTPP1...*

## 🚀 Quick Actions

### Curation Workflow
1. [[07-Wiki/Templates/Article-Template|Use Article Template]] for new literature
2. [[07-Wiki/Curation-Protocols/Standard-Process|Follow Curation Protocol]]
3. Use session logger: `python3 session_logger.py quick 'Project' 'Summary' proteins interactions hours`

### Database Commands
```bash
# Show progress
python3 daily_curation.py progress

# Find gaps
python3 daily_curation.py gaps

# Update this registry
python3 generate_article_registry.py
```

## 📋 Status Legend

| Symbol | Status | Description |
|--------|--------|-------------|
| ⚪ | Queued | Added to pipeline, awaiting curation |
| 🟡 | In Progress | Currently being curated |
| 🟢 | Curated | Curation completed, ready for review |
| 🔵 | Reviewed | Quality checked, ready for publication |
| 🟣 | Published | Data published to PHI-base |

---

*This registry is auto-generated from the SQLite database.*  
*Regenerate with: `python3 generate_article_registry.py`*  
*Last updated: 2026-04-18 14:42:58*
