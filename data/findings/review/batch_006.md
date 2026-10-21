# Review batch 006 — 22 items

For each item answer with one JSON line (Finding schema): {"formula_id": ..., "verdict": "FAIL", "review": {"status": "confirmed_error"|"false_positive"|"ambiguous", "reviewer": "<name>", "notes": "<why, one or two sentences>"}, "suggested_fix": "<corrected LaTeX or null>", "evidence": "<independent source or derivation>"}


---
## wiki:en:80262208:1376111431:692

- Page: [Golden field](https://en.wikipedia.org/wiki/Golden_field) › Fibonacci numbers  · verdict **FAIL**, symbolic unknown
- LaTeX: `\textstyle \mathrm{N}(\varphi^n) = (-1)^n`
- Context before: …tstyle \varphi^n$ and $\textstyle \overline\varphi^n$ are the roots of the quadratic polynomial $\textstyle x^2 - L_nx + (-1)^n$ . This is the minimal polynomial for $\textstyle \varphi^n$ for any non-zero integer $n$ . The quadratic polynomial $\textstyle x^2 - 5F_nx + (-1)^{n+1}5$ is the minimal polynomial for $\textstyle \varphi^n\sqrt5$ . [ref]
- Context after: In the limit, consecutive Fibonacci or Lucas numbers approach a ratio of $\varphi$ , and the ratio of Lucas to Fibonacci numbers approaches $\sqrt5$ : $\begin{align} \lim_{n \to \infty} \frac {F_{n+1}}{F_n} &= \lim_{n \to \infty} \frac{L_{n+1}}{L_n} = \varphi, & \lim_{n \to \infty} \frac {L_n}{F_n} &= \sqrt5. \end{align}$ Theorems about the Fibonac…
- Translator read: `N*phi**n`  =  `(-1)**n`  · notes: pre:style
mult_not_call:N
sides: \mathrm{N}(\varphi^n)  ||  (-1)^n
- Assumptions: domains {'N': 'nonneg_integer', 'n': 'nonneg_integer', 'phi': 'real'}; constants {}; constraints ['Ne(n, 0)']
- Verifier: The identity fails at 60 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at N=1, n=1, phi=1: lhs=1.000000000000, rhs=-1.00000000000).
- Counterexample: {'N': '1', 'n': '1', 'phi': '1'} → lhs 1.00000000000000000000000000000000000000, rhs -1.0000000000000000000000000000000000000, rel diff 2.0000000000
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:80262208:1376111431:694

- Page: [Golden field](https://en.wikipedia.org/wiki/Golden_field) › Fibonacci numbers  · verdict **FAIL**, symbolic unknown
- LaTeX: `\textstyle \mathrm{N}(\varphi^n\sqrt5~\!) = (-1)^n(-5)`
- Context before: …tstyle \varphi^n$ and $\textstyle \overline\varphi^n$ are the roots of the quadratic polynomial $\textstyle x^2 - L_nx + (-1)^n$ . This is the minimal polynomial for $\textstyle \varphi^n$ for any non-zero integer $n$ . The quadratic polynomial $\textstyle x^2 - 5F_nx + (-1)^{n+1}5$ is the minimal polynomial for $\textstyle \varphi^n\sqrt5$ . [ref]
- Context after: In the limit, consecutive Fibonacci or Lucas numbers approach a ratio of $\varphi$ , and the ratio of Lucas to Fibonacci numbers approaches $\sqrt5$ : $\begin{align} \lim_{n \to \infty} \frac {F_{n+1}}{F_n} &= \lim_{n \to \infty} \frac{L_{n+1}}{L_n} = \varphi, & \lim_{n \to \infty} \frac {L_n}{F_n} &= \sqrt5. \end{align}$ Theorems about the Fibonac…
- Translator read: `sqrt(5)*N*phi**n`  =  `-5*(-1)**n`  · notes: pre:spacing
pre:style
mult_not_call:N
sides: \mathrm{N}(\varphi^n\sqrt5~\!)  ||  (-1)^n(-5)
- Assumptions: domains {'N': 'nonneg_integer', 'n': 'nonneg_integer', 'phi': 'real'}; constants {}; constraints ['Ne(n, 0)']
- Verifier: The identity fails at 60 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at N=0, n=1, phi=0.566636: lhs=0, rhs=5.000000000000).
- Counterexample: {'N': '0', 'n': '1', 'phi': '0.566636'} → lhs 0, rhs 5.00000000000000000000000000000000000000, rel diff 1.0000000000
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:12386:1378520549:28

- Page: [Golden ratio](https://en.wikipedia.org/wiki/Golden_ratio) › Calculation  · verdict **FAIL**, symbolic unknown
- LaTeX: `\frac{\frac{a}{b}+1}{\frac{a}{b}} = \frac{a}{b},`
- Context before: …ving it to be aesthetically pleasing. These uses often appear in the form of a golden rectangle. Calculation. Two non-zero quantities $a$ and $b$ are in the golden ratio $\varphi$ if $\frac{a+b}{a} = \frac{a}{b} = \varphi.$ To determine $\varphi$ as a number, we can divide the numerator and denominator of the fraction on the left-hand side by $b$ ,
- Context after: and then substitute $\tfrac{a}{b} = \varphi$ , to obtain $\frac{\varphi + 1}{\varphi} = \varphi.$ Multiplying both sides by $\varphi$ gives $\varphi + 1 = \varphi^2$ which can be rearranged to ${\varphi}^2 - \varphi - 1 = 0.$ The quadratic formula yields two solutions: $\frac{1 + \sqrt5}{2} = 1.618033\dots\$ and $\ \frac{1 - \sqrt5}{2} = -0.618033\…
- Translator read: `b*(a/b + 1)/a`  =  `a/b`  · notes: pre:trailing_punct
sides: \frac{\frac{a}{b}+1}{\frac{a}{b}}  ||  \frac{a}{b}
- Assumptions: domains {'a': 'real', 'b': 'real'}; constants {}; constraints ['Ne(a, 0)', 'Ne(b, 0)']
- Verifier: The identity fails at 60 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at a=0.0503741, b=0.131939: lhs=3.619183270768, rhs=0.381798406839).
- Counterexample: {'a': '0.0503741', 'b': '0.131939'} → lhs 3.61918327076811297869341586251665042154, rhs 0.38179840683952432563533147894102577706, rel diff 0.8945070259
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:19447:1378281957:466

- Page: [Group (mathematics)](https://en.wikipedia.org/wiki/Group_(mathematics)) › Examples and applications > Numbers > Rationals  · verdict **FAIL**, symbolic not_equal
- LaTeX: `x\cdot 0=1`
- Context before: …frac{a}{b}.$ Fractions of integers (with $b$ nonzero) are known as rational numbers. The set of all such irreducible fractions is commonly denoted $\Q$ . There is still a minor obstacle for $\left(\Q,\cdot\right)$ , the rationals with multiplication, being a group: because zero does not have a multiplicative inverse (i.e., there is no $x$ such that
- Context after: ), $\left(\Q,\cdot\right)$ is still not a group. However, the set of all nonzero rational numbers $\Q\smallsetminus\left\{0\right\}=\left\{q\in\Q\mid q\neq 0\right\}$ does form an abelian group under multiplication, also denoted $\Q^{\times}$ . Associativity and identity element axioms follow from the properties of integers. The closure requirement…
- Translator read: `0`  =  `1`  · notes: sides: x\cdot 0  ||  1
- Assumptions: domains {}; constants {}; constraints []
- Verifier: The constant identity does not hold: both sides differ beyond 1e-8 relative error, stably at two working precisions (lhs=0, rhs=1.0000000000000000).
- Counterexample: {} → lhs 0, rhs 1.00000000000000000000000000000000000000, rel diff 1.0000000000
- Regimes: constant 1/1 fail, 0 err

---
## wiki:en:24958527:1379424795:23

- Page: [Group testing](https://en.wikipedia.org/wiki/Group_testing) › History and development > Combinatorial group testing  · verdict **FAIL**, symbolic unknown
- LaTeX: `n/d \geq 38`
- Context before: …nary-splitting algorithm still produces near-optimal results, requiring at most $d - 1$ tests above the information lower bound where $d$ is the number of defectives. Considerable improvements to this were made in 2013 by Allemann, getting the required number of tests to less than $0.187d + 0.5\log_2(d) + 5.5$ above the information lower bound when
- Context after: and $d \geq 10$ . This was achieved by changing the binary search in the binary-splitting algorithm to a complex set of sub-algorithms with overlapping test groups. As such, the problem of adaptive combinatorial group testing – with a known number or upper bound on the number of defectives – has essentially been solved, with little room for further…
- Translator read: `n/d`  >=  `38`  · notes: sides: n/d  ||  38
- Assumptions: domains {'d': 'positive', 'n': 'nonneg_integer'}; constants {}; constraints ['d >= 10']
- Verifier: The inequality fails at 60 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at d=10, n=1: lhs=0.100000000000, rhs=38.00000000000).
- Counterexample: {'d': '10', 'n': '1'} → lhs 0.10000000000000000000000000000000000000, rhs 38.0000000000000000000000000000000000000, rel diff 0.9973684210
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:11503563:1225658876:20

- Page: [H-vector](https://en.wikipedia.org/wiki/H-vector) › Recurrence relation  · verdict **FAIL**, symbolic unknown
- LaTeX: `\textstyle h_{k} = h^{d}_{k}`
- Context before: …e $\textstyle h$ -vector $(h_{0}, h_{1}, \dotsc, h_{d})$ can be computed from the $\textstyle f$ -vector $(f_{-1}, f_{0}, \dotsc, f_{d-1})$ by using the recurrence relation $h^{i}_{0} = 1, \qquad -1 \le i \le d$ $h^{i}_{i+1} = f_{i}, \qquad -1 \le i \le d-1$ $h^{i}_{k} = h^{i-1}_{k} - h^{i-1}_{k-1}, \qquad 1 \le k \le i \le d$ . and finally setting
- Context after: for $\textstyle 0 \le k \le d$ . For small examples, one can use this method to compute $\textstyle h$ -vectors quickly by hand by recursively filling the entries of an array similar to Pascal's triangle. For example, consider the boundary complex $\textstyle \Delta$ of an octahedron. The $\textstyle f$ -vector of $\textstyle \Delta$ is $\textstyle…
- Translator read: `h_k`  =  `h_k**d`  · notes: pre:style
sides: h_{k}  ||  h^{d}_{k}
- Assumptions: domains {'d': 'positive', 'h_k': 'positive'}; constants {}; constraints []
- Verifier: The identity fails at 60 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at d=0.0729162, h_k=0.0580483: lhs=0.058048300000, rhs=0.812568960025).
- Counterexample: {'d': '0.0729162', 'h_k': '0.0580483'} → lhs 0.05804830000000000000000000000000000000, rhs 0.81256896002511609560756058487221343889, rel diff 0.9285620016
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:11503563:1225658876:19

- Page: [H-vector](https://en.wikipedia.org/wiki/H-vector) › Recurrence relation  · verdict **FAIL**, symbolic unknown
- LaTeX: `h^{i}_{k} = h^{i-1}_{k} - h^{i-1}_{k-1}, \qquad 1 \le k \le i \le d`
- Context before: …the h*-vector for a convex lattice polytope, see Ehrhart polynomial. Recurrence relation. The $\textstyle h$ -vector $(h_{0}, h_{1}, \dotsc, h_{d})$ can be computed from the $\textstyle f$ -vector $(f_{-1}, f_{0}, \dotsc, f_{d-1})$ by using the recurrence relation $h^{i}_{0} = 1, \qquad -1 \le i \le d$ $h^{i}_{i+1} = f_{i}, \qquad -1 \le i \le d-1$
- Context after: . and finally setting $\textstyle h_{k} = h^{d}_{k}$ for $\textstyle 0 \le k \le d$ . For small examples, one can use this method to compute $\textstyle h$ -vectors quickly by hand by recursively filling the entries of an array similar to Pascal's triangle. For example, consider the boundary complex $\textstyle \Delta$ of an octahedron. The $\texts…
- Translator read: `h_k**i`  =  `h_k**(i - 1) - h_{k-1}**(i - 1)`  · notes: pre:spacing
subscript_expr:h_{k-1}
cond: 1 \le k \le i \le d
hint:i_present
sides: h^{i}_{k}  ||  h^{i-1}_{k} - h^{i-1}_{k-1}
- Assumptions: domains {'h_k': 'positive', 'h_{k-1}': 'positive'}; constants {'i': 'I'}; constraints []
- Verifier: The identity fails at 60 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at h_k=0.109008, h_{k-1}=0.0537151: lhs=(-0.6016280100, rhs=(12.6588835594).
- Counterexample: {'h_k': '0.109008', 'h_{k-1}': '0.0537151'} → lhs (-0.601628010079860582410549888597852866, rhs (12.658883559431451882559352687125954657, rel diff 1.0314678513
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:238199:1377787289:27

- Page: [Henry's law](https://en.wikipedia.org/wiki/Henry's_law) › Fundamental types and variants of Henry's law constants > Henry's law solubility constants Hs > Henry solubility defined via aqueous-phase mixing ratio (Hsxp)  · verdict **FAIL**, symbolic unknown
- LaTeX: `H_\text{s}^{xp} = \frac{x}{p},`
- Context before: …ure. Sometimes, this dimensionless constant is called the water–air partitioning coefficient $K_\text{WA}$ . It is closely related to the various, slightly different definitions of the Ostwald coefficient $L$ , as discussed by Battino (1984). Henry solubility defined via aqueous-phase mixing ratio (Hsxp) . Another Henry's law solubility constant is
- Context after: where $x$ is the molar mixing ratio in the aqueous phase. For a dilute aqueous solution the conversion between $x$ and $c_\text{a}$ is where is the density of water, and is the molar mass of water. Thus The SI unit for $H_\text{s}^{xp}$ is Pa−1, although atm−1 is still frequently used. Henry solubility defined via molality (Hsbp) . It can be advant…
- Translator read: `H_s**(p*x)`  =  `x/p`  · notes: pre:trailing_punct
sides: H_\text{s}^{xp}  ||  \frac{x}{p}
- Assumptions: domains {'H_s': 'positive', 'p': 'positive', 'x': 'real'}; constants {}; constraints []
- Verifier: The identity fails at 59 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at H_s=0.0961159, p=0.140229, x=0.132455: lhs=0.957428621022, rhs=0.944562109121).
- Counterexample: {'H_s': '0.0961159', 'p': '0.140229', 'x': '0.132455'} → lhs 0.95742862102295482210108147489946336886, rhs 0.94456210912150838984803428677377717875, rel diff 0.0134386121
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 11/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:238199:1377787289:35

- Page: [Henry's law](https://en.wikipedia.org/wiki/Henry's_law) › Fundamental types and variants of Henry's law constants > Henry's law solubility constants Hs > Henry solubility defined via molality (Hsbp)  · verdict **FAIL**, symbolic unknown
- LaTeX: `H_\text{s}^{bp} = \frac{b}{p},`
- Context before: …sity of a solution and thus its volume are temperature-dependent. Defining the aqueous-phase composition via molality has the advantage that any temperature dependence of the Henry's law constant is a true solubility phenomenon and not introduced indirectly via a density change of the solution. Using molality, the Henry solubility can be defined as
- Context after: where $b$ is used as the symbol for molality (instead of $m$ ) to avoid confusion with the symbol $m$ for mass. The SI unit for $H_\text{s}^{bp}$ is mol/(kg·Pa). There is no simple way to calculate $H_\text{s}^{cp}$ from $H_\text{s}^{bp}$ , since the conversion between concentration $c_\text{a}$ and molality $b$ involves all solutes of a solution.…
- Translator read: `H_s**(b*p)`  =  `b/p`  · notes: pre:trailing_punct
sides: H_\text{s}^{bp}  ||  \frac{b}{p}
- Assumptions: domains {'H_s': 'positive', 'b': 'real', 'p': 'positive'}; constants {}; constraints []
- Verifier: The identity fails at 60 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at H_s=0.246946, b=0.170862, p=0.23962: lhs=0.944347728030, rhs=0.713054002170).
- Counterexample: {'H_s': '0.246946', 'b': '0.170862', 'p': '0.23962'} → lhs 0.94434772803071024932822550091329215746, rhs 0.71305400217010266254903597362490610132, rel diff 0.2449243207
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:238199:1377787289:65

- Page: [Henry's law](https://en.wikipedia.org/wiki/Henry's_law) › Fundamental types and variants of Henry's law constants > Henry's law volatility constants Hv > The Henry volatility defined via aqueous-phase mixing ratio (H)  · verdict **FAIL**, symbolic unknown
- LaTeX: `H_{\rm v}^{px} = \frac{p}{x} = \frac{1}{H_{\rm s}^{xp}}.`
- Context before: …efined via concentration (H) . A common way to define a Henry volatility is dividing the partial pressure by the aqueous-phase concentration: $H_{\rm v}^{pc} = \frac{p}{c_\text{a}} = \frac{1}{H_{\rm s}^{cp}}.$ The SI unit for $H_{\rm v}^{pc}$ is Pa·m3/mol. The Henry volatility defined via aqueous-phase mixing ratio (H) . Another Henry volatility is
- Context after: The SI unit for $H_{\rm v}^{px}$ is Pa. However, atm is still frequently used. The dimensionless Henry volatility H . The Henry volatility can also be expressed as the dimensionless ratio between the gas-phase concentration $c_\text{g}$ of a species and its aqueous-phase concentration $c_\text{a}$ : $H_{\rm v}^{cc} = \frac{c_\text{g}}{c_\text{a}} =…
- Translator read (piece 0): `H_v**(p*x)`  =  `p/x`  · notes: pre:trailing_punct
sides: H_{\rm v}^{px}  ||  \frac{p}{x}
- Translator read (piece 1): `p/x`  =  `H_s**(-p*x)`  · notes: pre:trailing_punct
sides: \frac{p}{x}  ||  \frac{1}{H_{\rm s}^{xp}}
- Assumptions: domains {'H_s': 'positive', 'H_v': 'positive', 'p': 'positive', 'x': 'real'}; constants {}; constraints ['Ne(x, 0)']
- Verifier: Chain link 0: The identity fails at 60 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at H_v=0.0657255, p=0.0939978, x=0.0985271: lhs=0.975103337104, rhs=0.954029906492).
- Counterexample: {'H_v': '0.0657255', 'p': '0.0939978', 'x': '0.0985271'} → lhs 0.97510333710432041598263084110714488635, rhs 0.95402990649273144140038628966040815166, rel diff 0.0216114844
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:238199:1377787289:73

- Page: [Henry's law](https://en.wikipedia.org/wiki/Henry's_law) › Values of Henry's law constants  · verdict **FAIL**, symbolic unknown
- LaTeX: `H_{\rm v}^{px} = \frac{p}{x}`
- Context before: …ter partitioning coefficient $K_\text{AW}$ . Values of Henry's law constants. A large compilation of Henry's law constants has been published by Sander (2023). A few selected values are shown in the table below: + Henry's law constants (gases in water at 298.15 K) Gas $H_{\rm v}^{pc} = \frac{p}{c_\text{aq}}$ $H_{\rm s}^{cp} = \frac{c_\text{aq}}{p}$
- Context after: $H_{\rm s}^{cc} = \frac{c_\text{aq}}{c_\text{gas}}$ $\left(\frac{\text{L} \cdot \text{atm}}{\text{mol}}\right)$ $\left(\frac{\text{mol}}{\text{L} \cdot \text{atm}}\right)$ $\left(\text{atm}\right)$ (dimensionless) O2 770 1.3 4.3 3.2 H2 1300 7.8 7.1 1.9 CO2 29 3.4 1.6 8.3 N2 1600 6.1 9.1 1.5 He 2700 3.7 1.5 9.1 Ne 2200 4.5 1.2 1.1 Ar 710 1.4 4.0 3.4…
- Translator read: `H_v**(p*x)`  =  `p/x`  · notes: sides: H_{\rm v}^{px}  ||  \frac{p}{x}
- Assumptions: domains {'H_v': 'positive', 'p': 'positive', 'x': 'real'}; constants {}; constraints ['Ne(x, 0)']
- Verifier: The identity fails at 60 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at H_v=0.129406, p=0.118373, x=0.181044: lhs=0.957124740661, rhs=0.653835531693).
- Counterexample: {'H_v': '0.129406', 'p': '0.118373', 'x': '0.181044'} → lhs 0.95712474066159695199806580259980182409, rhs 0.65383553169395285124058239985859790990, rel diff 0.3168753205
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:20556903:1378902473:2

- Page: [Higgs boson](https://en.wikipedia.org/wiki/Higgs_boson) › History > Theorisation  · verdict **FAIL**, symbolic not_equal
- LaTeX: `\mu^2 < 0`
- Context before: …iggs mechanism could be used to break the electroweak symmetry of Sheldon Glashow's unified model for the weak and electromagnetic interactions, (itself an extension of work by Schwinger), forming what became the Standard Model of particle physics. Weinberg was the first to observe that this would also provide mass terms for the fermions. [efn | 1]
- Context after: At first, these seminal papers on spontaneous breaking of gauge symmetries were largely ignored, because it was widely believed that the (non-Abelian gauge) theories in question were a dead-end, and in particular that they could not be renormalised. In 1971–72, Martinus Veltman and Gerard 't Hooft proved renormalisation of Yang–Mills was possible i…
- Translator read: `mu**2`  <  `0`  · notes: sides: \mu^2  ||  0
- Assumptions: domains {'mu': 'positive'}; constants {}; constraints []
- Verifier: The inequality fails at 60 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at mu=0.0431047: lhs=0.001858015162, rhs=0).
- Counterexample: {'mu': '0.0431047'} → lhs 0.00185801516209000000000000000000000000, rhs 0, rel diff 1.0000000000
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:20598932:1381119901:6

- Page: [Hilbert space](https://en.wikipedia.org/wiki/Hilbert_space) › Definition and illustration > Motivating example: Euclidean vector space  · verdict **FAIL**, symbolic unknown
- LaTeX: `|z|^2 = z\overline{z} \,.`
- Context before: …the completeness of Euclidean space: that a series that converges absolutely also converges in the ordinary sense. Hilbert spaces are often taken over the complex numbers. The complex plane denoted by C is equipped with a notion of magnitude, the complex modulus z , which is defined as the square root of the product of z with its complex conjugate:
- Context after: If is a decomposition of z into its real and imaginary parts, then the modulus is the usual Euclidean two-dimensional length: $|z| = \sqrt{x^2 + y^2} \,.$ The inner product of a pair of complex numbers z and w is the product of z with the complex conjugate of w: $\langle z, w\rangle = z\overline{w}\,.$ This is complex-valued. The real part of ⟨z, w…
- Translator read: `Abs(z)**2`  =  `z*z_bar`  · notes: pre:spacing
pre:trailing_punct
ambig:bar:z_bar
sides: |z|^2  ||  z\overline{z}
- Assumptions: domains {'z': 'complex', 'z_bar': 'complex'}; constants {}; constraints []
- Verifier: The identity fails at 71 of 72 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, complex, large) (e.g. at z=0.0558678, z_bar=0.070551: lhs=0.003121211076, rhs=0.003941529157).
- Counterexample: {'z': '0.0558678', 'z_bar': '0.070551'} → lhs 0.00312121107684000000000000000000000000, rhs 0.00394152915780000000000000000000000000, rel diff 0.2081217842
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 11/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, complex 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:574024:1378540896:59

- Page: [Hilbert transform](https://en.wikipedia.org/wiki/Hilbert_transform) › Properties > Inverse transform  · verdict **FAIL**, symbolic unknown
- LaTeX: `\operatorname{H}^{-1} = -\operatorname{H}`
- Context before: …L^q(\mathbb{R})$ . Inverse transform. The Hilbert transform is an anti-involution, meaning that $\operatorname{H}\bigl(\operatorname{H}\left(u\right)\bigr) = -u$ provided each transform is well-defined. Since H preserves the space $L^p(\mathbb{R})$ , this implies in particular that the Hilbert transform is invertible on $L^p(\mathbb{R})$ , and that
- Context after: Complex structure. Because ("I" is the identity operator) on the real Banach space of real-valued functions in $L^p(\mathbb{R})$ , the Hilbert transform defines a linear complex structure on this Banach space. In particular, when , the Hilbert transform gives the Hilbert space of real-valued functions in $L^2(\mathbb{R})$ the structure of a complex…
- Translator read: `1/H`  =  `-H`  · notes: sides: \operatorname{H}^{-1}  ||  -\operatorname{H}
- Assumptions: domains {'H': 'positive'}; constants {}; constraints []
- Verifier: The identity fails at 60 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at H=0.0652033: lhs=15.33664707154, rhs=-0.06520330000).
- Counterexample: {'H': '0.0652033'} → lhs 15.3366470715439249240452553781787118136, rhs -0.0652033000000000000000000000000000000, rel diff 1.0042514703
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:2336224:1364361992:4

- Page: [Hilbert's eighteenth problem](https://en.wikipedia.org/wiki/Hilbert's_eighteenth_problem) › Third question: densest sphere packing  · verdict **FAIL**, symbolic not_equal
- LaTeX: `\frac{\pi}{3\sqrt{2}} = 0.74048.`
- Context before: …eres, it is generally taken as equivalent to the Kepler conjecture. The conjecture was named after 17th-century German mathematician Johannes Kepler in his booklet titled Strena, seu, de Nieu Sexangula. It states that the packing of equal volume spheres has a density greater than the packing of the face-centered cubic arrangement. Such a density is
- Context after: In 1998, American mathematician Thomas Callister Hales gave a computer-aided proof of the Kepler conjecture. It shows that the most space-efficient way to pack spheres is in a pyramid shape. References.…
- Translator read: `sqrt(2)*pi/6`  =  `2314/3125`  · notes: pre:trailing_punct
sides: \frac{\pi}{3\sqrt{2}}  ||  0.74048
- Assumptions: domains {}; constants {}; constraints []
- Verifier: The constant identity does not hold: both sides differ beyond 1e-8 relative error, stably at two working precisions (lhs=0.7404804896930610, rhs=0.7404800000000000).
- Counterexample: {} → lhs 0.74048048969306104116931349834344894976, rhs 0.74048000000000000000000000000000000000, rel diff 0.0000006613
- Regimes: constant 1/1 fail, 0 err

---
## wiki:en:229553:1375736650:37

- Page: [Hooke's law](https://en.wikipedia.org/wiki/Hooke's_law) › Linear elasticity theory for continuous media > Isotropic materials  · verdict **FAIL**, symbolic unknown
- LaTeX: `\sigma_1 = \frac{E}{1+\nu}\varepsilon_1 + \frac{\nu}{1+\nu}(\sigma_1+\sigma_2+\sigma_3)\,.`
- Context before: …where E is Young's modulus and ν is Poisson's ratio. (See 3-D elasticity). [math proof | proof]
- Context after: In matrix form, Hooke's law for isotropic materials can be written as…
- Translator read: `sigma_1`  =  `E*epsilon_1/(nu + 1) + nu*(sigma_1 + sigma_2 + sigma_3)/(nu + 1)`  · notes: pre:spacing
pre:trailing_punct
sides: \sigma_1  ||  \frac{E}{1+\nu}\varepsilon_1 + \frac{\nu}{1+\nu}(\sigma_1+\sigma_2+\sigma_3)
- Assumptions: domains {'E': 'positive', 'epsilon_1': 'positive', 'nu': 'positive', 'sigma_1': 'positive', 'sigma_2': 'positive', 'sigma_3': 'positive'}; constants {}; constraints []
- Verifier: The identity fails at 60 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at E=0.243913, epsilon_1=0.370754, nu=0.364337, sigma_1=0.266247, sigma_2=0.219451, sigma_3=0.615447: lhs=0.266247000000, rhs=0.360335889349).
- Counterexample: {'E': '0.243913', 'epsilon_1': '0.370754', 'nu': '0.364337', 'sigma_1': '0.266247', 'sigma_2': '0.219451', 'sigma_3': '0.615447'} → lhs 0.26624700000000000000000000000000000000, rhs 0.36033588934918572170951898248013503994, rel diff 0.2611143994
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:325714:1361162854:17

- Page: [Hopf algebra](https://en.wikipedia.org/wiki/Hopf_algebra) › Formal definition > Structure constants  · verdict **FAIL**, symbolic unknown
- LaTeX: `\nu_k^{\;ij}\nu_i^{\;mn}=\nu_k^{\;mi}\nu_i^{\;nj}`
- Context before: …gebra in terms of structure constants for multiplication: $e_i\nabla e_j = \sum_k \mu^k_{\;ij} e_k$ for co-multiplication: $\Delta e_i = \sum_{j,k} \nu^{\;jk}_i e_j\otimes e_k$ and the antipode: $S e_i = \sum_j \tau_i^{\;j} e_j$ Associativity then requires that $\mu^k_{\;ij}\mu^m_{\;kn}=\mu^k_{\;jn}\mu^m_{\;ik}$ while co-associativity requires that
- Context after: The connecting axiom requires that $\nu_k^{\;ij}\tau_j^{\;m}\mu^n_{\;im}=\nu_k^{\;jm}\tau_j^{\,\;i}\mu^n_{\;im}$ Properties of the antipode. The antipode S is sometimes required to have a K-linear inverse, which is automatic in the finite-dimensional case, or if H is commutative or cocommutative (or more generally quasitriangular). In general, S is…
- Translator read: `nu_i**(m*n)*nu_k**(i*j)`  =  `nu_i**(j*n)*nu_k**(i*m)`  · notes: pre:spacing
hint:i_present
sides: \nu_k^{\;ij}\nu_i^{\;mn}  ||  \nu_k^{\;mi}\nu_i^{\;nj}
- Assumptions: domains {'i': 'nonneg_integer', 'j': 'nonneg_integer', 'm': 'nonneg_integer', 'n': 'nonneg_integer', 'nu_i': 'positive', 'nu_k': 'positive'}; constants {}; constraints []
- Verifier: The identity fails at 53 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at i=1, j=0, m=2, n=1, nu_i=0.509732, nu_k=0.140373: lhs=0.259826711824, rhs=0.019704579129).
- Counterexample: {'i': '1', 'j': '0', 'm': '2', 'n': '1', 'nu_i': '0.509732', 'nu_k': '0.140373'} → lhs 0.25982671182400000000000000000000000000, rhs 0.01970457912900000000000000000000000000, rel diff 0.9241626121
- Regimes: small_positive 11/12 fail, 0 err, unit_interval 9/12 fail, 0 err, integers_small 11/12 fail, 0 err, mixed_sign 10/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:1170097:1377477270:155

- Page: [Hopfield network](https://en.wikipedia.org/wiki/Hopfield_network) › Dense associative memory or modern Hopfield network > Hierarchical associative memory network  · verdict **FAIL**, symbolic not_equal
- LaTeX: `g_i^0 =0, \ \ \ \ \ \text{and}\ \ \ \ \ g_i^{N_\text{layer}+1}=0`
- Context before: …the same as the order of the lower indices, in the example above this means that the index $i$ enumerates neurons in the layer $A$ , and index $j$ enumerates neurons in the layer $B$ ). The feedforward weights and the feedback weights are equal. The dynamical equations for the neurons' states can be written as with boundary conditions [NumBlk2 | 2]
- Context after: The main difference between these equations and those from the conventional feedforward networks is the presence of the second term, which is responsible for the feedback from higher layers. These top-down signals help neurons in lower layers to decide on their response to the presented stimuli. Following the general recipe it is convenient to intr…
- Translator read: `1`  =  `0`  · notes: pre:spacing
cond: g_i^{N_\text{layer}+1}=0
sides: g_i^0  ||  0
- Assumptions: domains {}; constants {}; constraints []
- Verifier: The constant identity does not hold: both sides differ beyond 1e-8 relative error, stably at two working precisions (lhs=1.0000000000000000, rhs=0).
- Counterexample: {} → lhs 1.00000000000000000000000000000000000000, rhs 0, rel diff 1.0000000000
- Regimes: constant 1/1 fail, 0 err

---
## wiki:en:51438:1378320581:39

- Page: [Hypercomplex number](https://en.wikipedia.org/wiki/Hypercomplex_number) › Two-dimensional real algebras  · verdict **FAIL**, symbolic not_equal
- LaTeX: `\tilde u^2<0`
- Context before: …lde u^2>0$ . This leads to the split-complex numbers, which have normalized basis $\{ 1 , ~j \}$ with $j^2 = +1$ . To obtain $j$ from $\tilde u$ , the latter must be divided by the positive real number $\textstyle a \mathrel{:=} \sqrt{a_0 + \frac{1}{4}a_1^2}$ , which has the same square as $\tilde u$ has. If $4a_0<-a_1^2$ , the above formula yields
- Context after: . This leads to the complex numbers, which have normalized basis $\{ 1 , ~i \}$ with $i^2 = -1$ . To yield $i$ from $\tilde u$ , the latter has to be divided by the positive real number $\textstyle a \mathrel{:=} \sqrt{-(a_0 + \frac{1}{4}a_1^2)}$ , which squares to the negative of $\tilde u^2$ . The complex numbers are the only quadratic algebra th…
- Translator read: `u_tilde**2`  <  `0`  · notes: sides: \tilde u^2  ||  0
- Assumptions: domains {'u_tilde': 'positive'}; constants {}; constraints []
- Verifier: The inequality fails at 59 of 59 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at u_tilde=0.0583643: lhs=0.003406391514, rhs=0).
- Counterexample: {'u_tilde': '0.0583643'} → lhs 0.00340639151449000000000000000000000000, rhs 0, rel diff 1.0000000000
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 11/11 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:3486002:1374081047:332

- Page: [Implementation of mathematics in set theory](https://en.wikipedia.org/wiki/Implementation_of_mathematics_in_set_theory) › Cardinal numbers  · verdict **FAIL**, symbolic unknown
- LaTeX: `|V|\cdot |V| = |V|`
- Context before: …ncouragement to the view that the "standard" cardinalities in NFU are the cantorian (indeed, the strongly cantorian) cardinalities, just as the "standard" ordinals seem to be the strongly cantorian ordinals. Now the usual theorems of cardinal arithmetic with the axiom of choice can be proved, including $\kappa \cdot \kappa = \kappa$ . From the case
- Context after: the existence of a type level ordered pair can be derived: $|V| \cdot |V| = T^{-2}(|V \times V|)$ is equal to $|V|$ just in case $|V \times V| = T^2(|V|) = |P_1^2(V)|$ , which would be witnessed by a one-to-one correspondence between Kuratowski pairs $(a,b)$ and double singletons $\{\{c\}\}$ : redefine $(a,b)$ as the c such that $\{\{c\}\}$ is asso…
- Translator read: `Abs(V)**2`  =  `Abs(V)`  · notes: sides: |V|\cdot |V|  ||  |V|
- Assumptions: domains {'V': 'positive'}; constants {}; constraints []
- Verifier: The identity fails at 59 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at V=0.0169116: lhs=0.000286002214, rhs=0.016911600000).
- Counterexample: {'V': '0.0169116'} → lhs 0.00028600221456000000000000000000000000, rhs 0.01691160000000000000000000000000000000, rel diff 0.9830884000
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 11/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:473775:1372217072:54

- Page: [Injective module](https://en.wikipedia.org/wiki/Injective_module) › Examples > Artinian examples > Computing injective hulls  · verdict **FAIL**, symbolic unknown
- LaTeX: `E = E(R/\mathfrak{p})`
- Context before: …haps even simpler: a prime ideal is an annihilator of a unique simple module, and the corresponding indecomposable injective module is its injective hull. For finite-dimensional algebras over fields, these injective hulls are finitely-generated modules . Computing injective hulls. If $R$ is a Noetherian ring and $\mathfrak{p}$ is a prime ideal, set
- Context after: as the injective hull. The injective hull of $R/\mathfrak{p}$ over the Artinian ring $R/\mathfrak{p}^k$ can be computed as the module $(0:_E\mathfrak{p}^k)$ . It is a module of the same length as $R/\mathfrak{p}^k$ . In particular, for the standard graded ring $R_\bullet = k[x_1,\ldots,x_n]_\bullet$ and $\mathfrak{p}=(x_1,\ldots, x_n)$ , $E = \oplu…
- Translator read: `E`  =  `E*R/frak_p`  · notes: mult_not_call:E
styled_symbol:frak_p
sides: E  ||  E(R/\mathfrak{p})
- Assumptions: domains {'E': 'positive', 'R': 'positive', 'frak_p': 'positive'}; constants {}; constraints []
- Verifier: The identity fails at 60 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at E=0.254135, R=0.0726565, frak_p=0.133105: lhs=0.254135000000, rhs=0.138721758217).
- Counterexample: {'E': '0.254135', 'R': '0.0726565', 'frak_p': '0.133105'} → lhs 0.25413500000000000000000000000000000000, rhs 0.13872175821719694977649224296607941099, rel diff 0.4541414672
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:27430123:1372869378:185

- Page: [Integer triangle](https://en.wikipedia.org/wiki/Integer_triangle) › Integer triangles with specific angle properties > Integer triangles with one angle with a given rational cosine > Integer triangles with a 60° angle (angles in arithmetic progression)  · verdict **FAIL**, symbolic not_equal
- LaTeX: `\gcd(a,b,c) = 3`
- Context before: …e of 60° is opposite to the side of length a). From here, all primitive solutions can be obtained by dividing a, b, and c by their greatest common divisor (e.g. an equilateral triangle solution is obtained by taking and , but this produces a = b = c = 3, which is not a primitive solution). See also More precisely, If $m \equiv -n \!\pmod{3}$ , then
- Context after: , otherwise $\gcd(a,b,c) = 1$ . Two different pairs $(m, n)$ and $(m, m-n)$ generate the same triple. Unfortunately the two pairs can both have a gcd of 3, so we can't avoid duplicates by simply skipping that case. Instead, duplicates can be avoided by $n$ going only till $m/2$ . We still need to divide by 3 if the gcd is 3. The only solution for $…
- Translator read: `1`  =  `3`  · notes: sides: \gcd(a,b,c)  ||  3
- Assumptions: domains {}; constants {}; constraints []
- Verifier: The constant identity does not hold: both sides differ beyond 1e-8 relative error, stably at two working precisions (lhs=1.0000000000000000, rhs=3.0000000000000000).
- Counterexample: {} → lhs 1.00000000000000000000000000000000000000, rhs 3.00000000000000000000000000000000000000, rel diff 0.6666666666
- Regimes: constant 1/1 fail, 0 err
