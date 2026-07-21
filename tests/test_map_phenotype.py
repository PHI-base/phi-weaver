#!/usr/bin/env python3
"""Network-free tests for map_phenotype.py.

map_phenotype went **offline** on 2026-07-17 (was EBI OLS), so these no longer mock HTTP —
they inject a small term list, or read the bundled release. Tests that only existed to cover
the HTTP layer (cache hits, 500s, "empty query makes no HTTP call") are gone with it.
"""

import tempfile
import unittest
from pathlib import Path

from phiweaver.lookup import map_phenotype as m


def term(obo_id, name, synonyms=(), obsolete=False):
    return m.Term(obo_id, name, tuple(synonyms), obsolete)


# A miniature ontology. Deliberately shares the generic vocabulary real PHIPO leans on
# ("host", "pathogen", "level of") so the IDF scorer is exercised, not bypassed.
TERMS = [
    term("PHIPO:0000015", "reduced virulence", ("decreased virulence",)),
    term("PHIPO:0001445", "decreased level of deoxynivalenol",
         ("decreased level of vomitoxin",)),
    term("PHIPO:0001447", "increased level of deoxynivalenol"),
    term("PHIPO:0000234", "pathogen deoxynivalenol within host absent"),
    term("PHIPO:0001033", "pyocyanin absent from cell"),
    term("PHIPO:0000503", "obsolete deoxynivalenol absent from cell", (), True),
    term("PHIPO:0000505", "phenotype"),
    term("PHIPO:0000011", "virulence phenotype"),
]


def mapper(terms=None):
    mp = m.PhenotypeMapper(terms=list(TERMS if terms is None else terms))
    return mp


class MapTests(unittest.TestCase):
    def test_match_returns_real_phipo_id(self):
        r = mapper().map("reduced virulence")
        self.assertEqual(r.status, "matched")
        self.assertEqual(r.candidates[0].obo_id, "PHIPO:0000015")
        self.assertTrue(r.ok)

    def test_no_match_is_explicit_not_guessed(self):
        r = mapper().map("qqqq wwww eeee")
        self.assertEqual(r.status, "no_match")
        self.assertEqual(r.candidates, [])
        self.assertTrue(r.ok)          # an honest empty result is success, not an error

    def test_exact_match_ranked_first(self):
        r = mapper().map("reduced virulence", rows=5)
        self.assertTrue(r.candidates[0].exact)
        self.assertEqual(r.candidates[0].obo_id, "PHIPO:0000015")

    def test_exact_synonym_counts_as_exact(self):
        r = mapper().map("decreased level of vomitoxin")
        self.assertTrue(r.candidates[0].exact)
        self.assertEqual(r.candidates[0].obo_id, "PHIPO:0001445")

    def test_rows_limit_respected(self):
        r = mapper().map("deoxynivalenol", rows=2)
        self.assertLessEqual(len(r.candidates), 2)

    def test_obsolete_excluded_by_default(self):
        """A curator cannot annotate to an obsolete term, so never suggest one."""
        r = mapper().map("deoxynivalenol absent from cell", rows=9)
        self.assertNotIn("PHIPO:0000503", [c.obo_id for c in r.candidates])

    def test_include_obsolete_surfaces_it_flagged(self):
        """The #452 lesson: OLS hides deprecated terms, so a gap that already existed looks
        virgin. Offline they are visible — but only on request, and marked."""
        r = mapper().map("deoxynivalenol absent from cell", rows=9, include_obsolete=True)
        hit = [c for c in r.candidates if c.obo_id == "PHIPO:0000503"]
        self.assertTrue(hit, "obsolete term should surface with include_obsolete")
        self.assertTrue(hit[0].obsolete)

    def test_generic_token_alone_does_not_match(self):
        """Regression: the borrowed map_condition scorer let the one-word label 'phenotype'
        match any query containing that word, so `no_match` was unreachable — and `no_match`
        is what gap detection and --log-gaps key on."""
        r = mapper().map("zzzz nonexistent phenotype qqq")
        self.assertEqual(r.status, "no_match")

    def test_empty_query_is_no_match(self):
        r = mapper().map("")
        self.assertEqual(r.status, "no_match")

    def test_missing_ontology_file_is_an_error_not_a_silent_no_match(self):
        mp = m.PhenotypeMapper(path=Path("/nonexistent/phipo-base.obo"))
        r = mp.map("reduced virulence")
        self.assertEqual(r.status, "error")
        self.assertFalse(r.ok)

    def test_to_dict_is_json_friendly(self):
        import json
        d = mapper().map("reduced virulence").to_dict()
        self.assertTrue(d["ok"])
        json.dumps(d)                  # must not raise


class ScoringTests(unittest.TestCase):
    def test_idf_downweights_common_tokens(self):
        idf = m.build_idf(TERMS)
        # In this fixture "pyocyanin" is in 1 label and "deoxynivalenol" in 4, so the rarer
        # token must carry more information.
        self.assertGreater(idf["pyocyanin"], idf["deoxynivalenol"])

    def test_idf_downweights_common_tokens_in_the_real_ontology(self):
        """Guards the real reason IDF is here: PHIPO's generic vocabulary is very common
        ('host' is in ~25% of labels) and must not carry a match on its own."""
        idf = m.build_idf(m.load_terms())
        self.assertGreater(idf["deoxynivalenol"], idf["host"])
        self.assertGreater(idf["deoxynivalenol"], idf["pathogen"])

    def test_unseen_token_gets_max_idf(self):
        idf = m.build_idf(TERMS)
        self.assertEqual(m._max_idf(idf), max(idf.values()))


class BundledOntologyTests(unittest.TestCase):
    """Against the real bundled release, not a fixture."""

    def test_bundled_release_parses(self):
        terms = m.load_terms()
        self.assertGreater(len(terms), 1000)

    def test_bundled_release_has_a_data_version(self):
        self.assertTrue(m.read_release())

    def test_obsolete_terms_are_present_in_the_file(self):
        """The whole point of going offline: OLS's search cannot see these."""
        terms = m.load_terms()
        self.assertTrue(any(t.obsolete for t in terms))

    def test_known_term_resolves(self):
        r = m.PhenotypeMapper().map("decreased level of deoxynivalenol")
        self.assertEqual(r.candidates[0].obo_id, "PHIPO:0001445")

    def test_only_phipo_ids_are_returned(self):
        for t in m.load_terms():
            self.assertTrue(t.obo_id.startswith("PHIPO:"))


class AnnotationUsageTests(unittest.TestCase):
    """PHI-Canto refuses some terms that exist and are not obsolete (PHIPO subset tags)."""

    def test_usage_classification(self):
        self.assertEqual(m.usage_of(["qc_do_not_annotate"]), m.USAGE_GROUPING)
        self.assertEqual(m.usage_of(["qc_do_not_manually_annotate"]), m.USAGE_GROUPING)
        self.assertEqual(m.usage_of(["qc_extension_only"]), m.USAGE_EXTENSION_ONLY)
        self.assertEqual(m.usage_of(["pathogen_phenotype"]), m.USAGE_PRIMARY)
        self.assertEqual(m.usage_of([]), m.USAGE_PRIMARY)

    def test_subsets_are_parsed_from_the_obo(self):
        by_id = {t.obo_id: t for t in m.load_terms()}
        # "pathogenicity phenotype" is a grouping term; "reduced virulence" extension-only.
        self.assertEqual(by_id["PHIPO:0000006"].usage, m.USAGE_GROUPING)
        self.assertEqual(by_id["PHIPO:0000015"].usage, m.USAGE_EXTENSION_ONLY)

    def test_extension_only_terms_are_returned_but_labelled(self):
        """The most common PHI-base phrase must not become a false gap."""
        r = m.PhenotypeMapper().map("reduced virulence")
        top = r.candidates[0]
        self.assertEqual(top.obo_id, "PHIPO:0000015")
        self.assertTrue(top.exact)
        self.assertEqual(top.usage, m.USAGE_EXTENSION_ONLY)

    def test_grouping_terms_are_withheld_not_dropped(self):
        r = m.PhenotypeMapper().map("pathogenicity phenotype")
        ids = {c.obo_id for c in r.candidates}
        withheld = {c.obo_id for c in r.withheld}
        self.assertNotIn("PHIPO:0000006", ids)       # not offered for annotation
        self.assertIn("PHIPO:0000006", withheld)     # but still reported

    def test_include_grouping_promotes_them(self):
        r = m.PhenotypeMapper().map("pathogenicity phenotype", include_grouping=True)
        self.assertIn("PHIPO:0000006", {c.obo_id for c in r.candidates})
        self.assertEqual(r.withheld, [])

    def test_withheld_terms_are_shown_to_the_curator(self):
        """A parent-only match must read as 'not a gap', not as a bare no_match."""
        r = m.PhenotypeMapper().map("pathogenicity phenotype")
        self.assertIn("NOT a gap", m.format_human([r]))


class ReadPhrasesTests(unittest.TestCase):
    def test_reads_nonempty_noncomment_lines(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "phrases.txt"
            p.write_text("reduced virulence\n\n# a comment\nabnormal growth\n")
            self.assertEqual(m.read_phrases(str(p)),
                             ["reduced virulence", "abnormal growth"])


if __name__ == "__main__":
    unittest.main()
