from formulaci.verify.policy import decide


def reg(name, n, fail=0, err=0):
    pts = [{"point": {"x": f"0.{i + 1}"}, "status": "fail" if i < fail else "pass", "lhs": "1", "rhs": "2",
            "abs_diff": "1", "rel_diff": "0.5", "rel": 0.5, "error": ""} for i in range(n - err)]
    pts += [{"point": {"x": "0"}, "status": "error", "error": "pole", "lhs": "", "rhs": "", "abs_diff": "",
             "rel_diff": "", "rel": None}] * err
    return {"name": name, "n_points": n, "n_fail": fail, "n_error": err, "points": pts}


BASE = ["small_positive", "unit_interval", "integers_small", "mixed_sign", "large"]
META = {"relation": "=", "branch": False}


def numeric(regs, **kw):
    return {"regimes": regs, "constant": False, "integer_resampled": False, "eval_error": "", **kw}


def test_fail_needs_every_qualified_regime():
    all_fail = numeric([reg(r, 12, 12) for r in BASE])
    v, reason, ce = decide(META, "unknown", all_fail)
    assert v == "FAIL" and ce is not None and ce.assignments == {"x": "0.1"}
    one_passes = numeric([reg(r, 12, 12) for r in BASE[:-1]] + [reg("large", 12, 0)])
    assert decide(META, "unknown", one_passes)[0] == "INCONCLUSIVE"


def test_symbolic_equal_never_fails():
    assert decide(META, "equal", numeric([reg(r, 12, 12) for r in BASE]))[0] == "INCONCLUSIVE"
    assert decide(META, "equal", numeric([reg(r, 12) for r in BASE]))[0] == "PASS"


def test_unqualified_regimes_are_ignored_but_two_are_needed():
    regs = [reg("small_positive", 12, 12), reg("unit_interval", 12, 12)] + [reg(r, 4, 0, 4) for r in BASE[2:]]
    assert decide(META, "unknown", numeric(regs))[0] == "FAIL"
    regs = [reg("small_positive", 12, 12)] + [reg(r, 4, 0, 4) for r in BASE[1:]]
    assert decide(META, "unknown", numeric(regs))[0] == "INCONCLUSIVE"
    regs = [reg(r, 12, 12) for r in BASE[:2]] + [reg(r, 4, 0, 4) for r in BASE[2:]]
    assert decide(META, "unknown", numeric(regs, timed_out=True))[0] == "INCONCLUSIVE"


def test_majority_threshold():
    regs = [reg(r, 10, 7) for r in BASE]
    assert decide(META, "unknown", numeric(regs))[0] == "FAIL"
    regs = [reg(r, 10, 6) for r in BASE]
    assert decide(META, "unknown", numeric(regs))[0] == "INCONCLUSIVE"


def test_branch_cut_rule():
    regs = [reg(r, 12) for r in BASE if r != "mixed_sign"] + [reg("mixed_sign", 12, 12)]
    v, reason, _ = decide({**META, "branch": True}, "unknown", numeric(regs))
    assert v == "INCONCLUSIVE" and "branch" in reason


def test_measure_zero_rule():
    regs = [reg(r, 12) for r in BASE if r != "integers_small"] + [reg("integers_small", 12, 12)]
    v, reason, _ = decide(META, "unknown", numeric(regs))
    assert v == "INCONCLUSIVE" and "measure-zero" in reason


def test_integer_only_rule():
    regs = [reg(r, 12, 12) for r in BASE if r != "integers_small"] + [
        reg("integers_small", 12), reg("integers_large", 12), reg("integers_mixed_sign", 12)]
    v, reason, _ = decide(META, "unknown", numeric(regs, integer_resampled=True))
    assert v == "PASS" and "integer-only" in reason


def test_constant_identity_and_errors():
    const = {"regimes": [reg("constant", 1, 1)], "constant": True, "eval_error": ""}
    assert decide(META, "unknown", const)[0] == "FAIL"
    assert decide(META, "equal", const)[0] == "INCONCLUSIVE"
    assert decide(META, "unknown", {"regimes": [], "eval_error": "boom"})[0] == "INCONCLUSIVE"
    assert decide(META, "equal", {"regimes": [], "eval_error": "boom"})[0] == "PASS"
    assert decide(META, "unknown", numeric([reg(r, 3) for r in BASE]))[0] == "INCONCLUSIVE"


def test_symbolic_disagreement_blocks_pass():
    assert decide(META, "not_equal", numeric([reg(r, 12) for r in BASE]))[0] == "INCONCLUSIVE"


def test_statement_guards():
    all_fail = numeric([reg(r, 12, 12) for r in BASE])
    v, reason, _ = decide({**META, "unmapped_constants": ["e", "i"]}, "unknown", all_fail)
    assert v == "INCONCLUSIVE" and "constant" in reason
    v, reason, _ = decide({**META, "zero_side": True}, "unknown", all_fail)
    assert v == "INCONCLUSIVE" and "equation to solve" in reason
    assert decide({**META, "zero_side": True}, "unknown", numeric([reg(r, 12) for r in BASE]))[0] == "PASS"
