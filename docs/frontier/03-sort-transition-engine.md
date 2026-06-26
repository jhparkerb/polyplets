# Frontier idea 03 — Sort-based transition engine
*Source: docs/scheduling-design.md §"Unexplored axes" #3. Related: docs/frontier/02-out-of-core-spill.md, docs/frontier/05-elastic-cloud-resources.md, scheduling-design §"One bet, not four" / §Survivors (M5), results/reach_projection.md.*

## Idea
Represent a column's frontier as a **sorted stream of (signature, counts)** records
and perform the column transition by **sort + merge** instead of random
find-or-insert into a hash table. Mergesort is external-memory-native (sequential
GB/s, IOPS-irrelevant), contention-free (no hot-slot atomics), and distributes
cleanly (range-partition the keyspace across boxes). This is the **load-bearing
idea of the whole "one bet"** — #2 (disk-spill), #5 (cloud KV), and M5
(distributed single-height) all reduce to *having this access pattern*.

## Why it might matter here
Every path past the a(24) RAM cliff (scheduling-design §"One bet, not four")
requires restructuring random ops into batched/sequential ones; per-state random
ops over disk OR network are equally fatal (#2 kill-test, #5 prong-a). The sort
engine **is** that restructure. It also de-risks the I7 hot-slot contention
question (scheduling-design §"Open empirical questions" #1) by eliminating shared
mutable slots entirely. Nothing else unlocks M5 or a(24)+.

## Kill-test — quickest path to INFEASIBLE
**Question it answers:** is one column transition done as in-memory sort+merge
within striking distance (≤~3–4×) of the existing hash engine's states/sec, AND
is connectivity-closure expressible under sort+merge without random mid-merge
lookups?
**Setup:** prototype ONE column transition as sort+merge, **in-memory**, at small
n (n=14–16 — frontier fits L3/RAM trivially, no I/O noise). Drive it from the
same input column the existing hash engine (build/tma) processes; emit the same
output column; on gympie, single-threaded, so the comparison is pure
access-pattern. Cost: a few hundred lines + an afternoon, no production risk.
**Measure:** (1) states/sec of sort+merge vs build/tma on the identical column;
(2) whether the boundary-partition merge at the seam (connectivity-closure) can be
done by **co-sorting on the partition key and merging**, or whether it demands a
random lookup *mid-merge*.
**NO-GO if (gate 1):** in-memory sort+merge is **>~3–4× slower** than hashing —
because external memory, even *free*, only repays a slowdown if the streaming win
covers it; a 4× compute penalty means the disk/network version starts already
underwater vs the in-RAM hash engine, and there is no win left to bank.
**NO-GO if (gate 2):** connectivity-closure needs a random find mid-merge — then
the contention-free / distributes-cleanly claim is false (you've reintroduced the
random op the whole bet exists to remove), and #2/#5/M5 all stay blocked.
*Back-of-envelope on why ~3× is the line:* sort is Θ(m log m) vs hash Θ(m); at a
pole frontier of m≈1.7×10⁸, log₂m≈27.4. A good radix/comparison sort on packed
fixed-width keys recovers most of that constant; if the prototype lands inside 3×,
the log factor is being amortized and external streaming (~GB/s seq vs ~10⁵ random
IOPS, a 10–100× I/O win) repays it many times over. >4× means the constant isn't
being recovered and the model breaks.

## Substantial-improvement ladder (must clear ALL to be worth building)
- **C1 — in-memory states/sec within ~2× of build/tma** at n=14–16 — measured
  head-to-head on the identical column (tighter than the kill-test's 3–4× floor).
- **C2 — external-memory streaming holds within ~2× more** (≤~4× total vs in-RAM
  hash) at the a(23) pole — measured on the a(23) testbed with sorted runs spilled
  to NVMe; this is the bit #2 depends on.
- **C3 — range-partition distributes across boxes** with linear-ish speedup and
  bounded cross-box traffic — measured by splitting the a(23) pole keyspace across
  ayr+dalby; this is what unlocks M5 and the a(24) cliff.
*Per-idea bar:* substantial = the a(24) pole (232 GB, no single box) becomes
*reachable at all* — via spill (#2) or sharding (M5) — at a wall the project will
sit through. Below C1 it isn't worth starting; below C3 it doesn't reach a(24).

## Composition / foreclosures
This is the trunk of the "one bet"; #2 and #5 are leaves that **cannot be built
until this passes**. It composes with state compression (§"Unexplored axes" #1,
docs/state-store-compression.md) — sorted fixed-width records compress well — and
with the cost model. It does NOT conflict with the work-unit queue (it changes the
leaf operation, not the scheduling). Ordering: **build/prototype this FIRST**;
everything downstream waits on its two gates.

## If it passes: effort & where it lands
Kill-test prototype: **S (ESTIMATE)**. Production in-memory engine (C1): **M**.
External-streaming + spill (C2): **L**. Distributed range-partition (C3): **XL**.
Lands at ROADMAP #20 (recast as the sort/stream restructure); new engine
alongside cpp/tma_main.cpp; trialled on the a(23) testbed (scheduling-design
§"Strategic staging" — "prove the sort/stream engine on a job that still fits").
