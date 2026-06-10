#!/usr/bin/env python3
"""
PHI-Canto Database Integration - SQLite
Server-free tracking database (sqlite3 is built into Python)
"""

import sqlite3
from datetime import datetime, date
import os
from pathlib import Path

class PHICantoSQLite:
    def __init__(self, db_path='phi_canto_tracking.db'):
        """Initialize SQLite database connection"""
        self.db_path = db_path
        self.connection = None
        self.cursor = None

    def connect(self):
        """Connect to SQLite database, create if needed"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row  # Enable dict-like access
            self.cursor = self.connection.cursor()
            print(f"✅ Connected to SQLite database: {self.db_path}")
            return True
        except sqlite3.Error as err:
            print(f"❌ Database connection failed: {err}")
            return False

    def create_schema(self):
        """Create database schema"""
        schema_sql = """
        -- Species table
        CREATE TABLE IF NOT EXISTS species (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT CHECK(type IN ('host', 'pathogen')) NOT NULL,
            taxonomy_id INTEGER,
            common_name TEXT,
            notes TEXT,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Articles table
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pmid TEXT UNIQUE,
            doi TEXT,
            title TEXT NOT NULL,
            journal TEXT,
            pub_year INTEGER,
            authors TEXT,
            status TEXT CHECK(status IN ('queued', 'in_progress', 'curated', 'reviewed', 'published')) DEFAULT 'queued',
            curator TEXT,
            priority TEXT CHECK(priority IN ('low', 'medium', 'high')) DEFAULT 'medium',
            obsidian_note_path TEXT,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Proteins table
        CREATE TABLE IF NOT EXISTS proteins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            gene_id TEXT,
            uniprot_id TEXT,
            species_id INTEGER,
            name TEXT,
            gene_name TEXT,
            function_summary TEXT,
            protein_type TEXT CHECK(protein_type IN ('effector', 'resistance', 'virulence', 'other')),
            obsidian_note_path TEXT,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (species_id) REFERENCES species(id)
        );

        -- Curation sessions table
        CREATE TABLE IF NOT EXISTS curation_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_date DATE NOT NULL,
            curator TEXT NOT NULL,
            article_id INTEGER,
            session_duration_hours REAL,
            proteins_curated INTEGER DEFAULT 0,
            interactions_added INTEGER DEFAULT 0,
            experiments_annotated INTEGER DEFAULT 0,
            notes TEXT,
            obsidian_session_log TEXT,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (article_id) REFERENCES articles(id)
        );

        -- Protein-article relationships
        CREATE TABLE IF NOT EXISTS protein_article_mentions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            protein_id INTEGER,
            article_id INTEGER,
            mention_context TEXT,
            experimental_evidence TEXT CHECK(experimental_evidence IN ('complementation', 'knockout', 'overexpression', 'biochemical', 'other')),
            curated INTEGER DEFAULT 0,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (protein_id) REFERENCES proteins(id),
            FOREIGN KEY (article_id) REFERENCES articles(id),
            UNIQUE(protein_id, article_id)
        );

        -- Create indexes for better performance
        CREATE INDEX IF NOT EXISTS idx_articles_status ON articles(status);
        CREATE INDEX IF NOT EXISTS idx_proteins_species ON proteins(species_id);
        CREATE INDEX IF NOT EXISTS idx_sessions_curator_date ON curation_sessions(curator, session_date);
        """

        try:
            self.cursor.executescript(schema_sql)
            self.connection.commit()
            print("✅ Database schema created successfully")
            return True
        except sqlite3.Error as err:
            print(f"❌ Error creating schema: {err}")
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
        """Get curation progress summary"""
        query = """
        SELECT
            DATE(session_date) as date,
            curator,
            COUNT(*) as sessions,
            SUM(proteins_curated) as total_proteins,
            SUM(interactions_added) as total_interactions,
            SUM(session_duration_hours) as total_hours
        FROM curation_sessions
        WHERE session_date >= DATE('now', '-{} days')
        GROUP BY DATE(session_date), curator
        ORDER BY session_date DESC
        """.format(days)

        self.cursor.execute(query)
        results = self.cursor.fetchall()

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
        """Get current status of articles"""
        query = """
        SELECT
            a.status,
            COUNT(a.id) as article_count,
            COUNT(pam.id) as total_protein_mentions
        FROM articles a
        LEFT JOIN protein_article_mentions pam ON a.id = pam.article_id
        GROUP BY a.status
        ORDER BY
            CASE a.status
                WHEN 'queued' THEN 1
                WHEN 'in_progress' THEN 2
                WHEN 'curated' THEN 3
                WHEN 'reviewed' THEN 4
                WHEN 'published' THEN 5
            END
        """

        self.cursor.execute(query)
        results = self.cursor.fetchall()

        print("\n📚 Article Curation Status")
        print("-" * 50)
        for row in results:
            print(f"{row['status'].title()}: {row['article_count']} articles, "
                 f"{row['total_protein_mentions']} protein mentions")

        return results

    def find_effector_proteins(self, species_pattern=None):
        """Find effector proteins"""
        query = """
        SELECT p.gene_id, p.name, p.gene_name, s.name as species_name, p.function_summary
        FROM proteins p
        JOIN species s ON p.species_id = s.id
        WHERE p.protein_type = 'effector'
        """

        params = []
        if species_pattern:
            query += " AND s.name LIKE ?"
            params.append(f"%{species_pattern}%")

        query += " ORDER BY s.name, p.gene_id"

        self.cursor.execute(query, params)
        results = self.cursor.fetchall()

        print(f"\n🎯 Effector Proteins" + (f" (filtered by '{species_pattern}')" if species_pattern else ""))
        print("-" * 80)
        for row in results:
            print(f"🧬 {row['gene_id']} ({row['gene_name']}) - {row['species_name']}")
            print(f"   📝 {row['name']}")
            if row['function_summary']:
                print(f"   ⚙️  {row['function_summary'][:100]}...")
            print()

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