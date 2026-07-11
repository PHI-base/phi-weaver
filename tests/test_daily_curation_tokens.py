#!/usr/bin/env python3
"""Network-free tests for the `tokens` view of daily_curation (pure renderer only)."""

import unittest

from phiweaver.tracking.daily_curation import format_token_costs

_HIST = [
    {"pmid": "38234567", "first_author_year": "Smith 2024", "model": "claude-opus-4-8",
     "total_tokens": 664150, "cost_usd": 0.45, "computed_at": "2026-07-11 10:00:00"},
    {"pmid": "38234567", "first_author_year": "Smith 2024", "model": "claude-haiku-4-5",
     "total_tokens": 664150, "cost_usd": 0.09, "computed_at": "2026-07-11 09:00:00"},
]


class DailyTokenViewTest(unittest.TestCase):
    def test_empty_shows_record_hint(self):
        out = format_token_costs([])
        self.assertIn("No token measurements recorded yet", out)
        self.assertIn("--record", out)

    def test_rows_and_per_model_rollup(self):
        out = format_token_costs(_HIST)
        self.assertIn("💰 Token Costs", out)
        self.assertIn("claude-opus-4-8: 1 run(s), ~$0.45", out)
        self.assertIn("claude-haiku-4-5: 1 run(s), ~$0.09", out)
        self.assertIn("PMID 38234567 (Smith 2024)", out)
        self.assertIn("$0.09", out)

    def test_pmid_scope_in_header(self):
        self.assertIn("for PMID 38234567", format_token_costs(_HIST, pmid="38234567"))

    def test_truncates_to_15(self):
        many = [dict(_HIST[0], pmid=str(i)) for i in range(20)]
        self.assertIn("showing 15 of 20 measurements", format_token_costs(many))


if __name__ == "__main__":
    unittest.main()
