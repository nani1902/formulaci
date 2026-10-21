# Review batch 003 — 22 items

For each item answer with one JSON line (Finding schema): {"formula_id": ..., "verdict": "FAIL", "review": {"status": "confirmed_error"|"false_positive"|"ambiguous", "reviewer": "<name>", "notes": "<why, one or two sentences>"}, "suggested_fix": "<corrected LaTeX or null>", "evidence": "<independent source or derivation>"}


---
## wiki:en:9697733:1342756400:238

- Page: [Contact mechanics](https://en.wikipedia.org/wiki/Contact_mechanics) › Adhesive contact between elastic bodies > Maugis–Dugdale model of elastic contact  · verdict **FAIL**, symbolic unknown
- LaTeX: `F = F^H + F^D`
- Context before: …compression due to Dugdale adhesion is $d^D = -\left(\frac{2\sigma_0 a}{E^*}\right)\sqrt{m^2-1}$ and the gap at $r = c$ is $h^D(c) = \left(\frac{4\sigma_0 a}{\pi E^*}\right)\left[\sqrt{m^2 - 1}\cos^{-1}\left(\frac{1}{m}\right) + 1 - m\right]$ The net traction on the contact area is then given by $p(r) = p^H(r) + p^D(r)$ and the net contact force is
- Context after: . When $h(c) = h^H(c) + h^D(c) = h_0$ the adhesive traction drops to zero. Non-dimensionalized values of $a, c, F, d$ are introduced at this stage that are defied as $\bar{a} = \alpha a ~;~~ \bar{c} := \alpha c ~;~~ \bar{d} := \alpha^2 Rd ~;~~ \alpha := \left(\frac{4E^*}{3\pi\Delta\gamma R^2}\right)^\frac{1}{3} ~;~~ \bar{A} := \pi c^2 ~;~~ \bar{F}…
- Translator read: `F`  =  `F**D + F**H`  · notes: sides: F  ||  F^H + F^D
- Assumptions: domains {'D': 'positive', 'F': 'positive', 'H': 'positive'}; constants {}; constraints []
- Verifier: The identity fails at 60 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at D=0.354086, F=0.233143, H=0.270635: lhs=0.233143000000, rhs=1.271455849522).
- Counterexample: {'D': '0.354086', 'F': '0.233143', 'H': '0.270635'} → lhs 0.23314300000000000000000000000000000000, rhs 1.27145584952259518086964942955215190503, rel diff 0.8166330352
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:297004:1378871712:25

- Page: [Coxeter group](https://en.wikipedia.org/wiki/Coxeter_group) › Definition  · verdict **FAIL**, symbolic unknown
- LaTeX: `r_i = r_i^{-1}`
- Context before: …relation $m_{ii} = 1$ means that $(r_ir_i)^1 = (r_i)^2 = 1$ for all $i$ ; as such the generators are involutions. If $m_{ij} = 2$ , then the generators $r_i$ and $r_j$ commute. This follows by observing that $xx = yy = 1$ , together with $xyxy = 1$ implies that $xy = x(xyxy)y = (xx)yx(yy) = yx$ . Alternatively, since the generators are involutions,
- Context after: , so $1 =(r_ir_j)^2=r_ir_jr_ir_j=r_ir_jr_i^{-1}r_j^{-1}$ . That is to say, the commutator of $r_i$ and $r_j$ is equal to 1, or equivalently that $r_i$ and $r_j$ commute. The reason that $m_{ij} = m_{ji}$ for $i \neq j$ is stipulated in the definition is that $yy = 1$ , together with $(xy)^m = 1$ already implies that $(yx)^m = (yx)^myy = y(xy)^my =…
- Translator read: `r_i`  =  `1/r_i`  · notes: sides: r_i  ||  r_i^{-1}
- Assumptions: domains {'r_i': 'nonneg'}; constants {}; constraints ['Ne(r_i, 0)']
- Verifier: The identity fails at 59 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at r_i=0.0864683: lhs=0.086468300000, rhs=11.56493188833).
- Counterexample: {'r_i': '0.0864683'} → lhs 0.08646830000000000000000000000000000000, rhs 11.5649318883336436590056702861048499854, rel diff 0.9925232330
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 11/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:180787:1381153688:37

- Page: [Cubic equation](https://en.wikipedia.org/wiki/Cubic_equation) › Discriminant and nature of the roots > Multiple root  · verdict **FAIL**, symbolic unknown
- LaTeX: `t^3 + p t + q = \left(t - \frac{3q}{p}\right)\left(t + \frac{3q}{2p}\right)^2.`
- Context before: …real, then all of its roots are real. The discriminant of the depressed cubic $t^3 + p t + q$ is zero if $4p^3 + 27q^2 = 0.$ If p is also zero, then p = q = 0 , and 0 is a triple root of the cubic. If $4p^3 + 27q^2 = 0,$ and p ≠ 0 , then the cubic has a simple root $t_1 = \frac{3q}{p}$ and a double root $t_2 = t_3 = -\frac{3q}{2p}.$ In other words,
- Context after: This result can be proved by expanding the latter product or retrieved by solving the rather simple system of equations resulting from Vieta's formulas. By using the reduction of a depressed cubic, these results can be extended to the general cubic. This gives: If the discriminant of the cubic $ax^3 + b x^2 + c x + d$ is zero, then either, if $b^2…
- Translator read: `p*t + q + t**3`  =  `(t - 3*q/p)*(t + 3*q/(2*p))**2`  · notes: pre:left_right
pre:trailing_punct
sides: t^3 + p t + q  ||  (t - \frac{3q}{p}\right)\left(t + \frac{3q}{2p}\right)^2
- Assumptions: domains {'p': 'positive', 'q': 'positive', 't': 'real'}; constants {}; constraints ['Ne(p, 0)']
- Verifier: The identity fails at 60 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at p=0.307486, q=0.326778, t=0.0858779: lhs=0.353817602649, rhs=-8.75594995370).
- Counterexample: {'p': '0.307486', 'q': '0.326778', 't': '0.0858779'} → lhs 0.35381760264914946313900000000000000000, rhs -8.7559499537096410925941427403217602613, rel diff 1.0404088196
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:180787:1381153688:56

- Page: [Cubic equation](https://en.wikipedia.org/wiki/Cubic_equation) › Cardano's formula  · verdict **FAIL**, symbolic not_equal
- LaTeX: `4p^3+27q^2 < 0,`
- Context before: …mitive cube root of unity $\varepsilon_1=\frac{-1+i\sqrt 3} 2,$ and the other cube root by the other primitive cube root of unity $\varepsilon_2=\varepsilon_1^2=\frac{-1-i\sqrt 3} 2.$ That is, the other roots of the equation are $\varepsilon_1\sqrt[3]{u_1}+\varepsilon_2 \sqrt[3]{u_2}$ and $\varepsilon_2\sqrt[3]{u_1}+\varepsilon_1 \sqrt[3]{u_2}.$ If
- Context after: there are three real roots, but Galois theory allows proving that, if there is no rational root, the roots cannot be expressed by an algebraic expression involving only real numbers. Therefore, the equation cannot be solved in this case with the knowledge of Cardano's time. This case has thus been called casus irreducibilis, meaning irreducible cas…
- Translator read: `4*p**3 + 27*q**2`  <  `0`  · notes: pre:trailing_punct
sides: 4p^3+27q^2  ||  0
- Assumptions: domains {'p': 'positive', 'q': 'positive'}; constants {}; constraints []
- Verifier: The inequality fails at 60 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at p=0.0518564, q=0.0596653: lhs=0.096676381973, rhs=0).
- Counterexample: {'p': '0.0518564', 'q': '0.0596653'} → lhs 0.09667638197326436057600000000000000000, rhs 0, rel diff 1.0000000000
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:180787:1381153688:103

- Page: [Cubic equation](https://en.wikipedia.org/wiki/Cubic_equation) › Trigonometric and hyperbolic solutions > Trigonometric solution for three real roots  · verdict **FAIL**, symbolic not_equal
- LaTeX: `4p^3 + 27q^2 < 0`
- Context before: …sines. More precisely, the roots of the depressed cubic $t^3 + pt + q = 0$ are $t_k = 2\,\sqrt{-\frac{p}{3}}\,\cos\left[\,\frac{1}{3} \arccos\left(\frac{3q}{2p}\sqrt{\frac{-3}{p}}\,\right) - \frac{2\pi k}{3}\,\right] \qquad \text{for } k=0,1,2.$ This formula is due to François Viète. It is purely real when the equation has three real roots (that is
- Context after: ). Otherwise, it is still correct but involves complex cosines and arccosines when there is only one real root, and it is nonsensical (division by zero) when p = 0. This formula can be straightforwardly transformed into a formula for the roots of a general cubic equation, using the back-substitution described in . The formula can be proved as follo…
- Translator read: `4*p**3 + 27*q**2`  <  `0`  · notes: sides: 4p^3 + 27q^2  ||  0
- Assumptions: domains {'p': 'positive', 'q': 'positive'}; constants {}; constraints []
- Verifier: The inequality fails at 60 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at p=0.0585457, q=0.110273: lhs=0.329126317011, rhs=0).
- Counterexample: {'p': '0.0585457', 'q': '0.110273'} → lhs 0.32912631701140175597200000000000000000, rhs 0, rel diff 1.0000000000
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:180787:1381153688:134

- Page: [Cubic equation](https://en.wikipedia.org/wiki/Cubic_equation) › Derivation of the roots > Cardano's method  · verdict **FAIL**, symbolic not_equal
- LaTeX: `4p^3+27q^2 < 0,`
- Context before: …ac {q^2}{4} +\frac {p^3}{27}}}.$ As $u+v=t,$ the sum of the cube roots of these solutions is a root of the equation. That is $t=\sqrt[3]{-{q\over 2}+\sqrt{{q^{2}\over 4}+{p^{3}\over 27}}} +\sqrt[3]{-{q\over 2}-\sqrt{{q^{2}\over 4}+{p^{3}\over 27}}}$ is a root of the equation; this is Cardano's formula. This works well when $4p^3+27q^2 > 0,$ but, if
- Context after: the square root appearing in the formula is not real. As a complex number has three cube roots, using Cardano's formula without care would provide nine roots, while a cubic equation cannot have more than three roots. This was clarified first by Rafael Bombelli in his book L'Algebra (1572). The solution is to use the fact that $uv=-\frac p3,$ that i…
- Translator read: `4*p**3 + 27*q**2`  <  `0`  · notes: pre:trailing_punct
sides: 4p^3+27q^2  ||  0
- Assumptions: domains {'p': 'positive', 'q': 'positive'}; constants {}; constraints []
- Verifier: The inequality fails at 60 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at p=0.0705278, q=0.0502893: lhs=0.069686638980, rhs=0).
- Counterexample: {'p': '0.0705278', 'q': '0.0502893'} → lhs 0.06968663898053857980800000000000000000, rhs 0, rel diff 1.0000000000
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:33034771:1252888468:28

- Page: [Defining equation (physical chemistry)](https://en.wikipedia.org/wiki/Defining_equation_(physical_chemistry)) › Kinetics and equilibria  · verdict **FAIL**, symbolic unknown
- LaTeX: `\mathrm{p} K = -\log_{10} K`
- Context before: …Pa(S1) ([M] [L]−1 [T]−2)(S1) Logarithm of any equilibrium constant pKc $\mathrm{p} K_c = -\log_{10} K_c = \sum_{j=1}^p \eta_j \log_{10} \left [ \mathrm{Y}_j \right ] - \sum_{i=1}^r \nu_i \log_{10} \left [ \mathrm{X}_i \right ]$ dimensionless dimensionless Logarithm of dissociation constant pK
- Context after: dimensionless dimensionless Logarithm of hydrogen ion (H+) activity, pH pH $\mathrm{pH} = -\log_{10} [\mathrm{H}^+]$ dimensionless dimensionless Logarithm of hydroxide ion (OH−) activity, pOH pOH $\mathrm{pOH} = -\log_{10} [\mathrm{OH}^{-}]$ dimensionless dimensionless Electrochemistry. Notation for half-reaction standard electrode potentials is as…
- Translator read: `K*p`  =  `-log(K)/log(10)`  · notes: log_base_given
sides: \mathrm{p} K  ||  -\log_{10} K
- Assumptions: domains {'K': 'positive', 'p': 'positive'}; constants {}; constraints []
- Verifier: The identity fails at 60 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at K=0.0854311, p=0.131418: lhs=0.011227184299, rhs=1.068384001680).
- Counterexample: {'K': '0.0854311', 'p': '0.131418'} → lhs 0.01122718429980000000000000000000000000, rhs 1.06838400168041238933546925998744724899, rel diff 0.9894914335
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:44135401:1324299460:39

- Page: [Derivative of the exponential map](https://en.wikipedia.org/wiki/Derivative_of_the_exponential_map) › Applications > Combinatoric details  · verdict **FAIL**, symbolic unknown
- LaTeX: `\log(A) = \sum_{k = 1}^\infty \frac{(-1)^{k + 1}}{k}{(A - I)}^k,\quad \text{and}\quad e^X = \sum_{k = 0}^\infty \frac{X^k}{k!}`
- Context before: …d expand $\frac{dZ}{dt} = \sum_{k = 0}^\infty \frac{(-1)^{k}}{k + 1}\left\{\left(e^{\mathrm{ad}_{tX}}e^{\mathrm{ad}_{tY}} - 1\right)^kX + \left(e^{\mathrm{ad}_{tX}}e^{\mathrm{ad}_{tY}} - 1\right)^ke^{\mathrm{ad}_{tX}}Y\right\}$ in a power series. To handle the series expansions simply, consider first . The log-series and the exp-series are given by
- Context after: respectively. Combining these one obtains $\log\left(e^X e^Y\right) = \sum_{k = 1}^\infty \frac{(-1)^{k + 1}}{k}{\left(e^Xe^Y - I\right)}^k = \sum_{k = 1}^\infty \frac{(-1)^{k + 1}}{k}\left({\sum_{i = 0}^\infty \frac{X^i}{i!}\sum_{j = 0}^\infty \frac{Y^j}{j!} - I}\right)^k = \sum_{k = 1}^\infty \frac{(-1)^{k + 1}}{k} \left(\sum_{i,j \ge 0, i + j >…
- Translator read: `log(A)`  =  `Sum((-1)**(k + 1)*(A - I)**k/k, (k, 1, oo))`  · notes: pre:spacing
log:unspecified_base
cond: e^X = \sum_{k = 0}^\infty \frac{X^k}{k!}
sides: \log(A)  ||  \sum_{k = 1}^\infty \frac{(-1)^{k + 1}}{k}{(A - I)}^k
- Assumptions: domains {'A': 'positive', 'I': 'positive'}; constants {}; constraints []
- Verifier: The identity fails at 23 of 23 evaluable points, a clear majority in every regime (small_positive, unit_interval, mixed_sign) (e.g. at A=0.150313, I=0.0589521: lhs=-1.89503549228, rhs=0.087425449583).
- Counterexample: {'A': '0.150313', 'I': '0.0589521'} → lhs -1.8950354922842627986503023356076353407, rhs 0.08742544958307300790648708101336666636, rel diff 1.0461339378
- Regimes: small_positive 6/13 fail, 7 err, unit_interval 6/6 fail, 0 err, integers_small 4/31 fail, 27 err, mixed_sign 6/10 fail, 4 err, large 1/40 fail, 39 err

---
## wiki:en:531871:1379991043:80

- Page: [Descartes's theorem](https://en.wikipedia.org/wiki/Descartes's_theorem) › Soddy circles of a triangle  · verdict **FAIL**, symbolic unknown
- LaTeX: `\begin{align}
\sqrt{r_1r_2r_3(r_1+r_2+r_3)}
= {} & \sqrt{r_1r_2r_4(r_1+r_2+r_4)}+{}\\
&\sqrt{r_1r_3r_4(r_1+r_3+r_4)}+{}\\
&\sqrt{r_2r_3r_4(r_2+r_3+r_4)}.
\end{align}`
- Context before: …oint $P_4$ inside the triangle. Triangle $\triangle P_1P_2P_3$ can be broken into three smaller triangles $\triangle P_1P_2P_4,$ $\triangle P_4P_2P_3,$ and $\triangle P_1P_4P_3,$ whose areas can be obtained by substituting $r_4$ for one of the other radii in the area formula above. The area of the first triangle equals the sum of these three areas:
- Context after: Careful algebraic manipulation shows that this formula is equivalent to equation (1), Descartes's theorem. This analysis covers all cases in which four circles are externally tangent; one is always the inner Soddy circle of the other three. The cases in which one of the circles is internally tangent to the other three and forms their outer Soddy ci…
- Translator read: `sqrt(r_1*r_2*r_3*(r_1 + r_2 + r_3))`  =  `sqrt(r_1*r_2*r_4*(r_1 + r_2 + r_4)) + sqrt(r_1*r_3*r_4*(r_1 + r_3 + r_4)) + sqrt(r_2*r_3*r_4*(r_2 + r_3 + r_4))`  · notes: pre:env_align
pre:row_continues_expr
pre:trailing_punct
sides: \sqrt{r_1r_2r_3(r_1+r_2+r_3)}  ||  \sqrt{r_1r_2r_4(r_1+r_2+r_4)}+{}\\ &\sqrt{r_1r_3r_4(r_1+r_3+r_4)}+{}\\ &\sqrt{r_2r_3r_4(r_2+r_3+r_4)}
- Assumptions: domains {'r_1': 'nonneg', 'r_2': 'nonneg', 'r_3': 'nonneg', 'r_4': 'nonneg'}; constants {}; constraints []
- Verifier: The identity fails at 58 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at r_1=0.496434, r_2=0.235091, r_3=0.034124, r_4=0.334779: lhs=0.055219642054, rhs=0.314441577955).
- Counterexample: {'r_1': '0.496434', 'r_2': '0.235091', 'r_3': '0.034124', 'r_4': '0.334779'} → lhs 0.05521964205477378625656276745800322006, rhs 0.31444157795517978092317519960361742409, rel diff 0.8243882300
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 10/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:81761:1376040312:1

- Page: [Diesel fuel](https://en.wikipedia.org/wiki/Diesel_fuel) › Carbon dioxide formation  · verdict **FAIL**, symbolic unknown
- LaTeX: `0.75 kg/L \cdot {\frac{6 \cdot 12}{6\cdot 12 + 14}\cdot 1} \cdot {\frac{44}{12}}= 2.3 kg/L`
- Context before: …an be calculated as: $0.838 kg/L \cdot {\frac{12}{14}}\cdot {\frac{44}{12}}= 2.63 kg/L$ The figure obtained with this estimation is close to the values found in the literature. For petrol, with a density of 0.75 kg/L and a ratio of carbon to hydrogen atoms of about 6 to 14, the estimated value of carbon emission if 1 litre of petrol is burnt gives:
- Context after: Hazards. Environment hazards of sulfur. In the past, diesel fuel contained higher quantities of sulfur. European emission standards and preferential taxation have forced oil refineries to dramatically reduce the level of sulfur in diesel fuels. In the European Union, the sulfur content has dramatically reduced during the last 20 years. Automotive d…
- Translator read: `99*g*k/(43*L)`  =  `23*g*k/(10*L)`  · notes: sides: 0.75 kg/L \cdot {\frac{6 \cdot 12}{6\cdot 12 + 14}\cdot 1} \cdot {\frac{44}{12}}  ||  2.3 kg/L
- Assumptions: domains {'L': 'positive', 'g': 'positive', 'k': 'nonneg_integer'}; constants {}; constraints []
- Verifier: The identity fails at 57 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at L=0.379984, g=0.262643, k=1: lhs=1.591355682540, rhs=1.589748252558).
- Counterexample: {'L': '0.379984', 'g': '0.262643', 'k': '1'} → lhs 1.59135568254036644872195353145836250632, rhs 1.58974825255800244220809297233567729167, rel diff 0.0010101010
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 9/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:23997203:1359018742:103

- Page: [Differential of a function](https://en.wikipedia.org/wiki/Differential_of_a_function) › Differentials in several variables > Application of the total differential to error estimation  · verdict **FAIL**, symbolic unknown
- LaTeX: `\frac{\Delta f}{f} = \frac{\Delta a}{a} + \frac{\Delta b}{b \ln b}`
- Context before: …frac{\Delta f}{f} = \frac{\Delta a}{a} + \frac{\Delta b}{b}.$ That is to say, in multiplication, the total relative error is the sum of the relative errors of the parameters. To illustrate how this depends on the function considered, consider the case where the function is $f(a,b)=a\ln b$ instead. Then, it can be computed that the error estimate is
- Context after: with an extra ln b factor not found in the case of a simple product. This additional factor tends to make the error smaller, as the denominator b ln b is larger than a bare b. Higher-order differentials. Higher-order differentials of a function of a single variable x can be defined via: $d^2y = d(dy) = d(f'(x)dx) = (df'(x))dx = f''(x)\,(dx)^2,$ and…
- Translator read: `Delta`  =  `Delta + Delta/log(b)`  · notes: sides: \frac{\Delta f}{f}  ||  \frac{\Delta a}{a} + \frac{\Delta b}{b \ln b}
- Assumptions: domains {'Delta': 'positive', 'b': 'positive'}; constants {}; constraints ['Ne(log(b), 0)']
- Verifier: The identity fails at 60 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at Delta=0.132792, b=0.0518753: lhs=0.132792000000, rhs=0.087913349744).
- Counterexample: {'Delta': '0.132792', 'b': '0.0518753'} → lhs 0.13279200000000000000000000000000000000, rhs 0.08791334974491296342459492145726547291, rel diff 0.3379620026
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:39407:1379998008:10

- Page: [Dirac equation](https://en.wikipedia.org/wiki/Dirac_equation) › History > Dirac's relativistic quantum mechanics  · verdict **FAIL**, symbolic unknown
- LaTeX: `\sqrt{p_1^2+p_2^2+p_3^2+(mc)^2} = \alpha_1p_1+\alpha_2p_2+\alpha_3p_3+\alpha_4 mc.`
- Context before: …mbol p^2+m^2c^2}$ . However, such a square root is mathematically problematic for the resulting theory, making it unfeasible. Dirac's first insight was the concept of linearization. He looked for some sort of variables $\alpha_i$ that are independent of momentum and spacetime coordinates for which the square root could be rewritten in a linear form
- Context after: By squaring this operator and demanding that it reduces to the Klein–Gordon equation, Dirac found that the variables must satisfy $\alpha_i^2=1$ and $\alpha_i\alpha_j + \alpha_j\alpha_i=0$ if $i \neq j$ . Dirac initially considered the $2\times 2$ Pauli matrices as a candidate, but then showed these would not work since it is impossible to find a s…
- Translator read: `sqrt(c**2*m**2 + p_1**2 + p_2**2 + p_3**2)`  =  `alpha_1*p_1 + alpha_2*p_2 + alpha_3*p_3 + alpha_4*c*m`  · notes: pre:trailing_punct
sides: \sqrt{p_1^2+p_2^2+p_3^2+(mc)^2}  ||  \alpha_1p_1+\alpha_2p_2+\alpha_3p_3+\alpha_4 mc
- Assumptions: domains {'alpha_1': 'real', 'alpha_2': 'real', 'alpha_3': 'real', 'alpha_4': 'real', 'c': 'real', 'm': 'nonneg_integer', 'p_1': 'positive', 'p_2': 'positive', 'p_3': 'positive'}; constants {}; constraints []
- Verifier: The identity fails at 60 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at alpha_1=0.911923, alpha_2=0.203856, alpha_3=0.446184, alpha_4=0.223233, c=0.308363, m=0, p_1=0.789757, p_2=0.686764, p_3=0.024839: lhs=1.046889624872, rhs=0.871281299071).
- Counterexample: {'alpha_1': '0.911923', 'alpha_2': '0.203856', 'alpha_3': '0.446184', 'alpha_4': '0.223233', 'c': '0.308363', 'm': '0', 'p_1': '0.789757', 'p_2': '0.686764', 'p_3': '0.024839'} → lhs 1.04688962487265103280767647332212720422, rhs 0.87128129907100000000000000000000000000, rel diff 0.1677429230
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:1235977:1370330378:78

- Page: [Dirichlet integral](https://en.wikipedia.org/wiki/Dirichlet_integral) › Evaluation > Dirichlet kernel  · verdict **FAIL**, symbolic unknown
- LaTeX: `1 - \cos(x) = 1 - \sum_{k\geq 0}\frac{{(-1)^{(k+1)}}x^{2k}}{(2k)!} = \sum_{k\geq 1}\frac{{(-1)^{(k+1)}}x^{2k}}{(2k)!}.`
- Context before: …\infty$ the term on the left converges with no problem. See the list of limits of trigonometric functions. We now show that $\int_{-\infty}^{\infty} \frac{1-\cos(x)}{x^2}dx$ is absolutely integrable, which implies that the limit exists. First, we seek to bound the integral near the origin. Using the Taylor-series expansion of the cosine about zero,
- Context after: Therefore, $\left|\frac{1 - \cos(x)}{x^2}\right| = \left|-\sum_{k\geq 0}\frac{x^{2k}}{2(k+1)!}\right| \leq \sum_{k\geq 0} \frac{|x|^k}{k!} = e^{|x|}.$ Splitting the integral into pieces, we have…
- Translator read (piece 0): `1 - cos(x)`  =  `1 - Sum((-1)**(k + 1)*x**(2*k)/factorial(2*k), (k, 0, oo))`  · notes: pre:trailing_punct
index_range_from_inequality
sides: 1 - \cos(x)  ||  1 - \sum_{k\geq 0}\frac{{(-1)^{(k+1)}}x^{2k}}{(2k)!}
- Translator read (piece 1): `1 - Sum((-1)**(k + 1)*x**(2*k)/factorial(2*k), (k, 0, oo))`  =  `Sum((-1)**(k + 1)*x**(2*k)/factorial(2*k), (k, 1, oo))`  · notes: pre:trailing_punct
index_range_from_inequality
sides: 1 - \sum_{k\geq 0}\frac{{(-1)^{(k+1)}}x^{2k}}{(2k)!}  ||  \sum_{k\geq 1}\frac{{(-1)^{(k+1)}}x^{2k}}{(2k)!}
- Assumptions: domains {'x': 'real'}; constants {}; constraints []
- Verifier: Chain link 0: The identity fails at 30 of 30 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at x=0.0813614: lhs=0.003308013269, rhs=1.996691986730).
- Counterexample: {'x': '0.0813614'} → lhs 0.00330801326910565729144296218813296418, rhs 1.99669198673089434270855703781186703581, rel diff 0.9983432530
- Regimes: small_positive 6/6 fail, 0 err, unit_interval 6/6 fail, 0 err, integers_small 6/6 fail, 0 err, mixed_sign 6/6 fail, 0 err, large 6/16 fail, 10 err

---
## wiki:en:1235977:1370330378:79

- Page: [Dirichlet integral](https://en.wikipedia.org/wiki/Dirichlet_integral) › Evaluation > Dirichlet kernel  · verdict **FAIL**, symbolic unknown
- LaTeX: `\left|\frac{1 - \cos(x)}{x^2}\right| 
  =  \left|-\sum_{k\geq 0}\frac{x^{2k}}{2(k+1)!}\right|
\leq \sum_{k\geq 0} \frac{|x|^k}{k!}
  =  e^{|x|}.`
- Context before: …\infty}^{\infty} \frac{1-\cos(x)}{x^2}dx$ is absolutely integrable, which implies that the limit exists. First, we seek to bound the integral near the origin. Using the Taylor-series expansion of the cosine about zero, $1 - \cos(x) = 1 - \sum_{k\geq 0}\frac{{(-1)^{(k+1)}}x^{2k}}{(2k)!} = \sum_{k\geq 1}\frac{{(-1)^{(k+1)}}x^{2k}}{(2k)!}.$ Therefore,
- Context after: Splitting the integral into pieces, we have $\int_{-\infty}^{\infty}\left|\frac{1-\cos(x)}{x^2}\right|dx \leq \int_{-\infty}^{-\varepsilon} \frac{2}{x^2}dx + \int_{-\varepsilon}^{\varepsilon} e^{|x|}dx + \int_{\varepsilon}^{\infty} \frac{2}{x^2}dx \leq K,$ for some constant $K > 0$ . This shows that the integral is absolutely integrable, which impl…
- Translator read (piece 0): `Abs((cos(x) - 1)/x**2)`  =  `Abs(Sum(x**(2*k)/(2*factorial(k + 1)), (k, 0, oo)))`  · notes: pre:left_right
pre:trailing_punct
index_range_from_inequality
sides: |\frac{1 - \cos(x)}{x^2}\right|  ||  |-\sum_{k\geq 0}\frac{x^{2k}}{2(k+1)!}\right|
- Translator read (piece 1): `Abs(Sum(x**(2*k)/(2*factorial(k + 1)), (k, 0, oo)))`  <=  `Sum(Abs(x)**k/factorial(k), (k, 0, oo))`  · notes: pre:left_right
pre:trailing_punct
index_range_from_inequality
sides: |-\sum_{k\geq 0}\frac{x^{2k}}{2(k+1)!}\right|  ||  \sum_{k\geq 0} \frac{|x|^k}{k!}
- Translator read (piece 2): `Sum(Abs(x)**k/factorial(k), (k, 0, oo))`  =  `e**Abs(x)`  · notes: pre:left_right
pre:trailing_punct
index_range_from_inequality
hint:e_only_as_exp_base
sides: \sum_{k\geq 0} \frac{|x|^k}{k!}  ||  e^{|x|}
- Assumptions: domains {'x': 'real'}; constants {'e': 'E'}; constraints ['Ne(x, 0)']
- Verifier: Chain link 0: The identity fails at 26 of 26 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign) (e.g. at x=0.0982632: lhs=0.499597810446, rhs=0.502421702217).
- Counterexample: {'x': '0.0982632'} → lhs 0.49959781044639060525043369397396963230, rhs 0.50242170221777483713016672665033177327, rel diff 0.0056205608
- Regimes: small_positive 6/6 fail, 0 err, unit_interval 6/6 fail, 0 err, integers_small 6/6 fail, 0 err, mixed_sign 6/6 fail, 0 err, large 2/30 fail, 28 err

---
## wiki:en:206210:1328878894:6

- Page: [Discrete Hartley transform](https://en.wikipedia.org/wiki/Discrete_Hartley_transform) › Multi-Dimensional Discrete Hartley Transform (MD-DHT)  · verdict **FAIL**, symbolic unknown
- LaTeX: `{\rm cas}(x)=\cos(x)+\sin(x).`
- Context before: …ble (Chu & Burrus, 1982). Multi-Dimensional Discrete Hartley Transform (MD-DHT). The rD-DHT (MD-DHT with "r" dimensions) is given by $X(k_1,k_2,...,k_r)=\sum_{n_1=0}^{N_1-1} \sum_{n_2=0}^{N_2-1} \dots \sum_{n_r=0}^{N_r-1} x(n_1,n_2,...,n_r){\rm cas}(\frac{2\pi n_1 k_1}{N_1}+\dots +\frac{2\pi n_r k_r}{N_r}),$ with $k_i = 0,1,\ldots, N_i-1$ and where
- Context after: Similar to the 1-D case, as a real and symmetric transform, the MD-DHT is simpler than the MD-DFT. For one, the inverse DHT is identical to the forward transform, with the addition of a scaling factor; and second, since the kernel is real, it avoids the computational complexity of complex numbers. Additionally, the DFT is directly obtainable from t…
- Translator read: `a*c*s*x`  =  `sin(x) + cos(x)`  · notes: pre:trailing_punct
sides: {\rm cas}(x)  ||  \cos(x)+\sin(x)
- Assumptions: domains {'a': 'real', 'c': 'real', 's': 'complex', 'x': 'real'}; constants {}; constraints []
- Verifier: The identity fails at 72 of 72 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, complex, large) (e.g. at a=0.132354, c=0.0603737, s=0.127126, x=0.285522: lhs=0.000290040618, rhs=1.241173114078).
- Counterexample: {'a': '0.132354', 'c': '0.0603737', 's': '0.127126', 'x': '0.285522'} → lhs 0.00029004061860497708872560000000000000, rhs 1.24117311407804893329227707971728790775, rel diff 0.9997663173
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, complex 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:185663:1380614065:57

- Page: [Division by zero](https://en.wikipedia.org/wiki/Division_by_zero) › Elementary arithmetic > Fallacies  · verdict **FAIL**, symbolic not_equal
- LaTeX: `1 = 2`
- Context before: …nd division by zero is not allowed. Fallacies. A compelling reason for not allowing division by zero is that allowing it leads to fallacies. When working with numbers, it is easy to identify an illegal division by zero. For example: From $0 \times 1 = 0$ and $0 \times 2 = 0$ one gets $0 \times 1 = 0 \times 2$ . Cancelling $0$ from both sides yields
- Context after: , a false statement. The fallacy here arises from the assumption that it is legitimate to cancel $0$ like any other number, whereas, in fact, doing so is a form of division by $0$ . Using algebra, it is possible to disguise a division by zero to obtain an invalid proof. For example: Let $x = 1$ . Multiply both sides by $x$ to get $\textstyle x = x^…
- Translator read: `1`  =  `2`  · notes: sides: 1  ||  2
- Assumptions: domains {}; constants {}; constraints []
- Verifier: The constant identity does not hold: both sides differ beyond 1e-8 relative error, stably at two working precisions (lhs=1.0000000000000000, rhs=2.0000000000000000).
- Counterexample: {} → lhs 1.00000000000000000000000000000000000000, rhs 2.00000000000000000000000000000000000000, rel diff 0.5000000000
- Regimes: constant 1/1 fail, 0 err

---
## wiki:en:185663:1380614065:69

- Page: [Division by zero](https://en.wikipedia.org/wiki/Division_by_zero) › Elementary arithmetic > Fallacies  · verdict **FAIL**, symbolic not_equal
- LaTeX: `1 = 2.`
- Context before: …, it is possible to disguise a division by zero to obtain an invalid proof. For example: Let $x = 1$ . Multiply both sides by $x$ to get $\textstyle x = x^2$ . Subtract $1$ from each side to get $x - 1 = x^2 - 1.$ The right side can be factored, $x - 1 = (x + 1)(x - 1).$ Dividing both sides by $x - 1$ yields $1 = x + 1.$ Substituting $x = 1$ yields
- Context after: This is essentially the same fallacious computation as the previous numerical version, but the division by zero was obfuscated because we wrote $0$ as $x - 1$ . Early attempts. The Brāhmasphuṭasiddhānta of Brahmagupta (c. 598–668) is the earliest text to treat zero as a number in its own right and to define operations involving zero. According to B…
- Translator read: `1`  =  `2`  · notes: pre:trailing_punct
sides: 1  ||  2
- Assumptions: domains {}; constants {}; constraints []
- Verifier: The constant identity does not hold: both sides differ beyond 1e-8 relative error, stably at two working precisions (lhs=1.0000000000000000, rhs=2.0000000000000000).
- Counterexample: {} → lhs 1.00000000000000000000000000000000000000, rhs 2.00000000000000000000000000000000000000, rel diff 0.5000000000
- Regimes: constant 1/1 fail, 0 err

---
## wiki:en:185663:1380614065:148

- Page: [Division by zero](https://en.wikipedia.org/wiki/Division_by_zero) › Higher mathematics > Abstract algebra  · verdict **FAIL**, symbolic not_equal
- LaTeX: `0 = 1`
- Context before: …ative ring, which is a mathematical structure where addition, subtraction, and multiplication behave as they do in the more familiar number systems, but division may not be defined. Adjoining a multiplicative inverses to a commutative ring is called localization. However, the localization of every commutative ring at zero is the trivial ring, where
- Context after: , so nontrivial commutative rings do not have inverses at zero, and thus division by zero is undefined for nontrivial commutative rings. Nevertheless, any number system that forms a commutative ring can be extended to a structure called a wheel in which division by zero is always possible. However, the resulting mathematical structure is no longer…
- Translator read: `0`  =  `1`  · notes: sides: 0  ||  1
- Assumptions: domains {}; constants {}; constraints []
- Verifier: The constant identity does not hold: both sides differ beyond 1e-8 relative error, stably at two working precisions (lhs=0, rhs=1.0000000000000000).
- Counterexample: {} → lhs 0, rhs 1.00000000000000000000000000000000000000, rel diff 1.0000000000
- Regimes: constant 1/1 fail, 0 err

---
## wiki:en:8400:1376450880:9

- Page: [Duodecimal](https://en.wikipedia.org/wiki/Duodecimal) › Fractions and irrational numbers > Fractions  · verdict **FAIL**, symbolic unknown
- LaTeX: `10^n=2^{2n}\times 3^n`
- Context before: …each prime and multiplying the resulting quantities together, so the number of factors of $10^n$ is $(n+1)(n+1)=(n+1)^2$ . For example, the number 8 is a factor of 103 (1000), so $\frac{1}{8}$ and other fractions with a denominator of 8 cannot require more than three fractional decimal digits to terminate. $\frac{5}{8}=0.625_{10}.$ For duodecimal,
- Context after: . This has $(2n+1)(n+1)$ divisors. The sample denominator of 8 is a factor of a gross $12^2=144$ (in decimal), so eighths cannot need more than two duodecimal fractional places to terminate. $\frac{5}{8}=0.76_{12}.$ Because both ten and twelve have two unique prime factors, the number of divisors of $b^n$ for b = 10 or 12 grows quadratically with t…
- Translator read: `10**n`  =  `2**(2*n)*3**n`  · notes: op:times
sides: 10^n  ||  2^{2n}\times 3^n
- Assumptions: domains {'n': 'nonneg_integer'}; constants {}; constraints []
- Verifier: The identity fails at 46 of 49 evaluable points, a clear majority in every regime (small_positive, integers_small, mixed_sign, large) (e.g. at n=1: lhs=10.00000000000, rhs=12.00000000000).
- Counterexample: {'n': '1'} → lhs 10.0000000000000000000000000000000000000, rhs 12.0000000000000000000000000000000000000, rel diff 0.1666666666
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 3/4 fail, 0 err, integers_small 11/12 fail, 0 err, mixed_sign 8/9 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:9633:1380657289:9

- Page: [E (mathematical constant)](https://en.wikipedia.org/wiki/E_(mathematical_constant)) › History  · verdict **FAIL**, symbolic unknown
- LaTeX: `\frac{dc}{c} = \frac{dy ds}{rdx}`
- Context before: …Gottfried Leibniz in letters to Christiaan Huygens in 1690 and 1691. Leonhard Euler started to use the letter e for the constant in 1727 or 1728, in an unpublished paper on explosive forces in cannons, and in a letter to Christian Goldbach on 25 November 1731. The first appearance of e in a printed publication was in Euler's Mechanica (1736). [ref]
- Context after: It is unknown why Euler chose the letter e. Although some researchers used the letter c in the subsequent years, the letter e was more common and eventually became standard. Euler proved that e is the sum of the infinite series $e = \sum_{n = 0}^\infty \frac{1}{n!} = \frac{1}{0!} + \frac{1}{1!} + \frac{1}{2!} + \frac{1}{3!} + \frac{1}{4!} + \cdots…
- Translator read: `d`  =  `d*s*y/(r*x)`  · notes: sides: \frac{dc}{c}  ||  \frac{dy ds}{rdx}
- Assumptions: domains {'d': 'positive', 'r': 'nonneg', 's': 'complex', 'x': 'real', 'y': 'real'}; constants {}; constraints ['Ne(r, 0)', 'Ne(x, 0)']
- Verifier: The identity fails at 72 of 72 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, complex, large) (e.g. at d=0.0955393, r=0.584414, s=0.220901, x=0.124636, y=0.316012: lhs=0.095539300000, rhs=0.091562827966).
- Counterexample: {'d': '0.0955393', 'r': '0.584414', 's': '0.220901', 'x': '0.124636', 'y': '0.316012'} → lhs 0.09553930000000000000000000000000000000, rhs 0.09156282796690740755899688690312260752, rel diff 0.0416213226
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, complex 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:9633:1380657289:11

- Page: [E (mathematical constant)](https://en.wikipedia.org/wiki/E_(mathematical_constant)) › History  · verdict **FAIL**, symbolic unknown
- LaTeX: `\frac{dc}{c} = \frac{dy ds}{rdx}`
- Context before: …Gottfried Leibniz in letters to Christiaan Huygens in 1690 and 1691. Leonhard Euler started to use the letter e for the constant in 1727 or 1728, in an unpublished paper on explosive forces in cannons, and in a letter to Christian Goldbach on 25 November 1731. The first appearance of e in a printed publication was in Euler's Mechanica (1736). [ref]
- Context after: It is unknown why Euler chose the letter e. Although some researchers used the letter c in the subsequent years, the letter e was more common and eventually became standard. Euler proved that e is the sum of the infinite series $e = \sum_{n = 0}^\infty \frac{1}{n!} = \frac{1}{0!} + \frac{1}{1!} + \frac{1}{2!} + \frac{1}{3!} + \frac{1}{4!} + \cdots…
- Translator read: `d`  =  `d*s*y/(r*x)`  · notes: sides: \frac{dc}{c}  ||  \frac{dy ds}{rdx}
- Assumptions: domains {'d': 'positive', 'r': 'nonneg', 's': 'complex', 'x': 'real', 'y': 'real'}; constants {}; constraints ['Ne(r, 0)', 'Ne(x, 0)']
- Verifier: The identity fails at 72 of 72 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, complex, large) (e.g. at d=0.646441, r=0.0209649, s=0.33998, x=0.21255, y=0.604124: lhs=0.646441000000, rhs=29.79575864692).
- Counterexample: {'d': '0.646441', 'r': '0.0209649', 's': '0.33998', 'x': '0.21255', 'y': '0.604124'} → lhs 0.64644100000000000000000000000000000000, rhs 29.7957586469223998383811633926800206691, rel diff 0.9783042610
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, complex 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:236020:1320309572:1

- Page: [Elliptic geometry](https://en.wikipedia.org/wiki/Elliptic_geometry) › Elliptic space (the 3D case)  · verdict **FAIL**, symbolic unknown
- LaTeX: `\exp(\theta r) = \cos \theta + r \sin \theta`
- Context before: …ipollent when they are of the same length, orientation, and great circle. These relations of equipollence produce 3D vector space and elliptic space, respectively. Access to elliptic space structure is provided through the vector algebra of William Rowan Hamilton: he envisioned a sphere as a domain of square roots of minus one. Then Euler's formula
- Context after: (where r is on the sphere) represents the great circle in the plane containing 1 and r. Opposite points r and −r correspond to oppositely directed circles. An arc between θ and φ is equipollent with one between 0 and φ − θ. In elliptic space, arc length is less than π, so arcs may be parametrized with θ in [0, π) or (−π/2, π/2]. For…
- Translator read: `exp(r*theta)`  =  `r*sin(theta) + cos(theta)`  · notes: sides: \exp(\theta r)  ||  \cos \theta + r \sin \theta
- Assumptions: domains {'r': 'nonneg', 'theta': 'angle'}; constants {}; constraints []
- Verifier: The identity fails at 57 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at r=0.209158, theta=0.162693: lhs=1.034614136774, rhs=1.020673284213).
- Counterexample: {'r': '0.209158', 'theta': '0.162693'} → lhs 1.03461413677447650450341161630413152438, rhs 1.02067328421350118513557361506973096054, rel diff 0.0134744462
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 9/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err
