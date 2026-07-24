"""PHI-Weaver — AI-assisted biocuration toolkit for PHI-base / PHI-Canto.

Importable package for the tooling engine. It needs no installation: run tools and tests
from the repository root (e.g. ``python3 -m phiweaver.lookup.query_uniprot`` or
``python3 -m unittest discover``) and the repo root is on ``sys.path``. A ``pyproject.toml``
is provided so ``pip install -e .`` also works where allowed (CI, Codespaces, a venv), but
nothing depends on it.

Subpackages:
- ``phiweaver.lookup``   — UniProtKB lookup, ontology-ID validation
- ``phiweaver.tracking`` — SQLite curation-tracking DB + session/reporting tools
- ``phiweaver.pipeline`` — the source→curation orchestration pipeline (dispatches by format)
- ``phiweaver.pdf``      — PDF ingest (PyMuPDF); structure inferred from page layout
- ``phiweaver.jats``     — JATS (NISO Z39.96) journal-XML ingest; structure declared
"""

from pathlib import Path

__all__ = ["repo_root"]


def repo_root(start=None) -> Path:
    """Return the repository root: the nearest ancestor containing ``AGENTS.md``.

    Robust to where modules live in the package, so paths never depend on a fragile
    ``parents[N]`` index.
    """
    p = Path(start or __file__).resolve()
    for parent in (p, *p.parents):
        if (parent / "AGENTS.md").exists():
            return parent
    raise RuntimeError("could not locate repo root (no AGENTS.md found above "
                       f"{p})")
