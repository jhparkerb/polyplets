// Bottleneck #5 gate: map_worker's --persistent mode, driven as a real
// subprocess. RED before the feature: --persistent is an unrecognized flag,
// so the process exits 1 immediately (map_worker's "unknown arg" path).
//
// Drives the SAME kink seed -> H stages -> finalize chain
// (test/gate_kink_worker_cli.cpp) through ONE persistent process fed all
// H+2 requests via stdin, instead of H+2 separate spawns -- the exact
// scenario the feature exists for. Asserts the persistent-mode result is
// byte-identical to a column-kernel one-shot run (same assertion the
// existing kink CLI gate makes), so this also re-proves the kink
// seed/stage/finalize chain itself still works when driven this way, not
// just that the process doesn't crash.
//
// Also covers: two independent one-shot columns replayed through a single
// persistent process (proves no state bleeds between requests -- the
// g_terminate reset and per-request local variables).

#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fstream>
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
    std::fprintf(stderr, "gate_persistent_worker FAIL: command exited %d: %s\n",
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
    std::fprintf(stderr, "gate_persistent_worker FAIL: cannot read %s\n",
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
                 "gate_persistent_worker FAIL (%s): key count %zu vs %zu\n",
                 what, a.size(), b.size());
    std::abort();
  }
  auto ia = a.begin();
  auto ib = b.begin();
  for (; ia != a.end(); ++ia, ++ib) {
    if (std::memcmp(ia->first.b, ib->first.b, SIGMAX) != 0 ||
        ia->second != ib->second) {
      std::fprintf(stderr, "gate_persistent_worker FAIL (%s): record mismatch\n", what);
      std::abort();
    }
  }
}

static void writeLine(std::ofstream& f, const std::string& line) {
  f << line << "\n";
}

// Drives the kink seed->H stages->finalize chain for one column through ONE
// persistent map_worker process (all H+2 requests queued as stdin lines up
// front), and checks the result matches the column-kernel one-shot path.
static void testPersistentKinkChainMatchesColumnKernel(int H, int maxn) {
  const std::string dir = "/tmp/gate_persistent_worker_" + std::to_string(H);
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

  // Reference: column kernel, one-shot (unchanged path).
  const std::string colOut = dir + "/col_column.bin";
  runOrDie(bin + " --in " + seedPath + common + " --out " + colOut +
          " > " + dir + "/column.log");

  // Build the full H+2-request stdin script for the kink chain up front --
  // this is the point: ALL of these go to ONE persistent process, not H+2
  // spawns.
  const std::string reqPath = dir + "/requests.txt";
  const std::string stage0 = dir + "/stage0.bin";
  std::vector<std::string> outPaths;
  {
    std::ofstream f(reqPath);
    writeLine(f, "--kernel kink --stage seed --in " + seedPath + common +
                 " --out " + stage0);
    std::string cur = stage0;
    for (int r = 0; r < H; ++r) {
      const std::string next = dir + "/stage" + std::to_string(r + 1) + ".bin";
      writeLine(f, "--kernel kink --stage " + std::to_string(r) + " --in " +
                   cur + common + " --out " + next);
      cur = next;
    }
    const std::string kinkOut = dir + "/col_kink.bin";
    writeLine(f, "--kernel kink --stage finalize --in " + cur + common +
                 " --out " + kinkOut);
    outPaths.push_back(kinkOut);
  }

  runOrDie(bin + " --persistent < " + reqPath + " > " + dir + "/persistent.log");

  // One event=done line per request expected.
  {
    std::ifstream lf(dir + "/persistent.log");
    int doneCount = 0;
    std::string line;
    while (std::getline(lf, line)) {
      if (line.rfind("event=done", 0) == 0) ++doneCount;
    }
    if (doneCount != H + 2) {
      std::fprintf(stderr,
                   "gate_persistent_worker FAIL: expected %d event=done lines, got %d\n",
                   H + 2, doneCount);
      std::abort();
    }
  }

  DenseMap wantCol = readDense(colOut, H, H + 2, maxn);
  DenseMap gotKink = readDense(outPaths[0], H, H + 2, maxn);
  assertDenseEqual(wantCol, gotKink, "kink-chain-vs-column");

  runOrDie("rm -rf " + dir);
}

// Two independent one-shot columns (different heights) replayed through a
// SINGLE persistent process, back to back -- proves no state (g_terminate,
// locals) bleeds from request 1 into request 2.
static void testTwoIndependentColumnsNoBleed() {
  const std::string dir = "/tmp/gate_persistent_worker_bleed";
  runOrDie("rm -rf " + dir + " && mkdir -p " + dir);

  const int H1 = 4, maxn1 = 8;
  const int H2 = 6, maxn2 = 10;
  const std::string seed1 = dir + "/seed1.bin";
  const std::string seed2 = dir + "/seed2.bin";
  {
    RunFileWriter<W> w(seed1, H1, maxn1, "", "", "test");
    w.append(seedRecord<W>(H1));
    w.finalize();
  }
  {
    RunFileWriter<W> w(seed2, H2, maxn2, "", "", "test");
    w.append(seedRecord<W>(H2));
    w.finalize();
  }

  const std::string bin = "./build/ns/map_worker";
  const std::string out1p = dir + "/out1_persistent.bin";
  const std::string out2p = dir + "/out2_persistent.bin";
  const std::string out1o = dir + "/out1_oneshot.bin";
  const std::string out2o = dir + "/out2_oneshot.bin";

  const std::string reqPath = dir + "/requests.txt";
  {
    std::ofstream f(reqPath);
    writeLine(f, "--in " + seed1 + " --H " + std::to_string(H1) + " --maxn " +
                 std::to_string(maxn1) + " --fold 0 --ram 134217728 --spill " +
                 dir + " --counter u64 --out " + out1p);
    writeLine(f, "--in " + seed2 + " --H " + std::to_string(H2) + " --maxn " +
                 std::to_string(maxn2) + " --fold 0 --ram 134217728 --spill " +
                 dir + " --counter u64 --out " + out2p);
  }
  runOrDie(bin + " --persistent < " + reqPath + " > " + dir + "/persistent.log");

  runOrDie(bin + " --in " + seed1 + " --H " + std::to_string(H1) + " --maxn " +
           std::to_string(maxn1) + " --fold 0 --ram 134217728 --spill " + dir +
           " --counter u64 --out " + out1o + " > " + dir + "/oneshot1.log");
  runOrDie(bin + " --in " + seed2 + " --H " + std::to_string(H2) + " --maxn " +
           std::to_string(maxn2) + " --fold 0 --ram 134217728 --spill " + dir +
           " --counter u64 --out " + out2o + " > " + dir + "/oneshot2.log");

  assertDenseEqual(readDense(out1p, H1, H1 + 2, maxn1),
                    readDense(out1o, H1, H1 + 2, maxn1), "req1-vs-oneshot1");
  assertDenseEqual(readDense(out2p, H2, H2 + 2, maxn2),
                    readDense(out2o, H2, H2 + 2, maxn2), "req2-vs-oneshot2");

  runOrDie("rm -rf " + dir);
}

int main() {
  for (int H : {4, 6, 8}) {
    testPersistentKinkChainMatchesColumnKernel(H, H + 4);
  }
  testTwoIndependentColumnsNoBleed();
  std::puts("gate_persistent_worker PASS");
}
