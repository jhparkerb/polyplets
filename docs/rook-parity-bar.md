# The rook-parity bar — round 1's product

2026-08-14, written by the lead from the five lane files of round 1
(`docs/rook1-brief.md`), which was the desk-only day chartered at
`docs/rook-parity.md:125-137`. This is the round's falsifiable deliverable: the
numeric bar, the `g` verdict against the thresholds registered before the
measurement, the Hankel verdict, and the go/kill for the route.

Lane files: `results/rook1/R1-K.md` (brief adversary), `R1-A.md` (base anatomy),
`R1-B.md` (gate 0), `R1-C.md` (rook Hankel), `R1-D.md` (transport obstruction),
`R1-E.md` (queue row B1). Every number below was re-derived by the lead before
it was written here.

## 1. The measured clause of the bar

**Threshold: a challenger's fitted per-term cost ratio over n = 24..30 must be
strictly below 1.7266** — exactly `√(3,329,644 / 1,116,858)`, the incumbent's
measured frontier per-height cpu ratio carried to per-n on the `dH/dn = ½`
treadmill the pipeline runs. Anchor: `results/ns_a40/PROVENANCE.md:16,19`.

Fit protocol, fixed so a challenger is measured identically: total cpu-seconds
for each end-to-end `maxn = N` run, N = 24..30, all seven points, one machine,
one build; least-squares slope of `ln(cpu)` vs N; the threshold applies to
`e^slope`; residuals reported per point. Cpu-seconds, never wall; end-to-end,
never per-height cherry-picks.

**What this threshold does not yet have: the incumbent's own curve on that
window.** The kink kernel entered production at a(30), so the window holds
exactly one kink point and the incumbent's on-window slope is NOT ESTABLISHED
in-tree. Job A1-JOB-1 (`results/rook1/R1-A.md` §5, ~2 h of dalby) would create
it; it is held pending jasonp and is not dispatched.

Deliberately not registered: the in-band aggregate 1.4595 (a transient — the
`P_k` fence advanced 6 diagonals in 10 terms, faster than the treadmill
sustains), and the retired column engine's 1.961.

## 2. The `g` verdict, and the object it was measured on

`g` ≈ 20 per level: one completed ratio 21.0 at k=4→5 and a MEASURED lower
bound 8.15 at k=5→6, both in the Python spec implementation
(`results/defect-gas.md:242`); the C++ port has a single timed point (k=9,
66 min, 53 GB) so no two-point C++ ratio exists.

Against the partition registered before the measurement — repaired mid-round
after `b` collapsed it, with the repair recorded rather than made silently
(`docs/rook1-brief.md` §Pre-registered kill thresholds) — **`g ≥ b²` fires and
the `P_k` tower is KILLED.** The verdict is invariant across every version of
the table: 8.15 exceeds both 5.856 and 2.9813. Scale check, for the record: at
even the parity threshold g = 3, climbing from the k = 9 anchor to the k = 19
the route needs is 7.4 years of 16-thread dalby.

**But gate 0 measured a harder object than the route requires** (R1-E, closing
queue row B1). The wired band consumes only two rational constants per level,
not the weight DP; below-onset cells at depth ≤ 4 are closed ab initio, so every
level the n = 40 assembly touches is pinnable from the route's own H ≤ 19 sweep.
Depth ≥ 5 and the surplus-k composition DP are consumed nowhere. The right cost
object is the half-height kink sweep plus the excess ≤ 3 family tables, and the
measurement gate 0 should have run is the growth ratio of that family DP over
K = 19..25 — minutes-scale, not a 7.4-year tower. **Unmeasured; queue row E2.**

This is not a parity rescue and R1-E does not claim one: both the incumbent and
the re-anchored route sweep to half height, so the corrected route's base **is**
the incumbent's `b`. Deleting phases B and C — 84% of the a(40) cpu — is a
constant-factor improvement, which `docs/rook-parity.md:11-12` puts out of scope
by its own terms.

## 3. The Hankel verdict

**Rook shows no char-2 crack.** On an identical state space (rook census = king
census = Motzkin(H+1)−1 at every H ≤ 9), rook GF(2) Hankel rank is
20/49/119/288/696/1681 at H = 4..9 — 77–100% of states, growth locked at
~2.42×/height across five consecutive ratios, no `2^H` law — where the king
`0.44·2^H` law gives 229 at H = 9. Mod-p rank is exactly full at every measured
H. Receipt: `experiments/rook1/rook1_R1-C_rank_probe.log`, which reproduces the
banked king table (6,15,27,58,112,229) and A-S1 mod-p as a regression before any
rook number is read, fires both RED controls, and ties ground truth to A001168
through `build/g2 --rook-bishop`.

**The king decision that changes**: the INV-4 explicit-basis hunt
(`results/triangle-r3-involution.md` §NOT ESTABLISHED) loses its CKN-precedent
justification. Rook is where matchings and planarity machinery natively live and
it shows no collapse, so the king collapse is stencil-specific rather than the
generic phenomenon, and the hunt's prior resets to unexplained king-specific
structure, mechanism unknown.

Secondary, and it speaks to the goal's frame: no field-linear realization of the
rook strip functional beats Motzkin in any characteristic at measured H. "Parity
means matching the Motzkin exponent, not breaking it" now has a measurement
behind it.

## 4. Go / kill

| route | verdict |
|---|---|
| ab-initio `P_k` tower to k = 19 | **KILLED** at gate 0. `g` ≈ 20/level; no `b` changes the outcome |
| the same route re-anchored on depth ≤ 4 closed forms | alive as a **constant-factor** win (deletes 84% of a(40) cpu), out of scope as a base change |
| king→rook transport | **DEAD unconditionally**, no longer merely out of scope — see below |
| rook-side Hankel structure | **no crack**; banked as a negative-map entry |

**Transport.** A size-preserving reduction has nothing to translate at the state
level — the Motzkin cut vocabulary is literally shared, king cut partitions
being non-crossing (hand proof in `results/rook1/R1-D.md`, corroborated by the
measured identical state sets at H ≤ 8). What must transport is the action:
king's zero-cell diagonal gap-jumps must be bought with rook bridge cells.
Against that stands an unconditional counting floor on all injective reductions,
`β ≥ ln λ_k / ln λ_r` = 1.244 rigorous (λ_k ≥ 6.543, λ_r ≤ 4.5252), 1.400 at
best estimates. With `b` = 1.7266 the budget is `β < ln b / ln √3` = **0.994**,
below 1, so no injective reduction of any kind can pay for itself. Under the old
(wrong) 2.42 the budget was 1.61 and a corridor [1.40, 1.61] survived for
animal-adaptive maps; measuring the incumbent honestly is what closed it.

The goal file's asserted `β ≥ 2` for the diagonal-splice family is now derived
and tight: both diagonals cheap is a lattice-parity impossibility, a staircase
along an expensive axis forces ≥ 2n−1 cells, identity-plus-bridges achieves
exactly that. β = 2 exactly for the whole translation-covariant family.

## 5. What round 1 hands to whoever goes next

Two things are jasonp's and are not decided here.

- **The bar now contradicts the pin.** With the incumbent at 1.7266, gate 1's
  "strictly below the incumbent" is strictly stronger than `c ≤ √3`: a method
  whose base is exactly √3 = 1.7321 — the goal's stated target — fails the
  clause. Keep the strict clause, or relax the pin to it (queue row A4).
- **The goal's test may no longer separate anything.** R1-E's trace shows the
  treadmill can self-anchor from a run's own half-height sweep, so "a(40)
  recomputed end to end with no anchor cells or intermediate values from the
  banked run" is passable by the incumbent kernel (queue row E3). Combined with
  the incumbent measuring at parity as operated, the goal as written is at risk
  of being satisfied or vacuous rather than aimed.

The live technical question, and the only one that can still move the base:
**does the per-height cpu ratio R converge below 3 or cross it?** It is still
rising at the last measured height (2.60 → 2.73 → 2.98 across H18..H21), and
`b = √R` sits 0.31% below the pin. Queue row A2. Everything else round 1 touched
is closed or constant-factor.

Two measurements would settle what round 1 could not, both small: A1-JOB-1 (the
incumbent's on-window curve, ~2 h dalby, held for jasonp) and E2 (the corrected
gate-0 measurement — e ≤ 3 family DP growth over K = 19..25, minutes).

## Corrections to the lane files

- R1-E cites `results/severance_w3_families_K19_e3.txt` for the 146 s K = 19
  timing; that artifact carries no timing. The number is banked at
  `results/onset-defect-depths234.md:25` and `docs/severance-w4-scoping.md:156`.
- R1-K noted the brief cites `docs/agent-types.md:51-54` (the scout
  two-successor rule) to bind R1-D, an adversary. The obligation binds anyway
  through the brief's own queue control. Harmless, recorded once.
