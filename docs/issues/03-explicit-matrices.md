coverage: evaluate identities between explicit matrices (9,106 relations, 1,831 pages)
labels: coverage, help-wanted, tier-A

`\begin{pmatrix} ... \end{pmatrix}`, `bmatrix`, `vmatrix` and `\left[\begin{matrix}` blocks appear in 9,106 relations and are refused outright (`Unsupported("matrix")`).

- *Quantum mechanics*: `B = \frac{1}{\sqrt 2}\begin{pmatrix} 1 & i \\ i & 1 \end{pmatrix}`
- *Antimetric electrical network*: `[\mathbf S] = \begin{bmatrix} S_{11} & S_{12} \\ S_{12} & -S_{11} \end{bmatrix}`
- *Ordered Bell number*: `a(n) = \sum_{k=0}^n k! \left\{\begin{matrix} n \\ k \end{matrix}\right\}` (a Stirling number written as a braced matrix, which is a different construct)

**What to build.** In the translator, build `sympy.Matrix` from the rows (`\\` separated) and cells (`&` separated); in verify, when either side is a `Matrix`, check shapes agree and compare entrywise with the existing scalar machinery. Many of these relations are definitions (`B = ...`) and will be skipped by semantics anyway; the checkable ones are products, inverses, determinants and eigen-relations between explicit matrices, which are common on the *Matrix*, *Rotation matrix*, *Pauli matrices* and *Quaternion* pages.

**Precision risk.** `\left\{\begin{matrix} n \\ k \end{matrix}\right\}` and `\left[\begin{matrix} n \\ k \end{matrix}\right]` are Stirling numbers; `\begin{matrix}` inside `\begin{cases}` is a piecewise definition. Detect those first.

**Fixtures.** Pauli matrix products, 2×2 inverse formula, rotation matrix composition, `\det` of an explicit 2×2 and 3×3.

Depends on nothing; pairs well with the typed-vectors issue.
