#!/usr/bin/env python3
"""
phiweaver.figure_ledger — did anyone actually look at the figures?

``figures_inspected: true`` in a draft is an **assertion**, not evidence. Nothing forces
it to be true, and a draft that claims it falsely is worse than one that admits captions
only — it launders a guess as an observation.

This module replaces the boolean with a **ledger**: one entry per figure, saying what was
read from the panel. The claim then becomes auditable, because the ledger is checked
against the converter's own figure roster (``figures`` in ``<stem>_converted_report.json``)
and against the figures the annotations actually cite.

It exists because the difference is not theoretical. On PMID:39852455, re-reading the
panels changed three annotations:

- **Figure 5B** — from its caption ("*, p < 0.05") the cell-wall-thickness effect looked
  marginal. The panel is a labelled nm axis: ~95 → ~45 nm, complementation-rescued.
- **Figure 3** — the hyphal-branching claim looked quantified. The panel quantifies tip
  diameter and septal distance and **never** branching.
- **Figure 4C** — the described lesion difference is not visible at the available
  resolution, so the annotation needed flagging rather than asserting.

Ledger shape, as a top-level ``figure_inspection`` key in the draft's ```json block::

    "figure_inspection": {
      "media_dir": "active/03-Media/PMC11767236",
      "figures": [
        {"label": "Figure 5", "file": "jof-11-00036-g005.jpg", "inspected": true,
         "read": "5B labelled nm axis: WT ~95, sec2D ~45, sec2D-C ~100; *** vs WT, ns vs complement",
         "supports": ["PHIPO:0000379"]}
      ]
    }

An entry with ``inspected: true`` and no ``read`` text is treated as **not inspected** —
ticking a box is not looking at a figure.

Usage (from the repo root):
    python3 -m phiweaver.figure_ledger /path/active/PMID..-phiweaver-DRAFT.md
    python3 -m phiweaver.figure_ledger draft.md --json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional

# "Figure 5A,B" / "Fig 5" / "Figures 3 and 4" -> the figure numbers cited.
_FIGURE_REF_RE = re.compile(r"\bfig(?:ure)?s?\.?\s*(\d+)", re.IGNORECASE)


def normalise_label(label: str) -> str:
    """'Fig 5A' / 'figure 5' / '5' -> 'Figure 5'. Unparseable labels pass through."""
    text = str(label or "").strip()
    if not text:
        return ""
    match = _FIGURE_REF_RE.search(text) or re.match(r"^\s*(\d+)", text)
    return f"Figure {match.group(1)}" if match else text


def figures_cited(text: str) -> List[str]:
    """Every figure a citation string refers to, e.g. 'Figure 5A,B; Figure 7' -> both."""
    seen, out = set(), []
    for number in _FIGURE_REF_RE.findall(str(text or "")):
        label = f"Figure {number}"
        if label not in seen:
            seen.add(label)
            out.append(label)
    return out


def parse_ledger(rec: dict) -> Dict[str, dict]:
    """The draft's ledger, keyed by normalised figure label."""
    block = (rec.get("figure_inspection") or {})
    out = {}
    for entry in block.get("figures") or []:
        label = normalise_label(entry.get("label") or entry.get("file") or "")
        if label:
            out[label] = entry
    return out


def _is_inspected(entry: dict) -> bool:
    """Inspected means a panel was read and something was recorded from it."""
    return bool(entry.get("inspected")) and bool(str(entry.get("read") or "").strip())


def needs_figure(annotation: dict) -> bool:
    """Does this annotation *require* its figure to be read?

    **Policy: decline by default, inspect on cause.** Text and captions carry the
    annotation set itself — on PMID:39852455, inspecting six panels changed zero term
    selections. Reading a figure buys confidence and caveats, not terms, so it is spent
    deliberately rather than by default.

    Mark ``needs_figure: true`` when one of the three causes applies:

    1. the claim is **qualitative** and only the panel can confirm it (histopathology,
       microscopy appearance) — the one case where the image is irreplaceable;
    2. **magnitude decides** the annotation rather than merely describing it (the
       growth-confound convention turns on 2-fold-with-rescue versus marginal);
    3. it is the paper's **take-home message**, where an author's summary and their own
       panel are worth checking against each other.
    """
    return bool(annotation.get("needs_figure"))


def roster_from_report(report: dict) -> List[dict]:
    """The converter's figure roster, if the conversion report carries one."""
    return list((report or {}).get("figures") or [])


def audit(rec: dict, report: Optional[dict] = None) -> dict:
    """Cross-check the ledger against the figure roster and the annotations.

    Reports four failure modes, all of which the old boolean hid:
    ``missing`` (a figure exists but has no ledger entry), ``claimed_not_read``
    (ticked without recorded content), ``unknown`` (a ledger entry for a figure the
    converter never found — usually a typo), and ``annotations_on_uninspected``
    (an annotation resting on a figure nobody opened — the Figure 3 case).
    """
    ledger = parse_ledger(rec)
    roster = roster_from_report(report)

    expected = [normalise_label(f.get("label") or f.get("id") or "") for f in roster]
    expected = [e for e in expected if e]
    not_openable = {normalise_label(f.get("label") or f.get("id") or "")
                    for f in roster if not f.get("openable", True)}

    inspected = sorted(label for label, e in ledger.items() if _is_inspected(e))
    claimed_not_read = sorted(label for label, e in ledger.items()
                              if e.get("inspected") and not _is_inspected(e))
    # A figure deliberately skipped *with a stated reason* is honest, not an error —
    # provided nothing depends on it, which annotations_on_uninspected then checks.
    declined = sorted(label for label, e in ledger.items()
                      if not e.get("inspected") and str(e.get("note") or "").strip())
    missing = sorted(set(expected) - set(ledger))
    unknown = sorted(set(ledger) - set(expected)) if expected else []

    # Two tiers, because the policy is decline-by-default. An annotation explicitly
    # marked needs_figure is a hard requirement; any other annotation citing an
    # un-inspected figure is reported as information only — it keeps the discovery value
    # (this check caught a draft claiming nothing depended on a figure that two GO
    # annotations cited) without turning routine, deliberate declines into warnings.
    required_uninspected, optional_uninspected = [], []
    for ann in ((rec.get("canto") or {}).get("annotations") or []):
        for label in figures_cited(ann.get("figure", "")):
            if label in inspected:
                continue
            item = {
                "term_id": ann.get("term_id", ""),
                "term_name": ann.get("term_name", ""),
                "feature": ann.get("feature", ""),
                "figure": label,
                "reason": ("image not available" if label in not_openable
                           else "figure not inspected"),
                "why_needed": str(ann.get("needs_figure_reason") or ""),
            }
            (required_uninspected if needs_figure(ann)
             else optional_uninspected).append(item)

    total = len(expected) if expected else len(ledger)
    return {
        "has_ledger": bool(ledger),
        "total_figures": total,
        "inspected": inspected,
        "inspected_count": len(inspected),
        "missing": missing,
        "declined": declined,
        "claimed_not_read": claimed_not_read,
        "unknown": unknown,
        "not_openable": sorted(not_openable),
        # Kept under the old key so callers keep working; it now means "required".
        "annotations_on_uninspected": required_uninspected,
        "optional_uninspected": optional_uninspected,
        # Complete means every *required* figure was read. A figure nobody needed and
        # nobody opened is the expected state, not an omission.
        "complete": (bool(ledger) and not claimed_not_read
                     and not required_uninspected),
    }


# --------------------------------------------------------------- inspection budget

# Vision models bill an image at roughly (width x height) / 750 tokens, so the cost of
# reading a figure is knowable *before* reading it. Measured on PMID:39852455: six panels
# cost ~3,550 tokens against ~10,900 for the parsed text — about +33%, worth spending on
# the figures the annotations actually rest on and not on the rest.
_TOKENS_PER_PIXEL_DIVISOR = 750

# Large images are downscaled before they are billed, so raw pixels over-count badly:
# a print-resolution PDF figure at 3.2 MP would look like ~4,300 tokens when it actually
# costs ~1,500. The cap is a long edge of 1568 px and roughly 1.15 megapixels.
_MAX_IMAGE_EDGE = 1568
_MAX_IMAGE_PIXELS = 1_150_000


def image_dimensions(path):
    """``(width, height)`` for a JPEG/PNG/GIF, or ``None``. Header parsing only — stdlib."""
    try:
        with open(path, "rb") as handle:
            data = handle.read(24)
            if data[:2] == b"\xff\xd8":            # JPEG: walk the segment markers
                handle.seek(2)
                blob = handle.read()
                i = 0
                while i < len(blob) - 9:
                    if blob[i] != 0xFF:
                        i += 1
                        continue
                    marker = blob[i + 1]
                    if marker in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7,
                                  0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
                        import struct
                        height, width = struct.unpack(">HH", blob[i + 5:i + 9])
                        return width, height
                    if marker in (0xD8, 0xD9) or 0xD0 <= marker <= 0xD7:
                        i += 2
                        continue
                    import struct
                    (length,) = struct.unpack(">H", blob[i + 2:i + 4])
                    i += 2 + length
                return None
            if data[:8] == b"\x89PNG\r\n\x1a\n":
                import struct
                return struct.unpack(">II", data[16:24])
            if data[:3] == b"GIF":
                import struct
                return struct.unpack("<HH", data[6:10])
    except (OSError, IndexError, ValueError):
        return None
    return None


def estimate_tokens(path) -> int:
    """Rough token cost of showing this image to a vision model; 0 if unmeasurable.

    Models the downscale the API applies before billing, so a print-resolution figure
    extracted from a PDF is priced at what it will actually cost rather than at its
    raw pixel count.
    """
    size = image_dimensions(path)
    if not size:
        return 0
    width, height = size
    if width <= 0 or height <= 0:
        return 0
    scale = min(1.0,
                _MAX_IMAGE_EDGE / max(width, height),
                (_MAX_IMAGE_PIXELS / (width * height)) ** 0.5)
    return round((width * scale) * (height * scale) / _TOKENS_PER_PIXEL_DIVISOR)


def needed_figures(rec: dict, report: Optional[dict] = None) -> dict:
    """Which figures the annotations actually rest on, and what reading them would cost.

    The inspection set is derived from the annotations, not from the figure list: a paper's
    alignment panel or a mechanism-only qRT-PCR figure need not be opened, but anything an
    annotation cites must be. Answering this *before* inspecting is what makes selective
    reading a decision rather than a guess.
    """
    ledger = parse_ledger(rec)
    roster = {normalise_label(f.get("label") or f.get("id") or ""): f
              for f in roster_from_report(report)}

    cited: Dict[str, List[str]] = {}
    for ann in ((rec.get("canto") or {}).get("annotations") or []):
        who = ann.get("term_id") or ann.get("term_name") or ann.get("feature") or "?"
        for label in figures_cited(ann.get("figure", "")):
            cited.setdefault(label, []).append(who)

    required = set()
    for ann in ((rec.get("canto") or {}).get("annotations") or []):
        if needs_figure(ann):
            required.update(figures_cited(ann.get("figure", "")))

    rows, pending_tokens, required_tokens = [], 0, 0
    for label in sorted(cited, key=lambda l: (len(l), l)):
        entry = ledger.get(label, {})
        done = _is_inspected(entry)
        images = (roster.get(label) or {}).get("images_on_disk") or []
        tokens = estimate_tokens(images[0]) if images else 0
        if not done:
            pending_tokens += tokens
            if label in required:
                required_tokens += tokens
        rows.append({
            "figure": label,
            "cited_by": cited[label],
            "inspected": done,
            "required": label in required,
            "image": images[0] if images else "",
            "est_tokens": tokens,
        })

    not_needed = sorted(set(roster) - set(cited), key=lambda l: (len(l), l))
    return {
        "needed": rows,
        "required": [r for r in rows if r["required"] and not r["inspected"]],
        "required_tokens": required_tokens,
        "pending": [r for r in rows if not r["inspected"]],
        "pending_tokens": pending_tokens,
        "not_needed": not_needed,
        "not_needed_tokens": sum(
            estimate_tokens(((roster.get(l) or {}).get("images_on_disk") or [""])[0])
            for l in not_needed),
    }


def summary_line(result: dict) -> str:
    """One markdown line for the entry queue; '' when the draft carries no ledger."""
    if not result.get("has_ledger"):
        return ""
    total = result["total_figures"]
    count = result["inspected_count"]
    problems = []
    if result["claimed_not_read"]:
        problems.append(f"{len(result['claimed_not_read'])} ticked without a reading")
    if result["annotations_on_uninspected"]:
        problems.append(
            f"{len(result['annotations_on_uninspected'])} annotation(s) marked "
            f"needs_figure rest on an un-inspected figure")
    if problems:
        return f"⚠️ **Figures inspected:** {count}/{total} — " + "; ".join(problems)

    # Not a warning: under decline-by-default, curating from text and captions is the
    # normal path. Reported so the reader knows what the draft did and did not look at.
    note = ""
    if result["optional_uninspected"]:
        pending = sorted({i["figure"] for i in result["optional_uninspected"]})
        note = (f" — {len(pending)} cited figure(s) not inspected "
                f"({', '.join(pending)}); text and captions were judged sufficient")
    return f"**Figures inspected:** {count}/{total}{note}"


def figures_inspected_flag(rec: dict, report: Optional[dict] = None):
    """Derive the flag instead of trusting it. ``None`` when no ledger exists."""
    result = audit(rec, report)
    if not result["has_ledger"]:
        return None
    return result["complete"]


# ---------------------------------------------------------------------------- CLI

def _load_draft(path: Path) -> dict:
    from phiweaver.canto.entry_queue import extract_record  # shared json-block parser
    rec = extract_record(Path(path).read_text(encoding="utf-8"))
    if rec is None:
        raise SystemExit(f"no json block found in {path}")
    return rec


def _load_report(draft_path: Path) -> Optional[dict]:
    """The conversion report beside the draft, if the draft names its source file."""
    rec = _load_draft(draft_path)
    source = str((rec.get("meta") or {}).get("source_file") or "")
    if not source:
        return None
    stem = Path(source).stem
    for directory in (draft_path.parent, Path(source).parent):
        candidate = directory / f"{stem}_converted_report.json"
        if candidate.exists():
            try:
                return json.loads(candidate.read_text(encoding="utf-8"))
            except ValueError:
                return None
    return None


def _record_coverage(rec: dict, result: dict, db_path: str = "") -> str:
    """Write the audited coverage to the tracking DB. Never raises — reports instead."""
    try:
        import sqlite3

        from phiweaver import repo_root
        from phiweaver.tracking import ingest_provenance
        from phiweaver.tracking.migrations import run_migrations

        meta = rec.get("meta") or {}
        path = db_path or str(
            repo_root() / "11-CLAUDE-AI" / "db" / "phi_canto_tracking.db")
        conn = sqlite3.connect(path)
        run_migrations(conn)
        # The audited count, not the draft's self-declared boolean.
        ok = ingest_provenance.record(
            conn, pmid=str(meta.get("pmid") or ""),
            route=str(meta.get("source_route") or ""),
            source_file=str(meta.get("source_file") or ""),
            figures_inspected=result["complete"],
            figures_read=result["inspected_count"],
            figures_total=result["total_figures"])
        conn.close()
        return ("📊 recorded coverage in the tracking DB" if ok else
                "⚠️  no matching article row — coverage not recorded")
    except Exception as e:
        return f"⚠️  coverage not recorded: {e}"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Audit a draft's figure-inspection ledger against the figures that exist.")
    parser.add_argument("draft", help="phiweaver draft .md")
    parser.add_argument("--report", default="", help="conversion report JSON (default: auto)")
    parser.add_argument("--json", action="store_true", help="emit the audit as JSON")
    parser.add_argument("--strict", action="store_true",
                        help="exit non-zero unless every figure was inspected")
    parser.add_argument("--needed", action="store_true",
                        help="list only the figures the annotations cite, with the "
                             "estimated token cost of reading the ones still pending")
    parser.add_argument("--record", action="store_true",
                        help="write the coverage to the tracking DB (articles.figures_*)")
    parser.add_argument("--db", default="", help="tracking DB path (default: repo default)")
    args = parser.parse_args(argv)

    draft_path = Path(args.draft)
    rec = _load_draft(draft_path)
    report = (json.loads(Path(args.report).read_text(encoding="utf-8"))
              if args.report else _load_report(draft_path))
    result = audit(rec, report)

    if args.needed:
        plan = needed_figures(rec, report)
        if args.json:
            print(json.dumps(plan, indent=2))
            return 0
        if not plan["needed"]:
            print("No annotation cites a figure — nothing needs inspecting.")
            return 0
        print(f"Figures the annotations rest on ({len(plan['needed'])}):")
        for row in plan["needed"]:
            mark = "✅" if row["inspected"] else ("📖" if row["required"] else "○")
            tier = "REQUIRED" if row["required"] else "optional"
            cost = f"~{row['est_tokens']} tokens" if row["est_tokens"] else "size unknown"
            cited = ", ".join(row["cited_by"][:4]) + (
                f" +{len(row['cited_by']) - 4} more" if len(row["cited_by"]) > 4 else "")
            print(f"  {mark} {row['figure']:<10} {tier:<9} {cost:<16} cited by: {cited}")
        if plan["required"]:
            print(f"\nMUST read: {len(plan['required'])} figure(s) marked needs_figure, "
                  f"~{plan['required_tokens']} tokens.")
        elif plan["pending"]:
            print(f"\nNothing is marked needs_figure. Optional: {len(plan['pending'])} "
                  f"figure(s), ~{plan['pending_tokens']} tokens — "
                  f"decline-by-default says skip unless a claim is qualitative, "
                  f"magnitude-dependent, or the paper's take-home message.")
        else:
            print("\nAll cited figures have been inspected.")
        if plan["not_needed"]:
            print(f"Not cited by any annotation: {', '.join(plan['not_needed'])} "
                  f"(~{plan['not_needed_tokens']} tokens saved by declining them).")
        return 0

    if args.record:
        print(_record_coverage(rec, result, args.db))

    if args.json:
        print(json.dumps(result, indent=2))
        return 0 if result["complete"] or not args.strict else 1

    if not result["has_ledger"]:
        print("⚠️  No figure_inspection ledger — figure claims in this draft rest on "
              "captions unless stated otherwise.")
        return 1 if args.strict else 0

    print(f"Figures inspected: {result['inspected_count']}/{result['total_figures']}")
    for label in result["inspected"]:
        print(f"  ✅ {label}")
    for label in result["declined"]:
        reason = str(parse_ledger(rec).get(label, {}).get("note") or "").strip()
        print(f"  ➖ {label} — deliberately not inspected: {reason}")
    for label in result["missing"]:
        note = " (image not available)" if label in result["not_openable"] else ""
        print(f"  ❌ {label} — no ledger entry{note}")
    for label in result["claimed_not_read"]:
        print(f"  ❌ {label} — marked inspected but nothing was recorded from it")
    for label in result["unknown"]:
        print(f"  ⚠️  {label} — ledger entry for a figure the converter never found")
    for item in result["annotations_on_uninspected"]:
        print(f"  ⚠️  annotation {item['term_id']} ({item['feature']}) cites "
              f"{item['figure']} — {item['reason']}")

    return 0 if result["complete"] or not args.strict else 1


if __name__ == "__main__":
    sys.exit(main())
