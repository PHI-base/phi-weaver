#!/usr/bin/env python3
"""Tests for the curation-example index generator (network-free, temp dir)."""

import tempfile
import unittest
from pathlib import Path

from phiweaver import curation_examples as ce

EXAMPLE_A = """---
type: curation-example
status: validated
topics:
  - effector
  - gene-deletion
annotation_types:
  - interaction-phenotype
source: PMID:111
pathogen: Fusarium graminearum
---
body
"""

EXAMPLE_B = """---
type: curation-example
status: draft
topics:
  - gene-deletion
source: PMID:222
---
body
"""

NOT_AN_EXAMPLE = """---
type: something-else
---
body
"""


def write_dir(tmp, files):
    d = Path(tmp) / "curation-examples"
    d.mkdir()
    for name, content in files.items():
        (d / name).write_text(content, encoding="utf-8")
    return d


class DiscoverTests(unittest.TestCase):
    def test_discovers_only_curation_examples(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = write_dir(tmp, {"a.md": EXAMPLE_A, "b.md": EXAMPLE_B,
                                "other.md": NOT_AN_EXAMPLE, "_TEMPLATE.md": EXAMPLE_A,
                                "INDEX.md": "x", "TAGS.md": "x"})
            names = sorted(e.name for e in ce.discover_examples(d))
            self.assertEqual(names, ["a", "b"])  # template/index/tags/other excluded

    def test_parses_tags_and_scalars(self):
        with tempfile.TemporaryDirectory() as tmp:
            e = ce.discover_examples(write_dir(tmp, {"a.md": EXAMPLE_A}))[0]
            self.assertEqual(e.status, "validated")
            self.assertEqual(e.topics, ["effector", "gene-deletion"])
            self.assertEqual(e.pathogen, "Fusarium graminearum")
            self.assertEqual(e.source, "PMID:111")

    def test_missing_dir_is_empty(self):
        self.assertEqual(ce.discover_examples(Path("/no/such/dir")), [])


class RenderTests(unittest.TestCase):
    def test_groups_by_topic_and_counts(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = ce.render_index(ce.discover_examples(
                write_dir(tmp, {"a.md": EXAMPLE_A, "b.md": EXAMPLE_B})))
            self.assertIn("1 validated", out)
            self.assertIn("### effector", out)      # topic grouping
            self.assertIn("### gene-deletion", out)
            self.assertIn("[[a]]", out)
            self.assertIn("[[b]]", out)

    def test_empty_library_message(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp) / "curation-examples"
            d.mkdir()
            self.assertIn("No examples yet", ce.render_index(ce.discover_examples(d)))


class ValidateTests(unittest.TestCase):
    def test_flags_missing_topics_and_bad_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad = "---\ntype: curation-example\nstatus: bogus\nsource: PMID:9\n---\n"
            problems = ce.validate_examples(ce.discover_examples(
                write_dir(tmp, {"bad.md": bad})))
            joined = " ".join(problems)
            self.assertIn("topics", joined)   # required field missing
            self.assertIn("status", joined)   # 'bogus' not an allowed status

    def test_valid_example_has_no_problems(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(
                ce.validate_examples(ce.discover_examples(
                    write_dir(tmp, {"a.md": EXAMPLE_A}))), [])


if __name__ == "__main__":
    unittest.main()
