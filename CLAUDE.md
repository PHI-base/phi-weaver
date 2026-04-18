# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Session Startup Protocol

**REQUIRED**: At the start of every Claude Code session, you MUST read:
`11-CLAUDE-AI/SESSION-LOGS/INDEX.md`

This provides context from previous sessions and ensures continuity across interactions.

## Claude Code Startup Requirements

**WSL Environment**: When starting Claude Code in this WSL environment, use the permissions bypass flag:

```bash
claude --dangerously-skip-permissions
```

This flag is required due to WSL permission handling when accessing Windows filesystem paths from Linux subsystem.

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

## Repository Overview

This is an Obsidian knowledge management vault dedicated to **PHI-Canto** — the curation interface and workflow for the PHI-base (Pathogen-Host Interactions) database. The vault contains curation notes, training materials, annotation protocols, literature references, and project documentation related to PHI-base community curation.

## Directory Structure

```
00-Inbox/          Temporary holding area for new notes before processing
  └─ To-curate/    Files queued for PHI-Canto annotation
01-Notes/          General working notes and reference materials
02-Projects/       Active curation projects and campaigns
  └─ MC-canto-training/   Molecular Connections curation training
  └─ Fusarium-effectors/  Research project on Fusarium effectors
03-Media/          Images, attachments, and media files
04-Literature/     Literature references for curation evidence
05-Protocols/      Standard operating procedures and experimental methods
06-Training/       Curator onboarding and educational materials
07-Standards/      Nomenclature, ontologies, and reference standards
08-QA/            Quality assurance procedures and validation
_Templates/        Note templates
11-CLAUDE-AI/      Claude Code session logs and tools
  └─ SESSION-LOGS/ Interaction history and session records
SystemSculpt/      AI tool integration (empty directory structure)
  └─ .systemsculpt/ Configuration and cache files (if SystemSculpt is used)
```

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

**IMPORTANT: This repository operates with LOCAL-ONLY version control.**

### Git Policy
- ✅ **Make local commits**: Use git for tracking changes and maintaining version history locally
- ❌ **NEVER push to remote**: Do not push commits to GitHub, GitLab, or any remote repository
- ❌ **NEVER set up remotes**: Avoid configuring remote repositories for this vault

### Rationale
This vault contains PHI-base curation work including unpublished annotations,
curator training materials, and internal workflow documentation.

### Commands to Use
- `git add .` and `git commit -m "message"` ✅ (local tracking)
- `git status`, `git log`, `git diff` ✅ (local operations)
- `git push`, `git remote add` ❌ (avoid remote operations)

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

## Session Logs

### Location and Purpose
**Path**: `11-CLAUDE-AI/SESSION-LOGS/`
**Index**: `11-CLAUDE-AI/SESSION-LOGS/INDEX.md` — read this at session start

Session logs document Claude Code interactions for continuity across sessions.

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
