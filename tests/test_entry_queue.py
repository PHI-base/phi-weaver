#!/usr/bin/env python3
"""Network-free tests for phiweaver.canto.entry_queue (stdlib only)."""

import tempfile
import unittest
from pathlib import Path

from phiweaver.canto import entry_queue as eq


def _rec(**over):
    """A compact draft record; override the canto sub-block as needed."""
    canto = {
        "genes": [
            {"name": "GeneA", "uniprot": "P11111", "organism": "Fusarium x", "locus": "L1"},
            {"name": "GeneB", "uniprot": "", "organism": "Fusarium x", "locus": "L2",
             "note": "no UniProt entry"},
        ],
        "alleles": [
            {"name": "geneAΔ", "gene": "GeneA", "type": "deletion", "expression": "null"},
            {"name": "GeneA(reintroduced)", "gene": "GeneA", "type": "wild type",
             "expression": "wild-type level"},
            {"name": "geneBΔ", "gene": "GeneB", "type": "deletion", "expression": "null"},
        ],
        "genotypes": [
            {"name": "WT", "organism": "Fusarium x", "alleles": [], "role": "control"},
            {"name": "geneAΔ", "organism": "Fusarium x", "alleles": ["geneAΔ"], "role": "experimental"},
            {"name": "geneBΔ", "organism": "Fusarium x", "alleles": ["geneBΔ"], "role": "experimental"},
            {"name": "host wt", "organism": "Triticum aestivum", "alleles": [], "role": "host"},
        ],
        "metagenotypes": [
            {"name": "geneAΔ x host", "pathogen_genotype": "geneAΔ", "host_genotype": "host wt",
             "role": "experimental"},
            {"name": "WT x host", "pathogen_genotype": "WT", "host_genotype": "host wt", "role": "control"},
            {"name": "geneBΔ x host", "pathogen_genotype": "geneBΔ", "host_genotype": "host wt",
             "role": "experimental"},
        ],
        "annotations": [
            {"feature_type": "genotype", "feature": "geneAΔ", "annotation_type": "pathogen_phenotype",
             "term_id": "PHIPO:0001212", "term_name": "decreased hyphal growth",
             "evidence": "growth assay", "extensions": [], "conditions": "PDA", "figure": "Fig 1"},
            {"feature_type": "genotype", "feature": "geneAΔ", "annotation_type": "pathogen_phenotype",
             "term_id": "", "term_name": "impaired autophagy", "evidence": "GFP flux",
             "extensions": [], "conditions": "MM-N", "figure": "Fig 3"},
            {"feature_type": "gene", "feature": "GeneA", "annotation_type": "molecular_function",
             "term_id": "GO:0005085", "term_name": "GEF activity",
             "evidence": "INTERPRETIVE — inferred from rescue, no direct assay",
             "extensions": [], "conditions": "", "figure": "Fig 8"},
            {"feature_type": "gene", "feature": "GeneA", "annotation_type": "physical_interaction",
             "term_id": "", "term_name": "physical interaction: GeneA – GeneB",
             "evidence": "Y2H + Co-IP", "extensions": [{"relation": "interactor", "value": "GeneB"}],
             "conditions": "", "figure": "Fig 1A"},
            {"feature_type": "metagenotype", "feature": "geneAΔ x host",
             "annotation_type": "pathogen_host_interaction_phenotype", "term_id": "PHIPO:0000015",
             "term_name": "reduced virulence", "evidence": "disease index",
             "extensions": [{"relation": "compared_to_control", "value": "WT x host"}],
             "conditions": "wheat", "figure": "Fig 2"},
            {"feature_type": "metagenotype", "feature": "WT x host", "annotation_type": "disease_name",
             "term_id": "PHIDO:0000162", "term_name": "Fusarium ear blight", "evidence": "",
             "extensions": [], "conditions": "", "figure": "Fig 2"},
            # annotation on a held gene -> must be parked
            {"feature_type": "genotype", "feature": "geneBΔ", "annotation_type": "pathogen_phenotype",
             "term_id": "PHIPO:0000052", "term_name": "decreased conidiation",
             "evidence": "growth assay", "extensions": [], "conditions": "", "figure": "Fig 4"},
        ],
    }
    canto.update(over.get("canto", {}))
    return {"meta": {"pmid": "999", "paper": "Test et al.", "system": "Fx -> wheat",
                     "model": "Fable 5", "date": "2026-07-08"}, "canto": canto}


class HeldGeneCascadeTests(unittest.TestCase):
    def setUp(self):
        self.md, self.counts = eq.render_entry_queue(_rec())

    def test_summary_counts(self):
        self.assertEqual(self.counts["genes_enter"], 1)   # GeneA
        self.assertEqual(self.counts["genes_held"], 1)    # GeneB (no accession)

    def test_held_gene_marked_hold_not_enter(self):
        # GeneB row is 'hold'; GeneA row is 'enter'
        self.assertRegex(self.md, r"GeneB.*unresolved.*hold")
        self.assertRegex(self.md, r"GeneA.*UniProtKB:P11111.*enter")

    def test_held_allele_and_genotype_not_in_entry_tables(self):
        # geneBΔ allele + genotype cascade to parked; not in the create tables
        c_section = self.md.split("## C. Create pathogen genotypes")[1].split("## D.")[0]
        self.assertNotIn("geneBΔ", c_section)

    def test_annotation_on_held_gene_is_parked(self):
        parked = self.md.split("## G. Parked items")[1]
        self.assertIn("decreased conidiation", parked)

    def test_blank_term_annotation_parked(self):
        parked = self.md.split("## G. Parked items")[1]
        self.assertIn("impaired autophagy", parked)
        self.assertIn("no ontology term resolved", parked)

    def test_interpretive_mf_parked(self):
        parked = self.md.split("## G. Parked items")[1]
        self.assertIn("interpretive molecular-function", parked)
        # and NOT in the F1 GO table
        f1 = self.md.split("### F1. GO annotations")[1].split("### F2.")[0]
        self.assertNotIn("GEF activity", f1)


class HostPathogenSplitTests(unittest.TestCase):
    def setUp(self):
        self.md, _ = eq.render_entry_queue(_rec())

    def test_host_genotype_in_section_d(self):
        d = self.md.split("## D. Create host genotype")[1].split("## E.")[0]
        self.assertIn("host wt", d)

    def test_pathogen_genotype_not_in_host_table(self):
        d = self.md.split("## D. Create host genotype")[1].split("## E.")[0]
        self.assertNotIn("| ☐ | WT |", d)


class PhysicalInteractionAndTableSafetyTests(unittest.TestCase):
    def setUp(self):
        self.md, _ = eq.render_entry_queue(_rec())

    def test_physical_interaction_enterable_despite_blank_term(self):
        f2 = self.md.split("### F2. Physical interaction")[1].split("### F3.")[0]
        self.assertIn("GeneB", f2)          # interactor listed
        self.assertIn("pick PSI-MI at entry", f2)

    def test_pipe_in_data_is_escaped(self):
        rec = _rec(canto={"genes": [
            {"name": "wei|rd", "uniprot": "P1", "organism": "Fx", "locus": ""}]})
        md, _ = eq.render_entry_queue(rec)
        self.assertIn("wei\\|rd", md)       # escaped so the table can't corrupt

    def test_disease_name_uses_current_id(self):
        f5 = self.md.split("### F5. Disease annotation")[1].split("## G.")[0]
        self.assertIn("PHIDO:0000162", f5)


class IntegrityAndStatusTests(unittest.TestCase):
    def test_dangling_allele_reference_parked(self):
        # an allele pointing at an undefined gene must be parked, not entered
        rec = _rec(canto={"alleles": [
            {"name": "orphanΔ", "gene": "GhostGene", "type": "deletion", "expression": "null"}]})
        md, _ = eq.render_entry_queue(rec)
        b = md.split("## B. Create alleles")[1].split("## C.")[0]
        self.assertNotIn("orphanΔ", b)
        parked = md.split("## G. Parked items")[1]
        self.assertIn("orphanΔ", parked)
        self.assertIn("undefined gene", parked)

    def test_annotation_with_undefined_subject_parked(self):
        rec = _rec(canto={"annotations": [
            {"feature_type": "genotype", "feature": "NoSuchGenotype",
             "annotation_type": "pathogen_phenotype", "term_id": "PHIPO:0000001",
             "term_name": "x", "evidence": "y", "extensions": [], "conditions": "", "figure": "F1"}]})
        md, _ = eq.render_entry_queue(rec)
        parked = md.split("## G. Parked items")[1]
        self.assertIn("is not defined", parked)

    def test_status_passthrough(self):
        md, _ = eq.render_entry_queue(_rec(), status="validated")
        self.assertIn("Status: validated", md)

    def test_status_defaults_to_draft(self):
        md, _ = eq.render_entry_queue(_rec())
        self.assertIn("Status: draft (not validated)", md)


class ExplicitHoldTests(unittest.TestCase):
    def test_explicit_hold_parks_with_reason(self):
        rec = _rec(canto={"annotations": [
            {"feature_type": "genotype", "feature": "geneAΔ", "annotation_type": "pathogen_phenotype",
             "term_id": "PHIPO:0000001", "term_name": "some phenotype", "evidence": "assay",
             "extensions": [], "conditions": "PDA", "figure": "F1",
             "hold": True, "hold_reason": "penetrance not quantified — curator confirm"}]})
        md, _ = eq.render_entry_queue(rec)
        parked = md.split("## G. Parked items")[1]
        self.assertIn("penetrance not quantified", parked)
        # and it is NOT in the F3 entry table
        f3 = md.split("### F3. Pathogen phenotype")[1].split("### F4.")[0]
        self.assertNotIn("some phenotype", f3)

    def test_note_stays_out_of_entry_queue(self):
        rec = _rec(canto={"annotations": [
            {"feature_type": "genotype", "feature": "geneAΔ", "annotation_type": "pathogen_phenotype",
             "term_id": "PHIPO:0000001", "term_name": "enterable phenotype", "evidence": "assay",
             "extensions": [], "conditions": "PDA", "figure": "F1",
             "note": "SECRET-CURATOR-NOTE that must not appear in the lean queue"}]})
        md, _ = eq.render_entry_queue(rec)
        self.assertIn("enterable phenotype", md)          # the annotation is entered
        self.assertNotIn("SECRET-CURATOR-NOTE", md)       # but its note is not shown here


class GuardTests(unittest.TestCase):
    def _write(self, text):
        p = Path(tempfile.mkdtemp()) / "d.md"
        p.write_text(text, encoding="utf-8")
        return p

    def test_no_json_block_raises(self):
        p = self._write("# draft with no json block\n")
        with self.assertRaises(SystemExit):
            eq.queue_for_draft(p)

    def test_json_without_canto_raises(self):
        p = self._write("```json\n{\"meta\": {}}\n```\n")
        with self.assertRaises(SystemExit):
            eq.queue_for_draft(p)


if __name__ == "__main__":
    unittest.main()
