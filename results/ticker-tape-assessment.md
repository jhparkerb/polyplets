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

Each rung closes one cell at the bottom of row 40 and one at the top, and closes
two more terms outright.

| | closes outright | row 40's residual cells | <!--q:prose-->
|---|---|---|
| after Half Measure (H<=17) | n <= 33 <!--q:closure_n@17=33--> | 7 <!--q:row40_residual.count@17=7--> |
| after Confetti (H<=18, tomorrow) | n <= 35 <!--q:closure_n@18=35--> | 5 <!--q:row40_residual.count@18=5--> |
| after Ticker Tape (H<=19) | n <= 37 <!--q:closure_n@19=37--> | 3 <!--q:row40_residual.count@19=3--> |

Every figure in this table is generated in `results/residual-cells.md` and
checked against it by `make gate-residual-cells`. Note that this is row 40's
**rule-independence** band --- Q2 there --- a different quantity from the
congruence-only cells the provenance gate pins, Q1; the two were conflated for
a day, which is why they now have names. <!--q:prose-->

Ticker Tape's two cells are T(40,19) and T(40,23)
<!--q:row40_retires.cells@19=T(40,19),T(40,23)-->, and its two terms are
a(36) and a(37). In Q1 terms it would retire three congruence-only cells
<!--q:retires.count@19=3-->, (38,19), (39,19) and (40,19)
<!--q:retires.cells@19=(38,19),(39,19),(40,19)-->.

## The judgement

Confetti buys two cells and two terms for 4.6 days. Ticker Tape buys two cells
and two terms for 26-40 days plus an arena redesign that has to find a factor
of 1.6 before the job fits in RAM at all. Same purchase, six to nine times the
wall clock, and a prerequisite nobody has measured.

The position afterwards is also unchanged in kind. Row 40 still has cells with
one source, so the sentence "part of row 40 rests on a single engine" survives
Ticker Tape exactly as it survives Confetti -- three cells instead of five is
not a different claim, it is the same claim with a smaller list. And a(38),
a(39) and a(40) stay outside rule-independent closure at every rung of this
ladder, which is what the paper is actually judged on.

**Recommendation: stop the ladder at Confetti.** Bank H=18, quote n <= 35
rule-independent, name the residual cells, and spend the month on the
release-critical items instead. Revisit only if the arena redesign lands for
some other reason and H = 19 becomes a weekend rather than a month.

**What does not substitute for it:** Coin Lift's exact-value route is excluded
by the mod-p floor (`results/coin-lift-g2.md`), so the residual band has no
cheap alternative closer. The mod-2/mod-4 subgroup census already covers every
cell of row 40 at congruence level (`results/subgroup-mod4.md`); that is a
different kind of evidence and it is already banked.
