---
created: 2026-08-02
type: documentation
tags: [docs, poster, outreach, benchmarking]
project: PHI-Weaver
---
```table-of-contents
```
# AI Catalyst 2026 poster — review FAQ

*A human-facing record of one poster review (2026-08-02).*

Question-shaped record of what was found and decided while reviewing the **AI Catalyst 2026**
PHI-Weaver poster, plus the method used to review it. Two audiences: whoever revises this poster
next, and whoever reuses the wording about the July 2026 benchmark in a talk, abstract or figure
legend.

**Outreach artefact, not system documentation.** Measurements below are frozen to
`Poster-MU16.svg` as it stood on 2026-08-02. For what the system does now see
[OVERVIEW.md](OVERVIEW.md); for the live module inventory, `skills/REGISTRY.md`.

---

## The poster file

### Where is the poster and what are its dimensions?
`/mnt/d/2026-08-01 AiCatalyst2026-weaver-poster/Poster-MU16.svg` — **A0 portrait**, 841 × 1189 mm,
`viewBox` 1400 × 1980 user units, so **1 unit ≈ 0.6 mm** and a font size in units converts to
points as `px × (841/1400) / 0.3528`. Authored in Inkscape 1.4.4 across six named layers
(background, section panels, figures, main text, title/authors, logos/QR). Earlier drafts
`MU12`–`MU15` sit in the same folder.

### Which sections does it have?
Left column 1–2, right column 3–7: (1) Why does PHI-base need AI assistance, (2) design
principles, (3) the AI system from article to curated record, (4) outputs and early performance,
(5) two kinds of output, (6) safeguards, (7) conclusions. MU15 numbered these 1, 2, 5, 6, 7, 8, 9
with gaps; MU16 renumbered them and the column-major reading order is now correct.

---

## Reviewing a poster without Inkscape

### How do I see the poster if Inkscape isn't installed?
There is **no Inkscape in this environment** — not in WSL, not on the Windows side. Render with
headless Chrome instead. Wrap the SVG in an HTML shim first, or Chrome renders it at its
intrinsic millimetre size and you capture only the top-left corner:

```bash
cd "/mnt/d/2026-08-01 AiCatalyst2026-weaver-poster/"
cat > _render.html <<'EOF'
<html><body style="margin:0"><img src="Poster-MU16.svg"
  style="width:1400px;height:1980px;display:block"></body></html>
EOF
"/mnt/c/Program Files (x86)/Google/Chrome/Application/chrome.exe" \
  --headless=new --disable-gpu --hide-scrollbars --window-size=1400,1980 \
  --screenshot="D:\...\_full.png" "file:///D:/.../_render.html"
```

For a legible crop, scale the `<img>` up (e.g. `width:2800px`) and offset it with
`position:absolute; left:-Xpx; top:-Ypx` inside a fixed-size `overflow:hidden` div.

### SVG or PDF — which should be sent for review?
**SVG.** Nearly every finding in this review came from the XML, not the picture: effective print
DPI, aspect-ratio distortion, non-uniform text scaling, font sizes in points, stray objects, and
a text diff against the previous draft. None of that survives into a PDF. The SVG also renders
fine (above), so it loses nothing. A PDF adds exactly one thing — it is Inkscape's own output
rather than Chrome's, so it is the ground truth for fonts and for what reaches the printer. Treat
it as a final print proof, not a review format.

### How do I diff two drafts?
Extract every `text`/`flowRoot` with its coordinates and sort by position, then diff the two
listings. Beware two traps: text inside a transformed group has raw `x`/`y` attributes that do
**not** match its rendered position, and a wrapped line split across `tspan`s looks like a
mid-word break when the tspans are joined. **Confirm any layout claim against a render.** One
finding in this review (a swapped pair of caption bodies) was true, and a later re-check of the
same coordinates suggested a regression that the render disproved.

---

## Benchmark wording (section 4)

### What does "accuracy" mean?
Per paper, **points ÷ applicable items**: Correct = 1, Needs improvement = 0.5, Incorrect = 0,
Not applicable excluded from the denominator. The rating column is filled by a **human curator**
against their own completed PHI-Canto curation — phiweaver never scores its own draft.
**See:** `07-Standards/curation-benchmarking/README.md` (Scoring); `make_scorecard.py`.

### What does "completeness" mean?
**Captured ÷ curatable** — a separate block counting curatable items in the paper, items captured
in the draft, and items missed. It measures coverage only, and is deliberately orthogonal to
accuracy: a finding captured under a slightly wrong ontology term takes **full completeness
credit** and loses accuracy instead. Extra draft annotations that aren't curatable from the paper
don't raise it, so it cannot exceed 100 %.
**See:** `07-Standards/curation-benchmarking/completeness-review-prompt.md` (lines 88–95).

### Are the "13 items" PHI-Canto annotation types?
**Partly — seven of thirteen.** PHI-Canto has **12** annotation types (`molecular_function`,
`biological_process`, `cellular_component`, `physical_interaction`,
`post_translational_modification`, `wt_rna_expression`, `wt_protein_expression`,
`pathogen_phenotype`, `host_phenotype`, `pathogen_host_interaction_phenotype`,
`gene_for_gene_phenotype`, `disease_name`). The scorecard's 13 items overlap but are not that
list: one row collapses the three GO types and another collapses the two expression types; six
rows (UniProtKB ID, species/strain/cultivar, genotype, metagenotype & control, evidence code,
conditions/extensions) are **not** annotation types but the entity, genotype and evidence fields
annotations depend on; and `gene_for_gene_phenotype` and `post_translational_modification` have
**no scorecard row at all**. Calling them "13 PHI-Canto annotation categories" invites a
PHI-base-literate reader to count and ask where gene-for-gene went.
**See:** `07-Standards/curation-examples/TAGS.md` (annotation_types);
`00-Inbox/for-weaver/Schemas/README.md` (Annotation types);
`07-Standards/curation-benchmarking/make_scorecard.py` (lines 115–127).

### Agreed poster wording
> Ten articles spanning diverse pathogen–host systems were curated by PHI-Weaver, then scored by
> a biocurator across 13 PHI-Canto annotation, entity, genotype and evidence items.

Optional unpacking of the noun pile: *"…across 13 items — PHI-Canto annotation, entity, genotype
and evidence."* Noted but not adopted: "curated by PHI-Weaver" is the one place on the poster
where the system appears to curate outright, against §2 ("AI drafts; the biocurator decides") and
§6 ("No record is released without expert review"); "drafted by" would align the three panels.

### How many field-level judgements is that?
**130 maximum** (13 items × 10 papers), minus every "Not applicable". The realised figure is the
sum of the **"Applicable items"** cell across the ten filled scorecards. Completeness has a
*different* denominator — the sum of "curatable items in the paper". Two numbers, not one. The
filled scorecards live outside the repo in the literature store; `scorecards_to_csv.py` →
`phiweaver.benchmark_report` totals them.

### Were the ten articles randomly selected?
**No** — and an early poster draft said "ten randomly selected articles", which was corrected.
They were ten **already-curated** PHI-Canto articles, deliberately composed: an 11th (PMID:1799694)
was dropped as a scanned PDF with no text layer, and two 1992 papers were included on purpose to
stress UniProtKB accession resolution, which the run identified as the biggest gap.
**See:** `07-Standards/curation-benchmarking/Benchmark-10-articles-July-2026.md`.

### What else belongs in section 4 but isn't there?
- **The blind protocol** — network allowlisted to UniProt + EBI OLS only, PHI-base/PHI-Canto/
  GitHub unreachable, each paper's own gold standard removed from the retrieval library, one
  isolated sub-agent per paper so no entity bleed. Few AI-for-curation posters can claim this and
  it pre-empts the leakage question. **See:** `07-Standards/curation-benchmarking/README.md`
  (Benchmark integrity).
- **The drafting model** (Fable 5). The benchmarking README states model is part of what the
  benchmark measures.
- **Whether a held-out control arm was run.** The design expects curated and control reported
  side by side.

---

## System counts in the section 3 figure

### Why does the figure undercount the system?
The figure is a **raster**, so its labels are pixels. It states "7 skills / 14 tools" and
"approximately 35 Python modules"; as of 2026-08-02 the repo has **12 skills** and **50 modules**
under `phiweaver/`. Five skills are absent from the Skills row — `benchmark`,
`canto-entry-queue`, `gene-for-gene`, `inbox-triage`, `ontology-term-request` — and
"Gold-Standard Import" appears in both the Skills and the Benchmarking rows. None of it is
editable without regenerating the whole image.

Don't copy those numbers forward. `skills/REGISTRY.md` (regenerate with
`python3 -m phiweaver.registry`) is the live inventory;
[PHI-WEAVER-MODULE-TABLE.md](PHI-WEAVER-MODULE-TABLE.md) is the manuscript-frozen description and
independently states 12 skills.

### Should the figure be regenerated as an image?
**No — as SVG.** Every defect in it follows from being a raster: 62 dpi at final size, a ~20 %
vertical stretch, 7–8 pt sub-labels, and stale counts frozen into pixels. A generated image also
has no way to know which skills exist, which is how a duplicated box and five omissions got in.
Hand-authored SVG in the poster's own coordinate system gives resolution independence, editable
text, consistent typography, and boxes sourced from the registry so the figure is correct by
construction. The open question is the per-box icons: an MIT-licensed set (Tabler, Bootstrap
Icons), extraction from the original source, or dropping them and leaning on the number badges
and KEY colour coding, which already carry the meaning.

---

## Print quality at A0

### Why might the printed poster look soft?
Seven of ten embedded rasters fall below 100 dpi at final size (150 dpi is the usual
large-format target). Measured on `Poster-MU16.svg`:

| Asset | Native px | Placed | Effective DPI |
|---|---|---|---|
| PHI-base logo | 204 × 70 | 169 × 58 mm | **31** |
| PHI-base 5.6 stats box | 720 × 504 | 341 × 200 mm | **54** |
| Main workflow diagram (§3) | 1536 × 1024 | 524 × 420 mm | **62** |
| §5 left table | 991 × 641 | 379 × 183 mm | **66** |
| Rothamsted logo | 282 × 281 | 69 × 81 mm | 88 |

Compute this by comparing each `<image>`'s decoded PNG/JPEG header dimensions against its placed
size in millimetres.

### Why is some text distorted?
Two independent causes, both still open as of 2026-08-02:

1. **`preserveAspectRatio="none"`** on six `<image>` elements. Where the placement box's aspect
   ratio differs from the source, the image stretches — the workflow diagram ~20 % vertically,
   the 5.6 stats box ~19 % horizontally.
2. **A non-uniform transform** on the "Paused items" table:
   `matrix(0.29235408, 0, 0, 0.45335219, …)`. The x and y scales differ, so glyphs print squashed
   to ~65 % of their proper width. Effective size ≈ 16–18 pt.

### What text sizes does the poster use?
Title 86 pt, section headings 32 pt, body 24 pt — all comfortable at A0. The low end: entry-guide
caption 20 pt, the §4 caption 21 pt, conclusions 23 pt, metric labels 14–16 pt. The §5 tables are
the real problem — the rasterised one works out at roughly **8 pt** at final size, readable at
30 cm and decorative at 1.5 m. Both tables show four near-identical rows; trimming to two
contrasting rows would buy the space to enlarge them.

---

## Still to add

Absent from the poster as of 2026-08-02:

- **The conference name and abstract/poster number** — "AI Catalyst 2026" appears only in the SVG
  `<title>` and RDF metadata, nowhere visible.
- **A funding and acknowledgement line** with the BBSRC award number and Rothamsted ISP
  attribution; the UKRI-BBSRC logo carries no grant ID.
- **A label on the QR code**, and a second QR for the phi-weaver repository — the GitHub URL is
  currently text only.
- **A code and data availability line** for phi-weaver (licence; whether the repo is public).
- **The presenting author's email and ORCID** — only generic PHI-base addresses appear.
- **Any time or throughput measurement.** §7 claims "a practical route to faster … curation"
  while §4 reports only accuracy and completeness. Either add a minutes-per-paper comparison or
  soften the claim to "more consistent". This is the largest single gap on the poster.

---

## Fixed in MU16

For the record, all resolved before this file was written: a duplicated "for" in the title;
`alterd`, `pathogesn`, `conistency`, `accuracys`, `typetransporter`, `asexualsporulation`; six
lost word-spaces from the PPTX import (`appliesPHI-base`, `anexplicit`, `thebiocurator`,
`arechecked`, `remainlinked`, `andmore`); three broken mid-word hyphenations; a white-on-white
orphan heading left by the renumbering; an off-canvas stray character; and the §6 "Verified IDs" /
"Evidence linked" captions, which were swapped.
