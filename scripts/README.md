# scripts/

Deterministic, testable helper tools that back the agent **skills** (`../skills/`).
Where a skill says "look it up", a script makes that lookup reproducible and verifiable.

## `query_uniprot.py` — UniProtKB lookup

Resolves a gene / locus tag / accession (optionally scoped to an organism) to a
UniProtKB accession and an evidence-backed function, via the UniProt **REST API**
(`https://rest.uniprot.org`). Backs the [`uniprot-lookup`](../skills/uniprot-lookup/SKILL.md)
skill.

### Why REST (not SPARQL)
The job is a narrow identity/function lookup, not a graph query. REST gives JSON, field
selection, organism filtering and a reviewed flag with far less complexity. (SPARQL would
only earn its keep for relational/cross-dataset queries — not needed here.)

### Install
```bash
pip install -r ../requirements.txt   # adds `requests`
```
The module itself imports `requests` lazily, so it loads and **tests** without it.

### CLI
```bash
# by gene + organism (NCBI taxonomy id)
python3 scripts/query_uniprot.py --gene FgTPP1 --organism 5518

# by locus tag
python3 scripts/query_uniprot.py --locus-tag FGSG_11164 --organism 5518

# by accession (direct fetch), machine-readable
python3 scripts/query_uniprot.py --accession P12345 --json

# options
--json        emit JSON instead of the human summary
--no-cache    bypass the local cache
--cache PATH  cache file (or set UNIPROT_CACHE)
```

### Behaviour (aligned with `AGENTS.md`)
- **Never guesses.** Multiple hits → status `ambiguous` with *all* candidates returned;
  zero hits → `not_found`. It never fabricates an accession.
- **Reviewed first.** Swiss-Prot entries are sorted ahead of TrEMBL, and TrEMBL is flagged
  as lower confidence.
- **Evidence-aware.** The function string is labelled experimental vs inferred from its
  ECO evidence codes.
- **Provenance.** Each result records the query, the **UniProt release** (from response
  headers), whether it came from cache, and a UTC timestamp.

### Output shape (`--json`)
```json
{
  "query": {"gene": "FgTPP1", "organism_id": 5518, ...},
  "status": "found",
  "candidates": [
    {"accession": "...", "protein_name": "...", "gene_names": ["..."],
     "organism": "...", "organism_id": 5518, "reviewed": true,
     "function": "...", "function_has_experimental_evidence": true}
  ],
  "uniprot_release": "2026_02",
  "retrieved_at": "2026-06-10T...Z",
  "from_cache": false
}
```
Exit code: `0` for `found`/`ambiguous`, `1` for `not_found`/`error`.

### Cache
Raw responses are cached in a small SQLite file (default `scripts/.cache/uniprot_cache.sqlite`,
gitignored). This speeds reruns and freezes results within a run; override with
`--cache` / `UNIPROT_CACHE`, or skip with `--no-cache`.

### Tests
Network-free — the HTTP getter is injected, so tests never hit UniProt:
```bash
python3 -m unittest discover -s scripts/tests        # or: pytest scripts/tests
```
Covers found / ambiguous / not-found, reviewed-before-TrEMBL ordering, function-evidence
labelling, HTTP errors, direct accession fetch, and cache hits.

## `validate_ontology_ids.py` — PHIPO / GO / PHIDO / UniProtKB ID validation

Checks the identifiers a curation depends on, so an invented, mistyped, or **obsolete**
term never reaches a curator. Backs the term-verification steps in the
[`curation-qc`](../skills/curation-qc/SKILL.md) and
[`phipo-mapping`](../skills/phipo-mapping/SKILL.md) skills.

Two stages:
1. **Format** (offline, always): the ID matches the official syntax for its prefix
   (`GO`/`PHIPO`/`PHIDO` = 7-digit; UniProtKB = the canonical accession regex).
2. **Existence / obsolescence** (online, OBO ontologies): the term exists and is current,
   via the EBI **Ontology Lookup Service** (`https://www.ebi.ac.uk/ols4/api`).

UniProtKB accessions are format-checked only here — their existence (and function) is the
job of `query_uniprot.py`, so they are marked `format_checked_only` rather than re-looked-up.

### CLI
```bash
# validate specific IDs (format + live OLS existence/obsolete check)
python3 scripts/validate_ontology_ids.py PHIPO:0000001 GO:0009405

# extract and validate every ontology ID found in a draft curation
python3 scripts/validate_ontology_ids.py --file draft-curation.md

# offline syntax check only (no network), machine-readable
python3 scripts/validate_ontology_ids.py --format-only PHIPO:0000001 --json

# options: --format-only  --json  --no-cache  --cache PATH (or ONTOLOGY_CACHE)
```
Exit code `0` only if every ID passes (valid format and not missing/obsolete); else `1`.

### Behaviour (aligned with `AGENTS.md`)
- **Never guesses / never corrects.** A bad-format ID is reported, not "fixed"; a term OLS
  does not return is `not_found`, never assumed valid.
- **Obsolete = fail.** The skills require non-obsolete terms; an obsolete term reports
  `obsolete` and fails the run, carrying its label so the curator can find a replacement.
- **Provenance.** Each online result records the source (OLS), cache hit/miss, and a UTC
  timestamp.

### Tests
Network-free — the HTTP getter is injected:
```bash
python3 -m unittest discover -s scripts/tests        # or: pytest scripts/tests
```
Covers each ID format, exists / obsolete / not-found, format-invalid and unknown-prefix
short-circuits (no network), UniProt format-checked-only, offline mode, HTTP errors,
wrong-term-returned, cache hits, and free-text ID extraction.

## `smoke_test.py` — fresh-checkout sanity check

Answers "I just cloned this repo — does the core tooling work here?" in one command.
**Network-free and needs zero pip installs** (the optional deps are only for live lookups
/ PDF conversion), so it's the first thing to run on a fresh clone or in a new Codespace.

```bash
python3 scripts/smoke_test.py          # human checklist, exit 0/1
python3 scripts/smoke_test.py --quiet  # summary + failures only
```

Checks: repo layout · all core modules import with stdlib only · the pipeline
auto-detects the repo root and bootstraps the `active/completed/media` storage folders ·
a fresh SQLite tracking DB creates its schema and accepts a row · the offline scripts
behave · the unit-test suite passes. Exit `0` only if every check is green.
