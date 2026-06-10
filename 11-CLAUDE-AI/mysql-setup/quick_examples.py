#!/usr/bin/env python3
"""
Quick Examples for PHI-Canto Database Integration
Run these to see how the hybrid system works in practice
"""

from phi_canto_db import PHICantoDB
from datetime import date
import sys

def example_daily_workflow():
    """Example of how you'd use this system daily"""
    print("🔄 Daily PHI-Canto Curation Workflow")
    print("=" * 50)

    db = PHICantoDB()
    if not db.connect():
        print("❌ Cannot connect to database. Make sure MySQL is running and database is set up.")
        return

    print("\n1. 📅 Log today's curation session...")
    session_id = db.log_session(
        session_date=date.today(),
        curator="martin.urban",
        session_duration_hours=2.0,
        proteins_curated=2,
        interactions_added=4,
        experiments_annotated=6,
        notes="Worked on Fusarium effectors, added FgTPP1 and FgSCP data",
        obsidian_log_path="11-CLAUDE-AI/SESSION-LOGS/2026-04-18-fusarium-work.md"
    )

    print("\n2. 📚 Add new article to curation pipeline...")
    article_id = db.add_article(
        pmid="38567890",
        title="Novel Fusarium graminearum effectors identified through proteomics",
        journal="Molecular Plant Pathology",
        pub_year=2024,
        authors="Garcia-Rodriguez et al.",
        status="queued",
        curator=None,  # Not assigned yet
        obsidian_path="04-Literature/novel-fg-effectors-2024.md"
    )

    print("\n3. 🧬 Add newly discovered protein...")
    if article_id:  # Only if article was added successfully
        protein_id = db.add_protein(
            gene_id="FGSG_09876",
            species_id=1,  # Fusarium graminearum
            name="Putative secreted effector FgNEW1",
            gene_name="FgNEW1",
            function_summary="Newly identified small secreted protein with signal peptide",
            protein_type="effector",
            obsidian_path="02-Projects/Fusarium-effectors/proteins/FgNEW1.md"
        )

    print("\n4. 📊 Check your progress...")
    db.get_curation_progress(days=7)  # Last week
    db.get_article_status()

    print("\n5. 🎯 Find effectors that need more work...")
    db.find_effector_proteins("Fusarium")

    db.disconnect()
    print("\n✅ Daily workflow complete!")

def example_project_setup():
    """Example of setting up a new curation project"""
    print("🚀 Setting Up New Curation Project")
    print("=" * 40)

    db = PHICantoDB()
    if not db.connect():
        return

    # Add a new pathogen species
    print("Adding new pathogen species...")
    species_id = db.add_species(
        name="Magnaporthe oryzae",
        type_="pathogen",
        taxonomy_id=148305,
        common_name="rice blast fungus",
        notes="Major rice pathogen, model organism for plant-fungal interactions"
    )

    # Add corresponding host
    print("Adding host species...")
    host_id = db.add_species(
        name="Oryza sativa",
        type_="host",
        taxonomy_id=4530,
        common_name="rice",
        notes="Major crop plant, model monocot"
    )

    # Add some literature
    print("Adding key literature...")
    article_id = db.add_article(
        pmid="35123456",
        title="Magnaporthe oryzae effector proteins and their roles in pathogenesis",
        journal="Annual Review of Phytopathology",
        pub_year=2024,
        authors="Wilson et al.",
        status="queued",
        obsidian_path="04-Literature/magnaporthe-effectors-review-2024.md"
    )

    print("\n📋 New project setup complete!")
    print(f"   🦠 Pathogen species ID: {species_id}")
    print(f"   🌱 Host species ID: {host_id}")
    print(f"   📄 Article ID: {article_id}")

    db.disconnect()

def example_queries():
    """Example queries you might run regularly"""
    print("🔍 Useful Database Queries")
    print("=" * 30)

    db = PHICantoDB()
    if not db.connect():
        return

    print("\n1. Articles that need curators assigned...")
    db.cursor.execute("""
        SELECT title, pmid, pub_year
        FROM articles
        WHERE curator IS NULL AND status = 'queued'
        ORDER BY pub_year DESC
        LIMIT 5
    """)
    results = db.cursor.fetchall()
    for article in results:
        print(f"   📄 {article['title'][:60]}... (PMID: {article['pmid']})")

    print("\n2. Proteins without UniProt IDs...")
    db.cursor.execute("""
        SELECT p.gene_id, p.name, s.name as species
        FROM proteins p
        JOIN species s ON p.species_id = s.id
        WHERE p.uniprot_id IS NULL OR p.uniprot_id = ''
        LIMIT 5
    """)
    results = db.cursor.fetchall()
    for protein in results:
        print(f"   🧬 {protein['gene_id']} - {protein['name'][:40]}... ({protein['species']})")

    print("\n3. Most productive curators this month...")
    db.cursor.execute("""
        SELECT
            curator,
            COUNT(*) as sessions,
            SUM(proteins_curated) as total_proteins,
            SUM(interactions_added) as total_interactions
        FROM curation_sessions
        WHERE session_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
        GROUP BY curator
        ORDER BY total_proteins DESC
    """)
    results = db.cursor.fetchall()
    for curator in results:
        print(f"   👤 {curator['curator']}: {curator['total_proteins']} proteins, "
              f"{curator['total_interactions']} interactions in {curator['sessions']} sessions")

    db.disconnect()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "workflow":
            example_daily_workflow()
        elif sys.argv[1] == "setup":
            example_project_setup()
        elif sys.argv[1] == "queries":
            example_queries()
        else:
            print("Usage: python quick_examples.py [workflow|setup|queries]")
    else:
        print("PHI-Canto Database Examples")
        print("=" * 30)
        print("Run with arguments:")
        print("  python quick_examples.py workflow  - Daily curation workflow")
        print("  python quick_examples.py setup     - Set up new project")
        print("  python quick_examples.py queries   - Useful database queries")
        print()
        print("Or run demo_queries() from phi_canto_db.py to see current data")