# Extension scout: what the tower method reaches past d=7, and what that buys

2026-08-11. Round-2 agent 4 (extension scout), per
`docs/triangle-structure-round2-brief.md` §Team shape, run after agents 1-3
went green. Verifier: `experiments/tristruct/r2_scout_d8.py` (subcommands
`levels`, `census`, `probes`, `d8`, `bits`; exact integer arithmetic
throughout; run log `experiments/tristruct/r2_scout_d8_run.log`). This is a
scouting and costing report — no LB certificate is attempted anywhere.

**Bits against enumeration error: 1.6 new** — the d=8 tower built in this
run predicts the law-free ENUMERATED cell (35,21) and the banked value
matches (§2); this is the first residue check the campaign has ever landed
on an enumerated law-free cell. **Bits against formula-chain error: ~270
new, correlated** — the d=4..8 levels re-match all 34 banked h_k, g_k
coefficients (k ≤ 17) mod 3^5..3^9 where mod 3^4 was the previous ceiling
(~5 fresh ternary digits × 34 coefficients), plus one wired-P_k family cell
(38,23) checked mod 3; same correlated-not-additive caveat as agent 1's.

## Verdict, in one paragraph

**No tower level "dies": the method needs zero new ideas at every level
m ≤ 20, and the measured plateau now extends through d=8** — this run built
the d=4..8 towers, found the d=8 target is period-3 after all (cycle
(0,1,1); round 1's "break at d=8" was a below-onset scan artifact, the real
break is at d=9), and landed the campaign's first enumerated-cell check:
(35,21) predicted 0, banked 0. What dies is the mission's premise. The route lands on the enumerated law-free sleeve cells —
27 real-sweep cells in columns H = 15..21 at rows n = 29..40 — but only ONE
of them is a row-40 cell, (40,21), which is 2.84% of a(40). **The row-40
H = 15..19 cells themselves (43.84% of a(40)) sit at k = 21..25, deficit
d = 24..36, i.e. at n < 2k+1 — BELOW the diagonal law's proved sharp onset —
and are therefore outside the tower's validity region at every depth,
forever.** (Onset n ≥ 2k+1 is proved and sharp: `docs/proofs/diagonal-law.md`
Step 5 + deg R_k = 2k+1 exactly, verified k ≤ 5.) What full success buys
against enumeration error is a check of the H = 15..21 per-height sweep
*artifacts* (which carry 50.84% of a(40)) at rows 29..40 — real teeth against
a systematic per-height/column bug, zero teeth against an error specific to
the row-40 tail of those files (overflow at the largest counts, CRT
reconstruction at n = 40). The cost curve is: **free through d=12
(overnight, one Python core), a fleet-scale Python week to d≈14, and a
C++-port + fleet-months campaign to d=19.** The binding resource at every
level past 14 is DP weight enumeration wall-clock — not proof difficulty,
not RAM (unmeasured, flagged), not ideas.

## 1. The measured plateau: d = 4, 5, 6 towers actually run

Agent 1's census promised d=4,5 free and d=6 cheap. Measured
(`r2_scout_d8.py levels`; every level: fixed point vs banked h_k k ≤ 17,
explicit monic curve ≡ 0, G vs banked g_k, family residues on the derived
series to k = 55):

| d | modulus | interior terms | curve deg | new weights | wall |
|---|---|---|---|---|---|
| 3 | 3^4 | 5 | 9 | 0 | 0.1 s (agent 1's level, re-run baseline) |
| 4 | 3^5 | 11 | 11 | 0 | 0.2 s |
| 5 | 3^6 | 16 | 11 | 0 | 0.5 s |
| 6 | 3^7 | 26 | 12 | 5 int + 5 bnd + (2^6,2^7) | 4 s of DP + 0.7 s |

Family cycles on the fully derived series, matching round 1's measured table
(`results/triangle-hunt-synthesis.md` negative 5) in every case: d=4 (2,2,2)
from k=4, d=5 (2,2,2) from k=5, d=6 **(2,1,1) from k=6** — each cycle now
holds on the derived series to k=55, well past its banked window (k ≤ 14 or
15), the same epistemic step agent 1 took for d=3. Agent 1's "hours of Python at worst"
for the five m=7 weights measured at **4 seconds** (they are (3,2,2,2,2)
permutations, all narrow): W = 2798827, 3897785, 3966217 (+2 reversals),
all v₃ = 0, all five survive. So d=4,5,6 need only their (routine,
one-session-each) LB certificates to reach agent-2-grade theorem status;
the towers are in hand and verified.

## 2. The d=8 level, built — and the "break at d=8" partly dissolved

The census said m=9 needs 74 new weight slots; the cost model said tens of
minutes. Measured (`d8` subcommand, run log): **the full m=9 weight set —
57 interior + 24 boundary DP runs — took 349 s**, the widest cell being
interior(2,4,3) = 230231 at 54.3 s. The tower then went green in 1.9 s:
72 interior survivors, monic curve of degree 19, **H and G mod 3^9 match
every banked h_k, g_k for k ≤ 17**, and P_k(3k−7) mod 3^9 matches the exact
banked P_k on k ≤ 17.

**The d=8 family residues on the derived series are period 3 after all:**

> r_k cycles **(0,1,1)** from k = 8 through k = 55 —
> v₃(P_k(3k−7)) > 8 exactly at k ≡ 2 (mod 3), unit residue 1 otherwise.

Round 1's table said "no period" for every d ≥ 8. For d=8 that verdict is a
**below-onset scan artifact**: the grid scan included cells with k < d
(e.g. (14,7) at k=7), which sit at n < 2k+1, below the proved sharp onset,
where T ≠ P_k(n)/3^d and the residues are unrelated to the family law.
Restricted to k ≥ d, the banked d=8 residues are plainly (0,1,1)-periodic
— and the in-script rescan (`d8` output, last block) confirms it. The same
rescan shows d = 9..13 and 15 are genuinely NOT period-3 even in-onset
(5–8 banked points each; d=14's 4 in-onset points are too few to test), so
the structural break is real but starts at **d=9, not d=8**, and on
windows that short it could still be a longer period or a later cycle
start; the m=10 tower would decide it for ~30–60 min of DP. (For any d the
target should be 3-automatic — coefficient sequences of the mod-3^m
algebraic fixed point fall under the Denef–Lipshitz diagonal theorems — so
"no period 3" ends the pretty cycles, not the provability: a certificate
would pin an automaton or a longer cycle instead of a 3-cycle. Left as a
pointer, not a claim; nothing below depends on it.)

The check against the banked triangle, provenance quoted per cell — 8/8
match:

| k | (n,H) | provenance | banked T mod 3 | predicted |
|---|---|---|---|---|
| 8 | (17,9) | real-sweep | 0 | 0 |
| 9 | (20,11) | real-sweep | 1 | 1 |
| 10 | (23,13) | real-sweep | 1 | 1 |
| 11 | (26,15) | real-sweep | 0 | 0 |
| 12 | (29,17) | real-sweep | 1 | 1 |
| 13 | (32,19) | real-sweep | 1 | 1 |
| **14** | **(35,21)** | **real-sweep** | **0** | **0** |
| 15 | (38,23) | closed-form-Pk | 1 | 1 |

The k=14 row is the d=8 law-free enumerated cell — the first time in either
round that a theorem-side prediction has landed on an enumerated law-free
cell at all. Its 1.6 bits (conditional on the frame: diagonal law + chain
identity, proved; plus the DP weight values) are this file's headline
number. The k ≤ 13 rows are law-implied (correlated with the P_k fit
anchors — claimed at 0 new bits); the k=15 row is a formula-chain check.
Since the target is again periodic-rational, **agent 2's LB certificate
route applies verbatim at d=8** — one desk session away from theorem
status, though the residue check above does not need it.

## 3. Per-level cost model, measured where cheap

Machine calibration: this box reproduces the 2026-08-01 banked DP walls at
factor ×1.03–1.06 (interior(3,5) 84 s vs 89 s banked; interior(4,4) 116 s vs
120 s banked, values match). New probe measurements (`probes` subcommand;
five new weights banked into the log, exact integers):

| cell | k | value | v₃ | wall |
|---|---|---|---|---|
| interior(2,2,4) | 5 | 29515 (matches table) | 0 | 0.7 s |
| interior(2,3,3) | 5 | 67371 (matches table) | 1 | 1.8 s |
| interior(2,2,5) | 6 | 55466 | 0 | 7.5 s |
| interior(2,3,4) | 6 | 184328 | 0 | 30.6 s |
| interior(3,3,3) | 6 | 253155 | 1 | 5.0 s |
| interior(2,2,6) | 7 | 93817 | 0 | 80.1 s |
| interior(2,2,2,4) | 6 | 429025 | 0 | 1.8 s |
| boundary(3,5) | 6 | 2585 | 0 | 37.2 s |
| boundary(4,4) | 6 | 3012 | 1 | 64.0 s |
| boundary(5,5) | 8 | — | — | TIMEOUT > 300 s |
| boundary(2,2,5) | 6 | 10481 | 0 | 4.5 s |

Measured growth per unit surplus: two-row ×8.4 (a=2), ×12 (a=3), ×15.9
(balanced) — banked walls; **three-row ×11.4 then ×10.6** ((2,2,4)→(2,2,5)→
(2,2,6)) — new. Boundary ≈ 0.45–0.55× the matching interior. Four-row and
narrower: cheap ((2,2,2,4) at 1.8 s; all (3,2⁴)-perms sub-second).

Census of weight slots the valuation filter consults (interior bar
2k−ℓ−1 ≤ m−1, boundary bar 2k−ℓ ≤ m−1; `census` subcommand — agent 1's
interior-only candidate counts, extended to include the boundary slots the
G-formula needs, hence larger absolute numbers, same ×1.62/level growth):

| m | d | total slots | newDP slots (cum.) | worst new cells entering |
|---|---|---|---|---|
| 9 | 8 | 142 | 74 | ℓ=3 int k=6 (measured 5–31 s each) |
| 10 | 9 | 231 | 155 | ℓ=4 int k=7 |
| 11 | 10 | 375 | 296 | ℓ=3 int k=7, ℓ=2 bnd k=6 |
| 12 | 11 | 608 | 520 | ℓ=4 int k=8 |
| 13 | 12 | 985 | 894 | ℓ=3 int k=8, ℓ=2 bnd k=7 |
| 14 | 13 | 1595 | 1496 | ℓ=2 int k=8 ((4,6)), ℓ=4 int k=9 |
| 15 | 14 | 2582 | 2480 | ℓ=3 int k=9, ℓ=5 int k=10 |
| 16 | 15 | 4179 | 4070 | ℓ=2 int k=9 ((5,6),(4,7)), ℓ=4 int k=10 |
| 17 | 16 | 6763 | 6651 | ℓ=3 int k=10, ℓ=5 int k=11 |
| 18 | 17 | 10944 | 10825 | ℓ=2 int k=10 ((6,6),(5,7),(4,8)) |
| 19 | 18 | 17709 | 17587 | ℓ=3 int k=11, ℓ=5 int k=12 |
| 20 | 19 | 28655 | 28526 | ℓ=2 int k=11 ((6,7),(5,8),(4,9)), ℓ=4 int k=12 |

Wall-clock estimates, anchored on the measured cells and the measured growth
factors (compounded ×11 for ℓ ≥ 3, family-specific for ℓ=2; boundary at
0.5×; uncertainty grows with extrapolation distance — the m=20 ℓ=4 figure
compounds six levels off a 1.8 s anchor, so treat the last rows as
order-of-magnitude):

| through d | est. single-core Python | practical shape |
|---|---|---|
| 8 | 351 s (MEASURED) | free — done in this scouting run |
| 12 | ~0.5–1 core-day | one overnight run, one box |
| 14 | ~10–15 core-days | a fleet week in Python (cells parallelize perfectly) |
| 15 | +~50 core-days | past the free-rein line; beg-and-agree territory |
| 17 | +~2–3 core-years | needs the C++ DP port (~×100, does not exist yet) |
| 19 | total ~30–100 core-years Python ≈ 0.3–1 core-years C++ | fleet-months even in C++ |

Calibration point: the model's a-priori m=9 estimate was 15–30 min; the
measured wall was 5.8 min, so the quoted ranges run conservative-high by
roughly ×3 at short range — which does not rescue the tail, where the
compounded growth factors dominate any constant.

The exponential is genuine: ×1.62/level in slot count times ×~11 per unit
surplus on the widest entrants. There is no cliff — every level is "only"
~5–15× its predecessor — and no floor either. RAM is unmeasured at the wide
cells ((6,7)-class state dictionaries could bind before wall-clock does);
flagged, not modeled.

## 4. The W(a,b) closed-form lever, honestly assessed

The named lever (agent 1) is a proved closed form for the two-row interior
family. Status: a=2 cubic (3 holdouts), a=3 quartic (1 holdout), pattern
deg_b = a+1, both leading coefficient 24 — fitted, not proved
(`results/defect-gas.md` §Open). Assessment:

- **Plausible?** Yes. Polynomiality of W(a,·) for fixed a has the shape of a
  transfer-matrix-in-b argument, and two rows is the easiest nontrivial case.
  But the *general* (a,b) form is explicitly known NOT to be a fixed-degree
  bivariate polynomial (the symmetric-bicubic refutation), i.e. the closed
  form is a genuinely open combinatorial problem, and pinning each row a by
  fit needs DP cells out to b ≈ a+3 — for a=6 that means (6,9), which is
  WORSE than the campaign cells the formula was meant to replace. Only a
  structural proof helps; a fitted formula would also degrade the frame:
  the d ≤ 8 certificates consume exact DP integers, and (A4) with fitted
  weights is a weaker statement than (A4) with computed ones.
- **Does it collapse the d ≥ 8 cost?** No — it shifts it. At m=18..20 the
  two-row interiors are roughly a third of the estimated cost; the ℓ=3 and
  ℓ=4 wide families ((2,2,b), (2,2,2,b), (2,3,b)…) are each comparable, and
  the two-row *boundary* family needs its own (un-fitted, un-started) closed
  form besides. Collapsing the campaign needs closed forms for the whole
  graded family of wide clusters — at which point one has proved a general
  cluster-weight structure theorem, a research program, not a lemma.
- **The lever that actually moves the wall** is unglamorous: the C++ port of
  `cluster_weight_dp.py` (measured ×100 claim in `defect-gas.md`) plus
  per-cell parallelism. That converts d=19 from impossible-in-Python to
  fleet-months — still frontier-push scale.

## 5. Exposure flags per level (agent 3 finding 2's shape, carried forward)

The audit's instruction: at each new level, the newly-entering weights'
mod-3^j digits are the entire new exposure; flag DP-only digits. Measured
shape (census, confirmed mechanically): **every weight enters its first
level needing exactly its mod-3 digit** (entry level m = 2k−ℓ for interior,
2k−ℓ+1 for boundary), then one more digit per subsequent level. The
enumeration-cross-checked set is frozen at k ≤ 3 plus (3,3), (2,4) — direct
enumeration is Ω(W), hopeless for everything wide — so **all 74 slots the
d=8 level adds are DP-only, and the DP-only fraction → 100% from here up**
(28,526 of 28,655 slots by m=20). W(2,2,2,2)-style one-off enumeration
close-outs (agent 3's caveat) cannot scale past d≈9. The honest mitigation
at campaign scale is not enumeration but a **second, independently-written
DP** (the project's checkers-above-content standard); without one, (A4)
for d ≥ 9 rests on a single Python implementation, however well validated
at k ≤ 5.

Note the run itself already banked fresh DP-only digits: the five m=7
weights, W(2,2,5), W(2,3,4), W(3,3,3), W(2,2,6), W(2,2,2,4), and the m=9
set in the log — none has (or realistically can have) an enumeration
cross-check beyond the k ≤ 5 validations the DP already carries.

## 6. Bit accounting — the mission's number

All provenance below quoted from `triangle.py provenance(n,H)` (H = 3..21
real-sweep; H ≥ 22 wired P_k; H ≤ 2 closed-form low strip). Block shares
verified against the banked triangle: H=15..19 of row 40 = **43.8432%** of
a(40); H=15..21 of row 40 = 50.8445%; T(40,21) alone = 2.8431%.

The 42 law-free sleeve cells (k = 14..19, n = 2k+1..min(3k+1,40)) split 27
real-sweep + 15 wired-P_k, exactly as round 1 measured; the 27 enumerated
ones have d = 2k+1−H ∈ [8,19] (full table with residues in the `bits`
output). A tower to mod 3^m predicts each family-d cell mod 3^(m−d)
(T = P_k(n)/3^d is inside the proved law for every sleeve cell, k ≥ d), so
each outcome carries a unit-check count and a full-depth count:

| outcome | tower | **bits vs ENUMERATION error** | full-depth variant | bits vs FORMULA-CHAIN error (full depth, conditional) |
|---|---|---|---|---|
| d=8 only — **DONE, this run** | 3^9 | **1.6** (1 cell: (35,21), passed) | 1.6 | 41.2 (8 wired-P_k cells; only the mod-3 digit of (38,23) checked so far) |
| d=8..12 | 3^13 | **14.3** (9 cells, columns H=17..21) | 34.9 | 114.1 (13 cells) |
| d=8..14 | 3^15 | **25.4** (16 cells, all columns H=15..21 touched) | 72.9 | ~180 |
| d=8..19 | 3^20 | **42.8** (27 cells) | 266.3 | 277.4 (15 cells) |

(The d=8..14 row is added because the cost model puts it at the edge of
free-rein reach and it is the first outcome that touches every enumerated
column H = 15..21.)

**What those bits are and are not.** They are conditional on the frame
(diagonal law + chain identity, both proved; plus the weight values, §5),
and they check the per-height sweep artifacts h15.out..h21.out at rows
29..40. A systematic error in any of those seven production sweeps —
transition table, kink-carry kernel, connectivity rule at that height —
would fail the check with the stated probability. They are NOT a check of
the row-40 values in those files except at (40,21): an error mode that hits
only the largest-n tail (counter overflow, CRT reconstruction at n = 40,
sharding of the biggest jobs) is invisible to all 26 other cells. Row-40
coverage even at full success: (40,21) mod 9 (~3.2 bits on 2.84% of a(40)),
(39,20) mod 3 and (39,21) mod 81 next door.

**And the mission's target block is out of reach at every depth.** The
row-40 H=15..19 cells have k = n−H = 21..25 and d = 2n−3H+1 = 24..36, so
n < 2k+1: below the proved sharp onset, where T = P_k(n)/3^d simply does not
hold (deg R_k = 2k+1 exactly — each such cell carries a fresh R_k
coefficient, round 1's own frame-exhaustion result). No tower depth changes
this; it is the same geometry that killed the fitted families, one level
deeper. The brief's hope that "the H = 15..19 block becomes checkable"
cashes out as: *the sweeps that produced the block* become spot-checkable at
lower n, worth the table above, and no more.

## 7. Recommendation

1. **d=8 is banked by this run** (351 s measured; weight set reproducible
   by `r2_scout_d8.py d8`, walls in the log). The one-session follow-up
   worth doing is the LB certificate for the (0,1,1) cycle — agent 2's
   route applies verbatim now that the target is known periodic — which
   would make d=8 a theorem and retire the corrected round-1 table row.
2. **d=9..12 are a legitimate overnight follow-up** (one box, one Python
   core, ~day): +12.7 unit bits over 8 more enumerated cells, and the m=10
   tower settles what the genuine break at d=9 actually is (longer period,
   later start, or true aperiodicity of the 3-automatic target). This is
   the knee of the value/cost curve.
3. **d=13,14 only with fleet time to burn** (a parallel-Python week):
   completes column coverage H=15..21 at +11 unit bits.
4. **Do not launch d=15..19.** Cost is C++-port + fleet-months; the
   marginal 17.4 unit bits land on the same seven columns already sampled,
   and none of it reaches the row-40 tail where the actual exposure lives.
   If the project ever wants those bits, the prerequisite is the second
   independent DP of §5, not more Python hours.
5. The one cheap thing that WOULD touch the row-40 tail is outside this
   method entirely: the H22 holdout / cross-ISA recount already scoped and
   declined (`p19-and-a40-recount-declined`) — noted for completeness, not
   re-pitched.

## Novelty

`git log --all --oneline --name-only -- 'results/*.md' 'docs/**/*.md'`
swept; off-branch hits inspected via `git show`. No extension-scout or
d ≥ 8 tower work exists on any branch; no prior claim of the d=8 (0,1,1)
cycle exists anywhere (round 1's table records "none" for d ≥ 8 — this file
CORRECTS that entry for d=8, with the artifact mechanism named, and leaves
d ≥ 9 as measured). Prior art credited: agent 1's census
and lever naming (this round, uncommitted), `results/defect-gas.md` (DP,
two-row fits, ×100 C++ claim), `experiments/spine_deeper.py` (mod-81
numerics), round 1's sleeve census and onset-sharpness measurements. The
below-onset unreachability of the row-40 H=15..19 cells is a scoping
consequence of already-proved results (sharp onset + cell geometry), stated
here explicitly for the first time; it contradicts no banked claim — it
sharpens the brief's mission sentence.
