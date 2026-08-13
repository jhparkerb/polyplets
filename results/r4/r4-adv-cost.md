# r4-adv-cost — are the numbers real?

ADVERSARY, round 4, 2026-08-13. **No compute was run.** This is reading,
`git show`, read-only ssh to dalby and ayr, and arithmetic. Where I compute a
number below I say which log line it came from, so the arithmetic can be
re-done against me.

Ground truth for everything in §1 is
`dalby:~/src/pm-b1/experiments/tristruct/r4_a_modp_bpw.log`, read 2026-08-13
00:07 and again 00:12 EDT. I re-derived every wall, RSS, total and marginal
slope from it myself rather than taking any lane's arithmetic.

---

## 0. Verdict in six lines

1. **The single largest misprice in the round is INV-8's 22.6 thread-days, and
   it is wrong by 16–82x in the *favourable* direction.** Re-priced against
   tonight's measured B1 walls, m=18..21 is **6.6 to 33 thread-hours**. The
   lead's hypothesis was right, and it is an order, not a factor (§2).
2. **r4-perf's u8 prime count is arithmetically wrong** — 14 primes below 256
   give **108.249 bits**, not the ~112 the table assumes, against a 110.842-bit
   target. Round 3's defect class, reproduced. r4-a's "16 runs" is the correct
   figure and r4-perf's "14+1 = 15" is not (§3).
3. **The 15x sharding factor is not load-bearing for the decision it is being
   blamed for.** With L5+L6 and *zero* sharding, H=19 is ~9 days, not 55. The
   thing that actually changed the round's answer is the MEASURED 2.5x
   exact/modp ratio plus the RAM lever — both grounded. Sharding decides
   9 hours vs 9 days, not yes vs no (§4.1).
4. **r4-perf's 28% slope reconciliation is correct and I can strengthen it.**
   It dropped the H=12 point; that point supplies a *third* marginal slope
   (1,235.9) which makes the monotone decline unambiguous. Overhead amortizing,
   not a rehash step. The lane was right and the lead's doubt should be
   withdrawn (§1.2).
5. **Two of tonight's three "compiled and gated" claims have no receipt on
   disk.** The Lean probe left a complete log. The perf patch and the spin
   engine left none, no binary exists on any of the three boxes, and PERF-JOB-1
   was never run (§6.2).
6. **r4-lean's 5-7 sessions: increments 3–6 are priced on nothing**, by the
   lane's own admission. "Bookkeeping rather than mathematics" is a judgement,
   and it is the wrong word for `encode_faithful` (§5).

---

## 1. The measured record, re-derived

### 1.1 What the log actually says

Every figure here is from an `event=done` line or a `/usr/bin/time -v` block in
`r4_a_modp_bpw.log`. Binary sha256
`4e3817b693d122eee7adf4c903b0f469ddbdd6c9349127e4a45a4b59480f8711`,
`git=48ac1089-dirty`, single thread, p = 2147483647, host dalby.

| H | windows | wall_s | peak_rss_mb | max RSS KB | B/window |
|---|---|---|---|---|---|
| 12 | 107,241 | **53.2** | 114.9 | 117,624 | 1,123.1 |
| 13 | 306,858 | **188.2** | 350.2 | 358,556 | 1,196.5 |
| 14 | 891,074 | **599.5** | 956.6 | 979,596 | 1,125.7 |
| 15 | 2,624,197 | **2,065.1** | 2,363.6 | 2,420,292 | 944.4 |
| 16 | 7,832,667 | in flight | — | — | — |

**r4-perf's H=13/14/15 walls and its three B/window totals reproduce exactly.**
Its H=14 wall is written as 600 against the log's 599.5 — rounding, not a slip.

**H=16, re-projected.** r4-perf read the log at column 13 of 41 (elapsed
2,074.9 s) and projected ~7,200 s. I read it at column 27 (elapsed 4,507.0 s).
Columns 13→27 took 2,432.1 s, 173.7 s/column, and the last two intervals were
169.9 and 167.1 — still falling. Fourteen columns remain at ~167–174 s, giving
**~6,850–6,950 s**. r4-perf is ~4% high. Immaterial, but replace it with the
log's own `wall_s=` when the job lands; the job was still running at 00:12
(pid 2498057, etime 01:22:57).

### 1.2 The 28% marginal-slope disagreement — r4-perf is right

Marginal slopes, computed from the `/usr/bin/time` max-RSS column:

| interval | ΔRSS bytes | Δwindows | B/window |
|---|---|---|---|
| 12→13 | 246,714,368 | 199,617 | **1,235.9** |
| 13→14 | 635,944,960 | 584,216 | **1,088.5** |
| 14→15 | 1,475,272,704 | 1,733,123 | **851.2** |

r4-perf reports only the last two, because it dropped the H=12 point. **The
dropped point strengthens its case.** Its argument was "a rehash event is a
step — one slope out of line, the others agreeing; here both decline
monotonically." With two intervals that is a two-point trend and the word
"monotonically" is doing more work than the data supports. With three it is
1,235.9 → 1,088.5 → 851.2, monotone over three intervals with no step
anywhere, which is what per-state allocator overhead amortizing looks like and
is not what a rehash discontinuity looks like.

**Verdict: r4-perf's call to override the ladder-gate's ">15% take the max"
rule is CORRECT, and its choice of 944 B/window (the H=15 total, an upper
bracket on a declining sequence) is conservative in the right direction.** Its
own predicted H=16 total, ~880 B/window = 6.4 GiB, follows from persisting the
851 slope and I get 882.4 B/window = 6.44 GiB the same way. Where the lead
doubted this lane, the lane was right.

One qualification the lane should have made and did not: **944 B/window governs
only the "as-is" column of its §2 RAM table.** Every H=19 and H=20 verdict runs
off 388 or 224 B/window, which come from the L5 flat-container model, not from
any measurement. Those are audited in §4.3.

### 1.3 The growth constant `c(H)`, re-derived

`c(H) = wall / (windows × H)`, seconds:

| H | 12 | 13 | 14 | 15 | 16 (my projection) |
|---|---|---|---|---|---|
| c(H) ×10⁵ | 4.134 | 4.718 | 4.806 | 5.246 | 5.506 |
| ratio | — | 1.141 | 1.019 | 1.092 | 1.050 |

r4-perf writes "It grows ~9% per height above H=14" and extrapolates at 1.09.
**That is one interval (14→15 = 1.092) presented as a trend.** The ratios are
noisy: 1.141, 1.019, 1.092, 1.050. Geometric mean over 12→16 is **1.0743**.

Does it matter? Re-running its H=19 as-is wall at 1.0743 off my c(16) gives
**80.9 h** against its 88.2 h — 8% apart. **It does not matter, and I decline
to manufacture a finding out of it.** The extrapolation is robust to the growth
constant over this range; r4-perf's number is conservative. Flagged only so
nobody quotes "9% per height" as measured. It is one measured interval.

### 1.4 The anchor that lets me price other people's kernels

This is the most useful thing tonight's log produces and no lane extracted it.

At H=14: 599.5 s over 41 columns × 14 stages × 891,074 states =
5.115×10⁸ state-stages → **1,172 ns per state-stage, MEASURED**. At the
inherited branch factor of 1.667 successors/state-stage (20.8×10⁶
transitions/column ÷ 12.475×10⁶ state-stages/column, an r3 figure I did not
re-derive) that is **703 ns per transition** and, over the modp payload's
41 slots × 2 coefficients, **8.6 ns per slot-op ≈ 26 cycles at 3 GHz**.

Twenty-six cycles is one non-pipelined 64-bit `udiv` on this core and nothing
else. **r4-perf's central thesis — that the inner loop is a divide standing
where an add belongs — is independently confirmed by tonight's log, to within
the width of a single instruction.** The lane reached it by inference from the
2.5x exact/modp gap; the arithmetic above reaches it directly.

### 1.5 The box, which nobody established

Read-only from dalby, 2026-08-13:

    Model name: Neoverse-N1     CPU(s): 80     max MHz: 3000
    NUMA node(s): 1             node0 CPU(s): 0-79
    Mem: 125 GiB total, 116 GiB available (with the H=16 job resident)

**One NUMA node.** No lane established this and it is directly favourable to
L7: the block-synchronous scatter's worst structural risk on a multi-socket box
— shard owners pulling source payloads across an interconnect — does not exist
here. r4-perf's L7 section would have been stronger if it had checked.

`ayr` was reachable; I did not need anything from it beyond §5's Lean survey,
which r4-lean had already measured correctly.

---

## 2. INV-8: the 22.6 thread-days is off by an order, and the error favours the route

The lead asked whether re-pricing from a measured `ns_per_transition` moves
22.6 thread-days by an order rather than a factor. **It does. Here is the
reductio, using only tonight's log.**

### 2.1 What the model charges

`results/r4/r4-inv.md` §1.2: `slot-ops(m) = 41 cols × m stages × W(m) states ×
3 branches × 41 area slots = 5043·m·W(m)`, costed at 40 ns/slot-op. I checked
every line of that arithmetic and **it is clean**: 5043×21 = 105,903;
×286,292,183 = 3.032e13; the four rows sum to 4.883e13; ×40 ns = 1.953e6 s =
22.6 thread-days. I also re-chained W(m) from the seeds W(2)=15, W(3)=37 and
t_m from t_1=3, t_2=7 and hit every banked value including t_17 = 3,880,899
and W/t = 0.8995. **The arithmetic is not the problem. The constant is.**

Dividing out, the model charges **41 × 40 = 1,640 ns per transition**, i.e.
3 × 1,640 = **4,920 ns per state-stage**.

### 2.2 The reductio

| kernel | payload moved per transition | arithmetic per transition | ns/transition |
|---|---|---|---|
| B1 exact I256 | 3,936 B | 123 slot-ops, each a 4-limb 256-bit multiply-add | 1,899 MEASURED |
| B1 `--modp` | 328 B | 82 slot-ops, each an add + a non-pipelined 64-bit `udiv` | **703 MEASURED tonight** |
| spin, as priced | **12 B** | **two lane-parallel adds, one u64 and one u32, no division** | 1,640 ASSERTED |

**The 22.6 thread-day figure asserts that a kernel moving 12 bytes with two
register adds is 2.3x slower per transition than the divide-bound residue
engine measured on the same box tonight moving 328 bytes with 82 divisions.**
Per byte of payload it is 285x worse than the exact I256 path. There is no
mechanism for that and none is offered.

The defect is a units error, exactly as `results/r4/r4-spinbuild.md` §1.4
warned before anyone quoted the number: *"The cost model's 'slot-op' counts 41
operations per transition. This kernel does two."* r4-spinbuild caught it and
refused the estimate ("minutes is as plausible as hours", §4.2). r4-inv did
not, the lead's correction to `results/triangle-r3-synthesis.md` propagated it,
and the queue carries it.

### 2.3 The re-price

Transitions for m = 18..21, from the same census
(`123·m·W(m)`): 4.505e10 + 1.148e11 + 2.917e11 + 7.396e11 = **1.191e12**.

| ns/transition | basis | m=18..21 total |
|---|---|---|
| 4 | two lane-adds + O(1) rank update, compute-bound, everything cached | 1.3 thread-hours |
| 20 | two L2/DRAM misses on the destination rank at ~10 outstanding misses/core | **6.6 thread-hours** |
| 40 | as above, halved MLP | 13.2 thread-hours |
| 100 | fully latency-bound, one serialized DRAM round trip per transition | **33 thread-hours = 1.4 thread-days** |
| 1,640 | **the filed figure** | 22.6 thread-days |

**Bracket: 6.6 to 33 thread-hours for the whole of m = 18..21, single thread.**
Factor 16 to 82 overstated. I mark my own bracket EXTRAPOLATED — it is reasoned
from the kernel's byte count and this core's miss concurrency, not measured —
but the *upper* end of it is still 16x below the filed number, so the direction
does not depend on which end is right.

The same correction hits the gate: R4-SPIN-JOB-0's "≈ 5.1 thread-hours" for
m = 1..16 becomes **minutes**, which is what r4-spinbuild §4.2 already said.

### 2.4 What this changes

Everything, in INV-8's favour.

- **It was ranked against its competitors on a number nobody had measured, and
  the number penalized it.** The lead asked me to establish whether that is the
  situation. It is, and the direction is the opposite of the usual: 22.6
  thread-days made INV-8 look like a job needing a scheduled multi-day
  sole-tenant window on dalby, competing for the same box as the B1 ladder. At
  6.6–33 thread-hours it competes with nothing. It can run overnight beside the
  H=16 job on 80 idle cores.
- **The lead's wave composition was right for the wrong reason.** Building the
  spin engine tonight was correct; the justification on file (a 22.6-thread-day
  route worth pre-building) was not the reason it was correct.
- **R4-SPIN-JOB-0 stays the right next job and its priority goes up, not down.**
  It is the only thing that converts my bracket to a measurement, and at minutes
  of wall it is now cheaper than the argument about it.

### 2.5 What I could not check

- I did not read `r3_spin_pipeline.py` or `r4_spin_engine.cpp` line by line.
  r4-inv's §1.2 arithmetic I re-derived; its correctness *as a description of
  the algorithm* I take from r4-spinbuild's function-by-function table.
- The branch factor 1.667 is inherited from r3's "20.8e6 transitions/column at
  H=14". If that figure is wrong, my 703 ns/transition moves, but the
  state-stage anchor (1,172 ns, derived only from the log and the census) does
  not, and the reductio survives on that alone.
- The percentages 4.1582% / 2.8431% / 7.00% are quoted, not recomputed. I did
  confirm they sum as claimed.

---

## 3. The bit budget — one real error, and it is r4-perf's

Round 3's cost adversary caught 13 primes claimed to cover a 103-bit value. The
lead asked me to check this class again. **There is one, and the two lanes
disagree with each other about it.**

### 3.1 The anchor is sound

From `results/triangle.txt`, summing row 40: `sum_H T(40,H) =
56749893611764175164545926946127`, **106 bits**. `41 × a(40)` is
**110.842 bits**, so r4-a's `C_H(40) < 2^112` is correct and one bit loose.
Its measured comparanda (C_12(40) = 105 bits, C_14 = 106, C_16 = 107) are
consistent. **r4-a §2.5's anchor: CONFIRMED.**

### 3.2 The prime products, computed exactly

Not `k × log2(bound)` — the actual product of the k largest primes below the
bound, which is what CRT recovers modulo.

| payload | k largest primes below | product bits | ≥ 110.842? | primes needed | + RED-D held out |
|---|---|---|---|---|---|
| u32, p < 2³¹ | 4 | **124.000** | yes | 4 | **5** |
| u16, p < 2¹⁶ | 7 | **111.991** | yes, by 1.15 bits | 7 | **8** |
| u8, p < 2⁸ | 14 | **108.249** | **NO** | — | — |
| u8, p < 2⁸ | 15 | 115.684 | yes | 15 | **16** |

**r4-a's `k = 4 + 1 = 5` for 31-bit primes is CORRECT.** Arithmetic verified
independently.

**r4-perf's L6 table row `u8, p < 2^8 … 14+1 = 15` is WRONG.** Fourteen primes
below 256 give 108.249 bits against a 110.842-bit target. The slip is the exact
round-3 defect: treating k primes near a bound b as delivering k·log2(b) bits.
Near 2³¹ that is harmless (2147483647 is 2³¹−1). Near 2⁸ it is not — the
fourteen largest primes below 256 run 251 down to 179 and average 7.73 bits
apiece, not 7.97.

**r4-a §4.3's "u8 needs 16 runs" is the correct figure.** The two lanes
disagree by one run and r4-a is right.

### 3.3 How much it matters, honestly

Little, for three reasons, and I rank it low accordingly.

- The affected rows are u8, which nothing in §2 of r4-perf actually recommends
  except the H=20 line that is RAM-blocked anyway. u16's 7+1 = 8 survives.
- The consequences are 15 runs → 16: r4-perf's u8 "total wall 1.26x" becomes
  1.34x, H=19-as-is "55 days" becomes 59, H=20's "~1.7 h" becomes ~1.8 h. No
  verdict moves.
- **RED-D is fail-closed against exactly this.** Reconstructing from k−1 primes
  and predicting the k-th fails with probability 1 − 1/p if the modulus product
  is short of the value. r4-a designed the control that catches its
  counterpart's arithmetic error. That is the battery working.

But the sentence in the tin does not match the contents, the tin is a table
that ranks payload widths against each other, and the round asked me to look.

### 3.4 A related internal inconsistency in r4-perf §2

"H=19 as-is: u32 does not fit anywhere; u8 fits dalby alone, 15 runs: 55 days"
multiplies the **944 B/window** wall (88.2 h, an as-is figure) by the **u8** run
count. As-is u8 would move less payload and, on the lane's own
bandwidth-boundedness premise, run faster than 88.2 h. The row is internally
muddled. It is the number being replaced, so nothing rests on it; noted so it
is not quoted.

---

## 4. r4-perf's four flagged claims

### 4.1 (a) Does the sharding argument survive the transition structure?

**The structural objection the lead raised does not land, and the number is
much less load-bearing than the brief assumes.**

On the merge eating the gain: I do not think it does. In the block-synchronous
scatter, each source payload is read once per outgoing edge whether one thread
or eighty runs it — the same ~5 reads a single thread performs — so sharding
adds no payload traffic. What it adds is the buffered edge record: 32 B written
and 32 B read back per edge, against 656 B/edge of payload traffic already
moving. **+10%, not a gain-eater.** The buffer footprint arithmetic checks out
(1M sources × ~5 edges × 32 B = 160 MB) and at 80×80 per-(thread,shard) buffers
that is ~25 KB each, which is a sane granularity. And §1.5's single NUMA node
removes the interconnect risk entirely.

Two things r4-perf did not model, one in each direction:

- *Against it.* The target accumulate is a read-modify-write of 164–328 B at a
  **random** index in a 40+ GB arena, not a stream. Its ceiling is set by DRAM
  page activation and TLB reach, not by STREAM bandwidth, and the 15x is derived
  from a streaming ratio. Huge pages are unmentioned; at 4 KB pages a 40 GB
  arena is 10M pages against a few thousand TLB entries.
- *For it.* Random access is latency-bound per core, and latency-bound loops
  scale *better* with core count than streaming ones do, because each added core
  brings its own miss concurrency. The bandwidth roof is reached later, not
  sooner.

The two do not cancel in any way I can compute without measuring. **The 15x
stands as ASSERTED and I cannot narrow it.** For calibration only: Neoverse-N1
at 80 cores on one node with 8-channel DDR4 has a socket-to-core streaming
ratio in the 15–20x region in published STREAM figures — so the *number* is not
absurd, which is a different statement from established, and I am not citing a
measurement of this box.

**The finding that matters is that the 15x is not the go/no-go.** r4-perf's own
§2 gives H=19 at flat-u16 as 17.0 h per run single-threaded, 8 runs. Working
the levers back out:

| what holds | H=19, 8 u16 runs, dalby sole-tenant |
|---|---|
| everything including 15x sharding | **~9 h** (the headline) |
| 2.5x + L5 + u16 halving, **no sharding at all** | 8 × 17.0 h = **5.7 days** |
| 2.5x + L5, **no sharding and no bandwidth halving** | 8 × 27.2 h = **9.1 days** |
| nothing but the measured 2.5x, u8, as-is container, 16 runs | 59 days |

**If the DP does not shard at all, H=19 is nine days, not fifty-five.** The
round's answer changed because tonight's log measured the residue path at 2.5x
below the I256 anchors and because L5+L6 take 197 GiB to 81 GiB. Both of those
are grounded — one MEASURED, one a container model I audit in §4.3. Sharding
decides whether H=19 is an evening or a fortnight. It does not decide whether
H=19 happens.

r4-perf's own caveat says "if the DP does not shard at all, H=19 stays out and
only H=17/18 land." **That sentence is wrong on the lane's own numbers**, and
it is wrong in the pessimistic direction. Its §2 table already contains the
refutation one column to the left.

### 4.2 (b) Is bandwidth-boundedness established, or assumed?

**Assumed, and labelled as assumed** ("the wall column assumes fully
bandwidth-bound, which is only true after L1–L4"). I can put a number on it
that the lane did not.

From tonight's log at H=15: 2,624,197 states × 615 state-steps × ~1.667 edges
× 656 B = 5.29×10¹² B moved in 2,065.1 s = **2.56 GB/s single-thread, MEASURED
(modulo the inherited branch factor)**. A single Neoverse-N1 core sustains
roughly 10 GB/s streaming. **The as-is loop is at about a quarter of its
single-core roof — it is not bandwidth-bound today**, which is consistent with
the lane's own divide-bound diagnosis and with §1.4's 26-cycle slot-op.

At the claimed 2.5x it lands at ~6.4 GB/s. That is *approaching* the roof but
sitting exactly at it would be a coincidence. So:

- **What would show it.** Two runs of the patched binary at H=14, one with the
  payload at u32 and one at u16, nothing else changed. If the wall halves,
  bandwidth-bound; if it barely moves, not. **Twenty minutes on dalby, and it
  is the only measurement that settles L6.** Filed as ADV-JOB-1 below.
- **What it costs if wrong.** L6's "u16 is free at wall parity" becomes "u16
  costs 8/5 = 1.6x the total wall of u32". H=19 goes from ~9 h to ~15 h with
  sharding, or 5.7 → 9.1 days without. **The RAM benefit of u16 is unaffected
  and is what actually forces the choice at H=19** — flat-u32 is 149.7 GiB
  against 116 available, so u16 is compulsory there regardless of the wall
  argument. Low rank.

One internal tension worth naming: L1 (2–3.5x, arithmetic), L2 (1.3–2x,
vectorization) and "then it is bandwidth-bound" cannot all be true at the roof,
because a vectorization lever buys nothing against a bandwidth wall. The lane
hedged by declining to multiply and calling 2.5x central. That is the right
instinct, but it means **the 2.5x is a judgement across four levers rather than
a sum of four estimates**, and PERF-JOB-1 measures the judgement, not the
levers. Its own decision table handles this correctly.

### 4.3 (c) The 944 B/window choice — right; the flat model beneath it — shakier

944 is audited in §1.2 and it is the right call. But the H=19 and H=20 verdicts
do not use 944, they use 388 and 224, and those come from L5's decomposition of
the H=15 container residual:

> ~96 B of libstdc++ nodes … ~32 B of bucket array, ~48 B of outer `vector`
> handles, ~32 B of heap-block headers and ~48 B of allocator slack

**Those five terms sum to 256 B, and the residual they are decomposing is
288 B.** The decomposition is 32 B short of the thing it explains, in a
paragraph whose purpose is to license replacing a measured 288 with a modelled
57. Nothing downstream is recomputed from the five terms — 716 = 656 + ~57 and
388 = 328 + ~57 are consistent on their own — so no table moves. But the
decomposition is offered as the *warrant* for the 57, and it does not close.

The 57 B/entry itself is arithmetically fine (u128 key + u32 index = 20 B at
0.7 load ≈ 29 B/entry, two tables). What is unwarranted is that a 224.5M-entry
open-addressed table at 0.7 load behaves like the model at all — that is 6.4 GB
per table of pure random access, and it is 150 lines of code nobody has
written. **Mark L5's 716/388/224 EXTRAPOLATED from an unclosed decomposition,
not MEASURED.** They are the numbers H=19 and H=20 rest on.

### 4.4 (d) Are the levers multiplied where they overlap?

**Mostly no, and the lane is unusually careful here.** It states the overlaps
explicitly (L1 subsumes most of L3; L2 is worthless without L1; L4 only
attacks what L1 leaves; L5 is a prerequisite for L7), refuses to multiply the
L1–L4 ranges, and takes 2.5x as a judgement rather than a product. The
individual ranges would multiply to 3.0–9.8x; it claims 2.5x. That is the
conservative discipline the brief asks for.

Where the multiplication *is* happening unguarded is §2's "everything" column,
which stacks **÷2.5 (EXTRAPOLATED) × ÷1.3 (EXTRAPOLATED) × ÷1.6 (EXTRAPOLATED,
and conditional on §4.2) × ÷15 (ASSERTED)** — a 78x product of four unmeasured
factors, three of which have never been measured on any engine and one of which
has never been measured on any multicore run of this DP. The column is honestly
labelled lever by lever. **It is not labelled at the product**, and "H=19 is
~9 hours" is the number the round is repeating. §4.1's floor is the honest way
to state it: between 9 hours and 9 days, and the 9 days does not need any
software that does not exist except L5, L6 and the patch.

---

## 5. r4-lean: what the probe established, and what it did not

### 5.1 What is now evidence, not assertion

I read `experiments/tristruct/r4_lean_funnel_probe.log` and the 302-line probe.
The lane and the lead are entitled to this, and it is the best-evidenced claim
of the night:

- Gate A: `gateA_exit=0`, `gateA_elaborator_output_lines=0`, **9.61 s wall,
  5,515,296,768 B peak RSS**, on gympie, toolchain v4.31.0. MEASURED.
- The `#guard_msgs` pin on `#print axioms redReach_of_reach` matched
  `[propext, Classical.choice, Quot.sound]` — so the crux theorem and
  everything it transitively depends on, including the four-case
  `redStep_of_step`, carry **no `sorryAx`**. That is a real axiom audit, not a
  grep for the word `sorry`.
- Gate B's mutant was rejected with `omega` failing at line 157 and producing
  the counterexample constraints, and the axiom pin then reported `sorryAx`
  present. **The RED fired at the designed site with the designed mechanism.**

I read the statements to check for the classic failure — a lemma that compiles
because it says nothing. `redStep_of_step` carries real hypotheses
(`hP`, `hM`, `hu : Unstranded P c`), a real conclusion over the reduced
relation, and four genuinely distinct cases with `cut_edge_cols` doing load
-bearing work in two of them. `redReach_of_reach` is one `lift'` line, as
claimed. **Not vacuous. The calibration claim is evidence.**

I also independently worked whether D1 follows as easily as claimed
(→: funnel is the identity on `colAt P c ∪ M`, apply C2; ←: funnel in with B3,
chain by redStep, convert with C4, glue). **It does, and `redStep P M c`
depends on `P` only through `colAt P c` and `reach P` restricted to it, which
is precisely what makes `sufficiency` immediate.** Where the lane claims the
crux collapses, I agree with it.

### 5.2 What is not priced on anything

**Increments 3–6 — four to six of the "5-7 sessions" — have no anchor, and the
lane says so** in its own NOT ESTABLISHED list: *"no comparable encoding-layer
work in this development to anchor them — the same gap r3 had, now moved from
the crux to the encoding layer rather than removed."* That is an honest
statement of an unpriced estimate, and it should be read as one. **The probe
calibrated increment 1 and nothing else.** The revised total is not more
measured than r3's 3-5; it is differently guessed, from a better-understood
lemma graph.

**"Bookkeeping rather than mathematics" is a judgement, and I think it is the
wrong word for E2.** `encode_faithful` asserts that a canonical label vector
over `Fin H` is equal for two prefixes **iff** their occupancies and restricted
reachability agree. The forward direction is bookkeeping. The reverse requires
showing the canonicalization is a normal form for partitions under relabeling —
a quotient argument, and the standard place this kind of development stalls.
E4 `step_correct` additionally consumes D2 `strand_dead`, which the lane itself
rates M and which is a soundness *and completeness* claim about the death rule,
i.e. a statement about columns the DP has not read yet. Neither is transcription.

**Rank: the schedule risk did not shrink, it moved.** The lane says this
plainly and the lead should carry the sentence, not the total.

### 5.3 The one measured miss

Wall estimate **"6-16 min total for both gates, EXTRAPOLATED"**, against
gate A's measured **9.61 s**. A factor of ~50, conservative direction. RAM
estimate 5.5–7 GB against 5.5 GB measured — accurate.

To the lane's credit the wall figure traces to an explicitly ASSERTED r3
number ("r3's L5 addendum ASSERTED 5-15 min") and the lane wrote NO MEASURED
ANCHOR EXISTS beside it. The label did its job. But the wall estimate is what
drove the escalation to jasonp: *"<=16 min against 10 min is the second
breach"*. **There was no wall breach.** The RAM breach (5.5 GB against a 2 GB
limit) was real and the escalation was justified on that ground alone — but it
was presented as two breaches and it was one.

---

## 6. The lead

The brief asked for silent caps, narrowing dispatches, unstateable framings,
and named four specific acts. Taking them in order of how much they cost.

### 6.1 The correction to `results/triangle-r3-synthesis.md` — right act, wrong number, and the wrong number is asserted to be double-sourced

Naming "~0.3 GiB" false was correct: the geometry error is real, the minimal
counterexample {(0,0),(1,1),(2,0)} is right, and appending a dated, attributed
CORRECTION section to a filed round-3 deliverable rather than editing it in
place is the right form.

But the correction then propagates **22.6 thread-days**, which §2 shows is
wrong by 16–82x, and it does so with this sentence:

> re-derived independently in `results/r4/r4-inv.md` (§1.2, by hand against the
> banked W(18) = 20,346,159 and 3.032e13 at m=21, **so the arithmetic is now
> double-sourced**)

**What was double-sourced is the op count. The constant was not.** Both
`results/triangle-r3-spin.md` and r4-inv multiply that op count by the same
borrowed 40 ns/slot anchor, measured on a different engine with a 328x larger
payload. Double-sourcing a multiplicand, single-sourcing the multiplier, and
describing the product as double-sourced is the same class of error the
correction was written to fix, committed inside the act of fixing it. It is
the most self-serving thing I found: the correction's authority — *the lead
caught an error* — is what makes 22.6 thread-days read as verified.

`r4-spinbuild.md` §1.4 had already flagged the units problem in writing before
the commit landed. **The warning was on disk and did not reach the correction.**

Two smaller things in the same section. "9.4 GiB peak" is arithmetically right
(10.1 GB = 9.43 GiB) though r4-inv notes the source file wrote GB as GiB. And
"6.5 GiB dense-ranked" was superseded within the hour by r4-spinbuild's actual
implementation at 7.11 GiB (aligned u64+u32, 24 B/state).

### 6.2 Two artifacts "compiled and gated" with no receipt

The commit message for e62af3a says:

> r4-perf: … **Patch builds clean and passes all seven gates including three
> REDs.**
> r4-spinbuild: 1113-line engine, **clean -Werror first try. GATE 0 49 cells
> zero mismatch; GATE 1 mutant flip sets 12/12/4**, matching the Python
> reference run independently here.

I looked for the receipts. **There are none.**

| expected | present? |
|---|---|
| `experiments/tristruct/r4_perf_fastmodp.log` | absent, gympie and dalby |
| `dalby:~/src/pm-b1/results/cutcount_b1/modp_fast/` | absent |
| a spin-engine gate log at any stem | absent, all three boxes |
| `build/r4_spin_engine` | absent, gympie, ayr and dalby |
| `build/cutcount_b1` on gympie | present, **dated Aug 11 09:29**, before the patch |
| the session scratchpad | checked; no gate output |

The Lean probe, by contrast, left a 2,057-byte log carrying host, toolchain,
both exit codes, the elaborator output line count, `/usr/bin/time -l`, and the
mutant's verbatim error. **That is the standard, it was met once tonight out of
three times, and the round's own dispatch rule is that logs live beside the
script at the same stem.**

I am not asserting the runs did not happen. I am reporting that **nothing on
disk distinguishes "GATE 0 49 cells zero mismatch" from a transcription of
r4-spinbuild §4.2's own predicted line, which reads `compared=49 mismatch=0`,
or "12/12/4" from round 3's recorded fixture** — the commit quotes exactly the
values both documents predict. By this project's gate-receipt standard (a
receipt names the binary's sha256) these two claims are **NOT ESTABLISHED**,
and they are the two claims a reader would most want to lean on.

Related, and separable: **PERF-JOB-1 has not been run.** No `modp_fast`
directory, no log, and its own stated prerequisite — that the bandwidth-
sensitive H=16 job finish first — was still unmet at 00:12 (pid 2498057,
etime 01:22:57). That is correct discipline on the lead's part. What is not
correct is the commit message placing *"H=19 reprices from 55 days to ~9 h"*
two sentences before *"Patch builds clean and passes all seven gates including
three REDs."* The gate in question is `tests/gate_cutcount_b1.py`, which
r4-perf itself says **"covers the EXACT paths only — the patch does not touch
them."** A gate that by construction cannot see the modified code path is
placed as corroboration for a 6x repricing that it does not touch. The
juxtaposition is the framing problem; each sentence is individually defensible.

### 6.3 The Lean probe run after a per-job decision — clean

Correct on the facts: gympie was the only box with a toolchain, r4-lean
measured that read-only rather than assuming it, the RAM breach against the
1 GB/core limit was real, and there is no way to bring a Mathlib-importing
elaboration under 2 GB. Escalating for a per-job decision is what the standing
rule requires. My only note is §5.3's: it was escalated as two breaches and
only one existed.

### 6.4 Wave composition — right outcome, and the reason on file is not the reason

Building the spin engine on the same night INV-8 was scoped was the right call,
and §2 makes it more right than the lead knew. But the *stated* rationale
priced it as a 22.6-thread-day route worth pre-building. At 6.6–33 thread-hours
the argument for building it first is different and stronger: it is now the
cheapest instrument in the campaign by an order, and the case for gating it
tonight does not depend on protecting a multi-day investment.

### 6.5 A framing that made something unstateable

r4-perf's §2 is organised as **as-is / cheap / everything**, three columns, and
every H=19 and H=20 verdict is read off the third. **There is no column for
"the code we will actually have next week"** — the patch plus L5 plus L6, all
of which are ≤ 210 lines and none of which is L7's 300 lines and 20–30 hours.
That column is where the honest H=19 answer lives (§4.1: 5.7 days), and because
the table has no slot for it, the round has been repeating a 9-hour figure that
requires a week of unwritten threading, and a 55-day figure that requires
nothing to be written at all. **The middle case, which is the one that will
happen, has no cell in the table.** That is a framing artifact of the
three-scenario shape, not an error in any number, and it is the round-3 lead
defect pattern the brief warned about: a structural choice in a dispatch
document that quietly removes an option.

Round 3's defect (every probe on the wrong machine) has no analogue tonight:
box choice was measured, not assumed, in r4-a, r4-perf and r4-lean alike, and
each gave its reason.

---

## 7. Provenance table — every load-bearing number

Labels: **M** measured and I verified it against the log or the file; **M\***
measured by someone else, receipt seen; **E** extrapolated from something
measured; **A** asserted; **X** wrong.

| # | number | filed in | label as filed | my label | verdict |
|---|---|---|---|---|---|
| 1 | walls 188.2 / 599.5 / 2065.1 s | r4-perf §1.0 | M | **M** | reproduces the log exactly |
| 2 | B/window 1196.5 / 1125.7 / 944.5 | r4-perf §1.0 | M | **M** | exact |
| 3 | marginal slopes 1088.5 / 851.2 | r4-perf §1.0 | M | **M** | exact; a third slope (1235.9) exists and was dropped |
| 4 | H=12 wall 53.2 s, slope 1235.9 | — | absent | **M** | in the log, used by nobody; supports r4-perf |
| 5 | H=16 wall ~7,200 s | r4-perf §1.0 | projected | **E** | ~4% high; mine is 6,850–6,950 |
| 6 | c(H) grows 9%/height | r4-perf §1.0 | implied M | **E** | one interval. Geo-mean 7.4%. Costs 8% at H=19 |
| 7 | 944 B/window for H≥17 | r4-perf §1.0 | conservative choice | **M-anchored** | correct call, monotone over 3 slopes |
| 8 | "the 28% gap is amortizing, not rehash" | r4-perf §1.0 | judgement | **CONFIRMED** | lane was right; lead's doubt withdrawn |
| 9 | ~90% of edges are (1,0) | r4-perf §1 | source inspection | **M-consistent** | branch factor 1.667/state-stage implies ~94% |
| 10 | L1–L4 = 2.5x (1.8–3.5) | r4-perf §1 | E | **E** | mechanism confirmed at 26 cycles/slot-op (§1.4); size unmeasured |
| 11 | loop is bandwidth-bound at 656 B/edge | r4-perf §1 | E | **A** | measured 2.56 GB/s ≈ ¼ of the single-core roof. Not bound today |
| 12 | u16 halves the wall | r4-perf L6 | E | **A** | needs the roof to sit at 6.4 GB/s. ADV-JOB-1 |
| 13 | L5 flat = 716/388/224 B/window | r4-perf L5 | E | **E, weak** | decomposition sums to 256 against a 288 residual |
| 14 | sharding 8x ayr / 15x dalby | r4-perf L7 | A | **A** | cannot narrow. Not the go/no-go (§4.1) |
| 15 | **H=19 in ~9 h** | r4-perf §2 | E | **A (product of 4)** | floor is 5.7 days with no sharding; the round should quote the range |
| 16 | H=20 short 26 GiB (21%) | r4-perf §2 | E | **E** | rests on #13 and a 15-run count that should be 16 |
| 17 | `b ≤ floor((H+1)/2)`, out[12] safe to H=20 | r4-perf §3 | argued | **argued, unrun** | two independent consistency checks; the guard is the right answer |
| 18 | a(40) = 106 bits; 41·a(40) = 110.842 | r4-a §2.5 | M | **M** | verified off `results/triangle.txt` |
| 19 | 4 primes = 124 bits, k = 4+1 = **5** | r4-a §2.5 | M-anchored | **CORRECT** | exact product 124.000 |
| 20 | u16: 7+1 = **8** | r4-perf L6 | E | **CORRECT** | 111.991 bits, margin 1.15 |
| 21 | u8: 14+1 = **15** | r4-perf L6 | E | **X WRONG** | 14 primes = 108.249 < 110.842. Needs 15+1 = 16 |
| 22 | u8 needs 16 runs | r4-a §4.3 | E | **CORRECT** | r4-a is right where r4-perf is wrong |
| 23 | 270 B container overhead | r4-a §4.2 | M (from I256) | **superseded** | measured at 288 declining to ~57 modelled; r4-perf corrects it |
| 24 | W(m), t_m chains to m=22 | r4-inv §1.2 | derived | **M-consistent** | re-chained by hand; every value hits |
| 25 | slot-ops 4.883e13 | r4-inv §1.2 | E | **E, arithmetic clean** | verified row by row |
| 26 | 40 ns/slot borrowed anchor | r4-inv §1.5 | M elsewhere, A here | **A, and wrong here** | implies 1,640 ns/transition (§2.2) |
| 27 | **INV-8 = 22.6 thread-days** | r4-inv §1.2 | E | **X, by 16–82x** | 6.6–33 thread-hours. §2 |
| 28 | R4-SPIN-JOB-0 = 5.1 thread-hours | r4-inv §4 | E | **X, same cause** | minutes |
| 29 | 9.43 GiB keyed / 6.52 GiB dense | r4-inv §1.3 | modelled | **E** | arithmetic right; r4-spinbuild's build gives 7.11 GiB |
| 30 | 7.00% of a(40) at H=20+21 | r4-inv §5 | quoted | **quoted** | sums as claimed; not recomputed |
| 31 | "agreement moves the odds by at most 4x" | r4-inv §5 | derived | **CORRECT** | the right way to state one bit per cell |
| 32 | 12 B/state, 7.11 GiB at m=21 | r4-spinbuild §1.3 | modelled | **E** | consistent with 318,281,039 × 24 |
| 33 | "this kernel does two ops, not 41" | r4-spinbuild §1.4 | warning | **CORRECT, ignored** | the warning that would have caught #27 |
| 34 | gate A: 9.61 s, 5.5 GB, exit 0, 0 output lines | lead / probe log | M | **M\*** | full receipt; the night's best-evidenced claim |
| 35 | no `sorryAx` in the crux | lead | M | **M\*** | `#guard_msgs` axiom pin, transitive over C1 |
| 36 | gate B RED rejected | lead / probe log | M | **M\*** | fired at the designed site |
| 37 | Lean gates "6-16 min" | r4-lean §4.2 | E | **X, ~50x** | measured 9.61 s. Drove a wall-breach claim that was not one |
| 38 | Lean RAM 5.5–7 GB | r4-lean §4.2 | E | **CORRECT** | 5,515,296,768 B |
| 39 | **5-7 sessions** total | r4-lean §3 | judgement | **A for incs. 3–6** | 4–6 of the 7 unanchored, by the lane's own admission |
| 40 | crux = lift' + 4 cases | r4-lean §1.2 | claim about uncompiled source | **ESTABLISHED** | compiled, non-vacuous, statements read and checked |
| 41 | `Tc_eq_T` contributes nothing to (a) | r4-lean §0.1 | source reading | **plausible, unverified by me** | I did not read `Compute.lean` |
| 42 | perf patch "passes all seven gates" | commit e62af3a | stated as done | **NOT ESTABLISHED** | no log, no binary, no receipt (§6.2) |
| 43 | spin engine GATE 0 49/0, GATE 1 12/12/4 | commit e62af3a | stated as done | **NOT ESTABLISHED** | same; values equal the documents' predictions |
| 44 | dalby = Neoverse-N1, 80 cores, **1 NUMA node**, 116 GiB avail | — | absent | **M** | mine, read-only; favourable to L7, unclaimed |

---

## 8. Ranked: claims that would change a decision if wrong

1. **INV-8 = 22.6 thread-days (#27).** WRONG, by 16–82x, favourably. Changes
   how the route is dispatched (no window needed), what it competes with
   (nothing), and its rank (up). Also invalidates the "double-sourced"
   assertion in the committed synthesis correction. **Settle with
   R4-SPIN-JOB-0, which is now minutes.**
2. **"H=19 in ~9 h" (#15)** as the round's operating figure. A product of four
   unmeasured factors. The decision-safe statement is a range whose floor —
   5.7 days, needing only the patch, L5 and L6 — is what should drive planning.
   If the round commits to L7's 20–30 hours on the strength of the 9 h, it is
   committing on an assertion.
3. **The perf-patch and spin-engine gate claims (#42, #43).** If either did not
   pass as stated, tonight's two build artifacts are unvalidated and the wave's
   headline is wrong. Cheapest fix in the round: re-run and keep the log.
4. **Bandwidth-boundedness (#11, #12).** Costs 1.6x on the H=19 wall if wrong.
   Does not change whether H=19 runs, because u16 is forced by RAM anyway.
   **ADV-JOB-1, 20 minutes.**
5. **L5's flat-container model (#13).** H=19's 81.1 GiB and H=20's 146.8 GiB
   both rest on it, and its stated warrant does not close. If flat-u16 comes in
   at 500 B/window rather than 388, H=19 is 105 GiB — still fits — and H=20 is
   further out of reach than the "21% short" headline. Directionally safe;
   quantitatively soft.
6. **The u8 prime count (#21).** Wrong, and it is round 3's defect class. Moves
   no verdict, and RED-D is fail-closed against it. Ranked here only because
   the round asked and because it is a table that ranks payload widths.
7. **Lean increments 3–6 (#39).** Unpriced. If E2/E4 is three sessions rather
   than one, the total is 8–10, not 5–7. Nothing tonight bears on it and the
   lane says so.

---

## 9. Treated as settled, and not

- **"H=20 is RAM-blocked by 21%, not refused."** Two unmeasured constants deep
  (§4.3) and one run count short (§3.2). It is a *hypothesis worth a
  measurement*, not a finding. The 564 GB of NVMe beside it does not make it
  one.
- **"The 15x sharding factor is the weakest link that changed the round's
  answer."** The lead's framing. The answer changed on the measured 2.5x and
  the RAM lever; sharding is downstream of both. Correcting this is what makes
  H=19 defensible without L7.
- **INV-8's op model.** The op *count* is double-derived and clean. The
  *constant* is single-sourced, borrowed across a 328x payload change, and
  wrong. Do not quote "22.6 thread-days" again, and do not quote a number in
  its place until `ns_per_transition` is emitted by GATE 4.
- **`Succ out[12]`.** r4-perf's `floor((H+1)/2)` argument is careful and it
  reproduces two independent checks (the source's own `<=9 for H<=16` comment,
  and H=2 by hand). It is still an argument that has never been run, concluding
  "zero headroom at exactly the heights we want". **The guard, not the
  argument, is what closes R4-A2**, which is what r4-perf itself recommends.
- **The Lean crux.** Genuinely established, and I want that on the record
  against the rest of this file: compiled, non-vacuous, axiom-audited, RED
  fired. What is *not* established is the schedule around it.

---

## 10. JOB REQUEST — ADV-JOB-1

The only measurement I want that nobody else has asked for. It settles the one
r4-perf claim that is both load-bearing and cheap.

    job id:            ADV-JOB-1  (rides on PERF-JOB-1; do not schedule separately)
    measures:          whether the post-L1-L4 inner loop is memory-bandwidth
                       bound, by the only test that distinguishes it: two runs
                       of the patched binary at H=14, identical but for the
                       payload word width (u32 vs u16), single thread, dalby.
    decides:           L6. If the u16 wall is ~0.5-0.6x the u32 wall, the loop
                       is bandwidth-bound, "u16 is free at wall parity" holds,
                       and H=19 is ~9 h with sharding / 5.7 days without. If
                       the wall barely moves, u16 costs 1.6x total wall (8 runs
                       against 5) and H=19 is ~15 h / 9.1 days. Either way u16
                       is still FORCED at H=19 by RAM, so this decides the
                       wall, not the route.
    why it is cheap:   the u16 build is r4-perf's own L6, ~10 lines on top of
                       the L1-L3 patch, and H=14's baseline (599.5 s) is
                       MEASURED on this box tonight.
    box:               dalby, single thread, after the H=16 job lands -- same
                       bandwidth-contamination reason as PERF-JOB-1, and more
                       so, since bandwidth is the quantity under test.
    wall estimate:     ~20 min. MEASURED basis: 599.5 s unpatched at H=14,
                       two runs, both expected faster than 1x.
    RAM estimate:      < 1 GiB. MEASURED: 979,596 KB unpatched at H=14.
    RED control:       the u16 run's rows, lifted to the u32 prime by CRT over
                       enough u16 primes, must reproduce the u32 row file
                       byte for byte -- or, cheaper and sufficient here, each
                       build's rows must match the exact banked C14.out
                       reduced mod its own prime. A wall measurement from a
                       build that computes the wrong thing is worthless.
    changes if:        ratio <= 0.65  -> bandwidth-bound; r4-perf L6 stands
                       0.65-0.85      -> partially; discount the wall column
                       > 0.85         -> not bandwidth-bound. L6's wall claim
                                         is void, L2's vectorization estimate
                                         is the one to believe instead, and
                                         L7's 15x loses its stated mechanism
                                         (which is a bandwidth ratio) -- so
                                         this measurement also weakens or
                                         strengthens #14 indirectly.
    closes:            #11 and #12 in the provenance table.

**Two receipts I want and am not filing as jobs, because they are re-runs of
things already claimed done:** the perf patch's build + gate output at
`experiments/tristruct/r4_perf_fastmodp.log` with the binary's sha256, and the
spin engine's GATE 0/1 output at `experiments/tristruct/r4_spin_engine.log`.
Both are seconds. Neither exists.

---

## 11. Where a lane was right and was doubted

Hostility is about ranking, not admission, so these are on the record.

- **r4-perf on the 28% slope.** The lead flagged it as a possible rehash
  discontinuity being explained away. It is not, and the H=12 point the lane
  omitted makes the case stronger than the lane made it (§1.2).
- **r4-perf on the divide.** The "~90% of edges carry (1,0), and the loop
  spends two `udiv` there" diagnosis is confirmed to within one instruction by
  arithmetic on tonight's log that the lane did not have (§1.4). Whatever
  PERF-JOB-1 returns for the *size* of the win, the mechanism is real.
- **r4-a on the bit budget.** The one lane that got the u8 run count right, and
  it got it right while the lane that corrected it got it wrong.
- **r4-a on refusing to guess the residue speedup.** It priced the whole ladder
  off measured I256 walls as upper bounds and said "I refuse to guess". Tonight
  measured 2.5x. Refusing was correct and cost nothing.
- **r4-spinbuild §1.4.** Wrote the exact sentence that invalidates the round's
  most-repeated cost figure, before it was repeated, and nobody read it.
- **r4-lean on the crux.** A claim about uncompiled Lean, which is the class
  r3's L5 lane got wrong at nine errors and six sites. This one was right, and
  it was right in the direction that costs the lane work rather than saves it
  (it also demolished its own inherited "half is done" anchor and revised the
  total *upward*).

---

## NOT ESTABLISHED

- **My own re-price of INV-8 (6.6–33 thread-hours).** EXTRAPOLATED from the
  kernel's 12-byte payload, its two lane-adds, and this core's miss
  concurrency. Only GATE 4's emitted `ns_per_transition` settles it. What IS
  established is that 1,640 ns/transition is impossible, and that is a claim
  about the filed number, not a replacement for it.
- **The branch factor 1.667.** Inherited from r3's "20.8e6 transitions/column
  at H=14"; I did not re-derive it from the engine. My 703 ns/transition and
  2.56 GB/s depend on it. The 1,172 ns/state-stage anchor does not.
- **dalby's memory bandwidth, and whether this DP shards.** Unmeasured, by
  anyone, at any thread count. My 15–20x socket-to-core remark is a
  recollection of published Neoverse-N1 STREAM behaviour, not a measurement of
  this box, and must not be quoted as one. R4-A4's probe is still the right
  first move — with one amendment: **at H=14 it exercises a 1 GB working set
  against H=19's 81 GiB**, so it measures cache-and-TLB-resident scaling, not
  the regime that matters. It should run at the largest H that fits and report
  achieved GB/s, not just a speedup ratio.
- **Whether the perf patch or the spin engine compile, run, or pass anything.**
  §6.2. No receipt on any box.
- **Whether `r4_spin_engine.cpp` implements what `r4-spinbuild.md` says.** I
  read the deliverable's function-by-function table and the file's line count
  (1113, confirmed). I did not read the 46 KB of C++.
- **r4-lean §0.1 and §0.2** (`Tc_eq_T` void, `Finite.lean:61-76` the missing
  anchor). I did not open `Compute.lean` or `Finite.lean`. Both are checkable
  in minutes by anyone who wants them.
- **The H=16 point.** Still in flight at 00:12 (pid 2498057). It confirms or
  breaks the 944 B/window constant and it is the stated prerequisite for
  PERF-JOB-1. My ~6,850–6,950 s is a projection from 27 of 41 columns, which is
  a better-supported projection than r4-perf's from 13, and it is still a
  projection.
- **Everything about H≥17 RAM.** No measurement above H=15 exists anywhere in
  this round. Every H=17..20 RAM figure in every lane is windows × a modelled
  constant.
