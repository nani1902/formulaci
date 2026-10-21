"""Review export/import: package FAIL verdicts for human or agent review, merge reviews back.

Export writes Markdown batches under data/findings/review/batch_NNN.md, each item carrying everything a
reviewer needs: page, section, raw LaTeX, prose context, the translator's reading of both sides, the
semantics stage's assumptions, the verifier's reason and counterexample. Reviewers answer with Finding
records (JSONL) which `import_reviews` appends to data/findings/reviews.jsonl.
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import sympy

from formulaci.schemas import Finding, Formula, Parsed, Semantics, Verdict, append_jsonl, read_jsonl

_NS = {n: getattr(sympy, n) for n in dir(sympy) if not n.startswith("_")}


def _pretty(srepr: str | None) -> str:
    if not srepr:
        return ""
    try:
        return str(eval(srepr, {"__builtins__": {}}, _NS))
    except Exception:
        return srepr[:200]


def export(data_dir="data", out_dir=None, batch_size=25, limit=0, include_inconclusive=False,
           skip_reviewed=True):
    data_dir = Path(data_dir)
    out_dir = Path(out_dir) if out_dir else data_dir / "findings" / "review"
    out_dir.mkdir(parents=True, exist_ok=True)
    formulas = {f.formula_id: f for f in read_jsonl(data_dir / "raw/formulas.jsonl", Formula)}
    parsed = defaultdict(list)
    for p in read_jsonl(data_dir / "parsed/parsed.jsonl", Parsed):
        parsed[p.formula_id].append(p)
    semantics = {s.formula_id: s for s in read_jsonl(data_dir / "semantics/semantics.jsonl", Semantics)}
    reviewed = {r.formula_id for r in read_jsonl(data_dir / "findings/reviews.jsonl", Finding)} if skip_reviewed else set()
    wanted = {"FAIL"} | ({"INCONCLUSIVE"} if include_inconclusive else set())
    verdicts = [v for v in read_jsonl(data_dir / "verdicts/verdicts.jsonl", Verdict)
                if v.verdict in wanted and v.formula_id not in reviewed and v.formula_id in formulas]
    verdicts.sort(key=lambda v: (v.verdict != "FAIL", formulas[v.formula_id].page_title))
    if limit:
        verdicts = verdicts[:limit]

    batches = [verdicts[i:i + batch_size] for i in range(0, len(verdicts), batch_size)]
    paths = []
    for b, batch in enumerate(batches, 1):
        lines = [f"# Review batch {b:03d} — {len(batch)} items\n",
                 "For each item answer with one JSON line (Finding schema): "
                 '{"formula_id": ..., "verdict": "FAIL", "review": {"status": "confirmed_error"|"false_positive"|"ambiguous", '
                 '"reviewer": "<name>", "notes": "<why, one or two sentences>"}, "suggested_fix": "<corrected LaTeX or null>", '
                 '"evidence": "<independent source or derivation>"}\n']
        for v in batch:
            f = formulas[v.formula_id]
            ps = parsed.get(v.formula_id, [])
            s = semantics.get(v.formula_id)
            lines.append(f"\n---\n## {v.formula_id}\n")
            lines.append(f"- Page: [{f.page_title}]({f.url}) › {f.section or '(lead)'}  · verdict **{v.verdict}**, symbolic {v.symbolic}")
            lines.append(f"- LaTeX: `{f.latex.strip()}`")
            lines.append(f"- Context before: …{f.context_before[-350:].strip()}")
            lines.append(f"- Context after: {f.context_after[:350].strip()}…")
            for p in ps:
                tag = f" (piece {p.index_in_chain})" if p.index_in_chain is not None else ""
                lines.append(f"- Translator read{tag}: `{_pretty(p.lhs)}`  {p.relation or '='}  `{_pretty(p.rhs)}`"
                             + (f"  · notes: {p.notes}" if p.notes else ""))
            if s:
                dom = {k: d.type for k, d in s.domains.items()}
                lines.append(f"- Assumptions: domains {dom}; constants {s.constants}; constraints {s.constraints}")
            lines.append(f"- Verifier: {v.reason}")
            if v.counterexample:
                c = v.counterexample
                lines.append(f"- Counterexample: {c.assignments} → lhs {c.lhs[:40]}, rhs {c.rhs[:40]}, rel diff {c.rel_diff[:12]}")
            regs = ", ".join(f"{r.name} {r.n_fail}/{r.n_points} fail, {r.n_error} err" for r in v.regimes)
            lines.append(f"- Regimes: {regs}")
        p = out_dir / f"batch_{b:03d}.md"
        p.write_text("\n".join(lines) + "\n")
        paths.append(str(p))
    return {"items": len(verdicts), "batches": len(batches), "paths": paths}


def import_reviews(data_dir="data", in_path=None, reviewer=""):
    data_dir = Path(data_dir)
    recs = []
    for line in Path(in_path).read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        d = json.loads(line)
        d.setdefault("verdict", "FAIL")
        rec = Finding.model_validate(d)
        if reviewer and not rec.review.reviewer:
            rec.review.reviewer = reviewer
        recs.append(rec)
    append_jsonl(data_dir / "findings/reviews.jsonl", recs)
    return {"imported": len(recs)}
