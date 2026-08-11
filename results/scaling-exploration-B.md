# Scaling exploration — Teammate B (complexity and semiring structure)

Date: 2026-08-11. Lane per `docs/scaling-exploration-brief.md`: lower bounds,
generality of the q² trick, and whether B1's growth can be lowered. Probe
tooling: `build/cutcount_b1 --modp` (mod-p series mode added to the validated
B1 engine — its exact mode matches the banked triangle 400/400 at H≤10 n≤40),
`scripts/atoms_bm.py` (Berlekamp–Massey with banked cross-check and holdout),
`scripts/run_atoms_h9.sh`. All series runs at two 31-bit primes
(2147483629, 2147483587); every reported order requires: first 40 terms equal
to the banked triangle mod p, BM order computed on a 75% prefix, exact
prediction of the held-out 25%, and agreement between the primes.

## Headline: the scalar Hankel floor q_H, measured to H=8 — read jointly with A's temporal floor

**Mechanism.** C_H(x) is rational; the degree q_H of its minimal denominator
(the repo's "atoms", `results/triangle-structure.md`, known 1, 2, 4, 9, 29, 68
for H ≤ 6) is the rank of the Hankel matrix of the sequence C_H(n). By
Carlyle–Paz/Fliess [CP71, Fl74], Hankel rank is *exactly* the minimal dimension
of any weighted automaton computing the series — i.e., a floor under every
linear-scan engine: the kink kernel, the strip TM, B1, and any semiring
reformulation whose per-column update is linear in a carried state vector. (A
column-sweep automaton with d states and area marked by x has transfer matrix
polynomial in x of degree ≤ H, so its denominator degree is ≤ dH: the floor on
*states* is q_H/H; the floor on the *base* is lim q_H^{1/H}, unaffected by /H.)

**Measurement** (this session; machinery validated by recovering all six known
atoms exactly under the same protocol before producing new ones):

| H | q_H (atom degree) | ratio | strip states s_H | ratio | q_H/s_H |
|---|---|---|---|---|---|
| 4 | 9 | 2.25 | 50 | 2.50 | 0.18 |
| 5 | 29 | 3.22 | 126 | 2.52 | 0.23 |
| 6 | 68 | 2.34 | 322 | 2.56 | 0.21 |
| 7 | **181** (new) | 2.66 | 834 | 2.59 | 0.22 |
| 8 | **462** (new) | 2.55 | 2187 | 2.62 | 0.21 |
| 9 | (run in flight, `results/atoms_ext/q9_verdict.txt`) | | 5797 | 2.65 | |

(s_H from `results/strip-engine.md`'s measured state counts, shifted to align
heights; the alignment constant does not affect ratios. Per A-S6 these have
the exact closed form Motzkin(H+1) − 1, so the incumbent's *asymptotic*
column base is Motzkin's 3 — the banked 2.65 is the local ratio near H = 10,
already ×2.75 at H = 14 and ×2.81 at H = 21. Local-vs-asymptotic applies to
every ratio quoted in this file; crossover statements below compare local
ratios at matched heights.)

**Two floors, reconciled** (coordinated with Teammate A, whose
`results/scaling-exploration-A.md` §A-S1 measured the *temporal* Hankel rank —
the observability dimension d_H of the column-sweep word function: 6, 17, 35,
88, 204, 501 at H = 4..9, base ~2.4×/height). These are different objects and
they cross-check: a d-dimensional column automaton with area marking has
scalar denominator degree ≤ d·H, so q_H ≤ d_H·H — measured: 181 ≤ 88·7,
462 ≤ 204·8 ✓ — and conversely d_H ≥ q_H/H (58 ≤ 204 at H = 8 ✓). d_H is
the floor for *engines* (per-column linear state maps); q_H is the floor for
*series/recurrence* representations of one C_H.

**Reading, both directions:**

1. **Lower bound (the negative the brief asks for).** No weighted-automaton /
   linear-DP method — over any field, with any state encoding, any
   connectivity bookkeeping or none — computes the strip word function in
   dimension below d_H (~2.4×/height measured, A-S1), and no linear
   representation of the single series C_H beats q_H (this section; scalar
   ratios 2.25, 3.22, 2.34, 2.66, 2.55 — noisier, consistent with a base in
   the 2.4–2.6 range). Rank bound in the Mehlhorn–Schmidt sense [MS82]
   across the column cut; certificates computable and holdout-verified.
2. **Upper bound / compression ceiling — and why the floor's base gap is
   unusable.** A dimension-d_H engine exists (observability closure) and a
   dimension-q_H companion recurrence exists per height. The dimension gap to
   the incumbent is real (4.4× at H = 9 and slowly growing, A-S1) and the
   floor's base ~2.4 is genuinely below the incumbent's ~2.65 — but the
   compressed transfer is dense, so its per-column cost grows as d² ≈
   5.7×/height against the incumbent's sparse ~2.65×/height: **crossover
   never** (A-S1's measured argument; 12.8× more work already at H = 9,
   worsening ×2.15/height). The only rescue would be exploitable structure
   (sparsity/displacement rank) in the minimal-basis transfer; nothing
   measured supports it and the burden sits there.

**Crossover:** none inside or outside the project range — the dimension floor
is below the incumbent but every known way to *run* at the floor pays a
squared base. Recorded as the campaign's primary negative for the linear
class, permanent rather than an engineering verdict.

**What the bound does NOT cover, stated precisely:**

- Methods not linear in a per-column state. The known escape hatches are
  closed by existing repo negatives: P-recursive shortcuts fail already for
  H = 3 (`results/triangle-structure.md` §3, orders ≤6 × degrees ≤3, exact
  nullspace), the anisotropic GF is not D-finite
  (`results/anisotropic-not-dfinite.md`), and object-materialising methods are
  killed by the a(22) fleet measurement. Guessing (BM/Padé) produces
  predictions, not counts — this probe itself is a guesser and is offered as a
  *bound*, not an engine.
- Sub-linear-communication tricks for the *decision* problem; counting is what
  q_H binds.
- **B1 does not escape it.** B1 is a weighted automaton (states = colour
  patterns, transitions linear, output a coefficient functional); its [q¹]
  output series is C_H, so Fliess applies verbatim. B1's win was rule
  independence; on this brief's axis it is bound like everything else.

## The floor is unconditional: Nisan's ABP characterization (citation found by C, made precise here)

**Statement.** Fix the word function f over the column alphabet (a column fill
is a letter; f(w) = the count contribution of the fill sequence w, area marked
at a numeric x). Any engine that sweeps columns carrying a finite LINEAR
summary over a field — with per-column update maps that may differ from column
to column — is an algebraic branching program over that alphabet, and Nisan's
theorem [Nis91] says the minimal width of layer t is EXACTLY the rank of the
Hankel block (prefixes of length t × suffixes) at that cut. So A's measured
ranks (d_H = 6, 17, 35, 88, 204, 501 at H = 4..9, §A-S1) are not a fitted
estimate: they are an unconditional width floor for the whole class. Modern
treatment: [FLOS21].

**Hypotheses, lined up against A-S1's realization framing.** Carlyle–Paz/
Fliess [CP71, Fl74] bind *uniform* realizations — one transition per letter,
used at every position. Nisan binds *layer-varying* linear maps: an engine
free to change its update rule per column index (as B1's cell maps vary with
row, and as any hand-tuned per-column optimization would) is still an ABP and
still floored. That closes the one linear escape the realization framing left
open. What NEITHER framing binds, stated so the escapes stay visible:
non-field semirings (tropical/pure DP — bound separately and more strongly by
[KN25]; boolean/monotone sharing, unmeasured — A-S5), and nonlinear state
maps (A-S5's open door).

**Both engines are ABPs in the required sense.** The incumbent: layers =
columns, layer vertices = its connectivity partitions (width Motzkin(H+1) − 1
exactly, A-S6), transitions linear with 0/1-with-multiplicity integer
weights. B1: same shape, width Σ_k C(H+1,2k)·Bell(k), transitions linear
over ℚ per graded coefficient (the (q−b) weights and the ℤ[q]/q² grading are
just two ℚ-linear coordinates). Both therefore sit provably ≥ d_H, and
measured they sit ~4.4× above it at H = 9. Neither escapes; nothing
column-linear does.

**Is the floor's base genuinely below 3, or does everything converge to
Motzkin's 3?** (C's caution; currently the most valuable open question in
this brief.) The measured bases all climb: incumbent local ratio 2.65 → 2.81
(H = 10 → 21, exact from the closed form; limit exactly 3), B1 above that,
floor local ratio 2.28 → 2.46 (A-S1). The floor-vs-states quotient
states/rank = 3.33, 2.94, 3.60, 3.66, 4.09, 4.37 (H = 4..9) is the decisive
object: if it grows like θ^H (θ ≈ 1.056 fits) the floor's base is ≈ 2.83 < 3
and a real opening exists; if it grows like H^c (c ≈ 0.34 fits equally well)
the floor's base is also 3 and **the linear class is closed with no opening
at all**. Six points cannot separate the two models — at H = 10 they predict
ranks 1280 vs 1256, inside noise. They separate at H ≈ 13 (predicted
quotients 4.94 vs 5.44, ~10%): the discriminating measurement is A's exact
observability closure at H = 12–13, whose cost grows with states² and needs
sizing before anyone commits.

One rigorous nugget toward "base 3, closed": the pointwise completion pairing
at a fixed interface of k runs is NONSINGULAR over ℚ — on the dual of the
partition lattice Π_k, det[𝟙(p ∨ q = 1̂)] = ∏_z μ(z, 1̂) by the
Wilf–Lindström semilattice determinant [Lin69, Wil68], and in Π_k
μ(z, 1̂) = (−1)^{b−1}(b−1)! ≠ 0 for every z. So the rank defect measured in
d_H cannot come from the completion pairing itself; it must live in the span
of *realizable* suffix functionals (which weighted completions actual column
words generate) and the area grading. That kills the most natural mechanism
for an exponential rank collapse, and tilts — without deciding — toward the
polynomial-quotient reading, i.e., floor base 3 and a fully closed class.
Flagged for A's review; the H = 12–13 closure decides it empirically.

## B1's own growth: the climbing ratio was a cut artifact — corrected per A-S4

My census numbers (107,241 / 306,858 / 891,074 at H = 12/13/14, ratios
climbing 2.72 → 2.90) count mid-column *window* states — the H+1-cell window
at a column boundary still holds a stale cell — and are therefore not
cut-consistent with the strip's column-state counts. They remain the correct
*resource curve for my implementation* (they priced the dalby calibration
correctly), but the cross-engine comparison drawn from them was wrong.
Teammate A measured both engines on equal column cuts
(`results/scaling-exploration-A.md` §A-S4, `probe_b1_column_states.py`): B1's
column states are ALL set partitions of the occupied runs vs the incumbent's
non-crossing ones — identical below H = 7 (crossing needs ≥ 4 runs), then
20, 50, 126, 323, 843, 2242 vs 20, 50, 126, 322, 834, 2187: **+2.5% at
H = 9**, a percent-level (though genuinely growing, Bell-vs-Catalan over run
count) surplus in the project's range, not the 2.4× my window numbers
suggested. B1's output has the same Hankel rank as the incumbent's (A-S4), so
the floor treats them identically. Verdict unchanged in substance, corrected
in reason: B1 is an independence artifact with essentially the incumbent's
scaling, its real overhead being the payload constant (41 areas × 3
coefficients × 32 B), not the state count.

## How far the q² trick generalises — analysis, with the exponent question answered

The trick: a global statistic (component count) becomes the grading of a
partition function with local weights, computed in a quotient ring (ℤ[q]/q²)
just big enough to expose the wanted coefficient. What else fits: any
statistic that grades a local-weight partition function — cycle rank/Euler
characteristic (local, free), colourings, Tutte/Potts specialisations. What
none of them buys: a base. Every such reformulation is still a linear scan
with a carried state, so the Hankel floor applies — **the "actual exponent"
of algebraic DP on this problem is the same ~2.6, not the textbook 2^tw**, and
textbook improvements target decision/optimization, not exact counting:

- GF(2) rank-based reduction (cut basis, dim 2^{H−1}, base 2.0): sound for
  existence, unsound for exact ℤ-counts (multiplicity is lost; the counting
  variant [BCKN15] works over the full cut space and lands back at the floor).
- Möbius/zeta over the subset lattice, subset convolution: state space 2^{HW};
  at the frontier HW = 840 cells this is 2^840 — dead on arrival by
  inspection, no probe needed.

**One measured crack — arithmetic shadows.** Counting mod small p is not
bound by the ℚ-rank floor (the relevant object is the GF(p) Hankel rank,
which can be lower). Probe (same protocol, BM over GF(p)):
`results/atoms_ext/` — mod-2 and mod-3 minimal LFSR orders of C_H(n), H ≤ 8
(distinct from A-S3, which tested a(n)-level algebraicity mod 2, 3 — negative;
this asks whether the per-height rational structure collapses mod p):
[PENDING — filled in when the shadow probe lands.]
If those ranks grow with a smaller base, a cheap engine exists for a(n) mod 2
(resp. 3) — not a count, but a strong structural invariant, and the honest
bridge to the brief's automatic-sequences item and the repo's ternary spine.

## Kill list / negatives ledger (this lane)

| item | verdict | number |
|---|---|---|
| Exact MPS / bond-dimension compression | base equals incumbent's; constant ~4–5× dimension only | q_H table above |
| Any weighted-automaton engine below b^H, b < ~2.6 | impossible (Fliess floor) | q_7 = 181, q_8 = 462, ratios ≈ 2.6 |
| B1 as a scaling candidate | same base as incumbent on equal cuts (+2.5% states at H=9); climbing-ratio claim was a window-cut artifact | A-S4; my window counts stand only as B1's own resource curve |
| Subset-lattice transforms / subset convolution | 2^{HW} states | HW = 840 at frontier |
| GF(2) rank-based (base 2.0) for exact counts | unsound for counting | [BCKN15] |
| P-recursive / holonomic shortcut | already closed in repo | `results/triangle-structure.md` §3 |

## Citations

- [CP71] J. W. Carlyle, A. Paz, "Realizations by stochastic finite automata,"
  J. Comput. Syst. Sci. 5(1):26–40 (1971). doi:10.1016/S0022-0000(71)80005-3.
- [Fl74] M. Fliess, "Matrices de Hankel," J. Math. Pures Appl. 53:197–222
  (1974). (Minimal weighted-automaton dimension = Hankel rank.)
- [MS82] K. Mehlhorn, E. M. Schmidt, "Las Vegas is better than determinism in
  VLSI and distributed computing," STOC 1982, pp. 330–337.
  doi:10.1145/800070.802208. (Rank as a communication-complexity lower bound.)
- [BCKN15] Bodlaender, Cygan, Kratsch, Nederlof — arXiv:1211.1505 (as in
  `results/second-source-candidates-B.md`).
- [KN25] Kluk, Nederlof — arXiv:2512.23121 (pure-DP/tropical lower bounds;
  complements the linear-class floor here).
- [Nis91] N. Nisan, "Lower bounds for non-commutative computation," STOC 1991,
  pp. 410–418. doi:10.1145/103418.103462. (ABP width = Hankel rank; citation
  located by Teammate C's field sweep.)
- [FLOS21] N. Fijalkow, G. Lagarde, P. Ohlmann, O. Serre, "Lower bounds for
  arithmetic circuits via the Hankel matrix," comput. complexity 30:14 (2021).
  doi:10.1007/s00037-021-00214-1.
- [Lin69] B. Lindström, "Determinants on semilattices," Proc. Amer. Math.
  Soc. 20:207–208 (1969).
- [Wil68] H. S. Wilf, "Hadamard determinants, Möbius functions, and the
  chromatic number of a graph," Bull. Amer. Math. Soc. 74:960–964 (1968).
