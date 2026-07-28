---
created: 2026-07-04
session_id: 2026-07-04-gold-standard-coverage
project: Gold-standard curation library — full annotation-type coverage
type: feature (curation + validator tooling)
tags: [curation, gold-standard, phido, psi-mod, ontology-validation, coverage, github-issue]
duration: ~1 session (continued from 2026-07-04-benchmarking-stack)
participants: [Claude Fable 5, martin2urban]
---

# Session Log: gold-standard library → 12/12 annotation-type coverage

## Recap

6 commits + GitHub issue #1. Grew the validated gold-standard example library from 1→**5 examples covering all 12 PHI-Canto annotation types (12/12)**: PMID:35468894 (physical_interaction/wt_rna/host_phenotype), 23498959 (PTM), 37177781 (wt_protein_expression), plus re-tagged 26177154 & 39787257. Made `annotation_types` = PHI-Canto's own 12 types + an auto-generated **coverage tracker** in `INDEX.md` (+ typo-guard in `--check`). Extended `validate_ontology_ids`: **PHIDO offline** (bundled `phido.obo`, OLS4 doesn't host it), **MOD/PSI-MOD** via OLS, defining-ontology term selection. Offline PHIDO caught 2 obsolete disease terms in PMID:39787257 (updated to replacements; **issue #1** tracks fixing the source Canto session). Installed+authed `gh`. Resolved physical-interaction scope (in scope). Smoke 7/7, 94 tests. **NEXT: depth not breadth; format convergence; action issue #1.**


**Date**: 2026-07-04
**Project**: PHI-Weaver — grow the validated gold-standard curation-example library to cover every
PHI-Canto annotation type, extending the ontology validator as the real curations demanded.
**Session Type**: Feature. 6 commits on `main` (all pushed), 1 GitHub issue filed; green throughout.

## ✅ Shipped (6 commits on `main`)
- **`05ccfdd` PHIDO validates offline** — OLS4 doesn't host PHIDO, so every PHIDO ID used to
  return `not_found` (a false negative, surfaced 2026-07-03). Fixed by vendoring `phido.obo`
  (`phiweaver/lookup/data/`, from github.com/PHI-base/phido) and resolving PHIDO **offline**
  against it (existence + obsolescence, no network); GO/PHIPO still use OLS. +8 tests. Refresh
  instructions in `data/README.md`.
- **`5bee87a` coverage tracking** — the example `annotation_types` vocabulary is now **PHI-Canto's
  own 12 annotation types** (`TAGS.md`, with session-prevalence counts); `curation_examples.py`
  auto-generates a "Coverage" table in `INDEX.md` (covered vs gap, ranked by prevalence) and its
  `--check` flags any annotation_type outside the canonical set. Re-tagged PMID:26177154 (GO
  aspects verified via OLS).
- **`c6a2991` example PMID:35468894** (PINE1 effector × host PGIP; *S. sclerotiorum* / *B. cinerea*
  on Arabidopsis / pea) — broad session, 9 types; first **physical_interaction, wt_rna_expression,
  host_phenotype**. Resolved the physical-interaction scope question (in scope).
- **`79b7bc5` PSI-MOD support + example PMID:23498959** (creD effector × rice RLCK185) — validator
  extended for **MOD** (5-digit IDs via OLS `mod`) and to prefer the **defining ontology** when OLS
  echoes an id across ontologies; the example is the reference for **post_translational_modification**.
  +3 tests.
- **`f76b393` example PMID:37177781** (AvrPi9 effector × rice E3 ligase OsRGLG5) — reference for the
  last uncovered type, **wt_protein_expression** → **12/12 coverage**.
- **`62e9b26` + `9759aa7` backlog** — recorded progress and linked GitHub issue #1.

## 🧭 Result: full breadth (12/12)
Five validated gold-standard examples, one anchoring each previously-missing annotation type:
PMID:26177154 (gene-for-gene + GO MF/BP/CC + disease_name), 39787257 (pathogen_phenotype),
35468894 (physical_interaction / wt_rna_expression / host_phenotype), 23498959 (PTM), 37177781
(wt_protein_expression). All imported via the **gold-standard-import** workflow (extract → validate
every ID → wrap in frontmatter keeping PHI-Canto structure → regenerate INDEX). Live coverage
tracker: the auto-generated table in `curation-examples/INDEX.md`.

## 🔎 Validator now covers GO / PHIPO / MOD / PHIDO / UniProtKB
GO, PHIPO and MOD (PSI-MOD) resolve online via EBI OLS; PHIDO resolves offline against the bundled
ontology; UniProtKB is format-checked (existence via `query_uniprot.py`). Obsolete terms fail, and
term selection prefers the defining ontology. The offline PHIDO check immediately earned its keep:
PMID:39787257 was curated with two now-**obsolete** disease-name terms (PHIDO:0000163 → 0000162,
PHIDO:0000331 → 0000329) — the example was updated to the current IDs, and **GitHub issue
[#1](https://github.com/PHI-base/phi-weaver/issues/1)** tracks fixing them in the source PHI-Canto
session `02e545aba274d209`.

## 🛠️ Also
- Installed `gh` locally (`~/.local/bin/gh`, no root) and authenticated, to file issue #1.
- Refreshed `HANDOFF.md` (5 examples / 12/12) and `docs/OVERVIEW.md`; updated project memory.

## ✅ Verification
Smoke **7/7**, **94 tests**, **8 skills**, `curation-examples --check` passes, **5 validated
examples / 12/12 annotation types**. Tree clean apart from `.obsidian/` editor state; source PDFs
stay in external `active/` (not committed).

## ⏭️ NEXT
1. **Depth, not breadth** — breadth (all 12 types) is done; add more examples per type / more
   pathosystems as PHI-Canto exports arrive in `PHI-Canto-Literature/active/`.
2. **Backlog**: format convergence (align phiweaver draft body shape with PHI-Canto's — the
   annotation_types vocabulary already converged); activate the benchmark sandbox (bwrap installed);
   auto per-paper token logging. See `docs/BACKLOG.md`.
3. Curator to action **issue #1** (obsolete PHIDO IDs in session `02e545aba274d209`).

---

*Gold-standard library kept human-validated; content stays in PHI-Canto's structure with only a
frontmatter wrapper. See `07-Standards/curation-examples/` (`INDEX.md`, `TAGS.md`) and
`docs/BACKLOG.md`.*
