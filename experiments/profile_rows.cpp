// Standalone count-row width profiler (the queued --profile-rows measurement,
// state-store-compression.md §"The measurement", frontier-revision-plan §0.2).
//
// Replicates the serial square-8 per-column sweep but, instead of (only) summing
// counts, histograms each live state's count-row WIDTH (hi-lo+1, the span of
// nonzero sizes) weighted by state count, per column and at the peak column. The
// ranged-row payoff is (maxn / mean-width). Validates the height row's a(n)
// contribution by summing over all heights and comparing to A006770.
//
// Usage: tma_profile_rows MAXN [H]
//   no H  -> sweep all heights, print totals (validate a(n)) + global width stats
//   H     -> just height H, print per-column width table + peak-column histogram

#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>

#include "tma/signature.h"
#include "tma/statedb.h"
#include "tma/transition_square8.h"

// hi index of a flat counts row (largest n with c[n] != 0), or -1 if empty.
static int maxSizeRow(const u64* c, int maxn) {
  for (int n = maxn; n >= 1; --n)
    if (c[n]) return n;
  return c[0] ? 0 : -1;
}

struct WidthStat {
  double sumWidthWeighted = 0;  // sum over states of width * (#animals? no: per STATE)
  u64 nStates = 0;
  int maxWidth = 0;
  std::vector<u64> hist;  // hist[w] = # states with width w
  explicit WidthStat(int maxn) : hist(maxn + 2, 0) {}
  void add(int width) {
    sumWidthWeighted += width;
    ++nStates;
    if (width > maxWidth) maxWidth = width;
    hist[width]++;
  }
};

// Sweep one height; if collectPeak, record the per-state width histogram at the
// column with the most live states (the RAM peak). Returns the byHeight row.
static Counts profileHeight(int H, int maxn, bool perColumn, WidthStat* peakStat,
                            u64* peakStatesOut) {
  Counts row(maxn + 1, 0);
  FlatDB db(maxn), next(maxn);
  Sig seed;
  std::memset(seed.b, 0, SIGMAX);
  db.slot(seed)[0] = 1;

  u64 peakStates = 0;
  int peakCol = -1;
  // First pass tracking: we don't know the peak column until we hit it; so do a
  // simple online approach -- recompute the histogram only when a new peak column
  // is seen. Since live-state count rises then falls, the peak is one column; we
  // snapshot the histogram of the db AT THE START of each column and keep the one
  // whose size is largest.
  for (int col = 0; col <= maxn && !db.empty(); ++col) {
    const u64 live = db.size();
    if (live > peakStates) { peakStates = live; peakCol = col; }

    if (perColumn || peakStat) {
      // compute width stats of the current column's live states
      WidthStat ws(maxn);
      db.for_each([&](const Sig&, const u64* counts) {
        const int lo = minSizeRow(counts, maxn);
        if (lo < 0) return;  // empty (shouldn't happen for live)
        const int hi = maxSizeRow(counts, maxn);
        ws.add(hi - lo + 1);
      });
      if (perColumn)
        std::printf("col=%2d states=%llu mean_width=%.3f max_width=%d (maxn=%d)\n",
                    col, (unsigned long long)live,
                    ws.nStates ? ws.sumWidthWeighted / ws.nStates : 0.0,
                    ws.maxWidth, maxn);
      if (peakStat && live >= peakStates) *peakStat = ws;  // keep histogram at peak col
    }

    next.clear();
    db.for_each([&](const Sig& sig, const u64* counts) {
      const int ms = minSizeRow(counts, maxn);
      if (ms < 0) return;
      int comps = 0;
      for (int j = 0; j < H; ++j)
        if (sig.b[j] > comps) comps = sig.b[j];
      if (comps == 1 && sig.b[H] && sig.b[H + 1])
        for (int n = 1; n <= maxn; ++n) row[n] += counts[n];
      forEachViableMask(sig, H, maxn - ms, [&](unsigned mask) {
        Sig out;
        if (stepColumnSquare8(sig, H, mask, out) != Outcome::Alive) return;
        const int cells = __builtin_popcount(mask);
        if (ms + cells + completionLowerBound(out.b, H) > maxn) return;
        addCounts(next, out, counts, cells, maxn);
      });
    });
    std::swap(db, next);
  }
  if (peakStatesOut) *peakStatesOut = peakStates;
  (void)peakCol;
  return row;
}

int main(int argc, char** argv) {
  if (argc < 2) { std::fprintf(stderr, "usage: %s MAXN [H]\n", argv[0]); return 2; }
  const int maxn = std::atoi(argv[1]);
  const int onlyH = argc >= 3 ? std::atoi(argv[2]) : 0;

  if (onlyH > 0) {
    WidthStat peak(maxn);
    u64 peakStates = 0;
    Counts row = profileHeight(onlyH, maxn, /*perColumn=*/true, &peak, &peakStates);
    std::printf("\n=== height %d, maxn %d ===\n", onlyH, maxn);
    std::printf("peak_states=%llu  a(%d)-contribution row[maxn]=%llu\n",
                (unsigned long long)peakStates, maxn, (unsigned long long)row[maxn]);
    std::printf("PEAK COLUMN width histogram (width: #states):\n");
    double sw = 0; u64 ns = 0;
    for (int w = 1; w <= maxn + 1; ++w)
      if (peak.hist[w]) {
        std::printf("  w=%2d : %llu\n", w, (unsigned long long)peak.hist[w]);
        sw += (double)w * peak.hist[w]; ns += peak.hist[w];
      }
    const double mean = ns ? sw / ns : 0;
    std::printf("peak-col mean_width=%.3f max_width=%d maxn=%d  =>  ranged payoff (maxn+1)/mean = %.2fx\n",
                mean, peak.maxWidth, maxn, mean > 0 ? (maxn + 1) / mean : 0.0);
    return 0;
  }

  // all heights: validate a(n) and aggregate a state-weighted width mean across
  // every (height, peak-column) -- the realistic ranged factor for the whole run.
  std::vector<u64> totals(maxn + 1, 0);
  double globSumWidth = 0; u64 globStates = 0; int globMax = 0;
  u64 grandPeak = 0; int grandPeakH = 0; double grandPeakMean = 0; int grandPeakMaxW = 0;
  for (int H = 1; H <= maxn; ++H) {
    WidthStat peak(maxn);
    u64 peakStates = 0;
    Counts row = profileHeight(H, maxn, /*perColumn=*/false, &peak, &peakStates);
    for (int n = 1; n <= maxn; ++n) totals[n] += row[n];
    double sw = 0; u64 ns = 0;
    for (int w = 1; w <= maxn + 1; ++w) { sw += (double)w * peak.hist[w]; ns += peak.hist[w]; }
    globSumWidth += sw; globStates += ns;
    if (peak.maxWidth > globMax) globMax = peak.maxWidth;
    const double mean = ns ? sw / ns : 0;
    std::printf("H=%2d peak_states=%llu peakcol_mean_width=%.3f max_width=%d\n",
                H, (unsigned long long)peakStates, mean, peak.maxWidth);
    if (peakStates > grandPeak) {
      grandPeak = peakStates; grandPeakH = H; grandPeakMean = mean; grandPeakMaxW = peak.maxWidth;
    }
  }
  std::printf("\n=== totals (validate vs A006770) ===\n");
  for (int n = 1; n <= maxn; ++n)
    std::printf("a(%d) = %llu\n", n, (unsigned long long)totals[n]);
  const double gmean = globStates ? globSumWidth / globStates : 0;
  std::printf("\n=== GLOBAL state-weighted (over all per-height peak columns) ===\n");
  std::printf("mean_width=%.3f max_width=%d maxn=%d  => ranged payoff (maxn+1)/mean = %.2fx\n",
              gmean, globMax, maxn, gmean > 0 ? (maxn + 1) / gmean : 0.0);
  std::printf("RAM-DOMINANT height H=%d (peak_states=%llu): peakcol mean_width=%.3f max_width=%d => payoff %.2fx\n",
              grandPeakH, (unsigned long long)grandPeak, grandPeakMean, grandPeakMaxW,
              grandPeakMean > 0 ? (maxn + 1) / grandPeakMean : 0.0);
  return 0;
}
