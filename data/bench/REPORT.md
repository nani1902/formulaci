# formulaci bench report

Generated 2026-10-21 23:04:55 · total runtime 395.86 s · stages requested: translate, semantics, verify

## Stage availability

| set | formulas | translate | semantics | verify | seconds |
|---|---|---|---|---|---|
| synthetic | 1592 | ok (1.81s) | ok (5.95s) | ok (367.4s) | 375.17 |
| lacast | 95 | ok (1.35s) | ok (0.25s) | ok (19.0s) | 20.59 |

## Synthetic sets (known-good identities + injected mutations)

- known-good: 272 formulas; mutated: 1320 formulas
- translate `ok` rate: known-good 100.0%, mutated 99.8%
- semantics checkable rate (of translated): known-good 97.4%, mutated 95.8%; end to end: 97.4% / 95.5%
- **precision 100.0%** (TP 1047, FP 0); **recall 79.3%** end to end, 83.5% of mutated formulas that reached a PASS/FAIL/INCONCLUSIVE verdict
- recall on mutations of identities whose known-good form PASSed: 81.3% (n=1279)
- known-good verdicts: PASS 259, FAIL 0, INCONCLUSIVE 3, SKIP 10, MISSING 0
- mutated verdicts: PASS 0, FAIL 1047, INCONCLUSIVE 207, SKIP 66, MISSING 0
- INCONCLUSIVE rate: known-good 1.1%, mutated 15.7%

### Per category

| category | n good | n mutated | translate ok (good) | translate ok (mut) | checkable (good) | good PASS | good FAIL | good INCONCL. | mut FAIL (recall) | mut INCONCL. | precision |
|---|---|---|---|---|---|---|---|---|---|---|---|
| algebra | 12 | 62 | 100.0% | 98.4% | 91.7% | 11 | 0 | 0 | 58 (93.5%) | 0.0% | 100.0% |
| binomial | 18 | 94 | 100.0% | 100.0% | 100.0% | 18 | 0 | 0 | 62 (66.0%) | 33.0% | 100.0% |
| complex | 7 | 38 | 100.0% | 100.0% | 100.0% | 7 | 0 | 0 | 36 (94.7%) | 5.3% | 100.0% |
| derivatives | 20 | 79 | 100.0% | 98.7% | 100.0% | 20 | 0 | 0 | 73 (92.4%) | 5.1% | 100.0% |
| exp_log | 19 | 62 | 100.0% | 100.0% | 89.5% | 17 | 0 | 0 | 55 (88.7%) | 6.5% | 100.0% |
| finite_series | 18 | 113 | 100.0% | 100.0% | 100.0% | 18 | 0 | 0 | 101 (89.4%) | 7.1% | 100.0% |
| gamma_beta | 20 | 84 | 100.0% | 100.0% | 100.0% | 16 | 0 | 1 | 66 (78.6%) | 5.9% | 100.0% |
| hyperbolic | 23 | 115 | 100.0% | 100.0% | 100.0% | 23 | 0 | 0 | 71 (61.7%) | 37.4% | 100.0% |
| inequalities | 24 | 59 | 100.0% | 100.0% | 91.7% | 22 | 0 | 0 | 22 (37.3%) | 50.8% | 100.0% |
| infinite_series | 21 | 122 | 100.0% | 100.0% | 90.5% | 19 | 0 | 0 | 77 (63.1%) | 30.3% | 100.0% |
| integrals | 22 | 119 | 100.0% | 100.0% | 100.0% | 22 | 0 | 0 | 107 (89.9%) | 7.6% | 100.0% |
| probability | 20 | 119 | 100.0% | 99.2% | 100.0% | 20 | 0 | 0 | 96 (80.7%) | 10.9% | 100.0% |
| trig | 39 | 213 | 100.0% | 100.0% | 100.0% | 39 | 0 | 0 | 199 (93.4%) | 2.4% | 100.0% |
| zeta | 9 | 41 | 100.0% | 100.0% | 100.0% | 7 | 0 | 2 | 24 (58.5%) | 39.0% | 100.0% |

### Per mutation type

| mutation | n | translate ok | checkable | FAIL (recall) | recall given verified | PASS (missed) | INCONCL. | SKIP | MISSING |
|---|---|---|---|---|---|---|---|---|---|
| dropped_factor | 151 | 100.0% | 93.4% | 119 (78.8%) | 85.0% | 0 | 21 | 11 | 0 |
| exponent_pm1 | 165 | 100.0% | 98.2% | 147 (89.1%) | 90.7% | 0 | 15 | 3 | 0 |
| missing_term | 182 | 98.4% | 89.9% | 125 (68.7%) | 78.1% | 0 | 35 | 22 | 0 |
| num_den_swap | 141 | 100.0% | 98.6% | 109 (77.3%) | 79.0% | 0 | 29 | 3 | 0 |
| off_by_one | 83 | 100.0% | 97.6% | 59 (71.1%) | 72.8% | 0 | 22 | 2 | 0 |
| sign_flip | 272 | 100.0% | 96.0% | 227 (83.5%) | 88.0% | 0 | 31 | 14 | 0 |
| swapped_symbols | 116 | 100.0% | 99.1% | 89 (76.7%) | 77.4% | 0 | 26 | 1 | 0 |
| wrong_constant | 210 | 100.0% | 95.7% | 172 (81.9%) | 86.0% | 0 | 28 | 10 | 0 |

### Per translator status

| translate status | n good | n mutated | good FAIL | mut FAIL | mut INCONCL. |
|---|---|---|---|---|---|
| not_checkable | 0 | 3 | – | 0 | 0 |
| ok | 272 | 1317 | 0 | 1047 | 207 |

### False positives (known-good formulas that got FAIL): 0


### Missed mutations: 273 not flagged (0 PASS, 207 INCONCLUSIVE, 66 SKIP/MISSING)

Mutations judged PASS (the worst kind of miss):

- none

The full missed list (with reasons) is in `metrics.json` → `synthetic.missed_mutations`.

## LaCASt Wikipedia gold set (95 hand-evaluated formulas)

The LaCASt human labels grade *translation* correctness (semantic LaTeX / Mathematica / Maple),
not mathematical truth; verify FAILs here are leads for review, not scored false positives.

- formulas: 95; translate ok: 40.0%; checkable: 4.2% end to end
- verdicts: PASS 3, FAIL 0, INCONCLUSIVE 1, SKIP 91, MISSING 0

| LaCASt human label | our translate status counts |
|---|---|
| human_mathematica=correct | not_checkable: 5, ok: 17, partial: 1, unparsed: 1 |
| human_mathematica=none | not_checkable: 15, ok: 1, unparsed: 2 |
| human_mathematica=wrong | not_checkable: 24, ok: 20, partial: 3, unparsed: 6 |
| human_semantic_latex=correct | not_checkable: 16, ok: 27, partial: 3, unparsed: 2 |
| human_semantic_latex=wrong | not_checkable: 28, ok: 11, partial: 1, unparsed: 7 |

