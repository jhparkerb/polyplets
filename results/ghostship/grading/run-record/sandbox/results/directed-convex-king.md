# Directed-convex king animals: two OEIS identifications

Date: 2026-08-15 (autonomous session 03). Byproduct of the kernel-method
proof (`docs/proofs/convex-box-kernel.md`): the phase decomposition isolates
the subfamily with phase parse in {(0,0),(1,0)} — convex king animals whose
top boundary r is non-decreasing row by row — the king analog of
directed-convex polyominoes. Its GF is F00(1) + F10(1), explicit in
Q(x,y,√Δ) by formulas (2) and (4) of the proof doc.

Control sanity: the polyomino version of the subfamily gives central
binomials C(2s−4, s−2) by semiperimeter and C(2n−2,n−1)² in an exact n×n
box — the classical directed-convex counts, confirming the phase-based
definition is the right analog.

## Identification 1: semiperimeter = A014300

a_dir(s) := #directed-convex king animals with w+h = s equals
**A014300(s−1)** ("nodes of odd outdegree in all ordered rooted trees with
n edges"): 1, 2, 7, 24, 86, 314, 1163, 4352, … Verified exactly for
s = 2..18 via A014300's binomial formula Σ_j C(2n−2j−2, n−1)
(`out_s03_dirconv_verify.txt`). Neither OEIS entry mentions king animals /
polyplets — the identification appears new.

Structural payoffs:
- A014300's GF is 2z/(1−4z+(1+2z)√(1−4z)) — the (1+2z) is exactly the
  diagonal shadow of the kernel weight (1+x+y) from the king boundary term,
  and the radicand is the same √(1−4z).
- A014300 satisfies 2a(n) + a(n−1) = (3n−1)·Catalan(n−1) — the SAME
  2a(s)+a(s−1) twist that session 02 found for the FULL convex king family
  (b(s) = 2a(s)+a(s−1) = (18s+49)4^(s−5) − …). The twist is the diagonal
  trace of the kernel factor K = x+y+xy (K(t,t)/t = 2+t); seeing it verbatim
  in a 1998-vintage OEIS entry for the directed subfamily independently
  confirms the kernel structure.
- A014300 = convolution of central binomials with Fine numbers; and counts
  "unimodal functions f:[n]→[n] with f(i)≠f(i+1)" (Heinz) — the latter is
  visibly king-flavored (a bijection to our top boundaries would explain
  the identification; open).

## Identification 2: exact n×n box = A112029

d(n,n) := #directed-convex king animals with bounding box exactly n×n
equals **A112029(n−1) = Σ_{k=0}^{n−1} C(n−1+k, k)²**: 1, 5, 46, 517, 6376,
82994, … Verified exactly for n = 1..17 (`out_s03_dirconv_verify.txt`).
Again no animal interpretation in OEIS. (Polyomino control: the single term
k = n−1, i.e. C(2n−2,n−1)² — the king version adds the full square-sum
tail.) Suggests a pair-of-king-paths-with-dominance bijection; open, and
likely the same mechanism as s02's N_h(1) = A153337 (king paths) hit.

## Receipts

`experiments/s03_directed_convex.py` → `out_s03_directed_convex.txt`
(tables, both modes); `experiments/s03_dirconv_verify.py` →
`out_s03_dirconv_verify.txt` (exact identity checks to 17×17).
OEIS queries logged in `reports/session-03.md`.
