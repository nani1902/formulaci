# Review batch 009 — 22 items

For each item answer with one JSON line (Finding schema): {"formula_id": ..., "verdict": "FAIL", "review": {"status": "confirmed_error"|"false_positive"|"ambiguous", "reviewer": "<name>", "notes": "<why, one or two sentences>"}, "suggested_fix": "<corrected LaTeX or null>", "evidence": "<independent source or derivation>"}


---
## wiki:en:237770:1339862115:18

- Page: [Negative resistance](https://en.wikipedia.org/wiki/Negative_resistance) › Definitions  · verdict **FAIL**, symbolic unknown
- LaTeX: `\Delta i < 0`
- Context before: …\mathrm{static}} = \frac{i}{v}$ Differential conductance $g_\mathrm{diff} = \frac{1}{r_\mathrm{diff}} = \frac{di}{dv}$ It can be seen that the conductance has the same sign as its corresponding resistance: a negative resistance will have a negative conductance while a positive resistance will have a positive conductance. [multiple image | caption2]
- Context after: Operation. One way in which the different types of resistance can be distinguished is in the directions of current and electric power between a circuit and an electronic component. The illustrations below, with a rectangle representing the component attached to a circuit, summarize how the different types work: The voltage v and current i variables…
- Translator read: `Delta*i`  <  `0`  · notes: hint:i_present
sides: \Delta i  ||  0
- Assumptions: domains {'Delta': 'positive', 'i': 'nonneg_integer'}; constants {}; constraints []
- Verifier: The inequality fails at 56 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at Delta=0.671682, i=1: lhs=0.671682000000, rhs=0).
- Counterexample: {'Delta': '0.671682', 'i': '1'} → lhs 0.67168200000000000000000000000000000000, rhs 0, rel diff 1.0000000000
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 9/12 fail, 0 err, integers_small 11/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:2503693:1372625656:114

- Page: [Nested radical](https://en.wikipedia.org/wiki/Nested_radical) › Infinitely nested radicals > Square roots  · verdict **FAIL**, symbolic unknown
- LaTeX: `x = \sqrt{2+x}.`
- Context before: …t obviously so) to one of the solutions 1, 2, or −3. Infinitely nested radicals. Square roots. Under certain conditions infinitely nested square roots such as $x= \sqrt{2+\sqrt{2+\sqrt{2+\sqrt{2+\cdots}}}}$ represent rational numbers. This rational number can be found by realizing that x also appears under the radical sign, which gives the equation
- Context after: If we solve this equation, we find that (the second solution doesn't apply, under the convention that the positive square root is meant). This approach can also be used to show that generally, if n > 0, then $\sqrt{n+\sqrt{n+\sqrt{n+\sqrt{n+\cdots}}}} = \tfrac{1}{2}\left(1 + \sqrt {1+4n}\right)$ and is the positive root of the equation . For , this…
- Translator read: `x`  =  `sqrt(x + 2)`  · notes: pre:trailing_punct
sides: x  ||  \sqrt{2+x}
- Assumptions: domains {'x': 'real'}; constants {}; constraints ['x + 2 >= 0']
- Verifier: The identity fails at 59 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at x=0: lhs=0, rhs=1.414213562373).
- Counterexample: {'x': '0'} → lhs 0, rhs 1.41421356237309504880168872420969807857, rel diff 1.0000000000
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 11/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:2503693:1372625656:144

- Page: [Nested radical](https://en.wikipedia.org/wiki/Nested_radical) › Infinitely nested radicals > Cube roots  · verdict **FAIL**, symbolic unknown
- LaTeX: `x = \sqrt[3]{6+x}.`
- Context before: …qrt2}{2}\cdot \frac{\sqrt{2+\sqrt2}}2\cdot \frac{\sqrt{2+\sqrt{2+\sqrt2}}}2\cdots.$ Cube roots. In certain cases, infinitely nested cube roots such as $x = \sqrt[3]{6+\sqrt[3]{6+\sqrt[3]{6+\sqrt[3]{6+\cdots}}}}$ can represent rational numbers as well. Again, by realizing that the whole expression appears inside itself, we are left with the equation
- Context after: If we solve this equation, we find that . More generally, we find that $\sqrt[3]{n+\sqrt[3]{n+\sqrt[3]{n+\sqrt[3]{n+\cdots}}}}$ is the positive real root of the equation for all n > 0. For , this root is the plastic ratio ρ, approximately equal to 1.3247. The same procedure also works to get $\sqrt[3]{n-\sqrt[3]{n-\sqrt[3]{n-\sqrt[3]{n-\cdots}}}}$…
- Translator read: `x`  =  `(x + 6)**(1/3)`  · notes: pre:trailing_punct
nth_root
sides: x  ||  \sqrt[3]{6+x}
- Assumptions: domains {'x': 'real'}; constants {}; constraints ['x + 6 >= 0']
- Verifier: The identity fails at 59 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at x=0: lhs=0, rhs=1.817120592832).
- Counterexample: {'x': '0'} → lhs 0, rhs 1.81712059283213965889121175632726050242, rel diff 1.0000000000
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 11/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:2139226:1379889185:3

- Page: [Ordinal arithmetic](https://en.wikipedia.org/wiki/Ordinal_arithmetic) › Cantor normal form > Sums  · verdict **FAIL**, symbolic not_equal
- LaTeX: `(\omega^2 \cdot 2 + \omega \cdot 3 + 4) + (\omega \cdot 5 + 6) = \omega^2 \cdot 2 + \omega \cdot 8 + 6 .`
- Context before: …o ε0 itself). Sums. The Cantor normal form also allows us to compute sums and products of ordinals: to compute the sum, for example, one need merely know (see the properties listed in and ) that , if > β. If one can apply the distributive law on the left and rewrite this as ωβ(c + ), and if < β the expression is already in Cantor normal form). E.g.
- Context after: Products. To compute products, the essential facts are that when is in Cantor normal form and 0 < , then and , if n is a non-zero natural number. E.g. $(\omega^3 \cdot 7 + \omega + 1) \cdot (\omega \cdot 8 + 9) = \omega^4 \cdot 8 + \omega^3 \cdot 63 + \omega + 1 .$ Powers. If ωα ≤ β < ωα+1, then βω = ωα·ω. For example,…
- Translator read: `2*omega**2 + 8*omega + 10`  =  `2*omega**2 + 8*omega + 6`  · notes: pre:trailing_punct
sides: (\omega^2 \cdot 2 + \omega \cdot 3 + 4) + (\omega \cdot 5 + 6)  ||  \omega^2 \cdot 2 + \omega \cdot 8 + 6
- Assumptions: domains {'omega': 'positive'}; constants {}; constraints []
- Verifier: The identity fails at 60 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at omega=0.0694953: lhs=10.56562159344, rhs=6.565621593444).
- Counterexample: {'omega': '0.0694953'} → lhs 10.5656215934441800000000000000000000000, rhs 6.56562159344418000000000000000000000000, rel diff 0.3785863391
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:2139226:1379889185:5

- Page: [Ordinal arithmetic](https://en.wikipedia.org/wiki/Ordinal_arithmetic) › Cantor normal form > Powers  · verdict **FAIL**, symbolic unknown
- LaTeX: `(\omega^\omega \cdot 2 + \omega \cdot 3 + 4)^{(\omega^2 \cdot 5 + 2)} = (\omega^{\omega^3 \cdot 5}) \cdot (\omega^{\omega \cdot 2} \cdot 2 + \omega^{\omega + 1} \cdot 3 + \omega^\omega \cdot 8 + \omega \cdot 3 + 4)`
- Context before: …Products. To compute products, the essential facts are that when is in Cantor normal form and 0 < , then and , if n is a non-zero natural number. E.g. $(\omega^3 \cdot 7 + \omega + 1) \cdot (\omega \cdot 8 + 9) = \omega^4 \cdot 8 + \omega^3 \cdot 63 + \omega + 1 .$ Powers. If ωα ≤ β < ωα+1, then βω = ωα·ω. For example,
- Context after: $= \omega^{\omega^3 \cdot 5 + \omega \cdot 2} \cdot 2 + \omega^{\omega^3 \cdot 5 + \omega + 1} \cdot 3 + \omega^{\omega^3 \cdot 5 + \omega} \cdot 8 + \omega^{\omega^3 \cdot 5 + 1} \cdot 3 + \omega^{\omega^3 \cdot 5} \cdot 4$ Variations. A variation of Cantor normal form is to set all the numbers ci equal to 1 and allow the exponents to be equal. In…
- Translator read: `(3*omega + 2*omega**omega + 4)**(5*omega**2 + 2)`  =  `omega**(5*omega**3)*(3*omega + 2*omega**(2*omega) + 8*omega**omega + 3*omega**(omega + 1) + 4)`  · notes: sides: (\omega^\omega \cdot 2 + \omega \cdot 3 + 4)^{(\omega^2 \cdot 5 + 2)}  ||  (\omega^{\omega^3 \cdot 5}) \cdot (\omega^{\omega \cdot 2} \cdot 2 + \omega^{\omega + 1} \cdot 3 + \omega^\omega \cdot 8 + \omega \cdot 3 + 4)
- Assumptions: domains {'omega': 'positive'}; constants {}; constraints []
- Verifier: The identity fails at 60 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at omega=0.0425285: lhs=35.08793180928, rhs=12.74729731472).
- Counterexample: {'omega': '0.0425285'} → lhs 35.0879318092807893250193817417164305291, rhs 12.7472973147279701271249470321104985374, rel diff 0.6367042268
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:26547932:1376378571:234

- Page: [Ordinal number](https://en.wikipedia.org/wiki/Ordinal_number) › Transfinite induction > Indexing classes of ordinals  · verdict **FAIL**, symbolic unknown
- LaTeX: `\omega^\alpha = \alpha`
- Context before: …additively indecomposable ordinals (meaning a nonzero ordinal that is not the sum of two strictly smaller ordinals): the $\gamma$ -th additively indecomposable ordinal is indexed as $\omega^\gamma$ . The technique of indexing classes of ordinals is often useful in the context of fixed points: for example, the $\gamma$ -th ordinal $\alpha$ such that
- Context after: is written $\varepsilon_\gamma$ . These are called the "epsilon numbers". Arithmetic of ordinals. There are three usual operations on ordinals: addition, multiplication, and exponentiation. Each can be defined in essentially two different ways: either by constructing an explicit well-ordered set that represents the operation or by using transfinite…
- Translator read: `omega**alpha`  =  `alpha`  · notes: sides: \omega^\alpha  ||  \alpha
- Assumptions: domains {'alpha': 'real', 'omega': 'positive'}; constants {}; constraints []
- Verifier: The identity fails at 60 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at alpha=-0.216987, omega=0.218918: lhs=1.390433888968, rhs=-0.21698700000).
- Counterexample: {'alpha': '-0.216987', 'omega': '0.218918'} → lhs 1.39043388896876936542729874093916781608, rhs -0.2169870000000000000000000000000000000, rel diff 1.1560570421
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:26547932:1376378571:313

- Page: [Ordinal number](https://en.wikipedia.org/wiki/Ordinal_number) › Some "large" countable ordinals  · verdict **FAIL**, symbolic unknown
- LaTeX: `\omega^\alpha = \alpha`
- Context before: …f limit cardinals, and the class of fixed points of the $\aleph$ -function. In contrast, the class of regular cardinals is unbounded but not closed. A class is stationary if it intersects every closed unbounded class. Some "large" countable ordinals. As mentioned above (see Cantor normal form), the ordinal ε0 is the smallest satisfying the equation
- Context after: , so it is the limit of the sequence 0, 1, $\omega$ , $\omega^\omega$ , $\omega^{\omega^\omega}$ , etc. Many ordinals can be defined in such a manner as fixed points of certain ordinal functions (the $\iota$ -th ordinal such that $\omega^\alpha = \alpha$ is called $\varepsilon_\iota$ , then one could go on trying to find the $\iota$ -th ordinal suc…
- Translator read: `omega**alpha`  =  `alpha`  · notes: sides: \omega^\alpha  ||  \alpha
- Assumptions: domains {'alpha': 'real', 'omega': 'positive'}; constants {}; constraints []
- Verifier: The identity fails at 60 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at alpha=0.0761405, omega=0.199362: lhs=0.884452310445, rhs=0.076140500000).
- Counterexample: {'alpha': '0.0761405', 'omega': '0.199362'} → lhs 0.88445231044591525848085819998177117183, rhs 0.07614050000000000000000000000000000000, rel diff 0.9139122606
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:1651906:1377507472:131

- Page: [Ordinary least squares](https://en.wikipedia.org/wiki/Ordinary_least_squares) › Properties > Violations of assumptions > Constrained estimation  · verdict **FAIL**, symbolic unknown
- LaTeX: `\hat\beta^c = \hat\beta - (X ^\operatorname{T} X)^{-1}Q\Big(Q ^\operatorname{T} (X ^\operatorname{T} X)^{-1}Q\Big)^{-1}(Q ^\operatorname{T} \hat\beta - c).`
- Context before: …ad Q ^\operatorname{T} \beta = c, \,$ where Q is a p×q matrix of full rank, and c is a q×1 vector of known constants, where q < p. In this case least squares estimation is equivalent to minimizing the sum of squared residuals of the model subject to the constraint A. The constrained least squares (CLS) estimator can be given by an explicit formula:
- Context after: This expression for the constrained estimator is valid as long as the matrix XTX is invertible. It was assumed from the beginning of this article that this matrix is of full rank, and it was noted that when the rank condition fails, β will not be identifiable. However it may happen that adding the restriction A makes β identifiable, in which case o…
- Translator read: `beta_hat**c`  =  `beta_hat - (Q**T*beta_hat - c)/Q**T`  · notes: pre:size
pre:trailing_punct
mult_not_call:Q
sides: \hat\beta^c  ||  \hat\beta - (X ^\operatorname{T} X)^{-1}Q\Big(Q ^\operatorname{T} (X ^\operatorname{T} X)^{-1}Q\Big)^{-1}(Q ^\operatorname{T} \hat\beta - c)
- Assumptions: domains {'Q': 'positive', 'T': 'positive', 'beta_hat': 'real', 'c': 'real'}; constants {}; constraints ['beta_hat > 0']
- Verifier: The identity fails at 60 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at Q=0.319107, T=0.345074, beta_hat=0.0669004, c=0.102727: lhs=0.757425313850, rhs=0.152357304249).
- Counterexample: {'Q': '0.319107', 'T': '0.345074', 'beta_hat': '0.0669004', 'c': '0.102727'} → lhs 0.75742531385018948045777454074652708528, rhs 0.15235730424935904494148791813761412898, rel diff 0.7988484125
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/19 fail, 7 err

---
## wiki:en:23231:1380256968:459

- Page: [Parabola](https://en.wikipedia.org/wiki/Parabola) › Generalizations  · verdict **FAIL**, symbolic not_equal
- LaTeX: `1 + 1 = 0`
- Context before: …ométrie (1637). Generalizations. If one replaces the real numbers by an arbitrary field, many geometric properties of the parabola $y = x^2$ are still valid: A line intersects in at most two points. At any point $(x_0, x_0^2)$ the line $y = 2 x_0 x - x_0^2$ is the tangent. Essentially new phenomena arise, if the field has characteristic 2 (that is,
- Context after: ): the tangents are all parallel. In algebraic geometry, the parabola is generalized by the rational normal curves, which have coordinates (x, x2, x3, ..., xn); the standard parabola is the case , and the case is known as the twisted cubic. A further generalization is given by the Veronese variety, when there is more than one input variable. In the…
- Translator read: `2`  =  `0`  · notes: sides: 1 + 1  ||  0
- Assumptions: domains {}; constants {}; constraints []
- Verifier: The constant identity does not hold: both sides differ beyond 1e-8 relative error, stably at two working precisions (lhs=2.0000000000000000, rhs=0).
- Counterexample: {} → lhs 2.00000000000000000000000000000000000000, rhs 0, rel diff 1.0000000000
- Regimes: constant 1/1 fail, 0 err

---
## wiki:en:53057:1357600136:172

- Page: [Pareto distribution](https://en.wikipedia.org/wiki/Pareto_distribution) › Occurrence and applications > Lorenz curve and Gini coefficient  · verdict **FAIL**, symbolic unknown
- LaTeX: `1-(1/2)^{1-\frac{1}{\alpha}}=\varepsilon^{1-\frac{1}{\alpha}}`
- Context before: …the Lorenz curve for a number of Pareto distributions are shown in the graph on the right. According to Oxfam (2016) the richest 62 people have as much wealth as the poorest half of the world's population. We can estimate the Pareto index that would apply to this situation. Letting ε equal $62/(7\times 10^9)$ we have: $L(1/2)=1-L(1-\varepsilon)$ or
- Context after: The solution is that α equals about 1.15, and about 9% of the wealth is owned by each of the two groups. But actually the poorest 69% of the world adult population owns only about 3% of the wealth. The Gini coefficient is a measure of the deviation of the Lorenz curve from the equidistribution line which is a line connecting [0, 0] and [1, 1], whic…
- Translator read: `1 - 2**(-1 + 1/alpha)`  =  `epsilon**(1 - 1/alpha)`  · notes: sides: 1-(1/2)^{1-\frac{1}{\alpha}}  ||  \varepsilon^{1-\frac{1}{\alpha}}
- Assumptions: domains {'alpha': 'real', 'epsilon': 'positive'}; constants {}; constraints ['Ne(alpha, 0)']
- Verifier: The identity fails at 60 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at alpha=0.121715, epsilon=0.0429987: lhs=-147.664278721, rhs=7258872306.660).
- Counterexample: {'alpha': '0.121715', 'epsilon': '0.0429987'} → lhs -147.66427872188806138385095960841561690, rhs 7258872306.66084900758382830524438309695, rel diff 1.0000000203
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:1396948:1381178057:194

- Page: [Particle filter](https://en.wikipedia.org/wiki/Particle_filter) › Sequential Importance Resampling (SIR) > Monte Carlo filter and bootstrap filter  · verdict **FAIL**, symbolic unknown
- LaTeX: `\sum_{i=1}^N w^{(i)}_k = 1.`
- Context before: …lied filtering algorithms, which approximate the filtering probability density $p(x_k|y_0,\cdots,y_k)$ by a weighted set of N samples $\left \{ \left (w^{(i)}_k,x^{(i)}_k \right ) \ : \ i\in\{1,\cdots,N\} \right \}.$ The importance weights $w^{(i)}_k$ are approximations to the relative posterior probabilities (or densities) of the samples such that
- Context after: Sequential importance sampling (SIS) is a sequential (i.e., recursive) version of importance sampling. As in importance sampling, the expectation of a function f can be approximated as a weighted average $\int f(x_k) p(x_k|y_0,\dots,y_k) dx_k \approx \sum_{i=1}^N w_k^{(i)} f(x_k^{(i)}).$ For a finite set of samples, the algorithm performance is dep…
- Translator read: `Sum(w_k**i, (i, 1, N))`  =  `1`  · notes: pre:trailing_punct
sides: \sum_{i=1}^N w^{(i)}_k  ||  1
- Assumptions: domains {'N': 'nonneg_integer', 'w_k': 'complex'}; constants {}; constraints []
- Verifier: The identity fails at 72 of 72 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, complex, large) (e.g. at N=0, w_k=0.123806: lhs=0, rhs=1.000000000000).
- Counterexample: {'N': '0', 'w_k': '0.123806'} → lhs 0, rhs 1.00000000000000000000000000000000000000, rel diff 1.0000000000
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, complex 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:24048:1375453918:44

- Page: [Particle in a box](https://en.wikipedia.org/wiki/Particle_in_a_box) › One-dimensional solution > Momentum wave function  · verdict **FAIL**, symbolic unknown
- LaTeX: `{\rm sinc}(x) = \sin(x)/x`
- Context before: …where the sinc function,
- Context after: . Note that the variable, $k = p/\hbar \in\R$ , that is often used to describe momentum wave functions, as a function of the wave vector, $k$ , is not the special kn from the boundary conditions, which is linked to the energy eigenvalues. For the centered box, , at time, $t=0$ , the solution is the product of a strictly real-valued function, and a…
- Translator read: `c*i*n*s*x`  =  `sin(x)/x`  · notes: hint:i_present
sides: {\rm sinc}(x)  ||  \sin(x)/x
- Assumptions: domains {'c': 'real', 'n': 'nonneg_integer', 's': 'complex', 'x': 'real'}; constants {'i': 'I'}; constraints ['Ne(x, 0)']
- Verifier: The identity fails at 72 of 72 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, complex, large) (e.g. at c=0.212573, n=0, s=0.773119, x=0.045581: lhs=0, rhs=0.999653764709).
- Counterexample: {'c': '0.212573', 'n': '0', 's': '0.773119', 'x': '0.045581'} → lhs 0, rhs 0.99965376470918967411856907800367803067, rel diff 1.0000000000
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, complex 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:24048:1375453918:49

- Page: [Particle in a box](https://en.wikipedia.org/wiki/Particle_in_a_box) › One-dimensional solution > Momentum wave function  · verdict **FAIL**, symbolic unknown
- LaTeX: `{\rm sinc}(p) = \sin(p)/p`
- Context before: …is often used to describe momentum wave functions, as a function of the wave vector, $k$ , is not the special kn from the boundary conditions, which is linked to the energy eigenvalues. For the centered box, , at time, $t=0$ , the solution is the product of a strictly real-valued function, and a unit modulus complex phase, $i^{n-1}$ . The function,
- Context after: , is an even function of p. It can be seen that the allowed values of the momentum in this wave packet is continuous, and one may conclude that for the energy state described by the wave number kn, the momentum can, when measured, attain other values beyond, $p = \pm \hbar k_n$ . Hence, it also appears that, since the energy is $E_n = \frac{\hbar^2…
- Translator read: `c*i*n*p*s`  =  `sin(p)/p`  · notes: hint:i_present
sides: {\rm sinc}(p)  ||  \sin(p)/p
- Assumptions: domains {'c': 'real', 'n': 'nonneg_integer', 'p': 'positive', 's': 'complex'}; constants {'i': 'I'}; constraints []
- Verifier: The identity fails at 72 of 72 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, complex, large) (e.g. at c=0.476784, n=0, p=0.249408, s=0.359852: lhs=0, rhs=0.989664805384).
- Counterexample: {'c': '0.476784', 'n': '0', 'p': '0.249408', 's': '0.359852'} → lhs 0, rhs 0.98966480538429015541887354646611109656, rel diff 1.0000000000
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, complex 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:312250:1371388914:87

- Page: [Partition function (number theory)](https://en.wikipedia.org/wiki/Partition_function_(number_theory)) › Strict partition function > Identities on strict partition numbers  · verdict **FAIL**, symbolic unknown
- LaTeX: `p(2n+1) = \sum_{k=0}^{n} p(n - k)q(2k + 1)`
- Context before: …fty}^{-1} = (x^2;x^2)_{\infty}^{-1}(x;x^2)_{\infty}^{-1}$ From this identity, using generating functions gives $\biggl[\sum_{n=0}^\infty p(n)x^n\biggr] = \biggl[\sum_{n=0}^\infty p(n)x^{2n}\biggr]\biggl[\sum_{n=0}^\infty q(n)x^n\biggr]$ Upon comparing coefficients, one then obtains the following two relations: $p(2n) = \sum_{k=0}^{n} p(n - k)q(2k)$
- Context after: Here, two examples are accurately executed: $p(8) = \sum_{k=0}^{4} p(4 - k)q(2k) =$ $= p(4)q(0) + p(3)q(2) + p(2)q(4) + p(1)q(6) + p(0)q(8) =$ $= 5\times 1 + 3\times 1 + 2\times 2 + 1\times 4 + 1\times 6 = 22$ $p(9) = \sum_{k=0}^{4} p(4 - k)q(2k + 1) =$ $= p(4)q(1) + p(3)q(3) + p(2)q(5) + p(1)q(7) + p(0)q(9) =$ $= 5\times 1 + 3\times 2 + 2\times 3…
- Translator read: `p*(2*n + 1)`  =  `Sum(p*q*(-k + n)*(2*k + 1), (k, 0, n))`  · notes: sides: p(2n+1)  ||  \sum_{k=0}^{n} p(n - k)q(2k + 1)
- Assumptions: domains {'n': 'nonneg_integer', 'p': 'positive', 'q': 'positive'}; constants {}; constraints []
- Verifier: The identity fails at 60 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at n=0, p=0.456824, q=0.277748: lhs=0.456824000000, rhs=0).
- Counterexample: {'n': '0', 'p': '0.456824', 'q': '0.277748'} → lhs 0.45682400000000000000000000000000000000, rhs 0, rel diff 1.0000000000
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:23670:1378937800:20

- Page: [Perfect number](https://en.wikipedia.org/wiki/Perfect_number) › Even perfect numbers  · verdict **FAIL**, symbolic not_equal
- LaTeX: `2^11 - 1 = 2047 = 23 \times 89`
- Context before: …^p-1$ are known as Mersenne primes, after the seventeenth-century monk Marin Mersenne, who studied number theory and perfect numbers. For $2^p-1$ to be prime, it is necessary that p itself be prime. However, not all numbers of the form $2^p-1$ with a prime p are prime; for example, $2^{11} - 1 = 2047 = 23 \times 89$ is not a prime number. [efn | 1]
- Context after: In fact, Mersenne primes are very rare: of the approximately 4 million primes p up to 68,874,199, $2^p-1$ is prime for only 48 of them. While Nicomachus had stated (without proof) that all perfect numbers were of the form $2^{n-1}(2^n-1)$ where $2^n-1$ is prime (though he stated this somewhat differently), Ibn al-Haytham (Alhazen) circa AD 1000 was…
- Translator read (piece 0): `1`  =  `2047`  · notes: op:times
sides: 2^11 - 1  ||  2047
- Translator read (piece 1): `2047`  =  `2047`  · notes: op:times
sides: 2047  ||  23 \times 89
- Assumptions: domains {}; constants {}; constraints []
- Verifier: Chain link 0: The constant identity does not hold: both sides differ beyond 1e-8 relative error, stably at two working precisions (lhs=1.0000000000000000, rhs=2047.0000000000000).
- Counterexample: {} → lhs 1.00000000000000000000000000000000000000, rhs 2047.00000000000000000000000000000000000, rel diff 0.9995114802
- Regimes: constant 1/1 fail, 0 err

---
## wiki:en:44027:1380025724:112

- Page: [Permutation](https://en.wikipedia.org/wiki/Permutation) › Properties > Parity of a permutation  · verdict **FAIL**, symbolic not_equal
- LaTeX: `\operatorname{sgn}\sigma = -1`
- Context before: …they all contain an even number of transpositions or they all contain an odd number of transpositions. Thus all permutations can be classified as even or odd depending on this number. This result can be extended so as to assign a sign, written $\operatorname{sgn}\sigma$ , to each permutation. $\operatorname{sgn}\sigma = +1$ if $\sigma$ is even and
- Context after: if $\sigma$ is odd. Then for two permutations $\sigma$ and $\pi$ $\operatorname{sgn}(\sigma\pi) = \operatorname{sgn}\sigma\cdot\operatorname{sgn}\pi.$ It follows that $\operatorname{sgn}\left(\sigma\sigma^{-1}\right) = +1.$ The sign of a permutation is equal to the determinant of its permutation matrix (below). Matrix representation. A permutation…
- Translator read: `sign(sigma)`  =  `-1`  · notes: sides: \operatorname{sgn}\sigma  ||  -1
- Assumptions: domains {'sigma': 'positive'}; constants {}; constraints []
- Verifier: The identity fails at 60 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at sigma=0.0232814: lhs=1.000000000000, rhs=-1.00000000000).
- Counterexample: {'sigma': '0.0232814'} → lhs 1.00000000000000000000000000000000000000, rhs -1.0000000000000000000000000000000000000, rel diff 2.0000000000
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:23601:1380390825:53

- Page: [Pi](https://en.wikipedia.org/wiki/Pi) › Modern quest for more digits > Rapidly convergent series  · verdict **FAIL**, symbolic unknown
- LaTeX: `\pi^k = \sum_{n=1}^\infty \frac{1}{n^k} \left(\frac{a}{q^n-1} + \frac{b}{q^{2n}-1} + \frac{c}{q^{4n}-1}\right),`
- Context before: …sky brothers, 10 trillion (1013) digits in 2011 by Alexander Yee and Shigeru Kondo, and 100 trillion digits by Emma Haruka Iwao in 2022. For similar formulae, see also the Ramanujan–Sato series. In 2006, mathematician Simon Plouffe used the PSLQ integer relation algorithm to generate several new formulae for π, conforming to the following template:
- Context after: where q is eπ (Gelfond's constant), k is an odd number, and a, b, c are certain rational numbers that Plouffe computed. Monte Carlo methods. Monte Carlo methods, which evaluate the results of multiple random trials, can be used to create approximations of π. Buffon's needle is one such technique: If a needle of length ℓ is dropped n times on a surf…
- Translator read: `pi**k`  =  `Sum((a/(q**n - 1) + b/(q**(2*n) - 1) + c/(q**(4*n) - 1))/n**k, (n, 1, oo))`  · notes: pre:left_right
pre:trailing_punct
sides: \pi^k  ||  \sum_{n=1}^\infty \frac{1}{n^k} \left(\frac{a}{q^n-1} + \frac{b}{q^{2n}-1} + \frac{c}{q^{4n}-1}\right)
- Assumptions: domains {'a': 'real', 'b': 'real', 'c': 'real', 'k': 'integer', 'q': 'positive'}; constants {}; constraints ['Eq(Mod(k, 2), 1)']
- Verifier: The identity fails at 28 of 28 evaluable points, a clear majority in every regime (small_positive, integers_small, mixed_sign, large) (e.g. at a=0.168703, b=0.481193, c=1.04653, k=1, q=1.164: lhs=3.141592653589, rhs=4.968279735732) [symbolic check timed out].
- Counterexample: {'a': '0.168703', 'b': '0.481193', 'c': '1.04653', 'k': '1', 'q': '1.164'} → lhs 3.14159265358979323846264338327950288419, rhs 4.96827973573278056219757644397080337198, rel diff 0.3676699339
- Regimes: small_positive 6/7 fail, 1 err, unit_interval 4/12 fail, 8 err, integers_small 6/7 fail, 1 err, mixed_sign 6/6 fail, 0 err, large 6/6 fail, 0 err

---
## wiki:en:882902:1377844797:135

- Page: [Poisson manifold](https://en.wikipedia.org/wiki/Poisson_manifold) › Examples > Trivial Poisson structures  · verdict **FAIL**, symbolic not_equal
- LaTeX: `\pi=0`
- Context before: …f $\pi$ is maximal (e.g. the Poisson structure is nondegenerate, so that $n = 2k$ ), one recovers the classical Darboux theorem for symplectic structures. Examples. Trivial Poisson structures. Every manifold $M$ carries the trivial Poisson structure $\{ f,g \} = 0 \quad \forall f,g \in \mathcal{C}^\infty (M),$ equivalently described by the bivector
- Context after: . Every point of $M$ is therefore a zero-dimensional symplectic leaf. Nondegenerate Poisson structures. A bivector field $\pi$ is called nondegenerate if $\pi^{\sharp}: T^{*} M \to T M$ is a vector bundle isomorphism. Nondegenerate Poisson bivector fields are actually the same thing as symplectic manifolds $(M,\omega)$ . Indeed, there is a bijectiv…
- Translator read: `pi`  =  `0`  · notes: sides: \pi  ||  0
- Assumptions: domains {}; constants {}; constraints []
- Verifier: The constant identity does not hold: both sides differ beyond 1e-8 relative error, stably at two working precisions (lhs=3.1415926535897932, rhs=0).
- Counterexample: {} → lhs 3.14159265358979323846264338327950288419, rhs 0, rel diff 1.0000000000
- Regimes: constant 1/1 fail, 0 err

---
## wiki:en:482471:1380575185:154

- Page: [Polylogarithm](https://en.wikipedia.org/wiki/Polylogarithm) › Polylogarithm ladders  · verdict **FAIL**, symbolic unknown
- LaTeX: `\operatorname{Li}_2(\rho) = \tfrac{1}{10} \pi^2 - \ln^2\rho`
- Context before: …ecial values. These are now called polylogarithm ladders. Define $\rho = \tfrac{1}{2} (\sqrt{5}-1)$ as the reciprocal of the golden ratio. Then two simple examples of dilogarithm ladders are $\operatorname{Li}_2(\rho^6) = 4 \operatorname{Li}_2(\rho^3) + 3 \operatorname{Li}_2(\rho^2) - 6 \operatorname{Li}_2(\rho) + \tfrac {7}{30} \pi^2$ given by and
- Context after: given by Landen. Polylogarithm ladders occur naturally and deeply in K-theory and algebraic geometry. Polylogarithm ladders provide the basis for the rapid computations of various mathematical constants by means of the BBP algorithm . Monodromy. The polylogarithm has two branch points; one at z = 1 and another at z = 0. The second branch point, at…
- Translator read: `polylog(2, rho)`  =  `-log(rho)**2 + pi**2/10`  · notes: sides: \operatorname{Li}_2(\rho)  ||  \tfrac{1}{10} \pi^2 - \ln^2\rho
- Assumptions: domains {'rho': 'positive'}; constants {}; constraints []
- Verifier: The identity fails at 35 of 35 evaluable points, a clear majority in every regime (small_positive, unit_interval, mixed_sign) (e.g. at rho=0.00462672: lhs=0.004632082667, rhs=-27.9134165492).
- Counterexample: {'rho': '0.00462672'} → lhs 0.00463208266788770467779576214180707042, rhs -27.913416549245177681612663421983888172, rel diff 1.0001659446
- Regimes: small_positive 12/22 fail, 10 err, unit_interval 12/12 fail, 0 err, integers_small 1/12 fail, 11 err, mixed_sign 10/40 fail, 30 err, large 0/40 fail, 40 err

---
## wiki:en:482471:1380575185:153

- Page: [Polylogarithm](https://en.wikipedia.org/wiki/Polylogarithm) › Polylogarithm ladders  · verdict **FAIL**, symbolic unknown
- LaTeX: `\operatorname{Li}_2(\rho^6) = 4 \operatorname{Li}_2(\rho^3) + 3 \operatorname{Li}_2(\rho^2) - 6 \operatorname{Li}_2(\rho) + \tfrac {7}{30} \pi^2`
- Context before: …ratio. Polylogarithm ladders. Leonard Lewin discovered a remarkable and broad generalization of a number of classical relationships on the polylogarithm for special values. These are now called polylogarithm ladders. Define $\rho = \tfrac{1}{2} (\sqrt{5}-1)$ as the reciprocal of the golden ratio. Then two simple examples of dilogarithm ladders are
- Context after: given by and $\operatorname{Li}_2(\rho) = \tfrac{1}{10} \pi^2 - \ln^2\rho$ given by Landen. Polylogarithm ladders occur naturally and deeply in K-theory and algebraic geometry. Polylogarithm ladders provide the basis for the rapid computations of various mathematical constants by means of the BBP algorithm . Monodromy. The polylogarithm has two bra…
- Translator read: `polylog(2, rho**6)`  =  `-6*polylog(2, rho) + 3*polylog(2, rho**2) + 4*polylog(2, rho**3) + 7*pi**2/30`  · notes: sides: \operatorname{Li}_2(\rho^6)  ||  4 \operatorname{Li}_2(\rho^3) + 3 \operatorname{Li}_2(\rho^2) - 6 \operatorname{Li}_2(\rho) + \tfrac {7}{30} \pi^2
- Assumptions: domains {'rho': 'positive'}; constants {}; constraints []
- Verifier: The identity fails at 29 of 29 evaluable points, a clear majority in every regime (small_positive, unit_interval) (e.g. at rho=0.0219558: lhs=0.000000000112, rhs=2.171931345200).
- Counterexample: {'rho': '0.0219558'} → lhs 0.00000000011202000721351666042413554995, rhs 2.17193134520088335636386410879286073642, rel diff 0.9999999999
- Regimes: small_positive 12/20 fail, 8 err, unit_interval 12/12 fail, 0 err, integers_small 1/12 fail, 11 err, mixed_sign 4/40 fail, 36 err, large 0/40 fail, 40 err

---
## wiki:en:24829:1379019090:44

- Page: [Primitive recursive function](https://en.wikipedia.org/wiki/Primitive_recursive_function) › Examples  · verdict **FAIL**, symbolic not_equal
- LaTeX: `C_3^0 = 3`
- Context before: …f vector-valued functions. A (vector-valued) function $f : \mathbb{N}^m \to \mathbb{N}^n$ is primitive recursive if it can be written as $f(x_1, \dots, x_m) = (f_1(x_1, \dots, x_m), \dots, f_n(x_1, \dots, x_m))$ where each component $f_i : \mathbb{N}^m \to \mathbb{N}$ is a (scalar-valued) primitive recursive function. Examples. [unordered list | 3]
- Context after: Addition. A definition of the 2-ary function $\operatorname{Add}$ , to compute the sum of its arguments, can be obtained using the primitive recursion operator $\rho$ . To this end, the well-known equations $\begin{align} 0 + y &= y, \\ S(x) + y &= S(x+y) \end{align}$ are "rephrased in primitive recursive function terminology": In the definition of…
- Translator read: `1`  =  `3`  · notes: sides: C_3^0  ||  3
- Assumptions: domains {}; constants {}; constraints []
- Verifier: The constant identity does not hold: both sides differ beyond 1e-8 relative error, stably at two working precisions (lhs=1.0000000000000000, rhs=3.0000000000000000).
- Counterexample: {} → lhs 1.00000000000000000000000000000000000000, rhs 3.00000000000000000000000000000000000000, rel diff 0.6666666666
- Regimes: constant 1/1 fail, 0 err

---
## wiki:en:26513034:1379898070:22

- Page: [Pythagorean theorem](https://en.wikipedia.org/wiki/Pythagorean_theorem) › Consequences and uses of the theorem > Inverse Pythagorean theorem  · verdict **FAIL**, symbolic unknown
- LaTeX: `\frac1{(xz)^2}+\frac1{(yz)^2} = \frac1{(xy)^2}`
- Context before: …Pythagorean theorem. Given a right triangle with sides $a,b,c$ and altitude d (a line from the right angle and perpendicular to the hypotenuse c). The Pythagorean theorem has, $a^2+b^2 = c^2$ while the inverse Pythagorean theorem relates the two legs a, b to the altitude d, $\frac1{a^2}+\frac1{b^2} = \frac1{d^2}$ The equation can be transformed to:
- Context after: where for any non-zero real x, y , z. If the a, b, d are to be integers, the smallest solution a > b > d is then $\frac1{20^2}+\frac1{15^2} = \frac1{12^2}$ using the smallest Pythagorean triple 3, 4, 5. The reciprocal Pythagorean theorem is a special case of the optic equation $\frac1{p}+\frac1{q} = \frac1{r}$ where the denominators are squares and…
- Translator read: `1/(y**2*z**2) + 1/(x**2*z**2)`  =  `1/(x**2*y**2)`  · notes: sides: \frac1{(xz)^2}+\frac1{(yz)^2}  ||  \frac1{(xy)^2}
- Assumptions: domains {'x': 'real', 'y': 'real', 'z': 'real'}; constants {}; constraints ['Ne(x, 0)', 'Ne(y, 0)', 'Ne(z, 0)']
- Verifier: The identity fails at 60 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at x=0.253471, y=0.255788, z=0.00752678: lhs=544529.0912650, rhs=237.8937931986).
- Counterexample: {'x': '0.253471', 'y': '0.255788', 'z': '0.00752678'} → lhs 544529.091265086929276668062472046176941, rhs 237.893793198617775462531485608951510676, rel diff 0.9995631201
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err
