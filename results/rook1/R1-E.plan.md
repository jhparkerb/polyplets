# R1-E plan — queue row B1: does the route need full ab-initio P_k, or only bounded-depth slices?

2026-08-13. Wave-3 dispatch off the queue. Scout, desk-only.

## The question, one sentence

Does the a(40) recompute route (kink sweep H ≤ 19 + P_k for k = 10..19 + closed
depth-1 correction at k = 20) consume the *full* ab-initio weight DP for
k = 10..19, or only values/coefficients that live in the exactly-known
bounded-depth slices (depth 1 proved, depths 2–4 exact) — i.e. was gate 0's
kill (g ~ 20/level for full P_k) aimed at a harder object than the route
requires?

## Steps

1. Read `docs/proofs/grand-form.md` — what a "wired P_k closed form" is, and
   what data parameterizes it (depth structure, number of coefficients, where
   they come from). Produces: statement of what P_k-as-consumed-by-assembly is.
2. Read `orchestrator/sweep.go` (diagCoeffTable and its consumers) — what the
   assembly actually reads per k. Produces: the concrete data shape.
3. Read `results/ns_a40/PROVENANCE.md` — how H22–H40 was produced from the
   k ≤ 18 closed forms; confirm which k band n = 40 consumes and at what depth.
4. Read `results/depth-tower-bivariate-dead-end.md` + severance records
   (`results/severance-w1-anchor-cut.md`, depth-1/2-4 exactness records) — which
   depths are exact/closed, and crucially: what depth does the assembly need at
   each k for n = 40? Depth needed is a function of n and k (how far below onset
   row 40 sits at height k+? — check the triangle-tower "row-40 H=15..19 below
   onset" record).
5. Verdict, one of the three chartered forms; if bounded-depth, state the right
   cost object and the measurement gate 0 should run.

## Stop conditions

- Any of the three verdicts reached → file, file ≥2 successor queue rows
  different in kind, close B1, stop.
- A load-bearing file missing or contradictory → NOT ESTABLISHED with the
  specific blocker named.

## What each step writes

Findings appended to `results/rook1/R1-E.md` as they exist; ABOUT TO / DONE in
`results/rook1/R1-E.progress.md` around every step.
