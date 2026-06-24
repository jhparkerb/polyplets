# Bottleneck investigation — thorough, rule-in AND rule-out

Goal: find what actually caps performance, not the first plausible story. Every line item gets a
test with a METRIC; we confirm non-causes as deliberately as causes; simple rule-in/out first,
then refine. Cross-machine: the SAME ceiling shows on dalby (ARM/80c/1-NUMA), ayr (x86/32c/4-NUMA),
gympie (clang/ARM/10c) — so a cause reproduced on all three is structural/algorithmic, not hardware;
a cause that differs by box is hardware/arch. Use that contrast as a discriminator throughout.

## Two distinct phenomena (don't conflate)
- **P1 — single-thread IPC ≈ 2.0–2.4** (not peak ~4–6). Per-core efficiency.
- **P2 — MT parallel efficiency caps ~8×** (S32 T20: user/wall = 91/11.2 on ayr, 93/11.6 on dalby),
  i.e. threads idle ~60% even at the sweet spot. Default S16 is worse (~2.5×).
The a(22) JOB also has **P3 — multi-sweep aggregate**: many independent sweeps (separate processes,
no shared barrier) — expected to scale ~linearly with cores since not bandwidth-bound; must verify.

## A. RULED OUT (with the metric that did it)
| # | hypothesis | verdict | evidence |
|---|-----------|---------|----------|
| A1 | Memory bandwidth | **OUT** | LLC-miss 0.7–1.5% (ayr x86), cache-miss 0.5–0.7% (dalby ARM). LLC miss = RAM trip; <2% ⇒ ~99% served from cache. Dual-arch. |
| A2 | NUMA placement | **OUT** | `--interleave=all` exactly neutral on ayr's 4 nodes (11.2 vs 11.0s, identical counters). A NUMA-bound code would move. |
| A3 | Compiler codegen | **OUT as a lever** | `-march=native` −5%, PGO ~0% clang / +2.7% gcc, `-mtune` ~0%. Cores aren't the limit. |
| A4 | The `%p` reduction / mask-gen *work* | **OUT** | `%p` ~0.2% (profile); reach-prune family cut only ~4% — work volume isn't the cap. |

## B. OPEN — the MT ~8× cap (P2). Decompose the umbrella; each is independently testable.
The MT structure (per column, from sweep8_modp.h): (1) serial `Σ dbS[s].size()`; (2) clear loc[t][s]
∀ t,s (T×S) + zero localRow[t]; (3) spawn T threads = PASS1 expand (drain source shards → own
loc[t]); (4) join; (5) PASS2 merge (spawn T threads; each folds loc[0..T-1][s] into db[s], mod p);
(6) join. So **two thread-team spawns + two barriers + a T-fold merge + a T×S clear, PER COLUMN**.

| # | hypothesis | simple rule-in/out test | metric | prior |
|---|-----------|------------------------|--------|------|
| B1 | **Load imbalance** across shards (some shards far heavier → threads finish early, wait at barrier) | instrument per-thread busy-time per column; compare max vs mean | (max−mean)/max thread time; >20% ⇒ imbalance | med — finer shards already helped (S16→S32 = 2.5→8×) |
| B2 | **Barrier overhead** (2 joins × N columns; many short columns ⇒ fixed join cost dominates) | phase-timing (T-battery below); also vary N (more columns = more barriers) — efficiency vs N | ns/barrier × 2(N+1); idle time attributed to join | med |
| B3 | **Merge pass is O(T)** per state (PASS2 folds T thread-shards → cost grows with thread count, capping scaling) | phase-timing: expand-time vs merge-time; does merge fraction grow with T? | merge_wall / total_wall vs T | **HIGH** — structurally O(T), the "second insert per state" the code flags |
| B4 | **Per-column thread spawn/teardown** (fresh `std::thread`×T, ×2 passes, ×N cols — no pool) | replace with a persistent pool OR measure spawn cost in isolation; perf on clone/pthread_create | pthread_create count = 2T(N+1); time in clone | **HIGH** — spawning ~hundreds–thousands of threads/sweep |
| B5 | **Clear overhead** O(T×S×cap) per column (loc clears grow with S) | time the clear loop vs compute; check if it grows with S | clear_wall fraction; S16 vs S32 vs S64 | low — S32 *faster* than S16, so clear not dominating (but confirm) |
| B6 | **False sharing** (loc[t]/localRow[t] adjacent cache lines) | perf c2c (HITM events); or pad to 64B and re-measure | HITM / cache-to-cache transfers; Δ from padding | low — per-thread vectors are heap-separate, but verify |
| B7 | **SMT / core topology** (ayr 32c/64t; T near/over physical cores) | pin with `taskset`/`numactl --physcpubind`; sweep T below vs above physical core count | efficiency vs T with pinning on/off | med (ayr only; dalby/gympie no SMT — cross-check) |
| B8 | **Power-of-2 thread anomaly** (T32 slow=35s; T20/T60 fast=11s; T40 mid=20s) — likely S/T stride aliasing (`shards t,t+T`: when T divides S evenly the ownership stride collides) | map efficiency over T∈{8,16,20,24,32,40,48,60,64} × S∈{16,32,64,128} | efficiency surface; find the bad (S,T) pattern | med — real, unexplained, reproduces cross-arch |
| B9 | **Amdahl serial sections** (the `Σ size()` scan, setup, merge coordination — non-parallel per column) | phase-timing: sum serial-section wall; fit f to Amdahl 1/(f+(1−f)/T) | serial fraction f (8× cap on T20 ⇒ f≈8%) — locate the 8% | med — umbrella for B2/B3/B4/B5 |

## C. OPEN — single-thread IPC≈2 (P1)
| # | hypothesis | test | metric | prior |
|---|-----------|------|--------|------|
| C1 | **Branch mispredict** in viableRec (data-dependent include/exclude recursion) | perf stat branch-misses, branch-miss-rate | branch-miss %; >2% is costly | **HIGH** — the recursion is branch-heavy, the profiled hotspot |
| C2 | **Backend stalls** (L1-miss 7% serial → L2/L3 latency, or dependency chains) | perf stat stalled-cycles-backend, cycle-activity | backend-stall % of cycles | med |
| C3 | **Frontend / i-cache** (template bloat, the recursion) | perf stat stalled-cycles-frontend, icache misses | frontend-stall % | low |

## D. Decisive test battery (run order: cheapest/most-discriminating first)
1. **Phase-timing instrumentation** (throwaway): wall-clock around {Σsize, clear, expand, join1,
   merge, join2} per column, summed per sweep, printed. ONE run attributes the ~60% idle across
   B2/B3/B4/B5/B9 simultaneously. **THE key test — do first.** Run at 2 thread counts (T20, T60) and
   2 sizes (H=11 N=20 small/many-columns, H=13 N=20 heavy) to see which phase grows with T and with column count.
2. **Per-thread busy-time** (same instrumentation, per-thread): rules B1 in/out (imbalance).
3. **T×S sweep** (timing only, cheap): T∈{8,16,20,24,32,40,48,60} × S∈{16,32,64,128} on each box →
   the efficiency surface; rules B8 (anomaly) + refines B1 (does S64 beat S32?). Cross-machine.
4. **perf single-thread** (T1): branch-misses + stalled-cycles-frontend/backend → C1/C2/C3 at once.
5. **Thread-pool A/B** (if B4 implicated): persistent pool vs per-column spawn → B4 magnitude.
6. **Pinning** (`--physcpubind`, ayr): B7 (SMT). 7. **c2c / padding**: B6 (false sharing) — only if 1–3 leave it open.

## E. Cross-machine discriminator (use throughout)
- Cause reproduces identically on ARM(dalby)+x86(ayr)+gympie ⇒ **algorithmic/structural** (B2/B3/B4/B5/B9, C1) — fix in code.
- Cause differs by box ⇒ **hardware/arch** (B6/B7/B8 partly) — config per box.
- The ~8× cap is ALREADY ~identical on dalby (8.0×) and ayr (8.2×) ⇒ strong prior the cap is **structural**
  (merge/barrier/spawn), not hardware. That points first at B3 (O(T) merge) and B4 (per-column spawn).

## Status
- A1–A4 ruled out (metrics above). B/C open. Next: run D1 (phase-timing) — it discriminates the
  highest-prior structural causes (B3 merge, B4 spawn, B9 serial) in a single measurement, cross-checked
  on dalby + ayr. Then D3 (T×S surface) and D4 (single-thread perf). Refine from there; do not commit a
  fix until the phase-timing names the dominant term with a number.

## RESOLUTION (executed — metric-backed)
Phase-timing (D1) + T-sweep + S-sweep + per-thread busy (D2), dual-arch (gympie/ayr):
- **RULED OUT** (phase-timing, both arches, H=11 & H=13): B2 barrier, B3 merge (0.04–0.95s, ~0–1%),
  B4 spawn (merge incl. spawn = ~0%), B5 clear, B9 serial prologue (~0.00s). ~94–99% is the EXPAND pass.
- **B1 LOAD IMBALANCE — CONFIRMED, the cap.** Per-thread busy (ayr H=11 N=20 T20): expand ≈ max-thread
  (10.85≈10.41), imbal=max/mean = 2.3× (S32) to 4.2× (S16/S64), min=0.00 (idle threads), mean≈4.5s
  constant. The pass waits for the busiest thread; configs only re-alias which threads get heavy shards
  (non-monotonic S/T zigzags ⇒ aliasing of static `thread t owns {t,t+T,…}` × hash skew + per-Sig work variance).
- **Upside:** balanced mean 4.5s ⇒ ~25× at T20 (vs ~10× now); at dalby T80 ~76× (vs ~8–10×). Imbalance
  costs ~2.4× (T20) to ~7× (T80) — the largest lever, on the confirmed bottleneck.
- **P1 single-thread IPC~2 / C1 branch:** not yet measured (perf branch-misses) — secondary; the MT cap (B1) dominates.
- **FIX:** dynamic shard assignment (atomic next-shard counter / work-stealing) replacing static stride
  ownership. Byte-identical (only thread→shard mapping changes). Next candidate to implement+gate.

## COUNTERFACTUAL on the fix (executed) — BOTH per-sweep fixes ruled out
Per-shard work distribution probe (floorPenalty = best-achievable-by-reassignment / perfect-ideal):
- gympie T8 S32: floorPenalty **3.23×**, and current expand == flooredIdeal → **reassignment headroom ≈ 0**.
- ayr T20: floorPenalty **2.17× (S32) → 1.48× (S512+, plateau)**. The heavy shard is *partly* multi-Sig
  (finer shards split that) + a residual **monster-Sig floor (~1.48×)** that no sharding touches.
- BUT finer shards raise per-shard store overhead (clear + scan of T×S mostly-empty shards) faster than
  the compute floor falls → **net WORSE wall** (S512 12.7s > S32 11.1s, from the earlier S-sweep).

**Verdicts:**
- **Work-stealing / reassignment — RULED OUT** (~no win; current static ≈ the heaviest-shard floor).
- **Finer shards — RULED OUT** (compute floor drops, store overhead eats it; wall doesn't improve).
- **Per-sweep MT is genuinely floored ~10–11×** (heaviest shard + a monster-Sig core); not simply fixable
  (only intra-Sig parallelism would beat it — hard/dangerous, deferred).

**THE LEVER (revised): multi-sweep concurrency (P3), not per-sweep MT.** a(22) = 66 independent (H,p)
sweeps; run many concurrently (`--jobs`, separate processes, no shared barrier, NOT bandwidth-bound) →
all cores fill via independent work, and the ~10× per-sweep cap is irrelevant to the job. The a(22) wall
≈ total-work / cores, bounded only by the single heaviest (H,p) sweep's ~10× latency in the tail.
**Next: verify P3 scales ~linearly with concurrent sweeps** (it should — bandwidth-free) — that, not
per-sweep MT, sets the real a(22) wall. (The "hold before implementing work-stealing" call was correct:
it would not have helped, and neither would the simpler shard-bump.)

## P3 (multi-sweep concurrency) — MEASURED, the a(22) execution model
Identical independent serial sweeps (H=11 N=18), batch wall vs J. eff = solo/batch.
- **dalby (80c, 1 NUMA): PERFECT 100% to J=76** (batch flat at ~82s, J=1→76). No aggregate
  contention. → a(22) = ~76 concurrent sweeps, linear. Per-sweep MT cap (~10×) IRRELEVANT.
- **ayr (2990WX 32c, GPU-off): smooth fabric gradient** 100/95/86/78/72/77/55/45% at
  J=1/8/16/24/31/32/40/48. No oversubscription cliff (J=31≈J=32); peak ~J=31-32 ≈ **24 effective cores**.
- **gympie (~4 effective)** — its own perf-core limit.

**ayr ceiling PINNED with counters (corrects earlier "aggregate bandwidth" — that was WRONG):**
- amd_df DRAM channels at J=31: ~1.75 GB/s of a ~40-85 GB/s ceiling = **~3% utilization → NOT
  DRAM-bandwidth-bound.**
- l3_misses sublinear (~×6-8 for 31× sweeps) → **L3 / Infinity-Fabric latency** (2990WX: 4 dies,
  only 2 with memory controllers; cross-die coherence). Intrinsic to the chip.
- GPU A/B (srsieve2cl paused): +5-10 points only (J=8 82→95, J=31 67→72) — minor, not the cause.

**Effective-core budget for a(22): dalby 76 + ayr ~24 + gympie ~4 ≈ 104.** dalby is the workhorse;
multi-sweep concurrency is the lever; per-sweep imbalance is moot. Q1/Q2 now computable on this footing.

## DEFERRED LEVER (pinned 2026-06-24) — intra-signature parallelism
We shard the expand pass BETWEEN boundary signatures but never WITHIN one. The per-sweep ~10× MT
cap is load imbalance from a few "monster" signatures whose mask fan-out (`forEachViableMask`)
dwarfs the rest — work-stealing/finer-shards couldn't beat it because the monster is one
indivisible unit. The untried decomposition: **split a single heavy signature's mask enumeration
across threads.** This is the ONLY identified lever that could raise the per-HEIGHT (long-pole)
ceiling — relevant only when the single heaviest height-sweep, not multi-sweep concurrency, is the
binding constraint on wall time (i.e. for a(n) where one height dominates and few heights exist).
Unmeasured; revisit then. Related deferred gaps from the same session: (1) the per-COLUMN heartbeat
is too coarse for high-H sweeps (few, long columns — they sit inside one column for minutes with no
beat; `col/maxn` also misreports since they empty near col ~maxn−H+1, not maxn) → needs a
within-column beat (every N states) + a real-column-count denominator; (2) height-dependent
scheduling (serial-concurrent for the cheap bulk, MT only the heaviest heights) beats a flat
`--jobs/--threads` config, but no driver does it yet.
