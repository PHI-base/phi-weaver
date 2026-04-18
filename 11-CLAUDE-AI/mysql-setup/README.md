# PHI-Canto MySQL Integration

Simple hybrid approach combining Obsidian vault with MySQL database for structured tracking.

## How It Works

### The Hybrid System

```
Obsidian Vault                    MySQL Database
├─ Literature notes         ←→    Articles table (status, curator)
├─ Protein research         ←→    Proteins table (gene IDs, function)
├─ Session logs            ←→    Curation sessions (progress tracking)
├─ Project documentation   ←→    Species table (hosts, pathogens)
└─ Protocols & training          Relationships & history
```

**Philosophy**: Obsidian for flexible research and documentation, MySQL for structured tracking and analytics.

## Setup Steps

### 1. Install MySQL
```bash
# Ubuntu/WSL
sudo apt update
sudo apt install mysql-server

# Start MySQL service
sudo service mysql start

# Secure installation (optional)
sudo mysql_secure_installation
```

### 2. Create Database
```bash
# Login to MySQL
mysql -u root -p

# Create user (optional)
CREATE USER 'phi_curator'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON phi_canto_tracking.* TO 'phi_curator'@'localhost';
```

### 3. Import Schema
```bash
# From the mysql-setup directory
mysql -u root -p < 01-database-schema.sql
mysql -u root -p < 02-sample-data.sql
```

### 4. Test Python Integration
```bash
# Install requirements
pip install mysql-connector-python

# Run demo
python phi_canto_db.py
```

## Timestamp Tracking

All curation activities are tracked with **precise timestamps** in format `YYYY-MM-DD HH:MM:SS`.

### Automatic Timestamp Fields
- **Session Logging**: `created_date` when work was logged
- **Articles**: `created_date` when added, `updated_date` when modified
- **Proteins**: `created_date` when documented, `updated_date` when information changes
- **Relationships**: `created_date` when protein-article connections identified

### View Full Timestamps
```bash
python3 show_recent.py      # Recent activity with timestamps
python3 check_timestamps.py # Detailed timestamp analysis
```

See `TIMESTAMPS.md` for complete timestamp documentation and SQL queries.

## Database Structure

### Core Tables

**Species** - Track hosts and pathogens
```sql
species (id, name, type, taxonomy_id, common_name, notes)
```

**Articles** - Literature being curated
```sql
articles (id, pmid, title, status, curator, obsidian_note_path)
```

**Proteins** - Genes/proteins being studied
```sql
proteins (id, gene_id, uniprot_id, species_id, name, protein_type)
```

**Curation Sessions** - Track daily work
```sql
curation_sessions (id, session_date, curator, proteins_curated, interactions_added)
```

### Key Features

- **Precise Timestamps**: Full date-time tracking (YYYY-MM-DD HH:MM:SS) for all curation activities
- **Links to Obsidian**: `obsidian_note_path` fields connect database records to your markdown notes
- **Progress tracking**: Automated views show curation progress over time with exact timing
- **Relationships**: Track which proteins appear in which articles with timestamps
- **Status management**: Article workflow from queued → curated → published with update tracking
- **Audit Trail**: Complete chronological history of all changes and additions

## Daily Workflow

### 1. Research in Obsidian
- Take literature notes
- Document protein functions
- Write session logs

### 2. Update Database
```python
from phi_canto_db import PHICantoDB

db = PHICantoDB()
db.connect()

# Log today's session
db.log_session(
    session_date="2026-04-18",
    curator="your_name",
    proteins_curated=3,
    interactions_added=5,
    notes="Worked on Fusarium effectors"
)

# Add new article
db.add_article(
    pmid="12345678",
    title="New effector discovery paper",
    status="in_progress",
    curator="your_name",
    obsidian_path="04-Literature/new-effector-2024.md"
)

db.disconnect()
```

### 3. Check Progress
```python
# See what you've accomplished
db.get_curation_progress(days=30)
db.get_article_status()
db.find_effector_proteins("Fusarium")
```

## Example Queries

### Find Articles Needing Curation
```sql
SELECT title, pmid, pub_year
FROM articles
WHERE status = 'queued'
ORDER BY priority DESC, pub_year DESC;
```

### Track Your Progress This Month
```sql
SELECT
    DATE(session_date) as date,
    proteins_curated,
    interactions_added,
    session_duration_hours
FROM curation_sessions
WHERE curator = 'your_name'
  AND session_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
ORDER BY session_date;
```

### Find Proteins Without UniProt IDs
```sql
SELECT gene_id, name, species.name as species
FROM proteins
JOIN species ON proteins.species_id = species.id
WHERE uniprot_id IS NULL OR uniprot_id = '';
```

## Integration Examples

### Sync New Session Log
When you create a new session log in Obsidian, update the database:

```python
# After writing: 11-CLAUDE-AI/SESSION-LOGS/2026-04-18-fusarium-work.md
db.log_session(
    session_date="2026-04-18",
    curator="martin.urban",
    session_duration_hours=2.5,
    proteins_curated=2,
    interactions_added=4,
    obsidian_session_log="11-CLAUDE-AI/SESSION-LOGS/2026-04-18-fusarium-work.md"
)
```

### Link Protein Research
When you research a protein, add it to the database:

```python
# After creating: 02-Projects/Fusarium-effectors/proteins/FgNEW1.md
fusarium_id = 1  # Fusarium graminearum species ID
db.add_protein(
    gene_id="FGSG_12345",
    species_id=fusarium_id,
    name="Novel effector protein FgNEW1",
    gene_name="FgNEW1",
    function_summary="Newly discovered effector with unknown function",
    protein_type="effector",
    obsidian_path="02-Projects/Fusarium-effectors/proteins/FgNEW1.md"
)
```

## Benefits of This Approach

1. **Keep doing what works**: Continue using Obsidian for flexible notes and research
2. **Add structure**: Database provides queryable structure and relationships
3. **Track progress**: See your curation work over time with metrics
4. **Find gaps**: Identify proteins without UniProt IDs, articles without curators
5. **Generate reports**: Query database for progress reports and statistics
6. **Maintain links**: Database points back to your Obsidian notes
7. **Simple maintenance**: Basic SQL queries you can understand and modify

## Next Steps

1. Set up MySQL and import the schema
2. Try the Python script with sample data
3. Start logging your daily curation sessions
4. Add articles and proteins as you work on them
5. Use queries to track your progress and find what needs attention

The system grows with your work - start simple and add complexity as needed!