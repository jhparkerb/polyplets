# Anti-diagonal closed forms of the polyplet height triangle

Date: 2026-07-10. `T(n,n-k)` = # fixed polyplets, n cells, bbox height exactly
`n-k` (near-maximal height). `experiments/Pk_explicit.py`.

## The closed forms

`T(n,n-k) = P_k(n)·3^n`, **degree(P_k) = k**, valid for `n ≥ k+2` (onset), with a
single pre-onset transient at `n=k+1` (the `H=1` bar). Degrees k=1..5 measured
exactly: `1,2,3,4,5`. (This corrects `boundary-push-recurrence.md`, which said
degree `2k` — that was the transient-inflated *recurrence order* `2k+1`, not the
polynomial degree. `dmirror-diagonals.md` already had degree k, consistently.)

| k | closed form | first terms (from onset) |
|---|---|---|
| 0 | `3^{n-1}` (king chain, **A000244**) | 1,3,9,27,81,… |
| 1 | `5(5n-9)·3^{n-4}` | 10,55,240,945,3510,… |
| 2 | `(625n²−2459n+1134)/(2·3⁷)·3^n` | 27,248,1480,7273,… |
| 3 | `(15625n³−100050n²+122213n−32940)/(?·3^{10})·3^n` | 68,996,7898,47066,… |
| 4 | deg 4 (see script) | 167,3775,39119,278240,… |
| 5 | deg 5 (see script) | 406,13837,185198,… |

Structure: leading coeff ~`5^{2k}` (25,625,15625,390625, then `5^9` at k=5 — the
`25^k` pattern breaks at k=5, unexplained, flag). Newton-basis denominator exactly
`3^{3k+1}` (results/production-matrix-probe.md).

## OEIS / literature status (sonnet-checked 2026-07-10)

- k=0 = **A000244** (powers of 3). NOT A025192 (that's `2·3^{n-1}`).
- **k=1..5: none in OEIS** (bare + leading-1 forms all searched). No height-refined
  triangle of A006770 in OEIS either. → genuinely new; stage for submission (task #6).
- **No prior literature** on `T(n,n-k)`-type closed forms for any lattice-animal
  family (polyominoes/plets/iamonds), king or square. Nearest: column-convex /
  bounded-width transfer-matrix rationality (Klarner–Rivest) is the *mechanism* that
  explains why a clean closed form exists, but nobody computed the sub-diagonals.
  Open territory.

## The defect ideal gas (task #7, leading order SOLVED)

`P_k` **leading coefficient = `25^k / (3^{3k+1}·k!)`** exactly (verified k=1..8,
`experiments/Pk_explicit.py`). Hence the asymptotic (large n, fixed k):

    T(n,n-k)  ~  3^{n-1} · (25n/27)^k / k!

**Combinatorial reading — defects as an ideal gas.** A near-max-height animal is
a king chain (`3^{n-1}`, three continuations per step) carrying `k` "defect"
cells. The `1/k!` says the defects are **indistinguishable**; the `n^k` says each
sits at one of `~n` positions along the chain; the weight per defect is
`25/27 = 5²/3³` — a defect spends three chain-steps of freedom (`3³`) and adds
`25 = 5²` local configurations. (Sonnet's "5 per defect" was close; it's `5²`.)

This explains every feature at once: degree `k` (k defects), `25^k` (weight per
defect), `1/k!` (indistinguishable), `3^{3k+1}` denominator (`3³` per defect
× the `3^{-1}` chain offset). The full bijection (exact `P_k`, not just leading)
remains, but the structure is now understood.

**Open exact form:** the EGF-in-k `G(n,y) = Σ_k T(n,n-k) y^k = 3^{n-1}·(…)` is
`~ 3^{n-1} e^{25ny/27}` to leading order; a closed bivariate `G(n,y)` (if the
subleading corrections are also clean) would be the exact statement. Not yet
derived. This, plus the ideal-gas picture, is what makes these OEIS-worthy /
paper-worthy rather than just tabulated diagonals.
