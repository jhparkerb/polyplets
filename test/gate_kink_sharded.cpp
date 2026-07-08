// Design: sharded-private column sweep (core/kink_sharded.h) gate.
//
// Promotes experiments/bench_shard_column.cpp's multi-column chain
// validation to a permanent, always-run correctness gate. See
// core/kink_sharded.h's header comment for the full design and the
// correctness mechanism (permissiveBudget) this exists to protect.
//
// The bar that matters: NOT single-column intermediate-table byte
// equality (kinkPrivateShardSweep's own private stage-H tables, and even
// mergeAndFinalizeShardedColumn's "next column" output, can legitimately
// differ from a K=1 barrier-per-stage run's intermediate tables --
// completionLowerBound is a documented LOWER bound, so K=1's own
// ms-based admissibility prune already keeps some provably-uncompletable
// states; sharding can keep a slightly different set of the same kind of
// harmless dead weight). The real bar is the HARVESTED TRIANGLE ROW --
// the actual T(n,H) contributions that feed a(n) -- summed across a real
// multi-column chain, which must match a K=1 chain EXACTLY.
//
// NOT red-first for permissiveBudget specifically, despite trying: flipping
// core/kink_sharded.h's permissiveBudget to false (disabling the defense
// described in that header) does NOT make this gate fail, even with the
// tight-budget configs below added specifically to stress the boundary.
// See core/kink_sharded.h's "HONEST STATUS" note -- this doesn't mean the
// defense is unnecessary, it means no test case here actually exercises
// the failure mode it's theoretically protecting against. This gate DOES
// verify the core design decision (H+1 barriers -> 1 merge point) is
// correct, which is the primary thing it exists to check.

#include <cstdio>
#include <cstring>
#include <random>
#include <vector>

#include "core/classifier.h"
#include "core/kink.h"
#include "core/kink_column.h"
#include "core/kink_sharded.h"
#include "core/run.h"
#include "core/signature.h"

using W = u64;

static Sig randomColumnState(std::mt19937& rng, int H) {
  Sig s;
  std::memset(s.b, 0, SIGMAX);
  std::uniform_int_distribution<int> presence(0, 1);
  std::uniform_int_distribution<int> labelPick(1, std::max(1, H / 2));
  for (int i = 0; i < H; ++i)
    if (presence(rng)) s.b[i] = static_cast<unsigned char>(labelPick(rng));
  canonicalizeSig(s.b, H);
  s.b[H] = static_cast<unsigned char>(presence(rng));
  s.b[H + 1] = static_cast<unsigned char>(presence(rng));
  return s;
}

static Run<W> randomColumnTable(std::mt19937& rng, int H, int maxn, int n) {
  std::uniform_int_distribution<int> loPick(0, maxn - 1);
  std::uniform_int_distribution<int> cntPick(1, 5);
  Run<W> run;
  for (int i = 0; i < n; ++i) {
    RunRecord<W> r;
    r.sig = randomColumnState(rng, H);
    r.H = H;
    r.keyLen = H + 2;
    const int lo = loPick(rng);
    const int len = std::min(maxn - lo + 1, 1 + cntPick(rng) % 3);
    r.lo = static_cast<uint8_t>(lo);
    r.len = static_cast<uint8_t>(len);
    r.counts.resize(len);
    for (int j = 0; j < len; ++j) r.counts[j] = static_cast<W>(cntPick(rng));
    run.push_back(std::move(r));
  }
  sortRun(run);
  deduplicateRun(run);
  return run;
}

static std::vector<Run<W>> splitIntoShards(const Run<W>& src, int K) {
  std::vector<Run<W>> shards(K);
  const size_t n = src.size();
  for (int k = 0; k < K; ++k) {
    const size_t lo = n * static_cast<size_t>(k) / static_cast<size_t>(K);
    const size_t hi = n * static_cast<size_t>(k + 1) / static_cast<size_t>(K);
    shards[static_cast<size_t>(k)].assign(src.begin() + static_cast<long>(lo),
                                          src.begin() + static_cast<long>(hi));
  }
  return shards;
}

// Runs one column via the standard, unmodified barrier-per-stage path
// (K=1, today's production shape) -- the reference this gate checks
// sharding against.
static Run<W> referenceColumnStep(const Run<W>& src, int H, int maxn, bool fold,
                                   TriangleRow<W>& harvestOut) {
  Run<W> stage = kinkSeedStage0<W, ClassifyTriangle>(src, H, harvestOut);
  for (int r = 0; r < H; ++r) {
    KinkStageCfg cfg{H, maxn, r, 0, ""};  // permissiveBudget=false: the real ms
    stage = map_shard_stage(stage, cfg);
  }
  return kinkFinalizeColumn(stage, H, maxn, fold);
}

// Runs one column via the sharded-private design (core/kink_sharded.h).
static Run<W> shardedColumnStep(const Run<W>& src, int H, int maxn, bool fold,
                                 int K, TriangleRow<W>& harvestOut) {
  auto shards = splitIntoShards(src, K);
  std::vector<Run<W>> stageHTables;
  stageHTables.reserve(shards.size());
  for (auto& shard : shards) {
    if (shard.empty()) continue;
    TriangleRow<W> h(H, maxn);
    stageHTables.push_back(kinkPrivateShardSweep<W, ClassifyTriangle>(shard, H, maxn, h));
    for (int n = 0; n <= maxn; ++n) harvestOut.row[n] += h.row[n];
  }
  return mergeAndFinalizeShardedColumn(stageHTables, H, maxn, fold);
}

// The real correctness bar: chain several columns end to end and compare
// ACCUMULATED HARVESTED TRIANGLE ROWS (the actual a(n) inputs), not
// intermediate-table byte equality (see file header for why that's not
// the right check).
static void testMultiColumnChainMatchesBarrierPerStage() {
  struct ChainConfig { int H, maxn, numCols, K, seedOffset, n0; };
  std::vector<ChainConfig> configs = {
      {8, 12, 6, 8, 777, 200},
      {8, 12, 8, 16, 111, 200},
      {6, 10, 6, 4, 222, 150},
      {10, 15, 5, 8, 333, 300},
      {10, 15, 5, 32, 444, 300},
      {12, 18, 4, 16, 555, 500},
      // Tight budget stress: maxn close to H (small headroom past the
      // seed's own H cells), meant to actually exercise the mid-sweep
      // ms+1>maxn budget check's boundary.
      {8, 9, 4, 8, 666, 300},
      {10, 11, 4, 16, 888, 400},
      {12, 13, 3, 32, 999, 600},
  };

  for (auto& cc : configs) {
    std::mt19937 rng(20260708u + static_cast<unsigned>(cc.seedOffset));
    Run<W> frontier = randomColumnTable(rng, cc.H, cc.maxn, cc.n0);

    Run<W> k1Frontier = frontier;
    TriangleRow<W> k1Total(cc.H, cc.maxn);
    for (int col = 0; col < cc.numCols && !k1Frontier.empty(); ++col) {
      TriangleRow<W> h(cc.H, cc.maxn);
      Run<W> next = referenceColumnStep(k1Frontier, cc.H, cc.maxn, /*fold=*/true, h);
      for (int n = 0; n <= cc.maxn; ++n) k1Total.row[n] += h.row[n];
      k1Frontier = std::move(next);
    }

    Run<W> shFrontier = frontier;
    TriangleRow<W> shTotal(cc.H, cc.maxn);
    for (int col = 0; col < cc.numCols && !shFrontier.empty(); ++col) {
      TriangleRow<W> h(cc.H, cc.maxn);
      Run<W> next = shardedColumnStep(shFrontier, cc.H, cc.maxn, /*fold=*/true, cc.K, h);
      for (int n = 0; n <= cc.maxn; ++n) shTotal.row[n] += h.row[n];
      shFrontier = std::move(next);
    }

    if (k1Total.row != shTotal.row) {
      std::fprintf(stderr,
                   "gate_kink_sharded FAIL (multi-column-chain): H=%d maxn=%d "
                   "cols=%d K=%d seed=%d -- harvested triangle rows differ\n",
                   cc.H, cc.maxn, cc.numCols, cc.K, cc.seedOffset);
      for (int n = 0; n <= cc.maxn; ++n) {
        if (k1Total.row[n] != shTotal.row[n]) {
          std::fprintf(stderr, "  n=%d: barrier-per-stage=%llu sharded=%llu\n", n,
                       (unsigned long long)k1Total.row[n],
                       (unsigned long long)shTotal.row[n]);
        }
      }
      std::abort();
    }
  }
}

int main() {
  testMultiColumnChainMatchesBarrierPerStage();
  std::puts("gate_kink_sharded PASS");
}
