# Reach Engine — Performance Bottleneck Log

Disciplined, per-Bentley-design-level optimization record for the mod-p transfer-matrix
reach engine (goal: a(22), A006770). Method: survey all levels → pick best
speedup-per-effort → reproduce → profile → fix → gate → cross-box benchmark → document →
commit. Process spec: `~/.claude/plans/a-1-correct-majestic-firefly.md`.

## Standard benchmark
`build/tma square8 20 --only-height 11 --modp 2147483647 --fold` (serial, one prime).
Heavy enough to exercise the inner DP, fast enough to iterate (~51 s on gympie, 14 MB RSS).
Heavier `(H,N)` used per-candidate when a bottleneck needs it. Timing = min of ≥2 reps via
`/usr/bin/time` (`-l` macOS, `-v` Linux). Correctness gate per change: `make gates`
(incl. gate-tma, gate_modp, gate-driver) + byte-identical at smallest n.

## Baseline — row 0 (commit 0e7e29a, branch `perf/reach-serial-baseline`)
| box | arch / compiler | wall (min of 3) | RSS |
|-----|------------------|-----------------|-----|
| gympie | Apple Silicon / clang | 51.0 s | 14 MB |
| ayr | Threadripper 2990WX / gcc | 114.5 s | 11.8 MB |
| dalby | ARM 80c / gcc | 126.8 s | 11.8 MB |

(gympie's single-core is ~2.2× faster than the 2018 Threadripper and the ARM box — relevant
for the eventual distribution cost model.)

## Level survey #1 (Bentley §5.2 — choose most speedup for least effort)
Hypotheses to verify scientifically; none assumed. ROI = rough speedup × confidence ÷ effort.

| level | candidate | est. speedup | effort | conf. | notes |
|-------|-----------|--------------|--------|-------|-------|
| 1 Problem Def | **2 primes instead of 3** (∏ > a(22)) | ~1.5× (−33% sweeps) | trivial | high | needs a rigorous a(22) magnitude bound (a(22) < 2^62 ⇒ two 31-bit primes suffice). **Top ROI.** |
| 1 Problem Def | 1 wide 62-bit prime, `__int128` CRT | up to 3× (1 sweep/H) | medium | med | needs u64 counts (~2× RAM) + 128-bit modmul; weigh vs the 2-prime win |
| 2 System Struct | fixed-width TM (Jensen/Conway) vs Σ_H | potentially large | high | low | record-count method; recomputes less boundary structure; big rewrite — back-of-envelope first |
| 3 Algo/DS | tighter boundary-state pruning (`completionLowerBound`) | ? (fewer states ⇒ time+RAM) | med | low | profile state counts first |
| 3 Algo/DS | state rep (`Sig`) / hash store (`FlatDB32`) layout | ? | med-high | low | only if profiling implicates it |
| 4 Code (indep) | **reduce the `% p` cost** (Barrett / Montgomery / lazy) | potentially large | low-med | med | `addCountsModP32` does a 64-bit `%` per nonzero count per output; divisions usually dominate modp loops — **profile to confirm its share, then high ROI** |
| 5 Code (dep) | SIMD the counts-row accumulate (AVX2/NEON) | med | med | med | gated by the reduction method (Barrett vectorizes; `%` doesn't) — after L4 |
| 6 System SW | `-march=native`, LTO, PGO | small-med | trivial | med | cheap; measure each |
| 7 HW/Parallel | within-host MT, then multi-machine | large (aggregate) | med | high | **LAST** — only after L1–6 marginal; re-derived with method this time |

**Survey #1 verdict — then UPDATED by reasoning + profiling (the method working):**
- **Level 1 (2 primes): downgraded — blocked on a non-trivial proof.** 2-prime CRT (∏≈4.6e18)
  is exact only if a(22) < 4.6e18. Best *rigorous* bound is a(n) ≤ λⁿ with proven λ ≤ 9.355 ⇒
  a(22) ≤ 2.3e21 > ∏. Not provably safe without a tighter bound (need rigorous λ < 7.05, vs
  true ≈6.8). Effort↑, parked as a sub-proof, not free.
- **Level 4 (`% p` reduction): REFUTED by profiling.** A `-g` sample of the standard benchmark
  (gympie, H=12 N=20) puts ~99% of samples in `s8::viableRec` (transition_square8.h:92);
  `addCountsModP32`'s `% p` (sweep8_modp.h:128) is ~10 samples (≈0.2%). Optimizing it would
  have been today's anti-pattern (tuning ~nothing).
- **TRUE hotspot (profiled): the viable-mask enumeration** `forEachViableMask`/`viableRec`
  (transition_square8.h:82–113) — the binary recursion that generates, per state, every
  next-column cell-mask with popcount≤budget that strands no component (up to ~2^H leaves).
  **This is the next candidate** (Level 3 Algo/DS + Level 4 code): make that enumeration
  cheaper — e.g. iterative bit-enumeration to kill the per-node recursion overhead, and/or a
  tighter generator. Reproduce = profile (done); fix = next iteration.

## Phase 2 input — per-box MT thread knee (H=11 N=20, default shardmult)
| box | T=1 | T=4 | T=8 | T=16 | knee | cores |
|-----|-----|-----|-----|------|------|-------|
| gympie | 51 s | 17.5 s (3.0×) | 17.0 s | — | ~T4 | 10 |
| ayr | 114 s | 37.4 s (3.0×) | 35.8 s | 34.0 s (3.4×) | ~T8 | 32 |
| dalby | 127 s | 39.7 s (3.2×) | 38.3 s | 36.1 s (3.5×) | ~T8 | 80 |

Per-core speed differs ~2.2× (gympie fastest). Memory-bandwidth-bound: ~3–3.4× and flat past
the knee at default shards (the T=20 + `TMA_SHARD_MULT=32` regime that reached ~10× is a
separate future candidate — NUMA-stable via `--interleave=all` on ayr). For distribution,
throughput ≈ (cores/knee-threads)/(knee-time): dalby ≫ gympie ≈ ayr. **Next: per-HEIGHT cost
curves per box** (the standard benchmark is one point; heavy heights cost minutes-to-hours),
then a validated cost model → assignment so all boxes finish within 10% → distributed a(22)
through the hardened driver.

## Fixes (chronological)
| # | level | candidate | benchmark | before → after | commit/tag | status |
|---|-------|-----------|-----------|----------------|------------|--------|
| — | — | Phase 0 baseline + driver hardening | — | — | 0e7e29a | baseline |
| 01 | 4 code | iterative viableRec (kill recursion overhead) | H=11 N=20 | 51.0s → 50.4s | `deadend/01-viablerec-iterative` | **dead end** — ~0% + clear mechanism (per-node cost constant, compiler already optimizes the recursion); no plausible scale effect → N=20 rules it out |
| 02 | 6 syssw | `-march=native` | H=11 N=20 | 51.0s → 53.4s | (no source change) | **dead end** — −5% regression; decisive at N=20 |
| 03 | 7 parallel | within-host lock-free MT (`--threads`) | H=11 N=20 | 51.0s → **17.5s (T4)** | ef4a82a (merged) | **WIN ~3×** — byte-identical; the achievable lever |

## Survey #2 — re-profiling: single-machine is NOT exhausted (correction)
"Stop after two dead ends" was premature. Instrumenting the mask pipeline
(`MASKSTATS`, H=12 N=16, throwaway):
```
H=12 N=16:  gen=188.7M  alive=188.7M (1.000)  kept=44.8M  (kept/gen=0.238, 76% wasted)
H=13 N=18:  gen=1.24B    alive=1.24B   (1.000)  kept=341M  (kept/gen=0.275, 72.5% wasted)
```
Holds at a ~6× larger sweep (per the larger-n rule) — not a small-n artifact.
- **alive/gen = 1.000** — `stepColumnSquare8` NEVER returns Dead; its union-find strandedness
  re-check is redundant (the generator's coverage prune is already sufficient). [minor: step ~1%]
- **kept/gen = 0.238** — **76% of generated masks are discarded by the `completionLowerBound`
  budget check AFTER generation.** Generation is the 99%, so this is wasted traversal.
  **Candidate 04 (next):** push the *reach* part of `completionLowerBound` into `viableRec`.
  `tr`/`br` (top/bottom occupied rows) = lowest/highest mask bits, and the top/bottom markers
  come from `old`+mask edges — so `topReach+bottomReach` is a valid LOWER bound on the full
  `completionLowerBound`, computable during generation. Pruning the recursion on it is a strict
  subset of the existing post-step prune ⇒ **byte-identical by construction**, but cuts up to
  ~4× of the generation work (the 99% hot path) ⇒ potentially a large win, compounding with MT.
  Effort: medium (must bound `br` correctly mid-recursion); gate: byte-identical + `make gates`.

## Phase 1 status (revised) — a real candidate remains
The hot path (`forEachViableMask`, ~99%) is the per-state viable-mask enumeration. Mechanical
*mechanics* tuning yields nothing (iterative ~0%, `-march` −5%, `% p` ~0.2%), BUT the generator
is **76% wasteful** (candidate 04 above) — a real algorithmic win, not research-grade. Beyond it:
- **L1 (2 primes, ~33%)** — blocked on a rigorous a(22) < 4.6e18 bound; best proven bound
  (λ≤9.355 ⇒ a(22)≤2.3e21) is far too loose; needs λ<7.05 ≈ the true value (research-grade).
- **L2 (fixed-width transfer matrix, Jensen/Conway)** — potentially the only large
  single-machine win; a major rewrite with different RAM profile. Back-of-envelope needed.
- **L3 (better boundary state / cheaper enumeration)** — research-grade, uncertain.

**Verdict:** by D9, the cheap levers are < 1% / negative, and the big single-machine levers
(L1/L2/L3) are high-effort/research-grade. Per Bentley ("most speedup for least effort,"
after the higher levels are surveyed) the **achievable** large win is **L7 — parallelism**
(within-host MT, then multi-machine), re-derived *with the discipline + the hardened driver*
this time (the lock-free MT was already validated byte-identical; per-box thread knee and the
NUMA `--interleave=all` finding were measured). That is the next phase of work.
