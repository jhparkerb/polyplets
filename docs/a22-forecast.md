# a(22) on dalby — runtime forecast

_Settled overnight 2026-06-24/25 by direct measurement on dalby. Headline: **a(22) is a
~5-day run (range 3–7); the single H21 pole sweep is ~2 days.** Corroborating point N19
landing tightens the cpu(N) extrapolation. All scripts in `scripts/a22_*`; raw measurements
in `runs/a22_forecast/`._

## Bottom line — a(22) on dalby is a **multi-day** run (settled by direct measurement)

- **The single H21 pole sweep (one prime): ~2 days** (≈45 h) = pole_cpu(22) ≈ 6.2×10⁶ cpu-s
  (ladder cpu(N) trend, §4a) ÷ the **~38 cores the pole sweep actually sustains** (measured
  directly on the live H21@N22 run, §4b — far above the ladder's ~8× because the huge sweep
  finally has work to fill threads).
- **The full 3-prime a(22) job: ~5–6 days** (RAM-confirmed the 3 poles serialize; range ~4–7),
  set by fitting the three H21 sweeps
  (each ~75 GB at t40) into 122 GB — they can't all run at once, so they partly serialize.
  Best schedule (heavy primes at reduced threads to pack 2–3 concurrently + lighter heights
  filling cores) targets ~3–4 days; naive sequential is the high end.
- **The two load-bearing numbers are measured, not extrapolated:** the pole's ~38-core
  scaling is measured directly on the live H21@N22 run, and that run **refutes the optimistic
  "hours" branch** — one *early* column (1.05M of 69M states) alone burned >20,000 cpu-s,
  exceeding the entire optimistic budget. Only the pole's *total* cpu is extrapolated, off a
  clean 4-point cpu(N) trend (5th point N19 landing for corroboration).
- **Pole = H21, pole_states(22) = 6.9×10⁷** (rock-solid 2.43×/N law, 6 points N13–18).
- **Why not hours, why not weeks:** per-state cost grows ~1.81×/N (the H-tall frontier's
  exponential mask enumeration — structural, confirmed flat-ratio over N15–18, no
  saturation) → *not hours*. But the pole sweep scales to ~38 cores → *not weeks*.
- **No algorithmic shortcut:** the per-state exponential is the transfer-matrix branching
  factor itself; the only alternative (Redelmeier, ~a(n)=5×10¹⁶ ops) is ~10⁹× worse. The
  levers (MT ~38×, schedule ~2×) shave constants, not the exponent.
- **Correctness:** MT engine byte-identical to serial (N14/16) + deterministic + reproduces
  known a(12); production self-gates 3-prime CRT vs a(20). **Verified.**
- **Improvements applied this session:** rebuilt+validated the MT engine on dalby; added an
  env-gated live-progress counter to the MT path (`TMA_PROGRESS=1`) — observability for the
  multi-day run; established the production config + RAM-aware 3-prime schedule; showed the
  ayr a(21) run wastes the MT speedup (single-threaded).
- **Launch command:** §6.

---

## 1. The cost model (why the wall is one number)

a(22) = Σ_{H=1}^{22} B_H(22), one mod-p transfer-matrix sweep per (height H, prime p),
CRT-combined over 3 primes near 2³¹. H=22 is the closed form 3²¹ (free). So the job is
**21 heights × 3 primes = 63 independent sweeps**.

dalby = aarch64, **80 cores**, 122 GB free, single NUMA node; their own perf campaign
measured it scaling *perfectly* to ~76 concurrent sweeps (DRAM ~3 % utilized, no
contention wall). 63 < 76, so by *core* count every sweep runs concurrently and the wall
would be the single heaviest sweep (the "pole"). The one wrinkle that breaks the pure
"one sweep" story is **RAM**: the pole sweep is ~75 GB, so the three H21 primes can't all
be resident at once — that's what lifts the job from ~2 days (one pole) to ~5 days (§4).

## 2. Correctness gate (must pass before any number is trusted)

The MT (`--threads`) path must be byte-identical to the single-thread path per (H,p);
otherwise a(22) would be silently wrong. `scripts/a22_mt_gate.sh`:

| check | result |
|---|---|
| N=14, H=9..12, serial vs MT | **PASS** — byte-identical |
| N=16, H=8..13, serial vs MT(24) | **PASS** — byte-identical |
| MT determinism (threads 2,8,24 ×3, shard 32/64) | **PASS** — bit-identical |
| end-to-end a(12) from N=22 single-prime columns (Σ_H B_H(12)) | **PASS** — = 257105146 exactly |
| final guarantee: production 3-prime CRT == known a(20) | built into launch (`EXACT` gate) |

**Correctness verdict: the MT engine is sound** — byte-identical to serial across N=14/16,
deterministic across thread/shard counts, and the full summed pipeline reproduces the known
a(12). The production run additionally self-gates its 3-prime CRT against the confirmed a(20).

(An earlier apparent mismatch was a *stale older binary*, not an MT bug: on the freshly
rebuilt engine MT == serial at N=14/16.)

## 3. Measured structure

- **State growth:** peak_states ≈ 2.45×/height, **N-independent at low/mid H**
  (H12: 38 009 @N18, 39 048 @N20, 39 259 @N22 — identical). Build-independent quantity.
- **Pole = H=N−1** (settled). Complete small-N curves show peak_states rises *monotonically*
  to the highest non-trivial height: N13 …H11=11284, H12=23778; N14 …H12=27831, H13=57408 —
  still rising (ratio ~2.1) at spare-cells=1. No middle turnover. So for a(22) the pole is
  **H21** (H22 is the free 3²¹). (An earlier "middle pole" read came from contended walls.)
- **Pole-states vs N grows a rock-steady 2.43×/N** (pole = H=N−1, 6 points):
  N13=23778 … N18=2 009 135 → ratios 2.41/2.41/2.42/2.45/2.45 ⇒ **pole_states(22) ≈ 6.9×10⁷**.
- **MT parallelism is size-dependent, NOT a flat ~6×.** Small ladder sweeps cap at 3–8×
  (load imbalance, not enough work); the real 69 M-state pole sweep sustains **~38 cores**
  (measured live). Plan the pole at its measured ~38×, the light heights at their few×.
- **Per-state cost grows ~1.81×/N and does NOT saturate** (the frontier-height mask
  enumeration is exponential in H) — so pole_cpu ×4.44/N. This is the finding that makes
  a(22) days, not hours; see §4.
- **MT effective parallelism rises with sweep size** (3.4× at N15 → 5.9× at N16, contended;
  the pole is far larger → expect closer to the ~9–10× cap). _Ladder N17–20 pinning the
  wall growth + the clean speedup test will finalize the hours figure._
- **Methodology caveat (locked in):** use **peak_states** (build/thread-independent) to
  locate the pole and **clean wall** (uncontended) to size it. Do NOT use cpu_s across
  runs — MT inflates it (climb H13 @t26 cpu=4690 vs N20 H13 serial cpu=3331, same work,
  states 105153≈102870), and the old N20 serial run is a different binary. The forecast
  number is a *measured MT wall*, not derived from cpu_s.

Measured N=22 climb anchors (sequential, t26): H11 states 14798, H12 39259, H13 105153.

## 4. The forecast

**Firm:** pole = H21; pole_states(22) = **6.63×10⁷** (log-linear fit, ratio 2.414/N over
measured N=13–16, σ negligible — 4 points on a straight line).

**Two measured inputs, multiplied.**

(a) **Pole-sweep total cpu, from the ladder (H=N−1, directly measured whole-sweep cpu):**

| N | states | cpu_s | cpu ratio | wall_s | eff_par |
|--:|--:|--:|--:|--:|--:|
| 15 | 138 190 | 183.5 | — | per-state 1.33 ms |
| 16 | 335 021 | 808.9 | 4.41 | 2.41 ms (×1.82) |
| 17 | 820 620 | 3 630.3 | 4.49 | 4.42 ms (×1.83) |
| 18 | 2 009 135 | 16 056.6 | 4.42 | 7.99 ms (×1.81) |
| 19 | 4 909 876 | 72 113.0 | 4.49 | 14.69 ms (×1.84) |

cpu(N) climbs a **steady 4.45×/N** (states ×2.44 × per-state ×1.82; per-state ratio flat at
1.82/1.83/1.81/1.84 over **5 points — no saturation**, structural: `forEachViableMask` is
exponential in the frontier height H). Extrapolating N=19→22 (just **3 steps**):
**pole_cpu(22) ≈ 72 113 × 4.45³ ≈ 6.4×10⁶ cpu-s ≈ 1 780 cpu-hr.** (N20 pole sweep running
→ 2-step.)

(b) **Pole-sweep parallelism, measured directly** by running the real H21@N22 sweep:
it sustains **~38 cores** (3 449–3 751 % CPU over minutes) — *far* above the ladder's 8×,
because the 69 M-state sweep finally has enough work to fill threads (eff_par rises
monotonically with size: 3.4→5.9→6.1→8.0→~38). This is the number that turns "weeks" into
"days." The same run **refutes the optimistic branch**: one *early* column (1.05 M of 69 M
states, loose budget ⇒ expensive) alone burned >20 000 cpu-s — already more than the whole
optimistic budget; per-state does not saturate.

**⇒ single H21 pole sweep (one prime): pole_cpu/par ≈ 6.4×10⁶ / 38 ≈ 1.7×10⁵ s ≈ ~47 h ≈
~2 days.**

**3-prime job (the deliverable number): ~5 days, range ~3–7.** Each pole sweep is ~75 GB at
t40, so the three H21 primes can't all be resident at once in 122 GB — naive sequential
gives ~3×2 d ≈ 6 d (+ the H20/H19 tails overlapping on spare cores). RAM-aware scheduling
(heavy primes at reduced threads to fit 2 concurrently, lighter heights packing the rest)
pulls it toward ~3–4 d. The wall is **the heavy-prime schedule against RAM**, not single-
sweep speed.

_Corroboration in flight: ladder N19 (5th cpu point, ~45 min) tightens the 4.44×/N
extrapolation from 4→3 steps._

**3-prime RAM caveat (the scheduling tension):** each pole sweep ≈ 75 GB at t40
(~1.1 KB/state × 6.9×10⁷; per-thread shard maps dominate the overhead). 3 concurrent at t40
= 225 GB > 122 → the 3 H21 primes can't all be resident, so they partly **RAM-serialize**.
- `--blocked` is **not** the fix: that store path is single-threaded (takes no `--threads`),
  trading the whole ~38× MT for RAM — a net loss.
- **RSS-vs-threads now measured (N17 H16, 2026-06-25):** t40 = 1.22 KB/state (pole ≈ 84 GB,
  1 fits), t24 = 1.06 KB/state ~same speed (still 1 fits), t8 = 0.71 KB/state (2 fit, 98 GB)
  but **2.5× slower** (1546 vs 603 s). No thread count both fits two poles *and* stays fast —
  so the **three H21 primes serialize**, wall ≈ 3 × one pole sweep, lighter heights hidden on
  the other ~42 cores. This collapses the band to the **upper-middle: ~5–6 days** (not the
  3–4 a clean 2-concurrent pack would have given). The earlier "lower threads → fit more"
  hope is killed by the speed penalty.

## 5. Improvements to minimize the wall (in priority order)

1. **Use the MT engine — the single biggest lever.** The a(21) run currently on ayr is
   **single-threaded** (`nlwp=1`, no `--threads`); it throws away the whole MT speedup. The
   pole sweep scales to **~38 cores** (measured), so MT turns a ~70-day serial pole into a
   ~2-day one. This is most of the win and costs nothing.
2. **Config: `--threads 40 --shardmult 32` (non-power-of-2).** Verified byte-identical to
   serial. Effective parallelism rises with sweep size — small heights get 3–8×, but the
   pole sweep gets ~38×, so size the heavy primes at high thread counts.
3. **Concurrent-sweep schedule (matches dalby's strength).** 21 heights × 3 primes = 63
   independent sweeps; dalby scales cleanly to ~76. Run them concurrently and **give the
   pole heights (H21, then H20) their own large thread allotment** — they are the wall;
   everything else hides behind them. H=N (3²¹) is short-circuited — one height free.
4. **Don't bother with 2 primes** (CRT threshold P^(1/22)=7.05 < λ≈7.10 — not provable) or
   PGO on dalby (ARM: ~0%). Multi-machine (ayr/gympie taking light heights) shaves only the
   tail; the wall is dalby's pole sweep regardless.
5. **No quick algorithmic win for the pole — and the method is already the right one.**
   If per-state cost is the exponential mask enumeration (`viableRec`, the transfer-matrix
   branching factor), it is intrinsic: the perf campaign already found `viableRec`
   ~0%-optimizable and `--blocked`/fixed-width-TM are transposes with identical compute.
   The only alternative method — Redelmeier/g2 direct generation (used for a(19)) — costs
   ~a(n) ≈ **5×10¹⁶ operations** (it enumerates the polyominoes themselves), vs the
   transfer matrix's ~6.5×10⁷ pole states: ~10⁹× worse, utterly infeasible. So the
   transfer matrix is provably the right tool and its pole cost is a genuine floor. Cutting
   it materially needs a richer boundary-symmetry state encoding — research, not a config
   change. **If N18/N19 confirm the growth, the honest message is: a(22) is a
   multi-week run; the wall is set by physics of the method, and the levers above only
   shave constant factors (MT ~6×, schedule ~2–3×), not the exponent.**

## 6. How to launch the real job

```
# on dalby, in ~/src/polyominoes-reach, MT engine built (byte-identical-gated):
python3 scripts/a21_reach.py 22 --jobs <J> --threads 40 --shardmult 32 --primes 3
#   --primes 3 -> exact CRT; built-in gate verifies the diagonal reproduces a(20) =
#   1,025,573,519,362,016 and a(12) before declaring a(22). Idempotent/resumable
#   (per-(H,p) rows; a kill costs one sweep, not the run). Heartbeats in runs/anmodp_N22/.
```
Schedule note: the default `--jobs` runs heights concurrently; ensure the H21/H20 sweeps
get a big `--threads` share (they set the wall). Provenance: binary carries the commit
stamp; every sweep must exit 0 + non-empty or the CRT flags it (no silent wrong answer).

_Expected wall + exact J/T: §4 (filling from the pole ladder)._
