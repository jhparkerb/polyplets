# Fault-injection / mutation testing of the cross-checks

Purpose: a wall of passing checks is ambiguous — it could mean "correct" or
"vacuous." This demonstrates the check suite has **discriminating power** by
planting deliberate bugs and confirming the checks reject them, and records each
mutant's **first-divergence n** (the depth a check must reach to catch it). Real
source is untouched; mutants are built from /tmp copies.

Oracle: totals must match A006770 (fixed polyplets) and the two methods
(generation `g2`, transfer matrix `tma`) must agree; the rook/bishop slice must
match A001168.

## Results (run to n=10)

| mutant | engine | planted change | outcome | first-divergence n |
|---|---|---|---|---:|
| M3 | g2 | count each animal twice | **killed** | 1 |
| M1 | g2 | drop NE diagonal from king adjacency | **killed** | 2 |
| T2 | tma | closure too lax (1 → ≤2 components) | **killed** | 2 |
| T1 | tma | prune off-by-one too tight (`>` → `>=`) | **killed** | **10** |
| M2 | g2 | reorder offsets (count-preserving) | **survives** (equivalent) | — |
| control | g2, tma | none | matches truth | — |

All planted *errors* were caught; both real engines match truth (control).

## What the first-divergence column tells us

- **Blunt bugs die immediately** (n=1–2): double-counting, wrong adjacency, wrong
  closure. Any check at all catches these.
- **Subtle bugs need depth.** The prune off-by-one (T1) produces *correct* counts
  through n=9 and only undercounts at n=10 — a check suite shallower than n=10
  would silently pass it. This locates the size-budget prune's correctness as
  "empirically pinned only at n≥10." Deeper prune bugs would bite only at larger
  n, i.e. need deeper checks — and any prune fault that first bites beyond the
  feasible check range is precisely the code that can only be established by
  *proof*, not by running. (This is the bridge to the formal-verification scoping
  question: mutation depth partitions the code into empirically-pinned vs
  must-prove.)
- **The equivalent mutant (M2) is the honest survivor.** Offset order does not
  change the count — a genuine algorithmic invariant (each fixed animal is
  generated once regardless of neighbour-visit order), not a coverage gap. Its
  survival shows the suite isn't passing everything by luck: it passes exactly
  the changes that *should* preserve the count and fails the ones that shouldn't.

## Cross-method check fires too

Both tma mutants (T1, T2) also disagree with the *real* generation engine
(Method A), so the two-independent-methods check independently rejects them —
not only the external-sequence check.

## For the paper

One line for the validation section: "We confirmed the cross-checks have
discriminating power by fault injection — every planted error is rejected (by
both the external-sequence and two-method checks), with the size-budget prune's
correctness pinned at depth n≥10; the sole surviving mutant is a provably
count-preserving change."
