#!/usr/bin/env python3
"""Network-free tests for map_phenotype.py (the HTTP getter is injected)."""

import tempfile
import unittest
from pathlib import Path

from phiweaver.lookup import map_phenotype as m


def doc(obo_id, label, ontology="phipo", obsolete=None, synonyms=None):
    """An OLS search 'doc' entry."""
    return {"obo_id": obo_id, "label": label, "ontology_name": ontology,
            "is_obsolete": obsolete, "exact_synonyms": synonyms or []}


def search_getter(docs, status=200):
    """Return an OLS /search response wrapping the given docs."""
    def _get(url, params):
        body = {"response": {"docs": docs, "numFound": len(docs or [])}}
        return status, (body if status == 200 else None), {}
    return _get


class CountingGetter:
    def __init__(self, docs):
        self.docs, self.calls = docs, 0

    def __call__(self, url, params):
        self.calls += 1
        return 200, {"response": {"docs": self.docs}}, {}


class MapTests(unittest.TestCase):
    def test_match_returns_real_phipo_id(self):
        mp = m.PhenotypeMapper(
            http_get=search_getter([doc("PHIPO:0000015", "reduced virulence")]))
        r = mp.map("reduced virulence")
        self.assertEqual(r.status, "matched")
        self.assertEqual(r.candidates[0].obo_id, "PHIPO:0000015")
        self.assertTrue(r.candidates[0].exact)
        self.assertTrue(r.ok)

    def test_no_match_is_explicit_not_guessed(self):
        mp = m.PhenotypeMapper(http_get=search_getter([]))
        r = mp.map("no such phenotype anywhere")
        self.assertEqual(r.status, "no_match")
        self.assertEqual(r.candidates, [])
        self.assertTrue(r.ok)  # honest empty result is success, not failure

    def test_non_phipo_ids_are_filtered_out(self):
        # A PHIPO search surfaces imported PATO terms; keep only PHIPO ids.
        mp = m.PhenotypeMapper(http_get=search_getter([
            doc("PATO:0002147", "reduced virulence"),
            doc("PHIPO:0000015", "reduced virulence"),
        ]))
        r = mp.map("reduced virulence")
        self.assertEqual([c.obo_id for c in r.candidates], ["PHIPO:0000015"])

    def test_obsolete_terms_excluded(self):
        mp = m.PhenotypeMapper(http_get=search_getter([
            doc("PHIPO:0000001", "old term", obsolete=True),
            doc("PHIPO:0000015", "reduced virulence"),
        ]))
        r = mp.map("reduced virulence")
        self.assertEqual([c.obo_id for c in r.candidates], ["PHIPO:0000015"])

    def test_exact_match_ranked_first(self):
        mp = m.PhenotypeMapper(http_get=search_getter([
            doc("PHIPO:0000100", "slightly reduced virulence"),   # partial
            doc("PHIPO:0000015", "reduced virulence"),            # exact
        ]))
        r = mp.map("reduced virulence")
        self.assertEqual(r.candidates[0].obo_id, "PHIPO:0000015")
        self.assertTrue(r.candidates[0].exact)
        self.assertFalse(r.candidates[1].exact)

    def test_exact_synonym_counts_as_exact(self):
        mp = m.PhenotypeMapper(http_get=search_getter([
            doc("PHIPO:0000015", "reduced virulence", synonyms=["decreased virulence"]),
        ]))
        r = mp.map("decreased virulence")
        self.assertTrue(r.candidates[0].exact)

    def test_rows_limit_respected(self):
        docs = [doc(f"PHIPO:{i:07d}", f"phenotype {i}") for i in range(10)]
        mp = m.PhenotypeMapper(http_get=search_getter(docs))
        r = mp.map("phenotype", rows=3)
        self.assertEqual(len(r.candidates), 3)

    def test_http_error_reported_and_fails(self):
        mp = m.PhenotypeMapper(http_get=search_getter(None, status=500))
        r = mp.map("reduced virulence")
        self.assertEqual(r.status, "error")
        self.assertIn("500", r.error)
        self.assertFalse(r.ok)

    def test_empty_query_makes_no_http_call(self):
        def boom(url, params):
            raise AssertionError("empty query must not hit the network")
        mp = m.PhenotypeMapper(http_get=boom)
        r = mp.map("   ")
        self.assertEqual(r.status, "no_match")

    def test_cache_avoids_second_http_call(self):
        getter = CountingGetter([doc("PHIPO:0000015", "reduced virulence")])
        with tempfile.TemporaryDirectory() as d:
            cache = m.ResponseCache(Path(d) / "c.sqlite")
            mp = m.PhenotypeMapper(cache=cache, http_get=getter)
            first = mp.map("reduced virulence")
            second = mp.map("reduced virulence")
            cache.close()
        self.assertFalse(first.from_cache)
        self.assertTrue(second.from_cache)
        self.assertEqual(getter.calls, 1)

    def test_to_dict_is_json_friendly(self):
        mp = m.PhenotypeMapper(
            http_get=search_getter([doc("PHIPO:0000015", "reduced virulence")]))
        d = mp.map("reduced virulence").to_dict()
        self.assertEqual(d["candidates"][0]["obo_id"], "PHIPO:0000015")
        self.assertTrue(d["ok"])


class ReadPhrasesTests(unittest.TestCase):
    def test_reads_nonempty_noncomment_lines(self):
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "ph.txt"
            f.write_text("reduced virulence\n\n# a comment\nabnormal conidiation\n")
            self.assertEqual(
                m.read_phrases(str(f)),
                ["reduced virulence", "abnormal conidiation"])


if __name__ == "__main__":
    unittest.main()
