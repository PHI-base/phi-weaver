#!/usr/bin/env python3
"""
term_context.py — flag PHIPO candidate terms whose *context* contradicts the assay.

A phenotype search can return a term that is lexically right and contextually wrong, and
nothing in the result marks it. The real case: PMID:42089373 measures DON in free-living
culture, "absent DON" searches cleanly, and the top hit is PHIPO:0000234 *pathogen
deoxynivalenol within host absent* — an in-host term, useless for an in-vitro assay. A
curator sees a confident match and can annotate the wrong term. This is the failure that
`no_match` cannot catch, because there *was* a match (see PHI-base/phipo#452).

It is catchable because PHIPO states context in the label. The DON branch splits cleanly:

    in-host       PHIPO:0000233/0000234  pathogen deoxynivalenol *within host* present/absent
    free-living   PHIPO:0001445/0001447  decreased / increased *level of deoxynivalenol*

and the free-living side has no "absent" term at all — which *is* gap #452. The same split
runs through growth (`within host` / `on host surface` vs plain `hyphal growth`).

**The rule:** a label mentioning "host" is an in-host term. Verified against PHIPO before
relying on it — searches for "host-free", "axenic" and "free-living" all return no_match, so
no label negates the word (a term like "growth in host-free medium" would defeat this). The
"absence of host X" terms are in-host phenotypes in which a host response is absent, so they
classify correctly too. Re-check this rule if PHIPO ever gains a host-negating label.

**Only one direction is flagged.** A free-living assay cannot use an in-host term — that is a
hard contradiction. The reverse is not: terms without a host marker ("decreased hyphal
growth") are context-neutral and an in-host assay may legitimately use them. So a term is
classified `in-host` or `unspecified`, never `free-living`, and the flag fires on exactly one
combination. Anything more would need to know what the assay measured, which is the curator's
judgement, not a regex's.

**What this does NOT do: find gaps automatically.** The tempting inference — "every candidate
is context-wrong, therefore the term is missing" — is unreliable, and measurably so. Searching
"absent DON" for a free-living assay returns four in-host terms *and* PHIPO:0000939 *asexual
spore lysis absent*: lexical noise off the word "absent", irrelevant to DON, but carrying no
host marker, so it counts as usable and `all_mismatched` stays False. One irrelevant neutral
candidate masks the gap — including on #452, the case this module was built for. So
`all_mismatched` has high precision but low recall, and is used only to sharpen the warning's
wording, never to record a gap.

Judging that the surviving candidates are *irrelevant* — and that the term is therefore
genuinely missing — requires knowing what the paper measured. That is the curator's call. This
module flags the contradiction and says what to check; a human decides whether it is a gap.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Optional, Sequence, Tuple

# The assay context a curator declares. There is deliberately no "unknown": if you don't know
# where the phenotype was measured, you are not ready to pick a term.
ASSAY_CONTEXTS = ("free-living", "in-host")

IN_HOST = "in-host"
UNSPECIFIED = "unspecified"

# Word-boundary "host" also catches "host-defense", "within host", "host surface".
_HOST_RE = re.compile(r"\bhost\b", re.IGNORECASE)


def classify_term(label: Optional[str]) -> str:
    """`in-host` if the term's label commits it to a host context, else `unspecified`.

    Never returns "free-living": an unmarked label is context-neutral, not host-free."""
    if not label:
        return UNSPECIFIED
    return IN_HOST if _HOST_RE.search(label) else UNSPECIFIED


def is_mismatched(label: Optional[str], assay_context: str) -> bool:
    """True only for the contradiction: an in-host term offered for a free-living assay."""
    if assay_context not in ASSAY_CONTEXTS:
        raise ValueError(f"unknown assay context {assay_context!r}; expected one of "
                         f"{', '.join(ASSAY_CONTEXTS)}")
    return assay_context == "free-living" and classify_term(label) == IN_HOST


@dataclass
class ContextReview:
    usable: List                 # candidates whose context does not contradict the assay
    mismatched: List             # in-host candidates offered for a free-living assay
    assay_context: str

    @property
    def all_mismatched(self) -> bool:
        """Every candidate is context-wrong, so nothing the search returned is usable.

        Suggestive of a term gap, but not evidence of one, and not a gap detector: a single
        irrelevant host-free candidate keeps this False even when the term really is missing
        (see the module docstring). Used only to word the warning more strongly."""
        return bool(self.mismatched) and not self.usable


def review(candidates: Sequence, assay_context: str) -> ContextReview:
    """Split candidates by whether their context contradicts the declared assay context.

    Takes anything with a ``.label`` (map_phenotype's Candidate), so it stays usable from the
    mapper without the mapper knowing about this module's types."""
    usable, bad = [], []
    for c in candidates:
        (bad if is_mismatched(getattr(c, "label", None), assay_context) else usable).append(c)
    return ContextReview(usable=usable, mismatched=bad, assay_context=assay_context)


def _describe(candidates: Sequence) -> str:
    return ", ".join(f"{getattr(c, 'obo_id', '?')} {getattr(c, 'label', '')}"
                     for c in candidates)


def format_warning(phrase: str, r: ContextReview) -> Optional[str]:
    """A human warning for a context problem, or None when there is nothing to say.

    Always ends by pointing at the surviving candidates, because that is where the judgement
    lives: the search happily pads a result with terms that merely share a word, and a curator
    who assumes the remainder must fit is exactly how a #452-shaped gap goes unnoticed."""
    if not r.mismatched:
        return None
    record_hint = (f"    python3 -m phiweaver.lookup.gap_log record PHIPO {phrase!r} "
                   f"--pmid <PMID> --context <where + what was measured>")
    if r.all_mismatched:
        return (f"⚠️  {phrase}: every candidate is an in-host term, but the assay is "
                f"free-living — nothing here is usable ({_describe(r.mismatched)}).\n"
                f"    Retry alternate wordings; if still nothing fits, record the gap:\n"
                f"{record_hint}")
    return (f"⚠️  {phrase}: {len(r.mismatched)} in-host candidate(s) are wrong for a "
            f"free-living assay — {_describe(r.mismatched)}.\n"
            f"    Now check the {len(r.usable)} remaining candidate(s) actually fit the "
            f"phenotype: {_describe(r.usable)}.\n"
            f"    A search result can share a word without sharing a meaning. If none of them "
            f"fit, this is a term gap the search cannot report as no_match — record it:\n"
            f"{record_hint}")


def annotate_dicts(candidates: Sequence, assay_context: str) -> List[dict]:
    """Candidates as JSON-ready dicts, each tagged with its context verdict."""
    out = []
    for c in candidates:
        label = getattr(c, "label", None)
        out.append({"obo_id": getattr(c, "obo_id", None), "label": label,
                    "term_context": classify_term(label),
                    "context_mismatch": is_mismatched(label, assay_context)})
    return out
