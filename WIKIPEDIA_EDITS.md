# Wikipedia edits for the 14 confirmed formula errors

Ten pages, eleven edits (two pages take one edit each covering two formulas). Each entry gives the exact
current wikitext to find (copied from the live page on 2026-10-21, revision id noted), the exact replacement,
and an edit summary. Every fix was recomputed with mpmath at 30 digits; details are in `CONFIRMED_ERRORS.md`.

How to submit each one: open the page, click **Edit source** (not the visual editor), use Find on the
"Find" text, replace it with the "Replace" text, paste the summary into the edit summary box, click
**Show preview** and check the rendered formula, then **Publish**. If the Find text is not there, the page
changed since 2026-10-21; stop and re-check before editing. Per Wikipedia's guidance on AI assistance, these
were AI-found and human-verified; a line like "found with a computer-algebra check, verified by hand" in the
summary is honest and sufficient.

---

## 1. Taylor series — rev 1377126901 (two formulas, one edit)
Section: Calculation of Taylor series › Examples › Term-by-term differentiation

**Find (line 88):**
```
<math display="block">\frac{1}{(1-x)^3} = \sum_{n=2}^\infty n(n-1)x^{n-2},\quad |x|<1.</math>
```
**Replace:**
```
<math display="block">\frac{2}{(1-x)^3} = \sum_{n=2}^\infty n(n-1)x^{n-2},\quad |x|<1.</math>
```
**Find (line 89):**
```
<math display="block">\frac{1}{(1-x)^4} = \sum_{n=3}^\infty n(n-1)(n-2)x^{n-3},\quad |x|<1.</math>
```
**Replace:**
```
<math display="block">\frac{6}{(1-x)^4} = \sum_{n=3}^\infty n(n-1)(n-2)x^{n-3},\quad |x|<1.</math>
```
**Summary:** `Term-by-term differentiation: the second and third derivatives of 1/(1−x) are 2/(1−x)^3 and 6/(1−x)^4; the series as written were missing those constants (e.g. at x=0.3 the sum is 5.83, not 2.92). Found with a computer-algebra check, verified by hand.`

---

## 2. Dirichlet integral — rev 1370330378 (two formulas, one edit)
Section: Evaluation › Dirichlet kernel

**Find (line 169):**
```
1 - \cos(x) = 1 - \sum_{k\geq 0}\frac{{(-1)^{(k+1)}}x^{2k}}{(2k)!} = \sum_{k\geq 1}\frac{{(-1)^{(k+1)}}x^{2k}}{(2k)!}.
```
**Replace:**
```
1 - \cos(x) = 1 - \sum_{k\geq 0}\frac{(-1)^{k}x^{2k}}{(2k)!} = \sum_{k\geq 1}\frac{(-1)^{(k+1)}x^{2k}}{(2k)!}.
```
**Find (line 174):**
```
  =  \left|-\sum_{k\geq 0}\frac{x^{2k}}{2(k+1)!}\right|
```
**Replace:**
```
  =  \left|\sum_{k\geq 0}\frac{(-1)^{k}x^{2k}}{(2k+2)!}\right|
```
**Summary:** `Dirichlet kernel bound: fix the cosine series (the middle sum with (−1)^(k+1) is −cos x, not cos x) and the series for (1−cos x)/x^2, which is Σ(−1)^k x^(2k)/(2k+2)!; the previous expression Σ x^(2k)/(2(k+1)!) equals (e^(x²)−1)/(2x²) and at x=3 exceeds the e^|x| bound used next. Verified numerically.`

---

## 3. Euler's constant — rev 1378444832
Section: Formulas and identities › Relation to gamma function

**Find (line 187):**
```
\gamma &= \lim_{n\to\infty}\left(\frac{ \Gamma\left(\frac1{n}\right) \Gamma(n+1)\, n^{1+\frac1{n}}}{\Gamma\left(2+n+\frac1{n}\right)} - \frac{n^2}{n+1}\right) \\
```
**Replace:**
```
\gamma &= \lim_{n\to\infty}\left(\frac{n^2}{n+1} - \frac{ \Gamma\left(\frac1{n}\right) \Gamma(n+1)\, n^{1+\frac1{n}}}{\Gamma\left(2+n+\frac1{n}\right)}\right) \\
```
**Summary:** `Relation to gamma function: the limit as written tends to −γ (at n=10^6 the expression is −0.5772157); swapped the two terms so it equals γ. The second line is unchanged. Verified numerically; the formula is uncited.`

---

## 4. List of trigonometric identities — rev 1379178075 (two formulas, one edit)
Section: Miscellaneous › Sum of Sines and Cosines of Arithmetic Sequences

**Find (line 1190):**
```
    \sum_{k=0}^n \cos (a + kd) = \frac{\sin (d(n+1)/2)}{\sin(d/2)}\sin\Big(a + \frac{nd}{2} \Big).
```
**Replace:**
```
    \sum_{k=0}^n \sin (a + kd) = \frac{\sin (d(n+1)/2)}{\sin(d/2)}\sin\Big(a + \frac{nd}{2} \Big).
```
**Find (line 1195):**
```
    \sum_{k=1}^n \cos (a + kd) = \frac{\sin (nd/2)}{\sin(d/2)}\sin\Big(a + \frac{n+1}{2}d \Big).
```
**Replace:**
```
    \sum_{k=1}^n \sin (a + kd) = \frac{\sin (nd/2)}{\sin(d/2)}\sin\Big(a + \frac{n+1}{2}d \Big).
```
**Summary:** `Sine formulations 1 and 2: the left-hand sides summed cos(a+kd) but the right-hand sides (and the cited ProofWiki source) are the sums of sin(a+kd); fails already at n=0. Changed cos to sin.`

---

## 5. List of definite integrals — rev 1336422728 (two formulas, one edit)
Section: Definite integrals involving trigonometric functions

**Find (line 46):**
```
<math>\int_0^{x}\sin^{2m}(t)dt=\frac{(2m-1)!!}{(2m)!!}\Biggl(x-\sin(x)\cos(x)\Biggl(1+\sum_{k=1}^\infty\frac{\sin^{2k}(x)(2k)!!}{(2k+1)!!}\Biggr)\Biggr)\quad\text{for }m=1,2,3\ldots</math>
```
**Replace:**
```
<math>\int_0^{x}\sin^{2m}(t)dt=\frac{(2m-1)!!}{(2m)!!}\Biggl(x-\sin(x)\cos(x)\Biggl(1+\sum_{k=1}^{m-1}\frac{\sin^{2k}(x)(2k)!!}{(2k+1)!!}\Biggr)\Biggr)\quad\text{for }m=1,2,3\ldots</math>
```
**Find (line 47):**
```
<math>\int_0^{x}\cos^{2m}(t)dt=\frac{(2m-1)!!}{(2m)!!}\Biggl(x-\sin(x)\cos(x)\Biggl(1+\sum_{k=1}^\infty\frac{\cos^{2k}(x)(2k)!!}{(2k+1)!!}\Biggr)\Biggr)\quad\text{for }m=1,2,3\ldots</math>
```
**Replace:**
```
<math>\int_0^{x}\cos^{2m}(t)dt=\frac{(2m-1)!!}{(2m)!!}\Biggl(x+\sin(x)\cos(x)\Biggl(1+\sum_{k=1}^{m-1}\frac{\cos^{2k}(x)(2k)!!}{(2k+1)!!}\Biggr)\Biggr)\quad\text{for }m=1,2,3\ldots</math>
```
**Summary:** `Reduction formulas for ∫sin^(2m) and ∫cos^(2m): the inner sums run to k=m−1, not ∞ (with ∞ the sine formula is identically 0), and the cosine formula needs +sin x cos x. Checked against numerical integration for m=1,2,3.`

---

## 6. Volume of an n-ball — rev 1377731322
Section: Proofs › The two-dimension recursion formula

**Find (line 191):**
```
{{tmath|1= \Gamma\bigl(\tfrac32\bigr) = \tfrac12 \cdot \Gamma\bigl(\tfrac12\bigr) = \tfrac\pi2}}
```
**Replace:**
```
{{tmath|1= \Gamma\bigl(\tfrac32\bigr) = \tfrac12 \cdot \Gamma\bigl(\tfrac12\bigr) = \tfrac{\sqrt\pi}{2}}}
```
**Summary:** `Γ(3/2) = √π/2, not π/2 (Γ(1/2) = √π). Consistent with V_1(R) = 2R.`

---

## 7. Special classes of semigroups — rev 1375897417
Section: List of special classes of semigroups, row DS

**Find (line 1070):**
```
*Equivalently, for finite monoids: <math>(a^\omega a^\omega a^\omega)^\omega=a^\omega</math>.
```
**Replace:**
```
*Equivalently, for finite monoids: <math>((ab)^\omega (ba)^\omega (ab)^\omega)^\omega=(ab)^\omega</math>.
```
**Summary:** `DS row: the identity (a^ω a^ω a^ω)^ω = a^ω holds in every finite semigroup (a^ω is idempotent) so it cannot characterize DS; replaced with the standard identity ((ab)^ω(ba)^ω(ab)^ω)^ω = (ab)^ω (Pin, cited on the row).`

**Before submitting:** this row cites Pin p. 158. Please confirm the replacement identity against that source
(it is the standard DS identity in Pin's and Almeida's treatments). The reviewer also checked it on the Brandt
monoid B₂¹, which is not in DS: the old identity holds there, the new one fails, as it should.

---

## 8. Perfect number — rev 1378937800
Section: Even perfect numbers (footnote text)

**Find (line 31):**
```
{{tmath|1=2^11 - 1 = 2047 = 23 \times 89}}
```
**Replace:**
```
{{tmath|1=2^{11} - 1 = 2047 = 23 \times 89}}
```
**Summary:** `Add braces to the exponent: 2^11 renders as 2^1 followed by 1.`

---

## 9. Student's t-distribution — rev 1370501651 (two occurrences, one edit)
Section: Occurrence and applications › Table of selected values

**Find (line 917):**
```
<math display="block">\ 10 - 1.372\ \frac{ \sqrt{2\ } }{\ \sqrt{11\ }\ } = 9.414 ~.</math>
```
**Replace:**
```
<math display="block">\ 10 - 1.372\ \frac{ \sqrt{2\ } }{\ \sqrt{11\ }\ } = 9.415 ~.</math>
```
**Find (a few lines below):**
```
= ( 9.414,\, 10.585) \,.</math>
```
**Replace:**
```
= ( 9.415,\, 10.585) \,.</math>
```
**Summary:** `10 − 1.372·√2/√11 = 9.41498, which rounds to 9.415 (the upper bound 10.585 is already rounded the same way).`

---

## 10. Frequency comb — rev 1363475288
Section: History

**Find (line 112):**
```
<math>2^{15} = 10^{4.5}</math>
```
**Replace:**
```
<math>2^{15} \approx 10^{4.5}</math>
```
**Summary:** `2^15 = 32768 and 10^4.5 ≈ 31623; changed = to ≈ (the point is the order of magnitude).`
