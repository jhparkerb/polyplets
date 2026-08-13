# r4-gen3 — generator pointed at the mission statement, not the recount

Generator `r4-gen3`, round 4, 2026-08-13. Angle: the goal sentence has two
halves and a hidden third. The recount half has four lanes. This file works
the **proof half**, the **"total confidence" half** (what else could make
a(40) wrong), and **what constrains a(40) from outside the campaign**.

**Standing label: I ran no compute.** Everything below is reading, four
desk-arithmetic evaluations on banked integers (sub-second `python3 -c`, big
ints only), and one read-only `ssh dalby ls`. No job, nothing on gympie
beyond the interpreter, no writes outside my three files and the queue.

Row ids are `R4-G3-01` … `R4-G3-25` (hyphenated so `R4-G31` and `R4-G3-1`
cannot be confused).

## 0. Do-not-repeat list, built first

Read in full: `results/r4/queue.md` (all 60 rows), the closed-doors and
three-floors sections of `results/triangle-r3-synthesis.md`,
`results/triangle-r3-provenance.md`, `results/ns_a40/PROVENANCE.md`,
`results/r4/r4-gen2.plan.md`. Skimmed `results/r4/r4-adv-ind.md`,
`results/r4/r4-adv-cost.md`, `results/r4/r4-lean.md` §0/§3,
`results/triangle-r3-l3-proofscope.md` §5-§7.

Not re-derived here, by prior closure: corner gluing (L1), contour encoding
(L3), symmetry quotient / mod-4 ceiling (L4), implicit routes to invariant
counts (LEAD-1), non-group involutions and the two-horn obstruction,
Pfaffian parity, enumeration-based third-party counters, the literature
sweep (L6), the three floors (state / information / term-source). Not
re-filed from the queue: everything in R4-G1..G23, R4-AI1..AI7,
R4-AC1..AC7, R4-P1..P4, R4-SB1..SB3, R4-INV-1..4, R4-A1..A5. Where a row of
mine touches one of those, it cites it and says what is different.

Deliberately left to `r4-gen2`, which is working the same hour: cost
consequences of the 207x overprice, bandwidth-vs-arithmetic, and what a
second validated engine enables.

### One correction to my own brief, before the rows

The brief says round 3 filed the a(40) run's binary provenance NOT
ESTABLISHED and called it "the cheapest attack on the record, an afternoon
of log headers". **That afternoon has been spent.** The round-3 provenance
scout did it (`results/triangle-r3-provenance.md`), the verdict is CLEAN
with one erratum (phase B ran two segments, 64 cores under `38956525` then
48 under `801afd59`, not a flat "48 cores") and one named gap, and since
2026-08-12 20:48 the evidence itself is banked in-repo with sha256s at
`results/ns_a40/dalby-run-evidence/`. The only piece still NOT ESTABLISHED
is **worker-binary identity**, which nothing on disk can now establish. A
lane dispatched at the brief's premise would have re-done finished work.

---

## 1. Direction 2 — how a(40) could still be wrong. Four checks run tonight, then the ranked list

The brief asked for probability × undetectability on the things nobody has
looked at. Four of them turned out to be checkable from files already in the
repo, in minutes, so they are filed as closures with their evidence rather
than as proposals. All four passed. **That is itself the finding: the
campaign is spending thread-days on the one proposition it fears and had
never spent an hour on the five it does not.**

### R4-G3-01 — CLOSED, ran it: the checkpoint tables independently confirm the harvest and combine path, all 40 rows

The three phase checkpoints banked at
`results/ns_a40/dalby-run-evidence/POLYCKPT.{A,B,C}` each carry a full
`tri n value` count table. That is a **second on-disk copy of the run's
counts**, written by the checkpoint serializer at a different moment and
through different code than `writePerHeight`. Nobody had ever compared
them; the recovery used POLYCKPT.B for `h20.out` alone.

Checked, all n = 1..40:

| identity | result |
|---|---|
| `POLYCKPT.A + POLYCKPT.B + POLYCKPT.C` vs `combine.log`'s `a(n)` | 40/40 exact, 0 mismatch |
| `POLYCKPT.A` vs sum of `perheight/h{1..19,22..40}.out` | 40/40 exact |
| `POLYCKPT.B` vs `perheight/h20.out` | 40/40 exact |
| `POLYCKPT.C` vs `perheight/h21.out` | 40/40 exact |
| `results/triangle.txt` vs `perheight/h*.out` | 820/820 cells exact |

Sanity that the partition is the claimed one: `POLYCKPT.A`'s `tri 20` is
1,025,572,357,100,549, short of the published a(20) by exactly
1,162,261,467 = 3^19 = T(20,20) = `POLYCKPT.B`'s `tri 20`. The phases
partition the heights exactly as PROVENANCE.md says.

**What this closes:** the whole class "the counts were right and the
harvest/combine/serialization lost or duplicated some of them" — the class
that actually bit this project once (Zero Harvest), and the only class it
has ever been bitten by in production.

**What it does not close, stated exactly:** `POLYCKPT.A` is an *aggregate*
over H = 1..19 and 22..40. Mass **moved between heights inside phase A** is
invisible to it; mass lost or duplicated is caught. So the per-height
attribution of the unconfirmed band H=15..19 remains single-sourced — see
R4-G3-06. Nor does it test the counting itself: both copies descend from
the same in-memory table.

Prior before running: 0.03 that it would fail. Value is not the prior, it
is that the residual is now one sentence instead of a shrug.

### R4-G3-02 — CLOSED, ran it: frontier conservation across all 779 production columns, including the resume seam

`run.log` emits `event=column H=… col=… frontier_in=… frontier_out=…` per
column. Parsed all of it:

- **779 column lines**, exactly 19 heights (H = 3..21) × 41 columns
  (col 0..40). No missing column, and **no duplicate (H,col) line** — so no
  column was swept twice and silently re-added.
- **760 links checked** (`frontier_out(c) == frontier_in(c+1)`), **0
  mismatches**, every height.
- The links hold **across the phase-B interruption**: H=20 col 6 out =
  128,930,885 = col 7 in, and col 7's line is present exactly once. The
  resumed segment picked up the checkpointed frontier without dropping or
  duplicating a record.

**What this closes:** record-level continuity of the shard/merge plumbing
and of the checkpoint/resume *frontier handoff* — two of the five items the
brief listed as unexamined. It is a record-count identity, not a value
identity.

**What it does not close:** a merge that keeps the right *number* of records
with wrong *counts* inside them, and a shard-boundary duplicate that is
compensated by a drop. See R4-G3-10.

### R4-G3-03 — CLOSED WITH THE KILL: the 1,397 `fastmap_fallback` events in the production log are semantically inert

The production run took a fallback path 1,397 times and no audit has ever
mentioned it. `orchestrator/sweep.go:1360-1375`: when the tmpfs budget
reservation for a map round is refused, the round writes its transient map
outputs to `cfg.RunDir` instead of `cfg.FastMapDir` and logs the event.
Storage location only — same units, same cuts, same arithmetic. The comment
says the event exists precisely so an unexplained slowdown stays
diagnosable.

Filed so nobody spends an afternoon on it. **Residual worth keeping:** 1,397
refusals is a memory-pressure fingerprint, and it is independent evidence
for the Overcommit-Hydra framing — the run really was operating at the RAM
edge, which is context for every OOM-adjacent failure mode below.

### R4-G3-04 — CLOSED, ran it: archived-state replay is possible at exactly one place and it is the one place it is worthless

Round 3 left NOT ESTABLISHED whether any frontier/shard state from the
production run survives for the cost adversary's replay idea. One read-only
`ssh dalby.jhpb.org ls`:

    983M total in ~/src/polyominoes/runs/ns_a40/dalby
     87  merge_h20_c7_k#_r#.bin      + 87 .idx
      1  spill/  run.log  POLYCKPT.A/B/C  combine.log  cost_profile.tsv
      1  a_n.txt  h20.out.zero-harvest-bug

**All 174 surviving state files are H=20, column 7.** Zero bytes of frontier
or shard state survive from H=15..19 or from H=21.

So archived-state replay — take a real production intermediate state and
re-derive the next column with an independent implementation — can be done
at H=20 col 7 and nowhere else. H=20 is already the *best*-corroborated cell
in the band: a byte-identical standalone re-sweep (`recheck/h20.out`,
A40_H20_RECHECK_MATCH). The technique is available exactly where it buys
nothing and unavailable everywhere it would buy something.

**Successors, different in kind:** (i) R4-G3-22's standing-rider row — any
future band sweep should checkpoint one in-band column's state deliberately,
because it is free in-pass and impossible retroactively (this is the third
time the project has learned that); (ii) the surviving H=20 shards are still
a **free plumbing fixture** — 87 real production merge shards with a known
correct successor column, which any future merge-path change can be
regression-tested against without running a sweep. That is worth banking a
hash manifest for before the directory is swept.

### The ranked list

Ranked by probability × undetectability, over what remains after the four
closures above. "Undetectability" = would the existing controls catch it.

| rank | failure mode | prob | undetect | net | row |
|---|---|---|---|---|---|
| 1 | per-height attribution error inside phase A (mass swapped between H, total preserved) | low-mid | **very high** — no control anywhere, and R4-G3-01 is blind to it by construction | **highest** | R4-G3-06 |
| 2 | shard-boundary duplicate/drop at a `BalancedCutsMulti` key cut | low | **very high** — record-count chain (R4-G3-02) does not see it | high | R4-G3-10 |
| 3 | silent u128 wrap in a per-state frontier accumulator | very low | **total** (silent by documented design) | mid-high | R4-G3-05 |
| 4 | single-ISA / single-compiler common mode across *every* engine in the project | low | high — no cross-ISA result exists at any n above the unit tests | mid-high | R4-G3-12 |
| 5 | UB exploited at `-O3` in the counting kernel | low | high — no sanitizer run of the ns worker is on record | mid | R4-G3-13 |
| 6 | closed-form injection path (H=22..40, 4.14%) evaluated wrong at n=40 | very low | mid — `diag_p*_test.go` exists per level | low-mid | R4-G3-09 |
| 7 | worker-binary identity (the one open PROV gap) | very low | high, and **unfixable retroactively** | low-mid | PROV-1, not re-filed |
| 8 | resume under-count (the Zero Harvest silent variant) at H=15..19 | ~0 | n/a | ~0 | R4-G3-07, closed |

### R4-G3-05 — the counter-width guard bounds the wrong quantity, and its own constant is at the razor's edge

`CheckCounterWidth` (`orchestrator/runref.go:591-610`) refuses at start if
`maxn > u128ExactMaxN = 48`. That guard bounds **a(maxn)**, the final
answer. It says nothing about the quantity that actually accumulates: the
per-state, per-n frontier count at a mid-sweep column. `core/counter.h:25`
is explicit that overflow of that is **silent by design** — "the design
prevents reaching it by refusing to start with an undersized counter", i.e.
the whole protection is the guard that bounds a different number.

There is a real guard on the *combine* path — `assert(slot >= prev &&
"count overflow in combine")` at `core/run.h:116,132,138` — and it is live
in production: `CXXFLAGS` (`Makefile:2`) never sets `-DNDEBUG`. It does not
cover the kernel's own per-transition accumulation.

**Half a kill, which is the honest amount.** Every prefix counted at column
c extends to at least one completed animal, and distinct prefixes at the
same column have distinct completions, so the count of any *completable*
prefix class is ≤ a(40) = 5.67e31 ≈ 2^105, leaving 23 bits under 2^128. The
argument does **not** cover prefixes that can never complete, which this DP
does carry, and nobody has bounded their number.

Also worth one line in the same breath, same class as R4-AC2's bit-budget
error: **`u128ExactMaxN = 48` has no documented warrant and is borderline.**
Continuing the banked ratio (6.935 at n=40, drifting to λ≈7.11) gives
a(48) ≈ 3.3e38 against 2^128 = 3.403e38 — under 5% margin, inside the
extrapolation's own error. The constant should be 47, or should carry a
derivation. Immaterial at n=40 (six orders of headroom) and material to
anyone who believes the guard means what it says.

**Cheapest kill:** emit `max_count` per column alongside `frontier_out` in
any future sweep — one comparison per record, free, and it converts this
from an argument into a measured margin. Prior a wrap actually occurred:
0.01. Prior it is worth the one-line instrument: 0.9.

### R4-G3-06 — rank 1: nothing anywhere tests which height a swept animal was attributed to

R4-G3-01 confirms phase A's total. `h15.out`..`h19.out` split that total by
height and **no artifact, test, or second source checks the split** at any n
where the band lives. The strip TM covers H≤14, B1 covers H≤16 (and B1's
H=15/16 agreement is the first real evidence for two of the five). H=17, 18,
19 have no per-height corroboration at any n at all.

This is the same proposition PROV-3/ADV-5 attack from the transpose side
(height marginal = width marginal), and PROV-3's cheap tier — g2
bounding-box binning at n ≤ 16 from a rooted-growth algorithm with no
frontier — is still the cheapest instrument. What I add is the ranking:
**this is the highest net-risk item left in the record**, because the one
control that would have covered it (R4-G3-01) is provably blind to it, and
because 22.20% of a(40) sits on it.

**Different-in-kind successor nobody has filed:** attribution is
checkable *within* the existing data by a sum rule the run never used.
`C_H(n) = Σ_{h≤H} T(n,h)` is what a height-capped sweep computes directly;
the B1 ladder produces exactly those cumulatives (R4-G17). A cumulative at
H=16 and at H=19 brackets the three unconfirmed heights **as a block**, and
a swap between H=17 and H=18 cancels in the block — so the ladder as
currently scoped *cannot* test attribution either. Any future sweep must
emit per-height, not cumulative, to touch this. Prior it changes the ladder
brief: 0.3.

### R4-G3-07 — CLOSED WITH THE ARGUMENT: the Zero Harvest silent variant has zero exposure at H=15..19

Worth writing down because it is the project's only production counting bug
and the natural next question is "where else did it bite". The silent
variant under-counts `h<H>.out` after **any** mid-height resume. Evidence
that it cannot have touched the band: phase A ran under a single
uninterrupted orchestrate invocation (banner line 1, 80 cores, 07-25 20:42 →
07-26 02:59, and the only later A banners resume at the `H=-1`
fully-complete sentinel, which skips harvest); R4-G3-02 shows no duplicate
column line at any height; and R4-G3-01 shows phase A's independent
checkpoint total agreeing with the sum of its `h*.out` files, which a
truncated harvest would break. H=20 is the phase that resumed, and it is the
one with a byte-identical clean re-sweep.

Successors: (i) R4-G3-02's chain check should be a committed script run
against any future run log, not a thing an agent did once — it is 30 lines
and it is the cheapest standing integrity test the project could own;
(ii) the fix's own RED test (`orchestrator/zero_harvest_test.go`) covers the
resume case — nothing covers the *aggregate-vs-per-height* case that
R4-G3-01 exercised by hand.

### R4-G3-08 — the banked `perheight/h*.out` files postdate the run by a day, and their relationship to the run's own output is testimony

All 40 files carry mtime 2026-07-29 11:24, the same minute as
`recheck/run.log` — i.e. they were written or rewritten during the H=20
recheck/recovery, not by the production run on 07-28. The recovery narrative
explains `h20.out`; it does not explain why h1..h19 and h21..h40 share the
timestamp (a `cp` of the whole directory is the obvious benign reason).
R4-G3-01 removes most of the sting — those files now agree with a
build-stamped-era checkpoint that was written on 07-26 and hashed on 08-12 —
so this row is filed **mostly closed by its neighbour**, which is the useful
observation: the checkpoint cross-check retroactively dates the per-height
content even though the files themselves are undated.

Cheapest kill for the remainder: `git log --diff-filter=A` on the perheight
directory plus the combine.log values, which R4-G3-01 already matched.
Prior anything is wrong: 0.02.

### R4-G3-09 — the 4.14% that no sweep touched: arithmetic in the closed-form injection path

H=22..40 at n=40 is 4.14% of a(40), produced by evaluating wired P_k closed
forms, not by counting. `orchestrator/diag_p11_test.go` … `diag_p19_test.go`
show per-level tests exist. What is not established: whether those tests pin
the evaluated value **at n=40** or only at the fit/holdout points, and
whether evaluation is exact rational arithmetic or u128 with a division by
19!. The v5 denominator law (`ĉ_k`, banked) makes the exact denominator
known, so an integrality check on every injected cell is free and total.

**Cheapest kill:** grep the diag tests for an n=40 pin; if present, the row
closes on the spot. Prior it is already covered: 0.7. Prior it is worth the
grep: 1.0. Entry-ticket: N/A, consistency-class.

### R4-G3-10 — rank 2: the shard cut is the one place a count can be duplicated without any existing control noticing

`mapPhase` splits the frontier at `BalancedCutsMulti` key boundaries
(`orchestrator/sweep.go:1346`) and merges the pieces back. A record landing
in two ranges is counted twice; a record landing in none is dropped. Neither
shows up in R4-G3-02's chain (`frontier_out` is measured after the merge,
so a duplicate is conserved through every later column), nor in R4-G3-01
(both copies descend from the merged table), nor in the banked gates, which
are small-n and single-unit.

**Cheapest kill, and it is genuinely cheap:** a RED-first unit test that
constructs a frontier whose keys sit *exactly* on computed cut boundaries
(including the lo/hi endpoints, an empty range, and a range whose entire
content is one key repeated across units), asserts the round-trip record
multiset is preserved, and is verified to go red under a deliberate
off-by-one in `cutsToBounds`. Minutes of authoring, no compute. Prior a bug
exists: 0.05 — the code is old and heavily exercised. Prior the test does
not exist today: 0.6 (`idx_test.go` / `bigwidth_test.go` are adjacent but
not this). Net rank is high because of undetectability, not probability.

### R4-G3-11 — CLOSED AT FILING: "recount the whole thing on a second machine" is already declined and I am not re-pitching it

Recorded so no successor generator files it again: a full a(40) recount,
and the H=22 holdout, are on-demand-only by jasonp's 2026-08-07 decision.
Every row of mine that touches cross-machine work (R4-G3-12) is scoped to a
*small cell*, never the record.

### R4-G3-12 — rank 4: every number this project has ever banked at n=40 came off one ISA

dalby is ARM (Neoverse-N1). The a(40) production run: dalby. The strip-TM
second source at N=40: dalby. The B1 calibration that banked H=15,16: dalby.
The H=20 recheck: dalby. `unsigned __int128` codegen, the compiler, and the
libc are therefore common to the record **and to every check on it**. ayr is
x86_64 and this is the one common mode a different box actually removes.

Scoped so it is not the declined recount: run the **cheapest already-gated
thing** on ayr and compare byte-for-byte — B1 `--modp` at H ≤ 12, or the
existing `tests/gate_cutcount_b1.py`, hours at most. r4-inv §3.4 already
offers an optional ayr repeat of SPIN-JOB-0 for ~5 thread-hours and calls it
"cross-ISA agreement on 640 cells"; **that framing is right and it is the
best-value cross-ISA artifact available** — I am promoting it from "optional
repeat" to the answer to a named common mode, which is a different argument
for the same job. Prior it finds a discrepancy: 0.02. Prior a referee asks
"did you ever run it on another machine": 0.5.

### R4-G3-13 — rank 5: the counting kernel has never been run under a sanitizer, on record

`Makefile` has `-fsanitize=address,undefined` targets (lines 223, 247, 251)
for some tools; nothing on disk records the **ns map/merge worker** ever
built or run that way. `-O3` plus signed-overflow or OOB UB is the classic
way a kernel that passes every small gate computes a different number at a
different size. Cost: build once, run the existing small-n gates, minutes,
one core, and it is a laptop-scale job.

**Cheapest kill:** grep the build/test scripts for a sanitized worker target
— if `make test` already does it, close the row. Prior it is uncovered: 0.6.
Prior of finding a *real* miscount: 0.02; prior of finding at least one
benign UB report: 0.4. Entry-ticket: N/A.

### R4-G3-14 — the external anchor inventory, stated exactly, because everyone assumes it is longer than it is

`fixtures/b006770.txt` is 22 lines and its terms stop at **n = 20**
(a(20) = 1,025,573,519,362,016). Independent-of-this-project values for
A006770 therefore exist for n ≤ 20 only, plus the project's own independent
Redelmeier row at n = 22 (`results/redelmeier_row22/combined.txt`) and the
banked a(23)/a(24)/a(25) artifacts, which are same-project. The
A40_VALIDATE_PASS "chain coverage 19/19" chains a(21)..a(39) against
**banked artifacts of the same engine family** — it is an artifact-integrity
check, not an external one, and its own log says so.

So the honest statement, which I have not seen written anywhere: **the
outside world constrains this project's numbers at n ≤ 20 and nowhere
else.** Every row above n = 20 is in-house. That is not a criticism of the
record; it is the denominator direction 3 has to work against, and it is why
R4-G3-21's inequality arithmetic came out the way it did.

---

## 2. Direction 1 — the proof half, and the unexplored space between (b) and (c)

Round 3 split the claim into (a) the abstract recurrence counts what we say,
(b) the algorithm-as-worded implements (a), (c) the compiled kernels
implement (b) — and filed (c) as **not proposed**. The campaign has one lane
on (a). Nothing has ever priced (c) or the space between. Five candidate
routes, priced.

### R4-G3-15 — the certificate the project can actually emit, and it is H ≤ 18-sized: the transition matrix itself

r4-perf's R4-P3 established something whose consequence it did not take:
`successors`/`gather` depend on the column index only through `c > 0`, so
**the reachable state set saturates after column 2 and the sweep is one
fixed sparse matrix per row, applied 39 more times.** r4-perf reads that as
a speed lever and prices the CSR at 16 GiB (H=17), 52 (H=18), 171 (H=19).

Read as a *proof* object instead, it splits (c) into two pieces that are
checkable by completely different means:

1. **Is the matrix right?** Each row of the CSR is "state s has successors
   s₁..s_k with these weights". That is a **local, stateless, embarrassingly
   parallel** predicate: a 40-line evaluator of the king-adjacency rule
   checks one row without knowing anything about the DP, the sweep, the
   payload, or any other state. No hash table, no canonicalization, no
   packing, no arithmetic wider than a byte. This is exactly the "40-line
   checker over a 300,000-line engine" the brief asks for, and it is the
   only route I found where that phrase is literally true.
2. **Was the linear algebra done right?** 40 sparse matvecs. Mod a 31-bit
   prime, that is one pass over the CSR in a few dozen lines, at soundness
   2^-31 per prime.

Neither step needs the production engine to be trusted, or even read; the
engine becomes an untrusted *proof producer* and the checker is the trusted
base. The 16 GiB certificate at H=17 is a thing a referee can be handed on a
disk and re-verify in hours with a program they wrote themselves.

Honest limits. The certificate must be emitted, which costs one production
run at that height — this reduces trust, it does not reduce compute.
Emitting states in a canonical order that the checker can recompute is the
fiddly part (the checker must not have to trust the engine's ranking
either). And H=19 at 171 GiB is on the edge, H=20/21 off it — so this covers
the ladder's heights, not the corner. Prior it is the best referee-facing
artifact this campaign can produce: **0.45**. Prior it survives contact with
the emission-ordering problem: 0.6. **Cheapest kill:** confirm R4-P3's
saturation premise by comparing the key set at consecutive columns at H=12
— the same probe R4-P3 already needs for its own semantics guard. If the
state set does *not* saturate, the certificate is 41 matrices and the row
degrades to a footnote. Entry-ticket: inherits B1's levels 1+2 if emitted
from the B1 engine; level 1 only if emitted from the incumbent.

### R4-G3-16 — CLOSED WITH THE KILL: `native_decide` cannot bridge (b)→(c), and the reason is worth banking

The tempting shortcut for anyone reading the Lean lane's progress is
"formalise the DP and evaluate it in Lean". It is dead twice over, and the
second reason is the interesting one:

- Kernel evaluation (`decide`) on a state space of 10^8 is not within
  orders of magnitude of feasible.
- `native_decide` **adds the Lean compiler, the C compiler and the runtime
  to the trusted base** — the very class of trust that (c) exists to
  question. A referee who accepts `native_decide` on a 10^8-state DP has
  already accepted a C++ program they did not read; they may as well accept
  ours. The development already uses `native_decide` for small cell pins
  (`Compute.lean`), so the precedent and its caveat are both in-tree.

**Consequence, and it should be stated in any writeup:** the Lean route's
value is *entirely* in statement (a). It contributes exactly zero bits
against implementation error at any n, and a paper that lets the 95.85%
figure sit next to the recount percentages without that sentence is
inviting a referee to add them. This is the same distinction R4-G21 asked
for a currency for, reached from the proof side.

**Two successors, different in kind:** (i) R4-G3-15, where the trusted base
is a program small enough to read instead of a compiler chain; (ii) R4-G3-19,
where Lean certifies a *table* rather than a computation.

### R4-G3-17 — CLOSED WITH THE ARITHMETIC: verified extraction of the production computation is not on any timescale

Extracting a DP from Lean (or writing it in CakeML) and running the band
gives a machine-checked (b)→(c) bridge in principle. The production sweep
was ~52 hours across 80 dalby cores with a hand-tuned cell-at-a-time kernel,
a packed signature, an arena allocator and a spill path. A Lean-extracted
equivalent pays boxed `Nat`, no packed keys, no arena, GC pressure, and no
control over the frontier layout: two to three orders of magnitude is the
optimistic reading, i.e. years to decades of core time, before anyone
writes the verified spill path that 363 GB of intermediate state requires.

**Residue worth keeping:** the ratio that kills it is the *engineering* in
the kernel, not the mathematics — which is precisely why R4-G3-15's split
(verify the matrix locally, verify the algebra in a small loop) is the only
survivable shape. Verify the *object*, never the *program that produced it*.

### R4-G3-18 — translation validation of one production column: possible at H=20 col 7, nowhere else, and therefore not worth doing

Take a real archived production state, apply an independently written
implementation of the transition, compare against the engine's next
archived state. It is the cheapest possible bite of (c): one column, no
sweep. R4-G3-04 settles the inventory — the only surviving in-band state is
the 87 `merge_h20_c7_*` shards, at the one height with a byte-identical
independent re-sweep.

Filed with its kill, and with the successor that keeps the idea alive:
**make it possible next time.** A single `--archive-state H,col` flag on any
future sweep, writing one column's frontier verbatim, costs one column's
disk and makes translation validation available forever after at the height
that matters. That is R4-G3-22's rider list, item 4, and this row is the
concrete reason it is on it.

### R4-G3-19 — the cheapest genuinely new proof artifact in this file: Lean-certify the adjacency stencil, not the algorithm

The independence adversary's standing finding (R4-AI6) is that the **king
adjacency definition** is the last shared thing between every engine —
"semantically load-bearing, hand-implemented in every engine, invisible to
every structural check". Round 3 measured it: with NW adjacency dropped,
both of B1's self-checks still pass while `[q^1]` is wrong from n=2.

That object is 9 cells. A Lean development can define king adjacency from
`Finset (ℤ × ℤ)` geometry, prove the concrete 8-neighbour offset table is
exactly it (a `decide`-scale finite fact), and **export the table** as a
generated header that every engine `#include`s. Every engine then shares one
machine-checked artifact instead of five hand-written ones, and the sharing
becomes a feature to disclose rather than a caveat.

Cost: hours, not sessions — it is a decidable finite statement, the exact
opposite of the sufficiency induction. Prior it lands: **0.8**. Prior a
referee values it: 0.5, and higher than that if the paper's independence
claim is what they are pushing on. **Cheapest kill:** if the engines'
stencils are not textually derivable from one table (e.g. B1's is fused into
a bitmask shift schedule), the export cannot be wired and the artifact is
decorative — check by reading the four stencil sites. Entry-ticket: this
does not clear levels, it *removes a shared input* from routes that already
cleared them.

### R4-G3-20 — nobody has counted the trusted base of any route, and the standard the project scores against asks for exactly that

`docs/skeptical-reader-standard.md` ranks routes partly by "cheapest checker
to a reader" (queue triage rule 3), and the round has never put a number on
it. The measurable version: **lines a referee must read and believe** per
route.

| route | trusted base, order of magnitude | who audits it |
|---|---|---|
| incumbent kink engine | 10^4–10^5 lines C++/Go, plus the orchestrator | nobody, realistically |
| B1 `cutcount_b1.cpp` | ~10^3 lines, single file, no orchestrator | plausible for one referee |
| R4-G3-15 checker | ~40 + ~40 lines, plus a 16 GiB certificate | plausible for a skeptical one |
| Lean (a) | mathlib + kernel, but audited by the kernel, not the reader | the kernel |
| `native_decide` anything | Lean compiler + C compiler + runtime | nobody |

Filed as a row rather than a table because the numbers above are ASSERTED
order-of-magnitudes and the point of the row is to **measure** them
(`cloc` on the transitive include set, an afternoon) and put the column in
the ledger. Prior it changes the ranking of the three live pieces: 0.35 —
and if it does, it changes it toward B1 and toward R4-G3-15, both of which
are currently ranked by share-of-a(40) alone. Different in kind from R4-G21:
that row proposes bits-against-error as a currency; this one proposes
lines-to-audit, and they disagree about which route wins.

---

## 3. Direction 3 — what constrains a(40) from outside the campaign

### R4-G3-21 — CLOSED WITH THE ARITHMETIC: no *rigorous* external inequality catches anything smaller than a factor of 7

Computed tonight on the banked terms (desk arithmetic, big ints):

- **Supermultiplicativity** (Klarner concatenation, banked as the lower-bound
  half in `results/concatenation-upper-bound.md`): a(40) ≥ max_k a(k)·a(40−k).
  The maximum over all 39 splits is at **k = 1** and equals **0.1442 × a(40)**
  — because a(n) ~ Cλⁿ/n makes balanced splits *worse*, not better. So the
  best rigorous lower bound is "a(40) ≥ 6.9× less than a(40)": it refutes
  only errors larger than a factor of 7.
- **Fekete upper**: a(n)^{1/n} ≤ λ ≤ 9.3154 (the exact certificate) gives
  a(40) ≤ **1.03e7 × a(40)**. Seven orders loose.

**The residue is the interesting half.** Both of these are weak because they
are the only *proved* inequalities available. Two much sharper statements
hold over all 40 banked terms and are **not** theorems:
`a(n)^{1/n}` is increasing (would give a(40) ≥ **0.894 × a(40)**, a 10.6%
window, from a(39) alone), and a(n)/a(n−1) is increasing (verified n=3..40
tonight). Consecutive-n monotonicity of a(n)^{1/n} does **not** follow from
supermultiplicativity — that only gives monotonicity along multiples — and I
believe it is open for polyominoes too.

**Successor, different in kind and cheap to scope:** prove
a(n)^{1/n} ≥ a(n−1)^{1/(n−1)} for king animals, or find it in the
polyomino literature. If it is a theorem, a(40) acquires a **rigorous
10.6% two-sided-ish bracket from a(39) alone**, which is the only rigorous
external constraint on the record that would be worth quoting in a paper.
Prior it is provable by concatenation-style arguments: 0.2. Prior it is
already known for polyominoes and transfers: 0.3. Cost to find out: a
literature check, hours. Entry-ticket: level 1 by construction (an
inequality, no rule); level 2 reaches row 40 exactly.

### R4-G3-22 — the sharpest outside instrument is series extrapolation of the ratio, and it is minutes of work

The ratio sequence is smooth: 6.9212, 6.9261, 6.9308, 6.9352 at n=37..40,
with differences 0.0049, 0.0047, 0.0044 — decaying regularly, consistent
with a(n) ~ Cλⁿ n^{-θ}. PROVENANCE.md quotes those four numbers and eyeballs
them. Nobody has **fitted** them.

Fit r(n) = λ(1 − θ/n + O(1/n²)) (or a Richardson / differential-approximant
extrapolation) on n ≤ 39, predict r(40), and compare. The residual of the
fit over the last ten terms *is* the error bar, so the instrument
self-calibrates — and by the shape of those differences it will land near
1e-4 relative, i.e. it would catch any error in a(40) larger than roughly
**0.01–0.1%**. For scale: dropping one whole height from the band is 2.8%
(H=21) to 22% (H=17..19); losing one shard of one column is smaller but
almost certainly above 0.1%.

Distinguish from GEN-4, which is filed CLOSED-with-kill: GEN-4's instrument
was the **certified per-height μ_H brackets** at fixed H, plus
supermultiplicativity — it scored low because the brackets are wide. This is
the **row-total ratio series across n**, a different object with a different
error bar, and it is the standard tool of the enumeration literature for
exactly this purpose. Prior it detects nothing: 0.97. Prior it is worth its
minutes anyway: 0.95, because it is the only instrument in the entire
campaign that is sensitive to a *fractional-percent* error, and because a
referee from the series-analysis tradition will ask for the plot.

**Cheapest kill:** do it; if the fit residual at n=39 (predicting a known
term) exceeds 1%, the instrument has no power and the row closes.

### R4-G3-23 — CLOSED WITH THE KILL: the symmetry route is circular, and the circularity is worth naming

The obvious "identity the project already holds": Burnside over the
order-8 group relates the free (up-to-symmetry) count to
(1/8)Σ_g Fix(g), with Fix(identity) = a(40). The project has an independent
symmetry engine (symtm) computing the non-identity Fix(g) at cost λ^{n/2},
so it is tempting to read this as an external constraint on a(40).

It is not. The free count is *derived from* a(40) plus the same Fix(g)
values; nothing in the project counts free animals by a route that does not
go through a(40). The identity is an accounting rearrangement, not a check.

**Residue worth keeping, and it is a real one:** the non-identity Fix(g) at
n=40 are computed by a **different engine at a different cost class**, and
they are constrained by their own smoothness and by the mod-2 forced-parity
theorem. They cannot check a(40), but a *disagreement* between symtm's
Fix(g) and the main engine's derived quantities would be evidence about the
shared substrate. Whether symtm reaches n=40 at all is **NOT ESTABLISHED**
here — the banked note is a "symcount wall" and I did not chase it.

### R4-G3-24 — the literature has never been searched for *values*, only for *methods*

L6's 35-candidate sweep was a search for **counting methods**. No lane has
searched for **published king-polyomino counts** — at any n, and
specifically at fixed height. Fixed-height king-animal counts are the kind
of thing that appears in transfer-matrix papers as a worked example, in
OEIS as separate small sequences (T(n,1), T(n,2), T(n,3), …), and in the
polyomino-column literature. Any published T(n,H) at H ≤ 6 and moderate n
that matches our table is an external anchor at a height where we currently
have none beyond n ≤ 20.

Honest limit, filed up front: it will not reach the band, and matching at
H ≤ 6 tests the shared stencil and little else. Its value is entirely
referee-facing and it is nearly free — an OEIS read-only search per height
row of the table, which the project is already permitted to run. Prior it
finds at least one published fixed-height king sequence not already known
here: **0.4**. Prior it finds anything above H = 6: 0.1. Entry-ticket: level
1 for whatever it matches (a different author's rule), level 2 never.

---

## 4. Second pass — what my own rows have in common

### R4-G3-25 — the campaign has been auditing its *reasoning* and has never audited its *plumbing*, and the plumbing was an hour of desk work

Four propositions the brief listed as unexamined — combine, checkpoint/
resume, shard continuity, archived-state availability — were settled tonight
in under an hour from files already in the repo, three of them by parsing a
log that has been sitting on dalby since July and in the repo since
yesterday evening. Nothing was found wrong. That is a good outcome and a bad
process: the same hour was available at any point in the last three weeks,
and the round was budgeting **thread-days** against the connectivity
objection while the record's five cheapest failure modes had never been
looked at.

Proposal, one line, no compute: **before any job is dispatched, one pass
that asks what the artifacts already on disk can settle for free.** Concrete
form for this round: R4-G3-01's and R4-G3-02's checks become a committed
script (~60 lines) run against every future run log and checkpoint set, so
they are standing controls rather than a thing an agent noticed once.

The other thing my rows share, and it disagrees with the queue's currency:
**five of them buy nothing measured in share-of-a(40) and would still change
what a referee is handed** — the stencil artifact (R4-G3-19), the trusted-
base count (R4-G3-20), the ratio screen (R4-G3-22), the cross-ISA cell
(R4-G3-12), the boundary test (R4-G3-10). R4-G21 proposed bits-against-error
as a second column; I would add a third and let them fight: **what does the
referee have to take on trust after this row is done.** The three columns
rank the three live pieces differently, and that disagreement is the useful
output, not any one ordering.

## NOT ESTABLISHED

- Whether `diag_p*_test.go` pins the injected closed-form values at n = 40
  (R4-G3-09) — I read the filenames, not the tests.
- Whether a sanitized build of the ns worker has ever been run (R4-G3-13) —
  nothing on disk says so; absence of a log is not absence of a run.
- Whether symtm's symmetry counts reach n = 40 (R4-G3-23).
- Whether R4-P3's state-set saturation premise holds — R4-G3-15's whole
  cost model rests on it and it is r4-perf's ASSERTED reading of the code,
  not a measurement.
- The trusted-base line counts in R4-G3-20 are ASSERTED order-of-magnitudes.
- a(48) ≈ 3.3e38 in R4-G3-05 is EXTRAPOLATED from the banked ratio trend,
  not computed.
