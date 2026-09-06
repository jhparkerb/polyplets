// gate_runfile: on-disk RunFileWriter/RunFileReader format gates.
// Covers the BUGS-OF-SHAME runfile.h pass: atomic publish (B4), per-stride
// sub-CRC on seeked reads (B3), and header/.idx magic+byteorder (D6).

#include <cassert>
#include <cstdint>
#include <cstdio>
#include <csignal>
#include <cstring>
#include <string>
#include <vector>
#include <sys/resource.h>
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

// Drop the last `bytes` bytes of a file (ENOSPC / lost-tail truncation).
static void truncateBy(const std::string& p, size_t bytes) {
  auto b = readAll(p);
  assert(b.size() > bytes);
  b.resize(b.size() - bytes);
  writeAll(p, b);
}

// Flip one bit in the byte at `off` (bit rot / a torn write inside the body).
static void flipByteAt(const std::string& p, size_t off) {
  auto b = readAll(p);
  assert(off < b.size());
  b[off] ^= 0x40;
  writeAll(p, b);
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
// exactly the failure mode docs/engine-record.md flagged
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

// Frontier block-zstd ("compression 2"): an indexed+compressed file stores the
// body as INDEPENDENT zstd frames, one per kZstdBlockRecords records, and its
// .idx offsets point at frame starts — so seekToKey works on compressed
// frontier files (the whole point; a single-frame body is unseekable).
static void testBlockCompressedRoundTripAndSeek() {
#ifdef POLY_ZSTD
  const std::string path = "/tmp/gate_runfile_blockz.bin";
  std::remove(path.c_str());
  std::remove((path + ".idx").c_str());
  const int N = 5000;  // several full frames + a partial tail frame
  {
    RunFileWriter<u64> w(path, 3, 8, "", "", "test", 0, /*write_index=*/true,
                         /*compress=*/true);
    assert(w.ok());
    appendN(w, N);
    w.finalize();
  }
  {
    auto b = readAll(path);
    std::string s(b.begin(), b.end());
    assert(s.find("compression 2\n") != std::string::npos &&
           "indexed+compressed file must declare block framing (compression 2)");
  }
  // Full sequential read across every frame boundary.
  {
    RunFileReader<u64> r(path, 3);
    assert(r.ok() && r.records() == static_cast<size_t>(N));
    RunRecord<u64> rec;
    int i = 0;
    while (r.next(rec)) {
      assert(rec.sig.b[0] == static_cast<uint8_t>(i / 256) &&
             rec.sig.b[1] == static_cast<uint8_t>(i % 256) &&
             "block-compressed sequential read out of order");
      assert(rec.counts.size() == 1 && rec.counts[0] == static_cast<u64>(i + 1));
      ++i;
    }
    assert(i == N && "block-compressed sequential read lost records");
  }
  // Seek to keys landing in different frames, at and off stride boundaries.
  for (int target : {0, 63, 64, 700, 1024, 1500, 3000, 4999}) {
    RunFileReader<u64> r(path, 3);
    assert(r.ok());
    uint8_t klo[SIGMAX] = {};
    klo[0] = static_cast<uint8_t>(target / 256);
    klo[1] = static_cast<uint8_t>(target % 256);
    assert(r.seekToKey(klo) && "seekToKey must succeed on a block-compressed file");
    RunRecord<u64> rec;
    bool found = false;
    while (r.next(rec)) {
      int got = rec.sig.b[0] * 256 + rec.sig.b[1];
      if (got == target) {
        found = true;
        assert(rec.counts[0] == static_cast<u64>(target + 1) &&
               "seeked read returned wrong record payload");
        break;
      }
      assert(got < target && "seek overshot the target key");
    }
    assert(found && "seeked read never reached the target key");
  }
  std::remove(path.c_str());
  std::remove((path + ".idx").c_str());
#endif
}

// Compressed inputs must merge correctly (mergeRunFiles seeks + streams them),
// and a mixed plain/compressed input set must behave identically to all-plain.
static void testMergeWithBlockCompressedInputs() {
#ifdef POLY_ZSTD
  const std::string inz = "/tmp/gate_runfile_mz_in1.bin";
  const std::string inp = "/tmp/gate_runfile_mz_in2.bin";
  const std::string out = "/tmp/gate_runfile_mz_out.bin";
  std::remove(inz.c_str()); std::remove((inz + ".idx").c_str());
  std::remove(inp.c_str()); std::remove((inp + ".idx").c_str());
  std::remove(out.c_str()); std::remove((out + ".idx").c_str());
  {
    RunFileWriter<u64> w(inz, 3, 8, "", "", "test", 0, true, /*compress=*/true);
    appendN(w, 3000);
    w.finalize();
  }
  writeRun(inp, 3, 3000);  // plain twin, same keys
  auto [bytes, recs] = mergeRunFiles<u64>({inz, inp}, 3, "", "", out, "test");
  (void)bytes;
  assert(recs == 3000 && "merge of compressed+plain twins must combine keys");
  RunFileReader<u64> r(out, 3);
  RunRecord<u64> rec;
  int i = 0;
  while (r.next(rec)) {
    assert(rec.counts.size() == 1 && rec.counts[0] == 2 * static_cast<u64>(i + 1) &&
           "merged counts must sum the compressed and plain twins");
    ++i;
  }
  assert(i == 3000);
  std::remove(inz.c_str()); std::remove((inz + ".idx").c_str());
  std::remove(inp.c_str()); std::remove((inp + ".idx").c_str());
  std::remove(out.c_str()); std::remove((out + ".idx").c_str());
#endif
}

// Fail-closed on formats from the future: a compression value this build does
// not understand must reject the file, never misread it as plain.
static void testHeaderRejectsUnknownCompression() {
#ifdef POLY_ZSTD
  const std::string path = "/tmp/gate_runfile_zver.bin";
  std::remove(path.c_str());
  std::remove((path + ".idx").c_str());
  {
    RunFileWriter<u64> w(path, 3, 8, "", "", "test", 0, true, /*compress=*/true);
    appendN(w, 10);
    w.finalize();
  }
  tamper(path, "compression 2", "compression 3");
  RunFileReader<u64> r(path, 3);
  assert(!r.ok() && "reader accepted an unknown compression value");
  std::remove(path.c_str());
  std::remove((path + ".idx").c_str());
#endif
}

// ─── E1 "Short Shrift": the reader must not report a short body as EOF ───────
//
// RunFileReader::next() used to return false identically for (i) the legitimate
// end of records, (ii) a body that ran out early, and (iii) a zstd decode /
// frame-checksum failure — and EVERY caller (mergeRunFiles' heap refill,
// map_shard_file, map_shard_stage_file) reads false as "this input is
// exhausted". A truncated or bit-rotted shard therefore contributed FEWER
// records than its own header claims, silently, with no oracle downstream:
// measured 2945 of 3000 records through a merge on a 500-byte truncation, and
// 0 of 3000 on the production seeked path from one flipped byte in a
// compression-2 file. Reachable via ENOSPC on the size-capped tmpfs the a(40)
// run used. The reader now compares records read against the header count and
// aborts.
static const std::string kTruncPath = "/tmp/gate_runfile_short_trunc.bin";
static const std::string kCorruptZPath = "/tmp/gate_runfile_short_corruptz.bin";

static void readTruncatedToEnd() {
  RunFileReader<u64> r(kTruncPath, 3);
  assert(r.ok());
  RunRecord<u64> rec;
  size_t got = 0;
  while (r.next(rec)) ++got;
  // Pre-fix: falls out of the loop short of r.records() and returns cleanly.
  std::fprintf(stderr, "child: yielded %zu of %zu records (no abort)\n", got, r.records());
}
static void testReaderTruncatedBodyAborts() {
  writeRun(kTruncPath, 3, 3000);
  truncateBy(kTruncPath, 500);
  const int rc = runInChild(readTruncatedToEnd);
  assert(rc > 0 &&
         "fail-closed: a body shorter than the header's record count must abort");
  std::remove(kTruncPath.c_str());
  std::remove((kTruncPath + ".idx").c_str());
}

// Same hole through the merge, which is how it would actually reach a banked
// value: a short input's records simply vanish from the merged output.
static void mergeOverTruncatedInput() {
  mergeRunFiles<u64>({kTruncPath}, 3, "", "",
                     "/tmp/gate_runfile_short_merge_out.bin", "test");
}
static void testMergeOverTruncatedInputAborts() {
  writeRun(kTruncPath, 3, 3000);
  truncateBy(kTruncPath, 500);
  const int rc = runInChild(mergeOverTruncatedInput);
  assert(rc > 0 &&
         "fail-closed: a merge over a short input must abort, not undercount");
  std::remove(kTruncPath.c_str());
  std::remove((kTruncPath + ".idx").c_str());
  std::remove("/tmp/gate_runfile_short_merge_out.bin");
  std::remove("/tmp/gate_runfile_short_merge_out.bin.idx");
}

// compression 2 + the production SEEKED read: zstd's in-band frame checksum is
// what replaces the FNV trailer for these files, so a decode failure must be
// fatal or the checksum buys nothing.
static void readCorruptCompressedSeeked() {
  RunFileReader<u64> r(kCorruptZPath, 3);
  assert(r.ok());
  uint8_t klo[SIGMAX] = {};
  klo[0] = 1;  // key 256, well into the body
  if (!r.seekToKey(klo)) { std::fprintf(stderr, "child: seek failed\n"); return; }
  RunRecord<u64> rec;
  size_t got = 0;
  while (r.next(rec)) ++got;
  std::fprintf(stderr, "child: seeked read yielded %zu records (no abort)\n", got);
}
static void testReaderCorruptCompressedAborts() {
#ifdef POLY_ZSTD
  std::remove(kCorruptZPath.c_str());
  std::remove((kCorruptZPath + ".idx").c_str());
  {
    RunFileWriter<u64> w(kCorruptZPath, 3, 8, "", "", "test", 0,
                         /*write_index=*/true, /*compress=*/true);
    appendN(w, 3000);
    w.finalize();
  }
  auto sz = readAll(kCorruptZPath).size();
  flipByteAt(kCorruptZPath, sz / 2);
  const int rc = runInChild(readCorruptCompressedSeeked);
  assert(rc > 0 &&
         "fail-closed: a zstd decode/checksum failure must abort, not read short");
  std::remove(kCorruptZPath.c_str());
  std::remove((kCorruptZPath + ".idx").c_str());
#endif
}

// ─── E1b "Short Shrift" (writer half): finalize() must fail closed ───────────
//
// finalize() published unconditionally: the count backpatch's fseek only warned
// on failure, and the CRC-trailer fwrite and the fclose were unchecked — so a
// writer that ran out of disk in its LAST few bytes still renamed a plausible
// file (placeholder or stale record count, missing CRC trailer) onto the final
// path. The .tmp + rename design exists precisely so a half-written file is
// never published; the error paths bypassed it.
//
// Forcing that state for real, no fault-injection seam: RLIMIT_FSIZE set to the
// exact byte length of the finished body, so every record write succeeds and
// only the 8-byte CRC trailer / its flush at fclose exceeds the limit (EFBIG;
// SIGXFSZ ignored so we see the error rather than die).
static const std::string kFsizePath = "/tmp/gate_runfile_finalize_fsize.bin";
static const int kFsizeRecords = 40;   // < index stride*2, keeps the .idx tiny
static long g_fsize_limit = 0;         // set by the parent before fork()

static void writeRunUnderFsizeLimit() {
  std::signal(SIGXFSZ, SIG_IGN);
  struct rlimit rl;
  rl.rlim_cur = static_cast<rlim_t>(g_fsize_limit);
  rl.rlim_max = static_cast<rlim_t>(g_fsize_limit);
  if (setrlimit(RLIMIT_FSIZE, &rl) != 0) { std::fprintf(stderr, "setrlimit failed\n"); _exit(2); }
  RunFileWriter<u64> w(kFsizePath, 3, 8, "", "", "test");
  for (int i = 0; i < kFsizeRecords; ++i) {
    RunRecord<u64> r;
    std::memset(r.sig.b, 0, SIGMAX);
    r.sig.b[0] = 0; r.sig.b[1] = static_cast<uint8_t>(i);
    r.H = 3; r.lo = 0; r.len = 1; r.counts = {static_cast<u64>(i + 1)};
    w.append(r);
  }
  w.finalize();   // pre-fix: warns at most, then renames the short file into place
  std::fprintf(stderr, "child: finalize returned normally (published=%d)\n",
               (int)exists(kFsizePath));
}
static void testFinalizeFailureDoesNotPublish() {
  // Reference write with no limit, to learn the exact finished size.
  writeRun(kFsizePath, 3, kFsizeRecords);
  const long full = static_cast<long>(readAll(kFsizePath).size());
  std::remove(kFsizePath.c_str());
  std::remove((kFsizePath + ".idx").c_str());
  std::remove((kFsizePath + ".tmp").c_str());
  g_fsize_limit = full - 8;   // everything but the CRC trailer fits

  const int rc = runInChild(writeRunUnderFsizeLimit);
  assert(rc > 0 &&
         "fail-closed: a finalize that cannot complete must abort, not publish");
  assert(!exists(kFsizePath) &&
         "fail-closed: a file whose finalize failed must NEVER be renamed into place");
  std::remove((kFsizePath + ".tmp").c_str());
  std::remove((kFsizePath + ".idx").c_str());
  std::remove((kFsizePath + ".idx.tmp").c_str());
}

// ─── E4 "Load-Bearing Label": an unparseable key bound must not be ignored ───
//
// The range filters were written as `has_lo = !lo_hex.empty() &&
// hexToBytes(...)`, so a bound that FAILED to parse (wrong length for this
// keyLen, non-hex byte) silently disabled the filter — while mergeRunFiles went
// on stamping that same bound into the output header's keylo/keyhi. The output
// then claims a range it does not respect: downstream pruneByBounds trusts the
// stamp and can skip the file for keys it actually contains. Fails closed now.
static void mergeWithUnparseableBound() {
  const std::string in = "/tmp/gate_runfile_badbound_in.bin";
  writeRun(in, 3, 200);
  // keyLen here is H+2 = 5 → 10 hex chars; give it 8.
  mergeRunFiles<u64>({in}, 3, "abcdef01", "", "/tmp/gate_runfile_badbound_out.bin",
                     "test");
  std::fprintf(stderr, "child: merge ran with the bound silently disabled\n");
}
static void testMergeUnparseableBoundAborts() {
  const int rc = runInChild(mergeWithUnparseableBound);
  assert(rc > 0 &&
         "fail-closed: an unparseable key bound must abort, not disable the filter");
  std::remove("/tmp/gate_runfile_badbound_in.bin");
  std::remove("/tmp/gate_runfile_badbound_in.bin.idx");
  std::remove("/tmp/gate_runfile_badbound_out.bin");
  std::remove("/tmp/gate_runfile_badbound_out.bin.idx");
}

// ─── V5: a keyLen wider than SIGMAX must be refused, not overflowed ─────────
//
// Every key in the engine lives in a fixed SIGMAX-byte Sig and is copied
// through SIGMAX-sized STACK arrays (mergeRunFiles' lo_sig/hi_sig,
// map_shard_file, map_shard_stage_file, map_worker's range filter, seekToKey's
// probe buffer), and deserializeRecord zero-pads with
// memset(sig.b + keyLen, 0, SIGMAX - keyLen) — which underflows to a huge
// size_t once keyLen > SIGMAX. Nothing checked it anywhere. The reachable case
// is the kink kernel's keyLen = H+4: at H >= 29 (SIGMAX=32) every one of those
// buffers overflows, silently. Far beyond the a(40) close (H<=21), but a stack
// smash with no diagnostic is not an acceptable way to find that out.
static void writerWithOversizeKeyLen() {
  RunFileWriter<u64> w("/tmp/gate_runfile_keylen.bin", SIGMAX - 4, 8, "", "",
                       "test", SIGMAX + 1);
  RunRecord<u64> r;
  std::memset(r.sig.b, 0, SIGMAX);
  r.H = SIGMAX - 4; r.keyLen = SIGMAX + 1; r.lo = 0; r.len = 1;
  r.counts = {u64{1}};
  w.append(r);        // pre-fix: memcpy reads SIGMAX+1 bytes out of a SIGMAX Sig
  w.finalize();
  std::fprintf(stderr, "child: wrote a keyLen=%d file with no complaint\n", SIGMAX + 1);
}
static void readerWithOversizeKeyLen() {
  writeRun("/tmp/gate_runfile_keylen_in.bin", 3, 4);
  RunFileReader<u64> r("/tmp/gate_runfile_keylen_in.bin", 3, SIGMAX + 1);
  RunRecord<u64> rec;
  while (r.next(rec)) {}
  std::fprintf(stderr, "child: read with keyLen=%d with no complaint\n", SIGMAX + 1);
}
static void mergeWithOversizeKeyLen() {
  writeRun("/tmp/gate_runfile_keylen_in.bin", 3, 4);
  mergeRunFiles<u64>({"/tmp/gate_runfile_keylen_in.bin"}, 3, "", "",
                     "/tmp/gate_runfile_keylen_out.bin", "test", SIGMAX + 1);
}
static void testOversizeKeyLenRefused() {
  assert(runInChild(writerWithOversizeKeyLen) > 0 &&
         "V5: RunFileWriter must refuse a keyLen wider than SIGMAX");
  assert(runInChild(readerWithOversizeKeyLen) > 0 &&
         "V5: RunFileReader must refuse a keyLen wider than SIGMAX");
  assert(runInChild(mergeWithOversizeKeyLen) > 0 &&
         "V5: mergeRunFiles must refuse a keyLen wider than SIGMAX");
  std::remove("/tmp/gate_runfile_keylen.bin");
  std::remove("/tmp/gate_runfile_keylen.bin.idx");
  std::remove("/tmp/gate_runfile_keylen_in.bin");
  std::remove("/tmp/gate_runfile_keylen_in.bin.idx");
  std::remove("/tmp/gate_runfile_keylen_out.bin");
  std::remove("/tmp/gate_runfile_keylen_out.bin.idx");
}

// Pooled zstd contexts must have BOUNDED retention: a persistent worker that
// once ran a 640-input merge must not hold 640 idle contexts forever (80
// workers x 640 x ~200KB was a standing ~10-20GB term in the a(40) OOM).
static void testZstdPoolRetentionBounded() {
#ifdef POLY_ZSTD
  std::vector<ZSTD_DStream*> d;
  std::vector<ZSTD_CStream*> c;
  for (int i = 0; i < 300; i++) { d.push_back(acquireDStream()); c.push_back(acquireCStream()); }
  for (auto* p : d) releaseDStream(p);
  for (auto* p : c) releaseCStream(p);
  assert(zstdCtxPool().d.size() <= zstdCtxPoolCap() &&
         "released DStreams beyond the cap must be freed, not pooled");
  assert(zstdCtxPool().c.size() <= zstdCtxPoolCap() &&
         "released CStreams beyond the cap must be freed, not pooled");
  assert(zstdCtxPoolCap() == kZstdCtxPoolCapDefault &&
         "the default idle-retention cap must stay 64 with the env unset");
#endif
}

// E6 "Pool Underwater": the idle-retention cap is now an env knob
// (POLY_ZSTD_CTX_POOL), parsed ONCE per process like the other POLY_* levers.
// That "once" is why this runs first and in a forked child: the parsed value is
// a function-local static, so a fork after any zstd use would inherit the
// parent's already-initialized value and test nothing.
static void poolCapFromEnv() {
#ifdef POLY_ZSTD
  setenv("POLY_ZSTD_CTX_POOL", "4", 1);
  if (zstdCtxPoolCap() != 4) { std::fprintf(stderr, "cap not honored\n"); _exit(3); }
  std::vector<ZSTD_DStream*> d;
  for (int i = 0; i < 50; i++) d.push_back(acquireDStream());
  for (auto* p : d) releaseDStream(p);
  if (zstdCtxPool().d.size() > 4) { std::fprintf(stderr, "retained past the cap\n"); _exit(4); }
#endif
}
static void testZstdPoolCapEnvOverride() {
#ifdef POLY_ZSTD
  const int rc = runInChild(poolCapFromEnv);
  assert(rc == 0 && "POLY_ZSTD_CTX_POOL must set the idle-retention cap");
#endif
}

int main() {
  testZstdPoolCapEnvOverride();   // must precede any zstd use in this process
  testAtomicPublish();
  testIndexHasMagic();
  testHeaderRejectsBadByteorder();
  testHeaderRejectsCounterMismatch();
  // Fail-closed spill I/O. These intentionally trigger "cannot open" on stderr
  // in the forked child — that noise is the behavior under test, not an error.
  testWriterOpenFailureAborts();
  testMergeReaderOpenFailureAborts();
  testMergeStopResumeMatchesUninterrupted();
  testBlockCompressedRoundTripAndSeek();
  testMergeWithBlockCompressedInputs();
  testHeaderRejectsUnknownCompression();
  // E1 "Short Shrift": short/corrupt bodies must abort, not read short. The
  // forked children print their own diagnostics — that noise is the behavior
  // under test.
  testReaderTruncatedBodyAborts();
  testMergeOverTruncatedInputAborts();
  testReaderCorruptCompressedAborts();
  testFinalizeFailureDoesNotPublish();
  testMergeUnparseableBoundAborts();
  testOversizeKeyLenRefused();
  testZstdPoolRetentionBounded();
  std::puts("gate_runfile PASS");
}
