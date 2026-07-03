# Curation benchmarking

`PHI-Weaver-Curation-Scorecard.xlsx` — a per-paper scoring matrix for benchmarking curation
quality, designed so **phiweaver pre-fills the machine-checkable parts and a human reviews the
judgement calls**.

## Sheets
- **Guide** — purpose, the rating rubric, the scoring rule, and how to use it.
- **Scorecard** — the per-paper template (copy the tab for each paper). Items are grouped by
  annotation level (entity → gene → genotype → metagenotype → phenotype → detail). Two scoring
  inputs per item:
  - *phiweaver auto-check* — filled automatically: does the identifier/term exist and is it
    current (UniProtKB via `query_uniprot`; GO/PHIPO via `validate_ontology_ids`).
  - *Reviewer rating* — the human decides Correct / Needs improvement / Incorrect / Not
    applicable (dropdown). Points and the overall accuracy % compute automatically.
  - A **Completeness** block records curatable items in the paper vs captured, because
    correctness alone doesn't reveal what was missed.
- **Summary** — one row per scored paper, to track accuracy + completeness over time.

## Scoring
Correct = 1, Needs improvement = 0.5, Incorrect = 0; Not applicable is excluded.
Overall accuracy = points ÷ applicable items. Completeness = captured ÷ curatable.

## Notes
- Confirm whether *physical / molecular interaction* is in PHI-Canto's phenotype scope before
  treating it as a scored row.
- A curation scored all-Correct with full completeness is, by definition, a validated
  gold-standard — add it to `../curation-examples/`.
- The `.xlsx` is generated; to change the item list or layout, edit the generator (kept with the
  session's working files) and regenerate, or just edit the spreadsheet directly.
