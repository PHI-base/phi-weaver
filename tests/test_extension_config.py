#!/usr/bin/env python3
"""Offline tests for extension_config.py (parses the bundled phipo_extensions.tsv)."""

import unittest

from phiweaver.lookup import extension_config as ec


class ParseTests(unittest.TestCase):
    def test_bundled_config_loads(self):
        index = ec.load()
        self.assertIn("infective_ability", index)
        self.assertIn("infects_tissue", index)
        self.assertIn("compared_to_control", index)

    def test_trailing_space_relation_is_stripped(self):
        # The source TSV has a trailing space on 'with_host_peptide '.
        rels = ec.attested_relations()
        self.assertIn("with_host_peptide", rels)
        self.assertNotIn("with_host_peptide ", rels)

    def test_range_kinds_classified(self):
        index = ec.load()
        self.assertEqual(index["infective_ability"].range_kind, ec.PHIPO_TERM)
        self.assertEqual(index["interaction_outcome"].range_kind, ec.PHIPO_TERM)
        self.assertEqual(index["infects_tissue"].range_kind, ec.BTO_TERM)
        self.assertEqual(index["compared_to_control"].range_kind, ec.METAGENOTYPE_ID)
        self.assertEqual(index["assayed_using"].range_kind, ec.GENE_ID)
        self.assertEqual(index["with_host_peptide"].range_kind, ec.FREE_TEXT)
        self.assertEqual(index["gene_for_gene_interaction"].range_kind, ec.PHIPO_EXT_TERM)
        self.assertEqual(index["has_severity"].range_kind, ec.FYPO_EXT_TERM)

    def test_annotation_type_recorded(self):
        index = ec.load()
        self.assertIn("pathogen_host_interaction_phenotype",
                      index["infective_ability"].annotation_types)


class ValidatePairTests(unittest.TestCase):
    def test_infective_ability_accepts_phipo_term(self):
        # PHIPO:0000015 'reduced virulence' — the value the Sdh draft needed.
        res = ec.validate_pair("infective_ability", "PHIPO:0000015")
        self.assertTrue(res.ok, res.reason)
        self.assertEqual(res.range_kind, ec.PHIPO_TERM)

    def test_infective_ability_rejects_free_text(self):
        # The original guess: a bare phrase, not a term ID.
        res = ec.validate_pair("infective_ability", "reduced virulence")
        self.assertTrue(res.attested)
        self.assertFalse(res.value_ok)
        self.assertFalse(res.ok)

    def test_unattested_relation_fails(self):
        res = ec.validate_pair("makes_it_worse", "PHIPO:0000015")
        self.assertFalse(res.attested)
        self.assertFalse(res.ok)
        self.assertIn("not an attested", res.reason)

    def test_infects_tissue_wants_bto(self):
        self.assertTrue(ec.validate_pair("infects_tissue", "BTO:0000934").ok)
        self.assertFalse(ec.validate_pair("infects_tissue", "PHIPO:0000015").value_ok)

    def test_metagenotype_and_gene_ranges_accept_free_ids(self):
        # These reference IDs the curation defines itself — not format-checked here.
        self.assertTrue(ec.validate_pair("compared_to_control", "some-metagenotype").ok)
        self.assertTrue(ec.validate_pair("assayed_using", "FgSdhB").ok)

    def test_penetrance_accepts_numeric_or_term(self):
        self.assertTrue(ec.validate_pair("has_penetrance", "75%").ok)
        self.assertTrue(ec.validate_pair("has_penetrance", "FYPO_EXT:1000002").ok)


if __name__ == "__main__":
    unittest.main()
