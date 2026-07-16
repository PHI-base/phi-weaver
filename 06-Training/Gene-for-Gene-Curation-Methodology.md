# Gene-for-Gene Pathogen–Host Interaction Curation — Methodology

> **Source:** curator methodology document by **Hsin-Yu Chang**, 2026-07-07
> (received from the PHI-base biocuration team). Lightly reformatted from the original
> export; content unchanged. This is the reference behind the `gene-for-gene` skill
> (`skills/gene-for-gene/SKILL.md`).

## Executive summary

Best-practice protocols for curating gene-for-gene and effector–host interactions in
PHI-base. As curation moves toward more complex interaction models, accurately representing
the relationships between pathogen effectors and (often multiple) host targets is essential.

Traditionally, gene-for-gene describes a **direct AVR–R relationship**. Modern evidence
supports a broader framework:

- Effectors frequently target **host proteins first**.
- Resistance (R) proteins often act as **sensors (guards)** rather than direct receptors.

### Interaction models

- **Direct recognition (classic model):** Effector → R protein → immunity.
- **Guard model (common in real systems):** Effector → host target → R protein detects the
  modification → immunity.

## 1. From gene-for-gene to host-target models

### Classic model (simplified)

- Pathogen *Avr* gene → Avr protein
- Host *R* gene → R protein
- Direct recognition → resistance

This model is often **insufficient** to describe experimental observations.

### Guard/decoy model

In many systems:

- The effector **does not primarily target the R protein**.
- The effector targets a **host virulence target**.
- The R protein monitors (**guards**) this target.

**Key components:**

- **Effector (Avr protein)**
- **Host target (virulence target)** — typically involved in defence signalling, vesicle
  trafficking, transcription regulation, or hormone signalling.
- **R protein**

**Mechanism:**

1. Effector delivery into the host cell.
2. Interaction with / modification of the host target.
3. R protein detects the alteration.
4. Effector-triggered immunity (ETI) is activated.

## 2. GO annotation strategy

### 2.1 Mandatory effector annotation

Every effector must include a GO Biological Process term beginning with **`effector-mediated …`**
(e.g. GO:0140418 *effector-mediated modulation of host process*). This serves as the
**primary identifier for effector proteins**.

### 2.2 Additional effector GO terms

Include only terms supported by experimental evidence:

- **Biological Process:** secretion by cell
- **Cellular Component:** host cell nucleus; host cell cytoplasm

### 2.3 Host protein GO terms

Curate only when supported by the experimental results:

- **Molecular Function:** innate immune receptor activity
- **Biological Process:** innate immune response

## 3. Pathogen genotype curation

Use controlled, standardized labels.

**Categories:**

- **Wild type (WT)**
- **Deletion / disruption / knockdown** — CRISPR-Cas9, RNAi, split-marker deletion
- **Complementation** — label: `Complement (Ectopic)`
- **Overexpression** — label the genotype `gene-OE`
- **GFP fusion** — label the genotype `gene-GFP`
- **Overexpression + GFP tag**
- **Signal-peptide deletion** — e.g. `Kwl1ΔSP`
- **Domain deletion** — e.g. `XopACΔLRR`
- **Amino-acid substitution** — e.g. `Ire1(aaS896A)[Ectopic]`
- **Non-functional allele** — e.g. `avrLm1(non-func)(unknown)[WT level]`

**Additional requirement:** strains must be accurately assigned.

## 4. Host genotype curation

Apply the same controlled vocabulary as pathogen genotypes.

- **Wild type (WT)**
- **Deletion / CRISPR-Cas9** — split-marker deletion
- **Disruption / knockdown** — RNAi; gene silencing: prefix the silenced gene with `si`
  (e.g. `siSec5`)
- **Complementation**
- **Overexpression** — label the genotype `gene-OE`
- **GFP fusion** — label the genotype `gene-GFP`
- **Overexpression + GFP tag**
- **Signal-peptide deletion**
- **Domain deletion**
- **Amino-acid substitution**
- **Non-functional allele**

**Additional requirement:** cultivars must be accurately assigned — critical for interpreting
R-gene presence/absence.

## 5. Metagenotypes (pathogen–host combinations)

Correct linkage of **pathogen genotype**, **host species**, and **host cultivar** is
**essential for biological accuracy**.

## 6. Phenotype curation

- **6.1 Pathogen phenotype** — record **only if different from WT**. Many effector mutants
  show **no phenotype**.
- **6.2 Host phenotype** — use PHIPO terms where available.
- **6.3 Interaction phenotypes** — minimum comparative set: WT pathogen × host; effector
  mutant × host; complement × host. This ensures **causal attribution of effector function**.

## 7. Experimental delivery mechanisms

Record how the effector is introduced (must be captured as metadata — it affects
interpretation):

- Agrobacterium-mediated delivery
- Delivery mechanism: pathogen gene expressed by transgenic host

## 8. Gene-for-gene phenotype annotation

- Select the appropriate **PHIPO term**.
- Add **PHIPO_EXT extensions**, including:
  - Presence/absence of the resistance gene — e.g. Falcon-MX (Rlm4, Rlm6), Westar (no R gene).
  - Model systems when used — e.g. `heterologous species: Arabidopsis thaliana`.

## 9. RNA expression annotation

Use when supported by data (RT-qPCR, RNA-seq) — the `wt_rna_expression` annotation type. Typical
annotation: *RNA level increased → during response to host*.

The RNA-level **qualifier is a controlled phrase**, not free text: pick exactly one of the seven
PomGeneEx qualifiers below (use the phrase — the numeric IDs are not required for the draft):

| Qualifier phrase | Use when |
|------------------|----------|
| RNA level increased | RNA present at a higher level under one condition/time than otherwise |
| RNA level decreased | RNA present at a lower level under one condition/time than otherwise |
| RNA level unchanged | RNA present at the same level under one condition/time as otherwise |
| RNA present | RNA detected (no level comparison) |
| RNA absent | RNA not detected |
| RNA level constant | level stays steady across conditions/time |
| RNA level fluctuates | level varies across conditions/time |

Keep the numeric specifics (fold-change, timepoints, method) in the annotation comment. Do not
invent a qualifier outside this list; if none fits, say so rather than forcing one.

## 10. Physical interaction evidence

Common methods: yeast two-hybrid, PCA, co-purification, affinity capture.

## 11. Disease naming

Assign disease names based **only** on the wild-type pathogen and the natural host. Do **not**
use mutants or artificial systems.

## 12. Inverse gene-for-gene interactions

Effector–R interactions can sometimes lead to **susceptibility instead of resistance**.

**Example — Tsn1–SnToxA:** no direct interaction; likely guard mechanism; activates
programmed cell death → **NE-triggered susceptibility (NETS)**.

## 13. Special annotation cases

**Insertion lines** — e.g. `rlp23-1(disruption)[Null]`.

## 14. Best-practice summary

Accurate curation requires:

- Mandatory effector GO tagging.
- Precise genotype classification.
- Correct metagenotype assignment.
- Evidence-based GO and phenotype annotations.
- Clear separation of pathogen phenotype vs interaction phenotype.
