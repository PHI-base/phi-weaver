import tempfile
import unittest
from pathlib import Path

from phiweaver import vault_names


def _mk(tmp, rels):
    for rel in rels:
        p = Path(tmp) / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("x", encoding="utf-8")
    return Path(tmp)


class VaultNamesTests(unittest.TestCase):
    def test_flags_duplicate_basename(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _mk(tmp, ["a/INDEX.md", "b/INDEX.md"])
            self.assertIn("INDEX.md", vault_names.duplicate_basenames(root))
            self.assertEqual(len(vault_names.check(root)), 1)

    def test_unique_basenames_are_clean(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _mk(tmp, ["a/Alpha-INDEX.md", "b/Beta-INDEX.md"])
            self.assertEqual(vault_names.check(root), [])

    def test_exempt_basenames_may_repeat(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _mk(tmp, ["a/README.md", "b/README.md",
                             "s1/SKILL.md", "s2/SKILL.md"])
            self.assertEqual(vault_names.check(root), [])

    def test_skips_excluded_dirs(self):
        with tempfile.TemporaryDirectory() as tmp:
            # only one live note.md; the others sit in excluded dirs, so no collision
            root = _mk(tmp, ["note.md", "archive/note.md", ".trash/note.md"])
            self.assertEqual(vault_names.check(root), [])


if __name__ == "__main__":
    unittest.main()
