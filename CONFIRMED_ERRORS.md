# Confirmed formula errors on English Wikipedia

First pass of formulaci, 2026-10-21. Pipeline run over 180,016 `<math>` formulas from the most-read
mathematics, physics, statistics and engineering articles. 2,867 were checkable identities; 266 were
flagged FAIL; every flag was reviewed by an independent reviewer with the brief in
`data/findings/review/REVIEWER_BRIEF.md`. 253 were pipeline mistakes (see "Pipeline mistakes" below) and
13 were confirmed as errors on the page. One further error was found by a reviewer next to a confirmed one.
Each of the 14 was then recomputed by the coordinator with mpmath at 30 digits and the live wikitext was
re-fetched on 2026-10-21 to confirm the formula is still there.

Nothing has been edited on Wikipedia. These are findings for editors.

## Substantive errors (wrong mathematics)

1. **Taylor series** › Term-by-term differentiation ([page](https://en.wikipedia.org/wiki/Taylor_series))
   - Written: `\frac{1}{(1-x)^3} = \sum_{n=2}^\infty n(n-1)x^{n-2}`
   - The sum equals `2/(1-x)^3`. At x = 0.3: sum = 5.8309, 1/(1-x)^3 = 2.9155.
   - Fix: `\frac{2}{(1-x)^3} = \sum_{n=2}^\infty n(n-1)x^{n-2}`

2. **Taylor series** › same section
   - Written: `\frac{1}{(1-x)^4} = \sum_{n=3}^\infty n(n-1)(n-2)x^{n-3}`
   - The sum equals `6/(1-x)^4`. At x = 0.3: sum = 24.9896, 1/(1-x)^4 = 4.1649.
   - Fix: `\frac{6}{(1-x)^4} = \sum_{n=3}^\infty n(n-1)(n-2)x^{n-3}`

3. **Dirichlet integral** › Evaluation › Dirichlet kernel ([page](https://en.wikipedia.org/wiki/Dirichlet_integral))
   - Written: `1 - \cos(x) = 1 - \sum_{k\geq 0}\frac{(-1)^{(k+1)}x^{2k}}{(2k)!} = \ldots`
   - The middle sum is `-\cos x`, so the middle expression equals `1 + \cos x`.
   - Fix: exponent `(-1)^k` in the middle sum.

4. **Dirichlet integral** › same section
   - Written: `\left|\frac{1-\cos x}{x^2}\right| = \left|-\sum_{k\geq 0}\frac{x^{2k}}{2(k+1)!}\right| \leq \ldots = e^{|x|}`
   - The correct series is `\sum_{k\geq 0}\frac{(-1)^k x^{2k}}{(2k+2)!}`. The page's sum equals
     `(e^{x^2}-1)/(2x^2)`; at x = 3 it is 450.1, which breaks the page's own bound e^3 ≈ 20.1.
   - Fix: `\left|\sum_{k\geq 0}\frac{(-1)^k x^{2k}}{(2k+2)!}\right|`

5. **Euler's constant** › Relation to gamma function ([page](https://en.wikipedia.org/wiki/Euler%27s_constant))
   - Written: `\gamma = \lim_{n\to\infty}\left(\frac{\Gamma(1/n)\Gamma(n+1)n^{1+1/n}}{\Gamma(2+n+1/n)} - \frac{n^2}{n+1}\right)`
   - The limit is −γ: at n = 10^6 the expression is −0.5772156. The two terms are swapped. (Uncited on the page.)
   - Fix: `\gamma = \lim_{n\to\infty}\left(\frac{n^2}{n+1} - \frac{\Gamma(1/n)\Gamma(n+1)n^{1+1/n}}{\Gamma(2+n+1/n)}\right)`

6. **List of trigonometric identities** › Sum of sines and cosines of arithmetic sequences, "Sine formulation 1" ([page](https://en.wikipedia.org/wiki/List_of_trigonometric_identities))
   - Written: `\sum_{k=0}^n \cos(a+kd) = \frac{\sin(d(n+1)/2)}{\sin(d/2)}\sin\left(a+\frac{nd}{2}\right)`
   - The left side should be a sum of sines (it fails already at n = 0, where cos a ≠ sin a).
   - Fix: `\sum_{k=0}^n \sin(a+kd) = \ldots`

7. **List of trigonometric identities** › "Sine formulation 2"
   - Written: `\sum_{k=1}^n \cos(a+kd) = \frac{\sin(nd/2)}{\sin(d/2)}\sin\left(a+\frac{n+1}{2}d\right)`
   - Same copy error. Fix: `\sum_{k=1}^n \sin(a+kd) = \ldots`

8. **List of definite integrals** › Definite integrals involving trigonometric functions ([page](https://en.wikipedia.org/wiki/List_of_definite_integrals))
   - Written: `\int_0^x\cos^{2m}(t)\,dt=\frac{(2m-1)!!}{(2m)!!}\Bigl(x-\sin x\cos x\Bigl(1+\sum_{k=1}^\infty\frac{\cos^{2k}x\,(2k)!!}{(2k+1)!!}\Bigr)\Bigr)`
   - Two errors: the sign before `\sin x\cos x` should be `+`, and the sum should stop at `k=m-1`.
     At m = 1, x = 0.7: page gives −0.0854, true value 0.5964, fixed formula 0.5964.
   - Fix: `x+\sin x\cos x\Bigl(1+\sum_{k=1}^{m-1}\ldots\Bigr)`

9. **List of definite integrals** › same section, the neighbouring sine formula (found by a reviewer, verified)
   - Written: `\int_0^x\sin^{2m}(t)\,dt=\frac{(2m-1)!!}{(2m)!!}\Bigl(x-\sin x\cos x\Bigl(1+\sum_{k=1}^\infty\frac{\sin^{2k}x\,(2k)!!}{(2k+1)!!}\Bigr)\Bigr)`
   - With the infinite sum the right side is identically 0. The sum should stop at `k=m-1`; the sign is correct.
     At m = 1, 2, 3 and x = 0.7 the fixed formula matches numeric integration to 30 digits.
   - Fix: `\sum_{k=1}^{m-1}`

10. **Volume of an n-ball** › Proofs › The two-dimension recursion formula ([page](https://en.wikipedia.org/wiki/Volume_of_an_n-ball))
    - Written: `\Gamma(3/2) = \tfrac12\,\Gamma(1/2) = \tfrac{\pi}{2}`
    - Γ(3/2) = √π/2 ≈ 0.8862, not π/2 ≈ 1.5708. The square root is missing.
    - Fix: `= \tfrac{\sqrt\pi}{2}`

11. **Special classes of semigroups** › List, row DS ([page](https://en.wikipedia.org/wiki/Special_classes_of_semigroups))
    - Written as the defining identity: `(a^\omega a^\omega a^\omega)^\omega = a^\omega`
    - `a^\omega` is idempotent, so this holds in every finite semigroup and defines nothing. The reviewer
      checked on the Brandt monoid B₂¹ (not in DS): the page's identity holds for every element while the
      standard DS identity fails. Suggested fix (Pin): `((ab)^\omega (ba)^\omega (ab)^\omega)^\omega = (ab)^\omega`.

## Minor errors (typos, rounding, exact sign where approximation is meant)

12. **Perfect number** › Even perfect numbers, footnote ([page](https://en.wikipedia.org/wiki/Perfect_number))
    - Written in `{{tmath}}`: `2^11 - 1 = 2047 = 23 \times 89`. Without braces this renders as 2¹1 − 1.
    - Fix: `2^{11} - 1`.

13. **Student's t-distribution** › Table of selected values ([page](https://en.wikipedia.org/wiki/Student%27s_t-distribution))
    - Written: `10 - 1.372\frac{\sqrt2}{\sqrt{11}} = 9.414`. The value is 9.41498, which rounds to 9.415,
      and the page's own upper bound 10.585 is rounded the other way. The interval (9.414, 10.585) is repeated below.
    - Fix: 9.415.

14. **Frequency comb** › History ([page](https://en.wikipedia.org/wiki/Frequency_comb))
    - Written: `2^{15} = 10^{4.5}`. 2^15 = 32768, 10^4.5 = 31623 (3.6 % apart). The point is the order of magnitude.
    - Fix: `\approx`.

## Pipeline mistakes (the 253 false positives), by cause

| cause | count |
|---|---|
| translator misread a function, operator, conjugate or residue symbol | 69 |
| semantics chose a wrong domain or constant, or dropped a stated constraint | 42 |
| arithmetic in a special structure (mod n, characteristic 2, ordinals, quaternions, semigroups) | 39 |
| superscript is a label, not a power | 32 |
| equation defines a constant or is to be solved, not an identity | 31 |
| the page itself says the equation is false | 12 |
| mixed numbers or other juxtaposition | 9 |
| extraction artifact | 6 |
| stated approximation or rounding | 6 |
| notation or convention (log base, numeral base, branch) | 5 |
| other | 2 |

Each cause has been fed back to the owning stage as a fixture and rule; see the second-pass numbers in the
stage READMEs once they land.
