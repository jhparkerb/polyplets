# dalby queue plan — the case for pushing dalby harder

_Written 2026-06-22. Planning/writing only — no jobs launched by this document._

**The ask.** dalby (the only >78 GB host) is up for 2026-06-22 and currently runs
one D1 job: `scripts/g2_split.sh 16 --maxhole-strat max`, 80 workers, full machine,
tmux session 0 window `d1strat`, output `runs/gsplit_maxholestrat_N16/combined.txt`.
jasonp is "open to making a case for pushing dalby harder once the current jobs
finish." This is that case: a ranked queue, with predicted costs, the exact
commands, the checklist items each must clear, and a launch order that respects the
**125 GiB firm ceiling (no swap)** and the **bandwidth-limited useful-core count
(~25–35, NOT 80, for holes/TM sweeps)**.

## Hard constraints (from machine memory + holes-per-height guidance)
- **125 GiB RAM is a FIRM ceiling.** No expansion planned. No swap is "fitting"
  (checklist item 2). RAM-borderline jobs have **no escape hatch** — benchmark, then
  bound to fit.
- **Only 4 of 8 memory channels are wired** (permanent). Our TM/holes sweeps are
  memory-LATENCY-bound at **~25–35 useful cores** for an n=18 per-height run, and a
  single heavy height fell from 10.6 effective cores at 15 GB to 4.6 at 31 GB as its
  hash state outgrew cache. The 67-of-80 figure is CADO's sparse-GF matmul — **does
  not apply to us.** So "fill 80 cores" is achieved by **per-height parallelism**
  (`scripts/dalby_holes_perheight.sh`, MAXJOBS concurrent heights), not by
  `--threads 80`.
- **Production engines on dalby are clang/ARM** (`build/tma`, `build/tma_holes` built
  `make CXX=c++`, clang 19.1.7; gate-TMA GREEN A–L 2026-06-21). clang/ARM is the
  2-axis decorrelation (compiler + ISA) vs ayr's gcc/x86 — strongest for the holes
  result, which has no independent-algorithm cross-check above n=14. `make
  CXX=clang++` does NOT work (that name isn't installed); use `make CXX=c++`.
- Repo on dalby is **`~/src/polyominoes`** (mirrors gympie; NOT `~/polyominoes`).
  FQDN `dalby.jhpb.org` (short alias does not resolve off-host). `/` ~376 GB free
  (watch checkpoint growth).

---

## Candidate jobs, ranked by value

### Rank 1 — n=19 EXACT hole count (#28, deliverable (a))
**Why it's #1: it is the natural and essentially the ONLY big-RAM-only job we have
ready.** n=18 already peaked **74.6 GB measured** (ayr, 44h single-thread, 0 swaps)
— it fits nowhere but dalby. n=19 extends the hole-stratified counts to match the
main a(n) reach (a(19)), and feeds #25 (OEIS — the hole-stratified sequences are all
novel) and #17 (paper). It is the headline term that dalby specifically exists to make.

**RAM/cores/wall — basis.**
- n=18 = **74.6 GB measured** (ayr, all-heights single-thread). Per the diagonal RAM
  model (`reach.md`), the tallest-strip term-to-term ratio is **×2.42** but the
  hole-stratified runs carry a larger constant; the memory note pegs raw n=19 holes
  at **~120–150 GB (≈ 74.6 × 1.7–2×)** — i.e. **RAM-borderline-to-OVER on 125 GiB.**
  This is the whole risk. It must be **bounded** to fit:
  - `--kmax 13 --hdrop` caps the holes dimension: drop partial states whose hole
    count exceeds kmax. **Exact for all k ≤ kmax** (holes only seal, never reopen),
    so kmax=13 loses nothing for the published k-slices (n=18 max was 10 holes;
    kmax=13 is safely above the n=19 max). This is the lever the memory note names.
  - **Per-height parallel** (`dalby_holes_perheight.sh`): RAM = MAXJOBS × heaviest
    single-height peak, NOT the all-heights 120–150 GB. Heaviest single height
    (kmax13/hdrop) est ~15–35 GB at n=18 scale; **MAXJOBS=2–3 ⇒ ~45–105 GB** — fits
    125 GiB with headroom, and uses far more than 3 cores.
- **Cores:** `--threads 16` per height × MAXJOBS 2–3 = nominal 32–48, realized ~25–35
  useful (bandwidth wall). Do NOT raise `--threads` to chase 80.
- **Wall:** n=18 was 44 h single-thread on ayr. Per-height-parallel + the ~10× faster
  MT/checkpoint engine + dalby's core count should bring n=19 to **order 1–3 days**,
  but this is the softest number — the benchmark step exists to pin it.

**Checklist items it must clear** (docs/job-checklist.md):
1. *Predict the cost* — **benchmark first** (see below); do NOT launch n=19 blind.
2. *Fit the budget* — only after dalby is idle (D1 done). MAXJOBS chosen so
   MAXJOBS × measured heaviest-height RSS < 125 GiB with real headroom, no swap.
3. *Saved in-repo script* — `scripts/dalby_holes_perheight.sh` (committed, self-
   describing header). ✓
4. *Provenance/observability* — `build/tma_holes` is clang/ARM with baked stamp;
   each height emits start/heartbeat/done + peak_rss to `runs/holes_n19_ph/h<H>.log`. ✓
5. *Recoverable* — `--checkpoint runs/holes_n19_ph/ckpt_h<H>` per height; finished
   heights skip on re-run, in-progress resume. ✓
6. *Recorded* — one HANDOFF line: "dalby: n=19 exact hole count (#28(a)) — the
   big-RAM-only term, feeds OEIS/paper."

**Benchmark-first step (the gate before committing n=19):**
```
# On dalby, after D1 clears. Validates the engine + MEASURES heaviest-height RSS.
# n=17 is fast and confirms correctness vs the n<=14 flood + A006770 sum-invariant;
# n=18 reproduces the known 74.6 GB result and pins the real per-height RSS curve.
cd ~/src/polyominoes
make CXX=c++ build/tma_holes                       # ensure clang/ARM, baked stamp
scripts/dalby_holes_perheight.sh 17 2 16           # quick correctness + timing probe
scripts/dalby_holes_perheight.sh 18 2 16           # RSS calibration: read peak_rss from
                                                   #   runs/holes_n18_ph/h*.log heartbeats
# CHECK: results/holes_n18.dalby.txt == results/holes_n18.txt (ayr) byte-for-byte
#        (clang/ARM vs gcc/x86 cross-ISA decorrelation of the hole result).
# DECIDE MAXJOBS for n=19 from the measured n=18 heaviest-height RSS:
#   MAXJOBS = floor( ~110 GiB / heaviest_height_RSS ), clamp to >=1.
```
**Exact production command + outputs:**
```
cd ~/src/polyominoes
# MAXJOBS from the benchmark (start 2, bump only if heartbeat RSS shows headroom):
scripts/dalby_holes_perheight.sh 19 2 16
#   -> runs/holes_n19_ph/h<H>.{out,log}   (per-height, checkpointed, observable)
#   -> results/holes_n19.dalby.txt        (combined n k count distribution)
```
**Validation on completion:** per-n sum == A006770 a(19); n≤14 rows == the flood
oracle `results/holes_n14.txt`; n≤18 rows == `results/holes_n18.txt`.

---

### Rank 2 — a(22) diagonal term (#21 / #19) — LATER, gated on a(21) + compression
**Why #2, why later.** a(22) is the first a(n) term that exceeds ayr's 78 GB
(`reach.md`: diagonal ~314 M states ⇒ **~85–100 GB** @270–320 B/state) — so it is
genuinely dalby-class. BUT it is **gated**: (i) **a(20) must confirm** (running on
ayr now — the gating item for ANY new reach term), then (ii) **a(21)** must land
(fits ayr at ~35–41 GB, so a(21) is NOT dalby-only and should run on ayr, not here),
and (iii) the #20 counts-row compression (~2.2×, recast in
`docs/state-store-compression.md`) would drop a(22) toward ~45 GB and might even
let it run on ayr — which would remove it from the dalby queue entirely. So a(22) is
a real dalby candidate **only if compression slips and a(21) is already done.**

**RAM/cores/wall — basis.** Diagonal job (tallest strip H=22) is the RAM driver:
~314 M states × 270–320 B = **85–100 GB** raw (`reach.md` table). Fits 125 GiB raw
**without** compression — comfortably with it. Cores: the diagonal is a single
`--only-height 22` sweep; within-height MT is ~2× useful, so this is a **few-core,
RAM-heavy** job (the opposite profile from the holes sweep — it does NOT fill the
box). Wall: ~2.4× the a(20) diagonal wall-clock per term ⇒ order several days.

**Checklist:** (1) benchmark = re-measure the a(21) diagonal RSS on whatever host
runs it to pin the ×2.42 anchor before a(22); (2) fits 125 GiB raw with headroom,
single heavy job so no MAXJOBS stacking; (3) driver script = a single-height diagonal
runner (the `--only-height N --checkpoint` pattern, same as the a20cross driver);
(4/5) `build/tma` clang/ARM, `--checkpoint runs/a22/ckpt_h22`; (6) HANDOFF line.

**Command sketch (do NOT run until gated):**
```
cd ~/src/polyominoes
make CXX=c++ build/tma
# diagonal driver, single tallest height, checkpointed:
build/tma square8 22 --only-height 22 --checkpoint runs/a22/ckpt_h22 \
  > runs/a22/h22.out 2> runs/a22/h22.log
# plus the remaining heights 1..21 (lighter; can run on ayr / gympie in parallel)
```

---

### Rank 3 — reach a(21) via the R1×R3 mod-p engine — ONLY if it can't run elsewhere
**Why #3, conditional.** a(21) **fits ayr** (~35–41 GB, `reach.md`) so it is **NOT
dalby-only** — by the "≤78 GB stays on ayr (x86 cross-ISA partner)" rule, ayr is the
correct host. It belongs on the dalby queue **only** if (a) ayr is occupied/unavailable
when a(21) is unblocked, AND (b) the composed reach engine (R1×R3 fold/mod-p, branch
`deploy/reach-modp`, + the blocked store B on `explore/reach-blocked-store`) is ready.
The reach engine is **gated on a(20) confirming** regardless of host.

**Basis.** R1×R3 fold + u32 mod-p sweeps are ~4× less RAM than the exact u64 sweep;
a(21) at ~35–41 GB exact ⇒ well under 125 GiB even unfolded, trivial on dalby. The
`an_modp_crt.sh` driver (on `deploy/reach-modp`) is **GATED: == A006770 for n≤12**.
Per-height parallelizable — the (H,p) sweeps are independent, so this DOES fill cores
(3 primes × up to N heights), bandwidth-capped at ~25–35 useful.

**Command (if it lands here, after a(20) confirms + engine composed):**
```
cd ~/src/polyominoes
git checkout deploy/reach-modp        # the keeper branch for reach
make CXX=c++ build/tma
scripts/an_modp_crt.sh 21 --fold      # 3 primes x heights -> CRT -> exact a(21)
#   -> runs/anmodp_N21/rows_<p>.txt, then CRT printout
# (production parallel variant: scripts/an_fold_parallel.sh per-height pattern)
```
**Default recommendation: run a(21) on ayr, keep dalby for n=19 holes.** List it here
only so the option is documented.

---

### Others considered — and why they are NOT queued on dalby
- **a(20) confirmation** — already running on ayr; it's the gate, not a dalby job.
- **H=8 / H≥9 hole GFs (#28 (b))** — wall is recurrence **order ∝ height** (a TIME
  limit, N≳9000, ∝N²), **not RAM**. dalby's RAM doesn't help; H≥9 needs a smaller
  recurrence, not a bigger box. Stay on gympie. Not queued.
- **#27 sampling-scaling, small-H bivariate GFs, lambda_11 GF recovery** —
  gympie-friendly, RAM-light, already placed. Wasting dalby on them.
- **D1 stats extension (g2_split to n=17)** — possible follow-on to the current D1
  job, but it's a generation sweep (embarrassingly parallel, RAM-light) that could
  run on ayr; only park it on dalby opportunistically if dalby would otherwise idle.

---

## Recommended launch ORDER (after the D1 g2_split job clears)

The D1 job owns the whole machine (80 workers). **Nothing new launches until
`runs/gsplit_maxholestrat_N16/driver.pid` is gone** (D1 done) — checklist item 2
forbids stacking against its peak.

1. **Rebuild the holes engine clang/ARM** (12 s):
   `make CXX=c++ build/tma_holes` — confirm `.comment` shows clang 19.1.7, gate-TMA
   if not already green on this tree.
2. **Benchmark n=17 then n=18** (`dalby_holes_perheight.sh 17 2 16`, then `18 2 16`).
   Confirm correctness (== ayr `holes_n18.txt`, == flood, == A006770 sum) and
   **measure the heaviest single-height RSS** from the heartbeats. This is the
   checklist-item-1 gate. ~hours.
3. **Set MAXJOBS for n=19** = floor(~110 GiB / measured heaviest-height RSS), clamp
   ≥1; start at **2** and bump only if live heartbeat RSS shows real headroom under
   125 GiB (no swap). Then launch **Rank 1: `dalby_holes_perheight.sh 19 <MAXJOBS> 16`**.
   This is dalby's headline run; let it own the box.
4. **While n=19 holes runs**, dalby is RAM-committed — do **not** start a(22) or a(21)
   reach alongside it (a single heavy diagonal/reach job + a 45–105 GB holes sweep
   would blow the ceiling). Queue them for *after* n=19 holes completes.
5. **After n=19 holes:** if a(20) has confirmed and a(21) is done/ayr-bound, evaluate
   **Rank 2 (a(22))** — but first check whether #20 compression has landed (it may
   move a(22) to ayr and free dalby). **Rank 3 (a(21) reach)** only if ayr is
   unavailable and the composed engine is ready.

Throughout: useful cores cap ~25–35 (bandwidth wall) — reach it via per-height
concurrency, never `--threads 80`.

---

## Open questions / decisions for jasonp

1. **n=19 holes kmax.** Plan uses `--kmax 13 --hdrop` (exact for k≤13; n=18 max was
   10 holes). Keep 13, or tighten to 11–12 to buy more RAM headroom if the n=18
   benchmark shows a single height running hotter than ~35 GB? (Tightening stays
   exact as long as kmax ≥ the true n=19 max-hole count, which we expect ≤ ~11.)
2. **MAXJOBS aggressiveness.** Start at 2 (conservative, ~45–105 GB) and bump live,
   or authorize a one-step bump to 3 up front if the n=18 heaviest height measures
   ≤ ~30 GB? (3 × 30 ≈ 90 GB, still under 125 with headroom.)
3. **a(22) host, pending compression.** If #20 counts-row compression lands and drops
   a(22) to ~45 GB (fits ayr), do we keep a(22) on ayr and reserve dalby purely for
   the next dalby-only frontier — or run a(22) on dalby anyway for the clang/ARM
   decorrelation cross-check? (Default: ayr if it fits; dalby only if it doesn't.)
4. **a(21) reach placement.** Default is ayr (it fits). Confirm we do NOT pre-empt
   dalby's n=19 holes for a(21) reach unless ayr is genuinely unavailable.
5. **Decorrelation value.** Is the clang/ARM cross-ISA recount of n=18 holes (a
   byproduct of the benchmark step) worth recording as a confirmation in RESULTS, or
   just a calibration step? (n=18 currently has only the gcc/x86 single-engine count
   above n=14.)
6. **dalby term.** Memory says machines free as of 2026-06-21; what is dalby's actual
   end-of-availability? n=19 holes is order 1–3 days — confirm the window covers it
   before launching, so a kill doesn't cost the run (it checkpoints, but still).
