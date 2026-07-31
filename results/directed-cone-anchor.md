# Cone anchor: the enumerate+filter pipeline against a closed form (2026-07-31)

Closes the "validation hook (feasible, not yet built)" of
[directed-king-animals.md](directed-king-animals.md). Filtering the fixed
king-animal (polyplet) enumeration down to Bacher's DIRECTED king animals
reproduces **A047781** exactly, and A047781 has an exact closed form -- so the
reference side is a formula, not a second enumeration, and is available at any n.
(The near-diagonal `P_k(n)` of [diagonal-closed-forms.md](diagonal-closed-forms.md)
are the project's other closed-form reference; this one anchors the *full-count*
enumerate-and-filter path rather than a band.) Tools: `cpp/directed_cone_anchor.cpp` ->
`build/directed_cone_anchor` (make target), driver
`experiments/directed_cone_anchor.py`, log
`experiments/directed_cone_anchor.log`.

## The object, exactly as the source defines it

Forward cone = the five directions `{W, NW, N, NE, E}` = `(-1,0) (-1,1) (0,1)
(1,1) (1,0)`; horizontal steps count as forward. Source = the
**leftmost-bottommost** cell. An animal is directed iff every cell is reachable
from that source by cone steps *staying inside the animal*. Counted up to
translation.

The bottom-row gotcha the note flags is not an extra rule -- it is a
**consequence**, and that is what makes it a good control. No cone step
decreases y, so a bottom-row cell can only be entered from another bottom-row
cell, via W/E; hence the bottom row must be one contiguous run, and every cell
of that run has the same forward-reachable set. Bacher's canonical source choice
is therefore not a choice at all (no source-choice double count), exactly as the
note claims.

## Three enumerations, one closed form

| route | what it is | reach |
|---|---|---|
| **filter** | Redelmeier untried-set DFS over ALL fixed king animals, O(cells) BFS directedness test applied to every animal generated | n <= 15 |
| **cone growth** | same DFS with the step set restricted to the cone (bottom row may not grow west), no filter -- each directed animal generated once | n <= 17 |
| **brute** | from-scratch Python: frozenset growth + explicit translation canonicalisation + dict reachability; shares no code with the C++ | n <= 9 |
| **closed form** | `D(t) = 1/4 ((1+t)/sqrt(1-6t+t^2) - 1)`, three independent evaluations | n <= 25 |

The closed form is itself computed three ways that must agree before it is used
as a reference: the Legendre recurrence `(n+1)P_{n+1}(3) = 3(2n+1)P_n(3) -
n P_{n-1}(3)` with `d(n) = (P_n+P_{n-1})/4`; an exact `Fraction` series square
root of `1/(1-6t+t^2)` (naive inversion `c_n = 6c_{n-1} - c_{n-2}`, then the
standard series-sqrt recurrence); and the closed binomial sum for the central
Delannoy numbers `P_n(3) = D(n) = Sum_k C(n,k) C(n+k,k)`. All three agree
term-by-term for n <= 25, and agree with the 8 published A047781 terms.

## Result

**Zero mismatches, every route, every n in range.**

| n | A006770 (all fixed king animals) | filter -> directed | cone growth | closed form `[t^n] D(t)` |
|---:|---:|---:|---:|---:|
| 1 | 1 | 1 | 1 | 1 |
| 2 | 4 | 4 | 4 | 4 |
| 3 | 20 | 19 | 19 | 19 |
| 4 | 110 | 96 | 96 | 96 |
| 5 | 638 | 501 | 501 | 501 |
| 6 | 3832 | 2668 | 2668 | 2668 |
| 7 | 23592 | 14407 | 14407 | 14407 |
| 8 | 147941 | 78592 | 78592 | 78592 |
| 9 | 940982 | 432073 | 432073 | 432073 |
| 10 | 6053180 | 2390004 | 2390004 | 2390004 |
| 11 | 39299408 | 13286043 | 13286043 | 13286043 |
| 12 | 257105146 | 74160672 | 74160672 | 74160672 |
| 13 | 1692931066 | 415382397 | 415382397 | 415382397 |
| 14 | 11208974860 | 2333445468 | 2333445468 | 2333445468 |
| 15 | 74570549714 | 13141557519 | 13141557519 | 13141557519 |
| 16 | -- | -- | 74174404608 | 74174404608 |
| 17 | -- | -- | 419472490257 | 419472490257 |

- **filter vs closed form: agree, n = 1..15.**
- **cone growth vs closed form: agree, n = 1..17.**
- **filter vs cone growth (engine cross-check): agree, n = 1..15.**
- **brute vs both: agree, n = 1..9.**
- unfiltered totals vs A006770: agree, n = 1..15 (the enumerator itself is right).
- closed form vs published A047781: agree on all 8 published terms.

Reference terms: no b-file for A047781 or A055834 exists in `fixtures/`, so the
published terms are hard-coded in the driver with provenance -- A047781's first 8
from [directed-king-animals.md](directed-king-animals.md) (verified there against
Bacher arXiv:1301.1365 + OEIS), A055834's first 6 from
[king-subfamilies.md](king-subfamilies.md) (verified there against the OEIS entry
to n=15). The A006770 control column comes from `fixtures/b006770.txt`.

## RED controls (the filter is discriminating, not vacuous)

A filter that passed everything would also "agree" with a sequence. Three
controls, all fail-closed (an empty comparison is a failure, and the two
divergence checks FAIL if they do not diverge):

| control | what changed | n=1..6 | vs A047781 |
|---|---|---|---|
| **A: wrong cone** | 4-step `{N, NE, E, SE}`, source = bottommost of leftmost column | 1, 4, **18**, 85, 413, 2044 | **diverges at n=3, 18 vs 19** |
| **B: bottom row waived** | same 5-step cone, BFS seeded from *every* bottom-row cell | 1, 4, **20**, 106, 576, 3179 | **diverges at n=3, 20 vs 19** |
| C: no filter | filter removed entirely | 1, 4, 20, 110, 638, 3832 | = A006770, diverges at n=3 |

All three run through the *same* enumeration and the *same* filter machinery,
differing only in the step set and the source rule -- so a divergence is
attributable to the perturbation and nothing else. The n=3 split is the sharpest
case: the single 3-cell animal `{(0,0), (1,1), (2,0)}` has a *split* bottom row,
so it is multi-directed but not directed; control A drops it plus one more,
control B keeps it.

Control A reproduces **A055834** and, run to n=14, independently confirms the
terms `36196706` (n=12), `187938842` (n=13), `978599560` (n=14) that
[king-subfamilies.md](king-subfamilies.md) obtained by *direct cone growth* in
`experiments/directed_halfplane.cpp` -- here by the entirely different route of
enumerating all 11.2 billion fixed king animals and filtering. Control B is a
genuine third sequence (1, 4, 20, 106, 576, 3179, 17736, 99748, ...), matching
neither A047781 nor A006770.

## Cost and reach (honest)

Measured on gympie (macOS, 8 threads). Work scales as A006770 (~6.7x/term) for
the filter route and as A047781 (~5.83x/term) for cone growth:

| run | mode | n | wall | CPU | peak RSS |
|---|---|---:|---:|---:|---:|
| filter | `dir5` | 15 | 457.6 s | 3484 s | 1.8 MB |
| cone growth | `cone5` | 17 | 194.8 s | 1505 s | 1.8 MB |
| control A | `dir4` | 14 | 81.0 s | 633 s | 1.8 MB |
| control B | `dir5nb` | 14 | 84.6 s | 629 s | 1.8 MB |
| brute | Python | 9 | 21.6 s | 21.5 s | -- |

Total 13.6 min wall on 8 threads, gympie, 2026-07-31.

n=16 by the filter route is ~1 hour and n=18 by cone growth ~40 min; neither was
run. The reach is what ~14 minutes of one laptop buys. It is nonetheless the
first check in the project that could in principle be pushed to *any* n, because
the reference side is a formula rather than a second enumeration.

## Scope statement -- what this does and does not validate

This validates the **enumeration + filter pipeline** against an exact closed form
on a *subfamily*: the canonical-translate Redelmeier DFS, the cell-set
bookkeeping, the sharded parallel decomposition, and a per-animal predicate
evaluated on every object generated. It is corroboration for the machinery.

It is **not** a check of `a(n)` itself. The frontier engine (`ns`, the kink
transfer matrix) shares no code with this tool, and directedness is precisely the
property that *discards* the hard part -- the connectivity wall
([[algorithmic-levers-dead-connectivity-wall]]) -- so a directed anchor cannot
exercise what makes the undirected count hard. Read it as: a third, closed-form,
orthogonal witness that the enumerate-and-filter idiom in this repo does what it
says, sitting alongside the strip-TM and g2 second sources rather than replacing
them.

## Reproduce

```
make build/directed_cone_anchor
python3 experiments/directed_cone_anchor.py --dir5 15 --cone5 17 --ctrl 14 \
    --threads 8            # ~14 min, the run recorded above
python3 experiments/directed_cone_anchor.py --brute 9 --dir5 11 --cone5 12 \
    --ctrl 11 --threads 8  # ~40 s, adds the from-scratch Python cross-check
```

Provenance caveat: the binary's baked stamp reads `ce506bc-dirty`. The tree was
dirty from concurrent work by other streams (and jasonp's untracked `paper/`
working files) at build time, not from an uncommitted change to this tool. The
source is `cpp/directed_cone_anchor.cpp`, unmodified since that build. Left
uncommitted deliberately: other streams had in-flight edits in the tree, and
sweeping them into a commit is jasonp's call, not this stream's.
