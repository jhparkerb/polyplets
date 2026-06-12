# Implementation Plan: Decomposed Architecture

*Drafted June 11, 2026. Executes `plan-option2-polyplets.md` first and
`plan-option3-polyhexes.md` second on the same components. **Ordering
confirmed as a deliberate decision June 11, 2026**: polyplets are the primary
campaign — generation quick-wins AND the polyplet TMA (accepting that its
non-planar-lattice state-growth question sits on the critical path, gated at
M3/S1) — with polyhexes as campaign 2 on the proven engine. Square-4
polyominoes remain a validation instrument only, never a record target. Governing
principle, per project strategy: decompose into separable parts that can be
implemented, tested, and **replaced entirely** without sinking the project.
Every component states its contract, its test, its fallback, and what is
OEIS-submittable without anything downstream of it existing.*

## 0. The three rules

1. **Chain of oracles.** Nothing validates against only itself. Each engine is
   tested for *per-bounding-box equality* (not just totals) against the
   engine below it on an overlap range, and the bottom of the chain is
   externally pinned (OEIS b-files, published paper tables):
   `golden data → naive enumerator → Redelmeier → TMA`.
2. **Optimizations must be invariance-tested no-ops.** Pruning, parallelism,
   compression, mod-p — each is a switch; with the switch flipped either way,
   every count must be bit-identical (mod-p: CRT-consistent). A wrong
   optimization is then detectable by bisection over switches and removable
   without touching correctness code.
3. **A result is submittable only off the ledger.** Every claimed term must
   trace to two runs with independent primes (or bignum + one prime), logged
   with code version, parameters, and machine. No exceptions, including
   "obviously right" small terms.

## 1. Component map

```
Layer 0  foundations      F1 golden-data   F2 lattice   F3 arith
Layer 1  generation       G1 naive   G2 redelmeier   G3 harness/ledger
Layer 2  TMA              T1 signature   T2 transition   T3 statedb
                          T4 sweep   T5 pruning   T6 parallel
Layer 3  science          S1 calibration   S2 symmetry/Burnside
                          S3 series-analysis   S4 oeis-packaging
```

Dependency arrows run strictly downward (S2 needs only Layer 0–1; the TMA
never depends on S2). Submittable milestones exist at the bottom of every
layer — see §4.

## 2. Component contracts

### Layer 0 — foundations

**F1 `golden-data`** — Machine-readable fixtures: pinned copies of the
b-files fetched this session (A006770, A030222, A001168, A001207, A000105,
…), plus tables transcribed from the local PDFs (Jensen's signature counts,
B–BS Table 2, V–G n ≤ 35, Redelmeier's symmetry tables). Data only, no code.
*Test:* checksummed; CI fails if fixtures drift. *Fallback:* none needed.
*Replaceable:* trivially (it's data).

**F2 `lattice`** — Pure geometry behind one small interface: cell coordinate
type, `neighbors(cell) -> [cell]` per connectivity rule (square-4, square-8,
tri-6), bounding-box arithmetic, the D4 symmetry action on cells and boxes.
No enumeration logic. *Test:* property tests (neighbor relation symmetric;
transforms are bijections composing per the group table; neighbor counts
correct). *Replaceable:* per-lattice implementations are independent plug-ins;
adding tri-6 later touches nothing else.

**F3 `arith`** — Count arithmetic: u64-mod-p residues (2–3 fixed 62-bit
primes), CRT recombination, and a bignum path (GMP) behind the same trait.
*Test:* algebraic identities vs GMP on random inputs; CRT round-trips.
*Replaceable:* swap primes, add primes, or run pure bignum — callers can't
tell.

### Layer 1 — generation (first OEIS results live here)

**G1 `naive`** — Slow, obviously-correct enumerator: BFS growth with
canonical-form dedup, any F2 lattice, n ≤ ~13. The oracle's oracle: code
simple enough to review line-by-line in one sitting. *Test:* matches F1 small
terms for polyominoes, polyplets, AND polyhexes (three lattices through one
code path is itself a strong cross-check). *Replaceable:* it's ~200 lines; if
in doubt, rewrite it independently and compare (cheap second implementation).

**G2 `redelmeier`** — Redelmeier's algorithm parameterized by F2:
counts fixed animals by size, with optional per-bounding-box histograms and
optional symmetry-class restriction (for S2). Modernizations (neighborhood
counter, iterative loop, bitboards) are internal and invisible to the
contract. *Test:* equals G1 everywhere G1 reaches, per-box; equals F1 to
n = 18 (polyplets) / n = 24 (polyominoes, Redelmeier's own paper range).
*Fallback:* G1 parallelized (slower ceiling, same results).
*Deliverable without anything else:* A006770 a(19), a(20) — **OEIS
submission #1.** Per-box histograms also become T2's test fixtures.

**G3 `harness/ledger`** — Job runner + provenance: work units (subtree
partitions for G2, signature-set chunks for TMA), checkpoint/resume, the
dual-prime run policy, and an append-only ledger (run id, component versions,
params, machine, result hashes). *Test:* kill/resume tests reproduce
uninterrupted results; ledger entries reconstruct every published number.
*Replaceable:* it's orchestration; any job system could substitute. Exists so
that rule 3 is mechanical rather than aspirational.

### Layer 2 — TMA (the centerpiece, itself decomposed along the risk lines)

The four risky concerns — *what a state is* (T1), *how states evolve* (T2),
*how states are stored* (T3), *what order work happens in* (T4) — are
separate components precisely so that the novel one for polyplets (T1/T2
under king adjacency) can be debugged, or torn out and redesigned, without
touching the others.

**T1 `signature`** — Boundary state value type: occupancy + partition of
occupied boundary cells into connectivity classes + touch-top/bottom flags.
Operations: canonicalize, hash, add/remove cell, k-way class merge, "class
vanished" query. Two implementations: (a) **generic partition codes** —
handles crossing partitions, required for square-8; (b) **non-crossing/
Motzkin compact codes** — optimization valid for square-4 and tri-6 only.
*Test:* property tests (canonicalization idempotent; operations commute where
they should); and (a) vs (b) bit-equivalence driven over millions of random
op sequences on square-4, where both apply. *Replaceable:* (a) is always a
valid fallback everywhere (b) is used; engine never knows which is loaded.

**T2 `transition`** — The lattice-specific kink-update rule: given signature
and the occupy/empty decision for the next cell, produce successor
signature(s) — including the polyplet-specific k-way merges and the
diagonal-contact cases. **The most bug-prone component in the project**, so
its test is the heaviest: exhaustive per-box equality against G2 histograms
for every box that fits n ≤ 16 (square-4 first, then square-8), plus —
square-4 only — reproduction of Jensen's/B–BS published signature-count
tables from F1, which validates state bookkeeping, not just final counts.
Three plug-ins, built in this order:
1. `square-4` — not needed for any new term; built first because it has the
   richest external validation (A001168 to n = 70) and separates "engine
   bugs" from "novel-rule bugs" before any novelty is attempted;
2. `square-8` — the polyplet rules (the research wrinkle lives here and ONLY
   here);
3. `tri-6` — the polyhex campaign later; nothing else changes.
*Fallback:* if square-8 rules resist correctness, the engine still ships
polyhexes via tri-6; the polyplet record still advances via G2. No quagmire
path exists.

**T3 `statedb`** — Map signature → counts-by-size. Interface: get/update,
iterate, partition by occupancy pattern, freeze/thaw chunk. Implementations
in escalating order, all behind the same trait: (1) plain hash map (correct,
small n); (2) chunked sets + compression of inactive chunks; (3) out-of-core
spill. *Test:* differential — every implementation must produce identical
sweep results; plus storage-level round-trip tests. *Replaceable:* this is
THE designed-to-be-replaced component; performance work happens here without
correctness review.

**T4 `sweep`** — Box iteration (heights, aspect-ratio counting rules,
double-vs-once bookkeeping), kink order, assembly of a(n) from per-box
results. *Test:* assembled totals equal G2/F1 on the full overlap range;
internal identity checks (transpose symmetry of box counts where applicable).
*Replaceable:* order-of-work choices (column-major, diagonal sweep for the
45° experiments) are T4 variants behind one interface — which is exactly how
the sweep-direction studies (both plans' M4) get implemented as experiments
rather than rewrites.

**T5 `pruning`** — Budget filters (connection cost n_c, span, aspect), each
individually toggleable. Hard requirement from rule 2: OFF must be the
default-correct path; ON must change no count, only cost — verified by
golden diff runs at every n the unpruned engine can reach. *Fallback:* run
unpruned at lower n; partial results remain records.

**T6 `parallel`** — k-way signature-set partitioning over threads/processes
+ G3 work units. Rule 2 applies: any k, any schedule → identical results.
*Fallback:* serial runs at lower n.

### Layer 3 — science and publication

**S1 `calibration`** — Telemetry + analysis: reachable-signature counts per
width, fitted growth base k, memory/time forecasts → the M3 go/no-go report
that picks production targets. Pure post-processing of engine telemetry.

**S2 `symmetry/Burnside`** — Free and one-sided counts: symmetry-restricted
G2 runs per Mason placement class + Burnside assembly (formulas from the
option-1 research). Depends only on Layers 0–1 — proceeds in parallel with,
or entirely without, the TMA. *Test:* assembled Free(n) equals A030222 for
n ≤ 17; Redelmeier's own 1981 symmetry tables (now in F1) check the small
range. *Deliverable:* A030222 extension + new one-sided and symmetry-class
sequences — an OEIS submission independent of all of Layer 2.

**S3 `series-analysis`** — Ratio/differential-approximant estimates of λ from
whatever terms exist. Optional garnish; zero coupling.

**S4 `oeis-packaging`** — b-file emitter + draft edit text + ledger
cross-references for each submission. Mechanical; exists so submissions are a
script, not a chore.

## 3. Build order and test gates

```
Week 0+:  F1 F2 F3 → G1            gate: G1 matches F1 on 3 lattices
Then:     G2 (+G3)                 gate: per-box equality w/ G1; F1 to n=18/24
          ── OEIS submission #1 possible here (G2 production runs) ──
Then:     T1(a) T3(1) T4 + T2/square-4   gate: A001168 small terms per-box;
                                          Jensen/B–BS signature counts match
Then:     T2/square-8              gate: per-box equality w/ G2 to n=16;
                                          then S1 calibration report
Then:     T5 T6 T3(2)              gate: invariance diffs clean at all
                                          reachable n
          ── staged TMA production: each run a submittable record ──
Parallel: S2 after G2              gate: Free(n) matches A030222 n≤17
Later:    T2/tri-6 + T1(b)         gate: V–G n≤35 from voge_guttmann_2003.pdf
          ── polyhex campaign on the same engine ──
```

No step depends on an unproven sibling; every gate is an equality against
something already trusted.

## 4. What is submittable if work stops at each point

| Project dies after… | Banked, submittable results |
|---|---|
| G2 | fixed polyplets a(19)–a(20) (+a(21)–a(22) with cloud burst) |
| S2 | + free/one-sided polyplets to same n, + new symmetry-class sequences |
| T2/square-4 | nothing new (by design — it's validation), but engine proven |
| T2/square-8 + T4 | + fixed polyplets into the high 20s even unpruned/serial |
| T5/T6 | + fixed polyplets to the M3-calibrated ceiling (target band 28–38) |
| tri-6 | + fixed polyhexes past 46 |

The strategy property this buys: **at no point is there a large body of
unvalidated code whose value depends on future work.** The maximum work at
risk at any moment is one component, and every component has a named
fallback.

## 5. Practical defaults (changeable without ceremony)

- **Languages (decided June 11, 2026, from fluency: Perl/Shell/Python/C++/Go
  professionally; no Rust):**
  - **C++20 — engines** (G2, all of Layer 2). Owner-fluent, native GMP,
    full memory-layout control for T3. The silent-corruption risk Rust would
    have removed is bought back with mandatory discipline: ASan+UBSan on all
    test builds in CI, warnings-as-errors, rapidcheck property tests on T1
    ops, occasional valgrind on production binaries — layered under the
    protocol-level defenses (dual-prime runs, per-box equality, invariance
    toggles), which are the primary safety net regardless of language.
  - **Python — G1 oracle, S1/S3 analysis, S4 packaging.** Deliberately a
    different language from the engines so oracle bugs are uncorrelated with
    engine bugs (different compiler, arithmetic, author habits).
  - **Go (optional) — G3 harness/ledger.** Orchestration, checkpointing, run
    ledger; Go's sweet spot, no hot loops, keeps process-management code out
    of C++.
  - Build: CMake + a Makefile front door; tests via GoogleTest/Catch2 +
    rapidcheck.
- **Division of labor (June 11, 2026):** Claude writes most of the C++
  (engines); the owner's review leverage is deliberately placed in the
  Python oracle, the fixtures, and the gates — the trust model runs through
  the verification gauntlet (different-language oracle, external golden data,
  dual primes, dual compilers, invariance toggles), not through reading
  engine internals. Consequences:
  - **Boring-dialect rule:** engine C++ stays in a plain subset — structs,
    `std::vector`, free functions, no template metaprogramming, no clever
    ownership games — so the owner can follow any file if needed.
  - **Component seams are the review unit:** each Layer-2 component small
    enough to be replaced wholesale (per rule from the decomposition
    strategy) is also small enough to be skimmed in one sitting.
  - G1 oracle and S-layer stay owner-maintainable Python; G3 harness in Go
    if the owner wants an engine-adjacent piece in a strong language.
- **Repo layout:** one crate/workspace per component group (`lattice`,
  `arith`, `enumerate`, `tma`, `science`), `fixtures/` for F1, `ledger/`
  append-only JSONL, `papers/` for the eight PDFs.
- **CI:** every gate in §3 is a test tag; fast tags on every commit, per-box
  exhaustive tags nightly.
- **First coding session:** F1 (b-files into `fixtures/` with checksums) +
  G1 oracle, ending at the first green gate: G1 reproduces A001168(1..10),
  A006770(1..8), A001207(1..8) from pinned fixtures (~3 s quick tier; deeper
  oracle validation is G2's job). **Done June 11, 2026 — GREEN.**

## 6. Component diagram

```
                              EXTERNAL TRUTH
            OEIS b-files (A006770, A030222, A001168, A001207, …)
    paper tables: Jensen sig-counts · B–BS Table 2 · V–G n≤35 · Redelmeier
══════════════════════════════════╪═════════════════════════════════════
                                  │ pinned, checksummed
┌─ LAYER 0 · FOUNDATIONS ─────────▼─────────────────────────────────────┐
│                                                                       │
│  ┌──────────────┐    ┌───────────────────────┐    ┌────────────────┐  │
│  │ F1           │    │ F2 lattice            │    │ F3 arith       │  │
│  │ golden-data  │    │ ┌────┐ ┌────┐ ┌─────┐ │    │ mod-p/CRT ⇄ GMP│  │
│  │ (fixtures)   │    │ │sq-4│ │sq-8│ │tri-6│ │    │ (interchange-  │  │
│  └──────────────┘    │ └────┘ └────┘ └─────┘ │    │  able)         │  │
│                      └───────────────────────┘    └────────────────┘  │
└────────┬──────────────────────┬────────────────────────┬──────────────┘
         │ golden tests         │ geometry                │ counts
┌─ LAYER 1 · GENERATION ────────▼────────────────────────▼──────────────┐
│                                                                       │
│  ┌───────────────┐  per-box    ┌─────────────────────────────────┐    │
│  │ G1 naive      │◄┈┈┈┈┈┈┈┈┈┈┈┈│ G2 redelmeier                   │    │
│  │ (oracle's     │  equality   │  + per-box histograms           │    │
│  │  oracle,      │             │  + symmetry-restricted mode     │    │
│  │  ~200 lines)  │             │  ⊞ SUBMIT #1: a(19)–a(20)       │    │
│  └───────────────┘             └────────┬───────────────┬────────┘    │
│                                         │               │             │
│  ┌──────────────────────────────────────▼─────┐         │ per-box     │
│  │ G3 harness/ledger                          │         │ histograms  │
│  │ checkpoints · dual-prime · provenance      │         │ become T2's │
│  └────────────────────────────────────────────┘         │ fixtures    │
└─────────────────────────────────────────────────────────┼─────────────┘
                                                          ┊
┌─ LAYER 2 · TMA (one engine, four seams) ────────────────┊─────────────┐
│                                                         ┊             │
│   T4 sweep — boxes · aspect rules · a(n) assembly       ┊             │
│      │       (sweep-direction variants = pluggable      ┊             │
│      │        experiments, not rewrites)                ┊             │
│      ▼ drives                                           ┊             │
│   T2 transition ◄┈┈ tested by per-box equality ┈┈┈┈┈┈┈┈┈┘             │
│   ┌──────────────┬────────────────┬──────────────┐                    │
│   │ square-4     │ square-8       │ tri-6        │  plug-ins,         │
│   │ validation   │ POLYPLETS      │ POLYHEXES    │  built in          │
│   │ only — rich  │ novel: k-way   │ campaign 2   │  this order        │
│   │ ext. truth   │ merges, non-   │              │                    │
│   │ (A001168→70) │ crossing ✗     │              │                    │
│   └──────────────┴────────────────┴──────────────┘                    │
│      │ reads/writes boundary states                                   │
│      ▼                                                                │
│   T1 signature ◄───────────────► T3 statedb                           │
│   (a) generic partitions         (1) hashmap                          │
│   (b) Motzkin compact             → (2) chunked + compressed          │
│   (a)⇄(b) bit-equal on sq-4       → (3) out-of-core    [swap stack]   │
│                                                                       │
│   count-invariant toggles (rule 2):                                   │
│   [ T5 pruning: n_c · span · aspect ]   [ T6 parallel: k-way sets ]   │
│                                                                       │
│   ⊞ SUBMIT #3+: staged records — polyplets ~28–38, later polyhexes 47+│
└───────────────────────────────────────────────────────────────────────┘
         │ telemetry                       (Layer 1 only ▲)
┌─ LAYER 3 · SCIENCE ──────────────────────────────────────┼────────────┐
│                                                          │            │
│  S1 calibration: k-fit, memory forecast, go/no-go        │            │
│  S2 symmetry/Burnside ───────────────────────────────────┘            │
│     needs ONLY Layer 1  ⊞ SUBMIT #2: free/one-sided + new sequences   │
│  S3 series-analysis (λ estimates)    S4 oeis-packaging (b-files)      │
└───────────────────────────────────────────────────────────────────────┘

  ──►  uses / depends on          ┈┈►  validated against (test-time only)
  ⊞    OEIS submission point      [ ]  toggleable; must not change counts

  Chain of oracles:  F1 ▷ G1 ▷ G2 ▷ TMA — each link is per-bounding-box
  equality with its predecessor; external truth pins the bottom.
```
