wikipedia: submit the 36 confirmed corrections
labels: wikipedia, help-wanted, no-code

`CONFIRMED_ERRORS.md` lists 36 formulas on live English Wikipedia pages that are wrong, each with the page, revision id, the error, the evidence (independent recomputation at 30 digits where applicable) and the fix. `WIKIPEDIA_EDITS.md` turns the first 14 into exact find-and-replace edits with ready edit summaries. None has been submitted: this project's maintainer cannot edit from their network (an IP range block on anonymous edits), and a bot is the wrong tool for a one-off list of 36 human-verified corrections.

**How.** Pick an entry, re-check the formula against the live page (the revision id tells you whether the section changed since), make the edit from your account with the suggested summary (which cites the counterexample so the talk page has the evidence), then add a line to the entry's status by pull request: date, your username, diff link. For the 22 second-pass entries without a prepared edit, write the find/replace in the same format as the first 14 and add it to `WIKIPEDIA_EDITS.md` in the same PR.

A note on *List of trigonometric identities* and *List of definite integrals*: those pages are heavily watched; a short talk-page note with the counterexample avoids a revert.
