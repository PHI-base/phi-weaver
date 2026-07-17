#!/usr/bin/env python3
"""
gap_log.py — append-only ledger of ontology term gaps met during curation.

Every time a phenotype or condition phrase fails to map (`no_match` from map_phenotype /
map_condition), that is evidence about the ontology, not just a dead end in one draft. This
module retains those events so they accumulate into something an ontology editor can act on:
a ranked list of gaps, each backed by the papers that actually needed the term.

Frequency is the point. A gap eight papers hit is a far stronger case than one curator's
itch, and today that distinction is invisible because misses are reported into a draft and
then forgotten.

Two outcomes are recorded, and the difference matters:

- **gap** — nothing matched, including after retrying alternate wordings. Evidence for a
  *new term* request.
- **synonym** — the phrase missed, but a retry found an existing term. That is not an
  ontology gap; it is a term whose wording curators don't naturally reach for. Evidence for
  a cheaper *synonym* request (see lesson L2 in docs/CURATION-LESSONS.md, where a DON phrase
  looked like a gap and wasn't).

Recording a `gap` before retrying alternate wordings floods the tracker with false gaps and
burns credibility with the ontology team, so the retry belongs *before* the record call —
see the phipo-mapping skill.

This tool only gathers evidence. It does not draft term definitions, propose parents, or
place terms in the hierarchy: that is the ontology editors' work.

The ledger is JSONL (one event per line) so it appends cleanly and diffs in git, alongside
the project's other append-only ledgers (docs/BACKLOG.md, docs/CURATION-LESSONS.md).

CLI:
    python3 -m phiweaver.lookup.gap_log record PHIPO "absent DON" \\
        --pmid 42089373 --context "Table S4: no detectable DON in the Sdh deletions"
    python3 -m phiweaver.lookup.gap_log record PHIPO "no DON produced" --pmid 42089373 \\
        --outcome synonym --matched-term PHIPO:0001445 --matched-via "decreased DON level"
    python3 -m phiweaver.lookup.gap_log report
    python3 -m phiweaver.lookup.gap_log report --ontology PECO --json

The ledger path is injectable (``path=``) and overridable via ``PHIWEAVER_GAP_LOG``, so this
tests offline without touching the real ledger.
"""

from __future__ import annotations

import argparse
import json
import os
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Optional

from phiweaver.common import utc_now

DEFAULT_LOG = Path(__file__).resolve().parents[2] / "docs" / "ontology-gaps.jsonl"

# Validated, not free text: a typo'd ontology name silently fragments the ranking, which is
# the one thing this ledger exists to produce.
ONTOLOGIES = ("PHIPO", "PECO", "PHIDO", "PHIPO_EXT", "FYPO_EXT")
OUTCOMES = ("gap", "synonym")

_WS_RE = re.compile(r"\s+")


class GapLogError(ValueError):
    """Raised when an event would corrupt the ledger's meaning."""


@dataclass
class GapEvent:
    ontology: str                    # one of ONTOLOGIES
    phrase: str                      # the phrase as the curator wrote it, verbatim
    outcome: str                     # gap | synonym
    pmid: Optional[str] = None       # the paper that needed the term
    context: Optional[str] = None    # where in the paper, and what was measured
    matched_term: Optional[str] = None   # synonym only: the term the retry found
    matched_via: Optional[str] = None    # synonym only: the wording that found it
    filed: Optional[str] = None          # tracker URL, once the request has been submitted
    recorded_at: Optional[str] = None

    def to_json(self) -> str:
        return json.dumps(asdict(self), sort_keys=True)


def normalise(phrase: str) -> str:
    """Group key for a phrase: case- and whitespace-insensitive, else the same gap seen in
    two papers ranks as two gaps."""
    return _WS_RE.sub(" ", phrase.strip().lower())


def _log_path(path: Optional[Path] = None) -> Path:
    if path is not None:
        return Path(path)
    return Path(os.environ.get("PHIWEAVER_GAP_LOG", str(DEFAULT_LOG)))


def record(ontology: str, phrase: str, outcome: str = "gap",
           pmid: Optional[str] = None, context: Optional[str] = None,
           matched_term: Optional[str] = None, matched_via: Optional[str] = None,
           filed: Optional[str] = None, path: Optional[Path] = None) -> GapEvent:
    """Append one event. Validates the invariants that keep `report` meaningful.

    To mark an already-recorded gap as filed, append a further event for the same phrase
    carrying ``filed`` — the ledger stays append-only and `rank_gaps` picks the URL up."""
    ontology = ontology.strip().upper()
    if ontology not in ONTOLOGIES:
        raise GapLogError(f"unknown ontology {ontology!r}; expected one of "
                          f"{', '.join(ONTOLOGIES)}")
    if outcome not in OUTCOMES:
        raise GapLogError(f"unknown outcome {outcome!r}; expected one of "
                          f"{', '.join(OUTCOMES)}")
    if not phrase.strip():
        raise GapLogError("phrase is empty — there is nothing to record")
    # A synonym event without the term it resolved to is indistinguishable from a gap, and
    # a gap carrying a term contradicts itself. Either way the ranking would lie.
    if outcome == "synonym" and not matched_term:
        raise GapLogError("outcome 'synonym' needs --matched-term: the term the retry found")
    if outcome == "gap" and matched_term:
        raise GapLogError("outcome 'gap' cannot carry a matched term — record it as 'synonym'")

    event = GapEvent(ontology=ontology, phrase=phrase.strip(), outcome=outcome,
                     pmid=(pmid.strip() if pmid else None),
                     context=(context.strip() if context else None),
                     matched_term=(matched_term.strip() if matched_term else None),
                     matched_via=(matched_via.strip() if matched_via else None),
                     filed=(filed.strip() if filed else None),
                     recorded_at=utc_now())

    p = _log_path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as fh:
        fh.write(event.to_json() + "\n")
    return event


def load(path: Optional[Path] = None) -> List[GapEvent]:
    """Read the ledger. A missing ledger is empty, not an error — nothing has been met yet."""
    p = _log_path(path)
    if not p.exists():
        return []
    events: List[GapEvent] = []
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        d = json.loads(line)
        events.append(GapEvent(**d))
    return events


@dataclass
class GapRank:
    ontology: str
    phrase: str                  # the most recent verbatim wording seen
    papers: List[str]            # distinct PMIDs that needed this term
    seen: int                    # total events, including repeats within one paper
    variants: List[str]          # the distinct wordings tried
    contexts: List[str]
    filed: Optional[str] = None  # tracker URL if already submitted — do not re-file


@dataclass
class SynonymRank:
    ontology: str
    matched_term: str
    missed_phrases: List[str]    # wordings that failed to find this term
    papers: List[str]


def rank_gaps(events: List[GapEvent], ontology: Optional[str] = None) -> List[GapRank]:
    """Genuine gaps, ranked by how many distinct papers needed the term."""
    buckets: Dict[tuple, GapRank] = {}
    for e in events:
        if e.outcome != "gap":
            continue
        if ontology and e.ontology != ontology.upper():
            continue
        key = (e.ontology, normalise(e.phrase))
        r = buckets.get(key)
        if r is None:
            r = buckets[key] = GapRank(e.ontology, e.phrase, [], 0, [], [])
        r.phrase = e.phrase
        r.seen += 1
        if e.pmid and e.pmid not in r.papers:
            r.papers.append(e.pmid)
        if e.phrase not in r.variants:
            r.variants.append(e.phrase)
        if e.context and e.context not in r.contexts:
            r.contexts.append(e.context)
        if e.filed:
            r.filed = e.filed
    out = list(buckets.values())
    # Unfiled first: a filed gap is the ontology team's move now, not ours.
    out.sort(key=lambda r: (r.filed is not None, -len(r.papers), -r.seen,
                            normalise(r.phrase)))
    return out


def rank_synonyms(events: List[GapEvent], ontology: Optional[str] = None) -> List[SynonymRank]:
    """Existing terms curators couldn't find, ranked by how many wordings missed them."""
    buckets: Dict[tuple, SynonymRank] = {}
    for e in events:
        if e.outcome != "synonym" or not e.matched_term:
            continue
        if ontology and e.ontology != ontology.upper():
            continue
        key = (e.ontology, e.matched_term)
        r = buckets.get(key)
        if r is None:
            r = buckets[key] = SynonymRank(e.ontology, e.matched_term, [], [])
        if e.phrase not in r.missed_phrases:
            r.missed_phrases.append(e.phrase)
        if e.pmid and e.pmid not in r.papers:
            r.papers.append(e.pmid)
    out = list(buckets.values())
    out.sort(key=lambda r: (-len(r.missed_phrases), r.matched_term))
    return out


def format_human(gaps: List[GapRank], synonyms: List[SynonymRank]) -> str:
    lines: List[str] = []
    lines.append("Term gaps — no match after retrying alternate wordings (→ new-term request)")
    if not gaps:
        lines.append("    (none recorded)")
    for g in gaps:
        papers = ", ".join(f"PMID:{p}" for p in g.papers) or "no PMID recorded"
        mark = "✓" if g.filed else "❌"
        lines.append(f"  {mark} [{g.ontology}] {g.phrase}")
        if g.filed:
            lines.append(f"       already filed: {g.filed} — do not re-file; chase instead")
        lines.append(f"       {len(g.papers)} paper(s): {papers}")
        if len(g.variants) > 1:
            lines.append(f"       wordings tried: {'; '.join(g.variants)}")
        for c in g.contexts:
            lines.append(f"       evidence: {c}")
    lines.append("")
    lines.append("Wording gaps — a retry found an existing term (→ synonym request, cheaper)")
    if not synonyms:
        lines.append("    (none recorded)")
    for s in synonyms:
        papers = ", ".join(f"PMID:{p}" for p in s.papers) or "no PMID recorded"
        lines.append(f"  ✎ [{s.ontology}] {s.matched_term} was missed by: "
                     f"{'; '.join(s.missed_phrases)}")
        lines.append(f"       {len(s.papers)} paper(s): {papers}")
    lines.append("")
    lines.append(f"{len(gaps)} term gap(s), {len(synonyms)} wording gap(s). Evidence only — a "
                 "curator decides what is worth filing, and the ontology editors decide what "
                 "gets built.")
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="Append-only ledger of ontology term gaps met during curation, and a "
                    "ranked report over them. Gathers evidence; never drafts ontology terms.")
    ap.add_argument("--log", help="ledger path (or set PHIWEAVER_GAP_LOG)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    rec = sub.add_parser("record", help="append one gap event")
    rec.add_argument("ontology", help=f"one of: {', '.join(ONTOLOGIES)}")
    rec.add_argument("phrase", help="the phrase that failed to map, verbatim")
    rec.add_argument("--outcome", default="gap", choices=OUTCOMES,
                     help="'gap' = nothing matched after retries; 'synonym' = a retry found "
                          "an existing term (default: gap)")
    rec.add_argument("--pmid", help="the paper that needed the term")
    rec.add_argument("--context", help="where in the paper, and what was measured")
    rec.add_argument("--matched-term", help="synonym only: the term the retry found")
    rec.add_argument("--matched-via", help="synonym only: the wording that found it")
    rec.add_argument("--filed", metavar="URL",
                     help="tracker URL, once the request is submitted — re-record the same "
                          "phrase with this to stop it resurfacing as a new candidate")

    rep = sub.add_parser("report", help="ranked gaps over the ledger")
    rep.add_argument("--ontology", help="restrict to one ontology, e.g. PECO")
    rep.add_argument("--json", action="store_true", help="emit machine-readable JSON")

    args = ap.parse_args(argv)
    path = Path(args.log) if args.log else None

    if args.cmd == "record":
        try:
            event = record(args.ontology, args.phrase, outcome=args.outcome, pmid=args.pmid,
                           context=args.context, matched_term=args.matched_term,
                           matched_via=args.matched_via, filed=args.filed, path=path)
        except GapLogError as exc:
            ap.error(str(exc))
        where = _log_path(path)
        print(f"recorded {event.outcome}: [{event.ontology}] {event.phrase} → {where}")
        return 0

    events = load(path)
    gaps = rank_gaps(events, args.ontology)
    synonyms = rank_synonyms(events, args.ontology)
    if args.json:
        print(json.dumps({"gaps": [asdict(g) for g in gaps],
                          "synonyms": [asdict(s) for s in synonyms]}, indent=2))
    else:
        print(format_human(gaps, synonyms))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
