// counter.h — Counter type tags and widening guards (DESIGN §3, evolvability §10).
//
// The counter is a compile-time template parameter on RunRecord and on the
// map_shard/merge instantiations. Two concrete tags:
//   CounterU64  — exact counting valid to a(25)
//   CounterU128 — exact counting valid to ~a(48)
//
// The actual arithmetic is just native +/= on u64/u128; the tag type exists to
// (a) let the Makefile build separate rev-stamped binaries per width, and
// (b) carry the width into the run-file header so readers know the record size.
//
// Widening guard: if the configured counter word cannot hold the target n, the
// binary must refuse at start (FR-7). The guard is applied in the orchestrator
// (which knows maxn) before workers are spawned; workers trust their configuration.

#pragma once
#include <cstdint>

using u64  = std::uint64_t;
using u128 = unsigned __int128;

struct CounterU64  { using Word = u64;  static constexpr int width = 8;  };
struct CounterU128 { using Word = u128; static constexpr int width = 16; };

// Sentinel: counter overflow is silent (counts only grow; wrap is detectable
// post-hoc via mod-p shadow, but the design prevents reaching it by refusing
// to start with an undersized counter).
