# Plan — hole-stratified counts + hole GFs in the transfer matrix (#28)

> **Status 2026-06-18:** deliverable (a) PRIMARY (4-bg) is built and validated —
> `cpp/tma/euler.h`, `cpp/tma/sweep8_holes.h`, `tma --holes`; byte-identical to
> the flood through n=14. Sign/border accounting unit-tested (`make gate-euler`).
> Remaining: n≥15 production run, the 8-bg companion, the GFs (b), and the
> `gate_tma.py` hole check. The convention/sign text below is the corrected,
> verified version. See ROADMAP #28 for the live status.

Carry hole count *inside* the column transfer matrix (`cpp/tma/`) so the
hole-stratified polyplet counts reach n=19 (matching the bare count's reach, no
per-animal flood) and, marking holes with `q`, yield the bivariate G_H(x,q) whose
fixed-hole-count slices are rational GFs. Validated against the n≤14 flood
oracle (`results/holes.md`, `build/g2 square8 N --holes/--holes8`).

## Central architectural fact: holes are a COUNT axis, not a state axis

The Euler characteristic is additive and the bit-quad contribution of each 2×2
window is a function of one adjacent **column pair** only — both columns are fully
present in `stepColumnSquare8` (the old boundary occupancy + the new `mask`). So
the number of holes of the *final* animal is a pure running tally accumulated
across the column transitions the engine already performs, exactly like the cell
count `n`.

Consequence: two partial animals that share a boundary signature but differ in
holes-so-far stay **merged in one state** (their future is identical) — their
counts live in different cells of a widened count vector. The **number of
distinct signatures (the memory driver) does not change.** Only the per-state
count vector widens by a factor (K+1), K = max holes tracked (~6 for n≤19). That
is the 12.5 GB → ~60–75 GB the roadmap predicts; it is *not* a state explosion.

This is the whole reason #28 is a tractable augmentation of the a(19) engine
rather than a new build.

## The bit-quad / border accounting (the stated correctness risk)

Euler number E_c = (#components under c) − (#holes under the dual of c). For a
binary image, Gray's 2×2-window formula gives 4·E_c = C1 − C3 + s·2·CD, where
over all 2×2 windows C1 = #windows with exactly one occupied cell, C3 = #with
exactly three, CD = #diagonal/checkerboard pairs, and **s is the convention
knob** (sign VERIFIED in `cpp/tma/euler.h` + `tests/euler_unit.cpp`, 191k random
images + the diamond/ring/pinch battery — my first draft had it backwards):
  - **s = −1** → 8-connected foreground (E_8fg). The polyplet IS 8-connected, so
    `comps_8fg = 1` and the **PRIMARY** hole count is a clean
    `holes_4bg = 1 − E_8fg` (Jordan dual / OEIS-A389193 convention = `--holes`).
  - **s = +1** → 4-connected foreground (E_4fg). The **companion**
    `holes_8bg = comps_4fg − E_4fg` (= `--holes8`).

**Implementation asymmetry the test surfaced:** the primary is a drop-in (the
animal's 8-connected component count is 1, already what the harvest checks). The
companion needs `comps_4fg` — the animal's component count under *4*-adjacency,
which is NOT 1 (the n=4 diamond splits into 4). The engine's union-find is
8-adjacency, so the companion requires a *second, 4-adjacency* component tally
threaded alongside. Both are cheap at the prototype's small H; the big n=19 run
can carry the primary only and leave the companion to the flood (capped at n=14)
unless the 4-adjacency tally is added.

Per-step encoding (keeps the hole axis small and integer):
- Track **holes-so-far** = comps − χ for the partial image *closed off at the
  current boundary column* (exterior treated as empty beyond it). Closing at the
  boundary makes χ a true integer Euler number at every step, so holes-so-far is
  a small nonneg integer (axis width ~7), not a wide swing.
- A transition old→new shifts holes-so-far by Δholes = Δcomps − ΔE, where ΔE is
  the closed-image Euler delta = internal windows (old,new) + right-edge windows
  (new,exterior) − right-edge windows (old,exterior), all /4 (integer per step
  under this closing), and Δcomps = newcomps − oldcomps (union-find already
  computes newcomps; oldcomps = max label of `old`, 0 for the seed).
- The **right-edge (border) windows** — boundary column against the empty
  exterior — are the subtle part the roadmap flags. They must be added at every
  step (not just at close) for the closing identity to hold, and they are a
  function of the boundary column alone.
- **No silent truncation.** Size the hole axis generously with a hard overflow
  assert (abort loud if an index would exceed the band), mirroring the engine's
  fail-loud-on-inadmissible-prune philosophy. The flood gate catches a low count.

Sharp test cases for the sign/border logic (from `results/holes.md`): 4-bg first
hole at **n=4** (the diamond), 8-bg first hole at **n=8** (the 3×3 ring); 2 holes
first at n=6; 3 holes first at n=8.

## File-by-file change list (`cpp/tma/`)

All changes are gated behind a `--holes` flag so the plain a(n) hot path is
byte-unchanged (the gate proves it).

1. **statedb.h** — widen the count vector to 2-D `(size, holeIdx)`.
   - `stride` becomes `(maxn+1) * (K+1)`; index `n*(K+1) + h`. `FlatDB` already
     stores rows as flat `stride`-apart spans, so this is a stride change plus
     index arithmetic — no structural change to the open-addressing store.
   - `addCounts(FlatDB&, sig, src, sizeShift, holeShift, maxn)` — add a hole
     shift alongside the existing size shift (drop rows exceeding maxn or K, the
     latter only if the overflow assert is disabled).
   - `minSizeRow` → smallest size with any nonzero across hole cells.

2. **transition_square8.h** — emit the Euler delta.
   - `stepColumnSquare8` already runs the union-find; have it also return
     `newcomps` (currently recomputed by the caller as max label) and the
     closed-image ΔE for `(old, mask)`. Add a small helper `eulerDelta(oldOcc,
     mask, H, s)` that sums the 2×2-window classes over rows −1..H−1 with zero
     padding, for the internal pair and the two right-edge pairs.
   - `forEachViableMask` is unchanged (hole count never prunes the mask set).

3. **sweep8.h** — thread the hole shift through both drivers.
   - In `sweepSquare8Height` and `…HeightMT`: at the `addCounts` call, pass
     `holeShift = Δcomps − ΔE`.
   - **Harvest/close** (`comps==1 && sig.b[H] && sig.b[H+1]`): the closing pair
     (boundary→exterior) is already folded into holes-so-far by the per-step
     border accounting, so harvest just reads holes = the current holeIdx and
     adds `counts[n][h]` into a 2-D `row[n][h]`. (Assert comps==1 ⇒ the only live
     hole indices are the true final hole counts.)
   - `Counts` row and `SweepResults::byHeight` become 2-D `(n, holes)`.

4. **tma_main.cpp** — flag + output.
   - `--holes` (and `--holes8`, or `--hole-bg {4|8}`) selects the convention `s`.
   - Per-height / checkpoint output line `h n holes count`; checkpoint
     `loadHeight`/`saveHeight` and the `meta` guard extended to carry the
     convention. The `--only-height` path is what the GF recovery consumes.
   - The `--perimeter` path is the existing precedent for a (size, X) joint
     distribution emitted from this engine — mirror its CLI/printf shape.

## Deliverable (a): hole-stratified counts to n=19

`build/tma square8 19 --holes --per-height --checkpoint DIR` →
byHeight[H][n][holes]; assemble holes-stratified a(n) = Σ_H. Memory ~60–75 GB at
full n=19 → **ayr / out-of-core (#20)**; the **small-/mid-H prototype runs on
gympie now** (axis width ~7 × cheap low-H state).

## Deliverable (b): bivariate hole GFs G_H(x,q)

Marking holes with q, [q^k] G_H(x,q) = the size-GF of height-H polyplets with
exactly k holes — C-finite for the same reason the plain fixed-height rows are
(finite transfer matrix; q-marking keeps it finite-dimensional). Pipeline reuses
the existing GF machinery unchanged:
  - `build/tma square8 N --only-height H --holes` → terms B_{H,k}(n) per hole
    slice k.
  - feed each fixed-k slice to `gf/recover.py` (Berlekamp–Massey over Q) →
    rational P_{H,k}(x)/Q_{H,k}(x). Use the **adaptive term count** (grow N until
    the recovered order sits well below N/2) — the lesson from the order-sequence
    work (two debunked conjectures from under-determined BM); see
    `results/fixed_height_gf.md`.

## Validation plan (the gate)

Fold into `tests/gate_tma.py` (which already checks per-height marginals):
1. **Sum invariant.** Σ_holes byHeight[H][n][holes] == the plain byHeight[H][n]
   (and Σ_H == A006770) for all n in range — proves we partition the right set.
2. **Flood agreement.** The (n, holes) table == the `g2 --holes` / `--holes8`
   flood tables for **both conventions through n=14** (the oracle in
   `results/holes.md`: e.g. 4-bg hole-free n=4 = 109, exactly-1-hole n=4 = 1,
   8-bg first hole n=8). A mismatch here = bit-quad sign or border-window bug.
3. **GF held-out.** Each recovered G_{H,k} reproduces terms beyond its fit
   window and matches the independently computed B_{H,k}(19).
4. **Plain path unchanged.** Without `--holes`, a(n) byte-identical to current
   (the hole code is fully gated).

## Sequencing

- **Now, gympie:** build the `--holes` path, validate small/mid-H against flood
  (n≤14), recover the small-/mid-H bivariate GFs. No dependency on #19/#20.
- **Heavy half (needs ayr ~Jun 27, ideally #20 for RAM):** full n=19
  stratification, ~60–75 GB.
- Outputs feed **#25** (hole sequences + GFs) and **#17**.
