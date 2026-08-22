> **NOTE: authored by Claude at jasonp's direction, 2026-08-18.** Source
> material for P1's validation chapter, assembled after the week's literature
> passes turned up three collisions. **This is a receipts list, not prose** —
> `paper/technical-report.tex` is his and stays untouched.

# External anchors: what this machinery reproduces that it did not produce

An internal consistency check asks the reader to trust us. An external anchor
does not: it is a number somebody else published, that our machinery lands on
without being told to. Every item below is of that kind, and each names where
its receipt lives so the reader can check it.

The ordering is by how little the reader has to take on faith.

**One trap, fixed 2026-08-19.** `fixtures/b006770.txt` carries **20** terms, not
18: the other gates read it as a general a(n) reference and want the extra two,
but **n = 19 and 20 in it are this project's, not OEIS's**. Until that date
`scripts/bfile_gate.py` compared our upload against all twenty and reported the
result as agreement with "the original OEIS terms" — two of which were our own
numbers on both sides. The external check is now scoped to `n <= 18` with the
overlap size pinned, so appending a further term to the fixture cannot quietly
widen the anchor. The live entry was re-checked the same day: revision 44 of
2026-05-30, DATA still 18 terms, `oeis.org/A006770/b006770.txt` still
auto-synthesized from DATA with no author-uploaded b-file, and identical to our
first 18 lines. The fixture's own header now says which lines are which; that
comment-only edit is why its `fixtures/SHA256SUMS` entry was re-pinned, with the
20 data lines verified byte-identical to the previous pin first.

## Tier 1 — published integers, reproduced exactly

| anchor | published by | what we reproduce | receipt | status |
|---|---|---|---|---|
| **A006770, a(1)–a(18)** | OEIS entry, pre-dating this work | all 18 terms, exactly | `fixtures/b006770.txt` lines n≤18; `make gate-bfiles` | **re-checked live 2026-08-19** |
| **A067675 / A067676** | Kotesovec (convex polyominoes by area) | 50 terms each, from the control arm of the king kernel pipeline | `results/convex-polyplets.md` | recorded; not re-run today |
| **A222205** | Sloane 2013, from Bacher | all 23 published terms, extended to 200 | `results/multi-directed.md`, `results/multidirected_terms_n200.txt` | recorded |
| **A187077** | OEIS (column-convex) | the generating function, rediscovered verbatim by Temperley's method | L5 §column-convex | recorded |
| **A053993** | Andrews, Memoirs AMS 301 (1984), `phi_2` | the square lattice's diamond-tip series, to n = 40 | `experiments/cone_order_ideals.py`; L6 §min | recorded |
| **A(n,2n+2) = 1, A(n,2n+1) = 4(n−2)** | Asinowski–Barequet–Zheng | our square-lattice defect column's k = 0 and k = 1 rows | L6 §max | recorded |

## Tier 2 — published constants, reproduced and extended

| anchor | published value | ours | receipt |
|---|---|---|---|
| **Bender's convex-polyomino growth constant** | 2.30914 | same, extended to **121 trusted digits** by the control arm | L5 §μ |
| **Klarner–Rivest constant (A276994)** | ~75 digits | every published digit, from the control kernel's smallest positive zero | `results/convex-polyplets.md` |
| **Kotesovec's amplitude for A067675** | ~71 digits | every published digit, from the same residue formula | same |

The control arm matters more than the king numbers beside it: it shares all its
machinery with the king computation and none of its inputs, so reproducing a
published constant to certified precision tests the pipeline that produced the
uncertified one.

## Tier 3 — published theorems our results land on

- **Richard, arXiv:0704.0716** — the rectangles area limit law `beta_{1,1/2}`
  for convex polygons. Our area-moment work rederived it without knowing, which
  is a collision on priority and simultaneously a check: the king lattice, where
  nothing is solved, lands in the same universality class as the solved square
  case. Enting–Guttmann (1989) cover the square control.
- **Delest–Viennot (1984)** — algebraicity of convex polyominoes by
  perimeter, used here as the *positive control* for the algebraicity guesser
  that produced our king verdicts. A guesser that cannot find a known algebraic
  equation is not evidence about an unknown one.
- **Fortuin–Kasteleyn / Potts** — the second enumeration source's rule is the
  spin representation of `q^{components}`, and the production engine is a
  connectivity-tracking method in the Jensen tradition. Their independence is
  therefore a structural fact about two classical representations of one
  partition function, not a claim about our two programs. See L9.
- **Asinowski–Barequet–Zheng** — the perimeter-defect identity `k = e + 2f` and
  rationality with cyclotomic denominators. The identity licenses our
  enumeration prune, so the prune rests on published mathematics.

- **The square-lattice growth constant, from our own DA code.** The
  differential-approximant spectrum written for A006770, run unchanged on
  A001168's 70 published terms, returns λ = 4.06257 against the published
  ≈4.0625696 — six digits, from code never tuned to that lattice. The same run
  gives θ_square = −0.9995 against θ_king = −0.9997 at matched length, which is
  the universality prediction tested rather than quoted.
  `results/theta-universality.md`.

## Tier 4 — controls that are required to FAIL, and do

These are anchors in the other direction: a method that would prove something
false is run against a case where the truth is published.

- **The λ bound argument on the square lattice.** The elementary encoding that
  gives λ ≤ 12.2 on the king lattice gives λ_polyomino ≤ 4 on the square one,
  against the published λ_polyomino ≈ 4.06 (Barequet–Rote–Shalah). It is run
  there first precisely so that a bound with no published number to check
  against is not the first place the argument is tested. L3 §false starts.
- **The OEIS search pipeline's control query.** `1,2,7,28,120,528,2344,...`
  must hit A005436 exactly, and does; a search apparatus that finds nothing is
  indistinguishable from one that is broken.

## What this list is for

Four uses, in the order they help a reader who has just arrived:

1. It answers "why should I believe the machinery" before the paper asks them
   to believe any new number.
2. Every item is checkable without us. Tier 1 needs a text comparison.
3. It converts three of this week's priority collisions from losses into
   evidence — the collision means somebody else got there first, and it also
   means our route arrived at their answer.
4. It gives the validation chapter an opening that does not depend on
   internal consistency checks, which are the weakest evidence a project can
   offer about itself.

**Not claimed here:** that any of this establishes a(23)–a(40). It does not.
The anchors test the machinery; the terms rest on the provenance table
(`results/provenance-table.md`) and on the second source.
