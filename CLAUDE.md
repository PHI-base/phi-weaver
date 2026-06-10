# CLAUDE.md

**`AGENTS.md` is the main source of truth for this project — read it and follow it.**
This file is a short bridge for Claude Code and intentionally does not duplicate AGENTS.md.

## Where things are
- Project rules, scientific-accuracy rules, coding standards, file-safety rules:
  **[AGENTS.md](AGENTS.md)**.
- Reusable task workflows: **`./skills/`** (one folder per skill, each with a `SKILL.md`).
  Invoke via the Skill tool when a skill's "when to use" applies.
- Prior session context: read `11-CLAUDE-AI/SESSION-LOGS/INDEX.md` at session start.
- Deep operational references: `11-CLAUDE-AI/AUTOMATION-GUIDE.md`, `docs/`.

## Claude Code specifics
- WSL: launch with `claude --dangerously-skip-permissions` (Windows-mount permissions).
- On the `z:` mount, edit `.git/config` directly — `git config` fails on its lock-file chmod.
