# Even Keel — falsifiable predictions for the frontier-scale confirmation

**Committed BEFORE the confirmation run, on purpose.** These are the numbers
jasonp will hold us to. Each prediction states the number, the confidence,
and — required — exactly what we investigate if it is invalidated. Written
2026-07-09 on branch `even-keel`.

## The question

Does balanced partitioning (`BalancedCutsMulti`, D1/D2) deliver the big
utilization win at the scale that actually matters — the dominant height
H18 at maxn=34, ~16.5M-record columns — not just the modest 1.45x seen at
D5's H15 (~795K records)?

## Evidence feeding these predictions

1. **Isolated-stage scaling curve** (`experiments/full_column_bench.cpp`,
   dalby 80 cores, real `kinkStageTransition`, output verified identical):
   balanced effective cores vs stage-table size N — 250K→18.8, 500K→28.2,
   1M→44.3, 2M→61.3, 4M→72.2, 8M→74.8, 16M→76.0. Unbalanced stays 5–9 at
   every N. **Balanced eff rises with records and saturates ~72–76 above
   N=4M.**
2. **D5 production anchor** (H15/maxn30, real sweep, byte-identical output):
   fat-column (col 3–9) eff `cpu_s/wall_s` — OLD ~22, NEW ~34; whole-sweep
   wall 204.3s→140.9s (1.45x).
3. **Banked a34 per-height OLD eff** (different rev/flags — informative for
   the OLD *trend*, NOT a valid A/B baseline): H15 22.3, H16 26.9, H17
   19.8, H18 13.75. OLD eff PEAKS at H16 then DECLINES — the straggler
   worsens with scale.

## The one real uncertainty (and the quick experiment that kills it)

Production whole-column eff = isolated-stage eff × a "whole-column
discount" (loss to round-size variation across the H+1 rounds, the separate
merge phase, seed/finalize, and per-round barriers). At H15, isolated ≈ 67
(interp at stage-table ~2.9M = 795K×3.6), production NEW = 34, so
**discount ≈ 0.51**. The question is whether that discount is CONSTANT
(→ H18 NEW ≈ 76×0.51 ≈ 39, a plateau) or IMPROVES at scale (→ ~50), because
at H18 every round has millions of records so the small-round drag shrinks.

**Quick experiment to resolve it BEFORE the 5.2hr H18 run:** run H16
(2.18M frontier, ~12min each side) old-vs-new. It gives a second production
discount point (stage-table ~7.85M → isolated ~74.7). If H16 NEW ≈ 38, the
discount is constant and P6 collapses to ~39 at H18 (still a 2.8x win, but
the isolated 76 is NOT reached — the next bottleneck is whole-column
overhead, not partitioning). If H16 NEW ≈ 45–50, the discount improves and
H18 P6 tightens to ~50. Either way we learn it in 25 minutes instead of
betting 5.2 hours.

## Predictions (H18 @ maxn=34, fresh OLD binary vs even-keel, identical flags)

**P1 — Correctness (non-negotiable).** NEW per-height T(n,18) output is
byte-identical to OLD and to banked `results/ns_a34`. `combine --diff-b`
→ PASS.
- *If invalidated:* STOP everything, revert D2. A value change means
  `BalancedCutsMulti` or the cut→bounds handling has a real bug; the entire
  approach is void until fixed. This is the hardest gate.

**P2 — Fresh OLD baseline reproduces the banked degradation.** A fresh OLD
(pre-even-keel) run's H18 fat-column eff = **13.75 ± 2.5**.
- *If invalidated (e.g. fresh OLD ≈ 20):* the banked a34 numbers hid a
  config/flag/rev confound; find it before trusting ANY A/B. (Likely
  suspects: persistent-workers, unit-mult, GOGC differences vs the banked
  run.)

**P3 — OLD straggler confirmed structurally.** In the OLD run, the single
largest map unit processes **> 8×** the median unit's records (the
open-ended last bucket). NEW: no unit > **2×** median; units within ±25%.
- *If invalidated (OLD units already balanced):* `SampleKeysMulti` is not
  the imbalance source at this scale — the root-cause diagnosis is wrong,
  re-open it before claiming the fix works for the right reason.

**P4 — THE HEADLINE: NEW H18 fat-column eff.** NEW col-2..8 eff_cores
**≥ 38** (≥ 2.7× over OLD 13.75). Point estimate **~45**, plausible range
**[39, 55]** pending the H16 tightener.
- *If invalidated (NEW < 38):* the cap is NOT the map straggler but
  whole-column serialization. Use D3 per-round telemetry
  (`map_eff_cores`/`merge_eff_cores`) to identify which round-type is
  serial — merge phase (merge-mult too low / merge not balanced),
  seed/finalize (single-threaded), or barrier count. That becomes the next
  deliverable ("Even Keel D6: parallelize the residual serial phase"). This
  is the prediction most likely to be partially wrong, and its failure is
  the most informative.

**P5 — Wall-clock speedup.** NEW H18 whole-height wall ≤ **0.5×** OLD
(≥ 2.0× faster); point estimate ~2.7×.
- *If invalidated (< 2.0×):* either eff didn't rise (see P4) or CPU
  inflated (see P6). Cross-check which.

**P6 — CPU-seconds conserved.** NEW total cpu_s within **±12%** of OLD
(expect equal-to-slightly-lower). The `BalancedCutsMulti` full-index-union
read adds < 1% (DD8).
- *If invalidated (NEW cpu > OLD +12%):* balanced partitioning is doing
  more total work than expected — profile the sampler and the reduce; the
  full-index-union read or finer effective balance may be adding cost that
  eats the wall win.

**P7 — The gap grows with scale.** NEW/OLD eff RATIO is larger at H18 than
at H16 than at H15. Predict: H15 ~1.5× (measured: 34/22), H16 ~1.8–2.2×,
H18 ~2.7–3.5×. Because OLD degrades with scale (26.9→13.75) while NEW holds
high.
- *If invalidated (ratio flat or shrinking):* OLD's scale-degradation is
  NOT the straggler we think it is — re-examine what actually caps OLD eff
  at large H.

**P8 — Unbalanced/straggler independence from scale.** If we also measure
the OLD run's per-round idle signature, the straggler's ABSOLUTE core-waste
grows with records while NEW's does not (mirrors the isolated curve: OLD
flat ~7, NEW rising).
- *If invalidated:* the isolated benchmark and production disagree on the
  straggler's scale behavior — reconcile before extrapolating.

## What "confirmed" means (the bar for declaring the big win real)

- **Strong confirm:** P1 holds AND P4 ≥ 45 AND P5 ≥ 2.5× — balanced
  partitioning delivers ~50 effective cores on the dominant height, a
  ~3.5× utilization win, byte-identical. The back is broken in production.
- **Partial confirm:** P1 holds AND P4 ∈ [38, 45] AND P5 ≥ 2× — a real,
  large win (~2.7×), but whole-column overhead (merge/seed/finalize) is the
  next ceiling below the isolated 76; opens D6.
- **Not confirmed / plateau:** P4 < 38 — balanced partitioning alone does
  NOT scale to the dominant height in production; the isolated benchmark
  overstated it, and the real bottleneck is elsewhere (P4's investigation).
  This would be the important negative result.

## Recommended run sequence (confound-controlled)

1. **H16 @ maxn=34 old-vs-new (~25min total)** — the quick tightener for
   P4/P7. Resolves the constant-vs-improving discount.
2. **H17 @ maxn=34 old-vs-new (~80min total)** — a 6M-record production
   point, further tightening before the big spend.
3. **H18 @ maxn=34 old-vs-new (~5.2hr total)** — THE definitive
   dominant-height confirmation, exact 16.5M-record benchmark regime.

Stop after any step if predictions are invalidated in a way that changes
the plan (esp. P1 fail → stop immediately; P4 plateau at H16 → investigate
before H18). Every run: fresh OLD binary (built from `aa4bbd29`, rev
verified in the banner) vs even-keel binary, IDENTICAL production flags,
`--overlap-heights 1 --heights H`, clean run dirs, machine idle,
byte-identical output check. Never the banked a34 cost_profile as baseline.
