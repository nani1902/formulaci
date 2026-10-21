"""Harness pieces that need no browser: host guard, templating, parsing, diagnosis, targets."""
from collections import Counter

import pytest
from typer.testing import CliRunner

from formulaci.clinical import audit as A
from formulaci.clinical import formulas as F
from formulaci.clinical.cli import app
from formulaci.clinical.mock.server import TARGETS as MOCK_TARGETS


@pytest.mark.parametrize("url,local", [
    ("http://127.0.0.1:8000/x", True), ("http://localhost/x", True), ("http://[::1]:9/", True),
    ("http://app.localhost/", True), ("https://www.mdcalc.com/calc/1", False),
    ("http://127.0.0.1.evil.com/", False), ("http://10.0.0.1/", False),
])
def test_is_local(url, local):
    assert A.is_local(url) is local


def test_live_targets_refused_without_flag(tmp_path):
    out = tmp_path / "a.jsonl"
    with pytest.raises(A.LiveSiteRefused):
        A.run(A.LIVE_TARGETS, out)  # raises before importing/launching playwright
    assert not out.exists()


def test_cli_refuses_live(tmp_path):
    r = CliRunner().invoke(app, ["audit", "--targets", str(A.LIVE_TARGETS),
                                 "--out", str(tmp_path / "a.jsonl")])
    assert r.exit_code == 2 and "refusing" in r.output


def test_relative_targets_need_base_url():
    with pytest.raises(ValueError):
        A.resolve_url("bmi.html", None)
    assert A.resolve_url("bmi.html", "http://127.0.0.1:5") == "http://127.0.0.1:5/bmi.html"


def test_template_vars():
    v = A.template_vars({"scr": 1.0, "age": 50, "sex": "female", "weight": 70, "height": 175,
                         "hr": 75})
    assert v["scr"] == "1" and v["scr_umol"] == "88.4" and v["sex_initial"] == "F"
    assert v["weight_lb"] == "154.32" and v["height_in"] == "68.9"
    assert v["height_ft"] == "5" and v["rr_s"] == "0.8" and v["rr_ms"] == "800"


def test_parse_and_tolerance():
    assert A.parse_value("eGFR = 92 mL/min", r"eGFR = ([0-9.]+)") == (92.0, 0)
    assert A.parse_value("1,234.5", r"([0-9.]+)") == (1234.5, 1)
    assert A.parse_value("—", r"([0-9.]+)") == (None, 0)
    assert A.tolerance(100, 0, A.Tol()) == pytest.approx(0.5 + 0.5)


def test_diagnose_recognises_planted_bug_classes():
    inp = {"scr": 1.0, "age": 50, "sex": "male"}
    site = F.egfr_ckd_epi_cr_2009(1.0, 50, "male", True)
    assert any("egfr_ckd_epi_cr@2009 with black=True" in d
               for d in A.diagnose("egfr_ckd_epi_cr@2021", inp, site, 0.5))
    qt = {"qt": 400, "hr": 75}
    assert any("ms instead of s" in d
               for d in A.diagnose("qtc_bazett@1920", qt, 400 / (800 ** 0.5), 0.5))
    cg = {"scr": 1.0, "age": 40, "sex": "male", "weight": 70}
    assert any("lb but used as kg" in d for d in A.diagnose(
        "crcl_cockcroft_gault@1976", cg, F.crcl_cockcroft_gault(1.0, 40, "male", 70 / 0.45359237), 0.5))


def test_live_targets_yaml_is_well_formed():
    ts = A.load_targets(A.LIVE_TARGETS)
    assert len(ts) >= 30
    assert len({t.id for t in ts}) == len(ts)
    for t in ts:
        assert t.formula in F.REGISTRY, (t.id, t.formula)
        assert t.url.startswith("https://") or t.url.startswith("http://"), t.id
        assert not A.is_local(t.url)
    assert len(Counter(t.site for t in ts)) >= 8  # spread across sites


def test_mock_targets_are_local_and_registered():
    for t in A.load_targets(MOCK_TARGETS):
        assert t.formula in F.REGISTRY
        assert A.is_local(A.resolve_url(t.url, "http://127.0.0.1:1"))
