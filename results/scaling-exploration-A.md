# Scaling exploration — lane A (algebraic and analytic)

2026-08-11, per `docs/scaling-exploration-brief.md`. Lane: exact tensor-network
bond dimension, holonomic/algebraic structure not closed by the
non-D-finiteness theorem, sparse interpolation and guessing. Scoring is growth
rate + crossover, per the brief; every number below is from a probe run this
session (scripts named, in `scripts/`) or a held citation. Two-core budget
respected: every foreground probe was single-core; the one >5-min job ran in a
tmux window on gympie's session 0 (`hankel10`).

Summary: one genuinely new measurement (the temporal Hankel rank of the strip
counting automaton — rank-deficient by 4.4× and growing, base ~2.4×/height vs
the frontier's 2.65×), which nevertheless closes as a negative on compute
growth and yields the useful thing the brief asked for under "lower bounds": a
measured dimension floor for the entire linear-realization class. The
tensor-network direction was already half-measured in-repo (spatial cut,
negative, banked 2026-07-02); the temporal cut measured here completes it —
both cuts are now closed with numbers. The guessing directions are scored
negatives with exact swept boxes.

---

## A-S1. Temporal Hankel rank / minimal exact linear realization of the strip automaton

**Mechanism.** The height-H strip counter is a weighted automaton: alphabet =
nonempty column fills (2^H − 1 symbols), states = king-connectivity partitions
of the current column with stranded-component death (the incumbent rule),
accepting functional = "exactly one component." The minimal dimension of ANY
exact field-linear realization of the same word function f(w) = [cells(w) are
one king-connected component] — weighted automaton, temporal MPS along the
sweep direction, rank-compressed DP — equals the rank of f's Hankel matrix
(prefixes × suffixes). All automaton states are reachable from length-1
prefixes, so the rank equals the dimension of the observability space
span{T_w · accept}. If that rank is far below the state count, an exactly
compressed transfer exists; its growth is the candidate.

This is the **temporal** cut. It is a different object from the banked
tensor-network probe (`results/boundary-push-tensornetwork.md`, 2026-07-02),
which measured the **spatial** (within-column) Schmidt rank of the frontier
vector — χ ~ λ^(H/4) ≈ 1.63^H, MPS storage H·χ² measured 2–5× *worse* than
the explicit frontier, closed negative. The scaling brief's "nobody has
measured it" is true only of the temporal cut; the spatial one was measured
and its verdict stands unchanged. This section closes the other cut.

**Probe** (`scripts/probe_hankel_rank.py`, superseded by
`scripts/probe_hankel_rank2.py`; the first, sampling suffix columns, wobbled
233/235 at H = 9 — under-spanned — and was replaced by an exact
observability-space closure mod p = 2³¹−1, run at x = 1 and at a random
x mod p, which agreed at every height). Measured, exact closure:

| H | frontier states | Hankel rank (= obs dim) | states/rank |
|---|---|---|---|
| 4 | 20 | 6 | 3.33 |
| 5 | 50 | 17 | 2.94 |
| 6 | 126 | 35 | 3.60 |
| 7 | 322 | 88 | 3.66 |
| 8 | 834 | 204 | 4.09 |
| 9 | 2187 | 501 | 4.37 |
| 10 | 5797 | 1217 | 4.76 |

(H = 10 landed after filing: 1217 at both x = 1 and random x, 26.5 min for
the pair, `results/hankel_rank_h10.log`. Model read, 7 points: the
states/rank quotient's even-step ratios *increase* — 1.081, 1.136, 1.165 at
H = 4→6→8→10 — where a power-law quotient (floor base exactly 3, class
closed) requires them to decrease (1.201, 1.139, 1.106 at the fitted
exponent), and the power fit misses d₁₀ by +5.2% against the geometric fit's
+1.9%. Leaning: geometric quotient, floor base ≈ 2.79 — a real opening below
the incumbent's asymptotic 3 — but seven points with parity wobble is a
lean, not a verdict; the H = 11 closure (sized at 7.2 h/x-value, 0.37 GB,
predictions 3091 vs 3281, 6.2% apart) is the next discriminator and is
awaiting jasonp's ruling.)

**Measured growth rate.** Two-height pairwise bases (odd/even oscillation
smoothed): rank — H5→7: 2.28, H6→8: 2.41, H7→9: 2.39. States over the same
pairs: 2.54, 2.57, 2.61. So the exact minimal dimension grows at
**~2.4×/height against the frontier's ~2.6×**, and the compression factor
(4.37× at H = 9) grows slowly. (Caution from A-S6: the state count is exactly
Motzkin(H+1) − 1, whose ratio drifts up to 3; the rank's base plausibly
drifts too, so treat both as local ratios at H ≈ 9, not asymptotics.)

**Independently reproduced (cross-validation, 2026-08-11).** C's scaling lane
measured the same object by a separate Fliess-style forward/backward
reduction, without either of us knowing: C reports 2, 2, 5, 7, 18, 36, 89
for H = 1..7 against this probe's 6, 17, 35, 88 at H = 4..7 — identical up
to C's +1 convention (C's reduction counts one extra dimension for the
empty-prefix/initial covector). Growth bases agree (C ≈ 2.33 in a 2.0–2.57
band). Both first attempts also failed the same way (sampled Hankel
under-measures; both superseded by exact closure/reduction) — recorded in
both files. Unlike the matching-identity convergence, which had a common repo
source, these are two independent measurements of the same quantity: the
floor is the best-evidenced number in the campaign. Convention, confirmed
against this implementation: this probe's states are all post-first-column,
so its table is the Hankel *without* the empty-prefix row; the initial
(pre-first-column) vector is one extra dimension outside that row space,
which is exactly C's +1. Merged document quotes this file's convention
("rank excluding the empty-prefix row"), noting the ±1 is conventional.

**Independent consistency rail (B, 2026-08-11).** B extended the scalar
per-height floor — the atom degrees q_H of `results/triangle-structure.md`,
i.e. the Hankel rank of the single sequence C_H(n) — to q_7 = 181 and
q_8 = 462 (Berlekamp–Massey, two 31-bit primes, holdout-validated;
`results/atoms_ext/`). A d-dimensional column automaton with area marking
has per-height denominator degree ≤ d·H, so q_H ≤ d_H·H is forced, and it
holds: 181 ≤ 88·7, 462 ≤ 204·8. The scalar floor and this engine floor are
different quantities that must satisfy that inequality, and do — an
independent rail under the table above.

**Crossover: never — the candidate loses on compute growth.** The compressed
column transfer is a dense d×d matrix (d = rank), so the per-column cost of
the compressed engine grows as d² ≈ (2.4²) = **5.7×/height**, against the
incumbent's sparse states×H ≈ **2.65×/height**. From the two best measured
points: at H = 9 the compressed matvec is 501²/(2187·9) ≈ 12.8× the
incumbent's work and worsens ×2.15 per height. Memory is the only axis where
it wins (rank < states), and the win is bounded by the same measurement — see
the lower bound below. The one unprobed rescue: if the compressed d×d matrix
had exploitable structure (sparsity, low displacement rank) the d² could
drop; nothing measured here supports that and the burden is on it.

**The valuable half — the dimension floor, stated as a theorem with its
hypotheses explicit (the brief's "lower bounds" bullet).**

*Theorem (classical realization theory + the measured ranks).* Fix H, and let
𝒜 be any exact algorithm computing T-type strip counts that (i) sweeps the
strip left to right in any order whose cuts pass through every column
boundary; (ii) at each column boundary carries its entire summary of the
prefix as a vector v ∈ K^d, K a field — ℤ or any subring is covered, since a
ℤ-linear realization is a ℚ-linear one; (iii) updates v column-to-column by a
map that is K-*linear in v* (the map may depend arbitrarily, even
nonlinearly, on the new column's content); and (iv) reads the answer by a
K-linear functional. Then d ≥ rank of the Hankel matrix of f — measured
501 at H = 9, growth ~2.4×/height. This is the Kronecker–Schützenberger–
Fliess minimal-realization theorem (minimal linear representation dimension =
Hankel rank) [Sch61, CP71, Fli74; modern treatment BR11], applied at the
column-aligned cuts; per-H the rank is an exact mod-p certificate and rank
over ℚ ≥ rank mod p. Determinism is not load-bearing (weighted branching is
already linear); randomization is not an escape for always-correct
algorithms, since each seed fixes a realization that must itself satisfy the
bound.

*What is inside the fence*, regardless of what the carried state "means"
combinatorially: weighted automata over any field, temporal MPS/MPO along the
sweep, rank-compressed or basis-changed DPs, the incumbent kernels, B1's
algebra, and any future "carry a cleverer linear summary" idea — column-sweep
computation as such, under (i)–(iv). Hypothesis (iii) does not even require
the update maps to be the same at every column: Nisan's exact characterization
of noncommutative ABP width by the same Hankel ranks [Nis91; FLOS21] covers
layer-varying linear maps, closing the one linear escape the uniform
Fliess/Carlyle–Paz framing left open — B's lane has the ABP writeup; noted
here as a cross-reference, not restated.

*Where the defect lives* (B's rigorous nugget, reviewed and agreed): the
abstract completion pairing between matched interfaces is nonsingular over ℚ
— a Wilf–Lindström semilattice determinant, det = ∏ Möbius values ≠ 0
[Wil68, Lin69] — so the Hankel rank defect cannot originate in the pairing
itself; it lives entirely in the span of *realizable* suffix functionals
(and the area grading). Consistent with this probe: the measured columns are
realizable completions only, and their span at H = 9 is 501-dimensional
inside a 2187-state space whose abstract pairing is full-rank. This localizes
the open asymptotic question (does the floor's base tend to 3 like the
states, or stay strictly below?) in the growth of the realizable-suffix span.

*What escapes the hypotheses* — where a new idea must live to be worth
raising: a state map nonlinear in the carried state (hash-consing/
ZDD-style structural sharing measures *bits*, not linear dimension — the
floor bounds dimension, not information); coefficient structures that are not
subrings of a field (min-plus/boolean semirings — the rank theorem is false
there); algorithms that do not sweep (divide-and-conquer on both axes,
inclusion–exclusion over rectangles, closed forms); and
certificate-verification schemes, where the floor constrains the prover's
sweep but not the certificate's size.

Consequence: the best possible *memory* win over the incumbent inside the
fence is (2.65/2.4)^H ≈ 8× at H = 21, while a dense minimal realization pays
~5.7×/height in compute. Together with the banked spatial-cut negative, the
"exponential frontier is intrinsic" conclusion of
`results/boundary-push-tensornetwork.md` extends from the site-MPS family to
all of (i)–(iv) at the measured base.

**What binds first**: compute (dense d² per column), before memory ever
matters.

**Independence bar**: not applicable as an engine (it never crosses over);
the *rank certificates* themselves are engine-independent linear algebra.

## A-S2. Exact site-MPS / spatial bond dimension — already measured, banked, stands

No new probe; correcting the brief's premise on the record.
`results/boundary-push-tensornetwork.md` (2026-07-02, `experiments/
frontier_svd/`) measured the exact spatial-cut bond dimension of the real
frontier vector at H = 8, 10, 12, 14: χ = 21, 51, 127, 298 — growth
~2.4 per +2 in H, i.e. **~1.56×/height, genuinely below the frontier's
2.65×** — but the exact-MPS algorithm pays H·χ² storage, measured 2–5× worse
than the explicit frontier and worsening monotonically (0.45→0.26 ratio over
H = 8..14), with singular values that barely decay (χ_eff(10⁻⁶) ≈ full rank).
Under this brief's scoring: bond-dimension growth 1.56×/height, cost growth
χ² ≈ 2.4–2.65×/height with a measured constant ≥ 2× against the incumbent —
**crossover never**; the low-growth quantity is not the cost carrier.
Truncated MPS (χ_eff at 10⁻³: ~3× smaller than frontier, margin growing) is
an *approximate* oracle only — excluded by the exact-integers rule. Closed
then, still closed; A-S1 above closes the remaining (temporal) cut.

## A-S3. Guessing on the banked data: holonomic over ℚ, algebraic mod 2 and mod 3

**Mechanism.** If a(n) (A006770, banked n ≤ 40, `results/b006770_upload.txt`)
satisfied a P-recurrence, terms would cost O(n·poly) to extend; if a(n) mod p
were p-automatic (⟺ Σ a(n)xⁿ algebraic over F_p(x), Christol), a term mod p
would cost polylog. The repo's non-D-finiteness theorem
(`results/anisotropic-not-dfinite.md`) kills neither: it is about the
two-variable F(x,y), and its own text notes the isotropic a(x) is untouched.
The ternary spine (`results/ternary-spine.md`, the mod-3 cubic W³ = W²+t at
triangle level) motivates the mod-3 attempt specifically.

**Probe** (`scripts/probe_guessing_an.py`, 0.5 s, exact arithmetic —
Fractions over ℚ, F_p linear algebra mod 2, 3; every box required ≥ 8 surplus
equations to exclude spurious fits):

- **Holonomic over ℚ: negative.** No recurrence Σ_{i≤r} c_i(n) a(n+i) = 0
  with deg c_i ≤ d exists in any box (r, d) ∈ {(1, ≤11), (2, ≤9), (3, ≤6),
  (4, ≤4), (5, ≤3), (6, ≤2), (7, ≤2)} — every box with
  (r+1)(d+1) ≤ (40−r)−8.
- **Algebraic mod 2: negative.** No P(x, F) = Σ_{j≤J} c_j(x) F^j ≡ 0 (mod 2,
  mod x⁴¹) with J ≤ 5 and (J+1)(deg c + 1) ≤ 33.
- **Algebraic mod 3: negative**, same boxes. Notable given the ternary spine:
  whatever the mod-3 cubic governs at triangle level, it does not descend to
  a small algebraic equation for the isotropic diagonal a(x) mod 3 within
  this window.

**Growth rate / crossover**: none to report — no structure found to price.
**What binds**: the data window. 40 terms supports only the boxes above; a
recurrence of order 8+ or an F_p-equation of higher degree is untestable
without more terms, and more terms cost the incumbent's curve. Per the
brief's trap clause, even a hit would have been a prediction needing a
certifier; none materialized to certify. **Independence bar**: n/a.

## A-S4. B1's automaton against the floor (team-lead follow-on 2)

**Question.** B1's measured state growth (~2.9×/height, climbing) sits above
the 2.4 floor: is B1 compressible, or does it compute a harder function?

**Answer: neither in the way the question assumed — the 2.9 was a
cut-comparison artifact, and B1's function has the same Hankel rank as the
incumbent's.** Two parts:

- *Same function, same floor.* B1's end-of-sweep output is the same connected
  count f (the q-grading is internal; [q¹] extraction is a linear functional),
  and at a generic x its graded family has the same generic rank — the
  measured rank at random x equalled the x = 1 rank at every H. So the minimal
  linear realization of what B1 computes is the same ~2.4^H, and B1's
  representation is in principle compressible by S_B1/rank like everyone
  else's; its climbing ratio is a property of its basis, not of its function.
- *Cut-consistent state counts* (probe `scripts/probe_b1_column_states.py`,
  4 s: column-aligned reachable coincidence-partition states, BFS closure from
  all seeded partitions):

  | H | incumbent (column cut) | B1 (column cut) | rank (floor) |
  |---|---|---|---|
  | 4 | 20 | 20 | 6 |
  | 5 | 50 | 50 | 17 |
  | 6 | 126 | 126 | 35 |
  | 7 | 322 | 323 | 88 |
  | 8 | 834 | 843 | 204 |
  | 9 | 2187 | 2242 | 501 |

  The structure is exact, not approximate: B1's column states are *all* set
  partitions of the column's occupied runs where the incumbent's are the
  non-crossing ones — they coincide below H = 7 (crossing needs ≥ 4 runs), and
  the surplus is exactly the crossing patterns (+1 at H = 7 = Bell(4) − 14
  over the single 4-run fill). So on equal cuts B1's overhead over the
  incumbent is **2.5% at H = 9**, not 2.4× — the 2.4×/2.9-climbing figures in
  `results/second-source-candidates-B.md` compared B1's *mid-column window*
  states (13,733 at H = 10) against the strip engine's *column-cut* states
  (5,797), which is apples-to-oranges. B1's true asymptotic overhead does grow
  (all-partitions vs non-crossing is Bell-vs-Catalan in the run count), but in
  the project's range it is percent-level at column cuts.
- *Distance from the floor*: incumbent 4.36×, B1 4.47× above the minimal
  dimension at H = 9 — both rule choices sit essentially the same factor above
  the same floor, i.e. the floor looks rule-universal in exactly the sense the
  team lead conjectured, and the "price of rule-independence" at column cuts
  is the percent-level crossing surplus, not a growth-rate change.

**For B**: this settles the climbing-ratio question — window-cut artifact plus
a genuinely-growing crossing surplus — and quantifies the compressibility
headroom (4.5× at H = 9, growing like states/rank) that a change of basis
could in principle recover, at the price of dense arithmetic per A-S1's
crossover argument. **Correction to the first draft of this section** (which
said "percent-level in the project's range"): with the exact closed forms of
A-S6 the surplus is percent-level only near H = 10 — ×1.047 at H = 10,
**×1.243 at H = 14** (B1's target region), ×1.551 at H = 17, ×2.349 at H = 21.
Still far from the 2.4× the window comparison suggested, and now exact rather
than extrapolated.

## A-S6. THEOREM (no asterisk): the whole-column king TM state space is Motzkin(H+1) − 1

**Banked as a standalone result: `results/king-column-motzkin.md`** — full
proof, verification trail, scope guard, and novelty trail live there; this
section is the campaign-context record. Cite the banked note, not this file.

C's scaling lane observed whole-column states+1 = Motzkin(H+1) for H ≤ 7,
flagged as a fit. It is now a theorem: the reachability lemma is closed by an
explicit witness construction, machine-verified over **every** (fill,
non-crossing partition) pair at every H ≤ 9 — 3,419 cases, zero failures
(`scripts/probe_reachability_witness.py`, 0.1 s).

**Theorem.** The reachable whole-column states of the height-H king strip
transfer matrix (connectivity partitions with stranded-death, the incumbent
rule) are exactly the pairs (nonempty fill, non-crossing partition of the
fill's runs), and their number is Σ_{k≥1} C(H+1, 2k)·Catalan(k) =
**Motzkin(H+1) − 1**.

- **Lemma 1 (non-crossing is forced).** Distinct components of a strip prefix
  cannot interleave on a straight column cut. If runs a₁ < b₁ < a₂ < b₂ carry
  components A, A, B, B, the king path in the prefix joining a₁ to a₂ and the
  one joining b₁ to b₂ must cross; two 8-connected paths cross either by
  sharing a cell or diagonally through a common 2×2 window (the standard
  digital-topology fact behind the repo's own matching-pair Euler identities,
  `results/matching-pair-convention.md`), and all four cells of a 2×2 window
  are mutually king-adjacent — a K₄ — so A = B either way. This is why the
  king TM behaves "planar" at column cuts despite the graph being nonplanar.
- **Lemma 2 (reachability — closed).** Every (nonempty fill F, non-crossing
  partition π of its runs) is reachable, by rails-and-spurs: order the
  non-singleton blocks by nesting depth δ (1 = outermost, D = max); block at
  depth δ gets a vertical **rail** at column −2(D−δ+1) spanning its full row
  interval, plus a horizontal **spur** at the bottom row of each member run
  from its rail to column −1; then F. Separations, each pairwise: (a)
  distinct runs' bottom rows differ by ≥ 2 (the ≥1-row gap), so spurs never
  touch foreign runs or each other; (b) non-crossing makes block spans nested
  or ≥ 2 rows apart, so rails never touch foreign spurs or rails at the same
  column; (c) nested blocks get rails ≥ 2 columns apart with the inner one
  strictly closer to F, so inner spurs never reach outer rail columns and
  outer rails never abut inner rails; (d) every rail-block is horizontally
  contiguous from its rail to column −1, so nothing strands mid-sweep; (e) a
  spur end at column −1, bottom row of run R, is king-adjacent to R and to
  nothing else in F. The machine check covers all cases at H ≤ 9 including
  every boundary case (runs at rows 0 and H−1, depth up to ⌊(H+1)/4⌋).
- **Lemma 3 (count).** Fills of height H with k runs number C(H+1, 2k)
  (stars and bars), and Σ_k C(n, 2k)·Cat(k) = M_n is the classical
  Motzkin–Catalan identity [Aig98; OEIS A001006]; the −1 removes the empty
  fill (k = 0).
- **Corollary (B1, also asterisk-free).** B1's column states are all set
  partitions of the runs — reachability is immediate since B1's fresh/
  coincide color branching realizes any partition of the first column's runs
  as an initial state — giving Σ_{k≥1} C(H+1, 2k)·Bell(k), verified exactly
  at every measured H ≤ 9.

Verified against every measured point (probe run this session): incumbent
20, 50, 126, 322, 834, 2187, 5797 = M₅..M₁₁ − 1 exactly; B1 20, 50, 126,
323, 843, 2242 = the Bell sum exactly. Exact project-range values, no
extrapolation: H = 14: incumbent 310,571, B1 386,061 (×1.243); H = 17:
6,536,381 vs 10,137,558 (×1.551); H = 21: 400,763,222 vs 941,574,416
(×2.349).

Two consequences worth stating loudly:

- **The incumbent's asymptotic column-state base is 3, not 2.65.** Motzkin
  ratios drift up: ×2.75 at H = 14, ×2.81 at H = 21, → 3. The "~2.65×/height"
  figure banked from H ≈ 10 is a local ratio. Every crossover extrapolation
  in this campaign (including A-S1's and B's calibration) should use
  like-for-like local ratios or these closed forms — the A-S1 verdicts only
  strengthen under the correction, since the compressed d² route pays the
  square of whatever the true base is.
- **The engine-design "no Motzkin shortcut" note and C's observation are both
  right, and the reconciliation is sharper than "granularity"**:
  `docs/engine-design.md` says crossing partitions are *needed* — that claim
  is about the cell-at-a-time signature, whose jagged cut spans two partial
  columns, where Lemma 1's K₄ argument does not apply (the four cells of a
  potential crossing need not all lie on one side of a jagged boundary). At
  straight column cuts crossings are provably impossible; at jagged cuts they
  genuinely occur. Both statements stand, each about its own cut.

**Novelty, per the grep-before-claiming-new rule.** In-repo: the banked strip
state series 1, 3, 8, 20, 50, 126, 322, 834, 2187, 5797
(`results/strip-engine.md`) has been M(H+1) − 1 all along; the identification
was never written down. `docs/glossary.md` gestures "Motzkin-like, ≈ 3^W" at
the TMA signature (the jagged-cut object, which is *not* exactly Motzkin);
nothing else in results/, docs/, or paper/ states the whole-column count
(grepped Motzkin, non-crossing, Catalan in state-count contexts). Literature:
Motzkin-dimension transfer matrices are standard for SQUARE-lattice models —
Jensen's polyomino signature encoding is Motzkin-path-based
(`papers/refs-transfer-matrix.md`), and the Salas–Sokal chromatic/Potts TM
line states dim = M_{m−1} for square-lattice non-crossing
non-nearest-neighbor partitions (e.g. arXiv:cond-mat/0108144 and the
"Transfer matrices and partition-function zeros" series). The king-lattice
instance — states = (fill, NC partition of runs), count M(H+1) − 1, with
non-crossing forced on a *nonplanar* graph via the 2×2-K₄ argument — was not
found: searched king graph / next-nearest-neighbor / NNN transfer matrix with
non-crossing partitions and Motzkin, on top of C's coverage-map sweep
(polyplets, polykings, pseudo-polyominoes, NNN site animals — the king TM
literature row is empty). Stated per repo practice: **not found**, which is
not proof of absence.

- [Aig98] M. Aigner, "Motzkin numbers," European J. Combin. 19 (1998)
  663–675. DOI 10.1006/eujc.1998.0235.
- [SS01b] J. Salas & A. D. Sokal / S.-C. Chang & R. Shrock lines on Potts TM
  dimensions for square-lattice strips (Motzkin-number dimensions for
  non-crossing partition bases): e.g. arXiv:cond-mat/0108144;
  arXiv:cond-mat/0004330.

## A-S5. Follow-on 3, conditional: where the honest open question now sits

With A-S1's fence stated, the open question is precisely: can a *nonlinear*
column-sweep state map, or a non-sweep method, compute exact T(n,H) below
~2.4^H? Two measured facts frame it: the information the state must determine
is a completion functional of rank ~2.4^H (so any method whose state
determines that functional *linearly* is fenced), and structural-sharing
representations (ZDD-style) compress bits, not dimension — nobody has
measured whether the incumbent's frontier vectors have exploitable *bit*
structure (shared sub-patterns, low-entropy count distributions). That
bit-compression measurement is the one cheap probe this file leaves open; it
attacks storage only, not arithmetic work, and the a(40)-closed project
status means it is priced for the record, not for a run.

## Coordination notes

- C_H(x) degree growth in H is C's probe (per team-lead assignment); not
  duplicated here. The banked atom degrees (deg ψ_H = 1, 2, 4, 9, 29, 68,
  181, 462, 1254, 3289, growth ~2.7/level,
  `results/anisotropic-not-dfinite.md`) already say the per-height rational
  structure tracks frontier size — the mod-p half assigned to this lane is
  the a(x) mod p probe above.
- Mod-p per-column recurrences as a cheap *computation* route are exhausted
  ground (CRT/mod-p is on the second-source brief's exhausted list; a mod-p
  count is not a count), and nothing here re-proposes them.

## Citations

- [Sch61] M. P. Schützenberger, "On the definition of a family of automata,"
  Information and Control 4 (1961) 245–270. DOI 10.1016/S0019-9958(61)80020-X.
- [CP71] J. W. Carlyle & A. Paz, "Realizations by stochastic finite
  automata," J. Comput. Syst. Sci. 5 (1971) 26–40. DOI
  10.1016/S0022-0000(71)80005-3. (Finite Hankel rank ⟺ realizable; verified
  via the ScienceDirect record this session.)
- [Fli74] M. Fliess, "Matrices de Hankel," J. Math. Pures Appl. 53 (1974)
  197–222. (Minimal realization dimension = Hankel rank; cited universally by
  the weighted-automata literature — journal/volume verified via secondary
  sources this session; no free copy located, one web pass →
  `papers/MISSING.md` block below.)
- [BR11] J. Berstel & C. Reutenauer, *Noncommutative Rational Series with
  Applications*, Encyclopedia of Mathematics and its Applications 137,
  Cambridge UP, 2011. (Modern treatment of the rank/realization theorem.)
- [Nis91] N. Nisan, "Lower bounds for non-commutative computation," STOC
  1991. DOI 10.1145/103418.103462.
- [FLOS21] N. Fijalkow, G. Lagarde, P. Ohlmann, O. Serre, comput. complexity
  30 (2021). DOI 10.1007/s00037-021-00214-1. (Both via B's lane; ABP width =
  Hankel ranks, layer-varying case.)
- [Wil68] H. S. Wilf, Bull. Amer. Math. Soc. 74 (1968); [Lin69] B. Lindström,
  Proc. Amer. Math. Soc. 20 (1969). (Semilattice determinant nonsingularity;
  via B's lane, reviewed here.)

**For `papers/MISSING.md`** (merge wave applies, same protocol as the
second-source file): Fliess 1974 as above — wanted as the primary for the
minimal-realization theorem behind A-S1's floor; searched once by
title+journal, paywalled/no free copy found.

## Probe artifacts

- `scripts/probe_hankel_rank.py` — sampled version (kept for the record of
  why sampling under-spans); superseded.
- `scripts/probe_hankel_rank2.py` — exact observability closure; the numbers
  in A-S1's table. H ≤ 9 foreground 93 s; H = 10 in tmux window `hankel10`,
  log `results/hankel_rank_h10.log`.
- `scripts/probe_guessing_an.py` — A-S3, 0.5 s.
- `scripts/probe_b1_column_states.py` — A-S4, 4 s.
- `scripts/probe_reachability_witness.py` — A-S6 Lemma 2 machine check, all
  3,419 (fill, NC-partition) pairs at H = 4..9, zero failures, 0.1 s.
- Nothing committed; nothing in /tmp; no binaries built.
