// bench_viablemask.cpp -- WRONG TARGET, kept for the record + methodology.
//
// This benchmarks forEachViableMask/viableRec (core/transition.h), the
// COLUMN kernel's enumeration mechanism (core/mapreduce.h's map_shard_file).
// Production uses --kernel kink (scripts/dalby_term.sh), whose actual hot
// path is kinkStageTransition (core/kink.h:98) -- a simple `for (occupy in
// {0,1})` loop, O(1)/O(H)-bounded, no recursive tree at all. The numbers
// below are real but answer a question about code nothing in production
// runs. See results/sub-record-interrupt-design.md's correction note.
//
// The METHODOLOGY (local throwaway C++ benchmark, minimum-of-N-trials, a
// volatile sink to defeat dead-code elimination -- caught a real 0.0000
// ns/call artifact from an under-specified baseline lambda, see git log)
// is still the right approach for the real question: what in
// kinkStageTransition's bounded per-record path causes unit 319's measured
// 100x+ wall-time variance at similar-to-lower record counts. Whoever
// picks that up should write a NEW benchmark against kinkStageTransition
// directly, not extend this one.
//
// Build: c++ -std=c++20 -O3 -I. experiments/bench_viablemask.cpp -o /tmp/bench_vm
// Run:   /tmp/bench_vm

#include <csignal>
#include <cstdio>
#include <chrono>
#include <cstring>

#include "core/signature.h"
#include "core/transition.h"

using Clock = std::chrono::steady_clock;

// A moderately-populated boundary signature: alternating small labels, a
// realistic mid-sweep pattern (not all-zero, which is a degenerate trivial
// case; not maximally-viable either).
static Sig makeSig(int H) {
  Sig s{};
  int label = 0;
  for (int i = 0; i < H; ++i) {
    if (i % 3 != 2) {
      label = (label % 4) + 1;
      s.b[i] = static_cast<unsigned char>(label);
    }
  }
  return s;
}

static volatile std::sig_atomic_t g_terminate = 0;

// Runs `body` for `reps` iterations, TRIALS times, and prints the MINIMUM
// ns/call across trials (min, not mean, is the standard way to filter
// system noise/interference out of a microbenchmark -- the true cost is a
// floor, and only noise pushes a trial's time above it).
template <class F>
static void bench(const char* label, int reps, long long callsPerRep, F&& body) {
  const int trials = 7;
  double bestUs = -1;
  for (int t = 0; t < trials; ++t) {
    auto t0 = Clock::now();
    for (int rep = 0; rep < reps; ++rep) body();
    auto t1 = Clock::now();
    double us = std::chrono::duration<double, std::micro>(t1 - t0).count();
    if (bestUs < 0 || us < bestUs) bestUs = us;
  }
  long long totalCalls = callsPerRep * reps;
  std::printf("%-16s best of %d: %.4f ns/call\n", label, trials,
              totalCalls ? (bestUs * 1000.0 / totalCalls) : 0.0);
}

// A volatile accumulator: every variant (including baseline) must write to
// this from inside the lambda, so all variants pay the SAME real per-mask
// side-effect cost and the compiler can't dead-code-eliminate the whole
// recursive walk (caught this: an early version of this benchmark had a
// truly-no-op baseline lambda, and the baseline measured 0.0000 ns/call --
// the optimizer had proven the entire forEachViableMask call had no
// observable effect and deleted it outright, invalidating the comparison).
static volatile unsigned g_sink = 0;

// A local copy of s8::viableRec (core/transition.h) with ONE added check at
// the top of the function: this is the version that could actually abort a
// pathological tree walk early (a lambda-side check, benchmarked above,
// cannot -- returning from the lambda doesn't stop viableRec's SIBLING
// branches from being explored). Copied here rather than modifying the
// production file, so this stays a pure measurement with zero risk to the
// real code until a decision is made from real numbers.
template <class M, class F>
static void viableRecChecked(int r, int H, M mask, int bits, std::uint32_t cov,
                              std::uint32_t all, const std::uint32_t* rowSup,
                              const std::uint32_t* sufSup, int budget,
                              bool topBase, F& fn) {
  if (g_terminate) return;  // <-- the one added line
  if ((cov | sufSup[r]) != all) return;
  if (!(topBase || (mask & 1u))) {
    const int lbTop =
        mask ? __builtin_ctzll(static_cast<unsigned long long>(mask)) : r;
    if (bits + lbTop > budget) return;
  }
  if (r == H) {
    if (mask) fn(mask);
    return;
  }
  viableRecChecked(r + 1, H, mask, bits, cov, all, rowSup, sufSup, budget, topBase, fn);
  if (bits + 1 <= budget)
    viableRecChecked(r + 1, H, static_cast<M>(mask | (M(1) << r)), bits + 1,
                      cov | rowSup[r], all, rowSup, sufSup, budget, topBase, fn);
}

template <class M = unsigned, class F>
static void forEachViableMaskChecked(const Sig& old, int H, int budget, F&& fn) {
  std::uint32_t all = 0, rowSup[SIGMAX], sufSup[SIGMAX + 1];
  for (int i = 0; i < H; ++i)
    if (old.b[i]) all |= 1u << old.b[i];
  for (int r = 0; r < H; ++r) {
    std::uint32_t s = 0;
    for (int rr = r - 1; rr <= r + 1; ++rr)
      if (rr >= 0 && rr < H && old.b[rr]) s |= 1u << old.b[rr];
    rowSup[r] = s;
  }
  sufSup[H] = 0;
  for (int r = H - 1; r >= 0; --r) sufSup[r] = sufSup[r + 1] | rowSup[r];
  viableRecChecked<M>(0, H, M(0), 0, 0u, all, rowSup, sufSup, budget, old.b[H] != 0, fn);
}

// Count recursive NODE visits (not just emitted leaves) to show why a
// per-node check is a different cost profile than a per-leaf check.
static long long countNodes(int r, int H, unsigned mask, int bits, std::uint32_t cov,
                             std::uint32_t all, const std::uint32_t* rowSup,
                             const std::uint32_t* sufSup, int budget, bool topBase) {
  if ((cov | sufSup[r]) != all) return 1;
  if (!(topBase || (mask & 1u))) {
    const int lbTop = mask ? __builtin_ctzll(static_cast<unsigned long long>(mask)) : r;
    if (bits + lbTop > budget) return 1;
  }
  if (r == H) return 1;
  long long n = 1;
  n += countNodes(r + 1, H, mask, bits, cov, all, rowSup, sufSup, budget, topBase);
  if (bits + 1 <= budget)
    n += countNodes(r + 1, H, mask | (1u << r), bits + 1, cov | rowSup[r], all,
                     rowSup, sufSup, budget, topBase);
  return n;
}

int main() {
  const int H = 20;
  Sig sig = makeSig(H);
  const int budget = H; // generous, allow most masks to be viable
  const int reps = 2000;

  // Count calls once up front (same every rep, deterministic).
  long long callsPerRep = 0;
  forEachViableMask(sig, H, budget, [&](unsigned) { ++callsPerRep; });

  bench("baseline", reps, callsPerRep, [&] {
    forEachViableMask(sig, H, budget, [&](unsigned m) { g_sink = m; });
  });

  bench("per-mask check", reps, callsPerRep, [&] {
    forEachViableMask(sig, H, budget, [&](unsigned m) {
      if (g_terminate) return;
      g_sink = m;
    });
  });

  for (int K : {16, 64, 256, 1024}) {
    unsigned counter = 0;
    char label[32];
    std::snprintf(label, sizeof(label), "K=%d check", K);
    bench(label, reps, callsPerRep, [&] {
      counter = 0;
      forEachViableMask(sig, H, budget, [&](unsigned m) {
        if ((++counter & (K - 1)) == 0 && g_terminate) return;
        g_sink = m;
      });
    });
  }

  std::uint32_t all = 0, rowSup[SIGMAX], sufSup[SIGMAX + 1];
  for (int i = 0; i < H; ++i)
    if (sig.b[i]) all |= 1u << sig.b[i];
  for (int r = 0; r < H; ++r) {
    std::uint32_t s = 0;
    for (int rr = r - 1; rr <= r + 1; ++rr)
      if (rr >= 0 && rr < H && sig.b[rr]) s |= 1u << sig.b[rr];
    rowSup[r] = s;
  }
  sufSup[H] = 0;
  for (int r = H - 1; r >= 0; --r) sufSup[r] = sufSup[r + 1] | rowSup[r];
  long long nodes = countNodes(0, H, 0u, 0, 0u, all, rowSup, sufSup, budget, sig.b[H] != 0);
  std::printf("(tree nodes visited per call: %lld, vs %lld emitted leaves -- ratio %.1fx)\n",
              nodes, callsPerRep, callsPerRep ? double(nodes) / double(callsPerRep) : 0.0);

  bench("recursion check", reps, callsPerRep, [&] {
    forEachViableMaskChecked(sig, H, budget, [&](unsigned m) { g_sink = m; });
  });

  return 0;
}
