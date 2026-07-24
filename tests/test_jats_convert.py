#!/usr/bin/env python3
"""Network-free tests for jats_convert.py (offline over a fixture article; stdlib only)."""

import json
import tempfile
import unittest
from pathlib import Path

from phiweaver.jats import jats_convert as jc
from phiweaver.pipeline import curation_pipeline as cp


# A miniature but structurally faithful JATS article: nested sections, inline markup on a
# gene name, a back-matter display-objects block (how MDPI ships figures), a real table,
# and a graphic that is referenced but never shipped.
TINY_JATS = """<?xml version="1.0" encoding="UTF-8"?>
<article xmlns:xlink="http://www.w3.org/1999/xlink" article-type="research-article" dtd-version="1.3">
  <front>
    <journal-meta>
      <journal-title-group><journal-title>Journal of Fungi</journal-title></journal-title-group>
      <publisher><publisher-name>MDPI</publisher-name></publisher>
    </journal-meta>
    <article-meta>
      <article-id pub-id-type="doi">10.3390/jof11010036</article-id>
      <title-group><article-title>Roles of <italic>Sec2p</italic> in Growth</article-title></title-group>
      <contrib-group>
        <contrib contrib-type="author">
          <name><surname>Liu</surname><given-names>Yuhuan</given-names></name>
        </contrib>
        <contrib contrib-type="author">
          <name><surname>Wang</surname><given-names>Li</given-names></name>
          <xref rid="c1" ref-type="corresp">*</xref>
        </contrib>
      </contrib-group>
      <pub-date pub-type="epub"><year>2025</year></pub-date>
      <volume>11</volume>
      <issue>1</issue>
      <abstract><p>Deleting <italic>Sec2p</italic> slowed growth at 6 &#xD7; 10<sup>6</sup> CFU/mL.</p></abstract>
      <kwd-group><kwd><italic>Aspergillus fumigatus</italic></kwd><kwd>autophagy</kwd></kwd-group>
    </article-meta>
  </front>
  <body>
    <sec id="sec1" sec-type="intro">
      <title>1. Introduction</title>
      <p>Growth matters [<xref ref-type="bibr" rid="B1">1</xref>].</p>
    </sec>
    <sec id="sec3" sec-type="results">
      <title>3. Results</title>
      <sec id="sec3dot1">
        <title>3.1. Colony Growth</title>
        <p>The <italic>&#x394;sec2p</italic> colony shrank (<xref ref-type="fig" rid="f1">Figure 1</xref>).</p>
      </sec>
    </sec>
  </body>
  <back>
    <ref-list>
      <ref id="B1">
        <label>1.</label>
        <element-citation publication-type="journal">
          <person-group person-group-type="author">
            <name><surname>Brown</surname><given-names>G.D.</given-names></name>
          </person-group>
          <article-title>Hidden Killers</article-title>
          <source>Sci. Transl. Med.</source>
          <year>2012</year>
          <volume>4</volume>
          <fpage>165</fpage>
          <pub-id pub-id-type="pmid">23253612</pub-id>
        </element-citation>
      </ref>
    </ref-list>
    <sec sec-type="display-objects">
      <title>Figures</title>
      <fig id="f1" position="float">
        <label>Figure 1</label>
        <caption><p>Colony morphology of <italic>A. fumigatus</italic>. Bar, 50 &#x3BC;m.</p></caption>
        <graphic xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="jof-g001.tif"/>
      </fig>
      <table-wrap id="t1">
        <label>Table 1</label>
        <caption><p>Strains used.</p></caption>
        <table>
          <thead><tr><th>Strain</th><th>Genotype</th></tr></thead>
          <tbody><tr><td>IFM40808</td><td>wild type</td></tr></tbody>
        </table>
      </table-wrap>
    </sec>
  </back>
</article>
"""

NOT_JATS = """<?xml version="1.0"?><collection><record>nope</record></collection>"""


def _convert(tmpdir, xml_text=TINY_JATS, name="paper.xml", **cfg):
    """Convert a fixture offline; returns (converter, output_path)."""
    src = Path(tmpdir) / name
    src.write_text(xml_text, encoding="utf-8")
    config = dict(jc.JATSConvertSkill()._load_default_config())
    config.update({"output_directory": str(tmpdir), "resolve_pmid": False})
    config.update(cfg)
    conv = jc.JATSConvertSkill(config)
    return conv, conv.convert_xml(str(src))


class InlineMarkdownTests(unittest.TestCase):
    def test_italic_bold_and_superscript(self):
        from xml.etree import ElementTree as ET
        el = ET.fromstring("<p>a <italic>Sec2p</italic> b <bold>x</bold> 10<sup>6</sup> c</p>")
        self.assertEqual(jc._para(el), "a *Sec2p* b **x** 10<sup>6</sup> c")

    def test_xref_keeps_text_and_drops_wrapper(self):
        from xml.etree import ElementTree as ET
        el = ET.fromstring('<p>see [<xref ref-type="bibr" rid="B1">1</xref>].</p>')
        self.assertEqual(jc._para(el), "see [1].")

    def test_ext_link_becomes_markdown_link(self):
        from xml.etree import ElementTree as ET
        el = ET.fromstring(
            '<p xmlns:xlink="http://www.w3.org/1999/xlink">'
            '<ext-link xlink:href="https://e.org">site</ext-link></p>')
        self.assertEqual(jc._para(el), "[site](https://e.org)")

    def test_unknown_inline_tag_keeps_its_text(self):
        from xml.etree import ElementTree as ET
        el = ET.fromstring("<p>a <styled-content>kept</styled-content> b</p>")
        self.assertEqual(jc._para(el), "a kept b")


class YamlScalarTests(unittest.TestCase):
    def test_markdown_value_is_quoted(self):
        # A bare leading '*' is a YAML alias node and would break the frontmatter block.
        self.assertEqual(jc._yaml_scalar("*Sec2p*"), '"*Sec2p*"')

    def test_embedded_double_quotes_downgraded(self):
        self.assertEqual(jc._yaml_scalar('a "b" c'), '"a \'b\' c"')


class ValidateInputTests(unittest.TestCase):
    def test_rejects_non_xml_suffix(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "paper.pdf"
            p.write_text("x", encoding="utf-8")
            self.assertFalse(jc.JATSConvertSkill()._validate_input(str(p)))

    def test_rejects_missing_file(self):
        self.assertFalse(jc.JATSConvertSkill()._validate_input("/nonexistent/paper.xml"))

    def test_rejects_xml_that_is_not_a_jats_article(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "paper.xml"
            p.write_text(NOT_JATS, encoding="utf-8")
            self.assertFalse(jc.JATSConvertSkill()._validate_input(str(p)))

    def test_rejects_malformed_xml(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "paper.xml"
            p.write_text("<article><body>", encoding="utf-8")
            self.assertFalse(jc.JATSConvertSkill()._validate_input(str(p)))

    def test_accepts_nxml(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "paper.nxml"
            p.write_text(TINY_JATS, encoding="utf-8")
            self.assertTrue(jc.JATSConvertSkill()._validate_input(str(p)))


class MetadataTests(unittest.TestCase):
    def test_extracts_identifiers_and_citation_fields(self):
        with tempfile.TemporaryDirectory() as d:
            conv, out = _convert(d)
            self.assertIsNotNone(out)
            self.assertEqual(conv.meta["doi"], "10.3390/jof11010036")
            self.assertEqual(conv.meta["journal"], "Journal of Fungi")
            self.assertEqual(conv.meta["publisher"], "MDPI")
            self.assertEqual(conv.meta["year"], "2025")
            self.assertEqual(conv.meta["volume"], "11")

    def test_title_keeps_markdown_but_plain_form_is_kept_too(self):
        with tempfile.TemporaryDirectory() as d:
            conv, _ = _convert(d)
            self.assertEqual(conv.meta["title"], "Roles of *Sec2p* in Growth")
            self.assertEqual(conv.meta["title_plain"], "Roles of Sec2p in Growth")

    def test_authors_and_corresponding_flag(self):
        with tempfile.TemporaryDirectory() as d:
            conv, _ = _convert(d)
            names = [a["name"] for a in conv.meta["authors"]]
            self.assertEqual(names, ["Yuhuan Liu", "Li Wang"])
            self.assertFalse(conv.meta["authors"][0]["corresponding"])
            self.assertTrue(conv.meta["authors"][1]["corresponding"])

    def test_no_pmid_in_xml_is_not_invented(self):
        with tempfile.TemporaryDirectory() as d:
            conv, _ = _convert(d)  # resolve_pmid disabled
            self.assertEqual(conv.meta["pmid"], "")


class StructureTests(unittest.TestCase):
    def test_sections_nest_by_depth(self):
        with tempfile.TemporaryDirectory() as d:
            conv, _ = _convert(d)
            found = {s["title"]: s["depth"] for s in conv.document_sections}
            self.assertEqual(found["1. Introduction"], 2)
            self.assertEqual(found["3. Results"], 2)
            self.assertEqual(found["3.1. Colony Growth"], 3)

    def test_sec_type_is_preserved(self):
        with tempfile.TemporaryDirectory() as d:
            conv, _ = _convert(d)
            by_title = {s["title"]: s for s in conv.document_sections}
            self.assertEqual(by_title["3. Results"]["sec_type"], "results")

    def test_figure_caption_extracted_from_back_matter_block(self):
        with tempfile.TemporaryDirectory() as d:
            conv, _ = _convert(d)
            self.assertEqual(len(conv.all_figures), 1)
            fig = conv.all_figures[0]
            self.assertEqual(fig["label"], "Figure 1")
            self.assertIn("Colony morphology of *A. fumigatus*", fig["caption"])

    def test_table_rows_parsed(self):
        with tempfile.TemporaryDirectory() as d:
            conv, _ = _convert(d)
            self.assertEqual(len(conv.all_tables), 1)
            self.assertEqual(conv.all_tables[0]["rows"],
                             [["Strain", "Genotype"], ["IFM40808", "wild type"]])

    def test_references_parsed_with_pmid(self):
        with tempfile.TemporaryDirectory() as d:
            conv, _ = _convert(d)
            self.assertEqual(len(conv.references), 1)
            ref = conv.references[0]
            self.assertEqual(ref["title"], "Hidden Killers")
            self.assertEqual(ref["pmid"], "23253612")


class GraphicsAuditTests(unittest.TestCase):
    def test_absent_graphic_is_reported_not_silently_linked(self):
        with tempfile.TemporaryDirectory() as d:
            conv, out = _convert(d)
            self.assertEqual(conv.graphics_status, {"jof-g001.tif": ""})
            self.assertTrue(any("CAPTIONS ONLY" in w for w in conv.warnings))
            text = Path(out).read_text(encoding="utf-8")
            self.assertIn("Image not shipped with the XML", text)

    def test_present_graphic_is_linked(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "jof-g001.tif").write_bytes(b"fake")
            conv, out = _convert(d)
            self.assertTrue(conv.graphics_status["jof-g001.tif"])
            self.assertFalse(any("CAPTIONS ONLY" in w for w in conv.warnings))
            self.assertIn("![[03-Media/paper/jof-g001.tif]]",
                          Path(out).read_text(encoding="utf-8"))

    def test_graphic_matched_on_stem_when_extension_differs(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "jof-g001.png").write_bytes(b"fake")  # web asset, .tif in the XML
            conv, _ = _convert(d)
            self.assertTrue(conv.graphics_status["jof-g001.tif"].endswith("jof-g001.png"))


class OutputContractTests(unittest.TestCase):
    def test_writes_converted_md_and_report_json(self):
        with tempfile.TemporaryDirectory() as d:
            conv, out = _convert(d)
            self.assertEqual(Path(out).name, "paper_converted.md")
            report = Path(d) / "paper_converted_report.json"
            self.assertTrue(report.exists())
            data = json.loads(report.read_text(encoding="utf-8"))
            self.assertEqual(data["source_format"], "jats")
            self.assertEqual(data["article"]["doi"], "10.3390/jof11010036")
            self.assertEqual(data["statistics"]["figures_found"], 1)
            self.assertEqual(data["statistics"]["references_found"], 1)
            self.assertEqual(data["media"]["graphics_absent"], ["jof-g001.tif"])

    def test_frontmatter_is_parseable_yaml_despite_markdown_values(self):
        with tempfile.TemporaryDirectory() as d:
            _, out = _convert(d)
            text = Path(out).read_text(encoding="utf-8")
            block = text.split("---", 2)[1]
            # '*' opens a YAML alias, so every markdown-bearing value must be quoted.
            for line in block.splitlines():
                if line.startswith(("title:", "keywords:")):
                    value = line.split(":", 1)[1].strip()
                    self.assertNotRegex(value, r"(^|[\[,]\s*)\*",
                                        f"unquoted markdown in frontmatter: {line}")

    def test_body_markup_survives_into_the_markdown(self):
        with tempfile.TemporaryDirectory() as d:
            _, out = _convert(d)
            text = Path(out).read_text(encoding="utf-8")
            self.assertIn("## 1. Introduction", text)
            self.assertIn("### 3.1. Colony Growth", text)
            self.assertIn("*Δsec2p*", text)          # gene italics preserved
            self.assertIn("10<sup>6</sup>", text)    # superscript not flattened


class DispatchTests(unittest.TestCase):
    def test_pdf_routes_to_pdf_converter(self):
        self.assertEqual(cp.converter_for("paper.pdf"), "phiweaver.pdf.pdf_convert")

    def test_xml_variants_route_to_jats_converter(self):
        for name in ("paper.xml", "paper.XML", "paper.nxml", "paper.jats"):
            self.assertEqual(cp.converter_for(name), "phiweaver.jats.jats_convert", name)

    def test_unsupported_format_returns_empty(self):
        self.assertEqual(cp.converter_for("paper.docx"), "")
        self.assertEqual(cp.converter_for("paper"), "")

    def test_process_pdf_workflow_is_an_alias(self):
        self.assertEqual(cp.CurationPipeline.process_pdf_workflow.__doc__.splitlines()[0],
                         "Back-compatible alias for :meth:`process_paper_workflow`.")


class PmidResolutionTests(unittest.TestCase):
    """The lookup is enrichment (now via Europe PMC): it must degrade, never raise."""

    def _offline(self):
        """Stub the single HTTP chokepoint in the Europe PMC client."""
        original = jc.europepmc._get
        jc.europepmc._get = lambda url, timeout=None, cache=None: (0, b"", "")
        self.addCleanup(lambda: setattr(jc.europepmc, "_get", original))

    def _resolving_to(self, pmid, pmcid):
        import json as _json
        body = _json.dumps({"hitCount": 1, "resultList": {"result": [
            {"id": pmid, "source": "MED", "pmid": pmid, "pmcid": pmcid,
             "doi": "10.3390/jof11010036", "title": "t", "isOpenAccess": "Y"}]}}).encode()
        original = jc.europepmc._get
        jc.europepmc._get = (
            lambda url, timeout=None, cache=None: (200, body, "application/json"))
        self.addCleanup(lambda: setattr(jc.europepmc, "_get", original))

    def test_empty_doi_short_circuits(self):
        self.assertEqual(jc.resolve_ids_from_doi(""), {})

    def test_network_failure_returns_empty(self):
        self._offline()
        self.assertEqual(jc.resolve_ids_from_doi("10.3390/jof11010036"), {})

    def test_malformed_doi_returns_empty_rather_than_raising(self):
        # classify_identifier raises for junk; the converter must absorb that.
        self.assertEqual(jc.resolve_ids_from_doi("not-a-doi"), {})

    def test_resolved_pmid_is_recorded_with_its_source(self):
        self._resolving_to("39852455", "PMC11767236")
        with tempfile.TemporaryDirectory() as d:
            conv, _ = _convert(d, resolve_pmid=True)
            self.assertEqual(conv.meta["pmid"], "39852455")
            self.assertEqual(conv.meta["pmcid"], "PMC11767236")
            self.assertEqual(conv.meta["pmid_source"], "europepmc")

    def test_unresolved_pmid_is_flagged_as_a_warning(self):
        self._offline()
        with tempfile.TemporaryDirectory() as d:
            conv, _ = _convert(d, resolve_pmid=True)
            self.assertEqual(conv.meta["pmid_source"], "unresolved")
            self.assertTrue(any("PMID" in w for w in conv.warnings))


if __name__ == "__main__":
    unittest.main()
