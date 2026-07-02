// Design 14 Phase 1 gate: map_shard_stage (core/kink.h) ported correctly from
// the kink-carry probe's per-stage transition (kinkStageTransition, shared
// with experiments/kink_tm/kink_tm.cpp -- see that file's kinkSweep()).
//
// map_shard_stage adapts kinkStageTransition from single dense per-state
// count vectors to the production ranged RunRecord<W> windowed format (the
// same lo/len shift-and-clip adaptation core/mapreduce.h's map_shard applies
// to forEachViableMask). The porting risk lives entirely in that windowing:
// this gate builds random stage-table shards at H=4..10, and for each checks
// TWO independent properties against ground truth and against each other:
//
//   1. Ground truth: expand every source record's ranged window to a dense
//      per-n vector, apply kinkStageTransition directly (no windowing), and
//      compare the accumulated dense result to map_shard_stage's ranged
//      output (also expanded to dense for comparison). Byte-identical.
//   2. Shard invariance (the actual Option A parallelism claim): splitting
//      the source table into shards, running map_shard_stage on each shard
//      independently, and merging via mergeRuns must produce the exact same
//      sorted Run as running map_shard_stage on the whole table at once.

#include <algorithm>
#include <cassert>
#include <cstdio>
#include <cstring>
#include <map>
#include <random>
#include <vector>

#include "core/kink.h"
#include "core/mapreduce.h"
#include "core/run.h"
#include "core/signature.h"

using W = u64;

// Comparator over the first `keyLen` sig bytes (memcmp order), for std::map.
struct SigLess {
  int keyLen;
  bool operator()(const Sig& a, const Sig& b) const {
    return sigCmp(a.b, b.b, keyLen) < 0;
  }
};
using DenseMap = std::map<Sig, std::vector<W>, SigLess>;

// Build a structurally plausible random mixed-state Sig: a random boundary
// partition (canonicalized), a carry that is either empty, an existing
// boundary label (the common case), or a label absent from the boundary
// (exercises the stranding-on-drop path), and random touch/placed flags.
static Sig randomMixedState(std::mt19937& rng, int H) {
  Sig s;
  std::memset(s.b, 0, SIGMAX);
  std::uniform_int_distribution<int> presence(0, 1);
  std::uniform_int_distribution<int> labelPick(1, std::max(1, H / 2));
  for (int i = 0; i < H; ++i)
    if (presence(rng)) s.b[i] = static_cast<unsigned char>(labelPick(rng));
  canonicalizeSig(s.b, H);

  std::vector<unsigned char> present;
  for (int i = 0; i < H; ++i)
    if (s.b[i]) present.push_back(s.b[i]);

  std::uniform_int_distribution<int> carryMode(0, 2);
  const int mode = present.empty() ? 0 : carryMode(rng);
  if (mode == 1) {
    std::uniform_int_distribution<size_t> pick(0, present.size() - 1);
    s.b[H + 2] = present[pick(rng)];
  } else if (mode == 2) {
    s.b[H + 2] = static_cast<unsigned char>(
        *std::max_element(present.begin(), present.end()) + 1);  // dangling
  }
  s.b[H] = static_cast<unsigned char>(presence(rng));
  s.b[H + 1] = static_cast<unsigned char>(presence(rng));
  s.b[H + 3] = static_cast<unsigned char>(presence(rng));
  canonMixed(s, H);
  return s;
}

// Build a random shard-table Run<W> of `n` records at height H, keyed on the
// mixed-state (keyLen H+4), with narrow ranged windows within [0, maxn].
static Run<W> randomStageTable(std::mt19937& rng, int H, int maxn, int n) {
  const int kLen = kinkKeyLen(H);
  std::uniform_int_distribution<int> loPick(0, maxn - 1);
  std::uniform_int_distribution<int> cntPick(1, 5);
  Run<W> run;
  for (int i = 0; i < n; ++i) {
    RunRecord<W> r;
    r.sig = randomMixedState(rng, H);
    r.H = H;
    r.keyLen = kLen;
    const int lo = loPick(rng);
    const int len = std::min(maxn - lo + 1, 1 + cntPick(rng) % 3);
    r.lo = static_cast<uint8_t>(lo);
    r.len = static_cast<uint8_t>(len);
    r.counts.resize(len);
    for (int j = 0; j < len; ++j) r.counts[j] = static_cast<W>(cntPick(rng));
    run.push_back(std::move(r));
  }
  return run;
}

// Expand a Run<W> into a dense sig -> counts[0..maxn] map, for comparison.
static DenseMap toDense(const Run<W>& run, int H, int maxn) {
  DenseMap out(SigLess{kinkKeyLen(H)});
  for (const auto& r : run) {
    auto& dst = out[r.sig];
    if (dst.empty()) dst.assign(maxn + 1, W{0});
    for (int i = 0; i < r.len; ++i) {
      const int n = static_cast<int>(r.lo) + i;
      if (n <= maxn) dst[n] += r.counts[i];
    }
  }
  return out;
}

// Ground truth: apply kinkStageTransition directly to every source record's
// dense-expanded window (no RunRecord windowing at all).
static DenseMap referenceStageStep(const Run<W>& src, int H, int r, int maxn) {
  DenseMap ref(SigLess{kinkKeyLen(H)});
  for (const auto& rec : src) {
    std::vector<W> dense(maxn + 1, W{0});
    for (int i = 0; i < rec.len; ++i) {
      const int n = static_cast<int>(rec.lo) + i;
      if (n <= maxn) dense[n] = rec.counts[i];
    }
    const int ms = rec.minSize();
    if (ms < 0) continue;
    kinkStageTransition(rec.sig, H, r, ms, maxn, [&](const Sig& t, int shift) {
      auto& dst = ref[t];
      if (dst.empty()) dst.assign(maxn + 1, W{0});
      for (int n = 0; n + shift <= maxn; ++n)
        if (dense[n]) dst[n + shift] += dense[n];
    });
  }
  return ref;
}

static void assertDenseEqual(const DenseMap& a, const DenseMap& b,
                             const char* what) {
  if (a.size() != b.size()) {
    std::fprintf(stderr, "gate_kink FAIL (%s): key count %zu vs %zu\n", what,
                a.size(), b.size());
    std::abort();
  }
  auto ia = a.begin();
  auto ib = b.begin();
  for (; ia != a.end(); ++ia, ++ib) {
    if (std::memcmp(ia->first.b, ib->first.b, SIGMAX) != 0 ||
        ia->second != ib->second) {
      std::fprintf(stderr, "gate_kink FAIL (%s): record mismatch\n", what);
      std::abort();
    }
  }
}

static void testAgainstGroundTruthAndSharding() {
  std::mt19937 rng(20260702u);
  for (int H = 4; H <= 10; ++H) {
    const int maxn = H + 4;
    for (int stage : {0, H / 2, H - 1}) {
      for (int trial = 0; trial < 3; ++trial) {
        Run<W> src = randomStageTable(rng, H, maxn, 30);
        KinkStageCfg cfg{H, maxn, stage, 0, ""};

        // 1. Ground truth (no windowing) vs map_shard_stage (windowed).
        DenseMap ref = referenceStageStep(src, H, stage, maxn);
        Run<W> full = map_shard_stage(src, cfg);
        DenseMap gotDense = toDense(full, H, maxn);
        assertDenseEqual(ref, gotDense, "ground-truth");

        // 2. Shard invariance: split src into two shards, map each
        // independently, merge -- must equal the whole-table result exactly
        // (not just densely: same sorted RunRecords, the real merge
        // contract).
        Run<W> shardA(src.begin(), src.begin() + src.size() / 2);
        Run<W> shardB(src.begin() + src.size() / 2, src.end());
        Run<W> outA = map_shard_stage(shardA, cfg);
        Run<W> outB = map_shard_stage(shardB, cfg);
        std::vector<Run<W>> parts{outA, outB};
        Run<W> merged = mergeRuns(parts);

        if (merged.size() != full.size()) {
          std::fprintf(stderr,
                       "gate_kink FAIL (shard-invariance): %zu vs %zu records "
                       "(H=%d stage=%d trial=%d)\n",
                       merged.size(), full.size(), H, stage, trial);
          std::abort();
        }
        for (size_t i = 0; i < full.size(); ++i) {
          if (std::memcmp(merged[i].sig.b, full[i].sig.b, SIGMAX) != 0 ||
              merged[i].lo != full[i].lo || merged[i].len != full[i].len ||
              merged[i].counts != full[i].counts) {
            std::fprintf(stderr,
                         "gate_kink FAIL (shard-invariance): record %zu "
                         "mismatch (H=%d stage=%d trial=%d)\n",
                         i, H, stage, trial);
            std::abort();
          }
        }
      }
    }
  }
}

int main() {
  testAgainstGroundTruthAndSharding();
  std::puts("gate_kink PASS");
}
