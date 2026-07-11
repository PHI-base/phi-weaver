#!/usr/bin/env python3
"""
Generate Obsidian Article Registry Dashboard
Creates a wiki-like article overview that pulls from the database
"""

from phiweaver.tracking.phi_canto_sqlite import PHICantoSQLite
from datetime import datetime, date
import os
from pathlib import Path

class ArticleRegistryGenerator:
    def __init__(self):
        self.db = PHICantoSQLite()
        self.vault_root = str(Path(__file__).resolve().parents[2])
        self.registry_path = f"{self.vault_root}/08-Wiki/Article-Registry.md"

    def generate_registry(self):
        """Generate the complete article registry dashboard"""
        if not self.db.connect():
            print("❌ Failed to connect to database")
            return False

        # Ensure wiki directory exists
        wiki_dir = f"{self.vault_root}/08-Wiki"
        os.makedirs(wiki_dir, exist_ok=True)

        try:
            # Get all data needed
            articles = self._get_articles_data()
            statistics = self._get_statistics()
            recent_activity = self._get_recent_activity()
            token_costs = self._get_token_costs()

            # Generate markdown content
            content = self._generate_dashboard_content(
                articles, statistics, recent_activity, token_costs)

            # Write to file
            with open(self.registry_path, 'w', encoding='utf-8') as f:
                f.write(content)

            print(f"✅ Article Registry generated: 08-Wiki/Article-Registry.md")
            return True

        except Exception as e:
            print(f"❌ Error generating registry: {e}")
            return False
        finally:
            self.db.disconnect()

    def _get_articles_data(self):
        """Get comprehensive article data"""
        self.db.cursor.execute("""
        SELECT
            a.id,
            a.pmid,
            a.title,
            a.journal,
            a.pub_year,
            a.authors,
            a.status,
            a.curator,
            a.priority,
            a.obsidian_note_path,
            a.created_date,
            a.updated_date,
            COUNT(pam.id) as protein_mentions,
            GROUP_CONCAT(p.gene_name, ', ') as proteins
        FROM articles a
        LEFT JOIN protein_article_mentions pam ON a.id = pam.article_id
        LEFT JOIN proteins p ON pam.protein_id = p.id
        GROUP BY a.id
        ORDER BY
            CASE a.status
                WHEN 'in_progress' THEN 1
                WHEN 'queued' THEN 2
                WHEN 'curated' THEN 3
                WHEN 'reviewed' THEN 4
                WHEN 'published' THEN 5
            END,
            a.priority DESC,
            a.pub_year DESC
        """)

        return self.db.cursor.fetchall()

    def _get_statistics(self):
        """Get summary statistics"""
        # Article status counts
        self.db.cursor.execute("""
        SELECT status, COUNT(*) as count
        FROM articles
        GROUP BY status
        """)
        status_stats = {row['status']: row['count'] for row in self.db.cursor.fetchall()}

        # Curator workload
        self.db.cursor.execute("""
        SELECT
            curator,
            COUNT(*) as articles,
            SUM(CASE WHEN status = 'in_progress' THEN 1 ELSE 0 END) as active
        FROM articles
        WHERE curator IS NOT NULL
        GROUP BY curator
        """)
        curator_stats = self.db.cursor.fetchall()

        # Recent productivity
        self.db.cursor.execute("""
        SELECT
            COUNT(*) as sessions,
            SUM(proteins_curated) as proteins,
            SUM(interactions_added) as interactions
        FROM curation_sessions
        WHERE DATE(created_date) >= DATE('now', '-7 days')
        """)
        productivity_stats = self.db.cursor.fetchone()

        return {
            'status': status_stats,
            'curators': curator_stats,
            'productivity': productivity_stats
        }

    def _get_recent_activity(self):
        """Get recent curation activity"""
        self.db.cursor.execute("""
        SELECT
            session_date,
            created_date,
            curator,
            proteins_curated,
            interactions_added,
            notes
        FROM curation_sessions
        ORDER BY created_date DESC
        LIMIT 5
        """)

        return self.db.cursor.fetchall()

    def _get_token_costs(self):
        """Stored per-article token measurements (newest first), or [] if none/absent.

        Reads via phiweaver.article_tokens so each row carries the derived overhead split
        and per-model $ estimate. Safe when the table was never created (no batch recorded
        with --record yet) — token_history creates it empty and returns [].
        """
        try:
            from phiweaver.article_tokens import token_history
            return token_history(Path(self.db.db_path))
        except Exception:
            return []

    def _generate_dashboard_content(self, articles, statistics, recent_activity,
                                    token_costs=None):
        """Generate the markdown content for the dashboard"""
        token_costs = token_costs or []

        content = f"""---
created: {date.today()}
type: registry
tags: [status/active, registry]
auto_generated: true
last_updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
---

# 📚 Article Registry Dashboard

*Auto-generated from database on {datetime.now().strftime('%Y-%m-%d at %H:%M:%S')}*

## 📊 Pipeline Overview

"""

        # Status overview
        status_emojis = {
            'queued': '⚪',
            'in_progress': '🟡',
            'curated': '🟢',
            'reviewed': '🔵',
            'published': '🟣'
        }

        total_articles = sum(statistics['status'].values())
        content += f"**Total Articles**: {total_articles}\n\n"

        for status, emoji in status_emojis.items():
            count = statistics['status'].get(status, 0)
            percentage = (count / total_articles * 100) if total_articles > 0 else 0
            content += f"- {emoji} **{status.title()}**: {count} articles ({percentage:.1f}%)\n"

        # Curator workload
        content += "\n## 👥 Curator Assignments\n\n"
        if statistics['curators']:
            for curator in statistics['curators']:
                content += f"- **{curator['curator']}**: {curator['articles']} total ({curator['active']} active)\n"
        else:
            content += "- No curator assignments yet\n"

        # Recent productivity
        if statistics['productivity']['sessions'] > 0:
            content += f"\n## 📈 Recent Activity (Last 7 Days)\n\n"
            content += f"- **{statistics['productivity']['sessions']}** curation sessions\n"
            content += f"- **{statistics['productivity']['proteins']}** proteins curated\n"
            content += f"- **{statistics['productivity']['interactions']}** interactions added\n"

        # Articles table
        content += f"\n## 📄 Article Pipeline\n\n"
        content += "| Status | Title | PMID | Curator | Proteins | Updated |\n"
        content += "|--------|-------|------|---------|----------|----------|\n"

        for article in articles:
            # Status with emoji
            status_emoji = status_emojis.get(article['status'], '❓')

            # Title with link if note exists
            title = article['title'][:50] + "..." if len(article['title']) > 50 else article['title']
            if article['obsidian_note_path']:
                title = f"[[{article['obsidian_note_path'].replace('.md', '')}|{title}]]"

            # PMID with external link
            pmid_link = f"[{article['pmid']}](https://pubmed.ncbi.nlm.nih.gov/{article['pmid']})" if article['pmid'] else "N/A"

            # Curator
            curator = article['curator'] or "Unassigned"

            # Proteins mentioned
            proteins = article['proteins'] or "None"
            if proteins and len(proteins) > 30:
                proteins = proteins[:30] + "..."

            # Updated date
            updated = article['updated_date'].split(' ')[0] if article['updated_date'] else "N/A"

            content += f"| {status_emoji} | {title} | {pmid_link} | {curator} | {proteins} | {updated} |\n"

        # Recent activity section
        content += f"\n## 🕒 Recent Curation Activity\n\n"
        for activity in recent_activity:
            date_str = activity['created_date'].split(' ')[0]
            time_str = activity['created_date'].split(' ')[1] if ' ' in activity['created_date'] else ''
            content += f"- **{date_str} {time_str}** | {activity['curator']} | "
            content += f"{activity['proteins_curated']} proteins, {activity['interactions_added']} interactions\n"
            if activity['notes']:
                content += f"  *{activity['notes'][:80]}...*\n"

        # Token-cost section (only when at least one batch was recorded with --record)
        if token_costs:
            content += "\n## 💰 Token Costs (per curated article)\n\n"

            # Per-model roll-up: how many measurements and total estimated $ each.
            by_model = {}
            for h in token_costs:
                m = h.get('model') or '?'
                agg = by_model.setdefault(m, {'n': 0, 'cost': 0.0})
                agg['n'] += 1
                agg['cost'] += h.get('cost_usd') or 0.0
            content += "**By model** (all stored measurements): "
            content += "; ".join(
                f"{m} — {a['n']} run(s), ~${a['cost']:.2f}"
                for m, a in sorted(by_model.items())) + "\n\n"

            content += "| PMID | First author-Year | Model | Total tokens | Est. $ | When |\n"
            content += "|------|-------------------|-------|-------------:|-------:|------|\n"
            for h in token_costs[:15]:
                pmid = h.get('pmid') or '—'
                pmid_link = (f"[{pmid}](https://pubmed.ncbi.nlm.nih.gov/{pmid})"
                             if pmid and pmid != '—' else '—')
                cite = h.get('first_author_year') or ''
                model = h.get('model') or '?'
                total = h.get('total_tokens') or 0
                cost = h.get('cost_usd')
                cost_str = f"${cost:.2f}" if cost is not None else "—"
                when = (h.get('computed_at') or '')[:10]
                content += (f"| {pmid_link} | {cite} | {model} | {total:,} "
                            f"| {cost_str} | {when} |\n")
            if len(token_costs) > 15:
                content += f"\n*Showing 15 of {len(token_costs)} measurements.*\n"
            content += ("\n*Direct work + an equal (1/N) share of the batch's shared overhead; "
                        "each bucket priced at its model's list rate (an estimate). Recurations "
                        "on a different model appear as separate rows. "
                        "Source: `phiweaver.article_tokens` (`--record`).*\n")

        # Quick actions section
        content += f"\n## 🚀 Quick Actions\n\n"
        content += "### Curation Workflow\n"
        content += "1. [[08-Wiki/Templates/Article-Template|Use Article Template]] for new literature\n"
        content += "2. [[08-Wiki/Curation-Protocols/Standard-Process|Follow Curation Protocol]]\n"
        content += "3. Use session logger: `python3 session_logger.py quick 'Project' 'Summary' proteins interactions hours`\n\n"

        content += "### Database Commands\n"
        content += "```bash\n"
        content += "# Show progress\n"
        content += "python3 daily_curation.py progress\n\n"
        content += "# Find gaps\n"
        content += "python3 daily_curation.py gaps\n\n"
        content += "# Update this registry\n"
        content += "python3 generate_article_registry.py\n"
        content += "```\n\n"

        # Status legend
        content += "## 📋 Status Legend\n\n"
        content += "| Symbol | Status | Description |\n"
        content += "|--------|--------|-------------|\n"
        content += "| ⚪ | Queued | Added to pipeline, awaiting curation |\n"
        content += "| 🟡 | In Progress | Currently being curated |\n"
        content += "| 🟢 | Curated | Curation completed, ready for review |\n"
        content += "| 🔵 | Reviewed | Quality checked, ready for publication |\n"
        content += "| 🟣 | Published | Data published to PHI-base |\n\n"

        # Footer with regeneration info
        content += f"---\n\n"
        content += f"*This registry is auto-generated from the SQLite database.*  \n"
        content += f"*Regenerate with: `python3 generate_article_registry.py`*  \n"
        content += f"*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"

        return content

def main():
    generator = ArticleRegistryGenerator()
    success = generator.generate_registry()

    if success:
        print("\n🎯 Article Registry Dashboard created!")
        print("📄 Open: 08-Wiki/Article-Registry.md")
        print("🔄 To update: python3 -m phiweaver.tracking.generate_article_registry")
    else:
        print("❌ Failed to generate registry")

if __name__ == "__main__":
    main()