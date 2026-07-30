# OW-4 "Factorial Residue" — `Polyplets/IntCoeff.lean`: k!·P_k ∈ ℤ[X]

Read first: `polyplets/OUTWORKS-PLAN.md`; `Polyplets/Shape.lean` — the
statements you build on (quoted here from the tree, do not re-derive):

```lean
theorem shape_production (k : ℕ) : ∃ P : Polynomial ℚ, P.natDegree ≤ k ∧
    (∀ n : ℕ, 2 * k + 1 ≤ n →
      (T n (n - k) : ℚ) = P.eval (n : ℚ) * (3 : ℚ) ^ ((n : ℤ) - 1 - 3 * k)) ∧
    (∀ n : ℕ, 2 * k + 1 ≤ n →
      (3 : ℚ) ^ (3 * k + 1) * (T n (n - k) : ℚ) = P.eval (n : ℚ) * 3 ^ n)

theorem production_int_all {k : ℕ} {P : Polynomial ℚ} (hdeg : P.natDegree ≤ k)
    (hP : ∀ n : ℕ, 2 * k + 1 ≤ n →
      (3 : ℚ) ^ (3 * k + 1) * (T n (n - k) : ℚ) = P.eval (n : ℚ) * 3 ^ n) :
    ∀ m : ℤ, ∃ z : ℤ, P.eval (m : ℚ) = (z : ℚ)
```

Also read `production_int_all`'s PROOF (Shape.lean:461 ff., built on
`production_int_onset` via finite differences) — reuse any difference
operator / Vandermonde helper it already sets up rather than duplicating.
Size S. New file `Polyplets/IntCoeff.lean` (keep `Shape.lean`'s guarded
axiom footprint untouched).

The paper (§6.1) states "P_k times k! must be integral". The Lean tree has
integer-VALUEDNESS (`production_int_all`); the missing residue is the
classical statement: a polynomial of degree ≤ k that is integer-valued on ℤ
has, after multiplication by k!, integer COEFFICIENTS.

**Mathlib status (checked in the pinned tree):** there is NO integer-valued
polynomial API — no binomial-basis theorem (`RingTheory/Binomial.lean` is
binomial *rings*; the Elliott integer-valued connection is a TODO in its
header). `descPochhammer` exists (`RingTheory/Polynomial/Pochhammer.lean`,
`descPochhammer ℚ j`, with `descPochhammer_eval_cast`,
`descPochhammer_eval_eq_descFactorial`). Build the small amount needed here.

## Deliverables

```lean
/-- Generic: a ℚ-polynomial of degree ≤ k that is integer-valued on ℤ has
k!·coefficients in ℤ. -/
theorem factorial_smul_int_coeff {k : ℕ} {P : Polynomial ℚ}
    (hdeg : P.natDegree ≤ k)
    (hval : ∀ m : ℤ, ∃ z : ℤ, P.eval (m : ℚ) = (z : ℚ)) :
    ∃ Q : Polynomial ℤ, (k.factorial : ℚ) • P = Q.map (Int.castRingHom ℚ)

/-- Applied: every shape witness of level k has k!·P ∈ ℤ[X]. -/
theorem production_factorial_int (k : ℕ) :
    ∃ P : Polynomial ℚ, P.natDegree ≤ k ∧
      (∀ n : ℕ, 2 * k + 1 ≤ n →
        (3 : ℚ) ^ (3 * k + 1) * (T n (n - k) : ℚ) = P.eval (n : ℚ) * 3 ^ n) ∧
      ∃ Q : Polynomial ℤ, (k.factorial : ℚ) • P = Q.map (Int.castRingHom ℚ)
```

(The applied form re-packages `shape_production`'s witness — same P, one
more conjunct; downstream text can then cite one theorem.)

## Proof route (binomial basis, explicit)

1. `binomQ (j : ℕ) : Polynomial ℚ := (j.factorial : ℚ)⁻¹ • descPochhammer ℚ j`
   — the polynomial `C(X, j)`. Facts: `natDegree = j` (from
   `descPochhammer`'s degree lemma — grep `natDegree_descPochhammer`),
   leading coeff `(j.factorial)⁻¹`, and evaluation
   `binomQ j |>.eval (m : ℚ) = (m.toNat.choose j : ℚ)`-style integrality:
   for EVERY `m : ℤ`, `∃ z : ℤ, eval = z` (for m ≥ 0 it is `Int.choose`-like
   via `descPochhammer_eval_cast` + descFactorial; for m < 0 the value is
   `(−1)^j C(j−1−m, j)` — don't chase the closed form, just prove
   "product of j consecutive integers is divisible by j!":
   `Int.factorial_dvd_descFactorial`-flavoured. Search Mathlib for
   `Int.factorial_dvd` / `descFactorial` divisibility; if absent for ℤ,
   derive from the ℕ statement by the two-sign case split).
2. **Expansion**: every `P` with `natDegree ≤ k` is a ℚ-combination
   `P = ∑ j ∈ range (k+1), c j • binomQ j`, by strong induction on the
   degree (subtract `(leadingCoeff · k!) • binomQ (natDegree P)`; degree
   drops — `binomQ` is monic-after-scaling). Alternative: the c-vector is
   the finite-difference vector `c j = Δʲ P (0)`; if Shape.lean's
   `production_int_all` proof already sets up Δ, PREFER extracting and
   reusing its machinery (state `deltaPoly P := P.comp (X + 1) − P` and the
   two lemmas: degree strictly drops, integer-valued is preserved).
3. **Integrality of the c's**: from `hval` and the triangular system —
   with the Δ route it is immediate (`c j = Δʲ P (0)` is a ℤ-linear
   combination of values `P(0..j)`, or directly integer-valued by
   induction); with the subtract-leading route, evaluate at `0, 1, …, k`
   and solve triangularly. The Δ route is cleaner: commit to it.
4. **Assemble**: `k! • P = ∑ j, c j · (k!/j!) • descPochhammer ℚ j` with
   `c j ∈ ℤ` and `k!/j! ∈ ℕ` (`Nat.factorial_dvd_factorial`, `j ≤ k`);
   `descPochhammer ℤ j` maps to `descPochhammer ℚ j`
   (`descPochhammer_map` — grep the exact name), so exhibit
   `Q = ∑ j, (c j · (k!/j!)) • descPochhammer ℤ j`.

## Notes

- Stay in `Polynomial ℚ` with `∃ z : ℤ`-style integrality throughout —
  matching Shape.lean's idiom — and produce the ℤ-polynomial only in the
  final assembly.
- `Polynomial.funext` needs an infinite domain — fine over ℚ; use it if
  you go via "two polynomials of degree ≤ k agreeing on k+1 points"
  (`Polynomial.eq_of_degree_lt_of_eval_finset_eq` — grep for the exact
  Lagrange-style uniqueness lemma; `Pin.lean` already does Lagrange
  pinning, look there first for the house pattern).
- No native_decide anywhere in this file.

## Done criteria

`lake build` green, no `sorry`; `#print axioms production_factorial_int` =
standard three, guarded. Commit
`lean-ow: IntCoeff — k!·P_k has integer coefficients`.
