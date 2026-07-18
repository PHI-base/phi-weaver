---
created: 2026-07-15
type: documentation
tags: [docs]
project: PHI-Weaver
---

# Curation Lessons — feeding curator feedback back into weaver

**What this is:** a running log of **general** curation lessons — rules that should improve
*every* future draft, not just one paper — and a trail of where each was folded into the pipeline.
The log is **intake + provenance**; the actual behaviour change lives in what weaver reads at
drafting time:

- **Rules** → `07-Standards/PHI-Canto-Curation-Conventions.md` and the relevant `skills/`.
- **Worked examples** → the validated gold-standard library (`07-Standards/curation-examples/`).
- **Tool / ontology gaps** → `docs/BACKLOG.md`.

A lesson that is logged but never folded into one of those changes nothing about the next draft —
the **"Applied to"** column is the point.

## Sources & type tags
Every row carries a **Type** tag so you can see at a glance where a lesson came from and how much
traceability it has (strongest → weakest provenance):

- `issue` — a GitHub issue discussion (permalink + open/closed status). Our own issues to the
  curator, or the `PHI-base/curation` tracker mined for team decisions (see D17).
- `paper-review` — a curator's review of a specific paper's draft (e.g. Hsin-Yun on PMID:42089373);
  ties back to that draft. Log only the *generalizable* points; paper-specific fixes go to the
  draft, not to this log.
- `meeting` / `email` — **freeform** discussion (a call, a hallway chat, a mail thread): no
  permalink, usually a paraphrase — the weakest provenance, see the guardrail below.
- `note` — an internal proposal from weaver's own drafting, pending curator confirmation.

## Guardrails (mainly for issue-sourced lessons)
- **Only fold in resolved / closed decisions.** An open thread may be wrong or get superseded —
  keep it `open` in the log and do not apply it yet.
- **Distill into our own words + a `See: #n` pointer** (matches the D17 provenance style), rather
  than pasting the issue.
- **GitHub is a benchmark-leakage source.** The distilled convention is fine, but keep the raw
  issue out of blind / scored runs (see the "PHI-Canto issues tracker — mine, don't ingest"
  backlog item).
- **Freeform sources (`meeting` / `email` / `note`) are intake, not authority.** Record *who* said
  it and *when*, and treat the wording as a paraphrase. A freeform lesson can drive a draft or
  skill tweak, but before it becomes a **stated rule** in the conventions doc give it a citable
  basis — get the curator's sign-off (recorded) or promote it to a GitHub issue that resolves — so
  every convention keeps a verifiable source, per the conventions-doc provenance rule. Don't
  enshrine a half-remembered hallway comment as a rule.
- **Never delete or overwrite a row — the log is append-only.** When a lesson changes, revise its
  status and add a superseding row (see *Revising a lesson* below). Statuses:
  `open` → `applied`, and later `revised` / `superseded` / `withdrawn`. When `applied`, cite where.

## Revising, withdrawing, or reversing a lesson
Conventions are not permanent — the team (or we) may change our minds, and a rule can be reversed
or refined later. This pipeline handles that cleanly **because weaver learns by reading rules and
examples, not by training**: there is no baked-in model weight to unlearn, so reversing a decision
is just an edit the next draft immediately follows, fully auditable. To change a lesson:

1. **Keep the ledger append-only.** Don't delete or rewrite the old row — set its Status to
   `superseded` / `withdrawn` / `revised` and add a **new row** carrying the current rule, noting
   `supersedes L<n>` (and back-link the old row `→ L<m>`). The evolution stays visible.
2. **Update the durable home the same way.** In the conventions doc, mark the old rule superseded
   in place (date + reason + pointer to the new rule) rather than silently rewriting it; cite what
   reversed it (issue #, lesson id, or curator sign-off).
3. **Propagate.** A changed convention ripples to the **skills** that encode it, and possibly to
   **past curations** made under the old rule — flag affected papers for re-curation (the
   recuration-comparison workflow) if the change is material.
4. **Git is the backstop.** Every edit to the log, conventions doc, skills and examples is in git
   history, so you can always see what a rule was, when it changed, and revert — the docs carry the
   human-readable *why*, git carries the exact diff.

## Log
_Append-only; `ID` is a stable handle so later rows can `supersede` earlier ones._

| ID | Date | Type | Source | Lesson (general rule) | Applied to | Status |
| --- | --- | --- | --- | --- | --- | --- |
| L1 | 2026-07-15 | note | weaver draft; surfaced curating PMID:42089373 (to confirm w/ Hsin-Yun) | A phenotype that co-occurs with a **severe growth/fitness defect** must be annotated but either justified as growth-independent (normal growth / biomass-normalised readout / complementation rescue) or flagged as possibly pleiotropic; assert **no GO function** from a growth-confounded phenotype alone. | Conventions doc "Phenotype interpretation" section + `curation-qc` step-7 check | applied (pending curator confirmation) |
| L2 | 2026-07-15 | issue | Drafted issue — DON/mycotoxin | DON / mycotoxin changes **are** curatable as PHIPO phenotypes (`PHIPO:0001445` etc.) — not a term gap. **Weaver behaviour:** when a phenotype phrase returns `no_match`, retry the "level of X" / "abnormal X biosynthesis" wording before declaring a gap. | `docs/BACKLOG.md` (lesson recorded) + Sdh draft remapped; **`phipo-mapping` skill step 7** (retry "level of X" / "abnormal X biosynthesis" before calling anything a gap, then hand to `ontology-term-request`) | **applied — fold-in complete** (status corrected 2026-07-17: previously read "skill note open", but the note had landed). **Re-verified 2026-07-17** against the now-offline PHIPO (`phipo-base.obo`, release 2026-03-12) after the search moved off OLS and the scorer changed: the premise still bites ("DON production was abolished" → `no_match`) and both retries still work — "level of deoxynivalenol" → PHIPO:0001445, "abnormal deoxynivalenol biosynthesis" → ★ PHIPO:0001443 exact. Generalised by **L8** (species-neutral + process→entity are two *systematic* instances of this same shape). |
| L3 | 2026-07-15 | issue | Drafted issue — GO evidence; resolved 2026-07-17 by Hsin-Yun Chang (`phi-weaver#8`) | When a paper gives **no biochemical evidence** (only knockout phenotypes), annotate **both**: the **MF by TAS** where the authors explicitly state the function and it matters to the experimental design, **and** the **BP terms the deletions demonstrate, by IMP**. TAS rests on the author's statement, **not** on UniProt carrying the term — UniProt GO is largely IEA pipeline prediction, so bulk transfer is excluded. Focus stays on experimentally verified annotations. | Conventions doc "Evidence codes (GO annotations)" — two rules added next to the ISS/TAS entries | applied — ruling received |
| L4 | 2026-07-15 | paper-review | Hsin-Yun Chang, PMID:42089373 | **Data standardisation:** gene symbol carries no species prefix (`SdhA`, not `FpSdhA`); deletion genotypes use the Δ-suffix (`SdhAΔ`, not `ΔFpSdhA`); write "Figure" in full, not "Fig." | Conventions doc "Naming & data standardisation" + `genotype-creation` + `curation-qc`; applied to the Sdh draft | applied (canonical gene-symbol source pending D1) |
| L5 | 2026-07-15 | paper-review | Hsin-Yun Chang, PMID:42089373 | **Interaction primary term is a measurement, not an interpretation:** use a measured term (e.g. `PHIPO:0000365` decreased pathogen growth within host) as primary and put "reduced virulence" in the annotation extension — not `PHIPO:0000015` as primary. | Conventions doc "Interaction phenotype …" + `phenotype-annotation` + `curation-qc`; applied to the Sdh draft. Extension resolved from PHI-Canto config (`phipo_extensions.tsv`): relation is `infective_ability`, value is the term ID `PHIPO:0000015` (under `PHIPO:0001179`), validated offline by `extension_config.py`; attested-relations table in `Ontology-Terms-Reference.md`. | applied — extension relation `infective_ability` + value `PHIPO:0000015` confirmed & validated offline |
| L6 | 2026-07-15 | paper-review | Hsin-Yun Chang, PMID:42089373 | **Conditions must use the controlled vocabulary (PHI-ECO, prefix `PECO:`):** weaver's free-text conditions (media/temp/duration) won't pass final approval. Treat conditions as advisory until PHI-ECO is vendored (mirror the PHIDO fix). | `validate_ontology_ids` validates `PECO:` offline (vendored `phi-eco.obo`); `map_condition` lookup + `phenotype-annotation`/`curation-qc` wiring; reference in `07-Standards/Ontology-Terms-Reference.md` | applied — validation + generation; drafts emit PECO Condition terms (PHI-ECO is qualitative, so numeric specifics stay in the comment at curator granularity) |
| L7 | 2026-07-17 | note | surfaced building the gap ledger; verified live against PHIPO/OLS | **A confident PHIPO match can be contextually impossible.** A free-living (in-vitro) phenotype search returns in-host terms with nothing marking them: `absent DON` in culture matches `PHIPO:0000234` *pathogen deoxynivalenol within host absent* — the very term PHI-base/phipo#452 rejects as wrong-context. **Declare the assay context** (`map_phenotype --assay-context free-living\|in-host`); PHIPO states context in the label (`within host`, `on host surface`). **And a surviving candidate is not a fitting candidate:** the same search also returns `PHIPO:0000939 asexual spore lysis absent` — host-free, so unflagged, and irrelevant to DON. Read every survivor against what the paper measured. **Corollary:** gap detection cannot be automated — `no_match` misses wrong-context gaps entirely, and one irrelevant host-free candidate masks them. The ledger under-counts, so a quiet report is not evidence of a complete ontology. | `phiweaver/lookup/term_context.py` (guard) + `map_phenotype --assay-context`; `phipo-mapping` workflow steps 4–5 + QC check; new `ontology-term-request` skill; ledger `docs/ontology-gaps.jsonl` via `gap_log.py`. Skills only — deliberately **not** in the conventions doc, per the freeform-source guardrail. | applied (skills only) — **two claims of different strength.** *Verified:* the label rule + the #452 wrong-context failure, checked live against PHIPO/OLS. *Weaver's proposal, pending curator confirmation:* the binary `free-living`/`in-host` assay-context split — no curator has ruled on it, and it may be too crude for detached-leaf or cell-culture assays. Raise with Hsin-Yun; if a third context is needed, supersede this row. |
| L8 | 2026-07-17 | curator ruling | Martin, closing the "complete loss of conidiation" backlog gap | **A phenotype phrase can miss PHIPO twice over on wording alone, and both misses are systematic — not bad luck.** PHIPO is **species-neutral by design** (a term must hold across pathogens), so a curator's own vocabulary misses the primary labels; and for presence/absence PHIPO models the **entity**, not the process. Natural phrasing ("conidiation abolished") misses on **both axes at once**, which reads exactly like a gap. **Curator ruling: the entity being absent covers the process having failed — they are not distinct phenotypes.** L2's shape, systematised. Already cost one false gap. | **Canonical: `ontology-term-request` skill, "not a gap" #1** — the two retries, the vocabulary, and the release-specific caveat live there. Also: `docs/BACKLOG.md` (false gap corrected + closed); memory `phipo-is-species-neutral`. | applied — **the ruling is the curator's; the vocabulary claims are verified** against `phipo-base.obo` (release 2026-03-12). |
