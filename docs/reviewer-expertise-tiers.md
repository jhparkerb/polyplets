# Reviewer expertise required, by claim tier

Written 2026-08-17. Question asked: what level of mathematical expertise is
needed to assess a(40), and then all the other claims we are confident in?

Short answer: **a(40) needs almost no mathematics to assess — it needs a
systems reviewer.** The rest splits into three genuinely different expertise
pools, and no one person covers all of them.

## Tier 0 — a(40) itself, and everything on the enumeration ladder

The claim is "this integer is the number of n = 40 king-connected animals."
The mathematical content is a definition anyone can restate in a sentence.
What is load-bearing is transfer-matrix / frontier enumeration as an
*engineering* artifact: checkpoint and resume semantics, CRT residue
recombination, and whether the validation chain closes — b-file n ≤ 20, the
banked chain a(21)–a(39), the strip second source, the subgroup mod-4 and
mod-8 congruences, the holdout P_k confirmations.

Reviewer profile: a strong computational combinatorialist, or a competent
systems person who has done exact enumeration once. Redelmeier's paper plus a
week is sufficient background. The Zero Harvest bug is the model of what a
real reviewer here would catch — it was a resume bug, not a math error.

**Bar: undergraduate combinatorics plus serious software-review skill.** That
is the whole requirement for the headline number.

## Tier 1 — the closed forms and the diagonal structure

P_k, the diagonal law, the grand form, the cutcount identity
Σ_configs Π_births (q − b) = q^{c(S)}, the k!·P_k ∈ ℤ[n] divisibility, the v₅
denominator law, the ternary spine cubic.

These are finite, checkable algebra over ℤ[q] and ℚ[n]. A first-year graduate
student in combinatorics can verify every one by hand or with a CAS; several
are Lean-formalized, which drops the bar to "can read Lean 4 + Mathlib." No
specialist knowledge beyond generating functions and polynomial arithmetic.

**Bar: graduate-level, not research-level.** This is the tier where
machine-checkability actually buys something.

## Tier 2 — the asymptotic and analytic claims

Here the requirement jumps, and it is a different person from Tier 0.

- **λ bracket 6.543 ≤ λ ≤ 9.3154** — both ends are certificates in exact
  arithmetic, so mechanically this is Tier 1. Judging whether the bound is
  *interesting* needs the polyomino growth-constant literature (Klarner,
  Barequet–Ben-Shachar, Madras).
- **Anisotropic GF not D-finite** — unconditional theorem, but assessing it
  needs holonomy / D-finiteness machinery: the Flajolet–Sedgewick and
  Bousquet-Mélou orbit.
- **Onset defect law, Ridgeline amplitudes, grand-form saddle μ₂ = 42.39460,
  α = 50/81** — singularity analysis, saddle-point method, branch-point
  velocity, "square root not Airy." Ridgeline §5 explicitly names four
  unproved singularity-form assumptions. A reviewer has to have *done*
  asymptotic enumeration, because the question is whether an
  unproved-but-argued assumption is the kind that usually holds.
- **Perimeter both-ends / tip factor = Andrews φ₂, an eta quotient** —
  q-series and modular-form fluency. A different subfield again.

**Bar: research mathematician active in analytic combinatorics.** The
Ridgeline/onset-defect items and the eta-quotient item plausibly want two
different such people.

## Tier 3 — the priority question

Ghost Ship Layer 3 is the cautionary case: the result was correct, internally
verified, and already in Richard arXiv:0704.0716. No amount of mathematical
skill catches that. It needs someone with the literature in their head, or a
systematic search — a bibliographic competence, orthogonal to the other three
tiers. Adopted as standing practice on any result called new.

## The composite

One reviewer covering the whole confident set would need exact-enumeration
engineering, analytic combinatorics, q-series, and the polyomino literature.
That is roughly Bousquet-Mélou or Jensen, and there are not many others.

The practical version is three reviewers: a computational person for a(40) and
the ladder (the bulk of the value, and the cheapest to check), an analytic
combinatorialist for Tier 2, and a literature pass.

The asymmetry worth recording: the headline claim is the *easiest* to assess
and the most heavily corroborated. The claims needing the scarcest reviewers
are the asymptotic ones, which are also the ones carrying named unproved
assumptions.
