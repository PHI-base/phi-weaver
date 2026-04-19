#!/usr/bin/env python3
"""
PDF to Markdown converter
Try different methods to extract text from PDF
"""

import sys
import os

def extract_with_fitz():
    """Try with PyMuPDF (fitz)"""
    try:
        import fitz  # PyMuPDF
        print("✅ Using PyMuPDF (fitz) for extraction...")

        pdf_path = "Tretiakova-2022.pdf"
        doc = fitz.open(pdf_path)

        full_text = ""
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            full_text += f"\n# Page {page_num + 1}\n\n"
            full_text += text + "\n\n"

        doc.close()
        return full_text
    except ImportError:
        print("❌ PyMuPDF not available")
        return None
    except Exception as e:
        print(f"❌ Error with PyMuPDF: {e}")
        return None

def extract_with_pypdf():
    """Try with PyPDF2/pypdf"""
    try:
        import PyPDF2
        print("✅ Using PyPDF2 for extraction...")

        pdf_path = "Tretiakova-2022.pdf"
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)

            full_text = ""
            for page_num, page in enumerate(pdf_reader.pages):
                text = page.extract_text()
                full_text += f"\n# Page {page_num + 1}\n\n"
                full_text += text + "\n\n"

        return full_text
    except ImportError:
        print("❌ PyPDF2 not available")
        return None
    except Exception as e:
        print(f"❌ Error with PyPDF2: {e}")
        return None

def extract_with_pdfplumber():
    """Try with pdfplumber"""
    try:
        import pdfplumber
        print("✅ Using pdfplumber for extraction...")

        pdf_path = "Tretiakova-2022.pdf"
        full_text = ""

        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                text = page.extract_text()
                full_text += f"\n# Page {page_num + 1}\n\n"
                if text:
                    full_text += text + "\n\n"

        return full_text
    except ImportError:
        print("❌ pdfplumber not available")
        return None
    except Exception as e:
        print(f"❌ Error with pdfplumber: {e}")
        return None

def main():
    print("🔄 Attempting PDF text extraction...")

    # Try different extraction methods
    extractors = [extract_with_fitz, extract_with_pdfplumber, extract_with_pypdf]

    extracted_text = None
    for extractor in extractors:
        extracted_text = extractor()
        if extracted_text:
            break

    if not extracted_text:
        print("❌ No PDF extraction libraries available")
        print("📦 Available libraries:")
        print("   pip install PyMuPDF  # Recommended for best quality")
        print("   pip install pdfplumber  # Good for tables and layout")
        print("   pip install PyPDF2  # Basic text extraction")
        return False

    # Convert to markdown format
    markdown_content = convert_to_markdown(extracted_text)

    # Write to file
    output_file = "Tretiakova-2022.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(markdown_content)

    print(f"✅ PDF converted to markdown: {output_file}")
    print(f"📄 Total length: {len(markdown_content)} characters")
    return True

def convert_to_markdown(text):
    """Convert extracted text to markdown format"""

    # Basic markdown formatting
    lines = text.split('\n')
    markdown_lines = []

    # Add frontmatter
    markdown_lines.extend([
        "---",
        "created: 2026-04-19",
        "type: literature",
        "tags: [literature, converted-pdf]",
        "source: Tretiakova-2022.pdf",
        "---",
        "",
        "# Tretiakova et al. (2022)",
        "",
        "*Converted from PDF to Markdown*",
        ""
    ])

    for line in lines:
        line = line.strip()
        if not line:
            markdown_lines.append("")
            continue

        # Simple heuristics for markdown conversion
        if line.startswith("# Page"):
            markdown_lines.append(f"\n{line}\n")
        elif len(line) < 100 and line.isupper() and len(line.split()) < 10:
            # Likely a heading
            markdown_lines.append(f"## {line.title()}")
        elif line.startswith(("Abstract", "Introduction", "Methods", "Results", "Discussion", "Conclusion", "References")):
            # Section headers
            markdown_lines.append(f"## {line}")
        else:
            # Regular paragraph
            markdown_lines.append(line)

    return '\n'.join(markdown_lines)

if __name__ == "__main__":
    main()