# Map-body profile — where the enumeration CPU actually goes (queue #8)

**2026-07-02.** `sample` on a live u128 map_worker (maxn=24, H=13, single sweep).
Prompted by the audit's claim that a per-successor `counts` arena (lever #2)
would save "moderate-to-large" map CPU. Measure-first before an invasive,
record-run-risky refactor.

## Result

`map_shard_file` = 3405 samples. Breakdown:
- **`s8::viableRec` (recursive viable-mask generator) ≈ 91%** — the descent
  itself, calling `stepColumnSquare8` at the leaves.
- `stepColumnSquare8` (the per-mask step) — scattered small leaf counts,
  low single-digit %.
- **`counts.assign` (`std::vector<u128>::__assign_with_size`) = 2 samples** —
  i.e. the per-successor malloc the arena would remove is **negligible**.

## Verdicts

1. **Arena allocator (#8): abandoned.** The malloc it targets is 2/3405 samples.
   The audit mis-estimated this; measurement kills it. Not worth the pmr footguns
   / record-run risk for ~0.06%.
2. **stepColumnSquare8 micro-opts (SIGMAX zero-init shrink, etc.): not worth it.**
   The whole step function is a small fraction; shrinking its per-call zero-init
   saves a fraction of a small fraction (<1%).
3. **The real hotspot is `viableRec`, and it is intrinsic + already tight.** It
   generates the viable next-column masks by a pruned binary recursion (coverage
   prune + reach prune, discarding 76% of leaves). A prior iterative rewrite
   measured ~0% (the per-node cost is already minimal), so the cost is the
   *number of nodes descended* — intrinsic to the enumeration, not overhead.

## The one lever that could actually cut map CPU

Fewer descended nodes = a **tighter completion-lower-bound prune** (queue #4):
`viableRec`'s reach prune is a slice of `completionLowerBound`. A stronger
admissible bound (Barequet's MST-based n_c on the 79%-multi-component states)
would cut subtrees earlier. That is the ONLY measured map-CPU lever — but it is
the high-risk one (an over-tight bound silently corrupts record-run counts; see
results/completion-pruning-audit.md). Requires the brute-force-oracle gating in
design #13 before any record run trusts it.

## Bottom line

Confirms the exploration arc's conclusion at the implementation level too: the
map cost is intrinsic enumeration at near-optimal per-node cost. No safe
constant-factor engineering win exists on the map side. Finish-sooner for
a28-a30 = parallelism (cross-machine split, already staged) + the small I/O
fast-path (done). The only deeper lever is tighter pruning, which trades
correctness risk for speed and must be oracle-gated.
