// kink_sharded.h — sharded-private column sweep (redesign branch).
//
// The standard kink-carry column sweep (core/kink_column.h's
// kinkSeedStage0/kinkFinalizeColumn, driven round-by-round by
// orchestrator/sweep.go's mapPhase/mergePhase) synchronizes ALL parallel
// workers at EVERY one of a column's H+1 rounds (seed, H mid-column stage
// transitions, finalize) -- each round is its own barrier: map phase, then
// a merge phase that combines every worker's output into one shared table
// before the next round can start. On narrow rounds (small frontiers, or
// late in a sweep where per-round work shrinks) that barrier overhead
// dominates -- the whole utilization investigation this branch grew out of
// (docs/utilization-bottleneck-log.md) found that no scheduling fix closes
// this: the barriers themselves are the floor.
//
// This header implements the alternative results/kink-carry.md's own
// "Caveats" section named but never measured: split a column's source
// frontier into K independent shards UP FRONT, run EACH shard through
// seed + ALL H mid-column stages PRIVATELY (no merge, no barrier at all
// during this phase -- each shard only ever sees its own records), then
// merge the K shards' stage-H tables EXACTLY ONCE, and run the standard,
// unmodified kinkFinalizeColumn once on the merged table. H+1 barriers
// become 1.
//
// CORRECTNESS -- read before touching this file:
//
// kinkStageTransition (core/kink.h:98) is not just consulted by the final
// admissibility prune -- it uses each record's own `ms` (minSize of its
// count-vec window) to gate whether a cell can be placed AT EVERY STAGE
// (`occupy && ms+1 > maxn` breaks the transition early). A shard's own,
// not-yet-cross-shard-merged window can have a narrower TRUE minSize than
// the fully-merged one would (another shard might hold the rest of that
// same canonical intermediate state's contributions) -- worked through by
// hand: if shard A holds a state's n=1..3 contributions and shard B holds
// the SAME canonical state's n=5..7 contributions, shard B's own ms=5
// could wrongly trip the budget break even though the TRUE combined ms=1
// would have allowed it, silently dropping shard B's occupy=1 branch --
// not a redundant-but-reconcilable duplicate, an actually lost
// contribution to the final count.
//
// The defense: every stage transition during the private per-shard sweep
// uses KinkStageCfg::permissiveBudget (core/kink.h) to force ms=0, so the
// mid-sweep budget check can never wrongly fire. This costs extra work
// (states a real, tighter ms would have safely pruned early now survive to
// the merge point instead).
//
// HONEST STATUS: this is a real, hand-verified mathematical concern, kept
// on as the safe default -- but despite deliberately trying (test/
// gate_kink_sharded.cpp includes tight-budget configs with maxn close to
// H specifically to stress the `ms+1>maxn` boundary), no test case run so
// far actually demonstrates a harvest-level DIFFERENCE between
// permissiveBudget=true and false. Either the failure mode is real but
// narrow enough that random sampling keeps missing it, or there's a
// reason (not yet found) why it doesn't manifest in practice. Do not
// interpret "no test caught it" as "it's safe to remove" -- the
// asymmetry is stark (silent undercounting vs. some wasted compute), so
// this stays on until someone either hand-constructs a concrete
// triggering case or proves the concern is unfounded. Don't "optimize"
// this back to the real per-shard ms without doing one of those two
// things first.
//
// The one merge point (this header's mergeAndFinalizeShardedColumn) uses
// the UNMODIFIED core/kink_column.h::kinkFinalizeColumn -- its ms-based
// admissibility prune is correct there because by that point every
// canonical mixed state has been fully combined across all K shards, so
// its ms reflects the true, complete window, exactly like the standard
// K=1 barrier-per-stage path always saw.
//
// VALIDATION: experiments/bench_shard_column.cpp's multi-column harvested-
// triangle-row chain test (not just single-column intermediate-table
// byte-equality, which is NOT the right correctness bar -- see that file's
// header comment for why) passed across 6 configurations (H=6..12,
// maxn=10..18, K=4..32, 4-8 chained columns). test/gate_kink_sharded.cpp
// is the same check promoted to a real, permanent gate.
//
// STILL OPEN before this can be trusted for a real term: real (not
// synthetic-random) frontier data at production scale, the holes path
// (untouched, triangle-only for now, same restriction as the rest of the
// kink kernel), and per-shard duplication cost measured against REAL RGS-
// skewed frontiers rather than uniform-random test data (duplication is
// expected to be worse on real data given everything else found this
// session about collision skew deepening into a sweep).

#pragma once

#include "core/kink.h"
#include "core/kink_column.h"
#include "core/run.h"

// Runs the seed + H mid-column private stage transitions for ONE shard of a
// column's source frontier (keyLen H+2), entirely independently of any
// other shard. Returns that shard's own stage-H mixed-state table (keyLen
// H+4, NOT finalized -- the caller must merge multiple shards' outputs and
// call kinkFinalizeColumn, see mergeAndFinalizeShardedColumn below).
// Harvests (classifies) on the way through exactly as kinkSeedStage0
// always has -- harvest is a per-record, purely additive accumulation, so
// summing each shard's own Output across shards reproduces the same total
// a K=1 sweep would harvest (unlike the stage-H table itself, harvest
// needs no merge-before-correctness treatment).
template <class W, class Classifier, class Output>
Run<W> kinkPrivateShardSweep(const Run<W>& srcShard, int H, int maxn,
                              Output& out_classified) {
  Run<W> stage = kinkSeedStage0<W, Classifier>(srcShard, H, out_classified);
  for (int r = 0; r < H; ++r) {
    KinkStageCfg cfg{H, maxn, r, 0, "", /*permissiveBudget=*/true};
    stage = map_shard_stage(stage, cfg);
  }
  return stage;
}

// The one synchronization point: merges K shards' stage-H tables (each
// produced by kinkPrivateShardSweep) into one fully cross-shard-combined
// table, then runs the standard, UNMODIFIED kinkFinalizeColumn on it
// exactly once. This is where kinkFinalizeColumn's real, precise ms-based
// admissibility prune runs -- correctly, since by this point every
// canonical mixed state has its true, complete window.
template <class W>
Run<W> mergeAndFinalizeShardedColumn(std::vector<Run<W>>& shardStageH, int H,
                                      int maxn, bool fold) {
  Run<W> merged;
  size_t total = 0;
  for (const auto& s : shardStageH) total += s.size();
  merged.reserve(total);
  for (auto& s : shardStageH) {
    merged.insert(merged.end(), s.begin(), s.end());
  }
  sortRun(merged);
  deduplicateRun(merged);  // the ONE cross-shard merge point
  return kinkFinalizeColumn(merged, H, maxn, fold);
}
