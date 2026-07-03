# PHI-Weaver Backlog

Durable to-do / known-gaps list. (The harness's in-session task tools don't persist across
sessions, so **this file is the record** — add items as they come up; tick `[x]` or delete when
done.) Larger design items live in `DESIGN-DECISIONS.md` (D11 deferred) and
`PLUGIN-ARCHITECTURE.md`.

## Tooling / bugs
- [ ] **PHIDO validation gap** — `validate_ontology_ids` lists PHIDO as supported, but EBI OLS4
  does not host PHIDO, so every PHIDO ID returns `not_found` (a false negative). Fix: either
  resolve PHIDO from another source, or mark PHIDO as *format-checked-only* (like UniProtKB) so it
  isn't wrongly failed. Surfaced 2026-07-03 curating PMID:26177154 (PHIDO:0000164 Fusarium wilt).

## Curation workflow
- [ ] **Format convergence** — phiweaver *drafts* use the example-template body shape while *gold
  standards* use PHI-Canto's structure; converge them (toward PHI-Canto) so retrieval and
  benchmarking compare like-for-like.
- [ ] **Physical-interaction scope** — decide whether/how PHI-Canto captures protein–protein
  interactions before treating it as a scored/example topic (recurs: Zhang-2024, Miltenburg-2022).
- [ ] Add more validated gold-standard examples as they are exported from PHI-Canto.

## Deferred (see DESIGN-DECISIONS.md D11 / PLUGIN-ARCHITECTURE.md)
- [ ] Full machine-readable curation-record schema (first slice done: the draft `auto_check` block).
- [ ] Plug-in host + local AI on ROGER (long-term; needs collaborator / research-computing help).
- [ ] Optional: UniProt mapping for Zhang-2024 from its genome IDs; read Zhang supplementary S1–S7.
