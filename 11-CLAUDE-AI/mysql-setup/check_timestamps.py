#!/usr/bin/env python3
"""
Check current timestamp implementation in database
"""

from phi_canto_sqlite import PHICantoSQLite

def check_timestamps():
    db = PHICantoSQLite()
    if not db.connect():
        return

    print("🕐 Current Timestamp Fields in Database")
    print("=" * 50)

    # Check curation_sessions timestamps
    print("\n📊 Curation Sessions Timestamps:")
    print("-" * 30)
    db.cursor.execute("""
        SELECT
            id,
            session_date,
            created_date,
            curator,
            notes
        FROM curation_sessions
        ORDER BY created_date DESC
        LIMIT 5
    """)

    sessions = db.cursor.fetchall()
    for session in sessions:
        print(f"Session {session['id']}: {session['session_date']} | Created: {session['created_date']}")
        if session['notes']:
            print(f"   📝 {session['notes'][:50]}...")

    # Check articles timestamps
    print("\n📚 Articles Timestamps:")
    print("-" * 30)
    db.cursor.execute("""
        SELECT
            id,
            title,
            created_date,
            updated_date,
            status
        FROM articles
        ORDER BY updated_date DESC
        LIMIT 3
    """)

    articles = db.cursor.fetchall()
    for article in articles:
        print(f"📄 {article['title'][:40]}...")
        print(f"   Created: {article['created_date']} | Updated: {article['updated_date']}")
        print(f"   Status: {article['status']}")

    # Check proteins timestamps
    print("\n🧬 Proteins Timestamps:")
    print("-" * 30)
    db.cursor.execute("""
        SELECT
            id,
            gene_id,
            name,
            created_date,
            updated_date
        FROM proteins
        ORDER BY updated_date DESC
        LIMIT 3
    """)

    proteins = db.cursor.fetchall()
    for protein in proteins:
        print(f"🧬 {protein['gene_id']} - {protein['name'][:30]}...")
        print(f"   Created: {protein['created_date']} | Updated: {protein['updated_date']}")

    # Check protein_article_mentions timestamps
    print("\n🔗 Protein-Article Mentions Timestamps:")
    print("-" * 30)
    db.cursor.execute("""
        SELECT
            pam.id,
            p.gene_id,
            a.pmid,
            pam.created_date,
            pam.experimental_evidence
        FROM protein_article_mentions pam
        JOIN proteins p ON pam.protein_id = p.id
        JOIN articles a ON pam.article_id = a.id
        ORDER BY pam.created_date DESC
        LIMIT 3
    """)

    mentions = db.cursor.fetchall()
    for mention in mentions:
        print(f"🔗 {mention['gene_id']} ↔ PMID:{mention['pmid']}")
        print(f"   Created: {mention['created_date']} | Evidence: {mention['experimental_evidence']}")

    db.disconnect()

if __name__ == "__main__":
    check_timestamps()