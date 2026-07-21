# polyplets

Lean 4 formalization of the diagonal structure of the polyplet height
triangle `T(n, H)` (fixed king-connected animals by size and bounding-box
height): the peeling recursion (`Peel.lean`), the diagonal-law shape theorem
(`Shape.lean`), explicit production-polynomial pinning (`Pin.lean`,
historical tiers), and the **grand form** via the staircase route
(`Polyplets/Grand/` — `d_mu_rec`, `T_staircase`, the unconditional
`grand_form`, `lead_coeff_25`, and `P<k>_grand_of_banked` for k ≤ 16 from
two real-swept cells per level). Status and axiom audits: `PROOF-STATUS.md`;
the Grand modules' plan and task briefs: `GRANDFORM-PLAN.md`, `briefs/`.

Build: `lake exe cache get` (once), then `lake build`. The heavy k=3 weight
enumeration (`Weights3Heavy.lean`) is outside the default build; see
`PROOF-STATUS.md`.

## GitHub configuration

To set up your new GitHub repository, follow these steps:

* Under your repository name, click **Settings**.
* In the **Actions** section of the sidebar, click "General".
* Check the box **Allow GitHub Actions to create and approve pull requests**.
* Click the **Pages** section of the settings sidebar.
* In the **Source** dropdown menu, select "GitHub Actions".

After following the steps above, you can remove this section from the README file.
