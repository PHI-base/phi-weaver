# 📂 Storage Configuration — Read This First

**New here? This page tells you where the curation pipeline reads and writes files,
and how to point it at your own location.**

This repository (`phi-weaver`) contains the **tools, protocols, and documentation**
for PHI-base curation. The actual **literature content** (PDFs, converted markdown,
figures) is deliberately kept **outside** the repo so the repository stays small and
fast, and so unpublished material isn't committed to GitHub.

## Where files go

The pipeline (`11-CLAUDE-AI/curation_pipeline.py`) uses a single **literature storage
root** with three sub-folders:

| Folder | Purpose | Pipeline term |
|--------|---------|---------------|
| `active/`    | **Input** — PDFs being worked on / converted | `inbox_path` |
| `completed/` | **Output** — finished curations + notes      | `literature_path` |
| `media/`     | Extracted images and figures                 | `media_path` |

## Default location

By default the storage root is a **sibling folder next to this repo**:

```
/mnt/z/
├── phi-weaver/             ← this repo (the tools)
└── PHI-Canto-Literature/   ← literature content (default storage root)
    ├── active/
    ├── completed/
    └── media/
```

You do **not** need to configure anything if your content lives there.

### In GitHub Codespaces (zero config)

When running in a Codespace (the devcontainer sets `PHI_CURATION_ENV=codespace`), the
storage root defaults to **`demo-literature/` inside the repo** instead, so converted
files appear right in the file explorer. It's gitignored, so nothing gets committed.
You can still override it with `PHI_LITERATURE_ROOT` (below). For a full walkthrough see
**[DEMO-CODESPACES.md](DEMO-CODESPACES.md)**.

## Overriding the location (for colleagues / Codespaces / different machines)

If your literature lives somewhere else — a different drive, a shared network path,
or a GitHub Codespace where `/mnt/z/...` doesn't exist — set the
**`PHI_LITERATURE_ROOT`** environment variable. The pipeline reads it at startup and
creates `active/`, `completed/`, and `media/` underneath it.

**One-off (single command):**
```bash
PHI_LITERATURE_ROOT=/path/to/your/literature \
  python3 11-CLAUDE-AI/curation_pipeline.py auto-process ~/Downloads/paper.pdf
```

**Persistent (add to your `~/.bashrc` or `~/.zshrc`):**
```bash
export PHI_LITERATURE_ROOT="$HOME/phi-literature"
```

**Verify what the pipeline will use:**
```bash
PHI_LITERATURE_ROOT=/path/to/check python3 -c "
import sys; sys.path.insert(0, '11-CLAUDE-AI')
from curation_pipeline import CurationPipeline
p = CurationPipeline()
print('storage root:', p.external_storage)
print('  input :', p.inbox_path)
print('  output:', p.literature_path)
"
```

## Notes

- The repo root and tool paths are **auto-detected** from the script location, so the
  repository itself works wherever you clone it — only the *content* location may need
  the override above.
- Keep unpublished annotations and any sensitive material in the storage root
  (outside the repo), **not** committed to git.
