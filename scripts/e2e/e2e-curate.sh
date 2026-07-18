#!/usr/bin/env bash
# e2e-curate.sh — end-to-end curation test, unattended.
#
#   paper text  --(headless claude, blind)-->  draft  --(deterministic)-->  score vs gold
#
# This is the "wrapping" of the manual draft step: it launches a headless Claude agent to
# curate one paper, then scores the draft's identifiers against the known-correct curation.
# Every heavy component already exists (the curation skills, the sandbox profile, the
# scorecard tool); this just chains them so the whole thing runs without a human in the room.
#
# Usage:
#   e2e-curate.sh <paper.md> <gold.md> [--out-dir DIR] [--no-sandbox] [--threshold F]
#
# Notes:
#   * With the sandbox (default) the agent can only WRITE under /mnt/z/PHI-Canto-Literature,
#     so --out-dir must live there; network is limited to UniProt/EBI (no PHI-base/GitHub).
#   * Leakage is the caller's job: make sure this paper's own gold standard is not readable
#     in the repo while drafting, or the agent just copies the answer.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$HERE/../.." && pwd)"

usage() { echo "usage: $0 <paper.md> <gold.md> [--out-dir DIR] [--no-sandbox] [--threshold F]" >&2; exit 2; }
[ $# -ge 2 ] || usage
PAPER="$1"; GOLD="$2"; shift 2

OUTDIR="/mnt/z/PHI-Canto-Literature/e2e-test"; SANDBOX=1; THRESH=0.5
while [ $# -gt 0 ]; do
  case "$1" in
    --out-dir)    OUTDIR="$2"; shift 2;;
    --no-sandbox) SANDBOX=0; shift;;
    --threshold)  THRESH="$2"; shift 2;;
    *) usage;;
  esac
done
mkdir -p "$OUTDIR"

STEM="$(basename "$PAPER")"; STEM="${STEM%_converted.md}"; STEM="${STEM%.md}"
DRAFT="$OUTDIR/${STEM}-phiweaver-DRAFT.md"

SETTINGS=()
[ "$SANDBOX" = 1 ] && SETTINGS=(--settings "$REPO/07-Standards/curation-benchmarking/benchmark-sandbox.settings.json")

read -r -d '' PROMPT <<EOF || true
You are curating ONE paper for PHI-Canto in blind benchmark mode.
Read ONLY the paper at this path: $PAPER
Follow the phiweaver curation skills in order: paper-triage, uniprot-lookup,
genotype-creation, phipo-mapping, phenotype-annotation, curation-qc. Validate every
ontology ID. Do NOT search for or read any existing gold-standard curation of this paper.
Write the finished curation draft — INCLUDING a fenced \`\`\`json auto_check block — to
exactly this path, and print nothing else:
$DRAFT
EOF

echo ">> [1/3] drafting headlessly (sandbox=$SANDBOX) — this is the slow part ..."
claude -p "$PROMPT" --permission-mode acceptEdits "${SETTINGS[@]}"

[ -f "$DRAFT" ] || { echo "!! no draft produced at $DRAFT" >&2; exit 1; }
echo ">> draft written: $DRAFT"

echo ">> [2/3] prefilling objective scorecard (best-effort) ..."
python3 "$REPO/07-Standards/curation-benchmarking/fill_scorecard.py" "$DRAFT" \
  --out "$OUTDIR/${STEM}-scorecard.xlsx" 2>/dev/null \
  && echo "   scorecard: $OUTDIR/${STEM}-scorecard.xlsx" \
  || echo "   (skipped — needs a json auto_check block + openpyxl)"

echo ">> [3/3] scoring draft identifiers vs gold ..."
exec python3 "$HERE/score_against_gold.py" "$DRAFT" "$GOLD" --threshold "$THRESH"
