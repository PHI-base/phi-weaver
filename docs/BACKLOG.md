---
created: 2026-07-03
type: documentation
tags: [docs]
project: PHI-Weaver
---

# PHI-Weaver Backlog

**Canonical for:** open tasks and known gaps. [`Roadmap.md`](Roadmap.md) is the readable
summary of the same ground — this file is the record. See [`README.md`](README.md).

Durable to-do / known-gaps list. (The harness's in-session task tools don't persist across
sessions, so **this file is the record** — add items as they come up; tick `[x]` or delete when
done.) Larger design items live in `DESIGN-DECISIONS.md` (D11 deferred) and
`PLUGIN-ARCHITECTURE.md`.

## Tooling / bugs
- [ ] **Ontology-access export for an outside LLM — shape decided, deliberately not built**
  (added 2026-07-30). If a consumer ever appears, add a **named profile** to the `FILES` list in
  `scripts/build_judge_handover.py` sourced from `phiweaver/lookup/data/README.md` (+
  `07-Standards/Ontology-Terms-Reference.md`, already bundled), plus a test asserting no profile
  contains a gitignored path — `canto_deploy.yaml` must never be republished. Do **not** write a
  second builder or a parallel export doc. **Trigger:** a real consumer, not a hunch. Full rationale
  and the four constraints: `DESIGN-DECISIONS.md` **D20**.
- [x] **PDF converter flattens tables and loses their columns** — *fixed 2026-07-26* (added
  2026-07-24, surfaced on PMID:9927411). Tables now arrive as **page renders**: the whole page a
  table sits on is rendered to PNG at 170 dpi beside the figures, and the report counts captions
  and renders separately so a miss can never again look like "this paper has no tables". The
  flattened text is left untouched — see the withdrawn in-body marker below.
  Spec: `docs/superpowers/specs/2026-07-26-pdf-table-extraction-design.md`;
  plan: `docs/superpowers/plans/2026-07-26-pdf-table-page-renders.md`. 8 commits, `9c7fd06..783a218`.
  - **The root cause was not the one this item named.** It was the **caption regex**:
    `^\s*(figure|fig\.?|table)\s*(\d+)` accepts Arabic numerals only, and the paper numbers its
    tables **Table I / Table II**. The converter found 22 figure captions and **0 table captions** —
    it did not believe the paper had tables at all. Widening the pattern to Roman and supplementary
    forms is the fix; everything else builds on it.
  - **`find_tables()` was measured, not assumed** — the structured option this item proposed
    returns **zero tables across all 10 pages** of the trigger PDF (PyMuPDF 1.27.2). Worse than the
    "unreliable on 1990s layouts" guessed here. Rejected on evidence.
  - **Whole page, not a crop.** A caption-anchored crop gives tidier images but a boundary
    heuristic decides where the table ends, and a wrong boundary clips a row — reproducing the very
    defect being fixed. The page render cannot clip.
  - **Verified on the trigger paper.** Table I renders legibly and its
    **"Appressorium formation (%) >95 >95 >95"** row — dropped entirely from the flattened text — is
    visible with all three strain columns. Table II confirms this item's own claim: its columns are
    `Compound | EC50 | MIC` with **no per-strain columns**, while its title names Guy11, AM25 and
    TF7-3131.
  - **Fact correction:** the paper has **three** tables, not two — `I` Phenotypic characterization,
    `II` Sensitivity, `III` *M. grisea* strains used in this study. Table III is the strains table in
    Methods.
  - **Two defects were caught by the process itself**, neither findable by unit tests: a shared
    regex fragment was duplicated into two modules with the word boundary in only one, manufacturing
    phantom tables from prose (`Table Legend is described…` → table `L`); and `__init__` did
    `config or defaults`, so a caller-supplied config *replaced* the defaults and the new
    `table_render_dpi` key broke the CLI and pipeline outright. Both fixed and re-reviewed.
- [ ] **Nothing marks a table's flattened text as unreliable** (built then **withdrawn**
  2026-07-26, curator decision). PDF text extraction loses a table's column grid, so its numbers
  arrive in the body as a flat run that reads like ordinary prose — which is how Table I's
  "Appressorium formation >95%" row went missing unnoticed. An in-body warning was built
  (`_mark_flattened_tables`) and then removed. **Two lessons are worth more than the code was:**
  - **It never fired in production, and three separate checks said it did.** The body generators
    append a whole page or section as *one* list element, and `CAPTION_BLOCK_RE.match()` only
    matches at position 0 — so a caption mid-page was never seen. The unit tests hand-fed a
    pre-split list with the caption as its own element; the wiring tests used synthetic pages
    containing *only* a caption; the end-to-end check did the same. All three put the caption at
    position 0 by construction, so each passed for the wrong reason. **A test that builds its input
    to match the implementation's assumption cannot falsify that assumption** — the whole-branch
    review found it by reading the call sites instead.
  - **Fixing it exposed why it was the wrong design.** Once firing, 2 of 3 markers on PMID:9927411
    pointed at the **wrong page** (`Table II` → `Table-p9.png`; it is on page 7), because the
    per-table page pointer resolves through the over-detected caption list below. A confident
    pointer to the wrong page is worse than no pointer. **The pointer was the overengineering:** it
    needed entry resolution, which needed correct detection, for something a generic sentence would
    have done. If revived, make it a generic warning with no filename or page.
- [ ] **Table captions are over-detected from in-text references** (added 2026-07-26; deferred by
  the curator the same day). `AdvancedCaptionExtractor`'s patterns match `Table N`
  **anywhere** in the text, so a sentence like *"Table I and Figure 6 show the results…"* is read as
  a caption. On PMID:9927411: 11 mentions → **10 "captions" → 5 rendered pages, where 3 real tables
  exist**. Two spurious PNGs per paper and inflated `table_captions_found` / `tables_rendered`
  counts, which undercuts the honest-reporting work above.
  - **Pre-existing, newly consequential.** The flaw predates the page-render work — it was
    previously a harmless miscount, and only became visible files once each caption triggered a
    render. It is *not* caused by widening the regex to Roman numerals.
  - **Nothing is broken by it:** all three real tables render correctly, so this is noise, not loss.
  - **The obvious fix does not work.** Anchoring to line-start cuts 10 to 4, but one survivor is a
    sentence that wrapped. Additionally requiring a `.` or `:` after the number gives exactly 3 here
    — but breaks `Table S1 Primers used in this study`, a real unpunctuated caption form with a
    passing test. **A missed table is invisible; a spurious one is obvious** — so do not trade this
    way round.
  - **If picked up:** line-start anchor, then dedupe by table number preferring a punctuated match
    (a paper has one Table I, whatever the layout). The deeper fix is to anchor captions to real
    text blocks the way the geometry path already does, rather than scanning free text.
- [x] **~~Ontologies are re-parsed on every test run~~ — misdiagnosed; the real cost was
  `git_commit()`** (added 2026-07-24, *measured and fixed 2026-07-25*). The slow gate was real; the
  cause was not ontology parsing.
  - **The premise was wrong.** This item assumed the `.obo` parse cost was paid "per test process,
    across 30 test modules". But **no test file spawns a subprocess** — `unittest discover` runs the
    whole suite in **one** process, where the existing `lru_cache(maxsize=1)` already parses each
    ontology exactly once. Measured cost of that one parse: `phipo-base.obo` = 61 ms read + 28 ms
    parse (1327 terms); `map_phenotype.load_terms` = 32 ms. **Total ontology parsing across all
    bundled files is ~0.2 s**, not "a large part" of the gate. A disk cache would have saved
    essentially nothing, and would have added an mtime-invalidation bug surface for free.
  - **The real hotspot, from `cProfile`:** `test_entry_queue` spent **7.49 s of its 8.17 s** in
    `render_entry_queue` → `provenance_line` → **`git_commit()` → `subprocess.run`**, 20 times at
    ~330 ms per call. Shelling out to git costs ~330 ms on the `z:` 9p mount, and every rendered
    entry queue asks for the commit once.
  - **Fix:** `@lru_cache(maxsize=1)` on `phiweaver.common.git_commit` — a process cannot
    meaningfully change commit underneath its own provenance stamp, and a `None` (git absent, or the
    5 s timeout tripped) is now paid once rather than per render. `git_commit.cache_clear()` covers
    the rare long-lived-process case. `tests/test_common.py` (7 tests) pins the call count, so
    removing the decorator fails the suite rather than silently costing 10 s again.
  - **Result: unit suite 22.1 s → ~11.6 s, full `smoke` gate 57.5 s → 34.0 s** (~41%), 8/8 green.
    The saving is larger than `test_entry_queue` alone because several other modules render
    provenance stamps too.
  - **Lesson:** profile before optimising a guess. This item named a plausible culprit (big files, a
    slow mount) and was written without measuring; the actual cost was 30× larger and elsewhere.
    *Still true and unfixed:* the 9p mount tax on per-file I/O is real — it just lands on process
    spawns and imports, not on ontology parsing.
- [ ] **PomGeneEx IDs are unverified, and the protein half is missing** (added 2026-07-24). The
  seven RNA-level qualifier IDs vendored in `5597729` (`data/pomgeneex.obo`) are **curator-supplied
  and were never checked against a published PomGeneEx release** — no public artifact could be
  found. The *phrases* have independent backing (PHI-Canto UI screenshot, 2026-07-11); the
  **ID↔phrase pairing does not**. **(a)** Confirm the pairing in Canto, then either point the file
  at an upstream copy or record here that none exists. **(b)** The parallel **protein**-level
  vocabulary (`PomGeneExProt`, behind `wt_protein_expression`) has **no IDs recorded at all**, so
  those annotations still carry a bare phrase — `entry_queue` accepts a blank `term_id` for both
  types on that basis, and that carve-out should narrow once the IDs exist.
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
  in `validate_ontology_ids`). **SUPERSEDED 2026-07-24:** the curator supplied the seven IDs, so the
  IDs ARE now carried — vendored as `phiweaver/lookup/data/pomgeneex.obo`, `PomGeneEx` registered in
  `validate_ontology_ids` (offline, like FYPO_EXT). IDs are curator-supplied and **not verified against
  a published PomGeneEx release**; see the provenance remarks in the `.obo`. The seven controlled qualifier phrases (PHI-Canto UI screenshot
  2026-07-11): RNA level increased, RNA level decreased, RNA level unchanged, RNA present, RNA
  absent, RNA level constant, RNA level fluctuates. **Surfaced to the drafting workflow (2026-07-16):**
  authoritative phrase table + per-phrase "use when" added to `Gene-for-Gene-Curation-Methodology.md`
  §9; a controlled-phrase step in the `phenotype-annotation` skill; and a QC flag in the `curation-qc`
  skill for free-prose RNA-level qualifiers. Motivating case: PMID:40756215 (Pt31812/Lr42), where the
  qRT-PCR "RNA level increased during infection" item was left as prose.
- [x] **Per-article token attribution** — *both follow-ups done 2026-07-11; box ticked 2026-07-25
  after verifying `article_tokens.py` is `benchmark` SKILL step 7 (`BATCH-TOKENS.md`) and `--db`
  defaults to `CANONICAL_DB`.* (tool landed 2026-07-11) — `phiweaver/article_tokens.py`
  attributes a batch session's token spend to each curated paper (PMID) + a shared-overhead split
  (equal 1/N, or `--weight-by-direct`), joining First-author/Year/Title from the tracking DB. Reads
  batch PMIDs from the draft `meta` blocks and segments turns by the per-paper draft references
  already in the transcript (no new marker discipline). Cache-read is counted wholly as shared
  overhead (session-cumulative, not attributable to one paper). Follow-ups: (1) ~~wire it into the
  batch skill~~ **done 2026-07-11** — `benchmark` SKILL step 7 emits `BATCH-TOKENS.md` for the
  session log; (2) ~~confirm the tracking-DB filename so `--db` auto-detects~~ **done 2026-07-11**
  — defaults to the canonical `11-CLAUDE-AI/db/phi_canto_tracking.db`.
- [x] **Persisted token history + recuration comparison** — *both follow-ups done 2026-07-11; box
  ticked 2026-07-25 after verifying the `article_token_costs` table + migration, `PRICES`,
  `--history`, the registry's "💰 Token Costs" section and `daily_curation tokens`.* Note the
  trailing "recuration comparison" in the title refers only to the DB shape this shares with the
  **Recuration-comparison workflow** item below — that item is separate and still open.
  (landed 2026-07-11) — `--record` writes
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
    `infective_ability reduced virulence` as text — decide with Hsin-Yu whether examples/drafts should
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

- [x] **PHI-Canto config wired in — follow-ups for James** — *rewired to the public repo
  2026-08-05* (added 2026-07-21). James Seager pointed us at `canto_deploy.yaml` in the private
  PHI-base/config repo (email 2026-07-21), which is PHI-Canto's own configuration. Read by
  **`phiweaver/lookup/canto_config.py`** (+ `tests/test_canto_config.py`, 16 tests): enabled
  annotation types, allele types, evidence codes, do-not-annotate subsets. **Weaver previously
  inferred all of this from gold-standard examples**, so a draft could name an annotation type
  PHI-Canto doesn't have and nothing caught it. Config = **two files merged** (public
  `canto_base.yaml` from pombase/canto + deploy overrides); provenance, source commits and
  refresh commands in `phiweaver/lookup/data/README.md`.
  - **① ✅ DONE 2026-08-05 — James Seager published the repo, and we rewired to it.** New public
    repo **`PHI-base/canto-config`** ("Configuration and other files for PHI-Canto") is a filtered
    copy of the private `PHI-base/config` with sensitive-file history stripped. The old private
    repo still exists for now but James will **rename it to `PHI-base/canto-config-private`** once
    the PHI-Canto server is switched over to `canto-config`, then **remove the migrated files from
    `PHI-base/config`** to kill the duplication (so don't treat `PHI-base/config` paths in older
    provenance notes as durable — re-check after the rename). He may also transfer relevant issues
    across. The private repo stays available for any future PHI-Canto file that genuinely needs to
    stay private. **Confirmed present** in `PHI-base/canto-config` at commit
    `3972a9be2aacbd0c0a7064d237e7efbd1c39bd52`: `canto_deploy.yaml` (byte-identical to our vendored
    copy) and `annotation_extension/{phipo_extensions.tsv, phibase_go_extensions.tsv,
    phido_extensions.tsv, phipo_extension_relations.obo}` — the latter two extension files had
    picked up a new `host_susceptibility` relation upstream since our 2026-07-15 hand-copy, now
    incorporated (see `Ontology-Terms-Reference.md`'s attested-relations table; its range term
    `PHIPO:0001456` is not yet in our vendored PHIPO release, same as the existing `PHIPO:0001456`
    caveat in `data/README.md`'s `phipo-base.obo` section).
    **Done:** un-gitignored `canto_deploy.yaml` and committed it; repointed every "Source" line in
    `phiweaver/lookup/data/README.md` at `PHI-base/canto-config` with the pinned commit and real
    `curl` recipes (resolves the sibling backlog item below, "Rewire the 4 hand-vendored extension
    configs…"); updated the now-stale "private"/"gitignored" language in `canto_config.py`,
    `extension_config.py`, `refresh_ontologies.py`, `entry_queue.py`, `test_canto_config.py`,
    `test_entry_queue.py`, `Ontology-Terms-Reference.md` and `docs/DESIGN-DECISIONS.md` (D18/D20);
    regenerated `docs/phiweaver-judge-handover.md`. Base-only fallback (`deploy_loaded = False`,
    the `test_canto_config`/`test_entry_queue` skips) no longer fires on a fresh clone or CI — kept
    as defensive behaviour only. Full suite green (619 tests).
  - **② Feed back one review note.** His clearance checks out independently (OAuth secret is only
    an env-var *name*, DB ref is a local SQLite path, all 4 emails are role accounts, GA/GTM id is
    public by construction — it's in the live site's page source). Worth telling him the reasoning
    for the GA id is stronger than "Copilot says so", and that the categories to re-check before a
    public move are the deploy-config ones — DSNs, SMTP creds, internal hostnames — not analytics.
  - **③ ❓ QUESTION for James / Hsin-Yu — is `qc_do_not_manually_annotate` missing from the
    config?** PHI-Canto's `ontology_namespace_config.do_not_annotate_subsets` lists **GO's**
    spellings — `gocheck_do_not_annotate`, `gocheck_do_not_manually_annotate` — plus
    `qc_do_not_annotate` and `canto_root_subset`. But **PHIPO's own** `qc_do_not_manually_annotate`
    is **not** listed, and **56 PHIPO terms carry it** (vs 67 for `qc_do_not_annotate`). PHI-Canto
    is a *manual* curation tool, so those 56 terms look like they should be excluded too.
    `map_phenotype` excludes them already (see ④); the question is whether PHI-Canto itself is
    letting them through — i.e. whether the config omission is an oversight or deliberate. Frame as
    a discussion, not a defect report: there may be a reason the GO spellings alone are enough (e.g.
    Canto normalises the prefixes internally), and that's worth knowing either way.
  - **④ ✅ DONE 2026-07-21 — `map_phenotype` honours the annotation-usage subsets.** It had been
    offering terms that exist, are non-obsolete, **and would still be rejected by PHI-Canto**.
    Worst case was the commonest phrase in PHI-base papers: *"reduced virulence"* returned
    `PHIPO:0000015` as a **primary** phenotype term when it is `qc_extension_only` and belongs in
    `infective_ability → PHIPO:0000015`. Now: extension-only terms are **kept and labelled** (hiding
    them would turn the most common phrases into false gaps); grouping terms are **withheld but
    still reported** under *"NOT a gap"* (silently dropping them turns a parent-only match into a
    bare `no_match`, which reads as an ontology gap and invites a duplicate term request — lessons
    L2/L8, phipo#452); `--include-grouping` promotes them for gap analysis, mirroring
    `--include-obsolete`. **Driven by PHIPO's own `subset:` tags, not by `canto_config`** — the
    PHI-Canto list lives in the gitignored deploy file, and a filter depending on a file present on
    one machine and absent on another would hand two curators different candidates for the same
    phrase. The committed ontology is identical everywhere. 6 new tests; suite 303 → 309.
  - *Related:* `extension_conf_files` names the 8 extension TSVs PHI-Canto actually loads,
    including the vendored `phipo_extensions.tsv` and `phido_extensions.tsv` — authoritative
    provenance for files previously taken on trust. May also bear on the open **PHIDO validation
    gap** item.

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

- [x] **PMC full text as an input format — parts (a) and (b) both DONE 2026-07-24.** *(The title
  read "part (a) still open" until 2026-07-25, contradicting its own body, which had recorded (a)
  as done since the day it shipped. That mismatch is what made the duplicate entry below look
  necessary — see the note at the end of this item.)*
  **(b) JATS → markdown converter** shipped as `phiweaver/jats/jats_convert.py` with
  `tests/test_jats_convert.py` (33 tests, offline). The pipeline now dispatches on file
  extension (`CONVERTERS` in `phiweaver/pipeline/curation_pipeline.py`): `.pdf` → the PyMuPDF
  converter, `.xml`/`.nxml`/`.jats` → the JATS converter, both writing the same
  `<stem>_converted.md` + `_converted_report.json`, so everything downstream is unchanged.
  New verb `process-paper`; `process-pdf` kept as an alias. Handles JATS tables, recursive
  section nesting, and back-matter display-object blocks (how MDPI ships figures).
  **The DOI→PMID/PMCID direction of the ID Converter is wired in** (a JATS file often carries a
  DOI and no PMID, and the toolchain keys on PMID); failure is a warning, never fatal.
  **Figures — resolved differently than expected.** There is no JATS counterpart to
  `pdf_convert.py`'s caption *extraction* because JATS already tags captions exactly. The real
  problem is the opposite one: JATS names image files it does not ship. The converter therefore
  audits every `<graphic>` href against disk and reports absent ones in the markdown, the
  frontmatter and the JSON — so a draft states "captions only" as a fact instead of a reader
  assuming the panels were seen.
  **Token cost — now measured, not ballpark** (PMID:39852455, 2333-line MDPI JATS,
  chars/4 approximation): raw XML **~31k tokens** → parsed markdown **~10.9k** (65% reduction),
  or **~7.7k** with `--no-references --no-index` (76%). The *parsed* estimate below was accurate;
  the *raw* estimate (80–150k) was high for an article this size. The direction of the argument
  holds.
  **(a) DONE 2026-07-24 too**, via **Europe PMC** rather than NCBI: `phiweaver/jats/europepmc.py`
  + `tests/test_europepmc.py` (31 tests, offline fixtures), and pipeline verb `from-pmid
  <PMID|PMCID|DOI>`. One Europe PMC call resolves any identifier *and* returns the access flags,
  so the NCBI ID Converter was dropped entirely — `jats_convert.resolve_ids_from_doi` now
  delegates here.
  **Correction to a common misconception:** there is **no separate "Europe PMC ID"** for journal
  articles — in a MEDLINE record the `id` field *is* the PMID. The key is the composite
  `source:id` (`MED:39852455`), which is what `article_ref()` builds.
  **The availability gate is `isOpenAccess`, not "a PMCID exists".** Verified: PMC206556
  (avrPto, 1992) has a PMCID and is viewable in Europe PMC, but `fullTextXML` returns **404** and
  `supplementaryFiles` returns **HTTP 200 with an `<errorBean>` body** — a status code alone will
  hand you an error message dressed as a zip. Both traps are absorbed by the client and tested.
  **Figures: solved.** Europe PMC's `supplementaryFiles` endpoint ships the article's **main
  figure images**, not just supplements — 14 images + the 1.17 MB supplement zip for
  PMID:39852455 — and the filenames match the `<graphic>` hrefs, so the JATS converter's
  stem-matching resolves `g001.tif` → `g001.jpg` and the captions-only warning disappears.
  Re-running PMID:39852455 through this route changed three annotations in the curation draft
  (one upgraded, one downgraded, one flagged), which is the concrete case for preferring it.
  **Deliberately NOT used as evidence: the Annotations API.** 378 text-mined entities are
  available for that paper, but sampling found "mice" → taxid 10095 (*Mus sp.*) instead of 10090,
  and "guanine nucleotide exchange factor" → UniProt P0CF32 (SDC25_YEASX, *S. cerevisiae*)
  instead of the article's own Q4WWM8 (SEC2_ASPFU). Exposed behind `--annotations` and documented
  as a **triage recall aid only**, never evidence, never straight into a `canto` block.
  **Caching DONE 2026-07-24.** `europepmc.ResponseCache` — an on-disk blob cache keyed by URL,
  with `--cache` / `--no-cache` / `EPMC_CACHE` mirroring `query_uniprot`'s conventions. It is
  deliberately **not** `phiweaver.common.ResponseCache`: that stores JSON in SQLite, and these
  payloads are full text XML and a 1.9 MB figure ZIP per article. Each entry is a `.bin` blob
  plus an inspectable `.json` sidecar (url, status, content type, bytes, fetched-at).
  **Only HTTP 200s with a body are stored.** A 404 is deliberately *not* cached: Europe PMC
  returns one for an embargoed article, embargoes lift, and a remembered 404 would permanently
  hide a paper that has since become open access. Measured on PMID:39852455: 1.93 s cold →
  0.50 s warm, and the 1.9 MB ZIP stops being re-fetched on every run.
  **Two residual questions were promoted out of this closed item on 2026-07-25** — preprint policy
  and the author-manuscript check — because open work buried inside an `[x]` entry is invisible to
  anyone scanning the checkboxes. See "**Europe PMC ingest: preprint policy + author-manuscript
  check**" below.

  *Why this item had a duplicate:* on 2026-07-25 a second entry was opened and closed for the same
  work, because the stale title above said (a) was outstanding. The duplicate has been removed and
  its one distinct observation folded in here: both halves shipped in `ebd73af` on 2026-07-24,
  three days after the original note was written, and no box was ticked — so the entry stayed open
  and misdescribed the code for a month.

  *Original rationale, for the record:* the only ingest route was PDF
  (`phiweaver/pdf/pdf_convert.py`, PyMuPDF). For open-access papers — most of what PHI-base
  curates — PMC's JATS XML is a strictly better input: sections, tables and references are already
  tagged, so gene symbols, strain IDs and table structure survive instead of being reconstructed
  from page layout. *(The original note's ballpark token estimates and "figures are the open
  question" caveat are superseded by the measured numbers and "Figures: solved" above.)*

  **Timing note:** the PMID→PMC gap is set by the journal's access model, not by PMC processing.
  Fully-OA journals deposit at publication (full text within ~2 weeks); paywalled ones are 6–12
  months or never. So recent OA papers usually *are* in PMC — don't assume otherwise.
  **See:** `docs/FAQ.md` ("Should I curate from PDF or EPUB?").

- [ ] **Europe PMC ingest: preprint policy + author-manuscript check** (promoted 2026-07-25 out of
  the closed PMC-ingest item above, where it was invisible). Two residual questions from the
  Europe PMC route:
  - **`source=PPR` preprints** — currently *flagged as a scope question*, never silently ingested.
    Needs a policy decision: does PHI-base curate from preprints at all, and if so under what
    caveat? (Curator call, not a code change.)
  - **Author manuscript vs version of record** — for some deposits PMC holds the *accepted
    manuscript*, not the published version, so figure/table numbering and wording can differ from
    what a curator cites. Whether Europe PMC exposes a clean flag for this is **unverified**; find
    out before trusting the route on non-fully-OA deposits.

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
- [ ] **`status: validated` may overstate curator sign-off on the example library** (added
  2026-08-02). `PMID39787257-FgKnr4-cell-wall-stress.md` carries `status: validated`,
  `reviewed_by: Hsin-Yu Chang`, `reviewed_date: 2026-07-04` and a header calling it a "Validated
  gold-standard curation"; `Curation-Examples-INDEX.md` shows ✅ validated. **The curator states they
  did not approve it.** Two readings, and the fix differs: (a) the underlying PHI-Canto session
  *was* curated by Hsin-Yu but the **example file / its use as a gold standard** was never signed
  off — then `reviewed_by` is the overclaim and the frontmatter needs a weaker status; or (b) the
  session itself was never approved — then the example should not be `validated` at all. **Resolve
  with the curator before editing the frontmatter** — this is a provenance record, not a
  cosmetic field. **Why it matters beyond one file:** examples are retrieved as references during
  drafting and five of them ship in `docs/phiweaver-judge-handover.md`, so a false approval claim
  propagates into both drafting and judging. **It is systematic, and the mechanism is a conflated
  field:** `skills/gold-standard-import/SKILL.md:49` defines `reviewed_by` as *"the PHI-Canto
  curator"* — i.e. whoever curated the **session**, which is not the same act as reviewing the
  **example**. All five examples carry `status: validated` (three naming Hsin-Yu Chang, one
  "Hsin-Yu Chang; Martin Urban", one "Melina Velasquez; Alayne Cuzick"), so any of them may assert a
  sign-off that never happened. The skill's own rules are right and are being undercut by the field
  name: `:65` says `validated` is "only for a genuinely curator-reviewed curation" and `:71` says to
  import as `status: draft` and flip only after review. **Likely fix:** split the field — `curated_by`
  (session curator, factual, safe to auto-fill) vs `reviewed_by` (example sign-off, set only when it
  happened) — and re-derive each example's real status. Surfaced while filing `phi-weaver#9`.
- [ ] **Genotypes have no explicit `strain` — the name is doing two jobs** (added 2026-07-25, found
  while aligning the entry queue to PHI-Canto's UI). PHI-Canto requires **one or more "experimental
  strains" for every organism** in a session *before* any genotype can be created
  (`docs/getting_started#adding_strains`), and its "strain" is broad — subspecies, varieties,
  pathovars, **cultivars**, and strains proper. Its genotype tables carry **`Strain`** and
  **`Background`** columns. The draft schema has neither field, and the genotype `name` is currently
  carrying the strain: on PMID:9927411 the pathogen genotypes are `Guy11` / `AM25` / `TF7-3131` /
  `AM30` (strain names), and the hosts are `WT Oryza sativa Sariceltic` / `WT Hordeum vulgare Golden
  Promise` (organism + cultivar folded into one string).
  - **Interim (done 2026-07-25):** the queue's **table A2** lists one row per organism with its
    pathogen/host role (derived from metagenotype use, not the species name) and prompts the curator
    to set the strain in Canto — **nothing is pre-filled**, because splitting a strain out of those
    names would be guessing at curated data. The draft's genotype names are shown alongside so the
    curator can recognise it. See **D19**.
  - **① ✅ RULED 2026-07-25 (Martin Urban): only a wild type carries a strain or cultivar; a mutant
    carries none and is named by its allele.** `Guy11` = strain, genotype wild type; `AM25` = the
    `abc1Δ` genotype; `TF7-3131` = the `abc1-1` genotype; rice `Sariceltic` = cultivar, genotype wild
    type. Written up in `07-Standards/PHI-Canto-Curation-Conventions.md` ("Strains and cultivars —
    wild type only") and applied in the renderer: **A2 excludes allele-bearing genotypes entirely**,
    and uses a genotype's optional `strain` verbatim when present.
  - **② ✅ Schema + drafting done 2026-07-26; backfilling the nine drafts is what remains.**
    `strain` and `background` are now **in the draft schema** (`_TEMPLATE.md` — the genotypes bullet
    documents the ruling, the JSON skeleton carries both keys) and the **drafting workflow writes
    them** (`skills/genotype-creation/SKILL.md`: workflow step 6, a "Strain and background" section,
    an output and a QC check). The same file's `#157` background vocabulary still said
    `<gene>delta`, superseded by `<gene>modified` on 2026-07-25 — fixed in passing.
    **A lint makes the omissions visible:** `coverage.strain_background_warnings` flags a wild type
    with no `strain`, a mutant with no `background`, a mutant carrying a `strain` (the isolate-label
    error the ruling exists to prevent) and any genotype setting both; it rides the entry-queue
    CLI's existing stderr channel, so it fires on every generation. 8 tests (suite 14 in that
    module); `python3 -m phiweaver.smoke` 8/8.
    - **Validated against curated data:** PMID:9927411 — the reference draft — lints **clean**,
      and the other nine flag **50 gaps** between them.
    - **Not backfilled, deliberately.** Filling those 50 means reading each paper for the parent
      strain; deriving them from genotype names (`wild type PH-1` → strain `PH-1`) is the guess D19
      already refused. The lint names each gap so a drafting pass can close it per paper.
    - **⑧ ✅ RULED 2026-07-26 (Martin Urban): a near-isogenic line's parent cultivar is a
      `background`.** Found by running the lint — host NILs carrying a *natural* allele
      (`tomato 76R (Pto/Pto)` / `76S (pto/pto)`, PMID:1537802) trip the mutant test, and the
      question was whether a natural allele should leave them a `strain` instead. It does not: a
      NIL is defined by its allele, so it follows the mutant rule and the lint's existing behaviour
      was already right — **no code change**. Written up in `PHI-Canto-Curation-Conventions.md`.
      *Corollary:* `wheat Lr42-NIL` (PMC12313645) records **no allele**, so it lints as a wild type
      — the `AM30` shape again, and its `Lr42` allele is the paper's entire subject.
  - **③ ✅ RULED 2026-07-25: a mutant's parent strain goes in `Background`.** `Guy11` is the
    background of every mutant derived from it, never their strain — the two fields are
    complementary and never both set. **AM30 is an insertion mutant in wild-type Guy11**, not a
    wild type, which confirms "has alleles" alone cannot decide: a `background` is the second
    signal, and A2 now excludes on either. Genotype tables carry Canto's `Strain` and `Background`
    columns, and a genotype with a background but no allele renders `⚠ no allele recorded` — that
    is a mutant whose allele the draft failed to capture, exactly AM30's case.
  - **④ ✅ RESOLVED 2026-07-25: `Background` is one field carrying both facts** — the parent strain
    *and* the endogenous copy's status from `#157`. `AM30` is now written into the draft as
    `Guy11; endogenous ABC1 present`. The `#157` vocabulary's third form was updated the same day
    from `<gene>delta` to **`<gene>modified`**, so an insertion mutant like `TF7-3131` has a form
    that fits it. Both recorded in `PHI-Canto-Curation-Conventions.md`.
  - **⑤ ✅ PMID:9927411 fully populated 2026-07-25.** Mutants carry a background (`AM25` =
    `Guy11; endogenous ABC1 absent`, `TF7-3131` = `Guy11; ABC1modified`, `AM30` =
    `Guy11; endogenous ABC1 present`) and the four wild types carry a strain/cultivar (`Guy11`,
    `Sariceltic`, `CO-39`, `Golden Promise`), so A2 pre-fills for all three organisms. The allele
    `abc1-2delta` was also respelled **`abc1-2Δ`** (12 occurrences) per the Δ-suffix convention.
    Queue + docx regenerated. This is the reference draft for the strain/background shape.
  - **⑥ ✅ DONE 2026-07-26 — genotypes renamed, and the rule is now enforced.** PMID:9927411's
    `AM25` → **`abc1-2Δ`** and `TF7-3131` → **`abc1-1`**, cascading through **22 structural
    references** (genotype `name`, metagenotype `name` + `pathogen_genotype`, annotation `feature`).
    Queue + docx regenerated; the draft lints clean.
    - **Free text deliberately keeps the paper's labels.** `conditions` and `hold_reason` quote
      Table I's own rows ("Guy11 32 ± 10, AM25 70 ± 19"), so renaming them would break the tie to
      the paper. Only structural fields moved. No `compared_to_control` value referenced either
      genotype, so no comparator broke.
    - **The rename would have cost the curator the paper.** Figures and tables say `AM25`; a queue
      row saying only `abc1-2Δ` cannot be reconciled with Table I. New optional genotype field
      **`paper_label`** records the isolate label and the queue prints it beside the name
      (`abc1-2Δ *(paper: AM25)*`). In `_TEMPLATE.md`; 2 tests.
    - **`genotype_naming_warnings`** flags a mutant naming none of its alleles — the deterministic
      form of the ruling. Matches on the allele's stem *or* its full form, so strain-prefixed
      (`Pta6605 ΔfleQ`), complementation (`SdhC1Δ-C` ← `SdhC1(ectopic)`) and multi-allele names all
      pass; flagged only when **no** allele matches, so an accidental short-stem match yields a
      miss rather than a false accusation. Across 14 drafts / ~50 mutant genotypes it raises
      **3 flags**: the two renamed here, plus one below. 9 tests. Drafting rule added to
      `genotype-creation` — get the name right at creation, since it is a foreign key.
    - **Found by the lint, left open:** `Pta7375 WT` (PMID:41229162) is named as a wild type but
      carries alleles `fleQ7375, gcbB7375` — a wild-type strain of a *second* isolate modelled as
      an allele-bearing genotype. Not a naming slip but a modelling question; needs the curator.
  - **⑦ `AM30` has a background but no allele** — the queue renders `⚠ no allele recorded`. Its
    ectopic vector integration is a real allele that the draft never captured; `#157` points at
    allele type `ectopic expression` for random/plasmid integration.
  - *Worth knowing:* the concept is **first-class in PHI-base already** — the v4-19 release carries
    `Experimental_strain` (`Guy11`) and `Pathogen_NCBI_strain_Taxonomy_ID`, both surfaced by
    `phibase_index`. So the target shape exists; only weaver's draft schema is missing it.
- [x] **Nothing checks whether a paper is already curated in PHI-base** — *resolved 2026-07-25*
  (added 2026-07-24, surfaced on PMID:9927411). Built **`phiweaver/lookup/phibase_index.py`**
  (+ `tests/test_phibase_index.py`, 20 tests, network-free): `python3 -m
  phiweaver.lookup.phibase_index <PMID>` indexes a pinned PHI-base release by PMID and reports a
  hit with the record's PHI accession, gene, pathogen taxon, host, phenotype and a verified
  record link, or an explicit miss. Wired in as **step 1 of `paper-triage`**, before conversion,
  so the answer lands before the drafting effort. Confirmed on the trigger paper: PMID:9927411 =
  **PHI:132** (ABC1, O13407), pathogen **taxid 318829** — the taxon the draft got wrong.
  - **Source:** `releases/` in <https://github.com/PHI-base/data> (CC-BY-4.0), pinned to
    `phi-base_v4-19_2026-03-25.csv` (24,122 records / **5,994 distinct PMIDs**); `--release`
    takes any release filename, `phi-base_current.csv` tracks the newest. Cached under
    `phiweaver/lookup/.cache/phibase/` (gitignored, ~17 MB); `PHIBASE_CACHE` relocates it —
    worth pointing at a native filesystem, since reading it costs ~3 s on the `z:` 9p mount.
  - **Two undocumented release quirks handled** (both pinned by tests): the CSV repeats its
    **header as the first data row**, and the PMID column was **renamed** (`PMID` → v4-08,
    `Literature_ID` since) — both spellings are accepted.
  - **Recall ceiling, printed with every miss:** releases exclude in-progress PHI-Canto
    sessions, and 61 records in v4-19 cite no PubMed ID, so a miss is never reported as
    "uncurated". *Deferred:* auto-diffing a draft's `canto` block against the matched record —
    the fields are surfaced for a curator to reconcile, but nothing compares them automatically.
  - **Why it mattered** (the original note): weaver drafted a foundational 1999 rice-blast paper
    end to end without ever asking whether PHI-base already holds it — and for a paper of that
    vintage and prominence it very likely does. A duplicate draft wastes the curator's review
    time, and worse, it can **silently disagree with the established entry** on exactly the
    judgement calls a draft is weakest on (there, the taxon — UniProtKB:O13407 is filed under
    *Pyricularia grisea* taxid 148305 while the experimental strain Guy11 is a rice isolate, now
    *P. oryzae* taxid 318829 — and the allele type for an ORF-replacement mutant). An existing
    curated entry should win over a fresh draft. Cheapest useful version: a lookup by PMID
    against PHI-base at **triage** time, so the answer arrives before the drafting effort is
    spent, not after; surface a hit as a flag with a link rather than refusing to draft.
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
- [ ] **Confirm open clarifications from Hsin-Yu's 2026-07-15 review** (applied with sensible
  defaults; fold her answers into `07-Standards/PHI-Canto-Curation-Conventions.md`): (D1) canonical
  **gene-symbol source** — UniProtKB gene name vs. "strip the species prefix" (drafted as
  strip-prefix, e.g. `SdhA`); (D2) is there a **full allele/genotype naming standard** beyond the
  deletion Δ-suffix; (D3) does **"Figure in full"** extend to other abbreviations (e.g. "Table");
  (D4) **filenames** keep the PMID/`FpSdh` basename (kept — cosmetic, renaming would orphan the
  queue/docx). Also the GO-no-biochem-evidence question (`CURATION-LESSONS.md` L3) is still open
  with her.
- [ ] **How much term *design* should a request carry?** (raised 2026-07-17; for Hsin-Yu) — the
  `ontology-term-request` skill's line is **"evidence, not design"**: never propose a term's parent,
  definition or hierarchy placement, on the principle that this project does not assert in-silico
  conclusions as fact (the same reasoning behind the ISS rejection). **But PHIPO's own
  `CONTRIBUTING.md` asks requesters to suggest "label (name), definition, references, position in
  hierarchy"** — so our guardrail is *stricter than the ontology team's house rule*, and was drawn
  against a constraint they do not actually impose. James has since asked for AI-drafted **PRs**
  (not issues) for the narrow pattern-extension case, and PR #454 duly proposed a label, definition
  and parent — all three of the things the skill forbids. The skill now scopes the prohibition to
  non-pattern-extension requests and records this as open. **Ask Hsin-Yu where the line should sit**,
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
  see `docs/LLM-AS-JUDGE-DESIGN.md`). Idea: use a *different* model
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
  No write API exists; session import is `canto_add.pl --sessions-from-json`, server-side only, and
  it carries **genes/alleles/genotypes only** — not metagenotypes or annotations (`canto_load.pl`,
  named here until 2026-07-25, loads reference data and cannot create sessions). Three routes
  assessed (assisted-entry queue / Canto import JSON + `canto_add.pl` / browser automation) with
  recommendation and open questions in **`docs/CANTO-SUBMISSION-ROUTES.md`**. Route 1 (assisted-entry queue) is built — a structured
  `canto` block in the draft + a deterministic `entry_queue.py` (the single Route-1 output; the
  earlier `worksheet.py` was retired, D16). Scope notes in **`docs/CANTO-ROUTE1-BUILD-SPEC.md`** —
  biocurator entry into PHI-Canto *is* the validation step.

  **Decision, 2026-07-25 — browser automation is rejected; do not re-litigate without new numbers.**
  Recorded as **D18** in `docs/DESIGN-DECISIONS.md`, which is the decision of record; this entry is
  the working summary.
  The end state is **Route 1 permanently + Route 2 for the scaffold if admin access exists**. Route 1
  is not an interim MVP: because the import format stops at genotypes, annotations are hand-entered
  for good. The only open input is server/admin access to canto.phi-base.org, and it now decides
  *how much* the curator clicks, not whether the approach works.

  **Why Route 3 is rejected — arithmetic, not principle.** A fluent curator spends ~1 min per
  annotation, so ~30–40 min of mechanical entry per paper; prefill might halve it (~15–20 min saved)
  against **60–100 h** to build (ontology-autocomplete handling with ID read-back, DOM re-derivation,
  provenance display, a local Canto instance). **Break-even ≈ 150–250 papers.**

  **The stronger reason: typing is not the bottleneck.** The live blockers are accession resolution
  (URA5, FleQ/GcbB), hand-scoring, PHIPO gaps and evidence-code rulings — all research or judgement.
  Route 3 would optimise the cheapest link. The entry queue already took most of the available win by
  removing the *"what do I enter next"* thinking; Route 3 competes only for the residual keystrokes.

  **What was actually considered, so it isn't reinvented worse.** The strongest form of Route 3 is
  *not* an autonomous bot — it is **supervised one-step prefill**: the curator drives, Playwright
  fills one wizard screen, the curator clicks every Next and the final Finish, and the bot never
  commits. That shape survives the brittleness objection (a broken selector degrades to typing) and
  preserves the "entry *is* validation" model. It was rejected on economics alone. Two further
  hazards found while designing it, which any revival must answer:
  - **Bind the term ID, not the label.** Canto's ontology fields are server-backed autocompletes; a
    fill must select from the dropdown and then **verify the bound ID**, or it silently produces a
    plausible sibling term — worse than no tool.
  - **Automation complacency degrades provenance.** After ~30 correct fills a reviewer rubber-stamps,
    and a machine error ships with a human's approval attached — laundered as a curator decision.
    Mitigation: never auto-fill anything the draft flagged uncertain; leave it blank and highlighted.

  **What would reverse this:** recurring throughput in the hundreds of papers, or a measured baseline
  showing mechanical entry is a much larger share of curator time than ~30–40 min/paper. Measure
  those two numbers before rebuilding anything. **See:** `docs/FAQ.md` ("How do phiweaver drafts get
  into PHI-Canto…").

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
- [ ] **Does the WT control metagenotype get its own phenotype annotation?** — filed 2026-08-02 as
  [PHI-base/phi-weaver#9](https://github.com/PHI-base/phi-weaver/issues/9), for Hsin-Yu Chang. The
  convention is settled that WT controls **are** made for metagenotype annotations (one per
  phenotype, linked via `compared to control` — PHI-base/curation `#78`, `#79`). What is open is
  whether the control is *itself* annotated. The filed issue cites
  `07-Standards/PHI-Canto-Framework-Cuzick2023.md:135` — "Wild-type control phenotypes — new
  `compared to control` AE **+ WT metagenotypes**" — and asks whether the WT metagenotype is
  annotated, and if so with the same measured term at WT level or a distinct normal/unaffected term.
  Tagged `#affecting-weaver-drafts` (body text, not a repo label).
  **Deliberately not cited in the issue:** `PMID39787257-FgKnr4-cell-wall-stress.md:70-71` carries no
  WT row (the control appears only as the extension value `compared_to_control *FgKnr4+*[WT level]`),
  which looks like a counter-example — but **the curator has not approved that example**, so it is not
  evidence about what PHI-Canto expects and was correctly left out. See the provenance discrepancy
  logged under "Curation workflow" (the file's `status: validated` / `reviewed_by: Hsin-Yu Chang`
  frontmatter overstates its actual sign-off). Once #9 is answered, use the answer to correct the
  example if needed — not the example to second-guess the answer.
  **Blocks:** the drafting fix below — weaver currently links a control *where one exists* rather than
  creating one, and the answer decides what "create" means. Log as a typed `issue` row in
  `CURATION-LESSONS.md` once answered (the route L3 took via `phi-weaver#8`).
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
- [x] **Rewire the 4 hand-vendored extension configs to a public source** — *done 2026-08-05*
  (added 2026-07-15; deferred 2026-07-16; unblocked and resolved 2026-08-05, together with ①
  in "PHI-Canto config wired in — follow-ups for James" above). `phiweaver/lookup/data/
  {phipo_extensions.tsv, phibase_go_extensions.tsv, phido_extensions.tsv,
  phipo_extension_relations.obo}` had been **copied in by hand** from the private PHI-base/config
  repo (`config/annotation_extension/`) — no `curl`-able source, unlike the public `phido.obo` /
  `phi-eco.obo`. James Seager published `config/annotation_extension/` (and `canto_deploy.yaml`)
  in the new public **`PHI-base/canto-config`** repo (2026-08-05). Verified present at commit
  `3972a9be2aacbd0c0a7064d237e7efbd1c39bd52`; `phibase_go_extensions.tsv`/`phido_extensions.tsv`
  were byte-identical to our 2026-07-15 copies, `phipo_extensions.tsv`/`phipo_extension_relations
  .obo` had gained a `host_susceptibility` relation upstream (now incorporated). Refresh
  instructions in `data/README.md` now point at `raw.githubusercontent.com/PHI-base/canto-config`
  with real `curl` recipes, and the "copied by hand" provenance is gone. `refresh_ontologies.py`
  still lists these four as `UNSOURCED` — not because they're unavailable, but because they're
  TSV/`[Typedef]`-shaped, not the `[Term]`-block OBO this tool's plausibility check understands;
  its reason text now says so instead of citing a private repo. James intends to later delete the
  duplicated files from `PHI-base/config` and rename that repo to `PHI-base/canto-config-private`
  — re-verify the source URLs still resolve after that happens.
