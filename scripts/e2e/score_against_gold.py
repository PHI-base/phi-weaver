#!/usr/bin/env python3
"""
score_against_gold.py — deterministic ID-overlap score of a phiweaver draft vs a gold standard.

The cheap, objective half of an end-to-end curation test: it does NOT judge curation nuance,
it measures how well the identifiers a draft asserts (PHIPO / GO / PHIDO / FYPO / PECO /
UniProtKB) overlap the ones in the known-correct curation. Precision = did the draft avoid
inventing IDs; recall = did it find the IDs the gold standard has. Stdlib only, network-free,
so it runs anywhere and in CI. Exit code is the pass/fail (overall F1 >= threshold).

    python3 score_against_gold.py <draft.md> <gold.md>
    python3 score_against_gold.py <draft.md> <gold.md> --threshold 0.5 --json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# Namespaces that identify a curated assertion. UniProt/UniProtKB are folded together.
_ID_RE = re.compile(r"\b(PHIPO|GO|PHIDO|FYPO|PECO|UniProtKB|UniProt):([A-Za-z0-9]+)\b")
# Markdown emphasis/code markers can sit between the prefix colon and the id
# (e.g. `UniProtKB:**A0A1C3YKU0**`); strip them so formatting can't hide a real id.
_EMPHASIS_RE = re.compile(r"[*`]+")


def extract_ids(text: str) -> set[str]:
    """The distinct, normalised identifiers asserted in a curation document."""
    text = _EMPHASIS_RE.sub("", text)
    ids = set()
    for ns, local in _ID_RE.findall(text):
        ns = "UniProtKB" if ns.lower().startswith("uniprot") else ns.upper()
        ids.add(f"{ns}:{local.upper()}")
    return ids


def _prf(pred: set[str], gold: set[str]) -> dict:
    tp = len(pred & gold)
    precision = tp / len(pred) if pred else 0.0
    recall = tp / len(gold) if gold else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0
    return {"tp": tp, "pred": len(pred), "gold": len(gold),
            "precision": precision, "recall": recall, "f1": f1}


def score(draft_text: str, gold_text: str) -> dict:
    pred, gold = extract_ids(draft_text), extract_ids(gold_text)
    namespaces = sorted({i.split(":", 1)[0] for i in pred | gold})
    per_ns = {ns: _prf({i for i in pred if i.startswith(ns + ":")},
                       {i for i in gold if i.startswith(ns + ":")})
              for ns in namespaces}
    overall = _prf(pred, gold)
    overall["missed"] = sorted(gold - pred)     # in gold, absent from draft (recall misses)
    overall["spurious"] = sorted(pred - gold)   # in draft, absent from gold (precision misses)
    return {"overall": overall, "per_namespace": per_ns}


def _fmt(row: dict) -> str:
    return (f"P {row['precision']:.2f}  R {row['recall']:.2f}  F1 {row['f1']:.2f}   "
            f"({row['tp']}/{row['pred']} pred, {row['tp']}/{row['gold']} gold)")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("draft")
    ap.add_argument("gold")
    ap.add_argument("--threshold", type=float, default=0.5,
                    help="minimum overall F1 to pass (default 0.5)")
    ap.add_argument("--json", action="store_true", help="emit the full result as JSON")
    args = ap.parse_args(argv)

    draft_text = Path(args.draft).read_text(encoding="utf-8")
    gold_text = Path(args.gold).read_text(encoding="utf-8")
    result = score(draft_text, gold_text)
    ov = result["overall"]

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"draft: {args.draft}")
        print(f"gold:  {args.gold}\n")
        for ns, row in result["per_namespace"].items():
            print(f"  {ns:<11} {_fmt(row)}")
        print(f"\n  {'OVERALL':<11} {_fmt(ov)}")
        if ov["missed"]:
            print(f"\n  missed (in gold, not in draft): {', '.join(ov['missed'])}")
        if ov["spurious"]:
            print(f"  spurious (in draft, not in gold): {', '.join(ov['spurious'])}")

    passed = ov["f1"] >= args.threshold
    print(f"\n{'PASS' if passed else 'FAIL'} — overall F1 {ov['f1']:.2f} "
          f"(threshold {args.threshold:.2f})", file=sys.stderr)
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
