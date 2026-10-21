"""Coverage statistics over a parsed.jsonl (+ the formulas it came from)."""
from __future__ import annotations

import re
from collections import Counter, defaultdict

from formulaci.schemas import Parsed

EQUATION_KINDS = {"equation", "chain", "definition_like"}


def failure_category(r: Parsed) -> str:
    if r.status == "ok":
        return "ok"
    if r.has_unsupported:
        return "unsupported:" + r.has_unsupported[0]
    if r.error:
        e = r.error.split(" | ")[0]
        e = re.sub(r"^(ParseError|ValueError|TypeError|AttributeError|KeyError|IndexError): ", "", e)
        e = re.sub(r"'[^']*'|\"[^\"]*\"", "<x>", e)
        e = re.sub(r"\\\\?[A-Za-z]+", lambda m: m.group(0) if e.startswith("unknown command") else "<cmd>", e)
        return "error:" + e[:60]
    if r.kind == "other":
        return "not_checkable:" + (r.relation or "no_relation")
    return "not_checkable"


def summarize(records: list[Parsed]) -> dict:
    by_formula: dict[str, list[Parsed]] = defaultdict(list)
    for r in records:
        by_formula[r.formula_id].append(r)
    n_formulas = len(by_formula)
    eq_formulas = {fid: rs for fid, rs in by_formula.items() if any(r.kind in EQUATION_KINDS for r in rs)}
    eq_any_ok = sum(1 for rs in eq_formulas.values()
                    if any(r.status == "ok" and r.kind in EQUATION_KINDS for r in rs))
    eq_all_ok = sum(1 for rs in eq_formulas.values()
                    if all(r.status == "ok" for r in rs if r.kind in EQUATION_KINDS))
    eq_records = [r for r in records if r.kind in EQUATION_KINDS]
    eq_rec_ok = sum(1 for r in eq_records if r.status == "ok")
    status = Counter(r.status for r in records)
    kinds = Counter(r.kind for r in records)
    fails = Counter(failure_category(r) for r in eq_records if r.status != "ok")
    all_fails = Counter(failure_category(r) for r in records if r.status != "ok")
    lark = sum(1 for r in records if r.translator.startswith("sympy-lark"))
    return {
        "formulas": n_formulas,
        "records": len(records),
        "equation_formulas": len(eq_formulas),
        "equation_formulas_any_ok": eq_any_ok,
        "equation_formulas_all_ok": eq_all_ok,
        "equation_records": len(eq_records),
        "equation_records_ok": eq_rec_ok,
        "status": dict(status),
        "kinds": dict(kinds),
        "lark_fallback_records": lark,
        "top_equation_failures": fails.most_common(25),
        "top_failures_all": all_fails.most_common(25),
    }


def format_summary(s: dict) -> str:
    def pct(a, b):
        return f"{100 * a / b:.1f}%" if b else "n/a"
    lines = [
        f"formulas: {s['formulas']}  records: {s['records']}  status: {s['status']}",
        f"kinds: {s['kinds']}",
        f"equation-kind formulas: {s['equation_formulas']}  "
        f"with >=1 ok equation record: {s['equation_formulas_any_ok']} ({pct(s['equation_formulas_any_ok'], s['equation_formulas'])})  "
        f"all equation records ok: {s['equation_formulas_all_ok']} ({pct(s['equation_formulas_all_ok'], s['equation_formulas'])})",
        f"equation-kind records: {s['equation_records']}  ok: {s['equation_records_ok']} "
        f"({pct(s['equation_records_ok'], s['equation_records'])})   lark fallback records: {s['lark_fallback_records']}",
        "top failure categories (equation-kind records):",
    ]
    for cat, n in s["top_equation_failures"]:
        lines.append(f"  {n:6d}  {cat}")
    return "\n".join(lines)
