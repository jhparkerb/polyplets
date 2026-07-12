# Work-stealing did not fire on a(32) — the H18 map straggler tail

**Date:** 2026-07-03. **Source data:** `results/ns_a32/cost_profile_dalby.tsv`,
and per-round `event=kink_round` / per-column `event=heartbeat` telemetry in
dalby's `runs/ns_a32/dalby/run.log`. **Status:** diagnosis banked, **not
deployed** (see Decision).

## Finding

a(32) ran with `--steal-grain 0.05` (work-stealing on) yet fired **zero steals**
across the entire run — all 558 heartbeats report `steals=0`, including every
column of H18, the dominant height. Meanwhile the top heights run badly
under-utilized, and it *worsens* with height:

| height | wall | avg cores busy (cpu_s/wall_s) | % of sweep |
|--------|------|------------------------------|-----------|
| H16 | 631s | 26.5 / 80 (33%) | 5.8% |
| H17 | 2010s | 19.9 / 80 (25%) | 18.4% |
| **H18** | **7516s** | **14.1 / 80 (18%)** | **68.8%** |

## Where the idle is: the late mid-column map stages, not merge

Each kink column runs 20 rounds: `seed` (mergeless) + H `stage{r}` rounds
(king-adjacency carry transfer, **stealable**) + `finalize`. Per-round telemetry
for the peak column **H18 col4** (731s):

| phase | wall | cpu | cores busy |
|-------|------|-----|-----------|
| map (20 rounds) | 469s | 6445s | **13.7 / 80** |
| merge (19 rounds) | 263s | 2193s | 8.3 / 80 |

The dominant waste is the **map straggler tail**, not merge. It concentrates in
the late stages: `stage10..stage17` each show `map_cpu` roughly *constant*
(~350 cpu-s) while `map_wall` *doubles* (25s → 52s) — the signature of a few
units grinding while ~300 sit idle. Those 8 stages spend **318s of map wall on
36s of actual work** (9/80 cores); ~280s per column is pure tail.

## Root cause (hypothesis): the eligibility floor is record-based, the tail is compute-based

`mapPhase` computes `grainRecs = 0.05 · frontier / cores ≈ 36k records` at H18.
`stealEligible` (sweep.go:914) gates first on **`rem > grainRecs`** — a victim
must have >36k *input records* remaining. But the late-stage stragglers have
`map_cpu` flat with `map_wall` growing: they are **compute-heavy on few
records** (a handful of pathological keys), so their *record* remainder falls
below the floor and they are filtered out **before** `stealScore` — the
wall-time ranker built for exactly this case (its own comment: "a compute-heavy
straggler ... can have few records remaining yet dominate the column tail") —
ever sees them. The eligibility gate is record-shaped; the stragglers are
compute-shaped. (This is distinct from the earlier maxn20 finding in
`scheduling.md`, which was the progress-pulse stride; here units are far above
the stride.)

## Open question — is the tail splittable? (decides whether any fix helps)

> **ANSWERED (see `results/utilization-fix-and-ceiling.md`):** effectively NO — via
> the current between-records mechanism the tail is not usefully splittable; the
> wall-estimate steal fix was built and bought ~nothing. Parking at a(34) was later
> lifted (a(35), a(36) since banked). Original probe follows:

Work-stealing splits a running straggler at a *record cursor*. If the tail is a
handful of heavy-but-separable key ranges, cursor-splitting divides the work and
the ~280s/column is recoverable (best case: H18 column ~731s → map_ideal 81s +
merge 263s ≈ 344s, roughly halving the dominant height → ~1/3 off a term's
wall). If instead a straggler is a *single* pathological key, splitting its
record cursor doesn't divide the compute inside that key — the tail is
fundamentally serial and no steal-fix helps (recoverable ≈ 0).

**This is not determinable from banked per-round logs** — it needs per-unit map
timing from one instrumented H18 column (which units carry the tail, and whether
their heaviness is one key or many). Cheap to get, not yet done.

## Decision (2026-07-03)

Not deployed. a(33)/a(34) run the a29-cell-validated trusted config; changing
`stealEligible` for a record run would require at-scale re-validation we don't
have deadline room for (close ~2026-07-06), and we are parking the term chase at
a(34). Banked here for any future a(35)+ push: the next step would be the
per-unit splittability probe above, and — if splittable — making steal
eligibility wall-estimate-based (reuse `stealScore`) instead of gating on raw
record remainder.
