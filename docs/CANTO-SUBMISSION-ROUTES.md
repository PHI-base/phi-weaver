# Getting phiweaver drafts into PHI-Canto — routes & recommendation

**Status:** planning note (2026-07-06). No code written yet. Decision pending on Canto server access.

**Goal:** enter the information from phiweaver curation drafts
(`/mnt/z/PHI-Canto-Literature/active/*-phiweaver-DRAFT.md`) into the PHI-Canto web tool at
<https://canto.phi-base.org/> so curated papers can be submitted for biocurator review.
Submission account: `phibase1@gmail.com`.

## Key facts about PHI-Canto (confirmed 2026-07-06)

- PHI-Canto is an instance of **Canto**, PomBase's community curation tool (Rothamsted runs the
  PHI-base configuration). Docs: <https://curation.pombase.org/docs/canto_admin>,
  tutorial <https://pombase.github.io/canto_tutorial/>, code <https://github.com/pombase/canto>.
- **No public write API.** Curation is done through a multi-step web UI; there is no REST endpoint
  to create annotations.
- Canto *does* have a documented **JSON export** and server-side command-line scripts, including
  **`canto_load.pl`** (plus `canto_export.pl`, `canto_merge.pl`, `canto_curs_map.pl`). Loading is
  a **server/admin operation on the Canto host**, not a web-curator feature.
- **The pivotal unknown:** do we have **server/admin (shell) access** to canto.phi-base.org (or a
  cooperating admin / the PomBase-Rutherford maintainer who does), or **only the curator web
  login**? This decides which route is viable.

## The drafts are already in Canto's shape

Each draft already contains Canto's data model in order: genes with UniProtKB IDs → genotypes
(allele type + expression) → **metagenotypes** (pathogen × host, controls marked) → annotations
(pathogen phenotype, pathogen–host interaction phenotype, disease name, GO), each with a term ID,
evidence code, and conditions/extensions. The biology structuring is done; what remains is
*transport* into Canto.

## Three routes

### Route 1 — Assisted-entry worksheet  ⭐ recommended first step
A script turns each draft into an ordered checklist matching Canto's exact click-path: PMID → gene
list (organism + identifier) → each allele (name/type/expression) → genotypes → metagenotypes
(controls flagged) → one row per annotation (feature → term ID + name → evidence → extensions →
figure). Curator opens Canto + worksheet side by side and enters it, ticking as they go.
- **Works with:** web login only. **Effort:** small. **Robustness:** high (a human does the clicks).
- **Pros:** works today; can't corrupt anything; keeps the curator's judgment on every AI-drafted
  item before submission; low build + maintenance; reuses existing draft structure.
- **Cons:** still manual typing (but fast and error-checked); doesn't auto-submit.

### Route 2 — Canto session JSON + `canto_load.pl`  (the durable target)
Generate Canto session JSON from each draft; an admin runs `canto_load.pl` to create sessions
directly in the biocurator review queue.
- **Works with:** server/admin access (ours, or a cooperating maintainer). **Effort:** medium–high.
  **Robustness:** high (design-aligned, no UI).
- **Pros:** true bulk; no brittle UI; papers land ready for approval; scales.
- **Cons:** requires shell access to the Canto host; must reverse-engineer the exact session-JSON
  schema and PHI-Canto's allele/metagenotype conventions; needs a **staging instance** to test
  loads before touching the live queue.

### Route 3 — Browser automation (Playwright/Selenium)  — not advised
A bot logs in as `phibase1@gmail.com` and drives the whole web UI.
- **Works with:** web login only. **Effort:** high + ongoing. **Robustness:** low.
- **Cons:** Canto's UI is a complex multi-step AJAX app with server-backed ontology autocompletes;
  a bot breaks on every Canto update and needs constant maintenance; it also fires automated writes
  into a shared community resource. Poor return; steer away.

## Recommendation

**Route 1 now** (MVP that lets submission start today), **Route 2 as the real pipeline if server
access exists.** Avoid Route 3.

## Caveat (any route)

These are **AI drafts** carrying curator flags (e.g. "no PHIPO term found"). They must pass curator
review before entering the biocurator queue — the existing draft → validated workflow enforces this.
Pushing unreviewed drafts in at volume would burden reviewers. Route 1 builds that checkpoint in
naturally.

## Open questions to resolve before building

1. **Server access** to canto.phi-base.org: shell/admin, or web login only? (Decides Route 1 vs 2.)
2. **Volume / cadence** of submissions (a few papers vs. many) — affects whether the manual
   worksheet is enough or the JSON pipeline is worth the investment.
3. If Route 2: who administers the instance and can run `canto_load.pl` / provide a staging server?
4. Relationship to the backlog **recuration-comparison** workflow and the longer-term
   plug-in/ROGER direction — is Canto submission a standalone tool or part of that.
