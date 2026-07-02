#!/usr/bin/env python3
"""
PHI-Canto Database Integration - SQLite
Server-free tracking database (sqlite3 is built into Python)
"""

import sqlite3
from datetime import datetime, date
import os
from pathlib import Path

from phiweaver import repo_root
from phiweaver.tracking import migrations, repository

# Canonical tracking-DB location (see AGENTS.md): a fixed home under the repo root so every
# consumer — pipeline, session logger, registry generator, daily report — reads and writes
# the SAME database regardless of the caller's current working directory.
DEFAULT_DB_PATH = "11-CLAUDE-AI/db/phi_canto_tracking.db"

class PHICantoSQLite:
    def __init__(self, db_path=None):
        """Initialize SQLite database connection.

        With no db_path, use the canonical tracking DB under the repo root, so the
        database location does not depend on the caller's working directory.
        """
        self.db_path = str(db_path) if db_path is not None else str(
            repo_root() / DEFAULT_DB_PATH)
        self.connection = None
        self.cursor = None

    def connect(self):
        """Connect to SQLite database, create if needed"""
        try:
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row  # Enable dict-like access
            self.cursor = self.connection.cursor()
            print(f"✅ Connected to SQLite database: {self.db_path}")
            return True
        except sqlite3.Error as err:
            print(f"❌ Database connection failed: {err}")
            return False

    def create_schema(self):
        """Bring the database schema up to date by running all pending migrations.

        Delegates to phiweaver.tracking.migrations (the schema lives there as the v1
        baseline). Idempotent and safe on a pre-existing DB; modules can register their
        own migrations without editing this method.
        """
        try:
            applied = migrations.run_migrations(self.connection)
            total = sum(applied.values())
            if total:
                print(f"✅ Database schema up to date ({total} migration(s) applied)")
            else:
                print("✅ Database schema already up to date")
            return True
        except sqlite3.Error as err:
            print(f"❌ Error applying migrations: {err}")
            return False

    def populate_sample_data(self):
        """Insert sample data based on Fusarium effectors project"""

        # Insert species
        species_data = [
            ('Fusarium graminearum', 'pathogen', 229533, 'wheat head blight fungus', 'Major cereal pathogen, teleomorph Gibberella zeae'),
            ('Triticum aestivum', 'host', 4565, 'wheat', 'Common wheat, major crop plant'),
            ('Arabidopsis thaliana', 'host', 3702, 'thale cress', 'Model plant organism'),
            ('Nicotiana benthamiana', 'host', 4100, 'tobacco', 'Common host for transient expression studies')
        ]

        for species in species_data:
            self.cursor.execute("""
                INSERT INTO species (name, type, taxonomy_id, common_name, notes)
                VALUES (?, ?, ?, ?, ?)
            """, species)

        # Insert articles
        articles_data = [
            ('38234567', 'FgTPP1 effector manipulates host immunity in Fusarium graminearum', 'Plant Pathology', 2024, 'Smith et al.', 'curated', 'martin.urban', '04-Literature/FgTPP1-effector-2024.md'),
            ('38456789', 'Characterization of FgSCP effector protein in wheat pathogenesis', 'Molecular Plant Pathology', 2024, 'Jones et al.', 'in_progress', 'martin.urban', '04-Literature/FgSCP-characterization-2024.md'),
            ('37123456', 'Fg62 effector targets host transcription factors', 'Nature Plants', 2023, 'Brown et al.', 'queued', None, '04-Literature/Fg62-transcription-targets.md')
        ]

        for article in articles_data:
            self.cursor.execute("""
                INSERT INTO articles (pmid, title, journal, pub_year, authors, status, curator, obsidian_note_path)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, article)

        # Insert proteins
        proteins_data = [
            ('FGSG_11164', 1, 'Trehalose-6-phosphate phosphatase', 'FgTPP1', 'Effector that manipulates host trehalose metabolism and immune responses', 'effector', '02-Projects/Fusarium-effectors/proteins/FgTPP1.md'),
            ('FGSG_08454', 1, 'Secreted cysteine-rich protein', 'FgSCP', 'Small secreted effector with unknown host targets', 'effector', '02-Projects/Fusarium-effectors/proteins/FgSCP.md'),
            ('FGSG_01831', 1, 'Fg62 effector protein', 'Fg62', 'Targets host transcription factors to suppress immunity', 'effector', '02-Projects/Fusarium-effectors/proteins/Fg62.md'),
            ('FGSG_03895', 1, 'OSP24-like effector', 'OSP24', 'Outer spore protein with potential effector function', 'effector', None),
            ('FGSG_02847', 1, 'Nuclear localization signal protein', 'FgNls1', 'Effector with nuclear targeting capability', 'effector', None)
        ]

        for protein in proteins_data:
            self.cursor.execute("""
                INSERT INTO proteins (gene_id, species_id, name, gene_name, function_summary, protein_type, obsidian_note_path)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, protein)

        # Insert curation sessions
        sessions_data = [
            ('2026-04-12', 'martin.urban', 1, 2.5, 3, 5, 8, 'Literature review and initial protein characterization for FgTPP1', '11-CLAUDE-AI/SESSION-LOGS/2026-04-12-fusarium-effectors-2.md'),
            ('2026-04-11', 'martin.urban', None, 1.5, 0, 0, 0, 'Vault setup and project initialization', '11-CLAUDE-AI/SESSION-LOGS/2026-04-11-vault-setup.md'),
            ('2026-04-18', 'martin.urban', 2, 3.0, 5, 7, 10, 'MySQL hybrid system setup and testing', '11-CLAUDE-AI/SESSION-LOGS/2026-04-18-mysql-hybrid-setup.md')
        ]

        for session in sessions_data:
            self.cursor.execute("""
                INSERT INTO curation_sessions (session_date, curator, article_id, session_duration_hours, proteins_curated, interactions_added, experiments_annotated, notes, obsidian_session_log)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, session)

        # Insert protein-article relationships
        relationships_data = [
            (1, 1, 'Main subject protein with detailed functional analysis', 'complementation', 1),
            (2, 2, 'Primary focus with structural and functional studies', 'knockout', 0),
            (3, 3, 'Transcription factor targeting mechanism described', 'biochemical', 0),
            (1, 2, 'Mentioned in comparison with other effectors', 'other', 0)
        ]

        for rel in relationships_data:
            self.cursor.execute("""
                INSERT INTO protein_article_mentions (protein_id, article_id, mention_context, experimental_evidence, curated)
                VALUES (?, ?, ?, ?, ?)
            """, rel)

        self.connection.commit()
        print("✅ Sample data inserted successfully")

    def get_curation_progress(self, days=30):
        """Get curation progress summary (data from repository; this method prints)."""
        results = repository.curation_progress(self.connection, days)

        print(f"\n📊 Curation Progress (Last {days} days)")
        print("-" * 80)
        if results:
            for row in results:
                print(f"📅 {row['date']} | 👤 {row['curator']} | "
                     f"Sessions: {row['sessions']} | Proteins: {row['total_proteins']} | "
                     f"Interactions: {row['total_interactions']} | Hours: {row['total_hours']}")
        else:
            print("No sessions recorded")

        return results

    def get_article_status(self):
        """Get current status of articles (data from repository; this method prints)."""
        results = repository.article_status(self.connection)

        print("\n📚 Article Curation Status")
        print("-" * 50)
        for row in results:
            print(f"{row['status'].title()}: {row['article_count']} articles, "
                 f"{row['total_protein_mentions']} protein mentions")

        return results

    def find_effector_proteins(self, species_pattern=None):
        """Find effector proteins (data from repository; this method prints)."""
        results = repository.effector_proteins(self.connection, species_pattern)

        print(f"\n🎯 Effector Proteins" + (f" (filtered by '{species_pattern}')" if species_pattern else ""))
        print("-" * 80)
        for row in results:
            print(f"🧬 {row['gene_id']} ({row['gene_name']}) - {row['species_name']}")
            print(f"   📝 {row['name']}")
            if row['function_summary']:
                print(f"   ⚙️  {row['function_summary'][:100]}...")
            print()

        return results

    DEFAULT_CURATOR = "martin.urban"

    def record_completion(self, base_name, summary, note_path=None, pmid=None,
                          proteins_curated=0, interactions_added=0,
                          experiments_annotated=0, session_duration_hours=None,
                          derived_notes=None, curator=None, session_date=None):
        """Record a finished curation: flip its article to 'curated' and log a real,
        article-linked completion session — in one transaction.

        This is the authoritative "completion metrics" entry point, replacing the old
        behaviour where completion logged a session with hardcoded zero counts and never
        updated article status.

        The article is matched by pmid, then obsidian_note_path, then title; if none
        exists yet (e.g. it was never added during intake), a minimal row is created so
        the metrics always have somewhere to attach.

        Returns a dict describing what was recorded.
        """
        if session_date is None:
            session_date = date.today()
        if isinstance(session_date, date):
            session_date = session_date.isoformat()  # avoid the 3.12 date-adapter warning
        curator = curator or self.DEFAULT_CURATOR
        cur = self.cursor

        # 1. Find the article (pmid → note_path → title), else create a minimal row.
        article_id = None
        for column, value in (("pmid", pmid), ("obsidian_note_path", note_path),
                              ("title", base_name)):
            if not value:
                continue
            row = cur.execute(
                f"SELECT id FROM articles WHERE {column} = ?", (value,)).fetchone()
            if row:
                article_id = row["id"]
                break

        article_created = False
        if article_id is None:
            cur.execute(
                "INSERT INTO articles (pmid, title, status, curator, obsidian_note_path)"
                " VALUES (?, ?, 'curated', ?, ?)",
                (pmid, base_name, curator, note_path))
            article_id = cur.lastrowid
            article_created = True
        else:
            cur.execute(
                "UPDATE articles SET status = 'curated', updated_date = CURRENT_TIMESTAMP"
                " WHERE id = ?", (article_id,))

        # 2. Log the completion session, linked to the article, with real metrics.
        notes = f"Completed: {summary}"
        if derived_notes:
            notes += f" | {derived_notes}"
        cur.execute(
            "INSERT INTO curation_sessions"
            " (session_date, curator, article_id, session_duration_hours,"
            "  proteins_curated, interactions_added, experiments_annotated, notes)"
            " VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (session_date, curator, article_id, session_duration_hours,
             proteins_curated, interactions_added, experiments_annotated, notes))
        session_id = cur.lastrowid
        self.connection.commit()

        return {
            "article_id": article_id,
            "article_created": article_created,
            "session_id": session_id,
            "status": "curated",
            "proteins_curated": proteins_curated,
            "interactions_added": interactions_added,
            "experiments_annotated": experiments_annotated,
            "session_duration_hours": session_duration_hours,
        }

    def get_completion_metrics(self):
        """Per-article completion metrics, aggregated from article-linked sessions, for
        articles that have reached 'curated' or beyond (data from repository; prints)."""
        results = repository.completion_metrics(self.connection)

        print("\n🏁 Completion Metrics (curated and beyond)")
        print("-" * 72)
        if not results:
            print("No completed curations recorded yet.")
        for r in results:
            print(f"✅ {r['title'][:50]} (PMID {r['pmid'] or '—'}) [{r['status']}]")
            print(f"   proteins {r['proteins']} | interactions {r['interactions']} | "
                  f"experiments {r['experiments']} | hours {r['hours']} | "
                  f"sessions {r['sessions']}")
        return results

    def disconnect(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        print("📴 Database connection closed")

def demo_sqlite_setup():
    """Demonstrate SQLite setup with sample data"""
    print("🚀 PHI-Canto SQLite Demo Setup")
    print("=" * 40)

    db = PHICantoSQLite()

    if not db.connect():
        return False

    print("\n1. Creating database schema...")
    if not db.create_schema():
        return False

    print("\n2. Populating with sample data...")
    db.populate_sample_data()

    print("\n3. Demonstrating queries...")
    db.get_curation_progress(days=30)
    db.get_article_status()
    db.find_effector_proteins("Fusarium")

    print(f"\n✅ SQLite database created: {db.db_path}")
    print("💡 SQLite needs no server — this single .db file is the whole tracking database.")

    db.disconnect()
    return True

if __name__ == "__main__":
    demo_sqlite_setup()