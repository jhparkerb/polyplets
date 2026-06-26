// libenum — the single-source-of-truth enumeration core (DESIGN §3).
//
// This is the ONLY header workers and gates include; arch_fitness enforces
// that nothing reaches past this seam into core internals.
//
// Exposes:
//   Trusted math (copied verbatim from cpp/tma/, never edited here):
//     Sig, canonicalizeSig, foldSig, reflectSig, completionLowerBound  [signature.h]
//     stepColumnSquare8, forEachViableMask                              [transition.h]
//     closedEulerDelta4, quadColumnPair                                 [euler.h]
//   New-system API:
//     Counter<W>, Classifier<Tag>, ShardCfg                            [counter.h, classifier.h]
//     RunRecord, RunWriter, RunReader                                   [run.h]
//     map_shard(), merge()                                              [mapreduce.h]

#pragma once

#include "core/signature.h"
#include "core/transition.h"
#include "core/euler.h"
#include "core/counter.h"
#include "core/classifier.h"
#include "core/run.h"
#include "core/mapreduce.h"
