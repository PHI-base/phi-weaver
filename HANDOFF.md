# HANDOFF — continue phiweaver

Concise "start here" pointer. Full history is the latest session log
(`11-CLAUDE-AI/SESSION-LOGS/Session-Logs-INDEX.md` → newest row) and `docs/DESIGN-DECISIONS.md`.

## Where things stand (2026-07-08)
- **Phase 4 complete:** all **10 benchmark drafts** have a structured `canto` block and a
  `*-phi-canto-entry-queue.md`. Work products live in external
  `/mnt/z/PHI-Canto-Literature/active/` (uncommitted by policy); tracker there is
  `PHASE4-CANTO-WORKSHEET-PROGRESS.md`.
- **PHI-Canto submission = Route 1**, one deterministic renderer (run from repo root, stdlib-only):
  `python3 -m phiweaver.canto.entry_queue <draft.md>` (lean table click-list; held-gene cascade +
  parked safety section; `--validate` opt-in ontology check). Biocurator entry into PHI-Canto **is**
  the validation step. A **coverage lint** (`phiweaver.canto.coverage`) warns (stderr) about block
  genotypes in no metagenotype. (The fuller `canto-worksheet` renderer was retired — see **D16**.)
- **11 skills** (`skills/REGISTRY.md`); green gate: `python3 -m phiweaver.smoke` (8/8, and the
  last of those 8 checks *is* the unit suite — 490 tests).

## Next tasks
1. **Resolve the 2 remaining accession blockers**: **URA5** (PMID:1541525, ambiguous) then
   **FleQ/GcbB** (PMID:41229162, no UniProt entry for the Pta6605 proteome — hardest). Use
   `python3 -m phiweaver.lookup.query_uniprot`; never invent an accession. (CgHat1 was resolved →
   A0A8H4CVH4.)
2. **Hand-score** the 10 benchmark scorecards (`07-Standards/curation-benchmarking/`) → then
   `scorecards_to_csv` → `benchmark_report`. phiweaver must not grade its own drafts.
3. **Canto route decision**: if server access to canto.phi-base.org exists, Route 2
   (`canto_load.pl`, server-side) vs the Route 1 entry queue. See `docs/CANTO-SUBMISSION-ROUTES.md`.
4. Ongoing depth work: more validated **gold-standard examples** (12/12 annotation-type breadth is
   already done; add depth). How-to below.

## How to add a gold-standard example (reference)
1. Curator drops a completed PHI-Canto session (PDF/HTML) into `PHI-Canto-Literature/active/`; give
   the filename + confirm the PMID from the content (the read-only Canto URL can't be fetched).
2. Extract (PDF via `fitz`; HTML read directly).
3. **Validate every ontology ID**: `python3 -m phiweaver.lookup.validate_ontology_ids GO:.. PHIPO:.. PHIDO:..`
   (GO/PHIPO via OLS; PHIDO offline). Obsolete/not-found → flag; use the `replaced_by` successor.
4. Write `07-Standards/curation-examples/<PMID>-<slug>.md`: curation-example frontmatter
   (`status: validated`, `annotation_types` = the real PHI-Canto types, etc.) + the curation **kept
   in PHI-Canto's structure** (gold standards are NOT retyped into the draft template body).
5. Register: `python3 -m phiweaver.curation_examples` then `--check`.

## Ground rules
- Work in `/mnt/z/phi-weaver`; on WSL launch `claude --dangerously-skip-permissions`.
- **Green gate: `python3 -m phiweaver.smoke`, on its own.** It already runs the unit suite,
  so adding `unittest discover` beside it executes every test twice (~89s instead of ~55s on
  the `z:` mount). While iterating, run the one relevant module
  (`python3 -m unittest tests.test_entry_queue`, a few seconds) and keep the full gate for
  pre-commit; `--no-tests` (~17s) gives the fresh-checkout checks alone.
- **Git rules live in [AGENTS.md](AGENTS.md) §5 — follow them there, not here.** They cover
  commit style, what must never be committed, and the `z:` mount's lock-file traps
  (`git config`, `git stash`). This file used to restate them and drifted out of sync twice,
  so it no longer keeps its own copy.
- Per-paper work products (PDFs, drafts, scorecards, entry queues) stay in external
  `active/`, **not committed**; only engine/skills/docs + wrapped gold-standard `.md` go in the repo.

## Read at session start
`MEMORY.md` · newest `11-CLAUDE-AI/SESSION-LOGS/` entry · `docs/BACKLOG.md` ·
`docs/DESIGN-DECISIONS.md` · `07-Standards/curation-examples/` (`TAGS.md`, `_TEMPLATE.md`, `INDEX.md`).

## Not this task (separate)
Benchmarking stack is complete. **phikestrel** (pipe/ROGER) is a *different repo*
(`/mnt/z/phikestrel`) — don't build it here.
