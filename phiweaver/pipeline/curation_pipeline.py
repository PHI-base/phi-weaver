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
import re
import shutil
import subprocess
from pathlib import Path
from datetime import date, datetime
import json

from phiweaver import repo_root

try:
    from phiweaver.tracking.session_logger import quick_session
    from phiweaver.tracking.phi_canto_sqlite import PHICantoSQLite
    HAS_DB = True
except ImportError:
    print("⚠️  Database integration not available - continuing without DB logging")
    HAS_DB = False

# Fungal-style locus tags (e.g. FGSG_11164) — a real, content-derived protein signal,
# since papers in this corpus often cite proteins by locus tag rather than accession.
LOCUS_TAG_RE = re.compile(r"\b[A-Z]{2,6}_\d{4,6}\b")


# Curation notes list pathogen–host interactions as bullet entries under an
# "Interactions…" heading (see 08-Wiki/Templates/Article-Template.md). Those explicit
# entries are counted deterministically — interactions are never inferred from prose.
_HEADING_RE = re.compile(r"^#{1,6}\s")
_INTERACTION_HEADING_RE = re.compile(r"^#{1,6}\s+.*interaction", re.IGNORECASE)
_BULLET_RE = re.compile(r"^\s*[-*]\s+(.*\S)\s*$")
_PLACEHOLDER_RE = re.compile(r"^\{\{.*\}\}$")


def _count_interaction_entries(text):
    """Count explicit interaction entries under any 'Interaction…' heading.

    Conservative and deterministic: counts non-empty, non-placeholder bullet lines inside a
    section whose heading mentions 'interaction'. Notes without such a section yield 0 — the
    count is never guessed from prose.
    """
    count = 0
    in_section = False
    for line in text.splitlines():
        if _HEADING_RE.match(line):
            in_section = bool(_INTERACTION_HEADING_RE.match(line))
            continue
        if in_section:
            mm = _BULLET_RE.match(line)
            if mm and not _PLACEHOLDER_RE.match(mm.group(1).strip()):
                count += 1
    return count


def derive_completion_metrics(notes_path):
    """Deterministically count the identifiers actually present in a curation notes file.

    Reuses the ID extractor from phiweaver.lookup.validate_ontology_ids so the counts stay
    consistent with the QC tool. Returns distinct counts plus a human-readable provenance
    string. Never guesses: if the file is unreadable, all counts are zero.
    """
    blank = {"uniprot": 0, "locus_tags": 0, "ontology_terms": 0, "proteins": 0,
             "interactions": 0, "summary": "no curation notes file to scan"}
    try:
        text = Path(notes_path).read_text(encoding="utf-8")
    except OSError:
        return blank

    from phiweaver.lookup.validate_ontology_ids import extract_ids  # deterministic

    uniprot, ontology = set(), set()
    for token in extract_ids(text):
        prefix = token.split(":", 1)[0].upper()
        if prefix in ("UNIPROT", "UNIPROTKB"):
            uniprot.add(token.split(":", 1)[1].upper())
        else:  # PHIPO / GO / PHIDO
            ontology.add(token.upper())
    locus_tags = {m.group(0) for m in LOCUS_TAG_RE.finditer(text)}

    # Distinct proteins referenced, by either accession or locus tag.
    proteins = len(uniprot) + len(locus_tags)
    interactions = _count_interaction_entries(text)
    summary = (f"derived from notes: {len(uniprot)} UniProtKB accession(s), "
               f"{len(locus_tags)} locus tag(s), {len(ontology)} ontology term(s), "
               f"{interactions} interaction(s)")
    return {"uniprot": len(uniprot), "locus_tags": len(locus_tags),
            "ontology_terms": len(ontology), "proteins": proteins,
            "interactions": interactions, "summary": summary}

class CurationPipeline:
    def __init__(self):
        # Repo root is auto-detected (nearest ancestor with AGENTS.md), so the pipeline
        # works wherever the repo is cloned and regardless of where this module lives in
        # the package.
        self.vault_root = repo_root()
        # Literature content lives OUTSIDE the repo. Resolution order:
        #   1. PHI_LITERATURE_ROOT env var, if set (explicit override).
        #   2. Codespaces (PHI_CURATION_ENV=codespace): an in-workspace folder,
        #      so demo files are visible in the file explorer with zero config.
        #   3. Default: a sibling folder next to the repo
        #      (on this machine: /mnt/z/PHI-Canto-Literature).
        # See docs/STORAGE-CONFIGURATION.md / docs/DEMO-CODESPACES.md.
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
        # The tracking DB has a fixed home so completion metrics always land in the same
        # file regardless of the current working directory.
        self.db_path = self.vault_root / "11-CLAUDE-AI" / "db" / "phi_canto_tracking.db"

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
            # Run the converter as a package module. cwd is the (external) active/ folder,
            # which is outside the repo, so put the repo root (vault_root) on PYTHONPATH to
            # keep phiweaver importable.
            result = subprocess.run(
                ["python3", "-m", "phiweaver.pdf.pdf_convert", filename],
                capture_output=True, text=True, cwd=self.inbox_path,
                env={**os.environ, "PYTHONPATH": str(self.vault_root)})

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

    def complete_paper_workflow(self, filename, summary, proteins=None,
                                interactions=None, experiments=None, hours=None,
                                pmid=None):
        """Complete curation and move files to Literature folder.

        Records real completion metrics in the tracking DB: any counts not given
        explicitly are derived from the curation notes (distinct UniProtKB accessions,
        locus tags and ontology terms present, and interaction entries listed under an
        'Interactions' heading), and the article is flipped to 'curated' with the session
        linked to it.
        """
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

        # Step 2: Record real completion metrics in the tracking DB
        notes_path = self.literature_path / f"{base_name}-Curation-Notes.md"
        derived = derive_completion_metrics(notes_path)
        # Explicit counts win; otherwise fall back to what the notes actually contain.
        proteins_final = proteins if proteins is not None else derived["proteins"]
        interactions_final = interactions if interactions is not None else derived["interactions"]
        experiments_final = experiments if experiments is not None else derived["ontology_terms"]
        self.log_action("Completion metrics", derived["summary"])

        if HAS_DB:
            self.log_action("Recording completion in tracking DB")
            try:
                db = PHICantoSQLite(str(self.db_path))
                if db.connect():
                    db.create_schema()  # no-op if it already exists
                    result = db.record_completion(
                        base_name=base_name, summary=summary,
                        note_path=str(notes_path), pmid=pmid,
                        proteins_curated=proteins_final,
                        interactions_added=interactions_final,
                        experiments_annotated=experiments_final,
                        session_duration_hours=hours,
                        derived_notes=derived["summary"],
                    )
                    db.disconnect()
                    verb = "created" if result["article_created"] else "updated"
                    self.log_action(
                        f"✅ Article {verb} → curated (session {result['session_id']}): "
                        f"{proteins_final} proteins, {interactions_final} interactions, "
                        f"{experiments_final} experiments"
                        + (f", {hours} h" if hours else ""))
            except Exception as e:
                self.log_action(f"⚠️  Completion logging error: {e}")

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
  complete-paper <filename> <summary> [proteins] [interactions] [experiments] [hours]
                                 Move completed curation to Literature and record real
                                 completion metrics (counts auto-derived from the notes
                                 when not given; article flipped to 'curated')
  auto-process <pdf_path>        Full automation: copy + process
  help                          Show this help

Examples:
  # Start with new PDF
  python3 curation_pipeline.py new-paper ~/Downloads/paper.pdf

  # Process PDF already in To-curate folder
  python3 curation_pipeline.py process-pdf paper.pdf

  # Complete curation (metrics auto-derived from the curation notes)
  python3 curation_pipeline.py complete-paper paper.pdf "Added 5 effector proteins"

  # Complete curation with explicit metrics (proteins interactions experiments hours)
  python3 curation_pipeline.py complete-paper paper.pdf "5 effectors" 5 8 12 3.5

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
            print("Usage: complete-paper <filename> <summary> "
                  "[proteins] [interactions] [experiments] [hours]")
            return
        as_int = lambda i: int(sys.argv[i]) if len(sys.argv) > i else None
        pipeline.complete_paper_workflow(
            sys.argv[2], sys.argv[3],
            proteins=as_int(4), interactions=as_int(5), experiments=as_int(6),
            hours=(float(sys.argv[7]) if len(sys.argv) > 7 else None))

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