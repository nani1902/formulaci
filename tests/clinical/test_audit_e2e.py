"""End-to-end: Playwright drives the local mock site; the audit must flag exactly the planted errors."""
import json

import pytest
import yaml

pytest.importorskip("playwright")

from formulaci.clinical import audit as A
from formulaci.clinical.mock.server import TARGETS, serve_in_thread


@pytest.fixture(scope="module")
def mock_records(tmp_path_factory):
    srv, base = serve_in_thread()
    out = tmp_path_factory.mktemp("clinical") / "audit.jsonl"
    try:
        recs = A.run(TARGETS, out, base_url=base, max_cases=2, timeout_ms=1500)
    finally:
        srv.shutdown()
    return recs, out


@pytest.mark.timeout(300)
def test_mock_audit_flags_exactly_the_planted_errors(mock_records):
    recs, out = mock_records
    truth = yaml.safe_load(TARGETS.read_text())["targets"]
    planted_wrong = {t["id"] for t in truth if t.get("planted") and t.get("expect") != "unreadable"}
    planted_unreadable = {t["id"] for t in truth if t.get("expect") == "unreadable"}
    status = {tid: A.target_status(c) for tid, c in A.summarize(recs).items()}
    assert set(status) == {t["id"] for t in truth}
    assert {t for t, s in status.items() if s == "mismatch"} == planted_wrong
    assert {t for t, s in status.items() if s == "unreadable"} == planted_unreadable
    assert len(planted_wrong) >= 3
    # every case of a planted page is wrong, every case of a good page is right
    for r in recs:
        if r.target in planted_wrong:
            assert r.status == "mismatch", r
        elif r.target not in planted_unreadable:
            assert r.status == "match", r
    # the JSONL on disk has the spec's fields
    rows = [json.loads(line) for line in out.read_text().splitlines()]
    assert len(rows) == len(recs)
    for row in rows:
        assert {"target", "formula", "inputs", "site_output", "reference_output", "status",
                "notes"} <= set(row)


@pytest.mark.timeout(300)
def test_mock_audit_diagnoses_each_planted_error(mock_records):
    recs, _ = mock_records
    diag = {r.target: " | ".join(r.diagnosis) for r in recs if r.status == "mismatch"}
    assert "egfr_ckd_epi_cr@2009" in diag["mock-egfr-ckd-epi-legacy"]
    assert "weight entered in lb but used as kg" in diag["mock-crcl-cockcroft-gault"]
    assert "RR interval used in ms instead of s" in diag["mock-qtc-bazett"]
    assert "sodium_corrected@katz" in diag["mock-sodium-corrected"]
    winters = [r for r in recs if r.target == "mock-winters"]
    assert winters and all("page errors" in r.notes for r in winters)


def test_audit_is_resumable(mock_records, tmp_path):
    srv, base = serve_in_thread()
    out = tmp_path / "a.jsonl"
    try:
        first = A.run(TARGETS, out, base_url=base, only=["mock-bmi"], max_cases=2)
        again = A.run(TARGETS, out, base_url=base, only=["mock-bmi"], max_cases=2)
    finally:
        srv.shutdown()
    assert len(first) == 2 and again == []
    assert len(out.read_text().splitlines()) == 2
