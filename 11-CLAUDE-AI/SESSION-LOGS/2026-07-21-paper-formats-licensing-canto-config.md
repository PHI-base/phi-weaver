---
created: 2026-07-21
type: session-log
tags: [status/complete]
project: Paper input formats, repo licensing/citation, PHI-Canto config wired into validation
summary: FAQ on PDF/EPUB/PMC input; found the public repo had no LICENSE and added MIT + CC BY 4.0 with CITATION.cff; wired PHI-Canto's own config (canto_deploy.yaml, from James) into new canto_config.py; made map_phenotype honour PHIPO's annotation-usage subsets, fixing "reduced virulence" being offered as a primary term.
---

# Session: input formats → licensing → PHI-Canto's real configuration

A question-driven session that started with "PDF or EPUB?" and ended three commits deep in
validation code, via a licensing gap nobody had noticed and an email from James.

## Objectives
- Decide which paper format to curate from, and record it.
- Sort out repository citation + licensing.
- React to James's email about the PHI-Canto configuration file, and use it if worth using.

## Work done

### 1. Paper input formats (FAQ + backlog)
- **Verdict: PDF is the default** — it's what publishers ship and what `pdf_convert.py` reads.
  EPUB is a book format journals rarely offer; its only edge is cleaner text (no two-column
  scrambling, real tables). **For open-access papers, prefer neither: take the PMC full text**
  (JATS XML / HTML), where sections and tables are already tagged. Order: **PMC → PDF → EPUB**.
- Corrected an over-general rule mid-thread: the PMID→PMC gap is set by the **journal's access
  model, not paper age**. Fully-OA journals deposit at publication (full text within ~2 weeks), so
  *last month's OA papers usually are in PMC*; paywalled ones are 6–12 months or never.
- **Token intuition inverts** (backlog): *raw* JATS is far more expensive than a PDF (~80–150k vs
  15–25k tokens — every citation an `<xref>`, the whole ref-list marked up), but *parsed* it is
  cheaper (~10–15k) because PDF text drags per-page furniture through the document and can't
  cleanly cut the reference list. **So the cost of a PMC path is the parser, not context size.**
  Numbers are ballpark, not measured on our corpus — flagged as such.

### 2. Licensing + citation (commits 6525ce8, 91be1d5, bece3dd)
- Martin believed the repo was MIT-licensed. **It wasn't** — `gh api` returned `license: null`,
  `visibility: public`, and nothing in git history. `README.md` claimed MIT and linked to a
  `LICENSE` file that had never been created. **Public + unlicensed = all rights reserved**, so
  collaborators at other institutions would have been blocked by their own legal review.
- **Dual-licensed**, since the repo is a hybrid: **`LICENSE` = MIT** (the `phiweaver/` package),
  **`LICENSE-CONTENT` = CC BY 4.0** (standards, docs, skills, curated examples — matching PHI-base
  practice, PHIPO ships CC BY). Vendored ontologies keep their upstream licenses, stated in both.
  GitHub now reports `license: MIT`. Copyright line reads **Rothamsted Research** (institutional,
  BBSRC-funded) — flagged for confirmation with James/Rothamsted.
- **`CITATION.cff`** added; Martin's ORCID `0000-0003-2440-4352` verified against ORCID's public
  API before writing it in. Co-author list deliberately left open.

### 3. Identity / persona discussion (no code)
- Asked whether weaver should get a persona, Gmail address and ORCID. **Verdict: named tool +
  version yes; service-account email yes if obviously non-human; ORCID no** — ORCID requires a
  natural person, and ICMJE/COPE hold that AI can't be an author because it can't be
  *accountable*. An ORCID on the tool would create database entries whose trail terminates at
  something that can't answer "why did you call that reduced virulence?".
- Correct instruments for the underlying need: Zenodo DOI, `CITATION.cff`, RRID. Provenance is
  already right — drafts carry `reviewed_by: <human>` beside the model record.
- **Authorship criteria** (recorded in `CITATION.cff` comments): needs *both* an intellectual
  contribution *and* consent. Reading the repo isn't the test — the standards encode Hsin-Yu's
  methodology whether or not she's read the code — but consent is not optional. Until each says
  yes, credit belongs in README Acknowledgments.
- Memory updated: `user-github-identity.md` now records that the interlocutor is always Martin,
  with GitHub handle, ORCID, affiliation and `created_by` value, so they need not be re-supplied.

### 4. PHI-Canto's own configuration (commit 48ccaa3) — from James's email
James pointed us at `canto_deploy.yaml` in the **private** PHI-base/config repo.

- **PHI-Canto = PomBase's Canto + a PHI-base override file.** Effective config is **two files
  merged**: public `canto_base.yaml` (pombase/canto, 2735 lines, committed) with the deploy file's
  top-level keys replacing it. For the annotation/allele lists it's a **full replacement**, not a
  patch; the 82 evidence codes are inherited from PomBase untouched.
- New **`phiweaver/lookup/canto_config.py`** + 16 tests: 12 enabled annotation types, 16 allele
  types, 82 evidence codes, do-not-annotate subsets, extension-config file list. **Weaver
  previously inferred all of this from gold-standard examples.**
- **The deploy file is gitignored.** James cleared it for *use*; that is not clearance for
  *republication*, and this repo is public. Independently verified his sensitivity assessment:
  OAuth entry holds only the env-var *name* (`ORCID_CLIENT_SECRET`), DB reference is a local SQLite
  path, all four emails are role accounts, and the GA/GTM id is public by construction (served in
  the live site's page source — a firmer argument than the Copilot one he was given).
- **Base-only is not a safe fallback**, so a missing deploy file degrades *loudly*
  (`deploy_loaded = False` + a warning on every check; the 10 tests needing it **skip**, not fail).
  Verified by temporarily removing the file. Comparing *enabled* lists:
  - PHI-Canto enables, base does not: `pathogen_phenotype`, `host_phenotype`,
    `pathogen_host_interaction_phenotype`, `gene_for_gene_phenotype`, `disease_name` — **5 of 12**.
  - base enables, PHI-Canto does not: `phenotype`, `genotype_interaction`, `genetic_interaction`,
    `protein_sequence_feature_or_motif`.
- **A test caught an error in my own constant**: I'd derived the divergence from
  `available_annotation_type_list`, but the governing list is `enabled_annotation_type_list` (base
  marks 14 available, enables 11). The corrected picture was worse than first described.

### 5. `map_phenotype` honours annotation-usage subsets (commit 6d087cc)
- **The find:** a PHIPO term can exist, be non-obsolete, **and still be unusable**. PHIPO tags this
  in the ontology file itself — 174 tagged terms: `qc_do_not_annotate` (67),
  `qc_do_not_manually_annotate` (56), `qc_extension_only` (13). *Mechanism* is PomBase/GO's
  convention; the *tags on PHIPO terms* are PHI-base's.
- **Worst case was the commonest phrase in PHI-base papers**: `"reduced virulence"` returned
  `PHIPO:0000015` as a **primary phenotype term**, when it is `qc_extension_only` and belongs in
  `infective_ability → PHIPO:0000015`.
- Three exclusions, each handled differently **on purpose**:
  - **extension-only → kept and labelled.** Hiding them would turn the most common phrases into
    false gaps.
  - **grouping → withheld but still reported** under *"NOT a gap"*. Silently dropping turns a
    parent-only match into a bare `no_match`, which reads as an ontology gap and invites a
    duplicate term request (lessons **L2/L8**, phipo#452). `--include-grouping` promotes them,
    mirroring `--include-obsolete`.
  - **obsolete → unchanged.**
- **Driven by PHIPO's own `subset:` tags, not by `canto_config`.** The PHI-Canto list lives in the
  gitignored deploy file; a filter depending on a file present on one machine and absent on another
  would hand two curators **different candidates for the same phrase**. The committed ontology is
  identical everywhere; `canto_config` stays the cross-check.
- Suite **303 → 309**, green.

## Decisions
1. Curate from **PMC full text → PDF → EPUB**, in that order.
2. Repo is **dual-licensed** (MIT code / CC BY 4.0 content); copyright to **Rothamsted Research**.
3. **No ORCID or human-passing persona for weaver**; credit via Zenodo DOI / `CITATION.cff` / RRID.
4. Config-derived validation must never depend on a file that may be absent — **reproducibility
   across curators outranks completeness on one machine**.
5. Non-annotatable matches are **labelled, never silently dropped** — a hidden match becomes a
   phantom gap.

## Open / next
- ⏰ **Chase James once the private repos go public** — while private, the checks only work on
  Martin's machine. Message drafted in `docs/BACKLOG.md`.
- ❓ **Question for James/Hsin-Yu:** PHI-Canto's `do_not_annotate_subsets` lists GO's `gocheck_*`
  spellings plus `qc_do_not_annotate`, but **not** PHIPO's `qc_do_not_manually_annotate`, which 56
  terms carry. Oversight, or does Canto normalise the prefixes? Raise as a discussion.
- `CITATION.cff` co-author list — needs Hsin-Yu / James / Alayne to consent.
- PMC/JATS input path (PMID→PMCID via NCBI ID Converter; JATS→markdown parser) — backlogged.
- Reply to James drafted and shortened; not yet sent.

## Files
- **New:** `LICENSE`, `LICENSE-CONTENT`, `CITATION.cff`, `phiweaver/lookup/canto_config.py`,
  `tests/test_canto_config.py`, `phiweaver/lookup/data/canto_base.yaml`
- **Modified:** `README.md`, `.gitignore`, `docs/FAQ.md`, `docs/BACKLOG.md`,
  `phiweaver/lookup/map_phenotype.py`, `tests/test_map_phenotype.py`,
  `phiweaver/lookup/data/README.md`
- **Local only (gitignored):** `phiweaver/lookup/data/canto_deploy.yaml` (commit `4319d224`)

## Commits
`6525ce8` FAQ/backlog: paper input formats · `91be1d5` LICENSE + LICENSE-CONTENT ·
`bece3dd` CITATION.cff ORCID · `48ccaa3` canto_config · `6d087cc` map_phenotype subsets ·
`c8160bd` backlog reminders
