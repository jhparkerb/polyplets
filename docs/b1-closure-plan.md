# Closure — locking P_k with B1, and the RAM ladder that decides how far B1 reaches

Thread name: **Closure**. Opened 2026-08-13. Two things are recorded here: the
P_k result that makes 100% rule-independent coverage of a(40) reachable at all,
and the memory plan for the engine that would deliver it.

Engine: `cutcount_b1` — the colour-symmetrized spin transfer matrix over
Z[q]/(q^2) (candidate B1). Banked run, source and rows:
`results/cutcount_b1/`. Measured ladder and gate design:
`results/triangle-r3-ladder-gate.md`. The standard this serves:
`docs/skeptical-reader-standard.md`.

---

## 1. The P_k lock (the thing to not forget)

**Every P_k needed for row 40 is anchored at H <= 20, so a B1 sweep to H = 20
pins the entire H >= 22 band ab initio, at zero additional compute.**

The band structure of a(40), recomputed this session from
`results/ns_a40/perheight/` by summing T(40,H) (reproduces a(40) =
56749893611764175164545926946127 exactly):

| band | share of a(40) |
|---|---|
| H <= 20 | 93.0120% |
| H = 21 | 2.8431% |
| H >= 22 | 4.1449% |

The H >= 22 band was never enumerated by anything — it is wired P_k closed
forms. The *shape* is a theorem (`docs/proofs/diagonal-law.md`, Lean-complete),
but the two free coefficients per level are fit from real swept cells, and
those cells came from the incumbent. So they inherited the incumbent's
connectivity rule, and the 4.1449% was not rule-independent.

The onset is sharp — `diagonal-law.md` step 5: P_k governs n >= 2k+1 — so the
cheapest pinning of level k is

    T(2k+1, k+1)  and  T(2k+2, k+2)

Cell T(40,H) lies on level k = 40 - H, so the H >= 22 band is exactly
k <= 18. Level 18's anchors are T(37,19) and T(38,20) — the highest anchors in
play, and both at H <= 20. Level 19 is the exception: its anchors are T(39,20)
and T(40,21), and the alternative second point T(41,22) costs more than
sweeping the cell directly, so **H = 21 stays required for its own 2.84%** and
cannot be reached by formula.

Consequences:

- A B1 sweep of H = 1..20 at Nmax = 40 emits every anchor in the pass it was
  already doing — the engine outputs whole rows C_H(n), n = 1..40. **The P_k
  lock costs no additional compute.**
- It converts H >= 22 from inherited-rule to rule-independent, so H <= 20
  in RAM means **97.157% of a(40) two-sourced**, and the entire remaining gap
  is one cell, T(40,21).
- Better than pinned: each level gets a rule-independent holdout inside the
  same sweep. P_5's diagonal continues through H = 8..21, thirteen cells past
  its two anchors; P_17 gets two; P_18 gets one, T(39,21).

**It does not cut the sweep.** P_k is worth using for T(40, 40-k) only if its
anchors are cheaper than the target: k + 2 < 40 - k, i.e. k < 19, i.e. H > 21.
Break-even lands exactly on H = 21 — the same diagonal read from both ends —
so the formula tower is always cheaper above H = 21 and never at or below it.
There is no overlap to harvest, and no height below 21 gets skipped.

---

## 2. The memory model, measured

From the completed H <= 16 run (dalby, 1 thread, exact I256 payload,
`results/triangle-r3-ladder-gate.md`):

| H | windows | wall s | peak RSS MiB | bytes/window |
|---|---|---|---|---|
| 14 | 891,074 | 1,618.6 | 6,924.6 | 8,149 |
| 15 | 2,624,197 | 5,134.5 | 20,382.8 | 8,144 |
| 16 | 7,832,667 | 16,475.2 | 60,827.4 | 8,143 |

Marginal slope H=15->16: **8,142 B/window, measured and flat.** The payload
model — 41 area slots x 3 coefficient streams x 32 B x 2 buffers = 7,872 B —
accounts for it to 3%; the residual **~270 B/window is container overhead**
(`unordered_map` node plus a separately heap-allocated `std::vector` per
state). That overhead is 3% of today's footprint and would be 55% of an
8-bit-payload footprint, which is why it appears as its own change below.

Window counts are anchored on the exact census `sum_k C(H+1,2k)*Bell(k)`; the
measured/census ratio is 2.286 / 2.298 / 2.308 / 2.318 / 2.327 at H = 12..16,
rising ~0.011 per height. Extrapolating that ratio:

| H | 17 | 18 | 19 | 20 | 21 |
|---|---|---|---|---|---|
| windows (proj.) | 23.7M | 72.8M | 226M | 709M | 2.25B |

Call it +-20%. (The naive x2.96-per-height fit gives 1.87B at H = 21, 17%
lower; nothing below turns on the difference.)

Budget: **dalby, 125 GB total, ~121 GB available.** ayr's 78 GB is strictly
worse and single-process work cannot span boxes, so dalby is the whole budget.

Headroom for exact arithmetic: C_H(40) is 1.42e32 at H = 16 (log2 = 106.8) and
its per-height ratio is *falling* (1.44, 1.36 at H = 15, 16), so C_21(40)
projects to ~2^108-111 — comfortably inside a wrapping u128 (final values
< 2^127 is what the ring-hom argument needs; intermediates may wrap freely).
The A(1) self-check stream is the exception in kind, not in width: its true
value C(861,40) is ~2^229.5, but it is *compared* against a Pascal row computed
in the same wrapping ring, so it stays valid at any width.

---

## 3. The change ladder, ordered

Six changes. Each is a multiplier on bytes/window, so they compose; the table
below is cumulative, in the order a build should apply them — biggest and
simplest first, stopping at the height you need.

**A — `I256` -> `u128`.** One typedef and one bound check. Final values project
to ~2^108-111 (C_H(40) is 2^106.8 at H = 16 and its per-height ratio is
*falling*: 1.44, 1.36), so a wrapping u128 is exact by the same ring-hom
argument the I256 uses today. **x1.9.** Hours of work.

**B — the A(1) self-check as its own pass.** Drop the third coefficient stream
from the production pass (ST 3 -> 2) and re-run the same states with a
single-stream payload to do the binomial check. Check preserved exactly, peak
down a third, total wall up a half. **x1.5.** Hours.

**F — flat arena, open-addressed index.** Replace `unordered_map<u128,u32>` +
one heap-allocated `vector<Payload>` per state with an open-addressed key table
and a contiguous payload slab. Takes the measured ~270 B/window container
overhead to ~57 B (16 B key + 4 B index at 0.7 load, both buffers). **x1.1
now, and it is what makes C/D/E worth anything** — at an 8-bit payload the old
overhead would be 62% of the footprint. u32 indices still suffice at H = 21
(2.25B < 2^32) and the 5-bit key still fits u128 at H = 21 (110 bits), so no
key-format work is needed; a mixed-radix RGS pack would shave 57 -> ~37 B if
H = 20 ends up tight. A day.

**C/D/E — the residue ladder.** Payload width becomes a template parameter and
a CRT driver runs the passes: **C** = 4 x 31-bit primes (u32), **D** = 8 x
16-bit (u16), **E** = 16 x 8-bit (u8), each with one extra prime held out as a
RED. Values < 2^112 fix the counts. **x4, x8, x16** over A, at x4/x8/x16 the
passes. This is the one real piece of engineering on the list — the driver, the
reconstruction, and a gate battery per width — call it a week. Widths after the
first are a parameter, not new work. The narrow inner loop also *speeds up*
(a 4-limb `iaddmul` becomes one multiply-add), by an unmeasured factor that
partly pays back the extra passes.

**G — chunked release of the consumed buffer.** Today both buffers are fully
live: peak = 2x working set. Iterate `cur` in arena order and `MADV_DONTNEED`
each chunk once consumed, so peak approaches ~1.2x. **x1.7.** The only change
that touches the sweep's structure rather than its data layout, and the
fiddliest; needed only for H = 20.

### Cumulative, against 121 GB available on dalby

Peak RSS in GB, per height, after each rung:

| rung | B/win | cum | H17 | H18 | H19 | H20 | H21 | top H |
|---|---|---|---|---|---|---|---|---|
| baseline (measured) | 8,142 | 1.0x | 193 | 593 | 1,839 | 5,772 | 18,322 | — |
| **A** u128 | 4,206 | 1.9x | **100** | 306 | 950 | 2,982 | 9,465 | **17** |
| **B** check own pass | 2,894 | 2.8x | 69 | 211 | 654 | 2,052 | 6,513 | 17 |
| **F** arena | 2,681 | 3.0x | 64 | 195 | 606 | 1,901 | 6,033 | 17 |
| **C** u32 x4 | 713 | 11.4x | 17 | **52** | 161 | 505 | 1,605 | **18** |
| **D** u16 x8 | 385 | 21.1x | 9 | 28 | **87** | 273 | 866 | **19** |
| **E** u8 x16 | 221 | 36.8x | 5 | 16 | 50 | 157 | 497 | 19 |
| **G** chunked release | 130 | 62.6x | 3 | 9 | 29 | **92** | 293 | **20** |

The factor each height demands off the measured baseline: H17 **1.6x**,
H18 **4.9x**, H19 **15.2x**, H20 **47.7x**, H21 **151x**.

### Where to stop

- **Stop after A** and you have H = 17 — 9.06% of a(40), and, more to the
  point, a measured wall, RSS and census ratio under every projection below.
- **Stop after C** and you have H = 18. B and F buy no height on their own;
  they are the margin that lets D and E land, and F is a prerequisite for them
  being worth anything.
- **Stop after D** and you have H = 19 at 87 GB — cumulative 88.85% of a(40)
  swept, plus P_0..P_17 locked, which is the H >= 23 band as well.
- **E + G together** are what H = 20 costs, and H = 20 is the height that
  finishes the job: 97.157% swept-or-locked, everything but T(40,21). E alone
  misses at 157 GB; G alone misses; both give 92 GB, ~24% margin on a +-20%
  window projection.
- **H = 21 never fits.** It needs 151x, and the payload floor caps the whole
  ladder at ~41x (at 1 byte per slot-coefficient the payload is still 164 B and
  the keys are 57 B). Out-of-core or nothing — and note that is *one cell*,
  T(40,21), 2.8431%.

---

## 4. What has to be true, and what to measure

- The **census ratio extrapolation** carries H = 20. Each of H = 17, 18, 19
  measures it against a closed form, in that order, before H = 20 is launched.
- The **~60 B container floor** for C2 is a design target, not a measurement.
  If open addressing lands at 90 B instead, H = 20 goes to ~115 GB and H = 21's
  key-only floor to 202 GB. Measure it at H = 18.
- The **C4 factor** is quoted at 1.7x from the 2x double-buffer accounting. It
  is unmeasured, and H = 20 is the only height that depends on it.
- The engine is still **single-threaded**. Everything above is per-process peak
  RSS, which is what the budget constrains; the wall figures (H = 20 projects
  to ~20 single-core days per prime pass before C1's inner-loop speedup) demand
  a parallel frontier that does not exist yet. RAM is the wall this document
  plans around; cores are the next one.
- The gate battery in `results/triangle-r3-ladder-gate.md` §4 applies unchanged
  per payload variant — the structural self-checks are blind to stencil errors,
  so each new width needs its own gate receipt before a production column.

## 5. Not levers (checked, recorded so they are not re-derived)

- **Ranged-area payload** (store only [n_lo, n_hi] per window). The incumbent
  measured 1.89x from this trick. **MEASURED HERE, and it is 1.13-1.16x — dead.**
  `experiments/cutcount/cutcount_b1_probe.cpp --probe H 40` (the banked engine
  plus an occupancy census; gated by reproducing banked `C9.out` byte for byte)
  reports, at the column where the ranged footprint peaks:

  | H | mean nonzero span | of 41 slots | ranged win |
  |---|---|---|---|
  | 8 | 36.4 | 89% | 1.127x |
  | 9 | 35.9 | 87% | 1.143x |
  | 10 | 35.4 | 86% | 1.160x |

  The mean *nonzero count* equals the mean span at every column, so the payload
  is not merely contiguous but fully dense inside its span — sparse storage is
  dead for the same reason. The trend is mildly favourable with H but nowhere
  near a factor that would change a rung.
- **Sweeping fewer columns to hold down peak states.** Same probe: **the state
  set saturates at column 2 of 41** and is flat thereafter, at every H measured.
  Peak footprint is reached almost immediately, so nothing about column count
  touches RAM (it is purely a wall lever, and see the width-truncation note
  below).
- **Evaluation/interpolation in the area variable** (carry A(x_0) as a scalar
  instead of 41 coefficients, x41 memory win, ~free in time because the inner
  n-loop collapses). Dead: the true degree in x is H*W = 861, not 40. The
  41-slot vector *is* the truncation to n <= 40, and evaluation cannot
  truncate. Cyclic aliasing mod (x^41 - 1) is fatal for the same reason.
- **Truncating the sweep width** from W = 41 to W = 42 - H. Sound for the
  telescope — sets excluded that way have height <= H-2 and cancel in
  C_H - 2C_{H-1} + C_{H-2}, provided all three are run at the same W — but it
  is a *time* lever (~2x at H = 21), not a memory one, since peak windows
  saturate within the first few columns. Needs the H <= 16 replay as its gate.
- **Top-bottom mirror symmetry** of the strip (~2x on states, which is the one
  factor that would move H = 21). The flip commutes with a column-at-a-time
  transfer but not with the row-at-a-time scan the engine uses, so mid-column
  states have no partner. Unpriced; the rewrite is not minimal.

---

## 6. If the target is a(39) instead of a(40)

The break-even in §1 generalises. Cell T(n,H) sits on level k = n - H, and
P_k's anchors reach H = k+2, so the formula is cheaper than the sweep exactly
when k + 2 < H, i.e. **H > (n+2)/2**. So closing row n ab initio costs a sweep
of

    H <= floor((n+2)/2)     at Nmax = n

and every anchor the formula band needs lands inside that same sweep (level
k <= n - H_max - 1 has anchors at n' <= 2k+2 <= n and H <= k+2 <= H_max).

| target | sweep to | top-rung RAM | closes at |
|---|---|---|---|
| a(37) | H <= 19 | 82 GB at rung **D** | 100% |
| a(38) | H <= 20 | 88 GB at rung **G** | 100% |
| a(39) | H <= 20 | 90 GB at rung **G** | 100% |
| a(40) | H <= 21 | out of RAM at any rung | 97.157% |

a(40) is the odd one out, and only because 21 = (40+2)/2 exactly: its top level
P_19 has T(40,21) as one of its own two anchors, so that cell cannot be
finessed. Row 39 falls on the other side of the same parity — its top consumed
level is k = 18, anchored at T(37,19) and T(38,20), both inside an H <= 20
sweep.

> **CORRECTED 2026-08-14 — `results/anchor-cut-map.md`.** "Cannot be finessed"
> is true of the staircase's *onset* instance and false of the cell. Level 19
> pins from columns 18 and 19 at depth 2, level 20 from the same two columns at
> depth 3, with the below-onset residual carried by the closed defects
> (`docs/proofs/depth-swap-residual.md`). The whole table above shifts by
> `J - 1 = 2`: **a(38), a(39) and a(40) all close from H <= 19**, and the
> H = 20 rung this section builds toward is not needed for them. Rung G and the
> out-of-core question are unaffected only in the sense that nothing now asks
> for them.

Two consequences worth carrying:

- **The whole out-of-core question disappears** if the deliverable is a(39).
  H = 21 was the only height needing spill; the ladder in §3 ends at rung G and
  ends in RAM. Per-window bytes shrink 2.4% besides (NA = 40 rather than 41):
  H = 20 lands at 90 GB rather than 92.
- **Stopping at rung D closes a(37) outright** — 82 GB at H = 19, no arena
  chunking, no 8-bit residues, no `MADV_DONTNEED`. That is the cheapest
  complete rule-independent a(n) available, and it is three rungs from where
  the engine stands today.

One honest caveat, and it is structural rather than fixable by more RAM: the
**topmost level a sweep consumes is anchor-exhausted**. For a(39), level 18 is
pinned by exactly T(37,19) and T(38,20) and predicts T(39,21) = 2.48% of a(39)
with no holdout inside the run, since the cell that would check it (T(39,21))
is the prediction itself. Row 40's H <= 21 sweep does better here — T(39,21)
falls inside it and serves as level 18's holdout. So a(39)-at-H<=20 buys
closure at the cost of the top level's redundancy; sweeping one more height is
the only thing that restores it, and that height is H = 21.

---

## 7. Can the 80 lines be Lean-proved?

The connectivity rule in B1 is 80 lines — `slot`, `canon`, `gather`, `shifted`,
`successors` (lines 93-173 of the banked source). Everything in §3 is machinery
around that core, which does not change on any rung. So a proof of the core
does not decay as the engine gets faster, and that is the argument for doing it.

**The statement is already expressible in the project's own vocabulary.**
`Polyplets/Defs.lean` has `kingAdj`, `KingConnected` and `T n H`;
`Polyplets/Graph.lean` has `kingGraph` with `kingConnected_iff_reachable`. A
theorem about B1 would land on the same `T n H` the papers cite, not on a fresh
model — a real head start over starting cold.

The work is not proportional to the 80 lines, because the content is not the
code. Three tiers:

1. **The cancellation identity** — the mathematical heart, and the thing a
   skeptic actually doubts. The DP assigns each subset a product of (q - b_i)
   factors, one per component birth, where b is the *live* block count at that
   moment (blocks that have left the window are not counted, which is why
   colours get reused). Those products do not individually vanish mod q^2 for
   disconnected sets — (q-b1)(q-b2) = -q(b1+b2) + b1*b2 mod q^2 — so the
   connected count emerges from a cancellation summed over all configurations.
   Proving that is pure combinatorics with no program in it, and it is the piece
   worth having. **Today its entire justification is the C++ comment asserting
   the rule plus `experiments/probe_cutcount_dp.py` checking it against brute
   force at five board sizes.** The identity has never been written down in
   closed form in this repo.
2. **The DP realises that sum** — window locality (king adjacency reaches at
   most H+1 cells back in scan order, so the H+1-slot window is a sufficient
   statistic) plus invariant preservation by `successors`. Mechanical and very
   provable; `canon` is just canonical form of a partition. Routine for this
   development — the GapWalk chain is fifteen files of exactly this kind of
   invariant work.
3. **The bridge to the binary** — not provable, and never is. The honest gate is
   evaluating the Lean model on small boards and comparing byte for byte with
   the C++ at H <= 6, exactly the pattern `Polyplets/ComputeBridge.lean` already
   established for `T n H` (`native_decide` on real rows, kept off the critical
   rebuild path because the runs take minutes). The hostile-witness audit of
   2026-07-21 (`docs/lean-hostile-witness.md`) is also the precedent for how
   that bridge gets over-claimed: every cell a real kernel-recorded theorem, not
   a comment.

**Scope.** Tier 2 is routine. Tier 1 is the real project — a correctness proof
for a cut-and-count DP over connectivity, a bigger single mathematical object
than anything in the tree except the grand form, comparable to the notary
piece K campaign in effort and with more risk, because the identity has to be
stated correctly before it can be proved.

**Payoff.** It upgrades the claim from "two engines that cannot share a
connectivity misconception agree" to "one engine's counting rule is proven
correct against a definition of king-connectivity the skeptic reads in
`Defs.lean`" — strictly stronger than anything the incumbent can offer, and
independent of how ugly the fast version gets. Pair it with the reference-engine
differential testing in §3: prove the rule, differential-test the machinery.

**Sequencing.** Tier 1 is worth writing down and proving *before* the
engineering ladder, not after. If the identity does not come out clean, that is
a fact about B1 worth having before a month goes into a parallel frontier — and
it costs desk time, not compute.
