// worker_util.h — small shared helpers for the thin worker CLIs (M1).
//
// argv plumbing + rusage/timing readouts used identically by map_worker and
// merge_worker (and the serial driver). Kept header-only and dependency-free
// beyond libc so the workers stay thin.

#pragma once

#include <cstring>
#include <ctime>
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
