#!/usr/bin/env python3
"""
Daily PHI-Canto Curation Helper
Simple commands for everyday database operations
"""

from phiweaver.tracking.phi_canto_sqlite import PHICantoSQLite
from datetime import date
import sys

def log_today_session(proteins=0, interactions=0, hours=None, notes=None):
    """Quick log of today's curation work"""
    db = PHICantoSQLite()
    if not db.connect():
        return

    db.cursor.execute("""
        INSERT INTO curation_sessions
        (session_date, curator, proteins_curated, interactions_added, session_duration_hours, notes)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (date.today(), 'martin.urban', proteins, interactions, hours, notes))

    db.connection.commit()

    session_id = db.cursor.lastrowid
    print(f"✅ Logged today's session: {proteins} proteins, {interactions} interactions")
    if hours:
        print(f"   ⏱️  Duration: {hours} hours")
    if notes:
        print(f"   📝 Notes: {notes}")

    db.disconnect()
    return session_id

def add_article(pmid, title, journal=None, year=None, authors=None):
    """Add new article to curation pipeline"""
    db = PHICantoSQLite()
    if not db.connect():
        return

    db.cursor.execute("""
        INSERT INTO articles (pmid, title, journal, pub_year, authors, status, curator)
        VALUES (?, ?, ?, ?, ?, 'queued', 'martin.urban')
    """, (pmid, title, journal, year, authors))

    db.connection.commit()

    article_id = db.cursor.lastrowid
    print(f"✅ Added article: {title[:60]}...")
    print(f"   📄 PMID: {pmid}")

    db.disconnect()
    return article_id

def update_article_status(pmid, status):
    """Update article curation status"""
    db = PHICantoSQLite()
    if not db.connect():
        return

    db.cursor.execute("""
        UPDATE articles SET status = ?, updated_date = CURRENT_TIMESTAMP
        WHERE pmid = ?
    """, (status, pmid))

    db.connection.commit()

    if db.cursor.rowcount > 0:
        print(f"✅ Updated PMID {pmid} status to: {status}")
    else:
        print(f"❌ Article with PMID {pmid} not found")

    db.disconnect()

def show_progress():
    """Show recent progress and current status"""
    db = PHICantoSQLite()
    if not db.connect():
        return

    db.get_curation_progress(days=14)
    db.get_article_status()

    # Show articles needing attention
    print("\n📋 Articles Needing Attention")
    print("-" * 40)

    db.cursor.execute("""
        SELECT title, pmid, status
        FROM articles
        WHERE status IN ('queued', 'in_progress')
        ORDER BY
            CASE status
                WHEN 'in_progress' THEN 1
                WHEN 'queued' THEN 2
            END,
            pub_year DESC
    """)

    articles = db.cursor.fetchall()
    for article in articles:
        status_emoji = "🟡" if article['status'] == 'in_progress' else "⚪"
        print(f"{status_emoji} {article['title'][:60]}... (PMID: {article['pmid']})")

    db.disconnect()

def show_completed():
    """Show real completion metrics per curated article"""
    db = PHICantoSQLite()
    if not db.connect():
        return

    db.get_completion_metrics()
    db.disconnect()

def find_gaps():
    """Find proteins and articles that need attention"""
    db = PHICantoSQLite()
    if not db.connect():
        return

    print("\n🔍 Data Gaps Analysis")
    print("=" * 30)

    # Proteins without UniProt IDs
    print("\n🧬 Proteins missing UniProt IDs:")
    db.cursor.execute("""
        SELECT gene_id, name
        FROM proteins
        WHERE uniprot_id IS NULL OR uniprot_id = ''
        LIMIT 5
    """)
    proteins = db.cursor.fetchall()
    for protein in proteins:
        print(f"   • {protein['gene_id']} - {protein['name'][:50]}...")

    # Articles without curators
    print("\n📚 Articles needing curator assignment:")
    db.cursor.execute("""
        SELECT title, pmid
        FROM articles
        WHERE curator IS NULL AND status = 'queued'
        LIMIT 3
    """)
    articles = db.cursor.fetchall()
    for article in articles:
        print(f"   • {article['title'][:50]}... (PMID: {article['pmid']})")

    db.disconnect()

def show_help():
    """Show available commands"""
    print("🔧 Daily PHI-Canto Database Commands")
    print("=" * 40)
    print("python3 daily_curation.py log 3 5 2.5 'Notes'    - Log session (proteins, interactions, hours, notes)")
    print("python3 daily_curation.py add 12345 'Title'      - Add article to pipeline")
    print("python3 daily_curation.py status 12345 curated   - Update article status")
    print("python3 daily_curation.py progress               - Show progress summary")
    print("python3 daily_curation.py completed              - Show completion metrics per curated article")
    print("python3 daily_curation.py gaps                   - Find data gaps")
    print("python3 daily_curation.py help                   - Show this help")
    print()
    print("Article statuses: queued, in_progress, curated, reviewed, published")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        show_help()
        sys.exit()

    command = sys.argv[1]

    if command == "log":
        proteins = int(sys.argv[2]) if len(sys.argv) > 2 else 0
        interactions = int(sys.argv[3]) if len(sys.argv) > 3 else 0
        hours = float(sys.argv[4]) if len(sys.argv) > 4 else None
        notes = sys.argv[5] if len(sys.argv) > 5 else None
        log_today_session(proteins, interactions, hours, notes)

    elif command == "add":
        pmid = sys.argv[2]
        title = sys.argv[3]
        journal = sys.argv[4] if len(sys.argv) > 4 else None
        year = int(sys.argv[5]) if len(sys.argv) > 5 else None
        add_article(pmid, title, journal, year)

    elif command == "status":
        pmid = sys.argv[2]
        status = sys.argv[3]
        update_article_status(pmid, status)

    elif command == "progress":
        show_progress()

    elif command == "completed":
        show_completed()

    elif command == "gaps":
        find_gaps()

    elif command == "help":
        show_help()

    else:
        print(f"Unknown command: {command}")
        show_help()