# H2: haruspicy on convex polyplets by area — a structural contrast

2026-07-14. Fixed-height convex (HV-convex king) area GFs recovered exactly
for H <= 7 (phase-automaton DP, brute-validated n<=8 incl. row sums; BM with
12-15 holdouts): denominator orders **1, 3, 7, 14, 25, 36, 53**.
Denominators: `results/convex_height_denominators.json`;
tool `experiments/convex_heights.py`.

## The finding: root RECYCLING, not root separation

New-root content psi_H (mod-p certified): degrees **1, 2, 3, 5, 7, 6, 8** —
near-linear growth, with psi_2 not even squarefree (repeated new factor).
The convex family's strip spectra massively REUSE earlier roots, the exact
opposite of the full family's Atom Ledger root separation (psi degrees
1, 2, 4, 9, 29, 68, 181, 462, 1254, 3289). Consequences:

- The pole-argument exclusion boxes for the convex anisotropic GF are weak
  (with 3 levels of deg psi > 5: only r <= 2 & D <= 5-class statements).
  H2 does NOT usefully strengthen the Convex Mirage by this route; the
  Mirage's by-area non-D-finiteness stands on its empirical footing.
- **Root separation is a feature, not a default.** The unrestricted king
  family generates genuinely new spectral content at every height; the
  convex restriction collapses that. This sharpens what the Atom Ledger
  measures: the H1 non-D-finiteness mechanism is special to the full family.
- Hook for the conditional statement: the dominant poles 1/mu_H^cc are
  strictly decreasing (mu increasing toward 3.129), giving >= 1 genuinely
  new root per level forever — but one new root per level only supports
  order-0 exclusions; the full-family argument needed the degree explosion.

## Status

H2 executed and closed: negative-but-informative. The exact H <= 7 convex
strip GFs are a new byproduct (orders 1,3,7,14,25,36,53 — not in OEIS as
far as checked for the full family; not submitted).
