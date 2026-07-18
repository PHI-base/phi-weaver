# 11-CLAUDE-AI/ — Claude-operational material

This folder holds **operational** material for working in this vault with Claude Code — not
the curation engine. The engine is the importable [`phiweaver/`](../phiweaver/README.md)
package (`lookup`, `tracking`, `pipeline`, `pdf`, `common`, `registry`).

## What lives here
- **`SESSION-LOGS/`** — Claude Code session history (read `SESSION-LOGS/Session-Logs-INDEX.md` at the
  start of each session).
- **`vault-ops/`** — the **vault-operational tools**, grouped in one place:
  - `generate_dev_timeline.py` / `update_timeline_incremental.py` — build the development
    timeline from the session logs;
  - `obsidian_reorganise.py` + `reorganise-config-OBS-PHI-Canto.yaml` — a vault-maintenance
    tool (moves notes and updates WikiLinks via the Obsidian CLI), tied to this vault's layout.
- **`DEVELOPMENT-TIMELINE.md`** — the generated development timeline (built by the `vault-ops/`
  timeline tools).
- **`AUTOMATION-GUIDE.md`, `CURATION-FILE-ORGANIZATION.md`, `TIMELINE-SYSTEM-GUIDE.md`** —
  operational guides.
- **`db/`** — the tracking-DB file (gitignored) plus thin **compatibility shims**; the DB
  code is in `phiweaver/tracking/`.
- **`curation_pipeline.py`, `convert-for-curation.py`, `pdf-convert-skill/pdf-convert.py`,
  `quick_demo.sh`** — compatibility shims / wrappers; the real code is under `phiweaver/`.

## Why the split
Engine code is tool-agnostic and importable (`phiweaver/`, run-from-root); this folder is
Claude/vault-operational, with the loose operational scripts now grouped under `vault-ops/`
so the concerns are separated at a glance. The engine no longer references anything here
except the tracking DB in `db/`. See `docs/MODULARITY-PLAN.md` (P1, P4).
