coverage: read series and products written with an ellipsis (9,676 relations, 3,031 pages)
labels: coverage, help-wanted, tier-A

Most articles state a famous series the way a textbook does, by writing out the first terms:

- *Pi*: `\frac{\pi^2}{6} = \frac{1}{1^2} + \frac{1}{2^2} + \frac{1}{3^2} + \frac{1}{4^2} + \cdots`
- *Pi*: `\arctan z = z - \frac{z^3}{3} + \frac{z^5}{5} - \frac{z^7}{7} + \cdots`
- *Archimedes*: `\sum_{n=0}^\infty 4^{-n} = 1 + 4^{-1} + 4^{-2} + 4^{-3} + \cdots = \frac{4}{3}`
- *Logarithm*: `\ln(n!) = \ln(1) + \ln(2) + \cdots + \ln(n)`

The translator raises `Unsupported("ellipsis")` on all of them, so none of the 9,676 relations that use `\cdots`, `\ldots` or `\dots` are checked. They are the most "checkable-looking" bucket in the ladder: real identities between computable expressions.

**What to build.** In `formulaci/translate/parser.py`, a recogniser that takes the explicit terms on either side of the ellipsis and infers a term formula `t(k)`, then emits `Sum(t(k), (k, 1, oo))` (or a finite `Sum` when a last term is given, as in the `\ln(n!)` example, or `Product` for `\cdots` between factors). Patterns worth covering, roughly in order of frequency on the pages: `1/k^p`, `x^k/k!`, `(-1)^k x^{2k+1}/(2k+1)`, geometric `r^k`, `1/(2k-1)`, odd/even index subsequences, and the finite forms `a_1 + \cdots + a_n`.

**Precision risk, which is why this is tier A and not a one-liner.** Three or four terms do not always determine the series: `1 + 2 + 4 + \cdots` could be `2^k` or the Catalan-like `1, 2, 4, 8, 16, 32, 63`. Refuse unless the inferred `t(k)` reproduces *every* explicit term and at least three terms are given. Divergent series summed by a method are stated the same way (`1 - 2 + 3 - 4 + \cdots = \frac{1}{4}` on the article of that name is an Abel sum and would be a false FAIL); the semantics stage already has `stated_false` and `approximation` cues, and a `\cdots` identity whose partial sums diverge should come back INCONCLUSIVE, never FAIL. The mutated bench will test this automatically once fixtures exist.

**Fixtures first.** Add ten written-out series you know (Basel, Leibniz, geometric, exponential, Mercator, arctan, `\ln(n!)`, harmonic partial sums) to `formulaci/bench/identities.py` in the ellipsis form, then make them PASS without any known-true identity FAILing.

**Acceptance.** Bench gate green; the ten fixtures PASS; their mutations FAIL; `1 - 2 + 3 - 4 + \cdots = 1/4` is not a FAIL.
