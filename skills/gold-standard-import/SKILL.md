---
name: gold-standard-import
description: Turn a completed PHI-Canto curation export (PDF or HTML) into a validated gold-standard example in the curation-example library. Use when a curator provides a finished PHI-Canto session to add to 07-Standards/curation-examples/.
backing_script:
  - phiweaver/lookup/validate_ontology_ids.py
  - phiweaver/curation_examples.py
tests:
  - tests/test_validate_ontology_ids.py
  - tests/test_curation_examples.py
inputs:
  - a completed PHI-Canto curation export (the read-only session saved as PDF or HTML) + its PMID
outputs:
  - a frontmatter-wrapped curation-example .md in 07-Standards/curation-examples/
  - every ontology ID validated (with any unverifiable ones flagged, e.g. PHIDO)
  - a regenerated curation-examples INDEX.md
---

# Gold-standard Import

## Purpose
Turn a **finished, human-curated PHI-Canto session** into a **validated gold-standard example**
that phiweaver can retrieve as a reference when drafting similar papers. Keep the PHI-Canto
content in its own structure — only add the curation-example frontmatter wrapper.

## When to use
- When a curator hands over a completed PHI-Canto curation (its read-only page saved as PDF or
  HTML, or the file placed in external storage) to seed or extend
  `07-Standards/curation-examples/`.

## Workflow
1. **Get the content.** The Canto read-only page loads its annotations via JavaScript, so a live
   URL fetch (WebFetch) sees only the shell — ask the curator to **save the rendered page as PDF
   or HTML** into `PHI-Canto-Literature/active/` and give the filename. Confirm the PMID from the
   content itself (a filename's PMID may not match the session).
   - **PDF**: extract text with PyMuPDF —
     `python3 -c "import fitz; print(chr(10).join(p.get_text() for p in fitz.open('FILE')))"`.
   - **HTML**: read the file directly.
2. **Extract the curation verbatim**: publication (PMID / title / authors), pathogen + host,
   genes (+ accessions), genotypes and metagenotypes, and every annotation — annotation type,
   ontology term ID + name, evidence code, conditions / extensions, figure, and the curator.
3. **Validate every ontology ID** and never alter the curator's IDs:
   `python3 -m phiweaver.lookup.validate_ontology_ids GO:XXXXXXX PHIPO:XXXXXXX PHIDO:XXXXXXX`.
   Record the result; **flag any that cannot be verified** (PHIDO is not hosted in EBI OLS4, so it
   returns `not_found` — treat it as format-checked-only, not wrong).
4. **Write the example** `07-Standards/curation-examples/<PMID>-<short-slug>.md`:
   - the curation-example **frontmatter** — `type: curation-example`, `status: validated`,
     `topics` (from `TAGS.md`), `annotation_types`, `evidence`, `pathogen`, `host`,
     `source: PMID:...`, `reviewed_by` (the PHI-Canto curator), `reviewed_date`;
   - then the curation content **kept in PHI-Canto's structure** (do NOT retype it into the draft
     template body). Omit the `auto_check` / `flags` block — that is for drafts, not validated
     gold standards.
   - Note the source PHI-Canto session link; the source PDF/HTML stays in external storage.
5. **Register**: `python3 -m phiweaver.curation_examples`, then
   `python3 -m phiweaver.curation_examples --check`.

## Expected outputs
- One `status: validated` curation-example `.md` in `07-Standards/curation-examples/`, tagged.
- A short validation note (IDs confirmed current; any that couldn't be verified).
- Updated `INDEX.md`.

## Quality-control checks
- Every ontology ID validated, or explicitly flagged as unverifiable (e.g. PHIDO).
- The import is **faithful** to the PHI-Canto session — no invented or altered IDs/terms.
- Tags come from `TAGS.md`; `status: validated` only for a genuinely curator-reviewed curation.
- `python3 -m phiweaver.curation_examples --check` passes.

## Human review
- The content is a curator's own validated curation, so the bar is fidelity: the curator confirms
  the tags and that nothing was dropped or altered. If the source is not yet fully reviewed,
  import it with `status: draft` and flip to `validated` only after review.
