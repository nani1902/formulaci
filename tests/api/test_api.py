import subprocess
import sys
import time

import pytest

from formulaci import api
from formulaci.api import CheckResult, check, check_many, extract_formulas

CASES = {
    "pythagoras": (r"\sin^2 x + \cos^2 x = 1", ""),
    "pythagoras_wrong": (r"\sin^2 x + \cos^2 x = 2", ""),
    "gamma": (r"\Gamma(n+1) = n!", "for positive integers n"),
    "euler": (r"e^{i\pi} + 1 = 0", ""),
    # a real Wikipedia error (Taylor series page): the sum is 2/(1-x)^3
    "taylor_wiki_error": (r"\frac{1}{(1-x)^3} = \sum_{n=2}^\infty n(n-1)x^{n-2}", "for |x|<1"),
    "garbage": ("not latex at all \\foo{", ""),
    "defining": (r"x = 5", ""),
}


@pytest.fixture(scope="module")
def results():
    return {k: check(latex, ctx) for k, (latex, ctx) in CASES.items()}


def test_true_identity_passes(results):
    r = results["pythagoras"]
    assert r.verdict == "PASS", r.explain()
    assert r.symbolic == "equal"
    assert r.counterexample is None
    assert r.translation[0]["lhs"] == "sin(x)**2 + cos(x)**2"
    assert r.assumptions["domains"] == {"x": "real"}
    assert sum(g["n_points"] for g in r.regimes) > 0


def test_wrong_identity_fails_with_counterexample(results):
    r = results["pythagoras_wrong"]
    assert r.verdict == "FAIL", r.explain()
    ce = r.counterexample
    assert ce and set(ce) == {"assignments", "lhs", "rhs", "abs_diff", "rel_diff"}
    assert all(isinstance(v, str) for v in ce["assignments"].values())
    assert float(ce["lhs"]) == pytest.approx(1) and float(ce["rhs"]) == pytest.approx(2)
    assert "counterexample" in r.explain()


def test_gamma_with_context_passes(results):
    r = results["gamma"]
    assert r.verdict == "PASS", r.explain()
    assert r.assumptions["domains"]["n"] in ("positive_integer", "nonneg_integer")


def test_euler_identity_passes(results):
    r = results["euler"]
    assert r.verdict == "PASS", r.explain()
    assert r.assumptions["constants"] == {"e": "E", "i": "I"}


def test_real_wikipedia_error_fails(results):
    r = results["taylor_wiki_error"]
    assert r.verdict == "FAIL", r.explain()
    assert r.counterexample is not None
    assert any("Abs(x) < 1" in c for c in r.assumptions["constraints"])


def test_unparsable_latex_is_skip(results):
    r = results["garbage"]
    assert r.verdict == "SKIP"
    assert r.skip_reason == "unparsed"
    assert "foo" in r.reason  # the translator's error


def test_defining_equation_is_not_fail(results):
    assert results["defining"].verdict in ("INCONCLUSIVE", "SKIP")


def test_result_shape(results):
    for k, r in results.items():
        assert isinstance(r, CheckResult)
        assert r.reason and "\n" not in r.reason, k
        assert r.elapsed_s >= 0
        assert r.formula_id.startswith("api:")
        text = r.explain()
        assert text.startswith(r.verdict) and len(text.splitlines()) >= 2
        CheckResult.model_validate_json(r.model_dump_json())  # JSON round-trip


def test_formula_id_is_sha1_of_latex_and_context():
    a, b = api._formula("x=x", "ctx", ""), api._formula("x=x", "other", "")
    assert a.formula_id != b.formula_id and len(a.formula_id) == len("api:") + 40
    assert api._formula("x=x", "ctx", "").formula_id == a.formula_id


@pytest.mark.parametrize("bad", [None, "", "   ", 123, "$$", "\\frac{", "=", "\\begin{matrix}"])
def test_bad_input_never_raises(bad):
    r = check(bad)
    assert r.verdict in ("SKIP", "INCONCLUSIVE")


def test_internal_error_is_inconclusive(monkeypatch):
    import formulaci.translate.core as core

    def boom(f, use_lark=False):
        raise RuntimeError("translator exploded")

    monkeypatch.setattr(core, "translate", boom)
    r = check(r"a + b = b + a")
    assert r.verdict == "INCONCLUSIVE"
    assert "RuntimeError" in r.reason and "translator exploded" in r.reason


def test_dead_worker_is_restarted():
    assert check("a+b=b+a").verdict == "PASS"
    for w in api._POOL._idle:
        w.proc.kill()
        w.proc.join()
    assert check("a b = b a").verdict == "PASS"


def test_timeout_is_honoured():
    # a slow infinite series: the numeric phase is cut by the deadline
    t0 = time.monotonic()
    r = check(r"\sum_{k=1}^\infty \frac{\sin(k x)}{k^3} = \frac{\pi^2 x}{6} - \frac{\pi x^2}{4} + \frac{x^3}{12}",
              "for 0 \\le x \\le 2\\pi", timeout=3)
    assert time.monotonic() - t0 < 8
    assert r.verdict != "FAIL"


def test_check_many_keeps_input_order():
    items = [(r"\sin^2 x + \cos^2 x = 2", ""), ("a+b=b+a", ""), {"latex": "x = 5"},
             {"latex": r"\Gamma(n+1) = n!", "context": "for positive integers n"}, ("1+1=3", "")]
    rs = check_many(items, workers=3)
    assert [r.latex for r in rs] == [r"\sin^2 x + \cos^2 x = 2", "a+b=b+a", "x = 5", r"\Gamma(n+1) = n!", "1+1=3"]
    assert [r.verdict for r in rs][:2] == ["FAIL", "PASS"]
    assert rs[2].verdict in ("SKIP", "INCONCLUSIVE")
    assert rs[3].verdict == "PASS" and rs[3].context == "for positive integers n"
    assert rs[4].verdict == "FAIL"


def test_check_many_bad_items_and_empty():
    assert check_many([]) == []
    rs = check_many([None, 42, ("a=a",)], workers=1)
    assert len(rs) == 3 and all(isinstance(r, CheckResult) for r in rs)


MD = ("Recall the Pythagorean identity $\\sin^2 x + \\cos^2 x = 1$, valid for every real angle. "
      "Euler's identity $e^{i\\pi} + 1 = 0$ links five constants.\n\nUnrelated paragraph costs $5.")


def test_extract_formulas_inline_markdown():
    got = extract_formulas(MD)
    assert [latex for latex, _ in got] == [r"\sin^2 x + \cos^2 x = 1", r"e^{i\pi} + 1 = 0"]
    ctx0, ctx1 = got[0][1], got[1][1]
    assert ctx0.startswith("Recall the Pythagorean identity") and "every real angle" in ctx0
    assert "Euler" not in ctx0
    assert ctx1.startswith("Euler's identity") and "five constants" in ctx1
    assert "$" not in ctx0 + ctx1
    assert [r.verdict for r in check_many(got)] == ["PASS", "PASS"]


def test_extract_formulas_all_delimiters():
    text = ("Display $$a+b=b+a$$ and \\(x^2 \\ge 0\\) and \\[ (a+b)^2 = a^2+2ab+b^2 \\]. "
            "Wiki <math>\\cos 0 = 1</math>. And\n\\begin{equation}\n e^{0} = 1\n\\end{equation}\n"
            "\\begin{align*} y &= 2 \\end{align*}")
    got = [latex for latex, _ in extract_formulas(text)]
    assert got == ["a+b=b+a", "x^2 \\ge 0", "(a+b)^2 = a^2+2ab+b^2", "\\cos 0 = 1", "e^{0} = 1", "y &= 2"]
    assert extract_formulas("") == [] and extract_formulas("no math here, it costs $5 or $6") == []


def test_context_split_around_formula():
    before, after = api._split_context("x=1", "We set x=1 here.")
    assert (before, after) == ("We set", "here.")
    assert api._split_context("x", "for |x|<1") == ("", "for |x|<1")
    assert api._split_context("x", "Let x be real") == ("Let x be real", "")


def test_unguarded_script_does_not_recurse(tmp_path):
    script = tmp_path / "s.py"
    script.write_text("from formulaci.api import check\nprint('RESULT', check('a+b=b+a').verdict)\n")
    out = subprocess.run([sys.executable, str(script)], capture_output=True, text=True, timeout=90)
    assert out.stdout.count("RESULT") == 1, out.stderr[-2000:]
    assert "RESULT PASS" in out.stdout
