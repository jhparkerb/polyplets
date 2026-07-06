// Design 14 Phase 2.3 gate: map_shard_stage_file (core/kink.h) -- the
// file-backed, spilling twin of Phase 1's already-gated in-RAM
// map_shard_stage.
//
// This is a mechanical adaptation (K-way heap over RunFileReader, spill past
// a RAM budget, final merge) with no new algorithmic content -- the risk
// lives entirely in whether kinkKeyLen(H)=H+4 was threaded through every
// place map_shard_file's file-I/O plumbing assumes a keyLen (readers,
// writers, mergeRunFiles' final-write call). This gate writes a random
// source stage table to a real POLYRUN file and asserts the file-backed
// output byte-matches the in-RAM map_shard_stage on the same data, in two
// RAM regimes: (a) ram_budget_bytes=0 (never spills, exercises the
// direct-write fast path) and (b) a tiny budget that forces spill on nearly
// every record (exercises do_spill + the final mergeRunFiles<W> call with
// explicit keyLen).
//
// SIGTERM stop-key round-tripping is NOT covered here -- that mechanism is
// driven by real process signals to a subprocess (see
// ns-gate-resume-boundaries's TestKillResumeAllBoundaries for the column
// kernel's analogous coverage) and gets its kink-kernel counterpart once
// map_worker's --kernel kink CLI wiring lands (Phase 2.4).

#include <cassert>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <map>
#include <random>
#include <string>
#include <vector>

#include "core/kink.h"
#include "core/run.h"
#include "core/runfile.h"
#include "core/signature.h"

using W = u64;

struct SigLess {
  int keyLen;
  bool operator()(const Sig& a, const Sig& b) const {
    return sigCmp(a.b, b.b, keyLen) < 0;
  }
};
using DenseMap = std::map<Sig, std::vector<W>, SigLess>;

// Same random-mixed-state builder as test/gate_kink.cpp (kept independent,
// not shared, so this gate does not silently depend on that file).
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
        *std::max_element(present.begin(), present.end()) + 1);
  }
  s.b[H] = static_cast<unsigned char>(presence(rng));
  s.b[H + 1] = static_cast<unsigned char>(presence(rng));
  s.b[H + 3] = static_cast<unsigned char>(presence(rng));
  canonMixed(s, H);
  return s;
}

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
  sortRun(run);
  deduplicateRun(run);
  return run;
}

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

static void assertDenseEqual(const DenseMap& a, const DenseMap& b,
                             const char* what) {
  if (a.size() != b.size()) {
    std::fprintf(stderr, "gate_kink_stage_file FAIL (%s): key count %zu vs %zu\n",
                what, a.size(), b.size());
    std::abort();
  }
  auto ia = a.begin();
  auto ib = b.begin();
  for (; ia != a.end(); ++ia, ++ib) {
    if (std::memcmp(ia->first.b, ib->first.b, SIGMAX) != 0 ||
        ia->second != ib->second) {
      std::fprintf(stderr, "gate_kink_stage_file FAIL (%s): record mismatch\n",
                   what);
      std::abort();
    }
  }
}

static void testFileBackedMatchesInRam() {
  std::mt19937 rng(20260702u);
  const std::string tmpDir = "/tmp";

  for (int H : {4, 6, 10}) {
    const int maxn = H + 4;
    for (int stage : {0, H / 2, H - 1}) {
      Run<W> src = randomStageTable(rng, H, maxn, 40);

      KinkStageCfg cfg{H, maxn, stage, 0, ""};
      Run<W> wantRun = map_shard_stage(src, cfg);
      DenseMap want = toDense(wantRun, H, maxn);

      // Write src to a real POLYRUN file (keyLen = kinkKeyLen(H)).
      const std::string inPath = tmpDir + "/gate_kink_stage_file_in_" +
                                 std::to_string(H) + "_" +
                                 std::to_string(stage) + ".bin";
      {
        RunFileWriter<W> w(inPath, H, maxn, "", "", "test", kinkKeyLen(H));
        for (const auto& r : src) w.append(r);
        w.finalize();
      }

      for (bool forceSpill : {false, true}) {
        const std::string outPath = tmpDir + "/gate_kink_stage_file_out_" +
                                    std::to_string(H) + "_" +
                                    std::to_string(stage) + "_" +
                                    (forceSpill ? "spill" : "direct") + ".bin";
        const std::string spillDir = tmpDir;
        KinkStageCfg fcfg{H, maxn, stage,
                          forceSpill ? size_t{1} : size_t{0}, spillDir};
        auto [spill_bytes, out_recs] = map_shard_stage_file<W>(
            {inPath}, fcfg, outPath, "", "", "test");
        (void)spill_bytes;
        (void)out_recs;
        if (forceSpill && spill_bytes == 0 && !wantRun.empty()) {
          std::fprintf(stderr,
                       "gate_kink_stage_file FAIL: forced-spill run at H=%d "
                       "stage=%d never spilled (test not exercising the "
                       "spill path)\n",
                       H, stage);
          std::abort();
        }

        Run<W> gotRun;
        {
          RunFileReader<W> r(outPath, H, kinkKeyLen(H));
          RunRecord<W> rec;
          while (r.next(rec)) gotRun.push_back(rec);
        }
        DenseMap got = toDense(gotRun, H, maxn);
        assertDenseEqual(want, got,
                         forceSpill ? "file-backed-spill" : "file-backed-direct");
        std::remove(outPath.c_str());
      }
      std::remove(inPath.c_str());
    }
  }
}

int main() {
  testFileBackedMatchesInRam();
  std::puts("gate_kink_stage_file PASS");
}
