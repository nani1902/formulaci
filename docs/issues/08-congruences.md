coverage: a modular evaluator for `a \equiv b \pmod n` (5,306 formulas)
labels: coverage, help-wanted, good-first-issue

Congruences are refused by semantics (`congruence`): the pipeline has no way to compare two integers modulo a third. Yet most congruences on number-theory pages are closed-form identities over integers (Fermat's little theorem, Wilson's theorem, binomial congruences, quadratic reciprocity instances) that can be checked by exact integer arithmetic at sampled points.

**What to build.** A translator reading of `\equiv` with `\pmod{n}` / `\bmod n` / `\mod n` into a relation object `Mod(a - b, n) == 0`; an integer-only sampling regime in `formulaci/verify/sampler.py` (the `integers_small`/`integers_large` regimes exist) with exact `int` evaluation instead of mpmath for this relation; and a semantics rule that reads "for every prime p" (the `P.type_phrase` machinery has `prime`). The FAIL policy is unchanged: a majority of sampled points in every regime.

**Precision risk.** Congruences stated for primes only, or for `a` coprime to `n`; the sampler must respect both (prime sampling and `gcd` constraints are small additions). `\equiv` is also used for definitions and for "identically equal" on analysis pages; only the `\pmod` form is a congruence.

**Fixtures.** Fermat, Euler, Wilson, `\binom{p}{k} \equiv 0 \pmod p`, Lucas' theorem instances, plus the obvious mutations (wrong modulus, wrong exponent).

A self-contained, well-bounded first contribution: one translator rule, one sampler regime, a dozen fixtures.
