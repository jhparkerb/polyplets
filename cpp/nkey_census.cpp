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

// Retire every live group that nothing can reach any more.
//
// `keep` must include BOTH the old blocks a later row can still attach to AND
// the ones the run in progress has already attached to.  Leaving the second
// out is a silent merge failure: a closed group and the open run can share an
// old block whose last row has just passed, and they are then one component
// that this would file as two.
void retire(Partial& p, u32 keep) {
  size_t w = 0;
  bool moved = false;
  for (size_t i = 0; i < p.liveMask.size(); ++i) {
    if ((p.liveTouch[i] & keep) == 0) {
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
        retire(q, reachable | q.curTouch);
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

// ------------------------------------------------------------- shared sweep
//
// The same census, with the partial fills SHARED between source states.
//
// successors() above rebuilds the row-by-row refinement separately for every
// source key, so a partial fill that a thousand sources admit is explored a
// thousand times -- which is why results/nkey-census.md prices H = 18 at three
// days and H = 21 out of reach.  The production engine does not have this
// problem: its carry sweeps cells globally, so intermediate states are shared.
// This does the same thing here.  A whole batch of sources is swept together,
// one row at a time, and the state carries only what the REMAINING rows can
// still see:
//
//   future[i]   old block i's dilated mask restricted to rows >= the current
//               one -- so two sources that differ only below the sweep become
//               the same state and their remaining work is done once
//   Partial     exactly the structure successors() uses, unchanged
//
// The correctness argument is that dropping a block is only ever done when
// nothing can reach it again: no later row attaches to it (no bit at or above
// the next row) and the run in progress does not hold it.  Both halves are
// needed -- leaving the second out is the merge failure 384bd2e fixed.  A
// block dropped without ever having been touched strands a component, and that
// column is dead, which is the same test successors() makes as `touched !=
// allOld` at the end.
//
// Nothing here is trusted on that argument.  The two engines are separate
// implementations of one count and --gate runs the banked king ladder and the
// rook RED control through BOTH, so a wrong sharing rule has to reproduce
// 8, 19, 43, 101, 239, 575, 1399, 3441, 8539, 21355 and Motzkin(H+1)-1 to hide.

struct Shared {
  std::vector<u32> future;  // old blocks still carried; index = touch bit
  Partial p;

  bool operator==(const Shared& o) const {
    return future == o.future && p == o.p;
  }
};

struct SharedHash {
  size_t operator()(const Shared& s) const {
    u64 h = PartialHash{}(s.p);
    for (u32 v : s.future) {
      h ^= v;
      h *= 1099511628211ull;
    }
    h ^= s.future.size() * 0x9e3779b97f4a7c15ull;
    h *= 1099511628211ull;
    return static_cast<size_t>(h);
  }
};

// Put the old blocks in an order that depends only on what they are and what
// touches them, so two states that differ by a relabelling become one.  This
// is an optimisation and nothing rests on it: a labelling that fails to
// canonicalise costs duplicated work, never a wrong count, because the answer
// is a set of KEYS and every key is sorted before it is counted.
void canonBlocks(Shared& s) {
  const size_t B = s.future.size();
  if (B < 2) {
    sortLive(s.p);
    return;
  }
  std::vector<std::vector<u32>> sig(B);
  for (size_t i = 0; i < B; ++i) {
    sig[i].push_back(s.future[i]);
    sig[i].push_back((s.p.curTouch >> i) & 1);
    for (size_t j = 0; j < s.p.liveMask.size(); ++j)
      if ((s.p.liveTouch[j] >> i) & 1) sig[i].push_back(s.p.liveMask[j]);
    std::sort(sig[i].begin() + 2, sig[i].end());
  }
  std::vector<size_t> idx(B);
  for (size_t i = 0; i < B; ++i) idx[i] = i;
  std::sort(idx.begin(), idx.end(), [&sig](size_t a, size_t b) {
    if (sig[a] != sig[b]) return sig[a] < sig[b];
    return a < b;
  });
  bool identity = true;
  for (size_t i = 0; i < B; ++i)
    if (idx[i] != i) { identity = false; break; }
  if (!identity) {
    std::vector<int> pos(B);
    for (size_t i = 0; i < B; ++i) pos[idx[i]] = static_cast<int>(i);
    auto remap = [&pos, B](u32 m) {
      u32 r = 0;
      for (size_t i = 0; i < B; ++i)
        if ((m >> i) & 1) r |= 1u << pos[i];
      return r;
    };
    std::vector<u32> nf(B);
    for (size_t i = 0; i < B; ++i) nf[i] = s.future[idx[i]];
    s.future.swap(nf);
    for (u32& t : s.p.liveTouch) t = remap(t);
    s.p.touched = remap(s.p.touched);
    s.p.curTouch = remap(s.p.curTouch);
  }
  sortLive(s.p);
}

// Advance the state to `nextRow`: forget the part of every old block that is
// now behind the sweep, drop the blocks nothing can reach again, and put what
// is left in canonical order.  False means the column strands a block.
bool advance(Shared& s, int nextRow) {
  const size_t B = s.future.size();
  const u32 above = (nextRow >= 32) ? 0u : ~((1u << nextRow) - 1u);
  bool drop = false;
  for (size_t i = 0; i < B; ++i) {
    const bool reach = (s.future[i] & above) != 0;
    const bool held = (s.p.curTouch >> i) & 1;
    if (reach || held) continue;
    if (((s.p.touched >> i) & 1) == 0) return false;  // stranded: dead column
    drop = true;
  }
  if (!drop) {
    for (size_t i = 0; i < B; ++i) s.future[i] &= above;
    canonBlocks(s);
    return true;
  }
  std::vector<u32> nf;
  nf.reserve(B);
  std::vector<int> pos(B, -1);
  for (size_t i = 0; i < B; ++i) {
    const bool reach = (s.future[i] & above) != 0;
    const bool held = (s.p.curTouch >> i) & 1;
    if (!reach && !held) continue;
    pos[i] = static_cast<int>(nf.size());
    nf.push_back(s.future[i] & above);
  }
  auto remap = [&pos, B](u32 m) {
    u32 r = 0;
    for (size_t i = 0; i < B; ++i)
      if (((m >> i) & 1) && pos[i] >= 0) r |= 1u << pos[i];
    return r;
  };
  for (u32& t : s.p.liveTouch) t = remap(t);
  s.p.touched = remap(s.p.touched);
  s.p.curTouch = remap(s.p.curTouch);
  s.future.swap(nf);
  retire(s.p, 0xffffffffu);  // a group with nothing left to merge through
  canonBlocks(s);
  return true;
}

// Sweep one batch of source keys together, appending every successor key.
void sweepBatch(const std::vector<Key>& srcs, int H, bool dilate_on,
                std::vector<Key>& out, u64* peak) {
  std::unordered_set<Shared, SharedHash> cur, next;
  for (const Key& k : srcs) {
    Shared s;
    s.future = k;
    canonBlocks(s);
    cur.insert(std::move(s));
  }
  for (int row = 0; row < H; ++row) {
    const u32 above = ~((1u << row) - 1u);
    next.clear();
    for (const Shared& s : cur) {
      const size_t B = s.future.size();
      u32 reachable = 0, attach = 0;
      for (size_t i = 0; i < B; ++i) {
        if (s.future[i] & above) reachable |= 1u << i;
        if ((s.future[i] >> row) & 1) attach |= 1u << i;
      }
      {  // (a) leave the row empty
        Shared q = s;
        closeRun(q.p);
        retire(q.p, reachable);
        if (advance(q, row + 1)) next.insert(std::move(q));
      }
      {  // (b) fill it
        Shared q = s;
        q.p.curDil |= dilate(1u << row, H, dilate_on);
        q.p.curTouch |= attach;
        q.p.curOpen = true;
        retire(q.p, reachable | q.p.curTouch);
        if (advance(q, row + 1)) next.insert(std::move(q));
      }
    }
    cur.swap(next);
    if (peak && cur.size() > *peak) *peak = cur.size();
  }
  for (const Shared& s0 : cur) {
    Shared s = s0;
    closeRun(s.p);
    retire(s.p, 0);
    if (!advance(s, H)) continue;  // an old block stranded: dead
    if (s.p.fin.empty()) continue; // the empty column is not a transition
    Key k = s.p.fin;
    std::sort(k.begin(), k.end());
    out.push_back(std::move(k));
  }
}

// The same reachable-key count as census(), by batched breadth-first rounds so
// that a whole round's sources share their partial fills.
u64 censusShared(int H, bool dilate_on, obs::Reporter* rep, size_t batch) {
  std::unordered_set<Key, KeyHash> seen;
  Key empty;
  seen.insert(empty);
  std::vector<Key> frontier{empty}, produced, grown;
  u64 rounds = 0, peak = 0;

  while (!frontier.empty()) {
    grown.clear();
    for (size_t off = 0; off < frontier.size(); off += batch) {
      const size_t hi = std::min(frontier.size(), off + batch);
      std::vector<Key> chunk(frontier.begin() + off, frontier.begin() + hi);
      produced.clear();
      sweepBatch(chunk, H, dilate_on, produced, &peak);
      for (Key& t : produced)
        if (seen.insert(t).second) grown.push_back(std::move(t));
    }
    frontier.swap(grown);
    ++rounds;
    if (rep)
      rep->beat(static_cast<double>(rounds),
                "seen=" + std::to_string(seen.size()) +
                    " frontier=" + std::to_string(frontier.size()) +
                    " peak_sweep=" + std::to_string(peak));
  }
  return seen.size() - 1;
}

// The reachable key set from the empty frontier, minus the empty start itself
// -- the convention of experiments/skeletonkey/nfamily_merge.py, whose counts
// this must reproduce.
u64 census(int H, bool dilate_on, obs::Reporter* rep) {
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
  return seen.size() - 1;
}

// Cross-check: the two engines must agree on the SUCCESSOR SET of every
// reachable key, not merely on how many keys are reachable.
//
// This exists because agreeing on the count is too weak.  Disabling the
// stranded-block prune in advance() -- letting a column that never touches an
// old block count as a transition -- leaves every banked class count intact,
// because the extra successors it invents are already reachable by other
// routes.  A control that a real defect walks through is not a control, so the
// comparison is made where the defect actually lives: per source, on the set
// of keys produced.
// TODO(2026-08-24, /simplify): every reachable key's successor set is computed
// twice -- once inside the reachability BFS (discarded past dedup) and again in
// the comparison loop. Keeping each key's successors from the BFS, or comparing
// inside it, halves that. Seconds at the gated H<=11, so worth doing only if
// this gate ever runs deeper.
bool crossCheck(int H, bool dilate_on) {
  std::unordered_set<Key, KeyHash> seen;
  std::vector<Key> frontier, order;
  Key empty;
  seen.insert(empty);
  frontier.push_back(empty);
  order.push_back(empty);
  std::vector<Key> work;
  while (!frontier.empty()) {
    Key s0 = std::move(frontier.back());
    frontier.pop_back();
    work.clear();
    successors(s0, H, dilate_on, work);
    for (Key& t : work)
      if (seen.insert(t).second) {
        frontier.push_back(t);
        order.push_back(std::move(t));
      }
  }
  std::vector<Key> a, b, one;
  u64 bad = 0;
  for (const Key& k : order) {
    a.clear();
    successors(k, H, dilate_on, a);
    std::sort(a.begin(), a.end());
    a.erase(std::unique(a.begin(), a.end()), a.end());
    b.clear();
    one.assign(1, k);
    sweepBatch(one, H, dilate_on, b, nullptr);
    std::sort(b.begin(), b.end());
    b.erase(std::unique(b.begin(), b.end()), b.end());
    if (a != b) ++bad;
  }
  std::printf("  H=%-3d %s  %zu sources, %llu disagree  %s\n", H,
              dilate_on ? "king" : "rook", order.size(),
              (unsigned long long)bad, bad ? "FAILED" : "ok");
  std::fflush(stdout);
  return bad == 0;
}

const u64 KING[] = {0, 0, 0, 0, 8, 19, 43, 101, 239, 575, 1399, 3441, 8539, 21355};
const u64 ROOK[] = {0, 0, 3, 8, 20, 50, 126, 322, 834, 2187, 5797};

bool gate(bool shared, size_t batch) {
  bool ok = true;
  const char* eng = shared ? "shared" : "per-source";
  std::printf("gate king [%s] (class counts, results/skeletonkey-nfamily-merge.md)\n", eng);
  for (int H = 4; H <= 13; ++H) {
    const u64 got = shared ? censusShared(H, true, nullptr, batch)
                           : census(H, true, nullptr);
    const u64 want = KING[H];
    const bool good = got == want;
    ok &= good;
    std::printf("  H=%-3d %10llu  want %10llu  %s\n", H,
                (unsigned long long)got, (unsigned long long)want,
                good ? "ok" : "FAILED");
    std::fflush(stdout);
  }
  std::printf("gate rook [%s] (RED control: no dilation => key is the state, "
              "so the count must be Motzkin(H+1)-1)\n", eng);
  for (int H = 2; H <= 10; ++H) {
    const u64 got = shared ? censusShared(H, false, nullptr, batch)
                           : census(H, false, nullptr);
    const u64 want = ROOK[H];
    const bool good = got == want;
    ok &= good;
    std::printf("  H=%-3d %10llu  want %10llu  %s\n", H,
                (unsigned long long)got, (unsigned long long)want,
                good ? "ok" : "FAILED");
    std::fflush(stdout);
  }
  if (shared) {
    std::printf("gate cross-engine (successor SETS per source, not just the "
                "reachable count)\n");
    for (int H = 2; H <= 11; ++H) ok &= crossCheck(H, true);
    for (int H = 2; H <= 9; ++H) ok &= crossCheck(H, false);
  }
  std::printf("%s [%s]\n", ok ? "GATES PASS" : "GATES FAILED", eng);
  return ok;
}

}  // namespace

const char kUsage[] =
    "usage: nkey_census --gate | [--rook] [--shared] [--batch=N] H [H2]\n";

int main(int argc, char** argv) {
  bool dilate_on = true, shared = false;
  size_t batch = 1u << 20;
  std::vector<const char*> rest;
  for (int i = 1; i < argc; ++i) {
    if (std::strcmp(argv[i], "--rook") == 0) dilate_on = false;
    else if (std::strcmp(argv[i], "--shared") == 0) shared = true;
    else if (std::strncmp(argv[i], "--batch=", 8) == 0) {
      batch = static_cast<size_t>(std::strtoull(argv[i] + 8, nullptr, 10));
      if (batch == 0) { std::fprintf(stderr, "--batch must be positive\n"); return 2; }
    } else rest.push_back(argv[i]);
  }
  if (rest.empty()) { std::fprintf(stderr, kUsage); return 2; }

  // --gate runs BOTH engines: they are two implementations of one count, and
  // the banked ladder plus the rook RED control is what either has to clear.
  if (std::strcmp(rest[0], "--gate") == 0)
    return (gate(false, batch) && gate(true, batch)) ? 0 : 1;

  // rest is non-empty (checked above), so H1 always exists; H2 defaults to it.
  const int H1 = std::atoi(rest[0]);
  const int H2 = rest.size() > 1 ? std::atoi(rest[1]) : H1;
  if (H1 < 1 || H2 < H1 || H2 > 30) {
    std::fprintf(stderr, "H out of range\n");
    return 2;
  }

  // The gates run first, every time, so no height is ever reported by a binary
  // that has not just re-established that it reproduces the banked ladder.
  if (!gate(shared, batch)) return 1;

  for (int H = H1; H <= H2; ++H) {
    obs::Reporter rep("nkey_census", 0,
                      "H=" + std::to_string(H) +
                          (dilate_on ? " lattice=king" : " lattice=rook") +
                          (shared ? " engine=shared" : " engine=per-source"));
    const u64 n = shared ? censusShared(H, dilate_on, &rep, batch)
                         : census(H, dilate_on, &rep);
    rep.done("H=" + std::to_string(H) + " classes=" + std::to_string(n));
    std::printf("%d %llu\n", H, (unsigned long long)n);
    std::fflush(stdout);
  }
  return 0;
}
