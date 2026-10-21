#!/usr/bin/env bash
# Run translate -> semantics -> verify -> report on data/raw/formulas.jsonl. Resumable; rerun to top up.
set -uo pipefail
cd "$(dirname "$0")/.."
W=${WORKERS:-6}
F=""; [ "${FORCE:-0}" = "1" ] && F="--force"
echo "[$(date +%T)] translate" ; uv run formulaci translate run --in data/raw/formulas.jsonl --out data/parsed/parsed.jsonl --workers "$W" $F
echo "[$(date +%T)] semantics" ; uv run formulaci semantics run --formulas data/raw/formulas.jsonl --parsed data/parsed/parsed.jsonl --out data/semantics/semantics.jsonl $F
echo "[$(date +%T)] verify"    ; uv run formulaci verify run --parsed data/parsed/parsed.jsonl --semantics data/semantics/semantics.jsonl --out data/verdicts/verdicts.jsonl --workers "$W" --quiet $F
echo "[$(date +%T)] report"    ; uv run formulaci report run --data-dir data
echo "[$(date +%T)] done"
