# Polyplets

A **polyplet** is a set of cells on the square grid that is connected when
cells touching only at a corner count as joined. Counted by number of cells,
up to translation, they are OEIS [A006770](https://oeis.org/A006770):
1, 4, 20, 110, 638, 3832, …. The published terms stopped at n = 18. This
repository extends the sequence to

    a(40) = 56749893611764175164545926946127

and has a value of a(41) that rests partly on closed forms (see below).

## Results

- **The terms a(19)–a(40)**, in `results/b006770_upload.txt`, with
  a(41) = 393811462683918679824582849262105 in `results/a41/`.
  [`results/confidence.md`](results/confidence.md) says what evidence stands
  behind each term; in short, a(1)–a(22) were computed twice by unrelated
  programs; every entry behind a(23)–a(39) was either recomputed by a second
  program or follows from a closed form fitted to that program's own output,
  which is agreement between formulas rather than a second enumeration.
- **A closed form for the tall part of the count.** If T(n,H) counts polyplets
  with n cells and bounding-box height H, then for H > n/2,
  T(n,H) = P_{n−H}(n)·3^(3H−2n−1) with P_k a polynomial of degree k and
  leading coefficient 25^k/k!. The shape and its range are proved
  ([`docs/proofs/diagonal-law.md`](docs/proofs/diagonal-law.md)) and checked
  in Lean ([`polyplets/README.md`](polyplets/README.md)). This is what made
  the large terms affordable: the tall heights never have to be enumerated.
- **The growth constant** λ = lim a(n)^(1/n) satisfies 6.543 ≤ λ ≤ 9.3154,
  both ends from computations in exact rational arithmetic whose certificates
  are in the repository, and is about 7.110
  ([`results/growth-constant.md`](results/growth-constant.md)).
- **Extensions of five related sequences**: free (A030222), one-sided
  (A030233), bilateral (A030234) and asymmetric (A030235) polyplets, and free
  polyplets that are not polyominoes (A194596)
  ([`results/symmetry-classes.md`](results/symmetry-classes.md)).

[`results/README.md`](results/README.md) lists the other results: arithmetic
of the triangle, the perimeter distribution, subclasses, and routes that were
tried and did not work.

## What has to be trusted

The terms come from computation, and nothing here proves the programs
correct. What the repository offers instead is independent recomputation, of
whole terms up to n = 22 and of individual entries beyond, plus checks against
structure that is known by proof. `results/provenance-table.md` lists, for each
of the 820 entries T(n,H) with n ≤ 40, which independent computations agree
with it. Three entries were enumerated by only one program.

The Lean development proves the shape of the closed form and its range from
the definitions, using only Lean's standard axioms. Fixing the polynomials P_k
for k ≤ 18 needs 32 counts supplied by the enumeration as a hypothesis; the
Lean files say which.

## Reproducing

    make                     # builds what each check needs and runs the checks
    scripts/term.sh 26       # computes a(1)..a(26), checking a(1)..a(25) against the stored values

On a 32-core machine `make` takes about 7 minutes and `scripts/term.sh 26`
about 23 seconds. `scripts/term.sh` enumerates the short heights and takes
the tall ones from the closed forms. The large terms took days on machines
with hundreds of gigabytes of memory and disk; `results/ns_a40/PROVENANCE.md`
records how a(40) was run. Two unrelated algorithms, with no closed forms
involved:

    build/redelmeier square8 12      # Redelmeier enumeration, a(1)..a(12)
    make gate-kink-oracle    # the transfer matrix enumerating every height, a(1)..a(18)

The second takes about a minute on 8 cores and compares its sums with the
published a(1)..a(18).

## Layout

| where | what |
|---|---|
| `results/` | the counts, the height triangle, per-term records, and notes on what they show |
| `docs/proofs/` | proofs of the closed forms and the upper bound on λ |
| `docs/` | how the enumerator works, and notes for maintaining the repository |
| `polyplets/` | the Lean 4 formalization |
| `paper/` | the technical report, and six papers written by a language model (labelled as such) |
| `core/`, `orchestrator/`, `worker/` | the production transfer-matrix enumerator (Go and C++) |
| `cpp/` | other C++ programs: the Redelmeier enumerator, the strip and coloring recounts, symmetry counts |
| `scripts/` | drivers and assembly scripts, and the simple reference counters the checks compare against |
| `experiments/` | one-off calculations behind particular statements in `results/` |
| `tests/` | the checks `make` runs; most include a control that plants an error and must fail |
| `fixtures/` | published b-files the checks compare against |
| `oeis/` | drafts of OEIS submissions, none submitted |
| `literature/` | an index of the literature consulted |

<!-- AI-use paragraph: to be written by Jason Parker. -->

## License

Apache License 2.0 (`LICENSE`), covering code, proofs and documents. The
papers indexed in `literature/` are other people's work and are not
distributed here.
