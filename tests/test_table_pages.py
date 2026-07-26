#!/usr/bin/env python3
"""Tests for rendering the page a table sits on (network-free, synthetic PDFs).

A typeset table is vector text, not an embedded image, so the figure path never captures
it and `find_tables()` returns nothing on 1990s layouts. The whole page is rendered
instead, which cannot clip a row.
"""

import tempfile
import unittest
from pathlib import Path

try:
    import fitz
    from phiweaver.pdf import table_pages as tp
    HAS_FITZ = True
except ImportError:  # PyMuPDF not installed
    HAS_FITZ = False


def _doc(pages_text):
    """A real in-memory PDF, one page per string."""
    doc = fitz.open()
    for text in pages_text:
        page = doc.new_page()
        page.insert_text((72, 72), text)
    return doc


def _caption(number, start_pos, caption="Growth and pathogenicity of strains"):
    return {"number": number, "label": f"Table {number}", "caption": caption,
            "confidence": 0.9, "start_pos": start_pos, "end_pos": start_pos + 10}


@unittest.skipUnless(HAS_FITZ, "PyMuPDF not installed")
class PageOffsetTests(unittest.TestCase):
    def test_offsets_mirror_the_extractor_concatenation(self):
        doc = _doc(["page one text", "page two text"])
        offsets = tp.page_text_offsets(doc)
        self.assertEqual(offsets[0], 0)
        # second page starts after page one's text plus the joining newline
        self.assertEqual(offsets[1], len(doc[0].get_text()) + 1)

    def test_offset_maps_back_to_its_page(self):
        doc = _doc(["page one text", "page two text"])
        offsets = tp.page_text_offsets(doc)
        self.assertEqual(tp.page_for_offset(offsets, 0), 0)
        self.assertEqual(tp.page_for_offset(offsets, offsets[1] + 2), 1)

    def test_offset_before_the_first_page_clamps(self):
        self.assertEqual(tp.page_for_offset([0, 50], -5), 0)


@unittest.skipUnless(HAS_FITZ, "PyMuPDF not installed")
class RenderTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.out = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def test_renders_one_png_per_table(self):
        doc = _doc(["intro text", "Table I. Growth and pathogenicity"])
        offsets = tp.page_text_offsets(doc)
        entries, warnings = tp.render_table_pages(
            doc, [_caption("I", offsets[1])], self.out)
        self.assertEqual(warnings, [])
        self.assertEqual(len(entries), 1)
        e = entries[0]
        self.assertEqual(e["page"], 2)
        self.assertEqual(e["region"], "full-page")
        self.assertEqual(e["source"], "page-render")
        self.assertTrue((self.out / e["filename"]).exists())

    def test_two_tables_on_one_page_share_one_render(self):
        doc = _doc(["Table I. First. Table II. Second."])
        offsets = tp.page_text_offsets(doc)
        entries, _ = tp.render_table_pages(
            doc, [_caption("I", offsets[0]), _caption("II", offsets[0] + 5)], self.out)
        self.assertEqual(len(entries), 2)
        self.assertEqual(entries[0]["filename"], entries[1]["filename"])
        self.assertTrue(all(e["shared_page"] for e in entries))
        self.assertEqual(len(list(self.out.glob("*.png"))), 1)

    def test_a_table_alone_on_its_page_is_not_marked_shared(self):
        doc = _doc(["Table I. Only one here"])
        offsets = tp.page_text_offsets(doc)
        entries, _ = tp.render_table_pages(doc, [_caption("I", offsets[0])], self.out)
        self.assertFalse(entries[0]["shared_page"])

    def test_higher_dpi_produces_a_larger_image(self):
        doc = _doc(["Table I. Growth"])
        offsets = tp.page_text_offsets(doc)
        small, _ = tp.render_table_pages(
            doc, [_caption("I", offsets[0])], self.out / "lo", dpi=72)
        big, _ = tp.render_table_pages(
            doc, [_caption("I", offsets[0])], self.out / "hi", dpi=170)
        lo = (self.out / "lo" / small[0]["filename"]).stat().st_size
        hi = (self.out / "hi" / big[0]["filename"]).stat().st_size
        self.assertGreater(hi, lo)

    def test_no_tables_yields_nothing_and_no_warning(self):
        doc = _doc(["just prose"])
        entries, warnings = tp.render_table_pages(doc, [], self.out)
        self.assertEqual((entries, warnings), ([], []))

    def test_an_unrenderable_page_warns_instead_of_raising(self):
        doc = _doc(["Table I. Growth"])
        # a caption whose offset lands past the end of the document text
        entries, warnings = tp.render_table_pages(doc, [_caption("I", 10 ** 9)], self.out)
        self.assertEqual(entries, [])
        self.assertTrue(any("Table I" in w for w in warnings))


@unittest.skipUnless(HAS_FITZ, "PyMuPDF not installed")
class ConverterWiringTests(unittest.TestCase):
    def setUp(self):
        from phiweaver.pdf import pdf_convert as pc
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.skill = pc.PDFConvertSkill()
        self.skill.images_dir = Path(self._tmp.name)
        self.skill.pdf_name = "synthetic"

    def test_dpi_is_a_config_key(self):
        self.assertEqual(self.skill.config["table_render_dpi"], 170)

    def test_a_typeset_table_lands_in_all_tables(self):
        doc = _doc(["intro prose", "Table I. Growth and pathogenicity of strains on rice"])
        self.skill._extract_media_with_advanced_captions(doc)
        self.assertEqual(len(self.skill.all_tables), 1)
        entry = self.skill.all_tables[0]
        self.assertEqual(entry["source"], "page-render")
        self.assertTrue((self.skill.images_dir / entry["filename"]).exists())

    def test_a_paper_with_no_tables_stays_empty_and_silent(self):
        doc = _doc(["just prose with no tabular content at all"])
        self.skill._extract_media_with_advanced_captions(doc)
        self.assertEqual(self.skill.all_tables, [])
        self.assertEqual(self.skill.table_warnings, [])


@unittest.skipUnless(HAS_FITZ, "PyMuPDF not installed")
class FlatTextMarkerTests(unittest.TestCase):
    def setUp(self):
        from phiweaver.pdf import pdf_convert as pc
        self.skill = pc.PDFConvertSkill()
        self.skill.all_tables = [{
            "filename": "Table-p5.png", "type": "table", "page": 5, "number": "I",
            "caption": {"number": "I", "caption": "Growth"}, "region": "full-page",
            "source": "page-render", "shared_page": False,
        }]

    def test_marker_precedes_the_flattened_run(self):
        out = self.skill._mark_flattened_tables(
            ["Some prose.", "Table I. Growth and pathogenicity", "Guy11 0.28 AM25 0.27"])
        joined = "\n".join(out)
        self.assertIn("FLATTENED TABLE", joined)
        self.assertIn("Table-p5.png", joined)
        self.assertLess(joined.index("FLATTENED TABLE"), joined.index("Table I. Growth"))

    def test_nothing_is_deleted(self):
        original = ["Some prose.", "Table I. Growth and pathogenicity", "Guy11 0.28"]
        out = self.skill._mark_flattened_tables(list(original))
        for line in original:
            self.assertIn(line, out)

    def test_no_marker_when_the_paper_has_no_tables(self):
        self.skill.all_tables = []
        lines = ["Some prose.", "Table I. Growth"]
        self.assertEqual(self.skill._mark_flattened_tables(lines), lines)

    def test_only_the_first_occurrence_is_marked(self):
        out = self.skill._mark_flattened_tables(
            ["Table I. Growth", "prose referring to Table I again", "Table I. Growth"])
        self.assertEqual("\n".join(out).count("FLATTENED TABLE"), 1)


if __name__ == "__main__":
    unittest.main()
