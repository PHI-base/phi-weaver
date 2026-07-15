# PHI-Canto Curation Conventions (from the team decision log)

**What this is:** durable curation rules the PHI-base/PHI-Canto team settled through
discussion, distilled so phiweaver's drafting and QC logic can follow them. Each rule cites
the issue where it was decided. These are conventions the papers themselves don't state — the
kind of thing a first-time community curator (or an AI draft) gets wrong without being told.

**Provenance:** extracted from the **PHI-base/curation** closed GitHub issue tracker,
collected **2026-07-12**. Issue numbers below (e.g. `#157`) refer to
`https://github.com/PHI-base/curation/issues/<n>`. Where a rule was later folded into the
PHI-Canto manuscript or FAQ, that is noted. Re-verify against the live tracker before treating
any single rule as current — some were reversed at least once before settling.

---

## Scope — what we do and do not curate

- **In scope:** PHI (pathogen–host interaction) phenotype papers, which may include
  single-species phenotypes. (`#115`)
- **Chemistry papers are the exception** — single-species pathogen chemistry phenotypes are
  curated even without a host interaction, but only when the paper contains **lab-engineered
  gene modification** (e.g. amino-acid substitution, overexpression). Focus on pathogenic
  organisms (e.g. *not* *S. cerevisiae*). Keep it Tier-1: the take-home message in the title;
  add more later if needed. (`#115`, `#67`)
- **Do NOT curate — natural-variant-only papers.** Chemistry (or other) papers containing
  *only* natural sequence-variant data are out of scope: there is no engineered change and no
  clear WT control to compare against. (`#115`, `#181`)
- **Do NOT curate — interspecies complementation.** A pathogen genotype cannot contain two
  species, so experiments expressing one species' variant in another (e.g. Mg CYP51 variants
  in *S. cerevisiae*) are not curatable. (`#115`, `#117`)
- **Papers with no gene-specific data are still approved.** Approve the (empty) session so the
  paper isn't re-triaged for curation again; PHI-base 5 is gene-indexed so it simply shows
  nothing. (`#112`)
- **Chemistry paper selection order:** newest papers first (better data, authors reachable),
  working backward — plus the first paper describing each chemical target. (`#115`)

## Evidence codes (GO annotations)

- **TAS (Traceable Author Statement) is enabled for all curators**, not just admins — because
  most PHI-base genes are poorly characterised and no experimental code fits. Prefer an
  experimental code (IDA, etc.) whenever the paper supports one; fall back to TAS otherwise.
  (`#245`)
- **Do NOT use ISS** (Inferred from Sequence or Structural Similarity). It was considered as a
  TAS substitute and **rejected** by the team as too predictive / in-silico in nature; it is
  not enabled in PHI-Canto's GO configuration. (`#246`)

## Allele typing

- **`transformant` is decided by ORIGIN, not method.** Use allele type `transformant` when an
  allele is taken from **strain A and introduced into strain B**. A same-strain
  mutate-and-reintroduce is **not** a transformant — use the mutation-based type (deletion,
  amino-acid substitution, …), or `ectopic expression` for random/plasmid integration.
  (`#157`)
- **Transformant naming standard** (`#157`):
  - allele name: `<gene> transformant` (auto-filled by PHI-Canto);
  - allele description: `<strain>-<gene>(<allele>)` — give the AA change if known, but not for
    a plain wild-type transgene;
  - **background field records the endogenous copy's status:** `endogenous <gene> present`,
    `endogenous <gene> absent` (naturally absent in that strain), or `<gene>delta` (deleted by
    the researchers).
- **Deletion + substitution in one allele** → allele type `partial deletion and amino acid
  change`. (`#16`)
- **Remove `overexpression` from an allele when the experiment is not in-host** — with no
  in-host context it can't be compared to normal WT expression. (`#76`)
- **Signal-peptide removal is NOT pushed to background** — considered and rejected; the assay
  is still looking at the (processed) WT protein. (`#77`)

## Naming & data standardisation
> **Provenance:** curator review (Hsin-Yun Chang, 2026-07-15) on PMID:42089373; logged as **L4**
> in `docs/CURATION-LESSONS.md`. Canonical gene-symbol source (UniProtKB gene name vs. strip the
> species prefix) pending clarification.

- **Gene symbol carries no species prefix.** Use the standard symbol — **`SdhA`**, not `FpSdhA`;
  **`TRI1`**, not `FpTRI1`. The species-specific prefix an author adds (`Fp`, `Fg`, …) is dropped
  for the annotated gene symbol.
- **Deletion genotypes use the Δ-suffix** (gene, then delta): **`SdhAΔ`**, not `ΔFpSdhA`. Applies
  to the double mutant (`SdhC1&2Δ`) and complement controls (`SdhC2Δ-C`).
- **Write "Figure" in full**, not "Fig." (whether this extends to other abbreviations, e.g.
  "Table", is pending confirmation).

## Interaction phenotype — primary term is a measurement; interpretation goes in the extension
> **Provenance:** curator review (Hsin-Yun Chang, 2026-07-15); logged as **L5**.

- The **primary term** of a pathogen–host interaction phenotype must be a **measured / observed**
  phenotype — e.g. `PHIPO:0000365` *decreased pathogen growth within host* (from lesion length /
  disease index / in-host growth).
- An **interpretation** such as "reduced virulence" is **not** the primary term — do **not** use
  `PHIPO:0000015 reduced virulence` as primary. It goes in the **annotation extension** (the exact
  relation/value is pending the PHI-Canto extension vocabulary).
- Choose the measured primary term to match the assay; keep the interpretive outcome in the
  extension.

## Expression levels

- **Never emit `Unknown` expression level** — it was retired. Real cases were almost always
  `not assayed` or `overexpression`; pick the one the paper supports. (`#70`, `#68`)

## WT controls and the "compared to control" model

- **No WT controls for single-species (pathogen) phenotypes.** The altered genotype is
  mentally compared to the reference/strain WT. (`#78`, `#115`)
- **WT controls ARE made for metagenotype annotations** — one control per phenotype — and
  linked from the mutant annotation via the `compared to control` annotation extension.
  (`#78`, `#79`)
- **Combined WT-pathogen / WT-host metagenotypes were tried and abandoned** (Sept 2020). Use a
  `specified-WT-gene` metagenotype instead (e.g. `GT2+(PH1) / WT-Ta(bobwhite)`). (`#78`)
- **`assayed_using` on protein-binding annotations is kept** even though it can duplicate the
  metagenotype's proteins — the assayed proteins are sometimes different from those in the
  metagenotype. (`#88`)

## Phenotype interpretation — effects that may be secondary to a growth / fitness defect

> **Provenance:** phiweaver **working convention**, adopted **2026-07-15** while curating
> PMID:42089373 (FpSdh subunits). **Not yet a PHI-base/curation team decision** — pending
> confirmation with biocurator Hsin-Yun Chang (discussion drafted). Treat as the current
> drafting rule; update the provenance to an issue number once the team settles it.

When a mutant shows a phenotype (e.g. reduced/abolished mycotoxin, altered pigment, lost
sporulation) **and** is also severely growth- or fitness-impaired, the phenotype may be a
downstream consequence of poor growth rather than a specific role of the gene. Rule:

- **Still annotate the observed phenotype.** Curation records what was observed; do not drop a
  real, figure-backed phenotype just because the mutant also grows poorly. Use the correct PHIPO
  term + evidence code.
- **Judge growth-independence from the experiment, and record it in the annotation comment.**
  Treat the phenotype as a **specific, growth-independent** effect (high confidence) when any of:
  the mutant grows **normally**; the readout is **normalised to biomass** (e.g. per mg dry
  weight); or **complementation restores** it.
- **When the phenotype co-occurs with a severe growth/fitness defect and is not separated** (no
  normal-growth comparison, not biomass-normalised, no rescue), annotate it **with an explicit
  comment that it may be pleiotropic / secondary to the growth defect**, and flag it for the
  curator. Do **not** present it as a direct/specific function.
- **Do not assert a specific molecular/biological function** (e.g. a GO annotation) on the basis
  of a growth-confounded phenotype alone.
- **Caveat on biomass normalisation:** normalising to dry weight strengthens confidence but does
  **not** fully exclude pleiotropy when the deleted gene is **core metabolism / respiration** — a
  cell that cannot respire may fail to make an energy-expensive secondary metabolite for reasons
  downstream of losing central metabolism, not a specific pathway role.

**Worked example (PMID:42089373, DON):** ∆FpSdhC2 loses DON with **normal growth**, a
biomass-normalised GC-MS readout, and complementation rescue → `PHIPO:0001445` (decreased level
of deoxynivalenol) annotated **with confidence**. ∆FpSdhA / ∆FpSdhB / ∆FpSdhD and the ∆FpSdhC1&2
double show **no detectable DON but are severely growth-impaired** (Sdh = core respiration) →
`PHIPO:0001445` annotated **with a "may be growth-secondary" comment**, flagged for the curator.

## Gene-for-gene and PHIPO_EXT

- **PHIPO_EXT terms are extension-only — NEVER a primary annotation term.** They belong in the
  `gene_for_gene_interaction` annotation extension; the primary term must be a PHIPO term.
  Using PHIPO_EXT as a primary term breaks the PHI-base 5 display and is flagged as a curation
  **error**. (`#249`)

## Disease name

- **Disease name is its own curation type**, attached to WT compatible/susceptible
  metagenotypes — **natural host + visible disease only**, all strain combinations, all WT
  genes, with tissue from BTO. (`#49`)
- **Do not apply a disease name** when no disease is observed, or on a non-natural host — e.g.
  don't use "rice blast" on a barley assay, or any disease name for effectors heterologously
  expressed in tobacco. (`#49`)

## Physical-interaction assays

- **BiFC → use interaction type `PCA`** (Protein-Fragment Complementation Assay) and note
  "BiFC" in the comment. PHI-Canto deliberately does not diverge from the BioGRID controlled
  vocabulary of interaction types, and BiFC is a PCA sub-type. (`#229`)

## Not needed / non-actions worth knowing

- **No special mechanism to "add an important background reference"** — PHI-base 5 already
  lists all papers for a gene together, by year, so the original and derived papers appear
  side by side. (`#215`)

---

## Open threads (were unresolved at collection date 2026-07-12)

- **Diploid mode:** enabled and used for a few *Candida albicans* chemistry sessions, but
  PHI-base 5 display support was unresolved; the interim workaround is to report diploid status
  in the background field. When/whether to use it beyond chemistry was still being written up.
  (`#169`, `#116`, `#127`)
- **Curating genotypes from genetic crosses:** raised, no decision reached. (`#134`)
- **`with_host_peptide` extension** is for a peptide's protein sequence (UniProt accession +
  residue range), not a generic "host peptide" — a possible rename to "with host peptide
  sequence" was discussed. Added ETI/PTI inducers go in **PHI-ECO**, not as bespoke extensions.
  (`#251`, `#230`)
