# Draft issues (not yet posted)

First batch of GitHub issues for contributors, drafted for review. Each file is one issue: the first
line is the title, the second the labels, the rest the body. Post with:

```bash
gh issue create --title "<title>" --label coverage,help-wanted --body-file docs/issues/<file>.md
```

| File | Tier | Title |
|---|---|---|
| `01-ellipsis-series.md` | A | Read series and products written with an ellipsis |
| `02-vector-algebra.md` | A | Typed vectors and matrices: dot and cross products, transpose, norms, inner products |
| `03-explicit-matrices.md` | A | Evaluate identities between explicit matrices |
| `04-superscript-labels.md` | B | Tell a label superscript from a power instead of refusing the formula |
| `05-definition-propagation.md` | B | Use a page's own definitions to make later formulas checkable |
| `06-index-sums-from-context.md` | B | Supply bounds for `\sum_i` from the prose |
| `07-named-distributions.md` | B | Moments of named distributions |
| `08-congruences.md` | B | A modular evaluator for `a \equiv b \pmod n` |
| `09-review-inconclusive.md` | review | Review the 756 INCONCLUSIVE verdicts from the second pass |
| `10-other-languages.md` | extract | Run the pipeline on German, French, Russian or Chinese Wikipedia |
| `11-wikipedia-edits.md` | wikipedia | Submit the 36 confirmed corrections |
| `12-clean-skips.md` | C | Cheap, precise skips for sets, tuples, words and empty sides |
