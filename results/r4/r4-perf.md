# r4-perf — how much faster and smaller can the B1 residue engine be, without changing what it counts?

SCOUT, 2026-08-12. **No compute was run for this deliverable.** It is reading,
`git show`, read-only ssh to dalby, and arithmetic on numbers already on disk.
The one artifact produced is a C++ patch, written and dry-run-applied against a
clean `git show` copy with `patch --dry-run`; it has **never been compiled and
never been executed**.

Line numbers are for `48ac108:cpp/cutcount_b1.cpp`.

---

## 0. Verdict in five lines

1. **The dominant cost is a 64-bit `%` that is not needed at all on ~90% of
   edges.** `successors` emits `(m0,m1) = (1,0)` on every successor except the
   single fresh-colour one (lines 160, 165, 183 versus 184). On those edges the
   inner loop is `d = (d + c*1) % p` — an add and a conditional subtract, written
   as a division. Nothing in the code tells the compiler `m0 == 1`.
2. **Fixing that, plus three smaller things, is ~50 lines and buys an estimated
   2.5x** (range 1.8–3.5x, EXTRAPOLATED). The patch is written:
   `experiments/tristruct/r4_perf_fastmodp.patch`. Measuring it is PERF-JOB-1 (§4),
   ~25 minutes of dalby.
3. **After that the inner loop is memory-bandwidth bound at 656 B/edge, and no
   further single-thread arithmetic lever exists.** Everything past 2.5x has to
   come from moving fewer bytes (narrower payload) or from more cores.
4. **`Succ out[12]` does not overflow.** The true bound is `b <= floor((H+1)/2)`,
   so `ns <= floor((H+1)/2) + 2`: 12 at H=19 and H=20, exactly full, and 13 at
   H=21. r4-a §2.2's `floor((H+3)/2)` is one too high because it ignores the seam
   between the two column segments of the window. Argument in §3; it reproduces
   the source's own `<= 9 for H<=16` comment as a loose bound. **Widen the buffer
   and guard it anyway** — the patch does both.
5. **The repriced answer (§2): H=17 is under three hours, H=18 is a day, H=19 is
   a day on dalby with sharding, and H=20 is not compute-blocked — it is RAM-blocked
   by 21%,** at 147 GiB against dalby's 121 GiB free, with 564 GB of idle NVMe next
   to it. H=20 has stopped being a "no" and become a hardware question.

---

## 1. The ordered lever list

Cost basis for every "speedup" below is the MEASURED single-thread dalby wall of
the committed `--modp` (§1.0). Labels are per the brief: MEASURED, EXTRAPOLATED
(reasoned from a measured quantity), ASSERTED (reasoned from nothing measured
here). "By construction" means the transformation provably preserves the value;
"by intent" means it relies on a property nobody has checked.

### 1.0 The measurements this rests on

From `dalby:~/src/pm-b1/experiments/tristruct/r4_a_modp_bpw.log`, read
2026-08-12 23:3x EDT, single thread, `p = 2147483647`, committed 48ac108:

| H | windows (exact census) | modp wall s | modp peak RSS KB | exact I256 wall s | exact/modp |
|---|---|---|---|---|---|
| 13 | 306,858 | 188 | 358,556 | 503.4 | 2.68 |
| 14 | 891,074 | 600 | 979,596 | 1,618.6 | 2.70 |
| 15 | 2,624,197 | **2,065.1** | **2,420,292** | 5,134.5 | 2.49 |
| 16 | 7,832,667 | ~7,200 (in flight) | — | 16,475.2 | ~2.29 |

H=15's two figures are quoted verbatim from the log's own `event=done ...
wall_s=2065.1 ... peak_rss_mb=2363.6` and `/usr/bin/time -v`'s
`Maximum resident set size (kbytes): 2420292`. H=16 was at column 13 of 41 at
elapsed 2,074.9 s when I read it, with the last four inter-heartbeat intervals
at 178.3 / 174.9 / 175.5 / 175.5 s; 41 columns at that rate is **~7,200 s**.
That figure is PROJECTED from a partial run — replace it with the log's own
`wall_s=` when the job lands.

Two things follow immediately, and they point in opposite directions:

- **The exact/modp ratio is falling with H** (2.68 → 2.70 → 2.49 → ~2.29). The
  container is the same object in both modes, so the shared per-state cost is
  growing as a share of the total. **The container lever gets more valuable at
  exactly the heights we care about, and the arithmetic lever gets less.**
- **2.5x is far too small a gap for a payload that is 1/12th the bytes.** The
  exact path does 4 `iaddmul` calls per slot — 16 64x64 multiplies and 4 carry
  chains — and moves 3,936 B of payload per state against the residue path's
  328 B. If the residue path were not paying something enormous per slot, it
  would be 5–10x faster, not 2.5x. The something enormous is two 64-bit `udiv`
  per slot on a divider that does not pipeline. That is the inference the brief
  asked me to check against the loop, and the loop confirms the mechanism
  (lines 336–337) — but the *size* of the term is EXTRAPOLATED, and PERF-JOB-1
  measures it directly rather than by inference.

Derived cost constant `c(H) = wall / (windows x H)`, in seconds:
4.71e-5 (H=13), 4.81e-5 (14), 5.25e-5 (15), 5.75e-5 (16, projected). It grows
~9% per height above H=14 — cache pressure. Extrapolating at 1.09/height:
**6.26e-5 (17), 6.83e-5 (18), 7.44e-5 (19), 8.11e-5 (20).** Those drive §2.

RAM, same log: total B/window is **1,196.5 / 1,125.7 / 944.5** at H=13/14/15,
marginal slopes **1,088.5 (13→14) and 851.2 (14→15)**. Model payload is
2 buffers x 41 slots x 2 coeffs x 4 B = **656 B**, so the container residual is
540 / 470 / 288 B/window — *declining*, not the flat 270 B r4-a extrapolated from
the exact binary.

**On the 28% slope disagreement the brief flagged:** it is not a rehash
discontinuity. A rehash event is a step — one slope out of line, the others
agreeing. Here both the totals and the slopes decline monotonically, which is
per-state allocator and bucket-array overhead being amortized as the table grows.
The ladder-gate's ">15% means take the max and label it" rule fires, but taking
the max (1,088) is the wrong call: the constant is converging downward and the
right extrapolation constant for H >= 17 is the **top of the measured range**.
I use **944 B/window** (the H=15 total, conservative) throughout §2 and note that
851 is the central estimate. Predicted H=16 total, from the trend: ~880 B/window
= 6.4 GiB. The in-flight job settles it; if H=16 comes in above 944 this whole
paragraph is wrong and §2's RAM column is optimistic.

### L0 — the two mandatory fixes (no speedup; blocks everything)

`SUCC_MAX = 16` with a fail-closed `b + 2 > SUCC_MAX` abort, and the `H > 16`
guard raised to `H > 24` with its bounds in a comment. **5 lines, 15 minutes.**
Both are in the patch. Not optional and not a lever — H >= 17 does not run
without them.

### L1 — specialize the `(m0,m1) == (1,0)` edge — **the whole ballgame**

`successors` emits exactly four kinds of edge:

| edge | line | m0 | m1 | how many per state |
|---|---|---|---|---|
| empty cell | 160 | 1 | 0 | always 1 |
| join the unique live neighbour | 165 | 1 | 0 | 0 or 1 |
| join a non-adjacent existing block | 183 | 1 | 0 | b, when the cell is free |
| **fresh colour, weight q−b** | 184 | **−b** | **1** | at most 1 |

So `(m0, m1) = (1, 0)` on **every edge but one per state**. For those the inner
loop's `d0 = (d0 + c0*m0) % p` is `(d0 + c0) % p` with both operands already in
`[0,p)`, i.e. an add and one conditional subtract. The committed code spends two
64-bit `udiv` there instead, because `m0` is a runtime `int64_t` the compiler
cannot constant-fold.

- **Speedup: 2–3.5x, EXTRAPOLATED.** The reasoning is §1.0's second bullet: the
  divides are the only term big enough to explain a 2.5x-only gap against a
  12x-fatter payload. The measurement is PERF-JOB-1.
- **Size: ~20 lines, 1 hour.**
- **Semantics: preserving by construction.** Every stored coefficient is in
  `[0,p)` — true initially and preserved by every write in both the old and the
  new code — so `d + c < 2p < 2^32` cannot overflow a `uint32_t` and a single
  conditional subtract *is* `% p`. The patch states this invariant in a comment
  because it is the load-bearing fact.
- **Overlap: L1 subsumes most of L3.** After L1 only ~10% of edges reach any
  reduction at all, so Barrett/Montgomery/Shoup — the brief's first suspect — is
  worth roughly a tenth of what it would be worth alone. Do L1 first; L3 becomes
  a rounding error that is still worth its 15 lines.

One risk, and it is the reason the measurement matters: L1's loop drops the
`if (!(c0|c1)) continue;` zero-skip, because a branchless contiguous add
vectorizes and a data-dependent branch does not. If the payload's active
fraction is low the branchless version does more work per edge. The output is
identical either way (adding zero); only the wall moves, and it could move the
wrong way. PERF-JOB-1 resolves it at H=13/14 for 13 minutes of dalby.

### L2 — structure-of-arrays payload layout

Store `c0[0..Nmax]` then `c1[0..Nmax]` instead of interleaving them. L1's common
edge then becomes two contiguous 164-byte modular vector adds, which NEON does
4 lanes at a time (`vaddq_u32`, `vsubq_u32`, `vminq_u32` for the conditional
subtract), and which the compiler will emit without intrinsics.

- **Speedup: 1.3–2x on top of L1, EXTRAPOLATED** from lane width (4x u32 per
  128-bit NEON register) discounted for load/store and loop overhead.
- **Size: ~10 lines, 30 minutes.** In the patch.
- **Semantics: by construction** — pure reindexing of the same values.
- **Overlap:** worthless without L1 (the interleaved multiply-and-reduce loop
  does not vectorize); L1 is worth noticeably less without it.

### L3 — Shoup reduction on the fresh-colour edge

`w = floor(m0 * 2^64 / p)` computed once per edge and amortized over the area
slots; then `r = m0*c − floor(w*c/2^64)*p` lies in `[0,2p)`. Two multiplies and a
conditional subtract instead of a divide. Exact for `m0, c < p < 2^63`, which
holds (`p < 2^31` is enforced at line 377).

- **Speedup: ~1.1x after L1, EXTRAPOLATED.** It only sees one edge in ten.
- **Size: ~15 lines, 30 minutes.** In the patch.
- **Semantics: by construction**, on the standard Shoup bound.
- Note this is the *general* answer to the brief's "Montgomery or Barrett with a
  compile-time prime". Shoup is strictly better here because the multiplier is
  loop-invariant across the 41 slots, and it needs no compile-time prime, so one
  binary still serves all five primes.

### L4 — lazy reduction in the column sum

Line 347 does `fcur[t] = (fcur[t] + P[t]) % p` — 82 divides per state per column,
82 x 41 = 3,362 per state per run. Against the *current* inner loop that is ~1%;
against the post-L1 inner loop it is ~10%. Accumulate raw in `uint64_t` and
reduce once per column.

- **Speedup: 1.05–1.10x after L1, EXTRAPOLATED.**
- **Size: 5 lines, 10 minutes.** In the patch.
- **Semantics: by construction while `states x (p−1) < 2^64`,** i.e. fewer than
  2^33 states. The patch checks it and exits 2, rather than assuming it.

**L1+L2+L3+L4 = the patch = PERF-JOB-1. Combined estimate 2.5x, range 1.8–3.5x,
EXTRAPOLATED. ~50 lines, ~2.5 hours of authoring, all of it written already.**
They do not multiply: L2 only multiplies L1, L3 and L4 only apply to what L1
leaves behind. 2.5x is my central number for the four together, not the product
of their individual ranges.

### L5 — flat open-addressed container with a payload arena

Replace `unordered_map<u128,uint32_t>` + `vector<vector<uint32_t>>` with an
open-addressed `(u128 key, u32 index)` table at ~0.7 load factor and a single
flat `uint32_t` arena of `states x 82`. This removes, per new state per
`(r,c)` step: one node malloc, one 328-byte payload malloc, the matching frees,
and a 328-byte `memset` — at H=17 that is 23.7M x 697 steps x 2 malloc/free pairs.

- **RAM: 944 → ~716 B/window, 1.32x, EXTRAPOLATED.** The 288 B/window container
  residual measured at H=15 decomposes as ~96 B of libstdc++ nodes (two tables,
  40-byte nodes rounded to 48 by glibc), ~32 B of bucket array, ~48 B of outer
  `vector` handles, ~32 B of heap-block headers and ~48 B of allocator slack on
  the 328-byte chunks. A flat table at 0.7 load is ~29 B/entry x 2 = 57 B and
  the arena has no per-state overhead at all.
- **Speedup: 1.2–1.4x, EXTRAPOLATED**, from removing the allocator traffic and
  improving locality.
- **Size: ~150 lines, 6–10 hours.**
- **Semantics: by construction.** State identity is the *key*; the integer index
  is internal and never reaches the output. Accumulation into the table is
  modular addition, which is commutative and associative, so the final payload
  per key is independent of insertion order and of index assignment.
- **Overlap: L5 is the prerequisite for L7.** You cannot shard a container that
  mallocs per insertion.

### L6 — narrow the payload to u16 (RAM lever, wall-neutral)

**This is the correction to r4-a §2.7.** r4-a priced narrowing as RAM against
run count and concluded it buys 2.1x RAM for 3.2x more runs. It missed the third
term: once L1–L4 land the loop is bandwidth-bound at 656 B/edge, so halving the
payload also **halves the wall per run**. The two effects nearly cancel.

| payload | B/window (flat) | RAM vs flat-u32 | wall/run | runs (bit budget 112 + held-out) | total wall |
|---|---|---|---|---|---|
| u32, p < 2^31 | 716 | 1.00x | 1.00 | 4+1 = **5** | 1.00x |
| u16, p < 2^16 | 388 | **1.85x better** | ~0.61 | 7+1 = **8** | **0.98x** |
| u8, p < 2^8 | 224 | 3.20x better | ~0.42 | 14+1 = **15** | 1.26x |

- **u16 is a free 1.85x on RAM at wall parity. u8 buys 3.2x on RAM for ~26% more
  wall.** Both EXTRAPOLATED — the wall column assumes fully bandwidth-bound,
  which is only true after L1–L4.
- **Size: ~10 lines, 1 hour** once L1–L3 are in (the Shoup path already keeps its
  intermediates in u32/u64).
- **Semantics: by construction for the DP.** It changes the primes, hence the
  residues, hence the CRT — the reconstruction is covered by RED-D, not by this.
- **Overlap: u16 is what makes H=19 fit dalby** (§2). Below H=19 it is not needed.

### L7 — shard across cores

Block-synchronous scatter. Partition *targets* by a hash of the successor key
into T shards. Threads take blocks of ~1M source states from a shared cursor,
run `successors`, and append `(source index, target key, m0, m1, dn)` — 32 B —
into per-(thread, shard) buffers. Then each shard has exactly one owner thread
that applies its buffered edges. Buffer footprint is bounded by the block size:
1M sources x ~5 edges x 32 B = 160 MB, regardless of H.

What in *this* code makes it easy, specifically:

- The only mutation is `+=` into a key-indexed table. Modular addition is
  commutative and associative, so **the result is bit-identical under any thread
  schedule** — this is semantics-preserving *by construction*, not by intent, and
  it is the strongest such argument on this list.
- `successors`, `gather`, `canon` and `shifted` are already pure functions of
  `(key, H, r, c)` with no shared state (lines 135–186). Nothing to make
  thread-safe.
- The `(r,c)` loop is a hard barrier, so there is exactly one synchronization
  point per step and no fine-grained locking anywhere.

What makes it hard: `std::unordered_map` and the per-state `vector` payload have
to go first (L5), and the source payload is read by whichever thread owns the
edge, so the source buffer must stay resident and read-only for the whole step —
which it already is.

- **Speedup: 8x on ayr (32 cores), 15x on dalby (80 cores). ASSERTED.** Not 32x
  and 80x, because after L1–L4 the loop is bandwidth-bound and server memory
  systems deliver roughly 10–20x a single core's streaming bandwidth, not
  core-count x. **dalby's actual memory bandwidth is NOT ESTABLISHED** and I have
  measured nothing here. r4-a's queue row R4-A4 already proposes the right probe:
  2/4/8 threads at H=14, 27 minutes.
- **Size: ~300 lines, 20–30 hours.**
- **Overlap:** L7 is where the RAM-bound heights get their wall back. At H=18
  and above only one run fits in RAM at a time, so the "5 primes concurrently,
  1 core each" plan is unavailable and single-run parallelism is the *only*
  lever. This is why L7 outranks everything except the patch despite costing a
  week.

### L8 — the transition structure is identical for every column c >= 1

`successors` depends on `c` only through `c > 0` (line 142), and `gather`
likewise. So for every `c >= 1` the edge relation at row `r` is the same
relation, and the reachable state set `S_r` saturates after the second column.
The DP is therefore **the same fixed sparse matrix applied 39 more times**, and
39/41 of all hashing, `canon` and `shifted` work is redundant.

Cache the CSR edge list per row `r` and reuse it across columns: no hash lookups
in the inner sweep at all, and the update becomes a fixed sparse matvec of
41-slot vectors — the ideal shape for both SIMD and L7.

- **Speedup: removes whatever share transition generation and hashing hold —
  NOT ESTABLISHED.** Plausibly 20–40% after L1–L4, when the arithmetic no longer
  dominates. Nobody has profiled this binary.
- **RAM cost is what kills it at scale:** H edge lists at ~8 B/edge is 16 GiB at
  H=17, 52 GiB at H=18, **171 GiB at H=19**. It is an H <= 18 lever.
- **Size: ~250 lines, 15 hours.**
- **Semantics: by intent, not by construction** — it assumes `S_r` is
  c-independent. Make it by construction by having the code compare the key-set
  size and an order-independent checksum between consecutive columns and exit 2
  on any difference. With that check I would trust it; without it I would not.
- Worth noting for the *other* mission: a fixed matrix per row is a more
  proof-shaped object than a hash table is. It is the version of this engine a
  skeptical reader could be handed.

### L9 — fuse the primes into one pass

Run k primes in a single sweep sharing one container, one set of hash lookups
and one `successors` call. Payload becomes k x 82 words.

- **Speedup 1.2–1.5x, EXTRAPOLATED**, and it grows as L1–L4 shrink the
  arithmetic share.
- **Size: ~30 lines, 2 hours.**
- **Semantics: by construction** — k independent DPs sharing a traversal.
- **Overlap: it competes with L6 and L7 for the same RAM and the same cores.**
  Only worth it at H=17, where 5 fused primes at flat-u32 are 73.6 GiB and fit
  dalby. Above that, RAM says no.

### L10 — park the source buffer on NVMe (the only lever that reaches H=20)

With L8's fixed index order the source payload is read in index order, i.e.
sequentially. dalby has **564 GB free on `/`**. Keep the target buffer in RAM and
stream the source from NVMe.

- **ASSERTED, nothing measured:** at H=20 flat-u8 this trades 73 GiB of RAM for
  ~120 TB of sequential I/O per prime, roughly 11 h at 3 GB/s.
- **It also writes ~120 TB per prime.** That is a real fraction of a consumer
  NVMe's rated endurance and it is jasonp's call, not a free lunch. I flag it and
  do not recommend it.

### Levers I checked and rejected

- **Drop the `c0` coefficient.** Impossible: `d1 += c0*m1` couples them (line 337,
  and the algebra of `(q − b)` in `Z[q]/(q^2)`).
- **61-bit primes** (r4-a §2.7 called this a rewrite). With Shoup it is now a
  5-line change — but it doubles the payload to save 2 of 5 runs, which is 1.2x
  worse on RAM and, once bandwidth-bound, ~1.2x worse on wall. Reject.
- **Range-restricted area slots.** The support in `n` is only narrow for the
  first two or three columns (at column c at most `c*H + r` cells are placed);
  by c=3 at H>=15 the range is full and the state count — hence the weight — is
  still tiny. Worth under 1%. Reject.
- **Compile-time prime via `-DPRIME=`.** Subsumed by L3 at no build-matrix cost.

### Validation cost, folded in

Every optimized binary owes `tests/gate_cutcount_b1.py` (~7 s, seven checks,
three REDs) plus the RED-modp oracle. Those are not equal in cost and should not
be treated as one item:

- **Per intermediate build: bit-exact row diff at H=13 and H=14** against the
  rows the current job is producing. ~13 minutes of dalby, and it is a *stronger*
  check than the gate for these levers, because every one of them claims
  bit-identical output rather than merely correct output.
- **Once, for the binary that goes to production: the H=16 oracle run** against
  `results/cutcount_b1/rows/C16.out` reduced mod p — ~2 h at as-is speed,
  production state count. Do not pay this per lever.

---

## 2. Repriced H=17..20

Three scenarios. **As-is** = committed `--modp` + L0. **Cheap** = + the patch
(L1–L4), 2.5x. **Everything** = + L5 (flat, 1.3x wall, 716 B/w) + L6 (u16 where
RAM demands it) + L7 (8x ayr / 15x dalby).

Boxes as checked 2026-08-12 in the ladder gate: **ayr 77 GiB free / 32 cores;
dalby 121 GiB free / 80 cores / 564 GB free NVMe.**

### RAM per run, GiB

| H | windows | as-is 944 B/w | flat u32 716 | flat u16 388 | flat u8 224 |
|---|---|---|---|---|---|
| 17 | 23,681,423 | 20.8 | 15.8 | 8.6 | 4.9 |
| 18 | 72,487,711 | 63.7 | 48.3 | 26.2 | 15.1 |
| 19 | 224,529,648 | 197.4 | 149.7 | **81.1** | 46.8 |
| 20 | 703,470,478 | 618.5 | 469.1 | 254.2 | **146.8** |

### Wall, single thread, per prime, hours

From `c(H)` in §1.0. As-is is EXTRAPOLATED from four MEASURED points; the rest
apply the lever factors.

| H | as-is | cheap (÷2.5) | everything, 1 thread (÷2.5 ÷1.3 ÷payload) |
|---|---|---|---|
| 17 | 7.0 | 2.8 | 2.2 (u32) |
| 18 | 24.8 | 9.9 | 7.6 (u32) |
| 19 | 88.2 | 35.3 | 17.0 (u16) |
| 20 | 316.9 | 126.8 | 41.4 (u8) |

### Total wall for a full 5-run (or 8/15-run) reconstruction

| H | as-is | cheap levers only | everything |
|---|---|---|---|
| **17** | 5 x 20.8 = 104 GiB, dalby holds all five: **7.0 h** | **2.8 h** | 5 fused or 5 x 16 cores: **~0.3 h** |
| **18** | 63.7 GiB/run — 1 on dalby + 1 on ayr, 3 waves: **74 h** | **30 h** | 3 concurrent (2 dalby + 1 ayr), 2 waves: **~2 h** |
| **19** | u32 does not fit anywhere; u8 fits dalby alone, 15 runs: **55 days** | **22 days** | flat u16, 81.1 GiB, dalby sole-tenant, 80 cores, 8 runs x 1.13 h: **~9 h** |
| **20** | out of RAM everywhere | out of RAM everywhere | flat u8 = **146.8 GiB vs 121 free — short by 21%.** Compute would be ~1.7 h total. |

**What changed against r4-a §4.3.** r4-a priced the ladder off the *exact* I256
walls as upper bounds, because it explicitly refused to guess the residue
speedup. The residue walls are now measured and they are 2.5x below those
anchors, which alone takes H=19 from 104 days to 55. The levers take it to a day.
H=17 and H=18 were never the problem and are now trivial.

**The finding I did not expect: H=20 is no longer compute-blocked.** At flat-u8
with sharding the arithmetic is under two hours. It is short 26 GiB of RAM on a
box with 564 GB of free NVMe. That is a different kind of problem from the one
the ladder-gate recorded, and a much more tractable one.

**Caveats that could move these numbers.** The 2.5x is EXTRAPOLATED and
PERF-JOB-1 measures it. The 15x sharding factor is ASSERTED and nothing here
measures it — if it is really 5x, H=19 is 27 h rather than 9 h, which does not
change the verdict; if the DP does not shard at all, H=19 stays out and only
H=17/18 land. The RAM column uses 944 B/window, which the in-flight H=16 point
will confirm or break.

---

## 3. `Succ out[12]` — settled by argument: safe through H=20, overflows at H=21

**Claim: `b <= floor((H+1)/2)`, hence `ns <= floor((H+1)/2) + 2`.**

| H | b | entries written | out[12] |
|---|---|---|---|
| 16 | 8 | 10 | fits, 2 spare |
| 17 | 9 | 11 | fits, 1 spare |
| 18 | 9 | 11 | fits, 1 spare |
| 19 | 10 | **12** | fits, **0 spare** |
| 20 | 10 | **12** | fits, **0 spare** |
| 21 | 11 | 13 | **overflows** |

**The invariant.** Every reachable key has the property that king-adjacent
occupied cells carry the same block id. It holds for the initial key 0, and
`successors` preserves it: `nb >= 2` returns without emitting a successor
(line 163, the clash), `nb == 1` gives the new cell that unique id (165), and
`nb == 0` means the new cell has no occupied neighbour at all, so whatever id it
takes — an existing non-adjacent one (183) or a fresh one (184) — cannot violate
it. So **distinct ids in a window are pairwise non-king-adjacent**, and `b` is
bounded by the maximum independent set of the window's king graph.

**The window's geometry.** Slot `k` is the cell processed `k+1` cells ago, and
cells are processed column-major. For the current cell `(r,c)` with `r >= 1`, the
`H+1` slots are exactly: column `c` rows `0..r-1` (slots `0..r-1`), then column
`c-1` rows `r-1..H-1` (slots `r..H`). This is checkable against `gather`, which
pushes slot 0 = `(r-1,c)` (up), slot `H-1` = `(r,c-1)` (left), slot `H-2` =
`(r+1,c-1)` (down-left) and slot `H` = `(r-1,c-1)` (up-left) — the four already-
placed king-neighbours, and they land where this parametrization says they do.

So the window is two vertical runs, `A` in column `c` over rows `[0, r-1]` and
`B` in column `c-1` over rows `[r-1, H-1]`, **overlapping at row r-1**. Within a
run, adjacent rows are king-adjacent, so each run contributes at most
`ceil(length/2)`. Across runs, `(i,c)` and `(j,c-1)` are king-adjacent iff
`|i-j| <= 1`, which given the row ranges bites only on the pairs
`(r-1,r-1)`, `(r-1,r)`, `(r-2,r-1)` — **the seam**.

**Where r4-a's bound loses one.** Ignoring the seam gives
`ceil(r/2) + ceil((H+1-r)/2)`, whose maximum is `floor((H+3)/2)` — r4-a's figure.
But for odd H at odd r, both runs attain their maxima *uniquely*: `A` must be
`{0,2,...,r-1}` and `B` must be `{r-1,r+1,...,H-1}`, and both contain row `r-1`,
which is the same row in two horizontally adjacent columns. They cannot both be
achieved. Enumerating the three ways to break the seam —

- `A` keeps `r-1`, so `B` must avoid `r-1` and `r`: `ceil(r/2) + ceil((H-r-1)/2)`
- `A` keeps `r-2` not `r-1`, so `B` must avoid `r-1`: `ceil((r-1)/2) + ceil((H-r)/2)`
- `A` avoids both, `B` free: `ceil((r-2)/2) + ceil((H-r+1)/2)`

— every branch maxes at `floor((H+1)/2)` for every `r in [1, H-1]`. The `r = 0`
case is a different shape (the window is all of column `c-1` plus `(H-1,c-2)`)
and gives the same value: `ceil(H/2)` for the column alone, or `1 + ceil((H-2)/2)`
if the stray cell is used, both `floor((H+1)/2)` at odd H.

**Two checks that the argument is not confused.** At H=16 it gives `b <= 8`,
consistent with — and tighter than — the source's own `<= 9 for H<=16` comment at
line 96. At H=2 it gives `b <= 1`, and the H=2 window is `(0,c)`, `(0,c-1)`,
`(1,c-1)`, which are mutually king-adjacent, so 1 is exactly right.

**What I recommend anyway.** The verdict is "safe with zero headroom at exactly
the heights the ladder wants", which is not a state a fail-closed codebase should
ship in. The patch widens the buffer to `SUCC_MAX = 16` and adds an explicit
`b + 2 > SUCC_MAX` abort in `successors` — 5 lines, no measurable cost (it is one
compare in the `nb == 0` branch, once per state per step, against ~3,500 slot
operations). **Then r4-A2's probe is no longer a blocker but is still worth its
seconds:** run `--states 17 21 41` with the guard compiled in and confirm it does
not fire at H=17..20 and *does* fire at H=21. That turns my case analysis into a
red-and-green pair, which is what this project's standard actually asks for.

R4-A2 can be closed on this argument. It should not be closed on this argument
*without* the guard.

---

## 4. JOB REQUEST — PERF-JOB-1

The measurement that most changes the answer. Every entry in §2's "cheap" and
"everything" columns is downstream of the single number this produces, and it
costs 25 minutes.

    job id:            PERF-JOB-1
    measures:          the wall of the L1-L4 patched --modp at H=13,14,15 on
                       dalby, one thread, p=2147483647, against the MEASURED
                       baselines 188 / 600 / 2065.1 s taken on the same box with
                       the same prime hours earlier. Output is the speedup factor
                       of the arithmetic levers, which is currently the largest
                       EXTRAPOLATED number in this deliverable.
    decides:           (a) whether the 2.5x central estimate holds, and therefore
                       whether H=19's "one dalby day" is real or whether the
                       remaining budget has to come out of sharding;
                       (b) whether dropping the zero-skip for a branchless
                       vectorized add is a win or a regression (the one way this
                       patch can be slower rather than faster);
                       (c) whether to spend the 6-10 hours on L5 and the 20-30 on
                       L7 at all. If the patch lands under 1.5x, the divides were
                       not the cost, the container was, and the whole ranking in
                       section 1 inverts.

    prerequisite:      WAIT for the in-flight r4_a_modp_bpw job to finish. The
                       baselines were taken on an otherwise-idle dalby and this
                       comparison is bandwidth-sensitive; running alongside the
                       H=16 job would contaminate both. Not a core-count issue --
                       dalby has 80 -- a shared-memory-bandwidth issue.

    box:               dalby, and dalby specifically. Same reason as LG-JOB-1R:
                       every number this is compared against was measured there,
                       on that ISA, with that allocator. A speedup measured on ayr
                       against a dalby baseline would be uninterpretable.
    cores:             1

    patch:             experiments/tristruct/r4_perf_fastmodp.patch
                       Written by r4-perf, NEVER COMPILED, NEVER RUN. Applies
                       cleanly to 48ac108:cpp/cutcount_b1.cpp -- verified with
                       `patch --dry-run -p1` against a clean `git show` copy, and
                       that is the only thing about it that has been verified.
                       Expect it to need a compile fix; read it before trusting it.
                       It contains L0 (SUCC_MAX=16 + abort, H<=24 guard) and
                       L1-L4 (edge specialization, SoA layout, Shoup, lazy column
                       sum). It does NOT contain L5-L10.

    build:             cd ~/src/pm-b1
                       git stash list            # expect empty; this tree is 48ac108
                       patch -p1 < experiments/tristruct/r4_perf_fastmodp.patch
                       make build/cutcount_b1
                       sha256sum build/cutcount_b1        # record in the receipt
                       python3 tests/gate_cutcount_b1.py  # ~7 s, must be GREEN

    run:               P=2147483647
                       mkdir -p results/cutcount_b1/modp_fast
                       for H in 13 14 15; do
                         /usr/bin/time -v ./build/cutcount_b1 --modp $H 40 $P \
                           results/cutcount_b1/modp_fast/C$H.p$P.out
                       done
                       # THE control: bit-exact, not merely correct
                       for H in 13 14 15; do
                         cmp results/cutcount_b1/modp/C$H.p$P.out \
                             results/cutcount_b1/modp_fast/C$H.p$P.out
                       done
                       (all under tee to
                        experiments/tristruct/r4_perf_fastmodp.log, tmux on dalby)

    wall estimate:     <= 50 min. MEASURED upper bound: the unpatched walls sum to
                       2,853 s = 48 min and the patch cannot plausibly be slower
                       than 1x on all three heights. EXTRAPOLATED expectation
                       ~19 min at 2.5x. Budget the upper bound.
    RAM estimate:      2.4 GiB peak at H=15. MEASURED -- the patch changes the
                       payload layout, not its size.
    disk estimate:     < 100 kB (3 row files of 40 lines + the log)
    interruptible:     yes, one file per height; a kill costs at most 35 min.

    RED controls:
      RED-exact  `cmp` against the unpatched rows from the same box, same prime,
                 must be byte-identical at all three heights. This is the whole
                 semantics argument of L1-L4 made executable: every one of them
                 claims to preserve the value bit for bit, not merely to compute
                 something correct, so a diff of one byte falsifies the patch.
                 Its RED half: flip one digit in one row file and confirm `cmp`
                 reports it. Do that first.
      RED-gate   tests/gate_cutcount_b1.py, all seven checks including the three
                 REDs. Note it covers the EXACT paths only -- the patch does not
                 touch them, so a gate failure here means the patch broke
                 something it had no business touching, which is exactly the
                 signal wanted.
      identities `q0_zero` fires per height in modp (line 356, exit 2). The q=1
                 binomial identity is still absent in modp (r4-a section 1b);
                 record that as a known gap in the receipt rather than letting
                 the log's silence imply it passed.
      guard      the new `FATAL succ_overflow` and `FATAL m1_not_bit` aborts must
                 NOT fire at H<=15. If either does, my section 3 analysis or my
                 reading of the weight table is wrong and everything downstream
                 of it is suspect.

    changes if:        >= 2.5x  -> build L5 then L7; section 2's "everything"
                                   column stands and H=19 is a one-day job.
                       1.5-2.5x -> section 2 stands with H=19 nearer two days;
                                   still build L5 and L7.
                       < 1.5x   -> the divides were not the cost. Re-rank: L5
                                   (container) becomes lever 1, and the falling
                                   exact/modp ratio in section 1.0 was the real
                                   signal all along. Profile before building L7.
                       slower   -> the zero-skip mattered; restore it inside L1's
                                   loop (loses vectorization, keeps the divide
                                   removal) and re-measure. 10 minutes.
    closes:            the largest EXTRAPOLATED number in this deliverable, and
                       r4-A2's memory-safety half by exercising the new guard.

---

## 5. Queue rows filed

Appended to `results/r4/queue.md`: **R4-P1** (this job request), **R4-P2**
(closes R4-A2 by argument plus guard), **R4-P3** (the c >= 1 transition
invariance, a structural row not a speed row), **R4-P4** (H=20 is RAM-blocked by
21%, a hardware row).

---

## NOT ESTABLISHED

- **Every speedup factor in section 1.** L1's 2–3.5x is the reasoned consequence
  of a measured ratio, not a measurement; L2's, L3's, L4's and L5's are reasoned
  from instruction counts and allocator behaviour. PERF-JOB-1 measures L1–L4
  together and nothing measures them apart.
- **Whether this DP shards, and by how much.** L7's 8x/15x is ASSERTED. dalby's
  memory bandwidth is unmeasured and so is any multi-threaded run of this engine.
  R4-A4's H=14 thread-scaling probe is still the right first move and is
  unaffected by anything here.
- **The share of the wall held by transition generation and hashing.** Nobody has
  profiled this binary. L8's value and L9's both depend on it, and both are
  ranked on reasoning alone.
- **H=16's residue wall and peak RSS.** Projected from 13 of 41 columns. Section 2's
  `c(H)` extrapolation and its 944 B/window constant both tighten or break when
  the in-flight job lands.
- **The maximum of `b`, measured.** Section 3 is an argument. It reproduces two
  independent checks (the source's H<=16 comment, and H=2 by hand) but it has not
  been run.
- **Whether the patch compiles.** It has not been built. It has been read, and it
  applies cleanly to 48ac108. That is all.
- **Whether dalby's RAM, cores and NVMe are free at build time.** Checked
  2026-08-12 in the ladder gate only, and there is a job on the box right now.
