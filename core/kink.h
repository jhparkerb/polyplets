// kink.h — kink-carry stage kernel (Design 14, Phase 1: library only, dark).
//
// The production engine (core/mapreduce.h) transfers a WHOLE COLUMN per step.
// Kink-carry instead moves the boundary ONE CELL at a time (H micro-stages per
// column), carrying the one NW cell each stage overwrites so king adjacency
// stays available without needing the whole old column. Serial win measured
// in experiments/kink_tm/kink_tm.cpp: results/kink-carry.md.
//
// Mixed-state key during a stage sweep (32-byte Sig, keyLen = H+4):
//   b[0..H)   mixed boundary: new-column cells for rows < stage (this
//             column), old-column cells for rows >= stage (previous column)
//   b[H]      touched-top flag
//   b[H+1]    touched-bottom flag
//   b[H+2]    carry: the old cell overwritten one stage ago, still
//             king-reachable (NW of the cell about to be placed)
//   b[H+3]    placed-any bit (at least one new cell placed so far this column)
// Canonicalisation covers b[0..H) AND the carry byte together (canonMixed);
// the touch/placed flags are never relabeled.
//
// Scope v1 = triangle only: the holes path's Euler-count accumulator lives in
// sig.b[H+2] (core/mapreduce.h), which collides with the carry byte here.
// Holes stays on the whole-column kernel (an a19/a20-era concern).
//
// map_shard_stage is the single-stage analogue of core/mapreduce.h's
// map_shard: it consumes a shard of the CURRENT stage's mixed-state table and
// produces that shard's successor records for stage+1 as a sorted,
// deduplicated Run<W> — same Run<W>/mergeRuns contract, just keyed on the
// mixed state instead of the end-of-column state. Column-boundary harvest
// (classify + seed stage 0) and finalize (drop the last carry, stranding
// check, canonicalize, admissibility prune, R1 fold) are Phase 2 concerns
// (orchestrator wiring); this header only ports the per-stage fan-out.

#pragma once

#include <algorithm>
#include <csignal>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <functional>
#include <memory>
#include <queue>
#include <string>
#include <unistd.h>
#include <vector>

#include "core/run.h"
#include "core/runfile.h"
#include "core/signature.h"
#include "core/transition.h"

// Mixed-state key length for a height-H kink-carry sweep.
inline int kinkKeyLen(int H) { return H + 4; }

// Canonicalize a mixed-state Sig in place: relabel components 1,2,... in
// order of first occurrence over b[0..H), mapping the carry byte b[H+2]
// through the SAME relabeling (it is part of the same partition). The
// touch/placed flags (b[H..H+1], b[H+3]) are untouched.
inline void canonMixed(Sig& s, int H) {
  unsigned char map[256] = {0};
  unsigned char next = 1;
  for (int i = 0; i < H; ++i) {
    const unsigned char v = s.b[i];
    if (v == 0) continue;
    if (map[v] == 0) map[v] = next++;
    s.b[i] = map[v];
  }
  const unsigned char c = s.b[H + 2];
  if (c != 0) {
    if (map[c] == 0) map[c] = next++;
    s.b[H + 2] = map[c];
  }
}

// True if label L (nonzero) still appears somewhere in the mixed state: the
// boundary b[0..H) or the carry b[H+2]. Used to detect a carried component
// stranded the instant it drops off (unreachable -> the state is dead).
inline bool labelInMixedState(const Sig& s, int H, unsigned char L) {
  for (int i = 0; i < H; ++i)
    if (s.b[i] == L) return true;
  return s.b[H + 2] == L;
}

// Apply one kink-carry stage transition to a single mixed-state source `s`
// (stage `r`, the new-column row about to be placed), calling
// emit(successor_sig, shift) for each surviving choice. `shift` is the number
// of new cells placed this stage (0 or 1) -- the amount by which a ranged
// count-vec's index n advances. `ms` is the minimum cell count already placed
// (budget check, mirrors RunRecord::minSize()).
//
// Ported verbatim from experiments/kink_tm/kink_tm.cpp's kinkSweep() per-r
// loop body (occupy in {0,1}; union-find over N/W/NW/SW; canonicalize;
// stranding check on the outgoing carry). This is the single source of truth
// for the transition -- experiments/kink_tm/kink_tm.cpp reuses it directly so
// the probe and the ported kernel can never drift apart.
template <class F>
inline void kinkStageTransition(const Sig& s, int H, int r, int ms, int maxn,
                                F&& emit) {
  int uf[2 * SIGMAX];
  for (int occupy = 0; occupy < 2; ++occupy) {
    if (occupy && ms + 1 > maxn) break;  // budget: cannot place another cell

    Sig t = s;
    unsigned char newLabel = 0;
    if (occupy) {
      for (int i = 0; i < 2 * SIGMAX; ++i) uf[i] = i;
      auto uadd = [&](unsigned char L) {
        if (L) {
          int a = s8::find(uf, 0), b = s8::find(uf, L);
          if (a != b) uf[a] = b;
        }
      };
      if (r > 0) uadd(s.b[r - 1]);       // N (new column cell)
      uadd(s.b[r]);                       // W (old, pre-overwrite)
      uadd(s.b[H + 2]);                   // NW = carry
      if (r + 1 < H) uadd(s.b[r + 1]);    // SW (old)
      // Relabel every label joining the new cell's component to one fresh
      // scratch label; canonMixed renumbers everything properly below.
      const int root = s8::find(uf, 0);
      unsigned char fresh = 200;
      for (int i = 0; i < H; ++i)
        if (t.b[i] && s8::find(uf, t.b[i]) == root) t.b[i] = fresh;
      if (t.b[H + 2] && s8::find(uf, t.b[H + 2]) == root) t.b[H + 2] = fresh;
      newLabel = fresh;
    }

    // Advance kink: outgoing carry = t.b[H+2] (already relabeled if occupy),
    // incoming carry = old value at row r (pre-overwrite).
    const unsigned char outgoing = t.b[H + 2];
    t.b[H + 2] = t.b[r];
    t.b[r] = occupy ? newLabel : 0;
    if (occupy) {
      if (r == 0) t.b[H] = 1;
      if (r == H - 1) t.b[H + 1] = 1;
      t.b[H + 3] = 1;
    }
    // Stranding: the outgoing carry's component is unreachable if its label
    // appears nowhere else in the state.
    if (outgoing != 0 && !labelInMixedState(t, H, outgoing)) continue;
    canonMixed(t, H);
    emit(t, occupy ? 1 : 0);
  }
}

// Configuration for one kink-carry stage's shard map pass.
struct KinkStageCfg {
  int H;      // height of this sweep
  int maxn;   // maximum cell count (budget)
  int stage;  // stage index r in [0, H): the new-column row placed this stage
  size_t ram_budget_bytes = 0;  // 0 = no spill (map_shard_stage_file only)
  std::string spill_dir;
};

// map_shard_stage: one micro-stage of the kink-carry sweep (Design 14 Phase
// 1). Consumes a shard of the current stage's mixed-state table (keyLen
// H+4) and produces that shard's successor records for stage+1 as a sorted,
// deduplicated Run<W> -- the same Run<W>/mergeRuns contract core/mapreduce.h's
// map_shard uses, just keyed on the mixed state instead of the end-of-column
// state. Applies kinkStageTransition per source record, shifting each ranged
// count-vec window by the transition's per-choice cell count (0 or 1) and
// clipping to maxn, exactly as map_shard shifts by forEachViableMask's cell
// count. Orchestrator wiring (partition/parallel/merge over H stages,
// column-start harvest+seed, end-of-column finalize) is Phase 2.
template <class W>
Run<W> map_shard_stage(const Run<W>& src, const KinkStageCfg& cfg) {
  const int H    = cfg.H;
  const int maxn = cfg.maxn;
  const int r    = cfg.stage;
  const int kLen = kinkKeyLen(H);
  Run<W> buf;
  buf.reserve(src.size() * 2);  // fan-out is at most 2 (occupy in {0,1})

  for (const auto& rec : src) {
    const int trueMs = rec.minSize();
    if (trueMs < 0) continue;  // empty count-vec (degenerate, skip)
    const int ms = trueMs;

    kinkStageTransition(rec.sig, H, r, ms, maxn, [&](const Sig& t, int shift) {
      const int new_lo = static_cast<int>(rec.lo) + shift;
      if (new_lo > maxn) return;  // entire window out of budget
      const int new_len = std::min<int>(rec.len, maxn - new_lo + 1);

      RunRecord<W> succ;
      succ.sig    = t;
      succ.H      = H;
      succ.keyLen = kLen;
      succ.lo     = static_cast<uint8_t>(new_lo);
      succ.len    = static_cast<uint8_t>(new_len);
      succ.counts.assign(rec.counts.begin(), rec.counts.begin() + new_len);
      buf.push_back(std::move(succ));
    });
  }

  sortRun(buf);
  deduplicateRun(buf);
  return buf;
}

// Progress-pulse stride for map_shard_stage_file, mirroring
// core/mapreduce.h's kProgressStrideMask (distinct name: map_worker.cpp
// includes both headers in the same TU once --kernel kink dispatches
// alongside the column kernel, so the two constants must not collide).
static constexpr unsigned kKinkProgressStrideMask = (1u << 10) - 1;

// File-backed version of map_shard_stage (Design 14 Phase 2.3): reads a
// shard of the current stage's mixed-state table from POLYRUN files (keyLen
// kinkKeyLen(H)), spills to disk past cfg's RAM budget, and writes one
// sorted POLYRUN output file for stage+1. Mirrors map_shard_file's shell
// (K-way heap over RunFileReader, spill/RAM-budget, progress pulse,
// cooperative SIGTERM stop-key) but with no Classifier/Output param (stage
// steps never classify -- harvest lives in kinkSeedStage0) and the inner
// per-record body replaced by kinkStageTransition. Returns {total_spill_bytes,
// output_record_count}.
template <class W>
std::pair<size_t, size_t> map_shard_stage_file(
    const std::vector<std::string>& in_paths,
    const KinkStageCfg& cfg,
    const std::string& out_path,
    const std::string& lo_hex,
    const std::string& hi_hex,
    const std::string& rev = "",
    const std::function<void(size_t)>& on_progress = {},
    const volatile std::sig_atomic_t* stop_flag = nullptr,
    std::string* stop_key_hex = nullptr) {
  const int H    = cfg.H;
  const int maxn = cfg.maxn;
  const int r    = cfg.stage;
  const int keyLen = kinkKeyLen(H);
  requireKeyLenFits(keyLen, "map_shard_stage_file");

  uint8_t lo_sig[SIGMAX] = {};
  uint8_t hi_sig[SIGMAX] = {};
  bool has_lo = parseKeyBound(lo_hex, lo_sig, keyLen, "map_shard_stage_file", "lo");
  bool has_hi = parseKeyBound(hi_hex, hi_sig, keyLen, "map_shard_stage_file", "hi");

  std::vector<std::unique_ptr<RunFileReader<W>>> readers;
  readers.reserve(in_paths.size());
  for (const auto& p : in_paths) {
    readers.push_back(std::make_unique<RunFileReader<W>>(p, H, keyLen));
    if (!readers.back()->ok()) {
      std::fprintf(stderr, "map_shard_stage_file: cannot read input %s\n",
                   p.c_str());
      std::exit(1);
    }
    if (has_lo) readers.back()->seekToKey(lo_sig);
  }

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

  Run<W> buf;
  size_t buf_bytes = 0;
  std::vector<std::string> spill_files;
  size_t total_spill_bytes = 0;
  int spill_seq = 0;

  const size_t record_est = sizeof(RunRecord<W>) +
                            static_cast<size_t>(maxn) * sizeof(W) + 32;

  // Successor-counts arena -- same rationale as mapreduce.h's map_shard_file
  // (map-profile.md B2): one bump-allocator per spill epoch instead of one
  // malloc/free per successor. Released at each do_spill(), matching
  // buf.clear()'s epoch boundary.
  std::pmr::monotonic_buffer_resource succArena(succArenaHint(cfg.ram_budget_bytes));

  auto do_spill = [&]() {
    if (buf.empty()) return;
    sortRun(buf);
    deduplicateRun(buf);
    std::string spill_path = cfg.spill_dir + "/spill_" +
                             std::to_string(static_cast<long>(getpid())) +
                             "_" + std::to_string(spill_seq++) + ".bin";
    bool spill_compress = false;
#ifdef POLY_ZSTD
    spill_compress = !std::getenv("POLY_NO_SPILL_ZSTD");
#endif
    RunFileWriter<W> sw(spill_path, H, maxn, "", "", rev, keyLen,
                        /*write_index=*/false, /*compress=*/spill_compress);
    for (const auto& r : buf) sw.append(r);
    size_t sb = sw.finalize();
    total_spill_bytes += sb;
    spill_files.push_back(spill_path);
    buf.clear();
    buf_bytes = 0;
    succArena.release();
  };

  size_t processed = 0;
  while (!heap.empty()) {
    if (on_progress && (++processed & kKinkProgressStrideMask) == 0) {
      on_progress(processed);
      if (stop_flag && *stop_flag && stop_key_hex) {
        const uint8_t* cur = heap.top().rec.sig.b;
        if (has_hi && sigCmp(cur, hi_sig, keyLen) >= 0)
          break;
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

    if (has_lo && sigCmp(top.rec.sig.b, lo_sig, keyLen) < 0)
      continue;
    if (has_hi && sigCmp(top.rec.sig.b, hi_sig, keyLen) >= 0)
      break;

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

    kinkStageTransition(rec.sig, H, r, ms, maxn, [&](const Sig& t, int shift) {
      const int new_lo = static_cast<int>(rec.lo) + shift;
      if (new_lo > maxn) return;
      const int new_len = std::min<int>(rec.len, maxn - new_lo + 1);

      RunRecord<W> succ(&succArena);
      succ.sig    = t;
      succ.H      = H;
      succ.keyLen = keyLen;
      succ.lo     = static_cast<uint8_t>(new_lo);
      succ.len    = static_cast<uint8_t>(new_len);
      succ.counts.assign(rec.counts.begin(), rec.counts.begin() + new_len);
      buf.push_back(std::move(succ));
      buf_bytes += record_est;
    });

    if (cfg.ram_budget_bytes > 0 && buf_bytes > cfg.ram_budget_bytes)
      do_spill();
  }

  size_t out_recs;
  if (spill_files.empty() && !std::getenv("POLY_NO_FASTPATH")) {
    sortRun(buf);
    deduplicateRun(buf);
    RunFileWriter<W> ow(out_path, H, 0, "", "", rev, keyLen, /*write_index=*/true,
                        /*compress=*/frontierZstd());
    for (const auto& r : buf) ow.append(r);
    ow.finalize();
    out_recs = buf.size();
    buf.clear();
  } else {
    do_spill();
    auto [out_bytes, merged] = mergeRunFiles<W>(spill_files, H, "", "", out_path, rev, keyLen);
    (void)out_bytes;
    out_recs = merged;
  }

  for (const auto& sf : spill_files)
    std::remove(sf.c_str());

  return {total_spill_bytes, out_recs};
}
