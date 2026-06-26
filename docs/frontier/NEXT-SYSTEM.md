# Next-system design space — investigation tracker

Goal: know **everything needed to DESIGN** the next-generation polyplet enumeration system —
not just evaluate the ideas we already have. Method: surface gaps → theorize the likely answer →
list ways to **falsify** it cheaply → smoke-test → confirm survivors → iterate until the design is
determined. Confirmed results are inputs, not fences.

## Design philosophy (jasonp, 2026-06-26)
**Evolvable / component-swappable.** Start "small" (a(24): single-box, NVMe-spill, by-height-
triangle output) and **scale by replacing components**, not rewriting, up to the limits of
feasibility.
- **Reach ladder:** a(24) → a(26) (u64→u128 boundary) → a(30)+ → as-far-as-feasible.
- **Distribution ladder:** single-box+NVMe-spill → multi-box manual-relay → cloud/new HW.
- **Counting ladder:** u64 (≤a(25)) → u128 (≤~a(48)) → bignum.
- **Output:** by-height triangle T(n,H) is the **irreducible minimum** (a(n)=Σ_H T(n,H)); holes +
  GFs are optional and get **dropped the moment they cost the design** flexibility.
- **Algorithm is REOPENED:** the validated sort/stream TM column-sweep is the incumbent, not a given.

## What's already MEASURED (inputs, not to be re-litigated)
- TM column-sweep transition = map (local closure) + commutative/associative reduce-by-key
  (sweep8.h:86–110). Sort+merge expresses it with no random lookup. **Gate-1 S≈1.0** (compute-free).
- **C2 bandwidth (dalby):** seq RAM 15.8, random RAM 0.76, seq NVMe 1.5w/3.1r GB/s. Sequential
  NVMe **out-bandwidths random RAM 2–4×** → spill-sort beats hash-in-RAM on data movement; a(24)
  cliff is I/O-crossable. (03-seam-closure-analysis.md)
- u128 add+widening-mul correct & byte-identical on arm64+x86. Cross-arch checkpoint resumes
  byte-identically (oq2 GREEN). RAM cost-model holds (~580–780 lean / ~1100 batched B/state).
- B-BS 45° rotation NO-GO for king-connectivity (phase01 probe).

## Design dimensions — KNOWN / GAP, hypothesis, falsification test
| # | dimension | status | working hypothesis | how to FALSIFY (smoke test) |
|---|-----------|--------|--------------------|------------------------------|
| **A** | algorithm / decomposition | **GAP (reopened)** | TM column-sweep (λ^min(H,W)) is near-optimal for king; FLM/width-bounded is the only scaling-changer and likely doesn't bend it | cost-model each alternative's growth base; FLM width-bounded state count vs height-bounded at small n; show a survivor beats λ^min(H,W) or confirm none does |
| **B** | state representation & RAM | **GAP** | count-vector (counts[1..n]) is ~85% of state; ranged-row is a real constant-factor win; packing the sig is marginal (Motzkin dead for crossing partitions) | `--profile-rows` the live count-row width; if mean≈maxn, ranged-row buys ~0 |
| **C** | sort/stream engine internals | GAP (Round 2) | external k-way mergesort of (sig,count-vec) runs; pole-scale S swings to sort | spill prototype; bench_column at larger n |
| **D** | counting arithmetic | ~KNOWN | u128 exact to ~a(48); composes with vector-add merge | (confirmed); re-check at bignum boundary only |
| **E** | parallelism model | GAP (Round 2) | parallel external sort (per-shard runs, parallel merge); no shared hash → no contention | scaling test of the sort engine |
| **F** | distribution staging | GAP (Round 2) | sort/stream **relaxes the sticky-height atom** — sorted runs shard/migrate freely (oq2 GREEN) | can a single height be split across boxes via sorted-run partition? |
| **G** | output stratification | ~KNOWN | height-tagged sweep yields T(n,H) directly; a(n)=Σ_H | (per-height sweep already does this) |
| **H** | component seams (evolvability) | GAP (Round 2) | clean seams: counter-type, store/spill backend, decomposition — each swappable | define the interfaces; show u64→u128→bignum & RAM→spill→dist are drop-ins |
| **I** | correctness / validation | ~KNOWN | byte-identical-to-dense gate survives (bench_column oracle already does it for sort); +continuous mod-p shadow | (oracle works); design the distributed-case gate |
| **J** | feasibility ceiling | **GAP** | a storage/compute wall exists well before the u128 counting wall (~a(48)); compute-time likely binds first | extrapolate measured laws; find which resource binds first at each n and where it goes infeasible |

## Investigation rounds
- **Round 1 (now):** A (algorithm — the big reopened one), B (state/RAM minimum), J (feasibility
  ceiling). These are independent and gate the rest (the engine/distribution/seams depend on which
  algorithm + state survive).
- **Round 2:** C, E, F, H — the engine/parallelism/distribution/seam design, given Round-1 survivors.
- **Round 3:** integrate → a complete design + the open risks; iterate any gap not yet closed.

## Round 1 RESULTS (2026-06-26)
**The headline convergence:** J proves the feasibility ceiling is set by **the growth base and
nothing else** (compute binds; storage/IO/counting all slack; cores buy <1 term each). A finds a
candidate that may **bend that base 2.42→2.04** — the diagonal sweep. So the entire next-system
ceiling now **hinges on confirming the diagonal base.** Confirmation dispatched (a correct king
diagonal TM, gated Σ==a(n)).

**A — algorithm: a SURVIVOR that REOPENS the retired 45°.** Distinct-STATE-count (the real TM
cost — not the bbox *width* that phase01 measured and wrongly retired the idea on) for a diagonal
king cut is base **~2.04 vs the column's ~2.42**, measured over king-polyplets n≤12
(`experiments/phase02_statecount_probe.cpp`), validated reproducing the engine's 2.42. If real in a
built engine: ~36× less peak RAM, ~18× less time at a(22), cliff out ~2 terms. **CAVEAT: a
state-count *signal*, not a built engine** — needs a correct king diagonal TM (king-closure
bookkeeping across the diagonal) with Σ==a(n) and the *real* peak-state base. **REOPENED;
confirmation running.** Also killed cleanly: GF factor-sharing (lifetime is exactly 3, structural
not a cost lever), Redelmeier (base 7.1), Motzkin (crossing partitions).
**B — state/RAM: ranged-row ~1.9×, CONFIRMED (and a mirage debunked).** Peak-column count-row
width = 0.56·n (NOT ≪n; the optimistic "~7×" was an all-heights-aggregate artifact dominated by
tall near-empty strips). Realistic floor **~110 B/state raw / ~130 deployed**. Constant-factor
SHIFT (~+1.3 terms), not a bend — sets *where* the cliff is, not *whether*.
**J — feasibility ceiling: COMPUTE binds; ceiling a(25), a(26) the wall. CONFIRMED.** The 4.44×/N
compute exponent dominates; storage crosses 1 TB at a(26)/100 TB at a(31), I/O is ≤3e-4 of compute
always, u128 covers to ~a(48). **The ONLY lever that moves the ceiling is lowering the growth
base** — exactly what A's diagonal candidate claims. The sort/spill engine lets you *fit* a(24/25)
but cannot push the ceiling.

## Updated dimension status
- **A:** RESOLVED 2026-06-26 — **diagonal FALSIFIED, column sweep stands.** A correct king diagonal TM
  (Σ==a(n) through n=11, `experiments/diag_king_tm.cpp`) measures base **~4.52, not 2.04** — *worse*
  than column's 2.42 (≈ its square). The 2.04 was a phantom: the probe omitted the king corner-link
  that jumps TWO diagonals, so a correct TM must carry a 2-diagonal boundary → squared base. **No
  base-reducer found; the ceiling (a(25)/a(26)) stands.** The column decomposition is the next
  system's static core (no decomposition-pluggability earned — like the classifier, the one
  alternative is dead/obsolete).
- **B:** CONFIRMED — target ~110 B/state; ranged-row is the keystone constant-factor (~1.9×).
- **J:** CONFIRMED — ceiling a(25)/a(26) on the column base; growth-base is the sole ceiling lever.
- **C/E/F/H (Round 2):** now CONDITIONAL on A — the engine/parallelism/distribution/seams differ
  for a column vs a diagonal decomposition. Hold Round 2 until A confirms or falls.

_Status: Round 1 closed; diagonal FALSIFIED 2026-06-26 (column stands, no base-reducer found). Round 2 (engine/parallelism/distribution/seams) UNGATED — proceeds on the column decomposition._

## Settled engineering conventions (jasonp, 2026-06-26)
How the next system is built and kept from blurring into mud. Researched: spec-driven
development ([spec-kit](https://github.com/github/spec-kit/blob/main/spec-driven.md)),
evolutionary-architecture fitness functions, AiiDA-style provenance.
- **Executable invariants over discipline.** Every architectural/correctness invariant is a
  build-FAILING gate (a *fitness function*), not a documented agreement. The byte-identical-to-
  dense gate is the template; extend to module-boundary tests and **cross-decomposition agreement**
  (column and diagonal must produce the identical triangle — a validation no dense baseline gives).
- **Code is built incrementally + tested, NOT regenerated from docs.** Design docs drive *intent
  and boundaries*; gates *enforce* them; regeneration is reserved for the derivable shell, never the
  tested core. Generate-only REJECTED — even SDD's best practitioners (Harper Reed) patch-with-tests;
  the teeth are the gates, not the regeneration. The hard-won core (closure math, lock-free merge,
  fold, CRT/u128) lives in specific tested code with git-bisectable trust.
- **Binary provenance — rev in the filename.** Binaries carry the short git rev in their NAME
  (`tma-<rev>`, `-dirty` if the tree isn't clean); they already stamp the rev in `event=start`, keep
  both (filename = at-a-glance + survives-without-logs; embedded = ground truth). `build/tma`
  convenience symlink ok; rev-named files live under `build/<rev>/` or get pruned.
- **Exit accounting (clean exit).** Every binary emits `cpu_s`, `wall_s`, `peak_rss` on normal exit
  (`tma` already does via `event=done` / `getrusage ru_maxrss`). Work = make it uniform across all
  binaries and land it durably, not just stderr.
- **Abnormal exit → accounting folds into the checkpoint.** Checkpoint stores `(cpu_so_far,
  wall_so_far, rss_max_so_far)`; resume seeds from them and keeps accumulating — cpu/wall SUM,
  peak-RSS MAX — so the final `event=done` reports the true total across the crash. Accounting
  granularity then equals work granularity (a crash loses exactly the accounting for the work it
  also lost). Costs a 3-field checkpoint-format bump.
- **Language (working decision, 2026-06-26): C++ core + Go for everything operational** —
  orchestration, scheduler/governor, telemetry, validation/verifier harness, cross-machine. Go
  replaces BOTH Python and bash → two compiled languages, no interpreted glue. Process boundary
  between them (no cgo/FFI), GC confined to the non-hot Go layer. Go `math/big` covers CRT/bignum
  natively. A real CAS (PARI/Sage/FLINT) only as an isolated standalone tool if symbolic GF work is
  ever revived — never Python-as-default. Migration incremental, next-system only (don't touch the
  running a(21) machinery). Rust ruled out: unknown to us, core is small + works, rewrite buys nothing.
- **NOT doing:** whole-hog provenance manifests (AiiDA-style DB). The above is the deliberate 80/20:
  "account for every binary we ran and what it cost" without standing up a provenance system.

## Work-safety & predictability (design model, 2026-06-26 conversation)
Touchstone (jasonp): never lose significant work to a mispredicted size/time. Reframe: you can't
predict an exponential, so make work-safety NOT depend on prediction.
- **Predictions are advisory, never load-bearing.** A wrong prediction revises a *plan*, never causes
  a crash or lost work. (Spill: RAM surprise → spill, don't die. Budget governor: wall/disk surprise
  → checkpoint+stop, don't OOM.)
- **Bounded loss by construction.** Loss ≤ one checkpoint interval, by *wall-clock* cadence — NOT
  structural boundary. (Today's bug: column-boundary-only checkpointing means a ~day-long pole column
  saves nothing mid-flight; H19 lost ~6 h to exactly this on 2026-06-26.) The sort engine's spilled
  sorted runs ARE a continuous mid-column checkpoint, for free.
- **Work unit = map a source-frontier slice → a sorted run.** Splitting a unit = partitioning a sorted
  key-range (trivial; a hash table can't). Runs are simultaneously checkpoint + resume-state +
  unit-output. "Self-checkpointing process" and "server hands out units" are the SAME machinery at 1
  vs many workers → single-box work-stealing pool now, multi-box later, no rewrite, no network in v1.
- **Splitting is for parallelism, NOT survival** (spill+checkpoint give safety without it). Do it
  *dynamically* (steal a hot unit's remaining range) to dodge prediction entirely.
- **Barrier-straggler hole + closure:** the column merge is a hard barrier; a straggler map-unit idles
  the rest, sneaking unpredictability back as utilization. Closed by (a) mid-flight stealable tails on
  the map (wall → total/N regardless of split), (b) output-range partitioned-merge (sample for even
  cut points), (c) optional v2 pipelining of merge(c)→map(c+1). Residual unpredictability is
  advisory-only (scheduling), not load-bearing.

### OPEN investigation idea — per-state map-cost distribution (saved 2026-06-26, run later)
**The one load-bearing assumption** under the entire straggler-closure: *no single source state is a
monster.* Work-stealing subdivides only down to one state, so the grain floor = the most expensive
single state's map cost. Bounded/low-variance → stealing balances everything. **Heavy-tailed → a few
states become irreducible mini-stragglers and the barrier unpredictability creeps back.**
- **Smoke test (cheap, falsifiable):** instrument the current engine to histogram per-source-state
  fan-out (viable-mask / successor count, or map µs) over a real heavy column. Tight → closure holds;
  heavy tail → need a deeper mitigation (split a hot state's *mask enumeration*, not just the source
  range).
- **Why saved not run:** load-bearing for the work-stealing scheduler design but not urgent — parked
  to keep the big-picture conversation moving. Run before committing to that scheduler.
- **RESOLVED 2026-06-26 — GO (no mask-splitting needed), with a small-shard refinement.** Probe
  (`experiments/fanout_probe.cpp`, validated Σ_H=a(n) through a(14)) measured per-source-state fan-out
  at (n=18, H=11). The FALLBACK triggers are NOT met anywhere: top 1% of states carry only **9.6–13.7%**
  of total work (no power-law; top 0.1% ≤1.8%), the largest single state is **≤1.9% of a 1k-shard** (no
  monster), max fan-out is **14% of 2^H** in pruning-active columns. So **work-stealing over
  hash-sharded states suffices; the mask-splitting fallback is unnecessary.** The nuance the prediction
  missed: roughness is **column-dependent** — early columns tame (max/median ~2×, σ/μ 0.56) but late,
  pruning-active columns rough (max/median up to **147×**, per-shard cv still 0.68 even at S=10k) because
  they hold few states (~12k) AND low median fan-out (2). Those rough columns are CHEAP, though (low
  state-count × low fan-out ≈ 1% of total work). **Design consequence: shards must be SMALL (S≈1k) and
  DYNAMIC (atomic-cursor work-stealing, not static striding — static would tail-stall on late columns);
  scale shard size to the column's state count.** This *validates* the work-stealing choice rather than
  merely permitting it — a static partition would have stalled on the late columns.
- **H-LADDER follow-up 2026-06-26 (`experiments/cost_ladder.cpp`, masks-EXAMINED cost, fixed maxn=16):
  GO confirmed at scale, with one correction.** The shard-relevant ratio max/MEAN climbs **18.9 → 24.6
  → 31.5 at H=11/12/13** — a stable **~×1.28/H** (not accelerating). Extrapolated to production: max/mean
  ~227 at H=21, ~470 at H=24. But a production pole column is 1.7×10⁸–4×10⁸ states → shards of 17k–170k
  states → the monster (one indivisible state) is only **0.1–1.3% of a shard.** The FALLBACK triggers
  when max/mean approaches shard-state-count (10⁴–10⁵); we're at 200–500, a **20–500× margin** robust to
  extrapolation error. **No mask-splitting.** CORRECTION to the line above: shards should be **~10k–100k
  states, NOT ~1k** — `monster_fraction ∝ 1/S`, so fine shards *inflate* the monster; you want them big
  enough to dilute it (free at 10⁸-state columns). Still DYNAMIC (cvKey~0.9 static is badly balanced;
  dalby sustains ~38× on the real pole, proving dynamic dispatch absorbs it). The max/MEDIAN blow-up
  (≈400) is the median collapsing — *divisible* spread, work-stealing's job — not the indivisible monster.
- **Certainty / independent sanity checks (2026-06-26).** The GO above leans on an 8-step extrapolation,
  so it's cross-checked two ways that are NOT more rungs:
  1. **Structural hard bound (applied, passes).** Masks-examined per state **≤ 2^H** (only 2^H next-column
     patterns exist) — a ceiling from structure, not a trend. mean cost is *growing* (~×1.25/H → ~600 at
     H=21), so **max/mean ≤ 2^H/mean ≈ 3,400 at H=21** even if the worst state saturates 2^H (it doesn't —
     mx/ceil is ~0.4 and falling). The empirical extrapolation gave ~225; the ceiling says ≤3,400; the true
     value is bracketed between, and BOTH are below the danger threshold (max/mean ≈ shard-state-count ≈
     17k–170k). Two independent methods (empirical trend + first-principles ceiling) converge on GO — that
     convergence is the confidence. **The one failure mode (mean *collapsing* at high H) is structurally
     precluded:** numerator is ceiling-bound, denominator only grows (more boundary cells → more masks/state).
  2. **Real-engine cross-check (available, not yet pulled).** The actual engine sustains ~38× on the real
     pole at H≈18–19 (nearer production than the probe), and the perf campaign pinned that cap to *hardware*
     (Infinity-Fabric), explicitly NOT monster imbalance. A monster problem would show heavy-tailed per-thread
     runtimes + a far-below-38× cap. TODO if more assurance wanted: pull the per-thread imbalance signature
     from the existing perf data (heavy tail = monster; flat-but-capped = confirms-not-monster) — no new compute.

## Worker threading model (decided 2026-06-26): SINGLE-THREADED workers, parallelism cross-process
Each C++ worker maps ONE shard single-threaded (`read shard → map → write run → exit`); ALL parallelism
is the Go orchestrator spawning many workers + stealing tails. No threads/locks/shared-state in the core.
- **Empirical clincher:** dalby scales **100% linear to 76 *independent* sweeps** but a single MT sweep
  caps at **~38×** (the cap is the shared-state contention — lock-free merge, shared nextDB, memory — that
  separate processes don't have). Cross-process is *faster*, not just simpler.
- Keeps the core at its ~600-line target (no hot-path threading), makes the process the fault/checkpoint
  boundary, keeps GC in Go off the hot path. Spawn cost is <0.1% at 10k–100k-state shards (seconds of work),
  and production columns (10⁸ states) give thousands of shards ≫ 76 cores. Same for merge workers
  (single-threaded, each owns an output key-range).

## Migration / build sequence (decided 2026-06-26): bottom-up, gated, OLD ENGINE AS ORACLE
Rule: the current engine runs a(21)/a(22) **uninterrupted**; the new one is built in parallel and the old
engine is its test oracle through a(22). No big-bang cutover. Each phase gated byte-identical before the next:
0. **`libenum` core** — extract the validated transition + signature canon from today's `cpp/tma/`, write the
   NEW part (sort/merge over runs) behind the library API. Gate: link-test reproduces a(n) small-n,
   byte-identical to today. *(Riskiest piece first.)*
1. **Single-process end-to-end** — worker + trivial driver, spill to disk, no orchestrator. Gate: a(18–20)
   byte-identical. *(Proves the sort/spill engine.)*
2. **Go orchestrator** — cross-process workers, work-stealing, budget governor, wall-clock checkpoint/resume.
   Gate: same a(n) parallel AND resumable (kill+resume byte-identical).
3. **a(22) cross-check** — new engine's a(22) must equal the old engine's. *The trust milestone* — new==old on
   the last term the old engine can reach.
4. **a(23) on the new engine** — first term only the new engine fits; no old oracle, so it leans on the
   validation stack (small-n regression + row-sum + mod-p shadow + publish-and-verify). a(23) is the testbed
   *because it still fits a box* — failures cheap and re-runnable.
5. **a(24)+** — add distribution/cloud as components only when the cliff demands (scale-by-replacement).
The de-risking core is #3: don't *trust* the new engine for a(23) on faith — prove it equals the old on a(22)
first. The old engine earns retirement by being out-reproduced, not merely replaced.

## Architecture — component map (B-as-a-library, external merge-sort core)
Settled direction, 2026-06-26 design conversation. **Granularity: shard, not height** — height is
maxed (it's already the current engine's coarse atom, can't be split across boxes). The system is
the **map-reduce SHAPE done as a parallel external merge-sort — NOT a map-reduce framework.**
- *Why no framework:* (1) our map is a ~µs C++ kernel over a packed state, so framework per-record
  bookkeeping dwarfs it (tiny-task overhead); (2) a column sweep is N *iterative* MR jobs (col c→c+1)
  and frameworks are iteration-unaware. Go MapReduce libs are educational; Dataflow/Spark are
  wrong-granularity + cloud cost. Right prior art = **external sorting** (run-gen → spill → k-way
  merge), thin and ownable.

Components & contracts:
- **`libenum` (C++ library, ~400 ln — the single-source-of-truth core):** `map_shard(in_run,cfg)→out_run`,
  `merge(runs,key_ranges)→runs`; classifier (triangle = count by (n,H)) and counter (u64/u128) are
  **templates**; column decomposition is static (diagonal falsified). NO main, NO I/O policy, NO
  scheduling. **Its public API IS the fitness-function seam.**
- **C++ worker-main (~50 ln):** links libenum; reads a run-path + cfg, calls map/merge, writes a run +
  exit-accounting. The process wrapper.
- **Go orchestrator:** scheduler + work-stealing queue · budget governor (graceful stop) · store
  interface (local NVMe v1 → distributed → cloud) · checkpoint cadence/bookkeeping · telemetry
  aggregation · run manifest. Spawns workers; owns ALL liveness/safety. Replaces today's bash drivers.
- **Go verifier (separate tool):** reads published runs/subtotals/mod-p residues, checks consistency,
  spot-checks by re-running sampled shards.

**Cardinal rule (carve in stone): the orchestrator touches RUNS (files), never individual states.**
The C++ worker is the only thing that ever sees a state, and it sees millions per call in a tight
loop. That one boundary keeps framework overhead ~0%, IS the `libenum` API seam, AND is the
fault/checkpoint boundary (worker = dumb fast process that maps a shard and dies; Go owns restart).
Spilled sorted runs are simultaneously output + checkpoint + resume-state + work-unit.

*Off the table:* MapReduce/Dataflow/Spark frameworks (granularity + iteration mismatch). Durable-task
orchestration (Temporal/Cadence) is the right CATEGORY only if managed durability is ever wanted —
later/multi-box, needs server+DB; v1 hand-rolls the thin conductor.

## Validation strategy (pinned 2026-06-26)
"Proof" is a category error: prove the **algorithm** (transfer-matrix bijection — provable, expected
in the writeup); validate the **execution** EMPIRICALLY (a proven algorithm + buggy code = a wrong
"proven" number). Literature standard (Jensen/Guttmann, polyominoes→n=46) = method-proof + layered
empirical confidence, reported as computed-with-checks, not a theorem; OEIS hosts computed-not-proved
terms. Choose layers by **failure mode**:
- gross bug → small-n byte-identical regression + triangle row-sum + growth-ratio smoothness (free).
- arithmetic/transient → multi-prime mod-p + CRT consistency (cheap; modp engine exists). *(run-twice-
  same-code is subsumed by this — skip it.)*
- algorithm-logic → the correctness proof (necessary, insufficient alone).
- impl-logic → a cleanly-independent second implementation, OR the published-dataset-anyone-can-check
  — the ONLY things that catch an impl bug.
**Decided emphasis: publish dataset + manifest + checkpoints + an independent verifier** (modern gold
standard, Pythagorean/Keller-style "check it yourself"), reinforced by the cheap consistency layers.
Caveat: counting has no succinct certificate (verify ≈ recompute), so the published verifier enables
consistency + spot-checks + others' recompute, not a cheap full proof. Honest frontier-term status:
the record term has NO independent computation yet (nobody else can run it either) — it rests on
method-proof + internal consistency + the publishable dataset, the accepted status of any record's
leading edge.

## On-disk format readability (decided 2026-06-26)
Principle: **a format's text budget scales with how often a human/verifier reads it vs how often the
machine streams it.**
- **Human-readable text:** results (triangle T(n,H), b-file), all metadata (checkpoint *headers*,
  provenance manifest, config), verification artifacts (mod-p residues). Small or rarely-streamed →
  text is ~free and buys grep/diff/eyeball/publish, and directly serves the publish-and-verify
  validation strategy (a skeptic needs no special tooling). A readable checkpoint header alone would
  have made this session's H19 rev/staleness debugging a one-line `cat`.
- **Documented simple binary + a `dump`/`--text` render tool:** the hot bulk — spilled sorted runs and
  checkpoint *bodies* (the frontier states). Text there costs ~2–4× the bytes AND throttles the GB/s
  sequential spill (text encode/decode ≫ memcpy; the sort key is a binary memcmp). Keep packed; a
  `runcat`-style tool renders any run on demand (the git-object / `git cat-file` model) → inspectable
  and parseable-by-anyone via `formats.md`, so nothing is ever opaque, but the machine streams it fast.

## Data formats (decided 2026-06-26)
Guiding principle: **compute-bound ⇒ favor simple + correct over byte-squeezing.** Squeeze only behind
the localized `libenum` serialize/deserialize, and only if a profile ever says bandwidth-bound (the
ceiling analysis says it never will).

**Sorted run (hot bulk) — fixed-width KEY + variable-width VALUE per record:**
```
[ sig: H+2 bytes (canonical RGS + 2 touch flags) | lo:u8 | len:u8 | counts[len]: len*W bytes LE ]
   |---- KEY: memcmp-sortable, fixed per height-sweep ----|   |---- VALUE: ranged count-vec (W=8 u64 / 16 u128) ----|
```
- Key = the canonical signature; it IS the state (no separate key), doubles as the sort key; memcmp
  gives order + equality; byte-array so endian-neutral. Merge of equal keys = union [lo,hi] + add.
- Value = ranged (contiguous nonzero window ~0.56*n wide). At H=21: ~23+2+12*8 ~= 121 B/record, matching
  the independently-derived ~110 B/state floor.
- **Sig encoding: byte-per-cell (H+2) for v1; order-preserving bit-pack LATER** (fixed 4-bit fields,
  MSB-first, still memcmp-sortable, no unpack to compare/merge) ~= H/2 B. The ~1.3-bit/cell info floor
  (~H/6) needs rank-encoding (deeper squeeze, not planned). Packing is ~compute-free (merge never
  unpacks; only a map worker unpacks source labels, a shift+mask dwarfed by the transition), so it's a
  contained later swap deferred purely to keep v1 core code minimal. *(No sub-H cute encoding: king
  boundary partitions CROSS, so Motzkin/balanced-parens is a square-4 win, not ours.)*

**Run file: PPM-style text header + binary body** (one artifact, head-able): `POLYRUN 1` then
`height/budget/counter/classifier/records/rev/byteorder` lines, blank line, binary records sorted
ascending by sig, trailing 8-byte body CRC. Counter width self-described (u64 to a(25), u128 to a(48);
never bignum, unreachable).

**Checkpoint = text** (the bulk IS the runs already on disk): `POLYCKPT` header naming done runs, the
in-flight worker shards + cursors, and the `acct` line (cpu_s SUM, wall_s SUM, rss_max MAX = the
resume fold-in). A readable header alone would have made this session's H19 staleness debug a `cat`.

**Text artifacts:** triangle (`# n H T(n,H)`, a(n)=sum_H), provenance manifest, mod-p residues
(`n prime residue`) — greppable/diffable/publishable, feeding publish-and-verify validation.
