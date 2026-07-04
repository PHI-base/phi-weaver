#!/usr/bin/env python3
"""
phiweaver.benchmark_report — a shareable HTML report from benchmark scores.

Reads a CSV of per-paper benchmark scores and writes ONE self-contained HTML report (opens in
any browser, no dependencies): headline stats, per-paper accuracy + completeness, an item x paper
heatmap of ratings, the item-level average accuracy ("where to improve"), a curated-vs-control
comparison, and a data table. Pure stdlib.

CSV columns (one row per paper):
    paper, group, curatable, captured, <item1>, <item2>, ...
    group    : "curated" (human-reviewed) or "control" (held-out gold standard)
    ratings  : Correct | Needs improvement | Incorrect | N/A | (empty = not scored)
Anything that is not paper/group/curatable/captured is treated as a scored item column.

Score: Correct = 1, Needs improvement = 0.5, Incorrect = 0; N/A and empty are excluded.
Accuracy = points / applicable items. Completeness = captured / curatable.

Usage:
    python3 -m phiweaver.benchmark_report scores.csv --out benchmark-report.html
"""

from __future__ import annotations

import argparse
import csv
import html
from pathlib import Path
from typing import List, Optional

FIXED = {"paper", "group", "curatable", "captured"}
POINTS = {"correct": 1.0, "needs improvement": 0.5, "incorrect": 0.0}
# status palette: (label, fill, ink). Text label is always shown — never colour alone.
RATING_STYLE = {
    "correct":           ("Correct", "#cfe8d4", "#1f5130"),
    "needs improvement": ("Needs imp.", "#f6e6b8", "#7a5b12"),
    "incorrect":         ("Incorrect", "#f4cdc7", "#8f2c22"),
    "n/a":               ("N/A", "#e6e6e6", "#5b5b5b"),
    "":                  ("—", "#f4f4f4", "#9a9a9a"),
}
ACC_HUE = "#2E5B62"     # accuracy (teal accent)
COMP_HUE = "#3F6FB0"    # completeness (blue accent)


def _pts(rating: str) -> Optional[float]:
    return POINTS.get((rating or "").strip().lower())


class Paper:
    def __init__(self, row: dict, items: List[str]):
        self.name = (row.get("paper") or "").strip()
        self.group = (row.get("group") or "curated").strip().lower()
        self.ratings = {it: (row.get(it) or "").strip() for it in items}
        self.curatable = _int(row.get("curatable"))
        self.captured = _int(row.get("captured"))

    @property
    def applicable(self) -> List[str]:
        return [it for it, r in self.ratings.items() if _pts(r) is not None]

    @property
    def accuracy(self) -> Optional[float]:
        ap = self.applicable
        return sum(_pts(self.ratings[it]) for it in ap) / len(ap) if ap else None

    @property
    def completeness(self) -> Optional[float]:
        return (self.captured / self.curatable) if self.curatable else None


def _int(v) -> int:
    try:
        return int(str(v).strip())
    except (TypeError, ValueError):
        return 0


def load(csv_path) -> "tuple[List[Paper], List[str]]":
    rows = list(csv.DictReader(open(csv_path, encoding="utf-8")))
    if not rows:
        return [], []
    items = [c for c in rows[0].keys() if c and c not in FIXED]
    return [Paper(r, items) for r in rows], items


def _mean(vals) -> Optional[float]:
    vals = [v for v in vals if v is not None]
    return sum(vals) / len(vals) if vals else None


def _pct(v: Optional[float]) -> str:
    return "—" if v is None else f"{round(v * 100)}%"


def item_accuracy(papers: List[Paper], items: List[str]) -> "dict":
    """Average accuracy per item across papers that scored it."""
    out = {}
    for it in items:
        pts = [_pts(p.ratings[it]) for p in papers if _pts(p.ratings.get(it, "")) is not None]
        out[it] = (sum(pts) / len(pts)) if pts else None
    return out


# --------------------------------------------------------------------------- render

def _tile(label, value, sub=""):
    sub = f"<div class='sub'>{html.escape(sub)}</div>" if sub else ""
    return (f"<div class='tile'><div class='val'>{html.escape(str(value))}</div>"
            f"<div class='lbl'>{html.escape(label)}</div>{sub}</div>")


def _bars(papers: List[Paper]) -> str:
    cols = []
    for p in papers:
        acc = p.accuracy or 0.0
        comp = p.completeness or 0.0
        short = html.escape(p.name[:14])
        tag = "control" if p.group == "control" else "curated"
        cols.append(
            f"<div class='pcol {tag}' title='{html.escape(p.name)} ({tag}) — "
            f"accuracy {_pct(p.accuracy)}, completeness {_pct(p.completeness)}'>"
            f"<div class='bars'>"
            f"<div class='bar' style='height:{acc*100:.0f}%;background:{ACC_HUE}'></div>"
            f"<div class='bar' style='height:{comp*100:.0f}%;background:{COMP_HUE}'></div>"
            f"</div><div class='pname'>{short}</div></div>")
    legend = (f"<div class='legend'>"
              f"<span><i style='background:{ACC_HUE}'></i>Accuracy</span>"
              f"<span><i style='background:{COMP_HUE}'></i>Completeness</span></div>")
    return f"{legend}<div class='barchart'>{''.join(cols)}</div>"


def _heatmap(papers: List[Paper], items: List[str]) -> str:
    head = "".join(f"<th title='{html.escape(p.name)}'>{html.escape(p.name[:10])}</th>"
                   for p in papers)
    rows = []
    for it in items:
        cells = []
        for p in papers:
            r = (p.ratings.get(it, "") or "").strip().lower()
            label, fill, ink = RATING_STYLE.get(r, RATING_STYLE["n/a"])
            cells.append(f"<td style='background:{fill};color:{ink}' "
                         f"title='{html.escape(p.name)} — {html.escape(it)}: {label}'>"
                         f"{html.escape(label)}</td>")
        rows.append(f"<tr><th class='rowlbl'>{html.escape(it)}</th>{''.join(cells)}</tr>")
    return (f"<div class='scroll'><table class='heat'><thead><tr><th></th>{head}</tr></thead>"
            f"<tbody>{''.join(rows)}</tbody></table></div>")


def _item_accuracy(papers: List[Paper], items: List[str]) -> str:
    ia = item_accuracy(papers, items)
    rows = []
    for it in items:
        v = ia[it]
        w = (v or 0) * 100
        rows.append(f"<div class='hrow'><div class='hlbl'>{html.escape(it)}</div>"
                    f"<div class='htrack'><div class='hbar' style='width:{w:.0f}%'></div></div>"
                    f"<div class='hval'>{_pct(v)}</div></div>")
    return f"<div class='hbars'>{''.join(rows)}</div>"


def _table(papers: List[Paper], items: List[str]) -> str:
    head = "".join(f"<th>{html.escape(it[:12])}</th>" for it in items)
    rows = []
    for p in papers:
        cells = "".join(f"<td>{html.escape(p.ratings.get(it, '') or '—')}</td>" for it in items)
        rows.append(f"<tr><td>{html.escape(p.name)}</td><td>{html.escape(p.group)}</td>"
                    f"<td>{_pct(p.accuracy)}</td><td>{_pct(p.completeness)}</td>{cells}</tr>")
    return (f"<div class='scroll'><table class='data'><thead><tr>"
            f"<th>Paper</th><th>Group</th><th>Acc</th><th>Compl</th>{head}</tr></thead>"
            f"<tbody>{''.join(rows)}</tbody></table></div>")


def render_html(papers: List[Paper], items: List[str], title="Benchmark report") -> str:
    curated = [p for p in papers if p.group != "control"]
    control = [p for p in papers if p.group == "control"]
    tiles = [
        _tile("papers", len(papers), f"{len(curated)} curated · {len(control)} control"),
        _tile("mean accuracy (curated)", _pct(_mean(p.accuracy for p in curated))),
        _tile("mean completeness (curated)", _pct(_mean(p.completeness for p in curated))),
    ]
    if control:
        tiles += [
            _tile("mean accuracy (control)", _pct(_mean(p.accuracy for p in control)),
                  "held-out gold standards"),
            _tile("mean completeness (control)", _pct(_mean(p.completeness for p in control))),
        ]
    ordered = curated + control
    css = """
    :root{--ink:#1F2A33;--muted:#5b6b73;--surf:#fff;--band:#eef2f2;--line:#d7e0e0;}
    *{box-sizing:border-box} body{margin:0;font:15px/1.5 -apple-system,Segoe UI,Roboto,sans-serif;
      color:var(--ink);background:#f6f8f8;padding:24px;font-variant-numeric:tabular-nums}
    h1{font-size:22px;margin:0 0 2px} .meta{color:var(--muted);margin:0 0 20px}
    h2{font-size:15px;letter-spacing:.04em;text-transform:uppercase;color:var(--muted);
      margin:28px 0 10px;border-bottom:1px solid var(--line);padding-bottom:6px}
    .tiles{display:flex;flex-wrap:wrap;gap:12px}
    .tile{background:var(--surf);border:1px solid var(--line);border-radius:10px;padding:14px 16px;min-width:150px}
    .tile .val{font-size:26px;font-weight:650} .tile .lbl{color:var(--muted);font-size:13px}
    .tile .sub{color:var(--muted);font-size:12px;margin-top:2px}
    .legend{display:flex;gap:16px;color:var(--muted);font-size:13px;margin-bottom:8px}
    .legend i{display:inline-block;width:11px;height:11px;border-radius:2px;margin-right:5px;vertical-align:middle}
    .barchart{display:flex;gap:10px;align-items:flex-end;height:200px;overflow-x:auto;
      border-bottom:1px solid var(--line);padding-bottom:0}
    .pcol{display:flex;flex-direction:column;align-items:center;min-width:42px}
    .pcol.control{background:#f0ede6;border-radius:6px 6px 0 0}
    .bars{display:flex;gap:3px;align-items:flex-end;height:170px}
    .bar{width:12px;border-radius:3px 3px 0 0}
    .pname{font-size:10px;color:var(--muted);margin-top:4px;max-width:44px;overflow:hidden;
      text-overflow:ellipsis;white-space:nowrap}
    .scroll{overflow-x:auto}
    table{border-collapse:collapse;font-size:13px} .heat td,.heat th{border:2px solid #fff;
      padding:5px 7px;text-align:center;white-space:nowrap} .heat .rowlbl,.heat thead th{
      background:var(--band);color:var(--ink);text-align:left;font-weight:600}
    .hbars{display:flex;flex-direction:column;gap:6px;max-width:640px}
    .hrow{display:flex;align-items:center;gap:10px}
    .hlbl{width:190px;color:var(--ink);font-size:13px;text-align:right}
    .htrack{flex:1;background:var(--band);border-radius:4px;height:16px}
    .hbar{height:16px;background:#2E5B62;border-radius:4px}
    .hval{width:44px;color:var(--muted);font-size:13px}
    .data td,.data th{border:1px solid var(--line);padding:4px 8px;text-align:left;white-space:nowrap}
    .data thead th{background:var(--band)}
    @media(prefers-color-scheme:dark){
      body{background:#12181b;color:#e7edee} .tile,.data thead th,.heat thead th,.heat .rowlbl{
        background:#1b2327;border-color:#2b363b} .tile{border-color:#2b363b}
      :root{--surf:#1b2327;--band:#232d31;--line:#2b363b;--muted:#9fb0b6}
    }
    """
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title><style>{css}</style></head><body>
<h1>{html.escape(title)}</h1>
<p class="meta">phiweaver curation benchmark · {len(papers)} paper(s) ·
scores against gold standards (blind, leakage-free).</p>
<div class="tiles">{''.join(tiles)}</div>
<h2>Accuracy &amp; completeness per paper</h2>{_bars(ordered)}
<h2>Ratings by item and paper</h2>{_heatmap(ordered, items)}
<h2>Average accuracy per item (where to improve)</h2>{_item_accuracy(papers, items)}
<h2>Data</h2>{_table(ordered, items)}
</body></html>"""


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Build a shareable HTML benchmark report from a scores CSV.")
    ap.add_argument("csv", help="per-paper scores CSV (see module docstring for columns)")
    ap.add_argument("--out", default="benchmark-report.html", help="output HTML path")
    ap.add_argument("--title", default="Benchmark report")
    args = ap.parse_args(argv)
    papers, items = load(args.csv)
    if not papers:
        raise SystemExit(f"no rows in {args.csv}")
    Path(args.out).write_text(render_html(papers, items, args.title), encoding="utf-8")
    print(f"wrote {args.out} ({len(papers)} paper(s), {len(items)} item(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
