#!/usr/bin/env python3
"""
text_score.py — shared phrase → ontology-term relevance scoring.

Used by `map_phenotype` (PHIPO) and `map_condition` (PHI-ECO). Both answer the same question
— *which terms in this ontology are candidates for this phrase?* — over a bundled `.obo`, so
they share one scorer rather than two that drift.

**Why IDF, and not plain token overlap.** The original scorer (exact > substring > Jaccard)
let a single shared *generic* token carry a match. Ontology labels are full of such tokens:
39% of PHIPO labels contain "to", 25% "host", 24% "pathogen". The consequence is not merely
noisy ranking — it is that **`no_match` stops being reachable**, and `no_match` is the signal
gap detection and `--log-gaps` key on (see `ontology-term-request`, and lesson L7's corollary
that gap detection cannot be automated). A scorer that always matches something silently
destroys the ability to notice a missing term.

Weighting by inverse document frequency asks the right question instead: **how much of the
phrase's *information* does this term actually cover?** A term sharing only "to" and "host"
covers almost nothing, however many tokens it has in common.

The tiers, in order:
  100   exact — the phrase equals a label or synonym
  60+   the whole phrase sits inside a longer label (a genuine narrowing: the term is a more
        specific version of what was asked)
  0-60  IDF-weighted coverage of the phrase's informative tokens

Deliberately simple beyond that: a human reads every candidate (lesson L7 — "a surviving
candidate is not a fitting candidate"), so **recall matters more than ranking finesse**. This
is why losing OLS's Solr ranking cost little.

Note the tier that is deliberately *absent*: label-inside-phrase. It let the one-word PHIPO
label "phenotype" score 60 against any phrase containing that word — the opposite of a
narrowing, and the specific reason `no_match` was unreachable.
"""

from __future__ import annotations

import math
import re
from typing import Dict, Iterable, Sequence

_TOKEN_RE = re.compile(r"[a-z0-9]+")


def tokens(text: str) -> set:
    """Lowercase alphanumeric tokens. No stemming — deliberate: a stemmer that collapsed
    'spore'/'sporulation' would need to be right about biology, and being wrong there is worse
    than being crude."""
    return set(_TOKEN_RE.findall((text or "").lower()))


def build_idf(documents: Iterable[Sequence[str]]) -> Dict[str, float]:
    """Inverse document frequency per token.

    `documents` is one iterable of texts per term — its label plus any synonyms. A token is
    counted once per term however many of that term's texts contain it.
    """
    df: Dict[str, int] = {}
    n = 0
    for texts in documents:
        n += 1
        seen: set = set()
        for t in texts:
            seen |= tokens(t)
        for tok in seen:
            df[tok] = df.get(tok, 0) + 1
    if not n:
        return {}
    return {tok: math.log(n / c) for tok, c in df.items()}


def max_idf(idf: Dict[str, float]) -> float:
    """IDF for a token the ontology has never seen — maximally informative, by definition.

    This matters for honesty: a phrase full of words the ontology has never heard of should
    *not* score well just because one generic word happens to overlap."""
    return max(idf.values(), default=1.0)


def score(phrase: str, texts: Sequence[str], idf: Dict[str, float]) -> float:
    """Relevance of one term (given its label + synonyms) to `phrase`. See module docstring."""
    q = (phrase or "").lower().strip()
    qt = tokens(phrase)
    if not qt:
        return 0.0
    fallback = max_idf(idf)
    q_mass = sum(idf.get(t, fallback) for t in qt)
    if q_mass <= 0:
        return 0.0
    best = 0.0
    for text in texts:
        cl = (text or "").lower().strip()
        if cl == q:
            return 100.0
        tt = tokens(text)
        shared = qt & tt
        if not shared:
            continue
        cover = sum(idf.get(t, fallback) for t in shared) / q_mass
        s = 60.0 * cover
        if q in cl:
            # The whole phrase sits inside a longer label: the term is a more specific version
            # of what was asked for. A genuine hit regardless of coverage.
            s = max(s, 60.0 + len(shared))
        best = max(best, s)
    return best


def is_exact(phrase: str, texts: Sequence[str]) -> bool:
    q = (phrase or "").lower().strip()
    return bool(q) and any((t or "").lower().strip() == q for t in texts)
