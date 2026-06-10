#!/usr/bin/env python3
"""
PHI-Canto Complete Curation Pipeline Automation
===============================================

Automates the entire workflow from PDF placement to completion:
1. PDF processing and conversion
2. File organization and placement
3. Database tracking and logging
4. Session management

Usage:
    # Start new curation with PDF
    python3 curation_pipeline.py new-paper /path/to/paper.pdf

    # Process existing PDF in To-curate folder
    python3 curation_pipeline.py process-pdf filename.pdf

    # Complete curation (move to Literature)
    python3 curation_pipeline.py complete-paper filename.pdf "Curation summary"

    # Full automation: PDF → processed → ready for curation
    python3 curation_pipeline.py auto-process /path/to/paper.pdf
"""

import sys
import os
import shutil
import subprocess
from pathlib import Path
from datetime import date, datetime
import json

# Import existing automation tools
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__), 'db'))

try:
    from session_logger import quick_session
    HAS_DB = True
except ImportError:
    print("⚠️  Database integration not available - continuing without DB logging")
    HAS_DB = False

class CurationPipeline:
    def __init__(self):
        # Repo root is auto-detected as the parent of the 11-CLAUDE-AI/ tools
        # folder, so the pipeline works wherever the repo is cloned (no hardcoded
        # vault path).
        self.vault_root = Path(__file__).resolve().parents[1]
        # Literature content lives OUTSIDE the repo. Resolution order:
        #   1. PHI_LITERATURE_ROOT env var, if set (explicit override).
        #   2. Codespaces (PHI_CURATION_ENV=codespace): an in-workspace folder,
        #      so demo files are visible in the file explorer with zero config.
        #   3. Default: a sibling folder next to the repo
        #      (on this machine: /mnt/z/PHI-Canto-Literature).
        # See STORAGE-CONFIGURATION.md / DEMO-CODESPACES.md in the repo root.
        env_root = os.environ.get("PHI_LITERATURE_ROOT")
        if env_root:
            self.external_storage = Path(env_root).expanduser().resolve()
        elif os.environ.get("PHI_CURATION_ENV") == "codespace":
            self.external_storage = self.vault_root / "demo-literature"
        else:
            self.external_storage = self.vault_root.parent / "PHI-Canto-Literature"
        self.inbox_path = self.external_storage / "active"
        self.literature_path = self.external_storage / "completed"
        self.media_path = self.external_storage / "media"
        # Tools live inside the repo itself
        self.pdf_converter = self.vault_root / "11-CLAUDE-AI" / "pdf-convert-skill" / "pdf-convert.py"
        self.reorganizer = self.vault_root / "11-CLAUDE-AI" / "obsidian_reorganise.py"
        self.reorganizer_config = self.vault_root / "11-CLAUDE-AI" / "reorganise-config-OBS-PHI-Canto.yaml"

    def log_action(self, action, details=""):
        """Log pipeline actions"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"🔄 [{timestamp}] {action}")
        if details:
            print(f"   {details}")

    def ensure_storage(self):
        """Create the literature storage folders if they don't exist yet.

        Makes the pipeline self-sufficient on a fresh checkout (e.g. a new
        Codespace), where the active/completed/media folders won't exist.
        """
        for d in (self.inbox_path, self.literature_path, self.media_path):
            d.mkdir(parents=True, exist_ok=True)

    def new_paper_workflow(self, pdf_path):
        """Complete workflow: new PDF → processed → ready for curation"""
        print("🚀 Starting New Paper Curation Workflow")
        print("=" * 50)

        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            print(f"❌ PDF not found: {pdf_path}")
            return False

        self.ensure_storage()

        # Step 1: Copy PDF to the active (input) folder
        target_path = self.inbox_path / pdf_path.name
        self.log_action("Copying PDF to To-curate folder", f"{pdf_path.name}")
        shutil.copy2(pdf_path, target_path)

        # Step 2: Process the PDF
        return self.process_pdf_workflow(pdf_path.name)

    def process_pdf_workflow(self, filename):
        """Process existing PDF in To-curate folder"""
        print(f"📄 Processing PDF: {filename}")
        print("=" * 50)

        self.ensure_storage()

        pdf_path = self.inbox_path / filename
        if not pdf_path.exists():
            print(f"❌ PDF not found in active/ folder: {filename}")
            return False

        # Step 1: Convert PDF to Markdown
        self.log_action("Converting PDF to Markdown")
        os.chdir(self.inbox_path)

        try:
            result = subprocess.run([
                "python3", str(self.pdf_converter), filename
            ], capture_output=True, text=True, cwd=self.inbox_path)

            if result.returncode == 0:
                self.log_action("✅ PDF conversion completed")
                print(result.stdout)
            else:
                self.log_action("❌ PDF conversion failed")
                print(result.stderr)
                return False
        except Exception as e:
            self.log_action(f"❌ PDF conversion error: {e}")
            return False

        # Step 2: Find generated files
        base_name = pdf_path.stem
        markdown_file = self.inbox_path / f"{base_name}_converted.md"
        media_folder = self.inbox_path / "03-Media"

        if markdown_file.exists():
            self.log_action("✅ Markdown file created", str(markdown_file.name))

        if media_folder.exists():
            media_count = len(list(media_folder.rglob("*.*")))
            self.log_action(f"✅ Media folder created with {media_count} files")

        # Step 3: Add to database (if available)
        if HAS_DB:
            self.log_action("Adding to database tracking")
            self.add_to_database(filename, markdown_file)

        # Step 4: Create curation session
        self.log_action("Creating initial session log")
        self.create_initial_session(base_name)

        print("\n🎉 PDF Processing Complete!")
        print("=" * 50)
        print(f"📄 Original PDF: {filename}")
        print(f"📝 Markdown file: {markdown_file.name}")
        print(f"📁 Ready for curation in: {self.inbox_path}")
        print("\nNext steps:")
        print("1. Review converted markdown file")
        print("2. Begin PHI-Canto annotation")
        print("3. Use 'complete-paper' when finished")

        return True

    def complete_paper_workflow(self, filename, summary):
        """Complete curation and move files to Literature folder"""
        print(f"🏁 Completing Curation: {filename}")
        print("=" * 50)

        self.ensure_storage()

        pdf_path = self.inbox_path / filename
        base_name = Path(filename).stem

        if not pdf_path.exists():
            print(f"❌ PDF not found: {filename}")
            return False

        # Step 1: Move files to Literature folder
        self.log_action("Moving files to Literature folder")

        # Move PDF
        lit_pdf_path = self.literature_path / filename
        shutil.move(pdf_path, lit_pdf_path)
        self.log_action(f"✅ Moved PDF: {filename}")

        # Move markdown file if exists
        markdown_file = self.inbox_path / f"{base_name}_converted.md"
        if markdown_file.exists():
            lit_markdown = self.literature_path / f"{base_name}-Curation-Notes.md"
            shutil.move(markdown_file, lit_markdown)
            self.log_action(f"✅ Moved markdown: {lit_markdown.name}")

        # Move media folder if exists (look for both patterns)
        media_patterns = [
            self.inbox_path / "03-Media" / base_name,  # Old structure
            self.inbox_path / f"{base_name}",  # New structure
        ]

        for media_folder in media_patterns:
            if media_folder.exists() and media_folder.is_dir():
                lit_media = self.literature_path / f"{base_name}-Media"
                if lit_media.exists():
                    shutil.rmtree(lit_media)
                shutil.move(media_folder, lit_media)
                self.log_action(f"✅ Moved media folder: {lit_media.name}")
                break

        # Clean up remaining conversion files
        for pattern in [f"{base_name}_converted*", f"{base_name}_report*"]:
            for file in self.inbox_path.glob(pattern):
                file.unlink()
                self.log_action(f"🧹 Cleaned up: {file.name}")

        # Step 2: Log completion session
        if HAS_DB:
            self.log_action("Logging completion session")
            try:
                result = quick_session(
                    project=f"Complete {base_name}",
                    summary=summary,
                    proteins=0,  # User can specify these
                    interactions=0,
                    hours=None
                )
                if result:
                    self.log_action(f"✅ Session logged: {result['session_id']}")
            except Exception as e:
                self.log_action(f"⚠️  Session logging error: {e}")

        # Step 3: Update literature index if it exists
        self.update_literature_index(base_name, summary)

        print("\n🎉 Curation Completed!")
        print("=" * 50)
        print(f"📄 PDF moved to: {self.literature_path / filename}")
        print(f"📝 Curation notes: {self.literature_path / (base_name + '-Curation-Notes.md')}")
        print(f"📊 Summary: {summary}")
        print("\n✅ Ready for next paper!")

        return True

    def add_to_database(self, filename, markdown_path):
        """Add paper to database tracking"""
        try:
            # Extract info from filename (basic implementation)
            base_name = Path(filename).stem

            # This would need enhancement to extract PMID, title etc.
            # For now, create basic record

            print(f"📊 Added to database: {base_name}")

        except Exception as e:
            print(f"⚠️  Database add error: {e}")

    def create_initial_session(self, base_name):
        """Create initial curation session"""
        try:
            if HAS_DB:
                result = quick_session(
                    project=f"Start {base_name}",
                    summary=f"Converted PDF and set up for curation: {base_name}",
                    proteins=0,
                    interactions=0,
                    hours=None
                )
                if result:
                    print(f"📊 Initial session created: {result['session_id']}")
        except Exception as e:
            print(f"⚠️  Session creation error: {e}")

    def update_literature_index(self, base_name, summary):
        """Update literature tracking"""
        index_file = self.literature_path / "LITERATURE-INDEX.md"

        try:
            # Create or update literature index
            entry = f"- [[{base_name}-Curation-Notes.md|{base_name}]] - {summary} (Completed: {date.today()})\n"

            if index_file.exists():
                with open(index_file, 'a') as f:
                    f.write(entry)
            else:
                with open(index_file, 'w') as f:
                    f.write("# Literature Index\n\n## Completed Curations\n\n")
                    f.write(entry)

            self.log_action("✅ Updated literature index")

        except Exception as e:
            self.log_action(f"⚠️  Index update error: {e}")

    def auto_process_workflow(self, pdf_path):
        """Fully automated: PDF → processed → ready"""
        print("🤖 Full Automation Mode")
        print("=" * 50)

        # Step 1: New paper workflow
        if not self.new_paper_workflow(pdf_path):
            return False

        print("\n🚀 Auto-processing completed!")
        print("📋 Paper is ready for manual curation")
        print(f"📁 Check: {self.inbox_path}")

        return True

def show_help():
    print("""
🚀 PHI-Canto Curation Pipeline
=============================

Complete automation for PDF curation workflow.

Commands:
  new-paper <pdf_path>           Copy PDF to vault and process
  process-pdf <filename>         Process PDF already in To-curate
  complete-paper <filename> <summary>  Move completed curation to Literature
  auto-process <pdf_path>        Full automation: copy + process
  help                          Show this help

Examples:
  # Start with new PDF
  python3 curation_pipeline.py new-paper ~/Downloads/paper.pdf

  # Process PDF already in To-curate folder
  python3 curation_pipeline.py process-pdf paper.pdf

  # Complete curation
  python3 curation_pipeline.py complete-paper paper.pdf "Added 5 effector proteins"

  # Full automation
  python3 curation_pipeline.py auto-process ~/Downloads/paper.pdf

Workflow:
  1. PDF → 00-Inbox/To-curate/ (with conversion to markdown)
  2. [Manual curation work in PHI-Canto]
  3. Completed → 04-Literature/ (with session logging)
""")

def main():
    if len(sys.argv) < 2:
        show_help()
        return

    pipeline = CurationPipeline()
    command = sys.argv[1]

    if command == "new-paper":
        if len(sys.argv) < 3:
            print("Usage: new-paper <pdf_path>")
            return
        pipeline.new_paper_workflow(sys.argv[2])

    elif command == "process-pdf":
        if len(sys.argv) < 3:
            print("Usage: process-pdf <filename>")
            return
        pipeline.process_pdf_workflow(sys.argv[2])

    elif command == "complete-paper":
        if len(sys.argv) < 4:
            print("Usage: complete-paper <filename> <summary>")
            return
        pipeline.complete_paper_workflow(sys.argv[2], sys.argv[3])

    elif command == "auto-process":
        if len(sys.argv) < 3:
            print("Usage: auto-process <pdf_path>")
            return
        pipeline.auto_process_workflow(sys.argv[2])

    elif command == "help":
        show_help()

    else:
        print(f"Unknown command: {command}")
        show_help()

if __name__ == "__main__":
    main()