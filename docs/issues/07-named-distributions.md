coverage: moments of named distributions (4,767 relations; the `probability` tag)
labels: coverage, help-wanted, tier-B

`\operatorname{E}[X] = np`, `\operatorname{Var}(X) = \lambda`, `\Pr[k \text{ wins of } n] = \binom{n}{k} p^k (1-p)^{n-k}` are refused as `probability` (and many more as the `operator_notation` semantics skip). When the page names the distribution ("X is binomial with parameters n and p", or the page *is* the distribution's article), the expectation, variance, moments, moment generating function and CDF are closed forms that can be evaluated.

**What to build.** A `distribution` type in semantics, set from prose or page title for the common families (binomial, Poisson, geometric, normal, exponential, gamma, beta, uniform, chi-squared, Student's t), a table of their moments and generating functions, and translator readings for `E[...]`, `\operatorname{Var}`, `\operatorname{Cov}`, `\Pr[...]`, `M_X(t)`. The verify stage then substitutes the closed form and samples the parameters within the distribution's domain. The bench already has a `probability` category (20 identities about moments) to extend.

**Precision risk.** Which random variable an `E[...]` refers to when a page has several; moments that exist only for some parameters (Student's t variance needs ν > 2). The parameter domain must come from the distribution table, not be sampled freely.

**Fixtures.** The moment identities on each distribution's article, with and without the distribution named in the context sentence.
