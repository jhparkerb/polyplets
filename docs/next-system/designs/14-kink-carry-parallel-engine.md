# Design 14 — Parallel Kink-Carry engine

**Status: REDESIGN NEEDED (2026-07-02).** Smoke-tested serial kernel in
`experiments/kink_tm/`, results in `results/kink-carry.md` — that win stands.
**Phase 0.1 ran and Option B (below) is NO-GO**: shard duplication grows
`~S^0.7-0.8`, no plateau, eating most of the kernel's win at production shard
counts (128-320). Data + verdict in
`results/kink-carry-shard-duplication.md`. Phases 1-4 as written assume
Option B and need revision (Option A / hybrid / analytic shard bound) before
proceeding — do not start Phase 1 on this doc's original text.

## What changes and what does not

The engine today (design 00–13) parallelises **within a column**: partition the
source frontier by key into map units, run `map_shard` per unit independently
(each source state → `Σ viableMasks` successor records), then a **single merge
barrier** combines the sorted per-unit Runs into the next column's frontier.
`map_shard`'s per-source cost is the masks-per-state exponential (~1.4k kept
successors/state at H12, growing with H) and its output is `Σ masks` records —
which is what drives sort/spill/merge (126 GB spill peak at a27 H16).

The **kink-carry kernel** replaces `map_shard` and *only* `map_shard`. A column
becomes H sequential micro-stages, each placing one new-column cell with
fan-out 2 (empty/occupied) and merging intermediate mixed-boundary states
(boundary + one carried NW cell + touch flags) by canonical key. Only
**end-of-column states** are emitted. Per-source work drops from `Σ masks` to
`2·H·(intermediate factor)`; the intermediate factor is a **measured flat
~3.6× the frontier**, independent of H. Measured end-to-end: **29× at H12,
~55× at H14, extrapolating ~150–200× at H16** — a per-term compute base drop
from ~4.4 to ~2.5, and end-of-column record volume ~1000× smaller.

Everything downstream of the map kernel is **unchanged and reused**: the
`Run<W>` output contract (sorted end-of-column states, keyLen H+2), `mergeRuns`,
the orchestrator's column loop, height overlap, checkpoint/resume, telemetry,
the spill/zstd machinery (now rarely triggered), and the diagonal P_k closed
forms (orthogonal — they still cap the top swept height; the two wins compose
multiplicatively).

## The parallelisation choice (Option B: shard sources, private stage DP)

A map unit stays what it is today: **a key-range of the source frontier.** The
worker runs the *entire H-stage kink DP on its shard, privately in RAM*, and
emits that shard's end-of-column states as a sorted Run. The merge barrier then
combines end-of-column states across units exactly as today (same key, same
`combine`). No new barrier, no orchestrator restruct, no merge change.

The **only** new inefficiency: intermediate mixed-boundary states that would
merge *across shards* mid-column do not — each shard rebuilds its own
intermediates. Because intermediates are cheap (fan-out 2, polynomial) and
never leave the worker, bounded duplication here is acceptable against a 150×
win. The exact duplication-vs-shard-count curve is the Phase-0 de-risk
measurement and sets the unit-size sweet spot.

Rejected alternatives:
- **Option A (shard each stage, H barriers/column):** zero intermediate
  duplication but H merge barriers per column instead of 1. Held in reserve
  *scoped to the top height only*, if Phase 0 shows duplication is bad at the
  shard counts the top height needs.
- **Sibling engine:** duplicates the orchestrator/merge/test harness for no
  benefit. Option B is a drop-in `map_shard` variant, so it lives in-tree
  behind a `--kernel` flag, default-off until byte-match validated — the same
  pattern the holes/perim variants used.

## Work-stealing under the kink kernel

Today a steal splits a unit's remaining **key-range** at a cursor; correct
because map is per-source independent. Under kink, a stolen sub-unit is simply
**a smaller source-shard run through its own independent kink DP** — the
un-started sources past the cursor become a new unit. The existing SIGTERM →
stop-at-source-boundary → `StopKey` = last-source-consumed machinery carries
over unchanged; the only semantic shift is the cursor is a *source* boundary,
not an *output-key* boundary. Steal adds intermediate duplication (another
independent sub-DP), same category of cost as Option B's sharding — measured in
Phase 3.

## Milestones (red-first; each gate byte-identical, not approximate)

### Phase 0 — De-risk by measurement (no production code)
- **0.1 Duplication curve. DONE — NO-GO for Option B.** Measured
  (`experiments/kink_tm/kink_shard_probe.cpp`, H=8/12, `--keyrange` and
  `--hash`, gated byte-identical at every S): duplication grows
  `~S^0.7-0.8` with no plateau (1.5× at S=2 → 8.1× at S=32, H=12,
  key-range). Does not hold to the < ~2× bar at production shard counts
  (128-320). Full data: `results/kink-carry-shard-duplication.md`.
  **Decision taken: Option B rejected as scoped.** Next step is to scope
  Option A (per-stage sharding, H barriers/column — zero duplication) or a
  hybrid/analytic approach, NOT to proceed to Phase 1 on Option B.
- **0.2 Production record format.** (deferred — moot until a shard strategy
  passes 0.1; revisit once Option A or a hybrid is measured.) Confirm the ~3.6× intermediate factor and
  the per-worker RAM projection hold with **ranged u128 rows** (not the probe's
  full u64 rows) at H16 shape. Establishes the real bytes/intermediate-state.
- Deliverable: numbers appended to `results/kink-carry.md`; go/no-go on B.

### Phase 1 — Kink kernel as a `map_shard` variant (library only)
- Port `kinkSweep` into `map_shard_kink<W, Classifier>` in `core/`, consuming a
  source Run (a shard) and producing the **identical** `Run<W>` contract as
  `map_shard`. Reuse `Sig`, ranged rows, `foldSig` (end-of-column only),
  `completionLowerBound`, `canonicalizeSig`, the classifier hooks. Intermediates
  live in a private in-RAM open-addressing map (mixed-state key: boundary +
  carry byte + placed bit; never keyed for merge, never written).
- **Scope v1 = triangle only.** The holes path uses `sig.b[H+2]` for the Euler
  hole count, which the kink state needs for the carry — conflict. Holes stay on
  the column kernel (they are an a19/a20-era concern, off the a(30) path).
- Red-first tests: for random source shards at H=4..10, `map_shard_kink` output
  (end-of-column states, per-n counts, per-height T(n,H)) is byte-identical to
  `map_shard`. Orchestrator still calls the old path; this phase ships dark.

### Phase 2 — Wire behind `--kernel`, gate at a(20)
- `map_worker --kernel kink|column` (default column); `orchestrate --kernel`
  plumbed through `SweepConfig`. Worker reads its source shard, runs the kink
  kernel, writes the end-of-column Run as today. Merge, checkpoint (column
  boundary; kink is atomic within a column, so resume granularity is coarser —
  fine), telemetry unchanged.
- Work-stealing: cursor at source boundary (above). Reuse `StopKey` path.
- **Gate:** full a(20) `--kernel kink --compare` byte-matches the b-file AND a
  whole-column a(20) run — the entire triangle and every T(n,H) identical.

### Phase 3 — Validate at scale + tune (dalby)
- a(24) `--kernel kink --compare` on dalby (a24 is certified): byte-match the
  full triangle and every T(n,H) against banked `results/ns_a24/`. This run is
  simultaneously the **independent reimplementation** the a(23) validation plan
  ([[a23-readiness-and-validation]]) names as the only closure for the
  shared-enumeration-bug gap — so it retroactively hardens a(21)–a(29).
- Measure: real wall, per-height cost profile, intermediate RAM, and the unit
  sweet spot / overlap-heights / steal-grain under the *new* cost shape (map now
  cheap; the merge barrier and end-of-column volume dominate — retune from the
  column-kernel defaults).

### Phase 4 — Production a(30)+
- Only after the Phase-3 byte-match. Re-measure the ladder as each term lands;
  project a(31)–a(33). Expectation from `results/kink-carry.md`: a29's dominant
  H16 (~10⁶ cpu-s whole-column) drops to ~10³–10⁴ cpu-s; a(30)–a(33) go from
  days to hours on dalby. New wall = frontier RAM at D_H ~ 2.6^H (H≈n/2−const)
  plus u128 row bandwidth — a distant ceiling (~a35+).

## Correctness surface (the parts to watch in the port)
- Canonicalise boundary **and** carry together every stage; apply the R1 fold
  **only** at end-of-column, never to intermediates (the probe does both).
- Stranding check as the carry drops off (each stage and at column end): a
  carried component whose label appears nowhere else is unreachable → dead.
- Completion harvest at column start (closable = single component + both touch
  flags), identical to the column loop.
- Every record run keeps the standing bar: gate a(1..18) vs known, full a(20)
  `--compare` byte-match, a21–27 vs banked totals.

## What this moots (stop paying rent)
- Completion-prune tightening (queue #4): already closed at ~2–4%
  ([[completion-oracle]]); irrelevant here — the kink kernel deletes the mask
  enumeration the prune was shaving.
- The map micro-opt backlog (viableRec 91%, PGO, arg-pack): all scoped to the
  *whole-column* kernel; the kink kernel has no `forEachViableMask` hot loop.
- Spill/zstd on the frontier path: intermediates stay in RAM; only the
  (~1000× smaller) end-of-column frontier can spill, and only past the D_H RAM
  wall (~a35+). Spill becomes a distant-scale concern, not a per-term cost.
