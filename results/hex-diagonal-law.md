# The diagonal law is universal: polyhexes (2026-07-15)

> **Which cells these are (clarified 2026-08-06).** **Hexagons**, six
> neighbours each. Their centres form the triangular *point* lattice, which is
> why the literature also calls this the triangular lattice — but the cells are
> not triangles. **Polyiamonds — animals of equilateral triangles — are a
> different object**: three neighbours per cell, alternating orientation,
> counts A001420 (2, 3, 6, 14, 36, …) against A001207's (1, 3, 11, 44, 186, …)
> here. They fall outside the row-local class because the adjacency is
> parity-dependent; the law does look to survive there in periodic form, probed
> in `experiments/universal_law_check.py`. See
> `docs/proofs/universal-diagonal-law.md` §The lattice class. The A001207
> validation below is what pins which of the two this note is about.

Question #1 of the fresh menu: does the walk-plus-clusters diagonal law
transfer to other lattices? Answer for the hexagonal lattice: YES, with
the identical structure. Tool: `experiments/hex_gas.py` (brute enumerator
validated against A001207 n<=10; row-transfer DP with the asymmetric hex
touch x' in {x-1, x}; validated cell-for-cell against brute).

## The hex diagonal law (data-exact, holdout-validated)

Drift walks on the brick lattice have TWO choices per row: T(H,H) = 2^(H-1).
And for k = n-H:

  T_hex(n, n-k) = P_k(n) * 2^(n-1-3k),   deg P_k = k,  onset n >= 2k+1

with P_1(n) = 9n - 15 (exact, 11 holdouts, H <= 14) and
P_2(n) = (81n^2 - 307n + 142)/2 (exact, 9 holdouts). Same exponent-3
structure, same onset as the king lattice. The proof template
(docs/proofs/diagonal-law.md) transfers verbatim: single-cell rows are cut
vertices on any row-adjacency lattice, clusters are finite, rows <= surplus
caps the numerator degree, partial fractions in (1-2z).

## The gas structure

Single-row cluster weights: solid s-runs only -- (s+1)^2 (contacts below x
contacts above; s=2 gives the leading density 9 = 3^2). Gap pairs
contribute ZERO: hex up/down neighbors {x-1, x} cannot bridge a gap, the
structural difference from king (25 = 16 + 9 included gap pairs).

## THE DYADIC SPINE: same cubic, new prime

Mod 2 the master equation collapses to the pair-row exactly as mod 3 did
for king (valuation lemma is lattice-independent: k >= l always, and
What = W * b^(2k-l-1) with b = 2): H = 1 + uH^-2, i.e.

  H^3 = H^2 + u   over F_2

-- the SAME spine cubic, now dyadic. The boundary factor differs:
G == 1 + u H^-3 (mod 2) (the king cancellation identity is 3-specific),
so P_k(n) mod 2 = [u^k] (1 + uH^-3) H^n. Verified: zero mismatches on all
in-band cells H <= 14, k <= 2.

## The universality statement (conjectural beyond these two lattices)

For a lattice whose height-slices give b drift choices per row, the height
triangle obeys T = P_k(n) b^(n-1-3k) with the mod-b structure governed by
H^3 = H^2 + u over F_b's prime field -- the curve is lattice-independent
because only the bare pair-row survives the valuation collapse. The
unit-ness question raised here is CLOSED (2026-07-31, superseding the
"always == 1" guess): w = W_pair mod p obeys w == 4 (mod p) for odd
p | b (so king 25 == 1 mod 3 and hex 9 == 1 mod 2 are both "4"), and
w == floor(b/2) (mod 2) for p = 2, degenerate iff 4 | b -- canonical
statement and corrected pair weights in
`docs/proofs/universal-diagonal-law.md` (Instances/CORRECTION section).
Open: polyiamonds (triangular lattice -- row structure alternates, drift
count TBD); higher-coordination lattices.
