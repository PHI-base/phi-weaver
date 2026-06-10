---
created: 2026-04-23
type: documentation
tags: [automation, file-organization, curation]
---

# PHI-Canto Curation File Organization Guide

## Correct Vault Structure

```
03-Media/                    # Images and media files
  └─ Paper-Name/            # One folder per paper
04-Literature/              # Converted papers and curation records  
  ├─ Paper_converted.md     # Converted markdown
  └─ Paper-Curation.md      # PHI-Canto curation record
11-CLAUDE-AI/               # Conversion reports and logs
  └─ Paper_converted_report.json
```

## Proper Conversion Process

### Use the Wrapper Script (Recommended)
```bash
# Converts PDF with automatic file organization
python3 11-CLAUDE-AI/convert-for-curation.py "path/to/paper.pdf"
```

### Manual Conversion (if needed)
```bash
# Use PHI-canto config for proper paths
cd 11-CLAUDE-AI/pdf-convert-skill
python3 pdf-convert.py "paper.pdf" --config phi_canto_config --output-dir "../../04-Literature"
```

## File Movement Commands (if files are in wrong locations)

```bash
# From the repo root

# Move converted markdown to Literature
mv "00-Inbox/To-curate/Paper_converted.md" "04-Literature/"

# Move media folder to vault root
mv "00-Inbox/To-curate/03-Media/Paper-Name" "03-Media/"

# Move conversion report to Claude AI folder  
mv "00-Inbox/To-curate/Paper_converted_report.json" "11-CLAUDE-AI/"

# Clean up empty 03-Media folder in To-curate (if empty)
rmdir "00-Inbox/To-curate/03-Media" 2>/dev/null || true
```

## Chen 2020 Paper Fix Applied

✅ **Fixed locations:**
- `Chen-2020-EnvironMicrobiol-32537857_converted.md` → `04-Literature/`
- `03-Media/Chen-2020-EnvironMicrobiol-32537857/` → vault root `03-Media/`  
- `Chen-2020-EnvironMicrobiol-32537857_converted_report.json` → `11-CLAUDE-AI/`

## Why Proper Organization Matters

1. **WikiLink consistency**: Media links work correctly from Literature folder
2. **Search efficiency**: Files in expected locations  
3. **Automation integration**: Scripts know where to find files
4. **Database linking**: Curation records reference correct paths
5. **Session logging**: Conversion reports properly tracked

## Quick Check Commands

```bash
# Verify file locations
ls -la 04-Literature/*converted*        # Converted papers
ls -la 03-Media/                        # Media folders  
ls -la 11-CLAUDE-AI/*report*           # Conversion reports
```

## Future Prevention

- **Always use**: `convert-for-curation.py` wrapper script
- **Check paths**: Before starting curation work
- **Commit organized**: Files after conversion and organization

---
*Updated after Chen 2020 paper organization fix*