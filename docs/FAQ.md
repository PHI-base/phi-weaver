# PHI-Weaver FAQ

* A human-facing record only*

Question-shaped lookup for recurring questions about PHI-base/PHI-Canto **curation
conventions** and about the **PHI-Weaver project & tooling**. Meant to be skimmable by a new
curator or collaborator, and to let us look up "what did we decide about X" later.

**This FAQ is a lookup layer, not a source of truth.** Each entry gives a short answer and a
**See:** pointer to the canonical doc that owns the detail (a skill, a standard, a design
decision, or a session log). When those change, the pointer still holds; keep answers short so
they don't drift. When a recurring question gets resolved, add a Q/A + pointer here.

---

## Curation conventions

### How do we handle the UniProtKB accession for a gene from a natural strain / field isolate?
PHI-Canto requires a UniProtKB accession, and UniProt often lists only the **reference
proteome**. Mapping the isolate's gene to the **reference gene's accession** is accepted
practice, even when the isolate's protein differs — the sequence difference is captured as the
*allele* against that reference gene. A reference accession is **not** the "wrong strain."
**See:** `07-Standards/judge-core-primer.md` (rule 9); `skills/genotype-creation/SKILL.md`.

### Does a mutation's consequence (truncation, substitution, deletion, fusion…) go in "Expression"?
No. **"Expression"** captures **abundance only** (Wild type product level, Overexpression,
Knockdown, Null, Not assayed). The mutation's **consequence** goes in the **"Allele type"**
field. Don't collapse a consequence into an expression level.
**See:** `07-Standards/judge-core-primer.md` (rule 6); `skills/genotype-creation/SKILL.md`.

### What if a phenotype has no suitable PHIPO term?
Don't drop it. A valid curation **records the phenotype with a note that a new PHIPO term should
possibly be requested**. The concern to flag is *overreach* (forcing a wrong/ill-fitting term),
not the missing term itself. Note the distinction: a purely **molecular readout** (e.g. c-di-GMP
level, in-vitro enzyme activity) is **not** a standalone phenotype — model it as an **annotation
extension / qualifier** on the phenotype it informs, not as a term request.
**See:** `07-Standards/judge-core-primer.md` (rule 11).

### How strongly can we attribute a natural strain's phenotype to one candidate gene?
Field isolates differ from the reference at many loci, so **record the candidate allele and note
the natural genetic background faithfully**; no isogenic line is required. Only an *overstated*
sole-cause claim is a problem. Partial rescue by an allele-swap/complement is a **two-sided
flag** — it may indicate additional genetic determinants **or** a dosage / ectopic-expression
artifact.
**See:** `07-Standards/judge-core-primer.md` (rule 10).

---

## Project & tooling

### Is "LLM-as-a-judge" a valid way to score curation quality?
Yes — it's a mainstream evaluation technique. Caveats: a judge must be **ground-truthed** before
its scores are trusted; without a per-paper gold standard it is a **reference-free critic**
(strong as a pre-review critic, weak as a headline benchmark number); and the human gold
standard is a **strong reference, not ground truth** — judge–human disagreements are
investigated both ways.
**See:** `11-CLAUDE-AI/SESSION-LOGS/2026-07-09-llm-as-judge-discussion.md`.

### How do I give an external model (e.g. GPT-5.5) the conventions to judge a draft?
Use the generated convention primer. Give the model the **core primer** (authoritative) always,
add only the **1–3 most relevant** worked examples for the paper, and watch **leakage** — if a
paper's own gold-standard example is in the bundle, remove it for that run. Regenerate the bundle
after editing any source file.
**See:** `docs/phiweaver-judge-handover.md`; `scripts/build_judge_handover.py`.

### Should we adopt OKF (Open Knowledge Format) to make PHI-Weaver knowledge shareable?
Not worth formally adopting now. PHI-Weaver already follows the OKF pattern — markdown + YAML
frontmatter + directory hierarchy + cross-links + generated indexes + git. OKF's payoff is
ecosystem interoperability we don't yet need. Revisit only if publishing the curation-example
library for outside consumers; the cheap alignment then is normalising a couple of frontmatter
keys (`type`, `resource`, `timestamp`). *(This FAQ is the canonical note for this decision.)*

### What keeps a scored benchmark honest (no leakage)?
Blind drafting (PHI-Weaver gets only the paper + UniProt/EBI OLS, never the existing curation),
no PHI-base access, and **exclude a paper's own gold standard** from the retrieval example
library when scoring that paper. An optional network-sandbox allowlist makes this airtight.
**See:** `07-Standards/curation-benchmarking/README.md`; `skills/benchmark/SKILL.md`.

### Can we tell how many tokens (and which model) each curated article cost?
Yes. Batch several papers in one session so they share the warm context cache, then run
`python3 -m phiweaver.article_tokens --drafts <drafts>` to get a table of **tokens per PMID**
(First author-Year, Title, model) plus the **shared overhead** split across the batch — equal
`1/N`, or `--weight-by-direct`. Attribution is automatic: turns are matched to a paper by the
per-paper draft/PMID references already in the session transcript, so no extra marker discipline
is needed. One honesty caveat baked in: **cache-read tokens are session-cumulative** (each turn
re-reads the whole accumulated context), so they're counted as shared overhead, not charged to
any single paper — a naive per-article sum overstates cost. The benchmark skill emits this as
`BATCH-TOKENS.md` for the session log. Add `--record` to persist the **raw** numbers (per-paper
direct tokens + session overhead + `N`, never the allocated total) to the tracking DB for
trend analysis.
**See:** `phiweaver/article_tokens.py`; `skills/benchmark/SKILL.md` (step 7).

### What happens if I recurate the same article with a different model?
You get a **new row**, not an overwrite. `--record` keys each measurement by
`(pmid, session_id, model)`, so a fresh curation session — including one on a different model —
is stored alongside the earlier one, and `python3 -m phiweaver.article_tokens --history <PMID>`
lists them side by side for a like-for-like cost comparison (direct tokens are each model's own
work; the overhead share is the equal split within that session's batch). Re-running the reporter
on the *same* transcript just upserts the same row, so it never double-counts. Only the raw
components are stored, so the `1/N` split is recomputed on read and old rows stay valid even if
the allocation policy changes. `--cost` / `--history` also show a per-paper **$ estimate**: the
four token buckets (input / output / cache-write / cache-read) are stored and priced separately at
each row's *model* list rate, so recurating a paper on a cheaper model shows a lower cost for the
same token profile (e.g. the same paper is ~$0.45 on Opus 4.8 vs ~$0.09 on Haiku 4.5). Prices are
estimates recomputed on read, so a rate change never invalidates stored rows. Recorded costs also
surface in the **Article-Registry dashboard** — `generate_article_registry` adds a "💰 Token Costs"
section (per-model roll-up + per-paper rows) once at least one batch has been recorded.
**See:** `phiweaver/article_tokens.py` (`record_to_db`, `token_history`, `PRICES`);
`phiweaver/tracking/generate_article_registry.py`.

### What's the difference between a "package" and a "module"?
A **module** is a single `.py` file you can import; a **package** is a *directory* of modules
with an `__init__.py` that makes the folder importable as a namespace (so it groups related
modules under one name). In this repo: `phiweaver/` is the top-level **package**,
`phiweaver/tracking/` is a **sub-package**, and `phiweaver/tracking/session_logger.py` is a
**module**. You run a module with `python3 -m phiweaver.tracking.session_logger` — the dots walk
packages left-to-right; the last name is the module. (So "the token reporter is a module, not a
loose script" means it lives as `phiweaver.article_tokens` inside the package, not as a
standalone file in `scripts/`.) Today phiweaver has 7 packages holding ~25 modules.
**See:** `phiweaver/README.md`; `phiweaver/__init__.py` (subpackage list).

### How does this repo handle git commits?
Current solo workflow commits **directly to `main`** rather than using feature branches + pull
requests. Pushing to `main` can trip an agent safety guardrail; the curator authorises the push
(e.g. `! git push origin main`). Revisit if collaborators need review-before-merge.

### Can the PHI-Canto issues tracker feed PHI-Weaver's knowledge?
**Mine it, don't ingest it.** The tracker holds useful convention decisions and ontology
term-request threads, but bulk-loading it would contaminate context two ways: (a) issues are
*discussion* — rejected, superseded, or unresolved — so raw ingestion imports wrong conventions;
and (b) it lives on GitHub, already a **benchmark-leakage** source, so it must stay excluded from
blind/scored runs. Instead: mine a **resolved** decision → write it into the owning
skill/standard/FAQ with a `See:` issue-number pointer → the pipeline reads the curated convention,
never the raw issue. *(This FAQ + `docs/BACKLOG.md` are the record for this decision.)*
