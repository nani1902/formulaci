# Review batch 005 — 22 items

For each item answer with one JSON line (Finding schema): {"formula_id": ..., "verdict": "FAIL", "review": {"status": "confirmed_error"|"false_positive"|"ambiguous", "reviewer": "<name>", "notes": "<why, one or two sentences>"}, "suggested_fix": "<corrected LaTeX or null>", "evidence": "<independent source or derivation>"}


---
## wiki:en:52247:1377137736:618

- Page: [Fourier transform](https://en.wikipedia.org/wiki/Fourier_transform) › Tables of important Fourier transforms > Distributions, one-dimensional  · verdict **FAIL**, symbolic unknown
- LaTeX: `\sin(a x) = \tfrac{e^{i a x} - e^{-i a x} }{2i}`
- Context before: …ules 101 and 303 using Euler's formula: $\cos(a x) = \tfrac{e^{i a x} + e^{-i a x} }{2}$ . 305 $\sin( ax)$ $\frac{\delta{\left(\xi-\frac{a}{2\pi}\right)} - \delta{\left(\xi+\frac{a}{2\pi}\right)}}{2i}$ $\sqrt{2 \pi}\,\frac{\delta(\omega-a)-\delta(\omega+a)}{2i}$ $i\pi\bigl(\delta(\omega+a)-\delta(\omega-a)\bigr)$ This follows from 101 and 303 using
- Context after: . 306 $\cos \left( a x^2 \right)$ $\sqrt{\frac{\pi}{a}} \cos \left( \frac{\pi^2 \xi^2}{a} - \frac{\pi}{4} \right)$ $\frac{1}{\sqrt{2 a}} \cos \left( \frac{\omega^2}{4 a} - \frac{\pi}{4} \right)$ $\sqrt{\frac{\pi}{a}} \cos \left( \frac{\omega^2}{4a} - \frac{\pi}{4} \right)$ This follows from 101 and 207 using $\cos(a x^2) = \tfrac{e^{i a x^2} + e^{-…
- Translator read: `sin(a*x)`  =  `(e^iax - 1/e**(a*i*x))/(2*i)`  · notes: superscript_label:e^iax
hint:e_only_as_exp_base
hint:i_present
sides: \sin(a x)  ||  \tfrac{e^{i a x} - e^{-i a x} }{2i}
- Assumptions: domains {'a': 'real', 'e^iax': 'positive', 'x': 'real'}; constants {'e': 'E', 'i': 'I'}; constraints []
- Verifier: The identity fails at 60 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at a=0.059468, e^iax=0.365057, x=0.0441333: lhs=0.002624516071, rhs=(0.00131225803).
- Counterexample: {'a': '0.059468', 'e^iax': '0.365057', 'x': '0.0441333'} → lhs 0.00262451607140920118125358070558034938, rhs (0.0013122580357046005906267903527901746, rel diff 1.0000000000
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:54055676:1376302047:55

- Page: [Frank-Kamenetskii theory](https://en.wikipedia.org/wiki/Frank-Kamenetskii_theory) › Semenov theory > Steady-state regime  · verdict **FAIL**, symbolic unknown
- LaTeX: `\delta e^\theta= \theta, \quad \Rightarrow \quad \theta = -W(-\delta)`
- Context before: …r $\delta$ . The numerical solution of the above equation for different values of $\delta$ is shown in the figure. Steady-state regime. When $0<\delta<e^{-1}$ , the linear term eventually dominates and the system is able to reach a steady state as $\tau\rightarrow \infty$ . At steady state ( $d\theta/d\tau=0$ ), the balance is given by the equation
- Context after: where $W$ represents the Lambert W function. From the properties of Lambert W function, it is easy to see that the steady state temperature provided by the above equation exists only when $\delta\leq \delta_c=1/e$ , where $\delta_c$ is called as Frank-Kamenetskii parameter as a critical point where the system bifurcates from the existence of steady…
- Translator read: `delta*e**theta`  =  `theta`  · notes: pre:spacing
cond: \Rightarrow \quad \theta = -W(-\delta)
hint:e_only_as_exp_base
sides: \delta e^\theta  ||  \theta
- Assumptions: domains {'delta': 'positive', 'theta': 'real'}; constants {'e': 'E'}; constraints ['0 < delta', 'delta <= delta']
- Verifier: The identity fails at 60 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at delta=0.182144, theta=0.0910258: lhs=0.199501824774, rhs=0.091025800000).
- Counterexample: {'delta': '0.182144', 'theta': '0.0910258'} → lhs 0.19950182477447947730028076108696588304, rhs 0.09102580000000000000000000000000000000, rel diff 0.5437344991
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:54055676:1376302047:109

- Page: [Frank-Kamenetskii theory](https://en.wikipedia.org/wiki/Frank-Kamenetskii_theory) › Frank-Kamenetskii steady-state theory > Planar vessel  · verdict **FAIL**, symbolic unknown
- LaTeX: `e^{\theta_m/2} = \cosh \sqrt{\frac{\delta e^{\theta_m}} 2}  \quad \text{or} \quad \delta = 2 e^{-\theta_m} \left(\operatorname{arcosh} e^{\theta_m/2}\right)^{\!2}`
- Context before: …ta)/2} = \cosh \left(\eta \sqrt{\frac{\delta e^{\theta_m}}{2}} \right)$ The above equation is the exact solution, but $\theta_m$ maximum temperature is unknown, but we have not used the boundary condition of the wall yet. Thus using the wall boundary condition $\theta=0$ at $\eta=1$ , the maximum temperature is obtained from an implicit expression,
- Context after: Critical $\delta_c$ is obtained by finding the maximum point of the equation (see figure), i.e., $d\delta/d\theta_m=0$ at $\delta_c$ . $\frac{d\delta}{d\theta_m}=0, \quad \Rightarrow \quad e^{\theta_{m,c}/2} - \sqrt{e^{\theta_{m,c}}-1}\operatorname{arcosh} e^{\theta_{m,c}/2} =0$ $\theta_{m,c}= 1.1868, \quad \Rightarrow \quad \delta_c = 0.8785$ So t…
- Translator read: `e**(theta_m/2)`  =  `cosh(sqrt(2)*sqrt(delta*e**theta_m)/2)`  · notes: pre:left_right
pre:spacing
cond: \delta = 2 e^{-\theta_m} \left(\operatorname{arcosh} e^{\theta_m/2}\right)^{\!2}
hint:e_only_as_exp_base
sides: e^{\theta_m/2}  ||  \cosh \sqrt{\frac{\delta e^{\theta_m}} 2}
- Assumptions: domains {'delta': 'positive', 'theta_m': 'real'}; constants {'e': 'E'}; constraints []
- Verifier: The identity fails at 57 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at delta=0.0526122, theta_m=0.126363: lhs=1.065220159145, rhs=1.014961848088).
- Counterexample: {'delta': '0.0526122', 'theta_m': '0.126363'} → lhs 1.06522015914587749424374030453626969181, rhs 1.01496184808842240670832919158482046827, rel diff 0.0471811490
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 9/12 fail, 0 err

---
## wiki:en:4555635:1363475288:25

- Page: [Frequency comb](https://en.wikipedia.org/wiki/Frequency_comb) › History  · verdict **FAIL**, symbolic not_equal
- LaTeX: `2^{15} = 10^{4.5}`
- Context before: …unters, allowing highly accurate measurements of absolute frequency. The optical range has no such device. The two ranges are separated by a frequency gap of $10^5 \times$ . Before the frequency comb, the only way to bridge the gap were the harmonic frequency chains, which doubles radio frequency in 15 stages, reaching a frequency multiplication of
- Context after: . However, those were large and expensive to operate. The frequency comb managed to bridge that gap in one stage. Theodor W. Hänsch and John L. Hall shared half of the 2005 Nobel Prize in Physics for contributions to the development of laser-based precision spectroscopy, including the optical frequency-comb technique. The other half of the prize wa…
- Translator read: `32768`  =  `10000*sqrt(10)`  · notes: sides: 2^{15}  ||  10^{4.5}
- Assumptions: domains {}; constants {}; constraints []
- Verifier: The constant identity does not hold: both sides differ beyond 1e-8 relative error, stably at two working precisions (lhs=32768.000000000000, rhs=31622.776601683793).
- Counterexample: {} → lhs 32768.0000000000000000000000000000000000, rhs 31622.7766016837933199889354443271853372, rel diff 0.0349494445
- Regimes: constant 1/1 fail, 0 err

---
## wiki:en:12316:1381182218:135

- Page: [Gamma function](https://en.wikipedia.org/wiki/Gamma_function) › Properties > General  · verdict **FAIL**, symbolic unknown
- LaTeX: `|\Gamma(a+bi)|^2 = |\Gamma(a)|^2 \prod_{k=0}^\infty \frac{1}{1+\frac{b^2}{(a+k)^2}}`
- Context before: …d_{k=0}^{m-1}\Gamma\left(z + \frac{k}{m}\right) = (2 \pi)^{\frac{m-1}{2}} \; m^{\frac12 - mz} \; \Gamma(mz).$ A simple but useful property, which can be seen from the limit definition, is: $\overline{\Gamma(z)} = \Gamma(\overline{z}) \; \Rightarrow \; \Gamma(z)\Gamma(\overline{z}) \in \mathbb{R} .$ In particular, with $z = a + bi$ , this product is
- Context after: If the real part is an integer or a half-integer, this can be finitely expressed in closed form:…
- Translator read: `Abs(gamma(a + b*i))**2`  =  `Abs(gamma(a))**2*Product(1/(b**2/(a + k)**2 + 1), (k, 0, oo))`  · notes: hint:i_present
sides: |\Gamma(a+bi)|^2  ||  |\Gamma(a)|^2 \prod_{k=0}^\infty \frac{1}{1+\frac{b^2}{(a+k)^2}}
- Assumptions: domains {'a': 'real', 'b': 'real', 'i': 'nonneg_integer'}; constants {}; constraints ['Not(And(Eq(a + b*i, floor(re(a + b*i))), re(a + b*i) <= 0))', 'Not(And(Eq(a, floor(re(a))), re(a) <= 0))']
- Verifier: The identity fails at 26 of 26 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign) (e.g. at a=0.922281, b=0.220953, i=0: lhs=1.105230872064, rhs=1.011326452624).
- Counterexample: {'a': '0.922281', 'b': '0.220953', 'i': '0'} → lhs 1.10523087206421458581502206496700847468, rhs 1.01132645262400754556636737851686049930, rel diff 0.0849636232
- Regimes: small_positive 6/6 fail, 0 err, unit_interval 6/6 fail, 0 err, integers_small 6/6 fail, 0 err, mixed_sign 6/6 fail, 0 err, large 2/7 fail, 5 err

---
## wiki:en:12316:1381182218:140

- Page: [Gamma function](https://en.wikipedia.org/wiki/Gamma_function) › Properties > General  · verdict **FAIL**, symbolic unknown
- LaTeX: `\Gamma(bi)\Gamma(-bi)=\frac{\pi}{-bi\sin \pi bi}=\frac{\pi}{b\sinh \pi b}`
- Context before: …First, consider the reflection formula applied to $z=bi$ . $\Gamma(bi)\Gamma(1-bi)=\frac{\pi}{\sin \pi bi}$ Applying the recurrence relation to the second term: $-bi \cdot \Gamma(bi)\Gamma(-bi)=\frac{\pi}{\sin \pi bi}$ which with simple rearrangement gives
- Context after: Second, consider the reflection formula applied to $z=\tfrac{1}{2}+bi$ . $\Gamma(\tfrac{1}{2}+bi)\Gamma\left(1-(\tfrac{1}{2}+bi)\right)=\Gamma(\tfrac{1}{2}+bi)\Gamma(\tfrac{1}{2}-bi)=\frac{\pi}{\sin \pi (\tfrac{1}{2}+bi)}=\frac{\pi}{\cos \pi bi}=\frac{\pi}{\cosh \pi b}$ Formulas for other values of $z$ for which the real part is integer or half-int…
- Translator read (piece 0): `gamma(-b*i)*gamma(b*i)`  =  `-pi/(b*i*sin(pi*b*i))`  · notes: implicit_function_arg
hint:i_present
sides: \Gamma(bi)\Gamma(-bi)  ||  \frac{\pi}{-bi\sin \pi bi}
- Translator read (piece 1): `-pi/(b*i*sin(pi*b*i))`  =  `pi/(b*sinh(pi*b))`  · notes: implicit_function_arg
hint:i_present
sides: \frac{\pi}{-bi\sin \pi bi}  ||  \frac{\pi}{b\sinh \pi b}
- Assumptions: domains {'b': 'real', 'i': 'nonneg_integer'}; constants {}; constraints ['Not(And(Eq(b*i, floor(re(b*i))), re(b*i) <= 0))', 'Not(And(Eq(-b*i, floor(re(-b*i))), re(-b*i) <= 0))', 'Ne(sin(pi*b*i), 0)', 'Ne(i, 0)', 'Ne(b, 0)', 'Ne(sinh(pi*b), 0)']
- Verifier: Chain link 1: The identity fails at 48 of 48 evaluable points, a clear majority in every regime (small_positive, unit_interval, mixed_sign, large) (e.g. at b=0.0739976, i=1: lhs=-184.282258082, rhs=180.9922717468).
- Counterexample: {'b': '0.0739976', 'i': '1'} → lhs -184.28225808206403627604227053209177721, rhs 180.992271746899301073471423726168854060, rel diff 1.9821470261
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 0/0 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:12316:1381182218:136

- Page: [Gamma function](https://en.wikipedia.org/wiki/Gamma_function) › Properties > General  · verdict **FAIL**, symbolic unknown
- LaTeX: `\begin{align}
|\Gamma(bi)|^2 & = \frac{\pi}{b\sinh \pi b} \\[6pt]
\left|\Gamma\left(\tfrac{1}{2}+bi\right)\right|^2 & = \frac{\pi}{\cosh \pi b} \\[6pt]
\left|\Gamma\left(1+bi\right)\right|^2 & = \frac{\pi b}{\sinh \pi b} \\[6pt]
\left|\Gamma\left(1+n+bi\right)\right|^2 & = \frac{\pi b}{\sinh \pi b} \prod_{k=1}^n \left(k^2 + b^2 \right), \quad n \in \N \\[6pt]
\left|\Gamma\left(-n+bi\right)\right|^2 & = \frac{\pi}{b \sinh \pi b} \prod_{k=1}^n \left(k^2 + b^2 \right)^{-1}, \quad n \in \N \\[6pt]
\left|\Gamma\left(\tfrac{1}{2} \pm n+bi\right)\right|^2 & = \frac{\pi}{\cosh \pi b} \prod_{k=1}^n \left(\left( k-\tfrac{1}{2}\right)^2 + b^2 \right)^{\pm 1}, \quad n \in \N
\\[-1ex]&
\end{align}`
- Context before: …, is: $\overline{\Gamma(z)} = \Gamma(\overline{z}) \; \Rightarrow \; \Gamma(z)\Gamma(\overline{z}) \in \mathbb{R} .$ In particular, with $z = a + bi$ , this product is $|\Gamma(a+bi)|^2 = |\Gamma(a)|^2 \prod_{k=0}^\infty \frac{1}{1+\frac{b^2}{(a+k)^2}}$ If the real part is an integer or a half-integer, this can be finitely expressed in closed form:
- Context after: First, consider the reflection formula applied to $z=bi$ . $\Gamma(bi)\Gamma(1-bi)=\frac{\pi}{\sin \pi bi}$ Applying the recurrence relation to the second term: $-bi \cdot \Gamma(bi)\Gamma(-bi)=\frac{\pi}{\sin \pi bi}$ which with simple rearrangement gives $\Gamma(bi)\Gamma(-bi)=\frac{\pi}{-bi\sin \pi bi}=\frac{\pi}{b\sinh \pi b}$ Second, consider…
- Translator read (piece 0): `Abs(gamma(b*i))**2`  =  `pi/(b*sinh(pi*b))`  · notes: pre:left_right
pre:spacing
pre:env_align
pre:rows=6
implicit_function_arg
hint:i_present
sides: |\Gamma(bi)|^2  ||  \frac{\pi}{b\sinh \pi b}
- Translator read (piece 1): `Abs(gamma(b*i + 1/2))**2`  =  `pi/cosh(pi*b)`  · notes: pre:left_right
pre:spacing
pre:env_align
pre:rows=6
implicit_function_arg
hint:i_present
sides: |\Gamma\left(\tfrac{1}{2}+bi\right)\right|^2  ||  \frac{\pi}{\cosh \pi b}
- Translator read (piece 2): `Abs(gamma(b*i + 1))**2`  =  `pi*b/sinh(pi*b)`  · notes: pre:left_right
pre:spacing
pre:env_align
pre:rows=6
implicit_function_arg
hint:i_present
sides: |\Gamma\left(1+bi\right)\right|^2  ||  \frac{\pi b}{\sinh \pi b}
- Translator read (piece 3): `Abs(gamma(b*i + n + 1))**2`  =  `pi*b*Product(b**2 + k**2, (k, 1, n))/sinh(pi*b)`  · notes: pre:left_right
pre:spacing
pre:env_align
pre:rows=6
implicit_function_arg
cond: n \in \N
hint:i_present
sides: |\Gamma\left(1+n+bi\right)\right|^2  ||  \frac{\pi b}{\sinh \pi b} \prod_{k=1}^n \left(k^2 + b^2 \right)
- Translator read (piece 4): `Abs(gamma(b*i - n))**2`  =  `pi*Product(1/(b**2 + k**2), (k, 1, n))/(b*sinh(pi*b))`  · notes: pre:left_right
pre:spacing
pre:env_align
pre:rows=6
implicit_function_arg
cond: n \in \N
hint:i_present
sides: |\Gamma\left(-n+bi\right)\right|^2  ||  \frac{\pi}{b \sinh \pi b} \prod_{k=1}^n \left(k^2 + b^2 \right)^{-1}
- Translator read (piece 5): `Abs(gamma(b*i + n + 1/2))**2`  =  `pi*Product(b**2 + (k - 1/2)**2, (k, 1, n))/cosh(pi*b)`  · notes: pre:left_right
pre:spacing
pre:env_align
pre:rows=6
implicit_function_arg
cond: n \in \N
pm_variant:+
hint:i_present
sides: |\Gamma\left(\tfrac{1}{2} \pm n+bi\right)\right|^2  ||  \frac{\pi}{\cosh \pi b} \prod_{k=1}^n \left(\left( k-\tfrac{1}{2}\right)^2 + b^2 \right)^{\pm 1}
- Translator read (piece 6): `Abs(gamma(b*i - n + 1/2))**2`  =  `pi*Product(1/(b**2 + (k - 1/2)**2), (k, 1, n))/cosh(pi*b)`  · notes: pre:left_right
pre:spacing
pre:env_align
pre:rows=6
implicit_function_arg
cond: n \in \N
pm_variant:-
hint:i_present
sides: |\Gamma\left(\tfrac{1}{2} \pm n+bi\right)\right|^2  ||  \frac{\pi}{\cosh \pi b} \prod_{k=1}^n \left(\left( k-\tfrac{1}{2}\right)^2 + b^2 \right)^{\pm 1}
- Assumptions: domains {'b': 'real', 'i': 'nonneg_integer', 'n': 'positive_integer'}; constants {}; constraints ['Not(And(Eq(b*i, floor(re(b*i))), re(b*i) <= 0))', 'Ne(sinh(pi*b), 0)', 'Ne(b, 0)', 'Not(And(Eq(b*i + 1/2, floor(re(b*i + 1/2))), re(b*i + 1/2) <= 0))', 'Not(And(Eq(b*i + 1, floor(re(b*i + 1))), re(b*i + 1) <= 0))', 'Not(And(Eq(b*i + n + 1, floor(re(b*i + n + 1))), re(b*i + n + 1) <= 0))', 'Not(And(Eq(b*i - n, floor(re(b*i - n))), re(b*i - n) <= 0))', 'Not(And(Eq(b*i + n + 1/2, floor(re(b*i + n + 1/2))), re(b*i + n + 1/2) <= 0))', 'Not(And(Eq(b*i - n + 1/2, floor(re(b*i - n + 1/2))), re(b*i - n + 1/2) <= 0))']
- Verifier: Chain link 0: The identity fails at 60 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at b=0.973153, i=1: lhs=1.032718263479, rhs=0.304237613552).
- Counterexample: {'b': '0.973153', 'i': '1'} → lhs 1.03271826347956097681810079512340910079, rhs 0.30423761355201194743624096001094815901, rel diff 0.7054011492
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:12316:1381182218:420

- Page: [Gamma function](https://en.wikipedia.org/wiki/Gamma_function) › History > 19th century: Gauss, Weierstrass, and Legendre  · verdict **FAIL**, symbolic unknown
- LaTeX: `\Gamma (n) = n!`
- Context before: …z!$ due to Gauss is sometimes encountered in older literature, but Legendre's notation is dominant in modern works. It is justified to ask why we distinguish between the "ordinary factorial" and the gamma function by using distinct symbols, and particularly why the gamma function should be normalized to $\Gamma (n + 1) = n!$ instead of simply using
- Context after: . Consider that the notation for exponents, $x^n$ , has been generalized from integers to complex numbers $x^z$ without any change. Legendre's motivation for the normalization is not known, and has been criticized as cumbersome by some (the 20th-century mathematician Cornelius Lanczos, for example, called it "void of any rationality" and would inst…
- Translator read: `gamma(n)`  =  `factorial(n)`  · notes: sides: \Gamma (n)  ||  n!
- Assumptions: domains {'n': 'nonneg_integer'}; constants {}; constraints ['Not(And(Eq(n, floor(re(n))), re(n) <= 0))']
- Verifier: The identity fails at 43 of 47 evaluable points, a clear majority in every regime (small_positive, integers_small, mixed_sign, large) (e.g. at n=2: lhs=1.000000000000, rhs=2.000000000000).
- Counterexample: {'n': '2'} → lhs 1.00000000000000000000000000000000000000, rhs 2.00000000000000000000000000000000000000, rel diff 0.5000000000
- Regimes: small_positive 11/12 fail, 0 err, unit_interval 2/3 fail, 0 err, integers_small 11/12 fail, 0 err, mixed_sign 7/8 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:2310978:1305585550:3

- Page: [Gauss's lemma (number theory)](https://en.wikipedia.org/wiki/Gauss's_lemma_(number_theory)) › Statement of the lemma > Example  · verdict **FAIL**, symbolic not_equal
- LaTeX: `\left(\frac
{7}{11}\right) = (-1)^3 = -1.`
- Context before: …right) = (-1)^n,$ where $\left(\frac{a}{p}\right)$ is the Legendre symbol. Example. Taking p = 11 and a = 7, the relevant sequence of integers is 7, 14, 21, 28, 35. After reduction modulo 11, this sequence becomes 7, 3, 10, 6, 2. Three of these integers are larger than 11/2 (namely 6, 7 and 10), so n = 3. Correspondingly Gauss's lemma predicts that
- Context after: This is indeed correct, because 7 is not a quadratic residue modulo 11. The above sequence of residues 7, 3, 10, 6, 2 may also be written −4, 3, −1, −5, 2. In this form, the integers larger than 11/2 appear as negative numbers. It is also apparent that the absolute values of the residues are a permutation of the residues 1, 2, 3, 4, 5. Proof. A fai…
- Translator read (piece 0): `7/11`  =  `-1`  · notes: pre:left_right
pre:trailing_punct
sides: (\frac {7}{11}\right)  ||  (-1)^3
- Translator read (piece 1): `-1`  =  `-1`  · notes: pre:left_right
pre:trailing_punct
sides: (-1)^3  ||  -1
- Assumptions: domains {}; constants {}; constraints []
- Verifier: Chain link 0: The constant identity does not hold: both sides differ beyond 1e-8 relative error, stably at two working precisions (lhs=0.6363636363636363, rhs=-1.000000000000000).
- Counterexample: {} → lhs 0.63636363636363636363636363636363636363, rhs -1.0000000000000000000000000000000000000, rel diff 1.6363636363
- Regimes: constant 1/1 fail, 0 err

---
## wiki:en:2310978:1305585550:20

- Page: [Gauss's lemma (number theory)](https://en.wikipedia.org/wiki/Gauss's_lemma_(number_theory)) › Applications  · verdict **FAIL**, symbolic unknown
- LaTeX: `\left(\frac{a}{p}\right)=\prod_{n=1}^{(p-1)/2}\frac{\sin{(2\pi an/p)}}{\sin{(2\pi n/p)}},`
- Context before: …{p}\right)=(-1)^t$ , where $t=\#\{j \in I: a j \in-I\}$ . In the original statement, $I=\{1,2,\dots,\frac{p-1}2\}$ . The proof is almost the same. Applications. Gauss's lemma is used in many, but by no means all, of the known proofs of quadratic reciprocity. For example, Gotthold Eisenstein used Gauss's lemma to prove that if p is an odd prime then
- Context after: and used this formula to prove quadratic reciprocity. By using elliptic rather than circular functions, he proved the cubic and quartic reciprocity laws. Leopold Kronecker used the lemma to show that $\left(\frac{p}{q}\right)=\sgn\prod_{i=1}^{\frac{q-1}{2}}\prod_{k=1}^{\frac{p-1}{2}}\left(\frac{k}{p}-\frac{i}{q}\right).$ Switching p and q immediate…
- Translator read: `a/p`  =  `Product(sin(2*pi*a*n/p)/sin(2*pi*n/p), (n, 1, p/2 - 1/2))`  · notes: pre:braced_parens
pre:left_right
pre:trailing_punct
sides: (\frac{a}{p}\right)  ||  \prod_{n=1}^{(p-1)/2}\frac{\sin{(2\pi an/p)}}{\sin{(2\pi n/p)}}
- Assumptions: domains {'a': 'real', 'p': 'positive_integer'}; constants {}; constraints ['Q.prime(p)']
- Verifier: The identity fails at 58 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at a=0.0207791, p=1: lhs=0.020779100000, rhs=1.000000000000).
- Counterexample: {'a': '0.0207791', 'p': '1'} → lhs 0.02077910000000000000000000000000000000, rhs 1.00000000000000000000000000000000000000, rel diff 0.9792209000
- Regimes: small_positive 12/28 fail, 16 err, unit_interval 12/15 fail, 3 err, integers_small 10/25 fail, 13 err, mixed_sign 12/20 fail, 8 err, large 12/22 fail, 10 err

---
## wiki:en:7043631:1352747379:87

- Page: [Generalized inverse](https://en.wikipedia.org/wiki/Generalized_inverse) › Types  · verdict **FAIL**, symbolic unknown
- LaTeX: `A^\mathrm{g} A A^\mathrm{g}= A^\mathrm{g}`
- Context before: …then there exists an $n \times m$ matrix $A_{\mathrm{L}}^{-1}$ called the left inverse of $A$ such that $A_{\mathrm{L}}^{-1} A = I_n$ , where $I_n$ is the $n \times n$ identity matrix. Bott–Duffin inverse Drazin inverse Moore–Penrose inverse Some generalized inverses are defined and classified based on the Penrose conditions: $A A^\mathrm{g} A = A$
- Context after: $(A A^\mathrm{g})^* = A A^\mathrm{g}$ $(A^\mathrm{g} A)^* = A^\mathrm{g} A,$ where ${}^*$ denotes conjugate transpose. If $A^\mathrm{g}$ satisfies the first condition, then it is a generalized inverse of $A$ . If it satisfies the first two conditions, then it is a reflexive generalized inverse of $A$ . If it satisfies all four conditions, then it i…
- Translator read: `A*A**(2*g)`  =  `A**g`  · notes: sides: A^\mathrm{g} A A^\mathrm{g}  ||  A^\mathrm{g}
- Assumptions: domains {'A': 'positive', 'g': 'positive'}; constants {}; constraints []
- Verifier: The identity fails at 60 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at A=0.125471, g=0.0530328: lhs=0.100676896610, rhs=0.895763228053).
- Counterexample: {'A': '0.125471', 'g': '0.0530328'} → lhs 0.10067689661086666358896551568010918837, rhs 0.89576322805331391547825526122711871121, rel diff 0.8876076920
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:7043631:1352747379:136

- Page: [Generalized inverse](https://en.wikipedia.org/wiki/Generalized_inverse) › Examples > Inverse of other semigroups (or rings)  · verdict **FAIL**, symbolic not_equal
- LaTeX: `3 \cdot 3 \cdot 3 = 3`
- Context before: …migroups (or rings). The element b is a generalized inverse of an element a if and only if $a \cdot b \cdot a = a$ , in any semigroup (or ring, since the multiplication function in any ring is a semigroup). The generalized inverses of the element 3 in the ring $\mathbb{Z}/12\mathbb{Z}$ are 3, 7, and 11, since in the ring $\mathbb{Z}/12\mathbb{Z}$ :
- Context after: $3 \cdot 7 \cdot 3 = 3$ $3 \cdot 11 \cdot 3 = 3$ The generalized inverses of the element 4 in the ring $\mathbb{Z}/12\mathbb{Z}$ are 1, 4, 7, and 10, since in the ring $\mathbb{Z}/12\mathbb{Z}$ : $4 \cdot 1 \cdot 4 = 4$ $4 \cdot 4 \cdot 4 = 4$ $4 \cdot 7 \cdot 4 = 4$ $4 \cdot 10 \cdot 4 = 4$ If an element a in a semigroup (or ring) has an inverse,…
- Translator read: `27`  =  `3`  · notes: sides: 3 \cdot 3 \cdot 3  ||  3
- Assumptions: domains {}; constants {}; constraints []
- Verifier: The constant identity does not hold: both sides differ beyond 1e-8 relative error, stably at two working precisions (lhs=27.000000000000000, rhs=3.0000000000000000).
- Counterexample: {} → lhs 27.0000000000000000000000000000000000000, rhs 3.00000000000000000000000000000000000000, rel diff 0.8888888888
- Regimes: constant 1/1 fail, 0 err

---
## wiki:en:7043631:1352747379:137

- Page: [Generalized inverse](https://en.wikipedia.org/wiki/Generalized_inverse) › Examples > Inverse of other semigroups (or rings)  · verdict **FAIL**, symbolic not_equal
- LaTeX: `3 \cdot 7 \cdot 3 = 3`
- Context before: …element b is a generalized inverse of an element a if and only if $a \cdot b \cdot a = a$ , in any semigroup (or ring, since the multiplication function in any ring is a semigroup). The generalized inverses of the element 3 in the ring $\mathbb{Z}/12\mathbb{Z}$ are 3, 7, and 11, since in the ring $\mathbb{Z}/12\mathbb{Z}$ : $3 \cdot 3 \cdot 3 = 3$
- Context after: $3 \cdot 11 \cdot 3 = 3$ The generalized inverses of the element 4 in the ring $\mathbb{Z}/12\mathbb{Z}$ are 1, 4, 7, and 10, since in the ring $\mathbb{Z}/12\mathbb{Z}$ : $4 \cdot 1 \cdot 4 = 4$ $4 \cdot 4 \cdot 4 = 4$ $4 \cdot 7 \cdot 4 = 4$ $4 \cdot 10 \cdot 4 = 4$ If an element a in a semigroup (or ring) has an inverse, the inverse must be the…
- Translator read: `63`  =  `3`  · notes: sides: 3 \cdot 7 \cdot 3  ||  3
- Assumptions: domains {}; constants {}; constraints []
- Verifier: The constant identity does not hold: both sides differ beyond 1e-8 relative error, stably at two working precisions (lhs=63.000000000000000, rhs=3.0000000000000000).
- Counterexample: {} → lhs 63.0000000000000000000000000000000000000, rhs 3.00000000000000000000000000000000000000, rel diff 0.9523809523
- Regimes: constant 1/1 fail, 0 err

---
## wiki:en:7043631:1352747379:138

- Page: [Generalized inverse](https://en.wikipedia.org/wiki/Generalized_inverse) › Examples > Inverse of other semigroups (or rings)  · verdict **FAIL**, symbolic not_equal
- LaTeX: `3 \cdot 11 \cdot 3 = 3`
- Context before: …zed inverse of an element a if and only if $a \cdot b \cdot a = a$ , in any semigroup (or ring, since the multiplication function in any ring is a semigroup). The generalized inverses of the element 3 in the ring $\mathbb{Z}/12\mathbb{Z}$ are 3, 7, and 11, since in the ring $\mathbb{Z}/12\mathbb{Z}$ : $3 \cdot 3 \cdot 3 = 3$ $3 \cdot 7 \cdot 3 = 3$
- Context after: The generalized inverses of the element 4 in the ring $\mathbb{Z}/12\mathbb{Z}$ are 1, 4, 7, and 10, since in the ring $\mathbb{Z}/12\mathbb{Z}$ : $4 \cdot 1 \cdot 4 = 4$ $4 \cdot 4 \cdot 4 = 4$ $4 \cdot 7 \cdot 4 = 4$ $4 \cdot 10 \cdot 4 = 4$ If an element a in a semigroup (or ring) has an inverse, the inverse must be the only generalized inverse…
- Translator read: `99`  =  `3`  · notes: sides: 3 \cdot 11 \cdot 3  ||  3
- Assumptions: domains {}; constants {}; constraints []
- Verifier: The constant identity does not hold: both sides differ beyond 1e-8 relative error, stably at two working precisions (lhs=99.000000000000000, rhs=3.0000000000000000).
- Counterexample: {} → lhs 99.0000000000000000000000000000000000000, rhs 3.00000000000000000000000000000000000000, rel diff 0.9696969696
- Regimes: constant 1/1 fail, 0 err

---
## wiki:en:7043631:1352747379:141

- Page: [Generalized inverse](https://en.wikipedia.org/wiki/Generalized_inverse) › Examples > Inverse of other semigroups (or rings)  · verdict **FAIL**, symbolic not_equal
- LaTeX: `4 \cdot 1 \cdot 4 = 4`
- Context before: …ed inverses of the element 3 in the ring $\mathbb{Z}/12\mathbb{Z}$ are 3, 7, and 11, since in the ring $\mathbb{Z}/12\mathbb{Z}$ : $3 \cdot 3 \cdot 3 = 3$ $3 \cdot 7 \cdot 3 = 3$ $3 \cdot 11 \cdot 3 = 3$ The generalized inverses of the element 4 in the ring $\mathbb{Z}/12\mathbb{Z}$ are 1, 4, 7, and 10, since in the ring $\mathbb{Z}/12\mathbb{Z}$ :
- Context after: $4 \cdot 4 \cdot 4 = 4$ $4 \cdot 7 \cdot 4 = 4$ $4 \cdot 10 \cdot 4 = 4$ If an element a in a semigroup (or ring) has an inverse, the inverse must be the only generalized inverse of this element, like the elements 1, 5, 7, and 11 in the ring $\mathbb{Z}/12\mathbb{Z}$ . In the ring $\mathbb{Z}/12\mathbb{Z}$ any element is a generalized inverse of 0;…
- Translator read: `16`  =  `4`  · notes: sides: 4 \cdot 1 \cdot 4  ||  4
- Assumptions: domains {}; constants {}; constraints []
- Verifier: The constant identity does not hold: both sides differ beyond 1e-8 relative error, stably at two working precisions (lhs=16.000000000000000, rhs=4.0000000000000000).
- Counterexample: {} → lhs 16.0000000000000000000000000000000000000, rhs 4.00000000000000000000000000000000000000, rel diff 0.7500000000
- Regimes: constant 1/1 fail, 0 err

---
## wiki:en:7043631:1352747379:142

- Page: [Generalized inverse](https://en.wikipedia.org/wiki/Generalized_inverse) › Examples > Inverse of other semigroups (or rings)  · verdict **FAIL**, symbolic not_equal
- LaTeX: `4 \cdot 4 \cdot 4 = 4`
- Context before: …nt 3 in the ring $\mathbb{Z}/12\mathbb{Z}$ are 3, 7, and 11, since in the ring $\mathbb{Z}/12\mathbb{Z}$ : $3 \cdot 3 \cdot 3 = 3$ $3 \cdot 7 \cdot 3 = 3$ $3 \cdot 11 \cdot 3 = 3$ The generalized inverses of the element 4 in the ring $\mathbb{Z}/12\mathbb{Z}$ are 1, 4, 7, and 10, since in the ring $\mathbb{Z}/12\mathbb{Z}$ : $4 \cdot 1 \cdot 4 = 4$
- Context after: $4 \cdot 7 \cdot 4 = 4$ $4 \cdot 10 \cdot 4 = 4$ If an element a in a semigroup (or ring) has an inverse, the inverse must be the only generalized inverse of this element, like the elements 1, 5, 7, and 11 in the ring $\mathbb{Z}/12\mathbb{Z}$ . In the ring $\mathbb{Z}/12\mathbb{Z}$ any element is a generalized inverse of 0; however 2 has no genera…
- Translator read: `64`  =  `4`  · notes: sides: 4 \cdot 4 \cdot 4  ||  4
- Assumptions: domains {}; constants {}; constraints []
- Verifier: The constant identity does not hold: both sides differ beyond 1e-8 relative error, stably at two working precisions (lhs=64.000000000000000, rhs=4.0000000000000000).
- Counterexample: {} → lhs 64.0000000000000000000000000000000000000, rhs 4.00000000000000000000000000000000000000, rel diff 0.9375000000
- Regimes: constant 1/1 fail, 0 err

---
## wiki:en:7043631:1352747379:143

- Page: [Generalized inverse](https://en.wikipedia.org/wiki/Generalized_inverse) › Examples > Inverse of other semigroups (or rings)  · verdict **FAIL**, symbolic not_equal
- LaTeX: `4 \cdot 7 \cdot 4 = 4`
- Context before: …b{Z}/12\mathbb{Z}$ are 3, 7, and 11, since in the ring $\mathbb{Z}/12\mathbb{Z}$ : $3 \cdot 3 \cdot 3 = 3$ $3 \cdot 7 \cdot 3 = 3$ $3 \cdot 11 \cdot 3 = 3$ The generalized inverses of the element 4 in the ring $\mathbb{Z}/12\mathbb{Z}$ are 1, 4, 7, and 10, since in the ring $\mathbb{Z}/12\mathbb{Z}$ : $4 \cdot 1 \cdot 4 = 4$ $4 \cdot 4 \cdot 4 = 4$
- Context after: $4 \cdot 10 \cdot 4 = 4$ If an element a in a semigroup (or ring) has an inverse, the inverse must be the only generalized inverse of this element, like the elements 1, 5, 7, and 11 in the ring $\mathbb{Z}/12\mathbb{Z}$ . In the ring $\mathbb{Z}/12\mathbb{Z}$ any element is a generalized inverse of 0; however 2 has no generalized inverse, since the…
- Translator read: `112`  =  `4`  · notes: sides: 4 \cdot 7 \cdot 4  ||  4
- Assumptions: domains {}; constants {}; constraints []
- Verifier: The constant identity does not hold: both sides differ beyond 1e-8 relative error, stably at two working precisions (lhs=112.00000000000000, rhs=4.0000000000000000).
- Counterexample: {} → lhs 112.000000000000000000000000000000000000, rhs 4.00000000000000000000000000000000000000, rel diff 0.9642857142
- Regimes: constant 1/1 fail, 0 err

---
## wiki:en:7043631:1352747379:144

- Page: [Generalized inverse](https://en.wikipedia.org/wiki/Generalized_inverse) › Examples > Inverse of other semigroups (or rings)  · verdict **FAIL**, symbolic not_equal
- LaTeX: `4 \cdot 10 \cdot 4 = 4`
- Context before: …, 7, and 11, since in the ring $\mathbb{Z}/12\mathbb{Z}$ : $3 \cdot 3 \cdot 3 = 3$ $3 \cdot 7 \cdot 3 = 3$ $3 \cdot 11 \cdot 3 = 3$ The generalized inverses of the element 4 in the ring $\mathbb{Z}/12\mathbb{Z}$ are 1, 4, 7, and 10, since in the ring $\mathbb{Z}/12\mathbb{Z}$ : $4 \cdot 1 \cdot 4 = 4$ $4 \cdot 4 \cdot 4 = 4$ $4 \cdot 7 \cdot 4 = 4$
- Context after: If an element a in a semigroup (or ring) has an inverse, the inverse must be the only generalized inverse of this element, like the elements 1, 5, 7, and 11 in the ring $\mathbb{Z}/12\mathbb{Z}$ . In the ring $\mathbb{Z}/12\mathbb{Z}$ any element is a generalized inverse of 0; however 2 has no generalized inverse, since there is no b in $\mathbb{Z}…
- Translator read: `160`  =  `4`  · notes: sides: 4 \cdot 10 \cdot 4  ||  4
- Assumptions: domains {}; constants {}; constraints []
- Verifier: The constant identity does not hold: both sides differ beyond 1e-8 relative error, stably at two working precisions (lhs=160.00000000000000, rhs=4.0000000000000000).
- Counterexample: {} → lhs 160.000000000000000000000000000000000000, rhs 4.00000000000000000000000000000000000000, rel diff 0.9750000000
- Regimes: constant 1/1 fail, 0 err

---
## wiki:en:238181:1346684211:84

- Page: [Gibbs free energy](https://en.wikipedia.org/wiki/Gibbs_free_energy) › Definitions  · verdict **FAIL**, symbolic unknown
- LaTeX: `\frac{G}{N} = \frac{G^\circ}{N} + kT\ln \frac{p}{p^\circ}\, .`
- Context before: …bbs free energy can be thought of as a "dynamic" quantity, in that it is a representative measure of the competing effects of the enthalpic and entropic driving forces involved in a thermodynamic process. The temperature dependence of the Gibbs energy for an ideal gas is given by the Gibbs–Helmholtz equation, and its pressure dependence is given by
- Context after: or more conveniently as its chemical potential: $\frac{G}{N} = \mu = \mu^\circ + kT\ln \frac{p}{p^\circ}\, .$ In non-ideal systems, fugacity comes into play. Derivation. The Gibbs free energy total differential with respect to natural variables may be derived by Legendre transforms of the internal energy. $\mathrm{d}U = T\,\mathrm{d}S - p\,\mathrm{…
- Translator read: `G/N`  =  `pi*G/(180*N) + T*k*log(180/pi)`  · notes: pre:spacing
pre:trailing_punct
degrees
sides: \frac{G}{N}  ||  \frac{G^\circ}{N} + kT\ln \frac{p}{p^\circ}
- Assumptions: domains {'G': 'positive', 'N': 'nonneg_integer', 'T': 'positive', 'k': 'nonneg_integer'}; constants {}; constraints ['Ne(N, 0)']
- Verifier: The identity fails at 60 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at G=0.850692, N=1, T=0.141339, k=0: lhs=0.850692000000, rhs=0.014847376320).
- Counterexample: {'G': '0.850692', 'N': '1', 'T': '0.141339', 'k': '0'} → lhs 0.85069200000000000000000000000000000000, rhs 0.01484737632037560216452368347227114926, rel diff 0.9825467074
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:53252845:1375875409:68

- Page: [Glossary of calculus](https://en.wikipedia.org/wiki/Glossary_of_calculus) › G  · verdict **FAIL**, symbolic unknown
- LaTeX: `(fg)^{(n)}=\sum_{k=0}^n {n \choose k} f^{(n-k)} g^{(k)},`
- Context before: …glossaries like this one are useful for looking up, comparing and reviewing large numbers of terms together. You can help enhance this page by adding new terms or writing definitions for existing ones. This glossary of calculus is a list of definitions about calculus, its sub-disciplines, and related fields. A. B. C. D. E. F. G. [defn | defn]
- Context after: H. I. J. L. M. N. O. P. Q. R. S. T. U. V. W. See also. Outline of calculus Glossary of areas of mathematics Glossary of astronomy Glossary of biology Glossary of botany Glossary of chemistry Glossary of ecology Glossary of engineering Glossary of physics Glossary of probability and statistics References. Works cited. . . . . Notes.…
- Translator read: `(f*g)**n`  =  `Sum(f**(-k + n)*g**k*binomial(n, k), (k, 0, n))`  · notes: pre:over_choose
pre:trailing_punct
sides: (fg)^{(n)}  ||  \sum_{k=0}^n {\binom{n }{ k}} f^{(n-k)} g^{(k)}
- Assumptions: domains {'f': 'positive', 'g': 'positive', 'n': 'nonneg_integer'}; constants {}; constraints []
- Verifier: The identity fails at 54 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at f=0.837724, g=0.00619904, n=1: lhs=0.005193084584, rhs=0.843923040000).
- Counterexample: {'f': '0.837724', 'g': '0.00619904', 'n': '1'} → lhs 0.00519308458496000000000000000000000000, rhs 0.84392304000000000000000000000000000000, rel diff 0.9938464950
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 11/12 fail, 0 err, integers_small 9/12 fail, 0 err, mixed_sign 10/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:80262208:1376111431:44

- Page: [Golden field](https://en.wikipedia.org/wiki/Golden_field) › Basic arithmetic  · verdict **FAIL**, symbolic unknown
- LaTeX: `\begin{align}
\frac{a_1 + b_1\sqrt5}{a_2 + b_2\sqrt5} &= \frac{a_1a_2 - 5b_1b_2}{a_2^2 - 5b_2^2} + \frac{-a_1b_2 + b_1a_2}{a_2^2 - 5b_2^2}\sqrt5, \\[6mu]
\frac{a_1 + b_1\varphi}{a_2 + b_2\varphi} &=  \frac{a_1a_2 + a_1b_2 - b_1b_2}{a_2^2 + a_2b_2 - b_2^2 } + \frac{-a_1b_2 + b_1a_2}{a_2^2 + a_2b_2 - b_2^2 }\varphi.
\end{align}`
- Context before: …To divide two numbers, multiply the first by second's reciprocal:
- Context after: As in any field, addition and multiplication of numbers in is associative and commutative; $0$ is the additive identity and $1$ is the multiplicative identity; every number $\alpha$ has an additive inverse $-\alpha$ and a multiplicative inverse $1/\alpha$ ; and multiplication distributes over addition. Arithmetic between numbers in is consistent wi…
- Translator read (piece 0): `(a_1 + sqrt(5)*b_1)/(a_2 + sqrt(5)*b_2)`  =  `(a_1*a_2 - 5*b_1*b_2)/(a_2**2 - 5*b_2**2) + sqrt(5)*(-a_1*b_2 + a_2*b_1)/(a_2**2 - 5*b_2**2)`  · notes: pre:env_align
pre:rows=2
pre:trailing_punct
sides: \frac{a_1 + b_1\sqrt5}{a_2 + b_2\sqrt5}  ||  \frac{a_1a_2 - 5b_1b_2}{a_2^2 - 5b_2^2} + \frac{-a_1b_2 + b_1a_2}{a_2^2 - 5b_2^2}\sqrt5
- Translator read (piece 1): `(a_1 + b_1*phi)/(a_2 + b_2*phi)`  =  `phi*(-a_1*b_2 + a_2*b_1)/(a_2**2 + a_2*b_2 - b_2**2) + (a_1*a_2 + a_1*b_2 - b_1*b_2)/(a_2**2 + a_2*b_2 - b_2**2)`  · notes: pre:env_align
pre:rows=2
pre:trailing_punct
sides: \frac{a_1 + b_1\varphi}{a_2 + b_2\varphi}  ||  \frac{a_1a_2 + a_1b_2 - b_1b_2}{a_2^2 + a_2b_2 - b_2^2 } + \frac{-a_1b_2 + b_1a_2}{a_2^2 + a_2b_2 - b_2^2 }\varphi
- Assumptions: domains {'a_1': 'real', 'a_2': 'real', 'b_1': 'real', 'b_2': 'real', 'phi': 'real'}; constants {}; constraints ['Ne(a_2 + sqrt(5)*b_2, 0)', 'Ne(a_2**2 - 1*5*b_2**2, 0)', 'Ne(a_2 + b_2*phi, 0)', 'Ne(a_2**2 + a_2*b_2 - b_2**2, 0)']
- Verifier: Chain link 1: The identity fails at 58 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at a_1=0.271799, a_2=0.177389, b_1=0.224993, b_2=0.0521641, phi=0.284272: lhs=1.746759260910, rhs=1.525587515163).
- Counterexample: {'a_1': '0.271799', 'a_2': '0.177389', 'b_1': '0.224993', 'b_2': '0.0521641', 'phi': '0.284272'} → lhs 1.74675926091043025354033096756750479359, rhs 1.52558751516313756561403440940612261185, rel diff 0.1266183329
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 10/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:80262208:1376111431:43

- Page: [Golden field](https://en.wikipedia.org/wiki/Golden_field) › Basic arithmetic  · verdict **FAIL**, symbolic unknown
- LaTeX: `\begin{align}
\frac{1}{a + b\sqrt5} &= \frac{1}{a + b\sqrt5} \cdot \frac{a - b\sqrt5}{a - b\sqrt5} = \frac{a}{a^2 - 5b^2} - \frac{b}{a^2 - 5b^2}\sqrt5, \\[3mu]
\frac{1}{a + b\varphi} &= \frac{1}{a + b\varphi} \cdot \frac{a + b - b\varphi}{a + b - b\varphi} = \frac{a + b}{a^2 + ab - b^2 } - \frac{b}{a^2 + ab - b^2 }\varphi.
\end{align}`
- Context before: …To find the reciprocal of a number $\alpha$ , rationalize the denominator: $1/\alpha = {}$ $\overline\alpha / \alpha \overline\alpha = {}$ $\overline\alpha / \mathrm{N}(\alpha)$ , where $\overline\alpha$ is the algebraic conjugate and $\mathrm N(\alpha)$ is the field norm, as defined below. Explicitly:
- Context after: To divide two numbers, multiply the first by second's reciprocal: $\begin{align} \frac{a_1 + b_1\sqrt5}{a_2 + b_2\sqrt5} &= \frac{a_1a_2 - 5b_1b_2}{a_2^2 - 5b_2^2} + \frac{-a_1b_2 + b_1a_2}{a_2^2 - 5b_2^2}\sqrt5, \\[6mu] \frac{a_1 + b_1\varphi}{a_2 + b_2\varphi} &= \frac{a_1a_2 + a_1b_2 - b_1b_2}{a_2^2 + a_2b_2 - b_2^2 } + \frac{-a_1b_2 + b_1a_2}{a…
- Translator read (piece 0): `1/(a + sqrt(5)*b)`  =  `1/(a + sqrt(5)*b)`  · notes: pre:env_align
pre:rows=2
pre:trailing_punct
sides: \frac{1}{a + b\sqrt5}  ||  \frac{1}{a + b\sqrt5} \cdot \frac{a - b\sqrt5}{a - b\sqrt5}
- Translator read (piece 1): `1/(a + sqrt(5)*b)`  =  `a/(a**2 - 5*b**2) - sqrt(5)*b/(a**2 - 5*b**2)`  · notes: pre:env_align
pre:rows=2
pre:trailing_punct
sides: \frac{1}{a + b\sqrt5} \cdot \frac{a - b\sqrt5}{a - b\sqrt5}  ||  \frac{a}{a^2 - 5b^2} - \frac{b}{a^2 - 5b^2}\sqrt5
- Translator read (piece 2): `1/(a + b*phi)`  =  `1/(a + b*phi)`  · notes: pre:env_align
pre:rows=2
pre:trailing_punct
sides: \frac{1}{a + b\varphi}  ||  \frac{1}{a + b\varphi} \cdot \frac{a + b - b\varphi}{a + b - b\varphi}
- Translator read (piece 3): `1/(a + b*phi)`  =  `-b*phi/(a**2 + a*b - b**2) + (a + b)/(a**2 + a*b - b**2)`  · notes: pre:env_align
pre:rows=2
pre:trailing_punct
sides: \frac{1}{a + b\varphi} \cdot \frac{a + b - b\varphi}{a + b - b\varphi}  ||  \frac{a + b}{a^2 + ab - b^2 } - \frac{b}{a^2 + ab - b^2 }\varphi
- Assumptions: domains {'a': 'real', 'b': 'real', 'phi': 'real'}; constants {}; constraints ['Ne(a + sqrt(5)*b, 0)', 'Ne(a**2 - 1*5*b**2, 0)', 'Ne(a + b*phi, 0)', 'Ne(a**2 + a*b - b**2, 0)']
- Verifier: Chain link 3: The identity fails at 59 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at a=0.377123, b=0.358638, phi=0.38293: lhs=1.943799888295, rhs=4.020309065824).
- Counterexample: {'a': '0.377123', 'b': '0.358638', 'phi': '0.38293'} → lhs 1.94379988829547298973433051542217271182, rhs 4.02030906582431682573296963057511520236, rel diff 0.5165048615
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 11/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err
