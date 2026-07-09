// worker_io.h — shared POLYRUN read/write helpers for the kink kernel's
// in-RAM worker steps (seed, finalize, and now the fused stage worker).
//
// readRangedRunFiles/writeRunFile were originally private statics inside
// map_worker.cpp (used only by its --kernel kink --stage seed/finalize
// paths). Even Keel D6's fused_stage.cpp needs the exact same read/write
// contract (same range-filter semantics, same .idx-sidecar-writing writer,
// so the next round's BalancedCutsMulti/SampleKeysMulti sees a normal
// POLYRUN file either way) — pulled out here so both workers share one
// implementation instead of two independently-maintained copies.

#pragma once

#include <string>
#include <vector>

#include "core/run.h"
#include "core/runfile.h"
#include "core/signature.h"

// Read+range-filter+merge a set of POLYRUN files into one sorted,
// deduplicated in-RAM Run<W>, keyed at `keyLen`. Mirrors map_shard_file's
// read side (core/mapreduce.h) without the transition -- just merge-by-key
// over the input files, combining any same-key records across files
// (deduplicateRun's combine(), same as map_shard_stage_file's K-way heap
// combine step, just via sort+dedup on an in-RAM Run instead of a heap).
template <class W>
Run<W> readRangedRunFiles(const std::vector<std::string>& paths, int H,
                          int keyLen, const std::string& lo_hex,
                          const std::string& hi_hex) {
  uint8_t lo_sig[SIGMAX] = {};
  uint8_t hi_sig[SIGMAX] = {};
  const bool has_lo = !lo_hex.empty() && hexToBytes(lo_hex, lo_sig, keyLen);
  const bool has_hi = !hi_hex.empty() && hexToBytes(hi_hex, hi_sig, keyLen);
  Run<W> run;
  for (const auto& p : paths) {
    RunFileReader<W> r(p, H, keyLen);
    if (!r.ok()) {
      std::fprintf(stderr, "worker_io: cannot read input %s\n", p.c_str());
      std::exit(1);
    }
    if (has_lo) r.seekToKey(lo_sig);
    RunRecord<W> rec;
    while (r.next(rec)) {
      if (has_lo && sigCmp(rec.sig.b, lo_sig, keyLen) < 0) continue;
      if (has_hi && sigCmp(rec.sig.b, hi_sig, keyLen) >= 0) break;
      run.push_back(std::move(rec));
    }
  }
  sortRun(run);
  deduplicateRun(run);
  return run;
}

// Write an in-RAM Run<W> to a POLYRUN file with its .idx sidecar (so the
// orchestrator's normal SampleKeys/BalancedCutsMulti partitioning works on
// this output exactly as it does on the spill/merge-path outputs).
template <class W>
size_t writeRunFile(const Run<W>& run, const std::string& out_path,
                    int H, int keyLen, const std::string& rev) {
  RunFileWriter<W> w(out_path, H, 0, "", "", rev, keyLen, /*write_index=*/true);
  for (const auto& r : run) w.append(r);
  return w.finalize();
}
