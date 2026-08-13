# r4-gen2 — generator, round 4, second wave

GENERATOR, 2026-08-13. Owns no question, builds nothing, **ran no compute on
any machine**. Everything below is reading, arithmetic, and read-only `ssh` to
dalby and ayr. Rows are `R4-G2-1` .. `R4-G2-25` in `results/r4/queue.md`; this
file carries the reasoning, the kills I can deliver myself, and the stale audit.

Do-not-repeat set taken as read: `R4-G1..G23`, `R4-A1..A5`, `R4-P1..P4`,
`R4-INV-1..4`, `R4-SB1..3`, `R4-AI1..7`, `R4-AC2..7`, `R4-LEAN-1..4`, the
"Closed, with the obstruction named" and "Three floors" sections of
`results/triangle-r3-synthesis.md`, and `designs/10`'s banded-ranking closure.

The three rows I would defend hardest are **R4-G2-8** (evaluate the size
variable instead of carrying it — a 23x RAM cut that turns H=19 into a weekend
and H=20 from impossible into a fortnight, in ~30 lines of a gated engine),
**R4-G2-1** (the 2.5x arithmetic lever was measured tonight at 1.12–1.28x and
*declining with height*, so the round's H=19 headline loses its first factor),
and **R4-G2-19** (every incumbent-free oracle in this campaign runs at H ≤ 6
and the band is H = 15..21; H-indexed stencil errors are the one class nothing
can see, and an index audit costing seconds closes it).

---

## 0. The measured record I am generating against

`results/r4/r4-adv-cost.md` was filed at 00:21 and correctly reported that two
of tonight's three artifacts had **no receipt on disk**. That is no longer
true. Read-only from dalby, 2026-08-13:

| file | what it establishes |
|---|---|
| `dalby:~/src/pm-b1/experiments/tristruct/r4_a_modp_bpw.log` | H=16 **landed**: `wall_s=6864.1 peak_rss_mb=7040.8`; four extra H=13 runs at four further primes |
| `dalby:~/src/pm-b1-perf/experiments/tristruct/r4_perf_job1.log` | patched `--modp` H=13/14/15 = **146.8 / 485.8 / 1840.7 s**, `peak_rss_mb` 302.8 / 959.1 / 2355.9 |
| `dalby:~/src/pm-b1-perf/experiments/tristruct/r4_spin_m16.log` | spin m=1..16: `wall_s=88.6 peak_rss_mb=90.7 compared=640 mismatch=0 sha256=578c940c…` |
| `dalby:~/src/pm-b1-perf/experiments/tristruct/r4_spin_gates.log` | `compared=49 mismatch=0` clean; mutants `drop-nw=12 drop-sw=12 rook=4`, each with its own binary sha256 |

Two derived anchors of my own, both from these logs:

- **Marginal B/window at H=16 = 941.6** — (7040.8 − 2363.6) MiB ÷ (7,832,667 −
  2,624,197) windows. MEASURED.
- **Measured `maxstates` equals ADV-I4's window census exactly** at H = 12..16
  (107,241 / 306,858 / 891,074 / 2,624,197 / 7,832,667). The census is not a
  model standing in for a measurement; it *is* the measurement, at Nmax = 40.
  Worth saying because §1 is otherwise a catalogue of the opposite.

Boxes, read-only: **ayr load 0.04, 77 GiB free, 32 cores**; **dalby 121 GiB
free, 80 cores, 563 GB on `/dev/md3`, no job resident**. Both idle as I write.

---

## 1. What a 207x overprice implies about everything else — R4-G2-1 .. R4-G2-7

The brief's framing is that INV-8's estimate was wrong because a model counted
41 ops where a kernel executes 2. That is right and `r4-adv-cost.md` §2 nails
it. But the inference "our estimates run pessimistic" is **refuted by tonight's
other measurement**, and that is the first thing I want on the record.

### 1.1 The other big lever was measured tonight and it went the wrong way — R4-G2-1

r4-perf's L1–L4 arithmetic patch was estimated at **2.5x (range 1.8–3.5x)** and
is the first factor in every H=19 and H=20 verdict in the round.

Measured, same box, same thread count, same prime:

| H | unpatched wall_s | patched wall_s | speedup |
|---|---|---|---|
| 13 | 188.2 (and 182.8 / 185.6 / 184.1 / 183.5 on the four re-runs) | 146.8 | **1.25–1.28x** |
| 14 | 599.5 | 485.8 | **1.234x** |
| 15 | 2065.1 | 1840.7 | **1.122x** |

The excess over parity is 0.25 → 0.23 → 0.12, i.e. **halving per height at the
top of the measured range**. Extrapolating that decline gives ~1.06x at H=16
and **~1.0x by H=17**, which is where the ladder actually lives. Peak RSS is
unchanged (2355.9 vs 2363.6 at H=15) — the structure-of-arrays half of the
patch bought no memory either.

The mechanism is not in dispute and `r4-adv-cost.md` §1.4 confirmed it to
within one instruction: the inner loop *does* spend 26 cycles where an add
belongs. Removing it buys 1.12x at H=15 anyway. **That is the definition of a
loop whose divide is hidden behind something else**, and the something else
grows with H. The patch is still worth keeping — it is value-preserving and
free — but it is not a 2.5x lever and nothing should be priced on one.

**Repricing.** `r4-adv-cost.md` §4.1's honest floor for H=19 was 5.7 days with
"2.5x + L5 + u16, no sharding". With the measured factor at the band (~1.05x
rather than 2.5x) that floor becomes **~13.5 days**, and the "~9 h with
everything" headline becomes ~21 h even granting the unmeasured 15x. The round
should stop quoting both.

**Cheapest thing that would kill this row:** one patched run at H=16 on dalby,
~1.9 h, giving a fourth point. If the speedup at H=16 comes in at 1.2x rather
than the ~1.06x the decline predicts, the decline is noise and 2.5x is merely
wrong rather than wrong-and-vanishing. Rides on any subsequent PERF job.
Prior the decline is real and continues: **0.7** (three points, monotone,
consistent with a growing memory-stall fraction).

### 1.2 The monotone-decline argument for 944 B/window is broken by the H=16 point — R4-G2-2

`r4-adv-cost.md` §1.2 adjudicated a disagreement in r4-perf's favour: three
marginal slopes, 1235.9 → 1088.5 → 851.2, "monotone over three intervals with
no step anywhere, which is what per-state allocator overhead amortizing looks
like". It was reading the log at column 27 of 41; H=16 landed at 00:46.

The fourth slope is **941.6**, an **increase of 10.6%**.

Nothing downstream breaks — 944 B/window remains a decent constant, now by
accident rather than by argument, and the *total* at H=16 (898.9 B/window) is
within 2% of r4-perf's ~880 projection. What breaks is the **model**: the
declining-overhead story predicted continued decline, and that story is what
licensed extrapolating B/window *downward* toward H=21. The right shape is
flat-to-rising, and a rising marginal is what you expect once the table stops
fitting in any cache.

Consequences worth a sentence each: r4-perf's H≥17 constant should be treated
as a *floor*, not a conservative upper bracket; and this is the second time
tonight a three-point trend has failed at the fourth point (§1.1 is the other,
in the other direction). **Cheapest kill: none needed — it is measured.** What
would change the reading is the H=17 point, which the ladder produces anyway.

### 1.3 Which other live numbers are models standing in for measurements — R4-G2-3

The brief asked for names. Ranked by how much a decision moves if the number is
wrong. Everything here is drawn from `r4-adv-cost.md` §7's provenance table plus
my own reading; the contribution is the ranking and, for the top two, the
observation that **both can be measured without the DP at all**.

| # | quantity | filed as | what it decides | measurable in isolation? |
|---|---|---|---|---|
| 1 | **15x sharding on dalby** | ASSERTED | whether H=19 is 30 h or 13 days | **yes** — R4-G2-4, 30 lines, no DP |
| 2 | **L5 flat container = 57 B/entry** | modelled, decomposition sums to 256 against a 288 residual | H=19's 81 GiB and H=20's "21% short" both rest on it | **yes** — R4-G2-5, 40 lines, no DP |
| 3 | payload work as a fraction of wall | never stated | whether R4-G2-8's 23x RAM cut costs 1.2x or 5x CPU | **yes** — one truncated-Nmax run |
| 4 | branch factor 1.667 | inherited from r3, never re-derived | two of the adversary's own anchors | yes — heartbeat already counts `maxtrans` |
| 5 | Lean increments 3–6 | ASSERTED by the lane's own admission | 5–7 sessions vs 8–10 | no |
| 6 | mincost survivor fraction (R4-G4) | structural argument | whether the prune is 2x or 10x | yes, desk |
| 7 | 2^−31 false-pass per prime | model | how many prime runs confirmation needs | **yes, from our own bug history** — R4-G2-7 |
| 8 | window census at H=17..21 | closed form | every RAM figure | **already confirmed**: measured `maxstates` = census exactly, H ≤ 16 |

The pattern behind #1, #2 and #3 is the generalisable finding and it is what
INV-8's 207x shares with them: **each is a property of a component, priced by a
model of the system.** INV-8 priced a two-add kernel with a whole-engine
constant. r4-perf priced a hash-table container with a decomposition of an
engine's RSS. L7 prices a scatter with a streaming ratio. In every case the
component is separately measurable in minutes, and in every case nobody
measured it because the *system* measurement looked too expensive. That is
R4-G2-25, my second-pass row.

### 1.4 Measure the sharding factor without writing the sharded DP — R4-G2-4

L7 wants to know one thing: how much aggregate random-access throughput 80
Neoverse-N1 cores get against a multi-tens-of-GB arena, relative to one core.
That is not a property of the DP. A ~30-line C program — allocate a 40 GB
arena, have *t* threads each perform read-modify-write of a 328 B record at a
uniformly random 64-byte-aligned offset, report aggregate GB/s for t = 1, 2, 4,
8, 16, 32, 64, 80 — measures exactly the quantity, in ten minutes, with no
correctness risk and nothing to gate.

Two refinements that make it worth doing properly rather than roughly: run it
with and without transparent huge pages (a 40 GB arena at 4 KB pages is 10M
pages against a few thousand TLB entries — `r4-adv-cost.md` §4.1 raised this and
nobody has priced it), and report *achieved GB/s*, not just a ratio, so the
result can be compared against the 2.56 GB/s the DP actually achieves.

Prior the measured factor is below 10x: **0.45**. Prior it is above 20x:
**0.2**. Either answer settles L7's go/no-go before 300 lines get written.
**Cheapest kill of the row itself:** if someone shows the DP's scatter is not
uniformly random over the arena — e.g. successors cluster in the key order —
the microbenchmark is measuring the wrong access pattern. That is worth
checking first and it is one histogram (see R4-G2-10 for why I expect it to
come back uniform).

### 1.5 Measure the flat container without writing the flat DP — R4-G2-5

Same move for #2. The claim is that a 224.5M-entry open-addressed table with a
u128 key and a u32 index runs at ~57 B/entry and behaves like the model. Test:
allocate it, insert 224.5M synthetic keys drawn to match the real key
distribution (or, cheaper and nearly as good, the real keys from a `--states`
dump at H=16 replicated), measure RSS and insert throughput. Forty lines, no
DP, ten minutes, and it converts the number H=19 and H=20 both rest on from
EXTRAPOLATED-from-an-unclosed-decomposition to MEASURED.

The reason to bother: if the answer comes back at 90 B/entry rather than 57,
H=20's "21% short" becomes "60% short" and the round should stop planning
around it. If it comes back at 57, H=19's 81 GiB is real and the flat container
is worth the 150 lines. Prior the model is within 25%: **0.5**.

### 1.6 A model that is *not* standing in for a measurement — R4-G2-6

Filed so nobody spends an afternoon checking it. ADV-I4's closed-form window
census is exactly equal to the engine's measured `maxstates` at every height
H = 12..16 (checked tonight against the heartbeats in
`r4_a_modp_bpw.log`). The state space saturates to the full census, which is
also R4-P3's prediction. **CLOSED AT FILING.**

Two riders, and they are the content. (i) The identity holds *at Nmax = 40*.
Any truncated-Nmax run (R4-G10) breaks it, and R4-G10's whole value depends on
by how much — so R4-G10 should report measured `maxstates` at reduced Nmax as
its primary output, not the wall. (ii) Saturation means the DP materializes
every reachable window regardless of whether that window can contribute at
n ≤ 40, which is R4-G4 arriving from the measurement side — and R4-G2-12 gives
the three-line version of it.

### 1.7 The false-pass probability of a residue check is a model, and our own bug history is the measurement — R4-G2-7

R4-G14 re-priced the ladder from 5 runs to 2 on the argument that one 31-bit
prime gives a false-pass probability of ~2^−31 "against any error not divisible
by p". That figure treats the error as a uniformly random integer. It is the
same class of substitution as the ones above: a model of the adversary standing
in for the adversary we have actually met.

The project has a documented error record — the kink resume/SIGTERM bug, the
phase-B erratum in the B1 provenance, the nine errors in L5-6, the r3 cost
adversary's 13-primes-for-103-bits slip. The generalisable question is: **what
did our real errors do to a count?** If they produced *small* deltas — a
handful of animals mis-attributed, a shard's worth of contribution dropped —
then for any error `e` with `|e| < p`, divisibility by `p` is impossible and a
single prime catches it with probability **1**, not 1 − 2^−31. If instead they
produced errors that scale with the count (a factor, a doubled shard), the
2^−31 model is the right one and R4-G14's two runs are the right answer for a
different reason.

Cost: an afternoon reading our own postmortems, zero compute. Value: it either
strengthens R4-G14 to "one prime is nearly certain against the error class we
have actually had" — which is a *publishable* sentence, unlike a 2^−31
hand-wave — or it names an error class the residue battery does not cover,
which is worth more. Prior that the historical record is dominated by
small-delta errors: **0.6**. **Cheapest kill:** if two of the four documented
errors are multiplicative, the row closes and 2^−31 stands.

---

## 2. Bandwidth, latency, and the 563 GB — R4-G2-8 .. R4-G2-15

### 2.1 Evaluate the size variable instead of carrying it — R4-G2-8

**This is the row.** It is the only thing in my pass that changes a verdict on
a band cell, it needs no unwritten infrastructure, and it is ~30 lines against
a committed, gated engine.

`cutcount_b1.cpp.59e90660:208`:

```
struct Payload { std::vector<I256> a; }; // 3*(Nmax+1): [3n]=c0, [3n+1]=c1, [3n+2]=A(1)
```

Every state carries a **dense length-41 vector in the size variable** for each
of three coefficient streams — 123 slots. The transition (lines 244-259) uses
that vector for exactly one thing: `n → n + dn`, a shift. In generating-function
terms the payload is a polynomial `P_s(z) = Σ_n p_{s,n} z^n` and the transition
multiplies by `z^{dn}`.

So run the DP with `z` set to a **number** rather than an indeterminate. The
payload collapses from 123 residues to 3. Recover the 41 coefficients by
running at 41 distinct `z` values and interpolating (a Vandermonde solve mod p,
microseconds). Every post-processing step in `run_height` is linear in the size
polynomial and therefore commutes with evaluation: the column sum is a sum, the
`f_W − f_{W−1}` normalization is a difference, and the prefix sum at line 278
is multiplication by `1/(1−z)`, fine at any `z ≠ 1`. Both self-checks survive —
`q0_zero` is a statement about the `c0` stream at any `z`, and
`q1eval_binomial` becomes an evaluated binomial identity.

**What it costs and what it buys, from tonight's measured anchors.**

RAM per state drops from ~941.6 B (MEASURED marginal at H=16) to a u128 key
plus 3 u32 residues at 0.7 load in a flat table, ~40 B — **a 23x cut**, and
unlike the flat-container lever it does not depend on an unclosed
decomposition, because the payload is 12 B by construction rather than 57 B by
model.

The cost is that the **per-state fixed work — the hash probe, the successor
generation, the key canonicalization — is paid 41 times instead of once**. Call
the payload's share of the wall `f`. Total CPU multiplies by `41(1−f) + f`.
That single unknown decides the row, and it is measurable in ten minutes: run
the committed `--modp` at H=14 with `Nmax = 20` and with `Nmax = 40`, and
compare wall per (column × state). If the wall halves, `f ≈ 0.9` and the
penalty is ~5x total CPU; if it barely moves, `f` is small and the row dies.
This rides on R4-G10's truncated-Nmax job and extracts a different number from
it.

Taking `f = 0.9` (consistent with `r4-adv-cost.md` §1.4's 82 slot-ops at 26
cycles against a ~200-cycle probe), per-`z` wall is 12.2% of a full run and
total CPU is 5.0x. Window counts EXTRAPOLATED by the measured ratio chain
(3.00 → 3.12) anchored on ADV-I4's exact 2,228,466,695 at H=21; `c(H)`
extrapolated at the geometric-mean 1.0729/height off the measured
`c(16) = 5.477e-5`:

| H | windows | full-payload RAM | **evaluated RAM/run** | full wall | **wall/z-run** | concurrent on dalby | **wall, 41 z-values, one prime** |
|---|---|---|---|---|---|---|---|
| 19 | 2.31e8 | 202 GiB | **8.6 GiB** | 82.5 h | 10.1 h | 14 | **~30 h** |
| 20 | 7.14e8 | 626 GiB | **26.6 GiB** | 288 h | 35 h | 4 | **~15 days** |
| 21 | 2.228e9 | 1.9 TiB | **83 GiB** | 1012 h | 123 h | 1 | ~210 days — **out** |

Read that table against the round's current position. H=19 is "39–104 days
serial, RAM-blocked at 202 GiB as-is, needs the flat container plus u16 plus a
15x sharding factor nobody has measured, to reach 9 hours". Under evaluation it
is **8.6 GiB per process and about 30 hours of an idle 80-core box**, using
14 of the 80 cores, with no flat container, no transposition, no mincost prune,
no sharded DP, and no u16 narrowing. Those levers all still compose on top.
H=20 goes from "RAM-blocked by 21%, hypothesis not finding" to a fortnight.
H=21 stays out, and I say so.

Honest counterweights, all four of them:

- **`f` is unmeasured.** At `f = 0.5` the total CPU penalty is 21x and H=19
  becomes ~5 days rather than 30 h — still a win on RAM, much less of one on
  wall. The row's value is a strong function of one number that costs ten
  minutes.
- **41 runs multiply against the prime count.** With R4-G14's two primes that
  is 82 runs at H=19. They are perfectly independent, which is why this fits an
  idle 80-core box, but it is 82 chances to lose a run and the assembly must be
  fail-closed on a missing `z`.
- **A new failure mode is introduced**: interpolation. Mitigated for free — run
  42 evaluation points and use the 42nd as a RED holdout, exactly the RED-D
  pattern r4-a already designed for primes. That control costs 2.4% and it is
  the reason I would not run this without one.
- **It does not clear either entry-ticket level.** This is reach, not
  independence. B1's rule class is unchanged; what changes is which cells that
  rule class can reach.
- **It is residue-only, and therefore does not compose with `R4-L2`.** At an
  integer `z` the evaluated sum is of order `z^40` and exact arithmetic would
  need thousands of bits, so evaluation lives entirely in the `--modp` path.
  R4-L2's exact-I128 second source and this row are alternatives at H=17, not
  layers.

Prior the arithmetic above is right in principle: **0.9** (the substitution is
elementary and the source structure is confirmed). Prior it delivers H=19
within a week of somebody starting: **0.5**. Prior it delivers H=20 at all:
**0.25**.

### 2.2 Compose evaluation with dense ranking, and amortize the key across everything — R4-G2-9, R4-G2-15

Once the payload is 12 B, **the key is the cost**: 16 B of u128 plus container
overhead against 12 B of data. Two composable moves.

**R4-G2-9 — dense ranking removes the key.** `designs/10` (and the banked
memory note behind it) established that a **dense** ranking of these frontier
states *exists* — set partitions are restricted-growth strings with an O(W)
Stirling/Bell rank — while a *banded* one cannot. Dense ranking is precisely
what evaluation needs and precisely what the full-payload engine did not: with
a rank there is no key, no hash, no container, and the table is a flat array of
12 B payloads indexed by rank. At H=21 that is 2.228e9 × 12 B = **27 GB**,
which fits dalby three times over. The catch is that ranking must be computed
per successor, which raises the fixed cost `f` fights against — so R4-G2-9 is
strictly downstream of R4-G2-8's `f` measurement and should not be attempted
before it. Prior: **0.3**, gated on `f`.

**R4-G2-15 — the key table is the invariant; make everything ride one
traversal.** Generalising: the reachable state set is *identical* across
primes, across evaluation points, and across coefficient streams. Today the
round pays for it once per prime run. If a single traversal carries `k` primes
× `g` evaluation points in its payload, the key cost is paid once for `kg`
results. With evaluation making the payload small, this is the difference
between 82 traversals and 2 at H=19. The design question is only the RAM/CPU
knob: payload = 12·k·g bytes against a ~28 B key. **Nobody in this round has
proposed amortizing anything across runs** — every table in every lane prices
runs as independent. Prior it is worth 2x or better on the ladder: **0.55**.
Cheapest kill: it is a strictly better version of R4-G2-8 arithmetic; if
R4-G2-8's `f` measurement kills the parent, this dies with it.

### 2.3 Two out-of-core shapes, both filed with their kills — R4-G2-10, R4-G2-11

The brief asks what 563 GB of idle NVMe makes possible. My honest answer is:
much less than it looks, and the reason is already banked.

**R4-G2-10 — CLOSED AT FILING: a local/banded state ordering does not exist,
so out-of-core must accept the shuffle.** `designs/10` resolved exactly this
question for the kink engine and the argument is generic to partition DPs on
this lattice: the transition graph *expands* (λ ≈ 7.1, directly observed
scatter), bandwidth would require small separators, and even the literature's
best ordering (Motzkin rank) gives a triangular-not-banded matrix. R4-G6's
external-memory DP is therefore not "measure the fan-out and design the
partitioning" — the all-to-all shuffle is forced, and the cost is full-table
sort/merge passes at ~123 passes and hundreds of TB of I/O. I file this as the
kill R4-G6 was missing, and I file the residue that survives it: **the shuffle
is forced, so the only out-of-core designs worth costing are the ones that
never need the whole table — which is R4-G2-8 and R4-G7, not R4-G6.**

**R4-G2-11 — CLOSED AT FILING: mmap the table onto NVMe and let the kernel
page.** The tempting one-liner. Dead with a number: the access pattern is
random RMW (R4-G2-10: expansion, no locality), so essentially every one of
2.23e9 states × ~5 edges × 41 columns × 22 cells touches a cold page. At even
20 µs per NVMe page fault that is 10^13 µs. It is not close, and the gap is so
large that no amount of readahead, larger pages or queue depth recovers it.
Filed so nobody re-derives it when they see 563 GB free.

### 2.4 If the loop is latency-bound, the lever vocabulary is TLB and concurrency — R4-G2-13

The brief's framing is "bandwidth, not arithmetic, is the wall". Tonight's
measurements support the negative half — arithmetic is not the wall, §1.1 — but
they point at **latency**, not bandwidth: `r4-adv-cost.md` §4.2 measured 2.56
GB/s single-thread against a ~10 GB/s single-core streaming roof. A loop at a
quarter of the streaming roof that does not speed up when you delete a 26-cycle
divide is a loop stalled on random-access misses, not one saturating a bus.

The distinction matters because the levers are different. Against bandwidth you
compress the payload (u16, u8) — and note that **R4-G2-8 compresses it 23x,
which is a bandwidth lever far larger than u16's 2x, so if bandwidth *is* the
wall the flagship row gets better, not worse.** Against latency you buy
concurrency and TLB reach. **`R4-L5` got to the TLB half first and with better
evidence than I have** (3,066,643 minor faults for a 2.36 GB peak RSS at H=15),
so I am not re-filing huge pages. What is left unclaimed:

- **software prefetch of the successor slot** — the successor key is computable
  several iterations ahead of the payload write, which is the textbook shape
  for a prefetch distance of 4–8. ~10 lines, and it is the lever that huge
  pages does *not* subsume, because it attacks miss latency rather than page
  walks.
- **more outstanding misses per core**, which is what makes multi-core scaling
  *better* than a bandwidth model predicts (`r4-adv-cost.md` §4.1 makes this
  point and it is the one argument for L7's 15x that survives) — and which
  R4-G2-4's microbenchmark measures directly.
- **the diagnosis itself**, which is the part nobody has stated: the round is
  saying "bandwidth-bound" and the evidence says *latency*-bound. The two
  prescribe opposite things about payload width. If it is bandwidth, u16 buys
  its 2x and R4-G2-8's 23x is enormous; if it is latency, u16 buys nearly
  nothing and R4-G2-8's value is entirely the RAM, not the wall.

Prior prefetch buys ≥1.15x: **0.35**. Cheapest kill for the family, and it
settles the diagnosis as well: `perf stat` on one H=15 run reporting
`dTLB-load-misses`, `LLC-load-misses` and `stalled-cycles-backend` per
state-stage. Ten minutes, and it decides between R4-L5, this row, and L6's u16
argument at once.

### 2.5 What the disk is actually good for — R4-G2-14

Not the DP. Three uses that are real and cheap, filed as one row because none
deserves its own:

1. **Per-column checkpointing of the H=17..19 runs.** At 8.6 GiB per evaluated
   run (R4-G2-8) or ~200 GiB unevaluated, 563 GB makes the ladder restartable
   instead of all-or-nothing. Given that a 30 h run on a mains-exposed box is
   the shape of thing this project has lost before, this is cheap insurance.
2. **Archiving the full state space at one in-band column** — which is exactly
   what `ADV-C4` (archived-state replay) has wanted for three rounds and has
   never had, because nobody wrote it out. It is free in-pass and impossible
   retroactively, which puts it squarely in R4-G22's class.
3. **Keeping every prime's rows rather than only the CRT result**, so a later
   prime can be added without re-running.

Prior any of it changes a verdict: **0.05**. Prior it prevents one lost run
over the remaining campaign: **0.4**. This is a row about not losing work, and
I file it as such.

### 2.6 The engine materializes dead states and never prunes them — R4-G2-12

A finding from reading the source, and the cheapest structural win I found.

At `cutcount_b1.cpp.59e90660:230-243`, a successor state is inserted into
`nidx`/`npay` and given a full `ST*NA` zero payload **before** the inner loop
discovers whether anything nonzero will be written into it. A state whose
minimum area already exceeds `Nmax` has every `n + dn > Nmax`, so nothing is
ever written — and it survives in the map, generating successors of its own,
for the rest of the run. There is no erase anywhere.

At Nmax = 40 and H ≤ 16 this is minor and invisible; the state space saturates
to the full census anyway (§1.6). It becomes decisive in exactly two places:

- **Truncated-Nmax runs (R4-G10).** At H = 20, Nmax = 6 the engine would
  materialize essentially the entire H=20 census with 21-slot zero payloads,
  so R4-G10's premise — "the reachable state count shrinks hard at small Nmax"
  — is **false for the engine as written** and true only after this fix. That
  is a kill of R4-G10-as-priced and a rescue of R4-G10-as-intended, and it
  costs three lines: don't insert the successor unless the source has a nonzero
  coefficient at some `n ≤ Nmax − dn`.
- **R4-G2-20 below**, which needs cheap large-H small-n runs to exist at all.

This is R4-G4's mincost prune in its cheapest possible form. R4-G4 proposes
computing `mincost(w)` combinatorially per window; the dynamic version needs no
theory, no census script and no new predicate — the DP already knows a state is
dead, it just doesn't act on it. It captures only the "cells to reach" half of
mincost, not the "cells to complete" half, so it is strictly weaker than R4-G4
at Nmax = 40 and strictly cheaper everywhere. **They compose and should both be
done, the three-line one first.** Prior it is a real prune at Nmax = 40:
**0.15**. Prior it is decisive for truncated-Nmax runs: **0.85**.

---

## 3. What a second validated engine makes newly askable — R4-G2-16 .. R4-G2-24

Spin now sweeps m = 1..16 in **88.6 s at 90.7 MB** and matches all 640 cells,
with its binary's sha256 in the log and three stencil mutants firing 12/12/4.
That is a validated instrument that costs less than two minutes per question.
The round has been treating it as a *counter* for two cells. It is worth much
more as an instrument.

### 3.1 Pre-register the parity predictions before the ladder runs — R4-G2-16

Zero cost, and it is the highest-value thing on this list per unit of effort.

Spin can produce `T(40,H) mod 2` for H = 17, 18, 19 — the exact cells the B1
ladder is about to compute over the next weeks — at a re-priced cost of hours,
not days (`r4-adv-cost.md` §2.3). Today the campaign's pattern is: run the
expensive thing, then note that the cheap thing agrees. That is a post-hoc
agreement, and a skeptical reader discounts post-hoc agreements because they
cannot see what would have happened on disagreement.

Instead: **run spin first, commit the predicted parity bits to git with the
binary's sha256 and the date, and only then run the ladder.** The ladder either
confirms a prediction that was on the record before it started, or it
contradicts one, and both outcomes are worth strictly more than the same bits
obtained afterwards. It costs nothing but ordering.

This generalises past parity — it is a *protocol*, and it is the answer to a
weakness `r4-adv-ind.md` §8 identified in a different form (transmission loss
between deliverable and summary): a pre-registered prediction cannot be
softened in the retelling. Prior jasonp likes it: **0.7**. Prior it changes any
technical outcome: **0.1** — the value is entirely in what a referee can check.
**Cheapest kill:** if spin's m=17..19 cost re-price is wrong by an order (GATE
4's `ns_per_transition` settles it, and it is minutes), the ordering forces the
ladder to wait, and then it is not free.

### 3.2 The mutant fixtures are measured at n ≤ 7 and the band is not — R4-G2-17

`r4_spin_gates.log` shows the three mutants run against the 49-cell set
(`compared=49`, of which 28 are the Python-validated `hlen` cells). The clean
run at `compared=640` was `mutant=none`. So the detector's measured power —
12/12/4 — is a statement about **n ≤ 7**, and `r4-adv-ind.md` §3.1 already
observed that the symmetric case (rook, 4 cells) is the thinnest control
guarding the most dangerous class.

Nobody has asked the obvious next question: **does detection power grow or
shrink with H and n?** Three more runs of 88.6 s each, mutants against the full
640-cell oracle, answer it. If the rook mutant flips 400 of 640 cells, the
control is far stronger than "4 cells" suggests and the campaign should say so.
If it flips 4 again — i.e. detection does not grow with the comparison set —
that is a much more alarming fact about the oracle than anything currently on
file, because it would mean the disagreement surface is concentrated at tiny n.
Five minutes. Prior detection grows roughly with cell count: **0.75**; the
value is in the 0.25.

### 3.3 The stencil common mode is a finite object — enumerate it — R4-G2-18

`r4-adv-ind.md` §7 concludes that after everything else is cleared, **the whole
residual common mode is one hand-written king-adjacency stencil**, and
JOB-IND-1 (`experiments/tristruct/r4_indoracle_brute.py`, written but not yet
run) closes it against the literal 3×3 definition at H ≤ 6.

The stronger and still-cheap version: the space of candidate stencils is
*finite and small*. `gather()` reads four previously-processed slots out of a
radius-1 window; widen to radius 2 and there are ~12 candidate offsets, so
~4096 stencils. With a fast engine, enumerate **every** one of them and report
which are consistent with `T(n,H)` for n ≤ 10, H ≤ 6.

If the king stencil is the **unique** consistent one, the stencil objection is
closed by exhaustion rather than by argument — a categorically stronger
statement than "we checked ours against brute force", because it also covers
the case where our *definition* of the neighbourhood is the shared
misconception. If several stencils are consistent at that range, the output is
the list of them and the smallest (n, H) that separates each from king — which
is the test suite the campaign should have been running all along.

Prior king is unique at n ≤ 10, H ≤ 6: **0.8**. Cost: the mutant machinery
already exists in both engines; the work is a loop over stencils. Hours of
laptop-scale compute at most. **Cheapest kill:** if the enumeration is not
closed under the engine's column-major processing order — i.e. some offsets are
not expressible as slot reads — the space is not 4096 and the exhaustion
argument weakens to "exhaustive over expressible stencils", which is still
worth having but is a smaller claim.

### 3.4 The blind spot nothing in this campaign can see — R4-G2-19

Every incumbent-free oracle in the campaign runs at small H. JOB-IND-1 is
scoped `n ≤ 12, H ≤ 6`. `probe_cutcount_dp.py` validates at H ≤ 4. The spin
pipeline's self-grown truth reaches n ≤ 8. The band is **H = 15..21**.

And `gather()` is H-indexed: `r4-adv-ind.md` §1.2 records the four slot offsets
as slot 0, slot **H−2**, slot **H−1**, slot **H** — two of the four depend on
H, and the boundary guards are at `r = 0`, `r = H−1`, `c = 0`. That adversary
verified them "by hand and at the guards" and filed, in its own NOT
ESTABLISHED list, that it did not verify them programmatically.

So the class of error that is invisible to every check this campaign has ever
run is: **an index error in the stencil or the guards that manifests only at
heights above those any oracle reaches.** It is not exotic; off-by-one at a
window boundary is the single most common defect shape in packed-slot code, and
this code packs H+1 five-bit slots into a u128.

The fix does not require counting anything. Write a standalone check that, for
every `H ≤ 21`, every `r < H` and `c ∈ {0, 1}`, computes the set of grid cells
`gather()` reads and asserts it equals the literal set of king-neighbours of
`(r, c)` that precede it in the processing order. That is a pure index audit —
seconds to run, no DP, no oracle, no counting — and it closes an entire error
class at every band height at once. **It is the cheapest independence-relevant
thing anywhere in the queue** and I am surprised it does not exist.

Prior it finds a defect: **0.1**. Prior it is worth doing anyway: **0.95** —
a negative result here is a sentence a referee can be handed, and the cost is
an hour.

### 3.5 Get an incumbent-free oracle into the band's height range — R4-G2-20

R4-G2-19 audits indices without counting. This one counts, at band heights, for
the first time.

Composition: with R4-G2-12's three-line dead-state prune, a run at **H = 20,
Nmax = 8** becomes cheap — the state space collapses because almost every
window is unreachable within 8 cells. On the other side, growing every fixed
king animal of size ≤ 8 by flood fill and bucketing by bounding-box height is
milliseconds (the grower in `r4_indoracle_brute.py` already does exactly this,
and `r4_spin_reference_gympie.log` shows totals to n=8 already computed:
1, 4, 20, 110, 638, 3832, 23592). Compare `T(n, 20)` for n ≤ 8 between the two.

Most of those cells are zero — an animal of 8 cells cannot have height 20 —
which sounds like it makes the test vacuous and in fact makes it *sharper*: the
engine must produce exact zeros at H=20 for n < 20, and it must produce them by
running its H=20 index paths. A stencil or guard error at slot H−2 with H=20
would very plausibly produce a nonzero. Then take H = 12..16, where nonzero
cells exist at n ≤ 12 and the brute force still runs, and compare real values —
which is JOB-IND-1 extended from H ≤ 6 to H ≤ 16 at essentially no extra cost,
because the brute side is bounded by n, not by H.

**That last observation is the point of the row and it is one sentence: the
brute-force oracle's cost depends on n, not on H, so restricting H ≤ 6 bought
nothing and gave up everything.** JOB-IND-1 should be re-scoped to `n ≤ 12,
H ≤ 21` before it is run. Prior the re-scope is free: **0.85** (the grower is
n-bounded; only the B1 side needs the prune, and only above H=16 where the
committed binary refuses anyway — see R4-G2-23).

### 3.6 Spin as a search instrument, not a counter — R4-G2-21, R4-G2-22

**R4-G2-21 — is `T(n,H) mod 2` 2-automatic in n?** Sequences of this kind
frequently are (Pascal, Motzkin, Catalan mod 2 all have finite 2-kernels), and
spin makes the question cheap for the first time: it produces parity for
arbitrary `n` at a fixed `H` for pennies, so run H = 6..10 out to n = 128 and
compute the 2-kernel rank. If the kernel closes at small rank, then
`T(40,20) mod 2` and `T(40,21) mod 2` follow from a finite automaton fitted at
small H — and, better, an automaton is the kind of object one can then *prove*
correct by a transfer-matrix-mod-2 argument, which would give a level-1-and-2
clean bit at the two cells nothing else reaches, with no m=21 run at all.

Prior the kernel closes: **0.15** — the objects that are 2-automatic usually
have a product formula or an algebraic GF mod 2, and this one has neither known
— but the test is a few hours of laptop-scale work and the payoff is a proved
route to the exact cells the campaign has written off. **Cheapest kill:**
compute the 2-kernel rank at H=6 out to n=128. If it exceeds ~30 without
closing, the family is not automatic at any useful H and the row dies. Note the
kill also produces something useful either way: a parity fingerprint of the
band far past n=40.

**R4-G2-22 — continuous differential testing.** Spin and B1 now agree on 640
cells. The pair is cheap enough (88.6 s) to be a *standing* control rather than
a one-off: a script that picks random `(m, n, prime)` triples, runs both, and
compares, run on every future B1 patch. `r4-adv-ind.md` §3.2 established that
the seven gates cover the exact path while the patch lives entirely in
`--modp`, so the round already has a demonstrated hole exactly where a cheap
differential fuzzer would sit. Prior it catches something over the remaining
campaign: **0.3**. Cost: an afternoon, then free forever. Note its limit
honestly — `r4-adv-ind.md` §2.2 shows spin and B1 share the stencil and the
colouring semantics, so this fuzzes implementations, not rules.

### 3.7 The `H <= 16` cap in the B1 binary is not a real limit — R4-G2-23

`cutcount_b1.cpp.59e90660:316` and `:381` both hard-refuse `H > 16`. The key is
`H+1` slots at 5 bits packed into a u128, so H=21 needs 110 of 128 bits and
H=24 is the true ceiling. **The cap is conservative, not structural.**

That matters for two rows above: R4-G2-20 wants B1 at H=20 with small Nmax, and
R4-G2-17/18 want the oracle extended. It also matters for the ladder — the
binary that everyone is planning H=17..19 runs with currently exits 1 on those
heights, which is a fine fail-closed default and a thing somebody should notice
before dispatching a 30-hour job.

Filed with the caveat that makes it a row rather than a note: **raising the cap
without re-deriving the `Succ out[12]` bound would be unsafe.** R4-P2 closed
that bound at `b ≤ floor((H+1)/2)`, which gives 11 at H=21 — inside 12, with
one slot of headroom, and R4-P2's argument has never been run. So the cap
should be raised *together with* the runtime guard r4-perf recommended, not
before it. Prior the raise is safe with the guard: **0.85**.

### 3.8 What tonight's second engine does *not* make askable — R4-G2-24, filed with its kill

**CLOSED AT FILING.** The tempting inference is that a cheap validated second
engine lets the campaign skip the B1 ladder at H=17..19 and take spin's parity
instead. It does not, and the reason is already banked twice over: parity is
one bit per cell, `r4-inv.md` §5 correctly states that agreement moves the odds
by at most 4x for two cells, and `r4-adv-ind.md` §2.2 establishes that spin is
B1's DP specialised to `q = 2` — sharing the stencil and the colouring
semantics outright. Spin's independence value is against the **kink** engines
only. Stacking more spin runs does not accumulate into a second source for the
band; it accumulates one bit per cell against one rule class.

Filed so that "spin is cheap, run spin at everything" does not become the
round's next plan without someone writing down what it would buy. What *is*
worth taking from it is R4-G2-16's ordering: the bits are nearly free, so take
them, but take them as pre-registered predictions rather than as a substitute.

---

## 4. Second pass — what my own rows share — R4-G2-25

Reading §1–§3 back, two things, and the first is a method the round should
adopt explicitly.

**(a) Every row I filed replaces a system-level estimate with a component-level
measurement, or replaces something being carried with something cheaper to
carry.** The two halves are not independent. The reason the round has been
pricing components with system models — 40 ns/slot-op from a 328x larger
payload, 57 B/entry from an RSS decomposition, 15x from a streaming ratio — is
that the *system* measurement (run the DP at H=19) is enormous, so the model
felt like the only option. It never was. A random-scatter microbenchmark, a
synthetic-key table fill, and a truncated-Nmax run each cost ten minutes and
each pins one of the numbers the round's whole cost table rests on. Tonight
proved the point twice in opposite directions: INV-8's model was 16–82x
pessimistic and r4-perf's was ~2x optimistic. **The lesson is not that our
estimates lean one way. It is that op-counting models have an error
distribution wide enough to swamp the decisions they are being used for, and
that the components are cheap to measure separately.** If the round adopts one
practice from my pass, it should be: *before pricing a lever inside the engine,
ask whether the quantity can be measured outside it.*

**(b) The rows that clear the entry-ticket levels and the rows that reach the
band are disjoint sets, and I did not manage to file a single row in both.**
R4-G2-8, -9, -12, -13, -15 reach further; none of them changes the rule class,
so none clears L1 or L2. R4-G2-16 through -22 clear or sharpen independence;
none of them reaches a cell the campaign does not already have. This is the
same split R4-G21 named in a different currency, and I want to add the
uncomfortable observation: **the only route on the whole board that is claimed
to do both is the Lean proof, and it reaches its 95.85% by proving the
incumbent's own rule rather than by recounting anything.** A generator's job is
to notice when a search has stopped producing a kind of thing, and this one
has: nobody has filed a *new rule class that reaches the band* since B1, and
B1 stops at H=16 for reasons (§3.7) that turn out to be a hard-coded constant
rather than a wall.

---

## 5. Stale and subsumed rows — the queue audit

Tonight invalidated several cost estimates. These are rows whose *numbers* are
now void; none is an edit to another agent's row, and the triage is the lead's.

**Stale — priced against a number measured wrong tonight:**

| row | why it is stale now |
|---|---|
| `R4-INV-1` | Prices R4-SPIN-JOB-0 at "~5.1 thread-hours" and at "0.94% of SPIN-JOB-1's 22.6 thread-days". **Measured: 88.6 s.** Both figures in the row are void; the job it requests has been run and passed. The row should be CLOSED against `r4_spin_m16.log`. |
| `R4-INV-3` | Kills q=4 with "~7.5 thread-years", derived from the same 40 ns/slot-op anchor that `r4-adv-cost.md` §2 voided. The *conclusion* (q=4 is much worse than q=2) survives on the growth ratio alone, which is measured; the **number does not**, and should not be quoted. Re-derive from the 88.6 s anchor before anyone repeats "7.5 thread-years". |
| `R4-INV-2` | Same defect, same direction: q=3's cost is priced off the model, not the measurement. Its conclusion may well *improve* — re-price it. |
| `R4-P1` / PERF-JOB-1 | Estimated 2.5x (1.8–3.5x). **Measured 1.12–1.28x, declining with height** (§1.1). The job is done; the row's estimate is refuted by its own job. Every downstream table using 2.5x — `r4-perf` §2 in full, `r4-adv-cost.md` §4.1's ladder of scenarios, R4-AC3's "5.7 days" floor — needs the substitution. |
| `R4-AC3` | Its arithmetic is right and its input is now wrong: the "no sharding at all" floor of 5.7 days uses 2.5x. At the measured factor the floor is **~13.5 days**. The row's *finding* (sharding is not the go/no-go) survives and is strengthened — at 1.05x, sharding matters more, not less. |
| `R4-P4` | "H=20 … ~1.7 h of dalby" composes 2.5x with the 15x and a 15-run count that `R4-AC2` corrected to 16. Two of its three factors are now known wrong. The RAM half of the row (146.8 GiB against 121) is the part that stands. |
| `R4-G10` | Its premise — that reachable state count shrinks hard at reduced Nmax — is **false for the engine as written** (§2.6): dead states are materialized and never pruned. The row is not wrong in intent; it is unrunnable as priced until R4-G2-12's three lines land. |
| `R4-SB1` | Still reads "UNCOMPILED … OPEN — needs the lead to build and gate". It has been built, gated and run, with a sha256 in `r4_spin_gates.log` and `r4_spin_m16.log`. `R4-AI3`/JOB-IND-3 asked for these receipts and they now exist; both rows should close against them. |
| `R4-AC5` | Filed at 00:21: "no receipt on disk" for the perf patch and spin engine. **Both receipts now exist** (§0), timestamped 01:29–02:13. The finding was correct when filed and the round should record that it was closed by production of the artifacts rather than by argument. |

**Subsumed:**

| row | subsumed by | why |
|---|---|---|
| `R4-G6` (external-memory sort/merge DP) | R4-G2-10 | The design question it asks — measure fan-out, choose a partitioning — is foreclosed by `designs/10`'s expansion argument: no local ordering exists, so the shuffle is forced and the pass count is the ~123-pass, hundreds-of-TB figure. What survives is not a design but a kill. |
| `R4-G4`'s combinatorial mincost census, *partially* | R4-G2-12 | The "cells to reach" half is obtained dynamically for three lines and no theory. R4-G4 keeps the "cells to complete" half, which is the harder and more valuable half, and should be re-scoped to it. |
| `R4-A4`'s multi-core DP probe, *for the sharding number only* | R4-G2-4 | R4-A4 asks for the sharding factor by running the DP multi-core; the quantity is measurable in a 30-line standalone with no DP, no correctness risk and no gate. R4-A4 still has independent value as an end-to-end check; it should not be the *first* measurement of the 15x. |
| `R4-AI1`/JOB-IND-1 as scoped (`H ≤ 6`) | R4-G2-20 | The brute-force side's cost is bounded by n, not H. Restricting to H ≤ 6 gave up the entire band-height index surface for nothing. Re-scope to `n ≤ 12, H ≤ 21` before running — it is the same job. |

**Not stale, and worth saying:** `R4-G14`'s re-pricing from 5 runs to 2 is
untouched by tonight and gets *more* valuable as the wall estimates rise;
`R4-AC4`/ADV-JOB-1 (the u32-vs-u16 bandwidth test) is still the right 20-minute
measurement and §1.1 makes it more interesting, not less, because a patch that
buys 1.12x at H=15 is evidence the loop is stalled on something u16 might
actually relieve; and `R4-AC2`'s u8 prime-count correction stands.

---

## NOT ESTABLISHED

- **`f`, the payload's share of the wall** (§2.1). Every number in R4-G2-8's
  table is a function of `f = 0.9`, which is EXTRAPOLATED from
  `r4-adv-cost.md` §1.4's cycle accounting and has never been measured. One
  truncated-Nmax run settles it and the row should not be dispatched before it.
- **Window counts at H = 17..20.** EXTRAPOLATED by the measured ratio chain
  (3.00 → 3.12 per height) anchored on ADV-I4's exact 2,228,466,695 at H=21.
  My chain lands ~6% below that anchor when run forward from H=16, and I
  rescaled to the anchor rather than to my chain.
- **`c(H)` beyond H=16.** Extrapolated at the geometric-mean 1.0729/height over
  the five measured points, per `r4-adv-cost.md` §1.3. Every wall figure in
  §2.1 inherits that.
- **The speedup decline continuing past H=15** (§1.1). Three points. The H=13
  baseline is itself ambiguous (188.2 s originally, 182.8–185.6 s on four
  re-runs), which moves that point's speedup between 1.25x and 1.28x. The
  direction is unambiguous; the extrapolation to 1.0x at H=17 is not.
- **Whether the dead-state prune (§2.6) is correct as three lines.** I read the
  insertion path and the `iszero` skip; I did not check whether any downstream
  code (the column sum at line 262, the `--states` mode) assumes the successor
  set is closed. It may need four lines.
- **Whether `gather()`'s offsets are right at every (H, r, c).** That is
  R4-G2-19's whole point and I did not run it; `r4-adv-ind.md` verified them by
  hand at the guards and filed the same gap.
- **The 2-kernel rank of `T(n,H) mod 2`** (§3.6). Pure speculation, filed with
  its kill.
- I ran **no compute on any machine**. The dalby and ayr readings in §0 are
  `ls`, `grep`, `df`, `free` and `uptime` over ssh. I did not verify any claim
  in `r4-perf.md`, `r4-inv.md` or `r4-spinbuild.md` beyond the log lines quoted
  in §0, and where I re-price another lane's table I am changing an input, not
  its measured anchors.
