# Reach projection — engine throughput, hardware limits, and the #20 decision

**Task #19.** Turns the measured engine characterizations (`complexity.md`,
`scaling.md`, `tma_state_growth.md`) into one defensible statement of *how far
each method reaches on the hardware we have*, and answers the question #19 exists
to answer: **is the out-of-core transfer-matrix backend (#20) worth building, and
for what?**

Scope note: every number tagged **[m]** is measured; **[p]** is projected from a
measured anchor with the stated growth law. The tall-height deceleration
(below) means projections are *upper-bounded* extrapolations, not point
predictions — the honest reading is "no larger than", and the true tall-height
costs must be measured, not trusted.

## The two engines (cost laws, measured this project)

| | Time | Memory | Parallelism |
|---|---|---|---|
| **Redelmeier generation** | Θ(a(n)) ≈ λⁿ/n, **λ ≈ 7.10** [m] | polynomial, O(n) — effectively free | embarrassingly parallel (ran 64–96-way) |
| **Column transfer matrix** | Θ(peak boundary-state count), per-height base **≈ 2.6–2.7** [m] | the state table *is* the memory; **≈ 570 B/state** [m] | memory-bandwidth bound, ~2× within a height; heights independent |

The split is the whole story: generation pays the full λ≈7.1 per term but needs
no RAM and scales to all cores; the transfer matrix has a far smaller time base
(it *merges* animals sharing a boundary) but pays in an exponential state table
and ~2× parallelism. **In wall-clock the workhorse is generation** (a(19) in
hours, 64–96-way) and **the transfer matrix is the independent check** (days,
bandwidth-bound) — its value is disjoint failure modes, not speed. So reach for
*more terms* is a generation-on-cores question; reach for the transfer matrix is
about the memory wall, which is what #20 addresses.

## Memory model (the anchor everything hangs on)

Per retained state ≈ Sig (32 B) + counts row ((maxn+1)·8 B) ≈ 200 B at n=20; the
sweep holds two maps (db + next) at load factor ≤0.7 ⇒ effective **≈ 570 B/state**
[m]. Anchor check: a(19) tallest height H19 peaked at **12.5 GB [m]** ⇒ ≈ 22 M
states — and the independent whole-sweep peak-state projection also lands at
**≈ 22 M [p]**. Two roads, same number: the model is trustworthy at n=19.

Implied machine capacity:
- **gympie 24 GB ≈ 42 M states**
- **ayr 78 GB ≈ 137 M states**

## Whole-sweep peak states vs n (the a(n) memory wall)

Measured peak states (optimized engine, `tma square8 N`):

| n | peak states | step ratio |
|---:|---:|---:|
| 14 | 259,422 [m] | — |
| 15 | 633,088 [m] | 2.44 |
| 16 | 1,541,984 [m] | 2.44 |
| 19 | ≈ 22 M [p] (=12.5 GB, matches measured H19) | — |

Per-n state base **k ≈ 2.44, easing down slightly** with n. Critically, the
within-a(n) per-height growth *decelerates near the top* — a(19)'s tallest
heights grew 2.0× then 1.56×, well below the 2.6× seen low down — so projecting a
constant 2.44 **over**states the tall end. Treat the table below as ceilings.

| n | peak states [p] | RAM @570 B/state | gympie 24 GB? | ayr 78 GB? |
|---:|---:|---:|:--:|:--:|
| 19 | 22 M [m-anchored] | 12.5 GB | ✗ time, fits RAM | ✓ (was run here) |
| 20 | ≤ 54 M | ≤ 31 GB | ✗ (>42 M) | ✓ comfortably |
| 21 | ≤ 131 M | ≤ 75 GB | ✗ | ⚠ at the 137 M edge |
| 22 | ≤ 320 M | ≤ 183 GB | ✗ | ✗ → **needs #20** |

(Deceleration likely shaves these; a(20) ≈ 29 GB and a(21) ≈ 67 GB under a 2.3×
base. The qualitative crossings — a(20) leaves gympie, a(22) leaves ayr — hold
under either base.)

## Two different binding constraints (do not conflate them)

- **On gympie, the wall is TIME, not RAM.** Measured on the a(20) partial: height
  14 alone ran **>68 min** holding only ~450 MB; H1–13 finished in ~35 min total,
  H1–15 took ~4 h, and per-height time grows ~2.5×/height. So gympie's reach is
  gated by wall-clock long before 24 GB binds — H16 ≈ hours, H17 ≈ ½ day, H18 ≈ a
  day+, H19–H20 time-prohibitive. **More RAM does not help gympie; cores or a
  faster engine would.**
- **On ayr, the wall is RAM at the top heights** — which is exactly where #20
  bites.

## Fixed-height GF reach (the other #19 deliverable)

The per-height boundary-state count D_H = 1, 5, 15, 39, 98, 246, 624, 1604, 4177,
11005, 29291 (H=1..11) [m], base **~2.7**, saturation-confirmed (maxn 25 vs 30
agree). This is **144× below** the Bell(H+1) I first feared (D₁₁=29,291 vs
Bell(12)=4.2 M), which is *why the fixed-height-GF wall sits at ~H17–18, not ~H13*.
Extrapolating: D₁₇ ≈ 11 M states — feasible in RAM; the mod-p engine
(`build/gf_modp`) already lifts the u64 *term*-count wall, so the limit is states
× (≈2·order) terms, not overflow. **Validated through H9 today; H10 attempted
(order 5005, not yet validated); H17–18 is the realistic ceiling** with the
current single-machine engine. GF heights are not a #20 driver.

## Verdict on #20 (out-of-core backend)

| Target | Verdict |
|---|---|
| a(20) | **#20 not needed.** ayr (~31 GB peak) completes it; gympie is time-bound, not RAM-bound. |
| a(21) | **Borderline on ayr** (~67–75 GB of 78) — too tight to be comfortable. **Bring this number down** (see levers below); the cleanest reduction is #20, so a(21) is now a #20 *target*, not just a(22)+. |
| **a(22)+** | **#20 required** (~180 GB ≫ 78 GB). This is the frontier it unlocks. |
| full n=19 hole stratification (#28) | ~60–75 GB — *fits ayr*, but #20 **relieves** the pressure and de-risks the run. |

**Recommendation.** #20 is **not** on the critical path for a(20); it *is* now
wanted for **a(21)** — ~67–75 GB of ayr's 78 is too tight to run with confidence
(a transient grow during a rehash, or a worse-than-projected tall height, OOMs
it), so we should bring that number down rather than bet on the deceleration.
And #20 is **required** for a(22)+ and to take full-n=19 holes off ayr's ceiling.
Decision rule: *build #20 (or the partial RAM-reduction below) for a(21)
confidence; it's mandatory for a(22)+.*

## RAM-reduction levers for a(21) (~570 B/state today)

Per state = Sig (32 B) + counts row ((maxn+1)·8 B ≈ 176 B at n=21) + the **db +
next double buffer** (≈2×) + open-addressing slack (load factor ≤0.7). Ways to
cut the ~75 GB:
- **#20 out-of-core (the real lever, ≥2×):** spill `next` (and cold `db` regions)
  to mmap/disk. The state store was built to be replaced, so this is a drop-in —
  and it's the only lever that also unlocks a(22)+. *Recommended primary.*
- **Single-buffer the sweep (~up to 2×):** the db+next doubling is the largest
  constant. A generational / in-place update that doesn't hold two full maps at
  peak would roughly halve RAM — cheaper to build than #20, a(21)-specific.
- **Trim the counts row (~10–25%):** carry only the live `[onset..maxn]` window
  per state instead of the full `maxn+1` row; most states never reach small or
  large n.
- **Compact Sig (minor):** 32 B is already lean; sub-leading.

Net: a single-buffer pass alone could bring a(21) to ~35–40 GB (comfortable on
ayr); #20 does that *and* generalizes. Either way, a(21) should not be run at
75 GB as-is.

## Residual unknowns (what would harden this)
- One clean **measured tall-height anchor at a(20)** (H18–H20 peak states) to
  replace the deceleration *assumption* with a number — the single biggest source
  of slack in the table above.
- a(21) sits exactly on ayr's RAM edge; whether it fits is genuinely unresolved
  until the a(20) tall heights pin the growth base.
