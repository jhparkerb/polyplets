// merge_worker.cpp — thin CLI wrapper for mergeRunFiles (DESIGN §8, T1.2).
//
// Usage:
//   merge_worker --in PATH[,PATH,...] --H N --out PATH
//                [--counter u64|u128] [--klo HEX] [--khi HEX] [--rev GITREV]
//                [--keylen N]
//
// K-way merges a set of sorted POLYRUN files into one output file, optionally
// restricting to the output key range [klo, khi).  Pure function of inputs
// (idempotent, safe to re-run on resume).
//
// --keylen overrides the run's key width in bytes; 0 (default, unset) keeps
// mergeRunFiles's own H+2 derivation (the column kernel's end-of-column
// sigs). The kink kernel's mixed-state stage tables are keyed on H+4 and
// pass --keylen explicitly — merge_worker itself has no kernel awareness,
// it just merges whatever fixed-width keys the caller tells it about.
//
// --persistent: read one whitespace-tokenized request per line from stdin
// and process it, looping until EOF, instead of a single argv-derived
// request -- eliminates the fork+exec cost paid on every single merge
// range (see map_worker.cpp's runOneRequest comment for the full
// rationale; same fix, same reasoning, applied here).

#include <cctype>
#include <csignal>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <iostream>
#include <string>
#include <vector>

#include "core/fdlimit.h"
#include "core/libenum.h"
#include "worker/worker_util.h"

// SIGTERM handling (cooperative work-stealing stop) is shared with
// map_worker.cpp: see worker_util.h's g_workerTerminate/
// installWorkerSigtermHandler. mergeRunFiles' resume semantics are simpler
// than map's -- see core/runfile.h's comment on the terminate/
// stop_key_out params -- stopping early just means "re-merge with
// lo_hex=stop_key," no partial-tree-state problem to solve.

// runOneRequest does everything a one-shot merge_worker invocation always
// did: parse one request's args, merge the shard files, emit accounting.
// `tokens` is the flag/value list with no program name.
static int runOneRequest(const std::vector<std::string>& tokens) {
  std::string in_str, out_path, klo_hex, khi_hex, rev;
  std::string counter_arg = "u64";
  int H = 0;
  int keyLen = 0;

  const int n = static_cast<int>(tokens.size());
  for (int i = 0; i < n; ++i) {
    auto arg = [&](const char* flag) {
      return tokens[i] == flag && i + 1 < n;
    };
    if (arg("--in"))           in_str      = tokens[++i];
    else if (arg("--H"))       H           = std::atoi(tokens[++i].c_str());
    else if (arg("--out"))     out_path    = tokens[++i];
    else if (arg("--counter")) counter_arg = tokens[++i];
    else if (arg("--klo"))     klo_hex     = tokens[++i];
    else if (arg("--khi"))     khi_hex     = tokens[++i];
    else if (arg("--rev"))     rev         = tokens[++i];
    else if (arg("--keylen"))  keyLen      = std::atoi(tokens[++i].c_str());
    else {
      std::fprintf(stderr, "merge_worker: unknown arg: %s\n", tokens[i].c_str());
      return 1;
    }
  }

  if (in_str.empty() || H <= 0 || out_path.empty()) {
    std::fprintf(stderr, "merge_worker: required: --in --H --out\n");
    return 1;
  }
  if (counter_arg != "u64" && counter_arg != "u128") {
    std::fprintf(stderr, "merge_worker: --counter must be u64 or u128\n");
    return 1;
  }

  const auto in_paths = splitComma(in_str);

  const double t0_wall = wallSeconds();
  const double t0_cpu  = cpuSeconds();

  // Throttled progress emitter (worker_util.h): first call fires
  // immediately (not gated by elapsed time), so a merge range's
  // processed>0 becomes visible to the orchestrator's stealEligible within
  // one progress stride, not up to 2s late.
  ThrottledProgressEmitter on_progress(t0_wall);

  size_t body_bytes, out_recs;
  std::string stop_key;  // set iff SIGTERM stopped us early (work-stealing cursor)
  if (counter_arg == "u128") {
    std::tie(body_bytes, out_recs) = mergeRunFiles<u128>(
        in_paths, H, klo_hex, khi_hex, out_path, rev, keyLen,
        on_progress, &g_workerTerminate, &stop_key);
  } else {
    std::tie(body_bytes, out_recs) = mergeRunFiles<u64>(
        in_paths, H, klo_hex, khi_hex, out_path, rev, keyLen,
        on_progress, &g_workerTerminate, &stop_key);
  }

  const double cpu_s  = cpuSeconds()  - t0_cpu;
  const double wall_s = wallSeconds() - t0_wall;
  const double rss_mb = peakRssMB();

  // stop_key non-empty iff SIGTERM stopped us early (work-stealing cursor):
  // the output covers [klo, stop_key) and the orchestrator requeues
  // [stop_key, khi) -- same accounting-line contract as map_worker.cpp.
  std::printf("event=done cpu_s=%.3f wall_s=%.3f peak_rss_mb=%.1f "
              "records=%zu spill_bytes=%zu stop_key=%s\n",
              cpu_s, wall_s, rss_mb, out_recs, body_bytes, stop_key.c_str());
  return 0;
}

// Whitespace-split a stdin request line into tokens (paths never contain
// spaces -- see map_worker.cpp's tokenizeLine for the same contract).
static std::vector<std::string> tokenizeLine(const std::string& line) {
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

int main(int argc, char** argv) {
  raiseFdLimitToHard();  // the spill/merge path fans out to many open files
  installWorkerSigtermHandler();

  std::vector<std::string> tokens(argv + 1, argv + argc);
  bool persistent = false;
  std::vector<std::string> filtered;
  filtered.reserve(tokens.size());
  for (auto& t : tokens) {
    if (t == "--persistent") persistent = true;
    else filtered.push_back(t);
  }

  if (!persistent) return runOneRequest(filtered);

  std::string line;
  while (std::getline(std::cin, line)) {
    if (line.empty()) continue;
    g_workerTerminate = 0;  // a prior request's SIGTERM must not bleed into the next
    const int rc = runOneRequest(tokenizeLine(line));
    if (rc != 0) return rc;
    std::fflush(stdout);
  }
  return 0;
}
