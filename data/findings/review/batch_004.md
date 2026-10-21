# Review batch 004 — 22 items

For each item answer with one JSON line (Finding schema): {"formula_id": ..., "verdict": "FAIL", "review": {"status": "confirmed_error"|"false_positive"|"ambiguous", "reviewer": "<name>", "notes": "<why, one or two sentences>"}, "suggested_fix": "<corrected LaTeX or null>", "evidence": "<independent source or derivation>"}


---
## wiki:en:9891:1380489591:37

- Page: [Entropy](https://en.wikipedia.org/wiki/Entropy) › Definitions and descriptions > Carnot cycle  · verdict **FAIL**, symbolic not_equal
- LaTeX: `\frac{Q_\mathsf{H}}{T_\mathsf{H}} + \frac{Q_\mathsf{C}}{T_\mathsf{C}} < 0`
- Context before: …ine which is less effective than Carnot cycle (i.e., the work $W$ produced by this engine is less than the maximum predicted by Carnot's theorem), its work output is capped by Carnot efficiency as: $W < \left( 1 - \frac{T_\mathsf{C}}{T_\mathsf{H}} \right) Q_\mathsf{H}$ Substitution of the work $W$ as the net heat into the inequality above gives us:
- Context after: or in terms of the entropy change $\Delta S_{\mathsf{r}, i}$ : $\Delta S_\mathsf{r, H} + \Delta S_\mathsf{r, C} > 0$ A Carnot cycle and an entropy as shown above prove to be useful in the study of any classical thermodynamic heat engine: other cycles, such as an Otto, Diesel or Brayton cycle, could be analysed from the same standpoint. Notably, any…
- Translator read: `Q_C/T_C + Q_H/T_H`  <  `0`  · notes: pre:unwrap
sides: \frac{Q_\mathsf{H}}{T_\mathsf{H}} + \frac{Q_\mathsf{C}}{T_\mathsf{C}}  ||  0
- Assumptions: domains {'Q_C': 'positive', 'Q_H': 'positive', 'T_C': 'positive', 'T_H': 'positive'}; constants {}; constraints []
- Verifier: The inequality fails at 60 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at Q_C=0.186477, Q_H=0.0552707, T_C=0.388219, T_H=0.12789: lhs=0.912513448226, rhs=0).
- Counterexample: {'Q_C': '0.186477', 'Q_H': '0.0552707', 'T_C': '0.388219', 'T_H': '0.12789'} → lhs 0.91251344822685637035041185918039147128, rhs 0, rel diff 1.0000000000
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:90446:1375212682:16

- Page: [Equality (mathematics)](https://en.wikipedia.org/wiki/Equality_(mathematics)) › Equations  · verdict **FAIL**, symbolic not_equal
- LaTeX: `1+1=3`
- Context before: …n and represents variables. Solving an equation corresponds to adding and removing objects on both sides in such a way that the sides stay in balance until the only object remaining on one side is the object of unknown mass. Often, equations are considered to be a statement, or relation, which can be true or false. For example, $1+1=2$ is true, and
- Context after: is false. Equations with unknowns are considered conditionally true; for example, $x^2 - 6x + 5=0$ is true when $x=1$ or $x=5,$ and false otherwise. There are several different terminologies for this. In mathematical logic, an equation is a binary predicate (i.e. a logical statement, that can have free variables) which satisfies certain properties.…
- Translator read: `2`  =  `3`  · notes: sides: 1+1  ||  3
- Assumptions: domains {}; constants {}; constraints []
- Verifier: The constant identity does not hold: both sides differ beyond 1e-8 relative error, stably at two working precisions (lhs=2.0000000000000000, rhs=3.0000000000000000).
- Counterexample: {} → lhs 2.00000000000000000000000000000000000000, rhs 3.00000000000000000000000000000000000000, rel diff 0.3333333333
- Regimes: constant 1/1 fail, 0 err

---
## wiki:en:24022514:1329285092:3

- Page: [Equipollence (geometry)](https://en.wikipedia.org/wiki/Equipollence_(geometry)) › Spherical geometry  · verdict **FAIL**, symbolic unknown
- LaTeX: `\exp(a r) = \cos a + r \sin a ,`
- Context before: …n a Euclidean three-dimensional space. Two such arcs are deemed equivalent if by sliding one along its great circle it can be made to coincide with the other. On a great circle of a sphere, two directed circular arcs are equipollent when they agree in direction and arc length. An equivalence class of such arcs is associated with a quaternion versor
- Context after: where a is arc length and r determines the plane of the great circle by perpendicularity. Abstraction. Properties of the equivalence classes of equipollent segments can be abstracted to define affine space: If A is a set of points and V is a vector space, then (A, V) is an affine space provided that for any two points a,b in A there is a vector $\o…
- Translator read: `exp(a*r)`  =  `r*sin(a) + cos(a)`  · notes: pre:trailing_punct
sides: \exp(a r)  ||  \cos a + r \sin a
- Assumptions: domains {'a': 'real', 'r': 'nonneg'}; constants {}; constraints []
- Verifier: The identity fails at 60 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at a=0.361486, r=0.363855: lhs=1.140570400433, rhs=1.064054939158).
- Counterexample: {'a': '0.361486', 'r': '0.363855'} → lhs 1.14057040043360414067242506200171083173, rhs 1.06405493915856591827675235902477326773, rel diff 0.0670852594
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:148594:1378444832:37

- Page: [Euler's constant](https://en.wikipedia.org/wiki/Euler's_constant) › Formulas and identities > Relation to gamma function  · verdict **FAIL**, symbolic not_equal
- LaTeX: `\begin{align} \gamma &= \lim_{n\to\infty}\left(\frac{ \Gamma\left(\frac1{n}\right) \Gamma(n+1)\, n^{1+\frac1{n}}}{\Gamma\left(2+n+\frac1{n}\right)} - \frac{n^2}{n+1}\right) \\
&= \lim\limits_{m\to\infty}\sum_{k=1}^m{m \choose k}\frac{(-1)^k}{k}\log\big(\Gamma(k+1)\big). \end{align}`
- Context before: …Further limit results are: $\begin{align} \lim_{z\to 0}\frac1{z}\left(\frac1{\Gamma(1+z)} - \frac1{\Gamma(1-z)}\right) &= 2\gamma \\ \lim_{z\to 0}\frac1{z}\left(\frac1{\psi(1-z)} - \frac1{\psi(1+z)}\right) &= \frac{\pi^2}{3\gamma^2}. \end{align}$ A limit related to the beta function (expressed in terms of gamma functions) is
- Context after: Relation to the zeta function. γ can also be expressed as an infinite sum whose terms involve the Riemann zeta function evaluated at positive integers: $\begin{align}\gamma &= \sum_{m=2}^{\infty} (-1)^m\frac{\zeta(m)}{m} \\ &= \log\frac4{\pi} + \sum_{m=2}^{\infty} (-1)^m\frac{\zeta(m)}{2^{m-1}m}.\end{align}$ The constant $\gamma$ can also be expres…
- Translator read (piece 0): `gamma`  =  `Limit(-n**2/(n + 1) + n**(1 + 1/n)*gamma(1/n)*gamma(n + 1)/gamma(n + 2 + 1/n), n, oo, dir='-')`  · notes: pre:over_choose
pre:drop
pre:left_right
pre:size
pre:spacing
pre:env_align
pre:row_continues_chain
pre:trailing_punct
log:unspecified_base
sides: \gamma  ||  \lim_{n\to\infty}\left(\frac{ \Gamma\left(\frac1{n}\right) \Gamma(n+1)\, n^{1+\frac1{n}}}{\Gamma\left(2+n+\frac1{n}\right)} - \frac{n^2}{n+1}\right)
- Translator read (piece 1): `Limit(-n**2/(n + 1) + n**(1 + 1/n)*gamma(1/n)*gamma(n + 1)/gamma(n + 2 + 1/n), n, oo, dir='-')`  =  `Limit(Sum((-1)**k*log(gamma(k + 1))*binomial(m, k)/k, (k, 1, m)), m, oo, dir='-')`  · notes: pre:over_choose
pre:drop
pre:left_right
pre:size
pre:spacing
pre:env_align
pre:row_continues_chain
pre:trailing_punct
log:unspecified_base
sides: \lim_{n\to\infty}\left(\frac{ \Gamma\left(\frac1{n}\right) \Gamma(n+1)\, n^{1+\frac1{n}}}{\Gamma\left(2+n+\frac1{n}\right)} - \frac{n^2}{n+1}\right)  ||  \lim\limits_{m\to\infty}\sum_{k=1}^m{\binom{m }{ k}}\frac{(-1)^k}{k}\log\big(\Gamma(k+1)\big)
- Assumptions: domains {}; constants {'gamma': 'EulerGamma'}; constraints []
- Verifier: Chain link 0: The constant identity does not hold: both sides differ beyond 1e-8 relative error, stably at two working precisions (lhs=0.5772156649015328, rhs=-0.577215664901532).
- Counterexample: {} → lhs 0.57721566490153286060651209008240243104, rhs -0.5772156649015328606065120900824024310, rel diff 2.0000000000
- Regimes: constant 1/1 fail, 0 err

---
## wiki:en:148594:1378444832:115

- Page: [Euler's constant](https://en.wikipedia.org/wiki/Euler's_constant) › Generalizations > Euler–Lehmer constants  · verdict **FAIL**, symbolic unknown
- LaTeX: `q\gamma(a,q) = \frac{q}{d}\gamma\left(\frac{a}{d},\frac{q}{d}\right)-\log d.`
- Context before: …<n\le x \atop n\equiv a \pmod q} \frac1{n}-\frac{\log x}{q}\right).$ The basic properties are $\begin{align} &\gamma(0,q) = \frac{\gamma -\log q}{q}, \\ &\sum_{a=0}^{q-1} \gamma(a,q)=\gamma, \\ &q\gamma(a,q) = \gamma-\sum_{j=1}^{q-1}e^{-\frac{2\pi aij}{q}}\log\left(1-e^{\frac{2\pi ij}{q}}\right), \end{align}$ and if the greatest common divisor then
- Context after: Masser–Gramain constant. A two-dimensional generalization of Euler's constant is the Masser–Gramain constant. It is defined as the following limiting difference: $\delta = \lim_{n\to\infty} \left( -\log n + \sum_{k=2}^n \frac{1}{\pi r_k^2} \right)$ where $r_k$ is the smallest radius of a disk in the complex plane containing at least $k$ Gaussian in…
- Translator read: `q*lowergamma(a, q)`  =  `-log(d) + q*lowergamma(a/d, q/d)/d`  · notes: pre:left_right
pre:trailing_punct
funcapp_rule:gamma:comma_args
log:unspecified_base
sides: q\gamma(a,q)  ||  \frac{q}{d}\gamma\left(\frac{a}{d},\frac{q}{d}\right)-\log d
- Assumptions: domains {'a': 'real', 'd': 'positive', 'q': 'positive'}; constants {}; constraints []
- Verifier: The identity fails at 59 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at a=0.134044, d=0.148506, q=0.129484: lhs=0.723592186336, rhs=2.490008347293).
- Counterexample: {'a': '0.134044', 'd': '0.148506', 'q': '0.129484'} → lhs 0.72359218633611278427268658198830933560, rhs 2.49000834729349087381016606399598549928, rel diff 0.7094017025
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 11/13 fail, 1 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:9678:1370424026:48

- Page: [Exponential function](https://en.wikipedia.org/wiki/Exponential_function) › Definitions and fundamental properties > Properties  · verdict **FAIL**, symbolic not_equal
- LaTeX: `e^x<0`
- Context before: …n goes to infinity, $\exp(x)=\lim_{n \to +\infty} \left(1+\frac xn\right)^n.$ Properties. Reciprocal: The functional equation implies $e^x e^{-x}=1$ . Therefore $e^x \ne 0$ for every $x$ and $\frac 1{e^x}=e^{-x}.$ Positiveness: $e^x>0$ for every real number $x$ . This results from the intermediate value theorem, since $e^0=1$ and, if one would have
- Context after: for some $x$ , there would be an $y$ such that $e^y=0$ between $0$ and $x$ . Since the exponential function equals its derivative, this implies that the exponential function is monotonically increasing. Extension of exponentiation to positive real bases: Let b be a positive real number. The exponential function and the natural logarithm being the i…
- Translator read: `e**x`  <  `0`  · notes: hint:e_only_as_exp_base
sides: e^x  ||  0
- Assumptions: domains {'x': 'real'}; constants {'e': 'E'}; constraints []
- Verifier: The inequality fails at 60 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at x=0: lhs=1.000000000000, rhs=0).
- Counterexample: {'x': '0'} → lhs 1.00000000000000000000000000000000000000, rhs 0, rel diff 1.0000000000
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:99491:1379331466:211

- Page: [Exponentiation](https://en.wikipedia.org/wiki/Exponentiation) › Non-integer exponents with a complex base > Complex exponentiation > Computation > Examples  · verdict **FAIL**, symbolic unknown
- LaTeX: `\begin{align}
(-2)^{3 + 4i} &= 2^3 e^{-4(\pi+2k\pi)} (\cos(4\ln 2 + 3(\pi +2k\pi)) +i\sin(4\ln 2 + 3(\pi+2k\pi)))\\
&=-2^3 e^{-4(\pi+2k\pi)}(\cos(4\ln 2) +i\sin(4\ln 2)).
\end{align}`
- Context before: …and the values of $\log i$ are thus $\log i=i\left(\frac \pi 2 +2k\pi\right).$ It follows that $i^i=e^{i\log i}=e^{-\frac \pi 2} e^{-2k\pi}.$ So, all values of $i^i$ are real, the principal one being $e^{-\frac \pi 2} \approx 0.2079.$ $(-2)^{3+4i}$ Similarly, the polar form of −2 is $-2 = 2e^{i \pi}.$ So, the above described method gives the values
- Context after: In this case, all the values have the same argument $4\ln 2,$ and different absolute values. In both examples, all values of $z^w$ have the same argument. More generally, this is true if and only if the real part of w is an integer. Failure of power and logarithm identities. Some identities for powers and logarithms for positive real numbers will f…
- Translator read (piece 0): `(-2)**(4*i + 3)`  =  `8*e**(-8*pi*k - 4*pi)*(-i*sin(6*pi*k + 4*log(2)) - cos(6*pi*k + 4*log(2)))`  · notes: pre:env_align
pre:row_continues_chain
pre:trailing_punct
hint:e_only_as_exp_base
hint:i_present
sides: (-2)^{3 + 4i}  ||  2^3 e^{-4(\pi+2k\pi)} (\cos(4\ln 2 + 3(\pi +2k\pi)) +i\sin(4\ln 2 + 3(\pi+2k\pi)))
- Translator read (piece 1): `8*e**(-8*pi*k - 4*pi)*(-i*sin(6*pi*k + 4*log(2)) - cos(6*pi*k + 4*log(2)))`  =  `-8*e**(-8*pi*k - 4*pi)*(i*sin(4*log(2)) + cos(4*log(2)))`  · notes: pre:env_align
pre:row_continues_chain
pre:trailing_punct
hint:e_only_as_exp_base
hint:i_present
sides: 2^3 e^{-4(\pi+2k\pi)} (\cos(4\ln 2 + 3(\pi +2k\pi)) +i\sin(4\ln 2 + 3(\pi+2k\pi)))  ||  -2^3 e^{-4(\pi+2k\pi)}(\cos(4\ln 2) +i\sin(4\ln 2))
- Assumptions: domains {'k': 'nonneg_integer'}; constants {'e': 'E', 'i': 'I'}; constraints []
- Verifier: Chain link 0: The identity fails at 46 of 49 evaluable points, a clear majority in every regime (small_positive, integers_small, mixed_sign, large) (e.g. at k=1: lhs=(0.00002602079, rhs=(3.16453351944).
- Counterexample: {'k': '1'} → lhs (0.0000260207931851134915263428631915232, rhs (3.1645335194456882683766523433077678091, rel diff 0.9999999999
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 3/4 fail, 0 err, integers_small 11/12 fail, 0 err, mixed_sign 8/9 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:99491:1379331466:261

- Page: [Exponentiation](https://en.wikipedia.org/wiki/Exponentiation) › Integer powers in algebra > Finite fields  · verdict **FAIL**, symbolic unknown
- LaTeX: `x^q=x`
- Context before: …ents is either a prime number or a prime power; that is, it has the form $q=p^k,$ where p is a prime number, and k is a positive integer. For every such q, there are fields with q elements. The fields with q elements are all isomorphic, which allows, in general, working as if there were only one field with q elements, denoted $\mathbb F_q.$ One has
- Context after: for every $x\in \mathbb F_q.$ A primitive element in $\mathbb F_q$ is an element g such that the set of the q − 1 first powers of g (that is, $\{g^1=g, g^2, \ldots, g^{p-1}=g^0=1\}$ ) equals the set of the nonzero elements of $\mathbb F_q.$ There are $\varphi (p-1)$ primitive elements in $\mathbb F_q,$ where $\varphi$ is Euler's totient function. I…
- Translator read: `x**q`  =  `x`  · notes: sides: x^q  ||  x
- Assumptions: domains {'q': 'positive', 'x': 'real'}; constants {}; constraints ['x > 0']
- Verifier: The identity fails at 59 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at q=0.227325, x=0.0616337: lhs=0.530756634314, rhs=0.061633700000).
- Counterexample: {'q': '0.227325', 'x': '0.0616337'} → lhs 0.53075663431405481986366354449345165313, rhs 0.06163370000000000000000000000000000000, rel diff 0.8838757803
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 11/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:99491:1379331466:270

- Page: [Exponentiation](https://en.wikipedia.org/wiki/Exponentiation) › Integer powers in algebra > Finite fields  · verdict **FAIL**, symbolic unknown
- LaTeX: `(x+y)^p = x^p+y^p`
- Context before: …ent in $\mathbb F_q$ is an element g such that the set of the q − 1 first powers of g (that is, $\{g^1=g, g^2, \ldots, g^{p-1}=g^0=1\}$ ) equals the set of the nonzero elements of $\mathbb F_q.$ There are $\varphi (p-1)$ primitive elements in $\mathbb F_q,$ where $\varphi$ is Euler's totient function. In $\mathbb F_q,$ the freshman's dream identity
- Context after: is true for the exponent p. As $x^p=x$ in $\mathbb F_q,$ It follows that the map $\begin{align} F\colon{} & \mathbb F_q \to \mathbb F_q\\ & x\mapsto x^p \end{align}$ is linear over $\mathbb F_q,$ and is a field automorphism, called the Frobenius automorphism. If $q=p^k,$ the field $\mathbb F_q$ has k automorphisms, which are the k first powers (und…
- Translator read: `(x + y)**p`  =  `x**p + y**p`  · notes: sides: (x+y)^p  ||  x^p+y^p
- Assumptions: domains {'p': 'positive', 'x': 'real', 'y': 'real'}; constants {}; constraints ['x + y > 0', 'y > 0', 'x > 0']
- Verifier: The identity fails at 56 of 58 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at p=0.289443, x=0.428486, y=0.27517: lhs=0.903274052549, rhs=1.470797707768).
- Counterexample: {'p': '0.289443', 'x': '0.428486', 'y': '0.27517'} → lhs 0.90327405254958445620823311525940592499, rhs 1.47079770776840350825499857484629172134, rel diff 0.3858611229
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 10/12 fail, 0 err, mixed_sign 10/10 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:1273836:1363301178:1

- Page: [Exsecant](https://en.wikipedia.org/wiki/Exsecant) › (lead)  · verdict **FAIL**, symbolic unknown
- LaTeX: `\operatorname{vers}\theta = 1 - \cos\theta`
- Context before: …The external secant function (abbreviated exsecant, symbolized exsec) is a trigonometric function defined in terms of the secant function: $\operatorname{exsec} \theta = \sec\theta - 1 = \frac{1}{\cos\theta} - 1.$ It was introduced in 1855 by American civil engineer Charles Haslett, who used it in conjunction with the existing versine function,
- Context after: , for designing and measuring circular sections of railroad track. It was adopted by surveyors and civil engineers in the United States for railroad and road design, and since the early 20th century has sometimes been briefly mentioned in American trigonometry textbooks and general-purpose engineering manuals. For completeness, a few books also def…
- Translator read: `theta*vers`  =  `1 - cos(theta)`  · notes: sides: \operatorname{vers}\theta  ||  1 - \cos\theta
- Assumptions: domains {'theta': 'angle', 'vers': 'positive'}; constants {}; constraints []
- Verifier: The identity fails at 60 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at theta=0.0488175, vers=0.0132221: lhs=0.000645469866, rhs=0.001191337530).
- Counterexample: {'theta': '0.0488175', 'vers': '0.0132221'} → lhs 0.00064546986675000000000000000000000000, rhs 0.00119133753042885993841275369129887721, rel diff 0.4581973200
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:1273836:1363301178:0

- Page: [Exsecant](https://en.wikipedia.org/wiki/Exsecant) › (lead)  · verdict **FAIL**, symbolic unknown
- LaTeX: `\operatorname{exsec} \theta = \sec\theta - 1 = \frac{1}{\cos\theta} - 1.`
- Context before: …The external secant function (abbreviated exsecant, symbolized exsec) is a trigonometric function defined in terms of the secant function:
- Context after: It was introduced in 1855 by American civil engineer Charles Haslett, who used it in conjunction with the existing versine function, $\operatorname{vers}\theta = 1 - \cos\theta$ , for designing and measuring circular sections of railroad track. It was adopted by surveyors and civil engineers in the United States for railroad and road design, and si…
- Translator read (piece 0): `exsec*theta`  =  `sec(theta) - 1`  · notes: pre:trailing_punct
sides: \operatorname{exsec} \theta  ||  \sec\theta - 1
- Translator read (piece 1): `sec(theta) - 1`  =  `-1 + 1/cos(theta)`  · notes: pre:trailing_punct
sides: \sec\theta - 1  ||  \frac{1}{\cos\theta} - 1
- Assumptions: domains {'exsec': 'positive', 'theta': 'angle'}; constants {}; constraints ['Ne(cos(theta), 0)']
- Verifier: Chain link 0: The identity fails at 59 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at exsec=0.16905, theta=0.072685: lhs=0.012287399250, rhs=0.002647381974).
- Counterexample: {'exsec': '0.16905', 'theta': '0.072685'} → lhs 0.01228739925000000000000000000000000000, rhs 0.00264738197460833047566336631276131399, rel diff 0.7845449699
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 11/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:1273836:1363301178:17

- Page: [Exsecant](https://en.wikipedia.org/wiki/Exsecant) › Mathematical identities > Double angle identity  · verdict **FAIL**, symbolic unknown
- LaTeX: `\operatorname{exsec} 2\theta = \frac{2 \sin^2 \theta} {1 - 2 \sin^2 \theta}.`
- Context before: …are: $\begin{align} \frac{\mathrm{d}}{\mathrm{d}x}\operatorname{exsec} x &= \tan x\,\sec x, \\[10mu] \int\operatorname{exsec} x\,\mathrm{d}x &= \ln\bigl|{\sec x + \tan x}\bigr| - x + C,\vphantom{\int_|} \end{align}$ where ln is the natural logarithm. See also Integral of the secant function. Double angle identity. The exsecant of twice an angle is:
- Context after: See also. Chord (geometry) – A line segment with endpoints on the circumference of a circle, historically used trigonometrically Exponential minus 1 – The function $x \mapsto e^x - 1$ , also used to improve precision for small inputs Notes and references.…
- Translator read: `2*exsec*theta`  =  `2*sin(theta)**2/(1 - 2*sin(theta)**2)`  · notes: pre:trailing_punct
sides: \operatorname{exsec} 2\theta  ||  \frac{2 \sin^2 \theta} {1 - 2 \sin^2 \theta}
- Assumptions: domains {'exsec': 'positive', 'theta': 'angle'}; constants {}; constraints ['Ne(-1*2*sin(theta)**2 + 1, 0)']
- Verifier: The identity fails at 60 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at exsec=0.0658055, theta=0.010141: lhs=0.001334667151, rhs=0.000205715021).
- Counterexample: {'exsec': '0.0658055', 'theta': '0.010141'} → lhs 0.00133466715100000000000000000000000000, rhs 0.00020571502136881673320222030926492988, rel diff 0.8458679220
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:221537:1380665267:242

- Page: [Exterior algebra](https://en.wikipedia.org/wiki/Exterior_algebra) › Alternating tensor algebra  · verdict **FAIL**, symbolic unknown
- LaTeX: `\operatorname{\mathcal{A}^{(r)}}\operatorname{\mathcal{A}^{(r)}}=r!\operatorname{\mathcal{A}^{(r)}}.`
- Context before: …where the sum is taken over the symmetric group of permutations on the symbols $\{ 1, \dots, r \}$ . This extends by linearity and homogeneity to an operation, also denoted by $\mathcal{A}$ and $\rm{Alt}$ , on the full tensor algebra $\mathrm{T}(V)$ . Note that
- Context after: Such that, when defined, $\operatorname{Alt}^{(r)}$ is the projection for the exterior (quotient) algebra onto the r-homogeneous alternating tensor subspace. On the other hand, the image $\mathcal{A}(\mathrm{T}(V))$ is always the alternating tensor graded subspace (not yet an algebra, as product is not yet defined), denoted $A(V)$ . This is a vecto…
- Translator read: `\mathcal{A}^{(r)}**2`  =  `\mathcal{A}^{(r)}*factorial(r)`  · notes: pre:trailing_punct
sides: \operatorname{\mathcal{A}^{(r)}}\operatorname{\mathcal{A}^{(r)}}  ||  r!\operatorname{\mathcal{A}^{(r)}}
- Assumptions: domains {'\\mathcal{A}^{(r)}': 'positive', 'r': 'nonneg_integer'}; constants {}; constraints []
- Verifier: The identity fails at 60 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at \mathcal{A}^{(r)}=0.0916286, r=0: lhs=0.008395800337, rhs=0.091628600000).
- Counterexample: {'\\mathcal{A}^{(r)}': '0.0916286', 'r': '0'} → lhs 0.00839580033796000000000000000000000000, rhs 0.09162860000000000000000000000000000000, rel diff 0.9083714000
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:9305752:1302584352:0

- Page: [Fanno flow](https://en.wikipedia.org/wiki/Fanno_flow) › Theory  · verdict **FAIL**, symbolic unknown
- LaTeX: `\ \frac{dM^2}{M^2} = \frac{\gamma M^2}{1 - M^2}\left(1 + \frac{\gamma - 1}{2}M^2\right)\frac{4f}{D_h}dx`
- Context before: …calorically perfect gas the maximum entropy occurs at M = 1.0. Theory. The Fanno flow model begins with a differential equation that relates the change in Mach number with respect to the length of the duct, dM/dx. Other terms in the differential equation are the heat capacity ratio, γ, the Fanning friction factor, f, and the hydraulic diameter, Dh:
- Context after: Assuming the Fanning friction factor is a constant along the duct wall, the differential equation can be solved easily. One must keep in mind, however, that the value of the Fanning friction factor can be difficult to determine for supersonic and especially hypersonic flow velocities. The resulting relation is shown below where L* is the required d…
- Translator read: `d`  =  `4*M**2*d*f*gamma*x*(M**2*(gamma/2 - 1/2) + 1)/(D_h*(1 - M**2))`  · notes: pre:left_right
pre:spacing
sides: \frac{dM^2}{M^2}  ||  \frac{\gamma M^2}{1 - M^2}\left(1 + \frac{\gamma - 1}{2}M^2\right)\frac{4f}{D_h}dx
- Assumptions: domains {'D_h': 'positive', 'M': 'positive', 'd': 'positive', 'f': 'positive', 'gamma': 'positive', 'x': 'real'}; constants {}; constraints ['Ne(1 - M**2, 0)']
- Verifier: The identity fails at 60 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at D_h=0.446601, M=0.468, d=0.305681, f=0.310455, gamma=0.278104, x=0.380183: lhs=0.305681000000, rhs=0.023211031691).
- Counterexample: {'D_h': '0.446601', 'M': '0.468', 'd': '0.305681', 'f': '0.310455', 'gamma': '0.278104', 'x': '0.380183'} → lhs 0.30568100000000000000000000000000000000, rhs 0.02321103169159104397789266921716172594, rel diff 0.9240677971
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:11615:1378306084:92

- Page: [Finite field](https://en.wikipedia.org/wiki/Finite_field) › Existence and uniqueness  · verdict **FAIL**, symbolic unknown
- LaTeX: `x^q = x,`
- Context before: …oots of $X^q-X$ , and $F$ cannot contain another subfield of order $q$ . In summary, we have the following classification theorem first proved in 1893 by E.&nbsp;H.&nbsp;Moore: The order of a finite field is a prime power. For every prime power $q$ there are fields of order $q$ , and they are all isomorphic. In these fields, every element satisfies
- Context after: and the polynomial $X^q - X$ factors as $X^q - X = \prod_{a\in F} (X - a).$ It follows that $\mathrm{GF}(p^n)$ contains a subfield isomorphic to $\mathrm{GF}(p^m)$ if and only if $m$ is a divisor of $n$ ; in that case, this subfield is unique. In fact, the polynomial $X^{p^m}-X$ divides $X^{p^n}-X$ if and only if $m$ is a divisor of $n$ . Explicit…
- Translator read: `x**q`  =  `x`  · notes: pre:trailing_punct
sides: x^q  ||  x
- Assumptions: domains {'q': 'positive', 'x': 'real'}; constants {}; constraints ['x > 0']
- Verifier: The identity fails at 58 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at q=0.095641, x=0.0638937: lhs=0.768692798216, rhs=0.063893700000).
- Counterexample: {'q': '0.095641', 'x': '0.0638937'} → lhs 0.76869279821624634035785524801721062214, rhs 0.06389370000000000000000000000000000000, rel diff 0.9168800590
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 10/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:11615:1378306084:156

- Page: [Finite field](https://en.wikipedia.org/wiki/Finite_field) › Explicit construction > Field with four elements  · verdict **FAIL**, symbolic unknown
- LaTeX: `\mathrm{GF}(4) = \mathrm{GF}(2)[X]/(X^2+X+1).`
- Context before: …duced from the distributive law. See below for the complete operation tables. This may be deduced as follows from the results of the preceding section. Over $\mathrm{GF}(2)$ , there is only one irreducible polynomial of degree $2$ : $X^2+X+1$ Therefore, for $\mathrm{GF}(4)$ the construction of the preceding section must involve this polynomial, and
- Context after: Let $\alpha$ denote a root of this polynomial in $\mathrm{GF}(4)$ . This implies that $\alpha^2 = 1 + \alpha,$ and that $\alpha$ and $1+\alpha$ are the elements of $\mathrm{GF}(4)$ that are not in $\mathrm{GF}(2)$ . The tables of the operations in $\mathrm{GF}(4)$ result from this, and are as follows: + Addition $x + y$ style="width:24%;" 0 1 α 1 +…
- Translator read: `4*GF`  =  `2*GF*X/(X**2 + X + 1)`  · notes: pre:trailing_punct
roman_word:GF
sides: \mathrm{GF}(4)  ||  \mathrm{GF}(2)[X]/(X^2+X+1)
- Assumptions: domains {'GF': 'positive', 'X': 'positive'}; constants {}; constraints []
- Verifier: The identity fails at 60 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at GF=0.187833, X=0.200399: lhs=0.751332000000, rhs=0.060684824620).
- Counterexample: {'GF': '0.187833', 'X': '0.200399'} → lhs 0.75133200000000000000000000000000000000, rhs 0.06068482462087259363037120652847318092, rel diff 0.9192303474
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:54267:1379191356:65

- Page: [Floor and ceiling functions](https://en.wikipedia.org/wiki/Floor_and_ceiling_functions) › Applications > Rounding  · verdict **FAIL**, symbolic unknown
- LaTeX: `\text{rpi}(x)=\left\lfloor x+\tfrac{1}{2}\right\rfloor = \left\lceil \tfrac12\lfloor 2x \rfloor \right\rceil;`
- Context before: …l numbers mod odd primes p: $\begin{align} \left(\frac{2}{p}\right) &= (-1)^{\left\lfloor\frac{p+1}{4}\right\rfloor}, \\[5mu] \left(\frac{3}{p}\right) &= (-1)^{\left\lfloor\frac{p+1}{6}\right\rfloor}. \end{align}$ Rounding. For an arbitrary real number $x$ , rounding $x$ to the nearest integer with tie breaking towards positive infinity is given by
- Context after: rounding towards negative infinity is given as $\text{rni}(x)=\left\lceil x-\tfrac{1}{2}\right\rceil = \left\lfloor \tfrac12 \lceil 2x \rceil \right\rfloor.$ If tie-breaking is away from 0, then the rounding function is $\text{ri}(x) = \sgn(x)\left\lfloor|x|+\tfrac{1}{2}\right\rfloor$ (where $\sgn$ is the sign function), and rounding towards even c…
- Translator read (piece 0): `rpi*x`  =  `floor(x + 1/2)`  · notes: pre:left_right
pre:trailing_punct
text_symbol:rpi
sides: \text{rpi}(x)  ||  \lfloor x+\tfrac{1}{2}\right\rfloor
- Translator read (piece 1): `floor(x + 1/2)`  =  `ceiling(floor(2*x)/2)`  · notes: pre:left_right
pre:trailing_punct
text_symbol:rpi
sides: \lfloor x+\tfrac{1}{2}\right\rfloor  ||  \lceil \tfrac12\lfloor 2x \rfloor \right\rceil
- Assumptions: domains {'rpi': 'positive', 'x': 'real'}; constants {}; constraints []
- Verifier: Chain link 0: The identity fails at 59 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at rpi=0.122846, x=0.102725: lhs=0.012619355350, rhs=0).
- Counterexample: {'rpi': '0.122846', 'x': '0.102725'} → lhs 0.01261935535000000000000000000000000000, rhs 0, rel diff 1.0000000000
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 11/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:54267:1379191356:67

- Page: [Floor and ceiling functions](https://en.wikipedia.org/wiki/Floor_and_ceiling_functions) › Applications > Rounding  · verdict **FAIL**, symbolic unknown
- LaTeX: `\text{ri}(x) = \sgn(x)\left\lfloor|x|+\tfrac{1}{2}\right\rfloor`
- Context before: …finity is given by $\text{rpi}(x)=\left\lfloor x+\tfrac{1}{2}\right\rfloor = \left\lceil \tfrac12\lfloor 2x \rfloor \right\rceil;$ rounding towards negative infinity is given as $\text{rni}(x)=\left\lceil x-\tfrac{1}{2}\right\rceil = \left\lfloor \tfrac12 \lceil 2x \rceil \right\rfloor.$ If tie-breaking is away from 0, then the rounding function is
- Context after: (where $\sgn$ is the sign function), and rounding towards even can be expressed with the more cumbersome $\lfloor x\rceil=\left\lfloor x+\tfrac{1}{2}\right\rfloor+\left\lceil\tfrac14(2x-1)\right\rceil-\left\lfloor\tfrac14(2x-1)\right\rfloor-1,$ which is the above expression for rounding towards positive infinity $\text{rpi}(x)$ minus an integrality…
- Translator read: `ri*x`  =  `floor(Abs(x) + 1/2)*sign(x)`  · notes: pre:left_right
text_symbol:ri
sides: \text{ri}(x)  ||  \sgn(x)\left\lfloor|x|+\tfrac{1}{2}\right\rfloor
- Assumptions: domains {'ri': 'positive', 'x': 'real'}; constants {}; constraints []
- Verifier: The identity fails at 59 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at ri=0.0988196, x=0.111485: lhs=0.011016903106, rhs=0).
- Counterexample: {'ri': '0.0988196', 'x': '0.111485'} → lhs 0.01101690310600000000000000000000000000, rhs 0, rel diff 1.0000000000
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 11/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:54267:1379191356:62

- Page: [Floor and ceiling functions](https://en.wikipedia.org/wiki/Floor_and_ceiling_functions) › Applications > Quadratic reciprocity  · verdict **FAIL**, symbolic unknown
- LaTeX: `\begin{align}
\left(\frac{2}{p}\right) &= (-1)^{\left\lfloor\frac{p+1}{4}\right\rfloor}, \\[5mu]
\left(\frac{3}{p}\right) &= (-1)^{\left\lfloor\frac{p+1}{6}\right\rfloor}.
\end{align}`
- Context before: …Combining these formulas gives quadratic reciprocity in the form $\left(\frac{p}{q}\right) \left(\frac{q}{p}\right) = (-1)^{mn}=(-1)^{\frac{p-1}{2}\frac{q-1}{2}}.$ There are formulas that use floor to express the quadratic character of small numbers mod odd primes p:
- Context after: Rounding. For an arbitrary real number $x$ , rounding $x$ to the nearest integer with tie breaking towards positive infinity is given by $\text{rpi}(x)=\left\lfloor x+\tfrac{1}{2}\right\rfloor = \left\lceil \tfrac12\lfloor 2x \rfloor \right\rceil;$ rounding towards negative infinity is given as…
- Translator read (piece 0): `2/p`  =  `(-1)**floor(p/4 + 1/4)`  · notes: pre:left_right
pre:env_align
pre:rows=2
pre:trailing_punct
sides: (\frac{2}{p}\right)  ||  (-1)^{\left\lfloor\frac{p+1}{4}\right\rfloor}
- Translator read (piece 1): `3/p`  =  `(-1)**floor(p/6 + 1/6)`  · notes: pre:left_right
pre:env_align
pre:rows=2
pre:trailing_punct
sides: (\frac{3}{p}\right)  ||  (-1)^{\left\lfloor\frac{p+1}{6}\right\rfloor}
- Assumptions: domains {'p': 'positive_integer'}; constants {}; constraints ['Q.prime(p)']
- Verifier: Chain link 0: The identity fails at 42 of 46 evaluable points, a clear majority in every regime (small_positive, integers_small, mixed_sign, large) (e.g. at p=1: lhs=2.000000000000, rhs=1.000000000000).
- Counterexample: {'p': '1'} → lhs 2.00000000000000000000000000000000000000, rhs 1.00000000000000000000000000000000000000, rel diff 0.5000000000
- Regimes: small_positive 10/11 fail, 0 err, unit_interval 2/3 fail, 0 err, integers_small 11/12 fail, 0 err, mixed_sign 7/8 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:52247:1377137736:547

- Page: [Fourier transform](https://en.wikipedia.org/wiki/Fourier_transform) › Tables of important Fourier transforms > Functional relationships, one-dimensional  · verdict **FAIL**, symbolic unknown
- LaTeX: `\cos(a x) = \tfrac{e^{i a x} + e^{-i a x} }{2}`
- Context before: …Complex conjugation, generalization of 110 and 113 115 $f(x) \cos (a x)$ $\frac{ \widehat{f}{\left(\xi - \frac{a}{2\pi}\right)} + \widehat{f}{\left(\xi+\frac{a}{2\pi}\right)}}{2}$ $\frac{\widehat{f}(\omega-a)+\widehat{f}(\omega+a)}{2}$ $\frac{\widehat{f}(\omega-a)+\widehat{f}(\omega+a)}{2}$ This follows from rules 101 and 103 using Euler's formula:
- Context after: . 116 $f(x)\sin( ax)$ $\frac{\widehat{f}{\left(\xi-\frac{a}{2\pi}\right)} - \widehat{f}{\left(\xi+\frac{a}{2\pi}\right)}}{2i}$ $\frac{\widehat{f}(\omega-a)-\widehat{f}(\omega+a)}{2i}$ $\frac{\widehat{f}(\omega-a)-\widehat{f}(\omega+a)}{2i}$ This follows from 101 and 103 using Euler's formula: $\sin(a x) = \tfrac{e^{i a x} - e^{-i a x} }{2i}$ . Squa…
- Translator read: `cos(a*x)`  =  `e^iax/2 + 1/(2*e**(a*i*x))`  · notes: superscript_label:e^iax
hint:e_only_as_exp_base
hint:i_present
sides: \cos(a x)  ||  \tfrac{e^{i a x} + e^{-i a x} }{2}
- Assumptions: domains {'a': 'real', 'e^iax': 'positive', 'x': 'real'}; constants {'e': 'E', 'i': 'I'}; constraints []
- Verifier: The identity fails at 60 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at a=0.134135, e^iax=0.0684811, x=0.168742: lhs=0.999743857245, rhs=(0.53411247862).
- Counterexample: {'a': '0.134135', 'e^iax': '0.0684811', 'x': '0.168742'} → lhs 0.99974385724585726624052600247226230882, rhs (0.5341124786229286331202630012361311544, rel diff 0.4658881990
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:52247:1377137736:552

- Page: [Fourier transform](https://en.wikipedia.org/wiki/Fourier_transform) › Tables of important Fourier transforms > Functional relationships, one-dimensional  · verdict **FAIL**, symbolic unknown
- LaTeX: `\sin(a x) = \tfrac{e^{i a x} - e^{-i a x} }{2i}`
- Context before: …ormula: $\cos(a x) = \tfrac{e^{i a x} + e^{-i a x} }{2}$ . 116 $f(x)\sin( ax)$ $\frac{\widehat{f}{\left(\xi-\frac{a}{2\pi}\right)} - \widehat{f}{\left(\xi+\frac{a}{2\pi}\right)}}{2i}$ $\frac{\widehat{f}(\omega-a)-\widehat{f}(\omega+a)}{2i}$ $\frac{\widehat{f}(\omega-a)-\widehat{f}(\omega+a)}{2i}$ This follows from 101 and 103 using Euler's formula:
- Context after: . Square-integrable functions, one-dimensional. The Fourier transforms in this table may be found in , , or . Function Fourier transform unitary, ordinary frequency Fourier transform unitary, angular frequency Fourier transform non-unitary, angular frequency Remarks $f(x)$…
- Translator read: `sin(a*x)`  =  `(e^iax - 1/e**(a*i*x))/(2*i)`  · notes: superscript_label:e^iax
hint:e_only_as_exp_base
hint:i_present
sides: \sin(a x)  ||  \tfrac{e^{i a x} - e^{-i a x} }{2i}
- Assumptions: domains {'a': 'real', 'e^iax': 'positive', 'x': 'real'}; constants {'e': 'E', 'i': 'I'}; constraints []
- Verifier: The identity fails at 60 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at a=0.335369, e^iax=0.141501, x=0.0433968: lhs=0.014553427628, rhs=(0.00727671381).
- Counterexample: {'a': '0.335369', 'e^iax': '0.141501', 'x': '0.0433968'} → lhs 0.01455342762876183820348193034005251120, rhs (0.0072767138143809191017409651700262556, rel diff 1.0000000000
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:52247:1377137736:613

- Page: [Fourier transform](https://en.wikipedia.org/wiki/Fourier_transform) › Tables of important Fourier transforms > Distributions, one-dimensional  · verdict **FAIL**, symbolic unknown
- LaTeX: `\cos(a x) = \tfrac{e^{i a x} + e^{-i a x} }{2}`
- Context before: …ga - a)$ $2 \pi\delta(\omega - a)$ This follows from 103 and 301. 304 $\cos (a x)$ $\frac{ \delta{\left(\xi - \frac{a}{2\pi}\right)} + \delta{\left(\xi+\frac{a}{2\pi}\right)}}{2}$ $\sqrt{2 \pi}\,\frac{\delta(\omega-a)+\delta(\omega+a)}{2}$ $\pi\left(\delta(\omega-a)+\delta(\omega+a)\right)$ This follows from rules 101 and 303 using Euler's formula:
- Context after: . 305 $\sin( ax)$ $\frac{\delta{\left(\xi-\frac{a}{2\pi}\right)} - \delta{\left(\xi+\frac{a}{2\pi}\right)}}{2i}$ $\sqrt{2 \pi}\,\frac{\delta(\omega-a)-\delta(\omega+a)}{2i}$ $i\pi\bigl(\delta(\omega+a)-\delta(\omega-a)\bigr)$ This follows from 101 and 303 using $\sin(a x) = \tfrac{e^{i a x} - e^{-i a x} }{2i}$ . 306 $\cos \left( a x^2 \right)$…
- Translator read: `cos(a*x)`  =  `e^iax/2 + 1/(2*e**(a*i*x))`  · notes: superscript_label:e^iax
hint:e_only_as_exp_base
hint:i_present
sides: \cos(a x)  ||  \tfrac{e^{i a x} + e^{-i a x} }{2}
- Assumptions: domains {'a': 'real', 'e^iax': 'positive', 'x': 'real'}; constants {'e': 'E', 'i': 'I'}; constraints []
- Verifier: The identity fails at 60 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at a=0.0958692, e^iax=0.247371, x=0.217557: lhs=0.999782500336, rhs=(0.62357675016).
- Counterexample: {'a': '0.0958692', 'e^iax': '0.247371', 'x': '0.217557'} → lhs 0.99978250033609828488105840005275227456, rhs (0.6235767501680491424405292000263761372, rel diff 0.3764321156
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err
