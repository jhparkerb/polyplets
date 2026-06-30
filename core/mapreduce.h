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
#include "core/profile.h"

// Configuration for one shard map pass.
struct ShardCfg {
  int H;       // height of this sweep
  int maxn;    // maximum cell count (budget)
  bool fold;   // apply R1 vertical-mirror fold
  size_t ram_budget_bytes = 0;  // 0 = no spill (M0 in-RAM mode)
  std::string spill_dir;
  int keyLen = 0;  // 0 = use H+2 (triangle); H+3 for holes path
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
  const int H      = cfg.H;
  const int maxn   = cfg.maxn;
  const int kLen   = (cfg.keyLen != 0) ? cfg.keyLen : H + 2;
  const bool holes = (kLen == H + 3);
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

    // occupancy bitmask of the current boundary column (for holes accounting)
    uint32_t oldOcc = 0;
    if (holes) {
      for (int r = 0; r < H; ++r)
        if (rec.sig.b[r] != 0) oldOcc |= (1u << r);
    }

    // enumerate viable masks and map each one
    forEachViableMask(rec.sig, H, maxn - ms, [&](unsigned mask) {
      Sig out_sig;
      if (stepColumnSquare8(rec.sig, H, mask, out_sig) != Outcome::Alive) return;

      const int cells = __builtin_popcount(mask);
      if (ms + cells + completionLowerBound(out_sig.b, H) > maxn) return;

      if (cfg.fold) foldSig(out_sig, H);

      // build the successor RunRecord: shift the ranged count-vec by `cells`
      RunRecord<W> succ;
      succ.sig    = out_sig;
      succ.H      = H;
      succ.keyLen = kLen;

      // holes path: accumulate Euler delta into sig.b[H+2]
      if (holes) {
        const int delta4 = closedEulerDelta4(oldOcc, static_cast<uint32_t>(mask), H,
                                             Conn::FG8);
        // comps delta = comps_new - comps_old
        int comps_old = 0, comps_new = 0;
        for (int r = 0; r < H; ++r) {
          if (rec.sig.b[r] > comps_old)   comps_old = rec.sig.b[r];
          if (out_sig.b[r] > comps_new)   comps_new = out_sig.b[r];
        }
        // dHoles = (comps_new - comps_old) - delta4/4
        const int dHoles = (comps_new - comps_old) - delta4 / 4;
        succ.sig.b[H + 2] = static_cast<uint8_t>(
            static_cast<int>(rec.sig.b[H + 2]) + dHoles);
      }

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
// progress / check the work-stealing stop flag (mapPhase's `processed` and
// `stealEligible` are fed ONLY from these pulses, via the orchestrator parsing
// "event=progress" lines — see orchestrator/telemetry.go unitProgress). MUST
// stay well below realistic per-unit key counts or a unit's processed count
// never leaves 0 for its entire life, making it permanently ineligible for
// stealing regardless of how slow it runs (results/scheduling.md, the
// overlap+steal coexistence investigation). Was 1<<14=16384, ABOVE typical
// per-unit counts at both test scale (~12K, maxn20) and a24/a25 production
// scale (H16 ~18K, only ~1.1x the old stride) — i.e. it almost never fired.
// Microbenchmarked (scripts/, not committed): the bitmask check + occasional
// wallSeconds() poll cost the same (~0.7-0.85 ns/record, noise-level) from
// stride 2^14 down to 2^6 — the cost concern that motivated the old large
// value was unfounded. 1<<10=1024 is ~16x finer, giving ~10-18 pulse
// opportunities across a realistic unit's life at both scales (each still
// gated by the worker's own 2s print throttle, worker/map_worker.cpp).
static constexpr unsigned kProgressStrideMask = (1u << 10) - 1;
// Compile-time tripwire: a future "just bump it for fewer interrupts" edit
// must not silently regress past realistic per-unit record counts (~12K test
// scale, ~18K a24/a25 production scale) and go blind again. 4096 leaves >=2
// pulse opportunities even at the smallest scale measured.
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

  // Work-stealing (DESIGN 08, T2.3): when the orchestrator detects this unit is
  // the straggler holding up a column's tail, it raises *stop_flag (via SIGTERM).
  // We finish the input key currently being merged, stop reading at the next
  // key boundary (the cursor), and finalize a fully valid sorted output over
  // [lo, cursor).  The orchestrator requeues [cursor, hi) to idle cores.  The
  // map output is unchanged (merge recombines by output key), so this is
  // result-invariant — only the partition of work across processes differs.

  const int H      = cfg.H;
  const int maxn   = cfg.maxn;
  const bool holes = (cfg.keyLen == H + 3);

  // Key-bound parsing.
  const int keyLen = (cfg.keyLen != 0) ? cfg.keyLen : H + 2;
  uint8_t lo_sig[SIGMAX] = {};
  uint8_t hi_sig[SIGMAX] = {};
  bool has_lo = !lo_hex.empty() && hexToBytes(lo_hex, lo_sig, keyLen);
  bool has_hi = !hi_hex.empty() && hexToBytes(hi_hex, hi_sig, keyLen);

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

#ifdef POLY_PROFILE
  // Coarse phase wall-time + counters (Track B). Times the get-next-source-record
  // path (read+heap+combine), the map body (classify+enumerate+step+build), the
  // spills, and the final merge separately. Plus the decisive Finding-1/2 numbers:
  // model buf_bytes vs the ACTUAL resident buf footprint at the largest spill.
  double prof_read_s = 0, prof_map_s = 0, prof_spill_s = 0, prof_merge_s = 0;
  uint64_t prof_src = 0, prof_masks = 0, prof_succ = 0;
  size_t prof_max_model = 0, prof_max_actual = 0, prof_max_size = 0, prof_max_cap = 0;
  const double prof_t0 = prof::now();
#endif

  // Per-record RESIDENT-RAM estimate for the spill trigger. Must reflect the
  // actual std::vector<RunRecord> footprint, not wire size: the object itself
  // (Sig + fields + the vector control block) + the heap-allocated counts vector
  // (<= maxn words) + allocator overhead. The old estimate charged only H+4 +
  // maxn*W (wire size), undercounting the ~96-byte object, so the buffer overshot
  // --ram before do_spill() fired (Budget Blind: an OOM lever at scale).
  const size_t record_est = sizeof(RunRecord<W>) +
                            static_cast<size_t>(maxn) * sizeof(W) + 32;

  auto do_spill = [&]() {
    if (buf.empty()) return;
#ifdef POLY_PROFILE
    // Measure the real resident footprint of buf right before it drains: the
    // backing-array capacity (geometric-doubling slack, Finding 2a) + every
    // counts allocation's capacity. Compare to buf_bytes (the record_est model).
    {
      size_t actual = buf.capacity() * sizeof(RunRecord<W>);
      for (const auto& r : buf) actual += r.counts.capacity() * sizeof(W);
      if (actual > prof_max_actual) {
        prof_max_actual = actual;
        prof_max_model  = buf_bytes;
        prof_max_size   = buf.size();
        prof_max_cap    = buf.capacity();
      }
    }
    const double _ts = prof::now();
#endif
    sortRun(buf);
    deduplicateRun(buf);
    std::string spill_path = cfg.spill_dir + "/spill_" +
                             std::to_string(static_cast<long>(getpid())) +
                             "_" + std::to_string(spill_seq++) + ".bin";
    RunFileWriter<W> sw(spill_path, H, maxn, "", "", rev, keyLen, /*write_index=*/false);
    for (const auto& r : buf) sw.append(r);
    size_t sb = sw.finalize();
    total_spill_bytes += sb;
    spill_files.push_back(spill_path);
    buf.clear();
    buf_bytes = 0;
#ifdef POLY_PROFILE
    prof_spill_s += prof::now() - _ts;
#endif
  };

  // Stream records from heap, apply map logic.
  size_t processed = 0;
  while (!heap.empty()) {
#ifdef POLY_PROFILE
    const double _tr = prof::now();
#endif
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

#ifdef POLY_PROFILE
    prof_read_s += prof::now() - _tr;
    ++prof_src;
    const double _tm = prof::now();
#endif
    Classifier::complete(rec.sig, H, rec, out_classified);

    // occupancy bitmask of the current boundary column (for holes accounting)
    uint32_t oldOcc = 0;
    if (holes) {
      for (int r = 0; r < H; ++r)
        if (rec.sig.b[r] != 0) oldOcc |= (1u << r);
    }

    forEachViableMask(rec.sig, H, maxn - ms, [&](unsigned mask) {
#ifdef POLY_PROFILE
      ++prof_masks;
#endif
      Sig out_sig;
      if (stepColumnSquare8(rec.sig, H, mask, out_sig) != Outcome::Alive) return;

      const int cells = __builtin_popcount(mask);
      if (ms + cells + completionLowerBound(out_sig.b, H) > maxn) return;

      if (cfg.fold) foldSig(out_sig, H);

      RunRecord<W> succ;
      succ.sig    = out_sig;
      succ.H      = H;
      succ.keyLen = keyLen;

      // holes path: accumulate Euler delta into sig.b[H+2]
      if (holes) {
        const int delta4 = closedEulerDelta4(oldOcc, static_cast<uint32_t>(mask), H,
                                             Conn::FG8);
        int comps_old = 0, comps_new = 0;
        for (int r = 0; r < H; ++r) {
          if (rec.sig.b[r] > comps_old)  comps_old = rec.sig.b[r];
          if (out_sig.b[r] > comps_new)  comps_new = out_sig.b[r];
        }
        const int dHoles = (comps_new - comps_old) - delta4 / 4;
        succ.sig.b[H + 2] = static_cast<uint8_t>(
            static_cast<int>(rec.sig.b[H + 2]) + dHoles);
      }

      const int new_lo = static_cast<int>(rec.lo) + cells;
      if (new_lo > maxn) return;
      succ.lo  = static_cast<uint8_t>(new_lo);
      const int new_len = std::min<int>(rec.len, maxn - new_lo + 1);
      succ.len = static_cast<uint8_t>(new_len);
      succ.counts.assign(rec.counts.begin(), rec.counts.begin() + new_len);
      buf.push_back(std::move(succ));
      buf_bytes += record_est;
#ifdef POLY_PROFILE
      ++prof_succ;
#endif
    });

#ifdef POLY_PROFILE
    prof_map_s += prof::now() - _tm;
#endif
    if (cfg.ram_budget_bytes > 0 && buf_bytes > cfg.ram_budget_bytes)
      do_spill();
  }

  // Final spill or direct write.
  do_spill();  // flush remaining buf to a spill file

  // Merge all spill files into out_path (record count threaded out of the merge).
#ifdef POLY_PROFILE
  const double _tmg = prof::now();
#endif
  auto [out_bytes, out_recs] = mergeRunFiles<W>(spill_files, H, "", "", out_path, rev, keyLen);
  (void)out_bytes;
#ifdef POLY_PROFILE
  prof_merge_s += prof::now() - _tmg;
  {
    char line[512];
    std::snprintf(line, sizeof(line),
      "mapphase H=%d maxn=%d src=%llu masks=%llu succ=%llu spills=%d out_recs=%zu "
      "read_s=%.4f map_s=%.4f spill_s=%.4f merge_s=%.4f total_s=%.4f peak_rss_mb=%.1f "
      "model_bytes=%zu actual_bytes=%zu buf_size=%zu buf_cap=%zu",
      H, maxn, (unsigned long long)prof_src, (unsigned long long)prof_masks,
      (unsigned long long)prof_succ, spill_seq, out_recs,
      prof_read_s, prof_map_s, prof_spill_s, prof_merge_s, prof::now() - prof_t0,
      prof::peakRssMB(), prof_max_model, prof_max_actual, prof_max_size, prof_max_cap);
    prof::emit(line);
  }
#endif

  // Delete temp spill files.
  for (const auto& sf : spill_files)
    std::remove(sf.c_str());

  return {total_spill_bytes, out_recs};
}
