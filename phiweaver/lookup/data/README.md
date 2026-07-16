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

## `phipo_ext.obo` — PHIPO_EXT (PHIPO extension ontology, prefix `PHIPO_EXT:`)

PHIPO_EXT is a **separate** PHI-base ontology of extension-only terms — the gene-for-gene /
inverse gene-for-gene interaction values used by the `gene_for_gene_interaction` /
`inverse_gene_for_gene` annotation extensions. It is **not part of PHIPO** (PHIPO obsoleted its
old gene-for-gene term in 2020 and moved these terms into PHIPO_EXT) and is **not on OLS4**, so
`validate_ontology_ids` resolves `PHIPO_EXT:` IDs **offline** against this bundled copy. Same
`_load_phido` parser. Note the shared `PHIPO` prefix: the ID splitter and the `--file` extractor
match `PHIPO_EXT` before `PHIPO` so the longer prefix wins.

- **Source**: <https://github.com/PHI-base/phipo_ext> (`master`), file `phipo_ext.obo` (**public**,
  CC-BY 4.0 — unlike the private `*_extensions.tsv` configs below).
- **Downloaded**: 2026-07-16 (47 terms, 15 obsolete; header `creation_date 2018-07-09`).

### Refreshing

```bash
curl -sL https://raw.githubusercontent.com/PHI-base/phipo_ext/master/phipo_ext.obo \
  -o phiweaver/lookup/data/phipo_ext.obo
python3 -m unittest tests.test_validate_ontology_ids   # confirm still green
```

## `fypo_extension.obo` — FYPO_EXT (penetrance/severity values, prefix `FYPO_EXT:`)

FYPO_EXT is a small **PomBase** extension ontology holding the values for the
`has_penetrance` / `has_severity` annotation extensions: `high` / `medium` / `low` /
`complete` (+ the root `FYPO_EXT:1000000`). Not in FYPO, not on OLS, so `validate_ontology_ids`
resolves `FYPO_EXT:` IDs **offline** against this bundled copy.

- **Source**: <https://github.com/PHI-base/canto> (`master`), file `t/data/fypo_extension.obo`
  (identical to the PomBase original; only 5 terms, so this "test-data" copy is the whole
  ontology). **Downloaded**: 2026-07-16.
- **Caveat:** `phipo_extensions.tsv` points `has_severity`/`has_penetrance` at `FYPO_EXT:1000001`
  / `FYPO_EXT:1000002` — those are **grouping/gate-root** ids and are **not** defined as terms in
  this file, so a literal `FYPO_EXT:1000001` value reads as `not_found` (correct: curators annotate
  `high`/`medium`/`low`/`complete`, not the root). PHI-base/canto's *other* `t/data/*_small.obo`
  files are truncated test fixtures — do NOT source PHIPO/GO/etc. from there.

> **⚠ Hand-vendored from a private repo — rewire when public.** The four extension-config files
> below (`phipo_extensions.tsv`, `phibase_go_extensions.tsv`, `phido_extensions.tsv`,
> `phipo_extension_relations.obo`) were **copied in by hand** from the **private** PHI-base/config
> repo (2026-07-15) — there is no `curl`-able source yet, unlike `phido.obo` / `phi-eco.obo`.
> When `config/annotation_extension/` becomes available on a **public** GitHub repo, replace this
> manual copy with a pinned public source: add real refresh URLs to the "Refreshing" notes and
> record the source commit. Tracked in `docs/BACKLOG.md`.

## `phipo_extensions.tsv` — attested PHI-Canto annotation-extension relations

A PHI-Canto phenotype annotation can carry **extensions** (`relation → value`, e.g.
`infects_tissue → BTO:…`, `infective_ability → PHIPO:…`). The set of legal relations and
the value type each accepts is **PHI-Canto configuration, not an OLS ontology**, so
`extension_config.py` validates relations **offline** against this bundled copy (relation
must be attested; value must match the range's value-type). Before this, weaver only
*inferred* relation names from gold-standard examples.

- **Source**: PHI-base/config (**private**), `master`, file
  `config/annotation_extension/phipo_extensions.tsv`.
- **Provided**: 2026-07-15 by the curator (copied in by hand — weaver is **not** pointed
  at the private repo, which also holds `canto_deploy.yaml` with a Google Tag Manager ID;
  only this single config file is vendored, and it carries no credentials).

### Refreshing

Re-copy when the extension config changes (new relations, ranges, or domain terms). Keep
weaver pointed only at this vendored file, never the live private repo:

```bash
# from a checkout of PHI-base/config:
cp config/annotation_extension/phipo_extensions.tsv \
   <phi-weaver>/phiweaver/lookup/data/phipo_extensions.tsv
python3 -m unittest tests.test_extension_config   # confirm still green
```

`extension_config._parse` reads the TSV columns `domain ID | subset relation |
extension relation | range ID | Canto display text | Help text | cardinality | role |
annotation_type_name`. It strips a known trailing space on `with_host_peptide `.

## `phibase_go_extensions.tsv` / `phido_extensions.tsv` — extensions for GO / disease annotations

Companions to `phipo_extensions.tsv`, one per PHI-Canto annotation family. Same TSV shape,
loaded by `extension_config` via `config="go"` / `config="phido"` (default is `"phipo"`).

- **Source**: PHI-base/config (**private**), `master`, `config/annotation_extension/`.
- **Provided**: 2026-07-15 by the curator (copied in by hand; weaver is not pointed at the repo).
- **`phibase_go_extensions.tsv`** — extensions on **GO** annotations: `has_input` (a `ProteinID`
  or free text), `with_host_species` / `with_symbiont_species` (an NCBI `TaxonID`). Note these
  values are **IDs/text, not ontology subtrees** — only the *domain* column is GO-based, so
  unlike PHIPO these are not "gate" ranges.
- **`phido_extensions.tsv`** — extensions on **disease-name (PHIDO)** annotations: one relation,
  `infects_tissue → BTO` (a real BTO tissue gate).

Neither is used by any current draft/example — vendored for completeness so weaver never
guesses a GO/disease extension once those annotations start carrying extensions.

## `phipo_extension_relations.obo` — relation *definitions* (reference, not a validator source)

An OBO of `[Typedef]` stanzas that **define the extension relations** (human-readable
definitions, plus synonym history such as `has_expressivity → has_severity`). It is
**deliberately not** wired into validation: it is **incomplete** relative to
`phipo_extensions.tsv` (6 relations vs 12, and it lists `causes_disease`, which the .tsv
does not), so using it to decide "is this relation attested?" would wrongly reject real
relations like `interaction_outcome`. `phipo_extensions.tsv` remains the authority for what
is attested; this file is kept only as the canonical **definitions reference**.

- **Source**: PHI-base/config (private), `master`, `config/annotation_extension/`. Provided 2026-07-15.

> **Extension value terms: now existence-checked** (2026-07-16). Both `PHIPO_EXT:` (gene-for-gene,
> `phipo_ext.obo`) and `FYPO_EXT:` (penetrance/severity, `fypo_extension.obo`) value terms are
> vendored and validated offline by `validate_ontology_ids`, so extension values are no longer
> format-check-only. (Only the two `FYPO_EXT:100000x` grouping-root ids are unresolved — see the
> caveat above; they are gate roots, not annotation values.)
