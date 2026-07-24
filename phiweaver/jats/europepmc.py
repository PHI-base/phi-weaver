#!/usr/bin/env python3
"""
Europe PMC client — resolve an article and fetch the richest available source.

Given any one of a PMID, PMCID or DOI, this answers the question the ingest pipeline
actually needs: *what is the best source I can get for this paper, and can I get the
figures?* It then fetches it.

Why Europe PMC rather than the NCBI ID Converter:
- One call resolves any identifier **and** returns the open-access flags that decide the
  route. The converter answers only "what are the other ids", which is not the deciding
  question — a PMCID can exist for an article whose full text is not retrievable.
- Its ``supplementaryFiles`` endpoint ships the **main figure images**, not only
  supplements. That is what turns a captions-only JATS conversion into one where a
  curator (or a draft) can actually look at the panels.

There is **no separate "Europe PMC ID"** for journal articles: in a MEDLINE record the
``id`` field *is* the PMID. The real key is the composite ``source:id`` (MED, PMC, PPR
for preprints, PAT, AGR, ...), which is what :func:`article_ref` builds.

Two traps this module exists to absorb:
- ``fullTextXML`` returns **404** for a non-open-access article, even when a PMCID exists
  and Europe PMC displays the paper.
- ``supplementaryFiles`` returns **HTTP 200 with an XML errorBean body** in the same case,
  so the status code alone will happily hand you a "zip" that is an error message.

Usage:
    python3 -m phiweaver.jats.europepmc 39852455
    python3 -m phiweaver.jats.europepmc 10.3390/jof11010036 --fetch-dir ./active
"""

import argparse
import io
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path

REST_BASE = "https://www.ebi.ac.uk/europepmc/webservices/rest"
ANNOTATIONS_BASE = "https://www.ebi.ac.uk/europepmc/annotations_api"
USER_AGENT = "phiweaver (PHI-base biocuration toolkit; phi-base@rothamsted.ac.uk)"
TIMEOUT = 30.0

# Routes the ingest pipeline can take, best first.
ROUTE_JATS = "jats"            # open access: full text XML (+ figure images)
ROUTE_PDF = "pdf"              # not OA, but a PDF exists locally or at the publisher
ROUTE_ABSTRACT = "abstract"    # metadata/abstract only — needs manual sourcing

PMID_RE = re.compile(r"^\d{1,8}$")
PMCID_RE = re.compile(r"^PMC\d+$", re.IGNORECASE)
DOI_RE = re.compile(r"^10\.\d{4,9}/\S+$")


class EuropePMCError(RuntimeError):
    """Raised only for programming errors (bad identifier); network issues degrade."""


# ------------------------------------------------------------------ HTTP plumbing

def _get(url, timeout=TIMEOUT):
    """GET a URL. Returns (status, body_bytes, content_type); (0, b'', '') on failure."""
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as resp:
            return resp.status, resp.read(), resp.headers.get("Content-Type", "")
    except urllib.error.HTTPError as e:
        return e.code, b"", ""
    except (urllib.error.URLError, OSError, TimeoutError):
        return 0, b"", ""


def _is_error_bean(body: bytes) -> bool:
    """Europe PMC signals 'not open access' with a 200 + <errorBean> XML body.

    Without this check a caller sees HTTP 200 and treats an error message as content.
    """
    return body[:200].lstrip().startswith(b"<?xml") and b"<errorBean>" in body[:400]


def classify_identifier(identifier: str) -> str:
    """Return 'pmid' | 'pmcid' | 'doi' for a bare identifier."""
    value = (identifier or "").strip()
    if PMCID_RE.match(value):
        return "pmcid"
    if PMID_RE.match(value):
        return "pmid"
    if DOI_RE.match(value) or value.lower().startswith("doi:"):
        return "doi"
    raise EuropePMCError(
        f"unrecognised identifier {identifier!r} — expected a PMID (digits), "
        f"a PMCID (PMC…) or a DOI (10.…/…)")


def _query_for(identifier: str) -> str:
    kind = classify_identifier(identifier)
    value = identifier.strip()
    if kind == "pmid":
        return f"EXT_ID:{value}"
    if kind == "pmcid":
        return f"PMCID:{value.upper()}"
    return "DOI:{}".format(re.sub(r"^doi:", "", value, flags=re.IGNORECASE))


# --------------------------------------------------------------------- resolution

def resolve(identifier: str, timeout=TIMEOUT) -> dict:
    """Resolve any identifier to a Europe PMC record.

    Returns a dict with ``found``/``error`` always present. Network failure yields
    ``found: False`` with an error string — never an exception, because ingest must be
    able to fall back to a local PDF.
    """
    query = _query_for(identifier)
    url = "{}/search?{}".format(REST_BASE, urllib.parse.urlencode({
        "query": query, "resultType": "core", "format": "json", "pageSize": 5,
    }))
    status, body, _ = _get(url, timeout)
    if status != 200 or not body:
        return {"found": False, "query": query,
                "error": f"Europe PMC search failed (HTTP {status or 'no response'})"}

    try:
        payload = json.loads(body.decode("utf-8"))
    except ValueError as e:
        return {"found": False, "query": query, "error": f"unparseable response: {e}"}

    results = payload.get("resultList", {}).get("result", [])
    hit_count = payload.get("hitCount", 0)
    if not results:
        return {"found": False, "query": query, "hit_count": 0,
                "error": f"no Europe PMC record for {identifier}"}

    record = _record_from(results[0])
    record.update({
        "found": True, "query": query, "hit_count": hit_count,
        # More than one hit means the identifier was not unique; the caller must not
        # silently accept the first row as if it were definitive.
        "ambiguous": hit_count > 1,
        "other_hits": [article_ref(r) for r in results[1:]] if hit_count > 1 else [],
        "error": "",
    })
    return record


def _record_from(result: dict) -> dict:
    yes = lambda key: str(result.get(key, "")).upper() == "Y"
    return {
        "id": result.get("id", ""),
        "source": result.get("source", ""),
        "pmid": result.get("pmid", ""),
        "pmcid": result.get("pmcid", ""),
        "doi": result.get("doi", ""),
        "title": re.sub(r"<[^>]+>", "", result.get("title", "") or ""),
        "journal": (result.get("journalInfo", {}) or {}).get("journal", {}).get("title", ""),
        "year": result.get("pubYear", ""),
        "is_open_access": yes("isOpenAccess"),
        "in_epmc": yes("inEPMC"),
        "in_pmc": yes("inPMC"),
        "has_pdf": yes("hasPDF"),
        "has_supplementary": yes("hasSuppl"),
        "has_text_mined_terms": yes("hasTextMinedTerms"),
        "is_preprint": result.get("source", "") == "PPR",
        "license": result.get("license", ""),
    }


def article_ref(record: dict) -> str:
    """The composite Europe PMC key, e.g. ``MED:39852455``. Not a separate 'EPMC id'."""
    source = record.get("source", "") or "MED"
    return f"{source}:{record.get('id', '')}"


def route_for(record: dict) -> str:
    """Decide the ingest route.

    The gate is **open access**, not 'a PMCID exists' — Europe PMC returns 404 for the
    full text of a non-OA article that nonetheless has a PMCID and is viewable on site.
    """
    if not record.get("found"):
        return ROUTE_PDF
    if record.get("is_open_access") and record.get("pmcid"):
        return ROUTE_JATS
    if record.get("has_pdf"):
        return ROUTE_PDF
    return ROUTE_ABSTRACT


# ------------------------------------------------------------------------ fetching

def fetch_full_text(pmcid: str, timeout=TIMEOUT) -> bytes:
    """Fetch JATS full text XML. Returns b'' when not open access (HTTP 404)."""
    if not pmcid:
        return b""
    status, body, _ = _get(f"{REST_BASE}/{pmcid.upper()}/fullTextXML", timeout)
    if status != 200 or not body or _is_error_bean(body):
        return b""
    return body


def fetch_supplementary(pmcid: str, timeout=TIMEOUT) -> bytes:
    """Fetch the supplementary/figure ZIP. Returns b'' when unavailable.

    Despite the endpoint name this carries the article's **main figure images** as well
    as true supplements — the reason this whole route beats a captions-only conversion.
    """
    if not pmcid:
        return b""
    status, body, _ = _get(f"{REST_BASE}/{pmcid.upper()}/supplementaryFiles", timeout)
    # HTTP 200 + <errorBean> is how "not open access" arrives here.
    if status != 200 or not body or _is_error_bean(body):
        return b""
    if not body[:4].startswith(b"PK"):  # not a zip
        return b""
    return body


def extract_media(zip_bytes: bytes, dest_dir, keep_nested_zips=True) -> dict:
    """Unpack the supplementary ZIP into ``dest_dir``.

    Splits what came back into figure images (which let a curator read the panels) and
    other supplementary payloads (kept, but reported separately).
    """
    dest = Path(dest_dir)
    dest.mkdir(parents=True, exist_ok=True)
    images, others = [], []
    if not zip_bytes:
        return {"images": images, "others": others, "dir": str(dest)}

    image_exts = {".jpg", ".jpeg", ".png", ".gif", ".tif", ".tiff", ".svg", ".webp"}
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as archive:
        for name in archive.namelist():
            if name.endswith("/"):
                continue
            # Flatten: never trust archive paths to stay inside the destination.
            target = dest / Path(name).name
            suffix = target.suffix.lower()
            if suffix not in image_exts and suffix == ".zip" and not keep_nested_zips:
                continue
            with archive.open(name) as src, open(target, "wb") as out:
                out.write(src.read())
            (images if suffix in image_exts else others).append(target.name)

    return {"images": sorted(images), "others": sorted(others), "dir": str(dest)}


def fetch_annotations(article_reference: str, timeout=TIMEOUT) -> list:
    """Fetch Europe PMC text-mined annotations.

    **Triage aid only.** These are machine-generated and demonstrably wrong often enough
    to matter: on PMID:39852455 the host "mice" maps to taxid 10095 (*Mus sp.*) rather
    than 10090 (*Mus musculus*), and "guanine nucleotide exchange factor" maps to
    UniProt P0CF32 (SDC25_YEASX, *S. cerevisiae*) rather than the article's own Q4WWM8
    (SEC2_ASPFU, *A. fumigatus*). Use them to widen a candidate list; never as evidence,
    and never straight into a curation's ``canto`` block. Verify with
    ``phiweaver.lookup.query_uniprot`` / ``validate_ontology_ids`` first.
    """
    url = "{}/annotationsByArticleIds?{}".format(ANNOTATIONS_BASE, urllib.parse.urlencode({
        "articleIds": article_reference, "format": "JSON",
    }))
    status, body, _ = _get(url, timeout)
    if status != 200 or not body:
        return []
    try:
        payload = json.loads(body.decode("utf-8"))
    except ValueError:
        return []
    if not payload:
        return []
    return payload[0].get("annotations", [])


# ------------------------------------------------------------------- orchestration

def acquire(identifier, dest_dir, fetch_media=True, media_dir=None, timeout=TIMEOUT):
    """Resolve an identifier and fetch the best available source into ``dest_dir``.

    Returns a manifest describing what was decided and what landed on disk. A failure to
    reach Europe PMC is reported, not raised: the caller falls back to a local PDF.
    """
    dest = Path(dest_dir)
    record = resolve(identifier, timeout=timeout)
    route = route_for(record)
    manifest = {
        "identifier": identifier,
        "record": record,
        "article_ref": article_ref(record) if record.get("found") else "",
        "route": route,
        "xml_path": "",
        "media": {"images": [], "others": [], "dir": ""},
        "notes": [],
    }

    if not record.get("found"):
        manifest["notes"].append(
            f"{record.get('error', 'not found')} — fall back to a local PDF.")
        return manifest

    if record.get("ambiguous"):
        manifest["notes"].append(
            f"identifier matched {record['hit_count']} Europe PMC records "
            f"({', '.join(record['other_hits'])} also matched); using the first — verify.")

    if record.get("is_preprint"):
        manifest["notes"].append(
            "source is PPR (preprint) — not peer reviewed; a curation-scope decision.")

    if route != ROUTE_JATS:
        reason = ("not open access" if not record.get("is_open_access")
                  else "no PMCID")
        manifest["notes"].append(
            f"full text XML unavailable ({reason}); route = {route}. "
            f"Convert the PDF instead and record that figures/supplement were not obtained.")
        return manifest

    xml = fetch_full_text(record["pmcid"], timeout=timeout)
    if not xml:
        manifest["route"] = ROUTE_PDF
        manifest["notes"].append(
            "flagged open access but fullTextXML did not return content — "
            "fall back to the PDF.")
        return manifest

    dest.mkdir(parents=True, exist_ok=True)
    stem = record["pmcid"].upper()
    xml_path = dest / f"{stem}.xml"
    xml_path.write_bytes(xml)
    manifest["xml_path"] = str(xml_path)
    manifest["notes"].append(
        "full text is the PMC-normalised JATS Archiving tagset, not the publisher's "
        "Publishing tagset — same content, slightly different markup.")

    if fetch_media:
        target = Path(media_dir) if media_dir else dest / "03-Media" / stem
        blob = fetch_supplementary(record["pmcid"], timeout=timeout)
        if blob:
            manifest["media"] = extract_media(blob, target)
            manifest["notes"].append(
                f"{len(manifest['media']['images'])} figure image(s) retrieved — "
                f"figure panels are readable, not captions-only.")
        elif record.get("has_supplementary"):
            manifest["notes"].append(
                "record claims supplementary files but the ZIP was not retrievable.")

    return manifest


# ---------------------------------------------------------------------------- CLI

def _print_manifest(manifest, as_json=False):
    if as_json:
        print(json.dumps(manifest, indent=2))
        return

    record = manifest["record"]
    if not record.get("found"):
        print(f"❌ {record.get('error')}")
        print(f"   route: {manifest['route']}")
        return

    print(f"✅ {manifest['article_ref']}  ({record['source']})")
    print(f"   title:   {record['title'][:78]}")
    print(f"   ids:     PMID:{record['pmid'] or '-'}  {record['pmcid'] or '-'}  "
          f"DOI:{record['doi'] or '-'}")
    print(f"   access:  open_access={record['is_open_access']}  in_epmc={record['in_epmc']}  "
          f"has_pdf={record['has_pdf']}  license={record['license'] or '-'}")
    print(f"   route:   {manifest['route']}")
    if manifest["xml_path"]:
        print(f"   xml:     {manifest['xml_path']}")
    media = manifest["media"]
    if media["images"] or media["others"]:
        print(f"   media:   {len(media['images'])} images, {len(media['others'])} other "
              f"→ {media['dir']}")
    for note in manifest["notes"]:
        print(f"   • {note}")


def main():
    parser = argparse.ArgumentParser(
        description="Europe PMC: resolve an article and fetch the richest available source.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 -m phiweaver.jats.europepmc 39852455
  python3 -m phiweaver.jats.europepmc PMC11767236 --fetch-dir ./active
  python3 -m phiweaver.jats.europepmc 10.3390/jof11010036 --json
        """)
    parser.add_argument('identifier', help='PMID, PMCID or DOI')
    parser.add_argument('--fetch-dir', default='',
                        help='download the full text (and figures) into this directory')
    parser.add_argument('--media-dir', default='',
                        help='override where figure images are unpacked')
    parser.add_argument('--no-media', action='store_true',
                        help='resolve and fetch XML but skip the figure/supplement ZIP')
    parser.add_argument('--annotations', action='store_true',
                        help='also print text-mined entity counts (TRIAGE AID ONLY — unverified)')
    parser.add_argument('--json', action='store_true', help='emit the manifest as JSON')
    args = parser.parse_args()

    try:
        if args.fetch_dir:
            manifest = acquire(args.identifier, args.fetch_dir,
                               fetch_media=not args.no_media,
                               media_dir=args.media_dir or None)
        else:
            record = resolve(args.identifier)
            manifest = {
                "identifier": args.identifier, "record": record,
                "article_ref": article_ref(record) if record.get("found") else "",
                "route": route_for(record), "xml_path": "",
                "media": {"images": [], "others": [], "dir": ""},
                "notes": ["resolve-only (pass --fetch-dir to download)"],
            }
    except EuropePMCError as e:
        print(f"❌ {e}")
        sys.exit(2)

    _print_manifest(manifest, as_json=args.json)

    if args.annotations and manifest["article_ref"]:
        annotations = fetch_annotations(manifest["article_ref"])
        from collections import Counter
        counts = Counter(a.get("type", "?") for a in annotations)
        print(f"\n⚠️  {len(annotations)} text-mined annotations "
              f"(UNVERIFIED — triage aid only, never evidence):")
        for kind, n in counts.most_common():
            print(f"   {n:>5}  {kind}")

    sys.exit(0 if manifest["record"].get("found") else 1)


if __name__ == "__main__":
    main()
