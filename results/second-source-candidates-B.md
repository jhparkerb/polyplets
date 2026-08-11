# Second-source candidates — Teammate B (model counting / parameterised algorithms)

Date: 2026-08-11. Lane: #SAT and weighted model counting, treewidth/pathwidth
DP, cut-and-count, rank-based methods, ZDD enumeration, per
`docs/second-source-team-brief.md`. Probes P0–P2 below; probe code (throwaway,
uncommitted): `experiments/probe_king_pathwidth.cpp`,
`experiments/probe_cutcount_dp.py`, binary `build/probe_king_pathwidth`.

The lane-wide tension the brief names is real and it is the organizing fact:
almost everything in this literature, when instantiated on a king strip,
becomes a frontier DP carrying a connectivity partition — the incumbent's rule
in another costume. Kluk–Nederlof [KN25] gives this teeth as a theorem: *pure*
DP (tropical-circuit) formulations of connectivity problems on bounded
pathwidth cannot avoid super-single-exponential state blowup; the known escapes
are algebraic (rank/determinant/cut algebra). So the one axis in this lane that
is genuinely different from union-find-over-a-frontier is the algebraic one,
and both surviving candidates live on it.

---

## Ranked candidates

### B1 — Colour-symmetrized spin TM with clash-zeroing: connectivity as a coefficient, never a decision  **[top pick]**

*(Naming corrected per Teammate A's review 2026-08-11: mechanically this is
NOT the FK/random-cluster TM — the FK TM joins partitions on adjacency, which
is union-find again; this DP never joins on a clash, it ZEROES. Salas–Sokal
and BCKN remain the lineage, not the mechanism.)*

**Mechanism.** For the height-H strip let A_n(q) = Σ_S q^{c(S)} over n-cell
subsets S, c = number of king-connected components. Then the connected count
is the *linear coefficient*: T-type counts = [q¹] A_n(q). A_n(q) equals the
number of pairs (S, coloring of S constant on components), and *that* is
computed by a frontier DP whose state is the **color-coincidence partition** of
the last H+1 cells — with no connectivity decision anywhere: no union-find
verdict, no stranded-component death. A cell adjacent to two distinct-color
blocks gets weight 0; a free cell chooses an existing color (weight 1 each) or
a fresh one (weight q−b, b = live blocks). Connectivity emerges at the end by
reading a coefficient of a polynomial identity, computed exactly in the ring
ℤ[q]/(q²). This is the counting face of cut-and-count [CNP+11] made
deterministic and exact the way [BCKN15] does (linear algebra over the cut
space); it descends from the Potts/colouring transfer-matrix tradition of
Salas–Sokal [SS01] but is the spin-side (colour-state) form, colour-
symmetrized, not the FK partition-join form — Teammate A's lane arrived at
the same family from the opposite direction; merged, not counted twice.

**Probe P2 (validated + measured, 2026-08-11, gympie).**
`experiments/probe_cutcount_dp.py`:

- Correctness: exact match of [q¹] A_n(q) against brute-force enumeration of
  all subsets at (H,W) = (2,3), (3,3), (3,4), (2,6), (4,3) — every n, OK.
  Structural self-check [q⁰] A_n = 0 (n ≥ 1) holds throughout.
- State space (max reachable frontier states, cell-at-a-time window H+1):

  | H | states | | H | states |
  |---|--------|---|---|--------|
  | 4 | 45     | | 9 | 5,041  |
  | 5 | 111    | | 10 | 13,733 |
  | 6 | 279    | | 11 | 38,065 |
  | 7 | 718    | | 12 | 107,241 |
  | 8 | 1,884  | | | |

  C++ census (build/cutcount_b1 --states, 2026-08-11, bit-for-bit equal to the
  Python probe at every overlapping H) extends this: **H = 13: 306,858;
  H = 14: 891,074** boundary states, 20.8M transitions/column at H = 14.
  These are mid-column WINDOW states — the correct resource curve for this
  implementation (they price its RAM/wall), but not cut-consistent with the
  strip's column-state counts: on equal column cuts B1 carries all set
  partitions of the occupied runs vs the incumbent's non-crossing ones,
  measured +2.5% at H = 9 (2242 vs 2187), identical below H = 7
  (`results/scaling-exploration-A.md` §A-S4). The "2.4× the incumbent" and
  climbing-ratio readings earlier drafts took from the window numbers were
  cut artifacts; the true cross-engine state overhead is percent-level in the
  project's range.

**Region and n — now measured, not planned** (C++ engine `cpp/cutcount_b1.cpp`
built after jasonp approved the calibration; coefficients are 4×u64 wrapping
mod 2^256, exact for finals < 2^216). Validated: **T(n,H) matches the banked
triangle on all 400 banked cells at H ≤ 10, n ≤ 40, in 4.0 s single-threaded
on gympie** (84/84 at H ≤ 6 first; strip engine comparison: its C₁₀ alone is
3.5 s, its C₁₄ was 8.6 h on dalby). Per-height cost tracks the state count
(~2.9×/height), not 2^H. Payload at H = 14: ~9e5 states × 41 areas × 3
coefficients × 32 B ≈ 3.5 GB plus transition double-buffering — call it
~7 GB, dwarfed by the strip's 38 GB at C₁₄ but not the "0.5 GB" an
area-blind read of the state table suggests (Teammate A's correction, folded).
Two structural self-checks are logged per height by the run itself:
[q⁰] C_H(n) = 0 for all n ≥ 1, and the full polynomial evaluated at q = 1
reproducing C(HW,n) − C(H(W−1),n) exactly (all-subsets binomial — exercises
every transition weight with no connectivity anywhere). Calibration run
covering H ≤ 15 then H = 16 at n ≤ 40 is live on dalby
(scripts/run_cutcount_b1_calib.sh, results/cutcount_b1/); H = 15/16 clean
would make kink-only Grand anchors T(28,15), T(29,15), T(30,16), T(31,16)
two-source. **Ceiling, re-derived 2026-08-11 after the cut-consistency
review:** the engine's working set is genuinely the mid-column window (the
hash table holds the H+1-cell window at every cell step), so the measured
window census — not the column-cut count — prices RAM, and for the *current
binary* (I256 coefficients ×3) H = 17 needs ~170 GB: dead on dalby. But the
I256 width is over-provisioned: finals obey the same bound the strip
documents (C_H(n) ≤ H·a(n) < 1.7e38 < 2^127), so (c0, c1) can be wrapping
u128 with the binomial self-check coefficient carried mod a 63-bit prime —
40 B/area-slot instead of 96 B — putting H = 17 at ~72 GB peak:
**alive with that design change**, wall ~10 h-class extrapolated from the
measured 34.2 s/column at H = 14 (to be firmed against the H = 15/16 walls
before committing). H = 18 stays dead (~210 GB). Ceiling: H = 16 with the
running binary (4 kink-only anchors flip), H = 17 with the u128 redesign
(6 of 11), H ≥ 18 closed — T(34,18)…T(38,20) stay kink-only.

**Structural price of independence** (Teammate A, §A-S4 of
`results/scaling-exploration-A.md`): on equal column cuts, B1's states are
exactly ALL set partitions of the occupied runs where the incumbent carries
the non-crossing ones — identical below H = 7 (a crossing needs ≥ 4 runs;
the first surplus at H = 7 is Bell(4) − 14 = +1 over the single 4-run fill).
A-S6 gives both spaces in closed form, verified at every measured point:
incumbent = Σ_k C(H+1,2k)·Catalan(k) = Motzkin(H+1) − 1, B1 =
Σ_k C(H+1,2k)·Bell(k). Exact overhead: ×1.047 at H = 10, ×1.243 at H = 14,
×1.551 at H = 17, ×2.349 at H = 21 — percent-level near H = 10, a genuine
but bounded factor at the frontier. The price of deciding nothing about
connectivity is *structural* and exactly priced — and the same ~2.4×/height
Hankel floor (A-S1) binds both engines, each sitting ~4.4× above it near
H = 9.

**Independence argument (the connectivity-rule axis).** The incumbent and the
strip engine share one rule: union-find over frontier labels with
stranded-component death — a per-state, per-event *decision* about
connectedness. B1 makes no such decision at any point: every subset,
connected or not, flows through the DP; the connectivity information is
carried globally by the q-grading and extracted once, at the end, as a
coefficient. **Named failure mode:** an error in the falling-factorial /
fresh-color weight (the q−b line), in the ℤ[q]/(q²) truncation, or in block
canonicalization. These corrupt the *entire* graded family {N_{n,j}}_j
jointly, not one frontier event — and the family is over-determined: [q⁰] = 0
identically (checked), the full-polynomial small-H runs must satisfy
A_n(1) = C(HW, n) exactly (a binomial identity no connectivity code touches),
and N_{n,2}, N_{n,3}, … are new numbers the incumbent never computes, cross-
checkable at small n by brute force. A stranded-death misconception cannot
pass through B1 because B1 contains no death rule to be wrong in the same
way. **What stays shared, honestly:** the king-adjacency definition itself
(any method on this problem shares it; only `build/g2`-style brute force at
small n checks the definition), and the translation-fixing / second-difference
accounting layer if T(n,H) is assembled the strip engine's way — that layer is
disjoint from the connectivity rule and is already two-sourced.

**Binding resource.** RAM for per-state payload (states × 41 areas × 3
coefficients × 32 B, double-buffered): ~7 GB at H = 14, ~27 GB at H = 15,
~80 GB at H = 16, > 125 GB at H = 17 — RAM kills it at H = 17 on current
hardware. Measured walls: C++ H ≤ 10 full = 4.0 s gympie; dalby ~4.4× slower
per thread (C₉: 3.1 s vs 0.7 s, this engine, measured).

### B2 — Certified knowledge compilation (d-DNNF + CPOG): the tier-3 mechanism nobody had proposed

**Mechanism.** Write the *definition* — cell variables of an H×W window, a
CNF connectivity encoding, cardinality |S| = n — and let an untrusted compiler
(D4 lineage) produce a dec-DNNF, plus a **CPOG certificate** that a **formally
verified checker written in Lean 4** [BNAH23] validates against the CNF and
then counts from. The trusted base is: the short definitional CNF generator +
the verified checker. The engine that does the exponential work is entirely
untrusted. This is the shape of the brief's outcome 2 — an exact-arithmetic
certificate for a cell that a short independent checker verifies — and this
repo already lives in Lean, so the verified-checker half is native
infrastructure, not exotica.

**Independence argument.** Strongest available on the stated axis: no
connectivity *rule* is trusted at all. If the compiler's internal reasoning
(which will, per [BCMS16], necessarily be at least frontier-partition-sized —
see kill list) harbored the same misconception as union-find-with-death, the
certificate would fail to check against the definitional CNF. **Named failure
mode:** a wrong CNF encoding of connectivity (e.g., an aux-variable scheme
that double-counts models or misses a reachability case). That failure lives
in ~a page of generator code reviewable by eye and testable against `build/g2`
at n ≤ 19 — and it is manifestly disjoint from frontier union-find, which the
trusted base does not contain.

**Region and n.** Small cells only. By [BCMS16], dec-DNNF size for a
connectivity constraint across a width-H cut is bounded below by the number of
distinct frontier behaviors, so certificates are DP-trace-sized: the method
buys *certainty*, not reach. One certified mid-triangle cell — ideally a cell
in the strip-confirmed region (upgrade to tier 3) or, at the outside, a small
kink-only anchor — is the prize. **Binding resource:** certificate size on
disk and checker wall; both grow with the compiled trace.

**Status: cannot be killed cheaply — measurement plan** (per brief): needs
D4 + cpog toolchain built from source into `build/` (third-party code:
jasonp's call, flagged below), then compile T(n,H) encodings at increasing n
on a small H and record cert size + check time until it falls over. No
counter/compiler exists on the fleet today (probe P1: `ganak`, `sharpSAT`,
`sharpSAT-td`, `d4`, `dsharp`, `c2d`, `cachet`, `approxmc`, `minisat`,
`cryptominisat` — all absent on gympie).

---

## The pathwidth question (assigned open question)

**Answer: pw(P_m ⊠ P_n) = m + 1 for all probed sizes (m = 2..5), and
provably m ≤ pw ≤ m + 1 in general (n ≥ m ≥ 2); the kink frontier achieves
width m + 1 — i.e., the true pathwidth at every probed size, and at worst one
more than optimal in general. No literature source states the exact value; the
earlier draft's implication was indeed unsourced, and for the *whole-column*
scan it is false.**

- Pathwidth = vertex separation number: Kinnersley [Kin92].
- Lower bound pw ≥ tw ≥ min(m,n): the king graph contains the m×n grid
  P_m □ P_n as a spanning subgraph, and tw(P_m □ P_n) = min(m,n) (Bodlaender's
  survey [Bod98]); treewidth is subgraph-monotone.
- Upper bound pw ≤ m+1: the column-major (cell-at-a-time) order has, after
  placing rows ≥ i of column j and rows < i of column j+1, boundary exactly
  (m−i+1) + i = m+1; max over the sweep is m+1. (Two-line argument; also
  reproduced by probe P0's exact DP.)
- Exact value, probe P0 (`experiments/probe_king_pathwidth.cpp`, exact
  vertex-separation DP over all 2^{mn} subsets): pw = 3 at 2×{4,6,8}; pw = 4
  at 3×{4..8}; pw = 5 at 4×{4..7}; pw = 6 at 5×5. Every case: **m+1**.
  (For m = 2 there is also a one-line proof: two adjacent columns form K₄, so
  tw ≥ 3.)
- Searched for a citable exact statement: king graph pathwidth/treewidth;
  strong product of paths treewidth/pathwidth; Kozawa–Otachi–Yamazaki [KOY14]
  product lower bounds (their strong-product bramble bound gives only
  tw ≥ had(P_n)·bn(P_m)/…-level constants, i.e., tw ≥ 3 here — far below m+1).
  Nothing found; logged in `papers/MISSING.md`.

**Consequences for this brief.** The kink frontier (window of H+1 cells, bag =
window + active cell, width H+1) sits exactly at the pathwidth at all probed
sizes — there is no better frontier *geometry*, closing that door with a
matching lower bound rather than folklore. The whole-column strip scan (bags
= two columns, width 2m−1) does *not* achieve pathwidth; its economy comes
from state compression, not bag size. And since a candidate must beat the
kink frontier *width* to beat its state ceiling on the same rule, the only
open axis is the rule itself — which is where B1 and B2 stand.

---

## Kill list

| # | Candidate | Killed by |
|---|-----------|-----------|
| K1 | **ZDD / frontier-based search** (Knuth simpath lineage; Kawahara–Inoue–Iwashita–Minato [KIIM17]) | Citation: the method's "mate" array is precisely the frontier connectivity partition with component-death bookkeeping — the incumbent's rule in a compressed-index costume. Zero independence on the stated axis. |
| K2 | **Rank-based reduction / representative sets** as a counting engine (BCKN [BCKN15] reduce-to-2^{pw} row basis; Fomin et al. matroid representative families) | Citation + argument: GF(2)/matroid row reduction keeps a *representative* subset of partition states — sound for existence/optimization, unsound for exact counting, which needs every state's multiplicity. BCKN's own *counting* variant works by determinants over the cut space — that algebra **is** candidate B1. Folded into B1, not an independent entry. |
| K3 | **Cut-and-count proper** [CNP+11] | Citation: isolation-lemma, Monte-Carlo, mod-2 — decides, does not count. Its exact-counting descendant is B1. |
| K4 | **Generic pathwidth/treewidth DP with partition states** | Probe P0 + [KN25]: the incumbent already sits at the graph's exact pathwidth (all probed sizes), and pure-DP formulations provably cannot escape partition-type state; there is nothing here that is not the incumbent. |
| K5 | **#SAT model counters as a reach instrument** (sharpSAT-td [KJ21], GANAK [SRSM19]) | Probe P1 (no counter exists on the fleet — 10 binaries checked, all absent) + citation [BCMS16]: the counter's component cache across a width-H cut is bounded below by frontier-behavior count, so at best it re-pays the incumbent's state budget through CNF overhead, for no reach. Survives *only* as the substrate of B2, where the point is the certificate, not the count. |
| K6 | **First-component inclusion–exclusion recursion** (peel the component of the minimal cell) | Argument + [KN25]: the "allowed remainder" region depends on the peeled component's shape, so the recursion is either exponential in shapes (object-materialising — closed door) or becomes a frontier DP carrying the component's boundary, i.e., the incumbent. |

Exhausted-list items (mod-p/CRT, Redelmeier variants, Lean verification of the
existing implementation, etc.) were not re-proposed. One boundary note: B1 at
production scale would likely use CRT *internally* for coefficient arithmetic;
that is arithmetic plumbing inside a rule-independent enumeration, not the
banned "CRT as a second source" — flagging so nobody mistakes it later.

---

## Needs jasonp's decision

1. **B1 go/no-go** (and merge with Teammate A's Potts/FK proposal if they
   filed one): a C++ measurement run per the plan above. This is the cheap,
   high-value one.
2. **B2 toolchain**: building D4 + CPOG tooling from third-party source into
   `build/` — outside code entering the repo's build, so his call before
   anything is cloned.
3. Whether H = 15–17 stretch (kink-only anchors) is worth sizing after the
   B1 H = 10 C++ calibration point exists.

---

## Citations

- [CNP+11] M. Cygan, J. Nederlof, M. Pilipczuk, M. Pilipczuk, J. M. M. van
  Rooij, J. O. Wojtaszczyk, "Solving connectivity problems parameterized by
  treewidth in single exponential time," FOCS 2011. arXiv:1103.0534.
- [BCKN15] H. L. Bodlaender, M. Cygan, S. Kratsch, J. Nederlof, "Solving
  weighted and counting variants of connectivity problems parameterized by
  treewidth deterministically in single exponential time" / "Deterministic
  single exponential time algorithms for connectivity problems parameterized
  by treewidth," Inform. and Comput. 243 (2015). arXiv:1211.1505.
- [KN25] K. Kluk, J. Nederlof, "Lower bounds on pure dynamic programming for
  connectivity problems on graphs of bounded path-width," 2025.
  arXiv:2512.23121.
- [SS01] J. Salas, A. D. Sokal, "Transfer matrices and partition-function
  zeros for antiferromagnetic Potts models. I. General theory and
  square-lattice chromatic polynomial," J. Stat. Phys. 104 (2001).
  arXiv:cond-mat/0004330. (Fortuin–Kasteleyn partition-state transfer matrix.)
- [BNAH23] R. E. Bryant, W. Nawrocki, J. Avigad, M. J. H. Heule, "Certified
  knowledge compilation with application to verified model counting," SAT
  2023, LIPIcs 271, doi:10.4230/LIPIcs.SAT.2023.6; extended version
  arXiv:2501.12906. (Lean 4 verified CPOG checker + counter.)
- [BCMS16] S. Bova, F. Capelli, S. Mengel, F. Slivovsky, "Knowledge
  compilation meets communication complexity," IJCAI 2016.
  https://www.ijcai.org/Proceedings/16/Papers/147.pdf.
- [KIIM17] J. Kawahara, T. Inoue, H. Iwashita, S. Minato, "Frontier-based
  search for enumerating all constrained subgraphs with compressed
  representation," IEICE Trans. Fundamentals E100-A(9):1773–1784 (2017).
  doi:10.1587/transfun.E100.A.1773.
- [SRSM19] S. Sharma, S. Roy, M. Soos, K. S. Meel, "GANAK: a scalable
  probabilistic exact model counter," IJCAI 2019.
  https://www.ijcai.org/proceedings/2019/0163.pdf.
- [KJ21] T. Korhonen, M. Järvisalo, "Integrating tree decompositions into
  decision heuristics of propositional model counters," CP 2021 (short);
  competition report arXiv:2308.15819 (SharpSAT-TD).
- [Kin92] N. G. Kinnersley, "The vertex separation number of a graph equals
  its path-width," Inf. Process. Lett. 42(6):345–350 (1992).
  doi:10.1016/0020-0190(92)90234-M.
- [Bod98] H. L. Bodlaender, "A partial k-arboretum of graphs with bounded
  treewidth," Theoret. Comput. Sci. 209(1–2):1–45 (1998).
  doi:10.1016/S0304-3975(97)00228-4.
- [KOY14] K. Kozawa, Y. Otachi, K. Yamazaki, "Lower bounds for treewidth of
  product graphs," Discrete Appl. Math. 162:251–258 (2014).
  doi:10.1016/j.dam.2013.08.005.
