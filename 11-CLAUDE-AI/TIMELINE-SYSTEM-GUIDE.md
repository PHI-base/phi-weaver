---
created: 2026-05-07
type: documentation
tags: [timeline, documentation, usage-guide]
---

# PHI-Canto Development Timeline System - Complete Guide

## 📋 **Overview**

The timeline system automatically tracks PHI-Canto system development milestones, filtering development work from content curation to provide clear progress tracking.

## 📁 **File Locations**

### **Timeline Files**
- **`11-CLAUDE-AI/DEVELOPMENT-TIMELINE.md`** - Main detailed timeline (auto-generated)
- **`content-links/dev-timeline-daily.md`** - Quick daily bullet points (manual)
- **`11-CLAUDE-AI/SESSION-LOGS/INDEX.md`** - Complete session index (includes content work)

### **Generator Scripts**
- **`11-CLAUDE-AI/update_timeline_incremental.py`** - Incremental updater (recommended)
- **`11-CLAUDE-AI/generate_dev_timeline.py`** - Full regeneration (when needed)

### **Documentation**
- **`CLAUDE.md`** - Main system documentation (includes timeline section)
- **`11-CLAUDE-AI/TIMELINE-SYSTEM-GUIDE.md`** - This comprehensive guide

## 🚀 **Quick Start Commands**

### **Check for Updates**
```bash
# See what new development sessions would be added
python3 11-CLAUDE-AI/update_timeline_incremental.py --check-only
```

### **Update Timeline**
```bash
# Add new sessions while preserving existing content (RECOMMENDED)
python3 11-CLAUDE-AI/update_timeline_incremental.py

# Full regeneration (overwrites manual edits)
python3 11-CLAUDE-AI/generate_dev_timeline.py
```

### **View Timeline**
```bash
# Detailed timeline
cat 11-CLAUDE-AI/DEVELOPMENT-TIMELINE.md

# Quick daily view
cat content-links/dev-timeline-daily.md

# View in editor
nano 11-CLAUDE-AI/DEVELOPMENT-TIMELINE.md
```

## 🔧 **How It Works**

### **Development Session Detection**
The system automatically identifies development vs content work using keyword analysis:

**Development Keywords** (included in timeline):
- `setup`, `infrastructure`, `automation`, `pipeline`, `system`
- `architecture`, `database`, `integration`, `migration`, `performance`
- `framework`, `tool`, `workflow`, `documentation`, `protocol`

**Content Keywords** (excluded from development timeline):
- `curation`, `effector`, `protein`, `literature`, `paper`, `pmid`

### **Session Categories**
- **Infrastructure**: Setup, initialization, foundation work
- **Automation**: Pipeline, workflow, processing automation  
- **Architecture**: System design, migration, modular improvements
- **Analytics**: Database, tracking, progress metrics
- **Knowledge Management**: Documentation, protocols, training
- **System Enhancement**: General improvements

## 📊 **Timeline Formats**

### **Detailed Format** (`DEVELOPMENT-TIMELINE.md`)
```markdown
## 2026-05-07
### Architecture
- ✅ **External Storage Migration**: Infrastructure improvement: separated development vault from content storage, updated automation, improved performance.

## 2026-04-24  
### Architecture
- ✅ **System Architecture & Funding Strategy**: Added system architecture documentation, created implementation assessment, developed funding framework
```

### **Daily Format** (`dev-timeline-daily.md`)
```markdown
• **May 07** - Architecture Revolution: External storage migration, performance optimization
• **Apr 24** - Strategic Framework: System architecture documentation, funding strategy
• **Apr 22** - Automation Complete: Full workflow automation, database integration
```

## ⚙️ **Incremental vs Full Regeneration**

### **Incremental Update (Recommended)**
```bash
python3 11-CLAUDE-AI/update_timeline_incremental.py
```
**Pros**:
- ✅ Preserves manual edits and customizations
- ✅ Only adds new sessions
- ✅ Faster execution  
- ✅ Collaboration-friendly

**Use When**: Regular updates, preserving manual timeline edits

### **Full Regeneration**
```bash
python3 11-CLAUDE-AI/generate_dev_timeline.py
```
**Pros**:
- ✅ Ensures complete consistency
- ✅ Fixes any formatting issues
- ✅ Can reorganize entire timeline

**Cons**: 
- ❌ Overwrites manual edits
- ❌ Slower execution

**Use When**: Major reorganization needed, fixing corruption

## 🎯 **Usage Workflows**

### **Daily Development Workflow**
1. Complete development work
2. Create session log in `SESSION-LOGS/`
3. Update session index
4. Run: `python3 11-CLAUDE-AI/update_timeline_incremental.py`
5. Commit to git

### **Weekly Review Workflow**
1. Check timeline status: `--check-only`
2. Update timeline with any missed sessions
3. Review development velocity and milestones
4. Update daily timeline summary if needed

### **Project Review Workflow**
1. Generate fresh timeline: `python3 11-CLAUDE-AI/generate_dev_timeline.py`
2. Export timeline: `cp DEVELOPMENT-TIMELINE.md ~/Desktop/project-timeline-$(date +%Y%m%d).md`
3. Create presentation summary from daily timeline

## 📈 **Timeline Metrics Available**

### **Development Velocity**
- Sessions per week/month
- Major milestones completed
- Time between major achievements
- Category distribution (Infrastructure vs Automation vs Architecture)

### **Current Example Metrics**
```
Development Sessions: 12
Time Span: 26 days (Apr 11 - May 7)
Major Milestones: 5
Categories: Infrastructure (42%), Automation (33%), Architecture (17%)
```

## 🔧 **Customization Options**

### **Manual Timeline Editing**
You can safely edit `DEVELOPMENT-TIMELINE.md` to:
- Add custom notes to entries
- Reorganize sections  
- Include additional context
- Cross-reference related work

**The incremental updater preserves your changes!**

### **Category Customization**
Modify `update_timeline_incremental.py` to change categorization rules:
```python
def categorize_session(self, project, summary):
    text = f"{project} {summary}".lower()
    
    # Add your custom categories here
    if 'your-keyword' in text:
        return "Your Category"
```

### **Keyword Filtering**
Adjust development vs content detection by modifying:
```python
self.dev_keywords = ['setup', 'infrastructure', ...] # Add your terms
self.content_keywords = ['curation', 'effector', ...] # Add exclusions  
```

## 🚨 **Troubleshooting**

### **Timeline Not Updating**
```bash
# Check session logs exist
ls 11-CLAUDE-AI/SESSION-LOGS/*.md

# Check index file
cat 11-CLAUDE-AI/SESSION-LOGS/INDEX.md | tail -5

# Debug with check-only
python3 11-CLAUDE-AI/update_timeline_incremental.py --check-only
```

### **Missing Development Sessions**
1. Check if session is marked as development vs content in INDEX.md
2. Verify keywords match development criteria  
3. Check for typos in project names
4. Use `--check-only` to see what would be added

### **Timeline Corruption**
```bash
# Backup current timeline
cp 11-CLAUDE-AI/DEVELOPMENT-TIMELINE.md 11-CLAUDE-AI/DEVELOPMENT-TIMELINE-backup.md

# Full regeneration
python3 11-CLAUDE-AI/generate_dev_timeline.py

# Compare and merge manual edits if needed
diff 11-CLAUDE-AI/DEVELOPMENT-TIMELINE-backup.md 11-CLAUDE-AI/DEVELOPMENT-TIMELINE.md
```

## 📚 **Integration with Other Systems**

### **Session Logs**
- Timeline generated from `SESSION-LOGS/INDEX.md`
- Session logs provide detailed technical information
- Timeline provides high-level milestone tracking

### **Git Integration**
```bash
# Include in commit workflow
git add 11-CLAUDE-AI/DEVELOPMENT-TIMELINE.md
git commit -m "Update development timeline"
```

### **Obsidian Integration**
- Timeline files are regular markdown with proper frontmatter
- Link to session logs via `[[SESSION-LOGS/filename]]`
- Reference external content via `[[content-links/literature-index]]`

## 🔄 **Automation Setup**

### **Git Hook Integration**
Add to `.git/hooks/post-commit`:
```bash
#!/bin/bash
# Auto-update timeline after commits
python3 11-CLAUDE-AI/update_timeline_incremental.py
```

### **Alias Setup**
Add to `~/.bashrc`:
```bash
alias timeline-update="python3 /mnt/z/OBS-PHI-Canto/11-CLAUDE-AI/update_timeline_incremental.py"
alias timeline-check="python3 /mnt/z/OBS-PHI-Canto/11-CLAUDE-AI/update_timeline_incremental.py --check-only"
alias timeline-view="cat /mnt/z/OBS-PHI-Canto/11-CLAUDE-AI/DEVELOPMENT-TIMELINE.md"
```

## 📋 **Best Practices**

### **Development Sessions**
1. **Clear project naming** in session logs for accurate categorization
2. **Descriptive summaries** that highlight development aspects
3. **Consistent terminology** for better keyword matching
4. **Regular updates** rather than batch processing

### **Timeline Maintenance**
1. **Use incremental updates** for daily work
2. **Review weekly** for accuracy and completeness
3. **Manual edits** for important context or corrections
4. **Backup before** major reorganizations

### **Collaboration**
1. **Document customizations** in this guide
2. **Coordinate timeline edits** to avoid conflicts
3. **Use check-only mode** before making changes
4. **Commit timeline updates** with descriptive messages

---

## 📞 **Support and Documentation**

- **Main Documentation**: `CLAUDE.md` (timeline section)
- **Session Logs**: `11-CLAUDE-AI/SESSION-LOGS/INDEX.md`
- **Usage Examples**: This guide and script help text
- **Source Code**: Generator scripts with inline documentation

*Timeline System Guide - Last Updated: 2026-05-07*