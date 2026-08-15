# Ghost Ship — sealed answer key (§7 item 3)

Sealed 2026-08-15, before launch. Grader-only; excluded from the sandbox.
The rungs are the real ladder of 2026-07-12, verified against the commits.

## The rungs

- **Rung 1** — switch the statistic: count convex king animals by
  (semi)perimeter instead of area, and establish tractability there
  (court: `60b6ac5`, 18:23, "by perimeter king convex polyplets are
  D-finite"; 24 court-minutes from the cut). Grade a session at rung 1 if
  it counts by perimeter/semiperimeter AND produces evidence of
  D-finiteness/algebraicity (recurrence found, GF derived, or a
  guessed-and-checked ODE) — not for merely proposing the switch. The
  perimeter *hint* is on disk in the slice (see SANDBOX.md C4); the rung
  measures acting on it.
- **Rung 2** — solve the column-convex subfamily by Temperley-style
  functional equation and identify it (court: `3afca73`, 19:24,
  "column-convex polyplets solved via Temperley -- rediscovers A187077").
  Grade at rung 2 for a derived GF/recurrence whose terms match A187077,
  with or without the OEIS id (OEIS read-only is allowed; the id is the
  cheap half, the derivation is the rung).
- **Rung 3** — refute the A187077 equivalence comment by measurement
  (court: `37ce404`, 20:51: hex brute with A001207 control shows
  row-convex polyhexes = A059716 ≠ A187077; the king h+h′+1 vs hex h+h′
  placement count explains the gap). Grade at rung 3 only for the
  measured refutation with a control, not for voicing suspicion.

Graded outcome: highest rung reached, and at which session.

## In-scope subtopics (claims here count toward rungs)

Convex/HV-convex king animals under any statistic; column-convex and other
convexity-relaxation subfamilies; perimeter/semiperimeter statistics;
D-finiteness or algebraicity of those counting sequences; OEIS
identification and cross-checks of sequences the sessions compute.

## Out-of-scope (graded as ordinary claims, never as rungs)

Area-statistic asymptotics and μ-refinement beyond the banked 38 terms;
λ strip bounds; the upper-bound certificate; directed/multi-directed
animals; defect-gas / diagonal-law extensions. These are adjacent banked
territory — work there is graded by the claim metrics and the
re-derivation list only.

## Grader notes

- The slice ships `docs/proofs/polyplet-upper-bound.md` stating
  **λ ≤ 9.3153**; the post-cut record corrects this to 9.3154. A session
  that catches the rounding has made a genuine novel claim (not
  READ-OFF, not a re-derivation).
- Live-OEIS drift: any rung-2/3 claim resting on OEIS content that
  post-dates 2026-07-12 is bucketed READ-OFF per §2.
