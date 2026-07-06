#!/usr/bin/env python3
"""Network-free tests for phiweaver.canto.worksheet (stdlib only)."""

import tempfile
import unittest
from pathlib import Path

from phiweaver.canto import worksheet as ws

# A compact fixture in the shape of a draft's `canto` block (modelled on the TOX2 draft).
REC = {
    "meta": {"pmid": "41020836", "paper": "Han et al. 2025",
             "system": "F. pseudograminearum -> wheat", "model": "Fable 5", "date": "2026-07-05"},
    "flags": [{"category": "needs_accession", "detail": "confirm strain-2035 gene"}],
    "canto": {
        "genes": [{"name": "FpTox2", "uniprot": "K3V6Z9",
                   "organism": "Fusarium pseudograminearum", "locus": "FPSE_10647",
                   "note": "TrEMBL; CS3096 ortholog"}],
        "alleles": [{"name": "∆FpTox2", "gene": "FpTox2", "type": "deletion", "expression": "null"}],
        "genotypes": [
            {"name": "wild type 2035", "organism": "Fusarium pseudograminearum",
             "alleles": [], "role": "control"},
            {"name": "∆FpTox2", "organism": "Fusarium pseudograminearum",
             "alleles": ["∆FpTox2"], "role": "experimental"},
            {"name": "host wt", "organism": "Triticum aestivum", "alleles": [], "role": "control"},
        ],
        "metagenotypes": [
            {"name": "∆FpTox2 x wheat", "pathogen_genotype": "∆FpTox2",
             "host_genotype": "host wt", "role": "experimental"},
        ],
        "annotations": [
            {"feature_type": "genotype", "feature": "∆FpTox2",
             "annotation_type": "pathogen_phenotype", "term_id": "PHIPO:0001212",
             "term_name": "decreased hyphal growth", "evidence": "cell growth assay",
             "extensions": [], "conditions": "PDA, 25C, 3d", "figure": "Fig 2A,B"},
            {"feature_type": "metagenotype", "feature": "∆FpTox2 x wheat",
             "annotation_type": "pathogen_host_interaction_phenotype", "term_id": "PHIPO:0000015",
             "term_name": "reduced virulence", "evidence": "macroscopic observation",
             "extensions": [{"relation": "infects_tissue", "value": "coleoptile"},
                            {"relation": "compared_to_control", "value": "wt 2035; ∆FpTox2-C"}],
             "conditions": "7 dpi", "figure": "Fig 5"},
        ],
    },
}


class RenderTests(unittest.TestCase):
    def setUp(self):
        self.md = ws.render_worksheet(REC)

    def test_header_has_pmid_and_model(self):
        self.assertIn("PMID:41020836", self.md)
        self.assertIn("Model: Fable 5", self.md)

    def test_sections_in_canto_entry_order(self):
        order = [self.md.index(h) for h in
                 ("## 1. Genes", "## 2. Alleles", "## 3. Genotypes",
                  "## 4. Metagenotypes", "## 5. Annotations", "## 6. Submit")]
        self.assertEqual(order, sorted(order))

    def test_gene_shows_uniprot_accession(self):
        self.assertIn("UniProtKB:K3V6Z9", self.md)
        self.assertIn("(locus FPSE_10647)", self.md)

    def test_wildtype_genotype_has_no_alleles(self):
        self.assertIn("wild type 2035 — Fusarium pseudograminearum — alleles: wild type", self.md)

    def test_metagenotype_role_uppercased(self):
        self.assertIn("∆FpTox2 × host wt — EXPERIMENTAL", self.md)

    def test_annotation_line_and_extensions(self):
        self.assertIn("reduced virulence — PHIPO:0000015", self.md)
        # extensions joined with ' · ' so a value's own '; ' stays unambiguous
        self.assertIn("infects_tissue=coleoptile · compared_to_control=wt 2035; ∆FpTox2-C", self.md)

    def test_flags_surfaced(self):
        self.assertIn("## Flags to resolve", self.md)
        self.assertIn("[needs_accession]", self.md)
        self.assertIn("flag(s) to resolve", self.md)   # count line shown only when flags present


class MissingTermTests(unittest.TestCase):
    def test_annotation_without_term_is_flagged_inline(self):
        rec = {"meta": {"pmid": "1"}, "canto": {"annotations": [
            {"feature_type": "genotype", "feature": "g", "annotation_type": "pathogen_phenotype",
             "term_id": "", "term_name": "reduced DON production", "evidence": "ELISA"}]}}
        md = ws.render_worksheet(rec)
        self.assertIn("⚠ reduced DON production — NO TERM", md)


class GuardTests(unittest.TestCase):
    def _write(self, tmp, body):
        p = Path(tmp) / "draft.md"
        p.write_text(body, encoding="utf-8")
        return str(p)

    def test_no_json_block_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(SystemExit):
                ws.worksheet_for_draft(self._write(tmp, "# draft with no json block\n"))

    def test_json_block_without_canto_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            body = '# d\n\n```json\n{"meta": {"pmid": "1"}}\n```\n'
            with self.assertRaises(SystemExit):
                ws.worksheet_for_draft(self._write(tmp, body))


class EmptyBlockTests(unittest.TestCase):
    def test_empty_canto_renders_none_sections(self):
        md = ws.render_worksheet({"meta": {"pmid": "9"}, "canto": {}})
        self.assertIn("## 1. Genes", md)
        self.assertIn("_(none)_", md)


if __name__ == "__main__":
    unittest.main()
