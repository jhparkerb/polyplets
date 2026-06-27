// run.h — sorted-run record format and I/O (DESIGN §9, data formats).
//
// A sorted run is a sequence of RunRecords in ascending memcmp(sig) order.
// Each record:
//   [ sig: (H+2) bytes | lo: u8 | len: u8 | counts[len]: len * W bytes LE ]
//   KEY = sig bytes (fixed per height-sweep, memcmp-sortable, endian-neutral)
//   VALUE = ranged count-vec: counts[lo .. lo+len) are the nonzero entries;
//           entries outside the window are implicitly 0.
//
// W = sizeof(CountWord): 8 for u64, 16 for u128.
// The window width is ~0.56*n (measured), so len typically << maxn+1.
//
// RunWriter: append records to a byte buffer (or file stream).
// RunReader: iterate records from a byte buffer in sorted key order.
// combine():  merge two same-key records by range-union + pointwise add.

#pragma once

#include <algorithm>
#include <cassert>
#include <cstdint>
#include <cstring>
#include <vector>

#include "core/signature.h"

// Supported counter widths.
using u64  = std::uint64_t;
using u128 = unsigned __int128;

// A single sorted-run record, held in host memory.
// Templated on the word width W (u64 or u128).
template <class W>
struct RunRecord {
  Sig    sig;          // canonical signature (keyLen bytes used, rest zero)
  int    H;            // height (needed to interpret sig and lo/len)
  int    keyLen;       // key length in bytes: H+2 for triangle, H+3 for holes
  uint8_t lo;         // first nonzero index in counts[]
  uint8_t len;        // number of nonzero entries
  std::vector<W> counts; // counts[lo .. lo+len), dense over the window

  // True if both records share the same key (same sig bytes for keyLen).
  bool sameKey(const RunRecord& o) const {
    return std::memcmp(sig.b, o.sig.b, static_cast<size_t>(keyLen)) == 0;
  }

  // Merge o INTO this record (range-union + componentwise add).
  // Both must share the same key. The associative reduce op.
  // TODO(perf, M1+): combine runs once per duplicate-key collision per column;
  // when the union only extends the existing high end (new_lo == lo) the merged
  // buffer can be grown in place instead of allocated fresh. Deferred until the
  // at-scale spill engine lands and the allocation actually shows up in a profile.
  void combine(const RunRecord& o) {
    assert(sameKey(o) && H == o.H && keyLen == o.keyLen);
    if (o.len == 0) return;
    if (len == 0) { lo = o.lo; len = o.len; counts = o.counts; return; }
    // Compute the union window in int; the byte-wide lo/len fields can only
    // hold n<=255, which the caller guarantees (n<=25 for u64 counters).
    const int new_lo  = std::min<int>(lo, o.lo);
    const int new_end = std::max<int>(lo + len, o.lo + o.len);
    const int new_len = new_end - new_lo;
    assert(new_end <= 256 && "count-vec window exceeded byte range");
    std::vector<W> merged(new_len, W{0});
    for (int i = 0; i < len; ++i)
      merged[(lo + i) - new_lo] += counts[i];
    for (int i = 0; i < o.len; ++i)
      merged[(o.lo + i) - new_lo] += o.counts[i];
    lo = static_cast<uint8_t>(new_lo);
    len = static_cast<uint8_t>(new_len);
    counts = std::move(merged);
  }

  // Return the minimum n index with a nonzero count (-1 if empty).
  int minSize() const {
    for (int i = 0; i < len; ++i)
      if (counts[i] != W{0}) return static_cast<int>(lo) + i;
    return -1;
  }
};

// ─── Serialization ────────────────────────────────────────────────────────────

// Append one record to a byte buffer in the binary run format.
template <class W>
inline void serializeRecord(const RunRecord<W>& r, std::vector<uint8_t>& buf) {
  const int keyLen = r.keyLen;
  buf.insert(buf.end(), r.sig.b, r.sig.b + keyLen);
  buf.push_back(r.lo);
  buf.push_back(r.len);
  // counts LE, W bytes each
  for (int i = 0; i < r.len; ++i) {
    W v = r.counts[i];
    for (size_t b = 0; b < sizeof(W); ++b) {
      buf.push_back(static_cast<uint8_t>(v & 0xff));
      v >>= 8;
    }
  }
}

// Deserialize one record from raw bytes at *pos; advance *pos past it.
// Returns false if there are insufficient bytes (end-of-run).
// keyLen defaults to 0 which means H+2 (triangle path).
template <class W>
inline bool deserializeRecord(const uint8_t* data, size_t size, size_t* pos,
                              int H, RunRecord<W>& out, int keyLen = 0) {
  if (keyLen == 0) keyLen = H + 2;
  const size_t minBytes = static_cast<size_t>(keyLen) + 2; // sig + lo + len
  if (*pos + minBytes > size) return false;

  std::memcpy(out.sig.b, data + *pos, static_cast<size_t>(keyLen));
  // zero-pad the unused SIGMAX tail (invariant: unused bytes always 0)
  std::memset(out.sig.b + keyLen, 0, SIGMAX - keyLen);
  *pos += keyLen;
  out.H      = H;
  out.keyLen = keyLen;
  out.lo  = data[(*pos)++];
  out.len = data[(*pos)++];

  const size_t valBytes = static_cast<size_t>(out.len) * sizeof(W);
  if (*pos + valBytes > size) return false;
  out.counts.resize(out.len);
  for (int i = 0; i < out.len; ++i) {
    W v{0};
    for (size_t b = 0; b < sizeof(W); ++b)
      v |= static_cast<W>(data[(*pos)++]) << (8 * b);
    out.counts[i] = v;
  }
  return true;
}

// ─── Sort-key comparison (memcmp on the sig bytes for keyLen) ─────────────────

template <class W>
inline bool recordLess(const RunRecord<W>& a, const RunRecord<W>& b) {
  return std::memcmp(a.sig.b, b.sig.b, static_cast<size_t>(a.keyLen)) < 0;
}

// The seed state of a height-sweep: the empty boundary (all-zero sig) with one
// partial animal of zero cells (counts[0]=1). Column 0 of every height H.
// keyLen defaults to 0 which means H+2 (triangle path); pass H+3 for holes.
template <class W>
inline RunRecord<W> seedRecord(int H, int keyLen = 0) {
  RunRecord<W> seed;
  std::memset(seed.sig.b, 0, SIGMAX);
  seed.H      = H;
  seed.keyLen = (keyLen == 0) ? H + 2 : keyLen;
  seed.lo     = 0;
  seed.len    = 1;
  seed.counts = {W{1}};
  return seed;
}

// ─── In-memory run: a sorted vector of RunRecords ────────────────────────────

template <class W>
using Run = std::vector<RunRecord<W>>;

// Sort a Run in place by sig key.
template <class W>
inline void sortRun(Run<W>& run) {
  std::sort(run.begin(), run.end(), recordLess<W>);
}

// Merge equal-key adjacent records produced by sortRun (combine in place).
// After this the run has one record per distinct sig.
template <class W>
inline void deduplicateRun(Run<W>& run) {
  if (run.empty()) return;
  size_t dst = 0;
  for (size_t src = 1; src < run.size(); ++src) {
    if (run[dst].sameKey(run[src])) {
      run[dst].combine(run[src]);
    } else {
      ++dst;
      if (dst != src) run[dst] = std::move(run[src]); // skip self-move
    }
  }
  run.resize(dst + 1);
}

// Serialize an entire in-memory Run to bytes.
template <class W>
inline std::vector<uint8_t> serializeRun(const Run<W>& run) {
  std::vector<uint8_t> buf;
  for (const auto& r : run) serializeRecord(r, buf);
  return buf;
}

// Deserialize an entire Run from bytes.
// keyLen defaults to 0 which means H+2 (triangle path).
template <class W>
inline Run<W> deserializeRun(const uint8_t* data, size_t size, int H,
                              int keyLen = 0) {
  Run<W> run;
  size_t pos = 0;
  RunRecord<W> rec;
  while (deserializeRecord(data, size, &pos, H, rec, keyLen))
    run.push_back(rec);
  return run;
}
