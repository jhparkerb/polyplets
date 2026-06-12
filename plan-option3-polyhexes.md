# Plan: Extending Fixed Polyhexes (Option 3)

*Drafted June 11, 2026. Companion to `research-options.md` and
`plan-option1-free-gap.md` (superseded for execution by the isolation
criterion; this plan and the polyplet project are the isolation-safe picks).
OEIS extents verified against live b-files on this date.*

## 1. Goal and why this target

Extend **fixed polyhexes** [A001207](https://oeis.org/A001207) beyond its
current record of **n = 46**, which has stood since **March 2004** (Markus
Vöge). Working target: **n ≈ 52–56**, with the exact ceiling set by a
calibration milestone rather than guessed in advance.

Why this is a good isolated project:

- **Dormant 22 years.** Last extension 2004; none of the currently active
  square-lattice people (Barequet/Ben-Shachar, Shirakawa, Mason-on-fixed-counts)
  have touched it. Mason's 2023 activity on the *free* polyhex side
  ([A000228](https://oeis.org/A000228), n = 36) consumes fixed counts as input
  and does not compete with producing them.
- **Proven method, ancient hardware.** The record was set with a transfer-matrix
  algorithm (TMA) on 2002–2004 hardware. Twenty-two years of cores and RAM, plus
  the pruning ideas published since (Barequet–Ben-Shachar 2024), have never been
  applied.
- **A real algorithmic question on top.** The 2024 square-lattice speedup came
  from changing the sweep direction relative to the lattice (45° rotation →
  far more aggressive pruning). Whether the hexagonal lattice has an analogous
  "good direction" is unexplored — that analysis is the publishable extra.
- **Outside audience.** Polyhexes with h hexagons are (a superset of) benzenoid
  hydrocarbon skeletons; counts get cited in chemistry literature.

## 2. State of the art

| Sequence | What | Known to | Last touched |
|---|---|---|---|
| [A001207](https://oeis.org/A001207) | fixed polyhexes | **46** | Vöge, Mar 2004 |
| [A000228](https://oeis.org/A000228) | free polyhexes | 36 | Mason, Jul 2023 |
| [A006535](https://oeis.org/A006535) | one-sided polyhexes | 36 | — |
| [A018190](https://oeis.org/A018190) | benzenoids (simply connected) | ~50 | Jensen-school parallel TMA |

Key literature (read in full during Phase 0):

- Vöge & Guttmann, [On the number of hexagonal polyominoes](https://www.sciencedirect.com/science/article/pii/S0304397503002299),
  TCS 307 (2003) 433–453. The record-setting method: refined finite-lattice /
  transfer-matrix enumeration of polyhexes **as site animals on the triangular
  lattice** (the two problems are equivalent; the triangular formulation is
  what the TMA actually sweeps). Reached n = 35 in-paper; the same machinery
  produced n = 46 by 2004. Also: growth constant τ estimated 5.1831478(17),
  rigorous bounds 4.8049 ≤ τ ≤ 5.9047.
- Jensen, [A parallel algorithm for the enumeration of benzenoid hydrocarbons](https://arxiv.org/abs/0808.0963)
  — closest prior art for parallelizing a hexagonal-geometry TMA (signature-set
  splitting on this lattice family).
- Barequet & Ben-Shachar 2024 (local copy `papers/counting_polyominoes_revisited.pdf`)
  — the pruning framework and sweep-direction analysis to transplant.
- Vöge–Guttmann–Jensen, "A parallel algorithm…" lineage + Guttmann (ed.),
  *Polygons, Polyominoes and Polycubes* (2009), ch. 16 — tabulates the n ≤ 46
  data (source of the current b-file).

## 3. Technical approach

### 3.1 Representation

Work on the **triangular lattice site-animal formulation** (each hexagon ↔ a
site of the triangular lattice; adjacency = 6 neighbors). The TMA sweeps a
boundary line across a bounding parallelogram, maintaining a database mapping
boundary *signatures* (occupancy + connectivity classes of boundary sites,
Motzkin-path-like encoding) to counts of partial animals by size. Same
paradigm as Jensen's square-lattice algorithm; the transition table and the
neighbor geometry differ.

### 3.2 Modernization layers (in order of expected value)

1. **Pruning** (the big one): discard signatures that cannot reach a valid
   counted animal within the remaining cell budget — connection cost n_c
   (min cells to join all components; DP or MST over components), span cost,
   and aspect-criterion cost, combined as in Barequet–Ben-Shachar §4.1. Their
   data shows pruning, not raw speed, is what moved n = 56 → 70 on the square
   lattice.
2. **Parallelism + memory**: k-way signature-set partitioning by occupancy
   pattern (Jensen's scheme, generalized k as in B–BS §4.3), compressed
   inactive sets, checkpoint/restart.
3. **Arithmetic**: counts modulo 2–3 independent 62-bit primes, CRT-recombined;
   halves memory per entry vs. bignum and gives verification for free.
4. **Sweep-direction study** (the research garnish): the triangular lattice
   has inequivalent sweep orientations (perpendicular to a lattice axis vs.
   rotated 30°/90° — the hexagonal analog of B–BS's 45° trick). For each
   candidate direction, redo the gap-closing cost analysis (how many cells
   must be spent to close a gap of k boundary cells — the quantity that
   determines pruning aggressiveness) on paper, then A/B the directions
   empirically at n ≈ 30 where runs take minutes. Pick the winner for
   production. Either outcome (a better direction exists / the standard one is
   provably best) is a reportable result.

### 3.3 What is deliberately out of scope

Free/one-sided polyhexes (A000228/A006535) require the D6 symmetry-class
machinery — that is Mason's active lane and re-introduces the coordination
problem this project selection was designed to avoid. Fixed counts stand alone
as the headline result. (If desired later, symmetry classes are a separate
decision with the option-1 plan as a template.)

## 4. Milestones

| # | Milestone | Exit criterion |
|---|---|---|
| M0 | Scaffolding + literature | C++/Rust build, GMP/mod-p libs, golden-data tests pinned to the 46 known terms; V–G and Jensen papers read |
| M1 | Brute-force oracle | Redelmeier-style hex enumerator; matches A001207 for n ≤ ~18, and per-bounding-box counts for cross-checks |
| M2 | TMA core correct | Reproduces a(1)–a(35) (V–G in-paper range) on a laptop |
| M3 | **Calibration** | Reproduces a(1)–a(46); measured per-term time/memory growth factor g; production ceiling computed from g, not guessed |
| M4 | Sweep-direction study | Paper analysis + empirical A/B at n ≈ 30; direction chosen |
| M5 | Modernization complete | Pruning + k-way parallel + mod-p + checkpointing; re-verify n ≤ 46 |
| M6 | Production | New terms in staged runs (48, 50, 52, … while cost ≤ budget), each run duplicated mod a second prime |
| M7 | Publication | b-file + OEIS edits for A001207; arXiv note (method, direction analysis, new terms, updated τ estimate) |

The staged structure of M6 means **every completed stage is already a record**;
nothing is wagered on reaching the final target.

## 5. Cost model (to be replaced by M3 measurements)

Two growth rates matter and must not be conflated:

- **Counts** grow ×τ ≈ 5.18 per term (this only affects digit/limb sizes —
  handled by mod-p).
- **TMA work/memory** grows by some factor g per term, where g ≪ τ is the
  whole point of transfer matrices. On the square lattice g ≈ √2 after
  pruning; the triangular lattice's 6-neighbor adjacency means richer
  signature interactions and plausibly a somewhat larger g (rough prior:
  1.5–2.0). The plan deliberately makes no commitment until M3 measures it.

Sanity bound on the target: the 2004 record machine-hours ≈ O(10²–10³) on
~2003 hardware. A modern 64-core node is ~10²–10³× that throughput, and
pruning historically buys another large factor. At g = 1.7, a 10³× total
budget increase is ~13 terms (n ≈ 59); at g = 2.0, ~10 terms (n ≈ 56). Hence
the working target band 52–56 with upside. Memory is the likelier binding
constraint (as always for TMAs); 256 GB–1 TB class hardware, with compressed
chunked signature sets, mirrors what comparable runs have needed.

## 6. Verification

- M1 oracle cross-checks all small-n behavior including per-box counts.
- All 46 known terms reproduced before any new term is claimed (n ≤ 35
  validates against the published paper independently of the b-file).
- Every production run executed under two independent primes (different code
  paths exercised, results CRT-consistent); disagreement localizes errors.
- Ratio test: a(n+1)/a(n) must approach τ = 5.1831453(4) (refined value from
  the Guttmann–Jensen appendix, `papers/guttmann_series_appendix.pdf`, which is also
  the authoritative source of the n ≤ 46 table) smoothly; a kink flags a bug.
  Bonus deliverable: refreshed differential-approximant estimate of τ with the
  new terms.

## 7. Risks

| Risk | Read | Mitigation |
|---|---|---|
| g (per-term cost growth) worse than square-lattice experience | plausible | M3 calibration before any hardware spend; staged targets mean partial success is still a record |
| Memory wall before CPU wall | likely eventually | mod-p, compression, k-way chunking, out-of-core sets; accept whatever n the box affords — still a record |
| Someone ports the 45° trick to hexagonal first | low — 22 years dormant, active groups publicly busy elsewhere (more square terms, 3D) | M4 is early in the schedule precisely so the novel piece lands with the first release |
| Transition-table subtleties on triangular lattice (more neighbor cases) | certain, just work | oracle-driven development from M1; per-box cross-checks |
| Free-polyhex entanglement pulls in coordination | avoidable | scope rule §3.3: fixed counts only |

## 8. Relationship to the polyplet project (option 2)

Same engine, different adjacency: signature database, pruning framework,
k-way parallel sets, mod-p/CRT, checkpointing, and the oracle-vs-TMA testing
methodology are all shared. Whichever project goes first pays the ~80% common
cost; the second becomes a few weeks of transition-table and geometry work.
Recommended order remains polyplets first (strictly simpler geometry — square
lattice with 8-neighbor adjacency — and zero competition), polyhexes as the
second campaign reusing the core. But the two are independent; this plan
stands alone if polyhexes go first.

## 9. Immediate next actions

1. ~~Obtain the Vöge–Guttmann TCS 2003 PDF~~ Done — `papers/voge_guttmann_2003.pdf`
   (and Jensen's benzenoid paper, `papers/jensen_benzenoid_parallel.pdf`). Remaining:
   read both in full and extract the exact signature encoding and era resource
   numbers to sharpen §5.
2. Repo scaffolding + golden-data test harness pinned to the 46 known terms.
3. M1 brute-force hex oracle (a few days; immediately useful, zero risk).
4. TMA core against the triangular-lattice formulation, oracle-driven.
