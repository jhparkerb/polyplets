// strip_stage_ops.h — the indexed-array form of the strip-mu kink column sweep.
//
// WHY.  cpp/strip_mu_kink.cpp and cpp/strip_mu_cert.cpp both compute one matvec
// of the height-<=H king transfer operator M(x) as a cell-at-a-time column
// sweep: seed -> H per-cell kink stage transitions (weight x^placed, states
// MERGE) -> finalize.  Both hold every intermediate stage in an
// unordered_map<Sig, value> and RE-DERIVE the transition for every state on
// every one of the thousands of matvecs a bisection-over-power-iteration needs.
// Measured at H=11 (results/strip-mu-fast.md): 37% of the sweep is the hash-map
// accumulate and the remaining 63% is the union-find + canonMixed + bucket walk
// — i.e. ~100% of the sweep is work whose ANSWER never changes with x or with
// the iterate.
//
// WHAT.  The state graph is enumerated ONCE per H and frozen into indices:
//
//   S_0            the boundary states (H canonical label bytes, flags zero) —
//                  exactly the key set the old engines' vectors converge to
//   S_1 .. S_H     the mixed states after stages 0..H-1 (row bytes, carry byte
//                  b[H+2], touch flags b[H], b[H+1], nonempty flag b[H+3])
//   t0[r], t1[r]   for each i in S_r, the index in S_{r+1} of the "no cell" and
//                  "cell placed" successor, or -1 when the kink transition
//                  suppresses it (stranded label).  At most two successors per
//                  state, so the sparse operator is two int32 arrays, not CSR.
//   fin            for each i in S_H, the S_0 index it finalizes to, or -1
//                  (empty column = completion, or a stranded outgoing label).
//
// A matvec is then H scatter passes over flat arrays plus one finalize pass —
// no hashing, no union-find, no signature bytes touched at all.
//
// The enumeration is a layered BFS: every state is expanded EXACTLY ONCE (a
// per-stage "processed" watermark), so building the tables costs about one
// symbolic sweep in total, which thousands of matvecs amortize to nothing.
//
// SHARED KERNEL.  applyOps is templated on the value type and on a weight
// policy, so the float power iteration (double, weight x) and the certificate's
// exact check (unsigned __int128, weight floor(v*p/q) with a 2^126 guard) run
// the SAME indexed operator over the SAME frozen state set.  A policy may fail
// (overflow); applyOps then returns false and the caller must treat that as a
// failed certificate — fail-closed, never a silent wrap.
//
// The three kink functions are copied VERBATIM from core/kink.h (the single
// source of truth), exactly as cpp/strip_mu_kink.cpp and cpp/strip_mu_cert.cpp
// do, to avoid pulling in the run/spill machinery kink.h includes. They live in
// namespace strip so a translation unit that already has its own copy (the
// certificate tool does) can include this header without a clash.

#pragma once

#include <cstdint>
#include <cstring>
#include <vector>

#include "core/signature.h"   // Sig, SIGMAX, canonicalizeSig
#include "core/transition.h"  // namespace s8 (find/unite)

namespace strip {

// ---- copied verbatim from core/kink.h ----
inline void canonMixed(Sig& s, int H) {
  unsigned char map[256] = {0}; unsigned char next = 1;
  for (int i = 0; i < H; ++i) { const unsigned char v = s.b[i];
    if (v == 0) continue; if (map[v] == 0) map[v] = next++; s.b[i] = map[v]; }
  const unsigned char c = s.b[H + 2];
  if (c != 0) { if (map[c] == 0) map[c] = next++; s.b[H + 2] = map[c]; }
}
inline bool labelInMixedState(const Sig& s, int H, unsigned char L) {
  for (int i = 0; i < H; ++i) if (s.b[i] == L) return true;
  return s.b[H + 2] == L;
}
template <class F>
inline void kinkStageTransition(const Sig& s, int H, int r, int ms, int maxn, F&& emit) {
  int uf[2 * SIGMAX];
  for (int occupy = 0; occupy < 2; ++occupy) {
    if (occupy && ms + 1 > maxn) break;
    Sig t = s; unsigned char newLabel = 0;
    if (occupy) {
      for (int i = 0; i < 2 * SIGMAX; ++i) uf[i] = i;
      auto uadd = [&](unsigned char L) { if (L) { int a = s8::find(uf, 0), b = s8::find(uf, L); if (a != b) uf[a] = b; } };
      if (r > 0) uadd(s.b[r - 1]);
      uadd(s.b[r]); uadd(s.b[H + 2]); if (r + 1 < H) uadd(s.b[r + 1]);
      const int root = s8::find(uf, 0); unsigned char fresh = 200;
      for (int i = 0; i < H; ++i) if (t.b[i] && s8::find(uf, t.b[i]) == root) t.b[i] = fresh;
      if (t.b[H + 2] && s8::find(uf, t.b[H + 2]) == root) t.b[H + 2] = fresh;
      newLabel = fresh;
    }
    const unsigned char outgoing = t.b[H + 2];
    t.b[H + 2] = t.b[r]; t.b[r] = occupy ? newLabel : 0;
    if (occupy) { if (r == 0) t.b[H] = 1; if (r == H - 1) t.b[H + 1] = 1; t.b[H + 3] = 1; }
    if (outgoing != 0 && !labelInMixedState(t, H, outgoing)) continue;
    canonMixed(t, H); emit(t, occupy ? 1 : 0);
  }
}
// ---- end copy ----

// The enumerator's state store: a flat open-addressing interner over keys
// PACKED to H+4 bytes rather than the full SIGMAX. Both economies are what make
// large H a memory question rather than a memory wall — an
// unordered_map<Sig,int32> costs ~165 bytes per state (measured, H=14), this
// costs ~26 at H=16, and the build touches every stage of every height at once.
// Packing to H+4 is lossless here: kinkStageTransition writes only bytes
// 0..H+3, and the empty seed is all zeros, so bytes past H+4 are identically 0
// for every reachable state.
class StageSet {
 public:
  explicit StageSet(int keyLen) : keyLen_(keyLen), slot_(1024, 0) {}

  std::size_t size() const { return count_; }

  void get(std::size_t i, Sig& out) const {
    std::memset(out.b, 0, SIGMAX);
    std::memcpy(out.b, data_.data() + i * keyLen_, keyLen_);
  }

  std::int32_t intern(const Sig& s) {
    std::size_t m = slot_.size() - 1;
    std::size_t h = hash(s.b) & m;
    while (slot_[h]) {
      const std::int32_t id = slot_[h] - 1;
      if (std::memcmp(data_.data() + (std::size_t)id * keyLen_, s.b,
                      (std::size_t)keyLen_) == 0)
        return id;
      h = (h + 1) & m;
    }
    const std::int32_t id = static_cast<std::int32_t>(count_++);
    data_.insert(data_.end(), s.b, s.b + keyLen_);
    slot_[h] = id + 1;
    if (count_ * 10 >= slot_.size() * 7) rehash();
    return id;
  }

 private:
  std::size_t hash(const unsigned char* b) const {
    std::size_t h = 1469598103934665603ULL;
    for (int i = 0; i < keyLen_; ++i) { h ^= b[i]; h *= 1099511628211ULL; }
    return h ^ (h >> 32);
  }
  void rehash() {
    std::vector<std::int32_t> ns(slot_.size() * 2, 0);
    const std::size_t m = ns.size() - 1;
    for (std::size_t i = 0; i < count_; ++i) {
      std::size_t h = hash(data_.data() + i * keyLen_) & m;
      while (ns[h]) h = (h + 1) & m;
      ns[h] = static_cast<std::int32_t>(i) + 1;
    }
    slot_.swap(ns);
  }
  int keyLen_;
  std::vector<unsigned char> data_;
  std::vector<std::int32_t> slot_;
  std::size_t count_ = 0;
};

// The frozen per-stage sparse operators for one height H.
struct StageOps {
  int H = 0;
  std::vector<Sig> boundary;                   // S_0: index -> boundary Sig
  std::vector<std::size_t> size;               // size[r] = |S_r|, r = 0..H
  std::vector<std::vector<std::int32_t>> t0;   // t0[r][i]: "no cell" successor
  std::vector<std::vector<std::int32_t>> t1;   // t1[r][i]: "cell placed"
  std::vector<std::int32_t> fin;               // |S_H| -> S_0 index, or -1
  std::size_t support = 0;                     // S_0 entries with an in-edge

  // The operator's live state count. S_0 additionally holds the empty seed
  // boundary, which no finalize edge ever targets (an empty column is a
  // completion, not a transfer), so it carries zero mass from the second matvec
  // on. Excluding it is what makes this number the one the map engines print
  // (their vectors converge to exactly the in-edge-reachable set) and the one in
  // results/strip_mu_certificates.log.
  std::size_t states() const { return support; }
  std::size_t maxStage() const {
    std::size_t m = 0; for (auto s : size) if (s > m) m = s; return m;
  }
  std::size_t stageTotal() const {                       // sum_r |S_r|, r < H
    std::size_t t = 0; for (int r = 0; r < H; ++r) t += size[r]; return t;
  }
  std::size_t tableBytes() const {
    return (stageTotal() * 2 + (size.empty() ? 0 : size[H])) *
           sizeof(std::int32_t);
  }
};

// maxn cap for kinkStageTransition: the strip operator places no bound on the
// cell count (the weight x^placed carries it), so the budget is effectively
// infinite. Same constant the two existing engines pass.
static const int STRIP_BIG = 1 << 29;

// Enumerate the reachable layered state graph from the empty boundary and
// freeze it. Layered BFS with a per-stage watermark: state i of S_r is expanded
// once, when it is first seen, and its two successor indices are appended in
// index order — so t0[r][i] / t1[r][i] line up with S_r by construction.
inline StageOps buildStageOps(int H) {
  StageOps O;
  O.H = H;
  O.t0.resize(H);
  O.t1.resize(H);
  std::vector<StageSet> st(H + 1, StageSet(H + 4));
  std::vector<std::size_t> done(H + 1, 0);

  Sig empty;
  std::memset(empty.b, 0, SIGMAX);
  st[0].intern(empty);

  bool grew = true;
  while (grew) {
    grew = false;
    for (int r = 0; r < H; ++r) {
      for (; done[r] < st[r].size(); ++done[r]) {
        Sig s;
        st[r].get(done[r], s);
        std::int32_t a = -1, b = -1;
        kinkStageTransition(s, H, r, 0, STRIP_BIG,
                            [&](const Sig& t, int shift) {
                              const std::int32_t j = st[r + 1].intern(t);
                              if (shift) b = j; else a = j;
                            });
        O.t0[r].push_back(a);
        O.t1[r].push_back(b);
        grew = true;
      }
    }
    for (; done[H] < st[H].size(); ++done[H]) {
      Sig m;
      st[H].get(done[H], m);
      std::int32_t target = -1;
      if (m.b[H + 3]) {                       // empty column = completion, drop
        const unsigned char outgoing = m.b[H + 2];
        Sig t = m;
        t.b[H + 2] = 0; t.b[H + 3] = 0;
        if (outgoing == 0 || labelInMixedState(t, H, outgoing)) {
          canonicalizeSig(t.b, H);
          t.b[H] = 0; t.b[H + 1] = 0;         // <=H merge: drop the touch flags
          target = st[0].intern(t);
        }
      }
      O.fin.push_back(target);
      grew = true;
    }
  }

  O.size.resize(H + 1);
  for (int r = 0; r <= H; ++r) O.size[r] = st[r].size();
  std::vector<char> hit(st[0].size(), 0);
  for (std::int32_t j : O.fin) if (j >= 0) hit[j] = 1;
  for (char c : hit) O.support += c ? 1 : 0;
  O.boundary.resize(st[0].size());
  for (std::size_t i = 0; i < st[0].size(); ++i) st[0].get(i, O.boundary[i]);
  return O;
}

// One matvec of M(x) restricted to S_0, as H indexed scatter passes plus a
// finalize pass. `in` and `out` are dense over S_0 (out may alias neither buf).
// `bufA` / `bufB` are caller-owned scratch so a power iteration allocates once.
// Returns false iff the weight policy reported overflow — callers must treat
// that as a hard failure, never as a result.
//
// A policy W provides:
//   bool placed(const T& val, T& term) const;   // "cell placed" branch weight
//   bool add(T& acc, const T& term) const;      // accumulate into a slot
// (the "no cell" branch has weight 1 and is added unchanged, exactly as the
// map engines do — that half of the sweep stays exact under the u128 policy).
template <class T, class W>
inline bool applyOps(const StageOps& O, const std::vector<T>& in,
                     std::vector<T>& out, const W& w, std::vector<T>& bufA,
                     std::vector<T>& bufB) {
  const int H = O.H;
  bufA.assign(in.begin(), in.end());
  for (int r = 0; r < H; ++r) {
    bufB.assign(O.size[r + 1], T(0));
    const std::int32_t* a = O.t0[r].data();
    const std::int32_t* b = O.t1[r].data();
    const std::size_t n = O.size[r];
    for (std::size_t i = 0; i < n; ++i) {
      const T val = bufA[i];
      if (val == T(0)) continue;
      const std::int32_t ja = a[i];
      if (ja >= 0 && !w.add(bufB[ja], val)) return false;
      const std::int32_t jb = b[i];
      if (jb >= 0) {
        T term;
        if (!w.placed(val, term)) return false;
        if (!w.add(bufB[jb], term)) return false;
      }
    }
    bufA.swap(bufB);
  }
  out.assign(O.size[0], T(0));
  const std::size_t n = O.size[H];
  for (std::size_t i = 0; i < n; ++i) {
    const std::int32_t j = O.fin[i];
    if (j < 0) continue;
    const T val = bufA[i];
    if (val == T(0)) continue;
    if (!w.add(out[j], val)) return false;
  }
  return true;
}

// Float policy: the "cell placed" branch carries x.
struct FloatWeight {
  double x;
  explicit FloatWeight(double x_) : x(x_) {}
  bool placed(double v, double& t) const { t = v * x; return true; }
  bool add(double& a, double t) const { a += t; return true; }
};

// Exact policy: x = p/q with EVERY rounding downward, so the computed vector is
// <= the true M(p/q) v componentwise and a passing check passes on the exact
// product. Every multiply and add is guarded against 2^126 (a full bit below
// the unsigned __int128 range, so the guard itself cannot wrap); a trip returns
// false, which applyOps turns into a hard failure. Identical arithmetic to
// cpp/strip_mu_cert.cpp's matvecExact, term for term.
struct ExactWeight {
  using u128 = unsigned __int128;
  static constexpr u128 LIMIT = (u128)1 << 126;
  u128 p, q;
  mutable u128 maxAcc = 0;
  ExactWeight(u128 p_, u128 q_) : p(p_), q(q_) {}
  bool placed(u128 v, u128& t) const {
    if (v > LIMIT / p) return false;
    t = (v * p) / q;                          // DOWNWARD: floor(val*x)
    return true;
  }
  bool add(u128& a, u128 t) const {
    if (a > LIMIT - t) return false;
    a += t;
    if (a > maxAcc) maxAcc = a;
    return true;
  }
};

}  // namespace strip
