from __future__ import annotations

import mpmath as mp

from formulaci.verify.guards import stated_type_symbols
from formulaci.verify.numeric import _infinite


def test_infinite_sum_with_late_peak_is_accurate():
    with mp.workdps(50):
        for lam in (5, 431.98, 787.057):
            lam = mp.mpf(lam)
            term = lambda k: k * lam ** k * mp.exp(-lam) / mp.factorial(k)  # noqa: E731
            assert abs(_infinite(term, 0, True) - lam) < mp.mpf("1e-40") * lam
        # geometric and slowly converging (Basel) series still work
        assert abs(_infinite(lambda k: mp.mpf(1) / 2 ** k, 0, True) - 2) < mp.mpf("1e-45")
        assert abs(_infinite(lambda k: 1 / mp.mpf(k) ** 2, 1, True) - mp.pi ** 2 / 6) < mp.mpf("1e-30")


def test_stated_type_symbols_reads_prose_tags():
    assert stated_type_symbols(["D.letter_real:x", "P.type_phrase:x", "K.inequality"]) == {"x"}
    assert stated_type_symbols(["P.member:n", "P.interval:p", "tol:rel=1e-3"]) == {"n", "p"}
    assert stated_type_symbols([]) == set()
