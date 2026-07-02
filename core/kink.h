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
#include <cstdint>
#include <cstring>

#include "core/run.h"
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
    const int ms = rec.minSize();
    if (ms < 0) continue;  // empty count-vec (degenerate, skip)

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
