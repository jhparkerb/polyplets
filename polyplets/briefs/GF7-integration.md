# GF-7 — Integration, audit, documentation

Read first: `polyplets/GRANDFORM-PLAN.md`; the reports of GF-1..GF-6 (ask the
orchestrator); `polyplets/PROOF-STATUS.md`; `polyplets/README.md`;
`docs/proofs/grand-form.md`.

## Deliverables

1. **Root imports**: add the `Polyplets.Grand.*` modules to
   `polyplets/Polyplets.lean` (alphabetical, matching style). Full
   `lake build` green from clean elaboration (`lake build` after
   `touch`-free incremental is fine; do NOT wipe `.lake`).
2. **Axiom audit**: a `Polyplets/Grand/Audit.lean` (or extend
   `Sanity.lean` — match house preference, check how `Sanity.lean` is used)
   with `#print axioms` for: `d_mu_rec`, `T_staircase`, `grand_form`,
   `lead_coeff_25`, `P16_grand_of_banked`, `mu_one`. Record the outputs
   verbatim in PROOF-STATUS (see 3). Expected:
   - `d_mu_rec`, `T_staircase`, `grand_form`: `[propext, Classical.choice, Quot.sound]`
   - `mu_one`, `lead_coeff_25`: + `Lean.ofReduceBool`
   - `P16_grand_of_banked`: + whatever `P3_pinned` carries (chunked
     native_decides) — via the level-3 anchor discharge.
3. **PROOF-STATUS.md rewrite** (surgical, keep history): new section "Grand
   form (staircase route)" summarizing: the μ-recursion & staircase theorems;
   `grand_form` UNCONDITIONAL; `P<k>_grand_of_banked` k = 1..16 with 2
   real-swept cells per level (26 hypotheses at k = 16, all H ≤ 18);
   **the PARTIAL/PREDICTED tier of Pin.lean is superseded** — state
   explicitly that k = 12..16 no longer rest on predicted points, and that
   k = 10..11's wired-cell hypotheses (`T 31 20` etc.) are also superseded;
   leading coeff 25^k/k! + deg = k now proved (Shape's deferred stretch
   closed). Update the "What is proved vs out of reach" section accordingly.
   Do NOT delete the Pin.lean tiers or their documentation — mark them
   historical/superseded, kept for cross-validation.
4. **README.md**: one paragraph + build note for the Grand modules.
5. **docs/proofs/grand-form.md**: append a short "Formalization" note:
   formalized 2026-MM-DD in `polyplets/Polyplets/Grand/`, staircase
   architecture (sequence form), axiom audit summary, pointer to
   GRANDFORM-PLAN.md.
6. **Oracle re-run**: `python3 experiments/staircase_check.py` and
   `python3 experiments/grand_form_check.py` still ALL PASS (no repo drift).
7. **Gate**: `rg -n "sorry" polyplets/Polyplets/` returns nothing;
   linters green.

## Out of scope (do NOT do)

- No push. No changes to `orchestrator/`, `docs/proofs/*.md` beyond item 5,
  no changes to `Pin.lean` itself, no HANDOFF.md edits (orchestrator does
  those at merge), no toolchain/mathlib changes.

## Done criteria

Full green build; audit outputs recorded; docs updated. This is milestone 3
— the orchestrator merges `lean-grandform` → master and closes the goal.
Commit `lean-gf: integration — imports, audit, PROOF-STATUS`.
