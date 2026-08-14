# R1-E — queue row B1: does the route need full ab-initio P_k?

2026-08-13. Scout, wave 3, desk-only. Question: does the a(40) recompute route
need the full ab-initio P_k weight DP at k = 10..19 (the object gate 0 killed
at g ~ 20/level), or only data living in the exactly-known bounded-depth
slices?

## Verdict

**The route needs only bounded-depth slices plus its own sweep's cells. The
full ab-initio P_k weight DP is consumed nowhere in the assembly.** Gate 0's
kill was aimed at an object the route does not require. This does NOT make the
route alive at parity: with the weight DP removed, the route's only remaining
exponential is the H ~ n/2 kink sweep itself — the incumbent's own Phase A —
so the corrected cost object is the sweep base b (R1-A's 1.7266, queue row A0)
plus a per-level anchor cost that is small and measurable. Details and the
right gate-0 measurement in §4-5.

## 1. What the assembly actually reads (the trace)

- **The wired band consumes polynomial VALUES, two constants per level.**
  `orchestrator/sweep.go:2063` (diagCoeffTable, j = 1..19) holds Horner
  coefficients; the consumer (`orchestrator/sweep.go:2349`) evaluates
  T(n,n−k) = P_k(n)·3^(n−1−3k). At n = 40 the band H = 22..40 reads P_k(40)
  for k ≤ 18, H = 21 reads P_19(40) (`results/ns_a40/PROVENANCE.md:25-26`,
  30-32), and the route replaces the H = 20 sweep with P_20(40) minus the
  depth-1 defect (`docs/rook-parity.md:65-67`).
- **Each level is two rational unknowns, not a weight enumeration.**
  Grand form (`docs/proofs/grand-form.md:160-166`, Corollary 1):
  P_k(n) = known_k(n) + a_k + b_k·n, with known_k determined by levels < k.
  Given the Lean shape theorem, ANY two exact in-onset cells on diagonal k pin
  (a_k, b_k) by a nonsingular 2×2 solve. That is exactly how production built
  the table — theory plus two real-swept cells per level, e.g.
  `orchestrator/sweep.go:2094-2101` (P_11: two cells) — not by running the
  weight DP.
- **The weight DP (cluster weights of surplus ≤ k) is one SOURCE for
  (a_k, b_k), not the consumed object.** It is the source severance built for
  k ≤ 9 (`results/severance-w1-anchor-cut.md`) and the source gate 0 priced
  at g ~ 20/level. The assembly cannot tell where (a_k, b_k) came from.

## 2. The bounded-depth alternative source, from in-tree records

- **Below-onset columns are finite bounded-depth data.**
  `results/onset-defect-depth1-closed.md` §1: the entire below-onset part of
  column k is k+1 integers, and the depth-j defect is the coefficient
  D_j(k) = [z^(k+1−j)]D(z). A below-onset cell at depth j sits at
  n = 2k+1−j, i.e. H = k+1−j.
- **Depths 1..4 are closed, ab initio, with no P_k and no triangle data in
  the derivation.** Depth 1: derived via the kernel method, D_1 exact to
  k = 200 in 42 s (`results/onset-defect-depth1-closed.md` §2-3). Depths
  2-4: exact identity over excess ≤ j−1 ≤ 3 weight families
  (`results/onset-defect-depths234.md`), matched against every banked cell
  k ≤ 19 per depth (`results/onset-defect-depths234.md:34-38`, gate
  `experiments/severance_w3_gate.py`). The e = 3 family table to K = 19 cost
  146 s (`results/severance_w3_families_K19_e3.txt`).
- **Therefore a below-onset swept cell at depth ≤ 4 converts to one exact
  linear equation in (a_k, b_k)**: T(n,n−k) − defect = P_k(n)·3^(n−1−3k),
  with the defect known in closed form.

## 3. Cell accounting at n = 40, H ≤ 19 sweep

Depth-j cell of level k lives at H = k+1−j; the sweep supplies every cell
with H ≤ 19. Per level:

| k | pin cells available inside H ≤ 19 | source of the conversion |
|---|---|---|
| ≤ 9 | not needed | ab-initio weights already banked, `results/severance-w1-anchor-cut.md` |
| 10..17 | two in-onset cells at H = k+1, k+2 ≤ 19 | grand form 2-cell solve alone, no defect data |
| 18 | in-onset H = 19 (n = 37) + depth 1 (n = 36, H = 18); depths 2-4 spare | closed D_1 |
| 19 | depths 1..4 at H = 19,18,17,16 (n = 38..35): two pin, two holdout | closed D_1, D_2 |
| 20 | depths 2,3,4 at H = 19,18,17 (n = 39..37): two pin, one holdout | closed D_2..D_4; then T(40,20) = P_20(40) − D_1(20)·3-power |

Every level the n = 40 assembly touches is pinned from cells the route's own
H ≤ 19 sweep produces, converted where below-onset by depth ≤ 4 closed forms.
Depth ≥ 5 is consumed nowhere. The full surplus-k composition DP — the 53 GB
k = 9 / 20x-per-level object — is consumed nowhere. Generalizing, with
depths ≤ 4 the pinnable band from a sweep capped at H0 reaches k = H0+2
(two cells need j ≥ k+1−H0 and j ≤ 4), and covering the formula band
k ≤ n−H0−1 needs H0 ≥ (n−3)/2 — the sweep stays at half height, exactly the
route's H ≤ 19 at n = 40.

Caveats, honestly:

- Depth-slice exactness is machine-matched at k ≤ 19 per depth
  (`results/onset-defect-depths234.md:34-38`); use at k = 20 extends the
  derived identity one level past its verification. The spare cells in the
  table above are in-sweep holdouts that make that extension fail-closed.
- The e = 3 family table stops at K = 19; K = 20 is a re-run of
  `cpp/severance_w3_families.cpp` (146 s at K = 19), a small job.
- The depth identities are derivation-plus-exact-match evidence
  (`results/onset-defect-depth1-closed.md` §Limits), not Lean; the 2-cell pin
  is the Lean `P<k>_grand_of_banked` pattern with fresh cells as hypotheses.
- No circularity: pins come from H ≤ 19 cells, the formulas produce H ≥ 20
  cells; no cell certifies itself, and nothing from the banked run enters —
  the goal's "no anchor cells or intermediate values from the banked run"
  (`docs/rook-parity.md:12-13`) is satisfied literally.

## 4. What the right cost object is

The route's cost decomposes as:

1. **The H ≤ ~n/2 kink sweep** — the dominant, exponential term. This is the
   incumbent's own Phase A (6.3 h of the a(40) run,
   `results/ns_a40/PROVENANCE.md:12-13`); its per-n base is R1-A's b (A0:
   b = 1.7266 = sqrt(R), R = 2.9813 and still rising — queue row A2). Note
   what dropped out: phases B and C, the H = 20, 21 solo sweeps that were 84%
   of the a(40) cpu, are replaced by the depth-pinned band — but for growing
   n both the incumbent and this route sweep to half height, so this is a
   constant-factor deletion at fixed n, not a base change.
2. **Per-level anchor cost**: the excess ≤ 3 family tables to K ~ n/2
   (anchor: 146 s at K = 19, 10 threads,
   `results/severance_w3_families_K19_e3.txt`) plus exact rational assembly
   (seconds, `experiments/severance_w3_depths.py` scale). No 20x/level term
   appears; the e = 4 wall measured in
   `results/depth-tower-bivariate-dead-end.md:66-73` is never hit because
   depth ≥ 5 is never consumed.

**What gate 0 should have measured** (and what a re-run against the right
object is): the growth ratio of the e ≤ 3 family DP in K over K = 19..25 —
if it stays far below R = b², the anchor side is free and the route's base is
exactly the sweep's b. That is a minutes-scale dalby job, not a 7.4-year
tower.

## 5. What this does and does not change

- **Gate 0's kill of the TOWER stands**: full ab-initio P_k past k = 9 is
  dead at g ~ 20/level, and nothing here revives it. What falls is the
  premise that the route needs the tower.
- **No parity rescue is claimed.** The corrected route's base is the sweep's
  b, so the parity question collapses onto queue row A2 (does R converge
  below 3 or cross it) — the route can never beat the incumbent's base,
  because its exponential IS the incumbent's sweep. Against the goal's
  charter, deleting the 84% band is a constant-factor improvement, which
  `docs/rook-parity.md:11-12` rules out of scope on its own.
- **One real upgrade to A0's conditionality**: R1-A's "incumbent already at
  rook parity as operated" was conditional on the fitted-P_k treadmill, whose
  fits historically consumed banked anchor cells. This trace shows the
  treadmill can self-anchor from the run's own half-height sweep — making
  "as operated" a legitimate end-to-end method under the goal's
  no-banked-values test, not a mode that quietly leans on the previous run.

## Queue actions

Closed B1 (verdict above). Filed successors E1, E2, E3 — see
`results/rook1/queue.md`.
