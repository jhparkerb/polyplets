# How far each term can be trusted

There are two ways to be confident in a count like a(40). One is to compute it
twice with programs that share no code and no method, so that a bug in one
would have to be matched by the same bug in the other. The other is to compute
it once and check it against structure that is known independently: closed
forms, congruences, row sums. The second catches gross errors but not every
subtle systematic one. This note says which kind of evidence stands behind
each term.

## Summary

| terms | evidence |
|---|---|
| a(1)–a(22) | two programs with no shared counting logic agree on the whole term |
| a(23)–a(39) | every entry of the height triangle is either recounted by a second program or given by a closed form whose constants come from that program's own entries |
| a(40) | heights 1–19 recounted by a second program; heights 20 and 21 enumerated by the main program only; heights 22–40 from the closed forms. Heights 20–40 are also reproduced by closed forms refitted to the second program's entries, which is agreement between formulas, not a second enumeration |
| a(41) | heights 1–19 recounted by a second program; height 20 enumerated by the main program only, and equal to the closed form's prediction; heights 21–41 from closed forms |

## How the terms were computed

a(n) is the sum over heights H of T(n,H), the number of polyplets with n cells
whose bounding box has height H. The production program is a column-by-column
transfer matrix that computes T(n,H) for every n up to a given maximum; each
run enumerates every height below the closed-form range described next, and
reproduces every earlier term (`docs/engine-record.md`).

The tall heights are not enumerated. Above H > n/2 the triangle satisfies
T(n,H) = P_{n−H}(n)·3^(3H−2n−1), where P_k is a polynomial of degree k with
leading coefficient 25^k/k!. The shape of this formula and the range where it
holds are proved (`docs/proofs/diagonal-law.md`, and in Lean, see
`polyplets/README.md`); two constants per level are not, and are fixed from
enumerated entries.

## The independent checks

**Redelmeier enumeration, n ≤ 22.** A cell-set-growing enumerator, run in
24,000 disjoint pieces on three machines of different architectures,
reproduced every row n ≤ 22 exactly. It shares no counting logic with the
transfer matrix. Its cost grows with the number of polyplets, so whole-term
checks stop at n = 22 (`results/redelmeier_row22/`, `make gate-redelmeier`).

**A strip transfer matrix, H ≤ 14.** A second transfer matrix computes, for a
strip of fixed height, the number of placements of polyplets of height at most
that height, from which the triangle follows by a second difference. All 469
entries with H ≤ 14 and n ≤ 40 agree. It decides connectivity by the same
union-find rule as the main program, so it would share a misconception about
king connectivity (`results/second-sources.md`).

**The coloring recount, H ≤ 19.** A third program counts subsets of a strip
weighted by their number of connected components and reads the connected
count off a coefficient. It never decides connectivity. Every entry with
H ≤ 19 and n ≤ 40 agrees with the main program, as do the 19 entries of row 41
at those heights (`results/coloring-recount/PROVENANCE.md`).

**Withheld entries.** Each closed form was fitted on earlier terms and then
compared with an entry enumerated later: P_15, P_16, P_17 and P_18 predicted
T(33,18), T(35,19), T(37,20) and T(39,21) exactly.

**Fits from below.** Below the range where the closed form holds, the deviation
from it is itself computable (`results/below-onset.md`). That turns short, cheap
entries into equations for the same constants. Every level k = 2..19 re-derived
this way agrees with the level used, and 189 enumerated entries are predicted
from shorter ones with no error (`results/below-onset-fit.md`). These fits share their
correction tables with the main route, so they are a consistency check, not an
independent one.

**A congruence on every entry.** Counting the polyplets fixed by each subgroup
of the square's symmetry group gives a(n) mod 4 and T(n,H) mod 2 by a separate
enumeration on a much smaller domain. All 40 terms and all 820 entries agree
(`results/symmetry-classes.md`). The same congruence exposed an error in the
published square-lattice count A(67) in 2026 (arXiv:2610.10632).

## What is not claimed

- Not that a(23)–a(40) are confirmed by two programs as whole terms. That
  frontier is n = 22.
- Not that every entry has two enumerations. Three entries, T(39,20),
  T(40,20) and T(40,21), were enumerated by only one program, and carry only
  the mod-4 congruence and agreement with the refitted closed forms
  <!--q:congruence_only.count@19=3--><!--q:congruence_only.cells@19=(39,20),(40,20),(40,21)-->.
  `results/provenance-table.md` lists the evidence for every entry.
- Not that the strip transfer matrix is fully independent; it shares the
  connectivity rule.
- Not that a(41) carries a(40)'s evidence. Its height 20 has one enumeration
  and one prediction, and heights 21–41 are formula
  (`results/a41/PROVENANCE.md`).

## When a formula may stand in for an enumeration

A value assembled partly from closed forms is accepted when the shape of the
formula is proved, the entry lies where the formula is proved to hold, and the
constants are fixed from enumerated entries with at least one enumerated entry
held back and reproduced. a(41) meets all three. The diagonal-mirror count
D(33), which four of the related symmetry sequences need, does not: the range
where its formula holds is observed, not proved
(`docs/proofs/dm-diagonal-law.md`), so D(33) is kept out of the b-files.

## Where an error could still hide

The closed forms for the tallest levels rest on correction tables computed to
a certain size and used slightly beyond it. Two of the three tables involved
have been derived twice by different code. The third is checked by a fourth
table at the next depth, which gives the top level a third data point; the
three agree, and `make gate-below-onset-fit-pairs` fails if they stop. An integer
error in that table would otherwise pass: an error of 9 in one entry moves
a(41) by 9 and survives the integrality check.
