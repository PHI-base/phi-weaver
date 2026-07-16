#!/usr/bin/env python3
"""Network-free tests for query_uniprot.py (HTTP getter is injected)."""

import tempfile
import unittest
from pathlib import Path

from phiweaver.lookup import query_uniprot as qu


def entry(acc, gene, reviewed=True, taxon=5518, func="Dephosphorylates a substrate.",
          experimental=True):
    return {
        "entryType": "UniProtKB reviewed (Swiss-Prot)" if reviewed
        else "UniProtKB unreviewed (TrEMBL)",
        "primaryAccession": acc,
        "uniProtkbId": f"{gene}_FUSGR",
        "proteinDescription": {"recommendedName": {"fullName": {"value": "Test protein"}}},
        "genes": [{"geneName": {"value": gene},
                   "orderedLocusNames": [{"value": "FGSG_11164"}]}],
        "organism": {"scientificName": "Fusarium graminearum", "taxonId": taxon},
        "comments": [{"commentType": "FUNCTION", "texts": [{
            "value": func,
            "evidences": [{"evidenceCode": "ECO:0000269"}] if experimental
            else [{"evidenceCode": "ECO:0000256"}],
        }]}],
    }


def search_getter(results, release="2026_02"):
    def _get(url, params):
        return 200, {"results": results}, {"x-uniprot-release": release}
    return _get


class TaxonAwareGetter:
    """Returns `species_results` when the query carries `organism_id:<species>`, else
    `relaxed_results` (the organism-filter-dropped retry). Counts calls."""

    def __init__(self, species, species_results, relaxed_results, release="2026_02"):
        self.species = species
        self.species_results = species_results
        self.relaxed_results = relaxed_results
        self.release = release
        self.calls = 0

    def __call__(self, url, params):
        self.calls += 1
        q = params.get("query", "")
        results = self.species_results if f"organism_id:{self.species}" in q \
            else self.relaxed_results
        return 200, {"results": results}, {"x-uniprot-release": self.release}


class CountingGetter:
    def __init__(self, body, release="2026_02"):
        self.body, self.release, self.calls = body, release, 0

    def __call__(self, url, params):
        self.calls += 1
        return 200, self.body, {"x-uniprot-release": self.release}


class LookupTests(unittest.TestCase):
    def test_found_single_reviewed(self):
        client = qu.UniProtClient(http_get=search_getter([entry("P12345", "FgTPP1")]))
        r = client.lookup(gene="FgTPP1", organism_id=5518)
        self.assertEqual(r.status, "found")
        self.assertEqual(len(r.candidates), 1)
        c = r.candidates[0]
        self.assertEqual(c["accession"], "P12345")
        self.assertTrue(c["reviewed"])
        self.assertIn("FGSG_11164", c["gene_names"])
        self.assertEqual(r.uniprot_release, "2026_02")

    def test_ambiguous_multiple_candidates(self):
        getter = search_getter([entry("P11111", "geneA"), entry("P22222", "geneB")])
        r = qu.UniProtClient(http_get=getter).lookup(gene="amb")
        self.assertEqual(r.status, "ambiguous")
        self.assertEqual(len(r.candidates), 2)

    def test_not_found(self):
        r = qu.UniProtClient(http_get=search_getter([])).lookup(gene="nope")
        self.assertEqual(r.status, "not_found")
        self.assertEqual(r.candidates, [])

    def test_no_input_is_error(self):
        r = qu.UniProtClient(http_get=search_getter([])).lookup()
        self.assertEqual(r.status, "error")

    def test_reviewed_sorts_before_unreviewed(self):
        getter = search_getter([
            entry("P_TREMBL", "g", reviewed=False),
            entry("P_SWISS", "g", reviewed=True),
        ])
        r = qu.UniProtClient(http_get=getter).lookup(gene="g")
        self.assertEqual(r.candidates[0]["accession"], "P_SWISS")
        self.assertTrue(r.candidates[0]["reviewed"])

    def test_function_evidence_labels(self):
        exp = qu.UniProtClient(http_get=search_getter([entry("A", "g", experimental=True)]))
        inf = qu.UniProtClient(http_get=search_getter([entry("B", "g", experimental=False)]))
        self.assertTrue(exp.lookup(gene="g").candidates[0]["function_has_experimental_evidence"])
        self.assertFalse(inf.lookup(gene="g").candidates[0]["function_has_experimental_evidence"])

    def test_http_error_returns_error_status(self):
        def boom(url, params):
            return 500, None, {}
        r = qu.UniProtClient(http_get=boom).lookup(gene="x")
        self.assertEqual(r.status, "error")
        self.assertIn("500", r.error)

    def test_accession_direct_fetch(self):
        def direct(url, params):
            self.assertIn("/uniprotkb/P12345.json", url)
            return 200, entry("P12345", "FgTPP1"), {"x-uniprot-release": "2026_02"}
        r = qu.UniProtClient(http_get=direct).lookup(accession="P12345")
        self.assertEqual(r.status, "found")
        self.assertEqual(r.candidates[0]["accession"], "P12345")

    def test_locus_tag_strain_fallback(self):
        # Species-taxon search is empty; the entry lives under a strain taxon (child).
        getter = TaxonAwareGetter(
            species=101028,
            species_results=[],
            relaxed_results=[entry("K3UT42", "FpSdhA", taxon=1028729)])
        r = qu.UniProtClient(http_get=getter).lookup(
            locus_tag="FPSE_04172", organism_id=101028)
        self.assertEqual(r.status, "found")
        self.assertTrue(r.organism_filter_relaxed)
        self.assertEqual(r.candidates[0]["accession"], "K3UT42")
        self.assertEqual(r.candidates[0]["organism_id"], 1028729)
        self.assertEqual(getter.calls, 2)  # species search + relaxed retry

    def test_no_fallback_when_species_hits(self):
        getter = TaxonAwareGetter(
            species=101028,
            species_results=[entry("P00001", "FpSdhA", taxon=101028)],
            relaxed_results=[entry("SHOULD_NOT_APPEAR", "x")])
        r = qu.UniProtClient(http_get=getter).lookup(
            locus_tag="FPSE_04172", organism_id=101028)
        self.assertEqual(r.status, "found")
        self.assertFalse(r.organism_filter_relaxed)
        self.assertEqual(r.candidates[0]["accession"], "P00001")
        self.assertEqual(getter.calls, 1)  # no retry needed

    def test_fallback_still_not_found(self):
        getter = TaxonAwareGetter(
            species=101028, species_results=[], relaxed_results=[])
        r = qu.UniProtClient(http_get=getter).lookup(
            locus_tag="FPSE_04172", organism_id=101028)
        self.assertEqual(r.status, "not_found")
        self.assertFalse(r.organism_filter_relaxed)
        self.assertEqual(getter.calls, 2)  # retry attempted, also empty

    def test_gene_only_search_does_not_trigger_fallback(self):
        # A gene search (no locus tag) must not broaden across taxa.
        getter = TaxonAwareGetter(
            species=101028, species_results=[], relaxed_results=[entry("X", "g")])
        r = qu.UniProtClient(http_get=getter).lookup(gene="SdhA", organism_id=101028)
        self.assertEqual(r.status, "not_found")
        self.assertFalse(r.organism_filter_relaxed)
        self.assertEqual(getter.calls, 1)

    def test_cache_avoids_second_http_call(self):
        getter = CountingGetter({"results": [entry("P12345", "FgTPP1")]})
        with tempfile.TemporaryDirectory() as d:
            cache = qu.Cache(Path(d) / "c.sqlite")
            client = qu.UniProtClient(cache=cache, http_get=getter)
            first = client.lookup(gene="FgTPP1", organism_id=5518)
            second = client.lookup(gene="FgTPP1", organism_id=5518)
            cache.close()
        self.assertFalse(first.from_cache)
        self.assertTrue(second.from_cache)
        self.assertEqual(getter.calls, 1)
        self.assertEqual(second.candidates[0]["accession"], "P12345")


if __name__ == "__main__":
    unittest.main()
