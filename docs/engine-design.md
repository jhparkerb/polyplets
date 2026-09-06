# Engine design — the production polyplet enumerator

Status: the build design of the run-file engine, written 2026-06-26, as built
for a(21)-a(36) (a(35) and a(36) via its varint evolution). **It is not the
engine that produced a(40) and a(41):** the kink-carry column kernel replaced
the transition of section 4 afterwards, and the engine as it actually ran, with
the measurements, is `docs/engine-record.md`. Read this one for the run-file
layer -- spilled runs, sort-merge, checkpoint and resume -- which survives
unchanged.

Names cited below that are not in the tree: `NEXT-SYSTEM.md`, the PRD,
`IMPLEMENTATION-PLAN.md` and `docs/layout.md` were the planning trilogy around
this design, removed at project close and readable in git history. `data/` is
the published-output directory this design proposed; it shipped as `results/`.

Design rule throughout: **re-express the validated engine, do not reinvent it.** Every transition,
signature, prune, and fold below is lifted from the working `cpp/tma/` code (cited inline); the *new*
work is externalizing the in-RAM `db→next` column step as sort-merge over spilled runs, and moving all
parallelism/liveness out of the C++ into a Go orchestrator.

---

## 0. The one key insight (why this is a small change, correctly framed)

Today's column step (`cpp/tma/sweep8.h:86–110`) is already a map + reduce-by-key:

```
for col in 0..maxn:                       # the sweep
  next.clear()
  db.for_each(sig, counts):               # MAP: each source state
     if completion-test(sig): classify    #   -> emit to T(n,H)
     forEachViableMask(sig, budget):       #   -> enumerate successor masks
        stepColumnSquare8(sig,mask)->out   #   -> local king-closure (the transition)
        if prune(out): continue
        addCounts(next, out, counts)        # REDUCE: accumulate count-vec into out's slot
  swap(db, next)
```

The reduce (`addCounts`) is **commutative + associative** (counts only accumulate), so the result is
**independent of how states are sharded, ordered, or batched** — the MT engine already exploits this and
is bit-identical to serial (`sweep8.h:130–131`, gate case M). That property is exactly what an external
merge-sort needs:

- **MAP** = `db.for_each` over a *shard* of source states → a buffer of `(out_sig, contribution)`
  records → **sort by `out_sig`** → spill a sorted run.
- **REDUCE** = **k-way merge** the sorted runs; equal `out_sig` keys combine by `addCounts` (range-union +
  vector-add). Output = the next column's frontier as sorted run(s).

No random-access hash table; sequential spill/merge only (NVMe seq out-runs random RAM 2–4×, C2). The
`FlatDB` open-addressing map (`statedb.h`) is *replaced* by sorted runs; everything else — `Sig`,
`canonicalizeSig`, `stepColumnSquare8`, `forEachViableMask`, `completionLowerBound`, `foldSig`,
`closedEulerDelta4` — is **reused verbatim** behind the `libenum` seam.

## 1. Component map (concrete)

```
              ┌─────────────────────── Go orchestrator ───────────────────────┐
              │  scheduler (column DAG, shard queue, work-stealing)            │
              │  governor (budget, graceful stop)   checkpoint (wall cadence)  │
   launch ───▶│  store (local NVMe v1)   telemetry   manifest                 │
              └───┬───────────────────────────────────────────────┬───────────┘
        spawns    │  hands (run paths + key-range + cfg)           │  reads runs/cursors (files only)
                  ▼                                                 ▼
        ┌── C++ map_worker ──┐   ...(N procs)...      ┌── C++ merge_worker ──┐
        │ read run(s)        │                        │ read runs (key-range)│
        │ libenum.map_shard  │   sorted runs on NVMe  │ libenum.merge        │
        │ write sorted run   │ ─────────────────────▶ │ write merged run     │
        │ exit + accounting  │                        │ exit + accounting    │
        └────────────────────┘                        └──────────────────────┘
                  ▲                                                 ▲
                  └──────────────── libenum (C++, single source of truth) ────┘
                       Sig · transition · classifier<C> · counter<W> · run I/O · map_shard/merge

        ┌── Go verifier (separate tool) ──┐   reads published data/ → consistency + spot-check
```

**Cardinal rule (carved in stone, NEXT-SYSTEM.md):** the orchestrator touches **runs (files)**, never
individual states. The C++ worker is the only code that ever sees a `Sig`, and it sees millions per call
in a tight loop. That boundary IS the `libenum` API seam AND the fault/checkpoint boundary.

## 2. State representation (lifted from `cpp/tma/signature.h`, unchanged)

- **Signature `Sig`** = boundary connectivity of a partial animal in one column: `H+2` bytes —
  `b[0..H)` = component label per boundary row (0=empty, else label), `b[H]` = touched-top flag,
  `b[H+1]` = touched-bottom. Labels canonicalized (relabel 1,2,… in first-occurrence order,
  `canonicalizeSig`). Crossing partitions allowed (king connectivity needs them — no Motzkin shortcut).
- **Sort key = the canonical sig bytes**, `memcmp`-ordered → endian-neutral, equality = byte equality,
  merge of equal keys is well-defined. *The key is the state; there is no separate key.*
- **Value = the count-vector** `counts[n]` = (number of partial animals with this boundary that have
  placed exactly `n` cells), stored **ranged**: a contiguous nonzero window `[lo, lo+len)` (~0.56·n
  wide, B.RESOLVED) — the keystone ~1.9× memory win. Width `W` per entry = 8 B (u64) or 16 B (u128).
- **R1 symmetry fold (`foldSig`)** optional: store only the vertical-mirror-canonical sig, ~2× fewer
  states, byte-identical totals. v1: on (validated `r1_sym_fold_check.py`).

## 3. `libenum` public API (the fitness-function seam)

The entire trusted surface. Header `core/libenum.h` is the ONLY thing workers include; `arch_fitness`
forbids anything else reaching past it. Classifier and counter are **compile-time templates**
(monomorphized — they are in the per-state hot loop, millions of calls/shard; a vtable indirection there
is unaffordable). The store is **not** in the hot loop, so it is a runtime interface in Go, not here.

```cpp
// ---- counter seam (template; W in the value width) ----
//   Counter<u64>  valid to a(25);  Counter<u128> to ~a(48);  Counter<ModP> = GF/shadow path.
template <class W> struct Counter { /* +=, widening where needed; ModP carries a prime */ };

// ---- classifier seam (template; the reduce's completion side) ----
// O1 triangle: on a closing column, a single component touching top+bottom of height H
//              contributes counts[n] to T(n,H).  (sweep8.h:95–96)
// O2 holes:    same, but keyed by (n,H,holes) using closedEulerDelta4 carried in the value.
// O3 GF:       counter=ModP; classifier accumulates residues per (H,n) for CRT recovery.
template <class Counter> struct Classifier {
  void complete(const Sig&, int H, const Value<Counter>&, Output&);   // emit to triangle/holes/residues
  // reduce op is fixed: union-range + componentwise Counter::+=   (addCounts, commutative/associative)
};

struct ShardCfg {
  int H, maxn; bool fold;            // sweep params (one height-sweep per H; a(n)=Σ_H)
  Key lo, hi;                        // [lo,hi) source key-range this shard owns (half-open, memcmp)
  size_t ram_budget_bytes;          // spill when the sort buffer would exceed this
  // counter/classifier are template params of the instantiation, not runtime fields
};

// MAP one shard: stream source states in [lo,hi) from in_runs, run the transition, emit
// successor records, sort, spill sorted runs, k-way-merge own spills -> ONE sorted out run.
// Also drives the classifier completion side, accumulating into `out_classified`.
template <class Counter, class Classifier>
RunRef map_shard(SpanOf<RunRef> in_runs, const ShardCfg&, RunWriter& out, Output& out_classified);

// REDUCE: k-way merge sorted runs over an output key-range [klo,khi); equal sigs combine
// (range-union + Counter::+=). Output = one sorted run covering [klo,khi).
template <class Counter>
RunRef merge(SpanOf<RunRef> in_runs, Key klo, Key khi, RunWriter& out);

// run (de)serialize + the sort-key contract live in run.h; transition/sig/prune are the
// existing headers (signature.h, transition_square8.h, euler.h) moved under core/ unchanged.
```

`RunRef` = an opaque handle (path + record count + key-range + CRC) the orchestrator passes around;
workers open it through the store. `map_shard`/`merge` do **no scheduling, no policy, no networking** —
they read named inputs and write named outputs. That is the whole contract.

## 4. The map algorithm (inside `map_shard`)

```
buf = []                                  # (out_sig, ranged-contribution) records
for each source state (sig, value) in in_runs restricted to [lo,hi):     # sorted stream, no random access
    ms = minSize(value)
    if completion-test(sig,H): classifier.complete(sig,H,value,out_classified)   # O1/O2/O3
    forEachViableMask(sig,H, maxn-ms, mask):                  # transition_square8.h, verbatim
        if stepColumnSquare8(sig,H,mask,out_sig) != Alive: continue
        cells = popcount(mask)
        if ms+cells+completionLowerBound(out_sig,H) > maxn: continue   # admissible prune, verbatim
        if fold: foldSig(out_sig,H)
        buf.append( (out_sig, value shifted by cells) )       # the addCounts contribution
        if bytes(buf) > ram_budget: sort(buf by out_sig); spill_run(buf); buf=[]   # mid-shard spill
sort(buf by out_sig); spill_run(buf)
return kway_merge(my_spilled_runs)        # one sorted run; equal sigs pre-combined here
```

Heavy-tailed per-state cost is fine: shards are 10⁴–10⁵ states so the worst single state is ≤0.1–1.3% of
a shard (C-4, monster verdict GO). Spilling is the *continuous mid-shard checkpoint* — a kill loses only
the records since the last spill.

## 5. The merge algorithm (inside `merge`)

Standard external k-way merge with a binary heap keyed on `memcmp(sig)`:

```
heap = one cursor per in_run (each run sorted ascending), seeded with first record ≥ klo
while heap.top.key < khi:
    group = pop all records with the minimal equal sig
    combined = fold-reduce group by (range-union of [lo,hi] + componentwise Counter +=)
    emit combined
    advance the popped cursors
```

Output is one sorted run for `[klo,khi)`. Equal keys across runs are where the column's reduce actually
happens (a sig produced by many source states/shards). Combine is associative ⇒ correctness is independent
of run order and partition cuts (the bit-identical property, §0).

## 6. The sweep driver (the column DAG, in the Go orchestrator)

One **height-sweep** per H ∈ [1, maxn]; `a(n) = Σ_H T(n,H)` (G-stratification is free, §G of design record).
Within a height-sweep:

```
frontier = [ seed run: the empty boundary, counts[0]=1 ]          # col 0
for col in 0..maxn while frontier nonempty:
    # MAP PHASE — partition source key-space into many shard units, dispatch to worker pool
    units = partition_keys(frontier, target_states≈10⁴–10⁵ per unit)   # thousands ≫ cores
    map_runs = workpool.run(map_worker, units)            # dynamic pull-queue + tail-steal (§7)
    # MERGE PHASE — partition OUTPUT key-space into ranges, dispatch merge workers
    ranges = sample_cut_points(map_runs, target≈cores)    # even split by sampled keys
    frontier = workpool.run(merge_worker, ranges)         # each merges its slice across all map_runs
    checkpoint(col, frontier, accounting)                 # the completed runs ARE the checkpoint
```

Map-phase output (many small runs) feeds the merge phase (few balanced runs = next frontier). The
completion contributions accumulate into the triangle as a side output of every map unit, summed at
height-sweep end. This is N iterative MR jobs — exactly why no off-the-shelf framework fits (iteration-
unaware); the loop is ~40 lines of Go.

## 7. Work-stealing & straggler closure (cross-process — the key mechanism)

All coordination is orchestrator-mediated; **C++ workers never talk to each other or share memory**
(matches single-threaded-worker decision, NEXT-SYSTEM.md). Three layers, in order of how often they fire:

1. **Fine-grained pull-queue (handles ~99%).** The map phase is thousands of shard units; a fixed pool of
   ≈`cores` worker processes each pulls the next unit when idle (the orchestrator's queue is the "atomic
   cursor" — dynamic by construction, never static striding, which the data shows tail-stalls on late
   columns, C-4). Unit grain 10⁴–10⁵ states = seconds–minutes each ⇒ natural balance, spawn cost <0.1%.
2. **Straggler tail-split (rare; the one genuine outlier unit).** A map_worker periodically (wall cadence)
   writes a *cursor* (how far through `[lo,hi)` it has mapped) alongside its spilled runs. If the
   orchestrator sees a unit running ≫ the median, it hands the **untouched tail** `[cursor,hi)` to an idle
   worker as a new unit and signals the straggler to stop at `cursor`. Both halves' spilled runs feed the
   merge. No shared cursor — the cursor is a file the orchestrator reads; Go owns the decision.
3. **Partitioned merge (kills the merge barrier).** The merge phase splits the *output* key-space into
   ≈`cores` ranges by sampling keys for even cut points, so no single merge worker is the long pole.
   (Optional v2: pipeline merge(col)→map(col+1); not in v1.)

Residual imbalance is advisory (scheduling only), never load-bearing on correctness or work-safety.

## 8. Worker process contracts (C++, thin)

Both are `read named inputs → call one libenum function → write named output + accounting → exit`. No
threads, no shared state, process = fault/checkpoint boundary.

- **`map_worker`** argv: `--in run1,run2,… --lo HEX --hi HEX --H h --maxn n --fold 0|1 --ram BYTES
  --counter u64|u128|modp:P --classifier triangle|holes|gf --out PATH --cursor PATH`. Emits the out run +
  an `event=done` accounting line (`cpu_s wall_s peak_rss records spill_bytes`). On SIGTERM from the
  governor: flush current buffer to a final spill, write `cursor`, exit cleanly (graceful stop).
- **`merge_worker`** argv: `--in run… --klo HEX --khi HEX --counter … --out PATH`. Emits merged run +
  accounting. Pure function of its inputs (idempotent ⇒ safely re-runnable on resume).

Idempotency + named deterministic outputs ⇒ a re-dispatched unit (after a crash) reproduces the same run
byte-for-byte; the orchestrator can always re-run a lost unit rather than reason about partial state.

## 9. On-disk formats (concrete — `docs/formats.md` is the published spec)

Principle: **text where humans/verifiers read, documented binary where the machine streams** (NEXT-SYSTEM.md).
Everything is renderable to text by `runcat` (the `git cat-file` model) so nothing is ever opaque.

**Sorted run record** (the hot bulk — binary):
```
[ sig: (H+2) B canonical, memcmp-sortable | lo:u8 | len:u8 | counts[len]: len*W B LE ]
  └── KEY (fixed per height-sweep) ──┘   └──────── VALUE: ranged count-vec, W∈{8,16} ───────┘
```
At H=21: 23 + 2 + 12·8 ≈ 121 B/record, matching the independently-derived ~110 B/state floor (B.RESOLVED).

**Run file** = PPM-style text header + binary body, one head-able artifact:
```
POLYRUN 1\n
height H\n  maxn N\n  counter u64|u128|modp:P\n  classifier triangle|holes|gf\n
keylo HEX\n  keyhi HEX\n  records M\n  rev <gitrev>\n  byteorder 1\n
\n
<M binary records, ascending by sig>  <8-byte body CRC>
```

**Checkpoint = text** (`POLYCKPT` — the bulk is the runs already on disk; this just names them):
```
POLYCKPT 1\n  job <id>\n  H h\n  col c\n
done_runs <path…>\n            # completed map/merge units this column
inflight <unit:lo-hi cursor:HEX run:path>…\n   # straggler tails mid-flight
frontier <path…>\n             # the current column's merged runs (resume source)
acct cpu_s=<SUM> wall_s=<SUM> rss_max=<MAX>\n   # the resume fold-in
```
Resume = reload frontier runs, re-dispatch not-done units (and inflight tails from cursors), seed
accounting from `acct` (cpu/wall SUM, rss MAX). A readable header alone would have made this session's H19
staleness debug a one-line `cat`.

**Result/verification text artifacts:** triangle `# n H T(n,H)` (a(n)=Σ_H); manifest (per-a(n): rev,
cpu·s, wall, peak RSS, spill bytes, run list, CRCs); mod-p residues `# n prime residue`. All
greppable/diffable/publishable — they ARE the publish-and-verify deliverable (G6).

**Sig encoding:** byte-per-cell (H+2) for v1; order-preserving 4-bit pack (still memcmp-sortable, no
unpack to compare/merge) is a contained later swap (~H/2 B) deferred purely to keep v1 core minimal.

## 10. Evolvability seams (G7 — how each swap is a drop-in)

| Seam | v1 | swap | mechanism | touches core? |
|------|-----|------|-----------|---------------|
| **counter** | `u64` | `u128` (≤a48), `ModP` (GF/shadow) | template param `W`; value width self-described in run header | no — recompile, new run files |
| **classifier** | `triangle` | `holes`, `gf` | template param; completion side only | no |
| **store** | local NVMe | distributed / cloud | Go `Store` interface (`put/get/list/open RunRef`) — runtime, cold path | no (Go only) |
| **distribution** | single-box pool | multi-box | orchestrator hands units by key-range; runs migrate freely (sorted-run partition) | no |
| **sig packing** | byte/cell | 4-bit pack | localized in `run.h` (de)serialize; merge never unpacks | core-local, behind seam |

The counter and classifier swaps recompile the C++ (a new monomorphized binary, rev-stamped); the store
and distribution swaps are Go-only. None edits the transition/signature/prune math — the trusted ~680 lines.

## 11. Validation & fitness functions (NFR-1 — build-failing gates)

Layered by failure mode (NEXT-SYSTEM.md "Validation strategy"); each maps to PRD acceptance gates:

| Gate | Catches | Mechanism | AC |
|------|---------|-----------|-----|
| `gate_regression` | gross bug | new engine T(n,H) byte-identical to old engine + pinned fixtures, small n | AC-0,1 |
| `gate_fold` | fold bug | fold == unfold, byte-identical | AC-0 |
| `gate_rowsum` | classifier bug | Σ_H T(n,H) == a(n) for known terms | AC-1 |
| `gate_resume` | checkpoint bug | kill-at-random-wall then resume == uninterrupted, byte-identical | AC-2 |
| `arch_fitness` (Go) | boundary erosion | core imports no I/O; nothing reaches past `libenum.h`; classifier/counter only via templates | all |
| `gate_modp` | arithmetic/transient | multi-prime mod-p shadow + CRT consistency | AC-4,5 |
| `gate_crossengine` | impl bug | **new a(22) == old a(22)** — the trust milestone | AC-3 |
| verifier (separate) | impl bug (public) | independent Go tool re-checks published runs/residues + spot-checks sampled shards | AC-5 |

The cross-engine gate (AC-3) is the de-risking core: a(23) is **not trusted on faith** — the new engine
must out-reproduce the old on a(22) first. For a(23) itself (no oracle) trust rests on: small-n regression
+ row-sum + mod-p shadow + the published-dataset-anyone-can-recompute (the accepted status of a record's
leading edge — counting has no succinct certificate, verify ≈ recompute).

## 12. Verifier (Go, separate tool — G6)

Reads only the published `data/` (runs, manifest, residues) + `formats.md`; needs neither our code nor
our hardware. Checks: (1) **consistency** — row-sum identity, mod-p CRT agreement, growth-ratio
smoothness; (2) **integrity** — every run's body CRC, manifest ↔ run cross-references; (3) **spot-check** —
re-run sampled shards through a fresh `map_worker` and compare byte-for-byte to the published run. This is
the modern "check it yourself" gold standard; it enables others' consistency checks + spot-checks +
full recompute, not a cheap full proof (none exists for counting).

## 13. Repo layout (promotes `docs/layout.md`, adjusted for holes/GF in v1)

`core/` (libenum ~700) · `worker/` (map+merge ~160) · `orchestrator/` (Go ~1820) · `verify/` (Go ~700) ·
`test/` (gates + `arch_fitness.go` ~330) · `data/` (published triangle/manifests/residues) ·
`docs/` (NEXT-SYSTEM, correctness, formats). Total ~3.7k LOC vs ~13.1k today. **v1 is a strict subset
(~2k LOC):** core + worker + a simple orchestrator (scheduler+governor+checkpoint, no store-abstraction/
distribution) + regression/fold/resume gates + the verifier's consistency checks. Holes = the `holes`
classifier template (reuses `euler.h`); GF = `counter=ModP` + `gf` classifier — **both are configs of the
one core, not the absent Python tree** the layout sketch retired. `store.go` pluggability, distribution,
and `spotcheck.go` grow later (scale-by-replacement).

## 14. Open design decisions (to confirm before/while planning)

These are the judgment calls made above where an alternative is defensible — flagged for review so the
IMPLEMENTATION-PLAN builds on a confirmed base:

- **D-1 Worker model = process-per-shard-unit** (spawn, map one unit, exit), not a long-lived worker pool
  reading units over a pipe. Chosen for the clean fault boundary + <0.1% spawn cost at unit grain.
  *Alternative:* persistent worker pool (lower spawn cost, but workers hold state across units → muddier
  fault model). Confirm.
- **D-2 Straggler tail-split via orchestrator-read cursor files** (§7.2), not a shared-memory cursor or
  worker-to-worker handoff. Keeps all coordination in Go. Confirm the cursor-file cadence is acceptable
  overhead.
- **D-3 v1 builds the `Store` as a thin Go interface but only the local-NVMe impl** (define the seam,
  don't over-build for deferred multi-box). Matches "start small" + keeps the swap cheap later.
- **D-4 Checkpoint granularity = shard-unit** (a lost in-flight unit is re-run whole; no sub-unit worker
  checkpoint in v1 except the straggler cursor). Loss bound = one unit (seconds–minutes), well inside
  "bounded loss" (NFR-2). Sub-unit resume is unnecessary at unit grain.
- **D-5 Counter/classifier = compile-time templates** (monomorphized, in the hot loop); store/distribution
  = runtime (cold). This is forced by the hot/cold boundary, not a free choice — noted for completeness.
