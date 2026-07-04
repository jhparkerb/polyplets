# dmirror TM design (Hall of Mirrors — the last symtm mode)

State as of 2026-07-04: hmirror + r180 built, gated, n=34 runs launched.
dmirror is the remaining blocker for A030222/A030234/A030235 (+A194596) at
n=34. This is the design dig from 2026-07-04, pre-implementation.

## Facts

- dmirror = transpose invariance. The axis always passes through cells
  (half-integer diagonal axes are not lattice symmetries) — one placement
  class, matching symcount_fast.
- Bbox is forced square S×S, and **S runs to n=34, not 17**: the main
  diagonal itself is an n-cell dmirror-fixed polyplet. Tall-sparse regime
  exists, as in the other modes.

## Recommended geometry: hook sweep (not anti-diagonal)

Process hooks k=0,1,… (cells with min(x,y)=k), outer loop over exact bbox
S=1..34. Anti-diagonal sweep rejected: king moves reach TWO diagonals ahead
(Δ=(1,1) jumps x+y by 2) forcing a two-layer frontier, and bbox anchoring in
diagonal coordinates is a mess. Hook frontier = one hook, absolute coords;
hook 0 nonempty ⟺ touches row 0 and col 0 (symmetric); one
touched-outer-edge flag for row S-1 ⟺ col S-1.

**Fold**: a hook's row arm mirrors its column arm, so stored state = column
arm only (≤34 bytes + corner + flags — POLY_SIGMAX 40 suffices). Mask
enumeration = the palindromic-pair pattern from hmirror: enumerate the arm
mask (u64), row arm forced, corner weight 1, off-diagonal pairs weight 2.
Coverage/reach/band prunes port.

## Crux 1 — selfPaired bit

A column-arm component A has a mirror image A′ on the row arm; they are
either THE SAME component (crosses the diagonal in history) or two distinct
components swapped by the mirror. Fold carries one bit per label:
selfPaired. Load-bearing at harvest: single arm label + selfPaired =
complete animal; single label NOT selfPaired = two disjoint mirror halves =
reject. Transition = unfold (A → A, A′ unless selfPaired), union-find over
real hook adjacencies, refold. Same pairing bookkeeping family as r180's
seam glue (built and validated there).

## Crux 2 — corner stencil

Linearized (column arm, corner, row arm), hook→hook adjacency is the
ordinary ±1 column stencil EXCEPT at the corner: new corner (k+1,k+1) is
king-adjacent to FIVE old hook cells — (k+2,k),(k+1,k),(k,k),(k,k+1),
(k,k+2) — a ±2 stencil at that one position. So stepColumnSquare8 is not
reusable; dmirror needs its own ~80-line hook step (same
union-find/stranding/canonicalize skeleton). This corner is where the bug
will live; add a targeted small-n identity check for ring-like symmetric
animals (halves connecting only through the diagonal) on top of the
gate_symtm cross-algorithm diff and the runs/sym24 oracle.

## Crux 3 — reach bound

hmirror's "owes 2t" prune weakens: the diagonal is a cost-1-per-step escape
route (a diagonal cell is its own mirror), so the safe reach charge to the
outer edge is ×1 not ×2. Start weak-but-admissible, tighten by measurement.

## Lessons to carry over from r180 (measured 2026-07-04)

- Post-step charging is nearly worthless; prunes must live IN the mask
  generator's recursion (r180: 18.3s → 9.2s at n=18 from that move alone).
- Coverage-style debts can ride as prune-only OR-merged per-state masks
  (never keyed) whenever the closing check is a faithful connectivity
  computation that auto-rejects uncovered animals.
- The structural symmetry lever: for r180 the transpose restriction (W≥H,
  weight 2/1) collapsed tall strips, 86× at n=20. dmirror is transpose-FIXED
  so that exact trick is unavailable — but the per-S outer loop plus
  exact-bbox column/row debts play the same role (a strip-S state owes
  enough future hooks/cells to reach the outer edge both ways).
- Cost expectation: hmirror-class (~hours cpu, ~1h dalby wall) if the tall-S
  regime is controlled; measure the n=24 ladder before believing anything.
