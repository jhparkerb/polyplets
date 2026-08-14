# Depth-swapped anchors: the residual band closes from H <= 19

2026-08-14. Instrument: `experiments/depth_swap_anchors.py` (`--pstair`,
`--identity`, `--rebuild`). Every number below is printed by that script.
Proof of the identity: `docs/proofs/depth-swap-residual.md`. Certification map
as it now stands: `results/anchor-cut-map.md`.

`docs/b1-closure-plan.md` §7 states that `T(40,21)` "cannot be finessed",
because level 19's own two anchors are `T(39,20)` and `T(40,21)` — both in the
band no sweep reaches. That is true of the *onset* instance of the staircase.
It is not true of the identity.

## Result

**All six residual cells rebuild exactly from cells at H <= 19, with no cell
above H = 19 read at any point.** `T(38,20)`, `T(39,20)`, `T(40,20)`,
`T(39,21)`, `T(40,21)`, `T(40,22)` — six of six against the banked triangle.
The read guard is enforced in the accessor, so a slip aborts rather than
passing quietly; the run reports `highest banked height read: H = 19`.

It is not only those six. From the same H <= 19 inputs, **every cell above the
guard in rows 20..40 is reproduced — 231 cells, 0 mismatches** — so the entire
band the sweep cannot reach comes back, not just the cells the closure plan
called residual.

## The mechanism

The grand-form staircase (`docs/proofs/grand-form.md`, `scripts/gen_grand_pin.py`)

    T(H+1+k, H+1) = sum_{i=0..k} mu_i T(H+k-i, H)        for H >= k+1

adds exactly one new constant `mu_k` per level. Pinning it at the onset
`H = k+1` is what drags in the unreachable cells. Below onset the residual is
not noise — at depth `j = k+1-H` it is exactly

    R(k,H) = D_{j-1}(k) - sum_{i=0..j-1} mu_i D_{j-i}(k-i),      D_0 := 0

with `D_j` the below-onset defect of `results/onset-defect-depths234.md`,
computed by `experiments/severance_w3_depths.py` from bounded-excess cluster
weights alone — no banked triangle, no wired `P_k`. At depth 1 this collapses
to `R = -3 D_1(k)`, which is the same statement as W1's
`lead(R_k) = (-3)^(k+1) D_1(k)` (`results/severance-w1-anchor-cut.md`) read
through the staircase.

So `mu_k` can be pinned from the depth-`j` instance instead, whose cells lie in
columns `k+1-j` and `k+2-j`:

| level | depth used | columns touched | previously needed |
|---|---|---|---|
| 18 | 2 | 17, 18 | `T(38,20)` |
| 19 | 2 | 18, 19 | `T(39,20)`, `T(40,21)` |
| 20 | 3 | 18, 19 | `T(42,22)` — past the triangle entirely |

`mu_18` and `mu_19` pinned this way agree with the ordinary onset-anchor route
at every level where both exist (k = 0..19), and `mu_20` — which the banked
triangle cannot pin at all, its anchor being `T(42,22)` — reproduces
`T(40,20)` exactly.

## Evidence

`--pstair`: the step the proof rests on — the P-staircase is a polynomial
identity, not an onset-conditional one — checked at **1026 instances** spanning
both sides of onset and into negative `n`, 779 of them below onset,
mismatches 0.

`--identity`: 54 instances at depths j = 1, 2, 3 and k <= 20, exact `Fraction`
arithmetic, **54 of 54 holding**. Two RED controls, both firing at 54/54: the
residual is never zero (so the defects are load-bearing), and dropping the
mu-weighted sum never reproduces it (so the correction's *shape* is
load-bearing, not just its leading term). The staircase is separately checked
to have zero residual at and above onset before any of this runs.

## The reach this buys

With a sweep to `H_max` and defects closed to depth `J`, level `k` is pinnable
whenever `k <= H_max + J - 2`, and row `n` closes when

    n <= 2*H_max + J - 1

against the closure plan's current `n <= 2*H_max - 1`. With the shipped
`D_1..D_3` and `H_max = 19`: **n <= 40**, which is the whole enumeration
target — the H = 20 rung the closure plan builds toward is not needed for it.
`D_4` (excess <= 3 families, already built at K = 19, would need K = 21) would
give `n <= 41`, but that also needs the sweep run at `Nmax = 41`, which is a
separate compute question and is not costed here.

## Honest limits — read before quoting any of this

- **This demonstrates the arithmetic, not rule-independence.** The H <= 19
  inputs here are the incumbent's own banked cells. The claim that the residual
  band is closed *rule-independently* needs Motley's rows substituted for them;
  that is a straight input swap, not new machinery, but it has not been done.
- ~~**The residual identity is verified, not proved.**~~ **Proved
  2026-08-14**, `docs/proofs/depth-swap-residual.md`: the law values satisfy the
  staircase identically (the P-staircase is a polynomial identity, so it
  carries no onset condition), and substituting `T = law + defect` leaves
  exactly the defect combination. The 54 instances are now a check on the
  arithmetic rather than the evidence for the shape.
- **The depth-j identity itself is single-sourced.** `D_j` comes from one
  script. jasonp's standing condition (2026-08-14) is that these cells count as
  shored up only once that identity is re-derived independently of
  `experiments/severance_w3_depths.py`. Until then this is a check on the
  incumbent, not a second source.
- `mu_20` has no independent confirmation of its own — nothing in the banked
  data can pin it. Its only evidence is that it reproduces `T(40,20)`.
