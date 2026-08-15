# Birthright — state and prove B1's cancellation identity

Brief written 2026-08-14 (Fable, in-session). Thread name: **Birthright**.
One agent, desk-scale. This executes Tier 1 of `docs/b1-closure-plan.md` §7:
the mathematical heart of the Motley/B1 second source, which today rests on a
C++ comment plus a small-board probe and **has never been written down in
closed form in this repo**.

## The object

The B1 engine (banked source `results/cutcount_b1/cutcount_b1.cpp.59e90660`;
the 80-line core is `slot`, `canon`, `gather`, `shifted`, `successors`, lines
93–173) claims to compute

    A_n(q) = Σ_{S ⊆ strip, |S| = n} q^{c(S)}   exactly in Z[q]/(q²),

with `c(S)` = number of king-connected components of `S`, and extracts
`T`-type counts as the linear coefficient `[q¹] A_n(q)`. The DP never decides
connectivity: it carries the colour-coincidence partition of the last H+1
cells in scan order. Its transition rule, verbatim from `successors`:

- a cell king-adjacent (within the window) to **two or more distinct-colour
  blocks** contributes weight 0 (the occupied branch is dropped);
- a cell adjacent to **exactly one** block joins it, weight 1;
- a **free** cell (no adjacent block in the window) either joins ANY live
  block — including blocks it does not touch — at weight 1 each, or takes a
  fresh colour at weight `q − b`, where `b` = number of live blocks in the
  window at that moment. Blocks expire when their last cell leaves the H+1
  window, so colours get reused and `b` counts *live* blocks only.

Weights are carried as `m0 + m1·q` (the ring Z[q]/(q²)). Component-birth
factors do not individually vanish mod q² on disconnected sets —
`(q−b₁)(q−b₂) ≡ −q(b₁+b₂) + b₁b₂` — so the correct count emerges only from a
cancellation summed over all colour assignments. **That summed cancellation is
the identity to state and prove.**

## Goal

A standalone proof document, `docs/proofs/cutcount-identity.md`:

1. **The statement, in closed form.** A theorem in the language of finite
   cell sets and king-connectivity (the same objects as `Polyplets/Defs.lean`'s
   `kingAdj`/`KingConnected` — cite the vocabulary, but this is a paper proof,
   NOT a Lean task). It must define the colouring model precisely: what a
   colour assignment is, what "live block" and expiry mean, what weight a
   configuration carries, and in what ring; then assert that the weighted sum
   over all configurations with underlying set S equals `q^{c(S)} mod q²`.
   Getting the statement right is the announced risk ("the identity has to be
   stated correctly before it can be proved") — derive it from the code, not
   from the plan's paraphrase, and flag any place where they differ.
2. **The proof.** Pure combinatorics, no program in it. Expected shape: a
   per-set identity — fix S, sum over colourings — probably by induction over
   the scan order or by an involution/telescoping on colour choices; mod q²
   only the constant and linear terms survive, and the free-cell "join any
   live block" branch is what makes the b-dependence cancel. If the clean
   statement requires a hypothesis you cannot discharge (e.g. a window-size
   condition tied to H+1 and king reach), state it explicitly as a condition
   and prove the conditional theorem — do not paper over it.
3. **Separation of tiers.** Tier 2 (the window DP with `canon`/`shifted`
   realises the sum — locality, sufficient statistic, invariants) is NOT in
   scope beyond a short remark delimiting it; §7 already prices it as routine.
   Lean formalization is a later campaign. Keep to Tier 1.

## Verification (required, but subordinate to the proof)

A small script, `experiments/birthright_identity_check.py`, that checks the
*identity as stated* — not the engine — by brute force at small sizes: for
every subset S of small boards (e.g. all boards up to ~16 cells across a few
H), enumerate the colouring model of your statement directly, sum weights in
Z[q]/(q²), and compare against `q^{c(S)}` with c(S) from flood fill. Include a
RED control that provably fires (e.g. drop the clash-zeroing rule or miscount
live blocks and watch it break). Note: the engine's header cites
`experiments/probe_cutcount_dp.py`, which is not in the tree — your script
re-establishes that validation under the theorem's own definitions; record
the missing-file fact in the doc.

## Required reading

1. `results/cutcount_b1/cutcount_b1.cpp.59e90660` — the whole header comment
   and lines 93–173. This is ground truth for the rule.
2. `docs/b1-closure-plan.md` §7 — scope, tiers, the sequencing argument.
3. `experiments/cutcount/cutcount_b1_probe.cpp` — the probe variant.
4. `docs/motley-plan.md` (what B1/Motley is; the rule never changes on any
   rung) and `results/motley-step0.md` (the rule's production validation).
5. `Polyplets/Defs.lean`, `Polyplets/Graph.lean` — vocabulary only.

## Hard constraints (violating any of these fails the task)

- **No project code executes on gympie. None.** Hard ban, 2026-08-14. The
  verification script runs on **ayr** over ssh: `scp` it to
  `~/tmp/birthright/` on ayr and run it there. Pure python3 stdlib only —
  the check needs nothing else. Keep it under 5 minutes of runtime (shrink
  the board list, not the rigor); if it genuinely needs more, stop and
  report the price.
- **Never** `pkill`/`killall`/`pgrep`; `ps` then `kill <pid>`. No sleep-loop
  polling.
- **Every number quoted in the doc must be printed by the shipped script.**
- **No commits.** Leave everything in the working tree for review. Do not
  touch `paper/` (technical-report.tex is READ-ONLY, hard rule); do not edit
  existing results/docs files — integration is the caller's. The working
  tree carries jasonp's own uncommitted changes (`docs/rook-parity.md`
  deleted, `results/coin-lift-g2.md` modified) — do not touch or "restore"
  those.
- No pompous naming: it is "the cancellation identity" or "the cut-count
  identity", never a "law" or "theorem of X".

## Deliverables

- `docs/proofs/cutcount-identity.md` — statement, proof, the conditional
  hypotheses if any, a short Tier-2 delimitation remark, and a limits ledger:
  what is proved, what is checked-not-proved, weak points conceded up front.
- `experiments/birthright_identity_check.py` — the RED-controlled brute-force
  check of the statement, with its ayr run transcript quoted in the doc.
- Final report back: the identity as one displayed formula, whether the proof
  closed clean or needed conditions, and anything in the code that
  contradicts §7's description of the rule.
