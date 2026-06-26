# Frontier idea 02 — Out-of-core / spill to disk
*Source: docs/scheduling-design.md §"Unexplored axes" #2 (= ROADMAP #20, dropped off critical path). Related: docs/frontier/03-sort-transition-engine.md, docs/frontier/05-elastic-cloud-resources.md, results/reach_projection.md, docs/state-store-compression.md.*

## Idea
Stop assuming the pole column's frontier hash table fits RAM; spill it to local
NVMe and let the OS / an mmap'd open-addressing map page it in and out. Attacks
the **RAM cliff** directly — the a(24) pole needs ~232 GB, fits no owned box.
The naive form keeps the current engine's access pattern (random find-or-insert)
and just moves the table to disk.

## Why it might matter here
The binding constraint is RAM at the pole (scheduling-design §"Strategic
staging"): a(24)~232 GB > dalby 122 GB. If RAW spill worked, the cliff would
just vanish — backend swap, no engine rewrite. So it is worth one decisive
arithmetic check before any build, precisely because the payoff is so large.

## Kill-test — quickest path to INFEASIBLE
**Question it answers:** does the pole column's random find-or-insert pattern
survive being backed by NVMe, or does seek latency blow the wall up by >10×?
**Setup:** back-of-envelope, no build. Inputs all measured/projected:
a(23) pole ≈ 1.7×10⁸ states (scheduling-design table); ~N≈23 columns each doing
~(pole-state) find-or-insert ops; a working set that exceeds RAM so a constant
fraction of ops are cold (random 4 KB page faults). NVMe random-read budget:
~10⁵ (consumer) to ~10⁶ (enterprise, deep queue) 4 KB IOPS.
**Measure:** projected wall = (cold ops) / (random IOPS), vs the in-RAM pole wall.
**Arithmetic (a(23), pessimistic — every op cold):**
  total random ops ≈ 23 cols × 1.7×10⁸ ≈ 3.9×10⁹ ops.
  at 10⁵ IOPS → 3.9×10⁴ s ≈ **11 h** of pure I/O stall;
  at 10⁶ IOPS → 3.9×10³ s ≈ **1.1 h**.
  For a(24) (4.0×10⁸ pole, 24 cols → 9.6×10⁹ ops): **27 h** @10⁵, **2.7 h** @10⁶.
  The in-RAM pole is memory-bandwidth bound at ~2.6 base/height; a(22) pole
  (~40 GB, RAM-resident) runs in the hours-to-low-days range. Even a *modest*
  cold fraction f puts NVMe I/O stall at f × (11–27 h) **on top of** compute, and
  at f→1 it is the dominant term.
**NO-GO if:** projected I/O wall > ~10× the in-RAM pole wall — i.e. whenever the
cold fraction f isn't pushed near zero. The arithmetic above shows raw random
spill is squarely in that regime at consumer IOPS and only marginal at
enterprise IOPS *with* a forgiving cold fraction. The threshold is decisive
because a 10× wall on a multi-day pole is the difference between a job that
finishes and one that never does.

**Headline finding — RAW spill collapses into idea #3.** The only way to dodge
the random-IOPS wall is to stop issuing random ops: batch/sort the find-or-inserts
so disk traffic is **sequential mergesort streaming** (~GB/s, IOPS-irrelevant),
not random 4 KB seeks. That restructure *is* docs/frontier/03-sort-transition-engine.md.
So out-of-core is not an independent bet — it is a **deployment backend** that
only becomes viable *after* #3 lands (scheduling-design §"One bet, not four").

## Substantial-improvement ladder (must clear ALL to be worth building)
- **C1 — cold-op fraction → near-zero** — only achievable by batching access
  (i.e. via #3); without it C1 fails outright at the kill-test.
- **C2 — sequential disk bandwidth ≥ a few GB/s sustained** — measured by an
  `fio` seq-read run on the target NVMe; sets whether streaming pays at all.
- **C3 — spill wall ≤ ~2× the in-RAM pole wall at a(23)** — measured on the
  a(23) testbed once #3's stream engine exists.
*Per-idea bar:* substantial = a(24) pole completes on an owned box (dalby) that
cannot hold it in RAM, within ~2× the wall a 232 GB box would take.

## Composition / foreclosures
Shares the "one bet" with #3 (sort engine), #5 (cloud KV), M5 (distributed
single-height). It **forecloses nothing** and **leads nothing**: it cannot be
built before #3 (the kill-test proves RAW spill dead). Ordering: #3 first, then
this is a backend choice (local NVMe) alongside cloud KV / sharded RAM.

## If it passes: effort & where it lands
**S (ESTIMATE)** *given #3 already exists* — wiring a sorted-run spill directory
into the stream engine is a backend, not an algorithm. **XL** if attempted
standalone (it can't be — dead at kill-test). Lands at ROADMAP #20; engine:
the sort/stream successor to cpp/tma_main.cpp (see build/tma_ooc_test as the
existing OOC scaffold).
