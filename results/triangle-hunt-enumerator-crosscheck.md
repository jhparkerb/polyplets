# Four independent enumerators reproduce the banked triangle (n ≤ 12)

2026-08-11. The mandatory first task of
`docs/triangle-structure-team-brief.md`: every proposer writes its own
polyplet enumerator from the lattice definition — its own connectivity rule,
its own code — before touching banked data, and compares against the banked
triangle. A disagreement at small n would have been the most important thing
the team could produce.

**Result: zero cell mismatches, all four, all 78 cells with n ≤ 12.**

## What was compared

Banked: `results/ns_a40/perheight/h<H>.out`, loaded and validated by
`experiments/tristruct/triangle.py` (row-sum identity for every n = 1..40,
anchors T(40,40) = 3^39 and T(40,39) = 955·3^36, structural zeros).

| enumerator | source | normalization / method |
|---|---|---|
| `p1_enum.cpp` | Proposer 1 (proof-first) | own |
| `p2_enum.cpp` | Proposer 2 (congruence/valuation) | translation class rep: min row 0, row-0 min col 0; frontier include/exclude recursion; also has a `--sym` mode tallying flip/rotation-invariant animals |
| `p3_enum.cc` | Proposer 3 (slice recurrences) | own |
| `xlat_enum.cpp` | Proposer 4 (cross-lattice) | Redelmeier untried-set over connected sets containing the root, restricted to y > 0 or (y = 0 and x ≥ 0); also does `square` and `tri` lattices |

None of the four read `core/transition.h`, `cpp/strip_tm.cpp`, or any existing
kernel; each states so in its header comment. King adjacency was written from
the definition independently in each (`max(|dx|,|dy|) = 1`, i.e. the 8 king
moves).

## Reproducing

Binaries build into `build/` (never elsewhere). From the repo root:

```
./build/p1_enum 12   > experiments/tristruct/data/p1_king_n12.txt
./build/p2_enum 12   > experiments/tristruct/data/p2_king_n12.txt
./build/p3_enum 12   > experiments/tristruct/data/p3_king_n12.txt
./build/xlat_enum king 12 > experiments/tristruct/data/p4_king_n12.txt
```

then from `experiments/tristruct/`:

```
python3 p1_compare.py data/p1_king_n12.txt 12
```

for each. `p1_compare.py` reports cell mismatches and row-sum mismatches
separately. **Reading note:** `p2` and `p3` emit only `n H count` lines, with
no `n SUM a(n)` line, so their comparison prints 12 row-sum mismatches of the
form `mine=None`. Those are an output-format difference, not a disagreement —
the cell mismatch count is 0 for all four. `p1` and `p4` emit SUM lines and
report 0 mismatches of both kinds.

## Caveat on the shared data file

`experiments/tristruct/data/king_enum_n12.txt` was written by more than one
agent (the path is not proposer-specific and was clobbered). Do not use it to
attribute a result to a proposer; the per-proposer files above were regenerated
from the binaries specifically to remove that ambiguity.

## What this does and does not buy

**Does:** four independently-written connectivity rules, plus the production
engines, agree on every cell out to n = 12. A shared misconception about
king-connectivity would have to survive five independent implementations.

**Does not:** say anything about n > 12. The brief's independence problem
stands — this is a check on the *rule*, not on the enumeration at frontier
sizes. Cells at large n rest on their own provenance
(`experiments/tristruct/README.md` records which rows are real sweeps and
which are wired closed forms).
