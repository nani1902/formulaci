# First batch of issues

Posted to GitHub on 2026-10-21 as issues #1 to #12 (same order as the files). Each file is one issue:
the first line is the title, the second the labels, the rest the body. The issue on GitHub is the live
version; these files are the drafts. To post a new draft:

```bash
gh issue create --title "<title>" --label coverage,help-wanted --body-file docs/issues/<file>.md
```

| File | Tier | Title | Issue |
|---|---|---|---|
| `01-ellipsis-series.md` | A | Read series and products written with an ellipsis | [#1](https://github.com/nani1902/formulaci/issues/1) |
| `02-vector-algebra.md` | A | Typed vectors and matrices: dot and cross products, transpose, norms, inner products | [#2](https://github.com/nani1902/formulaci/issues/2) |
| `03-explicit-matrices.md` | A | Evaluate identities between explicit matrices | [#3](https://github.com/nani1902/formulaci/issues/3) |
| `04-superscript-labels.md` | B | Tell a label superscript from a power instead of refusing the formula | [#4](https://github.com/nani1902/formulaci/issues/4) |
| `05-definition-propagation.md` | B | Use a page's own definitions to make later formulas checkable | [#5](https://github.com/nani1902/formulaci/issues/5) |
| `06-index-sums-from-context.md` | B | Supply bounds for `\sum_i` from the prose | [#6](https://github.com/nani1902/formulaci/issues/6) |
| `07-named-distributions.md` | B | Moments of named distributions | [#7](https://github.com/nani1902/formulaci/issues/7) |
| `08-congruences.md` | B | A modular evaluator for `a \equiv b \pmod n` | [#8](https://github.com/nani1902/formulaci/issues/8) |
| `09-review-inconclusive.md` | review | Review the 756 INCONCLUSIVE verdicts from the second pass | [#9](https://github.com/nani1902/formulaci/issues/9) |
| `10-other-languages.md` | extract | Run the pipeline on German, French, Russian or Chinese Wikipedia | [#10](https://github.com/nani1902/formulaci/issues/10) |
| `11-wikipedia-edits.md` | wikipedia | Submit the 36 confirmed corrections | [#11](https://github.com/nani1902/formulaci/issues/11) |
| `12-clean-skips.md` | C | Cheap, precise skips for sets, tuples, words and empty sides | [#12](https://github.com/nani1902/formulaci/issues/12) |
