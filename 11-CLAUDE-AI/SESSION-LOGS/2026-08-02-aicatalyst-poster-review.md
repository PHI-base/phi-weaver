---
created: 2026-08-02
type: session-log
tags: [status/complete]
project: AI Catalyst 2026 poster reviewed against the repo, and the benchmark wording pinned down
summary: Second session of the day. Reviewed `Poster-MU16.svg` (A0, Inkscape) for the AI Catalyst 2026 conference. No Inkscape exists in this environment, so the poster was rendered with headless Windows Chrome via an HTML shim and analysed as XML — and **the XML, not the picture, produced nearly every finding**: four rasters below 70 dpi at final size (the PHI-base logo at **31 dpi**), six `preserveAspectRatio="none"` attributes stretching the workflow diagram ~20 % and the stats box ~19 %, and a non-uniform `matrix(0.292, 0, 0, 0.453, …)` squashing the paused-items table to ~65 % glyph width. Hence the standing answer: **send SVG, not PDF**; a PDF is a final print proof only. Checked the poster's claims against the repo rather than reading them: the §3 figure states "7 skills / 14 tools" and "~35 Python modules" where `skills/REGISTRY.md` has **12 skills** and `phiweaver/` has **50 modules**, with five skills missing from the Skills row and `Gold-Standard Import` duplicated across two rows — all frozen in pixels, unreachable by any check. `Benchmark-10-articles-July-2026.md` contradicted the caption's "ten randomly selected articles": the set was deliberately composed. The curator's question about the "13 PHI-Canto categories" resolved to **seven of thirteen** — PHI-Canto has 12 annotation types, the scorecard collapses GO into one row and expression into another, six rows are entity/genotype/evidence fields rather than annotation types, and `gene_for_gene_phenotype` and `post_translational_modification` have **no scorecard row at all**. Final §4 wording agreed over three iterations. The curator applied every mechanical fix themselves; verification of that work nearly produced a false regression report, because raw `x`/`y` attributes inside a transformed group do not describe rendered position — **the render settled it, the coordinates lied**. Captured as `docs/AICatalyst2026-Poster-FAQ.md` with a pointer row in `docs/README.md`. No commits.
---

# Session: review the poster against the repo, not against itself

## Recap

A poster review that kept turning into a **verification** exercise. Almost nothing that mattered
was a matter of taste: the figure was soft because it is 62 dpi at A0, distorted because six
`<image>` elements carry `preserveAspectRatio="none"`, and wrong because its module counts were
baked into pixels months ago and no check can reach them.

Two things generalise beyond this poster. First, **structure beats picture** — the render found
two errors (a duplicated word in the title, a swapped pair of captions), the XML found everything
else, which settles the recurring "shall I send a PDF?" question in favour of SVG. Second,
**a raster figure is a `facts that drift` violation that no tooling can catch**. `docs/README.md`
already says to name the command that prints a count rather than write the number down; the §3
figure writes three counts down in a form where even a human proofreader has no way to check them.

## Objectives
- Review `Poster-MU16.svg` for errors, omissions and print quality before the conference deadline.
- Check the poster's factual claims against the repo rather than accepting them.
- Settle what "accuracy", "completeness" and "13 items" mean in the §4 results panel.
- Capture the outcome where the next person revising a poster will find it.

## Work done

### 1. Rendering an A0 SVG with no Inkscape (method, no commit)

There is **no Inkscape** in this environment — neither in WSL nor on the Windows side. Windows
Chrome (`/mnt/c/Program Files (x86)/Google/Chrome/Application/chrome.exe`) renders it via WSL
interop, but only through an **HTML shim**: pointed straight at the `.svg`, Chrome honours the
841 × 1189 mm intrinsic size and screenshots the top-left corner. Wrapping it in
`<img style="width:1400px;height:1980px">` fixes it; scaling the `<img>` to 2800–4200 px inside a
fixed `overflow:hidden` div gives legible 2–3× crops. Recipe recorded in the FAQ.

### 2. What the XML found that a picture could not

| Finding | Detail |
|---|---|
| Print resolution | 7 of 10 rasters < 100 dpi at final size; PHI-base logo **31 dpi**, stats box **54**, §3 workflow diagram **62**, §5 table **66** |
| Aspect distortion | 6 × `preserveAspectRatio="none"`; diagram stretched ~20 % vertically, stats box ~19 % horizontally |
| Squashed text | Paused-items table under `matrix(0.29235408, 0, 0, 0.45335219, …)` — x and y scales differ, glyphs at ~65 % width, effective 16–18 pt |
| Text sizes | Title 86 pt, headings 32, body 24; §5 rasterised table ≈ **8 pt** at final size |
| Stray objects | A white-on-white `3. Why AI assistance?` heading orphaned by the MU15→MU16 renumbering, and a stray `s` outside the 1400-unit canvas |

DPI was computed by decoding each `<image>`'s PNG/JPEG header for native pixels and comparing
against its placed size in millimetres.

### 3. The poster's claims vs the repo

- **Module counts.** Figure says "7 skills / 14 tools", "~35 Python modules". `skills/REGISTRY.md`
  lists **12 skills**; `phiweaver/` holds **50 modules**. Missing from the Skills row:
  `benchmark`, `canto-entry-queue`, `gene-for-gene`, `inbox-triage`, `ontology-term-request`.
  `Gold-Standard Import` appears in **both** the Skills and Benchmarking rows.
  [PHI-WEAVER-MODULE-TABLE.md](../../docs/PHI-WEAVER-MODULE-TABLE.md) independently says 12.
- **Sampling.** Caption said "ten randomly selected articles".
  `07-Standards/curation-benchmarking/Benchmark-10-articles-July-2026.md` says otherwise: ten
  **already-curated** articles, an 11th (PMID:1799694) dropped as a scanned PDF with no text
  layer, and two 1992 papers included **on purpose** to stress UniProtKB accession resolution.
  A purposive sample, not a random one. Corrected.
- **Unstated strengths.** The blind protocol (network allowlisted to UniProt + EBI OLS, own gold
  standard removed from the retrieval library, one isolated sub-agent per paper), the drafting
  model (Fable 5), and whether a held-out control arm ran — none appear on the poster, though
  they are what pre-empts the leakage question.

### 4. "Accuracy", "completeness", and the "13 PHI-Canto categories"

Definitions taken from `07-Standards/curation-benchmarking/README.md` and `make_scorecard.py`
rather than invented: **accuracy** = points ÷ applicable items (Correct 1 / Needs improvement 0.5
/ Incorrect 0, N/A excluded), human-scored, never self-scored; **completeness** = captured ÷
curatable, deliberately orthogonal — a finding captured under a wrong term takes full completeness
credit and loses accuracy. Two different denominators, so §4 needs two counts, not one; 130 is the
ceiling (13 × 10) before N/A exclusions.

The curator pushed back on my claim that the 13 items are not PHI-Canto annotation categories.
**Partly right, and worth the check.** PHI-Canto has **12** annotation types
(`07-Standards/curation-examples/TAGS.md`, `00-Inbox/for-weaver/Schemas/README.md`). Seven
scorecard rows are annotation types; one collapses the three GO types, another the two expression
types; six rows (UniProtKB ID, species/strain/cultivar, genotype, metagenotype & control, evidence
code, conditions/extensions) are the **fields annotations depend on**, not types; and
`gene_for_gene_phenotype` and `post_translational_modification` have **no row at all**. So the
phrase reads right to a general audience and wrong to a PHI-base-literate one — which is who
stands at this poster.

**Agreed wording**, after three iterations:

> Ten articles spanning diverse pathogen–host systems were curated by PHI-Weaver, then scored by a
> biocurator across 13 PHI-Canto annotation, entity, genotype and evidence items.

Noted, not adopted: "curated by PHI-Weaver" is the one place on the poster where the system
appears to curate outright, against §2 ("AI drafts; the biocurator decides") and §6 ("No record is
released without expert review").

### 5. Verifying the curator's own fixes — where I nearly got it wrong

The curator applied all mechanical fixes (title, six glued words, six typos, three broken
hyphenations, both stray objects, the swapped §6 captions). Re-extracting coordinates suggested
the §6 fix had *moved* both captions into the right-hand box rather than swapping them. **It had
not.** Raw `x`/`y` attributes inside a transformed group do not describe rendered position, and
the two caption blocks sit under different transforms. A 3× crop showed the fix was correct.
Recorded in the FAQ as a standing trap: confirm any layout claim against a render.

### 6. Should the §3 figure be regenerated as an image? (no commit)

Asked whether an image model could have done better. **On polish, yes; on this figure, no** — and
the reasons are structural rather than aesthetic. Every defect follows from it being a raster, and
a generated image has no access to `skills/REGISTRY.md`, which is precisely how five skills went
missing and one box got duplicated. Recommendation: hand-author it as SVG in the poster's own
coordinate system, boxes sourced from the registry so it is correct by construction. Open
question left with the curator: the per-box icons (MIT-licensed set, extract the originals, or
drop them and lean on the number badges and KEY).

### 7. Captured to the vault (no commit)

- **New:** `docs/AICatalyst2026-Poster-FAQ.md` — question-shaped, `See:` pointers rather than
  duplicated detail, per the `docs/FAQ.md` convention. Counts marked as a 2026-08-02 snapshot with
  the live source named, per `facts that drift`.
- **Edited:** `docs/README.md` — new **Outreach artefacts** bullet under "Not canonical, by
  design", so the ownership map stays true.
- `python3 -m phiweaver.vault_names --check` passes; all ten referenced paths resolve.

## Decisions

- **SVG is the review format.** PDF only as a final print proof, because it is Inkscape's own
  output and therefore ground truth for fonts. Everything else favours the SVG.
- **"13 PHI-Canto annotation, entity, genotype and evidence items"** replaces "13 PHI-Canto
  categories" — accurate to the scorecard without over-claiming annotation-type coverage.
- **The §3 figure should be rebuilt as hand-authored SVG**, not regenerated as an image.
- **The poster FAQ is an outreach artefact**, frozen to a date like the manuscript artefacts —
  not a description of the system now.

## Open items

- **Poster content:** conference name and abstract number, funding line with the BBSRC award ID,
  a QR label plus a second QR for the repo, code/data availability, presenting author's email and
  ORCID. Largest gap: **§7 claims "faster curation" and nothing on the poster measures time.**
- **Poster mechanics:** re-export four rasters at ≥150 dpi; strip the six
  `preserveAspectRatio="none"`; make the paused-items scale uniform; trim both §5 tables to two
  contrasting rows. Items 21–22 are contained XML edits and were offered.
- **The realised applicable-item count** for §4 must be summed from the filled scorecards, which
  live outside the repo in the literature store.
- **Two Q/As for `docs/FAQ.md`** (accuracy/completeness; the annotation-types answer) — offered,
  not added. They recur beyond this poster.
- **Icon route** for a rebuilt §3 figure, undecided.

## Lessons

- **The render is authoritative; coordinates are not.** Inside a transformed group, `x`/`y` are
  pre-transform. Nearly cost a false regression report.
- **Structure beats picture for review.** Two findings came from looking; a dozen came from the
  XML. This is the whole argument for SVG over PDF.
- **A raster figure freezes facts where no check can reach them.** `docs/README.md` warns against
  writing counts into prose; writing them into pixels is the same failure with no remedy short of
  regenerating the asset. Applies to any figure carrying a number.
- **Check the pushback rather than conceding or defending it.** The curator's "these are PHI-Canto
  annotation categories" was partly right, and the useful answer was the exact mapping — seven of
  thirteen, with two real types unrepresented — not a verdict.

## Commits

None. Two working-tree changes: `docs/AICatalyst2026-Poster-FAQ.md` (new) and `docs/README.md`
(one bullet). Poster edits were made by the curator in
`/mnt/d/2026-08-01 AiCatalyst2026-weaver-poster/`, outside the repo.
