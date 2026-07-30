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
#include <memory_resource>
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
  // H, keyLen: bounded <=SIGMAX-2 (<=38 even at the keyLen=H+4 kink-stage
  // width), so uint8_t is exact, not lossy -- was `int`, wasting 6 bytes/record
  // (measured: sizeof(RunRecord)=72->64) purely on alignment padding a value
  // that never exceeds 38. See results/hotpath-optim.md.
  uint8_t H;            // height (needed to interpret sig and lo/len)
  uint8_t keyLen;       // key length in bytes: H+2 for triangle, H+3 for holes
  uint8_t lo;         // first nonzero index in counts[]
  uint8_t len;        // number of nonzero entries
  // pmr::vector, not std::vector: lets the map hot loop (mapreduce.h,
  // kink.h) construct successor records against a monotonic_buffer_resource
  // arena scoped to one spill epoch, instead of one malloc/free per
  // successor (measured: 415.8M allocations in a34's swept portion,
  // ~14% of map cycles, map-profile.md B2). Default-constructed (no
  // allocator argument) it behaves EXACTLY like std::vector -- uses the
  // global default_resource, same semantics, same cost, zero change for
  // every other call site (deserializeRecord, seedRecord, tests, ...).
  // Only map_shard_file/map_shard_stage_file opt into the arena, via the
  // allocator-aware constructor below.
  std::pmr::vector<W> counts; // counts[lo .. lo+len), dense over the window

  RunRecord() = default;
  explicit RunRecord(std::pmr::memory_resource* mr) : counts(mr) {}

  // True if both records share the same key (same sig bytes for keyLen).
  bool sameKey(const RunRecord& o) const {
    return sigCmp(sig.b, o.sig.b, keyLen) == 0;
  }

  // Merge o INTO this record (range-union + componentwise add).
  // Both must share the same key. The associative reduce op.
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

    // Grow-in-place when this record already starts at or before o (new_lo == lo):
    // no left-shift is needed, so we extend our OWN counts buffer at the high end
    // (a no-op when o is fully within our window) and add o in. This avoids the
    // fresh allocate-copy-free that dominated merge CPU (combine was ~58% of merge
    // wall and alloc-bound — results/merge-ledger.md A5 / the run.h:51 lever). When
    // the same record accumulates many collisions (the k-way merge / dedup pattern)
    // the buffer grows once and every subsequent in-window combine is zero-alloc.
    // Silent Carry: guard each add against unsigned wrap; slot < prev means a u64
    // count exceeded 2^64 and the --counter is too narrow — fail loud.
    if (new_lo == lo) {
      if (new_len > len) counts.resize(new_len, W{0});  // append zeros; lower entries keep index
      const int off = static_cast<int>(o.lo) - lo;
      for (int i = 0; i < o.len; ++i) {
        W& slot = counts[off + i];
        W prev = slot;
        slot += o.counts[i];
        assert(slot >= prev && "count overflow in combine (need wider --counter)");
      }
      len = static_cast<uint8_t>(new_len);
      return;
    }

    // Left-extension (o starts before this): the existing entries would shift, so
    // build the union buffer fresh. Rarer than the in-place case above.
    // Same allocator as `counts` (arena-aware if this record is): keeps the
    // rare left-extension path in the same epoch's pool instead of falling
    // back to the global allocator underneath a pmr-typed field.
    std::pmr::vector<W> merged(new_len, W{0}, counts.get_allocator());
    for (int i = 0; i < len; ++i) {
      W& slot = merged[(lo + i) - new_lo];
      W prev = slot;
      slot += counts[i];
      assert(slot >= prev && "count overflow in combine (need wider --counter)");
    }
    for (int i = 0; i < o.len; ++i) {
      W& slot = merged[(o.lo + i) - new_lo];
      W prev = slot;
      slot += o.counts[i];
      assert(slot >= prev && "count overflow in combine (need wider --counter)");
    }
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

// Successor-counts arena sizing (map-profile.md B2): the map hot loop
// (mapreduce.h's map_shard_file, kink.h's map_shard_stage_file) bump-allocates
// RunRecord::counts from a std::pmr::monotonic_buffer_resource sized to the
// spill/ram budget, one arena per spill epoch instead of one malloc/free per
// successor. Both call sites compute the same fallback-when-unbounded chunk
// size; shared here so the fallback constant has one home.
inline size_t succArenaHint(size_t ram_budget_bytes) {
  return ram_budget_bytes > 0 ? ram_budget_bytes : (size_t{64} << 20);
}

// ─── Serialization ────────────────────────────────────────────────────────────

// ─── LEB128 varint counts ─────────────────────────────────────────────────────
// Counts are the dominant run-file byte cost (~92% of body) and are heavily
// over-provisioned against the fixed W width: even at frontier scale the largest
// count fits ~9 bytes vs u128's 16, so LEB128 varint cuts run-file write volume
// ~70% (measured; decays only mildly with n) — the direct lever on the
// disk-bound bottleneck. Self-delimiting, so records stay variable-length just
// like the ranged `len` already makes them; the `.idx` offsets are recorded
// from actual body bytes (body_bytes_), so range-seeking is unaffected. Encode
// writes 1 byte for count 0. Decode is bounds-checked against the body extent.
template <class W, class PushByte>
inline void encodeVarint(W v, PushByte push) {
  while (v >= 0x80) { push(static_cast<uint8_t>((v & 0x7f) | 0x80)); v >>= 7; }
  push(static_cast<uint8_t>(v & 0x7f));
}

template <class W>
inline bool decodeVarint(const uint8_t* data, size_t size, size_t* pos, W* out) {
  W result = 0; unsigned shift = 0; uint8_t byte;
  do {
    if (*pos >= size) return false;
    // WIDTH-BOUNDED (V3): a valid varint for W needs at most
    // ceil(8*sizeof(W)/7) bytes, so shift can never legitimately reach the
    // counter width. Without this bound a corrupt run of continuation bytes
    // shifts past it -- undefined behavior, and on hardware that merely masks
    // the shift count, a plausible WRONG count instead of a rejected record.
    // Treated as a failed decode, which every caller already handles
    // (end-of-run for deserializeRecord; a fail-closed abort in
    // RunFileReader::next, E1).
    if (shift >= 8 * sizeof(W)) return false;
    byte = data[(*pos)++];
    result |= (static_cast<W>(byte & 0x7f) << shift);
    shift += 7;
  } while (byte & 0x80);
  *out = result;
  return true;
}

// Append one record to a byte buffer in the binary run format.
template <class W>
inline void serializeRecord(const RunRecord<W>& r, std::vector<uint8_t>& buf) {
  const int keyLen = r.keyLen;
  buf.insert(buf.end(), r.sig.b, r.sig.b + keyLen);
  buf.push_back(r.lo);
  buf.push_back(r.len);
  // counts: LEB128 varint each (see encodeVarint)
  for (int i = 0; i < r.len; ++i)
    encodeVarint<W>(r.counts[i], [&](uint8_t b) { buf.push_back(b); });
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

  // counts: LEB128 varint each; decodeVarint is bounds-checked, so a truncated
  // record (insufficient bytes) reports end-of-run just like the old fixed path.
  out.counts.resize(out.len);
  for (int i = 0; i < out.len; ++i)
    if (!decodeVarint<W>(data, size, pos, &out.counts[i])) return false;
  return true;
}

// ─── Sort-key comparison (memcmp on the sig bytes for keyLen) ─────────────────

template <class W>
inline bool recordLess(const RunRecord<W>& a, const RunRecord<W>& b) {
  const int c = sigCmp(a.sig.b, b.sig.b, a.keyLen);
  if (c != 0) return c < 0;
  // Tiebreak by lo: std::sort isn't stable, so without this, same-key
  // collision groups land in arbitrary lo order after sortRun.
  // deduplicateRun's combine() has a cheap grow-in-place path (new_lo==lo)
  // and an expensive left-extension path (fresh alloc + full copy,
  // triggered whenever an incoming record's lo is BEFORE the accumulator's
  // current lo). With lo ascending within a key group, the accumulator's lo
  // is always the group minimum, so every combine sees o.lo >= lo and the
  // expensive path can never fire for this call site. Confirmed the
  // mechanism first with a real benchmark (experiments/bench_dedup.cpp) --
  // collision rate x window width was shown to compound combine() cost;
  // this is the fix for why, not a guess (docs/utilization-bottleneck-log.md
  // Bottleneck #6). mergeRunFiles' cross-file k-way merge doesn't get the
  // full benefit (per-file order still depends on which file a record came
  // from) but each file's OWN prior sortRun already carries this tiebreak,
  // so it's a pure win with no downside there either.
  return a.lo < b.lo;
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
