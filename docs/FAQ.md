---
created: 2026-07-09
type: documentation
tags: [docs]
project: PHI-Weaver
---
```table-of-contents
```
# PHI-Weaver FAQ

* A human-facing record only*

Question-shaped lookup for recurring questions about PHI-base/PHI-Canto **curation
conventions** and about the **PHI-Weaver project & tooling**. Meant to be skimmable by a new
curator or collaborator, and to let us look up "what did we decide about X" later.

**This FAQ is a lookup layer, not a source of truth.** Each entry gives a short answer and a
**See:** pointer to the canonical doc that owns the detail (a skill, a standard, a design
decision, or a session log) — [`README.md`](README.md) lists who owns what. When those change, the pointer still holds; keep answers short so
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

### Why doesn't PHIPO have "conidiation" / "appressorium" / "mycelium"?
**By design — PHIPO is species-neutral:** a term must hold across pathogens, and *conidiation* only
exists in some fungi while *asexual spores* covers most organisms. PHIPO says **asexual spores**,
**sexual spores**, **hyphae**, **pathogen penetration structure**. The species vocabulary is **not
missing** — it lives in EXACT synonyms, so `map_phenotype "conidia absent"` → ★ `PHIPO:0000061`.
**See:** `skills/ontology-term-request/SKILL.md` ("not a gap" #1) — full vocabulary, the two retries,
and the release-specific caveat; `docs/CURATION-LESSONS.md` (L8).

### My phenotype phrase found nothing. Which retries should I try first?
**Two, before any other — both systematic, not guesswork:** (1) **species-specific →
species-neutral** ("conidiation" → "asexual spores"); (2) **process noun → entity noun** for
presence/absence ("sporulation abolished" → "asexual spores absent") — absence is not a dimension of
the process form. Natural phrasing misses on **both axes at once**, which reads exactly like a gap;
this already put a real term in the backlog as a phantom gap. Then check `--include-obsolete`: the
term may exist but be deprecated, which OLS's search hides.
**See:** `skills/ontology-term-request/SKILL.md` (steps 4–5); `docs/CURATION-LESSONS.md` (L2, L8).

### What if a phenotype has no suitable PHIPO term?
Don't drop it. A valid curation **records the phenotype with a note that a new PHIPO term should
possibly be requested**. The concern to flag is *overreach* (forcing a wrong/ill-fitting term),
not the missing term itself. Note the distinction: a purely **molecular readout** (e.g. c-di-GMP
level, in-vitro enzyme activity) is **not** a standalone phenotype — model it as an **annotation
extension / qualifier** on the phenotype it informs, not as a term request.
**First, make sure it really has none** — run the two retries in the entry above, and check whether
the term exists but is **obsolete** (`map_phenotype --include-obsolete`; OLS hides deprecated terms,
which is how phipo#452 was filed unaware `PHIPO:0000503` existed). Most "no suitable term" findings
so far have turned out to be wording or obsoletion, not absence.
**See:** `07-Standards/judge-core-primer.md` (rule 11); `docs/CURATION-LESSONS.md` (L2, L8);
`skills/ontology-term-request/SKILL.md` (steps 4–5).

### How strongly can we attribute a natural strain's phenotype to one candidate gene?
Field isolates differ from the reference at many loci, so **record the candidate allele and note
the natural genetic background faithfully**; no isogenic line is required. Only an *overstated*
sole-cause claim is a problem. Partial rescue by an allele-swap/complement is a **two-sided
flag** — it may indicate additional genetic determinants **or** a dosage / ectopic-expression
artifact.
**See:** `07-Standards/judge-core-primer.md` (rule 10).

---

## Project & tooling

### Can input PDFs and output documents live on Google Drive?
Yes — the storage layer is a single filesystem path, so anything that makes Drive look like a
folder works with **no code change**. With Google Drive for Desktop on Windows + WSL, Drive
mounts as a Windows drive (e.g. `D:\GoogleDrivePHI` → `/mnt/d/GoogleDrivePHI`); set
`export PHI_LITERATURE_ROOT="/mnt/d/GoogleDrivePHI/PHI-Canto-Literature"` and the pipeline
creates `active/` (input), `completed/` (output), `media/` under it (verified live 2026-07-19).
**Keep the SQLite tracking DB off Drive** (it stays local at `11-CLAUDE-AI/db/`; SQLite + sync
risks corruption); mind sync latency, `media/` quota, and use a *private* Drive folder.
**See:** `docs/STORAGE-CONFIGURATION.md` ("Storage on Google Drive").

### Should I curate from PDF or EPUB?
**PDF — that's the default, and it's what our tooling reads.** EPUB is really a book format;
journals hardly ever offer it for a research paper, so in practice you won't get the choice.
EPUB's one advantage is cleaner text (no two-column scrambling, no broken hyphenation, tables
as real tables rather than a picture of a table) — so if you happen to have both and the PDF
converts badly, use the EPUB for the text.
**But if the paper is open access, use neither: take the PubMed Central full text (XML or the
HTML page) instead.** There the sections, tables and references are already labelled, so gene
symbols and strain IDs survive intact and nothing has to be reconstructed from page layout.
That covers most of what PHI-base curates. Order of preference: **PMC/publisher full text →
PDF → EPUB.** Whatever you use, supplementary data still arrives as PDF/XLSX.
**See:** `phiweaver/pdf/PDF-CONVERT-SKILL.md` (the PDF→Markdown converter, PyMuPDF).

### Should the model read the figure images, or do the text and legends already do the job?
**Decline by default; inspect on cause.** Text and captions carry the annotation set itself.
Measured on PMID:39852455 — curated twice, once from captions only and once with the panels —
inspecting six figures changed **zero term selections**. Which PHIPO term, which genotype,
evidence code, conditions and extensions all come from Methods and Results. Reading a figure
buys **confidence and caveats**, not terms.

**Where the panel is genuinely worth it** — the three causes that justify marking an annotation
`needs_figure: true`:
1. **The claim is qualitative** and only the image can confirm it (histopathology, microscopy
   appearance). The one case where the figure is irreplaceable. On PMID:39852455 the authors
   describe intact bronchial walls; the panel does not obviously show that, so the annotation
   was flagged rather than asserted.
2. **Magnitude decides the annotation** rather than merely describing it. The same paper's
   cell-wall result reads as a marginal `p < 0.05` from its caption and as a ~2-fold change with
   full complementation rescue from the panel — which changes the growth-confound judgement.
3. **It is the paper's take-home message**, where an author's summary is worth checking against
   their own figure.

**Be honest about what captions already tell you.** Two of the four things the panels "revealed"
on that paper were already in the text: the caption enumerates which panels were quantified (so
"branching was never measured" was readable without the image), and the Results prose states the
*ATG1*/*ATG12* direction outright. **Read the caption properly before deciding you need the
panel** — "was this quantified?" is usually answerable from the caption alone, and it is the
single most useful thing to know before spending the tokens.

**Cost** (a vision model bills roughly `width × height / 750`, after a downscale to ~1.15 MP):
Europe PMC's web-sized figures run ~300–1,100 tokens each (~3,550 for six); figures extracted
from a PDF are print resolution and cost ~1,500 each (~8,840 for six), about 2.5×. For context,
the JATS converter saves ~20,000 tokens against feeding raw XML, so selective figure reading
still leaves you well ahead. Plan the spend with
`python3 -m phiweaver.figure_ledger <draft.md> --needed`, which separates REQUIRED from optional
and prices what is still unread.

**Record the decision, don't just make it.** The `figure_inspection` ledger stores one entry per
figure with what was actually read; declining is fine *with a stated reason*. An entry marked
inspected with an empty `read` counts as **not** inspected — ticking a box is not looking at a
figure. The audit still reports, as information rather than a warning, any annotation citing an
un-inspected figure: that check caught a draft claiming nothing depended on Figure 7 when two GO
annotations cited it, and inspecting it added a real qualification.
**See:** `skills/canto-entry-queue/SKILL.md` (ledger fields and entry-queue output),
`phiweaver/figure_ledger.py` (`needs_figure`, `--needed`, `--strict`).

### Is "LLM-as-a-judge" a valid way to score curation quality?
Yes — it's a mainstream evaluation technique. Caveats: a judge must be **ground-truthed** before
its scores are trusted; without a per-paper gold standard it is a **reference-free critic**
(strong as a pre-review critic, weak as a headline benchmark number); and the human gold
standard is a **strong reference, not ground truth** — judge–human disagreements are
investigated both ways.
**See:** `docs/LLM-AS-JUDGE-DESIGN.md`.

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
**Keep commits simple:** a coherent unit of work is **one commit** — don't split into
micro-commits or agonise over logical separation unless asked; stage only the task's files
(leave unrelated dirty files like `.obsidian/` alone).
**See:** `AGENTS.md` §5 (File Safety Rules).

### How should I link between things — `[[wikilinks]]` or markdown paths?
By **what you point at**, not by file. An Obsidian `[[slug]]` wikilink for a **note in the same
store** (vault → vault, or Claude-memory → memory); a markdown path link `[path](path)` (or a
backtick path) for a **code/data/config file, or anything opened by path** — including from
AI-facing files like `AGENTS.md`. **Never `[[link]]` across stores:** Claude's memory lives
*outside* the vault (`~/.claude/.../memory/`), so a vault note that `[[links]]` a memory slug is a
dangling link in Obsidian — restate it in prose or link the real file/URL.
**See:** `AGENTS.md` §1 (Link conventions).

### Why were the two `INDEX.md` files renamed, and how should I name notes?
Obsidian labels graph nodes, the quick-switcher, and `[[links]]` by **basename**, so two
`INDEX.md` files showed as one ambiguous "INDEX" node. Give every explorable note a
**vault-unique, descriptive basename**; for a folder's index/meta note, prefix the subject
(`Curation-Examples-INDEX.md`, not `INDEX.md`). `SKILL.md` / `README.md` are exempt convention
files — **don't rename them**; hide them from the graph with a view filter (`-file:SKILL
-file:README`). A smoke-test guard (`python3 -m phiweaver.vault_names --check`) fails on any new
non-exempt collision.
**See:** `AGENTS.md` §1 (Note naming); `phiweaver/vault_names.py`.

### Can I use Obsidian content plugins (Table of Contents, Daily Notes, Calendar…)?
**Yes — content-*adding* plugins are safe.** Weaver reads files as text and never executes
fenced blocks, and its frontmatter parsers **stop at the closing `---`**, so an inert block like
```` ```table-of-contents ```` beneath the frontmatter is ignored; the contract checks only parse
`SKILL.md` / curation-example frontmatter, never note bodies. **Two cautions:** (1) plugin-rendered
blocks (a TOC) only render *in Obsidian* — on GitHub or inside a generated bundle they show as an
empty code block, so keep them out of GitHub-facing docs and any source doc a generator concatenates;
(2) never add plugin content to the **generated** files (`skills/REGISTRY.md`, the two `*-INDEX.md`,
`Article-Registry.md`, `DEVELOPMENT-TIMELINE.md`) — regeneration wipes it. **Avoid auto-rewriter
plugins** (linters / formatters / front-matter managers) on generated or contract files: they can
clobber the indexes or reformat contract frontmatter and fail `--check`. Daily Notes / Calendar / TOC
add content, they don't rewrite it — fine. `smoke_test.py` catches any contract breakage.
*(This FAQ is the canonical note for this decision.)*
**See:** `phiweaver/registry.py` (`parse_frontmatter`); `scripts/smoke_test.py`.

### How do we keep PHI-Weaver lean and maintainable?
**Where a fact is *derived*, put a check on it or expect it to drift.** Reviewed 2026-07-28:
every derived surface with a mechanical check was still true, and every one relying on someone
remembering had drifted — the judge bundle had been stale for three weeks, `OVERVIEW.md`
understated the test count tenfold, and session-index rows had reached 645 words against a stated
"one-line" rule. Size was not the predictor; enforcement was. Four working rules:
- **One doc owns each topic** — everywhere else, summarise and link. Parallel explanations drift
  silently: nothing fails, someone just reads the stale copy and acts on it.
- **Don't write a count into prose** when a generated file or a command already prints it.
- **A generated file needs a `--check` in `phiweaver.smoke`**, or its generator stops being run
  and no one notices.
- **Prefer removing an artefact to automating its upkeep** — count what actually reads a thing
  before building tooling for it. This is how the session-log prune was dropped in favour of
  promoting the one log that five docs cited.
**When a check is the wrong tool.** The rules above target *silent, cumulative* drift — a copied
number, a generator nobody runs, a file that grows a row per session. They do **not** apply to a
curation convention the drafting agent applies as it writes: put that in the conventions doc and
the relevant `skills/` file, and it takes effect on the next draft with no code at all. Evidence:
the Δ-suffix ruling (L4, 2026-07-15) was never coded, and **every** draft dated on or after it
uses `SdhAΔ` / `FgKnr4Δ` / `abc1-2Δ` correctly, while the pre-L4 drafts still read `ΔfleQ`. That
is the declarative-learning loop in `LEARNING-SYSTEM.md` working as designed — adding a lint there
would buy nothing and cost a moving part. Reach for a check when nothing would surface the
problem; rely on the rule when compliance is visible in the output. If a post-rule draft ever
breaks such a convention, *that* is the trigger to add the check.

And keep changes small: overengineering here has produced runs that fail to terminate.
**See:** `docs/README.md` (which doc owns what, and which docs are deliberately not canonical);
`AGENTS.md` §1 (index-row cap) and §4 (simplicity, verification); `phiweaver/registry.py` and
`phiweaver/session_index.py` (the check pattern to copy).

### Should the smoke test run at the start of every weaver session?
**No — run it when the code or environment could have changed, not as a ritual.** Smoke re-runs
the whole unit suite (~30–45 s; `python3 -m phiweaver.smoke` reports the count) and, on an
unchanged checkout, tells you nothing new. Run it **after
`git pull`** (collaborator code), after an environment change, and **before a scored benchmark
run**; code-editing sessions are already covered by the "verify before committing" rule
(`AGENTS.md` §4). A pure curation session doesn't need it — and the things that actually bite
curation (network availability, a **stale PHIPO clone**) are what smoke *doesn't* check (it's
network-free). **Automated option (set up locally):** a `SessionStart` hook runs smoke **only when a
code change has landed** — HEAD moved *and* the move touched `phiweaver/`, `scripts/`, `tests/`, or
`pyproject.toml`. Docs / frontmatter / FAQ commits (and docs-only pulls) advance the baseline
silently, since smoke tests none of that; only a code-touching pull/commit triggers the ~30–45 s run.
It stores the last-checked HEAD in `.git/last-smoke-head` and always exits 0 (warns on failure, never
blocks). The hook + script live in the gitignored `.claude/`, so they're per-machine, not shared.
*(This FAQ is the canonical note for this decision.)*
**See:** `.claude/session-start-smoke.sh` (local, gitignored); `scripts/smoke_test.py`; `AGENTS.md` §4.

### Can PHI-Weaver help with PHIPO ontology development?
**Yes, within limits.** Curation is the best gap detector — it meets gaps on real papers with the
evidence in hand — so weaver **records** them (`docs/ontology-gaps.jsonl`, ranked by how many papers
needed each), **drafts** evidence-backed requests, and for a **pattern extension** (a missing
dimension in a live sibling set) opens a **PR** against `phipo-edit.owl` — PHI-base/phipo#454 is the
worked example. It does **not** design terms otherwise, and it **cannot decide**: `no_match` is not
proof of a gap, so a human rules on every request. Most "gaps" so far were wording or obsoletion.
**See:** `skills/ontology-term-request/SKILL.md` (the two routes, and the checks before either).

### Could weaver ever develop PHIPO terms without a human — can recurrence confer legitimacy?
**Partly, and this is the real frontier — but the honest answer is "human ratifies patterns, not
terms," not "no human."** Curating at scale manufactures **warrant**: recurrence across independent
papers (`docs/ontology-gaps.jsonl`, ranked by demand) is genuine evidence a concept is real and
in-demand, and that is a large share of what an editorial review actually checks. So warrant is
automatable, and it shrinks the human's job. But recurrence confers warrant for **existence and
demand**, not for **design**: frequency is orthogonal to *granularity* (N mentions don't say whether
"X" is one term, three conflated, or a subtype), to *placement* (the leaf recurs; the parent doesn't
fall out of a count), and to *scope* (a molecular readout mentioned 50 times is still a qualifier, not
a phenotype — high recurrence just lends a category error false confidence). Worse, a **systematic**
bias produces a *consistent* false positive that looks *more* legitimate, not less: if a
species-specific phrasing keeps evading the L2 retry, weaver sees a recurring "gap" that is a recurring
*retry-failure*, and mining our own curations for patterns risks **manufactured consensus** —
recurrence that reflects weaver's phrasing, not the biology. So `no_match` at scale is still not proof
of a gap. The constructive move: recurrence should **promote a pattern into a ratified template** — a
human rules **once**, at the pattern level (as in phipo#454's sibling grid), and matching instances
then auto-mint with no human per term. That moves the decision from **per-term** to **per-pattern**,
rarely — autonomy from the curator's chair while keeping an accountable ratifier where a shared
standard needs one. In one line: weaver can automate a term's **generation**; legitimacy is
*granted*, not computed, and dropping the last guardrail just relabels the model as the authority
someone still has to choose to trust.
**See:** the entry above; `docs/CURATION-LESSONS.md` (L2, L7); `skills/ontology-term-request/SKILL.md`
(the pattern-extension route).

### Does PHIPO lookup use OLS or a local copy?
**Local — from two different files, and the distinction matters.** `phipo-base.obo` (the **release
artifact**) answers "give me a term for this phrase" and validates IDs, because that is the question
a curator has: *can I annotate this?* `phipo-edit.owl` (the **working file**) is for **gap analysis
only** — obsolete terms, sibling structure, hole sweeps — and must **never** be a source of
suggestions: it contains unreleased terms PHI-Canto does not have, so suggesting one is a bug that
looks like a feature. (`phipo.obo`, 7.3M, is the wrong file — it inlines GO/CHEBI.) Going local kills
the blind spot that OLS **hides deprecated terms**, which is how phipo#452 was written unaware that
PHIPO:0000503 already existed. **OLS is still used for GO** (not vendorable at any sane size).
Cost: a cruder scorer than Solr — acceptable, since L7 says OLS's ranking is untrustworthy anyway and
a human reads every candidate, so favour recall (generous `--rows`) over ranking.
Bundled as `phiweaver/lookup/data/phipo-base.obo` (release 2026-03-12) since 2026-07-17 — as are
PECO / PHIDO / PHIPO_EXT / FYPO_EXT. `map_phenotype --include-obsolete` surfaces deprecated terms for
gap analysis; every search prints the `data-version`, so a stale bundle is visible rather than silent.
**The clone needs refreshing** — see the next entry.
**See:** `phiweaver/lookup/data/README.md` (refresh command); `docs/BACKLOG.md` (Tooling);
`skills/ontology-term-request/SKILL.md` (step 5); `docs/CURATION-LESSONS.md` (L7).

### Does the local PHIPO clone need updating, and how?
Yes — this is the real cost of going local: OLS was self-updating, a clone is not. It lives at
`/mnt/z/Computer/GITHUBrepositories/phipo` and goes stale silently, so **`git pull` before any gap
analysis or term PR** — a stale clone can show a term as missing after someone has added it, or hide
an obsoletion. Same practice as the vendored `.obo` files, which carry per-file refresh commands.
```bash
cd /mnt/z/Computer/GITHUBrepositories/phipo && git checkout master && git pull
```
**On the `z:` mount:** `git config` fails on its lock-file chmod, so **clone on the native fs and
copy across**, then set `filemode = false` by editing `.git/config` directly. Never `sed -i` the
`.owl` — in-place edits destroy files on `/mnt/z`. PRs target **`master`**, and CI runs the full ODK
QC, so **no local `robot`/ODK install is needed** (confirmed on PR #454).
**See:** `skills/ontology-term-request/SKILL.md` (step 5); `phiweaver/lookup/data/README.md`
(refresh pattern for the vendored ontologies); `AGENTS.md` (file-safety rules).

### Is giving the benchmark access to PHIPO a leakage risk?
**No — PHIPO is a tool, not an answer, and the sandbox must have full access to it.** A human curator
works with the ontology open; withholding it doesn't make the benchmark harder, it measures a task
nobody performs. Same for UniProt and GO. What **is** leakage is the **curated PHI-base datasets** —
`phi-base.org` and the PHI-base **data** repos hold existing entries for the very papers under test,
so a scored run reaching them is reading the answer key. **The line is not drawn by domain:**
`github.com/PHI-base` hosts *both* the `phipo` ontology **and** the data repos, so "ontology yes, data
no" can't be expressed as a domain rule. Today it doesn't bite (allowlist is default-deny to UniProt +
OLS; PHIPO rides in on **EBI/OLS**, not GitHub), and **vendoring PHIPO removes the question entirely**
— a bundled `phipo-base.obo` needs no network during a run. The `git pull` + re-vendor is
**maintenance, outside scored runs**.
**See:** `docs/BACKLOG.md` (sandbox-allowlist item; offline-PHIPO item);
`07-Standards/curation-benchmarking/benchmark-sandbox.settings.json`.

### Can the PHI-Canto issues tracker feed PHI-Weaver's knowledge?
**Mine it, don't ingest it.** The tracker holds useful convention decisions and ontology
term-request threads, but bulk-loading it would contaminate context two ways: (a) issues are
*discussion* — rejected, superseded, or unresolved — so raw ingestion imports wrong conventions;
and (b) it lives on GitHub, already a **benchmark-leakage** source, so it must stay excluded from
blind/scored runs. Instead: mine a **resolved** decision → write it into the owning
skill/standard/FAQ with a `See:` issue-number pointer → the pipeline reads the curated convention,
never the raw issue. *(This FAQ + `docs/BACKLOG.md` are the record for this decision.)*

### How do phiweaver drafts get into PHI-Canto, and why isn't the data entry automated?
**A curator enters them, working through the generated entry queue — and that stays true.** There
is no write API. The one server-side import (`canto_add.pl --sessions-from-json`, admin only) can
create a session's **genes, alleles and genotypes but not its metagenotypes or annotations**, so the
annotation layer is hand-entered permanently; the entry queue is not an interim step.

**Browser automation was assessed and rejected (2026-07-25) on arithmetic, not principle.** Entry
costs a curator ~30–40 min per paper; automating it costs 60–100 h to build, so it breaks even at
roughly 150–250 papers. More decisively, **typing isn't the bottleneck** — accession resolution,
ontology gaps and evidence rulings are, and those are judgement, not keystrokes. Reversing this
needs two measurements, not an argument: recurring throughput in the hundreds of papers, or a
baseline showing mechanical entry dominates curator time.
**See:** `docs/DESIGN-DECISIONS.md` **D18** (the decision of record, with the rejected alternatives
and the two hazards any revival must answer); `docs/CANTO-SUBMISSION-ROUTES.md` (the three routes in
detail); `docs/BACKLOG.md` → "Submit drafts into PHI-Canto".

### What is end-to-end (E2E) testing here, and how is it different from the smoke/unit tests?
Three different questions. **Unit** (`tests/`): is one function correct in isolation? **Smoke**
(`phiweaver.smoke`): on a fresh checkout, is the whole thing *alive* — imports, wiring, storage,
DB? **E2E** (`scripts/e2e/`): does the *real flow*, run start to finish, produce the *correct
final output*? In one line — smoke checks the machine turns on; E2E checks it makes the right
product. It's good for failures that live in the **whole chain** (an unresolved accession, an
obsolete PHIPO/PHIDO term, a malformed Canto block) that a unit test on one prompt won't catch.
Note a distinction: telling Claude "curate paper X" is an end-to-end **run**; it's a **test** only
when a harness launches it unattended and reduces it to a pass/fail against a known answer. A
gold standard is only **half** of an E2E test — the answer key; the automated *producer* is the
other half (the reason the draft step had to be "wrapped").
**See:** `phiweaver/smoke.py`; `scripts/e2e/`; `skills/benchmark/SKILL.md`.

### What does `scripts/e2e/` do, and what does its score actually measure?
`e2e-curate.sh <paper.md> <gold.md>` launches a headless, blind-sandboxed `claude -p` to curate
one paper, prefills the scorecard, then runs `score_against_gold.py` — a stdlib-only
precision/recall/F1 over the identifiers (PHIPO/GO/PHIDO/FYPO/PECO/UniProtKB); exit code is the
pass/fail on overall F1. **It measures identifier overlap only** (did it find the right genes,
phenotypes, disease terms, without inventing any) — the cheap, CI-able *floor*. It does **not**
judge curation nuance (genotype correctness, evidence codes, extensions, annotation-type
attachment), so a perfect ID F1 is **not** a flawless curation — that deeper layer is the human
scorecard + the judge-in-design. Verified end-to-end on PMID39787257 (FgKnr4): 16/16 ids, F1
1.00. **Gotcha:** the blind sandbox needs **`socat` as well as `bubblewrap`** (`sudo apt install
socat`) or it refuses to start — this bites the `benchmark` skill too.
**See:** `scripts/e2e/e2e-curate.sh`; `07-Standards/curation-benchmarking/README.md`;
`docs/judge-rules-PROPOSED-for-review.md`.

### Can I use the E2E harness to curate real new papers, or is it test-only?
The drafting *engine* is production-usable; the *script* is test-shaped (it requires a gold
standard and ends by scoring, which a new paper has no answer for). For **real curation at small
volume, just use the Claude CLI** — it already is the agent that runs the skills; the wrapper only
matters when you want it unattended or as a scored test. Run it in a **normal (un-sandboxed)**
session so it *can* use the curation-example library + PHI-base for retrieval (the blind sandbox is
a testing constraint), and remember the output is a **review-ready draft, not an auto-submission** —
a human still confirms flagged items and enters it into PHI-Canto. To **batch ~10 papers over
several days without hitting usage limits**, use a drop-folder not a scheduler: PDFs into an inbox,
drafts land in an outbox, **"done" = the draft is in the outbox** (that folder is the progress
tracker), do a fixed few per day and come back tomorrow — resumable, and no rate-limit code to get
stuck. For consistency across days, capture the instruction once as a small `batch-curate` skill.
**See:** `scripts/e2e/`; `skills/canto-entry-queue/SKILL.md`.
