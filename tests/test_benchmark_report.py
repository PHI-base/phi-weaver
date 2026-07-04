#!/usr/bin/env python3
"""Network-free tests for phiweaver.benchmark_report (temp CSV, stdlib only)."""

import tempfile
import unittest
from pathlib import Path

from phiweaver import benchmark_report as br

CSV = """paper,group,curatable,captured,ID,Pheno
A,curated,4,4,Correct,Needs improvement
B,control,5,3,Incorrect,N/A
"""


def write(tmp):
    p = Path(tmp) / "scores.csv"
    p.write_text(CSV, encoding="utf-8")
    return str(p)


class LoadTests(unittest.TestCase):
    def test_items_and_papers(self):
        with tempfile.TemporaryDirectory() as tmp:
            papers, items = br.load(write(tmp))
            self.assertEqual(items, ["ID", "Pheno"])          # fixed cols excluded
            self.assertEqual([p.name for p in papers], ["A", "B"])
            self.assertEqual(papers[1].group, "control")


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


if __name__ == "__main__":
    unittest.main()
