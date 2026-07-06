#!/usr/bin/env python3
"""Network-free tests for phiweaver.benchmark_report (temp CSV, stdlib only)."""

import tempfile
import unittest
from pathlib import Path

from phiweaver import benchmark_report as br

CSV = """paper,group,curatable,captured,tokens,ID,Pheno
A,curated,4,4,12000,Correct,Needs improvement
B,control,5,3,9000,Incorrect,N/A
"""


def write(tmp):
    p = Path(tmp) / "scores.csv"
    p.write_text(CSV, encoding="utf-8")
    return str(p)


class LoadTests(unittest.TestCase):
    def test_items_and_papers(self):
        with tempfile.TemporaryDirectory() as tmp:
            papers, items = br.load(write(tmp))
            self.assertEqual(items, ["ID", "Pheno"])          # fixed cols (incl. tokens) excluded
            self.assertEqual([p.name for p in papers], ["A", "B"])
            self.assertEqual(papers[1].group, "control")
            self.assertEqual(papers[0].tokens, 12000)         # supplied token count read


class ScoreTests(unittest.TestCase):
    def test_accuracy_and_completeness(self):
        with tempfile.TemporaryDirectory() as tmp:
            papers, _ = br.load(write(tmp))
            a, b = papers
            self.assertEqual(a.accuracy, 0.75)     # (1 + 0.5) / 2
            self.assertEqual(a.completeness, 1.0)  # 4/4
            self.assertEqual(b.accuracy, 0.0)      # Incorrect=0; N/A excluded -> 1 applicable
            self.assertEqual(b.completeness, 0.6)  # 3/5

    def test_item_accuracy_ignores_na(self):
        with tempfile.TemporaryDirectory() as tmp:
            papers, items = br.load(write(tmp))
            ia = br.item_accuracy(papers, items)
            self.assertEqual(ia["ID"], 0.5)        # mean(Correct=1, Incorrect=0)
            self.assertEqual(ia["Pheno"], 0.5)     # only A scored (NI=0.5); B is N/A


class RenderTests(unittest.TestCase):
    def test_html_has_sections_and_data(self):
        with tempfile.TemporaryDirectory() as tmp:
            papers, items = br.load(write(tmp))
            out = br.render_html(papers, items)
            self.assertIn("<!doctype html>", out)
            self.assertIn("Accuracy", out)                 # per-paper section
            self.assertIn("where to improve", out)         # item-accuracy section
            self.assertIn("mean accuracy (control)", out)  # control group present
            self.assertIn("Needs imp.", out)               # a status label rendered

    def test_provenance_and_tokens(self):
        with tempfile.TemporaryDirectory() as tmp:
            papers, items = br.load(write(tmp))
            out = br.render_html(papers, items, model="claude-fable-5",
                                 source="scores.csv", generated="2026-07-04 09:00")
            self.assertIn("model claude-fable-5", out)     # model version in provenance
            self.assertIn("generated 2026-07-04 09:00", out)
            self.assertIn("source scores.csv", out)        # file location
            self.assertIn("21,000", out)                   # total curation tokens (12000+9000)


class ModelColumnTests(unittest.TestCase):
    CSV = ("paper,group,model,curatable,captured,ID\n"
           "A,curated,Fable 5,4,4,Correct\n"
           "B,curated,Fable 5,3,3,Correct\n")

    def _load(self, tmp):
        p = Path(tmp) / "m.csv"
        p.write_text(self.CSV, encoding="utf-8")
        return br.load(str(p))

    def test_model_column_is_not_an_item(self):
        with tempfile.TemporaryDirectory() as tmp:
            papers, items = self._load(tmp)
            self.assertEqual(items, ["ID"])                # model is a reserved column
            self.assertEqual(papers[0].model, "Fable 5")

    def test_model_derived_from_csv_when_no_flag(self):
        with tempfile.TemporaryDirectory() as tmp:
            papers, items = self._load(tmp)
            out = br.render_html(papers, items)            # no explicit model=
            self.assertIn("model Fable 5", out)

    def test_explicit_model_overrides_csv(self):
        with tempfile.TemporaryDirectory() as tmp:
            papers, items = self._load(tmp)
            out = br.render_html(papers, items, model="Opus 4.8")
            self.assertIn("model Opus 4.8", out)
            self.assertNotIn("model Fable 5", out)


if __name__ == "__main__":
    unittest.main()
