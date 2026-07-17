---
created: 2026-07-16
type: session-log
tags: [status/complete]
project: Backlog triage + UniProt strain fallback + RNA qualifiers
---

# Session: Backlog triage, UniProt strain fallback, RNA-level qualifiers

## Objectives
- Housekeeping on collaborators/memory, then work down `docs/BACKLOG.md` open items.

## Work done

### Memory / collaborators
- Added collaborator memory **James Seager** (GitHub `jseager7`, software developer at PHI-base /
  Rothamsted).
- Fixed the **Hsin-Yu Chang** memory: dropped the "NOT Hsin-Yun" correction, recorded her GitHub
  handle `Hsinyugithub`; updated the MEMORY.md index line.
- Added **user GitHub identity** memory: the user is Martin Urban, GitHub `martin2urban`; do **not**
  default his authorship to `changh` (that is Hsin-Yu's ontology contributor id from
  `Ontology-Terms-Reference.md`).
- Added **feedback** memory: when listing outstanding/backlog issues, present them **numbered** so
  items can be referenced by number.

### Backlog triage
- **Deferred** the "rewire the 4 hand-vendored extension configs to a public source" item (moved
  from Tooling/bugs → Deferred).
- **Benchmark sandbox (item 15):** user had installed `bubblewrap`; verified `/usr/bin/bwrap` 0.9.0
  works — userns OK, `--unshare-net` blocks connectivity while unsandboxed DNS resolves. Recorded
  the progress; the only remaining step is the one end-to-end test through Claude Code's sandbox
  layer (the domain allowlist is enforced there, not by raw bwrap).

### Feature — RNA-level qualifier phrases surfaced to drafting (commit 082ab3c)
- Curator ruled the PomGeneEx item **terms-only**: qualifier IDs not needed, only the phrases.
  Rewrote backlog item 1 to that reduced scope, then implemented it.
- Surfaced the seven controlled qualifier phrases (RNA level increased / decreased / unchanged /
  constant / fluctuates, RNA present, RNA absent) in three places the drafting workflow reads:
  `Gene-for-Gene-Curation-Methodology.md` §9 (authoritative phrase table + per-phrase "use when"),
  the `phenotype-annotation` skill (controlled-phrase step), and the `curation-qc` skill (flag
  free-prose RNA-level qualifiers). No ontology vendoring, no `PomGeneEx` prefix in the validator.

### Bug fix — query_uniprot strain-proteome fallback (commit f71fa2a)
- A `--locus-tag` search scoped to a **species** taxon returned a false `not_found` when the entry
  lived under a **strain** reference-proteome (child) taxon — e.g. PMID:42089373's five
  *F. pseudograminearum* Sdh subunits under strain CS3096 (taxon 1028729) vs species (101028).
- Fix: when a locus-tag search filtered by organism is empty, retry once without the organism filter
  and flag `organism_filter_relaxed`; `format_human` prints a strain-mismatch warning. Scoped to
  locus-tag searches only (gene-only searches never broaden). +4 tests; all 13 in
  `tests/test_query_uniprot.py` pass. Drove the PMID:42089373 case end-to-end: now `found` under the
  strain taxon with the warning, instead of `not_found`.

### PHIPO term request + backlog section (commit 0db0841)
- Filed **[PHI-base/phipo#452](https://github.com/PHI-base/phipo/issues/452)** — new free-living
  "absent deoxynivalenol" phenotype term (evidence PMID:42089373 Table S4). Confirmed it is a PHIPO
  request (not PECO); attributed to Martin Urban (@martin2urban), not `changh`.
- Added a **"Waiting for response (filed — external action)"** backlog section and moved the DON item
  there.

### Drafts left for the user (not sent/posted)
- A "Hello World" message reworked into a **GitHub Discussion** draft for PHI-base/phi-weaver
  (@Hsinyugithub, @jseager7) — not posted (needs category + Discussions enabled).
- A **Gmail draft** of the current backlog to `martin.urban@rothamsted.ac.uk` (the integration can
  only draft, not send) — sitting in Drafts for the user to send.

## Commits (all pushed to main)
- `082ab3c` — Surface the 7 PomGeneEx RNA-level qualifier phrases to the drafting workflow.
- `f71fa2a` — query_uniprot: strain-proteome fallback for locus-tag lookups (+4 tests; closes
  BACKLOG item 2).
- `0db0841` — BACKLOG: add "Waiting for response" section; file DON term request (#452).

## Notes / follow-ups
- Backlog items **1 and 2** (per-article token attribution; persisted token history) are marked open
  but their tools have landed with all sub-tasks done — candidates to tick `[x]`.
- Item 14 (benchmark sandbox): run the one end-to-end sandbox test.
- Item 9 (`phi-weaver#1`, obsolete PHIDO IDs) is also externally-blocked — candidate to move into the
  new "Waiting for response" section.
- Uncommitted, untouched: pre-existing `.obsidian/*` and `08-Wiki/Article-Registry.md` vault churn
  (left alone all session).
