# oq3 (cost-model) + 04 (per-column config) — data collection off the running a(21)

Frozen 2026-06-26. The a(21) fold is live on dalby (driver: `MAXJOBS=2 THREADS=40
heights=[20 19 18 17]`, rev 0f48081). H20 (pole) + H19 running; H18, H17 queued. This
captures the perishable per-height/per-column telemetry before those heights finish, and
freezes the cost-model's predictions **now** so oq3's predicted-vs-actual is honest, not
post-hoc fit.

## What's collected, where
| signal | source | for | retention |
|--------|--------|-----|-----------|
| per-column `src` (input frontier), `done`, `rate` (states/s), `elapsed`, `eta_col` | heartbeat `runs/a21fold/h##.log` (already tee'd, append) | **04** work + throughput variance; **oq3** per-height wall | on disk ✓ |
| RAM (`rss_kb`) + `cpu_pct` over time, tagged by `(height, col, pct)` | `scripts/a21_telemetry.sh` → `runs/a21fold/telemetry.csv` | **oq3** per-height peak RAM; **04** per-column RAM variance | NEW (this collection) |

Join key = **(height, col)**. The proctitle (`tma a(21) H20 c=2/21 ~24%`) carries the
column, so the sampler tags every RSS reading with its column with no engine change.

## Frozen cost-model predictions — N=21, model under test
Laws (docs/a22-forecast.md, anchored to the measured N20 pole + 6-point N13–18 ladder):
`peak_states`: pole=H=N−1, **2.43×/N** across N, **2.45×/height** down from the pole.
`bytes/state`: **~1086 B** (pole(22) 75 GB ÷ 6.9×10⁷ states, t40 batched production).
`cpu`: pole_cpu(22) ≈ 6.7×10⁶ cpu-s, **÷4.44/N**, **÷2.4/height**; pole sustains ~38 cores.
⇒ pole_states(21) = 6.9×10⁷ / 2.43 = **2.84×10⁷**.

| H | predicted peak_states | predicted peak RAM | predicted cpu-s | predicted wall (uncontended) |
|---|----------------------:|-------------------:|----------------:|------------------------------|
| 20 (pole) | 2.84×10⁷ | ~30.8 GB | 1.51×10⁶ | ~11 h @38c |
| 19 | 1.16×10⁷ | ~12.6 GB | 6.3×10⁵ | ~5–6 h |
| 18 | 4.73×10⁶ | ~5.1 GB | 2.6×10⁵ | ~2–3 h |
| 17 | 1.93×10⁶ | ~2.1 GB | 1.1×10⁵ | ~1 h |

Walls are the soft prediction (core-sustain drops on lighter heights; and MAXJOBS=2 means
H20+H19 share 80 cores, so observed walls run longer than uncontended). cpu-s + peak_states
+ peak RAM are the hard predictions to score.

## Early reality-check (live, NOT yet validated — peak not reached)
- **peak_states model looks good:** H19 col2 `src`=1.13×10⁷ ≈ predicted peak 1.16×10⁷.
  Caveat: unknown whether col2 is H19's peak column — watch later columns before crediting it.
- **RAM ran ~4–5× my frozen per-height *prediction* — but the bytes/state CONSTANT is fine;
  the prediction method was wrong (corrected below in Recalibration).** Live RSS H19 ~56 GB @
  col2 vs my frozen 12.6 GB looks alarming, but 12.6 GB = peak_states(1.16×10⁷)×1086 B used a
  *resident-multiple of 1* — whereas resident RAM holds **src + the growing dest** at the
  transition. H19 col2: src=1.13×10⁷, dest-under-construction ≈ several×10⁷ → resident ≈
  5×10⁷ states × 1086 B ≈ **55 GB**, which matches the observed 56 GB at ~1086 B/state. So the
  per-state cost is ~right; my peak-RAM *derivation* under-counted by ignoring src+dest.

## Cliff recalibration (provisional, 2026-06-26) — foundation HOLDS, earlier alarm RETRACTED
**Correction:** the "~4–5× under-models RAM" I flagged earlier was a *prediction* error, not a
cost-model flaw. Two fixes:
1. **bytes/state is sound.** Independent anchor from the new harness (`bench_column`, n=14,
   single-thread, unfolded): **781.6 B/state** — same order as the lean-engine ~580 B figure (a
   bit higher at small n, less amortized). The batched-production ~1086 B (a(22) pole, measured
   75 GB/6.9×10⁷) reconciles with the live a(21) RSS once resident states are counted right (above).
2. **peak RAM = peak_RESIDENT_states × bytes/state**, where peak_resident ≈ peak_states × a
   *resident-multiple* (~2–3 across the heaviest src+dest+batch transition), **not × 1**. My frozen
   table applied ×1, hence the under-count. The forecast's cliff table did NOT — it was built from
   *measured* pole RAM, so it already bakes the multiple in.
**Therefore the cliff table stands:** lean ~580–780 B/state → a(23) pole 1.7×10⁸ ≈ 100 GB (fits
dalby only with I7), a(24) pole 4.0×10⁸ ≈ 240 GB (fits no box) → **cliff stays at a(24)**;
batched ~1100–1560 B/state → a(23) ≈ 220 GB → OOM without I7, exactly as scheduling-design says.
PLAN.md staging is **unchanged** (no re-stage).
**Firms at H20 peak:** when the pole hits its heaviest column, `max(rss_kb)` ÷ peak resident
states (heartbeat `src` + measured dest) pins the resident-multiple and the true bytes/state
under production config — the one number that would move the cliff if it surprises. **This is the
live oq3 deliverable.**

## Offline analysis recipe (run after the fold)
**oq3:** per height, `peak_RAM = max(rss_kb)` from telemetry.csv; `wall` = final `elapsed`
from h##.log; compare to the frozen table → calibrate bytes/state and the cpu→wall map.
**04:** join h##.log (per-col `src`,`rate`) with telemetry.csv (per-col max `rss_kb`) on
(H,col). Plot, across one height's columns: state count, peak RSS, throughput. The
question 04 turns on: does the early-column optimum (cheap, RAM-slack) differ from the
peak-column optimum (RAM-tight) by enough — >~15% wall or RAM headroom — to justify
per-column (T,B,K)? `rate` already visibly decays *within* a column (H20 col1 295→77/s),
and `src` jumps 52× col1→col2 — the variance is real; 04 quantifies whether it's exploitable.

## Status
- Sampler: `scripts/a21_telemetry.sh 30` on dalby, pid in `runs/a21fold/telemetry.pid`;
  self-exits ~10 min after the last a(21) proc ends (no orphan).
- Heartbeat logs: already retained (driver tees `h##.log`, append) through completion.
- H18/H17 give two clean predicted-before-ran points; H20/H19 give peak-RAM-before-peaked.
