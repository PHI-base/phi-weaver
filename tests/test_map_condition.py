#!/usr/bin/env python3
"""Network-free tests for map_condition.py (offline over PHI-ECO; stdlib only)."""

import tempfile
import unittest
from pathlib import Path

from phiweaver.lookup import map_condition as mc


TINY_OBO = """format-version: 1.2

[Term]
id: PECO:0005224
name: rich medium

[Term]
id: PECO:0000005
name: standard temperature
synonym: "normal temperature" EXACT []

[Term]
id: PECO:0009999
name: grouping growth medium
subset: Grouping_terms

[Term]
id: PECO:0000002
name: obsolete old condition
is_obsolete: true

[Typedef]
id: part_of
name: part of
"""


class LoadTermsTests(unittest.TestCase):
    def _load(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "phi-eco.obo"
            p.write_text(TINY_OBO, encoding="utf-8")
            return mc.load_terms(p)

    def test_excludes_obsolete_and_grouping_and_typedef(self):
        ids = {t.obo_id for t in self._load()}
        self.assertEqual(ids, {"PECO:0005224", "PECO:0000005"})   # no grouping, obsolete, typedef

    def test_captures_synonyms(self):
        terms = {t.obo_id: t for t in self._load()}
        self.assertIn("normal temperature", terms["PECO:0000005"].synonyms)


class SearchTests(unittest.TestCase):
    TERMS = [
        mc.Term("PECO:0005224", "rich medium", ()),
        mc.Term("PECO:0005020", "minimal medium", ()),
        mc.Term("PECO:0000005", "standard temperature", ("normal temperature",)),
        mc.Term("PECO:0005242", "delivery mechanism: pathogen mycelium inoculation", ()),
    ]

    def test_exact_name_ranks_first(self):
        r = mc.search("rich medium", self.TERMS)
        self.assertEqual(r.status, "matched")
        self.assertEqual(r.candidates[0].obo_id, "PECO:0005224")

    def test_synonym_matches(self):
        r = mc.search("normal temperature", self.TERMS)
        self.assertEqual(r.candidates[0].obo_id, "PECO:0000005")

    def test_token_overlap_surfaces_related(self):
        r = mc.search("mycelium inoculation", self.TERMS)
        self.assertEqual(r.candidates[0].obo_id, "PECO:0005242")

    def test_no_match_is_explicit(self):
        r = mc.search("xylophone concerto", self.TERMS)
        self.assertEqual(r.status, "no_match")
        self.assertEqual(r.candidates, [])

    def test_rows_limits_results(self):
        r = mc.search("medium", self.TERMS, rows=1)
        self.assertEqual(len(r.candidates), 1)

    def test_prose_sharing_one_token_is_no_match(self):
        """Regression (2026-07-17): `search` used to keep anything scoring > 0, so a phrase
        that is not a condition at all came back with confident-looking candidates —
        "we grew the pathogen in the dark" starred `in vitro`. `no_match` must stay reachable:
        it is what gap detection and --log-gaps key on."""
        r = mc.search("we grew the pathogen in the dark", self.TERMS)
        self.assertEqual(r.status, "no_match")

    def test_star_means_exact_not_merely_first(self):
        """A weak top hit displayed as ★ reads as a confident match."""
        out = mc.format_human([mc.search("mycelium inoculation", self.TERMS)])
        self.assertNotIn("★", out)          # a partial match, however well ranked
        out = mc.format_human([mc.search("rich medium", self.TERMS)])
        self.assertIn("★", out)             # an exact one

    def test_min_score_is_honoured(self):
        r = mc.search("rich medium", self.TERMS, min_score=101.0)
        self.assertEqual(r.status, "no_match")


class BundledOntologyTests(unittest.TestCase):
    """End-to-end against the real vendored phi-eco.obo."""

    def test_known_terms_resolve(self):
        terms = mc.load_terms()
        self.assertGreater(len(terms), 100)
        by_name = {t.name: t.obo_id for t in terms}
        self.assertEqual(by_name.get("rich medium"), "PECO:0005224")
        self.assertEqual(by_name.get("delivery mechanism: pathogen mycelium inoculation"),
                         "PECO:0005242")

    def test_search_finds_delivery_mechanism(self):
        terms = mc.load_terms()
        r = mc.search("pathogen mycelium inoculation", terms)
        self.assertEqual(r.candidates[0].obo_id, "PECO:0005242")


if __name__ == "__main__":
    unittest.main()
