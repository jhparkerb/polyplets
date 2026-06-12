# Plan: Extending Polyplets (Option 2)

*Drafted June 11, 2026. Companion to `research-options.md`; sibling of
`plan-option3-polyhexes.md` (shared engine, see §8). The primary
isolation-safe project. OEIS extents and terms verified against live b-files
on this date.*

## 1. Goal and why this target

Extend **fixed polyplets** [A006770](https://oeis.org/A006770) (currently
**n = 18**) and **free polyplets** [A030222](https://oeis.org/A030222)
(currently **n = 17**) — connected sets of square cells under king-move
adjacency (edge *or* corner contact).

Why this is the best isolated project on the list:

- **Effectively dormant.** Free polyplets: last extended September 2002
  (Joseph Myers). Fixed: a(18) appeared December 2025 only as an OEIS editor's
  import from Tremblay–Vernay's general-purpose *generation* paper — nobody is
  running a polyplet research program.
- **An algorithmic moat.** Every existing term comes from generation, whose
  cost grows ×λ ≈ 7 per term (see §5) and is hard-capped near n ≈ 22. A
  transfer-matrix algorithm (TMA) counts without generating and should land in
  the 30s — territory no current actor can reach with their methods. Isolation
  is structural, not luck.
- **Quick wins exist before the hard part.** A modernized multithreaded
  Redelmeier can take the record from 18 to ~21–22 for hundreds-to-thousands
  of core-hours (§5), giving published results while the TMA is built.
- **Physics hook.** Polyplets are the site animals of the square lattice's
  matching (king) lattice, which appears in site-percolation duality; new
  series terms have an audience beyond OEIS.

## 2. State of the art

| Sequence | What | Known to | Last real computation |
|---|---|---|---|
| [A006770](https://oeis.org/A006770) | fixed polyplets | 18 | Tremblay–Vernay 2024 (generation; imported Dec 2025) |
| [A030222](https://oeis.org/A030222) | free polyplets | 17 | Joseph Myers, Sep 2002 |

Latest terms and ratios (from b-files): a(17) = 3,340,366,308,393;
a(18) = 22,471,158,811,164; a(18)/a(17) = 6.727, with ratios still rising
(6.681, 6.705, 6.727 at n = 16, 17, 18) → growth constant λ ≈ 7 (empirical;
no published precise estimate found — nailing it down is itself a deliverable).

No symmetry-class sequences (Mason-style M90/R180C/… decomposition) exist for
polyplets; the free/fixed bridge below n ≤ 17 predates that framework. Creating
them is part of this plan (§3.4) and is virgin OEIS territory.

## 3. Technical approach

### 3.1 Phase G — generation engine (oracle + quick records)

Redelmeier's algorithm with king-move adjacency, modernized: neighborhood-
counter frontier (Shirakawa's optimization), iterative backtracking, bitboard
cell sets, and synchronization-free thread partitioning (subtree mod thread-ID).
Roles:

1. **Verification oracle** for everything else (exhaustive ground truth,
   per-bounding-box cross-checks).
2. **Record terms now**: a(19) ≈ 1.5×10^14 … a(22) ≈ 5×10^16 generated
   shapes. At a realistic 10^8–10^9 nodes/sec/core, a(19)–a(20) are
   workstation-days and a(21)–a(22) are cloud-burst scale (~10^3–10^4
   core-hours). Each term is a new published record.
3. **Symmetric-class counting** for the free/fixed bridge (§3.4) — symmetric
   polyplets are ~√(fixed) rare, so generation covers them to roughly twice
   the n of the fixed record.

### 3.2 Phase T — the TMA, and its one research wrinkle

Jensen-paradigm TMA: sweep a boundary column across bounding boxes, database
from boundary signatures to partial-animal counts by size, aspect-ratio trick
(count animals at least as wide as tall, double the strictly-wider ones; needs
the touch-top/touch-bottom signature bits), final counts assembled over box
heights.

**The wrinkle — non-crossing fails.** On 4-connectivity lattices (square,
triangular), two connected components touching the boundary can never
interleave (planarity), so signatures are non-crossing partitions — Motzkin-
encodable, ~3^W states for boundary width W. The king graph is **non-planar**:
two disjoint diagonal chains can cross (cells (0,0)–(1,1) connected, and
(1,0)–(0,1) connected, all four distinct). Boundary components CAN interleave,
so the signature space is a larger family of partitions with limited
crossings. Consequences and handling:

- The clean 5-letter Motzkin alphabet is unavailable, but it was always an
  optimization: Jensen-style implementations fundamentally use a hash table
  from signature → counts. Represent signatures as canonical set-partition
  codes of the boundary's occupied cells; correctness is unaffected.
- The open question is the *reachable* state count: some base k with
  3 < k ≤ (worst-case partition growth). Crossings under king moves are
  geometrically constrained (a crossing costs cells), so k is plausibly
  modest — but this is exactly what milestone M3 measures empirically at
  widths 8–14 before any scale-up decision. The measured k is a publishable
  observation either way (first TMA on a non-planar lattice graph, as far as
  this survey found).
- Even pessimistically (k ≈ 6), TMA work ~ k^(n/2) ≈ 2.45^n crushes
  generation's 7^n; the method wins by a widening margin regardless.
- Transition table: more neighbor cases than 4-connectivity (the kink cell
  interacts with up to 4 already-swept neighbors: W, NW, N, and SW-diagonal
  effects on component merging). Derive once, verify exhaustively against the
  oracle per bounding box. Component merges can join *more than two*
  components in one step (a king-adjacent cell can touch 4 distinct
  components) — the update code must handle k-way merges.

**Pruning** carries over conceptually (connection budget n_c, span budget,
aspect budget) but must be re-derived: king moves close gaps cheaper (a
diagonal chain of g cells spans g rows AND g columns simultaneously), so
prune bounds are looser than on the square lattice. Expect pruning to help
less than it did for Barequet–Ben-Shachar; the sweep-direction question (is a
45° sweep better or worse under king adjacency? — note the king lattice is
self-dual-ish under 45° rotation in an interesting way: diagonal neighbors
become orthogonal) is a small research study, mirroring the polyhex plan's M4.

### 3.3 Modernization stack (shared with polyhex plan)

k-way signature-set partitioning for parallelism; compressed inactive sets;
counts mod 2–3 independent 62-bit primes with CRT recombination (memory +
free verification); checkpoint/restart on all runs > 1 day.

### 3.4 Free counts and new symmetry sequences (Burnside)

Free(n) and one-sided(n) follow from Fixed(n) plus counts of polyplets
invariant under each symmetry placement (D4 acting on the square lattice —
the same M90/M90V/M45/R180C/R180M/R180V/R90C/R90V decomposition as option 1,
since polyplets live on the same lattice; only the connectivity rule differs).
None of these sequences exist for polyplets: this plan creates them. The
symmetric classes are ~λ^(n/2)-rare (≈ 2.65^n), so Phase-G generation restricted
to each symmetry class covers them comfortably to wherever the fixed TMA
reaches (n ≈ 36+ needs only ~10^15-node searches at the very top end, and the
mirror classes can reuse the TMA with axis-weighting as in Shirakawa's method
if generation tires first). Derived deliverables: A030222 extension, a
one-sided polyplet sequence (does not currently exist), and 8 new
symmetry-class sequences — all in territory nobody is working.

## 4. Milestones

| # | Milestone | Exit criterion | Record impact |
|---|---|---|---|
| M0 | Scaffolding | build, mod-p/CRT + bignum libs, golden tests pinned to 18 + 17 known terms | — |
| M1 | Generation oracle | matches A006770 n ≤ 18 and A030222 n ≤ 17; per-box counts available | — |
| M2 | Generation records | a(19), a(20) fixed (+ free via §3.4) | **record 18 → 20** |
| M3 | TMA core + calibration | reproduces n ≤ 18 per-box exactly; reachable-state base k measured at W = 8–14; ceiling computed | — |
| M4 | Sweep/pruning study | king-adjacency prune bounds derived + verified; 45°-sweep A/B at small n | — |
| M5 | Modernized TMA | parallel + mod-p + checkpointing; re-verify | — |
| M6 | Production | staged runs upward while cost ≤ budget (target band n ≈ 28–38 pending M3) | **record → 28+** |
| M7 | Symmetry classes + free/one-sided | Burnside components to match fixed extent | A030222 + new sequences |
| M8 | Publication | OEIS b-files + edits; arXiv note (first non-planar-lattice TMA, measured k, λ estimate) | — |

M2 guarantees the project publishes records within weeks regardless of how
the TMA wrinkle resolves. M3 is the go/no-go gate for how far M6 aims.

## 5. Cost model (assumptions explicit, replaced by M3/M2 measurements)

- **Counts** grow ×λ ≈ 7/term → a(19) ≈ 1.5×10^14, a(20) ≈ 1.1×10^15,
  a(21) ≈ 7×10^15, a(22) ≈ 5×10^16.
- **Generation** cost ≈ count: at 3×10^8 nodes/s/core — a(19) ~140 core-h,
  a(20) ~10^3 core-h, a(21) ~6×10^3 core-h, a(22) ~4×10^4 core-h (cloud
  burst, ~$10^3). Diminishing returns exactly as designed; stop when TMA
  overtakes.
- **TMA** work ~ poly(n)·k^(n/2), memory ~ k^(n/2) signatures × bytes-per-
  entry (mod-p keeps entries small). If k ≈ 4: n = 36 needs ~4^18 ≈ 7×10^10
  raw signature-slots before pruning/reachability — large but in modern-server
  range with chunking; if k ≈ 6: n ≈ 30 is the comparable point. Hence the
  wide target band 28–38 until M3 pins k. Even the band's bottom doubles the
  21st-century record progress on this sequence.

## 6. Verification

- Oracle equality on every per-bounding-box count for n ≤ 18 (much stronger
  than matching 18 aggregate terms).
- Dual-prime runs for all production computations; CRT consistency required.
- Burnside cross-check: Free(n) assembled from components must match A030222
  for n ≤ 17, and One-sided must satisfy Free ≤ One-sided ≤ 2·Free.
- Ratio smoothness: a(n+1)/a(n) must continue the 6.68 → 6.73 → … monotone
  approach to λ; kinks flag bugs.
- Tremblay–Vernay's a(18) provides an independent-implementation anchor at
  the top of the known range.

## 7. Risks

| Risk | Read | Mitigation |
|---|---|---|
| Reachable signature base k large (crossing partitions proliferate) | the key unknown | M3 measures before scale-up; generation records (M2) bank value regardless; even k = 6 beats generation asymptotically |
| k-way component merges / transition-table bugs | certain, just work | oracle-driven development; exhaustive per-box equality n ≤ 18 |
| Pruning much weaker under king adjacency | likely | budgeted in target band; M4 quantifies; mod-p + chunking carry memory load |
| Competition | minimal — generation-bound actors, 24-year-dormant free side | the moat is the method; publish M2 records early to flag the territory anyway |
| Scope creep into symmetry sequences delays fixed-count headline | moderate | M7 strictly after M6; fixed records are the priority |

## 8. Relationship to the polyhex plan

Shared: engine architecture (signature DB, pruning framework, k-way parallel
sets, mod-p/CRT, checkpointing), oracle-vs-TMA methodology, staged-record
philosophy. Different: polyplets keep the square lattice but break
non-crossing (partition signatures, k unknown); polyhexes keep non-crossing
but change the lattice (triangular formulation, richer transition table).
Doing polyplets first front-loads the generic infrastructure plus the more
interesting open question; polyhexes then inherit ~80% of the code. The plans
are independent — either stands alone.

## 9. Immediate next actions

1. Repo scaffolding + golden-data harness (b-files already fetched this
   session; pin them).
2. M1 oracle: Redelmeier-with-king-moves (days; zero risk).
3. M2 production generation runs for a(19)–a(20) while developing the TMA.
4. Literature spot-check during M0: confirm no published TMA exists for
   king-lattice animals (search terms: "king lattice animals", "matching
   lattice site animals series", Mertens' perimeter-polynomial papers) — both
   for prior-art hygiene and for the arXiv note's novelty claim. Supporting
   datum already in hand: Tremblay–Vernay (`papers/tremblay_vernay.pdf`, the a(18)
   source) state that in their (a,b)-connectivity taxonomy the
   (4,8)/(8,4)/(8,8) figure families "have never been previously studied" —
   and those hole-constrained polyplet variants are further free territory
   adjacent to this project if wanted.
