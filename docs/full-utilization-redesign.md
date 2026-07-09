# Full-utilization redesign — distilled findings and best-in-breed designs (2026-07-09)

**Status: design settled by measurement. Nothing implemented, not
approved.** Phase 1 (radical simplification) has not started. This is
Phase 2 design work.

## MEASURED VERDICT (2026-07-09, both Part-3 tests run on dalby)

The two decisive tests the plan named were built and run on real dalby
(80-core Neoverse-N1). Both design forks are now closed by evidence, not
argument:

- **γ (clean-slate in-process substrate rewrite): DEAD.** The tmpfs test
  (identical H15/maxn30 sweep, run-files on disk vs `/dev/shm`) measured
  **disk 204s vs tmpfs 190-193s — file-I/O is only ~7% of wall.** If I/O
  were the disease, RAM-backing the files would slash the wall; it trims
  7%. Confirms the forensic split (idle is ~45% stragglers + ~55%
  per-round serialization, near-zero I/O). γ's rewrite would recover ~7%
  for an enormous correctness-re-establishment risk. Not worth it.

- **ρ (radix hash-aggregation) vs α (parallel sort-merge): α WINS.** A
  real 80-core micro-benchmark (`experiments/reduce_bench.cpp`) on ~16M
  emitted records built by the REAL `kinkStageTransition`/`canonMixed`,
  outputs verified byte-identical, swept over stage∈{1,5,9,12,16} and
  over-partition f∈{4,16,32,64,128}: **ρ's speedup vs α ranged 0.83-1.05x,
  median ~0.91 — ρ never decisively wins, ties α at best (f=16), and α is
  consistently faster and more stable (~3.45s vs ρ's 3.6-4.2s).** The
  DB-literature prediction that hash-agg beats sort-merge does NOT hold
  for THIS workload: short 22-byte keys (cheap memcmp-sort), low collision
  (fan-in ~1.16 — nearly a permutation, so hash-combine's advantage rarely
  fires), and a value-copy cost that C1 says is conserved and that
  dominates both. **This is exactly the outcome C1's "harshest critic"
  paragraph warned was possible; the measurement retired ρ.**

**THE ANSWER: Design α — bulk-synchronous within-column parallel map +
80-way key-range-partitioned parallel sort-merge reduce + in-flight
key-range straggler splitting + per-task count outputs (crash-proof
resume).** At wall-clock parity with ρ, α wins on engineering: it reuses
the battle-tested `sortRun`/`deduplicateRun`/`combine`; its natural
ascending-`lo` sorted order already hits `combine`'s optimized cheap path
(ρ needs the β-1 pre-extend workaround to avoid the left-extension
realloc); it integrates with the existing `SampleKeysMulti` partitioning
and stealing machinery; and it adds no new hash-table correctness surface.
The benchmark also confirms the architecture works: 16M records reduce in
~3.5s on 80 cores — genuine 80-way parallelism, i.e. the fat-column
13%→~90% utilization win is real and comes from parallelizing the reduce,
which the current single-threaded finalize does not do.

The rest of this document is the derivation that led here (kept because
the reasoning that killed B/C/D/δ/ρ and demoted γ is the actual content).
The bottom-line recommendation is α, above.

---

**Original status line:** design only, nothing implemented. This is Phase
2 design work, done first so Phase 1 can be scoped against a chosen
target.

**Where this landed after three adversarial rounds + a measured reframing
(eleven independent skeptical/forensic reviews total):**

The MEASURED headline (C8, from a real a34 run) reframed everything: **70%
of the whole run's wall is a single height, and its problem is ~13% util
in its FAT columns, not the thin tail.** Cross-height scheduling, the
Pincer cut, cross-column pipelining — every SCHEDULING trick — targets
<5% of wall and is a rounding error. The entire game is getting one
16M-record, 18-stage column from 13% to ~90% util, and forensics attribute
that 13% to **~45% stragglers + ~55% per-round serialization, both on the
current substrate, essentially zero I/O-wait** — squarely the domain of a
within-column parallel map+reduce with in-flight splitting.

**The architecture is therefore settled** (bulk-synchronous, within-column,
parallel map + parallel partitioned reduce, in-flight key-range straggler
splitting, per-task count outputs for crash-proof resume). The only open
question was the REDUCE PRIMITIVE, and a dedicated hunt resolved it:
**Design ρ — radix-partitioned private hash-aggregation** — strictly
dominates both earlier reduce candidates (α's parallel sort-merge and β's
shared concurrent table) and is grounded in the state-of-the-art database
group-by literature. **ρ is the primary candidate.** α (parallel
sort-merge) survives only as the conservative fallback; β is retired
(strictly cache-worse instance of ρ); **the one remaining micro-benchmark
is ρ-vs-α** (Part 3).

**γ** (clean-slate "throw out all the code" rewrite, as required) is
DEMOTED to build-only-if-one-cheap-measurement (a tmpfs I/O test) shows
the substrate matters — which the forensics say it almost certainly
doesn't; its one real contribution (a resume-bug fix) is harvested into ρ.
A fourth design **δ** (bidirectional column cut) was found and rejected as
economically dominated; the remaining decomposition axes were proven
closed (Part 4). Nothing here is committed until the ρ-vs-α benchmark runs
and you approve.

Round 1 attacked the earlier four candidates (A: dynamic source-shard
budget, B: state-space partitioning, C: tiled wavefront, D: in-process
engine); it killed B (termination detection collapses into the barrier it
claims to avoid) and C (its "local wavefront" dependency does not exist in
the code), and reframed A and D into the α/β/γ below. Round 2 attacked
those. Both rounds' findings are captured as hard constraints (Part 1) and
per-design outcomes (Part 2).

---

## Part 1 — what the adversarial reviews proved (the constraints every design must respect)

These are not opinions; each was traced to the actual code and is cited.

### C1. The computation is: (embarrassingly-parallel MAP) + (global all-to-all REDUCE), repeated H times per column.

Verified in `core/kink.h`. `kinkStageTransition` (line 98) reads ONLY a
single record's own signature bytes (`s.b[...]`), emits 0–2 successors,
and performs **zero cross-record reads**. So the per-record map at every
stage is embarrassingly parallel over ANY partition — this parallelism is
already free and is NOT where the difficulty is.

The difficulty is entirely in the REDUCE. `canonMixed` (line 59) relabels
a state's components by **order of first occurrence** — a global
relabeling with no relationship to the numeric order of the source key.
Two adjacent source keys can canonicalize to output keys anywhere in the
space; two far-apart source keys can collapse to the SAME output key.
This is confirmed both by the code and by the project's own prior memory
`merge-shuffle-ranking-locality`: "merge is all-to-all, conserved unless
partition-preserving... a LOCAL/banded one CANNOT [exist] (expansion)."

**Consequence:** No design can make the reduce local or avoid the
all-to-all data movement. Every viable design is a different way to *pay*
that reduce cost while keeping cores busy — not a way to remove it. This
killed Candidate C outright (it invented a Floyd-Warshall-style local
"wavefront" dependency that does not exist in the code).

### C2. Correct `ms`-pruning requires a canonical state's FULL window; a partial window can silently DROP a real contribution.

`kinkStageTransition`'s `occupy && ms+1 > maxn` check (line 102) fires at
EVERY stage, using the record's own `ms`. `core/kink_sharded.h`'s header
(lines 24–38) proves by hand-worked example that acting on a *partial*
window's `ms` silently drops a valid `occupy=1` branch — a lost
contribution to the final count, not a reconcilable duplicate. This is a
CORRECTNESS constraint, not a performance one.

Two ways to satisfy it, each with a cost:
- **Defer the prune** (`permissiveBudget=true`): safe, but more
  intermediate states survive to the merge → pruning-loss overhead that
  grows with how fragmented the window is. This is what current
  kink-sharded does.
- **Guarantee the full window before pruning**: requires knowing all
  contributions to a canonical state have arrived — which, without a
  barrier, is the distributed-termination problem that killed Candidate B
  (a worker cannot locally know another worker isn't still *computing* a
  contribution that hasn't been sent yet; the only sound guarantee is "all
  producers finished this stage" = a barrier).

**Consequence:** you either pay pruning-loss (defer) OR you pay a
per-stage barrier (to establish the full window cheaply). B tried to have
neither and secretly needed the barrier anyway.

### C3. A per-stage barrier is NOT inherently the enemy. Idle cores WITHIN a phase are.

The prior utilization work fixated on removing the H+1 barriers per
column. But a barrier only costs utilization if cores go idle waiting at
it. The measured real problem (`docs/utilization-bottleneck-log.md`
Bottlenecks #1, #8; H17 col3/col5) was the **straggler tail within a
phase** and an **under-parallelized merge**, not the barrier count. A
bulk-synchronous design with a barrier every stage can still hit ~100%
utilization IF every phase between barriers saturates all cores and the
last-straggler tail of each phase is stolen. This reframing is what makes
Design α below viable despite keeping barriers.

### C4. The one legitimate data dependency is column N+1 needing column N's finalized frontier. Everything else is fair to remove.

Owner-stated and consistent with the algorithm. Keep it. (A from-scratch
design MAY attempt to pipeline across it speculatively — see Design γ —
but must prove correctness if it does.)

### C5. Real frontiers are RGS-skewed; any static partition WILL have stragglers.

Frontier size varies 100x+ across a column's rounds (measured). Any
design that statically partitions work and cannot split a straggling
piece mid-flight will idle cores at every phase tail. **Mandatory for
every design: a running unit of work must be splittable while in flight.**
This is exactly the gap that disqualifies current kink-sharded (its
private shards are unstealable) and the reason the standard kernel needed
two dedicated stealing fixes.

### C6. Correctness is inviolate AND there is an existing unfixed resume bug.

`results/kink-resume-sigterm-bug.md`: real SIGTERM+resume overcounts,
root cause not yet identified, leading hypothesis is partial-`hTri`
double-fold at the checkpoint boundary. Any redesign that changes the
checkpoint model inherits this as a HARDER problem unless it fixes the
root cause first. A finer-grained/in-flight-splittable design (which C5
demands) makes "what is a consistent checkpoint" strictly harder. So:
**checkpoint consistency must be designed in from the start, not bolted
on** — and ideally the redesign's structure should make the existing bug
class impossible by construction.

### C7. The in-process-vs-file-boundary question (old Candidate D) is a REAL but SEPARATE and UNMEASURED axis.

Reviews confirmed: (a) the payoff is inferred, never measured — nobody
has isolated file-I/O's share of wall time on a real expensive column;
(b) `pgo-no-go-dalby` and `profile-rows-measured` suggest real columns
may be compute/dedup-bound, not I/O-bound, so the win could be modest;
(c) shared-memory threading trades away today's free structural
memory-safety (process isolation, fail-closed CRC'd run files) for a
silent-race risk class. **Ruling: the execution substrate (process+files
vs. in-process threads) is orthogonal to the decomposition question and
must be decided by MEASUREMENT, not folded into the decomposition design.
A cheap measurement gates it (see Part 3).**

### C8. THE MEASURED HEADLINE: the entire utilization problem is low util WITHIN THE FAT COLUMNS of the single dominant height. The "thin tail" and "cross-height scheduling" are both <5%-of-wall red herrings.

This is the most important finding in the document and it is measured, not
argued — from `results/ns_a34/cost_profile_dalby.tsv` (a real a34 frontier
run), verified 2026-07-09:

- **70.2% of the entire run's wall is a SINGLE height, H=18.** H=17 adds
  17.9%. The top two heights are 88% of wall; all of H3–H16 together are
  ~12%.
- **Within H=18, utilization is 12–16% in EVERY fat column, and the
  fattest columns are the WORST:** col 4 (15.4M records, 9,491 cpu-s) runs
  at **12.8%** util — ~10 of 80 cores busy — during the single most
  expensive column of the whole computation. The thin tail columns
  (col 19–34) are actually BETTER (24–30%).
- **Seven fat columns of this one height (H=18 cols 2–8) = 37.3% of the
  ENTIRE run's wall, at ~13% util.** At 90% util they would take 817s
  instead of 4963s — **saving ~4,150s = 31% of the whole run**, from seven
  columns.
- **The thin tail (H=18 cols 19–34) is 3.9% of H=18 ≈ 2.7% of the whole
  run.**

**What this proves and kills:**
1. **The "lone-final-height tail" framing (mine, and the prior
   investigation's) is WRONG.** The disease is not "not enough work to
   fill cores at the end." There is a MASSIVE surplus of work (col 4 has
   9,491 cpu-seconds; at 80 cores that's 119s of ideal wall, but it takes
   928s). The work is there; the engine extracts ~1/8 of it. The problem
   is the FAT middle, not the thin tail.
2. **Cross-height pipelining (γ's headline win) is a proved MIRAGE — and
   for a deeper reason than the earlier review gave.** Not just "no other
   height's work is left during the tail" — rather, 70% of wall is ONE
   height whose OWN fat columns are the bottleneck, so no amount of
   cross-height or tail scheduling can touch the dominant cost. Even a
   perfect scheduler filling every cross-height bubble leaves the 31%
   fat-column deficit untouched. Mirage: PROVED by arithmetic.
3. **δ (Pincer), ε (cross-column pipelining), deferred-backfill, and every
   other SCHEDULING trick target the tail — collectively <5% of wall.**
   They are rounding-error optimizations. The tail is already at higher
   util than the fat middle.
4. **The whole game is: get a 16M-record, 18-stage single column from 13%
   util to ~90%.** That is EXACTLY and ONLY what α and β do (parallelize
   the map AND the reduce WITHIN a column). This measurement is the
   strongest possible evidence that α/β target the real bottleneck and
   that the scheduling-centric designs (γ/δ/ε) do not.

**Root cause of the 13%, decomposed from real per-round data
(`results/steal-tail-h18.md`, the same H18 col4 one term down, 20
barriered rounds):**
- **~45% stragglers.** `stage10..stage17` show map_cpu roughly constant
  (~350 cpu-s) while map_wall doubles (25s→52s) — 318s of map wall on 36s
  of real work (9 of 80 cores). Traced to code: `stealEligible`
  (`sweep.go:914`) gates on record-remainder `rem > grainRecs`, so
  compute-heavy-FEW-record units (the open-ended `SampleKeysMulti` last
  bucket — the "590M records vs 64K estimate" unit) never reach the
  wall-time steal ranker. These are exactly the units α/β must be able to
  split by KEY sub-range regardless of record count.
- **~55% serialization / fixed per-round overhead.** 19 short merge
  phases that can't fill 80 cores + the barrier between all 20 rounds +
  dispatch. Merge ranges are already well-balanced (Bottleneck #2), so
  this is constant per-round overhead × H rounds and under-filled merge
  phases — NOT stragglers, NOT I/O. Pure "the reduce isn't 80-way
  parallel and every round pays a barrier" — exactly α/β's target.
- **I/O-wait: small, single-digit %, but never directly isolated.**
  Estimated tiny (bandwidth ~75 MB/s aggregate; 6.4GB RSS + prior outputs
  fit dalby's 122GB page cache so file reads stream from RAM; the idle
  signature is straggler-shaped not I/O-shaped). But C7's honest caveat
  stands: never measured directly.
- **GC/alloc: negligible** (already fixed — GOGC=1000, readIndexHeader).

**Verdict: ~45% stragglers + ~55% serialization, both on the current
process+file substrate, both squarely in α/β's domain (parallel reduce +
in-flight key-range splitting). γ's in-process rewrite is justified ONLY
if I/O-wait is large, and nothing measured says it is.** This substantially
collapses γ further.

**The one cheap measurement that makes it airtight** (the profile's
wall−cpu gap alone can't separate straggler-idle from I/O-block): run ONE
isolated H18 column with the run-file dir on **tmpfs (`/dev/shm`)** vs.
disk on dalby — a few GB/round, no code change. Wall unchanged → I/O
near-zero → α/β decisive, γ dead. Wall drops sharply → γ's substrate
change warranted. This replaces the more expensive instrumented
compute/IO/dispatch split as Part-3 measurement #1.

---

## Part 2 — the designs, after a full adversarial round

All respect C1–C8 and were each subjected to a dedicated adversarial
review (2026-07-09); outcomes are folded into each section. **Bottom line:
the within-column parallel map+reduce ARCHITECTURE is settled (C8 proved it
is the only thing that touches the dominant cost). The reduce PRIMITIVE
resolved to Design ρ (radix-partitioned private hash-aggregation), which
strictly dominates the two earlier reduce candidates — α (parallel
sort-merge, now the conservative fallback) and β (shared concurrent table,
RETIRED as a strictly cache-worse instance of ρ). γ is demoted to
conditional-on-the-tmpfs-test; δ found and rejected (Part 4).** Sections
below are kept in derivation order (α → β → ρ → γ → δ) because the
reasoning that retires β and demotes γ is the actual content — but the
live choice is ρ-vs-α, one micro-benchmark (Part 3), and ρ is favored.

### Design α — Bulk-synchronous partitioned-shuffle (keep stages+barriers, make EVERY phase 80-way parallel with in-phase stealing)

**Core idea:** stop trying to remove the per-stage barrier (C3 says it's
not the enemy). Instead, within each stage, run a classic MapReduce
partitioned shuffle:
1. Partition the OUTPUT (canonical) key space into P ≥ cores buckets by a
   hash/range of the canonical sig.
2. All cores run the per-record map in parallel (C1: free), scattering
   each emitted successor into its output bucket's buffer.
3. Barrier.
4. All cores each own a disjoint set of output buckets and reduce them in
   parallel (sort+combine, or hash-combine, within a bucket) — an
   80-way-parallel merge, not the current single-threaded finalize.
5. Because each bucket owner sees EVERY contribution to its canonical
   states (the shuffle routed them all there) before it reduces, the
   FULL window is present → `ms`-pruning is exact, **no `permissiveBudget`
   relaxation, no pruning-loss** (satisfies C2 via the barrier, not via
   deferral).

**Why it's different from everything prior:** current kink and Candidate
A both have an under-parallelized reduce (A's is a single per-column
finalize call, `NMergeRanges: 1`). α makes the reduce the *same* 80-way
parallel shape as the map. The barrier stays but no phase idles cores:
map is trivially stealable (per-record), and a hot output bucket is
sub-partitioned and its sub-ranges stolen (satisfies C5).

**Adversarial review outcome (2026-07-09): SURVIVES, strengthened by two
mandatory amendments now folded in.**

- **Amendment α-1 (splittable unit — fixes a real spec bug).** The
  original spec said a hot bucket can only split on WHOLE-canonical-key
  boundaries, which makes a single ultra-hot key an UNSPLITTABLE
  straggler — and the skew to make that real exists (a measured H17 unit
  saw 590M records against a 64K estimate). The fix is in the physics and
  the original spec missed it: the reduce step PRUNES NOTHING —
  `combine()` (run.h:67) is associative and commutative (range-union +
  pointwise add), and the `ms`-prune fires later, at the NEXT stage's map,
  off the input record's own `minSize` (kink.h:102, run.h:124). So a hot
  key's contributions CAN be tree-reduced across k reducers into k
  partials plus one O(k) fix-up combine, full window intact before any
  prune reads it — C2 holds. The splittable unit is "partial-combines of a
  key," NOT "whole keys." With this, α has no unsplittable straggler even
  under the measured skew. Without it, α fails C5 — load-bearing.
- **Amendment α-2 (soft reduce→next-map barrier — a free win).** The
  map→reduce barrier within a stage is HARD (a bucket's reduce needs all
  of that stage's mappers done — all-to-all, C1). But the reduce→next-map
  barrier is SOFT: stage-(r+1)'s map of a record needs only THAT record
  fully combined, so bucket b's stage-(r+1) map can start the instant
  bucket b's reduce finishes, overlapping other buckets' still-running
  reduces. Halves the per-superstep synchronization exposure. Column
  boundary stays hard (C4).
- **Claim correction:** α is NOT less total work than the current merge —
  C1 says the all-to-all data movement is conserved. α's real, sufficient
  wins are (a) the reduce becomes 80-way parallel instead of the current
  effectively-serial finalize, and (b) `permissiveBudget=false` everywhere
  (exact ms with a full window per stage, `KinkStageCfg` comment
  kink.h:162-167), so kink-sharded's pruning-loss volume vanishes.

**Barrier-tail cost — MEASURED, not guessed:** a real frontier height
(H17, maxn=33) has ~17 stages × ~30 columns ≈ 500 supersteps; all heights
sum to order 5-10k supersteps. Per-barrier round-trip is bounded at 6-30ms
(`results/kink-carry-optionA-barrier-overhead.md`) → ~2-3 minutes total
against multi-hour peak columns. Negligible, cheaper still in-process.

**Cost profile:** low novelty (textbook parallel MapReduce), moderate
implementation, no new correctness class. The safe evolution.

### Design β — Concurrent hash-aggregation (replace sort-merge-dedup with a sharded per-shard-mutex hash table; the reduce becomes incremental)

**Core idea:** the reduce cost in C1 is unavoidable, but it does NOT have
to be a *sort*. Replace the sort-then-dedup merge with a **sharded
concurrent hash table** keyed by canonical sig, where the value is the
ranged count-vec. Every core, as it maps source records, inserts each
emitted successor directly into the table; on key collision it COMBINES
counts in place (exactly `RunRecord::combine`), under a **per-shard
mutex** (see amendment β-3 — the earlier "or lock-free" option is struck).
There is no separate merge phase and no sort — dedup happens
incrementally, at insertion time, concurrently.

**How it satisfies C2:** a stage is still bulk-synchronous — all cores
finish inserting for stage r before any core reads the table for stage
r+1 (one barrier per stage, same as α). At that barrier the table holds
each canonical state's FULL combined window, so the stage-boundary
`ms`-prune is exact. No pruning-loss, no `permissiveBudget`.

**Why it's substantially different from α:** α keeps sort-based merging
and pays a scatter+barrier+sort per stage. β eliminates sorting entirely
and folds the reduce INTO the map (produce-and-insert), so the only
per-stage synchronization is the single "all inserts done" barrier — no
separate scatter phase, no separate reduce phase, so the two-sync-points
tail α worries about collapses to one. The bet is that concurrent
hash-combine throughput at 80 cores beats scatter+parallel-sort.

**Adversarial review outcome (2026-07-09): SURVIVES its supposed killer
(RAM) with real numbers; two mandatory amendments folded in.**

- **RAM ceiling — NOT the disqualifier I flagged. Real numbers (this
  replaces the earlier "possibly deciding tradeoff" hand-wave):** the
  scary figures I had in mind (627M records, 126GB spill peaks, ns_a21's
  ~80GB) are all the OLD whole-column kernel, whose per-column volume is
  Σ-masks. The kink kernel deleted that: per-stage volume is ~frontier-
  sized, measured at a flat 3.6× the column frontier across H=4-14
  (`results/kink-carry.md`). Real frontier scale (`results/ns_a34/
  cost_profile_dalby.tsv`): top REAL height is pinned at H18 by the P_k
  closed-form treadmill, frontier ~16.5M records and nearly flat a31→a34.
  So β's resident table ≈ 3.6 × 16.5M ≈ 60M entries × ~450 B ≈ **25-30GB
  against dalby's 125GB**. a35-36 lifts the top height to H19-20 →
  ~50-60GB, still fits. The RAM wall (~H22, ~375GB) roughly COINCIDES with
  the compute wall (H22 is ~6.7× the compute of H20), so α's spill
  advantage buys little exactly where β's ceiling bites. β is not
  RAM-disqualified for the terms this redesign targets.
- **Hash contention — NOT a real serialization point.** The 590M-vs-64K
  skew is KEY-RANGE skew in a merge unit, which hashing destroys; kink
  fan-out is 2, so mean fan-in per output key is ~1-2, and no data in
  results/ shows single-key concentration remotely near the ~10% of a
  stage's inserts one key would need to serialize 80 cores. Shard into
  ≫cores partitions, per-shard mutex, done.
- **Amendment β-1 (fix the combine left-extension regression —
  mandatory).** `combine()`'s cheap grow-in-place path requires incoming
  `lo >= accumulator lo`; the sorted path GUARANTEES that via the
  `recordLess` lo-tiebreak (the Bottleneck #6 fix — combine was ~58% of
  merge wall, alloc-bound). Under β contributions arrive in ARBITRARY
  order, re-triggering the expensive left-extension realloc+copy under the
  shard lock — the exact pathology that tiebreak was built to kill. Fix:
  on first insert of a key, pre-extend the accumulator window to the key's
  minimum reachable `lo` so every later combine hits the cheap path. Must
  be designed in; it also shortens lock hold time.
- **Amendment β-2 (count-conservation invariant — specify correctly).**
  Raw count-sum is NOT conserved across a stage (window clipping at maxn
  drops mass), so the resume/correctness invariant must be the per-stage
  form: "Σ counts each core inserted == table Σ at the barrier." That
  catches lost updates deterministically; TSan alone is
  interleaving-dependent (the `permissiveBudget` precedent: a real bug no
  test has ever tripped).
- **Amendment β-3 (per-shard mutex only — drop "lock-free").** A
  variable-length count-vec with a realloc path cannot be combined
  lock-free without full RCU/retry machinery; a naive CAS-swap of a
  rebuilt vector silently drops concurrent updates. Locking only. Also:
  the shard's own rehash must happen under the same lock (a resize while
  another thread holds a record reference is a use-after-free).

**Straggler handling (C5) — β's genuine advantage over α:** with reduce
folded into map, "splitting a straggler" means splitting a range of
SOURCE records — trivial (map is per-record), no hot-bucket
sub-partitioning needed. The table absorbs value-side skew; source
splitting handles compute-side skew.

**Cost profile:** moderate novelty (concurrent hash aggregation is
standard in DB/analytics engines, new here), moderate implementation, one
bounded correctness concern (concurrent combine — β-2's conservation
check + TSan).

**SUPERSEDED (2026-07-09) by Design ρ below.** A dedicated reduce-primitive
hunt found β's single shared 25-30GB sharded table is strictly
cache-worse than private per-partition tables: at 30GB ≫ 40MB L3, EVERY
insert is a random miss into a huge shared structure PLUS a lock atomic.
Partitioning by key-hash FIRST (so each key lands in exactly one
partition) makes the per-shard mutex unnecessary entirely and the tables
cache-resident. β is retained here only as the design-history step that
led to ρ; do not build β — build ρ.

### Design ρ — Radix-partitioned private hash-aggregation (the reduce winner; subsumes β, dominates α's reduce)

**This is the primary candidate as of 2026-07-09.** It is the
cache-conscious, lock-free realization of the same bulk-synchronous
within-column parallel map+reduce architecture α and β share — grounded in
the state-of-the-art database group-by literature (Manegold/Boncz
cache-conscious partitioning; Balkesen/Teubner radix; Leis morsel-driven
parallelism), which solved *exactly* this problem (high-cardinality
associative-commutative aggregation at many cores).

**Mechanism, per stage:**
1. Each core maps its source records (C1: embarrassingly parallel) and
   streams each emitted successor into one of `cores×f` partition buffers
   selected by **`hash(full canonical key)`** (`f`≈8-16 over-partition
   factor). Sequential write-combined stores into partition buffers, NOT
   random scatter into a shared structure.
2. Barrier.
3. Each core takes the partitions it owns and hash-aggregates them
   **entirely privately** — no shard mutex, no CAS, ever. Because
   partitioning is BY KEY-HASH, a given canonical key lands in exactly one
   partition, so per-partition aggregation IS the global aggregate —
   **there is no final cross-table merge** (this is what β got wrong by
   sharing one table). Partitions are sized to fit L2/L3, so hash-probe
   and slot traffic are cache-resident.
4. At the barrier the full window of every key is present in its one
   partition → exact `ms`-prune, `permissiveBudget=false`, no pruning-loss
   (satisfies C2 via the barrier, like α/β).

**Why radix-PARTITION but not radix-SORT:** MSD radix on the raw canonical
key is catastrophic — `canonMixed` relabels components in first-occurrence
order so `b[0]∈{0,1}`, `b[1]∈{0,1,2}`, … extreme low cardinality, ~2
non-empty top buckets. The fix: radix-partition on a HASH of the full key
(multiply-shift/CRC32), which is uniform. And grouping for an aggregate
needs only key EQUALITY, never global order — so α's comparison-sort
produces sorted output that is pure wasted work (the next stage's map
reads records in any order, C1). ρ does O(n) hash-partition + O(n) private
hash-agg, replacing α's O(n log n) sort entirely.

**Why ρ beats each predecessor:**
- **vs α:** removes the sort outright (O(n) hash-agg vs n log n); for
  near-all-distinct keys with fan-in ~1-2 the hash-agg constant is far
  below n log n.
- **vs β:** kills the shared-table random-miss + lock atomic on every
  insert; private cache-resident partitions, lock-free, no final merge.
- **skew (C5):** key-FREQUENCY skew is benign-to-HELPFUL for hash-agg (a
  hot key is repeated combine into one cache-resident slot — cache reuse),
  and malign for sort (α still pays n log n to gather a hot key's run —
  α-1's tree-reduce exists only to rescue this). The one real skew risk is
  partition-LOAD imbalance, covered by over-partitioning (`f`≈8-16×) plus
  source-range map-side splitting (C5, trivial since map is per-record).

**Inherited amendments (mandatory):** β-1's window pre-extend (arbitrary
arrival order otherwise re-triggers the `combine` left-extension realloc
the `recordLess` tiebreak was built to kill), and C6's per-task
count-output discipline (the harvested-from-γ resume-bug fix).

**The one honest limit (C1 again):** the DOMINANT cost is moving and
combining ~150-byte values, and C1 says that byte-movement is CONSERVED
across α/β/ρ — none of them reduce it. ρ's advantage is confined to (a)
killing the sort and (b) making key-probe/hash-slot traffic cache-resident
and lock-free. Real and worth having, but a FRACTION of total, since value
bandwidth is untouched and fan-in ~1-2 gives little value-cache reuse. So
ρ clearly beats α (sort removed) and modestly beats β (cache+lock); the
size of ρ's margin over the value-bandwidth floor is exactly what the
Part-3 micro-benchmark measures. **The live benchmark is now ρ vs α**
(β retired as a strictly-cache-worse instance of ρ).

**Cost profile:** moderate novelty (morsel-driven radix hash-agg is
textbook in modern analytical DBs, new to THIS codebase), moderate
implementation, one bounded correctness concern (private-partition combine
correctness — the β-2 conservation invariant, and no concurrency inside a
partition at all so it's simpler than β's shared-table case).

### Design γ — Clean-slate task-graph engine (throw out ALL current code: Go/C++ split, run-file protocol, subprocess model, checkpoint model)

**Mandate:** what's possible if nothing is kept. This design keeps only
the *mathematics* (kink-carry transition + canonMixed + ms-pruning — C1/
C2 are properties of the problem, not the code) and reconsiders every
engineering decision jointly.

**Core structure:** one long-running process. The ENTIRE computation
(all heights, all columns, all stages) is expressed as a single directed
acyclic graph of fine-grained tasks with explicit data dependencies, fed
to one work-stealing scheduler over persistent OS threads. A task is an
in-memory object (a source-record range + stage id + a reference to its
input state store), never a subprocess. The unavoidable C1 reduce is a
first-class node type ("aggregate these producer outputs by canonical
key") implemented with ρ's radix-partitioned private hash-aggregation as
its primitive — γ ADOPTS ρ's reduce rather than competing with it, and
spends its novelty budget on the three things a clean slate uniquely
unlocks:

1. **Cross-boundary pipelining (attacks C4's one real dependency without
   violating it).** Column N+1's map cannot start until column N's
   frontier is final — BUT other heights' columns, and speculative
   *partial* work, can fill any bubble. In the task-graph model this is
   automatic: the scheduler always has the union of ALL heights' ready
   tasks to draw from, so the "lone final height" idle problem is
   attacked structurally — there is no separate per-height dispatch that
   can run dry. During the final height (no siblings left), the graph
   still exposes that height's own next-stage tasks the instant its
   dependencies clear; utilization holds until the literal last stage of
   the last column (satisfies the ramp-down-only-at-the-very-end bar).
2. **Checkpoint as a graph-cut, designed in (attacks C6).** A consistent
   checkpoint is a well-defined antichain (cut) in the task DAG: the set
   of completed tasks whose outputs fully cover a frontier. Because tasks
   are pure functions of their inputs and outputs are content-addressed,
   a checkpoint is "the set of materialized node outputs at a cut" — and
   resume re-runs exactly the un-materialized frontier, with NO
   possibility of double-folding a partial result (the existing bug class
   becomes structurally impossible: a task's output is either fully
   present and counted once, or absent and recomputed). This is the
   strongest argument for γ: it doesn't just avoid the resume bug, it
   makes that category of bug unrepresentable.
3. **Substrate + representation chosen together.** Single language
   (C++ — the Go orchestrator becomes a thin in-process scheduler,
   eliminating the Go/C++ marshaling boundary entirely). State store is
   in-memory content-addressed with explicit, deliberate spill for RAM
   pressure (β's RAM-ceiling concern is met with a spill policy chosen on
   purpose, not inherited from the run-file accident). Metrics are
   per-thread in-process counters (C7's mandatory real metrics, free).

**Adversarial review outcome (2026-07-09): DEMOTED to conditional. Both
headline wins were overstated; the one real contribution is harvestable
into α/β without the rewrite.**

- **Win #1 (cross-height pipelining) is largely a MIRAGE for the case
  that matters.** By the time the dominant final height runs alone — the
  long tail that dominates wall-clock — every other height has finished by
  construction (they're shorter and started at similar times), so there is
  NO cross-height work left to pipeline. γ's own text concedes it falls
  back to "that height's OWN next-stage tasks" — which is exactly the
  within-height parallelism α and β already deliver. Worse, the non-tail
  benefit is ALREADY IMPLEMENTED: `orchestrator/sweep.go:293` sorts
  heights tallest-first so the critical-path height starts at t=0,
  `runOverlap` (line 397) runs heights concurrently off one shared pool,
  and the `activeHeights` steal gate (lines 246-254) already flips to full
  stealing when a height becomes the pool's sole occupant. So win #1 buys
  ~nothing over β during the only window that matters.
- **Win #2 (checkpoint-by-construction) protects the wrong thing AS
  WRITTEN — but the fix is real and harvestable.** Content-addressing the
  frontier STATES does nothing for the actual resume bug, which is an
  ACCUMULATOR/materialization disagreement on the COUNT (`hTri` is a
  running sum via `addTriContribs`, persisted opaquely by `writeCheckpoint`
  sweep.go:217-238). The genuine fix — and it IS a genuine fix for the
  existing `results/kink-resume-sigterm-bug.md` — is: **make each task's
  count contribution a per-task materialized output, and DERIVE the
  triangle as a fold over the materialized-output set at resume, never
  persist a running accumulator.** Under that discipline "counted once" is
  true by construction. But this is NOT clean-slate-exclusive: it's
  already the pattern `runOverlap`'s height-level `markDone` checkpoint
  uses safely (lines 407-433). Pushing it down to column/task granularity
  is an INCREMENTAL change to the existing engine — and it is now adopted
  as a cross-cutting requirement for α and β below (see "Harvested from
  γ").
- **What's left of γ:** γ = β's reduce + a from-scratch scheduler +
  single-process substrate. With win #1 hollow and win #2 retrofittable,
  γ's ONLY remaining justification is the substrate change (in-process
  vs. files) — which C7 says is unmeasured and the priors
  (`pgo-no-go-dalby`, `profile-rows-measured`) suggest is compute-bound,
  not I/O-bound. **γ is therefore GATED on Part-3 measurement #1: build it
  only if file-I/O + subprocess dispatch turns out to be a large fraction
  of real expensive-column wall time. If that measurement comes back small
  — as the priors predict — γ is conceded, and its checkpoint discipline
  is taken into α/β instead.** The full-rewrite correctness risk (must
  re-establish the hand-verified, not-fully-proven `permissiveBudget`
  argument from scratch, discarding the one battle-tested artifact that
  embodies it) is not worth paying for a substrate win that may not exist.

**Harvested from γ (applies to ρ/α regardless of the substrate
decision):** the resume bug fix — per-task materialized count outputs +
triangle-as-derived-fold, never a persisted accumulator. This kills the
existing `kink-resume-sigterm-bug.md` bug class by construction and is an
incremental change to whichever reduce wins. It is now a REQUIREMENT of
the chosen design, not a γ-only feature.

---

## Part 3 — how to choose (the two cheap measurements that decide it)

Nothing here is committed on reasoning alone. Two cheap measurements
collapse the remaining uncertainty; neither is a full build.

1. **The tmpfs I/O test (decides whether γ / the substrate change is worth
   considering — almost certainly not).** Run ONE isolated real H18 column
   with the run-file directory on **tmpfs (`/dev/shm`)** vs. disk on dalby
   — a few GB/round, NO code change. Wall essentially unchanged → I/O-wait
   is near-zero (as the forensics predict) → γ is dead and ρ/α on a
   simplified current substrate is enough. Wall drops sharply → γ's
   in-process substrate is warranted. This is strictly cheaper than
   instrumenting a compute/IO/dispatch split and answers the same
   question.

2. **The ρ-vs-α reduce micro-benchmark (the ONE live design question).**
   Prototype ρ (radix-partition on `hash(fullkey)` → private per-partition
   hash-agg, with β-1's window pre-extend) against α (scatter + parallel
   sort-merge, with α-1's tree-reduce) on ONE real H18 stage's ~16M
   records at 80 cores. Measure wall, cache-miss rate, and achieved
   utilization. Small, throwaway, decisive — it picks the reduce primitive.
   Expectation from theory + the DB group-by literature: ρ wins, but the
   MARGIN is bounded by the conserved value-bandwidth floor (C1), so this
   measures how much of the fat-column 13%→~90% gain is actually
   reachable.

Note: the K-vs-loss curve that dominated the PRIOR version of this document
is moot — ρ and α are both barrier-based, `permissiveBudget=false` (no
deferral, no pruning-loss), so "how bad does deferral get at high K" no
longer gates anything (it only mattered for the rejected deferral-based
kink-sharded).

**Recommended order:** both measurements are cheap and independent — run
them together. Test 1 kills or confirms γ; test 2 picks ρ vs α. Do NOT
start any Phase-1 simplification until test 2 resolves the reduce, so
simplification deletes toward the chosen target rather than a guess. The
resume-bug fix harvested from γ (per-task count outputs,
derived-fold triangle) goes into whichever wins.

---

## Part 4 — the fourth-design hunt: one real candidate found and rejected, plus a proof the space is covered

A dedicated search for a decomposition axis α/β/γ miss (2026-07-09) found
exactly one structurally-sound new design and then closed every remaining
axis quantitatively. Recorded so nobody re-derives them.

### Design δ — "Pincer Sweep" (bidirectional meet-in-the-middle on the column axis) — REJECTED, economically dominated

**Idea:** C4's column chain is the one serial axis nobody attacked. Cut
the dominant final height's sweep at column c*: a(n,H) decomposes
additively as (animals entirely left of c*, from the normal forward
sweep) + Σ_s Σ_k L_k(s)·R_{n−k}(s), where L is the forward frontier at c*
and R(s) is the completion-count vector — computable by an INDEPENDENT,
concurrent right-to-left sweep, which by mirror symmetry is the SAME
kink-carry computation on the mirrored problem. Two sweeps, zero
communication until one trivial merge-join + count-vec convolution at c*.
It composes WITH α/β (each half is internally parallelized by them) and
halves the critical path of exactly the lone-final-height tail. Correct:
`completionLowerBound` is admissible, windows convolve cleanly, each half's
`ms` is its own fully-merged window (C2 holds per side).

**Why it's rejected:** the per-height cost is front-loaded — frontier
peaks at cols ~2-4 then collapses ×0.42/col; 74-87% of a tall strip's wall
is in cols 0-4 (`engine-utilization-and-scheduling`). The backward sweep,
being the mirrored problem, has its OWN peak in ITS first columns (which
cost near-zero in the forward sweep), so δ pays ~2× total work to shorten
a serial path whose cost was never length-uniform. It wins only where
per-column parallelism has run out of width (late thin columns) — which
the kink kernel already made milliseconds-cheap. If a peak column
saturates 80 cores (α/β's whole job), δ's 2× work makes wall WORSE. And it
doesn't generalize: K>1 cuts need each segment's full transfer MATRIX
(~2.6^2H) instead of a vector — exponentially dead. A conditional dead
end: build never.

### Why every other decomposition axis is closed (each dies to a measurement already in the repo)

- **Count-index n (split the count-vec).** State enumeration (union-find,
  canonMixed, sort/dedup) is 85-90% of the sweep and identical for every
  n-slice → K slices duplicate it K times. Exactly the measured CRT-residue
  result (`crt-counter-shaping-settled`: pay enumeration once). Also each
  slice's `ms` is wrong (C2). Dead, empirically.
- **Stage pipelining (core k owns stage k).** Streaming a record to stage
  r+1 before its stage-r contributions merge is un-deduplicated
  continuation — the duplication `kink_shard_probe.cpp` measured growing
  ~S^0.7-0.8 with no plateau. Pipeline depth H≈16 ≪ 80 cores anyway. Dead
  — it's old Candidate B in a different hat.
- **Ownership-predicate independence (Redelmeier-style).** A DP worker
  must carry every state reachable from its owned prefixes; distinct
  owners' reachable sets re-collide almost immediately — that overlap IS
  the measured non-saturating shard-duplication curve. The only zero-
  overlap ownership predicate is a function of a cut-column state — which
  is δ, already priced. So any "no-communication" design is either δ or
  the measured NO-GO. Closed rigorously.
- **Symmetry classes.** Burnside decomposes FREE into Fixed + fixed-point
  counts; it does not partition Fixed's own transfer-matrix work, and the
  R1 fold already banks the one usable mirror.
- **Speculative replica execution (race duplicate stragglers).** Valid
  engineering but duplicated-by-design → excluded by the "real,
  non-duplicated work" bar; and α-1/β's in-flight splitting makes it
  unnecessary.

**Conclusion of the hunt:** the design space is genuinely covered by
canonical-key-space partitioning (α/β) and whole-task scheduling (γ).
Every other axis collapses onto one of three graves — enumeration-
duplication, continuation-duplication, or the front-loaded ×0.42 cliff —
each with a measurement already in the repo. This is a proof of coverage,
not a failure to think of more.

---

## Explicitly considered and set aside (so they're known-rejected, not missed)

- **Removing the global reduce.** Impossible (C1, proven against code +
  prior memory). Every design pays it; none removes it.
- **Local/wavefront tiling (old Candidate C).** Refuted — no such local
  dependency exists in `kinkStageTransition`.
- **Barrier-free cross-stage streaming (old Candidate B).** Refuted —
  needs distributed termination detection that collapses into the barrier
  it claims to avoid, or reintroduces the silent-undercount bug.
- **Deferral-based source sharding (old Candidate A / current
  kink-sharded).** Superseded by α/β, which get the same
  per-column-barrier-reduction WITHOUT `permissiveBudget` pruning-loss and
  WITH in-flight straggler splitting (α-1). Its own review found its
  merge-once-per-column step is itself a serial barrier (sawtooth
  relocated, not removed) and it has no straggler handling.
- **A different state representation that makes the reduce
  partition-local.** `merge-shuffle-ranking-locality` proves a
  partition-preserving encoding cannot exist (expansion). Not chased.
- **Bidirectional column cut (δ / Pincer Sweep).** Correct but 2× work to
  shorten a front-loaded path; wins only where α/β already saturate. Part
  4. Build never.
- **GPU/SIMD.** Set aside for hardware fit (`pgo-no-go-dalby`: workload
  is branch-mispredict-bound, dalby has no compute GPU), not on principle.
