# Plan — independent transfer-matrix confirmation of a(19)

## 0. Goal and success criterion

Compute **a(19) of A006770** (fixed king-move animals of 19 cells) with the
**column transfer-matrix engine** — a counting algorithm fundamentally different
from the Redelmeier *generation* used in both the gympie and ayr campaigns — and
check whether it equals

    a(19) = 151,609,203,011,580

- **If it matches:** a(19) is promoted from *candidate* to **confirmed** in
  RESULTS.md. This is the strongest possible check: the two methods share no
  algorithmic core, so a common bug would have to corrupt both identically.
- **If it disagrees:** we have caught a real error in *something* and stop; the
  three results (a19, Free18, OneSided18) all trace back to the generation
  engine, so a disagreement is a five-alarm fire worth finding before any
  submission.

This plan reuses the existing component decomposition (signature / transition /
state-store / sweep driver / CLI / gate) so each piece stays separately
testable and replaceable.

---

## 1. Why a height cap does NOT save us here (the corrected math)

For **ordinary polyominoes** the minimum number of cells spanning a w×h
bounding box is `w + h − 1` (a staircase), so `n ≥ w + h − 1`. Combined with the
transpose symmetry `f(w,h) = f(h,w)`, you only enumerate the shorter dimension
and it is bounded by `⌈n/2⌉`. That is the classic Jensen aspect trick.

For **polyplets (king / 8-connected)** that minimum collapses to `max(w,h)`,
because a diagonal of `k` cells already spans a `k×k` box. The only universal
bounds are:

    n ≥ w     (every column 0..w-1 must hold a cell — king-connectivity crosses
               one column per step)
    n ≥ h     (likewise every row)

and the diagonal saturates both at once: `w = h = n`.

Transpose symmetry still holds, so the count bookkeeping can be halved:

    A(n) = 2·D(n) + S(n)
      D(n) = #animals with width > height   (strictly wider than tall)
      S(n) = #animals with width = height   (square bounding box)

**but** it does not bound the swept (height) dimension, because shapes that are
large in *both* dimensions with few cells (the near-diagonals) exist for every
height up to `n`. We must sweep strip heights `H = 1 .. n`.

What makes `n = 19` reachable is therefore **not** a height cap but:

1. **Size-budget pruning** — a partial boundary is discarded the moment it
   cannot be completed into an animal of ≤ 19 cells. The tall strips
   (`H` near 19) admit only near-diagonal shapes, so pruning empties them fast;
   the real peak state-count lands at an intermediate height. *This is the
   load-bearing optimization and its payoff must be measured (Phase 0).*
2. **Viable-mask enumeration** — never iterate all `2^H` column masks; generate
   only masks that connect to the live boundary and stay within budget.
3. **Compact / out-of-core state storage** if Phase 0 says we need it.

The aspect-symmetry halving (#1 above, `A = 2D + S`) is a nice constant factor
but is *secondary* here and can be added last (or skipped) — it is the opposite
of its role for polyominoes.

---

## 2. Components (contract → what changes)

| ID | File | Contract | Change for this work |
|----|------|----------|----------------------|
| C1 | `cpp/tma/signature.h` | partition signature (H labels + 2 touch flags), `canonicalize` | add an integer *min-cells-to-complete* lower bound, or compute it in C2; possibly widen for H up to 19 (already fine: bytes) |
| C2 | `cpp/tma/transition_square8.h` | `stepColumnSquare8(old,H,mask)` → Alive/Dead/Complete | (a) add **viable-mask generator** `forEachViableMask(old,H,budget,fn)`; (b) compute a **completion lower bound** for pruning |
| C3 | `cpp/tma/statedb.h` | map signature → counts-by-size; `addCounts` | add a **prune predicate** at insert (drop states whose min completion cost exceeds maxn); keep the swap-for-compact-store seam |
| C4 | `cpp/tma/sweep8.h` | drive columns per strip height, accumulate `byHeight[H][n]` | replace brute `2^H` loop with C2's viable-mask generator; apply C3 pruning; (optional, last) track width for the `A = 2D + S` halving |
| C5 | `cpp/tma_main.cpp` | CLI `tma square8 MAXN [--per-height]` | lift the hard `MAXN ≤ 18` cap; keep `peak_states/peak_height` instrumentation; add `--checkpoint`/resume if Phase 0 says the run is long |
| C6 | `tests/gate_tma.py` | validates engine vs fixtures + G2 | extend square-8 totals check to **n ≤ 18** (full A006770), keep per-height cross-check vs G2, keep ASan equality |
| C7 | run wrapper | — | a tiny script (or ledger entry) that runs `tma square8 19`, records host/commit/peak, and compares to 151,609,203,011,580 |

Anything not in this table stays byte-for-byte unchanged.

---

## 3. Phases (each ends at a gate that must pass before the next)

### Phase 0 — Correct the record, instrument, and re-measure the true scale
*No optimization code yet — decide whether and where this runs before building.*

1. Fix `results/tma_state_growth.md` and RESULTS.md R1: replace the false
   ⌈n/2⌉ claim with §1 above; restate feasibility as "size-pruning + measured,
   ~GB on a big-memory host."
2. Add **min-cells-to-complete** instrumentation to the *existing* v0 engine
   (no behavior change to counts): for each live state print how many would
   survive a prune at budget = maxn. Also surface `peak_height` per maxn (we
   already print it but never tabulated it).
3. Run the instrumented v0 at `maxn = 12,13,14,15` (still brute, still slow but
   tractable) and record: peak viable states *with* the prune predicate, and
   the height at which the peak occurs.
4. Extrapolate honestly to 19. Decide target host + memory ceiling
   (gympie RAM? ayr's NUMA 32-core? — pick based on the measured bytes/state ×
   projected peak). Write the decision into the plan.

**Gate 0:** corrected docs committed; a table of measured pruned-peak vs height
for n=12..15; a defensible projection and a chosen target machine. If the
projection says ">RAM of every available host," stop and design the out-of-core
store (C3 swap) before Phase 1.

### Phase 1 — Viable-mask enumeration (kill the 2^H runtime blowup)
1. Implement `forEachViableMask(old, H, budget, fn)` in C2: enumerate only
   column masks that (a) leave no old component stranded and (b) have
   `popcount ≤ budget`. Generate by a row-walk / bitmask recursion, not a full
   `0..2^H` loop.
2. Rewire C4 to call it instead of the `for (mask = 0; mask < 1<<H; …)` loop.
3. The `mask == 0` (harvest/close) case stays explicit.

**Gate 1:** optimized engine reproduces the v0 engine's `byHeight[H][n]` table
**exactly** for all `n ≤ 12` (square8) — same counts, just faster. ASan-clean.
Record the speedup.

### Phase 2 — Size-budget pruning (kill the memory blowup)
1. Implement the completion lower bound in C2: from a signature with `c`
   components and current touch flags, the minimum extra cells to (a) merge the
   `c` components and (b) reach top+bottom touch. Conservative but admissible
   (never over-estimates) so it can never drop a reachable animal.
2. Apply it in C3/C4: a state is inserted only if `minCellsSoFar +
   completionLowerBound ≤ maxn`.

**Gate 2:** still reproduces v0 `byHeight` exactly for `n ≤ 12` (pruning must be
*lossless* for completable animals). Re-measure pruned peak vs Phase-0
projection — confirm the projection held.

### Phase 3 — Validate the optimized engine to the edge of known truth
1. Extend `tests/gate_tma.py` square-8 totals to **n ≤ 18** against
   `fixtures/b006770.txt` (the whole published sequence). This is the decisive
   pre-flight: the optimized engine must reproduce **every known term** by the
   transfer-matrix method before we trust term 19.
2. Keep the per-height cross-check vs G2 marginals and the ASan-equality check.
3. Build a second binary with a different compiler (GCC on ayr) and confirm it
   agrees to n ≤ 18 too (engine-level decorrelation, cheap).

**Gate 3:** transfer-matrix engine == A006770 for all 18 published terms, two
compilers, sanitizer-clean. Only now is the n=19 run meaningful.

### Phase 4 — Run n = 19 and compare
1. Run `tma square8 19` on the Phase-0 target host. Capture wall time, peak
   states, peak height, host, git commit; append a ledger entry.
2. Compare the result to **151,609,203,011,580**.
3. If equal: update RESULTS.md R1 to **confirmed**, citing the transfer-matrix
   run as the algorithm-independent check, and note the dual campaigns become a
   third line of evidence rather than the primary one.
4. If not equal: freeze, do not touch RESULTS, open an investigation —
   bisect by re-checking n=17,18 on the same binary, then diff the per-height
   marginals against G2 to localize the discrepancy.

**Gate 4:** match recorded in the ledger and RESULTS, *or* a documented
discrepancy with a localization plan.

---

## 4. Risks and how the plan absorbs them

- **Memory larger than projected.** Phase 0 measures before we build; C3 keeps
  the store behind a narrow interface so a chunked/compressed or on-disk store
  is a drop-in (the same seam noted in `statedb.h`). The out-of-core path is a
  fallback, only built if Gate 0 demands it.
- **A subtle pruning bug that drops real animals.** Caught structurally: Gate 2
  and Gate 3 require *exact* reproduction of v0 and of all 18 published terms.
  A lossy prune cannot pass them.
- **The transfer matrix has a bug invisible ≤18 but wrong at 19** (the same
  failure mode we worried about for generation). Mitigation is inherent: this
  engine and the generation engine are independent, so for a19 to be wrong *and
  agree*, both independent methods must share an error — vanishingly unlikely.
  We also keep the mod-8 Burnside congruence as an orthogonal sanity check.
- **Run is long.** If Phase 0 says many hours, add checkpoint/resume to C5
  before Phase 4 (per strip-height H is a natural checkpoint boundary — each H
  is an independent sub-sum into `byHeight`).

---

## 5. What I am NOT doing (scope fence)

- Not chasing a(20)+ — this engine's job is to *confirm* one number, not to set
  records; performance work stops once n=19 is reachable on an available host.
- Not touching the generation engine, the campaigns, or the symmetric counters.
- Not implementing the aspect (`A = 2D + S`) halving unless Phase 0/2 show we
  need the 2× to fit memory/time — for polyplets it is a minor constant, not the
  enabler it is for polyominoes.
