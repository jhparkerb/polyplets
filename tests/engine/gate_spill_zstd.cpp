// gate_spill_zstd: zstd spill-file compression round-trip + format gate.
//
// Covers the internal-spill compression path (core/runfile.h): a compressed
// spill file must (1) round-trip byte-identically to the records written,
// (2) carry the "POLYRUN 2" + "compression 1" header, (3) actually be smaller
// on disk than the plain equivalent (compression really fired), and (4) hold
// the same logical records as the plain writer. A separate translation unit
// compiled WITHOUT POLY_ZSTD must reject the compressed file (ok()==false)
// rather than misread it — see gate_spill_zstd_noz.cpp.

#include <cassert>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <string>
#include <vector>
#include <sys/stat.h>
#include "core/runfile.h"

static long fileSize(const std::string& p) {
  struct stat st;
  return (::stat(p.c_str(), &st) == 0) ? static_cast<long>(st.st_size) : -1;
}

static std::string slurp(const std::string& p) {
  FILE* f = std::fopen(p.c_str(), "rb");
  assert(f);
  std::string s;
  char buf[4096];
  size_t r;
  while ((r = std::fread(buf, 1, sizeof(buf), f)) > 0) s.append(buf, r);
  std::fclose(f);
  return s;
}

// Build a deterministic, mildly-compressible record set (H=3 → keyLen 5).
static std::vector<RunRecord<u64>> makeRecords(int H, int n) {
  std::vector<RunRecord<u64>> v;
  v.reserve(n);
  const int keyLen = H + 2;
  for (int i = 0; i < n; ++i) {
    RunRecord<u64> r;
    std::memset(r.sig.b, 0, SIGMAX);
    // Ascending keys (spill files are written sorted); spread over 3 bytes.
    r.sig.b[0] = static_cast<uint8_t>((i >> 16) & 0xff);
    r.sig.b[1] = static_cast<uint8_t>((i >> 8) & 0xff);
    r.sig.b[2] = static_cast<uint8_t>(i & 0xff);
    r.H = H;
    r.keyLen = keyLen;
    r.lo = static_cast<uint8_t>(i % 7);
    r.len = static_cast<uint8_t>(1 + (i % 4));
    r.counts.clear();
    for (int j = 0; j < r.len; ++j)
      r.counts.push_back(static_cast<u64>((i + 1) * 1000 + j));
    v.push_back(std::move(r));
  }
  return v;
}

static void writeRun(const std::string& path, int H,
                     const std::vector<RunRecord<u64>>& recs, bool compress) {
  std::remove(path.c_str());
  std::remove((path + ".idx").c_str());
  RunFileWriter<u64> w(path, H, 32, "", "", "test", /*keyLen=*/0,
                       /*write_index=*/false, /*compress=*/compress);
  assert(w.ok());
  for (const auto& r : recs) w.append(r);
  w.finalize();
}

static std::vector<RunRecord<u64>> readRun(const std::string& path, int H) {
  RunFileReader<u64> r(path, H);
  assert(r.ok() && "reader failed to open/parse the run file");
  std::vector<RunRecord<u64>> out;
  RunRecord<u64> rec;
  while (r.next(rec)) out.push_back(rec);
  return out;
}

static void assertEqual(const std::vector<RunRecord<u64>>& a,
                        const std::vector<RunRecord<u64>>& b) {
  assert(a.size() == b.size() && "record count mismatch");
  for (size_t i = 0; i < a.size(); ++i) {
    assert(std::memcmp(a[i].sig.b, b[i].sig.b, a[i].keyLen) == 0);
    assert(a[i].lo == b[i].lo && a[i].len == b[i].len);
    assert(a[i].counts == b[i].counts);
  }
}

int main() {
  const int H = 3;
  const std::string zpath = "/tmp/gate_spill_zstd_z.bin";
  const std::string ppath = "/tmp/gate_spill_zstd_p.bin";

  // Enough repetitive records that zstd -3 clearly wins on size and the body
  // spans several 256 KB compressed blocks internally.
  auto recs = makeRecords(H, 200000);

  writeRun(zpath, H, recs, /*compress=*/true);
  writeRun(ppath, H, recs, /*compress=*/false);

  // (1) round-trip byte-identical (both paths reproduce the input records).
  assertEqual(readRun(zpath, H), recs);
  assertEqual(readRun(ppath, H), recs);

  // (2) header signals version 2 + compression 1 on the compressed file, and the
  //     plain file is byte-for-byte the old "POLYRUN 1" format (no compression).
  std::string zhdr = slurp(zpath).substr(0, 200);
  assert(zhdr.find("POLYRUN 2\n") == 0 && "compressed file must be POLYRUN 2");
  assert(zhdr.find("compression 1\n") != std::string::npos);
  std::string phdr = slurp(ppath).substr(0, 200);
  assert(phdr.find("POLYRUN 1\n") == 0 && "plain file must stay POLYRUN 1");
  assert(phdr.find("compression") == std::string::npos &&
         "plain file must not carry a compression line");

  // (3) compression really fired: on-disk compressed size meaningfully < plain.
  // Threshold is >1.5x (zs < 2/3 ps), not the old >2x: run-file counts are now
  // LEB128 varint (core/run.h), so the PLAIN file is already ~70% smaller than
  // the old fixed-width format, leaving zstd less headroom (the sig stream and
  // structured counts still compress, ~1.9x on this fixture). zstd-on-varint
  // stacks on top of the varint win; it just isn't the 2x it was on fixed width.
  long zs = fileSize(zpath), ps = fileSize(ppath);
  std::printf("gate_spill_zstd: plain=%ld bytes zstd=%ld bytes (%.1fx)\n",
              ps, zs, ps / static_cast<double>(zs));
  assert(zs > 0 && ps > 0);
  assert(zs * 3 < ps * 2 && "compressed spill not meaningfully smaller than plain");

  // Leave zpath in place for gate_spill_zstd_noz (a build WITHOUT POLY_ZSTD must
  // reject it, not misread it); that step removes it.
  std::remove(ppath.c_str());
  std::puts("gate_spill_zstd PASS");
}
