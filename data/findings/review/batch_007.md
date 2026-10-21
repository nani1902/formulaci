# Review batch 007 — 22 items

For each item answer with one JSON line (Finding schema): {"formula_id": ..., "verdict": "FAIL", "review": {"status": "confirmed_error"|"false_positive"|"ambiguous", "reviewer": "<name>", "notes": "<why, one or two sentences>"}, "suggested_fix": "<corrected LaTeX or null>", "evidence": "<independent source or derivation>"}


---
## wiki:en:27430123:1372869378:199

- Page: [Integer triangle](https://en.wikipedia.org/wiki/Integer_triangle) › Integer triangles with specific angle properties > Integer triangles with one angle with a given rational cosine > Integer triangles with a 120° angle  · verdict **FAIL**, symbolic not_equal
- LaTeX: `\gcd(a,b,c) = 3`
- Context before: …,$ with coprime integers m, n with 0 < n < m (the angle of 120° is opposite to the side of length a). From here, all primitive solutions can be obtained by dividing a, b, and c by their greatest common divisor. The smallest solution, for m = 2 and n = 1, is the triangle with sides (3,5,7). See also. More precisely, If $m \equiv n \!\pmod{3}$ , then
- Context after: , otherwise $\gcd(a,b,c) = 1$ . Since the biggest side a can only be generated with a single $(m, n)$ pair, each primitive triple can be generated in precisely two ways: once directly with a gcd of 1, and once indirectly with a gcd of 3. Therefore, in order to generate all primitive triples uniquely, one can just add additional $m \not\equiv n \!\p…
- Translator read: `1`  =  `3`  · notes: sides: \gcd(a,b,c)  ||  3
- Assumptions: domains {}; constants {}; constraints []
- Verifier: The constant identity does not hold: both sides differ beyond 1e-8 relative error, stably at two working precisions (lhs=1.0000000000000000, rhs=3.0000000000000000).
- Counterexample: {} → lhs 1.00000000000000000000000000000000000000, rhs 3.00000000000000000000000000000000000000, rel diff 0.6666666666
- Regimes: constant 1/1 fail, 0 err

---
## wiki:en:374220:1380733448:374

- Page: [Inverse trigonometric functions](https://en.wikipedia.org/wiki/Inverse_trigonometric_functions) › Basic concepts > Relationships among the inverse trigonometric functions  · verdict **FAIL**, symbolic not_equal
- LaTeX: `\begin{align}
\arcsin(-x) &= -\arcsin(x) \\
\arccsc(-x) &= -\arccsc(x) \\
\arccos(-x) &= \pi -\arccos(x) \\
\arcsec(-x) &= \pi -\arcsec(x) \\
\arctan(-x) &= -\arctan(x) \\
\arccot(-x) &= \pi -\arccot(x)
\end{align}`
- Context before: …(x)) = \sqrt{1-\frac{1}{x^2}}$ $\tan(\arccsc(x)) = \frac{\sgn(x)}{\sqrt{x^2-1}}$ Relationships among the inverse trigonometric functions. Complementary angles: $\begin{align} \arccos(x) &= \frac{\pi}{2} - \arcsin(x) \\[0.5em] \arccot(x) &= \frac{\pi}{2} - \arctan(x) \\[0.5em] \arccsc(x) &= \frac{\pi}{2} - \arcsec(x) \end{align}$ Negative arguments:
- Context after: Reciprocal arguments:…
- Translator read (piece 0): `-asin(x)`  =  `-asin(x)`  · notes: pre:env_align
pre:rows=6
sides: \arcsin(-x)  ||  -\arcsin(x)
- Translator read (piece 1): `-acsc(x)`  =  `-acsc(x)`  · notes: pre:env_align
pre:rows=6
sides: \arccsc(-x)  ||  -\arccsc(x)
- Translator read (piece 2): `acos(-x)`  =  `pi - acos(x)`  · notes: pre:env_align
pre:rows=6
sides: \arccos(-x)  ||  \pi -\arccos(x)
- Translator read (piece 3): `asec(-x)`  =  `pi - asec(x)`  · notes: pre:env_align
pre:rows=6
sides: \arcsec(-x)  ||  \pi -\arcsec(x)
- Translator read (piece 4): `-atan(x)`  =  `-atan(x)`  · notes: pre:env_align
pre:rows=6
sides: \arctan(-x)  ||  -\arctan(x)
- Translator read (piece 5): `-acot(x)`  =  `pi - acot(x)`  · notes: pre:env_align
pre:rows=6
sides: \arccot(-x)  ||  \pi -\arccot(x)
- Assumptions: domains {'x': 'real'}; constants {}; constraints ['((x) >= -1) & ((x) <= 1)', 'Abs(x) >= 1', '((-x) >= -1) & ((-x) <= 1)']
- Verifier: Chain link 5: The identity fails at 48 of 48 evaluable points, a clear majority in every regime (small_positive, integers_small, mixed_sign, large) (e.g. at x=1: lhs=-0.78539816339, rhs=2.356194490192).
- Counterexample: {'x': '1'} → lhs -0.7853981633974483096156608458198757210, rhs 2.35619449019234492884698253745962716314, rel diff 1.3333333333
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 0/0 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:1521924:1361521690:13

- Page: [Jet (mathematics)](https://en.wikipedia.org/wiki/Jet_(mathematics)) › Jets of functions between Euclidean spaces > Algebraic properties of jets  · verdict **FAIL**, symbolic unknown
- LaTeX: `J^k_{x_0}f\cdot J^k_{x_0}g=J^k_{x_0}(f\cdot g).`
- Context before: …of jets. There are two basic algebraic structures jets can carry. The first is a product structure, although this ultimately turns out to be the least important. The second is the structure of the composition of jets. If $f,g:{\mathbb R}^n\rightarrow {\mathbb R}$ are a pair of real-valued functions, then we can define the product of their jets via
- Context after: Here we have suppressed the indeterminate z, since it is understood that jets are formal polynomials. This product is just the product of ordinary polynomials in z, modulo $z^{k+1}$ . In other words, it is multiplication in the ring ${\mathbb R}[z]/(z^{k+1})$ , where $(z^{k+1})$ is the ideal generated by homogeneous polynomials of order ≥ k + 1. We…
- Translator read: `J_{x_0}**(2*k)*f*g`  =  `J_{x_0}**k*f*g`  · notes: pre:trailing_punct
mult_not_call:J
subscript_expr:J_{x_0}
sides: J^k_{x_0}f\cdot J^k_{x_0}g  ||  J^k_{x_0}(f\cdot g)
- Assumptions: domains {'J_{x_0}': 'positive', 'f': 'positive', 'g': 'positive', 'k': 'nonneg_integer'}; constants {}; constraints []
- Verifier: The identity fails at 57 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at J_{x_0}=0.0455787, f=0.601272, g=0.929867, k=1: lhs=0.001161490557, rhs=0.025483187487).
- Counterexample: {'J_{x_0}': '0.0455787', 'f': '0.601272', 'g': '0.929867', 'k': '1'} → lhs 0.00116149055755337347750056000000000000, rhs 0.02548318748786984880000000000000000000, rel diff 0.9544213000
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 10/12 fail, 0 err, integers_small 11/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:312877:1374766194:18

- Page: [Jordan normal form](https://en.wikipedia.org/wiki/Jordan_normal_form) › Complex matrices > Example  · verdict **FAIL**, symbolic not_equal
- LaTeX: `i = 1,2,3`
- Context before: …ix} p_1 & p_2 & p_3 & p_4 \end{bmatrix} = \begin{bmatrix} p_1 & p_2 & p_3 & p_4 \end{bmatrix} \begin{bmatrix} 1 & 0 & 0 & 0 \\ 0 & 2 & 0 & 0 \\ 0 & 0 & 4 & 1 \\ 0 & 0 & 0 & 4 \end{bmatrix} = \begin{bmatrix} p_1 & 2p_2 & 4p_3 & p_3+4p_4 \end{bmatrix}.$ We see that $(A - 1 I) p_1 = 0$ $(A - 2 I) p_2 = 0$ $(A - 4 I) p_3 = 0$ $(A - 4 I) p_4 = p_3.$ For
- Context after: we have $p_i \in \ker(A-\lambda_{i} I)$ , that is, $p_i$ is an eigenvector of $A$ corresponding to the eigenvalue $\lambda_i$ . For $i=4$ , multiplying both sides by $(A-4I)$ gives $(A-4I)^2 p_4 = (A-4I) p_3.$ But $(A-4I)p_3 = 0$ , so $(A-4I)^2 p_4 = 0.$ Thus, $p_4 \in \ker(A-4 I)^2.$ Vectors such as $p_4$ are called generalized eigenvectors of A.…
- Translator read: `i`  =  `1`  · notes: cond: 2,3
hint:i_present
sides: i  ||  1
- Assumptions: domains {}; constants {'i': 'I'}; constraints []
- Verifier: The constant identity does not hold: both sides differ beyond 1e-8 relative error, stably at two working precisions (lhs=(0.0 + 1.0j), rhs=1.0000000000000000).
- Counterexample: {} → lhs (0.0 + 1.0j), rhs 1.00000000000000000000000000000000000000, rel diff 1.4142135623
- Regimes: constant 1/1 fail, 0 err

---
## wiki:en:17553:1380896199:115

- Page: [Kepler's laws of planetary motion](https://en.wikipedia.org/wiki/Kepler's_laws_of_planetary_motion) › Position as a function of time > True anomaly, θ  · verdict **FAIL**, symbolic unknown
- LaTeX: `|cd| = |cs| + |sd|,`
- Context before: …e next step is to calculate the true anomaly θ. Note that Cartesian position coordinates with reference to the center of ellipse are (a cos E, b sin E). With reference to the Sun (with coordinates (c, 0) = (ae, 0)), r = (a cos E − ae, b sin E). True anomaly would be arctan(ry/rx), magnitude of r would be . True anomaly, θ. Note from the figure that
- Context after: so that $a\cos E = a \varepsilon + r \cos\theta.$ Dividing by $a$ and inserting from Kepler's first law $\frac{r}{a} = \frac{1 - \varepsilon^2}{1 + \varepsilon \cos\theta}$ gives…
- Translator read: `Abs(c*d)`  =  `Abs(c*s) + Abs(d*s)`  · notes: pre:trailing_punct
sides: |cd|  ||  |cs| + |sd|
- Assumptions: domains {'c': 'real', 'd': 'positive', 's': 'complex'}; constants {}; constraints []
- Verifier: The identity fails at 72 of 72 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, complex, large) (e.g. at c=0.0723357, d=0.286951, s=0.015182: lhs=0.020756801450, rhs=0.005454690679).
- Counterexample: {'c': '0.0723357', 'd': '0.286951', 's': '0.015182'} → lhs 0.02075680145070000000000000000000000000, rhs 0.00545469067940000000000000000000000000, rel diff 0.7372094784
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, complex 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:24367204:1343874121:47

- Page: [Krippendorff's alpha](https://en.wikipedia.org/wiki/Krippendorff's_alpha) › A computational example  · verdict **FAIL**, symbolic not_equal
- LaTeX: `\frac {2}{2-1}=6`
- Context before: …and unit 1 contains only one value, which is not pairable within that unit. Thus, these reliability data consist not of mN = 45 but of n = 26 pairable values, not in N = 15 but in 12 multiply coded units. The coincidence matrix for these data would be constructed as follows: o11 = {in u=4}: $\frac {2}{2-1}+$ {in u=10}: $\frac {2}{2-1}+$ {in u=11}:
- Context after: o13 = {in u=8}: $\frac {1}{2-1}=1=$ o31 o22 = {in u=3}: $\frac {2}{2-1}+$ {in u=9}: $\frac {2}{2-1}=4$ o33 = {in u=5}: $\frac {2}{2-1}+$ {in u=6}: $\frac {2}{3-1}+$ {in u=12}: $\frac {2}{2-1}+$ {in u=13}: $\frac {2}{2-1}=7$ o34 = {in u=6}: $\frac {2}{3-1}+$ {in u=15}: $\frac {1}{2-1}=2=$ o43 o44 = {in u=7}: $\frac {6}{3-1}=3$ Values v or v′: 1 2 3…
- Translator read: `2`  =  `6`  · notes: sides: \frac {2}{2-1}  ||  6
- Assumptions: domains {}; constants {}; constraints []
- Verifier: The constant identity does not hold: both sides differ beyond 1e-8 relative error, stably at two working precisions (lhs=2.0000000000000000, rhs=6.0000000000000000).
- Counterexample: {} → lhs 2.00000000000000000000000000000000000000, rhs 6.00000000000000000000000000000000000000, rel diff 0.6666666666
- Regimes: constant 1/1 fail, 0 err

---
## wiki:en:24367204:1343874121:50

- Page: [Krippendorff's alpha](https://en.wikipedia.org/wiki/Krippendorff's_alpha) › A computational example  · verdict **FAIL**, symbolic not_equal
- LaTeX: `\frac {2}{2-1}=4`
- Context before: …ta consist not of mN = 45 but of n = 26 pairable values, not in N = 15 but in 12 multiply coded units. The coincidence matrix for these data would be constructed as follows: o11 = {in u=4}: $\frac {2}{2-1}+$ {in u=10}: $\frac {2}{2-1}+$ {in u=11}: $\frac {2}{2-1}=6$ o13 = {in u=8}: $\frac {1}{2-1}=1=$ o31 o22 = {in u=3}: $\frac {2}{2-1}+$ {in u=9}:
- Context after: o33 = {in u=5}: $\frac {2}{2-1}+$ {in u=6}: $\frac {2}{3-1}+$ {in u=12}: $\frac {2}{2-1}+$ {in u=13}: $\frac {2}{2-1}=7$ o34 = {in u=6}: $\frac {2}{3-1}+$ {in u=15}: $\frac {1}{2-1}=2=$ o43 o44 = {in u=7}: $\frac {6}{3-1}=3$ Values v or v′: 1 2 3 4 nv Value 1 6 1 7 Value 2 4 4 Value 3 1 7 2 10 Value 4 2 3 5 Frequency nv' 7 4 10 5 26 In terms of the…
- Translator read: `2`  =  `4`  · notes: sides: \frac {2}{2-1}  ||  4
- Assumptions: domains {}; constants {}; constraints []
- Verifier: The constant identity does not hold: both sides differ beyond 1e-8 relative error, stably at two working precisions (lhs=2.0000000000000000, rhs=4.0000000000000000).
- Counterexample: {} → lhs 2.00000000000000000000000000000000000000, rhs 4.00000000000000000000000000000000000000, rel diff 0.5000000000
- Regimes: constant 1/1 fail, 0 err

---
## wiki:en:24367204:1343874121:54

- Page: [Krippendorff's alpha](https://en.wikipedia.org/wiki/Krippendorff's_alpha) › A computational example  · verdict **FAIL**, symbolic not_equal
- LaTeX: `\frac {2}{2-1}=7`
- Context before: …trix for these data would be constructed as follows: o11 = {in u=4}: $\frac {2}{2-1}+$ {in u=10}: $\frac {2}{2-1}+$ {in u=11}: $\frac {2}{2-1}=6$ o13 = {in u=8}: $\frac {1}{2-1}=1=$ o31 o22 = {in u=3}: $\frac {2}{2-1}+$ {in u=9}: $\frac {2}{2-1}=4$ o33 = {in u=5}: $\frac {2}{2-1}+$ {in u=6}: $\frac {2}{3-1}+$ {in u=12}: $\frac {2}{2-1}+$ {in u=13}:
- Context after: o34 = {in u=6}: $\frac {2}{3-1}+$ {in u=15}: $\frac {1}{2-1}=2=$ o43 o44 = {in u=7}: $\frac {6}{3-1}=3$ Values v or v′: 1 2 3 4 nv Value 1 6 1 7 Value 2 4 4 Value 3 1 7 2 10 Value 4 2 3 5 Frequency nv' 7 4 10 5 26 In terms of the entries in this coincidence matrix, Krippendorff's alpha may be calculated from:…
- Translator read: `2`  =  `7`  · notes: sides: \frac {2}{2-1}  ||  7
- Assumptions: domains {}; constants {}; constraints []
- Verifier: The constant identity does not hold: both sides differ beyond 1e-8 relative error, stably at two working precisions (lhs=2.0000000000000000, rhs=7.0000000000000000).
- Counterexample: {} → lhs 2.00000000000000000000000000000000000000, rhs 7.00000000000000000000000000000000000000, rel diff 0.7142857142
- Regimes: constant 1/1 fail, 0 err

---
## wiki:en:92465:1379523476:40

- Page: [Lambert W function](https://en.wikipedia.org/wiki/Lambert_W_function) › History  · verdict **FAIL**, symbolic unknown
- LaTeX: `x = x^m + q.`
- Context before: …d as a converse relation rather than inverse function. It is related to the omega constant, which is equal to $W_0\left(1\right)$ . History. Lambert first considered the related Lambert's Transcendental Equation in 1758, which led to an article by Leonhard Euler in 1783 that discussed the special case of $we^w$ . The equation Lambert considered was
- Context after: Euler transformed this equation into the form $x^a - x^b = (a - b) c x^{a + b}.$ Both authors derived a series solution for their equations. Once Euler had solved this equation, he considered the case $a = b$ . Taking limits, he derived the equation $\ln x = c x^a.$ He then put $a = 1$ and obtained a convergent series solution for the resulting equ…
- Translator read: `x`  =  `q + x**m`  · notes: pre:trailing_punct
sides: x  ||  x^m + q
- Assumptions: domains {'m': 'nonneg_integer', 'q': 'positive', 'x': 'real'}; constants {}; constraints []
- Verifier: The identity fails at 60 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at m=0, q=0.561389, x=0.226567: lhs=0.226567000000, rhs=1.561389000000).
- Counterexample: {'m': '0', 'q': '0.561389', 'x': '0.226567'} → lhs 0.22656700000000000000000000000000000000, rhs 1.56138900000000000000000000000000000000, rel diff 0.8548939437
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:92465:1379523476:74

- Page: [Lambert W function](https://en.wikipedia.org/wiki/Lambert_W_function) › Elementary properties, branches and range > Inverse  · verdict **FAIL**, symbolic unknown
- LaTeX: `z \cdot e^z \leq \frac{-1}{e}`
- Context before: …$\ f = z\ e^z\$ implies that there exists an $\ n\$ such that $\ z = W_n(f) = W_n(z\ e^z)\ ,$ where $\ n\$ depends upon the value of $\ z ~.$ For real values of $\ z\ ,$ the value of the integer $\ n\$ changes abruptly when $\ z\ e^z\$ is at the branch cut of $\ W_n(z\ e^z)\ ,$ which means that $z \cdot e^z \leq 0$ except for $\ n = 0\$ where it is
- Context after: . For complex $\ z\ ,$ define $\ z = x + i\ y\ ,$ where $\ x\$ and $\ y\$ are real, and expressing $\ e^z\$ in polar coordinates, it is seen that $\begin{align} z\ e^z &= (x + i\ y)\ e^{x}\ (\cos y + i\ \sin y) \\ &= e^{x} (x\ \cos y\ -\ y\ \sin y)\ +\ i\ e^{x} (x\ \sin y\ +\ y\ \cos y) \\ \end{align}$ For $\ n \neq 0\ ,$ the branch cut for $\ W_n(…
- Translator read: `e**z*z`  <=  `-1/e`  · notes: hint:e_only_as_exp_base
sides: z \cdot e^z  ||  \frac{-1}{e}
- Assumptions: domains {'z': 'complex'}; constants {'e': 'E'}; constraints []
- Verifier: The inequality fails at 60 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at z=0: lhs=0, rhs=-0.36787944117).
- Counterexample: {'z': '0'} → lhs 0, rhs -0.3678794411714423215955237701614608674, rel diff 1.0000000000
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:92465:1379523476:222

- Page: [Lambert W function](https://en.wikipedia.org/wiki/Lambert_W_function) › Applications > Solving equations > Linear functions and exponentials  · verdict **FAIL**, symbolic unknown
- LaTeX: `2x+2 = 3^x`
- Context before: …equations. Linear functions and exponentials. The Lambert W function is used to solve equations in which the unknown quantity occurs both in the base and in the exponent, or both inside and outside of a logarithm. The strategy is to convert such an equation into one of the form and then to solve for z using the W function. For example, the equation
- Context after: (where x is an unknown real number) can be solved by rewriting it as $\begin{align} &(x+1)\ 3^{-x}=\frac{1}{2} & (\mbox{multiply by } 3^{-x}/2) \\ \Leftrightarrow\ &(-x-1)\ 3^{-x-1} = -\frac{1}{6} & (\mbox{multiply by } {-}1/3) \\ \Leftrightarrow\ &(\ln 3) (-x-1)\ e^{(\ln 3)(-x-1)} = -\frac{\ln 3}{6} & (\mbox{multiply by } \ln 3) \end{align}$ This…
- Translator read: `2*x + 2`  =  `3**x`  · notes: sides: 2x+2  ||  3^x
- Assumptions: domains {'x': 'real'}; constants {}; constraints []
- Verifier: The identity fails at 60 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at x=0: lhs=2.000000000000, rhs=1.000000000000).
- Counterexample: {'x': '0'} → lhs 2.00000000000000000000000000000000000000, rhs 1.00000000000000000000000000000000000000, rel diff 0.5000000000
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:18610:1378159659:237

- Page: [Laplace transform](https://en.wikipedia.org/wiki/Laplace_transform) › Examples and applications > Impulse response  · verdict **FAIL**, symbolic unknown
- LaTeX: `\frac{1}{(s + \alpha)(s + \beta)} = { P \over s + \alpha } + { R \over s+\beta }.`
- Context before: …linear time-invariant system with transfer function $H(s) = \frac{1}{(s + \alpha)(s + \beta)}.$ The impulse response is the inverse Laplace transform of this transfer function: $h(t) = \mathcal{L}^{-1}\{H(s)\}.$ Partial fraction expansion To evaluate this inverse transform, we begin by expanding H(s) using the method of partial fraction expansion,
- Context after: The unknown constants P and R are the residues located at the corresponding poles of the transfer function. Each residue represents the relative contribution of that singularity to the transfer function's overall shape. By the residue theorem, the inverse Laplace transform depends only upon the poles and their residues. To find the residue P, we mu…
- Translator read: `1/((alpha + s)*(beta + s))`  =  `P/(alpha + s) + R/(beta + s)`  · notes: pre:over_choose
pre:trailing_punct
sides: \frac{1}{(s + \alpha)(s + \beta)}  ||  {\frac{ P }{ s + \alpha }} + {\frac{ R }{ s+\beta }}
- Assumptions: domains {'P': 'positive', 'R': 'positive', 'alpha': 'real', 'beta': 'real', 's': 'complex'}; constants {}; constraints ['Ne(alpha + s, 0)', 'Ne(beta + s, 0)']
- Verifier: The identity fails at 72 of 72 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, complex, large) (e.g. at P=0.437631, R=0.391672, alpha=0.627707, beta=0.563643, s=0.185106: lhs=1.643134459172, rhs=1.061517222317).
- Counterexample: {'P': '0.437631', 'R': '0.391672', 'alpha': '0.627707', 'beta': '0.563643', 's': '0.185106'} → lhs 1.64313445917245145039711107874522582223, rhs 1.06151722231727303480414324634029225673, rel diff 0.3539681330
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, complex 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:4376814:1380621682:0

- Page: [Large countable ordinal](https://en.wikipedia.org/wiki/Large_countable_ordinal) › Specific recursive ordinals > Predicative definitions and the Veblen hierarchy  · verdict **FAIL**, symbolic unknown
- LaTeX: `\omega^\alpha = \alpha`
- Context before: …t state the well-ordering of all ordinals below the Bachmann–Howard ordinal is sufficient to obtain all arithmetical consequences of Kripke–Platek set theory. Specific recursive ordinals. Predicative definitions and the Veblen hierarchy. We have already mentioned (see Cantor normal form) the ordinal ε0, which is the smallest satisfying the equation
- Context after: , so it is the limit of the sequence 0, 1, $\omega$ , $\omega^\omega$ , $\omega^{\omega^\omega}$ , ... The next ordinal satisfying this equation is called ε1: it is the limit of the sequence $\varepsilon_0+1, \qquad \omega^{\varepsilon_0+1}=\varepsilon_0\cdot\omega,\qquad\omega^{\omega^{\varepsilon_0+1}}=(\varepsilon_0)^\omega,\qquad\text{etc.}$ Mo…
- Translator read: `omega**alpha`  =  `alpha`  · notes: sides: \omega^\alpha  ||  \alpha
- Assumptions: domains {'alpha': 'real', 'omega': 'positive'}; constants {}; constraints []
- Verifier: The identity fails at 60 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at alpha=0.119541, omega=0.0682403: lhs=0.725471049921, rhs=0.119541000000).
- Counterexample: {'alpha': '0.119541', 'omega': '0.0682403'} → lhs 0.72547104992187779923272682116114906170, rhs 0.11954100000000000000000000000000000000, rel diff 0.8352229216
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:4376814:1380621682:6

- Page: [Large countable ordinal](https://en.wikipedia.org/wiki/Large_countable_ordinal) › Specific recursive ordinals > Predicative definitions and the Veblen hierarchy  · verdict **FAIL**, symbolic unknown
- LaTeX: `\omega^\alpha = \alpha`
- Context before: …ega$ , $\omega^\omega$ , $\omega^{\omega^\omega}$ , ... The next ordinal satisfying this equation is called ε1: it is the limit of the sequence $\varepsilon_0+1, \qquad \omega^{\varepsilon_0+1}=\varepsilon_0\cdot\omega,\qquad\omega^{\omega^{\varepsilon_0+1}}=(\varepsilon_0)^\omega,\qquad\text{etc.}$ More generally, the $\iota$ -th ordinal such that
- Context after: is called $\varepsilon_\iota$ . We could define $\zeta_0$ as the smallest ordinal such that $\varepsilon_\alpha=\alpha$ , but since the Greek alphabet does not have transfinitely many letters it is better to use a more robust notation: define ordinals $\varphi_\gamma(\beta)$ by transfinite induction as follows: let $\varphi_0(\beta) = \omega^\beta$…
- Translator read: `omega**alpha`  =  `alpha`  · notes: sides: \omega^\alpha  ||  \alpha
- Assumptions: domains {'alpha': 'real', 'omega': 'positive'}; constants {}; constraints []
- Verifier: The identity fails at 59 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at alpha=0.259699, omega=0.0532144: lhs=0.466821714547, rhs=0.259699000000).
- Counterexample: {'alpha': '0.259699', 'omega': '0.0532144'} → lhs 0.46682171454764311350172281972809117805, rhs 0.25969900000000000000000000000000000000, rel diff 0.4436869753
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 11/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:19480890:1381118084:59

- Page: [Law of cosines](https://en.wikipedia.org/wiki/Law_of_cosines) › Proofs > By comparing areas  · verdict **FAIL**, symbolic unknown
- LaTeX: `a^2 + b^2 = c^2 + 2ab\cos\gamma.`
- Context before: …law of cosines. The various pieces are in pink, the areas a2, b2 on the left and the areas 2ab cos γ and c2 on the right; in blue, the triangle ABC, on the left and on the right; in grey, auxiliary triangles, all congruent to ABC, an equal number (namely 2) both on the left and on the right. The equality of areas on the left and on the right gives
- Context after: Obtuse case. Figure 7b cuts a hexagon in two different ways into smaller pieces, yielding a proof of the law of cosines in the case that the angle γ is obtuse. We have in pink, the areas a2, b2, and −2ab cos γ on the left and c2 on the right; in blue, the triangle ABC twice, on the left, as well as on the right. The equality of areas on the left an…
- Translator read: `a**2 + b**2`  =  `2*a*b*cos(gamma) + c**2`  · notes: pre:trailing_punct
sides: a^2 + b^2  ||  c^2 + 2ab\cos\gamma
- Assumptions: domains {'a': 'real', 'b': 'real', 'c': 'real', 'gamma': 'positive'}; constants {}; constraints []
- Verifier: The identity fails at 60 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at a=0.237994, b=0.187048, c=0.0324461, gamma=0.0459996: lhs=0.091628098340, rhs=0.089991174581).
- Counterexample: {'a': '0.237994', 'b': '0.187048', 'c': '0.0324461', 'gamma': '0.0459996'} → lhs 0.09162809834000000000000000000000000000, rhs 0.08999117458121285528120692150266957820, rel diff 0.0178648666
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:82359:1378982702:42

- Page: [Least squares](https://en.wikipedia.org/wiki/Least_squares) › Solution > Non-linear least squares  · verdict **FAIL**, symbolic unknown
- LaTeX: `{\beta_j}^{k+1} = {\beta_j}^k+\Delta \beta_j,`
- Context before: …– but in general there is not. In the case of no closed-form solution, numerical algorithms are used to find the value of the parameters $\beta$ that minimizes the objective. Most algorithms involve choosing initial values for the parameters. Then, the parameters are refined iteratively, that is, the values are obtained by successive approximation:
- Context after: where a superscript k is an iteration number, and the vector of increments $\Delta \beta_j$ is called the shift vector. In some commonly used algorithms, at each iteration the model may be linearized by approximation to a first-order Taylor series expansion about $\boldsymbol \beta^k$ :…
- Translator read: `beta_j**(k + 1)`  =  `Delta*beta_j + beta_j**k`  · notes: pre:trailing_punct
sides: {\beta_j}^{k+1}  ||  {\beta_j}^k+\Delta \beta_j
- Assumptions: domains {'Delta': 'positive', 'beta_j': 'real', 'k': 'nonneg_integer'}; constants {}; constraints []
- Verifier: The identity fails at 60 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at Delta=0.193187, beta_j=0.11798, k=0: lhs=0.117980000000, rhs=1.022792202260).
- Counterexample: {'Delta': '0.193187', 'beta_j': '0.11798', 'k': '0'} → lhs 0.11798000000000000000000000000000000000, rhs 1.02279220226000000000000000000000000000, rel diff 0.8846491010
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:17973:1377293254:34

- Page: [Liquid crystal](https://en.wikipedia.org/wiki/Liquid_crystal) › External influences on liquid crystals > Electric and magnetic field effects  · verdict **FAIL**, symbolic unknown
- LaTeX: `\Delta\epsilon > 0`
- Context before: …generated, making possible the emergence of vortices). The difference $\Delta\epsilon = \epsilon_\parallel - \epsilon_\bot$ is called dielectrical anisotropy and is an important parameter in liquid crystal applications. There are both $\Delta\epsilon > 0$ and $\Delta\epsilon < 0$ commercial liquid crystals. 5CB and E7 liquid crystal mixture are two
- Context after: liquid crystals commonly used. MBBA is a common $\Delta\epsilon < 0$ liquid crystal. The effects of magnetic fields on liquid crystal molecules are analogous to electric fields. Because magnetic fields are generated by moving electric charges, permanent magnetic dipoles are produced by electrons moving about atoms. When a magnetic field is applied,…
- Translator read: `Delta*epsilon`  >  `0`  · notes: sides: \Delta\epsilon  ||  0
- Assumptions: domains {'Delta': 'positive', 'epsilon': 'real'}; constants {}; constraints ['epsilon < 0']
- Verifier: The inequality fails at 48 of 48 evaluable points, a clear majority in every regime (small_positive, unit_interval, mixed_sign, large) (e.g. at Delta=0.18472, epsilon=-0.322165: lhs=-0.05951031880, rhs=0).
- Counterexample: {'Delta': '0.18472', 'epsilon': '-0.322165'} → lhs -0.0595103188000000000000000000000000000, rhs 0, rel diff 1.0000000000
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 0/0 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:36423541:1336422728:17

- Page: [List of definite integrals](https://en.wikipedia.org/wiki/List_of_definite_integrals) › Definite integrals involving trigonometric functions  · verdict **FAIL**, symbolic unknown
- LaTeX: `\int_0^{x}\cos^{2m}(t)dt=\frac{(2m-1)!!}{(2m)!!}\Biggl(x-\sin(x)\cos(x)\Biggl(1+\sum_{k=1}^\infty\frac{\cos^{2k}(x)(2k)!!}{(2k+1)!!}\Biggr)\Biggr)\quad\text{for }m=1,2,3\ldots`
- Context before: …x=\int_0^{\frac{\pi}{2}}\cos^{2m}(x)dx = \frac{1\times3\times5\times\cdots\times(2m-1)}{2\times4\times6\times\cdots\times2m}\cdot\frac{\pi}{2}\quad\text{for }m=1,2,3\ldots$ $\int_0^{x}\sin^{2m}(t)dt=\frac{(2m-1)!!}{(2m)!!}\Biggl(x-\sin(x)\cos(x)\Biggl(1+\sum_{k=1}^\infty\frac{\sin^{2k}(x)(2k)!!}{(2k+1)!!}\Biggr)\Biggr)\quad\text{for }m=1,2,3\ldots$
- Context after: $\int_0^{\frac{\pi}{2}}\sin^{2m+1}(x)dx=\int_0^{\frac{\pi}{2}}\cos^{2m+1}(x)dx = \frac{2\times4\times6\times\cdots\times2m}{1\times3\times5\times\cdots\times(2m+1)}\quad\text{for }m=1,2,3\ldots$ $\int_0^{\frac{\pi}{2}}\sin^{2p-1}(x)\cos^{2q-1}(x)dx = \frac{\Gamma(p)\Gamma(q)}{2\Gamma(p+q)}=\frac{1}{2} \text{B}(p,q)$…
- Translator read: `Integral(cos(t)**(2*m), (t, 0, x))`  =  `(x - (Sum(cos(x)**(2*k)*factorial2(2*k)/factorial2(2*k + 1), (k, 1, oo)) + 1)*sin(x)*cos(x))*factorial2(2*m - 1)/factorial2(2*m)`  · notes: pre:size
pre:spacing
cond: m=1,2,3\ldots
sides: \int_0^{x}\cos^{2m}(t)dt  ||  \frac{(2m-1)!!}{(2m)!!}\Biggl(x-\sin(x)\cos(x)\Biggl(1+\sum_{k=1}^\infty\frac{\cos^{2k}(x)(2k)!!}{(2k+1)!!}\Biggr)\Biggr)
- Assumptions: domains {'m': 'positive_integer', 'x': 'real'}; constants {}; constraints []
- Verifier: The identity fails at 20 of 20 evaluable points, a clear majority in every regime (unit_interval, integers_small, mixed_sign) (e.g. at m=1, x=0.353433: lhs=0.339079966913, rhs=-0.43196516339) [symbolic check timed out].
- Counterexample: {'m': '1', 'x': '0.353433'} → lhs 0.33907996691353549597336645203936401969, rhs -0.4319651633974483096156608458198757210, rel diff 1.7849706310
- Regimes: small_positive 4/5 fail, 1 err, unit_interval 5/5 fail, 0 err, integers_small 5/5 fail, 0 err, mixed_sign 5/5 fail, 0 err, large 1/5 fail, 4 err

---
## wiki:en:36423541:1336422728:28

- Page: [List of definite integrals](https://en.wikipedia.org/wiki/List_of_definite_integrals) › Definite integrals involving trigonometric functions  · verdict **FAIL**, symbolic unknown
- LaTeX: `\int_0^\infty \frac{x \sin mx}{x^2+a^2}\ dx=\frac{\pi}{2}e^{-ma}`
- Context before: …$\int_{0}^{\infty} \frac{\sin ^{2}px}{x^{2}}\ dx=\frac{\pi p}{2}$ $\int_{0}^{\infty} \frac{1-\cos px}{x^{2}}\ dx=\frac{\pi p}{2}$ $\int_{0}^{\infty} \frac{\cos px - \cos qx}{x}\ dx= \ln \frac {q}{p}$ $\int_{0}^{\infty} \frac{\cos px - \cos qx}{x^{2}}\ dx=\frac{\pi (q-p)}{2}$ $\int_{0}^{\infty} \frac{\cos mx}{x^{2}+a^{2}}\ dx=\frac{\pi}{2a}e^{-ma}$
- Context after: $\int_0^\infty \frac{ \sin mx}{x(x^2+a^2)}\ dx=\frac{\pi}{2a^2}\left(1-e^{-ma}\right)$ $\int_0^{2\pi} \frac{dx}{a+b\sin x}=\frac{2\pi}{\sqrt{a^2-b^2}}$ $\int_0^{2\pi} \frac{dx}{a+b\cos x}=\frac{2\pi}{\sqrt{a^2-b^2}}$ $\int_0^{\frac{\pi}{2}} \frac{dx}{a+b\cos x}=\frac{\cos^{-1} \left(\dfrac{b}{a}\right) }{\sqrt{a^2-b^2}}$…
- Translator read: `Integral(x*sin(m*x)/(a**2 + x**2), (x, 0, oo))`  =  `pi/(2*e**(a*m))`  · notes: pre:spacing
implicit_function_arg
hint:e_only_as_exp_base
sides: \int_0^\infty \frac{x \sin mx}{x^2+a^2}\ dx  ||  \frac{\pi}{2}e^{-ma}
- Assumptions: domains {'a': 'real', 'm': 'nonneg_integer'}; constants {'e': 'E'}; constraints []
- Verifier: The identity fails at 15 of 15 evaluable points, a clear majority in every regime (unit_interval, mixed_sign) (e.g. at a=0.126879, m=0: lhs=0, rhs=1.570796326794).
- Counterexample: {'a': '0.126879', 'm': '0'} → lhs 0, rhs 1.57079632679489661923132169163975144209, rel diff 1.0000000000
- Regimes: small_positive 0/40 fail, 40 err, unit_interval 6/29 fail, 23 err, integers_small 3/36 fail, 33 err, mixed_sign 6/28 fail, 22 err, large 0/40 fail, 40 err

---
## wiki:en:41302121:1380738944:81

- Page: [List of mathematical constants](https://en.wikipedia.org/wiki/List_of_mathematical_constants) › List  · verdict **FAIL**, symbolic unknown
- LaTeX: `\cos x = x`
- Context before: …1860 ? ? ? ? Catalan's constant $G$ 0.91596 55941 77219 01505 $\beta(2)=\sum_{n=0}^\infty\frac{(-1)^n}{(2n+1)^2} = \frac{1}{1^2}-\frac{1}{3^2} + \frac{1}{5^2} - \frac{1}{7^2} + \frac{1}{9^2} + \cdots$ with the Dirichlet beta function $\beta(s)$ 1864 ? ? ✓ ✓ Dottie number $D$ 0.73908 51332 15160 64165 Real root of
- Context after: 1865 ✗ ✗ ? ? Meissel–Mertens constant $M$ 0.26149 72128 47642 78375 $\lim_{n\to\infty}\left(\sum_{p\le n}\frac{1}{p}-\ln\ln n\right) = \gamma + \sum_{p}\left(\ln\left(1 - \frac{1}{p}\right) + \frac{1}{p}\right)$ where γ is the Euler–Mascheroni constant and p is prime 1866 & 1873 ? ? ? ? Universal parabolic constant $P$ 2.29558 71493 92638 07403…
- Translator read: `cos(x)`  =  `x`  · notes: sides: \cos x  ||  x
- Assumptions: domains {'x': 'real'}; constants {}; constraints []
- Verifier: The identity fails at 60 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at x=0.0882817: lhs=0.996105700944, rhs=0.088281700000).
- Counterexample: {'x': '0.0882817'} → lhs 0.99610570094488900559890898135349154630, rhs 0.08828170000000000000000000000000000000, rel diff 0.9113731605
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:41302121:1380738944:131

- Page: [List of mathematical constants](https://en.wikipedia.org/wiki/List_of_mathematical_constants) › List  · verdict **FAIL**, symbolic unknown
- LaTeX: `\frac{1}{\sqrt{2\pi}}\int_{-\infty}^{z} e^{-x^2/2} \, \mathrm{d}x = 0.975`
- Context before: …are $\frac{\sqrt{3}}{4}+2\times10^{-4}\leq B\leq \sqrt{\frac{\sqrt{3}-1}{2}}\cdot\frac{\Gamma(\frac{1}{3})\Gamma(\frac{11}{12})}{\Gamma(\frac{1}{4})}$ 1925 ? ? ? ? Z score for the 97.5 percentile point $z_{.975}$ 1.95996 39845 40054 23552 $\sqrt{2}\operatorname{erf}^{-1}(0.95)$ where erf−1(x) is the inverse error function Real number $z$ such that
- Context after: 1925 ? ? ? ? Landau's constant $L$ $0.5 < L \le 0.54326$ The best known bounds are $0.5 < L \le \frac{\Gamma(\frac{1}{3})\Gamma(\frac{5}{6})}{\Gamma(\frac{1}{6})}$ . 1929 ? ? ? ? Landau's third constant $A$ $0.5 < A \le 0.7853$ 1929 ? ? ? ? Prouhet–Thue–Morse constant $\tau$ 0.41245 40336 40107 59778…
- Translator read: `sqrt(2)*Integral(e**(-x**2/2), (x, -oo, z))/(2*sqrt(pi))`  =  `39/40`  · notes: pre:spacing
hint:e_only_as_exp_base
sides: \frac{1}{\sqrt{2\pi}}\int_{-\infty}^{z} e^{-x^2/2} \, \mathrm{d}x  ||  0.975
- Assumptions: domains {'z': 'complex'}; constants {'e': 'E'}; constraints []
- Verifier: The identity fails at 36 of 36 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, complex, large) (e.g. at z=0.0674758: lhs=0.526898536544, rhs=0.975000000000).
- Counterexample: {'z': '0.0674758'} → lhs 0.52689853654431514319663667910259126841, rhs 0.97500000000000000000000000000000000000, rel diff 0.4595912445
- Regimes: small_positive 6/6 fail, 0 err, unit_interval 6/6 fail, 0 err, integers_small 6/6 fail, 0 err, mixed_sign 6/6 fail, 0 err, complex 6/6 fail, 0 err, large 6/20 fail, 14 err

---
## wiki:en:41302121:1380738944:256

- Page: [List of mathematical constants](https://en.wikipedia.org/wiki/List_of_mathematical_constants) › List  · verdict **FAIL**, symbolic not_equal
- LaTeX: `\frac{\Gamma(\tfrac14)^2}{4 \pi^{3/2}}=\frac{\varpi}{\pi\sqrt{2}}`
- Context before: …1999 ? ? ? ? Foias constant $\alpha$ 1.18745 23511 26501 05459 The unique real number α such that if x1 = α then the sequence $x_{n+1} = \left( 1 + \frac{1}{x_n} \right)^n\text{ for }n=1,2,3,\ldots$ diverges to infinity 2000 ? ? ? ? Logarithmic capacity of the unit disk 0.59017 02995 08048 11302
- Context after: where $\varpi$ is the lemniscate constant Before 2003 ✗ ✗ ? ✓ Taniguchi constant $C_T$ 0.67823 44919 17391 97803 $\prod_{p\text{ prime}} \left(1 - \frac{3}{p^3}+\frac{2}{p^4}+\frac{1}{p^5}-\frac{1}{p^6}\right)$ Before 2005 ? ? ? ? Mathematical constants sorted by their representations as continued fractions. The following list includes the continue…
- Translator read: `gamma(1/4)**2/(4*pi**(3/2))`  =  `sqrt(2)*varpi/(2*pi)`  · notes: sides: \frac{\Gamma(\tfrac14)^2}{4 \pi^{3/2}}  ||  \frac{\varpi}{\pi\sqrt{2}}
- Assumptions: domains {}; constants {'varpi': 'pi'}; constraints []
- Verifier: The constant identity does not hold: both sides differ beyond 1e-8 relative error, stably at two working precisions (lhs=0.5901702995080481, rhs=0.7071067811865475).
- Counterexample: {} → lhs 0.59017029950804811302266897027924429361, rhs 0.70710678118654752440084436210484903928, rel diff 0.1653731583
- Regimes: constant 1/1 fail, 0 err
