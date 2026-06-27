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
#include <cstring>
#include <memory>
#include <queue>
#include <string>
#include <vector>

#include "core/run.h"

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

template <class W>
class RunFileWriter {
 public:
  // Real writer: opens file, writes header with placeholder record count.
  RunFileWriter(const std::string& path, int H, int maxn,
                const std::string& lo_hex, const std::string& hi_hex,
                const std::string& rev = "")
      : H_(H), fp_(nullptr), record_count_(0), body_bytes_(0),
        crc_(FNV_OFFSET), records_offset_(0) {
    fp_ = std::fopen(path.c_str(), "wb");
    if (!fp_) {
      std::fprintf(stderr, "RunFileWriter: cannot open %s\n", path.c_str());
      return;
    }
    writeHeader(H, maxn, lo_hex, hi_hex, rev);
  }

  // Default constructor: no-op.
  RunFileWriter()
      : H_(0), fp_(nullptr), record_count_(0), body_bytes_(0),
        crc_(FNV_OFFSET), records_offset_(0) {}

  ~RunFileWriter() {
    if (fp_) std::fclose(fp_);
  }

  RunFileWriter(const RunFileWriter&) = delete;
  RunFileWriter& operator=(const RunFileWriter&) = delete;

  void append(const RunRecord<W>& r) {
    if (!fp_) return;
    const int keyLen = H_ + 2;
    std::fwrite(r.sig.b, 1, static_cast<size_t>(keyLen), fp_);
    uint8_t lo  = r.lo;
    uint8_t len = r.len;
    std::fwrite(&lo,  1, 1, fp_);
    std::fwrite(&len, 1, 1, fp_);
    crc_ = fnv1a64_update(crc_, r.sig.b, static_cast<size_t>(keyLen));
    crc_ = fnv1a64_update(crc_, &lo,  1);
    crc_ = fnv1a64_update(crc_, &len, 1);
    body_bytes_ += static_cast<size_t>(keyLen) + 2;
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
    return body_bytes_;
  }

  bool ok() const { return fp_ != nullptr; }

 private:
  int H_;
  FILE* fp_;
  size_t record_count_;
  size_t body_bytes_;
  uint64_t crc_;
  long records_offset_;

  void writeHeader(int H, int maxn, const std::string& lo_hex,
                   const std::string& hi_hex, const std::string& rev) {
    std::fprintf(fp_, "POLYRUN 1\n");
    std::fprintf(fp_, "height %d\n", H);
    std::fprintf(fp_, "maxn %d\n", maxn);
    std::fprintf(fp_, "counter u64\n");
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
  }
};

// ─── RunFileReader ────────────────────────────────────────────────────────────

template <class W>
class RunFileReader {
 public:
  RunFileReader(const std::string& path, int H)
      : H_(H), fp_(nullptr), records_(0), records_read_(0),
        crc_(FNV_OFFSET) {
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
    const int keyLen = H_ + 2;
    out.sig = Sig{};
    if (std::fread(out.sig.b, 1, static_cast<size_t>(keyLen), fp_)
        != static_cast<size_t>(keyLen)) return false;
    crc_ = fnv1a64_update(crc_, out.sig.b, static_cast<size_t>(keyLen));

    uint8_t lo = 0, len = 0;
    if (std::fread(&lo,  1, 1, fp_) != 1) return false;
    if (std::fread(&len, 1, 1, fp_) != 1) return false;
    crc_ = fnv1a64_update(crc_, &lo,  1);
    crc_ = fnv1a64_update(crc_, &len, 1);

    out.H   = H_;
    out.lo  = lo;
    out.len = len;
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
    if (records_read_ == records_) verifyCRC();
    return true;
  }

  size_t records() const { return records_; }
  int    H()       const { return H_; }

 private:
  int H_;
  FILE* fp_;
  size_t records_;
  size_t records_read_;
  uint64_t crc_;

  bool parseHeader() {
    char line[512];
    bool saw_polyrun = false;
    while (std::fgets(line, sizeof(line), fp_)) {
      size_t ln = std::strlen(line);
      while (ln > 0 && (line[ln-1] == '\n' || line[ln-1] == '\r'))
        line[--ln] = '\0';
      if (ln == 0) break;  // blank line = end of header
      if (std::strncmp(line, "POLYRUN ", 8) == 0)
        saw_polyrun = true;
      else if (std::strncmp(line, "records ", 8) == 0)
        records_ = static_cast<size_t>(std::strtoull(line + 8, nullptr, 10));
      // height, maxn, counter, classifier, keylo, keyhi, rev, byteorder: ignored
    }
    return saw_polyrun;
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
// Returns total body bytes written to out_path.

template <class W>
size_t mergeRunFiles(const std::vector<std::string>& in_paths, int H,
                     const std::string& lo_hex, const std::string& hi_hex,
                     const std::string& out_path, const std::string& rev = "") {
  const int keyLen = H + 2;
  uint8_t lo_sig[SIGMAX] = {};
  uint8_t hi_sig[SIGMAX] = {};
  bool has_lo = !lo_hex.empty() && hexToBytes(lo_hex, lo_sig, keyLen);
  bool has_hi = !hi_hex.empty() && hexToBytes(hi_hex, hi_sig, keyLen);

  std::vector<std::unique_ptr<RunFileReader<W>>> readers;
  readers.reserve(in_paths.size());
  for (const auto& p : in_paths)
    readers.push_back(std::make_unique<RunFileReader<W>>(p, H));

  struct Cursor {
    RunRecord<W> rec;
    int idx;
    bool operator>(const Cursor& o) const {
      return std::memcmp(rec.sig.b, o.rec.sig.b,
                         static_cast<size_t>(rec.H + 2)) > 0;
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

  RunFileWriter<W> writer(out_path, H, 0, lo_hex, hi_hex, rev);

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

  return writer.finalize();
}
