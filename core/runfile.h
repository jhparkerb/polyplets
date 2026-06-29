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

#include <algorithm>
#include <cstdio>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <memory>
#include <queue>
#include <string>
#include <utility>
#include <vector>

#include "core/run.h"

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

template <class W>
class RunFileWriter {
 public:
  // Real writer: opens file, writes header with placeholder record count.
  // keyLen defaults to 0 which means H+2 (triangle path); pass H+3 for holes.
  RunFileWriter(const std::string& path, int H, int maxn,
                const std::string& lo_hex, const std::string& hi_hex,
                const std::string& rev = "", int keyLen = 0,
                bool write_index = true)
      : H_(H), keyLen_((keyLen == 0) ? H + 2 : keyLen),
        fp_(nullptr), record_count_(0), body_bytes_(0),
        crc_(FNV_OFFSET), records_offset_(0),
        path_(path), tmp_path_(path + ".tmp"),
        write_index_(write_index), body_start_offset_(0) {
    // Atomic publish (B4): stream to a temp file and rename onto the final path
    // in finalize().  A kill mid-write then leaves only a stale .tmp; the real
    // path never holds a placeholder record-count or a short CRC (which a seeked
    // read, skipping the body CRC, would otherwise consume as garbage).
    fp_ = std::fopen(tmp_path_.c_str(), "wb");
    if (!fp_) {
      std::fprintf(stderr, "RunFileWriter: cannot open %s\n", tmp_path_.c_str());
      return;
    }
    writeHeader(H, maxn, lo_hex, hi_hex, rev);
  }

  // Default constructor: no-op.
  RunFileWriter()
      : H_(0), keyLen_(2), fp_(nullptr), record_count_(0), body_bytes_(0),
        crc_(FNV_OFFSET), records_offset_(0) {}

  ~RunFileWriter() {
    if (fp_) std::fclose(fp_);
  }

  RunFileWriter(const RunFileWriter&) = delete;
  RunFileWriter& operator=(const RunFileWriter&) = delete;

  void append(const RunRecord<W>& r) {
    if (!fp_) return;
    // Sparse seek index: record (key, file-offset, record-index) every stride
    // records, so the merge can seek to a key range instead of scanning to it.
    if (write_index_ && (record_count_ % kIndexStride) == 0) {
      IdxEnt e;
      std::memset(e.key, 0, sizeof(e.key));
      std::memcpy(e.key, r.sig.b, static_cast<size_t>(keyLen_));
      e.offset = static_cast<uint64_t>(body_start_offset_) + body_bytes_;
      e.recidx = record_count_;
      index_.push_back(e);
    }
    std::fwrite(r.sig.b, 1, static_cast<size_t>(keyLen_), fp_);
    uint8_t lo  = r.lo;
    uint8_t len = r.len;
    std::fwrite(&lo,  1, 1, fp_);
    std::fwrite(&len, 1, 1, fp_);
    crc_ = fnv1a64_update(crc_, r.sig.b, static_cast<size_t>(keyLen_));
    crc_ = fnv1a64_update(crc_, &lo,  1);
    crc_ = fnv1a64_update(crc_, &len, 1);
    body_bytes_ += static_cast<size_t>(keyLen_) + 2;
    for (int i = 0; i < r.len; ++i) {
      W v = r.counts[i];
      uint8_t bytes[sizeof(W)];
      for (size_t b = 0; b < sizeof(W); ++b) {
        bytes[b] = static_cast<uint8_t>(v & 0xff);
        v >>= 8;
      }
      std::fwrite(bytes, 1, sizeof(W), fp_);
      crc_ = fnv1a64_update(crc_, bytes, sizeof(W));
      body_bytes_ += sizeof(W);
    }
    ++record_count_;
  }

  // Seek back to placeholder, write real count, append CRC, close.
  // Returns body bytes written.
  size_t finalize() {
    if (!fp_) return 0;
    if (std::fseek(fp_, records_offset_, SEEK_SET) != 0)
      std::fprintf(stderr, "RunFileWriter: fseek failed\n");
    else
      std::fprintf(fp_, "%018zu", record_count_);
    if (std::fseek(fp_, 0, SEEK_END) != 0)
      std::fprintf(stderr, "RunFileWriter: fseek-end failed\n");
    uint64_t crc = crc_;
    uint8_t crc_bytes[8];
    for (int i = 0; i < 8; ++i) {
      crc_bytes[i] = static_cast<uint8_t>(crc & 0xff);
      crc >>= 8;
    }
    std::fwrite(crc_bytes, 1, 8, fp_);
    std::fclose(fp_);
    fp_ = nullptr;
    // Publish the index sidecar first (to its own temp, then rename), then the
    // data file last: the data file's appearance at the final path is the commit
    // point, and by then its .idx is already in place.  Clear any stale .idx if
    // this run is too small to warrant one.
    if (write_index_ && !index_.empty()) {
      writeIndexSidecar();
      std::rename((path_ + ".idx.tmp").c_str(), (path_ + ".idx").c_str());
    } else {
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
  long body_start_offset_;          // file offset of the first record (post-header)
  struct IdxEnt { uint8_t key[64]; uint64_t offset; uint64_t recidx; };
  std::vector<IdxEnt> index_;
  static constexpr size_t kIndexStride = 64;

  // Sidecar <path>.idx: [u32 keyLen][u64 count][ {key[keyLen] u64 offset u64 recidx} ].
  // Native byte order — it's a machine-local seek aid, not part of the run's
  // byte-identical output, and map+merge of a column run on the same host.
  void writeIndexSidecar() {
    std::string ip = path_ + ".idx.tmp";
    FILE* f = std::fopen(ip.c_str(), "wb");
    if (!f) return;
    uint32_t magic = kRunIndexMagic;
    uint16_t ver   = kRunIndexVersion;
    uint8_t  bo    = kRunByteOrderLE;
    std::fwrite(&magic, sizeof(magic), 1, f);
    std::fwrite(&ver,   sizeof(ver),   1, f);
    std::fwrite(&bo,    sizeof(bo),    1, f);
    uint32_t kl = static_cast<uint32_t>(keyLen_);
    uint64_t cnt = index_.size();
    std::fwrite(&kl, sizeof(kl), 1, f);
    std::fwrite(&cnt, sizeof(cnt), 1, f);
    for (const auto& e : index_) {
      std::fwrite(e.key, 1, static_cast<size_t>(keyLen_), f);
      std::fwrite(&e.offset, sizeof(e.offset), 1, f);
      std::fwrite(&e.recidx, sizeof(e.recidx), 1, f);
    }
    std::fclose(f);
  }

  void writeHeader(int H, int maxn, const std::string& lo_hex,
                   const std::string& hi_hex, const std::string& rev) {
    std::fprintf(fp_, "POLYRUN 1\n");
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
        crc_(FNV_OFFSET), path_(path), seeked_(false), index_loaded_(false) {
    fp_ = std::fopen(path.c_str(), "rb");
    if (!fp_) {
      std::fprintf(stderr, "RunFileReader: cannot open %s\n", path.c_str());
      return;
    }
    if (!parseHeader()) {
      std::fprintf(stderr, "RunFileReader: bad header in %s\n", path.c_str());
      std::fclose(fp_);
      fp_ = nullptr;
      records_ = 0;
    }
  }

  ~RunFileReader() {
    if (fp_) std::fclose(fp_);
  }

  RunFileReader(const RunFileReader&) = delete;
  RunFileReader& operator=(const RunFileReader&) = delete;

  bool next(RunRecord<W>& out) {
    if (!fp_ || records_read_ >= records_) return false;
    out.sig = Sig{};
    if (std::fread(out.sig.b, 1, static_cast<size_t>(keyLen_), fp_)
        != static_cast<size_t>(keyLen_)) return false;
    crc_ = fnv1a64_update(crc_, out.sig.b, static_cast<size_t>(keyLen_));

    uint8_t lo = 0, len = 0;
    if (std::fread(&lo,  1, 1, fp_) != 1) return false;
    if (std::fread(&len, 1, 1, fp_) != 1) return false;
    crc_ = fnv1a64_update(crc_, &lo,  1);
    crc_ = fnv1a64_update(crc_, &len, 1);

    out.H      = H_;
    out.keyLen = keyLen_;
    out.lo     = lo;
    out.len    = len;
    out.counts.resize(len);
    for (int i = 0; i < len; ++i) {
      uint8_t bytes[sizeof(W)];
      if (std::fread(bytes, 1, sizeof(W), fp_) != sizeof(W)) return false;
      crc_ = fnv1a64_update(crc_, bytes, sizeof(W));
      W v{0};
      for (size_t b = 0; b < sizeof(W); ++b)
        v |= static_cast<W>(bytes[b]) << (8 * b);
      out.counts[i] = v;
    }
    ++records_read_;
    // Seeked readers cover only a slice, so the running CRC is partial — skip it
    // (corruption is caught by full reads / the verify gate).
    if (records_read_ == records_ && !seeked_) verifyCRC();
    return true;
  }

  // Seek so the next next() starts at the last indexed record with key <= klo
  // (the caller skips the small in-block overshoot below klo). Uses the sidecar
  // index; returns false / no-op if the index is absent (falls back to scan).
  // This is the merge read-amplification fix.
  bool seekToKey(const uint8_t* klo) {
    if (!fp_) return false;
    if (!index_loaded_) loadIndex();
    if (index_.empty()) return false;
    int a = 0, b = static_cast<int>(index_.size()) - 1, s = 0;
    while (a <= b) {
      int m = (a + b) / 2;
      if (std::memcmp(index_[m].key, klo, static_cast<size_t>(keyLen_)) <= 0) { s = m; a = m + 1; }
      else b = m - 1;
    }
    if (std::fseek(fp_, static_cast<long>(index_[s].offset), SEEK_SET) != 0) return false;
    records_read_ = index_[s].recidx;
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
  bool index_loaded_;
  struct IdxEnt { uint8_t key[64]; uint64_t offset; uint64_t recidx; };
  std::vector<IdxEnt> index_;

  void loadIndex() {
    index_loaded_ = true;
    std::string ip = path_ + ".idx";
    FILE* f = std::fopen(ip.c_str(), "rb");
    if (!f) return;
    // Validate the self-describing header; a stale / foreign / truncated sidecar
    // is ignored so the read falls back to a full scan rather than mis-seeking.
    uint32_t magic = 0; uint16_t ver = 0; uint8_t bo = 0;
    if (std::fread(&magic, sizeof(magic), 1, f) != 1 ||
        std::fread(&ver,   sizeof(ver),   1, f) != 1 ||
        std::fread(&bo,    sizeof(bo),    1, f) != 1 ||
        magic != kRunIndexMagic || ver != kRunIndexVersion || bo != kRunByteOrderLE) {
      std::fclose(f); return;
    }
    uint32_t kl = 0; uint64_t cnt = 0;
    if (std::fread(&kl, sizeof(kl), 1, f) != 1 || std::fread(&cnt, sizeof(cnt), 1, f) != 1 ||
        static_cast<int>(kl) != keyLen_) { std::fclose(f); return; }
    index_.resize(cnt);
    for (uint64_t i = 0; i < cnt; ++i) {
      std::memset(index_[i].key, 0, sizeof(index_[i].key));
      if (std::fread(index_[i].key, 1, kl, f) != kl ||
          std::fread(&index_[i].offset, sizeof(uint64_t), 1, f) != 1 ||
          std::fread(&index_[i].recidx, sizeof(uint64_t), 1, f) != 1) { index_.clear(); break; }
    }
    std::fclose(f);
  }

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
      if (std::strncmp(line, "POLYRUN ", 8) == 0)
        saw_polyrun = true;
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
    return saw_polyrun && byteorder_ok && counter_ok;
  }

  void verifyCRC() {
    if (!fp_) return;
    uint8_t stored[8];
    if (std::fread(stored, 1, 8, fp_) != 8) {
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

// keyLen defaults to 0 which means H+2 (triangle path); pass H+3 for holes.
template <class W>
std::pair<size_t, size_t> mergeRunFiles(
    const std::vector<std::string>& in_paths, int H,
    const std::string& lo_hex, const std::string& hi_hex,
    const std::string& out_path, const std::string& rev = "",
    int keyLen = 0) {
  if (keyLen == 0) keyLen = H + 2;
  uint8_t lo_sig[SIGMAX] = {};
  uint8_t hi_sig[SIGMAX] = {};
  bool has_lo = !lo_hex.empty() && hexToBytes(lo_hex, lo_sig, keyLen);
  bool has_hi = !hi_hex.empty() && hexToBytes(hi_hex, hi_sig, keyLen);

  std::vector<std::unique_ptr<RunFileReader<W>>> readers;
  readers.reserve(in_paths.size());
  for (const auto& p : in_paths)
    readers.push_back(std::make_unique<RunFileReader<W>>(p, H, keyLen));

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
      return std::memcmp(rec.sig.b, o.rec.sig.b,
                         static_cast<size_t>(rec.keyLen)) > 0;
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

  RunFileWriter<W> writer(out_path, H, 0, lo_hex, hi_hex, rev, keyLen);

  while (!heap.empty()) {
    Cursor top = heap.top();
    heap.pop();

    {
      Cursor nc;
      nc.idx = top.idx;
      if (readers[top.idx]->next(nc.rec))
        heap.push(std::move(nc));
    }

    if (has_lo &&
        std::memcmp(top.rec.sig.b, lo_sig, static_cast<size_t>(keyLen)) < 0)
      continue;
    if (has_hi &&
        std::memcmp(top.rec.sig.b, hi_sig, static_cast<size_t>(keyLen)) >= 0)
      break;

    while (!heap.empty()) {
      if (std::memcmp(top.rec.sig.b, heap.top().rec.sig.b,
                      static_cast<size_t>(keyLen)) != 0) break;
      Cursor eq = heap.top();
      heap.pop();
      top.rec.combine(eq.rec);
      Cursor nc;
      nc.idx = eq.idx;
      if (readers[eq.idx]->next(nc.rec))
        heap.push(std::move(nc));
    }

    writer.append(top.rec);
  }

  size_t body_bytes = writer.finalize();
  return {body_bytes, writer.records()};
}
