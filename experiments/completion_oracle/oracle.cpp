// FEASIBILITY PROBE -- NOT PRODUCTION. Thread: Shaving Lambda.
//
// Measures the HEADROOM of the completion-budget prune: how much frontier
// (states + emitted records) survives the current admissible bound
// (completionLowerBound: topReach + bottomReach + bandSum, vertical-only)
// that a PERFECT prune -- the true minimum number of additional cells any
// completion needs -- would kill. This is the ceiling for the Barequet-style
// n_c tightening flagged in results/completion-pruning-audit.md, measured
// before we invest in a deployable mechanism.
//
// Method:
//   Phase A  enumerate the full signature universe for height H (BFS closure
//            from the seed under all viable masks, fold-canonical keys).
//   Phase B  value-iterate dist[sig] = true min completion cost, using the
//            PRODUCTION kernel (stepColumnSquare8/forEachViableMask) as the
//            transition; dist=0 iff single component + both touch flags.
//            Cross-check: completionLowerBound <= dist everywhere (the
//            current bound's admissibility, exhaustively at this H), and
//            report the gap histogram.
//   Phase C  run the serial sweep twice at (H, maxn) -- once pruning with the
//            current bound, once pruning with dist -- and compare per-column
//            frontier states, total emitted records, and peak states. Final
//            per-n counts MUST match exactly (the prune-correctness gate of
//            the probe itself).
//
// The oracle prune is exact-safe by definition: a record is dropped only if
// (min cells so far + mask cells + dist(out)) > maxn, i.e. its smallest
// completable animal already overshoots the budget.
//
// Usage: oracle <H> <maxn>

#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <queue>
#include <unordered_map>
#include <vector>

#include "core/signature.h"
#include "core/transition.h"

using u64 = std::uint64_t;

struct SigHash {
  size_t operator()(const Sig& s) const {
    u64 h = 1469598103934665603ull;  // FNV-1a over the fixed 32 bytes
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

// ---------- Phase A+B: universe + exact min-completion distance ----------

struct Oracle {
  std::unordered_map<Sig, int, SigHash> idx;  // sig -> index
  std::vector<Sig> keys;
  std::vector<int> dist;
  int H;

  static constexpr int INF = 1 << 20;

  int lookup(const Sig& s) const {
    auto it = idx.find(s);
    return it == idx.end() ? INF : dist[it->second];
  }

  void build(int H_) {
    H = H_;
    // BFS closure from the seed under all viable masks (budget H: any column
    // content). Fold-canonical keys: dist(reflect(s)) == dist(s).
    Sig seed;
    std::memset(seed.b, 0, SIGMAX);
    std::queue<Sig> q;
    auto add = [&](Sig s) {
      foldSig(s, H);
      if (idx.emplace(s, static_cast<int>(keys.size())).second) {
        keys.push_back(s);
        q.push(s);
      }
    };
    add(seed);
    while (!q.empty()) {
      const Sig cur = q.front();
      q.pop();
      forEachViableMask(cur, H, H, [&](unsigned mask) {
        Sig out;
        if (stepColumnSquare8(cur, H, mask, out) != Outcome::Alive) return;
        add(out);
      });
    }
    std::fprintf(stderr, "H=%d universe=%zu signatures\n", H, keys.size());

    // Value iteration to the fixpoint. Costs are >=1 per relaxation and
    // bounded (~2H), so this converges in few rounds; each round re-derives
    // transitions with the production kernel (nothing cached, nothing new to
    // trust).
    dist.assign(keys.size(), INF);
    for (size_t i = 0; i < keys.size(); ++i)
      if (closable(keys[i], H)) dist[i] = 0;
    for (int round = 1;; ++round) {
      size_t changed = 0;
      for (size_t i = 0; i < keys.size(); ++i) {
        if (dist[i] == 0) continue;
        int best = dist[i];
        forEachViableMask(keys[i], H, H, [&](unsigned mask) {
          const int cells = __builtin_popcount(static_cast<int>(mask));
          if (cells >= best) return;  // can't improve
          Sig out;
          if (stepColumnSquare8(keys[i], H, mask, out) != Outcome::Alive)
            return;
          foldSig(out, H);
          const int d = lookup(out);
          if (d < INF && cells + d < best) best = cells + d;
        });
        if (best < dist[i]) { dist[i] = best; ++changed; }
      }
      std::fprintf(stderr, "  round %d: %zu improved\n", round, changed);
      if (changed == 0) break;
    }

    // Admissibility cross-check + gap histogram (bound vs truth).
    size_t unreachable = 0, violations = 0;
    std::vector<size_t> gapHist(2 * H + 2, 0);
    for (size_t i = 0; i < keys.size(); ++i) {
      if (dist[i] >= INF) { ++unreachable; continue; }
      const int lb = completionLowerBound(keys[i].b, H);
      if (lb > dist[i]) {
        ++violations;
        continue;
      }
      const int gap = dist[i] - lb;
      gapHist[gap < static_cast<int>(gapHist.size()) ? gap : gapHist.size() - 1]++;
    }
    std::fprintf(stderr,
                 "admissibility: %zu violations (MUST be 0), %zu uncompletable\n",
                 violations, unreachable);
    std::fprintf(stderr, "gap (dist - currentBound) histogram:\n");
    for (size_t g = 0; g < gapHist.size(); ++g)
      if (gapHist[g])
        std::fprintf(stderr, "  gap %2zu : %zu\n", g, gapHist[g]);
  }
};

// ---------- Phase C: measurement sweep, current bound vs oracle ----------

struct SweepStats {
  std::vector<u64> row;         // per-n completed counts
  std::vector<size_t> states;   // frontier size per column
  u64 emitted = 0;              // records kept post-prune, total
  size_t peak = 0;
  size_t stateColSum = 0;       // sum of frontier sizes over columns
};

static SweepStats sweep(int H, int maxn, const Oracle* oracle) {
  using DB = std::unordered_map<Sig, std::vector<u64>, SigHash>;
  DB db, next;
  SweepStats st;
  st.row.assign(maxn + 1, 0);
  Sig seed;
  std::memset(seed.b, 0, SIGMAX);
  db[seed] = std::vector<u64>(maxn + 1, 0);
  db[seed][0] = 1;

  for (int col = 0; col <= maxn && !db.empty(); ++col) {
    st.states.push_back(db.size());
    st.stateColSum += db.size();
    if (db.size() > st.peak) st.peak = db.size();
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
        if (oracle) {
          foldSig(out, H);
          if (ms + cells + oracle->lookup(out) > maxn) return;
        } else {
          if (ms + cells + completionLowerBound(out.b, H) > maxn) return;
          foldSig(out, H);
        }
        ++st.emitted;
        auto& dst = next[out];
        if (dst.empty()) dst.assign(maxn + 1, 0);
        for (int n = 0; n + cells <= maxn; ++n)
          if (counts[n]) dst[n + cells] += counts[n];
      });
    }
    std::swap(db, next);
  }
  return st;
}

int main(int argc, char** argv) {
  if (argc != 3) {
    std::fprintf(stderr, "usage: %s <H> <maxn>\n", argv[0]);
    return 2;
  }
  const int H = std::atoi(argv[1]);
  const int maxn = std::atoi(argv[2]);

  Oracle oracle;
  oracle.build(H);

  SweepStats cur = sweep(H, maxn, nullptr);
  SweepStats orc = sweep(H, maxn, &oracle);

  // Gate: identical per-n counts, or the probe itself is wrong.
  for (int n = 0; n <= maxn; ++n)
    if (cur.row[n] != orc.row[n]) {
      std::fprintf(stderr, "COUNT MISMATCH at n=%d: %llu vs %llu -- BUG\n", n,
                   (unsigned long long)cur.row[n],
                   (unsigned long long)orc.row[n]);
      return 1;
    }
  std::fprintf(stderr, "counts identical (gate ok)\n");

  std::printf("H=%d maxn=%d\n", H, maxn);
  std::printf("metric              current      oracle     ratio\n");
  std::printf("peak states     %10zu  %10zu  %8.3f\n", cur.peak, orc.peak,
              (double)cur.peak / (double)orc.peak);
  std::printf("state-cols sum  %10zu  %10zu  %8.3f\n", cur.stateColSum,
              orc.stateColSum, (double)cur.stateColSum / (double)orc.stateColSum);
  std::printf("records emitted %10llu  %10llu  %8.3f\n",
              (unsigned long long)cur.emitted, (unsigned long long)orc.emitted,
              (double)cur.emitted / (double)orc.emitted);
  std::printf("frontier by column (current / oracle):\n");
  for (size_t c = 0; c < cur.states.size() || c < orc.states.size(); ++c)
    std::printf("  col %2zu : %8zu / %8zu\n", c,
                c < cur.states.size() ? cur.states[c] : 0,
                c < orc.states.size() ? orc.states[c] : 0);
  return 0;
}
