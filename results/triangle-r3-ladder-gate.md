# Ladder gate prep (ADV-1) — the measured rows exist, and they change the plan

2026-08-12, wave-5 scout on queue row ADV-1 and phase-2 gate work for L6-1,
per `docs/r3-job-dispatch.md`. Everything below is reading, git, and READ-ONLY
ssh; the one local script run was a seconds-scale banked-triangle share
computation (`experiments/tristruct/triangle.py`, foreground).

## 1. The dalby B1 calibration run COMPLETED, and nobody had looked

**Established: the branch's calibration run finished cleanly on 2026-08-11
at 16:02 EDT, covering H = 1..16 at n <= 40, with 640/640 banked-cell
matches and 0 mismatches.** Both L6's and the independence adversary's
NOT ESTABLISHED item is closed in the direction everyone hoped.

What was searched, in order:

- This branch: no `results/cutcount_b1*` anywhere (`ls`, `git ls-tree`).
- `second-source` branch: `git ls-tree second-source results/` has no
  cutcount_b1 artifacts — deliberate; `git show second-source:HANDOFF.md`
  says "per-height rows land on dalby only (gathered here when the run
  finishes)" and records the run live at H=15 on 2026-08-11 10:45 EDT.
- `git show second-source:scripts/run_cutcount_b1_calib.sh`: output goes to
  `results/cutcount_b1/{calib_run.log,rows/C<H>.out}` on dalby.
- dalby (read-only ssh): `~/src/polyominoes/results/cutcount_b1/` holds
  `calib_run.log` (21,510 B, last write Aug 11 16:02),
  `calib_run.attempt1.log` (a false start at 09:18, superseded at 09:23),
  and `rows/C1.out .. C16.out`, all present and non-empty.

### The verdict lines (from `calib_run.log`, quoted)

    selfcheck H=16: q0_zero=OK q1eval_binomial=OK (n=1..40)   [and likewise H=1..15]
    event=done ... mode=assemble match=640 mismatch=0
    H=15: 40 match, 0 mismatch
    H=16: 40 match, 0 mismatch
    vs banked triangle: 640 match, 0 MISMATCH
    === done 2026-08-11T20:02:26Z

### The measured walls and RSS (dalby, 1 thread, exact I256 payload)

| H | windows (exact census) | wall s | peak RSS MiB | bytes/window |
|---|---|---|---|---|
| 12 | 107,241 | 158.5 | 835.5 | 8,169 |
| 13 | 306,858 | 503.4 | 2,393.4 | 8,179 |
| 14 | 891,074 | 1,618.6 | 6,924.6 | 8,149 |
| 15 | 2,624,197 | 5,134.5 | 20,382.8 | 8,144 |
| 16 | 7,832,667 | 16,475.2 | 60,827.4 | 8,143 |

Wall ratio per height: 3.21 / 3.17 / 3.21 (H=13→16). The census column is
the adversary's exact closed form; the run's own `states=` heartbeat values
match it at H=15 (2,624,197) and H=16 (7,832,667) exactly.

**Marginal bytes/window (H=15→16 slope): 8,142 B — flat, and measured.**
The model payload for this binary is 41 slots x 3 coeffs x 32 B x 2 buffers
= 7,872 B + 22 B key = 7,894 B. So the real container's overhead beyond the
raw payload arrays is **~250–270 B/window, stable across H=12..16**. That
is the first real RSS this DP family has ever had against its model, and
the model's payload accounting is confirmed to ~3% — but the overhead term
the residue model books at 22 B is actually ~270 B in this container.

### What the completed run banks, once gathered

- **T(n,15) and T(n,16) for all n <= 40 — including T(40,15) and T(40,16) —
  are now two-source by the cancellation rule, exactly, not mod p.**
  Computed from the banked triangle this session: H=15 is 11.23% and H=16
  is 10.41% of a(40) — **21.64% of a(40) already recounted exactly** by a
  rule that never decides connectivity. The synthesis's "largest unconfirmed
  block, 43.84% (H=15..19)" is stale: the remaining unconfirmed block is
  **H=17..19 = 22.20%**, plus H=20 (4.16%) and H=21 (2.84%).
- The four kink-only Grand anchors T(28,15), T(29,15), T(30,16), T(31,16)
  flip to two-source (the branch HANDOFF's stated purpose for the run).
- Provenance caveat, recorded: the rows were produced by source sha256
  `59e90660b42a0d94` (echoed in the log header), which is **dalby's
  untracked working copy of `cpp/cutcount_b1.cpp`** (sha verified identical
  over ssh) — it matches neither committed version of the engine
  (48ac108: `5ab04877...`, 7b13137: `017e639d...`; the committed one adds
  fail-closed exit codes after launch, per the script's own provenance
  note). The per-height match/mismatch lines are in the log regardless of
  exit-code behavior. Banking the working source file alongside the rows
  (PROV-2's motion) closes this.
- Collateral for ADV-4 (archived-state replay): `runs/ns_a40/dalby/`
  survives on dalby with `run.log`, `h20.out.zero-harvest-bug`, and many
  `merge_h20_c7_k5_r*.bin(+.idx)` shard files — the replay idea has
  material to work with. Listed only; not this row's job.

## 2. The bytes-per-window measurement, specified

The go/no-go constant is now half-measured: **the exact-payload binary's
overhead is ~270 B/window in its current hash container.** If a residue
binary reuses that container, its constant is ~82 + 270 = **~350 B/window,
not 104** — H=20 would be 703.5M x 350 B = **~230 GiB: fails ayr AND
dalby**, and even H=19 (~74 GiB) would just barely fit ayr sole-tenant.
If phase 2 uses a flat double-buffered array (key ~16 B + payload 82 B,
no per-node allocation), ~100 B/window is realistic and H=20 fits dalby
comfortably. **The container choice, not allocator noise, is the
go/no-go variable — the measurement must be of the residue binary with its
production container.**

How to take it:

- **Binary:** the residue-payload variant of `cpp/cutcount_b1.cpp`
  (branch `second-source`): coefficient arrays change from 3 x u256 wrapping
  to 2 x u8 mod p (drop the third self-check coefficient or carry it mod a
  63-bit prime as the branch specified); everything else — stencil,
  transitions, canonicalization, self-checks, `--assemble` compare —
  unchanged. This ~20-line variant is a phase-2 artifact; authoring it is
  the dispatch prerequisite (this round does not build).
- **Heights:** H = 12, 13, 14, 15 in one run (residue RAM <= ~1 GiB even at
  the pessimistic constant; wall bounded above by the measured exact-payload
  H<=15 total of ~2.1 h single-thread dalby, and byte arithmetic should be
  several-fold cheaper).
- **Attribution:** the engine's own `event=done ... peak_rss_mb=` per
  height (same obs format as the calib log), cross-checked with
  `/usr/bin/time -v`. Report **marginal slope** between consecutive
  heights — (RSS_H2 − RSS_H1)/(windows_H2 − windows_H1) — which cancels
  fixed overhead (code, census tables, banked rows); windows come from the
  binary's `states=` line (= the exact closed form).
- **Confounds:** (i) hash-table load factor / rehash doubling — three
  pairwise slopes across four heights expose a rehash discontinuity; if
  slopes disagree > 15%, take the max and label it; (ii) allocator slack —
  single-threaded run, marginal slope already nets most of it out; (iii)
  buffer doubling — peak RSS deliberately includes both buffers, because
  that is the deployed shape; do not subtract it.
- **Decisive vs noisy:** slope <= ~113 B → H=20 possible on ayr sole-tenant;
  113–175 B → H=20 is a dalby job only; > 175 B → H=20 out of RAM
  everywhere (out-of-core or dropped). Model says 104; same-container says
  ~350; the measurement separates these by 3x, so any stable answer is
  decisive. Noisy only if the pairwise slopes disagree > 15% after a rerun.
- **Correctness guard riding along:** `--assemble` H<=10 against the banked
  triangle (400 cells, seconds) must be green, per prime, before the RSS
  numbers are believed. Also measures **us/slot-col of the residue payload**
  from the same log lines, replacing the 0.94 us model number.

Runner script (written, readable, not run):
`experiments/tristruct/r3_ladder_bpw_probe.sh`.

### JOB REQUEST (filed in the queue as LG-JOB-1)

    job id:            LG-JOB-1
    measures:          bytes/window (marginal RSS slope) and us/slot-col of the
                       residue-payload cutcount_b1 at H=12..15, one 8-bit prime
    decides:           H=20 routing: <=113 B/window -> ayr sole-tenant possible;
                       113-175 -> dalby only; >175 -> H=20 residue out of RAM
                       everywhere (out-of-core or INV-8 only). Also replaces the
                       0.94 us/slot-col wall model with a measured constant,
                       repricing the whole H=17..19 ladder.
    command:           bash experiments/tristruct/r3_ladder_bpw_probe.sh <residue-binary> \
                         (prerequisite: ~20-line payload variant of
                         second-source:cpp/cutcount_b1.cpp, built on the target box;
                         authoring it is the lead's/jasonp's phase-2-gate call)
    script:            experiments/tristruct/r3_ladder_bpw_probe.sh (written this row)
    wall estimate:     <= 2.1 h single-thread — MEASURED upper bound (the exact-payload
                       binary's H<=15 total on dalby, calib_run.log); expected ~4x less
    RAM estimate:      <= 1.5 GiB — MEASURED anchor (exact payload H<=15 = 20 GiB,
                       residue payload is 1/80th the slot bytes; even the pessimistic
                       350 B/window at H=15 is 0.9 GiB)
    disk estimate:     ~1 MB (per-height row files + log)
    cores:             1
    interruptible:     yes — per-height rows, kill costs at most one height
    RED control:       --assemble H<=10 vs banked (400 cells) must be green per prime
                       (committed engine exits nonzero on mismatch or zero-cell
                       compare); [q^0]=0 and q=1 binomial self-checks logged per height
    closes:            the synthesis's go/no-go NOT ESTABLISHED (104 B/window model
                       vs real RSS); ADV-1's remaining half (its other half — measured
                       walls at H=15/16 — is closed by §1 above at zero cost)

## 3. Phase-2 plan, re-shaped against the real machines

Machine facts, checked this session (read-only): **ayr 78 GB, 32 cores,
idle — 77 GB available, load 0.03. dalby 125 GB, 80 cores, 121 GB
available, 564 GB free NVMe on /; only sshd-scale processes running.**
The synthesis was written assuming ayr was the only box; dalby is both
bigger-RAM and 2.5x the cores, and it is where the engine, the rows, and
the a(40) artifacts already live.

Per height, using the exact censuses (adversary §6) and the run's measured
walls as upper anchors (exact-payload cost; residue is cheaper):

| H | share of a(40) | status / RAM (model 104 B — pessimistic ~350 B) | box | wall anchor |
|---|---|---|---|---|
| 15 | 11.23% | **DONE, exact** — 2026-08-11, 640-cell match | dalby (done) | measured 1.43 h |
| 16 | 10.41% | **DONE, exact** — same run | dalby (done) | measured 4.58 h |
| 17 | 9.06% | 2.3 GiB — 7.8 GiB | ayr | <= 14.7 h/thread/prime (x3.2 from measured H=16) |
| 18 | 7.42% | 7.0 GiB — 24 GiB | ayr | <= 47 h/thread/prime |
| 19 | 5.72% | 21.7 GiB — 74 GiB | ayr (worst case sole-tenant) | <= 150 h/thread/prime |
| 20 | 4.16% | 68.1 GiB — 230 GiB | **dalby, gated on LG-JOB-1 <= 175 B** | <= 480 h/thread/prime |
| 21 | 2.84% | 215.8 GiB — 733 GiB | no box in RAM; dalby out-of-core or INV-8 | <= 1,540 h/thread/prime |

Recommended shape:

- **Piece 0 (free): gather and bank the completed H<=16 run.** Rows + both
  logs + the sha-identified working source from dalby into the repo;
  update provenance per the branch HANDOFF's step list. 21.64% of a(40)
  recounted exactly, four Grand anchors two-sourced, zero compute.
- **Piece 1: H=17..18 exact, no CRT.** Two 61-bit-prime runs each
  (2 x 61 = 122 bits > log2 T(40,15) = 102.33, so two runs reconstruct
  exact values; 63-bit RAM: H=17 15.0 GiB, H=18 45.8 GiB model). Both fit
  ayr; H=18 worst-case container overhead pushes ~2.4x — then run it on
  dalby instead. Avoids 14-run stacking entirely at these heights.
- **Piece 2: H=19 residue ladder** — 14 x 8-bit primes (or **7 x 16-bit
  primes**, payload 164 B + overhead: ~39 GiB at model — halves the run
  count at the same per-run wall; phase 2 picks after LG-JOB-1 measures
  the container) on ayr, 21.7–74 GiB per run, one to three concurrent
  runs depending on the measured constant. Exact values by CRT with a
  held-out-prime RED.
- **Piece 3: H=20 on dalby** (not ayr): 68.1 GiB against 121 GiB available
  is a comfortable job at the model constant and survives up to
  ~175 B/window — a threshold 50% softer than ayr's 113. 80 cores against
  a <= 480 thread-hour worst-case wall per prime, if state-sharding
  parallelizes as the project's stock machinery assumes (ASSERTED, per the
  cost adversary — unchanged).
- **H=21: still off-RAM everywhere** (215.8 GiB minimum). Out-of-core on
  dalby: 564 GB free today covers the 8-bit working set (~216 GiB
  double-buffered) plus staging *at the model constant only* — the
  pessimistic container constant (733 GiB) exceeds free disk, so H=21
  out-of-core is **conditional on LG-JOB-1 too**. Otherwise INV-8's spin
  basis (0.3 GiB, mod 2) remains the only H=21 reach.
- Wall totals, honest range: the 0.94 us/slot-col model gives ~61
  thread-hours per prime for H=17..19; the measured exact-payload walls
  bound it at ~210. Note the wall model also disagrees with the run's
  column count (the adversary priced 41−H columns; the calib binary runs
  41 columns per height — visible in its own heartbeats), so quote walls
  against the measured anchor until LG-JOB-1 lands.

## 4. The phase-2 gate, with an asymmetric RED

Carried requirement (queue rows ADV-1 gate-fact, L4-13 caveat): the DP's
structural self-checks ([q^0]=0, A_n(1)=binomial) are measured blind to
stencil errors, and state censuses are blind to *symmetric* stencil errors
(rook and king closures reach identical state sets at every measured
H <= 8). So the gate battery is the only instrument that sees the stencil,
and it must contain a RED the censuses and identities both miss.

Per built binary, per machine, per payload variant, before any production
column (fail-closed: the gate script exits nonzero unless every GREEN
passes and every RED fails; the production runner refuses to start without
a gate receipt naming the binary's sha256):

- **GREEN-1, brute battery:** [q^1] against an independent brute-force BFS
  enumeration (`r3_adv_state_iso.py` Part 1 machinery or L6's probe) at
  (H,W) in {(2,4), (3,3), (3,4), (4,3), (5,3), (6,2)}, every n, per prime.
- **GREEN-2, banked compare:** `--assemble` H<=10, 400 cells (seconds).
- **GREEN-3, identities:** [q^0]=0 and q=1 binomial per height, logged.
- **RED-A, the asymmetric one:** stencil mutant dropping only the NW
  neighbour (cross-cut stencil {r−1, r}), compile-flagged from the same
  source. Measured fact this gate encodes: this mutant **passes GREEN-3
  and the state census** while [q^1] is wrong at n = 2..10. It must be
  caught by GREEN-1, at every probe box, or the gate is broken.
- **RED-B, the symmetric one:** rook-stencil mutant (both diagonals
  dropped) — the error class censuses provably cannot see. Caught by
  GREEN-1/GREEN-2.
- **RED-C, weight:** fresh-class weight corrupted (q−b → q−b+1) — must
  trip [q^0] != 0 and the engine must exit nonzero (exercises the
  fail-closed path the committed engine added).
- **RED-D, CRT:** reconstruct from k−1 primes, predict the held-out k-th
  residue (independence adversary's control). Applies to the exact-value
  assembly step, not per binary.

A phase-2 brief can lift this section verbatim.

## 5. Queue rows filed

LG-JOB-1 (the job request above), LG-1 (bank the dalby run),
LG-2 (container overhead is the go/no-go variable), LG-3 (7 x 16-bit-prime
option), LG-4 (H=17/18 exact via paired 61-bit primes), LG-5 (stale-share
correction: remaining block is H=17..19 = 22.20%). Appended to
`results/triangle-r3-queue.md`.

## NOT ESTABLISHED

- The residue binary's actual bytes/window and us/slot-col — LG-JOB-1's
  whole point; everything in §3 marked "model"/"pessimistic" turns on it.
- Whether state-sharded parallelism holds for this DP (still ASSERTED,
  nobody has run it multi-core).
- Whether dalby's 564 GB free persists to phase-2 time (checked 2026-08-12
  only), and the out-of-core wall at H=21 (unpriced entirely).
- The exact-height second-difference assembly rows at H−2 for band
  coverage (cheap, but not re-derived here).
