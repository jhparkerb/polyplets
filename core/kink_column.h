// kink_column.h — column-boundary seed/finalize for the kink-carry kernel
// (Design 14, Phase 2). core/kink.h (Phase 1, already gated) ports only the
// per-stage fan-out; this header adds the two column-boundary steps Phase 1
// deliberately left out:
//
//   kinkSeedStage0   — column start: harvest (classify) the previous column's
//                      end-of-column records, then seed stage 0 of the next
//                      column's mixed-state sweep.
//   kinkFinalizeColumn — column end: after H stage transitions, drop the
//                      final carry (with its stranding check), canonicalize,
//                      admissibility-prune, R1-fold, and dedup back down to
//                      the next column's end-of-column Run<W>.
//
// Ported from experiments/kink_tm/kink_tm.cpp's kinkSweep() column loop
// (kink_tm.cpp:100-162), which was re-read directly to settle a design-doc
// ambiguity: harvest happens at COLUMN START (via a per-column-start
// completion check on the state being seeded), not column end; finalize
// itself never classifies. Both header comments below cite the exact
// invariant kept.
//
// Deliberately a separate header from core/kink.h: kink.h's map_shard_stage
// is already committed and gated (tests/engine/gate_kink.cpp); keeping these two
// column-boundary functions here means this phase's gate (tests/engine/gate_kink_column.cpp)
// cannot regress Phase 1's.

#pragma once

#include <cstring>

#include "core/kink.h"
#include "core/run.h"
#include "core/signature.h"

// Seed stage 0 of a column's kink-carry sweep from the PREVIOUS column's
// end-of-column Run (keyLen H+2), harvesting (classifying)
// each source record on the way through -- classify must see the H+2-keyed
// boundary before it gains the two extra mixed-state bytes.
//
// The transform appends a CONSTANT 2-byte suffix (carry=0, placed-any=0) to
// every record's key. Since every key gets the same suffix, sigCmp order
// over the new keyLen=H+4 is identical to sigCmp order over the old
// keyLen=H+2 (a constant suffix cannot change the relative order of already
// distinct prefixes) -- so `src` being sorted+deduplicated at H+2 implies
// the output is already sorted+deduplicated at H+4. No sortRun/deduplicateRun
// needed here (unlike kinkFinalizeColumn, which can genuinely collide keys).
template <class W, class Classifier, class Output>
Run<W> kinkSeedStage0(const Run<W>& src, int H, Output& out_classified) {
  const int kLen = kinkKeyLen(H);
  Run<W> stage0;
  stage0.reserve(src.size());
  for (const auto& rec : src) {
    Classifier::complete(rec.sig, H, rec, out_classified);

    RunRecord<W> s0;
    s0.sig = rec.sig;
    s0.sig.b[H + 2] = 0;  // carry: none yet
    s0.sig.b[H + 3] = 0;  // placed-any: none yet
    s0.H = H;
    s0.keyLen = kLen;
    s0.lo = rec.lo;
    s0.len = rec.len;
    s0.counts = rec.counts;
    stage0.push_back(std::move(s0));
  }
  return stage0;
}

// Finalize a column from its stage-H mixed-state table (keyLen kinkKeyLen(H),
// the table after H sequential kinkStageTransition rounds) into the next
// column's end-of-column Run (keyLen H+2).
//
// Per record: require placed-any (an all-empty column is the completion
// path, not an extend -- mirrors map_shard's nonzero-mask contract), then
// stranding-check the outgoing carry (its component must still be reachable
// via the boundary once the carry itself is dropped), zero the two
// mixed-state bytes, canonicalize, admissibility-prune, and (if cfg.fold)
// R1-fold. No classify here -- harvest already happened in kinkSeedStage0.
// Distinct mixed states can collapse to the same H+2 key after canonicalize/
// fold, so (unlike the seed transform) this DOES need a final sort+dedup.
template <class W>
Run<W> kinkFinalizeColumn(const Run<W>& stageH, int H, int maxn, bool fold) {
  const int kLen = H + 2;  // whole-column kernel's end-of-column key width
  Run<W> next;
  next.reserve(stageH.size());
  for (const auto& rec : stageH) {
    if (!rec.sig.b[H + 3]) continue;  // empty column = completion, not extend

    const unsigned char outgoing = rec.sig.b[H + 2];
    Sig t = rec.sig;
    t.b[H + 2] = 0;
    t.b[H + 3] = 0;
    if (outgoing != 0 && !labelInMixedState(t, H, outgoing)) continue;

    const int ms = rec.minSize();
    if (ms < 0) continue;  // empty count-vec (degenerate, skip)

    canonicalizeSig(t.b, H);
    if (ms + completionLowerBound(t.b, H) > maxn) continue;
    if (fold) foldSig(t, H);

    RunRecord<W> succ;
    succ.sig = t;
    succ.H = H;
    succ.keyLen = kLen;
    succ.lo = rec.lo;
    succ.len = rec.len;
    succ.counts = rec.counts;
    next.push_back(std::move(succ));
  }
  sortRun(next);
  deduplicateRun(next);
  return next;
}
