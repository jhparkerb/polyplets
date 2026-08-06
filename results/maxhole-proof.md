# Toward a proof of M(n) = round((n−2)²/8) (max enclosed hole area)

2026-07-11 (with jasonp). M(n) = max total enclosed empty area over n-cell
king-polyplets, 4-connected background. Confirmed exact by `g2 --maxhole` for
n≤17 (`results/maxhole.txt`); M(17)=28 matched the prediction. Machinery/
verification: `experiments/maxhole_proof_check.py`.

**STATUS (2026-08-06, third correction the same day, both papers now read).**
The theorem is **not ours, and it is no longer open**. Both halves are the
grid isoperimetric inequality, cited:

- **Single hole: a cited theorem.** `M_single(n) = ⌊((n−2)²+4)/8⌋` for every
  n ≥ 4. It is Sieben 2008 Theorem 4.1 *verbatim* — `σ(e) = ⌊e²/8 − e/2 + 1⌋`,
  the maximum size of an animal of site-perimeter e — not even inverted.
  (I'), (II') and the moat-cycle argument below reprove it from scratch, which
  is worth keeping as an independent check and is not worth claiming.
- **All holes: PROVED (2026-08-06), and also not ours.** Altshuler, Yanovsky,
  Vainsencher, Wagner & Bruckstein (DGCI 2006) prove the same minimum for an
  **arbitrary finite subset of ℤ²**, with no connectivity hypothesis. Apply it
  to the union of *all* the holes at once and the multi-hole bound is three
  lines (§The union argument). The overlap-counting question this note stopped
  on yesterday does not need answering: it was an artefact of bounding each
  hole separately.
- **Lean** (`Polyplets/HolesUpper.lean`) takes (II') as the named hypothesis
  `MoatBound`, since mathlib has no discrete-Jordan material to build the
  winding argument on. So `maxhole` is conditional there even though the paper
  proof is complete. The union argument would need the isoperimetric
  inequality itself as a hypothesis instead — not obviously an improvement in
  Lean, and not attempted.

A paper may state both halves outright **with the citations, not as new
results**. What remains ours is the *question* — nobody in the polyomino-hole
literature seems to have asked for maximum hole area — plus the enumeration
that confirms it to n = 17, and the reproofs.

## The literature: M(n) is Sieben's σ, verbatim (2026-08-06, both papers read)

The **site-perimeter** of a polyomino is the number of empty cells edge-adjacent
to it. Sieben 2008 gives both directions, for polyominoes (edge-connected, holes
allowed, the paper's own convention):

> **Theorem 4.1 (Sieben 2008).** For e ∈ {4, 6, 7, 8, …}, the maximum size of an
> animal of site-perimeter e is `σ(e) = ⌊e²/8 − e/2 + 1⌋`.
>
> **Theorem 5.3 (Sieben 2008).** The minimum site-perimeter of an s-cell animal
> is `ε(s) = ⌈2 + √(8s−4)⌉`.

**σ is M on the nose** — `⌊e²/8 − e/2 + 1⌋ = ⌊((e−2)²+4)/8⌋`, no inversion, no
rounding convention. (e = 5 is outside Theorem 4.1's domain, since no animal has
site-perimeter 5; M(5) = σ(4) = 1 anyway, so the closed form needs no case
split. σ is strictly increasing, Sieben Lemma 4.2, which is what makes
"site-perimeter ≤ n" and "site-perimeter = n" interchangeable for us.)

**The single-hole upper bound is then three lines.** Let H be a sealed hole of
area A in an n-cell king animal F. H is 4-connected, so it is a polyomino. Every
cell edge-adjacent to H from outside is foreground: a background one would be in
H's own 4-component. So H's site perimeter is a subset of F, giving
`n ≥ |sp(H)| ≥ sp_min(A)`, i.e. `A ≤ M(n)`. The (I') parity count, the (II')
span bound, the moat-cycle winding argument and the four-caps step all reprove
this, independently and from scratch.

Two things the identification also settles:

- **Nothing in the single-hole bound is king-specific.** The hole is 4-connected
  and its sealing set is its 4-site-perimeter whatever the foreground's
  connectivity is. The "king factor 1/8, double the rook's 1/16" reading below
  is really *site*-perimeter against *edge*-perimeter; the 8 is the 8 of
  `√(8n−4)`, and the diagonal-wall argument explains why site perimeter is the
  cheaper measure rather than why kings are special.
- **The extremal shapes agree.** Sieben's minimisers are the diagonal
  diamonds/boxes, which is the family the construction below arrives at
  independently.

## The union argument: the multi-hole case is closed (2026-08-06)

Yesterday's version of this note stopped at an overlap count — how many
foreground cells two sealed holes can share — because it bounded each hole
separately and then had to reassemble. **Don't reassemble.** Bound the union.

Altshuler et al. (DGCI 2006) prove the grid isoperimetric inequality for an
**arbitrary finite subset** of ℤ², not just a connected one. Their `n(k)` is
`min{|N(A)| : A ⊂ ℤ² finite, |A| ≥ k}` with `N(A)` the 4-neighbourhood, given
exactly in their Theorem 1; their §3.1 Theorem 7 re-derives it by a
self-contained slanted-bounding-rectangle projection, again for every finite A.
Their minimisers come out connected ("optimal ⟹ simple", their Theorem 2), so
`n(k) = ε(k)`: **allowing disconnection buys nothing.**

> **Theorem (all holes).** For every n-cell king animal F, the total area of the
> enclosed holes is at most `M(n) = ⌊((n−2)²+4)/8⌋`.
>
> *Proof.* Let `A = ⋃ᵢ Hᵢ` be the union of the bounded 4-components of ℤ² ∖ F,
> of total area `|A|`. Take `c ∈ N(A)`. Then `c ∉ A`, and c is 4-adjacent to
> some cell of some hole H_i; were c background it would lie in H_i's own
> 4-component, i.e. in H_i ⊆ A. So `N(A) ⊆ F` and `n ≥ |N(A)| ≥ n(|A|) =
> ε(|A|)`, whence `|A| ≤ σ(n) = M(n)`. ∎

The union A is exactly where connectivity had to be dropped — it is disconnected
whenever F has two holes — and dropping it is free. Tightness is the
single-hole construction below. The overlap question, the master inequality and
the peeling lemma are all superseded: none of them was ever the obstruction.

**What is still ours.** The *question* — no paper found stating the maximum
total hole area; the polyomino hole literature counts holes rather than
measuring them (Kahle & Roldán, maximally many holes f(n) ≈ n/2; Baralić &
Uppal, deep holes). The formula and both its bounds are the isoperimetric
inequality, cited. Enumeration to n = 17 confirms the statement independently.

Citations, both papers now held locally (`papers/INDEX.txt`):

- N. Sieben, "Polyominoes with minimum site-perimeter and full set achievement
  games," *European J. Combin.* **29**(1) (2008) 108–117.
- Y. Altshuler, V. Yanovsky, D. Vainsencher, I. A. Wagner & A. M. Bruckstein,
  "On minimal perimeter polyminoes," DGCI 2006, LNCS 4245, 17–28. (Five
  authors; earlier drafts of this note dropped Vainsencher.)

Checked rather than taken on trust, `experiments/maxhole_sieben_check.py`:
the minimum site perimeter brute-forced over all fixed polyominoes to n = 9
against ε (with an off-by-one RED control that must not match); `M(n) =
max{A : ε(A) ≤ n}` for n ≤ 2000 and the equivalence at every A ≤ 200,000;
σ(e) = M(e) directly; **Sieben's ε and Altshuler's n(k) agreeing at every
k ≤ 200,000**, i.e. the two papers state one theorem; superadditivity; the 17
banked rows of `results/maxhole.txt`; and the load-bearing hypothesis itself —
every ≥2-component subset of size k ≤ 10 (pairs, 3.4M configurations) and
k ≤ 8 (triples), over all relative placements within ±5, fails to beat ε(k).
It ties at k = 2 (a diagonal pair shares two neighbours) and loses by 1–2
everywhere else. The negative result is non-vacuous by construction: the run
asserts it reached placements whose components share neighbours.

## The formula and the extremal shape

M(n) = round((n−2)²/8) (round half up; the half-integers occur at n≡0 mod 4)
— equivalently, with no rounding convention at all, **M(n) = ⌊((n−2)²+4)/8⌋**
(the form `Polyplets/Holes.lean` already uses, `floor_maxhole_formula`;
identical for all n, checked to n=399).
The king factor is **1/8**, double the rook/polyomino ~1/16, because a **diagonal**
line of foreground cells seals the 4-connected background at one cell per step:
adjacent hole cells straddling a diagonal wall are not 4-adjacent, so a 45° wall is
half the cost of an axis wall. The extremal shape is a **diagonal diamond ring**.
(§The literature: the 1/8 is site-perimeter against edge-perimeter, not a king
fact — the same 8 as in Sieben's `√(8n−4)`.)

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

- **(Reduction) A single hole is optimal.** *No longer needed: §The union
  argument bounds every hole at once. Kept because the empirical check is still
  a check.* Splitting area over k holes is less
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

*An independent reproof of Sieben's bound, as it turns out (§The literature).
Kept as a check, and because it proves the sharper span form n ≥ ha+hm+2 rather
than the area form; the Lean file's `MoatBound` hypothesis is this statement.*

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

## Multi-hole reduction (2026-07-12) — SUPERSEDED by the Sieben route

*Everything in this section is the isoperimetric content, and the isoperimetric
content is now a citation (§The literature). The master inequality and the
peeling lemma remain true as far as checked and remain unproved; they are no
longer the shortest route, which is the sealing-set overlap count. Kept for the
refutations, which stay useful.*

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

## Refuted route: merging holes (2026-08-06)

The peeling route is not the only conceivable induction, so the obvious
alternative was tried and is dead. `experiments/maxhole_merge_probe.py`:

> **MERGE LEMMA (candidate).** A king animal with k ≥ 2 holes and total
> enclosed area A admits a nonempty W ⊆ F, |W| = t, such that F ∖ W is a king
> animal with fewer holes and enclosed area ≥ A + t.

Had it held, the multi-hole bound would follow from the single-hole theorem
with no isoperimetry at all: peel until one hole remains, having spent s cells
and gained ≥ s area, so `A + s ≤ M_single(n−s) ≤ M_single(n)`.

**It fails at the very first multi-hole animal, n = 6:**

    (0,2) (1,1) (1,3) (2,0) (2,2) (3,1)     holes {(1,2)}, {(2,1)}

two unit holes sealed across a shared diagonal. No cell can be removed without
opening a hole to the exterior, so no witness exists at any t. 6230 failures
over all king animals with n ≤ 9.

The failure is structural rather than incidental, and the measurement says why.
Maximum total enclosed area over MULTI-hole animals, against the bound:

| n | multi-hole animals | max A (multi) | M(n) | slack |
|---|---|---|---|---|
| 6 | 2 | 2 | 2 | **0** |
| 7 | 42 | 2 | 3 | 1 |
| 8 | 544 | 3 | 5 | 2 |
| 9 | 5741 | 4 | 6 | 2 |

At n = 6 the multi-hole configuration is **tight**, so any argument that must
strictly gain area when it merges cannot survive the margin. The slack then
grows, which is the useful half of the measurement: an eventual argument may
assume n ≥ 7 and still have room, and the n = 6 case is two animals checked by
hand.

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

*All of them are closed. The original two — (II'), and the n ≢ 0 mod 4
construction — by the moat-cycle argument and the parity-aligned diagonal boxes
below. The one that replaced them, "how many foreground cells can two sealed
holes share?", was dissolved rather than answered: §The union argument never
splits the holes up, so there is nothing to share. Anyone reopening that
question should read that section first.*

Verification: `python3 -m experiments.maxhole_proof_check` (the original
machinery), `python3 -m experiments.maxhole_sieben_check` (the identification
with Sieben and Altshuler et al., and the disconnected-subset check the union
argument rests on). Data: `results/maxhole.txt` (M(n), n≤17, exact from g2).
