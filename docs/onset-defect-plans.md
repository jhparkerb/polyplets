# Follow-on plans: the diagonal law's error term

2026-08-09. Five plans arising from `results/onset-defect-law.md`, which measured
the below-onset defect of the diagonal law as

```
D_j(k) ~ C_j · 9^k · k^(j−3/2),   C_1 = √6/(27√π),
A_j = C_j Γ(j−1/2) = (√6/27)·(25/81)^(j−1)·binom(2j−2,j−1)/2^(j−1)
```

with the rate equal, per cell, to the thin-diagonal rate `T(n,n) = 3^(n−1)`
(`9^k = 3^(n+j−1)` on the depth-j line) and confirmed on the square lattice (thin
rate 1, depth-1 defect not growing at all, exactly `(−1)^(k+1)`). Everything here is measured, nothing is derived. These five plans are
the routes onward.

No time estimates. Cost is stated only as desk work (post-processing data already
on disk) versus engine work versus machine time, since that determines what
gets blocked by what.

---

## 1. Second Term  — WORKED 2026-08-09, kill criterion fired

**Goal.** Extract `a` in `D_1(k) = C_1·9^k·k^(−1/2)·(1 + a/k + O(1/k²))` and try
to recognise it the way `√6/27` was recognised.

**Why.** `C_1` was identified to 2.3e−08 and that identification stands on one
constant. A second algebraic constant from the same expansion would make an exact
analytic form for the defect very hard to argue against, and it hands any
derivation a second target to reproduce — a derivation that gets `√6/27` right
and `a` wrong is wrong.

**Method.**
- `D_1(k)` is exact rational for k ≤ 19 (`experiments/slope2_law_vs_truth.py`
  builds it). Form `B_k = D_1(k)·9^(−k)·√k / C_1_exact − 1`, so `B_k ~ a/k`.
- Richardson in 1/k to successive orders, with the resolution fixed by a control
  suite. **Not** the control that shipped in `experiments/defect_amplitude.py` —
  that one used a correction series terminating at 1/k², which any Richardson of
  order ≥ 2 interpolates exactly, so it reported ~1e−15 "error" and measured
  nothing. Use non-terminating flavours: a smooth infinite 1/k series, a
  half-power contaminant (1/k^1.5), and a log contaminant (log k / k). Report only
  the digits the worst relevant flavour supports.
- Work in exact rationals or high precision, not float: `D_j(k)` exceeds 2^53 by
  k = 19, so float noise is otherwise inside the error budget for free.
- Recognition against the constant field the leading term lives in: rationals
  times `√6`, `√π`, and products with powers of 3 and 25. Reuse
  `experiments/amplitude_pslq.py` if the naive sweep misses.
- Repeat for `j = 2` and check whether `a_2` relates to `a_1` the way `A_2`
  relates to `A_1`.

**Kill criterion.** If the *non-terminating* control suite shows fewer than ~4
trustworthy digits in `a`, recognition is not possible on k ≤ 19 and the plan
stops there with that recorded — do not fit harder. (Stated against the honest
suite deliberately: the terminating control could never have fired this.)

**Depends on.** Nothing. Pure desk work on banked exact values.

**Feeds.** Discarded Term (§4).

**Output.** A section appended to `results/onset-defect-law.md`.

**RESULT.** `a = 0.005139 ± 0.000033` — 2.2 significant figures, 526 rationals
inside the bar. Kill criterion fired; not recognisable on k ≤ 19. Three
by-products kept: `C_1` confirmed to 3e−08 (10x sharper than §2, because a wrong
constant diverges rather than shifts), the `25/81` depth ratio confirmed the same
way at j=2, and `a` shown 24x smaller and opposite in sign to the central
binomial's −1/8, ruling out `D_1 ∝ binom(2k,k)(9/4)^k`. See
`results/onset-defect-law.md` §2b.

**SUPERSEDED 2026-08-09, same day:** `a` is now DERIVED exactly —
`a = 3293/92928 − 3251√3/185856 ∈ Q(√3)`, from the algebraic minimal
polynomial of the depth-1 generating function
(`results/onset-defect-depth1-closed.md`). The kill criterion was right to
fire: the constant lay outside every field this plan searched.

---

## 2. Boundary Layer  — WORKED 2026-08-09, partial success

**Goal.** Find the scaling variable that governs the crossover between the
near-onset law and the deep-below-onset region, i.e. the exponent `p` in `j/k^p`
that collapses the residual surface.

**Why.** §3 of `results/onset-defect-law.md` records that the resummation
`(1 − 9z − 50t/81)^(−1/2)` holds near the onset line and degrades smoothly with
depth: residual slope per k of −0.009 at `x = H/k ≥ 0.85` against −1.15 at
`x ≈ 0.18`. Smooth degradation means there is a crossover scale. This is the only
route I can see to `g(x)`, the large-deviation limit shape of
`results/diagonal-law-below-onset.md`, which remains unexplained — the
resummation predicts `g(0.35) = +0.66` where measurement gives −0.22.

**Method.**
- The residual table `ln D_measured − ln D_predicted` over all below-onset
  `(k, j)` already exists in `experiments/defect_bivariate.py`; factor it out into
  a reusable table first.
- Fit `residual = f(j/k^p)` by scanning `p` and scoring the collapse (spread of
  residuals within bins of the scaling variable, normalised). Candidate values
  carry meaning: `p = 1/2` Gaussian crossover, `p = 2/3` an Airy-type coalescing
  saddle, `p = 1` no boundary layer at all (the whole picture would be wrong).
- Control: build a synthetic surface with a *known* crossover exponent and
  confirm the scoring recovers it at the same data extent. Without this the scan
  will return its favourite `p` regardless.
- If a `p` collapses cleanly, fit the limiting crossover function and check
  whether it matches `g(x)` in the overlap region.

**Kill criterion.** If no `p` collapses the surface better than the control's
noise floor, record that the crossover is not a single power and stop.

**Depends on.** Nothing. Desk work on the existing residual table.

**Feeds.** Discarded Term (§4) — tells it what uniform form to aim for. Also
feeds `results/diagonal-law-below-onset.md` directly if `g(x)` falls out.

**Output.** `results/onset-defect-crossover.md`, plus an update to
`diagonal-law-below-onset.md` §2 if `g(x)` is explained.

**RESULT.** Crossover variable found: `u = j/k^p`, `p = 0.385` in [0.345, 0.485].
Airy (2/3) and no-layer (1) excluded; 1/2 disfavoured by 18%. The
large-deviation family `k^q φ(j/k)` is excluded outright, missing its own control
floor. 168 cells collapse onto `f(u) = 0.612·u(1−u)` — one parameter, 99.1% of
the spread. The layer's edge is `u = 1`, i.e. `j ≈ k^0.4`, which independently
agrees with §2's finding that the amplitude family is supported only to j ≤ 4.
`g(x)` is NOT reached: at fixed x, `u → ∞`, and the data reaches only u = 5.8.

---

## 3. Spectral Edge  — WORKED 2026-08-09, ABANDONED (negative)

**Goal.** Test the two-strand reading structurally rather than by curve fit: does
the row-transfer operator show a continuum edge at `3² = 9`?

**Why.** The mechanism claimed in `results/onset-defect-law.md` §4 — one-strand
sector at 3, two-strand continuum edge at 9, universal square-root density of
states giving `k^(−1/2)` — is a reading of the numbers plus one cross-lattice
test. Confirming it from the operator side would be independent of both.

**Method.**
- Work from the existing strip machinery: the `μ_H` certified ladder
  (`results/strip-mu-certificates.md`) and the `q_H` atoms with degrees
  1, 2, 4, 9, 29, 68, 181, 462, 1254, 3289.
- For each `H`, extract the spectrum below the dominant eigenvalue and look for a
  band of eigenvalues whose density near a lower edge approaches 9 as `H` grows.
- Cross-check on the square lattice, where the same construction must show the
  edge at 1.

**The hard part, stated up front.** A finite strip has a discrete spectrum. A
"continuum edge" only exists in the `H → ∞` limit, so this is an extrapolation
over a sequence of finite spectra — precisely the failure mode that
`results/slope-slicings.md` demonstrated with the a(n) control, where three
models predicted holdout to 1e−5 while disagreeing about the exponent by 0.1.
Any claim here needs a control on a strip family whose limiting edge is known
independently, and if no such control can be built the plan should be abandoned
rather than run on faith.

**Depends on.** Engine work — the strip machinery, so a rebuild on whichever box
it runs on (`rebuild-remote-after-engine-edit`). No new enumeration.

**Feeds.** Discarded Term (§4), as corroboration only.

**Output.** `results/strip-spectrum-defect-rate.md` (renamed — see below).

**RESULT: abandoned, negative, and the premise was wrong.** Per cell the defect
rate is 3, the thin-diagonal rate itself, not its square: `9^k = 3^(n+j−1)` on the
depth-j line, and no reachable data separates the two readings. §4 of
`onset-defect-law.md` rewritten. The squared reading was also impossible — 9
exceeds every `μ_H`. Testing for 3 instead: the spectrum is directly the
reciprocal roots of the fixed-height GF denominators (no engine work needed,
contrary to this plan's assumption); the control reproduces `μ_2 = 1+√2` exactly
and caps the usable range at H ≤ 7 by returning an impossible 13.67 at H = 8.
**Zero eigenvalues within 2% of 3 at every H ≤ 7**, and `Q_H(1/3) ≠ 0` exactly.
The strip operator is probably the wrong object anyway: it governs growth at
fixed H, while the defect lives where n and H grow together.

---

## 4. Discarded Term  — first pass 2026-08-09, term identified

**Goal.** Derive `9`, `√6/27`, and `25/81` from the cluster weights. Turn the
measurement into a theorem.

**Why.** This is the actual prize. It would also explain, rather than merely
record, why the depth resummation is a boundary layer.

**Method.**
- `experiments/grand_form_check.py` already builds the one-mode resummation ab
  initio from the Lean-verified aggregated cluster weights `V(l,j)`, `Vt(l,j)`
  (`polyplets/Polyplets/Weights.lean`, `Weights3.lean`, `Weights3Heavy.lean`),
  through the `(z*, u)` induction and the diagonal Lagrange substitution, out to
  y-order 3, and reproduces `P_1..P_3` coefficient-exactly.
- The proof's onset `H ≥ k+1` should come from a term whose y-valuation is at
  least `H`, which is exactly why it vanishes above onset and is the leading
  survivor below it. **Locate that term in the construction and keep it instead
  of dropping it.**
- Its leading behaviour should give the rate. The prediction to check against:
  rate exactly 9, exponent `j − 3/2`, amplitude `√6/27`, depth ratio `25/81`,
  and — from Second Term, if it ran — the 1/k coefficient.
- The square-lattice arm is the cheapest sanity check on any candidate
  derivation: it must give rate 1 and depth-1 defect exactly `(−1)^(k+1)`
  (i.e. +1, −1, +1, −1, +1 for k = 1..5 — get the sign right, a correct derivation
  producing this must not be rejected for disagreeing with a mis-stated target).

**Depends on.** Nothing strictly. Much better informed after Second Term (§1) and
Boundary Layer (§2), and corroborated by Spectral Edge (§3). Desk work, but real
research rather than post-processing.

**Output.** `docs/proofs/onset-defect.md` (planned) if it closes; otherwise a recorded
account of where the construction resists, which is itself worth having.

**RESULT (first pass), `results/discarded-term.md`.** The discarded object is
identified — and there are **two** terms, not one: `[y^k](μ^(H+1) ρ_H)` killed
above onset by `ord_y(ρ_H) ≥ H`, and `[y^k][z^H]P` killed by
`deg_z [y^k]P ≤ k`. Both cut in at exactly `H ≤ k`, which is why the onset is
sharp. Structural payoff: at depth j the extraction reaches `j−1` orders past the
valuation, predicting `θ_j − θ_1 = j−1` — which is exactly the measured
`θ_j = j−3/2`, at every depth. The exponent family is now explained rather than
observed. Not derived: `θ_1 = −1/2`, the rate, `√6/27`, `25/81`, all of which
reduce to the leading-y-coefficient asymptotics of `g_i` as `i → ∞`. Obstacle:
that needs `σ_j` to high order, and cluster weights are Lean-verified only to
j ≤ 3. Untested route around it: invert the Step 4–5 cumulant map to recover
`μ(y)`, `z*(y)` to order 19 from the wired `P_k` — partial, since it leaves the
edge series `E_b`, `E_t` unrecovered.

**SUPERSEDED at depth 1, 2026-08-09:** the cumulant-inversion route was never
needed. At the top z-degree the extraction collapses to the all-pairs families
alone, computable to any order by the gap walk; the two discarded terms are
exactly `[y^k]P̂` and `[y^k](B²/(3+S))`, their cancellation is the rank-one
residue cancellation of the localized eigenvalue, and the rate, `θ_1`,
`√6/27`, and the 1/k term are all derived —
`results/onset-defect-depth1-closed.md`. The `25/81` depth ratio and depths
j ≥ 2 remain open (one new weight family per unit of depth; priced in that
note's §6).

---

## 5. Third Lattice  — MOSTLY ALREADY ON DISK (found in review, 2026-08-09)

**Goal.** Test whether the defect rate is tied to the thin-diagonal rate at all,
on a lattice whose thin rate is neither 1 nor 3.

**Correction to this plan's original premise.** It said a third lattice would
discriminate the per-cell reading from the squared reading. **It cannot** — on any
lattice with onset `n = 2k+1`, a thin rate `g` gives `g^n = (g²)^k·g^(1−j)`, so the
two are the same function of (k,j) everywhere. Nothing separates them. What a
third lattice tests is the *generality of the thin-rate relation*, which is still
the weakest joint in `results/onset-defect-law.md` §4, since the square lattice is
degenerate (1 = 1²).

**It also called for fresh enumeration. That was wrong** — `results/hex-diagonal-law.md`
has been banked since 2026-07-15:

```
T_hex(n, n−k) = P_k(n)·2^(n−1−3k),   deg P_k = k,   onset n >= 2k+1
```

Thin growth **2**, exact `P_1`, `P_2`, validated enumerator `experiments/hex_gas.py`.
Both of this plan's original first steps — "choose a rule with continuation count
2" and "confirm the count" — are already answered.

**Method (desk work now, not machine time).**
- Compute hex depth-1 defects `D_1(k) = T_hex(2k,k) − law` from the banked `P_k`.
- Prediction to falsify: rate 4 (thin rate 2, so `2^n = 4^k` on that line), with
  exponent `−1/2`, i.e. `D_1(k)/D_1(k−1) → 4·(k/(k−1))^(−1/2)`.
- A first pass during review, surplus budget 3, gives `D_1 = 1/4, 7/8, 45/16` at
  k = 1, 2, 3, ratios 3.50 and 3.21 against predictions 2.83 and 3.27 — the k=2→3
  ratio within 1.6%. Three points prove nothing; extend `P_k` far enough for a
  real ratio test, which is what this plan should now be.

**Kill criteria.** (i) If hex `P_k` cannot be pushed far enough for the ratio
estimator to resolve 4 from, say, 3.8 — calibrate that first, as with the
polyplet rate control — stop. (ii) Do not assume the exponent `−1/2` carries over;
it is a separate measurement.

**Depends on.** Nothing. Desk work on banked hex data.

**Feeds.** `results/onset-defect-law.md` §4, whose thin-rate reading currently
rests on one non-degenerate lattice.

**Output.** `results/third-lattice-defect.md` (planned).

---

## 6. Series Acceleration

**Goal.** Sharpen the λ estimator of `results/slope-growth-saddle.md` (currently
7.08 ± 0.07) without new `P_k`.

**Why.** That doc concluded the estimator "cannot be sharpened without more
`P_k`". That was too quick. The limitation is that `y_c ≈ 0.0373` sits close to
`B`'s radius (~0.048), so the truncated series misbehaves — three of ten J values
give no saddle solution at all. Standard series acceleration is the textbook
response and it works on the series already in hand.

**Method.** Pade and differential approximants on `B(y)` in place of the raw
truncation; re-run the saddle from the approximant. Control: apply the same
acceleration to a series with a known singularity structure and confirm it
recovers the right `y_c`. Success looks like the J = 13, 15, 18 failures
disappearing and the spread across J collapsing.

**Kill criterion.** If the approximants disagree among themselves by more than
the current ±0.066, acceleration is not buying anything at 19 terms; record and
stop.

**Depends on.** Nothing. Desk work on `b_1..b_19`.

**Feeds.** Nothing else — this one is self-contained.

**Output.** An update to `results/slope-growth-saddle.md`.

---

## Dependency summary

```
Second Term  ──┐
Boundary Layer ┼──> Discarded Term        (informing, not blocking)
Spectral Edge ─┘

Third Lattice ───> independent of all four
Series Acceleration ───> independent of all five
```

Nothing blocks anything. All four of Second Term, Boundary Layer, Spectral Edge
and Discarded Term can start cold; the arrows mean the derivation is better armed
after the others, not that it must wait. Third Lattice shares no data or
machinery with the rest and tests a different claim — the generality of the
rate-squared relation rather than the structure of the polyplet defect.

Cost classes: Second Term and Boundary Layer are desk work on data already on
disk. Spectral Edge is engine work. Discarded Term is desk work but research.
Third Lattice needs machine time.

---

## Review record

These plans and the results they rest on were reviewed adversarially on
2026-08-09 before any of them was worked. The review re-verified the substrate
independently — the `diagCoeffTable` parse against all 380 banked in-onset cells,
the square-lattice file format and its onset claim, and the P-finite nulls — and
found those sound. It also found real defects, all since fixed in place:

- **Vacuous control.** `experiments/defect_amplitude.py`'s control used a
  correction series terminating at 1/k², which Richardson of order ≥ 2
  interpolates exactly. Its ~1e−15 "errors" were float roundoff, so the shipped
  justification for C_1's precision was empty. Independent re-testing with
  non-terminating controls indicated C_1 survives, but the fix is a prerequisite
  of Second Term, folded into §1 above.
- **Sign error.** The square-lattice depth-1 defect is `(−1)^(k+1)`, not
  `(−1)^k`, and the wrong sign had propagated into three files including the
  acceptance test in Discarded Term §4 — where it would have caused a correct
  derivation to be rejected.
- **λ overstated.** 7.12 ± 0.06 quoted the J=19 endpoint; the true spread is
  7.015–7.147, giving 7.08 ± 0.07. Three J values fail to solve, not two.
- **A circular check.** "All 19 log coefficients come out linear in n" is imposed
  by construction for k ≥ 11 by `scripts/derive_pk_fast.py`; it is a genuine test
  only for k ≤ 8.
- **Soft overdetermination.** The amplitude family's `binom(2j−2,j−1)/2^(j−1)`
  form is strongly supported at j = 2, well supported at j = 3, and only
  consistent at j = 4..7 — where the script's own rational recognizer returns
  different fractions entirely. The "five degrees of overdetermination" phrasing
  overstated this.

Two items the review raised are now plans in their own right: the honest control
suite (inside Second Term) and Series Acceleration (§6).
