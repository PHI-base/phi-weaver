#!/usr/bin/env python3
"""Network-free tests for phiweaver.export.docx (stdlib only)."""

import io
import tempfile
import unittest
import zipfile
from pathlib import Path
from xml.dom.minidom import parseString

from phiweaver.export import docx


SAMPLE_MD = """---
title: skip me
status: draft
---

# Title Heading

An intro paragraph with **bold** and `code` inline.

> A blockquote warning line.

## Section Two

- first bullet
- second bullet with a `token`

| Tick | Gene | ID |
| --- | --- | --- |
| ☐ | FpSdhA | UniProtKB:K3UT42 |
| ☐ | Gene\\|Pipe | X1 |

```json
{"a": 1, "b": "<tag> & \\"quote\\""}
```
"""


class DocxBytesTest(unittest.TestCase):
    def setUp(self):
        self.data = docx.md_to_docx_bytes(SAMPLE_MD)
        self.zf = zipfile.ZipFile(io.BytesIO(self.data))
        self.doc = self.zf.read("word/document.xml").decode("utf-8")

    def test_valid_zip_with_required_parts(self):
        names = set(self.zf.namelist())
        for required in ("[Content_Types].xml", "_rels/.rels",
                         "word/document.xml", "word/styles.xml",
                         "word/_rels/document.xml.rels"):
            self.assertIn(required, names)

    def test_document_and_styles_are_well_formed_xml(self):
        parseString(self.doc)                                  # raises if malformed
        parseString(self.zf.read("word/styles.xml").decode("utf-8"))

    def test_frontmatter_is_skipped(self):
        self.assertNotIn("skip me", self.doc)

    def test_headings_use_heading_styles(self):
        self.assertIn("Title Heading", self.doc)
        self.assertIn('<w:pStyle w:val="Heading1"/>', self.doc)
        self.assertIn('<w:pStyle w:val="Heading2"/>', self.doc)

    def test_inline_bold_and_code(self):
        self.assertIn("<w:b/>", self.doc)                      # from **bold**
        self.assertIn("Consolas", self.doc)                    # from `code`

    def test_table_rendered_with_cells(self):
        self.assertIn("<w:tbl>", self.doc)
        self.assertIn("FpSdhA", self.doc)
        self.assertIn("UniProtKB:K3UT42", self.doc)

    def test_escaped_pipe_kept_in_cell(self):
        # "Gene\|Pipe" must become one cell "Gene|Pipe", escaped for XML as "Gene|Pipe"
        self.assertIn("Gene|Pipe", self.doc)

    def test_code_block_content_xml_escaped(self):
        self.assertIn("&lt;tag&gt;", self.doc)                 # < > escaped
        self.assertIn("&amp;", self.doc)                       # & escaped

    def test_blockquote_uses_quote_style(self):
        self.assertIn('<w:pStyle w:val="Quote"/>', self.doc)

    def test_bullets_present(self):
        self.assertIn("first bullet", self.doc)
        self.assertIn('<w:pStyle w:val="ListBullet"/>', self.doc)


class ConvertFileTest(unittest.TestCase):
    def test_convert_file_writes_sibling_docx(self):
        with tempfile.TemporaryDirectory() as d:
            md = Path(d) / "paper-DRAFT.md"
            md.write_text(SAMPLE_MD, encoding="utf-8")
            out = docx.convert_file(md)
            self.assertEqual(out, md.with_suffix(".docx"))
            self.assertTrue(out.exists())
            # opens as a valid zip
            zipfile.ZipFile(out)

    def test_convert_file_explicit_out(self):
        with tempfile.TemporaryDirectory() as d:
            md = Path(d) / "q.md"
            md.write_text("# Hi\n\ntext\n", encoding="utf-8")
            target = Path(d) / "custom.docx"
            out = docx.convert_file(md, target)
            self.assertEqual(out, target)
            self.assertTrue(target.exists())


class EntryQueueIntegrationTest(unittest.TestCase):
    """The entry-queue CLI writes a .docx alongside the .md by default."""

    DRAFT = """---
status: draft
---

# Draft

```json
{
  "meta": {"pmid": "1", "paper": "p", "system": "s", "draft_by": "phiweaver"},
  "canto": {
    "genes": [{"name": "G", "uniprot": "P11111", "organism": "Fusarium x", "locus": "L"}],
    "alleles": [{"name": "gΔ", "gene": "G", "type": "deletion", "expression": "null"}],
    "genotypes": [{"name": "gΔ", "organism": "Fusarium x", "alleles": ["gΔ"], "role": "experimental"}],
    "metagenotypes": [],
    "annotations": [{"feature_type": "genotype", "feature": "gΔ", "annotation_type": "pathogen_phenotype", "term_id": "PHIPO:0000015", "term_name": "reduced virulence", "evidence": "x", "extensions": [], "conditions": "", "figure": "F1"}]
  }
}
```
"""

    def test_cli_emits_md_and_docx(self):
        from phiweaver.canto import entry_queue as eq
        with tempfile.TemporaryDirectory() as d:
            draft = Path(d) / "PMID1-x-phiweaver-DRAFT.md"
            draft.write_text(self.DRAFT, encoding="utf-8")
            rc = eq.main([str(draft)])
            self.assertEqual(rc, 0)
            md_out = eq.default_out(str(draft))
            self.assertTrue(md_out.exists())
            self.assertTrue(md_out.with_suffix(".docx").exists())
            zipfile.ZipFile(md_out.with_suffix(".docx"))       # valid zip

    def test_no_docx_flag_skips_docx(self):
        from phiweaver.canto import entry_queue as eq
        with tempfile.TemporaryDirectory() as d:
            draft = Path(d) / "PMID2-x-phiweaver-DRAFT.md"
            draft.write_text(self.DRAFT, encoding="utf-8")
            eq.main([str(draft), "--no-docx"])
            md_out = eq.default_out(str(draft))
            self.assertTrue(md_out.exists())
            self.assertFalse(md_out.with_suffix(".docx").exists())

    def test_no_md_flag_writes_only_docx(self):
        from phiweaver.canto import entry_queue as eq
        with tempfile.TemporaryDirectory() as d:
            draft = Path(d) / "PMID3-x-phiweaver-DRAFT.md"
            draft.write_text(self.DRAFT, encoding="utf-8")
            eq.main([str(draft), "--no-md"])
            md_out = eq.default_out(str(draft))
            self.assertFalse(md_out.exists())
            self.assertTrue(md_out.with_suffix(".docx").exists())

    def test_no_md_and_no_docx_together_errors(self):
        from phiweaver.canto import entry_queue as eq
        with tempfile.TemporaryDirectory() as d:
            draft = Path(d) / "PMID4-x-phiweaver-DRAFT.md"
            draft.write_text(self.DRAFT, encoding="utf-8")
            with self.assertRaises(SystemExit):        # argparse .error() exits
                eq.main([str(draft), "--no-md", "--no-docx"])


if __name__ == "__main__":
    unittest.main()
