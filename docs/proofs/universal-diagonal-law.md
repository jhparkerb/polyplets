# The universal diagonal law (all row-local lattices)

2026-07-15. Generalizes `docs/proofs/diagonal-law.md` (king lattice) to a
class of lattices; the two instances proved there and in
`results/hex-diagonal-law.md` become cases of one theorem, and the square
lattice joins as the degenerate b = 1 case. Machine checks:
`experiments/universal_law_check.py` (square, this doc),
`experiments/diagonal_law_proof_check.py` (king),
`experiments/hex_gas.py` (hex).

## The lattice class

A **row-local lattice** has cells indexed by Z^2 and a translation-invariant
symmetric adjacency A contained in {(dx, dy) : |dy| <= 1}, with:

- (R) within-row adjacency contains |dx| = 1 (rows of consecutive cells are
  connected) and is finite;
- (U) the up-offset set D = {dx : (dx, 1) in A} is finite and nonempty;
  write **b = |D|** (the drift count).

Instances: square lattice D = {0}, b = 1; hexagonal (brick) D = {-1, 0},
b = 2; king D = {-1, 0, 1}, b = 3. Animals = finite connected nonempty
cell sets up to translation; T(n, H) = those with n cells and exactly H
nonempty rows spanning a height-H window.

## Theorem A (universal diagonal law)

For every row-local lattice and every k >= 0 there is a polynomial q_k of
degree <= k with

    T(H+k, H) = q_k(H) * b^H    for ALL H >= k+1,

equivalently T(n, n-k) = P_k(n) * b^(n-1-3k) for n >= 2k+1 with
P_k(n) = b^(1+2k) q_k(n-k), and P_k(n) is an integer for all integers
n.

*Proof* -- the five steps of the king proof, none of which used b = 3:

1. **Separation.** Adjacency changes the row index by at most 1, so any
   path from below row r to above it contains a cell of row r; a
   single-cell row is a cut. Animals decompose uniquely at their
   single-cell rows into a drift walk decorated by clusters (maximal runs
   of multi-cell rows).
2. **Finiteness.** A connected piece of c cells has x-spread at most
   (c-1) * max|dx| (finite by (R), (U)), so each cluster type has a finite
   weight (configurations relative to its contact cells), and the cluster
   types of surplus k are the compositions of k: finitely many.
3. **Chain identity.** With y marking surplus and z marking rows,
   F(y,z) = E_b (1 - S)^{-1} E_t + P exactly, where
   S = b z + sum_c W_c y^{k_c} z^{l_c + 1} (a drift step has b choices by
   (U)) and E_b, E_t, P are the finite boundary/pure sums. Uniqueness of
   the decomposition and x-translation-invariance give exactness.
4. **Degree bound.** Every cluster row carries at least one surplus cell,
   so l_c <= k_c; hence [y^k] F = R_k(z)/(1 - bz)^{k+1} with R_k an
   integer polynomial of degree <= 2k+1.
5. **Partial fractions + integrality.** Expanding R_k in the (1 - bz)
   basis (coefficients in b^{-(2k+1)} Z) gives T(H+k, H) = q_k(H) b^H for
   H > deg of the correction polynomial <= k, i.e. for H >= k+1, with
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

## Instances (machine-checked)

| lattice | b | onset | density (pair wt) | P_1(n) | spine |
|---|---|---|---|---|---|
| square | 1 | n>=2k+1 | 4 = 2^2 | 4(n-2) | vacuous (no prime) |
| hex | 2 | n>=2k+1 | 9 = 3^2 | 9n-15 | H^3=H^2+u over F_2 (w=1) |
| king | 3 | n>=2k+1 | 25 = 5^2 | 25n-45 | H^3=H^2+u over F_3 (w=1) |

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

## Periodic extension: polyiamonds (data-grade, 2026-07-15)

The triangular lattice is row-local only with period-2 x-translation
(orientation parity), outside the theorem's literal class. The law
extends: fixed polyiamonds (A001420 control, n <= 12) have minimal
height-H animals with 2H-2 cells (up-down domino ground states) and

  T(2H-2, H) = 2^(H-2),   T(2H-1, H) = H 2^(H-1),
  T(2H-2+k, H) = q_k(H) 2^H with q_k rational of degree k, for
  H >= k+1 by analogy (onset below that unexamined; k = 2: constant
  second differences, verified).

So periodic row-local lattices obey the same law with b = per-period
drift and rational q_k; proving the periodic version = rerunning the five
steps with a transfer over one period (a matrix drift step). Left as the
stated extension, not formalized.

## Scope notes

- Theorem A needs no symmetry of D and no b-specific arithmetic; it also
  holds per extra additive marker (holes etc.) by the same proof with
  marked weights.
- Onset SHARPNESS (failure at n = 2k) remains per-lattice empirical, as in
  the king case.
- Together with the anisotropic non-D-finiteness theorem (same repo),
  which is also lattice-universal, the two structural results about
  by-height triangles hold across the class.
