# HANDOFF — for the next session

## 2026-06-25 ~13:15 dalby — REAL a(22) LAUNCHED + the u64-fold optimization (TOP)

- **The real a(22) is RUNNING on dalby:** `a21_reach.py 22 --jobs 1 --threads 40 --primes 3`,
  driver pid in `runs/anmodp_N22/driver.pid`, log `runs/a22_REAL.log`, tmux window `a22_REAL`.
  jobs=1 = strictly sequential → only ONE heavy sweep resident (≤84 GB) → **zero OOM risk**,
  auto-CRT-gated == a(20) at the end. **Conservative ~9–10 days** (heavy tail H17–21 ×3 runs
  sequentially; the ~6-day forecast needs RAM-aware overlap of H20 beside the pole, which I
  judged too risky to run unattended — 84+29 GB is too close to 122).
- **THE optimization to swap in (jasonp's catch — a real ~2-day path):** the 3 primes
  needn't serialize — the boundary-state enumeration is modulus-independent, and a(22) <
  2⁶⁴, so **one u64-exact sweep per height (no mod-p, no CRT)** does the expensive work once
  instead of 3×, AND removes the whole 3-prime RAM-juggling / scheduling problem. Verified:
  the u64 engine `sweepSquare8HeightMT` (sweep8.h) is exact + MT and gated == mod-p, BUT
  **lacks the R1 fold** → 2× states → won't fit 122 GB as-is. **The needed change: add fold
  to the u64 MT path (or u64 to the folded mod-p MT path `sweepSquare8HeightModPMT`).** Then
  pole ≈ 7×10⁷ folded states × u64 rows ≈ ~98 GB (fits), ONE sweep ≈ ~2 days, job ≈ ~2 days.
  **Do it carefully + gate END-TO-END == a(20)=1,025,573,519,362,016 before trusting it**, then
  kill the running mod-p job (resumable — rows banked) and relaunch with u64-fold. This was
  NOT done tonight (new MT engine = too risky to rush into a multi-day launch). Notes that
  drove the mod-p choice (RAM hedge): `docs/frontier-revision-plan.md:117-127`.
- Forecast doc `~/src/polyominoes-reach/docs/a22-forecast.md` says ~5–6 d (the achievable-
  with-overlap number); the running job is the safe ~9–10 d baseline; u64-fold → ~2 d.

## 2026-06-25 ~04:00 dalby (a(22) forecast + diagonal-sweep investigation)

**THE GOAL (ongoing): tell jasonp how long a(22) actually takes.** Current answer:

- **a(22) on dalby ≈ ~5–6 days** (3 mod-p primes). Single pole sweep H21 ≈ ~2 days; the
  3 pole primes **serialize** (RAM-confirmed: 84 GB each at t40, only 1 fits 122 GB; lower
  threads fit 2 but are 2.5× slower — net loss). Full writeup + all numbers:
  **`~/src/polyominoes-reach/docs/a22-forecast.md`** (the deliverable; read this first).
- Basis (all measured this session): pole = H=N−1 = H21; pole_states(22)=6.9e7 (rock-steady
  2.41×/N law, 6 ladder points N13–18); per-state cost grows 1.81×/N (no saturation,
  structural mask-enumeration); the live H21@N22 run sustains **~38 cores**; MT engine
  byte-identical-gated; end-to-end a(12) reproduces.
- **Pending tightening:** N20 pole sweep (H19@N20) still RUNNING on dalby (~3h in) — gives a
  5th→2-step extrapolation anchor. Waiter set earlier; if lost, re-create: it writes
  `runs/a22_forecast/n20_pole.log`. When it lands, fold its cpu_s/ratio into the forecast
  (should confirm ~4.45×/N) and tighten the ~2-day pole number.
- Forecast scripts: `scripts/a21_reach.py` (orchestrator), `a22_pole_ladder.sh`,
  `a22_pole_forecast.py`, `a22_mt_gate.sh`, `a22_ram_threads2.sh` — all in reach worktree.

**Big tangent — diagonal/4-direction transfer matrix (mostly a DEFLATION, recorded so we
don't re-chase it):**
- We explored a 45°/anti-diagonal sweep + 4-direction bounding-box split hoping for
  λ^(n/2). **Recalibration: our column TM is ALREADY at √λ per term (~2.42, < √λ≈2.665).**
  The exponent-halving is already banked by the boundary merge. A diagonal sweep's real job
  is "beat 2.42," not "beat 7.1" — a marginal nibble, not a revolution.
- **Our OWN repo already had this:** `results/tma_state_growth.md:18-24` records the killer
  (king diagonals span n×n → can't bound swept height); `docs/frontier-revision-plan.md:45-54`
  is an unrun "Phase 0.1 FLM scaling" GO/NO-GO gate = exactly this question, never answered;
  `docs/research-log-2026-06-22.md:382` has the `☐ (u,v) diagonal TM` checkbox.
- Measured (proxy): diagonal middle-cut signature base 2.76 vs column 3.22 (gap widening to
  n=9) — hints ~30% sparser, BUT the proxy ≠ engine peak, and the worst-case (max(w,h)) may
  kill it at the peak. The ONLY clean reason it might win: (u,v)=(x+y,x−y) rotation maps the
  worst-case king diagonal onto an axis line. Deciding it needs a diagonal state-counter
  built (compute) — the unresolved Phase 0.1 gate. Probes: `experiments/diag_width_probe.cpp`
  (max-ext ~0.77n, occupancy ⌈n/2⌉), `experiments/frontier_rank_probe.py`.
- **Literature (3 agents):** bounding-box/smaller-dim = standard (Conway/Jensen finite-lattice
  method). Diagonal sweep for GENERAL animals = appears novel (lit only does it for
  diagonally-convex subclasses). **King-polyplet TM enumeration = entirely novel; no published
  king growth constant.** A006770 sits at a(18) (Tremblay–Vernay 2024, Redelmeier/BFS
  generation Θ(λ^n)) — **we already hold a(19),a(20) via our √λ TM, so we're past the world
  record and a(22) is a genuine frontier comp with the best-known method.** Forecast premise
  intact. Full citations in the 3 agent reports (this session's transcript).

**bbox feature (validated, useful byproduct):** added `--bbox` to the reach tma engine →
B_{H,W}(n) (bounding-box-stratified polyplet counts, refines A006770). Validated: Σ_W=B_H(n),
transpose symmetry B_{H,W}=B_{W,H} (0 asymmetric), Σ=a(12)/a(14). CRT-exact driver
`scripts/bbox_crt.py`; exact tables `results/bbox_polyplets_n12.txt`, `..._n14_exact.txt`.
Costs ~3×a(n) (no speedup — diagonals defeat the half-height trick). **On branch
`feature/bbox-polyplets` in the reach worktree, UNCOMMITTED** (bbox engine + TMA_PROGRESS
counter in sweep8_modp.h + forecast doc + probes). COMMIT IT before any branch switch.

**Papers:** `papers/MISSING.md` is now a live list of un-findable citations for jasonp's
library lookups. Filed 6 PDFs this session (Barequet-Moffie 2007, Mertens 1990,
Mertens-Lautenbacher 1991, Read 1962, Klarner 1967, Klarner-Rivest 1973). Still missing:
Conway 1995 ×2, Enting 1980, Aleksandrowicz-Barequet; check-free: Tremblay-Vernay (RAIRO).

**dalby running now:** N20 pole sweep (H19, ~3h in); N22 climb (banking rows, at H15, single
prime — NOT the real job, just forecast data). gympie: idle (bbox/probe builds only).

---

_Written 2026-06-22 ~22:00 ET, end of an autonomous multi-task push. Three jobs running across
gympie/ayr/dalby; all session deliverables committed. Read the WAITERS section first if you just
`/clear`ed — the background completion waiters do NOT survive a clear and must be re-created._

## CURRENT STATE 2026-06-23 ~18:30 ET (LATEST — supersedes everything below)
- **modp sweep now MULTITHREADED + LOCK-FREE** (reach branch, commit 9e4c69b). The per-(H,p)
  reach sweep was single-threaded -> a(21)/a(22) heavy heights (H13-17) are cpu-HOURS each,
  serial, so --jobs alone left the long pole serial. Added sweepSquare8HeightModPMT: two
  parallel passes/column (expand into per-thread dest shards, then parallel merge), NO mutex.
  Byte-identical to serial (H=1..14, fold+nofold) + end-to-end CRT a(12)/a(14) correct.
  gympie H=11 N=21: 2.0x (locked) -> **3.16x (lock-free)** at T=8, sys 29s->0.05s; plateaus
  ~T=4 on gympie. `scripts/a21_reach.py` (gympie orchestrator) + `scripts/mt_scaling.sh`.
- **PRODUCTION SCALING CONFIG (measured, locked):** strided lock-free engine (commit 9e4c69b)
  + **`--threads 20`** + **`TMA_SHARD_MULT=32`** + (ayr only) **`numactl --interleave=all`** -->
  **~13.5s/heavy-sweep (H=11 N=21) on BOTH ayr and dalby, ~10x over serial.** Verified 3 reps
  each, stable. Engine deployed+built strided on ayr (~/polyominoes) and dalby (worktree
  ~/src/polyominoes-reach). gympie stays strided too.
  - **AVOID power-of-2 thread counts.** T=8/16/32 are ~2x SLOWER than T=12/18/20/24 -- a stable,
    architecture-INDEPENDENT effect (reproduced on ayr 4-node x86 AND dalby 1-node ARM, so NOT
    NUMA). Disproven causes: NUMA (dalby single-node shows it too), stride-aliasing (block-assignment
    fix made it WORSE at the optimum: 13.7->17.4, reverted), pure shard count (T=16/S=512 slow but
    T=18/S=512 fast). Mechanism UNEXPLAINED -- just use T=20. Block-assignment commit was reverted;
    9e4c69b (strided two-pass lock-free) is the keeper.
  - **ayr NUMA:** 4 nodes (0-7/8-15/16-23/24-31). Migration is harmless IFF memory is interleaved;
    `--interleave=all` removes the first-touch roulette (stable). CPU affinity (taskset) adds nothing
    over interleave. Node-PINNED (`--cpunodebind=i --membind=i --threads 8`) = stable 43s/node ->
    4 concurrent = throughput alternative. dalby (1 node, 128GB) needs no numactl.
  - **GOTCHA:** tma Makefile tracks tma_main.cpp only, NOT headers -> `rm build/tma` after a header
    edit or you ship a stale binary (bit us on ayr). See [[rebuild-remote-after-engine-edit]].
- **NEXT (production wiring, not yet done):** point a21_reach.py at `--threads 20 TMA_SHARD_MULT=32`
  (drop `--blocked`; non-blocked MT is the path), interleave on ayr; jobs x threads = 1 sweep on
  ayr(32c, leaves spare), 4 concurrent on dalby(80c=4x20). Then launch a(21)/a(22). dalby reach is
  gated ZERO-RISK behind n=19 holes (still running, ~16.5h); the scaling tests ran careful
  (ulimit -v 32G, <=T20) alongside holes -- modp RSS is only ~57MB so holes was never at risk.
- **a(21)/a(22) PLAN** (gympie small+medium heights, ayr+dalby heavy tail; dalby ZERO-RISK =
  holes-only until n=19 done): blocked on knowing each box's thread knee. a21_reach.py still
  uses --blocked (serial); switch production to --threads (non-blocked MT) sized to each box's
  knee x jobs = cores. NOT yet launched -- a(21) is hour-plus, a(22) many hours even MT.
- **a(20) CONFIRMED = 1,025,573,519,362,016.** ayr per-height run: h1..h19 measured
  (sum=1,025,572,357,100,549) + **h20 = 3^19 = 1,162,261,467 closed form** -> exact match.
  square8 IS the 8-neighbour (king/polyplet) lattice; the top height H=N is ALWAYS the
  trivial closed form 3^(N-1) (one cell/row, 3 king-shifts per inter-row step, fixed).
  ayr h20 sweep (a 2-day grind recomputing 3^19) was KILLED at 12:43 ET. **ayr now IDLE.**
- **ENGINE CHANGE (reach branch deploy/reach-modp-blocked, commit 8eec9d0)**: tma modp
  --only-height N now short-circuits H==N to 3^(N-1) instead of sweeping. Byte-identical
  (verified n=6,8,12,20), end-to-end reach CRT a(12)=257105146==master. Does NOT touch the
  24/24 per-height gate. Built in the gympie worktree ~/src/polyominoes-reach.
- **a(21) LIVE-ETA ORCHESTRATOR built**: scripts/a21_reach.py (reach worktree). Runs the
  N*3 (H,p) modp sweeps JOBS-parallel on GYMPIE (modp engine is MB-light, fits the 10-core
  cap -- no ayr needed), prints a continuously-updated SELF-CALIBRATED max-ETA (each height's
  first prime calibrates its remaining primes; 3rd CLI arg = #primes, =1 for a cost-curve
  calibration pass). Built-in gate: the CRT diagonal must reproduce a(20)/a(12). Tested
  N=14 VALIDATED (a(14)=11208974860). **a(21) single-prime CALIBRATION running on gympie**
  (measures the real per-height curve -> bake as fallback -> launch full 3-prime run).
- **dalby n=19 holes STILL RUNNING**: driver pid **1423357**, h18+h19 left (h19 long pole;
  h15/16/17 done). Waiter: `ssh dalby.jhpb.org "tail --pid=1423357 -f /dev/null"`. On finish:
  combine -> results/holes_n19.dalby.txt, sum-check sum_k == a(19)=151609203011580.

DELIVERABLES THIS SESSION (all committed on master):
- **lambda = 7.110 +/- 0.005** via differential approximants + theta=-1 biased ratio
  (experiments/series_da.py); FSS strip ladder extended to H<=13 (lambda_11=6.116,
  lambda_12=6.219, 13 pending) -> ~7.4-7.6 trending to 7.11, broken BST replaced
  (lambda_fss.py). Also lambda_0=6.94, amplitude C~0.19, lambda_k=lambda, symmetric
  ~sqrt(lambda), knight lambda~10-12 (subclass_growth.py, lattice_da.py,
  amplitude_ratios.py, lambda_ladder_fast.py [POLY_GF_ENGINE-aware]).
- **site-perimeter** added to g2 + FIRST cross-SOURCE validation vs Mertens 1990
  (results/site_perimeter*.txt, .md); #13/#15/#17 structural stats from existing samples.
- **gf_modp memory fixed**: CSR edge list + two-pass exact reserve -> H=13 peak 17->6.8GB,
  N-independent (results/modp_recover_profile.md). modp_recover.py: adaptive prime growth
  (fixes the H=11 CRT-wrap that failed C1) + parallel BM + P-hoist (results: 4.6h->min).
- **OEIS dedup pass** (oeis/README.md + in-file markers): maxholearea=known A001971
  (not for submission), A0/A1 masters superseded by submissions/oeis/, gf-orders +
  atom-degrees marked NOT-READY (paper says not-in-OEIS -> discuss with OEIS editors first).
- Full idea-list ledger + falsifications in docs/new-directions-2026-06-22.md.

NEXT: fold lambda_13 into FSS; sum-check n=19; on a(20) confirm -> a(21); editorial OEIS
calls (orders/atoms submit-vs-paper, maxholearea delete, square-bbox #3 Superseeker) = jasonp.
Remaining idea items needing code: #12 convex GFs, #14 contact density, #16 A389193;
quick: reach-2 growth via `gf_modp H N P 2` + lambda_ladder_fast.

## SESSION UPDATE 2026-06-23 (autonomous, jasonp asleep)
- **dalby n=19 hole count LAUNCHED + fitting** (driver pid 1423357; see dalby bullet).
  Reshaped from ~105 GiB to ~41 GiB peak via a **per-height kmax schedule**
  (kmax(H)=min(13,(N-H)+2), provably exact, validated byte-identical on an n=16 gate
  vs holes_n16.txt). THREADS=8 (benchmarked MT floor), MAXJOBS=6. ~67% headroom.
- **lambda upper bound depth-6 = 9.322** saved (results/lambda_upper_depth_sweep.txt).
- **C1 (H=11 fixed-height GF) FINISHED but FAILED VALIDATION** (2026-06-23 05:10,
  15h wall). `results/fixed_height_gfs.txt` now has `H=11 order=13381 validated=False`
  -- the recovered GF, expanded, disagrees with the engine at a fresh prime, so it is
  WRONG. **Do NOT fold in lambda_11 or the H=11 lifetime-3/atom extension** until a
  clean rerun. Diagnosis: `need = order//110 + 12 = 133` CRT primes was likely
  short for the order-13381 Q_11 coefficients, so CRT wrapped. CONFIRMED (cheap check,
  no compute): max Q coeff = 1241 digits = EXACTLY the 133-prime product ceiling, and
  3371/13382 coeffs sit within 30 digits of it -- textbook wraparound. True max coeff
  > 1241 digits (the 0.078*deg=1043 estimate under-predicts at H=11); order 13381 is
  fine (clean single-prime BM). >133 primes needed by an UNKNOWN margin. RECOMMENDED
  FIX (jasonp's call, gympie now free): rerun with generous primes, e.g.
  `python3 gf/modp_recover.py 11 11 250` (ceiling ~2333 digits), AFTER clearing only
  the coarse H11-gf checkpoint key in `runs/ckpt/fixedgf-H11_11/` (per-prime sweeps at
  N=26792 are cached + reused -> only ~117 new sweeps, gympie 8-way ~hours). BETTER
  long-term fix: make modp_recover.py grow primes + retry until validated=True, instead
  of the fixed `need = order//110 + 12` that silently wrapped. lambda_fss.py now SKIPS
  validated=False heights (BST 7.221 on H<=10). lambda_11 + H=11 lifetime-3 stay BLOCKED.
- **New-directions enqueued items worked** (docs/new-directions-2026-06-22.md, all
  committed): DONE #5 (site-perimeter + FIRST cross-SOURCE validation vs Mertens 1990,
  exact n=11/12/13; +min/max site-perim sequences), #9 (DA pipeline validated on
  king/triangular/cubic lattices), #10 (bbox aspect -> const ~1.4), #11 (free/one-sided
  amplitude ratios -> 1/8,1/4; tied to sqrt(lambda)), #13/#15/#17 (hole-area / rook-comp
  / gluing-graph from existing samples: 74% tree gluing-graphs, 90% area-1 holes). #1
  closed (both structural seqs Superseeker-novel). #8 knight started (~11-12, unconverged).
  STILL OPEN (need engine/code, deferred): #12 convex GFs, #14 contact density, #16 A389193.
- **New experiments/**: lambda_fss.py, series_da.py (lambda=7.110), subclass_growth.py
  (lambda_0=6.94), lattice_da.py, amplitude_ratios.py, sample_structure.py.
- **gympie also running** n=14 site-perim (tmux window sp14, pid 28682) alongside C1.
- **Found issue**: `make build/g2` fails under clang (Makefile -Wno-error=restrict);
  validated via direct compile. Needs a compiler-conditional guard (jasonp).

## Machines RIGHT NOW — 3 jobs running
- **gympie** (local, `~/src/polyominoes`): **C1 — H=11 fixed-height GF recovery**, nearly done.
  `bash` driver **pid 77451** in tmux session 0 window `2:c1-h11`, running
  `python3 gf/modp_recover.py 11 11 48 | tee runs/c1_h11.log` (8-way, 48 prime sweeps). Down to
  ~3 `gf_modp` workers (final shards), then the Python does GF reconstruction and **appends H=11**
  to `results/fixed_height_gfs.txt` (currently ends at H=10). When it lands → fold in **lambda_11**
  + the perf cores free. **DO NOT TOUCH C1.**
- **ayr** (`~/polyominoes`): **a(20) CONFIRMATION recount** — driver **pid 995458**
  (`runs/a20/parallel.pid`), tmux session 0 window `1:a20par` (pane 995439). Workers: pid 995469
  (`--only-height 18`), pid 996158 (`--only-height 20`). Heights 15/16/17 DONE
  (10204408045521 / 3357266652450 / 860061675780); **h18 + h20 still running** (~1.3 days in).
  THE gating item — confirms/refutes **a(20) = 1,025,573,519,362,016**; unblocks a(21).
- **dalby** (`~/src/polyominoes`, FQDN **dalby.jhpb.org** — the short alias does NOT resolve):
  **n=17/18 hole-count BENCHMARK — DONE 2026-06-23 ~05:39 dalby time, exit 0.** Both
  `results/holes_n17.dalby.txt` (84 rows) and `results/holes_n18.dalby.txt` (95 rows)
  complete. **CROSS-CHECK PASSED: `holes_n18.dalby.txt` == `holes_n18.txt` (ayr)
  byte-for-byte** (cross-ISA ARM/clang vs x86/gcc). n=17 dalby is new (no ayr n17 to
  compare yet). tmux window `2:holesbench` now idle. **RESULT — the benchmark corrected
  the n=19 projection: heaviest n=18 height is h18 = 46.4 GiB (47562.9 MB), NOT the
  ~28.8 GB the ROADMAP assumed (that was h17 = 29460.7 MB). Heaviest-height grows
  2.26x/term (h17@n17 20.5 GiB -> h18@n18 46.4 GiB), so n=19's heaviest height (h19)
  projects to ~105-111 GiB.** That FITS dalby (122 GiB avail) but only with ~10-15 GiB
  headroom and ONLY if the top heights run MAXJOBS=1 (the default per-height MAXJOBS=2
  does NOT fit n=19 — two big heights concurrently is ~170 GiB). n=18 total wall was
  ~4.8h at MAXJOBS=2; n=19 with top heights serialized ~ a full day.
  **n=19 LAUNCHED 2026-06-23 ~07:18 (jasonp approved ~1-day window).** Driver pid
  **1423357**, tmux session 0 window `n19holes`, `runs/holes_n19.log`. Reshaped to fit
  with big headroom via a **per-height kmax schedule** kmax(H)=min(13,(N-H)+2) in
  dalby_holes_perheight.sh — provably exact (hdrop drops only unreachable k; validated
  byte-identical on the n=16 gate vs holes_n16.txt). This collapses the tall heights
  (which dominate D_H but hold ~0 holes) ~5-7x: projected ~10-11 GiB each, first-wave
  realistic peak ~41 GiB. **THREADS=8** (benchmarked floor: 2->4 1.35x, 4->8 1.29x,
  8->16 NO gain -- MT saturates at 8), **MAXJOBS=6**. Observed 12.4 GB at 1:14 elapsed,
  110 GB free -> fitting (~67% headroom). On finish: combine ->
  results/holes_n19.dalby.txt, cross-check sum==a(19)=151609203011580, compare to ayr
  if/when ayr produces n19. SSD/out-of-core NOT needed (kmax schedule solved it).

## WAITERS — re-create these after `/clear` (3 background tasks)
Completion waiters are background Bash tasks; they die on `/clear`. Re-establish each as a
**`run_in_background: true`** Bash task (the remote ones also need **`dangerouslyDisableSandbox:
true`** for network). gympie MUST use **`gtail`** not `tail` (BSD `tail` lacks `--pid` and fires a
FALSE "finished" — cost a bogus signal this session). First check whether a job already finished
(then skip its waiter and do the follow-up instead).

**1. gympie C1** (local; skip if `grep '^H=11' results/fixed_height_gfs.txt` already present):
```
P=$(pgrep -f 'modp_recover.py 11 11 48' | sort -n | head -1); [ -n "$P" ] && gtail --pid=$P -f /dev/null; echo "C1 H=11 FINISHED - gympie perf cores free"
```

**2. ayr a(20)** (remote; bg + dangerouslyDisableSandbox). Re-find the driver pid from the pidfile:
```
AP=$(ssh ayr 'cat ~/polyominoes/runs/a20/parallel.pid'); ssh -o ServerAliveInterval=30 -o ServerAliveCountMax=20 ayr "tail --pid=$AP -f /dev/null"; echo "ayr a20 FINISHED"
```

**3. dalby holes benchmark — DONE 2026-06-23, do NOT re-create this waiter** (kept for reference):
```
DP=$(ssh dalby.jhpb.org "tmux list-windows -t 0 -F '#{window_name} #{pane_pid}' | awk '/holesbench/{print \$2}'"); ssh -o ServerAliveInterval=30 -o ServerAliveCountMax=20 dalby.jhpb.org "tail --pid=$DP -f /dev/null"; echo "dalby holes n17+n18 benchmark FINISHED"
```
(Linux boxes: plain GNU `tail --pid` is fine — `gtail` is a gympie-only requirement.)

## Session deliverables (ALL COMMITTED on master, except reach which is on its branch)
- **Reach engine — B composed with R1xR3 + parallelized** (`6f2a3a4` on branch
  **`deploy/reach-modp-blocked`**, built in worktree `~/src/polyominoes-reach`). `--blocked S`
  (drain-and-free partitioned u32/fold/modp store, ~2x less RAM on top of R1xR3) +
  `an_modp_crt.sh --jobs J --blocked S` (parallel independent (H,p) sweeps). **GATED**: 24/24
  byte-identical per-height (H∈{1,4,7,10}×fold×S∈{4,8,16}) + 3 end-to-end CRT configs == A006770.
  Fires a(21) once a(20) confirms.
- **lambda upper bound 10.354 → 9.355** (`ab6c4c8`) — iterated ancestor-exclusion (depth-5),
  validated on the square anchor (Eden 6.75 → 5.16). Rigorous interval now **[6.54, 9.355]**.
  PLATEAUS ~9.3 → reaching ~8 needs the **empty-cell-propagation** refinement (future work).
  `experiments/lambda_upper_bound_iterated.py` (numpy; runs on ayr).
- **lambda_0 correction** (`ab6c4c8`) — hole-free gap (λ₀~6.93 < λ~7.10) VERIFIED, but the
  "opposite the square lattice" framing was FALSE (both lattices decay ~0.977ⁿ).
  `results/lambda0-verification.md`.
- **OEIS — 4 sequences staged** (`d6f966f`, `submissions/oeis/`): hole-free, one-hole,
  **square-bbox (now computed to n=16** via ayr `--split`; marginal == A006770 ✓**)**,
  max-distinct-holes. 1/2/4 Superseeker-confirmed novel; **square-bbox novelty check still owed**
  (lookup string in `submissions/oeis/README.md`). jasonp submits.
- **dalby queue plan** (`f8dd46e`, `docs/dalby-queue-plan.md`) — n=19 hole-count ranked #1.
- **D1 fold-in** (`f8dd46e`, `results/maxhole-stratified-N16.dalby.txt`) — M_k(n) to n=16 from the
  finished dalby g2_split run.

## NEXT SESSION — pick up here
1. **When C1 lands**: fold in **lambda_11** (H=11 GF → lifetime-3 + sharper lambda bracket); perf
   cores then free → heavier gympie work OK (but keep it brief/targeted/RAM-light, see constraints).
2. **When a(20) confirms** (ayr): **run a(21)** with the `deploy/reach-modp-blocked` engine — THE
   reach goal. (Build in the worktree; an_modp_crt.sh with --fold --blocked --jobs.)
3. **dalby benchmark DONE (2026-06-23)**: n=18 == ayr byte-identical; heaviest height
   corrected to h18=46.4 GiB → n=19 heaviest ~105-111 GiB (see dalby bullet). **n=19 is
   feasible on dalby but TIGHT (MAXJOBS=1 at top, ~10-15 GiB headroom) and gated on
   jasonp confirming a ~1-day dalby window.** Awaiting his go/no-go + schedule approval.
4. **OEIS**: run the square-bbox Superseeker novelty check, then submit all 4 (jasonp).
5. **(Open research) lambda → ~8**: the empty-cell-propagation upper-bound refinement.
6. **(Ready) Reach**: compose Phase-4 OOC (`explore/reach-blocked-store`) on top of R1xR3xB for
   even bigger terms.

## Branches (unmerged)
- `deploy/reach-modp-blocked` — **THE reach keeper** (R1xR3 + B + parallel, gated). Worktree at
  `~/src/polyominoes-reach`.
- `deploy/reach-modp` — prior R1xR3 (superseded by the above).
- `explore/reach-blocked-store` — Phase-4 OOC, to compose next.
- `explore/cpp-stats-engine` — g2 stats / maxhole-stratified (n<=12; the n=16 extension is on
  master as `results/maxhole-stratified-N16.dalby.txt`).

## Standing constraints
- **gympie**: nothing heavy until C1's perf cores free; thereafter CPU is fine **only if brief,
  targeted, RAM-light** (commits/scp/small combines always OK) — no fat probes that spin the fan or
  risk OOM-killing a long job. The `ulimit -v` RAM guard does NOT work on macOS (silently ignored),
  so you cannot cap a reach probe's RAM that way — pick a size known to fit, or run it on ayr/dalby.
- **gtail not tail** for gympie `--pid` waiters (see [[long-jobs-tmux-not-nohup]]).
- 10 perf-core cap; never pkill/killall (explicit numeric PIDs); long jobs in tmux foreground.
- Claude preps OEIS/paper/repo; **jasonp pushes submit / external sends**. Publishing is his call.
