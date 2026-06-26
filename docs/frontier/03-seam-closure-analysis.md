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

## Gate 1 RESULT (measured 2026-06-26, bench_column sort backend) — PASS, S≈1.0
Sort backend implemented (map unchanged; `slot()` appends, `consolidate()` argsorts by sig under
the oracle's `memcmp` order + merge-sums count-vectors). **Oracle byte-identical to hash at both
sizes** — S is meaningful.

| n | src→out states | hash states/s | sort states/s | **S = hash/sort** | reduce % of wall |
|---|---|---|---|---|---|
| 14 | 55409→51314 | 1.183e4 | 1.176e4 | **1.006** | 3.4% |
| 15 | 137528→129337 | 6.214e3 | 6.544e3 | **0.950** | 2.6% |

**S≈1.0 — no measurable in-RAM compute tax.** The wall is the shared `stepColumnSquare8` closure
math (the map); the store/reduce is a single-digit-% slice for both backends, so swapping hash→sort
barely moves it. The O(m log m) tax is visible but tiny: per-emission reduce cost grew ~66→73 ns
(+10%) over a 3.1× emission jump (log-m consistent); log₂m runs 15.7 (n=14) → ~27 (a(23) pole), so
the reduce fraction might grow ~1.7× — from 3% to ~5%, still negligible vs the ≤3–4× gate.

**RSS caveat (expected, not a defect):** the in-RAM sort holds ALL pre-merge emissions (n=14:
2.27M records for 51k outputs, ~44× fan-out) → peak RSS ~13× hash (808 vs 62 MB). This is the
artifact the in-RAM prototype can't avoid; **the real engine spills those sorted runs to NVMe** —
i.e. the RSS blowup is exactly what external-memory sort is designed to stream away, not hold.

## Where 03 stands now
- **Gate 1 (in-RAM compute tax): PASS** — restructure is compute-free (S≈1.0). Best possible setup
  going into the external test: 03 carries NO compute penalty.
- **Gate 2 (no random mid-merge lookup): PASS** — confirmed operationally (map never reads the
  sorted stream).
- **C2 (external-memory verdict): OPEN** — the question is now purely I/O: can sequential
  spill+merge of sorted runs beat the random-access RAM the hash engine OOMs on? Needs the
  sequential-vs-random bandwidth ratio L on dalby/ayr (a cheap fio-style microbench) and the
  break-even cold-fraction. **This is the next measurement** — and with S≈1.0 the compute side is
  already free, so C2 alone decides 03.

**Verdict: 03 GO, gate-1 cleared with full margin. 02/05/M5 stay gated on C2 (the bandwidth test),
not on compute.**
