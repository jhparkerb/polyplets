# R1-B plan — P_k tower feasibility (scout)

2026-08-13. Question: is the ab-initio P_k tower feasible, and what is g (the
ab-initio P_k cost growth)? Gate 0 of docs/rook-parity.md.

Steps, in order:

1. Read `results/severance-w1-anchor-cut.md` (esp. §Ceiling) and any adjacent
   severance logs/records for per-k wall time and RAM at k ≤ 9.
   Produces: the table of MEASURED (k, time, RAM) points and their sources.
2. Fit g over the k range the records actually support — separate fits for
   time growth and state/RAM growth if both exist; residuals stated. Label
   every number MEASURED (which log) or EXTRAPOLATED (how far).
   Produces: g with basis, filed to R1-B.md.
3. Read the verdict off the pre-registered partition in `docs/rook1-brief.md`
   (g ≤ 3 parity / 3 < g < b² beats-incumbent-only / g ≥ b² kill; current best
   b = 2.42 ⇒ boundary 5.856, but report g itself so any b lands).
   Produces: verdict paragraph in R1-B.md.
4. Survey the state-space reduction the k = 10 wall requires: state the
   structural requirement (what dominates the 53 GB at k = 9 and what must
   shrink), then check `docs/middle-kingdom-plan.md`, existing results/, docs/,
   and build tree for anything that already bears on it. No candidate list
   given; no tool named as new without a grep first.
   Produces: §Survey in R1-B.md.
5. File ≥ 2 successor queue rows different in kind; run
   `./scripts/check_receipts.sh`; stop and report g + verdict + any job
   request to the lead.

Stop conditions: question answered and filed; or a stop instruction (write
partials first, label them). Desk-only: no compute beyond seconds-scale reads;
anything larger becomes a job request per docs/r3-job-dispatch.md.
