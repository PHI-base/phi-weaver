---
created: 2026-07-28
type: documentation
tags: [docs, index]
project: PHI-Weaver
---

# PHI-Weaver docs — the map

**One doc owns each topic.** Every other doc that touches the same topic must summarise and
link, never explain in parallel. Parallel explanations drift silently: nothing fails, an agent
just reads the stale copy and acts on it.

Before writing a doc, find the topic below and edit **that** file. Add a new doc only when the
topic genuinely isn't listed — then add its row here.

## Canonical owners

| Topic | Canonical doc |
|---|---|
| Rules every agent follows (accuracy, coding, file safety) | [`../AGENTS.md`](../AGENTS.md) |
| What PHI-Weaver is; what it can do today | [`OVERVIEW.md`](OVERVIEW.md) |
| Which modules/skills exist, their tools and tests | [`../skills/REGISTRY.md`](../skills/REGISTRY.md) — *generated* |
| How to add a module (the contract) | [`ADDING-A-MODULE.md`](ADDING-A-MODULE.md) |
| Why the system is built this way | [`DESIGN-DECISIONS.md`](DESIGN-DECISIONS.md) |
| Why it never self-validates; the LLM-judge design (parked) | [`LLM-AS-JUDGE-DESIGN.md`](LLM-AS-JUDGE-DESIGN.md) |
| Where it is going (readable summary) | [`Roadmap.md`](Roadmap.md) |
| Open tasks and known gaps (the record) | [`BACKLOG.md`](BACKLOG.md) |
| Where files are read and written | [`STORAGE-CONFIGURATION.md`](STORAGE-CONFIGURATION.md) |
| Running the PDF converter | [`PDF-CONVERTER-USAGE.md`](PDF-CONVERTER-USAGE.md) |
| Getting drafts into PHI-Canto (routes) | [`CANTO-SUBMISSION-ROUTES.md`](CANTO-SUBMISSION-ROUTES.md) |
| Route 1 entry queue, as built | [`CANTO-ROUTE1-BUILD-SPEC.md`](CANTO-ROUTE1-BUILD-SPEC.md) |
| How weaver learns (the design) | [`LEARNING-SYSTEM.md`](LEARNING-SYSTEM.md) |
| Lessons intake + where each was folded in | [`CURATION-LESSONS.md`](CURATION-LESSONS.md) |
| Ontology material (reference, tools, gaps) | [`../07-Standards/Ontology-INDEX.md`](../07-Standards/Ontology-INDEX.md) |
| Curation conventions | [`../07-Standards/PHI-Canto-Curation-Conventions.md`](../07-Standards/PHI-Canto-Curation-Conventions.md) |
| How the agent-instruction files are wired | [`agent-setup-notes.md`](agent-setup-notes.md) |
| Running the demo in Codespaces | [`DEMO-CODESPACES.md`](DEMO-CODESPACES.md) |

## Not canonical, by design

- **Lookup layer** — [`FAQ.md`](FAQ.md): short answers, each with a `See:` pointer to the owner
  above. Never the source of truth.
- **Future direction, not built** — [`PLUGIN-ARCHITECTURE.md`](PLUGIN-ARCHITECTURE.md).
  Describes a destination; do not read it as current architecture.
- **Pending review** — [`judge-rules-PROPOSED-for-review.md`](judge-rules-PROPOSED-for-review.md):
  held until a curator signs off.
- **Historical** — [`MODULARITY-PLAN.md`](MODULARITY-PLAN.md) (complete 2026-06-11),
  [`BENCHMARK-RUNBOOK-2026-07-05-test10articles.md`](BENCHMARK-RUNBOOK-2026-07-05-test10articles.md)
  (one dated run). Kept for the record; not a description of the system now.
- **Manuscript artefacts** — [`PHI-WEAVER-WHITEPAPER.md`](PHI-WEAVER-WHITEPAPER.md) and
  [`PHI-WEAVER-MODULE-TABLE.md`](PHI-WEAVER-MODULE-TABLE.md) (+ its `.html` render). Written for
  publication and frozen to what was true when drafted; correct them when the manuscript is
  revised, not on every code change.
- **Generated — do not hand-edit** — [`../skills/REGISTRY.md`](../skills/REGISTRY.md)
  (`python3 -m phiweaver.registry`, verified by `phiweaver.smoke`) and
  [`phiweaver-judge-handover.md`](phiweaver-judge-handover.md)
  (`python3 scripts/build_judge_handover.py`).

`superpowers/` holds per-task plans and specs — working notes for one piece of work, superseded
by whatever shipped.

## Facts that drift

Counts and inventories go stale the moment code lands. Where a doc must state one, prefer
naming the command that prints the truth over writing the number down. Live sources:
`skills/REGISTRY.md` (modules), `python3 -m phiweaver.smoke` (checks + test count).
