---
created: 2026-07-03
type: documentation
tags: [docs]
project: PHI-Weaver
---

# PHI-Weaver Backlog

Durable to-do / known-gaps list. (The harness's in-session task tools don't persist across
sessions, so **this file is the record** — add items as they come up; tick `[x]` or delete when
done.) Larger design items live in `DESIGN-DECISIONS.md` (D11 deferred) and
`PLUGIN-ARCHITECTURE.md`.

## Tooling / bugs
- [ ] **Make the "host" label rule self-checking** (added 2026-07-17).
  `phiweaver/lookup/term_context.py` classifies a PHIPO term as in-host if its label contains the word
  "host". That rule was **verified live** before relying on it — "host-free", "axenic" and
  "free-living" all return `no_match`, so no PHIPO label negates the word — but nothing re-verifies it.
  If PHIPO ever gains a label like "growth in host-free medium", the guard silently mislabels it and
  the failure is invisible. The docstring says "re-check this rule", which is a comment, not a check.
  The unit tests are network-free by design, so this needs either a separate online check or a step in
  the `ontology-term-request` skill. **Silent staleness, not a live bug.**
- [ ] **Resolve PHIPO offline + sweep for structural holes** (added 2026-07-17). **(a) done
  2026-07-17; (b) still open**, sequenced after phipo#454's ruling.

  **(a) Vendor PHIPO offline** — ✅ **done 2026-07-17.** `phiweaver/lookup/data/phipo-base.obo`
  (release 2026-03-12, 1327 terms / 210 obsolete); both `map_phenotype` and `validate_ontology_ids`
  resolve `PHIPO:` offline; **OLS dropped for PHIPO, kept for GO**. Verified at vendoring that OLS
  served the *same* release, so nothing was lost. `map_phenotype --include-obsolete` now surfaces
  deprecated terms (the #452 blind spot) and prints the `data-version` on every search. Refresh
  command + the `phipo-base.obo` vs `phipo-edit.owl` rule: `phiweaver/lookup/data/README.md`.
  **Two things found on the way, worth knowing:**
  - *The borrowed scorer could not return `no_match`.* `map_condition`'s exact/substring/Jaccard
    scorer let one shared generic token carry a match ("to" is in 39% of PHIPO labels, "host" 25%),
    and its label-inside-query tier let the one-word label "phenotype" match any query containing the
    word. Since **`no_match` is what gap detection and `--log-gaps` key on**, that silently broke gap
    detection. Fixed with **IDF weighting** (`build_idf`) + a tuned `MIN_SCORE = 20.0`: true matches
    score 35–100, prose/junk 0–12.7. **`map_condition` still has the unweighted scorer** — PECO is a
    different corpus so it may be fine, but nobody has checked. *(Candidate follow-up.)*
  - *A wording gap validated the threshold.* "abnormal conidiation" scores 14.1, correctly below
    MIN_SCORE: **PHIPO is species-neutral by design** (its own header says so — `dc:description
    "Ontology of species-neutral phenotypes…"`), so the process noun "conidiation" appears **nowhere
    in the file, not even as a synonym**. Retrying species-neutrally finds the term — which is
    lesson L2 exactly. See "PHIPO is species-neutral" below; this find **corrected a false gap**.

  **Bonus: it simplifies the benchmark sandbox.** A bundled `phipo-base.obo` needs no network during a
  scored run, so the allowlist stays default-deny with **no PHIPO exception**. That matters because
  `github.com/PHI-base` hosts *both* the `phipo` ontology **and** the curated data repos (= the answer
  key), so "ontology yes, data no" cannot be expressed at the domain level. **PHIPO is a tool, not an
  answer** — a curator works with the ontology open — but the data must stay blocked. Vendoring means
  the run never has to make that distinction. **Constraint: the `git pull` + re-vendor is maintenance
  and must happen *outside* scored runs.** See the sandbox-allowlist item under Deferred.

  **⚠ Two files, two questions — do not collapse them.** "PHIPO" is three different things, and they
  diverge *right now*:

  | source | what it is | use for |
  |---|---|---|
  | `phipo-base.obo` (618K, repo root) | the **release artifact** — PHIPO's own terms | **annotation lookup + ID validation** |
  | `phipo-edit.owl` | the **working file** — contains **unreleased** terms | **gap analysis only** |
  | OLS | the release as OLS loaded it | — (nothing, once local) |

  Use `phipo-base.obo` for "give me a term for this phrase", because that is the question a curator
  actually has: *can I annotate this?* Use `phipo-edit.owl` only for "is this a gap, and why" —
  obsolete terms, sibling structure, the sweeps in (b). **`phipo-edit.owl` must never be a source of
  suggestions to a curator.** Concretely: it contains PHIPO:0001456 today (PR #454, unreleased,
  absent from PHI-Canto) — suggesting it would be a bug that looks exactly like a feature. Note
  `phipo.obo` (7.3M) is the **wrong file** — it inlines GO, CHEBI and other imports.

  **On search quality (the honest cost).** OLS is Solr-backed with stemming and synonym expansion;
  the offline scorer in `map_condition.py` is exact > substring > token-overlap (Jaccard), and cruder.
  Acceptable, because **lesson L7 establishes OLS's ranking is not trustworthy anyway** — it
  confidently returned within-host PHIPO:0000234 for an in-vitro phrase and `asexual spore lysis
  absent` for a DON query. A human reads every candidate regardless, so **recall matters and ranking
  does not**: favour a generous `--rows` over clever scoring. The real cost is **staleness** — the
  clone needs a `git pull` + re-vendor where OLS was self-updating. PHIDO already carries that
  burden (refresh instructions in `data/README.md`), so it is an existing practice, not a new one.

  **(b) Sweep the structure for holes**, which (a) makes mechanical. Everything done by hand for PR
  #454 was: grep for an obsoleted term, walk up to the parent, enumerate siblings, diff the
  dimensions across sibling chemicals. Two sweeps worth having:
  - *"which chemicals have `decreased`+`increased` but no `absent`?"* — **would have found the DON
    hole with no paper at all**;
  - *"which obsolete terms have no `replaced_by`/`consider`?"* — the hygiene gap that kept
    PHIPO:0000503 invisible for five years. Useful to hand PHIPO in its own right.

  **The limit, and why this does not automate gap detection.** A sweep generates **candidates, not
  judgements**. A hole in a branch may be deliberate (the parallel-terms test says the *dimension* is
  live, not that *this* chemical should carry it) or may simply be something nobody has ever
  measured, in which case there is no evidence to file. The shape stays: **the sweep finds structural
  holes, curation supplies the evidence that a hole matters, a human decides.** Lesson L7's corollary
  — gap detection cannot be automated — is unchanged; this makes the first third free, not the last.
  The ledger still under-counts.
- [x] **PHIDO validation gap** (fixed 2026-07-04) — OLS4 does not host PHIDO, so every PHIDO ID
  used to return `not_found` (a false negative). Fixed by vendoring the ontology
  (`phiweaver/lookup/data/phido.obo`, from github.com/PHI-base/phido) and resolving PHIDO
  **offline** against it — existence + obsolescence, no network. GO/PHIPO still use OLS.
  Refresh instructions: `phiweaver/lookup/data/README.md`. Surfaced 2026-07-03 curating
  PMID:26177154 (PHIDO:0000164 Fusarium wilt), which now validates 7/7.
- [x] **PomGeneEx (RNA-level) qualifier vocabulary gap** (surfaced 2026-07-11; scope reduced to
  terms-only 2026-07-16; **done 2026-07-16**) — weaver knew the `wt_rna_expression` annotation type
  and the phrase "RNA level increased" (one gold-standard example, PINE1/PMID:35468894) but not the
  full controlled set of RNA-level qualifiers. **Terms-only scope (curator, 2026-07-16): the
  qualifier IDs are NOT needed — only the term phrases** (no offline ontology, no `PomGeneEx` prefix
  in `validate_ontology_ids`). The seven controlled qualifier phrases (PHI-Canto UI screenshot
  2026-07-11): RNA level increased, RNA level decreased, RNA level unchanged, RNA present, RNA
  absent, RNA level constant, RNA level fluctuates. **Surfaced to the drafting workflow (2026-07-16):**
  authoritative phrase table + per-phrase "use when" added to `Gene-for-Gene-Curation-Methodology.md`
  §9; a controlled-phrase step in the `phenotype-annotation` skill; and a QC flag in the `curation-qc`
  skill for free-prose RNA-level qualifiers. Motivating case: PMID:40756215 (Pt31812/Lr42), where the
  qRT-PCR "RNA level increased during infection" item was left as prose.
- [ ] **Per-article token attribution** (tool landed 2026-07-11) — `phiweaver/article_tokens.py`
  attributes a batch session's token spend to each curated paper (PMID) + a shared-overhead split
  (equal 1/N, or `--weight-by-direct`), joining First-author/Year/Title from the tracking DB. Reads
  batch PMIDs from the draft `meta` blocks and segments turns by the per-paper draft references
  already in the transcript (no new marker discipline). Cache-read is counted wholly as shared
  overhead (session-cumulative, not attributable to one paper). Follow-ups: (1) ~~wire it into the
  batch skill~~ **done 2026-07-11** — `benchmark` SKILL step 7 emits `BATCH-TOKENS.md` for the
  session log; (2) ~~confirm the tracking-DB filename so `--db` auto-detects~~ **done 2026-07-11**
  — defaults to the canonical `11-CLAUDE-AI/db/phi_canto_tracking.db`.
- [ ] **Persisted token history + recuration comparison** (landed 2026-07-11) — `--record` writes
  the **raw** per-article numbers (direct tokens + session `overhead_total` + `n_articles`, never
  the allocated `1/N` total) to the tracking DB via an `article_tokens`-namespaced migration
  (`article_token_costs` table). Keyed by `(pmid, session_id, model)`: re-running on one transcript
  upserts (no double-count); **recurating a paper in a new session — e.g. a different model — is a
  new row**, so `--history <PMID>` compares models like-for-like. The `1/N` split is derived on
  read, so old rows survive an allocation-policy change. Follow-ups: (a) ~~surface the history in the
  Article-Registry dashboard~~ **done 2026-07-11** — `generate_article_registry` adds a "💰 Token
  Costs" section (per-model roll-up + per-paper rows with $ estimate) when any batch was recorded,
  and `python3 -m phiweaver.tracking.daily_curation tokens [PMID]` prints the same as a terminal
  report (**both done 2026-07-11**); (b) ~~per-bucket
  cost pricing~~ **done 2026-07-11** — the four token buckets are stored + priced separately at each
  row's model rate (`PRICES` table), so `--cost`/`--history` show a per-paper `$` estimate and the
  same paper costs less on a cheaper model (recomputed on read; a rate change doesn't invalidate
  rows). Ties into the **Recuration-comparison workflow** item below (same "DB is the aggregation
  home, grows over time, neutral diff" shape).

- [x] **`query_uniprot --locus-tag` misses strain-proteome loci** (surfaced 2026-07-14; **fixed
  2026-07-16**) — for a gene named only by an NCBI locus tag, the tool queried the **species** taxon
  and returned `not_found` when the entry lives under a **strain** reference-proteome taxon. Curating
  PMID:42089373 (5 *F. pseudograminearum* Sdh subunits), `--locus-tag FPSE_04172 --organism 101028`
  (species) → `not_found` for all five; a direct UniProtKB REST query resolved them under **strain
  CS3096, taxon 1028729** (K3UT42/K3VJU5/K3UP39/K3VHW6/K3VVK3). **Fix (query_uniprot.py):** when a
  locus-tag search scoped to an organism returns empty, the lookup **retries once without the organism
  filter** (matching the locus tag across all taxa) and flags the result `organism_filter_relaxed` —
  `format_human` prints a strain-mismatch warning so a curator confirms the strain (experimental
  isolate vs reference proteome) rather than getting a false `not_found`. Scoped to locus-tag searches
  only (a gene-only search does not broaden). +4 tests in `tests/test_query_uniprot.py` (fallback hit,
  no-fallback-when-species-hits, fallback-still-not-found, gene-only-no-broaden); all 13 pass.

- [x] **Vendor PHI-ECO (conditions) offline + validate `PECO:`** (done 2026-07-15). PHI-ECO
  (prefix `PECO:`) is **PHI-base-local** — and crucially the OLS ontology named `peco` is the
  *unrelated* Planteome ontology sharing the prefix, so PECO **must** resolve offline, never via
  OLS. Vendored `phiweaver/lookup/data/phi-eco.obo` (from github.com/PHI-base/phi-eco, 658 terms)
  and taught `validate_ontology_ids` the `PECO` prefix (offline existence/obsolescence, reusing the
  PHIDO OBO parser via a shared `_validate_offline`). +5 tests; reference + term-request workflow in
  `07-Standards/Ontology-Terms-Reference.md`. **Generation side also done 2026-07-15:** added the
  offline `map_condition` lookup (`phiweaver/lookup/map_condition.py`, condition phrase → PECO
  candidates over the bundled ontology) and wired it into `phenotype-annotation` + `curation-qc`,
  so the drafting workflow emits PECO Condition terms (demonstrated on PMID:42089373's interaction
  annotations). PHI-ECO is qualitative (no "PDA"/"25 °C" term) so numeric specifics stay in the
  comment — the medium→PECO granularity is the curator's call.

- [x] **Annotation-extension relations + allowed values (Canto config)** — *resolved 2026-07-15*
  (surfaced 2026-07-15, PMID:42089373 review; = "C2"). PHI-Canto annotations carry `relation → value`
  **extensions**. The doubt was that `infective_ability = reduced virulence` in the Sdh draft looked
  like a **guess**. The curator supplied `config/annotation_extension/phipo_extensions.tsv` from the
  private PHI-base/config repo, which settles it: **`infective_ability` is a real, attested relation**
  (not a guess), and its value must be a **PHIPO term ID under `PHIPO:0001179` *infective ability
  phenotype*** — so "reduced virulence" is `PHIPO:0000015` (confirmed a descendant of PHIPO:0001179),
  written as the ID, **not** bare text. Done: vendored the TSV offline (weaver is *not* pointed at the
  private repo — data/README.md), added `phiweaver/lookup/extension_config.py` + `tests/
  test_extension_config.py` (attested-relation + value-type checks, mirroring BTO/PECO), documented the
  attested-relations table in `Ontology-Terms-Reference.md`, and fixed the `infective_ability` rule in
  `PHI-Canto-Curation-Conventions.md`. Tracks `CURATION-LESSONS.md` L5 (→ applied).
  - *Remaining (curator-facing, low priority):* the gold-standard example curations still display
    `infective_ability reduced virulence` as text — decide with Hsin-Yun whether examples/drafts should
    carry the term ID `PHIPO:0000015` in the value. Also **not** validated offline yet: term-value
    *subtree* membership and the per-primary-term `domain ID` subset constraints (deeper checks).
  - *Also vendored 2026-07-15:* the sibling configs `phibase_go_extensions.tsv` (GO annotations) and
    `phido_extensions.tsv` (disease annotations), plus `phipo_extension_relations.obo` (relation
    *definitions*, kept as reference — incomplete, not a validation source). `extension_config` now
    loads all three (`--config phipo|go|phido`). Neither GO nor disease extensions are used by current
    drafts. See `phiweaver/lookup/data/README.md`.

- [x] **PHIPO_EXT extension values — existence check CLOSED** (2026-07-16). PHIPO_EXT is a **separate**
  PHI-base ontology (not part of PHIPO — PHIPO obsoleted its old gene-for-gene term in 2020 and moved
  these into PHIPO_EXT; the PHIPO release has zero `PHIPO_EXT` ids). Its terms live in the **public**
  `github.com/PHI-base/phipo_ext` repo (`phipo_ext.obo`, CC-BY 4.0, 47 terms/15 obsolete). Vendored to
  `phiweaver/lookup/data/phipo_ext.obo` and wired into `validate_ontology_ids` (new `PHIPO_EXT` prefix,
  resolved offline like PHIDO/PECO; splitter/extractor match `PHIPO_EXT` before `PHIPO`). So
  `gene_for_gene_interaction` / `inverse_gene_for_gene` values are now existence + obsolescence checked.
  - *Contrast:* `infective_ability` values (reduced virulence, etc.) were always plain PHIPO terms
    (OLS-checked); this closes the *other* gate.

- [x] **FYPO_EXT extension values — existence check CLOSED (with a caveat)** (2026-07-16). The
  penetrance/severity value terms (`high`/`medium`/`low`/`complete` + root `FYPO_EXT:1000000`) are a
  tiny **PomBase** extension ontology. Vendored `fypo_extension.obo` from **PHI-base/canto**
  (`t/data/fypo_extension.obo`; only 5 terms so the test-data copy is the whole ontology) and wired
  `FYPO_EXT` into `validate_ontology_ids` (offline, like PHIPO_EXT). *Caveat:* `phipo_extensions.tsv`
  points `has_severity`/`has_penetrance` at `FYPO_EXT:1000001`/`1000002`, which are **grouping/gate
  roots not defined as terms** in the file — a literal such value reads `not_found`, which is correct
  (curators annotate high/medium/low/complete, not the root). **Confirmed non-issue (2026-07-16):** we
  don't need those root ids — they're never annotated as values, `extension_config` uses the range
  only to type-check (not existence-check), and we don't do subtree-membership validation (the only
  thing that would need them). The values curators actually pick all resolve. Nothing to chase; noted
  only as historical numbering drift (file root is `FYPO_EXT:1000000`; config points at `1000001/2`).
  - *Note on PHI-base/canto as a source:* its `t/data/*_small.obo` are **truncated test fixtures**
    (`phipo_small.obo` = 2 terms, `go_small.obo` = 21), and `t/data/extension_config.tsv` is a 9-line
    stub — do NOT source the full ontologies or the real extension config from there. FYPO_EXT is the
    lone exception because the ontology is genuinely tiny.

- [ ] **Licensing done; `CITATION.cff` still has blanks** (added 2026-07-21). The repo had been
  **public with no license at all** — verified live, `gh api repos/PHI-base/phi-weaver` returned
  `license: null, visibility: public`, with nothing in git history (`git log --all -- LICENSE`
  empty). That state means *all rights reserved*: public visibility grants nobody any rights, so
  anyone at another institution wanting to build on the standards would have been blocked by their
  own legal review. `README.md` had claimed MIT and linked to a LICENSE file that was never created.
  - ✅ **Dual-licensed 2026-07-21**, per the hybrid split — `phiweaver/` is code, but most of the
    repo (`07-Standards/`, `skills/`, `docs/`, gold-standard examples) is documentation and curated
    data. **`LICENSE` = MIT** (software), **`LICENSE-CONTENT` = CC BY 4.0** (content), README section
    rewritten to state the split, `license: MIT` added to `CITATION.cff`. CC BY matches house norm:
    PHIPO ships CC BY 3.0 Unported, `phipo_ext` CC BY 4.0. Vendored ontology files under
    `phiweaver/lookup/data/` keep their own upstream licenses (noted in both files).
  - **⚠ Still worth confirming with Rothamsted / James.** Copyright sits with the **institution**
    (BBSRC-funded work), not with an individual, and the copyright line reads
    **"Copyright (c) 2026 Rothamsted Research"** — that was our choice, not a checked fact. If
    PHI-base has an existing org position, match it; changing the license later is easy while the
    external contributor set is still small, and gets harder after.
  - **`CITATION.cff` drafted 2026-07-21** (repo root). GitHub auto-detects the filename and adds a
    "Cite this repository" button (APA + BibTeX); Zenodo reads it to pre-fill a release deposition.
    ✅ Martin Urban's **ORCID** added 2026-07-21 (`0000-0003-2440-4352`, verified against ORCID's
    public API — it resolves to the right person). Two things still left out so the file doesn't
    assert anything untrue: **(1)** the **co-author list** — adding someone needs *both* an
    intellectual contribution *and* their agreement, since a name on a curation tool implies they'd
    stand behind its output; note contribution doesn't require having read the repo (the standards
    encode Hsin-Yu's methodology), but consent is not optional, and until each says yes credit
    belongs in the README **Acknowledgments** section, not the author list. ORCIDs for co-authors
    are optional, though they let Zenodo push a release DOI onto the person's ORCID record
    automatically. **(2)** `version`/`date-released` (omitted rather than left to go stale) and the
    Zenodo **concept DOI** once a release is minted. Add a `preferred-citation:` block if a
    PHI-Weaver paper is ever published, so citations point at the article instead of the repo.
  - **Validate before relying on it** — a YAML typo silently kills the GitHub button with no error.
    `cffconvert` or the `cff-validator` Action.

- [ ] **PMC full text as an input format (PMID→PMCID check + JATS parser)** (added 2026-07-21).
  Today the only ingest route is PDF (`phiweaver/pdf/pdf_convert.py`, PyMuPDF). For open-access
  papers — most of what PHI-base curates — **PMC's JATS XML is a strictly better input**: sections,
  tables and references are already tagged, so gene symbols, strain IDs and table structure survive
  instead of being reconstructed from page layout. Two pieces, and (a) is useful on its own:

  **(a) Resolve PMID → PMCID.** One call to NCBI's ID Converter
  (`https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/?ids=<PMID>&format=json`) answers "is there
  full text?" definitively, so the PDF-vs-PMC choice stops being a guess. Worth checking **Europe
  PMC** too — it mirrors PMC and adds content PMC doesn't carry, which matters for the UK/European
  plant-pathology journals we curate from.

  **(b) JATS → markdown converter**, the `pdf_convert.py` equivalent. Needs to handle JATS tables
  and section nesting; drop `<ref-list>` and `<front>` boilerplate.

  **On token cost — the intuition is backwards, but only after parsing.** *Raw* JATS is far more
  expensive than a PDF (every citation an `<xref>`, every author a name nest, the whole reference
  list marked up structurally): order 80–150k tokens vs 15–25k for PDF-extracted text. *Parsed*, it
  wins: ~10–15k, because PDF extraction drags per-page furniture (running heads, page numbers, DOI
  footers) through the whole document and can't cleanly cut the reference list, which is often
  30–40% of the extracted text. **So the real cost of this item is the parser, not context size.**
  Figures are the open question — `pdf_convert.py`'s caption extraction has no obvious JATS
  counterpart to reuse. *(Numbers are ballpark from typical article sizes, **not measured on our
  corpus** — worth confirming on one already-curated paper before committing to (b).)*

  **Timing note for (a):** the PMID→PMC gap is set by the journal's access model, not by PMC
  processing. Fully-OA journals deposit at publication (full text within ~2 weeks); paywalled ones
  are 6–12 months or never. So recent OA papers usually *are* in PMC — don't assume otherwise.
  **See:** `docs/FAQ.md` ("Should I curate from PDF or EPUB?").

## Ontology coverage gaps (PHIPO term requests)
_Curatable phenotypes seen in papers that have **no** PHIPO term — captured and flagged in the draft,
not forced onto a wrong ID. Candidates to raise with the PHIPO/PHI-base ontology team._

_Gaps met during drafting now also accumulate in **`docs/ontology-gaps.jsonl`** (`gap_log.py`,
`ontology-term-request` skill), which ranks them by how many distinct papers needed each one —
frequency being the argument an ontology editor responds to. That ledger **under-counts** and does not
replace this hand-curated list: `no_match` cannot see a wrong-context match (the #452 shape), and one
irrelevant candidate masks a real gap (lesson L7). Treat the two as complementary._

_Note the recurring shape: **#452** (free-living "absent DON") and the free-living conidiation item
below are the same failure — a within-host term exists, the free-living branch stops short, and the
search offers the within-host term anyway. `phipo#453` asks whether that split is even two-way._

_**A third shape, found 2026-07-17 (PR #454): the term was obsoleted and never re-created.** OLS hides
deprecated terms, so this is invisible to every search we run and records as a clean `no_match` — #452
was written blind to PHIPO:0000503. **Grep `phipo-edit.owl` before calling anything a gap** (local
clone: `/mnt/z/Computer/GITHUBrepositories/phipo`), then run the parallel-terms test: if the sibling
concepts kept the dimension it is an oversight (fill it); if they all lost it, that was a modelling
decision and re-creating the term silently reopens it. See the `ontology-term-request` skill, step 5._
- [x] **Mycotoxin / DON production — terms exist** (corrected 2026-07-15). Earlier logged as a gap;
  **wrong** — PHIPO already has free-living DON phenotype terms: **PHIPO:0001445** decreased level of
  deoxynivalenol, **PHIPO:0001447** increased, **PHIPO:0001443** abnormal deoxynivalenol biosynthesis,
  **PHIPO:0001441** abnormal mycotoxin biosynthesis, **PHIPO:0001182** normal level (+ within-host
  variants PHIPO:0000219/232/233/234). The earlier `map_phenotype` phrasings ("decreased deoxynivalenol
  **production**") just didn't match the ontology wording ("decreased **level of** deoxynivalenol").
  PMID:42089373 reduced DON now maps to PHIPO:0001445. **Lesson for phiweaver:** when a phenotype
  phrase returns `no_match`, retry with the "level of" / "abnormal X biosynthesis" phrasings before
  declaring a gap. Two genuine *residual* items below.
- [ ] **Typo in PHIPO:0001441 label** — "abnormal mycotoxin **biosythesis**" (should be
  "biosynthesis"). Cosmetic ontology fix to raise with the PHIPO team.
- [ ] **Toxisome formation / ER-to-toxisome remodelling** — reduced toxisome number and failure of the
  ER to remodel into toxisomes (ΔFpSdhC2, PMID:42089373 Fig 3C, Tri1-GFP confocal). No PHIPO term for
  this subcellular structure.
- [ ] **SDHI fungicide sensitivity terms for 4 chemicals** — PHIPO has per-chemical
  sensitivity/resistance terms for fluopyram, boscalid, penflufen, thifluzamide (and carboxin) but
  **not** cyclobutrifluram, pydiflumetofen, fluxapyroxad, or isofetamid (PMID:42089373). Those four fell
  back to the generic PHIPO:0000021 (increased sensitivity to chemical) / PHIPO:0000022 (increased
  resistance to chemical) with the chemical named in conditions. Request per-chemical child terms.
- [x] **Complete loss of conidiation (free-living) — terms exist** (corrected + **closed by the
  curator 2026-07-17**: *"asexual spores absent covers it"* — annotate **PHIPO:0000061**). Earlier
  logged as a gap ("no free-living 'absence/abolished asexual sporulation' term, so total conidiation
  loss is under-described"); **wrong on two counts**, both wording:
  - **PHIPO:0000061 "asexual spores absent"** exists, is current, and is **free-living**
    (`namespace: single_species_phenotype`, no "host" in the label). Its definition is "a
    reproductive phenotype where asexual spores are absent", and it carries the **EXACT synonym
    "conidia absent"** — so `map_phenotype "conidia absent"` returns it as an exact ★ hit. The
    within-host counterpart the item cited (PHIPO:0000468) is the *other* context, not the only one.
  - **Two wording steps hid it:** (1) *species-specific → species-neutral* — "conidiation" appears
    **nowhere** in PHIPO, by design; (2) *process noun → entity noun, for presence/absence* — both
    forms exist but carry **different dimensions**: the *process* ("asexual sporulation") has quality
    (`normal`/`abnormal`) and timing (PHIPO:0000053 `delayed` / PHIPO:0000054 `premature`) but **no
    free-living absence term at all**, while the *entity* ("asexual spores") has count, size and
    presence/absence. So "abolished asexual sporulation" misses — absence is not a dimension of the
    process form — while "conidia absent" hits.

  **Curator ruling (2026-07-17):** *"asexual spores absent covers it"* — the **entity being absent
  covers the process having failed**; they are not distinct phenotypes for annotation. So
  PMID:41020836 ("completely lost conidiation") and PMID:42089373 (ΔFpSdhA/B/D + double) annotate to
  **PHIPO:0000061**, and no term request was ever needed. Generalised as **lesson L8**. See "PHIPO is
  species-neutral" above and lesson L2.

## Curation workflow
- [x] **Store input PDFs + output docs on Google Drive** (added + **verified 2026-07-19**; user has
  Google Drive for Desktop on Windows). **Low effort, no code change** — the pipeline's whole storage
  layer is a single filesystem path (`PHI_LITERATURE_ROOT` → `active/` input, `completed/` output,
  `media/` figures). **Verified live:** `D:\GoogleDrivePHI` is visible in WSL at
  `/mnt/d/GoogleDrivePHI`; `CurationPipeline` resolves `PHI_LITERATURE_ROOT=/mnt/d/GoogleDrivePHI/
  PHI-Canto-Literature` and the `active/`/`completed/`/`media/` folders were created + file
  round-tripped on the Drive mount. The tracking DB (`11-CLAUDE-AI/db/`) stays local (not sent to the
  literature root). Documented in `docs/STORAGE-CONFIGURATION.md` ("Storage on Google Drive"); fixed
  the stale verify snippet there (imported the old shim class path). **Caveats (in the doc):** keep
  the SQLite DB off Drive; sync latency before a file is readable; `media/` quota on big batches; use
  a **private** Drive folder. **Deferred harder option:** a native Drive-API storage adapter
  (headless, no mounted FS) — only needed for the future ROGER orchestrator; not worth it now.
- [ ] **Confirm open clarifications from Hsin-Yun's 2026-07-15 review** (applied with sensible
  defaults; fold her answers into `07-Standards/PHI-Canto-Curation-Conventions.md`): (D1) canonical
  **gene-symbol source** — UniProtKB gene name vs. "strip the species prefix" (drafted as
  strip-prefix, e.g. `SdhA`); (D2) is there a **full allele/genotype naming standard** beyond the
  deletion Δ-suffix; (D3) does **"Figure in full"** extend to other abbreviations (e.g. "Table");
  (D4) **filenames** keep the PMID/`FpSdh` basename (kept — cosmetic, renaming would orphan the
  queue/docx). Also the GO-no-biochem-evidence question (`CURATION-LESSONS.md` L3) is still open
  with her.
- [ ] **How much term *design* should a request carry?** (raised 2026-07-17; for Hsin-Yun) — the
  `ontology-term-request` skill's line is **"evidence, not design"**: never propose a term's parent,
  definition or hierarchy placement, on the principle that this project does not assert in-silico
  conclusions as fact (the same reasoning behind the ISS rejection). **But PHIPO's own
  `CONTRIBUTING.md` asks requesters to suggest "label (name), definition, references, position in
  hierarchy"** — so our guardrail is *stricter than the ontology team's house rule*, and was drawn
  against a constraint they do not actually impose. James has since asked for AI-drafted **PRs**
  (not issues) for the narrow pattern-extension case, and PR #454 duly proposed a label, definition
  and parent — all three of the things the skill forbids. The skill now scopes the prohibition to
  non-pattern-extension requests and records this as open. **Ask Hsin-Yun where the line should sit**,
  framed as a discussion, not a ruling: is "evidence only" the right default for a request that needs
  a *new* branch, given CONTRIBUTING.md invites more? Does the pattern-extension carve-out match how
  she would want it bounded? **Blocks:** nothing — the skill has a working default. Supersede the
  "Two routes" section + `## Purpose` guardrail in `skills/ontology-term-request/SKILL.md` when she
  answers. Worked context: PR #454 / issue #452 (see "Waiting for response").
- [ ] **Curator-triggered term-design proposals → GitHub issue** (requested 2026-07-17; **sequence
  after the ruling above**, which sets how much design a proposal should carry). Wanted: *"when I
  trigger it, PHIPO design suggestions are obtained, then logged as a GitHub issue for human curator
  review."* This fills the case the skill currently does **not** cover — it is written as a binary
  (pattern extension → PR; everything else → evidence-only issue) and is silent on *"the curator
  explicitly asked for a draft anyway"*.

  **Why the trigger is the whole design.** The guardrail's principle is "do not **assert** in-silico
  conclusions as fact" (the ISS reasoning) — not "never write a proposal". An explicit trigger makes
  the output a **proposal the curator requested**, not something weaver volunteered; the issue keeps
  the **editors deciding**. So the guardrail survives intact: weaver still never files design unasked.
  PHIPO's `CONTRIBUTING.md` already asks requesters for "label, definition, references, position in
  hierarchy", so the *artifact* is what the ontology team wants anyway.

  **Design notes (for whoever builds it):**
  - **Extend `ontology-term-request`, don't fork it** — as a third route. Steps 1–7 (retries, the
    obsolete + parallel-terms checks, the ledger dedup) must run **first and unchanged**: on this
    session's evidence the majority of "gaps" are wording or obsoletion, so a proposal drafted before
    those checks would mostly be **designing terms that already exist**. That is the main failure mode.
  - **State the confidence honestly, and what it was patterned on** — or that there was **no pattern**.
    A pattern extension has zero degrees of freedom (PR #454); outside that, weaver is *guessing* at
    the parent and the genus-differentia definition, which is exactly the editors' expertise. A
    confident-looking draft with no pattern behind it is the dangerous artifact.
  - **Issue, not PR.** PRs are for pattern extensions only (James's offer). A design proposal is a
    claim on the editors' judgement, so it goes where judgement lives.
  - Record the issue URL back against the gap (`gap_log record --filed`) so it stops resurfacing.
- [ ] **Format convergence** — phiweaver *drafts* use the example-template body shape while *gold
  standards* use PHI-Canto's structure; converge them (toward PHI-Canto) so retrieval and
  benchmarking compare like-for-like. *Partly done 2026-07-04*: the example `annotation_types`
  vocabulary now IS PHI-Canto's own annotation types (`TAGS.md`), and `INDEX.md` tracks coverage
  against them. Still to do: converge the draft-template **body shape** toward PHI-Canto's.
- [ ] **Obsolete PHIDO IDs in source PHI-Canto session** ([#1](https://github.com/PHI-base/phi-weaver/issues/1)) — session `02e545aba274d209`
  (PMID:39787257) curated now-obsolete disease-name terms PHIDO:0000163 / PHIDO:0000331. The
  gold-standard example was updated to the current PHIDO:0000162 / PHIDO:0000329; update the
  live PHI-Canto session too so source and example stay in step. (External / curator action.)
- [x] **Physical-interaction scope** (resolved 2026-07-04) — PHI-Canto **does** capture
  protein–protein interactions, via a dedicated `physical_interaction` annotation type
  (Interactor A/B + taxon + evidence: Co-purification / PCA / Two-hybrid). Confirmed by the
  gold-standard example PMID:35468894 (PINE1 effector × host PGIP). It is now a scored/example
  topic; `physical_interaction` is one of the 12 tracked annotation types.
- [x] **All 12 PHI-Canto annotation types covered** (2026-07-04) — the gold-standard library now
  has ≥1 validated example for every PHI-Canto annotation type (`annotation_types` vocabulary in
  `TAGS.md`). Live tracker: the auto-generated "Coverage" table in `curation-examples/Curation-Examples-INDEX.md`
  shows **12/12**. Five examples: PMID:26177154, 39787257, 35468894, 23498959, 37177781. Ongoing:
  keep adding examples for **depth** (more cases per type / more pathosystems), not breadth.
- [ ] **Recuration-comparison workflow** (biocurator vs phiweaver; future). Distinct from the
  gold-standard library — that stays small and rarely updated; this is an *ongoing* stream.
  Biocurators keep curating PHI-Canto articles by hand without phiweaver; recurate those same
  articles with phiweaver and diff the two. Goal: compare **different biocurators against
  phiweaver** (and each other) and use the divergences to fine-tune phiweaver or train biocurators.
  Neither side is declared "correct" — it's a **neutral, deterministic diff**, not phiweaver scoring
  itself; a human only adjudicates the divergent rows (that verdict is the training/tuning signal).
  phiweaver must still recurate **blind** (never sees the biocurator's export as input — reuse the
  `benchmark` skill + network sandbox). Pieces:
  - **`recuration-import` skill** (sibling of `gold-standard-import`): biocurator PHI-Canto PDF →
    structured record keyed by the same 13 annotation-type items the scorecard uses, tagged
    `curator: <name>`; stored as an **uncommitted** sidecar JSON in external `active/` (unpublished
    biocurator data — not the gold-standard library, not `status: validated`). This is the "auto-
    populate the spreadsheet from the PDF" step.
  - **Comparison-matrix template** — a variant of the quality-matrix `.xlsx` with *biocurator* and
    *phiweaver* value columns and an auto-computed **Agree / Diverge / phiweaver-only / curator-only**
    column, instead of the human Correct/Incorrect rating. Keep it a distinct template (different
    semantics from the gold-standard scorecard).
  - **`compare_recuration.py`** — deterministic item-by-item diff (ID set-equality, term overlap) +
    completeness counts → fills the matrix; tests for the set-diff edge cases.
  - **Cross-biocurator aggregation** — extend `scorecards_to_csv` / `benchmark_report` with a
    `curator` grouping dimension. Open decision: aggregation home = SQLite tracking DB (recommended,
    grows over time) vs Excel Summary sheets. Second open decision: when a paper *is* in the
    gold-standard set, score phiweaver against it (Correct/Incorrect); otherwise stay a neutral diff.

- [ ] **LLM-as-judge / independent reviewer for benchmarking** (parked 2026-07-09; discussion only,
  see `11-CLAUDE-AI/SESSION-LOGS/2026-07-09-llm-as-judge-discussion.md`). Idea: use a *different* model
  (e.g. GPT-5.5) as an independent scorer/critic so phiweaver never self-validates (extends D12's
  "independent scorer" slot; does **not** replace the human validation gate, D13). Trigger: GPT-5.5,
  given the paper + phiweaver draft + entry queue + scorecard, suggested improvements and scored lower
  than the curator. **Critical caveat: the judge must itself be ground-truthed** — validated against
  papers with a trusted human score-vs-gold (a confusion matrix) before any of its scores are trusted
  or reported; an un-calibrated LLM judge lacks PHI-base conventions and produces ambiguous low scores
  (real miss vs convention gap vs hallucination vs ambiguity). What was run was **reference-free**
  judging (judge invents its own ground truth), which is weaker than the gold-standard benchmark. Two
  uses at different bars: pre-review **critic** (low bar, adoptable) vs **benchmark scorer** reported
  to a team (high bar — ground-truth first, report alongside not instead of human scores; record the
  judge's model id in provenance, D7). Next step when resumed: adjudicate the GPT-vs-curator
  disagreements on the one paper already run, item by item, to decide viability. Distinct from the
  **Recuration-comparison** item below (that's a neutral biocurator-vs-phiweaver diff, not a judge).

- [ ] **PHI-Canto GitHub issues tracker — mine, don't ingest** (2026-07-09). Suggested as a
  biocuration knowledge source. Decision: it can contain useful convention decisions and ontology
  term-request threads, but must **not** be bulk-ingested into PHI-Weaver context — (a) issues are
  discussion (rejected/superseded/unresolved), so raw ingestion imports wrong conventions; (b) it
  lives on GitHub, already a **benchmark-leakage** source (see the sandbox-allowlist item) and must
  stay excluded from blind/scored runs. Pattern: mine **resolved/closed** convention decisions →
  write into the owning skill/standard/FAQ in our words with a `See:` issue-number pointer for
  provenance → the pipeline reads the curated convention, never the raw issue. To do: get the
  tracker URL, survey signal-to-noise (curation convention vs software bugs), then add it as a
  "sources to mine" reference (not context). FAQ: *"Can the PHI-Canto issues tracker feed
  PHI-Weaver's knowledge?"*.

- [ ] **Submit drafts into PHI-Canto for biocurator review** (planning; no code yet) — get the
  information from phiweaver drafts into the PHI-Canto web tool (<https://canto.phi-base.org/>).
  No write API exists; `canto_load.pl` is server-side only. Three routes assessed (assisted-entry
  queue / Canto session JSON + load / browser automation) with recommendation and open
  questions in **`docs/CANTO-SUBMISSION-ROUTES.md`**. Pivotal decision pending: server/admin access
  to canto.phi-base.org vs web login only. Route 1 (assisted-entry queue) is built — a structured
  `canto` block in the draft + a deterministic `entry_queue.py` (the single Route-1 output; the
  earlier `worksheet.py` was retired, D16). Scope notes in **`docs/CANTO-ROUTE1-BUILD-SPEC.md`** —
  biocurator entry into PHI-Canto *is* the validation step.

- [ ] **Activate the benchmark sandbox allowlist**: the airtight profile exists
  (`07-Standards/curation-benchmarking/benchmark-sandbox.settings.json`) — network allowlisted to
  UniProt + EBI OLS only, `failIfUnavailable: true`. Progress: **`bubblewrap` installed**
  (`/usr/bin/bwrap` 0.9.0, 2026-07-16) and the underlying isolation verified on this box — userns
  works and `--unshare-net` blocks connectivity while unsandboxed DNS resolves. Remaining: **run the
  one end-to-end test through Claude Code's sandbox** (`claude --settings
  07-Standards/curation-benchmarking/benchmark-sandbox.settings.json`, then confirm a UniProt/OLS
  lookup succeeds AND a `phi-base.org` / `raw.githubusercontent.com/PHI-base` fetch is blocked — the
  domain allowlist is enforced by Claude Code's sandbox layer, not raw bwrap), then use it for scored
  runs. This is the only route that
  also covers PHI-base's **GitHub data repos** (`github.com/PHI-base`, `raw.githubusercontent.com`),
  which can't be cleanly domain-denied. The local `.claude/settings.json` WebFetch deny on
  `*.phi-base.org` is the interim (website-only) control.

  **What is leakage and what is a tool** (clarified by the curator, 2026-07-17) — the line is *not*
  drawn by domain:
  - **PHIPO is a tool, not an answer. The sandbox must have full access to it.** A human curator sits
    down with the ontology open; withholding it doesn't make the benchmark harder, it measures a task
    nobody performs. Same for UniProt and GO.
  - **The curated PHI-base datasets *are* the answers.** `phi-base.org` and the PHI-base **data**
    repos hold existing entries for the very papers under test — a scored run that reaches them is
    reading the answer key. **Blocked.**

  **The coarseness problem:** `github.com/PHI-base` hosts *both* — the `phipo` ontology repo **and**
  the data repos. So "ontology yes, data no" **cannot be expressed at the domain level**; don't try.
  It doesn't bite today (the allowlist is default-deny to UniProt + OLS, and PHIPO rides in on
  **OLS/EBI**, not GitHub), but it would the moment anything fetched PHIPO from GitHub at run time.

  **Vendoring PHIPO dissolves this** (see the offline item under Tooling): a bundled `phipo-base.obo`
  needs **no network at all** during a scored run, so the sandbox keeps default-deny with **no PHIPO
  exception to get wrong**. The `git pull` + re-vendor is **maintenance, outside scored runs** — the
  one moment PHIPO legitimately comes from `github.com/PHI-base`. Note the local clone
  (`/mnt/z/Computer/GITHUBrepositories/phipo`) is ontology-only and is **not** a route to PHI-base
  data.

- [ ] **Automatic per-paper token logging**: `benchmark_report` can display curation tokens, but
  phiweaver does not measure them — they are supplied by hand in the `tokens` CSV column. Add a
  small logging step during drafting that records each paper's LLM token usage (from the CLI/API
  usage readout) into the scores (or the scorecard), so tokens flow into the report automatically.

## Waiting for response (filed — external action)
_Requests we have submitted and are now blocked on someone else (ontology team, curator). Chase
periodically; move back to the owning section if reopened, or tick `[x]` when accepted/closed._
- [ ] **Free-living "absent / abolished DON" term** — filed 2026-07-16 as
  [PHI-base/phipo#452](https://github.com/PHI-base/phipo/issues/452); **superseded 2026-07-17 by a PR,
  [PHI-base/phipo#454](https://github.com/PHI-base/phipo/pull/454)**, which closes #452. The free-living
  DON branch stops at PHIPO:0001445 "decreased" (used as closest); the only "absent" DON term,
  PHIPO:0000234, is *within-host* (wrong context for an in-vitro assay). Evidence: PMID:42089373 Table
  S4 (ΔFpSdhA/B/D + ΔFpSdhC1&2, no detectable DON).

  **What #452 missed:** the term **existed** as PHIPO:0000503 *deoxynivalenol absent from cell* and was
  obsoleted in the 2019 substance-level refactor — invisible from OLS, which hides deprecated terms.
  It is an **oversight, not a decision**: PHIPO:0001033 (pyocyanin) and PHIPO:0001105 (gliotoxin) both
  still live under PHIPO:0001034 *substance absent from cell*, while DON's decreased/increased were
  re-created in March 2025 and "absent" was missed. PR #454 re-creates it as PHIPO:0001456, patterned
  verbatim on 0001033. **Open for James:** whether 0001456 is the right ID to take (`phipo-idranges.owl`
  allocates by role, not editor, so there is no personal range), and whether PHIPO:0000503 should get a
  `replaced_by` pointer. **ODK QC CI passed** (2026-07-17) — confirming a local `robot`/ODK install is
  not needed to contribute terms. Awaiting James's review.
- [ ] **Is the in-host / free-living split always two-way?** — filed 2026-07-17 as
  [PHI-base/phipo#453](https://github.com/PHI-base/phipo/issues/453). PHIPO states context in the term
  label ("within host", "on host surface" vs plain labels), so an in-vitro assay cannot use a
  within-host term — the #452 failure. Asks whether two contexts are enough, or whether detached-leaf /
  host-extract / host-cell-culture assays need their own; whether a canonical in-host vs free-living
  branch list exists (we infer it from the label); and whether "on host surface" is a third context.
  **Blocks:** lesson L7's binary `free-living`/`in-host` assay-context split is weaver's proposal
  pending this answer — if a third context is needed, supersede L7 and widen
  `phiweaver/lookup/term_context.py`. Awaiting curator/ontology-team answer.
- [ ] **GO evidence code ISO — reopen the ISS-family ruling?** (raised by Hsin-Yu on
  `phi-weaver#8`, 2026-07-17; **not yet filed**). The team rejected ISS as too predictive/in-silico
  (`#246`), and ISO was assumed covered by that. But ISO is stricter: GO requires a `with/from` field
  naming the specific ortholog, the ortholog's own annotation must be experimentally supported, and it
  cannot chain off another ISS/IEA — so an ISO annotation traces to a real experiment in a named
  organism, which is the property ISS was rejected for lacking. Fits PHI-base's shape (the
  characterised ortholog is often in yeast). Decide whether to raise it as its own issue.

## Deferred (see DESIGN-DECISIONS.md D11 / PLUGIN-ARCHITECTURE.md)
- [ ] **Semantic recall over accumulated curation knowledge** (raised 2026-07-20). Today's memory —
  the flat `MEMORY.md` index, `LEARNING-SYSTEM.md`, the typed `CURATION-LESSONS.md` ledger, and the
  curation-example library — is read **linearly**: a human or the LLM scans it. That is the right
  tool while the corpus is small and it keeps every fact **human-auditable and git-versioned**. An
  embeddings-backed store (cf. the user's `gbrain`/Hermes stack: Postgres + pgvector, typed pages,
  `[[wikilink]]` graph edges, MCP) would add *semantic* retrieval — "have I decided something like
  this before?" across lessons, gene-for-gene cases and ontology rulings — which a flat index
  cannot do. **Do not adopt the full container stack now:** the corpus is a few dozen facts, and
  gbrain's autonomous nightly `dream` enrichment (an LLM silently rewriting/re-linking stored
  facts) conflicts with weaver's **declarative, reversible, human-approved** learning rule
  (`LEARNING-SYSTEM.md`) and the scientific-accuracy requirement that stored facts be
  provenance-tracked — it would have to be disabled to adopt safely.
  - **Trigger to reconsider:** when the lessons ledger / example library grows past what fits in
    context **and** we catch a draft (or ourselves) re-deciding something already ruled on — i.e.
    linear reading starts *missing* relevant priors. That is when semantic recall earns its keep.
  - **Proportionate move when the trigger fires:** keep markdown as the source of truth and add an
    **embeddings index over the existing markdown as a read-only layer** (retrieval only; `dream`
    off) — not the 3-container stack. Runs local on ROGER (D7) rather than via an external
    embeddings API, keeping unpublished curation data off third-party services. Aligns with the
    plug-in-host direction (D6) — a retrieval module, not core.
- [ ] Full machine-readable curation-record schema (first slice done: the draft `auto_check` block).
- [ ] Plug-in host + local AI on ROGER (long-term; needs collaborator / research-computing help).
- [ ] Optional: UniProt mapping for Zhang-2024 from its genome IDs; read Zhang supplementary S1–S7.
- [ ] **Rewire the 4 hand-vendored extension configs to a public source when available** (added
  2026-07-15; deferred 2026-07-16). `phiweaver/lookup/data/{phipo_extensions.tsv,
  phibase_go_extensions.tsv, phido_extensions.tsv, phipo_extension_relations.obo}` were **copied in
  by hand** from the **private** PHI-base/config repo (`config/annotation_extension/`) — no
  `curl`-able source, unlike the public `phido.obo` / `phi-eco.obo`. **When
  `config/annotation_extension/` is published to a public GitHub repo:** point the refresh
  instructions in `data/README.md` at the public raw URLs, pin the source commit, and drop the
  "copied by hand" provenance. Until then these are static snapshots that only update when the
  curator re-supplies them.
