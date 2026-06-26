// fanout_probe -- per-source-state FAN-OUT distribution of the king-polyplet
// (square-8 / A006770) column transfer matrix. Gates a work-stealing shard
// scheduler: is per-state map COST roughness heavy-tailed, or does it wash out
// at shard scale?
//
// FAN-OUT of a source boundary state = the number of viable next-column masks
// it emits: masks for which stepColumnSquare8 returns Alive AND survives the
// size-budget prune (ms + cells + completionLowerBound(out) <= maxn). This is
// EXACTLY the per-state successor-emission count the real engine (sweep8.h
// sweepSquare8Height inner loop) does -- the comps==1 closure harvest is NOT a
// successor (it emits no state), so it is not counted in fan-out.
//
// The transition body is the SAME code as the engine: forEachViableMask ->
// stepColumnSquare8 -> completionLowerBound prune, copied from sweep8.h (and
// matching experiments/bench_column.cpp's transitionColumn).
//
// Build:  g++ -std=c++20 -O3 -o build/fanout_probe experiments/fanout_probe.cpp
// Run:    build/fanout_probe square8 <maxn> --height <H>   [--validate <vmaxn>]
//   The probe builds the column sweep at (maxn, H), finds the HEAVIEST column,
//   and reports the fan-out distribution + shard cv for that column.
//   --validate vmaxn additionally runs the FULL multi-height sweep at vmaxn and
//   checks sum_H byHeight[H][n] == A006770(n) for a correctness gate (a(12)).

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>

#include "../cpp/tma/signature.h"
#include "../cpp/tma/statedb.h"
#include "../cpp/tma/transition_square8.h"

// Known A006770(n) (fixed king polyominoes / polyplets), n=0..14. Used for the
// correctness gate. a(0)=1 (empty), a(12)=257105146.
static const u64 A006770[] = {
    1ull, 1ull, 4ull, 20ull, 110ull, 638ull, 3832ull, 23592ull, 147941ull,
    940982ull, 6053180ull, 39299408ull, 257105146ull, 1696190565ull,
    11261573811ull};
static const int A006770_N = 14;

// ---- Engine transition body (verbatim from sweep8.h sweepSquare8Height) ------
// Advances one column: src FlatDB -> dst FlatDB, harvesting comps==1 closures.
static void transitionColumn(const FlatDB& src, FlatDB& dst, int H, int maxn,
                             Counts& harvest) {
  src.for_each([&](const Sig& sig, const u64* counts) {
    const int ms = minSizeRow(counts, maxn);
    if (ms < 0) return;
    int comps = 0;
    for (int j = 0; j < H; ++j)
      if (sig.b[j] > comps) comps = sig.b[j];
    if (comps == 1 && sig.b[H] && sig.b[H + 1])
      for (int n = 1; n <= maxn; ++n) harvest[n] += counts[n];
    forEachViableMask(sig, H, maxn - ms, [&](unsigned mask) {
      Sig out;
      if (stepColumnSquare8(sig, H, mask, out) != Outcome::Alive) return;
      const int cells = __builtin_popcount(mask);
      if (ms + cells + completionLowerBound(out.b, H) > maxn) return;
      addCounts(dst, out, counts, cells, maxn);
    });
  });
}

// Fan-out of ONE source state: the exact successor-emission count the engine
// would do (Alive AND size-budget survivor), per the same body above.
static u64 fanoutOfState(const Sig& sig, const u64* counts, int H, int maxn) {
  const int ms = minSizeRow(counts, maxn);
  if (ms < 0) return 0;
  u64 f = 0;
  forEachViableMask(sig, H, maxn - ms, [&](unsigned mask) {
    Sig out;
    if (stepColumnSquare8(sig, H, mask, out) != Outcome::Alive) return;
    const int cells = __builtin_popcount(mask);
    if (ms + cells + completionLowerBound(out.b, H) > maxn) return;
    ++f;
  });
  return f;
}

// Run the height-H sweep, return the FlatDB of the target column. If targetCol
// < 0, pick the heaviest column by state count; else stop at targetCol exactly.
// harvestRow optionally receives the per-size harvest (for validation).
// If profile != nullptr, fills it with per-column (states, total fan-out) so the
// caller can see where state-count and pruning-active load actually peak.
struct ColStat { size_t states; u64 totalFanout; };
static FlatDB buildColumn(int H, int maxn, int targetCol, int& chosenCol,
                          Counts* harvestRow, std::vector<ColStat>* profile) {
  Sig seed;
  std::memset(seed.b, 0, SIGMAX);

  // Pass 1: per-column state counts (and fan-out totals if profiling).
  std::vector<size_t> sizes;
  {
    FlatDB a(maxn), b(maxn);
    a.slot(seed)[0] = 1;
    Counts harvest(maxn + 1, 0);
    for (int col = 0; col <= maxn && !a.empty(); ++col) {
      sizes.push_back(a.size());
      if (profile) {
        u64 tf = 0;
        a.for_each([&](const Sig& sig, const u64* c) {
          tf += fanoutOfState(sig, c, H, maxn);
        });
        profile->push_back({a.size(), tf});
      }
      b.clear();
      transitionColumn(a, b, H, maxn, harvest);
      std::swap(a, b);
    }
    if (harvestRow) *harvestRow = harvest;
  }
  if (targetCol < 0) {
    chosenCol = 0;
    for (int c = 1; c < (int)sizes.size(); ++c)
      if (sizes[c] > sizes[chosenCol]) chosenCol = c;
  } else {
    chosenCol = targetCol;
  }

  // Pass 2: replay, stop AT chosenCol, return that source column.
  FlatDB db(maxn), next(maxn);
  db.slot(seed)[0] = 1;
  Counts harvest(maxn + 1, 0);
  for (int col = 0; col < chosenCol && !db.empty(); ++col) {
    next.clear();
    transitionColumn(db, next, H, maxn, harvest);
    std::swap(db, next);
  }
  return db;
}

// Full multi-height sweep -> totals[n], for the A006770 correctness gate.
static void fullSweepTotals(int maxn, std::vector<u64>& totals) {
  totals.assign(maxn + 1, 0);
  totals[0] = 1;  // empty animal (A006770 a(0)=1)
  for (int H = 1; H <= maxn; ++H) {
    int hc;
    Counts harvest;
    buildColumn(H, maxn, -1, hc, &harvest, nullptr);
    for (int n = 1; n <= maxn; ++n) totals[n] += harvest[n];
  }
}

static double pctile(const std::vector<u64>& s, double p) {  // s sorted asc
  if (s.empty()) return 0;
  double idx = p / 100.0 * (s.size() - 1);
  size_t lo = (size_t)idx;
  if (lo + 1 >= s.size()) return (double)s.back();
  double frac = idx - lo;
  return s[lo] * (1 - frac) + s[lo + 1] * frac;
}

int main(int argc, char** argv) {
  int maxn = 0, H = 0, validateN = 0, targetCol = -1;
  bool profile = false;
  std::string lattice;
  for (int i = 1; i < argc; ++i) {
    std::string a = argv[i];
    if (a == "square8") lattice = a;
    else if (a == "--height" && i + 1 < argc) H = std::atoi(argv[++i]);
    else if (a == "--validate" && i + 1 < argc) validateN = std::atoi(argv[++i]);
    else if (a == "--col" && i + 1 < argc) targetCol = std::atoi(argv[++i]);
    else if (a == "--profile") profile = true;
    else if (!a.empty() && a[0] >= '0' && a[0] <= '9') maxn = std::atoi(argv[i]);
    else { std::fprintf(stderr, "unknown arg: %s\n", a.c_str()); return 2; }
  }
  if (lattice != "square8" || maxn < 1 || H < 1) {
    std::fprintf(stderr,
                 "usage: %s square8 MAXN --height H [--validate VMAXN]\n", argv[0]);
    return 2;
  }

  // ---- correctness gate: full sweep at validateN must hit A006770 ----
  if (validateN > 0) {
    if (validateN > A006770_N) {
      std::fprintf(stderr, "no A006770 reference beyond n=%d\n", A006770_N);
      return 2;
    }
    std::vector<u64> totals;
    fullSweepTotals(validateN, totals);
    std::printf("=== CORRECTNESS GATE (full sweep, maxn=%d) ===\n", validateN);
    bool ok = true;
    for (int n = 0; n <= validateN; ++n) {
      bool match = totals[n] == A006770[n];
      ok &= match;
      std::printf("  a(%2d) = %15llu   ref %15llu   %s\n", n,
                  (unsigned long long)totals[n], (unsigned long long)A006770[n],
                  match ? "OK" : "MISMATCH");
    }
    std::printf("  => %s\n\n", ok ? "ALL MATCH (transition correct)"
                                  : "FAILED -- transition is WRONG");
    if (!ok) return 1;
  }

  // ---- build the target column at (maxn, H) ----
  int chosenCol;
  Counts harvest;
  std::vector<ColStat> colProfile;
  FlatDB col = buildColumn(H, maxn, targetCol, chosenCol, &harvest,
                           profile ? &colProfile : nullptr);
  if (profile) {
    std::printf("=== COLUMN PROFILE  square8  maxn=%d  H=%d ===\n", maxn, H);
    std::printf("%-5s %-12s %-16s %-12s\n", "col", "states", "total_fanout",
                "mean_fanout");
    for (int c = 0; c < (int)colProfile.size(); ++c)
      std::printf("%-5d %-12zu %-16llu %-12.2f\n", c, colProfile[c].states,
                  (unsigned long long)colProfile[c].totalFanout,
                  colProfile[c].states
                      ? (double)colProfile[c].totalFanout / colProfile[c].states
                      : 0.0);
    std::printf("\n");
  }
  std::printf("=== FAN-OUT DISTRIBUTION  square8  maxn=%d  H=%d ===\n", maxn, H);
  std::printf("%s column = col %d  (%zu source states)\n",
              targetCol < 0 ? "heaviest" : "selected", chosenCol, col.size());
  std::printf("height H => 2^H ceiling on masks = %llu\n\n",
              (unsigned long long)(1ull << H));

  // ---- per-state fan-out, in for_each (slot) order = the engine's shard order ----
  std::vector<u64> fan;
  fan.reserve(col.size());
  col.for_each([&](const Sig& sig, const u64* counts) {
    fan.push_back(fanoutOfState(sig, counts, H, maxn));
  });

  const size_t N = fan.size();
  // distribution stats (on a sorted copy; shard stats use the original order)
  std::vector<u64> sorted = fan;
  std::sort(sorted.begin(), sorted.end());

  u64 sum = 0, mn = sorted.front(), mx = sorted.back();
  for (u64 v : sorted) sum += v;
  double mean = (double)sum / N;
  double var = 0;
  for (u64 v : sorted) { double d = v - mean; var += d * d; }
  var /= N;
  double sd = std::sqrt(var);
  double median = pctile(sorted, 50);

  // top-X% share of total fan-out (sorted ascending => take from the high end)
  auto topShare = [&](double pct) -> double {
    size_t k = (size_t)std::ceil(pct / 100.0 * N);
    if (k < 1) k = 1;
    u64 s = 0;
    for (size_t i = N - k; i < N; ++i) s += sorted[i];
    return sum ? (double)s / sum : 0;
  };

  std::printf("n_states            %zu\n", N);
  std::printf("total fan-out (sum) %llu\n", (unsigned long long)sum);
  std::printf("mean                %.3f\n", mean);
  std::printf("median (p50)        %.1f\n", median);
  std::printf("min                 %llu\n", (unsigned long long)mn);
  std::printf("max                 %llu\n", (unsigned long long)mx);
  std::printf("stddev (sigma)      %.3f\n", sd);
  std::printf("cv (sigma/mu)       %.3f\n", mean ? sd / mean : 0);
  std::printf("p90                 %.1f\n", pctile(sorted, 90));
  std::printf("p99                 %.1f\n", pctile(sorted, 99));
  std::printf("p99.9               %.1f\n", pctile(sorted, 99.9));
  std::printf("max                 %llu\n", (unsigned long long)mx);
  std::printf("max/median ratio    %.2fx\n", median ? mx / median : 0);
  std::printf("top 1%%   share of total fan-out   %.2f%%\n", 100 * topShare(1.0));
  std::printf("top 0.1%% share of total fan-out   %.2f%%\n", 100 * topShare(0.1));
  std::printf("max fan-out %llu  vs 2^H ceiling %llu  => max is %.4f%% of ceiling\n",
              (unsigned long long)mx, (unsigned long long)(1ull << H),
              100.0 * mx / (double)(1ull << H));

  // ---- shard-level: contiguous shards of size S in for_each order ----
  std::printf("\n--- SHARD-LEVEL (contiguous shards, for_each order) ---\n");
  std::printf("%-10s %-8s %-14s %-12s %-12s %-10s %s\n", "shard_S",
              "nshards", "mean_total", "sd_total", "cv", "max_total",
              "max1state/mean_total");
  for (size_t S : {(size_t)1000, (size_t)10000, (size_t)100000}) {
    if (S > N) continue;
    std::vector<double> shardTot;
    for (size_t i = 0; i < N; i += S) {
      size_t e = std::min(i + S, N);
      // only full-ish shards: include the trailing partial too (it is a real shard)
      u64 t = 0;
      for (size_t j = i; j < e; ++j) t += fan[j];
      shardTot.push_back((double)t);
    }
    double smean = 0;
    for (double t : shardTot) smean += t;
    smean /= shardTot.size();
    double svar = 0, smax = 0;
    for (double t : shardTot) { double d = t - smean; svar += d * d; if (t > smax) smax = t; }
    svar /= shardTot.size();
    double ssd = std::sqrt(svar);
    std::printf("%-10zu %-8zu %-14.1f %-12.1f %-12.4f %-10.0f %.4f\n", S,
                shardTot.size(), smean, ssd, smean ? ssd / smean : 0, smax,
                smean ? (double)mx / smean : 0);
  }

  return 0;
}
