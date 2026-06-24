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

## Survey #2 — parallel brainstorm panel (5 agents, ~100s)
Two distractions struck rigorously; a reframing; a scored byte-identical queue.

**Struck (don't pursue):**
- **L1 (2 primes) — fundamentally blocked, not a method gap.** The CRT threshold P^(1/22) =
  7.053 lies *below* the true growth constant λ≈7.10, so a(22)≈λ²² already exceeds the 2-prime
  product; no exponential-form bound (λⁿ, site-perimeter 4n+4 ⇒ a(22)≤7.6e18>P, per-step ratio)
  can prove a(22)<P. The slack is the sub-exponential θ≈−1 correction, which no rigorous tool
  captures. 62-bit-prime pair sidesteps the bound but costs 128-bit modmul + 2× RAM (≈ wash).
- **L2 (fixed-width TM) — no win.** Our engine *is* a boundary TM (per strip height); fixed-width
  is the transpose ⇒ identical states/RAM/compute by lattice symmetry. Strip sweeps count disjoint
  animal sets (no shared substrate to save), and the fixed strip dim is what enables the size prune.

**Reframing — a(22) is RAM-bound (~120–183 GB > ayr's 78 GB), not time-bound** (results/reach_projection.md
marks it out-of-core). Binding levers for a(22) *running*: single-buffer the db/next pass (~2×),
out-of-core / mmap spill (#20), windowed counts rows (84% of footprint; research-grade). Memory ≥ compute.

**Candidate queue (byte-identical, scored best-first):**
| id | level | candidate | est. | effort | note |
|----|-------|-----------|------|--------|------|
| 05 | 3 algo | two-ended reach prune (pin tr & br; prune bits+topReach+bottomReach>budget) | 40–65% of the 76% gen waste | med | **measure-first** (attribute discard to top/bottom/band); subsumes 04 |
| 06 | 3 algo | delete strandedness Dead-check (PROVEN dead: coverage prune ⟺ alive, both directions) | ~0.3–0.5%, free | low | + debug assert to lock generator/step invariant; benefits all 5 callers |
| 07 | 6 syssw | PGO (`-fprofile-generate`→`use`) | ~5–15% | med | per-box (train+measure same box); targets the branch-heavy 99% |
| 08 | 6 syssw | `-mtune=native` (the safe half of failed `-march`) | ~1–3% | trivial | per-box; bench-triad |
| 09 | 3 algo | fuse canonicalizeSig 2nd relabel into UF labeling | ~0.5–0.8% | med | byte-identical; compounds with 06 |
| (mem) | 2/3 | single-buffer db/next; windowed rows | up to ~2× RAM | med/high | the a(22)-enabling lever — pursue once compute settles |

## Loop progress (live)
- **04 reach-prune MERGED** (c2bf4b8). Scales with depth (validates the larger-n rule): gympie
  ~2% / ayr ~2.7% @ H=11 N=20, but **ayr ~4.2% @ H=13 N=18** (more deep-strip columns haven't
  reached the top). Banked. Reach-prune **family CLOSED** by measure-first: discards are ~7×
  cheaper than avg (04 catches 18% of discards → 2–4% wall; two-ended 05 caps at 26% of discards
  → ~+2% over 04 for medium effort, poor ROI — not built unless the loop needs it for exhaustion).
- **07 PGO — arch-dependent: gympie (clang/ARM) ~0%, ayr (gcc/x86) ~2.7%** (114.1→111.0).
  Data-dependent branches give clang nothing to bias, but gcc/x86 PGO gains ~2.7%. **Per-box
  keeper for the gcc boxes** — available as a build option for distribution (two-phase build:
  instrument→train→use; byte-identical). **08 `-mtune` — dead (~0% ayr)**. System-SW level CLOSED
  (`-march` −5%, `-mtune` ~0%, PGO ~2.7% gcc-only).
- **a(22) FEASIBILITY (the "ready to start" gate): YES on dalby, no out-of-core.** Box RAM: gympie
  24 / ayr 78 / **dalby 125 GB (122 free), 80 cores**. The 183 GB / #20 wall is the *exact* engine;
  the *reach* engine (fold + u32 + blocked ≈ 3.4× less, run per-height) peaks ~50–70 GB on its
  heaviest height-sweep (anchored: a(21) ran under ~30 GB) ⇒ fits dalby comfortably, ayr for most
  heights. So a(22)'s gate is time + distribution, not memory. **Verify the reach peak empirically
  on a heavy a(22) height before launch (measure, don't trust the estimate).**
