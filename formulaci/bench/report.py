"""Markdown rendering of ``metrics.json`` -> ``REPORT.md``."""
from __future__ import annotations


def _p(x) -> str:
    return "–" if x is None else f"{100 * x:.1f}%"


def _v(blk: dict, key: str) -> str:
    return str(blk.get("verdicts", {}).get(key, "–"))


def _stage_lines(m: dict) -> list[str]:
    out = ["| set | formulas | translate | semantics | verify | seconds |", "|---|---|---|---|---|---|"]
    for name, run in m.get("runs", {}).items():
        st = run.get("stages", {})

        def cell(s):
            d = st.get(s, {})
            txt = d.get("status", "–")
            if d.get("seconds") is not None:
                txt += f" ({d['seconds']}s)"
            return txt

        out.append(f"| {name} | {run.get('n_formulas', '–')} | {cell('translate')} | {cell('semantics')} | "
                   f"{cell('verify')} | {run.get('seconds', '–')} |")
    details = [f"- `{name}/{s}`: {d.get('detail')}" for name, run in m.get("runs", {}).items()
               for s, d in run.get("stages", {}).items() if d.get("detail")]
    return out + ([""] + details if details else [])


def _table(rows: dict, label: str, with_pr: bool) -> list[str]:
    head = (f"| {label} | n good | n mutated | translate ok (good) | translate ok (mut) | checkable (good) | "
            "good PASS | good FAIL | good INCONCL. |" + (" mut FAIL (recall) | mut INCONCL. | precision |" if with_pr else ""))
    out = [head, "|" + "---|" * (head.count("|") - 1)]
    for k, blk in rows.items():
        g, mu = blk.get("known_good", {}), blk.get("mutated", {})
        line = (f"| {k} | {g.get('n', 0)} | {mu.get('n', 0)} | {_p(g.get('translate_ok_rate'))} | "
                f"{_p(mu.get('translate_ok_rate'))} | {_p(g.get('checkable_rate_given_translated'))} | "
                f"{_v(g, 'PASS')} | {_v(g, 'FAIL')} | {_v(g, 'INCONCLUSIVE')} |")
        if with_pr:
            line += (f" {_v(mu, 'FAIL')} ({_p(blk.get('recall'))}) | {_p(mu.get('inconclusive_rate'))} | "
                     f"{_p(blk.get('precision'))} |")
        out.append(line)
    return out


def render(m: dict) -> str:
    L = ["# formulaci bench report", "", f"Generated {m.get('generated_at')} · total runtime "
         f"{m.get('total_seconds')} s · stages requested: {', '.join(m.get('stages_requested', []))}"
         + (f" · subsample: first {m['limit']} identities" if m.get("limit") else ""), "",
         "## Stage availability", "", *_stage_lines(m), ""]
    syn = m.get("synthetic") or {}
    has_verify = bool(syn.get("overall", {}).get("known_good", {}).get("verdicts"))
    if syn:
        o = syn["overall"]
        g, mu = o["known_good"], o["mutated"]
        L += ["## Synthetic sets (known-good identities + injected mutations)", ""]
        L += [f"- known-good: {g['n']} formulas; mutated: {mu['n']} formulas"]
        if "translate_ok_rate" in g:
            L += [f"- translate `ok` rate: known-good {_p(g['translate_ok_rate'])}, mutated {_p(mu.get('translate_ok_rate'))}"]
        if "checkable_rate_given_translated" in g:
            L += [f"- semantics checkable rate (of translated): known-good {_p(g['checkable_rate_given_translated'])}, "
                  f"mutated {_p(mu.get('checkable_rate_given_translated'))}; end to end: "
                  f"{_p(g['checkable_rate_end_to_end'])} / {_p(mu.get('checkable_rate_end_to_end'))}"]
        if has_verify:
            L += [f"- **precision {_p(o.get('precision'))}** (TP {o['tp']}, FP {o['fp']}); "
                  f"**recall {_p(o.get('recall'))}** end to end, {_p(o.get('recall_given_verified'))} of mutated "
                  f"formulas that reached a PASS/FAIL/INCONCLUSIVE verdict",
                  f"- recall on mutations of identities whose known-good form PASSed: "
                  f"{_p(o.get('recall_on_mutations_of_passing_identities'))} "
                  f"(n={o.get('n_mutations_of_passing_identities')})",
                  f"- known-good verdicts: " + ", ".join(f"{k} {v}" for k, v in g["verdicts"].items()),
                  f"- mutated verdicts: " + ", ".join(f"{k} {v}" for k, v in mu["verdicts"].items()),
                  f"- INCONCLUSIVE rate: known-good {_p(g.get('inconclusive_rate'))}, mutated {_p(mu.get('inconclusive_rate'))}"]
        L += ["", "### Per category", "", *_table(syn.get("per_category", {}), "category", has_verify), ""]
        if syn.get("per_mutation"):
            L += ["### Per mutation type", "",
                  "| mutation | n | translate ok | checkable | FAIL (recall) | recall given verified | PASS (missed) | INCONCL. | SKIP | MISSING |",
                  "|---|---|---|---|---|---|---|---|---|---|"]
            for mt, b in syn["per_mutation"].items():
                L.append(f"| {mt} | {b['n']} | {_p(b.get('translate_ok_rate'))} | "
                         f"{_p(b.get('checkable_rate_given_translated'))} | {_v(b, 'FAIL')} ({_p(b.get('recall'))}) | "
                         f"{_p(b.get('recall_given_verified'))} | {_v(b, 'PASS')} | {_v(b, 'INCONCLUSIVE')} | "
                         f"{_v(b, 'SKIP')} | {_v(b, 'MISSING')} |")
            L.append("")
        if syn.get("per_translator_status"):
            L += ["### Per translator status", "", "| translate status | n good | n mutated | good FAIL | mut FAIL | mut INCONCL. |",
                  "|---|---|---|---|---|---|"]
            for st, b in syn["per_translator_status"].items():
                L.append(f"| {st} | {b['known_good'].get('n', 0)} | {b['mutated'].get('n', 0)} | "
                         f"{_v(b['known_good'], 'FAIL')} | {_v(b['mutated'], 'FAIL')} | {_v(b['mutated'], 'INCONCLUSIVE')} |")
            L.append("")
        if has_verify:
            fps = syn.get("false_positives", [])
            L += [f"### False positives (known-good formulas that got FAIL): {len(fps)}", ""]
            for r in fps:
                cex = r.get("counterexample") or {}
                L.append(f"- `{r['formula_id']}` ({r['category']}) `{r['latex']}` — {r.get('reason', '')} "
                         f"{'· at ' + str(cex.get('assignments')) if cex else ''}")
            missed = syn.get("missed_mutations", [])
            passed = [r for r in missed if r["verdict"] == "PASS"]
            L += ["", f"### Missed mutations: {len(missed)} not flagged ({len(passed)} PASS, "
                  f"{sum(r['verdict'] == 'INCONCLUSIVE' for r in missed)} INCONCLUSIVE, "
                  f"{sum(r['verdict'] in ('SKIP', 'MISSING') for r in missed)} SKIP/MISSING)", "",
                  "Mutations judged PASS (the worst kind of miss):", ""]
            for r in passed:
                L.append(f"- `{r['formula_id']}` [{r['mutation']}: {r.get('detail')}] `{r['latex']}` — {r.get('reason', '')}")
            if not passed:
                L.append("- none")
            L += ["", "The full missed list (with reasons) is in `metrics.json` → `synthetic.missed_mutations`.", ""]
        tf = syn.get("translate_failures_known_good", [])
        if tf:
            L += [f"### Known-good formulas the translator did not handle: {len(tf)}", ""]
            for r in tf[:60]:
                L.append(f"- `{r['formula_id']}` ({r['category']}, {r['translate']}) `{r['latex']}`")
            if len(tf) > 60:
                L.append(f"- … {len(tf) - 60} more in `metrics.json`")
            L.append("")
    lac = m.get("lacast") or {}
    if lac:
        o = lac["overall"]
        L += ["## LaCASt Wikipedia gold set (95 hand-evaluated formulas)", "",
              "The LaCASt human labels grade *translation* correctness (semantic LaTeX / Mathematica / Maple),",
              "not mathematical truth; verify FAILs here are leads for review, not scored false positives.", "",
              f"- formulas: {o['n']}; translate ok: {_p(o.get('translate_ok_rate'))}; checkable: "
              f"{_p(o.get('checkable_rate_end_to_end'))} end to end"]
        if o.get("verdicts"):
            L.append("- verdicts: " + ", ".join(f"{k} {v}" for k, v in o["verdicts"].items()))
        if lac.get("translate_vs_human_labels"):
            L += ["", "| LaCASt human label | our translate status counts |", "|---|---|"]
            for k, v in lac["translate_vs_human_labels"].items():
                L.append(f"| {k} | {', '.join(f'{s}: {n}' for s, n in sorted(v.items(), key=lambda kv: str(kv[0])))} |")
        if lac.get("fails_for_review"):
            L += ["", "FAIL verdicts to review:", ""]
            for r in lac["fails_for_review"]:
                L.append(f"- `{r['formula_id']}` ({r['name']}) `{r['latex']}` — {r.get('reason', '')}")
        L.append("")
    return "\n".join(L) + "\n"
