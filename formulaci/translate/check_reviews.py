"""Re-translate the formulas that human review blamed on the translator and report what happens now.

    uv run python -m formulaci.translate.check_reviews [--reviews data/findings/reviews.jsonl]
        [--formulas data/raw/formulas.jsonl] [--verbose]

For every reviewed false positive whose cause tag is one of TRANSLATOR_CAUSES, the formula is translated
with the current code and the record the FAIL came from (same `index_in_chain`) is classified:

- `refused`   no `ok` record is left for the reviewed relation (verify will skip it)
- `fixed`     every `ok` record of the formula is a reading checked by hand against the reviewer's
              note and listed in ACCEPTED_READINGS (e.g. `\\bar z` -> `conjugate(z)`, `e^{iax}` a power)
- `still_ok`  an `ok` record that is not in ACCEPTED_READINGS: needs a human look
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import sympy as sp

from formulaci.schemas import Formula

from .core import translate

TRANSLATOR_CAUSES = ("[translator_misread_other]", "[superscript_is_label]", "[mixed_number_or_juxtaposition]")

# formula_id -> every ok record (str(lhs), str(rhs)) after the second pass, each checked by hand against the
# reviewer's note: these are the readings the reviewer called correct (or harmless later pairs of a chain).
ACCEPTED_READINGS = {
    'wiki:en:80262208:1376111431:692': [('N(phi**n)', '(-1)**n')],
    'wiki:en:80262208:1376111431:694': [('N(sqrt(5)*phi**n)', '-5*(-1)**n')],
    'wiki:en:206210:1328878894:6': [('cas(x)', 'sin(x) + cos(x)')],
    'wiki:en:24048:1375453918:44': [('sinc(x)', 'sin(x)/x')],
    'wiki:en:24048:1375453918:49': [('sinc(p)', 'sin(p)/p')],
    'wiki:en:61338:1377884439:1': [('7/2', '7/2')],
    'wiki:en:5321016:1346298619:0': [('e_s(T)', '30547*exp(141*T/(8*(T + 6076/25)))/5000')],
    'wiki:en:4668:1376065730:236': [('-120', '-120'), ('-120', '-120'), ('-120', '-120')],
    'wiki:en:6220:1379953806:34': [('Abs(c - z)**2', 'c*conjugate(c) - c*conjugate(z) - z*conjugate(c) + z*conjugate(z)')],
    'wiki:en:5308:1366053287:47': [('20', '20'), ('20', '20'), ('20', '20')],
    'wiki:en:23997203:1359018742:103': [('Delta_f/f', 'Delta_a/a + Delta_b/(b*log(b))')],
    'wiki:en:148594:1378444832:115': [('q*gamma(a, q)', '-log(d) + q*gamma(a/d, q/d)/d')],
    'wiki:en:1273836:1363301178:0': [('sec(theta) - 1', '-1 + 1/cos(theta)')],
    'wiki:en:54267:1379191356:65': [('rpi(x)', 'floor(x + 1/2)'), ('floor(x + 1/2)', 'ceiling(floor(2*x)/2)')],
    'wiki:en:54267:1379191356:67': [('ri(x)', 'floor(Abs(x) + 1/2)*sign(x)')],
    'wiki:en:52247:1377137736:547': [('cos(a*x)', 'e**(a*i*x)/2 + 1/(2*e**(a*i*x))')],
    'wiki:en:52247:1377137736:552': [('sin(a*x)', '(e**(a*i*x) - 1/e**(a*i*x))/(2*i)')],
    'wiki:en:52247:1377137736:613': [('cos(a*x)', 'e**(a*i*x)/2 + 1/(2*e**(a*i*x))')],
    'wiki:en:52247:1377137736:618': [('sin(a*x)', '(e**(a*i*x) - 1/e**(a*i*x))/(2*i)')],
    'wiki:en:2310978:1305585550:3': [('-1', '-1')],
    'wiki:en:20598932:1381119901:6': [('Abs(z)**2', 'z*conjugate(z)')],
    'wiki:en:27430123:1372869378:185': [('gcd(a, b, c)', '3')],
    'wiki:en:27430123:1372869378:199': [('gcd(a, b, c)', '3')],
    'wiki:en:17973:1377293254:34': [('Delta_epsilon', '0')],
    'wiki:en:18814960:1376246270:39': [('Ti_2(x)', 'Sum((-1)**n*x**(2*n + 1)/(2*n + 1)**2, (n, 0, oo))'), ('Ti_3(x)', 'Sum((-1)**n*x**(2*n + 1)/(2*n + 1)**3, (n, 0, oo))')],
    'wiki:en:25804104:1379178075:371': [('sin(phi) + sin(theta)', '2*sin(phi/2 + theta/2)*cos(phi/2 - theta/2)')],
    'wiki:en:21476:1380767706:89': [('log1p(x)', 'log(x + 1)'), ('log(x + 1)', '2*atanh(x/(x + 2))')],
    'wiki:en:2091823:1380348958:183': [('M_2(f)', '0')],
    'wiki:en:2091823:1380348958:214': [('tau(A)', '0')],
    'wiki:en:2091823:1380348958:217': [('tau(A)', '0')],
    'wiki:en:2091823:1380348958:218': [('M_2(A)', '0')],
    'wiki:en:2091823:1380348958:309': [('M_2(f*h)', '0')],
    'wiki:en:61229:1379891258:3': [('re(z)', 'z/2 + conjugate(z)/2')],
    'wiki:en:61229:1379891258:5': [('Abs(z)', 'sqrt(z*conjugate(z))')],
    'wiki:en:61229:1379891258:4': [('im(z)', '(z - conjugate(z))/(2*i)')],
    'wiki:en:30448:1377126901:148': [('Ti_2(x)', 'Sum((-1)**n*x**(2*n + 1)/(2*n + 1)**2, (n, 0, oo))'), ('Ti_3(x)', 'Sum((-1)**n*x**(2*n + 1)/(2*n + 1)**3, (n, 0, oo))')],
    'wiki:en:449745:1370749078:129': [('theta_4(exp(-3*sqrt(2)*pi))', 'sqrt(3)*sqrt(sqrt(2) + sqrt(3))*theta_4(exp(-sqrt(2)*pi))/3')],
    'wiki:en:449745:1370749078:132': [('theta_4(exp(-3*sqrt(10)*pi))', 'sqrt(3)*sqrt(sqrt(1 + Phi**(-4)) + sqrt(2*sqrt(1 - 1/Phi**4 + Phi**(-8)) + 2 - 1/Phi**4))*theta_4(exp(-sqrt(10)*pi))/3')],
}



def load_reviews(path: Path) -> list[dict]:
    out = []
    with path.open() as f:
        for line in f:
            if line.strip():
                r = json.loads(line)
                if r["review"]["notes"].startswith(TRANSLATOR_CAUSES):
                    out.append(r)
    return out


def load_formulas(path: Path, ids: set[str]) -> dict[str, Formula]:
    out = {}
    with path.open() as f:
        for line in f:
            j = json.loads(line)
            if j["formula_id"] in ids:
                out[j["formula_id"]] = Formula.model_validate(j)
    return out


def classify(review: dict, f: Formula | None) -> tuple[str, str]:
    if f is None:
        return "missing", "formula not in input"
    recs = translate(f)
    idx = review.get("index_in_chain")
    rec = next((r for r in recs if r.index_in_chain == idx), None)
    if rec is None:
        # the record numbering changed (rows split differently); judge the formula as a whole
        oks = [r for r in recs if r.status == "ok" and r.kind in ("equation", "chain", "definition_like", "inequality")]
        if not oks:
            return "refused", f"all {len(recs)} records not ok: {sorted({u for r in recs for u in r.has_unsupported})}"
        rec = oks[0]
    if rec.status != "ok":
        return "refused", f"{rec.status} {rec.has_unsupported or rec.error}"
    from formulaci.safeload import readable
    oks = [(readable(r.lhs), readable(r.rhs)) for r in recs if r.status == "ok"]
    accepted = ACCEPTED_READINGS.get(f.formula_id, [])
    if all(o in accepted for o in oks):
        return "fixed", "; ".join(f"{a} = {b}" for a, b in oks)
    return "still_ok", "; ".join(f"{a} = {b}" for a, b in oks if (a, b) not in accepted)


def main(argv=None) -> dict:
    ap = argparse.ArgumentParser()
    ap.add_argument("--reviews", default="data/findings/reviews.jsonl")
    ap.add_argument("--formulas", default="data/raw/formulas.jsonl")
    ap.add_argument("--verbose", action="store_true")
    a = ap.parse_args(argv)
    reviews = load_reviews(Path(a.reviews))
    formulas = load_formulas(Path(a.formulas), {r["formula_id"] for r in reviews})
    counts: Counter = Counter()
    by_cause: dict[str, Counter] = {}
    for r in reviews:
        cause = r["review"]["notes"].split("]")[0] + "]"
        f = formulas.get(r["formula_id"])
        outcome, detail = classify(r, f)
        counts[outcome] += 1
        by_cause.setdefault(cause, Counter())[outcome] += 1
        if a.verbose or outcome in ("still_ok", "missing"):
            latex = f.latex.strip().replace("\n", " ")[:160] if f else "?"
            print(f"{outcome:9s} {r['formula_id']}#{r.get('index_in_chain')} {cause}\n    {latex}\n    -> {detail[:200]}")
    print(f"\n{len(reviews)} reviewed translator false positives: {dict(counts)}")
    for cause, c in by_cause.items():
        print(f"  {cause}: {dict(c)}")
    return dict(counts)


if __name__ == "__main__":
    main()
