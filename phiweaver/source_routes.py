#!/usr/bin/env python3
"""
phiweaver.source_routes — how a paper reached a curation, and what that route could show.

One shared vocabulary for the ingest route, used by the curation outputs (the draft header
and the PHI-Canto entry queue) **and** the tracking database, so a route recorded in one
place cannot drift from the other.

This is not bookkeeping. On PMID:39852455 the route changed three annotations:

- Read from a **publisher JATS XML**, which names image files it does not ship, figure
  content is captions only. A cell-wall-thickness measurement looked like a marginal
  ``p < 0.05``; a hyphal-branching claim looked quantified.
- Re-acquired from **Europe PMC** with the figure images, the thickness effect turned out
  to be a rescued ~2-fold change (~95 → ~45 nm) and the branching claim turned out never
  to have been quantified at all.

A curator reading a draft therefore needs to know which of those they are holding, which
is why every output states it before the first table.

The route names are the stored vocabulary — treat them as append-only.
"""

from __future__ import annotations

from pathlib import Path

# route -> (human label, what the route implies about figure evidence)
SOURCE_ROUTES = {
    "pdf": ("PDF", "figures embedded in the source and extracted"),
    "jats-publisher": ("publisher JATS XML",
                       "figures are CAPTIONS ONLY unless supplied separately"),
    "jats-europepmc": ("Europe PMC JATS XML", "full text + figure images retrieved"),
}

# Legacy/alias spellings accepted on read, normalised to the vocabulary above.
_ALIASES = {
    "europepmc-jats-with-figures": "jats-europepmc",
    "europepmc": "jats-europepmc",
    "jats": "jats-publisher",
    "xml": "jats-publisher",
}

_ROUTE_BY_SUFFIX = {
    ".pdf": "pdf",
    ".xml": "jats-publisher",
    ".jats": "jats-publisher",
    ".nxml": "jats-europepmc",   # PMC's own extension for its normalised full text
}


def normalise_route(route: str) -> str:
    """Map an alias to the stored vocabulary; unknown values pass through unchanged."""
    value = (route or "").strip().lower()
    return _ALIASES.get(value, value)


def route_from_filename(filename) -> str:
    """Infer the route from a source filename's extension, or '' if unrecognised."""
    if not filename:
        return ""
    return _ROUTE_BY_SUFFIX.get(Path(str(filename)).suffix.lower(), "")


def resolve_route(meta: dict) -> str:
    """The route a draft's ``meta`` block records, explicitly or by its source filename."""
    return (normalise_route(str(meta.get("source_route") or ""))
            or route_from_filename(meta.get("source_file")))


def figures_available(route: str, figures_inspected=None) -> bool:
    """Whether figure panels were readable.

    An explicit ``figures_inspected`` always wins: a publisher XML whose images were
    fetched separately is no longer captions-only, and a Europe PMC fetch whose zip failed
    is not as rich as its route suggests.
    """
    if figures_inspected is not None:
        return bool(figures_inspected)
    return normalise_route(route) in ("pdf", "jats-europepmc")


def describe_source(meta: dict) -> str:
    """One markdown line naming the source artefact and its figure evidence.

    Returns ``""`` when a draft records nothing — an unrecorded route is reported as
    unrecorded, never guessed.
    """
    route = resolve_route(meta)
    source_file = str(meta.get("source_file") or "")
    label, figure_note = SOURCE_ROUTES.get(route, ("", ""))

    if not label:
        if not source_file:
            return ""
        label, figure_note = f"`{Path(source_file).name}`", "route not recorded"
        name = ""
    else:
        name = f" (`{Path(source_file).name}`)" if source_file else ""

    inspected = meta.get("figures_inspected")
    if inspected is True:
        figure_note = "figure panels inspected"
    elif inspected is False:
        figure_note = "figures NOT inspected — captions only"

    warn = "⚠️ " if ("ONLY" in figure_note or "NOT" in figure_note
                    or "not recorded" in figure_note) else ""
    return f"{warn}**Curated from:** {label}{name} — {figure_note}"
