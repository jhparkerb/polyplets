// Transfer-matrix driver.
//
// CLI:  tma {square4|square8} MAXN [--per-height] [--checkpoint DIR]
//   totals: "n count" lines; --per-height: "h n count" lines.
//   --checkpoint DIR (square8): persist each strip height as it finishes and
//     resume completed heights on restart -- so a crash mid-run costs one
//     height, not the whole multi-day sweep. Heights are independent sub-sums.

#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <filesystem>
#include <string>

#include "tma/sweep.h"
#include "tma/sweep8.h"

namespace fs = std::filesystem;

// Load checkpoint height file "DIR/hH.txt" ("n count" lines) into row; returns
// false if it does not exist yet (height still to compute).
static bool loadHeight(const std::string& dir, int H, int maxn, Counts& row) {
  const std::string path = dir + "/h" + std::to_string(H) + ".txt";
  FILE* f = std::fopen(path.c_str(), "r");
  if (!f) return false;
  row.assign(maxn + 1, 0);
  int n;
  unsigned long long c;
  while (std::fscanf(f, "%d %llu", &n, &c) == 2)
    if (n >= 0 && n <= maxn) row[n] = c;
  std::fclose(f);
  return true;
}

// Atomically persist a height row: write a temp file, then rename it into
// place. A crash mid-write leaves the temp (ignored on resume), never a
// half-written hH.txt -- so "hH.txt exists" reliably means "height H is done".
static void saveHeight(const std::string& dir, int H, int maxn, const Counts& row) {
  const std::string tmp = dir + "/h" + std::to_string(H) + ".tmp";
  const std::string path = dir + "/h" + std::to_string(H) + ".txt";
  FILE* f = std::fopen(tmp.c_str(), "w");
  if (!f) { std::perror("checkpoint open"); std::exit(1); }
  for (int n = 1; n <= maxn; ++n)
    if (row[n]) std::fprintf(f, "%d %llu\n", n, static_cast<unsigned long long>(row[n]));
  std::fflush(f);
  std::fclose(f);
  if (std::rename(tmp.c_str(), path.c_str()) != 0) {
    std::perror("checkpoint rename");
    std::exit(1);
  }
}

// Guard a checkpoint dir against being reused with mismatched args (a resume
// must use the same lattice+maxn or the partial rows are meaningless).
static void checkMeta(const std::string& dir, const std::string& lattice, int maxn) {
  const std::string path = dir + "/meta";
  if (FILE* f = std::fopen(path.c_str(), "r")) {
    char lat[32] = {0};
    int m = 0;
    const bool ok = std::fscanf(f, "%31s %d", lat, &m) == 2;
    std::fclose(f);
    if (ok && (lattice != lat || maxn != m)) {
      std::fprintf(stderr,
                   "checkpoint %s is for %s maxn=%d, not %s maxn=%d -- refuse\n",
                   path.c_str(), lat, m, lattice.c_str(), maxn);
      std::exit(2);
    }
    if (ok) return;
  }
  if (FILE* f = std::fopen(path.c_str(), "w")) {
    std::fprintf(f, "%s %d\n", lattice.c_str(), maxn);
    std::fclose(f);
  }
}

static void emit(const SweepResults& res, int maxn, bool perHeight) {
  std::fprintf(stderr, "peak_states %llu peak_height %d\n",
               static_cast<unsigned long long>(res.peakStates), res.peakHeight);
  if (perHeight) {
    for (int h = 1; h <= maxn; ++h)
      for (int n = 1; n <= maxn; ++n)
        if (res.byHeight[h][n])
          std::printf("%d %d %llu\n", h, n,
                      static_cast<unsigned long long>(res.byHeight[h][n]));
  } else {
    for (int n = 1; n <= maxn; ++n)
      std::printf("%d %llu\n", n, static_cast<unsigned long long>(res.totals[n]));
  }
}

int main(int argc, char** argv) {
  if (argc < 3) {
    std::fprintf(stderr,
                 "usage: %s {square4|square8} MAXN [--per-height] "
                 "[--checkpoint DIR]\n",
                 argv[0]);
    return 2;
  }
  const std::string lattice = argv[1];
  if (lattice != "square4" && lattice != "square8") {
    std::fprintf(stderr, "lattice must be square4 or square8\n");
    return 2;
  }
  const int maxn = std::atoi(argv[2]);
  if (maxn < 1 || maxn > 30) {
    std::fprintf(stderr, "MAXN out of range (1..30)\n");
    return 2;
  }
  bool perHeight = false;
  std::string checkpointDir;
  for (int i = 3; i < argc; ++i) {
    if (std::strcmp(argv[i], "--per-height") == 0) {
      perHeight = true;
    } else if (std::strcmp(argv[i], "--checkpoint") == 0 && i + 1 < argc) {
      checkpointDir = argv[++i];
    } else {
      std::fprintf(stderr, "unknown arg: %s\n", argv[i]);
      return 2;
    }
  }

  if (!checkpointDir.empty()) {
    if (lattice != "square8") {
      std::fprintf(stderr, "--checkpoint is supported for square8 only\n");
      return 2;
    }
    fs::create_directories(checkpointDir);
    checkMeta(checkpointDir, lattice, maxn);

    SweepResults res;
    res.byHeight.assign(maxn + 1, Counts(maxn + 1, 0));
    res.totals.assign(maxn + 1, 0);
    for (int H = 1; H <= maxn; ++H) {
      Counts row;
      if (loadHeight(checkpointDir, H, maxn, row)) {
        std::fprintf(stderr, "height %d/%d resumed from checkpoint\n", H, maxn);
      } else {
        row = sweepSquare8Height(H, maxn, res);
        saveHeight(checkpointDir, H, maxn, row);
        std::fprintf(stderr, "height %d/%d done (peak_states %llu)\n", H, maxn,
                     static_cast<unsigned long long>(res.peakStates));
      }
      res.byHeight[H] = std::move(row);
    }
    accumulateTotals(res, maxn);
    emit(res, maxn, perHeight);
    return 0;
  }

  SweepResults res =
      (lattice == "square4") ? sweepSquare4(maxn) : sweepSquare8(maxn);
  emit(res, maxn, perHeight);
  return 0;
}
