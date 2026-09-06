# The diagonal formula of the height triangle

T(n,H) is the number of fixed polyplets (king-connected animals) with n
cells whose bounding box has height exactly H. For fixed k the diagonal
T(n, n−k) is a polynomial in n times a power of 3: shape, range and
integrality are theorems (`docs/proofs/diagonal-law.md`, Lean-checked), the
polynomials are the coefficients of one exponential in n
(`docs/proofs/grand-form.md`), and the same holds on every row-local lattice
(`docs/proofs/universal-diagonal-law.md`). This file records the mechanism
behind those theorems (the row model and its cluster weights, exact order by
order, carrying the mod-3 structure), the measured facts about the
polynomials, the production matrix, the columns and the fixed-height
generating functions, and the negative results on every other slicing.
Grades: proved, derived (exact algebra on enumerated weights), measured
(exact arithmetic on the enumerated triangle), or estimated.

## The law

Write k = n − H for the surplus of cells over the height. The **onset** of a
diagonal formula is the least n from which it holds; below onset the formula
is wrong, not approximately right.

**Theorem** (`docs/proofs/diagonal-law.md`). For every k ≥ 0 there is a
polynomial P_k of degree k with

    T(n, n−k) = P_k(n) · 3^(n−1−3k)   for all n ≥ 2k+1,

and P_k takes integer values at every integer. [n^k]P_k = 25^k/k!
(`docs/proofs/grand-form.md`, Corollary 2). The formula fails at n = 2k for
every k ≥ 1 (proved 2026-09-05; `results/below-onset.md`).

| k | closed form | onset |
|---|---|---|
| 0 | 3^(n−1) (the king chain, A000244) | all n |
| 1 | (25n − 45)·3^(n−4) = 5(5n − 9)·3^(n−4) | n ≥ 3 |
| 2 | ½(625n² − 2459n + 1134)·3^(n−7) | n ≥ 5 |

k = 1, 2 are proved by hand in `docs/proofs/T-n-nm1.md` and
`docs/proofs/T-n-nm2-and-general.md`. The onset is 2k+1, not k+2: at n = 4,
P_2(4)·3^(4−7) = 649/27 while T(4,2) = 27. k!·P_k ∈ ℤ[n] for all k (Lean
`production_factorial_int`), the engine's storage form; k! is not the least
denominator, the 5-part drops (`results/arithmetic-structure.md`). The
monomial coefficients are never all integers for k ≥ 2 (P_2 leads with
625/2); the binomial-basis coefficients are integers, checked k = 1..19.

**How P_8 was determined** (`scripts/pin_diagonal_k8.py`, deleted in
78602f8; exact rational arithmetic on the a(23) triangle). With the leading
coefficient fixed at 25^k/k!, k values in range determine P_k; this
reproduced P_7 and predicted the withheld entries T(22,15), T(23,16). For
k = 8 the seven values n = 17..23 were one short of T(24,16). The sum of
roots s_k = −c_(k−1)/c_k is quadratic in k (second differences 0.334;
s = 3.934, 6.403, 9.206, 12.344, 15.816, 19.622 for k = 2..7; a fit on
k = 2..6 predicts s_7 exactly), and s_8 = 23.763 predicted

    T(24,16) = 42 594 477 635 772 598,

confirmed exactly by `results/ns_a36/perheight/h16.out`, row n = 24. The
a(25) run then computed H ≤ 16 directly and the formulas gave H ≥ 17. Above
k = 8 each P_k is fixed from two values in range by the grand form
(`scripts/derive_pk_fast.py`); k ≤ 18 is verified on further entries,
k = 19 has none withheld and certifies nothing.

**Literature.** k = 0 is A000244; k = 1..5 are not in the OEIS and are not
submitted separately (`results/oeis-candidates.md`). No published closed
forms for T(n, n−k) of any animal family were found; the nearest relative
is the polycube dimension defect (`docs/proofs/universal-diagonal-law.md`
§Prior art).

## The row model and the cluster weights

Read a height-H animal row by row. With one cell per row it is a walk with
offsets {−1, 0, +1}: 3^(H−1) = T(H,H). An animal of surplus k is the walk
plus k cells forming **clusters**, maximal runs of rows with two or more
cells; a cluster's type is its stack of row sizes (s_1, …, s_ℓ), s_i ≥ 2,
its surplus Σ(s_i − 1) ≥ ℓ. A one-cell row is a cut vertex, so clusters at
row separation ≥ 1 compose as a Markov chain with exactly factoring
weights; only adjacent clusters interact. The **interior weight** W of a
type counts its connected configurations with a fixed one-cell row below
and a free one above; the **boundary weight** W^b omits the row below.

As a transfer DP over row contents and connectivity partitions
(`experiments/defect_gas.py`), sharing nothing with the production engine
or Redelmeier's algorithm, the model reproduces T(H+k, H) for k ≤ 3, H ≤ 8
(k ≤ 2 to H ≤ 10). Three window bugs, recorded so they are not
rediscovered: a naive cap on a cluster's spread, a gap cap from the
remaining budget, and a transfer window of 6 (clips W(2,2,2) to 4776) all
undercount silently; gaps may be bridged by cells already placed below, and
the only sound reach bound is the cost of carrying a disconnected block, at
least one surplus per row while it closes at most two columns per row.

**25 = 16 + 9** (proved). An adjacent pair has 4 contact positions below
times 4 above; a gap pair is joined only through the middle, so the contacts
must cover both cells and not be disjoint singletons, 9. T(4,3) =
15 + 25 + 15 = 55.

**Theorem** (single-row weights, proved 2026-07-12). The interior weight of
a one-row cluster of s cells is (2s+1)², its boundary weight 2s+1: 25, 49,
81, 121, 169 for s = 2..6. *Proof.* A gap of width 2 must be bridged by the
contact cell below or above standing at its middle (wider gaps need surplus
cells), and one cell bridges at most one gap. A row with j wide gaps
contributes (s+2)² for j = 0, 2(s+3) − 1 for j = 1, 2 for j = 2, nothing
for j ≥ 3, and (s+2)² + (s−1)(2s+5) + C(s−1, 2)·2 = (2s+1)². ∎ Interior =
entry factor × exit factor; the boundary weight is the entry factor.

**The k = 2 decomposition** (exact interior weights, normalized by 3^(H−5)):

| cluster type | coefficient of H | note |
|---|---|---|
| one row of three | 441 = 21² | |
| two adjacent pair rows | 1017 = 9·113 | the only interaction |
| two pair rows at separation 1 | 625 = 25² | exact factorization |
| pair rows at separation ≥ 2 | 625/2 · H² leading | independent, unordered |

The pieces sum to P_2(H+2) = 625/2·H² + 41/2·H − 642 symbolically: b_1 = 25
is the single-cluster density, b_1²/2 the pair term, b_2 = −209/2 the net
short-range correction. Mod 3: 25 ≡ 1, 441 ≡ 1, 1017 ≡ 0 (mod 9).

**General weights** (`cluster_weight()` in `experiments/defect_gas.py`; the
row-transfer DP `experiments/cluster_weight_dp.py` counts a type without
listing it and agrees with all 21 enumerated weights):

| type | W | surplus | rows |
|---|---|---|---|
| (2) | 25 | 1 | 1 |
| (3) | 49 | 2 | 1 |
| (4) | 81 | 3 | 1 |
| (2,2) | 339 = 3·113 | 2 | 2 |
| (2,3) = (3,2) | 930 = 3·310 | 3 | 2 |
| (3,3) | 3325 | 4 | 2 |
| (2,4) | 1993 | 4 | 2 |
| (2,2,2) | 4778 = 2·2389 | 3 | 3 |

Boundary: (2,2) = 66, (2,3) = 177, (3,2) = 130, (2,2,2) = 919.
W(2,2,2,2) = 68 314; all pairs at six rows 14 115 141; W(2^10) =
607 573 757 457, ratios 14.398, 14.404, 14.405, 14.407 at ℓ = 7..10. The
all-pairs family is **not C-finite**: an order-7 recurrence fitted on ℓ ≤ 14
predicts a non-integer at ℓ = 16; the gap between pending blocks is an
unbounded ±2 walk, so the generating function is at best algebraic.

**Two-row weights** (`cluster_weight_dp.py pair a b`, 2026-08-01; wall in
seconds; W(5,5) alone 8.4 h):

| (a,b) | (2,6) | (2,7) | (2,8) | (3,5) | (3,6) | (3,7) | (4,4) | (4,5) | (5,5) |
|---|---|---|---|---|---|---|---|---|---|
| W | 6111 | 9454 | 13845 | 19671 | 38422 | 68385 | 28559 | 74710 | 226545 |
| wall | | 178 | 1502 | 89 | 1144 | 13388 | 120 | 1975 | 30137 |

W(2,b) = 24b³ + 20b² + 35b − 3 (fitted b = 2..5, exact at b = 6, 7, 8).
W(3,b) = 24b⁴ + 16b³ + 110b² − 19b + 16 (fitted b = 2..6, exact at b = 7;
fourth differences 576 = 24·4!). So deg_b W(a,·) = a+1 and no bivariate
polynomial of fixed degree describes W(a,b); both rows lead with 24. W(4,·)
has four of the six points it needs; W(4,6) is about a day in Python.
W(n,n) = 339, 3325, 28559, 226545, ratios 9.81, 8.59, 7.93; no shape fitted.

Full-catalog DP cost in Python: k = 4, 3.1 s; k = 5, 65 s; k = 6, more than
530 s; about 20× per level, so about 10^17 s at k = 17, and C++ with a
thousand cores buys five orders. Reach k ≈ 7 in Python, 9–10 in C++;
certifying P_17 this way is priced out, direct enumeration to height 20
being the only route.

## The master equation and the boundary factor

Macro-steps are a walk step (weight 3z) or a cluster with the walk row above
it (W_c y^(k_c) z^(ℓ_c+1)); the per-row growth solves 1 = 3z + Σ W_c y^(k_c)
z^(ℓ_c+1) at z = 1/μ, so μ = 3 + Σ_c W_c y^(k_c) μ^(−ℓ_c) ([y²] of the
per-row log is 347/54 both ways). With μ = 3H(u), u = yμ/27:

    H(u) = 1 + Σ_c Ŵ_c u^(k_c) H^(−(k_c+ℓ_c)),   Ŵ_c = W_c · 3^(2k_c−ℓ_c−1).

H(u) = 1 + 25u + 208u² + 1483u³ + 20688u⁴ + 130208u⁵ + … is the series the
grand form calls e^B. The k = 2 numbers 441 = 49·9 and 1017 = 339·3 are the
natural weights Ŵ (the source first called them normalization artifacts;
the later statement holds). Exact through u³: h_2 = −2·25² + 441 + 1017 =
208; h_3 = 1483 from Ŵ = 6561, 25110, 25110, 43002 (`check_master()`). With
all 31 types of surplus ≤ 5 the equation returns H = [1, 25, 208, 1483,
20688, 130208] (`check_grand_form()` in `experiments/cluster_weight_dp.py`).
Two pathologies: fixed-point iteration of μ in exact rationals blows up on
pre-convergence garbage, so solve order by order; the u-series H is not the
y-series μ, and mixing them breaks the residue formula at order 1.

**Valuation lemma** (proved). Every cluster row carries a surplus, so k ≥ ℓ
and v_3(Ŵ) = 2k − ℓ − 1 + v_3(W) ≥ k − 1 ≥ 1 for every type except the bare
pair row (k = ℓ = 1, Ŵ = 25 ≡ 1 mod 3). Consequences, each verified against
all 18 known coefficients of H:

- mod 3: H = 1 + uH^(−2), i.e. H³ = H² + u, the cubic of the triangle's
  mod-3 structure (`results/arithmetic-structure.md`): mod 3 the gas is a
  gas of bare pair rows.
- mod 9: 441 + 1017 = 1458 ≡ 0, so H³ = H² + 25u ≡ H² + 7u.
- mod 27: every k ≥ 4 type dies, leaving
  H = 1 + 25uH^(−2) + 441u²H^(−3) + 1017u²H^(−4) + 43002u³H^(−6).
- mod 81: six terms, the four-pair stack entering at Ŵ ≡ 27; unique fixed
  point (`experiments/spine_deeper.py`).

**Boundary factor.** With E_b = z(1 + Σ W^b y^k z^ℓ), E_t its reversal,
D = 1 − 3z − Σ W y^k z^(ℓ+1) and a pure-cluster polynomial, the chain
identity F(y,z) = E_b E_t/D + pure reproduces all 40 enumerated entries with
k ≤ 3, H ≤ 10. The residue at z* = 1/μ gives G, verified through u³ and,
with the k ≤ 5 catalog, through u⁵: G = [1, −5, −62/9, −1625/81,
−56842/729, −2170913/6561].

    G = ε_b ε_t (1 − wH′) / (1 + Σ_c (ℓ_c+1) Ŵ_c u^(k_c) H^(−(k_c+ℓ_c))),
    ε = 1 + Σ_c B̂_c u^(k_c) H^(−(k_c+ℓ_c)),   B̂_c = W^b_c · 3^(2k_c−ℓ_c).

**G ≡ 1 (mod 9)** (derived). v_3(B̂) ≥ 2k − ℓ ≥ k kills every boundary type
mod 9 except the pair row (B̂ = 15); the denominator reduces to
1 + 50uH^(−2) (ℓ = k = 2 survives through ℓ+1 = 3). What remains,
(1 + 15uH^(−2))²(1 − uH′/H) ≡ 1 + 50uH^(−2), collapses to
H²H′ + 3uH′ + 2H ≡ 0 (mod 9); with u = 4(H³ − H²) from the mod-9 cubic and
its derivative identity (3H² − 2H)H′ ≡ 25, H′(3H³ − 2H²) + 2H = 27H ≡ 0. ∎

**G mod 27** (derived): only the pair-row boundary survives, the denominator
keeps 50uH^(−2) + 18u²H^(−3) + 18u³H^(−6), and the residue reproduces every
known g_j mod 27.

**The mod-9 identity for H(u³)** (proved 2026-07-13). Let X ∈ (ℤ/9)[[u]] be
the unique solution of X³ = X² + 25u with X(0) = 1, and W = X mod 3. Then

    H(u³) ≡ X² + 25u − 3u² − 3uW (mod 9),  hence
    S = (H³ − H(u³))/3 ≡ u² + uW (mod 3).

*Proof.* (i) Y := H(u³) mod 9 satisfies Y³ = Y² + 25u³, Y(0) = 1; dividing
by the unit Y² gives Y = 1 + 25u³Y^(−2), whose coefficients are forced
recursively. (ii) Y* = X² + 25u + 3E with E = −u² − uW satisfies the same
cubic: mod 9, (A+3E)³ ≡ A³ and (A+3E)² ≡ A² + 6AE, so with A = X² + 25u =
X³, Y*³ ≡ X⁹ and Y*² ≡ X⁶ + 6EX³. Expanding X⁹ = (X² + 25u)³ termwise mod 9
(3·25 ≡ 3, 3·625 ≡ 3, 25³ ≡ 1): X⁹ ≡ X⁶ + 3uX⁴ + 3u²X² + u³. Hence
Y*³ − Y*² − 25u³ ≡ 3(uX⁴ + u²X² + u³ + EX³) (mod 9), and the bracket
vanishes mod 3: with X ≡ W, X³ ≡ W² + u, X⁴ ≡ W² + u + uW, it is
uW² + u² − uW³ = uW² + u² − u(W² + u) = 0. (iii) By uniqueness Y = Y*, and
H³ − H(u³) ≡ X³ − Y* = 3u² + 3uW. ∎ Machine checks (`check_ladder()` in
`experiments/defect_gas.py`): the identity holds on the algebraic fixed point
to u^300 and against the 18 enumerated coefficients; the bracket
cancellation is re-verified as an F_3 identity.

**Deficit-2 congruence.** T(3m+2, 2m+1) ≡ 2 (mod 3), supported by data to
m ≈ 11, holds on the derived series for m = 1..94 (P_(m+1)(3m+2) ≡ 18 mod
27 from the mod-27 and mod-81 fixed points and G mod 27); symbolic closure
open here, later state in `results/arithmetic-structure.md`.

**Onset sharpness from the gas**: deg R_k = 2k+1 exactly for k ≤ 5 (leading
coefficients 1, 4, −80, 1753, −40928, 987355, alternating from k = 2, ratio
drifting toward about 24); the general proof came by another route
(`results/below-onset.md`).

Grade: chain identity exact; master equation and G by the Lagrange step of
`docs/proofs/grand-form.md`; each mod-3^j statement rests on the finitely
many weights entering that modulus (five integers mod 27).

## Holes

The hole-free triangle has its own law with hole-free weights: pair row
25 → 24 (the one holed configuration is the minimal diamond, a gap pair
bridged below and above), triple 49 → 47, stacked pairs 339 → 304, boundary
5, 7 unchanged and 62 for stacked pairs. The master equation and residue give

    P⁰_1(n) = 24n − 42,   P⁰_2(n) = 288n² − 1113n + 507,

exact against every enumerated hole-free fixed-height value (H ≤ 8, 5 + 3
withheld); 288 = 24²/2. Since 24 ≡ 0 (mod 3), the hole-free triangle is
mod-3 trivial in range and the full triangle's mod-3 structure lives in the
hole-making configurations (`experiments/holefree_gas.py`).

With a hole marker z (pair row 24 + z, triple 47 + 2z, stacked pairs
304 + 33z + 2z², boundary 5, 7, 62 + 4z), the marked equation gives the
stratified laws, exact on all 26 enumerated hole-resolved entries (j ≤ k ≤ 2,
H ≤ 7; `experiments/hole_strata_gas.py`):

    P_1(n,z) = (24n − 42) + z(n − 3),
    P_2(n,z) = (288n² − 1113n + 507) + z(24n² − 117n + 75) + z²(n+6)(n−5)/2.

**Mod-3 concentration** (derived). Mod 3 the marked equation collapses to
H(u,z) ≡ W(zu): on diagonal k only the maximal-hole stratum j = k survives
and inherits the cubic, and every z⁰ and z¹ coefficient above is divisible
by 3. The one-hole diagonal is T_1(n, n−1) = (n−3)·3^(n−4); the binomial
guess for higher strata fails because clusters carry several holes
(T_2(7,5) = 13, not 1).

## Other lattices

On every row-local lattice with b up-neighbors per cell, T(n, n−k) =
P_k(n) b^(n−1−3k) for n ≥ 2k+1 (Theorem A of
`docs/proofs/universal-diagonal-law.md`), and mod a prime p | b the series
obeys H³ = H² + wu with w the pair weight mod p (Theorem B).

**Polyhexes** (b = 2; cells are hexagons, A001207). T(H,H) = 2^(H−1).
Measured by `experiments/hex_gas.py` (brute enumerator checked against
A001207 to n = 10; row-transfer DP checked entry by entry against it):

    P_1 = 9n − 15,   P_2 = (81n² − 307n + 142)/2.

`experiments/hex_diag_deep.py` (2026-09-05) raises the surplus budget from 2
to 6 by building each row left to right and abandoning dead prefixes: 140
entries, H ≤ 20, 19 s, in `results/hex_diagonal_cells.txt`, checked against
brute force for n ≤ 9. Fits give P_1..P_6 with 72 withheld entries exact,
leading coefficients 9^k/k!, and

    P_3 = (243n³ − 1548n² + 1897n + 56)/2,
    P_4 = (2187n⁴ − 20574n³ + 46657n² − 4502n − 67336)/8.

P_3 agrees with the drift-parametric DP of the universal-law proof; P_4 is
the second route to the hex cumulant A_4 = 3915/4. Single-row weights are
(s+1)² for solid runs only (9 = 3² at s = 2); gap pairs weigh zero, since
hex up and down neighbors {x−1, x} cannot bridge a gap. Mod 2 the master
equation collapses to the pair row (Ŵ = W·b^(2k−ℓ−1), the valuation lemma
being lattice-independent), giving H³ = H² + u over F_2. The boundary
factor differs, G ≡ 1 + uH^(−3) (mod 2) (the king cancellation is
3-specific), so P_k(n) mod 2 = [u^k](1 + uH^(−3))H^n: zero mismatches on all
in-range entries H ≤ 14, k ≤ 2. Unit-ness of the pair weight: w ≡ 4 (mod p)
for odd p | b, w ≡ ⌊b/2⌋ (mod 2) for p = 2, degenerate iff 4 | b
(`docs/proofs/universal-diagonal-law.md` §Instances). Higher-coordination
lattices are open.

**Polyiamonds** (animals of equilateral triangles, A001420). Cell (x,y) is
an up- or down-triangle by the parity of x + y; adjacency is (x±1, y) always
and (x, y+1) iff x + y is odd. No single drift set exists, so condition (U)
fails; condition (M) holds with the rhombus (a receiver glued to a
horizontally adjacent sender) as row unit, m = 2, b = 2, the rhombus walk
being the polyhex walk in j = ⌊(x−y)/2⌋, and Theorem A gives a plain
polynomial rather than a period-2 quasi-polynomial. The least cell count at
height H is 2H − 2 (a cell receiving from below has even parity and cannot
send up). With n = 2H − 2 + k (`experiments/polyiamond_diagonal.py`, about
7 min; hypotheses checked by `experiments/polyiamond_fibre_check.py`, about
20 s; DP checked against brute force for all (n,H) with H ≤ 8, window 6
stable against 8):

| k | onset | T(2H−2+k, H) / 2^H | withheld |
|---|---|---|---|
| 0 | H ≥ 2 | 1/4 | 12 |
| 1 | H ≥ 2 | H/2 | 11 |
| 2 | H ≥ 3 | H²/2 + 11H/16 − 13/16 | 9 |
| 3 | H ≥ 3 | H³/3 + 11H²/8 − 29H/24 | 8 |
| 4 | H ≥ 4 | H⁴/6 + 11H³/8 + 59H²/384 − 137H/128 − 65/32 | 6 |

Theorem A guarantees H ≥ k+1; the measured onsets are ⌊k/2⌋ + 2, since each
row buys two cells. Normalized by q_0 = 1/4 the leading coefficients are
W^k/k! with W = 2 (lead·k! = 2, 4, 8, 16) and the cumulants are linear in
H: c_1 = 2H, c_2 = 11H/4 − 13/4, c_3 = 5H/3, c_4 = 149H/32 − 429/32. W = 2
is measured in H, not counted as a gadget. A first version budgeted by the
height's allowance 2H − 2 + k and undercounted the top diagonal (376 → 262
at (8,3)); the sound budget is the surplus over the per-row minimum,
s = used − (2h − 1).

**King against square** (`experiments/cross_lattice.py`).
`results/bbox_square4_n21.txt` summed over width gives the square height
triangle (row sums equal A001168, n ≤ 21). Down each diagonal n − H = k the
successive ratio of T_king/T_square converges to 3.000 (exact at k = 0;
2.998, 2.980, 2.94 at k = 1, 2, 3, rising with H), as b = 3 against b = 1
predicts. Off the diagonals the ratio grows smoothly with no structure.

## The production matrix and the 3-adic band

`experiments/production_matrix_probe.py` computes P = L^(−1)L̄ for L the
18×18 block of the triangle (`results/ns_a36/perheight/h{H}.out`), L̄ its
shift up one row. Not Riordan: 89 Toeplitz violations of 289. Not banded:
every row m has support H ∈ [2, m+1], so there is no finite production rule
and no constant-coefficient 2-D recurrence. The band near the diagonal is
eventually Toeplitz, offset −k settling at row about 2k+3:

| offset H−m | +1 | 0 | −1 | −2 | −3 | −4 |
|---|---|---|---|---|---|---|
| constant | 3 (exact) | 25/9 | 208/243 | 1483/6561 | 6896/59049 | 130208/4782969 |
| stable from row | 1 | 3 | 5 | 7 | 9 | 11 |

The band constant at offset −k has natural denominator 3^(3k+2)
(`experiments/band_constants_3adic.py`, c_k·3^(3k+2) ∈ ℤ for k = 0..6):

| k | 0 | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|---|
| natural | 3² | 3⁵ | 3⁸ | 3¹¹ | 3¹⁴ | 3¹⁷ | 3²⁰ |
| reduced | 3² | 3⁵ | 3⁸ | 3¹⁰ | 3¹⁴ | 3¹⁷ | 3¹⁹ |

Reduction eats one 3 at k ≡ 0 (mod 3), where the numerator has v_3 = 1
(20688 = 3·6896, 36500568 = 3·12166856). The monomial-basis P_k denominators
do not follow 3^(3k+2) and from k = 2 are not pure 3-powers (3, 3⁴, 3⁷·2, …;
`experiments/Pk_denominator_check.py`), an interpolation artifact; in the
binomial basis (`experiments/Pk_newton_3adic.py`) v_3(P_k) = 3k+1 exactly
for k = 0..8, no anomaly at k ≡ 0 (mod 3). Band and diagonal differ by the
one factor 3 of L̄ = 3D·L̄′, P = 3P′. The Smith normal form is
all-3-power (`results/arithmetic-structure.md`). No global production rule
and no Riordan row-sum shortcut for a(n): the atom obstruction below and
the non-D-finiteness of a(n) (`results/anisotropic-not-dfinite.md`).

## Columns: atoms and the root-separation theorem

Data `results/ns_a35/perheight/h{H}.out`; `experiments/triangle_relations.py`,
`triangle_relations2.py`, `triangle_atoms.py`; exact arithmetic, fitted on
the earliest terms, checked on the rest.

**Columns H ≤ 4** have minimal constant-coefficient recurrences of orders 1,
3, 7, 15 from 35, 34, 33, 32 terms, confirmed on 33, 28, 19, 2 further
terms; H ≥ 5 cannot be fixed from 35 rows.

**One atom per height** (measured H ≤ 4). Let C_H(n) = Σ_(h≤H) (H−h+1)
T(n,h), what a naive height-H strip transfer matrix counts. Its minimal
characteristic polynomials, the atoms:

    q_1 = x − 1
    q_2 = x² − 2x − 1                       (Pell)
    q_3 = x⁴ − 4x³ + 2x² − 1
    q_4 = x⁹ − 5x⁸ + 2x⁷ + 8x⁶ − 6x⁵ − 12x⁴ + 4x³ + 2x² − 3x − 1

Degrees 1, 2, 4, 9, 29, 68, 181, 462, 1254, 3289 (novel by Superseeker).
Since T(n,H) = C_H(n) − 2C_(H−1)(n) + C_(H−2)(n), the column characteristic
polynomials factor as p_H = q_H q_(H−1) q_(H−2) (verified H = 2, 3, 4; atoms
pairwise coprime): orders 3 = 2+1, 7 = 4+2+1, 15 = 9+4+2, 42 = 29+9+4,
106 = 68+29+9. Each height contributes one new atom. The degrees over
H = 5..10 fit base 2.592 against √λ = 2.667 (ratios wander 2.34..2.71):
consistent with the row-direction complexity being the frontier size, not a
confirmation.

**Measured negatives.** No constant-coefficient stencil T(n,H) = Σ c·T(n−j,
H−δ) for any H = 5..12 (j ≤ 4, columns H−2..H+1, ≥ 4 excess equations); no
polynomial-coefficient recurrence to order 6 × degree 3 even at H = 3.
Fixing q_5 (order 29) from data needs about 60 rows, q_6 about 140.

**Theorem** (root separation). Any relation Σ_(j≤J,δ) p_(jδ)(n,H)·T(n−j,H−δ)
= 0 with polynomial coefficients, holding for all n at a window of columns,
has depth J ≥ deg q_(H_top), where H_top is the highest column whose
coefficient face is not identically zero. Ingredients (measured): q_1..q_4
squarefree and pairwise coprime, so T_H(n) = Σ_λ c_λ λ^n over distinct
roots, and minimality of the orders forces every c_λ ≠ 0. Factorials of
integer linear forms enter only through ratios of shifted factorials, which
are polynomials, and fixed exponentials cancel, so polynomial coefficients
are the whole class. *Proof.* Specialize H. Let λ be a root of q_(H_top). By
coprimality λ appears in columns H_top, H_top+1, H_top+2 only, of which only
H_top is in the stencil. The λ^n component of the relation is
Σ_j p_j(n) c_λ λ^(n−j) = 0, one constant-coefficient linear condition on
(p_0, …, p_J) over C(n). Over all deg q_(H_top) distinct roots this is a
Vandermonde system: if J+1 ≤ deg q_(H_top) the whole H_top face vanishes.
Recurse downward. ∎ (Galois conjugation extends it to any algebraic constant
field.) Any relation touching column 5 needs depth ≥ 29, column 6 ≥ 68; the
stencil searches were instances J ≤ 4, degree ≤ 6. Not forbidden: unbounded
stencils (k·P_k = Σ_(j≤k) j(a_j + b_j n) P_(k−j), `scripts/derive_pk_fast.py`);
directions of non-constant column composition (a diagonal mixes unboundedly
many atoms, which is why the P_k exist); non-holonomic coefficients.

**Entries with two independent computations.** Of the 630 entries with
n ≤ 35: 128 from the column recurrences, 216 from the diagonal formulas, 6
from both, 350 in all; a strip transfer matrix independent of the production
engine (`experiments/strip_engine.py`) adds 184 at H ≤ 12, leaving 96
single-computation entries at H = 13..23 and high n. Over the 820 entries
with n ≤ 40 the union covers 742, or 552 when a diagonal is credited only
where its fitting entries were enumerated, and the strip engine alone 413;
k = 19 excluded throughout. One validated strip column gives the whole T
column through the differencing identity. Counting rule and per-term
coverage: `results/second-sources.md`.

## The fixed-height generating functions against the triangle

`results/fixed_height_gfs.txt` holds G_H(x) = Σ_n T(n,H) x^n = P_H/Q_H for
H = 1..11, orders 1, 3, 7, 15, 42, 106, 278, 711, 1897, 5005, 13381.
`experiments/gf_head_check.py` (0.04 s) expands the first 41 coefficients of
each (tails past x^40 cannot reach the head) and compares with the triangle
for n = H..40: 385 entries, 385 agreements, every series vanishing below x^H.
Controls: all blocks cut to 41 coefficients still pass; P_11[20] += 1 and
Q_5[7] += 1 fail exactly at H = 5, n = 12 and H = 11, n = 20, exit 1. For
H ≤ 10 this corroborates the mod-p, Berlekamp–Massey and CRT recovery on 355
entries.

**H = 11 is wrong** (2026-09-05). The recovery tool (`gf/modp_recover.py`,
deleted in 91bdcdc) lifted H = 11 from a fixed pool of 133 primes below
2^31, half-modulus 1241 digits, while coefficients grow at 0.097 digits per
degree at every validated height (H = 9: 184 digits at degree 1897; H = 10:
486 at 5005) and reach about 1299 digits at degree 13381, six primes short:
370 of the 26764 coefficients sit within 10% of M/2, the largest at 0.999,
and at H = 10 none does. `experiments/gf_h11_validate.py` expands Q_11·B_11
against P_11 mod the fresh prime 1073741789, B_11 from `build/gf_modp`,
n = 0..26792: first mismatch at n = 8170, first bad coefficient at degree
8159, where the size crosses the 133-prime ceiling (engine 884.8 s,
comparison 1.1 s); H = 8, 9 pass, and the corrupted control fails at the
perturbed degree plus H. The earlier "Q_11 shares no roots with Q_9 Q_10 mod
p" was this wraparound. The file carries `refuted=2026-09-05
first_bad_degree=8159`; parsers keyed on `validated=True` or `order=` were
re-run green. Survives: order 13381 with deg N_11 = 8838 (agreed across all
133 primes); the strip certificates, which read validated entries only; and
μ_11 = 6.1158416, since `experiments/mu_H_from_atoms.py` bisects for the
least positive root and at x = 1/6.1158416 the tail from degree 8159
contributes 10^(−5177) against 10^(−32) for the head. `build/strip_mu 10 11`
(Perron iteration, never reading the file) gives μ_10 = 5.9916958,
μ_11 = 6.1158416 in 10.3 s; `cpp/strip_mu_kink.cpp` reproduces it by a third
construction.

Re-recovery, priced on gympie and not launched:

| H | primes | wall | CPU-s | workers | M/2 digits | coeff digits | matches |
|---|---|---|---|---|---|---|---|
| 8 | 40 | 4.9 s | 26.2 | 10 | 373 | 72 | exactly |
| 9 | 40 | 42.3 s | 252 | 10 | 373 | 184 | exactly |
| 10 | 57 | 870.8 s | 4065 | 8 | 532 | 486 | exactly |

H = 11 at N = 26792 is 884.8 s per prime single-threaded at 248 MB; the pool
grows to 194 primes, 47.7 CPU-hours plus a serial 38-minute order search:
about 6.4 h on gympie (10 workers, 2.5 GB) or 2.5 h on ayr (32 cores,
8 GB), resumable per (H, N, prime). A validated H = 11 breaks
`experiments/anisotropic_dfinite.py` (validated set 1..10) until deg ψ_11
is added.

## Slices off the diagonal

The lines n = sH + c, s ≥ 2, cross the band with neither a fixed-height
generating function (H ≤ 10) nor a diagonal formula (H ≥ (n+1)/2). Data
`results/ns_a40/perheight/`.

**No constant-coefficient recurrence** (`experiments/slope_slices.py`,
`slope_onset.py`): minimal recurrence in H by exact elimination, one
equation of slack, largest-H point withheld and predicted, first t = 0..7
points dropped. Control: s = 1 gives order 1 (root 3) at k = 0, (x−3)² at
k = 1, (x−3)³ at k = 2 once the pre-onset head is dropped.

| slice | points | minimal order, t ≤ 7 | ratio at last point |
|---|---|---|---|
| n = 2H | 20 | none | 41.445 |
| n = 2H+1 | 19 | none | 41.645 |
| n = 2H+2 | 19 | none | 41.907 |
| n = 3H | 13 | none | 327.41 |
| n = 3H+1 | 13 | none | 331.49 |
| n = 3H+2 | 12 | none | 338.39 |

Excluded: poly(H)·μ^H, deg ≤ 7, one base, at every onset to H = 8 (s = 3
ceiling about 5). Not excluded: degree ≥ 8 or onset past H = 8.

**No polynomial-coefficient recurrence** (`experiments/pfinite_slices.py`):
Σ_(i≤r) p_i(H) T(s(H−i)+k, H−i) = 0, deg p_i ≤ d, last two points withheld,
≥ 2 excess equations, t = 0..5. Control: s = 1 at (r,d) = (1,0), (2,0),
(3,0) for k = 0, 1, 2. None at s = 2, 3 in the reachable envelope (n = 2H:
r = 1, d ≤ 5; r = 2, d ≤ 3; r = 3, d ≤ 2; r = 4, d ≤ 1; r = 5, d ≤ 0.
n = 3H: r = 1, d ≤ 3; r = 2, d ≤ 1; r = 3, d ≤ 0). Only k = 0, 1, 2 per
slope.

**Structural reason.** On the k = n − H background every row is one cell, a
cut vertex, so the animal factors into finitely many cluster types per
surplus level. At slope 2 the background row has two cells and is not a
cut: the obstruction the perimeter grading meets (`results/perimeter.md`),
consistent with T(n,H) not being 2-D holonomic (`results/closed-doors.md`).

**Exponent fitting** (`experiments/slope2_ansatz.py`): fit on H ∈ [H_0, 17],
predict H = 18, 19, 20; models linear in log space (basis 1, H, ln H, √H,
1/H, 1/H²). Control on the last 20 terms of a(n), where 40 terms give
θ = −1.000(1) (`results/growth-constant.md`): C μ^H H^θ, with e^(c/H), with
ν^√H, with e^(c/H + d/H²) give θ = −0.961, −0.992, −0.898, −0.998 at
withheld errors 0.014%, 0.000%, 0.001%, 0.000%, so a tiny withheld error is
no evidence for an exponent at this length; free-θ fits on slope 2 spread
over +0.15 … −0.63 and are discarded. Locking θ and fitting μ discriminates:
on the control the minimum is at θ = −1.00 (0.181%) and ±0.25 costs
1.0–1.4%, so θ resolves to about ±0.25.

| θ locked | μ (slope 2) | error | control a(n) error |
|---|---|---|---|
| 0.00 | 40.83 | 6.47% | 4.69% |
| −0.25 | 41.85 | 1.13% | 3.49% |
| −0.50 | 42.89 | 4.51% | 2.28% |
| −1.00 | 45.05 | 16.77% | 0.18% (truth) |
| −1.50 | 47.32 | 30.47% | 2.71% |

On the s = 1, k = 2 slice (quadratic × 3^H) the locked scan minimizes at
θ = 2.00, μ = 3.014, residual 2.3% at the truth: only the exponent's location
carries information. The local 3-point θ on n = 2H drifts from −0.15 (H = 6)
to −0.38 (H = 20), Richardson near −0.5 (±0.1: the control returns 1.93 for
2.00); on the k = 2 control it drifts 2.56 → 2.03 with collapsing increments.
Factorials: unbalanced Gamma quotients are excluded by the converging ratio,
balanced ones by the μ^H H^θ family and the order-1 test; the Stirling fit
ln S = a + bH + c ln H + d(H ln H) gives d = +0.0011 on a(n), +0.0339 on the
k = 2 control (both truth 0), +0.0185, +0.0215, +0.0170 on slope 2 for
H_0 = 3, 5, 7, so the floor is about 0.03 and a real factorial power
(20–50× that) is excluded.

Verdict: μ_2 ≈ 41.8–42.5 by fitting, rising with the window (41.76, 41.90,
42.02 at H_0 = 3, 5, 7) against λ² = 50.55; θ unidentified in roughly
[−0.6, −0.2]; θ = −3/2 (friendly walkers) refuted at 19–52% withheld error;
θ is no small non-negative integer, so the slice is not a low-degree
polynomial times an exponential.

**Growth constants from the grand form** (`experiments/grand_form_saddle.py`,
2026-08-09). Σ_k P_k(n) y^k = exp(A(y) + nB(y)); a_j, b_j extracted for
j = 1..19 from the engine's P_1..P_19 come out linear in n, b_1 = 25,
a_1 = −45, an independent test only for k ≤ 8 (partly 9, 10), since
`scripts/derive_pk_fast.py` builds P_11..P_19 from the recurrence. On n = 2H
the surplus is k = H: the slope-2 line is the onset line, where the relative
defect is about e^(−1.55k) (`results/below-onset.md`), so slice and formula
share their exponential growth. With k = κH, κ = s − 1, the saddle of
(1+κ)B(y) − κ ln y at y·B′(y) = κ/(1+κ) gives (1/H) ln T → (1−2κ) ln 3 + φ(κ):

    μ_s = 3^(1−2κ) · exp(φ(κ)).

y* is 0.022–0.034; b_19 y*^19 = 4.5·10^(−7) at s = 2.

| J | 8 | 10 | 12 | 14 | 16 | 19 |
|---|---|---|---|---|---|---|
| μ_2 | 42.394991 | 42.394545 | 42.395421 | 42.394930 | 42.394566 | 42.394597 |

Spread over J = 8..19: 42.393686 to 42.395421, four and a half digits.
Against the ratios T(2H,H)/T(2H−2,H−1) extrapolated in 1/H by exact
elimination (`experiments/slope2_law_vs_truth.py`):

| route | μ_2 |
|---|---|
| grand-form saddle | 42.39460 |
| ratios, order 2 (H = 18..20) | 42.39549 |
| ratios, order 3 (H = 17..20) | 42.39426 |
| ratios, order 4 (H = 16..20) | 42.39455 |

Two estimators on one enumeration. The supportable agreement is about 3
parts in 100,000; the fitting record's closing note said 6 parts in a
million from one pair of endpoints, and the saddle record, the later one,
holds. The raw ratio at H = 20 is 41.445, which is why the fits drifted up.
Higher slopes (b_19 y*^19 reaches 1.1·10^(−3) at s = 5):

| s | grand form | last measured ratio | Richardson | points |
|---|---|---|---|---|
| 2 | 42.3946 | 41.445 (H = 20) | 42.278 | 19 |
| 3 | 330.83 | 327.41 (H = 13) | 318.45 | 12 |
| 4 | 2434.1 | 2596.0 (H = 10) | 2194.7 | 9 |
| 5 | 17609 | 21356 (H = 8) | 16447 | 7 |

μ_2 to about 4.5 digits, μ_3 ≈ 331 to about three, s ≥ 4 illustrative. The
saddle cannot reach past P_19; the b_j alternate irregularly and |b_j|^(1/j)
still climbs at j = 19 (20.83), so the radius of B is unresolved and the
saddle is safe only because y* is an order of magnitude inside it.

**λ from the production constants** (`experiments/lambda_from_grand_form.py`).
A ray n = sH contributes μ_s^(n/s), so λ = sup_s μ_s^(1/s), attained as
s → ∞ since the typical box has H ~ c√n; then y_c B′(y_c) = 1 and

    ln λ = B(y_c) − ln y_c − 2 ln 3,

with no enumeration count in it.

| s | 2 | 3 | 4 | 6 | 8 | 10 | 20 | 40 |
|---|---|---|---|---|---|---|---|---|
| μ_s^(1/s) | 6.5111 | 6.9162 | 7.0240 | 7.0854 | 7.1028 | 7.1099 | 7.1175 | 7.1185 |

The direct s → ∞ form solves for 7 of J = 10..19 (J = 13, 15, 18 have no
solution, the truncated series not being monotone there): 7.065, 7.015,
7.134, 7.147, 7.079, 7.127, 7.118, midrange 7.081, spread ±0.066. So
λ = 7.08 ± 0.07 from the grand form alone, against 7.110(1) from series
analysis (`results/growth-constant.md`); the interval is the result. Two
caveats: |b_j|^(1/j) puts the radius of B near 0.048 while y_c ≈ 0.0373 and
the last term is 8·10^(−3); and the limit needs the formula to track the
truth as x = H/k → 0, measured only to x = 0.10 (`results/below-onset.md`),
so s = 15, 20, 40 (x = 0.07..0.026) rest on extrapolation. Untried: Padé or
differential approximants on B(y).

## Other combinations of the triangle

`experiments/triangle_combinations.py`, `alt_sign_runs.py`,
`parity_amplitude.py`, n ≤ 40. Novelty against the literature is unchecked.

- **Log-concavity holds everywhere**: every row in H (n = 3..40) and every
  column in n (H = 1..20), 820 entries, no exception. Not by real-rootedness
  (row 40 has 9 real roots of 39, max |Im| = 2.01). Distinct from the open
  log-concavity of a(n) (`results/closed-doors.md`).
- **Row polynomial at special points**: F_n(y) = Σ_H T(n,H) y^H at y = −1,
  1/3, −1/3, 3, 9, 1/9 has no constant-coefficient recurrence in n of order
  ≤ 8, last point withheld. Integrality at y = −1, 3, 9 only.
- **Alternating row sum** F_n(−1) is 1.16·10^(−6) a(40), sign runs 3, 5, 5,
  8, 8, 8 for n = 4..40 (growing, so no fixed conjugate singularity pair).
  The phase tracks π·mean_H(n), mean_H ~ n^0.687 (n ≥ 12); 3 of 5 flips fall
  at half-integer crossings, but run lengths give n^0.465, not an exponent
  estimator. Amplitude 20 orders above the Gaussian exp(−π²w²/2) ≈ 10^(−26)
  at w = 3.42; fitting ln(|F|/a) on n ≤ 33 and predicting 34..40, exp(−αw),
  α = 4.04, errs 1.33 in ln against 2.21 for exp(−βw²). The height
  distribution is not Gaussian at the parity scale; the signed sum grows
  like 5.76^n against 7.11^n.
- **Square bounding boxes** (`results/bbox_polyplets_n17_exact.txt`, columns
  H W n count; transpose symmetry 0 violations to 17, width sums equal the
  triangle for n ≤ 17). Share with a square box 0.183, 0.148, 0.126, 0.111
  at n = 8, 11, 14, 17, fitted n^(−0.658) over n ≥ 10 (local slopes
  −0.647..−0.686); with rms(H−W) = 2.073, 2.579, 3.036, 3.458 the product
  share × rms is 0.379, 0.381, 0.382, 0.384, climbing toward 1/√(2π) =
  0.3989: H − W is asymptotically normal at its own scale. This does not
  reopen ν as evidence for universality (`results/growth-constant.md`).

Not run: joint bounding-box structure beyond n ≈ 17, height moments in n,
symmetry-refined triangles, perimeter- or component-refined statistics.

## Open problems

- Closed forms for multi-row cluster weights; W(4,·) needs two more entries.
- The exact growth constant of the all-pairs family (about 14.41).
- The single-cluster generating function B(y): no algebraic or D-finite form
  at 18 terms (`docs/proofs/T-n-nm2-and-general.md` §5).
- Symbolic closure of T(3m+2, 2m+1) ≡ 2 (mod 3).
- Higher-coordination lattices; the polyiamond pair weight as a gadget.
- The slope-2 slice: a law of degree ≥ 8 or onset past H = 8, and θ.
- Series acceleration of B(y) for λ; re-recovery of G_11.

## Reproduce

All scripts run as `python3 <path>` with no arguments unless shown.

    experiments/defect_gas.py, cluster_weight_dp.py [pair A B], spine_deeper.py, holefree_gas.py, hole_strata_gas.py
    experiments/diagonal_law_proof_check.py, grand_form_check.py, Pk_explicit.py; scripts/derive_pk_fast.py, verify_diagonal_pins.py
    git show 78602f8^:scripts/pin_diagonal_k8.py
    experiments/hex_gas.py, hex_diag_deep.py, polyiamond_diagonal.py, polyiamond_fibre_check.py
    experiments/universal_law_check.py, gas_cumulants.py, cross_lattice.py
    experiments/production_matrix_probe.py, band_constants_3adic.py, Pk_denominator_check.py, Pk_newton_3adic.py
    experiments/triangle_relations.py, triangle_relations2.py, triangle_atoms.py
    experiments/gf_head_check.py; gf_h11_validate.py [H] [--perturb DEG]; mu_H_from_atoms.py; ./build/strip_mu 10 11
    git show 91bdcdc^:gf/modp_recover.py > experiments/modp_recover.py && POLY_MAX_WORKERS=10 python3 experiments/modp_recover.py 11 11 194 <outfile>
    experiments/slope_slices.py, slope_onset.py, pfinite_slices.py, slope2_ansatz.py
    experiments/grand_form_saddle.py, slope2_law_vs_truth.py, lambda_from_grand_form.py
    experiments/triangle_combinations.py, alt_sign_runs.py, parity_amplitude.py

## Sources

- `results/defect-gas.md` (deleted 2026-09-06; its content is above)
- `results/diagonal-closed-forms.md` (deleted 2026-09-06; its content is above)
- `results/k8-pinning.md` (deleted 2026-09-06; its content is above)
- `results/hex-diagonal-law.md` (deleted 2026-09-06; its content is above)
- `results/polyiamond-diagonal-law.md` (deleted 2026-09-06; its content is above)
- `results/slope-slicings.md` (deleted 2026-09-06; its content is above)
- `results/slope-growth-saddle.md` (deleted 2026-09-06; its content is above)
- `results/production-matrix-probe.md` (deleted 2026-09-06; its content is above)
- `results/triangle-combinations.md` (deleted 2026-09-06; its content is above)
- `results/triangle-structure.md` (deleted 2026-09-06; its content is above)
- `results/gf-head-check.md` (deleted 2026-09-06; its content is above)
