# L6 wildcard — triaged survey, kill counts, and the costed survivors

2026-08-12. Lane L6 of `docs/triangle-round3-brief.md`, scored under
`docs/skeptical-reader-standard.md`. Blind list filed first at
`results/triangle-r3-blind-l6.md` (timestamped 18:22:30 EDT, before any
paper, any `papers/` listing, or any web query; unrevised). Probe:
`experiments/tristruct/r3_l6_residue_dp.py` (+ `.log`), laptop, exact
integer arithmetic, 4m11s total.

**First line, per the brief: the top survivor clears entry-ticket level 1
and level 2.** And the lane's headline process finding, stated before the
survivors: **the strongest wildcard in the literature is already
project-held.** The color-coincidence cancellation DP — connectivity never
decided, read off as the [q¹] coefficient of Σ_S q^(c(S)) — was found,
probed, built and measured on the `second-source` branch on 2026-08-11 as
candidate B1 (`git show second-source:results/second-source-candidates-B.md`),
with kills already banked there for cut-and-count proper, rank-based
counting, ZDD/frontier search, #SAT counters, Potts integer-q interpolation,
Tutte/reliability specializations, FLM, and corner transfer matrices. My
blind list, written without knowledge of that file, converged on the same
family (items 6, 10, 28, 29). What survives as L6's own contribution is the
part the branch priced dead and the literature prices alive: **the residue /
CRT ladder on that DP**, which moves its ceiling from H = 17 (exact,
u128 payload) to H = 20 in RAM and puts H = 21 within phase-2 reach — full
band coverage at 8·k bits per cell, exact values as the stretch via CRT
stacking.

---

## Disclosure block (mapped to phase 1 per the brief)

    claim:            residues of T(40,H), H = 15..20 (H = 21 phase-2), to one or
                      more 8-bit prime moduli (CRT-stackable toward exact), by a
                      counting rule with no connectivity decision anywhere
    share of a(40) reached:            48.00% (bands: H = 15..20; provenance:
                                       'real-sweep' per harness Part 2 loader
                                       quotes; 50.84% if H = 21 lands at phase 2)
    bits against enumeration error:    0 today; projected at phase 2: 8k bits/cell
                                       for k independent prime runs, modulus stated
                                       per run
    bits against formula-chain error:  n/a — targets swept cells only; conditional
                                       on nothing
    rule independence:                 levels 1 AND 2 (argument below)
    derivation independence:           DP consumes only the lattice definition;
                                       banked cells touched only as post-hoc
                                       comparison targets
    input footprint:                   0 banked cells consumed; comparison set =
                                       the 6-7 band cells, max n = 40
    checker:                           phase-2 artifact = the residue DP with its
                                       two structural self-checks ([q^0] = 0
                                       identically; q = 1 full-polynomial binomial
                                       identity), plus a reader-side residue
                                       comparison against the banked file
                                       (minutes, laptop)
    sensitivity:                       deferred to phase 2, marked so; probe-scale
                                       RED control shown (corrupted fresh-class
                                       weight is caught by the [q^0] = 0 check —
                                       r3_l6_residue_dp.log)
    prior-work grep:                   commands in "Novelty greps" below,
                                       including cross-branch; verdict: family
                                       HELD on second-source branch, residue
                                       variant not priced there

---

## Blind list and filter, in brief

35 candidates filed blind, spanning parameterized algorithms, algebraic
cancellation, statistical mechanics, tensor contraction, knowledge
compilation, external series, bijective and topological methods
(`results/triangle-r3-blind-l6.md`). Filter fixed before reading, applied
first-fail in order:

| filter | question | kills |
|---|---|---|
| F1 | exact counts or stated-modulus residues **of T(n,H)** | **12** (bounds, MC, approximants, CTMRG, quantum, TDA, wrong-object polynomials with no site specialization, determinant-sum routes with no known formulation for induced connected subsets) |
| F2 | costed route to n = 40, H = 15..21 | **10** (Redelmeier-class at n = 40, 2^840 subset convolution, #SAT counters [BCMS16 floor], cluster inversion [gas-shaped, L2 closed], external series, verified small-n counters, heaps/bijective, dancing links) |
| F3 | connectivity decided off a labeled cell frontier | **5** (Jensen link patterns, FLM's in-rectangle counter, ZDD mate arrays, pathwidth DP, diagonal-direction TM with labels) |
| F4 | not already project-held or project-closed | **7** (cut-and-count proper, rank-based, spin-basis Potts = B1 itself, Euler-characteristic DP [`cpp/tma/euler.h` per branch `results/holes.md`], Temperley/solvable subclasses, FK reformulation, color-symmetrization engineering = B1) |
| — | **survivors** | **1** (blind item 29: residue ladder on the cancellation DP) |

12 + 10 + 5 + 7 + 1 = 35. The single survivor is costed below in two
implementations (partition basis; raw spin basis), which differ in state
space, modulus, and which band cells they reach — they are the "top two"
the brief asks for. Papers opened in full: 2 of the cap of 6 (CNP+11,
KN25); everything else killed by filter, by project citation, or by
search-level triage (searches listed at the end).

Blind-list scoring note for the completeness adversary: my prior expectation
recorded in the blind file — "the live find is the cancellation family
{6, 10, 28, 29}" — was correct, and items 6/10/28 turned out to be held on a
branch one day old. The blind file is unrevised; nothing was appended.

---

## Why the family was pruned to one survivor: the second-source holdings

`git show second-source:results/second-source-candidates-B.md` (B1): the
ℤ[q]/(q²) color-coincidence DP, **built** (`cpp/cutcount_b1.cpp`, branch),
**validated on all 400 banked cells at H ≤ 10, n ≤ 40, in 4.0 s**, window
census measured to H = 14 (891,074 states, 34.2 s/column, ~2.9×/height),
with a ceiling analysis for **exact-count payloads**: H = 16 with the
running I256 binary, H = 17 with a u128 redesign (~72 GB), "H ≥ 18 stays
dead (~210 GB)". Its kill list already covers most of my blind list's
algorithmic half; its lane-A twin killed the Potts/FK formulations
(K1-K3) and CTM (K6). Re-proposing any of that scores zero and I do not.

The branch's ceiling is a statement about 40-byte-per-slot exact payloads.
It is not a statement about residues, and no file on any branch prices the
residue variant — that is the gap this lane files.

---

## Survivor 1 — the residue / CRT ladder on the cancellation DP (partition basis)

**Entry ticket, first: levels 1 and 2.** Where is king-connectedness
decided? Nowhere. The DP computes A_n(q) = Σ_S q^(c(S)) as the number of
pairs (S, f: S → [q]) with f equal on king-adjacent pairs — a purely local
constraint — in the ring ℤ[q]/(q²) with coefficients mod m; the connected
count is the coefficient C₁ = [q¹] A_n(q), extracted once at the end. There
is no union-find, no component label in the connectivity sense (the state
partition is *color coincidence*, and a class may span disconnected cells —
my probe exercises exactly that branch), no stranded-component death, no
completion predicate. Level 2: the failure modes are the fresh-class weight
(q − b), the ring truncation, and canonicalization — errors that corrupt the
whole graded family jointly and are caught by two identities no connectivity
code touches ([q⁰] ≡ 0; A_n(1) = binomial). None of the harness Part-3
shared propositions (stencil completeness, label-partition sufficiency,
completion predicate) is assumed; the DP counts disconnected subsets too and
cancels them algebraically. Failure-mode disjointness from
union-find-over-a-frontier is as clean as this problem allows. (Independence
argument inherited from lane B's B1 entry, verified against my own
re-derivation; shared residue: the king-adjacency *definition* itself, which
every method on this problem shares.)

**My measurement** (`r3_l6_residue_dp.py`, gympie, 2026-08-12): an
independently re-derived implementation — written from the identity, not
from the branch's probe; the re-derivation caught and fixed the
isolated-cell-joins-live-class branch, which is itself a small definition-
level cross-check of the branch's description. Results:

- Exact match of [q¹] against my own brute-force BFS enumeration at
  (H,W) = (2,4), (3,3), (3,4), (4,3), every n. RED control: corrupting the
  fresh-class weight trips the [q⁰] = 0 structural check.
- (window, area)-state census at W = 8: H = 8: 100,655; H = 11: 2,757,851;
  growth **×2.98–3.04 per height** — corroborating the branch's ×2.9 window
  growth with an independent implementation.
- Python wall 51.6 s/col at H = 11 — consistency scale only; the wall model
  below is anchored on the branch's measured C++ throughput.

**Cost model** (anchor: branch-measured 34.2 s/col at H = 14 over
891k windows × 41 area slots ⇒ 0.94 µs per slot-column; windows
extrapolated at the twice-measured ×2.9/height; W ≤ n − H + 1 columns;
payload = 41 slots × bytes(m) × 2 buffers + ~22 B key per state):

| H | windows (proj.) | RAM, mod 8-bit prime | RAM, mod 61-bit prime | wall/height (1 thread) |
|---|---|---|---|---|
| 15 | 2.6 M | 0.3 GB | 1.8 GB | ~0.7 h |
| 16 | 7.5 M | 0.8 GB | 5 GB | ~2 h |
| 17 | 21.7 M | 2.3 GB | 15 GB | ~6 h |
| 18 | 63 M | 6.5 GB | 43 GB | ~16 h |
| 19 | 183 M | 19 GB | 124 GB | ~43 h |
| 20 | 530 M | 55 GB | 360 GB | ~5 days |
| 21 | 1.54 G | 160 GB | 1.0 TB | ~14 days |

Height-exactness is recovered by the strip engine's second-difference
accounting (an already-two-sourced layer disjoint from connectivity), so
band coverage needs the box runs at H − 2 as well — cheap rows.

**Levels cleared, reach, verdict.** 63-bit residues to H = 18; 8-bit-prime
residues to H = 20 within ayr's 78 GB (H = 20 fits, days-scale wall,
state-sharded parallelism is this project's stock in trade); H = 21 needs
~160 GB → dalby RAM or the project's out-of-core machinery — phase-2
question, not priced dead. **CRT stacking:** k independent 8-bit-prime runs
give 8k bits per cell at linear wall and flat RAM; 13 runs exceed
log₂ T(40,15) ≈ 103 bits — **exact values at H ≤ 20 are a wall-time
purchase, not a new idea**. That is the brief's "residues are the probable
ceiling, exact values the stretch," with the stretch priced. Against
enumeration error these are full bits per the standard (different rule
class); across the k runs the moduli are independent but the rule is one
rule — bits sum against the *production engines'* rule, not against B1's
own, and the deliverable must say so at phase 2.

## Survivor 2 — raw spin basis at q = 2, mod 2, for the cells the ladder may miss

**Entry ticket: levels 1 and 2**, same identity, different basis: no color
symmetrization at all. State = per-frontier-cell {empty, color A, color B},
3^(cut) states, weight bookkeeping trivial mod 2; C₁ mod 2 = Z(2)/2 mod 2.
No partitions of any kind in the state — the strongest possible distance
from the frontier-label rule, at the price of exponential states in the cut.
At n = 40, H = 21 the width obeys W ≤ 20, so the short cut has 20 cells:
3^20 = 3.5 G states × 41 areas, bitpacked mod 2 ≈ 18 GB/buffer, ~10^13–10^14
bit-ops ≈ fleet-days; H = 20 (W ≤ 21, cut 20 after orientation) similar.
Verdict: **1 bit per cell at H = 20..21** by a zero-subtlety kernel if the
partition-basis ladder stalls there — a backstop, not a first choice, and
its 1 bit duplicates a modulus already two-sourced (`percell-mod4.md`), one
source of which (symcount_fast) is itself label-free. Ranked accordingly:
real but marginal.

## Filed as not fitting the ticket

**External definition anchors from the physics literature.** Mertens 1990
(`papers/mertens_1990_lattice_animals.pdf`) publishes nnSquare (= king)
perimeter polynomials and totals to s = 14/22 computed by other people's
code — the branch already banked the crosscheck
(`second-source:results/mertens-1990-perimeter-crosscheck.md`). My search
for anything newer on the king lattice found only Monte-Carlo threshold work
(Majewski–Malarz-line extended-neighborhood percolation), no exact series
extension. This is definition-level semantic independence — the strongest
kind — at n ≤ ~22, and it cannot be pushed to row 40 by anyone. The ticket's
vocabulary (reach the band) does not fit it; filed per the brief as a
finding about the ticket: **the literature's only fully external evidence
class stops 18 rows short of the mission, permanently.**

## The obstruction paragraph (supports the round's outcome 2 if phase 2 is declined)

Verified citations, both read this session: Cygan–Nederlof–Pilipczuk–
Pilipczuk–van Rooij–Wojtaszczyk, "Solving connectivity problems
parameterized by treewidth in single exponential time," FOCS 2011,
arXiv:1103.0534 — Cut&Count is Monte-Carlo *decision*, not counting; its
exact deterministic descendant is precisely the cut-space algebra B1
implements (BCKN, Inform. & Comput. 243 (2015), arXiv:1211.1505, cited via
the branch file). Kluk–Nederlof, arXiv:2512.23121 — unconditional
2^Ω(k log log k) tropical-circuit lower bound for TSP at pathwidth k: *pure*
DP cannot beat partition-type state; the known escapes are algebraic. Bova–
Capelli–Mengel–Slivovsky (IJCAI 2016, via branch cite) puts the same floor
under any compilation-based counter. The branch's pathwidth probe measured
the kink frontier already at the graph's exact pathwidth. Assembled: every
route class the literature offers either pays frontier-behavior state
(pure DP, ZDD, #SAT, contour, any contraction across a cut — the measured
rank 21→51→127→298 is its floor) or is the algebraic cancellation family —
which the project now holds, and whose own state space is the measured
×2.9/height Bell-partition curve. **There is no third class in the
literature as of this search.** If phase 2 is declined, the closing
statement can cite this paragraph: the connectivity rule can be varied
within reach — B1's family is the variation — and everything else is proved
or measured to pay the same wall it escapes.

## The three standard questions, top two survivors

**Does it reach H = 15..21 at n = 40?** Survivor 1: H = 15..20 yes
(8-bit residues, RAM-feasible today; exact via 13-run CRT as a wall-time
purchase); H = 21 phase-2 (160 GB or out-of-core). Survivor 2: H = 20..21
yes, mod 2 only.

**At what cost, anchored how?** Survivor 1: table above; anchored on my own
probe (correctness, census, ×2.98–3.04 growth — measured 2026-08-12,
gympie) and the branch's measured C++ throughput (0.94 µs/slot-col at
H = 14) and window census, whose 40-B ceiling numbers my per-state model
reproduces at H = 17 (72 GB) and H = 18 (207 GB) before the payload change.
Survivor 2: state count is exact arithmetic (3^20), throughput a bitwise-DP
estimate — the weakest number in this file, marked as such.

**Which ticket levels?** Both clear 1 and 2. Neither carries component
labels across a cut; survivor 1's partition state is color-coincidence (may
span disconnected cells — probe-exercised), survivor 2's state carries no
partitions at all.

## Novelty greps (commands run)

    git log --all --oneline --name-only -- 'results/*.md' 'docs/*.md' 'docs/**/*.md'
    git grep -in -E 'cut.?and.?count|fortuin|kasteleyn|potts|chromatic|spin basis|euler characteristic' -- 'results/*.md' 'docs/*.md' 'docs/**/*.md' papers/...
    for b in $(git branch --format='%(refname:short)'); do git grep -il -E 'cut.?and.?count|fortuin|kasteleyn|potts|spin.basis|cygan|nederlof|euler.characteristic' $b -- 'results/*.md' 'docs/*.md' 'docs/**/*.md'; done
    git show second-source:results/second-source-candidates-B.md   # + -A, team brief, critique

Verdict already stated: family held on `second-source` (B1 + kill lists);
residue/CRT-ladder pricing appears nowhere on any branch — that pricing is
this file's claim to novelty, and it is a *variant pricing*, not a new
method; the adversary should score it against the seed list exactly so.

Web triage (search-level, no full read): counting-induced-subgraphs
modular-hardness line (Dörfler et al. / Roth-line, #W[1]-hardness even mod
p); extended-neighborhood site-percolation series (MC thresholds only, no
exact king series past Mertens 1990); post-2015 enumeration-method sweep
(Redelmeier/TM refinements only — Shirakawa n = 59 already in `papers/`;
one Nov-2025 convolutional *bounds* preprint, arXiv:2511.00461, F1-killed).

## Queue rows filed (per the mid-round amendment)

Eight rows appended to `results/triangle-r3-queue.md` as L6-1..L6-8: the two
survivors (L6-1, L6-2); successors different in kind from the closures —
joint q^c·x^χ hole-stratified grading (L6-3, from the Euler-DP kill),
mod-3^k ladder against the ternary-spine theorems (L6-4), third-party-code
external series extension (L6-5, from the external-series F2 kill),
one-cell certified-checker cert merged toward L5/B2 (L6-6, from the
compilation-floor kills); the cap-spillover reading list (L6-7); and the
terminal-family triage test distilled from the obstruction paragraph (L6-8).

## NOT ESTABLISHED

- dalby's RAM (whether 160 GB at H = 21 mod-8-bit is in-RAM there): not
  checked from here; phase-2 fact.
- Survivor 2's throughput (bit-DP ops/s): estimated, not measured.
- Whether the branch's B1 calibration run (H = 15/16, live on dalby
  2026-08-11 per its file) completed, and its walls — those would replace
  my extrapolation's first two rows with measurements; I did not go looking
  for the run's artifacts.
- KN25's theorem is stated for TSP round tours at pathwidth k; its
  application to counting connected induced subgraphs is by the paper's own
  "algebraic methods are necessary" framing, not a verbatim theorem about
  this problem — the obstruction paragraph leans on it only that far.
- Mod-2^j ladders via integer-q evaluations (Z(2^j)/2^j ≡ C₁ mod 2^j) were
  considered and set aside: (2^j+1)^cut spin states are dead past j = 1, and
  the partition basis already gives any byte modulus directly; recorded so
  nobody re-derives it as new.
