#!/bin/bash
# Simple PDF Converter Launcher
# Usage: ./convert-pdf.sh paper.pdf [options]

if [ $# -eq 0 ]; then
    echo "📚 PDF to Obsidian Converter"
    echo "Usage: ./convert-pdf.sh <pdf_file> [options]"
    echo ""
    echo "Examples:"
    echo "  ./convert-pdf.sh paper.pdf"
    echo "  ./convert-pdf.sh paper.pdf --output-dir 04-Literature"
    echo "  ./convert-pdf.sh paper.pdf --confidence-threshold 0.8 --debug"
    echo ""
    echo "Full documentation: 11-CLAUDE-AI/pdf-convert-skill/PDF-CONVERT-SKILL.md"
    exit 0
fi

# Execute the PDF converter
python3 11-CLAUDE-AI/pdf-convert-skill/pdf-convert.py "$@"