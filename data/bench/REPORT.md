# formulaci bench report

Generated 2026-10-21 14:12:07 · total runtime 536.4 s · stages requested: translate, semantics, verify

## Stage availability

| set | formulas | translate | semantics | verify | seconds |
|---|---|---|---|---|---|
| synthetic | 1592 | ok (7.81s) | ok (12.08s) | ok (490.79s) | 510.8 |
| lacast | 95 | ok (6.28s) | ok (0.29s) | ok (18.86s) | 25.42 |

## Synthetic sets (known-good identities + injected mutations)

- known-good: 272 formulas; mutated: 1320 formulas
- translate `ok` rate: known-good 100.0%, mutated 100.0%
- semantics checkable rate (of translated): known-good 99.6%, mutated 98.9%; end to end: 99.6% / 98.9%
- **precision 100.0%** (TP 1082, FP 0); **recall 82.0%** end to end, 83.5% of mutated formulas that reached a PASS/FAIL/INCONCLUSIVE verdict
- recall on mutations of identities whose known-good form PASSed: 83.5% (n=1282)
- known-good verdicts: PASS 263, FAIL 0, INCONCLUSIVE 5, SKIP 4, MISSING 0
- mutated verdicts: PASS 2, FAIL 1082, INCONCLUSIVE 212, SKIP 24, MISSING 0
- INCONCLUSIVE rate: known-good 1.8%, mutated 16.1%

### Per category

| category | n good | n mutated | translate ok (good) | translate ok (mut) | checkable (good) | good PASS | good FAIL | good INCONCL. | mut FAIL (recall) | mut INCONCL. | precision |
|---|---|---|---|---|---|---|---|---|---|---|---|
| algebra | 12 | 62 | 100.0% | 100.0% | 100.0% | 12 | 0 | 0 | 59 (95.2%) | 4.8% | 100.0% |
| binomial | 18 | 94 | 100.0% | 100.0% | 100.0% | 18 | 0 | 0 | 67 (71.3%) | 28.7% | 100.0% |
| complex | 7 | 38 | 100.0% | 100.0% | 100.0% | 7 | 0 | 0 | 35 (92.1%) | 7.9% | 100.0% |
| derivatives | 20 | 79 | 100.0% | 100.0% | 100.0% | 20 | 0 | 0 | 71 (89.9%) | 7.6% | 100.0% |
| exp_log | 19 | 62 | 100.0% | 100.0% | 100.0% | 19 | 0 | 0 | 60 (96.8%) | 3.2% | 100.0% |
| finite_series | 18 | 113 | 100.0% | 100.0% | 100.0% | 18 | 0 | 0 | 100 (88.5%) | 8.0% | 100.0% |
| gamma_beta | 20 | 84 | 100.0% | 100.0% | 100.0% | 17 | 0 | 0 | 68 (81.0%) | 9.5% | 100.0% |
| hyperbolic | 23 | 115 | 100.0% | 100.0% | 100.0% | 23 | 0 | 0 | 76 (66.1%) | 33.9% | 100.0% |
| inequalities | 24 | 59 | 100.0% | 100.0% | 100.0% | 24 | 0 | 0 | 22 (37.3%) | 61.0% | 100.0% |
| infinite_series | 21 | 122 | 100.0% | 100.0% | 95.2% | 20 | 0 | 0 | 88 (72.1%) | 23.8% | 100.0% |
| integrals | 22 | 119 | 100.0% | 100.0% | 100.0% | 22 | 0 | 0 | 108 (90.8%) | 8.4% | 100.0% |
| probability | 20 | 119 | 100.0% | 100.0% | 100.0% | 17 | 0 | 3 | 93 (78.1%) | 18.5% | 100.0% |
| trig | 39 | 213 | 100.0% | 100.0% | 100.0% | 39 | 0 | 0 | 210 (98.6%) | 0.9% | 100.0% |
| zeta | 9 | 41 | 100.0% | 100.0% | 100.0% | 7 | 0 | 2 | 25 (61.0%) | 39.0% | 100.0% |

### Per mutation type

| mutation | n | translate ok | checkable | FAIL (recall) | recall given verified | PASS (missed) | INCONCL. | SKIP | MISSING |
|---|---|---|---|---|---|---|---|---|---|
| dropped_factor | 151 | 100.0% | 98.7% | 125 (82.8%) | 84.5% | 0 | 23 | 3 | 0 |
| exponent_pm1 | 165 | 100.0% | 100.0% | 149 (90.3%) | 90.3% | 0 | 16 | 0 | 0 |
| missing_term | 182 | 100.0% | 95.6% | 136 (74.7%) | 79.1% | 0 | 36 | 10 | 0 |
| num_den_swap | 141 | 100.0% | 100.0% | 110 (78.0%) | 78.6% | 0 | 30 | 1 | 0 |
| off_by_one | 83 | 100.0% | 98.8% | 64 (77.1%) | 78.0% | 0 | 18 | 1 | 0 |
| sign_flip | 272 | 100.0% | 99.6% | 238 (87.5%) | 88.8% | 0 | 30 | 4 | 0 |
| swapped_symbols | 116 | 100.0% | 100.0% | 86 (74.1%) | 74.1% | 0 | 30 | 0 | 0 |
| wrong_constant | 210 | 100.0% | 98.6% | 174 (82.9%) | 84.9% | 2 | 29 | 5 | 0 |

### Per translator status

| translate status | n good | n mutated | good FAIL | mut FAIL | mut INCONCL. |
|---|---|---|---|---|---|
| ok | 272 | 1320 | 0 | 1082 | 212 |

### False positives (known-good formulas that got FAIL): 0


### Missed mutations: 238 not flagged (2 PASS, 212 INCONCLUSIVE, 24 SKIP/MISSING)

Mutations judged PASS (the worst kind of miss):

- `bench:mut:0157:wrong_constant` [wrong_constant: 1->e] `\arctan x = \sum_{n=0}^{\infty} \frac{(-1)^{n} x^{2n + 1}}{2n + e}` — Holds at all 12 integer sample points but not at non-integers, so it is an integer-only identity whose integer domain was not stated.
- `bench:mut:0162:wrong_constant` [wrong_constant: 1->e] `\ln(1 + x) = \sum_{n=1}^{\infty} \frac{(-e)^{n+1} x^{n}}{n} \quad |x| < 1` — Holds at all 12 integer sample points but not at non-integers, so it is an integer-only identity whose integer domain was not stated.

The full missed list (with reasons) is in `metrics.json` → `synthetic.missed_mutations`.

## LaCASt Wikipedia gold set (95 hand-evaluated formulas)

The LaCASt human labels grade *translation* correctness (semantic LaTeX / Mathematica / Maple),
not mathematical truth; verify FAILs here are leads for review, not scored false positives.

- formulas: 95; translate ok: 40.0%; checkable: 6.3% end to end
- verdicts: PASS 2, FAIL 2, INCONCLUSIVE 2, SKIP 89, MISSING 0

| LaCASt human label | our translate status counts |
|---|---|
| human_mathematica=correct | not_checkable: 5, ok: 17, partial: 1, unparsed: 1 |
| human_mathematica=none | not_checkable: 14, ok: 1, unparsed: 3 |
| human_mathematica=wrong | not_checkable: 24, ok: 20, partial: 3, unparsed: 6 |
| human_semantic_latex=correct | not_checkable: 16, ok: 27, partial: 3, unparsed: 2 |
| human_semantic_latex=wrong | not_checkable: 27, ok: 11, partial: 1, unparsed: 8 |

FAIL verdicts to review:

- `lacast:gold:016` (Trigonometric integral) `\operatorname{Si}(ix) = i\operatorname{Shi}(x)` — The identity fails at 55 of 60 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, large) (e.g. at i=1, x=0.950562: lhs=0.904119241841, rhs=0.999592054218).
- `lacast:gold:092` (Ince equation) `w^{\prime\prime}+\xi\sin(2z)w^{\prime}+(\eta-p\xi\cos(2z))w=0. ` — The identity fails at 72 of 72 evaluable points, a clear majority in every regime (small_positive, unit_interval, integers_small, mixed_sign, complex, large) (e.g. at eta=0.612903, p=0.76285, w=0.0348903, w_prime=0.522981, w_prime_prime=0.605665, xi=0.0741549, z=0.136218: lhs=0.635583743214, rhs=0).

