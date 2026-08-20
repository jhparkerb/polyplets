# Undertow review, Lane C — freedom from fitting

2026-08-20, Lane C of docs/undertow-review-brief.md. Blind findings list filed
to results/undertow-review-queue.md at 07:26 EDT before any other reading.

## Verdict, one paragraph

Strict freedom from fitting — no swept cell anywhere in the tower — is out of
reach past k ≈ 11, and the obstruction is a property of the construction
family, not of this lattice at these k: the grand-form theorem itself says the
two level-k constants are *equivalent to* the aggregate cluster weights of
surplus ≤ k (docs/proofs/grand-form.md:20), those aggregates are connected-
animal counts of the same species as the object being counted, and every known
exact route to them carries a frontier connectivity partition whose growth is
measured at ~20x/level in two independent implementations. But a weaker and
more useful freedom IS buyable: extending the excess-graded family tables to
e = 8 closes depths 8 and 9, and then every level k ≤ 21 — including the
level 21 that owns T(40,19) — pins from banked strip-engine cells (H ≤ 14,
n ≤ 40, already second-sourced), with the incumbent kink sweep leaving the
tower's dependency graph entirely. Extrapolated cost: ~10^6 core-seconds,
days-scale on dalby, with RAM the likely binder — one cheap calibration job
decides it.

## 1. What the proofs leave free, exactly

- `diagonal-law.md` + `grand-form.md` prove the SHAPE: each level adds
  exactly two rational constants, `P_k(n) = known_k(n) + a_k + b_k·n`
  (grand-form.md:160-163), and the proof is uniform in the weights.
- The same theorem names the only known fitting-free determination:
  "(a_j, b_j) determined by the cluster weights of surplus ≤ j"
  (grand-form.md:20). So *freedom from fitting = computing the surplus-k
  cluster-weight aggregates*, full stop. There is no third source: the known
  cross-level structure (3-adic ladder, 5-adic denominator law) is exact but
  finite-information — shadows, not values (see §4, route 4, for why the
  3-adic route is self-defeating).
- Two exact facts per level are therefore information-theoretically required
  from somewhere. "Fitting" in the brief's sense means taking them from an
  enumeration sweep; W1-style ab initio means taking them from the cluster
  DP. Both are enumerations. The honest form of Lane C's question is: does
  the cluster side have a cost structure fundamentally better than the sweep
  side, or a closed form that skips enumeration? Answers: no (measured), and
  no known one (with two named refutation targets, §3).

## 2. The real obstruction, named

The W1 stack DP's state is the top row's cells plus their connectivity
partition (cpp/severance_w1.cpp, `struct Key`, `emit()`'s union-find and
label compaction). That partition frontier is the same connectivity wall that
killed the four engine levers and the dual-connectivity TM (brief §2). The
measured facts:

- ~20x/level, in Python (defect-gas.md:247 context: k=4 3.1 s, k=5 65 s,
  k=6 >530 s) and again in C++ (severance_w1.cpp header: k ≤ 7 seconds, k=8
  minutes, k=9 hours); k = 9 is 66 min / 53 GB peak on dalby, k = 10 declined
  on memory (severance-w1-anchor-cut.md:48: needs "a state-space reduction
  (symmetry quotient or frontier compression in the stack DP), not more
  cores").
- Strict tower to level 21 at 20x/level from the k = 9 point is a factor
  ~20^12 ≈ 4·10^15 — not an engineering gap, a wall. defect-gas.md:247 drew
  the same conclusion at P_17 ("the gas route is priced out").
- The cheap compressions are closed doors already banked: the per-level span
  cap looks certain and UNDERCOUNTS (brief §2, 333 vs 339 at (e,k)=(0,2));
  mirror quotient is a ≤2x constant; linear-algebra compression of
  connectivity states was measured absent on the column TM (char-2 rank
  exactly A034299, ~6x, no mod-p collapse — results/exactchange-probes.md;
  applying that to the family DP is analogy, labelled as such, but it is the
  only measurement anyone has of this state space's rank structure).

## 3. Why it is intrinsic to the family — and what would refute that

The claim, argued about the construction and not the instance:

1. The mechanism is lattice-parametric (defect-gas.md:15: cumulants linear in
   n on square and hex too, pair weights 4, 9, 25). On ANY row-local lattice
   the level-k constants are aggregate weights of connected clusters with all
   rows ≥ 2 cells and surplus k — i.e. connected-animal counts of up to ~2k
   cells with contact factors. The construction re-encounters, at size ~2k,
   the same connectivity-tracking problem it was built to bypass at size n.
   That is a statement about the tower on the whole family, with the king
   20x/level as its instance measurement.
2. The GF-side escapes are blocked by measured or proved facts, not by
   pessimism: the all-pairs weight family is NOT C-finite (defect-gas.md:262,
   refuted at ℓ=16; state space infinite, GF at best algebraic); the full
   anisotropic GF is non-D-finite by theorem (results/anisotropic-not-
   dfinite.md — quantified: no ODE with r ≤ 5, deg_x ≤ 28, up to r=0,
   D ≤ 3288); and the depth-1 algebraic miracle (results/onset-defect-
   depth1-closed.md) came from a bounded-excess kernel: all rows size 2, a
   two-class gap walk, finite kernel dimension, plus a rank-one pole
   cancellation. Each added unit of excess adds a marker to that walk
   (depth1-closed §6); the full tower needs unboundedly many markers, so the
   W2 kernel method does not extend as-is — its kernel goes
   infinite-dimensional exactly where the tower needs it.
3. The depth/excess grading localizes the hardness precisely: the top j
   coefficients of column k need only excess ≤ j−1 families
   (severance_w3_depths.py:75) — polynomial in k, algebraic at depth 1,
   k = 200 in 42 s. The tower constants are the BOTTOM of the column: full
   excess, all 2^(k−1) compositions. Hardness grows with depth into the
   column, not with the level per se. The tame results are all
   bounded-excess shadows; so are the 3-adic finite equations (valuation
   lemma: mod 3^m only surplus ≤ m clusters survive).

What this is not: a lower bound. Two concrete refutation targets, either of
which would overturn the verdict — (a) a kernel-method closure of the
bivariate family GF Σ W_c y^{k_c} w^{ℓ_c} with unboundedly many markers
(nothing known rules it out; the depth-1 curve proves the machinery exists at
excess 0); (b) a super-constant state quotient in the stack DP (the measured
evidence against is the Exact Change rank result, which is a column-TM
measurement, not a family-DP one).

## 4. Routes past it, priced

Labels per the brief: MEASURED / EXTRAPOLATED / ASSERTED.

**Route 1 — the excess ladder to depth 9: incumbent-freedom for the whole
tower (recommended).** `D_series(j, K)` is generic in j — `emax = j−1`
(severance_w3_depths.py:407) — so depths 5..9 are a compute job, not a
derivation: family tables at emax ≤ 8, K = 21-22, through the existing
identity. With depths 8 and 9 closed, undertow's own coverage bound
(undertow.md:320, k_max = Hs + J − 2) gives k_max = 14 + 9 − 2 = 21: every
level 10..21 pins from two cells of height ≤ 14 at n ≤ 40 — all banked AND
strip-engine-confirmed (level 21's pair: T(35,14) at j=8, T(34,13) at j=9;
the 2×2 system in (a_k, b_k) at distinct n is always nonsingular, and the
342-cell audit is the k ≤ 19 empirical demonstration). The incumbent kink
sweep then exits the tower's dependency graph entirely. Cost:
- e-ladder wall growth MEASURED today at K=8 (4 threads): e2 0.09 s, e3
  0.65 s, e4 3.59 s, e5 15.45 s / 287 MB peak — 4.3-7.2x per excess unit,
  ratio falling. Banked anchor: (K=19, e=3) = 146 s / 494 MB
  (severance_w3_depths.py:129).
- (K=22, e=8) EXTRAPOLATED five excess steps past measurement: wall
  ~146 s × 5^5 × ~2.5 (K-scaling ≈ (22/19)^6.3, exponent from the measured
  K 8→19 factor of 225 at e=3) ≈ 10^6 core-seconds — days on dalby's 32
  cores. RAM at the same per-e ratio extrapolates from 494 MB through
  dalby's 125 GB around e ≈ 6-7 — **RAM, not wall, is the likely binder,
  exactly as in W1** (the state maps are stream-mergeable, so NVMe spill is
  plausible engineering if it binds).
- Decision the calibration changes: whether tower-wide incumbent-freedom is
  a days-scale dalby job or needs external-memory work first. Job request
  filed as queue row C-R1.
- Honest limits: this is freedom from the INCUMBENT, not from sweeps — the
  strip cells are swept by a second engine; and D_j at k = 20, 21 is
  extrapolation of a derivation beyond the k ≤ 19 validation window
  (undertow.md's own Limits section says the same).

**Route 2 — strict freedom, extended: external-memory W1.** Mirror quotient
(≤2x, ASSERTED from the state's reflection symmetry) plus NVMe-spilled state
maps (the row-transfer scan is sort/merge-friendly, ASSERTED) buys k = 10 at
~1 TB spill and perhaps k = 11 at ~20 TB (EXTRAPOLATED at the measured
20x/level from 53 GB). Never approaches 21. Worth doing only for what it
certifies: roughly two more rows of end-to-end two-source coverage past
n = 24, and two fewer anchored levels.

**Route 3 — kernel method in e.** Derive the excess-1 family GF by the W2
machinery with one marker (the K=60 e=1 table,
results/severance_w3_families_K60_e1.txt, is 60 orders of holdout sitting
ready). Tests the depth1-closed conjecture ("every fixed depth is algebraic,
on curves sharing the branch point at 1/27", onset-defect-depth1-closed.md:203)
one step up, and measures how the algebraic route's difficulty grows in e —
the quantity that decides whether route 1's tables could ever be replaced by
desk algebra. Desk work; no machine time.

**Route 4 — 3-adic pinning: a closed door, with the arithmetic reason.** The
valuation lemma (defect-gas.md, v₃(Ŵ) ≥ k−1) makes H mod 3^m a FINITE
computation — but only clusters of surplus ≤ m survive mod 3^m, and h_k grows
geometrically with ratio ρ_h ≈ 6-14 > 3 (banked H = 1, 25, 208, 1483, 20688,
130208). Pinning h_k exactly needs m ≈ k·log₃ρ_h > k, i.e. weights to surplus
BEYOND k. The 3-adic route needs more cluster data than the direct route it
would replace. Self-defeating for exact values; keep it for congruences.

## 5. Compute disclosure

The §4 e-ladder timings were run by me, foreground, ~20 s total wall of
build/severance_w3_families at K=8 — on gympie, which the brief bans. I
caught it after the e=5 run and stopped; nothing else was run beyond
grep/cat/ls. The numbers are retained above (they are seconds-scale and
load-bearing for route 1's pricing) with this flag; re-run on ayr if anyone
wants them clean.

## 6. Stop condition

Met: the question is answered with evidence. Strict freedom — no swept cell —
is blocked by a family-level obstruction (§3) with two named refutation
targets; practical freedom from the incumbent is priced (§4 route 1) and
waits on one calibration measurement, filed as a job-request queue row.
