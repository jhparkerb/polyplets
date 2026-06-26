# Frontier idea oq1 — I7: one shared lock-free concurrent hash table (hot-slot contention)
*Source: docs/scheduling-design.md §"Open empirical questions" #1, §"Survivors" (I7). Related: cpp/tma/sweep8.h (sweepSquare8HeightMT, the batched-merge engine it replaces), cpp/tma/statedb.h (FlatDB::slot find-or-insert), docs/frontier/02-out-of-core-spill.md, results/crt-counter-shaping.md.*

## Idea
Replace the per-shard **batched merge** (`loc[t][s]` private scratch → `nextDB[s]`,
sweep8.h) with **one shared next-column table** that all threads insert into directly:
atomic-CAS claim of an empty slot for a new signature, then atomic/fine-locked
accumulate of the counts row. Attacks the **RAM cliff**: the batched engine holds
`dbS + nextDB + loc_batch ≈ 2×` the column; a single shared table holds **one copy**,
which is exactly what the §"Strategic staging" table says makes a(23) RAM-resident.

## Why it might matter here
The pole-RAM table (scheduling-design): a(23) pole ≈ 1.7×10⁸ states, lean (1-copy)
≈ **96 GB fits dalby (122 GB)**, batched ~2× → **~150 GB → OOM**. There is no other
owned box for a(23). So this is not a speed tweak — it is the gate on whether a(23)
runs single-box at all. **Highest-stakes idea in the set.** The risk it trades for the
1-copy RAM: the batched merge is contention-free by construction (one writer per
`nextDB[s]`); a shared table reintroduces contention on the **hottest output sigs**
(low-comps boundaries that many sources fan into), and a mutex version already capped
this DP at ~2.3× and regressed past ~12 threads (sweep8.h comment, runs/exact_mt_scaling).

## Kill-test — quickest path to INFEASIBLE
**Question it answers:** does atomic accumulate on the hottest output states serialize
throughput by more than the 1-copy RAM win is worth — i.e. does contention, not
bandwidth, set the wall?
**Setup:** prototype a `ConcDB` (open-addressing like FlatDB, `cap` power-of-two): slot
claim = `CAS(used[h], 0→1)` then write key; row accumulate = per-count
`atomic<u64>::fetch_add` (or a per-slot spinlock around the row). Wire it as a third
expand mode in sweepSquare8HeightMT — threads route directly into `ConcDB` instead of
`loc[t][s]`, no merge pass. Run **ONE heavy column** of an existing a(21) pole height
(H=20, the column at peak `res.peakStates`) on dalby at full T. Instrument: count
CAS-retry iterations per insert and `fetch_add` attempts per hot slot; sample
cycles-stalled with `perf stat -e ... ` (x86 ayr) / `perf c2c` for false-sharing.
Cost: ~1 day to write ConcDB + one heavy-column run. **Single column, not a full sweep.**
**Measure:** throughput (states-expanded/s) of the shared-table column vs the same
column under the batched merge, AND the CAS-retry / fetch_add-contention rate on the
top-1% hottest slots.
**NO-GO if:** shared-table column throughput < ~0.5× the batched-merge column (hot-slot
contention serializes by >~2×) — decisive because the whole point of I7 is to keep the
lock-free engine's *scaling* while gaining the mutex version's *RAM*; if it can't hold
scaling, the batched merge stays and a(23) needs a different RAM story (compression /
out-of-core, idea #2).

## Substantial-improvement ladder (must clear ALL)
- **C1 — parallel efficiency ≥ ~0.7 at the pole** — measured states/s at full T vs T=1
  on the heavy column; the batched engine's current scaling is the bar to match.
- **C2 — peak RAM ≈ 1× the column (no per-thread duplication)** — measured RSS
  high-water on the heavy column ≤ ~1.1× `nextDB`-size; this is what lands a(23) inside
  dalby's ~96 GB budget (vs ~150 GB batched).
- **C3 — byte-identical to the dense baseline** — full small-N sweep through ConcDB ==
  the serial `sweepSquare8Height` output, exact (gate case M). Hard project invariant;
  atomic accumulate must not drop or double a single count.
*Per-idea bar:* makes a(23) **single-box RAM-resident** (~96 GB on dalby) **with
near-linear scaling** — both, or it's not worth displacing the proven batched merge.

## Composition / foreclosures
Replaces the batched merge in sweepSquare8HeightMT outright (not additive). Shares the
RAM-cliff target with #2 (out-of-core) and state compression (#1) — but I7 is the
*cheapest* path to a(23) (no access-pattern rewrite), so it should be tried FIRST; only
if it fails does a(23) fall back to those. Composes cleanly with adaptive per-column
config (04-adaptive-per-column-config.md): a 1-copy table changes the per-column RAM
curve the schedule keys on. Orthogonal to the counter-width work (modp/u128).

## If it passes: effort & where it lands
**M (ESTIMATE)** — ConcDB is a sibling of the existing FlatDB open-addressing store; the
hard part is the atomic accumulate + exact-equality gate, not new algorithm. Lands as
the I3+I7 intra-box engine in cpp/tma/sweep8.h (new expand path) gating ROADMAP a(23).
If it FAILS the kill-test: that result itself is high-value — it redirects a(23) RAM
onto compression / out-of-core and saves an epic build.
