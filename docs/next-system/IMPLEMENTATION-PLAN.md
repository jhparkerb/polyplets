# IMPLEMENTATION-PLAN — Next-system polyplet enumerator (v1)

Status: DRAFT 2026-06-26 · Third of the build trilogy. Inputs: [`PRD.md`](PRD.md) (requirements,
acceptance gates AC-0…6), [`DESIGN.md`](DESIGN.md) (architecture, API, formats, gate set),
[`docs/frontier/NEXT-SYSTEM.md`](../frontier/NEXT-SYSTEM.md) (closed design space). This document
sequences the build into milestones at **Sonnet-executable grain**, each task carrying its functional
checkpoint and a **pre-documented response to adverse results**.

## How to use this plan (for the implementer)

- **Work top-to-bottom.** Each milestone Mk satisfies acceptance gate AC-k. **Do not start Mk+1 until
  Mk's exit gate is green.** The gates are the teeth (NFR-1) — a red gate is a stop, not a warning.
- **Each task is `Build / Files / Gate / Adverse`.** *Build* = what to implement. *Files* = where.
  *Gate* = the executable check that closes the task. *Adverse* = what to do when the gate fails (the
  pre-planned response — follow it before improvising).
- **Reuse, don't reinvent.** Transition/signature/prune/fold come from today's `cpp/tma/` **verbatim**
  (DESIGN §0). If you find yourself rewriting the king-closure math, stop — you're off-plan.
- **The old engine is the oracle** (through a(22)). "Byte-identical to old engine" means: run the old
  `build/tma square8 N` (or its per-height triangle) and `diff` the T(n,H) output exactly.
- **Complexity tags** (S/M/L) hint relative effort for sequencing only — they are NOT schedule/ETA
  estimates (no fabricated ETAs).

## Operating guardrails (do not violate)

- **G-A The running a(21)/a(22) frontier jobs are untouchable.** They run on dalby/ayr on `master`. All
  v1 work is on the `next-system` branch and on *free* cores only. Never restart/disturb a healthy
  frontier job (correctness-or-dead-box bar only). Honor gympie's 10-perf-core cap and ayr's 78 GB /
  32-core budget when picking where to run gates.
- **G-B No >1 hr compute job without explicit beg-and-agree** (consult `docs/job-checklist.md` first).
  This gates M3's a(22) cross-check and M4's a(23) run specifically.
- **G-C Rev-stamped binaries.** Every build carries the git rev (`-dirty` if the tree differs) in
  filename and `event=start`. A gate run with a dirty tree is for iteration only; milestone-closing gate
  runs use a committed tree.
- **G-D Publishing is jasonp's call.** The plan PREPS the dataset/verifier/manifest; it never sends
  anything external. M5 ends "ready to publish," not "published."

## Milestone overview

| M | Objective | AC | Exit gate (the trust step) | Tag |
|---|-----------|-----|---------------------------|-----|
| **M0** | `libenum` core (riskiest first) | AC-0 | in-process map+merge reproduces T(n,H) byte-identical, n≤14 | L |
| **M1** | single-process end-to-end + NVMe spill | AC-1 | a(18)–a(20) byte-identical with real disk spill | M |
| **M2** | Go orchestrator (parallel + resumable) | AC-2 | parallel == serial AND kill+resume byte-identical | L |
| **M3** | a(22) cross-check (the trust milestone) | AC-3 | new a(22) == old a(22) | M |
| **M3.5** | a(23) sizing pre-flight | — | documented fit + box chosen + go/no-go | S |
| **M4** | a(23) record term | AC-4 | a(23) computed, resumably, internal checks pass | M |
| **M5** | deliverable + outputs (holes req, GF best-effort) | AC-5,6 | verifier passes on published dataset; holes cross-checked | L |

---

## M0 — `libenum` core extraction *(AC-0; riskiest piece first)*

**Objective:** the trusted ~700-line core compiles behind `libenum.h`, and an in-process driver computes
T(n,H) via `map_shard` + `merge` byte-identical to the old engine. No spill, no workers, no Go yet — prove
the algorithm re-expression in isolation. **Entry:** clean `next-system` branch.

- **T0.1 Repo scaffold.** *(S)*
  - Build: create `core/ worker/ orchestrator/ verify/ test/ data/ docs/`; `Makefile` with rev-stamping
    (copy the `GIT_REV/GIT_DIRTY` block from the current Makefile), `go.mod`, `README.md`. A no-op
    `arch_fitness.go` skeleton.
  - Files: tree per DESIGN §13 / `layout.md`.
  - Gate: `make` builds an empty core lib + `go vet ./...` clean; `arch_fitness` runs (asserts nothing yet).
  - Adverse: toolchain issues only — fix before proceeding; this task has no algorithmic risk.
- **T0.2 Move the trusted math under `core/`, unchanged.** *(M)*
  - Build: relocate `signature.h`, `transition_square8.h` (the `stepColumnSquare8`/`forEachViableMask`
    kernel), `euler.h` into `core/`; expose `Sig`, `canonicalizeSig`, `foldSig`, `completionLowerBound`,
    `stepColumnSquare8`, `forEachViableMask` through `libenum.h`. **Do not edit the math.**
  - Files: `core/signature.h`, `core/transition.h`, `core/euler.h`, `core/libenum.h`.
  - Gate: port the existing unit assertions (canonicalize/reflect involution, `completionLowerBound`
    admissibility on the fixtures) → all pass identically to today.
  - Adverse: any diff from old behavior here means an accidental edit during the move — `git diff` the
    math against `cpp/tma/`, revert to verbatim. The math is not in scope to change.
- **T0.3 `run.h` — record (de)serialize + sort-key contract.** *(M)*
  - Build: the sorted-run record (DESIGN §9): `sig (H+2) | lo:u8 | len:u8 | counts[len]·W`. Ranged
    count-vec (contiguous nonzero window). Sort key = `memcmp(sig)`. Serialize/deserialize + a `RunWriter`
    /`RunReader` over a byte stream.
  - Files: `core/run.h`, `core/run.cpp`.
  - Gate: round-trip property test (random valid states → serialize → deserialize → identical); `memcmp`
    order matches canonical-sig order; ranged value reconstructs the dense count-vec.
  - Adverse: if round-trip differs, suspect the `lo/len` ranging (off-by-one on the window) or counter
    width mismatch — unit-isolate the value codec from the sig codec before integrating.
- **T0.4 Counter + classifier templates (u64 / triangle).** *(M)*
  - Build: `Counter<u64>` (accumulate, widening guard) and `Classifier<triangle>` whose `complete()`
    reproduces `sweep8.h:95–96` (single component touching top+bottom of height H ⇒ `T[n] += counts[n]`).
    The reduce op (range-union + componentwise `+=`) lives in `run.h`/`mapreduce`.
  - Files: `core/counter.h`, `core/classifier.h`.
  - Gate: on a hand-built fixture of closing states, `complete()` emits exactly the old engine's triangle
    contribution.
  - Adverse: mismatch ⇒ check the completion predicate (comps==1 via max-label on a *canonical* sig, both
    touch flags) against `sweep8.h` line-for-line.
- **T0.5 `map_shard` + `merge` (in-RAM) and the AC-0 driver.** *(L — the integration risk)*
  - Build: `map_shard` per DESIGN §4 but **in-RAM** (no spill yet: buffer → sort → return run);
    `merge` per §5 (k-way heap, combine equal sigs). A throwaway `test/driver0.cpp`: per height H, loop
    columns running `map_shard`(whole frontier as one shard) then `merge`, summing the classifier output
    to T(n,H).
  - Files: `core/mapreduce.h/.cpp`, `test/driver0.cpp`.
  - Gate (**AC-0**): `driver0` reproduces T(n,H) for **all H, n≤14** byte-identical to the old engine;
    Σ_H T(n,H) == a(n) from fixtures.
  - Adverse: (a) **totals right but T(n,H) split wrong** → classifier/height bug, not transition — check
    the completion side. (b) **off by a little at one (n,H)** → prune over-aggressive: `completionLowerBound`
    must never over-estimate (DESIGN §2); temporarily disable the prune and re-gate to localize. (c)
    **off at large n only** → ranged count-vec window truncating nonzeros (T0.3 regression). (d) Bisect with
    the fold OFF first, then ON (isolates a `foldSig` integration bug from a transition bug).
- **Exit gate M0:** AC-0 green (in-process map+merge == old engine, n≤14, all H) on a committed tree.

## M1 — single-process end-to-end + NVMe spill *(AC-1)*

**Objective:** prove the sort/spill engine on real disk with thin worker binaries and a trivial driver —
still one process at a time, no Go. **Entry:** M0 green.

- **T1.1 Mid-shard spill in `map_shard`.** *(M)*
  - Build: when the sort buffer would exceed `ram_budget_bytes`, sort + spill a partial run, continue;
    finish by k-way-merging the shard's own spills into one sorted output run (DESIGN §4).
  - Files: `core/mapreduce.cpp`.
  - Gate: `map_shard` with a tiny `ram_budget` (forces many spills) returns a run **byte-identical** to the
    no-spill path. (The spill is invisible to the result — the bit-identical property.)
  - Adverse: any diff ⇒ spill/merge ordering bug; the per-shard final merge must combine equal sigs that
    landed in different spills. Test with `ram_budget` = 1 record (maximal spilling) to surface it.
- **T1.2 `map_worker` + `merge_worker` CLIs.** *(M)*
  - Build: the two thin process wrappers (DESIGN §8) — argv parse, open runs via paths, call the libenum
    function, write run + `event=done` accounting (`cpu_s wall_s peak_rss records spill_bytes` via
    `getrusage`), graceful SIGTERM → flush final spill + write cursor → exit.
  - Files: `worker/map_worker.cpp`, `worker/merge_worker.cpp`.
  - Gate: each worker, fed a captured run fixture (`test/fixtures/run_n14.bin`), produces the expected
    output run + a well-formed accounting line.
  - Adverse: SIGTERM mid-map must still leave a valid (sorted, CRC'd) partial run + cursor — test by
    sending SIGTERM during a large fixture and checking the partial run reads back clean.
- **T1.3 Trivial single-process driver + AC-1.** *(M)*
  - Build: `test/driver1` (or a `--serial` mode of the eventual orchestrator) that loops columns: partition
    the frontier into key-range units, invoke `map_worker` per unit **sequentially**, then `merge_worker`
    over output ranges, spilling all runs to a real NVMe dir.
  - Files: `test/driver1.cpp` (or Go `orchestrator --serial`).
  - Gate (**AC-1**): a(18), a(19), a(20) T(n,H) byte-identical to old engine, with runs actually spilled to
    and read from disk (verify spill_bytes > RAM).
  - Adverse: (a) **disk fills** → reduce `ram_budget` raises spill count not size; check runs are deleted
    once consumed by the next column's merge (the driver must GC consumed runs). (b) **slow** → expected at
    this stage (sequential, no parallelism); not a correctness signal, do not optimize yet. (c) **mismatch
    vs M0** → the only new variables are spill + worker I/O; bisect by running the same n through M0's
    in-RAM `driver0`.
- **Exit gate M1:** AC-1 green (a18–a20 byte-identical, real spill).

## M2 — Go orchestrator: parallel + resumable *(AC-2)*

**Objective:** cross-process parallelism (process-per-unit, D-1), work-stealing, budget governor, and
wall-clock checkpoint/resume. **Entry:** M1 green. This is the largest milestone.

- **T2.1 `store.go` — local NVMe RunRef backend.** *(M)*
  - Build: the `Store` interface (`Put/Get/List/Open RunRef`, where `RunRef` = path+records+key-range+CRC)
    with the **local-NVMe impl only** (D-3). Run GC (delete consumed runs).
  - Gate: store round-trips a run; `List` by column returns the frontier; CRC mismatch is detected on Open.
  - Adverse: CRC failure on Open ⇒ surface loudly and refuse (a corrupt run must never be silently merged —
    this is a no-silent-zeros guardrail).
- **T2.2 `scheduler.go` — column DAG + process-per-unit pull-queue.** *(L)*
  - Build: the sweep driver loop (DESIGN §6); partition frontier keys into ~10⁴–10⁵-state units; a pool of
    ≈`cores` workers each spawned per unit (D-1), pulling the next unit when idle.
  - Gate: parallel T(n,H) == serial (M1) **byte-identical** for a(16)–a(18), across several `--cores`
    values (commutative/associative property ⇒ result independent of sharding).
  - Adverse: **nondeterministic totals across core counts** ⇒ a reduce that isn't actually associative
    crept in (e.g., float, or a non-canonical sig in the key path) — the merge must combine by exact
    `memcmp` key; dump the differing run with `runcat` and diff.
- **T2.3 Work-stealing straggler tail-split.** *(M)*
  - Build: straggler detection (unit running ≫ median) → hand `[cursor,hi)` to an idle worker, signal the
    straggler to stop at cursor (DESIGN §7.2, cursor files, D-2).
  - Gate: inject an artificial heavy unit; verify (a) total is unchanged byte-identical, (b) wall drops vs
    no-split, (c) both halves' runs appear in the merge.
  - Adverse: **double-counting** (straggler didn't actually stop at cursor, tail re-mapped overlap) ⇒ the
    stop-at-cursor and the tail's `lo` must be the *same* key, half-open `[lo,hi)`; assert disjoint coverage
    of the unit's key-range in a debug check.
- **T2.4 Partitioned merge.** *(M)*
  - Build: sample keys from the map-phase runs to pick ≈`cores` even cut points; one `merge_worker` per
    output range (DESIGN §7.3).
  - Gate: partitioned merge == single-range merge, byte-identical; ranges are disjoint and cover the key
    space.
  - Adverse: **gap/overlap at a cut point** ⇒ boundary key assigned to two ranges or none; cut points are
    half-open and must tile exactly. Property-test coverage.
- **T2.5 `governor.go` — budget + graceful stop.** *(M)*
  - Build: wall/disk budget guards; on trip, SIGTERM workers → let them checkpoint → write POLYCKPT → stop.
    Never OOM, never silent overrun (FR-6, NFR-2).
  - Gate: set a tiny disk/wall budget mid-run → engine stops cleanly with a valid resumable checkpoint, no
    OOM, no partial-write corruption.
  - Adverse: **OOM before the governor trips** ⇒ the `ram_budget` per worker × concurrent workers exceeds
    box RAM; the governor must account aggregate worker RAM, not just its own.
- **T2.6 `checkpoint.go` — wall cadence, resume, accounting fold-in.** *(L — the AC-2 core)*
  - Build: POLYCKPT (DESIGN §9) written at wall cadence naming done runs + inflight cursors + frontier +
    `acct`; resume reloads frontier, re-dispatches not-done units and inflight tails, seeds accounting
    (cpu/wall SUM, rss MAX).
  - Gate (**AC-2**): kill the process at a **random wall moment** (not a column boundary) during a(19),
    resume, and get a(19) T(n,H) **byte-identical** to an uninterrupted run; the final `event=done`
    accounting equals the summed-across-crash truth (cpu/wall SUM, rss MAX).
  - Adverse: (a) **resume diverges** ⇒ an inflight unit was neither completed nor re-dispatched — a unit
    must be exactly-once: done (run present) XOR re-run from `lo` (or tail from cursor). (b) **double-count
    on resume** ⇒ a completed-but-not-recorded run got re-run; record done-runs in the checkpoint *before*
    deleting any input. (c) **accounting wrong** ⇒ cpu/wall must SUM across segments, rss must MAX — re-read
    the fold rule.
- **T2.7 `telemetry.go` — accounting aggregation + honest heartbeat.** *(S)*
  - Build: aggregate worker `event=` lines; heartbeat with an ETA basis that is **measured** (states
    done / rate), never invented; cost-weighted progress (states carry heavy-tailed cost, so a raw
    %-of-states is bursty — weight by observed map cost, the thing today's engine lacks).
  - Gate: telemetry sums per-worker cpu/wall correctly; a heartbeat with no rate history reports "ETA
    unknown," not a fabricated number.
  - Adverse: bursty/√ progress is expected (heavy-tailed cost) — surface it as cost-weighted, don't "smooth"
    it into a false-confidence linear bar.
- **Exit gate M2:** AC-2 green (parallel == serial AND kill+resume byte-identical, accounting correct).

## M3 — a(22) cross-check: the trust milestone *(AC-3)*

**Objective:** prove new == old on the last term the old engine reaches. **Entry:** M2 green. **G-B applies**
(a(22) is a >1 hr job → beg-and-agree, job-checklist).

- **T3.1 `Counter<u128>` drop-in.** *(S)*
  - Build: the u128 counter template + run-header width `u128` (the swap, DESIGN §10). u128 add/widening
    already PASS both ISAs (`u128_smoke`, committed).
  - Gate: u128 a(n) == u64 a(n) for n in u64 range, byte-identical totals.
  - Adverse: cross-ISA byte-diff ⇒ endianness in the value codec (must be LE per §9); the sig key is
    already endian-neutral (byte array).
- **T3.2 a(20)/a(21) full cross-check.** *(M)*
  - Build: run the new engine at a(20), a(21) on free cores.
  - Gate: T(n,H) byte-identical to the old engine for both.
  - Adverse: mismatch here (not at small n) ⇒ a scale-only bug: spill volume, u128 boundary, or a unit-
    partition edge that only appears with many units. Diff the per-(n,H) row to find the first divergent H.
- **T3.3 a(22) cross-check.** *(M — gated by G-B)*
  - Build: run new-engine a(22); compare to the old engine's a(22) (the frontier job's result, once it
    lands, or a dedicated run).
  - Gate (**AC-3**): new a(22) T(n,H) == old a(22) T(n,H), exactly. **The old engine earns retirement here.**
  - Adverse: **any disagreement halts the ladder — do NOT proceed to a(23).** Playbook: (1) confirm both on
    a clean rev (G-C); (2) `gate_modp` shadow on both — if mod-p agrees but full disagrees, suspect a
    counting-width/overflow issue, not the transition; (3) bisect down in n until they agree, the first
    divergent n localizes it; (4) the new engine is wrong until proven otherwise (the old engine is the
    validated oracle).
- **Exit gate M3:** AC-3 green. This is the de-risking core of the whole plan.

## M3.5 — a(23) sizing pre-flight *(go/no-go before spending compute)*

**Objective:** decide a(23) fits before launching it (NFR-2: never lose work to a misprediction).
**Entry:** M3 green.

- **T3.5 Sizing.** *(S)*
  - Build: project a(23) peak live states and total spill volume from the ~110 B/state floor (C-3) ×
    measured state-growth (2.43×/N pole, a22-forecast), plus the merge transient (~2× column). Pick the box:
    dalby first; if it doesn't fit RAM+NVMe with margin, spec a rented large cloud VM (acceptable fallback,
    PRD §4) and only commit when the fit is **certain**. Set governor wall/disk budgets from the projection.
  - Gate: a written sizing in `data/manifests/` (projected peak states, spill GB, chosen box, headroom
    margin, governor limits) reviewed before launch; explicit go/no-go.
  - Adverse: projection says it doesn't fit any available box with margin ⇒ **stop and replan** (defer to
    multi-box, or to the sig 4-bit pack which buys ~2× state bytes) rather than launch-and-hope. A
    misprediction must revise the plan, never crash a multi-day run (NFR-2).

## M4 — a(23) record term *(AC-4)*

**Objective:** compute the first term only the new engine reaches. **Entry:** M3.5 go. **G-B applies.**

- **T4.1 Launch + operate a(23).** *(M — long run, operated per job-checklist)*
  - Build: run a(23) on the chosen box, one tmux window, foreground-visible with tee; governor on;
    wall-cadence checkpoints; resume-on-interrupt exercised at least once deliberately early to confirm the
    real run is resumable (FR-4).
  - Gate (**AC-4**): a(23) = Σ_H T(n,H) computed to completion, resumably.
  - Adverse: (a) **counter near u64 edge** — a(23) is well below a(25), u64 valid; but FR-7 must have refused
    a too-narrow counter at start. (b) **doesn't fit despite M3.5** — governor checkpoints + stops; replan
    box (cloud fallback) and resume from checkpoint, no lost work. (c) **box dies** — resume from last
    checkpoint, loss ≤ one unit + one wall-cadence interval.
- **T4.2 Internal validation stack (no oracle exists for a(23)).** *(S)*
  - Build: run the cheap consistency layers on a(23): row-sum (Σ_H T == a(23) self-consistent shape),
    growth-ratio smoothness vs a(18..22), multi-prime `gate_modp` shadow + CRT.
  - Gate: all consistency layers agree; mod-p CRT residues match the full count's residues.
  - Adverse: **mod-p disagrees with the full count** ⇒ arithmetic/transient bug — the full count is suspect;
    re-run the disagreeing height under ASAN/TSAN; do not publish until they agree. **Growth ratio jumps** ⇒
    a dropped/double-counted height; check per-H continuity against the a(18..22) triangle.
- **Exit gate M4:** AC-4 green, a(23) computed, internal checks pass.

## M5 — deliverable + outputs *(AC-5 publish-and-verify; AC-6 holes required, GF best-effort)*

**Objective:** package a(23) as a publicly verifiable dataset and produce the holes/GF outputs.
**Entry:** M4 green. (Parts run in parallel with M4's long compute.)

- **T5.1 `formats.md` — the published format spec.** *(S)*
  - Build: document every byte of run/checkpoint/triangle/manifest/residue formats (DESIGN §9) so a skeptic
    with no code can parse the dataset.
  - Gate: a fresh reader (or `runcat` written only from `formats.md`) parses a published run correctly.
- **T5.2 `manifest.go` + residues + `runcat` dump tool.** *(M)*
  - Build: per-a(n) provenance manifest (rev, cpu·s, wall, peak RSS, spill bytes, run list + CRCs); mod-p
    residue emission; `runcat --text` renders any binary run.
  - Gate: manifest cross-references resolve (every listed run exists, CRC matches); `runcat` round-trips.
- **T5.3 `verify/` independent tool *(AC-5)*.** *(L)*
  - Build: the separate Go verifier (DESIGN §12) — consistency (row-sum, mod-p CRT, growth smoothness),
    integrity (CRCs, manifest cross-refs), spotcheck (re-run sampled shards via a fresh `map_worker`, diff
    to published runs). Reads only `data/` + `formats.md`.
  - Gate (**AC-5**): verifier passes on the published a(23) dataset; a deliberately corrupted run/residue is
    caught (negative test).
  - Adverse: spotcheck mismatch ⇒ either the published run is stale (rev skew — check manifest rev) or the
    verifier's worker build differs; pin both to the same rev (G-C) before trusting the diff.
- **T5.4 Holes classifier (O2 — REQUIRED, blocks AC-6).** *(M)*
  - Build: `Classifier<holes>` keying completion by (n,H,holes) using `closedEulerDelta4` (`euler.h`,
    reused) carried in the value (DESIGN §3,10). Same engine, new classifier template.
  - Gate (**AC-6**): hole-count distribution byte-identical to the **old engine's `--holes`** for small n
    (the old engine is still the oracle for holes); produced for the terms in range up to a(23).
  - Adverse: mismatch ⇒ the hole accounting carried in the ranged value desynced from the count — verify
    the Euler delta is accumulated under the same reduce (associative) as counts; small-n diff localizes.
- **T5.5 GF recovery (O3 — BEST-EFFORT, non-blocking).** *(M)*
  - Build: `Counter<ModP>` + `Classifier<gf>` accumulating per-(H,n) residues; CRT recovery of fixed-height
    GFs (the mod-p path, reused concept).
  - Gate: recovered GF reproduces known fixed-height series at small H; best-effort for higher H within
    compute budget. **Does not block v1** — if it costs the core flexibility, drop O3 (priority kill-switch,
    PRD §3) and ship without it.
  - Adverse: GF recovery unstable/expensive ⇒ invoke the kill-switch (drop O3, keep triangle + holes); note
    it as deferred, not failed.
- **Exit gate M5:** AC-5 green (verifier passes on published dataset) **and** AC-6 green (holes
  cross-checked). GF shipped if it fit. Dataset **ready to publish** (G-D — jasonp pushes the button).

---

## Adverse-results playbook (consolidated)

Cross-referenced from tasks; the standing responses to the failure classes:

1. **New ≠ old at small n** → transition/classifier/codec bug (cheap to find). Bisect: fold off→on,
   prune off→on, in-RAM `driver0` vs spill vs parallel. The first divergent (n,H) localizes the layer.
2. **New ≠ old only at scale (a21/a22)** → spill/u128/many-unit edge, not the math. Diff per-H rows; find
   the first divergent H; check the unit-partition boundaries and the merge cut points.
3. **Nondeterministic across cores/sharding** → a non-associative reduce or a non-canonical key slipped in.
   The merge MUST combine by exact `memcmp(sig)`; dump with `runcat` and diff runs.
4. **Resume diverges / double-counts** → exactly-once unit accounting broken. A unit is done (run present)
   XOR re-run; record done-runs before deleting inputs; tails are half-open and disjoint.
5. **mod-p shadow disagrees with full count** (the only check that catches a(23)-class arithmetic bugs) →
   full count suspect; re-run under sanitizers; never publish until CRT agrees.
6. **Doesn't fit the box** → governor checkpoints + stops (never OOM); replan box (cloud fallback) or apply
   the sig 4-bit pack; resume from checkpoint. A misprediction revises the plan, never loses work.
7. **a(22) cross-check fails (AC-3)** → HALT the ladder. The new engine is wrong until proven otherwise;
   do not compute a(23) on a disagreeing engine. (Playbook in T3.3.)
8. **GF (O3) misbehaves** → priority kill-switch: drop O3, keep triangle + holes; ship v1; defer GF.

## Validation ladder (which gate catches which failure — recap of DESIGN §11)

gross bug → `gate_regression`/`gate_fold`/`gate_rowsum` (M0–M1) · checkpoint bug → `gate_resume` (M2) ·
boundary erosion → `arch_fitness` (all) · arithmetic/transient → `gate_modp` (M3–M4) · impl bug → the
**cross-engine a(22) gate** (M3) + the **published-dataset verifier** (M5). a(23)'s leading-edge trust =
method-proof + internal consistency + publishable recompute (no external oracle exists — accepted status).

## Traceability (task → requirement/AC)

T0.* → AC-0, FR-1, NFR-5 · T1.* → AC-1, FR-2 · T2.1→FR-store · T2.2/2.3→FR-5,AC-2 · T2.4→FR-5 ·
T2.5→FR-6,NFR-2 · T2.6→FR-3,4,9,10,AC-2 · T2.7→NFR-6 · T3.1→FR-7 · T3.3→AC-3,G2 · T3.5→NFR-2,NFR-3 ·
T4.1→AC-4,G3,G4 · T4.2→FR-8,NFR-1 · T5.1/5.2→FR-11,12 · T5.3→FR-13,AC-5,G6 · T5.4→FR-O2,AC-6 ·
T5.5→FR-O3.

## What this plan deliberately does NOT do (v1 scope, PRD §10)

Multi-box distribution, cloud autoscaling, bignum, pushing the a(25)/a(26) compute ceiling, and the sig
4-bit pack (held as a sizing-contingency lever, T3.5/playbook-6) are all **out of v1** — added later by
component replacement, not rewrite.

---
_End of the build trilogy. PRD (why/what) → DESIGN (how) → this plan (build order + checkpoints + adverse
responses). The implementer works M0→M5 top to bottom; each AC gate is a hard stop until green._
