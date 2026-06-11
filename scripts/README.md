# scripts/

Thin **compatibility shims** only. The real tooling moved into the importable
[`phiweaver/`](../phiweaver/README.md) package in P1 (see `docs/MODULARITY-PLAN.md`).

- `query_uniprot.py` → `python3 -m phiweaver.lookup.query_uniprot`
- `validate_ontology_ids.py` → `python3 -m phiweaver.lookup.validate_ontology_ids`
- `smoke_test.py` → `python3 -m phiweaver.smoke`

Each shim just runs its package module, so existing documented commands keep working.
Prefer the `python3 -m phiweaver.…` form (run from the repo root). New tools go in the
package with tests under `../tests/`, not here.
