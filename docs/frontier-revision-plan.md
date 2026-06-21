# Frontier revision plan — extend a(n) reach via the memory stack (+ FLM gate)

> **Status (2026-06-21): a PLAN, not a results log.** The *what/why* of each
> compression lever lives in `state-store-compression.md` (design + decision record);
> this file is the *how/when/verify/deploy* — phases, file-level tasks, and the
> testing/benchmarking/deployment discipline. Update the per-task checkboxes as work
> lands; trust the status tags, not the projected term counts.

## Goal & non-goals

**Goal:** push the primary sequence A006770 by **~+1.3 terms of effective reach** —
concretely, make **a(22) cross-ISA *confirmable*** (shrink it under ayr's 78 GB so an
x86 run is possible, not just dalby-computable) and **a(23) computable** on dalby —
*and* relieve the memory-stall speed wall (the dalby finding: smaller working set ⇒
more usable cores ⇒ faster). The holes engine, which is 2D and more RAM-hungry, gets
the same treatment and benefits more.

**Non-goals (ruled out this session, with reasons):**
- **GPU** — gympie's 24 GB caps it below the a(21) frontier regardless of CPU/GPU;
  unified memory is favorable but the data won't reside. No big-memory card available.
- **Compact non-crossing (Motzkin) signature encoding** — polyplet (square-8) boundary
  partitions genuinely *cross* (`signature.h` line 9–13), so the Motzkin trick is a
  square-4 win, not ours; and the `Sig` is only ~15% of per-state RAM anyway.
- **Recurrence-guessing / exact solution** — a(n) is conjectured not D-finite; no leap.

**Hard invariant:** every engine change is **byte-identical** to the dense baseline,
proven by the gate, on every path (serial, MT, checkpoint, reserve). A compression
that changes a single count is a defect, not a tradeoff.

## Foundation already in place (do not redo)

- `--reserve` pre-sizing (B5) and load-factor 0.85 (A3) — **landed, gate-green.**
- `FlatDB`/`HoleDB` expose the whole store behind `slot()` / `for_each()` /
  `addCounts()` — `statedb.h` is explicitly "the designed-to-be-replaced component."
  All compression drops in **behind those three calls**; call sites don't change.
- The mod-p sweep machinery exists (`--modp`, `sweep8_holes.h`) for the GFs — Phase 2
  reuses it for exact a(n).
- `gate_tma.py` checks A–L are all byte-identical comparisons; new levers add checks
  in the same shape (the reserve check K and checkpoint check J are the templates).

---

## Phase 0 — Gate the investment + clean the tree (cheap, do first)

0.1 **FLM scaling back-of-envelope (GO/NO-GO for the whole approach's *scaling*).**
   The memory stack is all constant-factor (shifts the ×2.42/term curve down ~1 term,
   doesn't bend it). The finite-lattice (width-bounded boundary) decomposition is the
   only candidate that could change the *scaling*. Before sinking weeks into packing,
   spend an afternoon: estimate the width-bounded boundary-state growth vs our
   height-bounded diagonal over n=19..24 (from the same `peak_states`-by-height data
   in `reach.md` plus a quick width-bounded state count at small n). **If FLM bends the
   curve, it dominates and reorders everything; if not, rule it out and proceed.**
   *Deliverable:* a paragraph appended to `reach.md` with the verdict + the numbers.

0.2 **`--profile-rows` measurement (sizes the ranged row — Phase 1's input).**
   Add an opt-in flag that, in `for_each` at the peak layer, histograms the live
   count-row width `hi-lo+1` weighted by state (does **not** alter counts). Run
   `tma square8 16 --only-height 16 --profile-rows` (fits a core or two; the
   distribution is N-stable). Expected: mean width ≪ maxn ⇒ ranged row ≈
   (maxn / mean-width)× on `vals`. *Gates Phase 1's expected payoff.*

0.3 **Commit the in-flight uncommitted work** so engine surgery starts from a clean
   tree: the Makefile `-Wno-error=restrict` fix, `dalby_holes_perheight.sh`,
   `a20_remaining_parallel.sh`, `NEXT.md`, the RESULTS/ROADMAP edits, results files.
   One commit per logical change; gate-green.

0.4 **Formalize the per-height parallel driver.** We built ad-hoc dalby/ayr drivers
   this session; fold them into one parameterized `scripts/perheight.sh N ENGINE
   [MAXJOBS] [THREADS]` (plain a(n) *or* holes), RAM-budgeted, checkpointed, pidfile
   for the waiter. This is the deployment vehicle for every Phase 1–4 production run,
   so it should exist and be gate-touched before the big runs.

**Phase 0 testing:** `make gates` stays green (0.2/0.4 add no counting logic; 0.3 is
commits only). **Benchmarking:** 0.1 + 0.2 ARE the benchmarks. **Deployment:** runs on
a spare gympie core; does not touch the in-flight a(20)/holes jobs.

---

## Phase 1 — Ranged counts row (the keystone byte win, ×1.5–2.5 on the 85%)

1.1 **`statedb.h`: variable-width rows behind the interface.** Store each state's row
   as `(lo, len)` + a `len`-wide slice instead of dense `[0…maxn]`. Two viable layouts;
   pick from the 0.2 histogram:
   - *(a)* a side `lo[]`/`len[]` per slot with rows packed in a bump-allocated arena
     (best memory, more bookkeeping), or
   - *(b)* keep the flat `vals` but with a per-run *narrowed* uniform stride if the
     histogram shows width is tightly peaked (simpler, smaller win).
   `slot()`/`for_each()`/`addCounts()` keep their signatures; `minSizeRow` already
   finds `lo`.
1.2 **Holes 2D-sparse variant** (`sweep8_holes.h`): the `(size,#holes)` table is an
   upper-triangular wedge (size ≥ s, holes ≲ s) — range *both* axes or store the
   per-state wedge. Bigger win than the a(n) path; this is where exact n=18/19 and the
   mod-p GFs reclaim RAM.

**Testing (new gate checks, same shape as K):**
- `M ranged   square8 n≤11  ranged-row == dense` (plain).
- `M' ranged-holes square8 n≤11  ranged == dense` (holes 2D wedge).
- Extend the existing MT (I), checkpoint (J), reserve (K) checks to run *with* ranged
  rows on → ranged must be byte-identical under all of them, incl. the checkpoint
  serialize/reload (the ckpt format gains the `(lo,len)` per row — versioned, with a
  meta-guard bump in `checkpoint.h`).
- ASan: a `*_asan` ranged build, n≤8, clean + equal (checks C/F shape).
- External anchor unchanged: totals vs A006770 n≤18 (D), hole oracle n≤14 (H).

**Benchmarking:** the calibration matrix — fixed case `square8 18 --only-height 17`
(heavy but bounded) measured before/after for **peak RSS, wall time, cores-used**
(memory-stall proxy), **bytes/state**. Target: ranged matches the 0.2 projection on
`vals`, and the a(22) heaviest stratum lands **< 78 GB** (the confirmability gate).

**Deployment:** lands on whichever big box is free first; re-benchmark a(18) end-to-end
to validate, then this is the build used for the a(22) confirmable run.

---

## Phase 2 — u32 mod-p counts + exact a(n) via CRT (helps holes/GF + unlocks confirm)

2.1 **Template the counts type** (`u64` exact / `u32` mod-p) so the mod-p path stores
   4-byte rows — clean ×2 on the (already-ranged) row for every hole/GF run.
2.2 **Exact a(n) by mod-p + CRT.** Run the a(n) diagonal mod several primes < 2³¹ with
   u32 ranged rows, CRT the final `byHeight[H][n]`. This is what makes **a(22)
   confirmable** without u64-wide rows — and it reuses the existing `--modp` sweep,
   so the new code is the CRT-assembly + the driver, not a new engine.

**Testing:** `N modp-crt square8 n≤14  CRT(exact a(n)) == dense u64` (byte-identical
final counts). u32 row overflow guard (counts < p enforced). Holes mod-p path unchanged
result, smaller RAM. **Benchmarking:** RAM per prime (should ≈ half the ranged u64
row); total time = k× sweeps but each lighter + better core-use (CRT is cheap).
**Deployment:** the confirmable-a(22) recipe = ranged + u32-modp + CRT across ~k primes
on ayr (x86) *and* dalby (ARM) → cross-ISA confirm.

---

## Phase 3 — Structural bets (higher ceiling, higher risk — gate hardest)

3.1 **Vertical-flip symmetry fold (~2× on the state COUNT; cited Barequet &
   Ben-Shachar 2024 §4.2, Jensen 2003).** Merge mirror-image signatures. **Parity
   wrinkle:** per-column signature merge for odd-height strips; mirror-box pairing for
   even. **Correctness-critical** (self-symmetric signatures counted once, mirror pairs
   doubled) — the single most error-prone change here.
3.2 **Chunked/blocked store (~2× off the double-buffer; *and* the out-of-core seam).**
   Replace the one flat array with fixed-size blocks so `db` drains block-by-block into
   `next` — peak ~1×+overhead instead of 2×. This blocked, hash-partitioned structure
   IS the precursor to Phase 4, so it's not a detour.

**Testing:** `O symfold square8 n≤12 == plain` (both parities exercised: odd and even
maxn, since the fold differs); `P chunked square8 n≤12 == plain` (+ MT/checkpoint/
reserve cross-products). Symmetry fold gets the **widest** n-range gate we can afford
(it's the riskiest) and an explicit self-symmetric-signature unit test. **Benchmarking:**
peak RSS (expect ~2× each), and confirm they *stack* with Phase 1/2 (count× and bytes×
multiply). **Deployment:** these are what push **a(23)** (~95–110 GB after ranged)
toward fitting dalby — land them only when a(23) is the target.

---

## Phase 4 — Out-of-core backend (a(24)+, deferred until it's the goal)

External **hash-partitioned aggregation** (not mmap): emit `(successor-sig, row)`,
partition by `hash(sig)` into K RAM-sized buckets, aggregate bucket-by-bucket
(sequential I/O). The Phase 3.2 blocked store is the in-RAM half of this. **Testing:**
`Q out-of-core square8 n≤12 == in-RAM`, and a forced-small-bucket run (env knob) so the
spill path is exercised at tractable n. **Benchmarking:** disk I/O vs RAM crossover; the
new wall is wall-clock (×2.42/term). **Deployment:** dalby (376 GB free on `/`); only
when a(24) is wanted — at which point *time*, not RAM, is the ceiling.

---

## Cross-cutting: TESTING plan

- **Byte-identical is the contract.** Every lever adds a `<compressed> == <dense>` gate
  check in the shape of K, across the full path matrix: **serial · MT(--threads) ·
  checkpoint(write+resume) · reserve**. A lever isn't "done" until it's byte-identical
  under *all four*.
- **External truth anchors never move:** totals vs A006770 n≤18 (gate D), the confirmed
  a(19), the flood hole-oracle n≤14 (gate H), square-poly/polyhex b-file prefixes.
- **Checkpoint format is versioned per lever** (`checkpoint.h` meta-guard bump) so a
  resume across a format change refuses rather than corrupts — and gate L resumes the
  *new* format.
- **Sanitizers** (`*_asan`, address+UB) on each new path at small n; the gcc-12
  `-Wno-error=restrict` scoping stays.
- **Run `make gates` after every commit;** no lever merges on red.

## Cross-cutting: BENCHMARKING plan

- **One calibration case, measured before/after every lever:** `square8 18
  --only-height 17` — heavy enough to be representative, bounded enough to fit any box.
  Record **peak RSS, wall_s, cores-used (memory-stall proxy), bytes/state** (the obs
  `done` event already emits peak_rss; add a states/bytes line).
- **Validate projections, don't trust them:** ranged row must hit the 0.2 histogram
  factor; the a(22) heaviest stratum must measure **< 78 GB** before we call it
  confirmable; each structural bet must show its ~2× *and* that they stack.
- **Re-fit `reach.md` as data arrives:** a(21) (landing now) makes the ×2.42 a 3-point
  fit; re-run the whole ladder after Phase 1 and again after Phase 3. The
  cores-used/memory-stall curve from the dalby work becomes a second model (speed wall).
- **Per-height-parallel RAM budgeting** (from the dalby/ayr experiments) feeds every
  production launch: MAXJOBS × measured per-height peak < machine RAM, no swap.

## Cross-cutting: DEPLOYMENT plan

- **Job-checklist discipline** (`docs/job-checklist.md`) on every production run:
  predict/benchmark cost → fit the budget vs MAX of what's running → saved in-repo
  script → provenance baked → checkpointed/resumable → recorded in ledger + RESULTS.
- **Don't disturb in-flight work.** Current: gympie M(16), dalby n=18 holes, ayr a(20).
  Land engine changes on a box only after it frees; build under a new name if needed so
  a running binary isn't overwritten (SIGBUS risk on a live mmap).
- **Machine roles** ([[machine-availability-2026-06]]): **ayr** (x86/gcc) is the
  confirmation partner — the a(22) x86 run that compression unlocks; **dalby**
  (ARM/clang, 125 GB) computes the terms that only fit there (a(22) raw, a(23)
  compressed) and is the ARM cross-ISA leg; **gympie** (24 GB) does the `--profile-rows`
  measurement, light cross-checks, and dev/gate iteration.
- **Rollout sequence per term:** compression lands + gate-green → re-benchmark a(18)
  end-to-end (validate no regression, measure the new footprint) → run a(22) on ayr
  (now fits) and dalby → **cross-ISA diff = confirmed** → record R-result + ledger +
  b-file → then a(23) on dalby (compressed, computed-only). Free/one-sided(n) ride along.
- **Each lever is its own commit**, gate-green, with the calibration delta in the
  message; `state-store-compression.md` status tags flip from "projected/UNBUILT" to
  "landed + measured" as they go.

## Sequencing, dependencies, risk

```
0.1 FLM gate ─┬─(NO-GO scaling)─► reorder around FLM (out of this plan's scope)
              └─(GO)─► 0.2 profile-rows ─► Phase 1 ranged ─► Phase 2 u32+CRT ─► confirm a(22)
                                                   │
                                                   └─► Phase 3 structural ─► a(23) ─► Phase 4 OOC ─► a(24)+
0.3 commit / 0.4 driver — parallel, no deps, do immediately.
```

- **Keystone:** Phase 1 (ranged row) — biggest single win, cleanest drop-in. Everything
  downstream stacks on it.
- **Highest risk:** Phase 3.1 (symmetry fold) — correctness-critical parity handling;
  widest gate, dedicated unit test, land last among the "confirm a(22)" set.
- **Biggest unknown:** Phase 0.1 (FLM) — could reorder the whole plan; that's exactly
  why it's first and cheap.
- **Reversibility:** every lever is behind the store interface and gated byte-identical,
  so any can be reverted without touching call sites if a benchmark disappoints.
