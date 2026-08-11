# Scaling exploration — lane C (literature + cheapest decisive probes)

2026-08-11, per `docs/scaling-exploration-brief.md`. Three probes run, all
within budget (2 cores; the one job that could exceed 5 minutes ran in a
tmux window on session 0, log `results/scaling_s2_h8.log`). Scripts:
`scripts/scaling_probe_automatic.py`, `scripts/scaling_probe_ch_degree.py`,
`scripts/scaling_probe_minimal_dim.py` (plus the superseded
`scripts/scaling_probe_hankel_rank.py`, kept because its failure mode is
instructive and recorded below). Incumbent baselines: partition-frontier
states 1, 3, 8, 20, 50, 126, 322, 834 (H = 1..8, ~2.65×/height), strip wall
~6×/height (`results/strip-engine.md`).

Headline: **two clean negatives with numbers (S1, S2), and one qualified
negative with a genuinely new measured structure worth a follow-up (S3)** —
the exact bond dimension of the counting function is 3.6× smaller than the
partition state count at H = 7 and its measured growth base sits below the
incumbent's, but time cost squares it away and no cheap construction is
known.

---

## S1 — k-automaticity of a(n) mod 2 and mod 3: NEGATIVE

**Mechanism it would have bought**: if a(n) mod p were p-automatic, a term
mod p costs polylog(n) (read off base-p digits) — the brief's "different
universe." By Christol, p-automatic ⟺ Σ a(n)xⁿ algebraic over F_p(x).

**Probe** (`scaling_probe_automatic.py`, seconds, on the banked 40 terms):
sought any nontrivial P(x,y), deg_x ≤ Dx, deg_y ≤ Dy, with P(x, F) ≡ 0 mod
x⁴⁰ over F_p. Seven degree grids per prime, unknowns 24–36 against 41
equations (surplus 5–17; a spurious solution survives with probability
~p^−surplus):

- **mod 2: nullity 0 in every grid. mod 3: nullity 0 in every grid.**
- Kernel floor from the data: ≥ 9 provably distinct 2-kernel elements
  (mod 2), ≥ 8 (mod 3) — any automaton, if one existed, is not small.

**Verdict**: no algebraic relation within reach of the data; no automatic
structure detectable. Consistent context: BM mod p already found order ~n/2
(no C-finite structure, `results/unexplored-avenues.md`), and the ternary
spine (`results/ternary-spine.md`) makes the *in-regime diagonal family*
mod 3 3-automatic via W³ = W² + t — a(n) is a row sum crossing regimes and
provably-in-print inherits nothing. Growth rate: n/a (structural negative).
Crossover: never, within this data. Independence bar: n/a.

## S2 — per-height C_H(x) minimal-recurrence degree: NEGATIVE (same base, smaller constant)

**Mechanism**: each C_H(x) is rational; if its denominator degree q_H grew
at a base < 2.65, recurrence-based term generation could undercut the
frontier.

**Probe** (`scaling_probe_ch_degree.py`): independent column-DP recomputes
C_H mod 1,000,003 to depth N, validated against the banked triangle prefix
(n ≤ 40, exact match at every H run), then Berlekamp–Massey. Reproduces the
banked degrees 4, 9, 29, 68 (H = 3..6) and adds two new points:

| H | states | q_H | q ratio | q_H/states |
|---|---|---|---|---|
| 6 | 126 | 68 (banked, reproduced) | 2.34 | 0.54 |
| 7 | 322 | **181** (new; N = 420, 7.2 s) | **2.66** | 0.56 |
| 8 | 834 | **462** (new; N = 1000, 121.6 s, tmux) | **2.55** | 0.55 |

**Verdict**: the degree grows at the state-count's own base (~2.6/height;
the two new ratios straddle 2.65) with a flat constant ≈ 0.55 of the states.
The rational structure is a constant-factor compression, not a scaling
lever — and using it as a generator is circular anyway: fitting q_H needs
2q_H terms of C_H, which only the incumbent produces. Crossover: never
(same base). Independence bar: fails (the DP carries the partition rule).

## S3 — exact bond dimension of the transfer operator (Fliess/Hankel): qualified negative, new structure

**Mechanism**: by Carlyle–Paz/Fliess (realization theory: the Hankel rank of
a word function equals the minimal dimension of any weighted-automaton /
exact MPS realization — Carlyle & Paz, J. Comput. Syst. Sci. 5 (1971) 26–40;
Fliess, J. Math. Pures Appl. 53 (1974) 197–222), the height-H counting
function f(word of column masks) = x^{cells}·[connected] has a
realization-independent minimal dimension. If it grows slower than 2.65×,
an exactly compressed engine exists in principle.

**Method note, honest**: a first attempt (`scaling_probe_hankel_rank.py`)
sampled Hankel submatrices and provably under-measured. The kept probe
(`scaling_probe_minimal_dim.py`) computes the exact rank by forward/backward
Krylov closure of the partition realization under every letter matrix, at
random x in F_p (two specializations, agreeing; generic specialization
equals the ℚ(x) rank w.h.p.). En route it exposed and corrected a wrong
"floor": q_H does not lower-bound this rank (denominator degree obeys
q_H ≤ H·dim, and indeed dim < q_H from H = 4 on).

**Measured minimal dimensions** (exact, realization-independent):

| H | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
|---|---|---|---|---|---|---|---|
| dim | 2 | 2 | 5 | 7 | 18 | 36 | **89** |
| states+1 | 2 | 4 | 9 | 21 | 51 | 127 | 323 |
| compression | 1.0 | 2.0 | 1.8 | 3.0 | 2.8 | 3.5 | **3.6** |

Ratio band 2.00–2.57 with even/odd alternation; geometric mean over
H = 4→7 is **2.33×/height against the states' 2.5–2.56 over the same
window**. The sequence 2, 2, 5, 7, 18, 36, 89 is not in the OEIS
(searched 2026-08-11).

**Why it still loses as an engine** (the crossover arithmetic the brief
demands):

1. **Time**: the compressed realization is dense, so applying it costs
   dim²/column ≈ (2.33²) = 5.4×/height — against the strip's measured
   ~6×/height wall. Inside the alternation noise; no decisive base win.
2. **Construction**: the only route to the compressed basis measured here
   is reduction *of* the full partition realization — you must build the
   incumbent's state space first, so as a generator it can never undercut
   what it compresses.
3. **Memory**: the one real win — state storage scales at dim, factor 3.6
   and growing slowly. Meaningless until (2) is solved.

**Cross-validation against lane A (added 2026-08-11, team-lead's catch)**:
lane A independently measured the same quantity — the temporal Hankel rank
of the transfer operator — by its own reduction, getting 6, 17, 35, 88,
204, 501 for H = 4..9. Against this probe's 7, 18, 36, 89 (H = 4..7): **an
exact offset of +1 at every overlapping H**, and the origin is now VERIFIED
against this probe's code, not inferred: reseeding the reach closure from
the post-first-column vectors (A's convention — the Hankel without the
empty-prefix row) reproduces A's 6, 17, 35, 88 exactly at H = 4..7. The +1
is the empty-prefix/initial-vector dimension. Merged convention (agreed
with A and team-lead): quote the rank of f's Hankel proper — 6, 17, 35, 88,
204, 501 — with this probe's numbers noted as rank+1. Same object, two
implementations, two separate reductions, four exact agreements. Unlike the matching-identity convergence this is NOT
common-source — each lane measured, neither read the other's number. A's
two further points sharpen the growth: 204/88 = 2.32, 501/204 = 2.46, so
the combined band is ≈ 2.3–2.5 per height against the states' 2.5–2.65.
Any merged document should quote the rank WITH its convention stated
(with/without the empty-prefix row); the ±1 matters at small H.
**A's H = 10 point landed 2026-08-11: d_10 = 1217** (this probe's
convention 1218; both x = 1 and random x, exact closure,
`results/hankel_rank_h10.log`), quotient 5797/1217 = 4.76. With seven
points the base question's model fork (canonical file §4) LEANS geometric —
floor base ≈ 2.79, a real opening below the incumbent's asymptotic 3: the
even-step quotient ratios increase (1.081, 1.136, 1.165) where a power-law
quotient requires them to decrease, and the power fit misses d_10 by +5.2%
vs geometric's +1.9%. Lean, not verdict; the H = 11 discriminating point
(7.2 h per x-value) is with jasonp.

**Relation to banked work**: complementary to, not a re-tread of,
`results/boundary-push-tensornetwork.md` — that note SVD'd the kink frontier
*vector* across a *spatial* cut (χ ≈ √frontier, MPS 2–5× worse, verdict
negative); this probe minimizes the transfer *operator* over the temporal
word algebra. Both verdicts point the same way; this one adds that the
state-space itself carries ~3.6× exact redundancy the partition
canonicalization does not see.

**The open lead worth recording** (not priced, honestly speculative): what
IS the 89-dimensional invariant subspace at H = 7? A combinatorial basis
with a direct construction — the analogue of the non-crossing/Motzkin bases
of Potts TMs — would delete objection (2) and make this the best scaling
candidate on the table. One measured hint in that direction: **the
whole-column partition state counts satisfy states(H)+1 = Motzkin(H+1)
exactly for H = 1..7** (2, 4, 9, 21, 51, 127, 323) — measured on seven
points, NOT proved — apparently unrecorded in
the repo, and in tension worth resolving with `docs/engine-design.md`'s
note that the (cell-at-a-time) kink frontier admits "no Motzkin shortcut":
different frontier granularity, both can be true, but the whole-column
identity suggests planar/non-crossing structure survives at column
granularity. Independence bar: fails as constructed (reduction of the
partition realization); a direct combinatorial basis would need its own
assessment.

## S4 — the Motzkin identity: bijection found, identity now theorem-shaped

Second tranche (team-lead direction). Probe
`scripts/scaling_probe_motzkin.py`; H = 10 census ran in tmux
(`results/scaling_s4_h10.log`).

**Census**: states(H)+1 = Motzkin(H+1) now holds at **every height H = 1..10**
— H ≤ 7 from probe S3b, H = 8, 9, 10 recounted by this probe's own BFS
(834+1 = 835 = M₉; 2187+1 = 2188 = M₁₀; 5797+1 = 5798 = M₁₁), agreeing with
the strip engine's banked census (`results/strip-engine.md`) as a third
implementation.

**The bijection** (the structural claim, tested exhaustively): a reachable
whole-column state is exactly a pair (occupancy mask, **non-crossing**
partition of the mask's maximal runs). Verified by complete enumeration of
both sides at H = 2..7: reachable = NC-run-states at every height, zero
exceptions in either direction, and the run invariant (every maximal run
single-component) holds in all 533 reachable states checked. Counting then
closes it: the number of masks of length H with exactly r runs is
C(H+1, 2r), so

    #states + 1 = Σ_r C(H+1, 2r)·Catalan(r) = Motzkin(H+1),

the classical binomial–Catalan formula for Motzkin numbers.

**Proof status — final 2026-08-11: THEOREM, no asterisk** — the reachability
lemma is CLOSED by A's rails-and-spurs witness construction,
machine-verified over all 3,419 (fill, NC-partition) pairs at every H ≤ 9
(`scripts/probe_reachability_witness.py`); the Bell corollary for B1 is
likewise asterisk-free (B1's colour branching realizes any first-column
partition). **The theorem is banked standalone in
`results/king-column-motzkin.md`** — the citation target, carrying the full
proof, the three-implementation verification trail, the sharpened
cut-geometry scope (straight cuts provably crossing-free; jagged
cell-at-a-time cuts genuinely crossing — both repo notes true, each about
its own cut), the novelty trail, and the provenance split; the canonical
`results/scaling-exploration.md` §3 is the campaign-context summary. The
paragraph below is the earlier in-lane record, superseded on proof status:
(this lane observed the identity and the bijection; lane A supplied the
mechanism — provenance split, both belong in the record; A's
`results/scaling-exploration-A.md` §A-S6). (i) *Runs are single-component*
— immediate (vertical king adjacency). (ii) *No crossing partitions are
reachable* — PROVED (A): interleaved components need crossing king paths,
crossing king paths share a 2×2 window, and a 2×2 window is a K₄, so they
merge. (iii) The Motzkin step is classical: Σ_k C(H+1,2k)·Catalan(k) =
Motzkin(H+1) (Aigner, "Motzkin numbers," European J. Combin. 19 (1998)
663–675, DOI 10.1006/eujc.1998.0235; OEIS A001006), the −1 being the empty
fill. (iv) The one OPEN lemma: reachability of every non-crossing pattern —
BFS-verified exhaustively at every H ≤ 9 (A), two-sided at H ≤ 7 (this
probe); the constructive nesting argument is routine and unwritten. **The
same skeleton yields B1's column states in closed form: Σ_k
C(H+1,2k)·Bell(k)**, exact at every measured point (A) — so the price of
B1's rule-independence is exactly Bell-over-Catalan on the runs (×1.047 at
H = 10, ×1.243 at H = 14, ×2.349 at H = 21). Scope guard, unmissable:
**whole-column state space only.** The cell-at-a-time kink frontier
genuinely needs crossing partitions (`docs/engine-design.md`), and
`docs/glossary.md` already records the qualitative "Motzkin-like ≈ 3^W" for
Jensen-style signatures — the exact identity, the bijection, and the two
closed forms are the new content.

**The scaling consequence, and a correction that reaches outside this
campaign**: Motzkin's asymptotic ratio is 3, so the incumbent whole-column
state base is **exactly 3, not 2.65** — the banked "~2.65×/height" is the
local ratio near H ≈ 10 (×2.75 at H = 14, ×2.81 at H = 21, from the closed
form). Every "2.65" comparison earlier in this file (S2, S3, the header
baseline) is a like-for-like LOCAL ratio at matching heights and stands as
such; no crossover conclusion changes. Every measured base in this family
is pre-asymptotic and climbing: B1's window-cut 2.72→2.90 (window cut —
see the canonical file's cut-confusion warning), and the Hankel floor's
2.32→2.46. The honest scoreboard: incumbent base = 3 (proved modulo the
reachability lemma), floor base ≤ 3 and unknown (measured window 2.3–2.5,
climbing), so the incumbent-vs-floor gap at small H may be a vanishing
pre-asymptotic artifact rather than a real opening. **Finding for jasonp,
files deliberately NOT edited**: `results/strip-engine.md` (and anything
else quoting "~2.65×/height" as the state growth) is quoting a local ratio;
the exact closed form Motzkin(H+1) − 1 with asymptotic base 3 is now
available and is the number a referee should see.

## S5 — field sweep: CSP counting, algebraic complexity, non-integer-q Potts

Carried question: does anything here compute T(n,H) WITHOUT a per-column
summary? Verdicts:

- **Algebraic complexity: the floor is classical, and it is the sweep's one
  find.** Nisan's theorem (N. Nisan, "Lower bounds for non-commutative
  computation," STOC 1991, 410–418, DOI 10.1145/103418.103462; modern form:
  Fijalkow, Lagarde, Ohlmann & Serre, "Lower bounds for arithmetic circuits
  via the Hankel matrix," comput. complexity 30 (2021), DOI
  10.1007/s00037-021-00214-1) characterizes the width of a noncommutative
  algebraic branching program EXACTLY as the Hankel-matrix ranks. A
  column-sweeping engine maintaining any finite linear summary is an ABP
  over the column alphabet — so the C/A measured Hankel rank is an
  **unconditional lower bound on every method of that class**, not a fitted
  estimate. With S4, the class is boxed: floor (measured, base ≤ 3) ≤
  incumbent (= Motzkin, base exactly 3), within a factor ~3.6 at H = 7.
  Anything that sweeps columns is now priced by this pair of numbers; no
  further candidates from that class need individual probing.
- **CSP counting dichotomies**: classification results (poly vs #P-hard),
  not algorithms; the parameterized/fine-grained end says DP is
  conditionally optimal (SETH-tight counting bounds via matrix rank — e.g.
  Cygan, Kratsch & Nederlof for Hamiltonian cycles, arXiv:1709.02311; pure-DP
  unconditional bounds, Kluk & Nederlof arXiv:2512.23121, already cited in
  lane B). Supplies floor evidence, no method. Dead as a source of a
  candidate.
- **Non-integer-q Potts numerics**: transfer matrices in the FK basis are
  the partition realization again; the numeric end (CTM/tensor-RG at real q)
  approximates free energies and cannot produce exact integers — the repo's
  CTM read-negative stands (`results/strip-growth-lambda-bounds.md`, K6 of
  the second-source campaign). The exact-extraction member of this family is
  B1, already ranked. Dead as a new direction.

## Fields swept and not swept

Two targeted searches this session found no prior art for either the
Hankel-minimization angle on lattice-animal transfer matrices (the WFA
literature — spectral learning, canonical forms — never touches lattice
enumeration) or sub-transfer-matrix counting of *connected* patterns in
symbolic dynamics / CA (pattern-complexity counts words, not connectivity;
ancestor-counting results are #P-hardness, the wrong direction). The three
fields deferred in the first tranche — CSP counting dichotomies, algebraic
complexity, non-integer-q Potts numerics — are now swept in S5: one find
(Nisan's theorem, making the Hankel floor unconditional for the
column-summary class), two dead ends.

## Summary table

| probe | candidate | growth measured | crossover vs incumbent | verdict |
|---|---|---|---|---|
| S1 | a(n) mod 2/3 automatic → polylog terms | no algebraic relation, 7 grids × 2 primes, surplus 5–17 | never (in-data) | dead |
| S2 | rational-structure generator per height | q_H: 181 (H=7), 462 (H=8); base ≈ 2.6 = incumbent's | never (same base) | dead |
| S3 | exact compressed transfer operator | dim: 89 at H=7 (=A's 88 + convention); combined band 2.3–2.5, climbing | time: none (5.4 vs 6); memory: 3.6× level | dead as engine; floor now unconditional via S5/Nisan |
| S4 | Motzkin identity states+1 = M(H+1) | holds at ALL H = 1..10; bijection exhaustive H ≤ 7 (C) / H ≤ 9 (A) | n/a — structural | PROVED modulo reachability lemma (C observed, A mechanized); incumbent base exactly 3; B1 = Bell-over-Catalan |
| S5 | field sweep (CSP, alg. complexity, Potts q∉ℤ) | Nisan STOC'91: ABP width = Hankel rank, unconditional | n/a | floor formalized; both other fields dead as candidate sources |
