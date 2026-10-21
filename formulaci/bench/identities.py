r"""Catalogue of classical identities known to be true, in the Wikipedia LaTeX dialect.

Each entry: (category, name, latex, vars, cond, ctx)
- ``vars``: "x:real y:pos n:posint" — sampling types from ``oracle.SAMPLERS``; they also drive the
  domain sentence written into ``context_before``.
- ``cond``: optional Python expression over the variables, used for rejection sampling (and
  stated in prose via ``ctx`` when it matters).
- ``ctx``: optional override of the generated domain phrase.

Every entry is proven numerically by ``oracle.check`` at build time; entries that fail are not
written to ``known_good.jsonl`` (``build`` reports them).
"""
from __future__ import annotations

PAGES = {
    "trig": "List of trigonometric identities",
    "hyperbolic": "Hyperbolic functions",
    "exp_log": "Logarithm",
    "gamma_beta": "Gamma function",
    "zeta": "Riemann zeta function",
    "binomial": "Binomial coefficient",
    "finite_series": "Summation",
    "infinite_series": "Series (mathematics)",
    "integrals": "List of definite integrals",
    "derivatives": "Differentiation rules",
    "inequalities": "List of inequalities",
    "probability": "Moment (mathematics)",
    "algebra": "Factorization",
    "complex": "Euler's formula",
}

E: list[tuple] = []


def G(cat, name, latex, vars="", cond=None, ctx=None):
    E.append((cat, name, latex, vars, cond, ctx))


# --- trigonometry -----------------------------------------------------------------------------
xy = "x:real y:real"
G("trig", "Pythagorean identity", r"\sin^2 x + \cos^2 x = 1", "x:real")
G("trig", "Pythagorean identity for tangent", r"1 + \tan^2 x = \sec^2 x", "x:real")
G("trig", "Pythagorean identity for cotangent", r"1 + \cot^2 x = \csc^2 x", "x:real")
G("trig", "Angle sum formula for sine", r"\sin(x + y) = \sin x \cos y + \cos x \sin y", xy)
G("trig", "Angle difference formula for sine", r"\sin(x - y) = \sin x \cos y - \cos x \sin y", xy)
G("trig", "Angle sum formula for cosine", r"\cos(x + y) = \cos x \cos y - \sin x \sin y", xy)
G("trig", "Angle difference formula for cosine", r"\cos(x - y) = \cos x \cos y + \sin x \sin y", xy)
G("trig", "Angle sum formula for tangent", r"\tan(x + y) = \frac{\tan x + \tan y}{1 - \tan x \tan y}", xy)
G("trig", "Double-angle formula for sine", r"\sin 2x = 2 \sin x \cos x", "x:real")
G("trig", "Double-angle formula for cosine", r"\cos 2x = \cos^2 x - \sin^2 x", "x:real")
G("trig", "Double-angle formula for cosine (cosine form)", r"\cos 2x = 2\cos^2 x - 1", "x:real")
G("trig", "Double-angle formula for cosine (sine form)", r"\cos 2x = 1 - 2\sin^2 x", "x:real")
G("trig", "Double-angle formula for tangent", r"\tan 2x = \frac{2\tan x}{1 - \tan^2 x}", "x:real")
G("trig", "Triple-angle formula for sine", r"\sin 3x = 3\sin x - 4\sin^3 x", "x:real")
G("trig", "Triple-angle formula for cosine", r"\cos 3x = 4\cos^3 x - 3\cos x", "x:real")
G("trig", "Power-reduction formula for sine", r"\sin^2 x = \frac{1 - \cos 2x}{2}", "x:real")
G("trig", "Power-reduction formula for cosine", r"\cos^2 x = \frac{1 + \cos 2x}{2}", "x:real")
G("trig", "Sum-to-product formula for sine",
  r"\sin x + \sin y = 2 \sin\left(\frac{x + y}{2}\right) \cos\left(\frac{x - y}{2}\right)", xy)
G("trig", "Sum-to-product formula for cosine",
  r"\cos x + \cos y = 2 \cos\left(\frac{x + y}{2}\right) \cos\left(\frac{x - y}{2}\right)", xy)
G("trig", "Difference-to-product formula for cosine",
  r"\cos x - \cos y = -2 \sin\left(\frac{x + y}{2}\right) \sin\left(\frac{x - y}{2}\right)", xy)
G("trig", "Product-to-sum formula for sines",
  r"\sin x \sin y = \frac{1}{2}\left[\cos(x - y) - \cos(x + y)\right]", xy)
G("trig", "Product-to-sum formula for cosines",
  r"\cos x \cos y = \frac{1}{2}\left[\cos(x - y) + \cos(x + y)\right]", xy)
G("trig", "Product-to-sum formula for sine and cosine",
  r"\sin x \cos y = \frac{1}{2}\left[\sin(x + y) + \sin(x - y)\right]", xy)
G("trig", "Half-angle formula for tangent", r"\tan\frac{x}{2} = \frac{\sin x}{1 + \cos x}", "x:real")
G("trig", "Half-angle formula for tangent (second form)", r"\tan\frac{x}{2} = \frac{1 - \cos x}{\sin x}", "x:real")
G("trig", "Tangent half-angle substitution for sine",
  r"\sin x = \frac{2\tan\frac{x}{2}}{1 + \tan^2\frac{x}{2}}", "x:real")
G("trig", "Tangent half-angle substitution for cosine",
  r"\cos x = \frac{1 - \tan^2\frac{x}{2}}{1 + \tan^2\frac{x}{2}}", "x:real")
G("trig", "Complementary inverse functions", r"\arcsin x + \arccos x = \frac{\pi}{2} \quad -1 \le x \le 1", "x:sym1",
  ctx="for -1 ≤ x ≤ 1")
G("trig", "Arctangent reflection", r"\arctan x + \arctan\frac{1}{x} = \frac{\pi}{2}, \quad x > 0", "x:pos")
G("trig", "Supplementary angle identity", r"\sin(\pi - x) = \sin x", "x:real")
G("trig", "Cofunction identity", r"\cos\left(\frac{\pi}{2} - x\right) = \sin x", "x:real")
G("trig", "Difference of fourth powers", r"\cos^4 x - \sin^4 x = \cos 2x", "x:real")
G("trig", "Sine of arccosine", r"\sin(\arccos x) = \sqrt{1 - x^2}", "x:sym1", ctx="for -1 ≤ x ≤ 1")
G("trig", "Cosine of arctangent", r"\cos(\arctan x) = \frac{1}{\sqrt{1 + x^2}}", "x:real")
G("trig", "Triple product formula for sine",
  r"4 \sin x \sin\left(\frac{\pi}{3} - x\right) \sin\left(\frac{\pi}{3} + x\right) = \sin 3x", "x:real")
G("trig", "Lagrange's trigonometric identity for sines",
  r"\sum_{k=1}^{n} \sin kx = \frac{\sin\frac{nx}{2} \sin\frac{(n+1)x}{2}}{\sin\frac{x}{2}}", "n:posint x:real")
G("trig", "Dirichlet kernel",
  r"1 + 2\sum_{k=1}^{n} \cos kx = \frac{\sin\left(\left(n + \frac{1}{2}\right)x\right)}{\sin\frac{x}{2}}", "n:posint x:real")
G("trig", "Tangent of a difference", r"\tan(x - y) = \frac{\tan x - \tan y}{1 + \tan x \tan y}", xy)
G("trig", "Secant squared minus tangent squared", r"\sec^2 x - \tan^2 x = 1", "x:real")

# --- hyperbolic -------------------------------------------------------------------------------
G("hyperbolic", "Hyperbolic Pythagorean identity", r"\cosh^2 x - \sinh^2 x = 1", "x:real")
G("hyperbolic", "Addition formula for hyperbolic sine", r"\sinh(x + y) = \sinh x \cosh y + \cosh x \sinh y", xy)
G("hyperbolic", "Addition formula for hyperbolic cosine", r"\cosh(x + y) = \cosh x \cosh y + \sinh x \sinh y", xy)
G("hyperbolic", "Double-argument formula for hyperbolic sine", r"\sinh 2x = 2 \sinh x \cosh x", "x:real")
G("hyperbolic", "Double-argument formula for hyperbolic cosine", r"\cosh 2x = \cosh^2 x + \sinh^2 x", "x:real")
G("hyperbolic", "Double-argument formula for hyperbolic cosine (sinh form)", r"\cosh 2x = 2\sinh^2 x + 1", "x:real")
G("hyperbolic", "Double-argument formula for hyperbolic tangent", r"\tanh 2x = \frac{2\tanh x}{1 + \tanh^2 x}", "x:real")
G("hyperbolic", "Exponential definition of hyperbolic sine", r"\sinh x = \frac{e^{x} - e^{-x}}{2}", "x:real")
G("hyperbolic", "Exponential definition of hyperbolic cosine", r"\cosh x = \frac{e^{x} + e^{-x}}{2}", "x:real")
G("hyperbolic", "Exponential form of hyperbolic tangent", r"\tanh x = \frac{e^{2x} - 1}{e^{2x} + 1}", "x:real")
G("hyperbolic", "Hyperbolic secant identity", r"1 - \tanh^2 x = \operatorname{sech}^2 x", "x:real")
G("hyperbolic", "Hyperbolic cosecant identity", r"\coth^2 x - 1 = \operatorname{csch}^2 x", "x:pos")
G("hyperbolic", "Logarithmic form of inverse hyperbolic sine",
  r"\operatorname{arsinh} x = \ln\left(x + \sqrt{x^2 + 1}\right)", "x:real")
G("hyperbolic", "Logarithmic form of inverse hyperbolic cosine",
  r"\operatorname{arcosh} x = \ln\left(x + \sqrt{x^2 - 1}\right) \quad x \ge 1", "x:gt1", ctx="for x ≥ 1")
G("hyperbolic", "Logarithmic form of inverse hyperbolic tangent",
  r"\operatorname{artanh} x = \frac{1}{2}\ln\frac{1 + x}{1 - x}, \quad |x| < 1", "x:sym1")
G("hyperbolic", "Sum of hyperbolic cosine and sine", r"\cosh x + \sinh x = e^{x}", "x:real")
G("hyperbolic", "Triple-argument formula for hyperbolic sine", r"\sinh 3x = 3\sinh x + 4\sinh^3 x", "x:real")
G("hyperbolic", "Triple-argument formula for hyperbolic cosine", r"\cosh 3x = 4\cosh^3 x - 3\cosh x", "x:real")
G("hyperbolic", "Sum-to-product formula for hyperbolic sine",
  r"\sinh x + \sinh y = 2 \sinh\left(\frac{x + y}{2}\right) \cosh\left(\frac{x - y}{2}\right)", xy)
G("hyperbolic", "Hyperbolic cosine of an imaginary argument", r"\cosh(ix) = \cos x", "x:real")
G("hyperbolic", "Half-argument formula for hyperbolic tangent", r"\tanh\frac{x}{2} = \frac{\sinh x}{\cosh x + 1}", "x:real")
G("hyperbolic", "Power-reduction formula for hyperbolic sine", r"\sinh^2 x = \frac{\cosh 2x - 1}{2}", "x:real")
G("hyperbolic", "Difference formula for hyperbolic cosine", r"\cosh(x - y) = \cosh x \cosh y - \sinh x \sinh y", xy)

# --- exponential and logarithm ----------------------------------------------------------------
pxy = "x:pos y:pos"
G("exp_log", "Product rule for logarithms", r"\ln(xy) = \ln x + \ln y", pxy)
G("exp_log", "Quotient rule for logarithms", r"\ln\frac{x}{y} = \ln x - \ln y", pxy)
G("exp_log", "Power rule for logarithms", r"\ln\left(x^{y}\right) = y \ln x", "x:pos y:real")
G("exp_log", "Change of base formula", r"\log_b x = \frac{\ln x}{\ln b}", "x:pos b:gt1", ctx="for x > 0 and b > 1")
G("exp_log", "Product of exponentials", r"e^{x + y} = e^{x} e^{y}", xy)
G("exp_log", "Exponential of a logarithm", r"e^{\ln x} = x, \quad x > 0", "x:pos")
G("exp_log", "Logarithm of an exponential", r"\ln e^{x} = x", "x:real")
G("exp_log", "Power of an exponential", r"\left(e^{x}\right)^{y} = e^{xy}", xy)
G("exp_log", "Exponential with arbitrary base", r"a^{x} = e^{x \ln a}", "a:pos x:real")
G("exp_log", "Product rule for logarithms in base b", r"\log_b(xy) = \log_b x + \log_b y", "x:pos y:pos b:gt1",
  ctx="for positive x, y and b > 1")
G("exp_log", "Reciprocal of a logarithm", r"\log_{b} x = \frac{1}{\log_{x} b}", "x:gt1 b:gt1",
  ctx="for x > 1 and b > 1")
G("exp_log", "Product of powers", r"x^{a} x^{b} = x^{a + b}", "x:pos a:real b:real")
G("exp_log", "Quotient of powers", r"\frac{x^{a}}{x^{b}} = x^{a - b}", "x:pos a:real b:real")
G("exp_log", "Power of a product", r"(xy)^{a} = x^{a} y^{a}", "x:pos y:pos a:real")
G("exp_log", "Square root of a product", r"\sqrt{xy} = \sqrt{x}\sqrt{y}", pxy)
G("exp_log", "Inverse property of logarithms", r"a^{\log_a x} = x", "x:pos a:gt1", ctx="for x > 0 and a > 1")
G("exp_log", "Logarithm of a root", r"\ln \sqrt[n]{x} = \frac{\ln x}{n}", "x:pos n:posint")
G("exp_log", "Logarithm of a reciprocal", r"\ln\frac{1}{x} = -\ln x", "x:pos")
G("exp_log", "Exponential of a sum of logarithms", r"e^{\ln x + \ln y} = xy", pxy)

# --- gamma, beta and related ------------------------------------------------------------------
G("gamma_beta", "Recurrence relation of the gamma function", r"\Gamma(x + 1) = x\,\Gamma(x)", "x:pos")
G("gamma_beta", "Gamma function at integers", r"\Gamma(n) = (n - 1)!", "n:posint")
G("gamma_beta", "Gamma function at one half", r"\Gamma\left(\frac{1}{2}\right) = \sqrt{\pi}")
G("gamma_beta", "Euler's reflection formula", r"\Gamma(x)\,\Gamma(1 - x) = \frac{\pi}{\sin \pi x}", "x:unit")
G("gamma_beta", "Legendre duplication formula",
  r"\Gamma(x)\,\Gamma\left(x + \frac{1}{2}\right) = 2^{1 - 2x}\sqrt{\pi}\,\Gamma(2x)", "x:pos")
G("gamma_beta", "Beta function in terms of gamma",
  r"\mathrm{B}(x, y) = \frac{\Gamma(x)\,\Gamma(y)}{\Gamma(x + y)}", pxy)
G("gamma_beta", "Symmetry of the beta function", r"\mathrm{B}(x, y) = \mathrm{B}(y, x)", pxy)
G("gamma_beta", "Integral representation of the beta function",
  r"\mathrm{B}(x, y) = \int_0^1 t^{x - 1} (1 - t)^{y - 1}\,dt", "x:pos1 y:pos1")
G("gamma_beta", "Euler integral of the second kind", r"\Gamma(x) = \int_0^\infty t^{x - 1} e^{-t}\,dt", "x:pos1")
G("gamma_beta", "Recurrence relation of the digamma function", r"\psi(x + 1) = \psi(x) + \frac{1}{x}", "x:pos")
G("gamma_beta", "Digamma function at one", r"\psi(1) = -\gamma",
  ctx="where γ is the Euler–Mascheroni constant,")
G("gamma_beta", "Gamma function and Pochhammer product",
  r"\Gamma(x + n) = \Gamma(x) \prod_{k=0}^{n - 1} (x + k)", "x:pos n:posint")
G("gamma_beta", "Beta function with unit argument", r"\mathrm{B}(x, 1) = \frac{1}{x}", "x:pos")
G("gamma_beta", "Gamma function at half-integers",
  r"\Gamma\left(n + \tfrac{1}{2}\right) = \frac{(2n)!}{4^{n}\, n!}\sqrt{\pi}", "n:nonnegint")
G("gamma_beta", "Odd symmetry of the error function", r"\operatorname{erf}(-x) = -\operatorname{erf}(x)", "x:real")
G("gamma_beta", "Integral definition of the error function",
  r"\operatorname{erf}(x) = \frac{2}{\sqrt{\pi}} \int_0^{x} e^{-t^2}\,dt", "x:real")
G("gamma_beta", "Complementary error function", r"\operatorname{erfc}(x) = 1 - \operatorname{erf}(x)", "x:real")
G("gamma_beta", "Digamma function as logarithmic derivative", r"\psi(x) = \frac{d}{dx} \ln\Gamma(x)", "x:pos")
G("gamma_beta", "Reflection formula with negative argument",
  r"\Gamma(x)\,\Gamma(-x) = -\frac{\pi}{x \sin \pi x}", "x:unit")
G("gamma_beta", "Beta function recurrence",
  r"\mathrm{B}(x + 1, y) = \frac{x}{x + y}\,\mathrm{B}(x, y)", pxy)

# --- zeta -------------------------------------------------------------------------------------
G("zeta", "Basel problem (zeta form)", r"\zeta(2) = \frac{\pi^2}{6}")
G("zeta", "Zeta function at four", r"\zeta(4) = \frac{\pi^4}{90}")
G("zeta", "Dirichlet series of the zeta function", r"\zeta(s) = \sum_{n=1}^\infty \frac{1}{n^{s}} \quad s > 1", "s:gt1",
  ctx="for real s > 1")
G("zeta", "Dirichlet eta function in terms of zeta",
  r"\sum_{n=1}^{\infty} \frac{(-1)^{n+1}}{n^{s}} = \left(1 - 2^{1 - s}\right)\zeta(s)", "s:gt1", ctx="for real s > 1")
G("zeta", "Bose integral for the zeta function",
  r"\zeta(s)\,\Gamma(s) = \int_0^\infty \frac{x^{s - 1}}{e^{x} - 1}\,dx", "s:gt1", ctx="for real s > 1")
G("zeta", "Zeta function at zero", r"\zeta(0) = -\frac{1}{2}")
G("zeta", "Zeta function at minus one", r"\zeta(-1) = -\frac{1}{12}")
G("zeta", "Zeta function at six", r"\zeta(6) = \frac{\pi^6}{945}")
G("zeta", "Sum over odd reciprocal powers",
  r"\sum_{n=0}^{\infty} \frac{1}{(2n + 1)^{s}} = \left(1 - 2^{-s}\right)\zeta(s)", "s:gt1", ctx="for real s > 1")

# --- binomial and combinatorial ---------------------------------------------------------------
nk = "n:nonnegint k:nonnegint"
G("binomial", "Sum of binomial coefficients", r"\sum_{k=0}^{n} \binom{n}{k} = 2^{n}", "n:nonnegint")
G("binomial", "Symmetry of binomial coefficients", r"\binom{n}{k} = \binom{n}{n - k}", nk, "k <= n",
  ctx="for non-negative integers n and k with k ≤ n")
G("binomial", "Factorial formula for binomial coefficients", r"\binom{n}{k} = \frac{n!}{k!\,(n - k)!}", nk, "k <= n",
  ctx="for non-negative integers n and k with k ≤ n")
G("binomial", "Pascal's rule", r"\binom{n}{k} = \binom{n - 1}{k - 1} + \binom{n - 1}{k}", "n:posint k:posint", "k <= n",
  ctx="for positive integers n and k with 1 ≤ k ≤ n")
G("binomial", "Alternating sum of binomial coefficients", r"\sum_{k=0}^{n} (-1)^{k} \binom{n}{k} = 0", "n:posint")
G("binomial", "Weighted sum of binomial coefficients", r"\sum_{k=0}^{n} k \binom{n}{k} = n\, 2^{n - 1}", "n:posint")
G("binomial", "Sum of squared binomial coefficients", r"\sum_{k=0}^{n} \binom{n}{k}^{2} = \binom{2n}{n}", "n:nonnegint")
G("binomial", "Binomial theorem", r"(x + y)^{n} = \sum_{k=0}^{n} \binom{n}{k} x^{n - k} y^{k}", "x:real y:real n:nonnegint")
G("binomial", "Vandermonde's identity",
  r"\sum_{j=0}^{k} \binom{m}{j} \binom{n}{k - j} = \binom{m + n}{k}", "m:nonnegint n:nonnegint k:nonnegint")
G("binomial", "Hockey-stick identity", r"\sum_{i=k}^{n} \binom{i}{k} = \binom{n + 1}{k + 1}", nk, "k <= n",
  ctx="for non-negative integers n and k with k ≤ n")
G("binomial", "Absorption identity", r"k \binom{n}{k} = n \binom{n - 1}{k - 1}", "n:posint k:posint", "k <= n",
  ctx="for positive integers n and k with k ≤ n")
G("binomial", "Triangular numbers as binomial coefficients", r"\binom{n}{2} = \frac{n(n - 1)}{2}", "n:nonnegint")
G("binomial", "Binomial series (finite)", r"\sum_{k=0}^{n} \binom{n}{k} x^{k} = (1 + x)^{n}", "x:real n:nonnegint")
G("binomial", "Factorial as a product", r"n! = \prod_{k=1}^{n} k", "n:posint")
G("binomial", "Central binomial coefficient via gamma",
  r"\binom{2n}{n} = \frac{4^{n}}{\sqrt{\pi}}\, \frac{\Gamma\left(n + \frac{1}{2}\right)}{\Gamma(n + 1)}", "n:nonnegint")
G("binomial", "Catalan numbers as a difference",
  r"\frac{1}{n + 1}\binom{2n}{n} = \binom{2n}{n} - \binom{2n}{n + 1}", "n:nonnegint")
G("binomial", "Double factorial of an even number", r"(2n)!! = 2^{n}\, n!", "n:nonnegint")
G("binomial", "Negative binomial series",
  r"\sum_{k=0}^{\infty} \binom{k + n}{k} x^{k} = \frac{1}{(1 - x)^{n + 1}}", "x:sym1 n:nonnegint",
  ctx="for |x| < 1 and non-negative integers n")
G("binomial", "Row sum of odd binomial coefficients", r"\sum_{k=0}^{n} \binom{2n + 1}{k} = 4^{n}", "n:nonnegint")

# --- finite series ----------------------------------------------------------------------------
G("finite_series", "Sum of the first n integers", r"\sum_{k=1}^{n} k = \frac{n(n + 1)}{2}", "n:posint")
G("finite_series", "Sum of squares", r"\sum_{k=1}^{n} k^2 = \frac{n(n + 1)(2n + 1)}{6}", "n:posint")
G("finite_series", "Nicomachus's theorem", r"\sum_{k=1}^{n} k^3 = \left(\frac{n(n + 1)}{2}\right)^2", "n:posint")
G("finite_series", "Finite geometric series",
  r"\sum_{k=0}^{n - 1} x^{k} = \frac{1 - x^{n}}{1 - x}, \quad x \ne 1", "x:real n:posint", "abs(x - 1) > 0.05")
G("finite_series", "Sum of the first n odd numbers", r"\sum_{k=1}^{n} (2k - 1) = n^2", "n:posint")
G("finite_series", "Telescoping sum", r"\sum_{k=1}^{n} \frac{1}{k(k + 1)} = \frac{n}{n + 1}", "n:posint")
G("finite_series", "Arithmetico-geometric sum",
  r"\sum_{k=0}^{n} k x^{k} = \frac{x - (n + 1) x^{n + 1} + n x^{n + 2}}{(1 - x)^2}", "x:real n:posint", "abs(x - 1) > 0.05")
G("finite_series", "Sum of pronic numbers", r"\sum_{k=1}^{n} k(k + 1) = \frac{n(n + 1)(n + 2)}{3}", "n:posint")
G("finite_series", "Sum of fourth powers",
  r"\sum_{k=1}^{n} k^4 = \frac{n(n + 1)(2n + 1)(3n^2 + 3n - 1)}{30}", "n:posint")
G("finite_series", "Telescoping product", r"\prod_{k=1}^{n} \left(1 + \frac{1}{k}\right) = n + 1", "n:posint")
G("finite_series", "Telescoping product of squares",
  r"\prod_{k=2}^{n} \left(1 - \frac{1}{k^2}\right) = \frac{n + 1}{2n}", "n:posint", "n >= 2",
  ctx="for integers n ≥ 2")
G("finite_series", "Telescoping sum of odd reciprocals",
  r"\sum_{k=1}^{n} \frac{1}{(2k - 1)(2k + 1)} = \frac{n}{2n + 1}", "n:posint")
G("finite_series", "Arithmetic series", r"\sum_{k=0}^{n} (a + kd) = \frac{(n + 1)(2a + nd)}{2}", "a:real d:real n:nonnegint")
G("finite_series", "Alternating sum of squares",
  r"\sum_{k=1}^{n} (-1)^{k+1} k^2 = (-1)^{n+1} \frac{n(n + 1)}{2}", "n:posint")
G("finite_series", "Product of Fermat-type factors",
  r"\prod_{k=0}^{n - 1} \left(1 + x^{2^{k}}\right) = \frac{1 - x^{2^{n}}}{1 - x}", "x:sym1 n:posint",
  ctx="for |x| < 1 and positive integers n")
G("finite_series", "Sum of k over powers of two", r"\sum_{k=1}^{n} \frac{k}{2^{k}} = 2 - \frac{n + 2}{2^{n}}", "n:posint")
G("finite_series", "Sum of cubes of odd numbers", r"\sum_{k=1}^{n} (2k - 1)^3 = n^2 (2n^2 - 1)", "n:posint")
G("finite_series", "Sum of harmonic-type differences",
  r"\sum_{k=1}^{n} \left(\frac{1}{k} - \frac{1}{k + 1}\right) = 1 - \frac{1}{n + 1}", "n:posint")

# --- infinite series --------------------------------------------------------------------------
G("infinite_series", "Basel problem", r"\sum_{n=1}^{\infty} \frac{1}{n^2} = \frac{\pi^2}{6}")
G("infinite_series", "Leibniz formula for pi", r"\sum_{n=0}^{\infty} \frac{(-1)^{n}}{2n + 1} = \frac{\pi}{4}")
G("infinite_series", "Geometric series", r"\sum_{n=0}^{\infty} x^{n} = \frac{1}{1 - x}, \quad |x| < 1", "x:sym1")
G("infinite_series", "Taylor series of the sine function",
  r"\sin x = \sum_{n=0}^{\infty} \frac{(-1)^{n} x^{2n + 1}}{(2n + 1)!}", "x:real")
G("infinite_series", "Taylor series of the cosine function",
  r"\cos x = \sum_{n=0}^{\infty} \frac{(-1)^{n} x^{2n}}{(2n)!}", "x:real")
G("infinite_series", "Taylor series of the exponential function", r"e^{x} = \sum_{n=0}^{\infty} \frac{x^{n}}{n!}", "x:real")
G("infinite_series", "Series for e", r"\sum_{n=0}^{\infty} \frac{1}{n!} = e")
G("infinite_series", "Telescoping series", r"\sum_{n=1}^{\infty} \frac{1}{n(n + 1)} = 1")
G("infinite_series", "Derivative of the geometric series",
  r"\sum_{n=1}^{\infty} n x^{n} = \frac{x}{(1 - x)^2}, \quad |x| < 1", "x:sym1")
G("infinite_series", "Gregory series",
  r"\arctan x = \sum_{n=0}^{\infty} \frac{(-1)^{n} x^{2n + 1}}{2n + 1}", "x:sym1", ctx="for |x| < 1")
G("infinite_series", "Sum of reciprocal fourth powers", r"\sum_{n=1}^{\infty} \frac{1}{n^4} = \frac{\pi^4}{90}")
G("infinite_series", "Geometric series with ratio one half", r"\sum_{n=0}^{\infty} \frac{1}{2^{n}} = 2")
G("infinite_series", "Sum of reciprocal odd squares", r"\sum_{n=1}^{\infty} \frac{1}{(2n - 1)^2} = \frac{\pi^2}{8}")
G("infinite_series", "Taylor series of the hyperbolic cosine", r"\cosh x = \sum_{n=0}^{\infty} \frac{x^{2n}}{(2n)!}", "x:real")
G("infinite_series", "Mercator series",
  r"\ln(1 + x) = \sum_{n=1}^{\infty} \frac{(-1)^{n+1} x^{n}}{n} \quad |x| < 1", "x:sym1")
G("infinite_series", "Logarithmic series", r"\sum_{n=1}^{\infty} \frac{x^{n}}{n} = -\ln(1 - x)", "x:sym1",
  ctx="for |x| < 1")
G("infinite_series", "Wallis product", r"\prod_{n=1}^{\infty} \left(1 - \frac{1}{4n^2}\right) = \frac{2}{\pi}")
G("infinite_series", "Alternating series for 1/e", r"\sum_{n=0}^{\infty} \frac{(-1)^{n}}{n!} = \frac{1}{e}")
G("infinite_series", "Alternating harmonic series", r"\sum_{k=1}^{\infty} \frac{(-1)^{k+1}}{k} = \ln 2")
G("infinite_series", "Squared geometric series",
  r"\frac{1}{(1 - x)^2} = \sum_{n=0}^{\infty} (n + 1) x^{n}", "x:sym1", ctx="for |x| < 1")
G("infinite_series", "Series for the hyperbolic sine",
  r"\sinh x = \sum_{n=0}^{\infty} \frac{x^{2n + 1}}{(2n + 1)!}", "x:real")

# --- definite integrals -----------------------------------------------------------------------
G("integrals", "Gaussian integral (half line)", r"\int_0^\infty e^{-x^2}\,dx = \frac{\sqrt{\pi}}{2}")
G("integrals", "Gaussian integral", r"\int_{-\infty}^{\infty} e^{-a x^2}\,dx = \sqrt{\frac{\pi}{a}}", "a:pos")
G("integrals", "Integral of a power", r"\int_0^1 x^{n}\,dx = \frac{1}{n + 1}", "n:nonnegint")
G("integrals", "Integral of sine over a half period", r"\int_0^{\pi} \sin x\,dx = 2")
G("integrals", "Integral of sine squared", r"\int_0^{\pi/2} \sin^2 x\,dx = \frac{\pi}{4}")
G("integrals", "Integral of a decaying exponential", r"\int_0^\infty e^{-ax}\,dx = \frac{1}{a}", "a:pos")
G("integrals", "Gamma integral at integers", r"\int_0^\infty x^{n} e^{-x}\,dx = n!", "n:nonnegint")
G("integrals", "Integral of the Cauchy kernel", r"\int_0^\infty \frac{1}{1 + x^2}\,dx = \frac{\pi}{2}")
G("integrals", "Arctangent integral", r"\int_0^1 \frac{1}{1 + x^2}\,dx = \frac{\pi}{4}")
G("integrals", "Integral of the logarithm", r"\int_0^1 \ln x\,dx = -1")
G("integrals", "Integral of the identity", r"\int_a^b x\,dx = \frac{b^2 - a^2}{2}", "a:real b:real")
G("integrals", "Integral of cosine squared over a period", r"\int_0^{2\pi} \cos^2 x\,dx = \pi")
G("integrals", "First moment of the Gaussian", r"\int_0^\infty x e^{-x^2}\,dx = \frac{1}{2}")
G("integrals", "Beta integral", r"\int_0^1 x^{a - 1} (1 - x)^{b - 1}\,dx = \frac{\Gamma(a)\,\Gamma(b)}{\Gamma(a + b)}",
  "a:pos1 b:pos1")
G("integrals", "Bose–Einstein integral", r"\int_0^\infty \frac{x}{e^{x} - 1}\,dx = \frac{\pi^2}{6}")
G("integrals", "Integral of log sine", r"\int_0^{\pi/2} \ln \sin x\,dx = -\frac{\pi}{2} \ln 2")
G("integrals", "Dilogarithm integral", r"\int_0^1 \frac{\ln(1 + x)}{x}\,dx = \frac{\pi^2}{12}")
G("integrals", "Laplace transform of cosine",
  r"\int_0^\infty e^{-ax} \cos(bx)\,dx = \frac{a}{a^2 + b^2}", "a:pos b:real")
G("integrals", "Integral of a cubic", r"\int_0^{a} x^3\,dx = \frac{a^4}{4}", "a:real")
G("integrals", "Integral of the exponential", r"\int_0^{1} e^{x}\,dx = e - 1")
G("integrals", "Integral of the reciprocal", r"\int_1^{a} \frac{1}{x}\,dx = \ln a", "a:pos")
G("integrals", "Integral of a squared exponential decay", r"\int_0^\infty x^2 e^{-ax}\,dx = \frac{2}{a^3}", "a:pos")

# --- derivatives ------------------------------------------------------------------------------
G("derivatives", "Derivative of sine", r"\frac{d}{dx} \sin x = \cos x", "x:real")
G("derivatives", "Derivative of cosine", r"\frac{d}{dx} \cos x = -\sin x", "x:real")
G("derivatives", "Derivative of tangent", r"\frac{d}{dx} \tan x = \sec^2 x", "x:real")
G("derivatives", "Derivative of an exponential", r"\frac{d}{dx} e^{ax} = a e^{ax}", "x:real a:real")
G("derivatives", "Derivative of the natural logarithm", r"\frac{d}{dx} \ln x = \frac{1}{x}", "x:pos")
G("derivatives", "Power rule", r"\frac{d}{dx} x^{n} = n x^{n - 1}", "x:pos n:real")
G("derivatives", "Derivative of arctangent", r"\frac{d}{dx} \arctan x = \frac{1}{1 + x^2}", "x:real")
G("derivatives", "Derivative of arcsine", r"\frac{d}{dx} \arcsin x = \frac{1}{\sqrt{1 - x^2}}", "x:sym1",
  ctx="for -1 < x < 1")
G("derivatives", "Derivative of an exponential with base a", r"\frac{d}{dx} a^{x} = a^{x} \ln a", "x:real a:pos")
G("derivatives", "Derivative of hyperbolic sine", r"\frac{d}{dx} \sinh x = \cosh x", "x:real")
G("derivatives", "Derivative of hyperbolic tangent", r"\frac{d}{dx} \tanh x = 1 - \tanh^2 x", "x:real")
G("derivatives", "Second derivative of sine", r"\frac{d^2}{dx^2} \sin(ax) = -a^2 \sin(ax)", "x:real a:real")
G("derivatives", "Derivative of x to the x", r"\frac{d}{dx} x^{x} = x^{x} (1 + \ln x)", "x:pos")
G("derivatives", "Derivative of the error function",
  r"\frac{d}{dx} \operatorname{erf}(x) = \frac{2}{\sqrt{\pi}} e^{-x^2}", "x:real")
G("derivatives", "Derivative of the reciprocal", r"\frac{d}{dx} \left(\frac{1}{x}\right) = -\frac{1}{x^2}", "x:real")
G("derivatives", "Derivative of the square root", r"\frac{d}{dx} \sqrt{x} = \frac{1}{2\sqrt{x}}", "x:pos")
G("derivatives", "Derivative of cotangent", r"\frac{d}{dx} \cot x = -\csc^2 x", "x:real")
G("derivatives", "Derivative of a Gaussian", r"\frac{d}{dx} e^{-x^2} = -2x e^{-x^2}", "x:real")
G("derivatives", "Derivative of hyperbolic cosine", r"\frac{d}{dx} \cosh x = \sinh x", "x:real")
G("derivatives", "Derivative of the logarithm of the absolute value", r"\frac{d}{dx} \ln|x| = \frac{1}{x}", "x:real")

# --- inequalities -----------------------------------------------------------------------------
G("inequalities", "Inequality of arithmetic and geometric means", r"\frac{x + y}{2} \ge \sqrt{xy}", pxy,
  ctx="for non-negative real numbers x and y")
G("inequalities", "Exponential inequality", r"e^{x} \ge 1 + x", "x:real")
G("inequalities", "Logarithm inequality", r"\ln x \le x - 1 \quad x > 0", "x:pos")
G("inequalities", "Triangle inequality", r"|x + y| \le |x| + |y|", xy)
G("inequalities", "Harmonic–geometric mean inequality", r"\frac{2xy}{x + y} \le \sqrt{xy}", pxy)
G("inequalities", "Quadratic–arithmetic mean inequality",
  r"\sqrt{\frac{x^2 + y^2}{2}} \ge \frac{x + y}{2}", pxy)
G("inequalities", "Sine bound", r"|\sin x| \le |x|", "x:real")
G("inequalities", "Bernoulli's inequality", r"(1 + x)^{n} \ge 1 + nx", "x:gtm1 n:posint",
  ctx="for every integer n ≥ 1 and every real number x ≥ -1")
G("inequalities", "Sum of a number and its reciprocal", r"x + \frac{1}{x} \ge 2, \quad x > 0", "x:pos")
G("inequalities", "Lower bound for the logarithm", r"\frac{x}{1 + x} \le \ln(1 + x)", "x:pos")
G("inequalities", "Sine below identity", r"\sin x \le x \quad x \ge 0", "x:pos")
G("inequalities", "Cosine lower bound", r"\cos x \ge 1 - \frac{x^2}{2}", "x:real")
G("inequalities", "Powers of two", r"2^{n} \ge n + 1", "n:nonnegint")
G("inequalities", "Factorial bound", r"n! \le n^{n}", "n:posint")
G("inequalities", "Cauchy–Schwarz inequality in two dimensions",
  r"(ac + bd)^2 \le (a^2 + b^2)(c^2 + d^2)", "a:real b:real c:real d:real")
G("inequalities", "Two-square inequality", r"x^2 + y^2 \ge 2xy", xy)
G("inequalities", "Hyperbolic tangent bound", r"\tanh x \le x", "x:pos", ctx="for x ≥ 0")
G("inequalities", "Arctangent bound", r"\arctan x \le x", "x:pos", ctx="for x ≥ 0")
G("inequalities", "Logarithm bounds for the harmonic series",
  r"\frac{1}{n + 1} < \ln\left(1 + \frac{1}{n}\right) < \frac{1}{n}", "n:posint")
G("inequalities", "Tangent line of the exponential at one", r"e^{x} \ge e x", "x:real")
G("inequalities", "Sum of mixed powers", r"x^{y} + y^{x} > 1", pxy)
G("inequalities", "Logarithm lower bound", r"1 - \frac{1}{x} \le \ln x", "x:pos")
G("inequalities", "Jordan's inequality", r"\frac{2x}{\pi} \le \sin x", "x:unit", ctx="for 0 ≤ x ≤ π/2")
G("inequalities", "Young's inequality for products", r"xy \le \frac{x^2}{2} + \frac{y^2}{2}", xy)

# --- probability distribution moments ---------------------------------------------------------
G("probability", "Mean of the normal distribution",
  r"\int_{-\infty}^{\infty} x \frac{1}{\sigma\sqrt{2\pi}} e^{-\frac{(x - \mu)^2}{2\sigma^2}}\,dx = \mu",
  "mu:real sigma:pos", ctx="for every real μ and σ > 0")
G("probability", "Variance of the normal distribution",
  r"\int_{-\infty}^{\infty} (x - \mu)^2 \frac{1}{\sigma\sqrt{2\pi}} e^{-\frac{(x - \mu)^2}{2\sigma^2}}\,dx = \sigma^2",
  "mu:real sigma:pos", ctx="for every real μ and σ > 0")
G("probability", "Normalisation of the standard normal density",
  r"\int_{-\infty}^{\infty} \frac{1}{\sqrt{2\pi}} e^{-x^2/2}\,dx = 1")
G("probability", "Mean of the exponential distribution",
  r"\int_0^\infty x \lambda e^{-\lambda x}\,dx = \frac{1}{\lambda}", "lambda:pos", ctx="for rate λ > 0")
G("probability", "Second moment of the exponential distribution",
  r"\int_0^\infty x^2 \lambda e^{-\lambda x}\,dx = \frac{2}{\lambda^2}", "lambda:pos", ctx="for rate λ > 0")
G("probability", "Normalisation of the exponential distribution",
  r"\int_0^\infty \lambda e^{-\lambda x}\,dx = 1", "lambda:pos", ctx="for rate λ > 0")
G("probability", "Mean of the Poisson distribution",
  r"\sum_{k=0}^{\infty} k \frac{\lambda^{k} e^{-\lambda}}{k!} = \lambda", "lambda:pos", ctx="for λ > 0")
G("probability", "Second moment of the Poisson distribution",
  r"\sum_{k=0}^{\infty} k^2 \frac{\lambda^{k} e^{-\lambda}}{k!} = \lambda^2 + \lambda", "lambda:pos", ctx="for λ > 0")
G("probability", "Normalisation of the Poisson distribution",
  r"\sum_{k=0}^{\infty} \frac{\lambda^{k} e^{-\lambda}}{k!} = 1", "lambda:pos", ctx="for λ > 0")
G("probability", "Mean of the binomial distribution",
  r"\sum_{k=0}^{n} k \binom{n}{k} p^{k} (1 - p)^{n - k} = np", "n:posint p:unit")
G("probability", "Second moment of the binomial distribution",
  r"\sum_{k=0}^{n} k^2 \binom{n}{k} p^{k} (1 - p)^{n - k} = np(1 - p) + n^2 p^2", "n:posint p:unit")
G("probability", "Normalisation of the binomial distribution",
  r"\sum_{k=0}^{n} \binom{n}{k} p^{k} (1 - p)^{n - k} = 1", "n:posint p:unit")
G("probability", "Mean of the geometric distribution",
  r"\sum_{k=1}^{\infty} k (1 - p)^{k - 1} p = \frac{1}{p}", "p:unit")
G("probability", "Mean of the continuous uniform distribution",
  r"\int_a^b \frac{x}{b - a}\,dx = \frac{a + b}{2}", "a:real b:real", "abs(b - a) > 0.1", ctx="for real a < b")
G("probability", "Variance of the continuous uniform distribution",
  r"\int_a^b \frac{x^2}{b - a}\,dx - \left(\frac{a + b}{2}\right)^2 = \frac{(b - a)^2}{12}", "a:real b:real",
  "abs(b - a) > 0.1", ctx="for real a < b")
G("probability", "Mean of the beta distribution",
  r"\int_0^1 x \frac{x^{\alpha - 1} (1 - x)^{\beta - 1}}{\mathrm{B}(\alpha, \beta)}\,dx = \frac{\alpha}{\alpha + \beta}",
  "alpha:pos1 beta:pos1", ctx="for shape parameters α, β > 0")
G("probability", "Mean of the gamma distribution",
  r"\int_0^\infty x \frac{x^{k - 1} e^{-x/\theta}}{\Gamma(k)\, \theta^{k}}\,dx = k\theta", "k:pos1 theta:pos1",
  ctx="for shape k > 0 and scale θ > 0")
G("probability", "Moment-generating function of the standard normal",
  r"\int_{-\infty}^{\infty} e^{tx} \frac{1}{\sqrt{2\pi}} e^{-x^2/2}\,dx = e^{t^2/2}", "t:real")
G("probability", "Variance of the Bernoulli distribution", r"p(1 - p)^2 + (1 - p)p^2 = p(1 - p)", "p:unit")
G("probability", "Probability generating function of the geometric distribution",
  r"\sum_{k=1}^{\infty} (1 - p)^{k - 1} p\, z^{k} = \frac{pz}{1 - (1 - p)z}", "p:unit z:sym1",
  ctx="for 0 < p < 1 and |z| < 1")

# --- algebra ----------------------------------------------------------------------------------
ab = "a:real b:real"
G("algebra", "Square of a sum", r"(a + b)^2 = a^2 + 2ab + b^2", ab)
G("algebra", "Difference of two squares", r"a^2 - b^2 = (a - b)(a + b)", ab)
G("algebra", "Difference of two cubes", r"a^3 - b^3 = (a - b)(a^2 + ab + b^2)", ab)
G("algebra", "Sum of two cubes", r"a^3 + b^3 = (a + b)(a^2 - ab + b^2)", ab)
G("algebra", "Cube of a sum", r"(a + b)^3 = a^3 + 3a^2 b + 3ab^2 + b^3", ab)
G("algebra", "Sum of reciprocals", r"\frac{1}{a} + \frac{1}{b} = \frac{a + b}{ab}", ab)
G("algebra", "Square root of a square", r"\sqrt{a^2} = |a|", "a:real")
G("algebra", "Brahmagupta–Fibonacci identity",
  r"(a^2 + b^2)(c^2 + d^2) = (ac - bd)^2 + (ad + bc)^2", "a:real b:real c:real d:real")
G("algebra", "Square of a trinomial", r"(a + b + c)^2 = a^2 + b^2 + c^2 + 2ab + 2bc + 2ca", "a:real b:real c:real")
G("algebra", "Sophie Germain identity", r"a^4 + 4b^4 = (a^2 + 2b^2 + 2ab)(a^2 + 2b^2 - 2ab)", ab)
G("algebra", "Rationalising a denominator", r"\frac{1}{\sqrt{a} + \sqrt{b}} = \frac{\sqrt{a} - \sqrt{b}}{a - b}",
  "a:pos b:pos", "abs(a - b) > 0.05", ctx="for positive a ≠ b")
G("algebra", "Factorisation of a fourth-power difference", r"a^4 - b^4 = (a - b)(a + b)(a^2 + b^2)", ab)

# --- complex ----------------------------------------------------------------------------------
G("complex", "Euler's formula", r"e^{ix} = \cos x + i \sin x", "x:real")
G("complex", "Euler's identity", r"e^{i\pi} + 1 = 0")
G("complex", "De Moivre's formula", r"(\cos x + i \sin x)^{n} = \cos nx + i \sin nx", "x:real n:int")
G("complex", "Modulus of a unit phasor", r"\left|e^{ix}\right| = 1", "x:real")
G("complex", "Cosine via complex exponentials", r"\cos x = \frac{e^{ix} + e^{-ix}}{2}", "x:real")
G("complex", "Sine via complex exponentials", r"\sin x = \frac{e^{ix} - e^{-ix}}{2i}", "x:real")
G("complex", "Exponential of a complex number", r"e^{z} = e^{\operatorname{Re} z}\left(\cos \operatorname{Im} z + i \sin \operatorname{Im} z\right)",
  "z:complex", ctx="for every complex number z")
