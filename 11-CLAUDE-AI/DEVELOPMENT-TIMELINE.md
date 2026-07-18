---
created: 2026-07-18
type: timeline
tags: [development, timeline, auto-generated]
---

# PHI-Canto Development Timeline

*Auto-generated from session logs - System development only (excludes content curation)*

**Last Updated**: 2026-07-18 13:08:49
**Development Sessions**: 21


## 2026-07-17
### Automation
- ✅ **PHIPO PR workflow + offline PHIPO lookup + species-neutrality**: **Acted on James's emails: PHIPO term requests now go as PRs, not issues.** Cloned PHI-base/phipo (`/mnt/z/Computer/GITHUBrepositories/phipo`; clone on native fs then copy — chmod fails on `/mnt/z`; PRs target `master`; CI runs ODK QC so no local `robot`). Opened **[phipo#454](https://github.com/PHI-base/phipo/pull/454)** (`PHIPO:0001456` deoxynivalenol absent from cell) — CI green, awaiting James. **Finding:** #452's term already existed as `PHIPO:0000503`, obsoleted in 2019 and never re-created — OLS *search* hides deprecated terms so #452 was blind to it; the **parallel-terms test** (pyocyanin/gliotoxin kept theirs) shows it's an oversight → `obsolete-terms-are-fossils` memory + skill step 5. **Resolved PHIPO lookup offline** (`f9b7890`): vendored `phipo-base.obo` (release 2026-03-12); `map_phenotype` + `validate_ontology_ids` drop OLS for PHIPO (kept for GO); `--include-obsolete` surfaces deprecated terms; two files never conflated (release vs edit — `PHIPO:0001456` correctly validates not_found). Removes the benchmark sandbox's need for a PHIPO exception (**tool, not answer**). **Real bug fixed:** the borrowed scorer could never return `no_match` (one generic token carried a match; "phenotype" matched everything) — silently broke gap detection; fixed with **IDF weighting** in shared `text_score.py`, `map_condition` fixed too (`d08946e`). **L8 + false gap corrected:** PHIPO is **species-neutral by design** (verified: conidiation/appressorium/mycelium have zero label hits; species words live in EXACT synonyms) — retries species-specific→neutral and process→entity find `PHIPO:0000061`, closing the phantom "complete loss of conidiation" gap; curator ruling "entity absent covers process failed". **Meta (user noticed fixes taking longer):** cost is **doc duplication, not tangled code** — tightened L8 + FAQ back to pointers, canonical detail in the skill (`196dbea`). Curator rulings: **#4 strain 2035 + K3V6Z9** resolved & closed; **#6 CaCl₂→PHIPO:0001303** clean but **DON→PHIPO:0000219 tripped the L7 context guard** (measured in vitro) — user dropped the topic, #6 draft edits reverted. 283 tests green; 13 commits on `main`, unpushed.

## 2026-07-02
### Architecture
- ✅ **Post-modularity improvements + plug-in design**: Prioritised outstanding work; wrote `docs/PLUGIN-ARCHITECTURE.md` (plug-in host + local AI on ROGER; strawman). Shipped 8 commits: Group A cleanups, caption→phenotype→PHIPO tool (`map_phenotype` + 12 tests, wired into phipo-mapping), tracking-DB canonical-path fix, reorganiser config fix, two new skills (genotype-creation, phenotype-annotation → 6 total), interaction counts derived from notes, and split the 11-CLAUDE-AI grab-bag into `vault-ops/` + engine decoupling. Smoke 7/7, 62 tests.

## 2026-06-11
### Architecture
- ✅ **Modularity P5 — DB migrations**: Namespaced versioned migration runner `phiweaver/tracking/migrations.py` (baseline = core v1; modules register their own namespace without editing core) + data-returning `repository.py` (queries testable without stdout); `create_schema()` now runs migrations. Pre-existing DBs upgrade losslessly. 48 tests, smoke 7/7.
### Architecture
- ✅ **Modularity P2 — module contract**: Shared envelope `phiweaver/common/` (utc_now/make_getter/ResponseCache) used by both lookup tools; machine-readable skill frontmatter (backing_script/tests/inputs/outputs); `phiweaver/registry.py` generates+enforces `skills/REGISTRY.md` (smoke 7th check); `docs/ADDING-A-MODULE.md`. 39 tests, smoke 7/7.
### Automation
- ✅ **Modularity P1 — phiweaver package**: Stood up importable `phiweaver/` package (lookup/tracking/pipeline + smoke) with `pyproject.toml`; moved tools/db/pipeline/tests in, rewrote imports, added `repo_root()`, removed all engine/test sys.path glue; thin shims keep old commands working. Run-from-root (install optional, PEP 668). Also completes P3. 31 tests + smoke green.
### Architecture
- ✅ **Overview One-Pager**: Verified vault still fully functional (31 tests, smoke 6/6, real CLIs); wrote factual one-page overview `docs/OVERVIEW.md` (capabilities, architecture, future improvements).
### Architecture
- ✅ **Modularity Assessment**: Evaluated vault modularity (parts independently updatable/testable + future specialised modules); found grab-bag `11-CLAUDE-AI/`, sys.path glue, no package, no DB migrations, prose-only skill→tool links. Wrote phased plan to `docs/MODULARITY-PLAN.md`. No code changes.

## 2026-06-10
### Infrastructure
- ✅ **PHI-Weaver Sync, Restructure & Rebrand**: Synced renamed PHI-base/phi-weaver remote, fixed CRLF churn, made storage portable + Codespaces support, removed MySQL, renamed mysql-setup→db, docs/ move, full rebrand to PHI-Weaver.

## 2026-05-07
### Automation
- ✅ **PHI-Curation-Framework Repository Prep**: Prepared complete vault for GitHub sharing: sanitized personal configs, created comprehensive README, established collaborative workflow.
### Automation
- ✅ **External Storage Migration**: Infrastructure improvement: separated development vault from content storage, updated automation, improved performance.

## 2026-04-24
### Architecture
- ✅ **System Architecture & Funding Strategy**: Added system architecture documentation, created implementation assessment, developed funding framework

## 2026-04-23
### Automation
- ✅ **Chen-2020 Curation & File Organization**: Completed Chen 2020 F. graminearum curation, fixed file organization automation, created wrapper scripts

## 2026-04-22
### Automation
- ✅ **Curation Automation**: Complete workflow automation system: PDF processing, database integration, session management, documentation

## 2026-04-20
### Knowledge Management
- ✅ **PHI-Canto Documentation**: Integrated comprehensive PHI-Canto curation documentation into vault protocols, training, and standards

## 2026-04-19
### Knowledge Management
- ✅ **PDF-Convert Skill**: Professional skill creation: advanced caption extraction, quality validation, complete documentation, codebase organization

## 2026-04-18
### Analytics
- ✅ **Database Integration**: Tested integrated session logging system
### Infrastructure
- ✅ **MySQL integration**: Hybrid tracking system setup with database schema, Python integration, progress analytics

## 2026-04-12
### Infrastructure
- ✅ **Vault maintenance**: test.md created, tmux session setup for PHI-Canto vault

## 2026-04-11
### Infrastructure
- ✅ **Vault setup**: Git repository initialization, .gitignore configuration, template file exclusion
### Infrastructure
- ✅ **Vault maintenance**: Enhanced CLAUDE.md session protocol, attempted git setup
### Infrastructure
- ✅ **Vault setup**: Initial Claude Code setup, Obsidian CLI config, session log infrastructure

---

## Timeline Generation

This timeline is automatically generated from session logs using:
```bash
python3 11-CLAUDE-AI/generate_dev_timeline.py
```

**Development Filter Criteria**:
- Infrastructure, automation, system architecture
- Tool development and workflow improvements
- Performance optimizations and migrations
- Documentation and protocol enhancements

**Excluded**: Content curation, literature processing, paper annotations (tracked separately in session logs)

*For complete activity including content work, see: [[SESSION-LOGS/Session-Logs-INDEX]]*
