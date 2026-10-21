# Review batch 008 — 22 items

For each item answer with one JSON line (Finding schema): {"formula_id": ..., "verdict": "FAIL", "review": {"status": "confirmed_error"|"false_positive"|"ambiguous", "reviewer": "<name>", "notes": "<why, one or two sentences>"}, "suggested_fix": "<corrected LaTeX or null>", "evidence": "<independent source or derivation>"}


---
## wiki:en:18814960:1376246270:39

- Page: [List of mathematical series](https://en.wikipedia.org/wiki/List_of_mathematical_series) › Power series > Low-order polylogarithms  · verdict **FAIL**, symbolic unknown
- LaTeX: `\begin{align}
\text{Ti}_{2}(x) &= \sum_{n = 0}^{\infty} \frac{(-1)^{n}}{(2n + 1)^2} x^{2n + 1} \\
\text{Ti}_{3}(x) &= \sum_{n = 0}^{\infty} \frac{(-1)^{n}}{(2n + 1)^3} x^{2n + 1}
\end{align}`
- Context before: …um_{k=1}^\infty k^4 z^k =\frac{z(1+z)(1+10z+z^2)}{(1-z)^5}$ The Legendre chi functions are defined as follows: $\begin{align} \chi_{2}(x) &= \sum_{n = 0}^{\infty} \frac{1}{(2n + 1)^2} x^{2n + 1} \\ \chi_{3}(x) &= \sum_{n = 0}^{\infty} \frac{1}{(2n + 1)^3} x^{2n + 1} \end{align}$ And the formulas presented below are called inverse tangent integrals:
- Context after: Exponential function. $\sum_{k=0}^\infty \frac{z^k}{k!} = e^z$ $\sum_{k=0}^\infty k\frac{z^k}{k!} = z e^z$ (cf. mean of Poisson distribution) $\sum_{k=0}^\infty k^2 \frac{z^k}{k!} = (z + z^2) e^z$ (cf. second moment of Poisson distribution) $\sum_{k=0}^\infty k^3 \frac{z^k}{k!} = (z + 3z^2 + z^3) e^z$ $\sum_{k=0}^\infty k^4 \frac{z^k}{k!} = (z + 7z…
- Translator read (piece 0): `Ti_2*x`  =  `Sum((-1)**n*x**(2*n + 1)/(2*n + 1)**2, (n, 0, oo))`  · notes: pre:env_align
pre:rows=2
text_symbol:Ti
sides: \text{Ti}_{2}(x)  ||  \sum_{n = 0}^{\infty} \frac{(-1)^{n}}{(2n + 1)^2} x^{2n + 1}
- Translator read (piece 1): `Ti_3*x`  =  `Sum((-1)**n*x**(2*n + 1)/(2*n + 1)**3, (n, 0, oo))`  · notes: pre:env_align
pre:rows=2
text_symbol:Ti
sides: \text{Ti}_{3}(x)  ||  \sum_{n = 0}^{\infty} \frac{(-1)^{n}}{(2n + 1)^3} x^{2n + 1}
- Assumptions: domains {'Ti_2': 'positive', 'Ti_3': 'positive', 'x': 'real'}; constants {}; constraints []
- Verifier: Chain link 0: The identity fails at 23 of 24 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign) (e.g. at Ti_2=0.202675, x=0.430006: lhs=0.087151466050, rhs=0.421709642114).
- Counterexample: {'Ti_2': '0.202675', 'x': '0.430006'} → lhs 0.08715146605000000000000000000000000000, rhs 0.42170964211435937947499607420624365010, rel diff 0.7933377439
- Regimes: small_positive 6/13 fail, 7 err, unit_interval 6/6 fail, 0 err, integers_small 5/20 fail, 14 err, mixed_sign 6/23 fail, 17 err, large 0/40 fail, 40 err

---
## wiki:en:18814960:1376246270:59

- Page: [List of mathematical series](https://en.wikipedia.org/wiki/List_of_mathematical_series) › Power series > Trigonometric, inverse trigonometric, hyperbolic, and inverse hyperbolic functions relationship  · verdict **FAIL**, symbolic unknown
- LaTeX: `\sum_{k=1}^\infty \frac{(-1)^{k-1} z^{2k}}{(2k)!}=\operatorname{ver}z`
- Context before: …$\sum_{k=0}^\infty \frac{(-1)^{k-1}(2^{2k}-2)B_{2k}z^{2k-1}}{(2k)!}=\csc z, |z|<\pi$ $\sum_{k=0}^\infty \frac{-(2^{2k}-2)B_{2k}z^{2k-1}}{(2k)!}=\operatorname{csch} z, |z|<\pi$ $\sum_{k=0}^\infty \frac{(-1)^kE_{2k}z^{2k}}{(2k)!}=\operatorname{sech} z, |z|<\frac{\pi}{2}$ $\sum_{k=0}^\infty \frac{E_{2k}z^{2k}}{(2k)!}=\sec z, |z| < \frac{\pi}{2}$
- Context after: (versine) $\sum_{k=1}^\infty \frac{(-1)^{k-1} z^{2k}}{2(2k)!}=\operatorname{hav}z$ (haversine) $\sum_{k=0}^\infty \frac{(2k)!z^{2k+1}}{2^{2k}(k!)^2(2k+1)}=\arcsin z, |z|\le1$ $\sum_{k=0}^\infty \frac{(-1)^k(2k)!z^{2k+1}}{2^{2k}(k!)^2(2k+1)}=\operatorname{arcsinh} {z}, |z| \le 1$ $\sum_{k=0}^\infty \frac{(-1)^kz^{2k+1}}{2k+1}=\arctan z, |z|<1$…
- Translator read: `Sum((-1)**(k - 1)*z**(2*k)/factorial(2*k), (k, 1, oo))`  =  `ver*z`  · notes: sides: \sum_{k=1}^\infty \frac{(-1)^{k-1} z^{2k}}{(2k)!}  ||  \operatorname{ver}z
- Assumptions: domains {'ver': 'positive', 'z': 'complex'}; constants {}; constraints ['Abs(z) < pi/2', 'Abs(z) < 1']
- Verifier: The identity fails at 20 of 22 evaluable points, a clear majority in every regime (small_positive, unit_interval) (e.g. at ver=0.0977641, z=0.104498: lhs=0.005454949363, rhs=0.010216152921).
- Counterexample: {'ver': '0.0977641', 'z': '0.104498'} → lhs 0.00545494936300950810533567709636943492, rhs 0.01021615292180000000000000000000000000, rel diff 0.4660466219
- Regimes: small_positive 6/6 fail, 0 err, unit_interval 6/6 fail, 0 err, integers_small 0/2 fail, 0 err, mixed_sign 4/4 fail, 0 err, complex 4/4 fail, 0 err, large 0/0 fail, 0 err

---
## wiki:en:25804104:1379178075:371

- Page: [List of trigonometric identities](https://en.wikipedia.org/wiki/List_of_trigonometric_identities) › Product-to-sum and sum-to-product identities > Sum-to-product identities  · verdict **FAIL**, symbolic unknown
- LaTeX: `\sin \theta + \sin \varphi = 2 \sin \tfrac12 (\theta + \varphi)\, \cos\tfrac12(\theta - \varphi)`
- Context before: …Sum-to-product identities. [caption]
- Context after: The sum of sines or cosines of two angles can be converted to a product of sines or cosines of the mean and half the difference of the angles:…
- Translator read: `sin(phi) + sin(theta)`  =  `2*(-phi + theta)*(phi + theta)*sin(1/2)*cos(1/2)`  · notes: pre:spacing
sides: \sin \theta + \sin \varphi  ||  2 \sin \tfrac12 (\theta + \varphi)\, \cos\tfrac12(\theta - \varphi)
- Assumptions: domains {'phi': 'angle', 'theta': 'angle'}; constants {}; constraints []
- Verifier: The identity fails at 60 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at phi=0.252685, theta=0.278602: lhs=0.525016417629, rhs=0.011586521277).
- Counterexample: {'phi': '0.252685', 'theta': '0.278602'} → lhs 0.52501641762986158286945172216373370621, rhs 0.01158652127735268816293670732067289755, rel diff 0.9779311257
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:25804104:1379178075:403

- Page: [List of trigonometric identities](https://en.wikipedia.org/wiki/List_of_trigonometric_identities) › Lagrange's trigonometric identities  · verdict **FAIL**, symbolic unknown
- LaTeX: `\sum_{k=1}^n \cos (2k -1)\alpha = \frac{\sin (2n \alpha)}{2 \sin \alpha}.`
- Context before: …for $\theta \not\equiv 0 \pmod{2\pi}.$ A related function is the Dirichlet kernel: $D_n(\theta) = 1 + 2\sum_{k=1}^n \cos k\theta = \frac{\sin\left(\left(n + \tfrac12 \right)\theta\right)}{\sin \tfrac12 \theta}.$ A similar identity is
- Context after: The proof is the following. By using the angle sum and difference identities, $\sin (A + B) - \sin (A - B) = 2 \cos A \sin B.$ Then let's examine the following formula, $2 \sin \alpha \sum_{k=1}^n \cos (2k - 1)\alpha = 2\sin \alpha \cos \alpha + 2 \sin \alpha \cos 3\alpha + 2 \sin \alpha \cos 5 \alpha + \cdots + 2 \sin \alpha \cos (2n - 1) \alpha$…
- Translator read: `Sum(alpha*cos(2*k - 1), (k, 1, n))`  =  `sin(2*alpha*n)/(2*sin(alpha))`  · notes: pre:trailing_punct
sides: \sum_{k=1}^n \cos (2k -1)\alpha  ||  \frac{\sin (2n \alpha)}{2 \sin \alpha}
- Assumptions: domains {'alpha': 'angle', 'n': 'nonneg_integer'}; constants {}; constraints ['Ne(sin(alpha), 0)']
- Verifier: The identity fails at 54 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at alpha=-0.842326, n=1: lhs=-0.45511068009, rhs=0.665728981927).
- Counterexample: {'alpha': '-0.842326', 'n': '1'} → lhs -0.4551106800926866555994613288010127107, rhs 0.66572898192781807689677675895217581604, rel diff 1.6836275608
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 9/12 fail, 0 err, integers_small 10/12 fail, 0 err, mixed_sign 11/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:25804104:1379178075:426

- Page: [List of trigonometric identities](https://en.wikipedia.org/wiki/List_of_trigonometric_identities) › Relation to the complex exponential function  · verdict **FAIL**, symbolic unknown
- LaTeX: `\arccos x = -i\ln\left(x+\sqrt{x^2-1}\right)`
- Context before: …on formula for sine. The following table expresses the trigonometric functions and their inverses in terms of the exponential function and the complex logarithm. Function Inverse function $\sin \theta = \frac{e^{i\theta} - e^{-i\theta}}{2i}$ $\arcsin x = -i\, \ln \left(ix + \sqrt{1 - x^2}\right)$ $\cos \theta = \frac{e^{i\theta} + e^{-i\theta}}{2}$
- Context after: $\tan \theta = -i\, \frac{e^{i\theta} - e^{-i\theta}}{e^{i\theta} + e^{-i\theta}}$ $\arctan x = \frac{i}{2} \ln \left(\frac{i + x}{i - x}\right)$ $\csc \theta = \frac{2i}{e^{i\theta} - e^{-i\theta}}$ $\arccsc x = -i\, \ln \left(\frac{i}{x} + \sqrt{1 - \frac{1}{x^2}}\right)$ $\sec \theta = \frac{2}{e^{i\theta} + e^{-i\theta}}$…
- Translator read: `acos(x)`  =  `-i*log(x + sqrt(x**2 - 1))`  · notes: pre:left_right
hint:i_present
sides: \arccos x  ||  -i\ln\left(x+\sqrt{x^2-1}\right)
- Assumptions: domains {'x': 'real'}; constants {'i': 'I'}; constraints ['((x) >= -1) & ((x) <= 1)', 'x**2 - 1 >= 0', 'x + sqrt(x**2 - 1) > 0']
- Verifier: The identity fails at 47 of 48 evaluable points, a clear majority in every regime (small_positive, integers_small, mixed_sign, large) (e.g. at x=1.03887: lhs=(0.0 + 0.27792, rhs=(0.0 - 0.27792).
- Counterexample: {'x': '1.03887'} → lhs (0.0 + 0.2779236051168544147479180985605, rhs (0.0 - 0.2779236051168544147479180985605, rel diff 2.0000000000
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 0/0 fail, 0 err, integers_small 11/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:25804104:1379178075:435

- Page: [List of trigonometric identities](https://en.wikipedia.org/wiki/List_of_trigonometric_identities) › Relation to the complex exponential function  · verdict **FAIL**, symbolic unknown
- LaTeX: `\operatorname{cis} \theta = e^{i\theta}`
- Context before: …$\arccsc x = -i\, \ln \left(\frac{i}{x} + \sqrt{1 - \frac{1}{x^2}}\right)$ $\sec \theta = \frac{2}{e^{i\theta} + e^{-i\theta}}$ $\arcsec x = -i\, \ln \left(\frac{1}{x} +i \sqrt{1 - \frac{1}{x^2}}\right)$ $\cot \theta = i\, \frac{e^{i\theta} + e^{-i\theta}}{e^{i\theta} - e^{-i\theta}}$ $\arccot x = \frac{i}{2} \ln \left(\frac{x - i}{x + i}\right)$
- Context after: $\operatorname{arccis} x = -i \ln x$ Relation to complex hyperbolic functions. Trigonometric functions may be deduced from hyperbolic functions with complex arguments. The formulae for the relations are shown below.…
- Translator read: `cis*theta`  =  `e**(i*theta)`  · notes: hint:e_only_as_exp_base
hint:i_present
sides: \operatorname{cis} \theta  ||  e^{i\theta}
- Assumptions: domains {'cis': 'positive', 'theta': 'real'}; constants {'e': 'E', 'i': 'I'}; constraints []
- Verifier: The identity fails at 60 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at cis=0.102962, theta=0.102136: lhs=0.010516126832, rhs=(0.99478865141).
- Counterexample: {'cis': '0.102962', 'theta': '0.102136'} → lhs 0.01051612683200000000000000000000000000, rhs (0.9947886514118233723083118843302242154, rel diff 0.9895392572
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:25804104:1379178075:436

- Page: [List of trigonometric identities](https://en.wikipedia.org/wiki/List_of_trigonometric_identities) › Relation to the complex exponential function  · verdict **FAIL**, symbolic unknown
- LaTeX: `\operatorname{arccis} x = -i \ln x`
- Context before: …+ \sqrt{1 - \frac{1}{x^2}}\right)$ $\sec \theta = \frac{2}{e^{i\theta} + e^{-i\theta}}$ $\arcsec x = -i\, \ln \left(\frac{1}{x} +i \sqrt{1 - \frac{1}{x^2}}\right)$ $\cot \theta = i\, \frac{e^{i\theta} + e^{-i\theta}}{e^{i\theta} - e^{-i\theta}}$ $\arccot x = \frac{i}{2} \ln \left(\frac{x - i}{x + i}\right)$ $\operatorname{cis} \theta = e^{i\theta}$
- Context after: Relation to complex hyperbolic functions. Trigonometric functions may be deduced from hyperbolic functions with complex arguments. The formulae for the relations are shown below. $\begin{align} \sin x &= -i \sinh (ix) \\ \cos x &= \cosh (ix) \\ \tan x &= -i \tanh (i x) \\ \cot x &= i \coth (i x) \\ \sec x &= \operatorname{sech} (i x) \\ \csc x &= i…
- Translator read: `arccis*x`  =  `-i*log(x)`  · notes: hint:i_present
sides: \operatorname{arccis} x  ||  -i \ln x
- Assumptions: domains {'arccis': 'positive', 'x': 'positive'}; constants {'i': 'I'}; constraints []
- Verifier: The identity fails at 60 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at arccis=0.0906527, x=0.130221: lhs=0.011804885246, rhs=(0.0 + 2.03852).
- Counterexample: {'arccis': '0.0906527', 'x': '0.130221'} → lhs 0.01180488524670000000000000000000000000, rhs (0.0 + 2.0385222718909731546189036933010, rel diff 1.0000167671
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:25804104:1379178075:511

- Page: [List of trigonometric identities](https://en.wikipedia.org/wiki/List_of_trigonometric_identities) › Miscellaneous > Sum of Sines and Cosines of Arithmetic Sequences > Sine formulation 1:  · verdict **FAIL**, symbolic unknown
- LaTeX: `\begin{align}
    \sum_{k=0}^n \cos (a + kd) = \frac{\sin (d(n+1)/2)}{\sin(d/2)}\sin\Big(a + \frac{nd}{2} \Big).
\end{align}`
- Context before: …(When k = 0, then the number of differential operators being composed is 0, so the corresponding term in the sum above is just (sin x)n.) Sum of Sines and Cosines of Arithmetic Sequences. Let $d \in \mathbb{R}$ be a real number such that $d \neq 2\pi k$ for $k \in \mathbb{Z}$ . Then: Sine formulation 1:.
- Context after: Sine formulation 2:. $\begin{align} \sum_{k=1}^n \cos (a + kd) = \frac{\sin (nd/2)}{\sin(d/2)}\sin\Big(a + \frac{n+1}{2}d \Big). \end{align}$ Cosine formulation 1:. $\begin{align} \sum_{k=0}^n \cos (a + kd) = \frac{\sin (d(n+1)/2)}{\sin(d/2)}\cos\Big(a + \frac{nd}{2} \Big). \end{align}$ Cosine formulation 2:.…
- Translator read: `Sum(cos(a + d*k), (k, 0, n))`  =  `sin(d*(n + 1)/2)*sin(a + d*n/2)/sin(d/2)`  · notes: pre:size
pre:env_align
pre:trailing_punct
sides: \sum_{k=0}^n \cos (a + kd)  ||  \frac{\sin (d(n+1)/2)}{\sin(d/2)}\sin\Big(a + \frac{nd}{2} \Big)
- Assumptions: domains {'a': 'real', 'd': 'positive', 'n': 'nonneg_integer'}; constants {}; constraints ['Ne(d, 2*pi)', 'Ne(sin(d/2), 0)']
- Verifier: The identity fails at 60 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at a=0.0970472, d=0.334964, n=0: lhs=0.995294615230, rhs=0.096894937392).
- Counterexample: {'a': '0.0970472', 'd': '0.334964', 'n': '0'} → lhs 0.99529461523096582734230406352559582375, rhs 0.09689493739222749784739724993664064317, rel diff 0.9026469791
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:25804104:1379178075:512

- Page: [List of trigonometric identities](https://en.wikipedia.org/wiki/List_of_trigonometric_identities) › Miscellaneous > Sum of Sines and Cosines of Arithmetic Sequences > Sine formulation 2:  · verdict **FAIL**, symbolic unknown
- LaTeX: `\begin{align}
    \sum_{k=1}^n \cos (a + kd) = \frac{\sin (nd/2)}{\sin(d/2)}\sin\Big(a + \frac{n+1}{2}d \Big).
\end{align}`
- Context before: …rm in the sum above is just (sin x)n.) Sum of Sines and Cosines of Arithmetic Sequences. Let $d \in \mathbb{R}$ be a real number such that $d \neq 2\pi k$ for $k \in \mathbb{Z}$ . Then: Sine formulation 1:. $\begin{align} \sum_{k=0}^n \cos (a + kd) = \frac{\sin (d(n+1)/2)}{\sin(d/2)}\sin\Big(a + \frac{nd}{2} \Big). \end{align}$ Sine formulation 2:.
- Context after: Cosine formulation 1:. $\begin{align} \sum_{k=0}^n \cos (a + kd) = \frac{\sin (d(n+1)/2)}{\sin(d/2)}\cos\Big(a + \frac{nd}{2} \Big). \end{align}$ Cosine formulation 2:. $\begin{align} \sum_{k=1}^n \cos (a + kd) = \frac{\sin (nd/2)}{\sin(d/2)}\cos\Big(a + \frac{n+1}{2}d \Big). \end{align}$ See also. Aristarchus's inequality Derivatives of trigonomet…
- Translator read: `Sum(cos(a + d*k), (k, 1, n))`  =  `sin(d*n/2)*sin(a + d*(n/2 + 1/2))/sin(d/2)`  · notes: pre:size
pre:env_align
pre:trailing_punct
sides: \sum_{k=1}^n \cos (a + kd)  ||  \frac{\sin (nd/2)}{\sin(d/2)}\sin\Big(a + \frac{n+1}{2}d \Big)
- Assumptions: domains {'a': 'real', 'd': 'positive', 'n': 'nonneg_integer'}; constants {}; constraints ['Ne(d, 2*pi)', 'Ne(sin(d/2), 0)']
- Verifier: The identity fails at 57 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at a=0.963517, d=0.737204, n=1: lhs=-0.12955945107, rhs=0.991571655826).
- Counterexample: {'a': '0.963517', 'd': '0.737204', 'n': '1'} → lhs -0.1295594510725901055777455841681384192, rhs 0.99157165582612794375353225769486915254, rel diff 1.1306607044
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 11/12 fail, 0 err, integers_small 11/12 fail, 0 err, mixed_sign 11/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:17829294:1381187812:23

- Page: [Liu Hui's π algorithm](https://en.wikipedia.org/wiki/Liu_Hui's_%CF%80_algorithm) › Iterative algorithm  · verdict **FAIL**, symbolic not_equal
- LaTeX: `{}314\frac{64}{625}<100 \times \pi <314 \frac{64}{625} +\frac{105}{625}`
- Context before: …. With $r = 10$ units, he obtained area of 96-gon ${}A_{96} = 313 {584 \over 625}$ area of 192-gon ${}A_{192} = 314 {64 \over 625}$ Difference of 96-gon and 48-gon: ${}D_{192} = 314\frac{64}{625} - 313\frac{584}{625} = \frac{105}{625}$ from Liu Hui's π inequality: $A_{2N} < A_{C} < A_{2N} + D_{2N}.$ Since r = 10, $A_{C} = 100 \times \pi$ therefore:
- Context after: ${}314\frac{64}{625}<100 \times \pi <314 \frac{169}{625}$ ${} 3.141024 < \pi < 3.142704.$ He never took π as the average of the lower limit 3.141024 and upper limit 3.142704. Instead he suggested that 3.14 was a good enough approximation for π, and expressed it as a fraction $\tfrac{157}{50}$ ; he pointed out this number is slightly less than the a…
- Translator read (piece 0): `20096/625`  <  `100*pi`  · notes: op:times
sides: 314\frac{64}{625}  ||  100 \times \pi
- Translator read (piece 1): `100*pi`  <  `20201/625`  · notes: op:times
sides: 100 \times \pi  ||  314 \frac{64}{625} +\frac{105}{625}
- Assumptions: domains {}; constants {}; constraints []
- Verifier: Chain link 1: The constant inequality does not hold: both sides differ beyond 1e-8 relative error, stably at two working precisions (lhs=314.15926535897932, rhs=32.321600000000000).
- Counterexample: {} → lhs 314.159265358979323846264338327950288419, rhs 32.3216000000000000000000000000000000000, rel diff 0.8971171518
- Regimes: constant 1/1 fail, 0 err

---
## wiki:en:17829294:1381187812:24

- Page: [Liu Hui's π algorithm](https://en.wikipedia.org/wiki/Liu_Hui's_%CF%80_algorithm) › Iterative algorithm  · verdict **FAIL**, symbolic not_equal
- LaTeX: `{}314\frac{64}{625}<100 \times \pi <314 \frac{169}{625}`
- Context before: …er 625}$ area of 192-gon ${}A_{192} = 314 {64 \over 625}$ Difference of 96-gon and 48-gon: ${}D_{192} = 314\frac{64}{625} - 313\frac{584}{625} = \frac{105}{625}$ from Liu Hui's π inequality: $A_{2N} < A_{C} < A_{2N} + D_{2N}.$ Since r = 10, $A_{C} = 100 \times \pi$ therefore: ${}314\frac{64}{625}<100 \times \pi <314 \frac{64}{625} +\frac{105}{625}$
- Context after: ${} 3.141024 < \pi < 3.142704.$ He never took π as the average of the lower limit 3.141024 and upper limit 3.142704. Instead he suggested that 3.14 was a good enough approximation for π, and expressed it as a fraction $\tfrac{157}{50}$ ; he pointed out this number is slightly less than the actual value of π. Liu Hui carried out his calculation with…
- Translator read (piece 0): `20096/625`  <  `100*pi`  · notes: op:times
sides: 314\frac{64}{625}  ||  100 \times \pi
- Translator read (piece 1): `100*pi`  <  `53066/625`  · notes: op:times
sides: 100 \times \pi  ||  314 \frac{169}{625}
- Assumptions: domains {}; constants {}; constraints []
- Verifier: Chain link 1: The constant inequality does not hold: both sides differ beyond 1e-8 relative error, stably at two working precisions (lhs=314.15926535897932, rhs=84.905600000000000).
- Counterexample: {} → lhs 314.159265358979323846264338327950288419, rhs 84.9056000000000000000000000000000000000, rel diff 0.7297370812
- Regimes: constant 1/1 fail, 0 err

---
## wiki:en:17829294:1381187812:36

- Page: [Liu Hui's π algorithm](https://en.wikipedia.org/wiki/Liu_Hui's_%CF%80_algorithm) › Quick method  · verdict **FAIL**, symbolic not_equal
- LaTeX: `\pi = {3927 \over 1250}.`
- Context before: …3) and one more addition, instead of four more square root extractions. Why he preferred to calculate π through calculation of areas instead of circumferences of successive polygons, because the quick method required information about the difference in areas of successive polygons. Who was the true author of the paragraph containing calculation of
- Context after: That famous paragraph began with "A Han dynasty bronze container in the military warehouse of Jin dynasty....". Many scholars, among them Yoshio Mikami and Joseph Needham, believed that the "Han dynasty bronze container" paragraph was the work of Liu Hui and not Zu Chongzhi as other believed, because of the strong correlation of the two methods thr…
- Translator read: `pi`  =  `3927/1250`  · notes: pre:over_choose
pre:trailing_punct
sides: \pi  ||  {\frac{3927 }{ 1250}}
- Assumptions: domains {}; constants {}; constraints []
- Verifier: The constant identity does not hold: both sides differ beyond 1e-8 relative error, stably at two working precisions (lhs=3.1415926535897932, rhs=3.1416000000000000).
- Counterexample: {} → lhs 3.14159265358979323846264338327950288419, rhs 3.14160000000000000000000000000000000000, rel diff 0.0000023384
- Regimes: constant 1/1 fail, 0 err

---
## wiki:en:84563:1380195892:26

- Page: [Logistic function](https://en.wikipedia.org/wiki/Logistic_function) › Mathematical properties > Inverse function  · verdict **FAIL**, symbolic unknown
- LaTeX: `\operatorname{logit} p = \log \frac p {1-p} \quad \text{ for }\, 0<p<1`
- Context before: …he sum of the logistic function and its reflection about the vertical axis, $f(-x)$ , is $\frac{1}{1 + e^{-x}} + \frac{1}{1 + e^{-(-x)}} = \frac{e^x}{e^x + 1} + \frac{1}{e^x + 1} = 1.$ The logistic function is thus rotationally symmetrical about the point (0, 1/2). Inverse function. The logistic function is the inverse of the natural logit function
- Context after: and so converts the logarithm of odds into a probability. The conversion from the log-likelihood ratio of two alternatives also takes the form of a logistic curve. Hyperbolic tangent. The logistic function is an offset and scaled hyperbolic tangent function: $f(x) = \frac12 + \frac12 \tanh\left(\frac{x}{2}\right),$ or $\tanh(x) = 2 f(2x) - 1.$ This…
- Translator read: `logit*p`  =  `log(p/(1 - p))`  · notes: pre:spacing
log:unspecified_base
cond: 0<p<1
sides: \operatorname{logit} p  ||  \log \frac p {1-p}
- Assumptions: domains {'logit': 'positive', 'p': 'unit_interval'}; constants {}; constraints ['0 < p', 'p < 1', 'Ne(1 - p, 0)', 'p/(1 - p) > 0']
- Verifier: The identity fails at 48 of 48 evaluable points, a clear majority in every regime (small_positive, unit_interval, mixed_sign, large) (e.g. at logit=0.213914, p=0.136188: lhs=0.029132519832, rhs=-1.84731886842).
- Counterexample: {'logit': '0.213914', 'p': '0.136188'} → lhs 0.02913251983200000000000000000000000000, rhs -1.8473188684277580082403697669369758141, rel diff 1.0157701630
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 0/0 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:72773869:1339494963:68

- Page: [Madhava's correction term](https://en.wikipedia.org/wiki/Madhava's_correction_term) › Speculative derivation by Hayashi et al.  · verdict **FAIL**, symbolic not_equal
- LaTeX: `\pi=355/113,`
- Context before: …ingenious method by which Madhava might have obtained the three correction terms. Their proposal was based on two assumptions: Madhava used $355/113$ as the value of π and he used the Euclidean algorithm for division. Writing $S(n) = \left| 1 - \frac{1}{3} +\frac{1}{5}-\frac{1}{7}+ \cdots +\frac{(-1)^{n-1}}{2n-1} - \frac{\pi}{4}\right|$ and taking
- Context after: compute the values $S(n),$ express them as a fraction with 1 as numerator, and finally ignore the fractional parts in the denominator to obtain approximations:…
- Translator read: `pi`  =  `355/113`  · notes: pre:trailing_punct
sides: \pi  ||  355/113
- Assumptions: domains {}; constants {}; constraints []
- Verifier: The constant identity does not hold: both sides differ beyond 1e-8 relative error, stably at two working precisions (lhs=3.1415926535897932, rhs=3.1415929203539823).
- Counterexample: {} → lhs 3.14159265358979323846264338327950288419, rhs 3.14159292035398230088495575221238938053, rel diff 0.0000000849
- Regimes: constant 1/1 fail, 0 err

---
## wiki:en:274536:1367169495:110

- Page: [Martingale (probability theory)](https://en.wikipedia.org/wiki/Martingale_(probability_theory)) › Submartingales, supermartingales, and relationship to harmonic functions  · verdict **FAIL**, symbolic not_equal
- LaTeX: `\Delta f \le 0`
- Context before: …ends to increase in future time. Supermartingales: Analogously, a discrete-time supermartingale satisfies: $\mathbf{E}[X_{n+1} \mid X_1,\ldots,X_n] \le X_n.$ Likewise, a continuous-time supermartingale satisfies: $\mathbf{E}[X_t \mid \{X_\tau : \tau \le s\}] \le X_s \quad \forall s \le t.$ In potential theory, a superharmonic function $f$ satisfies
- Context after: . Roughly speaking, the prefix "super-" is consistent because the current observation $X_n$ is greater than (or equal to) the conditional expectation. Consequently, the process tends to decrease in future time. Examples of submartingales and supermartingales. Every martingale is also a submartingale and a supermartingale. Conversely, any stochastic…
- Translator read: `Delta*f`  <=  `0`  · notes: sides: \Delta f  ||  0
- Assumptions: domains {'Delta': 'positive', 'f': 'positive'}; constants {}; constraints []
- Verifier: The inequality fails at 60 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at Delta=0.154447, f=0.210057: lhs=0.032442673479, rhs=0).
- Counterexample: {'Delta': '0.154447', 'f': '0.210057'} → lhs 0.03244267347900000000000000000000000000, rhs 0, rel diff 1.0000000000
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:18881:1381140818:58

- Page: [Mathematical induction](https://en.wikipedia.org/wiki/Mathematical_induction) › Examples > A trigonometric inequality  · verdict **FAIL**, symbolic unknown
- LaTeX: `\begin{align} 
\left|\sin(k+1)x\right|
&= \left|\sin kx \cos x+\sin x \cos kx\right| && \text{(angle addition)}
\\ 
&\leq \left|\sin kx \cos x\right| + \left|\sin x\,\cos kx\right| && \text{(triangle inequality)}
\\ 
&= \left|\sin kx\right|\left| \cos x\right| + \left|\sin x\right|\left|\cos kx\right| 
\\ 
&\leq \left|\sin kx\right| + \left|\sin x\right| && (\left|\cos t\right| \leq 1)
\\ 
&\leq
k\left|\sin x\right|+\left|\sin x\right| && \text{(induction hypothesis})\\ 
&= (k+1)\left|\sin x\right|.
\end{align}`
- Context before: …lculation $\left|\sin 0x\right| = 0 \leq 0 = 0 \left|\sin x\right|$ verifies $P(0)$ . Induction step: We show the implication $P(k) \implies P(k+1)$ for any natural number $k$ . Assume the induction hypothesis: for a given value $n = k \geq 0$ , the single case $P(k)$ is true. Using the angle addition formula and the triangle inequality, we deduce:
- Context after: The inequality between the extreme left-hand and right-hand quantities shows that $P(k+1)$ is true, which completes the induction step. Conclusion: The proposition $P(n)$ holds for all natural numbers $n.$ Q.E.D. Variants. In practice, proofs by induction are often structured differently, depending on the exact nature of the property to be proven.…
- Translator read: `Abs(x*sin(k + 1))`  =  `Abs(sin(x)*cos(k*x) + sin(k*x)*cos(x))`  · notes: pre:left_right
pre:spacing
pre:env_align
pre:align_column_separator
pre:row_continues_chain
implicit_function_arg
cond: \leq \left|\sin kx \cos x\right| + \left|\sin x\,\cos kx\right| && \text{(triangle inequality)} \\  &= \left|\sin kx\right|\left| \cos x\right| + \left|\sin x\right|\left|\cos kx\right|  \\  &\leq \left|\sin kx\right| + \left|\sin x\right| && (\left|\cos t\right| \leq 1) \\  &\leq k\left|\sin x\right|+\left|\sin x\right| && \text{(induction hypothesis})\\  &= (k+1)\left|\sin x\right|. \end{align}
sides: |\sin(k+1)x\right|  ||  |\sin kx \cos x+\sin x \cos kx\right|
- Assumptions: domains {'k': 'positive_integer', 'x': 'real'}; constants {}; constraints []
- Verifier: The identity fails at 59 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at k=1, x=0.167716: lhs=0.152503727237, rhs=0.329177124436).
- Counterexample: {'k': '1', 'x': '0.167716'} → lhs 0.15250372723749603122503886783125419803, rhs 0.32917712443686613193048326390618407013, rel diff 0.5367122563
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 11/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:10972761:1374708864:35

- Page: [Mathematics of cyclic redundancy checks](https://en.wikipedia.org/wiki/Mathematics_of_cyclic_redundancy_checks) › Formulation  · verdict **FAIL**, symbolic not_equal
- LaTeX: `-1=1`
- Context before: …e original message bit shifted left $n$ times. Thus appending the $n$ bits of R (possibly with leading zeros) to the message by just adding the polynomials. Writing $W(x)$ this way demonstrates that $W(x)\bmod\,G(x)=0$ as $M(x) \cdot x^n = Q(x) \cdot G(x) + R(x)$ $\Rightarrow$ $M(x) \cdot x^n - R(x) = Q(x) \cdot G(x)$ $\Rightarrow$ because in GF(2)
- Context after: $W(x) = M(x) \cdot x^n + R(x) = Q(x) \cdot G(x)$ The receiver, knowing $G(x)$ , divides $W(x)$ by $G(x)$ and checks that the remainder is zero. If it is, the receiver discards $R(x)$ (the last $n$ bits) and assumes the received message bits $M(x)$ are correct. Software implementations sometimes separate the message into its parts and compare the re…
- Translator read: `-1`  =  `1`  · notes: sides: -1  ||  1
- Assumptions: domains {}; constants {}; constraints []
- Verifier: The constant identity does not hold: both sides differ beyond 1e-8 relative error, stably at two working precisions (lhs=-1.000000000000000, rhs=1.0000000000000000).
- Counterexample: {} → lhs -1.0000000000000000000000000000000000000, rhs 1.00000000000000000000000000000000000000, rel diff 2.0000000000
- Regimes: constant 1/1 fail, 0 err

---
## wiki:en:672731:1380739424:17

- Page: [Matrix exponential](https://en.wikipedia.org/wiki/Matrix_exponential) › Properties > Elementary properties  · verdict **FAIL**, symbolic unknown
- LaTeX: `\int_0^\infty e^{-ts}e^{tX}\,dt = (sI - X)^{-1}`
- Context before: …of this identity include: Using the above results, we can easily verify the following claims: If X is symmetric then eX is also symmetric. If X is skew-symmetric then eX is orthogonal. If X is Hermitian then eX is also Hermitian. If X is skew-Hermitian then eX is unitary. Finally, a Laplace transform of matrix exponentials amounts to the resolvent,
- Context after: for all sufficiently large positive values of s. Linear differential equation systems. One of the reasons for the importance of the matrix exponential is that it can be used to solve systems of linear ordinary differential equations. The solution of $\frac{d}{dt} y(t) = Ay(t), \quad y(0) = y_0,$ where A is a constant matrix and y is a column vector…
- Translator read: `Integral(e**(X*t)/e**(s*t), (t, 0, oo))`  =  `1/(I*s - X)`  · notes: pre:spacing
hint:e_only_as_exp_base
sides: \int_0^\infty e^{-ts}e^{tX}\,dt  ||  (sI - X)^{-1}
- Assumptions: domains {'I': 'positive', 'X': 'positive', 's': 'complex'}; constants {'e': 'E'}; constraints ['Ne(I*s - X, 0)']
- Verifier: The identity fails at 35 of 36 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, complex, large) (e.g. at I=0.0898739, X=0.0881404, s=0.129675: lhs=24.07631227940, rhs=-13.0742877601).
- Counterexample: {'I': '0.0898739', 'X': '0.0881404', 's': '0.129675'} → lhs 24.0763122794007887399902731698391220813, rhs -13.074287760147274584928921958344010002, rel diff 1.5430353124
- Regimes: small_positive 6/11 fail, 5 err, unit_interval 6/16 fail, 10 err, integers_small 5/21 fail, 15 err, mixed_sign 6/32 fail, 26 err, complex 6/25 fail, 19 err, large 6/10 fail, 4 err

---
## wiki:en:672731:1380739424:96

- Page: [Matrix exponential](https://en.wikipedia.org/wiki/Matrix_exponential) › Computing the matrix exponential > Projection case  · verdict **FAIL**, symbolic unknown
- LaTeX: `e^P = \sum_{k=0}^{\infty} \frac{P^k}{k!} = I + \left(\sum_{k=1}^{\infty} \frac{1}{k!}\right)P = I + (e - 1)P ~.`
- Context before: …en given by $e^J = e^{\lambda_1} e^{N_{a_1}} \oplus e^{\lambda_2} e^{N_{a_2}} \oplus \cdots \oplus e^{\lambda_n} e^{N_{a_n}}$ Projection case. If P is a projection matrix (i.e. is idempotent: ), its matrix exponential is: . Deriving this by expansion of the exponential function, each power of P reduces to P which becomes a common factor of the sum:
- Context after: Rotation case. For a simple rotation in which the perpendicular unit vectors a and b specify a plane, the rotation matrix R can be expressed in terms of a similar exponential function involving a generator G and angle θ. $\begin{align} G &= \mathbf{ba}^\mathsf{T} - \mathbf{ab}^\mathsf{T} & P &= -G^2 = \mathbf{aa}^\mathsf{T} + \mathbf{bb}^\mathsf{T}…
- Translator read (piece 0): `e**P`  =  `Sum(P**k/factorial(k), (k, 0, oo))`  · notes: pre:left_right
pre:spacing
pre:trailing_punct
hint:e_only_as_exp_base
sides: e^P  ||  \sum_{k=0}^{\infty} \frac{P^k}{k!}
- Translator read (piece 1): `Sum(P**k/factorial(k), (k, 0, oo))`  =  `I + P*Sum(1/factorial(k), (k, 1, oo))`  · notes: pre:left_right
pre:spacing
pre:trailing_punct
sides: \sum_{k=0}^{\infty} \frac{P^k}{k!}  ||  I + \left(\sum_{k=1}^{\infty} \frac{1}{k!}\right)P
- Translator read (piece 2): `I + P*Sum(1/factorial(k), (k, 1, oo))`  =  `I + P*(e - 1)`  · notes: pre:left_right
pre:spacing
pre:trailing_punct
hint:e_not_only_exp_base
sides: I + \left(\sum_{k=1}^{\infty} \frac{1}{k!}\right)P  ||  I + (e - 1)P
- Assumptions: domains {'I': 'positive', 'P': 'positive'}; constants {'e': 'E'}; constraints []
- Verifier: Chain link 1: The identity fails at 30 of 30 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at I=0.0507541, P=0.0590813: lhs=1.060861485273, rhs=0.152272424191).
- Counterexample: {'I': '0.0507541', 'P': '0.0590813'} → lhs 1.06086148527302394361859715327269214021, rhs 0.15227242419173738926389175218122805882, rel diff 0.8564634249
- Regimes: small_positive 6/6 fail, 0 err, unit_interval 6/6 fail, 0 err, integers_small 6/6 fail, 0 err, mixed_sign 6/6 fail, 0 err, large 6/6 fail, 0 err

---
## wiki:en:387297:1378457791:296

- Page: [Mellin transform](https://en.wikipedia.org/wiki/Mellin_transform) › Table of selected Mellin transforms  · verdict **FAIL**, symbolic unknown
- LaTeX: `\operatorname{acot} x = \frac{\pi}{2} - \operatorname{atan} x`
- Context before: …Re a$ Binomial series $u(1-x)\;(1-x)^{a-1}$ $\frac{\Gamma(s)\,\Gamma(a)}{\Gamma(s+a)}$ $0 < \Re s < \infty$ $\Re a > 0$ $u(x-1)\;(1-x)^{-a}$ $\frac{\Gamma(a-s)\,\Gamma(1-a)}{\Gamma(1-s)}$ $-\infty < \Re s < \Re a$ $\Re a < 1$ $\ln(1+x)$ $\frac{\pi}{s\,\sin(\pi s)}$ $-1 < \Re s < 0$ $\ln \vert 1-x \vert$ $\frac{\pi}{s}\,\cot(\pi s)$ $-1 < \Re s < 0$
- Context after: $\frac{\pi}{2s\,\cos(\pi s/2)}$ $0 < \Re s < 1$ $\sin(x)$ $\sin(\tfrac{1}{2}\pi s) \, \Gamma(s)$ $-1 < \Re s < 1$ $\cos(x)$ $\cos(\tfrac{1}{2}\pi s) \, \Gamma(s)$ $0 < \Re s < 1$ $e^{ix}$ $e^{i\pi s/2} \, \Gamma(s)$ $0 < \Re s < 1$ $\dfrac{1}{e^x / z - 1}$ $\Gamma(s)\operatorname{Li}_s(z)$…
- Translator read: `acot*x`  =  `-atan(x) + pi/2`  · notes: sides: \operatorname{acot} x  ||  \frac{\pi}{2} - \operatorname{atan} x
- Assumptions: domains {'acot': 'positive', 'x': 'real'}; constants {}; constraints []
- Verifier: The identity fails at 60 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at acot=0.0249826, x=0.166663: lhs=0.004163675063, rhs=1.405651216949).
- Counterexample: {'acot': '0.0249826', 'x': '0.166663'} → lhs 0.00416367506380000000000000000000000000, rhs 1.40565121694995859103709795736606906066, rel diff 0.9970379031
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:19858:1380980634:205

- Page: [Model theory](https://en.wikipedia.org/wiki/Model_theory) › Stability theory > The stability hierarchy  · verdict **FAIL**, symbolic unknown
- LaTeX: `\lambda^{\aleph_0} = \lambda`
- Context before: …-stable are called $\omega$ -stable. The stability hierarchy. A fundamental result in stability theory is the stability spectrum theorem, which implies that every complete theory T in a countable signature falls in one of the following classes: There are no cardinals $\lambda$ such that T is $\lambda$ -stable. T is $\lambda$ -stable if and only if
- Context after: (see Cardinal exponentiation for an explanation of $\lambda^{\aleph_0}$ ). T is $\lambda$ -stable for any $\lambda \geq 2^{\aleph_0}$ (where $2^{\aleph_0}$ is the cardinality of the continuum). A theory of the first type is called unstable, a theory of the second type is called strictly stable and a theory of the third type is called superstable. F…
- Translator read: `lambda**aleph_0`  =  `lambda`  · notes: sides: \lambda^{\aleph_0}  ||  \lambda
- Assumptions: domains {'aleph_0': 'positive', 'lambda': 'positive'}; constants {}; constraints []
- Verifier: The identity fails at 58 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at aleph_0=0.137468, lambda=0.146048: lhs=0.767617528163, rhs=0.146048000000).
- Counterexample: {'aleph_0': '0.137468', 'lambda': '0.146048'} → lhs 0.76761752816320673327095804488385700052, rhs 0.14604800000000000000000000000000000000, rel diff 0.8097385812
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 10/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:21476:1380767706:89

- Page: [Natural logarithm](https://en.wikipedia.org/wiki/Natural_logarithm) › Efficient computation > High precision  · verdict **FAIL**, symbolic unknown
- LaTeX: `\mathrm{log1p}(x) = \log(1+x) = 2 ~ \mathrm{artanh}\left(\frac{x}{2+x}\right)\,,`
- Context before: …esented as floating-point numbers. In addition to base e, the IEEE 754-2008 standard defines similar logarithmic functions near 1 for binary and decimal logarithms: log2(1 + x) and log10(1 + x). Similar inverse functions named "expm1", "expm" or "exp1m" exist as well, all with the meaning of . An identity in terms of the inverse hyperbolic tangent,
- Context after: gives a high precision value for small values of x on systems that do not implement log1p(x). Computational complexity. The computational complexity of computing the natural logarithm using the arithmetic-geometric mean (for both of the above methods) is $\text{O}\bigl(M(n) \ln n \bigr)$ . Here, n is the number of digits of precision at which the n…
- Translator read (piece 0): `log1p*x`  =  `log(x + 1)`  · notes: pre:left_right
pre:spacing
pre:trailing_punct
roman_word:log1p
log:unspecified_base
sides: \mathrm{log1p}(x)  ||  \log(1+x)
- Translator read (piece 1): `log(x + 1)`  =  `2*atanh(x/(x + 2))`  · notes: pre:left_right
pre:spacing
pre:trailing_punct
roman_word:log1p
log:unspecified_base
sides: \log(1+x)  ||  2 ~ \mathrm{artanh}\left(\frac{x}{2+x}\right)
- Assumptions: domains {'log1p': 'positive', 'x': 'real'}; constants {}; constraints ['x + 1 > 0', 'Ne(x + 2, 0)', 'Abs(x/(x + 2)) < 1']
- Verifier: Chain link 0: The identity fails at 58 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at log1p=0.209063, x=0.027517: lhs=0.005752786571, rhs=0.027145212263).
- Counterexample: {'log1p': '0.209063', 'x': '0.027517'} → lhs 0.00575278657100000000000000000000000000, rhs 0.02714521226355086582848666668077107379, rel diff 0.7880736199
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 10/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err
