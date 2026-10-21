# Posts (drafts, first-pass numbers; to be updated after run 2)

Repo: https://github.com/nani1902/formulaci
Errors: https://github.com/nani1902/formulaci/blob/main/CONFIRMED_ERRORS.md

---

## X thread

**1/**
Software has test suites. Human knowledge doesn't.

So I built one. formulaci runs every formula on Wikipedia's math, physics and statistics pages through a computer algebra system and reports the ones that are wrong.

It found 14 real errors on live pages. 🧵

**2/**
Examples it caught:
• Taylor series: the series for the 2nd and 3rd derivatives of 1/(1−x) are missing factors of 2 and 6
• Euler's constant: a limit that converges to −γ, not γ
• Volume of an n-ball: Γ(3/2) given as π/2 (it's √π/2)

Each one recomputed to 30 digits and still live today.

**3/**
More:
• Dirichlet integral: two wrong series in the page's own proof, one of which breaks the bound used in the next line
• List of trigonometric identities: two "sine" identities that sum cosines
• List of definite integrals: reduction formulas with ∞ where it should be m−1 (one side collapses to 0)

**4/**
How it works: extract 952k formulas from 64,617 articles → translate Wikipedia LaTeX to SymPy → infer domains and constraints from the prose → check symbolically and numerically at 50 digits across several sampling regimes → review every flag by hand before calling it an error.

**5/**
The honest part. On labeled data it had 0 false positives and caught 82% of injected errors. On real pages the first pass flagged 266 and only 13 were real. The rest were misread notation, label superscripts, arithmetic mod n, equations the page itself calls false.

**6/**
Every one of those 253 mistakes got a cause tag and became a rule. Second pass clears 109/110 translator cases and 130/135 semantics cases while still catching the real errors.

That loop is the actual product: a checker that learns what fooled it.

**7/**
This builds on real prior work: Greiner-Petter et al. proved the idea on 103 pages in 2022 (IEEE TPAMI) with Maple and Mathematica. It was never deployed. formulaci uses free tools and runs on the whole encyclopedia.

**8/**
It's MIT licensed, with the labeled benchmark, the 14 errors with evidence, and ready-to-paste Wikipedia fixes:

https://github.com/nani1902/formulaci

Built by directing a set of AI coding agents from a written spec, with every finding verified by hand. Next: clinical calculators.

---

## Show HN

**Title:** Show HN: formulaci – a test suite for Wikipedia's formulas (found 14 errors on live pages)

**Text:**
Software has test suites; human knowledge doesn't. formulaci extracts every <math> formula from English Wikipedia's mathematics, physics, statistics and engineering articles (952k formulas, 64,617 pages), translates the LaTeX to SymPy, infers variable domains and constraints from the surrounding prose, and checks each identity symbolically and numerically (mpmath, 50 digits, several sampling regimes). Every flag is reviewed before it is reported.

First pass found 14 real errors on live pages, each recomputed independently and re-checked today: two derivative series on "Taylor series" missing factors of 2 and 6, two wrong series inside the "Dirichlet integral" proof, a limit on "Euler's constant" with the wrong sign, two "sine formulation" identities on "List of trigonometric identities" that sum cosines, two reduction formulas on "List of definite integrals" with infinite bounds that should be m−1, Γ(3/2) = π/2 on "Volume of an n-ball", and a few minor ones. List with evidence and ready-to-paste fixes: CONFIRMED_ERRORS.md and WIKIPEDIA_EDITS.md in the repo.

Numbers: on a labeled benchmark (272 known-true identities, 1,320 injected errors) precision is 100% and recall 82%. On real pages the first pass was 5% precise before review (13 of 266 flags). Each false positive was tagged by cause (misread operators and conjugates, label superscripts, arithmetic in finite fields and ordinals, equations the page itself calls false, defining equations, rounding) and fed back as rules; the second pass clears 109/110 translator cases and 130/135 semantics cases while keeping the real errors flagged. Coverage is the main limitation: only identities with an explicit relation are checked, which is a small fraction of all <math> tags.

Prior art: Greiner-Petter et al., "Do the Math: Making Mathematics in Wikipedia Computable" (IEEE TPAMI 2022) proved this on 103 pages with Maple/Mathematica and LaCASt but was never deployed. This uses SymPy/mpmath and runs at the scale of the encyclopedia.

I designed the pipeline and the review protocol and directed a set of AI coding agents (Claude) that implemented the stages from a written spec; every reported error was recomputed by hand. MIT licensed. A second track audits online clinical calculators (eGFR, QTc, etc.) against the primary literature, so far only against a local mock.

https://github.com/nani1902/formulaci

---

## Email to the Göttingen authors (André Greiner-Petter, Bela Gipp)

Subject: Your "Do the Math" approach, deployed on all of English Wikipedia — 14 errors found

Dear Dr. Greiner-Petter, Prof. Gipp,

Your TPAMI paper "Do the Math: Making Mathematics in Wikipedia Computable" showed that CAS-based verification of Wikipedia formulas works, on 103 pages with Maple/Mathematica and LaCASt. I built a free-tool version (SymPy/mpmath, rules-based semantics) and ran it on the 952,136 formulas in the 64,617 articles tagged by WikiProjects Mathematics, Physics, Statistics and Engineering.

The first verification pass found 14 genuine errors on live pages (Taylor series, Dirichlet integral, Euler's constant, List of trigonometric identities, List of definite integrals, Volume of an n-ball, and others), each recomputed independently. The pipeline's measured precision on a labeled benchmark is 100% with 82% recall; on real pages the first pass was 5% precise before review, and I used the reviewed false positives as fixtures for a second pass. I also converted your 95-entry hand-evaluated benchmark (vendored under its MIT license) to the pipeline's format.

Everything is public under MIT: https://github.com/nani1902/formulaci. The confirmed errors with evidence are in CONFIRMED_ERRORS.md.

I would value your view on two things: whether the semantic-inference rules match what you found hardest, and whether there is interest in a bot or Toolforge deployment that posts flagged formulas to a review page, which your paper proposed. I am happy to collaborate or to be corrected.

Best regards,
Mahesh Balaram

---

## Note for Wikipedia talk:WikiProject Mathematics (to be posted by any editor, or you once an account exists)

== Fourteen formula errors found by computer-algebra verification ==

An open-source tool ran every <math> identity on the mathematics/physics/statistics/engineering articles through SymPy with inferred domains, and each flag was reviewed by hand. Fourteen errors were confirmed on live pages, each recomputed independently; the list with evidence and exact wikitext fixes is at https://github.com/nani1902/formulaci/blob/main/WIKIPEDIA_EDITS.md. The substantive ones are on [[Taylor series]] (derivative series missing factors 2 and 6), [[Dirichlet integral]] (two series in the proof), [[Euler's constant]] (limit sign), [[List of trigonometric identities]] (two "sine" sums written with cosines), [[List of definite integrals]] (reduction-formula bounds) and [[Volume of an n-ball]] (Γ(3/2)). The author cannot edit from their network (range block) and would be grateful if editors applied them, citing the repository. Method and prior art (Greiner-Petter et al., TPAMI 2022) are described in the repository README. ~~~~
