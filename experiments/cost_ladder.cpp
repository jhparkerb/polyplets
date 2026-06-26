// cost_ladder -- H-LADDER of the per-state map-COST distribution for the
// king-polyplet (square-8 / A006770) column transfer matrix. Successor to
// experiments/fanout_probe.cpp. Gates a work-stealing shard scheduler for the
// long-pole (high-H, one dominant height) regime: does the per-state cost
// TAIL worsen as the frontier height H grows toward production (H=21-25)?
//
// THREE refinements over fanout_probe.cpp:
//  (1) COST = masks EXAMINED (every stepColumnSquare8 call -- the real
//      mask-enumeration work, exponential in H), reported ALONGSIDE
//      successors-PASSED (Alive + budget survivors = fan-out). The gap is the
//      pruned-but-still-enumerated work that the fan-out metric missed.
//  (2) H-LADDER: H = 8, 11, 14, 17 (overridable). At each H we pick a maxn so
//      the representative columns run in seconds-to-minutes, then sample
//      SEVERAL pruning-active mid-to-late columns (where the roughness lives).
//  (3) KEY-RANGE shards: sort the column's states by canonical signature (the
//      sort engine's shard key) and form contiguous shards, vs random-order
//      shards. If cost correlates with the sig, key-range shards balance WORSE.
//
// Transition body is the SAME engine code (forEachViableMask ->
// stepColumnSquare8 -> completionLowerBound prune) as sweep8.h, validated
// Sum_H byHeight[H][n] == A006770(n).
//
// Build: g++ -std=c++20 -O3 -o build/cost_ladder experiments/cost_ladder.cpp
// Run:   build/cost_ladder square8 --ladder "8:13 11:16 14:18 17:20"
//        (each entry H:maxn; the H-ladder of cost trend metrics is the output)

#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <random>
#include <string>
#include <vector>

#include "../cpp/tma/signature.h"
#include "../cpp/tma/statedb.h"
#include "../cpp/tma/transition_square8.h"

static const u64 A006770[] = {
    1ull, 1ull, 4ull, 20ull, 110ull, 638ull, 3832ull, 23592ull, 147941ull,
    940982ull, 6053180ull, 39299408ull, 257105146ull, 1696190565ull,
    11261573811ull};
static const int A006770_N = 14;

// R1 fold toggle. When true the sweep stores orbit-canonical (vertical-mirror)
// signatures -- exactly what the production engine does (sweep8.h fold path) and
// what keeps state counts ~2x lower so high-H slack-1 sweeps fit a 24 GB box.
// Byte-identical totals (signature.h foldSig). Per-state COST is unaffected
// (fold only changes WHICH boundary reps exist, not a state's mask enumeration).
static bool g_fold = false;

// ---- engine transition body (verbatim from sweep8.h, +optional R1 fold) ----
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
      if (g_fold) foldSig(out, H);
      addCounts(dst, out, counts, cells, maxn);
    });
  });
}

// Per-state COST: masks EXAMINED = every stepColumnSquare8 call (the real
// mask-enumeration work, whatever its Alive/Dead/pruned outcome), and
// successors PASSED = Alive + budget-survivors (the fan-out the engine emits).
struct StateCost { u64 examined; u64 passed; };
static StateCost costOfState(const Sig& sig, const u64* counts, int H, int maxn) {
  const int ms = minSizeRow(counts, maxn);
  StateCost c{0, 0};
  if (ms < 0) return c;
  forEachViableMask(sig, H, maxn - ms, [&](unsigned mask) {
    ++c.examined;  // every enumerated mask costs a step call
    Sig out;
    if (stepColumnSquare8(sig, H, mask, out) != Outcome::Alive) return;
    const int cells = __builtin_popcount(mask);
    if (ms + cells + completionLowerBound(out.b, H) > maxn) return;
    ++c.passed;
  });
  return c;
}

// Pass 1: per-column STATE COUNTS only (cheap, no snapshots). Returns sizes;
// fills harvestRow for validation. Memory-light: only two live columns at once.
static std::vector<size_t> columnSizes(int H, int maxn, Counts* harvestRow) {
  Sig seed;
  std::memset(seed.b, 0, SIGMAX);
  std::vector<size_t> sizes;
  FlatDB a(maxn), b(maxn);
  a.slot(seed)[0] = 1;
  Counts harvest(maxn + 1, 0);
  for (int col = 0; col <= maxn && !a.empty(); ++col) {
    sizes.push_back(a.size());
    b.clear();
    transitionColumn(a, b, H, maxn, harvest);
    std::swap(a, b);
  }
  if (harvestRow) *harvestRow = harvest;
  return sizes;
}

// Pass 2: replay forward, snapshotting ONLY the requested target columns (the
// few mid-to-late ones we analyze). Early/huge columns are advanced and freed,
// never retained -- this is what keeps a 24 GB box safe at high maxn. `targets`
// must be sorted ascending. Returns one FlatDB per target (same order).
static std::vector<FlatDB> snapshotColumns(int H, int maxn,
                                           const std::vector<int>& targets) {
  Sig seed;
  std::memset(seed.b, 0, SIGMAX);
  std::vector<FlatDB> out;
  out.reserve(targets.size());
  FlatDB a(maxn), b(maxn);
  a.slot(seed)[0] = 1;
  Counts harvest(maxn + 1, 0);
  size_t ti = 0;
  for (int col = 0; col <= maxn && !a.empty(); ++col) {
    if (ti < targets.size() && col == targets[ti]) {
      FlatDB snap(maxn);
      a.for_each([&](const Sig& s, const u64* c) {
        std::memcpy(snap.slot(s), c, (size_t)(maxn + 1) * sizeof(u64));
      });
      out.push_back(std::move(snap));
      ++ti;
    }
    if (ti >= targets.size()) break;  // past the last target -> done
    b.clear();
    transitionColumn(a, b, H, maxn, harvest);
    std::swap(a, b);
  }
  return out;
}

static void fullSweepTotals(int maxn, std::vector<u64>& totals) {
  totals.assign(maxn + 1, 0);
  totals[0] = 1;
  for (int H = 1; H <= maxn; ++H) {
    Counts harvest;
    columnSizes(H, maxn, &harvest);
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

// per-column cost analysis result -- the row of trend metrics
struct ColReport {
  int col;
  size_t nstates;
  u64 sumExam, sumPass, maxExam, maxPass;
  double meanExam, medianExam;
  double maxOverMedian;        // tail roughness
  double monsterFrac1k;        // max single-state cost / mean 1k-shard cost
  double top1pct, top01pct;    // share of total cost
  double maxOverCeil;          // max examined / 2^H
  double cvKey1k, cvRand1k;    // per-shard cv, key-range vs random, S=1k
  double cvKey10k, cvRand10k;
  double wallUsPerState;       // sampled per-state wall (sanity)
};

// shard cv over a cost vector in a GIVEN order, shard size S
static double shardCv(const std::vector<u64>& cost, size_t S) {
  if (cost.empty()) return 0;
  std::vector<double> tot;
  for (size_t i = 0; i < cost.size(); i += S) {
    size_t e = std::min(i + S, cost.size());
    u64 t = 0;
    for (size_t j = i; j < e; ++j) t += cost[j];
    tot.push_back((double)t);
  }
  double m = 0;
  for (double t : tot) m += t;
  m /= tot.size();
  double v = 0;
  for (double t : tot) { double d = t - m; v += d * d; }
  v /= tot.size();
  return m ? std::sqrt(v) / m : 0;
}

static ColReport analyzeColumn(const FlatDB& col, int colIdx, int H, int maxn) {
  ColReport r{};
  r.col = colIdx;
  r.nstates = col.size();

  // Collect (sig, examined, passed) in for_each order; also keep sig keys so we
  // can sort by canonical signature for key-range sharding.
  std::vector<Sig> sigs;
  std::vector<u64> exam, pass;
  sigs.reserve(col.size());
  exam.reserve(col.size());
  pass.reserve(col.size());

  // sampled per-state wall: time the whole pass, divide by nstates
  auto t0 = std::chrono::steady_clock::now();
  col.for_each([&](const Sig& sig, const u64* counts) {
    StateCost c = costOfState(sig, counts, H, maxn);
    sigs.push_back(sig);
    exam.push_back(c.examined);
    pass.push_back(c.passed);
  });
  auto t1 = std::chrono::steady_clock::now();
  double wallUs = std::chrono::duration_cast<std::chrono::duration<double, std::micro>>(t1 - t0).count();
  r.wallUsPerState = col.size() ? wallUs / col.size() : 0;

  const size_t N = exam.size();
  if (N == 0) return r;

  std::vector<u64> se = exam;  // sorted examined (cost)
  std::sort(se.begin(), se.end());
  r.sumExam = 0; for (u64 v : exam) r.sumExam += v;
  r.sumPass = 0; for (u64 v : pass) r.sumPass += v;
  r.maxExam = se.back();
  r.maxPass = *std::max_element(pass.begin(), pass.end());
  r.meanExam = (double)r.sumExam / N;
  r.medianExam = pctile(se, 50);
  r.maxOverMedian = r.medianExam > 0 ? r.maxExam / r.medianExam : 0;

  // monster fraction = max single-state cost / mean 1k-shard total cost.
  // mean 1k-shard total = mean_state * min(1000, N).
  double shardStates1k = std::min((size_t)1000, N);
  double meanShard1k = r.meanExam * shardStates1k;
  r.monsterFrac1k = meanShard1k > 0 ? r.maxExam / meanShard1k : 0;

  auto topShare = [&](double pct) -> double {
    size_t k = (size_t)std::ceil(pct / 100.0 * N);
    if (k < 1) k = 1;
    u64 s = 0;
    for (size_t i = N - k; i < N; ++i) s += se[i];
    return r.sumExam ? (double)s / r.sumExam : 0;
  };
  r.top1pct = topShare(1.0);
  r.top01pct = topShare(0.1);
  r.maxOverCeil = (double)r.maxExam / (double)(1ull << H);

  // ---- KEY-RANGE shards: order states by canonical signature, contiguous shards ----
  // The sort engine shards by sorted-by-sig key ranges. Build cost in sig order.
  std::vector<size_t> idx(N);
  for (size_t i = 0; i < N; ++i) idx[i] = i;
  std::sort(idx.begin(), idx.end(), [&](size_t a, size_t b) {
    return std::memcmp(sigs[a].b, sigs[b].b, SIGMAX) < 0;
  });
  std::vector<u64> costKey(N);
  for (size_t i = 0; i < N; ++i) costKey[i] = exam[idx[i]];

  // random-order cost (fixed seed for reproducibility)
  std::vector<u64> costRand = exam;
  std::mt19937_64 rng(0xC051A77E);
  std::shuffle(costRand.begin(), costRand.end(), rng);

  r.cvKey1k = shardCv(costKey, 1000);
  r.cvRand1k = shardCv(costRand, 1000);
  r.cvKey10k = shardCv(costKey, 10000);
  r.cvRand10k = shardCv(costRand, 10000);
  return r;
}

int main(int argc, char** argv) {
  setvbuf(stdout, nullptr, _IOLBF, 0);  // line-buffered: progress survives a kill
  std::string lattice;
  std::string ladderArg = "8:13 11:16 14:18 17:20";
  int validateN = 0;
  // per H, how many representative columns to sample, and which fraction band
  // (mid-to-late, pruning-active). We sample the columns with the most states
  // among cols in [colFracLo, colFracHi] of the live range.
  int nSampleCols = 4;
  double colFracLo = 0.45, colFracHi = 0.95;
  for (int i = 1; i < argc; ++i) {
    std::string a = argv[i];
    if (a == "square8") lattice = a;
    else if (a == "--ladder" && i + 1 < argc) ladderArg = argv[++i];
    else if (a == "--validate" && i + 1 < argc) validateN = std::atoi(argv[++i]);
    else if (a == "--samplecols" && i + 1 < argc) nSampleCols = std::atoi(argv[++i]);
    else if (a == "--fold") g_fold = true;
    else { std::fprintf(stderr, "unknown arg: %s\n", a.c_str()); return 2; }
  }
  if (lattice != "square8") {
    std::fprintf(stderr,
        "usage: %s square8 [--ladder \"H:maxn ...\"] [--validate VMAXN] "
        "[--samplecols K]\n", argv[0]);
    return 2;
  }

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

  // parse the ladder
  struct Rung { int H, maxn; };
  std::vector<Rung> ladder;
  {
    std::string s = ladderArg;
    size_t pos = 0;
    while (pos < s.size()) {
      while (pos < s.size() && s[pos] == ' ') ++pos;
      if (pos >= s.size()) break;
      size_t colon = s.find(':', pos);
      size_t sp = s.find(' ', pos);
      if (colon == std::string::npos) break;
      int H = std::atoi(s.substr(pos, colon - pos).c_str());
      int mn = std::atoi(s.substr(colon + 1).c_str());
      ladder.push_back({H, mn});
      pos = (sp == std::string::npos) ? s.size() : sp;
    }
  }

  // Per-H, the chosen representative columns aggregated into a single H-row by
  // pooling their cost vectors? The metrics are best read per representative
  // column, then summarized per H. We print a per-column table and an H-summary
  // (median across the sampled columns, which is robust to one odd column).
  std::printf("=== COST H-LADDER  square8 ===\n");
  std::printf("cost metric = masks EXAMINED (stepColumnSquare8 calls); "
              "fan-out = successors PASSED (Alive+budget)\n\n");

  // accumulate H-summary rows
  struct HSummary {
    int H, maxn;
    double maxOverMedian, monsterFrac1k, top1pct, top01pct, maxOverCeil;
    double cvKey1k, cvRand1k, examPerPass, meanExam, maxExamFracCeil;
    size_t repCol; size_t repStates;
  };
  std::vector<HSummary> hsum;

  for (const Rung& rung : ladder) {
    int H = rung.H, maxn = rung.maxn;
    std::printf("---- H=%d  maxn=%d  (2^H ceiling = %llu) ----\n", H, maxn,
                (unsigned long long)(1ull << H));
    std::fflush(stdout);

    // Pass 1: cheap per-column state counts (memory-light).
    Counts harvest;
    std::vector<size_t> sizes = columnSizes(H, maxn, &harvest);
    int nCols = (int)sizes.size();
    int lastLive = nCols - 1;
    while (lastLive > 0 && sizes[lastLive] == 0) --lastLive;
    int loC = (int)std::floor(colFracLo * lastLive);
    int hiC = (int)std::ceil(colFracHi * lastLive);
    if (loC < 1) loC = 1;
    if (hiC > lastLive) hiC = lastLive;

    // pick the nSampleCols heaviest (by state count) columns in [loC,hiC]
    std::vector<int> cand;
    for (int c = loC; c <= hiC; ++c)
      if (sizes[c] > 0) cand.push_back(c);
    std::sort(cand.begin(), cand.end(),
              [&](int a, int b) { return sizes[a] > sizes[b]; });
    if ((int)cand.size() > nSampleCols) cand.resize(nSampleCols);
    std::sort(cand.begin(), cand.end());

    std::printf("  live cols 0..%d; pruning-active band [%d,%d]; sampling cols:",
                lastLive, loC, hiC);
    for (int c : cand) std::printf(" %d(%zu)", c, sizes[c]);
    std::printf("\n");
    std::fflush(stdout);

    // Pass 2: snapshot ONLY the sampled columns (frees the huge early ones).
    std::vector<FlatDB> cols = snapshotColumns(H, maxn, cand);

    std::printf("  %-4s %-9s %-11s %-10s %-9s %-9s %-9s %-9s %-9s %-8s %-8s %-8s %-8s %-8s\n",
                "col", "states", "exam/state", "pass/state", "ex/pass",
                "max/med", "monstr1k", "top1%", "top.1%", "mx/ceil",
                "cvKey1k", "cvRnd1k", "cvKey10k", "us/st");

    std::vector<ColReport> reps;
    for (size_t k = 0; k < cand.size(); ++k) {
      int c = cand[k];
      ColReport rep = analyzeColumn(cols[k], c, H, maxn);
      reps.push_back(rep);
      std::printf("  %-4d %-9zu %-11.2f %-10.2f %-9.2f %-9.1f %-9.4f %-9.4f %-9.4f %-8.5f %-8.4f %-8.4f %-8.4f %-8.3f\n",
                  rep.col, rep.nstates,
                  rep.nstates ? (double)rep.sumExam / rep.nstates : 0.0,
                  rep.nstates ? (double)rep.sumPass / rep.nstates : 0.0,
                  rep.sumPass ? (double)rep.sumExam / rep.sumPass : 0.0,
                  rep.maxOverMedian, rep.monsterFrac1k, rep.top1pct, rep.top01pct,
                  rep.maxOverCeil, rep.cvKey1k, rep.cvRand1k, rep.cvKey10k,
                  rep.wallUsPerState);
      std::fflush(stdout);
    }

    // H-summary = median across sampled columns of each metric
    auto med = [&](auto getter) -> double {
      std::vector<double> v;
      for (auto& rp : reps) v.push_back(getter(rp));
      std::sort(v.begin(), v.end());
      if (v.empty()) return 0;
      return v[v.size() / 2];
    };
    HSummary hs{};
    hs.H = H; hs.maxn = maxn;
    hs.maxOverMedian = med([](const ColReport& r){ return r.maxOverMedian; });
    hs.monsterFrac1k = med([](const ColReport& r){ return r.monsterFrac1k; });
    hs.top1pct = med([](const ColReport& r){ return r.top1pct; });
    hs.top01pct = med([](const ColReport& r){ return r.top01pct; });
    hs.maxOverCeil = med([](const ColReport& r){ return r.maxOverCeil; });
    hs.cvKey1k = med([](const ColReport& r){ return r.cvKey1k; });
    hs.cvRand1k = med([](const ColReport& r){ return r.cvRand1k; });
    hs.examPerPass = med([](const ColReport& r){
        return r.sumPass ? (double)r.sumExam / r.sumPass : 0.0; });
    hs.meanExam = med([](const ColReport& r){ return r.meanExam; });
    // representative = the heaviest sampled column (most states)
    {
      size_t best = 0; size_t bs = 0;
      for (size_t k = 0; k < reps.size(); ++k)
        if (reps[k].nstates > bs) { bs = reps[k].nstates; best = k; }
      hs.repCol = reps.empty() ? 0 : reps[best].col;
      hs.repStates = bs;
    }
    hsum.push_back(hs);
    std::printf("\n");
    std::fflush(stdout);
  }

  // ---- THE HEADLINE TREND TABLE (rows = H) ----
  std::printf("================ TREND vs H (median over sampled cols) ================\n");
  std::printf("%-4s %-6s %-9s %-9s %-11s %-9s %-8s %-8s %-9s %-9s %-9s\n",
              "H", "maxn", "repStates", "meanExam", "max/median", "monstr1k",
              "top1%", "top.1%", "mx/2^H", "cvKey1k", "cvRnd1k");
  for (auto& h : hsum) {
    std::printf("%-4d %-6d %-9zu %-9.1f %-11.1f %-9.4f %-8.4f %-8.4f %-9.5f %-9.4f %-9.4f\n",
                h.H, h.maxn, h.repStates, h.meanExam, h.maxOverMedian,
                h.monsterFrac1k, h.top1pct, h.top01pct, h.maxOverCeil,
                h.cvKey1k, h.cvRand1k);
  }
  std::printf("\nexam/pass gap (median over cols), per H:\n");
  for (auto& h : hsum)
    std::printf("  H=%-3d  examined/passed = %.2fx\n", h.H, h.examPerPass);

  return 0;
}
