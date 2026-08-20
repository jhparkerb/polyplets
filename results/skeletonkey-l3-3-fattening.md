# L3-3: the fattening bijection exists, and that is why it is worthless

2026-08-20, branch `skeletonkey`. Probe
`experiments/skeletonkey/l3_3_fattening.py`, run on ayr; the cost arithmetic is
desk work on banked numbers.

`results/r4/r4-floors.md` §"Routes the floors do not close that have been
treated as closed" objects that L3-3 and L3-4 were pruned by a rank floor, and
that "paying a floor of ~1.5e4 at H = 21 is not a cost objection to anything".
It calls both kills "merely asserted". `docs/skeletonkey-reprompt.md` then found
a second and sound kill for L3-4 (the dual-connectivity comparison,
`docs/lastditch-ideas.md` §6), leaving **L3-3 as the one genuinely open row**.

The row, from `git show triangle-structure:results/triangle-r3-queue.md`:

> **L3-3** Object change, not encoding change: bijection from king animals to a
> decorated polyomino class on a refined lattice (fatten each cell to a 2×2
> block, fill a marked corner cell at each pinch) — boundary becomes pinch-free
> and edge-based, so polyomino contour/SAP technology applies verbatim to the
> image class.
> OPEN | half-formed; injectivity and the marked-cell convention need checking
> at small n

Both halves are settled here. The construction **works** — that is the new
result — and the route dies on what the working construction costs.

## 1. The construction, and it is sound

King cell `(x, y)` fattens to the refined block
`{2x, 2x+1} × {2y, 2y+1}`. Fattening alone does not remove pinches: two
diagonally adjacent king cells still meet at a single refined corner point. A
grid corner `(x, y)` pinches when exactly one diagonal pair of the four king
cells meeting there is in the animal; the two absent cells are the two
candidate blocks for a filler, and each contributes the one refined cell it
owns at that corner. The marked-cell convention is the choice between them.

Four conventions were run over **every king animal to n = 8** — 176,138 of
them, count-gated against A006770 — and each was asked whether the image is
pinch-free, whether full 2×2 blocks decode back to the animal, and whether two
distinct animals ever share an image up to translation.

| convention | pinch-free | full-block decode | injective |
|---|---|---|---|
| `none` (RED control) | **NO**, first at n = 2 | — | yes |
| `lex` (filler to the lex-smaller candidate block) | YES | recovers every animal | YES |
| `lexmax` | YES | recovers every animal | YES |
| `both` (fill both candidates) | **NO**, first at n = 6 | **FAILS at n = 4** | yes |

The RED control is `none` — fatten and fill nothing — which must come out
pinched, since a diagonal contact is still a corner contact after fattening. It
fires at n = 2 on the domino `{(0,0), (1,1)}`. Without it the pinch detector
would have no teeth and no other row of the table would mean anything.

`both`'s decode failure is the informative one, and it is the natural trap: on
the 4-cell diamond `{(0,1), (1,0), (1,2), (2,1)}` the four pinches all point at
the empty centre block, filling it, and the image becomes the image of the
5-cell plus-pentomino. Fill-both is still injective — the outer marks
distinguish the two — but its images can no longer be read off block by block.

**`lex` is injective for a reason, not by measurement.** Block `(x, y)` owns
refined cell `(2x, 2y)` at grid corner `(x, y)`, and the two candidates at that
corner are always `(x−1, y−1)` and `(x, y)`, of which the block itself is the
lex-larger. So a block never wins the mark at its own bottom-left corner, its
bottom-left cell stays empty unless the block is a real animal cell, no block
is ever completed by marks, and **full blocks are exactly the animal**. The
decoder column of the table tests that statement rather than its shadow.

So the queue row's two flagged doubts are both resolved in the route's favour.
The image really is a pinch-free, edge-bounded polyomino, and the map really is
a bijection onto its image with a linear-time inverse.

## 2. Why the working construction buys nothing

**A bijection restates a counting problem; it does not reduce one.** The map is
local — a refined cell is determined by the animal within distance 1 — so
counting the image class *is* counting king animals, with only local recoding
in between. Any method that counts the image class quickly counts king animals
quickly, and vice versa. For the route to be a route, the image class would
have to be countable by machinery that is fast for reasons having nothing to do
with king structure. The row names that machinery: polyomino contour/SAP
technology, applied **verbatim**. Verbatim means class-agnostic, and that is
the branch that costs.

**Verbatim machinery pays for a lattice of twice the height.** A king column of
height H becomes a refined column of height 2H. The incumbent's own column-state
law is banked exactly — `Motzkin(H+1) − 1`, `results/triangle-r3-involution.md`
§3 — and reading that same law at the doubled height is the honest measure of
what a class-agnostic sweep of the refined lattice is being asked to carry:

    incumbent, king column   H = 21   Motzkin(22) − 1 =             400,763,222
    same law, refined column h = 42   Motzkin(43) − 1 = 1,614,282,136,160,911,721

a factor of 4.0 × 10⁹. The only way back down is to re-impose the block
alignment — which is the king transfer matrix again, in refined coordinates.

**And the sizes are out of reach on their own.** The image of an n-cell king
animal has 4n cells before any marks, so a(40) would be carried by polyominoes
of **≥ 160 cells** and a(41) by **≥ 164**. Square polyominoes are enumerated to
n = 56 in the literature (`docs/lastditch-ideas.md` §1b). The route asks
polyomino technology to run at roughly three times its own world record, on a
subclass a class-agnostic method cannot see. That kills the level-1 reading
(second source for a banked value) as flatly as the reach reading.

## 3. Verdict

**L3-3 is closed**, and unlike the kill r4-floors complained about, it is not
the rank floor doing the work. r4-floors was right that "pays L3-1's rank floor
at any cut" is not a cost objection. The objection is the opposite one: the
image class carries *exactly* the king information, by construction and by
bijection, so it cannot be cheaper — while the verbatim machinery the row wants
to borrow is priced on a lattice of twice the height and objects of four times
the area.

The queue row's own honest prior — "level-1 value only" — turns out to be
generous by one level.

## What this does not settle

- The construction itself is now a **usable object**, independent of the dead
  route: king animals acquire a genuine edge-based boundary, hence a perimeter
  grading in the square-lattice convention. Whether that connects to breadth
  candidate #15 (Sykes–Essam matching pair, "alive, needs perimeter-graded
  enumeration") is **not examined here**. `results/matching-pair-convention.md`
  pins perimeter as SAME-lattice, so the question is whether the fattened
  boundary is the same perimeter that convention means. Unknown.
- Injectivity is proved for `lex` and measured for `lexmax`. No proof is given
  for `lexmax`, and none is needed.
- Nothing here touches L3-4, which was already closed independently, or the
  other r4-floors rows (R4-G18, the char-2 cut representation), whose "equal
  floors do not imply equal costs" complaint stands unaddressed.
- No claim is made about the image class's *own* cut rank or column-state
  count. The 4.0 × 10⁹ figure is the incumbent's banked law read at the doubled
  height, which is what a class-agnostic method is being asked to carry — not a
  measurement of the image class.
