# OEIS candidates — staged, DEFERRED (viva + jasonp's button)

> These are **Wave 3** of the master plan in `oeis/SUBMISSION.md` (2026-07-16),
> which decides overall scope and order. A Superseeker pass for A and B is
> still owed before submission (they were model-checked only).

Date: 2026-07-10. Everything needed to file these the moment the viva clears and
jasonp decides to submit. Do NOT submit before then (docs/viva-*, policy memories
publishing-is-jasonps-call / oeis-submission-viva-gate). Curated to 2 strong +
1 optional — NOT a flood.

Standard prep still required per policy: %C own-words / pink-box, Superseeker
sanity check, jasonp pushes the button.

---

## Candidate A (strong): T(n,H) height triangle

**Definition.** `T(n,H)` = number of fixed polyplets (king-connected animals,
A006770) with `n` cells and bounding-box height **exactly** `H`. Triangle read by
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
  e.g. `T(n,n-1)=5(5n-9)3^{n-4}`; the defect ideal gas (leading coeff
  `25^k/(3^{3k+1}k!)`). See results/diagonal-closed-forms.md. Do NOT submit the
  sub-diagonals separately — they are derivable diagonals of this triangle.

**Regenerate / extend:** `results/ns_a36/perheight/h{H}.out` gives `T(n,H)` for
H<=18, all n<=36 (main a36 engine). Or `build/g2 --per-box`. Independently
cross-checked by the strip second source (results/strip-engine.md) over
H<=14 **and n<=36** — the banked strip run's reach. Cells with H>14, and all
cells at n=37..40, are not strip-covered as banked (an N=40 extension run was
launched 2026-07-30).

Confirmed NOT in OEIS (sonnet-checked 2026-07-10: no height-refined triangle of
A006770 exists).

---

## Candidate B (strong): C(n,c) component triangle

**Definition.** `C(n,c)` = number of fixed polyplets with `n` cells whose
edge-connected (rook) components number **exactly** `c` (the pieces are
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
- Related prior art: **A364928** (Achterberg, corner-connected polyominoes) —
  records the c=n bijection in the FREE case only; this fixed triangle is new.

**Regenerate / extend:** `experiments/component_stratification.py`
(reproduces A006770 through n=10, validating). Run to higher n to extend.

Confirmed NOT in OEIS (triangle + interior columns c=2,c=3; sonnet 2026-07-10).

---

## Candidate C (optional, lower priority): convex polyplets

**PRIMARY SOURCE: `docs/proofs/convex-mirage.md`** (prior, deeper — has 38 terms,
growth μ≈3.129, and the non-D-finite-by-area finding). Use its data, not the 10
terms below.

**Definition.** Number of fixed **HV-convex** king-connected animals (every row
and every column a contiguous run; king-connected). Strictly larger than convex
polyominoes (diagonal joins allowed, e.g. `{(0,0),(1,1)}`).

**Data (38 terms in convex-mirage; first 10):** `1, 4, 16, 61, 221, 766, 2566,
8390, 26982, 85834, 271174, 853111, …`.

**Keywords:** nonn.  **Offset:** 1.
**Cross-refs:** A006770 (superset), A067675 (convex polyominoes, subset).
**Comment for submission:** non-D-finite by area (Convex Mirage); growth ~3.129.
**Regenerate:** convex-mirage's row-transfer-matrix (reaches 38); the brute
`experiments/convex_polyplets.py` here only cross-checks the first ~10.
Confirmed NOT in OEIS.

---

## Explicitly NOT submitting

The five anti-diagonal sequences `T(n,n-k)` (k=1..5) — derivable diagonals of
Candidate A; their closed forms belong in A's comments, not as separate entries.
Submitting them would be the OEIS flood jasonp flagged. (Values + closed forms:
results/diagonal-closed-forms.md.)
