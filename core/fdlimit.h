// fdlimit.h — raise the open-file soft limit to the hard limit at startup.
//
// The spill/merge path opens one file per run-shard, and a heavily-fanned-out
// merge (small --ram budget → many tiny spill files) can need thousands of
// simultaneous descriptors. The default soft limit is often 1024 (Debian), far
// below that. Exceeding it makes fopen() fail; combined with fail-closed
// spill I/O that means the run ABORTS rather than silently undercounts — but
// aborting a multi-hour frontier run over a limit we can lift for free is
// pure waste. Raising the soft limit up to the hard limit needs no privilege
// (POSIX lets any process raise soft up to hard), so every spill-touching
// binary calls this from main() before it starts opening files.
#pragma once

#include <cstdio>
#include <sys/resource.h>

// Best-effort: raise RLIMIT_NOFILE soft to the hard cap. Never fatal — a
// failure here just leaves the inherited limit in place (and fail-closed I/O
// will still abort loudly rather than corrupt if that limit is later hit).
inline void raiseFdLimitToHard() {
  struct rlimit rl;
  if (getrlimit(RLIMIT_NOFILE, &rl) != 0) return;
  if (rl.rlim_cur == rl.rlim_max) return;  // already maxed
  const rlim_t want = rl.rlim_max;
  rl.rlim_cur = want;
  if (setrlimit(RLIMIT_NOFILE, &rl) != 0) {
    std::fprintf(stderr, "raiseFdLimitToHard: setrlimit failed; "
                         "leaving open-file limit as inherited\n");
  }
}
