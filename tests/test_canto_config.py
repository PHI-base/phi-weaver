#!/usr/bin/env python3
"""
Tests for canto_config — PHI-Canto's own configuration, read offline.

Split in two, because until 2026-08-05 the two config files had different availability:

  * `canto_base.yaml` is PUBLIC (pombase/canto) and committed, so tests that only need
    the base file run everywhere, including on a fresh clone and in CI.
  * `canto_deploy.yaml` is now also PUBLIC (PHI-base/canto-config) and committed, so
    `TestEffectiveConfig` below runs everywhere too. The `deploy_only` skip guard is kept
    as defensive behaviour (a skip reports "couldn't check", which is the truth, whereas
    a failure would claim weaver is broken when the file is merely missing) rather than
    removed, in case the file is ever absent locally.

The base-only test matters most: it pins the behaviour that a missing deploy file
degrades *loudly*, since PomBase's defaults are wrong for PHI-base in both directions.
"""

import unittest
from pathlib import Path

from phiweaver.lookup import canto_config
from phiweaver.lookup.canto_config import (
    BASE_ONLY_ANNOTATION_TYPES,
    DEPLOY_CONFIG,
    PHI_ONLY_ANNOTATION_TYPES,
    load_config,
)

HAS_DEPLOY = DEPLOY_CONFIG.exists()
deploy_only = unittest.skipUnless(
    HAS_DEPLOY,
    f"canto_deploy.yaml absent — expected at {DEPLOY_CONFIG}",
)


class TestBaseConfig(unittest.TestCase):
    """Runs everywhere: only needs the committed public base file."""

    def setUp(self):
        load_config.cache_clear()
        self.base_only = load_config(deploy_path=Path("/nonexistent/canto_deploy.yaml"))

    def test_base_config_loads(self):
        self.assertGreater(len(self.base_only.evidence_codes), 50)
        self.assertIn("IMP", self.base_only.evidence_codes)

    def test_missing_deploy_is_flagged(self):
        self.assertFalse(self.base_only.deploy_loaded)
        self.assertIsNone(self.base_only.deploy_path)

    def test_missing_deploy_warns_on_every_check(self):
        """A base-only answer must never look like a clean pass."""
        for result in (
            self.base_only.validate_annotation_type("molecular_function"),
            self.base_only.validate_allele_type("deletion"),
            self.base_only.validate_evidence_code("IMP", "molecular_function"),
        ):
            self.assertTrue(result["valid"])
            self.assertIn("warning", result)
            self.assertIn("NOT the PHI-Canto configuration", result["warning"])

    def test_base_lacks_phi_specific_types(self):
        """Why base-only can't be trusted: weaver's core types aren't in it."""
        for phi_type in PHI_ONLY_ANNOTATION_TYPES:
            self.assertNotIn(phi_type, self.base_only.annotation_types)

    def test_base_permits_types_phi_canto_rejects(self):
        """The other direction: base would wave through types PHI-Canto has dropped."""
        for base_type in BASE_ONLY_ANNOTATION_TYPES:
            self.assertIn(base_type, self.base_only.annotation_types)


@deploy_only
class TestEffectiveConfig(unittest.TestCase):
    """Needs the deploy file; skipped when it isn't present."""

    def setUp(self):
        load_config.cache_clear()
        self.cfg = load_config()

    def test_identifies_as_phi_canto(self):
        self.assertEqual(self.cfg.instance_name, "PHI-Canto")
        self.assertTrue(self.cfg.deploy_loaded)

    def test_twelve_annotation_types(self):
        """The 12 types the gold-standard library is built around."""
        self.assertEqual(len(self.cfg.annotation_types), 12)

    def test_phi_specific_types_present(self):
        for phi_type in PHI_ONLY_ANNOTATION_TYPES:
            self.assertIn(phi_type, self.cfg.annotation_types)

    def test_dropped_types_absent(self):
        """PHI-Canto removes these; a draft naming one is wrong."""
        for base_type in BASE_ONLY_ANNOTATION_TYPES:
            self.assertNotIn(base_type, self.cfg.annotation_types)

    def test_allele_types(self):
        self.assertEqual(len(self.cfg.allele_types), 16)
        # PHI-base additions to the PomBase set
        self.assertIn("nonsense mutation", self.cfg.allele_types)
        self.assertIn("transformant", self.cfg.allele_types)

    def test_evidence_codes_inherited_from_base(self):
        """The deploy file doesn't override evidence_types, so these come from base."""
        self.assertIn("IMP", self.cfg.evidence_codes)
        self.assertIn("IDA", self.cfg.evidence_codes)

    def test_evidence_codes_for_is_per_type_not_the_generic_catalog(self):
        """The bug this was built to fix: `evidence_codes` (generic) is missing values
        several types actually accept, and accepts values a type's real dropdown does not
        offer. `evidence_codes_for` must answer what a curator would actually see."""
        go_codes = self.cfg.evidence_codes_for("molecular_function")
        self.assertEqual(set(go_codes), {"IDA", "IGI", "IMP", "IPI", "EXP", "TAS"})
        self.assertNotIn("IEA", go_codes)              # not offered for this type...
        self.assertIn("IEA", self.cfg.evidence_codes)  # ...despite being in the generic catalog

        pheno_codes = self.cfg.evidence_codes_for("pathogen_phenotype")
        self.assertIn("Macroscopic observation (qualitative observation)", pheno_codes)
        self.assertIn("Macroscopic observation (quantitative observation)", pheno_codes)
        # ...but that pair is NOT in the generic catalog at all — the actual bug.
        self.assertNotIn("Macroscopic observation (quantitative observation)",
                         self.cfg.evidence_codes)

        self.assertEqual(self.cfg.evidence_codes_for("disease_name"), [])  # no evidence field
        self.assertEqual(self.cfg.evidence_codes_for("not_a_real_type"), [])

    def test_validate_evidence_code_is_scoped_to_the_type_given(self):
        ok = self.cfg.validate_evidence_code(
            "Macroscopic observation (quantitative observation)",
            "pathogen_host_interaction_phenotype")
        self.assertTrue(ok["valid"])
        wrong_type = self.cfg.validate_evidence_code(
            "Macroscopic observation (quantitative observation)", "molecular_function")
        self.assertFalse(wrong_type["valid"])

    def test_do_not_annotate_subsets(self):
        subsets = self.cfg.do_not_annotate_subsets
        self.assertTrue(any("qc_do_not_annotate" in s for s in subsets))
        self.assertTrue(any("canto_root_subset" in s for s in subsets))

    def test_extension_conf_files_include_vendored_ones(self):
        """Provenance check: the TSVs in data/ should be ones PHI-Canto actually loads."""
        listed = " ".join(self.cfg.extension_conf_files)
        self.assertIn("phipo_extensions.tsv", listed)
        self.assertIn("phido_extensions.tsv", listed)

    def test_checks_pass_without_warning(self):
        result = self.cfg.validate_annotation_type("gene_for_gene_phenotype")
        self.assertTrue(result["valid"])
        self.assertNotIn("warning", result)

    def test_unknown_value_rejected(self):
        self.assertFalse(self.cfg.validate_annotation_type("not_a_real_type")["valid"])
        self.assertFalse(self.cfg.validate_allele_type("frobnication")["valid"])


class TestCLI(unittest.TestCase):
    def test_list_runs(self):
        load_config.cache_clear()
        self.assertEqual(canto_config.main(["--list", "evidence"]), 0)


if __name__ == "__main__":
    unittest.main()
