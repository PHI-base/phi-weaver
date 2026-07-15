#!/usr/bin/env python3
"""
phiweaver.export.docx — convert a phiweaver markdown output into a Word ``.docx``.

Why this exists: the two Route-1 deliverables — the phiweaver **DRAFT** and the PHI-Canto
**entry queue** — are written as GitHub-flavoured markdown, but curators and reviewers often
want the same content as a Word document. A ``.docx`` is just a ZIP of Office Open XML parts,
so this produces a valid Word file using **only the standard library** — no pandoc,
python-docx, or any third-party dependency (matching the rest of this package).

Coverage is pragmatic — the markdown constructs these documents actually use:

- YAML frontmatter (``---`` … ``---`` at the top) — skipped;
- ATX headings ``#`` … ``######``;
- paragraphs, with inline ``**bold**`` and `` `code` `` spans;
- GFM pipe tables (with the ``\\|`` pipe-escaping the entry queue emits);
- bullet lists (``-`` / ``*``);
- blockquotes (``>``);
- fenced code blocks (```` ``` ````) — e.g. the draft's ``canto`` JSON block.

Anything else is emitted as a plain paragraph. Deterministic: same markdown in, same bytes out.

Usage (from the repo root):

    python3 -m phiweaver.export.docx PMID..-phiweaver-DRAFT.md        # writes ..DRAFT.docx
    python3 -m phiweaver.export.docx draft.md entry-queue.md          # one .docx each
    python3 -m phiweaver.export.docx draft.md --out /path/out.docx
"""

from __future__ import annotations

import argparse
import io
import re
import sys
import zipfile
from pathlib import Path
from typing import List
from xml.sax.saxutils import escape

_W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"

_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")
_BULLET_RE = re.compile(r"^\s*[-*]\s+(.*)$")
_QUOTE_RE = re.compile(r"^>\s?(.*)$")
_HR_RE = re.compile(r"^\s*([-*_])(?:\s*\1){2,}\s*$")          # --- *** ___ horizontal rule
_TABLE_SEP_RE = re.compile(r"^\s*\|?[\s:|-]*-[\s:|-]*\|?\s*$")  # |---|:--:| separator row
_CELL_SPLIT_RE = re.compile(r"(?<!\\)\|")                       # split on unescaped pipes
_INLINE_RE = re.compile(r"(\*\*.+?\*\*|`[^`]+`)")


# --------------------------------------------------------------------- runs / paragraphs

def _run(text: str, bold: bool = False, code: bool = False) -> str:
    props = []
    if bold:
        props.append("<w:b/>")
    if code:
        props.append('<w:rFonts w:ascii="Consolas" w:hAnsi="Consolas" w:cs="Consolas"/>')
    rpr = f"<w:rPr>{''.join(props)}</w:rPr>" if props else ""
    return f'<w:r>{rpr}<w:t xml:space="preserve">{escape(text)}</w:t></w:r>'


def _runs(text: str) -> str:
    """Render inline markdown (**bold**, `code`) into a sequence of runs."""
    out = []
    for tok in _INLINE_RE.split(text):
        if not tok:
            continue
        if len(tok) >= 4 and tok.startswith("**") and tok.endswith("**"):
            out.append(_run(tok[2:-2], bold=True))
        elif len(tok) >= 2 and tok.startswith("`") and tok.endswith("`"):
            out.append(_run(tok[1:-1], code=True))
        else:
            out.append(_run(tok))
    return "".join(out) or _run("")


def _para(text: str, style: str | None = None) -> str:
    ppr = f'<w:pPr><w:pStyle w:val="{style}"/></w:pPr>' if style else ""
    return f"<w:p>{ppr}{_runs(text)}</w:p>"


def _bullet(text: str) -> str:
    ppr = '<w:pPr><w:pStyle w:val="ListBullet"/><w:ind w:left="360" w:hanging="360"/></w:pPr>'
    return f"<w:p>{ppr}{_run('•  ')}{_runs(text)}</w:p>"


def _code_line(line: str) -> str:
    ppr = '<w:pPr><w:pStyle w:val="Code"/></w:pPr>'
    run = ('<w:r><w:rPr><w:rFonts w:ascii="Consolas" w:hAnsi="Consolas" w:cs="Consolas"/></w:rPr>'
           f'<w:t xml:space="preserve">{escape(line)}</w:t></w:r>')
    return f"<w:p>{ppr}{run}</w:p>"


# ------------------------------------------------------------------------------ tables

def _split_row(line: str) -> List[str]:
    parts = _CELL_SPLIT_RE.split(line.strip())
    if parts and parts[0].strip() == "":
        parts = parts[1:]
    if parts and parts[-1].strip() == "":
        parts = parts[:-1]
    return [p.strip().replace("\\|", "|") for p in parts]


def _tc(text: str, header: bool) -> str:
    body = _run(text, bold=True) if header else _runs(text)
    return f'<w:tc><w:tcPr><w:tcW w:w="0" w:type="auto"/></w:tcPr><w:p>{body}</w:p></w:tc>'


def _table(rows: List[List[str]]) -> str:
    borders = "<w:tblBorders>" + "".join(
        f'<w:{edge} w:val="single" w:sz="4" w:space="0" w:color="999999"/>'
        for edge in ("top", "left", "bottom", "right", "insideH", "insideV")
    ) + "</w:tblBorders>"
    tblpr = f'<w:tblPr><w:tblW w:w="0" w:type="auto"/>{borders}</w:tblPr>'
    trs = []
    for i, row in enumerate(rows):
        cells = "".join(_tc(c, header=(i == 0)) for c in row)
        trs.append(f"<w:tr>{cells}</w:tr>")
    return f"<w:tbl>{tblpr}{''.join(trs)}</w:tbl>"


# ------------------------------------------------------------------------------ parser

def _strip_frontmatter(text: str) -> str:
    lines = text.splitlines()
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                return "\n".join(lines[i + 1:])
    return text


def _parse_blocks(md_text: str) -> List[str]:
    lines = _strip_frontmatter(md_text).splitlines()
    body: List[str] = []
    i, n = 0, len(lines)
    while i < n:
        line = lines[i]
        stripped = line.strip()

        # fenced code block
        if stripped.startswith("```"):
            i += 1
            while i < n and not lines[i].strip().startswith("```"):
                body.append(_code_line(lines[i]))
                i += 1
            i += 1  # skip closing fence
            continue

        # heading
        m = _HEADING_RE.match(line)
        if m:
            level = min(len(m.group(1)), 4)
            body.append(_para(m.group(2).strip(), style=f"Heading{level}"))
            i += 1
            continue

        # table: a row followed by a separator row
        if "|" in line and i + 1 < n and _TABLE_SEP_RE.match(lines[i + 1]) and "|" in lines[i + 1]:
            rows = [_split_row(line)]
            i += 2  # header + separator
            while i < n and "|" in lines[i] and lines[i].strip():
                rows.append(_split_row(lines[i]))
                i += 1
            body.append(_table(rows))
            continue

        # horizontal rule — drop (headings/tables already handled above)
        if _HR_RE.match(line):
            i += 1
            continue

        # blockquote (collapse consecutive > lines into one paragraph)
        m = _QUOTE_RE.match(line)
        if m:
            quote = [m.group(1)]
            i += 1
            while i < n and _QUOTE_RE.match(lines[i]):
                quote.append(_QUOTE_RE.match(lines[i]).group(1))
                i += 1
            body.append(_para(" ".join(q.strip() for q in quote), style="Quote"))
            continue

        # bullet list item
        m = _BULLET_RE.match(line)
        if m:
            body.append(_bullet(m.group(1).strip()))
            i += 1
            continue

        # blank line
        if not stripped:
            i += 1
            continue

        # plain paragraph
        body.append(_para(stripped))
        i += 1
    return body


# ------------------------------------------------------------------- document assembly

_CONTENT_TYPES = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
    '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
    '<Default Extension="xml" ContentType="application/xml"/>'
    '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
    '<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>'
    "</Types>"
)

_RELS = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
    '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
    "</Relationships>"
)

_DOC_RELS = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
    '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
    "</Relationships>"
)


def _heading_style(i: int, half_pt: int) -> str:
    return (
        f'<w:style w:type="paragraph" w:styleId="Heading{i}"><w:name w:val="heading {i}"/>'
        f'<w:basedOn w:val="Normal"/><w:next w:val="Normal"/>'
        f'<w:pPr><w:keepNext/><w:spacing w:before="240" w:after="60"/><w:outlineLvl w:val="{i - 1}"/></w:pPr>'
        f'<w:rPr><w:b/><w:color w:val="2E5496"/><w:sz w:val="{half_pt}"/></w:rPr></w:style>'
    )


_STYLES_XML = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    f'<w:styles xmlns:w="{_W}">'
    '<w:docDefaults><w:rPrDefault><w:rPr>'
    '<w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/><w:sz w:val="22"/></w:rPr></w:rPrDefault></w:docDefaults>'
    '<w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/>'
    '<w:pPr><w:spacing w:after="120"/></w:pPr></w:style>'
    + _heading_style(1, 32) + _heading_style(2, 28) + _heading_style(3, 26) + _heading_style(4, 24)
    + '<w:style w:type="paragraph" w:styleId="ListBullet"><w:name w:val="List Bullet"/>'
    '<w:basedOn w:val="Normal"/><w:pPr><w:spacing w:after="40"/></w:pPr></w:style>'
    '<w:style w:type="paragraph" w:styleId="Quote"><w:name w:val="Quote"/><w:basedOn w:val="Normal"/>'
    '<w:pPr><w:ind w:left="720"/></w:pPr><w:rPr><w:i/><w:color w:val="555555"/></w:rPr></w:style>'
    '<w:style w:type="paragraph" w:styleId="Code"><w:name w:val="Code"/><w:basedOn w:val="Normal"/>'
    '<w:pPr><w:spacing w:before="0" w:after="0"/></w:pPr>'
    '<w:rPr><w:rFonts w:ascii="Consolas" w:hAnsi="Consolas" w:cs="Consolas"/><w:sz w:val="18"/></w:rPr></w:style>'
    "</w:styles>"
)


def _document_xml(body_parts: List[str]) -> str:
    sect = (
        '<w:sectPr><w:pgSz w:w="12240" w:h="15840"/>'
        '<w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440" '
        'w:header="720" w:footer="720" w:gutter="0"/></w:sectPr>'
    )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<w:document xmlns:w="{_W}"><w:body>{"".join(body_parts)}{sect}</w:body></w:document>'
    )


def md_to_docx_bytes(md_text: str) -> bytes:
    """Convert markdown text into the bytes of a ``.docx`` (Office Open XML) file."""
    parts = {
        "[Content_Types].xml": _CONTENT_TYPES,
        "_rels/.rels": _RELS,
        "word/_rels/document.xml.rels": _DOC_RELS,
        "word/document.xml": _document_xml(_parse_blocks(md_text)),
        "word/styles.xml": _STYLES_XML,
    }
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for name, content in parts.items():
            z.writestr(name, content)
    return buf.getvalue()


def write_docx(md_text: str, out_path) -> Path:
    out = Path(out_path)
    out.write_bytes(md_to_docx_bytes(md_text))
    return out


def convert_file(md_path, out_path=None) -> Path:
    """Read a markdown file and write a sibling ``.docx`` (or ``out_path``)."""
    src = Path(md_path)
    out = Path(out_path) if out_path else src.with_suffix(".docx")
    return write_docx(src.read_text(encoding="utf-8"), out)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Convert phiweaver markdown output(s) to Word .docx.")
    ap.add_argument("markdown", nargs="+", help="markdown file(s) to convert")
    ap.add_argument("--out", help="output .docx path (single input only)")
    args = ap.parse_args(argv)
    if args.out and len(args.markdown) != 1:
        ap.error("--out is only valid with a single input file")
    for md in args.markdown:
        out = convert_file(md, args.out)
        print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
