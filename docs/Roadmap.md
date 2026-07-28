---
created: 2026-07-20
type: documentation
tags: [docs, roadmap]
project: PHI-Weaver
---

# PHI-Weaver — Roadmap

**Canonical for:** where PHI-Weaver is going. What it does *today* belongs in
[`OVERVIEW.md`](OVERVIEW.md); task-level detail in [`BACKLOG.md`](BACKLOG.md).
See [`README.md`](README.md).

A short, shareable view of where PHI-Weaver is and where it is going — for team discussion and
for informing collaborators. This is the **readable summary**; the working detail (every task,
gap and rationale) lives in [`BACKLOG.md`](BACKLOG.md), [`DESIGN-DECISIONS.md`](DESIGN-DECISIONS.md)
and [`PLUGIN-ARCHITECTURE.md`](PLUGIN-ARCHITECTURE.md). When an item here needs the "why" or the
fine print, follow the link.

**What PHI-Weaver is:** an AI-assisted biocuration toolkit for **PHI-base / PHI-Canto**. It turns
published papers into structured, PHI-Canto-ready annotation **drafts** and tracks curation
progress — always as *draft curator assistance*, never a replacement for an expert curator.

**Guiding principles** (unchanged across the roadmap): never invent identifiers or terms; check
UniProtKB first; verify ontology terms exist and aren't obsolete; separate evidence /
interpretation / speculation; preserve provenance; a human always validates. Start simple; defer
heavy infrastructure until a concrete need forces it.

---

## ✅ Now — working today

- **Paper → draft pipeline:** PDF → clean markdown (+ figures/captions) → triage → UniProt
  resolution → genotype creation → phenotype→PHIPO mapping → annotation → QC.
- **Offline ontology validation:** PHIPO, PHIDO, PHI-ECO (PECO), PHIPO_EXT, FYPO_EXT and the
  extension configs all resolve **without network** from vendored copies (existence + obsolescence);
  GO/MOD via EBI OLS. Underpins both lookup and the leak-free benchmark.
- **All 12 PHI-Canto annotation types** covered by ≥1 validated gold-standard example; a
  tag-classified example library that drafting retrieves from.
- **Benchmarking:** blind, scored-vs-gold runs with a shareable HTML report; per-paper token cost
  tracking (per model, priced) in the tracking DB.
- **Tracking + provenance:** SQLite progress DB, session logs, model/commit provenance stamped on
  every draft.
- **Curation-record learning:** a declarative, reversible lessons ledger (`CURATION-LESSONS.md`)
  that feeds the drafting skills.

## 🔜 Next — near-term, active

- **Get drafts into PHI-Canto for biocurator review** — the validation step. Route 1 (assisted-entry
  queue) is built; the pivotal open decision is server/admin access to canto.phi-base.org vs
  web-login only. See [`CANTO-SUBMISSION-ROUTES.md`](CANTO-SUBMISSION-ROUTES.md).
- **Activate the leak-free benchmark sandbox** — isolation verified (`bwrap`); remaining step is one
  end-to-end run confirming ontology/UniProt access while PHI-base **data** repos stay blocked.
- **Format convergence** — converge draft body shape toward PHI-Canto's structure so retrieval and
  benchmarking compare like-for-like.
- **Fold in the curator's convention answers** — apply Hsin-Yu's review clarifications (gene-symbol
  source, allele naming, evidence-code questions) into the standards docs.
- **Close the open PHIPO ontology gaps** — per-chemical SDHI sensitivity terms, toxisome-formation
  phenotype, and the filed term requests (see *Collaborator questions* below).

## 🌱 Later — deliberately deferred (needs a concrete trigger or collaborator help)

- **Plug-in host + local AI on ROGER** — a light core that independently-built modules plug into;
  heavy GPU work (e.g. figure/image recognition) runs on the ROGER cluster. Destination, not first
  step — start with figure **caption text** before any vision model. See
  [`PLUGIN-ARCHITECTURE.md`](PLUGIN-ARCHITECTURE.md).
- **Semantic recall over accumulated curation knowledge** — an embeddings-backed retrieval layer
  ("have I decided something like this before?") over the lessons ledger and example library, added
  **only when** the corpus outgrows linear reading *and* we catch a draft re-deciding a settled
  question. Keep markdown as source of truth; add retrieval as a read-only layer (no autonomous
  memory rewriting — that conflicts with the reversible-learning rule); run embeddings local on
  ROGER. See the item in [`BACKLOG.md`](BACKLOG.md).
- **Recuration comparison** (biocurator vs PHI-Weaver) — a neutral, deterministic diff of the same
  papers curated both ways, to surface divergences for training/tuning. Neither side declared
  "correct"; a human adjudicates only the divergent rows.
- **LLM-as-judge / independent reviewer** — a *different* model as an independent critic/scorer so
  PHI-Weaver never self-validates. Must itself be ground-truthed before any score is trusted; never
  replaces the human gate.
- **Mine (don't ingest) the PHI-Canto issue tracker** — harvest *resolved* convention decisions into
  our standards with a `See:` pointer; never bulk-ingest raw discussion (wrong conventions +
  benchmark leakage).

---

## 🤝 Open questions for collaborators

These are framed as **discussions**, not decisions anyone must rule on alone.

**For Hsin-Yu (curation conventions / ontology judgement):**
- How much term **design** should an ontology request carry? Our guardrail is "evidence, not
  design", but PHIPO's `CONTRIBUTING.md` invites label/definition/parent — so we may be stricter
  than the ontology team's own house rule.
- Curator-triggered term-design proposals → GitHub issue: when a curator explicitly asks for a
  drafted proposal, what should it contain and how should confidence be stated?
- GO evidence code **ISO** — reopen the ISS-family ruling? ISO is stricter than the rejected ISS
  (traces to a real experiment in a named ortholog); does it fit PHI-base?

**For James (technical / PHI-base infrastructure):**
- Whether the leak-free benchmark and future modules can rely on public sources for the extension
  configs (currently hand-vendored from the private config repo).
- PHIPO PR [#454](https://github.com/PHI-base/phipo/pull/454): the right term ID to take and whether
  the obsoleted PHIPO:0000503 should get a `replaced_by` pointer.

**Filed and awaiting response (ontology team):**
- [phipo#452](https://github.com/PHI-base/phipo/issues/452) / [#454](https://github.com/PHI-base/phipo/pull/454)
  — free-living "absent DON" term.
- [phipo#453](https://github.com/PHI-base/phipo/issues/453) — is the in-host / free-living split
  always two-way?

---

*Maintenance: keep this in step with `BACKLOG.md` — when a Next item ships, move it to Now; when a
Later item's trigger fires, promote it to Next. This file is the summary; the backlog is the record.*
