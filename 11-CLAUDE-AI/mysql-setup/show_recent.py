#!/usr/bin/env python3
"""
Show recent curation records from database
"""

from phi_canto_sqlite import PHICantoSQLite
from datetime import datetime, timedelta

def show_recent_activity(days=7):
    """Show recent curation activity across all record types"""
    db = PHICantoSQLite()
    if not db.connect():
        return

    print(f"📊 Recent Curation Activity (Last {days} days)")
    print("=" * 60)

    # Recent curation sessions
    print("\n🕒 Recent Curation Sessions")
    print("-" * 40)
    db.cursor.execute("""
        SELECT
            session_date,
            created_date,
            session_duration_hours,
            proteins_curated,
            interactions_added,
            experiments_annotated,
            notes,
            obsidian_session_log
        FROM curation_sessions
        WHERE session_date >= DATE('now', '-{} days')
        ORDER BY created_date DESC
        LIMIT 10
    """.format(days))

    sessions = db.cursor.fetchall()
    for session in sessions:
        duration = f" | {session['session_duration_hours']}h" if session['session_duration_hours'] else ""
        print(f"📅 {session['session_date']} | ⏰ {session['created_date']}{duration}")
        print(f"   🧬 {session['proteins_curated']} proteins | 🔗 {session['interactions_added']} interactions | 🧪 {session['experiments_annotated']} experiments")
        if session['notes']:
            print(f"   📝 {session['notes']}")
        if session['obsidian_session_log']:
            print(f"   📄 Log: {session['obsidian_session_log']}")
        print()

    # Recent articles added/updated
    print("\n📚 Recent Articles Activity")
    print("-" * 40)
    db.cursor.execute("""
        SELECT
            title,
            pmid,
            status,
            curator,
            updated_date,
            obsidian_note_path
        FROM articles
        WHERE updated_date >= DATE('now', '-{} days')
        ORDER BY updated_date DESC
        LIMIT 5
    """.format(days))

    articles = db.cursor.fetchall()
    for article in articles:
        status_emoji = {
            'queued': '⚪',
            'in_progress': '🟡',
            'curated': '🟢',
            'reviewed': '🔵',
            'published': '🟣'
        }.get(article['status'], '❓')

        print(f"{status_emoji} {article['title'][:60]}...")
        print(f"   📄 PMID: {article['pmid']} | 👤 {article['curator']} | ⏰ {article['updated_date']}")
        if article['obsidian_note_path']:
            print(f"   📝 Note: {article['obsidian_note_path']}")
        print()

    # Recent protein mentions/relationships
    print("\n🧬 Recent Protein Research Activity")
    print("-" * 40)
    db.cursor.execute("""
        SELECT
            p.gene_id,
            p.name as protein_name,
            p.gene_name,
            s.name as species_name,
            p.updated_date,
            p.obsidian_note_path
        FROM proteins p
        JOIN species s ON p.species_id = s.id
        WHERE p.updated_date >= DATE('now', '-{} days')
        ORDER BY p.updated_date DESC
        LIMIT 5
    """.format(days))

    proteins = db.cursor.fetchall()
    for protein in proteins:
        print(f"🧬 {protein['gene_id']} ({protein['gene_name']}) - {protein['species_name']}")
        print(f"   📝 {protein['protein_name']}")
        print(f"   ⏰ Updated: {protein['updated_date']}")
        if protein['obsidian_note_path']:
            print(f"   📄 Note: {protein['obsidian_note_path']}")
        print()

    # Summary statistics
    print("\n📈 Summary Statistics")
    print("-" * 40)

    # Total activity in period
    db.cursor.execute("""
        SELECT
            COUNT(*) as total_sessions,
            SUM(proteins_curated) as total_proteins,
            SUM(interactions_added) as total_interactions,
            SUM(experiments_annotated) as total_experiments,
            SUM(session_duration_hours) as total_hours
        FROM curation_sessions
        WHERE session_date >= DATE('now', '-{} days')
    """.format(days))

    stats = db.cursor.fetchone()
    print(f"🎯 {stats['total_sessions']} sessions | {stats['total_proteins']} proteins | {stats['total_interactions']} interactions")
    print(f"🧪 {stats['total_experiments']} experiments | {stats['total_hours']} hours total")

    # Articles by status
    db.cursor.execute("""
        SELECT status, COUNT(*) as count
        FROM articles
        GROUP BY status
        ORDER BY
            CASE status
                WHEN 'in_progress' THEN 1
                WHEN 'queued' THEN 2
                WHEN 'curated' THEN 3
                WHEN 'reviewed' THEN 4
                WHEN 'published' THEN 5
            END
    """)

    article_stats = db.cursor.fetchall()
    print("\n📚 Article Pipeline:")
    for stat in article_stats:
        emoji = {
            'queued': '⚪',
            'in_progress': '🟡',
            'curated': '🟢',
            'reviewed': '🔵',
            'published': '🟣'
        }.get(stat['status'], '❓')
        print(f"   {emoji} {stat['status'].title()}: {stat['count']}")

    db.disconnect()

if __name__ == "__main__":
    import sys
    days = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    show_recent_activity(days)