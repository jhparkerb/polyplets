# r4-tallband — progress

ABOUT TO: step 1, read PROVENANCE.md + triangle.txt + perheight
DONE: step 1 (PROVENANCE.md) -> H22-H40 confirmed closed-form injected
  ("Real sweeps H3-H21; H22-H40 via wired P_k closed forms, k = 40-H <= 18"),
  BUT PROVENANCE also says "every one with a passed real-swept holdout" —
  gen4's "never swept by anything" is true only at n=40, false for the RULE.
ABOUT TO: step 2, read docs/proofs/diagonal-law.md for actual proved reach
DONE: step 2 -> diagonal-law.md THEOREM is "for every k >= 0", onset n >= 2k+1.
  k<=3 in the header is the CHECKER's scope, not the theorem's. At n=40 the
  tightest cell is H=22 (k=18, onset n>=37): the WHOLE block is in-onset.
  Lead's premise refuted.
DONE: step 1b -> per-height shares computed (desk arithmetic on triangle.txt).
ABOUT TO: step 3/4, establish the derivation chain for each P_k and which
  real swept cells the block actually depends on.
DONE: step 3/4 -> the block reduces to 30 named real-swept anchor cells
  (polyplets/PROOF-STATUS.md, Grand tier). Lean COVERS k<=18 = exactly this
  block; gen4's "outside the Lean theorem's scope" is inverted.
ABOUT TO: step 5/6, cost arithmetic on the residual anchors
DONE: step 5/6 -> cost table filed, r4-tallband.md §5. Tier 1/2 = 2.31866% at
  0 marginal thread-hours; Tier 3 (H=22, 1.82621%) gated on T(38,20), no route.
DONE: step 7 -> R4-TB-01..04 appended to results/r4/queue.md
DONE: all steps. Deliverable complete.
