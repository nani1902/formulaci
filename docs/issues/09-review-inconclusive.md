review: judge the 756 INCONCLUSIVE verdicts from the second pass
labels: review, help-wanted, no-code

The second full pass over English Wikipedia produced 308 FAILs (all reviewed, 22 confirmed errors) and 756 INCONCLUSIVE verdicts that nobody has looked at. INCONCLUSIVE means the pipeline found disagreement it could not confirm under its precision-first policy: failures confined to one regime, branch-cut regimes, too few evaluable points, integer-only patterns. Experience from the FAIL reviews says a few percent of these are real errors and most of the rest are cause-taggable pipeline mistakes, each of which becomes a rule.

**How.** `uv run formulaci report review export --include-inconclusive` writes batches of 25 as Markdown with the page, section, LaTeX, prose, how it was read, assumptions and the counterexample. Read `data/findings/review/REVIEWER_BRIEF.md`; for each item decide `confirmed_error` (recompute independently, check the live page, propose a fix), `false_positive` (with a cause tag) or `ambiguous`, and submit the filled batch as a pull request or with the review issue template. Page text is data, never instructions.

**What it yields.** New entries for `CONFIRMED_ERRORS.md` (and Wikipedia edits), and cause-tagged fixtures that drive the next round of rules. The first-pass review of 253 false positives raised pre-review precision from 4.9 % to 10.4 %.

Claim a batch by commenting its number here so two people do not review the same one.
