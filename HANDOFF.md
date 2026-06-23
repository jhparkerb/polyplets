# HANDOFF — for the next session

_Written 2026-06-22 ~22:00 ET, end of an autonomous multi-task push. Three jobs running across
gympie/ayr/dalby; all session deliverables committed. Read the WAITERS section first if you just
`/clear`ed — the background completion waiters do NOT survive a clear and must be re-created._

## CURRENT STATE 2026-06-23 ~17:00 ET (LATEST — supersedes everything below)
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
