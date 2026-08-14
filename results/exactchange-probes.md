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

## NOT ESTABLISHED

- A034299 identification beyond H = 12 (9 terms vs a 4-term recurrence).
- The Θ(H·2^H) cell-rank law (four points; ratio still rising at H = 7).
- Sparsity in any a-priori basis. Measured only in the closure's pivot
  basis, which is not available at production heights.
- Any lower bound forcing sparse transitions to exist at H = 21.
