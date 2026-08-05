# Bundled ontology data

## Refreshing all of them: one command

Nothing here self-updates — that is the price of resolving offline. Instead of the per-file
`curl` recipes below (still accurate, and the fallback if the tool is unavailable):

```bash
python3 -m phiweaver.lookup.refresh_ontologies            # fetch all 5, then run the tests
python3 -m phiweaver.lookup.refresh_ontologies --dry-run  # report what would change only
python3 -m phiweaver.lookup.refresh_ontologies --list     # sources, incl. what it can't fetch
```

It prints each file's `data-version` / term count / digest before → after, refuses content
that is not OBO or has lost >50% of its terms (a 404 page or a truncated download must never
overwrite a good bundle), and says **"nothing moved"** when upstream has not released — which
is the normal outcome and means there is no new term a curator could annotate to yet. It runs
`tests.test_map_phenotype tests.test_validate_ontology_ids` only when a file actually changed.

Run it **when you think it is needed** (before a curation batch, after a PHIPO release
notice): a no-op costs nothing, so there is no schedule to keep and nothing polls upstream.
Two things it deliberately does not do — fetch anything automatically, and touch the five
files it cannot source (`pomgeneex.obo`, hand-written; the four `PHI-base/canto-config`
copies, TSV/Typedef-shaped rather than the `[Term]`-block OBO this tool understands). Those
are named in its output rather than silently absent — refresh them with the `curl` recipes
in their own sections below instead.

**Never inside a scored benchmark run.** Under the sandbox's default-deny allowlist the fetch
fails, which is correct. After a refresh, update the "Downloaded" line in the relevant section
below and commit — the tool changes files, not this provenance record.

## `phipo-base.obo` — PHIPO (the main phenotype ontology)

Both `map_phenotype` (phrase → candidate terms) and `validate_ontology_ids` (`PHIPO:` IDs)
resolve **offline** against this file. **PHIPO moved off OLS on 2026-07-17** — unlike the
other bundled ontologies below, it *is* on OLS4, so this was a deliberate switch, for three
reasons in order of weight:

1. **OLS's search hides deprecated terms**, so a concept that once existed returns a clean
   `no_match` and looks like a virgin gap. That is exactly how PHI-base/phipo#452 was written
   unaware `PHIPO:0000503` already existed and had been obsoleted. Here obsolete terms are in
   the file: excluded from suggestions by default, surfaced by `map_phenotype
   --include-obsolete` for gap analysis (see the `ontology-term-request` skill, step 5).
2. **The benchmark sandbox.** No network during a scored run means the allowlist stays
   default-deny with no PHIPO exception — which matters because `github.com/PHI-base` hosts
   *both* the phipo ontology **and** the curated data repos (= the answer key), so "ontology
   yes, data no" cannot be expressed at the domain level. **PHIPO is a tool, not an answer.**
3. Deterministic and fast: no network flake, no cache staleness.

> **⚠ Which file — `phipo-base.obo`, never `phipo-edit.owl`.** This is the **release
> artifact**: the same content OLS serves, and approximately what PHI-Canto has loaded. It
> answers the question a curator actually has — *can I annotate this?* The **working file**
> `phipo-edit.owl` (in a clone of PHI-base/phipo) carries **unreleased** terms that PHI-Canto
> does **not** have, so suggesting or validating one is a bug that looks like a feature. Use
> the edit file for **gap analysis only**. Live example: at vendoring time the edit file held
> `PHIPO:0001456` (PR #454) and `PHIPO:0001455`, neither in this release nor on OLS.
> Also not `phipo.obo` (7.3M) — it inlines GO, CHEBI and other imports.

- **Source**: <https://github.com/PHI-base/phipo> (`master` branch), file `phipo-base.obo` at
  the repo root (a committed release artifact, not built locally).
- **Downloaded**: 2026-07-17 — release **2026-03-12** (`data-version:
  phipo/releases/2026-03-12/phipo-base.owl`), 1327 terms, 210 obsolete.
- **Verified at vendoring:** OLS served this same release — `PHIPO:0001455` (created
  2026-06-22) was absent from *both*, so going local lost nothing.

### Refreshing

The real cost of going local: OLS was self-updating, this is not. Re-download after a PHIPO
release (terms merged to `master` are **not** enough — they must be *released*, or a curator
cannot annotate to them):

```bash
curl -sL https://raw.githubusercontent.com/PHI-base/phipo/master/phipo-base.obo \
  -o phiweaver/lookup/data/phipo-base.obo
grep '^data-version' phiweaver/lookup/data/phipo-base.obo   # confirm it moved
python3 -m unittest tests.test_map_phenotype tests.test_validate_ontology_ids   # still green
```

**Do this outside a scored benchmark run** — it is the one moment PHIPO legitimately comes
from `github.com/PHI-base`, which a scored run must not reach. `map_phenotype` prints the
`data-version` on every search, so a stale bundle is visible rather than silent.

`map_phenotype` uses its own parser (it needs synonyms and the obsolete flag for scoring);
`validate_ontology_ids` reuses the `_load_phido` `[Term]`-block parser.

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

## `pomgeneex.obo` — PomGeneEx (RNA-level qualifiers, prefix `PomGeneEx:`)

The seven controlled qualifiers behind PHI-Canto's `wt_rna_expression` annotation type
(namespace `PomGeneExRNA` in `canto_base.yaml`): `RNA level increased` / `decreased` /
`unchanged` / `constant` / `fluctuates`, `RNA present`, `RNA absent`. Not on OLS4, so
`validate_ontology_ids` resolves `PomGeneEx:` IDs **offline** against this file — the same
pattern as `fypo_extension.obo`. The prefix is matched case-insensitively but reported in its
canonical mixed-case spelling.

- **Source**: **none — hand-written from IDs supplied by the curator on 2026-07-24.** No public
  PomGeneEx release artifact was located, so these IDs are **not verified against an upstream
  file**. The *phrases* have independent backing (PHI-Canto UI screenshot, 2026-07-11); the
  ID↔phrase *pairing* does not. This is the only bundled ontology here without an upstream.
- **History**: a 2026-07-16 curator ruling scoped this vocabulary to **terms-only** (no IDs, no
  bundled ontology). **Superseded 2026-07-24** when the IDs were supplied — see the closed item
  in `docs/BACKLOG.md`.
- **Caveat — RNA only.** The parallel protein-level vocabulary (`PomGeneExProt`, used by
  `wt_protein_expression`) has **no IDs recorded**, so those annotations still carry the phrase
  alone; `entry_queue` accordingly still accepts a blank `term_id` for both types.
- **Action**: re-confirm the pairing in Canto, then either replace this file with an upstream
  copy or record here that no upstream exists.

> **✅ Rewired to a public source (2026-08-05).** The four extension-config files below
> (`phipo_extensions.tsv`, `phibase_go_extensions.tsv`, `phido_extensions.tsv`,
> `phipo_extension_relations.obo`) were **hand-copied** from the **private** PHI-base/config repo
> on 2026-07-15. James Seager announced 2026-08-05 that `config/annotation_extension/` (and
> `canto_deploy.yaml`, see the section below) are now published in the new **public** repo
> **`PHI-base/canto-config`** — a filtered copy of `PHI-base/config` with sensitive-file history
> stripped. Each file section below now has a real `curl` recipe pinned to commit `3972a9b`
> (2026-08-05). **What's still private:** `PHI-base/config` itself still exists; James intends to
> rename it to `PHI-base/canto-config-private` once the PHI-Canto server switches to
> `canto-config`, then delete the migrated files from it to remove the duplication — so treat
> `PHI-base/config` paths in old provenance notes as historical, not durable. He may also transfer
> relevant issues across. `docs/BACKLOG.md` tracks the residual follow-ups.

## `phipo_extensions.tsv` — attested PHI-Canto annotation-extension relations

A PHI-Canto phenotype annotation can carry **extensions** (`relation → value`, e.g.
`infects_tissue → BTO:…`, `infective_ability → PHIPO:…`). The set of legal relations and
the value type each accepts is **PHI-Canto configuration, not an OLS ontology**, so
`extension_config.py` validates relations **offline** against this bundled copy (relation
must be attested; value must match the range's value-type). Before this, weaver only
*inferred* relation names from gold-standard examples.

- **Source**: <https://github.com/PHI-base/canto-config> (**public**, `main`), file
  `annotation_extension/phipo_extensions.tsv`.
- **Provided**: 2026-07-15 by the curator, hand-copied from the then-private PHI-base/config.
- **Rewired to the public repo**: 2026-08-05, commit `3972a9be2aacbd0c0a7064d237e7efbd1c39bd52`.
  This refresh also picked up a new relation added upstream since the 2026-07-15 copy —
  `host_susceptibility → PHIPO:0001456` ("host susceptibility to pathogen") — see the caveat
  below.

> **Caveat — `host_susceptibility`'s range term isn't in our vendored PHIPO release yet.**
> `PHIPO:0001456` is the same term already flagged in the `phipo-base.obo` section above as
> present in the *edit* file (PR #454) but absent from the 2026-03-12 release and from OLS.
> Until PHIPO releases it, `extension_config` will accept `host_susceptibility=PHIPO:0001456`
> as *attested* (relation name + value shape are both correct), but `validate_ontology_ids`
> will correctly report the term itself as `not_found` — that is the intended staged split,
> not a bug in either module.

### Refreshing

```bash
curl -sL https://raw.githubusercontent.com/PHI-base/canto-config/main/annotation_extension/phipo_extensions.tsv \
  -o phiweaver/lookup/data/phipo_extensions.tsv
python3 -m unittest tests.test_extension_config   # confirm still green
```

`extension_config._parse` reads the TSV columns `domain ID | subset relation |
extension relation | range ID | Canto display text | Help text | cardinality | role |
annotation_type_name`. It strips a known trailing space on `with_host_peptide `.

## `phibase_go_extensions.tsv` / `phido_extensions.tsv` — extensions for GO / disease annotations

Companions to `phipo_extensions.tsv`, one per PHI-Canto annotation family. Same TSV shape,
loaded by `extension_config` via `config="go"` / `config="phido"` (default is `"phipo"`).

- **Source**: <https://github.com/PHI-base/canto-config> (**public**, `main`),
  `annotation_extension/`.
- **Provided**: 2026-07-15 by the curator, hand-copied from the then-private PHI-base/config.
- **Rewired to the public repo**: 2026-08-05, commit `3972a9be2aacbd0c0a7064d237e7efbd1c39bd52`
  (content unchanged from the 2026-07-15 copy for both files).
- **`phibase_go_extensions.tsv`** — extensions on **GO** annotations: `has_input` (a `ProteinID`
  or free text), `with_host_species` / `with_symbiont_species` (an NCBI `TaxonID`). Note these
  values are **IDs/text, not ontology subtrees** — only the *domain* column is GO-based, so
  unlike PHIPO these are not "gate" ranges.
- **`phido_extensions.tsv`** — extensions on **disease-name (PHIDO)** annotations: one relation,
  `infects_tissue → BTO` (a real BTO tissue gate).

Neither is used by any current draft/example — vendored for completeness so weaver never
guesses a GO/disease extension once those annotations start carrying extensions.

### Refreshing

```bash
curl -sL https://raw.githubusercontent.com/PHI-base/canto-config/main/annotation_extension/phibase_go_extensions.tsv \
  -o phiweaver/lookup/data/phibase_go_extensions.tsv
curl -sL https://raw.githubusercontent.com/PHI-base/canto-config/main/annotation_extension/phido_extensions.tsv \
  -o phiweaver/lookup/data/phido_extensions.tsv
python3 -m unittest tests.test_extension_config   # confirm still green
```

## `phipo_extension_relations.obo` — relation *definitions* (reference, not a validator source)

An OBO of `[Typedef]` stanzas that **define the extension relations** (human-readable
definitions, plus synonym history such as `has_expressivity → has_severity`). It is
**deliberately not** wired into validation: it is **incomplete** relative to
`phipo_extensions.tsv` (7 relations vs 13, and it lists `causes_disease`, which the .tsv
does not), so using it to decide "is this relation attested?" would wrongly reject real
relations like `interaction_outcome`. `phipo_extensions.tsv` remains the authority for what
is attested; this file is kept only as the canonical **definitions reference**.

- **Source**: <https://github.com/PHI-base/canto-config> (**public**, `main`),
  `annotation_extension/phipo_extension_relations.obo`. Provided 2026-07-15 by the curator
  (hand-copied from the then-private PHI-base/config); rewired to the public repo 2026-08-05,
  commit `3972a9be2aacbd0c0a7064d237e7efbd1c39bd52` — which also added the `host_susceptibility`
  `[Typedef]` (see the `phipo_extensions.tsv` section above).

### Refreshing

```bash
curl -sL https://raw.githubusercontent.com/PHI-base/canto-config/main/annotation_extension/phipo_extension_relations.obo \
  -o phiweaver/lookup/data/phipo_extension_relations.obo
```

> **Extension value terms: now existence-checked** (2026-07-16). Both `PHIPO_EXT:` (gene-for-gene,
> `phipo_ext.obo`) and `FYPO_EXT:` (penetrance/severity, `fypo_extension.obo`) value terms are
> vendored and validated offline by `validate_ontology_ids`, so extension values are no longer
> format-check-only. (Only the two `FYPO_EXT:100000x` grouping-root ids are unresolved — see the
> caveat above; they are gate roots, not annotation values.)

---

## `canto_base.yaml` + `canto_deploy.yaml` — PHI-Canto's own configuration

What PHI-Canto *accepts*: the enabled annotation types, the legal allele types, the
evidence codes, and the ontology subsets it refuses to annotate against. Read by
`phiweaver/lookup/canto_config.py`. Before this, weaver inferred these from
gold-standard examples, so a draft could name an annotation type that does not exist.

PHI-Canto is a deployment of PomBase's Canto, so the configuration is **two files
merged** — effective config = base, with the deploy file's top-level keys replacing it:

| file | source | in git? |
|---|---|---|
| `canto_base.yaml` | **pombase/canto**, `master`, `canto.yaml` — **public** | ✅ committed |
| `canto_deploy.yaml` | **PHI-base/canto-config**, `main`, `canto_deploy.yaml` — **public** | ✅ committed |

**Source commits** (record these when refreshing):
- `canto_base.yaml` — blob `20534e1938f9`, downloaded 2026-07-21.
- `canto_deploy.yaml` — content unchanged since commit `4319d2243090` ("Allow TAS evidence
  code for non-admin users", 2026-01-26), first vendored 2026-07-21 from the then-private
  PHI-base/config, **rewired to the public PHI-base/canto-config repo 2026-08-05** at commit
  `3972a9be2aacbd0c0a7064d237e7efbd1c39bd52` (byte-identical to the private copy — confirmed
  by diff before committing).

### History — the deploy file used to be gitignored

Until 2026-08-05 this file came from the **private** PHI-base/config repo. James Seager
cleared it for local use on 2026-07-21 — the ORCID OAuth secret lives outside the file (the
config holds only the env-var name `ORCID_CLIENT_SECRET`), the only database reference is a
local SQLite path, all four email addresses are role accounts, and the GA/GTM measurement id
is public by construction since it is served in the page source of the live site. **Clearing
a file for use is not clearing it for republication**, so weaver read it locally without
committing it. James subsequently published a filtered, sensitive-history-stripped copy of
PHI-base/config as the new public **PHI-base/canto-config** repo (announced 2026-08-05); once
confirmed byte-identical (see above), the file was committed here and the `.gitignore` entry
removed. He intends to rename the old private repo to `PHI-base/canto-config-private` once the
PHI-Canto server itself switches to `canto-config`, then delete the migrated files from it —
the private repo remains available for any future PHI-Canto file that genuinely needs to stay
private.

### ⚠ Why the base file alone would not be a usable fallback

Both files are now committed, so this no longer happens on a fresh clone — but it is why
the deploy file matters enough to have vendored in the first place, and it is still the
real behaviour if `canto_deploy.yaml` is ever absent (deleted locally, a shallow checkout
that missed it, etc.). Base-only answers are wrong in **both** directions (comparing
*enabled* lists — base marks 14 types available but enables 11):

- **PHI-Canto enables, base does not:** `pathogen_phenotype`, `host_phenotype`,
  `pathogen_host_interaction_phenotype`, `gene_for_gene_phenotype`, `disease_name` —
  5 of PHI-Canto's 12, including the two most basic ones weaver drafts.
- **base enables, PHI-Canto does not:** `phenotype`, `genotype_interaction`,
  `genetic_interaction`, `protein_sequence_feature_or_motif`.

So `canto_config` reports `deploy_loaded = False` and attaches a warning to **every**
check when the deploy file is missing. Treat that as *"cannot validate"*, never as a
pass. `tests/test_canto_config.py` skips (does not fail) the 10 tests that need it — those
skips should not fire in normal use any more, and a run where they do is worth investigating.

### Refreshing

```bash
# public base:
curl -sL https://raw.githubusercontent.com/pombase/canto/master/canto.yaml \
  -o phiweaver/lookup/data/canto_base.yaml

# public deploy:
curl -sL https://raw.githubusercontent.com/PHI-base/canto-config/main/canto_deploy.yaml \
  -o phiweaver/lookup/data/canto_deploy.yaml

python3 -m unittest tests.test_canto_config   # confirm still green
python3 -m phiweaver.lookup.canto_config      # should print "deploy config loaded: True"
```

Record the new source commits in this file when you refresh; drift is otherwise invisible.

> **Provenance bonus:** `canto_deploy.yaml`'s `extension_conf_files` lists the 8 extension
> TSVs PHI-Canto actually loads — including `phipo_extensions.tsv` and
> `phido_extensions.tsv`, both vendored above. That is the authoritative source list for
> those files, which previously had to be taken on trust.
