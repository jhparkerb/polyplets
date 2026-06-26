// proctitle -- rewrite the process title so htop/ps shows what the engine is
// doing at a glance: "tma a(21) H20 c=12/21 ~63%" (term, strip height, column,
// and within-column shard progress). Deliberately NO resident size -- htop has
// that as a column already.
//
// Mechanism (Linux, where the heavy jobs run): overwrite the contiguous argv
// block in place (capped to its own length so we never run into envp) and set
// the 15-char `comm` once via prctl. On macOS/other it's a best-effort no-op --
// the long runs are on the Linux boxes.
//
// Cost: the engine pokes a few relaxed atomics (one fetch_add per *shard*, i.e.
// S~512-4096 times per column, not per state) and a detached thread rewrites the
// title every ~1.5 s. Negligible against the sweep, and harmless when no updater
// is running (the atomics just increment with no reader).
#pragma once
#include <atomic>
#include <chrono>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <string>
#include <thread>
#if defined(__linux__)
#include <sys/prctl.h>
#endif

// TODO(simplify): this is an engine-agnostic util (argv-overwrite + prctl + a refresh
// thread) parked under tma/ with a tma-specific format string. It could live beside obs.h
// with a caller-supplied label so other long opaque runs (e.g. g2_redelmeier) can reuse it.
namespace proctitle {
using u64 = std::uint64_t;

// --- progress the engine pokes (cheap relaxed atomics) ---
inline std::atomic<int> g_col{0};       // current column (1..maxn)
inline std::atomic<int> g_maxn{0};      // total columns (= N)
inline std::atomic<u64> g_shardDone{0}; // shards finished this column
inline std::atomic<u64> g_shardTot{0};  // shards per column (0 => no within-col bar)

inline void setCol(int col) { g_col.store(col, std::memory_order_relaxed); }
inline void setShardTotal(u64 s) { g_shardTot.store(s, std::memory_order_relaxed); }
inline void resetShards() { g_shardDone.store(0, std::memory_order_relaxed); }
inline void shardDone() { g_shardDone.fetch_add(1, std::memory_order_relaxed); }

// --- argv region captured at init ---
inline char* g_argv0 = nullptr;
inline size_t g_argvLen = 0;
inline std::atomic<bool> g_stop{false};

// Capture the writable argv span. Call once at the top of main(), before the
// updater starts overwriting it (arg parsing has read argv by then).
inline void init(int argc, char** argv) {
#if defined(__linux__)
  if (argc < 1 || !argv[argc - 1]) return;
  char* end = argv[argc - 1] + std::strlen(argv[argc - 1]) + 1;  // through last arg's NUL
  g_argv0 = argv[0];
  g_argvLen = static_cast<size_t>(end - argv[0]);
#else
  (void)argc;
  (void)argv;
#endif
}

inline void setTitle(const std::string& s) {
#if defined(__linux__)
  if (!g_argv0 || !g_argvLen) return;
  size_t n = s.size() < g_argvLen - 1 ? s.size() : g_argvLen - 1;
  std::memcpy(g_argv0, s.data(), n);
  std::memset(g_argv0 + n, 0, g_argvLen - n);  // NUL-pad so the old args don't bleed through
#else
  (void)s;
#endif
}

inline std::string format(int N, int H) {
  char buf[96];
  const int col = g_col.load(std::memory_order_relaxed);
  const int maxn = g_maxn.load(std::memory_order_relaxed);
  const u64 sd = g_shardDone.load(std::memory_order_relaxed);
  const u64 st = g_shardTot.load(std::memory_order_relaxed);
  // NB: no '/' anywhere in the title -- htop/btop strip the program path by default and a
  // slash (e.g. "c=3/21") gets mistaken for a path separator, truncating the display to the
  // "basename" after it ("21 ~87%"). Use ':' for the column-of-total separator instead.
  if (st > 0)
    std::snprintf(buf, sizeof buf, "tma a(%d) H%d c=%d:%d ~%d%%", N, H, col, maxn,
                  static_cast<int>(sd * 100 / st));
  else
    std::snprintf(buf, sizeof buf, "tma a(%d) H%d c=%d:%d", N, H, col, maxn);
  return buf;
}

// Start a detached updater that rewrites the title every `ms` until stop().
// Returns the thread (join via stop()).
inline std::thread start(int N, int H, int maxn, int ms = 1500) {
  g_maxn.store(maxn, std::memory_order_relaxed);
  g_col.store(0, std::memory_order_relaxed);
  g_shardTot.store(0, std::memory_order_relaxed);
  g_shardDone.store(0, std::memory_order_relaxed);
  g_stop.store(false, std::memory_order_relaxed);
#if defined(__linux__)
  char comm[16];
  std::snprintf(comm, sizeof comm, "tma-a%d-H%d", N, H);  // 15-char `comm`, set once
  prctl(PR_SET_NAME, comm, 0, 0, 0);
#endif
  setTitle(format(N, H));  // immediate, before the first sleep
  return std::thread([=] {
    while (!g_stop.load(std::memory_order_relaxed)) {
      std::this_thread::sleep_for(std::chrono::milliseconds(ms));
      setTitle(format(N, H));
    }
  });
}

inline void stop(std::thread& t) {
  g_stop.store(true, std::memory_order_relaxed);
  if (t.joinable()) t.join();
}

}  // namespace proctitle
