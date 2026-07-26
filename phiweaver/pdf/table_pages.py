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
