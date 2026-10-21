"""Re-check the semantics stage against human-reviewed FAILs (data/findings/reviews.jsonl).

For every reviewed id whose cause tag is a semantics problem (and for every confirmed error, which
must stay visible) this recomputes Semantics with the current rules, optionally runs the verify stage
on exactly those ids (through its CLI, so stages stay decoupled), and reports per cause class how
many are now skipped, how many are still checkable, and what verify now says.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

from formulaci.schemas import Formula, Parsed, Semantics, Verdict, read_jsonl
from formulaci.semantics.rules import infer

SEMANTICS_CLASSES = ("special_algebra", "wrong_domain_or_constant", "defining_equation_or_solve",
                     "intentionally_false_in_context", "approximation_or_rounding", "notation_or_convention")


def _tag(row) -> str | None:
    m = re.match(r"\[(\w+)\]", row["review"]["notes"])
    return m.group(1) if m else None


def check(reviews="data/findings/reviews.jsonl", formulas="data/raw/formulas.jsonl", parsed="data/parsed/parsed.jsonl",
          old_semantics="data/semantics/semantics.jsonl", out_dir="data/semantics/review_check", verify=True) -> dict:
    rows = [json.loads(l) for l in Path(reviews).read_text().splitlines() if l.strip()]
    cls = {}
    for r in rows:
        if r["review"]["status"] == "confirmed_error":
            cls[r["formula_id"]] = "confirmed_error"
        elif _tag(r) in SEMANTICS_CLASSES:
            cls[r["formula_id"]] = _tag(r)
    ids = set(cls)
    F = {f.formula_id: f for f in read_jsonl(formulas, Formula) if f.formula_id in ids}
    P: dict[str, list[Parsed]] = defaultdict(list)
    for p in read_jsonl(parsed, Parsed):
        if p.formula_id in ids:
            P[p.formula_id].append(p)
    old = {s.formula_id: s for s in read_jsonl(old_semantics, Semantics) if s.formula_id in ids} if Path(old_semantics).exists() else {}
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    new = {}
    for fid in sorted(ids):
        pieces = sorted(P[fid], key=lambda p: (p.index_in_chain is None, p.index_in_chain or 0))
        new[fid], _ = infer(F.get(fid), pieces)
    (out / "parsed.jsonl").write_text("".join(p.model_dump_json() + "\n" for fid in sorted(ids) for p in P[fid]))
    (out / "semantics.jsonl").write_text("".join(new[f].model_dump_json() + "\n" for f in sorted(ids)))
    verdicts = {}
    if verify:
        vpath = out / "verdicts.jsonl"
        subprocess.run([sys.executable, "-m", "formulaci.cli", "verify", "run", "--parsed", str(out / "parsed.jsonl"),
                        "--semantics", str(out / "semantics.jsonl"), "--out", str(vpath), "--force", "--quiet"],
                       check=True, stdout=subprocess.DEVNULL)
        verdicts = {v.formula_id: v for v in read_jsonl(vpath, Verdict)}
    report = {}
    for c in SEMANTICS_CLASSES + ("confirmed_error",):
        members = sorted(f for f in ids if cls[f] == c)
        skipped = Counter(new[f].skip_reason for f in members if not new[f].checkable)
        still = [f for f in members if new[f].checkable]
        vc = Counter(verdicts[f].verdict for f in still if f in verdicts)
        was_skipped = sum(1 for f in members if f in old and not old[f].checkable)
        report[c] = {"n": len(members), "skipped_now": sum(skipped.values()), "skip_reasons": dict(skipped),
                     "checkable_now": len(still), "verdicts_of_checkable": dict(vc), "skipped_before": was_skipped,
                     "still_fail": sorted(f for f in still if f in verdicts and verdicts[f].verdict == "FAIL"),
                     "checkable_ids": still}
    (out / "report.json").write_text(json.dumps(report, indent=1))
    return report


def format_report(rep: dict) -> str:
    L = [f"{'class':34s} {'n':>4s} {'skipped':>8s} {'checkable':>9s}  verify on the checkable ones", "-" * 90]
    tot_n = tot_fixed = 0
    for c, r in rep.items():
        L.append(f"{c:34s} {r['n']:4d} {r['skipped_now']:8d} {r['checkable_now']:9d}  {r['verdicts_of_checkable']}")
        if c != "confirmed_error":
            tot_n += r["n"]
            tot_fixed += r["n"] - len(r["still_fail"])
    L.append("-" * 90)
    L.append(f"semantics-caused false FAILs no longer FAIL: {tot_fixed}/{tot_n}")
    ce = rep.get("confirmed_error", {})
    if ce:
        L.append(f"confirmed real errors still FAIL: {len(ce['still_fail'])}/{ce['n']}  (skipped now: {ce['skip_reasons']})")
    L.append("")
    for c, r in rep.items():
        if c != "confirmed_error" and r["still_fail"]:
            L.append(f"still FAIL [{c}]: " + ", ".join(r["still_fail"]))
    return "\n".join(L)


if __name__ == "__main__":
    print(format_report(check()))
