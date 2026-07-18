# AGENTS.md — PHI-Weaver

Main source of truth for all agent instructions in this repository. Tool-agnostic:
Claude Code reads it via `CLAUDE.md`; OpenCode reads it natively. Keep it concise — put
procedures in `skills/`, not here.

## 1. Project Overview (stable knowledge)

PHI-Weaver is an AI-assisted biocuration toolkit for the **PHI-base / PHI-Canto**
pathogen–host interaction databases. It turns literature into structured,
PHI-Canto-ready annotation **drafts** and tracks curation progress.

- GitHub: `PHI-base/phi-weaver`. Pushing to `origin` is allowed (confirm first).
- Engine code is the importable **`phiweaver/`** package (`lookup/`, `tracking/`,
  `pipeline/`). No install needed: run from the repo root, e.g.
  `python3 -m phiweaver.lookup.query_uniprot …` or `python3 -m unittest discover -s tests`.
  `pip install -e .` is optional (CI/Codespaces). Old `python3 scripts/…` /
  `python3 11-CLAUDE-AI/…` paths still work via thin shims.
- Tools live in the repo; **literature content lives outside it**
  (default `../PHI-Canto-Literature/`, override with `PHI_LITERATURE_ROOT`; in
  Codespaces a `demo-literature/` folder is used). See `docs/STORAGE-CONFIGURATION.md`.
- Tracking database: SQLite at `11-CLAUDE-AI/db/phi_canto_tracking.db` (gitignored).
- At session start, read `11-CLAUDE-AI/SESSION-LOGS/Session-Logs-INDEX.md` for prior context.
- Key ontologies: PHIPO (phenotype), PHIDO (disease), GO, BRENDA tissue, UniProtKB, PHI-ECO
  (experimental conditions, prefix `PECO:`). Map of all ontology material (reference, tools,
  bundled data, gap ledger, term requests): [07-Standards/Ontology-INDEX.md](07-Standards/Ontology-INDEX.md).
- **Indexes** (this section is the map of maps; each index below is the map for its area):
  - [skills/REGISTRY.md](skills/REGISTRY.md) — reusable curation modules (skill → backing tool → tests); *generated*
  - [07-Standards/Ontology-INDEX.md](07-Standards/Ontology-INDEX.md) — where all ontology material lives (reference, tools, data, gaps)
  - [07-Standards/curation-examples/Curation-Examples-INDEX.md](07-Standards/curation-examples/Curation-Examples-INDEX.md) — the gold-standard curation-example library
  - [11-CLAUDE-AI/SESSION-LOGS/Session-Logs-INDEX.md](11-CLAUDE-AI/SESSION-LOGS/Session-Logs-INDEX.md) — prior session context (read at session start)
  - [content-links/literature-index.md](content-links/literature-index.md) — the external literature corpus
- **Link conventions.** Pick the link style by what you point at, not by file:
  - Pointing at a **note in the same store** (vault-note → vault-note, or memory → memory):
    use an Obsidian `[[slug]]` wikilink.
  - Pointing at a **code/data/config file, or anything to open by path** (incl. from AI-facing
    files like this one): use a markdown path link `[path](path)` or a backtick path.
  - **Never `[[link]]` across stores.** Claude's memory (`~/.claude/.../memory/`) lives *outside*
    the vault, so a vault note that `[[links]]` a memory slug is a dangling link in Obsidian.
    Restate the fact in prose, or link the real file/URL instead.
- **Note naming (graph-friendly).** Obsidian labels graph nodes, the quick-switcher, and
  `[[links]]` by a note's *basename*, so two notes with the same basename collide (they show as
  indistinguishable nodes and make a `[[link]]` ambiguous). Give every explorable note a
  **vault-unique, descriptive basename**; for a folder's index/meta note, prefix the folder's
  subject (`Curation-Examples-INDEX.md`, not `INDEX.md`). Fixed-name convention files
  (`SKILL.md`, `README.md`) are exempt — don't rename them; hide them from the graph with a view
  filter instead (e.g. `-path:skills -file:README`). Enforced by
  `python3 -m phiweaver.vault_names --check` (also a smoke-test check); add a justified
  exemption to `EXEMPT_BASENAMES` only when a name is dictated by a tool or platform.
- When a recurring question gets resolved, add a short Q/A + a `See:` pointer to
  `docs/FAQ.md` (a lookup layer over the canonical docs — keep answers short, don't duplicate).

## 2. Mission & Boundaries

- **Assist, do not replace, expert biocurators.** Every output is **draft curator
  assistance** unless a human has explicitly validated it.
- Surface uncertainty; never present a guess as a fact.
- The curator owns the final decision and any submission to PHI-base.

## 3. Scientific Accuracy Rules

- **Never invent** references, PMIDs, DOIs, UniProtKB accessions, gene names,
  gene/protein functions, ontology terms, or PHIPO/GO/PHIDO mappings. If unknown, say so.
- **Check UniProtKB first** for gene/protein identity and function; cite the accession.
  Prefer authoritative sources (UniProtKB, PubMed, PHI-base, GO/OLS).
- **Verify ontology term IDs exist and are not obsolete** before using them.
- **Separate evidence, interpretation, and speculation** — label each, and tie claims to
  a specific figure/table/section of the source.
- **Preserve provenance**: record input files, commands run, assumptions, outputs, and
  open uncertainties.
- State experimental evidence type and conditions; do not generalise beyond the data.

## 4. Coding Standards

- Match surrounding code's style, naming, and idioms; don't reformat unrelated code.
- Engine code lives in the `phiweaver/` package; add new tools under the right subpackage
  with co-located tests in `tests/`. **Derive paths from `phiweaver.repo_root()`** (or
  `__file__`), never hardcode machine-specific paths (e.g. `/mnt/z/...`).
- Make storage/config overridable via environment variables where it crosses machines.
- Keep changes small and reviewable; explain non-obvious choices in a brief comment.
- Verify before claiming done: `python3 -m py_compile` for scripts, and run the smoke path.

## 5. File Safety Rules

- **Do not delete or overwrite existing files without first showing the proposed change.**
- Look at a file before changing it; if its content contradicts how it was described,
  surface that instead of proceeding.
- **Never commit** unpublished curation data, personal-progress DBs, PDFs of copyrighted
  papers, or secrets. Respect `.gitignore`. Literature/media stay in external storage.
- Git: commit when asked; pushing to `PHI-base/phi-weaver` is allowed. On the `z:` Windows
  mount, `git config` / `git remote set-url` fail (lock-file chmod) — edit `.git/config`
  directly.
- **Keep commits simple.** A coherent unit of work is **one commit** — don't split into
  micro-commits or agonise over logical separation unless asked. Commit straight to `main`;
  stage only the task's files (leave unrelated dirty files like `.obsidian/` alone). Short
  imperative subject; add a brief body only when the *why* isn't obvious.

## 6. Reusable Workflows (skills)

Task workflows live in `./skills/`, one folder per skill with a `SKILL.md`:

- `uniprot-lookup/` — resolve a gene/protein to a UniProtKB accession + evidence-backed function
- `paper-triage/` — assess whether a paper has curatable PHI content
- `phipo-mapping/` — map described phenotypes to PHIPO terms
- `curation-qc/` — quality-check a draft curation before human review

Invoke a skill when its "when to use" condition is met, and follow its QC and
human-review requirements.

## 7. Tool-Specific Settings

- **Claude Code**: `CLAUDE.md` bridges to this file; skills run via the Skill tool.
- **OpenCode**: reads this `AGENTS.md` natively; same `./skills/` workflows apply.
- See `docs/agent-setup-notes.md` for how the setup is wired and maintained.
