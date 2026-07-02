// FEASIBILITY PROBE -- NOT PRODUCTION. Design 14 Phase 0.1: duplication curve.
//
// Design 14 (docs/next-system/designs/14-kink-carry-parallel-engine.md)
// proposes Option B: shard the SOURCE frontier by key (as production does
// today), run the private per-shard kink stage-DP independently, merge only
// end-of-column states. Intermediate mixed-boundary states that would have
// merged mid-column across shards instead duplicate. This probe measures
// that duplication as a function of shard count S, and the go/no-go gate:
// duplication factor at production shard counts (~cores*unit_mult).
//
// Method: at each column, partition source states into S shards by
// hash(sig) % S (stand-in for production's key-range partitioning -- same
// asymptotic behavior for a well-mixed hash, and avoids needing a real
// sorted-key-range cut here). Run the IDENTICAL stage-DP logic on each
// shard independently (shared code with the unsharded run -- no drift), sum
// end-of-column contributions into the next column's frontier (this must
// exactly equal the unsharded next column -- the correctness gate), and
// separately accumulate the sharded run's total/peak intermediate-state
// counts for comparison against the unsharded run's.
//
// Usage: kink_shard_probe <H> <maxn> <S1> [<S2> ...]

#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <algorithm>
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

static bool closable(const Sig& s, int H) {
  int c = 0;
  for (int i = 0; i < H; ++i)
    if (s.b[i] > c) c = s.b[i];
  return c == 1 && s.b[H] && s.b[H + 1];
}

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

using DB = std::unordered_map<Sig, std::vector<u64>, SigHash>;

// Shard hash for a source sig -- same key that would order a real sorted
// key-range cut (sigCmp order isn't needed here, only a stable partition of
// roughly-equal-mass shards, which hash % S gives on a well-mixed key).
static unsigned shardOf(const Sig& s, int keyLen, unsigned S) {
  u64 h = 1469598103934665603ull;
  for (int i = 0; i < keyLen; ++i) { h ^= s.b[i]; h *= 1099511628211ull; }
  return static_cast<unsigned>(h % S);
}

// Runs the full H-stage kink DP on ONE shard's source states, folding its
// end-of-column contributions into `outCol`. Accumulates this shard's
// intermediate-state footprint into `stageSizeSum` (sum over all H stages)
// and `stagePeak` (this shard's own peak stage size) -- the two numbers
// Phase 0.1 needs. `transitions` counts state expansions (informational).
static void runShardStageDP(const DB& src, int H, int maxn, DB& outCol,
                             u64& stageSizeSum, size_t& stagePeak,
                             u64& transitions) {
  DB stage, nextStage;
  int uf[2 * SIGMAX];
  stage.clear();
  for (auto& [sig, counts] : src) {
    Sig s = sig;
    s.b[H + 2] = 0;
    s.b[H + 3] = 0;
    auto& dst = stage[s];
    if (dst.empty()) dst.assign(maxn + 1, 0);
    for (int n = 0; n <= maxn; ++n) dst[n] += counts[n];
  }

  for (int r = 0; r < H; ++r) {
    stageSizeSum += stage.size();
    if (stage.size() > stagePeak) stagePeak = stage.size();
    nextStage.clear();
    for (auto& [s, counts] : stage) {
      int ms = -1;
      for (int n = 0; n <= maxn; ++n)
        if (counts[n]) { ms = n; break; }
      if (ms < 0) continue;

      for (int occupy = 0; occupy < 2; ++occupy) {
        if (occupy && ms + 1 > maxn) break;
        Sig t = s;
        unsigned char newLabel = 0;
        if (occupy) {
          for (int i = 0; i < 2 * SIGMAX; ++i) uf[i] = i;
          auto uadd = [&](unsigned char L) {
            if (L) { int a = s8::find(uf, 0), b = s8::find(uf, L); if (a != b) uf[a] = b; }
          };
          if (r > 0) uadd(s.b[r - 1]);
          uadd(s.b[r]);
          uadd(s.b[H + 2]);
          if (r + 1 < H) uadd(s.b[r + 1]);
          const int root = s8::find(uf, 0);
          unsigned char fresh = 200;
          for (int i = 0; i < H; ++i)
            if (t.b[i] && s8::find(uf, t.b[i]) == root) t.b[i] = fresh;
          if (t.b[H + 2] && s8::find(uf, t.b[H + 2]) == root)
            t.b[H + 2] = fresh;
          newLabel = fresh;
        }
        const unsigned char outgoing = t.b[H + 2];
        t.b[H + 2] = t.b[r];
        t.b[r] = occupy ? newLabel : 0;
        if (occupy) {
          if (r == 0) t.b[H] = 1;
          if (r == H - 1) t.b[H + 1] = 1;
          t.b[H + 3] = 1;
        }
        if (outgoing != 0 && !labelInState(t, H, outgoing)) continue;
        canonMixed(t, H);
        ++transitions;
        auto& dst = nextStage[t];
        if (dst.empty()) dst.assign(maxn + 1, 0);
        const int shift = occupy ? 1 : 0;
        for (int n = 0; n + shift <= maxn; ++n)
          if (counts[n]) dst[n + shift] += counts[n];
      }
    }
    std::swap(stage, nextStage);
  }

  for (auto& [s, counts] : stage) {
    if (!s.b[H + 3]) continue;
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
    auto& dst = outCol[t];
    if (dst.empty()) dst.assign(maxn + 1, 0);
    for (int n = 0; n <= maxn; ++n) dst[n] += counts[n];
  }
}

struct RunResult {
  std::vector<u64> row;
  u64 stageSizeSum = 0;      // sum over columns, over stages, over shards
  size_t peakShardStage = 0; // max single-shard stage size, over the whole run
  u64 transitions = 0;
  double secs = 0;
};

// S=1 is the unsharded baseline (same code path, shard count 1).
static RunResult run(int H, int maxn, unsigned S, bool keyRange) {
  RunResult res;
  res.row.assign(maxn + 1, 0);
  const auto t0 = std::chrono::steady_clock::now();

  DB col;
  Sig seed;
  std::memset(seed.b, 0, SIGMAX);
  col[seed] = std::vector<u64>(maxn + 1, 0);
  col[seed][0] = 1;

  const int keyLen = H + 2;  // shard on the canonical end-of-column key

  for (int c = 0; c <= maxn && !col.empty(); ++c) {
    for (auto& [sig, counts] : col)
      if (closable(sig, H))
        for (int n = 1; n <= maxn; ++n) res.row[n] += counts[n];

    std::vector<DB> shards(S);
    if (keyRange) {
      // Faithful to production: sort by key, cut into S contiguous ranges of
      // (nearly) equal record count -- not a hash scatter.
      std::vector<std::pair<Sig, std::vector<u64>>> sorted(col.begin(), col.end());
      std::sort(sorted.begin(), sorted.end(), [&](const auto& a, const auto& b) {
        return sigCmp(a.first.b, b.first.b, keyLen) < 0;
      });
      const size_t n = sorted.size();
      for (size_t i = 0; i < n; ++i) {
        const unsigned sh = static_cast<unsigned>(i * S / n);
        shards[sh][sorted[i].first] = sorted[i].second;
      }
    } else {
      for (auto& [sig, counts] : col)
        shards[shardOf(sig, keyLen, S)][sig] = counts;
    }

    DB nextCol;
    for (unsigned sh = 0; sh < S; ++sh) {
      if (shards[sh].empty()) continue;
      runShardStageDP(shards[sh], H, maxn, nextCol, res.stageSizeSum,
                       res.peakShardStage, res.transitions);
    }
    std::swap(col, nextCol);
  }
  res.secs = std::chrono::duration<double>(std::chrono::steady_clock::now() - t0)
                 .count();
  return res;
}

int main(int argc, char** argv) {
  if (argc < 4) {
    std::fprintf(stderr, "usage: %s <H> <maxn> [--hash|--keyrange] <S1> [<S2> ...]\n", argv[0]);
    return 2;
  }
  const int H = std::atoi(argv[1]);
  const int maxn = std::atoi(argv[2]);
  int argStart = 3;
  bool keyRange = true;
  if (argc > 3 && std::strcmp(argv[3], "--hash") == 0) { keyRange = false; argStart = 4; }
  else if (argc > 3 && std::strcmp(argv[3], "--keyrange") == 0) { keyRange = true; argStart = 4; }

  RunResult base = run(H, maxn, 1, keyRange);
  std::printf("H=%d maxn=%d  S=1 (baseline): stageSizeSum=%llu peakShardStage=%zu transitions=%llu secs=%.3f\n",
              H, maxn, (unsigned long long)base.stageSizeSum, base.peakShardStage,
              (unsigned long long)base.transitions, base.secs);

  for (int a = argStart; a < argc; ++a) {
    const unsigned S = static_cast<unsigned>(std::atoi(argv[a]));
    RunResult r = run(H, maxn, S, keyRange);
    bool ok = true;
    for (int n = 0; n <= maxn; ++n)
      if (r.row[n] != base.row[n]) { ok = false; break; }
    std::printf("S=%3u: stageSizeSum=%12llu (%.3fx dup)  peakShardStage=%9zu (%.3fx of baseline-shard-count-scaled)  transitions=%12llu (%.3fx)  secs=%.3f (%.3fx)  gate=%s\n",
                S, (unsigned long long)r.stageSizeSum,
                (double)r.stageSizeSum / (double)base.stageSizeSum,
                r.peakShardStage,
                (double)r.peakShardStage / ((double)base.peakShardStage / S),
                (unsigned long long)r.transitions,
                (double)r.transitions / (double)base.transitions,
                r.secs, r.secs / base.secs,
                ok ? "PASS" : "FAIL-COUNT-MISMATCH");
    if (!ok) return 1;
  }
  return 0;
}
