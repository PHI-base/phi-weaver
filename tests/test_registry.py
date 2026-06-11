#!/usr/bin/env python3
"""Tests for the skill/module registry (phiweaver.registry). Network-free, temp dirs."""

import tempfile
import unittest
from pathlib import Path

from phiweaver import registry, repo_root


SAMPLE_FM = """---
name: demo
description: A demo skill, with a pipe | in it
backing_script: phiweaver/lookup/query_uniprot.py
tests: tests/test_query_uniprot.py
inputs:
  - a gene
  - an organism
outputs:
  - an accession
---

# body ignored
"""


def _write_skill(skills_dir, name, frontmatter):
    d = skills_dir / name
    d.mkdir(parents=True)
    (d / "SKILL.md").write_text(frontmatter, encoding="utf-8")


class ParseTests(unittest.TestCase):
    def test_scalars_lists_and_null(self):
        meta = registry.parse_frontmatter(SAMPLE_FM)
        self.assertEqual(meta["name"], "demo")
        self.assertEqual(meta["backing_script"], "phiweaver/lookup/query_uniprot.py")
        self.assertEqual(meta["inputs"], ["a gene", "an organism"])
        self.assertEqual(meta["outputs"], ["an accession"])
        self.assertIn("pipe | in it", meta["description"])

    def test_null_becomes_none(self):
        meta = registry.parse_frontmatter(
            "---\nname: x\nbacking_script: null\n---\n")
        self.assertIsNone(meta["backing_script"])

    def test_no_frontmatter(self):
        self.assertEqual(registry.parse_frontmatter("# just a heading\n"), {})


class ValidateAndRenderTests(unittest.TestCase):
    def test_missing_backing_file_is_flagged(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_skill(root / "skills", "demo", SAMPLE_FM.replace(
                "phiweaver/lookup/query_uniprot.py", "phiweaver/lookup/nope.py"))
            skills = registry.discover_skills(root / "skills")
            problems = registry.validate_skills(skills, root)
            self.assertTrue(any("backing_script not found" in p for p in problems))

    def test_missing_required_field_is_flagged(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_skill(root / "skills", "demo",
                         "---\nname: demo\ndescription: d\n---\n")
            skills = registry.discover_skills(root / "skills")
            problems = registry.validate_skills(skills, root)
            self.assertTrue(any("missing frontmatter field 'inputs'" in p for p in problems))

    def test_render_lists_skill_and_reasoning_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_skill(root / "skills", "demo", SAMPLE_FM)
            _write_skill(root / "skills", "triage",
                         "---\nname: triage\ndescription: d\nbacking_script: null\n"
                         "tests: null\ninputs:\n  - a paper\noutputs:\n  - a verdict\n---\n")
            skills = registry.discover_skills(root / "skills")
            md = registry.render_registry(skills)
            self.assertIn("`demo`", md)
            self.assertIn("_(reasoning-only)_", md)

    def test_check_detects_stale_then_current(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "AGENTS.md").write_text("# marker\n", encoding="utf-8")
            # backing/tests files must exist for validation to pass
            (root / "phiweaver" / "lookup").mkdir(parents=True)
            (root / "phiweaver" / "lookup" / "query_uniprot.py").write_text("", "utf-8")
            (root / "tests").mkdir()
            (root / "tests" / "test_query_uniprot.py").write_text("", "utf-8")
            _write_skill(root / "skills", "demo", SAMPLE_FM)

            self.assertTrue(any("out of date" in p for p in registry.check(root)))
            skills = registry.discover_skills(root / "skills")
            (root / "skills" / "REGISTRY.md").write_text(
                registry.render_registry(skills), encoding="utf-8")
            self.assertEqual(registry.check(root), [])


class RealRepoTests(unittest.TestCase):
    def test_committed_registry_is_current_and_valid(self):
        # Guards the real repo: every skill's wiring resolves and REGISTRY.md is current.
        self.assertEqual(registry.check(repo_root()), [])


if __name__ == "__main__":
    unittest.main()
