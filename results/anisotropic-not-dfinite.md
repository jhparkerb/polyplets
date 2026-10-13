# The height-anisotropic polyplet generating function is not D-finite

Let `F(x,y) = Σ_{n,H} T(n,H) x^n y^H = Σ_H G_H(x) y^H`, with `G_H` the
fixed-height generating functions (`results/fixed_height_gfs.txt`). The
theorem below is that `F` is not D-finite, by an argument from strict
monotonicity of the strip growth constants plus Northcott finiteness. Before
it come two effective statements: explicit boxes of `(order, x-degree)` in
which no annihilating `y`-ODE exists, from certified root data at `H ≤ 10`.
Checker: `experiments/anisotropic_dfinite.py` (all certificates mod
`p = 2⁶¹−1`; a gcd of 1 mod `p` with preserved degrees is a certificate over
`ℚ`). Everything uses the validated `G_H`, `H ≤ 10`; the stored `H = 11`
entry is a failed reconstruction and is not used (last section).

## Certified root data

Define the **new-root content** `ψ_H = Q_H / gcd(Q_H, Q_1 Q_2 ⋯ Q_{H−1})`:
the denominator factors appearing first at height `H`. Certified:

- `deg ψ_H = 1, 2, 4, 9, 29, 68, 181, 462, 1254, 3289` (`H = 1..10`);
- every `ψ_H` squarefree; every `P_H/Q_H` in lowest terms (all roots active);
- `ψ`-roots are new: coprime to every earlier `Q` by construction;
- `ψ_H` is irreducible over `ℚ` for `H = 1..8` (degrees 1, 2, 4, 9, 29, 68,
  181, 462): single-prime certificates for `H ≤ 4`, multi-prime
  subset-sum-intersection certificates for `H = 5..8`. `H = 9, 10` (degrees
  1254, 3289) are uncertified, for factoring cost.
- The strip growth constants strictly increase: `μ_H = 1.0, 2.41421 (= 1+√2),
  3.44372, 4.18232, 4.71780, 5.11532, 5.41785, 5.65337, 5.84046, 5.99170`
  (`H = 1..10`, exact-coefficient evaluation).

Irreducibility gives `deg_ℚ(μ_H) = deg ψ_H` at every certified level, growing
at about `√λ ≈ 2.67` per level. Irreducibility plus positivity of the
dominant root also means, by Galois conjugation, that every root of `ψ_H` is
active in `T(n,H)`.

## Quantified theorem (from the ψ-ladder)

Suppose `Σ_{i≤r} p_i(x,y) ∂_y^i F = 0` with `p_i ∈ ℚ[x,y]`, not all zero,
`D = max deg_x p_i`. Extracting `y`-coefficients gives, for every `H`,
`Σ_{δ≤σ} c_δ(x,H) G_{H−δ}(x) = 0` with `deg_x c_δ ≤ D`, `deg_H c_δ ≤ r`, and
`{c_δ} ≡ 0` forces `{p_i} ≡ 0` (falling factorials of `H` are independent).
This extraction step is Lemma 9 of Bousquet-Mélou and Rechnitzer 2002 (see
below).

*Pole argument.* Let `α` be a root of `ψ_{H₀}`. Instance the relation at
`H = H₀`: every term with `δ ≥ 1` references a height `< H₀`, where `α` is not
a pole; `G_{H₀}` has a genuine pole at `α` (lowest terms + squarefree). Hence
`c_0(α, H₀) = 0` for all `deg ψ_{H₀}` roots, so `deg ψ_{H₀} > D` forces
`c_0(·, H₀) ≡ 0`. If this holds at `r+1` distinct levels, `c_0 ≡ 0` (its
`H`-degree is `≤ r`); recurse through the faces `δ = 1, 2, …` (each reuses
the same levels, anchored at `H₀+δ`). All faces vanish, a contradiction. ∎

**Corollary.** No annihilating `y`-ODE exists with (order `r`, `x`-degree
`D`) in any of: `r ≤ 5 & D ≤ 28`; `r ≤ 4 & D ≤ 67`; `r ≤ 3 & D ≤ 180`;
`r ≤ 2 & D ≤ 461`; `r ≤ 1 & D ≤ 1253`; `r = 0 & D ≤ 3288`. (Excluded
whenever `≥ r+1` certified levels have `deg ψ_H > D`.)

## The dichotomy theorem (from monotonicity and irreducibility)

**Theorem.** If `F(x,y)` is annihilated by a `y`-ODE of order `r` with
`x`-degrees `≤ D`, then `deg_ℚ(μ_H) ≤ D` for all but at most `r` values of `H`.

*Proof.* At level `H₀`, instance the coefficient relation at `H = H₀`; every
lower face is finite at `x = 1/μ_{H₀}` (strict monotonicity), `G_{H₀}` has a
pole there, so `c_0(1/μ_{H₀}, H₀) = 0`. A rational polynomial of degree `≤ D`
cannot vanish at an algebraic number of degree `> D`, so `deg_ℚ(μ_{H₀}) > D`
forces `c_0(·, H₀) ≡ 0`; `r+1` such levels kill `c_0` as a polynomial in `H`,
and the face recursion reuses the same levels. ∎

**Corollary.** No annihilating `y`-ODE with `r ≤ 4 & D ≤ 8`, `r ≤ 3 & D ≤ 28`,
`r ≤ 2 & D ≤ 67`, `r ≤ 1 & D ≤ 180`, `r = 0 & D ≤ 461`. Weaker than the
ψ-boxes above, but resting only on the monotonicity and irreducibility
certificates.

## The unconditional theorem

**Theorem.** `F(x,y) = Σ_{n,H} T(n,H) x^n y^H` is not D-finite.

*Proof, from four classical ingredients.*

1. **Fatou and rationality.** Each `G_H(x) = Σ_n T(n,H) x^n` is rational
   (finite transfer matrix) with integer coefficients, so by Fatou's lemma
   its lowest-terms denominator `Q_H` has `Q_H(0) = 1` and integer
   coefficients. The reversal of `Q_H` is monic integral, and its roots are
   exactly the reciprocals of the poles of `G_H`. Hence `μ_H := 1/(radius of
   convergence of G_H)` is an algebraic integer: the radius point of a
   rational series is a pole, positive-real by Pringsheim (`T ≥ 0`), and its
   minimal polynomial divides the monic reversal.

2. **House bound.** Every pole of `G_H` has modulus `≥ 1/μ_H`, by the
   definition of radius of convergence. So every Galois conjugate of `μ_H`
   (a root of the reversal) has modulus `≤ μ_H`: `house(μ_H) = μ_H`, and
   `μ_H < λ ≤ 9.3154` (the certified upper bound; any crude bound works).

3. **Strict monotonicity, by Perron–Frobenius.** Let `ν_H` be the growth
   constant of the height-`≤ H` strip counts, computed by the
   column-signature transfer `M_H(x)`: states are boundary signatures under
   the nonempty-column invariant; the signature digraph is strongly connected
   (any state reaches the single-cell state by closing components with a
   spanning column, and any state is reachable from it), so `M_H(x)` is
   irreducible nonnegative for `x > 0`. `M_H` sits inside `M_{H+1}` as a
   proper principal submatrix (signatures not using row `H+1`), and the extra
   states connect through the explicit cycle single-cell → full-`(H+1)`-column
   → single-cell. Deleting rows and columns of an irreducible nonnegative
   matrix strictly decreases the Perron root, so `ρ_{H+1}(x) > ρ_H(x)` at
   every `x > 0`; at `x*_H` (where `ρ_H = 1`) this gives `ρ_{H+1}(x*_H) > 1`,
   hence `x*_{H+1} < x*_H` and `ν_{H+1} > ν_H` strictly. Exact-height counts
   are second differences of strip counts, so (strictness means no
   cancellation) `μ_H = ν_H`, the pole `1/μ_H` of `G_H` is genuine, and the
   `μ_H` are pairwise distinct, converging up to `λ`. Numerically confirmed
   `H ≤ 10`; the Pringsheim minimum-modulus property confirmed `H ≤ 6`.

4. **Northcott–Kronecker finiteness.** For fixed `D`, an algebraic integer
   of degree `≤ D` with house `≤ B` has minimal-polynomial coefficients
   bounded by `binom(D,k) B^k`: finitely many integer polynomials, so
   finitely many such numbers. With `B = 9.3154`: for every `D`, only
   finitely many of the (infinitely many, distinct) `μ_H` can have degree
   `≤ D`. Therefore `deg_ℚ(μ_H) → ∞`.

5. **Dichotomy theorem.** A `y`-ODE of order `r` with `x`-degrees `≤ D`
   forces `deg_ℚ(μ_H) ≤ D` at all but at most `r` heights, contradicted by
   (4) for every `(r, D)`. (Without loss of generality the ODE is over
   `ℚ(x,y)`: `F` has rational coefficients, and D-finiteness over `ℂ`
   descends to the field of definition.) ∎

**Scope.** The proof uses only integer counts, per-height rationality, and
strictly increasing bounded strip growth constants. It therefore applies
verbatim to fixed polyominoes by height (A001168's triangle), polyhexes,
polyiamonds, and any lattice-animal family with a column transfer matrix. The
isotropic `a(x)` is untouched: the ordinary generating function being
non-D-finite remains a conjecture (`results/closed-doors.md` §2.4).

**Ceiling of the method.** The result is not-D-finite over `ℚ(x)` and does
not extend to D_A-finiteness (analytic coefficients, Klazar's enlarged
class): the step "a rational polynomial of degree `≤ D` cannot vanish at an
algebraic number of degree `> D`" is the entire dichotomy argument, and an
analytic coefficient may vanish at `1/μ_{H₀}` without vanishing identically.

## Relation to existing work

Papers held in `literature/`: Haruspicy 2 (arXiv math/0406450), Haruspicy 3
(math/0408054), and Bousquet-Mélou and Rechnitzer, "Lattice animals and
heaps of dimers," Discrete Math. 258 (2002) 235–274. The D-finiteness test
is not in Haruspicy 1: Haruspicy 2 states it as Theorem 15 "(from [4])" and
Haruspicy 3 as Theorem 5 "(from [6])", and both references resolve to BM-R
2002, Lemma 9. Haruspicy 1 supplies the combinatorial section/density
machinery (Haruspicy 2's Theorem 1), not the test.

**BM-R 2002, Lemma 9** (verbatim modulo notation):

> Let S(q,u) = sum_n S_n(q) u^n be a formal power series in u with
> coefficients in C(q). Assume S(q,u) is D-finite in u. For n >= 0 let P_n
> be the set of poles of S_n(q), and let P = union P_n. Then P has only a
> finite number of limit points.

Their proof: extract the coefficient of `u^n` from the ODE to get
`a_0(q,n)S_n = a_1(q,n)S_{n−1} + … + a_k(q,n)S_{n−k}` with `a_i ∈ ℂ[q,n]`;
so `S_n` has denominator `I(q)·Π_m a_0(q,m)`. If `l` is a limit point there
are `(q_i, n_i)` with `q_i → l`, `n_i → ∞`, `a_0(q_i,n_i) = 0`; dividing
`a_0 = Σ_k b_k(q)n^k` by `n_i^d` and letting `i → ∞` gives `b_d(l) = 0`. So
every limit point is a root of the fixed polynomial `b_d`.

| | BM-R 2002, Lemma 9 | the dichotomy theorem |
|---|---|---|
| opening move | extract y-coefficients of the ODE, giving a linear recurrence with polynomial coefficients | identical |
| what is tracked | the whole pole set of every slice | one pole per slice, `x = 1/μ_H` |
| finiteness input | topological: limit points of a subset of `ℂ` | arithmetic: Northcott (bounded degree + bounded house) |
| mechanism | asymptotic in `n`: divide by `n^d`, take the limit, hit the leading coefficient `b_d` | at a single level: lower faces regular at `1/μ_{H₀}` by strict monotonicity, so `c_0` vanishes there; a degree-`D` polynomial over `ℚ` cannot kill an algebraic number of degree `> D` |
| conclusion | qualitative: D-finite or not | effective: explicit `(r, D)` exclusion boxes |
| input needed to apply | an explicit combinatorial description of the denominators (cyclotomic `Ψ_k` from `k`-sections) | Perron–Frobenius monotonicity plus any crude upper bound on `λ` |

Step 1 is theirs and we cite Lemma 9 for it. Everything after step 1
diverges: they need all the poles and an accumulation argument in `ℂ`; we
need one distinguished pole and its degree over `ℚ`. Needing only
monotonicity plus a crude bound is why the proof transports to
polyominoes-by-height, polyhexes, polyiamonds, and any family with a column
transfer matrix, where theirs needs a combinatorial denominator analysis per
family. Northcott appears in neither paper.

**Klazar 2003** (M. Klazar, "Non-P-recursiveness of numbers of matchings
(linear chord diagrams) with many crossings," Adv. in Appl. Math. 30 (2003)
126–136) is a one-variable non-P-recursiveness proof whose obstruction is
analytic, not arithmetic. His Theorem 1: let `F` satisfy `F' = G(x,F)` with
`G` a Laurent series; if (i) `F` is not analytic, (ii) `G` is analytic,
(iii) `ord_y(G) < 0`, then `F` is not D_A-finite, a fortiori not D-finite.
Proof: iterate to get `F^(k) = G_k(x,F)` with `ord_y(G_k) = k(p−1)+1`
strictly negative; a D-finite relation collapses to `H(x,F) = 0` with `H`
analytic and nonzero, so Weierstrass preparation plus Puiseux force `F`
analytic, contradicting (i). The lever is divergence: `F` must have zero
radius of convergence. That cannot engage with our object: every `G_H` is
rational with radius `1/μ_H`, and `μ_H < λ`, so `F(x,y)` is analytic in a
bidisc, and condition (i) fails.

| | obstruction | lever |
|---|---|---|
| BM-R 2002 | topological | accumulation of the pole set in `ℂ` |
| Klazar 2003 | analytic | zero radius of convergence against forced analyticity |
| this note | arithmetic | degree and house of algebraic numbers (Northcott) |

Klazar's Theorem 4 is worth a separate look: `(con_n)` and `(cro_n)` are
P-recursive modulo `2^k` for every `k`, an object with no P-recursive
description whose reductions mod a prime power are algebraic. That is
structurally the same phenomenon as the mod-3 structure of the triangle
(`results/arithmetic-structure.md`): the height triangle admits no C-finite
recurrence, yet mod 3 it is governed by the cubic `W³ = W² + t`. Whether the
mechanisms are related is open.

**Other arithmetic neighbors.** Bell, Nguyen and Zannier, "D-finiteness,
rationality, and height" (Trans. AMS 373 (2020) 4889–4906; II, Adv. Math.
414 (2023); III, multivariate Pólya–Carlson, Math. Z. 306 (2024), with
S. Chen) is height theory applied directly to D-finite series. It is a
different configuration: they bound the Weil heights of the coefficients and
conclude rationality; we bound degree and house of the slice growth
constants and conclude a contradiction. Bell–Hu–Satriano (arXiv 2003.01255)
pairs heights with D-finiteness along orbits of rational maps, further
still. Bell–Gerhold–Klazar–Luca is zero-counting, analytic.

**Literature search.** Backward references and keyword search, then a
forward citation crawl with OpenAlex and Semantic Scholar
(`experiments/citation_crawl.py`) over BM-R 2002 (83/74 citing), Haruspicy 2
(13/17), Haruspicy 3 (4/4), Chan–Rechnitzer 2018 (20/2), BBEP 2020 (3/20),
Bell–Hu–Satriano (5) and Bell–Gerhold–Klazar–Luca (25), then Google
Scholar's full-text search within BM-R 2002's 79 citing articles
(`Northcott` 0 hits, `Mahler` 0 hits; `algebraic degree` and `height` hits
all false, being the degree of an algebraic equation a generating function
satisfies, or column/path height in bargraphs) and the standalone queries
`"growth constant" Northcott D-finite` and `"transfer matrix" "algebraic
degree" "not D-finite"` (nothing). Haruspicy 2's 14 citing articles read in
full: surveys, constructions, and the pole-accumulation route; the one new
name, Assis–van Hoeij–Maillard (J. Phys. A 2016), exhibits ODEs for solvable
models rather than supplying a non-D-finiteness criterion. Every descendant
of BM-R that proves non-D-finiteness uses pole or singularity accumulation;
no arithmetic endgame on a family of slice growth constants appears in any
of these sets. Table and per-seed notes in `literature/MISSING.md`. Absence
cannot be established by search, so the claim is scoped to the lighter
hypotheses and the effective boxes, with Lemma 9 cited for the shared
opening, and we do not write "first".

## The H = 11 entry

The stored `Q₁₁` is a failed reconstruction: a CRT lift from 133 primes whose
modulus half (1241 digits) is below the true coefficient size (about 1299
digits at degree 13381), so every coefficient from degree 8159 up is a
residue. Shown by the pipeline's own soundness check on the stored entry
(`experiments/gf_h11_validate.py`: `Q₁₁ · B₁₁ ≠ P₁₁` mod a fresh prime, first
mismatch at `n = 8170`); the full account and the price of a re-recovery
(about 48 CPU-hours, not run) are in
[`results/diagonal-formula.md`](diagonal-formula.md). The observation that
`Q₁₁` shares no roots with `Q₉Q₁₀` is a symptom of the wraparound, not a fact
about height 11. The ψ-ladder, the irreducibility certificates, the
monotonicity lemma and the theorem read `validated=True` blocks only and stop
at `H = 10`.
