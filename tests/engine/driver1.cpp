// driver1.cpp — AC-1 serial end-to-end driver with NVMe spill (T1.3).
//
// Runs one height-sweep at a time (H=1..maxn) using file-backed frontier runs.
// The entire frontier is written to disk between columns; map_shard_file spills
// partial sorted buffers to disk when the buffer exceeds --ram bytes.
//
// Usage:
//   driver1 [--maxn N] [--fold] [--ram BYTES] [--spill DIR] [--compare]
//
// Defaults: maxn=14, ram=134217728 (128 MB), spill=/tmp/ns_driver1_PID, compare=true
//
// AC-1 gate: ./driver1 --maxn 14 --ram 1048576 --spill /tmp/ns_m1_gate --compare
//   (ram=1 MB forces many spills even at n=14, exercises the spill path)
//
// Full AC-1 run (long — hours to days):
//   ./driver1 --maxn 18 --ram 67108864 --spill /some/nvme/dir --compare

#include <algorithm>
#include <cerrno>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <ctime>
#include <string>
#include <vector>

#include <sys/stat.h>
#include <unistd.h>

#include "core/fdlimit.h"
#include "core/libenum.h"
#include "worker/worker_util.h"

// ─── Helpers ──────────────────────────────────────────────────────────────────

static std::vector<uint64_t> loadKnown(const char* path) {
  std::vector<uint64_t> known(1, 0);
  FILE* f = std::fopen(path, "r");
  if (!f) return known;
  char line[256];
  while (std::fgets(line, sizeof line, f)) {
    int n; unsigned long long v;
    if (std::sscanf(line, "%d %llu", &n, &v) == 2 && n >= 0) {
      if (n >= static_cast<int>(known.size())) known.resize(n + 1, 0);
      known[n] = v;
    }
  }
  std::fclose(f);
  return known;
}

// Write the seed state (empty boundary, counts[0]=1) to a POLYRUN file.
static std::string writeSeed(const std::string& dir, int H, int maxn,
                             const std::string& rev) {
  std::string path = dir + "/seed_h" + std::to_string(H) + ".bin";
  RunFileWriter<u64> w(path, H, maxn, "", "", rev);
  w.append(seedRecord<u64>(H));
  w.finalize();
  return path;
}

// ─── Main ────────────────────────────────────────────────────────────────────

int main(int argc, char** argv) {
  raiseFdLimitToHard();  // the spill/merge path fans out to many open files
  int  maxn     = 14;
  bool fold     = false;
  bool compare  = true;
  size_t ram    = 134217728ULL;  // 128 MB
  std::string spill_dir;

  for (int i = 1; i < argc; ++i) {
    auto arg = [&](const char* flag) {
      return std::strcmp(argv[i], flag) == 0 && i + 1 < argc;
    };
    if (arg("--maxn"))         maxn      = std::atoi(argv[++i]);
    else if (!std::strcmp(argv[i], "--fold"))    fold    = true;
    else if (!std::strcmp(argv[i], "--compare")) compare = true;
    else if (!std::strcmp(argv[i], "--no-compare")) compare = false;
    else if (arg("--ram"))     ram       = static_cast<size_t>(std::strtoull(argv[++i], nullptr, 10));
    else if (arg("--spill"))   spill_dir = argv[++i];
    else {
      std::fprintf(stderr, "driver1: unknown arg: %s\n", argv[i]);
      return 1;
    }
  }

  // Default spill dir based on PID.
  if (spill_dir.empty()) {
    spill_dir = "/tmp/ns_driver1_" + std::to_string(static_cast<long>(getpid()));
  }

  // Create spill dir if needed (ignore EEXIST).
  if (mkdir(spill_dir.c_str(), 0777) != 0 && errno != EEXIST) {
    std::perror(("driver1: cannot create spill dir " + spill_dir).c_str());
    return 1;
  }

  const char* rev = GIT_REV;
  std::printf("driver1 maxn=%d fold=%d ram=%zu spill=%s rev=%s\n",
              maxn, (int)fold, ram, spill_dir.c_str(), rev);

  std::vector<uint64_t> total(maxn + 1, 0);
  size_t grand_spill = 0;
  const double t_start = wallSeconds();

  for (int H = 1; H <= maxn; ++H) {
    ShardCfg cfg;
    cfg.H                = H;
    cfg.maxn             = maxn;
    cfg.fold             = fold;
    cfg.ram_budget_bytes = ram;
    cfg.spill_dir        = spill_dir;

    // Write the seed run for this height.
    std::string frontier = writeSeed(spill_dir, H, maxn, rev);

    TriangleRow<u64> triangle(H, maxn);
    size_t height_spill = 0;

    for (int col = 0; col <= maxn; ++col) {
      std::string next = spill_dir + "/h" + std::to_string(H) +
                         "_col" + std::to_string(col + 1) + ".bin";

      auto [sb, recs] = map_shard_file<u64, ClassifyTriangle>(
          {frontier}, cfg, next, "", "", triangle, rev);

      height_spill += sb;

      // Clean up the input frontier file (no longer needed).
      std::remove(frontier.c_str());
      frontier = next;

      std::printf("  H=%d col=%d recs=%zu spill=%zu\n", H, col, recs, sb);

      if (recs == 0) {
        std::remove(frontier.c_str());
        break;
      }
    }

    // Accumulate triangle row into total.
    for (int n = 1; n <= maxn; ++n)
      total[n] += static_cast<uint64_t>(triangle.row[n]);

    grand_spill += height_spill;
    std::printf("H=%d done spill=%zu\n", H, height_spill);
  }

  const double wall_s = wallSeconds() - t_start;
  std::printf("\ntotal_spill_bytes=%zu  wall=%.1fs\n", grand_spill, wall_s);

  // ─── Compare to known a(n) ────────────────────────────────────────────────
  if (!compare) return 0;

  const auto known = loadKnown("fixtures/b006770.txt");
  const int nKnown = static_cast<int>(known.size()) - 1;
  if (nKnown < 1) {
    std::fprintf(stderr,
      "driver1: no known values from fixtures/b006770.txt (run from repo root)\n");
    return 1;
  }

  bool allOk = true;
  for (int n = 1; n <= std::min(maxn, nKnown); ++n) {
    const bool ok = (total[n] == known[n]);
    std::printf("n=%2d  a(n)=%llu  known=%llu  %s\n",
                n, (unsigned long long)total[n],
                (unsigned long long)known[n], ok ? "OK" : "FAIL");
    if (!ok) allOk = false;
  }

  if (!allOk) { std::puts("gate_spill FAIL"); return 1; }

  if (grand_spill == 0 && ram > 0) {
    std::printf("WARNING: no spill occurred (ram_budget=%zu, maxn=%d) — "
                "try smaller --ram to exercise the spill path\n", ram, maxn);
  }
  std::printf("gate_spill PASS (maxn=%d total_spill_bytes=%zu)\n",
              maxn, grand_spill);
  return 0;
}
