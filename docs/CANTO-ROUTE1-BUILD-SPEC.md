# Build spec — Route 1: PHI-Canto assisted-entry worksheet

**Status:** scoped, not built (2026-07-06). Route 1 of [[CANTO-SUBMISSION-ROUTES]] (recommended
first step). Works with a curator web login only — no server access or write API needed.

**Goal:** turn each phiweaver draft (`/mnt/z/PHI-Canto-Literature/active/*-phiweaver-DRAFT.md`)
into an ordered checklist that a biocurator enters into <https://canto.phi-base.org/>, submitting
the paper for biocurator review.

## Validation model — the entry step *is* the validation

The biocurator **entering the worksheet into the PHI-Canto website is itself the validation**.
There is no separate "review the draft" gate to build: as the curator transcribes each item into
Canto, they apply their judgment, Canto's controlled vocabularies / autocompletes / dependency
constraints force verification, and any draft error surfaces at the point of entry. The worksheet
is a transcription aid, not an auto-submitter; the human is unavoidably in the loop. The checkbox
per item doubles as the record that a curator vetted it. AI drafts therefore never enter the
biocurator queue unreviewed — the queue is reached only *through* a human curator's entry.

## What it produces

Per draft, one **ordered, dependency-respecting Markdown checklist** mirroring PHI-Canto's exact
entry sequence, so the curator works Canto and the worksheet side by side, top to bottom. Ordering
matters because Canto enforces the dependencies (no genotype before its allele; no metagenotype
before both genotypes). Example (TOX2 draft, PMID:41020836):

```
# PHI-Canto entry worksheet — PMID:41020836  (FpTox2 · F. pseudograminearum × wheat)
Model: Fable 5 · ⚠ 7 flags to resolve before entry (see end)

## 1. Genes  (Curation ▸ add gene)
- [ ] FpTox2 — organism Fusarium pseudograminearum — id UniProtKB:K3V6Z9  (locus FPSE_10647)
      ⚠ accession is strain CS3096; experimental strain is 2035 — confirm

## 2. Alleles
- [ ] ∆FpTox2              — gene FpTox2 — type deletion   — expression null
- [ ] FpTox2(reintroduced) — gene FpTox2 — type wild type — expression wild-type level

## 3. Genotypes
- [ ] wild type 2035  (control)
- [ ] ∆FpTox2         (allele: ∆FpTox2)
- [ ] ∆FpTox2-C       (allele: FpTox2 reintroduced)

## 4. Metagenotypes  (pathogen genotype × host genotype)
- [ ] ∆FpTox2 × T. aestivum cv. Shixin 828        — EXPERIMENTAL
- [ ] wild type 2035 × T. aestivum cv. Shixin 828 — CONTROL
- [ ] ∆FpTox2-C × T. aestivum cv. Shixin 828       — COMPLEMENTATION CONTROL

## 5. Annotations
### 5a Pathogen phenotype — genotype ∆FpTox2
- [ ] decreased hyphal growth — PHIPO:0001212 — ev: cell growth assay — PDA 25°C 3d — Fig 2A,B
- [ ] decreased asexual spores — PHIPO:0000052 — ev: cell growth assay — CMC — Fig 2C
      … (one row per phenotype)
- [ ] ⚠ reduced DON production — NO PHIPO TERM (flag) — resolve before entry
### 5b Pathogen–host interaction — metagenotype ∆FpTox2 × wheat
- [ ] reduced virulence — PHIPO:0000015 — ev: macroscopic observation
      extensions: infects_tissue=coleoptile/stem base; infective_ability=reduced virulence;
                  compared_to_control=wild type 2035, ∆FpTox2-C — Fig 5
### 5c Disease name — metagenotype wild type 2035 × wheat
- [ ] Fusarium crown rot — PHIDO:0000161 — Fig 5

## 6. Submit
- [ ] all flags resolved  - [ ] submit session for approval
```

## The gating decision — where the worksheet's data comes from

The draft's machine-readable `json` block holds only check results + flags, **not** the
genes/alleles/genotypes/annotation content (that is in the prose body + annotation tables). The
generator needs a reliable source:

- **Option A — add a structured `canto` block to the draft (recommended).** Extend the draft JSON
  with a `canto` object (`genes / alleles / genotypes / metagenotypes / annotations`). A
  **deterministic** `worksheet.py` renders it. The block is filled by the drafting agent (LLM does
  the prose→structure step, where it is strong); code renders (testable, reproducible). Also
  advances the backlog "converge draft body toward PHI-Canto shape" item.
- **Option B — LLM-only skill, no parser.** Fast on existing drafts but non-deterministic and
  **likely violates the skill contract** (smoke enforces `backing_script` + tests). Not clean here.
- **Option C — regex-parse the current prose/tables.** No draft changes, but brittle to phrasing.

**Recommend A** — only option that is both testable and contract-compliant, and it doubles as the
body-convergence work.

## Components (package + skill layout)

- `phiweaver/canto/worksheet.py` — `draft.md → Markdown worksheet`; reads the `canto` block, emits
  the ordered checklist, surfaces flags at the top.
- `tests/test_canto_worksheet.py` — network-free unit tests (block → expected worksheet). Edge
  cases: no metagenotypes, missing UniProt, control-only paper, a flagged missing term.
- `skills/canto-worksheet/SKILL.md` — "when to use" + frontmatter naming `worksheet.py` + the test;
  registered in `skills/REGISTRY.md` (smoke's 7th check enforces this).
- `_TEMPLATE.md` — add the `canto` block to the schema + document it.
- Small addition to the drafting workflow so future drafts fill the block.

## Phases & rough effort

1. **Schema** — define + document the `canto` block, extend the template. *Small.*
2. **Generator + tests** — `worksheet.py` + tests; ordering/dependency logic is the substance. *Medium.*
3. **Skill + registry + smoke.** *Small.*
4. **Back-fill the 10 existing drafts** — populate each `canto` block from its prose (LLM-assisted,
   carrying existing flags), then generate all 10 worksheets. *Medium.*

Total: a couple of focused sessions.

## Gotchas the build must handle

- **Evidence codes** — Canto restricts evidence codes per annotation type to a controlled list;
  drafts use free text ("cell growth assay", "macroscopic observation"). v1: **flag** mismatches
  for the curator; map to Canto's allowed display names later (a small `canto/evidence_codes.py`).
- **Gene identifier type** — confirm Canto's add-gene step expects the **UniProtKB accession**;
  worksheet presents the exact string to paste.
- **Extensions** — format Canto's structured relations (`infects_tissue`, `infective_ability`,
  `compared_to_control`) as the tool expects; drafts already use these names.
- **Term strings** — include term ID **and** exact term name so the autocomplete finds it.

## Open questions

1. **Output format** — Markdown checklist (recommended; renders in the vault) vs printable HTML vs
   spreadsheet.
2. **Gene identifier** — confirm UniProtKB accession is what Canto's add-gene step takes (curator
   knows from hand-curation; can also verify against the Canto tutorial).
3. Evidence-code mapping now vs flag-only in v1 (spec assumes flag-only in v1).
