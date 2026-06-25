# Optimally shaping CRT-based counting: prime size & counter width

_Investigation 2026-06-25. Question: CRT counting currently uses 32-bit primes (one
size down from the 64-bit counters that overflow / are RAM-heavy for a(22)). How many
primes would 16-bit or 8-bit counters need, what does that cost in runtime, and what
other levers exist? Deliverable: a specific prime-size + counter-size recommendation._

Sources: a microbenchmark (`experiments/crt_counter_bench.cpp`, raw data
`experiments/crt_bench_results.txt`), a real-engine timing probe, a literature scan,
and the current engine (`cpp/tma/sweep8_modp.h`).

---

## 0. The one structural fact that governs everything

The transfer matrix is **0/1**: a sweep step is `dst[n] += src[n]` with both operands
already `< p`. **There are no large multiplications — the work is additive only.** This
collapses most of the "fast modular arithmetic" toolbox (Barrett, Montgomery) because
those exist to reduce a *product* up to ~m²; for a sum `< 2m` they would only *add*
multiply latency. The relevant levers are therefore: **counter width, number/size of
moduli, reduction style (conditional-subtract vs deferred), pass layout
(independent vs interleaved), and SIMD.**

The current engine stores each state's counts-by-size row as `uint32_t` — and the code
itself notes the row is **~84 % of per-state memory**. So **counter width is, directly,
the dominant RAM lever.** The current reduction is `dst = (uint64_t)(dst+src) % p` — a
full 64-bit modulo per accumulation, which the benchmark below shows is the *slowest*
possible choice.

---

## 1. How big are the numbers (what sets the # of moduli)

We must CRT-recover exact counts up to `M = max state weight ≈ a(n)`. Let `L = log2 a(n)`.
Extrapolating the confirmed ratio a(20)/a(19) ≈ 6.76:

| n | a(n) (approx) | L = log2 | u64 exact? |
|--:|--:|--:|:--:|
| 20 | 1.03e15 | 49.9 | yes (confirmed) |
| 21 | 6.9e15 | 52.6 | yes |
| 22 | 4.7e16 | 55.4 | yes |
| 23 | 3.2e17 | 58.1 | yes |
| 24 | 2.1e18 | 60.9 | yes |
| 25 | 1.4e19 | 63.7 | **yes (last one)** |
| 26 | 9.8e19 | 66.4 | **NO — overflows 2^64** |
| 27 | 6.6e20 | 69.2 | no |
| 28 | 4.5e21 | 71.9 | no |

**Key consequence:** a single `uint64` counter is *exact* (no CRT, no modulus, pure
addition) all the way through **a(25)**. CRT only becomes *necessary* at **a(26)+**.
For a(21)–a(25), "CRT" is purely a RAM-reduction choice, not a correctness requirement.

### Moduli needed, `k(b) = ceil(L / usable_bits)`

Usable bits per modulus (largest prime that still fits the byte width *and* sits just
under the boundary to avoid packing waste): u8 → 7.97 (p=251), u16 → 16.0 (p=65521),
u32 → 31.0 (p=2³¹−1) or ~32.0 (p=2³²−5).

| target | L | u8 (k) | u16 (k) | u32 @2³¹ (k) | u64 |
|--|--:|--:|--:|--:|--:|
| a(22) | 55.4 | 7 | 4 | **2** | 1 |
| a(25) | 63.7 | 9 | 4 | 3 | 1 |
| a(26) | 66.4 | 9 | 5 | 3 | — |
| a(28) | 71.9 | 10 | 5 | 3 | — |

Note the current production default of **3 primes is over-provisioned for a(22)** (2
suffice: 62 bits > 55.4). Trimming to the minimal `k` is a free ~33 % cut there.

---

## 2. RAM: counter width sets peak per-state memory — but sub-linearly

Per-state memory = `sig (fixed) + row (R counts × b/8)`. The row is ~84 % at u32, the sig
~16 % and **width-independent**. So halving the counter does NOT halve per-state RAM:

| counter | row share | per-state vs u32 | per-state vs u64 |
|--|--:|--:|--:|
| u64 | 91 % | 1.72× | 1.0 |
| u32 | 84 % | **1.0** | 0.58× |
| u16 | 72 % | 0.58× (1.72× less) | 0.34× |
| u8 | 56 % | 0.37× (2.7× less) | 0.21× |

(Confirmed against the engine's own note: u64→u32 measured "1.73× less memory.")

So in **independent-pass** mode (one modulus resident at a time, the current design):
u16 buys ~1.7× RAM headroom over u32, u8 buys ~2.7×. Useful at the frontier — but
sub-linear, because the fixed sig overhead is paid at every width.

---

## 3. Benchmark: reduction style and counter width (gympie, arm64, single-thread, scalar)

`experiments/crt_counter_bench.cpp` — models the inner loop (accumulate in-edge source
rows into a destination row mod p; working set ~290 MB, exceeds cache). Best style per
width, "Macc/s" = million `dst+=src` row-adds/sec (higher = faster):

| width | noreduce (ceil) | **% p (current)** | cond-sub | **deferred** | GB/s (deferred) |
|--|--:|--:|--:|--:|--:|
| u8  | 23.5 | 17.9 | 20.2 | **25.4** | 1.8 |
| u16 | 19.1 | 15.3 | 17.0 | **20.3** | 2.9 |
| u32 | 17.3 | **14.0** | 15.8 | **31.4** | 9.0 |
| u64 | 16.4 | — | — | 16.4 (noreduce) | 9.4 |

Two hard results:

- **The current `% p` is the slowest reduction at every width.** At u32, switching to
  **deferred** reduction (sum the in-edge group in a `uint64` temp, reduce once per
  destination) takes throughput **14.0 → 31.4 Macc/s = 2.24×**. Deferred also writes each
  destination once per merge instead of once per in-edge, so it wins on memory traffic
  too. This is a counter-size-independent ~2× left on the table. (It generalizes the
  "u64-fold" idea already scoped in the repo.) Literature agrees: for additive-only work
  the optimum is deferred accumulation, falling back to branchless conditional-subtract
  `t -= p & -(t>=p)`; Barrett/Montgomery are inapplicable.

- **Small counters do NOT reach their bandwidth advantage in scalar code.** u8 stalls at
  1.8 GB/s (compute/loop-overhead-bound), while u32 streams 9.0 GB/s. So u8 delivers only
  ~25 Macc/s vs u32's 31 — *slower* despite moving 4× less data — and still needs 3–4×
  more moduli. **In scalar code, 8/16-bit lose on time and only win (sub-linearly) on
  RAM.** They reach memcpy speed only WITH SIMD (AVX-512BW / NEON vectorized
  add+min-subtract); the literature measures vectorized modular-add as fully
  bandwidth-bound (~8.5× on AVX-512). Without vectorizing the engine, small counters are
  not worth it.

---

## 4. Pass layout — the lever that interacts with enumeration cost

Two ways to carry `k` moduli:

- **Independent pass per modulus** (current): hold 1 residue, RAM = single-width
  per-state, but **re-do the full state enumeration `k` times.** Time ∝ k.
- **Interleaved RNS** (enumerate once, maintain all k residues per state): enumeration
  paid **once**, arithmetic = k cheap bandwidth-bound updates, but peak RAM = all k
  residues ≈ L bits/count (≈ the u64-class footprint we were trying to avoid).

Which wins depends on the **enumeration fraction** `f` of a pass (the width-independent
polyomino state-branching work, which the a(22) forecast identified as the dominant,
exponentially-growing cost). If `f` is high, interleaving (enumerate once) is the big
win and counter width barely affects *time* — it only sets RAM. If `f` is low
(arithmetic-bound), independent SoA passes are fine and time ∝ k.

**Probe result (real engine, single-thread, gympie):**

| case | u64-exact (no modulus) | mod-p, 1 prime (u32 + `%p`) |
|--|--:|--:|
| N=15, H=12 | 55.4 s | 50.6 s |

Adding *or removing the entire modular-arithmetic layer* moves total sweep time by **<10 %**
— and mod-p is even slightly *faster* (its half-width u32 rows save more bandwidth than
the `%p` costs). Cross-checked by order of magnitude: real sweeps are cpu-**hours** for
10⁷–10⁸ states (µs–ms per state) while the count arithmetic is ~30–60 **ns** per row-add.

⇒ **`f ≈ 0.85–0.90`. Enumeration dominates; count-arithmetic is ~10–15 % of a sweep.**

This is the governing finding. It means:
- **Pass count is the primary runtime multiplier.** Independent-pass-per-prime pays the
  ~85–90 % enumeration cost `k` times. With k=3 that is ≈ **2.7× the wall time** of a
  single interleaved sweep that pays enumeration once. No counter-width or reduction tweak
  comes close to this lever.
- The reduction-style win (§3, ~2.2× on arithmetic) acts on only the ~10–15 % arithmetic
  slice → ~5 % of wall. Real and free, but not the headline.
- Counter *width* barely affects time (arithmetic is small); it sets **RAM**, and matters
  only insofar as it decides whether the enumerate-once (interleaved) layout fits memory.

---

## 5. Other levers examined

- **Reduction style** — deferred > cond-sub > `% p` (§3). Biggest single win, ~2×.
- **Minimal k** — don't run 3 primes when 2 cover the target (§1). Free ~33 % at a(22)–25.
- **Near-2³² primes** (2³²−5, 2³²−17) instead of 2³¹: 32 usable bits, occasionally shaves
  a prime, same uint32 storage. Minor but free.
- **Byte-boundary discipline** — a modulus just *over* a power of two (e.g. 257) forces
  the next byte width and ~doubles storage. Always pick primes just *under* 2⁸/2¹⁶/2³²
  (251, 65521, 2³¹−1 / 2³²−5).
- **SIMD** — the only thing that revives 8/16-bit: vectorized add + min-unsigned subtract
  makes them memcpy-bound. Requires vectorizing the engine inner loop (real work).
- **CRT recombine** — keep scalar; it's O(#states) once at the end, negligible, and does
  not vectorize cleanly (carry propagation is serial).
- **u64-exact (no CRT)** — the simplest "lever" of all for a(21)–a(25): k=1, pure add.

---

## 6. Recommendation

The investigation **refutes the implied direction** of the question. Going to *smaller*
counters (16- or 8-bit) is the wrong move: it needs 4–5 / 9–10 primes respectively, runs
*slower* per pass in scalar code (overhead-bound, never reaching its bandwidth edge), and —
because the dominant cost is enumeration paid per pass — more primes means proportionally
more wall time. Smaller counters are a double loss unless you are simultaneously
RAM-cornered *and* willing to SIMD-vectorize the engine. The right moves are the opposite:
**fewer, wider counters, and pay the enumeration once.**

**Concrete recommendation, by regime:**

1. **a(21)–a(25): plain `uint64`, NO CRT at all.** Every count < 2⁶⁴, so a single exact
   pass (k=1, pure addition, no reduction) is correct and is the fewest-passes design
   possible. This is the immediate answer for a(21). Use mod-p here only if 8 bytes/count
   does not fit the target machine's RAM — and even then prefer #2 over shrinking counters.

2. **a(26)+ (CRT genuinely required): three primes just under 2³¹**
   (`2³¹−1, 2³¹−19, 2³¹−61` = 2147483647 / 2147483629 / 2147483587), **stored `uint32`,
   carried INTERLEAVED — one enumeration, three residue-rows per state — not three
   independent sweeps.** Interleaving pays the ~85–90 % enumeration cost once instead of
   three times: ≈ **2.7× wall-time saving**, the single biggest lever found. Interleaved
   count storage ≈ 12 bytes/count (3×u32) vs 8 for a u64 — a modest RAM premium for a
   ~2.7× speedup. (Optionally near-2³² primes `2³²−5, 2³²−17` for 32 usable bits, same
   storage, occasionally shaving the third prime.)

3. **Reduction: deferred** — accumulate each destination's in-edge group in a `uint64`
   temp and reduce once (`% p`, or branchless conditional-subtract). ~2.2× on the
   arithmetic slice (≈5 % of wall) and it removes the per-add `%`. Free; do it. This is the
   already-scoped "u64-fold" idea, generalized; it also *is* the u64 path of #1.

4. **Minimal `k`** — 2 primes through a(25)-range, 3 for a(26)–a(28). The current default
   of 3 is over-provisioned below a(26).

5. **16-/8-bit counters: only if** at a(26)+ the interleaved 3×u32 footprint busts the
   target machine **and** the inner add is SIMD-vectorized (NEON / AVX-512BW), using an
   AoSoA layout (per-modulus SoA tiles, enumeration shared per tile, uniform-modulus vector
   reduction). In interleaved mode total count storage ≈ L/8 bytes regardless of width, so
   8-bit's only RAM edge over 32-bit is the ~25 % saved top-of-range byte-rounding — not a
   4× win. Not worth the engine rewrite unless genuinely RAM-cornered.

**One-line answer:** keep **31-bit primes in `uint32`**, drop to the **minimal prime
count**, switch reduction to **deferred**, and — the real prize — **interleave the residues
so the dominant enumeration runs once, not once per prime**; below a(26) skip CRT entirely
and use a single exact `uint64`. Smaller (16/8-bit) counters are a net loss except in a
future SIMD + RAM-cornered corner at a(26)+.

---

### Artifacts
- `experiments/crt_counter_bench.cpp` (+ `build/crt_counter_bench`) — width × reduction-style
  × in-degree microbench; raw data `experiments/crt_bench_results.txt`.
- Real-engine probe: `build/tma` (u64) vs reach `build/tma --modp` single-height timing.
- Literature synthesis (additive-only reduction, RNS base selection, SIMD lane/bandwidth,
  pass-layout) folded into §0/§3/§4/§5.
