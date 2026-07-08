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

// RED-FIRST (Bottleneck: Merge Range Straggler, merge work-stealing):
// mergeRunFiles' stop/resume contract is "output covers [lo, stop_key);
// re-merge with lo_hex=stop_key covers the rest" -- forcing a stop with
// terminate pre-set to 1 (fires at the first progress stride, written=1024)
// and then resuming must reproduce byte-identical total output to an
// uninterrupted merge over the same inputs. A wrong stop_key boundary
// (off-by-one, wrong sig, etc.) would silently duplicate or drop records --
// exactly the failure mode results/sub-record-interrupt-design.md flagged
// as the reason NOT to build this for kink's mask enumeration; merge's
// simpler seek-based resume avoids that class of bug, but the boundary
// arithmetic itself still needs a real test, not just an argument.
static void testMergeStopResumeMatchesUninterrupted() {
  const std::string in1 = "/tmp/gate_runfile_stopresume_in1.bin";
  const std::string in2 = "/tmp/gate_runfile_stopresume_in2.bin";
  const std::string full = "/tmp/gate_runfile_stopresume_full.bin";
  const std::string part1 = "/tmp/gate_runfile_stopresume_part1.bin";
  const std::string part2 = "/tmp/gate_runfile_stopresume_part2.bin";

  // Two disjoint-keyspace inputs, enough records (> one progress stride) to
  // give the stop point somewhere genuinely mid-merge, not at the very end.
  {
    RunFileWriter<u64> w1(in1, 3, 8, "", "", "test");
    for (int i = 0; i < 3000; i += 2) {
      RunRecord<u64> r;
      std::memset(r.sig.b, 0, SIGMAX);
      r.sig.b[0] = static_cast<uint8_t>(i / 256);
      r.sig.b[1] = static_cast<uint8_t>(i % 256);
      r.lo = 0; r.len = 1; r.counts = {static_cast<u64>(i + 1)};
      w1.append(r);
    }
    w1.finalize();
    RunFileWriter<u64> w2(in2, 3, 8, "", "", "test");
    for (int i = 1; i < 3000; i += 2) {
      RunRecord<u64> r;
      std::memset(r.sig.b, 0, SIGMAX);
      r.sig.b[0] = static_cast<uint8_t>(i / 256);
      r.sig.b[1] = static_cast<uint8_t>(i % 256);
      r.lo = 0; r.len = 1; r.counts = {static_cast<u64>(i + 1)};
      w2.append(r);
    }
    w2.finalize();
  }
  std::vector<std::string> ins = {in1, in2};

  // Reference: full, uninterrupted merge.
  auto [full_bytes, full_recs] = mergeRunFiles<u64>(ins, 3, "", "", full, "test");
  assert(full_recs == 3000);

  // Interrupted: terminate pre-set so the FIRST stride check fires.
  volatile std::sig_atomic_t terminate = 1;
  std::string stop_key;
  auto [p1_bytes, p1_recs] = mergeRunFiles<u64>(
      ins, 3, "", "", part1, "test", 0, {}, &terminate, &stop_key);
  assert(!stop_key.empty() && "stop should have fired on the first stride");
  assert(p1_recs > 0 && p1_recs < 3000 && "partial output should be a strict subset");

  // Resume: re-merge the SAME inputs from stop_key to the end.
  auto [p2_bytes, p2_recs] = mergeRunFiles<u64>(ins, 3, stop_key, "", part2, "test");
  (void)full_bytes; (void)p1_bytes; (void)p2_bytes;

  assert(p1_recs + p2_recs == full_recs &&
         "stop+resume record count must equal the uninterrupted total");

  // Byte-for-byte: concatenated [part1, part2] output bodies (via a plain
  // record-by-record re-merge, since RunFileReader hides the header/CRC
  // framing) must match the reference exactly -- no duplicated or dropped
  // records, no reordering.
  RunFileReader<u64> rf(full, 3), r1(part1, 3), r2(part2, 3);
  assert(rf.ok() && r1.ok() && r2.ok());
  RunRecord<u64> a, b;
  size_t checked = 0;
  bool in_part1 = true;
  while (rf.next(a)) {
    bool got = in_part1 ? r1.next(b) : r2.next(b);
    if (!got && in_part1) {
      in_part1 = false;
      got = r2.next(b);
    }
    assert(got && "reference has more records than part1+part2");
    assert(sigCmp(a.sig.b, b.sig.b, a.keyLen) == 0 &&
           "stop+resume record key mismatch vs uninterrupted merge");
    assert(a.counts == b.counts &&
           "stop+resume record counts mismatch vs uninterrupted merge");
    ++checked;
  }
  assert(checked == full_recs);

  std::remove(in1.c_str()); std::remove((in1 + ".idx").c_str());
  std::remove(in2.c_str()); std::remove((in2 + ".idx").c_str());
  std::remove(full.c_str()); std::remove((full + ".idx").c_str());
  std::remove(part1.c_str()); std::remove((part1 + ".idx").c_str());
  std::remove(part2.c_str()); std::remove((part2 + ".idx").c_str());
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
  testMergeStopResumeMatchesUninterrupted();
  std::puts("gate_runfile PASS");
}
