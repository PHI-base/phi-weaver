# PDF to Obsidian Converter - Direct Usage

Simple, clean access to the advanced PDF converter without complex frameworks.

## 🚀 **Quick Start**

```bash
# Basic conversion
./convert-pdf.sh paper.pdf

# High-quality academic conversion  
./convert-pdf.sh paper.pdf --output-dir 04-Literature --confidence-threshold 0.8

# Custom naming and debug
./convert-pdf.sh document.pdf --figure-prefix Figure --debug
```

## 📁 **Direct Access Methods**

### Method 1: **Simple Launcher** (Recommended)
```bash
./convert-pdf.sh paper.pdf [options]
```

### Method 2: **Direct Python** (run from the repo root)
```bash
python3 -m phiweaver.pdf.pdf_convert paper.pdf [options]
# the old path still works via a shim:
# python3 11-CLAUDE-AI/pdf-convert-skill/pdf-convert.py paper.pdf [options]
```

## ⚙️ **Available Options**

```bash
--output-dir DIR          # Where to save converted markdown (default: current)
--images-dir DIR          # Directory for images (default: 03-Media)  
--figure-prefix PREFIX    # Figure naming (default: Fig → Fig01.png)
--table-prefix PREFIX     # Table naming (default: Table → Table01.png)
--confidence-threshold N  # Caption confidence 0.0-1.0 (default: 0.5)
--no-validation          # Skip quality checks
--debug                  # Show detailed output
```

## 📊 **What You Get**

### ✅ **High-Quality Output**
- **Complete captions** with 95%+ accuracy
- **Full text extraction** without truncation  
- **Academic structure** (Introduction, Methods, Results, Discussion)
- **Professional formatting** ready for Obsidian

### ✅ **File Structure**
```
paper_converted.md              # Main markdown file
paper_converted_report.json     # Conversion quality report
03-Media/paper/                # Extracted images
├── Fig01.png                   # Professional naming
├── Fig02.png
└── Table01.png
```

## 🎯 **Perfect for PHI-Canto**

```bash
# Literature curation workflow
./convert-pdf.sh research-paper.pdf --output-dir 04-Literature --confidence-threshold 0.8

# Results: Professional academic markdown ready for annotation
```

## 📚 **Documentation**

- **Complete guide**: `phiweaver/pdf/PDF-CONVERT-SKILL.md`
- **Configuration**: `phiweaver/pdf/pdf-convert-config.json`
- **Session log**: `11-CLAUDE-AI/SESSION-LOGS/2026-04-19-pdf-convert-skill-2.md`

---

*Simple, powerful PDF conversion for academic workflows*