#!/usr/bin/env python3
"""
PHI-Canto Workflow Helper
Quick commands for common curation workflows
"""

import sys
import os
from phiweaver.tracking.session_logger import SessionLogger, quick_session

def show_help():
    print("🚀 PHI-Canto Workflow Helper")
    print("=" * 40)
    print("Commands:")
    print("  start-session    - Begin new curation session")
    print("  end-session      - End current session with logging")
    print("  add-article      - Add new article to pipeline")
    print("  add-protein      - Add new protein to tracking")
    print("  status           - Show current progress")
    print("  gaps             - Show data needing attention")
    print("  help             - Show this help")
    print()
    print("Session workflow:")
    print("  1. workflow_helper.py start-session 'Project Name'")
    print("  2. [Do your curation work in Obsidian]")
    print("  3. workflow_helper.py end-session 'Summary' 3 5 2.0")
    print()

def start_session(project_name):
    """Start a new curation session"""
    from datetime import date
    print(f"🚀 Starting curation session: {project_name}")
    print(f"📅 Date: {date.today()}")
    print()
    print("📋 Workflow reminders:")
    print("- Take notes in Obsidian as usual")
    print("- Track your progress (proteins, interactions, experiments)")
    print("- When done, run: workflow_helper.py end-session 'Summary' [proteins] [interactions] [hours]")
    print()
    print("💡 Database tracking will happen automatically when you end the session!")

def end_session(project, summary, proteins=0, interactions=0, hours=None):
    """End curation session with automatic logging"""
    print(f"📊 Ending curation session: {project}")

    result = quick_session(project, summary, proteins, interactions, hours)

    if result:
        print(f"\n✅ Session completed successfully!")
        print(f"📄 Session log: {result['log_file']}")
        print(f"📊 Database session ID: {result['session_id']}")
        print(f"🎯 Proteins curated: {proteins}")
        print(f"🎯 Interactions added: {interactions}")
        if hours:
            print(f"⏱️  Duration: {hours} hours")
        print()
        print("💡 Both markdown session log AND database have been updated!")
    else:
        print("❌ Session logging failed")

def show_status():
    """Show current curation status"""
    os.system("python3 daily_curation.py progress")

def show_gaps():
    """Show data gaps needing attention"""
    os.system("python3 daily_curation.py gaps")

if __name__ == "__main__":
    from datetime import datetime

    if len(sys.argv) < 2:
        show_help()
        sys.exit()

    command = sys.argv[1]

    if command == "start-session":
        project = sys.argv[2] if len(sys.argv) > 2 else "PHI-Canto curation"
        start_session(project)

    elif command == "end-session":
        if len(sys.argv) < 4:
            print("Usage: workflow_helper.py end-session 'Project' 'Summary' [proteins] [interactions] [hours]")
            sys.exit(1)

        project = sys.argv[2]
        summary = sys.argv[3]
        proteins = int(sys.argv[4]) if len(sys.argv) > 4 else 0
        interactions = int(sys.argv[5]) if len(sys.argv) > 5 else 0
        hours = float(sys.argv[6]) if len(sys.argv) > 6 else None

        end_session(project, summary, proteins, interactions, hours)

    elif command == "status":
        show_status()

    elif command == "gaps":
        show_gaps()

    elif command == "help":
        show_help()

    else:
        print(f"Unknown command: {command}")
        show_help()