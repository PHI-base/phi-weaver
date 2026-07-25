#!/usr/bin/env python3
"""
Tests for phibase_index — "is this paper already curated in PHI-base?".

Network-free by design: the release download is an injectable ``fetch``, so every test
here runs offline and on a fresh clone.

The fixture reproduces four quirks observed in the real v4-19 release, because each one
silently corrupts a naive parse:

  * a **duplicated header row** as the first data row (would yield a phantom record whose
    every field is a column name, and a phantom PMID of ``"PMID"``);
  * ``Literature_source`` spelled ``Pubmed`` / ``PubMed`` / ``pubmed``;
  * records with **no PubMed ID** at all (``Not in PubMed``, an ISBN) — these set the
    recall ceiling the tool has to report on a miss;
  * one PMID carrying **many** records (genome-scale papers reach 709 in v4-19).
"""

import io
import json
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock

from phiweaver.lookup import phibase_index
from phiweaver.lookup.phibase_index import (
    MAX_LISTED,
    PhibaseReleaseError,
    build_index,
    ensure_release,
    format_report,
    load_index,
    normalise_pmid,
)

HEADER = ("Record ID,PHI_MolConn_ID,ProteinID,Gene_name,"
          "Pathogen_NCBI_species_Taxonomy ID,Pathogen_species,Experimental_strain,"
          "Disease_name,Host_NCBI_Taxonomy_ID,Experimental_host_species,"
          "Phenotype_of_mutant,Year_published,Literature_ID,Literature_source")

FIXTURE = "\n".join([
    HEADER,
    # The release repeats its own header as the first data row.
    HEADER,
    'Record 126,PHI:132,O13407,ABC1,318829,Magnaporthe oryzae,Guy11,"blast (rice)",'
    '4530,"Oryza sativa (related: rice)",reduced virulence,1999,9927411,Pubmed',
    "Record 200,PHI:200,Q00001,GENEA,5518,Fusarium graminearum,GZ3639,ear blight,"
    "4564,Triticum,reduced virulence,2011,22028654,PubMed",
    "Record 201,PHI:201,Q00002,GENEB,5518,Fusarium graminearum,GZ3639,ear blight,"
    "4564,Triticum,unaffected pathogenicity,2011,22028654,pubmed",
    # No usable PMID: neither of these can ever be found by PMID.
    "Record 300,PHI:300,Q00003,GENEC,5518,Fusarium graminearum,,,,,,,2020,,Not in PubMed",
    "Record 301,PHI:301,Q00004,GENED,5518,Fusarium graminearum,,,,,,,2019,"
    "978-1-908230-25-6,ISBN",
]) + "\n"

LEGACY_FIXTURE = "\n".join([
    HEADER.replace("Literature_ID", "PMID"),
    'Record 126,PHI:132,O13407,ABC1,318829,Magnaporthe oryzae,Guy11,"blast (rice)",'
    '4530,"Oryza sativa (related: rice)",reduced virulence,1999,9927411,Pubmed',
]) + "\n"


def write_fixture(directory, name="phi-base_test.csv", text=FIXTURE) -> Path:
    path = Path(directory) / name
    path.write_text(text, encoding="utf-8")
    return path


class NormalisePmidTests(unittest.TestCase):
    def test_accepts_prefix_whitespace_and_int(self):
        for raw in ("9927411", " 9927411 ", "PMID:9927411", "pmid: 9927411", 9927411):
            self.assertEqual(normalise_pmid(raw), "9927411")


class BuildIndexTests(unittest.TestCase):
    def setUp(self):
        self._tmp = TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.index = build_index(write_fixture(self._tmp.name))

    def test_skips_the_duplicated_header_row(self):
        # The phantom row's Literature_ID is the literal string "PMID".
        self.assertEqual(self.index.lookup("PMID"), [])
        self.assertNotIn("PMID", self.index.by_pmid)
        # 6 data rows minus the header repeat.
        self.assertEqual(self.index.n_records, 5)

    def test_indexes_case_variant_pubmed_sources(self):
        # 'Pubmed', 'PubMed' and 'pubmed' all appear in the real release.
        self.assertTrue(self.index.contains("9927411"))
        self.assertEqual(len(self.index.lookup("22028654")), 2)

    def test_counts_but_does_not_index_non_pubmed_records(self):
        self.assertEqual(self.index.n_non_pubmed, 2)  # 'Not in PubMed' + ISBN
        self.assertEqual(self.index.n_pmids, 2)

    def test_carries_the_cross_check_fields(self):
        rec = self.index.lookup("PMID:9927411")[0]
        self.assertEqual(rec.phi_id, "PHI:132")
        self.assertEqual(rec.gene_name, "ABC1")
        self.assertEqual(rec.protein_id, "O13407")
        # The taxon is the whole point: the draft had 148305, PHI-base says 318829.
        self.assertEqual(rec.pathogen_taxid, "318829")
        self.assertEqual(rec.pathogen_species, "Magnaporthe oryzae")
        self.assertEqual(rec.host_taxid, "4530")

    def test_accepts_the_legacy_pmid_column_name(self):
        # Releases up to v4-08 called the column 'PMID', not 'Literature_ID'.
        index = build_index(write_fixture(self._tmp.name, "legacy.csv", LEGACY_FIXTURE))
        self.assertTrue(index.contains("9927411"))

    def test_record_url_is_http_not_https(self):
        # Verified 2026-07-25: https://www.phi-base.org does not answer. Pinned so the
        # scheme is not "tidied up" into a dead link.
        url = self.index.lookup("9927411")[0].url
        self.assertTrue(url.startswith("http://www.phi-base.org/"), url)
        self.assertIn("PHI:132", url)

    def test_empty_file_is_an_error_not_an_empty_index(self):
        empty = Path(self._tmp.name) / "empty.csv"
        empty.write_text("", encoding="utf-8")
        with self.assertRaises(PhibaseReleaseError):
            build_index(empty)

    def test_missing_file_is_an_error(self):
        with self.assertRaises(PhibaseReleaseError):
            build_index(Path(self._tmp.name) / "nope.csv")


class FormatReportTests(unittest.TestCase):
    def setUp(self):
        self._tmp = TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.index = build_index(write_fixture(self._tmp.name))

    def test_hit_reports_accession_taxon_and_link(self):
        text = format_report("9927411", self.index.lookup("9927411"), self.index)
        self.assertIn("ALREADY CURATED", text)
        self.assertIn("PHI:132", text)
        self.assertIn("taxid 318829", text)
        self.assertIn("http://www.phi-base.org/", text)
        self.assertIn("don't re-draft", text)
        self.assertIn(self.index.release, text)  # provenance

    def test_miss_states_the_recall_ceiling_and_never_claims_uncurated(self):
        text = format_report("404", [], self.index)
        self.assertIn("not found", text)
        self.assertIn("Not proof it is uncurated", text)
        self.assertIn("PHI-Canto sessions", text)
        self.assertIn("2 record(s)", text)  # the measured non-PubMed count
        # Must not assert the paper is uncurated.
        self.assertNotIn("ALREADY CURATED", text)

    def test_long_hit_is_truncated_and_summarised(self):
        records = self.index.lookup("22028654") * 200  # 400 records
        text = format_report("22028654", records, self.index)
        self.assertIn("(400 records)", text)
        self.assertEqual(text.count("http://www.phi-base.org/"), MAX_LISTED)
        self.assertIn(f"{400 - MAX_LISTED} further record(s)", text)
        self.assertIn("Fusarium graminearum", text)


class EnsureReleaseTests(unittest.TestCase):
    def setUp(self):
        self._tmp = TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.calls = []

    def _fetch(self, url):
        self.calls.append(url)
        return FIXTURE.encode("utf-8")

    def test_downloads_once_then_reuses_the_cache(self):
        for _ in range(3):
            path = ensure_release("r.csv", self._tmp.name, fetch=self._fetch)
        self.assertEqual(len(self.calls), 1)
        self.assertTrue(path.exists())
        self.assertIn("PHI-base/data", self.calls[0])

    def test_refresh_re_downloads(self):
        ensure_release("r.csv", self._tmp.name, fetch=self._fetch)
        ensure_release("r.csv", self._tmp.name, refresh=True, fetch=self._fetch)
        self.assertEqual(len(self.calls), 2)

    def test_empty_download_raises_and_leaves_no_cache_file(self):
        with self.assertRaises(PhibaseReleaseError):
            ensure_release("r.csv", self._tmp.name, fetch=lambda url: b"")
        self.assertEqual(list(Path(self._tmp.name).glob("*")), [])

    def test_no_partial_file_survives_a_successful_download(self):
        ensure_release("r.csv", self._tmp.name, fetch=self._fetch)
        self.assertEqual([p.name for p in Path(self._tmp.name).glob("*.part")], [])

    def test_load_index_parses_the_downloaded_release(self):
        index = load_index("r.csv", self._tmp.name, fetch=self._fetch)
        self.assertEqual(index.release, "r.csv")
        self.assertTrue(index.contains("9927411"))


class CliTests(unittest.TestCase):
    def setUp(self):
        self._tmp = TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        write_fixture(self._tmp.name, "r.csv")

    def _run(self, *args):
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = phibase_index.main(["--release", "r.csv", "--cache", self._tmp.name, *args])
        return code, buf.getvalue()

    def test_reports_a_hit_and_a_miss_together(self):
        code, out = self._run("9927411", "404")
        self.assertEqual(code, 0)
        self.assertIn("ALREADY CURATED", out)
        self.assertIn("not found", out)

    def test_json_output_is_machine_readable(self):
        code, out = self._run("PMID:9927411", "404", "--json")
        self.assertEqual(code, 0)
        payload = json.loads(out)
        self.assertEqual(payload["release"], "r.csv")
        self.assertEqual(payload["non_pubmed_records"], 2)
        by_pmid = {r["pmid"]: r for r in payload["results"]}
        self.assertEqual(by_pmid["9927411"]["status"], "curated")
        self.assertEqual(by_pmid["9927411"]["records"][0]["pathogen_taxid"], "318829")
        self.assertEqual(by_pmid["404"]["status"], "not_found")
        self.assertEqual(by_pmid["404"]["records"], [])

    def test_unfetchable_release_exits_non_zero_without_a_traceback(self):
        # Patched, not left to hit the network: an uncached release would otherwise send a
        # real request from the test suite.
        def boom(url):
            raise OSError("no route to host")

        with mock.patch.object(phibase_index, "_default_fetch", boom):
            buf = io.StringIO()
            with redirect_stdout(buf), redirect_stderr(io.StringIO()):
                code = phibase_index.main(
                    ["--release", "absent.csv", "--cache", self._tmp.name, "9927411"])
        self.assertEqual(code, 2)


if __name__ == "__main__":
    unittest.main()
