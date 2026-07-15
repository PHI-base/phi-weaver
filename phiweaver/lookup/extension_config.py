#!/usr/bin/env python3
"""
extension_config.py — attested PHI-Canto annotation-extension relations, offline.

A PHI-Canto phenotype annotation can carry **extensions** of the form
`relation → value` (e.g. `infects_tissue → BTO:0000934`, `compared_to_control →
<metagenotype>`, `infective_ability → PHIPO:0000015`). The set of legal relations,
and the value type each one accepts, is **PHI-base/PHI-Canto configuration** — it is
NOT an OLS ontology, so it cannot be resolved the way PHIPO/GO/BTO/PECO IDs are.

Until now weaver only *inferred* relation names from gold-standard examples, so a draft
could invent a relation (or use the wrong value shape) with nothing to catch it. This
module closes that gap the same way `validate_ontology_ids` closes the PHIDO/PECO gap:
by validating **offline against a bundled copy** of the config —
`data/phipo_extensions.tsv`, vendored from the private PHI-base/config repo (see
data/README.md).

Scope (deliberately staged, mirroring validate_ontology_ids' FORMAT-vs-EXISTENCE split):
- We validate that a **relation name is attested**, and that a **value matches the value
  *type*** its range declares (a PHIPO term where a PHIPO term is required, a BTO term
  where BTO is required, free text where the range is `Text`, etc.).
- We do NOT here verify that a term-typed value is a **descendant of the range root**
  (e.g. that an `infective_ability` value really sits under `PHIPO:0001179`), nor do we
  enforce the per-domain `subset relation` constraints (the `is_a(...)` expressions in
  the `domain ID` column). Those need the ontology graph / the primary term in hand;
  they are a deeper check left to the curator + `validate_ontology_ids` for now.

The parser reads the TSV columns:
    domain ID | subset relation | extension relation | range ID | Canto display text |
    Help text | cardinality | role | annotation_type_name
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

_DATA = Path(__file__).resolve().parent / "data"

# The three bundled extension configs, keyed by the annotation family they govern.
# All share the same TSV shape (domain -> relation -> range); each covers a different
# PHI-Canto annotation type. "phipo" is the default (interaction/phenotype extensions).
BUNDLED_CONFIGS = {
    "phipo": _DATA / "phipo_extensions.tsv",   # PHIPO phenotype / interaction annotations
    "go": _DATA / "phibase_go_extensions.tsv",  # GO (gene product) annotations
    "phido": _DATA / "phido_extensions.tsv",    # PHIDO disease-name annotations
}
CONFIG_PATH = BUNDLED_CONFIGS["phipo"]          # backward-compatible default
CONFIG_SOURCE = "bundled phipo_extensions.tsv"

# Value-type of an extension, derived from its declared range ID.
#   free_text        range "Text"            — arbitrary text (e.g. with_host_peptide)
#   gene_id          range "GeneID"          — a gene identifier the curation defines
#   protein_id       range "ProteinID"       — a protein identifier the curation defines
#   metagenotype_id  range "MetagenotypeID"  — a metagenotype the curation defines
#   taxon_id         range "PathogenTaxonID"/"HostTaxonID" — an NCBI taxon the curation gives
#   phipo_term       range "PHIPO:xxxxxxx"   — a PHIPO term (subtree of the range root)
#   bto_term         range "BTO:xxxxxxx"     — a BTO tissue term
#   phipo_ext_term   range "PHIPO_EXT:xxx"   — a term in the PHIPO_EXT extension namespace
#   fypo_ext_term    range "FYPO_EXT:xxx"    — a FYPO_EXT term (optionally with a |unit)
FREE_TEXT = "free_text"
GENE_ID = "gene_id"
PROTEIN_ID = "protein_id"
METAGENOTYPE_ID = "metagenotype_id"
TAXON_ID = "taxon_id"
PHIPO_TERM = "phipo_term"
BTO_TERM = "bto_term"
PHIPO_EXT_TERM = "phipo_ext_term"
FYPO_EXT_TERM = "fypo_ext_term"
UNKNOWN_RANGE = "unknown_range"

# Value-ID syntax per term-typed range. OBO term ranges use a 7-digit local id.
_TERM_ID_RE = {
    PHIPO_TERM: re.compile(r"^PHIPO:\d{7}$"),
    BTO_TERM: re.compile(r"^BTO:\d{7}$"),
    PHIPO_EXT_TERM: re.compile(r"^PHIPO_EXT:\d{7}$"),
    FYPO_EXT_TERM: re.compile(r"^FYPO_EXT:\d{7}$"),
}


def _range_kind(range_id: str) -> str:
    """Classify a `range ID` cell into a value-type. A cell may list several allowed
    roots separated by `|` (e.g. `BTO:x|BTO:y`) or carry a unit suffix (`FYPO_EXT:x|%`);
    the leading token decides the kind."""
    head = range_id.split("|", 1)[0].strip()
    if head == "Text":
        return FREE_TEXT
    if head == "GeneID":
        return GENE_ID
    if head == "ProteinID":
        return PROTEIN_ID
    if head == "MetagenotypeID":
        return METAGENOTYPE_ID
    if head in ("PathogenTaxonID", "HostTaxonID"):
        return TAXON_ID
    if head.startswith("PHIPO_EXT:"):
        return PHIPO_EXT_TERM
    if head.startswith("FYPO_EXT:"):
        return FYPO_EXT_TERM
    if head.startswith("PHIPO:"):
        return PHIPO_TERM
    if head.startswith("BTO:"):
        return BTO_TERM
    return UNKNOWN_RANGE


@dataclass
class ExtensionRelation:
    """One attested extension relation, aggregated over every config row that declares it
    (a relation such as `assayed_using` appears once per allowed primary-term domain)."""

    name: str
    range_id: str                       # the range as written (first row seen)
    range_kind: str
    display_texts: Set[str] = field(default_factory=set)
    annotation_types: Set[str] = field(default_factory=set)
    domain_ids: Set[str] = field(default_factory=set)
    cardinalities: Set[str] = field(default_factory=set)


@dataclass
class ExtensionCheck:
    relation: str
    value: str
    attested: bool                      # is the relation name in the config?
    value_ok: bool                      # does the value match the range's value-type?
    range_kind: Optional[str]
    reason: Optional[str] = None

    @property
    def ok(self) -> bool:
        return self.attested and self.value_ok


def _parse(path: Path) -> Optional[Dict[str, ExtensionRelation]]:
    """Parse the bundled TSV into {relation_name: ExtensionRelation}. Returns None if the
    file is missing/unreadable, so callers report an honest error instead of silently
    treating every relation as unattested."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return None
    rels: Dict[str, ExtensionRelation] = {}
    lines = text.splitlines()
    for raw in lines[1:]:                # skip the header row
        if not raw.strip():
            continue
        cols = raw.split("\t")
        if len(cols) < 4:
            continue
        domain_id = cols[0].strip()
        relation = cols[2].strip()       # NB source has a trailing space on with_host_peptide
        range_id = cols[3].strip()
        display = cols[4].strip() if len(cols) > 4 else ""
        cardinality = cols[6].strip() if len(cols) > 6 else ""
        ann_type = cols[8].strip() if len(cols) > 8 else ""
        if not relation:
            continue
        rel = rels.get(relation)
        if rel is None:
            rel = ExtensionRelation(name=relation, range_id=range_id,
                                    range_kind=_range_kind(range_id))
            rels[relation] = rel
        if display:
            rel.display_texts.add(display)
        if ann_type:
            rel.annotation_types.add(ann_type)
        if domain_id:
            rel.domain_ids.add(domain_id)
        if cardinality:
            rel.cardinalities.add(cardinality)
    return rels


@lru_cache(maxsize=len(BUNDLED_CONFIGS))
def _index(config: str = "phipo") -> Optional[Dict[str, ExtensionRelation]]:
    """Module-level cache of a parsed bundled config, by name (None if unavailable)."""
    return _parse(BUNDLED_CONFIGS[config])


def load(path: Optional[Path] = None, config: str = "phipo") -> Dict[str, ExtensionRelation]:
    """Return {relation: ExtensionRelation} for a bundled config (or an explicit path).

    `config` selects which bundled TSV to read ('phipo' [default], 'go', or 'phido').
    An explicit `path` overrides `config`. Raises FileNotFoundError if unreadable, or
    KeyError for an unknown config name."""
    if path is not None:
        index = _parse(path)
    else:
        if config not in BUNDLED_CONFIGS:
            raise KeyError(f"unknown config '{config}'; expected one of {sorted(BUNDLED_CONFIGS)}")
        index = _index(config)
    if index is None:
        raise FileNotFoundError(
            f"cannot read extension config ({path or BUNDLED_CONFIGS.get(config)})")
    return index


def attested_relations(index: Optional[Dict[str, ExtensionRelation]] = None,
                       config: str = "phipo") -> List[str]:
    """Sorted list of attested extension-relation names in a config."""
    return sorted((index or load(config=config)).keys())


def validate_pair(relation: str, value: str,
                  index: Optional[Dict[str, ExtensionRelation]] = None,
                  config: str = "phipo") -> ExtensionCheck:
    """Check one `relation → value` extension against a bundled config.

    Validates (a) the relation is attested and (b) the value matches the *type* the
    relation's range declares. Does NOT check ontology-subtree membership or per-domain
    subset constraints (see module docstring)."""
    idx = index if index is not None else load(config=config)
    rel = idx.get(relation.strip())
    if rel is None:
        return ExtensionCheck(relation, value, False, False, None,
                              f"'{relation}' is not an attested extension relation; "
                              f"expected one of: {', '.join(sorted(idx))}")
    kind = rel.range_kind
    val = value.strip()
    # ID-typed ranges the curation defines itself, and free text: nothing to format-check.
    if kind in (FREE_TEXT, GENE_ID, PROTEIN_ID, METAGENOTYPE_ID, TAXON_ID):
        return ExtensionCheck(relation, value, True, True, kind)
    # For a FYPO_EXT range that permits a unit (e.g. `...|%`), a bare number+unit penetrance
    # is also valid; only reject when a term-looking value has the wrong prefix.
    term_re = _TERM_ID_RE.get(kind)
    if term_re is None:
        return ExtensionCheck(relation, value, True, True, kind,
                              "range type not format-checked")
    if term_re.match(val):
        return ExtensionCheck(relation, value, True, True, kind)
    if kind == FYPO_EXT_TERM and re.match(r"^\d+(\.\d+)?\s*%?$", val):
        # quantitative penetrance/severity written as a value, allowed by the |unit range
        return ExtensionCheck(relation, value, True, True, kind)
    expected = {PHIPO_TERM: "a PHIPO:####### term", BTO_TERM: "a BTO:####### term",
                PHIPO_EXT_TERM: "a PHIPO_EXT:####### term",
                FYPO_EXT_TERM: "a FYPO_EXT:####### term or a numeric value"}[kind]
    return ExtensionCheck(relation, value, True, False, kind,
                          f"'{relation}' expects {expected} (range {rel.range_id}); "
                          f"got '{value}'")


def main(argv=None) -> int:
    p = argparse.ArgumentParser(
        description="List attested PHI-Canto extension relations, or validate a relation:value pair.")
    p.add_argument("pair", nargs="?",
                   help="a 'relation=value' extension to validate, e.g. infective_ability=PHIPO:0000015")
    p.add_argument("--config", default="phipo", choices=sorted(BUNDLED_CONFIGS),
                   help="which bundled config to use (default: phipo)")
    p.add_argument("--config-file", help="path to an alternative extensions TSV (overrides --config)")
    args = p.parse_args(argv)

    path = Path(args.config_file) if args.config_file else None
    try:
        index = load(path, config=args.config)
    except (FileNotFoundError, KeyError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if not args.pair:
        print("Attested extension relations (relation → range → value-type):")
        for name in attested_relations(index):
            rel = index[name]
            types = f"  [{', '.join(sorted(rel.annotation_types))}]" if rel.annotation_types else ""
            print(f"  {name:24s} {rel.range_id:24s} {rel.range_kind}{types}")
        return 0

    if "=" not in args.pair:
        p.error("pair must be 'relation=value'")
    relation, value = args.pair.split("=", 1)
    res = validate_pair(relation, value, index)
    mark = "✅" if res.ok else "❌"
    print(f"{mark} {res.relation} = {res.value}  [{res.range_kind}]")
    if res.reason:
        print(f"    {res.reason}")
    return 0 if res.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
