# Motley — the plan for rungs Half Measure, Confetti, Ticker Tape

**Motley** is the engine formerly called B1: the colour-symmetrized spin
transfer matrix with clash-zeroing (`results/cutcount_b1/`). It counts by
painting every subset in motley colours and never once deciding whether
anything is connected; the answer is read off a coefficient at the end. The
three rungs this plan builds, in order:

| rung | what | factor |
|---|---|---|
| **Half Measure** | `I256` -> wrapping `u128` — half the coefficient width | x1.9 |
| **Confetti** | payload shredded into 4 x 31-bit residues + CRT | x4 over Half Measure |
| **Ticker Tape** | finer shreds: 8 x 16-bit residues | x2 over Confetti |

Background and the full seven-rung ladder: `docs/b1-closure-plan.md`. This
plan implements only the three rungs that carry heights, plus the two small
changes Ticker Tape cannot do without.

## What it delivers

Each height Motley reaches closes rows at the bottom *and* extends the P_k
lock at the top, so it removes two cells per rung from the top row's residue
(`docs/b1-closure-plan.md` §1, §6).

**Revised 2026-08-14 for the anchor cut** (`results/anchor-cut-map.md`). A
level's constant no longer has to be pinned at the staircase's onset: at depth
`j` it pins from columns `k+1-j`, `k+2-j`, so a sweep to `H_max` closes
`n <= 2 H_max + J - 1` where `J` is the deepest closed defect. With the shipped
`J = 3`, every rung is worth **three more terms** than this plan budgeted, and
the residual band empties one rung earlier than it was ever going to:

| after | Motley reaches | closes outright | was | row 40's residual band |
|---|---|---|---|---|
| today (banked) | H <= 16 | a(n), **n <= 34** | n <= 31 | T(40,20)..T(40,22), 3 cells |
| Half Measure | H <= 17 | **n <= 36** | n <= 33 | 3 cells |
| Confetti | H <= 18 | **n <= 38** | n <= 35 | 3 cells |
| Ticker Tape | H <= 19 | **n <= 40** | n <= 37 | **empty** |

Two consequences for this plan as written. The residual band was Coin Lift's
target; Coin Lift is dead at G2 (`results/coin-lift-g2.md`) and the band closes
here instead, at the last rung. And **the whole point of the ladder is now
Ticker Tape**: rows 35..40 are what the remaining rungs buy, and the first two
rungs buy terms that were already going to be reached.

If `J = 5` is bought (the excess-4 family table at K = 21 — a run, not new
code, `results/anchor-cut-map.md` §"Raising J"), Confetti's H = 18 closes
n <= 40 and **Ticker Tape becomes unnecessary** — which retires the check-split
and the flat arena with it, since those exist only because H = 19 does not fit
without them.

## Step 0 — the provenance re-run (before any new code) — DONE, GREEN

Run 2026-08-14: 16 of 16 rows byte-identical, 640 of 640 triangle cells,
binary stamped `48ac1089` clean with `gate-cutcount-b1` GREEN, 4.7 h of wall
across three streams. **a(n) is now citable for n <= 31.**
`results/motley-step0.md`.

> **Updated 2026-08-14:** those same rows now carry **n <= 34**, verified rather
> than argued — `experiments/depth_swap_anchors.py --rebuild --source motley`
> reads Motley's own `C_1..C_16`, rebuilds rows 17..34, and matches the banked
> triangle on 171 cells with 0 mismatches. Three terms at zero compute.

The banked H <= 16 rows came from source sha `59e90660`, a dirty working copy
matching no committed rev, with a gate battery predating the fail-closed exit
codes (`results/cutcount_b1/PROVENANCE.md`). Until that is redone, **a(30) is
closed but not citable.**

- Build the committed fail-closed engine from `second-source` (rev `48ac108`).
- Re-run H = 1..16 at Nmax = 40, compare to the banked rows byte for byte.
- Cost: 6.7 core-hours, one core, no new code. It is a chore, not a decision.
- Product: a(n) rule-independent for all n <= 31, citable.

This also establishes the reference engine as the **frozen specification**:
434 lines, the 80-line connectivity core (`slot`, `canon`, `gather`,
`shifted`, `successors`) unchanged by every rung below. Each rung must
reproduce the reference byte for byte at every height both can reach.

## What the in-engine self-checks do not check

Measured 2026-08-14 by planting a defect and running the battery: a
**bottom-anchored stencil defect** — `gather` skips the (r+1) diagonal when
r = 0, so components merge wrongly only along the bottom row — passes
`q0_zero` and `q1eval_binomial` **at every height**, and is caught only by the
banked-row comparison (59 of 84 cells mismatch, first at T(2,2)).

That is the expected behaviour on reflection and it should be said out loud:
the q^0 check tests that the count has no constant term, and the A(1) check
evaluates every transition weight at q = 1, where the colour bookkeeping
collapses and connectivity is not consulted at all. **Neither is a
connectivity check.** They catch arithmetic and wiring, not the rule.

The consequence for this plan: at every height with a banked row, the byte
comparison is the real gate and it is decisive. At H = 17 and above there is
no banked C row, so the only rule-level check is the assembled T(n,H) against
`results/triangle.txt` — which is why the H = 17 runner does that comparison
itself and exits nonzero on any mismatch, and why Confetti's held-out prime
matters more than its gate list makes it sound.

(The battery is fail-closed on this defect but inelegant about it: the engine
exits 2, and the gate script raises rather than printing a FAIL line. Nonzero
either way.)

## The height ceiling nobody costed

The engine refused H = 17 outright: three argument checks read `H <= 16`.
Neither this plan, `docs/b1-closure-plan.md`, nor either review caught it —
the launch did, by refusing. It was the height the banked ladder stopped at,
not a property of the algorithm.

The real ceiling is the key packing: H+1 slots of 5 bits in a u128, so
**H <= 24**. Two further limits are far away and are now asserted rather than
assumed, by a `check_height()` the three entry points call:

- **Block ids must fit a 5-bit slot.** The maximum id is the number of
  distinct blocks in the frontier window, bounded by the maximal filled runs
  in H+1 slots plus one for the column-boundary split — vertically adjacent
  filled cells in a column are king-adjacent and share an id, while the two
  slots either side of the boundary are not board neighbours. That is 10 at
  H = 17 and passes 31 only beyond H = 60.
- **`successors()` writes blocks + 2 entries.** The same bound gives <= 12 at
  H = 17 — inside the original buffer — but **13 at H = 18**, so the three
  caller-side buffers went to 32. Measured max fan-out is milder still,
  ceil(H/2) + 1: 3,4,4,5,5,6,6,7,7,8,8 at H = 4..14 by census, and 9 at H = 15
  confirming the formula.

The connectivity core is untouched — `slot`, `canon`, `gather`, `shifted`,
`successors` are byte-identical and only the callers' buffers grew. Commit
`4df3fec`, gate GREEN, C_13 still byte-identical after the change.

**Carry this into Confetti and Ticker Tape**: H = 18 would have overflowed the
original 12-entry buffer by one, silently, on the stack. The rung that first
needed it was two rungs away from the one that found it.

## Rung 1 — Half Measure

**Change.** `I256` becomes a wrapping `u128`. One type, one bound check.

**Why it is exact.** C_H(40) is 1.42e32 at H = 16 (log2 = 106.8) and its
per-height ratio is falling (1.44, 1.36 at H = 15, 16), so C_19(40) projects
to ~2^109 — inside a wrapping u128, by the same ring-hom argument the I256
already relies on. The A(1) self-check compares two values computed in the
*same* wrapping ring, so it stays valid at any width even though its true
value C(861,40) is ~2^229.

**Measured 2026-08-14** (commit `b9d725b`, gympie, against the reference
binary built from `8748d78` on the same box with the same flags): rows
byte-identical to the reference *and* to the banked rows at H = 12 and H = 13;
peak RSS 875 -> 451 MB and 2,478 -> 1,274 MB, a payload factor of **0.514** —
the x1.9 the ladder budgets, now measured rather than counted off the struct
width; wall 42.3 -> 26.9 s and 150.2 -> 102.8 s, **x1.57 and x1.46**, which is
a bonus the RAM ladder never spent. The diff is 21 lines of payload type and
helpers; the 80-line connectivity core and the DP body are untouched.

**Guard.** Fail-closed per height: assert the reconstructed C_H(n) < 2^127
before writing a row. If a future height violates it, the run stops rather
than wrapping silently.

**Run.** H = 17, Nmax = 40, one core. Against the measured ladder (RSS
x2.984/height, wall x3.209/height) and the measured payload factor: **91 GB
peak**, not the 100 GB budgeted before the factor was measured, and ~7-10 h
rather than ~15 h. The +-20% band the census-ratio extrapolation carries puts
the peak at **73-109 GB against dalby's 122 GB available** — the bad end of
the band now fits with 13 GB to spare, which is what makes it right to launch
this without first pulling the check-split (rung B) forward.

The row has an external oracle: `results/triangle.txt` carries the
incumbent's T(n,17) for every n <= 40, so the product and its check arrive
together. Runner `scripts/dalby_motley_h17.sh` does the T assembly and the
comparison, fail-closed.

**Product.** a(n) closed for n <= 36 (was n <= 33 before the anchor cut);
T(n,17) for all n <= 40 banked; and the first *measured* wall, RSS and census
ratio above H = 16, which every projection below currently rests on.

**Status**: launched 2026-08-14 06:32 EDT, binary `4df3fec9` clean, gate
GREEN. Byte-for-byte oracle passed at **H = 12, 13, 14, 15 and 16** — every
height the reference can also reach. Measured at H = 16: peak RSS 32.06 GB
against the reference's 62.29 (**x0.5147**), wall 12,231 s against 17,047
(**x1.394**, both under partial co-residency).

## Rung 2 — Confetti

**Change.** Payload width becomes a template parameter; a CRT driver runs the
passes and reconstructs. Confetti is the u32 instantiation: **4 x 31-bit
primes**, since final values < 2^112 and 4 x 31 = 124 bits, **plus one extra
prime run as a held-out RED** — reconstruct from four, predict the fifth,
compare.

**Reuse.** This is a port, not a design. `cpp/tma/sweep8_modp.h` already does
CRT over 2-3 primes for the incumbent, `cpp/gf_modp.cpp` (217 lines) and
`cpp/tma_modp_test.cpp` exist, and `results/crt-counter-shaping.md` settled the
prime shape (u32 with the 31-bit interleave) as a banked decision. **Motley's
own `--modp` mode is already in committed source** (`run_height_modp`, on
`second-source` since `7b13137`) — the round-3 premise that "nobody has
authored a residue-payload variant" was already stale. It carries two streams,
not three: it has the q0_zero check but **not** the A(1)/binomial check, which
the gate list below must say out loud, because the held-out prime and the
banked-row reproduction are then carrying that weight alone.

**Gate battery, per width, before any production column** (from
`results/triangle-r3-ladder-gate.md` §4, unchanged):

- GREEN: [q^1] against brute-force enumeration at (H,W) in {(2,4), (3,3),
  (3,4), (4,3), (5,3), (6,2)}, every n, every prime.
- GREEN: reproduce banked rows C_1..C_16 byte for byte at Nmax = 40.
- GREEN: the held-out prime predicts correctly.
- RED: a planted NW-stencil drop must fail the battery; the script exits
  nonzero unless every GREEN passes *and* every RED fails.
- Receipt naming the binary's sha256. **This does not exist yet**:
  `scripts/check_receipts.sh` is the docs-claims scanner, and nothing today
  makes a production runner refuse to start without a receipt. Small glue
  script, and it is Confetti's to write — Step 0 and Half Measure carry their
  provenance in the obs stamp (clean `GIT_REV`, no `-dirty`) and in the gate
  run recorded beside the launch.

**Run.** H = 18, Nmax = 40. **91 GB peak**; 5 passes, sequential (they cannot
be co-resident), ~60-120 h total depending on how much the narrow inner loop
buys back (a 4-limb `iaddmul` becomes one multiply-add; unmeasured, and Half
Measure's run is where it first gets measured).

**Product.** a(n) closed for n <= 38 (was n <= 35). With `J = 5` bought, this
rung closes n <= 40 and the plan ends here.

## Rung 3 — Ticker Tape

**Change.** The same driver at u16: **8 x 16-bit primes** (8 x 15.99 = 128
bits) plus one held out as RED. The width is a parameter; this rung is a
prime table and a gate re-run.

**Two changes it cannot do without**, because H = 19 does not fit otherwise:

- **Split the A(1) check into its own pass** (ST 3 -> 2). Peak drops a third,
  the check is preserved exactly, total wall rises by half. Without it:
  135 GB. Hours of work.
- **Flat arena with an open-addressed index.** The measured container overhead
  is ~270 B/window — 3% of today's footprint but 45% of a u16 payload. Replace
  `unordered_map<u128,u32>` plus a heap-allocated `vector` per state with an
  open-addressed key table and one contiguous slab, taking it to ~57 B.
  Without it: 135 GB. A day, and it wants its own differential test against
  `std::unordered_map` at small H, exhaustively.

**Run.** H = 19, Nmax = 40. **87 GB peak**; 9 passes, sequential.

**Wall is the binding constraint here, not RAM.** At today's arithmetic a
single H = 19 pass is ~150 h on one core; nine of them is 2-8 weeks depending
on the residue speedup. Motley is single-threaded, so this occupies one core
of dalby's 80 for the duration. Sharding the state space by key hash across
threads is the obvious fix and is **out of scope** — it is the change that
costs auditability, and it is not needed for any height in this plan.

**Product.** a(n) closed for n <= 40 (was n <= 37 with three cells left in row
40); row 40's residual band **empty**. This is the rung the ladder exists for,
and the only one whose terms nothing else reaches.

## Risks, and what retires each

| risk | retired by |
|---|---|
| census-ratio extrapolation carries H = 18, 19 | Half Measure's measured H = 17 windows, then Confetti's H = 18 |
| ~57 B arena constant is a design target, not a measurement | measure at H = 18 before Ticker Tape commits |
| residue speedup unmeasured; Ticker Tape's wall could be 8 weeks | measured on Confetti's first pass |
| CRT reconstruction wrong | held-out prime, per height, fail-closed |
| the arena is hand-rolled — the one place on this plan where a bug can hide | exhaustive differential test vs `unordered_map` at H <= 10 |

## What this plan deliberately does not do

- No H = 20 or 21. Those need the remaining rungs (u8 residues, chunked
  release) and H = 21 does not fit at any width — the keys alone are 135 GB.
  **Since the anchor cut, nothing asks for them**: H = 19 closes row 40, and
  `T(40,21)` — the cell the closure plan built the whole H = 20/21 argument
  around — rebuilds from columns 18 and 19.
- No parallel frontier, no spill, no dense ranking.
- No change to the 80-line connectivity core, at any rung.
