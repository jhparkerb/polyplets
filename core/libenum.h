// libenum — the single-source-of-truth enumeration core.
//
// This is the only header workers and gates include; arch_fitness enforces
// that nothing reaches past this seam into core internals.
//
// Exposes:
//   The transition math, derived from the older column engine in cpp/early_tm/
//   (euler.h is byte-identical to cpp/early_tm/euler.h; signature.h and
//   transition.h add sigCmp, a SIGMAX override and mask-width templates):
//     Sig, canonicalizeSig, foldSig, reflectSig, completionLowerBound  [signature.h]
//     stepColumnSquare8, forEachViableMask                              [transition.h]
//     closedEulerDelta4, quadColumnPair                                 [euler.h]
//   The enumerator's own API:
//     Classifier<Tag>, ShardCfg                                         [classifier.h, mapreduce.h]
//     RunRecord, RunWriter, RunReader                                   [run.h]
//     map_shard(), merge()                                              [mapreduce.h]

#pragma once

#include "core/signature.h"
#include "core/transition.h"
#include "core/euler.h"
#include "core/classifier.h"
#include "core/run.h"
#include "core/mapreduce.h"
