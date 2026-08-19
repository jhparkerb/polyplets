# Proof audit of the L papers, 2026-08-18

Companion to `docs/priority-passes-2026-08-18.md`. That pass asked "is it
new?"; this one asks "is it right?". The prompt for it is L3, whose
Proposition 6 carried a proof that was **false** and survived a five-phase trim
campaign, an LLM-tic sweep and a coinage sweep, because all three read prose
rather than arguments.

Method: for each load-bearing proved claim, re-derive the step that could
silently fail (injectivity of an encoding, exhaustiveness of a case split,
a threshold, a hidden hypothesis), and where a brute force is cheap, check the
claim against enumerated data with controls that must fire.

## Findings

### L9 — a real defect in the paper's rendering of its own proof. FIXED.

The paper wrote the final step as a product over component minima,
`sum_phi w(phi) = prod_i (b_i + (q - b_i)) = q^m`. That is wrong as written:
`b_phi(v_i)` depends on the choices made at `v_1..v_{i-1}`, so there is no fixed
`b_i` to multiply, and the source proof in `docs/proofs/cutcount-identity.md`
uses downward induction on a history precisely for that reason. The conclusion
is unaffected — `b` cancels whatever it was — but the argument as printed did
not establish it. Replaced by the induction, with the history dependence stated
rather than papered over.

Class of error: a compression that silently converts a history-dependent sum
into a product. Same family as L3's — a step that reads as bookkeeping and is
not.

### L3 — the repaired proof re-derived independently here. HOLDS.

The BFS-frame encoding's arithmetic was re-checked from scratch rather than
transcribed. For `u` with parent `d`, the shared set `N(u) ∩ N(d)` has
**4 cells for orthogonal `d`** (e.g. `u=(0,0)`, `d=(1,0)`: the shared cells are
`(0,±1)` and `(1,±1)`) and **2 for diagonal `d`** (`u=(0,0)`, `d=(1,1)`: `(0,1)`
and `(1,0)`), so frames carry `8-1-4 = 3` or `8-1-2 = 5` slots as the proof
says. Bounding every frame by the 5-slot alphabet `(1+x)^5` is a valid
over-count, and the root's 8-slot frame is one constant factor. The injectivity
that the broken proof lacked is supplied by the replay decoder and is
machine-verified over every animal with `n <= 8`.

### L7 — Lemma T checked against enumerated data. HOLDS, with the slack measured.

`experiments/l7_lemma_audit.py`, run on dalby against the two independent block
oracles (DFS and DP agree through `n = 16`), and the per-`h` split verified to
sum back to `T(n)` exactly:

| step | statement | verdict |
|---|---|---|
| (i) | `T(n) >= 2T(n-1)` | holds, `n <= 16` |
| (ii) | `T_h(n) <= 2T(n-h)` | holds |
| (iii) | `T_h(n) <= T_1(n + h(h-1)/2)` | holds |
| (iv) | `T_1(i)T_1(j) <= T_1(i+j)` | holds |
| (v) | `T(n) <= 4 max_{h<=3} T_h(n)` | holds |
| (vi) | `T(n) <= 4T_1(n+3)` | holds |

**And the checks' bite, measured rather than assumed**: `min T(n)/T(n-1) =
2.515` against the required 2; `min T_1(i+j)/(T_1(i)T_1(j)) = 2.000` against the
required 1; `max T(n)/T_1(n+3) = 0.119` against the allowed 4. So (i) and (iv)
are tested with a factor of ~2 to spare and (vi) with a factor of 34 — these
confirm the steps against gross mis-statement, not their constants. Two of the
five RED controls did not fire, which is reported in the script's own output as
marking a check with no bite rather than being quietly dropped.

### L5 / L7 — the phase decomposition and the mirror equality. HOLDS, and one implicit claim confirmed.

Enumerating unrestricted HV-convex polyplets by phase path to `n = 13`:

- **No animal visits both middle phases.** The "visited both" class is
  identically zero through `n = 13`, which is what the phase-bit monotonicity
  implies and which both papers use without stating. So the decomposition is
  exactly `total = via(1,0) + via(0,1) + neither`.
- **The mirror equality `A_(1,0)(n) = A_(0,1)(n)` holds termwise** for every
  `n <= 13` (at `n = 13`: `1333383` each, of `2677214`). This is the claim
  carrying the standing Gouyou-Beauchamps–Leroux attribution.
- **The remainder is small and its growth is falling**: `1, 2, 4, 9, 21, 50,
  118, 270, 598, 1280, 2652, 5335, 10448`, successive ratios declining
  `2.381 -> 1.958` over `n = 6..13`, and `0.39%` of the class at `n = 13`.
  Consistent with the sub-exponential stack bound, and too short to be decisive
  on its own — the bound is what proves it, and this is a check that the bound
  is not contradicted.

### Not audited this round

L1 (Theorem A is Lean-formalized, axiom footprint recorded), L2 (theorems are
explicitly conditional on congruences verified to `k <= 17`), L4 (unchanged
since its own sweep), L6 (the k=6 claims were re-derived from census data in
`paper/verify_l_papers.py` this week), L8 (every statement is already labelled
derived, measured or assumed, with four named assumptions).

## Round 2, 2026-08-19 — the papers round 1 skipped

Round 1 audited L3, L5, L7 and L9 and left L1, L2, L4, L6 and L8 alone. L4's
stated reason was "unchanged since its own sweep", and a sweep reads prose.

### L4 — the coefficient-extraction recurrence was mis-indexed. FIXED.

Theorem 6 (dichotomy) wrote the extracted recurrence as

    sum_{delta <= sigma} c_delta(x,H) G_{H-delta}(x) = 0

with no lower bound on `delta`, and then argued at `x = 1/mu_{H_0}`: "every term
with `delta >= 1` refers to a height below `H_0` ... the `delta = 0` term has
`G_{H_0}`, which has a genuine pole there."

Extraction does not produce that shape. With `p_i = sum_j p_ij(x) y^j`, the
coefficient of `y^H` in `p_i d_y^i F` sits at height `H + i - j`, so **height
indices above `H` occur whenever `i > j`**. The smallest counterexample is the
operator `d_y F = 0`: extraction gives `(H+1) G_{H+1} = 0`, a single term at
height `H+1`, and no term of height `H` at all. The proof's leading face is then
not present, and the terms it treats as bounded near `1/mu_{H_0}` include slices
of *greater* height, whose radius of convergence is strictly **smaller** — they
are not merely unbounded there, their series do not converge.

The conclusion survives. The repair is to run the argument on the top face
rather than on the `delta = 0` face: put `m := max{i - j : p_ij != 0} <= r` and
let `c(x,H)` be the coefficient of the highest slice `G_{H+m}`. Instancing at
`H = H_0 - m` (legal for `H_0 >= r`) puts `G_{H_0}` on top with every other term
strictly below it, and the rest goes through as printed. Two things improve:

- `c != 0` holds **by construction** — `m` is chosen so some `p_{i,i-m}`
  survives, and the falling factorials `(H+m)_(i)` have distinct degrees in `H`.
  So deriving `c == 0` is already the contradiction and the old proof's
  recursion through `delta = 1, 2, ...` is not needed. The proof is shorter.
- The theorem's conclusion picks up `H >= r`: at most `r` exceptional heights
  among `H >= r`. **Both effective tables survive this unchanged** — re-checked
  cell by cell against the psi-degrees `1,2,4,9,29,68,181,462,1254,3289`, every
  box still has its `r+1` certified levels with `H >= r`.

Class of error: an index range asserted rather than computed. Same family as
L3's and L9's — a step that reads as bookkeeping and is not.

### L4 §"Boxes from monotonicity and irreducibility alone" — overclaim. FIXED.

"The psi-construction needs the banked `G_H`. A second family of boxes rests
only on Lemma 4 plus irreducibility certificates, and so is self-contained."
Both families read `psi_H` off the banked `G_H`; that is where `psi_H` comes
from. The second needs *more*, not less: irreducibility certificates on top of
the same data, which is why its table is the weaker of the two. Retitled and
restated to say what actually separates them — the first extends the theorem to
all roots of `psi_{H_0}`, the second uses it at the dominant root only.

### L4 — the rest. HOLDS.

- Lemma 3 (`mu_H` an algebraic integer, house `= mu_H`). Fatou gives `Q_H(0) =
  1`; the reversal is monic and integral; in lowest terms every root of `Q_H` is
  a pole, so every root of the reversal has modulus at most `mu_H`, and the
  minimal polynomial of `mu_H` divides the reversal, so the conjugates are among
  them. Holds.
- Lemma 4 (strict monotonicity). The Perron-root half is standard. The
  compressed last sentence — "exact-height counts are second differences of
  strip counts, strictness rules out cancellation" — checks out: `G_H = C_H - 2
  C_{H-1} + C_{H-2}` with `nu_H > nu_{H-1} > nu_{H-2}`, so the pole at
  `1/nu_H` is not cancelled and nothing of smaller modulus is singular.
- Lemma 5 (Northcott) and the exclusion-box arithmetic in both tables. Holds.

### L2 — the unconditional half. HOLDS.

Proposition 1 (Polya integrality): the window `[2k+1, 3k+1]` is exactly `k+1`
consecutive integers, and on it `3^{3k+1-n}` has a nonnegative exponent while
L1's Theorem A is in force (`n >= 2k+1`) — the two ranges meet exactly, which is
the part that could have failed. Proposition 2 needs `P_0(0) = 1`, and `P_0` is
the constant polynomial because `T(n,n) = b^{n-1}` counts walks. Both hold. The
mod-3 theorems are stated conditionally on congruences checked to `k <= 17` and
were not re-derived here.

### Still not audited

L1 (Theorem A is Lean-formalized; Theorems B and C are not, and their proofs
were not re-derived this round), L6, L8.

## The pattern worth keeping

Both defects found in two days — L3's false proof and L9's false factorisation —
are *steps that look like bookkeeping*. Neither is a deep error and neither
changes a stated result. Prose-level review passes do not catch them, and
neither does numerical agreement, because both papers' numbers were right. What
catches them is re-deriving the step.
