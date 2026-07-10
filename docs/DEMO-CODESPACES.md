# 🚀 Demo: Curate an Article in GitHub Codespaces

This walkthrough lets a colleague run the curation pipeline end-to-end **in the browser**,
with no local setup. It uses an **open-access** paper (the demo environment is for public,
generic data only — no unpublished material).

## 1. Open a Codespace

On the GitHub repo page (`PHI-base/phi-weaver`): **Code ▸ Codespaces ▸ Create codespace on main**.

The devcontainer builds automatically and:
- installs Python 3.11, `git`, `gh`, Node
- runs `pip install -r requirements.txt` (PDF conversion needs **PyMuPDF**; live
  UniProt/OLS lookups need **requests**)
- installs the Claude Code VS Code extension (`anthropic.claude-dev`)
- sets `PHI_CURATION_ENV=codespace`

Wait for the terminal to show setup is complete.

## 1b. Verify the checkout (optional, ~1 s)

```bash
python3 scripts/smoke_test.py
```

This network-free check confirms the tooling imports, the storage folders bootstrap, the
tracking DB builds, and the tests pass. All green means you're good to go.

## 2. Storage is already configured

Because `PHI_CURATION_ENV=codespace` is set, the pipeline automatically uses
**`demo-literature/`** inside the workspace instead of a local `PHI-Canto-Literature/`
folder — so you don't need any of your local storage. The folders appear in the VS Code
file explorer as you go. **No configuration needed.**

Everything reads from and writes to three sub-folders under `demo-literature/`
(at `/workspaces/phi-weaver/demo-literature/`):

| What | Path in the Codespace |
|------|-----------------------|
| **Put articles here (input)** | `demo-literature/active/` |
| Converted markdown + drafts   | `demo-literature/active/` |
| **Finished curations (output)** | `demo-literature/completed/` |
| Extracted figures / images    | `demo-literature/media/` |

When phiweaver drafts a paper it writes three artifacts **next to the draft** in
`demo-literature/active/` (their location follows the draft, not the storage root):

| File | What it is |
|------|-----------|
| `<paper>-phiweaver-DRAFT.md` | the curation draft (the anchor file) |
| `<paper>-phi-canto-entry-queue.md` | the PHI-Canto entry queue (the click-list to enter in Canto) |
| `<paper>-scorecard-PREFILLED.xlsx` | the benchmarking scorecard, header + auto-check pre-filled |

These are working artifacts, so they stay in `active/` — they are not the finished
curation. `complete-paper` moves the PDF and notes into `completed/`; move these three
yourself if you want them filed there too.

> ⚠️ **`demo-literature/` is gitignored and lives only inside this Codespace** — it is
> never pushed to GitHub or synced back to your local `PHI-Canto-Literature/`. **Download
> anything you want to keep before deleting the Codespace** (in the file explorer,
> right-click a file or the `demo-literature/` folder → **Download**; folders come down as
> a zip). See *Persistence* under Notes & limitations below.

(To use a different location instead: `export PHI_LITERATURE_ROOT=/some/path` — the
pipeline creates `active/`, `completed/`, and `media/` underneath it.)

## 3. Get an open-access PDF into the Codespace

Either **drag-and-drop** a PDF into the VS Code file explorer, or fetch one by URL:

```bash
curl -L -o paper.pdf "https://<open-access-pdf-url>"
```

## 4. Convert + stage the paper

```bash
python3 11-CLAUDE-AI/curation_pipeline.py auto-process paper.pdf
```

This copies the PDF into `demo-literature/active/`, converts it to structured markdown
(with extracted figures), and reports where everything landed. Open the generated
`*_converted.md` to review it.

## 5. Curate with Claude

Open the Claude Code panel (the Anthropic extension) and ask it to analyse the converted
markdown — extract genes/organisms, suggest UniProtKB IDs and PHIPO/GO terms, and draft
the annotation records. This is the same assisted-curation workflow used locally.

### Curating several papers at once

You **can** stage a whole batch up front — drop all 10 PDFs into `demo-literature/active/`
(or `auto-process` each one), then ask Claude to curate them. But **curation must run
sequentially, one paper at a time** — do not curate papers in parallel.

- Claude drafts **one paper per subagent, and each draft lands to disk before the next
  starts.** This keeps each paper's context isolated (no genes/hosts/strains/figures
  bleeding between papers) and means an interrupted or timed-out Codespace keeps every
  draft already completed.
- So the workflow is: **batch the PDFs in → ask for curation → drafting runs sequentially**,
  writing each paper's `-phiweaver-DRAFT.md`, `-phi-canto-entry-queue.md`, and
  `-scorecard-PREFILLED.xlsx` into `active/` as it goes.
- Running papers in parallel is discouraged: it risks entity bleed-through, contends on the
  shared SQLite tracking DB, and burns concurrent rate limit and cost for no reliability gain.

## 6. Finish

```bash
python3 11-CLAUDE-AI/curation_pipeline.py complete-paper paper.pdf "Demo curation summary"
```

This moves the PDF, curation notes, and media into `demo-literature/completed/`.

---

## Notes & limitations

- **Database tracking**: the SQLite tracking DB is gitignored, so a fresh Codespace has
  none. The conversion/curation demo works without it; session-logging steps that need the
  DB will simply skip or require a one-time schema init.
- **Data policy**: use only **published, open-access** papers in Codespaces — see the
  environment note the devcontainer writes to `~/.claude/CLAUDE.md`.
- **Persistence**: `demo-literature/` is gitignored and lives in the Codespace only; it is
  not pushed back to the repo. Download anything you want to keep before deleting the
  Codespace.
- For the full storage/configuration reference, see
  **[STORAGE-CONFIGURATION.md](STORAGE-CONFIGURATION.md)**.
