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
