# Finite-lattice method — crossover analysis (NEGATIVE: does not stack)

Date: 2026-07-10. Closes the "does Enting/Jensen finite-lattice net us a reach
win over the current king TM" question. Resolved from banked data, no new run.

## Question

Jensen's finite-lattice method (FLM) computes a plane series by inclusion–
exclusion over finite `W×L` rectangles, each rectangle counted by a straight
column transfer matrix. Its headline win is the bounding-box inequality
`H+W ≤ n+1` for a connected `n`-cell animal: you sweep every animal along its
**longer** side, so the frontier you pay for exponentially is the **shorter**
side, `min(H,W) ≤ n/2`, never the full `n`. Does that halving stack on top of
what our engine already banks, or is it the same `½`?

## Verdict: same `½`. FLM does not stack; it would only add overhead.

The engine already caps the swept dimension at `n/2`, via **two** mechanisms:

1. **Transpose symmetry `B_{H,W}=B_{W,H}`.** A height-`W` strip sweep enumerates
   all widths at once, so sweeping heights `1…⌈n/2⌉` yields the *entire*
   bounding-box matrix; the tall half is filled by transpose. This is why
   `results/ns_a36/perheight/` stops at h18/h19 for n=36 — exactly `n/2`.
2. **Diagonal-polynomial derivation** (docs/a26-a30-diagonal-plan.md) pushes the
   highest *run* height even below `n/2`.

FLM's re-orientation payoff *is* that same cap: "sweep along the short side so
the frontier is `min(H,W) ≤ n/2`." We already do it. The hard floor for both
methods is the **square** animal `H≈W≈n/2`, which neither can avoid.

## Supporting data (banked, no new compute)

- Frontier state growth = atom degrees `q_H = 1, 2, 4, 9, 29, 68, …`
  (results/triangle-structure.md). The peak swept-height cost is `q_{n/2}`.
- `results/bbox_polyplets_n17_exact.txt`, mass by short dimension `min(H,W)`:

  | min(H,W) | mass (n=17) |
  |---|---|
  | 5 | 3.63e11 |
  | 6 | 8.97e11 |
  | 7 | 1.25e12 (peak) |
  | 8 | 9.16e11 |
  | 9 | 3.39e11 |

  Square-ish animals near `n/2` are numerous, not a tail — both methods pay
  `q_{n/2}` for them. The leading exponential is identical either way.

## Conclusion

FLM changes the leading term by nothing (`q_{n/2}` both ways) and adds the
inclusion–exclusion cost of many signed rectangle passes. **Net loss for us.**
Do not build it. The transpose cap already captures its only exponential lever.

## No residual algorithmic lever — connectivity is the wall

Correction to an earlier draft of this note: boundary-only / contour state is
**not** an untried lever. It was measured-negative on 2026-07-02 as the
tensor-network / MPS frontier-compression probe
(results/boundary-push-tensornetwork.md): the exact bond dimension grows
`χ ~ λ^(H/4)`, so `χ²` ≈ the frontier and MPS storage is 2–5× *worse*. The
entanglement is *connectivity* entanglement — cutting the boundary splits
non-crossing-partition components, rank ~ Catalan/Motzkin at the cut — intrinsic
to counting connected objects. The companion probe
(results/boundary-push-recurrence.md) separately showed T(n,H) is not
2D-holonomic (no recurrence accelerator).

Same wall as this doc's FLM negative and as the strong-product-factoring
negative (results-adjacent): **connectivity is global and does not compress,
factor, or re-slice away.** All four levers — new axis, finite-lattice, contour
compression, holonomic recurrence — are now measured or argued dead. The √λ
diagonal sweep is essentially optimal; remaining speed is engineering, not
algorithm.
