// Sharded-private column sweep CLI gate (redesign branch): map_worker's
// `--kernel kink --stage sharded` wiring, driven as a real subprocess (the
// actual compiled binary), mirroring test/gate_kink_worker_cli.cpp's own
// pattern for the standard seed/stage/finalize path.
//
// Drives ONE column two ways and checks the resulting H+2-keyed frontier
// files decode to the exact same set of records:
//
//   reference: map_worker --kernel kink --stage seed
//              map_worker --kernel kink --stage 0..H-1  (H sequential calls)
//              map_worker --kernel kink --stage finalize
//   sharded:   K parallel map_worker --kernel kink --stage sharded calls,
//              each given a disjoint --lo/--hi key range of the SAME seed
//              input (no cross-shard merge at all during this phase)
//              map_worker --kernel kink --stage finalize --in <all K outputs>
//              (readRangedRunFiles already merges+dedupes multiple --in
//              paths before finalize runs -- see worker/map_worker.cpp's
//              own comment -- so this is the SAME single merge point
//              core/kink_sharded.h's mergeAndFinalizeShardedColumn uses,
//              just reached through the CLI instead of calling the C++
//              function directly)
//
// This is the real end-to-end validation for the worker-CLI wiring that
// test/gate_kink_sharded.cpp (library-level) can't reach -- arg parsing,
// --stage sharded dispatch, and readRangedRunFiles' multi-file merge before
// finalize, all exercised through the actual compiled binary.

#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <map>
#include <string>
#include <vector>

#include "core/run.h"
#include "core/runfile.h"
#include "core/signature.h"

using W = u64;

static int runOrDie(const std::string& cmd) {
  const int rc = std::system(cmd.c_str());
  if (rc != 0) {
    std::fprintf(stderr, "gate_kink_sharded_worker_cli FAIL: command exited %d: %s\n",
                 rc, cmd.c_str());
    std::abort();
  }
  return rc;
}

struct SigLess {
  int keyLen;
  bool operator()(const Sig& a, const Sig& b) const {
    return sigCmp(a.b, b.b, keyLen) < 0;
  }
};
using DenseMap = std::map<Sig, std::vector<W>, SigLess>;

static DenseMap readDense(const std::string& path, int H, int keyLen, int maxn) {
  DenseMap out(SigLess{keyLen});
  RunFileReader<W> r(path, H, keyLen);
  if (!r.ok()) {
    std::fprintf(stderr, "gate_kink_sharded_worker_cli FAIL: cannot read %s\n",
                 path.c_str());
    std::abort();
  }
  RunRecord<W> rec;
  while (r.next(rec)) {
    auto& dst = out[rec.sig];
    if (dst.empty()) dst.assign(maxn + 1, W{0});
    for (int i = 0; i < rec.len; ++i) {
      const int n = static_cast<int>(rec.lo) + i;
      if (n <= maxn) dst[n] += rec.counts[i];
    }
  }
  return out;
}

static void assertDenseEqual(const DenseMap& a, const DenseMap& b, const char* what) {
  if (a.size() != b.size()) {
    std::fprintf(stderr,
                 "gate_kink_sharded_worker_cli FAIL (%s): key count %zu vs %zu\n",
                 what, a.size(), b.size());
    std::abort();
  }
  auto ia = a.begin();
  auto ib = b.begin();
  for (; ia != a.end(); ++ia, ++ib) {
    if (std::memcmp(ia->first.b, ib->first.b, SIGMAX) != 0 ||
        ia->second != ib->second) {
      std::fprintf(stderr, "gate_kink_sharded_worker_cli FAIL (%s): record mismatch\n", what);
      std::abort();
    }
  }
}

// A modest multi-record seed so key-range sharding actually splits
// something meaningful (gate_kink_worker_cli.cpp's single-record seed
// wouldn't exercise sharding at all -- every shard but one would be empty).
static void writeMultiRecordSeed(const std::string& path, int H, int maxn) {
  RunFileWriter<W> w(path, H, maxn, "", "", "test");
  // Spread several distinct end-of-column boundary states across the key
  // space: the all-empty seed record plus a handful of small hand-built
  // "already extended one column" states, canonicalized, sorted by
  // construction (ascending label pattern keeps sig bytes increasing).
  for (int variant = 0; variant < 6; ++variant) {
    RunRecord<W> r;
    std::memset(r.sig.b, 0, SIGMAX);
    if (variant > 0) {
      // occupy the first `variant` rows with label 1, touching top; leaves
      // bottom untouched except for the variant that fills the whole column.
      for (int i = 0; i < variant && i < H; ++i) r.sig.b[i] = 1;
      r.sig.b[H] = 1;  // touched top
      if (variant >= H) r.sig.b[H + 1] = 1;  // touched bottom too
    }
    r.H = H;
    r.keyLen = H + 2;
    r.lo = 0;
    r.len = 1;
    r.counts = {static_cast<W>(variant + 1)};
    w.append(r);
  }
  w.finalize();
}

static void testShardedMatchesReference(int H, int maxn, int K) {
  const std::string dir = "/tmp/gate_kink_sharded_worker_cli_" + std::to_string(H) +
                          "_" + std::to_string(K);
  runOrDie("rm -rf " + dir + " && mkdir -p " + dir);

  const std::string seedPath = dir + "/seed.bin";
  writeMultiRecordSeed(seedPath, H, maxn);

  const std::string bin = "./build/ns/map_worker";
  const std::string common = " --H " + std::to_string(H) +
                             " --maxn " + std::to_string(maxn) +
                             " --fold 0 --ram 134217728 --spill " + dir +
                             " --counter u64";

  // Reference: seed -> H stages -> finalize (today's production path).
  std::string cur = seedPath;
  const std::string stage0 = dir + "/ref_stage0.bin";
  runOrDie(bin + " --kernel kink --stage seed --in " + cur + common +
          " --out " + stage0 + " > " + dir + "/ref_seed.log");
  cur = stage0;
  for (int r = 0; r < H; ++r) {
    const std::string next = dir + "/ref_stage" + std::to_string(r + 1) + ".bin";
    runOrDie(bin + " --kernel kink --stage " + std::to_string(r) + " --in " +
            cur + common + " --out " + next + " > " + dir + "/ref_stage" +
            std::to_string(r) + ".log");
    cur = next;
  }
  const std::string refOut = dir + "/ref_final.bin";
  runOrDie(bin + " --kernel kink --stage finalize --in " + cur + common +
          " --out " + refOut + " > " + dir + "/ref_finalize.log");

  // Sharded: compute K disjoint quantile-based hex cut points from the
  // ACTUAL sig bytes present in the seed file -- a blind evenly-spaced hex
  // prefix split degenerates to one all-records shard + K-1 empty ones,
  // since real (and this gate's synthetic) sig bytes cluster in a small
  // low-value range (RGS-style canonical labels), not spread across
  // 0-255. Reading the real data back and cutting by quantile mirrors what
  // SampleKeysMulti actually does in production (out of scope to call
  // directly from this CLI-level gate, but the intent -- a meaningful,
  // non-degenerate split -- must match, or this test doesn't exercise
  // sharding at all).
  std::vector<Sig> sigs;
  {
    RunFileReader<W> r(seedPath, H, H + 2);
    RunRecord<W> rec;
    while (r.next(rec)) sigs.push_back(rec.sig);
  }
  std::vector<std::string> shardOuts;
  for (int k = 0; k < K; ++k) {
    std::string loHex, hiHex;
    if (k > 0) {
      const size_t idx = sigs.size() * static_cast<size_t>(k) / static_cast<size_t>(K);
      loHex = bytesToHex(sigs[idx].b, H + 2);
    }
    if (k < K - 1) {
      const size_t idx = sigs.size() * static_cast<size_t>(k + 1) / static_cast<size_t>(K);
      hiHex = bytesToHex(sigs[idx].b, H + 2);
    }
    const std::string out = dir + "/shard" + std::to_string(k) + ".bin";
    std::string loFlag = loHex.empty() ? "" : (" --lo " + loHex);
    std::string hiFlag = hiHex.empty() ? "" : (" --hi " + hiHex);
    runOrDie(bin + " --kernel kink --stage sharded --in " + seedPath + common +
            loFlag + hiFlag + " --out " + out + " > " + dir + "/shard" +
            std::to_string(k) + ".log");
    shardOuts.push_back(out);
  }

  std::string inList;
  for (size_t i = 0; i < shardOuts.size(); ++i) {
    if (i) inList += ",";
    inList += shardOuts[i];
  }
  const std::string shardedOut = dir + "/sharded_final.bin";
  runOrDie(bin + " --kernel kink --stage finalize --in " + inList + common +
          " --out " + shardedOut + " > " + dir + "/sharded_finalize.log");

  DenseMap want = readDense(refOut, H, H + 2, maxn);
  DenseMap got = readDense(shardedOut, H, H + 2, maxn);
  assertDenseEqual(want, got, "H+2 next-column frontier");

  runOrDie("rm -rf " + dir);
}

int main() {
  for (int H : {4, 6, 8}) {
    for (int K : {2, 4}) {
      testShardedMatchesReference(H, H + 4, K);
    }
  }
  std::puts("gate_kink_sharded_worker_cli PASS");
}
