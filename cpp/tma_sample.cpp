// Uniform random sampler / specimen emitter for fixed polyplets (A006770).
//
// Draws K animals of n cells uniformly at random from all a(n) of them, using
// the transfer-matrix completion DP (cpp/tma/sample8.h). Each specimen is then
// re-checked by an INDEPENDENT verifier (a plain king-BFS + bounding-box test
// that shares no code with the counting engine), so a clean run is evidence the
// engine's accepted states are all genuine, distinct n-cell polyplets. The
// height histogram is chi-square tested against the engine's own
// byHeight[H][n] / a(n) -- a consistency check between counter and sampler.
//
// Usage:
//   tma_sample N [--samples K] [--seed S] [--out FILE]
//                [--only-height H] [--byheight DIR]
//   --only-height H : sample only height H (uniform WITHIN that height)
//   --byheight DIR  : read byHeight[H][n] from DIR/h{H}.{txt,out} ("n count"
//                     lines) instead of recomputing -- lets the heavy a(19)
//                     heights be allocated from the existing checkpoints.

#include <algorithm>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <memory>
#include <queue>
#include <random>
#include <set>
#include <string>
#include <unordered_set>
#include <vector>

#include "obs.h"  // shared observability/provenance runtime (docs/observability.md)
#include "tma/sample8.h"

using Cells = std::vector<std::pair<int, int>>;

// ---- Independent verifier: NO transfer-matrix code below this line ----------
// A specimen is valid iff it has exactly n cells, its bounding box is anchored
// at column 0 and spans rows 0..H-1 (height exactly H), and it is a single
// king-connected (8-neighbor) component. Connectivity is a fresh BFS over the
// raw cell set -- it does not consult signatures, union-find, or any engine
// state, so it is a genuine second opinion.
static bool verifySpecimen(const Cells& cells, int n, int H, std::string& why) {
  if (static_cast<int>(cells.size()) != n) { why = "cell count != n"; return false; }
  int minc = 1 << 30, maxc = -1, minr = 1 << 30, maxr = -1;
  for (auto& [c, r] : cells) {
    minc = std::min(minc, c); maxc = std::max(maxc, c);
    minr = std::min(minr, r); maxr = std::max(maxr, r);
  }
  if (minc != 0) { why = "leftmost column not anchored at 0"; return false; }
  if (minr != 0 || maxr != H - 1) { why = "height != H"; return false; }
  std::set<std::pair<int, int>> S(cells.begin(), cells.end());
  if (static_cast<int>(S.size()) != n) { why = "duplicate cell"; return false; }
  // BFS king-connectivity from the first cell.
  std::set<std::pair<int, int>> seen;
  std::queue<std::pair<int, int>> q;
  q.push(cells[0]); seen.insert(cells[0]);
  while (!q.empty()) {
    auto [c, r] = q.front(); q.pop();
    for (int dc = -1; dc <= 1; ++dc)
      for (int dr = -1; dr <= 1; ++dr) {
        if (!dc && !dr) continue;
        std::pair<int, int> nb{c + dc, r + dr};
        if (S.count(nb) && !seen.count(nb)) { seen.insert(nb); q.push(nb); }
      }
  }
  if (static_cast<int>(seen.size()) != n) { why = "not king-connected"; return false; }
  return true;
}

// Canonical key for dedup: cells translated so the bounding box starts at (0,0),
// sorted. Two specimens collide iff they are the same fixed animal.
static std::string canonKey(const Cells& cells) {
  int minc = 1 << 30, minr = 1 << 30;
  for (auto& [c, r] : cells) { minc = std::min(minc, c); minr = std::min(minr, r); }
  Cells t;
  for (auto& [c, r] : cells) t.emplace_back(c - minc, r - minr);
  std::sort(t.begin(), t.end());
  std::string k;
  for (auto& [c, r] : t) { k += static_cast<char>(c); k += static_cast<char>(r); }
  return k;
}

static void renderSpecimen(FILE* f, const Cells& cells, int idx, int H) {
  int maxc = 0;
  for (auto& [c, r] : cells) maxc = std::max(maxc, c);
  std::fprintf(f, "# specimen %d  height %d  width %d  cells %d\n", idx, H,
               maxc + 1, static_cast<int>(cells.size()));
  std::vector<std::string> grid(H, std::string(maxc + 1, '.'));
  for (auto& [c, r] : cells) grid[r][c] = '#';
  for (int r = 0; r < H; ++r) std::fprintf(f, "%s\n", grid[r].c_str());
  std::fprintf(f, "coords:");
  Cells s = cells; std::sort(s.begin(), s.end());
  for (auto& [c, r] : s) std::fprintf(f, " (%d,%d)", c, r);
  std::fprintf(f, "\n\n");
}

// Read byHeight[H][n] for one H from DIR/h{H}.txt or DIR/h{H}.out ("n count").
static bool readByHeight(const std::string& dir, int H, int n, u64& out) {
  for (const char* ext : {".txt", ".out"}) {
    const std::string path = dir + "/h" + std::to_string(H) + ext;
    FILE* f = std::fopen(path.c_str(), "r");
    if (!f) continue;
    out = 0;
    int nn; unsigned long long c;
    while (std::fscanf(f, "%d %llu", &nn, &c) == 2)
      if (nn == n) out = c;
    std::fclose(f);
    return true;
  }
  return false;
}

// Upper-tail chi-square p-value via the Wilson-Hilferty normal approximation
// (good to ~3 sig figs for dof >= ~3) -- just a sanity readout, not a test gate.
static double chiSqUpperP(double x, int dof) {
  if (dof <= 0) return 1.0;
  const double k = dof;
  const double z = (std::cbrt(x / k) - (1.0 - 2.0 / (9.0 * k))) /
                   std::sqrt(2.0 / (9.0 * k));
  return 0.5 * std::erfc(z / std::sqrt(2.0));
}

int main(int argc, char** argv) {
  if (argc < 2) {
    std::fprintf(stderr,
                 "usage: %s N [--samples K] [--seed S] [--out FILE] "
                 "[--only-height H] [--byheight DIR]\n", argv[0]);
    return 2;
  }
  const int n = std::atoi(argv[1]);
  if (n < 1 || n > 30) { std::fprintf(stderr, "N out of range (1..30)\n"); return 2; }
  long K = 256;
  uint64_t seed = 0x9e3779b97f4a7c15ull;
  std::string outPath = "samples.txt", byHeightDir;
  int onlyHeight = 0, maxHeight = 0;  // maxHeight 0 = no cap (all heights 1..n)
  for (int i = 2; i < argc; ++i) {
    if (!std::strcmp(argv[i], "--samples") && i + 1 < argc) K = std::atol(argv[++i]);
    else if (!std::strcmp(argv[i], "--seed") && i + 1 < argc) seed = std::strtoull(argv[++i], nullptr, 0);
    else if (!std::strcmp(argv[i], "--out") && i + 1 < argc) outPath = argv[++i];
    else if (!std::strcmp(argv[i], "--only-height") && i + 1 < argc) onlyHeight = std::atoi(argv[++i]);
    else if (!std::strcmp(argv[i], "--max-height") && i + 1 < argc) maxHeight = std::atoi(argv[++i]);
    else if (!std::strcmp(argv[i], "--byheight") && i + 1 < argc) byHeightDir = argv[++i];
    else { std::fprintf(stderr, "unknown arg: %s\n", argv[i]); return 2; }
  }
  std::mt19937_64 rng(seed);
  obs::Reporter rep("sample-N" + std::to_string(n) + "-K" + std::to_string(K), 0,
                    "seed=" + std::to_string(seed));

  // 1. byHeight[H][n] for every height (the height-selection weights). From the
  //    checkpoint dir if given, else computed by the completion DP.
  std::vector<u64> bH(n + 1, 0);
  std::vector<std::unique_ptr<Completion>> comp(n + 1);  // built once, kept for sampling
  const int hLo = onlyHeight ? onlyHeight : 1;
  const int cap = (maxHeight > 0 && maxHeight < n) ? maxHeight : n;
  const int hHi = onlyHeight ? onlyHeight : cap;
  Sig seedSig; std::memset(seedSig.b, 0, SIGMAX);
  for (int H = hLo; H <= hHi; ++H) {
    if (!byHeightDir.empty() && readByHeight(byHeightDir, H, n, bH[H])) continue;
    comp[H] = std::make_unique<Completion>(H, n);
    bH[H] = comp[H]->W(seedSig, n);  // == byHeight[H][n]; primes the memo for sampling
    rep.beat(H, "phase=build height=" + std::to_string(H) + " byheight=" +
                    std::to_string(static_cast<unsigned long long>(bH[H])),
             true);
  }
  u64 total = 0;
  for (int H = hLo; H <= hHi; ++H) total += bH[H];
  if (total == 0) { std::fprintf(stderr, "no animals to sample\n"); return 1; }
  std::fprintf(stderr, "a(%d) over heights %d..%d = %llu\n", n, hLo, hHi,
               static_cast<unsigned long long>(total));

  // 2. Allocate K samples across heights by drawing K i.i.d. heights ~ bH/total
  //    (categorical) -- exactly the first random choice of a uniform draw.
  std::vector<long> alloc(n + 1, 0);
  std::vector<u64> cum(n + 1, 0);
  for (int H = 1; H <= n; ++H) cum[H] = cum[H - 1] + bH[H];
  std::uniform_int_distribution<u64> pick(0, total - 1);
  for (long s = 0; s < K; ++s) {
    const u64 r = pick(rng);
    int H = static_cast<int>(std::upper_bound(cum.begin(), cum.end(), r) - cum.begin());
    if (H < 1) H = 1;
    if (H > n) H = n;
    ++alloc[H];
  }

  // 3. Per height: build completion, draw its share, verify each specimen.
  FILE* f = std::fopen(outPath.c_str(), "w");
  if (!f) { std::perror("open --out"); return 1; }
  std::fprintf(f, "# %ld uniform random fixed polyplets of %d cells (A006770), seed 0x%llx\n\n",
               K, n, static_cast<unsigned long long>(seed));
  std::unordered_set<std::string> distinct;
  std::vector<long> obs(n + 1, 0);
  long emitted = 0, bad = 0, dups = 0;
  Cells firstFew[3]; int firstFewH[3]; int nFirst = 0;
  for (int H = 1; H <= n; ++H) {
    if (alloc[H] == 0) continue;
    if (!comp[H]) {  // --byheight path: weight came from a file, build DP now
      comp[H] = std::make_unique<Completion>(H, n);
      if (comp[H]->W(seedSig, n) == 0) continue;
    }
    Completion& C = *comp[H];
    for (long s = 0; s < alloc[H]; ++s) {
      Cells cells = sampleOne(C, rng);
      std::string why;
      if (!verifySpecimen(cells, n, H, why)) {
        std::fprintf(stderr, "INVALID specimen (height %d): %s\n", H, why.c_str());
        ++bad; continue;
      }
      if (!distinct.insert(canonKey(cells)).second) ++dups;
      ++obs[H];
      ++emitted;
      renderSpecimen(f, cells, static_cast<int>(emitted), H);
      if (nFirst < 3) { firstFew[nFirst] = cells; firstFewH[nFirst] = H; ++nFirst; }
    }
    rep.beat(emitted, "phase=sample height=" + std::to_string(H) +
                          " emitted=" + std::to_string(emitted), true);
  }
  std::fclose(f);

  // 4. chi-square: observed height histogram vs expected K * bH/total. Heights
  //    with expected < 5 are pooled together (Cochran's rule) so the asymptotic
  //    chi-square holds -- the extreme heights of a(n) have near-zero
  //    probability and would otherwise spuriously inflate the statistic.
  double chi = 0; int cells_used = 0;
  double poolObs = 0, poolExp = 0; int pooled = 0;
  for (int H = 1; H <= n; ++H) {
    const double exp = static_cast<double>(K) * static_cast<double>(bH[H]) / static_cast<double>(total);
    if (exp <= 0) continue;
    if (exp < 5.0) { poolObs += obs[H]; poolExp += exp; ++pooled; continue; }
    ++cells_used;
    const double d = obs[H] - exp;
    chi += d * d / exp;
  }
  if (poolExp >= 5.0) { ++cells_used; const double d = poolObs - poolExp; chi += d * d / poolExp; }
  const int dof = cells_used - 1;
  const double p = chiSqUpperP(chi, dof);

  // 5. Report.
  std::printf("samples requested : %ld\n", K);
  std::printf("specimens emitted : %ld\n", emitted);
  std::printf("INVALID specimens : %ld   (independent king-BFS + bbox verifier)\n", bad);
  std::printf("duplicate animals : %ld   (expected ~0 unless n tiny)\n", dups);
  std::printf("distinct animals  : %zu\n", distinct.size());
  std::printf("a(%d) [heights %d..%d] = %llu\n", n, hLo, hHi,
              static_cast<unsigned long long>(total));
  std::printf("height histogram chi-square = %.2f  dof %d  p = %.3f  (%d heights pooled, exp<5)\n",
              chi, dof, p, pooled);
  std::printf("specimens written to %s\n\n", outPath.c_str());
  for (int i = 0; i < nFirst; ++i) {
    int maxc = 0; for (auto& [c, r] : firstFew[i]) maxc = std::max(maxc, c);
    std::printf("--- specimen %d (height %d, width %d) ---\n", i + 1, firstFewH[i], maxc + 1);
    std::vector<std::string> grid(firstFewH[i], std::string(maxc + 1, '.'));
    for (auto& [c, r] : firstFew[i]) grid[r][c] = '#';
    for (auto& row : grid) std::printf("%s\n", row.c_str());
    std::printf("\n");
  }
  rep.done("result=" + std::to_string(static_cast<unsigned long long>(total)),
           "emitted=" + std::to_string(emitted) + " bad=" + std::to_string(bad) +
               " dups=" + std::to_string(dups));
  return bad ? 1 : 0;
}
