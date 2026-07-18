#!/usr/bin/env python3
"""
Development Timeline Generator for PHI-Canto System
================================================

Automatically generates development timeline from session logs,
filtering for system improvements vs content curation work.

Usage:
    python3 generate_dev_timeline.py [--format bullet|detailed]

Output: Updates DEVELOPMENT-TIMELINE.md with latest development milestones
"""

import os
import re
from datetime import datetime
from pathlib import Path

class DevTimelineGenerator:
    def __init__(self):
        self.vault_root = Path(__file__).resolve().parents[2]  # vault-ops -> 11-CLAUDE-AI -> repo root
        self.session_logs_dir = self.vault_root / "11-CLAUDE-AI" / "SESSION-LOGS"
        self.output_file = self.vault_root / "11-CLAUDE-AI" / "DEVELOPMENT-TIMELINE.md"

        # Development categories (vs content curation)
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

        # Check for development keywords
        dev_score = sum(1 for keyword in self.dev_keywords if keyword in text)
        content_score = sum(1 for keyword in self.content_keywords if keyword in text)

        # If mixed, prioritize by explicit development terms
        development_terms = ['setup', 'system', 'automation', 'infrastructure', 'migration', 'architecture']
        has_dev_terms = any(term in text for term in development_terms)

        return dev_score > content_score or has_dev_terms

    def parse_session_index(self):
        """Parse the session logs index for development sessions"""
        index_file = self.session_logs_dir / "Session-Logs-INDEX.md"

        if not index_file.exists():
            print(f"❌ Session index not found: {index_file}")
            return []

        development_sessions = []

        with open(index_file, 'r') as f:
            content = f.read()

        # Extract table rows (skip header)
        lines = content.split('\n')
        in_table = False

        for line in lines:
            if line.startswith('| Date '):
                in_table = True
                continue
            if line.startswith('|---'):
                continue
            if line.startswith('|') and in_table:
                parts = [p.strip() for p in line.split('|')[1:-1]]  # Remove empty first/last
                if len(parts) >= 4:
                    date, file_link, project, summary = parts[0], parts[1], parts[2], parts[3]

                    if self.is_development_session(project, summary):
                        development_sessions.append({
                            'date': date,
                            'project': project,
                            'summary': summary,
                            'file': file_link.replace('[[', '').replace(']]', '')
                        })
            elif in_table and not line.startswith('|'):
                break  # End of table

        return development_sessions

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

    def generate_bullet_timeline(self, sessions):
        """Generate simple bullet-point timeline"""
        timeline = []

        for session in reversed(sessions):  # Most recent first
            date = session['date']
            project = session['project']
            summary = session['summary']
            category = self.categorize_session(project, summary)

            bullet = f"• **{date}** - {category}: {summary[:80]}{'...' if len(summary) > 80 else ''}"
            timeline.append(bullet)

        return timeline

    def generate_detailed_timeline(self, sessions):
        """Generate detailed timeline with categories and impact"""
        timeline = []
        current_date = None

        for session in reversed(sessions):
            date = session['date']
            project = session['project']
            summary = session['summary']
            category = self.categorize_session(project, summary)

            if date != current_date:
                timeline.append(f"\n## {date}")
                current_date = date

            timeline.append(f"### {category}")
            timeline.append(f"- ✅ **{project}**: {summary}")

        return timeline

    def update_timeline_file(self, format_type="detailed"):
        """Update the development timeline file"""
        sessions = self.parse_session_index()

        if not sessions:
            print("❌ No development sessions found")
            return

        print(f"📊 Found {len(sessions)} development sessions")

        if format_type == "bullet":
            timeline_content = self.generate_bullet_timeline(sessions)
            content = "\n".join(timeline_content)
        else:
            timeline_content = self.generate_detailed_timeline(sessions)
            content = "\n".join(timeline_content)

        # Create header
        header = f"""---
created: {datetime.now().strftime('%Y-%m-%d')}
type: timeline
tags: [development, timeline, auto-generated]
---

# PHI-Canto Development Timeline

*Auto-generated from session logs - System development only (excludes content curation)*

**Last Updated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Development Sessions**: {len(sessions)}

"""

        full_content = header + content + f"""

---

## Timeline Generation

This timeline is automatically generated from session logs using:
```bash
python3 11-CLAUDE-AI/generate_dev_timeline.py
```

**Development Filter Criteria**:
- Infrastructure, automation, system architecture
- Tool development and workflow improvements
- Performance optimizations and migrations
- Documentation and protocol enhancements

**Excluded**: Content curation, literature processing, paper annotations (tracked separately in session logs)

*For complete activity including content work, see: [[SESSION-LOGS/Session-Logs-INDEX]]*
"""

        # Write to file
        try:
            with open(self.output_file, 'w') as f:
                f.write(full_content)
            print(f"✅ Development timeline updated: {self.output_file}")
            print(f"📈 {len(sessions)} development milestones tracked")
        except Exception as e:
            print(f"❌ Error writing timeline: {e}")

def main():
    import sys

    generator = DevTimelineGenerator()

    format_type = "detailed"
    if len(sys.argv) > 1 and sys.argv[1] == "--format":
        format_type = sys.argv[2] if len(sys.argv) > 2 else "detailed"

    generator.update_timeline_file(format_type)

if __name__ == "__main__":
    main()