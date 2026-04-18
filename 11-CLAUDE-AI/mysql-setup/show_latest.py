#!/usr/bin/env python3
"""
Show the most recent curated entries with detailed information
"""

from phi_canto_sqlite import PHICantoSQLite

def show_latest_entries():
    """Show the most recent curated entries across all categories"""
    db = PHICantoSQLite()
    if not db.connect():
        return

    print("🆕 Latest Curated Entries")
    print("=" * 50)

    # Latest curation session
    print("\n📊 Most Recent Curation Session")
    print("-" * 35)
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
        ORDER BY created_date DESC
        LIMIT 1
    """)

    latest_session = db.cursor.fetchone()
    if latest_session:
        duration = f" ({latest_session['session_duration_hours']}h)" if latest_session['session_duration_hours'] else ""
        print(f"⏰ {latest_session['created_date']}{duration}")
        print(f"📅 Session Date: {latest_session['session_date']}")
        print(f"🧬 Proteins: {latest_session['proteins_curated']} | 🔗 Interactions: {latest_session['interactions_added']} | 🧪 Experiments: {latest_session['experiments_annotated']}")
        if latest_session['notes']:
            print(f"📝 Notes: {latest_session['notes']}")
        if latest_session['obsidian_session_log']:
            print(f"📄 Log: {latest_session['obsidian_session_log']}")

    # Latest article activity
    print("\n📚 Most Recently Updated Article")
    print("-" * 35)
    db.cursor.execute("""
        SELECT
            title,
            pmid,
            status,
            curator,
            created_date,
            updated_date,
            obsidian_note_path
        FROM articles
        ORDER BY updated_date DESC
        LIMIT 1
    """)

    latest_article = db.cursor.fetchone()
    if latest_article:
        status_emoji = {
            'queued': '⚪',
            'in_progress': '🟡',
            'curated': '🟢',
            'reviewed': '🔵',
            'published': '🟣'
        }.get(latest_article['status'], '❓')

        print(f"{status_emoji} {latest_article['title']}")
        print(f"📄 PMID: {latest_article['pmid']}")
        print(f"👤 Curator: {latest_article['curator']}")
        print(f"⏰ Created: {latest_article['created_date']}")
        print(f"⏰ Updated: {latest_article['updated_date']}")
        if latest_article['obsidian_note_path']:
            print(f"📝 Note: {latest_article['obsidian_note_path']}")

    # Latest protein activity
    print("\n🧬 Most Recently Updated Protein")
    print("-" * 35)
    db.cursor.execute("""
        SELECT
            p.gene_id,
            p.name,
            p.gene_name,
            p.function_summary,
            p.protein_type,
            p.created_date,
            p.updated_date,
            p.obsidian_note_path,
            s.name as species_name
        FROM proteins p
        JOIN species s ON p.species_id = s.id
        ORDER BY p.updated_date DESC
        LIMIT 1
    """)

    latest_protein = db.cursor.fetchone()
    if latest_protein:
        type_emoji = {
            'effector': '🎯',
            'resistance': '🛡️',
            'virulence': '⚔️',
            'other': '🧬'
        }.get(latest_protein['protein_type'], '🧬')

        print(f"{type_emoji} {latest_protein['gene_id']} ({latest_protein['gene_name']}) - {latest_protein['species_name']}")
        print(f"📝 {latest_protein['name']}")
        if latest_protein['function_summary']:
            print(f"⚙️  Function: {latest_protein['function_summary']}")
        print(f"⏰ Created: {latest_protein['created_date']}")
        print(f"⏰ Updated: {latest_protein['updated_date']}")
        if latest_protein['obsidian_note_path']:
            print(f"📄 Note: {latest_protein['obsidian_note_path']}")

    # Latest protein-article relationship
    print("\n🔗 Most Recent Protein-Article Connection")
    print("-" * 40)
    db.cursor.execute("""
        SELECT
            p.gene_id,
            p.gene_name,
            a.title,
            a.pmid,
            pam.mention_context,
            pam.experimental_evidence,
            pam.curated,
            pam.created_date
        FROM protein_article_mentions pam
        JOIN proteins p ON pam.protein_id = p.id
        JOIN articles a ON pam.article_id = a.id
        ORDER BY pam.created_date DESC
        LIMIT 1
    """)

    latest_mention = db.cursor.fetchone()
    if latest_mention:
        curated_status = "✅ Curated" if latest_mention['curated'] else "⏳ Pending"
        evidence_emoji = {
            'complementation': '🧪',
            'knockout': '✂️',
            'overexpression': '📈',
            'biochemical': '⚗️',
            'other': '🔬'
        }.get(latest_mention['experimental_evidence'], '🔬')

        print(f"🧬 {latest_mention['gene_id']} ({latest_mention['gene_name']}) ↔ PMID:{latest_mention['pmid']}")
        print(f"📄 {latest_mention['title'][:50]}...")
        print(f"{evidence_emoji} Evidence: {latest_mention['experimental_evidence']}")
        print(f"📝 Context: {latest_mention['mention_context'][:80]}...")
        print(f"⏰ Documented: {latest_mention['created_date']}")
        print(f"✅ Status: {curated_status}")

    # Summary of today's activity
    print("\n📈 Today's Activity Summary")
    print("-" * 30)
    db.cursor.execute("""
        SELECT
            COUNT(*) as sessions,
            SUM(proteins_curated) as proteins,
            SUM(interactions_added) as interactions,
            SUM(experiments_annotated) as experiments,
            SUM(session_duration_hours) as hours
        FROM curation_sessions
        WHERE DATE(created_date) = DATE('now')
    """)

    today_stats = db.cursor.fetchone()
    if today_stats and today_stats['sessions'] > 0:
        print(f"📅 Today: {today_stats['sessions']} sessions")
        print(f"🧬 {today_stats['proteins']} proteins | 🔗 {today_stats['interactions']} interactions | 🧪 {today_stats['experiments']} experiments")
        if today_stats['hours']:
            print(f"⏱️  Total time: {today_stats['hours']} hours")
    else:
        print("📅 No sessions logged today yet")

    db.disconnect()

if __name__ == "__main__":
    show_latest_entries()