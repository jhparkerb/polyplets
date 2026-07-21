# GF-6 — `Polyplets/Grand/ExpForm.lean` + `Lead.lean`: the abstract grand
# form and the 25^k/k! corollary

Read first: `polyplets/GRANDFORM-PLAN.md`; `Grand/Series.lean`, `Grand/Mu.lean`,
`Grand/Staircase.lean`; `docs/proofs/grand-form.md` (Statement + Step 5 +
Corollaries — you are formalizing its exp-form and corollary 2);
`experiments/staircase_check.py` section 6 (numeric ground truth for W, a, b).
Independent of GF-5 (may run in parallel with it); shares its uniqueness-
induction skeleton, so if PinGrand.lean exists, read it.

## Part A — `ExpForm.lean`

### Definitions

```lean
/-- m_i = μ_i·3^(2i−1) in zpow-free form (m 0 = 1). -/
noncomputable def mSeq : ℕ → ℚ := fun i => mu i * 3 ^ (2 * i) / 3

/-- W: the unique series with W₀ = 1 and 1 = Σ_i m_i·(shift i)(W^{∗(i+1)}) —
the diagonal-Lagrange substitution ŵ = yφ(ŵ) of the paper, resummed. -/
noncomputable def Wc : ℕ → ℚ
  | 0     => 1
  | t + 1 => - ∑ i ∈ Finset.Icc 1 (t + 1), mSeq i *
      convPow (fun s => if s ≤ t then Wc s else 0) (i + 1) (t + 1 - i)
```
(prefix-guard + de-guard lemma exactly as `nu` in GF-2 — the (t+1−i)-th
coefficient of the (i+1)-power reads W only at ≤ t+1−i ≤ t). Export
`W_fixed : ∀ t, eps t = ∑ i ∈ Finset.range (t + 1), mSeq i *
convPow Wc (i + 1) (t - i)` — check the t = 0 case reads `1 = m₀·W₀ = 1`.
(Equivalently `Σ_i mSeq i · (shiftSeq i (convPow Wc (i+1))) = eps` as
functions; state whichever form the GF-1 lemmas consume best.)

```lean
/-- Series log via the derivative recursion t·L_t = t·a_t − Σ_{s<t} s·L_s·a_{t−s}. -/
noncomputable def logSeq (a : ℕ → ℚ) : ℕ → ℚ  -- a 0 = 1 assumed where used
/-- Series exp of a cumulant sequence (c 0 = 0): E_0 = 1,
t·E_t = Σ_{j∈Icc 1 t} j·c_j·E_{t−j}. -/
noncomputable def expSeq (c : ℕ → ℚ) : ℕ → ℚ
/-- Cumulant coefficients: b_j := −(log W)_j; a: level-solved from T. -/
noncomputable def bSeq : ℕ → ℚ := fun j => if j = 0 then 0 else - logSeq Wc j
noncomputable def aSeq : ℕ → ℚ   -- see below
/-- exp of the affine cumulants at a given n. -/
noncomputable def expCoeff (a b : ℕ → ℚ) (k : ℕ) (n : ℚ) : ℚ :=
  expSeq (fun j => a j + b j * n) k
```
`aSeq` by strong recursion (prefix-guard): `aSeq k` := the unique value
making level k match T at its onset point:
`aSeq k := 3^(3k+1) · (T (2k+1) (k+1) : ℚ) / 3^(2k+1)
  − expSeq (fun j => (if j = k then 0 else aSeqPrefix j) + bSeq j·(2k+1)) k`
— since `expSeq c k = c k + (terms in c_{<k})` (prove
`expSeq_top : expSeq c k = c k + <lower-only expression>` or simply that
`expSeq` is (coefficient-wise) `c k` plus a function of `c_{<k}`), this makes
`base_match (k) : 3^(3k+1)·(T (2k+1) (k+1) : ℚ) = expCoeff aSeq bSeq k (2k+1) · 3^(2k+1)`
definitional-by-construction (one unfolding lemma).

### Toolkit lemmas

1. `expSeq_add (c c' : ℕ → ℚ) (h : c 0 = 0) (h' : c' 0 = 0) :
   expSeq (c + c') = conv (expSeq c) (expSeq c')` — induction on the
   coefficient via the derivative recursion (classical; the only genuinely
   fiddly lemma of Part A; write the paper computation out first).
2. `expSeq_logSeq (a) (h : a 0 = 1) : expSeq (fun j => if j = 0 then 0 else logSeq a j) = a`
   — same recursion style. (Gives `expSeq (−bSeq) = Wc` up to sign
   bookkeeping: state as `expSeq_neg_b : expSeq (fun j => -bSeq j) = Wc`.)
3. Affine shift: for i ≥ 0,
   `expCoeff a b k (n − (i+1)) = (conv (expSeq (fun j => a j + b j * n)) (convPow Wc (i+1))) k`
   — from 1 + 2: the cumulant difference is `−(i+1)·b_j`, and
   `expSeq (−(i+1)·b) = convPow Wc (i+1)` (induction on i via `expSeq_add`).
4. **Exp-staircase**:
   `expCoeff a b k (n+1) = Σ_{i ∈ range (k+1)} mSeq i · expCoeff a b (k−i) (n−i)`
   — rewrite each term by 3, pull the common `expSeq (…n+1…)` factor out
   through `sum_conv_collapse`-style reindexing, and finish with `W_fixed`.
   (Set the common reference at n+1: term i's cumulants at `n − i` differ
   from those at `n+1` by `−(i+1)·b`, hence the `(i+1)`-th W-power.)

### Main theorem

```lean
/-- **The grand form, formalized** (unconditional): T's diagonals are the
exp of affine cumulants — 2 new rational constants per level. -/
theorem grand_form : ∀ k H : ℕ, k + 1 ≤ H →
    (3:ℚ)^(3*k+1) * (T (H + k) H : ℚ) = expCoeff aSeq bSeq k ((H:ℚ)+k) * 3^(H+k)
```
Proof: strong induction on k, inner `Nat.le_induction` on H — the SAME
skeleton as GF-5's `P<k>_grand_of_banked` but with `base_match` as the base
(no banked hypotheses!) and the exp-staircase (lemma 4) in place of
`Pstair<k>`. The step's 3-power bookkeeping is identical to GF-5's (copy the
exponent chain from that brief, with `mSeq i` in place of the literal
`μᵢ·3^(2i−1)`). Also export the n-form corollary
`grand_form_prod : ∀ k n, 2*k+1 ≤ n → (T n (n−k) : ℚ) =
expCoeff aSeq bSeq k n * (3:ℚ)^((n:ℤ)−1−3*k)` via the `shape_production`
conversion block.

## Part B — `Lead.lean`

1. `bSeq_one : bSeq 1 = 25` — numeric: `mSeq 1 = mu 1 · 9/3 = 25`
   (via `mu_one`), `Wc 1 = −25`, `logSeq Wc 1 = −25`, so `bSeq 1 = 25`.
   Pure `norm_num` after unfolding. (Unconditional; carries only V_1_1's
   `Lean.ofReduceBool`.)
2. Polynomial view: define `expPoly (a b : ℕ → ℚ) : ℕ → Polynomial ℚ` by the
   same derivative recursion with `C (a j) + C (b j) * X` in place of the
   affine value; lemma `expPoly_eval : (expPoly a b k).eval n = expCoeff a b k n`.
3. `expPoly_natDegree_le : (expPoly a b k).natDegree ≤ k` and
   **`expPoly_coeff_top : (expPoly a b k).coeff k = (b 1)^k / k.factorial`**
   — induction on k via the recursion: the only degree-k contribution to
   `k·E_k` is `1·(b₁X)·E_{k−1}`'s top term (spell the coefficient-extraction
   with `Polynomial.coeff_mul` + the degree bound on lower terms).
4. **`lead_coeff_25 : ∀ k, (expPoly aSeq bSeq k).coeff k = 25^k / k.factorial`**
   and `expPoly_natDegree_eq : (expPoly aSeq bSeq k).natDegree = k`
   (top coefficient ≠ 0 by `norm_num`-positivity of `25^k/k!`).
   Combined with `grand_form_prod` and `shape_production`'s uniqueness
   (a degree-≤k polynomial agreeing with T-diagonals on all n ≥ 2k+1 is
   unique — reuse `Pin.lean`'s `pin` or a small infinite-agreement lemma:
   two polynomials of degree ≤ k equal on the infinite set {n : ℚ | onset}
   are equal, `Polynomial.eq_of_infinite_eval_eq`), conclude the paper's
   Corollary 2: every shape witness has degree exactly k and leading
   coefficient 25^k/k!. State this as
   `shape_lead : ∀ k, ∀ P, P.natDegree ≤ k →
   (∀ n ≥ 2k+1 onset-form) → P.natDegree = k ∧ P.coeff k = 25^k/k!`
   (formulate the middle hypothesis exactly as `shape_production`'s
   conclusion so it composes).
5. Production spot checks (tiny, optional but cheap): for k = 4..16,
   `Pp<k>.coeff k = 25^k / k!` by `norm_num` — ask GF-5's generator to emit
   these into PinGrand.lean instead if coordination is easier; otherwise
   skip and note.

## Pitfalls

- `expSeq`/`logSeq`/`aSeq` recursions all need the prefix-guard trick; write
  ONE helper pattern and reuse. Keep `c 0 = 0` side conditions explicit.
- `mSeq`'s `/3`: keep divisions confined to literals; `field_simp` early in
  numeric lemmas.
- The b-sign conventions bite: fix them against the oracle's values
  (b₁ = 25, b₂ = −209/2) BEFORE proving anything downstream of `bSeq`.
- Statement casts: `expCoeff … ((H:ℚ)+k)` — keep ℚ-arguments explicit;
  never `((H+k : ℕ) : ℚ)` on one side and `(H:ℚ)+k` on the other.

## Done criteria

Green build, no `sorry`; `#print axioms grand_form` = STANDARD ONLY (this
is the headline audit — no native_decide anywhere in its dependency cone);
`#print axioms lead_coeff_25` = standard + `Lean.ofReduceBool`. Gates G5.
Commit `lean-gf: ExpForm — the grand form, unconditional` and
`lean-gf: Lead — 25^k/k! and exact degree`.
