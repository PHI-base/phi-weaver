#!/usr/bin/env python3
"""Network-free tests for phiweaver.canto.coverage (stdlib only)."""

import unittest

from phiweaver.canto import coverage as cov


def _canto(genotypes, metas, anns):
    return {"genotypes": genotypes, "metagenotypes": metas, "annotations": anns}


class CoverageTests(unittest.TestCase):
    def test_clean_block_no_warnings(self):
        c = _canto(
            [{"name": "mut", "role": "experimental"}, {"name": "host", "role": "host"}],
            [{"name": "mut x host", "pathogen_genotype": "mut", "host_genotype": "host"}],
            [{"feature_type": "metagenotype", "feature": "mut x host",
              "annotation_type": "pathogen_host_interaction_phenotype", "term_id": "PHIPO:1"}])
        self.assertEqual(cov.coverage_warnings(c), [])

    def test_unused_genotype_flagged_strongly(self):
        # a genotype referenced by nothing (this is the CgHat1/complementation-control class)
        c = _canto(
            [{"name": "mut", "role": "experimental"},
             {"name": "compl", "role": "complementation_control"},   # never used anywhere
             {"name": "host", "role": "host"}],
            [{"name": "mut x host", "pathogen_genotype": "mut", "host_genotype": "host"}],
            [{"feature_type": "metagenotype", "feature": "mut x host",
              "annotation_type": "pathogen_host_interaction_phenotype", "term_id": "PHIPO:1"}])
        ws = cov.coverage_warnings(c)
        self.assertTrue(any("compl" in w and "referenced by nothing" in w for w in ws))

    def test_pathogen_in_no_metagenotype_but_referenced_is_advisory(self):
        # used only as a compared_to_control → advisory (could be single-species-only), not "unused"
        c = _canto(
            [{"name": "mut", "role": "experimental"},
             {"name": "compl", "role": "complementation_control"},
             {"name": "host", "role": "host"}],
            [{"name": "mut x host", "pathogen_genotype": "mut", "host_genotype": "host"}],
            [{"feature_type": "genotype", "feature": "mut", "annotation_type": "pathogen_phenotype",
              "term_id": "PHIPO:2",
              "extensions": [{"relation": "compared_to_control", "value": "compl"}]}])
        ws = cov.coverage_warnings(c)
        self.assertTrue(any("compl" in w and "in no metagenotype" in w for w in ws))
        self.assertFalse(any("compl" in w and "referenced by nothing" in w for w in ws))

    def test_single_species_only_mutant_is_advisory_not_error(self):
        # a mutant with a single-species phenotype but no metagenotype — legit, but advised
        c = _canto(
            [{"name": "invitro", "role": "experimental"}, {"name": "host", "role": "host"}],
            [],
            [{"feature_type": "genotype", "feature": "invitro",
              "annotation_type": "pathogen_phenotype", "term_id": "PHIPO:3"}])
        ws = cov.coverage_warnings(c)
        self.assertTrue(any("invitro" in w and "single-species-only" in w for w in ws))

    def test_host_genotype_not_flagged_as_pathogen(self):
        c = _canto(
            [{"name": "mut", "role": "experimental"}, {"name": "host", "role": "host"}],
            [{"name": "mut x host", "pathogen_genotype": "mut", "host_genotype": "host"}],
            [])
        ws = cov.coverage_warnings(c)
        self.assertFalse(any("host" in w and "pathogen genotype" in w for w in ws))

    def test_empty_block_no_crash(self):
        self.assertEqual(cov.coverage_warnings({}), [])


if __name__ == "__main__":
    unittest.main()
