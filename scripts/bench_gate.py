"""Precision gate over bench metrics: refuses any change that trades precision for coverage.

    uv run python scripts/bench_gate.py [--bench-dir data/bench] [--baseline data/bench/baseline.json]

Fails (exit 1) when a known-true identity FAILs, an injected error PASSes, end-to-end recall drops by
more than RECALL_SLACK against the baseline, or more than PASS_SLACK fewer known-true identities PASS.
Prints the numbers either way; paste them into the pull request.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

RECALL_SLACK = 0.01   # absolute drop in end-to-end recall allowed
PASS_SLACK = 2        # fewer known-true identities passing allowed


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bench-dir", default="data/bench")
    ap.add_argument("--baseline", default="data/bench/baseline.json")
    ap.add_argument("--write-baseline", action="store_true", help="record the current metrics as the baseline")
    a = ap.parse_args()
    m = json.load(open(Path(a.bench_dir) / "metrics.json"))
    o = m["synthetic"]["overall"]
    good, mut = o["known_good"], o["mutated"]
    now = {"known_good_n": good["n"], "known_good_pass": good["verdicts"]["PASS"], "known_good_fail": good["verdicts"]["FAIL"],
           "mutated_n": mut["n"], "mutated_pass": mut["verdicts"]["PASS"], "mutated_fail": mut["verdicts"]["FAIL"],
           "recall_end_to_end": round(mut["fail_rate"], 4)}
    if a.write_baseline:
        Path(a.baseline).write_text(json.dumps(now, indent=1) + "\n")
        print("baseline written:", now)
        return 0
    base = json.load(open(a.baseline))
    problems = []
    if now["known_good_fail"]:
        problems.append(f"{now['known_good_fail']} known-true identities FAIL (precision gate: must be 0)")
    if now["mutated_pass"]:
        problems.append(f"{now['mutated_pass']} injected errors PASS (must be 0)")
    if now["recall_end_to_end"] < base["recall_end_to_end"] - RECALL_SLACK:
        problems.append(f"recall {now['recall_end_to_end']:.3f} is below baseline {base['recall_end_to_end']:.3f} - {RECALL_SLACK}")
    if now["known_good_pass"] < base["known_good_pass"] - PASS_SLACK:
        problems.append(f"only {now['known_good_pass']} known-true identities PASS (baseline {base['known_good_pass']})")
    print("bench gate")
    for k in now:
        print(f"  {k:20s} {now[k]!s:>8}   baseline {base.get(k, '-')}")
    if problems:
        print("REFUSED:")
        for p in problems:
            print("  -", p)
        return 1
    print("OK: precision 100%, no injected error passes, recall within slack of the baseline")
    return 0


if __name__ == "__main__":
    sys.exit(main())
