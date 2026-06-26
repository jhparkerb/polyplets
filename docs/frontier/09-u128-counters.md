# Frontier idea 09 — `__uint128_t` counters: CRT-free exact counting to ~a(48)
*Source: docs/scheduling-design.md §"Unexplored axes" #9. Related: results/crt-counter-shaping.md (the SETTLED interleaved-31-bit-CRT decision this contests), experiments/crt_counter_bench.cpp (the micro-bench this EXTENDS), cpp/tma/sweep8_modp.h (FlatDB32 u32 rows + CRT recombine).*

## Idea
Store each state's counts-by-size row as `__uint128_t` and count **exactly, with no CRT,
in a single enumeration pass**. a(n) < 2¹²⁸ until ~a(48), so a 128-bit counter is exact
across the whole reachable frontier. u128 is **double-width arithmetic, not bignum**:
add = `add`+`adc` (2 instrs); the sweep matrix is 0/1 so counting is **additive only**
(crt-counter-shaping §0) — the widening 64×64→128 multiply (x86 MUL/MULX, ARM64
MUL+UMULH) is never even hit, and the one missing hardware op, 128÷64 division, counting
never does. Attacks **complexity/footgun surface**, not RAM or wall: it deletes the CRT
machinery.

## Why it might matter here
Relevance window is narrow and must be stated: **u64 is exact through a(25)**
(a(25)≈1.5e19 < 2⁶⁴; crt-counter-shaping §1), so u128 buys nothing until **a(26)+**,
where it competes only against CRT (not against the u64 path). crt-counter-shaping
settled that race on *speed* as roughly a wash (enumeration is f≈0.85–0.90 of a sweep;
count arithmetic is ~10–15%), and recommended interleaved-31-bit-CRT (3×u32, one
enumeration). u128's pitch is therefore **simplicity**: no CRT lift, no prime pool, no
composite-prime footgun ("2147483479 is composite and silently corrupts" — §6), exact
integer falls straight out with no reconstruction. **Counting lever only:** for GF
recovery, 128-bit buys only 63-bit CRT primes (~half the prime count), NOT a single
prime — H=10 coeffs are ~2¹³⁰⁰ and need full bignum (§9 of scheduling-design). So this
is not a GF tool.

## Kill-test — quickest path to INFEASIBLE
**Question it answers:** is u128 single-counter increment+widening throughput within
striking distance of interleaved-31-bit-CRT on the hot row-add loop — on BOTH ISAs?
**Setup:** **extend experiments/crt_counter_bench.cpp** (don't reinvent — it already has
the width × style × in-degree harness, ~290 MB working set, kill-safe per-line flush).
Add a `u128` width arm (`__uint128_t` row, NOREDUCE = exact add — no reduce needed since
no modulus) and an **interleaved-CRT** arm (3 × `uint32_t` residues per count, the
production layout from crt-counter-shaping §6: 3 conditional-subtract adds per count,
enumeration shared). Build and run on **gympie (arm64)** AND **ayr (x86-64)** — the
widening-mul/adc codegen differs per ISA and that's the whole question. Cost: ~1 h
(small edit to an existing bench + two short runs).
**Measure:** Macc/s (million row-adds/s) and ns/accum for the u128-exact arm vs the
3×u32-interleaved-CRT arm, each ISA. (Optionally GB/s — u128 is 16 B/count vs 12 B for
3×u32, a modest traffic premium.)
**NO-GO as a WIN if:** u128 is materially slower than interleaved CRT — > ~1.3× ns/accum
on either ISA. Decisive because if CRT is the faster hot path, its complexity is *paid
for*, and u128 then buys only simplicity at a speed cost — not a clear win, just a
tradeoff to defer. (u128 is never *wrong*; this gates whether it's the recommended a(26)+
counter.)

## Substantial-improvement ladder (must clear ALL)
- **C1 — u128 within ~1.3× of interleaved CRT** on ns/accum on **both** arm64 and
  x86-64 — from the extended crt_counter_bench, the two `--out` runs.
- **C2 — deletes the CRT/prime-pool/lift/recombine machinery** — sweep8_modp.h's
  per-prime passes + CRT recombine + the composite-prime footgun all go away; one exact
  pass, one counter type. Measured as code/path removed, not perf.
- **C3 — exact integer falls straight out** — no reconstruction step; the row *is* the
  answer (split to two u64 limbs only for printing). Verified against known a(n) for
  small N in the same gate that checks the u64 path.
*Per-idea bar:* **parity-or-better speed AND a real cut in complexity/footgun surface**,
for the **a(26)..a(48)** window — speed parity alone isn't enough (CRT already works);
the win is deleting the prime-pool/CRT footguns at no speed cost.

## Composition / foreclosures
Mutually exclusive with interleaved-CRT as the a(26)+ counter — pick one (this is the
contest). RAM-neutral-ish vs interleaved CRT (16 B vs 12 B/count) and so composes with
the I7 1-copy table (oq1) and adaptive config (04) identically to CRT — it only swaps the
counter type behind `addCounts`. Forecloses nothing in the enumeration/scheduling layer.
The §3/§4 reduction-style and enumerate-once findings of crt-counter-shaping apply
unchanged (u128-exact is the ultimate "enumerate once, no reduce"). Below a(26): irrelevant
(u64 wins on size); above ~a(48): irrelevant (needs bignum).

## If it passes: effort & where it lands
**S (ESTIMATE)** — a `FlatDB128` is a one-type-swap sibling of FlatDB32 (sweep8_modp.h);
`addCounts` becomes a plain widening add, and the per-prime/CRT scaffolding is *deleted*,
not added. The kill-test (extend the existing bench) is itself **XS**. Lands as the
a(26)+ counting path in cpp/tma/sweep8_modp.h (or a sibling sweep8_u128.h), gating the
post-a(25) ROADMAP terms. Only schedule the build once a(25) is in hand — no value before.
