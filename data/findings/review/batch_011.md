# Review batch 011 — 22 items

For each item answer with one JSON line (Finding schema): {"formula_id": ..., "verdict": "FAIL", "review": {"status": "confirmed_error"|"false_positive"|"ambiguous", "reviewer": "<name>", "notes": "<why, one or two sentences>"}, "suggested_fix": "<corrected LaTeX or null>", "evidence": "<independent source or derivation>"}


---
## wiki:en:22653593:1375897417:22

- Page: [Special classes of semigroups](https://en.wikipedia.org/wiki/Special_classes_of_semigroups) › List of special classes of semigroups  · verdict **FAIL**, symbolic unknown
- LaTeX: `aa^\omega=a^\omega`
- Context before: …. 154, 155, 158 $\mathbb D\mathbf{A}$ : Semigroup whose regular D are aperiodic semigroup Each regular D-class is an aperiodic semigroup Equivalently, every regular D-class is a rectangular band Equivalently, regular D-class are semigroup, and furthermore S is aperiodic Equivalently, for finite monoid: regular D-class are semigroup, and furthermore
- Context after: Equivalently, e≤Ja implies eae = e Equivalently, e≤Jf implies efe = e. Finite Pin p. 156, 158 $\ell\mathbf{1}$ / $\mathbf K$ : Lefty trivial semigroup e: eS = e, Equivalently, I is a left zero semigroup equal to E, Equivalently, for finite semigroup: I is a left zero semigroup equals $S^{|S|}$ , Equivalently, for finite semigroup: $a_1\dots a_ny=a_…
- Translator read: `a*a**omega`  =  `a**omega`  · notes: sides: aa^\omega  ||  a^\omega
- Assumptions: domains {'a': 'real', 'omega': 'positive'}; constants {}; constraints ['a > 0']
- Verifier: The identity fails at 60 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at a=0.167696, omega=0.0956374: lhs=0.141370264729, rhs=0.843015126951).
- Counterexample: {'a': '0.167696', 'omega': '0.0956374'} → lhs 0.14137026472922754613577292271162837889, rhs 0.84301512695131396178664322769552272501, rel diff 0.8323040000
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:22653593:1375897417:27

- Page: [Special classes of semigroups](https://en.wikipedia.org/wiki/Special_classes_of_semigroups) › List of special classes of semigroups  · verdict **FAIL**, symbolic unknown
- LaTeX: `a^\omega b=a^\omega`
- Context before: …e≤Jf implies efe = e. Finite Pin p. 156, 158 $\ell\mathbf{1}$ / $\mathbf K$ : Lefty trivial semigroup e: eS = e, Equivalently, I is a left zero semigroup equal to E, Equivalently, for finite semigroup: I is a left zero semigroup equals $S^{|S|}$ , Equivalently, for finite semigroup: $a_1\dots a_ny=a_1\dots a_n$ , Equivalently, for finite semigroup:
- Context after: . Finite Pin pp. 149, 158 $\mathbf{r1}$ / $\mathbf D$ : Right trivial semigroup e: Se = e, Equivalently, I is a right zero semigroup equal to E, Equivalently, for finite semigroup: I is a right zero semigroup equals $S^{|S|}$ , Equivalently, for finite semigroup: $b a_1\dots a_n=a_1\dots a_n$ , Equivalently, for finite semigroup: $b a^\omega=a^\ome…
- Translator read: `a**omega*b`  =  `a**omega`  · notes: sides: a^\omega b  ||  a^\omega
- Assumptions: domains {'a': 'real', 'b': 'real', 'omega': 'positive'}; constants {}; constraints ['a > 0']
- Verifier: The identity fails at 59 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at a=0.0925836, b=0.156176, omega=0.17153: lhs=0.103835027770, rhs=0.664859054979).
- Counterexample: {'a': '0.0925836', 'b': '0.156176', 'omega': '0.17153'} → lhs 0.10383502777043617081850811920788902294, rhs 0.66485905497922965640372476698013153715, rel diff 0.8438240000
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 11/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:22653593:1375897417:32

- Page: [Special classes of semigroups](https://en.wikipedia.org/wiki/Special_classes_of_semigroups) › List of special classes of semigroups  · verdict **FAIL**, symbolic unknown
- LaTeX: `b a^\omega=a^\omega`
- Context before: …\omega b=a^\omega$ . Finite Pin pp. 149, 158 $\mathbf{r1}$ / $\mathbf D$ : Right trivial semigroup e: Se = e, Equivalently, I is a right zero semigroup equal to E, Equivalently, for finite semigroup: I is a right zero semigroup equals $S^{|S|}$ , Equivalently, for finite semigroup: $b a_1\dots a_n=a_1\dots a_n$ , Equivalently, for finite semigroup:
- Context after: . Finite Pin pp. 149, 158 $\mathbb L\mathbf{1}$ : Locally trivial semigroup eSe = e, Equivalently, I is equal to E, Equivalently, eaf = ef, Equivalently, for finite semigroup: $y a_1\dots a_n=a_1\dots a_n$ , Equivalently, for finite semigroup: $a_1\dots a_n y a_1\dots a_n=a_1\dots a_n$ , Equivalently, for finite semigroup: $a^\omega b a^\omega=a^\o…
- Translator read: `a**omega*b`  =  `a**omega`  · notes: sides: b a^\omega  ||  a^\omega
- Assumptions: domains {'a': 'real', 'b': 'real', 'omega': 'positive'}; constants {}; constraints ['a > 0']
- Verifier: The identity fails at 60 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at a=0.320843, b=0.173138, omega=0.0629166: lhs=0.161186996724, rhs=0.930974117317).
- Counterexample: {'a': '0.320843', 'b': '0.173138', 'omega': '0.0629166'} → lhs 0.16118699672413652626444982685776587696, rhs 0.93097411731761095926053106110597255923, rel diff 0.8268620000
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:173997:1375616063:69

- Page: [Special unitary group](https://en.wikipedia.org/wiki/Special_unitary_group) › SU(3) > Lie algebra  · verdict **FAIL**, symbolic unknown
- LaTeX: `\begin{align}
  \exp(i\theta H) ={}
          &\left[-\frac{1}{3} I\sin\left(\varphi + \frac{2\pi}{3}\right) \sin\left(\varphi - \frac{2\pi}{3}\right) - \frac{1}{2\sqrt{3}}~H\sin(\varphi) - \frac{1}{4}~H^2\right]
           \frac{\exp\left(\frac{2}{\sqrt{3}}~i\theta\sin(\varphi)\right)}
                {\cos\left(\varphi + \frac{2\pi}{3}\right) \cos\left(\varphi - \frac{2\pi}{3}\right)} \\[6pt]
    & {} + \left[-\frac{1}{3}~I\sin(\varphi) \sin\left(\varphi - \frac{2\pi}{3}\right) - \frac{1}{2\sqrt{3}}~H\sin\left(\varphi + \frac{2\pi}{3}\right) - \frac{1}{4}~H^{2}\right]
           \frac{\exp\left(\frac{2}{\sqrt{3}}~i\theta \sin\left(\varphi + \frac{2\pi}{3}\right)\right)}
                {\cos(\varphi) \cos\left(\varphi - \frac{2\pi}{3}\right)} \\[6pt]
    & {} + \left[-\frac{1}{3}~I\sin(\varphi) \sin\left(\varphi + \frac{2\pi}{3}\right) - \frac{1}{2\sqrt{3}}~H \sin\left(\varphi - \frac{2\pi}{3}\right) - \frac{1}{4}~H^2\right]
           \frac{\exp\left(\frac{2}{\sqrt{3}}~i\theta \sin\left(\varphi - \frac{2\pi}{3}\right)\right)}
                {\cos(\varphi)\cos\left(\varphi + \frac{2\pi}{3}\right)}
\end{align}`
- Context before: …They vanish if the number of indices from the set {2, 5, 7} is odd. A generic SU(3) group element generated by a traceless 3 × 3 Hermitian matrix H, normalized as tr(H2) = 2, can be expressed as a second order matrix polynomial in H:
- Context after: where $\varphi \equiv \frac{1}{3}\left[\arccos\left(\frac{3\sqrt{3}}{2}\det H\right) - \frac{\pi}{2}\right].$ Important subgroups. In physics the special unitary group is used to represent fermionic symmetries. In theories of symmetry breaking it is important to be able to find the subgroups of the special unitary group. Subgroups of SU(n) that are…
- Translator read: `exp(H*i*theta)`  =  `(-H**2/4 - sqrt(3)*H*sin(phi)/6 + I*sin(phi + pi/3)*cos(phi + pi/6)/3)*exp(2*sqrt(3)*i*theta*sin(phi)/3)/(sin(phi + pi/6)*cos(phi + pi/3)) - (-H**2/4 + sqrt(3)*H*sin(phi + pi/3)/6 - I*sin(phi)*cos(phi + pi/6)/3)*exp(-2*sqrt(3)*i*theta*sin(phi + pi/3)/3)/(sin(phi + pi/6)*cos(phi)) - (-H**2/4 - sqrt(3)*H*cos(phi + pi/6)/6 + I*sin(phi)*sin(phi + pi/3)/3)*exp(2*sqrt(3)*i*theta*cos(phi + pi/6)/3)/(cos(phi)*cos(phi + pi/3))`  · notes: pre:left_right
pre:spacing
pre:env_align
pre:row_continues_expr
hint:i_present
sides: \exp(i\theta H)  ||  [-\frac{1}{3} I\sin\left(\varphi + \frac{2\pi}{3}\right) \sin\left(\varphi - \frac{2\pi}{3}\right) - \frac{1}{2\sqrt{3}}~H\sin(\varphi) - \frac{1}{4}~H^2\right]            \frac{\exp\left(\frac{2}{\sqrt{3}}~i\theta\sin(\varphi)\right)}                 {\cos\left(\varphi + \frac{2\pi}{3}\right) \cos\left(\varphi - \frac{2\pi}{3}\right)} \\[6pt]     & {} + \left[-\frac{1}{3}~I\sin(\varphi) \sin\left(\varphi - \frac{2\pi}{3}\right) - \frac{1}{2\sqrt{3}}~H\sin\left(\varphi + \frac{2\pi}{3}\right) - \frac{1}{4}~H^{2}\right]            \frac{\exp\left(\frac{2}{\sqrt{3}}~i\theta \sin\left(\varphi + \frac{2\pi}{3}\right)\right)}                 {\cos(\varphi) \cos\left(\varphi - \frac{2\pi}{3}\right)} \\[6pt]     & {} + \left[-\frac{1}{3}~I\sin(\varphi) \sin\left(\varphi + \frac{2\pi}{3}\right) - \frac{1}{2\sqrt{3}}~H \sin\left(\varphi - \frac{2\pi}{3}\right) - \frac{1}{4}~H^2\right]            \frac{\exp\left(\frac{2}{\sqrt{3}}~i\theta \sin\left(\varphi - \frac{2\pi}{3}\right)\right)}                 {\cos(\varphi)\cos\left(\varphi + \frac{2\pi}{3}\right)}
- Assumptions: domains {'H': 'positive', 'I': 'positive', 'phi': 'angle', 'theta': 'real'}; constants {'i': 'I'}; constraints ['Ne(cos(phi + pi/3), 0)', 'Ne(sin(phi + pi/6), 0)', 'Ne(cos(phi), 0)']
- Verifier: The identity fails at 60 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at H=0.059987, I=0.388765, phi=0.0208956, theta=0.0131578: lhs=(0.99999968850, rhs=(0.38876468850) [symbolic check timed out].
- Counterexample: {'H': '0.059987', 'I': '0.388765', 'phi': '0.0208956', 'theta': '0.0131578'} → lhs (0.9999996885051796368696744871896268782, rhs (0.3887646885078510705889956371356830760, rel diff 0.6112349999
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:803894:1381147459:205

- Page: [Spectral sequence](https://en.wikipedia.org/wiki/Spectral_sequence) › Worked-out examples > 2 non-zero adjacent columns  · verdict **FAIL**, symbolic unknown
- LaTeX: `E^{\infty} = E^2`
- Context before: …The differentials on the second page have degree (-2, 1), so they are of the form $d^2_{p,q}:E^2_{p,q} \to E^2_{p-2,q+1}$ These maps are all zero since they are $d^2_{0,q}:E^2_{0,q} \to 0$ , $d^2_{1,q}:E^2_{1,q} \to 0$ hence the spectral sequence degenerates:
- Context after: . Say, it converges to $H_*$ with a filtration $0 = F_{-1} H_n \subset F_0 H_n \subset \dots \subset F_n H_n = H_n$ such that $E^{\infty}_{p, q} = F_p H_{p+q}/F_{p-1} H_{p+q}$ . Then $F_0 H_n = E^2_{0, n}$ , $F_1 H_n / F_0 H_n = E^2_{1, n -1}$ , $F_2 H_n / F_1 H_n = 0$ , $F_3 H_n / F_2 H_n = 0$ , etc. Thus, there is the exact sequence: $0 \to E^2_{…
- Translator read: `E**oo`  =  `E**2`  · notes: sides: E^{\infty}  ||  E^2
- Assumptions: domains {'E': 'positive'}; constants {}; constraints []
- Verifier: The identity fails at 33 of 33 evaluable points, a clear majority in every regime (small_positive, unit_interval, mixed_sign) (e.g. at E=0.0327277: lhs=0, rhs=0.001071102347).
- Counterexample: {'E': '0.0327277'} → lhs 0, rhs 0.00107110234729000000000000000000000000, rel diff 1.0000000000
- Regimes: small_positive 12/15 fail, 3 err, unit_interval 12/12 fail, 0 err, integers_small 0/12 fail, 12 err, mixed_sign 9/40 fail, 31 err, large 0/40 fail, 40 err

---
## wiki:en:803894:1381147459:238

- Page: [Spectral sequence](https://en.wikipedia.org/wiki/Spectral_sequence) › Worked-out examples > Wang sequence  · verdict **FAIL**, symbolic unknown
- LaTeX: `E^{n+1} = E^{\infty}`
- Context before: …Since the only non-zero differentials are on the $E^n$ -page, given by $d^n_{n,q}:E^n_{n,q} \to E^n_{0,q+n-1}$ which is $d^n_{n,q}:H_q(F) \to H_{q+n-1}(F)$ the spectral sequence converges on
- Context after: . By computing $E^{n+1}$ we get an exact sequence $0 \to E^{\infty}_{n, q-n} \to E^n_{n, q-n} \overset{d}\to E^n_{0, q-1} \to E^{\infty}_{0, q-1} \to 0.$ and written out using the homology groups, this is $0 \to E^{\infty}_{n, q-n} \to H_{q-n}(F) \overset{d}\to H_{q-1}(F) \to E^{\infty}_{0, q-1} \to 0.$ To establish what the two $E^\infty$ -terms a…
- Translator read: `E**(n + 1)`  =  `E**oo`  · notes: sides: E^{n+1}  ||  E^{\infty}
- Assumptions: domains {'E': 'positive', 'n': 'nonneg_integer'}; constants {}; constraints []
- Verifier: The identity fails at 34 of 34 evaluable points, a clear majority in every regime (small_positive, unit_interval, mixed_sign) (e.g. at E=0.542758, n=0: lhs=0.542758000000, rhs=0).
- Counterexample: {'E': '0.542758', 'n': '0'} → lhs 0.54275800000000000000000000000000000000, rhs 0, rel diff 1.0000000000
- Regimes: small_positive 12/21 fail, 9 err, unit_interval 12/12 fail, 0 err, integers_small 0/30 fail, 30 err, mixed_sign 10/40 fail, 30 err, large 0/40 fail, 40 err

---
## wiki:en:203056:1379321006:184

- Page: [Spherical harmonics](https://en.wikipedia.org/wiki/Spherical_harmonics) › Spherical harmonics in Cartesian form > Separated Cartesian form  · verdict **FAIL**, symbolic unknown
- LaTeX: `\bar{\Pi}^0_\ell(z)
= \sum_{k=0}^{\left \lfloor \ell/2\right \rfloor}
 (-1)^k 2^{-\ell} \binom{\ell}{k}\binom{2\ell-2k}{\ell} \; r^{2k}\; z^{\ell-2k}.`
- Context before: …) = \sum_{p=0}^m \binom{m}{p} x^p y^{m-p} \sin \left((m-p) \frac{\pi}{2}\right),$ and $\bar{\Pi}^m_\ell(z) = \left[\frac{(\ell-m)!}{(\ell+m)!}\right]^{1/2} \sum_{k=0}^{\left \lfloor (\ell-m)/2\right \rfloor} (-1)^k 2^{-\ell} \binom{\ell}{k}\binom{2\ell-2k}{\ell} \frac{(\ell-2k)!}{(\ell-2k-m)!} \; r^{2k}\; z^{\ell-2k-m}.$ For $m = 0$ this reduces to
- Context after: The factor $\bar{\Pi}_\ell^m(z)$ is essentially the associated Legendre polynomial $P_\ell^m(\cos\theta)$ , and the factors $(A_m \pm i B_m)$ are essentially $e^{\pm i m\varphi}$ . Examples. Using the expressions for $\bar{\Pi}_\ell^m(z)$ , $A_m(x,y)$ , and $B_m(x,y)$ listed explicitly above we obtain:…
- Translator read: `1`  =  `Sum((-1)**k*r**(2*k)*z**(ell - 2*k)*binomial(ell, k)*binomial(2*ell - 2*k, ell)/2**ell, (k, 0, floor(ell/2)))`  · notes: pre:left_right
pre:spacing
pre:trailing_punct
funcapp_rule:Pi_bar:single_atom_arg
funcapp_rule:ell:single_atom_arg
ambig:bar:Pi_bar
funcapp:Pi_bar_ell
power_of_function:Pi_bar_ell
sides: \bar{\Pi}^0_\ell(z)  ||  \sum_{k=0}^{\left \lfloor \ell/2\right \rfloor}  (-1)^k 2^{-\ell} \binom{\ell}{k}\binom{2\ell-2k}{\ell} \; r^{2k}\; z^{\ell-2k}
- Assumptions: domains {'ell': 'positive', 'r': 'nonneg', 'z': 'complex'}; constants {}; constraints []
- Verifier: The identity fails at 70 of 72 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, complex, large) (e.g. at ell=0.0983686, r=0.265713, z=0.195091: lhs=1.000000000000, rhs=0.806531380221).
- Counterexample: {'ell': '0.0983686', 'r': '0.265713', 'z': '0.195091'} → lhs 1.00000000000000000000000000000000000000, rhs 0.80653138022119105242665150994460178546, rel diff 0.1934686197
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/19 fail, 7 err, complex 12/12 fail, 0 err, large 10/12 fail, 0 err

---
## wiki:en:203056:1379321006:318

- Page: [Spherical harmonics](https://en.wikipedia.org/wiki/Spherical_harmonics) › List of spherical harmonics  · verdict **FAIL**, symbolic not_equal
- LaTeX: `Y_{0}^{0}(\theta,\varphi) = \frac{1}{2}\sqrt{\frac 1 \pi}`
- Context before: …More general spherical harmonics of degree ℓ are not necessarily those of the Laplace basis $Y_\ell^m$ , and their nodal sets can be of a fairly general kind. List of spherical harmonics. Analytic expressions for the first few orthonormalized Laplace spherical harmonics $Y_{\ell}^m : S^2 \to \Complex$ that use the Condon–Shortley phase convention:
- Context after: $\begin{align} Y_{1}^{-1}(\theta,\varphi) &= \frac{1}{2}\sqrt{\frac 3 {2\pi}} \, \sin\theta \, e^{-i\varphi} \\ Y_{1}^{0}(\theta,\varphi) &= \frac{1}{2}\sqrt{\frac 3 \pi}\, \cos\theta \\ Y_{1}^{1}(\theta,\varphi) &= \frac{-1}{2}\sqrt{\frac 3 {2\pi}}\, \sin\theta\, e^{i\varphi} \end{align}$…
- Translator read: `1`  =  `1/(2*sqrt(pi))`  · notes: funcapp_rule:Y:comma_args
funcapp:Y_0
power_of_function:Y_0
sides: Y_{0}^{0}(\theta,\varphi)  ||  \frac{1}{2}\sqrt{\frac 1 \pi}
- Assumptions: domains {}; constants {}; constraints []
- Verifier: The constant identity does not hold: both sides differ beyond 1e-8 relative error, stably at two working precisions (lhs=1.0000000000000000, rhs=0.2820947917738781).
- Counterexample: {} → lhs 1.00000000000000000000000000000000000000, rhs 0.28209479177387814347403972578038629292, rel diff 0.7179052082
- Regimes: constant 1/1 fail, 0 err

---
## wiki:en:29276:1367040217:108

- Page: [Spinor](https://en.wikipedia.org/wiki/Spinor) › Examples > Three dimensions  · verdict **FAIL**, symbolic unknown
- LaTeX: `\left[\cos\left(\frac{\theta}{2}\right) - i\sigma_3 \sin\left(\frac{\theta}{2}\right)\right]
    \sigma_3 \left[\cos\left(\frac{\theta}{2}\right) + i \sigma_3 \sin\left(\frac{\theta}{2}\right)\right] =
  \left[\cos^2\left(\frac{\theta}{2}\right) + \sin^2\left(\frac{\theta}{2}\right)\right] \sigma_3 =
  \sigma_3.`
- Context before: …corresponds to a vector rotation through an angle θ about an axis defined by a unit vector . As a special case, it is easy to see that, if , this reproduces the σ1σ2 rotation considered in the previous section; and that such rotation leaves the coefficients of vectors in the σ3 direction invariant, since
- Context after: The bivectors σ2σ3, σ3σ1 and σ1σ2 are in fact Hamilton's quaternions i, j, and k, discovered in 1843: $\begin{align} \mathbf{i} &= -\sigma_2 \sigma_3 = -i \sigma_1 \\ \mathbf{j} &= -\sigma_3 \sigma_1 = -i \sigma_2 \\ \mathbf{k} &= -\sigma_1 \sigma_2 = -i \sigma_3 \end{align}$ With the identification of the even-graded elements with the algebra $\ma…
- Translator read (piece 0): `sigma_3*(-i*sigma_3*sin(theta/2) + cos(theta/2))*(i*sigma_3*sin(theta/2) + cos(theta/2))`  =  `sigma_3*(sin(theta/2)**2 + cos(theta/2)**2)`  · notes: pre:left_right
pre:trailing_punct
hint:i_present
sides: [\cos\left(\frac{\theta}{2}\right) - i\sigma_3 \sin\left(\frac{\theta}{2}\right)\right]     \sigma_3 \left[\cos\left(\frac{\theta}{2}\right) + i \sigma_3 \sin\left(\frac{\theta}{2}\right)\right]  ||  [\cos^2\left(\frac{\theta}{2}\right) + \sin^2\left(\frac{\theta}{2}\right)\right] \sigma_3
- Translator read (piece 1): `sigma_3*(sin(theta/2)**2 + cos(theta/2)**2)`  =  `sigma_3`  · notes: pre:left_right
pre:trailing_punct
sides: [\cos^2\left(\frac{\theta}{2}\right) + \sin^2\left(\frac{\theta}{2}\right)\right] \sigma_3  ||  \sigma_3
- Assumptions: domains {'i': 'nonneg_integer', 'sigma_3': 'positive', 'theta': 'angle'}; constants {}; constraints []
- Verifier: Chain link 0: The identity fails at 60 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at i=0, sigma_3=0.0435783, theta=0.140187: lhs=0.043364545918, rhs=0.043578300000).
- Counterexample: {'i': '0', 'sigma_3': '0.0435783', 'theta': '0.140187'} → lhs 0.04336454591829978402838688161975111385, rhs 0.04357830000000000000000000000000000000, rel diff 0.0049050578
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:893559:1349131882:61

- Page: [Split-complex number](https://en.wikipedia.org/wiki/Split-complex_number) › Geometry  · verdict **FAIL**, symbolic unknown
- LaTeX: `\exp(j\theta) = \cosh(\theta) + j\sinh(\theta).`
- Context before: …lit-complex numbers z and w are said to be hyperbolic-orthogonal if . While analogous to ordinary orthogonality, particularly as it is known with ordinary complex number arithmetic, this condition is more subtle. It forms the basis for the simultaneous hyperplane concept in spacetime. The analogue of Euler's formula for the split-complex numbers is
- Context after: This formula can be derived from a power series expansion using the fact that cosh has only even powers while that for sinh has odd powers. For all real values of the hyperbolic angle θ the split-complex number has norm 1 and lies on the right branch of the unit hyperbola. Numbers such as λ have been called hyperbolic versors. Since λ has modulus 1…
- Translator read: `exp(j*theta)`  =  `j*sinh(theta) + cosh(theta)`  · notes: pre:trailing_punct
sides: \exp(j\theta)  ||  \cosh(\theta) + j\sinh(\theta)
- Assumptions: domains {'theta': 'real'}; constants {'j': 'I'}; constraints []
- Verifier: The identity fails at 59 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at theta=0.0552941: lhs=(0.99847167070, rhs=(1.00152910828).
- Counterexample: {'theta': '0.0552941'} → lhs (0.9984716707097365375404764626074686719, rhs (1.0015291082839373528050479408417887737, rel diff 0.0030486405
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 11/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:29208:1380705882:95

- Page: [Square root](https://en.wikipedia.org/wiki/Square_root) › Square roots of negative and complex numbers > Notes  · verdict **FAIL**, symbolic not_equal
- LaTeX: `\sqrt{1} = -1,`
- Context before: …square root that contains $\sqrt{1}\cdot\sqrt{-1}.$ The left-hand side becomes either $\sqrt{-1} \cdot \sqrt{-1}=i \cdot i=-1$ if the branch includes +i or $\sqrt{-1} \cdot \sqrt{-1}=(-i) \cdot (-i)=-1$ if the branch includes −i, while the right-hand side becomes $\sqrt{\left(-1\right)\cdot\left(-1\right)} = \sqrt{1} = -1,$ where the last equality,
- Context after: is a consequence of the choice of branch in the redefinition of √. nth roots and polynomial roots. The definition of a square root of $x$ as a number $y$ such that $y^2 = x$ has been generalized in the following way. A cube root of $x$ is a number $y$ such that $y^3 = x$ ; it is denoted $\sqrt[3]x.$ If n is an integer greater than two, a n-th root…
- Translator read: `1`  =  `-1`  · notes: pre:trailing_punct
sides: \sqrt{1}  ||  -1
- Assumptions: domains {}; constants {}; constraints []
- Verifier: The constant identity does not hold: both sides differ beyond 1e-8 relative error, stably at two working precisions (lhs=1.0000000000000000, rhs=-1.000000000000000).
- Counterexample: {} → lhs 1.00000000000000000000000000000000000000, rhs -1.0000000000000000000000000000000000000, rel diff 2.0000000000
- Regimes: constant 1/1 fail, 0 err

---
## wiki:en:29208:1380705882:94

- Page: [Square root](https://en.wikipedia.org/wiki/Square_root) › Square roots of negative and complex numbers > Notes  · verdict **FAIL**, symbolic not_equal
- LaTeX: `\sqrt{\left(-1\right)\cdot\left(-1\right)} = \sqrt{1} = -1,`
- Context before: …o longer represents the principal square root (see above) but selects a branch for the square root that contains $\sqrt{1}\cdot\sqrt{-1}.$ The left-hand side becomes either $\sqrt{-1} \cdot \sqrt{-1}=i \cdot i=-1$ if the branch includes +i or $\sqrt{-1} \cdot \sqrt{-1}=(-i) \cdot (-i)=-1$ if the branch includes −i, while the right-hand side becomes
- Context after: where the last equality, $\sqrt{1} = -1,$ is a consequence of the choice of branch in the redefinition of √. nth roots and polynomial roots. The definition of a square root of $x$ as a number $y$ such that $y^2 = x$ has been generalized in the following way. A cube root of $x$ is a number $y$ such that $y^3 = x$ ; it is denoted $\sqrt[3]x.$ If n is…
- Translator read (piece 0): `1`  =  `1`  · notes: pre:left_right
pre:trailing_punct
sides: \sqrt{\left(-1\right)\cdot\left(-1\right)}  ||  \sqrt{1}
- Translator read (piece 1): `1`  =  `-1`  · notes: pre:left_right
pre:trailing_punct
sides: \sqrt{1}  ||  -1
- Assumptions: domains {}; constants {}; constraints []
- Verifier: Chain link 1: The constant identity does not hold: both sides differ beyond 1e-8 relative error, stably at two working precisions (lhs=1.0000000000000000, rhs=-1.000000000000000).
- Counterexample: {} → lhs 1.00000000000000000000000000000000000000, rhs -1.0000000000000000000000000000000000000, rel diff 2.0000000000
- Regimes: constant 1/1 fail, 0 err

---
## wiki:en:29208:1380705882:90

- Page: [Square root](https://en.wikipedia.org/wiki/Square_root) › Square roots of negative and complex numbers > Notes  · verdict **FAIL**, symbolic not_equal
- LaTeX: `\begin{align}
-1 &= i \cdot i \\
&= \sqrt{-1} \cdot \sqrt{-1} \\
&= \sqrt{\left(-1\right)\cdot\left(-1\right)} \\
&= \sqrt{1} \\
&= 1.
\end{align}`
- Context before: …or the principal square root: ) This equality is valid only when $\theta_z\ne\pi$ A similar problem appears with other complex functions with branch cuts, e.g., the complex logarithm and the relations or which are not true in general. Wrongly assuming one of these laws underlies several faulty "proofs", for instance the following one showing that :
- Context after: The third equality cannot be justified (see invalid proof). It can be made to hold by changing the meaning of √ so that this no longer represents the principal square root (see above) but selects a branch for the square root that contains $\sqrt{1}\cdot\sqrt{-1}.$ The left-hand side becomes either $\sqrt{-1} \cdot \sqrt{-1}=i \cdot i=-1$ if the bra…
- Translator read (piece 0): `-1`  =  `i**2`  · notes: pre:left_right
pre:env_align
pre:row_continues_chain
pre:trailing_punct
hint:i_squared
sides: -1  ||  i \cdot i
- Translator read (piece 1): `i**2`  =  `-1`  · notes: pre:left_right
pre:env_align
pre:row_continues_chain
pre:trailing_punct
hint:i_squared
sides: i \cdot i  ||  \sqrt{-1} \cdot \sqrt{-1}
- Translator read (piece 2): `-1`  =  `1`  · notes: pre:left_right
pre:env_align
pre:row_continues_chain
pre:trailing_punct
sides: \sqrt{-1} \cdot \sqrt{-1}  ||  \sqrt{\left(-1\right)\cdot\left(-1\right)}
- Translator read (piece 3): `1`  =  `1`  · notes: pre:left_right
pre:env_align
pre:row_continues_chain
pre:trailing_punct
sides: \sqrt{\left(-1\right)\cdot\left(-1\right)}  ||  \sqrt{1}
- Translator read (piece 4): `1`  =  `1`  · notes: pre:left_right
pre:env_align
pre:row_continues_chain
pre:trailing_punct
sides: \sqrt{1}  ||  1
- Assumptions: domains {}; constants {'i': 'I'}; constraints []
- Verifier: Chain link 2: The constant identity does not hold: both sides differ beyond 1e-8 relative error, stably at two working precisions (lhs=-1.000000000000000, rhs=1.0000000000000000).
- Counterexample: {} → lhs -1.0000000000000000000000000000000000000, rhs 1.00000000000000000000000000000000000000, rel diff 2.0000000000
- Regimes: constant 1/1 fail, 0 err

---
## wiki:en:2091823:1380348958:58

- Page: [Stiff equation](https://en.wikipedia.org/wiki/Stiff_equation) › History and origins of a mathematical characterization  · verdict **FAIL**, symbolic not_equal
- LaTeX: `-2 \leq h\lambda \leq 0`
- Context before: …)^nx_0 + \sum_{k=0}^{n-1} \left(1+h\lambda\right)^{n-k-1} h\big(\dot g(t_k) - \lambda g(t_k)\big) \, .$ The impediment is clearly visible: positive powers of the factor $1 + h\lambda$ produce exponential growth (numerical instability) unless we impose the stability condition $|1+h\lambda| \leq 1$ . Since $\lambda$ is real and negative, this implies
- Context after: . Thus the explicit Euler method cannot use step sizes adapted to the regularity of $g(t)$ . Instead the total number of steps to complete the integration, $N = T/h \sim T|\lambda|$ , becomes extremely large. Efficiency is inversely proportional to stiffness as quantified by the product $T|\lambda| \gg 1$ . As a consequence the explicit Euler metho…
- Translator read (piece 0): `-2`  <=  `h*lambda`  · notes: sides: -2  ||  h\lambda
- Translator read (piece 1): `h*lambda`  <=  `0`  · notes: sides: h\lambda  ||  0
- Assumptions: domains {'h': 'positive', 'lambda': 'positive'}; constants {}; constraints []
- Verifier: Chain link 1: The inequality fails at 60 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at h=0.115344, lambda=0.0539731: lhs=0.006225473246, rhs=0).
- Counterexample: {'h': '0.115344', 'lambda': '0.0539731'} → lhs 0.00622547324640000000000000000000000000, rhs 0, rel diff 1.0000000000
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:2091823:1380348958:56

- Page: [Stiff equation](https://en.wikipedia.org/wiki/Stiff_equation) › History and origins of a mathematical characterization  · verdict **FAIL**, symbolic not_equal
- LaTeX: `|1+h\lambda| \leq 1`
- Context before: …s the numerical solution (on integrated form) $x_n = \left(1+h\lambda\right)^nx_0 + \sum_{k=0}^{n-1} \left(1+h\lambda\right)^{n-k-1} h\big(\dot g(t_k) - \lambda g(t_k)\big) \, .$ The impediment is clearly visible: positive powers of the factor $1 + h\lambda$ produce exponential growth (numerical instability) unless we impose the stability condition
- Context after: . Since $\lambda$ is real and negative, this implies $-2 \leq h\lambda \leq 0$ . Thus the explicit Euler method cannot use step sizes adapted to the regularity of $g(t)$ . Instead the total number of steps to complete the integration, $N = T/h \sim T|\lambda|$ , becomes extremely large. Efficiency is inversely proportional to stiffness as quantifie…
- Translator read: `Abs(h*lambda + 1)`  <=  `1`  · notes: sides: |1+h\lambda|  ||  1
- Assumptions: domains {'h': 'positive', 'lambda': 'positive'}; constants {}; constraints []
- Verifier: The inequality fails at 60 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at h=0.0754477, lambda=0.081015: lhs=1.006112395415, rhs=1.000000000000).
- Counterexample: {'h': '0.0754477', 'lambda': '0.081015'} → lhs 1.00611239541550000000000000000000000000, rhs 1.00000000000000000000000000000000000000, rel diff 0.0060752610
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:2091823:1380348958:69

- Page: [Stiff equation](https://en.wikipedia.org/wiki/Stiff_equation) › History and origins of a mathematical characterization  · verdict **FAIL**, symbolic not_equal
- LaTeX: `{\mathrm {Re}}\,\lambda < 0`
- Context before: …ites numerical instability. If instead the implicit Euler method is used, the numerical solution becomes $x_n = \left(1-h\lambda\right)^{-n}x_0 + \sum_{k=0}^{n-1} \left(1-h\lambda\right)^{k-n} h\big(\dot g(t_{k+1}) - \lambda g(t_{k+1})\big) \, .$ Here, the stability requirement is $|1-h\lambda|^{-1} \leq 1$ , which is satisfied for all $h > 0$ when
- Context after: , no matter how large $h|\lambda|$ is. A minor issue is that in practice one needs to resolve the transient (this may initially call for a short step size), but once it has decayed, one can use "large" step sizes, in the sense that $h$ is adapted to the regularity of $g(t)$ , irrespective of the magnitude of $|h\lambda|$ . Of the two methods above,…
- Translator read: `Re*lambda`  <  `0`  · notes: pre:spacing
function_name_as_symbol:Re
sides: {\mathrm {Re}}\,\lambda  ||  0
- Assumptions: domains {'Re': 'positive', 'lambda': 'positive'}; constants {}; constraints []
- Verifier: The inequality fails at 60 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at Re=0.192572, lambda=0.271127: lhs=0.052211468644, rhs=0).
- Counterexample: {'Re': '0.192572', 'lambda': '0.271127'} → lhs 0.05221146864400000000000000000000000000, rhs 0, rel diff 1.0000000000
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:2091823:1380348958:183

- Page: [Stiff equation](https://en.wikipedia.org/wiki/Stiff_equation) › Modern characterization: The stiffness indicator  · verdict **FAIL**, symbolic not_equal
- LaTeX: `M_2[f] < 0`
- Context before: …- I\big)(u) = -\psi \, ,$ the uniform monotonicity theorem applies: the equation has a unique solution if the map $\gamma hf - I$ is (negative) monotone, i.e., if $M_2[\gamma hf - I] < 0$ . Since $M_2[\gamma hf - I] < 0 \quad \Leftrightarrow \quad M_2[\gamma hf] < 1 \, ,$ this condition is usually satisfied by a fair margin in stiff computation. If
- Context after: , it is satisfied for all $h>0$ , but if $M_2[f] > 0$ , it may require a minor step size restriction. In the Shampine criterion, as well as in the stiffness indicator, it holds that ${\frac {m_2[\gamma hf] + M_2[\gamma hf]}{2}} \, = \, \gamma h\!\cdot\!s_2[f] \ll -1 \,,$ where $m_2[\gamma hf] \ll -1$ , and where $M_2[\gamma hf]$ is moderate if it i…
- Translator read: `M_2*f`  <  `0`  · notes: sides: M_2[f]  ||  0
- Assumptions: domains {'M_2': 'positive', 'f': 'positive'}; constants {}; constraints []
- Verifier: The inequality fails at 60 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at M_2=0.116678, f=0.182789: lhs=0.021327454942, rhs=0).
- Counterexample: {'M_2': '0.116678', 'f': '0.182789'} → lhs 0.02132745494200000000000000000000000000, rhs 0, rel diff 1.0000000000
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:2091823:1380348958:214

- Page: [Stiff equation](https://en.wikipedia.org/wiki/Stiff_equation) › A simplified stiffness indicator  · verdict **FAIL**, symbolic not_equal
- LaTeX: `\,\tau[A] < 0\,`
- Context before: …of the flow can now be rewritten ${\mathrm D}_t\, \delta\big[{\mathrm e}^{tA}\big] \, = \, \tau[A] \cdot \delta\big[{\mathrm e}^{tA}\big] \, .$ Hence $\delta\big[{\mathrm e}^{tA}\big] \, = \, {\mathrm e}^{t\,\tau[A]}\,,$ expressing that an initial (linear) phase volume changes by a factor $\,\delta\big[{\mathrm e}^{tA}\big]\,$ over a time $t$ . If
- Context after: , phase volume is compressed by the flow $\,{\mathrm e}^{tA}\,$ for $t\geq 0$ . It follows that $\,\tau[A] \leq 0\,$ is a necessary condition for stability. (Compare the sufficient criterion $\,M_2[A] \leq 0\,$ for the stability of the zero solution.) Shampine's characterization of stiffness, in terms of strongly unstable solutions in reverse time,…
- Translator read: `A*tau`  <  `0`  · notes: pre:spacing
pre:trailing_punct
sides: \tau[A]  ||  0
- Assumptions: domains {'A': 'positive', 'tau': 'positive'}; constants {}; constraints []
- Verifier: The inequality fails at 60 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at A=0.0742824, tau=0.0574865: lhs=0.004270235187, rhs=0).
- Counterexample: {'A': '0.0742824', 'tau': '0.0574865'} → lhs 0.00427023518760000000000000000000000000, rhs 0, rel diff 1.0000000000
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:2091823:1380348958:217

- Page: [Stiff equation](https://en.wikipedia.org/wiki/Stiff_equation) › A simplified stiffness indicator  · verdict **FAIL**, symbolic not_equal
- LaTeX: `\,\tau[A] \leq 0\,`
- Context before: …Hence $\delta\big[{\mathrm e}^{tA}\big] \, = \, {\mathrm e}^{t\,\tau[A]}\,,$ expressing that an initial (linear) phase volume changes by a factor $\,\delta\big[{\mathrm e}^{tA}\big]\,$ over a time $t$ . If $\,\tau[A] < 0\,$ , phase volume is compressed by the flow $\,{\mathrm e}^{tA}\,$ for $t\geq 0$ . It follows that
- Context after: is a necessary condition for stability. (Compare the sufficient criterion $\,M_2[A] \leq 0\,$ for the stability of the zero solution.) Shampine's characterization of stiffness, in terms of strongly unstable solutions in reverse time, can be written as $\,T\!\cdot \tau[-A] \gg 1\,$ , which, due to the odd parity of the trace, is equivalent to the st…
- Translator read: `A*tau`  <=  `0`  · notes: pre:spacing
pre:trailing_punct
sides: \tau[A]  ||  0
- Assumptions: domains {'A': 'positive', 'tau': 'positive'}; constants {}; constraints []
- Verifier: The inequality fails at 60 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at A=0.0776284, tau=0.123238: lhs=0.009566768759, rhs=0).
- Counterexample: {'A': '0.0776284', 'tau': '0.123238'} → lhs 0.00956676875920000000000000000000000000, rhs 0, rel diff 1.0000000000
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:2091823:1380348958:218

- Page: [Stiff equation](https://en.wikipedia.org/wiki/Stiff_equation) › A simplified stiffness indicator  · verdict **FAIL**, symbolic not_equal
- LaTeX: `\,M_2[A] \leq 0\,`
- Context before: …expressing that an initial (linear) phase volume changes by a factor $\,\delta\big[{\mathrm e}^{tA}\big]\,$ over a time $t$ . If $\,\tau[A] < 0\,$ , phase volume is compressed by the flow $\,{\mathrm e}^{tA}\,$ for $t\geq 0$ . It follows that $\,\tau[A] \leq 0\,$ is a necessary condition for stability. (Compare the sufficient criterion
- Context after: for the stability of the zero solution.) Shampine's characterization of stiffness, in terms of strongly unstable solutions in reverse time, can be written as $\,T\!\cdot \tau[-A] \gg 1\,$ , which, due to the odd parity of the trace, is equivalent to the stiffness condition $T\!\cdot \tau[A] \ll -1$ . These observations, concepts and constructions p…
- Translator read: `A*M_2`  <=  `0`  · notes: pre:spacing
pre:trailing_punct
sides: M_2[A]  ||  0
- Assumptions: domains {'A': 'positive', 'M_2': 'positive'}; constants {}; constraints []
- Verifier: The inequality fails at 60 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at A=0.116626, M_2=0.257948: lhs=0.030083443448, rhs=0).
- Counterexample: {'A': '0.116626', 'M_2': '0.257948'} → lhs 0.03008344344800000000000000000000000000, rhs 0, rel diff 1.0000000000
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:2091823:1380348958:309

- Page: [Stiff equation](https://en.wikipedia.org/wiki/Stiff_equation) › Methods and software for stiff equations  · verdict **FAIL**, symbolic not_equal
- LaTeX: `\,M_2[hf] \leq 0\,`
- Context before: …\leq 0 \, \Rightarrow \, \|R(hA)\|_2 \leq 1 \,,$ i.e., if $A$ is negative definite, then the method produces a contractive recursion. (This is a variant of the von Neumann inequality.) Unfortunately, this only carries over to nonlinear problems under additional conditions. B-stable Runge-Kutta methods are a subset of A-stable methods, such that if
- Context after: in a nonlinear problem, then the method produces a contractive recursion. Other special stability requirements are also common, such as L-stability. This is another subset of A-stable method, with the additional requirement $\,R(\infty) = 0\,$ for improved damping of eigenmodes for which $\,{\mathrm {Re}}\,h\lambda \ll -1$ . Because implicit Runge-…
- Translator read: `M_2*f*h`  <=  `0`  · notes: pre:spacing
pre:trailing_punct
sides: M_2[hf]  ||  0
- Assumptions: domains {'M_2': 'positive', 'f': 'positive', 'h': 'positive'}; constants {}; constraints []
- Verifier: The inequality fails at 60 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at M_2=0.0942386, f=0.129742, h=0.12188: lhs=0.001490190737, rhs=0).
- Counterexample: {'M_2': '0.0942386', 'f': '0.129742', 'h': '0.12188'} → lhs 0.00149019073729345600000000000000000000, rhs 0, rel diff 1.0000000000
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err

---
## wiki:en:61229:1379891258:3

- Page: [Straightedge and compass construction](https://en.wikipedia.org/wiki/Straightedge_and_compass_construction) › Constructible points > Relation to complex arithmetic  · verdict **FAIL**, symbolic unknown
- LaTeX: `\mathrm{Re}(z)=\frac{z+\bar z}{2}\;`
- Context before: …ible using straightedge and compass from such a set of ratios is precisely the smallest field containing the original ratios and closed under taking complex conjugates and square roots. For example, the real part, imaginary part and modulus of a point or ratio z (taking one of the two viewpoints above) are constructible as these may be expressed as
- Context after: $\mathrm{Im}(z)=\frac{z-\bar z}{2i}\;$ $\left | z \right | = \sqrt{z \bar z}.\;$ Doubling the cube and trisection of an angle (except for special angles such as any φ such that φ/(2π)) is a rational number with denominator not divisible by 3) require ratios which are the solution to cubic equations, while squaring the circle requires a transcendent…
- Translator read: `re(z)`  =  `z/2 + z_bar/2`  · notes: pre:spacing
pre:trailing_punct
ambig:bar:z_bar
sides: \mathrm{Re}(z)  ||  \frac{z+\bar z}{2}
- Assumptions: domains {'z': 'complex', 'z_bar': 'complex'}; constants {}; constraints []
- Verifier: The identity fails at 72 of 72 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, complex, large) (e.g. at z=0.125452, z_bar=0.0422567: lhs=0.125452000000, rhs=0.083854350000).
- Counterexample: {'z': '0.125452', 'z_bar': '0.0422567'} → lhs 0.12545200000000000000000000000000000000, rhs 0.08385435000000000000000000000000000000, rel diff 0.3315821987
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, complex 12/12 fail, 0 err, large 12/12 fail, 0 err
