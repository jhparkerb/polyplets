# r4-gen7 — the engines are instruments, and the campaign has only ever read them

Round 4 generator, 2026-08-13. Governed by `docs/triangle-round4.md`; standing
instruction line 124, never stop making ideas. I ran no compute: every number
below is desk arithmetic in `python3 -c` over values already on disk, or a
citation to a file and line. Read-only `ssh dalby.jhpb.org` once, to see what
exists there now.

Row ids are `R4-G7-01` … `R4-G7-24`. Six are **CLOSED WITH THE KILL** at
filing. Prior art I am writing successors to, not repeats of: `R4-G2-17`
(mutants measured at n≤7), `R4-G2-18` (stencil space is finite), `R4-G2-19`
(the `gather()` index audit), `R4-G2-20` (re-scope JOB-IND-1), `R4-G2-21`
(2-kernel), `R4-G2-22` (differential fuzzer), `R4-G3-12` (one ISA), `R4-G3-13`
(no sanitizer on record), `R4-G5-17` (the comparer is the reporter), `R4-G4*`.

---

## §0 The premise audit, first, because three of my own four premises are false

### R4-G7-00 — CLOSED WITH THE EVIDENCE: the instrument inventory this round is repeating to itself is ahead of what is on disk

My dispatch described four validated instruments. I checked each before
generating against it. **One is real as stated. Three are not.**

| premise as briefed | what is on disk |
|---|---|
| spin swept m=1..16 in 88.6 s, matched 640 cells, 90.7 MB | **TRUE, MEASURED.** dalby, `r4_spin_m16.log`; `compared=640 mismatch=0`, `wall_s=88.6`, `peak_rss_mb=90.7` (`r4-spinproj.md` §0) |
| binaries on two ISAs produce byte-identical output | **NOT ESTABLISHED — never run.** It is step P4 of a *proposed* battery (`r4-spinproj.md` §3.5) and `r4-spinbuild.md:416` calls it "optional and cheap". There is no ayr spin log anywhere. The two sha256s in the record (`578c940c…` output, `f7709903…` dalby binary) are two different objects on one machine |
| a B1 colour DP validated against a literal flood-fill definition | **NOT ESTABLISHED for the C++ binary.** `experiments/tristruct/r4_indoracle_brute.py` exists and has **no `.log`**; JOB-IND-1 is unrun. What was validated against flood fill is `probe_cutcount_dp.py`, the *Python* DP, at H≤4 (`R4-AI1`) |
| a flood-fill brute force reaching n≤10 exactly | **n≤8.** `r4_spin_reference_gympie.log` grower totals are `1, 4, 20, 110, 638, 3832, 23592` — seven terms, n=1..7, plus the n≤8 comparison in §6 |

This is not a complaint about the dispatch. It is the round's own transmission
loss, observed in a fourth place (`r4-adv-ind.md` §8 found it in the
deliverable→summary hop; `r4-adv-cost` R4-AC5 found two "compiled and gated"
claims with no receipt). **What is new here is the shape: every one of the
three errors upgrades a written-but-unrun instrument to a completed one, and
none goes the other way.** A drift with a sign is a bias, not noise.

Cheapest fix, and it is the successor row: a `results/r4/INSTRUMENTS.md` with
one line per instrument — name, what it measures, the log path that proves it
ran, the date. An instrument with no log path is listed as `WRITTEN, UNRUN`.
Ten minutes, and it is the file every subsequent brief should be built from.
Prior at least one further "we have X" in this round is unrun: **0.6**.

---

## §1 Differential testing as a continuous control, not a gate

### R4-G7-01 — FLAGSHIP: the standard demands a measured false-pass rate and the campaign has only ever asserted one. A fault-injection census measures it, for 3 minutes of ayr

`docs/skeptical-reader-standard.md` defines the currency: *bits = log₂ of the
a-priori probability that a wrong count passes the check*. Every bit-count in
this campaign is derived a priori from the modulus — mod 4 gives 2 bits, a
40-cell agreement gives 40 bits under an assumed independent-corruption model.
The standard's own calibration rule says the model must match the hypothesis
class, and nobody has ever measured the class.

The spin engine already carries `--inject m,col,stage,slot` (`r4_spin_engine.cpp:335-337`),
which corrupts one slot at one stage of one column at one height, and exits 72
if the resulting flip set is empty. That is a fault model and a detector in one
binary. **Sweep the injection site and count how often the 640-cell compare
fails to notice.** The output is a *measured* number of the exact kind the
standard asks for: "of N single-slot faults injected anywhere in the
computation, k passed the battery undetected".

Priced from the measured per-m wall table (`r4-spinproj.md` §0), cumulative:

| truncation | one run | 10,000 runs, 1 core | 10,000 runs, 32 cores |
|---|---|---|---|
| m ≤ 10 | 0.580 s | 1.61 core-h | **3.0 min** |
| m ≤ 13 | 5.32 s | 14.8 core-h | **27.7 min** |
| m ≤ 16 (full) | 88.4 s | 246 core-h | 7.7 h |

Ten thousand injections at m≤13 for half an hour of ayr. The campaign has never
run *one*. Entry ticket: this clears neither level — it is not a route, it is
the calibration of the routes. That is the point: it prices what everything
else's agreement is worth. Prior the measured rate is ≥100x better than the
a-priori model (i.e. faults are caught far more often than "one bit per bit"):
**0.7**. Prior it finds a non-empty undetected class: **0.25**, and that 0.25 is
worth the half hour on its own. **Cheapest kill:** if `--inject` is not
site-parameterizable in practice — if most (m,col,stage,slot) tuples are
rejected at argument parse — the census shrinks to whatever it accepts, and one
`--help` read settles it.

### R4-G7-02 — the mutant space is enumerable, so stop choosing three of it

The battery is five named compile-time mutants selected by an enum
(`r4_spin_engine.cpp:324`: `kDropNw, kDropSw, kRook, kSlot40, kNoHarvestDiff`),
of which three are stencil mutants with measured flip counts 12/12/4. Three
chosen mutants dying proves the detector has power. It does not bound the
undetected class, and *bounding the undetected class is the whole reason
mutation testing exists*.

The single-edit space over `gather()` (`cutcount_b1.cpp.59e90660:128-139`) is
small and finite, and I can write it out: 4 `push()` calls that can each be
deleted (4); 4 slot indices that can each be perturbed by ±1 (8); 3 guards
(`r > 0`, `r + 1 < H`, `c > 0`) each admitting off-by-one or negation (~9); the
`ids[]` dedup loop bound (2); in `successors()`, the `nb >= 2` threshold (2),
the `nb == 1` branch (1), the fresh-colour weight `-b` (2), `mx + 1` (2). Call
it **30 single-edit mutants in the stencil and transition layer alone**, and
the same census over the spin engine's three offsets is smaller.

At the full-sweep price that is 30 × 88.4 s = **44 minutes on one core** for a
statement the campaign cannot make today: *no single-edit change to the stencil
or the transition rule survives the 640-cell battery*. Entry ticket: level 1
n/a, level 2 — it is the evidence *for* a level-2 argument, since a level-2
claim names the failure mode the route would exhibit if its rule were wrong,
and this enumerates them. Prior all 30 die: **0.8**. Prior at least one
survives and is *interesting* rather than a compile error: **0.15**.

### R4-G7-03 — minimize every mutant to its smallest witness, and the 640-cell gate becomes a 100-millisecond pre-commit hook

Each mutant that dies, dies first at some smallest (m, n). Bisect for it. The
measured table says the whole m≤8 prefix costs **83 milliseconds**, and the
existing flip records already point that way — the drop-NW witness list starts
at (2,2) and the rook list at (4,3) (`r4_spin_reference_gympie.log` §5).

The product is not a number, it is a **fixture file**: for each mutant, the
minimal cell that catches it. A gate built from those cells runs in the noise
and can therefore run on *every* commit, not on the three occasions somebody
remembered. `r4-adv-ind.md` §3.2 established that the seven gates cover the
exact path while the `--modp` patch lives outside it — a demonstrated hole
exactly where a free gate would sit. Prior the minimal witness set is under 20
cells: **0.7**. Cheapest kill: if any mutant's minimal witness is above m=13,
the fast gate loses that mutant and the hook is partial — still worth having,
smaller claim.

### R4-G7-04 — the deliverable is the *undetectable* list, not the detected one

Stated separately from R4-G7-02 because it is the row that changes what gets
written down. A mutant that survives the whole battery is one of exactly two
things, and both are worth a paragraph in the report:

1. **A redundancy in the rule.** Two stencils that give the same T(n,H) over
   the tested range are a mathematical fact about king animals in a strip, not
   a bug — and a stated one is a much stronger sentence than silence, because
   it tells a referee precisely which part of the adjacency definition the data
   cannot see.
2. **A hole in the oracle.** The comparison range is too small, and now we know
   by how much and in which direction.

Today the campaign cannot distinguish these because it has never had a
surviving mutant to look at. Prior the census produces at least one survivor
of type 1: **0.35** — the `slot40` mutant already shows the design anticipates
non-stencil edits, and symmetric edits (swap two slot reads that are both king
neighbours) are the obvious candidates.

### R4-G7-05 — a RED on the RED: `--expect-flips` has never been tested for false negatives

The engine exits 71 when a mutant produces an empty flip set
(`r4_spin_engine.cpp:1099`) and accepts an `--expect-flips` count. That is a
fail-closed guard on the mutants, and by the project's own standard
(`docs/engineering-standards.md`, and `docs/quality-gates`) a guard is held to
a higher bar than the code it protects. Nothing on disk shows the guard being
made to fire wrongly: run a clean sweep with `--expect-flips 12` and confirm
non-zero exit; run a mutant with `--expect-flips 0` and confirm non-zero exit.
Two runs, 3 minutes. Prior it is uncovered: **0.7**. Prior it is broken:
**0.05**. Filed because it is the cheapest item in this file and because the
guard is what every mutant number in the round rests on.

### R4-G7-06 — CLOSED WITH THE KILL, and the kill has a survivor worth stating: mutation testing beats differential testing on exactly the axis differential testing cannot reach

`R4-G2-22` proposed a standing spin-vs-B1 differential fuzzer and honestly
noted its limit: `r4-adv-ind.md` §2.2 shows spin **is** B1's DP specialised to
q=2, sharing the stencil and the colouring semantics, so the fuzzer tests
implementations and not rules. Correct, and it kills the fuzzer as a *stencil*
control.

The survivor is an asymmetry nobody has written down. **A mutant of engine A
compared against unmutated engine B is not blocked by the shared stencil**,
because the shared component is exactly what is being varied on one side only.
Differential testing of two engines that share a rule measures nothing about
the rule; *mutation* testing of one engine against the other measures the
detection power of the pair against rule error directly — which is what the
12/12/4 numbers already are, and why they are the most valuable numbers in the
gate log. So: keep the mutants, drop the fuzzer, and say why. Prior this
reasoning survives adversarial review: **0.8**.

---

## §2 Engines as search instruments rather than counters

### R4-G7-07 — R4-G2-18's own kill fires, and here is the arithmetic it asked for: 6 of 12, not 12, and the full exhaustion needs a wider window that fits `u128` iff H ≤ 11

`R4-G2-18` proposed enumerating all ~4096 radius-2 stencils and reporting which
are consistent with T(n,H). Its stated kill was "if some offsets are not
expressible as slot reads in the column-major order the space is not 4096". It
is not 4096, and the correction is more useful than the kill.

Processing is column-major, row-increasing. From cell (r,c) the already-
processed cells within radius 2 are: column c rows r−1, r−2 (2); column c−1
rows r−2 … r+2 (5); column c−2 rows r−2 … r+2 (5). **Twelve, so 4096 subsets —
gen2's count of the space is right.** Counting steps backwards in processing
order, those twelve sit at slot indices:

| cell | slot | in today's window (0…H)? |
|---|---|---|
| (r−1, c) | 0 | yes — this is `push(0)` |
| (r−2, c) | 1 | yes |
| (r+2, c−1) | H−3 | yes |
| (r+1, c−1) | H−2 | yes — `push(H-2)` |
| (r,   c−1) | H−1 | yes — `push(H-1)` |
| (r−1, c−1) | H | yes — `push(H)` |
| (r−2, c−1) | H+1 | **no** |
| (r+2 … r−2, c−2) | 2H−3 … 2H+1 | **no** (all five) |

**Six of twelve are expressible, so an exhaustive enumeration on today's
container covers 2⁶ = 64 stencils, not 4096.** The full space needs a window of
2H+2 slots at 5 bits, i.e. 10H+10 bits, which fits `u128` iff **H ≤ 11**
(H=11 → 120 bits; H=12 → 130 bits, over). And that is the good news, because
the incumbent-free oracle is bounded by n, not H (`R4-G2-20`), and it reaches
n≤8 today and n≤12 with R4-G7-22's fix. **H ≤ 11 is inside the oracle's range,
so the 4096-stencil exhaustion is genuinely achievable — on a widened-window
build, at H ≤ 11.** Entry ticket: level 1 — an exhaustion over stencils covers
the case where our *definition* of the neighbourhood is the shared
misconception, which is the only argument in the campaign that does. Prior king
is the unique consistent stencil at n≤10, H≤11: **0.75** (lower than gen2's
0.8: the five column-(c−2) offsets are far from the cell and many will be
consistent-but-vacuous at small n). Prior the widened build is under a day:
**0.6**.

### R4-G7-08 — at m ≤ 10 the injection space is not a sample space, it is enumerable

R4-G7-01 samples 10,000 sites. At m ≤ 10 the site space is
`m × cols × stages × slots` ≈ 10 × 41 × (a few) × (≤11) — low tens of
thousands, at 0.58 s each. **The complete detection map costs the same order as
the sample and is a categorically different object**: not "the measured
false-pass rate is p" but "the set of injection sites the battery cannot see
is exactly S". If S is empty, that sentence needs no statistics at all. Prior S
is empty at m≤10: **0.5**. Prior S, if non-empty, is concentrated at the last
column or the top row: **0.8** — and a structured S is a bug report, not a rate.

### R4-G7-09 — metamorphic testing: every knob that must not change the answer, varied. Ten runs, fifteen minutes, and nobody has done one

Differential testing needs a second engine. Metamorphic testing needs only the
identity *"this parameter must not change the output"*, and the spin engine has
at least six such parameters:

- `--cols` above the minimum (41 vs 45 vs 50): T(n,H) for n ≤ 40 must be
  unchanged. Tests the column-boundary difference `f_W − f_{W−1}`.
- `--nmax` (40 vs 44): all shared cells identical. Tests the n-loop bounds.
- **m-range splitting**: `--m 1..16` versus `--m 1..8` then `--m 9..16`,
  concatenated. Must be identical. Tests every per-m setup path.
- `--dense-rank` on/off, `--verify-rank` on/off: identical output, different
  wall.
- `--threads` (excluded — the atomic path has never passed GATE 5, and
  `r4-spinproj` §5 says do not use it. Note that this *is* the metamorphic test
  that would gate it).

Ten runs of 88.4 s is **fifteen minutes** for a class of test that catches
exactly the defects a second engine cannot: shared-rule-correct,
bookkeeping-wrong. Entry ticket: n/a, it is a control. Prior all pass: **0.85**.
Prior the m-split one is the one that fails, if any does: **0.6** — per-m setup
is the code that runs 16 times in one process and once per process in the
other.

### R4-G7-10 — the rank verification is off in exactly the regime that matters, and the code and its own comment disagree about it

`r4_spin_engine.cpp:676-678`: the auto default is `verify = (m <= 10)`. The
header comment on `verify_language()` at `:296-299` says the odometer walk
"runs unconditionally up to len = 17 (~4e6 strings, well under a second) and on
demand above that via --verify-rank 1". **Those are two different thresholds
for the same guard**, and `r4-spinproj.md` §0 independently
identifies m=10→11 as the break in the timing table and calls **m=11..16 the
production regime**. So: the 640-cell match, the 12/12/4 mutant results at the
larger m, and the whole banked spin record above m=10 were produced with the
rank odometer walk **off**, while a comment asserts it is on to len=17.

Two things follow, and the second is the row. First, the fix is one run:
`--m 11..16 --verify-rank 1`, minutes, and it retires the gap. Second — and
this is what makes it a generator row rather than a bug report — **a comment
and a default that disagree is the exact defect shape this round has been
finding everywhere else** (R4-G7-00's premise drift, `r4-adv-cost` R4-AC5's
receiptless claims). The cheap systematic version: grep every gate and guard in
the round's code for a documented threshold, and check it against the constant.
Hours. Prior at least one more mismatch: **0.5**. Note the *state-count* Pell
check is **not** affected — it sits at `:304-307`, ahead of the
`if (!full) return;`, so it fires at every m unconditionally, and it will fire on the
m=21 run now in flight. That guard is good, and it is the model for the others.

### R4-G7-11 — pre-registered identity search: fit on H ≤ 12, predict H = 13..16, and only then look

`R4-G2-16` established the pre-registration protocol for parity bits;
`R4-G2-21` proposed a 2-kernel search. The successor is to apply the first to
the second, and to fitted forms generally. The 640-cell mod-4 table is on disk
(`spin_m16.txt`, 21,555 bytes). An identity search over it — recurrences in n
at fixed H, recurrences in H at fixed n, automatic-sequence kernels — will
produce candidates, and a candidate fitted on 640 cells and checked on 640
cells is worth nothing, by the standard's own axis 2 (*every banked cell a
blind derivation matches afterwards is a real test; every cell read during
derivation is not*).

So: **fit on H ≤ 12 (400 cells), hold out H = 13..16 (240 cells), commit the
predictions to git, then look.** Survivors then predict H = 17, 18, 19 — which
the B1 ladder is about to compute over weeks and the spin m=21 run is computing
right now. A fitted form that is on the record before either lands is a real
prediction; the same form fitted afterwards is a curve through points. Cost:
hours of laptop work, no compute job. Prior something survives the H=13..16
holdout: **0.3**. Prior a survivor also survives H=17..19: **0.12**. Entry
ticket: level 1 only, and only if the fitted form is later *proved* — an
unproved fit is a consistency check, and the standard ranks it as one.

### R4-G7-12 — CLOSED WITH THE KILL: q is a dial on cost, not on evidence, and the surviving use is cost-model calibration

The tempting reading of `r4-inv`'s growth law 1+√q is that q is a free
parameter to sweep. It is not: `R4-INV-3` closes q=4 (growth exactly 3, ~121x
states at m=21) and `R4-INV-2` prices q=3 at ~7x the entire q=2 job for one
height less reach. Both closures stand on the growth ratio, which is measured.

What survives, and it is small but free: **the growth law makes state count an
exact a-priori prediction at every (q, m), so a q=3 run at small m is a
zero-stakes calibration of the cost model** — 4 or 5 heights, seconds, and it
tests the one extrapolation every cost estimate in this round leans on. Not
evidence about a(40); a check on the arithmetic everyone is quoting. Prior it
agrees: **0.9**. Cost: minutes. Filed so "sweep q" does not get re-pitched as
an evidence route a third time.

### R4-G7-13 — CLOSED WITH THE KILL, and worth filing because it is the idea every reader will have: the "independent connectivity-free colour transfer matrix" *is* the spin engine

I derived this and then killed it, and the derivation is the content.

B1 computes `Z = Σ_S x^|S| q^{c(S)}` and extracts T = [q¹]Z. At integer q, Z
counts maps from cells to {0, 1, …, q} with 0 = empty and *king-adjacent
nonempty cells equal*, because a component may be coloured freely and distinct
components are non-adjacent by definition. That reformulation **never decides
connectivity** — connectedness is a local constraint in the encoding, not an
algorithm — so it clears entry-ticket level 1 outright, and at q=2 it is not
stencil-blind the way B1's q=1 binomial self-check admits it is
(`cutcount_b1.cpp.59e90660:168-170`: "*all-subsets binomial; … no connectivity
involved*"). It looked like the incumbent-free oracle at band heights that
`r4-spinproj` says does not exist.

**It is not new. It is spin.** The valid windows of that colour DP satisfy
`t_m = 2t_{m−1} + (q−1)t_{m−2}` — which is exactly `r4-inv.md` §1.2's derived
growth law — and at q=2 the counts are 7, 17, 41, 99, 239, 577, 1393, 3363,
8119, 19601, …, which are *precisely* the sixteen measured `states` values in
`r4-spinproj.md` §0's table, and precisely what `verify_language()` asserts at
`r4_spin_engine.cpp:300-307` (`die(78, "state_count_not_pell …")`). The spin engine is not a clever basis over some
other object; it is the naive colour DP with a dense ranking of the valid
colour strings.

Three things to bank from the kill. (a) **Spin's independence from B1 is
algorithmic, not semantic, and the level-1 clearance is real but is spin's, not
a new route's** — `r4-adv-ind.md` §2.2 said this and this is an independent
derivation of it from the state counts. (b) `Z_n(2) mod 4 = 2·T(n,H) mod 4` for
n ≥ 1, since only c=1 subsets survive mod 4 — so the q=2 object carries exactly
one bit per cell and no amount of implementation cleverness changes that; this
is the arithmetic behind `R4-G2-24`. (c) The one live residue is R4-G7-23: a
*deliberately naive* reimplementation of the same colour DP is an oracle for
spin's ranking layer, which is where spinproj puts the m>16 risk.

---

## §3 What the byte-identical cross-ISA result would license — once it exists

All of §3 is conditional on R4-G7-00: **the cross-ISA run has not happened.**
These rows are about what to do with it, and two of them change what the run
should be before it is dispatched.

### R4-G7-14 — the 90-second referee artifact, and it is the only artifact in this campaign a referee can actually complete

The round's goal statement asks for verification *a skeptical reviewer would
complete*. Every route on the board is weeks of dalby. This one is not:

- source: `r4_spin_engine.cpp`, 46,084 bytes, single file, no dependencies
- output: `spin_m16.txt`, 21,555 bytes, 640 T-rows, no timestamp or hostname in
  the header (`r4_spin_engine.cpp:965` writes only m-range, cols, nmax, mod,
  dense_rank, mutant, inject)
- cost to the referee: **88.6 s on one core, 90.7 MB**

Publish the source, the output's sha256, and the command. A referee with a C++
compiler reproduces 640 cells of the parity triangle in a minute and a half and
compares one hash. Entry ticket: level 1 cleared (spin's), level 2 argued by
`r4-adv-ind` §2.2 against the kink engines only — and the honest first line is
that it reaches **parity of T(n,H) for H ≤ 16 at n ≤ 40**, i.e. one bit per
cell over the already-confirmed part of the band. Prior jasonp wants this in
the paper: **0.6**. Prior it is the single highest referee-completability item
on the board: **0.8** — because it is the only one whose completion cost is
under an hour. **Cheapest kill:** if the output is not in fact reproducible on
a third machine, the whole row goes; which is R4-G7-16, and it is one job.

### R4-G7-15 — the output header cannot prove same-source, so cross-box identity proves less than it looks

`r4_spin_engine.cpp:965` writes the run parameters into the output header. It
does **not** write the source sha256 or any build identifier. The binary sha256
is reported at `:1083` — but the binaries on two ISAs differ by construction,
so the binary hash is not a control across boxes. Consequence: two boxes
producing byte-identical output is consistent with them having compiled two
*different sources*, and the campaign has already been bitten once by needing a
source hash to name an artifact (`cutcount_b1.cpp.59e90660`).

Fix: `-DSRC_SHA256='"…"'` at compile time, computed by the build rule from the
`.cpp`, printed in the output header. Then byte-identity of the outputs implies
same-source, and the header is self-describing for a referee who finds the file
alone. Minutes of Makefile work, and it must land **before** the cross-ISA run,
not after. Prior it is worth doing: **0.9**. Prior anyone would otherwise
notice before the paper: **0.3**.

### R4-G7-16 — make the second ISA a second *compiler* too; it is free and it removes a strictly larger common mode

`R4-G3-12` correctly names single-ISA codegen as a real common mode and
promotes the ayr repeat to the answer. The improvement is one flag: build ayr's
copy with **clang** while dalby's stays **gcc**. Same job, same wall, and the
removed common mode grows from "one instruction set" to "one instruction set
and one compiler middle-end". Since the exposure being tested is `-O3` plus
possible integer UB, the compiler is at least as likely a culprit as the ISA —
`R4-G3-13` is on the board precisely because nothing has run under a sanitizer.
Prior the two agree: **0.97**. Prior the change costs anything: **0.05**.
Cheapest kill: if the source is not clang-clean, one compile says so in
seconds, and *that is itself a finding*.

### R4-G7-17 — pre-position the bisection, because it is the only debugging instrument the round will have if m=21 disagrees

The m=21 run is in flight on dalby now (`~/src/pm-b1-perf/experiments/tristruct/r4_spin_m21.log`,
growing at 06:27). `r4-spinproj` §4 says a disagreement at the two frontier
cells is the highest-value outcome the round could produce and localizes by
pattern. It does not say how the localization would proceed. Byte-identical
output is what makes it mechanical: with a deterministic output file, the
campaign can bisect over the axes that are not the mathematics — optimisation
level, compiler, ISA, thread count, m-range split — and the first axis that
changes the hash names the layer. Each bisection step is 88.4 s at m≤16 and 5.6
h at m=21, so the bisection should be run **at the largest m that still
disagrees**, which R4-G7-03's minimization machinery finds. Cost now: zero, it
is a written procedure. Prior it is needed: **0.15**. Prior that, if needed, its
absence costs a day: **0.7**.

### R4-G7-18 — CLOSED WITH THE KILL: distributed third-party verification is not a thing this project should build

The tempting extension of a reproducible artifact is a verification network —
volunteers running the binary and posting hashes. Killed on three grounds, all
already on file: publishing is jasonp's call and nothing goes to an external
service on his behalf; N volunteers reporting the same hash adds *nothing* over
one published hash plus reproducible source, because the evidence is the
reproducibility, not the count of reproducers; and the campaign's stated bar is
one skeptical referee completing a verification, which R4-G7-14 already meets.
Filed so it does not surface a second time as a "what determinism enables"
suggestion.

### R4-G7-19 — determinism is a testable property and the round is treating it as an observed one

Nothing on disk asserts that the spin engine is deterministic; it is assumed
because integer arithmetic is. That assumption is fine for the *values* and not
automatic for everything else: B1 iterates an `unordered_map` and assigns
payload indices in iteration order (`cutcount_b1.cpp.59e90660:229-236`), so the
index assignment is allocator- and insertion-order-dependent even though the
summed values are not. Anything that ever prints or persists a state index —
a checkpoint, a debug dump, a spilled shard — inherits that non-determinism.

Cheap test: two runs on the *same* box with different `--threads`, different
`MALLOC_ARENA_MAX`, and `ASLR` on/off; assert identical sha256. Three runs,
five minutes, and it converts an assumption into a gate. Prior all identical
for the current outputs: **0.9**. Prior it matters later, when a checkpoint or
spill format is added for the ladder: **0.6** — and by then the property will
be assumed, not tested.

---

## §4 What is now cheap enough to be worth doing badly

### R4-G7-20 — the 640-cell comparator sensitivity map, and it costs minutes because the sweep does not have to be re-run

`R4-G5-17` ranks "every match=640 mismatch=0 is asserted by the script that
does the matching" as the campaign's rank-1 correlated failure, and proposes
one RED: perturb one banked row, assert the count is unchanged and the mismatch
rises to 1. Right, and too small. The successor: **perturb each of the 640
cells, one at a time, and record whether the compare catches it** — a per-cell
detection map rather than a single assertion.

The reason this is now cheap and was not before: the comparison runs against
`spin_m16.txt`, a file on disk. **The comparator can be re-run against a
perturbed oracle without re-running the sweep** — seconds per cell, so the full
map is minutes, not the 15.7 core-hours a naive 640-full-sweeps reading would
cost. That difference *is* the "worth doing badly" observation: the expensive
part and the checked part are separable, and nobody separated them.

A map with 640 hits is a sentence. A map with a hole — a cell class the
comparator silently skips, structural zeros being the obvious candidate, since
`r4-adv-ind` §6 item 8 found 21 of GATE 0's 49 cells are self-derived
structural zeros — is a bug in the thing every claim in the round rests on.
Prior the map is complete: **0.8**. Prior the holes, if any, are the structural
zeros: **0.7**.

### R4-G7-21 — UBSan over the whole 640-cell sweep is thirty minutes and it retires R4-G3-13 for one engine outright

`R4-G3-13` notes no counting kernel has been run under a sanitizer on record
and prices it as "build once, run the small gates". With spin, the *whole*
validated sweep is 88.4 s, so a UBSan build running the whole thing at a 10–20x
slowdown is **15 to 30 minutes on one core** — not the small gates, the entire
640-cell comparison, mutants included. That is a different claim: not "the
small cases are UB-clean" but "the run whose output we published is UB-clean".
Prior a real miscount: **0.02**. Prior at least one benign report: **0.4**
(`r4-adv-cost` and `r4-perf` both touch `unsigned __int128` shifts, the classic
source). Entry ticket: n/a. Do it **before** R4-G7-16's cross-compiler run, so
that a cross-ISA disagreement is not chased through UB that a sanitizer would
have named in half an hour.

### R4-G7-22 — the brute-force grower is memory-bound on `frozenset`, not bounded by n, and the fix is a line

`r4_indoracle_brute.py:normalize()` returns a `frozenset` of `(x, y)` tuples and
dedups on it. At n=10 there are ≈6×10⁶ fixed king animals (extrapolating the
banked 1, 4, 20, 110, 638, 3832, 23592 at ~6.2x per step, against
`fixtures/b006770.txt` which has the exact values to **n=20**), each held as a
Python frozenset of ten tuples — several gigabytes, which is why n≤8 is where
the campaign actually stands (R4-G7-00) rather than the n≤12 its job requests
assume. Key it on a canonical integer bitmask over the bounding box instead
(`int`, arbitrary precision, or two `u64`s for boxes up to 10×12) and the per-
shape cost drops by an order; n=11 or n=12 comes into laptop range, which is
what `R4-G2-20`'s re-scope needs.

And the check is free: **A006770 is banked exactly to n=20**, so every row the
grower produces is validated against an external published value with no
campaign code in the loop. That makes the grower the one instrument here whose
own correctness does not need arguing. Prior the bitmask fix reaches n=11:
**0.8**; n=12: **0.5**. Cost: an hour. Entry ticket: level 1 and level 2 both —
literal flood fill over the 3×3 neighbourhood, no frontier, no partition.

### R4-G7-23 — the deliberately naive reimplementation, and it is fifty lines aimed at the exact layer that carries the m>16 risk

From R4-G7-13: spin's states are the valid q=2 colour strings, and the engine's
sophistication is entirely in the *dense ranking* of them (`Ranker`, the
odometer, the `--dense-rank` flag) — which is precisely the layer
`r4-spinproj` §4 names as the likely source of a disagreement in the
never-executed m>16 paths ("mismatch at scattered n points at a rank/carry
fault"). A naive version — a `dict` keyed by the colour string, no ranking, no
packing, no cancellation — computes the same table and shares none of that
layer. Fifty lines of Python, exact at m ≤ 10 or 12 in seconds.

That is an incumbent-free oracle for the ranking layer. It is *not* an
incumbent-free oracle for the rule, since it is the same colour DP — say so in
the first line and it is still worth having, because the ranking layer is the
one nobody else can check. Prior it agrees at m≤12: **0.9**. Prior it is under
two hours to write: **0.8**. Entry ticket: level 1 cleared, same argument as
spin's; level 2 against spin's ranking only.

### R4-G7-24 — the standing list of things already priced under an hour that nobody has run, with times, because that list is the actual finding of this file

Every item below is written, prescribed, or one command, and none has a log:

| item | cost | source |
|---|---|---|
| JOB-IND-2, `r3_spin_pipeline.py` beside GATE 0 | **6.5 s** | `R4-AI2`; GATE 0's own text requires it and the reported result does not mention it |
| `gather()` index audit at every H ≤ 21, no counting | **seconds** | `R4-G2-19` — called the cheapest independence-relevant item in the queue on 2026-08-13, still unrun |
| JOB-IND-1, the flood-fill oracle pointed at the binary | **minutes** | `R4-AI1`; script written, no `.log` |
| `--m 11..16 --verify-rank 1` | **~2 min** | R4-G7-10, the production regime's rank walk |
| `--expect-flips` false-negative REDs | **3 min** | R4-G7-05 |
| clean-vs-clean determinism triple | **5 min** | R4-G7-19 |
| the metamorphic knob sweep | **15 min** | R4-G7-09 |
| UBSan over the full sweep | **≤30 min** | R4-G7-21 |
| 30 single-edit mutants, full sweep each | **44 min** | R4-G7-02 |
| 10,000-site injection census at m≤13 | **28 min, 32 cores** | R4-G7-01 |

**Total, sequential, one core except the last: under three hours.** Against a
ladder priced in weeks and 68–216 GiB. Prior that running this whole list
changes at least one number the round is currently quoting: **0.45**. Prior it
produces at least one sentence a referee cares about: **0.9**.

---

## §5 Second pass — what my own rows share

**(a) Every row above is the same move: the expensive part and the checked part
were fused, and unfusing them makes the check nearly free.** R4-G7-20 is the
clearest case — 640 comparator perturbations read as 15.7 core-hours if you
re-run the sweep and as minutes if you notice the sweep's output is a file on
disk. R4-G7-01 is the same move on the fault model (truncate m, keep the
detector). R4-G7-03 is the same move on the gate (minimize the witness, keep
the coverage). R4-G7-21 is the same move on the sanitizer (the whole sweep is
88 s, so instrument the whole sweep). The round has been pricing *checks* at
the cost of the *computation being checked*, and that is the single assumption
that made everything look rationed.

**(b) Not one of my rows produces a new cell of T(n,H), and I want that on the
record rather than discovered by an adversary.** `r4-gen4`'s R4-G422 and
`r4-gen2`'s pass 2 independently found the same hole from the opposite side —
the round has confirmation instruments and no new rule. My file makes the
instruments sharper and does not add a rule. Everything here raises the
*measured* power of the existing battery; nothing here reaches a cell nothing
else reaches. Three generators now agree on that gap, which is either the
strongest signal in the round about where it stands or evidence that generators
converge on the same reading of the same files. **I cannot distinguish those
two from inside the generator lane, and an adversary should be asked to.**

**(c) The row whose failure takes the most of the others with it is R4-G7-00.**
Nine rows here are priced off the 88.6 s / 640-cell / 90.7 MB measurement. That
one premise I verified and it holds, dalby-measured. But I began this file
believing four things and three were written-but-unrun, all drifting the same
direction — toward believing the instrument exists. If the 88.6 s figure had
also been aspirational, §1, §3 and §4 would all be wrong together, and the
common mode would not be in any engine: it would be in how this round talks to
itself. That is why R4-G7-00's ten-minute `INSTRUMENTS.md` is filed first and
not last.

**(d) A criticism of my own §1.** The false-pass rate R4-G7-01 measures is the
rate against *injected single-slot faults*, which is a model of a wrong
computation, not a model of a wrong rule. It calibrates the battery against
transient and bookkeeping error, and it says nothing at all about the stencil —
which every adversary in this round agrees is the whole residual common mode.
The rows that touch the stencil are R4-G7-02, R4-G7-07 and R4-G7-22, and only
R4-G7-07 could close it. I have ranked the cheap thing first because it is
cheap, and a reader entitled to rank by exposure should read R4-G7-07 first.

---

## NOT ESTABLISHED

- Every cost in this file is desk arithmetic over the measured per-m wall table
  in `r4-spinproj.md` §0. Runs at m > 16 are EXTRAPOLATED by that lane, not by
  me; I quote no m > 16 wall of my own.
- The 30-mutant count in R4-G7-02 is my enumeration of the edit space by
  reading `gather()`/`successors()`. It is a count of *conceivable* single
  edits, not of edits that compile and terminate. ASSERTED.
- R4-G7-22's ≈6×10⁶ at n=10 is extrapolation from the banked growth ratio; the
  exact value is in `fixtures/b006770.txt` (6,053,180) and I did not use the
  fixture for the memory estimate, only for the check that the estimate was the
  right size.
- I did not verify that `--inject` accepts arbitrary (m, col, stage, slot); the
  census in R4-G7-01/08 assumes it does, and R4-G7-01 states that as its kill.
- I did not run the injection census, the mutant census, or any comparison. No
  compute was performed for this file.
