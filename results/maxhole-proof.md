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
