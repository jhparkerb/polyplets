# What we know, and how well

Written 2026-08-20 for jasonp, in plain terms, as a snapshot; the running
job named at the bottom landed 2026-08-21 08:43 and items 3 and 4 are
rewritten to say what it settled; they were rewritten again 2026-09-05 after
AUDIT-2026-09-02 found both overstated. It says how much
evidence stands behind each value of A006770 and where the weak points are.
Supporting detail, with citations, is in `docs/lastditch-campaign.md`; this
file is the version that does not assume you have read any of it.

**This is a snapshot.** The last section says what was running when it was
written and what finishing it would change. Check that section's date before
relying on the confidence levels below.

---

## The two kinds of evidence

There are only two ways to be confident in one of these numbers.

**Compute it twice with genuinely different programs.** If two methods that
share no code and no strategy agree, a bug in one would have to be matched by
an identical bug in the other. This is the real evidence.

**Compute it once and check it against known structure** — growth continuing
smoothly, cells with exact known formulas coming out right, sums matching.
This catches gross errors. It does not catch a subtle systematic one.

Everything below is a statement about which of those two a given number has.

## Where things stood before 2026-08-20

Every value up to a(40) had been computed by one program — the column sweep
that has produced the frontier for years. A second, genuinely different
program (it counts by colouring, and never decides connectivity at all) had
been run up to height 18. Because of how the table assembles, that was enough
to independently confirm **a(n) for n <= 35 entirely**.

Above that, confirmation was partial. Row 40 had five of its forty cells that
no second program had ever touched <!--q:row40_residual.count@18=5-->. The plan to fix that was to run the second
program at heights 19, 20 and 21. Height 19 was priced at 27-40 days. Heights
20 and 21 were believed impossible on the hardware we have.

## What the work of 2026-08-20 to 09-05 changed

**One mathematical thing.** The cells near one edge of the table follow exact
formulas. Each formula has two unknown constants that have to be fixed from
real computed data. The standing rule fixed them using the two *tallest* cells
available — the most expensive ones in the whole calculation. That was never
necessary. Separate earlier work had already derived exact correction terms
for the region just below where each formula starts being valid, and those
corrections make cheap, short cells into equally valid equations for the same
two constants.

So the expensive computation no longer has to climb as high. For row 40 it now
stops at height 19 instead of 21. The two heights that come off are the two
that dominated everything: they were three-quarters of the processor time and
took the disk requirement from 69 GB to 363 GB.

**One engineering thing.** The second program ran on a single core of an
eighty-core machine. It now uses all of them and has a rewritten memory
layout. It is about fifty times faster. Height 19 went from 27-40 days to
about a day.

## The numbers, in order of confidence

**1. a(n) for n <= 35 — highest. Unchanged.**
Two independent programs agreed on every cell: each is either recounted by the
second program directly, or given by a formula pinned on that program's own
cells. Whole-row enumeration by a third, unrelated program (Redelmeier) reaches
n = 22. The work of 2026-08-20 onward did not touch any of this.

**2. a(n) for n = 36 to 39 — high. This was the largest gain of the work of
2026-08-20 to 09-05.**
Every cell of every one of those rows is now either computed directly by the
second program, or derived by formula from that program's own data. No part
depends on the original program. Each row was rebuilt from scratch that way
and compared: every cell matches, and every row sums to the published value
exactly. An adversarial review traced every input back to its source and found
nothing circular.

Before 2026-08-20 these rows were only partly confirmed. They are now fully
confirmed.

**3. a(40) — every height the second program reaches agrees, as of 2026-08-21.**
The second program covers heights 1 to 19, and at n = 40 every one of those
nineteen cells matches the original. Height 19 was the last swept cell resting
on the original alone; the second program computed it directly and got
3247572468599336484342102174163, which is what the original had. The row sums
to the published a(40).

The twenty-one cells above height 19 are not enumerated by any second program.
They are reproduced by the formula tower fitted to the second program's own
data, and item 4 says what that is worth. Before 2026-08-20, 35 of 40 cells
had a second program, or a formula anchored on the second program's cells,
behind them <!--q:row40_residual.count@18=5-->; now 37 of 40 do
<!--q:row40_residual.count@19=3-->, and the other three, T(40,20), T(40,21)
and T(40,22), rest on the tower alone. Those three are row 40's band; the
repo-wide list of cells carrying only the mod-4 congruence is a different
three, T(39,20), T(40,20) and T(40,21), and `results/residual-cells.md` is the
one place both are computed. The 2026-08-21 text here said
"40 of 40"; that counted the tower as a second program, which it is not
(AUDIT-2026-09-02 M2).

**4. a(41) = 393811462683918679824582849262105 — computed, with a second
program under nineteen of its forty-one heights, as of 2026-08-21; the top
formula overdetermined as of 2026-09-05; height 20 enumerated the same
evening, and it equals what the formula predicted.**

The colouring program was run at all nineteen heights it can reach, at the size
row 41 needs — the thing that had never been done, since every stored result it
had stopped at n = 40. Those nineteen cells agree with the original program's
sweep cell for cell (`results/cutcount_b1/rows41/`, gated by
`make gate-cutcount-assembly`).

The remaining twenty-two cells, heights 20 to 41, come from the formula tower,
and here the 2026-08-21 text of this item overstated. It said "two methods that
share no code and no strategy now agree on it". That is true of the nineteen
swept heights. Above them there is one tower strategy: its levels up to 19 are
the wired formulas, levels 20 and 21 are fitted below onset, and
`experiments/undertow_ri.py` refits them to the colouring program's own cells
and reproduces the row digit for digit — but that refit shares the correction
tables (`D_j` at levels 20 and 21) and the grand form with the original route.
The accurate statement is: **19 swept heights two-source with no shared code;
heights 20 and up one tower strategy pinned from the colouring program's data,
sharing `D_j(20..21)`** (AUDIT-2026-09-02 M2).

What still limits it: the top of the row is formula rather than direct
computation. Until 2026-09-05 the formula governing the tallest tower level was
fixed by exactly two data points with nothing left over to check it against.
A fifth correction table, banked 2026-08-23 and never wired into the assembler,
gives it a third point; the three fits agree, and `make gate-undertow-pairs`
fails if they stop (`results/a41/PROVENANCE.md`). That is agreement between
fits sharing their correction tables, not an enumeration of the cell.

The earlier reservation, that the independent re-derivation "took 0.2 seconds,
which is a fair measure of how much less it is than the weeks that went into
confirming a(40)", no longer applies to this item. The run that settled the
nineteen heights took about 22 hours.

**5. The rest of the table — a real consistency gain, weaker in kind.**
A systematic audit re-derived 189 previously computed values from shorter,
cheaper ones, and got every one right. That included two values which the top
formula had been fitted to and which had therefore never had any independent
check at all. This is the mathematics checking itself rather than a second
program checking it, so it is weaker than item 2 — but it covers the whole
table.

## When a cell may come from a formula instead of a computation

Two frontier values here are assembled with some of their cells supplied by a
formula rather than enumerated: a(41) for the main sequence, and D(33), the
diagonal-mirror count that four of the related sequences depend on
(`results/symmetry-classes.md`). One rule decides whether that is allowed, and
it is the same rule for both towers.

A formula cell may enter a banked value when all three of these hold, and the
value has to declare which of its cells they are.

1. The **shape** of the formula is proved, not observed in data.
2. The cell lies where the formula is **known** to hold, at the same grade as
   the claim: an onset that is proved, not one read off data.
3. The **constants** are fixed from enumerated cells, with at least one
   enumerated cell held back and reproduced.

**a(41) passes all three** (`results/a41/PROVENANCE.md`): shape and onset are
both theorems for the main tower, the onset was proved sharp on 2026-09-05
(`docs/proofs/diagonal-law.md`), and every level is pinned with cells left over
to check it. What limits a(41) is not this rule but the separate extrapolation
in the next section, which is why item 4 stops short of calling the top of the
row second-sourced.

**D(33) fails the second condition.** The shape of the diagonal-mirror formula
is a theorem (`docs/proofs/dm-diagonal-law.md`); the onset the assembly uses,
S >= 2k+2, is data-grade. The formula cells sit eighteen or more steps past
that onset with every intervening cell reproduced, but far past an unproved
bound is not the same grade as past a proved one. D(33) stays
conjecture-assisted and out of OEIS b-files. The mod-3 argument that settled
sharpness for the main tower has no diagonal-mirror counterpart
(`docs/proofs/dm-diagonal-law.md`).

## Where the residual risk actually sits

The formulas rely on correction terms that were verified against known data up
to a certain size and then used slightly beyond it. That extrapolation is the
one place where something could be wrong and not show up.

It is narrow. Two of the three correction values involved have fully
independent derivations produced by different code. The third was said here to
be "constrained by an arithmetic property that would break if it were wrong";
that was overstated. The property is integrality, it catches only a fractional
error, and every error the table behind that value can actually carry is an
integer one — measured 2026-09-05, an error of 9 in one table entry moves
a(41) by 9 and passes it. What checks the third value now is a fourth, at the
next depth, which gives the top formula a third data point; the three agree,
and `make gate-undertow-pairs` fails if they stop. But if any of this fails,
that is where.

## What was running, and what it bought

*Launched 2026-08-20 10:38, finished 2026-08-21 08:43 — about 22 hours on
dalby.* The second program across all heights up to 19, at the size row 41
needs.

It delivered both of the things it was launched for: every height the second
program reaches, agreed at n = 40 and at n = 41; and a(41) with a second
program under its nineteen swept heights rather than under none. Nineteen exact rows
were reconstructed from nine modular runs each, with one prime held out of
every reconstruction as a check — it predicted correctly at every length in
every height, and the reconstruction tool exits non-zero if it ever does not.

The job was originally launched at the wrong size — it would have finished
a(40) and done nothing at all for a(41). jasonp caught that.

*Landed 2026-09-05 21:19 EDT, 9.6 hours on dalby's 76 cores.* Height 20 at
the size row 41 needs was enumerated by the original program
(`results/a41/h20.out`), and the value, 18004779862205054677763902712770, is
exactly what the formula tower had predicted for it from shorter cells. That
was the last soft spot named above. What it settles: the tallest formula
level is checked against an enumeration, and a(41) no longer uses it at all.
What it does not settle: heights 21 to 41 of row 41 are still formula, and the
second program still reaches only height 19, so T(41,20) has one enumeration
and one prediction behind it, not two enumerations
(`results/a41/PROVENANCE.md`, `make gate-undertow-pairs`).

## On trusting this account

Several characterizations written while that work was in progress were wrong and were
corrected — by the review team, by the automated checks, and by jasonp. The
numbers themselves never changed; the descriptions of how well-supported they
were did. Every correction is written into the repository next to the claim it
corrects, so this account does not have to be taken on trust either.
