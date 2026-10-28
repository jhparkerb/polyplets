# OEIS candidates: three new sequences, not submitted

Scope and order of any submission are decided in `oeis/SUBMISSION.md`, where
these are the third wave. Nothing here has been submitted; a Superseeker pass
for A and B is still owed. The %C text below is a fact source, not
submission copy.

## Candidate A: the height triangle T(n,H)

**Definition.** `T(n,H)` = number of fixed polyplets (king-connected animals,
A006770) with `n` cells and bounding-box height exactly `H`. Triangle read by
rows, `n >= 1`, `1 <= H <= n`.

**Data (rows n=1..8):**
```
1
1, 3
1, 10, 9
1, 27, 55, 27
1, 68, 248, 240, 81
1, 167, 996, 1480, 945, 243
1, 406, 3775, 7898, 7273, 3510, 729
1, 983, 13837, 39119, 47066, 32193, 12555, 2187
```
Flattened: 1, 1,3, 1,10,9, 1,27,55,27, 1,68,248,240,81, …

**Keywords:** nonn, tabl.  **Offset:** 1.
**Cross-refs:**
- Row sums = **A006770** (fixed polyplets). [verified: 1,4,20,110,638,3832,23592,147941]
- Main diagonal `T(n,n) = 3^{n-1}` = **A000244** (king chain). NOT A025192.
- Column `H=1` = all-1s (horizontal bars).
- Sub-diagonals `T(n,n-k)` have closed forms `P_k(n)·3^n`, deg `P_k = k`,
  e.g. `T(n,n-1)=5(5n-9)3^{n-4}`, leading coefficient `25^k/(3^{3k+1}k!)`
  (`results/diagonal-formula.md`). The sub-diagonals are not to be submitted
  separately: they are derivable diagonals of this triangle.

**Regenerate / extend:** `results/triangle.txt` holds `T(n,H)` for all
`n <= 40`; `results/provenance-table.md` says which independent computations
agree with each entry. `build/redelmeier --per-box` recomputes small `n`.

Not in OEIS as of 2026-07-10 (no height-refined triangle of A006770).

## Candidate B: the component triangle C(n,c)

**Definition.** `C(n,c)` = number of fixed polyplets with `n` cells whose
edge-connected (rook) components number exactly `c` (the pieces are
polyominoes joined only at corners). Triangle read by rows, `1 <= c <= n`.

**Data (rows n=1..9):**
```
1
2, 2
6, 8, 6
19, 36, 36, 19
63, 156, 200, 156, 63
216, 660, 1038, 1040, 662, 216
760, 2752, 5142, 6236, 5166, 2776, 760
2725, 11390, 24620, 34962, 35097, 24860, 11562, 2725
9910, 46936, 115050, 186860, 218824, 188612, 116936, 47944, 9910
```

**Keywords:** nonn, tabl.  **Offset:** 1.
**Cross-refs:**
- Row sums = **A006770** (fixed polyplets).
- **Both** edge columns `C(n,1) = C(n,n)` = **A001168** (fixed polyominoes):
  c=1 = single edge-component (a polyomino); c=n = all cells edge-isolated =
  diagonal-contact-only = polyomino on the 45°-rotated sublattice (bijection).
- Near-symmetric under `c <-> n+1-c`; mean component count `≈ (n+1)/2`.
- Related prior art: **A364928** (Achterberg, corner-connected polyominoes)
  records the c=n bijection in the FREE case only.

**Regenerate / extend:** `experiments/component_stratification.py`
(reproduces A006770 through n=10). Run to higher n to extend.

Not in OEIS as of 2026-07-10 (triangle, and interior columns c=2, c=3).

## Candidate C (lower priority): convex polyplets by area

**Definition.** Number of fixed **HV-convex** king-connected animals (every row
and every column a contiguous run; king-connected). Strictly larger than convex
polyominoes (diagonal joins allowed, e.g. `{(0,0),(1,1)}`).

**Data:** `1, 4, 16, 61, 221, 766, 2566, 8390, 26982, 85834, 271174, 853111,
…`; 700 terms in `results/b_hvconvex_area_upload.txt`, with the growth
constant, the non-D-finiteness exclusion boxes and the derivation in
`results/subclasses.md`.

**Keywords:** nonn.  **Offset:** 1.
**Cross-refs:** A006770 (superset), A067675 (convex polyominoes, subset).
**Comment for submission:** no P-recurrence of order <= 24 and degree <= 24
on 700 terms; growth constant 3.128943269730886….
Not in OEIS.

## Not submitting

The five anti-diagonal sequences `T(n,n-k)` (k=1..5) are derivable diagonals
of Candidate A; their closed forms belong in A's comments, not as separate
entries (values and closed forms: `results/diagonal-formula.md`).
