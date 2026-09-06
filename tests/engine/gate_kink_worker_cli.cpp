// Design 14 Phase 2.4 gate: map_worker's --kernel kink CLI wiring, driven as
// a real subprocess (the actual compiled binary, not the functions it
// calls directly) -- this is the cheapest point to catch a wiring bug
// (arg parsing, --stage dispatch, --kernel validation) since it costs
// seconds, not the hours a full a(20) orchestrator gate would.
//
// Builds a real seed run file (column 0 of a height-H sweep), then drives it
// through ONE column two ways:
//   column: map_worker --kernel column (the existing, unmodified path)
//   kink:   map_worker --kernel kink --stage seed
//           map_worker --kernel kink --stage 0..H-1  (H sequential calls)
//           map_worker --kernel kink --stage finalize
// and asserts the two resulting H+2-keyed frontier files decode (via
// RunFileReader, so this test doesn't need its own record decoder) to the
// EXACT same set of records. No orchestrator involved -- the seed/stage
// chaining is driven directly by this test, matching the plan's "CLI-level
// integration test" gate for Phase 2.4.

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
    std::fprintf(stderr, "gate_kink_worker_cli FAIL: command exited %d: %s\n",
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
    std::fprintf(stderr, "gate_kink_worker_cli FAIL: cannot read %s\n",
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

static void assertDenseEqual(const DenseMap& a, const DenseMap& b) {
  if (a.size() != b.size()) {
    std::fprintf(stderr,
                 "gate_kink_worker_cli FAIL: key count %zu (column) vs %zu (kink)\n",
                 a.size(), b.size());
    std::abort();
  }
  auto ia = a.begin();
  auto ib = b.begin();
  for (; ia != a.end(); ++ia, ++ib) {
    if (std::memcmp(ia->first.b, ib->first.b, SIGMAX) != 0 ||
        ia->second != ib->second) {
      std::fprintf(stderr, "gate_kink_worker_cli FAIL: record mismatch\n");
      std::abort();
    }
  }
}

static void testOneColumnMatchesColumnKernel(int H, int maxn) {
  const std::string dir = "/tmp/gate_kink_worker_cli_" + std::to_string(H);
  runOrDie("rm -rf " + dir + " && mkdir -p " + dir);

  const std::string seedPath = dir + "/seed.bin";
  {
    RunFileWriter<W> w(seedPath, H, maxn, "", "", "test");
    w.append(seedRecord<W>(H));
    w.finalize();
  }

  const std::string bin = "./build/ns/map_worker";
  const std::string common = " --H " + std::to_string(H) +
                             " --maxn " + std::to_string(maxn) +
                             " --fold 0 --ram 134217728 --spill " + dir +
                             " --counter u64";

  // Column kernel: one column, straight from the binary's default path.
  const std::string colOut = dir + "/col1_column.bin";
  runOrDie(bin + " --in " + seedPath + common + " --out " + colOut +
          " > " + dir + "/column.log");

  // Kink kernel: seed -> H stages -> finalize.
  std::string cur = seedPath;
  const std::string stage0 = dir + "/stage0.bin";
  runOrDie(bin + " --kernel kink --stage seed --in " + cur + common +
          " --out " + stage0 + " > " + dir + "/seed.log");
  cur = stage0;
  for (int r = 0; r < H; ++r) {
    const std::string next = dir + "/stage" + std::to_string(r + 1) + ".bin";
    runOrDie(bin + " --kernel kink --stage " + std::to_string(r) + " --in " +
            cur + common + " --out " + next + " > " + dir + "/stage" +
            std::to_string(r) + ".log");
    cur = next;
  }
  const std::string kinkOut = dir + "/col1_kink.bin";
  runOrDie(bin + " --kernel kink --stage finalize --in " + cur + common +
          " --out " + kinkOut + " > " + dir + "/finalize.log");

  DenseMap wantCol = readDense(colOut, H, H + 2, maxn);
  DenseMap gotKink = readDense(kinkOut, H, H + 2, maxn);
  assertDenseEqual(wantCol, gotKink);

  runOrDie("rm -rf " + dir);
}

// H=8 (maxn 12) costs about as much as H=4 and H=6 together, and these two
// gates are 21 s of a 46 s push -- the serial half the hook runs before
// anything else. What they assert holds at every H: the persistent/CLI-driven
// chain reproduces the column kernel exactly. --deep restores H=8.
int main(int argc, char** argv) {
  bool deep = false;
  for (int i = 1; i < argc; ++i)
    if (std::strcmp(argv[i], "--deep") == 0) deep = true;
  std::vector<int> heights = deep ? std::vector<int>{4, 6, 8}
                                  : std::vector<int>{4, 6};
  for (int H : heights) {
    testOneColumnMatchesColumnKernel(H, H + 4);
  }
  std::puts("gate_kink_worker_cli PASS");
}
