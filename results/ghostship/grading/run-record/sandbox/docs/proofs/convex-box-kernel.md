# Kernel-method derivation of the bivariate box GF of convex king animals

Date: 2026-08-15 (autonomous session 03). Proves the structure fitted in
sessions 01–02 (`results/convex-box.md`, `results/convex-box-bivariate.md`).

**Theorem (established here; sole caveat in §7).** Let f(w,h) be the number
of convex king animals (HV-convex polyplets) with bounding box exactly w×h
and F(x,y) = Σ f(w,h) x^w y^h. Then F is algebraic over Q(x,y): with
u = √y, Δ = (1−x−y)² − 4xy, and the algebraic points

    s0   = ((1+x−y) − √Δ)/(2x)      [unique power-series root of
                                     x s² − (1+x−y)s + 1 = 0]
    σ±   = 1/(1 ∓ u)                 [roots of (s−1)² = y s²]

F is given by the finite expression (1)–(6) below, an element of Q(x,y,√Δ);
and this expression equals session 02's closed form

    F(x,y) = −[M + 2x²y²(1+x+y)²·√Δ] / (2·(x+y+xy)·Δ²)

(§7: identification closed on the full sufficient degree box, certified
modulo two ~10¹⁸ primes). The algebraicity of F itself — the headline —
depends only on the exact steps §§1–6. The same derivation with one
boundary term removed handles convex polyominoes (control), reproducing the
classical Δ-algebraicity.

Verification status of each step is marked [proved] / [checked]:
[checked] = verified by exact machine computation to a stated finite order,
with the residual gap quantified in §7.

## 1. The functional equation [proved combinatorially; validated exactly]

A convex king animal with rows i = 1..h is a sequence of integer intervals
[l_i, r_i], l_i ≤ r_i, with l valley-unimodal (non-increasing then
non-decreasing), r mountain-unimodal, and king-compatibility
l_{i+1} ≤ r_i + 1, r_{i+1} ≥ l_i − 1 (this row-interval model was validated
against definitional brute force in sessions 01–02). Parse each animal
uniquely by phases (pl, pr): pl flips 0→1 at the first strict increase of l,
pr flips at the first strict decrease of r. Key elementary observations:

- In phase (0,0), l = min_j≤i l_j and r = max_j≤i r_j: the last row spans the
  whole current bounding box. King-compatibility is automatic.
- In phase (1,0): r = current max (pr = 0), and the left box edge is final
  (l never returns below its phase-(0,0) minimum). Constraint l' ≤ r+1 is the
  only active king constraint. Mirror for (0,1).
- In phase (1,1): both box edges final; intervals nested decreasing;
  king-compatibility automatic.

Track the state (phase, k) with k = last-row length, weight x^(box width,
accumulated incrementally) y^(rows) s^k. Writing intervals' moves as
l' = l ± i/u, r' = r ± e/j, the complete transition list is (each ⋅y):

    (0,0)→(0,0): u,v ≥ 0                         k' = k+u+v,  x-weight u+v
    (0,0)→(1,0): 1 ≤ i ≤ k, e ≥ 0, (i=k ⟹ e≥1)  k' = k+e−i,  x-weight e
    (0,0)→(0,1): mirror of previous               k' = k+u−j,  x-weight u
    (0,0)→(1,1): i,j ≥ 1, i+j ≤ k−1              k' = k−i−j
    (1,0)→(1,0): 0 ≤ i ≤ k, e ≥ 0, (i=k ⟹ e≥1)  k' = k+e−i,  x-weight e
    (1,0)→(1,1): i ≥ 0, j ≥ 1, i+j ≤ k−1         k' = k−i−j
    (0,1)→(0,1), (0,1)→(1,1): mirrors
    (1,1)→(1,1): i,j ≥ 0, i+j ≤ k−1              k' = k−i−j

(The i=k boundary cases are the strictly-jumping rows allowed only by king
adjacency; deleting them, i.e. i ≤ k−1 with no e-condition, gives the convex
POLYOMINO model.) Initial state: one row of length k ≥ 1, weight x^k y s^k.

VALIDATION: `experiments/s03_funceq_check.py` implements exactly these
transitions (raw sums, no DP machinery) and reproduces the brute-force
validated DP table f(w,h) for ALL w,h ≤ 12, in both king and polyomino
modes (`out_s03_funceq_check.txt`). Exact integer arithmetic.

Summing geometric series (all elementary), with F_ph(s) the GF of states in
phase ph and G1 := G(1), G1' := G'(1) for divided differences:

    F00(s) = xys/(1−xs) + y·F00(s)/(1−xs)²                              (E0)
    F10(s) = y·B[F00](s) + y·C[F10](s)                                  (E1)
    F01(s) = F10(s)   [mirror bijection: reflect horizontally]
    F11(s) = y·D1[F00](s) + 2y·D2[F10](s) + y·L3[F11](s)                (E2)

    B[G](s) = (G(s) − s·G1)/((s−1)(1−xs)) + xs·G1/(1−xs)     [king]
              (polyomino: drop the xs·G1/(1−xs) term)
    C[G](s) = s(G(s) − G1)/((s−1)(1−xs)) + xs·G1/(1−xs)      [king]
              (polyomino: drop the boundary term)
    L3[G](s) = [s²G(s) − s²G1 − s(s−1)G1′]/(s−1)²
    D2[G](s) = L3[G](s) − s(G(s) − G1)/(s−1)
    D1[G](s) = [G(s) − s²G1 − s(s−1)(G1′−2G1)]/(s−1)²

The operator formulas D1, D2, L3 are unit-tested against the raw transition
sums for G = s^k, k ≤ 8, in `s03_kernel_solve.py`. The full GF is
F(x,y) = F00(1) + 2·F10(1) + F11(1).

Uniqueness: the system determines the y^h coefficients of all F_ph from the
y^{h−1} coefficients, so it has exactly one power-series solution — the
combinatorial one.

## 2. Substitution legitimacy [proved]

All series here lie in the space S of formal sums Σ c_{i,m,k} x^i u^m s^k
with k ≤ i (last-row length ≤ box width). For any algebraic point σ with
σ = 1 + (positive (x,u)-valuation), substitution s → σ is well defined on S
and is a ring homomorphism on the products appearing below: the coefficient
of x^a u^b in G(σ) receives contributions only from k ≤ a and from the first
⌊b/val(σ−1)⌋ terms of the binomial expansion of σ^k = (1+(σ−1))^k — finitely
many. s0 − 1 = y·s0/(1−x·s0) has u-valuation 2; σ± − 1 = ±u/(1∓u) has
u-valuation 1. Formal s-derivatives stay in S.

## 3. Solving the opening phase [proved]

(E0) is linear with no catalytic coupling:

    F00(s) = x y s (1−xs) / ((1−xs)² − y)                               (1)
    F00(1) = x y (1−x) / ((1−x)² − y)                                   (2)

## 4. Kernel method for the staircase phase [proved modulo §7 checks]

Multiply (E1) by W(s) = (s−1)(1−xs) and collect F10(s):

    F10(s)·P_K(s) = y·B[F00](s)·W(s) + y·F10(1)·Q(s)                    (3)
    P_K(s) = (s−1)(1−xs) − ys,   Q(s) = xs(s−1) − s   [king]
                                 Q(s) = −s             [polyomino]

P_K(s) = −(x s² − (1+x−y)s + 1) has discriminant (1+x−y)² − 4x = Δ — the
convex-polyomino radicand appears identically for the king model. Its unique
power-series root is s0 (constant term 1; the other root ∼ 1/x). Substituting
s = s0 (legal by §2) kills the left side:

    F10(1) = −B[F00](s0)·W(s0)/Q(s0) = y·B[F00](s0)/(1 + x − x·s0)      (4)

using W(s0) = y·s0 and, for the king case, Q(s0) = −s0(1+x−xs0). Note
1 + x − x·s0 = ((1+x+y) + √Δ)/2: the (1+x+y) weight of the fitted closed
form enters here. Then (3) determines F10(s) as an explicit rational
function of s over Q(x,y,√Δ).

## 5. Kernel method for the closing phase [proved modulo §7 checks]

Collect F11 in (E2):

    F11(s)·[(s−1)² − y s²]/(s−1)² =
        y·D1[F00](s) + 2y·D2[F10](s) − y·[s²F11(1) + s(s−1)F11′(1)]/(s−1)²

The kernel (s−1)² = ys² has the two roots σ± = 1/(1 ∓ u), both admissible
(§2). Substituting and using (σ−1)/σ = ±u:

    F11(1) ± u·F11′(1) = y·D1[F00](σ±) + 2y·D2[F10](σ±)                 (5)

Averaging the two equations (the ± mirror exchanges them; odd powers of u
cancel — machine-checked identically zero):

    F11(1) = ½ Σ_± [ y·D1[F00](σ±) + 2y·D2[F10](σ±) ]                   (6)

D2[F10] requires F10(1) (from (4)) and F10′(1) (formal derivative of the
explicit (3)); all ingredients are explicit elements of Q(x,u,√Δ).

## 6. Assembly and identification

    F(x,y) = F00(1) + 2·F10(1) + F11(1)

with (2), (4), (6): an explicit element of Q(x,y,√Δ) (evenness in u of (6)
machine-checked). This proves F is ALGEBRAIC. Machine verification
(`experiments/s03_kernel_solve.py`, `out_s03_kernel_solve.txt`; exact
truncated-series arithmetic executed independently mod p1 = 2^61−1 and
p2 = 10^18+9):

- the assembled F matches the (brute-force validated) DP table f(w,h) on all
  144 cells w,h ≤ 12, in BOTH king and polyomino modes, at both primes;
- the king F satisfies session 02's algebraic equation A2F² + A1F + A0 = 0
  (A2 = Δ⁴K, K = x+y+xy; all coefficients in the computed box vanish), i.e.
  the derived expression agrees with the fitted closed form
  F = −(M + 2x²y²(1+x+y)²√Δ)/(2KΔ²) to the computed order;
- internal consistency: val_{s=1} of the solved F10 SRat equals the kernel
  formula (4); the kernel-root residual P_K(s0) vanishes; D1/D2/L3 match raw
  transition sums.

## 7. Closing the identification on the full sufficient degree box

Steps (4)–(6) produce an explicit algebraic expression; identifying it with
s02's closed form is the polynomial identity

    T1:   2·K·Δ²·F + M + S·√Δ = 0,   S = 2x²y²(1+x+y)², M = A1/Δ².

This was closed as follows (`experiments/s03_specialize_close.py`,
`out_s03_specialize_close.txt`):

- Degree bounds. `experiments/s03_degree_bounds.py` mirrors every field
  operation of the pipeline in a degree-bound semiring over Q(x,u)[√Δ]
  (denominators tracked as formal products of the actually-inverted atoms)
  and proves the numerator components (P,Q) of T1 (rational and radical
  part) have deg ≤ (79,119) in (x,u) (`out_s03_degree_bounds.txt`).
- Lex-min/Newton-polytope argument: if P + Q·√Δ ≠ 0 with Δ not a square,
  then (P+Q√Δ)(P−Q√Δ) = P² − Q²Δ ≠ 0 has componentwise degree
  ≤ (2·79+2, 2·119+4) = (160, 242), and the lex-min monomial of P + Q√Δ,
  being componentwise ≤ that of the product, lies in the box (160, 242).
  So vanishing of the series T1 on that box forces P = Q = 0.
- Part A (exact over Z, no truncation): A2 = Δ⁴·K, A1 = Δ²·M (exact
  division, zero remainder), 4K·A0 = M² − ΔS², A1² − 4A2A0 = Δ⁵S² — the
  structural identities fitted in s02 re-verified as integer polynomial
  identities. They imply by direct expansion that −(M+S√Δ)/(2KΔ²)
  satisfies A2F²+A1F+A0 = 0:
  numerator = KΔ⁴[(M²+2MS√Δ+S²Δ) − 2M(M+S√Δ) + (M²−ΔS²)] = 0.
- Part B (specializations): for each c = 2,…,85 (84 > 79+1 distinct values)
  the entire kernel pipeline was rerun specialized at x = c (univariate
  series in u to degree 250) and T1 checked to u-degree 242. For every
  c ≠ 0,1, Δ(c,u²) has four distinct roots (disc_y = 16c ≠ 0,
  αβ = (1−c)² ≠ 0), hence is not a square, so per-c vanishing forces
  P(c,·) = Q(c,·) = 0; 84 values force P = Q = 0 since deg_x ≤ 79.
  All 84 × 2 runs pass at both p1 = 2⁶¹−1 and p2 = 10¹⁸+9; series validity
  245 ≥ 242.

RESIDUAL CAVEAT (the only one in the whole chain): Part B certifies
P = Q = 0 modulo p1 and p2 (jointly ≈ 2.3·10³⁶), not over Q — a false
coefficient would need numerator divisible by both primes. Everything else
(functional equation, uniqueness, substitution lemma, kernel logic, Part A)
is exact. An exact-Q rerun of Part B (Fraction arithmetic, ~hours in pure
Python) or a height bound would remove the caveat mechanically.

ADDENDUM (session 04, 2026-08-15): CAVEAT REMOVED. Part B was rerun in
exact rational arithmetic (`experiments/s04_kernel_solve_exact.py`, a
line-for-line Fraction twin of the mod-p pipeline, sanity-gated against the
DP table; `experiments/s04_exact_close.py`, 84 specializations c = 2..85 to
u-degree 245 ≥ 242, in parallel): T1 vanishes identically over Q on the
full sufficient box — zero failures (`out_s04_exact_close.txt`, 44 s wall
on 60 cores). The identification, and hence the entire theorem, is now
exact with no modular hypothesis anywhere in the chain.

## Receipts

`experiments/s03_funceq_check.py` → `out_s03_funceq_check.txt` (exact, both
modes); `experiments/s03_kernel_solve.py` → `out_s03_kernel_solve.txt`
(two primes, both modes, six check layers); `experiments/s03_degree_bounds.py`
→ `out_s03_degree_bounds.txt`.
