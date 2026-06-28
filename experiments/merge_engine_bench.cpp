// merge_engine_bench.cpp — profile / A-B the REAL production merge path.
//
// Writes N overlapping sorted POLYRUN files with the real RunFileWriter (so they
// carry the sparse .idx), then merges all M key-ranges via the real
// mergeRunFiles — the exact code merge_workers run. Unlike sampling the
// transient workers, this is one long-lived process: `sample` it for the true
// hotspots, and toggle POLY_NO_SEEK to A/B the seek-index on the production code.
//
// Usage: merge_engine_bench [T_RECORDS] [N_FILES] [M_RANGES] [REPS]
#include <chrono>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <random>
#include <string>
#include <vector>

#include "core/runfile.h"

using clk = std::chrono::steady_clock;
static double secs(clk::time_point a) { return std::chrono::duration<double>(clk::now() - a).count(); }

static std::string encodeHex(uint64_t k, int keyLen) {   // big-endian, memcmp-sortable
  uint8_t b[64] = {0};
  for (int i = 0; i < keyLen; i++) b[i] = i < 8 ? (k >> (8 * (7 - i))) & 0xFF : 0;
  return bytesToHex(b, keyLen);
}

int main(int argc, char** argv) {
  size_t T = argc > 1 ? strtoull(argv[1], nullptr, 10) : 4'000'000;
  int N    = argc > 2 ? atoi(argv[2]) : 64;
  int M    = argc > 3 ? atoi(argv[3]) : 64;
  int REPS = argc > 4 ? atoi(argv[4]) : 6;
  const int H = 18, keyLen = H + 2, maxn = 30;
  const std::string dir = "build/meb";
  std::system(("rm -rf " + dir + " && mkdir -p " + dir).c_str());

  // N overlapping sorted runs: assign T sorted keys to random files.
  std::mt19937_64 rng(11);
  std::vector<uint64_t> all(T);
  for (auto& k : all) k = rng();
  std::sort(all.begin(), all.end());
  std::vector<std::string> paths(N);
  std::vector<std::unique_ptr<RunFileWriter<u64>>> ws;
  ws.reserve(N);
  for (int r = 0; r < N; r++) {
    paths[r] = dir + "/run" + std::to_string(r) + ".bin";
    ws.push_back(std::make_unique<RunFileWriter<u64>>(paths[r], H, maxn, "", "", "bench", keyLen));
  }
  for (uint64_t k : all) {
    RunRecord<u64> rec;
    rec.H = H; rec.keyLen = keyLen; rec.lo = 1; rec.len = 4;
    rec.counts.assign(4, 1);
    for (int i = 0; i < keyLen; i++) rec.sig.b[i] = i < 8 ? (k >> (8 * (7 - i))) & 0xFF : 0;
    ws[rng() % N]->append(rec);
  }
  for (auto& w : ws) w->finalize();

  // M range cuts over the u64 keyspace.
  std::vector<std::string> cut(M + 1);
  for (int j = 0; j <= M; j++)
    cut[j] = encodeHex(j == M ? UINT64_MAX : (uint64_t)((__uint128_t)j * UINT64_MAX / M), keyLen);

  const bool seek = !std::getenv("POLY_NO_SEEK");
  size_t total_out = 0;
  auto t0 = clk::now();
  for (int rep = 0; rep < REPS; rep++)
    for (int j = 0; j < M; j++) {
      std::string out = dir + "/out.bin";
      auto [bytes, recs] = mergeRunFiles<u64>(paths, H, cut[j], cut[j + 1], out, "bench", keyLen);
      (void)bytes; total_out += recs;
    }
  double t = secs(t0);

  printf("seek=%s  T=%zu N=%d M=%d reps=%d  merged_out=%zu (expect %zu)  wall=%.3fs  %.1f Mrec-out/s\n",
         seek ? "ON" : "OFF", T, N, M, REPS, total_out, (size_t)T * REPS,
         t, total_out / t / 1e6);
  std::system(("rm -rf " + dir).c_str());
  return 0;
}
