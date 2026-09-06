// runfile.h — POLYRUN file format: streaming read/write of sorted runs (M1).
//
// Wire format:
//   POLYRUN 1\n
//   height H\n
//   maxn N\n
//   counter u64\n
//   classifier triangle\n
//   keylo HEX\n
//   keyhi HEX\n
//   records 000000000000000000\n   <- 18-digit zero-padded placeholder, fseek'd
//   rev GITREV\n
//   byteorder 1\n
//   \n
//   <M binary records in ascending sig order, same format as serializeRecord>
//   <8 bytes LE FNV-1a-64 CRC over all body record bytes>

#pragma once

#include <cerrno>
#include <csignal>
#include <cstdio>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <functional>
#include <memory>
#include <queue>
#include <string>
#include <utility>
#include <vector>

#include "core/run.h"
#include "core/profile.h"

#ifdef POLY_ZSTD
#include <zstd.h>
#endif

// ─── Spill compression (POLY_ZSTD) ────────────────────────────────────────────
//
// Internal spill files (do_spill, write_index=false, read back sequentially by
// mergeRunFiles) may be zstd-compressed to dissolve the map-phase disk write
// throttle. Signaled in the text header by "POLYRUN 2" + a "compression 1" line;
// the body is then a single zstd frame (checksum-enabled) INSTEAD of the plain
// records + FNV trailer. Plain files stay "POLYRUN 1" with no compression line —
// byte-identical to before — and old readers/tools still parse them.
//
// A bounded block buffer keeps memory flat regardless of file size. Compression
// level is POLY_SPILL_ZSTD_LEVEL (default 3). A build WITHOUT POLY_ZSTD errors
// clearly on a compressed file rather than misreading it.

inline constexpr size_t kSpillBlockBytes = 256 * 1024;

// Block-framed frontier compression ("compression 2"): indexed files (map and
// merge outputs — the frontier, ~all of a run's disk traffic) store the body as
// INDEPENDENT zstd frames of kZstdBlockRecords records each, and every .idx
// entry points at the enclosing frame's start. seekToKey then lands on a frame
// boundary and decompression starts cleanly there — a single-frame body
// ("compression 1", the unindexed internal spill path) cannot seek at all.
//
// INTEGRITY of a compression-2 (or -1) file is the zstd frame checksum, in
// band, not the FNV trailer plain files carry — and it is enforced fail-closed
// HERE: RunFileReader aborts on any decode or checksum failure and on any body
// that ends before the header's record count (E1). No independent out-of-band
// check exists for these files: verify.go and runcat are Go and decode plain
// bodies only, and there is no C++ dump tool (an audit reader is deferred, see
// AUDIT-2026-07-30 E2). The manual recovery/inspection path is
// `tail -c +<body offset+1> FILE | zstd -d`, which those two tools now print.
//
// Frame size in RECORDS (env POLY_FRONTIER_ZSTD_BLOCK, default 256).
// WRITER-SIDE ONLY: readers decompress whatever frames they find and idx
// entries always point at the containing frame's start, so any mix of frame
// sizes coexists (a default change never invalidates existing files).
// The curve is U-shaped, both ends measured (docs/engine-record.md):
//  - ratio on identical live a(39) H20 records (plain 158.8 B/rec):
//    64 -> 1.45x, 256 -> 1.72x, 512 -> 1.78x, 1024 -> 1.81x
//    (experiments/reframe_measure.cpp);
//  - gympie H15/maxn30 bench (plain 486s/6.0k cpu-s):
//    64 -> 684s/7.1k, 256 -> 576s/6.9k, 512 -> 778s/8.5k.
//    Below ~256, per-frame overhead (decompressBegin + checksum epilogue)
//    dominates; above it, (merge-range x input) seek-overshoot decompression
//    does. 256 dominates 64 on BOTH metrics — hence the default.
inline size_t frontierZstdBlockRecords() {
  static const size_t v = [] {
    const char* e = std::getenv("POLY_FRONTIER_ZSTD_BLOCK");
    if (e && *e) { long n = std::atol(e); if (n > 0) return (size_t)n; }
    return (size_t)256;
  }();
  return v;
}

// First body-read fill after open/seek; rawRead doubles from here up to
// kSpillBlockBytes so streaming readers still amortize while one-record
// peeks (merge heap-init at fan-in scale) stay cheap.
inline constexpr size_t kFirstFillBytes = 8 * 1024;

// Compressed readers cap their adaptive buffers here, NOT kSpillBlockBytes:
// a merge holds (inputs) readers open simultaneously per range, and 80
// workers x ~640 inputs x (cbuf+dbuf at 256KB each + dctx) was a ~35GB
// round-periodic RSS spike — the a(40) third OOM (mem.log: used 95->126.6GB
// swings with shm at only 3-10GB). 64KB keeps streaming amortization (8
// frames per fill at the 256-record default) at a quarter of the footprint.
inline constexpr size_t kZReaderMaxFill = 64 * 1024;

inline int spillZstdLevel() {
  const char* e = std::getenv("POLY_SPILL_ZSTD_LEVEL");
  if (e && *e) { int v = std::atoi(e); if (v != 0) return v; }
  return 3;
}

// Frontier-compression opt-in: block-framed zstd on the indexed map/merge
// outputs. OFF by default until validated at scale (the a(39) plan:
// POLY_FRONTIER_ZSTD=1 in the run environment; flip the default only after a
// full production run chain-validates). Distinct from internal-spill
// compression, which is on by default and covered by POLY_NO_SPILL_ZSTD.
inline bool frontierZstd() {
#ifdef POLY_ZSTD
  const char* e = std::getenv("POLY_FRONTIER_ZSTD");
  return e && *e && std::strcmp(e, "0") != 0;
#else
  return false;
#endif
}

// Frontier compression level: default 1, NOT spillZstdLevel()'s 3. Measured on
// live a(38) H20 merge outputs: zstd-1 = 1.83x, zstd-3 = 1.86x — the ratio
// gain is negligible while level 3 costs ~2-3x the compressor CPU, paid on
// every map AND merge writer at frontier scale.
inline int frontierZstdLevel() {
  const char* e = std::getenv("POLY_FRONTIER_ZSTD_LEVEL");
  if (e && *e) { int v = std::atoi(e); if (v != 0) return v; }
  return 1;
}

#ifdef POLY_ZSTD
// Thread-local zstd context pools. Creating a context allocates a multi-MB
// workspace — an mmap-class allocation whose kernel-side cost showed up as
// WALL (not cpu) at fan-in scale: (ranges x inputs) reader opens per round,
// each paying mach_vm/page-fault traps on macOS's allocator (sampled:
// mach_vm_reclaim under ZSTD_createDStream; the glibc-mmap-threshold Fan-In
// Tax lesson replayed through zstd). Workers are single-threaded and
// persistent, so a thread-local free list reaches steady state with zero
// context allocation. A k-way merge holds many readers open concurrently —
// hence a pool, not a single cached context.
// Retention cap: a persistent worker that once ran an N-input merge must not
// hold N idle contexts forever (80 workers x ~640 x ~200KB was a standing
// 10-20GB term in the a(40) OOM). Peak concurrent use is unbounded (k-way
// merges hold all readers open); only IDLE retention is capped.
//
// The cap is a RAM-vs-context-churn trade with a real cost on both sides: at a
// production fan-in of ~640 inputs a 64-slot pool serves only ~10% of the
// round's acquires and the rest pay ZSTD_createDStream's multi-MB workspace
// allocation (the very cost the pool exists to avoid), while raising it
// multiplies idle retention across every worker. Unlike every neighbouring
// lever (POLY_FRONTIER_ZSTD*, POLY_SPILL_ZSTD_LEVEL, POLY_NO_SEEK) it had NO
// knob, so the trade could not be moved without a rebuild. POLY_ZSTD_CTX_POOL
// overrides it; default 64, unchanged. Parsed once per process, like the rest.
inline constexpr size_t kZstdCtxPoolCapDefault = 64;
inline size_t zstdCtxPoolCap() {
  static const size_t v = [] {
    const char* e = std::getenv("POLY_ZSTD_CTX_POOL");
    if (e && *e) { long n = std::atol(e); if (n >= 0) return (size_t)n; }
    return kZstdCtxPoolCapDefault;
  }();
  return v;
}

struct ZstdCtxPool {
  std::vector<ZSTD_DStream*> d;
  std::vector<ZSTD_CStream*> c;
  ~ZstdCtxPool() {
    for (auto* p : d) ZSTD_freeDStream(p);
    for (auto* p : c) ZSTD_freeCStream(p);
  }
};
inline ZstdCtxPool& zstdCtxPool() {
  static thread_local ZstdCtxPool p;
  return p;
}
inline ZSTD_DStream* acquireDStream() {
  auto& pool = zstdCtxPool().d;
  if (!pool.empty()) {
    ZSTD_DStream* x = pool.back();
    pool.pop_back();
    ZSTD_DCtx_reset(x, ZSTD_reset_session_only);
    return x;
  }
  return ZSTD_createDStream();
}
inline void releaseDStream(ZSTD_DStream* x) {
  if (!x) return;
  auto& pool = zstdCtxPool().d;
  if (pool.size() >= zstdCtxPoolCap()) { ZSTD_freeDStream(x); return; }
  pool.push_back(x);
}
inline ZSTD_CStream* acquireCStream() {
  auto& pool = zstdCtxPool().c;
  if (!pool.empty()) {
    ZSTD_CStream* x = pool.back();
    pool.pop_back();
    // Full reset: parameters (level, checksum) are re-set by each writer.
    ZSTD_CCtx_reset(x, ZSTD_reset_session_and_parameters);
    return x;
  }
  return ZSTD_createCStream();
}
inline void releaseCStream(ZSTD_CStream* x) {
  if (!x) return;
  auto& pool = zstdCtxPool().c;
  if (pool.size() >= zstdCtxPoolCap()) { ZSTD_freeCStream(x); return; }
  pool.push_back(x);
}
#endif

// ─── Counter name ─────────────────────────────────────────────────────────────

template <class W> inline constexpr const char* counterTag();
template <> inline constexpr const char* counterTag<u64>()  { return "u64"; }
template <> inline constexpr const char* counterTag<u128>() { return "u128"; }

// ─── Hex helpers ──────────────────────────────────────────────────────────────

inline std::string bytesToHex(const uint8_t* b, int n) {
  static const char hex[] = "0123456789abcdef";
  std::string s;
  s.reserve(static_cast<size_t>(n) * 2);
  for (int i = 0; i < n; ++i) {
    s.push_back(hex[(b[i] >> 4) & 0xf]);
    s.push_back(hex[b[i] & 0xf]);
  }
  return s;
}

inline bool hexToBytes(const std::string& hex, uint8_t* b, int n) {
  if (static_cast<int>(hex.size()) != n * 2) return false;
  for (int i = 0; i < n; ++i) {
    int hi = -1, lo = -1;
    char ch = hex[static_cast<size_t>(i * 2)];
    if (ch >= '0' && ch <= '9') hi = ch - '0';
    else if (ch >= 'a' && ch <= 'f') hi = ch - 'a' + 10;
    else if (ch >= 'A' && ch <= 'F') hi = ch - 'A' + 10;
    else return false;
    ch = hex[static_cast<size_t>(i * 2 + 1)];
    if (ch >= '0' && ch <= '9') lo = ch - '0';
    else if (ch >= 'a' && ch <= 'f') lo = ch - 'a' + 10;
    else if (ch >= 'A' && ch <= 'F') lo = ch - 'A' + 10;
    else return false;
    b[i] = static_cast<uint8_t>((hi << 4) | lo);
  }
  return true;
}

// FAIL-CLOSED key-bound parse (E4 "Load-Bearing Label"). Every range filter in
// the engine was written as `has_lo = !lo_hex.empty() && hexToBytes(...)`, so a
// bound that FAILED to parse (wrong length for this keyLen, a non-hex byte)
// silently disabled the filter. Two distinct wrong answers follow:
//   - mergeRunFiles stamps lo_hex/hi_hex into the OUTPUT header regardless, so
//     the file advertises a range it did not honor; pruneByBounds then trusts
//     the stamp and can skip that file for keys it actually holds;
//   - a map unit with its filter disabled processes keys belonging to OTHER
//     units, and the merge combines both copies — a double count.
// Neither is detectable downstream, so an unparseable non-empty bound aborts.
// Empty ("open end") is still the legitimate way to say "no bound".
inline bool parseKeyBound(const std::string& hex, uint8_t* out, int keyLen,
                          const char* who, const char* which) {
  if (hex.empty()) return false;
  if (!hexToBytes(hex, out, keyLen)) {
    std::fprintf(stderr,
                 "%s: unparseable %s key bound \"%s\" for keyLen %d — refusing "
                 "to run with the range filter silently disabled\n",
                 who, which, hex.c_str(), keyLen);
    std::exit(1);
  }
  return true;
}

// ─── FNV-1a-64 ───────────────────────────────────────────────────────────────

static constexpr uint64_t FNV_OFFSET = 14695981039346656037ULL;
static constexpr uint64_t FNV_PRIME  = 1099511628211ULL;

inline uint64_t fnv1a64_update(uint64_t hash, const void* data, size_t len) {
  const uint8_t* p = static_cast<const uint8_t*>(data);
  for (size_t i = 0; i < len; ++i) {
    hash ^= static_cast<uint64_t>(p[i]);
    hash *= FNV_PRIME;
  }
  return hash;
}

// ─── RunFileWriter ────────────────────────────────────────────────────────────

// .idx sidecar self-describing header (D6): magic + format version + byteorder,
// so a stale, truncated, or wrong-ISA sidecar is recognized and ignored (the
// reader falls back to a full scan) instead of producing a wrong seek.
inline constexpr uint32_t kRunIndexMagic   = 0x49594C50u; // 'PLYI', little-endian
inline constexpr uint16_t kRunIndexVersion = 1;
inline constexpr uint8_t  kRunByteOrderLE  = 1;
inline constexpr long kRunIndexCountOffset = 11;                     // magic4+ver2+bo1+keyLen4
inline constexpr long kRunIndexHeaderLen   = kRunIndexCountOffset + 8; // + count8

template <class W>
class RunFileWriter {
 public:
  // Real writer: opens file, writes header with placeholder record count.
  // keyLen defaults to 0 which means H+2 (triangle path); pass H+3 for holes.
  RunFileWriter(const std::string& path, int H, int maxn,
                const std::string& lo_hex, const std::string& hi_hex,
                const std::string& rev = "", int keyLen = 0,
                bool write_index = true, bool compress = false)
      : H_(H), keyLen_((keyLen == 0) ? H + 2 : keyLen),
        fp_(nullptr), record_count_(0), body_bytes_(0),
        crc_(FNV_OFFSET), records_offset_(0),
        path_(path), tmp_path_(path + ".tmp"),
        write_index_(write_index), compress_(compress), body_start_offset_(0) {
    requireKeyLenFits(keyLen_, "RunFileWriter");
#ifndef POLY_ZSTD
    compress_ = false;  // no zstd in this build: only the plain path exists
#endif
    // Indexed+compressed = block-framed ("compression 2"): the .idx must point
    // at positions where decompression can start, so the body is framed per
    // kZstdBlockRecords. Unindexed+compressed stays the single-frame spill
    // format ("compression 1").
    block_framed_ = compress_ && write_index_;
    zstd_block_records_ = frontierZstdBlockRecords();
    // Atomic publish (B4): stream to a temp file and rename onto the final path
    // in finalize().  A kill mid-write then leaves only a stale .tmp; the real
    // path never holds a placeholder record-count or a short CRC (which a seeked
    // read, skipping the body CRC, would otherwise consume as garbage).
    fp_ = std::fopen(tmp_path_.c_str(), "wb");
    if (!fp_) {
      // FAIL-CLOSED: a writer that can't open its file has nowhere legitimate
      // to go — limping on with fp_==nullptr makes append()/finalize() silently
      // discard every record, yielding a plausible-looking UNDERCOUNT with no
      // signal (the exact failure an fd-exhausted spill produced). Unlike the
      // reader (whose !ok() also covers a legitimately-rejected foreign/corrupt
      // header, so its call sites decide), a failed writer open is never
      // tolerable, so we abort here rather than trust every call site to check
      // ok().  See core/fdlimit.h for why the fd limit is raised to avoid this.
      std::fprintf(stderr, "RunFileWriter: cannot open %s\n", tmp_path_.c_str());
      std::exit(1);
    }
#ifdef POLY_ZSTD
    if (compress_) {
      cctx_ = acquireCStream();
      ZSTD_CCtx_setParameter(cctx_, ZSTD_c_compressionLevel,
                             block_framed_ ? frontierZstdLevel() : spillZstdLevel());
      ZSTD_CCtx_setParameter(cctx_, ZSTD_c_checksumFlag, 1);
      obuf_.resize(kSpillBlockBytes);
    }
#endif
    writeHeader(H, maxn, lo_hex, hi_hex, rev);
    if (write_index_) openIndexSidecar();
  }

  ~RunFileWriter() {
    if (fp_) {
      flushWBuf();  // abandoned writer (no finalize): don't strand buffered bytes
      std::fclose(fp_);
    }
    if (idx_fp_) std::fclose(idx_fp_);
#ifdef POLY_ZSTD
    if (cctx_) releaseCStream(cctx_);
#endif
  }

  RunFileWriter(const RunFileWriter&) = delete;
  RunFileWriter& operator=(const RunFileWriter&) = delete;

  void append(const RunRecord<W>& r) {
    if (!fp_) return;
#ifdef POLY_ZSTD
    // Block framing: end the open frame and start a new one every
    // kZstdBlockRecords records. Must run BEFORE the index entry below so the
    // entry records the new frame's start, not a mid-frame position.
    if (block_framed_ && (record_count_ % zstd_block_records_) == 0) {
      if (record_count_ > 0) compressEndFrame();
      frame_offset_ = static_cast<uint64_t>(std::ftell(fp_));
      frame_recidx_ = record_count_;
    }
#endif
    // Sparse seek index: record (key, file-offset, record-index) every stride
    // records, so the merge can seek to a key range instead of scanning to it.
    // Block-framed files store the enclosing FRAME's start offset and first
    // record index — the only positions a zstd body can start decoding from;
    // the seeked reader then skips the in-frame overshoot exactly as the plain
    // path skips its in-stride overshoot.
    if (idx_fp_ && (record_count_ % kIndexStride) == 0) {
      // Stream one index entry straight to the .idx sidecar — no in-RAM buffer.
      uint64_t offset = block_framed_
          ? frame_offset_
          : static_cast<uint64_t>(body_start_offset_) + body_bytes_;
      uint64_t recidx = block_framed_ ? frame_recidx_ : record_count_;
      writeOrDie(r.sig.b, static_cast<size_t>(keyLen_), idx_fp_);
      writeOrDie(&offset, sizeof(offset), idx_fp_);
      writeOrDie(&recidx, sizeof(recidx), idx_fp_);
      ++index_count_;
    }
    // Assemble the whole record in a stack buffer and emit ONCE. Field-at-a-time
    // emit() was ~10-35 stdio calls per record (worst: one per varint byte), and
    // per-call FILE-lock + dispatch overhead dominated map/merge worker busy time
    // (measured ~90% of busy samples on gympie, docs/engine-record.md). Max
    // record size: keyLen<=SIGMAX-2+... sig (<=34) + lo,len (2) + up to
    // (maxn+1)<=40 counts x <=19 varint bytes = well under the 1KB below.
    uint8_t rec[1024];
    size_t n = 0;
    std::memcpy(rec + n, r.sig.b, static_cast<size_t>(keyLen_));
    n += static_cast<size_t>(keyLen_);
    rec[n++] = r.lo;
    rec[n++] = r.len;
    for (int i = 0; i < r.len; ++i) {
      // counts: LEB128 varint each (see encodeVarint in run.h). Max 19 bytes
      // for u128; body_bytes_ tracks actual bytes so the .idx offset above stays
      // exact and range-seeking is unaffected.
      encodeVarint<W>(r.counts[i], [&](uint8_t b) { rec[n++] = b; });
    }
    emit(rec, n);
    ++record_count_;
  }

  // Seek back to placeholder, write real count, append CRC, close.
  // Returns body bytes written.
  size_t finalize() {
    if (!fp_) return 0;
#ifdef POLY_ZSTD
    // Flush the zstd frame (ZSTD_e_end writes the checksum epilogue) so all body
    // bytes are on disk before we seek back into the header to patch the count.
    if (compress_) compressFinish();
#endif
    flushWBuf();
    // FAIL-CLOSED (E1): every leg of finalize is checked, because the ONLY
    // reason the writer streams to a .tmp and renames is so a file that could
    // not be finished is never published. Pre-fix the fseek legs merely warned
    // and the CRC fwrite / fclose were unchecked, so a writer that ran out of
    // disk in its last bytes still renamed a plausible file (stale or
    // placeholder record count, missing CRC trailer) onto the final path — a
    // silent undercount at the next reader, since the header count is what
    // next() trusts.
    if (std::fseek(fp_, records_offset_, SEEK_SET) != 0)
      failWriter("fseek to the record-count placeholder");
    if (std::fprintf(fp_, "%018zu", record_count_) != 18)
      failWriter("record-count backpatch");
    // Compressed files carry no FNV trailer — zstd's frame checksum replaces it.
    if (!compress_) {
      if (std::fseek(fp_, 0, SEEK_END) != 0)
        failWriter("fseek to the body end");
      uint64_t crc = crc_;
      uint8_t crc_bytes[8];
      for (int i = 0; i < 8; ++i) {
        crc_bytes[i] = static_cast<uint8_t>(crc & 0xff);
        crc >>= 8;
      }
      writeOrDie(crc_bytes, 8, fp_);
    }
    // fclose flushes: a buffered short write (ENOSPC, quota, EFBIG) surfaces
    // HERE, not at the fwrite that filled the buffer.
    const int close_rc = std::fclose(fp_);
    fp_ = nullptr;
    if (close_rc != 0) failWriter("fclose");
    // Publish the index sidecar first (to its own temp, then rename), then the
    // data file last: the data file's appearance at the final path is the commit
    // point, and by then its .idx is already in place.  Clear any stale .idx if
    // this run is too small to warrant one.
    if (idx_fp_ && index_count_ > 0) {
      // Backpatch the entry count into the header, then commit the sidecar.
      if (std::fseek(idx_fp_, kRunIndexCountOffset, SEEK_SET) == 0)
        std::fwrite(&index_count_, sizeof(index_count_), 1, idx_fp_);
      std::fclose(idx_fp_);
      idx_fp_ = nullptr;
      std::rename((path_ + ".idx.tmp").c_str(), (path_ + ".idx").c_str());
    } else {
      if (idx_fp_) { std::fclose(idx_fp_); idx_fp_ = nullptr; }
      std::remove((path_ + ".idx.tmp").c_str());
      std::remove((path_ + ".idx").c_str());
    }
    std::rename(tmp_path_.c_str(), path_.c_str());
    return body_bytes_;
  }

  bool ok() const { return fp_ != nullptr; }
  size_t records() const { return record_count_; }

 private:
  int H_;
  int keyLen_;
  FILE* fp_;
  size_t record_count_;
  size_t body_bytes_;
  uint64_t crc_;
  long records_offset_;
  std::string path_;
  std::string tmp_path_;
  bool write_index_;
  bool compress_;
  bool block_framed_ = false;     // compression 2: one zstd frame per block
  size_t zstd_block_records_ = 64;  // frame size in records (set in ctor)
  uint64_t frame_offset_ = 0;     // file offset of the open frame's start
  uint64_t frame_recidx_ = 0;     // record index of the open frame's first record
  long body_start_offset_;          // file offset of the first record (post-header)
  FILE* idx_fp_ = nullptr;        // streamed .idx sidecar (no in-RAM index buffer)
  uint64_t index_count_ = 0;      // entries streamed to idx_fp_
  std::vector<uint8_t> wbuf_;     // plain-path block buffer (lazy, kSpillBlockBytes)
  size_t wpos_ = 0;               // bytes pending in wbuf_
  static constexpr size_t kIndexStride = 64;
#ifdef POLY_ZSTD
  ZSTD_CStream* cctx_ = nullptr;
  std::vector<char> obuf_;        // bounded compressed-output block buffer
#endif

  // FAIL-CLOSED writes: an unchecked short fwrite (ENOSPC, quota, I/O error)
  // silently truncates the body; finalize() would then publish a plausible
  // file whose records vanish with no signal — the same undercount shape the
  // fail-closed open guard exists for. Runs near a disk-headroom gate (H21+)
  // and /dev/shm-routed map outputs make this a real, reachable state, so any
  // failed write aborts loudly instead.
  // FAIL-CLOSED (E1): drop the unfinished .tmp (so no later run can mistake it
  // for salvage) and abort WITHOUT renaming. Never publish.
  [[noreturn]] void failWriter(const char* what) {
    std::fprintf(stderr,
                 "RunFileWriter: %s failed (%s) for %s — not publishing "
                 "(%zu records)\n",
                 what, std::strerror(errno), path_.c_str(), record_count_);
    if (fp_) { std::fclose(fp_); fp_ = nullptr; }
    if (idx_fp_) { std::fclose(idx_fp_); idx_fp_ = nullptr; }
    std::remove(tmp_path_.c_str());
    std::remove((path_ + ".idx.tmp").c_str());
    std::exit(1);
  }

  void writeOrDie(const void* p, size_t n, FILE* f) {
    if (n && std::fwrite(p, 1, n, f) != n) {
      std::fprintf(stderr, "RunFileWriter: write failed (%s) for %s\n",
                   std::strerror(errno), path_.c_str());
      std::exit(1);
    }
  }

  // Emit body bytes: plain files buffer + fold the FNV CRC; compressed files feed
  // the zstd stream (no per-byte CRC — the frame checksum covers integrity).
  // Plain-path bytes accumulate in wbuf_ and hit stdio one block at a time
  // (flushWBuf), not one field at a time — see append()'s measurement note.
  void emit(const void* p, size_t n) {
#ifdef POLY_ZSTD
    if (compress_) {
      ZSTD_inBuffer in{p, n, 0};
      while (in.pos < in.size) {
        ZSTD_outBuffer out{obuf_.data(), obuf_.size(), 0};
        size_t r = ZSTD_compressStream2(cctx_, &out, &in, ZSTD_e_continue);
        // FAIL-CLOSED (E1): returning here dropped this record's bytes into a
        // body that still gets published and counted — a silent undercount.
        if (ZSTD_isError(r)) {
          std::fprintf(stderr, "RunFileWriter: zstd compress: %s\n",
                       ZSTD_getErrorName(r));
          failWriter("zstd compress");
        }
        if (out.pos) writeOrDie(obuf_.data(), out.pos, fp_);
      }
      body_bytes_ += n;
      return;
    }
#endif
    if (wbuf_.empty()) wbuf_.resize(kSpillBlockBytes);
    if (wpos_ + n > wbuf_.size()) flushWBuf();
    if (n >= wbuf_.size()) {
      // Oversized single emit (never happens for records, defensive): write direct.
      writeOrDie(p, n, fp_);
    } else {
      std::memcpy(wbuf_.data() + wpos_, p, n);
      wpos_ += n;
    }
    crc_ = fnv1a64_update(crc_, p, n);
    body_bytes_ += n;
  }

  // Flush the plain-path block buffer to stdio. Must run before any fseek on
  // fp_ (finalize's count backpatch / CRC trailer) and before close.
  void flushWBuf() {
    if (wpos_) {
      writeOrDie(wbuf_.data(), wpos_, fp_);
      wpos_ = 0;
    }
  }

#ifdef POLY_ZSTD
  // End the open zstd frame (writes buffered output + the frame checksum) and
  // leave cctx_ ready to start the next frame — the block-framing rollover.
  // After ZSTD_e_end returns 0 the stream context begins a fresh frame on the
  // next ZSTD_e_continue call; parameters (level, checksum) persist.
  void compressEndFrame() {
    if (!cctx_) return;
    ZSTD_inBuffer in{nullptr, 0, 0};
    size_t rem;
    do {
      ZSTD_outBuffer out{obuf_.data(), obuf_.size(), 0};
      rem = ZSTD_compressStream2(cctx_, &out, &in, ZSTD_e_end);
      // FAIL-CLOSED (E1): breaking left the frame unterminated (no checksum
      // epilogue) in a file that would still be published.
      if (ZSTD_isError(rem)) {
        std::fprintf(stderr, "RunFileWriter: zstd flush: %s\n",
                     ZSTD_getErrorName(rem));
        failWriter("zstd frame flush");
      }
      if (out.pos) writeOrDie(obuf_.data(), out.pos, fp_);
    } while (rem != 0);
    // No fflush here: ftell(fp_) — the next frame's .idx offset — is exact on
    // a buffered write stream, and flushing per ~8KB frame would turn every
    // frame into a write syscall.
  }

  // Flush the final zstd frame and retire the compression context (finalize).
  void compressFinish() {
    if (!cctx_) return;
    compressEndFrame();
    releaseCStream(cctx_);
    cctx_ = nullptr;
  }
#endif

  // Open the <path>.idx.tmp sidecar and write its header with a PLACEHOLDER count
  // (backpatched in finalize). Entries are then streamed in append() — there is no
  // in-RAM index buffer (Index Hoard: records/64 × 80B held to finalize was an OOM
  // lever at scale). Format unchanged: [u32 magic][u16 ver][u8 bo][u32 keyLen]
  // [u64 count]{ key[keyLen] u64 offset u64 recidx }*, native byte order.
  void openIndexSidecar() {
    idx_fp_ = std::fopen((path_ + ".idx.tmp").c_str(), "wb");
    if (!idx_fp_) return;
    uint32_t magic = kRunIndexMagic;
    uint16_t ver   = kRunIndexVersion;
    uint8_t  bo    = kRunByteOrderLE;
    uint32_t kl    = static_cast<uint32_t>(keyLen_);
    uint64_t cnt   = 0; // placeholder
    std::fwrite(&magic, sizeof(magic), 1, idx_fp_);
    std::fwrite(&ver,   sizeof(ver),   1, idx_fp_);
    std::fwrite(&bo,    sizeof(bo),    1, idx_fp_);
    std::fwrite(&kl,    sizeof(kl),    1, idx_fp_);
    std::fwrite(&cnt,   sizeof(cnt),   1, idx_fp_);
  }

  void writeHeader(int H, int maxn, const std::string& lo_hex,
                   const std::string& hi_hex, const std::string& rev) {
    // Plain files stay "POLYRUN 1" with no compression line (byte-identical to
    // the pre-compression format); compressed spills bump to "POLYRUN 2" and add
    // a "compression 1" line before the blank header terminator.
    std::fprintf(fp_, "POLYRUN %d\n", compress_ ? 2 : 1);
    std::fprintf(fp_, "height %d\n", H);
    std::fprintf(fp_, "maxn %d\n", maxn);
    std::fprintf(fp_, "counter %s\n", counterTag<W>());
    std::fprintf(fp_, "classifier triangle\n");
    std::fprintf(fp_, "keylo %s\n", lo_hex.c_str());
    std::fprintf(fp_, "keyhi %s\n", hi_hex.c_str());
    std::fflush(fp_);
    records_offset_ = std::ftell(fp_) + static_cast<long>(std::strlen("records "));
    std::fprintf(fp_, "records 000000000000000000\n");
    std::fprintf(fp_, "rev %s\n", rev.empty() ? "unknown" : rev.c_str());
    std::fprintf(fp_, "byteorder 1\n");
    if (compress_) std::fprintf(fp_, "compression %d\n", block_framed_ ? 2 : 1);
    std::fprintf(fp_, "\n");
    std::fflush(fp_);
    body_start_offset_ = std::ftell(fp_);
  }
};

// ─── RunFileReader ────────────────────────────────────────────────────────────

template <class W>
class RunFileReader {
 public:
  // keyLen defaults to 0 which means H+2 (triangle path); pass H+3 for holes.
  RunFileReader(const std::string& path, int H, int keyLen = 0)
      : H_(H), keyLen_((keyLen == 0) ? H + 2 : keyLen),
        fp_(nullptr), records_(0), records_read_(0),
        crc_(FNV_OFFSET), path_(path), seeked_(false),
        compressed_(false) {
    requireKeyLenFits(keyLen_, "RunFileReader");
    fp_ = std::fopen(path.c_str(), "rb");
    if (!fp_) {
      std::fprintf(stderr, "RunFileReader: cannot open %s\n", path.c_str());
      return;
    }
    // Small stdio buffer: only the text header goes through stdio's buffer
    // (body reads are explicit >=kFirstFillBytes freads, which glibc serves
    // directly). The default 4KB buffer made every open cost a 4KB read —
    // material at merge fan-in scale, where a round is ranges x inputs opens
    // for one-record peeks (Fan-In Tax, docs/engine-record.md).
    std::setvbuf(fp_, nullptr, _IOFBF, 512);
    if (!parseHeader()) {
      std::fprintf(stderr, "RunFileReader: bad header in %s\n", path.c_str());
      std::fclose(fp_);
      fp_ = nullptr;
      records_ = 0;
    }
  }

  ~RunFileReader() {
    if (fp_) std::fclose(fp_);
#ifdef POLY_ZSTD
    if (dctx_) releaseDStream(dctx_);
#endif
  }

  RunFileReader(const RunFileReader&) = delete;
  RunFileReader& operator=(const RunFileReader&) = delete;

  // The ONLY legitimate false from next() is "the header's record count has
  // been reached" (checked first). Everything else — a body that ran out, a
  // zstd decode or frame-checksum failure — is corruption, and E1 ("Short
  // Shrift") is what happens if it merely returns false: every caller
  // (mergeRunFiles' heap refill, map_shard_file, map_shard_stage_file) reads
  // false as "input exhausted", so a truncated or bit-rotted shard silently
  // contributes fewer records than its own header claims. Measured on the
  // pre-fix code: a 500-byte truncation gave 2945 of 3000 records through a
  // merge, and one flipped byte in a compression-2 file cut a seeked read off
  // at 1024 of 3000 — both with exit status 0. Reachable via ENOSPC on the
  // size-capped tmpfs the a(40) run used, so it fails closed instead.
  bool next(RunRecord<W>& out) {
    if (!fp_ || records_read_ >= records_) return false;
    out.sig = Sig{};
    if (!bodyRead(out.sig.b, static_cast<size_t>(keyLen_))) failShort("signature");

    uint8_t lo = 0, len = 0;
    if (!bodyRead(&lo,  1)) failShort("lo");
    if (!bodyRead(&len, 1)) failShort("len");

    out.H      = H_;
    out.keyLen = keyLen_;
    out.lo     = lo;
    out.len    = len;
    out.counts.resize(len);
    for (int i = 0; i < len; ++i) {
      // counts: LEB128 varint each; read byte-by-byte, bounds-checked by bodyRead.
      W v = 0;
      unsigned shift = 0;
      uint8_t byte;
      do {
        if (!bodyRead(&byte, 1)) failShort("count varint");
        // WIDTH-BOUNDED (V3), mirroring core/run.h's decodeVarint: a corrupt
        // run of continuation bytes must not shift past the counter width.
        if (shift >= 8 * sizeof(W)) failShort("over-wide count varint");
        v |= (static_cast<W>(byte & 0x7f) << shift);
        shift += 7;
      } while (byte & 0x80);
      out.counts[i] = v;
    }
    ++records_read_;
    // CRC contract (B3): a seeked reader covers only a key-slice, so its running
    // CRC is partial and CANNOT match the whole-body trailer — the body CRC is
    // therefore verified ONLY on a full (non-seeked) read to completion. Bounded
    // units and merges seek, so production reads intentionally skip it here. The
    // corruption backstop for those is an out-of-band FULL read: verify.go
    // (independent, recomputes the whole-body FNV and FAILS on mismatch) and
    // runcat (per-file, exits nonzero on mismatch). B4's atomic publish removes
    // the torn-file hazard that made a skipped seek-read dangerous.
    if (records_read_ == records_ && !seeked_) {
#ifdef POLY_ZSTD
      // Compressed files: no FNV trailer. Drain the frame epilogue so zstd
      // validates its checksum (replaces the FNV backstop for these files).
      if (compressed_) zfinish();
      else verifyCRC();
#else
      verifyCRC();
#endif
    }
    return true;
  }

  // Seek so the next next() starts at the last indexed record with key <= klo
  // (the caller skips the small in-block overshoot below klo). BINARY-SEARCHES the
  // .idx sidecar ON DISK (fixed-width entries → direct offsets) — never loads the
  // whole index into RAM (Index Slurp). Returns false / no-op if the index is
  // absent (the caller falls back to a scan).
  bool seekToKey(const uint8_t* klo) {
    if (!fp_) return false;
    FILE* f = std::fopen((path_ + ".idx").c_str(), "rb");
    if (!f) return false;
    // Each binary-search probe is a ~20-byte fread at a seeked offset; the
    // default 4KB stdio buffer turned every probe into a 4KB read (~14 probes
    // x 4KB per open at merge fan-in scale). 512B per probe is plenty.
    std::setvbuf(f, nullptr, _IOFBF, 512);
    uint32_t magic = 0; uint16_t ver = 0; uint8_t bo = 0; uint32_t kl = 0; uint64_t cnt = 0;
    if (std::fread(&magic, sizeof(magic), 1, f) != 1 || std::fread(&ver, sizeof(ver), 1, f) != 1 ||
        std::fread(&bo, sizeof(bo), 1, f) != 1 || magic != kRunIndexMagic ||
        ver != kRunIndexVersion || bo != kRunByteOrderLE ||
        std::fread(&kl, sizeof(kl), 1, f) != 1 || std::fread(&cnt, sizeof(cnt), 1, f) != 1 ||
        static_cast<int>(kl) != keyLen_ || cnt == 0) {
      std::fclose(f); return false;
    }
    const long hdr = kRunIndexHeaderLen;
    const long entryLen = static_cast<long>(keyLen_) + 16; // key + u64 offset + u64 recidx
    uint8_t key[SIGMAX];   // V5: sized by the key width, not a hardcoded 64
                           // (requireKeyLenFits in the ctor guarantees the fit)
    auto keyAt = [&](long i) -> bool {
      return std::fseek(f, hdr + i * entryLen, SEEK_SET) == 0 &&
             std::fread(key, 1, static_cast<size_t>(keyLen_), f) == static_cast<size_t>(keyLen_);
    };
    long a = 0, b = static_cast<long>(cnt) - 1, s = 0;     // last entry with key <= klo
    while (a <= b) {
      long m = (a + b) / 2;
      if (!keyAt(m)) { std::fclose(f); return false; }
      if (sigCmp(key, klo, keyLen_) <= 0) { s = m; a = m + 1; }
      else b = m - 1;
    }
    uint64_t offset = 0, recidx = 0;                       // entry s's offset + recidx
    if (std::fseek(f, hdr + s * entryLen + keyLen_, SEEK_SET) != 0 ||
        std::fread(&offset, sizeof(offset), 1, f) != 1 ||
        std::fread(&recidx, sizeof(recidx), 1, f) != 1) {
      std::fclose(f); return false;
    }
    std::fclose(f);
#ifdef POLY_ZSTD
    // Compressed bodies: only block-framed files are seekable (their .idx
    // offsets are frame starts). Single-frame spill files never carry an .idx,
    // so this guard is unreachable in practice — belt and braces.
    if (compressed_ && !block_framed_) return false;
#endif
    if (std::fseek(fp_, static_cast<long>(offset), SEEK_SET) != 0) return false;
    rpos_ = rlen_ = 0;  // drop the block buffer: its bytes predate the seek
    next_fill_ = kFirstFillBytes;  // post-seek reads are peek-sized until proven streaming
#ifdef POLY_ZSTD
    if (compressed_) {
      // The seek target is a frame start: reset the stream session and drop
      // buffered compressed/decompressed bytes — they predate the seek.
      ZSTD_DCtx_reset(dctx_, ZSTD_reset_session_only);
      in_.size = in_.pos = 0;
      dpos_ = dlen_ = 0;
      zhint_ = 1;
      zin_fill_ = zout_fill_ = kFirstFillBytes;  // post-seek reads are peeks
    }
#endif
    records_read_ = recidx;
    seeked_ = true;
    return true;
  }

  // ok() is false if the file could not be opened or its header was bad. A
  // legitimately empty run file still opens (ok()==true, records()==0), so this
  // distinguishes "no data" from "could not read" — the latter must abort the
  // worker rather than silently contribute zero records.
  bool   ok()      const { return fp_ != nullptr; }
  size_t records() const { return records_; }
  int    H()       const { return H_; }
  int    keyLen()  const { return keyLen_; }

 private:
  int H_;
  int keyLen_;
  FILE* fp_;
  size_t records_;
  size_t records_read_;
  uint64_t crc_;
  std::string path_;
  bool seeked_;
  bool compressed_;
  bool block_framed_ = false;       // compression 2: independent frames, seekable
  std::vector<uint8_t> rbuf_;       // plain-path block buffer (lazy, kSpillBlockBytes)
  size_t rpos_ = 0, rlen_ = 0;      // consumed / valid bytes in rbuf_
  size_t next_fill_ = kFirstFillBytes;  // adaptive fill size, doubles to kSpillBlockBytes
#ifdef POLY_ZSTD
  ZSTD_DStream* dctx_ = nullptr;
  std::vector<char> cbuf_;          // bounded compressed-input block buffer (adaptive)
  ZSTD_inBuffer in_{nullptr, 0, 0}; // persists leftover compressed bytes across reads
  size_t zhint_ = 1;                // last ZSTD_decompressStream return; 0 = frame done
  std::vector<uint8_t> dbuf_;       // decompressed-output block buffer (adaptive)
  size_t dpos_ = 0, dlen_ = 0;      // consumed / valid bytes in dbuf_
  size_t zin_fill_ = kFirstFillBytes;   // adaptive compressed-input fill size
  size_t zout_fill_ = kFirstFillBytes;  // adaptive decompressed-output size
#endif

  // FAIL-CLOSED short/corrupt body (E1): the body could not supply a record the
  // header promised. There is nowhere legitimate to go from here — the caller
  // cannot distinguish this from a clean end (that is the whole bug), and a
  // partial input is exactly the silent-undercount shape the fail-closed
  // writer/open guards exist for. `what` names the field that ran out, so the
  // log says how far the body got.
  [[noreturn]] void failShort(const char* what) {
    std::fprintf(stderr,
                 "RunFileReader: SHORT READ in %s: body ended or failed to "
                 "decode at record %zu of %zu (%s) — truncated, corrupt, or "
                 "lost to ENOSPC\n",
                 path_.c_str(), records_read_, records_, what);
    std::exit(1);
  }

  // Read body bytes: plain files from a block buffer + fold the FNV CRC;
  // compressed files from a decompressed block buffer fed by the zstd stream.
  // Field-at-a-time fread (worst: one locked stdio call per varint BYTE) was
  // ~60% of map-worker busy samples (docs/engine-record.md); both paths now
  // hit stdio/zstd one kSpillBlockBytes block at a time.
  bool bodyRead(void* dst, size_t n) {
#ifdef POLY_ZSTD
    if (compressed_) {
      uint8_t* d = static_cast<uint8_t*>(dst);
      while (n) {
        if (dpos_ == dlen_ && !refillD()) return false;
        size_t take = std::min(n, dlen_ - dpos_);
        std::memcpy(d, dbuf_.data() + dpos_, take);
        dpos_ += take; d += take; n -= take;
      }
      return true;
    }
#endif
    if (!rawRead(dst, n)) return false;
    crc_ = fnv1a64_update(crc_, dst, n);
    return true;
  }

  // Serve n bytes from the plain-path block buffer without folding the CRC
  // (verifyCRC uses this for the 8-byte trailer, which is not body). Refills
  // rbuf_ with one big fread per block.
  bool rawRead(void* dst, size_t n) {
    uint8_t* d = static_cast<uint8_t*>(dst);
    while (n) {
      if (rpos_ == rlen_) {
        // Adaptive fill: start small after open/seek, double toward the full
        // block. A streaming reader reaches kSpillBlockBytes within a few
        // fills; a merge-fan-in peek (open, seek, read one record to seed the
        // k-way heap) pays kFirstFillBytes instead of a full 256KB block.
        // The BUFFER grows with the fill for the same reason: a fixed 256KB
        // vector per reader put every allocation over glibc's mmap threshold,
        // so ranges x inputs reader instances per round each paid an
        // mmap+page-zero+munmap cycle (gdb-sampled as brk/sbrk churn in
        // reader destructors; Fan-In Tax, docs/engine-record.md). An 8KB peek
        // buffer stays arena-served and gets reused across readers.
        const size_t want = std::min(next_fill_, kSpillBlockBytes);
        if (rbuf_.size() < want) rbuf_.resize(want);
        rlen_ = std::fread(rbuf_.data(), 1, want, fp_);
        next_fill_ = std::min(next_fill_ * 2, kSpillBlockBytes);
        rpos_ = 0;
        if (rlen_ == 0) return false;  // EOF/short file
      }
      size_t take = std::min(n, rlen_ - rpos_);
      std::memcpy(d, rbuf_.data() + rpos_, take);
      rpos_ += take; d += take; n -= take;
    }
    return true;
  }

#ifdef POLY_ZSTD
  // Refill the decompressed-output block buffer from the zstd stream (refilling
  // the compressed-input block from the file as needed). Returns false if no
  // more decompressed bytes are available (EOF/truncated frame).
  // BOTH buffers fill adaptively (kFirstFillBytes doubling to
  // kSpillBlockBytes, reset on open/seek) for the same reason as rawRead's
  // plain path: a merge heap-init peek is (ranges x inputs) reader opens per
  // round, and a fixed 256KB read+decompress per open re-created the Fan-In
  // Tax through the compressed path — measured 4.7x wall on the gympie
  // H15/maxn30 bench before this fix.
  bool refillD() {
    const size_t dwant = std::min(zout_fill_, kZReaderMaxFill);
    if (dbuf_.size() < dwant) dbuf_.resize(dwant);
    zout_fill_ = std::min(zout_fill_ * 2, kZReaderMaxFill);
    dpos_ = dlen_ = 0;
    while (dlen_ == 0) {
      if (in_.pos == in_.size) {
        // Safe to resize here: in_ is fully consumed, so no live pointers
        // into cbuf_ survive the (possible) reallocation.
        const size_t want = std::min(zin_fill_, kZReaderMaxFill);
        if (cbuf_.size() < want) cbuf_.resize(want);
        zin_fill_ = std::min(zin_fill_ * 2, kZReaderMaxFill);
        size_t r = std::fread(cbuf_.data(), 1, want, fp_);
        in_.src = cbuf_.data(); in_.size = r; in_.pos = 0;
        if (r == 0) return false;  // needed more but hit EOF (truncated frame)
      }
      ZSTD_outBuffer out{dbuf_.data(), dwant, 0};
      zhint_ = ZSTD_decompressStream(dctx_, &out, &in_);
      if (ZSTD_isError(zhint_)) {
        std::fprintf(stderr, "RunFileReader: zstd decompress: %s\n",
                     ZSTD_getErrorName(zhint_));
        return false;
      }
      dlen_ = out.pos;
      // Frame end with no output: a single-frame body is done (EOF for the
      // caller), but a block-framed body may have the NEXT frame right behind
      // it — loop on: leftover in_ bytes (or the next file read) feed the new
      // frame, and ZSTD_decompressStream starts it in place. Termination is
      // still the fread()==0 EOF above; next() never asks past records_.
      if (zhint_ == 0 && dlen_ == 0 && !block_framed_) return false;
    }
    return true;
  }
#endif

#ifdef POLY_ZSTD
  // After the last record, consume the frame epilogue so zstd verifies the frame
  // checksum. A clean frame ends with ZSTD_decompressStream returning 0.
  void zfinish() {
    if (!dctx_) return;
    // The last record's decompress may already have completed the frame (and
    // validated the checksum) — zhint_==0 then, nothing more to do. Otherwise
    // push the remaining epilogue bytes until zstd reports the frame complete.
    char scratch[16];
    while (zhint_ != 0) {
      if (in_.pos == in_.size) {
        if (cbuf_.empty()) cbuf_.resize(kFirstFillBytes);
        size_t r = std::fread(cbuf_.data(), 1, cbuf_.size(), fp_);
        in_.src = cbuf_.data(); in_.size = r; in_.pos = 0;
        if (r == 0) break;
      }
      ZSTD_outBuffer out{scratch, sizeof(scratch), 0};
      zhint_ = ZSTD_decompressStream(dctx_, &out, &in_);
      // FAIL-CLOSED (E1): for compressed files the frame checksum IS the
      // integrity check (they carry no FNV trailer), so a failure here must
      // abort — warning and returning would leave the checksum decorative.
      if (ZSTD_isError(zhint_)) {
        std::fprintf(stderr, "RunFileReader: %s: zstd frame check failed: %s\n",
                     path_.c_str(), ZSTD_getErrorName(zhint_));
        std::exit(1);
      }
    }
    if (zhint_ != 0) {
      std::fprintf(stderr,
                   "RunFileReader: %s: zstd frame incomplete at EOF "
                   "(truncated body)\n", path_.c_str());
      std::exit(1);
    }
  }
#endif

  bool parseHeader() {
    char line[512];
    bool saw_polyrun = false;
    bool byteorder_ok = true;
    bool counter_ok = true;
    while (std::fgets(line, sizeof(line), fp_)) {
      size_t ln = std::strlen(line);
      while (ln > 0 && (line[ln-1] == '\n' || line[ln-1] == '\r'))
        line[--ln] = '\0';
      if (ln == 0) break;  // blank line = end of header
      if (std::strncmp(line, "POLYRUN ", 8) == 0) {
        saw_polyrun = true;
      }
      else if (std::strncmp(line, "compression ", 12) == 0) {
        // Absent = 0 (plain, old files). 1 = single zstd frame (unindexed
        // spill). 2 = block-framed zstd (indexed frontier; .idx offsets are
        // frame starts). Anything else is from a newer format: REJECT rather
        // than misread the body as plain bytes.
        int cv = std::atoi(line + 12);
        compressed_   = (cv >= 1);
        block_framed_ = (cv == 2);
        if (cv < 0 || cv > 2) {
          std::fprintf(stderr,
                       "RunFileReader: %s has unknown compression %d "
                       "(newer format? rebuild required)\n", path_.c_str(), cv);
          return false;
        }
      }
      else if (std::strncmp(line, "records ", 8) == 0)
        records_ = static_cast<size_t>(std::strtoull(line + 8, nullptr, 10));
      else if (std::strncmp(line, "byteorder ", 10) == 0)
        // Self-describing (D6): the body is canonically little-endian; a file
        // claiming any other order is rejected rather than silently misread.
        byteorder_ok = (std::atoi(line + 10) == kRunByteOrderLE);
      else if (std::strncmp(line, "counter ", 8) == 0)
        // Reject a counter tag that doesn't match this reader's word width
        // (e.g. reading a u128 file as u64) instead of misparsing the records.
        counter_ok = (std::strcmp(line + 8, counterTag<W>()) == 0);
      // height, maxn, classifier, keylo, keyhi, rev: not validated here
    }
    if (compressed_) {
#ifdef POLY_ZSTD
      dctx_ = acquireDStream();
      // cbuf_ stays empty here: refillD sizes it adaptively from
      // kFirstFillBytes so a one-record peek never pays a 256KB alloc+read.
      in_ = ZSTD_inBuffer{nullptr, 0, 0};
#else
      std::fprintf(stderr,
                   "RunFileReader: %s is zstd-compressed but this build lacks "
                   "POLY_ZSTD (rebuild with -DPOLY_ZSTD -lzstd)\n", path_.c_str());
      return false;
#endif
    }
    return saw_polyrun && byteorder_ok && counter_ok;
  }

  void verifyCRC() {
    if (!fp_) return;
    uint8_t stored[8];
    // rawRead, not fread: the trailer bytes are usually already in rbuf_.
    if (!rawRead(stored, 8)) {
      std::fprintf(stderr, "RunFileReader: CRC missing or truncated\n");
      return;
    }
    uint64_t stored_crc = 0;
    for (int i = 0; i < 8; ++i)
      stored_crc |= static_cast<uint64_t>(stored[i]) << (8 * i);
    if (stored_crc != crc_) {
      std::fprintf(stderr,
                   "RunFileReader: CRC mismatch (expected %016llx got %016llx)\n",
                   (unsigned long long)crc_, (unsigned long long)stored_crc);
    }
  }
};

// ─── mergeRunFiles ────────────────────────────────────────────────────────────
//
// K-way merge of sorted POLYRUN files into one output file.
// Skips records with sig < lo_hex (if non-empty); stops at sig >= hi_hex.
// Returns {body bytes written, record count} for out_path (count threaded out
// of the writer so callers never reopen the file just to count it).

// Progress/stop stride for mergeRunFiles' cooperative interrupt -- same
// 1024 cadence as core/kink.h's kKinkProgressStrideMask, for the same
// reason (cheap enough to check every time; a counter/gate around it costs
// more than the check itself, see experiments/bench_viablemask.cpp's
// counter-gating finding).
static constexpr unsigned kMergeProgressStrideMask = (1u << 10) - 1;

// keyLen defaults to 0 which means H+2 (triangle path); pass H+3 for holes.
//
// terminate/stop_key_out (both optional, nullptr = no steal support, the
// original behavior): mergeRunFiles is a k-way heap merge, so unlike a
// mid-record enumeration (kink's viableRec-shaped problem, deliberately
// NOT given an interrupt point -- see docs/engine-record.md),
// its "resume" semantics are simple and already native to this function:
// stopping early just means "everything with sig < stop_key has been
// written; call mergeRunFiles again with lo_hex=stop_key to cover the
// rest" -- exactly the seekToKey fast path this function already uses for
// its normal lo bound. No partial-tree-state problem, no new resume
// concept needed.
template <class W>
std::pair<size_t, size_t> mergeRunFiles(
    const std::vector<std::string>& in_paths, int H,
    const std::string& lo_hex, const std::string& hi_hex,
    const std::string& out_path, const std::string& rev = "",
    int keyLen = 0,
    const std::function<void(size_t)>& on_progress = {},
    volatile std::sig_atomic_t* terminate = nullptr,
    std::string* stop_key_out = nullptr) {
  if (keyLen == 0) keyLen = H + 2;
  requireKeyLenFits(keyLen, "mergeRunFiles");
  uint8_t lo_sig[SIGMAX] = {};
  uint8_t hi_sig[SIGMAX] = {};
  bool has_lo = parseKeyBound(lo_hex, lo_sig, keyLen, "mergeRunFiles", "lo");
  bool has_hi = parseKeyBound(hi_hex, hi_sig, keyLen, "mergeRunFiles", "hi");

  std::vector<std::unique_ptr<RunFileReader<W>>> readers;
  readers.reserve(in_paths.size());
  for (const auto& p : in_paths) {
    readers.push_back(std::make_unique<RunFileReader<W>>(p, H, keyLen));
    // FAIL-CLOSED: a merge input that can't be opened must abort, not be
    // treated as an empty shard — its records would vanish from the merged
    // count with no signal. Matches the map-phase reader checks
    // (core/mapreduce.h, core/kink.h, worker/map_worker.cpp).
    if (!readers.back()->ok()) {
      std::fprintf(stderr, "mergeRunFiles: cannot read input %s\n", p.c_str());
      std::exit(1);
    }
  }

  // Read-amplification fix: seek each input to klo via its sparse index instead
  // of reading from the start and skipping below klo. Without this, M workers
  // each rescan ~total/2 records (the ~M/2 amplification, measured 160x at
  // mult=4); with it, each reads only its [klo,khi) slice. No-op if a run has no
  // index (falls back to scan), so it stays correct on un-indexed inputs.
  if (has_lo && !std::getenv("POLY_NO_SEEK"))   // toggle off to A/B the old scan path
    for (auto& r : readers) r->seekToKey(lo_sig);

  struct Cursor {
    RunRecord<W> rec;
    int idx;
    bool operator>(const Cursor& o) const {
      return sigCmp(rec.sig.b, o.rec.sig.b, rec.keyLen) > 0;
    }
  };
  using MinHeap = std::priority_queue<Cursor, std::vector<Cursor>,
                                      std::greater<Cursor>>;
  MinHeap heap;
  for (int i = 0; i < static_cast<int>(readers.size()); ++i) {
    Cursor c;
    c.idx = i;
    if (readers[i]->next(c.rec))
      heap.push(std::move(c));
  }

  RunFileWriter<W> writer(out_path, H, 0, lo_hex, hi_hex, rev, keyLen,
                          /*write_index=*/true, /*compress=*/frontierZstd());

#ifdef POLY_PROFILE
  // Split the merge into read+heap (memcmp), combine, and write (FNV+fwrite).
  double prof_read_s = 0, prof_combine_s = 0, prof_write_s = 0;
  uint64_t prof_combines = 0;
  const double prof_t0 = prof::now();
#endif
  size_t written = 0;
  while (!heap.empty()) {
#ifdef POLY_PROFILE
    const double _tr = prof::now();
#endif
    Cursor top = heap.top();
    heap.pop();

    {
      Cursor nc;
      nc.idx = top.idx;
      if (readers[top.idx]->next(nc.rec))
        heap.push(std::move(nc));
    }

    if (has_lo &&
        sigCmp(top.rec.sig.b, lo_sig, keyLen) < 0)
      continue;
    if (has_hi &&
        sigCmp(top.rec.sig.b, hi_sig, keyLen) >= 0)
      break;

    // Cooperative stop (work-stealing): checked at the same cadence as the
    // progress callback, BEFORE this record's combine/write, so [lo,
    // stop_key) is exactly what's been written when we break -- the
    // resumer re-merges the same inputs with lo_hex=stop_key, using the
    // seekToKey fast path above, same as any other range boundary.
    const bool atStride = (written & kMergeProgressStrideMask) == 0;
    if (terminate && atStride && written > 0 && *terminate) {
      if (stop_key_out) *stop_key_out = bytesToHex(top.rec.sig.b, keyLen);
      break;
    }
    if (on_progress && atStride) {
      on_progress(written);
    }

#ifdef POLY_PROFILE
    prof_read_s += prof::now() - _tr;
    const double _tc = prof::now();
#endif
    while (!heap.empty()) {
      if (sigCmp(top.rec.sig.b, heap.top().rec.sig.b, keyLen) != 0) break;
      Cursor eq = heap.top();
      heap.pop();
      top.rec.combine(eq.rec);
      Cursor nc;
      nc.idx = eq.idx;
      if (readers[eq.idx]->next(nc.rec))
        heap.push(std::move(nc));
#ifdef POLY_PROFILE
      ++prof_combines;
#endif
    }

#ifdef POLY_PROFILE
    prof_combine_s += prof::now() - _tc;
    const double _tw = prof::now();
#endif
    writer.append(top.rec);
    ++written;
#ifdef POLY_PROFILE
    prof_write_s += prof::now() - _tw;
#endif
  }

  size_t body_bytes = writer.finalize();
#ifdef POLY_PROFILE
  {
    char line[512];
    std::snprintf(line, sizeof(line),
      "mergephase site=%s H=%d K=%zu out_recs=%zu combines=%llu "
      "read_s=%.4f combine_s=%.4f write_s=%.4f total_s=%.4f peak_rss_mb=%.1f",
      prof::site(), H, in_paths.size(), writer.records(),
      (unsigned long long)prof_combines,
      prof_read_s, prof_combine_s, prof_write_s, prof::now() - prof_t0,
      prof::peakRssMB());
    prof::emit(line);
  }
#endif
  return {body_bytes, writer.records()};
}
