# PDF to Obsidian Converter

Convert PDFs to Obsidian-compatible markdown with automatic image extraction and linking.

## 🏆 Recommended Tool: PyMuPDF (fitz)

### Why PyMuPDF is Best for Obsidian:
- ✅ **Preserves text layout** and formatting structure
- ✅ **Extracts images** in original quality (PNG, JPEG)
- ✅ **Maintains image positioning** for proper document flow
- ✅ **Fast processing** even for large PDFs
- ✅ **Cross-platform** support (Windows, macOS, Linux)

## 📦 Installation

### 🚀 **Automated Setup (Recommended)**

**One-command installation for all environments:**

```bash
# Navigate to PDF converter directory
cd 10-TEST

# Run automated setup
./setup_pdf_converter.sh
```

**What the script does:**
- ✅ **Detects your environment** (WSL2, Ubuntu, macOS, Windows)
- ✅ **Chooses best installation method** automatically
- ✅ **Handles externally-managed environments**
- ✅ **Verifies installation** works correctly
- ✅ **Tests PDF converter** functionality

### 📋 **Manual Installation Guide**

If you prefer manual installation or the automated script fails:

#### 🔧 **WSL2/Ubuntu (Externally-Managed Environment)**

**If you get "externally-managed-environment" error:**

```bash
# ✅ WORKING SOLUTION (Tested on WSL2)
python3 -m pip install --break-system-packages PyMuPDF

# Alternative: User-only installation
python3 -m pip install --user PyMuPDF
```

#### 🐍 **Python Virtual Environment (Recommended for Development)**

**For regular Linux/macOS systems:**

```bash
# Create virtual environment
python3 -m venv pdf_converter_env

# Activate environment
source pdf_converter_env/bin/activate

# Install packages
pip install PyMuPDF

# When done, deactivate
deactivate
```

**Note:** Virtual environments may have permission issues on WSL2 Windows mounts. Use the `--break-system-packages` method above for WSL2.

#### 🪟 **Windows Native Python**

```bash
# Standard installation
pip install PyMuPDF

# Or with virtual environment
python -m venv pdf_env
pdf_env\Scripts\activate
pip install PyMuPDF
```

#### 🍎 **macOS**

```bash
# With Homebrew Python
pip3 install PyMuPDF

# Or with virtual environment
python3 -m venv pdf_env
source pdf_env/bin/activate
pip install PyMuPDF
```

### 📚 Alternative PDF Libraries

```bash
# For table extraction (after solving environment)
python3 -m pip install --break-system-packages pdfplumber

# For OCR capabilities  
python3 -m pip install --break-system-packages pdf2image pillow pytesseract

# For advanced layout analysis
python3 -m pip install --break-system-packages pdfminer.six

# Lightweight text-only extraction
python3 -m pip install --break-system-packages PyPDF2
```

## 🚀 Usage

### Basic Conversion
```bash
cd 10-TEST
python3 obsidian_pdf_converter.py
```

### What It Does
1. **Extracts text** with intelligent heading detection
2. **Saves images** to `03-Media/[pdf-name]/` directory
3. **Creates markdown** with Obsidian image links: `![[03-Media/tretiakova-2022/page-01-img-01.png]]`
4. **Adds metadata** in frontmatter for organization
5. **Structures content** with proper headings and sections

## 📁 Output Structure

```
03-Media/
└── tretiakova-2022/
    ├── page-01-img-01.png
    ├── page-01-img-02.png
    ├── page-02-img-01.png
    └── ...

10-TEST/
└── Tretiakova-2022.md    # Generated markdown with embedded images
```

## 📝 Generated Markdown Format

```markdown
---
created: 2026-04-19
type: literature
tags: [literature, converted-pdf]
source: Tretiakova-2022.pdf
total_pages: 15
---

# Tretiakova Et Al. (2022)

*Converted from PDF: Tretiakova-2022.pdf*

## Page 1

### Abstract

Text content here...

### Images

![[03-Media/tretiakova-2022/page-01-img-01.png]]

## Page 2

More content...

![[03-Media/tretiakova-2022/page-02-img-01.png]]
```

## 🔧 Advanced Features

### Custom Image Placement
The converter:
- Detects logical image positions in text flow
- Groups images by page for organization
- Uses descriptive filenames: `page-XX-img-YY.ext`
- Maintains relative paths for vault portability

### Intelligent Text Processing
- **Heading detection**: Recognizes Abstract, Introduction, Methods, etc.
- **Text cleaning**: Removes artifacts and page numbers
- **Structure preservation**: Maintains logical document flow
- **Obsidian optimization**: Perfect WikiLink integration

## 🔄 Alternative Tools Comparison

### PyMuPDF (fitz) ⭐ Recommended
- **Pros**: Best image quality, fast, comprehensive
- **Cons**: Larger dependency
- **Best for**: Research papers, technical documents

### pdfplumber
- **Pros**: Excellent table extraction, precise layout
- **Cons**: Limited image extraction
- **Best for**: Data-heavy documents, forms

### pdf2image + OCR
- **Pros**: Handles scanned PDFs, any image format
- **Cons**: Slower, requires OCR setup
- **Best for**: Scanned documents, handwritten notes

### Online Tools
- **Pros**: No installation needed
- **Cons**: Privacy concerns, no automation
- **Best for**: One-off conversions

## 🎯 Obsidian Integration Benefits

### Perfect Vault Integration
- Images saved to standard `03-Media/` directory
- Automatic Obsidian image syntax: `![[path]]`
- Frontmatter metadata for organization
- Compatible with graph view and linking

### Literature Workflow
- Fits existing PHI-Canto structure
- Links to article registry and tracking
- Integrates with session logging
- Supports citation and reference management

### Quality Assurance
- Preserves original formatting structure
- Maintains image-text relationships
- Creates reviewable conversion logs
- Enables collaborative annotation

## 🛠️ Customization Options

Edit `obsidian_pdf_converter.py` to:
- Change image directory: Modify `images_dir` parameter
- Adjust heading detection: Update `detect_heading()` function  
- Customize markdown format: Edit `process_text_for_markdown()`
- Add metadata fields: Enhance frontmatter generation

## ⚡ Performance Tips

### For Large PDFs
- Process in pages chunks for memory efficiency
- Use image compression for storage optimization
- Consider parallel processing for bulk conversion

### For Image-Heavy Documents
- Adjust image quality settings if needed
- Use PNG for diagrams, JPEG for photos
- Implement image deduplication for efficiency

## 🔍 Troubleshooting

### Python Environment Issues

#### **"externally-managed-environment" Error**
```bash
# ✅ SOLUTION: Use --break-system-packages
python3 -m pip install --break-system-packages PyMuPDF

# ❌ DON'T USE: These don't work on newer Ubuntu/Debian
pip install PyMuPDF
pip3 install PyMuPDF
```

#### **Virtual Environment Permission Errors**
```bash
# On WSL2 Windows mounts, you might see:
# Error: [Errno 1] Operation not permitted: 'lib' -> '/mnt/.../lib64'

# ✅ SOLUTION: Use system packages instead
python3 -m pip install --break-system-packages PyMuPDF

# Or create venv in Linux filesystem (/tmp or ~/)
cd /tmp
python3 -m venv pdf_env
source pdf_env/bin/activate
pip install PyMuPDF
# Then run converter from original directory
```

#### **"pip not found" or "No module named pip"**
```bash
# Install pip first
sudo apt update
sudo apt install python3-pip

# Or use python module approach
python3 -m ensurepip --default-pip
```

### PDF Conversion Issues

#### **"PyMuPDF not found" After Installation**
```bash
# Verify installation
python3 -c "import fitz; print('PyMuPDF installed successfully')"

# Check if installed in user directory
python3 -m pip show PyMuPDF

# Reinstall if needed
python3 -m pip install --break-system-packages --upgrade PyMuPDF
```

#### **Permission Errors with PDF Files**
```bash
# Check file permissions
ls -la *.pdf

# Fix permissions if needed
chmod 644 *.pdf
```

### Common PDF Processing Issues
- **"PyMuPDF not found"**: Use environment-specific installation above
- **Permission errors**: Check file permissions and directory access
- **Memory issues**: Process large PDFs in smaller chunks
- **Missing images**: Verify PDF contains extractable images (not scanned)

### PDF Quality Issues
- **Poor text extraction**: Try OCR approach for scanned PDFs
- **Wrong heading levels**: Adjust heading detection heuristics
- **Missing content**: Check if PDF has copy protection
- **Garbled text**: PDF might use non-standard fonts or encoding

### Environment-Specific Solutions

#### **WSL2 Users**
```bash
# ✅ Always use this for WSL2
python3 -m pip install --break-system-packages PyMuPDF

# Check WSL version
wsl --version

# Update WSL if needed
wsl --update
```

#### **Docker/Container Users**
```bash
# Install system packages first
apt-get update && apt-get install -y python3-pip

# Then install PyMuPDF
python3 -m pip install PyMuPDF
```

#### **Conda Users**
```bash
# Use conda-forge channel
conda install -c conda-forge pymupdf

# Or create conda environment
conda create -n pdfconv pymupdf
conda activate pdfconv
```

## 📚 For PHI-Canto Workflow

Once converted:
1. **Move markdown** to `04-Literature/` directory
2. **Update article registry** with new literature
3. **Link to database** using session logger
4. **Follow curation protocol** for annotation

```bash
# After conversion
mv 10-TEST/Tretiakova-2022.md 04-Literature/
python3 session_logger.py quick "Literature" "Added Tretiakova 2022 PDF" 0 1 0.5
```

Perfect integration with your existing hybrid workflow!