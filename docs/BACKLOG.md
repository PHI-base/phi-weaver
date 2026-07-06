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

## Curation workflow
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

- [ ] **Submit drafts into PHI-Canto for biocurator review** (planning; no code yet) — get the
  information from phiweaver drafts into the PHI-Canto web tool (<https://canto.phi-base.org/>).
  No write API exists; `canto_load.pl` is server-side only. Three routes assessed (assisted-entry
  worksheet / Canto session JSON + load / browser automation) with recommendation and open
  questions in **`docs/CANTO-SUBMISSION-ROUTES.md`**. Pivotal decision pending: server/admin access
  to canto.phi-base.org vs web login only.

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
