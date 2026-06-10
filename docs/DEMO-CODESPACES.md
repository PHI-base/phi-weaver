# 🚀 Demo: Curate an Article in GitHub Codespaces

This walkthrough lets a colleague run the curation pipeline end-to-end **in the browser**,
with no local setup. It uses an **open-access** paper (the demo environment is for public,
generic data only — no unpublished material).

## 1. Open a Codespace

On the GitHub repo page (`PHI-base/phi-weaver`): **Code ▸ Codespaces ▸ Create codespace on main**.

The devcontainer builds automatically and:
- installs Python 3.11, `git`, `gh`, Node
- runs `pip install -r requirements.txt` (this brings in **PyMuPDF**, the PDF converter's
  only dependency)
- installs the Claude Code VS Code extension (`anthropic.claude-dev`)
- sets `PHI_CURATION_ENV=codespace`

Wait for the terminal to show setup is complete.

## 2. Storage is already configured

Because `PHI_CURATION_ENV=codespace` is set, the pipeline automatically uses
**`demo-literature/`** inside the workspace — you'll see the folders appear in the file
explorer as you go. **No configuration needed.**

(To use a different location instead: `export PHI_LITERATURE_ROOT=/some/path`.)

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
