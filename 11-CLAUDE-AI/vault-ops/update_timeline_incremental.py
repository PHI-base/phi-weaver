#!/usr/bin/env python3
"""
Incremental Development Timeline Updater
=======================================

Adds only new development sessions to existing timeline,
preserving manual edits and custom content.

Usage:
    python3 update_timeline_incremental.py [--check-only]

Features:
- Preserves existing timeline content
- Only adds new sessions not already tracked
- Maintains manual edits and customizations
- Provides dry-run option to preview changes
"""

import os
import re
from datetime import datetime
from pathlib import Path

class IncrementalTimelineUpdater:
    def __init__(self):
        self.vault_root = Path(__file__).resolve().parents[2]  # vault-ops -> 11-CLAUDE-AI -> repo root
        self.session_logs_dir = self.vault_root / "11-CLAUDE-AI" / "SESSION-LOGS"
        self.timeline_file = self.vault_root / "11-CLAUDE-AI" / "DEVELOPMENT-TIMELINE.md"

        # Development session criteria
        self.dev_keywords = [
            'setup', 'infrastructure', 'automation', 'pipeline', 'system',
            'architecture', 'database', 'integration', 'migration', 'performance',
            'framework', 'tool', 'workflow', 'documentation', 'protocol'
        ]

        self.content_keywords = [
            'curation', 'effector', 'protein', 'literature', 'paper', 'pmid'
        ]

    def is_development_session(self, project, summary):
        """Determine if session is system development vs content curation"""
        text = f"{project} {summary}".lower()

        dev_score = sum(1 for keyword in self.dev_keywords if keyword in text)
        content_score = sum(1 for keyword in self.content_keywords if keyword in text)

        development_terms = ['setup', 'system', 'automation', 'infrastructure', 'migration', 'architecture']
        has_dev_terms = any(term in text for term in development_terms)

        return dev_score > content_score or has_dev_terms

    def get_existing_timeline_sessions(self):
        """Extract sessions already in timeline"""
        if not self.timeline_file.exists():
            return set()

        existing_sessions = set()

        with open(self.timeline_file, 'r') as f:
            content = f.read()

        # Look for session entries in format: - ✅ **Project**: Description
        session_pattern = r'- ✅ \*\*(.*?)\*\*:'
        matches = re.findall(session_pattern, content)

        for match in matches:
            existing_sessions.add(match.strip())

        return existing_sessions

    def parse_new_sessions(self):
        """Get new development sessions not in timeline"""
        # Parse all sessions from index
        index_file = self.session_logs_dir / "INDEX.md"
        if not index_file.exists():
            return []

        all_sessions = []
        existing_sessions = self.get_existing_timeline_sessions()

        with open(index_file, 'r') as f:
            content = f.read()

        # Extract table rows
        lines = content.split('\n')
        in_table = False

        for line in lines:
            if line.startswith('| Date '):
                in_table = True
                continue
            if line.startswith('|---'):
                continue
            if line.startswith('|') and in_table:
                parts = [p.strip() for p in line.split('|')[1:-1]]
                if len(parts) >= 4:
                    date, file_link, project, summary = parts[0], parts[1], parts[2], parts[3]

                    # Check if development session and not already in timeline
                    if (self.is_development_session(project, summary) and
                        project not in existing_sessions):
                        all_sessions.append({
                            'date': date,
                            'project': project,
                            'summary': summary,
                            'file': file_link.replace('[[', '').replace(']]', '')
                        })
            elif in_table and not line.startswith('|'):
                break

        return all_sessions

    def categorize_session(self, project, summary):
        """Categorize development session type"""
        text = f"{project} {summary}".lower()

        if any(term in text for term in ['setup', 'initialization', 'foundation']):
            return "Infrastructure"
        elif any(term in text for term in ['automation', 'pipeline', 'workflow']):
            return "Automation"
        elif any(term in text for term in ['architecture', 'migration', 'modular']):
            return "Architecture"
        elif any(term in text for term in ['database', 'tracking', 'analytics']):
            return "Analytics"
        elif any(term in text for term in ['documentation', 'protocol', 'training']):
            return "Knowledge Management"
        else:
            return "System Enhancement"

    def format_new_session(self, session):
        """Format new session for timeline insertion"""
        date = session['date']
        project = session['project']
        summary = session['summary']
        category = self.categorize_session(project, summary)

        # Create timeline entry
        entry = f"""
## {date}
### {category}
- ✅ **{project}**: {summary}
"""
        return entry.strip()

    def find_insertion_point(self, content, new_date):
        """Find where to insert new session (chronological order)"""
        lines = content.split('\n')

        # Find insertion point (timelines are newest first)
        for i, line in enumerate(lines):
            if line.startswith('## 2026-') or line.startswith('## 2025-'):
                existing_date = line.replace('## ', '').strip()
                if new_date >= existing_date:
                    return i

        # If no dates found, insert after header
        for i, line in enumerate(lines):
            if line.strip() == '' and i > 15:  # After frontmatter and header
                return i

        return len(lines)

    def update_timeline(self, new_sessions, check_only=False):
        """Add new sessions to timeline incrementally"""
        if not new_sessions:
            print("✅ Timeline is up to date - no new development sessions found")
            return

        print(f"📊 Found {len(new_sessions)} new development sessions to add:")
        for session in new_sessions:
            print(f"  • {session['date']}: {session['project']}")

        if check_only:
            print("\n🔍 CHECK-ONLY MODE: Would add these sessions to timeline")
            for session in new_sessions:
                print(f"\n{self.format_new_session(session)}")
            return

        # Read existing timeline
        if self.timeline_file.exists():
            with open(self.timeline_file, 'r') as f:
                content = f.read()
        else:
            # Create new timeline if it doesn't exist
            content = f"""---
created: {datetime.now().strftime('%Y-%m-%d')}
type: timeline
tags: [development, timeline, incremental]
---

# PHI-Canto Development Timeline

*Incrementally updated - System development milestones*

**Last Updated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

"""

        # Add new sessions in chronological order (newest first)
        new_sessions.sort(key=lambda x: x['date'], reverse=True)

        for session in new_sessions:
            new_entry = self.format_new_session(session)
            insertion_point = self.find_insertion_point(content, session['date'])

            lines = content.split('\n')
            lines.insert(insertion_point, new_entry)
            content = '\n'.join(lines)

        # Update timestamp in header
        content = re.sub(
            r'\*\*Last Updated\*\*: .*',
            f"**Last Updated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            content
        )

        # Write updated timeline
        with open(self.timeline_file, 'w') as f:
            f.write(content)

        print(f"\n✅ Timeline updated with {len(new_sessions)} new sessions")
        print(f"📁 Updated: {self.timeline_file}")

def main():
    import sys

    updater = IncrementalTimelineUpdater()

    check_only = '--check-only' in sys.argv
    new_sessions = updater.parse_new_sessions()
    updater.update_timeline(new_sessions, check_only)

if __name__ == "__main__":
    main()