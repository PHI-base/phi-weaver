#!/usr/bin/env python3
"""Network-free tests for europepmc.py.

Fixtures are trimmed from real Europe PMC responses recorded 2026-07-24 (PMID:39852455
open access; PMID:1537802 / PMC206556 not open access). Every test stubs the single HTTP
chokepoint ``europepmc._get``, so the suite never touches the network.
"""

import io
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from phiweaver.jats import europepmc as ep


# --- recorded fixtures -------------------------------------------------------------

OA_RESULT = {
    "id": "39852455", "source": "MED", "pmid": "39852455", "pmcid": "PMC11767236",
    "doi": "10.3390/jof11010036",
    "title": "Roles of the <i>Sec2p</i> Gene in the Growth and Pathogenicity Regulation",
    "journalInfo": {"journal": {"title": "Journal of fungi"}}, "pubYear": "2025",
    "isOpenAccess": "Y", "inEPMC": "Y", "inPMC": "Y", "hasPDF": "Y", "hasSuppl": "Y",
    "hasTextMinedTerms": "Y", "license": "cc by",
}

CLOSED_RESULT = {
    "id": "1537802", "source": "MED", "pmid": "1537802", "pmcid": "PMC206556",
    "doi": "10.1128/jb.174.4.1327-1329.1992",
    "title": "The cloned avirulence gene avrPto induces disease resistance",
    "journalInfo": {"journal": {"title": "Journal of bacteriology"}}, "pubYear": "1992",
    "isOpenAccess": "N", "inEPMC": "Y", "inPMC": "Y", "hasPDF": "Y", "hasSuppl": "N",
}

PREPRINT_RESULT = {
    "id": "PPR123456", "source": "PPR", "pmid": "", "pmcid": "",
    "doi": "10.1101/2025.01.01.000001", "title": "A preprint",
    "journalInfo": {}, "pubYear": "2025", "isOpenAccess": "Y", "hasPDF": "Y",
}

# Europe PMC signals "not open access" on supplementaryFiles with HTTP 200 + this body.
ERROR_BEAN = (b'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
              b'<errorBean><errCode>0</errCode>'
              b'<errMsg>Article with id PMC206556 is not open access one</errMsg></errorBean>')

FULL_TEXT_XML = b'<?xml version="1.0"?><article><front/><body><p>text</p></body></article>'


def _search_body(results, hit_count=None):
    return json.dumps({
        "hitCount": len(results) if hit_count is None else hit_count,
        "resultList": {"result": results},
    }).encode("utf-8")


def _zip_bytes(names):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        for n in names:
            z.writestr(n, b"payload")
    return buf.getvalue()


class _StubHTTP:
    """Route stubbed responses by URL substring; records the calls and their cache arg."""

    def __init__(self, routes):
        self.routes = routes
        self.calls = []
        self.caches = []

    def __call__(self, url, timeout=ep.TIMEOUT, cache=None):
        self.calls.append(url)
        self.caches.append(cache)
        for needle, response in self.routes.items():
            if needle in url:
                return response
        return (404, b"", "")


def _patch(test, routes):
    stub = _StubHTTP(routes)
    original = ep._get
    ep._get = stub
    test.addCleanup(lambda: setattr(ep, "_get", original))
    return stub


# --- tests -------------------------------------------------------------------------

class IdentifierTests(unittest.TestCase):
    def test_classifies_each_identifier_type(self):
        self.assertEqual(ep.classify_identifier("39852455"), "pmid")
        self.assertEqual(ep.classify_identifier("PMC11767236"), "pmcid")
        self.assertEqual(ep.classify_identifier("pmc11767236"), "pmcid")
        self.assertEqual(ep.classify_identifier("10.3390/jof11010036"), "doi")
        self.assertEqual(ep.classify_identifier("doi:10.3390/jof11010036"), "doi")

    def test_rejects_nonsense(self):
        for bad in ("", "not-an-id", "PMCX", "10.3390"):
            with self.assertRaises(ep.EuropePMCError):
                ep.classify_identifier(bad)

    def test_query_forms(self):
        self.assertEqual(ep._query_for("39852455"), "EXT_ID:39852455")
        self.assertEqual(ep._query_for("PMC11767236"), "PMCID:PMC11767236")
        self.assertEqual(ep._query_for("10.3390/jof11010036"), "DOI:10.3390/jof11010036")
        self.assertEqual(ep._query_for("doi:10.3390/x"), "DOI:10.3390/x")

    def test_article_ref_is_composite_not_a_separate_id(self):
        # There is no distinct "Europe PMC ID": for a MEDLINE record id IS the PMID.
        record = ep._record_from(OA_RESULT)
        record["source"], record["id"] = "MED", "39852455"
        self.assertEqual(ep.article_ref(record), "MED:39852455")
        self.assertEqual(record["id"], record["pmid"])


class ResolveTests(unittest.TestCase):
    def test_resolves_open_access_record(self):
        _patch(self, {"/search": (200, _search_body([OA_RESULT]), "application/json")})
        r = ep.resolve("39852455")
        self.assertTrue(r["found"])
        self.assertEqual(r["pmcid"], "PMC11767236")
        self.assertTrue(r["is_open_access"])
        self.assertFalse(r["ambiguous"])
        self.assertEqual(r["title"], "Roles of the Sec2p Gene in the Growth and "
                                     "Pathogenicity Regulation")  # markup stripped

    def test_network_failure_degrades_without_raising(self):
        _patch(self, {"/search": (0, b"", "")})
        r = ep.resolve("39852455")
        self.assertFalse(r["found"])
        self.assertIn("failed", r["error"])

    def test_no_hits_reported_not_invented(self):
        _patch(self, {"/search": (200, _search_body([]), "application/json")})
        r = ep.resolve("99999999")
        self.assertFalse(r["found"])
        self.assertEqual(r["hit_count"], 0)

    def test_multiple_hits_flagged_ambiguous(self):
        _patch(self, {"/search": (200, _search_body([OA_RESULT, CLOSED_RESULT]),
                                  "application/json")})
        r = ep.resolve("10.3390/jof11010036")
        self.assertTrue(r["ambiguous"])
        self.assertEqual(r["other_hits"], ["MED:1537802"])

    def test_unparseable_body_degrades(self):
        _patch(self, {"/search": (200, b"<html>nope", "text/html")})
        self.assertFalse(ep.resolve("39852455")["found"])


class RouteTests(unittest.TestCase):
    def test_open_access_routes_to_jats(self):
        self.assertEqual(ep.route_for(ep._record_from(OA_RESULT) | {"found": True}),
                         ep.ROUTE_JATS)

    def test_pmcid_without_open_access_does_not_route_to_jats(self):
        # The whole point: a PMCID exists here, but full text is not retrievable.
        record = ep._record_from(CLOSED_RESULT) | {"found": True}
        self.assertTrue(record["pmcid"])
        self.assertEqual(ep.route_for(record), ep.ROUTE_PDF)

    def test_no_pdf_and_no_oa_routes_to_abstract(self):
        record = ep._record_from(CLOSED_RESULT) | {"found": True, "has_pdf": False}
        self.assertEqual(ep.route_for(record), ep.ROUTE_ABSTRACT)

    def test_unresolved_falls_back_to_pdf(self):
        self.assertEqual(ep.route_for({"found": False}), ep.ROUTE_PDF)


class FetchTests(unittest.TestCase):
    def test_full_text_returned_for_open_access(self):
        _patch(self, {"/fullTextXML": (200, FULL_TEXT_XML, "application/xml")})
        self.assertEqual(ep.fetch_full_text("PMC11767236"), FULL_TEXT_XML)

    def test_full_text_404_returns_empty(self):
        _patch(self, {"/fullTextXML": (404, b"", "")})
        self.assertEqual(ep.fetch_full_text("PMC206556"), b"")

    def test_supplementary_error_bean_is_not_mistaken_for_content(self):
        # HTTP 200 with an errorBean body is the trap this guards.
        _patch(self, {"/supplementaryFiles": (200, ERROR_BEAN, "application/xml")})
        self.assertEqual(ep.fetch_supplementary("PMC206556"), b"")

    def test_supplementary_rejects_non_zip_payload(self):
        _patch(self, {"/supplementaryFiles": (200, b"not a zip", "application/zip")})
        self.assertEqual(ep.fetch_supplementary("PMC11767236"), b"")

    def test_supplementary_returns_zip(self):
        blob = _zip_bytes(["a-g001.jpg"])
        _patch(self, {"/supplementaryFiles": (200, blob, "application/zip")})
        self.assertEqual(ep.fetch_supplementary("PMC11767236"), blob)

    def test_empty_pmcid_short_circuits(self):
        stub = _patch(self, {})
        self.assertEqual(ep.fetch_full_text(""), b"")
        self.assertEqual(ep.fetch_supplementary(""), b"")
        self.assertEqual(stub.calls, [])


class ExtractMediaTests(unittest.TestCase):
    def test_splits_images_from_other_payloads(self):
        blob = _zip_bytes(["jof-g001.jpg", "jof-g001.gif", "jof-s001.zip", "notes.txt"])
        with tempfile.TemporaryDirectory() as d:
            out = ep.extract_media(blob, d)
            self.assertEqual(out["images"], ["jof-g001.gif", "jof-g001.jpg"])
            self.assertEqual(out["others"], ["jof-s001.zip", "notes.txt"])
            self.assertTrue((Path(d) / "jof-g001.jpg").exists())

    def test_archive_paths_are_flattened_not_trusted(self):
        blob = _zip_bytes(["../../escape.jpg", "nested/dir/fig.png"])
        with tempfile.TemporaryDirectory() as d:
            out = ep.extract_media(blob, d)
            self.assertEqual(out["images"], ["escape.jpg", "fig.png"])
            for name in out["images"]:
                self.assertTrue((Path(d) / name).exists())

    def test_empty_blob_is_safe(self):
        with tempfile.TemporaryDirectory() as d:
            out = ep.extract_media(b"", d)
            self.assertEqual(out["images"], [])


class AcquireTests(unittest.TestCase):
    def test_open_access_acquires_xml_and_images(self):
        blob = _zip_bytes(["jof-g001.jpg", "jof-g002.jpg", "jof-s001.zip"])
        _patch(self, {
            "/search": (200, _search_body([OA_RESULT]), "application/json"),
            "/fullTextXML": (200, FULL_TEXT_XML, "application/xml"),
            "/supplementaryFiles": (200, blob, "application/zip"),
        })
        with tempfile.TemporaryDirectory() as d:
            m = ep.acquire("39852455", d)
            self.assertEqual(m["route"], ep.ROUTE_JATS)
            self.assertEqual(m["article_ref"], "MED:39852455")
            self.assertTrue(Path(m["xml_path"]).exists())
            self.assertEqual(Path(m["xml_path"]).name, "PMC11767236.xml")
            self.assertEqual(m["media"]["images"], ["jof-g001.jpg", "jof-g002.jpg"])
            self.assertTrue(any("figure image" in n for n in m["notes"]))

    def test_non_open_access_stops_before_fetching_and_says_why(self):
        stub = _patch(self, {
            "/search": (200, _search_body([CLOSED_RESULT]), "application/json"),
        })
        with tempfile.TemporaryDirectory() as d:
            m = ep.acquire("1537802", d)
            self.assertEqual(m["route"], ep.ROUTE_PDF)
            self.assertEqual(m["xml_path"], "")
            self.assertTrue(any("not open access" in n for n in m["notes"]))
            # It must not have wasted a call on a request that always 404s.
            self.assertFalse(any("fullTextXML" in c for c in stub.calls))

    def test_open_access_flag_but_missing_xml_falls_back_to_pdf(self):
        _patch(self, {
            "/search": (200, _search_body([OA_RESULT]), "application/json"),
            "/fullTextXML": (404, b"", ""),
        })
        with tempfile.TemporaryDirectory() as d:
            m = ep.acquire("39852455", d)
            self.assertEqual(m["route"], ep.ROUTE_PDF)
            self.assertTrue(any("fall back" in n for n in m["notes"]))

    def test_preprint_is_flagged_as_a_scope_decision(self):
        _patch(self, {"/search": (200, _search_body([PREPRINT_RESULT]), "application/json")})
        with tempfile.TemporaryDirectory() as d:
            m = ep.acquire("10.1101/2025.01.01.000001", d)
            self.assertTrue(any("preprint" in n for n in m["notes"]))

    def test_lookup_failure_reports_and_recommends_pdf(self):
        _patch(self, {"/search": (0, b"", "")})
        with tempfile.TemporaryDirectory() as d:
            m = ep.acquire("39852455", d)
            self.assertEqual(m["route"], ep.ROUTE_PDF)
            self.assertTrue(any("fall back to a local PDF" in n for n in m["notes"]))

    def test_no_media_flag_skips_the_zip(self):
        stub = _patch(self, {
            "/search": (200, _search_body([OA_RESULT]), "application/json"),
            "/fullTextXML": (200, FULL_TEXT_XML, "application/xml"),
        })
        with tempfile.TemporaryDirectory() as d:
            ep.acquire("39852455", d, fetch_media=False)
            self.assertFalse(any("supplementaryFiles" in c for c in stub.calls))


class ResponseCacheTests(unittest.TestCase):
    def _cache(self):
        d = tempfile.TemporaryDirectory()
        self.addCleanup(d.cleanup)
        return ep.ResponseCache(d.name)

    def test_roundtrip(self):
        c = self._cache()
        c.put("https://x/y", 200, b"payload", "application/xml")
        status, body, ctype, cached_at = c.get("https://x/y")
        self.assertEqual((status, body, ctype), (200, b"payload", "application/xml"))
        self.assertTrue(cached_at)

    def test_miss_returns_none(self):
        self.assertIsNone(self._cache().get("https://x/never-fetched"))

    def test_distinct_urls_do_not_collide(self):
        c = self._cache()
        c.put("https://x/a", 200, b"A", "")
        c.put("https://x/b", 200, b"B", "")
        self.assertEqual(c.get("https://x/a")[1], b"A")
        self.assertEqual(c.get("https://x/b")[1], b"B")

    def test_binary_payload_survives(self):
        # The whole reason this is not the shared JSON/SQLite cache: zips and XML.
        c = self._cache()
        blob = _zip_bytes(["fig-g001.jpg"])
        c.put("https://x/suppl", 200, blob, "application/zip")
        self.assertEqual(c.get("https://x/suppl")[1], blob)
        self.assertTrue(zipfile.ZipFile(io.BytesIO(c.get("https://x/suppl")[1])).namelist())

    def test_corrupt_sidecar_is_a_miss_not_an_error(self):
        c = self._cache()
        c.put("https://x/y", 200, b"payload", "")
        for side in Path(c.path).glob("*.json"):
            side.write_text("{ not json", encoding="utf-8")
        self.assertIsNone(c.get("https://x/y"))

    def test_sidecar_records_provenance(self):
        c = self._cache()
        c.put("https://x/y", 200, b"payload", "application/xml")
        meta = json.loads(next(Path(c.path).glob("*.json")).read_text(encoding="utf-8"))
        self.assertEqual(meta["url"], "https://x/y")
        self.assertEqual(meta["bytes"], len(b"payload"))
        self.assertEqual(meta["content_type"], "application/xml")


class CachedGetTests(unittest.TestCase):
    """_get is the single chokepoint, so caching is tested there."""

    def _cache(self):
        d = tempfile.TemporaryDirectory()
        self.addCleanup(d.cleanup)
        return ep.ResponseCache(d.name)

    def _counting_urlopen(self, status=200, body=b"ok", raise_http=None):
        calls = []

        class _Resp:
            def __init__(self):
                self.status, self.headers = status, {"Content-Type": "application/json"}

            def read(self):
                return body

            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False

        def fake(request, timeout=None):
            calls.append(getattr(request, "full_url", request))
            if raise_http:
                raise raise_http
            return _Resp()

        original = ep.urllib.request.urlopen
        ep.urllib.request.urlopen = fake
        self.addCleanup(lambda: setattr(ep.urllib.request, "urlopen", original))
        return calls

    def test_second_call_is_served_from_cache(self):
        calls = self._counting_urlopen()
        cache = self._cache()
        first = ep._get("https://x/y", cache=cache)
        second = ep._get("https://x/y", cache=cache)
        self.assertEqual(first, second)
        self.assertEqual(len(calls), 1, "second call should not hit the network")

    def test_without_a_cache_every_call_hits_the_network(self):
        calls = self._counting_urlopen()
        ep._get("https://x/y")
        ep._get("https://x/y")
        self.assertEqual(len(calls), 2)

    def test_404_is_not_cached_because_embargoes_lift(self):
        err = ep.urllib.error.HTTPError("https://x/y", 404, "Not Found", {}, None)
        calls = self._counting_urlopen(raise_http=err)
        cache = self._cache()
        self.assertEqual(ep._get("https://x/y", cache=cache), (404, b"", ""))
        self.assertEqual(ep._get("https://x/y", cache=cache), (404, b"", ""))
        self.assertEqual(len(calls), 2, "a 404 must be retried, not remembered")

    def test_network_failure_is_not_cached(self):
        calls = self._counting_urlopen(raise_http=OSError("down"))
        cache = self._cache()
        ep._get("https://x/y", cache=cache)
        ep._get("https://x/y", cache=cache)
        self.assertEqual(len(calls), 2)

    def test_empty_200_is_not_cached(self):
        calls = self._counting_urlopen(body=b"")
        cache = self._cache()
        ep._get("https://x/y", cache=cache)
        ep._get("https://x/y", cache=cache)
        self.assertEqual(len(calls), 2)

    def test_cache_is_threaded_through_acquire(self):
        blob = _zip_bytes(["g001.jpg"])
        stub = _patch(self, {
            "/search": (200, _search_body([OA_RESULT]), "application/json"),
            "/fullTextXML": (200, FULL_TEXT_XML, "application/xml"),
            "/supplementaryFiles": (200, blob, "application/zip"),
        })
        cache = self._cache()
        with tempfile.TemporaryDirectory() as d:
            ep.acquire("39852455", d, cache=cache)
        # Every network call in acquire must carry the cache through, not drop it —
        # a dropped kwarg is silent and would re-download the multi-MB zip each run.
        self.assertEqual(len(stub.calls), 3)
        self.assertTrue(all(c is cache for c in stub.caches), stub.caches)

    def test_default_cache_path_honours_env_var(self):
        import os
        original = os.environ.get("EPMC_CACHE")
        os.environ["EPMC_CACHE"] = "/tmp/epmc-test-cache"
        try:
            self.assertEqual(ep.default_cache_path(), "/tmp/epmc-test-cache")
        finally:
            if original is None:
                del os.environ["EPMC_CACHE"]
            else:
                os.environ["EPMC_CACHE"] = original


class AnnotationsTests(unittest.TestCase):
    def test_annotations_parsed(self):
        body = json.dumps([{"annotations": [
            {"type": "Organisms", "exact": "mice"},
            {"type": "Gene_Proteins", "exact": "GEF"},
        ]}]).encode("utf-8")
        _patch(self, {"annotationsByArticleIds": (200, body, "application/json")})
        anns = ep.fetch_annotations("MED:39852455")
        self.assertEqual(len(anns), 2)

    def test_failure_returns_empty_list(self):
        _patch(self, {"annotationsByArticleIds": (500, b"", "")})
        self.assertEqual(ep.fetch_annotations("MED:39852455"), [])

    def test_client_bug_cannot_abort_a_conversion(self):
        # Enrichment must degrade, not propagate: a broken _get signature once surfaced
        # as "conversion failed" on an otherwise perfect conversion.
        from phiweaver.jats import jats_convert as jc
        original = ep._get
        ep._get = lambda url: (_ for _ in ()).throw(TypeError("bad signature"))
        try:
            self.assertEqual(jc.resolve_ids_from_doi("10.3390/jof11010036"), {})
        finally:
            ep._get = original

    def test_docstring_records_the_known_error_rate(self):
        # The caveat is load-bearing: these annotations must never become evidence.
        doc = ep.fetch_annotations.__doc__
        self.assertIn("Triage aid only", doc)
        self.assertIn("P0CF32", doc)


if __name__ == "__main__":
    unittest.main()
