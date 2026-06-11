#!/usr/bin/env python3
"""
query_uniprot.py — deterministic UniProtKB lookups for PHI-Weaver curation.

Resolves a gene / locus tag / accession (optionally scoped to an organism) to a
UniProtKB accession and an evidence-backed function, via the UniProt REST API
(https://rest.uniprot.org). Responses are cached locally and stamped with the UniProt
release for reproducibility / provenance.

Design rules (see AGENTS.md):
- Never guess: if a search returns multiple entries, ALL candidates are returned and the
  status is "ambiguous" — a curator decides. A miss returns "not_found", never an
  invented accession.
- Prefer reviewed (Swiss-Prot) entries; flag unreviewed (TrEMBL) as lower confidence.
- Record provenance: the query, the UniProt release, and the retrieval timestamp.

CLI:
    python3 scripts/query_uniprot.py --gene FgTPP1 --organism 5518
    python3 scripts/query_uniprot.py --accession P12345 --json
    python3 scripts/query_uniprot.py --locus-tag FGSG_11164 --organism 5518

The HTTP getter is injectable (`UniProtClient(http_get=...)`), so the module imports and
tests cleanly without `requests` installed and without touching the network.
"""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, List, Optional

BASE_URL = "https://rest.uniprot.org"
DEFAULT_FIELDS = (
    "accession,id,protein_name,gene_names,organism_name,organism_id,reviewed,cc_function"
)
USER_AGENT = "PHI-Weaver-query-uniprot/1.0 (https://github.com/PHI-base/phi-weaver)"
DEFAULT_CACHE = Path(__file__).resolve().parent / ".cache" / "uniprot_cache.sqlite"
# ECO codes that denote experimental support (used to label function evidence).
EXPERIMENTAL_ECO = {"ECO:0000269", "ECO:0000314", "ECO:0000315", "ECO:0000353"}


class UniProtError(RuntimeError):
    """Raised when a UniProt request fails."""


@dataclass
class Candidate:
    accession: str
    entry_name: str
    protein_name: str
    gene_names: List[str]
    organism: str
    organism_id: Optional[int]
    reviewed: bool
    function: str
    function_has_experimental_evidence: bool


@dataclass
class LookupResult:
    query: dict
    status: str  # found | ambiguous | not_found | error
    candidates: List[dict]
    uniprot_release: Optional[str]
    retrieved_at: str
    from_cache: bool
    error: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# --------------------------------------------------------------------------- HTTP

def _requests_get(url: str, params: dict):
    """Default HTTP getter. Returns (status_code, json_or_None, headers_dict).

    `requests` is imported lazily so the module loads/tests without it.
    """
    import requests

    resp = requests.get(
        url,
        params=params,
        timeout=30,
        headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
    )
    try:
        body = resp.json()
    except ValueError:
        body = None
    return resp.status_code, body, dict(resp.headers)


# -------------------------------------------------------------------------- Cache

class Cache:
    """Tiny SQLite cache of raw UniProt JSON responses, keyed by request signature."""

    def __init__(self, path=DEFAULT_CACHE):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(self.path))
        self._conn.execute(
            "CREATE TABLE IF NOT EXISTS responses ("
            " key TEXT PRIMARY KEY, payload TEXT NOT NULL, release TEXT, cached_at TEXT)"
        )
        self._conn.commit()

    def get(self, key: str):
        row = self._conn.execute(
            "SELECT payload, release, cached_at FROM responses WHERE key = ?", (key,)
        ).fetchone()
        if not row:
            return None
        return {"payload": json.loads(row[0]), "release": row[1], "cached_at": row[2]}

    def put(self, key: str, payload: dict, release: Optional[str]):
        self._conn.execute(
            "INSERT OR REPLACE INTO responses (key, payload, release, cached_at)"
            " VALUES (?, ?, ?, ?)",
            (key, json.dumps(payload), release, _now()),
        )
        self._conn.commit()

    def close(self):
        self._conn.close()


# ------------------------------------------------------------------------- Client

class UniProtClient:
    def __init__(self, cache: Optional[Cache] = None, http_get: Optional[Callable] = None):
        self.cache = cache
        self._http_get = http_get or _requests_get

    def _get(self, url: str, params: dict, use_cache: bool):
        key = url + "?" + json.dumps(params, sort_keys=True)
        if use_cache and self.cache:
            hit = self.cache.get(key)
            if hit:
                return hit["payload"], hit["release"], True
        status, body, headers = self._http_get(url, params)
        if status != 200 or body is None:
            raise UniProtError(f"UniProt request failed (HTTP {status}) for {url}")
        release = headers.get("x-uniprot-release") or headers.get("X-UniProt-Release")
        if use_cache and self.cache:
            self.cache.put(key, body, release)
        return body, release, False

    def lookup(self, gene=None, locus_tag=None, organism_id=None, accession=None,
               use_cache=True) -> LookupResult:
        query_meta = {
            "gene": gene, "locus_tag": locus_tag,
            "organism_id": organism_id, "accession": accession,
        }
        try:
            if accession:
                body, release, cached = self._get(
                    f"{BASE_URL}/uniprotkb/{accession}.json", {}, use_cache)
                entries = [body] if body else []
            else:
                q = _build_query(gene, locus_tag, organism_id)
                if not q:
                    return LookupResult(query_meta, "error", [], None, _now(), False,
                                        "no gene / locus_tag / accession provided")
                body, release, cached = self._get(
                    f"{BASE_URL}/uniprotkb/search",
                    {"query": q, "fields": DEFAULT_FIELDS, "format": "json", "size": 25},
                    use_cache)
                entries = body.get("results", []) if body else []
        except UniProtError as exc:
            return LookupResult(query_meta, "error", [], None, _now(), False, str(exc))

        candidates = [_parse_entry(e) for e in entries]
        candidates.sort(key=lambda c: (not c.reviewed,))  # reviewed first
        if not candidates:
            status = "not_found"
        elif len(candidates) == 1:
            status = "found"
        else:
            status = "ambiguous"
        return LookupResult(
            query_meta, status, [asdict(c) for c in candidates],
            release, _now(), cached)


# ----------------------------------------------------------------------- Parsing

def _build_query(gene, locus_tag, organism_id) -> str:
    parts = []
    if gene:
        parts.append(f"gene:{gene}")
    if locus_tag:
        # Locus tags / ORF names are indexed under the gene field in UniProt.
        parts.append(f"gene:{locus_tag}")
    if not parts:
        return ""
    q = "(" + " OR ".join(parts) + ")"
    if organism_id:
        q += f" AND organism_id:{organism_id}"
    return q


def _parse_entry(e: dict) -> Candidate:
    acc = e.get("primaryAccession", "")
    entry_name = e.get("uniProtkbId", "")

    pd = e.get("proteinDescription", {}) or {}
    rec = pd.get("recommendedName") or {}
    protein_name = (rec.get("fullName") or {}).get("value", "")
    if not protein_name:
        subs = pd.get("submissionNames") or []
        if subs:
            protein_name = (subs[0].get("fullName") or {}).get("value", "")

    gene_names: List[str] = []
    for g in e.get("genes", []) or []:
        gn = g.get("geneName")
        if gn and gn.get("value"):
            gene_names.append(gn["value"])
        for key in ("orderedLocusNames", "orfNames", "synonyms"):
            for item in g.get(key, []) or []:
                if item.get("value"):
                    gene_names.append(item["value"])

    org = e.get("organism", {}) or {}
    organism = org.get("scientificName", "")
    organism_id = org.get("taxonId")

    et = (e.get("entryType", "") or "").lower()
    reviewed = ("reviewed" in et) and ("unreviewed" not in et)

    function, has_exp = _extract_function(e.get("comments", []) or [])
    return Candidate(acc, entry_name, protein_name, gene_names, organism,
                     organism_id, reviewed, function, has_exp)


def _extract_function(comments):
    for c in comments:
        if c.get("commentType") == "FUNCTION":
            texts = c.get("texts", []) or []
            if texts:
                value = texts[0].get("value", "")
                evidences = texts[0].get("evidences", []) or []
                has_exp = any(
                    ev.get("evidenceCode") in EXPERIMENTAL_ECO for ev in evidences)
                return value, has_exp
    return "", False


# --------------------------------------------------------------------------- CLI

def format_human(result: LookupResult) -> str:
    lines = [
        f"Query  : {result.query}",
        f"Status : {result.status}  "
        f"(UniProt release {result.uniprot_release or 'n/a'}, "
        f"{'cached' if result.from_cache else 'live'}, at {result.retrieved_at})",
    ]
    if result.error:
        lines.append(f"Error  : {result.error}")
    for i, c in enumerate(result.candidates, 1):
        rev = "reviewed (Swiss-Prot)" if c["reviewed"] \
            else "UNREVIEWED (TrEMBL — lower confidence)"
        ev = "experimental" if c["function_has_experimental_evidence"] \
            else "non-experimental / inferred"
        lines += [
            f"  [{i}] {c['accession']}  {c['protein_name']}  [{rev}]",
            f"      gene/locus: {', '.join(c['gene_names']) or '—'}",
            f"      organism : {c['organism']} (taxon {c['organism_id']})",
            f"      function : {c['function'] or '—'}",
            f"      evidence : {ev}",
        ]
    if result.status == "ambiguous":
        lines.append("  ⚠️  Multiple candidates — a curator must choose; not auto-resolved.")
    elif result.status == "not_found":
        lines.append("  No match found. Do not invent an accession.")
    return "\n".join(lines)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(
        description="Deterministic UniProtKB lookup for PHI-Weaver curation.")
    p.add_argument("--gene")
    p.add_argument("--locus-tag", dest="locus_tag")
    p.add_argument("--organism", dest="organism_id", type=int,
                   help="NCBI taxonomy id (e.g. 5518 for Fusarium graminearum)")
    p.add_argument("--accession")
    p.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    p.add_argument("--no-cache", action="store_true", help="bypass the local cache")
    p.add_argument("--cache", default=os.environ.get("UNIPROT_CACHE", str(DEFAULT_CACHE)),
                   help="cache file path (or set UNIPROT_CACHE)")
    args = p.parse_args(argv)

    if not (args.gene or args.locus_tag or args.accession):
        p.error("provide at least one of --gene / --locus-tag / --accession")

    cache = None if args.no_cache else Cache(args.cache)
    client = UniProtClient(cache=cache)
    result = client.lookup(
        gene=args.gene, locus_tag=args.locus_tag,
        organism_id=args.organism_id, accession=args.accession,
        use_cache=not args.no_cache)
    print(json.dumps(result.to_dict(), indent=2) if args.json else format_human(result))
    if cache:
        cache.close()
    return 0 if result.status in ("found", "ambiguous") else 1


if __name__ == "__main__":
    raise SystemExit(main())
