#!/usr/bin/env python3
"""
Tests for the shared module envelope (`phiweaver.common`).

Focused on `git_commit`'s per-process cache, which exists for a measured reason: the call
shells out to git, costs ~330 ms on the `z:` 9p mount, and every rendered entry queue asks
for it once. Uncached it was the single largest cost in the suite (~9.5 s of ~22 s across the
modules that render provenance stamps). The cache is therefore a performance contract, not an
incidental detail — these tests fail if the decorator is removed.
"""

import unittest
from unittest import mock

from phiweaver import common
from phiweaver.common import git_commit, provenance_line, utc_now


class GitCommitCacheTests(unittest.TestCase):
    def setUp(self):
        # The cache is process-wide, so every test here starts from a known state and
        # leaves one behind — otherwise a warm entry from another module's import would
        # make the call counts meaningless.
        git_commit.cache_clear()
        self.addCleanup(git_commit.cache_clear)

    def test_shells_out_only_once_across_many_calls(self):
        fake = mock.Mock(returncode=0, stdout="abc1234\n")
        with mock.patch.object(common.subprocess, "run", return_value=fake) as run:
            results = [git_commit() for _ in range(20)]
        self.assertEqual(results, ["abc1234"] * 20)
        self.assertEqual(run.call_count, 1, "git_commit must be cached per process")

    def test_asks_git_for_the_packages_own_repo_not_the_cwd(self):
        fake = mock.Mock(returncode=0, stdout="abc1234\n")
        with mock.patch.object(common.subprocess, "run", return_value=fake) as run:
            git_commit()
        argv = run.call_args[0][0]
        self.assertEqual(argv[:2], ["git", "-C"])
        self.assertIn("rev-parse", argv)
        self.assertIn("--short", argv)

    def test_an_unavailable_git_is_cached_too_so_a_timeout_is_paid_once(self):
        with mock.patch.object(common.subprocess, "run",
                               side_effect=OSError("no git")) as run:
            self.assertIsNone(git_commit())
            self.assertIsNone(git_commit())
        self.assertEqual(run.call_count, 1)

    def test_nonzero_exit_and_empty_output_both_give_none(self):
        for fake in (mock.Mock(returncode=128, stdout="fatal: not a repo\n"),
                     mock.Mock(returncode=0, stdout="   \n")):
            git_commit.cache_clear()
            with mock.patch.object(common.subprocess, "run", return_value=fake):
                self.assertIsNone(git_commit())

    def test_cache_clear_lets_a_long_lived_process_re_stamp(self):
        first = mock.Mock(returncode=0, stdout="aaaaaaa\n")
        second = mock.Mock(returncode=0, stdout="bbbbbbb\n")
        with mock.patch.object(common.subprocess, "run", return_value=first):
            self.assertEqual(git_commit(), "aaaaaaa")
        git_commit.cache_clear()
        with mock.patch.object(common.subprocess, "run", return_value=second):
            self.assertEqual(git_commit(), "bbbbbbb")


class ProvenanceLineTests(unittest.TestCase):
    def setUp(self):
        git_commit.cache_clear()
        self.addCleanup(git_commit.cache_clear)

    def test_includes_model_commit_and_date_when_all_are_known(self):
        fake = mock.Mock(returncode=0, stdout="abc1234\n")
        with mock.patch.object(common.subprocess, "run", return_value=fake):
            line = provenance_line("Fable 5", "2026-07-25")
        self.assertEqual(line, "phiweaver · Fable 5 · commit abc1234 · date 2026-07-25")

    def test_omits_missing_pieces_rather_than_inventing_them(self):
        with mock.patch.object(common.subprocess, "run", side_effect=OSError("no git")):
            line = provenance_line(None, None)
        self.assertNotIn("commit", line)
        self.assertNotIn("None", line)
        self.assertTrue(line.startswith("phiweaver · date "))
        # A missing draft date falls back to today's render date, never a blank.
        self.assertIn(utc_now()[:10], line)


if __name__ == "__main__":
    unittest.main()
