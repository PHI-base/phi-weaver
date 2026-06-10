# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Session Startup Protocol

**REQUIRED**: At the start of every Claude Code session, you MUST read:
`11-CLAUDE-AI/SESSION-LOGS/INDEX.md`

This provides context from previous sessions and ensures continuity across interactions.

## Claude Code Startup Requirements

**WSL Environment Setup**: When using Claude Code in WSL (Windows Subsystem for Linux):

```bash
claude --dangerously-skip-permissions
```

This flag is required due to WSL filesystem permission handling when accessing Windows paths from Linux subsystem. It's safe in this specific context and documented by Anthropic for WSL environments.

## Permissions and Capabilities

**AUTHORIZED**: For PHI-Canto curation and research tasks, Claude is permitted to:

### Internet Search & Research
- ✅ **Search the web** for scientific literature, database information, and curation resources
- ✅ **Access public databases** (UniProt, PubMed, PHI-base, Gene Ontology, etc.)
- ✅ **Fetch research papers** and supplementary materials when publicly available
- ✅ **Look up gene/protein information** from authoritative sources

### Agent Network & Collaboration
- ✅ **Spawn specialized agents** for complex research tasks (literature review, database queries, comparative analysis)
- ✅ **Use agent networks** for parallel processing of large curation tasks
- ✅ **Delegate research** to appropriate subagents (Explore, Plan, etc.)
- ✅ **Coordinate multi-agent workflows** for comprehensive curation projects

### Use Cases
These capabilities should be used for:
- Literature searches for effector research
- Database queries for gene/protein information  
- Comparative genomics research
- Ontology term validation
- Quality assurance of curation data
- Training material development

**Rationale**: PHI-Canto curation requires access to distributed scientific resources and complex research workflows that benefit from specialized agent capabilities and real-time information access.

## Database Integration

**Hybrid Tracking System**: This vault includes SQLite database integration for structured tracking alongside flexible Obsidian notes.

### Database Location
- **Path**: `11-CLAUDE-AI/mysql-setup/phi_canto_tracking.db`
- **Type**: SQLite (portable, no server required)
- **Purpose**: Track curation progress, articles, proteins, species, and relationships

### Quick Usage
```bash
# From mysql-setup directory
python3 daily_curation.py progress           # Show recent work
python3 daily_curation.py log 3 5 2.0       # Log session (proteins, interactions, hours)
python3 daily_curation.py gaps              # Find data needing attention
python3 daily_curation.py help              # Show all commands
```

### What It Tracks
- **Articles**: Literature pipeline with status (queued → curated → published)
- **Proteins**: Gene IDs, functions, UniProt links, species relationships  
- **Sessions**: Daily curation work with metrics over time
- **Progress**: Analytics on productivity and gaps in curation data
- **Timestamps**: Precise date-time tracking (YYYY-MM-DD HH:MM:SS) for all activities

### Timestamp Tracking
All curation activities automatically capture precise timestamps:
```bash
python3 show_recent.py          # View recent work with full timestamps
python3 check_timestamps.py     # Detailed timestamp analysis
```
Full documentation: `11-CLAUDE-AI/mysql-setup/TIMESTAMPS.md`

### Integration with Obsidian
- Database records link to Obsidian notes via file paths
- Session logs automatically reference corresponding markdown files
- Literature and protein research connects to vault structure
- Maintains vault flexibility while adding queryable structure

### Automated Session Logging
**IMPORTANT**: Use the integrated session logger to ensure database consistency:
```bash
# Replaces manual session log creation - updates BOTH markdown AND database
python3 session_logger.py quick 'Project Name' 'Summary' [proteins] [interactions] [hours]

# Example:
python3 session_logger.py quick 'Fusarium effectors' 'Added FgTPP1 analysis' 3 5 2.0
```

**Benefits**:
- ✅ Automatic database updates with every session
- ✅ Consistent markdown formatting with database metadata
- ✅ Session logs index automatically updated
- ✅ No risk of forgetting to update database or markdown
- ✅ Tracks session ID for linking database records to notes

## Workflow Automation

**COMPLETE AUTOMATION AVAILABLE**: The vault includes a comprehensive automation system for the entire curation pipeline from PDF intake to completion.

### Master Automation Script
**Path**: `11-CLAUDE-AI/curation_pipeline.py`
**Purpose**: Complete workflow automation handling PDF processing, file organization, database tracking, and session logging. **Updated for external storage**.

### Quick Automation Commands
```bash
# Full automation: new PDF → converted → ready for curation (outputs to external storage)
python3 curation_pipeline.py auto-process ~/Downloads/paper.pdf

# Process existing PDF in active work folder
python3 curation_pipeline.py process-pdf filename.pdf

# Complete curation and move to completed literature folder
python3 curation_pipeline.py complete-paper filename.pdf "summary"

# Integrated session tracking
python3 workflow_helper.py start-session "Project Name"
python3 workflow_helper.py end-session "Project" "Summary" proteins interactions hours
```

### What Gets Automated
- ✅ **PDF placement**: Auto-copy to `../PHI-Canto-Literature/active/`
- ✅ **PDF conversion**: Professional markdown with image extraction
- ✅ **File organization**: Proper placement in external storage with references
- ✅ **Database tracking**: Articles, proteins, sessions logged automatically
- ✅ **Session management**: Integrated progress tracking with timestamps
- ✅ **Completion workflow**: Auto-move to `../PHI-Canto-Literature/completed/` when done

### External Storage Integration
All automation tools have been updated to work with the external literature storage:
- **Input**: `../PHI-Canto-Literature/active/` (work in progress)
- **Output**: `../PHI-Canto-Literature/completed/` (finished curations)  
- **Media**: `../PHI-Canto-Literature/media/` (images and figures)
- **References**: `content-links/` (access from development vault)

### Automation Components
1. **PDF Conversion** (`pdf-convert-skill/`) - Academic formatting with caption extraction
2. **Session Management** (`mysql-setup/workflow_helper.py`) - Database-integrated logging
3. **File Organization** (`obsidian_reorganise.py`) - Auto-placement with WikiLink updates
4. **Progress Analytics** (`mysql-setup/daily_curation.py`) - Productivity tracking
5. **Master Pipeline** (`curation_pipeline.py`) - Complete workflow orchestration

**Documentation**: See `11-CLAUDE-AI/AUTOMATION-GUIDE.md` for complete automation usage guide and examples.

## System Architecture

**PURPOSE**: Modular framework for inspection, improvement, and future development of the curation system.

### Architectural Overview

```
Literature → Document Processing → Entity Recognition → Ontology Mapping → 
Relationship Analysis → Validation & Learning → Database Output → PHI-base
```

### Module 1: Document Processing
**Purpose**: Convert research papers into structured, analyzable format
**Current Implementation**:
- `pdf-convert-skill/pdf-convert.py` - Core PDF to markdown conversion
- `convert-for-curation.py` - Wrapper with proper file organization
- `pdf-convert-config.json` - Configuration for different conversion types

**Inputs**: PDF files, conversion parameters
**Outputs**: Structured markdown, extracted images, conversion metadata
**Interfaces**: File system, 03-Media/ folder, 04-Literature/ folder
**Status**: ✅ Fully implemented, automated
**Improvement Opportunities**: OCR enhancement, table parsing, multi-column layouts

### Module 2: Entity Recognition
**Purpose**: Extract biological entities (genes, organisms, phenotypes, diseases) from literature
**Current Implementation**:
- Claude reasoning applied to converted papers
- Agent spawning for complex entity research
- Manual verification and validation

**Inputs**: Converted markdown papers, domain knowledge
**Outputs**: Gene lists, organism identifications, experimental method classifications
**Interfaces**: Claude analysis, UniProtKB lookup, agent system
**Status**: ✅ Implemented via Claude reasoning
**Improvement Opportunities**: Named entity recognition automation, confidence scoring

### Module 3: Ontology Mapping
**Purpose**: Map extracted entities to standardized ontology terms and database identifiers
**Current Implementation**:
- Manual UniProtKB accession lookup
- Claude-assisted PHIPO/GO term suggestion
- Quick reference cards for common terms
- Web search agents for gene identification

**Inputs**: Entity lists, ontology requirements, curator preferences
**Outputs**: UniProtKB IDs, PHIPO terms, GO annotations, evidence codes
**Interfaces**: UniProtKB API, ontology browsers, quick reference system
**Status**: 🔶 Partially automated (suggestions), requires manual validation
**Improvement Opportunities**: API integration, automated mapping, confidence scoring

### Module 4: Relationship Analysis
**Purpose**: Identify and model biological relationships between entities
**Current Implementation**:
- Claude reasoning for interaction detection
- Pattern recognition from experimental descriptions
- Cross-pathway analysis capabilities

**Inputs**: Entity data, experimental descriptions, literature context
**Outputs**: Protein interactions, genotype-phenotype associations, pathway connections
**Interfaces**: Curation workflow, knowledge integration
**Status**: ✅ Implemented via Claude analysis
**Improvement Opportunities**: Relationship confidence scoring, automated network analysis

### Module 5: Validation & Learning
**Purpose**: Quality assurance and system improvement through experience
**Current Implementation**:
- Memory system (`/home/urbanm/.claude/projects/-mnt-z-OBS-PHI-Canto/memory/`)
- Feedback integration (user corrections saved to memory)
- Session logging with progress tracking
- Quick reference cards based on curation patterns

**Inputs**: Curator feedback, annotation quality metrics, session data
**Outputs**: Improved suggestions, updated templates, quality scores
**Interfaces**: Memory system, session logs, database tracking
**Status**: 🔶 Basic implementation (memory), learning capabilities conceptual
**Improvement Opportunities**: Automated quality scoring, pattern recognition algorithms, adaptive templates

### Module 6: Database Output
**Purpose**: Generate PHI-base compatible curation records
**Current Implementation**:
- Structured markdown curation records
- Comprehensive annotation capture
- Quality control checklists

**Inputs**: Processed entities, relationships, validation status
**Outputs**: PHI-Canto ready annotation records
**Interfaces**: 04-Literature/ folder, manual PHI-Canto submission
**Status**: ✅ Structured output, manual submission
**Improvement Opportunities**: Direct PHI-Canto API integration, automated submission

### Cross-Module Interfaces

**Data Flow**:
```
PDFs → [Module 1] → Structured Text → [Module 2] → Entities → 
[Module 3] → Annotated Entities → [Module 4] → Relationships → 
[Module 5] → Validated Annotations → [Module 6] → Curation Records
```

**Shared Resources**:
- **Database**: SQLite tracking system (`11-CLAUDE-AI/mysql-setup/phi_canto_tracking.db`)
- **Memory**: Learning and feedback system
- **Session Management**: Progress tracking and logging
- **File Organization**: Standardized vault structure

### Modularization Roadmap

**Phase 1 - Inspection (Current)**:
- Document existing implementations
- Identify module boundaries and interfaces
- Map data flow and dependencies

**Phase 2 - Interface Standardization**:
- Define APIs between modules
- Create standardized data formats
- Implement module testing frameworks

**Phase 3 - Component Isolation**:
- Extract modules into separate, testable components
- Implement module-specific configuration
- Create module deployment system

**Phase 4 - Enhancement**:
- Add missing automated capabilities
- Implement learning algorithms
- Integrate external APIs and services

### Development Guidelines

**Module Independence**: Each module should be:
- Testable in isolation
- Configurable via parameters
- Replaceable without affecting other modules

**Data Standards**: All inter-module communication should use:
- Defined schemas for entity data
- Standardized confidence scores
- Consistent error handling

**Quality Metrics**: Each module should provide:
- Processing time statistics
- Accuracy/confidence measures
- Error rates and failure modes

**Documentation Requirements**: Each module requires:
- Input/output specifications
- Configuration parameters
- Performance characteristics
- Integration guidelines

## Repository Overview

This is an Obsidian knowledge management vault dedicated to **PHI-Canto system development** — tools, protocols, and automation for the PHI-base (Pathogen-Host Interactions) database curation workflow. The vault focuses on developing the curation system, while actual literature content is stored externally for better organization and performance.

## Directory Structure

### Development Vault (OBS-PHI-Canto)
```
05-Protocols/      Standard operating procedures and experimental methods
06-Training/       Curator onboarding and educational materials  
07-Standards/      Nomenclature, ontologies, and reference standards
08-QA/            Quality assurance procedures and validation
11-CLAUDE-AI/      Claude Code session logs and automation tools
  ├─ SESSION-LOGS/ Interaction history and session records
  ├─ mysql-setup/  Database integration and session management
  ├─ pdf-convert-skill/ Professional PDF to markdown conversion
  ├─ curation_pipeline.py Master automation script (updated for external storage)
  ├─ AUTOMATION-GUIDE.md Complete automation documentation
  └─ obsidian_reorganise.py File organization with WikiLink updates
content-links/     References to external literature storage
  ├─ literature-index.md  Complete index of external content
  └─ quick-access.md     Fast navigation guide
_Templates/        Note templates
CLAUDE.md         This system documentation
```

### External Literature Storage (PHI-Canto-Literature)
```
../PHI-Canto-Literature/
├── completed/     Finished curations (formerly 04-Literature/)
├── active/        Work in progress (formerly 00-Inbox/To-curate/)
├── media/         Images, attachments, and media files (formerly 03-Media/)  
├── archive/       Historical materials
└── work-queue/    Queued for future curation
```

### Benefits of External Storage
- **Focused Development**: Vault stays lean and tool-focused
- **Scalable Content**: Literature can grow without affecting vault performance  
- **Clear Separation**: System development vs content storage distinction
- **Faster Operations**: Reduced vault size improves Obsidian performance
- **Flexible Deployment**: Curation system can work with different content collections

### Workflow-Specific Folders

The enhanced structure includes dedicated folders for PHI-Canto curation workflow stages:

- **05-Protocols/**: Standard operating procedures, experimental methods (complementation, transformation, annotation protocols)
- **06-Training/**: Curator onboarding materials, tutorials, educational resources (houses YouTube tutorials, training guides)
- **07-Standards/**: Genetic nomenclature, Gene Ontology terms, controlled vocabularies, reference standards
- **08-QA/**: Quality assurance procedures, validation checklists, error tracking workflows

This organization aligns with the PHI-Canto curation pipeline: Literature → Protocols → Training → Active Curation → Quality Assurance.

## Key Configuration Files

- **CLAUDE.md**: This file — guidance for Claude Code
- **11-CLAUDE-AI/obsidian_reorganise.py**: Generic vault reorganiser (uses Obsidian CLI)
- **11-CLAUDE-AI/reorganise-config-OBS-PHI-Canto.yaml**: Reorganiser rules for this vault
- **11-CLAUDE-AI/SESSION-LOGS/INDEX.md**: Index of all Claude Code sessions

## Git Usage Guidelines

**IMPORTANT: This repository is shared on GitHub at `PHI-base/phi-weaver`. Commits may be pushed to the remote.**

### Git Policy
- ✅ **Make local commits**: Use git for tracking changes and maintaining version history
- ✅ **Push to remote**: Push commits to `origin` (`PHI-base/phi-weaver`) when the user asks
- ⚠️ **Review before pushing**: This repo may contain unpublished annotations and internal
  workflow material — confirm with the user before pushing, and avoid committing sensitive
  or personal data

### Rationale
This repository is the collaborative PHI-Weaver curation framework hosted under the
PHI-base GitHub organization, intended for sharing tools and protocols with colleagues.

### Commands to Use
- `git add .` and `git commit -m "message"` ✅ (local tracking)
- `git status`, `git log`, `git diff` ✅ (local operations)
- `git push origin main` ✅ (push when requested)
- **Note**: On the `z:` Windows mount, `git config`/`git remote set-url` fail with a
  `config.lock` chmod error — edit `.git/config` directly instead.

## Obsidian CLI Integration

The Obsidian CLI enables file moves that auto-update WikiLinks.

**CLI path**: `D:\ObsidianProgram\Obsidian.com`

**Calling from WSL**:
```bash
/mnt/c/Windows/System32/cmd.exe /c 'D:\ObsidianProgram\Obsidian.com <command>'
```

**IMPORTANT**: This vault must be the **active vault open in Obsidian** for CLI commands
to work. Verify with:
```bash
/mnt/c/Windows/System32/cmd.exe /c 'D:\ObsidianProgram\Obsidian.com vault list'
```

**Reorganiser usage**:
```bash
# Dry-run preview (always run first)
python 11-CLAUDE-AI/obsidian_reorganise.py --config 11-CLAUDE-AI/reorganise-config-OBS-PHI-Canto.yaml

# Execute moves (Obsidian must be open on this vault)
python 11-CLAUDE-AI/obsidian_reorganise.py --config 11-CLAUDE-AI/reorganise-config-OBS-PHI-Canto.yaml --execute
```

**NOTE**: File organization is now automated through the curation pipeline. Manual reorganization is typically only needed for vault-wide maintenance.

## Session Logs

### Location and Purpose
**Path**: `11-CLAUDE-AI/SESSION-LOGS/`
**Index**: `11-CLAUDE-AI/SESSION-LOGS/INDEX.md` — read this at session start

Session logs document Claude Code interactions for continuity across sessions.

## Development Timeline System

### Purpose and Location
**Primary Timeline**: `11-CLAUDE-AI/DEVELOPMENT-TIMELINE.md`
**Quick Reference**: `content-links/dev-timeline-daily.md`
**Generator Scripts**: `11-CLAUDE-AI/generate_dev_timeline.py`, `11-CLAUDE-AI/update_timeline_incremental.py`

### Usage Commands

#### Incremental Updates (Recommended)
```bash
# Check what would be added (dry run)
python3 11-CLAUDE-AI/update_timeline_incremental.py --check-only

# Add only new development sessions to existing timeline
python3 11-CLAUDE-AI/update_timeline_incremental.py
```

#### Full Regeneration (When Needed)
```bash
# Regenerate entire timeline from session logs
python3 11-CLAUDE-AI/generate_dev_timeline.py

# Generate bullet-point format
python3 11-CLAUDE-AI/generate_dev_timeline.py --format bullet
```

### Timeline Features
- **Development Focus**: Filters system development from content curation work
- **Incremental Updates**: Preserves manual edits while adding new sessions
- **Categorization**: Infrastructure, Automation, Architecture, Analytics, Knowledge Management
- **Timestamps**: Tracks exact timing of development milestones
- **Auto-filtering**: Distinguishes development vs content work using keyword analysis

### When to Update
- After major development sessions (infrastructure, tools, automation)
- Weekly for development velocity tracking
- Before project reviews or status meetings
- When manual timeline edits need to be preserved

### File Naming Convention
**Format**: `YYYY-MM-DD-[project-slug].md`
Append `-2`, `-3` for multiple sessions on the same day.

### What to Include
- Session objectives and tasks completed
- File modifications and git commits made
- Key insights or decisions
- Recommendations for future sessions

### Session Workflow
1. **ALWAYS start by reading `INDEX.md`** to understand prior context
2. Create new session log file in `11-CLAUDE-AI/SESSION-LOGS/` with date prefix
3. Include YAML frontmatter (see template below)
4. Update `INDEX.md` with a new row
5. Commit to local git at session end

## Documentation Standards

### File Organisation
- Save new notes to appropriate folders (not vault root)
- Use kebab-case or Title-Case for filenames
- Date-prefixed files must use `YYYY-MM-DD` format

### Obsidian Syntax
- Always use `[[WikiLinks]]` for internal links
- Use `![[filename]]` for embedding images
- Use standard Obsidian callout syntax for callout blocks

### Frontmatter Template
```yaml
---
created: YYYY-MM-DD
type: note
tags: [status/wip]
project: PHI-Canto
---
```

## PHI-Canto Curation Workflow

This vault supports the complete PHI-Canto curation pipeline for pathogen-host interaction data:

### Core Curation Process
1. **Literature Discovery** → Find publications via PubMed ID
2. **Gene Identification** → UniProtKB accession lookup and validation
3. **Organism/Strain Management** → Pathogen and host strain specification
4. **Genotype Creation** → Single-allele and multi-locus genotype construction
5. **Metagenotype Assembly** → Pathogen-host interaction combinations
6. **Annotation** → Phenotype, disease, and interaction curation
7. **Quality Assurance** → Validation and submission

### Key Ontologies and Standards
- **PHIPO** (Pathogen-Host Interaction Phenotype Ontology): Phenotype terms for single-species and interaction phenotypes
- **PHIDO** (PHI-base Disease Ontology): Infectious disease terminology
- **Gene Ontology (GO)**: Molecular function, biological process, cellular component
- **BRENDA Tissue Ontology**: Host tissue type specification
- **UniProtKB**: Canonical gene/protein identifiers

### Annotation Types Supported
#### Gene Annotations
- GO molecular function, biological process, cellular component
- Protein modifications
- Physical interactions (with directionality support)
- RNA and protein level data

#### Genotype Annotations  
- Pathogen phenotypes (growth, morphology, resistance)
- Host phenotypes (defense responses, susceptibility)

#### Metagenotype Annotations
- Pathogen-host interaction phenotypes
- Gene-for-gene interactions
- Disease names with tissue specificity
- Infective ability and interaction outcomes

### Experimental Evidence Integration
- Evidence codes for all annotation types
- Experimental conditions specification
- Figure/table number referencing
- Annotation extensions for specificity

## Research Domain Context

This vault focuses on:
- **PHI-Canto**: Community curation platform for pathogen-host interaction data
- **PHI-base**: The Pathogen-Host Interactions database  
- **Curation workflows**: Annotation protocols, evidence codes, gene ontology terms
- **Curator training**: Onboarding materials for new curators (MC-canto-training project)
- **Literature curation**: Extracting interaction data from published papers

## File Types

### Searchable by Claude Code
- **Markdown (.md)**: Primary vault content
- **Canvas (.canvas)**: Visual layouts (JSON-based)
- **YAML / JSON / CSV**: Config and data files
- **Python (.py)**: Scripts in `11-CLAUDE-AI/`

### Not searchable (binary)
- Office documents (.docx, .pptx, .xlsx)
- Images (.png, .jpg) — reference by filename only

## Data Sensitivity

This vault may contain:
- Draft curation records not yet published to PHI-base
- Internal workflow and training documentation
- Curator correspondence and collaboration details

Exercise appropriate care and keep all version control strictly local.
