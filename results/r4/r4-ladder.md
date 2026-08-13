# r4-ladder — what is the real plan for H=17, 18 and 19?

SCOUT, 2026-08-13. **No compute was run for this deliverable.** It is reading,
read-only ssh to dalby, and arithmetic on numbers already on disk. Every table
below is reproducible from `r4_a_modp_bpw.log` (baseline), `r4_perf_job1.log`
(patched), the exact censuses in `r4-perf.md` §2, and `results/triangle.txt`.

Line numbers for `successors`/`gather` are for
`results/cutcount_b1/cutcount_b1.cpp.59e90660`, which is byte-identical to
`48ac108` over that block (r4-a's diff finding, re-checked by eye here).

---

## 0. Verdict in six lines

1. **The patch is measured, real, and small: 1.282 / 1.234 / 1.122 at H=13/14/15,
   declining.** Bit-identical rows at all three heights. This is r4-perf's own
   `< 1.5x` branch and it says, in that lane's words, *"the divides were not the
   cost, the container was, and the whole ranking in section 1 inverts."* The
   branch fired. §1.
2. **But the brief's proposed inversion — payload narrowing to the top — does not
   follow, and I argue against it.** The loop is not at the bandwidth roof; on
   r4-adv-cost's own MEASURED 2.56 GB/s it is at a quarter of one core's
   streaming ceiling. The binding constraint is **random-access memory latency**
   (hash probe + page walk), not streamed bytes. Narrowing halves bytes but not
   probes and not page walks. §2.
3. **The successor bound is `b <= floor((H-1)/2)`, one tighter than r4-perf and
   two tighter than r4-a. `Succ out[12]` is safe through H=22.** Both lanes
   bounded `b` by the independent-set number of the whole window; the code only
   writes `b+2` entries inside `if (nb == 0)`, the branch where the four
   king-neighbours of the current cell are *known empty*. Removing them from the
   window breaks the seam entirely. Airtight; no probe needed; the fail-closed
   abort already compiled into `pm-b1-perf` is the RED and has already run clean.
   §3.
4. **The single biggest finding is not a lever at all — it is that the ladder is
   a *confirmation*, not a *reconstruction*, and that cuts the cost 5x.**
   `results/triangle.txt` already holds `T(n,17)`, and `C_15`/`C_16` are banked
   exact. So one prime per height *predicts* `C_H(n) mod p` for all 40 values of
   n before the run starts. No CRT, no bit budget, no RED-D held-out prime, no
   16-prime u8 arithmetic. r4-a §2.5 and r4-adv-cost §3 both priced the ladder as
   reconstruction; the round's own goal statement says *confirm*. §4.1.
5. **Re-derived, MEASURED-anchored, no-new-code plan: H=17 is 6.6 h and 20.8 GiB;
   H=18 is 22.7 h and 63.8 GiB. Two primes each, run concurrently across dalby
   and ayr, is ~30 h of wall for 16.48% of a(40).** H=19 is 79.3 h and 197.6 GiB
   and fits nothing — it needs the flat container plus narrowing to fit RAM at
   all, and it is the only one of the three that is a project. §1, §4.
6. **The oracle does not run out at H=16 the way the brief fears.** The *exact
   B1 binary* stops at H=16, but the TM table does not — `T(n,H)` is banked to
   H=40, and the whole point of B1 is that it computes it by a rule that never
   decides connectivity. The honest weak point is different and narrower, and I
   name it in §4.4: agreement confirms, it does not reconstruct, and a
   *systematic* error shared by both rules is not caught by any number of primes.

---

## 1. Re-derived cost table for H=17, 18, 19

### 1.1 The anchors, all MEASURED

Unpatched `--modp`, dalby, single thread, `p = 2147483647`, from
`dalby:~/src/pm-b1/experiments/tristruct/r4_a_modp_bpw.log` `event=done` lines
and `/usr/bin/time -v` max-RSS, read 2026-08-13:

| H | windows | wall s | max RSS KB | B/window |
|---|---|---|---|---|
| 12 | 107,241 | 53.2 | 117,624 | 1,123.1 |
| 13 | 306,858 | 188.2 | 358,556 | 1,196.5 |
| 14 | 891,074 | 599.5 | 979,596 | 1,125.7 |
| 15 | 2,624,197 | 2,065.1 | 2,420,292 | 944.4 |
| 16 | 7,832,667 | **6,864.1** | **7,209,816** | **942.6** |

Patched (`pm-b1-perf`, L0+L1–L4), same box, same prime, from
`dalby:~/src/pm-b1-perf/experiments/tristruct/r4_perf_job1.log`:

| H | patched wall s | speedup | patched peak RSS MB | baseline peak RSS MB | rows |
|---|---|---|---|---|---|
| 13 | 146.8 | **1.2820** | 302.8 | 350.2 | IDENTICAL |
| 14 | 485.8 | **1.2340** | 959.1 | 956.6 | IDENTICAL |
| 15 | 1,840.7 | **1.1219** | 2,355.9 | 2,363.6 | IDENTICAL |

`cmp_failures=0`. The patch is value-preserving at production-ish scale and
**RAM-neutral** — the SoA relayout moved no bytes, which matters for §2.

### 1.2 The growth fit, and its residuals

`c(H) = wall / (windows × H)`, seconds:

| H | 12 | 13 | 14 | 15 | 16 |
|---|---|---|---|---|---|
| c(H) ×10⁵ | 4.1340 | 4.7178 | 4.8056 | 5.2463 | **5.4771** |

Log-linear least squares over the five MEASURED points gives
`c(H) = 4.2458e-5 × 1.06917^(H−12)`.

**Growth ratio fitted: g = 1.06917 per height.** Residuals (measured ÷ fitted):
0.9737, 1.0393, 0.9901, 1.0110, 0.9872 — **max deviation 3.9%, no trend in
sign.** Five points over a 129x range in windows; I am comfortable extrapolating
three heights on it and I would not extrapolate six.

Two corrections to lanes that fitted this before me:

- **r4-perf's "~9% per height"** was one interval (14→15). r4-adv-cost caught
  that and offered 1.0743 as the geometric mean — but off its *projected* c(16)
  of 5.506e-5. With H=16 now MEASURED at 5.4771e-5, the geometric mean is
  1.0729 and the least-squares slope is 1.06917. I use 1.06917. The difference
  costs 3% at H=19 and nothing decides on it.
- The extrapolation is anchored on the **measured** c(16), not the fitted one
  (the fit sits 1.3% high there). Anchoring on the fit raises every wall below
  by 1.3%.

### 1.3 The patch factor at H ≥ 17 — I bank none of it

MEASURED: 1.2820, 1.2340, 1.1219. In logs: 0.2484, 0.2102, 0.1150 — differences
−0.0382 then −0.0952. **The decline is accelerating, not flattening.** Naive
log-linear continuation puts the factor at ~1.02 by H=16 and below 1.0 by H=17,
which is certainly over-extrapolation from three points; a patch that removes
work cannot make the program slower on this evidence (it did not at any measured
height, and the guard is one compare per state).

So I plan on **1.00 and quote 1.12 as the optimistic bracket**, and I will not
pretend to a central estimate between them from three points:

| H | patch factor used | basis |
|---|---|---|
| ≤15 | 1.28 / 1.23 / 1.12 | MEASURED |
| 16 | 1.02–1.12 | EXTRAPOLATED, unmeasured, and cheap to measure |
| 17–19 | **1.00** planning, 1.12 optimistic | EXTRAPOLATED |

Banking 1.12 rather than 1.00 changes H=17 from 6.6 h to 5.8 h. It decides
nothing, which is exactly why the arithmetic lever is over.

### 1.4 The walls

`wall = c(16) × 1.06917^(H−16) × windows × H`, unpatched, single thread, dalby.
**EXTRAPOLATED from five MEASURED points; ±4% is the residual band of the fit,
and the extrapolation error over three heights is larger than that and not
quantified.**

| H | c(H) ×10⁵ | windows | wall/prime, s | wall/prime, h |
|---|---|---|---|---|
| 17 | 5.8560 | 23,681,423 | 23,575 | **6.55** |
| 18 | 6.2611 | 72,487,711 | 81,694 | **22.69** |
| 19 | 6.6942 | 224,529,648 | 285,579 | **79.33** |
| 20 | 7.1573 | 703,470,478 | 1,006,985 | 279.72 |

### 1.5 The RAM constant — the H=16 point breaks the declining story

Marginal B/window from the `/usr/bin/time` max-RSS column:

| interval | B/window |
|---|---|
| 12→13 | 1,235.9 |
| 13→14 | 1,088.5 |
| 14→15 | 851.2 |
| **15→16** | **941.6** |

**It is not monotone.** r4-perf's §1.0 argued "both the totals and the slopes
decline monotonically, which is per-state allocator and bucket-array overhead
being amortized", and r4-adv-cost §1.2 endorsed it — *"monotone over three
intervals with no step anywhere"* — and predicted ~880 B/window at H=16. The
measurement is 942.6 total, 941.6 marginal. **The 851 was the outlier; the
sequence is converging on ~942, not declining through it.**

The step that fails: the amortization story predicts a *monotone* limit, and a
non-monotone fourth point falsifies it without replacing it. What the data now
supports is much simpler and better for planning — a **flat** asymptote at
**945 B/window**, i.e. the 656 B model payload plus a **stable ~289 B container
residual**. r4-perf's conservative choice of 944 was, by luck or by good
instinct, right to three digits. r4-a's 270 B residual (extrapolated from the
I256 binary) was 7% low. I use **289 B** throughout.

Payload model: `2 buffers × 41 slots × 2 coefficients × sizeof(word)`.

| word | payload B/w | as-is total | flat container (L5, +57) |
|---|---|---|---|
| u32 (p < 2³¹) | 656 | **945** | 713 |
| u16 (p < 2¹⁶) | 328 | 617 | 385 |
| u8 (p < 2⁸) | 164 | 453 | 221 |

The 945 column is MEASURED-anchored. **The flat column is EXTRAPOLATED from a
model nobody has built**, and r4-adv-cost §4.3 showed r4-perf's warrant for the
57 B does not close (its five terms sum to 256 against a 288 B residual). I
carry the flat column and mark it EXTRAPOLATED-WEAK; every H=19 verdict rests
on it.

### 1.6 RAM per run, GiB

| H | as-is u32 | as-is u16 | as-is u8 | flat u32 | flat u16 | flat u8 |
|---|---|---|---|---|---|---|
| 17 | **20.8** | 13.6 | 10.0 | 15.7 | 8.5 | 4.9 |
| 18 | **63.8** | 41.7 | 30.6 | 48.1 | 26.0 | 14.9 |
| 19 | 197.6 | 129.0 | **94.7** | 149.1 | **80.5** | 46.2 |
| 20 | 619.1 | 404.2 | 296.8 | 467.1 | 252.2 | 144.8 |

Boxes, MEASURED by r4-adv-cost §1.5 on 2026-08-13: **dalby 125 GiB total, 116
GiB available with a job resident, 80 Neoverse-N1 cores at 3 GHz, one NUMA node,
564 GB free NVMe. ayr 78 GiB, 32 cores.**

### 1.7 The table the brief asked for

Under §4.1's confirmation framing (**1 prime + 1 RED prime = 2 runs per
height**), no new code beyond what is already built and gated in `pm-b1-perf`:

| H | share of a(40) | wall/prime | primes | thread-h | peak RAM/run | box | wall if concurrent |
|---|---|---|---|---|---|---|---|
| **17** | 9.0587% | 6.55 h | 2 | **13.1** | 20.8 GiB | dalby, both | **6.6 h** |
| **18** | 7.4180% | 22.69 h | 2 | **45.4** | 63.8 GiB | 1 dalby + 1 ayr | **22.7 h** |
| **19** | 5.7226% | 79.33 h | 2 (u32) | 158.7 | 197.6 GiB | **fits nothing** | — |
| 19 (u8) | | 79.33 h | 2 (8 bits each) | 158.7 | 94.7 GiB | dalby, serial | 158.7 h |
| 19 (flat u16) | | ~61 h¹ | 2 (16 bits each) | 122 | 80.5 GiB | dalby, serial | ~122 h |

¹ 79.33 h ÷ 1.3, the L5 wall factor, EXTRAPOLATED and unmeasured.

For comparison, the **reconstruction** framing r4-a and r4-adv-cost priced (4+1
u32 primes, or 7+1 u16, or 15+1 u8):

| H | primes | thread-h | wall, best fleet packing |
|---|---|---|---|
| 17 | 5 | 32.7 | 6.6 h (5 concurrent, 104 GiB on dalby) |
| 18 | 5 | 113.5 | 3 waves × 22.7 h = **68 h** |
| 19 | 16 (u8) | 1,269 | 16 serial on dalby = **53 days** |

**Reconstruction costs 2.5x at H=17/18 and 8x at H=19 for a property the mission
does not ask for.** §4.1.

---

## 2. Which lever is now worth building — and why the brief's inversion does not hold

### 2.1 The inversion as stated, and the step that fails

The brief puts it as: *"halving the bytes moved per state should now translate
close to directly into wall."* That is the correct inference **from
bandwidth-boundedness**. The declining patch factor is evidence the loop is not
*ALU*-bound. It is not evidence the loop is *bandwidth*-bound. Those are not the
only two options and the third one is what the numbers say.

r4-adv-cost §4.2, MEASURED at H=15 and never contradicted:

> 2,624,197 states × 615 state-steps × ~1.667 edges × 656 B = 5.29×10¹² B moved
> in 2,065.1 s = **2.56 GB/s single-thread** … A single Neoverse-N1 core
> sustains roughly 10 GB/s streaming. **The as-is loop is at about a quarter of
> its single-core roof — it is not bandwidth-bound today.**

Apply the measured 1.122x: the patched loop is at ~2.87 GB/s, still ~29% of the
roof. **A loop at 29% of its streaming ceiling is not bandwidth-bound, and
halving its bytes will not halve its wall.** If the patch had removed ~90% of
the divides and the loop were bandwidth-bound at the roof, the patch would have
bought ~0% — it bought 12%. If it were ALU-bound, it would have bought 2–3x — it
did not. It is bound by something that scales with neither instruction count nor
byte count.

That something is **random-access memory latency**, and there are three
independent tells:

1. `c(H)` grows 6.9% per height with a 3.9% residual over five points. Nothing
   about the arithmetic per state changes with H beyond a factor of H. What
   changes is the *table size*: 115 MB at H=12, 7.0 GB at H=16, ~21 GB at H=17.
   Access into it is by `KeyHash` of a u128 — uniformly random by construction.
2. The container residual is **flat at 289 B/window** (§1.5) — the per-state
   `unordered_map` node and the per-state `vector` payload are both separate
   heap allocations, so **every state touch is two dependent pointer chases**
   before the payload is even reached.
3. Minor page faults in the patched H=15 log: **3,066,643** for a 2.36 GB peak
   RSS = 4 KB pages throughout, 576,000 pages resident. At H=17 that is 5.1M
   pages against a Neoverse-N1 L2 TLB of roughly a thousand entries. **Every
   random probe is a page walk.**

### 2.2 What falsifies this, in twenty minutes

r4-adv-cost §4.2 already specified the right experiment and I endorse it
unchanged: **run the patched binary at H=14 with a u16 payload and with a u32
payload, nothing else different.**

- If the wall roughly halves → bandwidth-bound, the brief's inversion holds, L6
  goes to the top of the list, and my §2.3 ranking is wrong.
- If the wall barely moves (my prediction: **within 15%**) → latency-bound,
  narrowing stays a RAM lever only, and §2.3 stands.

That is the falsifier and it is cheap. It is the second job I would dispatch,
after §5's.

### 2.3 The re-ranked lever list

Ranked for a **latency-bound** loop. Where I move a lever relative to r4-perf I
say which of its steps I am rejecting.

| rank | lever | what it attacks | est. | was |
|---|---|---|---|---|
| 1 | **L7 shard across cores** | latency-bound loops scale *better* with cores, not worse | 8–20x, ASSERTED | r4-perf rank 3 |
| 2 | **L5 flat table + payload arena** | removes both dependent pointer chases per state touch | 1.5–2.5x, EXTRAPOLATED | r4-perf 1.2–1.4x |
| 3 | **huge pages** (2 MB, `madvise`/THP) | 512x TLB reach; ~5 lines | 1.1–1.4x, ASSERTED | **nobody proposed it** |
| 4 | **L8 CSR edge cache for c ≥ 1** | deletes the hash probe entirely from the inner sweep | 1.3–2x at H≤18, ASSERTED | r4-perf "20–40%, NOT ESTABLISHED" |
| 5 | software prefetch of target buckets | hides the miss instead of removing it | 1.2–1.5x, ASSERTED | not on r4-perf's list |
| 6 | **L6 narrow payload** | **RAM lever only** — required at H=19, worth little wall | 1.0–1.15x wall | r4-perf "halves the wall" |

**L7 goes to the top, and the measurement is the reason.** r4-adv-cost §4.1
already noted, as its "for it" bullet, that *"random access is latency-bound per
core, and latency-bound loops scale better with core count than streaming ones
do, because each added core brings its own miss concurrency."* Tonight's
measurement is what promotes that bullet from a hedge to the main argument.
dalby's single NUMA node (MEASURED, r4-adv-cost §1.5) removes the one structural
risk. The 8–20x remains **ASSERTED** — nobody has run this DP on more than one
core, and R4-A4's 2/4/8-thread probe at H=14 is still the right first move.

**L5 rises and its estimate rises with it.** r4-perf priced L5 at 1.2–1.4x from
"removing allocator traffic and improving locality" — an allocator-throughput
argument. Under latency-boundedness the argument is different and larger: the
flat table collapses `hash → bucket → node → payload vector → payload` from
three dependent misses to one probe plus one indexed load into a contiguous
arena. That is the single biggest structural change available without threads.

**Huge pages is the cheapest thing on the list and no lane proposed it.**
r4-adv-cost mentions huge pages once, inside the L7 discussion, as a risk to the
sharding estimate. It is a lever in its own right, it is five lines, and the
3.07M minor faults in the patched H=15 log are the evidence.

**L8 rises for a reason r4-perf did not use.** Its own §1's L8 argument is that
39/41 of hashing and `canon` work is *redundant*. Under an ALU-bound model
redundant work is cheap; under a latency-bound model **the hash probe is the
expensive thing and L8 deletes it**. Its RAM cost still rules it out at H=19
(171 GiB of edge lists) but at H=17 it is ~16 GiB on top of ~21, which fits
dalby. Its semantics are "by intent" — it assumes `S_r` is c-independent — and
r4-perf's proposed fix (compare key-set size and an order-independent checksum
between consecutive columns, exit 2 on difference) makes it by construction. Do
not build it without that check.

**L6 stays where r4-a put it and I side with r4-a against r4-perf.** r4-perf §1's
L6 says: *"once L1–L4 land the loop is bandwidth-bound at 656 B/edge, so halving
the payload also halves the wall per run. The two effects nearly cancel."* The
antecedent is false — L1–L4 landed and the loop is at 29% of its bandwidth roof.
So the "wall/run ~0.61" column of that table is unsupported, u16's 7+1 runs cost
7+1 runs of wall, and **narrowing is what it always was: a RAM lever, bought at
proportionally more runs.** It is still compulsory at H=19 for exactly that
reason — flat-u32 is 149 GiB against 116 available.

### 2.4 The container rewrite and cache blocking, reconsidered

**Container rewrite (L5): build it.** It was already the prerequisite for L7, and
the measurement makes it a first-class wall lever rather than a RAM lever with a
side benefit. 150 lines, 6–10 hours, semantics-preserving by construction
(modular addition into a key-indexed table is commutative and associative, so
the final payload per key is independent of index assignment and insertion
order). It is the one item on this list I would build before measuring anything
else, and even r4-perf's own decision table agrees: its `< 1.5x` branch says
*"L5 (container) becomes lever 1."*

**Cache blocking: I do not think it is available here, and I want to say why
rather than rank it low.** Blocking needs a reuse structure to exploit — a
working set you can partition so each block is touched many times while resident.
This DP's inner sweep touches each source state once per column-step and scatters
to targets at hash-random positions. There is no temporal reuse to block for; the
misses are compulsory, not capacity. What *looks* like blocking and is not is
L7's shard partition: partitioning targets by hash so each owner thread writes
into a smaller region does improve DRAM page locality on the write side, and that
is a genuine second-order benefit of L7 that r4-perf did not claim. But as a
single-thread lever, blocking has nothing to block. **Reject, with the reason
stated: no reuse to exploit.**

The nearest thing that *is* available is a **radix pre-pass** — bucket the
emitted edges by the high bits of the target hash before applying them, so the
apply phase writes into a region that fits in the last-level cache. That is L7's
scatter buffer running single-threaded, it costs 32 B written and read back per
edge against 656 B of payload traffic already moving (r4-adv-cost §4.1's
arithmetic, +10%), and it converts random scatter into sequential-plus-local.
**It is worth 1.3–2x on a latency-bound loop, ASSERTED, and it is 80 lines
rather than L7's 300.** Nobody has proposed it. If L7 turns out not to shard, the
radix pre-pass is the fallback that keeps most of the locality win.

---

## 3. The `H > 16` guard and the successor bound — settled, and both lanes are loose

### 3.1 The guard: r4-a is right, and it is already done

r4-a §2.1: key uses `BITS*(H+1) = 5*(H+1) ≤ 128` → **H ≤ 24**; block ids after
`canon` ≤ H+1 with `shifted` prepending `mx+1`, against `int map[32]` →
H ≤ 29; `uint32_t` state index holds 2.23e9 at H=21 < 2³². I re-derived all
three off the source and agree. **H ≤ 24 is the binding limit and it is the right
raise.**

It is already in the tree that ran tonight. `dalby:~/src/pm-b1-perf/cpp/cutcount_b1.cpp`:

    457:  if (H > 24 || p >= (1ull << 31)) { fprintf(stderr, "limits: H<=24, p<2^31\n"); return 1; }

with the exact-payload mode still capped at line 465 (`H > 16 || Nmax > 60`),
which is correct and should stay — see §4.3.

### 3.2 The successor bound: `b <= floor((H-1)/2)`

The two lanes disagree, and **r4-perf is right against r4-a. Both are loose, by
one and by two respectively.**

Where r4-a fails. Its words:

> cells adjacent within a column are king-adjacent, so distinct blocks must be
> non-adjacent within each part, giving `b <= ceil(r/2) + ceil((H+1-r)/2) <=
> floor((H+3)/2)`

The failing step is *"within each part"*. The window's two parts are vertically
adjacent **columns**, and a king graph has diagonal edges: `(i,c)` and `(j,c-1)`
are king-adjacent whenever `|i-j| <= 1`. r4-a drops every cross-column edge.
r4-perf's §3 restores them at the seam and gets `floor((H+1)/2)`, which is
correct as a bound on the window's independence number. Its geometry — window =
column `c` rows `0..r-1` in slots `0..r-1`, then column `c-1` rows `r-1..H-1` in
slots `r..H` — I re-derived from `gather` and it is right, including its check
that the four pushed slots `0`, `H-2`, `H-1`, `H` land on `(r-1,c)`, `(r+1,c-1)`,
`(r,c-1)`, `(r-1,c-1)`.

Where r4-perf is loose. Its words:

> **`b` is bounded by the maximum independent set of the window's king graph.**

True, and not tight, because **`b` is only ever *used* inside `if (nb == 0)`**
(line 178 of the recovered source; the `nb >= 2` and `nb == 1` branches return
before `b` is computed). `nb == 0` means every cell `gather` pushed is empty.
Those cells are exactly the four king-neighbours of `(r,c)` that lie in the
window. So the representatives counted by `b` live in the window **minus** those
four cells, and removing them destroys the seam:

For `r >= 1`, `c > 0`, `r+1 < H`:

- part `A` (column `c`, rows `0..r-1`) loses row `r-1` → usable rows `0..r-2`, a
  path of `r-1` vertices, independence `ceil((r-1)/2)`;
- part `B` (column `c-1`, rows `r-1..H-1`) loses rows `r-1`, `r`, `r+1` → usable
  rows `r+2..H-1`, a path of `H-r-2` vertices, independence `ceil((H-r-2)/2)`;
- the surviving parts are four rows apart (`r-2` versus `r+2`), so **there are no
  cross edges left at all** and the two maxima simply add.

    b <= ceil((r-1)/2) + ceil((H-r-2)/2)
       = floor(r/2) + floor((H-r-1)/2)
      <= floor((H-1)/2)

using `floor(a/2) + floor(b/2) <= floor((a+b)/2)` with `a+b = H-1`. The three
boundary shapes give the same value and two of them attain it:

| case | window after removals | bound |
|---|---|---|
| `r = 0` (window is column `c-1` plus the stray `(H-1,c-2)`; `gather` pushes `(0,c-1)`, `(1,c-1)`) | path rows `2..H-1` plus a stray adjacent to rows `H-2, H-1` | `ceil((H-2)/2) = floor((H-1)/2)`, attained |
| `r = H-1` (`(r+1,c-1)` off-grid, so `B` loses only rows `H-2, H-1`, which is all of `B`) | path rows `0..H-3` | `ceil((H-2)/2) = floor((H-1)/2)`, attained |
| `c = 0` (no column `c-1`; those slots are 0 from the initial key) | path rows `0..r-2` | `ceil((r-1)/2) <= floor((H-1)/2)` |

The invariant this rests on — **king-adjacent occupied cells in a reachable key
carry the same block id** — is r4-perf's and it is correct: it holds for the
initial key 0; `nb >= 2` emits nothing (line 163), `nb == 1` gives the new cell
that id (165), and `nb == 0` means no occupied king-neighbour so any id is
consistent (183, 184); `canon` is a bijection on ids and `shifted` only drops a
slot, so neither can break it. Pick one representative cell per distinct id: they
are pairwise non-king-adjacent, so `b` is at most the independence number of the
*occupied-eligible* window, which is what the case table bounds.

### 3.3 The verdict

`ns = b + 2` in the `nb == 0` branch, and at most 2 in the others.

| H | 16 | 17 | 18 | 19 | 20 | 21 | 22 | 23 | 24 |
|---|---|---|---|---|---|---|---|---|---|
| `b <= floor((H-1)/2)` | 7 | 8 | 8 | 9 | 9 | 10 | 10 | 11 | 11 |
| entries written | 9 | 10 | 10 | **11** | **11** | 12 | 12 | 13 | 13 |
| `out[12]` | fits | fits | fits | **1 spare** | **1 spare** | full | full | **overflow** | overflow |
| `SUCC_MAX = 16` | fits | fits | fits | fits | fits | fits | fits | fits | **3 spare** |

**Answers to the two lanes' question: `Succ out[12]` does not overflow at H=19 or
H=20 — it has one entry of headroom, not zero — and the first overflow is at
H=23, past the H≤24 key-packing limit by one height.** `SUCC_MAX = 16` is
provably sufficient across the entire range the raised guard admits.

Two consistency checks. At H=16 the bound gives 7, against the source's own
comment at line 96 (*"Max distinct blocks in a window of H+2 cells is <= 9 for
H<=16"*) — tighter and consistent. At H=2 it gives 0, and by hand the H=2 window
is three mutually king-adjacent cells all of which `gather` pushes, so `nb == 0`
forces every one of them empty and `b = 0` exactly.

### 3.4 The cheapest decisive probe: there is not one, and there does not need to be

**No compute probe is required.** The argument above is a case analysis over
three window shapes with no free parameters, and the thing it could get wrong —
the reachability invariant, or my reading of `gather` — is already **fail-closed
in the binary that ran tonight**:

    177:  if (b + 2 > SUCC_MAX) {
    178:    fprintf(stderr, "FATAL succ_overflow H=%d r=%d c=%d b=%d cap=%d\n", ...

That abort did not fire at H=13, 14 or 15 (all three runs exited 0). It is one
compare per state per step against ~3,500 slot operations — unmeasurable. **A
silent stack smash is impossible in this binary regardless of whose bound is
right**, which is the property the brief actually needs, and it costs nothing.

If a RED half is wanted for the *combinatorial* claim specifically — and the
project's standard does ask for one — it is a ~30-line pure-Python enumeration
of the window geometry for H = 1..24: build the king graph on the `H+1` window
cells for every `r`, delete the cells `gather` pushes, take the maximum
independent set by brute force (≤ 25 vertices, two paths, trivial), and assert it
equals `floor((H-1)/2)`. **Milliseconds, no engine, no box.** I have not written
or run it; it is queue row **R4-L3**. It tests the geometry, not the invariant
and not reachability — those are the runtime guard's job, and the division of
labour between the two is the honest one.

**R4-A2 can be closed on this.** It should be closed as *"bound is
`floor((H-1)/2)`, `out[12]` safe to H=22, `SUCC_MAX=16` safe to H=24, guard
compiled in and exercised clean at H≤15"* — not as *"argued safe"*.

---

## 4. The staged plan

### 4.1 The reframe that sets the stages: confirm, do not reconstruct

Round 4's goal statement asks for *"a (relatively) efficient way to **confirm**
the Transfer Matrix number(s) independently."* Both cost lanes priced a
**reconstruction**: r4-a §2.5 derives a bit budget (`C_H(40) < 2^112`), concludes
4 primes plus one held out for RED-D; r4-adv-cost §3 corrects the u8 prime count
from 14+1 to 15+1 against a 110.842-bit target — arithmetic I re-derived and
agree with, and which is only *needed* under reconstruction.

Confirmation does not need CRT, because the answer is already known and can be
**predicted**:

    T(n,H) = C_H(n) - 2*C_{H-1}(n) + C_{H-2}(n)

`T(n,17)` is banked in `results/triangle.txt` for every n, and `C_15`, `C_16` are
banked **exact** in `results/cutcount_b1/rows/`. So before a single cycle of the
H=17 run, we can compute, for each prime p and each n = 1..40,

    predicted C_17(n) mod p  =  ( T(n,17) + 2*C_16(n) - C_15(n) ) mod p

and the run either reproduces all 40 residues or it does not. Consequences:

- **One prime is already a strong check.** 24 of the 40 predictions are
  nontrivial at H=17 (`T(n,17) = 0` for n < 17), and a discrepancy in the DP
  would have to reproduce all 24 residues by accident. Under any random-error
  model that is ~`p^-24`.
- **The second prime is the RED**, not a bit-budget requirement. Two 31-bit
  primes is the whole battery.
- **No CRT assembler needs writing** to reach the goal (r4-a §2.5's script), and
  **no RED-D held-out prime** is needed. The comparator is ~30 lines of Python
  and is a *prediction* checker rather than a reconciler, which is the stronger
  shape.
- **The u8/u16 prime-count arithmetic becomes irrelevant at H=17 and H=18**,
  because RAM does not force narrowing there. It comes back at H=19, where u8's
  8 bits per run is a weak per-run check and u16's 16 bits is a moderate one —
  a real argument for the flat container at H=19 rather than for narrowing
  alone.

I flag the one thing this gives up in §4.4. Reconstruction stays available as a
later upgrade at 2.5x (H=17/18) to 8x (H=19) the cost, and it is the right thing
to buy **if and only if a residue disagrees**.

### 4.2 The stages

Each stage produces one checkable artifact and gates the next.

**Stage 0 — the predictions, before any compute.** Write
`experiments/tristruct/r4_ladder_predict.py`: read `results/triangle.txt` and
`results/cutcount_b1/rows/C15.out`, `C16.out`, emit `predicted C_17(n) mod p` for
n=1..40 and each prime, into `results/r4/predicted/C17.p<P>.pred`. RED half: flip
one digit of one banked `T` and confirm the comparator reports a mismatch.
**Artifact:** the prediction file, committed *before* the run. **Cost:** desk
work, no box. **Gate:** the file exists and its RED fires. This ordering is the
point — a prediction filed after the run is not a prediction.

**Stage 1 — H=17, one prime, `p = 2147483647`.** The same prime as every
measurement on record, so the wall is directly comparable to §1.4's 6.55 h
extrapolation and the run doubles as the calibration of that fit at H=17.
**Artifact:** `C17.p2147483647.out`, 40 lines. **Check:** byte-compare against
the Stage 0 prediction. **Cost:** 6.55 h EXTRAPOLATED, 20.8 GiB EXTRAPOLATED,
dalby, 1 core. **Gate:** all 40 residues match.
**Abort:** any mismatch → stop the ladder, do not start H=18. A mismatch means
either the TM row or the B1 rule is wrong at H=17, and *that* is the most
valuable result the round could produce — it escalates immediately to the full
5-prime reconstruction to find out which.

**Stage 2 — H=17, second prime (RED), concurrent with Stage 3.** Any second
31-bit prime, e.g. `2147483629`. **Artifact + check** as Stage 1.
**Cost:** 6.55 h, 20.8 GiB. **Gate:** match → **T(40,17) confirmed, 9.06% of
a(40) banked as second-source**, taking the two-source total from 21.64% to
30.70%.

**Stage 3 — H=18, one prime.** Gated on Stage 1 only (not on Stage 2 — they are
independent and dalby holds 20.8 + 63.8 = 84.6 GiB comfortably).
**Artifact:** `C18.p2147483647.out`. **Check:** the same prediction test, using
the newly produced exact-equivalent `C_17` — note the subtlety: `T(n,18)` needs
`C_18 - 2C_17 + C_16`, and we have `C_17` only **mod p**. That is fine and it is
the same prime, so the prediction is
`C_18(n) ≡ T(n,18) + 2*C_17(n) - C_16(n)  (mod p)` with `C_17(n) mod p` taken
from Stage 1's output. The chain is mod-p throughout and stays exact.
**Cost:** 22.69 h, 63.8 GiB, dalby. **Gate:** all 40 residues match.

**Stage 4 — H=18, second prime, on ayr.** 63.8 GiB against ayr's 78 GiB — fits,
and it is the only stage that needs ayr. **Caveat:** ayr is a different ISA and
the wall will not match §1.4; the *values* must still match, and that is the
whole point of running it there. A cross-ISA agreement on the residues is
strictly better evidence than a second prime on the same box.
**Gate:** match → **T(40,18) confirmed, cumulative 38.12% of a(40).**

**Stage 5 — decide H=19 on what Stages 1–4 measured, not on what §1.4
extrapolated.** By then there are two more MEASURED points on the `c(H)` fit and
two more on the B/window constant. H=19 needs, in order:
(a) the u32-vs-u16 discriminator of §2.2 (20 min);
(b) R4-A4's thread-scaling probe at H=14 (27 min);
(c) L5, the flat container, 6–10 h of authoring — required for RAM at H=19 under
every payload width;
(d) then a costing decision between flat-u16 sole-tenant serial (~122 h for two
primes, no threads) and L7 (~a day, if it shards).
**Nothing about H=19 should be committed before (a) and (b) land.** They are
47 minutes of dalby between them and they move a 5-day-to-3-week estimate.

### 4.3 What does *not* need building

- **CRT assembler and RED-D** (r4-a §2.5) — not on the confirmation path.
- **The binomial self-check in residue mode** (r4-a §2.3, +50% payload) — the
  prediction test is a strictly stronger control than the q=1 identity, checks
  all 40 values of n rather than one, and costs no RAM. r4-a recommended
  carrying the self-check; on the confirmation framing I recommend against it,
  and the reason is not cost — it is that the prediction test subsumes it.
  **The gate battery is not being weakened here; it is being replaced by a
  tighter one.** That sentence should be in the phase-2 brief in those words.
- **Raising the exact-mode cap at line 465.** I checked whether the exact oracle
  could be pushed to H=17 to extend the ground truth: 3 coefficients × 41 slots ×
  32 B × 2 buffers + 289 = **8,161 B/window = 180.0 GiB at H=17**. It does not
  fit dalby, and 2 coefficients at I256 is still 122.1 GiB. An **I128** exact
  payload would be 64.2 GiB (2 coeff) or 93.2 GiB (3 coeff) and *would* fit — but
  the `m0 = -b` weight (line 184) makes the DP a cancelling sum, so intermediate
  magnitudes are **not** bounded by the final row values and I128 safety is
  unproven. It is a real lever and I file it as **R4-L2** with the cheap probe
  (instrument the existing I256 exact binary to report max |coefficient| at
  H=12..15, ~1.4 h of dalby) rather than recommending it here.

### 4.4 The correctness evidence above H=16, stated plainly

The brief calls this the honest weak point. It is, but not quite where it is
placed.

**What is *not* the problem.** "The recovered oracle stops at H=16" is true of the
*exact B1 binary* and irrelevant to the check, because the thing being confirmed
is `T(n,H)`, which is banked to H=40 in `results/triangle.txt` from the transfer
matrix. The oracle above H=16 is the TM table itself, and the B1 rows at H=15/16
are what establish that B1 and the TM agree where both exist — 21.64% of a(40),
`mismatch=0` over 640 cells.

**What the evidence at H=17 actually is, in four layers:**

1. **Same binary, same code path.** The H=17 run uses `run_height_modp` with
   `successors`/`gather`/`shifted`/`canon` unchanged from the H≤16 runs — r4-a
   §1a established the sharing is by function, not by copy. The only thing H=17
   changes is a loop bound and one guard constant.
2. **The binary is bit-exact against its predecessor.** `cmp_failures=0` at
   H=13/14/15 tonight, and the residue path was validated against the exact
   oracle at 360 residues across H=12..16 with zero mismatch, at 7.8M states.
3. **The prediction test at H=17 itself**, 24 nontrivial residues per prime,
   filed before the run.
4. **A second prime, and at H=18 a second ISA.**

**What none of that catches, and this is the real weak point:** a **systematic**
error present in *both* the TM and B1 would produce agreement. More primes do not
help; they only bound *random* disagreement. The defence is structural rather
than statistical, and it is the reason the B1 rows are worth having at all —
`PROVENANCE.md`: *"Nothing in it decides connectivity: clashes zero rather than
join, there is no union-find verdict, no stranded-component death and no
completion predicate."* The independence analysis is
`results/triangle-r3-adv-independence.md` and it is not mine to re-litigate; I
note only that **the confirmation is exactly as strong as that independence
argument, and no stronger, at every height including 15 and 16.** H=17 adds no
new species of doubt; it adds one more cell to a check whose ceiling was already
set at H=15.

The second weak point is smaller and mine to name: **§1.4's walls and §1.6's RAM
are EXTRAPOLATED three heights past the last measurement**, on a fit with 3.9%
residuals. If H=17 comes in materially off 6.55 h and 20.8 GiB, the H=18 and
H=19 numbers should be re-fitted before anything is dispatched on them. Stage 1
is deliberately the cheapest possible test of the extrapolation as well as of the
mathematics.

---

## 5. JOB REQUEST — LADDER-JOB-1

    job id:            LADDER-JOB-1
    measures:          C_17(n) mod p for n <= 40, p = 2147483647, on the patched
                       fail-closed binary. It is simultaneously (a) the first
                       second-source recount of a band cell above H=16, worth
                       9.06% of a(40), (b) the first MEASURED point past the
                       c(H) fit, and (c) the first exercise of the raised H<=24
                       guard and the SUCC_MAX abort at a height where the
                       successor count actually grows.

    decides:           - whether T(40,17) survives an independent recount. A
                         mismatch stops the ladder and escalates to the full
                         5-prime reconstruction to find out which side is wrong;
                         it would be the round's most valuable result.
                       - whether section 1.4's extrapolation is trustworthy. It
                         predicts 6.55 h and 20.8 GiB. If either is off by more
                         than ~15%, H=18 and H=19 must be re-fitted before
                         dispatch.
                       - whether the fail-closed guards fire at H=17. Section 3
                         says b <= 8 there, so they must not.

    prerequisite:      Stage 0 -- experiments/tristruct/r4_ladder_predict.py must
                       exist, must have its RED exercised (perturb one banked T,
                       confirm mismatch), and its output
                       results/r4/predicted/C17.p2147483647.pred must be
                       COMMITTED BEFORE THE RUN STARTS. A prediction filed
                       afterwards is not a prediction. The script does not exist
                       yet; ~30 lines of Python, no box.

    box:               dalby. Same box as every wall in section 1, same ISA,
                       same allocator -- the timing half of this job is
                       uninterpretable anywhere else. The value half is not, and
                       the H=18 second prime should deliberately go to ayr
                       (section 4.2, Stage 4).
    cores:             1
    binary:            ~/src/pm-b1-perf/build/cutcount_b1 -- the L0+L1-L4 patched
                       build that produced r4_perf_job1.log with cmp_failures=0
                       at H=13,14,15. Record its sha256 in the receipt. It
                       already carries `H > 24` (line 457), SUCC_MAX = 16 with a
                       fail-closed abort (177-179), and the m1_not_bit guard.
                       No source change is required for this job.

    run:               P=2147483647
                       cd ~/src/pm-b1-perf
                       sha256sum build/cutcount_b1
                       python3 tests/gate_cutcount_b1.py     # ~7 s, must be GREEN
                       /usr/bin/time -v ./build/cutcount_b1 --modp 17 40 $P \
                         results/cutcount_b1/modp/C17.p$P.out
                       (tee to experiments/tristruct/r4_ladder_h17.log, tmux on
                        dalby; a named on-disk script, not stdin)

    wall estimate:     6.55 h EXTRAPOLATED (section 1.4), from a five-point
                       log-linear fit with 3.9% residuals, anchored on the
                       MEASURED c(16). Optimistic 5.8 h if the patch factor
                       holds at 1.12; I do not bank it. Budget 8 h.
    RAM estimate:      20.8 GiB EXTRAPOLATED, from the MEASURED 942.6 B/window at
                       H=16 rounded to 945. dalby has 116 GiB available. Even a
                       50% miss fits.
    disk estimate:     < 2 kB (40 lines) plus the log.
    interruptible:     no resume inside a height. A kill costs the whole run;
                       at 6.5 h that is acceptable and no checkpointing should be
                       built for it.

    RED controls:
      RED-predict  The 24 nontrivial residues of Stage 0's prediction file must
                   match byte for byte. RED half: run the comparator against a
                   deliberately perturbed prediction first and confirm it
                   reports the mismatch. This is the control that makes the job
                   worth running; without Stage 0 filed first it is just a
                   number.
      RED-gate     tests/gate_cutcount_b1.py, seven checks including its three
                   REDs, on the exact binary sha256 that runs. It covers the
                   exact paths only; a failure means the tree moved since
                   PERF-JOB-1.
      guard        FATAL succ_overflow and FATAL m1_not_bit must NOT fire.
                   Section 3 proves b <= 8 at H=17 against a cap of 16. If
                   succ_overflow fires, section 3 is wrong and every H >= 17
                   plan is void until it is re-derived.
      identity     q0_zero fires per height in modp (exit 2). The q=1 binomial
                   identity is absent in modp -- record that as a known and
                   deliberate gap in the receipt (section 4.3) rather than
                   letting the log's silence imply it passed.
      trailing     C_17(n) for n < 17 must equal C_16(n) exactly where the strip
                   cannot use the extra row -- a free consistency read off the
                   two row files, not a designed control, but worth eyeballing.

    changes if:        match, wall within 15%  -> dispatch Stage 2 (second prime,
                                                  H=17) and Stage 3 (H=18, first
                                                  prime) concurrently on dalby;
                                                  84.6 GiB combined, both fit.
                       match, wall off > 15%   -> re-fit c(H) on six points
                                                  before H=18 is dispatched.
                                                  H=18 at 22.7 h is where a bad
                                                  fit starts to cost real days.
                       mismatch                -> STOP THE LADDER. Escalate: run
                                                  the full 5-prime reconstruction
                                                  at H=17 and CRT it, to
                                                  determine whether the TM row or
                                                  the B1 rule is wrong. This is
                                                  the branch that justifies the
                                                  whole exercise.
                       guard fires             -> section 3.2 is wrong. Re-derive
                                                  before anything else runs; the
                                                  binary is fail-closed so
                                                  nothing is corrupted.
    closes:            R4-A2 (jointly with section 3), and the first cell of the
                       22.20% this lane was asked about.

---

## 6. Queue rows filed

Appended to `results/r4/queue.md`: **R4-L1** (this job request), **R4-L2** (the
I128 exact-payload route — a *different kind* of second source, exact rather than
residue), **R4-L3** (the window-geometry enumeration that REDs section 3's
combinatorial half), **R4-L4** (the radix pre-pass — the locality lever nobody
proposed, and L7's fallback), **R4-L5** (huge pages).

---

## NOT ESTABLISHED

- **Every wall and every RAM figure for H >= 17.** They are a three-height
  extrapolation of a five-point fit. The fit's internal residuals are 3.9%; its
  extrapolation error is not quantified and is certainly larger.
- **The patch factor above H=15.** Three points, declining, accelerating in the
  decline. I plan on 1.00 and I have not measured 1.00.
- **Latency-boundedness.** It is my reading of three tells (the c(H) growth, the
  flat 289 B container residual, the 3.07M minor faults) plus r4-adv-cost's
  MEASURED 2.56 GB/s against an *unmeasured* 10 GB/s single-core roof for this
  part. Section 2.2's u16-vs-u32 probe is the falsifier and it has not been run.
  **If it is wrong, section 2.3's ranking is wrong and the brief's inversion is
  right.**
- **The 8-20x for L7**, unchanged from r4-perf and r4-adv-cost. Nobody has run
  this DP on more than one core.
- **The flat-container B/window figures** (713 / 385 / 221). EXTRAPOLATED from a
  decomposition r4-adv-cost showed does not close, of code nobody has written.
  H=19 rests entirely on them.
- **Everything in section 2.3 ranked 3, 4, 5 and the radix pre-pass in 2.4.**
  Estimates from mechanism, not measurement. Nobody has profiled this binary --
  still true after tonight, because PERF-JOB-1 measured a wall, not a profile.
- **Whether `results/triangle.txt`'s H=17..19 rows are themselves right.** That
  is the thing being tested and it is assumed by nothing here except the
  prediction test's construction, which is symmetric: a mismatch indicts both
  sides equally and neither specifically.
- **I128 exact-payload safety** (section 4.3, R4-L2). The cancelling `m0 = -b`
  weight means intermediate magnitudes are unbounded by the row values, and
  nobody has measured them.
