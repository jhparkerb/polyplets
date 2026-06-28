# 08 — the map straggler tail: sized, and work-stealing vs LPT (plan T2.3)

Started as "can we combine `--unit-mult` with LPT ordering of units?" The
measurement says: **no — build reactive work-stealing (tail-split, plan T2.3),
not predictive LPT ordering.** Tools here re-run on any future trace with no
engine run. Triggered by a live observation: ayr and dalby both sat at **5–7%
core utilization** in the map straggler tail of their H20 peak column.

## What we measured and how

Per-unit cost is now traceable: `map_worker` already records `cpu_s`/`records`;
`sweep.go` emits one `event=unit H= col= u= lo= hi= out_records= cpu_s= wall_s=`
line per unit **iff `POLY_UNIT_LOG` is set** (result-invariant, off by default so
production logs stay clean). Two gympie probes, both `--compare` PASS (so the
trace is from a correct run): **a(16)** (cores 8, mult 8, no spill) and **a(18)**
(cores 8, mult 4 = production oversubscription, `--ram 128 MB` to force spill so
heavy units exhibit the real spill-driven tail).

- `scripts/unit_cost_analysis.py TRACE` — per-column cost spread, column-to-column
  predictability, and wall-weighted makespan under current / LPT / split.
- `scripts/sched_sim.py TRACE` — trace-driven policy simulator: replays the real
  per-unit costs under the current pull-queue, perfect-reorder LPT, and Cilk-style
  work-stealing (half-split the longest straggler's remaining work, down to a
  `--grain` floor). **The bench for evaluating scheduling without a full run.**

## Finding 1 — the imbalance is per-state cost variance, not unequal counts

`SampleKeys` cuts the frontier at equal *record* intervals (`stride =
Records/(numCuts+1)`), so every unit gets ~equal **state-count** by construction.
The roadmap's "heavy states cluster in fat key ranges → unequal units" framing is
wrong: counts are equalized; the imbalance is per-state cost variance (branching)
landing unevenly across equal-count quantiles.

## Finding 2 — per-unit cost is NOT predictable a priori (so LPT ordering is weak)

Column-to-column rank-correlation of per-unit cost (the realizable "use the
previous column as the size estimate" predictor): **0.23 at a(16), 0.49 at a(18)**
— weak, and on the peak columns it scatters/goes negative. A makespan sim ordering
each column's units by the previous column's costs realizes only ~2% (a16) to ~6%
(a18) of map-wall, and is *worse* than doing nothing on the biggest columns. The
strong signal in the data (`cpu`~`out_records` ≈ 0.8) is **output** volume — known
only after running; its a-priori cause is per-state branching (a structural
function of the signature), an untested but ceiling-capped predictor (Finding 4).

## Finding 3 — the tail GROWS with scale; the floor is crossing 1.0

| | a(16) | a(18) (spill, prod mult) | live a(20)/a(21) |
|---|--:|--:|--:|
| current scheduler makespan / ideal | 1.116× | **1.215×** | — |
| map-wall wasted now | ~10% | **~18%** | — |
| straggler floor (max unit / ideal, wall-wtd) | ~0.5 | **0.84** | (tail at 5–7% util) |

The waste roughly doubled a(16)→a(18) and the **straggler floor** (heaviest single
unit ÷ perfect-packing time) climbed 0.5→0.84. When it crosses **1.0** (a single
unit outlasts a perfectly-packed column — already true on individual a(18) mid-tail
columns, e.g. H18 col8/9/11 at 2.1–2.4×), **reordering becomes mathematically
futile and only splitting helps.** a(20)/a(22) will cross it wall-weighted.

## Finding 4 — work-stealing beats even perfect LPT, predictor-free (the bench)

`sched_sim.py` on the a(18) trace, wall-weighted, fraction of the 21.5% gap closed:

| policy | makespan/ideal | gap closed | needs predictor? |
|---|--:|--:|:--:|
| current (pull-queue) | 1.215× | — | — |
| LPT, **perfect** reorder | 1.062× | 71% | yes (and realizable ≈ 6%) |
| **steal**, grain 0.02 | 1.006× | **97%** | **no** |
| **steal**, grain 0.05 | 1.018× | **92%** | **no** |
| steal, grain 0.10 | 1.029× | 86% | no |
| steal, grain 0.25 | 1.104× | 52% | no |

Work-stealing closes **86–97%** of the gap at any reasonable grain, with **no cost
predictor** — and beats even *perfectly-predicted* LPT (71%), because it *splits*
the dominant straggler that reordering can only *move*. This is the canonical
non-clairvoyant result (Blumofe–Leiserson work-stealing; MapReduce speculative
execution): when sizes are unpredictable, go reactive, not predictive.

## Finding 5 — finer static units (unit-mult) make it WORSE, not better

The roadmap gated work-stealing on "only if high unit-mult can't fix the tail."
Tested directly: a(18) at mult=16 vs the mult=4 baseline (both spill, `--compare`
PASS):

| | mult=4 | mult=16 | pre-registered |
|---|--:|--:|--:|
| wall | 3434s | **3759s (+9.5%)** | predicted *down* |
| as-emitted makespan / ideal | 1.215× | **1.780×** | predicted ~1.03–1.05× |
| straggler floor (max/ideal) | 0.84 | **0.92** | predicted ~0.2 |

Refining the static partition does not *divide* the heavy work, it **isolates** it:
the pathological states collapse into one giant unit (0.92× a packed column) while
the rest go trivial, and that lone unit strands cores worse than the coarser binning
did. The heaviness is **concentrated by key, not spread** — the floor already being
0.84 at mult=4 was the tell. A *key-based* static cut cannot subdivide it; only a
*cursor-based* cut of the running straggler's remaining range (work-stealing) can. On
the same mult=16 trace, `sched_sim` steal still reaches 1.008× (99%). **This closes
the question: unit-mult cannot fix the tail, so work-stealing is necessary, not
optional.**

## Verdict

- **Build reactive work-stealing / tail-split (plan T2.3).** Worth **~18% of
  map-wall at a(18) and growing**; predictor-free; the only lever that survives the
  straggler floor crossing 1.0 at record scale. Grain ≈ 0.05 of the per-core share
  is the sweet spot (wide tolerance 0.02–0.10).
- **Do NOT build predictive LPT ordering of units.** Capped at a 12.6% ceiling that
  needs perfect prediction; realizable ~6%; degrades exactly when the tail worsens.
- Implementation sketch (T2.3): detect a unit running ≫ median; the straggler stops
  at its `cursor`, hands `[cursor, hi)` to an idle worker (half-split), repeat down
  to a grain floor. The map output is unchanged (merge recombines by key), so this
  is **result-invariant** — perf gate only.

## Scope & caveats

- **Map-phase-internal only.** The merge under-utilization and the map→merge
  barrier (the rest of the ~25% whole-run waste) are separate, addressed by the
  seek-index fix (`06`) and `--overlap-heights`.
- The steal sim splits *remaining work* evenly; the real split is by *key-range*,
  so cost-split is approximate — treat 92–97% as an optimistic upper bound (real
  recovery is lower, but still far above LPT's realizable ~6%). Detection latency
  and IPC overhead are partly modeled by `--grain`.
- a(18)/8-core is a proxy for a(20)+/30–80-core. Re-run both scripts on the
  a(20)/a(21) `--per-height-out`-adjacent traces when available (they predate
  `POLY_UNIT_LOG`, so a fresh instrumented a(19)/a(20) confirm is the next datum).
