# PHI-Canto Tracking Database (SQLite)

A lightweight **SQLite** database that complements the Obsidian vault with structured,
queryable tracking of curation progress. **No server to install** — SQLite is built into
Python, and the database is a single portable file: `phi_canto_tracking.db`.

> This system is SQLite-only. (Earlier MySQL setup files have been removed.)

## How It Works

```
Obsidian Vault                    SQLite Database (phi_canto_tracking.db)
├─ Literature notes         ←→    articles table (status, curator)
├─ Protein research         ←→    proteins table (gene IDs, function)
├─ Session logs             ←→    curation_sessions (progress tracking)
├─ Project documentation    ←→    species table (hosts, pathogens)
└─ Protocols & training           protein_article_mentions (relationships)
```

**Philosophy**: Obsidian for flexible research and documentation, SQLite for structured
tracking and analytics.

## Setup

Nothing to install — `sqlite3` ships with Python. To create the database and load demo
data, run:

```bash
python3 phi_canto_sqlite.py    # creates phi_canto_tracking.db with sample data
```

The DB file is gitignored (it holds per-curator progress), so each clone/Codespace starts
fresh.

## Daily Workflow

Use the helper scripts in this folder:

```bash
# Log a session (updates both markdown and the database)
python3 session_logger.py quick 'Project Name' 'Summary' [proteins] [interactions] [hours]

# Progress analytics and gaps
python3 daily_curation.py progress    # recent work
python3 daily_curation.py gaps        # data needing attention
python3 daily_curation.py help        # all commands

# Start / end a tracked session
python3 workflow_helper.py start-session 'Project Name'
python3 workflow_helper.py end-session 'Project' 'Summary' proteins interactions hours

# Inspect timestamps
python3 show_recent.py                # recent activity with timestamps
python3 check_timestamps.py           # detailed timestamp analysis
```

See `TIMESTAMPS.md` for the timestamp model and example queries.

## Database Structure

```sql
species              (id, name, type, taxonomy_id, common_name, notes)
articles             (id, pmid, title, status, curator, obsidian_note_path)
proteins             (id, gene_id, uniprot_id, species_id, name, protein_type)
curation_sessions    (id, session_date, curator, proteins_curated, interactions_added)
protein_article_mentions (id, protein_id, article_id, experimental_evidence, curated)
```

Key features: precise `YYYY-MM-DD HH:MM:SS` timestamps on all activity, `obsidian_note_path`
fields linking records back to markdown notes, article workflow status
(queued → in_progress → curated → reviewed → published), and progress analytics over time.

## Example Queries (SQLite syntax)

```sql
-- Articles still needing curation
SELECT title, pmid, pub_year
FROM articles
WHERE status = 'queued'
ORDER BY priority DESC, pub_year DESC;

-- Your progress over the last 30 days
SELECT DATE(session_date) AS date, proteins_curated, interactions_added, session_duration_hours
FROM curation_sessions
WHERE curator = 'your_name'
  AND session_date >= DATE('now', '-30 days')
ORDER BY session_date;

-- Proteins missing a UniProt ID
SELECT p.gene_id, p.name, s.name AS species
FROM proteins p
JOIN species s ON p.species_id = s.id
WHERE p.uniprot_id IS NULL OR p.uniprot_id = '';
```

Open the database directly anytime with:

```bash
sqlite3 phi_canto_tracking.db
```

## Benefits

1. **Zero setup** — no server, single-file database.
2. **Keep using Obsidian** for flexible notes; add queryable structure alongside.
3. **Track progress** with metrics and timestamps over time.
4. **Find gaps** — proteins without UniProt IDs, articles without curators.
5. **Portable** — the `.db` file works on any machine, including Codespaces.
