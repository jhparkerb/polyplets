# 09 — a-priori cost model from the cell-budget law, and how to assign work

The per-column cost of the fold engine is **predictable from first principles** —
no calibration run. This turns work-assignment (#32 cross-machine split, within-box
resource concentration, overlap timing) from "measure or guess" into "compute," and
it identifies the hard makespan floor. Derived from the full a(21) frontier profile
(`results/ns_a21/frontier_profile.txt`, all 441 columns, H=1..21).

## The law (measured, three clean parts)

Cost of a column ∝ its **frontier size** (distinct boundary signatures). Across the
whole sweep that frontier obeys:

1. **Geometric collapse.** Past its peak, a height's frontier shrinks by a constant
   factor **ρ ≈ 0.42 per column** (0.41 for tall strips, ~0.47 for short), nearly
   height-independent. The "cliff" past col 5–6 is just ρ⁶ ≈ 0.5%.
2. **Cell-budget width law.** Active columns (frontier ≥ 1% of peak) obey
   **active_width + H ≈ N + 6** (N = maxn = 21). Measured `active+H` = 26–27 across
   H = 8..20. Every row of height costs ~one column of width: a polyplet spends ≥H of
   its ≤N cells spanning the height, leaving ≤(N−H) to fund horizontal extent. Tall
   strips are intrinsically narrow.
3. **Peak grows ~geometrically, bending at the top.** peak_frontier(H)/peak(H−1) is
   ~2.6× through the mid heights, then **bends down** toward the pole as the width
   budget vanishes: 2.42 (H16) → 2.17 (H18) → 1.92 (H19) → **1.84 (H20)**. So the top
   heights are large but *less* dominant than a flat 2.4× would say.

Consequence: cost is **front-loaded** — 74–87% of a tall strip's wall lands in cols
≤ peak+1 (peak col ≈ 2–4, drifting earlier for tall H). Cols 6→21 are a rounding
error.

## The model

```
cost(H, col) ≈ peak_cost(H) · ρ^max(0, col − pk(H))      ρ ≈ 0.42,  pk ≈ 3
peak_cost(H) ≈ peak_cost(H−1) · r(H)                     r: 2.6 → 1.84 (bends near N)
active columns ≈ N + 6 − H                               (negligible cost beyond)
```

peak_cost(H) is anchored from any partial run's measured `frontier_out` ladder and
extrapolated one or two heights with the bent r. That gives the **full per-(H,col)
cost map of an unstarted term** — wall, and (× bytes/state) the per-column disk/RAM —
before launching it. This is M3.5 sizing made per-column-precise.

## How it changes work assignment

**1. Cross-machine height split (#32) becomes a-priori exact.** Feed
`heightsplit_plan.py --costs` the predicted `peak_cost(H)·(active-width sum)` per
height instead of a flat geometric r. Two payoffs: the LPT/dynamic assignment uses
*true* costs (no calibration run), and the **bent top makes balancing easier** — the
fast box's atomic top-height load is ~47% of total, not the ~58% a flat r predicts,
so it has more room to also take tail heights.

**2. The makespan floor is now named and quantified.** The single most expensive
column is **H_max's peak column (col ≈ 2)**, and it is *atomic* — sequential within
its height, unsplittable across heights. No height-level schedule can beat
`cost(H_max, col2) / throughput`. For a(21) that one column is ~9 h on the unfixed
engine. The only lever under that floor is intra-column key-range distribution with a
per-column shuffle (deferred, designs/07 §floor) — so don't look for a height-level
scheme to beat it.

**3. Within-box: concentrate effort on the peak, coast the tail.**
- The expensive levers — work-stealing (designs/08), the seek-index merge fix
  (designs/06), full core fan-out — pay off **only on cols 0–4**. Cols 6+ are ~free.
- The tail is **over-partitioned**: spawning `cores·mult` workers for a few-thousand-
  state column is fork/exec + merge-barrier overhead larger than the work. Cap units
  by frontier size on the tail (e.g. ≥ a few k states/unit); near-zero wall but it
  removes a per-column fixed tax that recurs ~16×/height.

**4. Cross-height feed-forward: ramp the next height in as the cliff drops (the key
policy).** Heights are independent, so the next one can start anytime — the only limit
is RAM/disk. The collapse is *predictable* (×ρ/col), so the orchestrator can
feed-forward: once a height crosses its peak (~col 4), its columns free cores at a
**known** rate (surplus = cores − peak·ρ^(col−pk)), and that surplus should be handed
to the **next** height's map — progressively more each column as the cliff drops. This
is a shared global work-pool pulling the highest-value ready work across all in-flight
heights (the "shared-pool scheduler"), not the static K-at-a-time `--overlap-heights`.

**The cliff shape makes this RAM-safe for free.** Ramping the next height up *exactly
as the current collapses* overlaps one height's PEAK with another's cheap TAIL (tiny
frontier ⇒ tiny working set) — never peak-with-peak, which would double peak RAM. So
staggering by the collapse is simultaneously utilization-optimal **and**
memory-bounded; the cost model proves the two goals coincide. This is the direct fix
for the **live 5–7% tail-utilization trough** (a height's tail idles the box today
only because the next height hasn't been started). Concretely: keep a running estimate
of free cores from the model, and the moment a height passes its peak, begin pulling
the next height's peak-column map onto the freeing cores.

**5. New candidate lever — cost-aware partitioning (testable).** The cell-budget law
suggests a state's branching cost rises with its *remaining* budget (more cells left ⇒
more viable extensions). If per-state cost is estimable from a cheap budget proxy
(lowest-n with nonzero count, off the counts vector), partition units by predicted
**cost** rather than equal **count** — pre-balancing the units and shrinking the
straggler tail *at the partition stage*, potentially obviating work-stealing on the
cheaper columns. Motivated by the law, not yet proven at the per-state level: test by
adding a budget proxy to the `POLY_UNIT_LOG` trace and correlating with `cpu_s`.

## Priority for a(22)/a(23)

1. Predict the full cost map (this model) → exact #32 split + per-column disk/RAM plan
   before launch (no probe run).
2. Work-stealing (designs/08, T2.3) on the peak columns — the ~18% lever, where the
   cost lives.
3. `--overlap-heights` peak↔tail pairing to fill the back half of every height.
4. Tail unit-capping (remove the over-partition tax) — cheap, do alongside.
The atomic H_max·col2 floor bounds all of it; intra-column distribution stays parked
for a real cluster (a24+).
