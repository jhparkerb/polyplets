# Spin-basis repricing (INV-8) — verified counts, a corrected geometry, the dispatchable job

2026-08-12, wave-5 queue scout, rows INV-8 (primary), INV-6, INV-7, per
`docs/triangle-round3-brief.md` under `docs/skeptical-reader-standard.md` and
`docs/r3-job-dispatch.md`. Scripts: `experiments/tristruct/r3_spin_counts.py`,
`r3_spin_pipeline.py` (+ `.log`s), pure Python, exact integers, 6.5 s total
foreground wall. Everything below re-derived from the lattice definition;
banked data read only post-hoc (disclosure block).

**Verdict in one line: the repricing is real and the job is dispatchable —
peak RAM ~10 GiB, ~23 thread-days at a conservative measured anchor, T(40,20)
and T(40,21) mod 2 by a rule class with no partitions in the state — but the
dispatched premise ("W ≤ n−H+1 = 20, so cut 20") is FALSE for king animals
(counterexample below), so the correct design keeps the strip in the H
direction with cuts 18..21, and the same false bound also kills queue row
GEN-1's transposed-L6-1 idea as written.**

## Disclosure block (mapped to phase 1 per the brief)

    claim:                             T(n,20) and T(n,21) mod 2 for all n <= 40
                                       (prize: the two n=40 cells the residue/CRT
                                       ladder cannot afford), by the q=2 spin-basis
                                       colour DP — no connectivity decision, no
                                       partitions in the state
    share of a(40) reached:            7.00% (bands: H=20 4.1582% + H=21 2.8431%;
                                       provenance 'real-sweep' both, quoted from
                                       tri.provenance(40,H) this session)
    bits against enumeration error:    0 today; projected at phase 2: 1 bit/cell
                                       (mod 2) on the two target cells, plus 1 bit
                                       on each banked real-sweep cell (n,20|21),
                                       n <= 39, reproduced by the same runs —
                                       distinct banked quantities, so they add
    bits against formula-chain error:  n/a — targets swept cells only
    rule independence:                 levels 1 AND 2 (entry ticket below, argued
                                       against harness Part 3's three propositions)
    derivation independence:           DP, accounting, and ground-truth grower
                                       written this session from the lattice
                                       definition; banked triangle read only as
                                       post-hoc comparison (pipeline §6)
    input footprint:                   0 banked cells consumed by any derivation;
                                       comparison set = 28 cells n<=7 + row sums
                                       n<=7 + the 2 target-cell parities quoted
    checker:                           phase-2 artifact = the C++ engine + logs;
                                       reader side = r3_spin_pipeline.py (6 s,
                                       laptop, self-contained: grows its own
                                       animals, brute-forces its own Z) + residue
                                       comparison against the banked file
    sensitivity:                       RED battery measured at desk: drop-NW,
                                       drop-SW, rook stencil mutants flip 12/12/4
                                       cells at n<=7 vs self-grown truth (0 false
                                       passes); value-level, not census-level
    prior-work grep:                   git log --all --oneline --name-only --
                                       'results/*.md' 'docs/*.md' 'docs/**/*.md'
                                       | grep -iE 'spin|pell|parity|mod4|...';
                                       per-branch git grep for A001333/pell/
                                       monochromatic; git grep for the 54,608,393
                                       count. Hits: only this round's own files
                                       (L6-2, INV-4 appendix, queue INV-8/GEN-1)
                                       and second-source B1. The Pell census, the
                                       W-bound correction, and the pipeline
                                       verification appear nowhere else.

## Entry ticket — where is king-connectedness decided, and what is shared

Nowhere. The DP counts pairs (S, f) where f 2-colours S constant on
king-components — equivalently, colourings in which king-adjacent cells agree,
a purely local constraint. Z(2) = Σ_S 2^{c(S)}, and T ≡ Z-derived N/2 (mod 2)
because every disconnected class contributes 2^c ≡ 0 (mod 4). Against the
harness Part 3 propositions: **proposition 2 (label partition as sufficient
statistic, stranded-component death) is not assumed** — the state is a colour
string, not a partition; two same-coloured separated runs are never asserted
connected or disconnected, nothing is ever united, nothing is ever killed for
stranding (disconnected subsets flow through and cancel mod 4).
**Proposition 3 (completion predicate) is not assumed** — there is no
closability test; harvest is an area-slot read plus exact extent differencing,
the accounting layer the strip engine already two-sources. What is shared with
the production engines is **proposition 1's weakest tier only**: the
king-adjacency definition itself (the r−1,r,r+1 clash stencil) and frontier
separation. Level 2: the failure modes — clash-stencil error, mod-4
bookkeeping, differencing arithmetic — have no carrier in a union-find engine,
and wrong-union/wrong-death/wrong-completion have no carrier here. This is the
same adjudication the independence adversary upheld for L6-2 ("no partitions
in the state at all"); the verification and the corrected geometry below are
what this file adds. Note honestly, as L6 did: the mod-2 bit is a modulus one
existing source (symcount_fast, itself label-free) already reaches; the value
here is a *third* rule class on two cells that are otherwise single-sourced at
any modulus beyond it, and cheap coverage where the partition ladder is
priced out (68.1 GiB sole-tenant at H=20; 215.8 GiB at H=21, per ADV-4).

## 1. The verified counts (task 1)

State = one symbol per strip row from {empty, A, B}; validity = occupied runs
monochromatic (vertically adjacent occupied cells are king-adjacent, so a
clash inside a column is weight 0). Verified independently of the
predecessor's derivation (`r3_spin_counts.py`):

- **Brute enumeration** of all 3^m strings at m = 1..12 matches the
  recurrence **t_m = 2 t_{m−1} + t_{m−2}**, t_1 = 3, t_2 = 7 (my own
  derivation via the {E, A, B} row transfer; this is the companion Pell
  sequence, t_m = A001333(m+1) = ((1+√2)^{m+1} + (1−√2)^{m+1})/2).
- **Reachability**: every valid string is reachable (the empty column
  transitions to any valid string); checked mechanically m ≤ 7.
- Exact values:

      t_18 =   9,369,319      t_19 =  22,619,537
      t_20 =  54,608,393      t_21 = 131,836,323      (t_22 = 318,281,039)

  **Cut 20 = 54,608,393 and cut 21 = 131,836,323, exactly as the dispatch
  stated** — the numbers are right; their assignment to the computation was
  not (next section).
- **Cell-at-a-time window census** W(m) (m+1 mixed cells, max over kink row):
  enumerated exactly m ≤ 9, follows the **same Pell recurrence** with seeds
  W(2) = 15, W(3) = 37 (verified at all 8 enumerated points), and is bounded
  by t_{m+1} unconditionally (the window's constraint graph contains a
  Hamiltonian path of its cells, so window colourings inject into path
  strings — the bound needs no recurrence extrapolation):

      W(18) =  20,346,159     W(19) =  49,119,973
      W(20) = 118,586,105     W(21) = 286,292,183     (≈ 0.8995 · t_{m+1})

- **Whole-column transition pairs** P_m ≈ 4.646^m (exact row-pair transfer:
  P_21 = 147,236,767,058,935): the whole-column kernel is priced out
  (~7×10¹⁵ slot-ops); **cell-at-a-time is mandatory**, as for every engine on
  this lattice.

## 2. The correction: W ≤ n−H+1 is false for king animals

The dispatched premise — monochromatic runs at "cut 20" cover H = 21 because
"the width obeys W ≤ 20" (L6-2, inherited by the INV-4 appendix and the
INV-8 queue row) — silently applies the **polyomino** bound W + H ≤ n + 1.
King animals violate it: a diagonal step advances both coordinates at once.

- Minimal counterexample: {(0,0), (1,1), (2,0)} — n = 3, H = 2, **W = 3** >
  n−H+1 = 2. At n = 40, H = 21 a zigzag path (rows 0→20→1) realises
  **W = 40**.
- Caught mechanically before it was caught by inspection: the transposed
  pipeline's m-stability assertion failed at (n,H) = (4,3) with
  g_stab − g = 258 ≡ 2 (mod 4) — an **odd number of connected classes beyond
  the claimed width bound** (`r3_spin_pipeline.log`, first run; the diagonal
  staircase (0,0),(1,1),(2,2)+1 is such a class).

Consequences:

- **The corrected INV-8 design** sweeps in the width direction with the strip
  in the H direction (cuts 18..21, below). Cost degrades from the dispatched
  "~0.3 GB, cut 20" to ~10 GiB peak and ~23 thread-days — still comfortably
  single-box, still the cheapest route to these two cells by orders of
  magnitude. The repricing vs the 3^20 = 3.5e9 original is ×12 on states
  (286M vs 3.5e9), not ×64.
- **Queue row GEN-1 is killed as written**: its transposed-L6-1 idea rests on
  the same sentence ("H=21 forces W ≤ n−H+1 = 20"). The transposed sweep does
  not shrink the cut; ADV-4's verdict — H = 21 exact does not fit ayr —
  stands. Row SPIN-2 files the closure.

## 3. The computation, specified (task 2)

Frame: strip of height m rows, sweep along width; exact ints throughout the
desk spec, **payload mod 4 in production** (sufficient: everything the route
reads is a value mod 4, T ≡ N/2 with N ≡ 2T mod 4).

- **State**: the m+1-cell mixed window (kink sweep), 2 bits per cell
  (E/A/B), key fits u64 (44 bits at m = 21); dense Pell ranking exists if
  wanted (the state language is regular; unrank is O(m) table lookups) — a
  sorted-array double buffer at 8 B key + 11 B payload (41 area slots × 2
  bits) is the baseline, per ADV-4's flat-buffer note.
- **Transition** (one cell per stage): new cell ∈ {E, A, B}; a colour choice
  is dropped iff it clashes with an occupied N/W/NW/SW neighbour (same
  stencil *geometry* as the kink kernel — shared adjacency definition, the
  weakest tier — but the state update is pure: no union, no death, no carry
  semantics beyond the window colours). Area slot shifts by 1 on occupied.
- **Column-extent (width) accounting**: harvest Z_{w,m}(n) := Σ over
  subsets of the w×m box of 2^c at every column w. A_m(n) = Z_{w,m}(n) −
  Z_{w−1,m}(n) at w = n is the width-translation fix; exact A grows with w
  (ever-wider disconnected classes) but is **stable mod 4** — verified at
  every cell n ≤ 7 — because classes wider than n are disconnected. Sweep 41
  columns; the w = 41 harvest is the in-run stability check.
- **Height-exactly-H**: second difference across strip heights,
  N_H(n) = A_H − 2A_{H−1} + A_{H−2} — row extent exactly H, the strip
  engine's own (two-sourced) accounting layer. Runs needed: m = 18, 19, 20
  (→ H = 20 column) and m = 19, 20, 21 (→ H = 21 column): **four runs,
  m ∈ {18, 19, 20, 21}**, two shared.
- **Result**: T(n,H) ≡ N_H(n)/2 (mod 2) for H ∈ {20, 21}, all n ≤ 40.
  Connectivity is never decided; it is read off a residue at the end.

Desk validation (`r3_spin_pipeline.py`, all asserted, log banked):

1. Z vs brute-force subset enumeration (own union-find on complete small
   objects) on six boxes up to 4×4 — exact, every n.
2. Full pipeline T(n,H) mod 2 vs a self-grown fixed-animal enumerator:
   **28/28 cells, n ≤ 7**; grower row totals = 1, 4, 20, 110, 638, 3832,
   23592 (match banked a(n) post-hoc); grower transpose symmetry asserted.
3. Exact N_H(n) (not just parity) vs brute translation-class sums at five
   spot cells up to N_4(6) = 821,380 — exact.
4. w-stability mod 4 asserted at every cell; banked comparison 28/28.

## 4. Cost (task 3)

Op count is arithmetic on exact state counts; the per-op constant is the
branch's measured production throughput.

- **Anchor, cited**: B1 C++ engine, H = 14, dalby (pre-round measurement on
  the `second-source` branch, `git show 5793ddf:results/second-source-candidates-B.md`):
  34.2 s/column over 20.8M transitions/column, 41 area slots →
  **40 ns per transition-slot**. Conservative for this kernel: B1's op moves
  40-byte exact coefficients through a hash; ours is a 2-bit mod-4 add.
- **Ops** (slot-ops = columns × stages/col (=m) × window states × 3 branches
  × 41 slots, 41 columns/run):

      m=18: 1.85e12    m=19: 4.71e12    m=20: 1.20e13    m=21: 3.03e13
      TOTAL 4.88e13 slot-ops

- **Wall**: 4.88e13 × 40 ns = **22.6 thread-days total** (m=21 alone: 14.0).
  MEASURED-anchored op cost, EXACT op count (window counts exact under the
  8-point-verified recurrence; unconditionally ≤ t_{m+1}, which changes the
  total by < 12%). Parallel: state-sharded per stage (the project's stock
  pattern) plus the four runs are independent — at 32 cores and 50%
  efficiency, **~1.5 days wall on one box**; sharding efficiency ASSERTED,
  the one unmeasured factor, and it moves wall, not feasibility.
- **RAM** (peak = m = 21 run): 286,292,183 states × 38 B (u64 key + 11 B
  mod-4 payload, ×2 buffers) = **10.1 GiB**; ×1.5 container margin 15.2 GiB.
  MODELED bytes/state (no RSS measured — ADV-4's caveat class), but with 5×
  headroom on ayr (78 GB) and 8× on dalby (125 GB) the go/no-go question
  L6-1 has at H = 20 does not arise here.
- **Disk**: checkpoint = one buffer dump ≈ 5.4 GiB at column boundaries;
  final artifact = 2 × 40 residues + logs, KB.
- **ayr**: fits alongside anything (10–15 GiB, ≤ 32 threads, ~1.5–3 days
  wall). **dalby**: same, more RAM slack, anchor machine for the 40 ns
  constant. Either box; both trivially.

## 5. RED design (task 4) — against the blindness this round found

The round's three incidents: structural identities pass while [q¹] is wrong
(NW-drop passes [q⁰]=0 and the binomial check); censuses blind to symmetric
stencil errors (rook and king closures reach identical state sets); and
uncompared-cell corruption. The battery is therefore **value-level and
asymmetric**, and its discriminating power is measured, not asserted:

1. **Asymmetric stencil mutants, each checked separately against self-grown
   ground truth**: drop-NW flips 12 of 28 cells at n ≤ 7 (first: (2,2),
   (3,3), (4,2)); drop-SW flips 12; the symmetric rook mutant flips only 4
   (first: (4,3)) — measured confirmation that symmetric corruption has a
   much smaller footprint, which is exactly why the asymmetric mutants are
   first-class. The engine gate: run the built binary at n ≤ 7 under each
   mutant flag and require the *exact* desk-verified flip sets — a mutant
   that agrees with truth anywhere it should differ is a build failure.
   Cannot be blind: the reference values are enumerated whole objects (own
   grower, own union-find), no frontier, no census, no shared identity.
2. **Payload fault injection**: flip one mod-4 slot in one mid-sweep state
   (small-m run); the harvested residue must change or the injection column
   must be re-run — exercises the uncompared-cell path directly.
3. **In-run structural checks, labelled for what they are**: w-stability
   (A_41 ≡ A_40 mod 4) and the q = 1-style total (Σ colourings with no
   clashes) are bookkeeping checks, **measured blind to stencil errors** at
   desk — they gate arithmetic, never correctness. Stated so nobody promotes
   them.
4. **Scale GREEN**: the production runs themselves emit T(n,20) and T(n,21)
   mod 2 for every n ≤ 39 — dozens of banked real-sweep cells reproduced by
   this rule class before the two n = 40 cells are read. A mismatch at any
   is a bug certificate for one of the two computations (forced-parity
   lemma: two correct routes cannot disagree). Caveat carried: m = 19, 20
   runs feed both target columns, so a corruption there touches both; the
   independent m = 18 and m = 21 runs and the per-column checkpoint hashes
   are the localizers.

## 6. JOB REQUEST (per docs/r3-job-dispatch.md)

    job id:            SPIN-JOB-1
    measures:          T(n,20) and T(n,21) mod 2 for all n <= 40 (four
                       cell-at-a-time spin-DP runs, strip heights m=18..21,
                       41 columns each, payload mod 4); prize cells T(40,20),
                       T(40,21) — currently single-sourced past mod 2, and the
                       two cells the L6-1 ladder cannot afford (68.1 GiB
                       sole-tenant / 215.8 GiB, ADV-4)
    decides:           whether the H=20..21 corner of the band gets a
                       second-rule-class determination. Agreement: the corner
                       is no longer kink-only at mod 2, and the phase-2
                       package (L6-1 H=15..19 + this) covers the whole band.
                       Disagreement at ANY cell: bug certificate against one
                       of the two rule classes — localized by the n<=39
                       lattice, escalates immediately.
    command:           build/r3_spin_engine --m {18,19,20,21} --cols 41
                       --nmax 40 --mod 4 --checkpoint <dir> --out <file>
                       (one tmux window per run or sequential; four runs)
    script:            engine source experiments/tristruct/r3_spin_engine.cpp
                       — NOT YET WRITTEN; this round does not build. The
                       validated executable spec it is ported from is
                       experiments/tristruct/r3_spin_pipeline.py (this file
                       §3); the port is the phase-2 build step, jasonp's call.
    wall estimate:     22.6 thread-days total (m=21: 14.0); ~1.5 days wall at
                       32 cores/50% sharding. Basis: op count EXACT
                       (4.88e13 slot-ops, window census exact under the
                       8-point Pell recurrence, unconditional bound within
                       12%); per-op MEASURED 40 ns/slot (B1 C++ at H=14 on
                       dalby, 34.2 s/col / (20.8e6 x 41), branch file cited
                       in §4) — conservative for a 2-bit payload; sharding
                       efficiency ASSERTED.
    RAM estimate:      10.1 GiB peak (m=21 run; 286,292,183 states x 38 B
                       double-buffered); x1.5 margin 15.2 GiB. Basis: EXACT
                       state count x MODELED bytes/state (no RSS measured;
                       first small-m run reports RSS/state before m=21
                       launches — same gate ADV-4 imposes on L6-1).
    disk estimate:     ~5.4 GiB checkpoint (one buffer, column-boundary);
                       artifact KB.
    cores:             parallelizes state-sharded per stage; four runs also
                       independent (m=18..21). Efficient at 8-32 cores.
    interruptible:     yes — checkpoint each column boundary; kill loses at
                       most one column of one run.
    RED control:       (i) mutant battery at n<=7 in the built binary must
                       reproduce the desk flip sets exactly (drop-NW 12
                       cells, drop-SW 12, rook 4 — value-level vs self-grown
                       truth; §5.1); (ii) n<=7 full pipeline must match the
                       28-cell desk table; (iii) one payload fault injection
                       must surface (§5.2); (iv) in-run: w-stability mod 4 +
                       banked comparison n<=39 on both columns before the
                       n=40 cells are read. Gates (i)-(iii) run before any
                       production m.
    closes:            queue rows INV-8 (as corrected here) and L6-2
                       (superseded pricing); with L6-1 H=15..19, closes "the
                       band corner stays single-sourced" for mod 2.

## 7. INV-6 — explicit GF(2) basis for the 0.44·2^H rank (desk verdict)

**Verdict: research program, not a construction — but with one new concrete
data point and one testable candidate.** CKN's explicit factorization
(arXiv:1211.1506) is specific to the matchings-connectivity matrix; nothing
in any project file names an analogous object here, and INV-4's rank was
computed by observability closure, which is non-constructive at scale. What
this lane adds: **the spin basis itself is an explicit GF(2)-linear
realization of the parity functional at dimension ~(1+√2)^H** — constructive
today, verified by this file's pipeline, and asymptotically *smaller than the
incumbent's Motzkin state count* (2.414^H vs ~3^H; at H = 21: 1.3e8 vs
4.0e8, ~7x below B1's Bell census). So the explicit-basis ladder now reads:
Bell (B1) > Motzkin (incumbent) > **Pell (spin, this file)** > 0.44·2^H
(measured floor, non-constructive) > Motzkin spatial floor. The remaining gap
is (2.414/2)^H ≈ 50x at H = 21. Testable candidate for closing it: a
row-subset-indexed family (the 2^H scaling suggests functionals indexed by
subsets of rows) checked for triangular pairing against the existing H ≤ 9
Hankel data from `r3_inv_rank_probe.py` — an afternoon of desk linear
algebra, filed as SPIN-4. Without that, no phase-2 pricing changes: the
Pell realization already collapses the parity cost to the point where the
basis hunt buys < 2x wall on the corner cells.

## 8. INV-7 — does any collapse survive over Z/4 / Z/2^m? (desk + job request)

Unmeasured, and the settling measurement is small. Over a field the Hankel
rank is THE minimal realization dimension; over Z/2^m the right invariant is
the minimal number of generators of the Hankel row module (Smith normal form
over Z/2^m: count of nonzero invariant factors, graded by 2-adic valuation).
The measurement: build the strip functional's Hankel blocks at H = 4..8
(same observability-closure machinery as `r3_inv_rank_probe.py`), reduce
over Z/4 and Z/8, and read the generator counts. Decision rule: if
generators(Z/4) tracks c·2^H (like the GF(2) rank), a mod-4 analogue of the
spin route plausibly exists via the Z/4-linear 5-colouring realization (INV-7
row) and is worth a construction hunt; if it tracks the mod-p curve
(~2.8^H), characteristic-2 collapse is a one-bit phenomenon and INV-7 closes.

    job id:            SPIN-JOB-2
    measures:          minimal generator counts of the strip-functional
                       Hankel module over Z/4 and Z/8, H = 4..8, vs the
                       measured GF(2) ranks (6/15/27/58/112) and mod-p curve
    decides:           whether a mod-4 spin-type route to the H=20..21 corner
                       is worth a construction hunt (see rule above); closes
                       or narrows queue row INV-7
    command:           python3 experiments/tristruct/r3_spin_z4_rank.py
    script:            NOT YET WRITTEN — a Z/4-payload + SNF variant of
                       r3_inv_rank_probe.py's closure probe; desk-scale
    wall estimate:     ~5 min (ASSERTED, from the 51 s INV-4 probe at the
                       same heights plus SNF overhead)
    RAM estimate:      < 1 GB (ASSERTED; H=8 blocks are ~10^3-square)
    disk estimate:     log only
    cores:             1
    interruptible:     trivially (per-H)
    RED control:       positive control: GF(2) reduction of the same blocks
                       must reproduce 6/15/27/58/112 exactly; negative
                       control: a corrupted-stencil functional must change
                       the generator counts (stencil-visible by construction
                       since the functional's values change)
    closes:            INV-7 (either way, per the decision rule)

## 9. Queue rows filed

Appended to `results/triangle-r3-queue.md`: SPIN-1 (INV-8 corrected +
JOB-REQUESTED), SPIN-2 (closes GEN-1: the W-bound is false for king animals,
counterexample + mechanical catch), SPIN-3 (q=3 spin sibling → T mod 3 on
the corner cells, cross-locks ternary-spine/L6-4; successor different in
kind), SPIN-4 (INV-6 successor: Pell realization banked, row-subset basis
test named), SPIN-5 (INV-7 → SPIN-JOB-2).

## NOT ESTABLISHED

- **Bytes/state of a real binary** (the 38 B model): no RSS measured for
  this DP at any scale; gated by the job's small-m RSS report before the
  m=21 run. Headroom is 5-8x, so this gates sizing, not feasibility.
- **Sharding efficiency** of the parallel wall (ASSERTED 50%; the 22.6
  thread-day total is the anchored number).
- **W(m) for m > 9** rests on the Pell recurrence verified at 8 enumerated
  points; the unconditional bound t_{m+1} caps the error at < 12% of ops and
  RAM, so no conclusion moves if the recurrence broke above m = 9 (no
  mechanism visible for it to).
- The 40 ns/slot anchor is another engine's measured constant on the same
  box class; this kernel's true constant is plausibly smaller (2-bit adds vs
  40 B coefficient moves), not larger — direction stated, magnitude unpriced.
- q=3 sibling state counts (SPIN-3): growth (1+√3)/row asserted from the
  same derivation shape, not yet computed exactly; desk row.
- Whether the dalby B1 calibration run completed (L6's and the adversaries'
  standing gap) — unexamined here; it would sharpen the 40 ns anchor only.

## Artifacts

- `experiments/tristruct/r3_spin_counts.py` + `.log` — state counts (brute vs
  recurrence), reachability, window census + Pell recurrence + unconditional
  bound, whole-column pair counts, cost model arithmetic
- `experiments/tristruct/r3_spin_pipeline.py` + `.log` — end-to-end desk
  pipeline: Z vs brute subsets, 28/28 cells vs self-grown animals, exact
  N_H spot checks, RED mutant battery (12/12/4 flips), banked post-hoc
  comparison; the log's first run banks the transposed design's mechanical
  failure at (4,3), the catch behind §2
