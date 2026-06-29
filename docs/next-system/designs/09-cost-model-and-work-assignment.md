# 09 — a-priori cost model from the frontier profile, and how to assign work

> **Correction (2026-06-29, D1):** like 07, the work-assignment analysis here
> treats H=N as the dominant atomic job. H=N is the **closed-form** top strip
> (`contributeTopHeight`, A1) and carries zero compute. Drop it from the cost
> vector; the pole is **H=N−1** (~53% of computed work). See the correction box
> at the top of [07-height-scheduling.md](07-height-scheduling.md) for the
> re-derived shares. The makespan-floor numbers below predate this.

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
2. **Width-of-mass shrinks with height (empirical curve — mechanism OPEN).** Columns
   carrying real frontier *mass* (≥ 1% of peak) obey **active_width + H ≈ N + 6**
   (measured 26–27 across H = 8..20): taller strips concentrate their mass in fewer
   columns. This is a statement about where the *count mass* sits, **not** a width
   ceiling — the maximum width is always ~N for *every* height. A king-diagonal
   advances one row AND one column per cell, so n cells buy height n and width n at
   once (the 4×4 diagonal is height 4, width 4, n=4). ⚠ An earlier draft "explained"
   this by a cell budget ("≥H cells for height ⇒ ≤N−H for width"); the diagonal
   **refutes** that — cells do double duty. Why the bulk is narrower for tall H is
   **not yet derived**; use active_width+H≈N+6 as a fitted curve (good for sizing),
   not a mechanism.
3. **Peak grows ~geometrically, bending at the top (empirical).** peak_frontier(H)/
   peak(H−1) is ~2.6× through the mid heights, then **bends down** toward the pole:
   2.42 (H16) → 2.17 (H18) → 1.92 (H19) → **1.84 (H20)**. So the top heights are large
   but *less* dominant than a flat 2.4× would say. (Reason for the bend is the same
   open question as part 2 — it is a measured fact, not the refuted width-budget
   story.)

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

**RAM is the binding constraint, NOT free — measured.** The batch-overlap experiment
gained ~32% (≈52/80 eff cores) but was **spill/RAM-bounded**: 3× oversubscription
collapsed to 26 cores on a spill storm, and at a(21)+ scale spill dominates (overlap
*amplifies* it). The cliff buys RAM-safety only for the *cheap-tail + expensive-peak*
pairing; the top heights are **adjacent and both expensive**, so pipelining them
overlaps two long peaks → peak-with-peak working set → blowup. The governor must
actively cap concurrent peak RAM; staggering by the cliff helps at the margin, it does
not make overlap free.

**And aim it at the right idle.** The cliff-tail is cheap by construction, so
backfilling *it* recovers little wall. The idle worth filling is the **peak-column
straggler tails + the map→merge barrier** — that is the live 5–7% trough (ayr was
stuck in H20 *col2*'s straggler tail, a peak column, not the tail). The shared pool
fixes that too: when a peak column's stragglers leave cores idle, they pull the next
height's independent peak-column map instead of waiting. That is the real target —
bigger than "ramp as the cliff drops," and bounded by RAM, which is why it pairs with
the governor and (designs/08) work-stealing, not replaces them.

**5. New candidate lever — cost-aware partitioning (speculative, testable).** A state's
branching cost *may* rise with its remaining cell budget (more cells left ⇒ more viable
extensions) — a plausible per-state effect, standing on its own, NOT on the refuted
width law above. If per-state cost is estimable from a cheap proxy (lowest-n with
nonzero count, off the counts vector), partition units by predicted **cost** instead of
equal **count**, pre-balancing the units. Caveat from designs/08 Finding 5: the
heaviness is *concentrated* in a few states, so cost-aware cuts could balance *across*
units but still can't subdivide a single super-heavy state — it complements
work-stealing, it doesn't replace it. Unproven; test by adding a budget proxy to the
`POLY_UNIT_LOG` trace and correlating with `cpu_s`.

## Priority for a(22)/a(23)

1. Predict the full cost map (this model) → exact #32 split + per-column disk/RAM plan
   before launch (no probe run).
2. Work-stealing (designs/08, T2.3) on the peak columns — the ~18% lever, where the
   cost lives.
3. `--overlap-heights` peak↔tail pairing to fill the back half of every height.
4. Tail unit-capping (remove the over-partition tax) — cheap, do alongside.
The atomic H_max·col2 floor bounds all of it; intra-column distribution stays parked
for a real cluster (a24+).

> **Caveat (BUGS-OF-SHAME D5): `--overlap-heights` (lever 3) forfeits BOTH
> checkpointing and work-stealing — don't recommend it for a multi-day record
> run unmodified.** `runOverlap` uses `noopCkpt` (no mid-run checkpoint: a crash
> re-runs every in-flight height from scratch), and stealing is gated
> `OverlapHeights<=1` (so lever 3 disables lever 2). "On failure re-run" violates
> the bounded-loss NFR for an a(22)/a(23) run measured in days. Before overlap is
> a real throughput lever it needs resumable in-flight heights (deferred) or must
> be confined to short heights whose re-run cost is acceptable. Also note lever 2
> here is "~18%" because it is *map-phase-internal only*, post the seek-index
> merge fix (06) — see the D3 note on assembling the combined post-fix budget.
