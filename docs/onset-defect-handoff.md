# Handoff: the diagonal law's error term

2026-08-09. Everything needed to pick this up cold. Two adversarial reviews have
run over this material; the corrections they forced are more instructive than the
original claims, so read §5 before trusting anything.

> **2026-08-09, later the same day — depth 1 is CLOSED.**
> `results/onset-defect-depth1-closed.md`. The depth-1 defect is the top
> coefficient of the column numerator `R_k`, assembles exactly from the
> all-pairs gap-walk families (`D_1 = [y^k](P̂ − B²/(3+S))`, verified at all
> 19 banked cells, extended exactly to k = 200 — the "P_k stops at 19" wall is
> gone), and its generating function is ALGEBRAIC: irreducible quartic `Φ`,
> 144 orders of holdout. All constants now DERIVED, not measured: rate 9,
> θ = −1/2, `C_1 = √6/(27√π)`, and the second term
> `a = 3293/92928 − 3251√3/185856 ∈ Q(√3)` — outside every field the k ≤ 19
> recognition searched, which is why its kill criterion fired. `D_1` is
> P-finite at (r,d) = (35,4), exhibited; the old nulls were correct as scoped.
> Scripts: `experiments/depth1_{gap_walk,asymptotics,minpoly,recurrence}.py`.
> Open there: ~~kernel-method derivation of `Φ`~~ **done 2026-08-09
> (Severance W2, `experiments/severance_w2_kernel.py` — Φ now derived, gate
> `severance_w2_gate.py` green)**, and depth j ≥ 2
> (finite new weight families per depth; priced in that note's §6).
> P_k anchors also severed for k ≤ 9 (Severance W1,
> `results/severance-w1-anchor-cut.md`).
> Items 1 and 3 of §4 below are superseded at depth 1; the ranking stands for
> the rest.

## 1. The question

The diagonal law `T(n,n−k) = P_k(n)·3^(n−1−3k)` is proved for `n ≥ 2k+1`
(`docs/proofs/diagonal-law.md`, `docs/proofs/grand-form.md`). Below that onset it
is invalid but remains numerically excellent. This campaign measures *how* it
fails, and asks whether that failure has structure.

Coordinates used throughout: surplus `k = n − H`; **depth below onset**
`j = 2k+1−n`, so `n = 2k+1−j` and `H = k+1−j`. `j = 1` is the first invalid line,
`n = 2H`. The defect is `D_j(k) = T − law`, exact rational for k ≤ 19.

## 2. What is established

| claim | where |
|---|---|
| law reproduces all 380 banked in-onset cells exactly | re-verified in review, `docs/onset-defect-plans.md:318` |
| rate at depth 1 = `8.999998 ± 2.2e−05`; `θ_j = j−3/2` consistent j=1..7 | `results/onset-defect-law.md:35` |
| `C_1 = √6/(27√π)`, 5e−08 away, bar 3e−07, unique in `√m/(n√π)` | `results/onset-defect-law.md:72` |
| amplitude family `binom(2j−2,j−1)/2^(j−1)` **supported j ≤ 4 only** | `results/onset-defect-law.md:97` |
| per cell the rate is 3 = the thin-diagonal rate (`9^k = 3^(n+j−1)`) | `results/onset-defect-law.md:207` |
| square lattice: degree k, onset exactly 2k+1, depth-1 defect `+1,−1,+1,−1,+1` | `results/onset-defect-law.md:238` |
| defect not P-finite in the reachable envelope (with a control that fires) | `results/onset-defect-law.md:307` |
| holdout: +3.4 digits on cells never fitted | `results/onset-defect-law.md:263` |
| `μ₂ = 42.3946` (~4.5 digits) by two estimators; `λ = 7.08 ± 0.07` | `results/slope-growth-saddle.md:59,108` |
| large-deviation family excluded; Airy and no-layer excluded | `results/onset-defect-crossover.md:34,53` |
| nothing within 2% of 3 in the strip spectrum, H ≤ 7 | `results/strip-spectrum-defect-rate.md:50` |
| two discarded terms, decomposition and signs verified exactly at k ≤ 3 | `results/discarded-term.md:20` |

## 3. Files

**Results.** `onset-defect-law.md` (main), `diagonal-law-below-onset.md`
(predecessor), `onset-defect-crossover.md`, `strip-spectrum-defect-rate.md`,
`discarded-term.md`, `slope-growth-saddle.md`, `slope-slicings.md`,
`hex-diagonal-law.md`.

**Plans.** `docs/onset-defect-plans.md` — six plans, each annotated inline with
its RESULT. Four are worked, Third Lattice and Series Acceleration are not.

**Scripts** (`experiments/`, all pure Python 3, run from repo root, seconds each):

- `slope2_law_vs_truth.py` — provides `read_pk`, `read_tri`, `law`; everything else imports these
- `defect_controls.py` — the control apparatus (non-terminating suites, matched control, mpmath extraction, rate control, θ-coherence, family bars)
- `onset_defect_nine.py`, `defect_nine_exponent.py` — rate and exponent
- `defect_amplitude.py`, `defect_amplitude_family.py` — amplitudes
- `defect_bivariate.py`, `boundary_layer.py` — the residual surface and its collapse
- `second_term.py`, `second_term_recognise.py` — the 1/k coefficient
- `defect_pfinite_full.py` — algebraic nulls
- `square_defect_rate.py`, `spectral_edge.py` — cross-lattice and spectrum
- `grand_form_saddle.py`, `lambda_from_grand_form.py`, `defect_holdout.py`

**Data formats — misread these and you silently get garbage.**
`results/ns_a40/perheight/h{H}.out` is `n count`.
`results/bbox_square4_n21.txt` is `n H W count` (both orientations listed).
`results/bbox_polyplets_n17_exact.txt` is `H W n count` — different order.
`P_k` lives in `orchestrator/sweep.go` `diagCoeffTable`, coefficients **descending**
with a denominator; ascending evaluation fails loudly, which is the check to run.

## 4. Open threads, ranked

1. **Discarded Term is the prize and its shape just changed.** The two discarded
   terms largely cancel (ρ-term is 7× the defect at k=3), so the constants live in
   the difference. Needs the asymptotics of *both* `[y^k]g_{k+1}` and `[z^k][y^k]P`.
   Blocked by cluster weights being Lean-verified only to `j ≤ 3`. The untested
   route around: invert the Step 4–5 cumulant map to recover `μ(y)`, `z*(y)` to
   order 19 from the wired `P_k` — partial, leaves `E_b`, `E_t` unrecovered.
2. **Third Lattice** is now desk work, not machine time — hex is banked with thin
   growth 2. Predicts rate 4. This repairs the weakest joint in §4, since the
   square lattice is degenerate (1 = 1²).
3. **Series Acceleration** — Padé / differential approximants on `B(y)` to sharpen
   `λ = 7.08 ± 0.07` without new `P_k`. Self-contained.
4. **`g(x)` remains unexplained.** Boundary Layer did not reach it: at fixed
   `x = H/k` the scaling variable runs to infinity and the data reaches only 5.8.

## 5. Read this before trusting anything above

Both reviews found the same failure mode, and it is the one to guard against:
**numbers computed at the shell rather than in a shipped script**, then quoted
with a precision the script cannot reproduce.

Specifically withdrawn or downgraded, all now marked in place:

- `f(u) = 0.612·u(1−u)` — **withdrawn.** Tail-dominated; refitting inside the layer
  gives 0.063, 10× smaller. Only the residual's sign structure is real.
- `p = 0.385` with 1/2 "disfavoured by 18%" — **downgraded.** Resampling moves it
  between 0.275 and 0.44. Only `p ≈ 0.4` is defensible; 2/3 and 1 stay excluded.
- `a = 0.005139 ± 0.000033` — the shipped script prints ±0.02. Conclusion (kill
  criterion) is robust; the precision is not in code.
- `C_1` to 3e−08 — sound argument, ~3× optimistic, conditional on `θ = −1/2`, and
  computed by no script in the repo.
- `θ_j − θ_1 = j−1` "explained" — it is a **retrodiction** resting on an underived
  step.
- "Third Lattice discriminates the per-cell from the squared reading" — **false.**
  On any lattice with onset `2k+1`, `g^n = (g²)^k·g^(1−j)`. Nothing separates them.

Earlier round-one findings, all fixed and verified: a vacuous control (a
correction series that terminated, so Richardson interpolated it and reported fake
1e−15 errors), a sign error `(−1)^k` → `(−1)^(k+1)` that had reached an acceptance
test, λ quoted off an endpoint, and a circular linearity check (imposed by
construction for k ≥ 11, genuine only k ≤ 8).

**Standing instruction for whoever continues:** before citing any number here,
check it is printed by a script in `experiments/`. Several of the best-sounding
ones are not, and that is exactly where both reviews landed. ~~Known script bugs
to fix~~ **both fixed 2026-08-09**: `defect_controls.py`'s (c3) verdicts now use
the doc's uniqueness scoping (supported j ≤ 4; consistent with 8/18/20 rival
rationals at j = 5/6/7), and `second_term.py` is main-guarded so importing
`bseq` no longer re-runs its pipeline.
