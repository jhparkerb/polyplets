# Method: computing a(19) of A006770 (fixed polyplets)

This documents exactly how a(19) is produced and why it is correct, at the level
of detail needed to vouch for an OEIS submission. a(19) is established by **two
independent algorithms** that agree; this note covers both but focuses on the
column transfer-matrix engine (`cpp/tma/`), which is the algorithm-independent
check.

```
a(19) = 151,609,203,011,580
```

A006770 = number of **fixed** (translation-distinct, not counted up to
rotation/reflection) **polyplets** = king-move (8-connected: edge OR corner)
lattice animals of n cells.

---

## 1. The two independent methods

**Method A — direct generation (Redelmeier).** `cpp/g2_redelmeier.cpp` grows
every fixed polyplet once by the standard min-cell-anchored backtracking
(untried/tried frontier discipline) and tallies by size. Run as two decorrelated
campaigns — gympie (ARM / Apple clang, split 7×64) and ayr (x86 / GCC, split
8×96) — whose `results.txt` are **byte-identical** (SHA256 `558f0bdf…` on both),
verified by `harness verify` and logged in `ledger/ledger.jsonl`. This already
pins a(19); it is decorrelated by ISA, compiler, decomposition, and hardware,
and reproduces all 18 published terms.

**Method B — column transfer matrix.** `cpp/tma/` recounts the same sequence by
a completely different algorithm (dynamic programming over boundary states, no
animal ever generated explicitly). Agreement between A and B is the strongest
check available: a wrong a(19) would require the *same* error in two algorithms
that share no logic. The rest of this document is Method B.

---

## 2. The transfer-matrix algorithm (the math)

**Decompose by bounding-box height.** Every fixed polyplet has a bounding box of
some height H (1 ≤ H ≤ n). Counting those of height *exactly* H separately,

```
a(n) = Σ_{H=1}^{n}  (number of fixed polyplets of n cells, bounding box height exactly H)
```

`cpp/tma/sweep8.h` computes one H at a time (`sweepSquare8Height`) and the driver
sums them (`accumulateTotals`). Heights are independent sub-problems — this is
why they can be checkpointed, resumed, and run as separate jobs.

**Sweep an H-row strip left to right, one column at a time.** Fix the animal in a
horizontal strip of H rows. Process columns 0,1,2,… A *boundary signature*
records everything about the columns placed so far that can affect the future:

- the occupancy of the **most recent column** (which of rows 0..H−1 are filled), and
- a partition of those filled cells into the **connected components** of the
  partial animal they belong to, and
- two flags: has any cell ever been in **row 0** (top) and in **row H−1** (bottom).

Earlier columns are forgotten — they cannot influence future cells, because a
future cell attaches only to the current column (one step left) or to other
future cells. That Markov property is what makes the state space finite and the
DP exact.

**Why a whole column at a time (the novel part for king moves).** For ordinary
(rook/edge-connected) polyominoes you can sweep cell by cell. King adjacency
includes the four diagonals, so deciding cell (col, r) needs the diagonal
neighbour (col−1, r−1) — which a cell-at-a-time sweep has already overwritten.
Transferring an **entire column** at once keeps the whole previous column
present, so all king adjacencies (old rows r−1, r, r+1 to new row r) are
available with no carry. Connectivity is then resolved by union-find.

**Counting each fixed animal exactly once.** Three invariants together give a
clean bijection between fixed polyplets and accepted sweeps:

1. *Left edge at column 0.* The sweep starts from the empty "seed" boundary; the
   first column placed (col 0) is forced nonempty, so the animal's leftmost
   cells sit in column 0. (No animal is counted at several horizontal offsets.)
2. *Height exactly H.* An animal is only tallied when the boundary has touched
   **both** row 0 and row H−1 (the two flags) — so it spans the strip exactly,
   and the `a(n) = Σ_H` decomposition has no double counting across heights.
3. *Connected.* An animal is tallied only when its boundary is a **single**
   component. Partial states with several components are allowed (they may merge
   via later columns), but a state in which an old component can never reconnect
   is killed immediately ("stranded → dead"), and closure requires one
   component.

The DP carries, per signature, a vector "how many distinct partial animals reach
this signature, by cell count." Distinct partial animals that share a signature
are summed (that is the whole point — it collapses an exponential animal count
into a polynomial state count). Each *complete* animal corresponds to exactly one
column sequence from seed to closure, so summing the closure counts gives the
exact number of animals. `byHeight[H][n]` is that sum; `a(n) = Σ_H byHeight[H][n]`.

---

## 3. Code map (component by component)

The engine is deliberately split into small, separately testable pieces.

### `cpp/tma/signature.h` — the boundary state
- `struct Sig { unsigned char b[SIGMAX]; }` — the signature as fixed bytes:
  `b[0..H)` = per-row component label (0 = empty, else a small integer label),
  `b[H]` = touched-top flag, `b[H+1]` = touched-bottom flag. Fixed size (no heap)
  so it can be a flat-hash-map key. SIGMAX = 32 ⇒ supports H ≤ 30.
- `canonicalizeSig` — relabels components 1,2,3,… in order of first appearance.
  Two boundaries with the same occupancy+connectivity but different label *names*
  become identical, so the DP merges them. (This is bookkeeping; it does not
  change which animals are distinct.)
- `completionLowerBound` — an **admissible** lower bound on how many *more* cells
  any completion of this boundary must place to become a valid height-H animal.
  Used only to prune (see §4). Three disjoint contributions, all provably forced
  because future cells can only extend rightward from the current column:
  - *top reach* `tr`: if row 0 never touched, climbing to it costs ≥ tr cells;
  - *bottom reach* `H−1−br`: symmetric;
  - *separating bands*: an empty row-band between two occupied rows that **no
    single component spans** must be bridged by a king path → ≥ its width. (A
    band a component already spans, via history, costs nothing — this is what
    keeps the bound from over-counting under interleaved labels like A,B,A.)

### `cpp/tma/transition_square8.h` — one column step (the core)
- `stepColumnSquare8(old, H, mask, out)` — given the current boundary `old` and a
  bitmask of which rows the new column fills, it:
  1. builds union-find over {new-column rows} ∪ {old component labels}, uniting a
     new cell at row r with the new cell at r+1 (vertical) and with old labels at
     rows r−1, r, r+1 (the king neighbours to the left) — handling k-way merges
     and crossing partitions with no special cases;
  2. returns **Dead** if any old component has no new-column cell adjacent to it
     (it is stranded — can never reconnect → would force a disconnected animal);
  3. otherwise writes the new canonical signature (labels from the union-find
     roots) and the updated touch flags, and returns **Alive**.
  Uses stack arrays (bounded by `2*SIGMAX`), no heap allocation on the hot path.
- `forEachViableMask(old, H, budget, fn)` — enumerates exactly the nonzero new
  columns worth trying: popcount ≤ budget (can't overshoot n) and no old
  component stranded. It generates only these (a recursion that prunes branches
  which can't cover every component), instead of looping all 2^H masks.
  `stepColumnSquare8` still re-checks stranding, so it remains the single source
  of truth; the generator is purely a "don't bother trying" optimisation.

### `cpp/tma/statedb.h` — the state store
- `FlatDB` — an open-addressing (linear-probe) hash map from `Sig` to a
  counts-by-size row, all in three flat arrays (keys / values / used-flags). No
  per-entry allocation, no pointer chasing. `slot()` find-or-inserts; `for_each`
  is the only read-back path; `clear()` resets occupancy without bulk-zeroing the
  values (rows are zeroed on insert). `addCounts` accumulates a shifted counts
  row into a destination signature. (The serial run uses this directly; it is the
  "designed to be replaced" component.)
- `SweepResults` carries `byHeight`, `totals`, and a peak-state high-water mark.

### `cpp/tma/sweep8.h` — the per-height sweep
- `sweepSquare8Height(H, maxn, res)` — the serial DP for one height: seed the
  empty boundary, then for each column move every live state through
  `forEachViableMask` → `stepColumnSquare8`, applying the size-budget prune
  (`min cells so far + cells added + completionLowerBound > maxn ⇒ drop`), and
  harvest closures (`mask == 0`: a single-component boundary touching top and
  bottom contributes its counts to `row`). Returns `byHeight[H]`.
- `sweepSquare8HeightMT(...)` — identical algorithm, but the output map is split
  into S shards (by signature hash) under per-shard mutexes and the source states
  are fanned across threads. Because per-shard counts only **accumulate**
  (commutative) and routing is deterministic by hash, the result is
  **bit-identical to the serial sweep** regardless of thread interleaving.
- `sweepSquare8(maxn, nthreads)` — loops the heights and sums.

### `cpp/tma_main.cpp` — driver
- CLI: `tma square8 MAXN [--per-height] [--checkpoint DIR] [--threads N]
  [--only-height H]`.
- `--checkpoint DIR`: after each height finishes, its row is written atomically
  (temp file + rename) to `DIR/hH.txt`; on restart, completed heights are
  reloaded instead of recomputed. A `meta` file guards against resuming with a
  mismatched lattice/MAXN. So a crash costs one height, not the run.
- `--only-height H`: compute a single height (used to run the independent heights
  as separate jobs and to measure per-height scaling).

---

## 4. Why we trust it

**Correctness of the prune.** The size-budget prune drops a state only when its
minimum cell count plus `completionLowerBound` exceeds n. If that bound ever
*over*-estimated, a real animal could be dropped and a count would come out
**low**. It cannot come out high. So the gate below is a complete admissibility
oracle: reproducing every published term proves the prune never dropped a real
animal in that range.

**The validation chain (`tests/gate_tma.py`, run by `make gate-tma`).**
- **Totals vs external truth:** the transfer-matrix totals equal A006770 (pinned
  b-file `fixtures/b006770.txt`) for the whole published range. The live a(19)
  run re-confirms a(n) for every n ≤ 18 as it goes (a(n) is final once all
  heights ≤ n are done), so any error would surface *before* a(19).
- **Cross-engine structural check:** the transfer matrix's per-height marginals
  (`--per-height`) equal the generation engine's per-bounding-box height
  marginals — two different algorithms agreeing not just on totals but on the
  finer (height, size) breakdown.
- **Sanitizers:** an AddressSanitizer/UBSan build agrees with the optimized build
  (no memory errors); a ThreadSanitizer build of the multithreaded path reports
  **zero data races**, and MT output is byte-identical to serial.
- **Compiler/ISA diversity:** the engine reproduces A006770 built with both Apple
  clang on ARM (gympie) and GCC on x86 (ayr).

**The headline result (confirmed 2026-06-16).** Method A (two decorrelated
Redelmeier campaigns) and Method B (column transfer matrix) **both** give

```
a(19) = 151,609,203,011,580
```

Method B's per-height rows (`~/poly-tma/runs/tma-a19/` on ayr) assemble to
a(n) = Σ_H byHeight[H][n], which is byte-identical to A006770 for every n ≤ 18
and equals Method A at n = 19. Two algorithms with no shared counting logic
agreeing — plus agreement with all 18 prior published terms — is the basis for
submission. (Extra cross-checks: a backward completion DP on a different
host/compiler/ISA reproduced byHeight[17][19] = 47,839,787,379 identically, and
the transfer-matrix per-height marginals match the generation engine's.)

---

## 5. Reproducing it

```
make gate-tma                         # full validation against A006770 + generation engine
build/tma square8 18                  # serial totals through the last published term (minutes)
build/tma square8 19 --checkpoint DIR # the a(19) run (resumable; large, run on a big-RAM host)
```

The b-file to submit is the transfer-matrix `totals` (n=1..19), which equals
A006770 on 1..18 and extends it by a(19). Provenance (host, git commit, binary
SHA, parameters) for each run is appended to `ledger/ledger.jsonl`; the
human-readable confidence record is `RESULTS.md` (entry R1).
```
