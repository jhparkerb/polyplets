# How we minimized a(n) reach runtime — what worked, what didn't, and why

The reach engine computes a(n) (king-polyominoes, A006770) as a(n) = Σ_H B_H(n): one mod-p
transfer-matrix sweep per (strip-height H, prime p), CRT-combined. This is the distilled record of
the disciplined performance campaign — method, wins, dead ends (with the measurement that killed
each), the bottleneck pinned by hardware counters, and the recipe that falls out.

## Method (the part that mattered most)
Bentley's design levels, but the discipline beat the framework: **measure, never infer.** Three
times a confidently-reasoned bottleneck did NOT survive a measurement —
1. `% p` reduction "must be hot" → profile said **0.2%**.
2. MT plateau "~3.5× = memory bandwidth" → it was **under-sharding**; finer shards hit ~10×.
3. "aggregate bandwidth saturates concurrency" → DRAM counters said **3% utilized**; it was fabric.
Corollaries that earned their place: **node-count ≠ wall-time** (a prune that cut 11% of nodes ran
*slower*); **re-check marginal results at larger n** (a 2% win at N=20 was 4% at N=22); **mutate a
failed idea before discarding** (scaled-up/down/variant); **the lever for the JOB ≠ the per-sweep
optimization.**

## Wins (banked)
| lever | gain | notes |
|-------|------|-------|
| **Multi-sweep concurrency** (the big one) | **~linear in cores** | dalby 100% to J=76; the a(n) JOB is many independent sweeps — run them concurrently, don't make one sweep use all cores |
| **MT shard tuning** `SHARD_MULT=32`, `T`=non-power-of-2 (~20) | **~3.5× → ~8–10×** per sweep | the default S16 under-shards; the merge/imbalance, not bandwidth, capped it. Power-of-2 thread counts alias badly (T32 slow) |
| **Within-host MT** (lock-free 2-pass) | ~3× baseline (→ ~8–10× tuned) | byte-identical; per-sweep |
| **Reach prune** (topReach into `viableRec`) | ~2% @N=20, **~4% @ heavy heights** | byte-identical; pushes part of `completionLowerBound` into generation |
| **PGO** | **~2.7% (gcc/x86)**, ~0% clang/ARM | per-box build option |
| **H==N closed form** 3^(N-1) | one whole height free | problem-level removal |
| R1×R3×B (fold + u32 mod-p + blocked store) | ~3.4× less RAM | enables big-n in memory |

## Dead ends (ruled out, with the metric — negative results are results)
- **`% p` Barrett/lazy reduction** — refuted: 0.2% of runtime (profile).
- **iterative `viableRec`** — ~0% (compiler already optimizes the recursion; cost is per-node arithmetic).
- **two-ended reach prune** — byte-identical, 11% fewer nodes, but **~2% slower at heavy heights** (interleaved-order overhead > cheap-node savings).
- **`-march=native`** −5%; **`-mtune`** ~0%.
- **work-stealing / dynamic shard assignment** — no win: static assignment already sits at the heaviest-shard floor (reassignment headroom ≈0; gympie current == floor exactly).
- **finer shards** — compute floor drops (penalty 2.2→1.5×) but per-shard store overhead rises faster → wall *worse*.
- **2 primes instead of 3** — blocked: the CRT threshold P^(1/22)=7.05 sits below the true growth constant λ≈7.10, so no exponential bound proves a(22)<P.
- **fixed-width TM (Jensen/Conway)** — it's the transpose of what we do; identical states/RAM/compute by lattice symmetry.

## Bottleneck (pinned with perf counters, dual-arch)
- **Single sweep**: per-sweep **load imbalance** in the expand pass (`imbal = max/mean thread = 2.3–4.2×`,
  `expand ≈ max-thread`, idle threads). NOT bandwidth (LLC-miss <1.5%, IPC ~2). Caps ~10×, and
  reassignment can't beat the heaviest-shard floor (partly one monster Sig). So we stopped trying to fix it —
- **The job**: **multi-sweep concurrency**, which sidesteps the per-sweep cap. dalby scales **perfectly
  to J=76** (no aggregate contention — DRAM at ~3% via `amd_df` counters). ayr is **fabric-latency-limited**
  (2990WX: 4 dies, 2 without memory controllers; cross-die coherence) to ~72–79% → ~24 effective cores,
  with the throughput peak at exactly N_cores−1 (J=31); gympie ~4. **Not a bandwidth wall anywhere.**

## The recipe (how to minimize a(n) runtime)
1. **Run the job as concurrent sweeps**, not MT-scaled single sweeps. `--jobs ≈ N_cores−1` per box
   (peak throughput is one below core count; oversubscription degrades).
2. **The heaviest single height-sweep is the wall's long pole** (states ~2.6^H, top height dominates).
   MT *it* (`SHARD_MULT=32 T≈20` → ~8–10×); let the rest fill cores concurrently.
3. **Per-box effective cores**: dalby ~76 (1 NUMA, scales perfectly) ≫ ayr ~24 (fabric-capped) > gympie ~4.
   dalby is the workhorse; distribution across boxes adds throughput but the wall is set by the heaviest
   MT'd sweep, which one big box handles.
4. **Config**: fold + u32 mod-p (+ blocked for RAM headroom); 3 primes (2 not provable); PGO on gcc;
   H==N short-circuited; non-power-of-2 thread counts.
5. **Provenance/safety**: hardened driver (`an_modp_crt.sh`) — every sweep must exit 0 + non-empty, CRT
   verifies completeness, so an OOM/crash is a *caught* re-run, never a silent wrong answer.
