# R1-B — P_k tower feasibility: g, and the reduction survey

2026-08-13, scout lane, desk-only. Question per `docs/rook1-brief.md` §R1-B:
fit `g` (the ab-initio P_k cost growth) from the severance records, and survey
what a state-space reduction past k = 10 would have to be. Gate 0 of
`docs/rook-parity.md:111-112`.

## 1. The measured record

Every per-k cost number in the tree, with its source. No new compute was run.

| point | value | basis | source |
|---|---|---|---|
| Python DP, k=4 | 3.1 s | MEASURED | `results/defect-gas.md:242` |
| Python DP, k=5 | 65 s | MEASURED | `results/defect-gas.md:242` |
| Python DP, k=6 | >530 s, killed incomplete | MEASURED lower bound | `results/defect-gas.md:242` |
| C++ (`build/severance_w1`), k=9 | 66 min wall, 16 threads, 53 GB peak, dalby | MEASURED | `results/severance-w1-anchor-cut.md:42` |
| C++, k=10 | declined: peak RSS "scales past dalby's 125 GB", state map of the one huge stack alone tens of GB | ASSERTED (projection made at run time, no run) | `results/severance-w1-anchor-cut.md:46-50` |
| C++, k=8 | "minutes" | ASSERTED (pre-run price estimate) | `docs/onset-defect-severance-plan.md:78` |

The C++ is a port of the same DP (`experiments/cluster_weight_dp.py` is the
spec, `cpp/severance_w1.cpp` the port, per `docs/onset-defect-severance-plan.md:62-66`
and `results/severance-w1-anchor-cut.md:15-17`); language and threads are
constant factors on the same operation count, so the growth rate is shared
between the two implementations. That is the one inference step in this fit.

Structural point, MEASURED from the artifact itself: level k contains exactly
2^(k-1) compositions (surplus-k compositions with parts >= 2; the 511-line
`results/severance_w1_weights_k9.txt` is 2^0+...+2^8). Composition count alone
doubles per level before any stack DP runs.

## 2. The fit: g

Only k=4 -> k=5 gives a completed-run ratio, so "fit" here is one ratio plus
one lower bound plus the banked per-level statement — stated as such, not
dressed as a regression.

- **g = 21.0, MEASURED at k=4 -> 5** (65/3.1, Python, `results/defect-gas.md:242`).
- **g >= 8.15, MEASURED lower bound at k=5 -> 6** (>530/65, killed incomplete,
  same line).
- Banked in-plan as "Measured Python cost about 20x/level"
  (`docs/onset-defect-severance-plan.md:76-78`), and `results/defect-gas.md:243-245`
  extrapolates on exactly that rate to price out P_17 ("the gas route is priced
  out").
- The single C++ point (k=9 at 66 min) is consistent with ~20x/level above a
  minutes-scale k=8, but with one point no C++-only ratio exists:
  **NOT ESTABLISHED in the C++ implementation as a two-point measurement.**
- Memory: 53 GB MEASURED at k=9; the k=10 decline implies RAM growth > 125/53
  = 2.36x/level at that step (ASSERTED projection, not a run).

So: **g ≈ 20 per level (MEASURED at k=4..6, Python, single completed ratio 21.0);
the same-algorithm C++ point at k=9 is consistent; everything past k=9 is
EXTRAPOLATED.** The route in `docs/rook-parity.md:65-69` needs k = 19: that is
10 levels past the last measured point. At g ≈ 20 that extrapolates to
~20^10 x 66 min ≈ 10^13 hours, and RAM ≥ 53 GB x 2.36^10 ≈ 290 TB — quoted only
to show no plausible error in the fit rescues it, EXTRAPOLATED 10 levels.

## 3. Verdict against the pre-registered partition

Partition per `docs/rook1-brief.md:47-66`: g <= 3 parity; 3 < g < b^2 beats
incumbent only; g >= b^2 kills the tower route. Under the current best reading
b = 2.42, b^2 = 5.856; R1-A's reconciliation fixes b.

- **g ≈ 20 (basis: MEASURED, Python k=4->5, `results/defect-gas.md:242`).**
- **g >= 8.15 even as a raw measured lower bound** (killed k=6 run, same line).

**The g >= b^2 row fires. The tower route as built is killed**, and not
marginally: the measured lower bound 8.15 already exceeds 5.856, and the
measured ratio 21.0 exceeds b^2 for every b in the 2.42/1.61/1.73 contradiction
that R1-A is reconciling (largest candidate b^2 = 5.856; even b = 2.5 gives
6.25). Parity (g <= 3) is excluded by the same lower bound. No value of b that
R1-A can land on changes which row fires. Filed plainly per the brief: this
kill is convertible only by jasonp, in so many words.

Caveat attached rather than softened: the ratio is measured in the Python
implementation at small k; the C++ port has no two-point in-tree timing. The
same-algorithm argument (§1) is why this does not move the verdict; a per-level
timed C++ run at k <= 8 (minutes, dalby) would upgrade the label from
"MEASURED in spec implementation" to "MEASURED in shipped implementation" and
is filed as queue row B4 — it cannot change which partition row fires unless
the port has a different asymptotic operation count than its spec, which would
itself be a bug finding.

## 4. Survey: what a state-space reduction past k = 10 would have to be

The wall (`results/severance-w1-anchor-cut.md:44-50`): k=10 was declined on
memory; the tail is one huge stack whose state map alone would be tens of GB;
"extending needs a state-space reduction (symmetry quotient or frontier
compression in the stack DP), not more cores."

**The structural requirement, quantified.** Total growth ≈ 20x/level factors
as 2x from composition count (exact, §1) times ~10x per-composition stack-DP
cost (ESTIMATED as the quotient of measured aggregates). To reach parity
(g <= 3) a reduction must therefore either

- (a) keep enumerating compositions and cut per-composition cost growth to
  <= 1.5x/level — below even the whole-level RAM growth of ~2.4x/level, i.e.
  per-stack state maps effectively polynomial in k; or
- (b) stop enumerating compositions individually — aggregate the 2^(k-1)
  compositions symbolically (a recursion/transfer structure over parts, or an
  analytic derivation of the level aggregate) with polynomially-growing state.

Constant-factor moves cannot fire either branch, whatever their size.

**What in the repo already bears on it** (checked before naming anything new;
`build/` inspected — `build/severance_w1` is the only weights tool, `build/g2`
is enumeration ground truth and computes no cluster weights):

- `docs/middle-kingdom-plan.md`: **no overlap.** Poly-time king-animal
  subclasses, explicitly off the a(n) record path; nothing touches the
  cluster-weight stack DP.
- Symmetry quotient (named in §Ceiling): the reversal symmetry is visible in
  the weights artifact (W(c) = W(reverse c) with boundary columns swapped,
  e.g. the (2,3)/(3,2) rows of `results/severance_w1_weights_k9.txt`). Factor
  <= 2, constant — cannot move g. The named candidate that could move g is
  frontier compression, on which:
- The nearest measured analog of frontier compression in this project is the
  MPS/bond-dimension probe, measured chi ~ lambda^(H/4) — exponential, dead
  (closed door, `docs/rook1-brief.md:87-90`). Different DP, same kind of hope.
- Branch (b)'s analytic form has a theorem against its strong version:
  `results/depth-tower-bivariate-dead-end.md` — the bivariate below-onset GF is
  not D-finite (via `results/anisotropic-not-dfinite.md`, Northcott, atom
  degrees 1,2,4,9,29,68,... unbounded), and the W4 field test measured slice
  degree 4 -> >= 7 and climbing at depth 2. Fixed slices compress (W2's
  kernel-method depth-1 derivation is the existence proof); the family does
  not compress uniformly into closed forms. Any (b)-route must be a
  combinatorial recursion in k, not a closed-form family.
- mod-p / CRT machinery (`experiments/severance_w3_modp.py`, measured 7.4x;
  `results/crt-counter-shaping.md`): bigint-width constants only — cannot
  move g.

**Bottom line of the survey:** the k=10 wall demands a reduction that changes
the growth rate of the stack DP's state map or removes per-composition
enumeration entirely; every mechanism with measured or proved evidence in-tree
is either constant-factor (symmetry, mod-p) or measured/proved dead in its
nearest analog (MPS-style compression; closed-form families). Whether a
combinatorial recursion in k with sub-2x state growth exists is
**NOT ESTABLISHED** — nothing in-tree bears on it in either direction. Filed
as queue rows B1-B3 rather than as a candidate list, per the brief.

## 5. Queue rows filed

B1-B4 appended to `results/rook1/queue.md` (successors, different in kind, plus
the optional label-upgrade timing row). No job request blocks this verdict; B4
is dispatchable if jasonp wants the g label upgraded before acting on the kill.
