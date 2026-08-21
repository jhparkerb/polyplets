# What we know, and how well

Written 2026-08-20 for jasonp, in plain terms, as a snapshot; the running
job named at the bottom landed 2026-08-21 08:43 and items 3 and 4 are
rewritten to say what it settled. It says how much
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

## Before this session

Every value up to a(40) had been computed by one program — the column sweep
that has produced the frontier for years. A second, genuinely different
program (it counts by colouring, and never decides connectivity at all) had
been run up to height 18. Because of how the table assembles, that was enough
to independently confirm **a(n) for n <= 35 entirely**.

Above that, confirmation was partial. Row 40 had five of its forty cells that
no second program had ever touched. The plan to fix that was to run the second
program at heights 19, 20 and 21. Height 19 was priced at 27-40 days. Heights
20 and 21 were believed impossible on the hardware we have.

## What changed

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
Two independent programs agreed. This session did not touch it.

**2. a(n) for n = 36 to 39 — high, and this is the largest gain of the
session.**
Every cell of every one of those rows is now either computed directly by the
second program, or derived by formula from that program's own data. No part
depends on the original program. Each row was rebuilt from scratch that way
and compared: every cell matches, and every row sums to the published value
exactly. An adversarial review traced every input back to its source and found
nothing circular.

Before this session these rows were only partly confirmed. They are now fully
confirmed.

**3. a(40) — complete, as of 2026-08-21.**
All forty cells. The last one, at height 19, was the only cell in the row that
had ever rested on a single program; the second program computed it directly
and got 3247572468599336484342102174163, which is what the original program
had. Every one of the nineteen heights the second program covers agrees with
the original at n = 40, and the row sums to the published a(40).

Before this session: 35 of 40 cells independently confirmed. Now: 40 of 40.

**4. a(41) = 393811462683918679824582849262105 — high, as of 2026-08-21. It
was the weak one.**

It now has a second program in it. The colouring program was run at all
nineteen heights it can reach, at the size row 41 needs — which is the thing
that had never been done, since every stored result it had stopped at n = 40.
Those nineteen cells were rebuilt from it, the formulas for the remaining
twenty-two cells were fitted to *its* data rather than the original program's,
and the row was summed. It came out
393811462683918679824582849262105, digit for digit.

So a(41) is now on the same footing as a(36)-a(39): every cell either computed
directly by the second program or derived by formula from that program's own
data, with no part of it depending on the original program. Two methods that
share no code and no strategy now agree on it.

What still limits it, and it is the same limit a(36)-a(39) have: the top of the
row is formula rather than direct computation, and the formula governing it is
fixed by exactly two data points with nothing left over to check it against.
That is a statement about the top twenty-two cells, not about the agreement —
the agreement is real and was not available yesterday.

The earlier reservation, that the independent re-derivation "took 0.2 seconds,
which is a fair measure of how much less it is than the weeks that went into
confirming a(40)", no longer applies to this item. The run that settled it took
about 22 hours.

**5. The rest of the table — a real consistency gain, weaker in kind.**
A systematic audit re-derived 189 previously computed values from shorter,
cheaper ones, and got every one right. That included two values which the top
formula had been fitted to and which had therefore never had any independent
check at all. This is the mathematics checking itself rather than a second
program checking it, so it is weaker than item 2 — but it covers the whole
table.

## Where the residual risk actually sits

The formulas rely on correction terms that were verified against known data up
to a certain size and then used slightly beyond it. That extrapolation is the
one place where something could be wrong and not show up.

It is narrow. Two of the three correction values involved now have fully
independent derivations produced by different code. The third is constrained
by an arithmetic property that would break if it were wrong. But if any of
this fails, that is where.

## What was running, and what it bought

*Launched 2026-08-20 10:38, finished 2026-08-21 08:43 — about 22 hours on
dalby.* The second program across all heights up to 19, at the size row 41
needs.

It delivered both of the things it was launched for: a(40) complete, and a(41)
confirmed by a second program rather than merely computed. Nineteen exact rows
were reconstructed from nine modular runs each, with one prime held out of
every reconstruction as a check — it predicted correctly at every length in
every height, and the reconstruction tool exits non-zero if it ever does not.

The job was originally launched at the wrong size — it would have finished
a(40) and done nothing at all for a(41). jasonp caught that.

One further run of about eleven hours would test the single unchecked formula
against a directly computed value, which is now the last soft spot in the whole
construction.

## On trusting this account

Several characterizations written during the session were wrong and were
corrected — by the review team, by the automated checks, and by jasonp. The
numbers themselves never changed; the descriptions of how well-supported they
were did. Every correction is written into the repository next to the claim it
corrects, so this account does not have to be taken on trust either.
