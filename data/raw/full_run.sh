#!/bin/zsh
# extract stage full run. Requires FORMULACI_CONTACT in the environment (never stored in files).
# Views pass (all pages) and extraction (all pages, into a side file) share the 200 req/min budget.
cd "$(dirname "$0")/../.."
[ -n "$FORMULACI_CONTACT" ] || { echo "FORMULACI_CONTACT not set" >&2; exit 1; }
FORMULACI_RPS=1.8 uv run python -m formulaci.cli extract pages --out data/raw/pages.txt >> data/raw/pages_build.log 2>&1 &
FORMULACI_RPS=1.0 uv run python -m formulaci.cli extract run --pages data/raw/pages.txt \
  --out data/raw/formulas.next.jsonl >> data/raw/extract_all.log 2>&1
echo "extraction exit $?" >> data/raw/extract_all.log
wait
echo "views exit $?" >> data/raw/pages_build.log
