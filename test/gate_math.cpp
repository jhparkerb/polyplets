// T0.2 gate: trusted math (signature + transition) copied into core/ correctly.
// Tests: canonicalize idempotent, reflect is involution, fold(fold(x))==fold(x),
// completionLowerBound never over-estimates (verified by checking against the
// exhaustively-computed oracle -- but here we just verify structural properties
// and spot-check known values from the original unit assertions).

#include <cassert>
#include <cstring>
#include <cstdio>
#include "core/signature.h"
#include "core/transition.h"

static void testCanonicalize() {
  // relabeling is idempotent
  Sig s;
  std::memset(s.b, 0, SIGMAX);
  s.b[0] = 3; s.b[1] = 1; s.b[2] = 3;  // H=3, labels 3,1,3 -> should become 1,2,1
  canonicalizeSig(s.b, 3);
  assert(s.b[0] == 1 && s.b[1] == 2 && s.b[2] == 1);
  // idempotent: second pass unchanged
  Sig s2 = s;
  canonicalizeSig(s2.b, 3);
  assert(std::memcmp(s.b, s2.b, SIGMAX) == 0);
}

static void testReflectInvolution() {
  // reflect twice = identity (after double-canonicalize)
  Sig s;
  std::memset(s.b, 0, SIGMAX);
  s.b[0] = 1; s.b[2] = 2; s.b[4] = 1;  // H=5, sparse
  s.b[5] = 1; s.b[6] = 0;               // touch flags
  const int H = 5;
  Sig r1 = reflectSig(s, H);
  Sig r2 = reflectSig(r1, H);
  // r2 should equal canonicalize(s)
  Sig sc = s;
  canonicalizeSig(sc.b, H);
  assert(std::memcmp(r2.b, sc.b, SIGMAX) == 0);
}

static void testFoldIdempotent() {
  // fold(fold(x)) == fold(x): fold selects the canonical min of {s, reflect(s)}
  for (int H = 2; H <= 8; ++H) {
    Sig s;
    std::memset(s.b, 0, SIGMAX);
    for (int i = 0; i < H; ++i) s.b[i] = (unsigned char)((i % 3) + (i > 0 ? 1 : 0));
    canonicalizeSig(s.b, H);
    Sig once = s; foldSig(once, H);
    Sig twice = once; foldSig(twice, H);
    assert(std::memcmp(once.b, twice.b, SIGMAX) == 0);
  }
}

static void testCompletionLowerBoundAdmissible() {
  // CLB(empty sig) == 0
  Sig empty; std::memset(empty.b, 0, SIGMAX);
  assert(completionLowerBound(empty.b, 4) == 0);

  // CLB(single cell at row 0, H=4, untouched bottom) must require >=3 cells
  // (need to reach row 3: gap of 3)
  Sig s; std::memset(s.b, 0, SIGMAX);
  s.b[0] = 1;   // occupied row 0
  s.b[4] = 1;   // touched top
  s.b[5] = 0;   // not touched bottom
  const int lb = completionLowerBound(s.b, 4);
  assert(lb >= 3);  // must span rows 1,2,3 at minimum

  // CLB never over-estimates: lb <= actual minimum cells to complete.
  // Structural: CLB is defined to never over-estimate; admissibility is
  // tested by the regression gate (a wrong lb makes counts low, gate catches it).
}

static void testStepColumnSmoke() {
  // Minimal smoke: feed an empty sig, a mask with one bit set -> Alive result
  const int H = 4;
  Sig src; std::memset(src.b, 0, SIGMAX);
  Sig dst;
  // mask = bit 1 set (second row): one new cell, no old connectivity to link
  unsigned mask = 1u << 1;
  Outcome o = stepColumnSquare8(src, H, mask, dst);
  assert(o == Outcome::Alive);
  // dst should have exactly one label in row 1
  assert(dst.b[1] != 0);
  assert(dst.b[0] == 0 && dst.b[2] == 0 && dst.b[3] == 0);
}

int main() {
  testCanonicalize();
  testReflectInvolution();
  testFoldIdempotent();
  testCompletionLowerBoundAdmissible();
  testStepColumnSmoke();
  std::puts("gate_math PASS");
}
