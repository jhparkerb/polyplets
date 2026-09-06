# Proof: T(n, n−1) = (25n − 45)·3^(n−4)

T(n,H) = number of **fixed** king-move animals (polyplets) of n cells whose
bounding box has height **exactly** H. Here we prove the closed form for the
first sub-diagonal, H = n−1, used by `contributePoleHeight` (commit C1). Valid
for n ≥ 4; n = 3 is a boundary case (T(3,2)=10, which the formula also gives via
3^(n−4)=3^(−1)).

## 1. Structure: one doubled row

Height exactly n−1 with n cells means all n−1 rows are occupied (≥1 cell each),
and n cells in n−1 rows forces **exactly one row to hold 2 cells** (the "double
row"); the other n−2 rows hold 1 cell each.

## 2. Connectivity is a consecutive-row condition

King-adjacency spans only ±1 row. Since every row is occupied, the animal is
connected **iff every consecutive pair of rows (r, r+1) shares at least one
king-adjacent cross-pair.** (If some pair does not, the set splits there; all
rows being occupied, there is no way to bridge across a missing link.)

## 3. The doubled row's two cells are at column-gap 1 or 2

Let the double row's cells sit at columns c and c+g, g ≥ 1.

- **g = 1** (domino, c and c+1): mutually adjacent. ✓
- **g = 2** (c and c+2): not mutually adjacent. They join **only** through a
  "bridge" — a cell at column c+1 in an adjacent row, which is king-adjacent to
  both. ✓ exactly when a neighbor row's single cell is at c+1.
- **g ≥ 3**: no single neighbor cell is within 1 of both, and the two would-be
  components (below ∪ {c} vs. above ∪ {c+g}) share no joining edge. **Impossible.**

*Proof of the g≥3 impossibility / g=2 bridge:* the cell at c connects only to
neighbor cells in columns {c−1,c,c+1}; the cell at c+g only to {c+g−1,c+g,c+g+1}.
For both to be non-isolated and in one component, some neighbor cell must be
adjacent to both — possible iff those two intervals overlap, i.e. g ≤ 2, and for
g = 2 the unique common column is c+1.

## 4. Count via the offset chain

Fix horizontal translation (set the bottom row's reference column to 0). The
animal is then determined by the sequence of **relative offsets** between
consecutive rows, and — because the only constraints are the per-pair
connectivity conditions (no overlap issues: distinct rows never coincide) — the
total count is a **product** over transitions, summed over the doubled row's
position and gap.

- A **single→single** transition has offset ∈ {−1, 0, +1}: **3** choices.
- The doubled row + its neighbor transition(s) form a **gadget**; the remaining
  transitions are a free 3-chain. Of the n−2 total transitions, the gadget
  consumes 2 (if the double row is interior) or 1 (if it is a boundary row).

**Gadget multiplicities** (single neighbor must be king-adjacent to the pair; for
g=2 at least one neighbor sits on the bridge column c+1):

| | interior (2 sides) | boundary (1 side) |
|---|---|---|
| **g = 1** (domino) | 4 × 4 = **16** | **4** |
| **g = 2** (split + bridge) | 5² − 4² = **9** | **1** |

- *g=1 side:* the single neighbor ∈ {c−1, c, c+1, c+2} → 4 offsets.
- *g=2 interior:* each side ∈ {c−1,…,c+3} = 5 offsets, minus the 4×4 with neither
  side on the bridge → 9.
- *g=2 boundary:* the lone neighbor is forced onto c+1 → 1.

## 5. Sum over position and gap

Double-row positions: **n−3 interior** rows, **2 boundary** rows. Free
single→single transitions contribute 3^(n−4) (interior) or 3^(n−3)=3·3^(n−4)
(boundary):

$$
T(n,n{-}1) = \underbrace{(16+9)(n{-}3)}_{\text{interior, }g=1,2}\,3^{n-4}
\;+\; \underbrace{(4+1)\cdot 2\cdot 3}_{\text{boundary, }g=1,2}\,3^{n-4}
= \big[25(n{-}3) + 30\big]\,3^{n-4} = (25n - 45)\,3^{n-4}. \qquad\blacksquare
$$

## 6. Checks

- n=3: (75−45)·3^(−1) = 10 = T(3,2). ✓
- n=4: 55·1 = 55 = T(4,3). ✓  n=5: 80·3 = 240 = T(5,4). ✓  n=8: 155·81 = 12555 = T(8,7). ✓
- n=21: 480·3^17 = 61,987,278,240 = T(21,20) (the dalby a(21) `h20.out` value). ✓
- `TestPoleHeightFormula` pins it; `ns-gate-closedform` runs it on every change.

## 7. Why the form, and the road to T(n, n−k)

The doubling is a **single bounded-width defect** on an otherwise-free 3-chain, so
the answer is necessarily (linear in n)·3^(n−4). The two contributing gap-types
(domino 16, split 9) sum to the leading 25 = 16+9.

For the next diagonal, height n−2 carries **2 excess cells** → either one triple
row or two double rows — a **two-defect** version of the same argument, which
must give (quadratic in n)·3^(n−7). Empirically (fitted exact, n=5..20):
`T(n,n−2) = ½(625 n² − 2459 n + 1134)·3^(n−7)`, leading coefficient 625/2 = 25²/2!.
The diagonal leading coefficients run 1, 25, 25²/2! = **25^k/k!**, with power
3^(n−1−3k) — i.e. `T(n,n−k) ~ 3^(n−1)·(25n/27)^k / k!`, a Poisson/defect-gas
structure. The general T(n,n−k) is the open target this method is meant to reach.

## Formalization and supersession (2026-07-21)

This proof is fully formalized in Lean 4: `polyplets/Polyplets/Diagonal.lean`
re-proves `T_n_nm1` from `Pin.lean`'s `P1_closed`, with the gadget
multiplicities 16+9 / 4+1 of §4 as the `native_decide` weight leaves
V(1,1) = 25, Vᵗ(1,1) = 5 of `Weights.lean` (the same 25 = 16+9 split).

§7's road map is CLOSED, beyond what this method was meant to reach:

- T(n,n−2) is no longer "fitted" — the quadratic is proved
  (`P2_closed`, and `T_n_nm2` in `Diagonal.lean`).
- The general shape T(n,n−k) = P_k(n)·3^(n−1−3k), deg P_k ≤ k, onset
  n ≥ 2k+1, is a theorem for ALL k (`Shape.lean`; paper proof
  `diagonal-law.md`), and the defect-gas structure is exact: the
  diagonals are the exp of affine cumulants (`grand-form.md`,
  Lean `Grand/ExpForm.lean`, standard axioms only).
- The Poisson leading coefficient is proved: deg P_k = k exactly and
  [n^k]P_k = 25^k/k! for all k (`Grand/Lead.lean`, standard axioms +
  the single V(1,1) leaf — the 25 of this file's §5).
- Production P_1..P_18 are pinned for all n ≥ 2k+1 (`Grand/PinGrand.lean`):
  k ≤ 3 outright, k = 4..18 as conditional theorems whose explicit
  hypotheses are the two real-swept onset cells per level — engine values
  assumed, not proved in Lean (levels ≥ 12 single-algorithm; see
  `docs/lean-record.md`). k = 19, the engine's last wired
  diagonal, is deliberately excluded: fitted-no-holdout, load-bearing for
  no banked term.

Status ledger: `polyplets/PROOF-STATUS.md`.
