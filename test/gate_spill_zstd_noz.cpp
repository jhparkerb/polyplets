// gate_spill_zstd_noz: a build WITHOUT POLY_ZSTD must REJECT (not misread) a
// zstd-compressed spill file. Compiled with no -DPOLY_ZSTD; reads the compressed
// file left by gate_spill_zstd and asserts the reader fails cleanly (ok()==false)
// with a clear diagnostic, rather than silently parsing the zstd frame as records.

#include <cassert>
#include <cstdio>
#include <string>
#include "core/runfile.h"

int main() {
  const std::string zpath = "/tmp/gate_spill_zstd_z.bin";
  RunFileReader<u64> r(zpath, 3);
  assert(!r.ok() &&
         "no-POLY_ZSTD build accepted a compressed file (must reject it)");
  std::remove(zpath.c_str());
  std::puts("gate_spill_zstd_noz PASS");
}
