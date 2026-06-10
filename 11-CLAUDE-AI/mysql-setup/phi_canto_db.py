#!/usr/bin/env python3
"""
PHI-Canto Database Integration
Simple hybrid approach to complement Obsidian vault with structured tracking
"""

import mysql.connector
from datetime import datetime, date
import os
import re
from pathlib import Path

class PHICantoDB:
    def __init__(self, host='localhost', user='root', password='', database='phi_canto_tracking'):
        """Initialize database connection"""
        self.config = {
            'host': host,
            'user': user,
            'password': password,
            'database': database
        }
        self.connection = None
        self.cursor = None

    def connect(self):
        """Connect to MySQL database"""
        try:
            self.connection = mysql.connector.connect(**self.config)
            self.cursor = self.connection.cursor(dictionary=True)
            print("✅ Connected to MySQL database")
            return True
        except mysql.connector.Error as err:
            print(f"❌ Database connection failed: {err}")
            return False

    def disconnect(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        print("📴 Database connection closed")

    # ================== BASIC CRUD OPERATIONS ==================

    def add_species(self, name, type_, taxonomy_id=None, common_name=None, notes=None):
        """Add a new species to track"""
        query = """
        INSERT INTO species (name, type, taxonomy_id, common_name, notes)
        VALUES (%s, %s, %s, %s, %s)
        """
        values = (name, type_, taxonomy_id, common_name, notes)

        try:
            self.cursor.execute(query, values)
            self.connection.commit()
            species_id = self.cursor.lastrowid
            print(f"✅ Added species: {name} (ID: {species_id})")
            return species_id
        except mysql.connector.Error as err:
            print(f"❌ Error adding species: {err}")
            return None

    def add_article(self, pmid, title, journal=None, pub_year=None, authors=None,
                   status='queued', curator=None, obsidian_path=None):
        """Add a new article to track"""
        query = """
        INSERT INTO articles (pmid, title, journal, pub_year, authors, status, curator, obsidian_note_path)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (pmid, title, journal, pub_year, authors, status, curator, obsidian_path)

        try:
            self.cursor.execute(query, values)
            self.connection.commit()
            article_id = self.cursor.lastrowid
            print(f"✅ Added article: {title[:50]}... (ID: {article_id})")
            return article_id
        except mysql.connector.Error as err:
            print(f"❌ Error adding article: {err}")
            return None

    def add_protein(self, gene_id, species_id, name, gene_name=None, function_summary=None,
                   protein_type='other', obsidian_path=None):
        """Add a new protein to track"""
        query = """
        INSERT INTO proteins (gene_id, species_id, name, gene_name, function_summary, protein_type, obsidian_note_path)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        values = (gene_id, species_id, name, gene_name, function_summary, protein_type, obsidian_path)

        try:
            self.cursor.execute(query, values)
            self.connection.commit()
            protein_id = self.cursor.lastrowid
            print(f"✅ Added protein: {name} (ID: {protein_id})")
            return protein_id
        except mysql.connector.Error as err:
            print(f"❌ Error adding protein: {err}")
            return None

    def log_session(self, session_date, curator, article_id=None, duration=None,
                   proteins_curated=0, interactions_added=0, experiments=0,
                   notes=None, obsidian_log_path=None):
        """Log a curation session"""
        query = """
        INSERT INTO curation_sessions
        (session_date, curator, article_id, session_duration_hours, proteins_curated,
         interactions_added, experiments_annotated, notes, obsidian_session_log)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (session_date, curator, article_id, duration, proteins_curated,
                 interactions_added, experiments, notes, obsidian_log_path)

        try:
            self.cursor.execute(query, values)
            self.connection.commit()
            session_id = self.cursor.lastrowid
            print(f"✅ Logged session for {curator} on {session_date} (ID: {session_id})")
            return session_id
        except mysql.connector.Error as err:
            print(f"❌ Error logging session: {err}")
            return None

    # ================== QUERY OPERATIONS ==================

    def get_curation_progress(self, days=30):
        """Get curation progress summary for recent days"""
        query = """
        SELECT * FROM curation_progress
        WHERE date >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
        ORDER BY date DESC
        """

        self.cursor.execute(query, (days,))
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

    def get_species_summary(self):
        """Get summary of species being tracked"""
        self.cursor.execute("SELECT * FROM species_summary")
        results = self.cursor.fetchall()

        print("\n🧬 Species Summary")
        print("-" * 40)
        for row in results:
            print(f"{row['type'].title()}: {row['species_count']} species, {row['protein_count']} proteins")

        return results

    def get_article_status(self):
        """Get current status of articles in curation pipeline"""
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
        """Find effector proteins, optionally filtered by species"""
        query = """
        SELECT p.gene_id, p.name, p.gene_name, s.name as species_name, p.function_summary
        FROM proteins p
        JOIN species s ON p.species_id = s.id
        WHERE p.protein_type = 'effector'
        """

        params = []
        if species_pattern:
            query += " AND s.name LIKE %s"
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

# ================== UTILITY FUNCTIONS ==================

def demo_queries():
    """Demonstrate basic database queries"""
    db = PHICantoDB()

    if not db.connect():
        return

    print("🔍 Running database demonstration queries...")
    print("=" * 60)

    # Show recent progress
    db.get_curation_progress(days=30)

    # Show species summary
    db.get_species_summary()

    # Show article status
    db.get_article_status()

    # Show effector proteins
    db.find_effector_proteins(species_pattern="Fusarium")

    db.disconnect()

def quick_add_session(curator="martin.urban", proteins=0, interactions=0):
    """Quick way to log today's curation session"""
    db = PHICantoDB()

    if not db.connect():
        return

    session_id = db.log_session(
        session_date=date.today(),
        curator=curator,
        proteins_curated=proteins,
        interactions_added=interactions,
        notes=f"Quick session log via script"
    )

    if session_id:
        print(f"✅ Logged today's session (ID: {session_id})")

    db.disconnect()
    return session_id

if __name__ == "__main__":
    print("PHI-Canto Database Integration")
    print("==============================")
    print()
    print("Available functions:")
    print("- demo_queries(): Show database contents")
    print("- quick_add_session(): Log today's work")
    print()

    # Run demo
    demo_queries()