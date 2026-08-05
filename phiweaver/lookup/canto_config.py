#!/usr/bin/env python3
"""
canto_config.py — what PHI-Canto actually accepts, read from its own configuration.

PHI-Canto is a deployment of PomBase's Canto. Its configuration is therefore **two
files merged**, and neither one alone is correct:

    canto_base.yaml    pombase/canto, PUBLIC        — the defaults (2735 lines)
    canto_deploy.yaml  PHI-base/canto-config, PUBLIC — the PHI-base overrides (650 lines)

Effective config = base, with deploy's top-level keys replacing base's.

Until now weaver *inferred* the annotation types, allele types and evidence codes from
gold-standard examples, so a draft could name an annotation type PHI-Canto doesn't have,
or an allele type it would reject, with nothing to catch it. This module closes that gap
the same way `extension_config` closed the extension-relation gap: by reading the real
configuration offline.

**Why the base file alone is not a usable fallback.** The two configs diverge in both
directions, so base-only answers are wrong twice over (comparing *enabled* lists, which
is what governs what a curator can actually annotate — note base marks 14 types
*available* but enables only 11):

  PHI-Canto ENABLES, base does not:  pathogen_phenotype, host_phenotype,
                                     pathogen_host_interaction_phenotype,
                                     gene_for_gene_phenotype, disease_name
  base ENABLES, PHI-Canto does not:  phenotype, genotype_interaction,
                                     genetic_interaction,
                                     protein_sequence_feature_or_motif

That is 5 of PHI-Canto's 12 types invisible to a base-only check — including
`pathogen_phenotype` and `host_phenotype`, the two most basic things weaver drafts. In
the other direction a base-only check would wave through `genetic_interaction` and a bare
`phenotype`, neither of which PHI-Canto accepts. So when the deploy file is missing this
module reports `deploy_loaded = False` and every accessor is explicit that the values are
PomBase defaults, not PHI-base's. Callers should treat that as "cannot validate", not as
"validated OK".

**On the deploy file.** `canto_deploy.yaml` now comes from the **public** repo
PHI-base/canto-config, and is committed here. Until 2026-08-05 it came from the private
PHI-base/config repo; James Seager cleared it for local use on 2026-07-21 (the ORCID OAuth
secret is stored outside the file — the config holds only the env-var name — and the
GA/GTM measurement id is public by construction, being served in the page source of the
live site), so weaver read it locally without committing it. James then published a
filtered, sensitive-history-stripped copy of PHI-base/config as the public
PHI-base/canto-config repo; once confirmed byte-identical, the file was committed and the
`.gitignore` entry removed. The `deploy_loaded = False` fallback below therefore should not
fire on a normal clone any more — it remains as defensive behaviour for a missing file.
See data/README.md for the refresh command and full history.

Scope: this module answers "is this a thing PHI-Canto accepts?" for annotation types,
allele types, evidence codes and the do-not-annotate subsets. It does not validate
ontology term IDs (that is `validate_ontology_ids`) or extension relations (that is
`extension_config`).
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Set

try:
    import yaml
except ImportError:  # pragma: no cover - dependency is declared, this is a clearer error
    sys.exit("canto_config needs PyYAML: python3 -m pip install PyYAML")

DATA_DIR = Path(__file__).parent / "data"
BASE_CONFIG = DATA_DIR / "canto_base.yaml"
DEPLOY_CONFIG = DATA_DIR / "canto_deploy.yaml"

# How the two ENABLED lists diverge (verified 2026-07-21 against the files in data/).
# Recorded here so the warning text can be specific, and so drift in either file shows up
# as a test failure rather than as silently wrong validation.
PHI_ONLY_ANNOTATION_TYPES = frozenset(
    {
        "pathogen_phenotype",
        "host_phenotype",
        "pathogen_host_interaction_phenotype",
        "gene_for_gene_phenotype",
        "disease_name",
    }
)
BASE_ONLY_ANNOTATION_TYPES = frozenset(
    {
        "phenotype",
        "genotype_interaction",
        "genetic_interaction",
        "protein_sequence_feature_or_motif",
    }
)


def _names(entries: Sequence) -> List[str]:
    """Canto writes these lists either as plain names or as dicts with a 'name' key."""
    out = []
    for e in entries or []:
        if isinstance(e, str):
            out.append(e)
        elif isinstance(e, dict) and e.get("name"):
            out.append(e["name"])
    return out


@dataclass
class CantoConfig:
    """The effective PHI-Canto configuration (base + deploy overrides)."""

    raw: Dict
    deploy_loaded: bool
    base_path: Path
    deploy_path: Optional[Path] = None

    @property
    def instance_name(self) -> str:
        return self.raw.get("name", "unknown")

    @property
    def annotation_types(self) -> List[str]:
        """The enabled annotation types — the 12 weaver drafts against."""
        return _names(
            self.raw.get("enabled_annotation_type_list")
            or self.raw.get("available_annotation_type_list", [])
        )

    @property
    def allele_types(self) -> List[str]:
        """Legal values for the 'Allele type' field (NOT 'Expression' — see FAQ rule 6)."""
        return _names(self.raw.get("allele_type_list", []))

    @property
    def evidence_codes(self) -> List[str]:
        """Evidence codes, e.g. IMP / IDA / IGI. Defined in the base config only."""
        return sorted(self.raw.get("evidence_types", {}).keys())

    @property
    def do_not_annotate_subsets(self) -> List[str]:
        """
        Ontology subsets PHI-Canto refuses to annotate against — grouping/root/QC terms.

        Useful defensively: a term can exist and be non-obsolete and *still* be
        unusable, so a suggestion drawn from one of these subsets would be rejected
        by the curation tool after weaver proposed it.
        """
        cfg = self.raw.get("ontology_namespace_config", {}) or {}
        return list(cfg.get("do_not_annotate_subsets", []))

    @property
    def extension_conf_files(self) -> List[str]:
        """The extension-config TSVs PHI-Canto loads (provenance for data/*.tsv)."""
        return list(self.raw.get("extension_conf_files", []))

    def _check(self, value: str, allowed: Sequence[str], what: str) -> Dict:
        ok = value in allowed
        result = {"value": value, "valid": ok, "checked_against": what}
        if not self.deploy_loaded:
            result["warning"] = (
                "PomBase defaults only — canto_deploy.yaml not present, so this is NOT "
                "the PHI-Canto configuration. Treat as unverified."
            )
        if not ok:
            close = [a for a in allowed if value.lower() in a.lower()]
            if close:
                result["did_you_mean"] = close
        return result

    def validate_annotation_type(self, value: str) -> Dict:
        return self._check(value, self.annotation_types, "enabled_annotation_type_list")

    def validate_allele_type(self, value: str) -> Dict:
        return self._check(value, self.allele_types, "allele_type_list")

    def validate_evidence_code(self, value: str) -> Dict:
        return self._check(value, self.evidence_codes, "evidence_types")


@lru_cache(maxsize=4)
def load_config(
    base_path: Optional[Path] = None, deploy_path: Optional[Path] = None
) -> CantoConfig:
    """
    Load base + deploy and merge. Deploy's top-level keys replace base's.

    Canto itself does a deeper merge, but every key weaver reads is replaced wholesale
    by the deploy file (the annotation-type and allele-type lists are given in full),
    so a top-level override is faithful for our purposes and easier to reason about.
    """
    base_path = Path(base_path) if base_path else BASE_CONFIG
    deploy_path = Path(deploy_path) if deploy_path else DEPLOY_CONFIG

    if not base_path.exists():
        raise FileNotFoundError(f"base config missing: {base_path}")

    with open(base_path) as fh:
        merged = yaml.safe_load(fh) or {}

    deploy_loaded = False
    if deploy_path.exists():
        with open(deploy_path) as fh:
            overrides = yaml.safe_load(fh) or {}
        merged.update(overrides)
        deploy_loaded = True

    return CantoConfig(
        raw=merged,
        deploy_loaded=deploy_loaded,
        base_path=base_path,
        deploy_path=deploy_path if deploy_loaded else None,
    )


def main(argv=None):
    p = argparse.ArgumentParser(
        description="Show or check PHI-Canto's own configuration (base + PHI-base overrides)."
    )
    p.add_argument(
        "--list",
        choices=["annotation-types", "allele-types", "evidence", "subsets", "extensions"],
        help="print a config list",
    )
    p.add_argument("--check-annotation-type", metavar="NAME")
    p.add_argument("--check-allele-type", metavar="NAME")
    p.add_argument("--check-evidence", metavar="CODE")
    args = p.parse_args(argv)

    cfg = load_config()

    if not cfg.deploy_loaded:
        print(
            "WARNING: canto_deploy.yaml not found — showing PomBase defaults, NOT "
            "PHI-Canto's configuration.\n"
            f"         Expected at: {DEPLOY_CONFIG}\n"
            "         See phiweaver/lookup/data/README.md to copy it in.\n",
            file=sys.stderr,
        )

    lists = {
        "annotation-types": cfg.annotation_types,
        "allele-types": cfg.allele_types,
        "evidence": cfg.evidence_codes,
        "subsets": cfg.do_not_annotate_subsets,
        "extensions": cfg.extension_conf_files,
    }
    if args.list:
        for item in lists[args.list]:
            print(item)
        return 0

    checks = [
        (args.check_annotation_type, cfg.validate_annotation_type),
        (args.check_allele_type, cfg.validate_allele_type),
        (args.check_evidence, cfg.validate_evidence_code),
    ]
    ran = False
    for value, fn in checks:
        if value:
            ran = True
            r = fn(value)
            mark = "OK" if r["valid"] else "NOT FOUND"
            print(f"{mark}: {r['value']}  (checked against {r['checked_against']})")
            if r.get("did_you_mean"):
                print(f"  did you mean: {', '.join(r['did_you_mean'])}")
            if r.get("warning"):
                print(f"  ! {r['warning']}")
    if ran:
        return 0

    print(f"instance: {cfg.instance_name}   deploy config loaded: {cfg.deploy_loaded}")
    for name, values in lists.items():
        print(f"  {name:<18} {len(values)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
