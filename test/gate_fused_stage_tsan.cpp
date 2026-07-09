// Even Keel D6 TSan gate driver: builds a real stage-0 table (via the real,
// non-TSan map_worker binary -- only its OUTPUT is needed here, not itself
// under sanitizer) and then execs the REAL ThreadSanitizer build of
// worker/fused_stage.cpp (build/ns_tsan/fused_stage) over it with a
// meaningfully concurrent shape: cores=8, three output ranges, a
// non-trivial H so the map+scatter phase (DDF3 Phase 1: each thread owns
// its own input slice AND its own output-bucket row) and the reduce phase
// (DDF3 Phase 2: each range owned by exactly one thread) both actually run
// with real cross-thread data movement. A clean (zero) exit means
// ThreadSanitizer reported no race -- this is the DDF3-mandated gate, run
// separately from the byte-identical correctness gate (test/gate_fused_stage.cpp)
// because a TSan binary is a different (slower, sanitized) build.

#include <cstdio>
#include <cstdlib>
#include <string>

#include "core/run.h"
#include "core/runfile.h"
#include "core/signature.h"

using W = u64;

static int runOrDie(const std::string& cmd) {
  const int rc = std::system(cmd.c_str());
  if (rc != 0) {
    std::fprintf(stderr, "gate_fused_stage_tsan FAIL: command exited %d: %s\n", rc, cmd.c_str());
    std::abort();
  }
  return rc;
}

int main() {
  const std::string dir = "/tmp/gate_fused_stage_tsan";
  runOrDie("rm -rf " + dir + " && mkdir -p " + dir);

  const int H = 10, maxn = 14, r = 5;  // non-trivial H, a real mid-column stage

  const std::string seedPath = dir + "/seed.bin";
  {
    RunFileWriter<W> w(seedPath, H, maxn, "", "", "test");
    w.append(seedRecord<W>(H));
    w.finalize();
  }

  const std::string mapBin = "./build/ns/map_worker";
  const std::string mapCommon = " --H " + std::to_string(H) + " --maxn " + std::to_string(maxn) +
                                " --fold 0 --ram 134217728 --spill " + dir + " --counter u64";
  const std::string stage0 = dir + "/stage0.bin";
  runOrDie(mapBin + " --kernel kink --stage seed --in " + seedPath + mapCommon +
          " --out " + stage0 + " > " + dir + "/seed.log");

  // Two cuts on the leading key byte -> three output ranges.
  const int kLen = H + 4;
  std::string cut1(static_cast<size_t>(kLen) * 2, '0');
  std::string cut2(static_cast<size_t>(kLen) * 2, '0');
  cut1[0] = '4'; cut1[1] = '0';
  cut2[0] = 'c'; cut2[1] = '0';

  const std::string tsanBin = "./build/ns_tsan/fused_stage";
  const std::string outPrefix = dir + "/tsan_out";
  const std::string cmd = "TSAN_OPTIONS=halt_on_error=1:exitcode=66 " + tsanBin +
      " --in " + stage0 + " --H " + std::to_string(H) + " --maxn " + std::to_string(maxn) +
      " --stage " + std::to_string(r) + " --counter u64 --cores 8 --cuts " + cut1 + "," + cut2 +
      " --out-prefix " + outPrefix + " --rev test > " + dir + "/tsan.log 2>&1";
  runOrDie(cmd);

  runOrDie("rm -rf " + dir);
  std::puts("gate_fused_stage_tsan PASS");
}
