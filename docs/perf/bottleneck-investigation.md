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
