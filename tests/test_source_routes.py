#!/usr/bin/env python3
"""Tests for the shared ingest-route vocabulary and its two consumers.

The point of the shared module is that the curation outputs and the tracking DB describe
the same paper the same way, so these tests pin both ends against one vocabulary.
"""

import sqlite3
import unittest

from phiweaver import source_routes as sr
from phiweaver.canto import entry_queue as eq
from phiweaver.tracking import ingest_provenance as ip
from phiweaver.tracking.migrations import run_migrations


class VocabularyTests(unittest.TestCase):
    def test_routes_infer_from_extension(self):
        self.assertEqual(sr.route_from_filename("paper.pdf"), "pdf")
        self.assertEqual(sr.route_from_filename("paper.xml"), "jats-publisher")
        self.assertEqual(sr.route_from_filename("PMC1.nxml"), "jats-europepmc")
        self.assertEqual(sr.route_from_filename("paper.PDF"), "pdf")

    def test_unknown_extension_is_blank_not_guessed(self):
        self.assertEqual(sr.route_from_filename("paper.docx"), "")
        self.assertEqual(sr.route_from_filename(""), "")

    def test_aliases_normalise(self):
        self.assertEqual(sr.normalise_route("europepmc-jats-with-figures"), "jats-europepmc")
        self.assertEqual(sr.normalise_route("XML"), "jats-publisher")
        self.assertEqual(sr.normalise_route("pdf"), "pdf")

    def test_unknown_route_passes_through(self):
        self.assertEqual(sr.normalise_route("something-new"), "something-new")

    def test_figure_availability_by_route(self):
        self.assertTrue(sr.figures_available("pdf"))
        self.assertTrue(sr.figures_available("jats-europepmc"))
        self.assertFalse(sr.figures_available("jats-publisher"))

    def test_explicit_flag_overrides_the_route(self):
        # A publisher XML whose images were fetched separately is no longer captions-only,
        # and a Europe PMC fetch whose zip failed is not as rich as its route implies.
        self.assertTrue(sr.figures_available("jats-publisher", figures_inspected=True))
        self.assertFalse(sr.figures_available("jats-europepmc", figures_inspected=False))


class DescribeSourceTests(unittest.TestCase):
    def test_europepmc_route_reads_as_figures_retrieved(self):
        line = sr.describe_source({"source_route": "jats-europepmc",
                                   "source_file": "PMC11767236.xml"})
        self.assertIn("Europe PMC JATS XML", line)
        self.assertIn("PMC11767236.xml", line)
        self.assertIn("figure images retrieved", line)
        self.assertNotIn("⚠️", line)

    def test_publisher_xml_is_warned_as_captions_only(self):
        line = sr.describe_source({"source_file": "jof-11-00036.xml"})
        self.assertIn("publisher JATS XML", line)
        self.assertIn("CAPTIONS ONLY", line)
        self.assertIn("⚠️", line)

    def test_pdf_route(self):
        line = sr.describe_source({"source_file": "paper.pdf"})
        self.assertIn("PDF", line)
        self.assertIn("figures embedded", line)

    def test_figures_inspected_flag_wins(self):
        line = sr.describe_source({"source_file": "jof.xml", "figures_inspected": True})
        self.assertIn("figure panels inspected", line)
        self.assertNotIn("CAPTIONS ONLY", line)

    def test_unrecorded_route_says_so_rather_than_guessing(self):
        line = sr.describe_source({"source_file": "paper.docx"})
        self.assertIn("route not recorded", line)
        self.assertIn("⚠️", line)

    def test_no_source_recorded_yields_nothing(self):
        self.assertEqual(sr.describe_source({}), "")


class EntryQueueHeaderTests(unittest.TestCase):
    def _render(self, meta):
        rec = {"meta": meta, "canto": {"genes": [], "alleles": [], "genotypes": [],
                                       "metagenotypes": [], "annotations": []}}
        text, _counts = eq.render_entry_queue(rec)
        return text

    def test_source_line_appears_before_the_first_table(self):
        text = self._render({"pmid": "39852455", "source_route": "jats-europepmc",
                             "source_file": "PMC11767236.xml"})
        self.assertIn("**Curated from:** Europe PMC JATS XML", text)
        self.assertLess(text.index("Curated from"), text.index("## A. Enter genes"))

    def test_captions_only_warning_reaches_the_queue(self):
        text = self._render({"pmid": "1", "source_file": "jof-11-00036.xml"})
        self.assertIn("CAPTIONS ONLY", text)

    def test_queue_without_source_metadata_still_renders(self):
        text = self._render({"pmid": "1"})
        self.assertNotIn("Curated from", text)
        self.assertIn("## A. Enter genes", text)


class IngestProvenanceDBTests(unittest.TestCase):
    def _db(self):
        conn = sqlite3.connect(":memory:")
        run_migrations(conn)
        self.addCleanup(conn.close)
        return conn

    def _article(self, conn, pmid="39852455", title="Sec2p paper"):
        conn.execute("INSERT INTO articles (pmid, title) VALUES (?, ?)", (pmid, title))
        conn.commit()

    def test_migration_adds_the_columns(self):
        conn = self._db()
        cols = {r[1] for r in conn.execute("PRAGMA table_info(articles)")}
        self.assertIn("source_route", cols)
        self.assertIn("source_file", cols)
        self.assertIn("figures_available", cols)

    def test_records_route_against_an_article(self):
        conn = self._db()
        self._article(conn)
        self.assertTrue(ip.record(conn, pmid="39852455", route="jats-europepmc",
                                  source_file="PMC11767236.xml", figures_inspected=True))
        row = conn.execute(
            "SELECT source_route, source_file, figures_available FROM articles"
            " WHERE pmid = '39852455'").fetchone()
        self.assertEqual(row, ("jats-europepmc", "PMC11767236.xml", 1))

    def test_alias_is_normalised_on_write(self):
        conn = self._db()
        self._article(conn)
        ip.record(conn, pmid="39852455", route="europepmc-jats-with-figures")
        row = conn.execute(
            "SELECT source_route FROM articles WHERE pmid = '39852455'").fetchone()
        self.assertEqual(row[0], "jats-europepmc")

    def test_figures_derived_from_route_when_not_stated(self):
        conn = self._db()
        self._article(conn)
        ip.record(conn, pmid="39852455", route="jats-publisher")
        row = conn.execute(
            "SELECT figures_available FROM articles WHERE pmid = '39852455'").fetchone()
        self.assertEqual(row[0], 0)

    def test_no_matching_article_does_not_invent_one(self):
        conn = self._db()
        self.assertFalse(ip.record(conn, pmid="00000", route="pdf"))
        self.assertEqual(conn.execute("SELECT COUNT(*) FROM articles").fetchone()[0], 0)

    def test_falls_back_to_title_when_no_pmid(self):
        conn = self._db()
        self._article(conn, pmid=None, title="untitled-stem")
        self.assertTrue(ip.record(conn, route="pdf", title="untitled-stem"))

    def test_captions_only_query_is_the_revisit_list(self):
        conn = self._db()
        self._article(conn, pmid="1", title="captions only")
        self._article(conn, pmid="2", title="with figures")
        ip.record(conn, pmid="1", route="jats-publisher")
        ip.record(conn, pmid="2", route="jats-europepmc")
        rows = ip.captions_only_articles(conn)
        self.assertEqual([r["pmid"] for r in rows], ["1"])

    def test_route_counts(self):
        conn = self._db()
        self._article(conn, pmid="1", title="a")
        self._article(conn, pmid="2", title="b")
        ip.record(conn, pmid="1", route="pdf")
        ip.record(conn, pmid="2", route="pdf")
        counts = {r["source_route"]: r["article_count"] for r in ip.route_counts(conn)}
        self.assertEqual(counts["pdf"], 2)

    def test_v2_coverage_columns_exist_and_record(self):
        conn = self._db()
        self._article(conn)
        ip.record(conn, pmid="39852455", route="jats-europepmc",
                  figures_inspected=True, figures_read=6, figures_total=7)
        row = conn.execute(
            "SELECT figures_inspected, figures_total FROM articles"
            " WHERE pmid = '39852455'").fetchone()
        self.assertEqual(row, (6, 7))

    def test_unread_figure_articles_is_distinct_from_captions_only(self):
        conn = self._db()
        self._article(conn, pmid="1", title="figures available, not all read")
        self._article(conn, pmid="2", title="figures available, all read")
        self._article(conn, pmid="3", title="captions only")
        ip.record(conn, pmid="1", route="jats-europepmc", figures_read=2, figures_total=7)
        ip.record(conn, pmid="2", route="jats-europepmc", figures_read=7, figures_total=7)
        ip.record(conn, pmid="3", route="jats-publisher")
        self.assertEqual([r["pmid"] for r in ip.unread_figure_articles(conn)], ["1"])
        self.assertEqual([r["pmid"] for r in ip.captions_only_articles(conn)], ["3"])

    def test_pre_existing_articles_read_as_unknown_not_backfilled(self):
        conn = self._db()
        self._article(conn)
        row = conn.execute(
            "SELECT source_route, figures_available FROM articles").fetchone()
        self.assertEqual(row, (None, None))


if __name__ == "__main__":
    unittest.main()
