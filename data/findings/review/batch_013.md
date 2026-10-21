# Review batch 013 — 2 items

For each item answer with one JSON line (Finding schema): {"formula_id": ..., "verdict": "FAIL", "review": {"status": "confirmed_error"|"false_positive"|"ambiguous", "reviewer": "<name>", "notes": "<why, one or two sentences>"}, "suggested_fix": "<corrected LaTeX or null>", "evidence": "<independent source or derivation>"}


---
## wiki:en:28479408:1365260495:72

- Page: [Wirtinger derivatives](https://en.wikipedia.org/wiki/Wirtinger_derivatives) › Basic properties > Conjugation  · verdict **FAIL**, symbolic not_equal
- LaTeX: `i=1,\dots,n`
- Context before: …Conjugation. If $f\in C^1(\Omega),$ then for
- Context after: the following equalities hold $\begin{align} \overline{\frac{\partial f}{\partial z_i}} &= \overline{\Big(\frac{\partial f}{\partial z_i}\Big)} =\frac{\partial \bar{f}}{\partial \bar{z}_i} \\ \overline{\frac{\partial f}{\partial \bar{z}_i}} &= \overline{\Big(\frac{\partial f}{\partial \bar{z}_i}\Big)} =\frac{\partial \bar{f}}{\partial z_i} \end{ali…
- Translator read: `i`  =  `1`  · notes: cond: \dots,n
hint:i_present
sides: i  ||  1
- Assumptions: domains {}; constants {'i': 'I'}; constraints []
- Verifier: The constant identity does not hold: both sides differ beyond 1e-8 relative error, stably at two working precisions (lhs=(0.0 + 1.0j), rhs=1.0000000000000000).
- Counterexample: {} → lhs (0.0 + 1.0j), rhs 1.00000000000000000000000000000000000000, rel diff 1.4142135623
- Regimes: constant 1/1 fail, 0 err

---
## wiki:en:672202:1381246594:17

- Page: [Yang–Mills theory](https://en.wikipedia.org/wiki/Yang%E2%80%93Mills_theory) › Mathematical overview  · verdict **FAIL**, symbolic unknown
- LaTeX: `\ F_{\mu\nu}=T^aF^a_{\mu\nu}\ ,`
- Context before: …nents is trivial for a indices (e.g. $\ f^{abc} = f_{abc}\$ ), whereas for μ and ν it is nontrivial, corresponding e.g. to the usual Lorentz signature, $\ \eta_{\mu \nu } = {\rm diag}(+---) ~.$ From the given Lagrangian one can derive the equations of motion given by $\ \partial^\mu F_{\mu\nu}^a + g\ f^{abc}\ A^{\mu b}\ F_{\mu\nu}^c = 0 ~.$ Putting
- Context after: these can be rewritten as $\ \left( D^\mu F_{\mu\nu} \right)^a = 0 ~.$ A Bianchi identity holds $\ \left( D_\mu\ F_{\nu \kappa} \right)^a + \left( D_\kappa\ F_{\mu \nu} \right)^a + \left( D_\nu\ F_{\kappa \mu} \right)^a = 0\$ which is equivalent to the Jacobi identity…
- Translator read: `F_munu`  =  `F_munu**a*T**a`  · notes: pre:spacing
pre:trailing_punct
sides: F_{\mu\nu}  ||  T^aF^a_{\mu\nu}
- Assumptions: domains {'F_munu': 'positive', 'T': 'positive', 'a': 'real'}; constants {}; constraints []
- Verifier: The identity fails at 60 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at F_munu=0.0534095, T=0.381161, a=0.0580631: lhs=0.053409500000, rhs=0.797626262294).
- Counterexample: {'F_munu': '0.0534095', 'T': '0.381161', 'a': '0.0580631'} → lhs 0.05340950000000000000000000000000000000, rhs 0.79762626229404321079858157285099797399, rel diff 0.9330394414
- Regimes: small_positive 12/12 fail, 0 err, unit_interval 12/12 fail, 0 err, integers_small 12/12 fail, 0 err, mixed_sign 12/12 fail, 0 err, large 12/12 fail, 0 err
