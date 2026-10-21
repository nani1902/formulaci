coverage: tell a label superscript from a power instead of refusing the whole formula (11,979 relations)
labels: coverage, help-wanted, tier-B

`\omega_1^n`, `K_n^M(F)`, `x^{(k)}`, `H^n(F, \mu)`: a superscript that is an index, not a power. The translator refuses the formula (`Unsupported("superscript_label")`) whenever it cannot decide, which costs 11,979 relations on 3,130 pages. Label superscripts read as powers were also the second-largest cause of false FAILs in the first full pass, so the current refusal is deliberate caution.

**What to build.** A page-level decision in `formulaci/translate/parser.py` (`_superscript_label`) with more evidence: a superscript on a symbol that also carries a subscript; a parenthesised superscript `^{(k)}`; a superscript letter that is never used as a variable elsewhere in the formula or the surrounding formulas; a symbol whose "powers" would be of a function name (`H^n(...)`). When the verdict is "label", fold it into the symbol name (`omega_1^n` → `omega_1_n`) so the rest of the formula can still be checked.

**Precision risk.** This is the one construct where recall gains come straight out of precision. `x^n` with `n` an integer variable is a power; `x^{(n)}` is a derivative on an analysis page and a label on a statistics page. The fixtures in `tests/translate/fixtures/review_false_positives.jsonl` include the misreads from pass one; none may regress, and the bench must stay at zero false FAILs.

**Acceptance.** Bench gate green; the review fixtures pass; a sample of 50 recovered formulas from the corpus, read by hand, contains no power-as-label misreads.
