#!/usr/bin/env python3
"""
JATS-Convert Skill
JATS (NISO Z39.96) journal XML to curation-ready Obsidian Markdown

Sibling of ``phiweaver.pdf.pdf_convert``: the same output contract
(``<stem>_converted.md`` plus ``<stem>_converted_report.json``, media under
``03-Media/<stem>/``), a different input format. Publisher XML declares the structure a
PDF only implies — section types, figure and reference cross-reference ids, italics on
gene names — so nothing here is inferred from page layout and there is no OCR step.

Two things JATS does *not* carry, both handled explicitly rather than silently:
- **Images.** ``<graphic xlink:href="...">`` names a file that is usually not shipped with
  the XML. Every reference is checked on disk and the missing ones are reported, in the
  markdown and in the JSON, so a curation draft can state the limitation instead of a
  reader assuming the figures were read.
- **PMID.** Some publishers (MDPI among them) emit a DOI and no PMID, and the rest of the
  toolchain keys curation on the PMID. It is resolved from the DOI via Europe PMC when the
  network allows; failure is reported, never fatal.

To acquire a paper *from* Europe PMC — full text plus the figure images that make a
conversion more than captions — see :mod:`phiweaver.jats.europepmc`.

Usage: python3 -m phiweaver.jats.jats_convert <xml_file>
"""

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path
from xml.etree import ElementTree as ET

from phiweaver.jats import europepmc

XLINK_HREF = "{http://www.w3.org/1999/xlink}href"

# Image extensions a publisher graphic may resolve to when the href carries none, or
# carries a print-only one (.tif) while the shipped asset is web-sized.
GRAPHIC_EXTS = [".tif", ".tiff", ".jpg", ".jpeg", ".png", ".gif", ".eps", ".svg", ".webp"]


# --------------------------------------------------------------------------- helpers

def _tag(el) -> str:
    """Local element name, namespace-insensitive."""
    return el.tag.rpartition("}")[2] if isinstance(el.tag, str) else ""


def _collapse(text: str) -> str:
    """Collapse XML-pretty-printing whitespace without touching intentional content."""
    return re.sub(r"[ \t\r\n]+", " ", text or "").strip()


def _md_children(el) -> str:
    """Render an element's mixed content (text + inline children + tails) to Markdown."""
    parts = [el.text or ""]
    for child in el:
        parts.append(_md_element(child))
        parts.append(child.tail or "")
    return "".join(parts)


def _md_element(el) -> str:
    """Render one inline element. Unknown tags degrade to their text, never to nothing."""
    name = _tag(el)
    inner = _md_children(el)

    if not inner.strip():
        # An empty wrapper still may carry a tail; the caller handles that.
        return inner

    if name == "italic":
        return f"*{inner}*"
    if name in ("bold", "b"):
        return f"**{inner}**"
    if name == "monospace":
        return f"`{inner}`"
    if name == "sup":
        # HTML passthrough: Obsidian renders it, and "6 x 10<sup>6</sup> CFU/mL" stays
        # readable as a number rather than collapsing to an ambiguous "6 x 106".
        return f"<sup>{inner}</sup>"
    if name == "sub":
        return f"<sub>{inner}</sub>"
    if name in ("ext-link", "uri"):
        href = el.get(XLINK_HREF) or el.get("href") or inner
        return f"[{inner}]({href})"
    if name == "inline-graphic":
        href = el.get(XLINK_HREF) or ""
        return f"![{inner}]({href})"

    # xref (citation/figure markers), sc, underline, named-content, styled-content,
    # inline-formula, mml:* and anything else: keep the text, drop the wrapper.
    return inner


def _para(el) -> str:
    """A <p> as a single Markdown paragraph."""
    return _collapse(_md_children(el))


def _plain(el) -> str:
    """All descendant text of an element, collapsed. For metadata fields."""
    return _collapse("".join(el.itertext())) if el is not None else ""


def _find_text(parent, path: str) -> str:
    return _plain(parent.find(path)) if parent is not None else ""


def _yaml_scalar(value: str) -> str:
    """Quote a value for YAML frontmatter.

    Journal XML italicises species and gene names, which render as ``*Sec2p*``. A bare
    ``*`` opens an *alias node* in YAML, so an unquoted markdown value silently breaks
    the whole frontmatter block. Everything string-ish is quoted, with embedded double
    quotes downgraded to single.
    """
    return '"{}"'.format(str(value).replace('"', "'"))


# ------------------------------------------------------------------- PMID resolution

def resolve_ids_from_doi(doi: str, timeout: float = 15.0) -> dict:
    """Map a DOI to ``{'pmid': ..., 'pmcid': ...}`` via Europe PMC.

    Europe PMC rather than NCBI's ID Converter because one call answers both "what are
    the other identifiers" and "is the full text retrievable" — and the second question
    is the one that decides the ingest route. See :mod:`phiweaver.jats.europepmc`.

    Returns ``{}`` on any failure — no network, HTTP error, or an unmatched DOI. A
    conversion must never fail because an enrichment lookup did.
    """
    if not doi:
        return {}
    try:
        record = europepmc.resolve(doi, timeout=timeout)
    except Exception:
        # Deliberately broad. This is enrichment: an unparseable DOI, a client bug or
        # anything else here must degrade to "no PMID", never abort a conversion that
        # has already succeeded in every other respect.
        return {}
    if not record.get("found"):
        return {}
    return {k: record[k] for k in ("pmid", "pmcid") if record.get(k)}


# ---------------------------------------------------------------------- the converter

class JATSConvertSkill:
    """JATS journal XML to Obsidian Markdown, structure-preserving."""

    def __init__(self, config=None):
        self.config = config or self._load_default_config()
        self.xml_path = None
        self.xml_name = None
        self.output_dir = None
        self.images_dir = None
        self.root = None
        self.meta = {}
        self.document_sections = []
        self.all_figures = []
        self.all_tables = []
        self.references = []
        self.graphics = []
        self.warnings = []

    def _load_default_config(self):
        return {
            'output_directory': '.',
            'images_directory': '03-Media',
            'resolve_pmid': True,
            'quality_validation': True,
            'create_index': True,
            'include_references': True,
            'debug': False,
        }

    # -- entry point ---------------------------------------------------------

    def convert_xml(self, xml_file, **kwargs):
        """Convert a JATS XML file. Returns the output path, or None on failure."""
        for key, value in kwargs.items():
            if key in self.config:
                self.config[key] = value

        if not self._validate_input(xml_file):
            return None

        self.xml_path = Path(xml_file).resolve()
        self.xml_name = self.xml_path.stem
        self._setup_directories()

        print(f"🚀 JATS-Convert Skill: {self.xml_path.name}")
        print(f"📁 Output: {self.output_dir}")

        try:
            print("📖 Phase 1: Parsing article metadata...")
            self._parse_metadata()

            print("🔍 Phase 2: Extracting body, figures and tables...")
            self._extract_body()
            self._extract_display_objects()
            self._extract_references()

            print("🖼️  Phase 3: Checking referenced graphics on disk...")
            self._audit_graphics()

            if self.config['resolve_pmid'] and not self.meta.get('pmid'):
                print("🔗 Phase 4: Resolving PMID from DOI (Europe PMC)...")
                self._resolve_pmid()

            print("📝 Phase 5: Markdown generation...")
            markdown_content = self._generate_markdown()

            if self.config['quality_validation']:
                print("✅ Phase 6: Quality validation...")
                self._validate_output_quality()

            output_file = self.output_dir / f"{self.xml_name}_converted.md"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(markdown_content)

            self._generate_conversion_report(output_file)
            self._print_success_summary(output_file)
            return output_file

        except Exception as e:
            print(f"❌ Conversion failed: {str(e)}")
            if self.config.get('debug', False):
                import traceback
                traceback.print_exc()
            return None

    def _validate_input(self, xml_file):
        """Validate the input is a readable JATS article."""
        xml_path = Path(xml_file)
        if not xml_path.exists():
            print(f"❌ Error: File not found: {xml_file}")
            return False

        if xml_path.suffix.lower() not in ('.xml', '.jats', '.nxml'):
            print(f"❌ Error: Not an XML file: {xml_file}")
            return False

        try:
            self.root = ET.parse(str(xml_path)).getroot()
        except ET.ParseError as e:
            print(f"❌ Error: Malformed XML: {e}")
            return False

        if _tag(self.root) != 'article':
            print(f"❌ Error: Not a JATS article (root element is "
                  f"<{_tag(self.root)}>, expected <article>): {xml_file}")
            return False

        return True

    def _setup_directories(self):
        if self.config['output_directory'] == '.':
            self.output_dir = Path.cwd()
        else:
            self.output_dir = Path(self.config['output_directory'])
        self.images_dir = self.output_dir / self.config['images_directory'] / self.xml_name

    # -- extraction ----------------------------------------------------------

    def _parse_metadata(self):
        """Pull front-matter metadata. Everything here is declared, not guessed."""
        front = self.root.find('front')
        journal_meta = front.find('journal-meta') if front is not None else None
        article_meta = front.find('article-meta') if front is not None else None

        meta = {
            'article_type': self.root.get('article-type', ''),
            'dtd_version': self.root.get('dtd-version', ''),
            'journal': _find_text(journal_meta, 'journal-title-group/journal-title'),
            'journal_abbrev': _find_text(journal_meta, "abbrev-journal-title"),
            'publisher': _find_text(journal_meta, 'publisher/publisher-name'),
            'issn': _find_text(journal_meta, 'issn'),
            'title': '', 'title_plain': '', 'doi': '', 'pmid': '', 'pmcid': '',
            'publisher_id': '', 'volume': '', 'issue': '', 'elocation_id': '',
            'fpage': '', 'lpage': '', 'year': '', 'authors': [], 'affiliations': [],
            'keywords': [], 'keywords_plain': [],
            'abstract': [], 'license': '', 'pmid_source': '',
        }

        if journal_meta is not None and not meta['journal']:
            meta['journal'] = _find_text(journal_meta, 'journal-title')

        if article_meta is None:
            self.warnings.append("no <article-meta> found — metadata is empty")
            self.meta = meta
            return

        title_el = article_meta.find('title-group/article-title')
        if title_el is not None:
            meta['title'] = _collapse(_md_children(title_el))
            meta['title_plain'] = _plain(title_el)

        for aid in article_meta.findall('article-id'):
            kind = aid.get('pub-id-type', '')
            if kind == 'doi':
                meta['doi'] = _plain(aid)
            elif kind == 'pmid':
                meta['pmid'] = _plain(aid)
                meta['pmid_source'] = 'xml'
            elif kind in ('pmc', 'pmcid'):
                meta['pmcid'] = _plain(aid)
            elif kind == 'publisher-id':
                meta['publisher_id'] = _plain(aid)

        for contrib in article_meta.findall('.//contrib[@contrib-type="author"]'):
            surname = _find_text(contrib, 'name/surname')
            given = _find_text(contrib, 'name/given-names')
            name = " ".join(p for p in (given, surname) if p) or _find_text(contrib, 'string-name')
            if not name:
                continue
            orcid = _find_text(contrib, 'contrib-id[@contrib-id-type="orcid"]')
            meta['authors'].append({
                'name': name,
                'surname': surname,
                'orcid': orcid,
                'corresponding': contrib.find('xref[@ref-type="corresp"]') is not None,
            })

        for aff in article_meta.findall('aff'):
            text = _plain(aff)
            if text:
                meta['affiliations'].append(text)

        for kwd in article_meta.findall('kwd-group/kwd'):
            text = _collapse(_md_children(kwd))
            if text:
                meta['keywords'].append(text)
                meta['keywords_plain'].append(_plain(kwd))

        abstract = article_meta.find('abstract')
        if abstract is not None:
            meta['abstract'] = [_para(p) for p in abstract.findall('.//p') if _para(p)]
        else:
            self.warnings.append("no <abstract> in the article metadata")

        meta['volume'] = _find_text(article_meta, 'volume')
        meta['issue'] = _find_text(article_meta, 'issue')
        meta['elocation_id'] = _find_text(article_meta, 'elocation-id')
        meta['fpage'] = _find_text(article_meta, 'fpage')
        meta['lpage'] = _find_text(article_meta, 'lpage')
        meta['license'] = _find_text(article_meta, 'permissions/license/license-p')

        for pub_date in article_meta.findall('pub-date'):
            year = _find_text(pub_date, 'year')
            if year:
                meta['year'] = year
                break

        self.meta = meta

    def _extract_body(self):
        """Walk <body> sections recursively, preserving nesting depth and sec-type."""
        body = self.root.find('body')
        if body is None:
            self.warnings.append("no <body> element — the XML may be metadata-only")
            return

        for sec in body.findall('sec'):
            self._walk_section(sec, depth=2)

        # Paragraphs sitting directly in <body>, outside any <sec>.
        loose = [_para(p) for p in body.findall('p')]
        loose = [p for p in loose if p]
        if loose:
            self.document_sections.append({
                'title': 'Body', 'sec_type': '', 'depth': 2, 'id': '',
                'blocks': loose,
            })

    def _walk_section(self, sec, depth):
        title_el = sec.find('title')
        title = _collapse(_md_children(title_el)) if title_el is not None else '(untitled section)'

        blocks = []
        for child in sec:
            name = _tag(child)
            if name == 'p':
                text = _para(child)
                if text:
                    blocks.append(text)
            elif name == 'list':
                blocks.extend(self._render_list(child))
            elif name == 'disp-quote':
                for p in child.findall('.//p'):
                    text = _para(p)
                    if text:
                        blocks.append(f"> {text}")
            elif name in ('disp-formula', 'boxed-text'):
                text = _plain(child)
                if text:
                    blocks.append(text)

        self.document_sections.append({
            'title': title,
            'sec_type': sec.get('sec-type', ''),
            'depth': min(depth, 6),
            'id': sec.get('id', ''),
            'blocks': blocks,
        })

        for sub in sec.findall('sec'):
            self._walk_section(sub, depth + 1)

    def _render_list(self, list_el):
        """Render <list> as Markdown bullets (ordered lists keep their numbering)."""
        ordered = list_el.get('list-type') in ('order', 'ordered', 'roman-lower', 'alpha-lower')
        out = []
        for i, item in enumerate(list_el.findall('list-item'), start=1):
            text = " ".join(t for t in (_para(p) for p in item.findall('p')) if t)
            if not text:
                text = _plain(item)
            if text:
                out.append(f"{i}. {text}" if ordered else f"- {text}")
        return out

    def _extract_display_objects(self):
        """Collect every <fig> and <table-wrap>, wherever they sit.

        Publishers place these inline in <body> or grouped in a back-matter
        display-objects section (MDPI does the latter), so the whole tree is scanned and
        results are de-duplicated by id.
        """
        seen_figs, seen_tables = set(), set()

        for fig in self.root.iter():
            name = _tag(fig)
            if name == 'fig':
                key = fig.get('id') or id(fig)
                if key in seen_figs:
                    continue
                seen_figs.add(key)
                self.all_figures.append({
                    'id': fig.get('id', ''),
                    'label': _find_text(fig, 'label'),
                    'caption': self._caption_of(fig),
                    'graphics': self._graphics_of(fig),
                })
            elif name == 'table-wrap':
                key = fig.get('id') or id(fig)
                if key in seen_tables:
                    continue
                seen_tables.add(key)
                self.all_tables.append({
                    'id': fig.get('id', ''),
                    'label': _find_text(fig, 'label'),
                    'caption': self._caption_of(fig),
                    'graphics': self._graphics_of(fig),
                    'rows': self._table_rows(fig),
                    'footer': [_para(p) for p in fig.findall('table-wrap-foot//p') if _para(p)],
                })

    def _caption_of(self, el) -> str:
        caption = el.find('caption')
        if caption is None:
            return ''
        parts = []
        title_el = caption.find('title')
        if title_el is not None:
            parts.append(_collapse(_md_children(title_el)))
        parts.extend(_para(p) for p in caption.findall('p'))
        return " ".join(p for p in parts if p)

    def _graphics_of(self, el):
        out = []
        for g in el.iter():
            if _tag(g) in ('graphic', 'inline-graphic'):
                href = g.get(XLINK_HREF) or g.get('href') or ''
                if href:
                    out.append(href)
                    self.graphics.append(href)
        return out

    def _table_rows(self, table_wrap):
        """Extract a real <table> as a list of rows. Image-only tables return []."""
        table = table_wrap.find('.//table')
        if table is None:
            return []
        rows = []
        for tr in table.iter():
            if _tag(tr) != 'tr':
                continue
            cells = [_collapse(_md_children(td)).replace('|', '\\|')
                     for td in tr if _tag(td) in ('td', 'th')]
            if cells:
                rows.append(cells)
        return rows

    def _extract_references(self):
        for ref in self.root.findall('.//ref-list/ref'):
            citation = ref.find('element-citation')
            if citation is None:
                citation = ref.find('mixed-citation')
            if citation is None:
                self.references.append({'label': _find_text(ref, 'label'), 'text': _plain(ref)})
                continue

            authors = []
            for name_el in citation.findall('.//name'):
                surname = _find_text(name_el, 'surname')
                given = _find_text(name_el, 'given-names')
                if surname:
                    authors.append(f"{surname} {given}".strip())

            pub_ids = {}
            for pid in citation.findall('pub-id'):
                pub_ids[pid.get('pub-id-type', '')] = _plain(pid)

            self.references.append({
                'label': _find_text(ref, 'label'),
                'authors': authors,
                'title': _find_text(citation, 'article-title'),
                'source': _find_text(citation, 'source'),
                'year': _find_text(citation, 'year'),
                'volume': _find_text(citation, 'volume'),
                'fpage': _find_text(citation, 'fpage'),
                'lpage': _find_text(citation, 'lpage'),
                'doi': pub_ids.get('doi', ''),
                'pmid': pub_ids.get('pmid', ''),
            })

    def _audit_graphics(self):
        """Check each referenced graphic on disk. This is the honesty step.

        JATS names image files it does not ship. Recording present/absent here is what
        lets a curation draft say "figure content is captions only" as a fact rather
        than a reader assuming the panels were seen.
        """
        search_dirs = [self.xml_path.parent, self.images_dir,
                       self.xml_path.parent / self.config['images_directory']]
        for href in self.graphics:
            resolved = self._locate_graphic(href, search_dirs)
            self.graphics_status = getattr(self, 'graphics_status', {})
            self.graphics_status[href] = str(resolved) if resolved else ''

        absent = [h for h, p in getattr(self, 'graphics_status', {}).items() if not p]
        if absent:
            self.warnings.append(
                f"{len(absent)} of {len(getattr(self, 'graphics_status', {}))} referenced "
                f"graphics are not present on disk — figure content is CAPTIONS ONLY. "
                f"Any claim that needs the image itself cannot be made from this file."
            )

    def _locate_graphic(self, href, search_dirs):
        stem = Path(href).stem
        for directory in search_dirs:
            if not directory or not directory.exists():
                continue
            candidate = directory / href
            if candidate.exists():
                return candidate
            for ext in GRAPHIC_EXTS:
                candidate = directory / f"{stem}{ext}"
                if candidate.exists():
                    return candidate
        return None

    def _resolve_pmid(self):
        found = resolve_ids_from_doi(self.meta.get('doi', ''))
        if found.get('pmid'):
            self.meta['pmid'] = found['pmid']
            self.meta['pmid_source'] = 'europepmc'
            self.meta['pmcid'] = self.meta.get('pmcid') or found.get('pmcid', '')
            print(f"   ✅ PMID:{self.meta['pmid']}"
                  + (f" · {self.meta['pmcid']}" if self.meta.get('pmcid') else ""))
        else:
            self.meta['pmid_source'] = 'unresolved'
            self.warnings.append(
                "PMID not present in the XML and could not be resolved from the DOI "
                "(no network, or NCBI has no record). Downstream tools key on the PMID — "
                "supply it by hand."
            )
            print("   ⚠️  PMID unresolved")

    # -- rendering -----------------------------------------------------------

    def _generate_markdown(self):
        content = []
        content.extend(self._frontmatter())
        content.extend(self._header_block())

        if self.document_sections and self.config.get('create_index', True):
            content.append("## Document Structure")
            content.append("")
            for sec in self.document_sections:
                indent = "  " * max(0, sec['depth'] - 2)
                content.append(f"{indent}- [[#{sec['title']}]]")
            content.append("")

        for sec in self.document_sections:
            content.append(f"{'#' * sec['depth']} {sec['title']}")
            content.append("")
            for block in sec['blocks']:
                content.append(block)
                content.append("")

        content.extend([
            "",
            "---",
            "",
            "# Figures and Tables",
            "",
            "*This section contains all figures and tables with complete captions, "
            "clearly separated from the main text.*",
            "",
        ])

        if self.all_figures:
            content.extend(self._figures_section())
        if self.all_tables:
            content.extend(self._tables_section())

        if self.references and self.config.get('include_references', True):
            content.extend(self._references_section())

        if self.config.get('create_index', True):
            content.extend(self._conversion_index())

        return '\n'.join(content)

    def _frontmatter(self):
        meta = self.meta
        lines = [
            "---",
            f"created: {date.today()}",
            "type: literature",
            "tags: [literature, converted-xml, jats-convert-skill]",
            f"source: {self.xml_path.name}",
            "source_format: jats",
        ]
        if meta.get('title'):
            lines.append(f"title: {_yaml_scalar(meta['title_plain'] or meta['title'])}")
        for key in ('doi', 'pmid', 'pmcid', 'journal'):
            if meta.get(key):
                lines.append(f"{key}: {_yaml_scalar(meta[key])}")
        for key in ('year', 'volume', 'issue'):
            if meta.get(key):
                lines.append(f"{key}: {meta[key]}")
        if meta.get('keywords_plain'):
            lines.append("keywords: [{}]".format(
                ", ".join(_yaml_scalar(k) for k in meta['keywords_plain'])))
        lines.extend([
            f"figures: {len(self.all_figures)}",
            f"tables: {len(self.all_tables)}",
            f"sections: {len(self.document_sections)}",
            f"references: {len(self.references)}",
            f"graphics_present: {sum(1 for v in getattr(self, 'graphics_status', {}).values() if v)}",
            f"graphics_absent: {sum(1 for v in getattr(self, 'graphics_status', {}).values() if not v)}",
            "conversion_tool: jats-convert-skill",
            "conversion_quality: structural",
            "---",
            "",
        ])
        return lines

    def _header_block(self):
        meta = self.meta
        content = [f"# {meta.get('title') or self.xml_name}", ""]

        authors = meta.get('authors', [])
        if authors:
            names = ", ".join(a['name'] + (" *" if a['corresponding'] else "") for a in authors)
            content.extend([f"**Authors**: {names}", ""])

        citation_bits = [b for b in (
            meta.get('journal'), meta.get('year'),
            f"{meta['volume']}({meta['issue']})" if meta.get('volume') and meta.get('issue')
            else meta.get('volume'),
            meta.get('elocation_id') or meta.get('fpage'),
        ) if b]
        if citation_bits:
            content.extend([f"**Citation**: {', '.join(citation_bits)}", ""])

        ids = [f"DOI:{meta['doi']}" if meta.get('doi') else "",
               f"PMID:{meta['pmid']}" if meta.get('pmid') else "",
               meta.get('pmcid', '')]
        ids = [i for i in ids if i]
        if ids:
            source_note = f" *(PMID via {meta['pmid_source']})*" if meta.get('pmid_source') == 'europepmc' else ""
            content.extend([f"**Identifiers**: {' · '.join(ids)}{source_note}", ""])

        content.extend([
            f"*Converted from JATS XML: {self.xml_path.name}*",
            f"*Conversion date: {date.today()}*",
            "",
        ])

        if self.warnings:
            content.extend(["> [!warning] Conversion caveats"])
            content.extend(f"> - {w}" for w in self.warnings)
            content.append("")

        if meta.get('abstract'):
            content.extend(["## Abstract", ""])
            for para in meta['abstract']:
                content.extend([para, ""])

        if meta.get('keywords'):
            content.extend([f"**Keywords**: {', '.join(meta['keywords'])}", ""])

        return content

    def _figures_section(self):
        content = ["## Figures", ""]
        status = getattr(self, 'graphics_status', {})
        for fig in self.all_figures:
            label = fig['label'] or fig['id'] or 'Figure'
            content.extend([f"### {label}", ""])
            if fig['caption']:
                content.extend([f"**{label}** {fig['caption']}", ""])
            for href in fig['graphics']:
                if status.get(href):
                    content.append(f"![[{self.config['images_directory']}/{self.xml_name}/{Path(href).name}]]")
                else:
                    content.append(f"*Image not shipped with the XML: `{href}` — caption only.*")
                content.append("")
        return content

    def _tables_section(self):
        content = ["## Tables", ""]
        status = getattr(self, 'graphics_status', {})
        for table in self.all_tables:
            label = table['label'] or table['id'] or 'Table'
            content.extend([f"### {label}", ""])
            if table['caption']:
                content.extend([f"**{label}** {table['caption']}", ""])

            rows = table['rows']
            if rows:
                header, body = rows[0], rows[1:]
                width = max(len(r) for r in rows)
                header = header + [""] * (width - len(header))
                content.append("| " + " | ".join(header) + " |")
                content.append("| " + " | ".join(["---"] * width) + " |")
                for row in body:
                    row = row + [""] * (width - len(row))
                    content.append("| " + " | ".join(row) + " |")
                content.append("")
            else:
                for href in table['graphics']:
                    if status.get(href):
                        content.append(f"![[{self.config['images_directory']}/{self.xml_name}/{Path(href).name}]]")
                    else:
                        content.append(f"*Table image not shipped with the XML: `{href}` — caption only.*")
                    content.append("")

            for note in table['footer']:
                content.extend([f"*{note}*", ""])
        return content

    def _references_section(self):
        content = ["", "---", "", "## References", ""]
        for ref in self.references:
            label = ref.get('label', '') or ''
            if 'text' in ref:
                content.append(f"{label} {ref['text']}".strip())
                continue
            authors = ref.get('authors', [])
            author_str = ", ".join(authors[:3])
            if len(authors) > 3:
                author_str += " et al."
            bits = [author_str, ref.get('title', ''), ref.get('source', ''), ref.get('year', '')]
            if ref.get('volume'):
                pages = f":{ref['fpage']}" + (f"-{ref['lpage']}" if ref.get('lpage') else "")
                bits.append(f"{ref['volume']}{pages if ref.get('fpage') else ''}")
            line = ". ".join(b for b in bits if b)
            ids = " ".join(f"{k.upper()}:{ref[k]}" for k in ('doi', 'pmid') if ref.get(k))
            content.append(f"{label} {line}. {ids}".strip())
        content.append("")
        return content

    def _conversion_index(self):
        status = getattr(self, 'graphics_status', {})
        present = sum(1 for v in status.values() if v)
        content = [
            "",
            "---",
            "",
            "## Conversion Index",
            "",
            "### Statistics",
            f"- **Sections Detected**: {len(self.document_sections)}",
            f"- **Figures Found**: {len(self.all_figures)}",
            f"- **Tables Found**: {len(self.all_tables)}",
            f"- **References Found**: {len(self.references)}",
            "",
            "### Media",
            f"- **Graphics Referenced**: {len(status)}",
            f"- **Graphics Present on Disk**: {present}",
            f"- **Graphics Absent**: {len(status) - present}",
            "",
            "### Files Generated",
            f"- **Markdown File**: `{self.xml_name}_converted.md`",
            f"- **Images Directory**: `{self.config['images_directory']}/{self.xml_name}/`",
            "",
        ]
        return content

    # -- reporting -----------------------------------------------------------

    def _validate_output_quality(self):
        issues = list(self.warnings)

        no_caption = [f for f in self.all_figures if not f['caption']]
        if no_caption:
            issues.append(f"⚠️  {len(no_caption)} figures without captions")

        if not self.document_sections:
            issues.append("⚠️  No body sections found — check the XML is a full-text article")

        if not self.meta.get('doi') and not self.meta.get('pmid'):
            issues.append("⚠️  Neither DOI nor PMID present — the article cannot be keyed")

        if issues:
            print("⚠️  Quality validation issues found:")
            for issue in issues:
                print(f"   {issue}")
        else:
            print("✅ Quality validation passed - high quality conversion")

        return issues

    def _generate_conversion_report(self, output_file):
        status = getattr(self, 'graphics_status', {})
        report = {
            'source_file': str(self.xml_path),
            'output_file': str(output_file),
            'conversion_date': str(date.today()),
            'source_format': 'jats',
            'article': {
                'title': self.meta.get('title', ''),
                'doi': self.meta.get('doi', ''),
                'pmid': self.meta.get('pmid', ''),
                'pmcid': self.meta.get('pmcid', ''),
                'pmid_source': self.meta.get('pmid_source', ''),
                'journal': self.meta.get('journal', ''),
                'year': self.meta.get('year', ''),
                'publisher': self.meta.get('publisher', ''),
                'article_type': self.meta.get('article_type', ''),
                'dtd_version': self.meta.get('dtd_version', ''),
                'authors': [a['name'] for a in self.meta.get('authors', [])],
                'keywords': self.meta.get('keywords', []),
            },
            'statistics': {
                'sections_detected': len(self.document_sections),
                'figures_found': len(self.all_figures),
                'tables_found': len(self.all_tables),
                'references_found': len(self.references),
                'abstract_paragraphs': len(self.meta.get('abstract', [])),
            },
            'media': {
                'images_directory': str(self.images_dir),
                'graphics_referenced': len(status),
                'graphics_present': sum(1 for v in status.values() if v),
                'graphics_absent': sorted(h for h, v in status.items() if not v),
            },
            'quality_metrics': {
                'figures_with_captions': len([f for f in self.all_figures if f['caption']]),
                'tables_with_captions': len([t for t in self.all_tables if t['caption']]),
                'tables_with_parsed_rows': len([t for t in self.all_tables if t['rows']]),
                'sections_with_content': len([s for s in self.document_sections if s['blocks']]),
            },
            'warnings': self.warnings,
            'config_used': self.config,
        }

        report_file = output_file.parent / f"{output_file.stem}_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)

        print(f"📊 Conversion report saved: {report_file.name}")

    def _print_success_summary(self, output_file):
        status = getattr(self, 'graphics_status', {})
        absent = sum(1 for v in status.values() if not v)
        print(f"\n✅ JATS-Convert Skill completed successfully!")
        print(f"📄 Output file: {output_file.name}")
        print(f"📊 Statistics:")
        print(f"   • {len(self.document_sections)} sections")
        print(f"   • {len(self.all_figures)} figures, {len(self.all_tables)} tables")
        print(f"   • {len(self.references)} references")
        if absent:
            print(f"   • ⚠️  {absent} referenced graphics absent — captions only")
        if self.meta.get('pmid'):
            print(f"   • PMID:{self.meta['pmid']} ({self.meta.get('pmid_source', 'xml')})")
        print(f"\n🎯 Ready for curation.")


def main():
    """Command-line interface for the JATS-Convert skill"""
    parser = argparse.ArgumentParser(
        description='JATS-Convert Skill: JATS journal XML to Obsidian Markdown',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 -m phiweaver.jats.jats_convert paper.xml
  python3 -m phiweaver.jats.jats_convert paper.xml --output-dir ./converted
  python3 -m phiweaver.jats.jats_convert paper.xml --no-pmid-lookup --debug
        """
    )

    parser.add_argument('xml_file', help='JATS XML file to convert')
    parser.add_argument('--output-dir', default='.', help='Output directory (default: current)')
    parser.add_argument('--images-dir', default='03-Media', help='Images directory (default: 03-Media)')
    parser.add_argument('--no-pmid-lookup', action='store_true',
                        help='Skip the DOI->PMID lookup at NCBI (stay fully offline)')
    parser.add_argument('--no-references', action='store_true', help='Skip the reference list')
    parser.add_argument('--no-validation', action='store_true', help='Skip quality validation')
    parser.add_argument('--no-index', action='store_true', help='Skip index generation')
    parser.add_argument('--debug', action='store_true', help='Enable debug output')

    args = parser.parse_args()

    config = {
        'output_directory': args.output_dir,
        'images_directory': args.images_dir,
        'resolve_pmid': not args.no_pmid_lookup,
        'include_references': not args.no_references,
        'quality_validation': not args.no_validation,
        'create_index': not args.no_index,
        'debug': args.debug,
    }

    converter = JATSConvertSkill(config)
    result = converter.convert_xml(args.xml_file)

    sys.exit(0 if result else 1)


if __name__ == "__main__":
    main()
