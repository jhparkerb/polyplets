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
- **A:** SURVIVOR (diagonal, base ~2.04) — pending engine-level confirmation. Incumbent column sweep
  is the fallback. *This is the pivotal open question.*
- **B:** CONFIRMED — target ~110 B/state; ranged-row is the keystone constant-factor (~1.9×).
- **J:** CONFIRMED — ceiling a(25)/a(26) on the column base; growth-base is the sole ceiling lever.
- **C/E/F/H (Round 2):** now CONDITIONAL on A — the engine/parallelism/distribution/seams differ
  for a column vs a diagonal decomposition. Hold Round 2 until A confirms or falls.

_Status: Round 1 closed; diagonal-confirmation running 2026-06-26. Round 2 gated on it._

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
- **NOT doing:** whole-hog provenance manifests (AiiDA-style DB). The above is the deliberate 80/20:
  "account for every binary we ran and what it cost" without standing up a provenance system.
