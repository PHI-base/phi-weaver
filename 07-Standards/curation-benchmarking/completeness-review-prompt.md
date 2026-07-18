---
created: 2026-07-10
type: standards
tags: [standards]
project: PHI-Canto
---

# Completeness-scoring prompt (for the GPT reviewer)

Use this when you want a completeness score but have **no finished PHI-Canto gold standard** —
the reviewer builds the reference annotation list **directly from the paper**, then scores the
draft against it.

Paste the text below to the reviewer, then attach the two inputs for ONE paper:
1. the **paper** (PDF or full text), and
2. **phiweaver's draft** for the same paper (`*-phiweaver-DRAFT.md`).

(If you *do* have an accepted PHI-Canto curation, attach it too and tell the reviewer to use it
as the reference instead of enumerating — or to reconcile its own list against it.)

Run once per paper. Copy the three numbers into that paper's scorecard Completeness block
(Curatable items in the paper / Items captured in the draft / Items missed).

---

You are a second biocuration reviewer scoring the **completeness** of an automated PHI-Canto
draft. Completeness measures coverage — *of everything that should have been curated from this
paper, what fraction did the draft capture?* It is separate from accuracy (whether each captured
item is correct); do not score accuracy here.

**Inputs**
- PAPER: the full text / PDF of the publication — this is your source of truth.
- DRAFT: phiweaver's automated draft for the same paper.

**Work in two phases, in this order. Do PHASE A from the PAPER alone — do not read the DRAFT
until PHASE B.** Reading the draft first would anchor your reference list to what the tool
happened to produce and inflate the score; the reference must come from the paper independently.

---

### PHASE A — Enumerate the curatable annotations from the PAPER

Read the paper and list every annotation a PHI-Canto curator should make. This list is the
denominator ("curatable items in the paper").

**Counting unit: the annotation** = one ontology term attached to one genotype or metagenotype,
supported by one experimental result. So:
- One mutant showing three distinct phenotypes = **three** annotations.
- The same phenotype shown for two different alleles/genotypes = **two** annotations.
- A gene with a molecular function *and* a biological process *and* a cellular component =
  **three** GO annotations.

**What is curatable (the 12 PHI-Canto annotation types)** — enumerate any that the paper
supports with experimental data:
| Type | Curate when the paper shows… |
|------|------------------------------|
| `pathogen_host_interaction_phenotype` | a pathogen genotype × host result (e.g. altered virulence/lesion/colonisation in planta or in an animal host) |
| `pathogen_phenotype` | a single-species pathogen phenotype in vitro (growth, morphology, stress/chemical sensitivity, sporulation…) |
| `host_phenotype` | a phenotype of a manipulated **host** gene in the interaction |
| `gene_for_gene_phenotype` | an avr × R (resistance-gene) recognition outcome |
| `biological_process` / `molecular_function` / `cellular_component` | GO annotations experimentally supported for the gene/protein (process, activity, localisation) |
| `physical_interaction` | a demonstrated protein–protein (or protein–nucleic-acid) interaction (Y2H, co-IP, pulldown, BiFC…) |
| `post_translational_modification` | an experimentally shown PTM (phosphorylation, ubiquitination…) at a defined residue |
| `wt_rna_expression` / `wt_protein_expression` | measured wild-type RNA / protein level or localisation pattern |
| `disease_name` | the disease studied, tied to the pathogen–host system |

**Scope rules — count only what the DATA show:**
- Only genes/proteins that are **experimentally characterised or measured** here — deletion,
  overexpression, complementation, point mutation, RNAi, localisation, interaction, expression.
  **Do not** count genes merely mentioned, cited from other papers, or named only for pathway
  context.
- Each annotation needs an **entity + an experiment + a result** that maps to an ontology term.
- Include **negative / unchanged** results if the paper establishes them experimentally (they
  are curatable as "normal / unaffected" annotations).
- Do **not** count speculation, models, or introduction/discussion claims that are not backed by
  this paper's own experiments.
- When unsure whether something is one annotation or several, state your splitting decision.

Output PHASE A as a numbered list: `#. gene/protein · annotation type · finding (figure/table)`.

---

### PHASE B — Match the DRAFT against your PHASE-A list

Now read the DRAFT. For each PHASE-A annotation, decide whether the draft produced an equivalent
one. **Equivalent = same gene/protein + same annotation type + same biological finding.**

- **Present-but-wrong still counts as captured.** If the draft made the annotation but chose a
  slightly wrong ontology term, it *captured* the finding (completeness credit) — the term error
  is an accuracy issue scored elsewhere. Do not penalise it here.
- **Extra draft annotations not in your PHASE-A list do NOT raise completeness.** They are
  over-curation / false positives (a precision concern) — OR a genuine curatable item you missed
  in PHASE A. If, on reflection, an "extra" really is curatable from the paper, add it to the
  PHASE-A list (increasing the denominator) rather than silently crediting it. Never let extras
  push completeness above 100%.
- Be conservative: if you cannot find a clear draft equivalent, mark it **missed**, not captured.

---

### Output exactly this

```
Paper: <title / PMID>

PHASE A — curatable annotations from the paper:
1. <gene · type · finding (fig/table)>
2. ...

Curatable items in the paper: <N>
Items captured in the draft:  <M>
Items missed:                 <N − M>
Completeness:                 <round(M/N*100)>%

Match table:
| # | Curatable annotation (gene · type · finding) | In draft? | Draft equivalent / note |
|---|----------------------------------------------|-----------|-------------------------|
| 1 | ...                                          | yes/no    | ...                     |

Missed (curatable, absent from draft):
- ...

Extra in draft (not curatable from the paper — precision note, does not affect completeness):
- ...

Assumptions / borderline calls:
- ...
```
