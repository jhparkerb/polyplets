# Plan: Efficient Symmetric Enumerator (S2 phase 2)

*Drafted June 13, 2026. Supersedes the sketch in
`docs-s2-symmetric-enumerator.md`. Builds on the validated S2 Burnside
foundation (`oracle/g1_naive.py` count_symmetry, `tests/gate_s2.py`). Same
discipline as the rest of the project: separable components, oracle-anchored
gates, results submittable only against external truth.*

## 1. Goal and HONEST scope

Compute the four symmetry-invariant fixed-polyplet counts efficiently to
n ≥ 19 (and well beyond — they are cheap):

    R90(n) = #{fixed polyplets invariant under a 90° rotation}
    R180(n) = #{... under a 180° rotation}
    H(n)   = #{... under an axis-parallel mirror}
    D(n)   = #{... under a diagonal mirror}

These feed two things:

**(a) Deliverable — new OEIS terms.** With Fixed(n) from G2, Burnside gives
free polyplets A030222 (stuck at n=17 since 2002) and one-sided polyplets (no
OEIS sequence exists yet), plus the eight symmetry-class sequences (none exist
for polyplets). Free(18) is already a new term; Free(19) lands when the a(19)
campaign verifies.

**(b) Cross-check on Fixed(19) — and exactly how strong it is.** Burnside is
*one* equation:

    Free(n) = (1/8)[ Fixed(n) + 2 R90(n) + R180(n) + 2 H(n) + 2 D(n) ]

With the symmetric counts computed independently (different algorithm, this
plan) and Free(n) forced to be a non-negative integer, this pins **Fixed(19)
modulo 8** — likewise mod 4 from the one-sided identity. That is a genuine
*algorithm-independent* check (the symmetric counts come from a different code
path than G2's Redelmeier walk), and it catches ~7/8 of additive errors,
including the kind of ~5% incomplete-campaign deficit the recent review
worried about. **It is NOT a full re-computation of Fixed(19).** Burnside
cannot do better than a congruence from a single new Fixed value, because the
equation has two unknowns (Free and Fixed) and Free has no independent source
at n=19.

**The complementary FULL check** — an algorithm-independent *equality* on
Fixed(19) — is the square-8 TMA reaching n=19 (separate, larger effort:
pruning + the state-growth question), or campaign B run with a structurally
different generator rather than just a different split. This plan does not
replace that; it provides the cheap partial check now and the free-count
science regardless. Both should be stated plainly when a(19) is submitted.

## 2. Method: the orbit-graph reduction

A g-symmetric animal is a union of ⟨g⟩-orbits of cells. Claim (proved in
`docs-s2-symmetric-enumerator.md`): g-symmetric animals of size n correspond
one-to-one with **connected weighted subgraphs of total weight n in the orbit
graph**, where

- nodes = ⟨g⟩-orbits of cells (within a bounded region big enough for size-n
  animals),
- node weight = orbit size (1 on the fixed cell/axis, 2 for a mirror or 180°
  pair, 4 for a 90° quadruple),
- edges = king-adjacency between any cell of one orbit and any cell of another
  (this is where cross-center / cross-axis adjacencies enter — the careful
  part).

The symmetry element is pinned at a canonical location (center at the origin /
axis through the origin), which removes translation freedom, so each symmetric
translation-class is counted exactly once. Counting connected weighted
subgraphs by total weight is **Redelmeier on a finite weighted graph**,
anchored by the minimum-index node to count each subgraph once.

Each symmetry splits into *placements* (Mason's nomenclature), each a distinct
orbit graph; the total for a symmetry is their sum:

| Quantity | Placements (center/axis position) | weights present |
|---|---|---|
| R90 | center on cell (R90C); center on vertex (R90V) | 1 (cell only), 4 |
| R180 | cell (R180C); edge-midpoint (R180M); vertex (R180V) | 1 (cell only), 2 |
| H | axis through cell row (H_cell); axis between rows (H_edge) | 1 (axis cells), 2 |
| D | diagonal through cells (D_cell); diagonal off cells (D_edge) | 1, 2 |

We do **not** need to get this taxonomy perfectly a priori: the per-symmetry
sum is validated against the oracle's Fix(g) at small n (§4), so a missing or
spurious placement shows up immediately as a mismatch. The taxonomy is a
starting hypothesis the gate audits.

## 3. Components and contracts

**E1 `subgraph_count` — weighted connected-subgraph counter (generic).**
Input: a finite graph (adjacency lists) with per-node integer weights, and
maxn. Output: counts[w] = number of connected node-subsets with total weight
exactly w, for w ≤ maxn, each subset counted once (min-index-node anchoring,
grow only to higher-index nodes — the finite-graph analogue of Redelmeier's
half-plane rule). *Test:* hand-computed tiny graphs (path, cycle, star,
weighted triangle); a weight-1 grid patch must reproduce small polyplet/
polyomino counts when handed the plain king/edge graph. *Replaceable:* pure
graph algorithm, no geometry. C++ for speed, but counts are √-rare so even
modest speed suffices.

**E2 `orbit_graph` — per-(symmetry, placement) graph builders.** Geometry
only: enumerate orbit representatives in a bounded region, assign weights,
compute king-adjacency edges *including the cross-center/cross-axis ones*.
One small builder per placement in the §2 table. *Test:* for each builder, the
orbit structure round-trips (every cell maps to exactly one rep; applying g to
a rep's cells stays within the region or is correctly clipped); adjacency is
symmetric. The real test is E-gate §4. *Replaceable:* each placement is
independent; a wrong one is caught by the oracle gate and fixed in isolation.

**E3 `burnside_assemble` — free/one-sided + congruence check.** Combines
Fixed(n) (from a b-file or a campaign results.txt) with the four symmetric
counts to produce Free(n), One-sided(n), and the mod-8 / mod-4 residue checks.
*Test:* reproduces A030222 (free) on the overlap range; integer-ness of every
output. Reuses/mirrors the Python Burnside already in `count_symmetry`.

**E4 `gate_s2b` — the validation gate.** Wires E1+E2+E3 against external and
oracle truth (§4).

Language: E1/E2 in C++ (boring dialect) for headroom to large n; E3/E4 in
Python (analysis layer, reuses common.py and the b-files). The C++ emits
per-symmetry, per-placement counts; Python assembles and audits.

## 4. Validation chain (oracle-anchored, no self-reference)

1. **E1 unit**: tiny hand-graphs with known connected-subgraph counts.
2. **Per-symmetry vs the brute oracle**: the efficient R90/R180/H/D totals
   must equal `count_symmetry`'s Fix(r90)/Fix(r180)/Fix(h)/Fix(d1) for every n
   the oracle reaches (n ≤ ~10–11, where the oracle generates all fixed
   animals). This independently checks both E1 and the E2 placement taxonomy
   — if a placement is missing, the sum is short and the gate goes red.
3. **Per-placement vs an extended oracle**: extend `count_symmetry` to also
   classify each symmetric animal by the lattice position of its center/axis
   (cell / edge / vertex), giving per-placement ground truth — so a wrong
   single builder is localized, not just the sum.
4. **Free count vs A030222**: Burnside(known-Fixed from b006770, efficient
   symmetric counts) must equal A030222 for all n ≤ 17 (the external anchor),
   and the oracle's free count for n ≤ ~10. This validates E3 and the whole
   chain on real data, far past where the oracle alone reaches.
5. **Internal Burnside consistency**: Free and One-sided integer-valued; the
   conjugacy equalities already in gate_s2.

Only after 1–5 are green is the n=19 congruence check trustworthy.

## 5. Milestones

| # | Milestone | Exit criterion | Yield |
|---|---|---|---|
| E0 | E1 weighted subgraph counter | tiny-graph unit tests; plain king graph reproduces small Fixed | — |
| E1 | R180 placements (simplest: weights 1,2) | R180 total == oracle Fix(r180), n ≤ 10; per-placement vs extended oracle | — |
| E2 | H and D placements (mirrors) | totals == oracle Fix(h), Fix(d1), n ≤ 10 | — |
| E3 | R90 placements (weight-4 quadruples) | R90 total == oracle Fix(r90), n ≤ 10 | — |
| E4 | Burnside assembly + A030222 | Free == A030222, n ≤ 17; one-sided integer | **all four symmetric counts to n ≥ 19 cheaply** |
| E5 | Free/one-sided/symmetry-class b-files | extend to the Fixed limit; package for OEIS | **A030222 + new sequences (SUBMIT #2)** |
| E6 | a(19) congruence cross-check | Fixed(19) ≡ −(2R90+R180+2H+2D) (mod 8) holds | partial independent check on a(19) |

E0–E4 are workstation-minutes (symmetric counts ~2.6^n: R180(19) ~ 10^7).
Nothing here is compute-bound; the work is correctness of the builders.

## 6. The a(19) cross-check protocol (when the campaign verifies)

1. Run `audit_results.py` (b-file overlap + ratio) on the verified
   results.txt — already built.
2. Compute the four symmetric counts at n=19 (this enumerator), each validated
   to n=17 against A030222 via E4.
3. Check the congruence: Fixed(19) ≡ −(2 R90(19) + R180(19) + 2 H(19) +
   2 D(19)) (mod 8), and the mod-4 one-sided analogue.
4. Compute and record Free(19), One-sided(19) (new terms, contingent on the
   verified Fixed(19)).
5. State in the submission, plainly: a(19) rests on (i) dual independent-split
   campaigns + merge completeness gate, (ii) external b-file audit on n ≤ 18,
   (iii) this mod-8 algorithm-independent congruence — and that a full
   algorithm-independent equality (TMA at n=19) is future work, not yet done.

## 7. Limitations / complementary work (state honestly at submission)

- The congruence is mod 8, not a full re-computation. Quantify: catches all
  but a 1/8 measure of additive errors.
- The strongest independent equality check on Fixed(19) is the square-8 TMA
  reaching n=19 (needs pruning + the state-growth-base measurement, S1), or a
  campaign B built on a structurally different generator. Either is a separate
  plan; this one does not substitute for it.
- This enumerator's own trust rests on the oracle (n ≤ ~10) and A030222
  (n ≤ 17); both are external. Good to n=17; the n=18,19 symmetric counts are
  extrapolated only in the sense that the *algorithm* is fixed and validated —
  same standing as any validated engine past its last cross-checkable term.

## 8. Immediate first step

E0: the weighted connected-subgraph counter with tiny-graph unit tests, then
feed it the plain n×n king graph and confirm it reproduces A006770's small
terms (a sanity check that the generic counter + a trivial "all weight 1, no
symmetry" graph agrees with the existing engines before any orbit geometry is
added).
