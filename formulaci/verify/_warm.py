"""Imported only by the forkserver preload: fill mpmath's tanh-sinh node caches up to the maximum
degree once, so every forked worker inherits them instead of rebuilding them per precision
(about a second each)."""
import mpmath as mp

from formulaci.verify.numeric import LADDER

for _dps in LADDER[:3]:
    with mp.workdps(_dps):
        # oscillatory / singular integrands force quad up to maxdegree on both node families
        mp.quad(lambda t: mp.sqrt(t) * mp.log(t) * mp.sin(40 * t), [0, 1], maxdegree=8)
        mp.quad(lambda t: t ** mp.mpf("0.07") * mp.exp(-t) * mp.cos(3 * t), [0, mp.inf], maxdegree=8)
