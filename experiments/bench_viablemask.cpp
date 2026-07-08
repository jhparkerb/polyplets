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

// NOTE (trimmed via /simplify): an earlier version of this file also
// carried a local copy of s8::viableRec with an added per-node check
// (viableRecChecked/forEachViableMaskChecked) plus a countNodes tree-visit
// counter, to test whether a recursion-level interrupt point was cheap
// enough to be worth building for forEachViableMask. Since this whole file
// is now WRONG TARGET (see the header note -- kink's real hot path,
// kinkStageTransition, has no recursive tree to interrupt at all), that
// apparatus was exploratory scaffolding for a question that no longer
// applies here, not part of the reusable benchmark methodology. Dropped
// rather than kept as dead code; git history has the full version if
// someone building a kinkStageTransition-targeted benchmark wants the
// pattern for reference.

int main() {
  const int H = 20;
  Sig sig = makeSig(H);
  const int budget = H; // generous, allow most masks to be viable
  // reps=50 (was 2000): at H=20 each forEachViableMask call visits ~2M tree
  // nodes (see the emitted ratio line), so 2000 reps x 7 trials x 6 variants
  // was ~168B node visits -- several CPU-minutes for a "throwaway, iterate
  // fast" benchmark. min-of-N-trials only needs enough reps per trial to
  // amortize timer overhead, not thousands; found while re-verifying this
  // file post-/simplify (it looked hung, wasn't -- just this expensive).
  const int reps = 50;

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

  return 0;
}
