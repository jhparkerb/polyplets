# Priority pass for L10 (Undertow)

2026-08-23, run overnight at jasonp's direction. `paper/L10-undertow.tex` was
drafted 2026-08-22 carrying a banner saying no pass had been run and naming one
as a gate before circulation. This is that pass.

**Verdict: a near neighbour exists, in a different problem, and the paper must
cite it. No collision on the specific claim.**

## What was searched

Five web searches, in this order:

1. lattice animal enumeration + correction term below threshold + exact defect
   polynomial + fixed height / bounding box + asymptotic law;
2. "below the threshold" / "before the onset" + exact correction to a
   polynomial formula + series extrapolation + fewer terms needed;
3. Jensen / Guttmann + series expansion percolation probability + correction
   terms + finite lattice method;
4. polyomino enumeration + transfer matrix + finite lattice method + correction
   terms + exact error term below validity threshold;
5. "finite lattice method" + corrections known exactly + quasi-polynomial +
   onset + validity range + animals.

## What it found — the near neighbour, and it is close

**Directed-percolation series extrapolation by correction terms.** Baxter and
Guttmann (1988), then Jensen and Guttmann through the 1990s, extend the
percolation-probability series for directed lattices by exactly the manoeuvre
this paper's method is built on: a finite-lattice calculation of size `N` is
exact only up to some order, the difference between the exact infinite series
and the finite one is a *correction term* `d_{N,r}`, and knowing those
corrections lets a series be pushed past where the finite lattice is exact —
so the same reach is bought with smaller calculations.

- R. J. Baxter and A. J. Guttmann, *Series expansion of the percolation
  probability for the directed square lattice*, J. Phys. A 21 (1988) 3193.
- I. Jensen and A. J. Guttmann, *Series expansions of the percolation
  probability for directed square and honeycomb lattices*,
  `arXiv:cond-mat/9509121`; and the directed triangular lattice,
  `arXiv:cond-mat/9511084`.

**The ambient family** is the finite-lattice method (Enting; Jensen), in which
small-lattice transfer-matrix data is combined to reach the infinite lattice.
Undertow is a member of that family and the paper should say so rather than
present the shape of the idea as new.

## The one distinction that survives, and it is the honest claim

In the percolation work the correction terms are **conjectured and fitted** —
Baxter and Guttmann conjecture them as rational functions of Catalan numbers,
and the extrapolation rests on that ansatz holding at the next order. That is
what makes their extended series a prediction rather than an enumeration.

Here the correction is **computed exactly, ab initio, by a machine that never
sees the object it corrects**: `D_j(k)` comes from a bounded-excess family
enumeration that reads neither the triangle nor `P_k`. And the number of
unknowns it has to determine per level is not assumed but **proved** — the
grand form gives exactly two constants per level, and that proof is
Lean-complete against the standard axioms.

So the honest form of the claim is the one the draft already anticipated: what
may be new is not the idea of correcting finite-size data, which is standard
practice in this literature, but the combination of an exact independently
computed correction with a proved constant count, in a setting where the saving
is measured in banked compute rather than in extrapolated series orders.

## No collision on the specific claim

Nothing found applies a correction of this kind to **bounding-box-height
animal counts**, and nothing found corrects a **diagonal law** for such counts
in order to pin polynomial levels from below its onset. Searches 1, 4 and 5
were aimed squarely at that and returned the finite-lattice-method literature
and the polyomino enumeration record, not this.

## What this pass is worth, stated as a limit

Web search only. No MathSciNet, no Zentralblatt, no citation-graph crawl of the
Baxter–Guttmann line — which is exactly where a closer instance would sit if
one exists, because a paper that did this for animals would likely cite them.
Five queries is a thin sweep for a negative. The positive finding above is
solid; the negative is provisional and should be re-run against a citation
database before submission.

## Side finding, which the tree had already made

The searches turned up that the square-lattice fixed-polyomino record is not
`n = 56`: OEIS [A001168](https://oeis.org/A001168)'s b-file, contributed by
Barequet and Ben-Shachar, runs to **n = 70**, and Shirakawa,
*Enumeration of Polyominoes up to Size N=59* ([arXiv:2510.22446](https://arxiv.org/abs/2510.22446),
October 2025) independently reaches 59.

**This project found that first** — `docs/rook-parity.md:151` says so, and
`results/rook1/queue.md` row K4 is an open chore to sweep the stale mentions.
So the correct status is "known, unswept", not "found tonight". The sweep has
now been done and K4 is closed:
`results/literature-record-56-corrected.md` is the one place, it lists all six
live sites and what each becomes, and the answer is that no conclusion moves —
the record that grew is the sequence of *totals*, while every use this project
has wants the bounding-box triangle or a perimeter grading, and neither is
published at any n.
