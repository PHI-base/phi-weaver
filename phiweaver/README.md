# phiweaver/ — the PHI-Weaver engine package

Importable package holding the deterministic, testable tooling that backs the agent
**skills** (`../skills/`). Where a skill says "look it up", a module here makes that lookup
reproducible and verifiable.

## Running (no install required)
Run from the **repo root**; the package is importable because the repo root is on the path:

```bash
python3 -m phiweaver.lookup.query_uniprot --gene FgTPP1 --organism 5518
python3 -m phiweaver.lookup.validate_ontology_ids PHIPO:0000001 GO:0009405
python3 -m phiweaver.pipeline.curation_pipeline help
python3 -m phiweaver.smoke              # fresh-checkout sanity check
python3 -m unittest discover -s tests   # the test suite
```

`pip install -e .` is **optional** (handy in CI / Codespaces / a venv); it also exposes
console entry points (`phiweaver-uniprot`, `phiweaver-validate`, `phiweaver-pipeline`,
`phiweaver-smoke`). The old `python3 scripts/…` and `python3 11-CLAUDE-AI/…` commands still
work via thin compatibility shims.

## Layout
- **`lookup/`**
  - `query_uniprot.py` — resolve a gene/locus tag/accession to a UniProtKB accession +
    evidence-backed function (UniProt REST). Never guesses: multiple hits → `ambiguous`
    with all candidates; reviewed (Swiss-Prot) sorted first; provenance recorded.
  - `validate_ontology_ids.py` — PHIPO/GO/PHIDO/UniProtKB ID validation: offline format
    check + online existence/obsolescence via the EBI Ontology Lookup Service. Obsolete = fail.
- **`tracking/`** — the SQLite curation-tracking DB and its tools: `phi_canto_sqlite.py`
  (schema + queries + `record_completion`/`get_completion_metrics`), `session_logger.py`,
  `daily_curation.py`, `workflow_helper.py`, `generate_article_registry.py`, and the
  `show_*` / `check_timestamps` reporters.
- **`pipeline/`** — `curation_pipeline.py`, the PDF→curation orchestration (convert, place,
  track, record real completion metrics).
- **`smoke.py`** — the fresh-checkout sanity check.

## Design contract (shared by every tool)
- A structured result with a `status`, the payload, and **provenance** (source, cache
  hit/miss, UTC timestamp); `--json` for machine output; exit `0`/`1`.
- **Injectable I/O** (HTTP getter / DB handle) so tests are deterministic and offline.
- **Never guess** — ambiguity and "not found" are explicit statuses, never invented data.

## Tests
Network-free; injected I/O. Run from the repo root:
```bash
python3 -m unittest discover -s tests
```
