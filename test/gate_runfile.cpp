// gate_runfile: on-disk RunFileWriter/RunFileReader format gates.
// Covers the BUGS-OF-SHAME runfile.h pass: atomic publish (B4), per-stride
// sub-CRC on seeked reads (B3), and header/.idx magic+byteorder (D6).

#include <cassert>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <string>
#include <vector>
#include <sys/stat.h>
#include <sys/wait.h>
#include <unistd.h>
#include "core/runfile.h"

static bool exists(const std::string& p) {
  struct stat st;
  return ::stat(p.c_str(), &st) == 0;
}

static std::vector<uint8_t> readAll(const std::string& p) {
  FILE* f = std::fopen(p.c_str(), "rb");
  assert(f);
  std::fseek(f, 0, SEEK_END);
  long n = std::ftell(f);
  std::fseek(f, 0, SEEK_SET);
  std::vector<uint8_t> b(static_cast<size_t>(n));
  assert(std::fread(b.data(), 1, b.size(), f) == b.size());
  std::fclose(f);
  return b;
}

static void writeAll(const std::string& p, const std::vector<uint8_t>& b) {
  FILE* f = std::fopen(p.c_str(), "wb");
  assert(f);
  std::fwrite(b.data(), 1, b.size(), f);
  std::fclose(f);
}

// Replace the first occurrence of `from` (a header token) with `to` of equal
// length, so byte offsets are preserved.
static void tamper(const std::string& path, const std::string& from,
                   const std::string& to) {
  assert(from.size() == to.size());
  auto b = readAll(path);
  std::string s(b.begin(), b.end());
  auto pos = s.find(from);
  assert(pos != std::string::npos);
  std::memcpy(b.data() + pos, to.data(), to.size());
  writeAll(path, b);
}

// writeRun streams n records of height H to path and finalizes.
static void writeRun(const std::string& path, int H, int n) {
  std::remove(path.c_str());
  std::remove((path + ".idx").c_str());
  RunFileWriter<u64> w(path, H, 8, "", "", "test");
  assert(w.ok());
  for (int i = 0; i < n; ++i) {
    RunRecord<u64> r;
    std::memset(r.sig.b, 0, SIGMAX);
    r.sig.b[0] = static_cast<uint8_t>(i / 256);
    r.sig.b[1] = static_cast<uint8_t>(i % 256);
    r.H = H;
    r.lo = 0;
    r.len = 1;
    r.counts = {static_cast<u64>(i + 1)};
    w.append(r);
  }
  w.finalize();
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

// D6 (.idx self-describing): the index sidecar must begin with a magic word so
// a stale / wrong-format / wrong-ISA sidecar is recognized and ignored rather
// than mis-seeked. Pre-fix the file began with the raw keyLen (5), not a magic.
static void testIndexHasMagic() {
  const std::string path = "/tmp/gate_runfile_magic.bin";
  writeRun(path, 3, 200); // > stride, so a sidecar exists
  auto idx = readAll(path + ".idx");
  assert(idx.size() >= 4);
  uint32_t magic;
  std::memcpy(&magic, idx.data(), 4);
  assert(magic == 0x49594C50u && "B/D6: .idx does not start with the 'PLYI' magic");
  std::remove(path.c_str());
  std::remove((path + ".idx").c_str());
}

// D6 (header self-describing): parseHeader must validate byteorder, not ignore
// it. A file claiming a foreign byte order must be rejected (ok()==false).
static void testHeaderRejectsBadByteorder() {
  const std::string path = "/tmp/gate_runfile_bo.bin";
  writeRun(path, 3, 4);
  tamper(path, "byteorder 1", "byteorder 9");
  RunFileReader<u64> r(path, 3);
  assert(!r.ok() && "D6: reader accepted a foreign byteorder");
  std::remove(path.c_str());
  std::remove((path + ".idx").c_str());
}

// D6 (header self-describing): parseHeader must reject a counter tag that does
// not match the reader's word width (reading a u128 file as u64 = silent
// misparse). u64's tag is "u64"; tampering it must be caught.
static void testHeaderRejectsCounterMismatch() {
  const std::string path = "/tmp/gate_runfile_ctr.bin";
  writeRun(path, 3, 4);
  tamper(path, "counter u64", "counter u12"); // != "u64", same length
  RunFileReader<u64> r(path, 3);
  assert(!r.ok() && "D6: reader accepted a mismatched counter tag");
  std::remove(path.c_str());
  std::remove((path + ".idx").c_str());
}

// Run body() in a forked child; return its exit code, or -1 if it died by a
// signal. Lets us assert a fail-closed abort without taking down the gate.
static int runInChild(void (*body)()) {
  std::fflush(nullptr);
  pid_t pid = fork();
  assert(pid >= 0 && "fork failed");
  if (pid == 0) {
    body();          // a fail-closed path exits/aborts here and never returns
    _exit(0);        // body returned normally → child reports success
  }
  int status = 0;
  assert(waitpid(pid, &status, 0) == pid);
  if (WIFEXITED(status)) return WEXITSTATUS(status);
  return -1;  // signal (e.g. abort())
}

// FAIL-CLOSED (fd-exhaustion / ENOSPC / bad spill dir): a RunFileWriter that
// cannot open its file must ABORT, not silently swallow every appended record
// (which yields a plausible-looking UNDERCOUNT with no oracle to catch it —
// the exact way an fd-limited spill run produced a wrong a(11)). The path
// below lives under a directory that does not exist, so fopen() fails.
static void writerOnUnopenablePath() {
  RunFileWriter<u64> w("/nonexistent_dir_zzz/gate_runfile_failclosed.bin",
                       3, 8, "", "", "test");
  RunRecord<u64> r;
  std::memset(r.sig.b, 0, SIGMAX);
  r.lo = 0; r.len = 1; r.counts.assign(1, u64{1});
  w.append(r);       // pre-fix: no-op (fp_ null) → record lost, child exits 0
  w.finalize();
}
static void testWriterOpenFailureAborts() {
  // rc>0 = clean nonzero exit (the desired fail-closed abort); rc==0 =
  // silent drop (the pre-fix bug); rc==-1 = crash (also unacceptable).
  const int rc = runInChild(writerOnUnopenablePath);
  assert(rc > 0 &&
         "fail-closed: RunFileWriter open failure must abort, not drop data");
}

// FAIL-CLOSED (merge side): mergeRunFiles over an input that cannot be opened
// must abort, not treat the missing shard as empty (its records would vanish
// from the merged count). Mirrors the ok()+exit checks the map-phase readers
// already have.
static void mergeOnMissingInput() {
  std::vector<std::string> in = {"/nonexistent_dir_zzz/no_such_shard.bin"};
  mergeRunFiles<u64>(in, 3, "", "", "/tmp/gate_runfile_merge_out.bin", "test");
}
static void testMergeReaderOpenFailureAborts() {
  const int rc = runInChild(mergeOnMissingInput);
  assert(rc > 0 &&
         "fail-closed: mergeRunFiles open failure must abort, not drop a shard");
  std::remove("/tmp/gate_runfile_merge_out.bin");
}

int main() {
  testAtomicPublish();
  testIndexHasMagic();
  testHeaderRejectsBadByteorder();
  testHeaderRejectsCounterMismatch();
  // Fail-closed spill I/O. These intentionally trigger "cannot open" on stderr
  // in the forked child — that noise is the behavior under test, not an error.
  testWriterOpenFailureAborts();
  testMergeReaderOpenFailureAborts();
  std::puts("gate_runfile PASS");
}
