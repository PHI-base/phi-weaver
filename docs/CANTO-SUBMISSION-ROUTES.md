---
created: 2026-07-06
type: documentation
tags: [docs]
project: PHI-Weaver
---

# Getting phiweaver drafts into PHI-Canto — routes & recommendation

**Status:** planning note (2026-07-06). No code written yet. Decision pending on Canto server access.
**Corrected 2026-07-25:** the original Route 2 named the wrong script — `canto_load.pl` does *not*
create sessions. Corrected below, along with the consequence: the documented import format covers
less than this note assumed. Routes 1 and 3 verdicts are unchanged.

**Goal:** enter the information from phiweaver curation drafts
(`/mnt/z/PHI-Canto-Literature/active/*-phiweaver-DRAFT.md`) into the PHI-Canto web tool at
<https://canto.phi-base.org/> so curated papers can be submitted for biocurator review.
Submission account: `phibase1@gmail.com`.

## Key facts about PHI-Canto (confirmed 2026-07-06; script facts re-verified 2026-07-25)

- PHI-Canto is an instance of **Canto**, PomBase's community curation tool (Rothamsted runs the
  PHI-base configuration). Docs: <https://curation.pombase.org/docs/canto_admin>,
  tutorial <https://pombase.github.io/canto_tutorial/>, code <https://github.com/pombase/canto>.
- **No public write API.** Curation is done through a multi-step web UI; there is no REST endpoint
  to create annotations.
- Canto *does* have a documented **JSON export** and server-side command-line scripts. Which script
  does what (verified against the sources, 2026-07-25):
  - **`canto_add.pl --sessions-from-json <file> <curator_email> <default_taxonid>`** — **creates
    sessions from JSON.** This is the only session-import route. Format documented at
    <https://github.com/pombase/canto/wiki/JSON-Import-Format>. (`--session <pmid> <email>` creates
    a single empty session.)
  - **`canto_load.pl`** — loads **reference data only**: genes, organisms, strains, ontologies
    (OBO), PubMed XML. It **does not create sessions**, and an earlier version of this note wrongly
    said it did.
  - **`canto_export.pl canto-json --dump-approved`** — exports approved sessions. One-way *out*.
  - **`pombase-import.pl`** (separate pombase-chado repo) — loads exported JSON into a **Chado**
    database. That is downstream of Canto, not a way back in.
  - **`canto_merge.pl`** — merges **person records**, not sessions.
- **What the import format covers:** session/publication, genes, alleles, genotypes (incl. diploids),
  and session notes. It does **not** cover **metagenotypes** or **annotations** (term IDs, evidence
  codes, conditions, extensions) — i.e. it can build the scaffold but not the curation itself.
- Loading is a **server/admin operation on the Canto host**, not a web-curator feature.
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

### Route 1 — Assisted-entry queue  ⭐ recommended first step
A script turns each draft into a table-driven click-list matching Canto's exact click-path: PMID →
gene list (organism + identifier) → each allele (name/type/expression) → genotypes → metagenotypes
(controls flagged) → one row per annotation (feature → term ID + name → evidence → extensions →
figure), with uncertain items parked in a safety section so they can't be entered by accident.
Curator opens Canto + entry queue side by side and enters it, ticking as they go.
- **Works with:** web login only. **Effort:** small. **Robustness:** high (a human does the clicks).
- **Pros:** works today; can't corrupt anything; keeps the curator's judgment on every AI-drafted
  item before submission; low build + maintenance; reuses existing draft structure.
- **Cons:** still manual typing (but fast and error-checked); doesn't auto-submit.

### Route 2 — Canto import JSON + `canto_add.pl --sessions-from-json`  (scaffold only)
Generate Canto import JSON from each draft; an admin runs
`canto_add.pl --sessions-from-json <file> <curator_email> <default_taxonid>` to create sessions
pre-loaded with the **genes, alleles and genotypes**. **Metagenotypes and annotations are not
importable** (see key facts), so those are still entered in the web UI afterwards — Route 2 shortens
Route 1's click-list, it does not replace it.
- **Works with:** server/admin access (ours, or a cooperating maintainer). **Effort:** medium.
  **Robustness:** high (design-aligned, no UI).
- **Pros:** removes the most tedious, least judgment-laden entry (alleles/genotypes) with no brittle
  UI; the schema is **documented**, not reverse-engineered; scaffold errors are objective and cheap
  to eyeball; scales.
- **Cons:** requires shell access to the Canto host; papers do **not** land ready for approval — the
  annotation layer remains manual; needs PHI-Canto's own `canto_deploy.yaml` (private repo) plus a
  **staging/local instance** to test loads before touching the live queue; PHI-base
  allele/metagenotype conventions still have to be mapped onto the documented format.

### Route 3 — Browser automation (Playwright/Selenium)  — not advised
A bot logs in as `phibase1@gmail.com` and drives the whole web UI.
- **Works with:** web login only. **Effort:** high + ongoing. **Robustness:** low.
- **Cons:** Canto's UI is a complex multi-step AJAX app with server-backed ontology autocompletes;
  a bot breaks on every Canto update and needs constant maintenance; it also fires automated writes
  into a shared community resource. Poor return; steer away.

## Recommendation

**Route 1 now** (MVP that lets submission start today), **plus Route 2 for the scaffold if server
access exists.** Avoid Route 3.

Route 2 was originally written up as "the durable target" that would supersede Route 1. With the
script correction above that is no longer right: because the import format stops at genotypes, the
end state is **Route 2 + Route 1 together** — imported scaffold, hand-entered annotations — and
Route 1's entry queue stays in the workflow permanently rather than being an interim MVP.

## Caveat (any route)

These are **AI drafts** carrying curator flags (e.g. "no PHIPO term found"). They must pass curator
review before entering the biocurator queue — the existing draft → validated workflow enforces this.
Pushing unreviewed drafts in at volume would burden reviewers. Route 1 builds that checkpoint in
naturally.

## Open questions to resolve before building

1. **Server access** to canto.phi-base.org: shell/admin, or web login only? (Decides whether Route 2
   can add the scaffold import on top of Route 1 — not "Route 1 vs 2"; see the recommendation.)
2. **Volume / cadence** of submissions (a few papers vs. many) — affects whether the manual
   entry queue is enough or the JSON pipeline is worth the investment.
3. If Route 2: who administers the instance and can run `canto_load.pl` / provide a staging server?
4. Relationship to the backlog **recuration-comparison** workflow and the longer-term
   plug-in/ROGER direction — is Canto submission a standalone tool or part of that.
