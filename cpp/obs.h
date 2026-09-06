// Observability & provenance for the C++ engines -- the compiled-language half
// of docs/observability.md, emitting the SAME logfmt event stream as the Python
// scripts/obs.py so a job's log alone answers "what code, alive, how far, when done".
//
// Provenance is baked at BUILD time (GIT_REV / BUILD_TIME via -D in the Makefile):
// a binary outlives its source, so it reports the commit it was *built* at, not
// the tree's state now. Absent the -D defines it falls back to "unknown".
//
// Events go to STDERR. The engines' stdout is a pure data stream consumed by the
// Python parsers (which `int()` each token), so a banner line there would crash
// them -- provenance rides the stderr event stream instead, never stdout.
//
// Header-only, stdlib + POSIX (getrusage / gethostname) only; compiles on gympie
// (macOS/clang) and ayr (Linux/gcc), the one fork being ru_maxrss's units.

#pragma once

#include <chrono>
#include <cstdio>
#include <cstdlib>
#include <ctime>
#include <string>
#include <sys/resource.h>
#include <unistd.h>

#ifndef GIT_REV
#define GIT_REV "unknown"
#endif
#ifndef BUILD_TIME
#define BUILD_TIME "unknown"
#endif

namespace obs {

// ISO-8601 to the second WITH local tz offset, colon form (2026-06-20T15:30:00-04:00)
// -- matches scripts/obs.py so a cross-machine log diff is clean. strftime's %z gives the
// basic "-0400"; we splice the colon in to mirror Python's isoformat.
inline std::string iso_of(std::time_t t) {
  std::tm tm{};
  localtime_r(&t, &tm);
  char buf[40];
  const size_t len =
      std::strftime(buf, sizeof buf, "%Y-%m-%dT%H:%M:%S%z", &tm);
  if (len >= 5) {  // -0400 -> -04:00 (in the buffer: string::insert trips
    buf[len + 1] = '\0';  // GCC 12's bogus -Wrestrict, PR 105651)
    buf[len] = buf[len - 1];
    buf[len - 1] = buf[len - 2];
    buf[len - 2] = ':';
  }
  return std::string(buf);
}
inline std::string now_iso() { return iso_of(std::time(nullptr)); }

inline std::string host() {
  char h[256];
  return gethostname(h, sizeof h) == 0 ? std::string(h) : std::string("unknown");
}

// CPU seconds (self + waited children) and peak RSS in MB. The one cross-platform
// fork: ru_maxrss is *bytes* on macOS, *kilobytes* on Linux.
inline double cpu_s() {
  auto sec = [](const timeval& tv) { return tv.tv_sec + tv.tv_usec * 1e-6; };
  rusage s{}, c{};
  getrusage(RUSAGE_SELF, &s);
  getrusage(RUSAGE_CHILDREN, &c);
  return sec(s.ru_utime) + sec(s.ru_stime) + sec(c.ru_utime) + sec(c.ru_stime);
}
inline double rss_mb() {
  rusage s{};
  getrusage(RUSAGE_SELF, &s);
#ifdef __APPLE__
  return s.ru_maxrss / (1024.0 * 1024.0);
#else
  return s.ru_maxrss / 1024.0;
#endif
}

// Emits the start / heartbeat / done event stream for one run. The `extra`
// arguments are pre-formatted logfmt fragments ("threads=6 height=19") the caller
// builds -- keeps this dependency-free of variadic machinery.
struct Reporter {
  std::string job, startWall;
  double total;                                  // 0 => denominator unknown
  std::chrono::steady_clock::time_point t0, lastBeat;
  double heartbeatS;

  Reporter(const std::string& job_, double total_ = 0,
           const std::string& startExtra = "")
      : job(job_), total(total_),
        t0(std::chrono::steady_clock::now()), lastBeat(t0) {
    const char* hb = std::getenv("POLY_HEARTBEAT_S");
    heartbeatS = hb ? std::atof(hb) : 45.0;
    startWall = now_iso();
    std::fprintf(stderr, "event=start job=%s t=%s git=%s built=%s host=%s",
                 job.c_str(), startWall.c_str(), GIT_REV, BUILD_TIME, host().c_str());
    if (total > 0) std::fprintf(stderr, " total=%g", total);
    if (!startExtra.empty()) std::fprintf(stderr, " %s", startExtra.c_str());
    std::fputc('\n', stderr);
    std::fflush(stderr);
  }

  double elapsed() const {
    return std::chrono::duration<double>(
               std::chrono::steady_clock::now() - t0).count();
  }

  // Throttled to heartbeatS wall-clock seconds (force=true overrides). `done` is
  // work units so far; with a known total the line carries fraction + a
  // self-computed ETA, else a monotonic counter. Returns true if it emitted.
  bool beat(double done, const std::string& extra = "", bool force = false) {
    auto now = std::chrono::steady_clock::now();
    if (!force &&
        std::chrono::duration<double>(now - lastBeat).count() < heartbeatS)
      return false;
    lastBeat = now;
    const double el = elapsed();
    std::fprintf(stderr, "event=heartbeat job=%s t=%s elapsed_s=%.1f",
                 job.c_str(), now_iso().c_str(), el);
    const double rate = (done > 0 && el > 0) ? done / el : 0;
    if (rate > 0) std::fprintf(stderr, " rate=%.4g/s", rate);
    if (total > 0) {
      std::fprintf(stderr, " done=%.4f", done / total);
      if (rate > 0 && done < total)
        std::fprintf(stderr, " eta=%s",
                     iso_of(std::time(nullptr) +
                            static_cast<std::time_t>((total - done) / rate))
                         .c_str());
    } else if (done > 0) {
      std::fprintf(stderr, " count=%.0f", done);
    }
    if (!extra.empty()) std::fprintf(stderr, " %s", extra.c_str());
    std::fputc('\n', stderr);
    std::fflush(stderr);
    return true;
  }

  // The canonical ledger line: restates absolute start, so wall is done.t-start.t
  // from the log alone, plus the key cost metrics. resultKV/extra are logfmt.
  void done(const std::string& resultKV, const std::string& extra = "") {
    std::fprintf(stderr,
                 "event=done job=%s t=%s start=%s wall_s=%.1f cpu_s=%.1f "
                 "peak_rss_mb=%.1f",
                 job.c_str(), now_iso().c_str(), startWall.c_str(), elapsed(),
                 cpu_s(), rss_mb());
    if (!resultKV.empty()) std::fprintf(stderr, " %s", resultKV.c_str());
    if (!extra.empty()) std::fprintf(stderr, " %s", extra.c_str());
    std::fputc('\n', stderr);
    std::fflush(stderr);
  }
};

}  // namespace obs
