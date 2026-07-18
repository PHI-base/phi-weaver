---
type: documentation
tags: [inbox]
project: PHI-Weaver
---

# for-weaver — drop zone for curation feedback

Drop material here that weaver should learn from: a GitHub issue/discussion thread, a
`PHI-base/curation` export, a curator's paper review, or a freeform meeting/email note. One
item per file.

**The contract:**
- Contents here are **raw and non-authoritative**. Nothing in this folder is read while
  drafting a curation or running a benchmark — it is deliberately outside that read path (keeps
  GitHub text out of scored runs; "mine, don't ingest").
- Weaver processes items with the **`inbox-triage`** skill: it identifies the source, checks
  whether the point is already covered in the conventions / skills / backlog / examples, and
  **proposes** a `docs/CURATION-LESSONS.md` row plus the durable edit — for a human to approve.
  It never auto-applies.
- Processed items move to `done/` with their ledger `L`-id prefixed to the filename.

**Before it can become a stated rule:** GitHub issues must be **closed/resolved**; freeform
notes need a citable basis (a recorded curator sign-off, or promotion to an issue that
resolves). Open or uncited items are logged as intake only.

See `skills/inbox-triage/SKILL.md` and `docs/LEARNING-SYSTEM.md` (the `A2/A3 → B1 → B2` path).
