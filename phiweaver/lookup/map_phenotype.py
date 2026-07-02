#!/usr/bin/env python3
"""
map_phenotype.py — deterministic phenotype-phrase → PHIPO term search for PHI-Weaver.

Given a phenotype description (typically a phrase a curator lifted from a paper's figure
caption or results text), search the Pathogen–Host Interaction Phenotype Ontology (PHIPO)
via the EBI Ontology Lookup Service and return the candidate terms that actually exist —
with their real PHIPO IDs and labels. It NEVER invents an ID: a phrase with no PHIPO hit
is reported as "no_match", not mapped to a guessed term.

This is the deterministic half of the caption → phenotype → PHIPO workflow (see the
phipo-mapping skill). Deciding which phrases in a caption *are* phenotypes is a reasoning
step done by the curator/agent; this tool maps a given phrase to real candidate terms, and
the companion validate_ontology_ids.py confirms the chosen ID is current.

Design rules (see AGENTS.md, phipo-mapping / curation-qc skills):
- Never guess: only real OLS results are returned; "no_match" is explicit, never a
  fabricated ID. PHIPO search also surfaces imported terms from other ontologies (e.g.
  PATO); only PHIPO: IDs are kept.
- Obsolete terms are excluded (curation requires current terms).
- Record provenance: source service, cache hit/miss, UTC timestamp.
- The exit code reflects whether the *search ran*, not whether it found a match: 0 unless a
  query errored (a clean "no_match" is exit 0). The per-query `status` carries the result.

CLI:
    python3 -m phiweaver.lookup.map_phenotype "reduced virulence"
    python3 -m phiweaver.lookup.map_phenotype --file phenotype-phrases.txt --json
    python3 -m phiweaver.lookup.map_phenotype "abnormal conidiation" --rows 10

The HTTP getter is injectable (``PhenotypeMapper(http_get=...)``), so this imports and
tests cleanly without ``requests`` installed and without touching the network.
"""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable, List, Optional

from phiweaver.common import ResponseCache, make_getter, utc_now

OLS_SEARCH_URL = "https://www.ebi.ac.uk/ols4/api/search"
PHIPO_ONTOLOGY = "phipo"
PHIPO_PREFIX = "PHIPO:"
USER_AGENT = "PHI-Weaver-map-phenotype/1.0 (https://github.com/PHI-base/phi-weaver)"
DEFAULT_CACHE = Path(__file__).resolve().parent / ".cache" / "phenotype_cache.sqlite"
DEFAULT_ROWS = 5


class PhenotypeSearchError(RuntimeError):
    """Raised when an OLS search request fails."""


@dataclass
class Candidate:
    obo_id: str
    label: Optional[str]
    exact: bool          # phrase equals the term's label or an exact synonym


@dataclass
class PhenotypeMapping:
    query: str
    status: str                       # matched | no_match | error
    candidates: List[Candidate]
    source: Optional[str]
    from_cache: bool
    retrieved_at: Optional[str]
    error: Optional[str] = None

    @property
    def ok(self) -> bool:
        """The search completed without error. A clean 'no_match' is not a failure —
        never-guess means an honest empty result is success, not an error."""
        return self.status in ("matched", "no_match")

    def to_dict(self) -> dict:
        d = asdict(self)                 # nested Candidate dataclasses become dicts too
        d["ok"] = self.ok
        return d


_requests_get = make_getter(USER_AGENT)


class PhenotypeMapper:
    def __init__(self, cache: Optional[ResponseCache] = None,
                 http_get: Optional[Callable] = None):
        self.cache = cache
        self._http_get = http_get or _requests_get

    def _get(self, params: dict, use_cache: bool):
        key = OLS_SEARCH_URL + "?" + json.dumps(params, sort_keys=True)
        if use_cache and self.cache:
            hit = self.cache.get(key)
            if hit:
                return hit["payload"], True
        status, body, _headers = self._http_get(OLS_SEARCH_URL, params)
        if status != 200 or body is None:
            raise PhenotypeSearchError(
                f"OLS search failed (HTTP {status}) for {params.get('q')!r}")
        if use_cache and self.cache:
            self.cache.put(key, body)
        return body, False

    def map(self, phrase: str, rows: int = DEFAULT_ROWS, use_cache: bool = True
            ) -> PhenotypeMapping:
        phrase = phrase.strip()
        if not phrase:
            return PhenotypeMapping(phrase, "no_match", [], None, False, None,
                                    "empty query")
        params = {"q": phrase, "ontology": PHIPO_ONTOLOGY, "rows": rows}
        try:
            body, cached = self._get(params, use_cache)
        except PhenotypeSearchError as exc:
            return PhenotypeMapping(phrase, "error", [], OLS_SEARCH_URL, False,
                                    utc_now(), str(exc))
        candidates = _extract_candidates(body, phrase, rows)
        status = "matched" if candidates else "no_match"
        return PhenotypeMapping(phrase, status, candidates, OLS_SEARCH_URL, cached,
                                utc_now())


def _extract_candidates(body: dict, phrase: str, rows: int) -> List[Candidate]:
    """Pull PHIPO candidate terms from an OLS search response, exact matches first."""
    docs = ((body or {}).get("response") or {}).get("docs") or []
    q = phrase.strip().lower()
    out: List[Candidate] = []
    for d in docs:
        obo = d.get("obo_id")
        if not obo or not obo.upper().startswith(PHIPO_PREFIX):
            continue                      # keep PHIPO terms only (drop imported PATO/etc.)
        if d.get("is_obsolete"):
            continue                      # never suggest an obsolete term
        label = d.get("label")
        synonyms = [s.strip().lower() for s in (d.get("exact_synonyms") or [])]
        exact = (label or "").strip().lower() == q or q in synonyms
        out.append(Candidate(obo_id=obo, label=label, exact=exact))
    out.sort(key=lambda c: not c.exact)   # stable: exact first, else OLS relevance order
    return out[:rows]


def read_phrases(path: str) -> List[str]:
    """Read one phenotype phrase per line; skip blank lines and ``#`` comments."""
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    return [ln.strip() for ln in lines if ln.strip() and not ln.strip().startswith("#")]


def format_human(results: List[PhenotypeMapping]) -> str:
    lines: List[str] = []
    for r in results:
        if r.status == "error":
            lines.append(f"⚠️  {r.query}  [error]")
            if r.error:
                lines.append(f"    {r.error}")
            continue
        if r.status == "no_match":
            lines.append(f"❌ {r.query}  [no PHIPO match]")
            continue
        prov = f"({'cached' if r.from_cache else 'live'} via OLS)"
        lines.append(f"✅ {r.query}  {prov}")
        for c in r.candidates:
            mark = "★" if c.exact else "•"
            lines.append(f"    {mark} {c.obo_id}  {c.label or ''}")
    matched = sum(1 for r in results if r.status == "matched")
    lines.append("")
    lines.append(f"{matched}/{len(results)} phrase(s) matched at least one PHIPO term. "
                 "Suggestions only — a curator confirms the term; verify the chosen ID "
                 "with `python3 -m phiweaver.lookup.validate_ontology_ids`.")
    return "\n".join(lines)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(
        description="Map phenotype phrases to candidate PHIPO terms via the EBI OLS. "
                    "Never invents IDs; unmatched phrases are reported as no_match.")
    p.add_argument("phrases", nargs="*",
                   help='phenotype description(s), e.g. "reduced virulence"')
    p.add_argument("--file", help="read one phenotype phrase per line from a file")
    p.add_argument("--rows", type=int, default=DEFAULT_ROWS,
                   help=f"max candidate terms per phrase (default {DEFAULT_ROWS})")
    p.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    p.add_argument("--no-cache", action="store_true", help="bypass the local cache")
    p.add_argument("--cache", default=os.environ.get("PHENOTYPE_CACHE", str(DEFAULT_CACHE)),
                   help="cache file path (or set PHENOTYPE_CACHE)")
    args = p.parse_args(argv)

    phrases: List[str] = list(args.phrases)
    if args.file:
        try:
            phrases.extend(read_phrases(args.file))
        except OSError as exc:
            p.error(f"cannot read --file: {exc}")
    if not phrases:
        p.error("provide one or more phenotype phrases, or --file")

    cache = None if args.no_cache else ResponseCache(args.cache)
    mapper = PhenotypeMapper(cache=cache)
    results = [mapper.map(ph, rows=args.rows, use_cache=not args.no_cache)
               for ph in phrases]
    if cache:
        cache.close()

    if args.json:
        print(json.dumps([r.to_dict() for r in results], indent=2))
    else:
        print(format_human(results))
    # Exit reflects whether the search ran, not whether it matched: only errors fail.
    return 0 if all(r.ok for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
