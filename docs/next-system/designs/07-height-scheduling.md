# 07 — cross-machine height scheduling for a(22)+ (ROADMAP #32)

How to split a multi-height run across two unequal boxes (ayr 32c, dalby 80c) to
minimize wall time. Supersedes the "meet-in-the-middle" sketch in ROADMAP #32,
which the simulation below shows is the *worst* dynamic option (up to 47% over
ideal). Calculator: `scripts/heightsplit_plan.py`.

## The cost structure decides everything

The fold engine computes each bounding-box height H as an **independent** sweep,
so heights distribute across boxes with no coordination. Four facts constrain the
split:

1. **Cost is geometric in height, ~r^H with r ≈ 2.0–2.4** (measured per-height
   wall ~doubles h17→h19; forecast cost ratio ~2.4). The work is grotesquely
   top-heavy: the **top two heights are ~80%** of the run (H=N ≈ 50–58%, H=N−1 ≈
   24%, H=N−2 ≈ 10%, tail negligible).
2. **A single height is atomic across machines** (see "why" below). You assign
   *whole heights*; you cannot split one height between boxes economically here.
3. **Columns within a height are strictly sequential** — column c+1's frontier is
   produced from column c. So there is no "odd/even **columns**" scheme: there is
   no column-level independence to exploit. (Odd/even **heights** is fine and is
   evaluated below — heights *are* independent.)
4. **The boxes are unequal and the effective ratio is uncertain and
   height-dependent.** Measured this session: ayr ≈25.5 eff cores / 30 (85%, fixed
   engine), dalby ≈44.5 / 80 (56%, *unfixed* engine, merge-bound) → ratio ≈1.75
   now; the a22-forecast assumed ~2.5; the seek-index merge fix (`06`) will raise
   dalby. dalby's 80c suffer *more* merge under-utilization on the expensive tall
   heights than ayr's 30c. **The throughput ratio is a moving target.**

This makes the problem **Q2‖Cmax** (makespan on two uniform-but-unequal machines)
with a job set where two atomic jobs are 80% of the load. The binding constraint
is the **atomicity of H=N** (~55%): whichever box gets it is committed, so it must
be the fast box, and every other height exists only to fine-balance around it.

## Why a height is atomic across machines (the per-column shuffle)

The data *can* flow between machines — a column's map-merge output is just a
sorted frontier you can ship anywhere. It buys nothing *within one height*:

- **Pipelining columns is a relay race.** If box A computes column c and hands the
  frontier to box B for column c+1, B was idle waiting for A and now A idles
  waiting for B. Only one box ever works on that height at a time; you've added
  network latency for zero concurrency. A dependent chain doesn't parallelize by
  spreading its links.
- **Getting both boxes onto one height at once needs a key-range split + a
  per-column shuffle.** Partition the frontier by signature key (A takes `[0,mid)`,
  B takes `[mid,hi)`); each maps its slice. But the column transition **moves
  states between key-ranges** — a state A computed can belong in B's range after
  the step — so every column needs an all-to-all **shuffle** of multi-GB frontiers
  between boxes. With no shared FS and no fast interconnect, ~20 shuffles/height
  costs far more than it saves at 2-box scale.

So within-height cross-machine work is *uneconomical here, not impossible*. It is
the "true distribution" path, parked for a(24)+ on a real cluster (§ floor below).
The free parallelism is across **whole independent heights** — what this doc
schedules.

## The schemes, by simulated makespan

`heightsplit_plan.py` evaluates each scheme by Cmax vs the perfectly-divisible
ideal, swept over the two uncertain axes (r ∈ {2.0, 2.4}, throughput ∈
{measured-1.75, forecast-2.53}) for N = 22 and 23. Penalty ranges across all 8
regimes:

| scheme | type | penalty | verdict |
|---|---|---:|---|
| **LPT static** (largest height → box that finishes it soonest) | static | **0.0–0.8%** | near-optimal everywhere |
| **dynamic pull** (pole pinned to fast box; each box pulls largest-unclaimed when idle = online LPT) | dynamic | **0.1–2.9%** | near-optimal everywhere |
| odd/even heights (fast box gets N, N−2, …) | static | 3.9–17.8% | good only when r ≈ capacity ratio |
| contiguous split (#6 today: ayr H1..k, dalby k+1..N) | static | 4.6–18.0% | always mediocre |
| meet-in-the-middle (ROADMAP #32 sketch) | dynamic | 4.6–**47.2%** | catastrophic when dalby fast + pole dominates |
| odd/even **columns** | — | — | invalid (columns sequential, fact 3) |

Findings:

- **The two adaptive schemes never lose** (<3% in every regime). Everything else
  has a regime where it is 15–47% off.
- **Odd/even's quality is luck.** Its split ratio is fixed at *r*; it is ~4% when
  that matches the real capacity ratio and ~18% when it does not. (LPT/dynamic
  adapt to the actual ratio, occasionally giving the fast box two heights in a row
  to correct.)
- **Meet-in-the-middle is the worst, and worst where it matters** — 47% in the
  forecast case (fast dalby, r=2.4): ayr rips through the cheap low heights and
  then *grabs H=N−1* (the 2nd-biggest) while dalby sits idle after H=N. The
  "self-balancing" intuition assumes smooth cost; with two jobs = 80%, the
  hand-off granularity at the top is far too coarse. **#32's recommendation is
  retired.**
- **The calculator cannot separate the top two** — LPT-static and dynamic-pull are
  ~tied in these clean sims. Their real difference is robustness to what the sim
  does *not* model: throughput drift mid-run, a box pausing/resuming, per-height
  efficiency departing from the flat model. That is precisely what a live run, not
  a calculator, reveals.

## The three to test

1. **Dynamic pull** — the practical pick; near-optimal *and* the only one whose
   advantage shows under real-world mess (drift, resume, efficiency variation).
   Minimal coordination: a shared claim of "next-largest unclaimed height," with
   the single largest pinned to the fast box so a slow box can't grab it.
2. **LPT static** — the optimum yardstick and the zero-runtime-coordination option
   (whole assignment computed up front). Best when the cost + throughput estimates
   are trusted.
3. **Odd/even heights** — the zero-knowledge, no-cost-model fallback, **with its
   documented failure mode** (ratio mismatch → up to ~18%).

Drop contiguous (#6's current behavior) and meet-in-the-middle; odd/even-columns
is impossible.

## The floor, and the one lever past it

Every height-level scheme is capped at ~throughput-proportional makespan because
H=N is atomic (~55%). The only way under that floor is to split the top height
itself across boxes via key-range frontier partition + per-column shuffle — real
distribution, needing a shared FS / fast interconnect the 2-box setup lacks. Park
it for a(24)+ on a cluster; it is out of v1 scope (PRD §10).

## Using the calculator

```
scripts/heightsplit_plan.py                       # geometric sweep (default)
scripts/heightsplit_plan.py --N 22 --r 2.4 --sa 30 --sb 76
scripts/heightsplit_plan.py --costs perheight.tsv # measured: "H cpu_seconds" per line
```

The two real unknowns are **r and the throughput ratio**, both nailed down for
free when the a(20)/a(21) `--per-height-out` land: feed the measured per-height
cpu-seconds via `--costs` and the ranking re-computes on real numbers (and the
merge fix will have moved dalby's effective cores off the 1.75 measurement toward
the forecast). The `dalby gets {...}` column of each scheme is the runnable
height-split it produces.

Apply when a(22) is launched (M4). Until then this is paper only — no compute, no
engine change.
