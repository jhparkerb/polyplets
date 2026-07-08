# HANDOFF — 2026-07-08 (utilization work, branch `steal-wall-time-floor`)

**Not yet merged to kink-carry/master.** This session's work (a(n) engine
whole-run utilization, per jasonp's 2026-07-07 `/goal`) lives on
`steal-wall-time-floor`, branched from `kink-carry@2cb81a4`. Term chase
stays parked per the 2026-07-07 entry below; this is a separate,
reopened thread specifically for utilization.

**6 bottlenecks found and solved, deployed to `scripts/dalby_term.sh`,
each independently real-dalby-validated with correct output:**

1. **Straggler Tail** — `--overlap-heights` was only ever measured at a
   fixed 2 (one pair); raised to "all owned heights" per
   `results/scheduling.md`'s own original recommendation. 1.82x
   wall-clock at maxn=30 (21.6%->38.8% util).
2. **Merge Fan-Out Overhead** — merge was fanning out at map's granularity
   (320-way) for no reason; `--merge-mult 1` cuts fan-out to 80-way. 19%
   faster wall, 37% fewer CPU-seconds at maxn=30.
3. **GC Churn** — `GOGC=1000` (default 100 was firing ~26 GCs/sec against
   an 8MB heap goal for no reason; RAM was never remotely tight). 6.7%
   faster wall at maxn=30.
4. **Allocation Overhead** — the real root cause behind #3's symptom,
   found via a real heap-alloc profile (`POLY_MEMPROFILE`, gated
   diagnostic in `cmd/orchestrate/main.go`): `readIndexHeader` was
   allocating a full 4KB `bufio.Reader` just to decode a 19-byte header,
   at two call sites, 55% of a real run's total allocation. Fixed with a
   single `io.ReadFull` into a stack array. Also right-sized
   `ParseHeader`'s buffer. New fast local-iteration tool for this class of
   question: `orchestrator/sample_bench_test.go` (`go test -bench
   -benchmem`, ~0.5s vs a ~5min dalby round trip).
5. **Process-Per-Unit Spawn** — jasonp's standing, repeated point (not new
   from me): map/merge workers ran for a fraction of a second and paid
   real fork+exec cost every single time, thousands of times per run.
   `--persistent-workers` (new flag): a pool of long-lived `--persistent`
   map_worker/merge_worker processes fed via stdin instead of spawned
   fresh per unit (`orchestrator/workerpool.go` + the same feature in both
   worker CLIs). 6.2% faster wall, 7.7% fewer CPU-seconds at maxn=30, zero
   orphaned processes after normal exit or a real SIGTERM.

**Bottlenecks #1-#5 combined only bought 0.6% at real maxn=33 scale**
(6842.7s -> 6803.2s) — H17 (the dominant real-swept height) consumed
nearly the entire wall clock once it was the pool's sole occupant, and
none of those 5 touched that specific floor. Chased a sub-record
interrupt design (`forEachViableMask`/`viableRec`) that turned out to
target the wrong function entirely (that's the **column kernel**'s
enumeration, unused by production's `--kernel kink`; caught and corrected
same session, `results/sub-record-interrupt-design.md`). Real data then
showed the actual pattern: concurrency collapsed progressively across a
column's own kink-sweep stages (~43 active cores early, ~2.5 late, at
near-constant frontier size) — not a single pathological unit. A first
real fix attempt (`recordLess` lo-tiebreak, avoiding `combine()`'s
expensive left-extension path) was real but only bought 0.07% at scale.

**6. Kink-Stage Concurrency Collapse — the actual fix**: `--unit-mult 8`
(up from 4). Genuinely untested territory, not a dead-end retry — the one
prior "finer unit-mult rejected" memory finding was measured on the OLD
engine (pre-kink-carry), the same mistargeting class already caught once
this round. Real maxn=33 confirmation: **6798.6s -> 5674.2s (16.5%
faster), utilization 10.2%->12.4%** — the first real-scale utilization
GAIN this entire round, and the first fix that demonstrably moves H17's
dominant floor rather than only helping a secondary cost swallowed by it.
Best win of the session.

**Also found, separately flagged, NOT this session's fault, NOT fixed**:
a real, pre-existing correctness bug — real `SIGTERM` + `--resume` on the
kink kernel produces wrong `a(n)` values. Confirmed present identically
without any of this session's changes. `results/kink-resume-sigterm-bug.md`
has the full repro; `dalby_term.sh`'s `--resume` usage comment now warns
about it. **Do not trust a resumed kink-kernel run's output without
independently re-validating it** until this is fixed.

Full bottleneck-by-bottleneck log with every dead end (named, so none get
retried) and every real-dalby A/B: `docs/utilization-bottleneck-log.md`.

---

# HANDOFF — 2026-07-07

Frontier **a(34) = 515316838423862758858377704**, banked+validated, term chase
**parked**. **MERGED TO MASTER 2026-07-06** (master is the repo's public
face; kink-carry remains the working branch). Big tidy DONE — README.md is
the fork-and-reproduce entry point. Durable facts live in `MEMORY.md`,
`results/*.md`, `README.md`, and git history — this file is the live state.
GitHub repo RENAMED to `jhparkerb/polyplets` 2026-07-06; remotes updated
on all three hosts. Local dirs stay `~/src/polyominoes` until the running
jobs finish (their cwd lives there).

**No live jobs right now** — dalby and ayr both idle, all three machines'
working trees clean. Everything below is either fully landed or explicitly
parked with a reason, not silently stalled.

## Frontier / what's banked
- **a(1)…a(34)** all banked under `results/ns_a{n}/` (triangle, PROVENANCE,
  perheight, cost_profile). a(1)-a(20) match the b-file; a(21)-a(34) chain-match
  each prior term; ayr cross-ISA verify folded into a34 PROVENANCE.
- **Diagonal closed forms P_2…P_15 wired** (`orchestrator/sweep.go`
  diagCoeffTable, `diagonalStripValid` k≤15); deriver `scripts/derive_pk_fast.py`.
- **Symmetric counts (Hall of Mirrors, `cpp/sym/symtm.cpp`)** — all four types
  built, gated (`tests/gate_symtm.py`) and byte-matched to `runs/sym24/`:
  - **r90, r180, hmirror: n=34 banked** (gympie `runs/sym34/`;
    r180(34)=48710062997772, hmirror(34)=17385821908346).
  - **dmirror: n=32 banked** (`runs/sym32/dmirror.out`, D(32)=2156235549286;
    32-strip farm dalby+ayr complete 2026-07-05, prefix-matches sym24+sym28).
    Engine is the **Shrink Ray** compact-frontier rewrite (b358e39): flat
    sharded storage, ~1.6× RAM + ~2× speed vs the unordered_map frontier
    that OOMed dalby. Farm cost: dalby S=26..31 3.0M cpu-s / ayr S≤25
    1.7M cpu-s.
- **Related sequences: all five banked to full current reach**
  (`results/related-seqs-n32.md`): A030233 to n=34; the D-dependent four
  (A030222/34/35/194596) to n=32. n=33 for the four lands with the dalby
  run (T3, P_4-assisted — OEIS comment-only). Combiner
  `scripts/derive_related.py` via symdir `runs/sym32.derive/` (symlinks
  sym34 r90/r180/hmirror + sym32 dmirror); validates all 95 known OEIS
  terms, /4 and /8 divisibility asserts.
- **OEIS staging (2026-07-05)**: b-files `results/b*_upload.txt` for all six
  sequences (A006770+A030233 to a(33), the four D-dependent to n=32);
  a(34)/A030233(34) staged as *conjectured comments*, deliberately out of
  the b-files (no held-out P_16 check until a(35)). Entry files
  `oeis/A*.txt` updated with %C/%E, signatures normalized to full-date
  form. **Pre-submission checklist** (from jasonp's past editor threads) is
  in `oeis/README.md` — check every batch against it; signature dates must
  be set to the actual submission day. Submission is jasonp's.
- **dmirror diagonal quasi-polynomials** (`results/dmirror-diagonals.md`):
  d(S,S+k) is period-2 quasi-polynomial, degree k per parity class, leading
  S^k/k!, onset ≈2k+2. **P_0..P_4 pinned BOTH parities** (P_4-odd pinned by
  the completed n=32 farm's S=23 strip; P_4-even also cross-validated by two
  independent methods); **P_5 both parities fitted** via the cumulant/exp
  form (`scripts/dmirror_pk_exp.py`), now with 6 exact witnesses/parity —
  unchanged from the 4-witness fit (forward confirmation); level 6 refuses.
  GF-basis structure: G_k = N_k(x)/((1-x)^(k+1)(1+x)^k), N_k(±1) = (±2)^k
  for k≥1; G_k generates the polynomial law (raw counts agree in-regime
  only — paper wording fixed accordingly). No low-order bivariate closure.
  These formulas replace the RAM-impossible sparse strips: n=33 needs only
  P_4 (direct S≤28), n=34 only P_5 (direct S≤28).
- **Paper (`paper/polyplets-report.tex`)**: computational-report form,
  through five external review rounds + one big self-check round.
  Growth §3 upgraded to the confluent 3-param fit (Δ₁=1/2, λ≈7.111,
  θ→-1.02 emergent; `paper/lambda_fit.py`). GF bound recomputed beyond
  frontier (a(35)≥5.07e26, a(40)≥4.27e30; 16% capture at 34).
  **`paper/verify_claims.py` re-targeted at the full report — 397 checks
  GREEN** (parses tables from the .tex; caught + fixed 3 overclaims:
  G_k definition, residual-factor claim, N_k boundary k≥1). Restored
  91bdcdc-deleted data files it needs (results/fixed_height_gfs.txt etc.).
  Remaining TODO: n33-cost (job-gated).

## Jobs landed (2026-07-07 early morning; both started 2026-07-06)
- **dalby — M(17) max-hole-area sweep DONE 2026-07-07 04:27** (78-way
  split, wall 74,870s ≈ 20.8h, 4.928M cpu-s ≈ 1369 core-h). **Result:
  M(17)=28 — confirms Conjecture 1's prediction exactly** (fitted on
  n≤16, no forward test until this run). results/maxhole.txt pulled to
  the Mac (was stale at n≤16 locally, now synced through n=17). Paper
  updated (`paper/polyplets-report.tex`, the M(n) paragraph + Conjecture
  1 + open problem block): verified range n≤16→n≤17, next untested
  prediction is now M(18)=32 (exact, no rounding ambiguity).
- **ayr — dmirror n=33 cross-ISA recompute DONE 2026-07-07 03:34**
  (queue S=25,24,23,22,21,20 fully drained). **Cross-ISA byte-compare
  (ayr x86 vs dalby ARM): ALL SIX STRIPS MATCH** (S=25 matched earlier;
  S=24..20 matched this morning) — closes the "S≤25 compare pending"
  item in `results/related-seqs-n33.md`.
- ~~dalby n=33 direct strips~~ **DONE 2026-07-06 07:39** (24.0h wall,
  6.71M cpu-s, peak 126.2GB) — **completion drill EXECUTED**: strips on
  gympie runs/sym33/, all n<=32 prefixes byte-match n=32 farm (413/413);
  **D(33)=5475149862148** via fail-closed `scripts/dmirror_hybrid_sum.py`
  (closed forms reproduced 124 overlap cells before supplying 15 sparse
  cells); companions n=33 (T3) banked results/related-seqs-n33.md + staged
  as conjectured OEIS comments; **P_5-even conventionally PINNED** (equals
  exp fit; P_5-odd stays fitted, 7 witnesses; level 6 refuses); paper
  updated (D(33) ‡ cell, companions block, n=33 cost, dagger narrowed),
  verify_claims 398 GREEN.
- **n=34 dmirror: DECLINED 2026-07-06** (jasonp, at the close deadline).
  Measured n=33 peaks supersede the old ~90-160GB estimate: S=28@34 (k<=6)
  extrapolates to ~175-200GB and S=27@34 (k<=7) similar, vs dalby's 189GB
  incl. swap — marginal-to-infeasible, and P_6 (the formula escape) is
  unpinnable without n=34 data (circular). If ever revisited: probe
  S=28@34 alone first. The related-seqs reach is final at n=32 (T2) /
  n=33 (T3, comments); term chase for a(35)+ stays parked.

## Engine hot-path optimization (2026-07-07, branch `tm-hotpath-optim`)

Pushed to origin, NOT merged (jasonp's call whether/when). Two real,
gate+ASan-validated fixes on top of `kink-carry`'s `0fe41b4`:
1. `RunRecord.H`/`.keyLen`: `int`->`uint8_t` (bounded <=38, never lossy).
   `sizeof(RunRecord<W>)` 72->64 bytes, compiler-verified.
2. `succ.counts` in both hot paths (`map_shard_file`, `map_shard_stage_file`)
   now allocates from a `std::pmr::monotonic_buffer_resource` scoped to one
   spill epoch instead of the default allocator (map-profile.md's B2
   finding: 415.8M allocations counted in a34's swept portion, ~14% of map
   cycles predicted).

**Measured, not assumed:** on gympie (macOS/clang) fix 2 was a small
*regression* (~2-3% slower, likely `polymorphic_allocator`'s virtual-
dispatch overhead beating macOS's already-fast small-object allocator).
On **dalby** (Linux/ARM/g++, the actual production target) combined
fixes 1+2 gave a real, reproducible **4.47% speedup** (2 reps each,
n=28, `baseline_times=[259.9,260]` vs `fixed_times=[248.65,249]`).
Environment mattered more than the fix itself.

**Reach extrapolation** (a34's real 3.70h/80-core baseline, 4.4x/term
growth, applying the measured 4.47%): **a(36) fits in a week, a(37)
does not, on every configuration** (dalby-alone or full 122-core fleet,
optimized or not) -- 1.9-3.0 days for a(36) either way, 8.2-13.1 days
for a(37) either way. The optimization shifts wall time by a few hours
per row, never crosses the a(36)/a(37) boundary. An earlier version of
this table had an off-by-one loop bug that mislabeled a(37) as
reachable at 45.0h (that was actually a(36)'s wall) -- corrected, this
version is right.

A scary-looking multi-minute hang on gympie during gate-suite
re-validation turned out to be **not a bug**: driver1's `--ram 1MB`
forced-constant-spilling test legitimately takes ~4.5 minutes under
system contention (XProtect was pegging two cores at the time), not an
infinite loop. Confirmed by running the identical gate suite + ASan on
idle dalby: all gates PASS clean, including `gate_spill` and
`ns-gate-asan` on both kernels. Lesson: an unexplained slowdown on a
loaded/contended dev machine isn't automatically a code defect --
cross-check on the actual clean target environment before concluding
there's a bug.

**Terminal-sort investigation: fully closed, not abandoned.** The
codebase's own `map-profile.md` flags the terminal `sortRun` as the
next-biggest cost (~19-39% of hot-column wall) after the alloc fix.
Three genuinely different attacks were tested against REAL captured
signature data (dumped via a temporary, since-reverted debug hook) and
all three came back measured-negative, not just "seemed hard":
- **Radix bucket by leading signature byte**: real data shows severe
  skew (only 2/256 buckets ever populated) -- signature bytes are a
  restricted growth string (RGS) encoding of a partition, which has a
  hard mathematical bound (byte[i] <= 1+max(byte[0..i))), verified
  against ~5M real records (1 violation, parse-boundary noise). This
  isn't an implementation quirk, it's inherent to RGS; reordering which
  cell maps to which byte position does not help.
- **Recursive (multi-level) radix bucketing**, jasonp's suggestion to
  exploit the skew via recursion: measured at depths 1-4, total cost
  (sort-cost + partition-pass cost) stays flat at 99.9-100.9% of plain
  sort. Sort-cost alone does shrink as predicted, but partition-pass
  cost grows right alongside it and eats the saving.
- **Hash-bucket for balance + k-way merge** (near-perfect balance,
  stddev 7,629 vs 140k-197k for raw bytes): PROVEN algebraically, not
  just measured, to never beat plain comparison sort -- N*log2(N/K) +
  N*log2(K) = N*log2(N) exactly, independent of K, so bucketing can
  only match plain sort minus the extra O(N) routing-pass overhead.
  General fact, not specific to this encoding: bucketing can't beat the
  N log N comparison-sort floor unless key width is genuinely bounded
  independent of N, which ours isn't (needs ~log(N) bits to distinguish
  N growing frontier states).
- **Generation-order "nearly sorted" hypothesis** (successors might
  arrive close to sorted, making an adaptive sort cheap): measured on
  real data, 1.84M ascending runs out of ~5M records, mean run length
  2.71 -- barely above the ~2.0 expected for a PURE RANDOM permutation.
  Real but weak structure, ~6.5% theoretical ceiling before accounting
  for the overhead of tracking 1.84M run boundaries.

**Net: nothing left on the terminal-sort lever that survives contact
with real numbers.** If revisited, the honest starting point is that
all four natural attacks are closed, not unexplored -- a fifth idea
would need to be a genuinely different shape, not a variant of these.

## Data ceiling (why the term chase is parked)
- **P_16 is derivable** (fit from T(33,17)+T(34,18), self-consistent) but has
  **no independent holdout** until a(35); a(34)'s top cell has no closed-form
  cross-check. More terms need a fresh sweep — not planned pre-close.
- **Transfer-matrix Option 5** (`scripts/diag_transfer_gen.py`) infeasible:
  state count ~7.4×/k. Dead end without a rewritten engine.

## Open independent threads
- **Lean proof** (branch `lean-diagonal-proofs`, `polyplets/PROOF-STATUS.md`):
  (a) finiteness, (b) row profile, (c-fwd), (d-local) done+green; remain
  (c-rev), (d-global gap≤2), (e) offset-chain count.
- **Steal-tail diagnostic** (`results/steal-tail-h18.md`): banked, not
  deployed (trusted config).

## OEIS submission readiness (supersedes the hard 2026-07-06 date)
Batch is staged and checklist-clean, but **submission is now gated on
jasonp's own readiness process, at his insistence** — the OEIS AI policy
makes the author personally responsible for correctness, and editors now
routinely ask "how much of this is AI-generated?". Research on the policy
+ accepted/rejected precedents: `docs/oeis-ai-policy.md`.
- **The viva** (local-only files, deliberately uncommitted, in
  .git/info/exclude: docs/viva-exam.md, viva-reserve.md [chmod 000],
  viva-state.md, drill1-counting.md, drill2-tiers.md): exam taken
  2026-07-05, 56.5/100 vs bar (>=80, no core question below half).
  **Drill 1 (counting arguments) DONE 2026-07-06** — all of A1/A2/B1/B2/
  C1/C2 closed. **Drill 2 (tiers + validation) graded 2026-07-06/07** —
  D1 tier definitions done (one contested point resolved, jasonp's
  answer stands); E1 shared-logic mitigations strong but missing the
  held-out P_k item; F1 mod-p mechanism correct but doesn't name the
  reimplementation as the closing answer. Cold retake variants still
  pending after a spacing gap. **Full grading state: docs/viva-state.md**
  (local).
- Before submitting, also: jasonp rewrites all staged %C lines in his own
  words (Claude meaning-checks only); signature dates -> actual
  submission day; pink-box replies are jasonp's alone, always.

## Remaining work ledger
1. ~~Housekeeping~~ DONE 2026-07-06 (the big tidy: process docs, one-shot
   scripts, experiments/, stale drafts, autonomy/, polyplets/ removed;
   README.md replaces ROADMAP.md as the repo face).
2. ~~M(17) on dalby~~ DONE 2026-07-07 04:27 — M(17)=28 confirmed, paper
   Conjecture-1 note + maxhole.txt updated (see "Jobs landed" above).
3. ~~Engine hot-path optimization pass~~ DONE 2026-07-07 — branch
   `tm-hotpath-optim` pushed, validated (dalby gates+ASan clean), real
   4.47% win measured, reach ceiling confirmed unchanged (a36 yes/a37
   no either way). NOT merged -- jasonp's call. Terminal-sort lever
   fully investigated and closed (see section above); nothing else
   queued there.
4. Paper: final read-through after the tidy passes.
5. Viva: cold retakes (V8/V12/V13 drill-1-flavor, V18/V19/V20 drill-2-
   flavor per docs/viva-state.md), then %C authorship pass (jasonp's own
   words), then jasonp submits.
6. **Lessons-learned document** (jasonp + Claude collaboration) — after
   compute and paper are done, BEFORE submitting. jasonp's explicit ask
   2026-07-06.

## Starting a fresh session from here
Read this file first, then `MEMORY.md`'s index (auto-loaded) for standing
practices. The two active branches: `kink-carry` (general work, docs,
paper, results -- this file lives here) and `tm-hotpath-optim` (engine
optimization, pushed, unmerged, nothing pending on it). No open threads
need immediate action; next steps are entirely jasonp's pacing (viva
retakes, whether/when to merge the optimization branch, whether to revisit
a35+ compute at all given the reach ceiling above).
