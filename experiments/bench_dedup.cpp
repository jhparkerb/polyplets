// bench_dedup.cpp -- local, fast benchmark for deduplicateRun/combine
// (core/run.h), testing the lead from docs/utilization-bottleneck-log.md's
// "Bottleneck #6 attempt" section: does dedup-collision RATE (how many
// records share a canonical key after sortRun) explain the observed
// concurrency collapse across kink sweep stages, given kinkStageTransition
// itself is confirmed cheap? Not wired into any gate -- throwaway
// measurement tool, same minimum-of-N-trials methodology as
// bench_viablemask.cpp (kept honest this time: verified against the REAL
// production hot path, core/kink.h's actual call chain, not assumed).
//
// Build: c++ -std=c++20 -O3 -I. experiments/bench_dedup.cpp -o /tmp/bench_dedup
// Run:   /tmp/bench_dedup

#include <chrono>
#include <cstdio>
#include <random>
#include <vector>

#include "core/run.h"
#include "core/signature.h"

using W = unsigned __int128;
using Clock = std::chrono::steady_clock;

// Builds a sorted Run<W> of `n` records over `distinctKeys` distinct sig
// values (so avg collisions per key = n/distinctKeys), each with a count-vec
// window of `width` entries at a RANDOMIZED offset -- mimicking a real kink
// stage table shard, where different records' ranged windows start at
// different `lo` offsets (a flat lo=0 for every record, an earlier version
// of this benchmark's bug, never exercises combine()'s left-extension path
// at all regardless of sort order -- caught by the fix showing no
// measurable difference on the flawed version, a real "the fix did
// nothing" signal that was itself the tell).
static Run<W> makeRun(int H, int keyLen, size_t n, size_t distinctKeys, int width,
                       int maxLoSpread, unsigned seed) {
  std::mt19937 rng(seed);
  std::uniform_int_distribution<int> keyDist(0, static_cast<int>(distinctKeys) - 1);
  std::uniform_int_distribution<int> loDist(0, maxLoSpread);
  Run<W> run;
  run.reserve(n);
  for (size_t i = 0; i < n; ++i) {
    RunRecord<W> r;
    r.H = static_cast<uint8_t>(H);
    r.keyLen = static_cast<uint8_t>(keyLen);
    int k = keyDist(rng);
    // Encode k into the first bytes of sig (deterministic, sortable).
    r.sig.b[0] = static_cast<unsigned char>((k >> 8) & 0xff);
    r.sig.b[1] = static_cast<unsigned char>(k & 0xff);
    r.lo = static_cast<uint8_t>(loDist(rng));
    r.len = static_cast<uint8_t>(width);
    r.counts.assign(width, W(1));
    run.push_back(std::move(r));
  }
  sortRun(run);
  return run;
}

// A volatile sink: without an observable use of `run` after
// deduplicateRun mutates it, the compiler can legally prove the whole call
// has no effect and eliminate it (this exact mistake, caught once already
// in bench_viablemask.cpp's git history, showed up as an impossible
// 0.0000 ns/call baseline).
static volatile size_t g_sink = 0;

// Times ONLY deduplicateRun(run) itself, minimum across `trials` fresh
// copies of `base` (copying is excluded from the timed window).
static double dedupMinMs(const Run<W>& base, int trials) {
  double best = -1;
  for (int t = 0; t < trials; ++t) {
    Run<W> run = base;
    auto t0 = Clock::now();
    deduplicateRun(run);
    auto t1 = Clock::now();
    double ms = std::chrono::duration<double, std::milli>(t1 - t0).count();
    if (best < 0 || ms < best) best = ms;
    g_sink = run.size();
  }
  return best;
}

int main() {
  const int H = 21, keyLen = H + 4; // kink stage table key width
  const size_t n = 65625;           // ~21M frontier / 320 units, one unit's share
  const int trials = 7;

  struct Scenario { const char* label; size_t distinctKeys; int width; };
  std::vector<Scenario> scenarios = {
      {"low-collision, narrow", n,      4},   // every record distinct, narrow window
      {"low-collision, wide",   n,      30},  // every record distinct, wide window
      {"high-collision, narrow", n / 20, 4},  // 20x avg collisions, narrow window
      {"high-collision, wide",   n / 20, 30}, // 20x avg collisions, wide window
  };

  for (auto& sc : scenarios) {
    // lo spread of 3x width: windows overlap variably, so combine() calls
    // within a collision group hit both the grow-in-place and (pre-fix)
    // left-extension paths, matching a real ranged count-vec's lo variance.
    Run<W> base = makeRun(H, keyLen, n, sc.distinctKeys, sc.width, sc.width * 3, 42);
    size_t outSize = base.size(); // will shrink after dedup; probe separately
    {
      Run<W> probe = base;
      deduplicateRun(probe);
      outSize = probe.size();
    }
    double ms = dedupMinMs(base, trials);
    std::printf("%-24s n=%zu distinct=%zu width=%d -> %zu records: dedup best-of-%d = %.3f ms\n",
                sc.label, n, sc.distinctKeys, sc.width, outSize, trials, ms);
  }

  return 0;
}
