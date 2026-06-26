// T0.3 gate: run.h round-trip, sort-key ordering, combine correctness.

#include <cassert>
#include <cstring>
#include <cstdio>
#include "core/run.h"

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
    r.H = H; r.lo = 2; r.len = 3;
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
    r.H = H; r.lo = 1; r.len = 1; r.counts = {1};
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
  makeSig(a.sig, H, {1, 0}); a.H = H; a.lo = 3; a.len = 2; a.counts = {10, 20};
  makeSig(b.sig, H, {1, 0}); b.H = H; b.lo = 4; b.len = 2; b.counts = {30, 40};
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
    makeSig(r.sig, H, {1, 0}); r.H = H;
    r.lo = static_cast<uint8_t>(lo); r.len = 2;
    r.counts = {10, 20};
    run.push_back(r);
  }
  // One record with different sig
  RunRecord<u64> r2;
  makeSig(r2.sig, H, {2, 0}); r2.H = H; r2.lo = 2; r2.len = 1; r2.counts = {99};
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

int main() {
  testRoundTrip();
  testSortOrder();
  testCombine();
  testDeduplicate();
  std::puts("gate_run PASS");
}
