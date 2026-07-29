---
created: 2026-07-29
type: documentation
tags: [docs, benchmarking, gold-standard, reference]
project: PHI-Weaver
---

# Benchmark article set — 10 articles, July 2026

**Canonical for:** which papers were used in the 2026-07-05 benchmark run. The run's *procedure*
is [BENCHMARK-RUNBOOK-2026-07-05-test10articles.md](../../docs/BENCHMARK-RUNBOOK-2026-07-05-test10articles.md);
the reusable workflow is `skills/benchmark/SKILL.md`. This note is the article list only.

Ten already-curated PHI-Canto articles, drafted blind by phiweaver (Fable 5, one isolated
sub-agent per paper so no entity bleed between drafts), then hand-scored against the curator's
own curations.

## The set

| PMID     | Europe PMC  | First author – Year | Journal              | Short title                                                      |
| -------- | ----------- | ------------------- | -------------------- | ---------------------------------------------------------------- |
| 1537802  | PMC206556   | Ronald PC – 1992    | J Bacteriol          | avrPto induces Pto-dependent resistance in tomato                |
| 1541525  | PMC257600   | Varma A – 1992      | Infect Immun         | URA5 transformants of *Cryptococcus neoformans*                  |
| 41020836 | PMC12468165 | Han S – 2025        | Curr Issues Mol Biol | TOX2 in conidiation and full virulence of *F. pseudograminearum* |
| 41051314 | PMC12520088 | Wang J – 2025       | Virulence            | Rad53 overexpression in *Candida albicans*                       |
| 41134853 | PMC12578332 | Chen L – 2025       | PLoS Pathog          | TRAPPIII complex in *Fusarium graminearum*                       |
| 41156765 | PMC12566070 | Li C – 2025         | Microorganisms       | SNARE CfSec22 in *Ceratocystis fimbriata*                        |
| 41170998 | PMC12691644 | Kramara J – 2025    | mBio                 | Efg1 governs hyphal morphogenesis independently of cAMP–PKA      |
| 41205159 | —           | Wang J – 2025       | Phytopathology       | GATA TF NsdD in *C. siamense* and *C. graminicola*               |
| 41229162 | PMC12612558 | Hidayat MT – 2025   | Mol Plant Pathol     | FleQ and GcbB as virulence factors in *P. syringae* pv. *tabaci* |
| 41295150 | PMC12653700 | Jia B – 2025        | J Fungi              | CgHat1 histone acetyltransferase in *C. gloeosporioides*         |

## Pathogen × host systems

| PMID | System |
|---|---|
| 1537802 | *P. syringae* pv. *tomato* avrPto × tomato Pto (gene-for-gene) |
| 1541525 | *Cryptococcus neoformans* URA5 × mouse (virulence) |
| 41020836 | *Fusarium pseudograminearum* TOX2 × wheat |
| 41051314 | *Candida albicans* Rad53 × *Galleria*/mouse (overexpression) |
| 41134853 | *Fusarium graminearum* TRAPPIII × wheat (autophagy) |
| 41156765 | *Ceratocystis fimbriata* CfSec22 × sweet potato |
| 41170998 | *Candida albicans* Efg1 × mouse (hyphal morphogenesis) |
| 41205159 | *Colletotrichum siamense*/*graminicola* NsdD × rubber/maize |
| 41229162 | *P. syringae* pv. *tabaci* FleQ/GcbB × tobacco (c-di-GMP) |
| 41295150 | *Colletotrichum gloeosporioides* CgHat1 × mulberry |

## Notes on the set

- **An 11th paper was dropped.** PMID:1799694 (van Kan 1991) — scanned PDF with no text layer,
  removed by the curator before drafting.
- **One PMID was wrong on disk.** The Rad53 paper's file read `4101314` (impossible for a 2025
  paper); phiweaver flagged it and it was corrected to **41051314**, curator-confirmed.
- **Two 1992 papers are in the set deliberately** — older papers stress UniProtKB accession
  resolution, which the run identified as phiweaver's single biggest gap.
- **`PMID41156765-…-phiweaver-DRAFT.md` cites the first author as "Li L"**; Europe PMC gives
  **Li C** for the same DOI (`10.3390/microorganisms13102305`). The draft is wrong; fix at source.

## Provenance

The set was recorded only in `11-CLAUDE-AI/SESSION-LOGS/2026-07-05-benchmark-drafting-10-papers.md`
until this note was written (2026-07-29) — the runbook named for the run carried no PMIDs. PMIDs and
systems come from that log; **first author, year, journal, DOI and Europe PMC ID were resolved
against Europe PMC on 2026-07-29** via `phiweaver.jats.europepmc`, not copied from filenames.
Drafts and PDFs live outside the repo, in the literature store under `completed/`.
