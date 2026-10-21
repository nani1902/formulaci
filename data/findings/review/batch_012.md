# Review batch 012 — 22 items

For each item answer with one JSON line (Finding schema): {"formula_id": ..., "verdict": "FAIL", "review": {"status": "confirmed_error"|"false_positive"|"ambiguous", "reviewer": "<name>", "notes": "<why, one or two sentences>"}, "suggested_fix": "<corrected LaTeX or null>", "evidence": "<independent source or derivation>"}


---
## wiki:en:61229:1379891258:5

- Page: [Straightedge and compass construction](https://en.wikipedia.org/wiki/Straightedge_and_compass_construction) › Constructible points > Relation to complex arithmetic  · verdict **FAIL**, symbolic unknown
- LaTeX: `\left | z \right | = \sqrt{z \bar z}.\;`
- Context before: …e smallest field containing the original ratios and closed under taking complex conjugates and square roots. For example, the real part, imaginary part and modulus of a point or ratio z (taking one of the two viewpoints above) are constructible as these may be expressed as $\mathrm{Re}(z)=\frac{z+\bar z}{2}\;$ $\mathrm{Im}(z)=\frac{z-\bar z}{2i}\;$
- Context after: Doubling the cube and trisection of an angle (except for special angles such as any φ such that φ/(2π)) is a rational number with denominator not divisible by 3) require ratios which are the solution to cubic equations, while squaring the circle requires a transcendental ratio. None of these are in the fields described, hence no straightedge-and-co…
- Translator read: `Abs(z)`  =  `sqrt(z*z_bar)`  · notes: pre:left_right
pre:spacing
pre:trailing_punct
ambig:bar:z_bar
sides: | z \right |  ||  \sqrt{z \bar z}
- Assumptions: domains {'z': 'complex', 'z_bar': 'complex'}; constants {}; constraints []
- Verifier: The identity fails at 70 of 72 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, complex, large) (e.g. at z=0.0761123, z_bar=0.0549291: lhs=0.076112300000, rhs=0.064658952496).
- Counterexample: {'z': '0.0761123', 'z_bar': '0.0549291'} → lhs 0.07611230000000000000000000000000000000, rhs 0.06465895249638676291567625162016402614, rel diff 0.1504795874
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 10/12 fail, 0 err, mixed_sign 12/20 fail, 8 err, complex 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:61229:1379891258:4

- Page: [Straightedge and compass construction](https://en.wikipedia.org/wiki/Straightedge_and_compass_construction) › Constructible points > Relation to complex arithmetic  · verdict **FAIL**, symbolic unknown
- LaTeX: `\mathrm{Im}(z)=\frac{z-\bar z}{2i}\;`
- Context before: …om such a set of ratios is precisely the smallest field containing the original ratios and closed under taking complex conjugates and square roots. For example, the real part, imaginary part and modulus of a point or ratio z (taking one of the two viewpoints above) are constructible as these may be expressed as $\mathrm{Re}(z)=\frac{z+\bar z}{2}\;$
- Context after: $\left | z \right | = \sqrt{z \bar z}.\;$ Doubling the cube and trisection of an angle (except for special angles such as any φ such that φ/(2π)) is a rational number with denominator not divisible by 3) require ratios which are the solution to cubic equations, while squaring the circle requires a transcendental ratio. None of these are in the fiel…
- Translator read: `im(z)`  =  `(z - z_bar)/(2*i)`  · notes: pre:spacing
pre:trailing_punct
ambig:bar:z_bar
hint:i_present
sides: \mathrm{Im}(z)  ||  \frac{z-\bar z}{2i}
- Assumptions: domains {'z': 'complex', 'z_bar': 'complex'}; constants {'i': 'I'}; constraints []
- Verifier: The identity fails at 71 of 72 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, complex, large) (e.g. at z=0.0785787, z_bar=0.0544606: lhs=0, rhs=(0.0 - 0.01205).
- Counterexample: {'z': '0.0785787', 'z_bar': '0.0544606'} → lhs 0, rhs (0.0 - 0.01205905j), rel diff 1.0000000000
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 11/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, complex 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:28305:1380903411:18

- Page: [String theory](https://en.wikipedia.org/wiki/String_theory) › AdS/CFT correspondence > Applications to infrared duality  · verdict **FAIL**, symbolic unknown
- LaTeX: `a^{\Omega}<a/2`
- Context before: …theory is then half of that of the parent theory. In Scenario II, however, the projection breaks the superconformal symmetry and does not produce a new fixed point. The most interesting case is Scenario III, in which the orientifolded theory still reaches a superconformal fixed point, but with different $R$ -charges than the parent theory and with
- Context after: . In this case, some examples show that the theory obtained via Scenario III orientifold has the same $R$ -charges, the same central charge and the same superconformal index as another theory obtained via Scenario I orientifold. This suggests the existence of an infrared duality between two apparently different orientifolded theories. The duality i…
- Translator read: `a**Omega`  <  `a/2`  · notes: sides: a^{\Omega}  ||  a/2
- Assumptions: domains {'Omega': 'positive', 'a': 'real'}; constants {}; constraints ['a > 0']
- Verifier: The inequality fails at 57 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at Omega=0.104105, a=0.200764: lhs=0.846069636245, rhs=0.100382000000).
- Counterexample: {'Omega': '0.104105', 'a': '0.200764'} → lhs 0.84606963624588765022143369168133650884, rhs 0.10038200000000000000000000000000000000, rel diff 0.8813549196
- Regimes: small_positive 9/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:105375:1370501651:158

- Page: [Student's t-distribution](https://en.wikipedia.org/wiki/Student's_t-distribution) › Occurrence and applications > Table of selected values  · verdict **FAIL**, symbolic not_equal
- LaTeX: `10 + 1.372\, \frac{\sqrt{2}}{ \sqrt{11} } = 10.585 \,.`
- Context before: …s say we have a sample with size 11, sample mean 10, and sample variance 2. For 90% confidence with 10 degrees of freedom, the one-sided t value from the table is 1.372 . Then with confidence interval calculated from $\overline{X}_n \pm t_{\alpha,\nu} \, \frac{S_n}{\sqrt{n}}\, ,$ we determine that with 90% confidence we have a true mean lying below
- Context after: In other words, 90% of the times that an upper threshold is calculated by this method from particular samples, this upper threshold exceeds the true mean. And with 90% confidence we have a true mean lying above $\ 10 - 1.372\ \frac{ \sqrt{2\ } }{\ \sqrt{11\ }\ } = 9.414 ~.$ In other words, 90% of the times that a lower threshold is calculated by th…
- Translator read: `343*sqrt(22)/2750 + 10`  =  `2117/200`  · notes: pre:spacing
pre:trailing_punct
sides: 10 + 1.372\, \frac{\sqrt{2}}{ \sqrt{11} }  ||  10.585
- Assumptions: domains {}; constants {}; constraints []
- Verifier: The constant identity does not hold: both sides differ beyond 1e-8 relative error, stably at two working precisions (lhs=10.585022765679795, rhs=10.585000000000000).
- Counterexample: {} → lhs 10.5850227656797950317149131377984552488, rhs 10.5850000000000000000000000000000000000, rel diff 0.0000021507
- Regimes: constant 1/1 fail, 0 err

---
## wiki:en:105375:1370501651:159

- Page: [Student's t-distribution](https://en.wikipedia.org/wiki/Student's_t-distribution) › Occurrence and applications > Table of selected values  · verdict **FAIL**, symbolic not_equal
- LaTeX: `\ 10 - 1.372\ \frac{ \sqrt{2\ } }{\ \sqrt{11\ }\ } = 9.414 ~.`
- Context before: …we determine that with 90% confidence we have a true mean lying below $10 + 1.372\, \frac{\sqrt{2}}{ \sqrt{11} } = 10.585 \,.$ In other words, 90% of the times that an upper threshold is calculated by this method from particular samples, this upper threshold exceeds the true mean. And with 90% confidence we have a true mean lying above
- Context after: In other words, 90% of the times that a lower threshold is calculated by this method from particular samples, this lower threshold lies below the true mean. So that at 80% confidence (calculated from 100% − 2 × (1 − 90%) = 80%), we have a true mean lying within the interval…
- Translator read: `10 - 343*sqrt(22)/2750`  =  `4707/500`  · notes: pre:spacing
pre:trailing_punct
sides: 10 - 1.372\ \frac{ \sqrt{2\ } }{\ \sqrt{11\ }\ }  ||  9.414
- Assumptions: domains {}; constants {}; constraints []
- Verifier: The constant identity does not hold: both sides differ beyond 1e-8 relative error, stably at two working precisions (lhs=9.4149772343202049, rhs=9.4140000000000000).
- Counterexample: {} → lhs 9.41497723432020496828508686220154475118, rhs 9.41400000000000000000000000000000000000, rel diff 0.0001037957
- Regimes: constant 1/1 fail, 0 err

---
## wiki:en:30448:1377126901:25

- Page: [Taylor series](https://en.wikipedia.org/wiki/Taylor_series) › Calculation of Taylor series > Examples > Term-by-term differentiation  · verdict **FAIL**, symbolic unknown
- LaTeX: `\frac{1}{(1-x)^3} = \sum_{n=2}^\infty n(n-1)x^{n-2},\quad |x|<1.`
- Context before: …ries can be differentiated term-by-term. For example, differentiating the geometric series $\frac1{1-x} = 1 + x + x^2 + x^3 + \cdots,\quad |x|<1,$ one gets $\frac{d}{dx}\frac{1}{1-x} = \frac{1}{(1-x)^2} = 0 + 1 + 2x + 3x^2 + \cdots, \quad |x|<1.$ Thus $\frac{1}{(1-x)^2} = \sum_{n=1}^\infty nx^{n-1},\quad |x|<1.$ This process can be iterated, giving
- Context after: $\frac{1}{(1-x)^4} = \sum_{n=3}^\infty n(n-1)(n-2)x^{n-3},\quad |x|<1.$ and so forth. Term-by-term integration. Inside the region of convergence, a Taylor series can be integrated term-by-term. For example, integrating the geometric series $\frac1{1-t} = 1 + t + t^2 + t^3 + \cdots,\quad |t|<1,$ one gets…
- Translator read: `(1 - x)**(-3)`  =  `Sum(n*x**(n - 2)*(n - 1), (n, 2, oo))`  · notes: pre:spacing
pre:trailing_punct
cond: |x|<1
sides: \frac{1}{(1-x)^3}  ||  \sum_{n=2}^\infty n(n-1)x^{n-2}
- Assumptions: domains {'x': 'real'}; constants {}; constraints ['Abs(x) < 1', 'Ne(1 - x, 0)']
- Verifier: The identity fails at 25 of 25 evaluable points, a clear majority in every regime (small_positive, unit_interval, mixed_sign, large) (e.g. at x=0: lhs=1.000000000000, rhs=2.000000000000).
- Counterexample: {'x': '0'} → lhs 1.00000000000000000000000000000000000000, rhs 2.00000000000000000000000000000000000000, rel diff 0.5000000000
- Regimes: small_positive 6/6 fail, 0 err, unit_interval 6/6 fail, 0 err, integers_small 1/1 fail, 0 err, mixed_sign 6/6 fail, 0 err, large 6/6 fail, 0 err

---
## wiki:en:30448:1377126901:26

- Page: [Taylor series](https://en.wikipedia.org/wiki/Taylor_series) › Calculation of Taylor series > Examples > Term-by-term differentiation  · verdict **FAIL**, symbolic unknown
- LaTeX: `\frac{1}{(1-x)^4} = \sum_{n=3}^\infty n(n-1)(n-2)x^{n-3},\quad |x|<1.`
- Context before: …ng the geometric series $\frac1{1-x} = 1 + x + x^2 + x^3 + \cdots,\quad |x|<1,$ one gets $\frac{d}{dx}\frac{1}{1-x} = \frac{1}{(1-x)^2} = 0 + 1 + 2x + 3x^2 + \cdots, \quad |x|<1.$ Thus $\frac{1}{(1-x)^2} = \sum_{n=1}^\infty nx^{n-1},\quad |x|<1.$ This process can be iterated, giving $\frac{1}{(1-x)^3} = \sum_{n=2}^\infty n(n-1)x^{n-2},\quad |x|<1.$
- Context after: and so forth. Term-by-term integration. Inside the region of convergence, a Taylor series can be integrated term-by-term. For example, integrating the geometric series $\frac1{1-t} = 1 + t + t^2 + t^3 + \cdots,\quad |t|<1,$ one gets $-\log(1-x) = \int_0^x \frac{dt}{1-t} = x + \frac{x^2}{2} + \frac{x^3}{3} + \frac{x^4}{4} + \cdots,\quad |x|<1.$ This…
- Translator read: `(1 - x)**(-4)`  =  `Sum(n*x**(n - 3)*(n - 2)*(n - 1), (n, 3, oo))`  · notes: pre:spacing
pre:trailing_punct
cond: |x|<1
sides: \frac{1}{(1-x)^4}  ||  \sum_{n=3}^\infty n(n-1)(n-2)x^{n-3}
- Assumptions: domains {'x': 'real'}; constants {}; constraints ['Abs(x) < 1', 'Ne(1 - x, 0)']
- Verifier: The identity fails at 25 of 25 evaluable points, a clear majority in every regime (small_positive, unit_interval, mixed_sign, large) (e.g. at x=0: lhs=1.000000000000, rhs=6.000000000000).
- Counterexample: {'x': '0'} → lhs 1.00000000000000000000000000000000000000, rhs 6.00000000000000000000000000000000000000, rel diff 0.8333333333
- Regimes: small_positive 6/6 fail, 0 err, unit_interval 6/6 fail, 0 err, integers_small 1/1 fail, 0 err, mixed_sign 6/6 fail, 0 err, large 6/6 fail, 0 err

---
## wiki:en:30448:1377126901:148

- Page: [Taylor series](https://en.wikipedia.org/wiki/Taylor_series) › List of Maclaurin series of some common functions > Polylogarithmic functions  · verdict **FAIL**, symbolic unknown
- LaTeX: `\begin{align}
\text{Ti}_{2}(x) &= \sum_{n = 0}^{\infty} \frac{(-1)^{n}}{(2n + 1)^2} x^{2n + 1} \\
\text{Ti}_{3}(x) &= \sum_{n = 0}^{\infty} \frac{(-1)^{n}}{(2n + 1)^3} x^{2n + 1}
\end{align}`
- Context before: …The Legendre chi functions are defined as follows: $\begin{align} \chi_{2}(x) &= \sum_{n = 0}^{\infty} \frac{1}{(2n + 1)^2} x^{2n + 1} \\ \chi_{3}(x) &= \sum_{n = 0}^{\infty} \frac{1}{(2n + 1)^3} x^{2n + 1} \end{align}$ And the formulas presented below are called inverse tangent integrals:
- Context after: These formulas occur in statistical mechanics. Integrals encountered in Bose–Einstein and Fermi–Dirac statistics can be expressed in terms of polylogarithms. The inverse tangent integral value $\text{Ti}_2(1/\sqrt{3})$ appears in the per-site entropy of spanning trees on a large triangular lattice. Elliptic functions. The complete elliptic integral…
- Translator read (piece 0): `Ti_2*x`  =  `Sum((-1)**n*x**(2*n + 1)/(2*n + 1)**2, (n, 0, oo))`  · notes: pre:env_align
pre:rows=2
text_symbol:Ti
sides: \text{Ti}_{2}(x)  ||  \sum_{n = 0}^{\infty} \frac{(-1)^{n}}{(2n + 1)^2} x^{2n + 1}
- Translator read (piece 1): `Ti_3*x`  =  `Sum((-1)**n*x**(2*n + 1)/(2*n + 1)**3, (n, 0, oo))`  · notes: pre:env_align
pre:rows=2
text_symbol:Ti
sides: \text{Ti}_{3}(x)  ||  \sum_{n = 0}^{\infty} \frac{(-1)^{n}}{(2n + 1)^3} x^{2n + 1}
- Assumptions: domains {'Ti_2': 'positive', 'Ti_3': 'positive', 'x': 'real'}; constants {}; constraints []
- Verifier: Chain link 0: The identity fails at 19 of 21 evaluable points, a clear majority in every regime (small_positive, unit_interval, mixed_sign) (e.g. at Ti_2=0.07382, x=0.0886145: lhs=0.006541522390, rhs=0.088537401252).
- Counterexample: {'Ti_2': '0.07382', 'x': '0.0886145'} → lhs 0.00654152239000000000000000000000000000, rhs 0.08853740125235612923090546858327438747, rel diff 0.9261157172
- Regimes: small_positive 6/10 fail, 4 err, unit_interval 6/6 fail, 0 err, integers_small 1/35 fail, 32 err, mixed_sign 6/16 fail, 10 err, large 0/40 fail, 40 err

---
## wiki:en:482379:1378391024:236

- Page: [Tetration](https://en.wikipedia.org/wiki/Tetration) › Inverse operations > Super-root > Square super-root  · verdict **FAIL**, symbolic unknown
- LaTeX: `\sqrt[y]{x} = \log_y x.`
- Context before: …)$ and $\sqrt{x}_s$ . It is the inverse of $^2 x = x^x$ and can be represented with the Lambert W function: $\mathrm{ssrt}(x)=\exp(W(\ln x))=\frac{\ln x}{W(\ln x)}$ or $\sqrt{x}_s=e^{W(\ln x)}$ The function also illustrates the reflective nature of the root and logarithm functions, as the equation below only holds true when $y = \mathrm{ssrt}(x)$ :
- Context after: Like square roots, the square super-root of x may not have a single solution. Unlike square roots, determining the number of square super-roots of x may be difficult. In general, if $e^{-1/e}<x<1$ , then x has two positive square super-roots between 0 and 1, calculated as $\sqrt{x}_s=\left\{e^{W_{-1}(\ln x)};e^{W_{0}(\ln x)}\right\},$ and if $x > 1…
- Translator read: `x**(1/y)`  =  `log(x)/log(y)`  · notes: pre:trailing_punct
nth_root
log_base_given
sides: \sqrt[y]{x}  ||  \log_y x
- Assumptions: domains {'x': 'real', 'y': 'positive'}; constants {}; constraints ['x < 1', 'x > 0', 'Ne(log(y), 0)']
- Verifier: The identity fails at 38 of 38 evaluable points, a clear majority in every regime (small_positive, unit_interval, large) (e.g. at x=0.118935, y=0.0776313: lhs=0.000000000001, rhs=0.833082008587).
- Counterexample: {'x': '0.118935', 'y': '0.0776313'} → lhs 0.00000000000122656910444784029465200038, rhs 0.83308200858714092030404621964828282214, rel diff 0.9999999999
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 0/0 fail, 0 err, mixed_sign 3/3 fail, 0 err, large 11/11 fail, 0 err

---
## wiki:en:449745:1370749078:129

- Page: [Theta function](https://en.wikipedia.org/wiki/Theta_function) › Nome power theorems > Modulus dependent theorems  · verdict **FAIL**, symbolic unknown
- LaTeX: `\theta_4\bigl[\exp(-3\sqrt{2}\,\pi)\bigr] = 
\theta_4\bigl[\exp(-\sqrt{2}\,\pi)\bigr] \,3^{-1/2} \bigl(\sqrt{3} + \sqrt{2}\,\bigr)^{1/2}`
- Context before: …lid. And for this formula two examples shall be given: First calculation example with the value $t = 1$ inserted: $\theta_4\biggl\langle q\bigl\{\tan\bigl[\tfrac{1}{2}\arctan(1)\bigr]\bigr\}^3 \biggr\rangle = \theta_4\biggl\langle q\bigl\{\tan\bigl[\tfrac{1}{2}\arctan(1)\bigr]\bigr\} \biggr\rangle \,3^{-1/2} \bigl(\sqrt{3} + \sqrt{2}\,\bigr)^{1/2}$
- Context after: Second calculation example with the value $t = \Phi^{-2}$ inserted: $\theta_4\biggl\langle q\bigl\{\tan\bigl[\tfrac{1}{2}\arctan(\Phi^{-6})\bigr]\bigr\}^3 \biggr\rangle = \theta_4\biggl\langle q\bigl\{\tan\bigl[\tfrac{1}{2}\arctan(\Phi^{-6})\bigr]\bigr\} \biggr\rangle \,3^{-1/2} \bigl(\sqrt{2\sqrt{\Phi^{-8} - \Phi^{-4} + 1} - \Phi^{-4} + 2} + \sqrt…
- Translator read: `theta_4*exp(-3*sqrt(2)*pi)`  =  `sqrt(3)*theta_4*sqrt(sqrt(2) + sqrt(3))*exp(-sqrt(2)*pi)/3`  · notes: pre:size
pre:spacing
sides: \theta_4\bigl[\exp(-3\sqrt{2}\,\pi)\bigr]  ||  \theta_4\bigl[\exp(-\sqrt{2}\,\pi)\bigr] \,3^{-1/2} \bigl(\sqrt{3} + \sqrt{2}\,\bigr)^{1/2}
- Assumptions: domains {'theta_4': 'real'}; constants {}; constraints []
- Verifier: The identity fails at 59 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at theta_4=0.0285494: lhs=0.000000046455, rhs=0.000343885940).
- Counterexample: {'theta_4': '0.0285494'} → lhs 0.00000004645563000446344968079228096077, rhs 0.00034388594047278355730038499330216148, rel diff 0.9998649097
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 11/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:449745:1370749078:132

- Page: [Theta function](https://en.wikipedia.org/wiki/Theta_function) › Nome power theorems > Modulus dependent theorems  · verdict **FAIL**, symbolic unknown
- LaTeX: `\theta_4\bigl[\exp(-3\sqrt{10}\,\pi)\bigr] = 
\theta_4\bigl[\exp(-\sqrt{10}\,\pi)\bigr] \,3^{-1/2} \bigl(\sqrt{2\sqrt{\Phi^{-8} - \Phi^{-4} + 1} - \Phi^{-4} + 2} + \sqrt{\Phi^{-4} + 1}\,\bigr)^{1/2}`
- Context before: …h the value $t = \Phi^{-2}$ inserted: $\theta_4\biggl\langle q\bigl\{\tan\bigl[\tfrac{1}{2}\arctan(\Phi^{-6})\bigr]\bigr\}^3 \biggr\rangle = \theta_4\biggl\langle q\bigl\{\tan\bigl[\tfrac{1}{2}\arctan(\Phi^{-6})\bigr]\bigr\} \biggr\rangle \,3^{-1/2} \bigl(\sqrt{2\sqrt{\Phi^{-8} - \Phi^{-4} + 1} - \Phi^{-4} + 2} + \sqrt{\Phi^{-4} + 1}\,\bigr)^{1/2}$
- Context after: The constant $\Phi$ represents the golden ratio number $\Phi = \tfrac{1}{2}(\sqrt{5} + 1)$ exactly. Some series identities. Sums with theta function in the result. The infinite sum of the reciprocals of Fibonacci numbers with odd indices has the identity:…
- Translator read: `theta_4*exp(-3*sqrt(10)*pi)`  =  `sqrt(3)*theta_4*sqrt(sqrt(1 + Phi**(-4)) + sqrt(2*sqrt(1 - 1/Phi**4 + Phi**(-8)) + 2 - 1/Phi**4))*exp(-sqrt(10)*pi)/3`  · notes: pre:size
pre:spacing
sides: \theta_4\bigl[\exp(-3\sqrt{10}\,\pi)\bigr]  ||  \theta_4\bigl[\exp(-\sqrt{10}\,\pi)\bigr] \,3^{-1/2} \bigl(\sqrt{2\sqrt{\Phi^{-8} - \Phi^{-4} + 1} - \Phi^{-4} + 2} + \sqrt{\Phi^{-4} + 1}\,\bigr)^{1/2}
- Assumptions: domains {'Phi': 'positive', 'theta_4': 'real'}; constants {}; constraints ['sqrt(1 + Phi**(-4)) + sqrt(2*sqrt(1 - 1/Phi**4 + Phi**(-8)) + 2 - 1/Phi**4) >= 0', '2*sqrt(1 - 1/Phi**4 + Phi**(-8)) + 2 - 1/Phi**4 >= 0', '1 - 1/Phi**4 + Phi**(-8) >= 0']
- Verifier: The identity fails at 59 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at Phi=0.104375, theta_4=0.108341: lhs=1.233622404979, rhs=0.000041079650).
- Counterexample: {'Phi': '0.104375', 'theta_4': '0.108341'} → lhs 1.23362240497944982237622098629934952604, rhs 0.00004107965083816093357618890383332552, rel diff 0.9999999996
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 11/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:449745:1370749078:196

- Page: [Theta function](https://en.wikipedia.org/wiki/Theta_function) › Derivation of the theta values > Identity of the Euler beta function  · verdict **FAIL**, symbolic unknown
- LaTeX: `\frac{4^{-1/(n + 2)}}{n + 2}\csc\bigl(\frac{\pi}{n + 2}\bigr)\beta\biggl[\frac{n}{2(n + 2)}\biggr] = \int_0^\infty \frac{1}{\sqrt{x^{n+2} + 1}} \,\mathrm {d}x`
- Context before: …values. Identity of the Euler beta function. In the following, three important theta function values are to be derived as examples: This is how the Euler beta function is defined in its reduced form: $\beta(x) = \frac{\Gamma(x)^2}{\Gamma(2x)}$ In general, for all natural numbers $n \isin \mathbb{N}$ this formula of the Euler beta function is valid:
- Context after: Exemplary elliptic integrals. In the following some Elliptic Integral Singular Values are derived: The ensuing function has the following lemniscatically elliptic antiderivative: $\frac{1}{\sqrt{x^4 + 1}} = \frac{\mathrm{d}}{\mathrm{d}x}\,\frac{1}{2} F\biggl[2\arctan(x); \frac{1}{2}\sqrt{2}\,\biggr]$ For the value $n = 2$ this identity appears:…
- Translator read: `beta*n*csc(pi/(n + 2))/(4**(1/(n + 2))*(n + 2)*(2*n + 4))`  =  `Integral(1/sqrt(x**(n + 2) + 1), (x, 0, oo))`  · notes: pre:size
pre:spacing
sides: \frac{4^{-1/(n + 2)}}{n + 2}\csc\bigl(\frac{\pi}{n + 2}\bigr)\beta\biggl[\frac{n}{2(n + 2)}\biggr]  ||  \int_0^\infty \frac{1}{\sqrt{x^{n+2} + 1}} \,\mathrm {d}x
- Assumptions: domains {'beta': 'real', 'n': 'positive_integer'}; constants {}; constraints ['Ne(sin(pi/(n + 2)), 0)']
- Verifier: The identity fails at 30 of 30 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at beta=0.920797, n=1: lhs=0.037211235949, rhs=2.804364210650).
- Counterexample: {'beta': '0.920797', 'n': '1'} → lhs 0.03721123594932789456421867344178272031, rhs 2.80436421065090852235003815810058821923, rel diff 0.9867309546
- Regimes: small_positive 6/6 fail, 0 err, unit_interval 6/6 fail, 0 err, integers_small 6/6 fail, 0 err, mixed_sign 6/6 fail, 0 err, large 6/10 fail, 4 err

---
## wiki:en:67654308:1380646758:16

- Page: [Tides in marginal seas](https://en.wikipedia.org/wiki/Tides_in_marginal_seas) › Tides on the continental shelf  · verdict **FAIL**, symbolic not_equal
- LaTeX: `h2<h1`
- Context before: …ave: $c_p = c_g = \sqrt{gh}$ . The wave energy is transmitted by the group velocity of a wave and thus the energy flux ( $F_E$ ) is given by: $F_E = \frac{1}{2}\rho g A^2 \sqrt{gh}$ The energy flux needs to be conserved and with $\rho$ and $g$ constant, this leads to: $F_{E,1}=F_{E,2}\Longrightarrow{A_1}^{2}\sqrt{gh_1} = {A_2}^{2}\sqrt{gh_2}$ where
- Context after: and thus $A_2 > A_1$ . When the tidal wave propagates onto the continental shelf, the water depth $(h)$ decreases. In order to conserve the energy flux, the amplitude of the wave needs to increase (see figure 1). Transmission coefficient. The above explanation is a simplification as not all tidal wave energy is transmitted, but it is partly reflect…
- Translator read: `2*h`  <  `h`  · notes: sides: h2  ||  h1
- Assumptions: domains {'h': 'positive'}; constants {}; constraints []
- Verifier: The inequality fails at 60 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at h=0.00320992: lhs=0.006419840000, rhs=0.003209920000).
- Counterexample: {'h': '0.00320992'} → lhs 0.00641984000000000000000000000000000000, rhs 0.00320992000000000000000000000000000000, rel diff 0.5000000000
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:53941:1379202452:38

- Page: [Triangle inequality](https://en.wikipedia.org/wiki/Triangle_inequality) › Normed vector space > Example norms  · verdict **FAIL**, symbolic unknown
- LaTeX: `|u + v| = |u| - |v| < |u| + |v|.`
- Context before: …Example norms. The absolute value is a norm for the real line; as required, the absolute value satisfies the triangle inequality for any real numbers u and v. If u and v have the same sign or either of them is zero, then $|u + v| = |u|+|v|.$ If u and v have opposite signs, then without loss of generality assume $|u| \ge |v|.$ Then
- Context after: Combining these cases: $|u + v| \leq |u|+|v|.$ The triangle inequality is useful in mathematical analysis for determining the best upper estimate on the size of the sum of two numbers, in terms of the sizes of the individual numbers. There is also a lower estimate, which can be found using the reverse triangle inequality which states that for any r…
- Translator read (piece 0): `Abs(u + v)`  =  `Abs(u) - Abs(v)`  · notes: pre:trailing_punct
sides: |u + v|  ||  |u| - |v|
- Translator read (piece 1): `Abs(u) - Abs(v)`  <  `Abs(u) + Abs(v)`  · notes: pre:trailing_punct
sides: |u| - |v|  ||  |u| + |v|
- Assumptions: domains {'u': 'positive', 'v': 'positive'}; constants {}; constraints ['Abs(u) >= Abs(v)']
- Verifier: Chain link 0: The identity fails at 60 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at u=0.0700566, v=0.0688275: lhs=0.138884100000, rhs=0.001229100000).
- Counterexample: {'u': '0.0700566', 'v': '0.0688275'} → lhs 0.13888410000000000000000000000000000000, rhs 0.00122910000000000000000000000000000000, rel diff 0.9911501748
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:30367:1378578661:154

- Page: [Trigonometric functions](https://en.wikipedia.org/wiki/Trigonometric_functions) › Definitions in analysis > Euler's formula and the exponential function  · verdict **FAIL**, symbolic unknown
- LaTeX: `e(t) = \exp(2\pi i t)`
- Context before: …. The set $U$ of complex numbers of unit modulus is a compact and connected topological group, which has a neighborhood of the identity that is homeomorphic to the real line. Therefore, it is isomorphic as a topological group to the one-dimensional torus group $\mathbb R/\mathbb Z$ , via an isomorphism $e:\mathbb R/\mathbb Z\to U.$ In simple terms,
- Context after: , and this isomorphism is unique up to taking complex conjugates. For a nonzero real number $a$ (the base), the function $t\mapsto e(t/a)$ defines an isomorphism of the group $\R/a\Z \to U$ . The real and imaginary parts of $e(t/a)$ are the cosine and sine, where $a$ is used as the base for measuring angles. For example, when $a=2\pi$ , we get the…
- Translator read: `e*t`  =  `exp(2*pi*i*t)`  · notes: hint:e_not_only_exp_base
hint:i_present
sides: e(t)  ||  \exp(2\pi i t)
- Assumptions: domains {'t': 'real'}; constants {'e': 'E', 'i': 'I'}; constraints []
- Verifier: The identity fails at 60 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at t=0: lhs=0, rhs=1.000000000000).
- Counterexample: {'t': '0'} → lhs 0, rhs 1.00000000000000000000000000000000000000, rel diff 1.0000000000
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:245560:1361311731:26

- Page: [Trigonometric integral](https://en.wikipedia.org/wiki/Trigonometric_integral) › Hyperbolic sine integral  · verdict **FAIL**, symbolic unknown
- LaTeX: `\operatorname{Si}(ix) = i\operatorname{Shi}(x).`
- Context before: …vative of $\textstyle \frac{\cos x}{x}$ (which vanishes as $x \to \infty$ ). The two definitions are related by $\operatorname{Ci}(x) = \gamma + \ln x - \operatorname{Cin}(x).$ Hyperbolic sine integral. The hyperbolic sine integral is defined as $\operatorname{Shi}(x) =\int_0^x \frac {\sinh t}{t}\,dt.$ It is related to the ordinary sine integral by
- Context after: Hyperbolic cosine integral. The hyperbolic cosine integral is $\operatorname{Chi}(x) = \gamma+\ln x + \int_0^x\frac{\cosh(t) - 1}{t}\,dt \qquad ~ \text{ for } ~ \left| \operatorname{Arg}(x) \right| < \pi~,$ where $\gamma$ is the Euler–Mascheroni constant. It has the series expansion…
- Translator read: `Si(i*x)`  =  `i*Shi(x)`  · notes: pre:trailing_punct
hint:i_present
sides: \operatorname{Si}(ix)  ||  i\operatorname{Shi}(x)
- Assumptions: domains {'i': 'nonneg_integer', 'x': 'real'}; constants {}; constraints []
- Verifier: The identity fails at 54 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at i=1, x=0.0503455: lhs=0.050338411139, rhs=0.050352589938).
- Counterexample: {'i': '1', 'x': '0.0503455'} → lhs 0.05033841113923419343894430134144139278, rhs 0.05035258993892288263449804622074216989, rel diff 0.0002815902
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 9/12 fail, 0 err, integers_small 9/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:32339:1378526249:50

- Page: [Uniform space](https://en.wikipedia.org/wiki/Uniform_space) › Definition > Entourage definition  · verdict **FAIL**, symbolic unknown
- LaTeX: `U^{-1} = U`
- Context before: …the different $U[x]$ 's form the vertical cross-sections. If $(x, y) \in U$ then one says that $x$ and $y$ are . Similarly, if all pairs of points in a subset $A$ of $X$ are $U$ -close (that is, if $A \times A$ is contained in $U$ ), $A$ is called $U$ -small. An entourage $U$ is if $(x, y) \in U$ precisely when $(y, x) \in U$ , or equivalently, if
- Context after: . The first axiom states that each point is $U$ -close to itself for each entourage $U.$ The third axiom guarantees that being "both $U$ -close and $V$ -close" is also a closeness relation in the uniformity. The fourth axiom states that for each entourage $U$ there is an entourage $V$ that is "not more than half as large". Finally, the last axiom s…
- Translator read: `1/U`  =  `U`  · notes: sides: U^{-1}  ||  U
- Assumptions: domains {'U': 'positive'}; constants {}; constraints []
- Verifier: The identity fails at 59 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at U=0.023675: lhs=42.23864836325, rhs=0.023675000000).
- Counterexample: {'U': '0.023675'} → lhs 42.2386483632523759239704329461457233368, rhs 0.02367500000000000000000000000000000000, rel diff 0.9994394943
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 11/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:491316:1379550108:52

- Page: [Unit fraction](https://en.wikipedia.org/wiki/Unit_fraction) › Combinations > Adjacency and Ford circles  · verdict **FAIL**, symbolic unknown
- LaTeX: `\left|\frac{a}{b}-\frac{c}{d}\right|=\frac{|ad-bc|}{bd}=\frac{1}{bd}.`
- Context before: …= \frac1{F_{i+j-1}},$ where $F_i$ denotes the $i$ th Fibonacci number. He calls this matrix the Filbert matrix and it has the same property of having an integer inverse. Adjacency and Ford circles. Two fractions $a/b$ and $c/d$ (in lowest terms) are called adjacent if $ad-bc=\pm1,$ which implies that they differ from each other by a unit fraction:
- Context after: For instance, $\tfrac12$ and $\tfrac35$ are adjacent: $1\cdot 5-2\cdot 3=-1$ and $\tfrac35-\tfrac12=\tfrac1{10}$ . However, some pairs of fractions whose difference is a unit fraction are not adjacent in this sense: for instance, $\tfrac13$ and $\tfrac23$ differ by a unit fraction, but are not adjacent, because for them $ad-bc=3$ . This terminology…
- Translator read (piece 0): `Abs(a/b - c/d)`  =  `Abs(a*d - b*c)/(b*d)`  · notes: pre:left_right
pre:trailing_punct
sides: |\frac{a}{b}-\frac{c}{d}\right|  ||  \frac{|ad-bc|}{bd}
- Translator read (piece 1): `Abs(a*d - b*c)/(b*d)`  =  `1/(b*d)`  · notes: pre:left_right
pre:trailing_punct
sides: \frac{|ad-bc|}{bd}  ||  \frac{1}{bd}
- Assumptions: domains {'a': 'real', 'b': 'real', 'c': 'real', 'd': 'positive'}; constants {}; constraints ['Ne(b, 0)']
- Verifier: Chain link 1: The identity fails at 60 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at a=0.300919, b=0.486014, c=0.578828, d=0.330614: lhs=1.131609693869, rhs=6.223432454839).
- Counterexample: {'a': '0.300919', 'b': '0.486014', 'c': '0.578828', 'd': '0.330614'} → lhs 1.13160969386960922204724705256894055041, rhs 6.22343245483962648225098600690091745273, rel diff 0.8181695226
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:21067650:1377731322:65

- Page: [Volume of an n-ball](https://en.wikipedia.org/wiki/Volume_of_an_n-ball) › Proofs > The two-dimension recursion formula  · verdict **FAIL**, symbolic not_equal
- LaTeX: `\Gamma\bigl(\tfrac32\bigr) = \tfrac12 \cdot \Gamma\bigl(\tfrac12\bigr) = \tfrac\pi2`
- Context before: …which is the two-dimension recursion formula. The same technique can be used to give an inductive proof of the volume formula. The base cases of the induction are the 0-ball and the 1-ball, which can be checked directly using the facts $\Gamma(1) = 1$ and
- Context after: . The inductive step is similar to the above, but instead of applying proportionality to the volumes of the (n − 2)-balls, the inductive hypothesis is applied instead. The one-dimension recursion formula. The proportionality relation can also be used to prove the recursion formula relating the volumes of an n-ball and an (n − 1)-ball. As in the pro…
- Translator read (piece 0): `sqrt(pi)/2`  =  `sqrt(pi)/2`  · notes: pre:size
sides: \Gamma\bigl(\tfrac32\bigr)  ||  \tfrac12 \cdot \Gamma\bigl(\tfrac12\bigr)
- Translator read (piece 1): `sqrt(pi)/2`  =  `pi/2`  · notes: pre:size
sides: \tfrac12 \cdot \Gamma\bigl(\tfrac12\bigr)  ||  \tfrac\pi2
- Assumptions: domains {}; constants {}; constraints []
- Verifier: Chain link 1: The constant identity does not hold: both sides differ beyond 1e-8 relative error, stably at two working precisions (lhs=0.8862269254527580, rhs=1.5707963267948966).
- Counterexample: {} → lhs 0.88622692545275801364908374167057259139, rhs 1.57079632679489661923132169163975144209, rel diff 0.4358104164
- Regimes: constant 1/1 fail, 0 err

---
## wiki:en:1739001:1362483628:36

- Page: [Wetting](https://en.wikipedia.org/wiki/Wetting) › Ideal solid surfaces > Minimization of energy, three phases > Generalized model for the contact angle of droplets on flat and curved surfaces  · verdict **FAIL**, symbolic unknown
- LaTeX: `\cos(\theta) = \frac{\gamma_\text{SG}-\gamma_\text{SL}}{\gamma_{LG}} + \frac{\kappa}{\gamma_\text{LG}} \frac{1}{a} -\frac{\gamma}{3\gamma_\text{LG}}(2+\cos(\theta)-2\cos^2(\theta)-\cos^3(\theta))`
- Context before: …= \frac{\kappa}{\gamma_\text{LG}}$ and $C = \frac{\gamma}{3\gamma_\text{LG}}$ This equation relates the contact angle $\theta$ , a geometric property of a sessile droplet to the bulk thermodynamics, the energy at the three phase contact boundary, and the curvature of the surface α. For the special case of a sessile droplet on a flat surface (α=0),
- Context after: The first two terms are the modified Young's equation, while the third term is due to the Laplace pressure. This nonlinear equation correctly predicts the sign and magnitude of κ, the flattening of the contact angle at very small scales, and contact angle hysteresis. Computational prediction of wetting. For many surface/adsorbate configurations, su…
- Translator read: `cos(theta)`  =  `-gamma*(-cos(theta)**3 - 2*cos(theta)**2 + cos(theta) + 2)/(3*gamma_LG) + (gamma_SG - gamma_SL)/gamma_LG + kappa/(a*gamma_LG)`  · notes: sides: \cos(\theta)  ||  \frac{\gamma_\text{SG}-\gamma_\text{SL}}{\gamma_{LG}} + \frac{\kappa}{\gamma_\text{LG}} \frac{1}{a} -\frac{\gamma}{3\gamma_\text{LG}}(2+\cos(\theta)-2\cos^2(\theta)-\cos^3(\theta))
- Assumptions: domains {'a': 'real', 'gamma': 'positive', 'gamma_LG': 'positive', 'gamma_SG': 'positive', 'gamma_SL': 'positive', 'kappa': 'positive', 'theta': 'angle'}; constants {}; constraints ['Ne(a, 0)']
- Verifier: The identity fails at 60 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at a=0.0788561, gamma=0.494877, gamma_LG=0.297482, gamma_SG=0.540944, gamma_SL=0.716019, kappa=0.671109, theta=0.621063: lhs=0.813260356574, rhs=27.49187935888).
- Counterexample: {'a': '0.0788561', 'gamma': '0.494877', 'gamma_LG': '0.297482', 'gamma_SG': '0.540944', 'gamma_SL': '0.716019', 'kappa': '0.671109', 'theta': '0.621063'} → lhs 0.81326035657453224751643352374727152558, rhs 27.4918793588811615041063375061954225041, rel diff 0.9704181607
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:28479408:1365260495:54

- Page: [Wirtinger derivatives](https://en.wikipedia.org/wiki/Wirtinger_derivatives) › Basic properties > Linearity  · verdict **FAIL**, symbolic not_equal
- LaTeX: `i=1,\dots,n`
- Context before: …the subset $\Omega$ can be thought of as a domain in the real euclidean space $\R^{2n}$ or in its isomorphic complex counterpart $\Complex^n.$ All the proofs are easy consequences of and and of the corresponding properties of the derivatives (ordinary or partial). Linearity. If $f,g \in C^1(\Omega)$ and $\alpha,\beta$ are complex numbers, then for
- Context after: the following equalities hold $\begin{align} \frac{\partial}{\partial z_i} \left(\alpha f+\beta g\right) &= \alpha\frac{\partial f}{\partial z_i} + \beta\frac{\partial g}{\partial z_i} \\ \frac{\partial}{\partial\bar{z}_i} \left(\alpha f+\beta g\right) &= \alpha\frac{\partial f}{\partial\bar{z}_i} + \beta\frac{\partial g}{\partial\bar{z}_i} \end{al…
- Translator read: `i`  =  `1`  · notes: cond: \dots,n
hint:i_present
sides: i  ||  1
- Assumptions: domains {}; constants {'i': 'I'}; constraints []
- Verifier: The constant identity does not hold: both sides differ beyond 1e-8 relative error, stably at two working precisions (lhs=(0.0 + 1.0j), rhs=1.0000000000000000).
- Counterexample: {} → lhs (0.0 + 1.0j), rhs 1.00000000000000000000000000000000000000, rel diff 1.4142135623
- Regimes: constant 1/1 fail, 0 err

---
## wiki:en:28479408:1365260495:69

- Page: [Wirtinger derivatives](https://en.wikipedia.org/wiki/Wirtinger_derivatives) › Basic properties > Chain rule > Functions of n > 1 complex variables  · verdict **FAIL**, symbolic not_equal
- LaTeX: `i= 1,\dots,n`
- Context before: …Functions of n > 1 complex variables. If $g \in C^1(\Omega',\Omega)$ and $f \in C^1(\Omega,\Omega''),$ then for
- Context after: the following form of the chain rule holds…
- Translator read: `i`  =  `1`  · notes: cond: \dots,n
hint:i_present
sides: i  ||  1
- Assumptions: domains {}; constants {'i': 'I'}; constraints []
- Verifier: The constant identity does not hold: both sides differ beyond 1e-8 relative error, stably at two working precisions (lhs=(0.0 + 1.0j), rhs=1.0000000000000000).
- Counterexample: {} → lhs (0.0 + 1.0j), rhs 1.00000000000000000000000000000000000000, rel diff 1.4142135623
- Regimes: constant 1/1 fail, 0 err
