from pathlib import Path

import pytest

from formulaci.bench import mutate, oracle
from formulaci.bench.sets import read_jsonl
from formulaci.bench.structure import balanced

FIX = Path(__file__).parent / "fixtures" / "known_good_sample.jsonl"
RECS = {r["bench"]["name"]: r for r in read_jsonl(FIX)}


@pytest.mark.parametrize("mtype", mutate.MUTATION_TYPES)
def test_each_mutation_changes_value_and_parses(mtype):
    produced = 0
    for rec in RECS.values():
        out, stats = mutate.mutate_record(rec, mtype)
        if out is None:
            continue
        produced += 1
        b = out["bench"]
        assert b["mutation"] == mtype and b["source_id"] == rec["formula_id"] and b["label"] == "false"
        assert out["formula_id"] == f"bench:mut:{rec['formula_id'][-4:]}:{mtype}"
        assert out["latex"] != rec["latex"] and balanced(out["latex"])
        vars = b["vars"]
        parsed = oracle.parse(out["latex"], vars)  # still parseable LaTeX
        r = oracle.check(parsed, vars, b.get("cond"), n=6, seed=3)  # independent points
        assert r.n_fail > 0, (mtype, out["latex"])
        # the trailing condition is never mutated
        assert oracle.split_condition(out["latex"])[1] == oracle.split_condition(rec["latex"])[1]
    assert produced >= 1, f"{mtype} produced nothing on the fixture"


def test_identity_preserving_mutations_are_dropped_and_counted():
    rec = RECS["Symmetry of the beta function"]  # B(x,y) = B(y,x): swapping x<->y preserves it
    out, stats = mutate.mutate_record(rec, "swapped_symbols")
    assert stats["preserved"] >= 1
    if out is not None:
        assert "B(x, y) = \\mathrm{B}(y, x)" not in out["latex"]


def test_run_writes_file_and_stats(tmp_path):
    out = tmp_path / "mutated.jsonl"
    st = mutate.run(FIX, out, types=["sign_flip", "num_den_swap"], jobs=2)
    rows = read_jsonl(out)
    assert st["n_kept"] == len(rows) > 0
    assert set(st["per_type"]) == {"sign_flip", "num_den_swap"}
    assert "dropped_preserving_identity" in st
    assert all(r["bench"]["source_latex"] in {x["latex"] for x in RECS.values()} for r in rows)
