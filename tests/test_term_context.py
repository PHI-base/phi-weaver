#!/usr/bin/env python3
"""Network-free tests for term_context.py — the wrong-context guard (stdlib only).

Labels below are real PHIPO labels, taken from live searches while building the rule.
"""

import unittest
from dataclasses import dataclass
from typing import Optional

from phiweaver.lookup import term_context as tc


@dataclass
class FakeCandidate:
    """Structurally what map_phenotype.Candidate gives us: an id and a label."""
    obo_id: str
    label: Optional[str]


class ClassifyTests(unittest.TestCase):
    def test_within_host_labels_are_in_host(self):
        for label in ("pathogen deoxynivalenol within host absent",
                      "decreased level of pathogen deoxynivalenol within host",
                      "presence of pathogen growth within host"):
            self.assertEqual(tc.classify_term(label), tc.IN_HOST, label)

    def test_host_surface_and_host_defense_labels_are_in_host(self):
        for label in ("presence of pathogen growth on host surface",
                      "host defense-induced reactive oxygen species absent",
                      "absence of pathogen-associated host lesions"):
            self.assertEqual(tc.classify_term(label), tc.IN_HOST, label)

    def test_free_living_branch_labels_are_unspecified(self):
        # The other half of the DON split — no host marker, so no host commitment.
        for label in ("decreased level of deoxynivalenol",
                      "abnormal deoxynivalenol biosynthesis",
                      "decreased hyphal growth",
                      "asexual spores absent"):
            self.assertEqual(tc.classify_term(label), tc.UNSPECIFIED, label)

    def test_nothing_is_ever_classified_free_living(self):
        # An unmarked label is context-neutral, not proof the term is host-free.
        for label in ("decreased hyphal growth", "", None):
            self.assertIn(tc.classify_term(label), (tc.IN_HOST, tc.UNSPECIFIED))

    def test_classification_is_case_insensitive(self):
        self.assertEqual(tc.classify_term("Pathogen DON Within Host absent"), tc.IN_HOST)

    def test_host_inside_a_longer_word_does_not_count(self):
        # Word-boundary, so a term about e.g. a "hostile" condition isn't miscalled in-host.
        self.assertEqual(tc.classify_term("growth in hostile medium"), tc.UNSPECIFIED)


class MismatchTests(unittest.TestCase):
    def test_the_452_case_in_host_term_for_a_free_living_assay(self):
        self.assertTrue(tc.is_mismatched("pathogen deoxynivalenol within host absent",
                                         "free-living"))

    def test_neutral_term_is_fine_for_a_free_living_assay(self):
        self.assertFalse(tc.is_mismatched("decreased level of deoxynivalenol", "free-living"))

    def test_in_host_assay_may_use_an_in_host_term(self):
        self.assertFalse(tc.is_mismatched("pathogen deoxynivalenol within host absent",
                                          "in-host"))

    def test_in_host_assay_may_also_use_a_neutral_term(self):
        # The reverse direction is deliberately not flagged — a neutral term is legitimate
        # in planta, and flagging it would be noise a curator learns to ignore.
        self.assertFalse(tc.is_mismatched("decreased hyphal growth", "in-host"))

    def test_unknown_assay_context_is_rejected_rather_than_guessed(self):
        with self.assertRaises(ValueError):
            tc.is_mismatched("decreased hyphal growth", "in planta")


class ReviewTests(unittest.TestCase):
    DON_IN_HOST = FakeCandidate("PHIPO:0000234",
                                "pathogen deoxynivalenol within host absent")
    DON_FREE = FakeCandidate("PHIPO:0001445", "decreased level of deoxynivalenol")

    def test_splits_usable_from_mismatched(self):
        r = tc.review([self.DON_IN_HOST, self.DON_FREE], "free-living")
        self.assertEqual([c.obo_id for c in r.usable], ["PHIPO:0001445"])
        self.assertEqual([c.obo_id for c in r.mismatched], ["PHIPO:0000234"])

    def test_all_mismatched_when_every_candidate_is_context_wrong(self):
        r = tc.review([self.DON_IN_HOST], "free-living")
        self.assertTrue(r.all_mismatched)

    def test_an_irrelevant_host_free_candidate_masks_a_real_gap(self):
        # The live #452 result: searching "absent DON" for a free-living assay returns the
        # in-host DON term plus 'asexual spore lysis absent' — lexical noise off "absent",
        # nothing to do with DON, but host-free, so it reads as usable. This is why
        # all_mismatched must never drive gap recording: it is False here, on the very case
        # the module exists for.
        noise = FakeCandidate("PHIPO:0000939", "asexual spore lysis absent")
        r = tc.review([self.DON_IN_HOST, noise], "free-living")
        self.assertFalse(r.all_mismatched)
        self.assertEqual([c.obo_id for c in r.usable], ["PHIPO:0000939"])

    def test_all_mismatched_is_false_when_something_is_usable(self):
        r = tc.review([self.DON_IN_HOST, self.DON_FREE], "free-living")
        self.assertFalse(r.all_mismatched)

    def test_all_mismatched_is_false_with_no_candidates(self):
        # An empty result is map_phenotype's no_match, not a context problem.
        self.assertFalse(tc.review([], "free-living").all_mismatched)

    def test_in_host_assay_flags_nothing(self):
        r = tc.review([self.DON_IN_HOST, self.DON_FREE], "in-host")
        self.assertEqual(r.mismatched, [])
        self.assertFalse(r.all_mismatched)


class WarningTests(unittest.TestCase):
    def test_no_warning_when_nothing_mismatched(self):
        r = tc.review([FakeCandidate("PHIPO:0001445", "decreased level of deoxynivalenol")],
                      "free-living")
        self.assertIsNone(tc.format_warning("decreased DON", r))

    def test_all_mismatched_warning_names_the_gap_and_the_next_step(self):
        r = tc.review([FakeCandidate("PHIPO:0000234",
                                     "pathogen deoxynivalenol within host absent")],
                      "free-living")
        w = tc.format_warning("absent DON", r)
        self.assertIn("nothing here is usable", w)
        self.assertIn("PHIPO:0000234", w)
        self.assertIn("gap_log record", w, "the warning must say what to do next")

    def test_partial_mismatch_sends_the_curator_at_the_survivors(self):
        # The #452 shape: the noise candidate survives, so the warning must not imply it fits.
        r = tc.review([FakeCandidate("PHIPO:0000234", "pathogen DON within host absent"),
                       FakeCandidate("PHIPO:0000939", "asexual spore lysis absent")],
                      "free-living")
        w = tc.format_warning("absent DON", r)
        self.assertIn("wrong for a free-living assay", w)
        self.assertIn("PHIPO:0000939", w, "the survivor must be named for checking")
        self.assertIn("share a word without sharing a meaning", w)
        self.assertIn("gap_log record", w)


class AnnotateTests(unittest.TestCase):
    def test_each_candidate_carries_its_verdict(self):
        out = tc.annotate_dicts(
            [FakeCandidate("PHIPO:0000234", "pathogen DON within host absent"),
             FakeCandidate("PHIPO:0001445", "decreased level of deoxynivalenol")],
            "free-living")
        self.assertEqual(out[0]["term_context"], tc.IN_HOST)
        self.assertTrue(out[0]["context_mismatch"])
        self.assertFalse(out[1]["context_mismatch"])


if __name__ == "__main__":
    unittest.main()
