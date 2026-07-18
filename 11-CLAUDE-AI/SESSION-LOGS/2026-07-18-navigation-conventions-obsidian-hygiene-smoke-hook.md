---
created: 2026-07-18
type: session-log
tags: [status/complete]
project: Navigation indexes, link/naming/commit conventions, Obsidian hygiene, code-gated smoke hook
---

# Session: ontology index, conventions (link/naming/commit), Obsidian gitignore, code-gated smoke hook

A documentation / vault-hygiene / tooling-guard session — no curation. Entirely question-driven:
each step came from a user question, and several exposed a real flaw that then got fixed. Theme:
make weaver's parts **navigable and self-guarding** without adding duplication.

## Objectives
- Answer "should weaver have an ontology / curation *section* as index files with pointers?"
- …which cascaded into: link conventions, an Obsidian graph-view name collision, a naming guard,
  frontmatter coverage, Obsidian plugin/gitignore hygiene, and a smoke-test-on-session-start hook.

## Work done

### Ontology index + AGENTS "map of maps" (commits 603d065, 10abaa5)
- The **curation** index already exists (generated `skills/REGISTRY.md`) — a second one would
  duplicate it. The **ontology** material was the real gap: scattered across six homes (reference
  guide, cheatsheet, `phiweaver/lookup/` tools, vendored `data/*.obo`, gap ledger, term-request
  skill) with no single pointer page. Wrote **`07-Standards/Ontology-INDEX.md`** — pointers only,
  no duplicated content; tooling rows mirror `REGISTRY.md` (authoritative).
- Added an **Indexes** list to `AGENTS.md` §1 as the map-of-maps (registry, ontology, curation
  examples, session logs, literature), each reachable in one hop from the file agents load first.

### Link conventions + a cross-store dangling-link bug (10abaa5, 9205d99)
- **Bug caught:** `Ontology-INDEX.md` (a *vault* file) used `[[phipo-local-clone]]` etc. — but those
  are **Claude-memory slugs** living outside the vault (`~/.claude/.../memory/`), so they render as
  **dangling links in Obsidian**. Replaced all four with vault-resolvable prose/paths; fixed the same
  pre-existing `[[phipo-local-clone]]` in `skills/ontology-term-request/SKILL.md`.
- **Rule written into `AGENTS.md` §1:** link style by *what you point at* — `[[slug]]` for a note in
  the **same store**, a markdown path link for code/data/anything opened by path; **never `[[link]]`
  across stores.** (Obsidian graph labels/`[[links]]` resolve by *basename*; markdown path links stay
  in the graph as long as they're vault-relative, not filesystem-absolute.)

### INDEX.md graph collision → renamed both (10abaa5)
- Two files literally named `INDEX.md` showed as one ambiguous "INDEX" node in graph view (Obsidian
  labels by basename). Renamed → **`Curation-Examples-INDEX.md`** and **`Session-Logs-INDEX.md`**,
  updating both generators (`curation_examples.py` `INDEX_PATH`/`_SKIP_NAMES`; `generate_dev_timeline.py`
  read path + emitted `[[…]]`), the two tests, and ~14 doc references. Renamed the session-logs index →
  **note: this log's index is now `Session-Logs-INDEX.md`.** 287 tests + smoke green.

### Note-naming guard: `phiweaver/vault_names.py` (10abaa5)
- New deterministic guard: fails if two explorable `.md` share a basename, **exempting fixed-name
  convention files** (`SKILL.md`, `README.md`, and the `MIGRATED-TO-EXTERNAL-STORAGE.md` marker).
  Wired as the smoke test's **8th check** ("unique note names") + `tests/test_vault_names.py`.
- Rule documented in `AGENTS.md` §1; the graph-noise from the unfixable convention files
  (`SKILL.md` ×11, `README.md` ×9) is handled with a graph **view filter** (`-file:SKILL -file:README`),
  not renaming.

### Keep-it-simple commit rule (e8b59e1)
- User preferred "one commit in one go" over a 3-way logical split. Wrote it into `AGENTS.md` §5:
  **a coherent unit of work is one commit**; commit straight to `main`; stage only the task's files
  (leave unrelated dirty files like `.obsidian/` alone); short subject, body only when the *why* isn't
  obvious. Followed for the rest of the session.

### Frontmatter on 31 content notes (7a5156a)
- 46 `.md` lacked YAML frontmatter; added `created`/`type`/`tags`/`project` to the **31 genuine content
  notes** (`created` from each file's first git-commit date; type/tags by folder). **Excluded by
  design:** all `README.md` and root instruction files (`AGENTS`/`CLAUDE`/`HANDOFF`) — frontmatter
  renders as an ugly table on GitHub — and the generated indexes. Verified via a script + all contract
  checks green. Confirmed the tooling ignores unknown frontmatter keys (parsers only require named
  fields), so this is safe.

### Obsidian fully gitignored + daily-notes folder (c447703, 4b5b24c, b9bb1d1)
- Root cause of the session-long git-status noise: `workspace.json` was **in `.gitignore` yet still
  tracked** (ignore doesn't untrack). Progressively untracked `workspace.json`, `app.json`,
  `community-plugins.json`, then **ignored all of `.obsidian/`** (`git rm -r --cached`, local files
  kept). Also ignored **`__Obsidian-SYSTEM/`** where Daily Notes/Calendar write (user set Daily Notes'
  folder to `__Obsidian-SYSTEM/Daily`). Net: git-status quiet on Obsidian; each collaborator configures
  their own vault.

### Article-Registry dashboard refresh (61d5e19)
- Committed the user's pre-existing regenerated `08-Wiki/Article-Registry.md` (auto-generated dashboard:
  updated activity counts + new "Token Costs" section — Li paper, Opus 4.8, ~$73.45).

### FAQ: Obsidian content plugins are safe + TOC-block proof (5d506f5, 024a30a)
- FAQ entry (canonical): content plugins (Table of Contents, Daily Notes, Calendar) are safe — weaver
  never executes fenced blocks and its frontmatter parsers **stop at the closing `---`**, so a
  ```` ```table-of-contents ```` block beneath frontmatter is inert. Cautions: such blocks only render
  *in Obsidian* (empty code block on GitHub / in generated bundles); keep them off generated files;
  avoid **auto-rewriter** plugins (linters/formatters) on generated/contract files. **Proven live:** the
  user's TOC block in the Gene-for-Gene methodology passed the full contract suite when committed.

### SessionStart smoke hook — HEAD-moved, then **code-change-gated** (82c94b4, 3239718)
- Advice first: **don't** run smoke every session (287 tests, ~30–45 s, no new info on an unchanged
  checkout). Run it after a pull / env change / before a scored benchmark; the network + a stale PHIPO
  clone are what smoke *doesn't* check anyway.
- Built a local (gitignored `.claude/`) `SessionStart` hook + `session-start-smoke.sh`. **v1 fired on any
  HEAD move** — user flagged that this includes every docs commit. **v2 (final) gates on code:** runs
  smoke only when the diff since the last check touched `phiweaver/` | `scripts/` | `tests/` |
  `pyproject.toml`; docs/frontmatter/FAQ changes advance the baseline **silently**. Stores last-checked
  HEAD in `.git/last-smoke-head`; always exits 0 (warns, never blocks). Both paths tested; the FAQ
  commit documenting it self-proved the silent path.

## Key decisions
- **Pointers, not duplication.** New indexes/FAQ entries are pointer layers over canonical homes
  (`AGENTS.md`, skills). Every "canonical for this decision" note says so explicitly.
- **Link style by target, within a store.** Slug wikilinks between notes in the same store; markdown
  path links to code/data; never across the vault↔memory boundary.
- **Unique note basenames**, enforced by smoke; convention files (`SKILL.md`/`README.md`) exempt and
  filtered out of the graph instead of renamed.
- **One commit per unit of work**, straight to `main`, unrelated dirty files left alone.
- **Frontmatter yes for content notes, no for READMEs / root-instruction / generated files.**
- **Smoke automation gates on code changes, not HEAD moves** — the sharper signal (catches code from a
  commit *or* pull; ignores prose from either).

## State / open threads
- 13 commits on `main` (`603d065`…`3239718`); **2 unpushed** (`82c94b4`, `3239718`) at session end.
- **3 `06-Training` files** carry uncommitted TOC-block edits from the user (Obsidian) — left for the
  user to commit.
- SessionStart smoke hook is **local-only** (gitignored `.claude/`), armed for next session; baseline
  at current HEAD so it stays silent until a code change lands.
- 287 tests + smoke 8/8 green throughout.
