# PRD — Next-system polyplet enumerator (v1)

Status: DRAFT 2026-06-26 · Owner: jasonp · First of the build trilogy (PRD → DESIGN → IMPLEMENTATION-PLAN).
Source design record: [`docs/frontier/NEXT-SYSTEM.md`](../frontier/NEXT-SYSTEM.md) (the investigation that
determined the architecture). This PRD states **what v1 must do and why**; it does not prescribe how
(that is DESIGN.md). Where a requirement is already settled by the design record, it is cited, not
re-argued.

---

## 1. Purpose & background

We count **polyplets** (king-connected polyominoes, OEIS [A030222](https://oeis.org/A030222)) by cell
count `n`. The current transfer-matrix column-sweep engine (`cpp/tma/`) has reached the frontier and is
presently computing a(21)/a(22); it is **compute-bound** and cannot be tuned past roughly a(25)/a(26)
(the growth base, not storage/IO/counting, is the sole ceiling lever — confirmed, NEXT-SYSTEM.md §J).

The current engine also has two structural limits that block the next terms even *within* the compute
ceiling: (1) it checkpoints only at **column boundaries**, so a multi-day pole column that crashes loses
everything (this session lost ~6 h of H19 to exactly this); (2) all parallelism is **in-process** shared
state, which caps a single sweep at ~38× on dalby while *independent* sweeps scale 100% to 76×.

The next system re-expresses the validated transfer-matrix transition as a **parallel external
merge-sort** over spilled sorted runs. Spilled runs are simultaneously output + checkpoint + resume-state
+ work-unit, which makes loss bounded by wall-clock cadence (not column structure) and lets parallelism
be **cross-process** (no shared state → no 38× cap). This is an evolvable, component-swappable
architecture: start single-box with NVMe spill, scale by replacing components (store backend, counter
width, distribution) without rewriting the core.

**Why now:** the design space is closed (NEXT-SYSTEM.md Rounds 1–3 — algorithm confirmed as the column
sweep, diagonal falsified, state floor measured, monster verdict GO, threading/migration/format all
settled). What remains is to *build* it. This trilogy turns the closed design into an executable plan.

## 2. Goals & success criteria

**v1 success = reproduce a(22) byte-identically against the old engine, then compute a(23) — the first
term only the new engine reaches — and ship it with a publicly verifiable dataset.**

| # | Goal | Measurable success criterion |
|---|------|------------------------------|
| G1 | **Correct core** | New engine reproduces a(n) for all n it computes, byte-identical to the old engine's per-height triangle T(n,H) through a(22). |
| G2 | **Trust milestone** | New engine's a(22) == old engine's a(22) (the last term the old engine reaches). The old engine earns retirement by being **out-reproduced**, not merely replaced. |
| G3 | **First record term** | New engine computes a(23) — a term no prior engine has reached — on a single box, resumably. |
| G4 | **Bounded-loss operation** | A kill at any wall-clock moment loses ≤ one checkpoint interval of work; resume is byte-identical to an uninterrupted run. |
| G5 | **Cross-process scaling** | A single n,H computation uses many cores via independent worker processes, beating the old engine's ~38× single-sweep cap on the same box. |
| G6 | **Publishable, verifiable result** | a(23) ships as: the triangle, the run dataset + manifest, mod-p residues, and an **independent Go verifier** a skeptic can run with no special tooling (`formats.md` documents every byte). |
| G7 | **Evolvable seams** | counter width (u64→u128), store backend (RAM→NVMe→distributed), and classifier (triangle/holes/GF) are swappable at defined interfaces without touching the tested core. |

**Primary metric:** a(23) computed and published with the full verification stack.
**Definition of done:** all of G1–G7 hold; the milestone gates in §8 pass.

## 3. Outputs (in v1 scope)

The engine produces three classifier outputs from the **same** core sweep (each a counter/classifier
configuration, per the component design — NEXT-SYSTEM.md "Architecture"):

- **FR-O1 — By-height triangle T(n,H)** *(spine, primary).* `a(n) = Σ_H T(n,H)`. The irreducible-minimum
  output; everything else is layered on it.
- **FR-O2 — Hole-count distribution** *(required).* Per-(n, hole-count) breakdown, reusing the existing
  Euler/hole accounting (`cpp/tma/euler.h`). Important to jasonp — a v1 ship requirement for the terms in
  range (blocks AC-6), not merely best-effort.
- **FR-O3 — Generating-function recovery (fixed-height, mod-p)** *(best-effort).* The mod-p column engine
  path recovering fixed-height GFs. Very desirable but **non-blocking**: build the seam and produce GFs
  where they fit; a(23) + triangle + holes + verifier may ship without it.

> Note (carried to DESIGN): O2 and O3 are additional classifier/counter configurations over the one core
> transition, gated the same way as O1 — not separate engines. Priority order if either costs the core
> flexibility (design-record standing rule, NEXT-SYSTEM.md "Design philosophy"): drop **O3 (GF) first**,
> keep O2 (holes); the O1 triangle spine is never dropped. The kill-switch is the contingency, not the plan.

## 4. Users & operating context

- **Single operator** (jasonp), running on the known boxes: gympie (10 perf-core cap), ayr (78 GB /
  32-core budget), dalby (big-RAM reach box). No multi-tenant, no external users.
- **The old engine keeps running a(21)/a(22) uninterrupted** on dalby/ayr; the new system is built in
  parallel and uses the old engine as its **test oracle through a(22)** (NEXT-SYSTEM.md "Migration").
  Hard constraint: v1 work must not disturb the running frontier jobs.
- **Operation is interactive + long-running:** an operator launches a run, monitors telemetry, and may
  kill/resume across days. No unattended cloud autoscaling in v1.
- **a(23) target box = dalby** (big-RAM reach box), sized from the ~110 B/state floor (C-3). **A rented
  large cloud VM is an acceptable fallback** *iff* pre-launch sizing makes the fit certain — the engine
  must therefore stay box-agnostic (no dalby-specific assumptions baked into the core); box choice is a
  launch-time decision, not a design-time one.
- **Verifier audience:** a future skeptic (OEIS reviewer, another researcher) who has the published
  dataset and `formats.md` but not our hardware or code.

## 5. Functional requirements

**Engine & execution**
- FR-1 Compute T(n,H) (and O2/O3 outputs) via the transfer-matrix column sweep expressed as external
  merge-sort over sorted runs.
- FR-2 Spill sorted runs to NVMe when RAM pressure demands; a RAM surprise spills, never crashes
  (predictions advisory — NEXT-SYSTEM.md "Work-safety").
- FR-3 Wall-clock-cadence checkpointing: a checkpoint is takeable mid-column, bounding loss to one
  interval regardless of column structure.
- FR-4 Resume from checkpoint produces byte-identical results to an uninterrupted run, including
  cross-architecture (arm64 ↔ x86 — already GREEN, NEXT-SYSTEM.md oq2).
- FR-5 Cross-process parallelism: an orchestrator spawns single-threaded worker processes over shards
  and steals hot tails dynamically (work-stealing, atomic-cursor — not static striding).
- FR-6 Budget governor: a wall/disk budget surprise triggers graceful checkpoint+stop, never an OOM or
  silent overrun.

**Counting & correctness**
- FR-7 Exact counting with a swappable counter: u64 (valid ≤ a(25)), u128 (valid ≤ ~a(48)); the engine
  refuses to start (or warns + widens) if the configured counter cannot hold the target.
- FR-8 Continuous mod-p shadow available as a consistency layer (multi-prime + CRT).

**Provenance & accounting**
- FR-9 Every binary stamps git rev (with `-dirty`) in both its filename and its `event=start`; every
  clean exit reports `cpu_s`, `wall_s`, `peak_rss`.
- FR-10 Abnormal exit folds accounting into the checkpoint (cpu/wall SUM, rss MAX) so the eventual
  `event=done` reports the true total across a crash.

**Deliverable / verification (G6)**
- FR-11 Emit the triangle as human-readable text (`# n H T(n,H)`, a(n)=Σ_H).
- FR-12 Publish the run dataset (sorted runs), a provenance manifest, and mod-p residues; document every
  byte in `formats.md`; provide a `dump`/`--text` render tool for the binary run bodies.
- FR-13 Ship an **independent Go verifier** that re-checks published runs/subtotals/residues for
  consistency and spot-checks by re-running sampled shards.

## 6. Non-functional requirements

- NFR-1 **Correctness is enforced by build-failing gates** (fitness functions), not documentation. The
  byte-identical-to-old-engine gate is the template; extend to module-boundary and (where two
  decompositions exist) cross-decomposition agreement. A failing invariant fails the build.
- NFR-2 **Work-safety:** no mispredicted size/time ever causes a crash or work loss beyond one
  checkpoint interval. Predictions revise plans, never correctness.
- NFR-3 **Performance envelope:** a(23) should *fit and finish* on a single box within an
  operator-tolerable wall — **target days, not weeks** (achievability is open: a(21) already takes days,
  and a(23) is ~2 growth-terms larger). This is an aspiration that shapes how hard the design leans on
  cross-process scaling, **not** a correctness requirement — a slow-but-correct a(23) still ships. The
  system need not beat the compute ceiling (a(25)/a(26)) — only fit the v1 target term.
- NFR-4 **Evolvability:** counter, store, and classifier seams are clean interfaces; swapping one is a
  drop-in that does not touch the tested transition/signature core (G7).
- NFR-5 **Small tested core:** the single-source-of-truth C++ core (`libenum`) stays near its ~400–600
  line target; no hot-path threading, no I/O policy, no scheduling inside it.
- NFR-6 **Observability:** uniform telemetry (`event=` lines, heartbeat with a real measured ETA basis,
  per-worker accounting) sufficient for an operator to watch a multi-day run and trust its progress.
- NFR-7 **Two compiled languages only:** C++ core + Go for all operational tooling (orchestrator,
  governor, telemetry, verifier). No interpreted glue in the production path.
- NFR-8 **Readable-where-read, packed-where-streamed:** text for results/metadata/headers/residues;
  documented simple binary for hot sorted-run bodies, always renderable to text on demand.

## 7. Constraints & assumptions

- C-1 **Compute ceiling is real and accepted:** a(25)/a(26) is the wall on the column base; v1 does not
  attempt to move it. (NEXT-SYSTEM.md §J — confirmed.)
- C-2 **Algorithm is fixed:** column decomposition; the diagonal alternative is **falsified** (base ~4.52,
  not 2.04). No decomposition-pluggability is built — there is no live second decomposition.
- C-3 **State floor:** ~110 B/state raw / ~130 deployed, with ranged-row the keystone constant factor.
  a(23) memory/spill sizing follows from this measured floor.
- C-4 **Monster verdict GO:** no single source state is a cost monster at production shard sizes
  (10k–100k states); work-stealing over hash-sharded states suffices, no mask-splitting. Shards are
  small *and dynamic* (NEXT-SYSTEM.md "per-state map-cost" RESOLVED).
- C-5 **Old engine is the oracle** through a(22); after that, v1 leans on the validation stack (small-n
  regression + row-sum + mod-p shadow + publish-and-verify). There is no external oracle for a(23).
- C-6 **Don't disturb the frontier:** a(21)/a(22) on dalby/ayr run uninterrupted; new-system development
  is isolated (this `next-system` branch; remote boxes stay on master).
- A-1 NVMe sequential bandwidth out-runs random RAM 2–4× (measured, dalby) — the basis for spill-sort
  beating hash-in-RAM. Assumed to hold on the box that runs a(23).

## 8. Acceptance criteria (product-level gates)

v1 is accepted when each milestone gate passes (these become the IMPLEMENTATION-PLAN checkpoints):

- AC-0 **libenum core:** link-test reproduces a(n) for small n, byte-identical to the old engine.
- AC-1 **Single-process end-to-end:** a(18)–a(20) byte-identical via worker + trivial driver + NVMe
  spill (proves the sort/spill engine).
- AC-2 **Orchestrator:** same a(n) computed in parallel across worker processes AND resumable —
  kill-at-arbitrary-wall-moment then resume is byte-identical.
- AC-3 **Trust milestone (G2):** new engine a(22) == old engine a(22).
- AC-4 **Record term (G3):** new engine computes a(23), resumably, on a single box.
- AC-5 **Deliverable (G6):** a(23) ships with triangle + dataset + manifest + residues + independent
  verifier, all documented in `formats.md`; the verifier passes on the published artifacts.
- AC-6 **Outputs (FR-O2):** hole-count distribution produced and cross-checked for the terms in range
  (required). GF recovery (FR-O3) is best-effort — shipped if it fits, does not block v1.

## 9. Risks & pre-planned responses (advisory; expanded in the plan)

| Risk | Signal | Pre-planned response |
|------|--------|----------------------|
| Straggler/barrier imbalance sneaks unpredictability back as low utilization | per-worker runtime heavy tail; merge waits on one map | mid-flight stealable tails; output-range partitioned merge; (v2) merge(c)→map(c+1) pipelining |
| Monster state defeats work-stealing (verdict says no) | a shard's max/mean approaches its state count | already bounded 20–500× below threshold; fallback = split a hot state's mask enumeration (designed, not built) |
| a(23) doesn't fit dalby's RAM+NVMe | spill volume projection exceeds disk | size from the ~110 B/state floor before launch; if dalby can't fit, rent a large cloud VM (acceptable fallback) once sizing makes the fit certain; governor stops gracefully if wrong mid-run |
| Counter overflow near the u64 edge | target term > a(25) validity | FR-7 refuses/widens at start; u128 is the drop-in |
| New engine disagrees with old at a(22) | AC-3 fails | do NOT proceed to a(23); bisect via byte-identical small-n gates + mod-p shadow until new==old |
| GF/holes path compromises the core | core flexibility cost shows up | priority-ordered kill-switch: drop O3 (GF, best-effort) first; keep O2 (holes, required) and the O1 triangle spine |

## 10. Out of scope for v1 (deferred, not cut — the scale-by-replacement ladder)

- Multi-box distribution (splitting one height across machines via sorted-run partition) — the sort
  engine *enables* it; v1 is single-box + NVMe.
- Cloud / elastic resources / new hardware.
- bignum counting (u128 covers to ~a(48), far past the compute ceiling — never reached).
- Pushing the compute ceiling (a(25)/a(26)) — no algorithmic base-reducer exists (C-2).
- Whole-hog provenance database (AiiDA-style) — the rev-stamping 80/20 is deliberate.

---
_Next: DESIGN.md turns these requirements into the concrete architecture, interfaces, and on-disk
formats, drawing the settled material forward from NEXT-SYSTEM.md and resolving any remaining design
choices by interview._
