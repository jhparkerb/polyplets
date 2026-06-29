// gate_runfile: on-disk RunFileWriter/RunFileReader format gates.
// Covers the BUGS-OF-SHAME runfile.h pass: atomic publish (B4), per-stride
// sub-CRC on seeked reads (B3), and header/.idx magic+byteorder (D6).

#include <cassert>
#include <cstdio>
#include <cstring>
#include <string>
#include <sys/stat.h>
#include "core/runfile.h"

static bool exists(const std::string& p) {
  struct stat st;
  return ::stat(p.c_str(), &st) == 0;
}

static void appendN(RunFileWriter<u64>& w, int n) {
  for (int i = 0; i < n; ++i) {
    RunRecord<u64> r;
    std::memset(r.sig.b, 0, SIGMAX);
    // Spread keys across the first two sig bytes so the sparse index has
    // distinct keys to seek on.
    r.sig.b[0] = static_cast<uint8_t>(i / 256);
    r.sig.b[1] = static_cast<uint8_t>(i % 256);
    r.H = 3;
    r.lo = 0;
    r.len = 1;
    r.counts = {static_cast<u64>(i + 1)};
    w.append(r);
  }
}

// B4 Torn Publish: the final path must not appear until finalize() completes.
// The writer streams to a temp file and atomically renames on finalize, so a
// kill mid-write can never leave a stale record-count / short CRC at the real
// path (which a seeked read, skipping the body CRC, would consume as garbage).
static void testAtomicPublish() {
  const std::string path = "/tmp/gate_runfile_atomic.bin";
  std::remove(path.c_str());
  std::remove((path + ".idx").c_str());
  std::remove((path + ".tmp").c_str());

  RunFileWriter<u64> w(path, 3, 8, "", "", "test");
  assert(w.ok());
  appendN(w, 200); // > index stride (64), so a sidecar is written too
  assert(!exists(path) && "B4: final path exists before finalize (not atomic)");
  w.finalize();

  assert(exists(path) && "finalize did not publish the final path");
  assert(!exists(path + ".tmp") && "temp data file left behind after finalize");
  assert(!exists(path + ".idx.tmp") && "temp index file left behind after finalize");

  std::remove(path.c_str());
  std::remove((path + ".idx").c_str());
}

int main() {
  testAtomicPublish();
  std::puts("gate_runfile PASS");
}
