# Determining the diagonal formulas from entries below their onset

Each diagonal formula P_k of the polyplet triangle carries two constants. The
rule used through a(40) fixed them from the two tallest entries on the
formula's diagonal, the most expensive entries in the whole enumeration. The
same two constants can be fixed from entries below the formula's onset (the
smallest n at which the formula holds), once each such entry is corrected by
an exactly known defect. This is how a(41) was computed. The results are of
four grades. Proved: the formula's shape, its onset, and the
two-constants-per-level statement, in `docs/proofs/` (the last in Lean).
Exact and checked: the defects D_j for depths 1 to 5, computed by a program
that never reads the triangle, and reproducing every recorded entry at
k <= 19. Computed and checked: a(41), with heights 1 to 20 enumerated directly
and heights 21 to 41 from the formulas; a(n) for n <= 40 rebuilt with no input
from the main enumeration program. Measured: the cost of each depth table, the
cost of a fixed-height enumeration as the maximum size grows, and the identity
itself on the square lattice against published counts. Two routes are closed
with their obstructions: freeing the formulas from enumerated entries
altogether, and depths 8 and 9.

## Definitions

- **T(n,H)** is the number of fixed polyplets (king animals) with n cells whose
  bounding box has height H; T is the triangle, stored as `results/triangle.txt`
  for n <= 40 and as per-height rows `h<H>.out`. A value of T is an entry.
- **The main program** is the transfer-matrix enumeration `orchestrate`
  (`orchestrator/`), which produced every T(n,H) to n = 40 and the enumerated
  heights of row 41. Its formula table `diagCoeffTable` in
  `orchestrator/sweep.go` holds P_k for k <= 19, each fitted from two entries;
  the a(40) run wrote formula values for heights H >= 22 instead of
  enumerating them (`results/ns_a40/PROVENANCE.md`).
- **The coloring recount** (`cpp/motley_par.cpp`, records in
  `results/cutcount_b1/`) counts C_H(n) by coloring and never decides
  connectivity. T(n,H) = C_H(n) - 2 C_{H-1}(n) + C_{H-2}(n)
  (`docs/proofs/cutcount-identity.md`). It covers H <= 18 at n <= 40
  (`results/cutcount_b1/rows/`) and H <= 19 at n <= 41
  (`results/cutcount_b1/rows41/`). A value derived with no input from the main
  program is called rule-independent, because the coloring recount never
  decides connectivity at all.
- **The strip engine** is a third program covering H <= 14 at n <= 40
  (`results/second-sources.md`).
- **Level k = n - H.** The diagonal formula (`docs/proofs/diagonal-law.md`)
  says T(n, n-k) = P_k(n) 3^(n-1-3k) for n >= 2k+1, with P_k a polynomial of
  degree k. The smallest n at which it holds, 2k+1, is the onset; the onset
  is proved sharp for every k. Entries with n >= 2k+1 are at or above onset.
- **The product form** (`docs/proofs/product-form.md`, Lean-complete) says
  P_k(n) = [y^k] exp(sum_j (a_j + b_j n) y^j), so level k adds exactly two
  rational constants (a_k, b_k) and P_k(n) = known_k(n) + a_k + b_k n with
  known_k fixed by the lower levels.
- **Depth j** of an entry below onset is j = 2k+1-n; the depth-j entry of
  level k is T(2k+1-j, k+1-j), at height k+1-j.
- **The defect D_j(k)** is the rational correction in the identity of the next
  section. Depth 1 comes from the gap walk `experiments/depth1_gap_walk.py`;
  depths 2 to 5 from the bounded-excess family enumeration
  (`cpp/severance_w3_families.cpp`, assembled by
  `experiments/severance_w3_depths.py`; derivation in `results/below-onset.md`).
  Depth j needs the family table at excess e <= j-1. The tables
  `results/severance_w3_families_K<K>_e<e>.txt` carry three weight columns,
  `sig`, `bb`, `pp`, per (e, k). None of this reads the triangle or any P_k.
- **The cluster-weight enumeration** (`cpp/severance_w1.cpp`,
  `results/severance_w1_weights_k9.txt`) gives P_1 to P_9 with no triangle
  input.
- **The assembly** is the set of formulas P_k with their constants fixed,
  used to supply the entries of a row that were not enumerated.
- **The onset rule** fixes level k from its two entries at n = 2k+1 and
  n = 2k+2, at heights k+1 and k+2. It is the rule the formula table was built
  by.

## The identity, and the reach it gives

For level k and depth j >= 1,

    T(2k+1-j, k+1-j) = P_k(2k+1-j) 3^(-(k+j)) + D_j(k).

D_j(k) has denominator dividing 3^(k+j); checked, not assumed, for j <= 4 and
k <= 21 (`experiments/undertow_congruence_gate.py`). P_k(n) is linear in
(a_k, b_k) with coefficient 1, so each below-onset entry with an exact D_j is
one linear equation in the two constants of its level, and two entries at
distinct depths determine the level; the 2x2 system at distinct n is never
singular. The depth-j entry is j rows shorter than the onset rule's. No new
theorem is involved: the content is the choice of entries.

**Reach.** With exact defects through depth J and every height H <= Hs
enumerated at maximum size N, level k is determined when two depths
j1 < j2 <= J satisfy k+1-j <= Hs, so

    k_max = Hs + J - 2,      rows complete for  n <= 2 Hs + J - 1.

Both determining entries lie inside the enumeration, since
2k+1-j <= k + Hs <= 2Hs + J - 2 <= N. The onset rule gives n <= 2 Hs.
Each unit of depth buys one row; each unit of height buys two.

| term | height needed, onset rule | height needed with J = 4 |
|---|---|---|
| a(40) | 21 | 19 |
| a(41) | 21 | 19 |
| a(42) | 22 | 20 |

What the two removed heights cost in the a(40) run
(`results/ns_a40/PROVENANCE.md`, `results/ns_a40/rundir_size.log`):

| phase | heights | wall | cores | cpu (s) | disk peak |
|---|---|---|---|---|---|
| A | 1..19 (and 22..40 by formula) | 6.3 h | 80 | 871,963 | 69.2 GB |
| B | 20 | 9.6 h | 48 | 1,116,858 | 172.3 GB |
| C | 21 | 36.4 h | 32 | 3,329,644 | 363.4 GB |

## Checks on the recorded triangle

All by `experiments/undertow_pin.py`, in exact rational arithmetic; every
comparison is equality of rationals.

- **Consistency of the formula table.** At every level k <= 19, P_k minus its
  lower-level part is linear in n. The extraction raises otherwise.
- **Re-derivation (`--verify`).** The 18 levels k = 2..19 are re-derived
  exactly from below-onset entries and the defects, without the entries they
  were fitted from. Level 19 comes back from T(38,19) and T(37,18), without
  T(39,20) or T(40,21).

| depths allowed | depth pairs | wrong |
|---|---|---|
| j <= 4 | 100 (1 skipped) | 0 |
| j <= 5 | 160 | 0 |

  Pairs share entries: a level with c usable entries carries c - 2 independent
  checks, about 36 in all at j <= 4.
- **Negative controls (`--selftest`).** A perturbed D_j breaks the solution;
  the same equation offered twice is refused as singular; a corrupted lower
  level breaks the solution.
- **Audit (`--audit`).** Each level is determined from its two shortest
  usable entries, then every recorded entry at or above onset on its diagonal
  that it did not use is predicted.

| entries predicted | of which enumerated (H <= 21) | of which formula values written by the a(40) run (H >= 22) | wrong |
|---|---|---|---|
| 342 | 189 | 153 | 0 |

  The 153 are identities: all 171 recorded in-onset entries at H >= 22 equal
  the formula table's evaluation, and the extraction and the product form are
  exact inverses, so any assembly built on the table's levels evaluates to
  the same polynomial. The 189 include T(39,20) and T(40,21), the two entries
  P_19 was fitted from, predicted from a level 19 determined at H <= 18
  (depths 2, 3) or at H <= 17 (depths 3, 4). Levels 3 to 17 of the table each
  had an entry withheld and reproduced when they were fitted. Level 18's
  holdout, T(39,21), was enumerated later, in the a(40) run; level 19 has
  none apart from this. Levels through 15 (depths 2, 3) or 16 (depths 3, 4)
  are determined at H <= 14, inside the strip engine's range.
- **"Shorter" is per level, not transitive.** The audit takes lower levels
  from the formula table, and P_18 embeds T(38,20), so the audit's prediction
  of T(39,20) uses an equal-height entry through level 18. It never uses the
  same entry. The transitive statement is the rule-independent assembly of the
  next section.
- **Prediction past the table (`--predict`).** Level 20 is determined from
  T(40,20), T(39,19), T(38,18) with three depth pairs (two independent checks)
  agreeing, and predicts

      T(41,21) = 12639811314502944123098075912198
      T(42,22) = 66507597655339889181525572632880

  The line "T(40,21) k=19: match" that this mode prints is worth nothing:
  T(40,21) is one of P_19's own fitting entries, and a two-constant exact fit
  reproduces its fitting data.

## a(n) rule-independent for n <= 40

`experiments/undertow_ri.py` answers each row with an assembly built from
nothing the main program produced, excluding the row from its own determining
set: levels 1..9 from the cluster-weight enumeration through
`experiments/severance_w1_assemble.py`; levels 10 and up from the coloring
recount's entries, every determining entry at H <= hmax; D_j for j <= 4; the
product form. The main program's triangle and the OEIS b-file appear only as
comparison targets. Every input was traced to its file; none comes from the
main program.

| rows from | hmax | rows | result |
|---|---|---|---|
| `results/cutcount_b1/rows/` | 18 | 19..39 | complete; every entry agrees; every sum matches a(n) |
| same | 18 | 40 | complete except T(40,19) |
| `results/cutcount_b1/rows41/` | 19 | 39, 40 | complete; sums match |
| same | 19 | 41 | complete; a(41) as below |

At hmax 18, level 20 is determined from the single pair (37,17), (38,18),
with no check at its own level; its values of T(39,19) and T(40,20) agree with
the main program. The coloring recount and the main program agree on all 720
shared entries at H <= 18; the new content is the 173 entries at H > 18 of
rows 30..40 that the assembly reproduces. The script fails on rows <= 18 (an
empty formula band); those rows reduce to the 720-entry agreement.

T(40,19), the one entry of row 40 the assembly could not reach from H <= 18,
was enumerated by the coloring recount in its run at maximum size 41 (nine
primes per height, one held back to predict every entry, about 22 hours;
`results/cutcount_b1/rows41/README.md`):

    T(40,19) = 3247572468599336484342102174163

equal to the main program's entry. Which entries of row 40 still have no
direct enumeration by a second program is recorded in
`results/residual-cells.md`.

## a(41)

    a(41) = 393811462683918679824582849262105

Record: `results/a41/PROVENANCE.md`. Assembler: `experiments/undertow_a41.py`.

| heights | source | run |
|---|---|---|
| 1..19 | main program, 40 cores, 4.72 h, cpu 605,643 s, rss 557 MB | 2026-08-20 |
| 20 | main program, 76 cores, 9.63 h (section below) | 2026-09-05 |
| 21..41 | the assembly: k <= 19 from the formula table, level 20 determined below onset; T(41,21) is level 20 exactly at onset | |

The assembly also gives T(41,20), as level 21 at depth 2, carrying
D_2(21) = 1534183878653401344302049616588 / 3^23; it equals the enumerated
value (below).

**Checks the assembler refuses without.**

- Every height 1..41 accounted for once.
- Edges exact: T(41,41) = 3^40 and T(41,40) = (25n - 45) 3^37.
- The enumeration at maximum size 41 reproduces every recorded entry at
  n <= 40 it touches: 760 entries with heights 1..19, 800 with height 20,
  0 disagree, at least 200 required. Same program at a different maximum
  size, so a regression, not a second count.
- A separate assembly with row 40 excluded from its own determining set
  reproduces the 21 entries of row 40 at H >= 20 and re-sums the row to
  a(40) = 56749893611764175164545926946127. Of the 21, one is a real check,
  T(40,20), predicted from a level 20 determined at H <= 19; T(40,21) is
  P_19's fitting entry; the 19 at H >= 22 are formula identities.
- Growth: a(41)/a(40) = 6.9394 after 6.9212, 6.9261, 6.9308, 6.9352, with
  successive differences 0.0049, 0.0047, 0.0044, 0.0042.

Two limits of these checks. "a(40) comes out of heights 1..19 alone" holds
only when composed with `--verify`; the assembler alone demonstrates it modulo
the formula table. And the same script run at n = 39, 38, 37 with the height
cap at 19, 18, 18 contains no below-onset determination at all: the loop over
new levels is empty because the table already reaches k = 19, and the cap
constrains newly determined levels only, so those rows consume constants
fitted to entries above their stated cap (a(39)'s height-20 value is T(39,20)
through P_19's fit). In the row-40 dry run the check of the enumeration
against the recorded triangle compares a directory with itself; the same
check in the real run is genuine.

**Independent recount.** `experiments/lane_b_a41_recount.py` rebuilds the
term by a route chosen to differ wherever it can: levels 1..19 fitted from
their two onset entries in `results/triangle.txt` rather than read from the
table; its own polynomial representation, product-form recurrence, solver and
assembly loop; D_j imported only at k >= 20 and first checked at every k <= 19
against its own extraction from the recorded entries; level 20 determined
from depths (1, 2) with depths 3 and 4 withheld and reproduced.

    589 enumerated entries vs the recorded triangle: 0 mismatch
    342 in-onset entries predicted by anchor-fitted levels k <= 19: 0 wrong
    70 imported D_j(k), k <= 19, vs own extraction: 0 wrong
    a(41) recount: AGREE

It is a second implementation, not a second count. It retires assembly,
transcription and arithmetic error across two disjoint code bases. It shares
with the assembler the enumerated files, the product form, D_j at k = 20 and
21, and level 21's determining entries T(40,19) and T(39,18).

**Level 21.** With depths j <= 4, level 21 has one determining pair, T(40,19)
and T(39,18), and no check at its own level; level 20 has 6 pairs and 5
checks. What the depth-4 assembly rests on with a single computation behind
it is three integers, `sig`, `bb`, `pp` at e = 3, k = 21 of
`results/severance_w3_families_K22_e3.txt`, plus the two determining entries:
the k = 22 row is truncated away by `D_series(4, 21)` and the k = 20 row is
checked by level 20's pair agreement. The congruence gate below guards only
the fractional part of D_4(21): measured on a shadow copy of the table,
`sig[3][21] + 9` leaves the congruence gate green and moves the depth-4
assembler's a(41) by exactly 9, because a shift of Delta in D_4(21) moves
T(41,20) by 9 Delta and every single-entry error enters D_4(21) with a
coefficient in (1/9) Z.

Depth 5 closes it. `results/severance_w3_families_K21_e4.txt` supplies D_5,
and level 21 gains T(38,17), an entry the coloring recount covers:

    python3 experiments/undertow_a41.py --jmax 5 --perheight results/a41
    level k=20 determined from (36,16) (37,17) (38,18) (39,19): 6 pairs, 5 independent checks
    level k=21 determined from (38,17) (39,18) (40,19):         3 pairs, 2 independent checks

`pp[3][21]` enters D_4(21) but not D_5(21), and `sig`, `bb` enter the two
with different coefficients, so any single-entry error in that row makes the
pairs disagree and the build refuses. `make gate-undertow-pairs`
(`experiments/undertow_pairs_gate.py`) rebuilds the depth-5 assembly with the
determining entries and pair counts fixed in the check, requires a(41) from
`results/a41/h*.out` plus the assembly to equal the value above, and carries
six negative controls: the +9 mutation end to end, `bb` and `pp` at (3, 21),
the e = 4 row of the K21_e4 table, a corrupted determining entry, and the
enumerated T(41,20) shifted by 1 in a shadow copy of `results/a41`.

Three pairs agreeing is agreement between fits that share D_j(20..21) and the
product form. The check that crosses assumption families is an enumeration of
T(41,20).

**The height-20 enumeration.** `scripts/dalby_a41_h20.sh`, rev
`b88b38bc5`, 76 cores, nothing injected from the formula table; 2026-09-05,
11:41 to 21:19 EDT, exit 0.

| wall | cpu | rss | frontier peak |
|---|---|---|---|
| 34,678.8 s (9.63 h) | 1,766,882 s | 814.7 MB | 129,487,745 records at column 7 |

The disk peak was not recorded. Per-column profile:
`results/a41/h20_cost_profile.tsv`.

    T(41,20) = 18004779862205054677763902712770    enumerated, results/a41/h20.out
    T(41,20) = 18004779862205054677763902712770    the assembly, level 21 at depth 2

Column 20 of the run agrees with the recorded triangle on all 40 entries at
n <= 40. Reassembled with the enumerated height, a(41) is unchanged, 800
entries agree, and the term no longer uses P_21 at all. What does not change:
heights 21 to 41 are formula values, and the coloring recount stops at
height 19, so T(41,20) has one enumeration and one prediction behind it.
`results/confidence.md` is the plain statement of how far the term is trusted.

## What an agreement is worth

Before the runs above, T(40,19) was the only entry of row 40 without a
rule-independent value. It sits on level 21 at depth 3:

    T(40,19) = P_21(40) 3^(-24) + D_3(21).

Its value is fixed by the levels k <= 20, the constants (a_21, b_21), and
D_3(21), so only level-21 entries bear on it, one per row.

| row | level-21 entry | depth | status before the runs below |
|---|---|---|---|
| 39 | T(39,18) | 4 | enumerated by both programs |
| 40 | T(40,19) | 3 | main program only |
| 41 | T(41,20) | 2 | not enumerated |
| 42 | T(42,21) | 1 | not enumerated |
| 38 | T(38,17) | 5 | both programs; usable once D_5 exists |

Two goods are held apart: validation, where the main program's T(40,19) is
checked against something it did not feed; and rule-independence, where a
value for T(40,19) is derived with no main-program input. Every route is a way
of buying a third level-21 equation.

| route | what it produces | buys | outcome |
|---|---|---|---|
| height 20 at size 41 | T(41,20); level 21 gets pairs (2,3), (2,4), (3,4) | validation of T(40,19), and an enumeration against P_21's prediction; no rule-independence (same program) | run |
| height 21 at size 42 | T(42,21) | the same kind of evidence at more wall and disk (extrapolated 44 h, 443 GB from phase C times 1.22); P_19's first withheld entry, its other justification, was already met by the audit | not run (dominated) |
| coloring recount at height 19 | T(40,19) directly under the other rule | rule-independence and validation in one act, through neither D_j nor the product form | run |
| depth 5 | level 21 from T(39,18), T(38,17), both H <= 18 | a rule-independent derivation, agreeing with the enumerated entry; weaker in kind, since the chain runs through D_3, D_4, D_5 at k = 21 | run |

Where two routes look independent and are not: every formula statement about
T(40,19) contains D_3(21); the two formula routes (determine from (2,4),
predict depth 3; determine from (4,5), predict depth 3) share D_3(21),
D_4(21) and the product form, so their agreement checks the determining entries
and never the shared defect machinery. Re-running the assembly under the other
rule adds nothing once the entries agree, because both rules' assemblies are
determined from the same (n, H) entries. The family tables feed every depth at
every level and were checked against entries only at k <= 19; a shared error
surfacing first at k >= 20 would move all depth pairs coherently and pass
every agreement-only check. Only an enumeration crosses that family.

## The family tables' own software leg

The D_j consumed at k = 20 and 21 come from the k = 20..22 rows of the
K22 tables, produced by the C++ enumerator alone. The pure-Python enumeration
in `experiments/severance_w3_depths.py` was run to overlap them:

| Python run | wall | compared against | entries | mismatch |
|---|---|---|---|---|
| e <= 2, K = 22 | 150.2 s | `K22_e2` | 207 (all three columns, k <= 22) | 0 |
| e = 3, K = 10, 11, 12 | 62.5, 105.5, 169.3 s | `K22_e3` | 52 at K = 12 | 0 |
| C++ `K19_e3` vs C++ `K22_e3` (different span caps 42, 47) | | | 228 | 0 |

D_2 and D_3 computed from the Python families and from the C++ tables are
identical at every k <= 22; so D_2(20), D_3(20), D_2(21), D_3(21) have two
computations. A Python e = 3 run to K = 22 was estimated at 3 to 4 hours plus
the memory growth that stopped a K = 19 attempt at 1.5 GB, and was not run.

**The depth-5 check** (`experiments/severance_w3_depth5_gate.py`,
`make gate-severance-depth5`) compares against the 15 recorded entries
T(2k-4, k-4), k = 5..19; it exits 1 without a K >= 19, e = 4 table and does
not fall back to the Python enumeration. Its comparator is
`severance_w3_gate.check_depth`, imported. The table
`results/severance_w3_families_K21_e4.txt` was produced by
`scripts/severance_e4_k21.sh` (`families 21 4`, 8 threads,
2026-08-23 09:27 to 14:21, rev `95fbb6ceb`, 105 entries, sha256 checked
against the producing machine's copy). The check passes: depth 1, 19 entries
and depth 5, 15 entries, all exact; 0.20 s. Its negative control, +3^-17 at
k = 12, fails as it should.

Mutation test of the check (every entry with e <= 2 and k <= 8, last digit
perturbed in a shadow tree):

| column | mutants killed |
|---|---|
| `sig` | 21 of 21 |
| `bb` | 21 of 21 |
| `pp` | 0 of 21 |

`pp` is not inert above depth 1: measured on `D_series(j, 10)`,
`pp[e][8] + 1` moves D_{e+1}(8) by exactly 1 and no other depth. The sample
fed depths 1 to 3, which this check does not look at; the e = 4 row's `pp`
column is exercised by depth 5, and `pp[3][21] + 1` is refused by the depth-5
build (`undertow_pairs_gate.py`, control 3).

Overlap of the K21_e4 table with every earlier table, all three columns:

| table | shared entries | mismatch |
|---|---|---|
| `K19_e3` | 76 | 0 |
| `K22_e0` | 21 | 0 |
| `K22_e1` | 42 | 0 |
| `K22_e2` | 63 | 0 |
| `K22_e3` | 84 | 0 |
| `K60_e1` | 42 | 0 |

The 21 e = 4 rows are new to that table.

## The integrality congruence gate

`experiments/undertow_congruence_gate.py` (`make gate-undertow-congruence`).
The left side of the identity is an integer and den(D_j(k)) divides 3^(k+j),
so

    P_k(2k+1-j) + 3^(k+j) D_j(k) == 0   (mod 3^(k+j)),

which fixes the numerator of D_j(k) modulo 3^(k+j) from P_k alone. The
modulus grows with k and j, so the strongest congruences fall on the
frontier's unenumerated entries. Entries used to determine their own level
are reported and never counted. 71 recorded entries are checked at full
equality (which subsumes the entries `experiments/severance_w3_gate.py`
checks, and T(40,20)); the two free entries, with no recorded value, get the
congruence:

    T(42,21)  k=21, j=1   D_1(21) mod 3^22   OK
    T(41,20)  k=21, j=2   D_2(21) mod 3^23   OK

This is the only check of any kind on D_1(21). The check fails if the free
set empties. Four negative controls: D_2(21) + 3^-23 caught at the free
entry; a corrupted a_21 caught; an integer shift of a free entry's defect
passes (the blind spot, demonstrated on purpose); D_4(21) + 3^-25 caught
transitively through the constants it feeds. Every error a real table entry
can carry is an integer shift (previous sections), so this check never guards
the tables; the pair-agreement check does.

## Freedom from fitting

Can the assembly be freed of every enumerated entry? Not past k of about 11,
for a reason that belongs to the construction rather than to this lattice.

- The product form makes (a_k, b_k) equivalent to the aggregate cluster weights
  of surplus <= k, and those are connected-animal counts of the same species
  as the object being counted. Every known exact route to them carries a
  frontier connectivity partition (the state of `cpp/severance_w1.cpp` is the
  top row's cells plus their partition). Growth per level, measured in two
  implementations: Python, k = 4, 5, 6 at 3.1 s, 65 s, more than 530 s; C++,
  k <= 7 in seconds, k = 8 in minutes, k = 9 in 66 min and 53 GB, k = 10 not
  run for want of memory (`results/below-onset.md`). From k = 9 to level 21
  at 20x per level is a factor of about 20^12.
- The cheap compressions are closed: a per-level span cap undercounts
  (333 against 339 at (e, k) = (0, 2), K = 9; `results/closed-doors.md`); the
  mirror quotient is at most 2x; the only rank measurement of a comparable
  state space, the column transfer matrix in characteristic 2, found no
  collapse (`results/arithmetic-structure.md`), which is analogy, not
  measurement, for the family enumeration.
- The generating-function escapes are blocked by measured or proved facts:
  the all-pairs weight family is not C-finite (refuted at length 16,
  `results/diagonal-formula.md`); the anisotropic generating function is not
  D-finite (`results/anisotropic-not-dfinite.md`); the depth-1 algebraic
  generating function came from a bounded-excess walk with a finite state
  space, and each unit of excess adds a marker, so the walk's state space is
  infinite exactly where the assembly needs it. The top j coefficients of
  column k need only excess <= j-1 families; the constants are the bottom of
  the column, at full excess. Hardness grows with depth into the column.
- Two refutation targets, either of which overturns the verdict: (a) a
  closure of the bivariate family generating function with unboundedly many
  markers by the kernel method of enumerative combinatorics; (b) a
  super-constant state quotient in the cluster enumeration. The cheap probe
  of (a) is that method at e = 1 against the 60-order table
  `results/severance_w3_families_K60_e1.txt`; desk work, not done.

**Depths 8 and 9, closed.** With exact defects through depth 9 every level
k <= 21 would be determined from strip-engine entries at H <= 14 (level 21
from T(35,14) at depth 8 and T(34,13) at depth 9), and the main program would
leave the assembly's inputs entirely. The per-excess cost series below kills
it: from (K = 10, e = 4), reaching e = 8 costs another factor of about 8^4 in
wall and 6^4 in memory before any K scaling, which is 10^8 to 10^9 core-seconds
and terabytes of state on every K slope in range. No table with K < 21 reaches
level 21, because D_j(k) draws on families at surplus up to k itself. What
would revive it is a representation with states polynomial in e, target (a)
above.

**Other routes.** External-memory cluster enumeration with the mirror quotient
reaches k = 10 at about 1 TB of spill and k = 11 at about 20 TB (extrapolated
at 20x per level from 53 GB), never 21. Determining the constants 3-adically
is self-defeating for exact values: only clusters of surplus <= m survive
modulo 3^m, and the level aggregates h_k grow with ratio 6 to 14 (recorded
h = 1, 25, 208, 1483, 20688, 130208), so fixing h_k exactly needs m about
k log_3(ratio) > k, more cluster data than the direct route. Kept for
congruences only.

**Reach, repriced.** A depth step costs 6.6 to 9.5x in wall and about 6x in
memory; a height step of a rule-independent enumeration costs 3 to 4.4x.
Both are exponential; heights buy two rows per step at the shallower slope.

| determining entries from | hmax | J | k_max | rows complete to |
|---|---|---|---|---|
| strip engine | 14 | 4 | 16 | 31 |
| strip engine | 14 | 5 | 17 | 32 |
| coloring recount, size 40 | 18 | 4 | 20 | 39 |
| coloring recount, size 40 | 18 | 5 | 21 | 40 |
| coloring recount, size 41 | 19 | 4 | 21 | 41 |

A row is complete only when heights <= hmax are enumerated at that size; the
coloring recount's rows stop at size 41.

## Measured costs

The depth-5 family enumeration at 8 threads
(`./build/severance_w3_families families K 4 8`, `results/depth5/ladder.txt`):

| K | wall | rss |
|---|---|---|
| 8 | 6.52 s | 128.9 MB |
| 10 | 48.16 s | 462.9 MB |
| 12 | 219.20 s | 1150.1 MB |
| 14 | 731.86 s | 2459.5 MB |
| 16 | 1988.13 s | 4239.2 MB |
| 21 | 17,660 s | 18,743 MB |

The K = 21 run is the one a(41) uses. Extrapolating the K ≤ 16 ladder
(`experiments/depth5_cost_ladder.py`) had predicted 3.1 to 6.7 h and 8.5 to
16.1 GB for it, so projections from this ladder bracket wall and
under-predict memory. Memory scales with thread count as well as K, since
the enumeration builds per-thread maps and merges them afterward, so a
slope taken across thread counts is not a slope. Depth 6 was priced
(`scripts/lastditch/emax5_kladder.sh`) at 36 to 44 h and 74 to 85 GB for
K = 21 and not run.

## The square lattice

The square lattice is the one check whose answers other people published.
There the set D of row-to-row displacements has size b = |D| = 1, so the
factor 3^(n-1-3k) is 1 and the formula is a plain polynomial
T_sq(n, n-k) = P_k(n) of degree k for n >= 2k+1. Data: the bounding-box
triangle `results/bbox_square4_n21.txt` (n <= 21), whose 21 row sums equal
A001168 in `results/b001168_external.txt` (the b-file, with a(57) to a(70)
due to Barequet and Ben-Shachar, 2024) before any fitting. P_k fitted from
in-onset entries alone needs n up to 3k+1, so k <= 6.

**Depth 1** (`experiments/undertow_square.py`). D_1(k) = (-1)^(k+1), measured
at k <= 5 in `results/below-onset.md` and derived for every k: the square gap
walk closes on two states with F_1 = -1/(1+y)
(`experiments/depth1_parametric.py`, checked to k = 40;
`docs/proofs/universal-diagonal-law.md`). Per level, two fits of the same
polynomial: by the onset rule, from the k+1 entries at n = 2k+1 to 3k+1; and
with the tallest of those dropped and the depth-1 entry at n = 2k used
instead.

| k | fits agree | tallest entry, predicted from below onset |
|---|---|---|
| 1 | yes | 8 |
| 2 | yes | 121 |
| 3 | yes | 2,110 |
| 4 | yes | 39,183 |
| 5 | yes | 752,927 |
| 6 | yes | 14,780,288 |

Three negative controls: one input entry perturbed by 1 breaks the agreement;
the wrong defect sign breaks the fit; the row-sum check fails against a
perturbed A001168.

**Depth 2** (`experiments/undertow_square_depth2.py`).
D_2(k) = T_sq(2k-1, k-1) - P_k(2k-1), measured against the P_k fitted by the
onset rule:

| k | T_sq(2k-1, k-1) | P_k(2k-1) | D_2(k) |
|---|---|---|---|
| 2 | 1 | 5 | -4 |
| 3 | 18 | 10 | 8 |
| 4 | 269 | 272 | -3 |
| 5 | 3,468 | 3,458 | 10 |
| 6 | 42,099 | 42,100 | -1 |

All integers, sign (-1)^(k+1) at every level; the magnitudes 4, 8, 3, 10, 1
are not monotone, do not separate by parity, and are recorded as five values,
not a formula. The depth-2 fit uses n = 2k-1, 2k and the in-onset entries
n = 2k+1 to 3k-1, exactly k+1 points, with the two tallest entries never seen:

| k | agrees with the onset-rule fit | T(3k, 2k) predicted | T(3k+1, 2k+1) predicted |
|---|---|---|---|
| 2 | yes | 68 | 121 |
| 3 | yes | 1,226 | 2,110 |
| 4 | yes | 23,182 | 39,183 |
| 5 | yes | 450,432 | 752,927 |
| 6 | yes | 8,908,454 | 14,780,288 |

Ten withheld entries, ten exact hits. A D_2 corrupted by 1 breaks the fit at
every k, so the agreement carries the defect rather than surviving it.

**What this establishes and what it does not.** A below-onset entry plus its
defect is a valid equation for the diagonal polynomial on a lattice whose
answers were published before this project existed. It does not establish the
king D_j, which are separate derivations. The square test fits all k+1
coefficients, so it validates "below-onset entries are equations" and not
"two of them suffice", which is the product form's part. D_2 here is measured
against a P_k fitted by the onset rule, so it is not an independent route to
D_2 and does not by itself make a square P_k cheaper. Six levels, tallest
entry at height 13; the king case runs to k = 21. Reaching the square record
(n = 70) would need square below-onset entries at H <= 28. k = 7 needs
n <= 22 and k = 8 needs n <= 25, and A001168(25) = 5,940,738,676, so each
further level is an engine run. The family enumeration is king-only in both
its Python and C++ forms, with adjacency built into the row transfer; the
lattice-parametric machinery of `docs/proofs/universal-diagonal-law.md`
covers the above-onset assembly only, so a square D_2 derivation is a build,
and these five integers are its target.

## Open problems

- D_j at k = 20 and 21 are exact derivations checked against entries only at
  k <= 19; at k = 21 they are guarded by pair agreement and by the enumerated
  T(41,20), not by a second computation of the tables' e = 3, k = 21 row.
- A closed form for the square-lattice D_2, from five values that gave none.
- A lattice-parametric family enumeration, which would give D_j on the square
  lattice at every depth and turn the external check into a second instance.
- The excess-1 family generating function derived in closed form and checked
  against the K60_e1 table: the cheap probe of whether the per-excess cost
  can ever be sub-6x.
- Depth 6 (`families 21 5`), priced at 36 to 44 h and 74 to 85 GB, not run.
- The exponent of a fixed-height enumeration in the maximum size is measured
  at two heights only; the height-20 run's disk peak was not recorded.
- `undertow_ri.py` on rows <= 18, where it fails; those rows rest on the
  720-entry agreement.
- n = 42 needs heights <= 19 enumerated at size 42 with J = 5, or height 20
  with J = 4; heights are the cheaper step.

## Reproduce

    python3 experiments/undertow_pin.py --verify [--jmax 5]
    python3 experiments/undertow_pin.py --audit  [--jmax 4]
    python3 experiments/undertow_pin.py --predict
    python3 experiments/undertow_pin.py --selftest
    python3 experiments/undertow_ri.py --hmax 18 --jmax 4
    python3 experiments/undertow_ri.py --hmax 19 --jmax 4 --rowdir results/cutcount_b1/rows41 --rows 39,40,41
    python3 experiments/undertow_a41.py --jmax 5 --perheight results/a41
    python3 experiments/lane_b_a41_recount.py
    make gate-undertow-pairs gate-undertow-congruence gate-severance-depth5
    python3 experiments/undertow_square.py
    python3 experiments/undertow_square_depth2.py
    python3 experiments/depth5_cost_ladder.py
    python3 experiments/depth6_cost_ladder.py

All of the above run in seconds on the files in the tree. The measurements
were `scripts/nmax_scaling.sh`, `scripts/lastditch/emax_ladder.sh`,
`scripts/lastditch/emax4_kladder.sh`, the 8-thread series
`./build/severance_w3_families families K 4 8` for K = 8, 10, 12, 14, 16,
`scripts/lastditch/emax5_kladder.sh` (about 2.2 h),
`scripts/severance_e4_k21.sh` (4 h 54 m) and `scripts/dalby_a41_h20.sh`
(9.63 h on 76 cores).
