# polyplets

Lean 4 formalization of the diagonal structure of the polyplet height
triangle `T(n, H)` (fixed king-connected animals by size and bounding-box
height): the peeling recursion (`Peel.lean`), the diagonal-law shape theorem
(`Shape.lean`), explicit production-polynomial pinning (`Pin.lean`,
historical tiers), and the **grand form** via the staircase route
(`Polyplets/Grand/` — `d_mu_rec`, `T_staircase`, the unconditional
`grand_form`, `lead_coeff_25`, and `P<k>_grand_of_banked` for k ≤ 18 from
two real-swept cells per level). Status and axiom audits: `PROOF-STATUS.md`;
the Grand modules' plan and task briefs: `GRANDFORM-PLAN.md`, `briefs/`.

Build: `lake exe cache get` (once, for Mathlib), then `lake build`. The heavy
k=3 weight enumeration (`Weights3Heavy.lean` and its fifteen
`native_decide` chunk modules) **is** in the default target's closure —
`Polyplets.lean` → `Grand.PinGrand` → `Weights3Heavy` — so a cold `lake
build` spends ~37 min on it once and is incremental thereafter. Mathlib's
cache does not cover it (it is this project's own code). See
`PROOF-STATUS.md`.

The tree is **sorry-free** (34 `.lean` files, ~10.8k lines) and every
axiom-footprint claim is enforced by `#guard_msgs` in
`Polyplets/Grand/Audit.lean`, so a drifting axiom set fails the build.
