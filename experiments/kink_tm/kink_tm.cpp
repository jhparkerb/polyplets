// FEASIBILITY PROBE -- NOT PRODUCTION. Thread: Shaving Lambda / Kink Carry.
//
// Question: the production engine transfers a WHOLE COLUMN per step
// (core/transition.h) because king adjacency needs the old NW cell that a
// cell-at-a-time boundary has already overwritten. The literature-standard
// alternative (Jensen's polyomino TM and every FLM descendant) moves the
// boundary ONE CELL at a time, and its per-state fan-out is 2 (cell empty /
// occupied) with intermediate states canonicalized and merged after every
// cell -- while ours is "all viable masks" (measured ~1.4k kept successors
// per state at H=12, growing exponentially with H). The whole-column design
// note "sidesteps" the NW problem; nothing in the repo ever priced the
// obvious fix: carry the ONE overwritten cell in the state (the kink carry).
//
// This probe implements the kink-carry cell-at-a-time king TM serially and
// checks it against the whole-column serial sweep:
//   gate    per-n counts at (H, maxn) must match the whole-column sweep
//           exactly (independent transition logic; shared helpers only).
//   metric  total transitions + peak/summed intermediate states + CPU time,
//           vs the whole-column sweep's kept-records + states + CPU time.
//
// Mixed-boundary state layout during a column (kink at row r = next cell to
// place in the new column):
//   b[0..r)    new-column cells (rightmost cell of those rows = column col)
//   b[r..H)    old-column cells (still column col-1)
//   carry      the old cell (col-1, r-1), overwritten at stage r-1 but still
//              king-reachable (it is NW of the cell being placed at stage r)
//   flags      touched-top / touched-bottom, as production
// Component labels span all of b[] plus the carry; canonicalized per stage.
// A new cell at (col, r) king-connects to: N = b[r-1] (new), W = b[r] (old,
// pre-overwrite), NW = carry, SW = b[r+1] (old). When the carry is replaced
// at the end of stage r, the outgoing carry's component is checked for
// stranding: if its label no longer appears in b[] or the new carry, that
// component can never be reached again -> state dead. The all-empty column
// (mask==0 in production, i.e. completion/no-op) is excluded by discarding
// end-of-column states that placed no cell, matching forEachViableMask's
// nonzero-mask contract; harvest of closable states happens at column start
// exactly as in the production sweep loop.
//
// Usage: kink_tm <H> <maxn>

#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <chrono>
#include <unordered_map>
#include <vector>

#include "core/signature.h"
#include "core/transition.h"

using u64 = std::uint64_t;

struct SigHash {
  size_t operator()(const Sig& s) const {
    u64 h = 1469598103934665603ull;
    for (int i = 0; i < SIGMAX; ++i) { h ^= s.b[i]; h *= 1099511628211ull; }
    return static_cast<size_t>(h);
  }
};

static int compCount(const Sig& s, int H) {
  int c = 0;
  for (int i = 0; i < H; ++i)
    if (s.b[i] > c) c = s.b[i];
  return c;
}
static bool closable(const Sig& s, int H) {
  return compCount(s, H) == 1 && s.b[H] && s.b[H + 1];
}

// ---------------- kink-carry cell-at-a-time sweep ----------------
//
// Mixed-state key reuses Sig's 32 bytes: b[0..H) mixed boundary, b[H]/b[H+1]
// the touch flags, b[H+2] carry label (0 = empty), b[H+3] placed-any bit.
// Canonicalization must relabel boundary AND carry together, so we run
// first-occurrence relabeling over b[0..H) then map the carry through it.

struct KinkStats {
  std::vector<u64> row;
  u64 transitions = 0;      // state expansions x choices actually taken
  u64 stageStateSum = 0;    // sum of live intermediate states over all stages
  size_t peakStates = 0;    // max intermediate map size
  size_t peakColStates = 0; // max end-of-column frontier
  double secs = 0;
};

static void canonMixed(Sig& s, int H) {
  unsigned char map[256] = {0};
  unsigned char next = 1;
  for (int i = 0; i < H; ++i) {
    const unsigned char v = s.b[i];
    if (v == 0) continue;
    if (map[v] == 0) map[v] = next++;
    s.b[i] = map[v];
  }
  const unsigned char c = s.b[H + 2];
  if (c != 0) {
    if (map[c] == 0) map[c] = next++;
    s.b[H + 2] = map[c];
  }
}

static bool labelInState(const Sig& s, int H, unsigned char L) {
  for (int i = 0; i < H; ++i)
    if (s.b[i] == L) return true;
  return s.b[H + 2] == L;
}

static KinkStats kinkSweep(int H, int maxn) {
  using DB = std::unordered_map<Sig, std::vector<u64>, SigHash>;
  KinkStats st;
  st.row.assign(maxn + 1, 0);
  const auto t0 = std::chrono::steady_clock::now();

  DB col, stage, nextStage;
  Sig seed;
  std::memset(seed.b, 0, SIGMAX);
  col[seed] = std::vector<u64>(maxn + 1, 0);
  col[seed][0] = 1;

  int uf[2 * SIGMAX];

  for (int c = 0; c <= maxn && !col.empty(); ++c) {
    if (col.size() > st.peakColStates) st.peakColStates = col.size();
    // Harvest closable states (production: at column start), then seed the
    // stage DP: kink at row 0, no carry yet, placed-any = 0.
    stage.clear();
    for (auto& [sig, counts] : col) {
      if (closable(sig, H))
        for (int n = 1; n <= maxn; ++n) st.row[n] += counts[n];
      Sig s = sig;
      s.b[H + 2] = 0;
      s.b[H + 3] = 0;
      auto& dst = stage[s];
      if (dst.empty()) dst.assign(maxn + 1, 0);
      for (int n = 0; n <= maxn; ++n) dst[n] += counts[n];
    }

    for (int r = 0; r < H; ++r) {
      if (stage.size() > st.peakStates) st.peakStates = stage.size();
      st.stageStateSum += stage.size();
      nextStage.clear();
      for (auto& [s, counts] : stage) {
        int ms = -1;
        for (int n = 0; n <= maxn; ++n)
          if (counts[n]) { ms = n; break; }
        if (ms < 0) continue;

        // Choice 1: leave (col, r) empty. Outgoing carry = old b[r-1] value
        // is s.b[H+2]; it is replaced by old b[r]... but b[r] must become the
        // new cell's value (0). Save old b[r] as the new carry, then check
        // the OUTGOING carry's component for stranding.
        for (int occupy = 0; occupy < 2; ++occupy) {
          if (occupy && ms + 1 > maxn) break;  // budget: cannot place
          Sig t = s;
          unsigned char newLabel = 0;
          if (occupy) {
            // Union-find over labels 1..H+? plus the new cell (slot 0).
            for (int i = 0; i < 2 * SIGMAX; ++i) uf[i] = i;
            auto uadd = [&](unsigned char L) {
              if (L) { int a=s8::find(uf,0), b=s8::find(uf,L); if(a!=b) uf[a]=b; }
            };
            if (r > 0) uadd(s.b[r - 1]);          // N (new column cell)
            uadd(s.b[r]);                          // W (old, pre-overwrite)
            uadd(s.b[H + 2]);                      // NW = carry
            if (r + 1 < H) uadd(s.b[r + 1]);       // SW (old)
            // Relabel: every label in the state that joins the new cell's
            // component gets one label; pick a fresh scratch label 200+.
            const int root = s8::find(uf, 0);
            unsigned char fresh = 200;
            for (int i = 0; i < H; ++i)
              if (t.b[i] && s8::find(uf, t.b[i]) == root) t.b[i] = fresh;
            if (t.b[H + 2] && s8::find(uf, t.b[H + 2]) == root)
              t.b[H + 2] = fresh;
            newLabel = fresh;
          }
          // Advance kink: outgoing carry = t.b[H+2] (already relabeled),
          // incoming carry = old value at row r (t.b[r] pre-overwrite).
          const unsigned char outgoing = t.b[H + 2];
          t.b[H + 2] = t.b[r];
          t.b[r] = occupy ? newLabel : 0;
          if (occupy) {
            if (r == 0) t.b[H] = 1;
            if (r == H - 1) t.b[H + 1] = 1;
            t.b[H + 3] = 1;
          }
          // Stranding: the outgoing carry's component is now unreachable if
          // its label appears nowhere else in the state.
          if (outgoing != 0 && !labelInState(t, H, outgoing)) continue;
          canonMixed(t, H);
          ++st.transitions;
          auto& dst = nextStage[t];
          if (dst.empty()) dst.assign(maxn + 1, 0);
          const int shift = occupy ? 1 : 0;
          for (int n = 0; n + shift <= maxn; ++n)
            if (counts[n]) dst[n + shift] += counts[n];
        }
      }
      std::swap(stage, nextStage);
    }

    // End of column: drop the final carry (old (col-1, H-1)) with the same
    // stranding check, require placed-any, prune, fold, store.
    col.clear();
    for (auto& [s, counts] : stage) {
      if (!s.b[H + 3]) continue;  // empty column = completion path, not extend
      const unsigned char outgoing = s.b[H + 2];
      Sig t = s;
      t.b[H + 2] = 0;
      t.b[H + 3] = 0;
      if (outgoing != 0 && !labelInState(t, H, outgoing)) continue;
      int ms = -1;
      for (int n = 0; n <= maxn; ++n)
        if (counts[n]) { ms = n; break; }
      if (ms < 0) continue;
      canonicalizeSig(t.b, H);
      if (ms + completionLowerBound(t.b, H) > maxn) continue;
      foldSig(t, H);
      auto& dst = col[t];
      if (dst.empty()) dst.assign(maxn + 1, 0);
      for (int n = 0; n <= maxn; ++n) dst[n] += counts[n];
    }
  }
  st.secs = std::chrono::duration<double>(std::chrono::steady_clock::now() - t0)
                .count();
  return st;
}

// ---------------- whole-column baseline (production semantics) ----------------

struct ColStats {
  std::vector<u64> row;
  u64 emitted = 0;
  size_t peakStates = 0;
  u64 stateColSum = 0;
  double secs = 0;
};

static ColStats columnSweep(int H, int maxn) {
  using DB = std::unordered_map<Sig, std::vector<u64>, SigHash>;
  ColStats st;
  st.row.assign(maxn + 1, 0);
  const auto t0 = std::chrono::steady_clock::now();
  DB db, next;
  Sig seed;
  std::memset(seed.b, 0, SIGMAX);
  db[seed] = std::vector<u64>(maxn + 1, 0);
  db[seed][0] = 1;
  for (int col = 0; col <= maxn && !db.empty(); ++col) {
    if (db.size() > st.peakStates) st.peakStates = db.size();
    st.stateColSum += db.size();
    next.clear();
    for (auto& [sig, counts] : db) {
      int ms = -1;
      for (int n = 0; n <= maxn; ++n)
        if (counts[n]) { ms = n; break; }
      if (ms < 0) continue;
      if (closable(sig, H))
        for (int n = 1; n <= maxn; ++n) st.row[n] += counts[n];
      forEachViableMask(sig, H, maxn - ms, [&](unsigned mask) {
        Sig out;
        if (stepColumnSquare8(sig, H, mask, out) != Outcome::Alive) return;
        const int cells = __builtin_popcount(static_cast<int>(mask));
        if (ms + cells + completionLowerBound(out.b, H) > maxn) return;
        foldSig(out, H);
        ++st.emitted;
        auto& dst = next[out];
        if (dst.empty()) dst.assign(maxn + 1, 0);
        for (int n = 0; n + cells <= maxn; ++n)
          if (counts[n]) dst[n + cells] += counts[n];
      });
    }
    std::swap(db, next);
  }
  st.secs = std::chrono::duration<double>(std::chrono::steady_clock::now() - t0)
                .count();
  return st;
}

int main(int argc, char** argv) {
  if (argc < 3) {
    std::fprintf(stderr, "usage: %s <H> <maxn> [--kink-only]\n", argv[0]);
    return 2;
  }
  const int H = std::atoi(argv[1]);
  const int maxn = std::atoi(argv[2]);

  if (argc > 3 && std::strcmp(argv[3], "--kink-only") == 0) {
    // No local baseline: gate externally against production per-height data
    // (results/ns_a2*/perheight/hH.out).
    KinkStats kink = kinkSweep(H, maxn);
    std::printf("H=%d maxn=%d kink-only\n", H, maxn);
    std::printf("kink-carry  : %10.3fs  transitions  %12llu  peak-interm %9zu  peak-col %9zu  stageStateSum %14llu\n",
                kink.secs, (unsigned long long)kink.transitions,
                kink.peakStates, kink.peakColStates,
                (unsigned long long)kink.stageStateSum);
    for (int n = 1; n <= maxn; ++n)
      std::printf("%d %llu\n", n, (unsigned long long)kink.row[n]);
    return 0;
  }

  ColStats base = columnSweep(H, maxn);
  KinkStats kink = kinkSweep(H, maxn);

  for (int n = 0; n <= maxn; ++n)
    if (base.row[n] != kink.row[n]) {
      std::fprintf(stderr, "COUNT MISMATCH n=%d: column=%llu kink=%llu\n", n,
                   (unsigned long long)base.row[n],
                   (unsigned long long)kink.row[n]);
      return 1;
    }
  std::fprintf(stderr, "counts identical (gate ok)\n");

  std::printf("H=%d maxn=%d\n", H, maxn);
  std::printf("whole-column: %10.3fs  kept-records %12llu  peak-states %9zu\n",
              base.secs, (unsigned long long)base.emitted, base.peakStates);
  std::printf("kink-carry  : %10.3fs  transitions  %12llu  peak-interm %9zu  peak-col %9zu  stageStateSum %14llu\n",
              kink.secs, (unsigned long long)kink.transitions, kink.peakStates,
              kink.peakColStates, (unsigned long long)kink.stageStateSum);
  std::printf("ratios      : time %.2fx   records/transitions %.2fx   interm/col-states %.2fx\n",
              base.secs / kink.secs,
              (double)base.emitted / (double)kink.transitions,
              (double)kink.peakStates / (double)base.peakStates);
  std::printf("Option-A merge volume (stageStateSum) vs whole-column single-barrier volume (kept-records): %.4fx\n",
              (double)kink.stageStateSum / (double)base.emitted);
  std::printf("T(n,%d):", H);
  for (int n = maxn - 2; n <= maxn; ++n)
    std::printf(" n=%d %llu", n, (unsigned long long)kink.row[n]);
  std::printf("\n");
  return 0;
}
