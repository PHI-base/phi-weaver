#!/usr/bin/env python3
"""Tests for the shared phrase → term scorer used by map_phenotype and map_condition.

The property under test throughout is not "good ranking" — it is that **`no_match` stays
reachable**. A scorer that always matches something silently destroys gap detection, which is
what the ontology-term-request workflow and `--log-gaps` are built on.
"""

import unittest

from phiweaver.lookup import text_score as ts


# "host" is in *every* document (so it carries zero information), "deoxynivalenol" in one —
# the shape of a real ontology, where generic vocabulary is everywhere and the informative
# words are rare.
DOCS = [
    ("host response to pathogen",),
    ("host colonisation by pathogen",),
    ("host tissue phenotype",),
    ("decreased level of deoxynivalenol in host", "decreased level of vomitoxin in host"),
]
IDF = ts.build_idf(DOCS)


class TokensTests(unittest.TestCase):
    def test_lowercases_and_splits_on_punctuation(self):
        self.assertEqual(ts.tokens("Rich-Medium, 25C"), {"rich", "medium", "25c"})

    def test_empty_is_empty(self):
        self.assertEqual(ts.tokens(""), set())
        self.assertEqual(ts.tokens(None), set())


class IdfTests(unittest.TestCase):
    def test_rare_token_beats_common_token(self):
        self.assertGreater(IDF["deoxynivalenol"], IDF["host"])

    def test_token_in_every_document_carries_no_information(self):
        self.assertEqual(IDF["host"], 0.0)

    def test_synonyms_count_once_per_term_not_per_text(self):
        # "decreased" appears in both texts of one term; it must not count twice.
        self.assertEqual(IDF["decreased"], IDF["level"])

    def test_empty_corpus_is_empty(self):
        self.assertEqual(ts.build_idf([]), {})

    def test_unseen_token_is_maximally_informative(self):
        self.assertEqual(ts.max_idf(IDF), max(IDF.values()))


class ScoreTests(unittest.TestCase):
    def test_exact_scores_100(self):
        self.assertEqual(ts.score("host tissue phenotype", ("host tissue phenotype",), IDF), 100.0)

    def test_exact_synonym_scores_100(self):
        self.assertEqual(ts.score("decreased level of vomitoxin in host",
                                  ("decreased level of deoxynivalenol in host",
                                   "decreased level of vomitoxin in host"), IDF), 100.0)

    def test_zero_information_token_alone_scores_zero(self):
        """'host' is in every document, so sharing only it means sharing nothing."""
        self.assertEqual(ts.score("host", ("host response to pathogen",), IDF), 0.0)

    def test_phrase_inside_a_longer_label_is_a_narrowing(self):
        s = ts.score("deoxynivalenol", ("decreased level of deoxynivalenol",), IDF)
        self.assertGreaterEqual(s, 60.0)

    def test_label_inside_phrase_is_not_a_match(self):
        """The removed tier. A one-word generic label must not match any phrase containing
        that word — this is precisely what made `no_match` unreachable."""
        idf = ts.build_idf([("phenotype",), ("virulence phenotype",), ("cell phenotype",)])
        s = ts.score("zzzz nonexistent phenotype qqq", ("phenotype",), idf)
        self.assertLess(s, 20.0)

    def test_no_shared_tokens_scores_zero(self):
        self.assertEqual(ts.score("xylophone concerto", ("host tissue phenotype",), IDF), 0.0)

    def test_empty_phrase_scores_zero(self):
        self.assertEqual(ts.score("", ("host tissue phenotype",), IDF), 0.0)

    def test_unseen_words_dilute_the_score(self):
        """A phrase mostly made of words the ontology has never heard should not score well
        on the strength of one overlapping word."""
        near = ts.score("decreased deoxynivalenol", ("decreased level of deoxynivalenol",), IDF)
        far = ts.score("decreased deoxynivalenol in xylophone concerto orchestral tuning",
                       ("decreased level of deoxynivalenol",), IDF)
        self.assertGreater(near, far)


class IsExactTests(unittest.TestCase):
    def test_matches_any_text_case_insensitively(self):
        self.assertTrue(ts.is_exact("Rich Medium", ("rich medium",)))

    def test_empty_phrase_is_never_exact(self):
        self.assertFalse(ts.is_exact("", ("rich medium",)))


if __name__ == "__main__":
    unittest.main()
