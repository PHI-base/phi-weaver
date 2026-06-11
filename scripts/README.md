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
