import json
import random
from collections import Counter
from pathlib import Path

import pytest

from formulaci.bench import lacast, oracle
from formulaci.bench.identities import E
from formulaci.bench.sets import domain_phrase, known_good_records, parse_vars
from formulaci.schemas import Formula

SNAP = Path(__file__).parents[2] / "formulaci" / "bench" / "sets" / "known_good.jsonl"


def test_catalogue_size_and_categories():
    assert len(E) >= 150
    cats = Counter(e[0] for e in E)
    for c in ["trig", "hyperbolic", "exp_log", "gamma_beta", "zeta", "binomial", "finite_series",
              "infinite_series", "integrals", "derivatives", "inequalities", "probability"]:
        assert cats[c] >= 5, c
    assert len({e[2] for e in E}) == len(E), "duplicate LaTeX in catalogue"


def test_records_are_formulas_with_labels():
    recs, _ = known_good_records(verify=False)
    assert len({r["formula_id"] for r in recs}) == len(recs)
    for r in recs:
        Formula.model_validate(r)  # extra "bench" key is ignored by the shared schema
        assert r["formula_id"].startswith("bench:good:")
        assert r["bench"]["label"] == "true" and r["bench"]["category"]
        assert f"bench-category:{r['bench']['category']}" in r["page_categories"]
        assert r["context_before"].startswith("The ")


def test_domain_phrase():
    assert domain_phrase({"x": "real", "y": "real"}) == "for all real x and y"
    assert domain_phrase({"n": "posint"}) == "for positive integer n"
    assert domain_phrase({"p": "unit"}) == "for 0 < p < 1"


@pytest.mark.parametrize("i", random.Random(7).sample(range(len(E)), 25))
def test_catalogue_sample_holds_numerically(i):
    cat, name, latex, vars_s, cond, ctx = E[i]
    vars = parse_vars(vars_s)
    r = oracle.check(oracle.parse(latex, vars), vars, cond, n=4, seed=i)
    assert r.holds, (name, r)


def test_oracle_detects_a_wrong_formula():
    vars = {"x": "real"}
    r = oracle.check(oracle.parse(r"\sin^2 x - \cos^2 x = 1", vars), vars, n=5)
    assert r.majority_fails


def test_oracle_condition_split_and_dialect():
    body, cond = oracle.split_condition(r"\ln(1 + x) = \sum_{n=1}^{\infty} \frac{(-1)^{n+1} x^{n}}{n} \quad |x| < 1")
    assert cond.startswith(r"\quad") and body.endswith("{n}")
    p = oracle.parse(r"\mathrm{B}(x, y) = \int_0^1 t^{x - 1} (1 - t)^{y - 1}\,dt", {"x": "pos1", "y": "pos1"})
    assert len(p.sides) == 2 and p.rels == ["=="]


def test_snapshot_if_built():
    if not SNAP.exists():
        pytest.skip("run `formulaci bench build` to create the snapshot")
    lines = [json.loads(x) for x in SNAP.read_text().splitlines() if x.strip()]
    assert len(lines) >= 150


def test_lacast_snapshot():
    recs = lacast.records()
    assert len(recs) == 95
    assert recs[0]["formula_id"] == "lacast:gold:001"
    human = Counter(r["bench"]["lacast"]["human"]["semantic_latex"] for r in recs)
    assert set(human) <= {"correct", "wrong", "none"} and human["correct"] > 0
    for r in recs:
        Formula.model_validate(r)
