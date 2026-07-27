#!/usr/bin/env python3
"""Network-free tests for refresh_ontologies.py (fetch injected; stdlib only)."""

import tempfile
import unittest
from pathlib import Path

from phiweaver.lookup import refresh_ontologies as ro

PHIPO_OLD = """format-version: 1.2
data-version: phipo/releases/2026-03-12/phipo-base.owl

[Term]
id: PHIPO:0000001
name: pathogen phenotype

[Term]
id: PHIPO:0000002
name: reduced virulence
"""

PHIPO_NEW = PHIPO_OLD.replace("2026-03-12", "2026-08-01") + """
[Term]
id: PHIPO:0000003
name: loss of pathogenicity
"""

NO_VERSION = """format-version: 1.2
creation_date: 2018-07-09

[Term]
id: PHIDO:0000001
name: head blight
"""


def _dir_with(files):
    """A temp data dir holding `files` ({name: text}); caller keeps the TemporaryDirectory."""
    tmp = tempfile.TemporaryDirectory()
    for name, text in files.items():
        (Path(tmp.name) / name).write_text(text, encoding="utf-8")
    return tmp


def _fetch(payload):
    """A fetch stub returning fixed bytes for any URL."""
    return lambda url: payload.encode("utf-8") if isinstance(payload, str) else payload


class DescribeTests(unittest.TestCase):
    def test_reads_data_version_and_counts_terms(self):
        b = ro.describe(PHIPO_OLD)
        self.assertEqual(b.release, "phipo/releases/2026-03-12/phipo-base.owl")
        self.assertEqual(b.terms, 2)
        self.assertEqual(len(b.digest), 12)

    def test_release_is_none_when_the_ontology_has_no_data_version(self):
        b = ro.describe(NO_VERSION)
        self.assertIsNone(b.release, "PHIDO/PHI-ECO carry no data-version line")
        self.assertEqual(b.terms, 1)

    def test_does_not_mistake_a_term_body_line_for_the_header(self):
        # A `data-version:` appearing after the first [Term] must not be read as the release.
        text = PHIPO_OLD.replace("data-version: phipo/releases/2026-03-12/phipo-base.owl", "")
        text += "data-version: bogus\n"
        self.assertIsNone(ro.describe(text).release)

    def test_digest_distinguishes_files_with_no_data_version(self):
        self.assertNotEqual(ro.describe(NO_VERSION).digest,
                            ro.describe(NO_VERSION + "\n[Term]\nid: X:1\n").digest)


class PlausibilityTests(unittest.TestCase):
    def test_rejects_content_with_no_term_blocks(self):
        reason = ro.implausible(ro.describe("404: Not Found"), ro.describe(PHIPO_OLD))
        self.assertIn("no [Term] blocks", reason or "")

    def test_rejects_a_truncated_download(self):
        big = ro.Bundle(release=None, terms=1327, digest="a" * 12)
        reason = ro.implausible(ro.Bundle(release=None, terms=12, digest="b" * 12), big)
        self.assertIn("truncated", reason or "")

    def test_accepts_growth_and_small_shrinkage(self):
        old = ro.Bundle(release=None, terms=100, digest="a" * 12)
        self.assertIsNone(ro.implausible(ro.Bundle(None, 140, "b" * 12), old))
        self.assertIsNone(ro.implausible(ro.Bundle(None, 90, "b" * 12), old),
                          "terms are obsoleted, not always added")

    def test_a_new_file_only_has_to_be_an_obo(self):
        self.assertIsNone(ro.implausible(ro.describe(NO_VERSION), None))


class RefreshOneTests(unittest.TestCase):
    def setUp(self):
        self.tmp = _dir_with({"phipo-base.obo": PHIPO_OLD})
        self.addCleanup(self.tmp.cleanup)
        self.data = Path(self.tmp.name)
        self.source = ro.Source("phipo-base.obo", "https://example.invalid/phipo-base.obo")

    def _run(self, payload, **kw):
        return ro.refresh_one(self.source, fetch=_fetch(payload), data_dir=self.data, **kw)

    def test_identical_upstream_is_unchanged_and_leaves_the_file_alone(self):
        r = self._run(PHIPO_OLD)
        self.assertEqual(r.status, "unchanged")
        self.assertEqual((self.data / "phipo-base.obo").read_text(encoding="utf-8"), PHIPO_OLD)

    def test_a_new_release_is_written_and_both_releases_reported(self):
        r = self._run(PHIPO_NEW)
        self.assertEqual(r.status, "updated")
        self.assertIn("2026-03-12", r.old.release)
        self.assertIn("2026-08-01", r.new.release)
        self.assertEqual((self.data / "phipo-base.obo").read_text(encoding="utf-8"), PHIPO_NEW)

    def test_dry_run_reports_the_change_without_writing(self):
        r = self._run(PHIPO_NEW, dry_run=True)
        self.assertEqual(r.status, "would-update")
        self.assertEqual((self.data / "phipo-base.obo").read_text(encoding="utf-8"), PHIPO_OLD,
                         "--dry-run must never touch a vendored file")

    def test_implausible_content_is_rejected_and_the_good_bundle_survives(self):
        r = self._run("<html>404</html>")
        self.assertEqual(r.status, "rejected")
        self.assertTrue(r.failed)
        self.assertEqual((self.data / "phipo-base.obo").read_text(encoding="utf-8"), PHIPO_OLD)

    def test_non_utf8_is_rejected_rather_than_raising(self):
        r = ro.refresh_one(self.source, fetch=lambda url: b"\xff\xfe[Term]",
                           data_dir=self.data)
        self.assertEqual(r.status, "rejected")
        self.assertIn("UTF-8", r.message)

    def test_a_transport_failure_is_an_error_not_a_crash(self):
        def boom(url):
            raise OSError("network is unreachable")   # the benchmark sandbox's default-deny

        r = ro.refresh_one(self.source, fetch=boom, data_dir=self.data)
        self.assertEqual(r.status, "error")
        self.assertIn("network is unreachable", r.message)
        self.assertEqual((self.data / "phipo-base.obo").read_text(encoding="utf-8"), PHIPO_OLD)

    def test_an_absent_file_is_vendored_as_new(self):
        r = ro.refresh_one(ro.Source("phido.obo", "https://example.invalid/phido.obo"),
                           fetch=_fetch(NO_VERSION), data_dir=self.data)
        self.assertEqual(r.status, "new")
        self.assertTrue((self.data / "phido.obo").exists())


class ReportTests(unittest.TestCase):
    def test_report_lists_every_outcome_and_the_unsourced_files(self):
        results = [
            ro.Result("phipo-base.obo", "updated",
                      old=ro.describe(PHIPO_OLD), new=ro.describe(PHIPO_NEW)),
            ro.Result("phido.obo", "unchanged", old=ro.describe(NO_VERSION)),
            ro.Result("phi-eco.obo", "error", message="fetch failed: OSError: nope"),
        ]
        out = ro.format_report(results)
        self.assertIn("2026-03-12", out)
        self.assertIn("2026-08-01", out)
        self.assertIn("unchanged", out)
        self.assertIn("fetch failed", out)
        self.assertIn("pomgeneex.obo", out, "no-upstream files are named, not silently absent")

    def test_skipped_files_are_omitted_when_the_caller_asked_for_one_file(self):
        out = ro.format_report([ro.Result("phido.obo", "unchanged", old=ro.describe(NO_VERSION))],
                               include_skipped=False)
        self.assertIn("phido.obo", out)
        self.assertNotIn("pomgeneex.obo", out)

    def test_failed_flags_only_rejected_and_error(self):
        self.assertTrue(ro.Result("x", "rejected").failed)
        self.assertTrue(ro.Result("x", "error").failed)
        for ok in ("unchanged", "updated", "would-update", "new"):
            self.assertFalse(ro.Result("x", ok).failed)


class SourceTableTests(unittest.TestCase):
    def test_every_source_is_a_raw_githubusercontent_url_under_a_known_org(self):
        for s in ro.SOURCES:
            self.assertTrue(s.url.startswith("https://raw.githubusercontent.com/"), s.url)
            self.assertTrue(s.url.endswith(s.filename), "URL must fetch the file it vendors")

    def test_sources_never_point_at_a_working_or_import_bloated_file(self):
        # phipo-edit.owl carries unreleased terms; phipo.obo inlines GO/CHEBI.
        for s in ro.SOURCES:
            self.assertNotIn("edit", s.url)
            self.assertFalse(s.url.endswith("/phipo.obo"), s.url)

    def test_every_bundled_obo_is_either_refreshable_or_explained(self):
        bundled = {p.name for p in ro.DATA_DIR.glob("*.obo")}
        covered = {s.filename for s in ro.SOURCES} | set(ro.UNSOURCED)
        self.assertEqual(bundled - covered, set(),
                         "a new bundled .obo needs a source or an UNSOURCED reason")


if __name__ == "__main__":
    unittest.main()
