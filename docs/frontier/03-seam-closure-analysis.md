# 03 seam-closure — dead-on-arrival smoke RESOLVED: PASS (code-grounded, 2026-06-26)

*Source: docs/frontier/03-sort-transition-engine.md (its "## Smoke test"). The pivotal free
question for the whole one-bet: can the column transition's connectivity-closure be expressed
as sort+merge WITHOUT a random mid-merge lookup? If not, 03 dies and 02/05/M5 die with it.*

## Verdict: YES — the transition is already map + reduce-by-key. **Greenlight the sort backend.**

## The actual transition (cpp/tma/sweep8.h:86–110), per source state `(sig, counts)`
1. `comps` = component count, read straight off the **canonical** signature labels (`sig.b[j]`)
   — local to this one state.
2. Closing test (`comps==1 && sig.b[H] && sig.b[H+1]`) — local.
3. `forEachViableMask(sig, H, …)` → for each next-column mask, `stepColumnSquare8(sig, H, mask,
   out)` computes the successor signature `out`. **`out` is a pure function of `(sig, H, mask)`**
   — the connectivity closure (union of the new column's cells into this state's boundary
   partition, re-canonicalized) touches *only this state's data plus the mask*. No read of any
   other state.
4. `addCounts(next, out, counts, cells, maxn)` — insert-or-accumulate `out`'s count-vector into
   the next-column map. **This is the only cross-state step**, and it is a reduce-by-key.

So one column = **map** (step 1–3: per-source-state, local closure, fan-out over masks) →
**reduce-by-key** (step 4: sum count-vectors for equal successor sigs). The successor stream of
one column is the source stream of the next; iterate it sequentially. Nothing in the closure
needs random access to the frontier.

## Why sort+merge expresses it exactly
Replace `addCounts` (hash find-or-insert) with: emit every `(out_sig, count_vec)` the map
produces to a stream, **sort by `out_sig`, merge-sum adjacent equal keys**. The closure
(`stepColumnSquare8`) is computed in the map, before the sort — it never reaches back into the
sorted stream. The merge only sums count-vectors of identical keys. The engine's own MT comment
(sweep8.h:112–128) clinches it: *"Counts only ACCUMULATE (commutative+associative), so the
result is bit-identical regardless of sharding/threading/batching."* A reduce that is
commutative+associative is precisely one a sort-merge may reorder and regroup freely.

The current batched-merge MT engine is **already a partial sort/stream**: it shards source,
routes outputs to per-thread scratch, then merges shards into `nextDB` — a hash-bucketed
reduce-by-key. The sort engine is the same reduce with a *sorted* merge instead of a hashed one.

## Subtleties (real, but none reintroduce a random lookup)
- The reduce value is a **count-vector** `counts[1..maxn]`, not a scalar → merge does a fixed-
  width vector-add per equal-key group. Still a pure reduce-by-key.
- Successor canonicalization must be **deterministic & total-orderable** for the sort key — it
  is: `foldSig`/the canonical labelling already give a byte-encodable sig with a lex order.
- Fan-out: each source state emits several successors (one per viable mask) → a flatMap, still
  streaming, no barrier.

## What this does and doesn't settle
- **Settles (smoke):** sort+merge is structurally sufficient — feasibility is not the question.
  03 is GO to prototype.
- **Does NOT settle (kill-test):** whether sort+merge is *competitive in RAM* with hashing (the
  O(m log m) vs O(m) tax, m up to ~1.7×10⁸ at the a(23) pole → log₂m≈27). That is a measured
  number, `S = (sort states/sec)/(hash states/sec)`, and the harness is now ready to produce it:
  drop a `sort` backend into `experiments/bench_column.cpp` beside the validated `hash` baseline
  (1.18×10⁴ states/sec on the n=14 fixture) and read off S. See harness-spec.md.

## Next action
Implement the `sort` backend in bench_column (the stub is already there), run it on the fixture,
compute S, then apply 03's sharpened break-even (S vs the cold-fraction the disk/RAM bandwidth
ratio can repay). Until then: **03 stays GO, 02/05/M5 stay gated behind its S number.**
