// mapreduce.h — map_shard() and merge() (DESIGN §4, §5).
//
// map_shard<Classifier>(source_run, cfg, out_classified) -> Run<W>
//   Stream source states, apply the king-column transition, sort + deduplicate
//   successor records -> one sorted Run (the next column's contribution).
//   Also drives the completion (classify) side into out_classified.
//
// merge<W>(runs) -> Run<W>
//   K-way merge of sorted runs (equal keys combined via RunRecord::combine).
//   The commutative+associative combine means result is independent of run order
//   and shard partition cuts (the bit-identical property, DESIGN §0).
//
// Both are in-RAM (no file I/O, no spill) for M0. Spill is added in M1.

#pragma once

#include <algorithm>
#include <cassert>
#include <cstdio>
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
  bool fold;   // apply R1 vertical-mirror fold
  size_t ram_budget_bytes = 0;  // 0 = no spill (M0 in-RAM mode)
  std::string spill_dir;
};

// ─── map_shard ────────────────────────────────────────────────────────────────
//
// For each source state in `src`:
//   1. Check the completion predicate; if met, call Classifier::complete.
//   2. Enumerate all viable successor masks (forEachViableMask).
//   3. Apply stepColumnSquare8 for each mask -> successor sig + contribution.
//   4. Admissibility prune (completionLowerBound).
//   5. Optionally fold the successor sig (R1 symmetry).
//   6. Collect the (successor_sig, ranged_contribution) record.
// After processing all source states: sort + deduplicate -> one sorted Run.

template <class W, class Classifier, class Output>
Run<W> map_shard(const Run<W>& src, const ShardCfg& cfg, Output& out_classified) {
  const int H    = cfg.H;
  const int maxn = cfg.maxn;
  Run<W> buf;
  buf.reserve(src.size()); // at least one successor per source; skips early doublings

  // TODO(perf, M1+): the inner lambda allocates succ.counts per successor (millions
  // at scale) and the trailing sortRun re-sorts data the sorted frontier already
  // partly orders. Hoist a reusable scratch record and replace sort+dedup with a
  // structure-aware k-way merge once the spill engine makes this the bottleneck.
  for (const auto& rec : src) {
    // minimum cells already placed
    const int ms = rec.minSize();
    if (ms < 0) continue;  // empty count-vec (degenerate, skip)

    // completion test: single component touching both top and bottom
    Classifier::complete(rec.sig, H, rec, out_classified);

    // enumerate viable masks and map each one
    forEachViableMask(rec.sig, H, maxn - ms, [&](unsigned mask) {
      Sig out_sig;
      if (stepColumnSquare8(rec.sig, H, mask, out_sig) != Outcome::Alive) return;

      const int cells = __builtin_popcount(mask);
      if (ms + cells + completionLowerBound(out_sig.b, H) > maxn) return;

      if (cfg.fold) foldSig(out_sig, H);

      // build the successor RunRecord: shift the ranged count-vec by `cells`
      RunRecord<W> succ;
      succ.sig = out_sig;
      succ.H   = H;
      // new lo = rec.lo + cells; clip window to stay within [0..maxn]
      const int new_lo = static_cast<int>(rec.lo) + cells;
      if (new_lo > maxn) return; // entire window out of budget
      succ.lo  = static_cast<uint8_t>(new_lo);
      // clip: only keep entries with index <= maxn
      const int new_len = std::min<int>(rec.len, maxn - new_lo + 1);
      succ.len = static_cast<uint8_t>(new_len);
      succ.counts.assign(rec.counts.begin(), rec.counts.begin() + new_len);
      buf.push_back(std::move(succ));
    });
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
      return std::memcmp(rec->sig.b, o.rec->sig.b,
                         static_cast<size_t>(rec->H + 2)) > 0;
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
      if (std::memcmp(combined.sig.b, nxt.rec->sig.b,
                      static_cast<size_t>(combined.H + 2)) != 0) break;
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

template <class W, class Classifier, class Output>
std::pair<size_t, size_t> map_shard_file(
    const std::vector<std::string>& in_paths,
    const ShardCfg& cfg,
    const std::string& out_path,
    const std::string& lo_hex,
    const std::string& hi_hex,
    Output& out_classified,
    const std::string& rev = "") {

  const int H    = cfg.H;
  const int maxn = cfg.maxn;

  // Key-bound parsing.
  const int keyLen = H + 2;
  uint8_t lo_sig[SIGMAX] = {};
  uint8_t hi_sig[SIGMAX] = {};
  bool has_lo = !lo_hex.empty() && hexToBytes(lo_hex, lo_sig, keyLen);
  bool has_hi = !hi_hex.empty() && hexToBytes(hi_hex, hi_sig, keyLen);

  // Open all input files.
  std::vector<std::unique_ptr<RunFileReader<W>>> readers;
  readers.reserve(in_paths.size());
  for (const auto& p : in_paths)
    readers.push_back(std::make_unique<RunFileReader<W>>(p, H));

  // K-way heap over RunFileReaders.
  struct FileCursor {
    RunRecord<W> rec;
    int idx;
    bool operator>(const FileCursor& o) const {
      return std::memcmp(rec.sig.b, o.rec.sig.b,
                         static_cast<size_t>(rec.H + 2)) > 0;
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

  // Conservative record size estimate for budget tracking.
  const size_t record_est = static_cast<size_t>(H + 4) +
                            static_cast<size_t>(maxn) * sizeof(W);

  auto do_spill = [&]() {
    if (buf.empty()) return;
    sortRun(buf);
    deduplicateRun(buf);
    std::string spill_path = cfg.spill_dir + "/spill_" +
                             std::to_string(static_cast<long>(getpid())) +
                             "_" + std::to_string(spill_seq++) + ".bin";
    RunFileWriter<W> sw(spill_path, H, maxn, "", "", rev);
    for (const auto& r : buf) sw.append(r);
    size_t sb = sw.finalize();
    total_spill_bytes += sb;
    spill_files.push_back(spill_path);
    buf.clear();
    buf_bytes = 0;
  };

  // Stream records from heap, apply map logic.
  while (!heap.empty()) {
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
        std::memcmp(top.rec.sig.b, lo_sig, static_cast<size_t>(keyLen)) < 0)
      continue;
    if (has_hi &&
        std::memcmp(top.rec.sig.b, hi_sig, static_cast<size_t>(keyLen)) >= 0)
      break;

    // Combine equal-key records from heap.
    while (!heap.empty()) {
      if (std::memcmp(top.rec.sig.b, heap.top().rec.sig.b,
                      static_cast<size_t>(keyLen)) != 0) break;
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

    forEachViableMask(rec.sig, H, maxn - ms, [&](unsigned mask) {
      Sig out_sig;
      if (stepColumnSquare8(rec.sig, H, mask, out_sig) != Outcome::Alive) return;

      const int cells = __builtin_popcount(mask);
      if (ms + cells + completionLowerBound(out_sig.b, H) > maxn) return;

      if (cfg.fold) foldSig(out_sig, H);

      RunRecord<W> succ;
      succ.sig = out_sig;
      succ.H   = H;
      const int new_lo = static_cast<int>(rec.lo) + cells;
      if (new_lo > maxn) return;
      succ.lo  = static_cast<uint8_t>(new_lo);
      const int new_len = std::min<int>(rec.len, maxn - new_lo + 1);
      succ.len = static_cast<uint8_t>(new_len);
      succ.counts.assign(rec.counts.begin(), rec.counts.begin() + new_len);
      buf.push_back(std::move(succ));
      buf_bytes += record_est;
    });

    if (cfg.ram_budget_bytes > 0 && buf_bytes > cfg.ram_budget_bytes)
      do_spill();
  }

  // Final spill or direct write.
  do_spill();  // flush remaining buf to a spill file

  // Merge all spill files into out_path.
  size_t out_bytes = mergeRunFiles<W>(spill_files, H, "", "", out_path, rev);
  (void)out_bytes;

  // Count output records.
  RunFileReader<W> counter(out_path, H);
  size_t out_recs = counter.records();

  // Delete temp spill files.
  for (const auto& sf : spill_files)
    std::remove(sf.c_str());

  return {total_spill_bytes, out_recs};
}
