# Engine record: the production enumerator as measured

The production enumerator is a transfer-matrix program that counts fixed
polyplets by bounding-box height. It computes the triangle entry `T(n,H)`, the
number of fixed polyplets of `n` cells whose bounding box has height exactly
`H`, one height at a time; `a(n) = Σ_H T(n,H)`. This file is the engine as
measured: the two transitions and the price of the choice between them, what
limited core utilization and what moved it, memory and disk, the counter
representation, the negative results, what each term cost, and how a(41) was
reached with twenty of its forty-one heights enumerated. Every number is a
measurement from a run record, a benchmark or a profile, with the script, the
machine and the date beside it; estimates and extrapolations are labeled as
such. One statement is proved by exhaustion: the completion bound is
admissible at every signature for `H ≤ 12`. The file formats are
`docs/formats.md`; the per-term records are `results/ns_a*/PROVENANCE.md` and
`results/a41/PROVENANCE.md`.

Terms used throughout. A **height run** is the enumeration of `T(·,H)` for one
`H`; heights are independent jobs. The run proceeds **column by column** across
the bounding box; the **frontier** after a column is the set of boundary states
alive with their count vectors. Within a column, **map** applies the transition
to a shard of the frontier and writes a sorted run of successor records;
**merge** combines the sorted runs, adding the counts of equal keys; a **unit**
is one shard of map or merge work given to one worker process. A map worker
that outgrows its RAM budget **spills** a sorted run to disk. **Stealing**
splits a running unit at a cursor and gives its remainder to an idle core.
**Overlap** runs several heights in one core pool. A height is **injected**
when its entries are composed from the closed forms `P_k` of the diagonals
`k = n − H` held in the formula table `diagCoeffTable` in
`orchestrator/sweep.go`, instead of being enumerated; the formula for level `k`
holds from its **onset** `n ≥ 2k + 1`. **Utilization** is
`cpu_s / (wall_s × cores)`; **effective cores** is `cpu_s / wall_s`. The two
transitions are selected by the `--kernel` option and are called the **column
kernel** and the **kink kernel** below. Machines: dalby is an 80-core ARM
Neoverse-N1 (Ampere Altra) with 125 GB RAM and two NVMe drives in a RAID1
mirror, one thread per core, one socket; ayr is a 32-core x86-64 AMD
Threadripper 2990WX with 78 GB; gympie is an Apple Silicon laptop with 10
performance cores.

## What is in here

| section | what it answers |
|---|---|
| 1. The engine, component by component | what the program is: orchestrator, workers, run files, checkpoints |
| 2. The two transitions | the column kernel and the kink kernel, and the price of the choice |
| 3. Keeping the cores busy | what kept the cores idle, what moved it, and what the floor is |
| 4. The C++ hot path | where the time goes inside a worker |
| 5. The completion prune | within a few percent of optimal, admissible by exhaustion for H ≤ 12 |
| 6. Memory and disk | the layouts, the spills, the peaks, and what each term needed |
| 7. Counters | why production carries no modular arithmetic |
| 8. What the checks cover | the resume and combiner gates, and what the disk layer does not check |
| 9. The Redelmeier program | the independent enumerator's throughput |
| 10. Negative results | each with the measurement that closed it |
| 11. The cost of each term | the per-term table: wall, cores, disk, date |

## 1. The engine, component by component

Code anchors are file names; line numbers, where given, are at commit `25d7f61`.

**Boundary state.** In the column kernel a signature is `H + 2` bytes: one byte
per row of the most recent column holding `0` (empty) or a component label,
then a touched-top flag and a touched-bottom flag (`core/signature.h`). Labels
partition the occupied boundary cells into the connected components of the
partial animal. Crossing partitions are allowed, which king adjacency needs and
which is why the Motzkin encodings of the polyomino literature do not apply.
Labels are renumbered in first-occurrence order after every step so that
equivalent partitions cannot proliferate as distinct states. The hot path uses a
fixed 32-byte inline key (`H ≤ 30`), so the state store is a flat sorted run,
not a hash map of strings.

**Payload.** Each state carries a count vector indexed by cells placed so far,
stored as a window `(lo, len, counts[])`; two records with the same key combine
by elementwise addition, growing the window in place (`core/run.h`). The
combine is commutative and associative, which makes the merged result
independent of shard cuts and run order (`core/mapreduce.h`). Every addition is
guarded: `slot < prev` after an add means a word overflowed and the run aborts.
The guard is live only because `NSFLAGS` carries no `-DNDEBUG` (section 8).

**Counter width.** Two compile-time tags: `u64`, exact to a(25); `u128`, exact
to about a(48). The orchestrator refuses to start with an undersized counter
for the requested `maxn` (`core/counter.h`, `orchestrator/runref.go`). Every
production run from a(26) on used `u128` (`results/ns_a26/PROVENANCE.md`).
There is no modular arithmetic anywhere in the production path (section 7).

**Admissibility prune.** A state is dropped when cells placed so far plus a
lower bound on the cells any completion must still place exceed `maxn`. The
bound is the sum of three disjoint forcings: rows to climb to reach row 0 if
the top is untouched, rows to descend to reach row `H − 1` if the bottom is
untouched, and every empty band of rows between occupied rows that no single
component spans (`core/signature.h`). It must never over-estimate, since an
over-estimate silently drops real animals; section 5 measures its slack against
the true optimum.

**Map, merge, classify.** `map_shard` streams one shard of the frontier: for
each state, check the completion predicate and tally if met; enumerate the
viable successor masks; apply the transition; prune; optionally fold under the
vertical mirror (`--fold`, halving the state space); collect
`(successor, counts)`; sort and deduplicate into one sorted run. `merge` is a
k-way merge of sorted runs combining equal keys. Completion is the
closing-column path: a state whose next column is empty and whose boundary is a
single component with both touch flags set is one fixed polyplet of height
exactly `H`, tallied by size into the row `T(·,H)`; the holes variant reuses the
Euler accounting of `core/euler.h` (`core/classifier.h`).

**On disk.** Frontiers are `POLYRUN` files: a text header (height, `maxn`,
counter width, classifier, key range, record count, git revision, byte order),
sorted binary records, and an FNV-1a-64 checksum over the body
(`core/runfile.h`); zstd framing of spill and frontier files is a build option.
A checkpoint is a `POLYCKPT` file naming the frontier run files plus the
accumulated triangle, so the bulk of a checkpoint is the frontier already on
disk (`orchestrator/checkpoint.go`). Resume refuses a configuration mismatch,
and specifically refuses a different `--max-diag-k`, because that changes which
heights were injected.

**Orchestrator.** Go, one process per machine. Per column: partition the source
key space into map units, run map workers from a pool of persistent worker
processes (`orchestrator/workerpool.go`), sample the output key space into
merge ranges, run merge workers, garbage-collect consumed runs, checkpoint. The
options that mattered in production are all in `SweepConfig`
(`orchestrator/sweep.go`): `Cores`, `UnitMult` (map units per core),
`MergeMult`, `StealGrain`, `OverlapHeights`, `RAM` (per-worker spill budget),
`FastMapDir` (a tmpfs for transient map output), `Heights` (the multi-machine
split), `CounterWidth`, `MaxDiagK`.

- *Stealing* (`orchestrator/sweep.go`, `stealEligible`, `refGrainSeconds`,
  `stealAllowed`): when a core idles in a column's tail, the longest-remaining
  unit is stopped at a cursor and its remainder split across idle cores. A unit
  is eligible when its remaining records, or its remaining wall time at its own
  observed rate, exceeds a grain. The grain in seconds comes from the pace of
  finished units, not from elapsed wall time, because the latter is diluted by
  however long the current straggler has idled everyone. Stealing fires only
  when a height is the sole occupant of the pool, which lets it coexist with
  overlap. Merge has the same stop-key machinery and a queue-plus-steal phase.
- *Overlap* (`runOverlap`): several heights share one core pool so one height's
  low-utilization merge hides behind another's map; checkpoints fall at height
  boundaries, and an in-flight height is re-run from scratch on resume.
- *Injection* (`orchestrator/sweep.go`): heights `H = 1, 2` are elementary rows,
  `H = maxn` is `3^(n−1)`, `H = maxn − 1` is `(25n − 45)·3^(n−4)`, and
  heights with `k = maxn − H` in the formula table (`k = 1..19`) are
  composed from `P_k`. `--max-diag-k` caps which diagonals may be injected; a
  zero value means no injection, so a caller that forgets to set it gets more
  enumeration, never a wrong entry. Per-height rows are written as `h<H>.out`
  and re-summed by a combiner that refuses partial or duplicated inputs
  (`--require-cover`).

## 2. The two transitions

### 2.1 Mechanism

**Column kernel** (`core/transition.h`). King adjacency reaches the diagonal
neighbors `(c − 1, r ± 1)`, so a cell-at-a-time boundary would already have
overwritten the north-west cell a new cell may attach to. The column kernel
transfers an entire column per step with the old column wholly present;
connectivity is resolved by union-find over the new column's cells and the old
column's components, so k-way merges (a new cell fusing its W, NW and SW old
neighbors plus N and S new neighbors) need no special cases. A mask that
strands an old component is dead. The price is that every state pays
`Σ viableMasks(state)` per column, and masks per state was measured at about
1,400 at `H = 12`, growing exponentially with `H`. This is the transition every
production term through a(29) used.

**Kink kernel** (`core/kink.h`, `core/kink_column.h`). The boundary advances one
cell per stage, `H` stages per column, as in every published polyomino transfer
matrix from Jensen (2001) to Barequet and Ben-Shachar (2024). The key grows to
`H + 4` bytes: the mixed boundary (new-column cells above the stage row,
old-column cells below), the two touch flags, a carry byte holding the one old
cell overwritten a stage ago that is still king-reachable, and a placed-any bit.
Canonicalization relabels the boundary and the carry together. Harvest
(classifying completed animals) happens at column start on the state being
seeded; finalize at column end drops the last carry with a stranding check,
then canonicalizes, prunes, folds and deduplicates back to an end-of-column
run. Per state the work is about `2 × H × 3.6` successor records per column,
polynomial in `H`, where 3.6 is the measured ratio of intermediate states to
frontier states (flat across `H = 4..14`).

### 2.2 The measured price of the choice

Serial, one core, gympie, 2026-07-02, a probe since removed from the tree.
Identical per-`n` counts at every size were the built-in check.

| H | maxn | column kernel | kink kernel | ratio | column records | kink transitions | intermediate / frontier |
|---|---|---|---|---|---|---|---|
| 8 | 15 | 0.13 s | 0.04 s | 3.5× | 813 K | 314 K | 3.63 |
| 10 | 18 | 4.5 s | 0.41 s | 11.1× | 19.8 M | 3.1 M | 3.63 |
| 12 | 22 | 175 s | 6.0 s | 29.2× | 627 M | 32.6 M | 3.62 |
| 14 | 26 | ~5,000 s (estimated) | 95 s | ~55× (extrapolated) | — | 326 M | 3.60 |

The ratio grows about 2.7× per two rows of height because it is the
masks-per-state exponential being deleted. Extrapolated to `H = 16`, the probe
put the map-compute ratio at 150–200×; that figure was never measured. It is a
base change, not a constant: per-term compute growth of the column kernel was
about 4.4× (state growth about 2.42× times masks-per-state growth about 1.8×);
the kink kernel's per-state work is polynomial in `H`, so per-term growth falls
to about the state growth alone, about 2.5×.

The second consequence is that the shuffle collapses. Per-column record volume
drops from `Σ masks` (627 M at `H = 12`; a 126 GB spill peak at a(27) `H = 16`)
to frontier size, so the sort, spill and merge machinery and its zstd pipeline
stop being necessary for the tallest heights of a term.

Validation. `T(20..22, 12)` at `maxn = 22` and `T(24..26, 14)` at `maxn = 26`
match `results/ns_a27/perheight/` exactly. The two transitions are independent
implementations (per-cell union-find with carry stranding against per-column
union-find), so this is a cross-check between programs, not a regression test.
The production-scale validation is the a(29) entry-by-entry comparison of a kink
run at `maxn = 29` against the recorded column-kernel rows
(`scripts/kink_validate.sh`), after which the kink kernel computed a(30)
(`results/ns_a30/PROVENANCE.md`). `make gate-kink-oracle` runs the kink kernel
at `maxn = 18` with no injection against the published a(1..18).

### 2.3 Parallelizing the kink kernel

Two ways to run the stage-by-stage transition across many workers were priced
before the production version was built (2026-07-02; the probes have since been
removed, the numbers are these).

**Private per-shard stage DP, rejected.** Shard the sources by key, run the
full `H`-stage DP privately per shard, merge only end-of-column states.
Duplication of intermediate states grows with the shard count `S` and does not
saturate, measured as the ratio of summed stage sizes to the unsharded run:

| S | H = 8, key-range shards | H = 12, key-range shards |
|---|---|---|
| 2 | 1.44× | 1.52× |
| 4 | 2.07× | 2.32× |
| 8 | 2.90× | 3.52× |
| 16 | 3.91× | 5.38× |
| 32 | — | 8.08× |

Hash sharding is worse at every `S` (12.7× at `H = 12`, `S = 32`). The growth is
roughly `S^0.7–0.8`, worsening with `H`. Production shard counts are
`cores × unit_mult`, 128–320 on the two compute machines; extrapolating the
`H = 12` trend to `S ≈ 200` puts duplication in the tens to about 50×, which
eats most of the kernel's 29–55× win. Each shard rediscovers every intermediate
state reachable from its own sources, because key-range locality is not
connectivity locality.

**One merge barrier per stage, adopted.** Every stage is a single canonicalized
table, never sharded privately, so duplication is zero by construction. Its
total merge volume, summed over all `H` barriers per column, is already below
the column kernel's single barrier and the ratio shrinks with `H`:

| H | maxn | column-kernel barrier volume | per-stage barriers, all H | ratio |
|---|---|---|---|---|
| 8 | 15 | 812,669 | 166,407 | 0.205× |
| 10 | 18 | 19,848,039 | 1,646,580 | 0.083× |
| 12 | 22 | 626,679,092 | 17,096,571 | 0.027× |
| 14 | 26 | ~19.4 B (extrapolated) | 170,227,633 | ~0.009× |

The fixed cost of a barrier was bounded from production telemetry: the tail
columns of a height, where the frontier collapses toward zero, still pay every
fixed cost of dispatch, process start, sync and merge round-trip.

| run | H | column | frontier in | wall |
|---|---|---|---|---|
| a(27), dalby, 80 cores | 16 | 25 | 67 | 0.030 s |
| | 16 | 26 | 24 | 0.014 s |
| | 16 | 27 | 8 | 0.006 s |
| a(26), dalby, 80 cores | 15 | 23 | 159 | 0.066 s |
| | 15 | 24 | 64 | 0.031 s |
| | 15 | 25 | 23 | 0.014 s |
| | 15 | 26 | 8 | 0.006 s |

The round trip floors at 6–30 ms with no plateau above it, so `H` barriers per
column add well under a second of fixed cost at `H = 16` against savings of
100–300× in barrier volume. Source files: `results/ns_a27/cost_profile_dalby.tsv`,
`results/ns_a26/cost_profile.tsv`. At `H = 17`, `maxn = 33`, about 17 stages
by about 30 columns is about 500 barriers per height and 5,000–10,000 per
term, which at 6–30 ms each is two to three minutes against multi-hour peak
columns.

### 2.4 Which transition produced which term

From the per-term records, `results/ns_a*/PROVENANCE.md`.

| terms | engine | counter | notes |
|---|---|---|---|
| a(19)–a(20) | the earlier `cpp/tma` column engine | — | a(20) on ayr, all heights enumerated (`results/ns_a20/PROVENANCE.md`); a(19) is the first term where two algorithms agree |
| a(21)–a(22) | new engine, column kernel | u64 | a(21) dalby, 35.8 h, all heights enumerated, ayr `H = 1..17` identical (`results/ns_a21/PROVENANCE.md`); a(22) inside the a(23) run; both confirmed by the Redelmeier program (`results/redelmeier_row22/PROVENANCE.md`) |
| a(23) | column kernel | u64 | ayr `H = 1..16` + dalby `H = 17..23`; `H = 17, 18` identical across the two instruction sets (`results/ns_a23/PROVENANCE.md`) |
| a(24)–a(25) | column kernel | u64 | dalby; first closed-form injection at a(24) (`k ≤ 7`), `P_0..P_8` at a(25) |
| a(26)–a(29) | column kernel | u128 | first `u128` term is a(26); a(27) split dalby `H = 16` + ayr `H = 3..15`; a(28) ayr alone and a(29) dalby alone, run concurrently |
| a(30)–a(41) | kink kernel | u128 | a(30) is the first kink production term; configuration fixed from the a(29) comparison onward |

Tallest enumerated height per term: `H = 15` (a26, a28), 16 (a27, a29), 17
(a30), 18 (a31–a34), 19 (a35–a37), 20 (a38–a39), 21 (a40), 20 (a41, with the
diagonal formulas above it; section 11.3). The injection boundary advances one
height each time a new `P_k` enters the formula table.

## 3. Keeping the cores busy

The wins in wall clock were in keeping the cores fed, not in making the
transition faster. Two structural facts frame everything here. Columns within
a height are strictly sequential: column `c + 1`'s frontier is a function of
the fully merged frontier at column `c`, so nothing can start `c + 1` early.
Heights are mutually independent, which is the axis overlap uses.

### 3.1 Where the wall clock lives

Per-column telemetry of a(34) (`results/ns_a34/cost_profile_dalby.tsv`; dalby,
80 cores, no overlap, kink kernel, 2026-07-07):

    TOTAL wall_s = 13300.4   cpu_s = 210666.1   util = 19.8%

Heights `H ≥ 19` were injected; `H = 3..18` were enumerated.

| H | wall s | cpu s | utilization | share of total wall |
|---|---|---|---|---|
| 12 | 36.8 | 351.7 | 11.9% | 0.3% |
| 13 | 98.9 | 1,474.7 | 18.6% | 0.7% |
| 14 | 257.9 | 4,829.9 | 23.4% | 1.9% |
| 15 | 407.3 | 9,090.2 | 27.9% | 3.1% |
| 16 | 722.1 | 19,395.0 | 33.6% | 5.4% |
| 17 | 2,376.2 | 47,028.2 | 24.7% | 17.9% |
| 18 | 9,335.5 | 128,349.6 | 17.2% | 70.2% |

The tallest enumerated height is most of the run at the worst utilization of
any height that matters. Within `H = 18`, utilization is 12–16% in every fat
column and the fattest are the worst: column 4 holds 15.4 M records and
9,491 cpu-s and runs at 12.8%, about 10 of 80 cores. The seven fat columns
(`H = 18`, columns 2–8) are 37.3% of the whole run's wall at about 13%; the
thin tail, columns 19–34, is 2.7% of the run. So the idle was in the fat
middle of one height, not in the final tail, and cross-height scheduling could
touch at most a few percent of wall.

Inside a fat column the idle is the stage sequence concentrating work. At
`maxn = 33`, `H = 17`, column 5 (dalby, 2026-07-08):

| round | frontier in | map wall s | map cpu s | average cores active |
|---|---|---|---|---|
| stage 1 | 9,587,734 | 1.024 | 60.446 | ~59 |
| stage 4 | 19,641,706 | 2.951 | 127.722 | ~43 |
| stage 6 | 20,717,652 | 17.270 | 135.514 | ~7.8 |
| stage 8 | 20,943,386 | 25.058 | 131.604 | ~5.2 |
| stage 12 | 21,068,044 | 36.426 | 115.683 | ~3.2 |
| stage 16 | 21,364,246 | 45.584 | 112.973 | ~2.5 |

Frontier size is flat from stage 4 on while wall climbs 16× and cpu stays
flat: the same total work concentrates onto fewer of the 320 units as the
stage sequence deepens. The last open-ended key range topped the wall ranking
in 9 of 10 sampled rounds with wall uncorrelated to record count (4 M records
in 46 s; 957 M records in 21 s). The cause is the partition, not the
transition: cutting the key space by record count is blind to cost, and the
restricted-growth-string structure of the signature bytes makes even-by-count
diverge from even-by-cost as more cells are placed. Merge ranges show the same
last-bucket pattern. Section 3.3 is the fix.

### 3.2 Overlapping heights

Merge is the light, I/O-bound half of a column: it combines already-sorted
range-partitioned data, saturates with a few workers, and is all-to-all, so a
single column cannot absorb all cores during merge or during the map straggler
tail; overlap fills that gap with another height's map.

- gympie, 6 cores, `maxn = 18`, the column kernel (2026-06): overlap cut wall
  from 30.0 s to 24.5 s, about 18%, with checkpoint skipping ruled out
  (sequential with checkpoints off was still 30.2 s). Diminishing returns past
  depth about 2; overlapping all heights marginally best. Launching the tallest
  height first was a no-op when all heights fit concurrently (ascending 25.3 s,
  descending 25.3 s); it bites only when the overlap depth is capped below the
  height count.
- dalby, `maxn = 34`, `--heights 16,17`, kink kernel (2026-07-07):

| | wall | cpu s | utilization |
|---|---|---|---|
| `H = 17` alone | 2,462.7 s | 47,335.4 | 24.0% |
| `H = 16` alone (from the a(34) record) | 722.1 s | 19,395.0 | 33.6% |
| sum, hypothetical sequential | 3,184.8 s | 66,730.4 | 26.2% |
| `H = 16` + `H = 17`, `--overlap-heights 2` | 2,522 s | 66,596.3 | 33.0% |

`H = 16`'s 722 s landed almost free: the combined run took 59 s longer than
`H = 17` alone, a 21% wall cut with identical cpu-seconds. Overlap packs work,
it does not redo it. Peak RSS for the pair was 2.7 GB.

- dalby, `maxn = 30`, enumerating `H = 3..15`:

| `--overlap-heights` | wall | cpu s | utilization | a(30) |
|---|---|---|---|---|
| 1 (sequential) | 689.6 s | 11,926.6 | 21.6% | 227969227118066423789154, correct |
| 15 (all owned) | 378.2 s | 11,742.2 | 38.8% | correct |

A 1.82× wall speedup with near-identical cpu-seconds. Deployed in
`scripts/term.sh` as `--overlap-heights "$N"`; over-provisioning the pool
past the enumerated count is harmless, and the co-resident RAM of all
enumerated heights at this scale was under 100 MB. Per-unit instrumentation
(`POLY_UNIT_LOG=1`, `scripts/analyze_unit_concurrency.py`) on a `maxn = 26`
column showed map active only about 22% of a column's span (`H = 13`, column
4: 0.88 s of 4.09 s); the rest is inter-round merge with zero map concurrency,
which is why the deployed depth is all owned heights, not 2.

- The floor at scale. At `maxn = 33` through the same driver, utilization was
  about 10.4%, and `H = 17` alone was 6,839.6 s of the 6,842.7 s total: once
  every cheaper height finishes, the tallest runs alone with nothing to hide
  behind. The wall cannot drop below the tallest height's serial column chain,
  and its own merge and straggler idle is unrecoverable by any cross-height
  scheduler.

### 3.3 Partition balance

A benchmark on one real fat `H = 18` stage (16 M records, the real
`kinkStageTransition` and `combine`, dalby, 80 cores, 2026-07-09; the
benchmark program has since been removed) measured effective cores under two
partitions of the same data:

| partition | effective cores of 80 |
|---|---|
| balanced, record-quantile splitters | 74.6 (93%) |
| even key-value ranges, the engine's open-ended last bucket | 6.8 |

Identical output both ways, 13,623,078 records. The production ceiling of
about 13.7 cores at `H = 18` was reproduced by the unbalanced partition and
lifted about 11× by balancing it; the record-level parallelism was already in
the data.

Built as `BalancedCutsMulti` (true record-quantile partitioning replacing
per-file fixed-count sampling) and confirmed on a real height run (dalby,
`--heights 15 --maxn 30`, `--kernel kink --counter u128 --cores 80
--ram 1073741824 --unit-mult 8 --merge-mult 1 --steal-grain 0.05
--persistent-workers`, old `aa4bbd29` against new `60dd2cde`, 2026-07-09):

| column | old effective cores | new effective cores |
|---|---|---|
| 3 | 20.88 | 33.66 |
| 4 | 23.39 | 33.98 |
| 5 | 23.59 | 33.63 |
| 6 | 24.10 | 33.74 |
| 7 | 23.40 | 34.16 |
| 8 | 23.03 | 34.75 |
| 9 | 24.38 | 34.81 |

Whole `H = 15` run of 30 columns: 204.3 s → 140.9 s (1.45×), cpu 4,626.4 →
4,554.1 s, `T(n,15)` identical for every `n` (`build/ns/combine --diff-b`). The
lift is 1.4–1.5× rather than the benchmark's 11× because these columns hold
640–790 K records, not 16 M; fewer records means fewer well-sized units for 80
cores, independent of balance. The residual gap after balancing (fat columns
at about 34 of 80) is compute-per-record skew inside units, the case for
in-flight splitting (open).

Two more measurements that settled the design. Files on tmpfs (`/dev/shm`)
against NVMe for the identical `H = 15`, `maxn = 30` run: 204 s against
190–193 s, so file I/O was about 7% of wall at that scale and a clean-slate
in-process rewrite could recover at most that. A reduce-primitive benchmark
(since removed) on about 16 M records emitted by the real transition, stages
1, 5, 9, 12 and 16, over-partition factor 4–128: radix-partitioned private
hash aggregation ran at 0.83–1.05× the speed of the parallel sort-merge
(median about 0.91; sort-merge about 3.45 s, hash 3.6–4.2 s). Short 22-byte
keys, low collision (fan-in about 1.16) and a conserved value-copy cost
dominate both, so the database-literature prediction that hash aggregation
beats sort-merge does not hold here. The parallel sort-merge reduce on the
existing process-and-file substrate was kept.

### 3.4 Work stealing

Stealing as first built fired zero steals at every scale, for three
independent reasons, each fixed and each measured:

1. **Progress stride.** The progress callback fired only every
   `2^14 = 16,384` source records, and a unit with `processed = 0` was
   ineligible; at `maxn = 20` each of 8 units held about 11.8 K records, and
   at a(24)/a(25) scale (`H = 16` frontier about 4.7 M records, 256 units) a
   unit holds about 18.4 K, about 1.1 strides. The stride is now 1,024
   (`kProgressStrideMask` in `core/mapreduce.h`, compile-time limit 4,096); a
   microbenchmark put the check at 0.7–0.85 ns per record at every stride
   from `2^14` down to `2^6`. On an isolated `H = 13` column with a confirmed
   2× per-unit compute imbalance (gympie, `maxn = 20`, column kernel): steals
   0 → 15; wall 151.4 s → 98.5 s over 3 repetitions; cpu-seconds 618.8
   against 618.5; sampled core occupancy 51.3% → 68.7%.
2. **Overlap and stealing coexist.** Stealing had been statically disabled
   whenever `OverlapHeights > 1`. A dynamic `activeHeights` count, re-checked on
   every steal decision, allows stealing once a height is the pool's sole
   occupant. Identical output, unit-tested.
3. **The 2 s throttle.** An unconditional 2 s throttle on progress reports
   meant units finishing faster than 2 s never registered any progress, so the
   `processed > 0` gate blocked them permanently. With the first progress
   report firing immediately (dalby, `H = 17` isolated, 2026-07-08): before,
   "steals = 0 for 173 s"; after, 9,468 steals in a 3,523.9 s run with
   identical output. Merge had no rebalancing mechanism at all; adding the
   same stop-key machinery to `mergeRunFiles` and a queue-plus-steal merge
   phase took the same column from 3,523.9 s to 3,103.2 s (11.9%), 10,448
   steal events, identical `H = 17` output. Both are in production.

Three further eligibility changes (a wall-time fallback in `stealEligible`; a
reference pace from finished units only; a 2× overshoot fallback in
`remaining()` for the open-ended last key range) are correct and tested but
moved nothing measurable on their own (dalby, a(34) `H = 17` column 3:
24.7% → 25.1% → 25.0% → 24.0%), because they sit downstream of the throttle.

A stop-flag check inside a record's own transition was priced on the column
kernel's recursive mask generator at about 10.7% overhead; that generator is
not what production runs. The kink kernel's per-record path,
`kinkStageTransition` in `core/kink.h`, is a bounded loop over two choices
with `O(H)` work per call, and its cooperative-stop flag is checked once per
1,024 records, between records.

At `maxn = 30` with every fix above in place, `--steal-grain 0` against `0.05`
measured 281.6 s against 283.4 s: at that scale stealing neither costs nor
saves anything measurable.

### 3.5 Unit and merge granularity

**Merge fan-out.** Merge's own active-window concurrency was about 15 of 80
cores even under overlap. Not imbalance: on `H = 15`, column 4 (5,120 ranges),
the largest single range was 0.1% of the column's merge wall. Fixed per-process
overhead: wall barely correlates with output records (Pearson `r = 0.24`); a
range with 1,206 records takes about 0.035 s and one with 31,745 records about
0.09 s; most of each about 37 ms range is process start and file opens.
`--merge-mult` had silently followed `--unit-mult`. dalby, `maxn = 30`, all
heights overlapped:

| `--merge-mult` | wall | cpu s | utilization | a(30) |
|---|---|---|---|---|
| 4 (implicit) | 377.7 s | 11,670.5 | 38.6% | correct |
| 1 (deployed) | 305.7 s | 7,291.7 | 29.8% | correct |

19% faster and 37% fewer cpu-seconds. The utilization ratio fell because
unproductive cpu-seconds were removed; wall and total cpu are the truer
signals.

**Map units.** Coarser units lose: `--unit-mult 2` against 4 was 384.5 s
against 283.4 s, a 35% regression. Finer units on the column kernel also lost
(a18/a23 tests: `--unit-mult` 4 → 16 added 9.5% wall and pushed makespan over
ideal from 1.215× to 1.780×, because static repartitioning isolates heavy
states into one unit instead of dividing them; predictive longest-first
ordering closed at most 71% of the gap and needs a predictor that does not
exist, the column-to-column rank correlation of unit cost being 0.23–0.49). On
the kink kernel finer units win:

| `--unit-mult` | `maxn = 30` wall | cpu s |
|---|---|---|
| 4 | 265.0 s | 7,155.8 |
| 8 | 215.4 s | 7,463.6 |
| 16 | 252.0 s | 8,068.8 |

| `--unit-mult` | `maxn = 33` wall | cpu s | utilization | a(33) |
|---|---|---|---|---|
| 4 | 6,798.6 s | 55,440.2 | 10.19% | correct |
| 8 | 5,674.2 s | 56,300.5 | 12.40% | correct |

16.5% faster at production scale with utilization up;
a(33) = 74631481980411777590683952 both times. Deployed as `--unit-mult 8`.
The mechanism is plausible, not proved: finer units keep any one unit's local
sort-and-dedup small in the collision-heavy late stages.

**Checkpoint cadence.** `--checkpoint-every 300` against effectively off
(`999999`), `maxn = 30`: 305.7 s against 303.9 s. Not a lever at these run
lengths.

### 3.6 The orchestrator's own overheads

- **GC churn.** `GODEBUG=gctrace=1` on dalby, `maxn = 30`: 8,063 GC cycles in
  about 305 s against an 8 MB heap goal, about 5% of CPU by Go's own account.

| `GOGC` | wall | cpu s | a(30) |
|---|---|---|---|
| 100 (default) | 303.9 s | 7,377.7 | correct |
| 400 | 288.7 s | 7,688.9 | correct |
| 1000 (deployed) | 283.4 s | 7,762.4 | correct |

- **Allocation.** A heap profile (`POLY_MEMPROFILE`) found `readIndexHeader`
  allocating a full 4 KB buffered reader to decode a 19-byte fixed header at
  two call sites; key sampling alone was 55% of a run's allocation, 11.7 GB
  of 21.4 GB. Replaced by one `io.ReadFull` into a stack array; `ParseHeader`'s
  buffer right-sized to 256 bytes. Wall was flat at `maxn = 30` with `GOGC =
  1000` already masking the symptom (282.5 s against 283.4 s); a second profile
  showed a 24% cumulative reduction in `sampleIndexKeys` allocation.
  `orchestrator/sample_bench_test.go` exercises the path in about 0.5 s.
- **Process per unit.** Map and merge workers ran a fraction of a second each
  and paid fork and exec every time. `--persistent-workers` keeps one map and
  one merge process per pool slot alive for the run, reading request lines from
  stdin (`worker/map_worker.cpp`, `worker/merge_worker.cpp`,
  `orchestrator/workerpool.go`; `tests/engine/gate_persistent_worker.cpp` drives
  the real binaries through one process against the one-shot path). dalby,
  `maxn = 30`: 282.5 s / 7,755.3 cpu-s → 265.0 s / 7,155.8 cpu-s, 6.2% and 7.7%,
  zero orphaned processes after normal exit and after a real SIGTERM.
- **All of these at production scale**, `maxn = 33`: wall 6,803.2 s against
  6,842.7 s, 0.6% faster. The fixes are real at small and medium scale and
  shrink to noise once one height's own floor swallows the budget;
  `--unit-mult 8` and the steal fixes came after this measurement.
- **Orchestrator RSS.** During the a(40) attempts the orchestrator's RSS grew
  from 2.8 GB to 4.4 GB in minutes. Not a leak: telemetry streams to disk and
  every pool is capped; `GOGC = 1000` is a ratio, so the heap may reach about
  11× live before a collection. The orchestrator keeps `GOGC = 1000` and sets
  `debug.SetMemoryLimit` (default 4 GiB, `POLY_GO_MEMLIMIT_GB`, 0 = off); an
  undersized limit costs CPU, never correctness
  (`orchestrator/gomemlimit_test.go`).

### 3.7 The design space

Two constraints every parallel decomposition must respect, verified against
`core/kink.h`. The per-record map reads only its own signature bytes and emits
0–2 successors, so the map is embarrassingly parallel over any partition. The
reduce cannot be made local: `canonMixed` relabels components in
first-occurrence order, so adjacent source keys canonicalize to output keys
anywhere in the space and far-apart keys collapse to the same output key
(a partition-preserving encoding cannot exist without expansion). The
`ms`-prune fires at every stage off the record's own minimum size, and a
partial window silently drops a valid branch, so either the prune is deferred
(more surviving states) or a per-stage barrier establishes the full window.
The barrier is not the enemy; idle cores within a phase are.

Decompositions priced and rejected, each against a measurement in this file:

- **Bidirectional column cut** (meet in the middle at column `c*`; the backward
  pass is the mirrored problem). Frontier peaks at columns 2–4 and then falls
  about ×0.42 per column, with 74–87% of a tall height's wall in columns 0–4,
  so the backward pass has its own peak where the forward pass is cheap: about
  2× total work to shorten a path whose cost was never uniform. `K > 1` cuts
  need a full transfer matrix (about `2.6^(2H)`) per segment.
- **Splitting the count index `n`.** State enumeration is 85–90% of the work
  and identical for every slice; `K` slices pay it `K` times (section 7), and
  each slice's `ms` is wrong.
- **Stage pipelining** (core `k` owns stage `k`): un-deduplicated continuation,
  the `S^0.7–0.8` duplication of section 2.3; depth `H ≈ 16` is below 80 cores
  anyway.
- **Ownership by prefix** (Redelmeier-style): reachable sets of distinct owners
  re-collide at once, the same non-saturating duplication curve; the only
  zero-overlap ownership predicate is a cut-column state, which is the
  bidirectional cut.
- **Symmetry classes.** Burnside decomposes free into fixed plus fixed-point
  counts; it does not partition the fixed count's own transfer-matrix work; the
  mirror fold already uses the one usable symmetry.
- **Speculative replicas** of stragglers: duplicated by design.
- **Barrier-free cross-stage streaming**: needs distributed termination
  detection that collapses into the barrier it avoids, or reintroduces the
  silent undercount.
- **Local wavefront tiling**: no such dependency exists in `kinkStageTransition`.
- **Cross-machine stealing.** The big machine is reachable only over a
  sub-MB/s uplink and the column merge is all-to-all, 0.4–1 GB per column.
- **GPU or SIMD.** Set aside for hardware fit: no compute GPU on the big
  machine.

### 3.8 System-level profile

A full run under `vmstat`, `iostat`, `mpstat`, `pidstat` and `/proc/pressure`
sampling (dalby, rev `5fadde3`, `--maxn 24 --heights 1-15 --cores 80 --ram
1073741824 --unit-mult 4 --overlap-heights 15 --steal-grain 0.05`, column
kernel, 2026-06-30; the script has since been removed). Wall 2,283.3 s, peak
RSS 614 MB, `H = 15` the dominant height. The figure is
`results/dalby-perf-audit.png`.

- Utilization 79.3% (cpu 144,889.6 s), agreeing with `mpstat`'s 20.1% mean
  idle over 1,141 samples. Median idle 0.14%, 75th percentile 23.3%: the idle
  is concentrated, not spread, in `H = 15`'s last ten columns, where units
  fall below the pool (column 21: 92 units; 22: 32; 23: 9; 24: 0) as the
  frontier collapses toward the injection boundary. This 79.3% is not
  comparable with a(34)'s 19.8%: the shape is far shallower and overlap was on.
- No disk or memory pressure: `iostat` essentially idle (occasional writes
  under 103 IOPS); `/proc/pressure/io` and `/proc/pressure/memory` zero in
  every sample; `/proc/pressure/cpu` "some" nonzero in 576 of 1,141 samples,
  peaking at 4.9% (mild oversubscription at `unit_mult 4`). Free memory never
  below about 73 GB.
- Process churn: 10,365 distinct `map_worker` PIDs; minor faults about 2,024/s
  per sampled process row; major faults 0.003/s; involuntary context switches
  about 31/s. Fork and exec cost showed as scheduler noise, not disk.
- Compiler: clang beat gcc by about 5% (75.4 s against 78.9 s, `maxn = 18`,
  3 repetitions, identical output); `-mcpu=native` was a wash to slightly
  negative for both. Deployed clang. Neoverse-N1 has no SMT and no NUMA, so
  the usual x86 levers do not apply. The Makefile's `CXX ?= c++` had been
  losing to GNU Make's built-in `CXX = g++`, so the Linux boxes had been
  building with GCC 15.2.0.
- `perf stat` produced no data: the sampling loop ran `timeout 30 perf stat -a
  ... -- sleep 30` with zero margin, so every iteration was killed before it
  printed. IPC and cache-miss rates for the transfer-matrix workload remain
  unmeasured.

### 3.9 Measurement tooling

External process sampling at 1 Hz and 0.1 Hz (`scripts/profile_concurrency.py`)
is unusable below production scale: 96.6% of samples read zero map workers
during the dominant height of a `maxn = 26` run, because unit runtimes are
under 100 ms and `ps` itself costs as much. Exact in-process intervals
(`POLY_UNIT_LOG=1`, `start_unix` per unit, `scripts/analyze_unit_concurrency.py`)
replaced it. Repeated two-minute toy benchmarks were abandoned as too noisy in
favor of one 20–25 minute `maxn = 29` reference run. A same-code sequential
baseline is taken before any speedup is believed: the first all-heights
overlap run at `maxn = 30` appeared to stop enumerating at `H = 15` instead of
`H = 17` and looked like data loss; it was the closed-form coverage having
grown (`P_13` and `P_14` had entered the formula table, so `H = 15` is the
tallest enumerated height at `maxn = 30`).

## 4. The C++ hot path

### 4.1 Map profile (column kernel, gympie, 2026-06)

Static audit of `map_shard_file` in `core/mapreduce.h`: the successor build
`succ.counts.assign` is the sole per-successor heap allocation; the transition
and mask enumeration are stack-only; `combine` allocated a fresh vector per
equal-key collision. `record_est = sizeof(RunRecord) + maxn·sizeof(W) + 32` with
`sizeof(RunRecord) = 72` for both widths:

| width | `record_est` at `maxn = 25` | actual mean resident per record |
|---|---|---|
| u64 | 304 B | about 224 B |
| u128 | 504 B | about 336 B |

The estimate charges `maxn` count words where the real window is about
`0.56·maxn` (about 14 words), so it is conservative in steady state and blind to
two transients: the `buf` vector doubling (up to 2× live objects, 3× during the
copy) and millions of tiny `counts` mallocs.

Dynamic profile, `-DPOLY_PROFILE` phase timers in `core/profile.h`, `maxn = 16`
and 18, gympie, `--ram 2 GB`, weighted over the 20 hottest `H = 12` columns:

| phase | share |
|---|---|
| map (classify, enumerate, step, build) | 61% |
| spill (sort, dedup, write with FNV) | 39% |
| merge (one-file spill merge) | ~0% |
| read | 0% |

Function-level (`sample`, leaf self-time, single-process `maxn = 17`):

| bucket | share of cycles |
|---|---|
| enumeration (`stepColumnSquare8` about 44%, plus the per-mask lambda and `viableRec`) | 57% |
| alloc and free of per-successor `counts` (`free` about 4× `malloc`) | 14% |
| sort (`__partition`, `recordLess`, `memcmp`) | ~19% |
| zeroing the 32-byte `Sig` | 4% |
| combine | 3% |

Memory: `buf.capacity() / buf.size()` up to 1.92 at the spill point;
`record_est` 1.2–1.3× actual at a full buffer; peak RSS 1.0–1.05× `--ram` at a
2 GB budget (1,909–2,114 MB measured) because the over-charge cancels the
doubling and fragmentation overhead, and 1.54× at a 16 MB budget where fixed
overhead dominates. So `--ram` is a faithful peak-RSS proxy at GB scale (±10%).

### 4.2 Map body profile (u128, `maxn = 24`, `H = 13`, 2026-07-02)

`map_shard_file`, 3,405 samples: `s8::viableRec` (the recursive viable-mask
generator, which prunes 76% of leaves) about 91%; `stepColumnSquare8` low
single digits; `counts.assign` 2 samples. A per-successor arena would have
removed 2 of 3,405 samples and was abandoned; micro-optimizing the step
function's zero-initialization was worth under 1%. A prior iterative rewrite
of `viableRec` measured about 0%, so the cost is the number of nodes descended.
The only map-CPU lever left was a tighter completion bound, which section 5
closes.

### 4.3 Merge ledger (2026-06)

`merge_worker` calls the streaming `mergeRunFiles` in `core/runfile.h`, which
holds `K` readers (one `FILE*` with a stdio buffer of about 4 KB each), a heap
of exactly one record per reader (`sizeof(Cursor) = 80 B`), and no result
vector; resident set about `K × 4.2 KB`, about 1 MB at `K = 256` and 1.3 MB at
`K ≈ 320`. Measured: RSS never left the few-MB floor. A bounded merge unit
seeks every reader to its `lo` through the on-disk `.idx` (binary search by
`fseek`, never loaded into RAM) and reads its slice plus at most 64 records of
overshoot per file. The write path hashes every body byte with FNV-1a-64; a
seeked read skips the read-side check.

CPU split over 123 standalone column merges (`maxn = 18`, mean `K = 5.8`,
566 K output records):

| phase | share |
|---|---|
| combine (a fresh vector per equal-key collision) | 58% |
| write (FNV-1a and `fwrite`) | 23% |
| read and heap (`memcmp`) | 19% |

2.36 combines per output record. The merge is combine-bound and combine was
allocation-bound.

### 4.4 What shipped and what was rejected (2026-06, gympie)

Acceptance for anything touching sort, merge or combine: identical output on
a(14), a(16) and a(18) `--compare`.

| change | measured | validation |
|---|---|---|
| `combine` grow-in-place when `new_lo == lo` (`core/run.h`) | 0 allocations on the in-window path; map sort-dedup-write phase 39% → 32% at `maxn = 18`; merge combine bucket 58% → 56% (the timer includes the heap drain) | `tests/engine/gate_run.cpp` requires 0 heap allocations over 1,000 in-window combines; identical a(14), a(16), a(18) |
| `sigCmp`, 8-byte-chunk key compare (`core/signature.h`) | 1.29–1.52× on the sort and heap comparator, 13 sites | microbenchmark; identical a(14), a(18) |

End to end, multi-process orchestration at `maxn = 18`, 4 repetitions each,
against the baseline `e694a39`: −7.3% wall at 2 GB RAM (43.6 → 40.4 s),
−6.6% at 256 MB (41.7 → 39.0 s). The at-scale check before the a(24) and
a(25) runs: a(20) `--compare` through the full stack (combine, `sigCmp`,
`--overlap-heights 13`, height-boundary checkpoints, commit `f40e12b`),
a(1..20) identical including a(20) = 1025573519362016, wall 118.9 s on 8 cores.

Rejected after measurement: an indirect sort (index array, permute once) at
0.61× the speed of `std::sort` on the 72-byte records; a radix sort of the
terminal buffer (needs an `N`-record temporary at the moment the buffer is at
`--ram`); in-place left extension in `combine` (rare, bug-prone `memmove`); a
thread-local counts pool by size class, built with identical output, 0.5%
slower at production RAM and 0.9% slower under multi-spill because the system
allocator already keeps per-size thread caches (its headline "14%" was a
single-process leaf-sample artifact). Deferred: hardware CRC32C in place of
byte-wise FNV-1a, 10.6× on the hash (1.0 → 10.6 GB/s) with no global build
flags, about 5% of compute, but a checksum format change consumed by 7 Go files
and 2 C++ headers.

### 4.5 Block-buffered run-file I/O (2026-07-22)

Profiling the persistent workers on gympie (`H = 15`, `maxn = 30`, 10 cores,
macOS `sample`) found about 90% of busy samples inside stdio:
`RunFileReader::next` issued one locked `fread` per field, in the worst case
one per varint byte (about 120 calls per record), and `RunFileWriter::append`
one `fwrite` per field; the kink transition was about 5% of busy time. The fix
is internal to `core/runfile.h` and byte-format identical: the writer assembles
each record in a stack buffer and emits it into a 256 KB block buffer; the
reader serves plain reads from a 256 KB block (checksum folded at consumption,
buffer dropped on `seekToKey`) and compressed reads from a decompressed block,
which also removes the per-byte `ZSTD_decompressStream` calls.

`scripts/gympie_bench_phase.sh`, `H = 15`, `maxn = 30`, 10 cores: wall 335.1 s
→ 99.8 s (3.36×), cpu 2,899 → 764 cpu-s (3.8×). Validation: full `make
ns-gates`; a fresh a(20) run with `combine --compare`; a full a(26)
production-shape run (kink, u128, overlap, formula-table diagonals, 23.7 s on
gympie) matching `results/ns_a26/triangle.txt` on a(20)–a(26). The post-fix
profile is balanced (reader about 303, writer about 293, transition about 150,
sort and moves about 250 samples), with no dominant slice left. Section 6.1 is
what this became on the 80-core machine.

### 4.6 Dedup collisions and window width

Do deeper stages cost more per unique key because more predecessors
canonicalize to the same successor? Benchmark (since removed), best of 7
trials, 65,625 records per unit (one `H = 17` unit's share of a 21 M frontier
at 320 units), against the real `deduplicateRun` and `combine`:

| scenario | collision rate | window width | dedup time |
|---|---|---|---|
| low collision, narrow | 1× | 4 | 1.23 ms |
| low collision, wide | 1× | 30 | 1.49 ms |
| high collision, narrow | 20× | 4 | 1.12 ms |
| high collision, wide | 20× | 30 | 2.71 ms |

Collision rate and width compound rather than add. A `recordLess` tiebreak on
`lo`, so the sorted path always hits combine's cheap grow path, gave 7.4% in
that scenario locally and at production scale (`maxn = 33`) 6,803.2 →
6,798.6 s wall (0.07%) and 55,825.9 → 55,440.2 cpu-s (0.69%): its savings land
on cores that were already idle. Deployed, harmless, not the driver of the
16× per-stage wall growth; that was the partition (sections 3.1 and 3.3).

## 5. The completion prune is within a few percent of optimal

Does `completionLowerBound` (top reach, bottom reach, unspanned vertical bands)
match Barequet's completion budget, whose `n_c` is a two-dimensional minimum
spanning tree over the components? Frontier dumps showed a large
multi-component population:

| H | surviving states | mean components | two or more components |
|---|---|---|---|
| 8 | 1,604 | 1.79 | 64% |
| 10 | 11,005 | 2.12 | 79% |

Ours ignores the horizontal cost of merging components with no vertical gap,
so it is plausibly looser. A king cell can merge several components at once,
so the naive `(c − 1)` cells for `c` components is not even a valid lower
bound, and an over-tight bound silently prunes valid states.

An oracle (since removed) computed the true minimum completion cost of every
signature by value iteration over the production transition on the full
signature universe per height, then re-ran the enumeration with the perfect
prune, `n / H ≈ 1.8` throughout (the production top-height ratio; a(29)
enumerates `H = 16` at `maxn = 29`, 1.81). Both variants produced identical
per-`n` counts.

| H | maxn | universe | states with zero gap | peak-states ratio | records ratio, perfect / current |
|---|---|---|---|---|---|
| 8 | 15 | 826 | 87% | 1.000 | 1.007 |
| 10 | 18 | 5,568 | 74% | 1.003 | 1.020 |
| 12 | 22 | 39,507 | 60% | 1.003 | 1.037 |
| 14 | 26 | not completed; estimated 1.05–1.06 | | | |

`completionLowerBound` is admissible at every signature, exhaustively for each
`H ≤ 12` (0 violations). Most states sit exactly at the bound; gaps of one or
two cells cover nearly all the rest, with one outlier per `H` at gap `H`, the
never-touched state. The peak frontier, which sets RAM, spill and most of the
map wall, is untouched (ratio at most 1.003); the prune only bites in the tail
columns. The ceiling for any completion-prune improvement, including a full
Barequet `n_c`, lazy exact lookahead or lookup tables, is 2–4% of emitted
records at probe heights, extrapolating to about 6% at `H = 16`, with zero
effect on peak states. The horizontal merges are usually free because a
next-column cell that merges two vertically adjacent components also serves
the rightward extension both need. Not built.

## 6. Memory and disk

### 6.1 Reader fan-in (dalby, 2026-07-23)

The 3.36× of section 4.5 did not reproduce on the 80-core machine:
`scripts/bench_util.sh` `H = 15`, `maxn = 30` gave 336 s wall and 20,106
cpu-s on both the fixed and the pre-fix build, against the balanced-cuts
baseline of 140.9 s and 4,554 cpu-s. Not frequency (cores at 3.0 GHz under
load), not a stale binary (revision stamps checked).

The mechanism, measured: system-wide `perf` put about 33% of all box cycles in
`__arch_copy_to_user` under page-cache reads, mostly in merge workers, and
about 10% in anonymous-page zeroing on the map side; `/proc/PID/io` showed
342 GB of logical reads in 20 s (about 17 GB/s) against a run directory of
about 350 MB, a read amplification of 10³–10⁴; `strace` on a map worker showed
every unit opening every input range file of the previous round (header read,
on-disk `.idx` binary search, buffer setup) though a unit's range overlaps 1–2
of the 74–80 files: about 640 units × 80 files ≈ 51 K open-and-seek sequences
per round, about 25 M per run, about 0.45 ms each; `gdb` stack samples attributed
the rest to request lines of about 25 KB read one byte per `underflow` through
`std::getline(std::cin)`, and every reader's fixed 256 KB buffer crossing
glibc's mmap threshold, so each of about 18 M reader instances paid an
mmap-zero-munmap cycle. The 10-core laptop never showed it: 10 cores × mult
8 = 80 units against 640, and about 10 merge ranges against 74, a units ×
inputs pair count about 59× smaller, under macOS's per-byte stdio cost.

Four format-neutral fixes, each followed by the full gate suite and an a(26)
production-shape run (a(1)–a(20) exact, a(21) and a(26) exact): per-unit input
pruning by the stamped key range of each file (unstamped files never pruned; an
empty prune falls back to the full list; `orchestrator/prune_inputs_test.go`);
a merge-range record cap so each range carries at least 2,048 records;
peek-sized reads (adaptive body fill from 8 KB doubling to 256 KB, reset on
seek; 512 B stdio buffers on header and `.idx` handles, so a peek costs about
16 KB rather than 285 KB); arena-sized reader buffers plus bulk request reads
through POSIX `getline(3)`.

| build (dalby, `bench_util.sh`, `H = 15`, `maxn = 30`) | wall | cpu s |
|---|---|---|
| before | 336–344 s | 20–21 K |
| plus pruning and merge cap | 204.6 s | 10.3 K |
| plus peek reads | 184.9 s | 9.3 K |
| plus arena buffers and `getline` | 104.5 s | 3.9 K |
| the balanced-cuts baseline for comparison | 140.9 s | 4.6 K |

3.2× wall and 5.2× cpu against the same code's own baseline on that machine.
A performance result measured on one machine is a result about that machine;
the engine is rebuilt and re-benchmarked on the target machine after every
edit.

### 6.2 The saturated mirror (2026-07-23/24)

Live `iostat` during a(38)'s `H = 20`: the RAID1 device `md3` at 100%
utilization, about 755 MB/s of writes and 720 MB/s of reads concurrently,
queue depth 120–170, write await 17–26 ms; merge writers stalled on the
device. The since-boot average of 37 MB/s had hidden it. Two software levers:

- **Block-framed frontier zstd** (`POLY_FRONTIER_ZSTD=1`, level
  `POLY_FRONTIER_ZSTD_LEVEL`, default 1): map and merge outputs, previously
  plain, get one independent zstd frame per index stride, with `.idx` entries
  at frame starts so `seekToKey` works compressed. Whole-file ratio on a live
  a(38) `H = 20` merge file: 1.83× at level 1, 1.86× at level 3. The Go tools
  refuse compressed bodies they cannot read.
- **`--fast-map-dir`**: a map round's outputs are read once by merge and
  deleted, about half of all device traffic; routed to `/dev/shm` with a
  per-round `statfs` headroom check (2× projection plus 20% margin; fallback
  to the run directory logged as `event=fastmap_fallback`). Live residency at
  the `H = 20` peak about 10.5 GB of 62 GB. C++ writers abort on any short
  write (`writeOrDie`), so `ENOSPC` kills the run rather than undercounting.

The compressed path on the 10-core laptop's bench loop (baseline 486 s wall,
6.0 K cpu-s):

| build | wall | cpu s |
|---|---|---|
| first cut (256 KB peeks, 1,024-record frames, per-open contexts) | 2,283 s | 19.8 K |
| plus adaptive compressed-path fills | 1,164 s | 10.8 K |
| plus frames equal to the index stride (64 records; seek overshoot 63, not 1,023) | 1,292 s | 6.0 K |
| plus pooled zstd contexts | 684 s | 7.1 K |

The residual there (+41% wall, +20% cpu) is the worst case: CPU-starved,
paying zstd with no disk problem to solve. The frame-size curve on identical
live a(39) `H = 20` records (5.72 M records, plain 158.8 B per record,
`experiments/reframe_measure.cpp`, `POLY_FRONTIER_ZSTD_BLOCK`):

| frame, records | B per record | ratio | gympie bench wall / cpu |
|---|---|---|---|
| plain | 158.8 | 1.00× | 486 s / 6.0 K |
| 64 | 109.8 | 1.45× | 684 s / 7.1 K |
| 256 | 92.1 | 1.72× | 576 s / 6.9 K |
| 512 | 89.0 | 1.78× | 778 s / 8.5 K |
| 1,024 | 87.5 | 1.81× | killed early at 1.8× merge cpu |

U-shaped: below about 256 records per-frame overhead dominates, above it
seek overshoot times fan-in does; 256 beats 64 on both axes and is the default
(a(39) itself ran at 64). dalby A/B at the 64-frame configuration: bench
105.6 s / 3.9 K → 119.3 s / 5.1 K with the levers on (+13% wall, the
no-disk-benefit regime). The production win was at the tallest height: a(39)
`H = 20` columns about 3,500–3,600 s against a(38)'s about 5,400–5,600 s at the
same 127–128 M frontier, 1.5×, from tmpfs map outputs and compressed merge
traffic together; a(39) took 11.1 h against a(38)'s 15.8 h one term lower.

a(38)'s `H = 20` was far heavier than a ×2.15-per-height model predicted:
frontier 127 M records (2.8× `H = 19`'s 45 M peak), about 5.5 ks per column at
column 8 of about 39, effective cores about 14, cpu per record about 1.6×
`H = 19`'s. Per-record cost growing with height is what the a(40) phasing and
the `H = 21` projection (about 2.1× `H = 20`, 280–350 GB of disk) were priced
on.

### 6.3 The RAM budget and phasing

With every height of `maxn = 40` overlapped on 80 cores the machine's 125 GB
does not hold the co-residency of the `H = 19, 20, 21` rounds. The budget is

    workers × (spill budget + about 0.5 GB per-worker overhead)
      + tmpfs map output + merge readers + orchestrator + page-cache floor.

At 72–80 workers the first term alone is 90–120 GB; no option setting closes it
while all heights run concurrently. The contributing terms as measured: the
tmpfs admission check was a point-in-time `statfs` that `N` concurrent rounds
could each pass (now a reservation with a floor); idle zstd reader pools were
unbounded (now capped at 64); the merge reader army, 80 workers × about 640
open compressed readers × about 0.7 MB grown buffers, was about 35 GB of
round-periodic spikes (now a 64 KB reader-fill cap); and each worker carries
about 0.5 GB of RSS beyond its spill budget (unaudited).

The design that fits is phasing (`scripts/term.sh` for `N ≥ 40`): phase A, the
cheap heights with full overlap on 80 cores; phase B, `H = 20` alone; phase C,
`H = 21` alone on fewer cores. A single height bounds RAM at one working set,
and the tallest height is disk-bound at about 14 effective cores anyway. The
cost is the loss of overlap's interleave on the cheap phases (about +20–40%
wall there, about nothing at the top). The per-worker RAM budget is
`(total × margin) / cores`, never a flat number.

### 6.4 tmpfs run directories

Placing the whole run directory on tmpfs was a large win up to a(34) (no
measurement of the figure survives) and ran out of memory at a(35); a(35) and
later ran on NVMe. The varint format's −60% writes plausibly shrink the
`H = 19` working set from a(35)'s 150–200 GB to 60–80 GB, which would fit
125 GB; measure the run-directory footprint with `du` during an NVMe run
before trying it again. The 7% of section 3.3 is for a much smaller run
(`H = 15`, `maxn = 30`) that never touched the disk regime of section 6.2.

### 6.5 Disk does not scale like CPU (dalby, 40 cores, rev `7429268b1`, 2026-08-24)

`scripts/dalby_nmax_disk.sh` measured the peak run-directory size, sampled
every 10 s with spill kept:

| H | Nmax 40 | Nmax 42 | Nmax 45 | factor 40 → 45 | 40 → 44, interpolated |
|---|---|---|---|---|---|
| 14 | 499 MB | 437 MB | 580 MB | 1.162 | 1.058 |
| 15 | 1,244 MB | 1,533 MB | 1,872 MB | 1.505 | 1.408 |
| 16 | 3,634 MB | 4,456 MB | 5,040 MB | 1.387 | 1.331 |

`H = 14` is not usable (its Nmax-42 peak reads below its Nmax-40 peak, which
is impossible; the runs are under a minute and six samples miss the peak), and
every figure is a floor on the true peak. Against the a(40) peak of 363.4 GB:

| target | factor | projected peak | against 563 GB free |
|---|---|---|---|
| Nmax 44 | 1.331–1.408 | 484–512 GB | +51 to +79 GB spare |
| Nmax 45 | 1.387–1.505 | 504–547 GB | +16 to +59 GB spare |
| Nmax 45 at the CPU factor 1.620 | 1.620 | 589 GB | −26 GB |

Both targets fit on every usable reading. The CPU factor climbs with height
(1.442 at `H = 14`, 1.466 at `H = 15`); the disk factor falls (1.505 at
`H = 15`, 1.387 at `H = 16`). Two points do not make a law, but nothing
supports 1.62× for disk. This removes disk as an argument against a term
beyond a(41) and says nothing about the other argument, that row 45 rests on
level `k = 23` with one pair of determining entries and no check value.

## 7. Counters: fewer, wider, and no modular arithmetic in production

The earlier `cpp/tma` engine (`cpp/tma/sweep8_modp.h`) counted residues
recombined by the Chinese remainder theorem. The production engine that
computed a(23)–a(41) counts in native 64- or 128-bit words (section 1);
modular counting survives in the tree only in the coloring recount
(`results/second-sources.md`), a different program. The production counts were
never reconstructed from primes. The measurements below (2026-06-25, benchmark
since removed) are what settled that.

The transfer matrix is 0/1, so a step is `dst[n] += src[n]` with both operands
already below `p`. There are no multiplications, so Barrett and Montgomery
reduction do not apply; the levers are counter width, number and size of
moduli, reduction style, pass layout and SIMD. The count row is about 84% of
per-state memory in that engine, so width is directly the RAM lever (u64 →
u32 measured 1.73× less memory), but sub-linearly: at u16 the row is 72% and
per-state memory 0.58× of u32; at u8, 56% and 0.37×.

Extrapolating a(20)/a(19) ≈ 6.76, `L = log₂ a(n)`:

| n | a(n), approximate | L | u64 exact |
|---|---|---|---|
| 20 | 1.03e15 | 49.9 | yes (confirmed) |
| 21 | 6.9e15 | 52.6 | yes |
| 22 | 4.7e16 | 55.4 | yes |
| 23 | 3.2e17 | 58.1 | yes |
| 24 | 2.1e18 | 60.9 | yes |
| 25 | 1.4e19 | 63.7 | yes, the last |
| 26 | 9.8e19 | 66.4 | no |
| 27 | 6.6e20 | 69.2 | no |
| 28 | 4.5e21 | 71.9 | no |

Moduli needed, `k = ceil(L / usable bits)` with usable bits 7.97 (p = 251),
16.0 (65521), 31.0 (2³¹ − 1):

| target | L | u8 | u16 | u32 at 2³¹ | u64 |
|---|---|---|---|---|---|
| a(22) | 55.4 | 7 | 4 | 2 | 1 |
| a(25) | 63.7 | 9 | 4 | 3 | 1 |
| a(26) | 66.4 | 9 | 5 | 3 | — |
| a(28) | 71.9 | 10 | 5 | 3 | — |

Reduction style and width, gympie, single thread, scalar, working set about
290 MB, in millions of row-adds per second:

| width | no reduce (ceiling) | `% p` | conditional subtract | deferred | GB/s, deferred |
|---|---|---|---|---|---|
| u8 | 23.5 | 17.9 | 20.2 | 25.4 | 1.8 |
| u16 | 19.1 | 15.3 | 17.0 | 20.3 | 2.9 |
| u32 | 17.3 | 14.0 | 15.8 | 31.4 | 9.0 |
| u64 | 16.4 | — | — | 16.4 (no reduce) | 9.4 |

`% p` is the slowest reduction at every width; deferred reduction (sum the
in-edge group in a `uint64` temporary, reduce once per destination) takes u32
from 14.0 to 31.4, 2.24×. Small counters never reach their bandwidth advantage
in scalar code: u8 stalls at 1.8 GB/s and is slower than u32 while needing 3–4×
the moduli; only SIMD (vectorized add and min-subtract) makes them memcpy-bound.

The governing probe on the real engine (`N = 15`, `H = 12`, single thread,
gympie): u64 exact 55.4 s, mod-p one prime 50.6 s. Removing the entire modular
layer moves the time by under 10%, so enumeration is 85–90% of a pass and the
count arithmetic 10–15%. Hence the pass count is the primary multiplier: three
independent passes pay the enumeration three times (about 2.7× the wall of one
interleaved pass carrying three residues per state), and the reduction-style
win acts on the 10–15% slice (about 5% of wall). The production engine uses
native words; the coloring recount uses u32 primes just under 2³¹
(2147483647, 2147483629, 2147483587) carried interleaved in one enumeration
with deferred reduction.

The `u128` ceiling: `orchestrator/runref.go` refuses `u128` above `maxn` 48
on the final row sum alone, while intermediate multi-component counts exceed
the row sum; silent wrap is prevented only by the `assert(slot >= prev)`
guards in `core/run.h`, live because `NSFLAGS` has no `-DNDEBUG`, and
`core/counter.h` still says overflow is silent. Any run at `Nmax ≥ 45` should
first measure the largest per-state count in an existing run.

## 8. What the checks cover

**Resume after SIGTERM.** A real SIGTERM to a kink-kernel run followed by
`--resume` once produced a(n) too high from about `n = 8` on: each column's
seed-round completions were folded into the running height row before the
stage and finalize rounds, while the mid-column checkpoint stamped
`Col = col − 1`, so a resume re-ran the seed round and counted it again. The
fold now waits until the finalize round succeeds, so the row only ever holds
completed columns. `orchestrator/kink_resume_midcolumn_test.go`
(`TestKinkResumeMidColumn`, in `ns-gate-resume-boundaries`) kills mid-column
through a test seam, resumes and asserts the triangle; it failed before the
fix (`n = 3`: 21 against the known 20) and passes after; a real subprocess
SIGTERM reproduction passes 5 of 5. The overlap path was never affected: it
checkpoints only a completed-height set and re-runs any in-flight height.

**Zeroed rows.** Re-entering a completed phase in resume mode once rewrote
`perheight/h20.out` from an empty in-memory table. The combiner refused the
zeroed shard; the value was recovered from the checkpoint's count table, and a
clean `H = 20`-only re-run reproduced it (`results/ns_a40/PROVENANCE.md`;
`orchestrator/zero_harvest_test.go`).

**Kink kernel against independent values.** `make gate-kink-oracle` runs the
kink kernel at `maxn = 18` with `--max-diag-k 0` against the published
a(1..18); the production validation is the a(29) comparison against the column
kernel (`scripts/kink_validate.sh`) and the agreement with the coloring
recount, neither automated.

**What the disk layer does not check.** The plain-format body checksum only
prints on mismatch and is never invoked on the seeking reads production uses;
under zstd the last frame of a range-bounded read is never checksummed
(`core/runfile.h`). The a(40) run predates the short-read fix `b5b4948`, under
which a truncated frontier body read as end-of-run with exit 0; a dropped
record loses a whole count vector, so the chain and `H = 21` checks would
almost certainly have caught it, but it is a residual. No manifest or
`build/ns/verify` pass is recorded for a(40) or a(41). The `H = 20` identical
re-run of a(40) is determinism on the same reader, not independence.

**Fixtures.** `fixtures/` is protected by `SHA256SUMS`, which `gate_g1` checks
first; the checksum file is regenerable, so the protection is against
accident, not a deliberate edit of both. The b-file headers record the OEIS
revision and date checked (`b006770.txt`: revision 44, 2026-05-30);
`scripts/fixture_oeis_recheck.py` re-verifies over the network, not as a gate.

## 9. The Redelmeier program's throughput (dalby, 2026-07-10/11)

`build/g2` is the independent Redelmeier enumerator used to confirm rows by a
second algorithm (`results/redelmeier_row22/PROVENANCE.md`).

Profile of rev `7eab237`, `build/g2 square8 15`, one core, 167.1 s:

| counter | value | derived |
|---|---|---|
| cycles | 501.02e9 | |
| instructions | 1,187.39e9 | IPC 2.37 |
| branches | 210.81e9 | |
| branch misses | 4.14e9 | 1.96% miss rate, about 9% of cycles |
| L1 data loads | 513.10e9 | |
| L1 data misses | 1.49e6 | 0.0003% |

Full-cost nodes at `N = 15`, `Σ a(1..14) = 1.3157e10`: 90 instructions and 38
cycles per node. Not branch-miss-bound (IPC healthy, cache perfect) but
instruction-throughput-bound, so the levers that delete instructions win.
`perf annotate` put over 30% of samples in the unrolled 8-way neighbor probe
(offsets reloaded from the struct every node, status byte load, conditional
push), significant `memcpy` weight in the per-call copy of the untried list,
and about 7% in the spill store. The terminal-parent level holds
a(N−1) / Σ a(1..N−1) of all full-cost nodes: 84.8% at `N = 15`, 85.2% at
`N = 21`. This profile is of the Redelmeier program; the transfer-matrix
engine's IPC and miss rates were never captured (section 3.8).

| lever, cumulative | `N = 15` | against base | kept |
|---|---|---|---|
| baseline `7eab237` | 167.1 s | 1.00× | |
| pure count at the terminal-parent level | 95.0 s | 1.76× | yes |
| plus `-mcpu=neoverse-n1` | 95.2 s | 1.76× | no |
| plus constexpr neighbor offsets | 89.1 s | 1.88× | yes |
| plus branchless probe | 89.4 s | 1.87× | no, reverted |
| plus u16 untried list | 88.7 s | 1.88× | kept for footprint |
| plus gcc PGO | 91.0 s | 1.84× | no, worse than `-O3` |
| plus clang++-19 `-O3` | 81.3 s | 2.06× | yes, in the Makefile as `G2CXX` |
| plus clang PGO | | | blocked: no `libclang-rt-19-dev` or `llvm-19` on that machine |

Settled at 2.06×. Fusing the size `maxn − 2` level was estimated at about 3%
for real structural risk and skipped.

Fleet throughput, single core, `N = 15`, clang builds:

| box | ISA | cores | wall | per core against dalby | dalby-core equivalent |
|---|---|---|---|---|---|
| dalby | Neoverse-N1 | 80 | 81.3 s | 1.00× | 80 |
| ayr | x86-64 | 32 | 63.5 s | 1.28× | 41 |
| gympie | Apple Silicon | 10 | 27.1 s | 3.00× | 30 |
| fleet | | 122 | | | 151 |

The single-core shares over-predicted ayr: under all-core load its
Threadripper reaches memory over Infinity Fabric for half its cores and ran at
0.92× dalby per core (1.275 against 1.386 shards per hour per core), gympie at
2.62×. The row-22 run (`scripts/g2_fleet_launch.sh 22 12 24000`, launched
2026-07-11) was rebalanced 2.9 h in to contiguous ranges dalby [0, 14300), ayr
[14300, 19460), gympie [19460, 24000) with about 1% of shards redone, and
completed 2026-07-16 (box walls 427,974 s, 418,525 s, 440,745 s), with
a(21) = 6954084405510437 and a(22) = 47255332844367680 equal to the
transfer-matrix values. Rows 18 and 19 had validated the pure-count path
across three compilers and instruction sets (a(18) = 22471158811164,
a(19) = 151609203011580, 360 of 360 shards). Benchmark fleet boxes under
all-core load before allocating shares.

## 10. Negative results, with the measurement that closed each

- **Work stealing as first built.** Zero steals at every scale until the
  progress stride and the 2 s throttle were fixed (section 3.4); the three
  eligibility fixes alone moved nothing.
- **Sub-record interrupt.** Priced at 10.7% on a transition production does not
  run; never designed for the kink kernel, where the cost sits at the
  shard-level sort and dedup, not the per-record transition.
- **Finer static units on the column kernel; predictive longest-first
  ordering.** Section 3.5.
- **Coarser map units** (`--unit-mult 2`): 35% regression.
- **Checkpoint cadence, steal disable, spill-zstd toggle** at `maxn = 30`: all
  within noise; the spill-zstd result is inconclusive by scale (a(30) barely
  spills) and untested at the 5.5 GB RSS of `maxn = 33`.
- **Cross-height pipelining as the main lever**: at most a few percent of wall
  (section 3.1).
- **Clean-slate in-process rewrite**: file I/O about 7% of wall at `H = 15`,
  `maxn = 30`.
- **Hash aggregation as the reduce**: ties or loses to sort-merge (section 3.3).
- **Private per-shard stage DP**: `S^0.7–0.8` duplication (section 2.3).
- **Bidirectional column cut and the other decompositions**: section 3.7.
- **A tighter completion prune**: at most 2–4% of records, 0% of peak states.
- **Indirect sort, radix sort, in-place left extension, a counts pool, a
  per-successor arena**: sections 4.4 and 4.2.
- **Smaller modular counters**: slower per pass and more passes (section 7).
- **PGO** on `build/g2`: worse than `-O3`; `-mcpu=native` or `-mcpu=neoverse-n1`:
  a wash for both compilers and both programs.
- **tmpfs run directories past a(34)**: out of memory (section 6.4).
- **The 4-bit signature pack**: after varint the key is about 20% of record
  bytes and spills are compressed, so about 10% of bytes for a format risk.
- **Cloud.** At 19.8% utilization core count was not the binding constraint.
  The wall is floored by the single most expensive height, an inherently
  sequential column chain, so extra small machines do nothing; the only
  purchasable speedup was one bigger machine for that one height, sized at an
  `hpc7a.96xlarge` (192 physical cores, no SMT, about 2.4× the 80-core
  machine) at roughly $7–8 per hour on demand. Decided against.

## 11. The cost of each term

### 11.1 The ledger, a(26)–a(41)

From `results/ns_a*/PROVENANCE.md` and `results/a41/PROVENANCE.md`. A blank
means the record does not state it. Where two machines ran, the wall is per
machine, not summed. Dates are 2026.

| n | date | machine, cores | transition | enumerated H | wall | cpu s | RSS max | disk peak |
|---|---|---|---|---|---|---|---|---|
| 26 | 07-02 | dalby 80 | column | 1–15 | 4,066.5 s | | | |
| 27 | 07-02 | dalby 80 (`H = 16`) + ayr 32 (`H = 3..15`) | column | 3–16 | 13,553.9 s / 9,697.2 s | | | spill about 126 GB |
| 28 | 07-02 | ayr 32 | column | 3–15 | 11,723.8 s | 353,201.8 | 786.9 MB | |
| 29 | 07-02 | dalby 80 | column | 3–16 | 26,202.2 s | 1,960,646.8 | 1,647.1 MB | |
| 30 | 07-03 | dalby 80 | kink | 3–17 | 3,711 s | | about 76 MB | |
| 31 | 07-03 | dalby 80 | kink | 3–18 | 10,003.1 s | | about 5.9 GB | |
| 32 | 07-03 | dalby 80 | kink | 3–18 | 10,945.3 s | | about 5.78 GB | |
| 33 | 07-04 | dalby 80 | kink | 3–18 | 12,200.3 s | | about 6.02 GB | |
| 34 | 07-04 | dalby 80 | kink | 3–18 | 13,316.7 s | | about 6.44 GB | |
| 35 | 07-10 | dalby 80 (`H = 19`) + ayr 32 (the rest) | kink | 3–19 | 25,112.2 s (dalby) | | 372 MB | |
| 36 | 07-10 | ayr 32 (`H = 1..18`) + dalby 80 (`H = 19`) | kink | 3–19 | 6,988.2 s / 11,810.4 s | 187,437.7 / 397,861 | 351.6 / 380.2 MB | |
| 37 | 07-23 | dalby 80 | kink | 3–19 | 13,048.4 s | 580,223 | 394.6 MB | 75.7 GB |
| 38 | 07-23/24 | dalby 80 | kink | 3–20 | 56,994 s | 1,783,598 | 971 MB | 221.5 GB |
| 39 | 07-24/25 | dalby 80 | kink | 3–20 | 39,957 s | 2,070,672 | 1,516 MB | 174.5 GB |
| 40 | 07-25..28 | dalby, three phases | kink | 3–21 | section 11.2 | 5,318,465 (sum) | 4,045 MB | 363.4 GB |
| 41 | 08-20 | dalby 40 | kink, `H = 1..19` | 3–19 | 16,998.7 s | 605,643 | 557 MB | under 100 GB |
| 41, `H = 20` | 09-05 | dalby 76 | kink | 20 | 34,678.8 s | 1,766,882 | 814.7 MB | not recorded |

Three things the table shows: the kink kernel's entry at a(30), a whole run of
62 minutes with `H = 17` as its tallest height against 7.3 hours for a(29) with
`H = 16` on the column kernel; the disk wall from a(37) on; and that a(41)'s
enumerated half on 40 cores cost about what a(37) did on 80 (605,643 against
580,223 cpu-s) because the two tallest heights were not enumerated.

### 11.2 a(40), three phases

`maxn = 40` with full overlap does not fit 125 GB (section 6.3), so a(40) ran
2026-07-25..28 on dalby alone as `FRONTIER_LEVERS=1 scripts/term.sh 40`:

| phase | heights | cores | wall | cpu s | RSS max |
|---|---|---|---|---|---|
| A | 1–19 and 22–40 | 80 | about 6.3 h | 871,963 | 827 MB |
| B | 20 alone | 48 | 9.6 h, one interruption and resume | 1,116,858 | 1,023 MB |
| C | 21 alone | 32 | 36.4 h | 3,329,644 | 4,045 MB |

Disk peak 363.4 GB mid-`H = 21`. The `H = 21` frontier peaked at 355,390,806
records, a stable about 2.7× per-column cost over `H = 20`. `H = 21` is the
tallest height ever enumerated by the project. `scripts/term.sh` sets
`--max-diag-k 18` for `N ≥ 40` so that a re-run keeps `H = 21` an enumeration
rather than an injection from `P_19`, the formula determined from that very
entry.

### 11.3 How a(41) was reached

Level `k` of the diagonal formulas needs two entries at or above its onset,
the two tallest entries on its diagonal; for `P_19` those were `T(39,20)` and
`T(40,21)`, the latter being a(40)'s 36.4-hour phase C. The grand form
(`docs/proofs/grand-form.md`, its content proved in Lean) makes each level carry exactly
two new constants, so any two independent linear equations determine it, and
the below-onset defect identity (`results/below-onset.md`) supplies such
equations from entries `j` rows shorter than the onset, with the defect
`D_j(k)` computed from cluster-weight families that read neither the triangle
nor the formula table. Nothing new was proved; the content is the choice of
determining entries.

So a(41) was two jobs (`results/a41/PROVENANCE.md`): heights 1–19 enumerated at
`Nmax 41` (`--kernel kink --counter u128 --cores 40 --overlap-heights 19
--heights 1-19`, 4.72 h), and heights 20–41 composed by
`experiments/undertow_a41.py`, levels `k ≤ 19` from the formula table and
`k = 20, 21` determined from below-onset entries. A run at `Nmax 41` also
reproduces every recorded row `n ≤ 40` at the heights it enumerates: 760
entries agree, 0 disagree, and the assembler refuses the `n = 41` row unless
they match. An independent recount by a route that never reads the assembler
agrees. For the 19 enumerated heights, two programs with no shared code agree
on every entry; for heights 20 and up, the formulas are a second
implementation fed the same defect tables, not a second enumeration.

The one enumeration that crosses assumption families for `T(41,20)`, the
`H = 20` run at `Nmax 41`, ran 2026-09-05 (`scripts/dalby_a41_h20.sh`, dalby, rev
`b88b38bc5`, 76 cores, `--max-diag-k -1`): 9.63 h, and the enumerated entry
equals the formulas' prediction, 18004779862205054677763902712770. The frontier
peaked at 129,487,745 records at column 7; columns 6–8 each took about 2,300 s
at about 126,000 cpu-s (`results/a41/h20_cost_profile.tsv`). a(41) is heights
1–20 enumerated, 21–41 from the formulas, 800 entries of `n ≤ 40` agreeing.

### 11.4 Where the engine stops

- Per-term compute growth is about 2.5× on the kink kernel (about 4.4× on the
  column kernel), and from a(37) the binding limit is disk (section 6.5 for the
  Nmax-44 and 45 projections).
- The algorithmic decompositions are measured closed (section 3.7); the
  bounding side reaches the same connectivity wall
  (`results/growth-constant.md`). What is left is engineering.
- Cost is not the count. A height's compute tracks its frontier, which grows
  exponentially in `H` (the kink probe's estimate is about `2.6^H` states with
  `H ≈ n/2 − const`), not the number of animals it contributes, so the tallest
  heights are never cheap however small their entries: `H = 21` alone cost
  36.4 h at a(40).
- The strip enumerator cannot follow: `C_14` measured about 38 GB and `C_15`
  would need over 200 GB (`results/second-sources.md`).

## Open problems

- Which code path carries the concentrated cost in a late-stage kink unit
  (shard-level `sortRun` and `deduplicateRun`, spill I/O, or
  `RunRecord::counts.assign`'s width-dependent cost) was never profiled
  directly; the dedup benchmark of section 4.6 explains part of the 16×
  per-stage wall growth and the partition of section 3.3 the rest, but no
  `perf record` of one slow unit exists.
- In-flight splitting by key sub-range regardless of record count, the
  residual after balanced cuts (fat columns at about 34 of 80 cores).
- The about 0.5 GB of non-budget RSS per worker (arena retention, zstd
  contexts, reader buffers, request scratch) was never audited, and `--ram
  1GiB` with `unit-mult 8` was never restored for the phased configuration.
- Spill-side zstd at a scale where spilling is substantial is untested.
- `deduplicateRun`'s combine-call count and time per stage on a real kink run
  were never extracted; the collision rate and window width of real late-stage
  data are unmeasured.
- Two deferred cleanups in `orchestrator/sweep.go`: `mapPhase` and
  `mergePhase` are about 90% structurally duplicated, and `splitRemainder` does
  `.idx` I/O under the scheduler mutex on every steal.
- Hardware CRC32C in place of FNV-1a (10.6× on the hash, about 5% of compute)
  needs a cross-language format-version dispatch.
- IPC, cache-miss and branch-mispredict rates of the transfer-matrix workload
  were never captured (section 3.8).
- The disk-layer residuals of section 8: a body checksum that only prints, an
  unchecked last zstd frame, no manifest or `verify` pass on a(40) and a(41),
  and overflow guards that depend on `NSFLAGS` carrying no `-DNDEBUG`.

## Reproduce

Production runs and their validation (the driver's own validation compares
a(1..20) with `fixtures/b006770.txt` and the chain of recorded terms):

    scripts/term.sh N                    # one term; phased for N >= 40; --resume per phase
    FRONTIER_LEVERS=1 scripts/term.sh 40 # a(40) as run
    scripts/dalby_a41_low.sh                   # a(41) heights 1..19 at Nmax 41
    scripts/dalby_a41_h20.sh                   # a(41) height 20 at Nmax 41, 9.63 h on 76 cores
    python3 experiments/undertow_a41.py --jmax 5 --perheight results/a41
    scripts/kink_validate.sh                   # kink against column-kernel rows at maxn 29
    make gate-kink-oracle                      # kink at maxn 18, no injection, against a(1..18)
    make ns-gates                              # the engine gate suite, both ASan kernels
    make gates                                 # all gates; scripts/run_full_make.sh results/make_<topic>.log

Benchmarks and profiles:

    scripts/bench_util.sh <label> <maxn> <heights> # A/B harness; OVERLAP, MERGE_MULT parameters
    scripts/gympie_bench_phase.sh                  # H15/maxn30 on the laptop, 10 cores
    scripts/dalby_nmax_disk.sh                     # run-directory peak at Nmax 40/42/45
    POLY_UNIT_LOG=1 ... ; python3 scripts/analyze_unit_concurrency.py
    scripts/profile_concurrency.py                 # external sampler, production scale only
    POLY_STEAL_DEBUG=1 ...                         # trace every pickVictim decision
    GODEBUG=gctrace=1 ... ; POLY_MEMPROFILE=... ; go test -bench -benchmem ./orchestrator (sample_bench_test.go)
    experiments/reframe_measure.cpp                # frame-size curve on a real frontier file
    scripts/dalby_du_monitor.sh RUNDIR PID         # disk-footprint telemetry
    build/g2 square8 15                            # the Redelmeier profile target
    scripts/g2_fleet_launch.sh 22 12 24000 ; scripts/g2_combine.sh runs/g2row_N22 22 24000

Data: `results/ns_a26/cost_profile.tsv`, `results/ns_a27/cost_profile_dalby.tsv`,
`results/ns_a32/cost_profile_dalby.tsv`, `results/ns_a34/cost_profile_dalby.tsv`,
`results/a41/h20_cost_profile.tsv`, `results/dalby-perf-audit.png`,
`results/ns_a27/perheight/`, `results/ns_a26/triangle.txt`.
