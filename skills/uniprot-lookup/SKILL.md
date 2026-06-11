---
name: uniprot-lookup
description: Resolve a gene or protein to a UniProtKB accession and evidence-backed function. Use before asserting any gene/protein identity or function in a curation.
backing_script: phiweaver/lookup/query_uniprot.py
tests: tests/test_query_uniprot.py
inputs:
  - gene name / locus tag / accession
  - organism (NCBI taxon id)
outputs:
  - UniProtKB accession (or not_found / ambiguous)
  - protein and gene names, organism
  - function summary + evidence type (experimental vs inferred)
---

# UniProt Lookup

## Purpose
Resolve a gene/protein mentioned in a paper to its canonical UniProtKB accession and
summarise its function from authoritative records — so curation never relies on invented
identity or function.

## When to use
- Whenever a curation step needs a gene/protein's accession, name, or function.
- Before writing any functional claim about a gene/protein.
- When disambiguating gene names, synonyms, or species-specific orthologs.

## Workflow
1. Collect identifiers from the source: gene name/symbol, locus tag, organism, and
   sequence if given.
2. Query UniProtKB for the organism + identifier with the backing script
   `python3 scripts/query_uniprot.py --gene <NAME> --organism <TAXID>` (or
   `--locus-tag` / `--accession`; add `--json` for machine output). It prefers reviewed
   (Swiss-Prot) entries, flags TrEMBL as lower confidence, returns `ambiguous` with all
   candidates rather than guessing, and records provenance (UniProt release + timestamp).
3. Confirm the match by organism and gene/locus. If ambiguous, list candidates rather
   than guessing.
4. Extract: primary accession, protein name, gene name(s), organism, and function with
   its evidence (experimental vs. inferred).
5. Record the source accession/URL and the exact query used (provenance).

## Expected outputs
- UniProtKB accession, or an explicit "not found / ambiguous".
- Protein and gene name(s), organism.
- Function summary with evidence type, with evidence separated from inference.
- The exact identifier/query used.

## Quality-control checks
- Accession exists and resolves; organism matches the paper.
- Reviewed status noted; TrEMBL flagged as lower confidence.
- No function stated without a UniProtKB/GO source; unknowns marked "unknown".

## Human review
- A curator must confirm the accession when multiple candidates exist or only TrEMBL
  entries are available. Flag all ambiguous matches for review.
