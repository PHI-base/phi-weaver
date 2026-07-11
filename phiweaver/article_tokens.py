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

    # persist the raw per-article numbers to the tracking DB (for trends over time)
    python3 -m phiweaver.article_tokens --drafts active/*-phiweaver-DRAFT.md --record

    # what did recurating one paper cost across sessions / models?
    python3 -m phiweaver.article_tokens --history 38234567

Persistence (``--record``): only the **raw** components are stored — per-article
``direct_tokens`` plus the session-level ``overhead_total`` + ``n_articles`` — never the
allocated ``1/N`` total, which stays a query so the split policy can change without
invalidating history. Each measurement is keyed by ``(pmid, session_id, model)``: re-running
the reporter on the same transcript upserts the same row (no double-count), while **recurating
a paper in a new session — e.g. with a different model — writes a NEW row**, so both curations
are preserved side by side for cost-vs-model comparison (see ``--history``).

Dollar cost (``--cost``, ``--history``): the four token buckets (input / output / cache-write /
cache-read) are stored separately and priced separately at each row's **model** list rate (see
``PRICES``), so recurating a paper on a cheaper model shows a lower ``$`` for the same token
profile. Prices are estimates recomputed on read, so a rate change never invalidates stored rows.
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

# Bumped when the stored schema/meaning changes, so old rows stay interpretable.
TOOL_VERSION = "article_tokens/2"
# Canonical tracking DB (mirrors phiweaver.tracking.phi_canto_sqlite.DEFAULT_DB_PATH).
CANONICAL_DB = "11-CLAUDE-AI/db/phi_canto_tracking.db"

# Module-owned migration (its own namespace, per phiweaver.tracking.migrations). We store the
# RAW components only — never the allocated 1/N total — so the split policy stays a query.
# (pmid, session_id, model) is unique: same transcript re-run upserts; a recuration in a new
# session (e.g. a different model) is a new row.
_TOKENS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS article_token_costs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pmid TEXT,
    session_id TEXT NOT NULL,
    model TEXT,
    direct_tokens INTEGER DEFAULT 0,
    overhead_total INTEGER DEFAULT 0,
    n_articles INTEGER DEFAULT 0,
    first_author_year TEXT,
    title TEXT,
    tool_version TEXT,
    transcript_path TEXT,
    computed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(pmid, session_id, model)
);
CREATE INDEX IF NOT EXISTS idx_article_token_costs_pmid ON article_token_costs(pmid);
"""

# v2 adds the per-bucket token counts, so dollar cost can be computed per model on read
# (input/output/cache-write/cache-read priced separately). direct_tokens (v1) stays as the
# article's own work total; the bucket columns break it down and split the overhead too.
_TOKENS_TABLE_V2_SQL = """
ALTER TABLE article_token_costs ADD COLUMN direct_input INTEGER DEFAULT 0;
ALTER TABLE article_token_costs ADD COLUMN direct_output INTEGER DEFAULT 0;
ALTER TABLE article_token_costs ADD COLUMN direct_cache_write INTEGER DEFAULT 0;
ALTER TABLE article_token_costs ADD COLUMN overhead_input INTEGER DEFAULT 0;
ALTER TABLE article_token_costs ADD COLUMN overhead_output INTEGER DEFAULT 0;
ALTER TABLE article_token_costs ADD COLUMN overhead_cache_write INTEGER DEFAULT 0;
ALTER TABLE article_token_costs ADD COLUMN overhead_cache_read INTEGER DEFAULT 0;
"""


def _register_migration() -> None:
    """Register this module's schema migrations once (idempotent)."""
    from phiweaver.tracking import migrations
    migrations.register_migrations("article_tokens", [
        ("v1 article_token_costs table", _TOKENS_TABLE_SQL),
        ("v2 per-bucket token columns", _TOKENS_TABLE_V2_SQL),
    ])


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


def default_db_path(must_exist: bool = True) -> Optional[Path]:
    """The canonical tracking SQLite DB under the repo root.

    With ``must_exist`` (the default, for enrichment reads) return it only if present, else a
    legacy fallback, else None. With ``must_exist=False`` (for ``--record``) always return the
    canonical path so a first write can create it.
    """
    canonical = repo_root() / CANONICAL_DB
    if not must_exist or canonical.exists():
        return canonical
    for cand in ("phi_canto.db", "phi_canto.sqlite", "tracking.db"):
        p = repo_root() / cand
        if p.exists():
            return p
    hits = list(repo_root().glob("**/*.db"))
    return hits[0] if hits else None


# --------------------------------------------------------------------------- persistence

def session_id_of(transcript: Path) -> str:
    """Stable per-session key: the transcript's filename stem (Claude Code's session id)."""
    return Path(transcript).stem


def record_to_db(rows: Sequence["Row"], attr: "Attribution", db_path: Path,
                 transcript: Path) -> int:
    """Persist the raw per-article numbers, keyed by (pmid, session_id, model).

    Idempotent per transcript (re-runs upsert the same rows); a recuration in a *new* session
    lands as new rows. Returns the number of rows written. Creates the schema if needed.
    """
    from phiweaver.tracking import migrations
    _register_migration()
    sid = session_id_of(transcript)
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(str(db_path))
    try:
        migrations.run_migrations(con)  # applies core baseline + this table if missing
        ov = attr.overhead_buckets
        for r in rows:
            d = r.direct_buckets
            con.execute(
                "INSERT INTO article_token_costs"
                " (pmid, session_id, model, direct_tokens, overhead_total, n_articles,"
                "  first_author_year, title, tool_version, transcript_path,"
                "  direct_input, direct_output, direct_cache_write,"
                "  overhead_input, overhead_output, overhead_cache_write, overhead_cache_read)"
                " VALUES (?,?,?,?,?,?,?,?,?,?, ?,?,?, ?,?,?,?)"
                " ON CONFLICT(pmid, session_id, model) DO UPDATE SET"
                "  direct_tokens=excluded.direct_tokens,"
                "  overhead_total=excluded.overhead_total,"
                "  n_articles=excluded.n_articles,"
                "  first_author_year=excluded.first_author_year,"
                "  title=excluded.title,"
                "  tool_version=excluded.tool_version,"
                "  transcript_path=excluded.transcript_path,"
                "  direct_input=excluded.direct_input,"
                "  direct_output=excluded.direct_output,"
                "  direct_cache_write=excluded.direct_cache_write,"
                "  overhead_input=excluded.overhead_input,"
                "  overhead_output=excluded.overhead_output,"
                "  overhead_cache_write=excluded.overhead_cache_write,"
                "  overhead_cache_read=excluded.overhead_cache_read,"
                "  computed_at=CURRENT_TIMESTAMP",
                (r.article.pmid, sid, r.model, r.direct, attr.overhead, len(rows),
                 r.article.citation, r.article.title or r.article.label,
                 TOOL_VERSION, str(transcript),
                 d.inp, d.out, d.cache_write,
                 ov.inp, ov.out, ov.cache_write, ov.cache_read))
        con.commit()
        return len(rows)
    finally:
        con.close()


def token_history(db_path: Path, pmid: Optional[str] = None) -> List[dict]:
    """All stored measurements (optionally for one PMID), newest first, with the equal-split
    allocated overhead derived on read (not stored)."""
    from phiweaver.tracking import migrations
    _register_migration()
    con = sqlite3.connect(str(db_path))
    con.row_factory = sqlite3.Row
    try:
        migrations.run_migrations(con)
        sql = "SELECT * FROM article_token_costs"
        args: tuple = ()
        if pmid:
            sql += " WHERE pmid = ?"
            args = (pmid,)
        sql += " ORDER BY computed_at DESC, pmid"
        out = []
        for r in con.execute(sql, args):
            n = r["n_articles"] or 1
            share = round((r["overhead_total"] or 0) / n)
            model = r["model"] or "?"
            # Reconstruct the per-bucket vectors to price each row (equal split on read).
            direct = Buckets(r["direct_input"] or 0, r["direct_output"] or 0,
                             r["direct_cache_write"] or 0)
            ov_share = Buckets(r["overhead_input"] or 0, r["overhead_output"] or 0,
                               r["overhead_cache_write"] or 0,
                               r["overhead_cache_read"] or 0).scaled(1 / n)
            cost = direct.cost(model) + ov_share.cost(model)
            out.append({**dict(r), "overhead_share": share,
                        "total_tokens": (r["direct_tokens"] or 0) + share,
                        "cost_usd": cost})
        return out
    finally:
        con.close()


def render_history(hist: Sequence[dict], pmid: Optional[str]) -> str:
    title = f"# Token history — PMID {pmid}" if pmid else "# Token history — all articles"
    lines = [title, ""]
    if not hist:
        return title + "\n\n_No stored measurements yet (run with --record first)._"
    lines += [
        "| PMID | First author-Year | Model | Session | Direct | Overhead share | Total | Est. $ | When |",
        "|------|-------------------|-------|---------|-------:|---------------:|------:|-------:|------|",
    ]
    for h in hist:
        sid = (h["session_id"] or "")[:8]
        when = (h["computed_at"] or "")[:10]
        cost = f"${h.get('cost_usd', 0):.2f}" if h.get("cost_usd") is not None else "—"
        lines.append(
            f"| {h['pmid'] or '—'} | {h['first_author_year'] or ''} | {h['model'] or '?'} "
            f"| {sid} | {h['direct_tokens']:,} | {h['overhead_share']:,} "
            f"| {h['total_tokens']:,} | {cost} | {when} |")
    if pmid and len({h['model'] for h in hist}) > 1:
        lines += ["", "_Same paper curated by more than one model — rows are directly "
                  "comparable. Direct tokens are the model's own work; overhead share is the "
                  "equal split within each session's batch; est. $ prices each bucket at that "
                  "model's list rate (an estimate)._"]
    return "\n".join(lines)


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


# --------------------------------------------------------------------------- pricing

# Anthropic list price, US$ per 1M tokens. input/output are published rates; cache-write is
# 1.25x input (5-min TTL) and cache-read is 0.1x input (see the claude-api reference). These
# are estimates for reporting — override with --prices <json>. Keyed by model id; "default"
# is used for unknown / "?" models. Source: claude-api skill, 2026-06 model table.
PRICES: Dict[str, dict] = {
    "claude-opus-4-8": {"input": 5.0, "output": 25.0, "cache_write": 6.25, "cache_read": 0.5},
    "claude-fable-5": {"input": 10.0, "output": 50.0, "cache_write": 12.5, "cache_read": 1.0},
    "claude-sonnet-5": {"input": 3.0, "output": 15.0, "cache_write": 3.75, "cache_read": 0.3},
    "claude-haiku-4-5": {"input": 1.0, "output": 5.0, "cache_write": 1.25, "cache_read": 0.1},
}
PRICES["default"] = PRICES["claude-opus-4-8"]


def price_for(model: str, table: Optional[dict] = None) -> dict:
    table = table or PRICES
    return table.get(model) or table.get("default") or PRICES["default"]


# --------------------------------------------------------------------------- attribution

@dataclass
class Buckets:
    """Token counts split by billing bucket (the four Anthropic usage fields)."""
    inp: int = 0            # fresh input_tokens
    out: int = 0            # output_tokens
    cache_write: int = 0    # cache_creation_input_tokens
    cache_read: int = 0     # cache_read_input_tokens (session-cumulative; overhead only)

    def add_work(self, usage: dict) -> None:
        """Accumulate the three 'work' buckets from a usage dict (not cache-read)."""
        self.inp += int(usage.get("input_tokens", 0) or 0)
        self.out += int(usage.get("output_tokens", 0) or 0)
        self.cache_write += int(usage.get("cache_creation_input_tokens", 0) or 0)

    @property
    def work(self) -> int:
        return self.inp + self.out + self.cache_write

    @property
    def total(self) -> int:
        return self.work + self.cache_read

    def scaled(self, factor: float) -> "Buckets":
        return Buckets(round(self.inp * factor), round(self.out * factor),
                       round(self.cache_write * factor), round(self.cache_read * factor))

    def cost(self, model: str, table: Optional[dict] = None) -> float:
        """US$ estimate for these tokens at the given model's per-bucket rate."""
        p = price_for(model, table)
        return (self.inp * p["input"] + self.out * p["output"]
                + self.cache_write * p["cache_write"]
                + self.cache_read * p["cache_read"]) / 1e6


@dataclass
class Attribution:
    articles: List[Article]
    direct_buckets: Dict[str, Buckets]   # pmid -> that paper's own work (cache_read stays 0)
    models: Dict[str, set]               # pmid -> models seen on its turns
    overhead_buckets: Buckets            # shared work + ALL cache-read
    unmatched_turns: int
    matched_turns: int

    # Backward-compatible scalar views (tokens, not $).
    @property
    def direct(self) -> Dict[str, int]:
        return {p: b.work for p, b in self.direct_buckets.items()}

    @property
    def shared_work(self) -> int:
        return self.overhead_buckets.work

    @property
    def reread_total(self) -> int:
        return self.overhead_buckets.cache_read

    @property
    def overhead(self) -> int:
        return self.overhead_buckets.total


def attribute(turns: Sequence[Turn], articles: Sequence[Article]) -> Attribution:
    """Assign each turn to one article (direct) or to shared overhead, per bucket."""
    direct = {a.pmid: Buckets() for a in articles}
    models: Dict[str, set] = {a.pmid: set() for a in articles}
    overhead = Buckets()
    matched = unmatched = 0

    for t in turns:
        overhead.cache_read += int(t.usage.get("cache_read_input_tokens", 0) or 0)  # always overhead
        owners = [a for a in articles if any(k and k.lower() in t.blob for k in a.keys)]
        if len(owners) == 1:
            a = owners[0]
            direct[a.pmid].add_work(t.usage)
            models[a.pmid].add(t.model)
            matched += 1
        else:                                     # 0 or >1 article referenced -> shared
            overhead.add_work(t.usage)
            unmatched += 1

    return Attribution(list(articles), direct, models, overhead, unmatched, matched)


@dataclass
class Row:
    article: Article
    direct_buckets: Buckets
    overhead_share_buckets: Buckets
    model: str

    @property
    def direct(self) -> int:
        return self.direct_buckets.work

    @property
    def overhead_share(self) -> int:
        return self.overhead_share_buckets.total

    @property
    def total(self) -> int:
        return self.direct + self.overhead_share

    def cost(self, table: Optional[dict] = None) -> float:
        return (self.direct_buckets.cost(self.model, table)
                + self.overhead_share_buckets.cost(self.model, table))


def build_rows(attr: Attribution, weight_by_direct: bool = False) -> List[Row]:
    """Split overhead across articles and produce one output row each."""
    n = len(attr.articles)
    total_direct = sum(b.work for b in attr.direct_buckets.values()) or 1
    rows: List[Row] = []
    for a in attr.articles:
        if weight_by_direct:
            factor = attr.direct_buckets[a.pmid].work / total_direct
        else:
            factor = 1 / n if n else 0
        share = attr.overhead_buckets.scaled(factor)
        seen = {m for m in attr.models[a.pmid] if m and m != "?"}
        model = a.model or (sorted(seen)[0] if seen else "?")
        rows.append(Row(a, attr.direct_buckets[a.pmid], share, model))
    return rows


def estimate_cost(attr: Attribution, price: Optional[dict] = None,
                  weight_by_direct: bool = False, table: Optional[dict] = None) -> float:
    """US$ estimate for the whole batch, per-bucket at each article's own model rate."""
    return sum(r.cost(table) for r in build_rows(attr, weight_by_direct))


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
        "| PMID | First author-Year | Title | Model | Direct | Overhead share | Total | Est. $ |",
        "|------|-------------------|-------|-------|-------:|---------------:|------:|-------:|",
    ]
    for r in rows:
        title = (r.article.title or r.article.label or "")[:60]
        lines.append(
            f"| {r.article.pmid or '—'} | {r.article.citation} | {title} | {r.model} "
            f"| {r.direct:,} | {r.overhead_share:,} | {r.total:,} | ${r.cost():.2f} |")
    if cost is not None:
        lines += ["", f"_Rough batch cost estimate: **~US${cost:,.2f}** "
                  "(each bucket priced at its model's list rate — an estimate)._"]
    lines += ["",
              "_Direct = fresh input + output + cache-creation on this paper's turns. "
              "Context re-read (cache-read) is session-cumulative, so it is counted as "
              "shared overhead, not charged to any single paper. Est. $ prices the four "
              "buckets separately at the row's model rate._"]
    return "\n".join(lines)


def write_csv(rows: Sequence[Row], attr: Attribution, path: Path) -> None:
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["pmid", "first_author_year", "title", "model",
                    "direct_tokens", "overhead_share", "total_tokens", "est_cost_usd",
                    "n_articles", "overhead_total"])
        for r in rows:
            w.writerow([r.article.pmid, r.article.citation,
                        r.article.title or r.article.label, r.model,
                        r.direct, r.overhead_share, r.total, round(r.cost(), 4),
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
            "est_cost_usd": round(r.cost(), 4),
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
    ap.add_argument("--db", help="tracking SQLite DB (default: canonical repo DB)")
    ap.add_argument("--csv", help="also write a CSV to this path")
    ap.add_argument("--json", action="store_true", help="emit JSON instead of markdown")
    ap.add_argument("--cost", action="store_true", help="include a rough $ estimate")
    ap.add_argument("--record", action="store_true",
                    help="persist the raw per-article numbers to the tracking DB")
    ap.add_argument("--history", nargs="?", const="", metavar="PMID",
                    help="show stored measurements (optionally for one PMID) and exit")
    ap.add_argument("--out", help="write markdown to this path instead of stdout")
    args = ap.parse_args(argv)

    # --history is a standalone read: no transcript / drafts needed.
    if args.history is not None:
        db = Path(args.db) if args.db else default_db_path(must_exist=False)
        hist = token_history(db, args.history or None)
        print(render_history(hist, args.history or None))
        return 0

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

    if args.record:
        rec_db = Path(args.db) if args.db else default_db_path(must_exist=False)
        written = record_to_db(rows, attr, rec_db, Path(tpath))
        print(f"recorded {written} article(s) to {rec_db} "
              f"(session {session_id_of(tpath)[:8]})")

    if args.csv:
        write_csv(rows, attr, Path(args.csv))
    if args.json:
        print(json.dumps(rows_to_json(rows, attr), indent=2))
        return 0

    cost = estimate_cost(attr, weight_by_direct=args.weight_by_direct) if args.cost else None
    md = render_markdown(rows, attr, args.weight_by_direct, cost)
    if args.out:
        Path(args.out).write_text(md + "\n", encoding="utf-8")
        print(f"wrote {args.out}")
    else:
        print(md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
