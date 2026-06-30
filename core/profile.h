// profile.h — opt-in phase timers for the workers (Track B; designs/11,12).
//
// ALL code here is behind POLY_PROFILE. The production build never defines it,
// so map_shard_file / mergeRunFiles compile byte-identically without it — zero
// hot-path overhead. Build a throwaway profiling binary with -DPOLY_PROFILE to
// get per-phase wall-time + counters appended to $POLY_PROFILE_OUT (one line per
// map/merge invocation), used only by the dedicated small-n profiling runs.
#pragma once

#ifdef POLY_PROFILE
#include <cstdio>
#include <cstdlib>
#include <ctime>
#include <sys/resource.h>

namespace prof {

inline double now() {
  struct timespec ts;
  clock_gettime(CLOCK_MONOTONIC, &ts);
  return static_cast<double>(ts.tv_sec) + static_cast<double>(ts.tv_nsec) * 1e-9;
}

inline double peakRssMB() {
  struct rusage ru;
  getrusage(RUSAGE_SELF, &ru);
#ifdef __APPLE__
  return static_cast<double>(ru.ru_maxrss) / (1024.0 * 1024.0);
#else
  return static_cast<double>(ru.ru_maxrss) / 1024.0;
#endif
}

// Append one profile line to $POLY_PROFILE_OUT (fallback: stderr).
inline void emit(const char* line) {
  const char* p = std::getenv("POLY_PROFILE_OUT");
  FILE* f = p ? std::fopen(p, "a") : stderr;
  if (!f) f = stderr;
  std::fprintf(f, "%s\n", line);
  if (p && f != stderr) std::fclose(f);
}

inline const char* site() {
  const char* s = std::getenv("POLY_PROFILE_SITE");
  return s ? s : "merge";
}

}  // namespace prof
#endif  // POLY_PROFILE
