# Review batch 002 — 22 items

For each item answer with one JSON line (Finding schema): {"formula_id": ..., "verdict": "FAIL", "review": {"status": "confirmed_error"|"false_positive"|"ambiguous", "reviewer": "<name>", "notes": "<why, one or two sentences>"}, "suggested_fix": "<corrected LaTeX or null>", "evidence": "<independent source or derivation>"}


---
## wiki:en:238686:1378219065:16

- Page: [Binary number](https://en.wikipedia.org/wiki/Binary_number) › Conversion to and from other numeral systems > Binary to decimal  · verdict **FAIL**, symbolic not_equal
- LaTeX: `\frac{2}{3} \times 2 = 1\frac{1}{3} \ge 1`
- Context before: …hm: Repeatedly double the number to be converted, record if the result is at least 1, and then throw away the integer part. For example, $(\frac{1}{3})_{10}$ , in binary, is: Converting Result $\frac{1}{3}$ 0. $\frac{1}{3} \times 2 = \frac{2}{3} < 1$ 0.0 $\frac{2}{3} \times 2 = 1\frac{1}{3} \ge 1$ 0.01 $\frac{1}{3} \times 2 = \frac{2}{3} < 1$ 0.010
- Context after: 0.0101 Thus the repeating decimal fraction 0.3... is equivalent to the repeating binary fraction 0.01... . Or for example, 0.110, in binary, is: Converting Result 0.1 0. 0.1 × 2 = 0.2 < 1 0.0 0.2 × 2 = 0.4 < 1 0.00 0.4 × 2 = 0.8 < 1 0.000 0.8 × 2 = 1.6 ≥ 1 0.0001 0.6 × 2 = 1.2 ≥ 1 0.00011 0.2 × 2 = 0.4 < 1 0.000110 0.4 × 2 = 0.8 < 1 0.0001100 0.8 ×…
- Translator read (piece 0): `4/3`  =  `1/3`  · notes: op:times
sides: \frac{2}{3} \times 2  ||  1\frac{1}{3}
- Translator read (piece 1): `1/3`  >=  `1`  · notes: op:times
sides: 1\frac{1}{3}  ||  1
- Assumptions: domains {}; constants {}; constraints []
- Verifier: Chain link 0: The constant identity does not hold: both sides differ beyond 1e-8 relative error, stably at two working precisions (lhs=1.3333333333333333, rhs=0.3333333333333333).
- Counterexample: {} → lhs 1.33333333333333333333333333333333333333, rhs 0.33333333333333333333333333333333333333, rel diff 0.7500000000
- Regimes: constant 1/1 fail, 0 err

---
## wiki:en:4668:1376065730:236

- Page: [Binomial coefficient](https://en.wikipedia.org/wiki/Binomial_coefficient) › Generalizations > Multiset (rising) binomial coefficient > Generalization to negative integers n  · verdict **FAIL**, symbolic not_equal
- LaTeX: `\begin{align}\binom{-4}{7} &= \frac
{-10\cdot-9\cdot-8\cdot-7\cdot-6\cdot-5\cdot-4}
{1\cdot2\cdot3\cdot4\cdot5\cdot6\cdot7}\\
&=(-1)^7\;\frac{4\cdot5\cdot6\cdot7\cdot8\cdot9\cdot10}
{1\cdot2\cdot3\cdot4\cdot5\cdot6\cdot7}\\
&=\left(\!\!\binom{-7}{7}\!\!\right)\left(\!\!\binom{4}{7}\!\!\right)=\binom{-1}{7}\binom{10}{7}.\end{align}`
- Context before: …In particular, binomial coefficients evaluated at negative integers n are given by signed multiset coefficients. In the special case $n = -1$ , this reduces to $(-1)^k=\binom{-1}{k}=\left(\!\!\binom{-k}{k}\!\!\right)$ . For example, if and , then and :
- Context after: Two real or complex valued arguments. The binomial coefficient is generalized to two real or complex valued arguments using the gamma function or beta function via $\binom{x}{y}= \frac{\Gamma(x+1)}{\Gamma(y+1) \Gamma(x-y+1)}= \frac{1}{(x+1) \Beta(y+1, x-y+1)}.$ This definition inherits these following additional properties from $\Gamma$ :…
- Translator read (piece 0): `-120`  =  `-120`  · notes: pre:left_right
pre:spacing
pre:env_align
pre:row_continues_chain
pre:trailing_punct
sides: \binom{-4}{7}  ||  \frac {-10\cdot-9\cdot-8\cdot-7\cdot-6\cdot-5\cdot-4} {1\cdot2\cdot3\cdot4\cdot5\cdot6\cdot7}
- Translator read (piece 1): `-120`  =  `-120`  · notes: pre:left_right
pre:spacing
pre:env_align
pre:row_continues_chain
pre:trailing_punct
sides: \frac {-10\cdot-9\cdot-8\cdot-7\cdot-6\cdot-5\cdot-4} {1\cdot2\cdot3\cdot4\cdot5\cdot6\cdot7}  ||  (-1)^7\;\frac{4\cdot5\cdot6\cdot7\cdot8\cdot9\cdot10} {1\cdot2\cdot3\cdot4\cdot5\cdot6\cdot7}
- Translator read (piece 2): `-120`  =  `0`  · notes: pre:left_right
pre:spacing
pre:env_align
pre:row_continues_chain
pre:trailing_punct
sides: (-1)^7\;\frac{4\cdot5\cdot6\cdot7\cdot8\cdot9\cdot10} {1\cdot2\cdot3\cdot4\cdot5\cdot6\cdot7}  ||  (\!\!\binom{-7}{7}\!\!\right)\left(\!\!\binom{4}{7}\!\!\right)
- Translator read (piece 3): `0`  =  `-120`  · notes: pre:left_right
pre:spacing
pre:env_align
pre:row_continues_chain
pre:trailing_punct
sides: (\!\!\binom{-7}{7}\!\!\right)\left(\!\!\binom{4}{7}\!\!\right)  ||  \binom{-1}{7}\binom{10}{7}
- Assumptions: domains {}; constants {}; constraints []
- Verifier: Chain link 2: The constant identity does not hold: both sides differ beyond 1e-8 relative error, stably at two working precisions (lhs=-120.0000000000000, rhs=0).
- Counterexample: {} → lhs -120.00000000000000000000000000000000000, rhs 0, rel diff 1.0000000000
- Regimes: constant 1/1 fail, 0 err

---
## wiki:en:4668:1376065730:256

- Page: [Binomial coefficient](https://en.wikipedia.org/wiki/Binomial_coefficient) › Generalizations > Generalization to infinite cardinals  · verdict **FAIL**, symbolic unknown
- LaTeX: `\binom{\alpha}{\alpha} = 2^{\alpha}`
- Context before: …that the generalized binomial coefficient is well-defined, in the sense that no matter what set we choose to represent the cardinal number $\alpha$ , ${\alpha \choose \beta}$ will remain the same. For finite cardinals, this definition coincides with the standard definition of the binomial coefficient. Assuming the Axiom of Choice, one can show that
- Context after: for any infinite cardinal $\alpha$ . See also. Binomial transform Delannoy number Eulerian number Hypergeometric function List of factorial and binomial topics Macaulay representation of an integer Motzkin number Multiplicities of entries in Pascal's triangle Narayana number Star of David theorem Sun's curious identity Table of Newtonian series Tri…
- Translator read: `binomial(alpha, alpha)`  =  `2**alpha`  · notes: sides: \binom{\alpha}{\alpha}  ||  2^{\alpha}
- Assumptions: domains {'alpha': 'real'}; constants {}; constraints []
- Verifier: The identity fails at 59 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at alpha=0.0067705: lhs=1.000000000000, rhs=1.004703982136).
- Counterexample: {'alpha': '0.0067705'} → lhs 1.00000000000000000000000000000000000000, rhs 1.00470398213619045321426361475326839153, rel diff 0.0046819582
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 11/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:4677:1377889688:129

- Page: [Binomial theorem](https://en.wikipedia.org/wiki/Binomial_theorem) › Applications > Multiple-angle identities  · verdict **FAIL**, symbolic unknown
- LaTeX: `\left(\cos x + i\sin x\right)^3 = \cos^3 x + 3i \cos^2 x \sin x - 3 \cos x \sin^2 x - i \sin^3 x,`
- Context before: …s x + i\sin x\right)^2 = \cos^2 x + 2i \cos x \sin x - \sin^2 x = (\cos^2 x-\sin^2 x) + i(2\cos x\sin x),$ But De Moivre's formula identifies the left side with $(\cos x+i\sin x)^2 = \cos(2x)+i\sin(2x)$ , so $\cos(2x) = \cos^2 x - \sin^2 x \quad\text{and}\quad\sin(2x) = 2 \cos x \sin x,$ which are the usual double-angle identities. Similarly, since
- Context after: De Moivre's formula yields $\cos(3x) = \cos^3 x - 3 \cos x \sin^2 x \quad\text{and}\quad \sin(3x) = 3\cos^2 x \sin x - \sin^3 x.$ In general, $\cos(nx) = \sum_{k\text{ even}} (-1)^{k/2} {\binom{n}{k}}\cos^{n-k} x \sin^k x$ and $\sin(nx) = \sum_{k\text{ odd}} (-1)^{(k-1)/2} {\binom{n}{k}}\cos^{n-k} x \sin^k x.$ There are also similar formulas using…
- Translator read: `(i*sin(x) + cos(x))**3`  =  `-i*sin(x)**3 + 3*i*sin(x)*cos(x)**2 - 3*sin(x)**2*cos(x) + cos(x)**3`  · notes: pre:left_right
pre:trailing_punct
hint:i_present
sides: (\cos x + i\sin x\right)^3  ||  \cos^3 x + 3i \cos^2 x \sin x - 3 \cos x \sin^2 x - i \sin^3 x
- Assumptions: domains {'i': 'nonneg_integer', 'x': 'real'}; constants {}; constraints []
- Verifier: The identity fails at 60 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at i=0, x=0.263367: lhs=0.900082575389, rhs=0.703773566381).
- Counterexample: {'i': '0', 'x': '0.263367'} → lhs 0.90008257538969788206872228421719027082, rhs 0.70377356638188086870595247861319633825, rel diff 0.2181011102
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:1207070:1375349641:39

- Page: [Biquaternion](https://en.wikipedia.org/wiki/Biquaternion) › Associated terminology  · verdict **FAIL**, symbolic unknown
- LaTeX: `\exp(ahr) = \cosh(a) + hr\ \sinh(a),\quad a \in R.`
- Context before: …of the sphere of square roots of minus one in the real quaternion subalgebra H. Then and the plane of biquaternions given by $D_r = \lbrace z = x + yhr : x, y \in \mathbb R \rbrace$ is a commutative subalgebra isomorphic to the plane of split-complex numbers. Just as the ordinary complex plane has a unit circle, $D_r$ has a unit hyperbola given by
- Context after: Just as the unit circle turns by multiplication through one of its elements, so the hyperbola turns because $\exp(ahr) \exp(bhr) = \exp((a+b)hr).$ Hence these algebraic operators on the hyperbola are called hyperbolic versors. The unit circle in C and unit hyperbola in Dr are examples of one-parameter groups. For every square root r of minus one in…
- Translator read: `exp(a*h*r)`  =  `h*r*sinh(a) + cosh(a)`  · notes: pre:spacing
pre:trailing_punct
cond: a \in R
sides: \exp(ahr)  ||  \cosh(a) + hr\ \sinh(a)
- Assumptions: domains {'a': 'real', 'h': 'positive', 'r': 'nonneg'}; constants {}; constraints []
- Verifier: The identity fails at 60 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at a=0.0930195, h=0.0599641, r=0.0733242: lhs=1.000409073614, rhs=1.004739014116).
- Counterexample: {'a': '0.0930195', 'h': '0.0599641', 'r': '0.0733242'} → lhs 1.00040907361427650807385667193188337507, rhs 1.00473901411634532065258597793177145317, rel diff 0.0043095176
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:357657:1376907021:73

- Page: [Bloch's theorem](https://en.wikipedia.org/wiki/Bloch's_theorem) › Proof > Using group theory  · verdict **FAIL**, symbolic unknown
- LaTeX: `e^{i k_1 n_1 a_1} = e^{i k_1 ( n_1 a_1 + L_1)}`
- Context before: …ing the band structure, spectrum and specific heats of crystals given a specific crystal group symmetry like FCC or BCC and eventually an extra basis. In this proof it is also possible to notice how it is key that the extra point group is driven by a symmetry in the effective potential but it shall commute with the Hamiltonian. [math proof | proof]
- Context after: In the generalized version of the Bloch theorem, the Fourier transform, i.e. the wave function expansion, gets generalized from a discrete Fourier transform which is applicable only for cyclic groups, and therefore translations, into a character expansion of the wave function where the characters are given from the specific finite point group. Also…
- Translator read: `e**(a_1*i*k_1*n_1)`  =  `e**(i*k_1*(L_1 + a_1*n_1))`  · notes: hint:e_only_as_exp_base
hint:i_present
sides: e^{i k_1 n_1 a_1}  ||  e^{i k_1 ( n_1 a_1 + L_1)}
- Assumptions: domains {'L_1': 'positive', 'a_1': 'real', 'k_1': 'nonneg_integer', 'n_1': 'nonneg_integer'}; constants {'e': 'E', 'i': 'I'}; constraints []
- Verifier: The identity fails at 57 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at L_1=0.958472, a_1=0.73225, k_1=1, n_1=1: lhs=(0.74367206071, rhs=(-0.1196384146).
- Counterexample: {'L_1': '0.958472', 'a_1': '0.73225', 'k_1': '1', 'n_1': '1'} → lhs (0.7436720607102118854343542561155463316, rhs (-0.119638414674465206453093705261521634, rel diff 0.9222027534
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 11/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 10/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:24158072:1354478531:9

- Page: [Boole's rule](https://en.wikipedia.org/wiki/Boole's_rule) › Formula > Composite Boole's rule  · verdict **FAIL**, symbolic not_equal
- LaTeX: `4 = 0`
- Context before: …om Abramowitz and Stegun. The following constitutes a very simple implementation of the method in Common Lisp which ignores the error term: Composite Boole's rule. In cases where the integration is permitted to extend over equidistant sections of the interval $[a, b]$ , the composite Boole's rule might be applied. Given $N$ divisions, where $N$ mod
- Context after: , the integrated value amounts to $\int_{x_0}^{x_N} f(x)\,dx = \frac{2h}{45} \left[7\big(f(x_0) + f(x_N)\big) + 32 \sum_{i \in \{1, 3, 5, \ldots, N - 1\}} f(x_i) + 12 \sum_{i \in \{2, 6, 10, \ldots, N - 2\}} f(x_i) + 14 \sum_{i \in \{4, 8, 12, \ldots, N - 4\}} f(x_i) \right] + \text{error term},$ where the error term is similar to above. The follow…
- Translator read: `4`  =  `0`  · notes: sides: 4  ||  0
- Assumptions: domains {}; constants {}; constraints []
- Verifier: The constant identity does not hold: both sides differ beyond 1e-8 relative error, stably at two working precisions (lhs=4.0000000000000000, rhs=0).
- Counterexample: {} → lhs 4.00000000000000000000000000000000000000, rhs 0, rel diff 1.0000000000
- Regimes: constant 1/1 fail, 0 err

---
## wiki:en:171882:1354539070:11

- Page: [Calculus of variations](https://en.wikipedia.org/wiki/Calculus_of_variations) › Extrema  · verdict **FAIL**, symbolic unknown
- LaTeX: `\Delta J \leq 0`
- Context before: …e elements $y$ of a given function space defined over a given domain. A functional $J[y]$ is said to have an extremum at the function $f$ if $\Delta J = J[y] - J[f]$ has the same sign for all $y$ in an arbitrarily small neighborhood of $f.$ The function $f$ is called an extremal function or extremal. The extremum $J[f]$ is called a local maximum if
- Context after: everywhere in an arbitrarily small neighborhood of $f,$ and a local minimum if $\Delta J \geq 0$ there. For a function space of continuous functions, extrema of corresponding functionals are called strong extrema or weak extrema, depending on whether the first derivatives of the continuous functions are respectively all continuous or not. Both stro…
- Translator read: `Delta*J`  <=  `0`  · notes: sides: \Delta J  ||  0
- Assumptions: domains {'Delta': 'positive', 'J': 'nonneg'}; constants {}; constraints ['J >= 0']
- Verifier: The inequality fails at 59 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at Delta=0.0593581, J=0.0834067: lhs=0.004950863239, rhs=0).
- Counterexample: {'Delta': '0.0593581', 'J': '0.0834067'} → lhs 0.00495086323927000000000000000000000000, rhs 0, rel diff 1.0000000000
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 11/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:514534:1350723541:38

- Page: [Canonical transformation](https://en.wikipedia.org/wiki/Canonical_transformation) › Conditions for restricted canonical transformation > Symplectic condition  · verdict **FAIL**, symbolic unknown
- LaTeX: `J^{-1}=-J`
- Context before: …symplectic condition as: $M J M^T = J$ The left hand side of the above is called the Poisson matrix of $\varepsilon$ , denoted as $\mathcal P(\varepsilon) = MJM^T$ . Similarly, a Lagrange matrix of $\eta$ can be constructed as $\mathcal L(\eta) = M^TJM$ . It can be shown that the symplectic condition is also equivalent to $M^T J M = J$ by using the
- Context after: property. The set of all matrices $M$ which satisfy symplectic conditions form a symplectic group. The symplectic conditions are equivalent with indirect conditions as they both lead to the equation $\dot{\varepsilon}= J \nabla_\varepsilon H$ , which is used in both of the derivations. Invariance of the Poisson bracket. The Poisson bracket which is…
- Translator read: `1/J`  =  `-J`  · notes: sides: J^{-1}  ||  -J
- Assumptions: domains {'J': 'positive'}; constants {}; constraints []
- Verifier: The identity fails at 60 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at J=0.0505177: lhs=19.79504213374, rhs=-0.05051770000).
- Counterexample: {'J': '0.0505177'} → lhs 19.7950421337471816808762077450081852499, rhs -0.0505177000000000000000000000000000000, rel diff 1.0025520380
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:51426:1375662524:18

- Page: [Cantor's diagonal argument](https://en.wikipedia.org/wiki/Cantor's_diagonal_argument) › Consequences > Ordering of cardinals  · verdict **FAIL**, symbolic unknown
- LaTeX: `|2^S|=|{\mathcal P}(S)|`
- Context before: …natives such as the negation of Cantor's preorder, or a definition in terms of assigned ordinals). Also $|S|<|{\mathcal P}(S)|$ in this sense, as has been shown, and at the same time it is the case that $\neg(|{\mathcal P}(S)|\le|S|)$ , for all sets $S$ . Assuming the law of excluded middle, characteristic functions surject onto powersets, and then
- Context after: . So the uncountable $2^{\mathbb N}$ is also not enumerable and it can also be mapped onto ${\mathbb N}$ . Classically, the Schröder–Bernstein theorem is valid and says that any two sets which are in the injective image of one another are in bijection as well. Here, every unbounded subset of ${\mathbb N}$ is then in bijection with ${\mathbb N}$ its…
- Translator read: `2**re(S)`  =  `Abs(S*cal_P)`  · notes: styled_symbol:cal_P
sides: |2^S|  ||  |{\mathcal P}(S)|
- Assumptions: domains {'S': 'positive', 'cal_P': 'positive'}; constants {}; constraints []
- Verifier: The identity fails at 60 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at S=0.0590205, cal_P=0.093453: lhs=1.041758231784, rhs=0.005515642786).
- Counterexample: {'S': '0.0590205', 'cal_P': '0.093453'} → lhs 1.04175823178456525644385567985505686130, rhs 0.00551564278650000000000000000000000000, rel diff 0.9947054483
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:6173:1380852941:33

- Page: [Cardinal number](https://en.wikipedia.org/wiki/Cardinal_number) › Motivation  · verdict **FAIL**, symbolic not_equal
- LaTeX: `\aleph_0 + 1 = \aleph_0`
- Context before: …ection between the sets $\{1,2,3,...\}$ and $\{2,3,4,...\}$ , and thus they have the same cardinality $\aleph_0$ , despite the second being a proper subset of the first. Therefore the intuition that the size of a proper subset of $X$ is always strictly less than the size of $X$ is usually only valid for finite sets. Conversely, this also shows that
- Context after: (the cardinality of $\{2,3,4,...\}$ plus the cardinality of $\{1\}$ is equal to the cardinality of $\{1,2,3,...\}$ ), and thus the "plus one" operation does not always construct a new cardinal number as it does for natural numbers. However, Cantor's diagonal argument shows that the power set operation always results in a strictly greater cardinalit…
- Translator read: `aleph_0 + 1`  =  `aleph_0`  · notes: sides: \aleph_0 + 1  ||  \aleph_0
- Assumptions: domains {'aleph_0': 'positive'}; constants {}; constraints []
- Verifier: The identity fails at 60 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at aleph_0=0.0565157: lhs=1.056515700000, rhs=0.056515700000).
- Counterexample: {'aleph_0': '0.0565157'} → lhs 1.05651570000000000000000000000000000000, rhs 0.05651570000000000000000000000000000000, rel diff 0.9465074678
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:6173:1380852941:79

- Page: [Cardinal number](https://en.wikipedia.org/wiki/Cardinal_number) › Constructive definition > Von Neumann cardinal assignment  · verdict **FAIL**, symbolic unknown
- LaTeX: `2^\omega=\omega<\omega^2`
- Context before: …inality of any countable set) as $\aleph_0$ . The von Neumann cardinal assignment identifies $\omega_{\alpha}$ with $\aleph_{\alpha}$ , but the notation $\aleph_{\alpha}$ is used for writing cardinals, and $\omega_{\alpha}$ for writing ordinals. This is important because arithmetic on cardinals is different from arithmetic on ordinals. For example,
- Context after: in ordinal arithmetic while $2^{\aleph_0}>\aleph_0=\aleph_0^2$ in cardinal arithmetic, even though under the von Neumann cardinal assignment $\aleph_0$ and $\omega$ are represented by the same set. Also, $\omega_{1}$ is the smallest uncountable ordinal (to see that it exists, consider the set of equivalence classes of well-orderings of the natural…
- Translator read (piece 0): `2**omega`  =  `omega`  · notes: sides: 2^\omega  ||  \omega
- Translator read (piece 1): `omega`  <  `omega**2`  · notes: sides: \omega  ||  \omega^2
- Assumptions: domains {'omega': 'positive'}; constants {}; constraints []
- Verifier: Chain link 0: The identity fails at 60 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at omega=0.0318242: lhs=1.022303949891, rhs=0.031824200000).
- Counterexample: {'omega': '0.0318242'} → lhs 1.02230394989139232586483921185057811531, rhs 0.03182420000000000000000000000000000000, rel diff 0.9688701192
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:1574901:1369454080:33

- Page: [Cardinality of the continuum](https://en.wikipedia.org/wiki/Cardinality_of_the_continuum) › Properties > Cardinal equalities  · verdict **FAIL**, symbolic unknown
- LaTeX: `\mathfrak c ^{\mathfrak c}  =  (2^{\aleph_0})^{\mathfrak c}  = 2^{\mathfrak c\times\aleph_0} = 2^{\mathfrak c}`
- Context before: …cardinal arithmetic: $\mathfrak{c}^2 = (2^{\aleph_0})^2 = 2^{2\times{\aleph_0}} = 2^{\aleph_0} = \mathfrak{c}.$ By using the rules of cardinal arithmetic, one can also show that $\mathfrak c^{\aleph_0} = {\aleph_0}^{\aleph_0} = n^{\aleph_0} = \mathfrak c^n = \aleph_0 \mathfrak c = n \mathfrak c = \mathfrak c$ where n is any finite cardinal ≥ 2 and
- Context after: where $2 ^{\mathfrak c}$ is the cardinality of the power set of R, and $2 ^{\mathfrak c} > \mathfrak c$ . Alternative explanation for . Every real number has at least one infinite decimal expansion. For example, 1/2 = 0.50000... 1/3 = 0.33333... π = 3.14159.... (This is true even in the case the expansion repeats, as in the first two examples.) In…
- Translator read (piece 0): `frak_c**frak_c`  =  `(2**aleph_0)**frak_c`  · notes: styled_symbol:frak_c
op:times
sides: \mathfrak c ^{\mathfrak c}  ||  (2^{\aleph_0})^{\mathfrak c}
- Translator read (piece 1): `(2**aleph_0)**frak_c`  =  `2**(aleph_0*frak_c)`  · notes: styled_symbol:frak_c
op:times
sides: (2^{\aleph_0})^{\mathfrak c}  ||  2^{\mathfrak c\times\aleph_0}
- Translator read (piece 2): `2**(aleph_0*frak_c)`  =  `2**frak_c`  · notes: styled_symbol:frak_c
op:times
sides: 2^{\mathfrak c\times\aleph_0}  ||  2^{\mathfrak c}
- Assumptions: domains {'aleph_0': 'positive', 'frak_c': 'positive'}; constants {}; constraints []
- Verifier: Chain link 0: The identity fails at 60 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at aleph_0=0.0518412, frak_c=0.102804: lhs=0.791463110208, rhs=1.003700947580).
- Counterexample: {'aleph_0': '0.0518412', 'frak_c': '0.102804'} → lhs 0.79146311020850835802645862734155680331, rhs 1.00370094758048938983627703691138680112, rel diff 0.2114552525
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:853175:1371650040:48

- Page: [Characterizations of the exponential function](https://en.wikipedia.org/wiki/Characterizations_of_the_exponential_function) › Proof that each characterization makes sense > Characterization 6  · verdict **FAIL**, symbolic unknown
- LaTeX: `\lim_{h \to 0} \frac{a^h - 1}{h} = 1.`
- Context before: …$\begin{align} \int_1^\infty \frac{dt} t & = \infty \\[8pt] \int_1^0 \frac{dt} t & = -\infty \end{align}$ hold, then it is surjective as well. Indeed, these integrals do hold; they follow from the integral test and the divergence of the harmonic series. Characterization 6. The definition depends on the unique positive real number $a=e$ satisfying:
- Context after: This limit can be shown to exist for any $a$ , and it defines a continuous increasing function $f(a)=\ln(a)$ with $f(1)=0$ and $\lim_{a\to\infty}f(a) = \infty$ , so the Intermediate value theorem guarantees the existence of such a value $a=e$ . Equivalence of the characterizations. The following arguments demonstrate the equivalence of the above ch…
- Translator read: `Limit((a**h - 1)/h, h, 0, dir='+-')`  =  `1`  · notes: pre:trailing_punct
sides: \lim_{h \to 0} \frac{a^h - 1}{h}  ||  1
- Assumptions: domains {'a': 'real'}; constants {}; constraints ['a > 0']
- Verifier: The identity fails at 59 of 59 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at a=0.0793616: lhs=-2.53374065491, rhs=1.000000000000).
- Counterexample: {'a': '0.0793616'} → lhs -2.5337406549184332002502863288135289651, rhs 1.00000000000000000000000000000000000000, rel diff 1.3946733846
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 11/11 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:853175:1371650040:113

- Page: [Characterizations of the exponential function](https://en.wikipedia.org/wiki/Characterizations_of_the_exponential_function) › Equivalence of the characterizations > Characterization 5 ⇔ characterization 6  · verdict **FAIL**, symbolic unknown
- LaTeX: `\lim_{h\to 0}\tfrac{a^h-1}{h}=1`
- Context before: …Characterization 5 ⇔ characterization 6. By inductively applying the multiplication rule, we get: $f\left(\frac{n}{m}\right)^m=f\left(\frac{n}{m}+\cdots+\frac{n}{m} \right)=f(n)=f(1)^n,$ and thus $f\left(\frac{n}{m}\right)=\sqrt[m]{f(1)^n}\ \stackrel{\text{def}}=\ a^{n/m}$ for $a=f(1)$ . Then the condition $f'(0)=1$ means that
- Context after: , so $a=e$ by definition. Also, any of the regularity conditions of definition 5 imply that $f(x)$ is continuous at all real $x$ (see below). The converse is similar. Characterization 5 ⇒ characterization 6. Let $f(x)$ be a Lebesgue-integrable non-zero function satisfying the mulitiplicative property $f(x+y)=f(x)f(y)$ with $f(1) = e$ . Following He…
- Translator read: `Limit((a**h - 1)/h, h, 0, dir='+-')`  =  `1`  · notes: sides: \lim_{h\to 0}\tfrac{a^h-1}{h}  ||  1
- Assumptions: domains {'a': 'real'}; constants {}; constraints ['a > 0']
- Verifier: The identity fails at 59 of 59 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at a=0.00122965: lhs=-6.70102570293, rhs=1.000000000000).
- Counterexample: {'a': '0.00122965'} → lhs -6.7010257029361820805376070472362941806, rhs 1.00000000000000000000000000000000000000, rel diff 1.1492308855
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 11/11 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:156533:1372897661:11

- Page: [Chebyshev's inequality](https://en.wikipedia.org/wiki/Chebyshev's_inequality) › Statement > Probabilistic statement  · verdict **FAIL**, symbolic unknown
- LaTeX: `1/k^2 \geq 1`
- Context before: …e generalized to a statement about measure spaces. Probabilistic statement. Let $X$ (integrable) be a random variable with finite non-zero variance $\sigma^2$ (and thus finite expected value $\mu$ ). Then for any real number $k > 0$ , $\Pr(|X-\mu|\geq k\sigma) \leq \frac{1}{k^2}.$ Only the case $k > 1$ is useful. When $k \leq 1$ the right-hand side
- Context after: and the inequality is trivial as all probabilities are at most 1. As an example, using $k = \sqrt{2}$ shows that the probability values lie outside the interval $(\mu - \sqrt{2}\sigma, \mu + \sqrt{2}\sigma)$ does not exceed $1/2$ . Equivalently, it implies that the probability of values lying within the interval (i.e. its "coverage") is at least $1…
- Translator read: `k**(-2)`  >=  `1`  · notes: sides: 1/k^2  ||  1
- Assumptions: domains {'k': 'positive_integer'}; constants {}; constraints ['k > 0']
- Verifier: The inequality fails at 42 of 46 evaluable points, a clear majority in every regime (small_positive, integers_small, mixed_sign, large) (e.g. at k=2: lhs=0.250000000000, rhs=1.000000000000).
- Counterexample: {'k': '2'} → lhs 0.25000000000000000000000000000000000000, rhs 1.00000000000000000000000000000000000000, rel diff 0.7500000000
- Regimes: small_positive 11/12 fail, 0 err, unit_interval 2/3 fail, 0 err, integers_small 10/11 fail, 0 err, mixed_sign 7/8 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:2989409:1381138631:83

- Page: [Church encoding](https://en.wikipedia.org/wiki/Church_encoding) › Church numerals > Table of functions on Church numerals  · verdict **FAIL**, symbolic unknown
- LaTeX: `\operatorname{exp} \ b\ n\ f\ x = n\ b\ f\ x`
- Context before: …\ n\ f\ x = m\ f\ (n\ f\ x)$ $\lambda m n f x.m\ f\ (n\ f\ x)$ $\lambda m n.n \operatorname{succ} m$ Multiplication $m * n$ $f^{\circ (m*n)} = (f^{\circ m})^{\circ n}$ $\operatorname{multiply}\ m\ n\ f\ x = m\ (n\ f) \ x$ $\lambda m n f x.m\ (n\ f) \ x$ $\lambda m n f.m\ (n\ f)$ Exponentiation $b^n$ $b^{\circ n} = (\operatorname{mult} b)^{\circ n}$
- Context after: $\lambda b n f x.n\ b\ f\ x$ $\lambda b n.n\ b$ Predecessor $n - 1$ $first((\langle i,j\rangle \mapsto \langle j,f \circ j\rangle)^{\circ n}\langle I,I\rangle) = f^{\circ (n-1)}$ $\operatorname{pred} (n+1)\ f\ x = I\ (n\ f\ x)$ $\lambda n f x.n\ (\lambda r i.i\ (r\ f))\ (\lambda f.x)\ (\lambda u.u)$ Subtraction (Monus) $m - n$ $m-n = pred^{\circ n}…
- Translator read: `exp(b*f*n*x)`  =  `b*f*n*x`  · notes: pre:spacing
implicit_function_arg
sides: \operatorname{exp} \ b\ n\ f\ x  ||  n\ b\ f\ x
- Assumptions: domains {'b': 'real', 'f': 'positive', 'n': 'nonneg_integer', 'x': 'real'}; constants {}; constraints []
- Verifier: The identity fails at 60 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at b=0.456557, f=0.853352, n=0, x=0.398477: lhs=1.000000000000, rhs=0).
- Counterexample: {'b': '0.456557', 'f': '0.853352', 'n': '0', 'x': '0.398477'} → lhs 1.00000000000000000000000000000000000000, rhs 0, rel diff 1.0000000000
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:6220:1379953806:34

- Page: [Circle](https://en.wikipedia.org/wiki/Circle) › Analytic results > Equations > Complex plane  · verdict **FAIL**, symbolic unknown
- LaTeX: `|z - c|^2 = z\overline{z} - \overline{c}z - c\overline{z} + c\overline{c}`
- Context before: …dius r has the equation $|z - c| = r.$ In parametric form, this can be written as $z = re^{it} + c.$ The slightly generalised equation $pz\overline{z} + gz + \overline{gz} = q$ for real p, q and complex g is sometimes called a generalised circle. This becomes the above equation for a circle with $p = 1,\ g = -\overline{c},\ q = r^2 - |c|^2$ , since
- Context after: . Not all generalised circles are actually circles: a generalised circle is either a (true) circle or a line. Tangent lines. The tangent line through a point P on the circle is perpendicular to the diameter passing through P. If P = (x1, y1) and the circle has centre (a, b) and radius r, then the tangent line is perpendicular to the line from (a, b…
- Translator read: `Abs(c - z)**2`  =  `c*c_bar - c*z_bar - c_bar*z + z*z_bar`  · notes: ambig:bar:z_bar
ambig:bar:c_bar
sides: |z - c|^2  ||  z\overline{z} - \overline{c}z - c\overline{z} + c\overline{c}
- Assumptions: domains {'c': 'real', 'c_bar': 'real', 'z': 'complex', 'z_bar': 'complex'}; constants {}; constraints []
- Verifier: The identity fails at 72 of 72 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, complex, large) (e.g. at c=0.182565, c_bar=0.341771, z=0.337196, z_bar=0.0629117: lhs=0.023910746161, rhs=-0.04312029241).
- Counterexample: {'c': '0.182565', 'c_bar': '0.341771', 'z': '0.337196', 'z_bar': '0.0629117'} → lhs 0.02391074616100000000000000000000000000, rhs -0.0431202924183000000000000000000000000, rel diff 1.5545126162
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, complex 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:2932144:1357876522:13

- Page: [Circles of Apollonius](https://en.wikipedia.org/wiki/Circles_of_Apollonius) › Apollonius's definition of a circle > Apollonius pursuit problem  · verdict **FAIL**, symbolic unknown
- LaTeX: `\left( x + \frac{d\mu^2}{1-\mu^2}\right)^2 + y^2 = \left( \frac{d \mu}{1-\mu^2} \right)^2`
- Context before: …ht-hand side: $\begin{align} \left( x + \frac{d\mu^2}{1-\mu^2} \right)^2 + y^2 &= \frac{d^2\mu^4}{(1-\mu^2)^2} + \frac{d^2 \mu^2}{1-\mu^2}\\[2pt] &= \frac{d^2 \mu^4}{(1-\mu^2)^2} + \frac{d^2 \mu^2}{1-\mu^2} \frac{(1-\mu^2)}{(1-\mu^2)}\\[2pt] &= \frac{d^2\mu^4+d^2\mu^2-d^2\mu^4}{(1-\mu^2)^2}\\[2pt] &= \frac{d^2 \mu^2}{(1-\mu^2)^2} \end{align}$ Then:
- Context after: Therefore, the point must lie on a circle as defined by Apollonius, with their starting points as the foci. Circles sharing a radical axis. The circles defined by the Apollonian pursuit problem for the same two points A and B, but with varying ratios of the two speeds, are disjoint from each other and form a continuous family that cover the entire…
- Translator read: `y**2 + (d*mu**2/(1 - mu**2) + x)**2`  =  `d**2*mu**2/(1 - mu**2)**2`  · notes: pre:left_right
sides: ( x + \frac{d\mu^2}{1-\mu^2}\right)^2 + y^2  ||  ( \frac{d \mu}{1-\mu^2} \right)^2
- Assumptions: domains {'d': 'positive', 'mu': 'positive', 'x': 'real', 'y': 'real'}; constants {}; constraints ['Ne(1 - mu**2, 0)']
- Verifier: The identity fails at 60 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at d=0.0714694, mu=0.318868, x=0.470429, y=0.346867: lhs=0.349296451575, rhs=0.000643571668).
- Counterexample: {'d': '0.0714694', 'mu': '0.318868', 'x': '0.470429', 'y': '0.346867'} → lhs 0.34929645157525656019557715867649393988, rhs 0.00064357166893240085729694627887243522, rel diff 0.9981575201
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:277213:1372096557:5

- Page: [Coherent state](https://en.wikipedia.org/wiki/Coherent_state) › Quantum mechanical definition  · verdict **FAIL**, symbolic unknown
- LaTeX: `\alpha = |\alpha|e^{i\theta}`
- Context before: …mplitude. Quantum mechanical definition. Mathematically, a coherent state $|\alpha\rangle$ is defined to be the (unique) eigenstate of the annihilation operator â with corresponding eigenvalue $\alpha$ . Formally, this reads, $\hat{a}|\alpha\rangle=\alpha|\alpha\rangle ~.$ Since â is not hermitian, $\alpha$ is, in general, a complex number. Writing
- Context after: , $|\alpha|$ and θ are called the amplitude and phase of the state $|\alpha\rangle$ . The state $|\alpha\rangle$ is called a canonical coherent state in the literature, since there are many other types of coherent states, as can be seen in the companion article Coherent states in mathematical physics. Physically, this formula means that a coherent…
- Translator read: `alpha`  =  `e**(i*theta)*Abs(alpha)`  · notes: hint:e_only_as_exp_base
hint:i_present
sides: \alpha  ||  |\alpha|e^{i\theta}
- Assumptions: domains {'alpha': 'real', 'theta': 'real'}; constants {'e': 'E', 'i': 'I'}; constraints []
- Verifier: The identity fails at 58 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at alpha=0.0588668, theta=0.154285: lhs=0.058866800000, rhs=(0.05816756013).
- Counterexample: {'alpha': '0.0588668', 'theta': '0.154285'} → lhs 0.05886680000000000000000000000000000000, rhs (0.0581675601341663742915894572456180499, rel diff 0.1541320214
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 10/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:5308:1366053287:44

- Page: [Combination](https://en.wikipedia.org/wiki/Combination) › Number of combinations with repetition  · verdict **FAIL**, symbolic not_equal
- LaTeX: `\binom{7}{3} = \left(\!\! \binom{5}{3}\!\!\right)`
- Context before: …+ x_4 = 10$ (n = 4 and k = 10) can be represented by $\bigstar \bigstar \bigstar | \bigstar \bigstar | | \bigstar \bigstar \bigstar \bigstar \bigstar.$ The number of such strings is the number of ways to place 10 stars in 13 positions, $\binom{13}{10} = \binom{13}{3} = 286,$ which is the number of 10-multisubsets of a set with 4 elements. [caption]
- Context after: As with binomial coefficients, there are several relationships between these multichoose expressions. For example, for $n \ge 1, k \ge 0$ , $\left(\!\!\binom{n}{k}\!\!\right)=\left(\!\!\binom{k+1}{n-1}\!\!\right).$ This identity follows from interchanging the stars and bars in the above representation. Example of counting multisubsets. For example,…
- Translator read: `35`  =  `10`  · notes: pre:left_right
pre:spacing
sides: \binom{7}{3}  ||  (\!\! \binom{5}{3}\!\!\right)
- Assumptions: domains {}; constants {}; constraints []
- Verifier: The constant identity does not hold: both sides differ beyond 1e-8 relative error, stably at two working precisions (lhs=35.000000000000000, rhs=10.000000000000000).
- Counterexample: {} → lhs 35.0000000000000000000000000000000000000, rhs 10.0000000000000000000000000000000000000, rel diff 0.7142857142
- Regimes: constant 1/1 fail, 0 err

---
## wiki:en:5308:1366053287:47

- Page: [Combination](https://en.wikipedia.org/wiki/Combination) › Number of combinations with repetition > Example of counting multisubsets  · verdict **FAIL**, symbolic not_equal
- LaTeX: `\left(\!\!\binom{4}{3}\!\!\right) = \binom{4+3-1}3 = \binom{6}{3} = \frac{6 \times 5 \times 4}{3 \times 2 \times 1} = 20.`
- Context before: …ft(\!\!\binom{k+1}{n-1}\!\!\right).$ This identity follows from interchanging the stars and bars in the above representation. Example of counting multisubsets. For example, if you have four types of donuts (n = 4) on a menu to choose from and you want three donuts (k = 3), the number of ways to choose the donuts with repetition can be calculated as
- Context after: This result can be verified by listing all the 3-multisubsets of the set S = {1,2,3,4}. This is displayed in the following table. The second column lists the donuts you actually chose, the third column shows the nonnegative integer solutions $[x_1,x_2,x_3,x_4]$ of the equation $x_1 + x_2 + x_3 + x_4 = 3$ and the last column gives the stars and bars…
- Translator read (piece 0): `4`  =  `20`  · notes: pre:left_right
pre:spacing
pre:trailing_punct
op:times
sides: (\!\!\binom{4}{3}\!\!\right)  ||  \binom{4+3-1}3
- Translator read (piece 1): `20`  =  `20`  · notes: pre:left_right
pre:spacing
pre:trailing_punct
op:times
sides: \binom{4+3-1}3  ||  \binom{6}{3}
- Translator read (piece 2): `20`  =  `20`  · notes: pre:left_right
pre:spacing
pre:trailing_punct
op:times
sides: \binom{6}{3}  ||  \frac{6 \times 5 \times 4}{3 \times 2 \times 1}
- Translator read (piece 3): `20`  =  `20`  · notes: pre:left_right
pre:spacing
pre:trailing_punct
op:times
sides: \frac{6 \times 5 \times 4}{3 \times 2 \times 1}  ||  20
- Assumptions: domains {}; constants {}; constraints []
- Verifier: Chain link 0: The constant identity does not hold: both sides differ beyond 1e-8 relative error, stably at two working precisions (lhs=4.0000000000000000, rhs=20.000000000000000).
- Counterexample: {} → lhs 4.00000000000000000000000000000000000000, rhs 20.0000000000000000000000000000000000000, rel diff 0.8000000000
- Regimes: constant 1/1 fail, 0 err
