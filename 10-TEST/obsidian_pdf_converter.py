#!/usr/bin/env python3
"""
Obsidian PDF Converter with Image Extraction
Converts PDF to Markdown with embedded images using Obsidian notation
"""

import os
import sys
from pathlib import Path
import re

def check_dependencies():
    """Check if required libraries are available"""
    try:
        import fitz  # PyMuPDF
        return True, "PyMuPDF available"
    except ImportError:
        return False, "PyMuPDF not installed. Run: pip install PyMuPDF"

def extract_pdf_with_images(pdf_path, output_dir=".", images_dir="03-Media"):
    """
    Extract PDF to markdown with images

    Args:
        pdf_path: Path to PDF file
        output_dir: Directory for markdown output
        images_dir: Directory for extracted images (relative to vault root)
    """
    try:
        import fitz
    except ImportError:
        print("❌ PyMuPDF not available. Install with: pip install PyMuPDF")
        return None

    # Setup paths
    pdf_path = Path(pdf_path)
    output_dir = Path(output_dir)

    # Create images directory in vault root (go up from 10-TEST)
    vault_root = output_dir.parent
    images_full_path = vault_root / images_dir
    images_full_path.mkdir(exist_ok=True)

    # Create subfolder for this PDF's images
    pdf_name = pdf_path.stem
    pdf_images_dir = images_full_path / pdf_name
    pdf_images_dir.mkdir(exist_ok=True)

    print(f"🔄 Processing PDF: {pdf_path.name}")
    print(f"📁 Images will be saved to: {pdf_images_dir}")

    # Open PDF
    doc = fitz.open(pdf_path)

    markdown_content = []
    image_counter = 0

    # Add frontmatter
    markdown_content.extend([
        "---",
        f"created: {get_current_date()}",
        "type: literature",
        "tags: [literature, converted-pdf]",
        f"source: {pdf_path.name}",
        f"total_pages: {len(doc)}",
        "---",
        "",
        f"# {pdf_name.replace('-', ' ').replace('_', ' ').title()}",
        "",
        f"*Converted from PDF: {pdf_path.name}*",
        f"*Total pages: {len(doc)}*",
        ""
    ])

    # Process each page
    for page_num in range(len(doc)):
        page = doc[page_num]

        print(f"📄 Processing page {page_num + 1}/{len(doc)}")

        # Add page header
        markdown_content.append(f"## Page {page_num + 1}")
        markdown_content.append("")

        # Extract and save images from this page
        image_list = page.get_images()
        page_images = {}

        for img_index, img in enumerate(image_list):
            # Extract image
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]

            # Generate image filename
            image_filename = f"page-{page_num+1:02d}-img-{img_index+1:02d}.{image_ext}"
            image_path = pdf_images_dir / image_filename

            # Save image
            with open(image_path, "wb") as img_file:
                img_file.write(image_bytes)

            # Store for text replacement (using relative path from vault root)
            relative_image_path = f"{images_dir}/{pdf_name}/{image_filename}"
            page_images[f"img_{img_index}"] = relative_image_path

            image_counter += 1
            print(f"  💾 Saved image: {image_filename}")

        # Extract text
        text = page.get_text()

        # Process text and replace image references
        processed_text = process_text_for_markdown(text, page_images, page_num + 1)

        # Add images that weren't referenced in text
        for img_key, img_path in page_images.items():
            if f"![[{img_path}]]" not in processed_text:
                processed_text += f"\n\n![[{img_path}]]\n"

        markdown_content.append(processed_text)
        markdown_content.append("")

    doc.close()

    # Generate final markdown
    final_markdown = '\n'.join(markdown_content)

    # Save markdown file
    output_file = output_dir / f"{pdf_name}.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(final_markdown)

    print(f"✅ Conversion complete!")
    print(f"📄 Markdown: {output_file}")
    print(f"🖼️  Images: {image_counter} images saved to {pdf_images_dir}")
    print(f"📁 Images directory: {images_dir}/{pdf_name}/")

    return output_file

def process_text_for_markdown(text, page_images, page_num):
    """Process extracted text and format for markdown"""

    lines = text.split('\n')
    processed_lines = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Detect headings based on formatting patterns
        if detect_heading(line):
            # Convert to markdown heading
            level = determine_heading_level(line)
            processed_lines.append(f"{'#' * level} {line}")
        else:
            # Regular text - clean up and format
            cleaned_line = clean_text_line(line)
            if cleaned_line:
                processed_lines.append(cleaned_line)

    # Join with appropriate spacing
    result = '\n\n'.join(processed_lines)

    # Add images at the end of page content
    if page_images:
        result += "\n\n### Images\n\n"
        for img_path in page_images.values():
            result += f"![[{img_path}]]\n\n"

    return result

def detect_heading(line):
    """Detect if a line is likely a heading"""
    # Heuristics for heading detection
    if len(line) < 5:
        return False

    # Common heading patterns
    heading_keywords = [
        'abstract', 'introduction', 'methods', 'methodology', 'results',
        'discussion', 'conclusion', 'references', 'bibliography',
        'background', 'materials', 'analysis', 'findings', 'summary'
    ]

    line_lower = line.lower()

    # Check if line contains heading keywords
    if any(keyword in line_lower for keyword in heading_keywords):
        return True

    # Check if line is short and mostly caps
    if len(line) < 50 and line.isupper() and len(line.split()) < 8:
        return True

    # Check if line ends with typical heading patterns
    if line.endswith(':') and len(line.split()) < 10:
        return True

    return False

def determine_heading_level(line):
    """Determine appropriate heading level"""
    line_lower = line.lower()

    # Main sections (level 2)
    main_sections = ['abstract', 'introduction', 'methods', 'results', 'discussion', 'conclusion', 'references']
    if any(section in line_lower for section in main_sections):
        return 3

    # Subsections (level 3)
    return 4

def clean_text_line(line):
    """Clean and format text line"""
    # Remove excessive whitespace
    line = ' '.join(line.split())

    # Skip very short lines that are likely artifacts
    if len(line) < 3:
        return None

    # Skip lines that are mostly numbers/symbols (page numbers, etc.)
    if re.match(r'^[\d\s\-\.\(\)]+$', line):
        return None

    return line

def get_current_date():
    """Get current date in YYYY-MM-DD format"""
    from datetime import date
    return date.today().strftime('%Y-%m-%d')

def main():
    """Main conversion function"""

    # Check dependencies
    available, message = check_dependencies()
    if not available:
        print(f"❌ {message}")
        return False

    # Check for PDF file
    pdf_file = "Tretiakova-2022.pdf"
    if not os.path.exists(pdf_file):
        print(f"❌ PDF file not found: {pdf_file}")
        print("📁 Current directory contents:")
        for file in os.listdir('.'):
            if file.endswith('.pdf'):
                print(f"   📄 {file}")
        return False

    # Convert PDF
    result = extract_pdf_with_images(pdf_file)

    if result:
        print(f"\n🎯 Conversion successful!")
        print(f"📝 Open in Obsidian: {result.name}")
        print(f"🖼️  Images automatically linked with Obsidian notation")
        return True
    else:
        print("❌ Conversion failed")
        return False

if __name__ == "__main__":
    main()