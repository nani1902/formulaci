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

# Second run (full corpus, 2026-10-21): 22 further confirmed errors
The second pass ran over all 952,136 formulas from 64,617 articles with the rules learned from the first review. 6,140 identities were checkable: 5,076 PASS, 756 INCONCLUSIVE, 308 FAIL. Of the 308, 10 were errors confirmed in the first run, 11 were first-run false positives that survived, and 287 were new; all 287 were reviewed (22 confirmed, 265 pipeline mistakes, 0 ambiguous). Pre-review precision rose from 4.9 % to 10.4 %. Three first-run errors are no longer flagged: two became INCONCLUSIVE under load (fewer qualifying sampling regimes, a per-point time cap) and the semigroup identity is now skipped as operator notation.
Every error below was re-fetched from the live page on 2026-10-21 and, where computable, recomputed with mpmath at 30 digits by the coordinator.

## Substantive
15. **54 (number)** › Trigonometry and the golden ratio ([page](https://en.wikipedia.org/wiki/54_(number)))
   - Written: `\sin{54} = \cos{\frac{\pi}{5}} = \frac{2\sqrt{5}}{4} = \frac{\phi}{2}`
   - The middle term 2\sqrt5/4 = \sqrt5/2 ≈ 1.118 is wrong; sin 54° = cos(π/5) = (1+√5)/4 = φ/2 ≈ 0.809. (The verifier also read sin 54 in radians, but the real error is the 2√5/4 term; 'sin 54' should also carry a degree sign.)
   - Fix: `\sin 54^\circ = \cos\frac{\pi}{5} = \frac{1+\sqrt{5}}{4} = \frac{\phi}{2}`
16. **Area of a circle** › Non-Euclidean circles ([page](https://en.wikipedia.org/wiki/Area_of_a_circle))
   - Written: `2\pi(1-\cos R) < \pi R^2 < 2\pi(1-\cosh R)`
   - The upper bound 2π(1−cosh R) is negative for all R>0, so πR^2 < 2π(1−cosh R) is false; the hyperbolic-disc area is 2π(cosh R − 1). The preceding formula A = 2πk^{-2}(1−cosh(kR)) on the page has the same sign error.
   - Fix: `2\pi(1-\cos R) < \pi R^2 < 2\pi(\cosh R - 1)`
17. **Basel problem** › Generalizations of Euler's method using elementary symmetric polynomials ([page](https://en.wikipedia.org/wiki/Basel_problem))
   - Written: `\frac{\pi^{2k}}{2}\cdot \frac{(2k) \cdot (-1)^k}{(2k+1)!} = -[x^{2k}] \frac{\sin(\pi x)}{\pi x} \times \sum_{i \geq 1} \zeta(2i) x^i.`
   - The generating series must be Σ ζ(2i) x^{2i}, not x^i: with x^i the coefficient identity already fails at k=1 (gives −ζ(4) instead of −ζ(2)). With x^{2i} it is exactly Newton's identity k e_k = Σ(−1)^{j−1} p_j e_{k−j} with e_k = π^{2k}/(2k+1)!, p_j = ζ(2j). (The verifier's failure came from reading [x^{2k}] as multiplication, but the formula is wrong anyway.)
   - Fix: `\frac{\pi^{2k}}{2}\cdot \frac{(2k) \cdot (-1)^k}{(2k+1)!} = -[x^{2k}] \frac{\sin(\pi x)}{\pi x} \times \sum_{i \geq 1} \zeta(2i) x^{2i}.`
18. **Bipolar coordinates** › Scale factors ([page](https://en.wikipedia.org/wiki/Bipolar_coordinates))
   - Written: `2\sin\tfrac{1}{2}\bigl(\sigma + i\tau\bigr) \sin\tfrac{1}{2}\bigl(\sigma - i\tau\bigr)
 = \cos\sigma - \cosh\tau,`
   - Sign error: 2 sin A sin B = cos(A−B) − cos(A+B) with A,B = ½(σ±iτ) gives cos(iτ) − cos σ = cosh τ − cos σ, not cos σ − cosh τ. Harmless downstream (the next line squares it and correctly writes (cosh τ − cos σ)²), but the displayed equation is wrong.
   - Fix: `2\sin\tfrac{1}{2}\bigl(\sigma + i\tau\bigr) \sin\tfrac{1}{2}\bigl(\sigma - i\tau\bigr) = \cosh\tau - \cos\sigma,`
19. **Dirichlet series inversion** › A formal generating-function-like convolution lemma ([page](https://en.wikipedia.org/wiki/Dirichlet_series_inversion)) *(verified by the reviewer's recomputation; coordinator re-checked live presence only)*
   - Written: `\begin{align}\sum_{r=0}^{\lfloor k/2 \rfloor} \frac{(-1)^{r+1} T^{2r}}{\log^{k-2r}(x) (2r)!} & = -\frac{1}{2}[z^k]\left(\frac{e^{\imath T \sqrt{z}}}{1-\frac{z}{\log x}} + \frac{e^{-\imath T \sqrt{z}}}{1+\frac{z}{\log x}}`
   - Under any reading of [z^k] the right-hand sides do not match the sums: row 1 already fails at k=1 (RHS T²/2 vs LHS −1/log x), and row 2 lacks a factor 1/i and has the wrong upper limit (r=⌊k/2⌋ gives a positive power of log x for even k). The sums are exactly the coefficients of −cos(Tz)/(1−z/log x) and −sin(Tz)/(1−z/log x) in z.
   - Fix: `\begin{align}\sum_{r=0}^{\lfloor k/2 \rfloor} \frac{(-1)^{r+1} T^{2r}}{\log^{k-2r}(x) (2r)!} & = -\frac{1}{2}[z^k]\frac{e^{\imath T z} + e^{-\imath T z}}{1-\frac{z}{\log x}} \\ \sum_{r=0}^{\lfloor (k-1)/2 \rfloor} \frac{(-1)^{r+1} T^{2r+1}}{\log^{k-2r-1}(x) (2`
20. **Discrete cosine transform** › Arithmetic complexity ([page](https://en.wikipedia.org/wiki/Discrete_cosine_transform))
   - Written: `~ \underbrace{\left[\frac{3}{2}N^3 \log_2N\right]}_\text{Real}+\underbrace{\left[\frac{3}{2}N^3 \log_2N-3N^3+3N^2\right]}_\text{Recursive} = \left[\frac{9}{2}N^3 \log_2N-3N^3+3N^2\right] ~.`
   - Arithmetic is inconsistent: 3/2 + 3/2 = 3, not 9/2. The 'Real' term is wrong: (1/8)N³log₂N butterflies × 24 real additions each (stated just before) = 3N³log₂N, which makes the stated total 9/2 N³log₂N − 3N³ + 3N² correct.
   - Fix: `~ \underbrace{\left[3N^3 \log_2N\right]}_\text{Real}+\underbrace{\left[\frac{3}{2}N^3 \log_2N-3N^3+3N^2\right]}_\text{Recursive} = \left[\frac{9}{2}N^3 \log_2N-3N^3+3N^2\right] ~.`
21. **Double factorial** › Additional identities ([page](https://en.wikipedia.org/wiki/Double_factorial)) *(verified by the reviewer's recomputation; coordinator re-checked live presence only)*
   - Written: `\begin{align}
(2n-1)!! &= \sum_{k=0}^{n-1} \binom{n}{k+1} (2k-1)!! (2n-2k-3)!! \\
  &= \sum_{k=1}^{n} \binom{n}{k} (2k-3)!! (2(n-k)-1)!! \\
  &= \sum_{k=0}^{n} \binom{2n-k-1}{k-1} \frac{(2k-1)(2n-k+1)}{k+1}(2n-2k-3)!! \\`
   - The third line has (2k−1) where the source (Callan 2009, identity (2)) has (2n−2k−1); as written it gives −1, −1, 13, 85 for n=1..4 instead of 1, 3, 15, 105. The other three lines are correct.
   - Fix: `&= \sum_{k=0}^{n} \binom{2n-k-1}{k-1} \frac{(2n-2k-1)(2n-k+1)}{k+1}(2n-2k-3)!!`
22. **Extreme learning machine** › Complex domain ([page](https://en.wikipedia.org/wiki/Extreme_learning_machine))
   - Written: `\arccos(z)= \int_0^z\frac{dt}{(1-t^2)^{1/2}}`
   - [confirmed] The integral from 0 to z of (1-t^2)^{-1/2} is arcsin(z), not arccos(z). At z = 0 the left side is pi/2 and the right side is 0.
   - Fix: `\arccos(z)= \int_z^1\frac{dt}{(1-t^2)^{1/2}}`
23. **Gautschi's inequality** › Related inequalities ([page](https://en.wikipedia.org/wiki/Gautschi's_inequality))
   - Written: `\frac{(x + 1)^{x + 1}}{(x + s)^{x + s}}e^{s - 1} < \frac{\Gamma(x + 1)}{\Gamma(x + s)} < \frac{(x + 1/2)^{x + 1/2}}{(x + s - 1/2)^{x + s - 1/2}}e^{s - 1}.`
   - [confirmed] The lower and upper bounds are swapped. Setting y -> x and x -> x+s-1 in the Guo–Qi–Srivastava inequality (valid for y > x > 0) and taking reciprocals gives the reverse ordering for s in (0,1).
   - Fix: `\frac{(x + 1/2)^{x + 1/2}}{(x + s - 1/2)^{x + s - 1/2}}e^{s - 1} < \frac{\Gamma(x + 1)}{\Gamma(x + s)} < \frac{(x + 1)^{x + 1}}{(x + s)^{x + s}}e^{s - 1}`
24. **Generating function transformation** › Examples of the generalized negative-order zeta series transformations ([page](https://en.wikipedia.org/wiki/Generating_function_transformation)) *(verified by the reviewer's recomputation; coordinator re-checked live presence only)*
   - Written: `\begin{align}
\frac{4 \sqrt{3} \pi}{9} & = \sum_{j \geq 0} \frac{8}{9^{j+1}}\left(2 \binom{j+\frac{1}{3}}{\frac{1}{3}}^{-1} + \frac{1}{2} \binom{j+\frac{2}{3}}{\frac{2}{3}}^{-1}\right) \\ 
\log\left(\frac{n^2-n+1}{n^2}\r`
   - [confirmed] In the second identity the series base should be (n^3+1)^{j+1}, not (n^2+1)^{j+1}. The first identity (4√3π/9) checks out numerically.
   - Fix: `\log\left(\frac{n^2-n+1}{n^2}\right) = \sum_{j \geq 0} \frac{1}{(n^3+1)^{j+1}}\left(\frac{2}{3 \cdot (j+1)} - n^2 \binom{j+\frac{1}{3}}{\frac{1}{3}}^{-1} + \frac{n}{2} \binom{j+\frac{2}{3}}{\frac{2}{3}}^{-1}\right)`
25. **Ginzburg–Landau theory** › Flux quantization ([page](https://en.wikipedia.org/wiki/Ginzburg%E2%80%93Landau_theory))
   - Written: `e^{ix}=e^{ix+2\pi n}`
   - [confirmed] The factor i is missing from the period: e^{ix} = e^{ix+2\pi n} is false for integer n ≠ 0 because e^{2\pi n} ≠ 1. Single-valuedness needs e^{ix} = e^{i(x+2\pi n)}.
   - Fix: `e^{ix}=e^{i(x+2\pi n)}`
26. **Half-range Fourier series** › Applications ([page](https://en.wikipedia.org/wiki/Half-range_Fourier_series))
   - Written: `\int_0^\pi \sin(mx)\,dx=\frac{1-(-1)^m}{2}.`
   - [confirmed] The denominator should be m, not 2. The preceding line states (1-cos(mπ))/m, and the next line uses (1-(-1)^{n±1})/(n±1).
   - Fix: `\int_0^\pi \sin(mx)\,dx=\frac{1-(-1)^m}{m}.`
27. **Holm–Bonferroni method** › Adjusted p-values ([page](https://en.wikipedia.org/wiki/Holm%E2%80%93Bonferroni_method))
   - Written: `1 - (1 - \alpha)^{1/n} < \alpha/n`
   - Inequality is reversed: for 0<\alpha<1 and n>=2, 1-(1-\alpha)^{1/n} > \alpha/n (the Sidak per-test threshold exceeds the Bonferroni one), which is exactly why the page's conclusion that Holm-Sidak is more powerful follows.
   - Fix: `1 - (1 - \alpha)^{1/n} > \alpha/n`
28. **The monkey and the coconuts** › The original version ([page](https://en.wikipedia.org/wiki/The_monkey_and_the_coconuts))
   - Written: `\tfrac{5}{4}(\tfrac{25}{4}F+\tfrac{9}{4})+1 = \tfrac{125}{16}F+\tfrac{241}{16}`
   - Arithmetic error: \tfrac54(\tfrac{25}4F+\tfrac94)+1 = \tfrac{125}{16}F+\tfrac{45}{16}+\tfrac{16}{16} = \tfrac{125}{16}F+\tfrac{61}{16}, not 241/16. The page's own final equation 1024N=15625F+11529 is only consistent with 61/16.
   - Fix: `\tfrac{5}{4}(\tfrac{25}{4}F+\tfrac{9}{4})+1 = \tfrac{125}{16}F+\tfrac{61}{16}`
29. **Tridecagon** › Construction ([page](https://en.wikipedia.org/wiki/Tridecagon))
   - Written: `\cos\left(\frac{2\pi}{13}\right)=\frac{1}{12}\left(2\sqrt{26-2\sqrt{13}}\cos\left(\frac{1}{3}\arctan\left(\frac{26+5\sqrt{13}}{9}\right)\right)+\sqrt{13}-1\right).`
   - The closed form is numerically wrong: the RHS is 0.86562477... while \cos(2\pi/13)=0.88545602.... The arctan argument (26+5\sqrt{13})/9 is wrong; with this prefactor structure the correct argument is (5\sqrt3+2\sqrt{39})/9.
   - Fix: `\cos\left(\frac{2\pi}{13}\right)=\frac{1}{12}\left(2\sqrt{26-2\sqrt{13}}\cos\left(\frac{1}{3}\arctan\left(\frac{5\sqrt{3}+2\sqrt{39}}{9}\right)\right)+\sqrt{13}-1\right)`
30. **Universal joint** › Double Cardan shaft ([page](https://en.wikipedia.org/wiki/Universal_joint))
   - Written: `\tan\left(\gamma + \tfrac{\pi}{2}\right) = \frac{1}{\tan\gamma}`
   - Sign error: \tan(\gamma+\pi/2)=-\cot\gamma=-1/\tan\gamma, not +1/\tan\gamma. The displayed derivation that follows (\tan\gamma_4=\cos\beta/\tan\gamma_2=1/\tan\gamma_1) inherits the missing minus signs, though its end result \tan(\gamma_1+\pi/2) is right.
   - Fix: `\tan\left(\gamma + \tfrac{\pi}{2}\right) = -\frac{1}{\tan\gamma}`

## Minor (rounding, typos, a self-referential definition)
31. **Blade element theory** › Example ([page](https://en.wikipedia.org/wiki/Blade_element_theory))
   - Written: `\begin{align} \int_{0}^{R} T_cdr & = \frac{0.15}{3}[0+2(0.038+0.600+1.050+1.091)+4(0+0.253+0.863+1.120+0912)+0] \\ & = 0.9075, \end{align}`
   - Typo '0912' (missing decimal point) for 0.912, the tabulated T_c at r/R=0.90; as written the bracket evaluates to 183.13, not 0.9075. With 0.912 the stated result 0.9075 is exact.
   - Fix: `\int_{0}^{R} T_c\,dr = \frac{0.15}{3}[0+2(0.038+0.600+1.050+1.091)+4(0+0.253+0.863+1.120+0.912)+0] = 0.9075`
32. **Cupola (geometry)** › Coordinates of the vertices ([page](https://en.wikipedia.org/wiki/Cupola_(geometry)))
   - Written: `\begin{align}
  & r_b \sqrt{ \left[\cos\left(\tfrac{2\pi}{n} - \alpha\right) - \cos \alpha\right]^2 + \left[\sin\left(\tfrac{2\pi}{n} - \alpha\right) - \sin\alpha\right]^2} \\[5pt]
  =\ & r_b \sqrt{ \left[\cos^2 \left(\t`
   - LaTeX typo on the second line: '\tfrac{2pi}{n}' is missing the backslash and renders as italic '2pi/n' instead of 2π/n. Mathematically the chain is otherwise correct (all three links verify with 2π).
   - Fix: `=\ & r_b \sqrt{ \left[\cos^2 \left(\tfrac{2\pi}{n} - \alpha\right) - 2\cos\left(\tfrac{2\pi}{n} - \alpha\right)\cos\alpha + \cos^2 \alpha \right] + \left[\sin^2 \left(\tfrac{2\pi}{n} - \alpha\right) - 2\sin\left(\tfrac{2\pi}{n} - \alpha\right) \sin\alpha + \si`
33. **Graphene** › Structure ([page](https://en.wikipedia.org/wiki/Graphene))
   - Written: `0.0399/0.0524 = 0.762`
   - [confirmed] Arithmetic and rounding slip: 0.0399/0.0524 = 0.76145..., which is 0.761 to three decimals, not 0.762. More precise inputs give the same answer.
   - Fix: `0.0399/0.0524 = 0.761`
34. **Limit of a function** › Infinite limits ([page](https://en.wikipedia.org/wiki/Limit_of_a_function))
   - Written: `\delta =  \tfrac{1}{\sqrt{N}\delta} = \tfrac{1}{\sqrt N}`
   - The chosen delta is garbled: 'delta = 1/(sqrt(N) delta)' defines delta in terms of itself and the middle term equals 1/sqrt(N) only if delta=1. The correct choice is simply delta = 1/sqrt(N).
   - Fix: `\delta = \tfrac{1}{\sqrt N}`
35. **Proportional hazards model** › A single binary covariate ([page](https://en.wikipedia.org/wiki/Proportional_hazards_model))
   - Written: `\exp(2.12) = 8.32`
   - exp(2.12)=8.3311..., which rounds to 8.33, not 8.32. The article gives no coefficient with more decimals, so the equation as written is wrong. It probably comes from an unrounded coefficient near 2.1188.
   - Fix: `\exp(2.12) \approx 8.33`
36. **Weighted arithmetic mean** › Exponentially decreasing weights ([page](https://en.wikipedia.org/wiki/Weighted_arithmetic_mean))
   - Written: `{1-e^{-1}}=0.61`
   - Numerical error: 1-e^{-1}=0.6321..., which rounds to 0.63, not 0.61. The page's companion value e^{-1}(1-w)=0.39(1-w) is wrong in the same way (e^{-1}=0.368, about 0.37).
   - Fix: `{1-e^{-1}}\approx 0.63`

## Pipeline mistakes in the second run, by cause (276 of 308 flags)

| cause | count |
|---|---|
| translator misread (double zeta read as Hurwitz zeta, elliptic K[·] and nome q[·], coefficient extraction [zⁿ], proof-line labels, conjugates) | 66 |
| wrong domain or constant (named constants such as the plastic, silver, supergolden ratios and the omega constant read as variables; dropped angle-sum and modulus constraints) | 63 |
| defining equation or equation to solve | 54 |
| the page itself says the equation is false | 26 |
| notation or convention (algorithm assignments, 0⁰, cycle notation, sgn(0)) | 22 |
| special algebra | 16 |
| extraction artifact | 11 |
| superscript is a label | 9 |
| stated approximation or rounding | 6 |
| other | 3 |
