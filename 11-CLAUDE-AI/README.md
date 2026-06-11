# 11-CLAUDE-AI/ — Claude-operational material

This folder holds **operational** material for working in this vault with Claude Code — not
the curation engine. The engine is the importable [`phiweaver/`](../phiweaver/README.md)
package (`lookup`, `tracking`, `pipeline`, `pdf`, `common`, `registry`).

## What lives here
- **`SESSION-LOGS/`** — Claude Code session history (read `SESSION-LOGS/INDEX.md` at the
  start of each session).
- **`DEVELOPMENT-TIMELINE.md`** + `generate_dev_timeline.py` / `update_timeline_incremental.py`
  — the development timeline and the tools that build it from the session logs.
- **`AUTOMATION-GUIDE.md`, `CURATION-FILE-ORGANIZATION.md`, `TIMELINE-SYSTEM-GUIDE.md`** —
  operational guides.
- **`obsidian_reorganise.py`** + `reorganise-config-OBS-PHI-Canto.yaml` — a vault-maintenance
  tool (moves notes and updates WikiLinks via the Obsidian CLI), tied to this vault's layout.
- **`db/`** — the tracking-DB file (gitignored) plus thin **compatibility shims**; the DB
  code is in `phiweaver/tracking/`.
- **`curation_pipeline.py`, `convert-for-curation.py`, `pdf-convert-skill/pdf-convert.py`,
  `quick_demo.sh`** — compatibility shims / wrappers; the real code is under `phiweaver/`.

## Why the split
Engine code is tool-agnostic and importable (`phiweaver/`, run-from-root); this folder is
Claude/vault-operational. See `docs/MODULARITY-PLAN.md` (P1, P4).
