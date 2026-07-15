# Bundled ontology data

## `phido.obo` — PHIDO (PHI-base disease-name ontology)

PHIDO is **not hosted by EBI OLS4**, so `validate_ontology_ids` cannot verify PHIDO
IDs the way it verifies GO/PHIPO (which resolve online via OLS). To close that gap we
vendor the ontology file and validate PHIDO IDs **offline against this bundled copy**.

- **Source**: <https://github.com/PHI-base/phido> (`master` branch), file `phido.obo`.
- **Downloaded**: 2026-07-04.
- **Ontology `creation_date` in the file header**: 2018-07-09 (the ontology is small and
  changes rarely; there is no `data-version` line).

### Refreshing

Re-download when PHIDO gains new disease terms:

```bash
curl -sL https://raw.githubusercontent.com/PHI-base/phido/master/phido.obo \
  -o phiweaver/lookup/data/phido.obo
python3 -m unittest tests.test_validate_ontology_ids   # confirm still green
```

The parser (`validate_ontology_ids._load_phido`) reads only `[Term]` blocks and their
`id:`, `name:`, and `is_obsolete:` lines, so the `.obo` (not `.owl`/`.tsv`) is the file
to keep here.

## `phi-eco.obo` — PHI-ECO (PHI-base experimental-conditions ontology, prefix `PECO:`)

The **Condition** field of a PHI-Canto annotation uses PHI-ECO. Like PHIDO, it is
**PHI-base-local and not on OLS4**, so `validate_ontology_ids` resolves `PECO:` IDs
**offline** against this bundled copy. **Caution:** the OLS ontology named `peco` is the
*unrelated* Planteome **Plant Experimental Conditions Ontology** that merely shares the
prefix — PHI-base PECO terms are only in this file, never validate them against OLS.

- **Source**: <https://github.com/PHI-base/phi-eco> (`master` branch), file `phi-eco.obo`.
- **Downloaded**: 2026-07-15 (658 terms, 66 obsolete; header `date: 20:03:2018`; derived
  from an FYPO/PECO snapshot, since modified for PHI-eco).

### Refreshing

Re-download when PHI-ECO gains new condition terms (the curator adds them via the
"PHI-ECO term creator" spreadsheet, then the maintainer loads them — see
`07-Standards/Ontology-Terms-Reference.md`):

```bash
curl -sL https://raw.githubusercontent.com/PHI-base/phi-eco/master/phi-eco.obo \
  -o phiweaver/lookup/data/phi-eco.obo
python3 -m unittest tests.test_validate_ontology_ids   # confirm still green
```

Same parser as PHIDO (`_load_phido`, reused for the `[Term]` blocks).
