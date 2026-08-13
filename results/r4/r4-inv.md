# r4-inv — INV-8 spin parity at H=20..21: buildable, mispriced, and gateable at production scale

Round 4 scout, 2026-08-12, gympie, no compute run (desk arithmetic only, by
hand and checked against banked logs). Governed by `docs/triangle-round4.md`.

**Verdict in one line: INV-8 is buildable and was already specified — round 3's
wave-5 file `results/triangle-r3-spin.md` did it, corrected its own geometry,
and filed job SPIN-JOB-1 — but the number my brief and the synthesis ledger
carry (~0.3 GiB) is stale by one wave and wrong by a factor of ~30; the true
peak is ~9.4 GiB and ~22.6 thread-days across four runs. The lane's new content
is therefore not the build but the gate: the recovered B1 rows let the engine be
validated on 640 production-scale cells before anything at m=18..21 launches, at
~0.9% of the production wall, and that gate simultaneously measures the two
constants the pricing has never measured. It escapes the two-horn obstruction
completely — it is escape route 1 of that obstruction, not a new attempt at the
family that failed.**

---

## 0. The premise correction, first, because everything downstream moved

My brief says INV-8 "reaches those two cells at roughly 0.3 GiB on a single box"
and that "nobody has ever built it". Both statements trace to the same source
and both are superseded:

| where | says | written |
|---|---|---|
| `results/triangle-r3-queue.md` row INV-8 | 54,608,393 states at "cut 20", ~0.3 GB/buffer, single box | wave 4 |
| `results/triangle-r3-involution.md` §4 (INV-4 appendix) | same, "64x less" | wave 4 |
| `results/triangle-r3-synthesis.md` ranked ledger line 29 + item 3 | "~0.3 GiB, single box", "repriced 64x" | 20:26 |
| **`results/triangle-r3-spin.md`** | **premise false; ~10 GiB, 22.6 thread-days, four runs m=18..21** | **21:18** |

The spin file postdates the synthesis by 52 minutes and postdates the last write
to the round-3 queue (21:09) by 9. Its five queue rows SPIN-1..5 are *not* in
`results/triangle-r3-queue.md` — `grep -n "^| SPIN-"` returns nothing — so
round 4's queue, seeded from the round-3 queue's open rows, never saw them, and
the brief that dispatched me inherited the pre-correction pricing. All three
files above are untracked working-tree state; none of this is committed.

**The correction itself** (spin file §2, and I accept it): the dispatched
premise was that H=21 forces width W ≤ n−H+1 = 20, so a strip of height 20
suffices. That is the *polyomino* bound; king animals violate it because a
diagonal step advances both coordinates. Minimal counterexample {(0,0),(1,1),
(2,0)}: n=3, H=2, W=3 > 2. At n=40, H=21 a zigzag realises W=40. The bound was
caught mechanically before it was caught by eye — the transposed pipeline's
w-stability assertion failed at (n,H)=(4,3) with an excess of 258 ≡ 2 (mod 4),
an odd number of connected classes beyond the claimed bound
(`experiments/tristruct/r3_spin_pipeline.log`, first run). The corrected design
keeps the strip in the H direction and sweeps along width, needing strip heights
m ∈ {18,19,20,21}.

Consequence for the lead: **the synthesis ledger's INV-8 row and item 3 of its
recommendation are both wrong as written**, and so is the sentence in my brief.
The route survives the correction comfortably — it is still the cheapest thing
that reaches these cells by orders of magnitude — but "0.3 GiB" must not be
quoted again.

---

## 1. Buildability verdict

### 1.1 What the spin basis is, precisely enough to implement

Count pairs (S, f) where S is a subset of cells of a w×m box and f: S → {A,B} is
constant on king-components of S. Equivalently: 2-colourings in which any two
king-adjacent occupied cells agree — a purely local constraint. Then

    Z_{w,m}(n)  =  Σ_{S ⊆ box, |S|=n}  2^{c(S)}          (c = king-components)

and since 2^c ≡ 0 (mod 4) for c ≥ 2 and ≡ 2 for c = 1,

    Z_{w,m}(n)  ≡  2 · #{connected S}   (mod 4).

So the connected count mod 2 is read off a residue. Nothing in the DP decides
connectivity: two same-coloured runs separated by a gap are never asserted joined
or disjoint, nothing is united, nothing dies for stranding, and there is no
completion predicate.

The engine, as specified in the spin file §3 and unchanged by me:

- **Strip** of height m rows; sweep along the width, 41 columns (n ≤ 40).
- **State**: one symbol per row from {E, A, B}; validity = every maximal vertical
  run of occupied cells is monochromatic (vertically adjacent occupied cells are
  king-adjacent). Cell-at-a-time (kink) sweep, so the live object is an
  (m+1)-cell mixed window.
- **Transition**: new cell ∈ {E, A, B}; a colour is dropped iff it clashes with an
  occupied N/W/NW/SW neighbour. Area slot shifts by 1 on occupied. Payload is
  mod 4, 41 area slots × 2 bits.
- **Width accounting**: A_m(n) = Z_{n,m}(n) − Z_{n−1,m}(n). Exact A grows with w
  (ever-wider disconnected classes) but is stable mod 4, because classes wider
  than n are necessarily disconnected — verified at every cell n ≤ 7, and the
  w = 41 harvest is the in-run restatement of it.
- **Height exactly H**: N_H(n) = A_H − 2A_{H−1} + A_{H−2}. Hence four runs,
  m ∈ {18,19,20,21}: {18,19,20} → H=20, {19,20,21} → H=21.
- **Result**: T(n,H) ≡ N_H(n)/2 (mod 2), H ∈ {20,21}, all n ≤ 40.

### 1.2 The arithmetic, re-derived here rather than quoted

I re-derived the state counts from the definition by hand and hit the banked
numbers, so the pricing rests on arithmetic that has now been done twice from
two directions.

Row-language generating function, general q colours (this is new — round 3 left
the q ≠ 2 growth ASSERTED). A valid column string is an alternating sequence of
E-blocks and monochromatic runs; with e = x/(1−x) and r = qx/(1−x),

    F(x) = (1+r)(1+e)/(1−er) = (1 − x + qx) / (1 − 2x + (1−q)x²)

so **t_m = 2 t_{m−1} + (q−1) t_{m−2}, growth 1 + √q**. At q = 2 this is
t_m = 2t_{m−1} + t_{m−2}, t_1 = 3, t_2 = 7 — the companion Pell sequence, which
is exactly what `r3_spin_counts.log` brute-forced against at m ≤ 12. Confirmed:
t_18 = 9,369,319; t_19 = 22,619,537; t_20 = 54,608,393; t_21 = 131,836,323;
t_22 = 318,281,039.

The live object is the window census W(m), not t_m; the spin file measured that
W obeys the same recurrence with seeds W(2) = 15, W(3) = 37 (verified at all 8
enumerated points, m ≤ 9) and is unconditionally ≤ t_{m+1}. Chaining that
recurrence by hand from the seeds:

    W(10)=17,631   W(11)=42,565     W(12)=102,761    W(13)=248,087
    W(14)=598,935  W(15)=1,445,957  W(16)=3,490,849  W(17)=8,427,655
    W(18)=20,346,159  W(19)=49,119,973  W(20)=118,586,105  W(21)=286,292,183

The last four match the banked log exactly, so my chain and theirs agree.

Op count: slot-ops(m) = 41 columns × m stages/column × W(m) states × 3 branches
× 41 area slots = **5043 · m · W(m)**. At m = 21 that is
105,903 × 286,292,183 = 3.032 × 10¹³, reproducing the banked figure. Totals:

| m | W(m) | slot-ops | wall at 40 ns |
|---|---|---|---|
| 18 | 20,346,159 | 1.847e12 | 0.86 thread-days |
| 19 | 49,119,973 | 4.707e12 | 2.18 |
| 20 | 118,586,105 | 1.196e13 | 5.54 |
| 21 | 286,292,183 | 3.032e13 | 14.03 |
| **total** | | **4.883e13** | **22.6 thread-days** |

**State space at the two target heights, stated as the brief asks:** the live
state space is the (m+1)-cell window, 118,586,105 states for the H=20-critical
run and 286,292,183 for the H=21-critical run; the whole-column state space is
t_21 = 131,836,323 / t_22 = 318,281,039. The naive 3^m figures are
3^20 = 3.49e9 and 3^21 = 1.05e10, so the monochromatic-run constraint buys ×29
and ×33 — *not* ×64, which was the number obtained by comparing the corrected
constraint against the uncorrected geometry.

### 1.3 RAM: the ~0.3 GiB figure, and where it went

    ~0.3 GiB   the brief's figure. Provenance: 54,608,393 states ("cut 20")
               x ~5-6 B. Dead — wrong geometry AND a bytes/state that no
               design document supports.
    10.1 GB    spin file: 286,292,183 x 38 B (u64 key 8 B + 11 B mod-4
               payload, x2 buffers) = 1.088e10 B = 10.1 GB = 9.43 GiB.
               (The file says "GiB"; the arithmetic is GB. Minor.)
     7.0 GB    with dense ranking instead of a keyed buffer (below)
               = 6.52 GiB.

The spin file notes that dense Pell ranking exists — the state language is
regular, unrank is O(m) table lookups — but prices a sorted-array keyed buffer
as the baseline. **I would make dense ranking a requirement, not an option**, for
two reasons. First it deletes the 8-byte key (index *is* the state), taking
bytes/state from 38 to 22 and peak from 9.43 to 6.52 GiB even if you rank over
the whole t_{m+1} language and waste the 10% that W/t = 0.8995 represents:
318,281,039 × 22 = 7.00e9 B. Second, and more important, **the 40 ns/slot anchor
is only defensible for a directly-addressed array.** A sorted-array double buffer
at 286M entries × 21 stages × 41 columns implies a merge or sort per stage whose
cost is nowhere in the op model; the anchor engine (B1) was hash-based and paid
that cost inside its 40 ns, but nothing licenses assuming the same constant for a
design whose op model counts only slot arithmetic. Dense ranking makes the model
and the constant consistent. All valid states are reachable from the empty column
(measured, m ≤ 7), so a dense array wastes nothing beyond the W/t gap.

### 1.4 Where connectivity is decided, and which entry-ticket levels clear

**Nowhere.** That is the whole point of the route and I believe it.

*Level 1 — connectivity defined somewhere the engines' hypothesised misconception
cannot reproduce: CLEARS.* The only thing shared with the production kink engine
is the king-adjacency stencil geometry (the r−1, r, r+1 clash pattern) and the
fact of frontier separation. There is no label partition, no union, no
stranded-component death, no closability test. A misconception about *what
connectivity means for the count* has no expression in this DP; it has only one
narrow carrier, the stencil itself, which the RED battery attacks directly.

*Level 2 — failure mode disjoint from union-find-over-a-frontier's: CLEARS for the
connectivity layer.* Wrong-union, wrong-death, wrong-completion have no carrier
here; clash-stencil error, mod-4 bookkeeping and width differencing have no
carrier there.

*The caveat round 3 states only in passing, and I want it in bold:* **the height
accounting is common-mode.** N_H = A_H − 2A_{H−1} + A_{H−2} is formally the same
second difference that B1 uses (T = C_H − 2C_{H−1} + C_{H−2}) and that the strip
engine uses. It is not shared code, but it is one formula and one semantics
("extent at most H" → "exactly H"), and a misconception in it would hit all three
routes identically. What mitigates it is that the layer is separately two-sourced
in the strip engine's own accounting, not anything the spin route adds. Same for
the area-slot bookkeeping. So the honest ticket is: **levels 1 and 2 for the
connectivity rule; level 0 for the extent accounting, mitigated elsewhere.**

### 1.5 What the pricing still rests on that nobody has measured

Three things, and the gate job in §4 measures the first two:

1. **Bytes/state of a real binary.** 38 B (or my 22 B) is a model. No RSS has
   been read for this DP at any scale. Headroom is 8–13× on either box, so this
   gates sizing, not feasibility — unlike L6-1 at H=20, where the same
   unmeasured constant is the whole go/no-go.
2. **The 40 ns/slot constant.** MEASURED, but for a *different engine* (B1 C++
   at H=14 on dalby: 34.2 s/column over 20.8e6 transitions × 41 slots) moving
   40-byte exact coefficients through a hash. This kernel does a 2-bit mod-4 add
   into a directly-addressed array. The direction is favourable and the magnitude
   is unpriced; a 3× swing in either direction changes 22.6 thread-days to 7.5 or
   68 and changes nothing about feasibility.
3. **Sharding efficiency**, asserted at 50%. Moves wall, not feasibility.

The one thing I would add to the NOT ESTABLISHED list that round 3 did not:
**the window census W(m) beyond m = 9 rests on an 8-point recurrence fit.** The
spin file is right that the unconditional bound t_{m+1} caps the error at under
12%, so nothing moves — but the recurrence itself is asserted, not proved, and
the derivation in §1.2 above proves it only for the *column* language, not the
kink window. Proving W(m) = 2W(m−1) + W(m−2) from the window's transfer structure
is half a page of desk work and would retire the last extrapolation in the cost
model.

---

## 2. The forced-parity question, head on

The forced-parity lemma (`results/triangle-r3-synthesis.md`, derived in
`results/triangle-r3-involution.md`) is that any correct method producing a
parity for T(n,H) produces *the same bit*, necessarily. So a match proves nothing
about the mathematics; it can only be evidence about the *implementations*. All
the value therefore lives in whether the rule classes that computed the bit fail
in disjoint ways. Three things a referee will actually press on:

**It clears the bar against the production engines, and this is the strong
claim.** The kink/TM engines reach T(40,20) and T(40,21) by maintaining a
connectivity partition across a frontier, uniting labels, killing stranded
components and testing closability. The spin DP maintains a colour string and
adds mod 4. There is no shared state object, no shared invariant, and no shared
bug that I can construct: to make both engines wrong in the same direction you
need an error in the king-adjacency stencil *geometry* (shared, and the only
shared thing) or in the height-extent differencing (shared in form, §1.4). Those
two are exactly what the RED battery in §3 is aimed at, which is the correct
design response.

**It does not clear the bar against B1, and nobody should claim it does.** B1
computes A_n(q) = Σ_S q^{c(S)} in Z[q]/(q²) and reads [q¹]. Spin computes the
same polynomial A_n(q) evaluated at q = 2 in Z/4 and reads the residue. **These
are two extractions from one identity.** The state bases differ genuinely
(colour-coincidence partitions vs colour strings) and the arithmetic differs
(polynomial truncation vs 2-adic evaluation), so implementation failures are
largely disjoint — but if the cancellation identity itself were wrong, both die
together. This matters less than it sounds for the prize, because B1 cannot
afford H=20 or 21 and so is not a comparand there; it matters a lot for §3,
because the gate oracle *is* B1, and I say so there.

**Would a referee agree it is independent?** For the two prize cells, yes, with
the caveat named: the referee is being offered a second rule class against the
kink engine, and the parity agreement is evidence that the kink engine's
connectivity bookkeeping did not corrupt those two cells in a parity-changing
way. They should not be told it is evidence that Σ q^{c(S)} counts what we say it
counts — that is a mathematical claim, provable at desk (and verified at n ≤ 7
against self-grown animals with an independent union-find), not something the run
establishes.

---

## 3. Gate battery on the recovered oracle

This is the lane's substantive new content. Round 3's battery is value-level and
well-designed but **tops out at 28 cells at n ≤ 7**. `results/cutcount_b1/rows/`
gives exact T(n,H) for H = 1..16 at every n ≤ 40 (40 lines per file, 16 files,
recomputed at recovery time and matching `results/triangle.txt` to all 31 digits
at the two cells checked, with the run's own `match=640 mismatch=0`). That is a
**640-cell production-scale oracle**, and the spin engine can be run against all
of it for pocket change.

### 3.1 The cells, and what they cost

Extending the op formula 5043·m·W(m) downward with the hand-chained W values:

| m | W(m) | slot-ops | wall at 40 ns |
|---|---|---|---|
| 12 | 102,761 | 6.22e9 | 4.1 min |
| 13 | 248,087 | 1.63e10 | 10.8 min |
| 14 | 598,935 | 4.23e10 | 28.2 min |
| 15 | 1,445,957 | 1.09e11 | 1.22 h |
| 16 | 3,490,849 | 2.82e11 | 3.13 h |
| m ≤ 11 | | < 4e9 | < 3 min |
| **m = 1..16** | | **≈ 4.6e11** | **≈ 5.1 thread-hours** |

**The full 640-cell gate costs ~0.94% of the production wall** and 85 MB of RAM
at m = 16 under dense ranking (t_17 = 3,880,899 × 22 B). Every cell of it is a
value both the kink engine and B1 already agree on, so a pass cannot be explained
away as agreement with a possibly-corrupt incumbent — that is precisely the
increment the recovered rows buy over gating against `triangle.txt` alone, and
it is a modest increment, not a transformation, because the two sources already
matched.

Comparison is at the T level on both sides (both routes second-difference their
own row sums). Direct comparison of raw C_H(n) against A_m(n) is not available:
they are different quantities, B1's coefficient extraction versus spin's
evaluation.

### 3.2 REDs

Carried from round 3, measured at desk (`r3_spin_pipeline.log`), all value-level
against self-grown animals with an independent union-find:

1. **drop-NW** mutant: 12 of 28 cells wrong at n ≤ 7, first at (2,2).
2. **drop-SW** mutant: 12 of 28, same first cells.
3. **rook** mutant (drop both diagonals): only 4 of 28, first at (4,3).

**The mutant the structural self-checks provably cannot see is #3, and here is
the argument, not the hope.** Round 3 measured two blindnesses: (a) state
censuses cannot see symmetric stencil errors — the rook and king closures reach
*identical state sets* at every measured H ≤ 8, so any check that counts or
hashes states is blind by construction; (b) the DP's own structural identities
pass while the answer is wrong — B1's [q⁰] = 0 and A_n(1) = binomial both pass a
dropped-NW stencil. Add the two in-run checks this engine would carry:
w-stability mod 4 asserts that classes wider than n are disconnected, which is
just as true for rook-connectivity as for king-connectivity, so it is blind to a
rook mutant; and the no-clash total is a count of colourings of the mutant's own
language, so it is definitionally blind. **Every structural self-check available
to this engine is blind to the rook mutant. Only value-level comparison against
the oracle catches it, and at n ≤ 7 it catches it in just 4 cells of 28.** That
is the argument for running the mutants at production scale: the rook mutant's
footprint over 640 cells is unknown and should be *measured by the gate job*, not
assumed to grow.

Two REDs I am adding, both aimed at failures that n ≤ 7 structurally cannot
express:

4. **Area-slot boundary mutant**: build with the payload array sized 40 instead
   of 41, or with the area shift saturating at 40. Invisible at n ≤ 7 — the slots
   are never approached — and it corrupts exactly the prize cells. Must be caught
   at n = 40 by the oracle and by nothing else.
5. **Width-harvest off-by-one**: harvest at w = 40 without the w = 41 difference
   (i.e. drop the width-translation fix). At small n the wide disconnected classes
   cancel mod 4 and it may pass; whether it does is exactly what the gate should
   measure.

Fail-closed on the REDs themselves: **a mutant whose measured flip set over the
640 cells is empty is a gate-design failure and blocks dispatch**, not a passing
grade. Each mutant's flip set is recorded as a fixture; a later build that
reproduces the flip sets *inexactly* — agreeing with truth where it should differ
— is a build failure.

6. **Payload fault injection** (round 3's #2): flip one mod-4 slot mid-sweep at
   small m; the harvested residue must change.

### 3.3 Blind harvest — a referee-facing requirement

`r3_spin_pipeline.log` line 24–25 records the banked answers: T(40,20) mod 2 = 1
and T(40,21) mod 2 = 1, both `real-sweep`. **The target values are known in
advance to whoever debugs the engine.** That is a genuine confirmation-bias
exposure and it is cheap to close: the production run writes its full output file
(both columns, all n ≤ 40) and its sha256 to the log *before* any comparison is
made, and the comparison is a separate scripted step over the committed file. No
interactive peeking at n = 40 during a debugging session. Pre-registration is
already effectively done by the values appearing in this file.

### 3.4 Fail-closed exit contract

    GATE 0  build reproduces the 28-cell n<=7 desk table exactly       -> else exit 70
    GATE 1  each mutant reproduces its recorded flip set exactly;
            any mutant with an empty flip set over the oracle          -> exit 71 (design failure)
    GATE 2  payload fault injection surfaces                           -> else exit 72
    GATE 3  640-cell oracle comparison, H=1..16, n<=40, mod 2,
            zero mismatches                                            -> else exit 73
    GATE 4  RSS/state and ns/slot recorded at m=14,15,16 and written
            to the log; absence of either measurement                  -> exit 74
    GATE 5  one m=16 pass at production thread count, identical
            output to the single-threaded pass (sharding race check)   -> else exit 75
    GATE 6  in-run: w-stability mod 4 at every harvest; labelled in
            the log as a bookkeeping check, never as correctness       -> else exit 76

    Gates 0-5 all pass -> production m=18..21 may be dispatched. Any nonzero
    exit blocks dispatch; no override path, no "known-benign" list.
    Production runs additionally reproduce T(n,20) and T(n,21) mod 2 for all
    n <= 39 against the banked triangle BEFORE the n=40 residues are read; a
    mismatch anywhere escalates immediately as a bug certificate against one
    of the two rule classes (forced-parity lemma: two correct routes cannot
    disagree).

Localizer caveat, carried from round 3 and still true: m = 19 and m = 20 feed
both target columns, so a corruption there touches both; the independent m = 18
and m = 21 runs plus per-column checkpoint hashes are what separate them.

---

## 4. Build plan and the first dispatchable increment

**Increment 1 (this job request): write the engine, gate it on the oracle,
measure the two constants.** ~5 thread-hours. Nothing at m ≥ 17 runs until it
passes.
**Increment 2:** m = 18 and m = 19 production (3.0 thread-days combined), which
completes nothing on its own but re-prices the remaining wall from a measured
constant for *this* kernel.
**Increment 3:** m = 20, m = 21 (19.6 thread-days), harvest, blind comparison.

    job id:            R4-SPIN-JOB-0  (gate + calibration; precedes SPIN-JOB-1)
    measures:          (a) T(n,H) mod 2 for all H = 1..16, n <= 40 from the
                       spin engine, compared against results/cutcount_b1/rows/
                       (640 cells, exact, two-sourced);
                       (b) RSS per state at m = 14,15,16 -> retires the 38 B
                       (or 22 B) model;
                       (c) ns per slot-op for THIS kernel -> retires the
                       borrowed 40 ns B1 anchor;
                       (d) the flip set of each stencil mutant over 640 cells.
    decides:           whether SPIN-JOB-1 (m = 18..21, the H=20/21 parities)
                       is dispatched at all, and at what true wall and RAM.
                       A gate failure kills the route before 22.6 thread-days
                       are spent; a pass converts every EXTRAPOLATED number in
                       this file to MEASURED.
    command:           build/r4_spin_engine --m 1..16 --cols 41 --nmax 40
                       --mod 4 --dense-rank --oracle results/cutcount_b1/rows
                       --mutant {none,drop-nw,drop-sw,rook,slot40,noharvestdiff}
                       --report-rss --out <file>
    script:            experiments/tristruct/r4_spin_engine.cpp — NOT YET
                       WRITTEN. Ported from the validated executable spec
                       experiments/tristruct/r3_spin_pipeline.py (28/28 cells,
                       exact N_H spot checks to N_4(6) = 821,380, RED battery).
                       C++ per project practice; Python is the reference only.
    wall estimate:     ~5.1 thread-hours for the clean m = 1..16 sweep
                       (EXTRAPOLATED: op count 4.6e11 EXACT under the 8-point
                       window recurrence, x the 40 ns/slot MEASURED-elsewhere
                       B1 anchor). Mutant passes: 5 more sweeps, but only to
                       m = 16 and they can stop at the first flip, so budget
                       2x total -> ~10-12 thread-hours ASSERTED. Trivially
                       parallel across m; ~1 h at 16 cores.
    RAM estimate:      85 MB peak at m = 16 (t_17 = 3,880,899 x 22 B dense-
                       ranked, MODELED) or 133 MB keyed. Under 1 GB on any
                       reading; this job cannot OOM anything.
    disk estimate:     logs and a 640-line output file. KB.
    cores:             1 suffices; use 16 for wall. GATE 5 requires one m = 16
                       pass at the production thread count.
    interruptible:     yes, per m. Losing one m costs at most 3.1 thread-hours.
    box:               **dalby.** Reasons in order: (1) the 40 ns anchor was
                       measured on dalby, so calibrating this kernel there is
                       the only apples-to-apples comparison and (c) above is
                       half the job's value; (2) dalby has the RAM slack for
                       the eventual m = 21 run, and calibration should happen
                       on the box that will run production; (3) it currently
                       carries one single-threaded job, so 16 cores for an
                       hour is free. **Optional, and I recommend it:** repeat
                       the 5-thread-hour clean sweep on ayr. Cross-ISA
                       agreement (ARM vs AMD) on 640 cells for ~5 thread-hours
                       is the cheapest independence evidence available
                       anywhere in this campaign.
    RED control:       gates 0-2 of the exit contract above, run before the
                       oracle sweep; the oracle sweep is itself gate 3.
    closes:            re-prices and gates SPIN-JOB-1; retires the "~0.3 GiB"
                       figure in the synthesis ledger; measures the constant
                       that is currently borrowed.

**On SPIN-JOB-1 itself:** I endorse it as written in `results/triangle-r3-spin.md`
§6, with three amendments — dense ranking made mandatory (§1.3), the blind-harvest
requirement (§3.3), and R4-SPIN-JOB-0 as a hard precondition. Its wall (22.6
thread-days, ~1.5 days at 32 cores) and RAM (9.4 GiB keyed / 6.5 GiB dense) fit
either box with 8-13x headroom. dalby for the same reasons.

---

## 5. What one bit per cell is worth

Written for the skeptical reader, and deliberately flat.

H=20 is 4.1582% of a(40) and H=21 is 2.8431%, together **7.00%** (quoted from
`results/triangle-r3-spin.md`; both cells `real-sweep` provenance). T(40,20) and
T(40,21) are roughly 99-bit and 98-bit numbers. What this route delivers, if it
runs and agrees, is **one bit about each** — the low bit.

**What that rules out.** Any error in the kink engine's connectivity bookkeeping
at those two cells that changes the parity. For an error that perturbs the value
in a way uncorrelated with parity, that is half of them at each cell, so the two
cells together are caught with probability 3/4. Stated as a bound rather than a
boast: **agreement moves the probability that these two cells are silently wrong
down by at most a factor of 4.** Additionally, the production runs reproduce
T(n,20) and T(n,21) mod 2 for every n ≤ 39 as a by-product, and the gate job
reproduces 640 cells at H ≤ 16 — those are strong evidence *about the spin engine
and about the H≤16 block*, and they are what makes the two prize bits worth
believing, but they are not additional evidence about the two prize cells.

**What it does not rule out.** Any parity-preserving error at either cell —
including the whole class of errors that miscount by an even number, which is
most systematic errors (a doubled or dropped symmetry class, an off-by-one in a
count of pairs). Anything at all in the other 93% of a(40). Any error in the
summation of the band into a(40). And it says nothing about the *value* of either
cell: after this run, T(40,20) and T(40,21) remain single-sourced at every
modulus above 2.

**The one thing it does that nothing else currently can:** these two cells are
the ones the residue/CRT ladder cannot afford (68.1 GiB sole-tenant at H=20,
215.8 GiB at H=21 — off-RAM on both boxes at the second). After this route runs,
no cell of the band is untouched by a second rule class. That is a coverage
statement about the *band*, and it is the honest headline. Round 3's brief is
explicit that a route ending in one more bit per band cell is a real result and
must not be written up as if it were the count; that instruction applies here
without qualification, and the write-up should lead with "7.00% of a(40) now has
a second-rule-class parity" and never with a number of digits.

**On the two-horn obstruction, since the brief asks whether INV-8 escapes it or
postpones it: it escapes, and it escapes by construction rather than by luck.**
The obstruction says a site-keyed involution on animals must have a key that is
either validity-aware (and therefore drifts under its own move, because
move-validity is connectivity, a global predicate) or validity-blind (and
therefore produces images outside the class). INV-8 is escape route 1 of that
very analysis: toggle something that *cannot* break the constraint. The toggled
datum is a component-constant colouring of an arbitrary subset S, not a cell; the
key is the component structure of S, which the colour toggle leaves untouched; the
image is always a valid (S, f) pair. There is no move-validity predicate anywhere
in it. The DP is the computational form of that involution, and its fixed set —
connected S with the trivial colouring — is what the mod-4 residue reads. Nothing
is postponed.

---

## 6. Queue rows filed

Appended to `results/r4/queue.md`: R4-INV-1 (R4-SPIN-JOB-0, the oracle gate),
R4-INV-2 (q=3 sibling, priced from the 1+√q derivation), R4-INV-3 (q≥4 killed,
filed with its kill), R4-INV-4 (the lost SPIN-1..5 rows). Detail on the two
successor ideas:

**R4-INV-2 — the q = 3 spin sibling, T mod 3 at the corner.** Z(3) = Σ 3^c and
3^c ≡ 0 (mod 9) for c ≥ 2, so Z(3) mod 9 = 3T mod 9 gives **T mod 3**. Different
modulus, different rule class, and it cross-locks the ternary spine
(`results/ternary-spine.md`) and L6-4. Pricing from §1.2's growth law: q = 3 has
growth 1 + √3 = 2.732 against q = 2's 2.414, so at the same m the state count
scales by 1.1317^m, and branches go from 3 to 4. At m = 20: ×14.4 states →
~1.7e9 window states → **~65 GiB** at 38 B/state (marginal on ayr, comfortable on
dalby) and ~150 thread-days. At m = 21: ×16.3 → ~4.7e9 states → **~166 GiB**,
off-RAM on both boxes. So **the q = 3 sibling reaches H = 20 only, at roughly 7×
the cost of the entire q = 2 job, and cannot reach H = 21.** Real but expensive;
file it, do not do it before the q = 2 route has run. All figures EXTRAPOLATED
from the derived growth rate, not from an exact q = 3 census — computing that
census is minutes of desk work and is the row's first step.

**R4-INV-3 — q = 4 for T mod 4, killed here.** Z(4) = Σ 4^c, 4^c ≡ 0 (mod 16) for
c ≥ 2, so Z(4) mod 16 = 4T mod 16 gives T mod 4 — the obvious way to get a second
bit. Growth 1 + √4 = 3 exactly, so states scale by (3/2.414)^m = 1.2427^m; at
m = 21 that is **×121** → ~3.5e10 window states → **~1.2 TiB** and ~7.5
thread-years. Dead on RAM and on wall, on any box, by a wide margin. The general
statement, which is the useful part: **the q-colour spin basis buys T mod q at
state-space growth (1+√q)^m, so each extra modulus costs
((1+√q)/(1+√2))^m ≈ 1.24^m for q = 4 — the modulus ladder is exponentially
priced in m and terminates immediately at the band's top.** One bit at H = 20..21
is not a first step toward two.

---

## NOT ESTABLISHED

- **Everything in §1.2's cost table is desk arithmetic over a state census; no
  spin engine has ever been run at any scale in any language other than the
  round-3 Python pipeline at n ≤ 7.** The 22.6 thread-days and the 5.1
  thread-hours are op counts times a borrowed constant.
- Bytes/state (38 B keyed, 22 B dense-ranked): MODELED. No RSS at any scale.
- 40 ns/slot: MEASURED for B1 on dalby, ASSERTED as transferable here. Direction
  favourable, magnitude unpriced.
- Sharding efficiency 50%: ASSERTED.
- W(m) = 2W(m−1) + W(m−2) for the kink window: verified at 8 points (m ≤ 9),
  extrapolated to m = 21. The unconditional bound W ≤ t_{m+1} caps the error at
  under 12%. My §1.2 derivation proves the recurrence for the *column* language
  only; the window case is not proved here.
- The rook mutant's flip set over the 640-cell oracle: unknown. Measured only at
  n ≤ 7 (4 of 28 cells). REDs 4 and 5 in §3.2 have no measured flip set at all —
  they are proposed, and GATE 1 fails closed if either turns out to be invisible.
- q = 3 and q = 4 state counts (§6): EXTRAPOLATED from the derived growth rate
  1 + √q, not from an exact census at those q.
- I did not re-run `r3_spin_pipeline.py` or `r3_spin_counts.py` (no compute).
  Their logs are read as banked evidence; the state counts and op counts in them
  I re-derived by hand and they agree.
- Whether `results/triangle-r3-spin.md`'s desk pipeline is itself correct beyond
  what its log shows: not audited line by line. I read the log, not the 11.5 KB
  of Python.
- The percentages 4.1582% / 2.8431% are quoted from the spin file, not
  recomputed.
