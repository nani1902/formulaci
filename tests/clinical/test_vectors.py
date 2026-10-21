"""Reference implementations reproduce the independently generated vectors."""
import json
import math

import pytest

from formulaci.clinical import formulas as F
from formulaci.clinical import vectorgen

VECS = json.loads(vectorgen.VECTORS_PATH.read_text())["vectors"]


@pytest.mark.parametrize("v", VECS, ids=lambda v: f"{v['formula']}:{v['note'] or v['inputs']}")
def test_vector_round_trip(v):
    got = F.evaluate(v["formula"], v["inputs"], v["units"])
    assert got == pytest.approx(v["expected"], rel=1e-9, abs=1e-9)


def test_vectors_file_is_current():
    """vectors.json is exactly what vectorgen produces (nobody hand-edited it)."""
    assert vectorgen.build() == VECS


def test_every_formula_has_five_vectors_and_a_unit_or_edge_case():
    by = {}
    for v in VECS:
        by.setdefault(v["formula"], []).append(v)
    for key in F.REGISTRY:
        if key == "ldl_martin_hopkins@2013" and not F.MH_TABLE_PATH.exists():
            continue
        assert len(by.get(key, [])) >= 5, key
        assert any({"unit", "edge"} & set(v["tags"]) for v in by[key]), key


def test_martin_hopkins_without_table_says_so():
    if F.MH_TABLE_PATH.exists():
        pytest.skip("table present")
    with pytest.raises(NotImplementedError):
        F.evaluate("ldl_martin_hopkins@2013", {"tc": 200, "hdl": 50, "tg": 150})


def test_docstrings_quote_equation_and_doi():
    for spec in F.REGISTRY.values():
        assert spec.citation and spec.doc, spec.key
        if spec.doi:
            assert spec.doi in spec.doc, f"{spec.key} docstring lacks its DOI"
        assert "=" in spec.doc, f"{spec.key} docstring lacks the equation"


def test_unit_conversions():
    # mg/dL <-> µmol/L creatinine, in <-> cm, lb <-> kg
    a = F.evaluate("egfr_ckd_epi_cr@2021", {"scr": 1.2, "age": 60, "sex": "female"})
    b = F.evaluate("egfr_ckd_epi_cr@2021", {"scr": 1.2 * 88.4, "age": 60, "sex": "female"},
                   {"scr": "umol/L"})
    assert a == pytest.approx(b, rel=1e-12)
    assert F.convert("height", 1, "in") == 2.54
    assert F.convert("weight", 1, "lb") == 0.45359237
    assert F.evaluate("bmi@quetelet", {"weight": 150, "height": 65}, {"weight": "lb", "height": "in"}) \
        == pytest.approx(703.0695796 * 150 / 65 ** 2, rel=1e-9)
    with pytest.raises(ValueError):
        F.convert("scr", 1, "mmol/L")


def test_known_anchor_values():
    # Hand-computable anchors straight from the equations.
    assert F.crcl_cockcroft_gault(1.0, 40, "male", 72) == pytest.approx(100)
    assert F.qtc_bazett(400, 60) == pytest.approx(400)
    assert F.qtc_fridericia(400, 60) == pytest.approx(400)
    assert F.qtc_framingham(400, 60) == pytest.approx(400)
    assert F.qtc_hodges(400, 60) == pytest.approx(400)
    assert F.holliday_segar(20) == 1500 and F.holliday_segar_hourly(20) == 60
    assert F.ibw_devine(152.4, "male") == pytest.approx(50)
    assert F.bsa_mosteller(36, 100) == pytest.approx(1.0)
    # 2009 race coefficient is exactly 1.159x the non-black value
    nb = F.egfr_ckd_epi_cr_2009(1.0, 50, "male", False)
    assert F.egfr_ckd_epi_cr_2009(1.0, 50, "male", True) / nb == pytest.approx(1.159)
    # 2021 and 2009 differ materially for the same patient (what the audit relies on)
    assert abs(F.egfr_ckd_epi_cr_2021(1.0, 50, "male") / nb - 1) > 0.03


def test_bad_sex_rejected():
    with pytest.raises(ValueError):
        F.egfr_ckd_epi_cr_2021(1.0, 50, "x")
    assert all(math.isfinite(F.evaluate(v["formula"], v["inputs"], v["units"])) for v in VECS)
