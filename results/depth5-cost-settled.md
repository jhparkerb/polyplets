# Depth 5 costs about 5 hours and 18 GB, not 103 GB

2026-08-22, executing `docs/last-orders.md` A1.2 and closing
`results/undertow-review-queue.md` row L-2. Measured on ayr; ladder at
`results/depth5/ladder.txt`, analysis
`experiments/depth5_cost_ladder.py`.

> **OUTCOME, 2026-08-23 — the run happened, and the RAM bracket missed.**
> `families 21 4` ran on dalby at 8 threads: **4 h 54 m** (17,660 s) and
> **18,743 MB** peak RSS. The wall projection below bracketed that correctly
> (3.1 h to 6.7 h). The RSS projection did **not** — 18.3 GB is 14% above even
> the pessimistic end, the one that assumed the deceleration stopped dead.
> The original title of this file claimed "9–16 GB" and was wrong; it has been
> corrected above. The headline conclusion survives — depth 5 is nowhere near
> 103 GB and fits dalby with room — but the *method* here brackets wall well
> and under-predicts RSS, so treat every RSS figure it produces, including the
> ~74–85 GB it implies for `families 21 5`, as a floor rather than a bracket.
> Gate outcome and mutation audit: `results/depth5-gate-green.md`.

## The answer

**At 8 threads, `families 21 4` projects to ~3.1 h and ~8.5 GB.** Holding the
top ratio flat instead — assuming the deceleration stops dead, which is the
pessimistic bound — gives **~6.7 h and ~16.1 GB**. Both ends are far inside
dalby's 125 GB.

Against what the tree asserted:

| source | wall | RSS |
|---|---|---|
| `docs/lastditch-ideas.md` §2 | 16 h | 103 GB |
| review row L-2, low end | — | 110 GB |
| review row L-2, high end | — | 390 GB |
| **measured ladder, decelerating** | **3.1 h** | **8.5 GB** |
| **measured ladder, no further deceleration** | **6.7 h** | **16.1 GB** |

L-2 said the geometric mean over the whole range overestimates the tail because
the ratio decelerates. It does, and it overestimates it by an order of
magnitude.

## The ladder

Five rungs, **8 threads throughout**. Fixed threads is not a detail: the family
DP's RSS scales with thread count, so a K-slope mixing widths is not a slope.

| K | wall (s) | RSS (MB) | wall ×/+2K | RSS ×/+2K |
|---|---|---|---|---|
| 8 | 6.52 | 128.9 | — | — |
| 10 | 48.16 | 462.9 | 7.39 | 3.59 |
| 12 | 219.20 | 1150.1 | 4.55 | 2.48 |
| 14 | 731.86 | 2459.5 | 3.34 | 2.14 |
| 16 | 1988.13 | 4239.2 | 2.72 | 1.72 |

Both ratios decelerate monotonically, which is the whole point.

## Why the extrapolation is worth anything: a real holdout

**K = 16 was predicted from the first four rungs before it ran.**

    predicted   1859 s   4607 MB
    measured    1988 s   4239 MB
    error       6.9% under      8.0% over

That is the only evidence the extrapolation carries. It is one rung out from
four points; the K = 21 projection is two and a half rungs out from five, so it
deserves less confidence than 8% — which is what the pessimistic bound above is
for.

## What this changes

**Depth 5 stops being the blocker it was priced as.** `docs/lastditch-ideas.md`
§2 called `families 21 4` "~16 h and ~103 GB. Inside dalby, at the wall", and
review row L-2 widened that to a "marginal" ~110–390 GB. Neither survives. At
8 threads it fits with an order of magnitude of headroom, and even at 40 threads
the RSS projection is ~42 GB.

What depth 5 buys is unchanged and is still the point: level 21 gains a second
pin pair from `T(38,17)`, so `P_21` — which today pins from one pair with
nothing checking it — gets agreement. `results/confidence.md` calls that the
last soft spot in the whole construction.

**It does not make depth 5 free of its other gate.** Review row B13 requires
`experiments/severance_w3_depth5_gate.py` to pass against the 15 banked
depth-5 cells at `k ≤ 19` before `D_5` is used at `k = 21`. That gate's selftest
is green and it is correctly RED in production until the `emax = 4` table
exists. This file prices the table; it does not license using it.
[**2026-08-24: the table exists and the gate passed** — all 15 cells match
exactly. B13 closed. `results/depth5-gate-green.md`.]

## Honest limits

- **The thread scaling is asserted, not measured here.** Every rung is 8
  threads, so the ladder is internally consistent, but the "×5 at 40 threads"
  arithmetic rests on the memory note that RSS scales with thread count. If it
  is sublinear the picture improves; if superlinear it worsens. One rung at two
  widths would settle it and was not run.
- **The decay model is fitted from two ratios.** The decelerating projection
  assumes the ratio's excess over 1 shrinks by a constant factor each step.
  A different model gives a different number, which is why the flat-ratio bound
  is quoted alongside it rather than buried.
- **Nothing here was run at K = 18 or 20.** The two rungs between the ladder's
  top and the target are projected, not measured. K = 18 at ~1.2 h would halve
  the remaining extrapolation and is the obvious next rung if the decision
  needs tightening.
- **This prices a run; it does not approve one.** Whether depth 5 gets computed
  is jasonp's call, and the ladder was run because A1.2 named these two rungs as
  the measurement that settles the price.

## Reproduce

    python3 experiments/depth5_cost_ladder.py

Instant, from the banked ladder. The ladder itself was
`./build/severance_w3_families families K 4 8` for K = 8, 10, 12, 14, 16 on ayr,
2026-08-22 01:17–02:07 EDT, rev `a66bc61`, total wall 50 minutes.
