# PHI-Weaver Backlog

Durable to-do / known-gaps list. (The harness's in-session task tools don't persist across
sessions, so **this file is the record** — add items as they come up; tick `[x]` or delete when
done.) Larger design items live in `DESIGN-DECISIONS.md` (D11 deferred) and
`PLUGIN-ARCHITECTURE.md`.

## Tooling / bugs
- [x] **PHIDO validation gap** (fixed 2026-07-04) — OLS4 does not host PHIDO, so every PHIDO ID
  used to return `not_found` (a false negative). Fixed by vendoring the ontology
  (`phiweaver/lookup/data/phido.obo`, from github.com/PHI-base/phido) and resolving PHIDO
  **offline** against it — existence + obsolescence, no network. GO/PHIPO still use OLS.
  Refresh instructions: `phiweaver/lookup/data/README.md`. Surfaced 2026-07-03 curating
  PMID:26177154 (PHIDO:0000164 Fusarium wilt), which now validates 7/7.
- [ ] **PomGeneEx (RNA-level) vocabulary + validation gap** (surfaced 2026-07-11) — weaver knows
  the `wt_rna_expression` annotation type and the phrase "RNA level increased" (one gold-standard
  example, PINE1/PMID:35468894; RT-qPCR/RNA-seq guidance in the methodology docs), but does **not**
  know the PomGeneEx term **IDs** or the full controlled set, and `validate_ontology_ids` cannot
  validate PomGeneEx (supports PHIPO/GO/PHIDO/MOD/UniProtKB only). Repo grep: `PomGeneEx` = 0 hits;
  the six non-"increased" qualifiers (decreased / unchanged / present / absent / constant /
  fluctuates) = 0 hits. The seven RNA-level qualifiers, from the PHI-Canto UI (curator screenshot,
  2026-07-11): RNA level increased **PomGeneEx:0000011**, decreased **:0000012**, unchanged
  **:0000013**, RNA present **:0000014**, RNA absent **:0000015**, RNA level constant **:0000016**,
  RNA level fluctuates **:0000017**. Plan (mirror the PHIDO fix — PomGeneEx is PomBase-local, not on
  OLS4): **vendor the PomGeneEx ontology offline** under `phiweaver/lookup/data/` and teach
  `validate_ontology_ids` the `PomGeneEx` prefix (offline existence/obsolescence), plus surface the
  7-term vocabulary to the drafting/entry-queue workflow so RNA-level items get the right qualifier +
  ID, not just prose. **NEEDS: the link to the PomBase GitHub repository file** that is the
  authoritative PomGeneEx source (analogous to github.com/PHI-base/phido for PHIDO) — obtain and
  record it before vendoring; do not hand-transcribe/invent IDs beyond the seven above. Surfaced
  curating PMID:40756215 (Pt31812/Lr42), where the qRT-PCR "RNA level increased during infection"
  item was left as prose, not annotated with the qualifier/ID.
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

- [ ] **`query_uniprot --locus-tag` misses strain-proteome loci** (surfaced 2026-07-14) — for a gene
  named only by an NCBI locus tag, the tool queries the **species** taxon and returns `not_found` when
  the entry lives under a **strain** reference-proteome taxon. Curating PMID:42089373 (5 *F.
  pseudograminearum* Sdh subunits), `--locus-tag FPSE_04172 --organism 101028` (species) → `not_found`
  for all five; a direct UniProtKB REST query resolved them under **strain CS3096, taxon 1028729**
  (K3UT42/K3VJU5/K3UP39/K3VHW6/K3VVK3). Worked around by hand. Fix options: when the species-taxon
  locus-tag search is empty, **retry across child/strain taxa** (or drop the organism filter and match
  the locus tag in the returned entries), and flag the strain mismatch (expt isolate vs reference
  proteome) rather than reporting a false `not_found`. Recurring accession-resolution weakness (also
  noted in the 2026-07-05 benchmark run).

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

## Ontology coverage gaps (PHIPO term requests)
_Curatable phenotypes seen in papers that have **no** PHIPO term — captured and flagged in the draft,
not forced onto a wrong ID. Candidates to raise with the PHIPO/PHI-base ontology team._
- [x] **Mycotoxin / DON production — terms exist** (corrected 2026-07-15). Earlier logged as a gap;
  **wrong** — PHIPO already has free-living DON phenotype terms: **PHIPO:0001445** decreased level of
  deoxynivalenol, **PHIPO:0001447** increased, **PHIPO:0001443** abnormal deoxynivalenol biosynthesis,
  **PHIPO:0001441** abnormal mycotoxin biosynthesis, **PHIPO:0001182** normal level (+ within-host
  variants PHIPO:0000219/232/233/234). The earlier `map_phenotype` phrasings ("decreased deoxynivalenol
  **production**") just didn't match the ontology wording ("decreased **level of** deoxynivalenol").
  PMID:42089373 reduced DON now maps to PHIPO:0001445. **Lesson for phiweaver:** when a phenotype
  phrase returns `no_match`, retry with the "level of" / "abnormal X biosynthesis" phrasings before
  declaring a gap. Two genuine *residual* items below.
- [ ] **No free-living "absent / abolished DON" term** — for a plate/flask assay with *no detectable*
  DON (ΔFpSdhA/B/D + ΔFpSdhC1&2, PMID:42089373 Table S4) there is only PHIPO:0001445 "decreased" (used
  as closest) and the *within-host* PHIPO:0000234 "pathogen deoxynivalenol within host absent" — no
  free-living "absent" phenotype. Minor term request.
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
- [ ] **Complete loss of conidiation (free-living)** — only PHIPO:0000052 "decreased number of asexual
  spores" and *within-host* absence terms (e.g. PHIPO:0000468) exist; there is no free-living
  "absence/abolished asexual sporulation" phenotype term, so total conidiation loss (ΔFpSdhA/B/D +
  double, PMID:42089373; "completely lost conidiation", PMID:41020836) is under-described.

## Curation workflow
- [ ] **Confirm open clarifications from Hsin-Yun's 2026-07-15 review** (applied with sensible
  defaults; fold her answers into `07-Standards/PHI-Canto-Curation-Conventions.md`): (D1) canonical
  **gene-symbol source** — UniProtKB gene name vs. "strip the species prefix" (drafted as
  strip-prefix, e.g. `SdhA`); (D2) is there a **full allele/genotype naming standard** beyond the
  deletion Δ-suffix; (D3) does **"Figure in full"** extend to other abbreviations (e.g. "Table");
  (D4) **filenames** keep the PMID/`FpSdh` basename (kept — cosmetic, renaming would orphan the
  queue/docx). Also the GO-no-biochem-evidence question (`CURATION-LESSONS.md` L3) is still open
  with her.
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
  `TAGS.md`). Live tracker: the auto-generated "Coverage" table in `curation-examples/INDEX.md`
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
  UniProt + EBI OLS only, `failIfUnavailable: true`. Remaining: **install `bubblewrap`** (not on
  the box yet) and **test it once** (tools reachable, a PHI-base fetch blocked), then use
  `claude --settings …benchmark-sandbox.settings.json` for scored runs. This is the only route that
  also covers PHI-base's **GitHub data repos** (`github.com/PHI-base`, `raw.githubusercontent.com`),
  which can't be cleanly domain-denied. The local `.claude/settings.json` WebFetch deny on
  `*.phi-base.org` is the interim (website-only) control.

- [ ] **Automatic per-paper token logging**: `benchmark_report` can display curation tokens, but
  phiweaver does not measure them — they are supplied by hand in the `tokens` CSV column. Add a
  small logging step during drafting that records each paper's LLM token usage (from the CLI/API
  usage readout) into the scores (or the scorecard), so tokens flow into the report automatically.

## Deferred (see DESIGN-DECISIONS.md D11 / PLUGIN-ARCHITECTURE.md)
- [ ] Full machine-readable curation-record schema (first slice done: the draft `auto_check` block).
- [ ] Plug-in host + local AI on ROGER (long-term; needs collaborator / research-computing help).
- [ ] Optional: UniProt mapping for Zhang-2024 from its genome IDs; read Zhang supplementary S1–S7.
