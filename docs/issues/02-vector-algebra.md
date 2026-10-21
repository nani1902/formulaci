coverage: typed vectors and matrices (dot and cross products, transpose, norms, inner products; ~24,000 relations)
labels: coverage, help-wanted, tier-A

Five constructs in the ladder are the same missing feature: the pipeline has no object type other than scalars.

| tag | relations | example |
|---|---:|---|
| `inner_product` | 5,896 | *Hilbert space*: `\langle z, w\rangle = z_1\overline{w}_1 + z_2\overline{w}_2` |
| `norm` | 4,352 | *Vector space*: `\|f + g\|_p \leq \|f\|_p + \|g\|_p` |
| `vector_product` | 4,075 | *Matrix (mathematics)*: `|\mathbf{AB}| = |\mathbf A| \cdot |\mathbf B|` |
| `transpose` | 3,522 | *Descartes's theorem*: `\mathbf{k}^\mathsf{T}\mathbf{Q}^{-1}\mathbf{k} = 0` |
| `styled_expression` | 3,143 | *Matrix (mathematics)*: `\mathbf{Ax} = \mathbf{b}` |

plus the `matrix_or_vector` semantics skip (76,071 formulas whose symbols the prose marks as vectors or matrices).

**What to build.** A `vector`/`matrix` symbol type in `formulaci/semantics` (shape from the prose: "a vector in R^3", "an n×n matrix", "column vectors"), a translator reading for `\mathbf{v}`, `\vec v`, `\boldsymbol`, `^T`/`^\mathsf{T}`, `\cdot`, `\times`, `\langle a, b \rangle`, `\|v\|` and `\|v\|_p`, and in `formulaci/verify` a sampler that draws small random real (and, when the domain says so, complex) vectors and matrices and an evaluator that compares componentwise. Dimension is a free integer to sample over (2, 3, 4) unless fixed.

**Precision risk.** `\langle\delta, f\rangle` is a distribution pairing, `\|f\|_{H^1}` a Sobolev norm, `\mathbf{AB}` on a physics page may be a tensor product. Only typed, finite-dimensional objects are checkable; everything else must keep a clean skip. Identities that hold only in R^3 (`\mathbf{a} \times (\mathbf{b} \times \mathbf{c})`) need the dimension fixed from the formula or the prose.

**Fixtures first.** Lagrange's identity, the triangle and Cauchy–Schwarz inequalities, `(AB)^T = B^T A^T`, `\det(AB) = \det A \det B`, the BAC–CAB rule, `\|a\|^2 = a \cdot a`, parallelogram law. Add a `vectors` category to `formulaci/bench/identities.py` and a vector sampler to `formulaci/bench/oracle.py` so the bench can prove them independently.

**Acceptance.** Bench gate green with the new category included; the physics pages' `\mathbf{F} = m\mathbf{a}` style laws still skip as definitions.
