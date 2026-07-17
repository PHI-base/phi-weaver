#!/usr/bin/env python3
"""Network-free tests for gap_log.py (ledger path injected; stdlib only)."""

import json
import tempfile
import unittest
from pathlib import Path

from phiweaver.lookup import gap_log as gl


class RecordTests(unittest.TestCase):
    def _tmp(self, d):
        return Path(d) / "gaps.jsonl"

    def test_record_appends_one_json_line_with_provenance(self):
        with tempfile.TemporaryDirectory() as d:
            p = self._tmp(d)
            gl.record("PHIPO", "absent DON", pmid="42089373",
                      context="Table S4: no detectable DON", path=p)
            lines = p.read_text(encoding="utf-8").strip().splitlines()
            self.assertEqual(len(lines), 1)
            row = json.loads(lines[0])
            self.assertEqual(row["ontology"], "PHIPO")
            self.assertEqual(row["phrase"], "absent DON")
            self.assertEqual(row["outcome"], "gap")
            self.assertEqual(row["pmid"], "42089373")
            self.assertTrue(row["recorded_at"], "every event carries a UTC stamp")

    def test_record_creates_the_ledger_and_appends_rather_than_overwrites(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "nested" / "gaps.jsonl"
            gl.record("PECO", "24 h dark incubation", pmid="1", path=p)
            gl.record("PECO", "wounded leaf assay", pmid="2", path=p)
            self.assertEqual(len(gl.load(p)), 2)

    def test_ontology_is_normalised_and_validated(self):
        with tempfile.TemporaryDirectory() as d:
            p = self._tmp(d)
            self.assertEqual(gl.record("phipo", "x", path=p).ontology, "PHIPO")
            # A typo'd ontology would silently split one gap's ranking across two buckets.
            with self.assertRaises(gl.GapLogError):
                gl.record("PHIPPO", "x", path=p)

    def test_synonym_without_its_term_is_rejected(self):
        # Indistinguishable from a gap on read-back, so it would inflate the new-term list.
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(gl.GapLogError):
                gl.record("PHIPO", "no DON produced", outcome="synonym",
                          path=self._tmp(d))

    def test_gap_carrying_a_matched_term_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(gl.GapLogError):
                gl.record("PHIPO", "x", outcome="gap", matched_term="PHIPO:0001445",
                          path=self._tmp(d))

    def test_empty_phrase_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(gl.GapLogError):
                gl.record("PHIPO", "   ", path=self._tmp(d))


class LoadTests(unittest.TestCase):
    def test_missing_ledger_is_empty_not_an_error(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(gl.load(Path(d) / "nothing-here.jsonl"), [])

    def test_blank_lines_are_skipped(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "gaps.jsonl"
            gl.record("PHIPO", "a", path=p)
            with p.open("a", encoding="utf-8") as fh:
                fh.write("\n\n")
            self.assertEqual(len(gl.load(p)), 1)


class RankGapsTests(unittest.TestCase):
    def _events(self, *specs):
        return [gl.GapEvent(**s) for s in specs]

    def test_ranked_by_distinct_papers_not_raw_event_count(self):
        events = self._events(
            {"ontology": "PHIPO", "phrase": "once-wanted", "outcome": "gap", "pmid": "1"},
            {"ontology": "PHIPO", "phrase": "widely-wanted", "outcome": "gap", "pmid": "1"},
            {"ontology": "PHIPO", "phrase": "widely-wanted", "outcome": "gap", "pmid": "2"},
        )
        ranked = gl.rank_gaps(events)
        self.assertEqual(ranked[0].phrase, "widely-wanted")
        self.assertEqual(ranked[0].papers, ["1", "2"])

    def test_one_paper_hitting_a_gap_twice_counts_as_one_paper(self):
        # Otherwise a single chatty draft outranks a gap several papers really need.
        events = self._events(
            {"ontology": "PHIPO", "phrase": "same gap", "outcome": "gap", "pmid": "1"},
            {"ontology": "PHIPO", "phrase": "same gap", "outcome": "gap", "pmid": "1"},
        )
        ranked = gl.rank_gaps(events)
        self.assertEqual(len(ranked), 1)
        self.assertEqual(ranked[0].papers, ["1"])
        self.assertEqual(ranked[0].seen, 2)

    def test_wording_variants_group_into_one_gap_and_are_retained(self):
        events = self._events(
            {"ontology": "PHIPO", "phrase": "Absent DON", "outcome": "gap", "pmid": "1"},
            {"ontology": "PHIPO", "phrase": "absent  don", "outcome": "gap", "pmid": "2"},
        )
        ranked = gl.rank_gaps(events)
        self.assertEqual(len(ranked), 1, "case/whitespace must not split one gap in two")
        self.assertEqual(ranked[0].papers, ["1", "2"])
        self.assertEqual(len(ranked[0].variants), 2, "the exact wordings are the evidence")

    def test_same_phrase_in_two_ontologies_stays_separate(self):
        events = self._events(
            {"ontology": "PHIPO", "phrase": "wounding", "outcome": "gap", "pmid": "1"},
            {"ontology": "PECO", "phrase": "wounding", "outcome": "gap", "pmid": "1"},
        )
        self.assertEqual(len(gl.rank_gaps(events)), 2)

    def test_synonym_events_are_excluded_from_the_gap_ranking(self):
        events = self._events(
            {"ontology": "PHIPO", "phrase": "no DON produced", "outcome": "synonym",
             "matched_term": "PHIPO:0001445", "pmid": "1"},
        )
        self.assertEqual(gl.rank_gaps(events), [])

    def test_ontology_filter(self):
        events = self._events(
            {"ontology": "PHIPO", "phrase": "a", "outcome": "gap", "pmid": "1"},
            {"ontology": "PECO", "phrase": "b", "outcome": "gap", "pmid": "1"},
        )
        ranked = gl.rank_gaps(events, ontology="peco")
        self.assertEqual([r.phrase for r in ranked], ["b"])

    def test_filing_is_appended_not_edited_and_deranks_the_gap(self):
        # Append-only: marking a gap filed means recording it again with the URL.
        events = self._events(
            {"ontology": "PHIPO", "phrase": "filed one", "outcome": "gap", "pmid": "1"},
            {"ontology": "PHIPO", "phrase": "filed one", "outcome": "gap", "pmid": "2"},
            {"ontology": "PHIPO", "phrase": "filed one", "outcome": "gap",
             "filed": "https://github.com/PHI-base/phipo/issues/452"},
            {"ontology": "PHIPO", "phrase": "still open", "outcome": "gap", "pmid": "3"},
        )
        ranked = gl.rank_gaps(events)
        # Two papers beats one, but a filed gap is the ontology team's move — not ours.
        self.assertEqual(ranked[0].phrase, "still open")
        self.assertEqual(ranked[1].filed, "https://github.com/PHI-base/phipo/issues/452")

    def test_report_flags_a_filed_gap_rather_than_inviting_a_re_file(self):
        ranked = gl.rank_gaps(self._events(
            {"ontology": "PHIPO", "phrase": "x", "outcome": "gap", "pmid": "1",
             "filed": "https://example.org/issues/452"}))
        out = gl.format_human(ranked, [])
        self.assertIn("already filed", out)
        self.assertIn("https://example.org/issues/452", out)

    def test_contexts_are_deduped(self):
        events = self._events(
            {"ontology": "PHIPO", "phrase": "a", "outcome": "gap", "pmid": "1",
             "context": "Table S4"},
            {"ontology": "PHIPO", "phrase": "a", "outcome": "gap", "pmid": "2",
             "context": "Table S4"},
        )
        self.assertEqual(gl.rank_gaps(events)[0].contexts, ["Table S4"])


class RankSynonymsTests(unittest.TestCase):
    def test_grouped_by_term_and_ranked_by_missed_wordings(self):
        events = [
            gl.GapEvent("PHIPO", "no DON produced", "synonym", pmid="1",
                        matched_term="PHIPO:0001445", matched_via="decreased DON level"),
            gl.GapEvent("PHIPO", "DON abolished", "synonym", pmid="2",
                        matched_term="PHIPO:0001445", matched_via="decreased DON level"),
            gl.GapEvent("PHIPO", "poor growth", "synonym", pmid="1",
                        matched_term="PHIPO:0000001", matched_via="decreased growth"),
        ]
        ranked = gl.rank_synonyms(events)
        self.assertEqual(ranked[0].matched_term, "PHIPO:0001445")
        self.assertEqual(len(ranked[0].missed_phrases), 2)
        self.assertEqual(ranked[0].papers, ["1", "2"])

    def test_gap_events_are_excluded(self):
        events = [gl.GapEvent("PHIPO", "a", "gap", pmid="1")]
        self.assertEqual(gl.rank_synonyms(events), [])


class CLITests(unittest.TestCase):
    def test_record_then_report_json_round_trip(self):
        with tempfile.TemporaryDirectory() as d:
            p = str(Path(d) / "gaps.jsonl")
            self.assertEqual(
                gl.main(["--log", p, "record", "PECO", "24 h dark", "--pmid", "1"]), 0)
            self.assertEqual(gl.main(["--log", p, "report", "--json"]), 0)

    def test_report_on_an_empty_ledger_succeeds(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(
                gl.main(["--log", str(Path(d) / "none.jsonl"), "report"]), 0)


class FormatTests(unittest.TestCase):
    def test_human_report_names_the_papers_and_both_gap_kinds(self):
        gaps = gl.rank_gaps([gl.GapEvent("PHIPO", "absent DON", "gap", pmid="42089373",
                                         context="Table S4")])
        syns = gl.rank_synonyms([gl.GapEvent("PHIPO", "no DON", "synonym", pmid="1",
                                             matched_term="PHIPO:0001445")])
        out = gl.format_human(gaps, syns)
        self.assertIn("PMID:42089373", out)
        self.assertIn("Table S4", out)
        self.assertIn("PHIPO:0001445", out)
        self.assertIn("1 term gap(s), 1 wording gap(s)", out)


if __name__ == "__main__":
    unittest.main()
