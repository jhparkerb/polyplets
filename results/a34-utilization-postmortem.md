# a(34) core-utilization postmortem — verified, root-caused, and what (if anything) beats it

**Date:** 2026-07-07. **Status:** analysis only, no code changed, no job launched.

## 1. The 19.8% figure is confirmed, independently, from raw telemetry

Recomputed directly from `results/ns_a34/cost_profile_dalby.tsv` (per-column
`wall_s`/`cpu_s`, not the earlier chat estimate):

```
TOTAL wall_s=13300.4  cpu_s=210666.1  util=19.8%   (matches orchestrate wall 13316.7s)
```

Per-height breakdown (only H3–H18 are real sweep; H19+ are closed-form P9–P15,
zero compute):

| H | wall_s | cpu_s | util% | % of total wall |
|---|---:|---:|---:|---:|
| 12 | 36.8 | 351.7 | 11.9 | 0.3% |
| 13 | 98.9 | 1474.7 | 18.6 | 0.7% |
| 14 | 257.9 | 4829.9 | 23.4 | 1.9% |
| 15 | 407.3 | 9090.2 | 27.9 | 3.1% |
| **16** | 722.1 | 19395.0 | **33.6** | 5.4% |
| 17 | 2376.2 | 47028.2 | 24.7 | 17.9% |
| **18** | 9335.5 | 128349.6 | **17.2** | **70.2%** |

**Key finding: utilization does not degrade uniformly — it peaks at H16 (33.6%)
then *reverses* exactly where the wall-clock is concentrated.** H18 is 70% of the
run and its utilization (17.2%) is the worst of any height that matters. This
rules out "it's just an average over an otherwise-fine run" — the waste is
concentrated precisely where fixing it pays the most.

## 2. The dependency-graph recollection: confirmed, and it's the wrong axis

Verified against the engine's own design record
(`docs/next-system/designs/07-height-scheduling.md`, git history at `78602f8^`,
since removed from the working tree at project-tidy but preserved in git log):

> "Columns within a height are strictly sequential — column c+1's frontier is
> produced from column c. So there is no 'odd/even **columns**' scheme: there is
> no column-level independence to exploit."

This is **iron-clad, not a scheduling choice**. The frontier signature at column
c+1 is defined as a function of the fully-merged frontier at column c (each
king-adjacency step reads the complete boundary state to its left); you cannot
start column c+1 before column c's map+merge has produced its output. No
scheduler, no amount of hardware, no algorithm change *at the current state
representation* gets around this — it is the transfer-matrix method's structure,
the same reason any left-to-right DP is sequential in the sweep direction.

**But this is not what explains the 17-33% utilization within a single column.**
Heights ARE mutually independent (`a(n) = Σ_H T(n,H)`, separate sweeps) — that's
a genuinely different axis of parallelism, already identified and explored
(§4 below) — but a34 ran heights one at a time on dalby (no `--overlap-heights`),
so it isn't in play for this run. The question that actually matters is: **why
does one column's own map+merge phase, fanned out over thousands of shard units
across 80 cores, only average ~17-34% busy?** The column-sequential fact
explains why heights can't be pipelined *within themselves*; it says nothing
about intra-column core occupancy.

## 3. Root cause of the intra-column waste: a diagnosed, shipped-but-broken fix

This part is not new speculation — it's already been measured twice in this
repo, for two different engine generations, and the second measurement shows
the fix regressed.

**Design (`docs/next-system/designs/08-straggler-tail-sizing.md`, the old
whole-column engine):** the imbalance is not unequal state counts (units are
equalized by record count) — it's *per-state cost variance*. A handful of
branching-heavy states dominate a column's map wall while the rest finish early.
Finer static partitioning (`--unit-mult`) makes it **worse, not better**
(measured: mult 4→16 turned +9.5% wall and pushed makespan/ideal from 1.215×
to 1.780×) because it *isolates* the heavy states into one giant unit instead of
dividing them. Predictive LPT ordering caps out at ~71% of the gap closed and
needs a predictor that doesn't exist (rank-correlation of unit cost
column-to-column is only 0.23–0.49). **Reactive work-stealing was the one thing
that worked in simulation: grain 0.05 closes 92% of the gap, no predictor
needed** — this became plan T2.3 and shipped.

**Production reality (`results/steal-tail-h18.md`, the kink-carry engine, a32
data — same config a34 used):** work-stealing was configured on
(`--steal-grain 0.05`) and **fired zero steals across the entire run — every
single heartbeat, every column of H18 included.** Root cause, confirmed against
the live code (`orchestrator/sweep.go:909-914`):

```go
func stealEligible(r *runningUnit, grainRecs uint64) bool {
    if r.stopped || r.u.noSteal || r.processed.Load() == 0 {
        return false
    }
    rem := r.remaining()
    return rem > grainRecs && rem >= 2*indexStride
}
```

`stealEligible` gates on **remaining record count** (`rem > grainRecs`). But the
late-stage H18 stragglers are exactly the case `stealScore`'s own comment
anticipates and `stealEligible` filters out first: "a compute-heavy straggler (a
few pathological keys) can have few records remaining yet dominate the column
tail." Because their *record* remainder is small, they never clear the record
floor, so the wall-time-aware ranker (`stealScore`, which computes seconds
remaining from the observed rate) never even gets to see them as candidates.
Per-round telemetry for the peak column (H18 col4, 731s) shows the signature
directly: `stage10..stage17` have map_cpu roughly flat (~350 cpu-s) while
map_wall doubles (25s→52s) — a few units grinding on ~9 of 80 cores while the
rest sit idle, for 8 of the column's 20 rounds.

**This is a real, scoped, already-understood bug — not an intrinsic limit.**
The fix is narrow: make `stealEligible`'s floor wall-estimate-based (reuse
`stealScore`'s own rate-based remaining-seconds estimate, or a cheap cost
proxy) instead of raw record count, so a low-record/high-compute straggler still
clears the bar. `results/steal-tail-h18.md`'s own back-of-envelope: H18 col4
~731s could plausibly shrink toward map_ideal 81s + merge 263s ≈ 344s if the
tail is actually splittable — roughly halving the dominant height, ~1/3 off a
term's total wall. Scaled against the per-height table above, that's plausibly
the difference between ~13,300s and ~9,000-10,000s wall for a34-shaped runs,
i.e. utilization moving from 19.8% toward the high-20s% — a real, substantial,
not-yet-banked improvement, gated on one open question:

**Unresolved (explicitly flagged, never measured):** is the H18 tail *many*
separable heavy states (splittable — the fix helps) or a *single* pathological
state (unsplittable — no scheduling change, however smart, can divide one
state's own compute; the tail is then a genuine floor)? `steal-tail-h18.md`
calls this "not determinable from banked per-round logs — needs per-unit map
timing from one instrumented H18 column." That's a cheap, minutes-long
diagnostic (not a job requiring a beg-and-agree), never run because the project
closed before it was prioritized.

## 4. Everything else has already been tried and is either capped by physics or measured worse

- **Note on the ~79.3% utilization figure previously cited from
  `results/dalby-perf-audit.md`:** that run is not a fair comparison. It probed
  `--maxn 24, heights 1-15` (much shallower/cheaper than a34's real top heights
  H17/H18) **with `--overlap-heights 15` enabled**. a34's own PROVENANCE.md
  explicitly records `(no overlap-heights)` for the production run — overlap
  was available and even measured to help, but was deliberately not used for
  the record run (see next bullet). The 79.3% figure never exercised the
  H17/H18 straggler-tail pathology that dominates a34's wall-clock; it isn't
  evidence the same run mode was available and skipped for no reason.
- **Cross-height overlap** (`designs/09-cost-model-and-work-assignment.md`,
  the "shared-pool scheduler" idea — start the next height early to fill cores
  a draining height frees up). Real idea, matches the genuine height
  independence. **Measured RAM/spill-bounded**: batch overlap recovered only
  ~32% (52/80 eff cores) before 3× oversubscription collapsed dalby to 26
  effective cores on a spill storm; adjacent top heights are both expensive, so
  overlapping them is peak-with-peak RAM, not peak-with-cheap-tail. Also
  disqualified operationally for a production record run: `--overlap-heights`
  disables both checkpointing and work-stealing simultaneously (a crash re-runs
  every in-flight height from scratch) — unacceptable for a multi-day run.
  Correctly parked, not free money left on the table.
- **Cross-machine work-stealing** (`designs/border-raid.md`). Bandwidth-dead:
  dalby is a remote cloud box reachable only via a sub-MB/s gympie uplink, and
  the column merge is all-to-all (~0.4-1 GB/column would need to move). Analyzed
  and correctly parked.
- **Finer static unit-mult / predictive LPT** (`designs/08`, Findings 2 & 5).
  Both measured to make the tail *worse*: static repartitioning isolates the
  heavy states rather than dividing them; LPT needs a predictor that doesn't
  exist and caps at 71% even if it did. Correctly rejected already.

## 5. Bottom line

- The column-sequential dependency the recollection named is **real and
  iron-clad** — it bounds *sequencing within a height* and correctly rules out
  any column-level parallelism scheme. It does **not**, however, explain the
  measured utilization number; that lives one level down, inside a single
  column's map phase.
- The actual cause of a34's 19.8% (and its concentration at H18, the height that
  matters) is a **known, already-designed, already-partially-validated
  mechanism (work-stealing, T2.3) that is live in the code but disabled in
  practice by a record-vs-wall-time mismatch in its eligibility gate** — a
  bug of omission from porting the scheduler from the old whole-column engine
  to the kink-carry engine, not a fundamental limit. This is the "substantial
  improvement, not yet built" bucket, not the "iron-clad, cannot be better"
  bucket.
- The one gate before committing to that fix: run the cheap per-unit H18 probe
  to learn whether the tail is splittable. If it is, wire `stealEligible` to a
  wall-estimate (not record-count) floor and re-validate on a small-n gate
  before trusting it for any future term. If it isn't (a single pathological
  state), the 17-33% ceiling on the top heights is real and this whole
  investigation converges on "cannot possibly be better" for the current state
  representation.
- Pie-in-the-sky beyond that: a genuinely different state representation where
  the per-column transition is a small enough algebraic object to compose via
  associative/parallel-scan doubling (skipping ahead many columns at once)
  would break the sequential-column floor itself — but the frontier state space
  here is combinatorial and size-varying, not a fixed-size matrix, so this is a
  research question, not an engineering one, and design 09's own cost model
  (cost lives in per-state branching, not a fixed operator) argues against it
  being tractable. Real distributed clusters (many boxes, fast interconnect,
  splitting the top height's own key-range with a per-column shuffle) is the
  other genuine escape, explicitly parked for "a24+ on a real cluster" and
  already decided against on cost grounds for the current setup.
