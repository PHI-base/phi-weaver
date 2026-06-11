#!/usr/bin/env python3
"""Network-free tests for validate_ontology_ids.py (HTTP getter is injected)."""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # scripts/
import validate_ontology_ids as v  # noqa: E402


def term(obo_id, label="some phenotype", obsolete=False):
    return {"obo_id": obo_id, "label": label, "is_obsolete": obsolete}


def ols_getter(terms, status=200):
    """Return an OLS /terms response wrapping the given embedded terms."""
    def _get(url, params):
        body = {"_embedded": {"terms": terms}} if terms else {"page": {"totalElements": 0}}
        return status, (body if status == 200 else None), {}
    return _get


class CountingGetter:
    def __init__(self, terms):
        self.terms, self.calls = terms, 0

    def __call__(self, url, params):
        self.calls += 1
        return 200, {"_embedded": {"terms": self.terms}}, {}


class FormatTests(unittest.TestCase):
    def test_valid_obo_formats(self):
        for good in ("PHIPO:0000001", "GO:0009405", "PHIDO:0000123"):
            prefix, ok = v.check_format(good)
            self.assertTrue(ok, good)
            self.assertEqual(prefix, good.split(":")[0])

    def test_short_or_long_obo_local_id_is_invalid(self):
        self.assertFalse(v.check_format("GO:12345")[1])      # too short
        self.assertFalse(v.check_format("GO:00094051")[1])   # too long
        self.assertFalse(v.check_format("PHIPO:abc1234")[1])  # non-numeric

    def test_uniprot_accession_formats(self):
        for good in ("P12345", "Q1AAA9", "A0A0B4J2F0", "P12345-2"):
            prefix, ok = v.check_format(f"UniProtKB:{good}")
            self.assertTrue(ok, good)
            self.assertEqual(prefix, "UniProtKB")
        self.assertFalse(v.check_format("UniProtKB:NOTANACC")[1])

    def test_uniprot_prefix_aliases_normalise(self):
        self.assertEqual(v.check_format("UNIPROT:P12345")[0], "UniProtKB")
        self.assertEqual(v.check_format("uniprotkb:P12345")[0], "UniProtKB")

    def test_unknown_prefix(self):
        self.assertEqual(v.check_format("FOO:0000001"), (None, False))
        self.assertEqual(v.check_format("no-colon"), (None, False))


class ValidateTests(unittest.TestCase):
    def test_exists_non_obsolete_passes(self):
        val = v.OntologyValidator(http_get=ols_getter([term("GO:0009405", "pathogenesis")]))
        r = val.validate("GO:0009405")
        self.assertEqual(r.existence, "exists")
        self.assertEqual(r.label, "pathogenesis")
        self.assertTrue(r.ok)

    def test_obsolete_fails(self):
        val = v.OntologyValidator(
            http_get=ols_getter([term("PHIPO:0000001", "old term", obsolete=True)]))
        r = val.validate("PHIPO:0000001")
        self.assertEqual(r.existence, "obsolete")
        self.assertFalse(r.ok)

    def test_not_found_fails(self):
        val = v.OntologyValidator(http_get=ols_getter([]))
        r = val.validate("PHIPO:0009999")
        self.assertEqual(r.existence, "not_found")
        self.assertFalse(r.ok)

    def test_format_invalid_short_circuits_without_http(self):
        def boom(url, params):
            raise AssertionError("must not hit the network on a bad-format ID")
        val = v.OntologyValidator(http_get=boom)
        r = val.validate("GO:123")
        self.assertEqual(r.existence, "format_invalid")
        self.assertFalse(r.ok)

    def test_unknown_prefix_short_circuits(self):
        r = v.OntologyValidator(http_get=ols_getter([])).validate("FOO:0000001")
        self.assertEqual(r.existence, "unknown_prefix")
        self.assertFalse(r.ok)

    def test_uniprot_is_format_checked_only_no_http(self):
        def boom(url, params):
            raise AssertionError("UniProt existence is query_uniprot.py's job")
        r = v.OntologyValidator(http_get=boom).validate("UniProtKB:P12345")
        self.assertEqual(r.existence, "format_checked_only")
        self.assertTrue(r.ok)

    def test_offline_mode_skips_lookup(self):
        def boom(url, params):
            raise AssertionError("format-only must not hit the network")
        r = v.OntologyValidator(http_get=boom).validate("GO:0009405", online=False)
        self.assertEqual(r.existence, "not_checked")
        self.assertTrue(r.format_valid)
        self.assertTrue(r.ok)  # opting out of the online check is not a failure

    def test_http_error_is_reported(self):
        val = v.OntologyValidator(http_get=ols_getter(None, status=500))
        r = val.validate("GO:0009405")
        self.assertEqual(r.existence, "error")
        self.assertIn("500", r.error)
        self.assertFalse(r.ok)

    def test_wrong_term_returned_is_not_a_match(self):
        # OLS returns a term, but not the one we asked for → not_found.
        val = v.OntologyValidator(http_get=ols_getter([term("GO:0000001")]))
        r = val.validate("GO:0009405")
        self.assertEqual(r.existence, "not_found")

    def test_cache_avoids_second_http_call(self):
        getter = CountingGetter([term("GO:0009405", "pathogenesis")])
        with tempfile.TemporaryDirectory() as d:
            cache = v.Cache(Path(d) / "c.sqlite")
            val = v.OntologyValidator(cache=cache, http_get=getter)
            first = val.validate("GO:0009405")
            second = val.validate("GO:0009405")
            cache.close()
        self.assertFalse(first.from_cache)
        self.assertTrue(second.from_cache)
        self.assertEqual(getter.calls, 1)


class ExtractionTests(unittest.TestCase):
    def test_extracts_and_dedupes_ids_in_order(self):
        text = (
            "We annotate PHIPO:0000022 (reduced virulence) and GO:0009405; the host gene "
            "UniProtKB:P12345 is involved. See also GO:0009405 again and PHIDO:0000007."
        )
        ids = v.extract_ids(text)
        self.assertEqual(
            ids, ["PHIPO:0000022", "GO:0009405", "UniProtKB:P12345", "PHIDO:0000007"])


if __name__ == "__main__":
    unittest.main()
