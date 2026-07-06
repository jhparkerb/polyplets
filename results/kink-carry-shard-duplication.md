# Design 14 Phase 0.1: shard duplication curve — Option B is NO-GO

**2026-07-02.** `experiments/kink_tm/kink_shard_probe.cpp`. Measures the
duplication cost of Design 14's Option B (shard sources by key, run the full
per-shard kink stage-DP privately, merge only end-of-column states).

## Method

At each column, partition the source frontier into S shards two ways:
`--hash` (hash(sig)%S, worst-case scatter) and `--keyrange` (sort by key,
cut into S contiguous ranges — what production actually does). Run the
identical stage-DP on each shard independently; sum end-of-column output
(gated byte-identical to the unsharded S=1 run at every S tested).

## Result — duplication grows with S, does not saturate

`--keyrange` (the realistic mode):

| S | H=8 stageSizeSum dup | H=12 stageSizeSum dup |
|---|---|---|
| 2  | 1.44× | 1.52× |
| 4  | 2.07× | 2.32× |
| 8  | 2.90× | 3.52× |
| 16 | 3.91× | 5.38× |
| 32 | —     | 8.08× |

`--hash` is worse at every S (e.g. H=12/S=32: 12.7× vs 8.1×), confirming
key-range is the right production model, but the trend is the same shape:
roughly `S^0.7-0.8` growth, worsening with H, no sign of a plateau.

## Verdict

**Option B as scoped in design 14 is NO-GO at realistic shard counts.**
Production shard counts are `cores × unit_mult` — 128–320 on dalby/ayr.
Extrapolating the H=12 trend to S~200 puts duplication in the tens-to-~50×
range, which eats most or all of the kernel's raw 29–55× win before any
production shard count is reached. The design doc's own decision rule
("duplication < ~2× at target shard counts → Option B; else scope Option A")
resolves cleanly: **fall back toward Option A** (per-stage sharding, H
barriers per column) or a hybrid, not straight Option B.

## Why it doesn't saturate

Each shard's private stage-DP independently rediscovers every intermediate
mixed-boundary state reachable from ITS sources — key-range locality does not
translate into connectivity locality (the same all-to-all-scatter finding
from [[merge-shuffle-ranking-locality]] / designs/10 applies here too: the
transition graph mixes regardless of key order). More shards → more
independent rediscovery, with no cap.

## What this does NOT kill

The core kink-carry win (per-source cost `2H·intermediate` vs `Σ masks`) is
untouched — it's a serial, per-source-state result, independent of how
sources get sharded. Only the *shard-and-go-parallel-for-free* assumption
(Option B) is refuted. The path to parallel kink is now:
- **Option A** (H barriers per column): zero duplication, exact — cost is H
  small merge/repartition steps per column instead of 1. Given intermediate
  stage sizes are a flat ~3.6× the frontier (not `Σ masks`), H tiny barriers
  may still be far cheaper than today's one `Σ masks`-sized barrier. Needs
  its own measurement (barrier overhead × H vs the win).
- **Hybrid**: coarse-grained sharding (small S, duplication still ~1.5-2×)
  to fill cores partially, or a shard count that grows only sublinearly with
  core count, accepting some idle cores in exchange for bounded duplication.
- **Re-derive the duplication bound analytically** from the state graph's
  mixing rate before picking a shard count, rather than shard-and-measure.

Design 14 needs a Phase 0.1-informed redesign before Phase 1 starts; see the
doc's updated status.
