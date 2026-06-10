#!/usr/bin/env python3
"""
Integrated PHI-Canto Session Logger
Automatically updates both markdown session log AND SQLite database
"""

from phi_canto_sqlite import PHICantoSQLite
from datetime import datetime, date
import os
import sys
from pathlib import Path

class SessionLogger:
    def __init__(self):
        self.db = PHICantoSQLite()
        self.vault_root = str(Path(__file__).resolve().parents[2])
        self.session_logs_dir = "11-CLAUDE-AI/SESSION-LOGS"
        self.curator = "martin.urban"

    def create_session_log(self, project_name, objectives, tasks_completed,
                          files_modified=None, git_commits=None,
                          proteins_curated=0, interactions_added=0,
                          experiments_annotated=0, session_duration_hours=None,
                          articles_added=None, articles_updated=None,
                          new_species=None, notes=None):
        """
        Create comprehensive session log with automatic database updates

        Args:
            project_name: Name of the project being worked on
            objectives: List of session objectives
            tasks_completed: List of completed tasks
            files_modified: List of modified files
            git_commits: List of git commits made
            proteins_curated: Number of proteins curated
            interactions_added: Number of interactions added
            experiments_annotated: Number of experiments annotated
            session_duration_hours: Duration of session in hours
            articles_added: List of new articles added (dict with pmid, title, etc.)
            articles_updated: List of articles with status updates (dict with pmid, status)
            new_species: List of new species added (dict with name, type, etc.)
            notes: Additional notes
        """

        session_date = date.today()
        session_datetime = datetime.now()

        # Generate session log filename
        filename = f"{session_date}-{project_name.lower().replace(' ', '-')}"

        # Check if filename exists and append number if needed
        counter = 2
        base_filename = filename
        while os.path.exists(f"{self.vault_root}/{self.session_logs_dir}/{filename}.md"):
            filename = f"{base_filename}-{counter}"
            counter += 1

        log_filepath = f"{self.vault_root}/{self.session_logs_dir}/{filename}.md"
        relative_log_path = f"{self.session_logs_dir}/{filename}.md"

        # Connect to database
        if not self.db.connect():
            print("❌ Failed to connect to database")
            return None

        try:
            # 1. UPDATE DATABASE FIRST
            print("📊 Updating database...")

            # Add new species if provided
            species_ids = {}
            if new_species:
                for species in new_species:
                    species_id = self._add_species_to_db(species)
                    if species_id:
                        species_ids[species['name']] = species_id

            # Add new articles if provided
            article_ids = {}
            if articles_added:
                for article in articles_added:
                    article_id = self._add_article_to_db(article)
                    if article_id:
                        article_ids[article.get('pmid', article['title'])] = article_id

            # Update article statuses if provided
            if articles_updated:
                for update in articles_updated:
                    self._update_article_status_in_db(update['pmid'], update['status'])

            # Log the curation session
            session_id = self._log_session_to_db(
                session_date, proteins_curated, interactions_added,
                experiments_annotated, session_duration_hours,
                notes, relative_log_path
            )

            print(f"✅ Database updated - Session ID: {session_id}")

            # 2. CREATE MARKDOWN SESSION LOG
            print("📝 Creating session log markdown...")

            markdown_content = self._generate_session_markdown(
                session_date, project_name, objectives, tasks_completed,
                files_modified, git_commits, proteins_curated,
                interactions_added, experiments_annotated,
                session_duration_hours, articles_added, articles_updated,
                new_species, notes, session_id
            )

            # Write markdown file
            with open(log_filepath, 'w', encoding='utf-8') as f:
                f.write(markdown_content)

            print(f"✅ Session log created: {relative_log_path}")

            # 3. UPDATE SESSION LOGS INDEX
            self._update_session_index(filename, project_name, tasks_completed)

            print("✅ Session logs index updated")

            # 4. AUTO-REGENERATE WIKI ARTICLE REGISTRY
            self._update_wiki_registry()

            return {
                'log_file': relative_log_path,
                'session_id': session_id,
                'database_updated': True,
                'wiki_updated': True
            }

        except Exception as e:
            print(f"❌ Error during session logging: {e}")
            return None
        finally:
            self.db.disconnect()

    def _add_species_to_db(self, species):
        """Add species to database"""
        try:
            self.db.cursor.execute("""
                INSERT INTO species (name, type, taxonomy_id, common_name, notes)
                VALUES (?, ?, ?, ?, ?)
            """, (
                species['name'], species['type'],
                species.get('taxonomy_id'), species.get('common_name'),
                species.get('notes')
            ))
            self.db.connection.commit()
            species_id = self.db.cursor.lastrowid
            print(f"   ✅ Added species: {species['name']}")
            return species_id
        except Exception as e:
            print(f"   ❌ Error adding species {species['name']}: {e}")
            return None

    def _add_article_to_db(self, article):
        """Add article to database"""
        try:
            self.db.cursor.execute("""
                INSERT INTO articles (pmid, title, journal, pub_year, authors, status, curator, obsidian_note_path)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                article.get('pmid'), article['title'],
                article.get('journal'), article.get('pub_year'),
                article.get('authors'), article.get('status', 'queued'),
                self.curator, article.get('obsidian_note_path')
            ))
            self.db.connection.commit()
            article_id = self.db.cursor.lastrowid
            print(f"   ✅ Added article: {article['title'][:50]}...")
            return article_id
        except Exception as e:
            print(f"   ❌ Error adding article: {e}")
            return None

    def _update_article_status_in_db(self, pmid, status):
        """Update article status in database"""
        try:
            self.db.cursor.execute("""
                UPDATE articles SET status = ?, updated_date = CURRENT_TIMESTAMP
                WHERE pmid = ?
            """, (status, pmid))
            self.db.connection.commit()
            if self.db.cursor.rowcount > 0:
                print(f"   ✅ Updated PMID {pmid} status to: {status}")
            return True
        except Exception as e:
            print(f"   ❌ Error updating article status: {e}")
            return False

    def _log_session_to_db(self, session_date, proteins_curated, interactions_added,
                          experiments_annotated, session_duration_hours, notes, log_path):
        """Log session to database"""
        try:
            self.db.cursor.execute("""
                INSERT INTO curation_sessions
                (session_date, curator, session_duration_hours, proteins_curated,
                 interactions_added, experiments_annotated, notes, obsidian_session_log)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                session_date, self.curator, session_duration_hours,
                proteins_curated, interactions_added, experiments_annotated,
                notes, log_path
            ))
            self.db.connection.commit()
            return self.db.cursor.lastrowid
        except Exception as e:
            print(f"   ❌ Error logging session: {e}")
            return None

    def _generate_session_markdown(self, session_date, project_name, objectives,
                                 tasks_completed, files_modified, git_commits,
                                 proteins_curated, interactions_added,
                                 experiments_annotated, session_duration_hours,
                                 articles_added, articles_updated, new_species,
                                 notes, session_id):
        """Generate session log markdown content"""

        content = f"""---
created: {session_date}
type: session-log
tags: [status/complete]
project: {project_name}
session_id: {session_id}
---

# Session: {project_name}

## Objectives
"""

        if isinstance(objectives, list):
            for obj in objectives:
                content += f"- {obj}\n"
        else:
            content += f"{objectives}\n"

        content += "\n## Tasks Completed\n"
        if isinstance(tasks_completed, list):
            for task in tasks_completed:
                content += f"- {task}\n"
        else:
            content += f"{tasks_completed}\n"

        if files_modified:
            content += "\n## Files Modified\n"
            if isinstance(files_modified, list):
                for file in files_modified:
                    content += f"- `{file}`\n"
            else:
                content += f"- `{files_modified}`\n"

        # Database updates section
        content += f"\n## Database Updates\n"
        content += f"- **Session logged**: ID {session_id}\n"
        content += f"- **Proteins curated**: {proteins_curated}\n"
        content += f"- **Interactions added**: {interactions_added}\n"
        content += f"- **Experiments annotated**: {experiments_annotated}\n"

        if session_duration_hours:
            content += f"- **Session duration**: {session_duration_hours} hours\n"

        if new_species:
            content += f"- **Species added**: {len(new_species)} ({', '.join([s['name'] for s in new_species])})\n"

        if articles_added:
            content += f"- **Articles added**: {len(articles_added)}\n"
            for article in articles_added:
                content += f"  - {article['title'][:60]}... (PMID: {article.get('pmid', 'N/A')})\n"

        if articles_updated:
            content += f"- **Articles updated**: {len(articles_updated)}\n"
            for update in articles_updated:
                content += f"  - PMID {update['pmid']} → {update['status']}\n"

        if git_commits:
            content += "\n## Git Commits Made\n"
            if isinstance(git_commits, list):
                for commit in git_commits:
                    content += f"- `{commit}`\n"
            else:
                content += f"- `{git_commits}`\n"

        if notes:
            content += f"\n## Notes\n{notes}\n"

        content += f"\n## Session Summary\n"
        summary = f"Completed {project_name} curation session with {proteins_curated} proteins curated, "
        summary += f"{interactions_added} interactions added"
        if experiments_annotated > 0:
            summary += f", and {experiments_annotated} experiments annotated"
        summary += ". Database automatically updated with session progress and new entries."

        content += summary

        return content

    def _update_session_index(self, filename, project_name, tasks_completed):
        """Update the session logs index"""
        index_path = f"{self.vault_root}/{self.session_logs_dir}/INDEX.md"

        # Generate summary from tasks
        if isinstance(tasks_completed, list):
            summary = ", ".join(tasks_completed[:3])  # First 3 tasks
            if len(tasks_completed) > 3:
                summary += f", +{len(tasks_completed) - 3} more"
        else:
            summary = str(tasks_completed)[:80]

        # Read current index
        try:
            with open(index_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Find the table and add new entry
            lines = content.split('\n')
            table_end = -1

            # Find where to insert (after the last table row)
            for i, line in enumerate(lines):
                if line.startswith('|') and '|' in line and 'Date' not in line and '---' not in line:
                    table_end = i

            new_entry = f"| {date.today()} | [[{filename}]] | {project_name} | {summary} |"

            if table_end >= 0:
                lines.insert(table_end + 1, new_entry)
            else:
                # If no table found, append to end
                lines.append(new_entry)

            # Write back
            with open(index_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))

        except Exception as e:
            print(f"   ⚠️  Warning: Could not update session index: {e}")

    def _update_wiki_registry(self):
        """Auto-regenerate the wiki article registry"""
        try:
            # Import and run the registry generator
            import sys
            import os

            # Add the current directory to Python path for import
            current_dir = os.path.dirname(os.path.abspath(__file__))
            if current_dir not in sys.path:
                sys.path.insert(0, current_dir)

            from generate_article_registry import ArticleRegistryGenerator

            generator = ArticleRegistryGenerator()
            if generator.generate_registry():
                print("✅ Wiki article registry auto-updated")
            else:
                print("⚠️  Warning: Could not update wiki registry")

        except Exception as e:
            print(f"⚠️  Warning: Could not update wiki registry: {e}")

def quick_session(project, summary, proteins=0, interactions=0, hours=None):
    """Quick session logger for simple updates"""
    logger = SessionLogger()

    return logger.create_session_log(
        project_name=project,
        objectives=[f"Continue {project} curation work"],
        tasks_completed=[summary],
        proteins_curated=proteins,
        interactions_added=interactions,
        experiments_annotated=0,
        session_duration_hours=hours,
        notes=f"Quick session update: {summary}"
    )

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("🚀 PHI-Canto Integrated Session Logger")
        print("=" * 40)
        print("Usage:")
        print("  python3 session_logger.py quick 'Project' 'Summary' [proteins] [interactions] [hours]")
        print("  python3 session_logger.py example  # Show example usage")
        print()
        print("Example:")
        print("  python3 session_logger.py quick 'Fusarium effectors' 'Added FgNEW1 characterization' 2 3 1.5")
        sys.exit()

    if sys.argv[1] == "quick":
        project = sys.argv[2]
        summary = sys.argv[3]
        proteins = int(sys.argv[4]) if len(sys.argv) > 4 else 0
        interactions = int(sys.argv[5]) if len(sys.argv) > 5 else 0
        hours = float(sys.argv[6]) if len(sys.argv) > 6 else None

        result = quick_session(project, summary, proteins, interactions, hours)
        if result:
            print(f"\n✅ Session logged successfully!")
            print(f"📄 Log file: {result['log_file']}")
            print(f"📊 Database session ID: {result['session_id']}")

    elif sys.argv[1] == "example":
        print("📋 Example of comprehensive session logging:")
        print()
        logger = SessionLogger()
        result = logger.create_session_log(
            project_name="Fusarium effectors",
            objectives=[
                "Characterize FgNEW1 effector protein",
                "Update literature review with 2024 papers",
                "Add UniProt mappings for existing proteins"
            ],
            tasks_completed=[
                "Completed functional analysis of FgNEW1",
                "Added 3 new research papers to literature database",
                "Updated 5 proteins with UniProt accession numbers"
            ],
            files_modified=[
                "02-Projects/Fusarium-effectors/proteins/FgNEW1.md",
                "04-Literature/fgnew1-characterization-2024.md"
            ],
            git_commits=["Add FgNEW1 protein characterization and literature"],
            proteins_curated=3,
            interactions_added=7,
            experiments_annotated=12,
            session_duration_hours=2.5,
            articles_added=[
                {
                    'pmid': '38999999',
                    'title': 'Novel characterization of FgNEW1 effector',
                    'journal': 'Molecular Plant Pathology',
                    'pub_year': 2024,
                    'status': 'in_progress'
                }
            ],
            articles_updated=[
                {'pmid': '38456789', 'status': 'curated'}
            ],
            notes="Significant progress on FgNEW1 characterization. Ready for validation experiments."
        )

        if result:
            print(f"✅ Example session logged: {result['log_file']}")
        else:
            print("❌ Example session failed")

    else:
        print(f"Unknown command: {sys.argv[1]}")
        print("Use 'quick' or 'example'")