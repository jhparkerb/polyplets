// worker_util.h — small shared helpers for the thin worker CLIs (M1).
//
// argv plumbing + rusage/timing readouts used identically by map_worker and
// merge_worker (and the serial driver). Kept header-only and dependency-free
// beyond libc so the workers stay thin.

#pragma once

#include <cctype>
#include <csignal>
#include <cstdio>
#include <cstdlib>
#ifdef __GLIBC__
#include <malloc.h>
#endif
#include <cstring>
#include <ctime>
#include <functional>
#include <string>
#include <vector>

#include <sys/resource.h>

// Split a comma-separated path list ("a,b,c") into its parts.
inline std::vector<std::string> splitComma(const std::string& s) {
  std::vector<std::string> parts;
  size_t start = 0;
  while (true) {
    size_t pos = s.find(',', start);
    if (pos == std::string::npos) {
      parts.push_back(s.substr(start));
      break;
    }
    parts.push_back(s.substr(start, pos - start));
    start = pos + 1;
  }
  return parts;
}

// Monotonic wall-clock seconds (for elapsed timing).
inline double wallSeconds() {
  struct timespec ts;
  clock_gettime(CLOCK_MONOTONIC, &ts);
  return static_cast<double>(ts.tv_sec) + static_cast<double>(ts.tv_nsec) * 1e-9;
}

// Process CPU seconds (user + system) so far.
inline double cpuSeconds() {
  struct rusage ru;
  getrusage(RUSAGE_SELF, &ru);
  return static_cast<double>(ru.ru_utime.tv_sec) +
         static_cast<double>(ru.ru_utime.tv_usec) * 1e-6 +
         static_cast<double>(ru.ru_stime.tv_sec) +
         static_cast<double>(ru.ru_stime.tv_usec) * 1e-6;
}

// Print an unsigned __int128 as decimal.  Returns pointer into buf[0..41).
inline const char* u128Dec(unsigned __int128 v, char buf[41]) {
  buf[40] = '\0';
  int pos = 40;
  if (v == 0) { buf[--pos] = '0'; return buf + pos; }
  while (v > 0) { buf[--pos] = '0' + static_cast<int>(v % 10); v /= 10; }
  return buf + pos;
}

// Emit "tri H n value\n" for every nonzero entry in a TriangleRow.
template <class T>
inline void printTriangleRows(int H, int maxn, const std::vector<T>& row) {
  char buf[41];
  for (int n = 1; n <= maxn; ++n) {
    if (row[n] == T{0}) continue;
    if constexpr (sizeof(T) == 16)
      std::printf("tri %d %d %s\n", H, n, u128Dec(row[n], buf));
    else
      std::printf("tri %d %d %llu\n", H, n, (unsigned long long)row[n]);
  }
}

// Emit "holes H n k count\n" for every nonzero entry in a HolesRow.
template <class T>
inline void printHolesRows(int H, int maxn, const std::vector<std::vector<T>>& byNHoles) {
  char buf[41];
  for (int n = 1; n <= maxn; ++n) {
    if (n >= static_cast<int>(byNHoles.size())) break;
    for (int k = 0; k < static_cast<int>(byNHoles[n].size()); ++k) {
      if (byNHoles[n][k] == T{0}) continue;
      if constexpr (sizeof(T) == 16)
        std::printf("holes %d %d %d %s\n", H, n, k, u128Dec(byNHoles[n][k], buf));
      else
        std::printf("holes %d %d %d %llu\n", H, n, k,
                    (unsigned long long)byNHoles[n][k]);
    }
  }
}

// Peak resident set size in MB. ru_maxrss is bytes on macOS, KB on Linux.
inline double peakRssMB() {
  struct rusage ru;
  getrusage(RUSAGE_SELF, &ru);
#ifdef __APPLE__
  return static_cast<double>(ru.ru_maxrss) / (1024.0 * 1024.0);
#else
  return static_cast<double>(ru.ru_maxrss) / 1024.0;
#endif
}

// ─── SIGTERM handling: cooperative work-stealing stop ────────────────────────
// Shared by map_worker.cpp and merge_worker.cpp (identical in both before
// this extraction): the orchestrator raises SIGTERM to ask a straggler unit
// to stop early and hand its remainder to idle cores. `g_workerTerminate`
// (a `volatile sig_atomic_t`, the only signal-safe flag width) is checked
// cooperatively inside the hot loop; the SIGTERM handler itself just sets
// the flag, does not exit -- a clean, successful stop (status 0) is
// distinct from a hard SIGKILL (uncatchable, discards the partial output
// for a later --resume). Each worker binary gets its own copy of this flag
// (separate processes, separate translation units), so no cross-binary
// aliasing risk despite the shared header.
inline volatile std::sig_atomic_t g_workerTerminate = 0;
inline void onWorkerSigterm(int) { g_workerTerminate = 1; }
inline void installWorkerSigtermHandler() {
  std::signal(SIGTERM, onWorkerSigterm);
}

// Throttled progress emitter: at most one "event=progress processed=N
// elapsed_s=T" line every ~2s, EXCEPT the very first call, which fires
// immediately regardless of elapsed time. The orchestrator streams these
// to drive the within-column heartbeat AND gates work-stealing eligibility
// on processed>0 (stealEligible, orchestrator/sweep.go) -- with a flat 2s
// throttle including the first call, any unit whose whole runtime fell
// under 2s reported processed=0 for its entire life, making it permanently
// un-stealable no matter how much of the pool was waiting on it (found
// investigating why work-stealing measured near-zero even with an idle
// pool and a lone straggler: picked=false because processed=0 the whole
// time). Construct one per request (not once per process): `t0` should be
// the request's own start time, and `emitted_once` must reset per request
// so a fast request doesn't inherit a slow one's "already emitted" state.
class ThrottledProgressEmitter {
 public:
  explicit ThrottledProgressEmitter(double t0) : t0_(t0), lastEmit_(t0) {}

  void operator()(size_t processed) {
    const double now = wallSeconds();
    if (!emittedOnce_ || now - lastEmit_ >= 2.0) {
      emittedOnce_ = true;
      lastEmit_ = now;
      std::printf("event=progress processed=%zu elapsed_s=%.1f\n", processed, now - t0_);
      std::fflush(stdout);
    }
  }

 private:
  double t0_;
  double lastEmit_;
  bool emittedOnce_ = false;
};

// Whitespace-split a stdin request line into tokens. Paths in this codebase
// are always constructed (run-dir/spill-dir-relative filenames), never
// contain spaces, so this simple split is exact -- no quoting support
// needed, matching argv's own space-delimited contract for the same flag
// set used one-shot.
inline std::vector<std::string> tokenizeLine(const std::string& line) {
  std::vector<std::string> tokens;
  size_t i = 0;
  while (i < line.size()) {
    while (i < line.size() && std::isspace(static_cast<unsigned char>(line[i]))) ++i;
    size_t start = i;
    while (i < line.size() && !std::isspace(static_cast<unsigned char>(line[i]))) ++i;
    if (i > start) tokens.push_back(line.substr(start, i - start));
  }
  return tokens;
}

// Shared driver for both worker CLIs' main(): parses argv for --persistent,
// and either runs runOneRequest once (one-shot, the original per-process
// contract) or loops over stdin lines calling it (persistent mode,
// resetting g_workerTerminate between requests so a prior request's
// SIGTERM doesn't bleed into the next -- see g_workerTerminate's comment).
// Callers still call installWorkerSigtermHandler() and raiseFdLimitToHard()
// themselves before this (the latter kept out of worker_util.h to preserve
// its "no core/ dependency" contract stated at the top of this file).
inline int runWorkerMain(
    int argc, char** argv,
    const std::function<int(const std::vector<std::string>&)>& runOneRequest) {
  std::vector<std::string> tokens(argv + 1, argv + argc);
  bool persistent = false;
  std::vector<std::string> filtered;
  filtered.reserve(tokens.size());
  for (auto& t : tokens) {
    if (t == "--persistent") persistent = true;
    else filtered.push_back(t);
  }

  if (!persistent) return runOneRequest(filtered);

  // POSIX getline, not std::getline(std::cin): cin's stdio_sync_filebuf pulls
  // one BYTE per virtual underflow call, and a merge request line listing
  // every map output of a round runs to tens of KB — measured as a top-3
  // merge_worker cost at fan-in scale (Fan-In Tax, results/fanin-tax.md).
  char* line = nullptr;
  size_t cap = 0;
  ssize_t n;
  while ((n = getline(&line, &cap, stdin)) != -1) {
    while (n > 0 && (line[n - 1] == '\n' || line[n - 1] == '\r')) line[--n] = '\0';
    if (n == 0) continue;
    g_workerTerminate = 0;
    const int rc = runOneRequest(tokenizeLine(line));
    if (rc != 0) { std::free(line); return rc; }  // real failure exits, same as one-shot
    std::fflush(stdout);
#ifdef __GLIBC__
    // Return freed arena pages to the OS between requests. A persistent
    // worker otherwise RETAINS its peak heap forever: after a big H20 round,
    // 64 idle merge workers each held ~1GB while the 64 map workers ran
    // their own ~1.3GB round — the two fleets' retained peaks summed past
    // 125GB and the kernel OOM killer fired (5th a(40) death, 2026-07-26;
    // results/overcommit-hydra.md). Cost: ~ms per request, paid off-round.
    malloc_trim(0);
#endif
  }
  std::free(line);
  return 0;
}
