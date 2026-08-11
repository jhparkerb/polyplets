# Scaling exploration — merged findings of the three-lane campaign

2026-08-11. The canonical deliverable of `docs/scaling-exploration-brief.md`,
synthesised from the lane files, which remain the working record:

- `results/scaling-exploration-A.md` — algebraic/analytic: temporal Hankel
  rank, the realization-theory floor, the Motzkin theorem, guessing boxes
- `results/scaling-exploration-B.md` — complexity/semiring: the scalar floor
  q_H, Nisan made precise, generality of the q² trick, the open base question
- `results/scaling-exploration-C.md` — literature + cheapest probes:
  automaticity, C_H degrees, minimal-dimension cross-check, the Motzkin
  observation, the Nisan find

## 1. The question and the scoring

Is there a way to compute T(n,H) whose cost **grows more slowly** than the
frontier transfer matrix's, even if far slower today? A method 1000× slower
at H = 10 with base 2.0×/height instead of the incumbent's ~2.65 is a win;
wall time is not the metric. Every candidate below is scored as a growth
base with a crossover height computed from at least two measured points, and
negatives carry the number that killed them.

**The campaign's one-line verdict**: no candidate crosses over, inside or
past the project's range. What it produced instead is stronger than a
survivor — an unconditional lower bound fencing the entire class every
engine here lives in, exact closed forms for both engines' state spaces, and
one sharply-posed open question on which any future attempt turns.

## 2. The class bound, stated once

**The floor.** Let f be the strip word function (alphabet = column fills,
f(w) = x^{cells}·[w is one king-connected component]). Any exact algorithm
that (i) sweeps column boundaries, (ii) carries its entire prefix summary as
a vector over a field, (iii) updates it column-to-column by a map linear in
the carried vector (arbitrary in the new column), and (iv) reads the answer
linearly, has dimension ≥ the Hankel rank of f at the cut. This is classical
realization theory (Schützenberger 1961; Carlyle–Paz 1971; Fliess 1974;
modern treatment Berstel–Reutenauer 2011) for uniform transitions, and
**Nisan's theorem [Nis91] extends it to layer-varying maps** — an engine
free to change its update rule per column is still an algebraic branching
program, and ABP layer width is *exactly* the Hankel block rank (modern form
[FLOS21]). The citation chain: C's field sweep found Nisan; B lined its
hypotheses up against A's realization framing and closed the layer-varying
escape. The floor is unconditional, not fitted.

**The measured floor** (convention: rank of f's Hankel proper, excluding
the empty-prefix row; C's independent reduction gives rank+1, the offset
verified in code as exactly the initial-vector dimension):

| H | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|
| Hankel rank d_H | 6 | 17 | 35 | 88 | 204 | 501 | 1217 |
| incumbent states | 20 | 50 | 126 | 322 | 834 | 2187 | 5797 |
| states/rank | 3.33 | 2.94 | 3.60 | 3.66 | 4.09 | 4.37 | 4.76 |

(d_10 at both x = 1 and random x, exact closure, 26.5 min/pair,
`results/hankel_rank_h10.log`.) **Cross-validated in the strongest sense
available**:
A's observability closure and C's forward/backward reduction are two
independent implementations, written blind to each other, agreeing exactly
at all four overlapping heights — and both lanes' first *sampled* attempts
under-measured the same way before being superseded by exact closure, which
is recorded in both files. The scalar companion floor (B): q_H = deg of
C_H's minimal recurrence = 1, 2, 4, 9, 29, 68, 181, 462, tied to the engine
floor by q_H ≤ d_H·H, which holds at every measured point.

**Correction 2026-08-11 (post-merge grep): 181 and 462 are NOT new, and the
sequence was already banked two terms further.** deg ψ_H = 1, 2, 4, 9, 29,
68, 181, 462, **1254, 3289** for H = 1..10 is in
`results/anisotropic-not-dfinite.md` (and repeated in
`results/triangle-combinations.md`, `results/open-conjectures.md`,
`docs/onset-defect-plans.md`, and the L4 paper) — lane A's own coordination
note cites it; lane B measured H = 7, 8 independently and the merge adopted
B's "(new)" without checking A's citation. What the measurement actually
bought is a **cross-method confirmation** — Berlekamp–Massey on C_H(n) mod
two primes agreeing with the ψ_H denominator degrees obtained by factoring —
which is worth having and is not a new point. Consequence for §7: the q_9
probe is **redundant, and its target value is known to be 1254**; the
verdict file's non-convergence (BM order 1125 on 2250 terms) is consistent
with that, since resolving order 1254 needs upward of 2600 terms.

**What the fence encloses**: weighted automata over any field, temporal
MPS/MPO, rank-compressed or basis-changed DPs, the incumbent kernels, B1,
and every future "carry a cleverer linear summary" idea. **The named
escapes, kept visible**: nonlinear state maps; non-field semirings
(tropical/pure DP — bound separately and more strongly by [KN25];
boolean/monotone sharing unmeasured — A-S5's one open probe, priced for the
record only); non-sweep methods (divide-and-conquer, rectangle
inclusion–exclusion, closed forms); certificate schemes (the floor binds
the prover's sweep, not the certificate).

**Why the floor is not an engine**: the minimal realization is dense, so
running at dimension d_H costs d² ≈ 5.4–5.7×/height against the incumbent's
sparse ~2.65 local — 12.8× more work already at H = 9, worsening
×2.15/height (A-S1; C's S3 concurs independently). Crossover: never. The
only rescue would be exploitable structure (sparsity, low displacement
rank) in the minimal-basis transfer; nothing measured supports it and the
burden sits there.

## 3. The closed forms and the Motzkin theorem

**The theorem is banked standalone in `results/king-column-motzkin.md`** —
full proof (the K₄ lemma written out, rails-and-spurs with the five
separation facts), the three-implementation verification trail, the
jagged-vs-column scope guard, the novelty trail, and the provenance split.
That file is the citation target; this section is the campaign-context
summary. Provenance: C observed the identity and verified the bijection
two-sidedly (H ≤ 7); A supplied the mechanism and the witness construction;
the strip engine's banked census is a third, independent numerical rail.
Verified at **every H = 1..10 across three implementations**.

- **THEOREM (no asterisk): incumbent whole-column states =
  Σ_{k≥1} C(H+1,2k)·Catalan(k) = Motzkin(H+1) − 1.** A state is exactly
  (nonempty fill, non-crossing partition of its runs). Lemma 1
  (non-crossing forced): crossing king paths share a 2×2 window, which is
  a K₄, so crossing components merge. Lemma 2 (every non-crossing pattern
  reachable) — **CLOSED by A's rails-and-spurs witness**: non-singleton
  blocks ordered by nesting depth δ, each given a vertical rail at column
  −2(D−δ+1) spanning its row interval plus a horizontal spur at the bottom
  row of each member run reaching column −1; five pairwise separation
  facts make it exact (distinct runs' bottom rows differ ≥ 2; NC spans
  nested or ≥ 2 apart; nested rails ≥ 2 columns apart, inner strictly
  closer, so inner spurs never reach outer rail columns; every rail-block
  horizontally contiguous, so nothing strands; a spur end touches exactly
  its run). Machine-verified over every (fill, NC-partition) pair at every
  H ≤ 9 — 3,419 cases, zero failures
  (`scripts/probe_reachability_witness.py`). The Motzkin step is classical
  (Aigner 1998, DOI 10.1006/eujc.1998.0235; OEIS A001006).
- **B1 column states = Σ_{k≥1} C(H+1,2k)·Bell(k)** — also asterisk-free:
  B1's colour branching realizes any partition of the first column's runs,
  so reachability is immediate. The price of B1's rule-independence is
  therefore Bell-over-Catalan: ×1.047 at H = 10, ×1.243 at H = 14, ×1.551
  at H = 17, ×2.349 at H = 21 (exact values: 310,571 vs 386,090 at H = 14;
  400,763,222 vs 941,584,983 at H = 21).
- **Scope: a fact about cut geometry, not a discrepancy.** At straight
  column cuts, crossings are provably impossible (Lemma 1). At the jagged
  cell-at-a-time cut, the K₄ argument genuinely fails — a crossing's four
  cells need not lie on one side of a jagged boundary — and crossing
  partitions genuinely occur. `docs/engine-design.md`'s "no Motzkin
  shortcut — crossing partitions allowed" is a true statement about the
  jagged cut; this theorem is about the straight cut; both stand, each
  about its own geometry.
- **Novelty and provenance, so nobody overclaims**: in-repo, the banked
  strip state series 1, 3, 8, …, 5797 (`results/strip-engine.md`) has been
  M(H+1) − 1 all along, the identification never written down — the
  identity sat in banked data unrecognized. In the literature,
  Motzkin-dimension transfer matrices are standard vocabulary for
  *square-lattice* models (Jensen's signature encoding, `docs/glossary.md`'s
  "Motzkin-like ≈ 3^W"; Salas–Sokal's Potts line has dim = M_{m−1} for
  square-lattice non-crossing bases, arXiv:cond-mat/0108144 et seq.). What
  was not found: the king-lattice instance, where non-crossing is FORCED
  on a nonplanar graph by the 2×2 K₄ — not found is not proof of absence.
  That same 2×2 mutual-adjacency fact is the mechanism behind the
  matching-pair Euler identities of the second-source campaign
  (`results/matching-pair-convention.md`) — one structural fact surfacing
  on two fronts.

## 4. THE open question (PENDING B) — is the floor's base below 3, or does everything converge?

Prominence deliberate: this is the question the whole brief turns on, and it
is unresolved. **Every base measured in this campaign is pre-asymptotic and
climbing**: the incumbent's true base is exactly 3 (Motzkin; the banked
"2.65" is the local ratio near H ≈ 10 — ×2.75 at H = 14, ×2.81 at H = 21),
B1 sits above it, and the floor's local ratios climb 2.28 → 2.46. The
decisive object is the quotient states/rank (3.33 → 4.76 over H = 4..10):
growing like θ^H means floor base < 3 and a real opening; growing like H^c
means floor base = 3 and **the linear class is closed with no opening at
all**. **With the seventh point (d_10 = 1217) the evidence LEANS
geometric**: the even-step quotient ratios increase (1.081, 1.136, 1.165 at
H = 4→6→8→10) where a power-law quotient requires them to decrease (fitted
1.201, 1.139, 1.106), and the power fit misses d_10 by +5.2% against the
geometric fit's +1.9% — floor base ≈ 2.79, a real opening below the
incumbent's 3, IF the lean holds. A lean is not a verdict: H = 11 (7.2 h
per x-value; the models predict 3091 vs 3281, ~6%) is the next
discriminating point and is **with jasonp**. The rigorous nugget on the
other side stands (B): the completion pairing on the partition lattice is
nonsingular over ℚ (Wilf–Lindström semilattice determinant, all Möbius
values nonzero), killing the most natural mechanism for exponential rank
collapse. Do not cite either outcome as settled.

## 5. Dead directions, with their numbers

| direction | killed by | lanes |
|---|---|---|
| a(n) mod 2 / mod 3 automatic (polylog terms via Christol) | no algebraic relation: C's 7 grids × 2 primes on 40 banked terms (surplus 5–17); A's independent boxes (J ≤ 5, ≥ 8 surplus) — mod 3 negative is notable against the ternary spine, which lives at triangle level and does not descend | **two-source: A + C** |
| P-recurrence / holonomic a(n) over ℚ | A's exact swept boxes, every (r,d) with (r+1)(d+1) ≤ 32−r; consistent with `results/triangle-structure.md` §3 | A |
| C_H recurrence degrees as a generator | same base as the incumbent (q ratios 2.66, 2.55 at the new points), constant ≈ 0.55×states, and circular (fitting q_H needs 2q_H terms) — C measured, B independently validated with holdout at two primes | **two-source: B + C** |
| Spatial-cut exact MPS | banked negative stands (`results/boundary-push-tensornetwork.md`: H·χ² is 2–5× the frontier, worsening); the brief's "nobody has measured it" was true only of the temporal cut | A (record correction) |
| Temporal Hankel compression as an engine | dimension win real (4.4× at H = 9, growing) but dense d² costs 5.4–5.7×/height vs 2.65 local: crossover never | **two-source: A + C** |
| B1 as a *scaling* candidate | equal-cut states are the incumbent's +2.5% at H = 9 (Bell-vs-Catalan, closed forms above); the "2.9×/height climbing" figure was a window-vs-column-cut artifact | A + B (B retains the window census as B1's own resource curve) |
| Subset-lattice transforms / subset convolution | 2^{HW} states; HW = 840 at the frontier | B (by inspection) |
| GF(2) rank-based reduction (base 2.0) | unsound for exact counting (multiplicity lost); the counting variant lands back at the floor | B ([BCKN15]) |
| CSP counting dichotomies | classification + conditional DP-optimality results, no method | C |
| Non-integer-q Potts numerics | approximations only; the exact member is B1, already bound by the floor | C |
| Nonlinear/boolean bit-sharing compression | NOT dead — unmeasured; priced for the record only (a(40)-closed project) | A-S5, open |
| mod-p per-height arithmetic shadows (GF(p) Hankel ranks of C_H) | NOT dead — B's probe in flight (`results/atoms_ext/`); would give a(n) mod p structure, not a count | B, in flight |

## 6. Corrections this campaign produced that reach outside it

Findings for jasonp; the affected files are deliberately NOT edited.

1. **"~2.65×/height" is a local ratio, not the base.** The incumbent's
   column-state count is exactly Motzkin(H+1) − 1, asymptotic base 3.
   `results/strip-engine.md` (and anything else extrapolating on 2.65)
   quotes the local H ≈ 10 ratio; the closed form is what a referee should
   see, and crossover claims should use like-for-like local ratios or the
   closed forms.
2. **Window cuts and column cuts are different objects**, and conflating
   them produced two wrong cross-engine comparisons in one day (B1 "2.4×
   the strip's states"; the "2.9×/height climbing" base). Window censuses
   remain correct as an implementation's own resource curve; cross-engine
   comparisons must be cut-matched. The second-source canonical file
   (`results/second-source-candidates.md` §5.1) carries the same warning
   where it bit.

## 7. In flight / markers

- A: nothing in flight — d_10 landed (§2 table), the Motzkin theorem is
  banked standalone (`results/king-column-motzkin.md`). The H = 11 floor
  point that would firm §4's lean (7.2 h per x-value) is a jasonp decision,
  not a running job.
- B: ~~q_9 verdict~~ **cancelled 2026-08-11** — q_9 = 1254 is banked (§2
  correction); `results/atoms_ext/q9_verdict.txt` records only that 2250
  terms are too few to resolve it. Live: mod-p shadow ranks;
  the H = 12–13 closure sizing that decides §4. (B1's memory ceiling
  RESOLVED 2026-08-11 — the window census is the true working set; tier
  table in `results/second-source-candidates.md` §2.)
- Left open and priced only: A-S5's bit-compression probe.

## 8. Citations (load-bearing here; lane files carry the rest)

- [Sch61] Schützenberger, Inf. Control 4 (1961) 245–270,
  DOI 10.1016/S0019-9958(61)80020-X.
- [CP71] Carlyle & Paz, J. Comput. Syst. Sci. 5 (1971) 26–40,
  DOI 10.1016/S0022-0000(71)80005-3.
- [Fli74] Fliess, J. Math. Pures Appl. 53 (1974) 197–222 — unheld;
  `papers/MISSING.md`.
- [BR11] Berstel & Reutenauer, *Noncommutative Rational Series with
  Applications*, CUP 2011.
- [Nis91] Nisan, STOC 1991, 410–418, DOI 10.1145/103418.103462.
- [FLOS21] Fijalkow, Lagarde, Ohlmann & Serre, comput. complexity 30 (2021),
  DOI 10.1007/s00037-021-00214-1.
- [MS82] Mehlhorn & Schmidt, STOC 1982, DOI 10.1145/800070.802208.
- [Aig98] Aigner, European J. Combin. 19 (1998) 663–675,
  DOI 10.1006/eujc.1998.0235.
- [KN25] Kluk & Nederlof, arXiv:2512.23121. [BCKN15] arXiv:1211.1505.
- [Lin69] Lindström, Proc. AMS 20 (1969) 207–208. [Wil68] Wilf, Bull. AMS 74
  (1968) 960–964.
