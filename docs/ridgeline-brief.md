# Ridgeline — derive the depth-amplitude family at the onset ridge

Brief written 2026-08-14 (Fable, in-session). Thread name: **Ridgeline**.
One agent, desk-scale. This is the recorded pickup point of
`results/depth-tower-bivariate-dead-end.md` ("What survives"), executed.

## Goal

Derive — not fit — the near-onset depth amplitude family. The defect at depth
`j` below onset behaves as `D_j(k) ~ A_j · 9^k · k^(j−3/2)` (θ_j = j−3/2,
measured j ≤ 7). The four-point fit (j ≤ 4) suggests

    Σ_j A_j t^j = (√6/27) · t / √(1 − 50t/81),
    i.e. A_j = (√6/27)(25/81)^(j−1) · binom(2j−2,j−1)/2^(j−1),

but at j = 5 the conjectured ratio 35/8 sits OUTSIDE the measured bar while
118/27 sits inside (`results/onset-defect-law.md` §2), more data is
structurally unreachable (the extraction is capped at k ≤ 18 by P_k; the
ab-initio route at excess 4 is a many-hour wall), and the dead-end note is
explicit: **the only path that settles this is a derivation.**

Acceptable outcomes, in descending order of value:

1. The double-scaling function at the onset ridge derived exactly, settling
   the A_j family (confirming the √-form, or replacing it).
2. A derivation that the scaling function is NOT algebraic (e.g. the layer
   exponent is 1/3 → Airy class) — that is a real answer, record it.
3. A precisely characterized obstruction: which limit fails to commute, which
   family sum diverges, what the honest state of the j = 5 question is after
   the attempt. A well-mapped wall is a valid deliverable; more fitting is not.

## Method (the recorded sketch — start here, deviate with reasons)

Onset double-scaling limit: local expansion of the depth-1 kernel
`D(u) = u² − y(1+u+u²)²` near its branch point `y = 1/9`, with depth as the
slow coordinate. The depth-j defect assembles exactly from excess-graded gap-walk
families (total row excess `Σ(s_i−2) ≤ j−1`) — identities (C)/(D) in
`experiments/severance_w3_depths.py`, closed against all banked cells at
depths 2, 3 (`experiments/severance_w3_gate.py`). Depth 1's own derivation —
kernel method, two quadratic branches in `s = √y`, `A² = (1−3s)(1+s)`,
`B² = (1+3s)(1−s)`, dihedral closure — is fully executed in
`experiments/severance_w2_kernel.py` with gate `severance_w2_gate.py`; it is
the pattern to emulate one depth up. The measured `(25/81)` per-depth factor
and the central-binomial family are the shape your local analysis must either
produce or refute.

Guard against confirmation bias: derive the local factors first, only then
compare with the conjectured family. Do not steer intermediate choices by the
target.

## Required reading, in order

1. `results/onset-defect-depth1-closed.md` — §2 (gap-walk identity), the §3
   DERIVED status block (kernel method), §6 (depth j ≥ 2 priced, the W3
   excess correction).
2. `results/depth-tower-bivariate-dead-end.md` — why the bivariate G is dead,
   what survives, why fitting is structurally over.
3. `results/onset-defect-law.md` §2 — the amplitude measurements and bars,
   especially the j = 5 ambiguity (35/8 vs 118/27).
4. `docs/onset-defect-handoff.md` §5 — the campaign's recorded failure mode.
5. `experiments/severance_w2_kernel.py`, `severance_w2_gate.py`,
   `severance_w3_depths.py`, `severance_w3_gate.py`, `depth1_gap_walk.py`.

## Ground truth for verification

- Exact `D_j(k)`: depths 2–3 from the W3 assembly; all depths at k ≤ 19 from
  the banked triangle − law (readers in `experiments/slope2_law_vs_truth.py`;
  data-format traps listed in `docs/onset-defect-handoff.md` §3 — read them).
- Depth 1 exact to k = 200 via `depth1_gap_walk.py`.
- Measured `A_j`, j ≤ 4, and the j = 5..7 bars in `onset-defect-law.md` §2.
- Any derived family must reproduce the DERIVED depth-1 constants exactly:
  rate 9, θ = −1/2, `C_1 = A_1 = √6/(27√π)`.

## Hard constraints (violating any of these fails the task)

- **No project code executes on gympie. None.** Hard ban, 2026-08-14. Author
  scripts here; run them on **ayr** over ssh. ayr's repo checkout may be
  behind — `scp` what you need to `~/tmp/ridgeline/` on ayr and run there.
  Pure python3 preferred; test `python3 -c "import sympy"` / `mpmath` on ayr
  before relying on either, and if a needed library is missing, STOP and
  report the exact install ask — no degraded workaround.
- Anything that could exceed 5 minutes: tmux window on ayr
  (`tmux new-window -t 0 -n ridgeline`), named on-disk script, PID recorded;
  wait with `tail --pid`, never a sleep loop. Nothing over 1 hour, period —
  if the honest cost is more, report the price and stop.
- **Never** `pkill`/`killall`/`pgrep`; `ps` then `kill <pid>`.
- **Every number you quote must be printed by a script you ship** in
  `experiments/` (the campaign was burned twice by shell-computed numbers).
  Verification scripts get a RED control that provably fires.
- **No commits.** Leave everything in the working tree for review. Do not
  touch `paper/` (technical-report.tex is READ-ONLY, hard rule), do not edit
  existing results/docs files — pointers and integration are the caller's.
  The working tree already carries jasonp's own uncommitted changes
  (`docs/rook-parity.md` deleted, `results/coin-lift-g2.md` modified) — do
  not touch or "restore" those.
- No external services, no OEIS submissions; read-only oeis.org lookups are
  allowed.

## Deliverables

- `results/ridgeline-depth-amplitudes.md`: the statement, the derivation (or
  the obstruction map), a verification table with every number script-printed,
  and a limits ledger — what is derived, what is verified-not-derived, what
  remains open, weak points conceded up front.
- `experiments/ridgeline_*.py`: the derivation's verification, RED-controlled.
- Final report back: verdict on the A_j family (confirmed / replaced /
  transcendental / wall), the one-line answer to "35/8 or 118/27 at j = 5",
  and anything you found that contradicts the notes you were pointed at.
