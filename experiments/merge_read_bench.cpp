// merge_read_bench.cpp — isolate the merge's range-filter read pattern.
//
// The merge (core/runfile.h mergeRunFiles) extracts each merge worker's key
// range [klo,khi) by reading from the START of every input and *skipping*
// records below klo (the `if (key < lo) continue;`). Every one of the M workers
// does that independently, so the aggregate scan is ~M*total/2 records. This
// benchmark measures that amplification against the fix — seek to klo via a
// sparse (key->offset) index and read only the range.
//
// One sorted variable-length-record buffer stands in for the map output; we
// extract all M ranges (which partition the keyspace) two ways and compare
// records-scanned and wall. Warm (in-memory) regime = the current a(21) merge
// regime (data in page cache); on disk the amplification also multiplies I/O.
//
// Usage: merge_read_bench [N_RECORDS] [M_RANGES] [KEYLEN] [MAXVLEN] [INDEX_STRIDE]
#include <algorithm>
#include <chrono>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <random>
#include <vector>

using u64 = uint64_t;
using clk = std::chrono::steady_clock;
static double secs(clk::time_point a) {
  return std::chrono::duration<double>(clk::now() - a).count();
}

int main(int argc, char** argv) {
  size_t N   = argc > 1 ? strtoull(argv[1], nullptr, 10) : 5'000'000; // records
  int M       = argc > 2 ? atoi(argv[2]) : 320;   // merge ranges = cores*mult
  int KEYLEN  = argc > 3 ? atoi(argv[3]) : 20;     // ~ H+2
  int MAXVLEN = argc > 4 ? atoi(argv[4]) : 20;     // count-vector length
  int STRIDE  = argc > 5 ? atoi(argv[5]) : 1024;   // index one key every STRIDE recs

  auto encode = [&](u64 k, uint8_t* out) {         // big-endian -> memcmp-sortable
    for (int b = 0; b < KEYLEN; b++) out[b] = b < 8 ? (k >> (8 * (7 - b))) & 0xFF : 0;
  };

  // --- build one sorted buffer: key[KEYLEN] vlen(1) payload[vlen*8] ---
  std::mt19937_64 rng(12345);
  std::vector<u64> keys(N);
  for (auto& k : keys) k = rng();
  std::sort(keys.begin(), keys.end());

  std::vector<uint8_t> buf;
  buf.reserve(N * (KEYLEN + 2 + 8 * (MAXVLEN / 2)));
  for (size_t i = 0; i < N; i++) {
    uint8_t key[64]; encode(keys[i], key);
    buf.insert(buf.end(), key, key + KEYLEN);
    uint8_t vlen = 1 + (rng() % MAXVLEN);
    buf.push_back(vlen);
    buf.resize(buf.size() + (size_t)vlen * 8);      // payload (zeroed, never read)
  }
  const size_t total = buf.size();
  const uint8_t* B = buf.data();
  auto rec_size = [&](size_t off) { return KEYLEN + 1 + (size_t)B[off + KEYLEN] * 8; };

  // --- M ranges partitioning the u64 keyspace ---
  std::vector<u64> cut(M + 1);
  for (int j = 0; j <= M; j++)
    cut[j] = j == M ? UINT64_MAX : (u64)((__uint128_t)j * UINT64_MAX / M);

  // === Option A: read-and-skip from the start, per range ===
  size_t scanA = 0, keptA = 0;
  auto tA = clk::now();
  for (int j = 0; j < M; j++) {
    uint8_t lo[64], hi[64]; encode(cut[j], lo); encode(cut[j + 1], hi);
    for (size_t off = 0; off < total; off += rec_size(off)) {
      scanA++;
      if (memcmp(B + off, lo, KEYLEN) < 0) continue;     // skip prefix below klo
      if (memcmp(B + off, hi, KEYLEN) >= 0) break;        // stop at khi
      keptA++;
    }
  }
  double timeA = secs(tA);

  // --- sparse index: (key, offset) every STRIDE records (one pass) ---
  struct Idx { uint8_t key[64]; size_t off; };
  std::vector<Idx> index;
  { size_t off = 0, i = 0;
    while (off < total) { if (i % STRIDE == 0) { Idx e; memcpy(e.key, B + off, KEYLEN); e.off = off; index.push_back(e); } off += rec_size(off); i++; } }

  // === Option B: binary-search the index to klo, then read only the range ===
  size_t scanB = 0, keptB = 0;
  auto tB = clk::now();
  for (int j = 0; j < M; j++) {
    uint8_t lo[64], hi[64]; encode(cut[j], lo); encode(cut[j + 1], hi);
    int a = 0, b = (int)index.size() - 1, start = 0;       // last index entry <= lo
    while (a <= b) { int m = (a + b) / 2; if (memcmp(index[m].key, lo, KEYLEN) <= 0) { start = m; a = m + 1; } else b = m - 1; }
    for (size_t off = index[start].off; off < total; off += rec_size(off)) {
      scanB++;
      if (memcmp(B + off, lo, KEYLEN) < 0) continue;       // tiny in-block skip
      if (memcmp(B + off, hi, KEYLEN) >= 0) break;
      keptB++;
    }
  }
  double timeB = secs(tB);

  printf("records=%zu ranges=%d keyLen=%d total=%.0fMB index_entries=%zu\n",
         N, M, KEYLEN, total / 1e6, index.size());
  printf("A read+skip : scanned=%zu (%.1fx records)  time=%.3fs  kept=%zu\n",
         scanA, (double)scanA / N, timeA, keptA);
  printf("B seek-index: scanned=%zu (%.2fx records)  time=%.3fs  kept=%zu\n",
         scanB, (double)scanB / N, timeB, keptB);
  printf("=> B scans %.0fx fewer records, %.1fx faster  (kept match: %s)\n",
         (double)scanA / scanB, timeA / timeB, keptA == keptB ? "yes" : "NO");
  return 0;
}
