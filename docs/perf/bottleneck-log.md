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

**Survey #1 verdict (to act on first):** start at **Level 1 — drop to 2 primes** (trivial,
~33% free, high confidence) after proving the a(22) bound; then **profile the standard
benchmark** to confirm whether the **`% p` reduction (Level 4)** is the next-biggest lever.

## Fixes (chronological)
| # | level | candidate | benchmark | before → after | commit | status |
|---|-------|-----------|-----------|----------------|--------|--------|
| — | — | (Phase 0 baseline + driver hardening) | — | — | 11124c9, 0e7e29a | baseline |
