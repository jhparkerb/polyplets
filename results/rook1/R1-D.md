# R1-D — adversary: the transport obstruction

Filed 2026-08-13. Charter: `docs/rook1-brief.md` §R1-D, running
`docs/rook-parity.md:88-90` as its negative, plus queue row K2
(diagonal-splice β ≥ 2). Everything below is desk work; the only compute was
foreground arithmetic, stated inline where it is used. Every
argument here is a hand argument and is labelled as such; nothing in this file
is formalized or machine-checked.

## §1 Surplus inventory — what a king cut actually carries beyond a rook cut

### 1a. Vocabulary: none. The cut vocabulary is shared, and that is provable, not just measured

The goal file asserts a "shared Motzkin cut vocabulary"
(`docs/rook-parity.md:47-49`) and gate 1 records the measurement: rook and
king closures reach identical state sets at every measured H ≤ 8
(`docs/rook-parity.md:120`). The code, meanwhile, hedges the other way:
`core/signature.h:8-13` says the generic partition representation "allows
CROSSING partitions … which the square-8 (polyplet) transition will need."

The hedge is over-provisioned. Hand argument that king (square-8) cut
partitions are non-crossing, same as rook:

- **Crossing lemma (L∞).** Two cell-disjoint king paths whose cell-center
  polylines cross in the plane must contain L∞-adjacent cells. Case analysis
  on segment pairs: orthogonal–orthogonal and orthogonal–diagonal segments can
  only meet at integer points, i.e. shared cell centers; the one transversal
  crossing at a non-cell point is NE-diagonal × SE-diagonal at a half-integer
  point, and there the four endpoint cells form a 2×2 square, pairwise
  L∞-adjacent. Since king adjacency IS L∞-adjacency, the two paths merge into
  one component either way. (This is exactly the surplus one expects king to
  have — disjoint strands crossing at a point — and L∞ adjacency is what
  confiscates it: the strands cannot cross without touching.)
- **Jordan step.** Suppose a reachable cut state had components A ≠ B with cut
  rows a < b < c < d, a,c ∈ A and b,d ∈ B (a crossing pattern). A king path
  inside A from (0,a) to (0,c) in the swept half-plane, closed up through a
  detour at x = +1/2 (which no animal cell can reach), separates (0,b) from
  (0,d). B's path from b to d must cross the closed curve; crossing the detour
  or its stubs forces a shared cell with A's endpoints, and crossing A's path
  forces L∞ adjacency by the lemma — either way A = B, contradiction.
  Boundary tangencies (A owning other cut cells above d, B touching the cut
  between a and c) are handled by taking the crossing witness with c − a
  minimal and descending; that step is standard but is the part I have not
  written out in full. Status: hand argument, believed complete, not
  formalized; independently corroborated by the measured identical state sets
  at H ≤ 8 (`docs/rook-parity.md:120`).
- Converse inclusion is trivial (king adjacency ⊇ rook adjacency, and every
  non-crossing pattern is rook-reachable), which is why the measured state
  sets are *identical*, not merely nested.

Collateral finding: the crossing-capable generic representation in
`core/signature.h` is dead weight for square-8; the compact Motzkin encoding
(T1(b), same file line 13) is valid for king too. Filed as queue row D5.

### 1b. Dynamics: the surplus is the action, not the alphabet

Same states, different transition monoid action:

- King's per-cell update consults three old boundary cells (width-3 stencil —
  the NW problem; `results/kink-carry.md:5-18`, the carry byte is its
  operational trace). Rook's consults one.
- Operational consequence: **gap-jumping merges.** Cut cells at rows r and
  r+2, gap empty at r+1, are separate components in both vocabularies; king
  merges them with ONE future cell at (next, r+1) — diagonal reach to both —
  while leaving the gap unoccupied. Rook can only merge them by paying cells:
  a bridge path whose cells then sit on the cut and alter every subsequent
  state. In king the merge is free of cell budget; in rook every merge is
  bought with n.

### 1c. Geometry: the bbox theorem is the real asymmetry

Rook animals satisfy min(H,W) ≤ (n+1)/2 (spanning argument: p columns and q
rows force ≥ p+q−1 cells), which is what lets the rook method sweep the short
side at Motzkin cost √3^n. King animals do not — the diagonal staircase has
min(H,W) = n (`docs/rook-parity.md:145-147`). The shared vocabulary must be
swept over cuts that can be Θ(n) wide. The cut *information* per unit width is
the same; what king lacks is the guarantee that some straight cut is short.

So the precise statement of the surplus: **not one extra state — an extra
generator in the action (gap-jump at zero cell cost) and a missing geometric
cap (no short side).** A reduction has to buy back both.

## §2 The requirement, precisely

A king→rook reduction that composes with the straight-cut rook TM and beats
the incumbent must be a map φ from n-cell king animals into rook animals of
≤ βn cells with:

- **(R0) budget:** β < ln b / ln √3, where b is the incumbent's per-n base.
  b = 2.42 gives β < 1.6124; b = 1.73 (the PROVENANCE cpu reading, R1-K §1d)
  gives β < 1 — strictly size-decreasing. R1-A's reconciliation picks b.
- **(R1) countability:** injective, or fibers of subexponential size with
  sweep-computable weights. Exponential uncontrolled fibers mean the image
  count is not a(n).
- **(R2) recognizability at no state cost:** "S ∈ image(φ)" must be decidable
  *within* the rook sweep with O(poly) extra per-state information — an image
  predicate needing its own exponential state multiplies the base and forfeits
  √3.
- **(R3) transport of the action:** since the vocabulary is shared (§1a),
  nothing about the states needs translating. What must be transported is the
  action and the geometry: every king gap-jump merge must be realized by
  bridge cells (≥ 1 cell each, §1b), every diagonal run must be re-embedded to
  a rook-cheap direction, and the staircase must land on an image with a short
  side — all under (R0)'s total budget, i.e. average added cells per king cell
  ≤ β − 1 over the *whole* animal class, worst case included.

That is what "size-preserving reduction must do to the Motzkin cut
information": leave the alphabet alone, pay cells for every merge the king
action got free, and pay embedding for every diagonal — within a budget of
0.61 extra cells per cell (b = 2.42) or zero (b = 1.73).

## §3 Obstructions

### 3a. Counting floor — every injective reduction, uniform or not

Image classes must be at least as numerous as sources:
β · ln λ_rook ≥ ln λ_king, so β ≥ ln λ_k / ln λ_r.

| inputs | floor on β |
|---|---|
| rigorous: λ_k ≥ 6.543 (certificate sandwich, `docs/rook-parity.md:38`), λ_r ≤ 4.5252 (Klarner–Rivest, `papers/klarner_rivest_1973_upper_bound.pdf`, `docs/glossary.md:48-49`) | **β ≥ 1.244** |
| best estimates: λ_k ≈ 7.12 (grand-form saddle, in-repo), λ_r ≈ 4.0625696 (`docs/glossary.md:48`) | **β ≥ 1.400** |

Both floors are `log λ_k / log λ_r`: log 6.543 / log 4.5252 = 1.2443, and
log 7.12 / log 4.0625696 = 1.4003. Two consequences:

- **Under b = 1.73 (R0 demands β < 1), transport is dead outright**, by the
  rigorous floor alone: 1.244 > 1. No cleverness escapes an injective
  counting bound. This couples the transport verdict to R1-A / queue rows
  K1, K3.
- **Under b = 2.42, counting can never close the kill.** Pushing the floor to
  1.6124 needs λ_k ≥ 4.0626^1.6124 = 9.586 (est. λ_r) or ≥ 4.0025^1.6124 =
  9.358 (rigorous lower λ_r) — both above the certificate ceiling 9.3154. So
  a corridor **β ∈ [1.40, 1.61]** survives arithmetic *permanently*; anything
  that kills it must come from (R2)/(R3), not counting.

### 3b. Uniform family killed at exactly 2 — and K2 derived

**Claim.** Every translation-covariant reduction (image = injective affine
cell embedding φ plus any added bridge cells) has β ≥ 2 − 1/n; and β = 2 is
achieved. So the uniform-family optimum is exactly 2, and no member sits
below 2. Hand derivation:

1. Translation covariance forces φ affine: φ(x) = φ(0) + L(x), L an injective
   lattice map Z² → Z².
2. **Pigeonhole, 8 → 4.** King has 8 unit directions; rook-adjacent offsets
   number 4. L injective sends the 8 to 8 distinct offsets, so at most 4 land
   at L1-norm 1 — at least 4 king directions (≥ 2 antipodal axes, since
   L(−d) = −L(d)) map to offsets of L1 ≥ 2.
3. **Both diagonals cheap is impossible**, so an expensive axis can always be
   chosen diagonal or the embedding already loses an orthogonal axis:
   L(1,1) + L(1,−1) = 2·L(1,0) must be even; the sum of two distinct
   non-antipodal L1-unit vectors never is, and equal or antipodal choices make
   L non-injective. (Identity: both diagonals cost 2. The 45°-shear: NE and E
   cost 1, but N costs 2 and SE costs 3 — this is the rotation family the
   repo already measured worse, commit 210fb0b.)
4. **Staircase along an expensive axis.** Take d with s = |L(d)|_{L1} ≥ 2 and
   the n-cell straight king run {t·d}. Its image points are collinear, spaced
   s, spanning a bounding box of (n−1)|a|+1 columns × (n−1)|b|+1 rows where
   L(d) = (a,b). Any rook-connected set with p columns and q rows has
   ≥ p + q − 1 cells (contract vertical tree edges: ≥ p−1 horizontal edges;
   symmetrically ≥ q−1 vertical). So the image has ≥ (n−1)s + 1 ≥ 2n − 1
   cells: **β ≥ 2 − 1/n.**
5. **Tight.** Identity embedding plus one orthogonal bridge cell per diagonal
   edge of a spanning tree costs ≤ n + (n−1) cells on every king animal, with
   equality on the staircase. β = 2 exactly.

**K2 verdict (rook-parity.md:86, "diagonal-splice β ≥ 2"):** derived, not
just asserted — and sharpened three ways: (i) the bound is tight, β = 2, so
no splice variant gets below it; (ii) it holds for the *entire*
translation-covariant family, not just identity-plus-bridges — block maps
(β = 4) and shears included; (iii) β = 2 is dead against every post-kink base
reading, since 1.73² = 2.993 > b for b ∈ {1.73, 2.42, ~2.5} (R1-K §1b,
`results/rook1/R1-K.md`). The soft spot the kill leaned on is now load-bearing
masonry. Queue row D1 supersedes K2.

### 3c. What survives, and its exact burden

Only **non-uniform (animal-adaptive) reductions in the corridor
β ∈ [1.40, 1.61], and only under the b = 2.42 reading.** Their burden,
concretely: re-embed each diagonal run cheaply (per-run this is possible — a
shear makes NE runs free) while paying for (a) the *other* diagonal, which the
same shear makes cost 3 (step 3 above: no embedding serves both), (b) every
seam between differently-embedded regions, and (c) recognizability (R2): the
sweep must still decide image membership without exponential extra state. The
alternating NE/SE zigzag at run length ℓ is the canonical hard instance: any
single embedding averages ≥ 2 on it, so an adaptive map must switch at Θ(n/ℓ)
seams whose cost is not established here. I do not exhibit an impossibility
for this family; I state its requirement (R0–R3 with the weave battery) and
note that the only permanent kill available is structural — counting is
exhausted by 3a.

NOT ESTABLISHED: a lower bound above 1.61 for adaptive reductions; the seam
cost of switching embeddings; whether (R2) alone forces state blowup at
β < 2. These are queue rows D3/D4, not claims.

## §4 Negative-map entry

King→rook transport needs no translation of cut states — the Motzkin
vocabulary is literally shared (identical measured state sets, and
non-crossing is derivable for king by the L∞ crossing lemma). What it must
transport is the action and the geometry: every gap-jump merge king gets free
must be bought with bridge cells, and every diagonal run must be re-embedded,
within a budget of β − 1 extra cells per cell where β < 1.61 (b = 2.42) or
β < 1 (b = 1.73). Against that: an unconditional counting floor β ≥ 1.244
rigorous / 1.40 best-estimate on all injective reductions — which already
kills transport outright under the b = 1.73 reading — and a tight β = 2 bound
on the entire translation-covariant family (K2 derived, sharpened), leaving
only animal-adaptive maps in a [1.40, 1.61] corridor that arithmetic can
never close (λ_k needed ≥ 9.36 > certificate 9.3154) and only structural
recognizability arguments could.

## §5 Filed successors

Queue rows D1–D5 in `results/rook1/queue.md`; D2 (family criterion across
target lattices), D3 (R2 as the residual kill route), D4 (hard-instance
battery as a pre-run gate), D5 (signature.h Motzkin compaction) are the
successor rows, different in kind per the queue control.
