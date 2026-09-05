# The universal diagonal law (row-local lattices, and rows with a fibre)

2026-07-15. Generalizes `docs/proofs/diagonal-law.md` (king lattice) to a
class of lattices; the two instances proved there and in
`results/hex-diagonal-law.md` become cases of one theorem, and the square
lattice joins as the degenerate b = 1 case. Machine checks:
`experiments/universal_law_check.py` (square, this doc),
`experiments/diagonal_law_proof_check.py` (king),
`experiments/hex_gas.py` (hex),
`experiments/polyiamond_fibre_check.py` (polyiamonds, the fibred case).

## The lattice class

A **row-local lattice** has cells indexed by Z^2 and a translation-invariant
symmetric adjacency A contained in {(dx, dy) : |dy| <= 1}, with:

- (R) within-row adjacency contains |dx| = 1 (rows of consecutive cells are
  connected) and is finite;
- (U) the up-offset set D = {dx : (dx, 1) in A} is finite and nonempty;
  write **b = |D|** (the drift count).

Instances: square lattice D = {0}, b = 1; **polyhexes** D = {-1, 0}, b = 2;
king D = {-1, 0, 1}, b = 3. Animals = finite connected nonempty
cell sets up to translation; T(n, H) = those with n cells and exactly H
nonempty rows spanning a height-H window.

**What the b = 2 instance is, settled 2026-08-06 by measurement**
(`experiments/diagonal_machine.py` `identify()`, brute force to n = 8, run on
every invocation so the labels cannot drift). D = {−1, 0} is **six**-regular,
totals 1, 3, 11, 44, 186, 814, 3652, 16689 = **A001207: fixed hexagonal
polyominoes**. Cells are hexagons; each has six neighbours; their centres form
the triangular *point* lattice, which is why the literature also calls this the
triangular lattice (Madras's §3.1(b) "Tri"). This repo's "hex" label is the
cell-side name and is correct.

### Rows with a fibre

Some lattices have no single-cell interior rows at all, and the theorem covers
them once the row unit is enlarged. Take cells indexed by Z^2 × B with B finite
(the **fibre**), adjacency translation-invariant in Z^2, locally finite,
changing the row index by at most 1, and each row connected. Call a row of an
animal *interior* if it is neither its top nor its bottom row. The proof uses

- (M) for some m >= 1, every interior row has at least m cells; every interior
  row of exactly m cells is connected and holds exactly one cell that can take
  an edge from below (its **entry**) and exactly one that can pass an edge up
  (its **exit**); and from a fixed entry cell the number of ways to continue —
  pairs (minimal row with that entry, edge upward out of its exit) — is **b**,
  independent of where the entry cell sits.

A row-local lattice satisfies (M) with m = 1 and b = |D|: a single-cell row is
its own entry and exit, and its b continuations are the b up-offsets. Write
n_min(H) for the least cell count at height H; it is H in the row-local case.

**Polyiamonds are in the class, with a fibre of two.** Cells are equilateral
triangles, each with **three** edge-neighbours, and the up/down orientation
alternates: with cell (x, y) an up- or down-triangle by the parity of x + y,
adjacency is (x ± 1, y) always and (x, y + 1) only when x + y is odd. Condition
(U) fails outright — there is no single drift set D. Condition (M) holds with
m = 2. Only a cell of even x + y can take an edge from below and only a cell of
odd x + y can pass one up, so an interior row needs one of each: two cells at
least, and a two-cell interior row must be horizontally adjacent, since
otherwise each of its two cells has degree one and the animal falls apart. That
adjacent pair is a **rhombus** — one entry, one exit — and from a fixed entry
there are exactly two of them, the odd cell to its left or to its right; each
exit has a single edge upward, so b = 2. Hence
n_min(H) = 1 + 2(H − 2) + 1 = 2H − 2, and in the coordinate j = ⌊(x − y)/2⌋
the exit offsets are D = {0, −1}: the rhombus walk is the polyhex walk.
`experiments/polyiamond_fibre_check.py` checks every clause against brute
force to n = 14, the change of variables included: the map
(x, y) ↦ (j, y, entry/exit) is an isomorphism onto the honeycomb graph carrying
its translation group, height for height, so polyiamonds are the site animals
of the honeycomb lattice — a Z^2 lattice with a two-point fibre. Their counts
are A001420 (2, 3, 6, 14, 36, 94, 250, 675, 1838 …), nothing like A001207,
and two names collide here: *triangular lattice*
as a point lattice means six neighbours and gives polyhexes; *tiling by
triangles* means three neighbours and gives polyiamonds. OEIS itself files
polyiamonds under "the 2-dimensional hexagonal lattice".

## Theorem A (universal diagonal law)

For every lattice satisfying (M) and every k >= 0 there is a polynomial q_k
of degree <= k with

    T(n_min(H)+k, H) = q_k(H) * b^H    for ALL H >= k+1.

For a row-local lattice n_min(H) = H, so this reads T(H+k, H) = q_k(H) b^H,
equivalently T(n, n-k) = P_k(n) * b^(n-1-3k) for n >= 2k+1 with
P_k(n) = b^(1+2k) q_k(n-k), and P_k(n) is an integer for all integers
n. (The n-indexed form is row-local only: at m = 2 the height is not
recoverable from n and k alone.)

*Proof* -- the five steps of the king proof, none of which used b = 3 or
m = 1:

1. **Separation.** Adjacency changes the row index by at most 1, so any
   path from below row r to above it contains a cell of row r; a minimal
   interior row is a cut, with a single entry and a single exit by (M).
   Animals decompose uniquely at their minimal rows into a drift walk
   decorated by clusters (maximal runs of non-minimal interior rows).
2. **Finiteness.** A connected piece of c cells has x-spread at most
   (c-1) * max|dx| (finite by (R), (U)), so each cluster type has a finite
   weight (configurations relative to its contact cells), and the cluster
   types of surplus k are the compositions of k: finitely many.
3. **Chain identity.** With y marking surplus over n_min and z marking
   rows, F(y,z) = E_b (1 - S)^{-1} E_t + P exactly, where
   S = b z + sum_c W_c y^{k_c} z^{l_c + 1} (a drift step has b choices by
   (M)) and E_b, E_t, P are the finite boundary/pure sums. Uniqueness of
   the decomposition and x-translation-invariance give exactness.
4. **Degree bound.** Every cluster row is an interior row of more than m
   cells, so carries at least one surplus cell, so l_c <= k_c; hence
   [y^k] F = R_k(z)/(1 - bz)^{k+1} with R_k an integer polynomial of
   degree <= 2k+1.
5. **Partial fractions + integrality.** Expanding R_k in the (1 - bz)
   basis (coefficients in b^{-(2k+1)} Z) gives T(n_min(H)+k, H) = q_k(H) b^H
   for H > deg of the correction polynomial <= k, i.e. for H >= k+1, with
   deg q_k <= k; and P_k = b^{1+2k} q_k has integer values since the basis
   coefficients have p-adic valuation >= -(2k+1) v_p(b) for every prime
   p | b and no other denominators. QED

## Theorem B (universal spine)

Let p be a prime dividing b, and let w = W_pair mod p, where W_pair is the
total weight of the one-surplus single-row cluster (the pair-row). Then,
mod p, the grand series H(u) of the law satisfies

    H = 1 + w u H^{-2},  i.e.  H^3 = H^2 + w u  over F_p .

If w != 0 this is the spine cubic W^3 = W^2 + t after the rescaling
t = w u: **the curve is lattice-independent**; the lattice chooses only
the prime (through b) and the scaling (through W_pair). If w = 0 the
mod-p triangle is trivial in the band (the hole-free/king mod-3 situation
shows this branch is realized by natural subfamilies).

*Proof.* The master equation H = 1 + sum_c What_c u^{k_c} H^{-(k_c+l_c)}
with What_c = W_c b^{2k_c - l_c - 1} follows from the chain identity by
the same substitution as in the king case (mu = bH, u = y mu / b^3).
Valuation: v_p(What_c) = (2k_c - l_c - 1) v_p(b) + v_p(W_c) >=
(k_c - 1) v_p(b) >= 1 for every cluster except k = l = 1, using k >= l.
Only the pair-row survives mod p, with weight What = W_pair. QED

## Corollary: OEIS A308359's open conjecture (2026-08-06)

**A308359** (R. J. Mathar, May 2019) is the triangle of *fixed polyominoes with
n cells by bounding-box width*, height free — our own T(n, H) transposed. It
records `T(n,n-1) = 4n-8` for n ≥ 3 as known, and

> **Conjecture: T(n,n−2) = 8n² − 51n + 86 for n ≥ 5.**

That is Theorem A at b = 1, k = 2. The theorem gives deg ≤ 2 and onset
n ≥ 2k+1 = 5 — exactly the range the conjecture states — so **three enumerated
values determine the polynomial and the conjecture follows**.
`experiments/oeis_a308359_check.py` does it from our own enumeration rather
than from their numbers: totals against A001168 first, then k=1 reproducing
their proved 4n−8 (which is what certifies our triangle is theirs), then the
quadratic through n = 5,6,7 — which comes out `8n² − 51n + 86` verbatim and
reproduces every value to n = 11. Two RED controls: a linear fit through
n = 5,6 must miss at n = 7 (it gives 105 against 121), and the formula must
**fail** at n = 2k = 4, since the onset is sharp (T(4,2) = 9, quadratic says
10) — otherwise neither the degree nor the onset would be under test.

Two things worth noting. The k=1 agreement is an independent third party's
check on our machinery. And the onset in their conjecture, "n ≥ 5", was
presumably read off data; ours is 2k+1 for every k, proved, which is where the
next diagonals would come from.

## The diagonal machine (2026-08-06)

`experiments/diagonal_machine.py`. Theorem A's degree bound and onset turn
k+1 enumerated values into a proved closed form, for **any** row-local lattice.
The script supplies the values with a surplus-budgeted row transfer DP that is
parametric in the drift set D — state is (this row's cells normalized, which
component of the animal-so-far each belongs to, surplus spent), components that
lose their foothold in the current row are pruned as unreconnectable — so its
cost depends on k and H rather than on the number of animals. Rows may have
gaps, so positions are searched in a window and every run reports a stability
check at window and window+2.

It reproduces every independently known form and then keeps going:

| lattice | b | k | P_k(n) | status |
|---|---|---|---|---|
| square | 1 | 1 | 4n − 8 | matches A308359 (proved there) |
| square | 1 | 2 | 8n² − 51n + 86 | matches A308359's **conjecture** |
| square | 1 | 3 | 32/3 n³ − 140n² + 1960/3 n − 1090 | new |
| square | 1 | 4 | 32/3 n⁴ − 712/3 n³ + 12635/6 n² − 52813/6 n + 14496 | new |
| hex | 2 | 1 | 9n − 15 | matches `results/hex-diagonal-law.md` |
| hex | 2 | 2 | 81/2 n² − 307/2 n + 71 | new |
| hex | 2 | 3 | 243/2 n³ − 774n² + 1897/2 n + 28 | new |
| king | 3 | 1 | 25n − 45 | matches `docs/proofs/diagonal-law.md` |
| king | 3 | 2 | 625/2 n² − 2459/2 n + 567 | matches `T-n-nm2-and-general.md` |

The king k=2 row is the strongest check: `½(625n² − 2459n + 1134)` was derived
by hand in a separate proof, and the parametric DP returns it. The square k=3
row can be checked against A308359's own printed triangle without running
anything — it gives 282 at n=7 and 638 at n=8, which are that entry's values.
Every row also survives 5–11 holdout values past the ones used to fit it.

Coefficients are rational, not integral, which is the expected shape:
`k!·P_k ∈ ℤ[n]` with P_k integer-*valued* (32/3 × 3! = 64).

## The gas, made lattice-parametric (2026-08-06)

`experiments/gas_cumulants.py`. The machine above says *what* P_k is; the gas
says *why*, and its content turns out to be one line about cumulants. Write

    F(n, u) = Σ_k P_k(n) u^k,  P_0 = 1,   and   c_k = [u^k] log F.

**Every c_k is linear in n**, on every lattice tested, at every k reached:

| lattice | c_1 | c_2 | c_3 | c_4 |
|---|---|---|---|---|
| square | 4n − 8 | −19n + 54 | 472/3 n − 1718/3 | −3099/2 n + 6558 |
| hex | 9n − 15 | −37/2 n − 83/2 | 32n − 32 | |
| king | 25n − 45 | −209/2 n − 891/2 | | |

That is extensivity — an independent 1-D gas of defects whose interactions live
entirely in the constants — and **the shape of the law follows from it**:
deg P_k ≤ k because the top term of P_k is c_1^k/k!, and the leading
coefficient is therefore `W^k/k!` with W the slope of c_1. Checked: square
4^k/k!, hex 9^k/k!, king 25^k/k!, against the machine's polynomials.

The king row is the calibration — `c_2 = −209/2 n − 891/2` is exactly the
`(a2, b2) = (−891/2, −209/2)` hardcoded in `experiments/defect_gas.py`'s
reconstruction, arrived at here from a drift-parametric DP instead.

W is also the **pair-cluster weight**, counted independently as a gadget by
`experiments/universal_pair_weights.py` — two routes with no shared code path,
agreeing at 4, 9, 25. And `cluster_weight(D, sizes)` is now parametric, with
king reproducing every weight in `defect_gas.py`'s table:

| cluster | square | hex | king (must match `defect_gas.py`) |
|---|---|---|---|
| (2,) | 4 | 9 | 25 |
| (3,) | 9 | 16 | 49 |
| (4,) | 16 | 25 | 81 |
| (2,2) | 12 | 60 | 339 |
| (2,3) | 30 | 138 | 930 |
| (2,2,2) | 36 | 409 | 4778 |

Run at window 6 rather than 9, the port reproduces the *documented bug* —
(2,2,2) clips to 4776 — which is a check on the port and a trap to keep away
from.

**What is still king-only:** assembling c_k for k ≥ 2 *from* the cluster
weights, i.e. `defect_gas.py`'s ledger and the master equation. The parametric
statement above is what makes that step worth taking: we know the target is
linear in n on every lattice, so what is missing is the combination of weights
that produces its two coefficients.

## Instances (machine-checked)

| lattice | b | onset | density (pair wt) | P_1(n) | spine |
|---|---|---|---|---|---|
| square | 1 | n>=2k+1 | 4 = 2^2 | 4(n-2) | vacuous (no prime) |
| hex | 2 | n>=2k+1 | 9 = 3^2 | 9n-15 | H^3=H^2+u over F_2 (w=1) |
| king | 3 | n>=2k+1 | 25 = 5^2 | 25n-45 | H^3=H^2+u over F_3 (w=1) |
| polyiamond (m=2) | 2 | H>=k+1 | 2 (in H, not measured as a gadget) | q_1 = H/2 | not examined |

The polyiamond row is indexed by height, not by n, and its measured onsets are
⌊k/2⌋+2, earlier than the k+1 guaranteed; diagonals to k = 4 in
`results/polyiamond-diagonal-law.md`.

CORRECTION 2026-07-31 (hygiene sweep; `experiments/universal_pair_weights.py`,
two independent methods: direct gadget count with no gap cap, and
end-to-end k = 1 diagonal enumeration with holdouts — [n]P_1 = W_pair
confirmed on all six test lattices). The 2026-07-15 synthetic computation
capped the pair's column gap at 2 — correct for max|dx| <= 1, silently
lossy beyond — and its numerals for the wider lattices were undercounts:
interval b = 4, 5 have **W_pair = 58, 114** (not 45, 69; the old numbers
are exactly the gap <= 2 subtotals), and D = {-2, 0, 2} has **W_pair = 57**
(not 48). Every qualitative conclusion survives, and the corrected
sequence has a closed form for interval D:

    W_pair(b) = b^3 - b(b+1)/2 + 4     (verified b = 1..8 gadget-side,
                                        b <= 5 end-to-end),

> **SCOPE NOTE 2026-07-31 (cold-eyed pass), on everything from the closed
> form to the end of this paragraph.** The *correction* above is load-bearing
> and stays in full: 45/69/48 were wrong, one of them reached the paper, and
> killing the "densities are squares" reading was necessary. What is demoted
> to supporting detail is the **generalization**: the cubic in b, and the
> "degenerate iff 4 | b" classification, describe a family of hypothetical
> interval lattices at b >= 4 that nobody enumerates. Exactly three members
> of the class are objects anyone studies — square (b=1), hex (b=2), king
> (b=3) — and all three are machine-checked here.
>
> Theorem B's sharpness needs only two witnesses, and we have both
> independently of the cubic: `D = {-2,0,2}` realizes w = 0 (degenerate
> branch nonempty), and interval b = 5 gives w = 4 != 1 (scaling genuinely
> nontrivial). Those two examples carry the theorem. Keep the closed form as
> the convenient way to *generate* such witnesses; do not present it, or the
> 4 | b classification, as a result in its own right, and do not extend the
> b-family further.

so densities are NOT squares beyond b = 3 — "squares" was a b <= 3
artifact. The solid-pair term (b+1)^2 == 1 mod p | b stands. Mod-p
corollary of the closed form: for **odd p | b** both b^3 and b(b+1)/2
vanish, so **w == 4 (mod p) — always a unit**, and the universal spine for
odd p is H^3 = H^2 + 4u with the 4 lattice-independent too (king's w = 1
is 4 mod 3; b = 5's w is 4 mod 5 — a unit but not 1, so "w = 1 always"
stays false with genuine scaling). For **p = 2**, w == floor(b/2) (mod 2):
the DEGENERATE branch is realized exactly when 4 | b — by an ordinary
interval lattice (b = 4: W = 58 == 0 mod 2), no contrived offset set
needed; D = {-2, 0, 2} also lands there (57 == 0 mod 3, replacing the old
48). Theorem B's statement (curve up to scaling when w != 0; trivial band
when w == 0) is exactly sharp, with the branch condition now closed-form:
degenerate iff p = 2 and 4 | b (for interval D).

**Degree sharpening (2026-07-31).** deg q_k = k exactly, with leading
coefficient [n^k]P_k = W_pair^k / k!: proved for king (grand-form
Corollary 2, Lean `lead_coeff_25`; the argument is uniform in the weights
with 25 -> W_pair, not written out for general b), and measured: k = 1 at
all six test lattices above (slope = W_pair), hex k <= 2 (banked lead
81/2 = 9^2/2!, `results/hex-diagonal-law.md`), square deg-k diagonals
(`experiments/universal_law_check.py`). Since W_pair >= 4 > 0, the
"degree <= k" of Theorem A is never slack at the top.

## Scope notes

- Theorem A needs no symmetry of D and no b-specific arithmetic; it also
  holds per extra additive marker (holes etc.) by the same proof with
  marked weights.
- Onset SHARPNESS (failure at n = 2k) remains per-lattice empirical, as in
  the king case.
- Together with the anisotropic non-D-finiteness theorem (same repo),
  which is also lattice-universal, the two structural results about
  by-height triangles hold across the class.

## Prior art (2026-08-06, `results/novelty-sortie.md` N5)

No height-diagonal law for lattice-animal triangles was found in print, and
`results/diagonal-closed-forms.md` had already recorded no published T(n,n−k)
closed forms. The nearest published relative measures the defect in
**dimension** rather than in height, on polycubes:

- Barequet, Barequet & Rote, *Formulae and growth rates of high-dimensional
  polycubes*, Combinatorica 30 (2010) 257–275 — for fixed n, the count is a
  polynomial in the dimension d.
- Barequet & Shalah, *Counting n-cell polycubes proper in n−k dimensions*,
  European J. Combin. 63 (2017) 146–163 — for general k the formula has the
  proved shape `2^(n−2k+1) n^(n−2k−1) (n−k) h_k(n)` with `h_k` polynomial.

Same statement shape — fix the defect, get polynomial × exponential, degree
governed by the defect — for one lattice family and one defect parameter.
Theorem A quantifies over every row-local lattice instead, and is proved once
for all of them. Cite that line as the precedent for the shape; do not present
the phenomenon as unheard-of. Neither paper is held locally
(`papers/MISSING.md`).
