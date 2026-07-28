#!/usr/bin/env python3
"""Assemble the PHI-Weaver -> LLM-judge handover bundle into one markdown file.

The bundle is layered:
  * a CORE JUDGE PRIMER (authoritative) at the top -- purpose, operating rules,
    rating scale, output contract, per-paper summary, example-use rules; and
  * APPENDICES (convention references only) -- scorecard rubric, controlled
    vocabulary, ontology/UniProt/nomenclature guides, effector methodology,
    module registry, and worked gold-standard examples.

Output is a GENERATED artifact -- edit the source files, then rerun:

    python3 scripts/build_judge_handover.py

Writes docs/phiweaver-judge-handover.md. On each run it also validates that every
curation-example `annotation_types` value is in the controlled vocabulary (TAGS.md)
and prints a warning for any that are not. See the parked design note
docs/LLM-AS-JUDGE-DESIGN.md for the rationale.
"""
import re
import sys
from pathlib import Path
from datetime import date

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "docs" / "phiweaver-judge-handover.md"
TAGS = REPO / "07-Standards" / "curation-examples" / "TAGS.md"
EXAMPLES_DIR = REPO / "07-Standards" / "curation-examples"

# (vault-relative path, tier, role blurb) in reading order.
# tier: "core" = authoritative judge instructions; "appendix" = convention reference only.
FILES = [
    ("07-Standards/judge-core-primer.md", "core",
     "CORE JUDGE PRIMER (authoritative) — purpose, operating rules, output contract"),
    ("07-Standards/curation-benchmarking/README.md", "appendix",
     "Scorecard rubric — the criteria the judge grades against"),
    ("07-Standards/curation-examples/TAGS.md", "appendix",
     "Controlled vocabulary (annotation types, topics, evidence) used in examples"),
    ("07-Standards/curation-examples/Curation-Examples-INDEX.md", "appendix",
     "Index of the worked examples + PHI-Canto annotation-type coverage"),
    ("07-Standards/curation-examples/_TEMPLATE.md", "appendix",
     "Template showing the shape of a worked curation example"),
    ("07-Standards/Ontology-Terms-Reference.md", "appendix",
     "Ontology reference (PHIPO / PHIDO / GO / BRENDA) conventions"),
    ("07-Standards/UniProtKB-Gene-Identification-Guide.md", "appendix",
     "How genes/proteins are resolved to UniProtKB accessions"),
    ("07-Standards/Genetic Nomenclature.md", "appendix",
     "Gene/allele naming conventions"),
    ("07-Standards/Effector-curation-2026-04-15/"
     "Curation Methodologies for Pathogen Effector Curation.md", "appendix",
     "Effector curation methodology (gene-for-gene, guard/decoy, recognition)"),
    ("07-Standards/Effector-curation-2026-04-15/"
     "GO-terms used for gene-for-gene-entries.md", "appendix",
     "GO terms conventionally used for gene-for-gene / effector entries"),
    ("skills/REGISTRY.md", "appendix",
     "What each curation step is supposed to produce (module registry)"),
    ("07-Standards/curation-examples/PMID26177154-Fol-I7-gene-for-gene.md", "appendix",
     "WORKED EXAMPLE — gene-for-gene (Fol effectors x tomato I-7)"),
    ("07-Standards/curation-examples/"
     "PMID35468894-PINE1-effector-PGIP-physical-interaction.md", "appendix",
     "WORKED EXAMPLE — effector physical interaction (PINE1 x PGIP)"),
    ("07-Standards/curation-examples/PMID37177781-AvrPi9-OsRGLG5-protein-level.md", "appendix",
     "WORKED EXAMPLE — protein-level effect (AvrPi9 x OsRGLG5)"),
    ("07-Standards/curation-examples/PMID23498959-creD-RLCK185-phosphorylation.md", "appendix",
     "WORKED EXAMPLE — phosphorylation (creD / RLCK185)"),
    ("07-Standards/curation-examples/PMID39787257-FgKnr4-cell-wall-stress.md", "appendix",
     "WORKED EXAMPLE — cell-wall stress phenotype (FgKnr4)"),
]


def anchor(tier, role):
    if tier == "core":
        return "core-primer"
    return "worked-example" if role.startswith("WORKED EXAMPLE") else "appendix"


def controlled_annotation_types():
    """Parse the controlled `annotation_types` values from TAGS.md."""
    text = TAGS.read_text(encoding="utf-8")
    # Grab the block under the annotation_types heading up to the next "## " heading.
    m = re.search(r"##\s+`annotation_types`.*?(?=\n##\s)", text, re.DOTALL)
    block = m.group(0) if m else ""
    return set(re.findall(r"^-\s+`([^`]+)`", block, re.MULTILINE))


def frontmatter_annotation_types(text):
    """Return the annotation_types list from a file's YAML frontmatter (or [])."""
    if not text.startswith("---"):
        return []
    end = text.find("\n---", 3)
    fm = text[3:end] if end != -1 else text
    m = re.search(r"^annotation_types:\s*\n((?:\s*-\s*.+\n?)+)", fm, re.MULTILINE)
    if not m:
        return []
    return re.findall(r"-\s*(.+?)\s*$", m.group(1), re.MULTILINE)


def validate_vocab():
    """Warn on any example annotation_types value not in the controlled vocabulary."""
    allowed = controlled_annotation_types()
    issues = []
    for f in sorted(EXAMPLES_DIR.glob("*.md")):
        for val in frontmatter_annotation_types(f.read_text(encoding="utf-8")):
            if val not in allowed:
                issues.append((f.relative_to(REPO), val))
    if issues:
        print("⚠ annotation_types NOT in TAGS.md controlled vocabulary:", file=sys.stderr)
        for path, val in issues:
            print(f"    {path}: {val!r}", file=sys.stderr)
    else:
        print(f"✓ annotation_types vocab OK ({len(allowed)} controlled values)")
    return issues


def build():
    parts = [f"""# PHI-Weaver → LLM-as-judge handover bundle

<!-- GENERATED by `python3 scripts/build_judge_handover.py`. Do not edit by hand;
     edit the source files listed in the index below and regenerate. -->

*Generated {date.today().isoformat()} from the PHI-Weaver vault. Layered convention primer
for an external model (e.g. GPT-5.5) acting as an independent judge / pre-review critic of
PHI-Weaver curation drafts.*

## How this bundle is layered
1. The **CORE JUDGE PRIMER** (first section) is **authoritative** — it holds the judge's
   purpose, operating rules, rating scale, output contract, and example-use rules.
2. Everything after it is an **APPENDIX**: convention reference / retrieved supporting material
   only. Use appendices to interpret a convention, **never as evidence for the paper under
   review**. If an appendix conflicts with the core primer, the core primer wins.

## How to use it
1. Always give the model the **core primer**. Add the appendices the paper needs — and only
   the **1–3 most relevant worked examples** by topic (see leakage note), not all of them.
2. Then per paper add: the publication, the PHI-Weaver draft, the PHI-Canto entry queue, and
   the blank scorecard.
3. Have the model grade **against the core primer's rules and the rubric**, not against its own
   idea of a correct curation. Treat its output as **candidate issues for a human to
   adjudicate**, not a verdict.

## ⚠️ Leakage & example-bias note
- The worked examples are human-validated gold standards. If you judge a paper whose **PMID
  appears in a worked example, remove that example for that run** so the judge can't grade
  against the answer key. (Not an issue for papers with no gold standard.)
- Prefer only the **1–3 most relevant** validated examples for a given paper; many unrelated
  examples can bias the judge toward their shapes.
- The human gold standard is a **strong reference, not ground truth** — a judge–human
  disagreement is investigated both ways (see the design note,
  `docs/LLM-AS-JUDGE-DESIGN.md`).

## Contents
| # | Tier | Role | Vault path |
| - | ---- | ---- | ---------- |"""]

    for i, (path, tier, role) in enumerate(FILES, 1):
        parts.append(f"| {i} | {tier} | {role} | `{path}` |")

    parts.append("\n---\n")

    for i, (path, tier, role) in enumerate(FILES, 1):
        f = REPO / path
        body = f.read_text(encoding="utf-8") if f.exists() else "_(file not found)_\n"
        label = "CORE PRIMER (authoritative)" if tier == "core" else "APPENDIX (reference only)"
        parts.append(f"""<!-- ===== FILE {i}/{len(FILES)} :: {anchor(tier, role)} ===== -->
## {i}. [{label}] {role}
**Vault path:** `{path}`

````markdown
{body.rstrip()}
````

---
""")

    OUT.write_text("\n".join(parts), encoding="utf-8")
    text = OUT.read_text(encoding="utf-8")
    n_core = sum(1 for _, tier, _ in FILES if tier == "core")
    print(f"Wrote {OUT.relative_to(REPO)} — "
          f"{OUT.stat().st_size / 1024:.1f} KB, {text.count(chr(10))} lines, "
          f"{len(FILES)} source files ({n_core} core, {len(FILES) - n_core} appendix)")


if __name__ == "__main__":
    validate_vocab()
    build()
