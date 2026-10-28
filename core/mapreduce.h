// mapreduce.h — map_shard() and merge().
//
// map_shard<Classifier>(source_run, cfg, out_classified) -> Run<W>
//   Stream source states, apply the king-column transition, sort + deduplicate
//   successor records -> one sorted Run (the next column's contribution).
//   Also drives the completion (classify) side into out_classified.
//
// merge<W>(runs) -> Run<W>
//   K-way merge of sorted runs (equal keys combined via RunRecord::combine).
//   The commutative+associative combine means result is independent of run order
//   and shard partition cuts (the bit-identical property).
//
// Both are in-RAM (no file I/O, no spill); the file-backed versions spill.

#pragma once

#include <algorithm>
#include <cassert>
#include <csignal>
#include <cstdio>
#include <functional>
#include <queue>
#include <string>
#include <unistd.h>
#include <vector>

#include "core/signature.h"
#include "core/transition.h"
#include "core/run.h"
#include "core/classifier.h"

// Configuration for one shard map pass.
struct ShardCfg {
  int H;       // height of this sweep
  int maxn;    // maximum cell count (budget)
  bool fold;   // fold each state with its vertical mirror (foldSig)
  size_t ram_budget_bytes = 0;  // 0 = no spill
  std::string spill_dir;
  int keyLen = 0;  // 0 = use H+2 (triangle); H+3 for holes path
};

// ─── successors ───────────────────────────────────────────────────────────────
//
// For one source record, the column transition shared by map_shard and
// map_shard_file:
//   1. Enumerate all viable successor masks (forEachViableMask).
//   2. Apply stepColumnSquare8 for each mask -> successor sig.
//   3. Admissibility prune (completionLowerBound).
//   4. Optionally fold the successor sig with its vertical mirror.
//   5. On the holes path, carry the hole count in key byte b[H+2].
//   6. Shift the ranged count-vec by the cells placed, clipped to maxn.
// emit(RunRecord<W>&&) receives each successor; `mr` is the allocator for
// its counts (nullptr: the default).
template <class W, class Emit>
inline void forEachSuccessor(const RunRecord<W>& rec, const ShardCfg& cfg,
                             int keyLen, int ms, std::pmr::memory_resource* mr,
                             Emit&& emit) {
  const int H = cfg.H, maxn = cfg.maxn;
  const bool holes = (keyLen == H + 3);
  uint32_t oldOcc = 0;  // occupancy of the current boundary column (holes only)
  if (holes)
    for (int r = 0; r < H; ++r)
      if (rec.sig.b[r] != 0) oldOcc |= (1u << r);

  forEachViableMask(rec.sig, H, maxn - ms, [&](unsigned mask) {
    Sig out_sig;
    if (stepColumnSquare8(rec.sig, H, mask, out_sig) != Outcome::Alive) return;

    const int cells = __builtin_popcount(mask);
    if (ms + cells + completionLowerBound(out_sig.b, H) > maxn) return;

    if (cfg.fold) foldSig(out_sig, H);

    RunRecord<W> succ(mr ? mr : std::pmr::get_default_resource());
    succ.sig    = out_sig;
    succ.H      = H;
    succ.keyLen = keyLen;

    if (holes) {
      // holes so far = components - (4*Euler)/4 of the closed image, so the
      // change is the change in components minus the Euler delta.
      const int delta4 = closedEulerDelta4(oldOcc, static_cast<uint32_t>(mask), H,
                                           Conn::FG8);
      int comps_old = 0, comps_new = 0;
      for (int r = 0; r < H; ++r) {
        if (rec.sig.b[r] > comps_old) comps_old = rec.sig.b[r];
        if (out_sig.b[r] > comps_new) comps_new = out_sig.b[r];
      }
      const int dHoles = (comps_new - comps_old) - delta4 / 4;
      succ.sig.b[H + 2] = static_cast<uint8_t>(
          static_cast<int>(rec.sig.b[H + 2]) + dHoles);
    }

    const int new_lo = static_cast<int>(rec.lo) + cells;
    if (new_lo > maxn) return;  // entire window out of budget
    succ.lo  = static_cast<uint8_t>(new_lo);
    const int new_len = std::min<int>(rec.len, maxn - new_lo + 1);
    succ.len = static_cast<uint8_t>(new_len);
    succ.counts.assign(rec.counts.begin(), rec.counts.begin() + new_len);
    emit(std::move(succ));
  });
}

// ─── map_shard ────────────────────────────────────────────────────────────────
//
// In RAM: for each source state, classify it if it completes an animal, then
// collect its successors; sort + deduplicate -> one sorted Run.
template <class W, class Classifier, class Output>
Run<W> map_shard(const Run<W>& src, const ShardCfg& cfg, Output& out_classified) {
  const int kLen = (cfg.keyLen != 0) ? cfg.keyLen : cfg.H + 2;
  Run<W> buf;
  buf.reserve(src.size()); // at least one successor per source; skips early doublings
  for (const auto& rec : src) {
    const int ms = rec.minSize();
    if (ms < 0) continue;  // empty count-vec (degenerate, skip)
    Classifier::complete(rec.sig, cfg.H, rec, out_classified);
    forEachSuccessor<W>(rec, cfg, kLen, ms, nullptr,
                        [&](RunRecord<W>&& succ) { buf.push_back(std::move(succ)); });
  }
  sortRun(buf);
  deduplicateRun(buf);
  return buf;
}

// ─── merge ────────────────────────────────────────────────────────────────────
//
// K-way merge of sorted Runs. Uses a min-heap keyed on sig (memcmp order).
// Equal keys are combined via RunRecord::combine (range-union + componentwise add).

template <class W>
Run<W> mergeRuns(std::vector<Run<W>>& runs) {
  // Cursor into one run: (run_index, record_index). Holds a raw pointer into
  // runs[i]; `runs` and its inner vectors must NOT be resized during the merge.
  struct Cursor {
    int run;
    size_t pos;
    const RunRecord<W>* rec;
    bool operator>(const Cursor& o) const {
      return sigCmp(rec->sig.b, o.rec->sig.b, rec->keyLen) > 0;
    }
  };

  using MinHeap = std::priority_queue<Cursor, std::vector<Cursor>, std::greater<Cursor>>;
  MinHeap heap;
  size_t totalRecords = 0;
  for (int i = 0; i < static_cast<int>(runs.size()); ++i) {
    totalRecords += runs[i].size();
    if (!runs[i].empty())
      heap.push({i, 0, &runs[i][0]});
  }

  Run<W> result;
  result.reserve(totalRecords); // exact upper bound: merge only ever combines keys
  while (!heap.empty()) {
    Cursor top = heap.top(); heap.pop();
    RunRecord<W> combined = *top.rec;

    // advance this cursor
    ++top.pos;
    if (top.pos < runs[top.run].size()) {
      top.rec = &runs[top.run][top.pos];
      heap.push(top);
    }

    // drain all equal-key records from the heap into combined
    while (!heap.empty()) {
      Cursor nxt = heap.top();
      if (sigCmp(combined.sig.b, nxt.rec->sig.b, combined.keyLen) != 0) break;
      heap.pop();
      combined.combine(*nxt.rec);
      ++nxt.pos;
      if (nxt.pos < runs[nxt.run].size()) {
        nxt.rec = &runs[nxt.run][nxt.pos];
        heap.push(nxt);
      }
    }
    result.push_back(std::move(combined));
  }
  return result;
}

// ─── runfile.h is included below; mergeRunFiles forwarded for callers ─────────
#include "core/runfile.h"

// ─── map_shard_file ──────────────────────────────────────────────────────────
//
// File-backed version of map_shard: reads from POLYRUN files, spills to disk
// when the in-memory buffer exceeds cfg.ram_budget_bytes, and produces one
// sorted POLYRUN output file.  Returns {total_spill_bytes, output_record_count}.

// Progress-pulse stride: how many source keys between opportunities to report
// progress / check the work-stealing stop flag (the orchestrator's `processed`
// and stealEligible are fed only from these pulses; orchestrator/telemetry.go
// unitProgress). It must stay well below realistic per-unit key counts (~12K
// at test scale, ~18K at H16 in production), or a unit's processed count
// never leaves 0 and it can never be stolen. The check costs the same
// (~0.8 ns/record, measured) at any stride from 2^14 down to 2^6.
static constexpr unsigned kProgressStrideMask = (1u << 10) - 1;
// 4096 leaves >= 2 pulse opportunities even at the smallest scale measured.
static_assert(kProgressStrideMask + 1 <= 4096,
              "progress-pulse stride too coarse: see kProgressStrideMask comment");

template <class W, class Classifier, class Output>
std::pair<size_t, size_t> map_shard_file(
    const std::vector<std::string>& in_paths,
    const ShardCfg& cfg,
    const std::string& out_path,
    const std::string& lo_hex,
    const std::string& hi_hex,
    Output& out_classified,
    const std::string& rev = "",
    const std::function<void(size_t)>& on_progress = {},
    const volatile std::sig_atomic_t* stop_flag = nullptr,
    std::string* stop_key_hex = nullptr) {

  // Work-stealing: when the orchestrator detects this unit is
  // the straggler holding up a column's tail, it raises *stop_flag (via SIGTERM).
  // We finish the input key currently being merged, stop reading at the next
  // key boundary (the cursor), and finalize a fully valid sorted output over
  // [lo, cursor).  The orchestrator requeues [cursor, hi) to idle cores.  The
  // map output is unchanged (merge recombines by output key), so this is
  // result-invariant — only the partition of work across processes differs.

  const int H      = cfg.H;
  const int maxn   = cfg.maxn;
  // Key-bound parsing.
  const int keyLen = (cfg.keyLen != 0) ? cfg.keyLen : H + 2;
  requireKeyLenFits(keyLen, "map_shard_file");
  uint8_t lo_sig[SIGMAX] = {};
  uint8_t hi_sig[SIGMAX] = {};
  bool has_lo = parseKeyBound(lo_hex, lo_sig, keyLen, "map_shard_file", "lo");
  bool has_hi = parseKeyBound(hi_hex, hi_sig, keyLen, "map_shard_file", "hi");

  // Open all input files.  If this is a bounded unit, seek each reader to lo via
  // the sparse .idx sidecar (same as mergeRunFiles): a key-range unit then skips
  // its [start, lo) prefix instead of scanning+discarding it.  This makes the
  // base case cheaper AND keeps work-stealing cheap — a requeued [cursor, hi)
  // sub-unit seeks straight to cursor rather than re-reading the whole prefix.
  // seekToKey lands at-or-before lo (no index → no-op); the range filter below
  // remains the exact correctness boundary.
  std::vector<std::unique_ptr<RunFileReader<W>>> readers;
  readers.reserve(in_paths.size());
  for (const auto& p : in_paths) {
    readers.push_back(std::make_unique<RunFileReader<W>>(p, H, keyLen));
    // A frontier input that can't be opened (e.g. lost to a GC race) must abort
    // the worker, not be silently treated as an empty file — otherwise its
    // records vanish from the count with no signal.
    if (!readers.back()->ok()) {
      std::fprintf(stderr, "map_shard_file: cannot read input %s\n", p.c_str());
      std::exit(1);
    }
    if (has_lo) readers.back()->seekToKey(lo_sig);
  }

  // K-way heap over RunFileReaders.
  struct FileCursor {
    RunRecord<W> rec;
    int idx;
    bool operator>(const FileCursor& o) const {
      return sigCmp(rec.sig.b, o.rec.sig.b, rec.keyLen) > 0;
    }
  };
  using MinHeap = std::priority_queue<FileCursor, std::vector<FileCursor>,
                                      std::greater<FileCursor>>;
  MinHeap heap;
  for (int i = 0; i < static_cast<int>(readers.size()); ++i) {
    FileCursor c;
    c.idx = i;
    if (readers[i]->next(c.rec))
      heap.push(std::move(c));
  }

  // In-memory accumulation buffer + spill tracking.
  Run<W> buf;
  size_t buf_bytes = 0;
  std::vector<std::string> spill_files;
  size_t total_spill_bytes = 0;
  int spill_seq = 0;

  // Successor-counts arena (succ.counts.assign() was the
  // sole per-successor heap allocation, ~14% of map cycles; measured 415.8M
  // allocations in a34's swept portion). Bump-allocates from a chunk sized
  // to the spill budget; every succ this epoch shares it (all with EQUAL
  // pmr allocators, so pmr::vector's move/swap/assign all take their normal
  // fast paths, no element-wise fallback). Released (not just cleared) right
  // after each do_spill() write-out, matching buf.clear()'s epoch boundary --
  // bulk-freeing beats N individual frees, same asymmetry as the malloc side.
  std::pmr::monotonic_buffer_resource succArena(succArenaHint(cfg.ram_budget_bytes));


  // Per-record RESIDENT-RAM estimate for the spill trigger. Must reflect the
  // actual std::vector<RunRecord> footprint, not wire size: the object itself
  // (Sig + fields + the vector control block) + the heap-allocated counts vector
  // (<= maxn words) + allocator overhead. Charging wire size alone undercounts
  // the ~96-byte object and lets the buffer overshoot --ram before do_spill().
  const size_t record_est = sizeof(RunRecord<W>) +
                            static_cast<size_t>(maxn) * sizeof(W) + 32;

  auto do_spill = [&]() {
    if (buf.empty()) return;
    sortRun(buf);
    deduplicateRun(buf);
    std::string spill_path = cfg.spill_dir + "/spill_" +
                             std::to_string(static_cast<long>(getpid())) +
                             "_" + std::to_string(spill_seq++) + ".bin";
    // Internal spill: no index (read back sequentially by mergeRunFiles), so it
    // is zstd-compressed when the build has zstd, which relieves the map
    // phase's disk write bandwidth.
    bool spill_compress = false;
#ifdef POLY_ZSTD
    spill_compress = true;
#endif
    RunFileWriter<W> sw(spill_path, H, maxn, "", "", rev, keyLen,
                        /*write_index=*/false, /*compress=*/spill_compress);
    for (const auto& r : buf) sw.append(r);
    size_t sb = sw.finalize();
    total_spill_bytes += sb;
    spill_files.push_back(spill_path);
    buf.clear();
    buf_bytes = 0;
    succArena.release();  // bulk-free this epoch's succ.counts allocations
  };

  // Stream records from heap, apply map logic.
  size_t processed = 0;
  while (!heap.empty()) {
    // Periodic progress pulse (every kProgressStrideMask+1 source keys); the
    // callback throttles by wall time and emits event=progress.  Cheap: a mask
    // test per iteration (measured noise-level cost regardless of stride; see
    // kProgressStrideMask's comment).  The orchestrator needs this signal both
    // for the heartbeat and to size in-flight units for work-stealing.
    if (on_progress && (++processed & kProgressStrideMask) == 0) {
      on_progress(processed);
      // Cooperative stop point (work-stealing): break at a key boundary so the
      // output covers [lo, cursor) exactly.  Checked on the same throttle as
      // progress so the per-iteration cost stays a single mask test.
      if (stop_flag && *stop_flag && stop_key_hex) {
        const uint8_t* cur = heap.top().rec.sig.b;
        // Past the upper bound already → nothing left in range; ran to completion.
        if (has_hi && sigCmp(cur, hi_sig, keyLen) >= 0)
          break;
        // Before the lower bound → no in-range work done yet; requeue [lo, hi)
        // whole (report lo) so we neither double-count nor leave a gap.
        if (has_lo && sigCmp(cur, lo_sig, keyLen) < 0)
          *stop_key_hex = lo_hex;
        else
          *stop_key_hex = bytesToHex(cur, keyLen);
        break;
      }
    }

    FileCursor top = heap.top();
    heap.pop();

    {
      FileCursor nc;
      nc.idx = top.idx;
      if (readers[top.idx]->next(nc.rec))
        heap.push(std::move(nc));
    }

    // Range filter.
    if (has_lo &&
        sigCmp(top.rec.sig.b, lo_sig, keyLen) < 0)
      continue;
    if (has_hi &&
        sigCmp(top.rec.sig.b, hi_sig, keyLen) >= 0)
      break;

    // Combine equal-key records from heap.
    while (!heap.empty()) {
      if (sigCmp(top.rec.sig.b, heap.top().rec.sig.b, keyLen) != 0) break;
      FileCursor eq = heap.top();
      heap.pop();
      top.rec.combine(eq.rec);
      FileCursor nc;
      nc.idx = eq.idx;
      if (readers[eq.idx]->next(nc.rec))
        heap.push(std::move(nc));
    }

    const RunRecord<W>& rec = top.rec;
    const int ms = rec.minSize();
    if (ms < 0) continue;

    Classifier::complete(rec.sig, H, rec, out_classified);
    forEachSuccessor<W>(rec, cfg, keyLen, ms, &succArena, [&](RunRecord<W>&& succ) {
      buf.push_back(std::move(succ));
      buf_bytes += record_est;
    });

    if (cfg.ram_budget_bytes > 0 && buf_bytes > cfg.ram_budget_bytes)
      do_spill();
  }

  // Final write. Fast path: a column that fit in RAM (no mid-stream spill) is
  // sorted+deduped and written STRAIGHT to out_path with its index, skipping
  // the write-a-lone-spill-then-read-it-back-through-mergeRunFiles round trip
  // (a full extra write + full read of the whole column output, for nothing).
  // On the spill-bound engine most columns never spill mid-stream, so this
  // halves their output I/O. Byte-identical: do_spill already sorts+dedups, and
  // mergeRunFiles over one already-deduped run just copies it out with maxn=0
  // in the header -- exactly what this direct write produces.
  size_t out_recs;
  if (spill_files.empty()) {
    sortRun(buf);
    deduplicateRun(buf);
    RunFileWriter<W> ow(out_path, H, 0, "", "", rev, keyLen, /*write_index=*/true,
                        /*compress=*/frontierZstd());
    for (const auto& r : buf) ow.append(r);
    ow.finalize();
    out_recs = buf.size();
    buf.clear();
  } else {
    do_spill();  // flush remaining buf to a final spill file
    auto [out_bytes, merged] = mergeRunFiles<W>(spill_files, H, "", "", out_path, rev, keyLen);
    (void)out_bytes;
    out_recs = merged;
  }

  // Delete temp spill files.
  for (const auto& sf : spill_files)
    std::remove(sf.c_str());

  return {total_spill_bytes, out_recs};
}
