---
name: inbox-triage
description: Triage material dropped in 00-Inbox/for-weaver/ (GitHub issues/discussions, paper reviews, freeform notes), decide whether it carries information the curation system is missing, and propose ledger rows + durable edits for human sign-off. Use when items have accumulated in the for-weaver drop zone, or on demand to process a newly dropped item.
backing_script: null
tests: null
inputs:
  - one or more files in 00-Inbox/for-weaver/ (raw issue thread, discussion export, paper review, or freeform note)
outputs:
  - per-item source + provenance (issue #/permalink/status, PMID, or freeform who/when)
  - per-item triage class (general rule / tool-or-ontology gap / worked example / paper-specific-only)
  - "already covered vs genuinely new" verdict with the file(s) checked
  - proposed CURATION-LESSONS.md row(s) + the specific durable edit, for sign-off
---

# Inbox Triage

## Purpose
Give the learning system's feedback sources a front door. Material dropped in
`00-Inbox/for-weaver/` — GitHub issue threads, `PHI-base/curation` discussion exports,
curator paper reviews, meeting/email/freeform notes — is read, checked against what weaver
already knows, and turned into **proposals**: a `docs/CURATION-LESSONS.md` ledger row plus the
specific convention/skill/backlog/example edit that would fold the lesson in. This is the
manual `A2/A3 → B1 → B2` path of `docs/LEARNING-SYSTEM.md`, made concrete.

Weaver **proposes; the human approves.** Nothing here silently changes what weaver reads at
drafting time.

## When to use
- Items have accumulated in `00-Inbox/for-weaver/` and need processing.
- On demand for a single freshly dropped item.
- Not during a drafting or benchmark run — the drop zone is deliberately outside that read
  path (see Guardrails).

## The drop zone
- `00-Inbox/for-weaver/` holds **raw, non-authoritative** material. Its contents are never
  read while drafting or benchmarking.
- Processed items move to `00-Inbox/for-weaver/done/` (append the ledger `ID` to the filename,
  e.g. `issue-142-don-scope.md` → `done/L9-issue-142-don-scope.md`) so the folder shows only
  what's outstanding.
- Skip `README.md` and `done/` when triaging.

## Workflow
1. **Enumerate** items in `00-Inbox/for-weaver/` (excluding `README.md` and `done/`). Handle
   each independently.
2. **Identify source + provenance**, mapping to a ledger `Type` (see `docs/CURATION-LESSONS.md`
   "Sources & type tags"):
   - `issue` — GitHub issue/discussion: capture the number, permalink, and **open/closed
     status**.
   - `paper-review` — a curator's review of a specific draft: capture the reviewer and PMID.
   - `meeting` / `email` / `note` — freeform: capture **who said it and when**; treat the
     wording as a paraphrase.
3. **Apply the intake guardrails before classifying** (see below). An `open` issue, or a
   freeform item with no citable basis, can still be logged as `open` intake but must **not**
   be proposed as an applied rule.
4. **Triage class (B2)** — pick one:
   - **general rule** → destined for the conventions doc `C1` and/or a `skills/` step `C2`.
   - **tool / ontology gap** → destined for `docs/BACKLOG.md` `C4` (or the ontology-gap ledger
     / `ontology-term-request` skill if it's a term gap).
   - **worked example** → destined for `07-Standards/curation-examples/` `C3`.
   - **paper-specific only** → fix the affected draft, not the pipeline; no durable edit.
5. **"Missing information" check — is it already covered?** Before proposing anything, search
   the durable knowledge for an existing rule/gap/example that already says this:
   - conventions: `07-Standards/PHI-Canto-Curation-Conventions.md`
   - skills: `skills/*/SKILL.md`
   - backlog + gap ledger: `docs/BACKLOG.md`, `docs/ontology-gaps.jsonl`
   - examples: `07-Standards/curation-examples/`
   - prior lessons: `docs/CURATION-LESSONS.md`

   Report the verdict as **already-covered** (name the file/section; recommend no action, or a
   status/provenance update if the item strengthens an existing rule) or **genuinely new**.
6. **Draft the proposal** for each new, eligible item:
   - A `CURATION-LESSONS.md` row in the exact column order
     `| ID | Date | Type | Source | Lesson (general rule) | Applied to | Status |` — next free
     `L`-id, today's date, the type, a source string with the permalink/PMID/who+when.
   - **Distill the lesson in our own words + a `See: #n` pointer** — never paste the raw issue
     (matches the D17 provenance style).
   - The specific durable edit (which file, which section, the proposed wording) that the
     "Applied to" column will cite.
7. **Present for sign-off.** Show all proposals together; do not apply. On approval:
   - append the ledger row (**append-only** — never edit or delete existing rows);
   - make the durable edit, citing the source in-line per the conventions-doc provenance rule;
   - move the processed file to `done/` with the `L`-id prefix.

## Intake guardrails (from docs/CURATION-LESSONS.md)
- **Only fold in resolved / closed decisions.** An open issue thread may be wrong or get
  superseded — keep it `open` in the log and do **not** apply it yet.
- **Distill, don't paste** — our own words plus `See: #n`, not the raw issue text.
- **GitHub is a benchmark-leakage source — mine, don't ingest.** The distilled convention is
  fine; raw issue/discussion text must stay out of blind / scored runs. `for-weaver/` (raw)
  and `done/` are **not** part of any drafting or benchmark read path — keep it that way; never
  glob `00-Inbox/**` into a drafting or scoring prompt.
- **Freeform (`meeting` / `email` / `note`) is intake, not authority.** It can drive a draft or
  a skill tweak, but before it becomes a **stated rule** in the conventions doc it needs a
  citable basis — a recorded curator sign-off, or promotion to a GitHub issue that resolves.
  Don't enshrine a half-remembered hallway comment as a rule.
- **The ledger is append-only.** Lessons are superseded with a new row, never overwritten.

## Expected outputs
- Per item: source + provenance, triage class, and an already-covered / genuinely-new verdict
  naming the file(s) checked.
- For each new, eligible item: a ready-to-paste `CURATION-LESSONS.md` row and the specific
  durable edit it cites — as a proposal.
- A short list of items **held** (open issue, freeform lacking a citable basis) with what they
  need before they can be applied.

## Quality-control checks
- Every proposed rule cites a verifiable source (issue permalink + closed status, PMID, or a
  recorded sign-off) — no rule without provenance.
- The lesson is generalisable (improves *future* drafts), not a one-paper fix; paper-specific
  points go to the draft, not the ledger.
- The "already covered" search actually ran and is reported — a proposal that duplicates an
  existing convention is a triage failure.
- No raw issue text copied into a durable file.

## Human review
- Every proposal is a recommendation. A human approves the ledger row and the durable edit
  before either lands; for freeform-sourced rules, the curator sign-off is itself the gate.
