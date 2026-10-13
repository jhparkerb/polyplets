# The coloring recount

This directory holds the output of the second enumerator, `cpp/motley_par.cpp`
(the exact source of the n ≤ 40 rows is `cutcount_b1.cpp.59e90660`). It shares
no code with the transfer-matrix engine that produced `results/triangle.txt`,
and it never decides whether a set of cells is connected.

## The method

Let `A_n(q) = Σ_S q^{c(S)}`, summed over n-cell subsets S of a strip of
height H and weighted by the number of king-connected components c(S). The
number of connected subsets is the coefficient of `q^1`. The program computes
`A_n(q)` modulo `q^2` by a frontier dynamic program over partitions of the
frontier cells by color; when two components meet, the term is zeroed rather
than joined. Connectivity is read off a coefficient at the end. The identity
that makes this the count is proved in `docs/proofs/cutcount-identity.md`.

The program computes `C_H(n) = Σ_{h ≤ H} (H−h+1) T(n,h)`, the number of
placements of n-cell polyplets of height at most H in a strip of height H. The
triangle is recovered by the second difference
`T(n,H) = C_H(n) − 2C_{H−1}(n) + C_{H−2}(n)`.

## Files

| file | what |
|---|---|
| `rows/C<H>.out` | `n C_H(n)` for H = 1..18, n ≤ 40 |
| `residues/C18.p<prime>.out` | C_18 modulo five primes: four are combined by the Chinese remainder theorem, the fifth must agree with the result |
| `rows41/C<H>.out` | a second run, H = 1..19, n ≤ 41 (see `rows41/README.md`) |
| `residues41/C<H>.p<prime>.out` | that run's residues, nine primes per height, the largest held out |
| `rows41/run/` | that run's timings and console logs |
| `cutcount_b1.cpp.59e90660` | the exact source that produced `rows/` |

The two sets cannot be mixed in one second difference: every `C_H` in a
difference must come from the same run.

## What the rows establish

Every entry T(n,H) with H ≤ 19 and n ≤ 40 recomputed from these files equals
`results/triangle.txt`. `make gate-cutcount-assembly` repeats that
comparison, and re-derives each held-out prime's agreement from the stored
residues. `scripts/provenance_table.py` reads the reach (H ≤ 19) from these
files rather than taking it as given.

## A caveat about the source

The sha256 of the source that produced `rows/` is
`59e90660b42a0d94ceae5459287db35b4d93f87a5e62753ccd549235edaa8d3d`. It matches
no committed version of the program; the nearest committed version differs
from it by the removal of a modular-arithmetic mode, with the counting
recursion unchanged. That is why the source file is stored here beside its
output.
