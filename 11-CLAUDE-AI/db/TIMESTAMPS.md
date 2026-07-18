---
created: 2026-04-18
type: reference
tags: [operations]
project: PHI-Weaver
---

# PHI-Canto Database Timestamps

Complete reference for timestamp tracking in the PHI-Canto hybrid database system.

## Timestamp Format

All timestamps use **YYYY-MM-DD HH:MM:SS** format (e.g., `2026-04-18 13:08:49`)

## Automatic Timestamp Fields

### Core Tables

**1. Curation Sessions** (`curation_sessions`)
```sql
created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- When session logged
```
- Records exact time when curation work was logged
- Automatically set when session is created
- Used for chronological ordering and productivity tracking

**2. Articles** (`articles`)
```sql
created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP   -- When added to pipeline
updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP   -- When status/details changed
  ON UPDATE CURRENT_TIMESTAMP
```
- `created_date`: When article first added to curation pipeline
- `updated_date`: Automatically updates when status changes or details modified

**3. Proteins** (`proteins`)
```sql
created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP   -- When first documented
updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP   -- When information updated
  ON UPDATE CURRENT_TIMESTAMP
```
- `created_date`: When protein first added to database
- `updated_date`: Automatically updates when function, UniProt ID, or other details change

**4. Species** (`species`)
```sql
created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP   -- When species added
updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP   -- When details updated
  ON UPDATE CURRENT_TIMESTAMP
```
- Tracks when host/pathogen species were added to tracking

**5. Protein-Article Mentions** (`protein_article_mentions`)
```sql
created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP   -- When relationship documented
```
- Records when protein-literature relationships were identified

## Viewing Timestamps

### Command Line Tools

**Show Recent Activity with Full Timestamps:**
```bash
python3 show_recent.py [days]    # Default: 7 days
python3 check_timestamps.py     # Detailed timestamp analysis
```

**Example Output:**
```
📅 2026-04-18 | ⏰ 2026-04-18 13:08:49 | 1.0h
   🧬 1 proteins | 🔗 3 interactions | 🧪 0 experiments
   📝 Quick session update: Updated FgNls1 protein characterization
```

### SQL Queries

**Recent Sessions with Precise Times:**
```sql
SELECT
    session_date,
    created_date,
    curator,
    proteins_curated,
    interactions_added,
    notes
FROM curation_sessions
WHERE created_date >= DATETIME('now', '-7 days')
ORDER BY created_date DESC;
```

**Article Status Changes:**
```sql
SELECT
    title,
    status,
    created_date,
    updated_date,
    curator
FROM articles
WHERE updated_date != created_date  -- Shows articles that were modified
ORDER BY updated_date DESC;
```

**Most Recently Updated Proteins:**
```sql
SELECT
    p.gene_id,
    p.name,
    s.name as species,
    p.created_date,
    p.updated_date,
    CASE
        WHEN p.updated_date > p.created_date THEN 'Modified'
        ELSE 'Original'
    END as status
FROM proteins p
JOIN species s ON p.species_id = s.id
ORDER BY p.updated_date DESC;
```

## Timestamp-Based Analytics

### Productivity Tracking
```sql
-- Sessions per day with timestamps
SELECT
    DATE(created_date) as date,
    COUNT(*) as sessions,
    MIN(created_date) as first_session,
    MAX(created_date) as last_session,
    SUM(proteins_curated) as proteins
FROM curation_sessions
WHERE created_date >= DATE('now', '-30 days')
GROUP BY DATE(created_date)
ORDER BY date DESC;
```

### Data Freshness Analysis
```sql
-- Find stale articles (not updated recently)
SELECT
    title,
    status,
    created_date,
    updated_date,
    ROUND(JULIANDAY('now') - JULIANDAY(updated_date), 1) as days_since_update
FROM articles
WHERE status IN ('queued', 'in_progress')
ORDER BY days_since_update DESC;
```

### Curation Velocity
```sql
-- Average time between creation and completion
SELECT
    AVG(JULIANDAY(updated_date) - JULIANDAY(created_date)) as avg_days_to_curate
FROM articles
WHERE status = 'curated';
```

## Integration with Session Logging

When using the automated session logger:

```bash
python3 session_logger.py quick 'Project' 'Summary' 2 3 1.5
```

**Automatic Timestamp Capture:**
1. `curation_sessions.created_date` = Current timestamp when logged
2. Session markdown includes database session ID for linking
3. All new articles/proteins get current timestamps
4. Updates to existing records refresh `updated_date`

**Session Log Frontmatter:**
```yaml
---
created: 2026-04-18          # Date only for Obsidian
session_id: 6                # Links to database record
---
```

Database record has full timestamp: `2026-04-18 13:08:49`

## Benefits of Precise Timestamps

1. **Chronological Ordering**: See exact sequence of curation activities
2. **Productivity Analysis**: Track work patterns and session timing
3. **Data Freshness**: Identify stale records needing attention
4. **Audit Trail**: Complete history of when changes were made
5. **Performance Metrics**: Measure curation velocity and efficiency
6. **Quality Assurance**: Correlate timestamps with external events

## Timezone Considerations

- All timestamps are in system local time (WSL environment)
- SQLite uses local timezone for CURRENT_TIMESTAMP
- For multi-user scenarios, consider UTC timestamps

## Best Practices

1. **Use session logger** for automatic timestamp consistency
2. **Check data freshness** regularly with timestamp queries
3. **Monitor productivity** trends with timestamp analytics
4. **Link timestamps** between database and Obsidian notes
5. **Archive old data** based on timestamp thresholds if needed

The timestamp system provides complete traceability of your PHI-Canto curation work with precise timing information for analysis and reporting.