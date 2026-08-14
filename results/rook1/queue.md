# Round-1 idea queue — append-only

Opened 2026-08-13 by the lead, before the first spawn. This is the round's only
inter-round carrier: round 2's brief may cite rows here and receipts, and
nothing else. A sentence from anyone's synthesis with no row behind it is not a
launchable premise.

**Append-only. Never revise a row; add a new one that supersedes it, naming the
row it supersedes.** Every agent that closes a candidate files at least two
successor rows, different in kind from what it killed — not parameter tweaks.
Half-formed rows are wanted. Cross-lane rows are wanted. A pruned near-miss goes
here; it never goes into a silent cap.

Rank order: rows that move a gate of `docs/rook-parity.md` outrank rows that
close a door, which outrank rows that open a question.

Close protocol: the queue closes only after the census confirms every agent
stopped or explicitly handed off. A job still in flight gets an IN FLIGHT row
with a waiter named. Anything filed after close becomes round 2's first rows.

Status vocabulary: OPEN, CLOSED, KILLED, JOB-REQUESTED, IN FLIGHT, SUPERSEDED.

| row | filed by | kind | claim or question | cheapest thing that kills it | status |
|---|---|---|---|---|---|
| K1 | R1-K | question | Which of the three per-height cost-growth numbers is the kink engine's real one: cpu ratio 2.98 (PROVENANCE:16,19), record ratio ~2.7 (PROVENANCE:20), frontier 2.6 (kink-carry:69)? R1-A's fit should say which quantity the per-n base comes from | R1-A's n=24..30 fit with residuals distinguishing cost from records from states | OPEN |
| K2 | R1-K | claim | "diagonal-splice beta >= 2" (rook-parity.md:86) is asserted, never derived in-repo; the transport kill for that family leans on it | R1-D derives the blowup or exhibits a beta < 2 splice, either way replacing the assertion | OPEN |
| K3 | R1-K | question | If R1-A's reconciliation lands on 1.73 as the incumbent's true per-n cost base, the incumbent is already at rook parity and the goal's whole weight shifts to gate 1's measured clause — does the goal file need a contingency paragraph for that outcome? | R1-A's fit landing anywhere other than ~1.73 | OPEN |
| K4 | R1-K | chore | Project docs stale at n=56 for the polyomino record (goal says so, rook-parity.md:151; confirmed n=70 in papers/counting_polyominoes_revisited.pdf) — sweep and fix the stale mentions | grep for "56" record mentions coming back empty | OPEN |
| B1 | R1-B | question | Does the a(40) recompute route need full ab-initio P_k at k=10..19 at all, or only the values/coefficients in the exactly-known depth slices (depth 1 proved, 2-4 exact, results/depth-tower-bivariate-dead-end.md)? If the H<=19 sweep + closed depth corrections consume only bounded-depth data, the tower's g becomes the depth-slice cost, not the 20x/level weight-DP cost — a different object, not a faster DP | desk: trace the assembly chain (docs/proofs/grand-form.md, orchestrator/sweep.go diagCoeffTable) and count which parts of P_k the k=10..19 band consumes at n=40 | OPEN |
| B2 | R1-B | question | Is 20x/level king-specific? Rook connectivity is local (bbox theorem, docs/rook-parity.md:48); the rook-side analog of the cluster-weight stack DP may have polynomially smaller state maps. If yes, the tower route lives on the rook side even though it died on king | count analogous stack-DP states for rook at k=4..6 (seconds-scale script; job row if larger) | OPEN |
| B3 | R1-B | question | Is the level-k cost concentrated in one composition family ("one huge stack", severance-w1-anchor-cut.md:47) or uniform across the 2^(k-1) compositions? If concentrated, a reduction need only solve one 1-parameter family, which may carry its own recursion — the obstruction would then be about the instance, not the family | per-composition state/peak profile at k<=6 from build/severance_w1 with counting instrumentation (short dalby job; field block on request) | OPEN |
| B4 | R1-B | chore | Per-level timed C++ run k<=8 (minutes, dalby, build/severance_w1) to upgrade g's label from MEASURED-in-spec-implementation (Python, defect-gas.md:242) to MEASURED-in-shipped-implementation. Cannot change which partition row fires (results/rook1/R1-B.md §3): measured lower bound 8.15 already exceeds b^2 = 5.856 | dispatch it; or decline because no decision depends on it | OPEN |
