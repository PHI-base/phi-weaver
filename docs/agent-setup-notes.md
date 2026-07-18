---
created: 2026-06-10
type: documentation
tags: [docs]
project: PHI-Weaver
---

# Agent Setup Notes

How PHI-Weaver's portable agent-instruction structure is organised, and how each tool
consumes it.

## Files

- **`AGENTS.md`** — the single source of truth. Tool-agnostic project rules: stable
  project knowledge, scientific/biocuration rules, coding + file-safety rules, and
  pointers to skills and tool settings.
- **`CLAUDE.md`** — short bridge for Claude Code. Says "read `AGENTS.md`" and adds only
  Claude-Code-specific notes. Does not duplicate `AGENTS.md`.
- **`skills/<name>/SKILL.md`** — reusable task workflows (purpose, when-to-use, steps,
  outputs, QC, human-review). One folder per skill.
- **`docs/agent-setup-notes.md`** — this file.

## Separation of concerns

| Content | Lives in |
|---|---|
| Stable project knowledge | `AGENTS.md` §1 |
| Scientific / biocuration rules | `AGENTS.md` §2–3 |
| Coding & file-handling rules | `AGENTS.md` §4–5 |
| Reusable task workflows | `skills/` |
| Tool-specific settings | `CLAUDE.md` (Claude Code); `AGENTS.md` natively (OpenCode) |

## How each tool uses it

**Claude Code** reads `CLAUDE.md` automatically at startup, which directs it to
`AGENTS.md`. Skills in `./skills/` are discovered via their `SKILL.md` frontmatter and
invoked with the Skill tool when a skill's "when to use" applies.

**OpenCode** reads `AGENTS.md` natively (its standard instructions file). The same
`./skills/` workflows apply. If OpenCode-specific configuration is ever needed, add an
`opencode.json` at the repo root — it is not required for instructions, which come from
`AGENTS.md`.

## Maintenance

- Put durable rules in `AGENTS.md`; keep it concise.
- Put repeatable procedures in a skill, not in `AGENTS.md`.
- Keep `CLAUDE.md` a thin pointer — never copy `AGENTS.md` content into it.
- Older detailed operational docs (`11-CLAUDE-AI/AUTOMATION-GUIDE.md`,
  `docs/STORAGE-CONFIGURATION.md`, etc.) remain the deep references; `AGENTS.md` links to
  them rather than restating them.
