#!/usr/bin/env python3
"""Tests for `phiweaver.smoke --no-tests` check selection.

Deliberately covers only the *selection* logic, not the checks themselves: running the
checks costs ~17s and running the bundled suite costs ~34s more, and a slow test here
would worsen the exact problem --no-tests exists to fix.
"""

import unittest

from phiweaver import smoke


class CheckSelectionTests(unittest.TestCase):
    def test_default_includes_the_unit_suite(self):
        names = [n for n, _ in smoke.selected_checks()]
        self.assertIn(smoke._UNIT_TEST_CHECK, names)
        self.assertEqual(len(names), len(smoke.CHECKS))

    def test_no_tests_drops_exactly_the_unit_suite(self):
        full = [n for n, _ in smoke.selected_checks()]
        trimmed = [n for n, _ in smoke.selected_checks(no_tests=True)]
        self.assertNotIn(smoke._UNIT_TEST_CHECK, trimmed)
        # Every other check survives, in order — --no-tests is not a "quick mode".
        self.assertEqual(trimmed, [n for n in full if n != smoke._UNIT_TEST_CHECK])

    def test_the_named_check_actually_exists(self):
        # Guards against the constant drifting from the CHECKS entry, which would make
        # --no-tests silently skip nothing and quietly restore the double run.
        self.assertIn(smoke._UNIT_TEST_CHECK, [n for n, _ in smoke.CHECKS])


if __name__ == "__main__":
    unittest.main()
