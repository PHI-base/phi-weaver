# PDF Table Page Renders — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make a table-carrying PDF yield a readable image of every table, so a curator never has to reconstruct a column grid from flattened text.

**Architecture:** Fix the caption regex so tables are detected at all (the root cause), then render the whole page each table caption sits on to a PNG and feed it into the converter's existing — and currently empty — `all_tables` slot. The flattened body text stays, marked unreliable. Reporting counts captions and renders separately so a failure can never again look like "this paper has no tables".

**Tech Stack:** Python 3.12 stdlib + PyMuPDF (`fitz`) 1.27, `unittest`. No network.

**Spec:** `docs/superpowers/specs/2026-07-26-pdf-table-extraction-design.md`

## Global Constraints

- **Engine code lives in `phiweaver/`**, tests co-located in `tests/`. Derive paths from `phiweaver.repo_root()` or `__file__`; never hardcode `/mnt/z/...`.
- **Tests are network-free and must not depend on the literature corpus** — it lives outside the repo under `PHI_LITERATURE_ROOT` and is uncommitted. Build synthetic PDFs with `fitz` instead.
- **PyMuPDF is an optional import.** Follow `tests/test_pdf_captions.py`: wrap the import in `try/except ImportError` and skip the module when absent.
- **Green gate is `python3 -m phiweaver.smoke` alone** (it runs the unit suite as its last check). While iterating run the single module, e.g. `python3 -m unittest tests.test_table_pages`.
- **Never delete source text** from a converted document — annotate only.
- **Commits:** short imperative subject, no AI co-author or provenance trailer.
- **Default render dpi is `170`.**

---

### Task 1: Detect Roman-numeral and supplementary table captions

The root cause. On PMID:9927411 the extractor finds 22 figure captions and **0** table captions, because every table pattern requires `\d+` and the paper numbers its tables `Table I` / `Table II`. Until this is fixed there is nothing to render.

`[IVXL]` deliberately excludes `C`, `D` and `M`: no paper numbers tables past `XXXIX`, and those three letters start too many English words. `(?-i:...)` keeps the Roman branch case-sensitive even though the surrounding match is `IGNORECASE`, so the word "in" cannot be read as table `i`.

**Verified before writing this plan** — the proposed pattern accepts `Table I` → `I`, `Table S1` → `S1`, `Table 2` → `2`, `Table IV` → `IV`, `Table XII` → `XII`, and rejects `Table in the appendix` and `Table Interpretation of results`. It also rejects **lowercase** Roman (`table iii`), which is intended: captions capitalise their numbering, and accepting lowercase is exactly what would let "in" and "is" through. Do not "fix" this.

**Files:**
- Modify: `phiweaver/pdf/pdf_convert.py:19` (`CAPTION_BLOCK_RE`)
- Modify: `phiweaver/pdf/enhanced_caption_extractor.py:25-32` (`table_patterns`)
- Test: `tests/test_pdf_captions.py`

**Interfaces:**
- Consumes: nothing
- Produces: `CAPTION_BLOCK_RE` matching group(2) ∈ {`1`, `1a`, `I`, `S1`}; `AdvancedCaptionExtractor.extract_tables_advanced(text) -> List[Dict]` with `number` carrying the same forms. Dict keys unchanged: `number`, `label`, `caption`, `confidence`, `start_pos`, `end_pos`.

- [ ] **Step 1: Write the failing test**

Append to `tests/test_pdf_captions.py`:

```python
@unittest.skipUnless(HAS_FITZ, "PyMuPDF not installed")
class RomanAndSupplementaryTableNumbering(unittest.TestCase):
    """PMID:9927411 numbers its tables `Table I` / `Table II`, which `\\d+` cannot see."""

    def test_caption_block_re_accepts_roman(self):
        m = pc.CAPTION_BLOCK_RE.match("Table I. Growth and pathogenicity of strains")
        self.assertIsNotNone(m)
        self.assertEqual(m.group(2), "I")

    def test_caption_block_re_accepts_supplementary(self):
        m = pc.CAPTION_BLOCK_RE.match("Table S1 Primers used in this study")
        self.assertIsNotNone(m)
        self.assertEqual(m.group(2), "S1")

    def test_caption_block_re_still_accepts_arabic(self):
        m = pc.CAPTION_BLOCK_RE.match("Table 2. Strains and plasmids")
        self.assertIsNotNone(m)
        self.assertEqual(m.group(2), "2")

    def test_lowercase_word_is_not_read_as_a_roman_numeral(self):
        # "Table in the appendix" must not parse as table `i`
        self.assertIsNone(pc.CAPTION_BLOCK_RE.match("Table in the appendix lists"))

    def test_word_starting_with_a_roman_letter_is_not_a_number(self):
        self.assertIsNone(pc.CAPTION_BLOCK_RE.match("Table Interpretation of results"))

    def test_extractor_finds_a_roman_numbered_table(self):
        from phiweaver.pdf.enhanced_caption_extractor import AdvancedCaptionExtractor
        text = "Table I. Growth and pathogenicity of Magnaporthe grisea strains on rice\n\n"
        tables = AdvancedCaptionExtractor().extract_tables_advanced(text)
        self.assertEqual([t["number"] for t in tables], ["I"])

    def test_extractor_still_finds_an_arabic_table(self):
        from phiweaver.pdf.enhanced_caption_extractor import AdvancedCaptionExtractor
        text = "Table 1. Growth and pathogenicity of Magnaporthe grisea strains on rice\n\n"
        tables = AdvancedCaptionExtractor().extract_tables_advanced(text)
        self.assertEqual([t["number"] for t in tables], ["1"])
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests.test_pdf_captions.RomanAndSupplementaryTableNumbering -v`
Expected: FAIL — `test_caption_block_re_accepts_roman` gives `AssertionError: unexpectedly None`, and `test_extractor_finds_a_roman_numbered_table` gives `[] != ['I']`.

- [ ] **Step 3: Write minimal implementation**

In `phiweaver/pdf/pdf_convert.py`, replace the `CAPTION_BLOCK_RE` definition (line 19) and its comment:

```python
# A caption line begins its own text block: "Figure 3. ..." / "Table 1 ..." / "Fig. 2 ...".
# The number may be Arabic ("1", "1a"), supplementary ("S1") or Roman ("I", "IV") — 1990s
# journals number tables in Roman, and requiring \d+ made those tables invisible entirely.
# `(?-i:[IVXL]+)` stays case-sensitive inside the IGNORECASE match so the word "in" is not
# read as table `i`; C/D/M are excluded because they start too many English words and no
# paper numbers tables past XXXIX.
CAPTION_NUMBER = r"(\d+[A-Za-z]*|S\d+[A-Za-z]*|(?-i:[IVXL]+))\b"
CAPTION_BLOCK_RE = re.compile(r"^\s*(figure|fig\.?|table)\s*" + CAPTION_NUMBER, re.IGNORECASE)
```

In `phiweaver/pdf/enhanced_caption_extractor.py`, add the shared fragment above the class (after the imports):

```python
# Same numbering forms the converter's CAPTION_BLOCK_RE accepts — Arabic, supplementary,
# Roman. Kept as one capturing group so the existing group indices are unchanged.
CAPTION_NUMBER = r"(\d+[A-Za-z]*|S\d+[A-Za-z]*|(?-i:[IVXL]+))"
```

and replace the three entries of `self.table_patterns` with:

```python
        self.table_patterns = [
            # Standard table patterns
            r'(Table\s+' + CAPTION_NUMBER + r'\.?\s*[\:\-\.\s]*)(.*?)(?=\n\s*\n|\n\s*(?:Table|Figure|References|\d+\.|[A-Z]{2,})|$)',
            r'(TABLE\s+' + CAPTION_NUMBER + r'\.?\s*[\:\-\.\s]*)(.*?)(?=\n\s*\n|\n\s*(?:TABLE|FIGURE|REFERENCES)|$)',

            # Extended patterns
            r'([Tt]able\s+' + CAPTION_NUMBER + r'[\.\:\s]*[–\-]?\s*)([\s\S]*?)(?=\n\s*[Tt]able|\n\s*[Ff]igure|\n\s*\d+\.|\n\s*[A-Z][A-Z]|\n\s*References|$)',
        ]
```

Note the outer `(...)` wrapping each pattern is the label group and `CAPTION_NUMBER` is the number group, so `match.group(1)`/`group(2)`/`group(3)` keep their current meanings.

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m unittest tests.test_pdf_captions -v`
Expected: PASS, including every pre-existing test in the file (the figure patterns are untouched).

- [ ] **Step 5: Commit**

```bash
git add phiweaver/pdf/pdf_convert.py phiweaver/pdf/enhanced_caption_extractor.py tests/test_pdf_captions.py
git commit -m "Detect Roman-numeral and supplementary table captions"
```

---

### Task 2: Render the page a table sits on

**Files:**
- Create: `phiweaver/pdf/table_pages.py`
- Test: `tests/test_table_pages.py`

**Interfaces:**
- Consumes: caption dicts from Task 1 — `{'number', 'label', 'caption', 'confidence', 'start_pos', 'end_pos'}`.
- Produces:
  - `DEFAULT_TABLE_DPI: int = 170`
  - `page_text_offsets(doc) -> List[int]`
  - `page_for_offset(offsets: List[int], pos: int) -> int` (0-based page index)
  - `render_table_pages(doc, tables, images_dir, prefix="Table", dpi=DEFAULT_TABLE_DPI) -> Tuple[List[Dict], List[str]]` returning `(entries, warnings)`, where each entry is
    `{'filename', 'type': 'table', 'page' (1-based), 'number', 'caption', 'region': 'full-page', 'source': 'page-render', 'shared_page': bool}`.

Why `page_text_offsets` exists: the caption dicts carry `start_pos` into the concatenated document text and **no page number**. `_extract_media_with_advanced_captions` builds that string as `page.get_text() + "\n"` per page, so this helper must mirror that exactly (hence the `+ 1` for the joining newline).

- [ ] **Step 1: Write the failing test**

Create `tests/test_table_pages.py`:

```python
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


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests.test_table_pages -v`
Expected: FAIL at import — `ModuleNotFoundError: No module named 'phiweaver.pdf.table_pages'`, so the whole module skips or errors.

- [ ] **Step 3: Write minimal implementation**

Create `phiweaver/pdf/table_pages.py`:

```python
#!/usr/bin/env python3
"""Render the page a table sits on.

A typeset table is vector text with ruled lines, not an embedded image, so the converter's
figure path — which walks `page.get_images()` — never captures one. PyMuPDF's
`find_tables()` is not a way out either: measured on PMID:9927411 (1999) it detects zero
tables across all ten pages.

So the whole page is rendered instead. It cannot clip a row, which a caption-anchored crop
can — and losing a row is the exact defect this closes (Table I's "Appressorium formation
>95%" row existed only in the page render). The cost is that the image carries the
surrounding body text too, and two tables on one page share one render.

Pure PyMuPDF + stdlib. No network, no state.
"""

from __future__ import annotations

import bisect
from pathlib import Path
from typing import Dict, List, Tuple

import fitz

# Matches the manual practice the backlog prescribes for table-carrying papers.
DEFAULT_TABLE_DPI = 170


def page_text_offsets(doc) -> List[int]:
    """Character offset at which each page's text starts in the concatenated document text.

    Caption dicts carry `start_pos` into that concatenation and no page number, so this is
    the only route back from a caption to its page. It must mirror how the caller builds
    the string — `page.get_text() + "\\n"` per page — hence the `+ 1`.
    """
    offsets, running = [], 0
    for page in doc:
        offsets.append(running)
        running += len(page.get_text()) + 1
    return offsets


def page_for_offset(offsets: List[int], pos: int) -> int:
    """The 0-based page index containing `pos`; clamped at the first page."""
    return max(0, bisect.bisect_right(offsets, pos) - 1)


def render_table_pages(doc, tables: List[Dict], images_dir, prefix: str = "Table",
                       dpi: int = DEFAULT_TABLE_DPI) -> Tuple[List[Dict], List[str]]:
    """Render one PNG per table caption. Returns (entries, warnings).

    Tables whose captions land on the same page share a single render — the file is written
    once and both entries point at it, flagged `shared_page` so the markdown can say so.
    """
    entries: List[Dict] = []
    warnings: List[str] = []
    if not tables:
        return entries, warnings

    images_dir = Path(images_dir)
    images_dir.mkdir(parents=True, exist_ok=True)
    offsets = page_text_offsets(doc)
    end_of_text = offsets[-1] + len(doc[-1].get_text()) if offsets else 0

    rendered: Dict[int, str] = {}          # page index -> filename
    page_tally: Dict[int, int] = {}
    for table in tables:
        number = str(table.get("number") or "?")
        pos = table.get("start_pos")
        if pos is None or pos > end_of_text:
            warnings.append(f"Table {number}: caption position does not fall on any page; "
                            f"no image rendered")
            continue
        page_index = page_for_offset(offsets, pos)
        if page_index not in rendered:
            filename = f"{prefix}-p{page_index + 1}.png"
            try:
                pix = doc[page_index].get_pixmap(dpi=dpi)
                pix.save(str(images_dir / filename))
            except Exception as exc:                      # a damaged page must not abort
                warnings.append(f"Table {number}: page {page_index + 1} could not be "
                                f"rendered ({exc})")
                continue
            rendered[page_index] = filename
        page_tally[page_index] = page_tally.get(page_index, 0) + 1
        entries.append({
            "filename": rendered[page_index],
            "type": "table",
            "page": page_index + 1,
            "number": number,
            "caption": table,
            "region": "full-page",
            "source": "page-render",
            "shared_page": False,
        })

    for entry in entries:                                  # known only once all are placed
        entry["shared_page"] = page_tally[entry["page"] - 1] > 1
    return entries, warnings
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m unittest tests.test_table_pages -v`
Expected: PASS, 9 tests.

- [ ] **Step 5: Commit**

```bash
git add phiweaver/pdf/table_pages.py tests/test_table_pages.py
git commit -m "Render the page a table sits on"
```

---

### Task 3: Feed page renders into the converter's table slot

The converter already has the slot end to end — `self.all_tables`, the `table_prefix` config key, `_caption_for_number(..., 'table', ...)` and `_generate_tables_section()`. It is empty, not missing. A table that genuinely *is* an embedded image still goes through the existing path; renders fill only the gaps, so nothing is counted twice.

**Files:**
- Modify: `phiweaver/pdf/pdf_convert.py` — `_load_default_config` (add `table_render_dpi`) and the end of `_extract_media_with_advanced_captions`
- Test: `tests/test_table_pages.py`

**Interfaces:**
- Consumes: `table_pages.render_table_pages(...)` from Task 2.
- Produces: `PDFConvertSkill.all_tables` populated with the entry dicts from Task 2; `PDFConvertSkill.table_warnings: List[str]` for Task 5.

- [ ] **Step 1: Write the failing test**

Append to `tests/test_table_pages.py`:

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests.test_table_pages.ConverterWiringTests -v`
Expected: FAIL — `KeyError: 'table_render_dpi'` on the first test, and `AttributeError: 'PDFConvertSkill' object has no attribute 'table_warnings'` on the third.

- [ ] **Step 3: Write minimal implementation**

In `phiweaver/pdf/pdf_convert.py`, add the dpi key to `_load_default_config`'s returned dict, right after `'table_prefix': 'Table',`:

```python
            'table_render_dpi': 170,
```

In `__init__`, beside `self.all_tables = []`, add:

```python
        self.table_warnings = []
```

At the **end** of `_extract_media_with_advanced_captions` (after the page/image loop completes), append:

```python
        # A typeset table is not an embedded image, so the loop above cannot have found it.
        # Render the page for every table caption the image path did not already cover —
        # `find_tables()` is no help here (zero hits on the 1999 trigger paper), and a crop
        # could clip a row, which is the defect being closed.
        from phiweaver.pdf.table_pages import render_table_pages

        already = {str(t.get('number')) for t in self.all_tables}
        missing = [t for t in tables if str(t.get('number')) not in already]
        rendered, warnings = render_table_pages(
            doc, missing, self.images_dir,
            prefix=self.config['table_prefix'],
            dpi=self.config['table_render_dpi'])
        self.all_tables.extend(rendered)
        self.table_warnings.extend(warnings)
        for entry in rendered:
            print(f"  📊 Table {entry['number']}: page {entry['page']} rendered "
                  f"({entry['filename']})")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m unittest tests.test_table_pages -v`
Expected: PASS, 12 tests.

- [ ] **Step 5: Commit**

```bash
git add phiweaver/pdf/pdf_convert.py tests/test_table_pages.py
git commit -m "Fill the converter's empty table slot with page renders"
```

---

### Task 4: Mark the flattened table text as unreliable

The flattened run stays — it carries searchable numbers — but it must not read as ordinary body text, because that is what dropped Table I's ">95%" row. The marker is a pure string→string transform so it can be tested without a PDF, and it is applied in **both** body-generation paths, since which one runs depends on whether section detection succeeded.

**Files:**
- Modify: `phiweaver/pdf/pdf_convert.py` — new `_mark_flattened_tables`, called from `_generate_sectioned_content` and `_generate_page_based_content`
- Test: `tests/test_table_pages.py`

**Interfaces:**
- Consumes: `self.all_tables` entries from Task 3.
- Produces: `PDFConvertSkill._mark_flattened_tables(lines: List[str]) -> List[str]`.

- [ ] **Step 1: Write the failing test**

Append to `tests/test_table_pages.py`:

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests.test_table_pages.FlatTextMarkerTests -v`
Expected: FAIL — `AttributeError: 'PDFConvertSkill' object has no attribute '_mark_flattened_tables'`.

- [ ] **Step 3: Write minimal implementation**

Add the method to `PDFConvertSkill` in `phiweaver/pdf/pdf_convert.py`, next to the other `_generate_*` helpers:

```python
    def _mark_flattened_tables(self, lines):
        """Warn before each table's flattened run; never delete it.

        PDF text extraction loses a table's column grid, so the numbers arrive as a flat
        run that reads like ordinary prose — which is how a row goes missing unnoticed.
        The text is kept (it is searchable, and deleting risks eating real prose) and the
        page render is named as the authority.
        """
        if not self.all_tables:
            return lines

        pending = {}
        for entry in self.all_tables:
            pending.setdefault(str(entry.get('number')), entry)

        out = []
        for line in lines:
            match = CAPTION_BLOCK_RE.match(line)
            if match and match.group(1).lower().startswith('table'):
                entry = pending.pop(match.group(2), None)
                if entry:
                    out.extend([
                        f"> ⚠ **FLATTENED TABLE — column structure lost.** Read "
                        f"`{entry['filename']}` (page {entry['page']}) instead; rows may be "
                        f"missing from the text below.",
                        "",
                    ])
            out.append(line)
        return out
```

Then apply it at the end of both body generators. In `_generate_sectioned_content`, change the final `return content` to:

```python
        return self._mark_flattened_tables(content)
```

and make the identical change to the final `return content` of `_generate_page_based_content`.

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m unittest tests.test_table_pages -v`
Expected: PASS, 16 tests.

- [ ] **Step 5: Commit**

```bash
git add phiweaver/pdf/pdf_convert.py tests/test_table_pages.py
git commit -m "Mark a table's flattened text as unreliable"
```

---

### Task 5: Report captions and renders separately

Today `tables_found: 0` means "extraction failed" but reads as "this paper has no tables". That silence is why the defect survived a full curation. Counting captions and renders separately makes a failure state itself.

**Files:**
- Modify: `phiweaver/pdf/pdf_convert.py` — `_generate_structured_markdown` frontmatter and the report-JSON builder
- Test: `tests/test_table_pages.py`

**Interfaces:**
- Consumes: `self.all_tables`, `self.table_warnings` from Tasks 3–4.
- Produces: frontmatter keys `tables`, `table_captions`, `tables_rendered`; report `statistics.table_captions_found`, `statistics.tables_rendered`, and `warnings`.

- [ ] **Step 1: Write the failing test**

First locate the report builder: `grep -n "tables_found" phiweaver/pdf/pdf_convert.py`. Append to `tests/test_table_pages.py`:

```python
@unittest.skipUnless(HAS_FITZ, "PyMuPDF not installed")
class ReportHonestyTests(unittest.TestCase):
    def setUp(self):
        from phiweaver.pdf import pdf_convert as pc
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.skill = pc.PDFConvertSkill()
        self.skill.images_dir = Path(self._tmp.name)
        self.skill.pdf_name = "synthetic"
        self.skill.pdf_path = Path(self._tmp.name) / "synthetic.pdf"

    def test_frontmatter_separates_captions_from_renders(self):
        doc = _doc(["intro", "Table I. Growth and pathogenicity of strains on rice"])
        self.skill._extract_media_with_advanced_captions(doc)
        md = self.skill._generate_structured_markdown(doc)
        self.assertIn("table_captions: 1", md)
        self.assertIn("tables_rendered: 1", md)

    def test_a_caption_with_no_render_is_warned_about(self):
        self.skill.all_tables = []
        self.skill.table_warnings = ["Table I: page 5 could not be rendered (boom)"]
        report = self.skill._build_report()
        self.assertEqual(report["statistics"]["tables_rendered"], 0)
        self.assertTrue(report["warnings"])

    def test_a_paper_with_no_tables_reports_zero_without_warning(self):
        self.skill.all_tables = []
        self.skill.table_warnings = []
        report = self.skill._build_report()
        self.assertEqual(report["statistics"]["tables_rendered"], 0)
        self.assertEqual(report["warnings"], [])
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests.test_table_pages.ReportHonestyTests -v`
Expected: FAIL — `table_captions: 1` absent from the frontmatter, and `AttributeError` on `_build_report` if the report is built inline rather than in a named method.

- [ ] **Step 3: Write minimal implementation**

In `_generate_structured_markdown`, replace the single `f"tables: {len(self.all_tables)}",` frontmatter line with:

```python
            f"tables: {len(self.all_tables)}",
            f"table_captions: {self.table_caption_count}",
            f"tables_rendered: {sum(1 for t in self.all_tables if t.get('source') == 'page-render')}",
```

Record the caption count in `_extract_media_with_advanced_captions`, immediately after `tables = extractor.extract_tables_advanced(full_text)`:

```python
        self.table_caption_count = len(tables)
```

and initialise `self.table_caption_count = 0` in `__init__` beside `self.table_warnings`.

If the report JSON is assembled inline, extract it into a `_build_report(self)` method returning the dict (leaving the caller writing `json.dump(self._build_report(), ...)`), then add to its `statistics`:

```python
            'table_captions_found': self.table_caption_count,
            'tables_rendered': sum(1 for t in self.all_tables
                                   if t.get('source') == 'page-render'),
```

and a top-level key, so a failure survives the run rather than scrolling past:

```python
            'warnings': list(self.table_warnings),
```

Finally, print the mismatch during conversion — the converter already prints per-figure lines, so this belongs beside them. At the end of `_extract_media_with_advanced_captions`:

```python
        if self.table_caption_count > len(self.all_tables):
            missing = self.table_caption_count - len(self.all_tables)
            print(f"   ⚠ {missing} table caption(s) found with no image — see the report's "
                  f"warnings; do not treat the flattened text as the table")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m unittest tests.test_table_pages -v`
Expected: PASS, 19 tests.

- [ ] **Step 5: Run the full gate**

Run: `python3 -m phiweaver.smoke`
Expected: `SMOKE TEST PASSED — all 8 checks green.`

- [ ] **Step 6: Commit**

```bash
git add phiweaver/pdf/pdf_convert.py tests/test_table_pages.py
git commit -m "Count table captions and renders separately so a miss is visible"
```

---

### Task 6: Verify against the real paper, then close the backlog item

The corpus cannot live in the repo, so this end-to-end check is run by hand and its result recorded in the backlog rather than in a test.

**Files:**
- Modify: `docs/BACKLOG.md` (the "PDF converter flattens tables" item)

- [ ] **Step 1: Re-convert the trigger paper**

```bash
python3 -m phiweaver.pipeline.curation_pipeline process-paper \
  "/mnt/z/PHI-Canto-Literature/active/PMID9927411_Urban1999_MgABC1.pdf"
```

Expected: 2 table captions found (`Table I`, `Table II`), 2 page renders written under
`03-Media/PMID9927411_Urban1999_MgABC1/`, and a report whose `table_captions_found` is 2 rather than the previous `tables_found: 0`.

- [ ] **Step 2: Confirm the renders are legible**

Open both PNGs and check that Table I's **"Appressorium formation >95%" row** — the row lost entirely in the flattened text — is visible, and that Table II shows EC50/MIC columns for the wild type only. If a render is unreadable, raise `table_render_dpi` and re-run before proceeding.

- [ ] **Step 3: Record the result and close the item**

Tick the backlog item, stating: the root cause was the Arabic-only caption regex (not the extraction path); `find_tables()` measured zero on this paper; and what the re-conversion produced. Note the residual — the image carries surrounding body text, and two tables on one page share one render.

- [ ] **Step 4: Commit**

```bash
git add docs/BACKLOG.md
git commit -m "Close the PDF table item: tables now arrive as page renders"
```

---

## Self-review

**Spec coverage:** component 1 → Task 1; component 2 → Task 2; component 3 → Task 3; component 4 → Task 4; component 5 → Task 5; the spec's manual end-to-end check → Task 6. The spec's "follow-on, not included" (drafting-workflow provenance) is deliberately absent.

**Placeholder scan:** none — every step carries the actual regex, code or command.

**Type consistency:** the entry dict defined in Task 2 (`filename`, `type`, `page`, `number`, `caption`, `region`, `source`, `shared_page`) is the same shape consumed in Tasks 3, 4 and 5. `table_warnings` and `table_caption_count` are initialised in Task 3 and Task 5 respectively and read in Task 5. `CAPTION_BLOCK_RE` group(2) from Task 1 is what Task 4's marker matches on.

**Known soft spot:** Task 5 Step 3 assumes the report JSON may be built inline and asks the implementer to extract `_build_report`. That is the one place the plan cannot name exact line numbers, because the builder's current location must be found with the `grep` given in Step 1.
