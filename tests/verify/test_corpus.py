"""The built-in corpus: true identities must PASS, mutations must FAIL, branch-cut traps must be
INCONCLUSIVE. Rows marked `known miss` are mutations the policy is designed not to flag."""
import mpmath
import pytest

# Without gmpy2, mpmath's pure-Python backend is ~2x slower and integral / infinite-series cases can
# run out of their 20 s budget (INCONCLUSIVE, never a wrong verdict). See PROPOSALS.md (verify).
SLOW_OK = mpmath.libmp.BACKEND != "gmpy"


def _slow(row):
    return "Integral" in row["parsed"]["lhs"] + row["parsed"]["rhs"] or "Infinity" in row["parsed"]["lhs"]


@pytest.mark.timeout(900)
def test_corpus_size(corpus_results):
    rows, _, _ = corpus_results
    by_cat = {c: sum(r["category"] == c for r in rows) for c in ("true", "mutated", "branch")}
    assert by_cat["true"] >= 40 and by_cat["mutated"] >= 40 and by_cat["branch"] >= 10


@pytest.mark.timeout(900)
def test_no_true_identity_or_trap_fails(corpus_results):
    rows, verdicts, _ = corpus_results
    bad = [(r["id"], verdicts[r["parsed"]["formula_id"]].verdict, verdicts[r["parsed"]["formula_id"]].reason)
           for r in rows if r["expected"] != "FAIL" and verdicts[r["parsed"]["formula_id"]].verdict == "FAIL"
           and "known miss" not in r["note"]]
    assert not bad, bad


@pytest.mark.timeout(900)
def test_every_row_matches(corpus_results):
    rows, verdicts, table = corpus_results
    print("\n" + "\n".join(f"{k}: {v}" for k, v in sorted(table.items())))
    mismatches = []
    for r in rows:
        v = verdicts[r["parsed"]["formula_id"]]
        ok = v.verdict == r["expected"]
        if SLOW_OK and _slow(r) and v.verdict == "INCONCLUSIVE":
            ok = True
        if "known miss" in r["note"]:
            ok = v.verdict in ("INCONCLUSIVE", "FAIL")  # FAIL is correct too, if the large regime errors out
        if not ok:
            mismatches.append((r["id"], r["expected"], v.verdict, v.reason))
    assert not mismatches, "\n".join(map(str, mismatches))


@pytest.mark.timeout(900)
def test_fail_verdicts_carry_counterexamples(corpus_results):
    rows, verdicts, _ = corpus_results
    for v in verdicts.values():
        if v.verdict == "FAIL":
            ce = v.counterexample
            assert ce is not None and v.regimes
            for val in (ce.lhs, ce.rhs):
                assert val == "0" or len(val.replace("-", "").replace(".", "")) >= 30, val
            assert v.reason.count(".") >= 1 and len(v.reason) < 400
