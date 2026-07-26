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


class StrainBackgroundTests(unittest.TestCase):
    """The 2026-07-25 ruling: wild type → strain, mutant → background, never both."""

    def test_populated_block_is_clean(self):
        c = {"genotypes": [
            {"name": "Guy11", "alleles": [], "strain": "Guy11"},
            {"name": "AM25", "alleles": ["abc1-2Δ"], "background": "Guy11; endogenous ABC1 absent"},
            {"name": "WT rice Sariceltic", "alleles": [], "strain": "Sariceltic"}]}
        self.assertEqual(cov.strain_background_warnings(c), [])

    def test_wild_type_without_strain_flagged(self):
        c = {"genotypes": [{"name": "Guy11", "alleles": []}]}
        ws = cov.strain_background_warnings(c)
        self.assertTrue(any("Guy11" in w and "wild type with no 'strain'" in w for w in ws))

    def test_mutant_without_background_flagged(self):
        c = {"genotypes": [{"name": "AM25", "alleles": ["abc1-2Δ"]}]}
        ws = cov.strain_background_warnings(c)
        self.assertTrue(any("AM25" in w and "no 'background'" in w for w in ws))

    def test_mutant_carrying_a_strain_flagged(self):
        # the failure the ruling exists to prevent — the isolate label used as a strain
        c = {"genotypes": [{"name": "AM25", "alleles": ["abc1-2Δ"], "strain": "AM25"}]}
        ws = cov.strain_background_warnings(c)
        self.assertTrue(any("AM25" in w and "belongs in 'background'" in w for w in ws))

    def test_both_fields_set_flagged(self):
        c = {"genotypes": [{"name": "AM25", "alleles": ["abc1-2Δ"],
                            "strain": "Guy11", "background": "Guy11"}]}
        ws = cov.strain_background_warnings(c)
        self.assertTrue(any("AM25" in w and "complementary" in w for w in ws))

    def test_background_alone_marks_a_mutant_without_alleles(self):
        # AM30: ectopic insertion in wild-type Guy11, no allele recorded — must not read wild type
        c = {"genotypes": [{"name": "AM30", "alleles": [],
                            "background": "Guy11; endogenous ABC1 present"}]}
        self.assertEqual(cov.strain_background_warnings(c), [])

    def test_empty_alleles_entries_do_not_make_a_mutant(self):
        c = {"genotypes": [{"name": "Guy11", "alleles": ["", "  "], "strain": "Guy11"}]}
        self.assertEqual(cov.strain_background_warnings(c), [])

    def test_unnamed_genotype_skipped_and_empty_block_no_crash(self):
        self.assertEqual(cov.strain_background_warnings({}), [])
        self.assertEqual(cov.strain_background_warnings({"genotypes": [{"alleles": []}]}), [])


if __name__ == "__main__":
    unittest.main()
