# The square-lattice record is n = 70, not n = 56 — and no conclusion moves

2026-08-23, executing `results/rook1/queue.md` row **K4**, an open chore whose
kill criterion is "grep for `56` record mentions coming back empty". This is the
one place the record is stated, so that the next file to need it cites this
rather than re-deriving it.

**The chore's finding is not new here.** `docs/rook-parity.md:151` already says
"the polyomino record in project docs is stale at n = 56; it is n = 70", from
`papers/counting_polyominoes_revisited.pdf`. What this file adds is the sweep it
asked for, a second confirmation, and — the part that matters — an explicit
check of every claim in the tree that was resting on the stale number.

## What the record actually is

| quantity | reach | source |
|---|---|---|
| `a(n)`, fixed square polyominoes, **totals** | **n = 70** | OEIS [A001168](https://oeis.org/A001168) b-file, contributed by Barequet and Ben-Shachar; `a(0)..a(56)` credited there to Jensen |
| the same, independently | n = 59 | Shirakawa, *Enumeration of Polyominoes up to Size N=59*, [arXiv:2510.22446](https://arxiv.org/abs/2510.22446), October 2025 |
| `T_sq(n, H)`, the **bounding-box triangle** | not published at any n | — |
| perimeter-graded square counts | not to the order this project would need | — |

Verified 2026-08-23 by reading the b-file directly: its last line is
`70 18500792645885711270652890811942343400814`.

**The distinction that does all the work below**: what moved from 56 to 70 is
the sequence of *totals*. Every use this project has for square-lattice data
wants something finer — the triangle by bounding-box height, or a perimeter
grading — and none of that is published at any size. The project's own square
triangle is `results/bbox_square4_n21.txt` and stops at n = 21.

## Every claim that quoted 56, and what it becomes

| file | what it said | after |
|---|---|---|
| `docs/lastditch-ideas.md` §1b | "square polyominoes are enumerated to n = 56 in the literature" | **stale number, live claim**: n = 70. The §1b headline needs square cells *below onset* at `H ≤ 28`, which is triangle data and is published at no n, so the headline is no closer than it was |
| `docs/skeletonkey-reprompt.md` (#18) | "the published-n=56 headline still needs square cells below onset at `H ≤ 28`" | same: the number changes, the blocker does not |
| `results/skeletonkey-parametric-master.md` | "n = 56 needs square cells at `H ≤ 28`. That is Jensen's computation" | same, and "Jensen's computation" is now Barequet and Ben-Shachar's for the totals — but the triangle is still nobody's |
| `results/undertow-square-validation.md` | "nor does it reach the n = 56 headline §1b hoped for" | unchanged in force |
| `results/skeletonkey-l3-3-fattening.md` | a(40) would need polyominoes of ≥ 160 cells "against a literature record of n = 56" | **kill unaffected**: 160 against 70 is still more than twice the record, and the objection that actually closed L3-3 was the bijection test, not the size |
| `results/skeletonkey-four-mechanisms.md` §7 | Sykes–Essam needs square data "to order about 200 in the percolation variable, against a literature record of 56 by area" | **kill unaffected**: the requirement is perimeter-graded to order ~200, and totals to 70 do not touch it |

**So nothing reopens.** Every door the number was used to close stays closed,
and in the two cases where it was load-bearing (L3-3's size argument, Sykes–
Essam) the margin is large enough that 70 changes no verdict. What was wrong was
a fact, quoted six times.

## Why it went stale, which is the reusable part

The number entered the tree as "Jensen 2003, n = 56" — correct when written, and
correct as a statement about *one* computation. It was then re-quoted as "the
literature record", which is a different claim with a different lifetime: a
record is a moving quantity and a citation is not. `docs/project-postmortem.md`
names asserted prices propagating as a failure class; this is the same failure
with an external fact rather than an internal price.

The cheap guard is the one this file is: **quote the record from one place, and
have that place say when it was last checked.** Last checked 2026-08-23.
