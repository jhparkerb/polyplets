// Census of the reach-merged column frontier: how many N-key classes exist at
// height H, exactly, with no extrapolation.
//
// WHY.  results/skeletonkey-nfamily-merge.md establishes that two strip states
// are equivalent iff they carry the same multiset of block neighbourhoods
// N(b) = rows(b) dilated by +-1 -- a congruence, gated exhaustively, over any
// semiring.  The merged set IS the end-of-column frontier that
// results/kink-carry.md names as the engine's wall.  What the merge file
// refuses to do, correctly, is quote a class count at H = 21: the ratio
// compounds with no closed form, no OEIS match on 8, 19, 43, 101, 239, 575,
// 1399, 3441, 8539, and no recurrence with surplus.  This measures it instead.
//
// WHAT IT REPLACES.  experiments/skeletonkey/nfamily_merge.py generates
// successors by iterating all 2^H column masks per state: H = 13 cost 962 s
// and 18 GB on ayr and H = 14 alone would be over an hour.  Here the column is
// swept ONE CELL AT A TIME -- a row-by-row breadth-first refinement of partial
// states, deduped at every row -- so a source state costs the number of
// distinct partial fills it admits rather than 2^H.
//
// WHAT IT DOES NOT SETTLE, unchanged from the merge file: whether the
// mid-column stage tables inherit the cut (the congruence is proved at column
// boundaries only), and what the telescope costs the completion prune.  This
// is a state count and nothing else -- no engine change is implied and no wall
// clock is measured.
//
// GATES, both fail-closed and both run by --gate before any new height:
//   king  the class counts must be 8, 19, 43, 101, 239, 575, 1399, 3441, 8539
//         at H = 4..12 (results/skeletonkey-nfamily-merge.md, and Exact
//         Change's independent minauto at H = 12) and 21355 at H = 13
//         (measured 2026-08-22 by the Python probe).
//   rook  with the dilation switched off, N(b) = rows(b), so the key IS the
//         state and the count must be the raw frontier Motzkin(H+1) - 1
//         exactly: 3, 8, 20, 50, 126, 322, 834, 2187, 5797 at H = 2..10.
//         This is the RED control -- it fails loudly if the key is doing
//         anything other than what it claims.
//
// Usage:
//     build/nkey_census --gate            # both gate ladders, then exit
//     build/nkey_census H [H2]            # census at H, or the range H..H2
//     build/nkey_census --rook H          # the rook control at H
//
// Target: ayr or dalby.  Cost is measured per height as it goes and printed;
// H <= 14 is seconds.  Memory is the reachable key set: at H = 21 the
// extrapolated ~4e7 classes at ~40 B each is single-digit GB, and that
// extrapolation is exactly what this program exists to replace.

#include <algorithm>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <unordered_set>
#include <vector>

#include "obs.h"

namespace {

using u32 = uint32_t;
using u64 = uint64_t;

// A key is a sorted multiset of dilated masks, one per live block.  Blocks are
// few (at most (H+1)/2 of them), so a small vector is the whole data structure.
using Key = std::vector<u32>;

struct KeyHash {
  size_t operator()(const Key& k) const {
    u64 h = 1469598103934665603ull;
    for (u32 v : k) {
      h ^= v;
      h *= 1099511628211ull;
    }
    h ^= k.size();
    h *= 1099511628211ull;
    return static_cast<size_t>(h);
  }
};

// rows -> rows dilated by +-1, clipped to [0, H).  King adjacency is |dr| <= 1;
// dilate=false is the rook control, where the key degenerates to the state.
inline u32 dilate(u32 rows, int H, bool dilate_on) {
  if (!dilate_on) return rows;
  const u32 all = (H >= 32) ? 0xffffffffu : ((1u << H) - 1);
  return (rows | (rows << 1) | (rows >> 1)) & all;
}

// One partial fill of the new column, swept bottom to top.
//
// The compression that makes this affordable is the merge applied DURING the
// sweep rather than only at the end.  A new group can still absorb a later run
// only if the two share an old block that some later row can still attach to.
// Once every old block a group touches is out of reach, the group's identity
// stops mattering and only its dilated mask survives into the key -- so it is
// dropped into `fin`, a plain sorted multiset, and every partial fill that
// differs only in how it produced those masks collapses to one state.
//
//   fin        dilated masks of groups that can no longer merge, sorted
//   liveMask   dilated masks of groups that still can
//   liveTouch  the old blocks each of those has attached to
//   touched    every old block attached so far -- the survival test
//   cur*       the run in progress, if the previous row was filled
struct Partial {
  std::vector<u32> fin;
  std::vector<u32> liveMask;
  std::vector<u32> liveTouch;
  u32 touched = 0;
  u32 curDil = 0;
  u32 curTouch = 0;
  bool curOpen = false;

  bool operator==(const Partial& o) const {
    return touched == o.touched && curDil == o.curDil &&
           curTouch == o.curTouch && curOpen == o.curOpen && fin == o.fin &&
           liveMask == o.liveMask && liveTouch == o.liveTouch;
  }
};

struct PartialHash {
  size_t operator()(const Partial& p) const {
    u64 h = 14695981039346656037ull;
    auto mix = [&h](u64 v) { h ^= v; h *= 1099511628211ull; };
    for (u32 v : p.fin) mix(v);
    mix(0x9e3779b9u);
    for (size_t i = 0; i < p.liveMask.size(); ++i) {
      mix(p.liveMask[i]);
      mix(p.liveTouch[i]);
    }
    mix(p.touched);
    mix(p.curDil);
    mix(p.curTouch);
    mix(p.curOpen ? 1 : 0);
    return static_cast<size_t>(h);
  }
};

// Canonical order for the live groups, so two equal partials compare equal.
void sortLive(Partial& p) {
  const size_t n = p.liveMask.size();
  if (n < 2) return;
  std::vector<size_t> idx(n);
  for (size_t i = 0; i < n; ++i) idx[i] = i;
  std::sort(idx.begin(), idx.end(), [&p](size_t a, size_t b) {
    if (p.liveMask[a] != p.liveMask[b]) return p.liveMask[a] < p.liveMask[b];
    return p.liveTouch[a] < p.liveTouch[b];
  });
  std::vector<u32> m(n), t(n);
  for (size_t i = 0; i < n; ++i) {
    m[i] = p.liveMask[idx[i]];
    t[i] = p.liveTouch[idx[i]];
  }
  p.liveMask.swap(m);
  p.liveTouch.swap(t);
}

// Close the run in progress, merging it with every live group it shares an old
// block with.  A run that touches no old block is a fresh component.
void closeRun(Partial& p) {
  if (!p.curOpen) return;
  u32 mask = p.curDil, touch = p.curTouch;
  size_t w = 0;
  for (size_t i = 0; i < p.liveMask.size(); ++i) {
    if (touch && (p.liveTouch[i] & touch)) {
      mask |= p.liveMask[i];
      touch |= p.liveTouch[i];
    } else {
      p.liveMask[w] = p.liveMask[i];
      p.liveTouch[w] = p.liveTouch[i];
      ++w;
    }
  }
  p.liveMask.resize(w);
  p.liveTouch.resize(w);
  p.liveMask.push_back(mask);
  p.liveTouch.push_back(touch);
  p.touched |= touch;
  p.curDil = p.curTouch = 0;
  p.curOpen = false;
  sortLive(p);
}

// Retire every live group that no row from `row` on can reach.
void retire(Partial& p, u32 reachable) {
  size_t w = 0;
  bool moved = false;
  for (size_t i = 0; i < p.liveMask.size(); ++i) {
    if ((p.liveTouch[i] & reachable) == 0) {
      p.fin.push_back(p.liveMask[i]);
      moved = true;
    } else {
      p.liveMask[w] = p.liveMask[i];
      p.liveTouch[w] = p.liveTouch[i];
      ++w;
    }
  }
  if (!moved) return;
  p.liveMask.resize(w);
  p.liveTouch.resize(w);
  std::sort(p.fin.begin(), p.fin.end());
}

// All successor keys of one source key, generated cell at a time.
void successors(const Key& src, int H, bool dilate_on, std::vector<Key>& out) {
  const size_t B = src.size();
  const u32 allOld = (B >= 32) ? 0xffffffffu : ((1u << B) - 1);

  // topRow[i]: the last row at which old block i can still be attached to.
  std::vector<int> topRow(B);
  for (size_t i = 0; i < B; ++i) {
    int t = -1;
    for (int r = 0; r < H; ++r)
      if ((src[i] >> r) & 1) t = r;
    topRow[i] = t;
  }

  std::vector<Partial> cur, next;
  cur.push_back(Partial{});
  std::unordered_set<Partial, PartialHash> seen;

  for (int row = 0; row < H; ++row) {
    u32 expired = 0;    // out of reach from this row on -- must be touched
    u32 reachable = 0;  // still attachable at this row or later
    for (size_t i = 0; i < B; ++i) {
      if (topRow[i] < row) expired |= (1u << i);
      else reachable |= (1u << i);
    }
    u32 attach = 0;  // old blocks a cell in this row would attach to
    for (size_t i = 0; i < B; ++i)
      if ((src[i] >> row) & 1) attach |= (1u << i);

    next.clear();
    seen.clear();
    for (const Partial& p : cur) {
      // (a) leave the row empty
      {
        Partial q = p;
        closeRun(q);
        retire(q, reachable);
        if ((q.touched & expired) == expired && seen.insert(q).second)
          next.push_back(std::move(q));
      }
      // (b) fill it
      {
        Partial q = p;
        q.curDil |= dilate(1u << row, H, dilate_on);
        q.curTouch |= attach;
        q.curOpen = true;
        retire(q, reachable);
        if (((q.touched | q.curTouch) & expired) == expired &&
            seen.insert(q).second)
          next.push_back(std::move(q));
      }
    }
    cur.swap(next);
  }

  for (Partial& p : cur) {
    closeRun(p);
    retire(p, 0);
    if (p.touched != allOld) continue;  // an old block stranded: dead
    if (p.fin.empty()) continue;        // the empty column is not a transition
    Key k = p.fin;
    std::sort(k.begin(), k.end());
    out.push_back(std::move(k));
  }
}

// The reachable key set from the empty frontier, minus the empty start itself
// -- the convention of experiments/skeletonkey/nfamily_merge.py, whose counts
// this must reproduce.
u64 census(int H, bool dilate_on, obs::Reporter* rep, double* peakStates) {
  std::unordered_set<Key, KeyHash> seen;
  std::vector<Key> frontier, work;
  Key empty;
  seen.insert(empty);
  frontier.push_back(empty);
  u64 expanded = 0;

  while (!frontier.empty()) {
    Key s = std::move(frontier.back());
    frontier.pop_back();
    work.clear();
    successors(s, H, dilate_on, work);
    ++expanded;
    for (Key& t : work)
      if (seen.insert(t).second) frontier.push_back(std::move(t));
    if (rep && (expanded & 0xffff) == 0)
      rep->beat(static_cast<double>(expanded),
                "seen=" + std::to_string(seen.size()));
  }
  if (peakStates) *peakStates = static_cast<double>(seen.size());
  return seen.size() - 1;
}

const u64 KING[] = {0, 0, 0, 0, 8, 19, 43, 101, 239, 575, 1399, 3441, 8539, 21355};
const u64 ROOK[] = {0, 0, 3, 8, 20, 50, 126, 322, 834, 2187, 5797};

bool gate() {
  bool ok = true;
  std::printf("gate king (class counts, results/skeletonkey-nfamily-merge.md)\n");
  for (int H = 4; H <= 13; ++H) {
    const u64 got = census(H, true, nullptr, nullptr);
    const u64 want = KING[H];
    const bool good = got == want;
    ok &= good;
    std::printf("  H=%-3d %10llu  want %10llu  %s\n", H,
                (unsigned long long)got, (unsigned long long)want,
                good ? "ok" : "FAILED");
    std::fflush(stdout);
  }
  std::printf("gate rook (RED control: no dilation => key is the state, "
              "so the count must be Motzkin(H+1)-1)\n");
  for (int H = 2; H <= 10; ++H) {
    const u64 got = census(H, false, nullptr, nullptr);
    const u64 want = ROOK[H];
    const bool good = got == want;
    ok &= good;
    std::printf("  H=%-3d %10llu  want %10llu  %s\n", H,
                (unsigned long long)got, (unsigned long long)want,
                good ? "ok" : "FAILED");
    std::fflush(stdout);
  }
  std::printf("%s\n", ok ? "GATES PASS" : "GATES FAILED");
  return ok;
}

}  // namespace

int main(int argc, char** argv) {
  if (argc < 2) {
    std::fprintf(stderr,
                 "usage: nkey_census --gate | [--rook] H [H2]\n");
    return 2;
  }
  if (std::strcmp(argv[1], "--gate") == 0) return gate() ? 0 : 1;

  bool dilate_on = true;
  int a = 1;
  if (std::strcmp(argv[a], "--rook") == 0) {
    dilate_on = false;
    ++a;
  }
  if (a >= argc) {
    std::fprintf(stderr, "usage: nkey_census --gate | [--rook] H [H2]\n");
    return 2;
  }
  const int H1 = std::atoi(argv[a]);
  const int H2 = (a + 1 < argc) ? std::atoi(argv[a + 1]) : H1;
  if (H1 < 1 || H2 < H1 || H2 > 30) {
    std::fprintf(stderr, "H out of range\n");
    return 2;
  }

  // The gates run first, every time, so no height is ever reported by a binary
  // that has not just re-established that it reproduces the banked ladder.
  if (!gate()) return 1;

  for (int H = H1; H <= H2; ++H) {
    obs::Reporter rep("nkey_census", 0,
                      "H=" + std::to_string(H) +
                          (dilate_on ? " lattice=king" : " lattice=rook"));
    double states = 0;
    const u64 n = census(H, dilate_on, &rep, &states);
    rep.done("H=" + std::to_string(H) + " classes=" + std::to_string(n));
    std::printf("%d %llu\n", H, (unsigned long long)n);
    std::fflush(stdout);
  }
  return 0;
}
