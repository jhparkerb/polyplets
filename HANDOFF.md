# HANDOFF — for the next session

_Written 2026-06-22 ~22:00 ET, end of an autonomous multi-task push. Three jobs running across
gympie/ayr/dalby; all session deliverables committed. Read the WAITERS section first if you just
`/clear`ed — the background completion waiters do NOT survive a clear and must be re-created._

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
  **DECISION PENDING jasonp: (a) is the dalby window still open for ~1 day (it was "free
  for 2026-06-22"; now 06-23 — may have reverted to factoring), and (b) approve the
  tuned schedule (MAXJOBS=2 for h<=16, MAXJOBS=1 for h17-19; checkpoint/resume on for
  OOM safety).**

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
