#!/usr/bin/env python3
"""Network-free tests for the token-cost section of the Article-Registry dashboard.

Exercises the pure renderer only (no DB): build the generator via __new__ so __init__
(which constructs a PHICantoSQLite) never runs, then call _generate_dashboard_content.
"""

import unittest

from phiweaver.tracking.generate_article_registry import ArticleRegistryGenerator

_STATS = {"status": {}, "curators": [],
          "productivity": {"sessions": 0, "proteins": 0, "interactions": 0}}

_TOKEN_COSTS = [
    {"pmid": "38234567", "first_author_year": "Smith 2024", "model": "claude-opus-4-8",
     "total_tokens": 664150, "cost_usd": 0.45, "computed_at": "2026-07-11 10:00:00"},
    {"pmid": "38234567", "first_author_year": "Smith 2024", "model": "claude-haiku-4-5",
     "total_tokens": 664150, "cost_usd": 0.09, "computed_at": "2026-07-11 09:00:00"},
]


def _render(token_costs):
    gen = ArticleRegistryGenerator.__new__(ArticleRegistryGenerator)  # skip DB __init__
    return gen._generate_dashboard_content([], _STATS, [], token_costs)


class RegistryTokenSectionTest(unittest.TestCase):
    def test_section_absent_without_measurements(self):
        self.assertNotIn("Token Costs", _render([]))

    def test_section_renders_rows_and_dollars(self):
        out = _render(_TOKEN_COSTS)
        self.assertIn("💰 Token Costs", out)
        self.assertIn("$0.45", out)
        self.assertIn("$0.09", out)
        self.assertIn("claude-haiku-4-5", out)
        # PMID becomes a PubMed link
        self.assertIn("https://pubmed.ncbi.nlm.nih.gov/38234567", out)

    def test_per_model_rollup_line(self):
        out = _render(_TOKEN_COSTS)
        self.assertIn("By model", out)
        # each model contributes its own summed estimate
        self.assertIn("claude-opus-4-8 — 1 run(s), ~$0.45", out)
        self.assertIn("claude-haiku-4-5 — 1 run(s), ~$0.09", out)

    def test_truncates_to_15_rows_with_note(self):
        many = [dict(_TOKEN_COSTS[0], pmid=str(i)) for i in range(20)]
        out = _render(many)
        self.assertIn("Showing 15 of 20 measurements", out)


if __name__ == "__main__":
    unittest.main()
