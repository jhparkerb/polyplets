# Motley — ensemble goal document

Plan: `docs/motley-plan.md`. Engine: `results/cutcount_b1/`, branch
`second-source`.

## Recommendation, stated first

**Do not convene an ensemble for this.** Motley's three rungs are a specified
engineering sequence with mechanical gates and no discovery content — the RAM
arithmetic is done, the prime shape is a banked decision, the gate battery is
written, and every step has a byte-for-byte oracle in the banked rows. Lanes
would duplicate work and add coordination cost against a task that one
executor can carry serially while dalby runs the compute.

This document exists so that if one is convened anyway — for wall-clock
reasons, or because Ticker Tape's arena wants a second pair of eyes — the goal
is written down rather than improvised.

## The goal

Close a(n) rule-independently for **n <= 37**, and reduce row 40's residual
band to three cells, by building three rungs on a frozen 80-line connectivity
core.

Done means: `a(n)` for n <= 37 reproduced by Motley from an in-tree
fail-closed binary with a gate receipt, matching the banked triangle byte for
byte, with the P_k levels those runs pin recorded and their holdout cells
checked.

## Kill conditions

- **Half Measure's measured H = 17 windows depart from the census ratio by
  more than 20%.** Every RAM projection above H = 17 rests on that ratio;
  if it breaks, stop and re-derive before Confetti.
- **The arena's measured overhead exceeds ~90 B/window.** Ticker Tape does not
  fit at 135 GB; re-plan rather than push.
- **Any RED passes, or any GREEN fails, in a width's gate battery.** No
  production column runs without a receipt.

## Lanes, if convened

| lane | scope | gate |
|---|---|---|
| **HM** | Half Measure: u128 typedef, fail-closed bound check, H=17 run | banked rows byte-identical H <= 16; H=17 windows vs census |
| **CF** | Confetti: width template + CRT driver + held-out-prime RED | brute battery at 6 board sizes per prime; banked rows |
| **TT** | Ticker Tape: check-split, flat arena, u16 prime table | arena differentially tested vs `unordered_map` at H <= 10, exhaustively |
| **GATE** | adversarial: plant defects, verify the battery fails closed | at least one defect the value ties alone would miss |

GATE is the only lane worth running concurrently with the others; it is also
the one lane an ensemble genuinely improves, because its job is to think of
defect classes the implementer did not.

## Standing constraints

- The 80-line connectivity core is **frozen**. Any diff touching `slot`,
  `canon`, `gather`, `shifted` or `successors` is out of scope and must be
  escalated, not merged.
- The 434-line reference engine is the specification; every rung reproduces it
  byte for byte wherever both can run.
- Compute runs on dalby, one core, in a named tmux window with a traceable
  PID. Ticker Tape's H = 19 is a multi-week single-threaded job — budget the
  whole loop, not one pass.
- No parallel frontier, no spill, no dense ranking. Those are the changes that
  cost auditability and no height in this plan needs them.
