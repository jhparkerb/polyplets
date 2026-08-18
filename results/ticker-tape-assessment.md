# Is Ticker Tape (H = 19) worth it? Priced on Confetti's measured cost

2026-08-18, from Confetti's four completed passes rather than from the plan's
model. Short answer: **no, not as it stands** — it does not fit in dalby's RAM
with the current layout, and what it buys does not change any statement the
project can make.

## What Confetti actually cost

Measured, `~/var/motley-h18/run.log`: passes 1–4 landed 08-15, 08-16, 08-17 and
08-18, at **79,039 s each (22.0 h)**, peak RSS **65.9 GB**, single-threaded.
Five passes is **110 h ≈ 4.6 days** of dalby, ending ~08-19 08:40 EDT. One core
of eighty, but 66 GB of 125 GB, so the box is not free for anything large while
it runs.

## What H = 19 would cost, on the same constants

The ladder constants measured at H=16→17 are **wall x3.209** and **RSS x2.984**
per height (`results/motley-h17.md`).

| quantity | H = 18 measured | H = 19 projected |
|---|---|---|
| wall per pass | 79,039 s (22.0 h) | ~253,700 s (**70.5 h**) |
| passes | 5 | 9 |
| total wall | 110 h (4.6 d) | **634 h ≈ 26 days** (~40 with the ST 3→2 split) |
| peak RSS per pass | 65.9 GB | **~197 GB** |

**197 GB against dalby's 125.** The plan's 87 GB projection assumed an arena at
57 B/window; Confetti measured **909.7 B/window**, 16x that target. So Ticker
Tape does not run today at all: it needs the arena redesign first, and that
redesign has to find a factor of ~1.6 just to fit, with no measurement yet
saying it can.

## What it would buy

Each rung closes one cell at the bottom of row 40 and one at the top.

| | closes outright | row 40 residual | share of a(40) with no exact second source |
|---|---|---|---|
| after Half Measure (H≤17) | n ≤ 33 | 7 cells | 25.0% |
| after Confetti (H≤18, tomorrow) | n ≤ 35 | 5 cells | **15.65%** |
| after Ticker Tape (H≤19) | n ≤ 37 | 3 cells | **8.83%** |

Ticker Tape's two cells are T(40,19) = 5.72% and T(40,23) = 1.10% of a(40):
**6.82% of the term**, plus rule-independent closure of a(36) and a(37).

## The rate, and the judgement

- Confetti: **16.5%** of a(40) second-sourced, plus two terms, for **4.6 days**
  — 3.6 points per day.
- Ticker Tape: **6.8%**, plus two terms, for **26–40 days** plus an arena
  redesign — 0.2 points per day.

That is an **18x worse return**, and the qualitative position is unchanged
either way: after Confetti the honest sentence is "8.8–15.7% of a(40) rests on
a single engine"; Ticker Tape moves the number and does not remove the
sentence. a(38), a(39) and a(40) stay outside rule-independent closure at every
rung of this ladder, and they are the terms the paper is actually judged on.

**Recommendation: stop the ladder at Confetti.** Bank H=18, quote n ≤ 35
rule-independent and 15.65% single-sourced, and spend the month on the
release-critical items instead. Revisit only if the arena redesign lands for
some other reason and H = 19 becomes a weekend rather than a month.

**What does not substitute for it:** Coin Lift's exact-value route is excluded
by the mod-p floor (`results/coin-lift-g2.md`), so the residual band has no
cheap alternative closer. The mod-2/mod-4 subgroup census already covers 100%
of row 40's cells at congruence level (`results/subgroup-mod4.md`); that is a
different kind of evidence and it is already banked.
