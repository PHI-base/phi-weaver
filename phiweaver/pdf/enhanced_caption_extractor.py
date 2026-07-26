#!/usr/bin/env python3
"""
Enhanced Caption Extraction Module
Improves figure/table caption detection and text processing
"""

import re
from typing import List, Dict, Tuple

# A caption line begins its own text block: "Figure 3. ..." / "Table 1 ..." / "Fig. 2 ...".
# The number may be Arabic ("1", "1a"), supplementary ("S1") or Roman ("I", "IV") — 1990s
# journals number tables in Roman, and requiring \d+ made those tables invisible entirely.
# `(?-i:[IVXL]+)` stays case-sensitive inside the IGNORECASE match so the word "in" is not
# read as table `i`; C/D/M are excluded because they start too many English words and no
# paper numbers tables past XXXIX.
#
# Single definition: pdf_convert.py's CAPTION_BLOCK_RE imports this fragment rather than
# redefining it. The two used to be hand-synced copies and drifted once — a missing
# trailing \b in one copy manufactured phantom tables from prose.
CAPTION_NUMBER = r"(\d+[A-Za-z]*|S\d+[A-Za-z]*|(?-i:[IVXL]+))\b"

class AdvancedCaptionExtractor:
    """Advanced caption extraction with better pattern matching"""

    def __init__(self):
        self.figure_patterns = [
            # Standard patterns
            r'(Figure\s+(\d+[A-Z]?)\.?\s*[\:\-\.\s]*)(.*?)(?=\n\s*\n|\n\s*(?:Figure|Table|References|\d+\.|[A-Z]{2,})|$)',
            r'(Fig\.?\s+(\d+[A-Z]?)\.?\s*[\:\-\.\s]*)(.*?)(?=\n\s*\n|\n\s*(?:Fig|Table|References|\d+\.|[A-Z]{2,})|$)',
            r'(FIGURE\s+(\d+[A-Z]?)\.?\s*[\:\-\.\s]*)(.*?)(?=\n\s*\n|\n\s*(?:FIGURE|TABLE|REFERENCES)|$)',

            # Extended patterns for better capture
            r'([Ff]igure\s+(\d+[A-Za-z]*)[\.\:\s]*[–\-]?\s*)([\s\S]*?)(?=\n\s*[Ff]igure|\n\s*[Tt]able|\n\s*\d+\.|\n\s*[A-Z][A-Z]|\n\s*References|$)',
            r'([Ff]ig\.?\s+(\d+[A-Za-z]*)[\.\:\s]*[–\-]?\s*)([\s\S]*?)(?=\n\s*[Ff]ig|\n\s*[Tt]able|\n\s*\d+\.|\n\s*[A-Z][A-Z]|\n\s*References|$)',
        ]

        self.table_patterns = [
            # Standard table patterns
            r'(Table\s+' + CAPTION_NUMBER + r'\.?\s*[\:\-\.\s]*)(.*?)(?=\n\s*\n|\n\s*(?:Table|Figure|References|\d+\.|[A-Z]{2,})|$)',
            r'(TABLE\s+' + CAPTION_NUMBER + r'\.?\s*[\:\-\.\s]*)(.*?)(?=\n\s*\n|\n\s*(?:TABLE|FIGURE|REFERENCES)|$)',

            # Extended patterns
            r'([Tt]able\s+' + CAPTION_NUMBER + r'[\.\:\s]*[–\-]?\s*)([\s\S]*?)(?=\n\s*[Tt]able|\n\s*[Ff]igure|\n\s*\d+\.|\n\s*[A-Z][A-Z]|\n\s*References|$)',
        ]

    def extract_figures_advanced(self, text: str) -> List[Dict]:
        """Extract figure captions with improved accuracy"""
        figures = []

        for pattern in self.figure_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE | re.DOTALL)

            for match in matches:
                figure_label = match.group(1).strip()
                figure_number = match.group(2).strip() if match.group(2) else "?"
                caption_text = match.group(3).strip() if match.group(3) else ""

                # Clean and validate caption
                cleaned_caption = self._clean_caption_advanced(caption_text)

                if cleaned_caption and len(cleaned_caption) > 10:
                    figures.append({
                        'number': figure_number,
                        'label': figure_label,
                        'caption': cleaned_caption,
                        'confidence': self._calculate_confidence(figure_label, cleaned_caption),
                        'start_pos': match.start(),
                        'end_pos': match.end()
                    })

        # Deduplicate and sort by confidence
        figures = self._deduplicate_captions(figures)
        figures.sort(key=lambda x: (-x['confidence'], x['start_pos']))

        return figures

    def extract_tables_advanced(self, text: str) -> List[Dict]:
        """Extract table captions with improved accuracy"""
        tables = []

        for pattern in self.table_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE | re.DOTALL)

            for match in matches:
                table_label = match.group(1).strip()
                table_number = match.group(2).strip() if match.group(2) else "?"
                caption_text = match.group(3).strip() if match.group(3) else ""

                # Clean and validate caption
                cleaned_caption = self._clean_caption_advanced(caption_text)

                if cleaned_caption and len(cleaned_caption) > 5:
                    tables.append({
                        'number': table_number,
                        'label': table_label,
                        'caption': cleaned_caption,
                        'confidence': self._calculate_confidence(table_label, cleaned_caption),
                        'start_pos': match.start(),
                        'end_pos': match.end()
                    })

        # Deduplicate and sort by confidence
        tables = self._deduplicate_captions(tables)
        tables.sort(key=lambda x: (-x['confidence'], x['start_pos']))

        return tables

    def _clean_caption_advanced(self, text: str) -> str:
        """Advanced caption cleaning"""
        if not text:
            return ""

        # Remove excessive whitespace
        text = ' '.join(text.split())

        # Remove common artifacts
        text = re.sub(r'^\W+', '', text)  # Leading punctuation
        text = re.sub(r'\s+\d+\s*$', '', text)  # Trailing page numbers
        text = re.sub(r'\([Cc]olor online\)', '', text)  # Color online notes
        text = re.sub(r'\([Cc]olour figure can be viewed at.*?\)', '', text)  # Color figure notes

        # Handle common patterns
        text = re.sub(r'^[:\-\.\s]+', '', text)  # Remove leading punctuation
        text = re.sub(r'[\.\s]*\([Ss]ee [Tt]ext\)', '', text)  # Remove "see text" notes

        # Clean up spacing
        text = re.sub(r'\s+', ' ', text).strip()

        # Limit length for very long captions
        if len(text) > 800:
            sentences = re.split(r'[.!?]+', text)
            if len(sentences) > 1:
                text = '. '.join(sentences[:3]) + '.'
            else:
                text = text[:800] + '...'

        return text

    def _calculate_confidence(self, label: str, caption: str) -> float:
        """Calculate confidence score for caption extraction"""
        score = 0.0

        # Base score for having a caption
        if caption and len(caption) > 10:
            score += 0.5

        # Bonus for proper label format
        if re.match(r'^(Figure|Fig\.?|Table)\s+\d+', label, re.IGNORECASE):
            score += 0.3

        # Bonus for reasonable caption length
        if 20 <= len(caption) <= 300:
            score += 0.2

        # Penalty for very short or very long captions
        if len(caption) < 20 or len(caption) > 500:
            score -= 0.2

        # Bonus for ending with period
        if caption.endswith('.'):
            score += 0.1

        # Bonus for containing descriptive words
        descriptive_words = ['showing', 'demonstrating', 'illustrating', 'depicting',
                           'represents', 'indicates', 'analysis', 'comparison', 'effect']
        if any(word in caption.lower() for word in descriptive_words):
            score += 0.2

        return min(1.0, max(0.0, score))

    def _deduplicate_captions(self, captions: List[Dict]) -> List[Dict]:
        """Remove duplicate captions based on similarity"""
        if not captions:
            return []

        unique_captions = []

        for caption in captions:
            is_duplicate = False

            for existing in unique_captions:
                # Check for duplicates based on number and similarity
                if (caption['number'] == existing['number'] and
                    self._text_similarity(caption['caption'], existing['caption']) > 0.8):
                    is_duplicate = True
                    # Keep the one with higher confidence
                    if caption['confidence'] > existing['confidence']:
                        unique_captions.remove(existing)
                        unique_captions.append(caption)
                    break

            if not is_duplicate:
                unique_captions.append(caption)

        return unique_captions

    def _text_similarity(self, text1: str, text2: str) -> float:
        """Calculate simple text similarity"""
        if not text1 or not text2:
            return 0.0

        # Simple word-based similarity
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        if not words1 or not words2:
            return 0.0

        intersection = words1.intersection(words2)
        union = words1.union(words2)

        return len(intersection) / len(union) if union else 0.0

def test_advanced_extractor():
    """Test the advanced caption extractor"""
    extractor = AdvancedCaptionExtractor()

    # Sample text with various caption formats
    test_text = """
    Figure 1. Wheat leaves infected with virus constructs. 10–12 dpi. 1—negative control, 2—empty
    vector control, 3—BSMV:GFP, 4—BSMV:00 (containing PDS sequence complementary to wheat
    PDS mRNA), 5—BSMV:01.

    The results show clear differences between treatments (Figure 1), thus demonstrating effective PDS silencing.

    Table 1. Summary of experimental conditions and results for each treatment showing
    significant differences in infection rates.

    Figure 2. Microscopy images showing cellular changes. A) Control cells, B) Treated cells
    demonstrating clear morphological differences.
    """

    figures = extractor.extract_figures_advanced(test_text)
    tables = extractor.extract_tables_advanced(test_text)

    print("🔍 Advanced Caption Extraction Test")
    print("=" * 50)

    print(f"\n📊 Found {len(figures)} figures:")
    for fig in figures:
        print(f"  • Figure {fig['number']} (confidence: {fig['confidence']:.2f})")
        print(f"    Caption: {fig['caption'][:80]}...")

    print(f"\n📋 Found {len(tables)} tables:")
    for tab in tables:
        print(f"  • Table {tab['number']} (confidence: {tab['confidence']:.2f})")
        print(f"    Caption: {tab['caption'][:80]}...")

if __name__ == "__main__":
    test_advanced_extractor()