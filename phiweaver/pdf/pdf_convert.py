#!/usr/bin/env python3
"""
PDF-Convert Skill
Advanced PDF to Obsidian Markdown converter for academic papers

Usage: /pdf-convert [options] <pdf_file>
"""

import sys
import argparse
from pathlib import Path
import fitz  # PyMuPDF
import re
from datetime import date
from typing import List, Dict, Tuple
import json

class PDFConvertSkill:
    """Professional PDF to Obsidian converter with advanced features"""

    def __init__(self, config=None):
        self.config = config or self._load_default_config()
        self.pdf_path = None
        self.pdf_name = None
        self.output_dir = None
        self.images_dir = None
        self.document_sections = {}
        self.all_figures = []
        self.all_tables = []
        self.conversion_stats = {}

    def _load_default_config(self):
        """Load default configuration"""
        return {
            'output_directory': '.',
            'images_directory': '03-Media',
            'figure_prefix': 'Fig',
            'table_prefix': 'Table',
            'image_formats': ['png', 'jpeg', 'jpg'],
            'min_caption_length': 10,
            'confidence_threshold': 0.5,
            'max_figures_per_page': 10,
            'quality_validation': True,
            'create_index': True,
            'preserve_structure': True
        }

    def convert_pdf(self, pdf_file, **kwargs):
        """
        Main conversion method

        Args:
            pdf_file: Path to PDF file
            **kwargs: Override config options
        """
        # Update config with provided options
        for key, value in kwargs.items():
            if key in self.config:
                self.config[key] = value

        # Validate input
        if not self._validate_input(pdf_file):
            return None

        self.pdf_path = Path(pdf_file).resolve()
        self.pdf_name = self.pdf_path.stem

        # Set up directories
        self._setup_directories()

        print(f"🚀 PDF-Convert Skill: {self.pdf_path.name}")
        print(f"📁 Output: {self.output_dir}")
        print(f"🖼️  Images: {self.images_dir}")

        try:
            # Open PDF
            doc = fitz.open(str(self.pdf_path))

            # Phase 1: Document Analysis
            print("📖 Phase 1: Document structure analysis...")
            self._analyze_document_structure(doc)

            # Phase 2: Advanced Caption Extraction
            print("🔍 Phase 2: Advanced caption extraction...")
            self._extract_media_with_advanced_captions(doc)

            # Phase 3: Generate Structured Markdown
            print("📝 Phase 3: Structured markdown generation...")
            markdown_content = self._generate_structured_markdown(doc)

            # Phase 4: Quality Validation
            if self.config['quality_validation']:
                print("✅ Phase 4: Quality validation...")
                self._validate_output_quality()

            # Save output
            output_file = self.output_dir / f"{self.pdf_name}_converted.md"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(markdown_content)

            # Generate conversion report
            self._generate_conversion_report(output_file)

            doc.close()

            # Success summary
            self._print_success_summary(output_file)
            return output_file

        except Exception as e:
            print(f"❌ Conversion failed: {str(e)}")
            if self.config.get('debug', False):
                import traceback
                traceback.print_exc()
            return None

    def _validate_input(self, pdf_file):
        """Validate input file and requirements"""
        # Check file exists
        pdf_path = Path(pdf_file)
        if not pdf_path.exists():
            print(f"❌ Error: File not found: {pdf_file}")
            return False

        # Check if PDF
        if pdf_path.suffix.lower() != '.pdf':
            print(f"❌ Error: Not a PDF file: {pdf_file}")
            return False

        # Check PyMuPDF availability
        try:
            import fitz
        except ImportError:
            print("❌ Error: PyMuPDF not installed. Run: pip install PyMuPDF")
            return False

        return True

    def _setup_directories(self):
        """Set up output directories"""
        # Output directory
        if self.config['output_directory'] == '.':
            self.output_dir = Path.cwd()
        else:
            self.output_dir = Path(self.config['output_directory'])

        # Images directory
        self.images_dir = self.output_dir / self.config['images_directory'] / self.pdf_name
        self.images_dir.mkdir(parents=True, exist_ok=True)

    def _analyze_document_structure(self, doc):
        """Analyze document for sections and overall structure"""
        full_text = ""
        page_texts = {}

        # Extract all text first
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            page_texts[page_num] = text
            full_text += f"\n--- PAGE {page_num + 1} ---\n" + text

        # Detect document sections
        self.document_sections = self._detect_sections(full_text, page_texts)

    def _detect_sections(self, full_text, page_texts):
        """Detect document sections like Abstract, Introduction, etc."""
        sections = {}

        # Common academic section patterns
        section_patterns = [
            (r'\n\s*ABSTRACT\s*\n', 'Abstract'),
            (r'\n\s*Abstract\s*\n', 'Abstract'),
            (r'\n\s*INTRODUCTION\s*\n', 'Introduction'),
            (r'\n\s*Introduction\s*\n', 'Introduction'),
            (r'\n\s*1\.?\s*Introduction\s*\n', 'Introduction'),
            (r'\n\s*MATERIALS?\s+AND\s+METHODS?\s*\n', 'Methods'),
            (r'\n\s*Materials?\s+and\s+Methods?\s*\n', 'Methods'),
            (r'\n\s*METHODS?\s*\n', 'Methods'),
            (r'\n\s*Methods?\s*\n', 'Methods'),
            (r'\n\s*2\.?\s*Materials?\s+and\s+Methods?\s*\n', 'Methods'),
            (r'\n\s*RESULTS?\s*\n', 'Results'),
            (r'\n\s*Results?\s*\n', 'Results'),
            (r'\n\s*3\.?\s*Results?\s*\n', 'Results'),
            (r'\n\s*DISCUSSION\s*\n', 'Discussion'),
            (r'\n\s*Discussion\s*\n', 'Discussion'),
            (r'\n\s*4\.?\s*Discussion\s*\n', 'Discussion'),
            (r'\n\s*CONCLUSION\s*\n', 'Conclusion'),
            (r'\n\s*Conclusion\s*\n', 'Conclusion'),
            (r'\n\s*REFERENCES?\s*\n', 'References'),
            (r'\n\s*References?\s*\n', 'References'),
        ]

        # Find section boundaries
        for pattern, section_name in section_patterns:
            match = re.search(pattern, full_text, re.IGNORECASE)
            if match:
                sections[section_name] = {
                    'start_pos': match.start(),
                    'end_pos': None,
                    'title': section_name
                }

        # Set end positions
        section_items = sorted(sections.items(), key=lambda x: x[1]['start_pos'])
        for i, (name, info) in enumerate(section_items):
            if i < len(section_items) - 1:
                next_start = section_items[i + 1][1]['start_pos']
                sections[name]['end_pos'] = next_start
            else:
                sections[name]['end_pos'] = len(full_text)

        return sections

    def _extract_media_with_advanced_captions(self, doc):
        """Extract images with advanced caption matching"""
        # Import the advanced caption extractor
        from phiweaver.pdf.enhanced_caption_extractor import AdvancedCaptionExtractor

        extractor = AdvancedCaptionExtractor()

        # Extract captions from full document text
        full_text = ""
        for page_num in range(len(doc)):
            page = doc[page_num]
            full_text += page.get_text() + "\n"

        # Get captions using advanced extractor
        figures = extractor.extract_figures_advanced(full_text)
        tables = extractor.extract_tables_advanced(full_text)

        print(f"   📊 Found {len(figures)} figure captions")
        print(f"   📋 Found {len(tables)} table captions")

        # Process each page for images
        for page_num in range(len(doc)):
            page = doc[page_num]
            image_list = page.get_images(full=True)

            if image_list:
                print(f"📄 Processing page {page_num + 1}: {len(image_list)} images")

            for img_index, img in enumerate(image_list):
                # Extract image
                xref = img[0]
                pix = fitz.Pixmap(doc, xref)

                # Skip masks and very small images
                if pix.width < 50 or pix.height < 50:
                    pix = None
                    continue

                # Determine image type and filename
                filename, image_type = self._get_smart_filename(
                    page_num, img_index, figures, tables
                )

                # Save image
                image_path = self.images_dir / filename
                if pix.n - pix.alpha < 4:  # GRAY or RGB
                    if filename.endswith('.png'):
                        pix.save(str(image_path))
                    else:
                        pix.save(str(image_path))
                else:  # CMYK
                    pix1 = fitz.Pixmap(fitz.csRGB, pix)
                    pix1.save(str(image_path))
                    pix1 = None

                # Store image info
                image_info = {
                    'filename': filename,
                    'type': image_type,
                    'page': page_num + 1,
                    'caption': self._match_caption_to_image(
                        page_num, img_index, figures if image_type == 'figure' else tables
                    )
                }

                if image_type == 'figure':
                    self.all_figures.append(image_info)
                else:
                    self.all_tables.append(image_info)

                # Print extraction info
                if image_info['caption']:
                    caption_preview = image_info['caption']['caption'][:60] + "..."
                    icon = "🖼️ " if image_type == 'figure' else "📊"
                    print(f"  {icon} {image_info['caption']['label']}: {caption_preview}")

                pix = None

    def _get_smart_filename(self, page_num, img_index, figures, tables):
        """Generate intelligent filename based on detected captions"""
        # Try to match with detected captions
        page_figures = [f for f in figures if self._is_caption_on_page(f, page_num)]
        page_tables = [t for t in tables if self._is_caption_on_page(t, page_num)]

        # Determine if this is likely a figure or table
        if page_tables and img_index < len(page_tables):
            # Likely a table
            table_info = page_tables[img_index]
            number = table_info['number'].zfill(2)
            return f"{self.config['table_prefix']}{number}.png", 'table'
        elif page_figures and img_index < len(page_figures):
            # Likely a figure
            figure_info = page_figures[img_index]
            number = figure_info['number'].zfill(2)
            # Handle subfigures (e.g., "2A" -> "02A")
            if re.match(r'\d+[A-Za-z]', figure_info['number']):
                return f"{self.config['figure_prefix']}{figure_info['number'].zfill(3)}.png", 'figure'
            else:
                return f"{self.config['figure_prefix']}{number}.png", 'figure'
        else:
            # Fallback naming
            return f"page-{page_num + 1:02d}-img-{img_index + 1:02d}.png", 'figure'

    def _is_caption_on_page(self, caption, page_num):
        """Simple heuristic to check if caption might be on this page"""
        # This could be improved with position analysis
        return True

    def _match_caption_to_image(self, page_num, img_index, captions):
        """Match extracted caption to specific image"""
        if not captions or img_index >= len(captions):
            return None

        # Simple matching - could be improved with position analysis
        return captions[img_index] if img_index < len(captions) else None

    def _generate_structured_markdown(self, doc):
        """Generate well-structured markdown with clear separation"""
        content = []

        # Enhanced frontmatter
        content.extend([
            "---",
            f"created: {date.today()}",
            "type: literature",
            "tags: [literature, converted-pdf, pdf-convert-skill]",
            f"source: {self.pdf_path.name}",
            f"total_pages: {len(doc)}",
            f"figures: {len(self.all_figures)}",
            f"tables: {len(self.all_tables)}",
            f"sections: {len(self.document_sections)}",
            "conversion_tool: pdf-convert-skill",
            "conversion_quality: enhanced",
            "---",
            "",
            f"# {self.pdf_name.replace('-', ' ').replace('_', ' ').title()}",
            "",
            f"*Converted from PDF: {self.pdf_path.name}*",
            f"*Conversion date: {date.today()}*",
            ""
        ])

        # Document structure navigation
        if self.document_sections and self.config['preserve_structure']:
            content.append("## Document Structure")
            content.append("")
            for section_name in self.document_sections.keys():
                content.append(f"- [[#{section_name}]]")
            content.append("")

        # Main content sections
        if self.document_sections:
            content.extend(self._generate_sectioned_content(doc))
        else:
            content.extend(self._generate_page_based_content(doc))

        # Separator for figures and tables
        content.extend([
            "",
            "---",
            "",
            "# Figures and Tables",
            "",
            "*This section contains all figures and tables with complete captions, clearly separated from the main text.*",
            ""
        ])

        # Figures section
        if self.all_figures:
            content.extend(self._generate_figures_section())

        # Tables section
        if self.all_tables:
            content.extend(self._generate_tables_section())

        # Optional index
        if self.config['create_index']:
            content.extend(self._generate_reference_index())

        return '\n'.join(content)

    def _generate_sectioned_content(self, doc):
        """Generate content organized by sections"""
        content = []

        # Get full text for section extraction
        full_text = ""
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            full_text += f"\n--- PAGE {page_num + 1} ---\n" + text

        for section_name, section_info in sorted(self.document_sections.items(),
                                                key=lambda x: x[1]['start_pos']):
            content.append(f"## {section_name}")
            content.append("")

            # Extract actual section text
            start_pos = section_info['start_pos']
            end_pos = section_info.get('end_pos')

            if end_pos:
                section_text = full_text[start_pos:end_pos]
            else:
                section_text = full_text[start_pos:]

            # Clean the section text
            section_text = self._clean_section_text(section_text, section_name)

            if section_text.strip():
                content.append(section_text)
            else:
                content.append(f"*{section_name} content could not be extracted clearly*")

            content.append("")

        return content

    def _clean_section_text(self, text, section_name):
        """Clean and format section text"""
        if not text:
            return ""

        # Remove section header from the beginning
        lines = text.split('\n')
        cleaned_lines = []

        skip_header = True
        for line in lines:
            line = line.strip()

            # Skip empty lines and section headers at start
            if skip_header:
                if not line or section_name.lower() in line.lower():
                    continue
                skip_header = False

            # Remove page markers
            if line.startswith('--- PAGE'):
                continue

            # Keep meaningful content
            if len(line) > 3:
                cleaned_lines.append(line)

        # Join and clean up spacing
        cleaned_text = '\n\n'.join(cleaned_lines)
        return cleaned_text.strip()

    def _generate_page_based_content(self, doc):
        """Generate basic page-based content when sections not detected"""
        content = []
        content.append("## Document Content")
        content.append("")
        content.append("*Organized by pages (section detection not available)*")
        content.append("")

        for page_num in range(min(5, len(doc))):  # Limit for example
            page = doc[page_num]
            text = page.get_text()
            if text.strip():
                content.append(f"### Page {page_num + 1}")
                content.append("")
                content.append(text.strip())
                content.append("")

        return content

    def _generate_figures_section(self):
        """Generate figures section with captions"""
        content = ["## Figures", ""]

        for figure in self.all_figures:
            if figure['caption']:
                number = figure['caption']['number']
                caption_text = figure['caption']['caption']
                content.extend([
                    f"### Figure {number}",
                    "",
                    f"**Figure {number}** {caption_text}",
                    "",
                    f"![[{self.config['images_directory']}/{self.pdf_name}/{figure['filename']}]]",
                    "",
                    f"*Page {figure['page']} | Confidence: {figure['caption']['confidence']:.2f} | File: `{figure['filename']}`*",
                    ""
                ])
            else:
                content.extend([
                    f"### {figure['filename']}",
                    "",
                    f"![[{self.config['images_directory']}/{self.pdf_name}/{figure['filename']}]]",
                    "",
                    f"*Page {figure['page']} | File: `{figure['filename']}`*",
                    ""
                ])

        return content

    def _generate_tables_section(self):
        """Generate tables section with captions"""
        content = ["## Tables", ""]

        for table in self.all_tables:
            if table['caption']:
                number = table['caption']['number']
                caption_text = table['caption']['caption']
                content.extend([
                    f"### Table {number}",
                    "",
                    f"**Table {number}** {caption_text}",
                    "",
                    f"![[{self.config['images_directory']}/{self.pdf_name}/{table['filename']}]]",
                    "",
                    f"*Page {table['page']} | Confidence: {table['caption']['confidence']:.2f} | File: `{table['filename']}`*",
                    ""
                ])
            else:
                content.extend([
                    f"### {table['filename']}",
                    "",
                    f"![[{self.config['images_directory']}/{self.pdf_name}/{table['filename']}]]",
                    "",
                    f"*Page {table['page']} | File: `{table['filename']}`*",
                    ""
                ])

        return content

    def _generate_reference_index(self):
        """Generate reference index for navigation"""
        content = [
            "",
            "---",
            "",
            "## Conversion Index",
            "",
            "### Statistics",
            f"- **Total Pages**: {self.conversion_stats.get('pages', 'Unknown')}",
            f"- **Figures Found**: {len(self.all_figures)}",
            f"- **Tables Found**: {len(self.all_tables)}",
            f"- **Sections Detected**: {len(self.document_sections)}",
            "",
            "### Quality Metrics",
            f"- **Figure Captions with Confidence > 0.8**: {len([f for f in self.all_figures if f['caption'] and f['caption']['confidence'] > 0.8])}",
            f"- **Table Captions with Confidence > 0.8**: {len([t for t in self.all_tables if t['caption'] and t['caption']['confidence'] > 0.8])}",
            "",
            "### Files Generated",
            f"- **Markdown File**: `{self.pdf_name}_converted.md`",
            f"- **Images Directory**: `{self.config['images_directory']}/{self.pdf_name}/`",
            ""
        ]

        return content

    def _validate_output_quality(self):
        """Validate the quality of conversion output"""
        issues = []

        # Check for figures without captions
        figures_no_captions = len([f for f in self.all_figures if not f['caption']])
        if figures_no_captions > 0:
            issues.append(f"⚠️  {figures_no_captions} figures without captions detected")

        # Check caption confidence
        low_confidence_captions = len([
            f for f in (self.all_figures + self.all_tables)
            if f['caption'] and f['caption']['confidence'] < self.config['confidence_threshold']
        ])
        if low_confidence_captions > 0:
            issues.append(f"⚠️  {low_confidence_captions} captions with low confidence")

        # Check if sections were detected
        if not self.document_sections:
            issues.append("⚠️  No document sections detected - using page-based organization")

        # Report issues
        if issues:
            print("⚠️  Quality validation issues found:")
            for issue in issues:
                print(f"   {issue}")
        else:
            print("✅ Quality validation passed - high quality conversion")

        return issues

    def _generate_conversion_report(self, output_file):
        """Generate detailed conversion report"""
        report = {
            'source_file': str(self.pdf_path),
            'output_file': str(output_file),
            'conversion_date': str(date.today()),
            'statistics': {
                'total_pages': self.conversion_stats.get('pages', 0),
                'figures_found': len(self.all_figures),
                'tables_found': len(self.all_tables),
                'sections_detected': len(self.document_sections),
            },
            'quality_metrics': {
                'high_confidence_captions': len([
                    f for f in (self.all_figures + self.all_tables)
                    if f['caption'] and f['caption']['confidence'] > 0.8
                ]),
                'sections_with_content': len([
                    s for s in self.document_sections.values()
                    if s.get('end_pos', 0) - s.get('start_pos', 0) > 100
                ])
            },
            'config_used': self.config
        }

        # Save report
        report_file = output_file.parent / f"{output_file.stem}_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)

        print(f"📊 Conversion report saved: {report_file.name}")

    def _print_success_summary(self, output_file):
        """Print success summary"""
        print(f"\n✅ PDF-Convert Skill completed successfully!")
        print(f"📄 Output file: {output_file.name}")
        print(f"📁 Images directory: {self.images_dir.name}")
        print(f"📊 Statistics:")
        print(f"   • {len(self.all_figures)} figures with quality captions")
        print(f"   • {len(self.all_tables)} tables with quality captions")
        print(f"   • {len(self.document_sections)} document sections detected")
        print(f"\n🎯 Ready for Obsidian import!")


def main():
    """Command-line interface for the PDF-Convert skill"""
    parser = argparse.ArgumentParser(
        description='PDF-Convert Skill: Advanced PDF to Obsidian converter',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python pdf-convert.py paper.pdf
  python pdf-convert.py paper.pdf --output-dir ./converted
  python pdf-convert.py paper.pdf --images-dir Media --figure-prefix Figure
  python pdf-convert.py paper.pdf --no-validation --debug
        """
    )

    parser.add_argument('pdf_file', help='PDF file to convert')
    parser.add_argument('--output-dir', default='.', help='Output directory (default: current)')
    parser.add_argument('--images-dir', default='03-Media', help='Images directory (default: 03-Media)')
    parser.add_argument('--figure-prefix', default='Fig', help='Figure filename prefix (default: Fig)')
    parser.add_argument('--table-prefix', default='Table', help='Table filename prefix (default: Table)')
    parser.add_argument('--confidence-threshold', type=float, default=0.5, help='Caption confidence threshold')
    parser.add_argument('--no-validation', action='store_true', help='Skip quality validation')
    parser.add_argument('--no-index', action='store_true', help='Skip reference index generation')
    parser.add_argument('--debug', action='store_true', help='Enable debug output')

    args = parser.parse_args()

    # Build config from arguments
    config = {
        'output_directory': args.output_dir,
        'images_directory': args.images_dir,
        'figure_prefix': args.figure_prefix,
        'table_prefix': args.table_prefix,
        'confidence_threshold': args.confidence_threshold,
        'quality_validation': not args.no_validation,
        'create_index': not args.no_index,
        'debug': args.debug,
        'preserve_structure': True
    }

    # Create and run converter
    converter = PDFConvertSkill(config)
    result = converter.convert_pdf(args.pdf_file)

    if result:
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure


if __name__ == "__main__":
    main()