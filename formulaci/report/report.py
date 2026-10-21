"""Report stage: join all stage outputs, emit findings JSONL + an HTML report.

Owned by the coordinator. Reads:
  data/raw/formulas.jsonl, data/parsed/parsed.jsonl, data/semantics/semantics.jsonl,
  data/verdicts/verdicts.jsonl, and optional data/findings/reviews.jsonl (Finding records
  written by reviewers; merged by formula_id).
Writes:
  data/findings/findings.jsonl and data/findings/report.html
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

from jinja2 import Template

from formulaci.schemas import (Finding, Formula, Parsed, Review, Semantics, Verdict, read_jsonl)

TEMPLATE = Template(autoescape=True, source=r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>formulaci report</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
:root{--bg:#fff;--fg:#1a1a1a;--muted:#666;--line:#e3e3e3;--fail:#b3261e;--inc:#8a6d00;--pass:#2e7d32;--chip:#f3f3f3}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#121212;--fg:#eee;--muted:#aaa;--line:#333;--chip:#222}}
body{margin:0;padding:24px 16px;background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,sans-serif;max-width:1100px;margin-inline:auto}
h1{font-size:24px;margin:0 0 4px}h2{font-size:18px;margin:28px 0 8px}
.muted{color:var(--muted)}table{border-collapse:collapse;width:100%;margin:8px 0}
td,th{border-bottom:1px solid var(--line);padding:6px 8px;text-align:left;vertical-align:top}
th{font-weight:600}code{font-family:ui-monospace,Menlo,monospace;font-size:13px;white-space:pre-wrap;word-break:break-word}
.chip{display:inline-block;padding:1px 8px;border-radius:999px;background:var(--chip);font-size:12px}
.FAIL{color:var(--fail);font-weight:600}.INCONCLUSIVE{color:var(--inc)}.PASS{color:var(--pass)}
.card{border:1px solid var(--line);border-radius:8px;padding:12px 14px;margin:12px 0}
.card .latex{background:var(--chip);padding:8px;border-radius:6px;overflow-x:auto}
details summary{cursor:pointer}
</style></head><body>
<h1>formulaci — formula verification report</h1>
<div class="muted">Generated {{ generated }} · {{ n_formulas }} formulas from {{ n_pages }} pages</div>

<h2>Pipeline coverage</h2>
<table>
<tr><th>Stage</th><th>Outcome</th><th>Count</th></tr>
{% for stage, counts in coverage %}{% for k, v in counts %}<tr><td>{{ stage }}</td><td>{{ k }}</td><td>{{ v }}</td></tr>{% endfor %}{% endfor %}
</table>

<h2>Findings ({{ findings|length }} FAIL{% if n_inconclusive %}, {{ n_inconclusive }} INCONCLUSIVE not shown{% endif %})</h2>
<div class="muted">Review status: {% for k, v in review_counts %}<span class="chip">{{ k }}: {{ v }}</span> {% endfor %}</div>
{% for f in findings %}
<div class="card">
  <div><a href="{{ f.url }}">{{ f.page_title }}</a> <span class="muted">› {{ f.section }}</span>
     <span class="chip {{ f.verdict }}">{{ f.verdict }}</span>
     <span class="chip">review: {{ f.review_status }}</span>
     {% if f.confidence %}<span class="chip">confidence {{ '%.2f'|format(f.confidence) }}</span>{% endif %}</div>
  <div class="latex"><code>{{ f.latex }}</code></div>
  <div>{{ f.reason }}</div>
  {% if f.counterexample %}<details><summary>Counterexample</summary><code>{{ f.counterexample }}</code></details>{% endif %}
  {% if f.notes %}<div class="muted">Reviewer: {{ f.notes }}</div>{% endif %}
  {% if f.suggested_fix %}<div>Suggested fix: <code>{{ f.suggested_fix }}</code></div>{% endif %}
  <details><summary>Context</summary><div class="muted">…{{ f.context_before }} <b>[formula]</b> {{ f.context_after }}…</div>
  <div class="muted">id <code>{{ f.formula_id }}</code></div></details>
</div>
{% endfor %}
</body></html>""")


def _safe_url(u: str) -> str:
    """Only plain https Wikipedia links are rendered as links (everything is autoescaped by Jinja)."""
    return u if isinstance(u, str) and u.startswith("https://en.wikipedia.org/") and "\n" not in u else ""


def _load(data_dir: Path):
    formulas = {f.formula_id: f for f in read_jsonl(data_dir / "raw/formulas.jsonl", Formula)}
    parsed = defaultdict(list)
    for p in read_jsonl(data_dir / "parsed/parsed.jsonl", Parsed):
        parsed[p.formula_id].append(p)
    semantics = {s.formula_id: s for s in read_jsonl(data_dir / "semantics/semantics.jsonl", Semantics)}
    verdicts = {v.formula_id: v for v in read_jsonl(data_dir / "verdicts/verdicts.jsonl", Verdict)}
    reviews = {r.formula_id: r for r in read_jsonl(data_dir / "findings/reviews.jsonl", Finding)}
    return formulas, parsed, semantics, verdicts, reviews


def _coverage(formulas, parsed, semantics, verdicts):
    c_parse = Counter()
    for fid in formulas:
        ps = parsed.get(fid)
        c_parse[ps[0].status if ps else "missing"] += 1
    c_sem = Counter()
    for fid in formulas:
        s = semantics.get(fid)
        c_sem["checkable" if s and s.checkable else (f"skip:{s.skip_reason}" if s else "missing")] += 1
    c_ver = Counter(v.verdict for v in verdicts.values())
    return [("translate", sorted(c_parse.items())), ("semantics", sorted(c_sem.items())),
            ("verify", sorted(c_ver.items()))]


def build_findings(formulas, verdicts, reviews, include_inconclusive=False):
    out = []
    for fid, v in verdicts.items():
        if v.verdict == "FAIL" or (include_inconclusive and v.verdict == "INCONCLUSIVE"):
            prior = reviews.get(fid)
            ce = v.counterexample.model_dump() if v.counterexample else None
            evidence = v.reason + ("\n" + json.dumps(ce, indent=1) if ce else "")
            conf = 0.0
            if v.verdict == "FAIL":
                # crude prior: symbolic disagreement + many regimes failing raises confidence
                regimes_failing = sum(1 for r in v.regimes if r.n_points and r.n_fail > r.n_points / 2)
                conf = min(1.0, 0.4 + 0.1 * regimes_failing + (0.2 if v.symbolic == "not_equal" else 0.0))
            out.append(Finding(
                formula_id=fid, verdict=v.verdict, confidence=conf,
                review=prior.review if prior else Review(),
                suggested_fix=prior.suggested_fix if prior else None,
                evidence=prior.evidence if prior and prior.evidence else evidence,
            ))
    out.sort(key=lambda f: (f.review.status != "confirmed_error", -f.confidence))
    return out


def run(data_dir="data", out_dir=None, include_inconclusive=False):
    data_dir = Path(data_dir)
    out_dir = Path(out_dir) if out_dir else data_dir / "findings"
    out_dir.mkdir(parents=True, exist_ok=True)
    formulas, parsed, semantics, verdicts, reviews = _load(data_dir)
    findings = build_findings(formulas, verdicts, reviews, include_inconclusive)
    (out_dir / "findings.jsonl").write_text("".join(f.model_dump_json() + "\n" for f in findings))

    rows = []
    for f in findings:
        fm = formulas.get(f.formula_id)
        v = verdicts[f.formula_id]
        rows.append(dict(
            formula_id=f.formula_id, verdict=f.verdict, confidence=f.confidence,
            review_status=f.review.status, notes=f.review.notes,
            suggested_fix=f.suggested_fix or "",
            url=_safe_url(fm.url if fm else ""), page_title=(fm.page_title if fm else f.formula_id),
            section=(fm.section if fm else ""), latex=(fm.latex if fm else ""),
            reason=v.reason,
            counterexample=json.dumps(v.counterexample.model_dump(), indent=1) if v.counterexample else "",
            context_before=(fm.context_before if fm else "")[-200:],
            context_after=(fm.context_after if fm else "")[:200],
        ))
    n_inc = sum(1 for v in verdicts.values() if v.verdict == "INCONCLUSIVE") if not include_inconclusive else 0
    page = TEMPLATE.render(
        generated=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        n_formulas=len(formulas), n_pages=len({f.page_id for f in formulas.values()}),
        coverage=_coverage(formulas, parsed, semantics, verdicts), findings=rows,
        n_inconclusive=n_inc,
        review_counts=sorted(Counter(f.review.status for f in findings).items()),
    )
    (out_dir / "report.html").write_text(page)
    return {"findings": len(findings), "inconclusive": n_inc, "formulas": len(formulas),
            "report": str(out_dir / "report.html")}
