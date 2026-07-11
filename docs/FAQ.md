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
`BATCH-TOKENS.md` for the session log.
**See:** `phiweaver/article_tokens.py`; `skills/benchmark/SKILL.md` (step 7).

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
