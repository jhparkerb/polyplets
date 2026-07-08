// bench_shard_column.cpp -- measures the central unknown named (but never
// measured) in results/kink-carry.md's "Caveats" section: what does it cost
// to remove the H-1 barrier-merge synchronizations inside one column's
// stage sweep, replacing them with fully independent per-shard private
// sweeps (kinkSeedStage0 -> H stages -> kinkFinalizeColumn, run to
// completion with NO cross-shard merging until a single final reduce)?
//
// Barrier-per-stage (K=1, today's production shape, restated as a
// baseline): one shared stage table, merged/deduplicated at every one of
// the H+1 round boundaries.
//
// Sharded-private (K>1): split the initial column input into K disjoint
// key-range pieces UP FRONT, run each piece through the ENTIRE column
// pipeline independently (no merge until the very end), concatenate the K
// finalized outputs, sort+dedup ONCE. Correctness (final triangle row
// must match K=1 exactly) is necessary but not sufficient -- the real
// question is DUPLICATION: how much MORE total record volume gets
// produced across all H stages, summed over all K shards, vs the K=1
// baseline. A state reachable from multiple shards gets its own future
// computed redundantly once per reaching shard, and reachability from
// multiple shards should get MORE likely deeper into the sweep (more
// cells placed = more canonicalization collapse = the same
// collision-skew mechanism already found this session for map-unit
// imbalance) -- so duplication is expected to compound, not stay flat.
// This experiment measures whether it's bounded or explodes.
//
// Build: c++ -std=c++20 -O3 -I. experiments/bench_shard_column.cpp -o /tmp/bench_shard
// Run:   /tmp/bench_shard

#include <chrono>
#include <cstdio>
#include <cstring>
#include <random>
#include <vector>

#include "core/classifier.h"
#include "core/kink.h"
#include "core/kink_column.h"
#include "core/run.h"
#include "core/signature.h"

using W = u64;
using Clock = std::chrono::steady_clock;

// Same random end-of-column boundary generator as test/gate_kink_column.cpp
// (kept independent, not #include'd from test/, to keep this a pure
// throwaway local experiment with zero gate coupling).
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

// Runs one column's full pipeline (seed -> H stages -> finalize) over
// `src`, returning the finalized next-column table and the total record
// volume summed across all H+1 rounds' output tables (the compute-cost
// proxy: each round's output size is exactly how many records the NEXT
// round has to process, mirroring real map_wall_s's dependence on
// frontier size measured all session).
struct ColumnRunResult {
  Run<W> next;
  TriangleRow<W> harvested;
  size_t totalRecordVolume = 0;
};

// Local copy of kinkFinalizeColumn (core/kink_column.h) with the
// admissibility prune (`ms + completionLowerBound(t.b, H) > maxn`)
// REMOVED -- testing the hypothesis that this per-record, per-shard prune
// decision is exactly what's wrong with the sharded-private approach:
// `ms = rec.minSize()` depends on a record's OWN count-vec window, which is
// only PARTIAL in a private shard (other shards may hold the rest of that
// same canonical state's contributions). Deferring the prune to AFTER the
// cross-shard merge means every shard's raw survivors get carried through
// uncut; the prune runs exactly once, on the fully-combined window, exactly
// like the K=1 baseline's own single kinkFinalizeColumn call sees.
template <class W>
Run<W> kinkFinalizeColumnDeferredPrune(const Run<W>& stageH, int H, int maxn, bool fold) {
  (void)maxn;  // no admissibility prune here -- deferred to the post-merge pass
  const int kLen = H + 2;
  Run<W> next;
  next.reserve(stageH.size());
  for (const auto& rec : stageH) {
    if (!rec.sig.b[H + 3]) continue;
    const unsigned char outgoing = rec.sig.b[H + 2];
    Sig t = rec.sig;
    t.b[H + 2] = 0;
    t.b[H + 3] = 0;
    if (outgoing != 0 && !labelInMixedState(t, H, outgoing)) continue;
    const int ms = rec.minSize();
    if (ms < 0) continue;
    canonicalizeSig(t.b, H);
    // NO admissibility prune here -- deferred to the post-merge pass.
    if (fold) foldSig(t, H);
    RunRecord<W> succ;
    succ.sig = t;
    succ.H = H;
    succ.keyLen = kLen;
    succ.lo = rec.lo;
    succ.len = rec.len;
    succ.counts = rec.counts;
    next.push_back(std::move(succ));
  }
  sortRun(next);
  deduplicateRun(next);
  return next;
}

// Applies the admissibility prune once, to an already fully-merged table.
template <class W>
Run<W> applyAdmissibilityPrune(const Run<W>& src, int H, int maxn) {
  Run<W> out;
  out.reserve(src.size());
  for (auto rec : src) {
    // Per-n admissibility, not per-record ms: n+completionLowerBound is
    // stricter for larger n, so a window spanning multiple n can have SOME
    // individually admissible and others not -- ms-only pruning (checking
    // just the smallest n) either wrongly drops the whole record (if a
    // shard's own partial window's ms looks inadmissible even though the
    // true cross-shard-combined ms would have passed) or, if deferred,
    // wrongly ADMITS large-n entries that individually violate budget just
    // because a smaller n in the same window happened to pass. Zero each
    // individually-inadmissible n instead of an all-or-nothing decision.
    const int bound = completionLowerBound(rec.sig.b, H);
    for (int i = 0; i < rec.len; ++i) {
      const int n = static_cast<int>(rec.lo) + i;
      if (n + bound > maxn) rec.counts[i] = W{0};
    }
    // Trim the window to [first nonzero, last nonzero] so the on-disk shape
    // matches production's kinkFinalizeColumn exactly -- a wide window with
    // zeroed edges is logically equivalent but not byte-comparable, and
    // real disk/merge cost scales with window width, so trimming isn't
    // just cosmetic.
    int first = -1, last = -1;
    for (int i = 0; i < rec.len; ++i) {
      if (rec.counts[i] != W{0}) {
        if (first < 0) first = i;
        last = i;
      }
    }
    if (first < 0) continue;  // everything pruned
    if (first > 0 || last < rec.len - 1) {
      rec.lo = static_cast<uint8_t>(static_cast<int>(rec.lo) + first);
      rec.len = static_cast<uint8_t>(last - first + 1);
      rec.counts.assign(rec.counts.begin() + first, rec.counts.begin() + last + 1);
    }
    out.push_back(std::move(rec));
  }
  return out;
}

static ColumnRunResult runColumnPrivate(const Run<W>& src, int H, int maxn, bool fold,
                                         bool deferPrune) {
  ColumnRunResult result{{}, TriangleRow<W>(H, maxn), 0};
  Run<W> stage = kinkSeedStage0<W, ClassifyTriangle>(src, H, result.harvested);
  result.totalRecordVolume += stage.size();
  for (int r = 0; r < H; ++r) {
    KinkStageCfg cfg{H, maxn, r, 0, ""};
    stage = map_shard_stage(stage, cfg);
    result.totalRecordVolume += stage.size();
  }
  result.next = deferPrune ? kinkFinalizeColumnDeferredPrune(stage, H, maxn, fold)
                            : kinkFinalizeColumn(stage, H, maxn, fold);
  result.totalRecordVolume += result.next.size();
  return result;
}

// Runs the seed + H mid-column stages PRIVATELY per shard (no barrier at
// all during this phase -- each shard's stage table only ever sees its own
// records), then merges ALL shards' stage-H tables ONCE (a single
// cross-shard sort+dedup, giving finalize's ms-based prune the SAME full
// picture kinkFinalizeColumn always sees for K=1), then runs the
// STANDARD, unmodified kinkFinalizeColumn exactly once on the merged
// table. This is the "one synchronization point instead of H+1" design:
// H-1 of the H+1 round barriers are eliminated, only the seed->stage0 and
// stageH->finalize boundaries still see cross-shard data.
struct ShardedMergeBeforeFinalizeResult {
  Run<W> next;
  TriangleRow<W> harvested;
  size_t totalRecordVolume = 0;
};

// Local copy of core/kink.h's map_shard_stage with ms forced to 0 (the most
// permissive possible value: `occupy && ms+1 > maxn` can never trip, so the
// occupy=1 branch is always attempted). Root cause found by reading
// kinkStageTransition directly: `ms` is NOT just used by the final
// admissibility prune -- it gates the budget check INSIDE the transition
// itself, at EVERY mid-column stage (core/kink.h:102). A shard's own
// narrower, pre-cross-shard-merge window can have a LARGER true ms than the
// fully-combined window would, wrongly tripping the budget break and
// silently DROPPING a valid occupy=1 transition -- not a redundant-but-
// reconcilable duplicate, an actual lost path. Forcing ms=0 during the
// private per-shard sweep makes the budget check permissive everywhere
// (never wrongly prunes), deferring ALL precision to the one real,
// fully-merged admissibility prune inside the unmodified kinkFinalizeColumn
// at the very end. Costs extra work processing states a real ms would have
// safely skipped early; the question is how much.
template <class W>
Run<W> map_shard_stage_permissive(const Run<W>& src, const KinkStageCfg& cfg) {
  const int H = cfg.H;
  const int maxn = cfg.maxn;
  const int r = cfg.stage;
  const int kLen = kinkKeyLen(H);
  Run<W> buf;
  buf.reserve(src.size() * 2);
  for (const auto& rec : src) {
    if (rec.minSize() < 0) continue;
    kinkStageTransition(rec.sig, H, r, /*ms=*/0, maxn, [&](const Sig& t, int shift) {
      const int new_lo = static_cast<int>(rec.lo) + shift;
      if (new_lo > maxn) return;
      const int new_len = std::min<int>(rec.len, maxn - new_lo + 1);
      RunRecord<W> succ;
      succ.sig = t;
      succ.H = H;
      succ.keyLen = kLen;
      succ.lo = static_cast<uint8_t>(new_lo);
      succ.len = static_cast<uint8_t>(new_len);
      succ.counts.assign(rec.counts.begin(), rec.counts.begin() + new_len);
      buf.push_back(std::move(succ));
    });
  }
  sortRun(buf);
  deduplicateRun(buf);
  return buf;
}

static ShardedMergeBeforeFinalizeResult runShardedMergeBeforeFinalizePermissive(
    const std::vector<Run<W>>& shards, int H, int maxn, bool fold) {
  ShardedMergeBeforeFinalizeResult result{{}, TriangleRow<W>(H, maxn), 0};
  Run<W> mergedStageH;
  for (auto& shard : shards) {
    if (shard.empty()) continue;
    TriangleRow<W> h(H, maxn);
    Run<W> stage = kinkSeedStage0<W, ClassifyTriangle>(shard, H, h);
    result.totalRecordVolume += stage.size();
    for (int r = 0; r < H; ++r) {
      KinkStageCfg cfg{H, maxn, r, 0, ""};
      stage = map_shard_stage_permissive(stage, cfg);
      result.totalRecordVolume += stage.size();
    }
    for (int n = 0; n <= maxn; ++n) result.harvested.row[n] += h.row[n];
    mergedStageH.insert(mergedStageH.end(), stage.begin(), stage.end());
  }
  sortRun(mergedStageH);
  deduplicateRun(mergedStageH);
  result.totalRecordVolume += mergedStageH.size();
  result.next = kinkFinalizeColumn(mergedStageH, H, maxn, fold);  // unmodified, real prune
  result.totalRecordVolume += result.next.size();
  return result;
}

// Splits `src` into K contiguous, roughly-equal-count pieces by index (src
// is already sorted, so this is a valid disjoint key-range split -- the
// same shape SampleKeysMulti produces in production, simplified since this
// experiment doesn't need the .idx-sidecar machinery).
static std::vector<Run<W>> splitIntoShards(const Run<W>& src, int K) {
  std::vector<Run<W>> shards(K);
  const size_t n = src.size();
  for (int k = 0; k < K; ++k) {
    const size_t lo = n * k / K;
    const size_t hi = n * (k + 1) / K;
    shards[k].assign(src.begin() + static_cast<long>(lo), src.begin() + static_cast<long>(hi));
  }
  return shards;
}

static double elapsedMs(Clock::time_point t0) {
  return std::chrono::duration<double, std::milli>(Clock::now() - t0).count();
}

int main() {
  std::mt19937 rng(20260708u);

  struct Config { int H, maxn, n; };
  std::vector<Config> configs = {
      {8, 12, 400}, {10, 14, 800}, {12, 16, 1600},
  };

  for (auto& c : configs) {
    Run<W> src = randomColumnTable(rng, c.H, c.maxn, c.n);
    std::printf("=== H=%d maxn=%d input=%zu records ===\n", c.H, c.maxn, src.size());

    // K=1 baseline: today's barrier-per-stage shape (one shared table, no
    // splitting at all -- this IS the merged-every-round path).
    auto t0 = Clock::now();
    ColumnRunResult base = runColumnPrivate(src, c.H, c.maxn, /*fold=*/true, /*deferPrune=*/false);
    double baseMs = elapsedMs(t0);
    std::printf("K=1  (barrier-per-stage) : wall=%.2fms  total_record_volume=%zu  final=%zu\n",
                baseMs, base.totalRecordVolume, base.next.size());

    // Sanity check: does deferring the prune to a post-merge pass change K=1's
    // OWN answer (no sharding at all -- isolates whether prune-timing itself
    // is order-sensitive, independent of sharding)?
    {
      ColumnRunResult k1d = runColumnPrivate(src, c.H, c.maxn, /*fold=*/true, /*deferPrune=*/true);
      Run<W> k1dPruned = applyAdmissibilityPrune(k1d.next, c.H, c.maxn);
      bool same = (k1dPruned.size() == base.next.size());
      if (same) {
        for (size_t i = 0; i < k1dPruned.size() && same; ++i) {
          if (std::memcmp(k1dPruned[i].sig.b, base.next[i].sig.b, SIGMAX) != 0 ||
              k1dPruned[i].counts != base.next[i].counts) {
            same = false;
          }
        }
      }
      std::printf("K=1  deferred-prune vs early-prune (no sharding): %s (sizes %zu vs %zu)\n",
                  same ? "SAME" : "DIFFERENT", k1dPruned.size(), base.next.size());
    }

    for (int K : {2, 4, 8, 16, 32, 64}) {
      if (static_cast<size_t>(K) > src.size()) break;
      auto shards = splitIntoShards(src, K);

      auto tK0 = Clock::now();
      ShardedMergeBeforeFinalizeResult r =
          runShardedMergeBeforeFinalizePermissive(shards, c.H, c.maxn, /*fold=*/true);
      double kMs = elapsedMs(tK0);

      bool harvestOk = (r.harvested.row == base.harvested.row);
      if (!harvestOk) {
        for (int n = 0; n <= c.maxn; ++n) {
          if (r.harvested.row[n] != base.harvested.row[n]) {
            std::printf("  harvest mismatch at n=%d: sharded=%llu base=%llu\n",
                        n, (unsigned long long)r.harvested.row[n],
                        (unsigned long long)base.harvested.row[n]);
          }
        }
      }
      bool finalOk = (r.next.size() == base.next.size());
      if (!finalOk) {
        std::printf("  final size mismatch: sharded=%zu base=%zu\n",
                    r.next.size(), base.next.size());
      }
      if (finalOk) {
        int shown = 0;
        for (size_t i = 0; i < r.next.size(); ++i) {
          bool sigDiff = std::memcmp(r.next[i].sig.b, base.next[i].sig.b, SIGMAX) != 0;
          bool countsDiff = r.next[i].counts != base.next[i].counts;
          if (sigDiff || countsDiff) {
            finalOk = false;
            if (shown++ < 5) {
              std::printf("  mismatch at i=%zu: sigDiff=%d countsDiff=%d\n", i, sigDiff, countsDiff);
            }
          }
        }
      }

      const double dupFactor = base.totalRecordVolume
                                    ? double(r.totalRecordVolume) / double(base.totalRecordVolume)
                                    : 0.0;
      std::printf("K=%-3d(shard,permissive-ms,merge-before-finalize): wall=%.2fms  total_record_volume=%zu  "
                  "dup_factor=%.2fx  correct=%s%s\n",
                  K, kMs, r.totalRecordVolume, dupFactor,
                  (harvestOk && finalOk) ? "YES" : "NO",
                  (harvestOk && finalOk) ? "" : "  <-- MISMATCH");
    }
    std::printf("\n");
  }

  // ─── Multi-column chain: does the "final table" mismatch actually matter? ──
  //
  // Every single-column test above shows harvestOk=YES (the a(n)-contributing
  // triangle row matches exactly) even when the intermediate "next column"
  // table differs byte-for-byte from K=1's. completionLowerBound is
  // documented as a LOWER bound (an underestimate of true remaining cost),
  // so ms-only pruning (production's real behavior) is EXPECTED to
  // sometimes keep entries a stricter per-n check would drop -- entries
  // that are still mathematically provably unable to ever complete, just
  // not caught by this specific conservative estimate. That would make the
  // observed "final" mismatches wasted-compute noise, not a correctness
  // bug -- but only a real multi-column chain proves it, since a kept
  // "should be dead" record becomes the INPUT to the next column, and
  // could behave differently there instead of just sitting inert.
  //
  // This chains several columns using ONLY the sharded, merge-before-
  // finalize approach, and checks the accumulated harvested triangle rows
  // (the actual a(n) inputs) against a pure K=1 chain over the SAME number
  // of columns -- the real end-to-end correctness bar.
  struct ChainConfig { int H, maxn, numCols, K, seedOffset, n0; };
  std::vector<ChainConfig> chainConfigs = {
      {8, 12, 6, 8, 777, 200},
      {8, 12, 8, 16, 111, 200},
      {6, 10, 6, 4, 222, 150},
      {10, 15, 5, 8, 333, 300},
      {10, 15, 5, 32, 444, 300},
      {12, 18, 4, 16, 555, 500},
  };
  bool anyFailed = false;
  for (auto& cc : chainConfigs) {
    std::mt19937 chainRng(20260708u + static_cast<unsigned>(cc.seedOffset));
    Run<W> frontier = randomColumnTable(chainRng, cc.H, cc.maxn, cc.n0);

    Run<W> k1Frontier = frontier;
    TriangleRow<W> k1Total(cc.H, cc.maxn);
    for (int col = 0; col < cc.numCols && !k1Frontier.empty(); ++col) {
      ColumnRunResult r = runColumnPrivate(k1Frontier, cc.H, cc.maxn, /*fold=*/true, /*deferPrune=*/false);
      for (int n = 0; n <= cc.maxn; ++n) k1Total.row[n] += r.harvested.row[n];
      k1Frontier = std::move(r.next);
    }

    Run<W> shFrontier = frontier;
    TriangleRow<W> shTotal(cc.H, cc.maxn);
    for (int col = 0; col < cc.numCols && !shFrontier.empty(); ++col) {
      auto shards = splitIntoShards(shFrontier, cc.K);
      ShardedMergeBeforeFinalizeResult r =
          runShardedMergeBeforeFinalizePermissive(shards, cc.H, cc.maxn, /*fold=*/true);
      for (int n = 0; n <= cc.maxn; ++n) shTotal.row[n] += r.harvested.row[n];
      shFrontier = std::move(r.next);
    }

    bool chainOk = (k1Total.row == shTotal.row);
    if (!chainOk) anyFailed = true;
    std::printf("Chain H=%-2d maxn=%-2d cols=%-2d K=%-3d seed=%-4d: %s\n",
                cc.H, cc.maxn, cc.numCols, cc.K, cc.seedOffset,
                chainOk ? "CORRECT" : "MISMATCH <-- REAL BUG");
    if (!chainOk) {
      for (int n = 0; n <= cc.maxn; ++n) {
        if (k1Total.row[n] != shTotal.row[n]) {
          std::printf("  n=%d: K=1=%llu sharded=%llu\n", n,
                      (unsigned long long)k1Total.row[n], (unsigned long long)shTotal.row[n]);
        }
      }
    }
  }
  std::printf("\n=== OVERALL: %s ===\n", anyFailed ? "AT LEAST ONE CHAIN FAILED" : "ALL CHAINS CORRECT");

  return 0;
}
