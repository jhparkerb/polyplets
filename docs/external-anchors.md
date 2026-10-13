# External anchors: published values this machinery reproduces

An internal consistency check asks the reader to trust us. An external anchor
does not: it is a number somebody else published, which our programs land on
without being told to. Every item below is of that kind, with the file where
the comparison can be repeated. The order is by how little the reader has to
take on faith.

One caution on the first anchor. `fixtures/b006770.txt` carries 20 terms, but
n = 19 and 20 in it are this project's; OEIS A006770 (revision 44, 2026-05-30)
lists 18 terms and has no author-uploaded b-file. The comparison in
`scripts/bfile_gate.py` is scoped to n ≤ 18, with the overlap size fixed so
that appending a term to the fixture cannot widen the anchor.

## Tier 1 — published integers, reproduced exactly

| anchor | published by | what we reproduce | where to repeat it |
|---|---|---|---|
| A006770, a(1)–a(18) | OEIS entry, pre-dating this work | all 18 terms | `fixtures/b006770.txt` lines n ≤ 18; `make gate-bfiles` |
| A067675 / A067676 | Kotesovec (convex polyominoes by area) | 50 terms each, from the square-lattice control of the convex-polyplet transfer matrix | `results/subclasses.md` |
| A222205 | Sloane 2013, from Bacher | all 23 published terms, extended to 200 | `results/subclasses.md`, `results/multidirected_terms_n200.txt` |
| A187077 | OEIS (column-convex) | the generating function, rediscovered by Temperley's method | `paper/L5-convex-polyplets.tex`, §column-convex |
| A053993 | Andrews, Memoirs AMS 301 (1984), `phi_2` | the square lattice's diamond-tip series, to n = 40 | `experiments/cone_order_ideals.py`; `paper/L6-perimeter-gradings.tex`, §min |
| A(n,2n+2) = 1, A(n,2n+1) = 4(n−2) | Asinowski–Barequet–Zheng | our square-lattice defect column's k = 0 and k = 1 rows | `paper/L6-perimeter-gradings.tex`, §max |

## Tier 2 — published constants, reproduced and extended

| anchor | published value | ours | where to repeat it |
|---|---|---|---|
| Bender's convex-polyomino growth constant | 2.30914 | same, extended to 121 trusted digits by the square-lattice control | `paper/L5-convex-polyplets.tex`, §μ |
| Klarner–Rivest constant (A276994) | ~75 digits | every published digit, from the control kernel's smallest positive zero | `results/subclasses.md` |
| Kotesovec's amplitude for A067675 | ~71 digits | every published digit, from the same residue formula | same |

The square-lattice control matters more than the king numbers beside it: it
shares all its machinery with the king computation and none of its inputs, so
reproducing a published constant to certified precision tests the pipeline that
produced the uncertified one.

## Tier 3 — published theorems our results land on

- Richard, arXiv:0704.0716: the rectangles area limit law `beta_{1,1/2}` for
  convex polygons. Our area-moment work rederived it without knowing, which is
  a collision on priority and at the same time a check: the king lattice, where
  nothing is solved, lands in the same universality class as the solved square
  case. Enting–Guttmann (1989) cover the square control.
- Delest–Viennot (1984): algebraicity of convex polyominoes by perimeter, used
  as the positive control for the algebraicity guesser that produced our king
  verdicts. A guesser that cannot find a known algebraic equation is not
  evidence about an unknown one.
- Fortuin–Kasteleyn / Potts: the coloring recount's rule is the spin
  representation of `q^{components}`, and the production engine is a
  connectivity-tracking method in the Jensen tradition. Their independence is
  a structural fact about two classical representations of one partition
  function, not a claim about our two programs
  (`docs/proofs/cutcount-identity.md`).
- Asinowski–Barequet–Zheng: the perimeter-defect identity `k = e + 2f` and
  rationality with cyclotomic denominators. The identity licenses our
  enumeration prune, so the prune rests on published mathematics.
- The square-lattice growth constant, from our own differential-approximant
  code. The spectrum written for A006770, run unchanged on A001168's 70
  published terms, returns λ = 4.06257 against the published ≈4.0625696: six
  digits, from code never tuned to that lattice. The same run gives
  θ_square = −0.9995 against θ_king = −0.9997 at matched length, which is the
  universality prediction tested rather than quoted.
  `results/growth-constant.md`.

## Tier 4 — controls that are required to fail, and do

A method that would prove something false is run against a case where the
truth is published.

- The λ bound argument on the square lattice. The elementary encoding that
  gives λ ≤ 12.2 on the king lattice gives λ_polyomino ≤ 4 on the square one,
  against the published λ_polyomino ≈ 4.06 (Barequet–Rote–Shalah). It is run
  there first so that a bound with no published number to check against is
  not the first place the argument is tested. `paper/L3-lambda-bounds.tex`,
  §false starts.
- The OEIS search pipeline's control query. `1,2,7,28,120,528,2344,...` must
  hit A005436 exactly, and does; a search that finds nothing is
  indistinguishable from one that is broken.

## What this list does not claim

None of this establishes a(23)–a(40). The anchors test the machinery; the
terms rest on the provenance table (`results/provenance-table.md`) and on the
second source.
