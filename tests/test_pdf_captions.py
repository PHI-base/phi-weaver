#!/usr/bin/env python3
"""Tests for PDF figure/caption matching.

These pin the bug that lost 15 of 17 images on PMID:42089373: captions were matched from
a document-wide list by a per-page index, so nearly every image resolved to the same
caption and overwrote the previous file. The fix matches by position on the page and
guarantees a unique filename.

The module needs PyMuPDF to import, so the whole file skips when it is absent; the logic
under test is exercised with lightweight fakes rather than real PDFs.
"""

import unittest

try:
    from phiweaver.pdf import pdf_convert as pc
    HAS_FITZ = True
except ImportError:  # PyMuPDF not installed
    HAS_FITZ = False


class _Rect:
    """Minimal stand-in for fitz.Rect — only y0/y1 matter to the matcher."""

    def __init__(self, y0, y1):
        self.y0, self.y1 = y0, y1


class _Page:
    def __init__(self, blocks=(), rect=None):
        self._blocks = list(blocks)
        self._rect = rect

    def get_text(self, kind):
        return self._blocks

    def get_image_rects(self, xref):
        return [self._rect] if self._rect else []


def _block(text, y0, y1):
    return (0.0, y0, 100.0, y1, text, 0, 0)


@unittest.skipUnless(HAS_FITZ, "PyMuPDF not installed")
class CaptionRegexTests(unittest.TestCase):
    def test_matches_common_caption_openings(self):
        for text, kind, number in (
            ("Figure 1. Mycelial growth of FpSdh deletion mutants.", "figure", "1"),
            ("Fig. 2 Conidiation and virulence", "figure", "2"),
            ("Fig 12 something", "figure", "12"),
            ("Table 3. Primers used in this study", "table", "3"),
        ):
            m = pc.CAPTION_BLOCK_RE.match(text)
            self.assertIsNotNone(m, text)
            self.assertEqual(m.group(2), number)
            self.assertEqual(
                "table" if m.group(1).lower().startswith("table") else "figure", kind)

    def test_ignores_mid_sentence_references(self):
        # "...as shown in Figure 3" must not be treated as a caption block.
        self.assertIsNone(pc.CAPTION_BLOCK_RE.match("as shown in Figure 3, the mutant"))

    def test_ignores_unnumbered_text(self):
        self.assertIsNone(pc.CAPTION_BLOCK_RE.match("Figures were prepared in Prism"))


@unittest.skipUnless(HAS_FITZ, "PyMuPDF not installed")
class PageCaptionBlockTests(unittest.TestCase):
    def _skill(self):
        return pc.PDFConvertSkill()

    def test_finds_captions_with_positions(self):
        page = _Page([_block("Figure 1. Growth of mutants.", 500, 520),
                      _block("Some body text about results.", 200, 240),
                      _block("Table 2. Primer list", 600, 615)])
        blocks = self._skill()._page_caption_blocks(page)
        self.assertEqual([(b["kind"], b["number"]) for b in blocks],
                         [("figure", "1"), ("table", "2")])
        self.assertEqual(blocks[0]["y0"], 500)

    def test_page_with_no_captions_yields_none(self):
        page = _Page([_block("Body text only", 100, 140)])
        self.assertEqual(self._skill()._page_caption_blocks(page), [])


@unittest.skipUnless(HAS_FITZ, "PyMuPDF not installed")
class GeometryMatchTests(unittest.TestCase):
    def _skill(self):
        return pc.PDFConvertSkill()

    def test_figure_caption_below_the_image_matches(self):
        page = _Page(rect=_Rect(100, 400))
        captions = [{"kind": "figure", "number": "1", "y0": 410, "y1": 430}]
        match = self._skill()._match_by_geometry(page, (1,), captions)
        self.assertEqual(match["number"], "1")

    def test_figure_caption_above_the_image_is_rejected(self):
        # Journal convention: figure captions sit below their artwork.
        page = _Page(rect=_Rect(400, 700))
        captions = [{"kind": "figure", "number": "1", "y0": 100, "y1": 120}]
        self.assertIsNone(self._skill()._match_by_geometry(page, (1,), captions))

    def test_table_caption_above_the_image_matches(self):
        page = _Page(rect=_Rect(400, 700))
        captions = [{"kind": "table", "number": "2", "y0": 360, "y1": 380}]
        match = self._skill()._match_by_geometry(page, (1,), captions)
        self.assertEqual(match["number"], "2")

    def test_nearest_caption_wins(self):
        page = _Page(rect=_Rect(100, 300))
        captions = [{"kind": "figure", "number": "9", "y0": 500, "y1": 515},
                    {"kind": "figure", "number": "3", "y0": 310, "y1": 325}]
        self.assertEqual(
            self._skill()._match_by_geometry(page, (1,), captions)["number"], "3")

    def test_distant_caption_does_not_match(self):
        # An image with no caption near it must stay unmatched, not adopt a far one.
        page = _Page(rect=_Rect(50, 80))
        captions = [{"kind": "figure", "number": "1",
                     "y0": 80 + pc.MAX_CAPTION_DISTANCE + 50, "y1": 800}]
        self.assertIsNone(self._skill()._match_by_geometry(page, (1,), captions))

    def test_unlocatable_image_does_not_match(self):
        page = _Page(rect=None)
        captions = [{"kind": "figure", "number": "1", "y0": 10, "y1": 20}]
        self.assertIsNone(self._skill()._match_by_geometry(page, (1,), captions))


@unittest.skipUnless(HAS_FITZ, "PyMuPDF not installed")
class FilenameUniquenessTests(unittest.TestCase):
    """The data-loss guard: a name is never reused, whatever the caption match says."""

    def _skill(self):
        return pc.PDFConvertSkill()

    def test_first_use_keeps_the_plain_name(self):
        self.assertEqual(self._skill()._unique_name("Fig03", ".png", set()), "Fig03.png")

    def test_collision_gets_a_letter_not_an_overwrite(self):
        used = {"Fig03.png"}
        self.assertEqual(self._skill()._unique_name("Fig03", ".png", used), "Fig03b.png")

    def test_repeated_collisions_keep_going(self):
        used = {"Fig03.png", "Fig03b.png", "Fig03c.png"}
        self.assertEqual(self._skill()._unique_name("Fig03", ".png", used), "Fig03d.png")

    def test_exhausted_letters_fall_back_to_numbers(self):
        used = {"Fig03.png"} | {f"Fig03{c}.png" for c in "bcdefghijklmnopqrstuvwxyz"}
        self.assertEqual(self._skill()._unique_name("Fig03", ".png", used), "Fig03-2.png")

    def test_unmatched_image_gets_a_positional_name_and_is_kept(self):
        skill = self._skill()
        page = _Page(rect=None)
        name, kind, number = skill._get_smart_filename(page, 11, 0, (1,), [], set())
        self.assertEqual(name, "page-12-img-01.png")
        self.assertEqual(number, "")

    def test_two_unmatched_images_on_a_page_do_not_collide(self):
        skill = self._skill()
        page = _Page(rect=None)
        used = set()
        first, _, _ = skill._get_smart_filename(page, 23, 0, (1,), [], used)
        used.add(first)
        second, _, _ = skill._get_smart_filename(page, 23, 1, (2,), [], used)
        self.assertNotEqual(first, second)


@unittest.skipUnless(HAS_FITZ, "PyMuPDF not installed")
class CaptionLookupTests(unittest.TestCase):
    def test_caption_is_looked_up_by_number_not_position(self):
        skill = pc.PDFConvertSkill()
        figures = [{"number": "1", "caption": "first"}, {"number": "5", "caption": "fifth"}]
        self.assertEqual(
            skill._caption_for_number("5", "figure", figures, [])["caption"], "fifth")

    def test_unknown_number_yields_none(self):
        skill = pc.PDFConvertSkill()
        self.assertIsNone(skill._caption_for_number("9", "figure", [], []))
        self.assertIsNone(skill._caption_for_number("", "figure", [], []))


class TokenEstimateCapTests(unittest.TestCase):
    """Large images are downscaled before billing; the estimate must model that."""

    def _jpeg(self, w, h):
        import struct
        import tempfile
        from pathlib import Path
        d = tempfile.TemporaryDirectory()
        self.addCleanup(d.cleanup)
        p = Path(d.name) / "f.jpg"
        p.write_bytes(b"\xff\xd8" + b"\xff\xc0\x00\x11\x08"
                      + struct.pack(">HH", h, w) + b"\x03" * 8)
        return p

    def test_small_image_is_priced_at_raw_pixels(self):
        from phiweaver.figure_ledger import estimate_tokens
        self.assertEqual(estimate_tokens(self._jpeg(750, 300)), 300)

    def test_print_resolution_figure_is_capped(self):
        # 2088x1533 = 3.2 MP: raw pixels would say ~4268, the real cost is ~1533.
        from phiweaver.figure_ledger import estimate_tokens
        tokens = estimate_tokens(self._jpeg(2088, 1533))
        self.assertLess(tokens, 1600)
        self.assertGreater(tokens, 1400)

    def test_very_long_thin_image_is_capped_by_edge_not_area(self):
        from phiweaver.figure_ledger import estimate_tokens
        self.assertLessEqual(estimate_tokens(self._jpeg(6000, 200)), 1600)

    def test_zero_dimensions_do_not_divide_by_zero(self):
        from phiweaver.figure_ledger import estimate_tokens
        self.assertEqual(estimate_tokens(self._jpeg(0, 0)), 0)


if __name__ == "__main__":
    unittest.main()
