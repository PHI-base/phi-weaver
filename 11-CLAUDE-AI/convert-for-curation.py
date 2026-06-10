#!/usr/bin/env python3
"""
PHI-Canto PDF Conversion Wrapper
Ensures PDFs are converted with proper file organization for curation workflow
"""

import os
import sys
import shutil
import subprocess
import json
from pathlib import Path

def convert_pdf_for_curation(pdf_path, vault_root=str(Path(__file__).resolve().parents[1])):
    """Convert PDF with proper PHI-Canto file organization"""

    # Ensure we're working from vault root
    os.chdir(vault_root)

    # Get PDF filename without extension
    pdf_file = Path(pdf_path)
    pdf_name = pdf_file.stem

    # Set up proper paths
    literature_dir = "04-Literature"
    media_dir = "03-Media"
    logs_dir = "11-CLAUDE-AI"

    # Ensure directories exist
    Path(literature_dir).mkdir(exist_ok=True)
    Path(media_dir).mkdir(exist_ok=True)
    Path(logs_dir).mkdir(exist_ok=True)

    # Run PDF conversion with PHI-canto config
    conversion_cmd = [
        "python3",
        "11-CLAUDE-AI/pdf-convert-skill/pdf-convert.py",
        str(pdf_path),
        "--config", "phi_canto_config",
        "--output-dir", literature_dir
    ]

    print(f"🚀 Converting {pdf_name} for PHI-Canto curation...")
    result = subprocess.run(conversion_cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"❌ Conversion failed: {result.stderr}")
        return False

    print(result.stdout)

    # Move files to correct locations
    converted_md = f"{pdf_name}_converted.md"
    converted_json = f"{pdf_name}_converted_report.json"
    media_folder = pdf_name

    # Check if files were created in wrong location and move them
    to_curate_dir = Path("00-Inbox/To-curate")

    # Move markdown file if in wrong location
    wrong_md_path = to_curate_dir / converted_md
    correct_md_path = Path(literature_dir) / converted_md
    if wrong_md_path.exists() and not correct_md_path.exists():
        shutil.move(str(wrong_md_path), str(correct_md_path))
        print(f"📄 Moved {converted_md} to {literature_dir}/")

    # Move JSON report if in wrong location
    wrong_json_path = to_curate_dir / converted_json
    correct_json_path = Path(logs_dir) / converted_json
    if wrong_json_path.exists() and not correct_json_path.exists():
        shutil.move(str(wrong_json_path), str(correct_json_path))
        print(f"📊 Moved {converted_json} to {logs_dir}/")

    # Move media folder if in wrong location
    wrong_media_path = to_curate_dir / "03-Media" / media_folder
    correct_media_path = Path(media_dir) / media_folder
    if wrong_media_path.exists() and not correct_media_path.exists():
        shutil.move(str(wrong_media_path), str(correct_media_path))
        print(f"🖼️  Moved media folder to {media_dir}/{media_folder}/")

        # Remove empty 03-Media folder from To-curate if it exists
        empty_media_dir = to_curate_dir / "03-Media"
        if empty_media_dir.exists() and not any(empty_media_dir.iterdir()):
            empty_media_dir.rmdir()

    print(f"✅ {pdf_name} ready for curation with proper file organization")
    print(f"📄 Markdown: {literature_dir}/{converted_md}")
    print(f"🖼️  Images: {media_dir}/{media_folder}/")
    print(f"📊 Report: {logs_dir}/{converted_json}")

    return True

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 convert-for-curation.py <pdf_path>")
        sys.exit(1)

    pdf_path = sys.argv[1]
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file not found: {pdf_path}")
        sys.exit(1)

    success = convert_pdf_for_curation(pdf_path)
    sys.exit(0 if success else 1)