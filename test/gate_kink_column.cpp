// Design 14 Phase 2.2 gate: kinkSeedStage0 + kinkFinalizeColumn
// (core/kink_column.h) -- the column-boundary steps Phase 1's map_shard_stage
// deliberately left out.
//
// Two independent properties, checked end-to-end (seed -> H stage
// transitions via the already-gated map_shard_stage -> finalize) against a
// ground-truth column step built directly from experiments/kink_tm/kink_tm.cpp's
// kinkSweep() column-loop logic (classify at seed, no classify at finalize;
// stranding-check the outgoing carry; canonicalize; admissibility-prune;
// fold; dedup) -- but reimplemented HERE independently (not by calling
// kinkSeedStage0/kinkFinalizeColumn) so this is a real ground-truth check,
// not a tautology:
//
//   1. Harvest: kinkSeedStage0's Classifier::complete calls must match
//      running ClassifyTriangle::complete directly on the same source
//      records (same triangle rows accumulated).
//   2. Column step: kinkFinalizeColumn(mapShardStage^H(kinkSeedStage0(src)))
//      must byte-match a dense ground-truth column step (expand to per-n
//      vectors, apply the seed/stage/finalize logic directly with no
//      RunRecord windowing at all).
//
// Verified red (see comment above testFinalizeCatchesMissingStrandingCheck):
// injecting a bug (classify at finalize instead of seed; skip the stranding
// check) makes this gate fail.

#include <algorithm>
#include <cassert>
#include <cstdio>
#include <cstring>
#include <map>
#include <random>
#include <vector>

#include "core/classifier.h"
#include "core/kink.h"
#include "core/kink_column.h"
#include "core/run.h"
#include "core/signature.h"

using W = u64;

struct SigLess {
  int keyLen;
  bool operator()(const Sig& a, const Sig& b) const {
    return sigCmp(a.b, b.b, keyLen) < 0;
  }
};
using DenseMap = std::map<Sig, std::vector<W>, SigLess>;

// Build a random plausible end-of-column boundary Sig (keyLen H+2): a random
// partition, canonicalized, plus random touch flags. Same shape as
// gate_kink.cpp's randomMixedState but without the carry byte (H+2 world).
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

// Dense ground truth for one whole column step (seed -> H stages -> finalize),
// reimplemented directly from kink_tm.cpp's kinkSweep() loop body -- no
// windowing, no calls into kinkSeedStage0/map_shard_stage/kinkFinalizeColumn.
struct GroundTruth {
  DenseMap nextCol;
  std::vector<W> harvestedRow;  // row[n] accumulated by the completion check
};

static GroundTruth referenceColumnStep(const Run<W>& src, int H, int maxn,
                                        bool fold) {
  GroundTruth gt;
  gt.nextCol = DenseMap(SigLess{H + 2});
  gt.harvestedRow.assign(maxn + 1, W{0});

  // seed: dense stage-0 table keyed on mixed state (H+4), harvesting on the
  // way through exactly as ClassifyTriangle::complete would.
  DenseMap stage(SigLess{kinkKeyLen(H)});
  for (const auto& rec : src) {
    int comps = 0;
    for (int j = 0; j < H; ++j)
      if (rec.sig.b[j] > comps) comps = rec.sig.b[j];
    if (comps == 1 && rec.sig.b[H] && rec.sig.b[H + 1]) {
      for (int i = 0; i < rec.len; ++i) {
        const int n = static_cast<int>(rec.lo) + i;
        if (n >= 1 && n <= maxn) gt.harvestedRow[n] += rec.counts[i];
      }
    }
    Sig s0 = rec.sig;
    s0.b[H + 2] = 0;
    s0.b[H + 3] = 0;
    auto& dst = stage[s0];
    if (dst.empty()) dst.assign(maxn + 1, W{0});
    for (int i = 0; i < rec.len; ++i) {
      const int n = static_cast<int>(rec.lo) + i;
      if (n <= maxn) dst[n] += rec.counts[i];
    }
  }

  // H stage transitions (dense, unwindowed kinkStageTransition).
  for (int r = 0; r < H; ++r) {
    DenseMap next(SigLess{kinkKeyLen(H)});
    for (auto& kv : stage) {
      int ms = -1;
      for (int n = 0; n <= maxn; ++n)
        if (kv.second[n]) { ms = n; break; }
      if (ms < 0) continue;
      kinkStageTransition(kv.first, H, r, ms, maxn, [&](const Sig& t, int shift) {
        auto& dst = next[t];
        if (dst.empty()) dst.assign(maxn + 1, W{0});
        for (int n = 0; n + shift <= maxn; ++n)
          if (kv.second[n]) dst[n + shift] += kv.second[n];
      });
    }
    stage = std::move(next);
  }

  // finalize: drop carry, stranding-check, canonicalize, prune, fold.
  for (auto& kv : stage) {
    const Sig& s = kv.first;
    if (!s.b[H + 3]) continue;
    const unsigned char outgoing = s.b[H + 2];
    Sig t = s;
    t.b[H + 2] = 0;
    t.b[H + 3] = 0;
    if (outgoing != 0 && !labelInMixedState(t, H, outgoing)) continue;
    int ms = -1;
    for (int n = 0; n <= maxn; ++n)
      if (kv.second[n]) { ms = n; break; }
    if (ms < 0) continue;
    canonicalizeSig(t.b, H);
    if (ms + completionLowerBound(t.b, H) > maxn) continue;
    if (fold) foldSig(t, H);
    auto& dst = gt.nextCol[t];
    if (dst.empty()) dst.assign(maxn + 1, W{0});
    for (int n = 0; n <= maxn; ++n) dst[n] += kv.second[n];
  }
  return gt;
}

static DenseMap toDense(const Run<W>& run, int H, int maxn) {
  DenseMap out(SigLess{H + 2});
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

static void assertDenseEqual(const DenseMap& a, const DenseMap& b,
                             const char* what) {
  if (a.size() != b.size()) {
    std::fprintf(stderr, "gate_kink_column FAIL (%s): key count %zu vs %zu\n",
                what, a.size(), b.size());
    std::abort();
  }
  auto ia = a.begin();
  auto ib = b.begin();
  for (; ia != a.end(); ++ia, ++ib) {
    if (std::memcmp(ia->first.b, ib->first.b, SIGMAX) != 0 ||
        ia->second != ib->second) {
      std::fprintf(stderr, "gate_kink_column FAIL (%s): record mismatch\n",
                   what);
      std::abort();
    }
  }
}

static void assertRowEqual(const std::vector<W>& a, const std::vector<W>& b,
                           const char* what) {
  if (a != b) {
    std::fprintf(stderr, "gate_kink_column FAIL (%s): harvested row mismatch\n",
                 what);
    std::abort();
  }
}

static void testAgainstGroundTruth() {
  std::mt19937 rng(20260702u);
  for (int H = 4; H <= 10; ++H) {
    const int maxn = H + 4;
    for (bool fold : {false, true}) {
      for (int trial = 0; trial < 3; ++trial) {
        Run<W> src = randomColumnTable(rng, H, maxn, 20);

        GroundTruth gt = referenceColumnStep(src, H, maxn, fold);

        TriangleRow<W> out(H, maxn);
        Run<W> stage = kinkSeedStage0<W, ClassifyTriangle>(src, H, out);
        for (int r = 0; r < H; ++r) {
          KinkStageCfg cfg{H, maxn, r, 0, ""};
          stage = map_shard_stage(stage, cfg);
        }
        Run<W> next = kinkFinalizeColumn(stage, H, maxn, fold);

        assertRowEqual(out.row, gt.harvestedRow, "harvest");
        assertDenseEqual(gt.nextCol, toDense(next, H, maxn), "column-step");
      }
    }
  }
}

int main() {
  testAgainstGroundTruth();
  std::puts("gate_kink_column PASS");
}
