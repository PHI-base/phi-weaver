---
created: 2026-06-11
type: documentation
tags: [docs]
project: PHI-Weaver
---

# Adding a specialised curation module

PHI-Weaver is built so a new curation capability plugs in by following one **module
contract**. A module is a **skill** (the workflow) optionally backed by a **deterministic
tool** (the reproducible part), with **tests** and a registry entry. Independently
testable, independently shippable.

## The contract

Every backed tool follows the shared *envelope* (`phiweaver/common`):

- a structured result with a **`status`**, the payload, and **provenance** (source, cache
  hit/miss, UTC timestamp);
- **`--json`** for machine output, a human summary otherwise; exit **`0`** on success /
  **`1`** on failure;
- **injectable I/O** (an HTTP getter or DB handle) so tests run offline and deterministically;
- **never guess** — ambiguity and "not found" are explicit statuses, never invented data.

## Checklist

1. **Skill** — create `skills/<name>/SKILL.md` with frontmatter declaring its wiring:
   ```yaml
   ---
   name: <name>
   description: <one line; when to use>
   backing_script: phiweaver/<subpkg>/<tool>.py   # or a list, or null (reasoning-only)
   tests: tests/test_<tool>.py                     # or null
   inputs:  [ ... ]
   outputs: [ ... ]
   ---
   ```
   Then the workflow body (Purpose / When to use / Workflow / Expected outputs / QC /
   Human review), following the existing skills.

2. **Tool** (if not reasoning-only) — add `phiweaver/<subpkg>/<tool>.py`. Reuse the
   envelope: `from phiweaver.common import utc_now, make_getter, ResponseCache`. Take an
   injectable getter/handle. Provide a `main(argv=None)` returning an exit code.

3. **Tests** — add `tests/test_<tool>.py`, network-free, injecting a fake getter/handle.
   Cover the happy path, the ambiguous/not-found path, and errors.

4. **Register** — run `python3 -m phiweaver.registry` to regenerate `skills/REGISTRY.md`.

5. **Verify** — `python3 -m phiweaver.smoke` must be green (it runs the contract check and
   the suite). For just the contract: `python3 -m phiweaver.registry --check`.

6. **Wire in** — reference the tool from the skill's workflow (the command), and, if it
   should run during QC, from `curation-qc`.

## Needs its own DB tables?
Register migrations under your **own namespace** — no need to edit core schema:
```python
from phiweaver.tracking import migrations
migrations.register_migrations("mymodule", [("add foo table", "CREATE TABLE foo(...)")])
```
Migrations are append-only and tracked per namespace in `schema_migrations`. Put queries in
a data-returning module (like `phiweaver/tracking/repository.py`) so they test without
capturing stdout.

## Conventions
- Run from the repo root (`python3 -m phiweaver.<subpkg>.<tool>`); no install needed.
- Derive paths from `phiweaver.repo_root()`, never hardcode machine paths.
- Keep the change behaviour-preserving for everything else; keep the smoke test green.
