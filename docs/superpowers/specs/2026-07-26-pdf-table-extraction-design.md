---
created: 2026-07-26
type: documentation
tags: [docs, design-spec]
project: PHI-Weaver
---

# Design — capture tables from PDFs as page renders

Closes the `docs/BACKLOG.md` tooling item *"PDF converter flattens tables and loses their
columns"* (added 2026-07-24, surfaced on PMID:9927411).

## Why this matters

On PMID:9927411 the tables carried **most of the quantitative evidence**, and the single most
consequential finding of the whole curation was a statement *about the column structure*: Table II
lists EC50/MIC for the wild type only, with **no per-strain columns**, so the paper's headline "no
drug hypersensitivity" claim has no visible supporting data. A reader of the flattened text cannot
see that. Table I's "Appressorium formation >95%" row was dropped entirely and exists only in the
page render.

## What exploration found (2026-07-26)

The backlog recorded one failure. There are three, and the first is the root cause.

1. **Caption detection is Arabic-only.** `CAPTION_BLOCK_RE` (`phiweaver/pdf/pdf_convert.py:19`) is
   `^\s*(figure|fig\.?|table)\s*(\d+)`, and `AdvancedCaptionExtractor` matches the same way. The
   paper numbers its tables **Table I / Table II**, so on PMID:9927411 the extractor finds
   **22 figure captions and 0 table captions**. The converter does not believe the paper has any
   tables.
2. **A typeset table produces no image.** The extraction path walks `page.get_images()`, so it only
   ever captures a table that was *pasted in as artwork*. A table set as vector text with ruled
   lines yields nothing, and its numbers flow into the body as a flat run.
3. **`find_tables()` does not rescue it.** Measured on the trigger PDF with PyMuPDF 1.27.2:
   **zero tables detected across all 10 pages**. The backlog's guess was "unreliable on
   scanned/ruled 1990s layouts"; the measurement is stronger than that — it finds nothing.

The failure is also **silent**: `PMID9927411_Urban1999_MgABC1_converted_report.json` records
`tables_found: 0`, which reads as "this paper has no tables" rather than "extraction failed".

**What already works.** The converter has a table slot end to end — `self.all_tables`, a
`table_prefix` config key, `_caption_for_number(..., 'table', ...)` and
`_generate_tables_section()`. The slot is *empty*, not missing. Nothing downstream needs building.

## Decisions

Settled with the curator, 2026-07-26:

| Question | Decision |
|---|---|
| What does the curator need? | **A faithful image per table.** Preserves the column grid exactly as printed, and cannot silently mangle a number. |
| Which region is rendered? | **The whole page**, at ~170 dpi. Cannot ever clip a row; matches the manual practice the backlog prescribes. |
| What about the flattened text? | **Left in place, marked unreliable.** Nothing is deleted; the marker says the image is authoritative. |

**Why not structured extraction.** A parser that returns rows and columns is machine-readable, but
on this class of paper it returns nothing, and a *partial* parse drops a row silently — which is
precisely how "Appressorium formation >95%" was lost. An image cannot fail that way: it is either
there or it is not.

**Why the whole page and not a crop.** A caption-anchored crop gives one clean image per table, but
a boundary heuristic decides where the table ends, and a wrong boundary clips data — reproducing
the bug being fixed. The whole page trades tidiness for a guarantee.

## Architecture

New module **`phiweaver/pdf/table_pages.py`**, called from the existing extraction path.
`pdf_convert.py` is already 805 lines and does document analysis, media extraction, caption
geometry and markdown generation; the render logic is a separate job with one input and one output,
and it is easier to test standing alone.

### Components

1. **Caption numbering (`pdf_convert.py`, `enhanced_caption_extractor.py`)** — widen both patterns
   to accept Roman numerals and supplementary labels: `Table I`, `Table S1`, `Table 1a`. This is
   the root-cause fix and is independent of rendering: without it there is nothing to render.

2. **`table_pages.py`** — given an open document and the detected table captions, render one PNG
   per table caption at a configurable dpi (default **170**). Pure PyMuPDF, no network, no state.
   Two tables whose captions land on the same page share a single render. The dpi is set through
   the converter's existing config dict — a new `table_render_dpi` key alongside `table_prefix` —
   so it is overridable the same way every other converter setting is.

3. **Wiring (`_extract_media_with_advanced_captions`)** — populate `all_tables` with the dict shape
   the figure path already uses (`filename`, `type`, `page`, `number`, `caption`), plus
   `region: "full-page"` and `source: "page-render"` so the record states how the image was
   obtained. `_generate_tables_section()` consumes it unchanged.

4. **Flat-text marker** — wrap the flattened run in the body with a blockquote warning that the
   column structure is lost, naming the image to read instead. Nothing is deleted. Applied in
   **both** body-generation paths — `_generate_sectioned_content` and
   `_generate_page_based_content` — since which one runs depends on whether section detection
   succeeded, and the marker must not depend on that.

5. **Honest reporting (`_generate_structured_markdown`, the report JSON)** — count table
   *captions* found and images *rendered* separately, and warn when they disagree. A paper with
   genuinely no tables stays a silent `0`. The disagreement warning goes to **both** the report
   JSON (a `warnings` list, so it survives the run) and stdout (so it is seen during conversion),
   matching how the converter already prints per-figure extraction lines.

### Data flow

```
PDF
 └→ caption extraction (figures + tables)          ← component 1 makes tables visible here
     └→ per table caption: note its page
         └→ render page at dpi → 03-Media/<stem>/Table01.png   ← component 2
             └→ append to all_tables                            ← component 3
                 ├→ markdown "Tables" section (existing renderer)
                 ├→ body flat-text marker                       ← component 4
                 └→ report JSON + frontmatter counts            ← component 5
```

### Error handling

- A page that cannot be rendered is recorded as a warning in the report; it never raises.
- Two tables on one page share one image, and the markdown says so rather than implying two.
- Body text is never deleted — only annotated.
- A table caption with no resolvable page is reported as `captions only`, the same honest state the
  JATS converter already reports for absent figure files.

### Testing

Network-free, using **synthetic PDFs built with `fitz`** — the real corpus lives outside the repo
(`PHI_LITERATURE_ROOT`) and cannot be committed, so no test may depend on it.

| Case | Asserts |
|---|---|
| `Table I` caption | Roman numerals detected (regression for the root cause) |
| `Table 1` caption | Arabic numbering still detected |
| `Table S1` caption | supplementary labels detected |
| one table, one page | PNG on disk; markdown references it; `region: "full-page"` |
| two tables, one page | one render, both tables reference it, markdown says so |
| paper with no tables | count `0`, **no** warning emitted |
| flattened body text | marker present and names the image |
| unrenderable page | warning recorded, no exception |

The end-to-end check against the real PMID:9927411 PDF is run by hand, since the file cannot live
in the repo. Expected: 2 table captions, 2 page renders, and a report that no longer says `0`.

## Out of scope

- **The JATS / Europe PMC path.** JATS tags tables explicitly and `jats_convert.py` already handles
  them; this is a PDF-only defect. It matters mainly for **old and paywalled papers**, which is
  exactly where `find_tables()` fails and Roman numerals appear.
- **Structured row/column parsing.** Rejected above.
- **`find_tables()`.** Measured at zero on the trigger paper; not worth a fast path until a
  measurement says otherwise.

## Known cost

Full-page renders at 170 dpi run roughly 200–400 KB each and land in `media/`.
`docs/STORAGE-CONFIGURATION.md` already flags a `media/` quota caveat for Google Drive storage on
big batches; this adds to it. The dpi is configurable, so the cost is tunable if it bites.

## Follow-on, not included

The draft's provenance should state that a table-carrying paper's tables were read from page
renders rather than from text. That is a drafting-workflow change (`paper-triage` /
`curation-qc`), and is left out so this stays one reviewable change.
