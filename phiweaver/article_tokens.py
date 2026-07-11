#!/usr/bin/env python3
"""
phiweaver.article_tokens — attribute a batch-curation session's token spend to each
curated article (PMID), with the shared overhead split explicitly.

Batch curation deliberately curates several papers (say 3, up to ~10) in ONE Claude Code
session so they share the warm context cache. That sharing is the point — but it means the
session transcript is a single stream, and "how many tokens did paper X cost" is not a field
anyone recorded. This module reconstructs it.

How attribution works (no new curator discipline required):
- Claude Code writes every assistant turn to a session transcript (``~/.claude/projects/
  <slug>/<session>.jsonl``) with, per turn, ``message.model`` and ``message.usage`` (fresh
  input, output, cache-creation, cache-read tokens).
- The batch flow already writes one ``*-phiweaver-DRAFT.md`` per paper. So when the agent is
  working on paper X, its tool calls reference X's PMID or X's draft filename. A turn that
  references exactly ONE batch article is attributed to that article ("direct"); a turn that
  references none (setup: loading ontologies, the paper list) or several (cross-article
  reasoning) is "shared".

The token model, kept deliberately simple and honest:
- **work tokens** = fresh input + output + cache-creation. These reflect the incremental
  work of a turn and attribute cleanly to whichever article the turn is about.
- **context re-read** = cache-read tokens. Each turn re-reads the whole accumulated context,
  so by the time paper 3 is curated the re-read also covers papers 1–2. Re-read is a function
  of session *length*, not of any one article, so it is treated as pure overhead and never
  charged to a single paper. (This is the one thing a naive per-article sum gets wrong.)
- **overhead** = shared work tokens + all context re-read. It is split **equally** across the
  N articles (fraction = 1/N), and both N and the fraction are reported so the number is
  auditable. (A ``--weight-by-direct`` option splits it proportionally instead.)

So each article's total = its direct work + (overhead / N).

Citation fields (First author-Year, Title) are joined from the tracking DB
(``phiweaver.tracking`` ``articles`` table) by PMID, falling back to the draft ``meta``.

Pure stdlib. Emits markdown, and optional CSV / JSON.

Usage (from the repo root):
    # articles auto-discovered from the batch's draft files; latest transcript auto-found
    python3 -m phiweaver.article_tokens --drafts active/*-phiweaver-DRAFT.md

    # explicit transcript + explicit PMIDs, write a CSV too
    python3 -m phiweaver.article_tokens session.jsonl --pmid 38234567 --pmid 37123456 --csv out.csv
"""

from __future__ import annotations

import argparse
import csv
import glob
import json
import re
import sqlite3
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Sequence

from phiweaver import repo_root

_JSON_BLOCK = re.compile(r"```json\s*(.*?)```", re.DOTALL)
_PMID_RE = re.compile(r"\b\d{6,9}\b")

# Rough Anthropic list price for Opus-class models, US$ per 1M tokens. Only used for the
# optional cost estimate; override with --price-in / --price-out. Labelled "est." in output.
_DEFAULT_PRICE = {"input": 15.0, "output": 75.0, "cache_write": 18.75, "cache_read": 1.5}


# --------------------------------------------------------------------------- articles

@dataclass
class Article:
    """One curated paper in the batch, with the strings that identify its turns."""
    pmid: str
    label: str = ""            # short paper name from draft meta.paper (fallback title)
    draft_stem: str = ""       # draft filename stem, a strong per-turn reference signal
    model: str = ""            # model recorded in the draft meta, if any
    first_author: str = ""
    year: str = ""
    title: str = ""

    @property
    def keys(self) -> List[str]:
        """Strings whose presence in a turn marks it as being about this article."""
        out = [self.pmid] if self.pmid else []
        if self.draft_stem:
            out.append(self.draft_stem)
        return out

    @property
    def citation(self) -> str:
        """'First author Year', e.g. 'Smith 2024'; falls back to label/pmid."""
        author = self.first_author or (self.label.split()[0] if self.label else "")
        if author and self.year:
            return f"{author} {self.year}"
        return author or self.label or f"PMID:{self.pmid}"


def articles_from_drafts(paths: Sequence[str]) -> List[Article]:
    """Build the article list from batch draft files' ```json meta``` blocks."""
    arts: List[Article] = []
    for p in paths:
        path = Path(p)
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        m = _JSON_BLOCK.search(text)
        meta = {}
        if m:
            try:
                meta = (json.loads(m.group(1)) or {}).get("meta") or {}
            except json.JSONDecodeError:
                meta = {}
        arts.append(Article(
            pmid=str(meta.get("pmid") or "").strip(),
            label=str(meta.get("paper") or path.stem).strip(),
            draft_stem=path.stem,
            model=str(meta.get("model") or "").strip(),
        ))
    return arts


def enrich_from_db(articles: Sequence[Article], db_path: Optional[Path]) -> None:
    """Fill first_author / year / title from the tracking DB's articles table, by PMID.

    Silent no-op if the DB or table is absent, so the tool works with drafts alone.
    """
    if not db_path or not Path(db_path).exists():
        return
    try:
        con = sqlite3.connect(str(db_path))
        con.row_factory = sqlite3.Row
        rows = {str(r["pmid"]): r for r in con.execute(
            "SELECT pmid, title, authors, pub_year FROM articles")}
    except sqlite3.Error:
        return
    finally:
        try:
            con.close()
        except Exception:
            pass
    for a in articles:
        r = rows.get(a.pmid)
        if not r:
            continue
        a.title = r["title"] or a.title or a.label
        a.year = str(r["pub_year"] or "").strip()
        authors = (r["authors"] or "").strip()
        # "Smith et al." / "Smith, Jones" -> "Smith"
        a.first_author = re.split(r"[ ,]", authors)[0] if authors else a.first_author


def default_db_path() -> Optional[Path]:
    """Best-effort location of the tracking SQLite DB; None if not found."""
    for cand in ("phi_canto.db", "phi_canto.sqlite", "tracking.db"):
        p = repo_root() / cand
        if p.exists():
            return p
    hits = list(repo_root().glob("**/*.db"))
    return hits[0] if hits else None


# --------------------------------------------------------------------------- transcript

@dataclass
class Turn:
    model: str
    usage: dict
    blob: str  # text + serialized tool-call inputs, for reference matching


def _turn_blob(message: dict) -> str:
    """Assistant text + tool_use inputs, lowercased, for substring reference matching."""
    parts: List[str] = []
    content = message.get("content")
    if isinstance(content, str):
        parts.append(content)
    elif isinstance(content, list):
        for block in content:
            if not isinstance(block, dict):
                continue
            if block.get("type") == "text":
                parts.append(str(block.get("text", "")))
            elif block.get("type") == "tool_use":
                # file paths, written content, search patterns — the strongest signal
                parts.append(json.dumps(block.get("input", ""), default=str))
    return "\n".join(parts)


def load_turns(jsonl_path: Path) -> List[Turn]:
    """Read assistant turns (those carrying a usage block) from a session transcript."""
    turns: List[Turn] = []
    with open(jsonl_path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            msg = rec.get("message")
            if not isinstance(msg, dict):
                continue
            usage = msg.get("usage")
            if not isinstance(usage, dict):
                continue
            turns.append(Turn(model=msg.get("model", "?"), usage=usage,
                              blob=_turn_blob(msg).lower()))
    return turns


def latest_transcript(slug: Optional[str] = None) -> Optional[Path]:
    """Newest .jsonl transcript for this project under ~/.claude/projects/<slug>/."""
    if slug is None:
        slug = "-" + str(repo_root()).lstrip("/").replace("/", "-")
    proj = Path.home() / ".claude" / "projects" / slug
    files = sorted(proj.glob("*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)
    return files[0] if files else None


# --------------------------------------------------------------------------- attribution

_WORK_KEYS = ("input_tokens", "output_tokens", "cache_creation_input_tokens")


def _work(usage: dict) -> int:
    return sum(int(usage.get(k, 0) or 0) for k in _WORK_KEYS)


def _reread(usage: dict) -> int:
    return int(usage.get("cache_read_input_tokens", 0) or 0)


@dataclass
class Attribution:
    articles: List[Article]
    direct: Dict[str, int]          # pmid -> direct work tokens
    models: Dict[str, set]          # pmid -> models seen on its turns
    shared_work: int
    reread_total: int
    unmatched_turns: int
    matched_turns: int

    @property
    def overhead(self) -> int:
        return self.shared_work + self.reread_total


def attribute(turns: Sequence[Turn], articles: Sequence[Article]) -> Attribution:
    """Assign each turn to one article (direct) or to shared overhead."""
    direct = {a.pmid: 0 for a in articles}
    models: Dict[str, set] = {a.pmid: set() for a in articles}
    shared_work = reread_total = matched = unmatched = 0

    for t in turns:
        reread_total += _reread(t.usage)          # re-read is always overhead
        owners = [a for a in articles if any(k and k.lower() in t.blob for k in a.keys)]
        if len(owners) == 1:
            a = owners[0]
            direct[a.pmid] += _work(t.usage)
            models[a.pmid].add(t.model)
            matched += 1
        else:                                     # 0 or >1 article referenced -> shared
            shared_work += _work(t.usage)
            unmatched += 1

    return Attribution(list(articles), direct, models, shared_work,
                       reread_total, unmatched, matched)


@dataclass
class Row:
    article: Article
    direct: int
    overhead_share: int
    model: str

    @property
    def total(self) -> int:
        return self.direct + self.overhead_share


def build_rows(attr: Attribution, weight_by_direct: bool = False) -> List[Row]:
    """Split overhead across articles and produce one output row each."""
    n = len(attr.articles)
    overhead = attr.overhead
    total_direct = sum(attr.direct.values()) or 1
    rows: List[Row] = []
    for a in attr.articles:
        if weight_by_direct:
            share = round(overhead * attr.direct[a.pmid] / total_direct)
        else:
            share = round(overhead / n) if n else 0
        seen = {m for m in attr.models[a.pmid] if m and m != "?"}
        model = a.model or (sorted(seen)[0] if seen else "?")
        rows.append(Row(a, attr.direct[a.pmid], share, model))
    return rows


def estimate_cost(attr: Attribution, price: dict) -> float:
    """Very rough US$ estimate for the whole batch (all buckets, whole session)."""
    # Only re-read is tracked whole-session here; direct/shared split work tokens but the
    # per-bucket breakdown isn't retained, so this uses aggregate work vs read at blended
    # rates for a balpark figure only.
    work = sum(attr.direct.values()) + attr.shared_work
    return work * price["output"] / 1e6 + attr.reread_total * price["cache_read"] / 1e6


# --------------------------------------------------------------------------- rendering

def render_markdown(rows: Sequence[Row], attr: Attribution, weighted: bool,
                    cost: Optional[float] = None) -> str:
    n = len(rows)
    frac = "weighted by direct work" if weighted else (f"1/{n}" if n else "—")
    lines = [
        "# Batch curation — tokens per article",
        "",
        f"- Articles in batch (N): **{n}**",
        f"- Shared overhead: **{attr.overhead:,}** tokens "
        f"(= {attr.shared_work:,} shared work + {attr.reread_total:,} context re-read)",
        f"- Overhead split: **{frac}** per article"
        + ("" if weighted else f" ≈ {round(attr.overhead / n):,} tokens each" if n else ""),
        f"- Turns attributed directly: {attr.matched_turns} / "
        f"{attr.matched_turns + attr.unmatched_turns}",
        "",
        "| PMID | First author-Year | Title | Model | Direct | Overhead share | Total |",
        "|------|-------------------|-------|-------|-------:|---------------:|------:|",
    ]
    for r in rows:
        title = (r.article.title or r.article.label or "")[:60]
        lines.append(
            f"| {r.article.pmid or '—'} | {r.article.citation} | {title} | {r.model} "
            f"| {r.direct:,} | {r.overhead_share:,} | {r.total:,} |")
    if cost is not None:
        lines += ["", f"_Rough batch cost estimate: **~US${cost:,.2f}** "
                  "(list price, whole session; per-article split not priced separately)._"]
    lines += ["",
              "_Direct = fresh input + output + cache-creation on this paper's turns. "
              "Context re-read (cache-read) is session-cumulative, so it is counted as "
              "shared overhead, not charged to any single paper._"]
    return "\n".join(lines)


def write_csv(rows: Sequence[Row], attr: Attribution, path: Path) -> None:
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["pmid", "first_author_year", "title", "model",
                    "direct_tokens", "overhead_share", "total_tokens",
                    "n_articles", "overhead_total"])
        for r in rows:
            w.writerow([r.article.pmid, r.article.citation,
                        r.article.title or r.article.label, r.model,
                        r.direct, r.overhead_share, r.total,
                        len(rows), attr.overhead])


def rows_to_json(rows: Sequence[Row], attr: Attribution) -> dict:
    return {
        "n_articles": len(rows),
        "overhead_total": attr.overhead,
        "shared_work": attr.shared_work,
        "context_reread": attr.reread_total,
        "articles": [{
            "pmid": r.article.pmid,
            "first_author_year": r.article.citation,
            "title": r.article.title or r.article.label,
            "model": r.model,
            "direct_tokens": r.direct,
            "overhead_share": r.overhead_share,
            "total_tokens": r.total,
        } for r in rows],
    }


# --------------------------------------------------------------------------- CLI

def build_articles(args) -> List[Article]:
    arts: List[Article] = []
    if args.drafts:
        paths: List[str] = []
        for pat in args.drafts:
            paths.extend(glob.glob(pat))
        arts = articles_from_drafts(sorted(set(paths)))
    for pmid in args.pmid or []:
        if pmid not in {a.pmid for a in arts}:
            arts.append(Article(pmid=str(pmid).strip()))
    return arts


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("transcript", nargs="?", help="session .jsonl (default: latest for repo)")
    ap.add_argument("--drafts", nargs="*", help="batch draft file globs (source of PMIDs)")
    ap.add_argument("--pmid", action="append", help="extra PMID(s) to attribute")
    ap.add_argument("--weight-by-direct", action="store_true",
                    help="split overhead proportionally to direct work, not equally")
    ap.add_argument("--db", help="tracking SQLite DB (default: auto-detect)")
    ap.add_argument("--csv", help="also write a CSV to this path")
    ap.add_argument("--json", action="store_true", help="emit JSON instead of markdown")
    ap.add_argument("--cost", action="store_true", help="include a rough $ estimate")
    ap.add_argument("--out", help="write markdown to this path instead of stdout")
    args = ap.parse_args(argv)

    articles = build_articles(args)
    if not articles:
        ap.error("no articles: pass --drafts <glob> and/or --pmid <PMID>")

    db = Path(args.db) if args.db else default_db_path()
    enrich_from_db(articles, db)

    tpath = Path(args.transcript) if args.transcript else latest_transcript()
    if not tpath or not Path(tpath).exists():
        ap.error("no transcript found; pass one explicitly")

    turns = load_turns(Path(tpath))
    attr = attribute(turns, articles)
    rows = build_rows(attr, weight_by_direct=args.weight_by_direct)

    if args.csv:
        write_csv(rows, attr, Path(args.csv))
    if args.json:
        print(json.dumps(rows_to_json(rows, attr), indent=2))
        return 0

    cost = estimate_cost(attr, _DEFAULT_PRICE) if args.cost else None
    md = render_markdown(rows, attr, args.weight_by_direct, cost)
    if args.out:
        Path(args.out).write_text(md + "\n", encoding="utf-8")
        print(f"wrote {args.out}")
    else:
        print(md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
