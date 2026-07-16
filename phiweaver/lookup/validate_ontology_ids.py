#!/usr/bin/env python3
"""
validate_ontology_ids.py — deterministic ontology-ID validation for PHI-Weaver curation.

Checks the identifiers a curation depends on — PHIPO, GO, PHIDO, MOD (PSI-MOD),
BTO (BRENDA tissue, for the host-tissue extension), PECO (PHI-ECO experimental
conditions) and UniProtKB — in two stages:

  1. FORMAT (offline, always): does the ID match the official syntax for its prefix?
     Catches typos and invented IDs without touching the network. (OBO terms use a
     7-digit local id; MOD/PSI-MOD uses a 5-digit local id.)
  2. EXISTENCE / OBSOLESCENCE: does the term actually exist in the ontology, and is it
     current (not obsolete)?
       - GO, PHIPO, MOD and BTO resolve **online** via the EBI Ontology Lookup Service REST
         API (https://www.ebi.ac.uk/ols4/api). Responses are cached and stamped with a
         retrieval timestamp for provenance.
       - PHIDO, PECO (PHI-ECO), PHIPO_EXT and FYPO_EXT are **not hosted by OLS4**, so each
         resolves **offline** against a bundled copy of the ontology (`data/phido.obo`,
         `data/phi-eco.obo`, `data/phipo_ext.obo`, `data/fypo_extension.obo`; vendored from
         github.com/PHI-base/{phido,phi-eco,phipo_ext} and PHI-base/canto). This closes a
         false-negative gap where every such ID used to return not_found. NB the OLS ontology
         named "peco" is the unrelated Planteome ontology — PHI-base PECO terms are only in the
         bundled file. PHIPO_EXT is a *separate* PHI-base ontology of extension-only terms
         (gene-for-gene interaction values); it is NOT part of PHIPO (PHIPO obsoleted its old
         gene-for-gene term and moved these into PHIPO_EXT). FYPO_EXT is a small PomBase extension
         ontology holding the penetrance/severity values (high/medium/low/complete).

UniProtKB accessions are format-checked here; their *existence* is resolved by the
companion `query_uniprot.py` (which also returns the protein function), so this script
marks them "format-checked only" rather than duplicating that lookup.

Design rules (see AGENTS.md, and the curation-qc / phipo-mapping skills):
- Never guess. A bad-format ID is reported, never "corrected". A term the ontology does
  not return is "not_found", never assumed valid.
- Obsolete terms FAIL: the skills require non-obsolete terms only.
- Record provenance: the source service, whether the answer came from cache, and a UTC
  timestamp.

CLI:
    python3 scripts/validate_ontology_ids.py PHIPO:0000001 GO:0009405
    python3 scripts/validate_ontology_ids.py --format-only UniProtKB:P12345
    python3 scripts/validate_ontology_ids.py --file draft-curation.md --json

The HTTP getter is injectable (`OntologyValidator(http_get=...)`), so the module imports
and tests cleanly without `requests` installed and without touching the network.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import asdict, dataclass
from functools import lru_cache
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

from phiweaver.common import ResponseCache, make_getter, utc_now

OLS_BASE_URL = "https://www.ebi.ac.uk/ols4/api"
USER_AGENT = "PHI-Weaver-validate-ontology-ids/1.0 (https://github.com/PHI-base/phi-weaver)"
DEFAULT_CACHE = Path(__file__).resolve().parent / ".cache" / "ontology_cache.sqlite"

# Ontology-term prefixes we recognise (as opposed to UniProtKB accessions).
OBO_PREFIXES = {"PHIPO", "PHIPO_EXT", "GO", "PHIDO", "MOD", "BTO", "PECO", "FYPO_EXT"}
# The subset we verify online, mapped to their OLS ontology name. PHIDO and PECO are absent
# on purpose: OLS4 hosts neither, so they resolve offline against a bundled .obo.
# (PECO here = the PHI-base experimental-conditions ontology / PHI-ECO — NOT the Planteome
# "peco" on OLS, a different ontology that happens to share the prefix.) MOD is PSI-MOD;
# BTO is the BRENDA Tissue Ontology, used for the host-tissue (infects_tissue) extension.
OLS_ONTOLOGY = {"PHIPO": "phipo", "GO": "go", "MOD": "mod", "BTO": "bto"}

# Bundled offline ontologies (vendored from PHI-base repos — see data/README.md).
PHIDO_OBO_PATH = Path(__file__).resolve().parent / "data" / "phido.obo"
PHIDO_SOURCE = "bundled phido.obo"
PHI_ECO_OBO_PATH = Path(__file__).resolve().parent / "data" / "phi-eco.obo"
PHI_ECO_SOURCE = "bundled phi-eco.obo"
PHIPO_EXT_OBO_PATH = Path(__file__).resolve().parent / "data" / "phipo_ext.obo"
PHIPO_EXT_SOURCE = "bundled phipo_ext.obo"
FYPO_EXT_OBO_PATH = Path(__file__).resolve().parent / "data" / "fypo_extension.obo"
FYPO_EXT_SOURCE = "bundled fypo_extension.obo"

# Sentinel: "no PHIDO index was injected, use the bundled one". Distinct from an
# injected None, which models an unreadable ontology file.
_UNSET = object()

# Official ID syntax per prefix. Anchored, so a partial match is a fail.
#   GO/PHIPO/PHIDO/BTO/PECO: 7-digit zero-padded numeric local id.
#   MOD (PSI-MOD):           5-digit zero-padded numeric local id.
#   UniProtKB:               the canonical accession regex, with an optional isoform suffix.
_OBO7_RE = re.compile(r"\d{7}$")
_MOD_RE = re.compile(r"\d{5}$")
_LOCAL_ID_RE = {"PHIPO": _OBO7_RE, "PHIPO_EXT": _OBO7_RE, "GO": _OBO7_RE, "PHIDO": _OBO7_RE,
                "MOD": _MOD_RE, "BTO": _OBO7_RE, "PECO": _OBO7_RE, "FYPO_EXT": _OBO7_RE}
_UNIPROT_RE = re.compile(
    r"(?:[OPQ][0-9][A-Z0-9]{3}[0-9]|[A-NR-Z][0-9](?:[A-Z][A-Z0-9]{2}[0-9]){1,2})"
    r"(?:-\d+)?$"
)
# Recognised ways to write a UniProt prefix in a curation.
_UNIPROT_PREFIXES = {"UNIPROTKB", "UNIPROT"}

# Matches any candidate ontology ID in free text, for --file extraction.
# PHIPO_EXT must precede PHIPO in the alternation so the longer prefix wins.
_ID_IN_TEXT_RE = re.compile(
    r"\b(PHIPO_EXT|PHIPO|FYPO_EXT|PHIDO|GO|MOD|BTO|PECO|UniProtKB|UniProt):[A-Za-z0-9-]+",
    re.IGNORECASE)


class OntologyError(RuntimeError):
    """Raised when an OLS request fails."""


@dataclass
class ValidationResult:
    input_id: str
    prefix: Optional[str]          # normalised prefix (PHIPO/GO/PHIDO/UniProtKB) or None
    format_valid: bool
    # exists | obsolete | not_found | format_invalid | format_checked_only |
    # unknown_prefix | error | not_checked
    existence: str
    label: Optional[str]
    source: Optional[str]
    from_cache: bool
    retrieved_at: Optional[str]
    error: Optional[str] = None

    @property
    def ok(self) -> bool:
        """A result passes if its format is valid and there is no positive evidence of a
        problem. `not_checked` (the --format-only case) passes on format alone; only
        format_invalid / not_found / obsolete / unknown_prefix / error fail."""
        return self.format_valid and self.existence in (
            "exists", "format_checked_only", "not_checked")

    def to_dict(self) -> dict:
        d = asdict(self)
        d["ok"] = self.ok
        return d


# Provenance timestamp, HTTP getter and response cache come from the shared envelope
# (phiweaver.common); `_now`/`_requests_get`/`Cache` are kept as backward-compat aliases.
_now = utc_now
_requests_get = make_getter(USER_AGENT)
Cache = ResponseCache


def _split_id(raw: str):
    """Split 'PREFIX:LOCAL' into a normalised (prefix, local) pair.

    Returns (None, raw) when there is no recognised prefix.
    """
    if ":" not in raw:
        return None, raw
    prefix, local = raw.split(":", 1)
    key = prefix.strip().upper()
    if key in OBO_PREFIXES:
        return key, local.strip()
    if key in _UNIPROT_PREFIXES:
        return "UniProtKB", local.strip()
    return None, raw


def check_format(raw: str):
    """Pure, offline format check. Returns (prefix_or_None, format_valid: bool)."""
    prefix, local = _split_id(raw)
    if prefix in OBO_PREFIXES:
        return prefix, bool(_LOCAL_ID_RE[prefix].match(local))
    if prefix == "UniProtKB":
        return prefix, bool(_UNIPROT_RE.match(local))
    return None, False


# ------------------------------------------------------------------- PHIDO (offline)

def _load_phido(path: Path = PHIDO_OBO_PATH) -> Optional[Dict[str, Tuple[Optional[str], bool]]]:
    """Parse the bundled PHIDO .obo into {obo_id: (name, is_obsolete)}.

    Reads only `[Term]` stanzas (ignoring `[Typedef]` etc.). Returns None if the file
    is missing/unreadable, so the caller can report an honest error rather than treating
    every PHIDO ID as not_found.
    """
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return None
    index: Dict[str, Tuple[Optional[str], bool]] = {}
    in_term = False
    cur_id: Optional[str] = None
    name: Optional[str] = None
    obsolete = False

    def flush():
        if in_term and cur_id:
            index[cur_id] = (name, obsolete)

    for line in text.splitlines():
        line = line.strip()
        if line.startswith("[") and line.endswith("]"):
            flush()
            in_term = line == "[Term]"
            cur_id, name, obsolete = None, None, False
        elif not in_term:
            continue
        elif line.startswith("id:"):
            cur_id = line[3:].strip()
        elif line.startswith("name:"):
            name = line[5:].strip()
        elif line.startswith("is_obsolete:"):
            obsolete = line.split(":", 1)[1].strip().lower() == "true"
    flush()
    return index


@lru_cache(maxsize=1)
def _phido_index() -> Optional[Dict[str, Tuple[Optional[str], bool]]]:
    """Module-level cache of the parsed bundled PHIDO ontology (None if unavailable)."""
    return _load_phido()


@lru_cache(maxsize=1)
def _peco_index() -> Optional[Dict[str, Tuple[Optional[str], bool]]]:
    """Module-level cache of the parsed bundled PHI-ECO ontology (None if unavailable)."""
    return _load_phido(PHI_ECO_OBO_PATH)


@lru_cache(maxsize=1)
def _phipo_ext_index() -> Optional[Dict[str, Tuple[Optional[str], bool]]]:
    """Module-level cache of the parsed bundled PHIPO_EXT ontology (None if unavailable)."""
    return _load_phido(PHIPO_EXT_OBO_PATH)


@lru_cache(maxsize=1)
def _fypo_ext_index() -> Optional[Dict[str, Tuple[Optional[str], bool]]]:
    """Module-level cache of the parsed bundled FYPO_EXT ontology (None if unavailable)."""
    return _load_phido(FYPO_EXT_OBO_PATH)


# ------------------------------------------------------------------------- Client

class OntologyValidator:
    def __init__(self, cache: Optional[ResponseCache] = None,
                 http_get: Optional[Callable] = None,
                 phido_index=_UNSET, peco_index=_UNSET, phipo_ext_index=_UNSET,
                 fypo_ext_index=_UNSET):
        self.cache = cache
        self._http_get = http_get or _requests_get
        # Injectable for tests; falls back to the bundled ontology when not supplied.
        self._phido_index = phido_index
        self._peco_index = peco_index
        self._phipo_ext_index = phipo_ext_index
        self._fypo_ext_index = fypo_ext_index

    def _get(self, url: str, params: dict, use_cache: bool):
        key = url + "?" + json.dumps(params, sort_keys=True)
        if use_cache and self.cache:
            hit = self.cache.get(key)
            if hit:
                return hit["payload"], True
        status, body, _headers = self._http_get(url, params)
        if status != 200 or body is None:
            raise OntologyError(f"OLS request failed (HTTP {status}) for {url}")
        if use_cache and self.cache:
            self.cache.put(key, body)
        return body, False

    def validate(self, raw: str, online: bool = True, use_cache: bool = True
                 ) -> ValidationResult:
        prefix, fmt_ok = check_format(raw)

        if prefix is None:
            return ValidationResult(raw, None, False, "unknown_prefix",
                                    None, None, False, None,
                                    "unrecognised prefix; expected PHIPO/PHIPO_EXT/GO/PHIDO/MOD/BTO/PECO/FYPO_EXT/UniProtKB")
        if not fmt_ok:
            return ValidationResult(raw, prefix, False, "format_invalid",
                                    None, None, False, None,
                                    f"does not match {prefix} ID syntax")
        if prefix == "UniProtKB":
            # Existence is resolved by query_uniprot.py, not here.
            return ValidationResult(raw, prefix, True, "format_checked_only",
                                    None, None, False, None,
                                    "use query_uniprot.py to verify existence/function")
        if not online:
            return ValidationResult(raw, prefix, True, "not_checked",
                                    None, None, False, None, None)

        if prefix == "PHIDO":
            # PHIDO is not on OLS4 — resolve offline against the bundled ontology.
            return self._validate_phido(raw)
        if prefix == "PECO":
            # PHI-ECO is PHI-base-local (OLS 'peco' is the unrelated Planteome ontology) —
            # resolve offline against the bundled ontology.
            return self._validate_peco(raw)
        if prefix == "PHIPO_EXT":
            # PHIPO_EXT is a SEPARATE PHI-base ontology (not part of PHIPO, not on OLS) —
            # the extension-only terms (gene-for-gene etc.); resolve offline.
            return self._validate_phipo_ext(raw)
        if prefix == "FYPO_EXT":
            # FYPO_EXT is a small PomBase extension ontology (penetrance/severity values:
            # high/medium/low/complete); not on OLS; resolve offline.
            return self._validate_fypo_ext(raw)

        # GO/PHIPO: verify existence + obsolescence via OLS.
        obo_id = f"{prefix}:{raw.split(':', 1)[1].strip()}"
        ontology = OLS_ONTOLOGY[prefix]
        try:
            body, cached = self._get(
                f"{OLS_BASE_URL}/terms",
                {"obo_id": obo_id, "ontology": ontology},
                use_cache)
        except OntologyError as exc:
            return ValidationResult(raw, prefix, True, "error",
                                    None, OLS_BASE_URL, False, _now(), str(exc))

        term = _find_term(body, obo_id)
        if term is None:
            return ValidationResult(raw, prefix, True, "not_found",
                                    None, OLS_BASE_URL, cached, _now(),
                                    "term not present in ontology")
        label = term.get("label")
        if term.get("is_obsolete"):
            return ValidationResult(raw, prefix, True, "obsolete",
                                    label, OLS_BASE_URL, cached, _now(),
                                    "term is obsolete; do not use")
        return ValidationResult(raw, prefix, True, "exists",
                                label, OLS_BASE_URL, cached, _now())

    def _validate_phido(self, raw: str) -> ValidationResult:
        """Resolve a PHIDO ID offline against the bundled ontology."""
        index = _phido_index() if self._phido_index is _UNSET else self._phido_index
        return self._validate_offline(raw, "PHIDO", index, PHIDO_SOURCE, PHIDO_OBO_PATH)

    def _validate_peco(self, raw: str) -> ValidationResult:
        """Resolve a PECO (PHI-ECO) ID offline against the bundled ontology."""
        index = _peco_index() if self._peco_index is _UNSET else self._peco_index
        return self._validate_offline(raw, "PECO", index, PHI_ECO_SOURCE, PHI_ECO_OBO_PATH)

    def _validate_phipo_ext(self, raw: str) -> ValidationResult:
        """Resolve a PHIPO_EXT ID offline against the bundled ontology."""
        index = _phipo_ext_index() if self._phipo_ext_index is _UNSET else self._phipo_ext_index
        return self._validate_offline(raw, "PHIPO_EXT", index, PHIPO_EXT_SOURCE, PHIPO_EXT_OBO_PATH)

    def _validate_fypo_ext(self, raw: str) -> ValidationResult:
        """Resolve a FYPO_EXT ID offline against the bundled ontology."""
        index = _fypo_ext_index() if self._fypo_ext_index is _UNSET else self._fypo_ext_index
        return self._validate_offline(raw, "FYPO_EXT", index, FYPO_EXT_SOURCE, FYPO_EXT_OBO_PATH)

    @staticmethod
    def _validate_offline(raw: str, prefix: str, index, source: str, path) -> ValidationResult:
        """Resolve an ID offline against a bundled ontology index (PHIDO / PECO)."""
        obo_id = f"{prefix}:{raw.split(':', 1)[1].strip()}"
        if index is None:
            return ValidationResult(raw, prefix, True, "error",
                                    None, source, False, _now(),
                                    f"cannot read bundled {prefix} ontology ({path})")
        if obo_id not in index:
            return ValidationResult(raw, prefix, True, "not_found",
                                    None, source, False, None,
                                    f"term not present in bundled {prefix}")
        name, obsolete = index[obo_id]
        if obsolete:
            return ValidationResult(raw, prefix, True, "obsolete",
                                    name, source, False, None,
                                    "term is obsolete; do not use")
        return ValidationResult(raw, prefix, True, "exists",
                                name, source, False, None)


def _find_term(body: dict, obo_id: str):
    """Return the embedded OLS term whose obo_id matches, or None.

    A single obo_id can appear several times in one ontology's response as cross-references
    from other ontologies (e.g. MOD:00696 is echoed by GO with a placeholder label). Prefer
    the term flagged as the defining ontology's own entry; fall back to the first match."""
    terms = ((body or {}).get("_embedded") or {}).get("terms") or []
    matches = [t for t in terms if (t.get("obo_id") or "").upper() == obo_id.upper()]
    if not matches:
        return None
    for t in matches:
        if t.get("is_defining_ontology"):
            return t
    return matches[0]


# --------------------------------------------------------------------- Extraction

def extract_ids(text: str) -> List[str]:
    """Pull candidate ontology IDs out of free text (e.g. a draft curation), in order,
    de-duplicated. Used by --file."""
    seen = set()
    out = []
    for m in _ID_IN_TEXT_RE.finditer(text):
        token = m.group(0)
        if token not in seen:
            seen.add(token)
            out.append(token)
    return out


# --------------------------------------------------------------------------- CLI

def format_human(results: List[ValidationResult]) -> str:
    mark = {
        "exists": "✅", "format_checked_only": "✅", "not_checked": "•",
        "obsolete": "⛔", "not_found": "❌", "format_invalid": "❌",
        "unknown_prefix": "❌", "error": "⚠️",
    }
    lines = []
    for r in results:
        symbol = mark.get(r.existence, "?")
        label = f"  {r.label}" if r.label else ""
        prov = ""
        if r.existence in ("exists", "obsolete", "not_found"):
            if r.source == OLS_BASE_URL:
                prov = f"  ({'cached' if r.from_cache else 'live'} via OLS)"
            elif r.source:
                prov = f"  (via {r.source})"
        lines.append(f"{symbol} {r.input_id}  [{r.existence}]{label}{prov}")
        if r.error and r.existence not in ("format_checked_only",):
            lines.append(f"    {r.error}")
    passed = sum(1 for r in results if r.ok)
    lines.append("")
    lines.append(f"{passed}/{len(results)} passed "
                 f"(pass = valid format and not missing/obsolete).")
    return "\n".join(lines)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(
        description="Validate PHIPO / GO / PHIDO / MOD / UniProtKB IDs for PHI-Weaver curation.")
    p.add_argument("ids", nargs="*", help="ontology IDs, e.g. PHIPO:0000001 GO:0009405")
    p.add_argument("--file", help="extract and validate every ontology ID found in a file")
    p.add_argument("--format-only", action="store_true",
                   help="offline: check ID syntax only, no OLS lookup")
    p.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    p.add_argument("--no-cache", action="store_true", help="bypass the local cache")
    p.add_argument("--cache", default=os.environ.get("ONTOLOGY_CACHE", str(DEFAULT_CACHE)),
                   help="cache file path (or set ONTOLOGY_CACHE)")
    args = p.parse_args(argv)

    ids: List[str] = list(args.ids)
    if args.file:
        try:
            ids.extend(extract_ids(Path(args.file).read_text(encoding="utf-8")))
        except OSError as exc:
            p.error(f"cannot read --file: {exc}")
    if not ids:
        p.error("provide one or more IDs, or --file")

    cache = None if (args.no_cache or args.format_only) else Cache(args.cache)
    validator = OntologyValidator(cache=cache)
    results = [
        validator.validate(i, online=not args.format_only, use_cache=not args.no_cache)
        for i in ids
    ]
    if cache:
        cache.close()

    if args.json:
        print(json.dumps([r.to_dict() for r in results], indent=2))
    else:
        print(format_human(results))
    return 0 if all(r.ok for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
