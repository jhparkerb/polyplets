# Toward proving the dm-mirror diagonal law: reconnaissance (2026-07-13)

Goal: prove the paper's last conjectural law — d(S, S+k) quasi-polynomial in
S, period 2, degree k, poles at x = ±1 with multiplicities k+1, k — by the
same walk-plus-clusters program that proved the height-triangle law
(docs/proofs/diagonal-law.md). Enumerator + census:
`experiments/dm_sym_enum.py`.

## Ground truth secured

A brute-force enumerator of diagonal-mirror-symmetric king animals (growth
by symmetric orbits, canonical diagonal translation) reproduces the banked
law exactly for S ≤ 10, k ≤ 2 — d(S,S) = 2, d(S,S+1) = S+6/S+7 from the
onsets, d(S,S+2) = the pinned quadratics, pre-onset deviations included.

## The permutation skeleton (the k=0 structure, now explained)

n = S cells in an exactly-S×S box forces **one cell per row and one per
column** — a permutation matrix σ. King-connectivity forces
|σ(i+1)−σ(i)| = 1 (0 impossible, ≥2 disconnects), and injectivity then
forces global monotonicity: σ strictly increasing (main diagonal) or
strictly decreasing (anti-diagonal). Hence d(S,S) = 2 — a clean proof of
P₀ = 2, and the right frame for everything above it: a general (S+k)-cell
animal is a permutation-with-k-repeats read row by row.

## The two-family dichotomy is FALSE — the family list is monotone phases

Census at k = 1, 2 (S ≤ 10): besides main-spine-decorated and
anti-spine-decorated animals there is a growing third class — main spines
with **anti-diagonal excursions** (direction reversals), e.g.
{(0,0),(1,1),(2,2),(3,3)} + pair {(2,4),(4,2)} at S = 5. This is exactly
the "parity anomaly / additional length-free families" the paper's §dmdiag
recorded as refuting the naive two-ground-state defect gas. The correct
structure hypothesis:

> The row-reading of a sparse symmetric animal decomposes into **monotone
> phases** (maximal runs where the column trend is +1 or −1), separated by
> reversal clusters. Each reversal (and each width-surplus row) costs
> surplus, so an animal at level k has at most f(k) phases; for fixed k the
> catalogue of (phase pattern, decoration types) is finite, each pattern
> contributes a product of two drift chains (one per direction) with free
> lengths, and the mirror symmetry couples the pattern to its reversal.

That shape would deliver quasi-polynomiality with poles at ±1: the two
drifts are period-2 objects (the main-diagonal spine occupies alternate
anti-diagonal slices; the checkerboard color of the diagonal alternates),
and the number of free lengths per pattern caps the pole multiplicities at
the observed k+1, k. The k=3 parity anomaly should fall out of the
reversal-cluster catalogue rather than fight it.

## Program (next session)

1. Formalize the phase decomposition: separation lemma analog — which rows
   are cut rows (single-cell rows with single-cell neighbors?), what is the
   reversal-cluster catalogue at surplus ≤ k.
2. Weight enumeration for reversal/decoration clusters (symmetric-orbit
   variant of `cluster_weight_dp.py` — count relative to the two contact
   spine directions).
3. Exact chain identity vs the enumerator (the 40/40 analog), including
   the exact-box boundary factors (box-exactness = the analogue of the
   touch flags; onset S ≥ 2k+2/2k+3 should emerge as the correction
   degree, parity split from the drift period).
4. Partial fractions in the two-drift variable → the law, replacing the
   paper's §dmdiag conjecture and retiring the T3 caveat.

Open risk: the anti-family in row-reading is a globally-decreasing chain of
the SAME kind, so it should be symmetric-in-treatment; hybrids (V shapes)
are where the catalogue could in principle grow with S — the census says
reversals cost ≥ 1 surplus each (V count grows only linearly), which is the
lemma to prove first.


## STEP 1 COMPLETE (2026-07-15): the phase lemma, proved and tight

**Lemma (reversal cost).** A dm-symmetric animal with box exactly SxS and
S+k cells has at most 2k strict direction reversals in its row-min (and
row-max) sequence -- hence at most 2k+1 monotone phases.

*Proof.* Within a maximal stretch of single-cell rows, consecutive cells
must king-touch, so the cell position moves by {-1, 0, +1} per step. A
reversal inside a stretch immediately revisits a column (the step after
the turn returns to the previous value), costing >= 1 column surplus; a
0-step costs the same. Reversals at multi-cell rows are bounded by the
number of multi-cell rows, i.e. by row surplus. By mirror symmetry the row
and column surplus pools each hold exactly k: total <= 2k. QED
(Tight: max runs observed = 1, 3, 5, 7 at k = 0..3.)

**Grammar validated.** Each phase class (k, runs) is SEPARATELY
per-parity quasi-polynomial of degree <= k from S >= 2k+2, and the classes
partition d(S,S+k) (k <= 2, S <= 13, `experiments/dm_phase_census.py`).
The decomposition is therefore the right chain grammar; e.g. at k=1 the
three classes are (runs=1) the linear-in-S near-spine class, (runs=2)
constant 4, (runs=3) the parity-oscillating 2/4 class -- summing to the
known S+6/S+7.

Remaining (steps 2-4): per-class chain weights, the exact-box boundary
factors, and partial fractions with the (1-x)(1+x) pole bookkeeping.
The involution frame (symmetric permutation = involution; main family =
involutions near identity, anti family = involutions near the reversal,
paired into half-length chains -- the origin of period 2) is the working
frame for step 2.
