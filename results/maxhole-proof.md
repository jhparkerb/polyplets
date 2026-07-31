# Toward a proof of M(n) = round((n−2)²/8) (max enclosed hole area)

2026-07-11 (with jasonp). M(n) = max total enclosed empty area over n-cell
king-polyplets, 4-connected background. Confirmed exact by `g2 --maxhole` for
n≤17 (`results/maxhole.txt`); M(17)=28 matched the prediction. Here: a near-complete
proof, reduced to one clean open lemma. Machinery/verification:
`experiments/maxhole_proof_check.py`.

## The formula and the extremal shape

M(n) = round((n−2)²/8) (round half up; the half-integers occur at n≡0 mod 4).
The king factor is **1/8**, double the rook/polyomino ~1/16, because a **diagonal**
line of foreground cells seals the 4-connected background at one cell per step:
adjacent hole cells straddling a diagonal wall are not 4-adjacent, so a 45° wall is
half the cost of an axis wall. The extremal shape is a **diagonal diamond ring**.

## Lower bound (construction) — done for n ≡ 0 mod 4

The diamond ring {(x,y) : |x|+|y| = r} has **n = 4r** cells and encloses exactly
{|x|+|y| ≤ r−1}, which is **2r²−2r+1 = round((n−2)²/8)** cells. So M(4r) is achieved
exactly (verified r=1..6). Its boundary is four diagonal walls → the 1/8 packing.
*Open detail:* the extremal shapes for n ≢ 0 mod 4 are elongated diamonds; the
formula is confirmed but a clean closed construction for all residues isn't written
(symmetric octagons fall 1 short — the intermediate optima are slightly asymmetric).

## Upper bound — reduced to lemma (II'); (I') + reductions in hand

Work in diagonal coordinates u = x+y, v = x−y (all cells have u ≡ v mod 2). For a
single 4-connected hole H, let **ha = range of u over H**, **hm = range of v over H**.

- **(Reduction) A single hole is optimal.** Splitting area over k holes is less
  efficient (⌈ha·hm/2⌉ is superadditive against a shared cell budget — two holes of
  half the linear size enclose ~½ the area). Verified: over 2680 random
  hole-polyplets, total area never exceeds M(n) even with multiple holes. So M(n) is
  attained by a single hole and it suffices to bound that case.

- **(I') A ≤ ⌈ha·hm/2⌉.** Every hole cell has u in an interval of length ha and v in
  one of length hm, with u ≡ v mod 2; the parity sublattice has ⌈ha·hm/2⌉ points in
  an ha×hm box. *This is an elementary lattice-point count — provable directly.*
  Verified (0 violations, tight on diamonds).

- **(II') n ≥ ha + hm + 2.**  ⟵ **THE OPEN CRUX.** Enclosing a single 4-connected
  hole whose diagonal extent is ha×hm requires at least ha+hm+2 king cells.
  Verified on ~1600 single-hole polyplets (0 violations, tight on every diamond).

**Combine.** Maximize ⌈ha·hm/2⌉ over positive integers with ha+hm ≤ n−2 (from II'):
the max is at ha,hm as equal as possible, giving ⌈⌊(n−2)²/4⌋/2⌉ = round((n−2)²/8) =
M(n). Using integer ha,hm (not real AM-GM) makes this **exact**, matching M(n) for
every residue — no off-by-one. ∎ modulo (I') and (II').

## What's proved vs open

## (II') PROVED — the moat-cycle argument (2026-07-12)

The winding-number route works. Five steps, each machine-checked end-to-end on
3,927 random single-hole king animals (116 with pinched contours exercising the
loop-erasure; 3,356 tight) — `experiments/maxhole_moat_check.py`, 0 failures.

1. **Moat walk.** Trace the outer contour of the hole region R (union of its
   unit squares). Across every boundary edge lies a foreground cell (else the
   hole leaks 4-connectedly or extends). Consecutive boundary edges share a
   corner and their outside cells are equal, 4-adjacent, or diagonal — including
   at pinch corners, where they are exactly the diagonal sealing pair. So the
   outside cells form a closed king-walk γ ⊆ F with winding 1 around R.
2. **Winding constant on the hole.** γ's polygon passes only through F-squares
   (touching hole squares at most at corners), while hole centers are 4-connected
   through hole squares; the connecting segments avoid γ's polygon, so all hole
   centers lie in one component of the complement — one winding number.
3. **Loop-erasure.** If γ repeats a cell, split there into two closed subwalks;
   winding numbers add, so one part keeps winding ≠ 0 (by step 2, around the
   WHOLE hole). Iterate → a SIMPLE cycle σ ⊆ F, winding ≠ 0 around every hole cell.
4. **Escape segment ⇒ four caps.** If σ stayed in u ≤ u_max, the top hole cell's
   center would connect to infinity along the ray (1,1) without meeting σ
   (σ ∌ that cell and lies weakly below the line) — winding 0, contradiction.
   So σ attains u ≥ u_max+1; symmetrically u ≤ u_min−1, v ≥ v_max+1, v ≤ v_min−1.
5. **Count.** In diagonal coordinates a king step has |Δu|+|Δv| ≤ 2. σ is closed
   and spans u across ha+1 and v across hm+1, so Σ|Δu| ≥ 2(ha+1), Σ|Δv| ≥ 2(hm+1),
   giving |σ| ≥ ha+hm+2. σ is simple, so n ≥ |σ| ≥ ha+hm+2. ∎

(Write-up rigor still owed on step 1's contour construction — standard
marching-squares/Jordan material — and step 3's winding bookkeeping; the
mathematical content is complete.)

## Status after the moat proof

- (I') A ≤ ⌈ha·hm/2⌉: elementary parity count — done.
- **(II') n ≥ ha+hm+2: PROVED (above).** With (I') and the integer maximization,
  the SINGLE-HOLE upper bound M_single(n) ≤ round((n−2)²/8) is a theorem.

## The uniform construction (2026-07-12) — lower bound complete for ALL n

**Parity-aligned diagonal-box holes.** Hole(a,b) = all cells with u ∈ [0,a−1],
v ∈ [0,b−1] (corner-aligned so the populated parity class dominates: area
⌈ab/2⌉); animal = its 4-neighbour ring, which has **exactly a+b+2 cells**, is
king-connected, and encloses exactly the box. Choosing a+b = n−2 with the
near-equal parity-optimal split achieves **round((n−2)²/8) for every n ≥ 4**
(n=5 via the n=4 diamond plus one padding cell, M(5)=M(4)=1). Verified n ≤ 60,
matching banked M(n) exactly for n ≤ 17: `experiments/maxhole_box_construction.py`.

*Caveat (2026-07-31 adversarial review of the Lean formalization,
docs/reviews/outworks-adversarial.md): the unqualified a+b+2 claim above
holds only off the degenerate margin — the 4-neighbour ring has a+b+1 cells
when min(a,b)=1 with max(a,b) even, and the box is not one 4-connected
region (so the ring is a multi-hole animal, not a single-hole witness) when
min(a,b)=1 with max(a,b) ≥ 3; measured for all a,b ≤ 12 by
`experiments/maxhole_review_checks.py`. The optimizing split above never
enters that margin, so every stated M(n) value is unaffected. The Lean
construction (`Polyplets/Holes.lean`) uses the diagonal frame
hullBox∖boxHole instead, which has a+b+2 cells for ALL a,b and subsumes the
n=5 padding cell. The paper's §8 sentence quoting the unqualified ring claim
should be qualified the same way.*
The diamond is the a=b odd case; the previously-mysterious "slightly asymmetric"
optima at n ≢ 0 (mod 4) are just the boxes with |a−b| ∈ {1,2}.

**⇒ M_single(n) = round((n−2)²/8) is now a two-sided theorem for all n.**

## Multi-hole reduction (2026-07-12) — reformulated, verified, one clean target

Fill the holes: F′ = F ∪ (holes) is a hole-free animal of size N = n + A. The
holes avoid F′'s 4-shell (cells with a 4-neighbour in the exterior — else leak),
so **A ≤ interior₄(F′)** and **n ≥ |shell₄(F′)|**. Everything then follows from
one isoperimetric statement about hole-free animals:

> **Master inequality (conjecture).** interior₄(F′) ≤ round((|shell₄(F′)|−2)²/8).

Verified on 6,000 random filled animals, **0 violations, 1,028 tight cases**;
solid diamonds are exactly tight (shell 4r, interior 2r²−2r+1). By n ≥ shell and
monotonicity this implies the multi-hole bound A ≤ round((n−2)²/8) outright.
- **Refuted route (recorded):** the range-form core "r_u+r_v ≤ shell−2 for the
  interior's diagonal ranges" is FALSE for disconnected interiors — minimal
  counterexample: two lone interior cells in separate lobes (11 filled cells,
  shell 9, r_u+r_v = 8 > 7). The moat argument needs the wound set connected;
  a filled animal's interior needn't be. The area bound survives because
  scattered interiors are far from filling their diagonal box.
- **Peeling route (2026-07-12, pushed):** the master inequality follows from

  > **PEELING LEMMA.** Hole-free F′ with shell S and interior I, |I| ≥ 2 ⟹
  > |shell₄(I)| ≤ |S| − 4.

  because the recursion f(m) ≤ (m−4) + f(m−4) with the (constructively realized)
  bases f(4)=1, f(5)=1, f(6)=2, f(7)=3 telescopes to **exactly**
  round((m−2)²/8) for every m (verified m ≤ 199; the interior decomposes into
  hole-free king-components, and the inductive bound is superadditive so one
  component is worst). Peeling verified on 7,645 filled animals + adversarial
  families (combs, spirals, rectangles, diamonds): **0 violations**, tight
  exactly on diagonal-boundary shapes (onion rings drop by 4 per layer).

  **Decomposition of peeling into two verified sub-lemmas**
  (`experiments/maxhole_peeling_check.py`):
  - **(A-int)** each king-component J of an interior (|J| ≥ 2) has
    |shell₄(J)| ≤ r_u(J) + r_v(J) − 2. *False for general king sets* (14-cell
    counterexample found) but 0/7,599 on interior components with **6,744
    tight** — erosion components are exactly the sets for which the diagonal
    semi-perimeter is the right complexity measure. Open: why erosion tames the
    boundary (the exposed sides of interior cells face S, whose cells face the
    exterior — a two-layer rigidity not yet formalized).
  - **(Σ)** Σ_j max(r_u,j + r_v,j − 2, 1) ≤ |S| − 4 (0/7,645, 885 tight).
    The per-component moat-packing statement; each component's moat costs
    r_u+r_v+2 but overlaps are bounded so the shell is charged only r_u+r_v−2
    per component plus a global −4. Open: the packing argument.
  - Also refuted en route (recorded to save future work): the union-range core
    (two-lone-cells), the per-component sum Σ(r_u,j+r_v,j+2) ≤ |S| (7-cell
    two-plus example), and claim (A) for general king-connected sets.

## Superseded notes (pre-proof)

- (I'): elementary, essentially done.
- Single-hole reduction: needs the superadditivity written cleanly, but is standard.
- **(II') is the real theorem** and where your geometry helps. Partial progress:
  *the foreground extends exactly one diagonal step beyond the hole on all four
  sides.* Proof: let c\* be a hole cell with u(c\*)=u_max. Its 4-neighbours at
  u_max+1 are (x+1,y) and (x,y+1); neither is a hole cell (u_max is the max), and if
  either were exterior background, c\* would be 4-connected to the outside —
  contradicting "sealed". So both are **foreground**, at u = u_max+1. Symmetrically
  the foreground reaches u_min−1, v_max+1, v_min−1. Hence the foreground's u-range is
  ≥ ha+2 and its v-range ≥ hm+2.

  **The gap:** foreground u-range ≥ ha+2 and v-range ≥ hm+2 give only n ≥
  max(ha+2, hm+2), not the *sum* ha+hm+2. Getting the sum needs the **enclosing
  (winding) property**, not just the span — connectivity + span alone is far too
  weak (a diagonal path spans huge ha,hm with few cells but encloses nothing). The
  diamond shows the target is tight: every anti-diagonal in the hole's u-range is
  crossed by **two** foreground cells (the two sides of the ring), and the two
  v-extreme cells close it off — that "2 per level, summed over both axes" is the
  bound to formalize. A winding-number / discrete-Jordan-curve argument on the
  foreground cycle is the likely route.

## Questions for you

1. Is there a slick winding/parity argument for **(II')** — why a closed king-curve
   enclosing an ha×hm (diagonal) region must use ≥ ha+hm+2 cells? (This is the whole
   theorem; the rest is bookkeeping.)
2. The elongated-diamond construction for n ≢ 0 mod 4 — is there a clean uniform
   family, or is a small per-residue case analysis the honest answer?

Verification: `python3 -m experiments.maxhole_proof_check`. Data:
`results/maxhole.txt` (M(n), n≤17, exact from g2).
