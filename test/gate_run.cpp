// T0.3 gate: run.h round-trip, sort-key ordering, combine correctness.

#include <cassert>
#include <cstring>
#include <cstdio>
#include <cstdlib>
#include "core/run.h"

// Heap-allocation counter (global new/delete) for the combine alloc-churn gate.
// combine() on the dominant merge path must NOT allocate when the incoming
// record's window is already contained in this record's window — see
// docs/engine-record.md A5 (combine was 58% of merge wall, alloc-bound).
static size_t g_allocs = 0;
void* operator new(std::size_t n) { ++g_allocs; void* p = std::malloc(n); if (!p) std::abort(); return p; }
void* operator new[](std::size_t n) { ++g_allocs; void* p = std::malloc(n); if (!p) std::abort(); return p; }
void operator delete(void* p) noexcept { std::free(p); }
void operator delete(void* p, std::size_t) noexcept { std::free(p); }
void operator delete[](void* p) noexcept { std::free(p); }
void operator delete[](void* p, std::size_t) noexcept { std::free(p); }

static void makeSig(Sig& s, int H, std::initializer_list<int> labels,
                    int touchTop=0, int touchBot=0) {
  std::memset(s.b, 0, SIGMAX);
  int i = 0;
  for (int v : labels) s.b[i++] = static_cast<uint8_t>(v);
  s.b[H]   = static_cast<uint8_t>(touchTop);
  s.b[H+1] = static_cast<uint8_t>(touchBot);
}

static void testRoundTrip() {
  const int H = 4;
  Run<u64> run;
  for (int label = 1; label <= 3; ++label) {
    RunRecord<u64> r;
    makeSig(r.sig, H, {0, (int)label, 0, 0}, 0, 0);
    r.H = H; r.keyLen = H + 2; r.lo = 2; r.len = 3;
    r.counts = {100u + label, 200u + label, 300u + label};
    run.push_back(r);
  }
  auto bytes = serializeRun(run);
  auto run2  = deserializeRun<u64>(bytes.data(), bytes.size(), H);
  assert(run2.size() == run.size());
  for (size_t i = 0; i < run.size(); ++i) {
    assert(run2[i].sameKey(run[i]));
    assert(run2[i].lo  == run[i].lo);
    assert(run2[i].len == run[i].len);
    assert(run2[i].counts == run[i].counts);
  }
}

static void testSortOrder() {
  // records with different sigs must sort by memcmp on the sig bytes
  const int H = 3;
  Run<u64> run;
  for (int v : {3, 1, 2}) {
    RunRecord<u64> r;
    makeSig(r.sig, H, {0, v, 0});
    r.H = H; r.keyLen = H + 2; r.lo = 1; r.len = 1; r.counts = {1};
    run.push_back(r);
  }
  sortRun(run);
  assert(run[0].sig.b[1] == 1);
  assert(run[1].sig.b[1] == 2);
  assert(run[2].sig.b[1] == 3);
}

static void testCombine() {
  const int H = 2;
  RunRecord<u64> a, b;
  makeSig(a.sig, H, {1, 0}); a.H = H; a.keyLen = H + 2; a.lo = 3; a.len = 2; a.counts = {10, 20};
  makeSig(b.sig, H, {1, 0}); b.H = H; b.keyLen = H + 2; b.lo = 4; b.len = 2; b.counts = {30, 40};
  // windows [3,5) and [4,6) -> union [3,6), len=3
  a.combine(b);
  assert(a.lo == 3 && a.len == 3);
  assert(a.counts[0] == 10);   // index 3: only from a
  assert(a.counts[1] == 50);   // index 4: 20+30
  assert(a.counts[2] == 40);   // index 5: only from b
}

static void testDeduplicate() {
  const int H = 2;
  Run<u64> run;
  // Two records with same sig, different ranges
  for (int lo : {1, 3}) {
    RunRecord<u64> r;
    makeSig(r.sig, H, {1, 0}); r.H = H; r.keyLen = H + 2;
    r.lo = static_cast<uint8_t>(lo); r.len = 2;
    r.counts = {10, 20};
    run.push_back(r);
  }
  // One record with different sig
  RunRecord<u64> r2;
  makeSig(r2.sig, H, {2, 0}); r2.H = H; r2.keyLen = H + 2; r2.lo = 2; r2.len = 1; r2.counts = {99};
  run.push_back(r2);
  sortRun(run);
  deduplicateRun(run);
  assert(run.size() == 2);
  // first record is sig {1,0}: combined [1,5), counts 10,20,10,20
  assert(run[0].lo == 1 && run[0].len == 4);
  assert(run[0].counts[0] == 10);
  assert(run[0].counts[2] == 10);
  // second record is sig {2,0}
  assert(run[1].sig.b[0] == 2);
}

// Repeatedly combining an in-window record must do ZERO heap allocations: the
// grow-in-place path reuses this record's own counts buffer. Pre-fix combine
// allocated a fresh union vector on every call (the merge-CPU lever, A5), so
// this fails red with g_allocs == K.
static void testCombineNoAlloc() {
  const int H = 2;
  RunRecord<u64> a;
  makeSig(a.sig, H, {1, 0}); a.H = H; a.keyLen = H + 2; a.lo = 2; a.len = 10;
  a.counts.assign(10, 0u);                     // window [2,12)
  RunRecord<u64> b;
  makeSig(b.sig, H, {1, 0}); b.H = H; b.keyLen = H + 2; b.lo = 4; b.len = 4;
  b.counts = {1u, 1u, 1u, 1u};                 // window [4,8) ⊂ [2,12)

  const int K = 1000;
  g_allocs = 0;                                // measure only the combine loop
  for (int i = 0; i < K; ++i) a.combine(b);
  if (g_allocs != 0) {
    std::printf("gate_run FAIL: combine allocated %zu times over %d in-window "
                "combines (want 0)\n", g_allocs, K);
    std::abort();
  }
  // Correctness: window unchanged; indices 4..7 (counts[2..5]) each got +K.
  assert(a.lo == 2 && a.len == 10);
  assert(a.counts[2] == (u64)K && a.counts[3] == (u64)K &&
         a.counts[4] == (u64)K && a.counts[5] == (u64)K);
  assert(a.counts[0] == 0 && a.counts[1] == 0 && a.counts[6] == 0);
}

// V3 (AUDIT-2026-07-30): decodeVarint's `shift += 7` had NO width bound, so a
// corrupt stream of continuation bytes kept shifting past the counter width —
// undefined behavior at shift >= 8*sizeof(W), and (on the hardware where the
// shift is merely masked) a plausible wrong count rather than a rejected
// record. A varint can never legitimately need more than ceil(8*sizeof(W)/7)
// bytes, so anything longer is corruption and must be reported as a failed
// decode, which is what every caller already handles (end-of-run for
// deserializeRecord; a fail-closed abort in RunFileReader::next, E1).
static void testVarintWidthBound() {
  // 20 continuation bytes then a terminator: legal-looking, but 20 * 7 = 140
  // bits, far past u64 and past u128.
  uint8_t buf[21];
  for (int i = 0; i < 20; ++i) buf[i] = 0x80;
  buf[20] = 0x01;

  size_t pos = 0;
  u64 v64 = 0;
  assert(!decodeVarint<u64>(buf, sizeof(buf), &pos, &v64) &&
         "V3: an over-wide varint must fail to decode, not shift past u64");

  pos = 0;
  u128 v128 = 0;
  assert(!decodeVarint<u128>(buf, sizeof(buf), &pos, &v128) &&
         "V3: an over-wide varint must fail to decode, not shift past u128");

  // The widest LEGITIMATE encodings still decode: 10 bytes for u64 (shifts
  // 0..63), 19 for u128 (shifts 0..126).
  uint8_t ok64[10];
  for (int i = 0; i < 9; ++i) ok64[i] = 0x80;
  ok64[9] = 0x01;                       // bit 63 set
  pos = 0; v64 = 0;
  assert(decodeVarint<u64>(ok64, sizeof(ok64), &pos, &v64) &&
         "V3: the widest legal u64 varint must still decode");
  assert(v64 == (u64{1} << 63));

  uint8_t ok128[19];
  for (int i = 0; i < 18; ++i) ok128[i] = 0x80;
  ok128[18] = 0x01;                     // bit 126 set
  pos = 0; v128 = 0;
  assert(decodeVarint<u128>(ok128, sizeof(ok128), &pos, &v128) &&
         "V3: the widest legal u128 varint must still decode");
  assert(v128 == (u128{1} << 126));
}

int main() {
  testRoundTrip();
  testSortOrder();
  testCombine();
  testDeduplicate();
  testCombineNoAlloc();
  testVarintWidthBound();
  std::puts("gate_run PASS");
}
