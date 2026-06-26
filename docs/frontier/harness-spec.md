# Frontier harness — shared smoke fixture + single-column micro-bench
*Source: docs/frontier/README.md §"Do-first ordering" — implements the shared infra the do-first
items lean on: a standing **smoke** (#1, the minutes-cheap dead-on-arrival check each idea file's
`## Smoke test` section invokes) and the **sort-vs-hash micro-bench** (#2, the load-bearing
states/sec + byte-equality prototype). Backends served: 03-sort-transition-engine.md,
oq1-i7-hot-slot.md, 01-state-compression.md, 09-u128-counters.md.*

Today every engine-swap idea (03 sort/merge, oq1 lock-free, 01 compression, 09 u128) is a bespoke
prototype with its own ad-hoc "is it right / is it fast" scaffolding. This spec defines the **two
shared pieces** all four reuse, so each idea collapses to *a backend + a row in one table*:
apples-to-apples states/sec and shared correctness from day one.

The seam is `cpp/tma/statedb.h` — `FlatDB::slot()` (find-or-insert → counts row), `for_each()` (the
only read-back path), `addCounts()` (shift+accumulate). README/frontier-revision-plan call it "the
designed-to-be-replaced component"; both pieces below drop in *behind* it.

## Part 1 — Standing smoke fixture

A FIXED, off-frontier `(N,H)` that runs in **well under a minute on one core**, gate-checkable,
runnable anytime — the dead-on-arrival check every idea's `## Smoke test` cites.

**Fixture:**
```
build/tma square8 14 --only-height 12
```
**Measured (gympie, one core):** wall **27 s**, peak_states **55409** (stderr `peak_states 55409
peak_height 12`), peak RSS **~28 MB**. Big enough to drive a real column transition through the
height-12 frontier (55k live signatures, a grow or two, a full seam-closure), small enough to fit
in L3-ish and finish before you look away. Result line: the height-12 marginal of A006770 over
n≤14 (a partial-by-height count, NOT a(14)).

**Expected exact output:** byte-identical to the **dense FlatDB baseline** — the value `build/tma`
emits *now*. It must reproduce that exactly; a backend swap that changes one count is a defect.
The canonical full-sequence values already live in `fixtures/b006770.txt` and the gate
(`tests/gate_tma.py`) already knows them (cases A/D check totals vs the b-file; M checks
`--only-height` folded==unfolded). The smoke is the *cheap* sibling of those, not a new oracle.

**Gate plug-in (`gate_tma.py`):** add one case after L/M, same shape as the others — capture the
dense baseline once, assert each backend reproduces it byte-for-byte:
```python
# N. smoke fixture: every engine-swap backend reproduces the dense column exactly.
base = run(TMA, "square8", 14, "--only-height", 12)            # dense FlatDB baseline
for backend in ("hash", "sort", "concurrent", "compressed", "u128"):
    got = run(TMA, "square8", 14, "--only-height", 12, "--backend", backend)
    gate.check(got == base, f"N smoke {backend:10} square8 H12 N14 == dense baseline")
```
(`hash` is the existing path; absent backends are skipped until built. Reuse the gate's
`run`/`parse_counts` exactly — same byte-identical notion as A–M.)

**Why a FIXED fixture, decoupled from the frontier job:** repeatable (same `(N,H)`, same expected
bytes, every run), **zero frontier risk** (never touches the live a(21)/a(22) pole), runnable
anytime on any box in seconds — versus scavenging a test column off a multi-day production run,
which is unrepeatable, perishable, and one fat-finger from disturbing the real job. The smoke is the
floor every idea trips over *before* anyone spends a day on its kill-test.

## Part 2 — Single-column micro-bench harness

A standalone driver `experiments/bench_column.cpp` (built per the experiment convention: single
`.cpp`, `g++ -std=c++20 -O3`, count-equality gate) that:

1. **loads or regenerates a FIXED input column** at n≈14–16 — the height-12 (or H14/N16) boundary
   frontier from the smoke fixture, captured once via `for_each()` to a file and replayed, so every
   backend runs the *identical* input (no enumeration noise in the comparison);
2. runs **ONE column transition** through a **selectable backend** (`--backend NAME`);
3. measures **states/sec + peak RSS** (plus per-backend counters, below);
4. asserts the output column is **BYTE-IDENTICAL to the dense hash baseline** — the correctness
   oracle, reusing the gate's notion: serialize `for_each()` in a canonical (sorted-by-sig) order
   and compare bytes against the `hash` backend's output. A non-matching backend FAILS the run; you
   never benchmark a wrong engine.

### Backend interface (the swappable seam)

A backend implements the three `statedb.h` operations and nothing else — the transition logic
(neighbour enumeration, seam-closure, `addCounts` shift) is written once against this interface and
never edited per backend:
```cpp
struct Backend {                       // modelled on FlatDB
  void   reserve(size_t nStates);      // pre-size to skip grows (FlatDB::reserve)
  Row    slot(const Sig& k);           // find-or-insert -> mutable counts row (FlatDB::slot)
  template<class F> void for_each(F&&); // canonical read-back (FlatDB::for_each) -> oracle compare
  Metrics metrics() const;             // states/sec contributors + per-backend counters
};
```
`Row` is `u64*` for hash/sort/concurrent/compressed and a `u128*` view for u128 (the counter axis is
the only thing that changes there). `addCounts(db, sig, src, shift, maxn)` stays as-is — it only
calls `slot()`. Swapping the backend swaps the store; the sweep never knows.

### Backends and which idea each serves

| `--backend` | store | serves | what it proves |
|-------------|-------|--------|----------------|
| `hash` | current FlatDB (statedb.h) | baseline | the oracle + the states/sec all others are scored against |
| `sort` | sorted (sig,row) stream, sort+merge transition | **03** | in-RAM sort-vs-hash slowdown **S** at n=14–16 (no random find-or-insert) |
| `concurrent` | `ConcDB`: open-addr, CAS slot-claim + atomic row-accumulate | **oq1** | lock-free shared table holds scaling at full T, 1-copy RAM |
| `compressed` | ranged-row / packed-signature FlatDB | **01** | bytes/state cut, ranged-row width, byte-identical under packing |
| `u128` | FlatDB with `__uint128_t` rows | **09** | **counter** swap, not a store swap — a different axis (note below) |

**u128 is a different axis.** 09 changes the *counter type* behind `addCounts` (u64→`__uint128_t`,
add+adc, no CRT), not the store's access pattern. It composes with any of hash/sort/concurrent.
Benched here for the same byte-equality + states/sec table, but its real contest is vs interleaved
31-bit CRT in `experiments/crt_counter_bench.cpp` (which it EXTENDS) — keep the counter-width arm
there; this harness just confirms a `u128`-row store stays exact and within traffic budget (16 B vs
12 B/count).

### Metrics emitted

Per `(backend, column)`, one kill-safe line (printed + appended+flushed to `--out`, like
crt_counter_bench):
- **states/sec** — output states produced per second on the single transition (the headline);
- **peak RSS** — high-water bytes (the RAM-cliff axis oq1/01 live on; 1-copy vs batched-2×);
- **03 only:** in-RAM **slowdown S** = (sort states/sec) / (hash states/sec) — the exact input the
  03 kill-test's sharpened break-even needs (NO-GO if real cold-fraction can't reach `f*` where
  `f*·L ≈ S`; the harness reports **S**, the doc computes `f*`);
- **oq1 only:** **CAS-retry iterations/insert** and **fetch_add attempts on top-1% hottest slots**
  — the contention counters whose serialization sets oq1's wall (NO-GO if column throughput
  < ~0.5× batched);
- **01:** bytes/state and mean ranged-row width (`hi−lo+1`) — the shift factor;
- **09:** ns/accum + GB/s (cross-referenced to crt_counter_bench's arm).

### The payoff

Every engine idea becomes **a backend + a row in one comparison table** — same fixed input column,
same byte-equality oracle, same states/sec/RSS columns — instead of four bespoke prototypes with
incomparable numbers and four separate correctness stories. Apples-to-apples from day one.

## Build & run
```sh
g++ -std=c++20 -O3 -o build/bench_column experiments/bench_column.cpp

# capture the fixed input column once (from the smoke fixture frontier), then bench each backend:
build/bench_column --capture square8 14 --only-height 12 --out experiments/col_n14.bin
build/bench_column --backend hash       --in experiments/col_n14.bin --out experiments/bench_column_results.txt
build/bench_column --backend sort       --in experiments/col_n14.bin --out experiments/bench_column_results.txt
build/bench_column --backend concurrent --in experiments/col_n14.bin --threads 8 --out experiments/bench_column_results.txt
```
Each `--backend` run asserts byte-identical-to-`hash` before reporting; a mismatch exits nonzero
(the count-equality gate, matching the experiment convention). Smoke fixture needs no build —
it is the existing `build/tma`.

## Effort
Smoke fixture + gate case N: **XS (ESTIMATE)** — one gate block, no new binary. Micro-bench
harness + the two baseline backends (`hash`, `sort`): **S (ESTIMATE)**. Each further backend
(`concurrent`/`compressed`/`u128`) rides the same harness at its own idea's effort. *T-shirt sizes,
never a wall-clock.*
