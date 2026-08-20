# Undertow — the diagonal tower pins from below, not from above

2026-08-20, branch `lastditch`. Script `experiments/undertow_pin.py`; every
number here is printed by it.

## The claim

`docs/b1-closure-plan.md` §1 costs level `k` of the diagonal tower two
**above-onset** anchors, `T(2k+1, k+1)` and `T(2k+2, k+2)` — the two *tallest*
cells on its diagonal. That is the rule that made row 40 expensive: P₁₉'s
anchors are `T(39,20)` and `T(40,21)`, and `T(40,21)` is the 36.4-hour H = 21
sweep of `results/ns_a40/PROVENANCE.md` phase C.

The anchors do not have to be the tall ones. The grand form
(`docs/proofs/grand-form.md`, Lean-complete) makes level `k` carry exactly two
new constants,

    P_k(n) = [y^k] exp( sum_j (a_j + b_j n) y^j ),

so any two independent linear equations in `(a_k, b_k)` pin it. Severance W3
(`results/onset-defect-depths234.md`) supplies them from short cells: at depth
`j` below onset,

    T(2k+1-j, k+1-j) = P_k(2k+1-j) · 3^(2k-3k-j) + D_j(k)                  (*)

and `D_j(k)` is computed **ab initio** from bounded-excess cluster-weight
families — it reads neither the triangle nor the wired `P_k`, which is what the
W3 gate exists to keep true. `P_k(n)` is linear in `(a_k, b_k)` with
coefficient 1, so (*) is one linear equation, and its cell sits at height
`k+1-j`: **j rows shorter than the onset anchor.**

## Verify — 18 levels, every available depth pair

    grand form consistent on wired levels k = 1..19 (every residual linear in n)
    ab-initio depth series loaded for j = 1..3, k <= 19
      k= 2 ... k=19, each OK
    verify: 18 levels re-derived exactly, 0 wrong, 1 skipped
    VERIFY GREEN

Exactly — the same rationals, not agreement to some number of digits. The
`k = 19` line is the one that matters: **P₁₉ re-derived from `T(38,19)` and
`T(37,18)`, without `T(39,20)` or `T(40,21)`.**

RED controls (`--selftest`), all fire before the verify is believed:

- a perturbed `D_j` breaks the pin;
- one equation used twice is refused as singular;
- a corrupted lower level breaks the pin.

The grand form's own consistency is a fourth check and it is not optional:
`extract_ab` raises unless `P_k` minus the lower-level part is linear in `n` at
every wired level. It is.

## Predict — the cell that could not be swept

`--predict` pins past the wired table and prints what the tower then says:

    k=20 pinned, 3 depth pairs AGREE (2 independent checks);
         cells T(40,20), T(39,19), T(38,18)
    ...
    T(40,21) k=19: match

`T(40,21)` — the one cell `docs/b1-closure-plan.md` §3 says
"never fits", the reason its §6 table reads "out of RAM at any rung" — comes
out of the formula and matches the banked value. Every in-onset banked cell of
rows 40 and below that the tower touches matches; the run prints them.

Level 20, which the wired table never had, is pinned **overdetermined**: three
depth pairs, two independent checks, all agreeing. It predicts

    T(41,21) = 12639811314502944123098075912198
    T(42,22) = 66507597655339889181525572632880

and the whole `k ≤ 20` band of rows 41 and 42, none of which any sweep has
produced.

## What it costs, and what it buys

Coverage becomes `n ≤ 2·H_sweep + J - 1` for exact depths through `J`, against
`n ≤ 2·H_sweep` under the onset-anchor rule. Depths 1–4 are closed, so:

| target | old sweep ceiling | Undertow ceiling |
|---|---|---|
| a(40) | H = 21 (36.4 h, 363 GB disk) | H = 19 |
| a(41) | H = 21 at Nmax 41 | H = 19 |
| a(42) | H = 22 | H = 20 |

A height is ~3× compute, so the a(41) run stops needing both poles that
dominated a(40) — phase B (H20, 9.6 h/48c) and phase C (H21, 36.4 h/32c) — and
keeps only phase A's range, which was 6.3 h on 80 cores at Nmax 40.

Deeper depths extend it one term per level. `D_j` needs excess ≤ j-1 cluster
families, and `cpp/severance_w3_families.cpp` takes `emax` as an argument;
measured on dalby, emax = 4 costs 12.2 s / 138 MB at K = 8, 71.4 s / 577 MB at
K = 10 and 265.0 s / 1.54 GB at K = 12 — about 1.82× per unit K in time and
1.6× in RSS. `families 21 4` (depth 5) extrapolates to roughly 16 h and 103 GB:
inside dalby, but at the wall, and it is the run that would let level 21 pin
from `T(39,18)` and `T(38,17)`, both inside Motley's already-banked H ≤ 18
rows — i.e. **a(40) rule-independent in every cell, with no new sweep at all.**

## The row-40 regression

`experiments/undertow_a41.py` runs the assembled tower back at n = 40, with
row 40 **excluded from its own pinning set** (level 20's depth-1 cell is
literally `T(40,20)`, and pinning from a cell you then call a prediction is
circular). Level 20 then pins from `T(38,18)` and `T(39,19)` alone — tallest
cell H = 19 — and:

    level k=20 pinned from [(38, 18), (39, 19)] (tallest H=19)
    row 40 regression: 21 cells reproduced, 0 wrong
    banked row 40 re-sums to a(40) exactly

**Twenty-one of row 40's forty cells — every one with H >= 20, including
`T(40,20)` and `T(40,21)` — come back exactly from data no taller than
H = 19.** The RED control is a perturbed level 20, and it fails the
regression.

## Limits

- Levels 20 and 21 have no above-onset cell to cross-check against, by
  construction — that is the point of the method. Level 20's guard is the
  three agreeing depth pairs; level 21 has one pair until depth 5 exists, and
  should not be wired into `diagCoeffTable` before it has two.
- The depth identities are exact and derived, but they were *checked* against
  banked cells only at `k ≤ 19` (W3's 16–19 cells per depth). Using them at
  `k = 20, 21` is extrapolation of a derivation, not of a fit — but it is
  extrapolation, and the agreeing-pairs test is what stands in for a holdout.
- Everything below level 10 rests on Severance W1's ab-initio `P_k`; above it,
  on the wired table. Undertow does not change that dependency, it moves which
  *cells* the wired table needs.
