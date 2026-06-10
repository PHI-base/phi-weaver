---
created: 2026-04-18
type: index
tags: [wiki, index, status/active]
---

# 📚 PHI-Canto Wiki

Wiki-style organization for PHI-Canto curation workflow and documentation.

## 📊 Registries (Auto-Generated)

### [[07-Wiki/Article-Registry|📄 Article Registry Dashboard]]
- Complete overview of literature curation pipeline
- Status tracking with visual indicators  
- Curator assignments and workload
- Recent activity summary
- **Auto-updates**: Run `python3 generate_article_registry.py`

### [[07-Wiki/Protein-Registry|🧬 Protein Registry]]
- Central catalog of all tracked proteins
- Species organization and coverage
- UniProt ID tracking
- Functional classifications

## 📋 Templates

### [[07-Wiki/Templates/Article-Template|📄 Article Template]]
- Standardized literature curation format
- Complete metadata capture
- Evidence documentation structure
- Quality assurance checklist

### Protein Template (TBD)
- Protein characterization format
- Functional annotation standards
- Cross-reference documentation

## 📖 Protocols

### [[07-Wiki/Curation-Protocols/Standard-Process|📋 Standard Curation Process]]
- Complete 6-phase workflow
- Quality standards and best practices
- Evidence classification system
- Tools and resources guide

### Quality Assurance (TBD)
- Review procedures
- Validation checklists
- Error correction protocols

## 🚀 Quick Start

### Daily Workflow
1. **Check Pipeline**: [[07-Wiki/Article-Registry|Article Registry]]
2. **Select Article**: Priority-based assignment
3. **Use Template**: [[07-Wiki/Templates/Article-Template|Article Template]]
4. **Follow Protocol**: [[07-Wiki/Curation-Protocols/Standard-Process|Standard Process]]
5. **Log Session**: `python3 session_logger.py quick "Project" "Summary" proteins interactions hours`
6. **Update Registry**: Auto-generated on session completion

### Database Integration

The wiki connects seamlessly with your SQLite database:
- **Registries**: Auto-generated from current database state
- **Templates**: Include database integration commands  
- **Session Logging**: Automatically updates wiki content
- **Cross-References**: Links between wiki pages and database records

## 🔄 Auto-Generation

### Article Registry
```bash
python3 generate_article_registry.py
```
- Updates article pipeline overview
- Refreshes status indicators
- Includes recent activity
- Links to individual article notes

### Session Integration
The session logger automatically:
- Updates database with new curation work
- Creates properly formatted session logs
- Maintains links between database and wiki
- Preserves audit trail with timestamps

## 📁 Wiki Structure

```
07-Wiki/
├── Article-Registry.md         # Auto-generated article dashboard
├── Protein-Registry.md         # Protein catalog (manual/auto)
├── README.md                   # This index page
├── Templates/
│   ├── Article-Template.md     # Literature curation template
│   └── Protein-Template.md     # Protein documentation template
└── Curation-Protocols/
    ├── Standard-Process.md     # Main curation workflow
    ├── Quality-Assurance.md    # Review and validation
    └── Evidence-Standards.md   # Experimental evidence criteria
```

## 🔗 Integration with Obsidian Vault

The wiki leverages your existing vault structure:

### Links to Existing Content
- **Literature**: `04-Literature/` → Individual article notes
- **Projects**: `02-Projects/` → Research project documentation  
- **Session Logs**: `11-CLAUDE-AI/SESSION-LOGS/` → Historical activity
- **Database**: `11-CLAUDE-AI/mysql-setup/` → Tools and scripts

### Obsidian Features Used
- **Templates**: Standardized note creation
- **Links**: [[WikiLinks]] for cross-references
- **Tags**: Organization and filtering
- **Graph View**: Relationship visualization
- **Search**: Full-text content discovery

## 🎯 Benefits

### Wiki Advantages
✅ **Centralized overview** of all curation activities  
✅ **Standardized processes** via templates and protocols  
✅ **Auto-generated dashboards** from database  
✅ **Cross-reference discovery** through linking  
✅ **Process documentation** for consistency and onboarding  

### Integration Benefits  
✅ **No duplicate work** - wiki pulls from existing database  
✅ **Seamless workflow** - fits within established session logging  
✅ **Audit trail preserved** - all changes tracked with timestamps  
✅ **Flexible structure** - combines wiki organization with database power  

## 🛠️ Maintenance

### Automatic Updates
- Article registry regenerated with `generate_article_registry.py`
- Session logs automatically link to wiki pages
- Database changes reflected in wiki dashboards

### Manual Updates
- Protocol refinements based on curation experience
- Template improvements for better standardization
- Additional registry generators as needed

---

**This wiki provides structured organization while leveraging your existing hybrid database + Obsidian system. It adds wiki benefits without fragmenting your successful workflow.**

## 📞 Navigation

- 🏠 **Vault Root**: [[README|PHI-Canto Vault]]
- 📊 **Database Tools**: `11-CLAUDE-AI/mysql-setup/`
- 📝 **Session Logs**: `11-CLAUDE-AI/SESSION-LOGS/`
- 🧬 **Projects**: [[02-Projects/]]
- 📚 **Literature**: [[04-Literature/]]