// Even Keel D6, F1 gate: worker/fused_stage.cpp (the real compiled binary)
// vs the existing map_worker+merge_worker path for one mid-column kink
// stage round -- byte-identical output required (docs/even-keel-fusion-
// plan.md DDF9). Drives both as real subprocesses (not the library calls
// directly), same pattern as test/gate_kink_worker_cli.cpp.
//
// For each (H, maxn) case: build a real seed run, run it through
// --kernel kink --stage seed to get the stage-0 table (keyLen H+4), then
// run stage r=H/2 two ways:
//   existing: ONE map_worker --kernel kink --stage r (whole input, no
//             --lo/--hi splitting) piped into ONE merge_worker split into
//             THREE output ranges via two --klo/--khi cut points -- this
//             exercises the real merge-range-boundary combine path, not
//             just a pass-through.
//   fused:    ONE fused_stage --cores 3 --cuts <same two cut points>
// and asserts the resulting (possibly multi-file) range sets decode to the
// exact same dense per-key count-vector map. Includes a tight-budget case
// (maxn == H+1) to stress the ms/budget boundary near the admissibility
// cliff (kinkStageTransition's `occupy && ms+1 > maxn` check).

#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <map>
#include <string>
#include <vector>

#include "core/kink.h"
#include "core/run.h"
#include "core/runfile.h"
#include "core/signature.h"

using W = u64;

static int runOrDie(const std::string& cmd) {
  const int rc = std::system(cmd.c_str());
  if (rc != 0) {
    std::fprintf(stderr, "gate_fused_stage FAIL: command exited %d: %s\n", rc, cmd.c_str());
    std::abort();
  }
  return rc;
}

struct SigLess {
  int keyLen;
  bool operator()(const Sig& a, const Sig& b) const { return sigCmp(a.b, b.b, keyLen) < 0; }
};
using DenseMap = std::map<Sig, std::vector<W>, SigLess>;

// Read one or more POLYRUN files (skipping any that don't exist -- a range
// with zero records legitimately has no file) into one dense per-key
// count-vector map, so this gate doesn't care how many range files either
// side split its output into.
static void readDenseInto(DenseMap& out, const std::string& path, int H, int keyLen, int maxn) {
  RunFileReader<W> r(path, H, keyLen);
  if (!r.ok()) return;  // absent range file = zero records for that range
  RunRecord<W> rec;
  while (r.next(rec)) {
    auto& dst = out[rec.sig];
    if (dst.empty()) dst.assign(static_cast<size_t>(maxn) + 1, W{0});
    for (int i = 0; i < rec.len; ++i) {
      const int n = static_cast<int>(rec.lo) + i;
      if (n <= maxn) dst[static_cast<size_t>(n)] += rec.counts[static_cast<size_t>(i)];
    }
  }
}

static void assertDenseEqual(const DenseMap& a, const DenseMap& b, const char* what) {
  if (a.size() != b.size()) {
    std::fprintf(stderr, "gate_fused_stage FAIL [%s]: key count %zu (existing) vs %zu (fused)\n",
                 what, a.size(), b.size());
    std::abort();
  }
  auto ia = a.begin();
  auto ib = b.begin();
  for (; ia != a.end(); ++ia, ++ib) {
    if (std::memcmp(ia->first.b, ib->first.b, SIGMAX) != 0 || ia->second != ib->second) {
      std::fprintf(stderr, "gate_fused_stage FAIL [%s]: record mismatch\n", what);
      std::abort();
    }
  }
}

static void testStageRoundMatches(int H, int maxn) {
  const std::string dir = "/tmp/gate_fused_stage_" + std::to_string(H) + "_" + std::to_string(maxn);
  runOrDie("rm -rf " + dir + " && mkdir -p " + dir);

  const int kLen = kinkKeyLen(H);
  const std::string seedPath = dir + "/seed.bin";
  {
    RunFileWriter<W> w(seedPath, H, maxn, "", "", "test");
    w.append(seedRecord<W>(H));
    w.finalize();
  }

  const std::string mapBin   = "./build/ns/map_worker";
  const std::string mergeBin = "./build/ns/merge_worker";
  const std::string fusedBin = "./build/ns/fused_stage";
  const std::string mapCommon = " --H " + std::to_string(H) + " --maxn " + std::to_string(maxn) +
                                " --fold 0 --ram 134217728 --spill " + dir + " --counter u64";

  // seed -> stage-0 table (H+4-keyed).
  const std::string stage0 = dir + "/stage0.bin";
  runOrDie(mapBin + " --kernel kink --stage seed --in " + seedPath + mapCommon +
          " --out " + stage0 + " > " + dir + "/seed.log");

  const int r = H / 2;  // a mid-column stage, matches the plan's mid-column scope

  // Two cut points splitting the H+4-keyed key space into three ranges by
  // the leading byte (0x40, 0xC0) -- doesn't need to be balanced for a
  // correctness gate, just needs to be VALID hex of the right width and to
  // land some records on both sides of at least one cut across the H cases
  // tested (small H concentrates canonMixed's leading byte in a narrow
  // range, so not every cut is guaranteed non-trivial for every H -- the
  // point of the gate is byte-identical output regardless).
  auto cutHex = [&](unsigned char firstByte) {
    std::string hex(static_cast<size_t>(kLen) * 2, '0');
    char buf[3];
    std::snprintf(buf, sizeof(buf), "%02x", firstByte);
    hex[0] = buf[0]; hex[1] = buf[1];
    return hex;
  };
  const std::string cut1 = cutHex(0x40);
  const std::string cut2 = cutHex(0xC0);

  // ---- existing path: one map_worker (whole range) + one merge_worker,
  // split into 3 output ranges via the two cuts. ----
  const std::string mapOut = dir + "/map_out.bin";
  runOrDie(mapBin + " --kernel kink --stage " + std::to_string(r) + " --in " + stage0 +
          mapCommon + " --out " + mapOut + " > " + dir + "/map.log");

  const std::string mergeCommon = " --H " + std::to_string(H) + " --counter u64 --keylen " +
                                  std::to_string(kLen) + " --rev test";
  const std::string existR0 = dir + "/exist_r0.bin";
  const std::string existR1 = dir + "/exist_r1.bin";
  const std::string existR2 = dir + "/exist_r2.bin";
  runOrDie(mergeBin + " --in " + mapOut + mergeCommon + " --khi " + cut1 +
          " --out " + existR0 + " > " + dir + "/merge0.log");
  runOrDie(mergeBin + " --in " + mapOut + mergeCommon + " --klo " + cut1 + " --khi " + cut2 +
          " --out " + existR1 + " > " + dir + "/merge1.log");
  runOrDie(mergeBin + " --in " + mapOut + mergeCommon + " --klo " + cut2 +
          " --out " + existR2 + " > " + dir + "/merge2.log");

  // ---- fused path: one fused_stage call, cores=3, same two cuts. ----
  const std::string fusedPrefix = dir + "/fused";
  runOrDie(fusedBin + " --in " + stage0 + " --H " + std::to_string(H) + " --maxn " +
          std::to_string(maxn) + " --stage " + std::to_string(r) + " --counter u64 --cores 3" +
          " --cuts " + cut1 + "," + cut2 + " --out-prefix " + fusedPrefix + " --rev test" +
          " > " + dir + "/fused.log");

  DenseMap wantExisting(SigLess{kLen}), gotFused(SigLess{kLen});
  readDenseInto(wantExisting, existR0, H, kLen, maxn);
  readDenseInto(wantExisting, existR1, H, kLen, maxn);
  readDenseInto(wantExisting, existR2, H, kLen, maxn);
  readDenseInto(gotFused, fusedPrefix + "_u0.bin", H, kLen, maxn);
  readDenseInto(gotFused, fusedPrefix + "_u1.bin", H, kLen, maxn);
  readDenseInto(gotFused, fusedPrefix + "_u2.bin", H, kLen, maxn);

  const std::string what = "H=" + std::to_string(H) + " maxn=" + std::to_string(maxn);
  assertDenseEqual(wantExisting, gotFused, what.c_str());

  // Sanity: the stage actually produced something (an empty gate proves
  // nothing about scatter/reduce correctness).
  if (wantExisting.empty()) {
    std::fprintf(stderr, "gate_fused_stage FAIL [%s]: stage produced zero records, gate is vacuous\n",
                 what.c_str());
    std::abort();
  }

  runOrDie("rm -rf " + dir);
}

int main() {
  for (int H : {4, 6, 8}) testStageRoundMatches(H, H + 4);
  // Tight-budget case: maxn just above H stresses the ms/budget cliff in
  // kinkStageTransition (occupy && ms+1 > maxn) much harder than the
  // generous H+4 headroom above.
  testStageRoundMatches(6, 7);
  std::puts("gate_fused_stage PASS");
}
