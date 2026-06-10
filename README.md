# PHI-Curation-Framework

🧬 **AI-Powered Pathogen-Host Interaction Curation System**

A comprehensive framework for automating [PHI-base](http://phi-base.org/) and [PHI-Canto](https://curation.phi-base.org/) curation workflows using Large Language Models and intelligent automation tools.

> 📂 **New colleague? Start with [STORAGE-CONFIGURATION.md](STORAGE-CONFIGURATION.md)** — it explains
> where the pipeline reads/writes literature files and how to point it at your own location
> (via the `PHI_LITERATURE_ROOT` environment variable).
>
> 🚀 **Want to try it with zero local setup?** Follow **[DEMO-CODESPACES.md](DEMO-CODESPACES.md)**
> to curate an open-access article entirely in a GitHub Codespace.

## 🎯 **Overview**

The PHI-Curation-Framework streamlines the complex process of curating pathogen-host interaction data from scientific literature. It integrates Claude Code, automated PDF processing, database tracking, and quality assurance tools to accelerate high-quality curation for the PHI-base database.

### **Key Features**

✅ **Complete Automation Pipeline** - End-to-end workflow from PDF intake to curation completion  
✅ **LLM-Powered Analysis** - Claude integration for intelligent entity extraction and annotation  
✅ **Professional PDF Processing** - Academic formatting with figure/table caption extraction  
✅ **Database Integration** - SQLite tracking for progress analytics and session management  
✅ **Timeline System** - Development tracking with incremental updates  
✅ **External Storage Architecture** - Scalable content management with performance optimization  
✅ **Quality Assurance Tools** - Validation workflows and error detection  
✅ **Training Materials** - Comprehensive onboarding and quick reference guides  

## 📁 **Repository Structure**

```
PHI-Curation-Framework/
├── 00-Inbox/                    # Incoming tasks and project coordination
├── 05-Protocols/               # Standard operating procedures
├── 06-Training/                # Curator onboarding and quick references
├── 07-Standards/               # Genetic nomenclature and ontology guides
├── 08-QA/                      # Quality assurance procedures
├── 11-CLAUDE-AI/               # Automation tools and session management
│   ├── curation_pipeline.py   # Master automation script
│   ├── pdf-convert-skill/     # PDF processing system
│   ├── mysql-setup/           # Database integration
│   ├── SESSION-LOGS/          # Development history and context
│   └── *.py                   # Timeline tracking and automation tools
├── content-links/              # References to external literature storage
├── CLAUDE.md                   # System configuration and guidelines
└── README.md                   # This file
```

## 🚀 **Quick Start**

### **Prerequisites**

- **Python 3.8+** with pip
- **Claude Code CLI** ([installation guide](https://claude.ai/code))
- **Git** for version control
- **WSL/Linux environment** recommended for full functionality

### **Installation**

1. **Clone the repository:**
```bash
git clone https://github.com/martin2urban/PHI-Curation-Framework.git
cd PHI-Curation-Framework
```

2. **Install Python dependencies:**
```bash
pip install -r requirements.txt  # If available
# Or manually install: pandas, sqlite3, requests, pypdf2
```

3. **Set up Claude Code:**
```bash
# WSL users may need permission bypass
claude --dangerously-skip-permissions
```

4. **Initialize the system:**
```bash
# Set up database and external storage
python3 11-CLAUDE-AI/mysql-setup/phi_canto_sqlite.py --init
```

### **First Curation Session**

```bash
# Process a new PDF through the complete pipeline
python3 11-CLAUDE-AI/curation_pipeline.py auto-process ~/Downloads/paper.pdf

# Start an interactive curation session
python3 11-CLAUDE-AI/mysql-setup/session_logger.py quick "Project Name" "Summary"

# Generate development timeline
python3 11-CLAUDE-AI/update_timeline_incremental.py
```

## 📚 **Core Workflows**

### **1. PDF Processing**
```bash
# Convert PDF with academic formatting
python3 11-CLAUDE-AI/pdf-convert-skill/pdf-convert.py paper.pdf

# Process for curation with file organization
python3 11-CLAUDE-AI/convert-for-curation.py paper.pdf
```

### **2. Session Management**
```bash
# Quick session logging
python3 11-CLAUDE-AI/mysql-setup/session_logger.py quick 'Fusarium effectors' 'Added FgTPP1 analysis' 3 5 2.0

# View recent progress
python3 11-CLAUDE-AI/mysql-setup/daily_curation.py progress

# Check productivity analytics
python3 11-CLAUDE-AI/mysql-setup/daily_curation.py gaps
```

### **3. Timeline Tracking**
```bash
# Update development timeline (preserves manual edits)
python3 11-CLAUDE-AI/update_timeline_incremental.py

# Full regeneration when needed
python3 11-CLAUDE-AI/generate_dev_timeline.py
```

## 🏗️ **System Architecture**

### **Modular Framework Design**

```
Literature → Document Processing → Entity Recognition → Ontology Mapping → 
Relationship Analysis → Validation & Learning → Database Output → PHI-base
```

**Module 1: Document Processing**
- PDF to markdown conversion with figure extraction
- Caption and table extraction for academic papers
- Quality validation and formatting

**Module 2: Entity Recognition** 
- LLM-powered gene/protein identification
- Organism and strain classification
- Experimental method detection

**Module 3: Ontology Mapping**
- UniProtKB accession lookup and validation
- PHIPO/GO term suggestion and mapping
- Quality assurance with confidence scoring

**Module 4: Relationship Analysis**
- Protein interaction detection
- Genotype-phenotype association mapping
- Cross-pathway analysis capabilities

**Module 5: Validation & Learning**
- Memory system for curator feedback
- Progress tracking and analytics
- Quality metrics and improvement suggestions

**Module 6: Database Output**
- PHI-Canto ready annotation records
- Structured data export capabilities
- Integration with external storage systems

### **External Storage Integration**

The framework uses external storage for scalable content management:

- **Development Vault** (this repository): Tools, documentation, automation
- **Literature Storage** (external): Active work, completed curations, media files
- **Content Links**: References connecting development tools to literature content

## 🛠️ **Configuration**

### **Claude Code Setup**

Edit `CLAUDE.md` for system-specific configuration:

- **Session startup protocol**: Automatic context loading
- **Database integration settings**: SQLite configuration
- **Permission and capabilities**: Research access authorization
- **External storage paths**: Literature storage configuration

### **Environment Variables**

```bash
export CURATION_ROOT="/path/to/curation/workspace"
export LITERATURE_STORAGE="/path/to/external/literature"
export PHI_CANTO_DB="/path/to/phi_canto_tracking.db"
```

### **Database Configuration**

The system uses SQLite for tracking:
- **Articles**: Literature pipeline status (queued → curated → published)
- **Proteins**: Gene IDs, functions, UniProtKB links, species relationships  
- **Sessions**: Daily curation work with metrics and timestamps
- **Progress**: Analytics on productivity and data completeness

## 📖 **Documentation**

### **User Guides**
- **[Complete System Guide](CLAUDE.md)** - Comprehensive framework documentation
- **[Automation Guide](11-CLAUDE-AI/AUTOMATION-GUIDE.md)** - Workflow automation usage
- **[Timeline System Guide](11-CLAUDE-AI/TIMELINE-SYSTEM-GUIDE.md)** - Development tracking

### **Training Materials**
- **[PHI-Canto Curation Protocol](05-Protocols/PHI-Canto-Complete-Curation-Protocol.md)**
- **[Curator Onboarding](06-Training/PHI-Canto-Curator-Onboarding.md)**
- **Quick References**: Genotype creation, phenotype annotation, UniProtKB lookup, ontology terms

### **Technical Documentation**
- **[PDF Conversion System](11-CLAUDE-AI/pdf-convert-skill/PDF-CONVERT-SKILL.md)**
- **[Database Schema](11-CLAUDE-AI/mysql-setup/database_schema.sql)**
- **[Session Logs](11-CLAUDE-AI/SESSION-LOGS/INDEX.md)** - Development history and context

## 🤝 **Contributing**

We welcome contributions to improve the PHI-Curation-Framework!

### **Getting Started**
1. **Read the session logs** in `11-CLAUDE-AI/SESSION-LOGS/INDEX.md` for context
2. **Check the development timeline** for current priorities
3. **Review the architecture documentation** in `CLAUDE.md`

### **Development Workflow**
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-improvement`)
3. Use the session logging system to track your work
4. Update the timeline with development progress
5. Commit your changes (`git commit -m 'Add amazing improvement'`)
6. Push to your branch (`git push origin feature/amazing-improvement`)
7. Open a Pull Request

### **Areas for Contribution**
- 🔬 **Module Enhancement**: Improve entity recognition, ontology mapping
- 🤖 **LLM Integration**: Enhanced agent workflows, memory systems
- 📊 **Analytics**: Advanced progress tracking, quality metrics
- 🔗 **API Integration**: Direct PHI-Canto submission, external database connections
- 📝 **Documentation**: User guides, video tutorials, training materials
- 🧪 **Testing**: Automated testing frameworks, validation systems

## 📞 **Support**

### **Getting Help**
- **Issues**: Report bugs or request features via [GitHub Issues](https://github.com/martin2urban/PHI-Curation-Framework/issues)
- **Discussions**: Join community discussions for usage questions
- **Documentation**: Check `CLAUDE.md` and guides in `11-CLAUDE-AI/`

### **Contact**
- **Maintainer**: [martin2urban](https://github.com/martin2urban)
- **Research Domain**: Pathogen-Host Interactions, PHI-base, PHI-Canto
- **LLM Integration**: Claude Code, Agent Networks, Automation Workflows

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🏆 **Acknowledgments**

- **[PHI-base Team](http://phi-base.org/)** - Database infrastructure and curation standards
- **[PHI-Canto Platform](https://curation.phi-base.org/)** - Community curation system
- **[Claude AI/Anthropic](https://claude.ai/)** - LLM integration and automation capabilities
- **Research Community** - Domain expertise and collaborative curation efforts

## 📈 **Project Status**

**Current Version**: Development Framework  
**Development Timeline**: 26 days (Apr 11 - May 7, 2026)  
**Major Milestones**: 5 infrastructure additions  
**Session Logs**: 12 development sessions tracked  
**Automation Level**: Complete pipeline with external storage integration  

---

*Built for accelerating scientific curation through intelligent automation* 🚀