# Review batch 001 — 22 items

For each item answer with one JSON line (Finding schema): {"formula_id": ..., "verdict": "FAIL", "review": {"status": "confirmed_error"|"false_positive"|"ambiguous", "reviewer": "<name>", "notes": "<why, one or two sentences>"}, "suggested_fix": "<corrected LaTeX or null>", "evidence": "<independent source or derivation>"}


---
## wiki:en:64516:1372219930:3

- Page: [2](https://en.wikipedia.org/wiki/2) › Mathematics  · verdict **FAIL**, symbolic not_equal
- LaTeX: `1+1=0`
- Context before: …2$ , the smallest finite field. It has two elements, usually denoted 0 and 1, and addition in $\mathbb F_2$ corresponds to parity. Thus reduction modulo 2 records the parity of an integer: even integers are congruent to 0 modulo 2, and odd integers are congruent to 1 modulo 2. In algebra, structures of characteristic 2 have special behavior because
- Context after: ; in particular, every element satisfies $x=-x$ . For this reason, many algebraic constructions have separate forms in characteristic 2. A symmetry of order two is called an involution. List of basic calculations. Multiplication 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 20 25 50 100 1000 2 * x 2 4 6 8 10 12 14 16 18 20 22 24 26 28 30 32 40 50 100 200…
- Translator read: `2`  =  `0`  · notes: sides: 1+1  ||  0
- Assumptions: domains {}; constants {}; constraints []
- Verifier: The constant identity does not hold: both sides differ beyond 1e-8 relative error, stably at two working precisions (lhs=2.0000000000000000, rhs=0).
- Counterexample: {} → lhs 2.00000000000000000000000000000000000000, rhs 0, rel diff 1.0000000000
- Regimes: constant 1/1 fail, 0 err

---
## wiki:en:15542628:1380534400:4

- Page: [97.5th percentile point](https://en.wikipedia.org/wiki/97.5th_percentile_point) › (lead)  · verdict **FAIL**, symbolic unknown
- LaTeX: `\frac{1}{\sqrt{2\pi}}\int_{-z_{.975}}^{z_{.975}} e^{-x^2/2} \, \mathrm{d}x = 0.95.`
- Context before: …n, i.e. X ~ N(0,1), $\mathrm{P}(X > 1.96) \approx 0.025, \,$ $\mathrm{P}(X < 1.96) \approx 0.975, \,$ and as the normal distribution is symmetric, $\mathrm{P}(-1.96 < X < 1.96) \approx 0.95. \,$ One notation for this number is z.975. From the probability density function of the standard normal distribution, the exact value of z.975 is determined by
- Context after: Its square, about 3.84146, is the 95th percentile point of a chi-squared distribution with 1 degree of freedom, often used for testing 2×2 contingency tables. History. The use of this number in applied statistics can be traced to the influence of Ronald Fisher's classic textbook, Statistical Methods for Research Workers, first published in 1925: "T…
- Translator read: `sqrt(2)*Integral(e**(-x**2/2), (x, -z_{.975}, z_{.975}))/(2*sqrt(pi))`  =  `19/20`  · notes: pre:spacing
pre:trailing_punct
subscript_expr:z_{.975}
hint:e_only_as_exp_base
sides: \frac{1}{\sqrt{2\pi}}\int_{-z_{.975}}^{z_{.975}} e^{-x^2/2} \, \mathrm{d}x  ||  0.95
- Assumptions: domains {'z_{.975}': 'complex'}; constants {'e': 'E'}; constraints []
- Verifier: The identity fails at 36 of 36 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, complex, large) (e.g. at z_{.975}=0: lhs=0, rhs=0.950000000000).
- Counterexample: {'z_{.975}': '0'} → lhs 0, rhs 0.95000000000000000000000000000000000000, rel diff 1.0000000000
- Regimes: small_positive 6/6 fail, 0 err, unit_interval 6/6 fail, 0 err, integers_small 6/6 fail, 0 err, mixed_sign 6/6 fail, 0 err, complex 6/6 fail, 0 err, large 6/12 fail, 6 err

---
## wiki:en:61338:1377884439:1

- Page: [Addition](https://en.wikipedia.org/wiki/Addition) › Notation and terminology  · verdict **FAIL**, symbolic not_equal
- LaTeX: `3\frac{1}{2}=3+\frac{1}{2}=3.5.`
- Context before: …+" between the terms, and the result is expressed with an equals sign. For example, $1 + 2 = 3$ reads "one plus two equals three". Nonetheless, there are some situations where addition is understood, even though no symbol appears: a whole number followed immediately by a fraction indicates the sum of the two, called a mixed number, with an example,
- Context after: This notation can cause confusion, since in most other contexts, juxtaposition denotes multiplication instead. The numbers or the objects to be added in general addition are collectively referred to as the , the addends or the summands. This terminology carries over to the summation of multiple terms. This is to be distinguished from factors, which…
- Translator read (piece 0): `3/2`  =  `7/2`  · notes: pre:trailing_punct
sides: 3\frac{1}{2}  ||  3+\frac{1}{2}
- Translator read (piece 1): `7/2`  =  `7/2`  · notes: pre:trailing_punct
sides: 3+\frac{1}{2}  ||  3.5
- Assumptions: domains {}; constants {}; constraints []
- Verifier: Chain link 0: The constant identity does not hold: both sides differ beyond 1e-8 relative error, stably at two working precisions (lhs=1.5000000000000000, rhs=3.5000000000000000).
- Counterexample: {} → lhs 1.50000000000000000000000000000000000000, rhs 3.50000000000000000000000000000000000000, rel diff 0.5714285714
- Regimes: constant 1/1 fail, 0 err

---
## wiki:en:14668760:1380593947:32

- Page: [Alternating-direction implicit method](https://en.wikipedia.org/wiki/Alternating-direction_implicit_method) › ADI for matrix equations > Shift-parameter selection and the ADI error equation  · verdict **FAIL**, symbolic not_equal
- LaTeX: `X^{(0)} = 0`
- Context before: …equation. The problem of finding good shift parameters is nontrivial. This problem can be understood by examining the ADI error equation. After $K$ iterations, the error is given by $X - X^{(K)} = \prod_{j = 1}^K \frac{(A - \alpha_j I)}{(A - \beta_j I)} \left ( X - X^{(0)} \right ) \prod_{j = 1}^K \frac{(B - \beta_j I)}{(B - \alpha_j I)}.$ Choosing
- Context after: results in the following bound on the relative error: $\frac{\left \|X - X^{(K)} \right \|_2}{\|X\|_2} \leq \| r_K(A) \|_2 \| r_K(B)^{-1}\|_2, \quad r_K(M) = \prod_{j = 1}^K \frac{(M - \alpha_j I)}{(M - \beta_j I)}.$ where $\| \cdot \|_2$ is the operator norm. The ideal set of shift parameters $\{ (\alpha_j, \beta_j)\}_{j = 1}^K$ defines a rational…
- Translator read: `1`  =  `0`  · notes: sides: X^{(0)}  ||  0
- Assumptions: domains {}; constants {}; constraints []
- Verifier: The constant identity does not hold: both sides differ beyond 1e-8 relative error, stably at two working precisions (lhs=1.0000000000000000, rhs=0).
- Counterexample: {} → lhs 1.00000000000000000000000000000000000000, rhs 0, rel diff 1.0000000000
- Regimes: constant 1/1 fail, 0 err

---
## wiki:en:2202:1373603189:91

- Page: [Analytic geometry](https://en.wikipedia.org/wiki/Analytic_geometry) › Finding intersections of geometric objects  · verdict **FAIL**, symbolic not_equal
- LaTeX: `0=1`
- Context before: …circles is the collection of points which make both equations true. Does the point $(0,0)$ make both equations true? Using $(0,0)$ for $(x,y)$ , the equation for $Q$ becomes $(0-1)^2+0^2=1$ or $(-1)^2=1$ which is true, so $(0,0)$ is in the relation $Q$ . On the other hand, still using $(0,0)$ for $(x,y)$ the equation for $P$ becomes $0^2+0^2=1$ or
- Context after: which is false. $(0,0)$ is not in $P$ so it is not in the intersection. The intersection of $P$ and $Q$ can be found by solving the simultaneous equations: $x^2+y^2 = 1$ $(x-1)^2+y^2 = 1.$ Traditional methods for finding intersections include substitution and elimination. Substitution: Solve the first equation for $y$ in terms of $x$ and then subst…
- Translator read: `0`  =  `1`  · notes: sides: 0  ||  1
- Assumptions: domains {}; constants {}; constraints []
- Verifier: The constant identity does not hold: both sides differ beyond 1e-8 relative error, stably at two working precisions (lhs=0, rhs=1.0000000000000000).
- Counterexample: {} → lhs 0, rhs 1.00000000000000000000000000000000000000, rel diff 1.0000000000
- Regimes: constant 1/1 fail, 0 err

---
## wiki:en:2202:1373603189:90

- Page: [Analytic geometry](https://en.wikipedia.org/wiki/Analytic_geometry) › Finding intersections of geometric objects  · verdict **FAIL**, symbolic not_equal
- LaTeX: `0^2+0^2=1`
- Context before: …on of these two circles is the collection of points which make both equations true. Does the point $(0,0)$ make both equations true? Using $(0,0)$ for $(x,y)$ , the equation for $Q$ becomes $(0-1)^2+0^2=1$ or $(-1)^2=1$ which is true, so $(0,0)$ is in the relation $Q$ . On the other hand, still using $(0,0)$ for $(x,y)$ the equation for $P$ becomes
- Context after: or $0=1$ which is false. $(0,0)$ is not in $P$ so it is not in the intersection. The intersection of $P$ and $Q$ can be found by solving the simultaneous equations: $x^2+y^2 = 1$ $(x-1)^2+y^2 = 1.$ Traditional methods for finding intersections include substitution and elimination. Substitution: Solve the first equation for $y$ in terms of $x$ and t…
- Translator read: `0`  =  `1`  · notes: sides: 0^2+0^2  ||  1
- Assumptions: domains {}; constants {}; constraints []
- Verifier: The constant identity does not hold: both sides differ beyond 1e-8 relative error, stably at two working precisions (lhs=0, rhs=1.0000000000000000).
- Counterexample: {} → lhs 0, rhs 1.00000000000000000000000000000000000000, rel diff 1.0000000000
- Regimes: constant 1/1 fail, 0 err

---
## wiki:en:11864519:1374041215:112

- Page: [Approximate Bayesian computation](https://en.wikipedia.org/wiki/Approximate_Bayesian_computation) › Pitfalls and remedies > Bayes factor with ABC and summary statistics  · verdict **FAIL**, symbolic unknown
- LaTeX: `B_{1,2}=B_{1,2}^s`
- Context before: …B_{1,2}$ and $B_{1,2}^s$ takes the form: $B_{1,2}=\frac{p(D|M_1)}{p(D|M_2)}=\frac{p(D|S(D),M_1)}{p(D|S(D),M_2)} \frac{p(S(D)|M_1)}{p(S(D)|M_2)}=\frac{p(D|S(D),M_1)}{p(D|S(D),M_2)} B_{1,2}^s$ . Thus, a summary statistic $S(D)$ is sufficient for comparing two models $M_1$ and $M_2$ if and only if: $p(D|S(D),M_1)=p(D|S(D),M_2)$ , which results in that
- Context after: . It is also clear from the equation above that there might be a huge difference between $B_{1,2}$ and $B_{1,2}^s$ if the condition is not satisfied, as can be demonstrated by toy examples. Crucially, it was shown that sufficiency for $M_1$ or $M_2$ alone, or for both models, does not guarantee sufficiency for ranking the models. However, it was al…
- Translator read: `B_{1,2}`  =  `B_{1,2}**s`  · notes: subscript_expr:B_{1,2}
sides: B_{1,2}  ||  B_{1,2}^s
- Assumptions: domains {'B_{1,2}': 'positive', 's': 'complex'}; constants {}; constraints []
- Verifier: The identity fails at 70 of 72 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, complex, large) (e.g. at B_{1,2}=0.0761495, s=0.0704135: lhs=0.076149500000, rhs=0.834169416829).
- Counterexample: {'B_{1,2}': '0.0761495', 's': '0.0704135'} → lhs 0.07614950000000000000000000000000000000, rhs 0.83416941682921515696241412317530977942, rel diff 0.9087121890
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 10/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, complex 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:3118:1380008421:60

- Page: [Arithmetic](https://en.wikipedia.org/wiki/Arithmetic) › Operations > Exponentiation and logarithm  · verdict **FAIL**, symbolic not_equal
- LaTeX: `3 = 27`
- Context before: …arithmetic operation in which a number, known as the base, is raised to the power of another number, known as the exponent. The result of this operation is called the power. Exponentiation is sometimes expressed using the symbol ^ but the more common way is to write the exponent in superscript right after the base. Examples are $2^4 = 16$ and $3$ ^
- Context after: . If the exponent is a natural number then exponentiation is the same as repeated multiplication, as in $2^4 = 2 \times 2 \times 2 \times 2$ . Roots are a special type of exponentiation using a fractional exponent. For example, the square root of a number is the same as raising the number to the power of $\tfrac{1}{2}$ and the cube root of a number…
- Translator read: `3`  =  `27`  · notes: sides: 3  ||  27
- Assumptions: domains {}; constants {}; constraints []
- Verifier: The constant identity does not hold: both sides differ beyond 1e-8 relative error, stably at two working precisions (lhs=3.0000000000000000, rhs=27.000000000000000).
- Counterexample: {} → lhs 3.00000000000000000000000000000000000000, rhs 27.0000000000000000000000000000000000000, rel diff 0.8888888888
- Regimes: constant 1/1 fail, 0 err

---
## wiki:en:3118:1380008421:116

- Page: [Arithmetic](https://en.wikipedia.org/wiki/Arithmetic) › Types > Others  · verdict **FAIL**, symbolic not_equal
- LaTeX: `1 + 1 = 1`
- Context before: …al operations to govern the transformation between single unit and compound unit quantities. For example, the operation of reduction is used to transform the compound quantity 1 h 90 min into the single unit quantity 150 min. Non-Diophantine arithmetics are arithmetic systems that violate traditional arithmetic intuitions and include equations like
- Context after: and $2 + 2 = 5$ . They can be employed to represent some real-world situations in modern physics and everyday life. For instance, the equation $1 + 1 = 1$ can be used to describe the observation that if one raindrop is added to another raindrop then they do not remain two separate entities but become one. Axiomatic foundations. Axiomatic foundation…
- Translator read: `2`  =  `1`  · notes: sides: 1 + 1  ||  1
- Assumptions: domains {}; constants {}; constraints []
- Verifier: The constant identity does not hold: both sides differ beyond 1e-8 relative error, stably at two working precisions (lhs=2.0000000000000000, rhs=1.0000000000000000).
- Counterexample: {} → lhs 2.00000000000000000000000000000000000000, rhs 1.00000000000000000000000000000000000000, rel diff 0.5000000000
- Regimes: constant 1/1 fail, 0 err

---
## wiki:en:3118:1380008421:117

- Page: [Arithmetic](https://en.wikipedia.org/wiki/Arithmetic) › Types > Others  · verdict **FAIL**, symbolic not_equal
- LaTeX: `2 + 2 = 5`
- Context before: …govern the transformation between single unit and compound unit quantities. For example, the operation of reduction is used to transform the compound quantity 1 h 90 min into the single unit quantity 150 min. Non-Diophantine arithmetics are arithmetic systems that violate traditional arithmetic intuitions and include equations like $1 + 1 = 1$ and
- Context after: . They can be employed to represent some real-world situations in modern physics and everyday life. For instance, the equation $1 + 1 = 1$ can be used to describe the observation that if one raindrop is added to another raindrop then they do not remain two separate entities but become one. Axiomatic foundations. Axiomatic foundations of arithmetic…
- Translator read: `4`  =  `5`  · notes: sides: 2 + 2  ||  5
- Assumptions: domains {}; constants {}; constraints []
- Verifier: The constant identity does not hold: both sides differ beyond 1e-8 relative error, stably at two working precisions (lhs=4.0000000000000000, rhs=5.0000000000000000).
- Counterexample: {} → lhs 4.00000000000000000000000000000000000000, rhs 5.00000000000000000000000000000000000000, rel diff 0.2000000000
- Regimes: constant 1/1 fail, 0 err

---
## wiki:en:3118:1380008421:118

- Page: [Arithmetic](https://en.wikipedia.org/wiki/Arithmetic) › Types > Others  · verdict **FAIL**, symbolic not_equal
- LaTeX: `1 + 1 = 1`
- Context before: …he compound quantity 1 h 90 min into the single unit quantity 150 min. Non-Diophantine arithmetics are arithmetic systems that violate traditional arithmetic intuitions and include equations like $1 + 1 = 1$ and $2 + 2 = 5$ . They can be employed to represent some real-world situations in modern physics and everyday life. For instance, the equation
- Context after: can be used to describe the observation that if one raindrop is added to another raindrop then they do not remain two separate entities but become one. Axiomatic foundations. Axiomatic foundations of arithmetic try to provide a small set of laws, called axioms, from which all fundamental properties of and operations on numbers can be derived. They…
- Translator read: `2`  =  `1`  · notes: sides: 1 + 1  ||  1
- Assumptions: domains {}; constants {}; constraints []
- Verifier: The constant identity does not hold: both sides differ beyond 1e-8 relative error, stably at two working precisions (lhs=2.0000000000000000, rhs=1.0000000000000000).
- Counterexample: {} → lhs 2.00000000000000000000000000000000000000, rhs 1.00000000000000000000000000000000000000, rel diff 0.5000000000
- Regimes: constant 1/1 fail, 0 err

---
## wiki:en:577053:1374796707:27

- Page: [Association rule learning](https://en.wikipedia.org/wiki/Association_rule_learning) › Useful Concepts > Confidence  · verdict **FAIL**, symbolic not_equal
- LaTeX: `\frac{2/5}{3/5}=\frac{0.4}{0.6}=0.67`
- Context before: …{1/5}{1/5}=\frac{0.2}{0.2}=1.0$ in the dataset, which denotes that every time a customer buys butter and bread, they also buy milk. This particular example demonstrates the rule being correct 100% of the time for transactions containing both butter and bread. The rule $\{\mathrm{fruit}\} \Rightarrow \{\mathrm{eggs}\}$ , however, has a confidence of
- Context after: . This suggests that eggs are bought 67% of the times that fruit is brought. Within this particular dataset, fruit is purchased a total of 3 times, with two of those times consisting of egg purchases. For larger datasets, a minimum threshold, or a percentage cutoff, for the confidence can be useful for determining item relationships. When applying…
- Translator read (piece 0): `2/3`  =  `2/3`  · notes: sides: \frac{2/5}{3/5}  ||  \frac{0.4}{0.6}
- Translator read (piece 1): `2/3`  =  `67/100`  · notes: sides: \frac{0.4}{0.6}  ||  0.67
- Assumptions: domains {}; constants {}; constraints []
- Verifier: Chain link 1: The constant identity does not hold: both sides differ beyond 1e-8 relative error, stably at two working precisions (lhs=0.6666666666666666, rhs=0.6700000000000000).
- Counterexample: {} → lhs 0.66666666666666666666666666666666666666, rhs 0.67000000000000000000000000000000000000, rel diff 0.0049751243
- Regimes: constant 1/1 fail, 0 err

---
## wiki:en:324752:1361359420:61

- Page: [Atiyah–Singer index theorem](https://en.wikipedia.org/wiki/Atiyah%E2%80%93Singer_index_theorem) › Examples > Chern-Gauss-Bonnet theorem  · verdict **FAIL**, symbolic not_equal
- LaTeX: `i = 1,\, \ldots,\, r`
- Context before: …hat there are complex line bundles $l_1,\, \ldots,\, l_r$ such that $E \otimes \mathbb{C} = l_1 \oplus \overline{l_1} \oplus \dotsm l_r \oplus \overline{l_r}$ . Therefore, we can consider the Chern roots $x_i (E \otimes \mathbb{C}) = c_1(l_i)$ , $x_{r+i} (E \otimes \mathbb{C}) = c_1\mathord\left(\overline{l_i}\right) = -x_i(E \otimes \mathbb{C})$ ,
- Context after: . Using Chern roots as above and the standard properties of the Euler class, we have that $e(TM) = \prod^r_i x_i(TM \otimes \mathbb{C})$ . As for the Chern character and the Todd class,…
- Translator read: `i`  =  `1`  · notes: pre:spacing
cond: \ldots,\, r
hint:i_present
sides: i  ||  1
- Assumptions: domains {}; constants {'i': 'I'}; constraints []
- Verifier: The constant identity does not hold: both sides differ beyond 1e-8 relative error, stably at two working precisions (lhs=(0.0 + 1.0j), rhs=1.0000000000000000).
- Counterexample: {} → lhs (0.0 + 1.0j), rhs 1.00000000000000000000000000000000000000, rel diff 1.4142135623
- Regimes: constant 1/1 fail, 0 err

---
## wiki:en:5321016:1346298619:0

- Page: [Atmospheric thermodynamics](https://en.wikipedia.org/wiki/Atmospheric_thermodynamics) › Applications > Water vapor and global climate change  · verdict **FAIL**, symbolic unknown
- LaTeX: `e_s(T)= 6.1094 \exp \left( \frac{17.625T}{T+243.04} \right)`
- Context before: …nge. The Clausius–Clapeyron relation shows how the water-holding capacity of the atmosphere increases by about 8% per Celsius increase in temperature. (It does not directly depend on other parameters like the pressure or density.) This water-holding capacity, or "equilibrium vapor pressure", can be approximated using the August-Roche-Magnus formula
- Context after: (where $e_s(T)$ is the equilibrium or saturation vapor pressure in hPa, and $T$ is temperature in degrees Celsius). This shows that when atmospheric temperature increases (e.g., due to greenhouse gases) the absolute humidity should also increase exponentially (assuming a constant relative humidity). However, this purely thermodynamic argument is su…
- Translator read: `T*e_s`  =  `30547*exp(141*T/(8*(T + 6076/25)))/5000`  · notes: pre:left_right
funcapp_rule:s:single_atom_arg
sides: e_s(T)  ||  6.1094 \exp \left( \frac{17.625T}{T+243.04} \right)
- Assumptions: domains {'T': 'positive', 'e_s': 'positive'}; constants {}; constraints []
- Verifier: The identity fails at 60 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at T=0.0551549, e_s=0.0568491: lhs=0.003135506425, rhs=6.133879588716).
- Counterexample: {'T': '0.0551549', 'e_s': '0.0568491'} → lhs 0.00313550642559000000000000000000000000, rhs 6.13387958871674060372820894099457990464, rel diff 0.9994888216
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:18949289:1377005691:0

- Page: [Augustus De Morgan](https://en.wikipedia.org/wiki/Augustus_De_Morgan) › Works > A Budget of Paradoxes  · verdict **FAIL**, symbolic not_equal
- LaTeX: `\pi = 3 \tfrac{1}{8}`
- Context before: …rs, such as Thomas Baxter, cube-duplicators, and angle-trisectors. One such angle-trisector was James Sabben, whose work received a one-line review from De Morgan: "The consequence of years of intense thought": very likely, and very sad. Another pseudomath identified by De Morgan was James Smith, a successful merchant of Liverpool, who claimed that
- Context after: . De Morgan writes: Mr. Smith continues to write me long letters, to which he hints that I am to answer. In his last of 31 closely written sides of note paper, he informs me, with reference to my obstinate silence, that though I think myself and am thought by others to be a mathematical Goliath, I have resolved to play the mathematical snail, and k…
- Translator read: `pi`  =  `3/8`  · notes: sides: \pi  ||  3 \tfrac{1}{8}
- Assumptions: domains {}; constants {}; constraints []
- Verifier: The constant identity does not hold: both sides differ beyond 1e-8 relative error, stably at two working precisions (lhs=3.1415926535897932, rhs=0.3750000000000000).
- Counterexample: {} → lhs 3.14159265358979323846264338327950288419, rhs 0.37500000000000000000000000000000000000, rel diff 0.8806337926
- Regimes: constant 1/1 fail, 0 err

---
## wiki:en:285422:1368909113:107

- Page: [Baker–Campbell–Hausdorff formula](https://en.wikipedia.org/wiki/Baker%E2%80%93Campbell%E2%80%93Hausdorff_formula) › Special cases  · verdict **FAIL**, symbolic unknown
- LaTeX: `e^X e^Y = \exp\left( X+\frac{s}{1-e^{-s}}Y\right).`
- Context before: …nested commutators with a single $Y$ are normalized Bernoulli numbers.) Now assume that the commutator is a multiple of $Y$ , so that $[X,Y] = sY$ . Then all iterated commutators will be multiples of $Y$ , and no quadratic or higher terms in $Y$ appear. Thus, the $O\left(Y^2\right)$ term above vanishes and we obtain: [Math theorem | math_statement]
- Context after: Again, in this case there are no smallness restriction on $X$ and $Y$ . The restriction on $s$ guarantees that the expression on the right side makes sense. (When $s = 0$ we may interpret $\lim_{s\to 0} s/(1-e^{-s}) = 1$ .) We also obtain a simple "braiding identity": $e^{X} e^{Y} = e^{\exp (s) Y} e^{X} ,$ which may be written as an adjoint dilatio…
- Translator read: `e**X*e**Y`  =  `exp(X + Y*s/(1 - 1/e**s))`  · notes: pre:left_right
pre:trailing_punct
hint:e_only_as_exp_base
sides: e^X e^Y  ||  \exp\left( X+\frac{s}{1-e^{-s}}Y\right)
- Assumptions: domains {'X': 'positive', 'Y': 'positive', 's': 'complex'}; constants {'e': 'E'}; constraints ['Ne(1 - 1/E**s, 0)']
- Verifier: The identity fails at 72 of 72 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, complex, large) (e.g. at X=0.334924, Y=0.325733, s=0.079915: lhs=1.936063910632, rhs=1.961767422715).
- Counterexample: {'X': '0.334924', 'Y': '0.325733', 's': '0.079915'} → lhs 1.93606391063278590884570597067836594323, rhs 1.96176742271579111675655116658503359859, rel diff 0.0131022218
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, complex 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:24235330:1380193530:49

- Page: [Behavioural genetics](https://en.wikipedia.org/wiki/Behavioural_genetics) › General findings > Nature of genetic influence  · verdict **FAIL**, symbolic unknown
- LaTeX: `R^2<0.3\%`
- Context before: …variant; $\beta$ or $OR$ describe the effect of having a risk allele on the individual who harbours it, relative to an individual who does not harbour a risk allele. When described on the $R^2$ metric, the effects of individual genetic variants on complex human behavioural traits and disorders are vanishingly small, with each variant accounting for
- Context after: of variation in the phenotype. This fact has been discovered primarily through genome-wide association studies of complex behavioural phenotypes, including results on substance use, personality, fertility, schizophrenia, depression, and endophenotypes including brain structure and function. There are a small handful of replicated and robustly studi…
- Translator read: `R**2`  <  `3/1000`  · notes: percent
sides: R^2  ||  0.3\%
- Assumptions: domains {'R': 'positive'}; constants {}; constraints []
- Verifier: The inequality fails at 59 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at R=0.087436: lhs=0.007645054096, rhs=0.003000000000).
- Counterexample: {'R': '0.087436'} → lhs 0.00764505409600000000000000000000000000, rhs 0.00300000000000000000000000000000000000, rel diff 0.6075894346
- Regimes: small_positive 11/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:207074:1380844686:82

- Page: [Beta distribution](https://en.wikipedia.org/wiki/Beta_distribution) › Properties > Measures of central tendency > Median  · verdict **FAIL**, symbolic unknown
- LaTeX: `\begin{align}
\lim_{\beta \to  0} \text{median}= \lim_{\alpha \to \infty} \text{median} = 1,\\
\lim_{\alpha\to  0} \text{median}= \lim_{\beta \to  \infty} \text{median} = 0.
\end{align}`
- Context before: …the power function distribution) For α = 3 and β = 2, median = 0.6142724318676105..., the real solution to the quartic equation 1 − 8x3 + 6x4 = 0, which lies in [0,1]. For α = 2 and β = 3, median = 0.38572756813238945... = 1−median(Beta(3, 2)) The following are the limits with one parameter finite (non-zero) and the other approaching these limits:
- Context after: A reasonable approximation of the value of the median of the beta distribution, for both α and β greater or equal to one, is given by the formula $\text{median} \approx \frac{\alpha - \tfrac{1}{3}}{\alpha + \beta - \tfrac{2}{3}} \text{ for } \alpha, \beta \ge 1.$ When α, β ≥ 1, the relative error (the absolute error divided by the median) in this a…
- Translator read (piece 0): `Limit(median, beta, 0, dir='+-')`  =  `Limit(median, alpha, oo, dir='-')`  · notes: pre:env_align
pre:rows=2
pre:trailing_punct
text_symbol:median
sides: \lim_{\beta \to  0} \text{median}  ||  \lim_{\alpha \to \infty} \text{median}
- Translator read (piece 1): `Limit(median, alpha, oo, dir='-')`  =  `1`  · notes: pre:env_align
pre:rows=2
pre:trailing_punct
text_symbol:median
sides: \lim_{\alpha \to \infty} \text{median}  ||  1
- Translator read (piece 2): `Limit(median, alpha, 0, dir='+-')`  =  `Limit(median, beta, oo, dir='-')`  · notes: pre:env_align
pre:rows=2
pre:trailing_punct
text_symbol:median
sides: \lim_{\alpha\to  0} \text{median}  ||  \lim_{\beta \to  \infty} \text{median}
- Translator read (piece 3): `Limit(median, beta, oo, dir='-')`  =  `0`  · notes: pre:env_align
pre:rows=2
pre:trailing_punct
text_symbol:median
sides: \lim_{\beta \to  \infty} \text{median}  ||  0
- Assumptions: domains {'median': 'positive'}; constants {}; constraints []
- Verifier: Chain link 1: The identity fails at 59 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at median=0.00962103: lhs=0.009621030000, rhs=1.000000000000).
- Counterexample: {'median': '0.00962103'} → lhs 0.00962103000000000000000000000000000000, rhs 1.00000000000000000000000000000000000000, rel diff 0.9903789700
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 11/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:207074:1380844686:86

- Page: [Beta distribution](https://en.wikipedia.org/wiki/Beta_distribution) › Properties > Measures of central tendency > Mean  · verdict **FAIL**, symbolic unknown
- LaTeX: `\begin{align}
\lim_{\beta \to  0} \mu = \lim_{\alpha \to  \infty} \mu = 1\\
\lim_{\alpha\to  0} \mu = \lim_{\beta \to  \infty} \mu = 0
\end{align}`
- Context before: …bution becomes a 1-point Degenerate distribution with a Dirac delta function spike at the left end, x = 0, with probability 1, and zero probability everywhere else. There is 100% probability (absolute certainty) concentrated at the left end, x = 0. Following are the limits with one parameter finite (non-zero) and the other approaching these limits:
- Context after: While for typical unimodal distributions (with centrally located modes, inflexion points at both sides of the mode, and longer tails) (with Beta(α, β) such that α, β > 2) it is known that the sample mean (as an estimate of location) is not as robust as the sample median, the opposite is the case for uniform or "U-shaped" bimodal distributions (with…
- Translator read (piece 0): `Limit(mu, beta, 0, dir='+-')`  =  `Limit(mu, alpha, oo, dir='-')`  · notes: pre:env_align
pre:rows=2
sides: \lim_{\beta \to  0} \mu  ||  \lim_{\alpha \to  \infty} \mu
- Translator read (piece 1): `Limit(mu, alpha, oo, dir='-')`  =  `1`  · notes: pre:env_align
pre:rows=2
sides: \lim_{\alpha \to  \infty} \mu  ||  1
- Translator read (piece 2): `Limit(mu, alpha, 0, dir='+-')`  =  `Limit(mu, beta, oo, dir='-')`  · notes: pre:env_align
pre:rows=2
sides: \lim_{\alpha\to  0} \mu  ||  \lim_{\beta \to  \infty} \mu
- Translator read (piece 3): `Limit(mu, beta, oo, dir='-')`  =  `0`  · notes: pre:env_align
pre:rows=2
sides: \lim_{\beta \to  \infty} \mu  ||  0
- Assumptions: domains {'mu': 'positive'}; constants {}; constraints []
- Verifier: Chain link 1: The identity fails at 58 of 59 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at mu=0.0250236: lhs=0.025023600000, rhs=1.000000000000).
- Counterexample: {'mu': '0.0250236'} → lhs 0.02502360000000000000000000000000000000, rhs 1.00000000000000000000000000000000000000, rel diff 0.9749764000
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 10/11 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:207074:1380844686:91

- Page: [Beta distribution](https://en.wikipedia.org/wiki/Beta_distribution) › Properties > Measures of central tendency > Geometric mean  · verdict **FAIL**, symbolic unknown
- LaTeX: `\begin{align}
\lim_{\beta \to  0} G_X = \lim_{\alpha \to  \infty} G_X = 1\\
\lim_{\alpha\to  0} G_X = \lim_{\beta \to  \infty} G_X = 0
\end{align}`
- Context before: …s negative infinity as X approaches zero, while ln(X) flattens towards zero as X → 1. Along a line , the following limits apply: $\begin{align} &\lim_{\alpha = \beta \to 0} G_X = 0 \\ &\lim_{\alpha = \beta \to \infty} G_X =\tfrac{1}{2} \end{align}$ Following are the limits with one parameter finite (non-zero) and the other approaching these limits:
- Context after: The accompanying plot shows the difference between the mean and the geometric mean for shape parameters α and β from zero to 2. Besides the fact that the difference between them approaches zero as α and β approach infinity and that the difference becomes large for values of α and β approaching zero, one can observe an evident asymmetry of the geome…
- Translator read (piece 0): `Limit(G_X, beta, 0, dir='+-')`  =  `Limit(G_X, alpha, oo, dir='-')`  · notes: pre:env_align
pre:rows=2
sides: \lim_{\beta \to  0} G_X  ||  \lim_{\alpha \to  \infty} G_X
- Translator read (piece 1): `Limit(G_X, alpha, oo, dir='-')`  =  `1`  · notes: pre:env_align
pre:rows=2
sides: \lim_{\alpha \to  \infty} G_X  ||  1
- Translator read (piece 2): `Limit(G_X, alpha, 0, dir='+-')`  =  `Limit(G_X, beta, oo, dir='-')`  · notes: pre:env_align
pre:rows=2
sides: \lim_{\alpha\to  0} G_X  ||  \lim_{\beta \to  \infty} G_X
- Translator read (piece 3): `Limit(G_X, beta, oo, dir='-')`  =  `0`  · notes: pre:env_align
pre:rows=2
sides: \lim_{\beta \to  \infty} G_X  ||  0
- Assumptions: domains {'G_X': 'positive'}; constants {}; constraints []
- Verifier: Chain link 1: The identity fails at 58 of 59 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at G_X=0.0564545: lhs=0.056454500000, rhs=1.000000000000).
- Counterexample: {'G_X': '0.0564545'} → lhs 0.05645450000000000000000000000000000000, rhs 1.00000000000000000000000000000000000000, rel diff 0.9435455000
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 10/11 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:238686:1378219065:5

- Page: [Binary number](https://en.wikipedia.org/wiki/Binary_number) › Binary arithmetic > Addition > Addition table  · verdict **FAIL**, symbolic not_equal
- LaTeX: `1+1=10`
- Context before: …ditional carry method required eight carry operations, yet the long carry method required only two, representing a substantial reduction of effort. Addition table. 0 1 0 0 1 1 1 10 The binary addition table is similar to, but not the same as, the truth table of the logical disjunction operation $\lor$ . The difference is that $1 \lor 1 = 1$ , while
- Context after: . Subtraction. Subtraction works in much the same way: 0 − 0 → 0 0 − 1 → 1, borrow 1 1 − 0 → 1 1 − 1 → 0 Subtracting a "1" digit from a "0" digit produces the digit "1", while 1 will have to be subtracted from the next column. This is known as borrowing. The principle is the same as for carrying. When the result of a subtraction is less than 0, the…
- Translator read: `2`  =  `10`  · notes: sides: 1+1  ||  10
- Assumptions: domains {}; constants {}; constraints []
- Verifier: The constant identity does not hold: both sides differ beyond 1e-8 relative error, stably at two working precisions (lhs=2.0000000000000000, rhs=10.000000000000000).
- Counterexample: {} → lhs 2.00000000000000000000000000000000000000, rhs 10.0000000000000000000000000000000000000, rel diff 0.8000000000
- Regimes: constant 1/1 fail, 0 err

---
## wiki:en:238686:1378219065:14

- Page: [Binary number](https://en.wikipedia.org/wiki/Binary_number) › Conversion to and from other numeral systems > Binary to decimal  · verdict **FAIL**, symbolic not_equal
- LaTeX: `\frac{2}{3} \times 2 = 1\frac{1}{3} \ge 1`
- Context before: …east $\frac{1}{2}$ , and vice versa. Double that number is at least 1. This suggests the algorithm: Repeatedly double the number to be converted, record if the result is at least 1, and then throw away the integer part. For example, $(\frac{1}{3})_{10}$ , in binary, is: Converting Result $\frac{1}{3}$ 0. $\frac{1}{3} \times 2 = \frac{2}{3} < 1$ 0.0
- Context after: 0.01 $\frac{1}{3} \times 2 = \frac{2}{3} < 1$ 0.010 $\frac{2}{3} \times 2 = 1\frac{1}{3} \ge 1$ 0.0101 Thus the repeating decimal fraction 0.3... is equivalent to the repeating binary fraction 0.01... . Or for example, 0.110, in binary, is: Converting Result 0.1 0. 0.1 × 2 = 0.2 < 1 0.0 0.2 × 2 = 0.4 < 1 0.00 0.4 × 2 = 0.8 < 1 0.000 0.8 × 2 = 1.6 ≥…
- Translator read (piece 0): `4/3`  =  `1/3`  · notes: op:times
sides: \frac{2}{3} \times 2  ||  1\frac{1}{3}
- Translator read (piece 1): `1/3`  >=  `1`  · notes: op:times
sides: 1\frac{1}{3}  ||  1
- Assumptions: domains {}; constants {}; constraints []
- Verifier: Chain link 0: The constant identity does not hold: both sides differ beyond 1e-8 relative error, stably at two working precisions (lhs=1.3333333333333333, rhs=0.3333333333333333).
- Counterexample: {} → lhs 1.33333333333333333333333333333333333333, rhs 0.33333333333333333333333333333333333333, rel diff 0.7500000000
- Regimes: constant 1/1 fail, 0 err
