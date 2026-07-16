#!/usr/bin/env python3
"""Network-free tests for validate_ontology_ids.py (HTTP getter is injected)."""

import tempfile
import unittest
from pathlib import Path

from phiweaver.lookup import validate_ontology_ids as v


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
        for good in ("PHIPO:0000001", "GO:0009405", "PHIDO:0000123", "BTO:0000268"):
            prefix, ok = v.check_format(good)
            self.assertTrue(ok, good)
            self.assertEqual(prefix, good.split(":")[0])

    def test_short_or_long_obo_local_id_is_invalid(self):
        self.assertFalse(v.check_format("GO:12345")[1])      # too short
        self.assertFalse(v.check_format("GO:00094051")[1])   # too long
        self.assertFalse(v.check_format("PHIPO:abc1234")[1])  # non-numeric

    def test_mod_uses_five_digit_local_id(self):
        prefix, ok = v.check_format("MOD:00696")
        self.assertEqual(prefix, "MOD")
        self.assertTrue(ok)
        self.assertFalse(v.check_format("MOD:0696")[1])       # 4 digits — too short
        self.assertFalse(v.check_format("MOD:0000696")[1])    # 7 digits — too long for MOD

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

    def test_mod_resolves_via_ols(self):
        val = v.OntologyValidator(
            http_get=ols_getter([term("MOD:00696", "phosphorylated residue")]))
        r = val.validate("MOD:00696")
        self.assertEqual(r.existence, "exists")
        self.assertEqual(r.label, "phosphorylated residue")
        self.assertTrue(r.ok)

    def test_bto_resolves_via_ols(self):
        # BRENDA tissue (host-tissue extension) resolves online like GO/PHIPO/MOD.
        val = v.OntologyValidator(http_get=ols_getter([term("BTO:0000268", "coleoptile")]))
        r = val.validate("BTO:0000268")
        self.assertEqual(r.prefix, "BTO")
        self.assertEqual(r.existence, "exists")
        self.assertEqual(r.label, "coleoptile")
        self.assertTrue(r.ok)

    def test_bto_not_found_fails(self):
        r = v.OntologyValidator(http_get=ols_getter([])).validate("BTO:9999999")
        self.assertEqual(r.existence, "not_found")
        self.assertFalse(r.ok)

    def test_find_term_prefers_defining_ontology(self):
        # OLS echoes one obo_id from several ontologies; the non-defining cross-reference
        # carries a placeholder label. We must pick the defining ontology's own entry.
        body = {"_embedded": {"terms": [
            {"obo_id": "MOD:00696", "label": "MOD_00696", "is_defining_ontology": False},
            {"obo_id": "MOD:00696", "label": "phosphorylated residue",
             "is_defining_ontology": True},
        ]}}
        self.assertEqual(v._find_term(body, "MOD:00696")["label"], "phosphorylated residue")

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


class PhidoOfflineTests(unittest.TestCase):
    """PHIDO is not on OLS4, so it resolves offline against the bundled .obo.
    These inject a tiny index so they never touch the filesystem or the network."""

    INDEX = {
        "PHIDO:0000164": ("Fusarium wilt", False),
        "PHIDO:0000002": ("obsolete abortion", True),
    }

    def _validator(self, index):
        def boom(url, params):
            raise AssertionError("PHIDO must not hit OLS/the network")
        return v.OntologyValidator(http_get=boom, phido_index=index)

    def test_existing_phido_passes(self):
        r = self._validator(self.INDEX).validate("PHIDO:0000164")
        self.assertEqual(r.existence, "exists")
        self.assertEqual(r.label, "Fusarium wilt")
        self.assertEqual(r.source, v.PHIDO_SOURCE)
        self.assertTrue(r.ok)

    def test_obsolete_phido_fails(self):
        r = self._validator(self.INDEX).validate("PHIDO:0000002")
        self.assertEqual(r.existence, "obsolete")
        self.assertFalse(r.ok)

    def test_missing_phido_is_not_found(self):
        r = self._validator(self.INDEX).validate("PHIDO:0009999")
        self.assertEqual(r.existence, "not_found")
        self.assertFalse(r.ok)

    def test_format_only_skips_phido_lookup(self):
        r = self._validator(self.INDEX).validate("PHIDO:0000164", online=False)
        self.assertEqual(r.existence, "not_checked")
        self.assertTrue(r.ok)

    def test_missing_ontology_file_is_reported_not_silently_passed(self):
        # index None models an unreadable bundled file: honest error, not not_found.
        r = self._validator(None).validate("PHIDO:0000164")
        self.assertEqual(r.existence, "error")
        self.assertFalse(r.ok)

    def test_bundled_ontology_loads_and_has_fusarium_wilt(self):
        # Exercises the real bundled file end-to-end (the term that used to false-fail).
        r = v.OntologyValidator().validate("PHIDO:0000164")
        self.assertEqual(r.existence, "exists")
        self.assertEqual(r.label, "Fusarium wilt")


class PecoOfflineTests(unittest.TestCase):
    """PHI-ECO (PECO) is PHI-base-local (OLS 'peco' is the unrelated Planteome ontology),
    so it resolves offline against the bundled phi-eco.obo. Injected index → no network."""

    INDEX = {
        "PECO:0005028": ("delivery mechanism: agrobacterium", False),
        "PECO:0000002": ("obsolete condition", True),
    }

    def _validator(self, index):
        def boom(url, params):
            raise AssertionError("PECO must not hit OLS/the network")
        return v.OntologyValidator(http_get=boom, peco_index=index)

    def test_existing_peco_passes(self):
        r = self._validator(self.INDEX).validate("PECO:0005028")
        self.assertEqual(r.existence, "exists")
        self.assertEqual(r.label, "delivery mechanism: agrobacterium")
        self.assertEqual(r.source, v.PHI_ECO_SOURCE)
        self.assertTrue(r.ok)

    def test_obsolete_peco_fails(self):
        r = self._validator(self.INDEX).validate("PECO:0000002")
        self.assertEqual(r.existence, "obsolete")
        self.assertFalse(r.ok)

    def test_missing_peco_is_not_found(self):
        r = self._validator(self.INDEX).validate("PECO:0009999")
        self.assertEqual(r.existence, "not_found")
        self.assertFalse(r.ok)

    def test_missing_ontology_file_is_reported_not_silently_passed(self):
        # index None models an unreadable bundled file: honest error, not not_found.
        r = self._validator(None).validate("PECO:0005028")
        self.assertEqual(r.existence, "error")
        self.assertFalse(r.ok)

    def test_bundled_ontology_loads_and_has_delivery_term(self):
        # Exercises the real bundled phi-eco.obo end-to-end.
        r = v.OntologyValidator().validate("PECO:0005028")
        self.assertEqual(r.existence, "exists")
        self.assertEqual(r.label, "delivery mechanism: agrobacterium")


class PhipoExtOfflineTests(unittest.TestCase):
    """PHIPO_EXT is a SEPARATE PHI-base ontology of extension-only terms (gene-for-gene
    values), not part of PHIPO and not on OLS, so it resolves offline against the bundled
    phipo_ext.obo. Injected index → no network."""

    INDEX = {
        "PHIPO_EXT:0000001": ("gene-for-gene interaction phenotype", False),
        "PHIPO_EXT:0000099": ("obsolete extension term", True),
    }

    def _validator(self, index):
        def boom(url, params):
            raise AssertionError("PHIPO_EXT must not hit OLS/the network")
        return v.OntologyValidator(http_get=boom, phipo_ext_index=index)

    def test_format_and_split(self):
        prefix, ok = v.check_format("PHIPO_EXT:0000001")
        self.assertEqual(prefix, "PHIPO_EXT")
        self.assertTrue(ok)
        # the shared PHIPO prefix must not swallow PHIPO_EXT
        self.assertEqual(v.check_format("PHIPO:0000015")[0], "PHIPO")

    def test_existing_phipo_ext_passes(self):
        r = self._validator(self.INDEX).validate("PHIPO_EXT:0000001")
        self.assertEqual(r.existence, "exists")
        self.assertEqual(r.label, "gene-for-gene interaction phenotype")
        self.assertEqual(r.source, v.PHIPO_EXT_SOURCE)
        self.assertTrue(r.ok)

    def test_obsolete_phipo_ext_fails(self):
        r = self._validator(self.INDEX).validate("PHIPO_EXT:0000099")
        self.assertEqual(r.existence, "obsolete")
        self.assertFalse(r.ok)

    def test_missing_phipo_ext_is_not_found(self):
        r = self._validator(self.INDEX).validate("PHIPO_EXT:0009999")
        self.assertEqual(r.existence, "not_found")
        self.assertFalse(r.ok)

    def test_extraction_picks_up_both_prefixes(self):
        ids = v.extract_ids("gene-for-gene PHIPO_EXT:0000001 with PHIPO:0000015")
        self.assertEqual(ids, ["PHIPO_EXT:0000001", "PHIPO:0000015"])

    def test_bundled_ontology_loads_end_to_end(self):
        # Exercises the real bundled phipo_ext.obo (offline; no network).
        r = v.OntologyValidator().validate("PHIPO_EXT:0000001")
        self.assertEqual(r.existence, "exists")
        self.assertEqual(r.label, "gene-for-gene interaction phenotype")


class FypoExtOfflineTests(unittest.TestCase):
    """FYPO_EXT is a small PomBase extension ontology (penetrance/severity values), not on
    OLS, resolved offline against the bundled fypo_extension.obo."""

    def test_format_and_split(self):
        prefix, ok = v.check_format("FYPO_EXT:0000001")
        self.assertEqual(prefix, "FYPO_EXT")
        self.assertTrue(ok)

    def test_real_values_pass(self):
        # high / medium / low / complete are the real penetrance/severity values.
        val = v.OntologyValidator()
        r = val.validate("FYPO_EXT:0000001")
        self.assertEqual(r.existence, "exists")
        self.assertEqual(r.label, "high")
        self.assertEqual(r.source, v.FYPO_EXT_SOURCE)
        self.assertTrue(r.ok)
        self.assertTrue(val.validate("FYPO_EXT:0000003").ok)  # low

    def test_missing_id_not_found(self):
        # 1000001/1000002 are config grouping-roots, not defined as terms in the file.
        r = v.OntologyValidator().validate("FYPO_EXT:1000001")
        self.assertEqual(r.existence, "not_found")
        self.assertFalse(r.ok)

    def test_no_network_used(self):
        def boom(url, params):
            raise AssertionError("FYPO_EXT must not hit OLS/the network")
        r = v.OntologyValidator(http_get=boom).validate("FYPO_EXT:0000004")
        self.assertEqual(r.existence, "exists")
        self.assertEqual(r.label, "complete")

    def test_extraction_distinguishes_phipo_ext_and_fypo_ext(self):
        ids = v.extract_ids("PHIPO_EXT:0000001, FYPO_EXT:0000001, PHIPO:0000015")
        self.assertEqual(ids, ["PHIPO_EXT:0000001", "FYPO_EXT:0000001", "PHIPO:0000015"])


class LoaderTests(unittest.TestCase):
    def test_load_phido_parses_terms_and_obsolete_flags(self):
        idx = v._load_phido()
        self.assertIsNotNone(idx)
        self.assertIn("PHIDO:0000164", idx)
        self.assertEqual(idx["PHIDO:0000164"], ("Fusarium wilt", False))
        self.assertTrue(idx["PHIDO:0000002"][1])  # obsolete abortion

    def test_load_phido_missing_file_returns_none(self):
        self.assertIsNone(v._load_phido(v.Path("/no/such/phido.obo")))


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
