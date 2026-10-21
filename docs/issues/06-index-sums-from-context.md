coverage: supply bounds for `\sum_i` from the prose (6,698 relations, 2,101 pages)
labels: coverage, help-wanted, tier-B

- *Dirac delta function*: `\delta(g(x)) = \sum_i \frac{\delta(x - x_i)}{|g'(x_i)|}`
- *Hilbert space*: `\sum_{i \in I} \|x_i\|^2 < \infty`
- *Leonhard Euler*: `ds = \sum_i (k_i \cdot p_i - k_i) + 1`

A sum over an index with no bounds is refused (`Unsupported("sum_index_set")`). Many are genuinely not checkable (sums over an abstract index set, or over the roots of `g`), but a tractable subset has its range in the prose: "for i = 1, ..., n", "where the sum runs over the divisors of n", "over all primes p ≤ x", "over the k-subsets of {1, ..., n}".

**What to build.** Let the translator emit the sum with an unbound index and a marker; in `formulaci/semantics/prose.py` add patterns that extract a range or a finite set description; in verify, enumerate explicit finite sets (divisors, primes up to N, subsets for small n) with the existing `Sum` evaluator. Divisor sums and sums over primes cover number-theory pages (*Divisor function*, *Euler's totient function*, *Möbius function*) where identities are dense and often wrong in small ways.

**Precision risk.** A range stated for one sum applied to another in the same formula; sets that depend on an unstated variable. Attach a range only when the index letter matches and the sentence is adjacent.

**Fixtures.** Divisor-sum identities (`\sum_{d \mid n} \varphi(d) = n`), Möbius inversion instances, `\sum_{p \le x}` partial sums with explicit `x`.
