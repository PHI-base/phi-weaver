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

> **Still open (not closed by these files):** the `PHIPO_EXT:` / `FYPO_EXT:` **gate roots** are
> already in `phipo_extensions.tsv` (`gene_for_gene_interaction → PHIPO_EXT:0000001`,
> `has_severity → FYPO_EXT:1000001`, etc.) — those aren't missing. What we lack is the list of
> *child value terms* under those roots: unlike PHIPO (on OLS), `PHIPO_EXT` / `FYPO_EXT` don't
> resolve on OLS4 and aren't in any bundled `.obo` (this `.obo` defines *relations*), so a
> specific value can only be format-checked, not existence-checked. See BACKLOG.md.
