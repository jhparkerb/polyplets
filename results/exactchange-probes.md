# Exact Change — probes 1 and 2: the char-2 rank has a closed form; the compression shrinks 100x at cell level; sparsity exists but is not yet constructive

2026-08-14. Continues `results/triangle-r3-involution.md` INV-4 ("an explicit
basis with explicit transitions ... is the entire remaining question of this
row"). Scripts `experiments/tristruct/exactchange_phi_probe.py` and
`exactchange_cell_rank.py`, run on dalby (`~/var/exactchange`), seconds each,
exact GF(2) arithmetic, fail-closed anchors throughout (rank must equal the
banked values; phi must separate accepting states — the latter caught a real
bit-offset bug in the probe on first run).

## 1. The rank sequence is A034299, exactly

The G1 ladder (`r3_inv_rank_probe_h12.log`) finished through H = 12 before
gympie was retired: ranks 6, 15, 27, 58, 112, 229, 453, 912, 1818 at
H = 4..12. All nine points match OEIS **A034299** (alternating sum transform
of A000975) at offset r(H) = a(H−1):

    r(H) = (2^(H+4) − (−1)^H (6H+7) − 9) / 36
    r(H) = 2 r(H−1) + (−1)^(H−1) floor((H+1)/2)
    GF   = 1 / ((1−x²)(1−x−2x²))  — partial sums of Jacobsthal numbers

The 0.44·2^H fit is exactly 4/9 · 2^H asymptotically — a 3² denominator in a
characteristic-2 rank — and the ⌊(H+1)/2⌋ correction has the same shape as
the engine's measured successor fan-out ceil(H/2)+1. The extrapolated
dimension at H = 21 becomes an exact prediction: **r(21) = 932,071**
(A034299's own data, and the closed form).

Match is 9 consecutive terms of a 4-term linear recurrence: identification,
not proof. Nothing below leans on it beyond the measured range.

## 2. Probe 1 — the quotient is not a state-merge

phi(s) (coordinates of state s in the closure basis) is **injective within
every mask class** at H = 4..8: no two partitions of the same column mask are
Hankel-equivalent. All compression is cross-mask linear algebra. Consequently
no key of the form (mask, small local data) parametrizes the quotient —
(mask), (mask, #blocks mod 2), (mask, #blocks) all fail (split counts in the
probe output). Nerode class counts 8, 19, 43, 101, 239 at H = 4..8; no OEIS
match. A greedy pivot basis in canonical state order shows no clean
combinatorial law (order-dependent; mixed contiguous/non-contiguous states).

## 3. Probe 2 — the cell-level rank, and the 10³ becoming 10¹

The column-level minimal automaton needs one r×r matrix per column mask —
2^H − 1 of them, useless. An algorithm must read one cell at a time. The
cell-level functional's GF(2) rank (product presentation, rank is
presentation-independent):

    H          4     5     6     7
    cell rank  32    93    210   516      — vs column rank 6, 15, 27, 58
    ratio      5.3   6.2   7.8   8.9      — growing ~linearly in H

So cell rank ≈ Θ(H · 2^H), extrapolating to **~2×10⁷ at H = 21** — against
the spin engine's reachable 1.3×10⁸ (H-orientation) at the same height. The
column-level compression (~10³ vs partition states) is **~6x** where an
algorithm would actually live. INV-4's conditional pricing ("~10⁶ dimension,
megabytes, laptop hours") implicitly priced column-level transitions that
cannot be stored; the honest compressed dimension is 20x larger.

## 4. Sparsity: the CKN shape exists here, non-constructively

In the pivot basis the closure hands over, the two compressed transition
matrices are **sparse**: average row weight 1.8→3.6 (A₀) and 2.7→5.0 (A₁)
across H = 4..7, ~O(H) growth, against dense ~r/2. Conditional on having the
basis at H = 21: nnz ~ 5×10⁸ (a few GB), wall ~10¹¹ sparse GF(2) ops —
laptop hours. This is the Cygan–Kratsch–Nederlof signature: low rank AND
sparse factorization. **But the basis here is extracted from the
observability closure, which at H = 21 costs more than counting** — the
existence is now measured; the construction (a basis defined a priori, CKN's
actual achievement for matchings) remains entirely open. The A034299
recurrence a(n) = a(n−1) + 2a(n−2) + [n even] is the best scent: it reads
like a height-recursive basis decomposition.

## 5. The prize, re-priced honestly

T(40,20) mod 2 and T(40,21) mod 2 are **already banked** (spin twin runs,
2026-08-13, `results/triangle-salvage.md` §1.2). Exact Change compresses the
same functional in the same characteristic, so it would re-derive an
already-banked bit ~6x cheaper — its residual value is dynamics diversity
against the B1 family, which the salvage file already flags as limited (one
identity, two extractions). The exact value of T(40,21) stays single-sourced
whatever happens here. The construction hunt is mathematically live and
now well-scented, but it is not on any critical path.

## NOT ESTABLISHED (as of probes 1-2; superseded in part below)

- A034299 identification beyond H = 12 (9 terms vs a 4-term recurrence).
- The Θ(H·2^H) cell-rank law (four points; ratio still rising at H = 7).
- Sparsity in any a-priori basis. Measured only in the closure's pivot
  basis, which is not available at production heights.
- Any lower bound forcing sparse transitions to exist at H = 21.

---

# Probes 3-5 (2026-08-14, same day, later): the Nerode layer is solved;
# the rank has a Jacobsthal filtration; adversarial review

Scripts `exactchange_kernel_probe.py`, `exactchange_minauto.py`,
`exactchange_doubling_probe.py`, run on dalby (`~/var/exactchange`).
Adversarial review by a Fable fork with full session context; its findings
are folded in below and listed in §9.

## 6. The Nerode layer is solved, and it is characteristic-free

**Result (proved, one direction; measured exact, the other).**  Two strip
states are GF(2)-Nerode-equivalent iff they have the same multiset of block
neighborhoods N(b) = rows(b) expanded ±1 (clipped to [0,H)).

The "if" direction is a proof, not a fit: the transition rule reads nothing
about a block except N(b) -- a new cell at row r attaches to b iff r ∈ N(b),
and b strands iff the new mask misses N(b) -- so the N-family determines the
successor family and acceptance (|family| = 1), over every field.  The
"only if" direction (no further char-2 merging) is measured EXACT at
H = 4..10, with the class inventories printed and inspected.  All the probe-2
candidate keys (run-collapse, parity, masks) fail; this one does not split a
single class.

Minimized state counts N(H), H = 4..11: 8, 19, 43, 101, 239, 575, 1399,
3441.  Growth ~2.4x/height.  (An A001333/NSW identification was tried on the
early terms and DIED at H = 9-10: 575 vs 577, 1399 vs 1393.  Recorded as a
warning about pattern-matching this table.)

Consequence: the strip DFA's minimal automaton is constructible A PRIORI --
states are N-families, no observability closure needed.  Layer 1 of the
basis hunt (probe 3's framing) is closed.

## 7. The minimized automaton, built a priori

`exactchange_minauto.py` builds the automaton directly on N-families.
Anchors: brute-force counts at H ≤ 3, W ≤ 4 (small -- see §9 item 3);
state counts equal the banked Nerode counts; ranks equal both A034299 AND
the independently-computed partition-automaton ranks at every H ≤ 11
(two-implementation agreement; H = 12 pending, H = 13 would be minauto-only
and needs a second source before it counts).  Fast numpy closure: 23x over
the int-loop version (H = 10 rank in 13 s).

Layer 2 (relations among the N distinct phi values, dim N − r):
- **No weight-3 relations exist at any measured height** -- the distinct phi
  values form a sum-free-like family.  NOT the CKN matchings shape.
- Weight-4 relations exist but do not span (H = 8: 93 of 127; H = 10: 748
  of 946).  CORRECTION per review: the raw weight-4 counts printed by the
  probe are 3x inflated (each 4-set is found once per pairing); span
  dimensions are unaffected.
- A "shadowing" reading of the H = 4/5 quads (rows covered by a companion
  block's neighborhood can be toggled) rests on two distinct quads --
  suggestive, far too thin to call a mechanism.

## 8. Cut-and-count linearization and the Jacobsthal filtration

**Step 1 (derived, NOT yet machine-checked).**  Mod 2, the connectivity
indicator equals the parity of anchored {A,B}-colorings with no AB
king-adjacency (2^(c−1) with c components).  This identity IS the B1 spin
engine's foundation, used here as mathematics.

**Step 2 (derived, NOT yet machine-checked).**  The Hankel matrix factors:
M[F,G] ≡ Σ_{σ: F→{A,B} anchored} Π_j [C_j meets exactly one of U_A(σ),
U_B(σ)], U_X = union of the X-colored neighborhoods.  Rows factor through
spin patterns (U_A, U_B) -- the Z[q]/(q²) colour algebra appears as a rank
factorization, not an engineering choice.  A hand re-derivation by the
review fork found no gap (anchor, empty footprints, U_A∩U_B cases all
close), but the red-first numeric check against the connectivity indicator
has NOT been run.  A claimed self-duality (suffix classes are also
N-families) is asserted, not established.

**The filtration (measured, 7 points each, H = 4..10).**  With V_low =
span{g_w : w avoids the top row} and V_int = span{g_w : w avoids both
boundary rows}:

    dim V_int = 2^(H−2)                  exactly (4, 8, ..., 256)
    dim V_low = (2^H − (−1)^H)/3 = J(H)  Jacobsthal A001045
                                         (5, 11, 21, 43, 85, 171, 341)
    r(H) − dim V_low = r(H−2)            arithmetically

The H = 10 values (341, 256) were predictions stated before the measurement
landed -- the only pre-registered points; the rest are post-hoc fits with
4-5 surplus points each, i.e. NO more numerical surplus than the A034299
match itself (review finding).  The bottom-row variant equals the top-row
variant at every height (symmetry control).

r(H) = J(H) + r(H−2) telescopes to r(H) = Σ_k J(H−2k), which is Paul
Barry's formula on the A034299 entry.  The A000975 gloss ("PSumSIGN of
A000975") is bookkeeping: A000975 = partial sums of Jacobsthal; the
substance, if the filtration is real, is that Jacobsthal appears as the
dimension of the boundary-row-avoiding observability subspace.

**Caveat (review finding 1): the quotient identity is arithmetic, not
structure.**  Only dim V_low is a new measurement; r(H) − dim V_low =
r(H−2) is a subtraction, and no map between the top-row quotient and the
height-(H−2) system has been exhibited.  The proof program is three lemmas:
(L1) dim V_int = 2^(H−2); (L2) dim V_low = J(H); (L3) an explicit
isomorphism V_H / V_low ≅ V_{H−2}-pullback.  None is proved.

## 9. Adversarial review (Fable fork, 2026-08-14)

Ranked findings, all accepted: (1) "three identities" is one measurement
plus arithmetic -- exhibit the quotient map or stop counting it; (2) the
new fits have no more surplus than the doubted A034299 match, and this
table has now eaten three pattern-matches (NSW died, ⌈H/2⌉-doubling died,
Jacobsthal is the third); (3) H = 13 via minauto alone is single-source --
wants a cross-automaton random-word equality test at H = 8..10 and/or a
partition-side pass at 13; (4) the "proved" steps are derived-twice-by-the-
same-author, red-check pending; (5) self-duality asserted only; (6) the 3x
weight-4 count bug (span dims unaffected).  Conceded solid: cut-and-count,
the factorization derivation, the N-family congruence direction, the
seven-height EXACT Nerode match (could not construct a spurious route to
it), the low=bot symmetry control.

Pending settling checks (queued, cheap): numeric red-check of the σ-sum
formula at H = 4/5; cross-automaton random-word test at H = 8..10; the
quotient-subspace comparison for L3.

## 10. What this would NOT give: king-animal counting stays hard

Even if L1-L3 are proved and the layer-2 basis hunt fully succeeds, the
object compressed is the GF(2) rank -- the mod-2 bit of T(n,H), nothing
else.  The mod-p ranks (A-S1: 6, 17, 35, 88, 204, 501, 1217; growth
~2.79x/height) show NO collapse, so exact and odd-prime counting keep
their floor; Coin Lift's exact-value exclusion stands.  And for the mod-2
bit itself the spin engine already runs in the coloring space
(~(1+√2)^H = 2.414^H states), so the ceiling on the whole campaign is a
(2.414/2)^H ≈ 1.21^H factor on one bit -- at H = 21, roughly 55x on a
computation that is already cheap relative to the exact engines.  The
structure is the prize here, not the wall clock.

## Still running / next when resumed

- ~~minauto H = 12 fast-closure confirmation (dalby, in flight)~~ **DONE
  2026-08-14** (dalby run landed, exit 0; brute anchors H=2,3 OK 27/286/1906):

      H   minstates   rank   A034299         (build, rank wall)
      10      1,399    453   453  OK         (4.6 s,   13.2 s)
      11      3,441    912   912  OK         (24.6 s,  152.3 s)
      12      8,539  1,818  1,818 OK         (130.4 s, 1696.3 s)

  The N-family automaton route independently reproduces the G1 ladder's
  three top points, so the A034299 match no longer rests on the retired
  gympie run alone. Rank wall grew ~11.1x from H = 11 to 12; naive
  extrapolation puts the H = 13 rank step at ~5-6 h single-core, matching
  the projection below.
- H = 13 decisive test of A034299's 3643: ~5-6 h single-core projected
  (now calibrated off the measured H = 12 wall), PLUS a second source per
  §9 item 3.  Needs sign-off.
- The three settling checks above; the L1-L3 proof program.
