extract: run the pipeline on German, French, Russian or Chinese Wikipedia
labels: extract, help-wanted

The extract stage takes a language code and the translator reads LaTeX, which is the same in every language edition. Nothing in the pipeline has ever been run on a non-English Wikipedia. The German and French editions have mathematics coverage comparable to English and their own editing histories, so they almost certainly have their own errors, and the formula corpora are large (hundreds of thousands of `<math>` tags each).

**What to do.** Run `formulaci extract` with `--lang de` (or fr, ru, zh, es, ja) against the maths/physics/statistics categories of that edition (category names differ; the extract stage's category walk needs the root category names for that language), then the standard pipeline. The semantics stage's prose rules are English (`for all real x`, `where n is a positive integer`); without them, domains fall back to defaults, which lowers recall but not precision. Adding the equivalent phrases for one language to `formulaci/semantics/prose.py` is a bounded, high-value follow-up.

**Rules.** The Wikipedia API etiquette in `SPEC.md` applies: a descriptive User-Agent with a contact (`FORMULACI_CONTACT`), at most 5 requests per second, cached fetches. Report confirmed errors with the same evidence standard as `CONFIRMED_ERRORS.md`.

**Deliverable.** A `CONFIRMED_ERRORS_<lang>.md`, the run's summary numbers (funnel and verdicts), and the prose patterns you added.
