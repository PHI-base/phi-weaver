# Curation benchmarking

`PHI-Weaver-Curation-Scorecard.xlsx` — a per-paper scoring matrix for benchmarking curation
quality, designed so **phiweaver pre-fills the machine-checkable parts and a human reviews the
judgement calls**.

## Sheets
- **Guide** — purpose, the rating rubric, the scoring rule, and how to use it.
- **Scorecard** — the per-paper template (copy the tab for each paper). Items are grouped by
  annotation level (entity → gene → genotype → metagenotype → phenotype → detail). Two scoring
  inputs per item:
  - *phiweaver auto-check* — filled automatically: does the identifier/term exist and is it
    current (UniProtKB via `query_uniprot`; GO/PHIPO via `validate_ontology_ids`).
  - *Reviewer rating* — the human decides Correct / Needs improvement / Incorrect / Not
    applicable (dropdown). Points and the overall accuracy % compute automatically.
  - A **Completeness** block records curatable items in the paper vs captured, because
    correctness alone doesn't reveal what was missed.
- **Summary** — one row per scored paper, to track accuracy + completeness over time.

## Scoring
Correct = 1, Needs improvement = 0.5, Incorrect = 0; Not applicable is excluded.
Overall accuracy = points ÷ applicable items. Completeness = captured ÷ curatable.

## Prefilling from a phiweaver draft (single or batch)
`fill_scorecard.py` reads a draft's machine-readable auto-check block (the ```json block in
the curation-example template) and writes a copy of the scorecard with the **header and the
phiweaver auto-check column pre-filled** — the reviewer rating column stays blank by design.
```
python3 fill_scorecard.py path/to/<paper>-phiweaver-DRAFT.md          # one scorecard next to it
python3 fill_scorecard.py active/*-phiweaver-DRAFT.md                  # a batch, one each
```
Needs openpyxl. Close the target `.xlsx` in Excel before rerunning (an open file is locked).
The auto-check column reflects only the machine-checkable items (ID validity, term
existence/obsolescence); the curator still fills every rating and the completeness block.

## Batch review dashboard
For unattended batch drafting, phiweaver records what it can't resolve as **structured flags**
(category + detail) and a **triage** verdict in each draft's json block, instead of asking
questions mid-run. Roll them up into one review dashboard:
```
python3 -m phiweaver.batch_summary /path/active/*-phiweaver-DRAFT.md --out BATCH-REVIEW.md --csv batch.csv
```
It lists every paper most-in-need-of-attention first (triage, auto-check signal, flags), then
groups the flags by category across the batch so you can work through them (e.g. resolve all
`needs_accession` at once). Pure stdlib. The human answers the flags at review time — nothing is
asked during drafting.

## Benchmark integrity (scoring against your own gold standards)
When you score phiweaver against papers you have **already curated**, keep the comparison honest:
- **Blind drafting** — phiweaver gets only the paper + reference databases (UniProt, EBI OLS —
  which a human curator uses too). The gold-standard curation is used only at scoring time, never
  given to phiweaver as input.
- **No PHI-base access** — phiweaver must not read the existing curation from PHI-base / PHI-Canto.
  Web access to those hosts is **denied** in `.claude/settings.json`
  (`WebFetch(domain:*.phi-base.org)`, `www.phi-base.org`, `canto.phi-base.org`,
  `phi5.phi-base.org`). The curation tools only reach UniProt + EBI OLS, not PHI-base. Note:
  `.claude/` is gitignored here, so each curator adds this deny locally (or an admin enables it
  org-wide in managed settings). Takes effect in a **freshly started** Claude session.
  - The PHI-base **data also live on GitHub** (`github.com/PHI-base`, raw files via
    `raw.githubusercontent.com`) — a leakage source too, but it **cannot be cleanly domain-denied**
    (GitHub also hosts the phi-weaver tooling, and the `gh` CLI / `git clone` bypass a WebFetch
    deny). For GitHub-level protection use the **allowlist** below.
  - **Airtight option (recommended for scored runs):** a **network-sandbox allowlist** permitting
    only UniProt + EBI OLS and denying all other network. A blind benchmark needs nothing else
    (paper is local), so this excludes PHI-base's website *and* GitHub with no enumeration or bypass.
- **No leakage** — exclude a paper's **own** gold standard from the retrieval example library when
  benchmarking that paper, or phiweaver just retrieves the answer and looks artificially perfect.

Report the human-reviewed curated papers and a **held-out gold-standard control set** (drafts
scored against the known-correct curation) side by side.

### Running a locked-down benchmark session (network allowlist)
`benchmark-sandbox.settings.json` (in this folder) is an **opt-in** profile that runs Claude with
the network **allowlisted to UniProt + EBI OLS only** — no PHI-base, no GitHub, no other web.
Launch a scored benchmark session with it:
```
claude --settings 07-Standards/curation-benchmarking/benchmark-sandbox.settings.json
```
- **Requires bubblewrap** (`bwrap`) — the sandbox needs it. Install first (`sudo apt-get install
  bubblewrap`, or your distro's equivalent; on WSL, inside the WSL distro). `failIfUnavailable:
  true` means the session **refuses to start** if the sandbox can't run, so you never benchmark
  unsandboxed by accident.
- Use it **only for scored benchmark drafting** — it blocks GitHub, so don't push/develop in it.
- **Test once** after installing bwrap: in a session started with this profile, confirm
  `python3 -m phiweaver.lookup.map_phenotype "reduced virulence"` still works (UniProt/OLS
  reachable) and that fetching a PHI-base URL is blocked, before relying on it for scoring.

## Notes
- Confirm whether *physical / molecular interaction* is in PHI-Canto's phenotype scope before
  treating it as a scored row.
- A curation scored all-Correct with full completeness is, by definition, a validated
  gold-standard — add it to `../curation-examples/`.
- The `.xlsx` is generated by `make_scorecard.py` in this folder; to change the item list or
  layout, edit that generator and rerun it (needs openpyxl), or just edit the spreadsheet
  directly.
