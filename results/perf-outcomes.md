# Engine performance pass — outcomes (post-profiling)

Driven by the Track B profiling (results/{map-profile,merge-ledger}.md). Every
candidate was measured before shipping; byte-exactness (a14/a16/a18 `--compare`)
is the acceptance gate for anything that touches the sort/merge/combine path.

## Shipped (measured win, byte-exact, gated)

| Change | Win | Validation |
|---|---|---|
| **`combine` grow-in-place** (run.h) | 0 allocs on the in-window path (was 1 malloc+copy+free/collision); map sort+dedup phase 39%→32% at maxn18 | red-first `gate_run` + a14/a16/a18 |
| **`sigCmp`** 8-byte-chunk key compare (signature.h) | **1.29–1.52×** on the sort + merge-heap comparator (13 sites) | microbench same-order=1; a14/a18 |

## Measured and REJECTED (no win / wrong tradeoff)

| Candidate | Why not |
|---|---|
| **Indirect sort** (sort an index array, permute once) | Measured **0.61× — slower**. `std::sort` already moves the cheap 72-byte records well; the permute's random access + index-sort overhead lose. |
| **Radix sort** of the terminal buffer | Out-of-place radix needs an N-record temp buffer — extra RAM at the exact moment the buffer is at `--ram` (the spill trigger). Conflicts with the spill purpose; in-place (American-flag) is bug-prone for a correctness-critical sort. Not worth it given the indirect-sort result shows record-movement isn't the bottleneck. |
| **`combine` left-extension in-place** (`o.lo < lo`) | Rare case; in-place needs a right-shift `memmove` + selective zeroing — bug-prone for a marginal gain. Kept the fresh-alloc fallback. |
| **Counts pool / arena** (the headline ~14% candidate) | Built on a worktree (`PoolAlloc<W>`, thread-local free-list by size, byte-exact a14/a16/a18). A/B'd vs baseline on real multi-process orchestrate runs: **0.5% slower at production ram, 0.9% slower multi-spill** — a consistent small *loss*. The system allocator already keeps per-size-class thread-cache freelists for these millions of identical small allocations, so a userspace pool just duplicates it with extra indirection. The "14%" was a `driver1` single-process leaf-sample artifact, **not a production wall cost**. Worktree abandoned, not merged. A true bump-arena would only save the malloc *call* overhead (already small in production) at a RAM/lifecycle cost — not worth it. |

## Deferred — real win, but blast radius too large for a pre-record rush

| Candidate | Measured potential | Why deferred |
|---|---|---|
| **Hardware CRC32C** instead of byte-wise FNV-1a | **10.6×** on the hash (1.0 → 10.6 GB/s); `__attribute__((target("crc"/"sse4.2")))` needs **no global build flags** (compiles clean on arm64 + x86-64) | It's a checksum **format change**. The checksum is consumed by 7 Go files (verify, runcat, manifest, runref, idx_test, crc_test) + 2 C++ (runfile.h, checkpoint.h). Shipping it safely means a back-compat format-version dispatch across **both languages** so existing a(23) run files + checkpoints still verify. ~5% of total compute for a 9-file cross-language change. Do it as a focused effort with its own validation, not bundled in. |

## Bottom line

Two clean wins shipped (combine, sigCmp). Everything else the profiling pointed
at was measured and **did not pan out**: the terminal sort doesn't beat
`std::sort`; the counts pool (the headline ~14% candidate) is a measured *loss* in
production because the system allocator already pools same-size small allocations.
The one remaining real lever, CRC32C (~5%), is a cross-language format change held
for a focused effort. Net: the engine was already well-tuned — the profiling's
biggest apparent levers were artifacts of single-process micro-profiling, and the
real win is the **a(24)→a(25) ladder + k=8 injection (~38% wall)**, which carries
zero engine risk.
