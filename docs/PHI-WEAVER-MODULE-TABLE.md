---
created: 2026-07-23
type: documentation
tags: [docs, manuscript]
project: PHI-Weaver
---

# PHI-Weaver — Module Operating-Mode Table (manuscript Table 1)

*Manuscript-ready description of how many agents PHI-Weaver uses and which stages are
language-model-driven versus deterministic. Rendered version: [PHI-WEAVER-MODULE-TABLE.html](PHI-WEAVER-MODULE-TABLE.html).*

---

## Agent count — the short answer

PHI-Weaver defines **no specialised agents**. There is no `.claude/agents/` directory, no agent
personas, no orchestrator, no router, and no agent-to-agent messaging. A **single general-purpose
language-model agent** (used through Claude Code; portable to any assistant that reads
[AGENTS.md](../AGENTS.md)) executes every stage, governed by one instruction file, 12 skills
([skills/REGISTRY.md](../skills/REGISTRY.md)), and deterministic Python tools in `phiweaver/`.

For multi-paper batches, **one ephemeral copy of the same agent is spawned per paper and run
sequentially** — identical configuration, differing only in which paper it is given. The purpose is
context isolation, to stop genes, hosts, strains, or figure numbers bleeding between drafts; each
draft lands on disk before the next paper starts. Concurrency is 1 by design. See
[DEMO-CODESPACES.md](DEMO-CODESPACES.md) and
[BENCHMARK-RUNBOOK-2026-07-05-test10articles.md](BENCHMARK-RUNBOOK-2026-07-05-test10articles.md).

So: **1 agent role, 1 concurrent agent, *n* ephemeral identical instances for a batch of *n* papers.**

## Methods text (plain English, for biologists)

PHI-Weaver is not a collection of specialised AI programs that talk to each other. It is a single
general-purpose AI assistant (a large language model, used here through Claude Code) that has been
given three things: one instruction file setting the rules it must follow, twelve written procedures
covering the individual curation tasks, and a set of conventional Python scripts that it calls
whenever a fact must be looked up rather than recalled. The division of labour is deliberate.
Judgement calls — is this paper curatable, what phenotype does this figure describe — are left to
the language model, whereas anything with a correct answer in an external database, such as a
UniProtKB accession or the current status of a PHIPO term, is retrieved by a script that queries the
source directly. The model is prohibited from generating identifiers of any kind.

When several papers are curated in one session, each paper is handled by a separate, temporary copy
of the same assistant, and these run one after another rather than at the same time. The copies are
identical: they receive the same instructions and differ only in which paper they are given. The
purpose is isolation. Curating several papers within one continuous session risks carrying genes,
host species, fungal strains, or figure numbers from one paper into the draft for another, and
giving each paper its own working memory removes that possibility. Each draft is written to disk
before the next paper begins, so an interrupted run retains all completed work. No component of the
system delegates to, queries, or coordinates with another AI component.

## Table 1

**Table 1. Functional modules of PHI-Weaver and their operating mode.** All modules are executed by
one general-purpose language-model agent; they are stages in a pipeline, not independent agents.
Examples are drawn from a validated gold-standard curation of PMID:39787257 (*Knr4/Smi1* in
*Fusarium graminearum* and *Zymoseptoria tritici* on wheat). LLM: ✓ language-model reasoning,
✗ deterministic code, ◐ hybrid (model proposes, code verifies).

| Module | Operating Mode | LLM | Reason | Example |
| --- | --- | :---: | --- | --- |
| PDF conversion | Algorithm-based | ✗ | Text, figure, caption, and table extraction must be reproducible; no interpretation is involved | — |
| Paper triage | LLM-based | ✓ | Judging whether a paper holds curatable PHI data requires reading comprehension over prose and figures | — |
| Gene/protein resolution | Hybrid | ◐ | Model names candidate genes; the accession and function are returned by a UniProtKB query, never generated | A0A1C3YKU0<br>*FgKnr4* |
| Genotype construction | LLM-based | ✓ | Mapping described mutants, complementations, and expression levels onto PHI-base's controlled vocabulary is interpretive | *FgKnr4Δ* |
| Phenotype → PHIPO mapping | Hybrid | ◐ | Model proposes a mapping from the described phenotype; term identity is verified, and `no_match` is returned rather than an approximation | PHIPO:0001020<br>sensitive to calcofluor white |
| Ontology ID validation | Rule-based | ✗ | Existence and obsolescence checks must be transparent, auditable, and identical on every run | PHIDO:0000163 `replaced_by` PHIDO:0000162<br>Fusarium ear blight |
| Annotation assembly | LLM-based | ✓ | Evidence codes, conditions, and extensions follow from the paper's experimental design | PHIPO:0000365<br>decreased pathogen growth within host |
| Gene-for-gene curation | LLM-based | ✓ | Encodes curator methodology (guard/decoy versus direct recognition) that has no algorithmic form | — |
| Curation QC | Hybrid | ◐ | Deterministic checks on accessions and term status, combined with model review of completeness and provenance | 14/14 IDs valid |
| PHI-Canto entry queue | Algorithm-based | ✗ | Built as a deterministic renderer so it cannot invent an accession, term, or evidence code; unresolved genes and everything depending on them are parked automatically | — |
| Progress tracking | Algorithm-based | ✗ | Completion metrics are derived only from explicit structure in the draft, so counts are reproducible | — |
| Benchmark scoring | Rule-based | ✗ | Mechanical checks are prefilled automatically; accuracy and completeness ratings are supplied by a curator, so the system never scores itself | — |

Four of the twelve reusable procedures run on reasoning alone, eight call deterministic tools, and
every identifier that reaches a draft is retrieved from UniProtKB or the EBI Ontology Lookup Service
rather than produced by the model.

## Source of the examples

All example terms come from
[07-Standards/curation-examples/PMID39787257-FgKnr4-cell-wall-stress.md](../07-Standards/curation-examples/PMID39787257-FgKnr4-cell-wall-stress.md),
a validated gold standard imported from PHI-Canto session `02e545aba274d209` (curated by
Hsin-Yu Chang) and re-validated at 14/14 identifiers. Expanded form of each example:

| Module | Input from the paper | Output |
| --- | --- | --- |
| Gene/protein resolution | "*FgKnr4*, gene *FGRAMPH1_01T23707* in *F. graminearum* PH-1" | UniProtKB:A0A1C3YKU0 (and UniProtKB:F9XI26 for *ZtKnr4*, *MYCGRDRAFT_105330*) |
| Genotype construction | "the *FgKnr4* deletion mutant and its complemented control were inoculated onto wheat cv. Bobwhite" | Genotype *FgKnr4Δ*; control *FgKnr4+*[wild-type level]; metagenotype with wild-type *T. aestivum* cv. Bobwhite |
| Phenotype → PHIPO mapping | "increased sensitivity to calcofluor white in a growth assay (Fig 6A)" | PHIPO:0001020, sensitive to calcofluor white (host-scored phenotypes map to PHIPO:0000365) |
| Ontology ID validation | Disease name curated as PHIDO:0000163, "fusarium head blight" | Flagged `is_obsolete: true` offline against the bundled PHIDO ontology and substituted with its `replaced_by` target, PHIDO:0000162, "Fusarium ear blight" (which carries "Fusarium head blight" as an exact synonym) |
| Annotation assembly | Fig 5: *FgKnr4Δ* versus complemented control on wheat spikes, scored at 15 dpi | PHIPO:0000365, evidence macroscopic observation (quantitative), condition 15 dpi, extensions `infects_tissue` spike, `infective_ability` reduced virulence |

The obsolescence catch is the strongest single demonstration in the table: two of fourteen
identifiers in a curator-completed PHI-Canto session were obsolete, and the deterministic check
found both offline — the system correcting a human-curated record, not only its own drafts.

## Caveats for the manuscript

- **Do not describe the plug-in host or GPU-worker deployment as built.**
  [PLUGIN-ARCHITECTURE.md](PLUGIN-ARCHITECTURE.md) and whitepaper §5 mark them as the intended
  destination, explicitly not yet implemented.
- **The model name still has to be filled in.** The provenance footer format is
  `phiweaver · <model> · commit <hash> · date <date>`, but the repository holds only the `<model>`
  placeholder; take the actual string from the benchmark drafts in the external literature store.
- Five modules are blank because PMID:39787257 does not exercise them. Gene-for-gene curation can be
  filled from
  [PMID26177154-Fol-I7-gene-for-gene.md](../07-Standards/curation-examples/PMID26177154-Fol-I7-gene-for-gene.md)
  if the table should carry no gaps, at the cost of drawing on two papers.
