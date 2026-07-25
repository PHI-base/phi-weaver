#!/usr/bin/env python3
"""
phibase_index.py — has this paper already been curated in PHI-base?

Answers, by PMID, whether a paper already appears in a published PHI-base release, so the
answer arrives at **triage** time rather than after the drafting effort is spent.

Surfaced 2026-07-24 on PMID:9927411 (see docs/BACKLOG.md): phiweaver drafted that paper end
to end, but PHI-base has held it as ``PHI:132`` since at least release v4-08.

Why a hit is worth more than "stop, duplicate":
- A duplicate draft wastes the curator's review time.
- Worse, a draft can **silently disagree** with the established entry on exactly the
  judgements it is weakest on. For PMID:9927411 the PHI-base record files the pathogen under
  taxid 318829 (*Magnaporthe oryzae*); the draft had used *Pyricularia grisea* (148305).
  An existing curated entry should win over a fresh draft, so a hit reports the record's
  gene / pathogen / host / phenotype fields as a cross-check rather than a bare flag.

Design rules (see AGENTS.md):
- **Never invent.** A miss is reported as ``not_found`` — never as "probably not curated".
- **State the recall ceiling.** A miss is not proof a paper is uncurated: PHI-base 4
  *releases* do not contain in-progress PHI-Canto sessions, and a few records cite a
  non-PubMed source and so cannot be found by PMID at all. Both caveats are printed with
  every miss, and the non-PubMed count is measured from the release, not hardcoded.
- **Provenance.** Every answer names the release file it came from.

Data source: https://github.com/PHI-base/data (CC-BY-4.0), ``releases/``. Pinned to a named
release so results are reproducible; ``--release`` takes any filename from that directory
(``phi-base_current.csv`` tracks the newest). The download is cached under ``.cache/`` and
reused; ``--refresh`` re-fetches.

Two release quirks this handles, both found in v4-19 and neither documented upstream:
- The CSV carries a **duplicated header row as its first data row**; a naive parse yields a
  phantom record whose every field is a column name.
- The PMID column was renamed: ``PMID`` up to v4-08, ``Literature_ID`` in current releases.
  Both spellings are accepted so an old pinned release still works.

CLI:
    python3 -m phiweaver.lookup.phibase_index 9927411
    python3 -m phiweaver.lookup.phibase_index 9927411 33712518 --json
    python3 -m phiweaver.lookup.phibase_index 9927411 --refresh
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Callable, Dict, List, Optional

RAW_BASE = "https://raw.githubusercontent.com/PHI-base/data/master/releases"
DEFAULT_RELEASE = "phi-base_v4-19_2026-03-25.csv"
DEFAULT_CACHE = Path(__file__).resolve().parent / ".cache" / "phibase"
USER_AGENT = "PHI-Weaver-phibase-index/1.0 (https://github.com/PHI-base/phi-weaver)"
TIMEOUT = 120  # the release CSV is ~17 MB
MAX_LISTED = 5  # records listed per PMID before the rest are summarised

# Verified 2026-07-25 to resolve to the record itself (PHI:132 → ABC1). Note **http**:
# https://www.phi-base.org does not answer, so this must not be "upgraded" to https.
RECORD_URL = "http://www.phi-base.org/searchFacet.htm?queryTerm={phi_id}"

# Release column → our field name. Kept in one place because the release schema does drift
# (the PMID column has already been renamed once); a future rename is a one-line fix here.
COLUMNS = {
    "phi_id": ("PHI_MolConn_ID",),
    "record_id": ("Record ID",),
    "protein_id": ("ProteinID",),
    "gene_name": ("Gene_name",),
    "pathogen_taxid": ("Pathogen_NCBI_species_Taxonomy ID",),
    "pathogen_species": ("Pathogen_species",),
    "pathogen_strain": ("Experimental_strain",),
    "disease": ("Disease_name",),
    "host_taxid": ("Host_NCBI_Taxonomy_ID",),
    "host_species": ("Experimental_host_species",),
    "mutant_phenotype": ("Phenotype_of_mutant",),
    "year": ("Year_published",),
}
PMID_COLUMNS = ("Literature_ID", "PMID")
SOURCE_COLUMNS = ("Literature_source",)


class PhibaseReleaseError(RuntimeError):
    """Raised when a release file cannot be fetched or parsed."""


@dataclass
class PhibaseRecord:
    """One PHI-base record (one row of a release), reduced to the cross-check fields."""

    phi_id: str = ""
    record_id: str = ""
    protein_id: str = ""
    gene_name: str = ""
    pathogen_taxid: str = ""
    pathogen_species: str = ""
    pathogen_strain: str = ""
    disease: str = ""
    host_taxid: str = ""
    host_species: str = ""
    mutant_phenotype: str = ""
    year: str = ""

    @property
    def url(self) -> str:
        return RECORD_URL.format(phi_id=self.phi_id) if self.phi_id else ""


@dataclass
class PhibaseIndex:
    """PMID → records, plus the counts needed to state the index's own recall limits."""

    release: str = DEFAULT_RELEASE
    by_pmid: Dict[str, List[PhibaseRecord]] = field(default_factory=dict)
    n_records: int = 0
    n_non_pubmed: int = 0

    @property
    def n_pmids(self) -> int:
        return len(self.by_pmid)

    def lookup(self, pmid) -> List[PhibaseRecord]:
        return self.by_pmid.get(normalise_pmid(pmid), [])

    def contains(self, pmid) -> bool:
        return bool(self.lookup(pmid))


def normalise_pmid(pmid) -> str:
    """``'PMID:9927411'``, ``' 9927411 '``, ``9927411`` → ``'9927411'``."""
    text = str(pmid).strip()
    if text.lower().startswith("pmid:"):
        text = text[5:].strip()
    return text


def _first(row: dict, names) -> str:
    """Value of the first column present in ``row`` — tolerates schema drift."""
    for name in names:
        if name in row and row[name] is not None:
            return row[name].strip()
    return ""


def _is_header_repeat(row: dict) -> bool:
    """True for a row that restates the header (the release's first data row does)."""
    return any(row.get(name, "").strip() == name for name in ("Record ID", "PHI_MolConn_ID"))


def build_index(path, release: Optional[str] = None) -> PhibaseIndex:
    """Parse a release CSV into a PMID index.

    Only rows whose literature source is PubMed *and* whose ID is all digits are indexed;
    everything else is counted into ``n_non_pubmed`` so a miss can be reported honestly.
    """
    path = Path(path)
    index = PhibaseIndex(release=release or path.name)
    try:
        handle = path.open(newline="", encoding="utf-8-sig")
    except OSError as exc:
        raise PhibaseReleaseError(f"cannot read release {path}: {exc}") from exc
    with handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise PhibaseReleaseError(f"release {path} has no header row")
        for row in reader:
            if _is_header_repeat(row):
                continue
            index.n_records += 1
            pmid = _first(row, PMID_COLUMNS)
            source = _first(row, SOURCE_COLUMNS).lower()
            if not pmid.isdigit() or "pubmed" not in source:
                index.n_non_pubmed += 1
                continue
            record = PhibaseRecord(**{key: _first(row, names)
                                      for key, names in COLUMNS.items()})
            index.by_pmid.setdefault(pmid, []).append(record)
    return index


def _default_fetch(url: str) -> bytes:
    import urllib.request

    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:  # nosec - fixed host
        return resp.read()


def default_cache_dir() -> str:
    return os.environ.get("PHIBASE_CACHE", str(DEFAULT_CACHE))


def release_path(release: str = DEFAULT_RELEASE, cache_dir=None) -> Path:
    return Path(cache_dir or default_cache_dir()) / release


def ensure_release(release: str = DEFAULT_RELEASE, cache_dir=None, refresh: bool = False,
                   fetch: Optional[Callable[[str], bytes]] = None) -> Path:
    """Return a local path to ``release``, downloading it once if absent.

    ``fetch`` is injectable so tests never touch the network.
    """
    path = release_path(release, cache_dir)
    if path.exists() and not refresh:
        return path
    payload = (fetch or _default_fetch)(f"{RAW_BASE}/{release}")
    if not payload:
        raise PhibaseReleaseError(f"empty download for release {release}")
    path.parent.mkdir(parents=True, exist_ok=True)
    # Write via a temp file so an interrupted download can't leave a truncated release
    # that later looks like a valid cache hit.
    tmp = path.with_suffix(path.suffix + ".part")
    tmp.write_bytes(payload)
    tmp.replace(path)
    return path


def load_index(release: str = DEFAULT_RELEASE, cache_dir=None, refresh: bool = False,
               fetch: Optional[Callable[[str], bytes]] = None) -> PhibaseIndex:
    """Download (if needed) and parse a release into a :class:`PhibaseIndex`."""
    return build_index(ensure_release(release, cache_dir, refresh, fetch), release=release)


def format_report(pmid, records: List[PhibaseRecord], index: PhibaseIndex,
                  max_records: int = MAX_LISTED) -> str:
    """Human-readable triage flag for one PMID.

    Long hits are truncated: genome-scale papers reach hundreds of records in one release
    (v4-19's largest is 709), and dumping them all buries the one fact triage needs. The
    remainder is summarised by distinct gene / pathogen counts instead.
    """
    pmid = normalise_pmid(pmid)
    if not records:
        return "\n".join([
            f"PMID:{pmid} — not found in {index.release}",
            "  Not proof it is uncurated: releases exclude in-progress PHI-Canto sessions, "
            f"and {index.n_non_pubmed} record(s) in this release cite a non-PubMed source.",
        ])
    plural = "record" if len(records) == 1 else "records"
    lines = [f"PMID:{pmid} — ALREADY CURATED in PHI-base ({len(records)} {plural})"]
    for rec in records[:max_records]:
        head = "  ".join(x for x in (rec.phi_id, rec.record_id, rec.gene_name) if x)
        if rec.protein_id:
            head += f"  UniProtKB:{rec.protein_id}"
        lines.append(f"  {head}")
        pathogen = rec.pathogen_species or "?"
        if rec.pathogen_taxid:
            pathogen += f" (taxid {rec.pathogen_taxid})"
        if rec.pathogen_strain:
            pathogen += f", strain {rec.pathogen_strain}"
        lines.append(f"    pathogen: {pathogen}")
        host = rec.host_species or "?"
        if rec.host_taxid:
            host += f" (taxid {rec.host_taxid})"
        lines.append(f"    host:     {host}")
        tail = [x for x in (f"disease: {rec.disease}" if rec.disease else "",
                            f"phenotype: {rec.mutant_phenotype}" if rec.mutant_phenotype else "",
                            f"published: {rec.year}" if rec.year else "") if x]
        if tail:
            lines.append("    " + "   ".join(tail))
        if rec.url:
            lines.append(f"    {rec.url}")
    hidden = records[max_records:]
    if hidden:
        genes = len({r.gene_name for r in records if r.gene_name})
        pathogens = sorted({r.pathogen_species for r in records if r.pathogen_species})
        summary = f"  … {len(hidden)} further record(s): {genes} distinct gene(s)"
        if pathogens:
            shown = ", ".join(pathogens[:3])
            more = f" +{len(pathogens) - 3} more" if len(pathogens) > 3 else ""
            summary += f"; pathogen(s): {shown}{more}"
        lines.append(summary)
    lines.append("  An existing curated entry wins over a fresh draft — reconcile against "
                 "these fields, don't re-draft.")
    lines.append(f"  Source: {index.release}")
    return "\n".join(lines)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Check whether a paper (by PMID) is already curated in PHI-base.")
    parser.add_argument("pmids", nargs="+", help="one or more PMIDs (bare or PMID:-prefixed)")
    parser.add_argument("--release", default=DEFAULT_RELEASE,
                        help=f"release filename from PHI-base/data releases/ "
                             f"(default {DEFAULT_RELEASE}; 'phi-base_current.csv' tracks newest)")
    parser.add_argument("--cache", default=None,
                        help="cache directory (default $PHIBASE_CACHE or .cache/phibase)")
    parser.add_argument("--refresh", action="store_true",
                        help="re-download the release even if cached")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    args = parser.parse_args(argv)

    cached = release_path(args.release, args.cache).exists()
    try:
        index = load_index(args.release, args.cache, args.refresh)
    except PhibaseReleaseError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"error: could not fetch release {args.release}: {exc}", file=sys.stderr)
        return 2

    results = [{"pmid": normalise_pmid(p),
                "status": "curated" if index.contains(p) else "not_found",
                "records": [{**asdict(r), "url": r.url} for r in index.lookup(p)]}
               for p in args.pmids]

    if args.json:
        print(json.dumps({"release": index.release,
                          "release_cached": cached and not args.refresh,
                          "records_in_release": index.n_records,
                          "pmids_in_release": index.n_pmids,
                          "non_pubmed_records": index.n_non_pubmed,
                          "results": results}, indent=2))
    else:
        if not cached or args.refresh:
            print(f"(downloaded {index.release}; "
                  f"{index.n_pmids} PMIDs / {index.n_records} records)\n")
        for i, pmid in enumerate(args.pmids):
            if i:
                print()
            print(format_report(pmid, index.lookup(pmid), index))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
