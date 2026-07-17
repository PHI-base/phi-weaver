#!/usr/bin/env python3
"""
map_phenotype.py — deterministic phenotype-phrase → PHIPO term search for PHI-Weaver.

Given a phenotype description (typically a phrase a curator lifted from a paper's figure
caption or results text), search the Pathogen–Host Interaction Phenotype Ontology (PHIPO)
and return the candidate terms that actually exist — with their real PHIPO IDs and labels.
It NEVER invents an ID: a phrase with no PHIPO hit is reported as "no_match", not mapped to
a guessed term.

This is the deterministic half of the caption → phenotype → PHIPO workflow (see the
phipo-mapping skill). Deciding which phrases in a caption *are* phenotypes is a reasoning
step done by the curator/agent; this tool maps a given phrase to real candidate terms, and
the companion validate_ontology_ids.py confirms the chosen ID is current.

**Offline by design** (2026-07-17; was EBI OLS). Searches the bundled `data/phipo-base.obo`
— no network. Three reasons, in order of weight:

1. **OLS search hides deprecated terms**, so a concept that once existed returns a clean
   `no_match` and looks like a virgin gap. That is exactly how PHI-base/phipo#452 was
   written unaware that PHIPO:0000503 already existed and had been obsoleted. Here obsolete
   terms are *in the file*: excluded from suggestions by default (a curator cannot annotate
   to one), but surfaced by ``--include-obsolete`` for gap analysis.
2. **The benchmark sandbox.** A bundled file needs no network during a scored run, so the
   allowlist stays default-deny with no PHIPO exception. This matters because
   `github.com/PHI-base` hosts *both* the phipo ontology **and** the curated data repos (=
   the answer key), so "ontology yes, data no" cannot be expressed at the domain level.
   PHIPO is a tool, not an answer.
3. Deterministic and fast: no network flake, no cache staleness, same result every run.

**Which file, and why it matters.** `phipo-base.obo` is the *release artifact* — what OLS
serves and (approximately) what PHI-Canto has loaded. It answers the question a curator
actually has: *can I annotate this?* The working file `phipo-edit.owl` (in a clone of
PHI-base/phipo) is **deliberately not used here**: it contains **unreleased** terms that
PHI-Canto does not have, so suggesting one would be a bug that looks like a feature. Use the
edit file for gap analysis only — see `skills/ontology-term-request/SKILL.md` step 5.

The cost is search quality: OLS is Solr-backed with stemming; the scorer here is exact >
substring > token overlap. Acceptable — lesson L7 establishes OLS's ranking is untrustworthy
anyway (it confidently returned a within-host term for an in-vitro phrase), so a human reads
every candidate regardless: favour recall (a generous ``--rows``) over clever ranking.

Design rules (see AGENTS.md, phipo-mapping / curation-qc skills):
- Never guess: only terms present in the bundled ontology are returned; "no_match" is
  explicit, never a fabricated ID.
- Obsolete terms are excluded from suggestions (curation requires current terms).
- Record provenance: source file, ontology release, UTC timestamp.
- The exit code reflects whether the *search ran*, not whether it found a match: 0 unless a
  query errored (a clean "no_match" is exit 0). The per-query `status` carries the result.

CLI:
    python3 -m phiweaver.lookup.map_phenotype "reduced virulence"
    python3 -m phiweaver.lookup.map_phenotype --file phenotype-phrases.txt --json
    python3 -m phiweaver.lookup.map_phenotype "abnormal conidiation" --rows 10
    python3 -m phiweaver.lookup.map_phenotype "deoxynivalenol absent" --include-obsolete
"""

from __future__ import annotations

import argparse
import json
import math
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import List, Optional

from phiweaver.common import utc_now
from phiweaver.lookup import gap_log, term_context

PHIPO_OBO_PATH = Path(__file__).resolve().parent / "data" / "phipo-base.obo"
PHIPO_PREFIX = "PHIPO:"
DEFAULT_ROWS = 5
# Minimum IDF-coverage score for a term to count as a candidate; below it, `no_match`.
# Tuned empirically (2026-07-17) against real curation phrases vs. prose/junk:
#   true matches            35–100  ("increased sensitivity to hydrogen peroxide" = 35, lowest)
#   junk / running prose     0–12.7 (shares only generic vocabulary: "to", "host", "pathogen")
#   a genuine wording gap    14.1   ("abnormal conidiation" — PHIPO says "asexual spores" and
#                                    has no "conidiation" token at all; BACKLOG tracks it)
# 20.0 sits in the wide gap between junk and true matches, and correctly leaves the wording
# gap unmatched — which is the point: `no_match` is what --log-gaps and gap detection key on,
# so it must stay reachable. See build_idf() for why an unweighted score cannot separate these.
MIN_SCORE = 20.0

_TOKEN_RE = re.compile(r"[a-z0-9]+")
_SYN_RE = re.compile(r'"([^"]*)"')


class PhenotypeSearchError(RuntimeError):
    """Raised when the bundled ontology cannot be read or parsed."""


@dataclass(frozen=True)
class Term:
    obo_id: str
    name: str
    synonyms: tuple
    obsolete: bool = False


@dataclass
class Candidate:
    obo_id: str
    label: Optional[str]
    exact: bool               # phrase equals the term's label or an exact synonym
    score: float = 0.0
    obsolete: bool = False    # only ever True when --include-obsolete was passed


@dataclass
class PhenotypeMapping:
    query: str
    status: str                       # matched | no_match | error
    candidates: List[Candidate]
    source: Optional[str]
    retrieved_at: Optional[str]
    release: Optional[str] = None     # the ontology's data-version
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


def _tokens(text: str) -> set:
    return set(_TOKEN_RE.findall(text.lower()))


def load_terms(path: Path = PHIPO_OBO_PATH) -> List[Term]:
    """Parse phipo-base.obo into PHIPO terms, **including obsolete ones**.

    Obsolete terms are kept here and filtered at search time: excluding them at parse would
    reproduce the OLS blind spot this module exists to remove (see the module docstring).
    """
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise PhenotypeSearchError(f"cannot read bundled PHIPO ontology {path}: {exc}")

    terms: List[Term] = []
    in_term = False
    cur: dict = {}

    def flush():
        oid = cur.get("id", "")
        name = cur.get("name", "")
        if not oid.startswith(PHIPO_PREFIX):
            return                       # keep PHIPO only (drop any imported PATO/GO/etc.)
        # PHIPO marks obsoletion two ways: an `is_obsolete: true` line, and an "obsolete "
        # label prefix. Some terms carry only the label form, so check both.
        obsolete = bool(cur.get("obsolete")) or name.lower().startswith("obsolete ")
        terms.append(Term(oid, name, tuple(cur.get("syn", [])), obsolete))

    for line in raw.splitlines():
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
        elif line.startswith("synonym:"):
            m = _SYN_RE.search(line)
            if m:
                cur.setdefault("syn", []).append(m.group(1))
    if in_term and cur:
        flush()
    return terms


def read_release(path: Path = PHIPO_OBO_PATH) -> Optional[str]:
    """The ontology's `data-version` line — provenance for what was actually searched."""
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.startswith("data-version:"):
                return line.split(":", 1)[1].strip()
            if line.startswith("[Term]"):
                break                     # header is over; no data-version present
    except OSError:
        return None
    return None


def build_idf(terms: List[Term]) -> dict:
    """Inverse document frequency per token, over every label + synonym in the ontology.

    Why this is not optional: PHIPO's labels share a lot of generic vocabulary — "to" is in
    39% of labels, "host" 25%, "pathogen" 24%. A plain token-overlap score (map_condition's,
    which this module first borrowed) lets one shared generic word carry a match, so **nothing
    ever returns `no_match`** — and `no_match` is what gap detection and `--log-gaps` key on.
    Weighting by IDF means a term must cover the *informative* part of the query.
    """
    df: dict = {}
    for t in terms:
        seen = set()
        for text in (t.name, *t.synonyms):
            seen |= _tokens(text)
        for tok in seen:
            df[tok] = df.get(tok, 0) + 1
    n = max(len(terms), 1)
    return {tok: math.log(n / c) for tok, c in df.items()}


def _max_idf(idf: dict) -> float:
    """IDF for a token the ontology has never seen — maximally informative, by definition."""
    return max(idf.values(), default=1.0)


def _score(phrase: str, term: Term, idf: dict) -> float:
    """Relevance of a term to a phrase, as **how much of the query's information it covers**.

    Tiers: exact label/synonym (100) > query-inside-label (a real narrowing, 60+) >
    IDF-weighted coverage (0–60). Deliberately simple beyond that: a human reads every
    candidate (lesson L7), so recall matters more than ranking finesse.

    Note the removed tier: the old scorer also matched **label-inside-query**, which let the
    one-word label "phenotype" score 60 against any query containing that word. That is the
    opposite of a narrowing, and it is what stopped `no_match` ever being reachable.
    """
    q = phrase.lower().strip()
    qt = _tokens(phrase)
    if not qt:
        return 0.0
    fallback = _max_idf(idf)
    q_mass = sum(idf.get(t, fallback) for t in qt)
    if q_mass <= 0:
        return 0.0
    best = 0.0
    for text in (term.name, *term.synonyms):
        cl = text.lower().strip()
        if cl == q:
            return 100.0
        tt = _tokens(text)
        shared = qt & tt
        if not shared:
            continue
        cover = sum(idf.get(t, fallback) for t in shared) / q_mass
        s = 60.0 * cover
        if q in cl:
            # The whole query sits inside a longer label: the term is a more specific
            # version of what was asked for. A genuine hit regardless of coverage.
            s = max(s, 60.0 + len(shared))
        best = max(best, s)
    return best


def _is_exact(phrase: str, term: Term) -> bool:
    q = phrase.lower().strip()
    return any(t.lower().strip() == q for t in (term.name, *term.synonyms))


class PhenotypeMapper:
    """Searches the bundled PHIPO release. Terms are loaded once and reused."""

    def __init__(self, terms: Optional[List[Term]] = None,
                 path: Path = PHIPO_OBO_PATH):
        self.path = path
        self._terms = terms
        self._idf: Optional[dict] = None
        self._release: Optional[str] = None if terms is not None else read_release(path)

    @property
    def terms(self) -> List[Term]:
        if self._terms is None:
            self._terms = load_terms(self.path)
        return self._terms

    @property
    def idf(self) -> dict:
        if self._idf is None:
            self._idf = build_idf(self.terms)
        return self._idf

    def map(self, phrase: str, rows: int = DEFAULT_ROWS,
            include_obsolete: bool = False,
            min_score: float = MIN_SCORE) -> PhenotypeMapping:
        phrase = (phrase or "").strip()
        src = str(self.path)
        if not phrase:
            return PhenotypeMapping(phrase, "no_match", [], src, None,
                                    self._release, "empty query")
        try:
            terms, idf = self.terms, self.idf
        except PhenotypeSearchError as exc:
            return PhenotypeMapping(phrase, "error", [], src, utc_now(),
                                    self._release, str(exc))
        candidates = _search(phrase, terms, idf, rows, include_obsolete, min_score)
        status = "matched" if candidates else "no_match"
        return PhenotypeMapping(phrase, status, candidates, src, utc_now(),
                                self._release)


def _search(phrase: str, terms: List[Term], idf: dict, rows: int = DEFAULT_ROWS,
            include_obsolete: bool = False,
            min_score: float = MIN_SCORE) -> List[Candidate]:
    """Score every term, keep the best `rows` above `min_score`. Exact first, then by score.

    Obsolete terms are dropped unless `include_obsolete` — a curator cannot annotate to an
    obsolete term, so suggesting one is wrong; but a *gap* analysis needs to see them (the
    #452 lesson), which is what the flag is for."""
    scored = []
    for t in terms:
        if t.obsolete and not include_obsolete:
            continue
        s = _score(phrase, t, idf)
        if s >= min_score:
            scored.append((s, t))
    # Exact first, then score desc, then id — deterministic for equal scores.
    scored.sort(key=lambda st: (not _is_exact(phrase, st[1]), -st[0], st[1].obo_id))
    return [Candidate(obo_id=t.obo_id, label=t.name, exact=_is_exact(phrase, t),
                      score=round(s, 2), obsolete=t.obsolete)
            for s, t in scored[:rows]]


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
        rel = f" {r.release}" if r.release else ""
        lines.append(f"✅ {r.query}  (offline via phipo-base.obo{rel})")
        for c in r.candidates:
            mark = "★" if c.exact else "•"
            obs = "  ⚠️ OBSOLETE — not annotatable; gap-analysis only" if c.obsolete else ""
            lines.append(f"    {mark} {c.obo_id}  {c.label or ''}{obs}")
    matched = sum(1 for r in results if r.status == "matched")
    lines.append("")
    lines.append(f"{matched}/{len(results)} phrase(s) matched at least one PHIPO term. "
                 "Suggestions only — a curator confirms the term; verify the chosen ID "
                 "with `python3 -m phiweaver.lookup.validate_ontology_ids`.")
    return "\n".join(lines)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(
        description="Map phenotype phrases to candidate PHIPO terms, offline against the "
                    "bundled phipo-base.obo release. Never invents IDs; unmatched phrases "
                    "are reported as no_match.")
    p.add_argument("phrases", nargs="*",
                   help='phenotype description(s), e.g. "reduced virulence"')
    p.add_argument("--file", help="read one phenotype phrase per line from a file")
    p.add_argument("--rows", type=int, default=DEFAULT_ROWS,
                   help=f"max candidate terms per phrase (default {DEFAULT_ROWS}). The "
                        "offline scorer is cruder than OLS's; favour recall over ranking.")
    p.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    p.add_argument("--include-obsolete", action="store_true",
                   help="also return obsolete terms, flagged. NOT for annotation — a curator "
                        "cannot use an obsolete term. This is for gap analysis: OLS hides "
                        "deprecated terms, so a concept that was obsoleted looks like a "
                        "virgin gap (phipo#452 / PHIPO:0000503). See the "
                        "ontology-term-request skill, step 5.")
    p.add_argument("--ontology", default=str(PHIPO_OBO_PATH),
                   help="path to the PHIPO .obo to search (default: the bundled release)")
    p.add_argument("--log-gaps", action="store_true",
                   help="append each no_match to the ontology gap ledger. Use only after "
                        "retrying alternate wordings — an un-retried miss is often a wording "
                        "gap, not a term gap (see the phipo-mapping skill).")
    p.add_argument("--pmid", help="with --log-gaps: the paper that needed the term")
    p.add_argument("--context", help="with --log-gaps: where in the paper, and what was measured")
    p.add_argument("--assay-context", choices=term_context.ASSAY_CONTEXTS,
                   help="where the phenotype was measured. With 'free-living', in-host terms "
                        "are flagged as contextually wrong — a match the search cannot know "
                        "is unusable (see term_context.py, PHI-base/phipo#452).")
    args = p.parse_args(argv)

    phrases: List[str] = list(args.phrases)
    if args.file:
        try:
            phrases.extend(read_phrases(args.file))
        except OSError as exc:
            p.error(f"cannot read --file: {exc}")
    if not phrases:
        p.error("provide one or more phenotype phrases, or --file")

    mapper = PhenotypeMapper(path=Path(args.ontology))
    results = [mapper.map(ph, rows=args.rows, include_obsolete=args.include_obsolete)
               for ph in phrases]

    reviews = [term_context.review(r.candidates, args.assay_context)
               if (args.assay_context and r.candidates) else None
               for r in results]

    if args.log_gaps:
        # Only no_match is auto-recorded. A context-wrong result is *not* auto-recorded as a
        # gap: deciding the surviving candidates are irrelevant needs to know what the paper
        # measured, so --assay-context warns and a curator records the gap deliberately.
        for r in results:
            if r.status == "no_match" and r.query:
                gap_log.record("PHIPO", r.query, pmid=args.pmid, context=args.context)

    if args.json:
        payload = []
        for r, rev in zip(results, reviews):
            d = r.to_dict()
            if rev:
                d["assay_context"] = args.assay_context
                d["candidates"] = term_context.annotate_dicts(r.candidates,
                                                              args.assay_context)
                d["usable_candidates"] = len(rev.usable)
            payload.append(d)
        print(json.dumps(payload, indent=2))
    else:
        print(format_human(results))
        for r, rev in zip(results, reviews):
            if rev and (warning := term_context.format_warning(r.query, rev)):
                print(warning)
    # Exit reflects whether the search ran, not whether it matched: only errors fail.
    return 0 if all(r.ok for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
