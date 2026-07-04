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
  benchmarking compare like-for-like.
- [ ] **Physical-interaction scope** — decide whether/how PHI-Canto captures protein–protein
  interactions before treating it as a scored/example topic (recurs: Zhang-2024, Miltenburg-2022).
- [ ] **Add more validated gold-standard examples** — coverage target is **all 12 PHI-Canto
  annotation types** (the `annotation_types` vocabulary in `TAGS.md`). Live tracker: the
  "Coverage — PHI-Canto annotation types" table in `curation-examples/INDEX.md` (auto-generated).
  Currently **6/12** (the one PMID:26177154 example). Gaps, by PHI-Canto prevalence:
  `pathogen_phenotype` (281), `physical_interaction` (99), `wt_rna_expression` (95),
  `host_phenotype` (17), `post_translational_modification` (14), `wt_protein_expression` (4).
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
