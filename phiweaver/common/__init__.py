"""Shared *module envelope* — the contract every phiweaver tool follows.

A tool returns a structured result carrying a ``status``, its payload, and **provenance**
(source, cache hit/miss, UTC timestamp); emits ``--json`` for machines and a human summary
otherwise; exits ``0`` on success / ``1`` on failure; and takes an **injectable I/O**
callable (an HTTP getter or DB handle) so tests run offline and deterministically. It
**never guesses** — ambiguity and "not found" are explicit statuses, never invented data.

This package provides the reusable pieces of that envelope so tools don't re-implement
them: a UTC timestamp, a lazy ``requests`` getter factory, and a tiny SQLite response cache.
See ``docs/ADDING-A-MODULE.md`` for how to build a new module on top of this.
"""

from __future__ import annotations

import json
import sqlite3
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Optional

__all__ = ["utc_now", "git_commit", "provenance_line", "make_getter", "ResponseCache"]


def utc_now() -> str:
    """An ISO-8601 UTC timestamp (seconds precision) for provenance stamps."""
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def git_commit() -> Optional[str]:
    """The framework's current short git revision, or ``None`` if unavailable.

    This is phiweaver's real *version number*: one token that pins the rules and examples
    that produced an output (reproduce by checking out this commit + rerunning the model).
    Resolved against the package's own repo, so it is correct regardless of the caller's cwd.
    """
    repo = Path(__file__).resolve().parents[2]   # phiweaver/common/__init__.py -> repo root
    try:
        r = subprocess.run(["git", "-C", str(repo), "rev-parse", "--short", "HEAD"],
                           capture_output=True, text=True, timeout=5)
    except (OSError, subprocess.SubprocessError):
        return None
    return r.stdout.strip() or None if r.returncode == 0 else None


def provenance_line(model: Optional[str] = None, date: Optional[str] = None) -> str:
    """One-line provenance stamp for a generated output: tool + model · commit · date.

    ``model`` and ``date`` come from the draft's ``meta`` when present; the commit is the
    framework's current revision. Missing pieces are simply omitted — the stamp never invents
    a value. ``date`` falls back to today (render date) only when the draft carries none.
    """
    parts = [f"phiweaver · {model}" if model else "phiweaver"]
    commit = git_commit()
    if commit:
        parts.append(f"commit {commit}")
    parts.append(f"date {date}" if date else f"date {utc_now()[:10]}")
    return " · ".join(parts)


def make_getter(user_agent: str, accept: str = "application/json",
                timeout: int = 30) -> Callable:
    """Return an HTTP getter ``(url, params) -> (status, json_or_None, headers)``.

    ``requests`` is imported lazily so a module loads and **tests** without it installed.
    The getter is injectable, so tests pass a fake instead of touching the network.
    """
    def _get(url: str, params: dict):
        import requests

        resp = requests.get(
            url, params=params, timeout=timeout,
            headers={"User-Agent": user_agent, "Accept": accept})
        try:
            body = resp.json()
        except ValueError:
            body = None
        return resp.status_code, body, dict(resp.headers)

    return _get


class ResponseCache:
    """Tiny SQLite cache of raw JSON responses, keyed by request signature.

    Optionally stores a small ``meta`` dict alongside each payload (e.g. a dataset
    release stamp). Speeds reruns and freezes results within a run.
    """

    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(self.path))
        self._conn.execute(
            "CREATE TABLE IF NOT EXISTS responses ("
            " key TEXT PRIMARY KEY, payload TEXT NOT NULL, meta TEXT, cached_at TEXT)")
        self._conn.commit()

    def get(self, key: str):
        row = self._conn.execute(
            "SELECT payload, meta, cached_at FROM responses WHERE key = ?", (key,)
        ).fetchone()
        if not row:
            return None
        return {"payload": json.loads(row[0]),
                "meta": json.loads(row[1]) if row[1] else {},
                "cached_at": row[2]}

    def put(self, key: str, payload: dict, meta: Optional[dict] = None):
        self._conn.execute(
            "INSERT OR REPLACE INTO responses (key, payload, meta, cached_at)"
            " VALUES (?, ?, ?, ?)",
            (key, json.dumps(payload), json.dumps(meta) if meta else None, utc_now()))
        self._conn.commit()

    def close(self):
        self._conn.close()
