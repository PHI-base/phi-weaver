#!/usr/bin/env python3
"""
map_condition.py — deterministic condition-phrase → PECO (PHI-ECO) term search.

Given an experimental-condition phrase (growth medium, temperature, inoculation / delivery
method, light regime, wounding, ...), search the bundled **PHI-ECO** ontology and return the
candidate **PECO** terms that actually exist — with their real PECO IDs and labels. This is
the deterministic half of the "condition → PECO term" step so the drafting workflow can emit
controlled Condition-field terms instead of free-text prose. It NEVER invents an ID: a phrase
with no PECO hit is reported as "no_match".

Offline by design: PHI-ECO is PHI-base-local (the OLS ontology named `peco` is the *unrelated*
Planteome ontology), so this searches the vendored `data/phi-eco.obo` — no network. Obsolete
terms and high-level `Grouping_terms` (not for direct annotation) are excluded.

**Granularity note:** PHI-ECO conditions are largely **qualitative** — e.g. `rich medium`,
`minimal medium`, `standard/high/low temperature`, delivery mechanisms, `+ wounding`. It does
**not** hold granular values like "PDA" or "25 °C". Map the qualitative condition to a PECO
term and keep the numeric specifics (exact medium, temperature, duration) in the annotation
comment. `validate_ontology_ids` confirms the chosen PECO ID is current.

CLI:
    python3 -m phiweaver.lookup.map_condition "rich medium" "pathogen mycelium inoculation"
    python3 -m phiweaver.lookup.map_condition --file conditions.txt --json
    python3 -m phiweaver.lookup.map_condition "wounding" --rows 8
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import List, Optional

PHI_ECO_OBO_PATH = Path(__file__).resolve().parent / "data" / "phi-eco.obo"
PHI_ECO_SOURCE = "bundled phi-eco.obo"
DEFAULT_ROWS = 5
_TOKEN_RE = re.compile(r"[a-z0-9]+")
_SYN_RE = re.compile(r'"([^"]*)"')


@dataclass(frozen=True)
class Term:
    obo_id: str
    name: str
    synonyms: tuple


@dataclass
class Candidate:
    obo_id: str
    label: str
    score: float


@dataclass
class ConditionMapping:
    phrase: str
    status: str                # "matched" | "no_match"
    candidates: List[Candidate]
    source: str = PHI_ECO_SOURCE


def _tokens(text: str) -> set:
    return set(_TOKEN_RE.findall(text.lower()))


def load_terms(path: Path = PHI_ECO_OBO_PATH) -> List[Term]:
    """Parse phi-eco.obo into annotatable PECO terms (excludes obsolete + Grouping_terms)."""
    terms: List[Term] = []
    in_term = False
    cur: dict = {}

    def flush():
        oid = cur.get("id", "")
        name = cur.get("name", "")
        if (oid.startswith("PECO:") and not cur.get("obsolete")
                and "Grouping_terms" not in cur.get("subsets", ())
                and not name.lower().startswith("obsolete ")):
            terms.append(Term(oid, name, tuple(cur.get("syn", []))))

    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("[") and line.endswith("]"):
            if in_term and cur:
                flush()
            in_term, cur = (line == "[Term]"), {}
        elif not in_term:
            continue
        elif line.startswith("id:"):
            cur["id"] = line[3:].strip()
        elif line.startswith("name:"):
            cur["name"] = line[5:].strip()
        elif line.startswith("is_obsolete:"):
            cur["obsolete"] = line.split(":", 1)[1].strip().lower() == "true"
        elif line.startswith("subset:"):
            cur.setdefault("subsets", []).append(line.split(":", 1)[1].strip())
        elif line.startswith("synonym:"):
            m = _SYN_RE.search(line)
            if m:
                cur.setdefault("syn", []).append(m.group(1))
    if in_term and cur:
        flush()
    return terms


def _score(phrase: str, term: Term) -> float:
    """Relevance of a term to a phrase: exact > substring > token overlap (Jaccard)."""
    q = phrase.lower().strip()
    qt = _tokens(phrase)
    best = 0.0
    for text in (term.name, *term.synonyms):
        cl = text.lower().strip()
        if cl == q:
            return 100.0
        if q and (q in cl or cl in q):
            best = max(best, 60.0 + len(qt & _tokens(text)))
            continue
        tt = _tokens(text)
        if qt and tt:
            overlap = len(qt & tt)
            if overlap:
                best = max(best, 20.0 * overlap * overlap / len(qt | tt))
    return best


def search(phrase: str, terms: List[Term], rows: int = DEFAULT_ROWS) -> ConditionMapping:
    scored = [(s, t) for t in terms if (s := _score(phrase, t)) > 0]
    scored.sort(key=lambda st: (-st[0], st[1].name))
    cands = [Candidate(t.obo_id, t.name, round(s, 2)) for s, t in scored[:rows]]
    return ConditionMapping(phrase, "matched" if cands else "no_match", cands)


def read_phrases(path: str) -> List[str]:
    return [ln.strip() for ln in Path(path).read_text(encoding="utf-8").splitlines() if ln.strip()]


def format_human(results: List[ConditionMapping]) -> str:
    out = []
    for r in results:
        if r.status == "no_match":
            out.append(f"❌ {r.phrase}  [no PECO match]")
            continue
        out.append(f"✅ {r.phrase}")
        for i, c in enumerate(r.candidates):
            out.append(f"    {'★' if i == 0 else '•'} {c.obo_id}  {c.label}")
    matched = sum(1 for r in results if r.status == "matched")
    out.append(f"\n{matched}/{len(results)} phrase(s) matched a PECO term. Suggestions only — "
               "map the qualitative condition, keep numeric specifics in the comment; verify the "
               "chosen ID with validate_ontology_ids.")
    return "\n".join(out)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="Map experimental-condition phrase(s) to candidate PECO (PHI-ECO) terms "
                    "(offline, over the bundled ontology). Never invents IDs.")
    ap.add_argument("phrases", nargs="*", help="condition description(s), e.g. \"rich medium\"")
    ap.add_argument("--file", help="read one condition phrase per line from a file")
    ap.add_argument("--rows", type=int, default=DEFAULT_ROWS, help="max candidates per phrase")
    ap.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    args = ap.parse_args(argv)

    phrases = list(args.phrases)
    if args.file:
        phrases += read_phrases(args.file)
    if not phrases:
        ap.error("give at least one phrase, or --file")

    terms = load_terms()
    results = [search(p, terms, rows=args.rows) for p in phrases]
    if args.json:
        print(json.dumps([asdict(r) for r in results], indent=2))
    else:
        print(format_human(results))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
