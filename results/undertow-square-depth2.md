# Square Undertow at depth 2: the identity holds, and D_2 has no law in five levels

2026-08-22, executing `docs/time-at-the-bar.md` A1.4. Probe
`experiments/undertow_square_depth2.py`, three RED controls green, run on ayr.
Exact rational arithmetic on the banked square bounding-box triangle; instant.

## The answer in one line

**The below-onset identity holds at depth 2 on the square lattice for k = 2..6:
the depth-2 fit drops the two tallest in-onset cells and reproduces both of
them exactly.** So the external check `results/undertow-square-validation.md`
opened now covers two heights of saving rather than one. What it does *not*
supply is a formula for `D_2` — five measured levels give `−4, 8, −3, 10, −1`
and no law is visible in them.

## What was done

On the square lattice `b = |D| = 1`, so the diagonal law is a plain polynomial
`T_sq(n, n−k) = P_k(n)` for `n ≥ 2k+1`. Depth `j` is the cell at `n = 2k+1−j`:

    depth 1   n = 2k     D_1(k) = T_sq(2k,   k)   − P_k(2k)     = (−1)^(k+1)
    depth 2   n = 2k−1   D_2(k) = T_sq(2k−1, k−1) − P_k(2k−1)   measured here

`P_k` is pinned from in-onset cells alone, which needs `n` up to `3k+1`, and
`results/bbox_square4_n21.txt` stops at n = 21. So k ≤ 6 — five levels for
`D_2`, the same number `D_1` was measured from, and the same wall.

## The measurement

| k | `T_sq(2k−1, k−1)` | `P_k(2k−1)` | `D_2(k)` |
|---|---|---|---|
| 2 | 1 | 5 | **−4** |
| 3 | 18 | 10 | **8** |
| 4 | 269 | 272 | **−3** |
| 5 | 3,468 | 3,458 | **10** |
| 6 | 42,099 | 42,100 | **−1** |

All integers. The sign is `(−1)^(k+1)` at every level — the same alternation
`D_1` has. The magnitudes are `4, 8, 3, 10, 1`, which are not monotone, do not
separate cleanly by parity (even k gives 4, 3, 1 and odd k gives 8, 10), and
support no fit worth writing down on three and two points. **Recorded as five
measurements, not as a law.**

## The identity itself does hold

The depth-2 fit uses the two below-onset cells `n = 2k−1` and `n = 2k`, plus the
in-onset cells `n = 2k+1 … 3k−1`. That is exactly `k+1` points for a degree-k
polynomial, and the two tallest in-onset cells are never seen.

| k | agrees with the classical fit | predicts `T(3k, 2k)` | predicts `T(3k+1, 2k+1)` |
|---|---|---|---|
| 2 | yes | 68 ✓ | 121 ✓ |
| 3 | yes | 1,226 ✓ | 2,110 ✓ |
| 4 | yes | 23,182 ✓ | 39,183 ✓ |
| 5 | yes | 450,432 ✓ | 752,927 ✓ |
| 6 | yes | 8,908,454 ✓ | 14,780,288 ✓ |

Ten held-out cells, ten exact hits, in exact rational arithmetic.

Controls: the depth-1 result of the file this extends still reproduces at
k = 1..6; and **a `D_2` corrupted by 1 breaks the fit at every k**, so the
holdout is not passing for a reason unrelated to the defect. Without that
second control the whole table would be consistent with `D_2` being irrelevant.

## The honest limit, and it is the important part

`D_2` here is *measured against* `P_k`, and `P_k` was pinned classically. That
is fine as a validation of the identity — it establishes that a cell two rows
below the onset, corrected, is a valid equation for the same polynomial — but it
is **not** an independent route to `D_2`, so it does not by itself let anyone
compute a square `P_k` more cheaply.

On the king lattice the corresponding `D_j` come from the family DP
(`cpp/severance_w3_families.cpp`), which computes them without knowing `P_k`.
A1.4 asked for the square `D_2` "through the now lattice-parametric ledger"
(`results/skeletonkey-parametric-master.md`) — that derivation is what would
close the gap, and it is untouched. This file supplies the target it has to hit:
`−4, 8, −3, 10, −1` at k = 2..6. A ledger derivation that reproduces those five
integers would be checkable immediately, which is worth more than a derivation
with nothing to land on.

The irregularity makes that derivation more interesting rather than less. Depth
1 is `(−1)^(k+1)` and could plausibly have been guessed; depth 2 could not.

## What more levels would cost

`k = 7` needs `P_7` pinned, hence `n` up to 22, and `k = 8` up to 25. The banked
square bounding-box triangle stops at n = 21, so every extra level needs a
larger square-lattice bounding-box enumeration — `A001168(25)` is
5,940,738,676, so this is an engine run and not an afternoon. Two more levels
would take the parity classes to four and three points, which is still thin.

## Reproduce

    python3 experiments/undertow_square_depth2.py

Instant, ayr or dalby. Input: `results/bbox_square4_n21.txt`, and
`experiments/undertow_square.py` for the loaders and the depth-1 comparison.
