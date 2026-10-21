# Review batch 010 — 22 items

For each item answer with one JSON line (Finding schema): {"formula_id": ..., "verdict": "FAIL", "review": {"status": "confirmed_error"|"false_positive"|"ambiguous", "reviewer": "<name>", "notes": "<why, one or two sentences>"}, "suggested_fix": "<corrected LaTeX or null>", "evidence": "<independent source or derivation>"}


---
## wiki:en:24172:1380816662:15

- Page: [Pythagorean triple](https://en.wikipedia.org/wiki/Pythagorean_triple) › Generating a triple > Proof of Euclid's formula  · verdict **FAIL**, symbolic unknown
- LaTeX: `\tfrac{(c+a)}{b}=\tfrac{b}{(c-a)}.`
- Context before: …at least one of them is odd. If we suppose that a is odd, then b is even and c is odd (if both a and b were odd, c would be even, and c2 would be a multiple of 4, while a2 + b2 would be congruent to 2 modulo 4, as an odd square is congruent to 1 modulo 4). From $a^2+b^2=c^2,$ assume a is odd. We obtain $c^2-a^2=b^2$ and hence $(c-a)(c+a)=b^2.$ Then
- Context after: Since $\tfrac{(c+a)}{b}$ is rational, we set it equal to $\tfrac{m}{n}$ in lowest terms. Thus $\tfrac{(c-a)}{b}=\tfrac{n}{m},$ being the reciprocal of $\tfrac{(c+a)}{b}.$ Then solving $\frac{c}{b}+\frac{a}{b}=\frac{m}{n}, \quad \quad \frac{c}{b}-\frac{a}{b}=\frac{n}{m}$ for $\tfrac{c}{b}$ and $\tfrac{a}{b}$ gives…
- Translator read: `(a + c)/b`  =  `b/(-a + c)`  · notes: pre:trailing_punct
sides: \tfrac{(c+a)}{b}  ||  \tfrac{b}{(c-a)}
- Assumptions: domains {'a': 'real', 'b': 'real', 'c': 'real'}; constants {}; constraints ['Ne(b, 0)', 'Ne(-a + c, 0)']
- Verifier: The identity fails at 60 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at a=0.0613502, b=0.296237, c=0.0273087: lhs=0.299283681646, rhs=-8.70223110027).
- Counterexample: {'a': '0.0613502', 'b': '0.296237', 'c': '0.0273087'} → lhs 0.29928368164678956376144775973291654992, rhs -8.7022311002746647474406239443032768826, rel diff 1.0343916035
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:25175:1380939644:92

- Page: [Quadratic equation](https://en.wikipedia.org/wiki/Quadratic_equation) › Advanced topics > Generalization of quadratic equation > Characteristic 2  · verdict **FAIL**, symbolic unknown
- LaTeX: `\displaystyle x^{2} + c = (x + \sqrt{c})^{2}.`
- Context before: …e quadratic formula, which relies on 2 being a unit, does not hold. Consider the monic quadratic polynomial $x^{2} + bx + c$ over a field of characteristic 2. If b = 0, then the solution reduces to extracting a square root, so the solution is $x = \sqrt{c}$ and there is only one root since $-\sqrt{c} = -\sqrt{c} + 2\sqrt{c} = \sqrt{c}.$ In summary,
- Context after: See quadratic residue for more information about extracting square roots in finite fields. In the case that b ≠ 0, there are two distinct roots, but if the polynomial is irreducible, they cannot be expressed in terms of square roots of numbers in the coefficient field. Instead, define the 2-root R(c) of c to be a root of the polynomial x2 + x + c,…
- Translator read: `c + x**2`  =  `(sqrt(c) + x)**2`  · notes: pre:style
pre:trailing_punct
sides: x^{2} + c  ||  (x + \sqrt{c})^{2}
- Assumptions: domains {'c': 'real', 'x': 'real'}; constants {}; constraints ['c >= 0']
- Verifier: The identity fails at 59 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at c=0.084956, x=0.103015: lhs=0.095568090225, rhs=0.155620092261).
- Counterexample: {'c': '0.084956', 'x': '0.103015'} → lhs 0.09556809022500000000000000000000000000, rhs 0.15562009226173812572185611828932109430, rel diff 0.3858884875
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 11/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:25175:1380939644:91

- Page: [Quadratic equation](https://en.wikipedia.org/wiki/Quadratic_equation) › Advanced topics > Generalization of quadratic equation > Characteristic 2  · verdict **FAIL**, symbolic unknown
- LaTeX: `-\sqrt{c} = -\sqrt{c} + 2\sqrt{c} = \sqrt{c}.`
- Context before: …field. Characteristic 2. In a field of characteristic 2, the quadratic formula, which relies on 2 being a unit, does not hold. Consider the monic quadratic polynomial $x^{2} + bx + c$ over a field of characteristic 2. If b = 0, then the solution reduces to extracting a square root, so the solution is $x = \sqrt{c}$ and there is only one root since
- Context after: In summary, $\displaystyle x^{2} + c = (x + \sqrt{c})^{2}.$ See quadratic residue for more information about extracting square roots in finite fields. In the case that b ≠ 0, there are two distinct roots, but if the polynomial is irreducible, they cannot be expressed in terms of square roots of numbers in the coefficient field. Instead, define the…
- Translator read (piece 0): `-sqrt(c)`  =  `sqrt(c)`  · notes: pre:trailing_punct
sides: -\sqrt{c}  ||  -\sqrt{c} + 2\sqrt{c}
- Translator read (piece 1): `sqrt(c)`  =  `sqrt(c)`  · notes: pre:trailing_punct
sides: -\sqrt{c} + 2\sqrt{c}  ||  \sqrt{c}
- Assumptions: domains {'c': 'real'}; constants {}; constraints ['c >= 0']
- Verifier: Chain link 0: The identity fails at 58 of 59 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at c=0.0305244: lhs=-0.17471233499, rhs=0.174712334996).
- Counterexample: {'c': '0.0305244'} → lhs -0.1747123349967025081543015453016741840, rhs 0.17471233499670250815430154530167418401, rel diff 2.0000000000
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 10/11 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:25272:1378159893:147

- Page: [Quadratic reciprocity](https://en.wikipedia.org/wiki/Quadratic_reciprocity) › History and alternative statements > Jacobi symbol  · verdict **FAIL**, symbolic unknown
- LaTeX: `\left(\frac{m}{n}\right) = (-1)^{\frac{(m-1)(n-1)}{4}}\left(\frac{n}{m}\right).`
- Context before: …and if both numbers are positive and odd (this is sometimes called "Jacobi's reciprocity law"):
- Context after: However, if the Jacobi symbol is 1 but the denominator is not a prime, it does not necessarily follow that the numerator is a quadratic residue of the denominator. Gauss's cases 9) - 14) above can be expressed in terms of Jacobi symbols: $\left (\frac{M}{p}\right) = (-1)^{\frac{(p-1)(M-1)}{4}} \left(\frac{p}{M}\right ),$ and since p is prime the le…
- Translator read: `m/n`  =  `(-1)**((m - 1)*(n - 1)/4)*n/m`  · notes: pre:left_right
pre:trailing_punct
sides: (\frac{m}{n}\right)  ||  (-1)^{\frac{(m-1)(n-1)}{4}}\left(\frac{n}{m}\right)
- Assumptions: domains {'m': 'nonneg_integer', 'n': 'nonneg_integer'}; constants {}; constraints ['Ne(n, 0)', 'Ne(m, 0)']
- Verifier: The identity fails at 52 of 53 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at m=2, n=1: lhs=2.000000000000, rhs=0.500000000000).
- Counterexample: {'m': '2', 'n': '1'} → lhs 2.00000000000000000000000000000000000000, rhs 0.50000000000000000000000000000000000000, rel diff 0.7500000000
- Regimes: small_positive 12/19 fail, 7 err, unit_interval 5/8 fail, 3 err, integers_small 12/23 fail, 11 err, mixed_sign 11/19 fail, 7 err, large 12/19 fail, 7 err

---
## wiki:en:25272:1378159893:148

- Page: [Quadratic reciprocity](https://en.wikipedia.org/wiki/Quadratic_reciprocity) › History and alternative statements > Jacobi symbol  · verdict **FAIL**, symbolic unknown
- LaTeX: `\left (\frac{M}{p}\right) = (-1)^{\frac{(p-1)(M-1)}{4}} \left(\frac{p}{M}\right ),`
- Context before: …d "Jacobi's reciprocity law"): $\left(\frac{m}{n}\right) = (-1)^{\frac{(m-1)(n-1)}{4}}\left(\frac{n}{m}\right).$ However, if the Jacobi symbol is 1 but the denominator is not a prime, it does not necessarily follow that the numerator is a quadratic residue of the denominator. Gauss's cases 9) - 14) above can be expressed in terms of Jacobi symbols:
- Context after: and since p is prime the left hand side is a Legendre symbol, and we know whether M is a residue modulo p or not. The formulas listed in the preceding section are true for Jacobi symbols as long as the symbols are defined. Euler's formula may be written $\left(\frac{a}{m}\right) =\left(\frac{a}{m \pm 4an}\right), \qquad n \in \Z, m\pm4an>0.$ Exampl…
- Translator read: `M/p`  =  `(-1)**((M - 1)*(p - 1)/4)*p/M`  · notes: pre:left_right
pre:trailing_punct
sides: (\frac{M}{p}\right)  ||  (-1)^{\frac{(p-1)(M-1)}{4}} \left(\frac{p}{M}\right )
- Assumptions: domains {'M': 'positive', 'p': 'positive_integer'}; constants {}; constraints ['Q.prime(p)']
- Verifier: The identity fails at 29 of 29 evaluable points, a clear majority in every regime (unit_interval, integers_small) (e.g. at M=0.0785788, p=1: lhs=0.078578800000, rhs=12.72607878969).
- Counterexample: {'M': '0.0785788', 'p': '1'} → lhs 0.07857880000000000000000000000000000000, rhs 12.7260787896990027844660391861418092411, rel diff 0.9938253721
- Regimes: small_positive 2/40 fail, 38 err, unit_interval 12/34 fail, 22 err, integers_small 12/25 fail, 13 err, mixed_sign 3/40 fail, 37 err, large 0/40 fail, 40 err

---
## wiki:en:40087321:1350938227:12

- Page: [Quadrisecant](https://en.wikipedia.org/wiki/Quadrisecant) › For special classes of curves > Skew lines  · verdict **FAIL**, symbolic not_equal
- LaTeX: `i=1,2,3,4,5`
- Context before: …e no quadrisecants. In spaces with complex number coordinates rather than real coordinates, four skew lines always have exactly two quadrisecants. The quadrisecants of sets of lines play an important role in the construction of the Schläfli double six, a configuration of twelve lines intersecting each other in 30 crossings. If five lines $a_i$ (for
- Context after: ) are given in three-dimensional space, such that all five are intersected by a common line $b_6$ but are otherwise in general position, then each of the five quadruples of the lines $a_i$ has a second quadrisecant $b_i$ , and the five lines $b_i$ formed in this way are all intersected by a common line $a_6$ . These twelve lines and the 30 intersec…
- Translator read: `i`  =  `1`  · notes: cond: 2,3,4,5
hint:i_present
sides: i  ||  1
- Assumptions: domains {}; constants {'i': 'I'}; constraints []
- Verifier: The constant identity does not hold: both sides differ beyond 1e-8 relative error, stably at two working precisions (lhs=(0.0 + 1.0j), rhs=1.0000000000000000).
- Counterexample: {} → lhs (0.0 + 1.0j), rhs 1.00000000000000000000000000000000000000, rel diff 1.4142135623
- Regimes: constant 1/1 fail, 0 err

---
## wiki:en:20131133:1374307038:33

- Page: [Quartic reciprocity](https://en.wikipedia.org/wiki/Quartic_reciprocity) › Gaussian integers > Quartic residue character  · verdict **FAIL**, symbolic unknown
- LaTeX: `\Bigg[\frac{\alpha}{\pi}\Bigg]=\Bigg[\frac{\alpha}{\theta}\Bigg]`
- Context before: …\pmod{\pi}$ is solvable in Z[i] if and only if $\left[\frac{\alpha}{\pi}\right] = 1.$ $\Bigg[\frac{\alpha\beta}{\pi}\Bigg]=\Bigg[\frac{\alpha}{\pi}\Bigg]\Bigg[\frac{\beta}{\pi}\Bigg]$ $\overline{\Bigg[\frac{\alpha}{\pi}\Bigg]}=\Bigg[\frac{\overline{\alpha}}{\overline{\pi}}\Bigg]$ where the bar denotes complex conjugation. if π and θ are associates,
- Context after: if α ≡ β (mod π), $\Bigg[\frac{\alpha}{\pi}\Bigg]=\Bigg[\frac{\beta}{\pi}\Bigg]$ The biquadratic character can be extended to odd composite numbers in the "denominator" in the same way the Legendre symbol is generalized into the Jacobi symbol. As in that case, if the "denominator" is composite, the symbol can equal one without the congruence being…
- Translator read: `alpha/pi`  =  `alpha/theta`  · notes: pre:size
sides: [\frac{\alpha}{\pi}\Bigg]  ||  [\frac{\alpha}{\theta}\Bigg]
- Assumptions: domains {'alpha': 'real', 'theta': 'real'}; constants {}; constraints ['Ne(theta, 0)']
- Verifier: The identity fails at 60 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at alpha=0.221202, theta=0.0591842: lhs=0.070410783443, rhs=3.737517783462).
- Counterexample: {'alpha': '0.221202', 'theta': '0.0591842'} → lhs 0.07041078344362686412549725245105384382, rhs 3.73751778346247816140118477566647855339, rel diff 0.9811610840
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:20131133:1374307038:38

- Page: [Quartic reciprocity](https://en.wikipedia.org/wiki/Quartic_reciprocity) › Gaussian integers > Statements of the theorem  · verdict **FAIL**, symbolic unknown
- LaTeX: `\Bigg[\frac{\pi}{\theta}\Bigg] =\left[\frac{\theta}{\pi}\right],`
- Context before: …da = \pi_1^{\alpha_1}\pi_2^{\alpha_2}\pi_3^{\alpha_3} \dots$ If a and b are ordinary integers, a ≠ 0, |b > 1, gcd(a, b) = 1, then $\left[\frac{a}{b}\right] = 1.$ Statements of the theorem. Gauss stated the law of biquadratic reciprocity in this form: Let π and θ be distinct primary primes of Z[i]. Then if either π or θ or both are ≡ 1 (mod 4), then
- Context after: but if both π and θ are ≡ 3 + 2i (mod 4), then $\Bigg[\frac{\pi}{\theta}\Bigg] =-\left[\frac{\theta}{\pi}\right].$ Just as the quadratic reciprocity law for the Legendre symbol is also true for the Jacobi symbol, the requirement that the numbers be prime is not needed; it suffices that they be odd relatively prime nonunits. Probably the most well-k…
- Translator read: `pi/theta`  =  `theta/pi`  · notes: pre:left_right
pre:size
pre:trailing_punct
sides: [\frac{\pi}{\theta}\Bigg]  ||  [\frac{\theta}{\pi}\right]
- Assumptions: domains {'theta': 'real'}; constants {}; constraints ['Ne(theta, 0)']
- Verifier: The identity fails at 60 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at theta=0.157283: lhs=19.97413994894, rhs=0.050064733828).
- Counterexample: {'theta': '0.157283'} → lhs 19.9741399489442167205778334802839651087, rhs 0.05006473382864514819147468990903835280, rel diff 0.9974935224
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:20131133:1374307038:39

- Page: [Quartic reciprocity](https://en.wikipedia.org/wiki/Quartic_reciprocity) › Gaussian integers > Statements of the theorem  · verdict **FAIL**, symbolic unknown
- LaTeX: `\Bigg[\frac{\pi}{\theta}\Bigg] =-\left[\frac{\theta}{\pi}\right].`
- Context before: …a, b) = 1, then $\left[\frac{a}{b}\right] = 1.$ Statements of the theorem. Gauss stated the law of biquadratic reciprocity in this form: Let π and θ be distinct primary primes of Z[i]. Then if either π or θ or both are ≡ 1 (mod 4), then $\Bigg[\frac{\pi}{\theta}\Bigg] =\left[\frac{\theta}{\pi}\right],$ but if both π and θ are ≡ 3 + 2i (mod 4), then
- Context after: Just as the quadratic reciprocity law for the Legendre symbol is also true for the Jacobi symbol, the requirement that the numbers be prime is not needed; it suffices that they be odd relatively prime nonunits. Probably the most well-known statement is: Let π and θ be primary relatively prime nonunits. Then…
- Translator read: `pi/theta`  =  `-theta/pi`  · notes: pre:left_right
pre:size
pre:trailing_punct
sides: [\frac{\pi}{\theta}\Bigg]  ||  -\left[\frac{\theta}{\pi}\right]
- Assumptions: domains {'theta': 'real'}; constants {}; constraints ['Ne(theta, 0)']
- Verifier: The identity fails at 60 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at theta=0.0673956: lhs=46.61421003136, rhs=-0.02145268576).
- Counterexample: {'theta': '0.0673956'} → lhs 46.6142100313639649838067082017149915454, rhs -0.0214526857652882825826907651254972578, rel diff 1.0004602177
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:2887560:1343297065:0

- Page: [Rayleigh flow](https://en.wikipedia.org/wiki/Rayleigh_flow) › Theory  · verdict **FAIL**, symbolic unknown
- LaTeX: `\ \frac{dM^2}{M^2} = \frac{1 + \gamma M^2}{1 - M^2}\left(1 + \frac{\gamma - 1}{2}M^2\right)\frac{dT_0}{T_0}`
- Context before: …onic Mach number and increases a supersonic Mach number along the duct. It can be shown that for calorically perfect flows the maximum entropy occurs at . Theory. The Rayleigh flow model begins with a differential equation that relates the change in Mach number with the change in stagnation temperature, T0. The differential equation is shown below.
- Context after: Solving the differential equation leads to the relation shown below, where T0* is the stagnation temperature at the throat location of the duct which is required for thermally choking the flow. $\ \frac{T_0}{T_0^*} = \frac{2\left(\gamma + 1\right)M^2}{\left(1 + \gamma M^2\right)^2}\left(1 + \frac{\gamma - 1}{2}M^2\right)$ These values are significa…
- Translator read: `d`  =  `d*(M**2*gamma + 1)*(M**2*(gamma/2 - 1/2) + 1)/(1 - M**2)`  · notes: pre:left_right
pre:spacing
sides: \frac{dM^2}{M^2}  ||  \frac{1 + \gamma M^2}{1 - M^2}\left(1 + \frac{\gamma - 1}{2}M^2\right)\frac{dT_0}{T_0}
- Assumptions: domains {'M': 'positive', 'd': 'positive', 'gamma': 'positive'}; constants {}; constraints ['Ne(1 - M**2, 0)']
- Verifier: The identity fails at 60 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at M=0.419096, d=0.290172, gamma=0.545711: lhs=0.290172000000, rhs=0.370346758144).
- Counterexample: {'M': '0.419096', 'd': '0.290172', 'gamma': '0.545711'} → lhs 0.29017200000000000000000000000000000000, rhs 0.37034675814452911487875636795908060254, rel diff 0.2164856486
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:25880:1375887525:17

- Page: [Refractive index](https://en.wikipedia.org/wiki/Refractive_index) › Relations to other quantities > Total internal reflection  · verdict **FAIL**, symbolic unknown
- LaTeX: `\frac{n_1}{n_2} \sin \theta_1 > 1,`
- Context before: …efracted towards the normal of the surface. The higher the refractive index, the closer to the normal direction the light will travel. When passing into a medium with lower refractive index, the light will instead be refracted away from the normal, towards the surface. Total internal reflection. If there is no angle θ2 fulfilling Snell's law, i.e.,
- Context after: the light cannot be transmitted and will instead undergo total internal reflection. This occurs only when going to a less optically dense material, i.e., one with lower refractive index. To get total internal reflection the angles of incidence θ1 must be larger than the critical angle $\theta_\mathrm{c} = \arcsin\!\left(\frac{n_2}{n_1}\right)\!.$ R…
- Translator read: `n_1*sin(theta_1)/n_2`  >  `1`  · notes: pre:trailing_punct
sides: \frac{n_1}{n_2} \sin \theta_1  ||  1
- Assumptions: domains {'n_1': 'nonneg_integer', 'n_2': 'nonneg_integer', 'theta_1': 'angle'}; constants {}; constraints ['Ne(n_2, 0)']
- Verifier: The inequality fails at 53 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at n_1=0, n_2=2, theta_1=0.0489134: lhs=0, rhs=1.000000000000).
- Counterexample: {'n_1': '0', 'n_2': '2', 'theta_1': '0.0489134'} → lhs 0, rhs 1.00000000000000000000000000000000000000, rel diff 1.0000000000
- Regimes: small_positive 10/12 fail, 0 err, unit_interval 9/12 fail, 0 err, integers_small 11/12 fail, 0 err, mixed_sign 11/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:288291:1380743965:76

- Page: [Ricci flow](https://en.wikipedia.org/wiki/Ricci_flow) › Examples > Ricci solitons  · verdict **FAIL**, symbolic unknown
- LaTeX: `\operatorname{Ric}^g+\operatorname{Hess}^gf=\frac{1}{2}g.`
- Context before: …birational to Cn, which are Ricci solitons. These examples were constructed by Cao and Feldman-Ilmanen-Knopf. (Chow-Knopf 2004) A 4-dimensional example exhibiting only torus symmetry was recently discovered by Bamler-Cifarelli-Conlon-Deruelle. A gradient shrinking Ricci soliton consists of a smooth Riemannian manifold (M,g) and f ∈ C∞(M) such that
- Context after: One of the major achievements of was to show that, if M is a closed three-dimensional smooth manifold, then finite-time singularities of the Ricci flow on M are modeled on complete gradient shrinking Ricci solitons (possibly on underlying manifolds distinct from M). In 2008, Huai-Dong Cao, Bing-Long Chen, and Xi-Ping Zhu completed the classificatio…
- Translator read: `Hess**g*f + Ric**g`  =  `g/2`  · notes: pre:trailing_punct
sides: \operatorname{Ric}^g+\operatorname{Hess}^gf  ||  \frac{1}{2}g
- Assumptions: domains {'Hess': 'positive', 'Ric': 'positive', 'f': 'positive', 'g': 'positive'}; constants {}; constraints []
- Verifier: The identity fails at 60 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at Hess=0.105713, Ric=0.559012, f=0.0313371, g=0.248755: lhs=0.883224730112, rhs=0.124377500000).
- Counterexample: {'Hess': '0.105713', 'Ric': '0.559012', 'f': '0.0313371', 'g': '0.248755'} → lhs 0.88322473011267124100842388037050735421, rhs 0.12437750000000000000000000000000000000, rel diff 0.8591779693
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:25809:1381282197:146

- Page: [Riemann zeta function](https://en.wikipedia.org/wiki/Riemann_zeta_function) › Applications > Infinite series  · verdict **FAIL**, symbolic unknown
- LaTeX: `\sum_{n=2}^\infty\left[\frac{2(-1)^n\zeta(n)}{4^n n}-\frac{(-1)^n\zeta(n)}{2^n n} \right]= \ln \left( \frac{\varpi}{2\sqrt2} \right)`
- Context before: …\infty\bigl(\zeta(4n)-1\bigr) = \frac78-\frac{\pi}{4}\left(\frac{e^{2\pi}+1}{e^{2\pi}-1}\right)$ $\sum_{n=2}^\infty\frac{\zeta(n)-1}{n}\Im \bigl((1+i)^n-1-i^n\bigr) = \frac{\pi}{4}$ where $\Im$ denotes the imaginary part of a complex number. Another interesting series that relates to the natural logarithm of the lemniscate constant is the following
- Context after: There are yet more formulas in the article Harmonic number. Generalizations. There are a number of related zeta functions that can be considered to be generalizations of the Riemann zeta function. These include the Hurwitz zeta function $\zeta(s,q) = \sum_{k=0}^\infty \frac{1}{(k+q)^s}$ (the convergent series representation was given by Helmut Hass…
- Translator read: `Sum(2*(-1)**n*zeta(n)/(4**n*n) - (-1)**n*zeta(n)/(2**n*n), (n, 2, oo))`  =  `log(sqrt(2)*varpi/4)`  · notes: pre:left_right
sides: \sum_{n=2}^\infty\left[\frac{2(-1)^n\zeta(n)}{4^n n}-\frac{(-1)^n\zeta(n)}{2^n n} \right]  ||  \ln \left( \frac{\varpi}{2\sqrt2} \right)
- Assumptions: domains {}; constants {'varpi': 'pi'}; constraints []
- Verifier: The constant identity does not hold: both sides differ beyond 1e-8 relative error, stably at two working precisions (lhs=-0.075761435208381, rhs=0.1050091150094822).
- Counterexample: {} → lhs -0.0757614352083811005821891596116244681, rhs 0.10500911500948221001757916916579385953, rel diff 1.7214748472
- Regimes: constant 1/1 fail, 0 err

---
## wiki:en:26452:1345571927:372

- Page: [Riesz representation theorem](https://en.wikipedia.org/wiki/Riesz_representation_theorem) › Riesz representation theorem > Constructions of the representing vector > Example in finite dimensions using matrix transformations  · verdict **FAIL**, symbolic not_equal
- LaTeX: `i = 1, \ldots, n.`
- Context before: …t $\varphi \in H^*$ be any linear functional and let $\varphi_1, \ldots, \varphi_n \in \Complex$ be the unique scalars such that $\varphi\left(w_1, \ldots, w_n\right) = \varphi_1 w_1 + \cdots + \varphi_n w_n \qquad \text{ for all } \; w := \left(w_1, \ldots, w_n\right) \in H,$ where it can be shown that $\varphi_i = \varphi\left(e_i\right)$ for all
- Context after: Then the Riesz representation of $\varphi$ is the vector $f_{\varphi} ~:=~ \overline{\varphi_1} e_1 + \cdots + \overline{\varphi_n} e_n ~=~ \left(\overline{\varphi_1}, \ldots, \overline{\varphi_n}\right) \in H.$ To see why, identify every vector $w = \left(w_1, \ldots, w_n\right)$ in $H$ with the column matrix $\vec{w} := \begin{bmatrix}w_1 \\ \vdo…
- Translator read: `i`  =  `1`  · notes: pre:trailing_punct
cond: \ldots, n
hint:i_present
sides: i  ||  1
- Assumptions: domains {}; constants {'i': 'I'}; constraints []
- Verifier: The constant identity does not hold: both sides differ beyond 1e-8 relative error, stably at two working precisions (lhs=(0.0 + 1.0j), rhs=1.0000000000000000).
- Counterexample: {} → lhs (0.0 + 1.0j), rhs 1.00000000000000000000000000000000000000, rel diff 1.4142135623
- Regimes: constant 1/1 fail, 0 err

---
## wiki:en:622053:1377937648:52

- Page: [S-matrix](https://en.wikipedia.org/wiki/S-matrix) › In one-dimensional quantum mechanics > Time-reversal symmetry > Finite square well  · verdict **FAIL**, symbolic unknown
- LaTeX: `-e^{-i\delta}=e^{i\delta}`
- Context before: …a plane wave coming (faraway) from the left side or likewise $D_k\exp(-ikx)$ (faraway) from the right side. The S-matrix for the plane wave with wave number k has the solution: $S_{12}=S_{21}=\frac{\exp(-2ika)}{\cos(2la)-i\sin(2la)\frac{l^2+k^2}{2kl}}$ and $S_{11}=S_{12}\cdot i\sin(2la)\frac{l^2-k^2}{2kl}$ ; hence $e^{i\delta}=\pm i$ and therefore
- Context after: and $S_{22}=S_{11}$ in this case. Whereby $l = \sqrt{k^2+\frac{2mV_0}{\hbar^2}}$ is the (increased) wave number of the plane wave inside the square well, as the energy eigenvalue $E_k$ associated with the plane wave has to stay constant: $E_k = \frac{\hbar^2 k^2}{2m}=\frac{\hbar^2 l^2}{2m}-V_0$ The transmission is…
- Translator read: `-1/e**(delta*i)`  =  `e**(delta*i)`  · notes: hint:e_only_as_exp_base
hint:i_present
sides: -e^{-i\delta}  ||  e^{i\delta}
- Assumptions: domains {'delta': 'positive'}; constants {'e': 'E', 'i': 'I'}; constraints []
- Verifier: The identity fails at 58 of 58 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at delta=0.00684557: lhs=(-0.9999765691, rhs=(0.99997656917).
- Counterexample: {'delta': '0.00684557'} → lhs (-0.999976569177188697989088181933154381, rhs (0.9999765691771886979890881819331543811, rel diff 1.9999531383
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 10/10 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:9653775:1347211283:11

- Page: [Semimartingale](https://en.wikipedia.org/wiki/Semimartingale) › Semimartingale decompositions > Special semimartingales  · verdict **FAIL**, symbolic unknown
- LaTeX: `X = M^X +B^X`
- Context before: …ocal martingale and A is a continuous finite-variation process starting at zero. For example, if X is an Itō process satisfying the stochastic differential equation dXt = σt dWt + bt dt, then $M_t=X_0+\int_0^t\sigma_s\,dW_s,\ A_t=\int_0^t b_s\,ds.$ Special semimartingales. A special semimartingale is a real-valued process $X$ with the decomposition
- Context after: , where $M^X$ is a local martingale and $B^X$ is a predictable finite-variation process starting at zero. If this decomposition exists, then it is unique up to a P-null set. Every special semimartingale is a semimartingale. Conversely, a semimartingale is a special semimartingale if and only if the process Xt* ≡ sups ≤ t Xs is locally integrable .…
- Translator read: `X`  =  `B**X + M**X`  · notes: sides: X  ||  M^X +B^X
- Assumptions: domains {'B': 'positive', 'M': 'positive', 'X': 'positive'}; constants {}; constraints []
- Verifier: The identity fails at 60 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at B=0.241437, M=0.000409698, X=0.0401906: lhs=0.040190600000, rhs=1.675375268094).
- Counterexample: {'B': '0.241437', 'M': '0.000409698', 'X': '0.0401906'} → lhs 0.04019060000000000000000000000000000000, rhs 1.67537526809482645631328185513217888868, rel diff 0.9760109864
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:22653593:1375897417:4

- Page: [Special classes of semigroups](https://en.wikipedia.org/wiki/Special_classes_of_semigroups) › List of special classes of semigroups  · verdict **FAIL**, symbolic unknown
- LaTeX: `a^\omega a=a^\omega`
- Context before: …then a = b. C&P p. 4 Separative semigroup ab = a2 = b2 ⇒ a = b C&P p. 130–131 Reversible semigroup Sa ∩ Sb ≠ Ø aS ∩ bS ≠ Ø C&P p. 34 Right reversible semigroup Sa ∩ Sb ≠ Ø C&P p. 34 Left reversible semigroup aS ∩ bS ≠ Ø C&P p. 34 Aperiodic semigroup There exists k (depending on a) such that ak = ak+1 Equivalently, for finite semigroup: for each a,
- Context after: . KKM p. 29 Pin p. 158 ω-semigroup E is countable descending chain under the order a ≤H b Gril p. 233–238 Left Clifford semigroup (LC-semigroup) aS ⊆ Sa Shum Right Clifford semigroup (RC-semigroup) Sa ⊆ aS Shum Orthogroup Ha is a group. E is a subsemigroup of S Shum Complete commutative semigroup ab = ba ak is in a subgroup of S for some k. Every n…
- Translator read: `a*a**omega`  =  `a**omega`  · notes: sides: a^\omega a  ||  a^\omega
- Assumptions: domains {'a': 'real', 'omega': 'positive'}; constants {}; constraints ['a > 0']
- Verifier: The identity fails at 60 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at a=0.0500503, omega=0.0941054: lhs=0.037758421552, rhs=0.754409495098).
- Counterexample: {'a': '0.0500503', 'omega': '0.0941054'} → lhs 0.03775842155252540960462334918646810843, rhs 0.75440949509843916229519801452674825986, rel diff 0.9499497000
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:22653593:1375897417:8

- Page: [Special classes of semigroups](https://en.wikipedia.org/wiki/Special_classes_of_semigroups) › List of special classes of semigroups  · verdict **FAIL**, symbolic unknown
- LaTeX: `(aba)^\omega=a^\omega`
- Context before: …p. 76 D-simple semigroup (Bisimple semigroup) Da = S C&P p. 49 Semisimple semigroup Let J(a) = S1aS1, I(a) = J(a) − Ja. Each Rees factor semigroup J(a)/I(a) is 0-simple or simple. C&P p. 71–75 $\mathbf{CS}$ : Simple semigroup Ja = S. (There exists no A ⊆ S, A ≠ S such that SA ⊆ A and AS ⊆ A.), equivalently, for finite semigroup: $a^{\omega}a=a$ and
- Context after: . Finite C&P p. 5 Higg p. 16 Pin pp. 151, 158 0-simple semigroup 0 ∈ S S2 ≠ 0 If A ⊆ S is such that AS ⊆ A and SA ⊆ A then A = 0. C&P p. 67 Left 0-simple semigroup 0 ∈ S S2 ≠ 0 If A ⊆ S is such that SA ⊆ A then A = 0. C&P p. 67 Right 0-simple semigroup 0 ∈ S S2 ≠ 0 If A ⊆ S is such that AS ⊆ A then A = 0. C&P p. 67 Cyclic semigroup (Monogenic semig…
- Translator read: `(a**2*b)**omega`  =  `a**omega`  · notes: sides: (aba)^\omega  ||  a^\omega
- Assumptions: domains {'a': 'real', 'b': 'real', 'omega': 'positive'}; constants {}; constraints ['a**2*b > 0', 'a > 0']
- Verifier: The identity fails at 54 of 54 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at a=0.175022, b=0.0711951, omega=0.224891: lhs=0.252047881365, rhs=0.675738008298).
- Counterexample: {'a': '0.175022', 'b': '0.0711951', 'omega': '0.224891'} → lhs 0.25204788136585140427028854197511965683, rhs 0.67573800829834093501785398193761181955, rel diff 0.6270035453
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 6/6 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:22653593:1375897417:5

- Page: [Special classes of semigroups](https://en.wikipedia.org/wiki/Special_classes_of_semigroups) › List of special classes of semigroups  · verdict **FAIL**, symbolic unknown
- LaTeX: `yx^\omega =x^\omega=x^\omega y`
- Context before: …) Sa ⊆ aS Shum Orthogroup Ha is a group. E is a subsemigroup of S Shum Complete commutative semigroup ab = ba ak is in a subgroup of S for some k. Every nonempty subset of E has an infimum. Gril p. 110 Nilsemigroup (Nilpotent semigroup) 0 ∈ S ak = 0 for some integer k which depends on a. Equivalently, for finite semigroup: for each element x and y,
- Context after: . Finite Gril p. 99 Pin p. 148 Elementary semigroup ab = ba S is of the form G ∪ N where G is a group, and 1 ∈ G N is an ideal, a nilsemigroup, and 0 ∈ N Gril p. 111 E-unitary semigroup There exists unique x such that axa = a and xax = x. ea = e ⇒ a ∈ E Gril p. 245 Finitely presented semigroup S has a presentation ( X; R ) in which X and R are fini…
- Translator read (piece 0): `x**omega*y`  =  `x**omega`  · notes: sides: yx^\omega  ||  x^\omega
- Translator read (piece 1): `x**omega`  =  `x**omega*y`  · notes: sides: x^\omega  ||  x^\omega y
- Assumptions: domains {'omega': 'positive', 'x': 'real', 'y': 'real'}; constants {}; constraints ['x > 0']
- Verifier: Chain link 0: The identity fails at 58 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at omega=0.0547788, x=0.142366, y=0.0125532: lhs=0.011281817244, rhs=0.898720425389).
- Counterexample: {'omega': '0.0547788', 'x': '0.142366', 'y': '0.0125532'} → lhs 0.01128181724400077038938374442508157629, rhs 0.89872042538960347874516015239792055405, rel diff 0.9874468000
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 10/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:22653593:1375897417:11

- Page: [Special classes of semigroups](https://en.wikipedia.org/wiki/Special_classes_of_semigroups) › List of special classes of semigroups  · verdict **FAIL**, symbolic unknown
- LaTeX: `(ab)^\omega a=(ab)^\omega`
- Context before: …group which is also a topological space. Such that the semigroup product is continuous. Not applicable Pin p. 130 Syntactic semigroup The smallest finite monoid which can recognize a subset of another semigroup. Pin p. 14 $\mathbf R$ : the R-trivial monoids R-trivial. That is, each R-equivalence class is trivial. Equivalently, for finite semigroup:
- Context after: . Finite Pin p. 158 $\mathbf L$ : the L-trivial monoids L-trivial. That is, each L-equivalence class is trivial. Equivalently, for finite monoids, $b(ab)^\omega=(ab)^\omega$ . Finite Pin p. 158 $\mathbf J$ : the J-trivial monoids Monoids which are J-trivial. That is, each J-equivalence class is trivial. Equivalently, the monoids which are L-trivial…
- Translator read: `a*(a*b)**omega`  =  `(a*b)**omega`  · notes: sides: (ab)^\omega a  ||  (ab)^\omega
- Assumptions: domains {'a': 'real', 'b': 'real', 'omega': 'positive'}; constants {}; constraints ['a*b > 0']
- Verifier: The identity fails at 58 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at a=0.0786547, b=0.25012, omega=0.0875879: lhs=0.055755614483, rhs=0.708865642905).
- Counterexample: {'a': '0.0786547', 'b': '0.25012', 'omega': '0.0875879'} → lhs 0.05575561448305410842350072691542845289, rhs 0.70886564290568915047035621412869736832, rel diff 0.9213453000
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 10/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:22653593:1375897417:13

- Page: [Special classes of semigroups](https://en.wikipedia.org/wiki/Special_classes_of_semigroups) › List of special classes of semigroups  · verdict **FAIL**, symbolic unknown
- LaTeX: `b(ab)^\omega=(ab)^\omega`
- Context before: …gnize a subset of another semigroup. Pin p. 14 $\mathbf R$ : the R-trivial monoids R-trivial. That is, each R-equivalence class is trivial. Equivalently, for finite semigroup: $(ab)^\omega a=(ab)^\omega$ . Finite Pin p. 158 $\mathbf L$ : the L-trivial monoids L-trivial. That is, each L-equivalence class is trivial. Equivalently, for finite monoids,
- Context after: . Finite Pin p. 158 $\mathbf J$ : the J-trivial monoids Monoids which are J-trivial. That is, each J-equivalence class is trivial. Equivalently, the monoids which are L-trivial and R-trivial. Finite Pin p. 158 $\mathbf{R_1}$ : idempotent and R-trivial monoids R-trivial. That is, each R-equivalence class is trivial. Equivalently, for finite monoids:…
- Translator read: `b*(a*b)**omega`  =  `(a*b)**omega`  · notes: sides: b(ab)^\omega  ||  (ab)^\omega
- Assumptions: domains {'a': 'real', 'b': 'real', 'omega': 'positive'}; constants {}; constraints ['a*b > 0']
- Verifier: The identity fails at 59 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at a=0.0756399, b=0.185269, omega=0.229624: lhs=0.069535567752, rhs=0.375322195035).
- Counterexample: {'a': '0.0756399', 'b': '0.185269', 'omega': '0.229624'} → lhs 0.06953556775204214556523412740023834948, rhs 0.37532219503555449408823995055966378336, rel diff 0.8147310000
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 11/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:22653593:1375897417:18

- Page: [Special classes of semigroups](https://en.wikipedia.org/wiki/Special_classes_of_semigroups) › List of special classes of semigroups  · verdict **FAIL**, symbolic unknown
- LaTeX: `(a^\omega a^\omega a^\omega)^\omega=a^\omega`
- Context before: …ce class is trivial. Equivalently, for finite monoids: aba = ab. Finite Pin p. 158 $\mathbf {L_1}$ : idempotent and L-trivial monoids L-trivial. That is, each L-equivalence class is trivial. Equivalently, for finite monoids: aba = ba. Finite Pin p. 158 $\mathbb D\mathbf{S}$ : Semigroup whose regular D are semigroup Equivalently, for finite monoids:
- Context after: . Equivalently, regular H-classes are groups, Equivalently, v≤Ja implies v R va and v L av Equivalently, for each idempotent e, the set of a such that e≤Ja is closed under product (i.e. this set is a subsemigroup) Equivalently, there exists no idempotent e and f such that e J f but not ef J e Equivalently, the monoid $B^1_2$ does not divide $S\time…
- Translator read: `(a**(3*omega))**omega`  =  `a**omega`  · notes: sides: (a^\omega a^\omega a^\omega)^\omega  ||  a^\omega
- Assumptions: domains {'a': 'real', 'omega': 'positive'}; constants {}; constraints ['a**(3*omega) > 0', 'a > 0']
- Verifier: The identity fails at 60 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at a=0.00331622, omega=0.0560892: lhs=0.947544999428, rhs=0.725997070224).
- Counterexample: {'a': '0.00331622', 'omega': '0.0560892'} → lhs 0.94754499942839349715410199181665949771, rhs 0.72599707022486021719992659827925307555, rel diff 0.2338125675
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err
