# Symmetry classes of polyplets

A polyplet is a finite set of cells of the square lattice that is connected
under king adjacency: two cells touch if they share an edge or a corner. The
fixed count a(n) (OEIS A006770) counts polyplets with n cells up to
translation. This file records the polyplets that have a symmetry: the free,
one-sided, bilateral, asymmetric and free-non-polyomino counts to n = 32, and
with one formula-assisted input to n = 33; the congruences the symmetry
counts impose on a(n) and on every entry of the height triangle T(n,H),
checked to n = 40; the two families inside the bilateral count; and the
diagonal-mirror strip counts d(S,n), whose diagonals obey a proved
quasi-polynomial law with explicit formulas to level 5, a measured sharp
onset, and a measured split into two families. The sequences to n = 32
inherit A006770's grade; the n = 33 values that need the diagonal-mirror
count are formula-assisted and stay out of OEIS b-files; the congruences are
exact identities checked on data; the diagonal law is a theorem in its shape
and degree, and measured in its onset, leading coefficients and split.

## Notation

The symmetry group of the square lattice is the dihedral group D4 of order 8:
the identity e, the rotations r90, r180, r270, the axis-parallel mirrors h
and v, and the diagonal mirrors d (the transpose) and ad. Fix(g)(n) is the
number of fixed polyplets with n cells that g maps to themselves, counted for
one placement of the symmetry element; the factor 2 in Burnside's formulas
covers the conjugate placement. The symmetric counts are written R90, R180,
H (= Fix(h)) and D (= Fix(d)). On the diagonal only the through-cell
placement is a lattice symmetry.

The subgroups used are C4 = <r90>, D2ax = {e, h, v, r180},
D2diag = {e, d, ad, r180}, and D4. I(K)(n) is the number of fixed polyplets
with n cells invariant under every element of the subgroup K; this is not
Fix(g), since I(D2ax) is fixed by both axis mirrors and Fix(h) by one. For a
subgroup K that preserves height, I_H(K)(n) counts those of height H.

T(n,H) is the height triangle, the number of fixed polyplets with n cells and
bounding-box height exactly H; a(n) is its row sum. Its values are entries;
"cell" below always means a lattice cell.

d(S,n) is the number of diagonal-mirror-symmetric fixed polyplets with n cells
and bounding box exactly S x S. Its level is k = n - S, and D(n), the sum over
S, equals Fix(d)(n). A formula for a level holds from some S on; its onset is
the least S from which it reproduces every entry.

The tracked data is `results/sym_counts.txt`: R90 to n = 33, R180 and H to
n = 34, D to n = 32 directly and to n = 33 with formula assistance, and the
423 strip entries d(S,n) for n <= 32.

## Burnside and the five related sequences

With Free = A030222, OneSided = A030233, Bilateral = A030234, Asym = A030235,
FreeNonPoly = A194596 and A000105 the free polyomino count:

    Free        = (Fixed + 2 R90 + R180 + 2 H + 2 D) / 8
    OneSided    = (Fixed + 2 R90 + R180) / 4
    Bilateral   = (H + D) / 2
    Asym        = Free - Bilateral
    FreeNonPoly = Free - A000105

The combiner `scripts/derive_related.py` checks the 95 OEIS terms known
before this work (the five sequences ended at n = 19), the divisibilities by
8, 4 and 2 at every n, and Asym = Free - Bilateral. R90 is zero for n not
congruent to 0 or 1 modulo 4.

| input | reach | program, machine, date |
|---|---|---|
| Fixed | n <= 34 | row sums of the height triangle, `results/ns_a34/` |
| R90, R180, H | n <= 34 | `build/symtm`, gympie and dalby, 2026-07-05 |
| D | n <= 32 | per-strip runs of `build/symtm`, dalby S = 26..32 and ayr S = 25..1, summed by `scripts/dmirror_sum.py 32`, 2026-07-05 |
| D | n = 33 | direct strips S <= 28 plus formulas for S = 29..33, next section |

The first extension, to n = 24, used `build/symcount_fast` (`sym_extend 24`,
dalby, 2026-07-04); each further term cost about 2.6 times the last there,
and the transfer matrix replaced it. D is the wall: a mirror-symmetric animal
is determined by half of itself, so Fix(d) grows like the square root of
a(n). The n = 33 strip run on dalby:

| wall | CPU | peak strip resident size |
|---|---|---|
| 24.0 h | 6.71 million core-seconds | 126.2 GB at S = 28 |

n = 34 was declined. Grades follow A006770: n <= 22 by two programs sharing
no code; n = 23..33 by one program with cross-checks (T2); A030233(34)
inherits a(34)'s grade (T2-). The four sequences that need D are
formula-assisted at n = 33 (T3), in the OEIS staging as comments only.

The values for n = 20..32 (n = 20..34 for A030233) are the b-files
`results/b0*_upload.txt`, checked by `make gate-bfiles`; the staging is
`oeis/A03022*.txt` and `oeis/A194596.txt`. The terms in no b-file:

| sequence | n | value | grade |
|---|---|---|---|
| A030222 free | 33 | 9328935247555296909698722 | T3 |
| A030234 bilateral | 33 | 5909238725043 | T3 |
| A030235 asymmetric | 33 | 9328935247549387670973679 | T3 |
| A194596 free-non-polyomino | 33 | 9328935102907028734392020 | T3 |
| A030233 one-sided | 33 | 18657870495104684580672401 | T2 |
| A030233 one-sided | 34 | 128829209605977867230343869 | T2- |

### D(33), the formula-assisted entry

D(33) = 5475149862148, assembled by `scripts/dmirror_hybrid_sum.py 33 28` from
the direct strips S = 1..28 and the diagonal formulas below for the 15 sparse
entries at S = 29..33. The script refuses unless every direct strip is
complete over its full n range, the formulas reproduce the 124 direct entries
in the overlap, only formulas fixed by exact differencing are used (P_5 on
odd S is fitted and is refused), and the assembled column matches the
recorded n <= 32 values. Every strip's n <= 32 prefix matched the n = 32 run
on all 413 entries; ayr recomputed the S <= 25 strips on another processor
architecture.

The five formula entries in D(33) itself, with the onset of the formula's
parity class and the number of exact entries below the fit it reproduces:

| entry | k | onset | margin above onset | reproduced entries |
|---|---|---|---|---|
| d(29,33) | 4 | S >= 11 | 18 | 4 |
| d(30,33) | 3 | S >= 8 | 22 | 7 |
| d(31,33) | 2 | S >= 7 | 24 | 9 |
| d(32,33) | 1 | S >= 4 | 28 | 12 |
| d(33,33) | 0 | S >= 3 | 30 | 14 |

The other ten formula entries lie at n < 33 on levels k <= 3 with margins of
at least 18. Four of the five above are checked modulo 2 against an unrelated
program (the Burnside tie below).

The rule in `results/confidence.md` admits a formula entry when the formula's
shape is proved, the entry lies inside a proved region of validity, and the
constants are fixed from enumerated entries with at least one held back.
D(33) meets the first and third; the onset S >= 2k+2 is measured, not
proved, so it fails the second however far past the onset its entries sit.
The sharpness argument for the main triangle (`docs/proofs/diagonal-law.md`)
has no diagonal-mirror counterpart (`docs/proofs/dm-diagonal-law.md`).

## Congruences from the subgroup counts

Burnside's lemma read through orbit sizes gives congruences. With F(K) the
number of fixed polyplets whose stabilizer is exactly K, so that I(K) is the
sum of F over the subgroups containing K, the orbits of size 1 number F(D4)
and twice the orbits of size 2 number I(C4) + I(D2ax) + I(D2diag) - 3 I(D4);
every other orbit has size 4 or 8:

    a(n) = I(C4) + I(D2ax) + I(D2diag) - 2 I(D4)                        (mod 4)
    a(n) = R180 + 2 H + 2 D - 2 I(D2ax) - 2 I(D2diag)                    (mod 8)

In the mod-8 line the two order-2 mirror classes each contribute twice ({e,h}
with {e,v}, {e,d} with {e,ad}) and the C4 and D4 terms cancel.

D2ax is exactly the height-preserving subgroup of D4, since r90, r270 and both
diagonal mirrors exchange height and width. It acts on the polyplets of each
height separately, orbit sizes there divide 4, and every entry of the height
triangle carries its own bit; with C2 = <r180>:

    T(n,H) = I_H(D2ax)                                                   (mod 2)
    T(n,H) = I_H(<h>) + I_H(<v>) + I_H(C2) - 2 I_H(D2ax)                (mod 4)

Each input is a quotient-domain family of size about lambda^(n/4): the
residue of a(40) costs minutes on a laptop, a(40) cost over a hundred
core-days on the column transfer matrix.

The counts to n = 40 (`scripts/subgroup_mod4.sh 40 8`, `build/symcount_fast`,
gympie, 2026-08-07, 8 threads, peak resident size 4.6 MB) are
`results/subgroup_counts.txt`; the per-height D2ax counts, 630 rows, are
`results/subgroup_d2ax_byheight.txt`. The C4 column equals the recorded R90
on every row n <= 33.

| subgroup | I(K)(40) | wall |
|---|---|---|
| C4 | 16671983 | 7.3 min |
| D2ax | 123753061 | 15.0 min |
| D2diag | 108831725 | 8.2 min |
| D4 | 10379 | under a second |

Results (`results/subgroup_mod4_verdict.txt`, assembler
`experiments/subgroup_mod4.py`); a(40) is 3 modulo 4 by both routes:

| check | rows or entries | mismatches |
|---|---|---|
| a(n) mod 4, n <= 40 | 40 | 0 |
| a(n) mod 8, n <= 33 | 33 | 0 |
| T(n,H) mod 2, every entry with n <= 40 | 820 | 0 |

The 820 entries by height band, with the other evidence each band had:

| band | entries | other evidence |
|---|---|---|
| H = 1..10 | 355 | fixed-height generating functions |
| H = 11..14 | 114 | the strip transfer matrix |
| H = 15..19 | 120 | none |
| H = 20 | 21 | a repeated identical run |
| H = 21 | 20 | a direct run |
| H = 22..40 | 190 | formulas, with no entry left to hold back |

H = 15..19 will get no evidence beyond these bits: the strip transfer
matrix's cost grows about sixfold per height (H = 14 took 8.6 h on dalby,
`results/second-sources.md`).

An error of size delta in one entry is caught if and only if delta is odd; in
a row, if and only if it is nonzero modulo 4 (modulo 8 where D exists). Every
failure that has occurred in this project corrupted many entries at once (a
zeroed row of 20 entries, a dropped shard, an off-by-one in a column loop),
and 820 independent bits catch a corruption of j entries with probability
1 - 2^(-j). The two programs share no code, state representation or domain.
The congruences are elementary and probably folklore; no novelty is claimed.
`tests/gate_subgroup.py` (`make gate-subgroup`) carries controls that must
fail: Fix(h) in place of I(D2ax) breaks the mod-4 line at n = 3; coefficient
1 in place of 2 breaks the mod-8 line (the first version had that error and
failed on 21 of 33 rows; `results/subgroup_mod4_20260807.log` is that run);
D2diag graded by height breaks the parity. The subgroup counts do not feed
the related sequences: Burnside needs Fix(g), and the binding input is D.

### The mod-4 refinement, entry by entry

`symtm --byheight` emits (n, H, W, count) in hmirror mode, which summed over
W gives I_H(<h>) and grouped by W gives I_W(<v>) (an h-symmetric W x H animal
transposes to a v-symmetric H x W one), and (n, H, count) in r180 mode. The
gate's control: the height grouping used for both mirrors must break the
congruence, and does. Run: `scripts/percell_mod4.sh 32 8`, gympie,
2026-08-07, 8 threads, binary from the tree that landed as `ffd0c2b`, log
`results/percell_mod4_20260807.log`, assembler `experiments/percell_mod4.py`,
raw tables in `results/percell_raw/`.

| phase | wall | CPU | peak resident size | rows |
|---|---|---|---|---|
| hmirror --byheight | 1180.6 s | 5498.4 s | 3890.1 MB | 4693 |
| r180 --byheight | 605.2 s | 2758.0 s | 3233.1 MB | 408 |

Summed over height, both tables reproduce the recorded Fix(h) and Fix(r180)
at every n <= 32 (at n = 32, 2546382907164 and 7063812264280). Against the
height triangle, every entry with n <= 32:

| band | entries | mod-2 mismatches | mod-4 mismatches |
|---|---|---|---|
| H = 1..10 | 275 | 0 | 0 |
| H = 11..14 | 82 | 0 | 0 |
| H = 15..19 | 80 | 0 | 0 |
| H >= 20 | 91 | 0 | 0 |

I_H(<v>) has a value at all 528 entries, I_H(<h>) and I_H(C2) at 408; the
rest are genuine zeros, which the flat regression confirms. The identity had
previously been checked on the 78 entries with n <= 12 only.

The refinement is not extended to n = 40. I_H(<v>) has no bounded-height
route: a v-symmetric animal of height H transposes to one of width H and
unbounded height, so it needs every strip up to n (a width cap of 8 across
all 40 strips still ran past two minutes), and a bounded-height route is a
new transfer-matrix mode. The cost of r180 peaks on the band that needs it,
since the transpose restriction forces W >= H and tall strips collapse
(`results/symtm_strip_profile_n40.txt`, N = 40, 8 threads, 120 s cap; at
N = 32 r180 was slowest at H = 21 and hmirror at H = 31):

| mode | H = 5 | 10 | 15 | 19 | 20 | 25..30 | 34 | 38 | 40 |
|---|---|---|---|---|---|---|---|---|---|
| hmirror, s | 0 | 0 | 3 | 51 | 33 | >120 | >120 | >120 | >120 |
| r180, s | 0 | 15 | >120 | >120 | >120 | >120 | 7 | 0 | 0 |

And the second bit moves the single-entry adversarial case from one half to
three quarters, adds nothing against correlated failures, and would rest on a
new mode with no history against the brute-force oracle.

## Bilateral symmetry has two families

A mirror axis of a bilaterally symmetric polyplet either runs along a column
(through-cell: its cells are fixed, the rest paired, n odd or even, and at
least one axis cell is forced since otherwise the halves sit two columns
apart and are not king-adjacent) or between two columns (between-cell: no
cell fixed, so n is even; the halves connect because (0, j) and (1, j) share
an edge). With T(n) the through-cell and B(n) the between-cell count,

    A030234(n) = T(n) + [n even] B(n).

The test is log-convexity in exact integers on the b-files, a(n)^2 <
a(n-1) a(n+1) across parity classes against a(n)^2 < a(n-2) a(n+2) within one
(`experiments/bilateral_parity.py`, ayr, 2026-08-22, zero terms excluded).
Controls: a geometric sequence is flagged at the strict boundary; one
log-convex family is clean both ways; a planted sequence of the conjectured
shape fails interleaved and is clean within each class.

| sequence | terms | violations, interleaved | violations, same parity |
|---|---|---|---|
| A006770 fixed | n <= 40 | none | none |
| A030222 free | n <= 32 | n = 4 | none |
| A030233 one-sided | n <= 34 | n = 4 | none |
| A030234 bilateral | n <= 32 | n = 2, 4, ..., 30 | none |
| A030235 asymmetric | n <= 32 | n = 4, 6 | n = 5 |

The bilateral count fails at every even n the data can test and is clean
within each parity class. With rho = B/T and T(n) ~ C mu^n n^theta, the
consecutive ratios b(even)/b(odd) and b(odd)/b(even) have product mu^2 and
quotient (1 + rho)^2 asymptotically, so both come out with no fit:

| n | 8 | 12 | 16 | 20 | 24 | 28 | 30 |
|---|---|---|---|---|---|---|---|
| mu | 2.48661 | 2.53641 | 2.56358 | 2.58083 | 2.59284 | 2.60172 | 2.60535 |
| rho = B/T | 0.05604 | 0.04928 | 0.04541 | 0.04277 | 0.04078 | 0.03923 | 0.03856 |

mu rises monotonically toward the square root of the growth constant,
sqrt(7.1102) = 2.66650, as it must if a symmetric animal is determined by
half of itself, and is still short of it at n = 30. rho decreases, its
decrements shrinking by about a tenth per step, which extrapolates to a limit
near 0.03 if the shrinkage holds and to zero if not; 32 terms do not decide.
Nothing here proves log-convexity of either class. T and B are not counted
separately: `results/sym_counts.txt` carries H as one total, and rho is
inferred from the interleaving.

## The diagonal-mirror strip counts d(S,n)

### The diagonal law

**Theorem** (`docs/proofs/dm-diagonal-law.md`, 2026-07-15). For every k there
exist polynomials p_k^even, p_k^odd of degree <= k and an effective S_0(k)
such that d(S, S+k) = p_k^parity(S)(S) for all S >= S_0(k). Consequently the
generating function sum_S d(S,S+k) x^S is rational with poles only at x = 1
and x = -1, of total order <= k+1 at each.

The polynomials are fixed by exact finite differencing on the deepest k+1
entries of a parity class, the degree read from a constant tail of
differences, and every entry between the onset and the fit must be
reproduced. Entries computed after a polynomial was fixed (S = 29..32 at
k <= 2, S = 29 at k = 3, then the n = 33 run) were reproduced. Derivation:
`scripts/dmirror_diagonals.py` over the per-strip outputs.

| k | even S | odd S | grade |
|---|---|---|---|
| 0 | 2 | 2 | proved below |
| 1 | S + 6 | S + 7 | exact differencing |
| 2 | S^2/2 + 7S + 12 | S^2/2 + 6S + 27/2 | exact differencing |
| 3 | S^3/6 + 3S^2 + 40S/3 + 50 | S^3/6 + 7S^2/2 + 83S/6 + 93/2 | exact differencing |
| 4 | S^4/24 + 3S^3/2 + 28S^2/3 + 33S + 180 | S^4/24 + 4S^3/3 + 97S^2/12 + 119S/3 + 1367/8 | exact differencing; odd S needed the S = 23 strip |
| 5 | S^5/120 + 5S^4/12 + 4S^3 + 55S^2/3 + 2278S/15 + 570 | S^5/120 + 11S^4/24 + 19S^3/4 + 185S^2/12 + 18869S/120 + 4545/8 | even: exact differencing on the n = 33 entries, S_0 = 12, 3 reproduced; odd: fitted by `scripts/dmirror_pk_exp.py` on 7 exact witnesses, not used in D(33) |

Level 6 does not fit within the degree caps on the recorded data; with seven
even entries and an expected degree 6, the sixth difference has one value and
no flatness test can run.

### The onset is sharp

`experiments/dmirror_onset_probe.py` (ayr, 2026-08-22, exact rational
arithmetic on the 423 tracked entries) fixes each class on its deepest k+1
entries, walks back, and records the least S at which the polynomial still
reproduces the entry; the entry below fails on every level.

| k | even onset | odd onset | even entries reproduced below the fit | odd |
|---|---|---|---|---|
| 0 | 2 | 3 | 15 | 14 |
| 1 | 4 | 5 | 12 | 12 |
| 2 | 6 | 7 | 10 | 9 |
| 3 | 8 | 9 | 7 | 7 |
| 4 | 10 | 11 | 5 | 4 |
| 5 | 12 | 13 | 2 | 2 |

The onset is S >= 2k+2 on even S and S >= 2k+3 on odd S, the single
condition S >= 2k+2 since 2k+3 is the least odd integer past 2k+2. The
probe's control is that the polynomials reproduce the five leading
coefficients below (it caught a hand-expanded Newton form that reported -27,
675/2 and -4025/2 for 1, 1/2 and 1/6). At k = 6 the even class has 7 entries
above its onset of 14 and the odd class 6 above 15, so the even class fixes
with nothing left to check and the odd class does not fix; the missing
entries are d(27,33) and d(29,35).

### Leading coefficients and the generating functions

Verified exactly for k = 1..5:

- lead(P_k^even) = lead(P_k^odd) = S^k / k!.
- lead(P_k^even - P_k^odd) = (-1)^k / (k-1)!, the values -1, 1, -1/2, 1/6,
  -1/24; the difference has degree k-1.
- G_k(x) = sum_S d(S,S+k) x^S = N_k(x) / ((1-x)^(k+1) (1+x)^k), N_k an
  integer polynomial of degree 2k (k = 0..5).
- N_k(1) = 2^k and N_k(-1) = (-2)^k, equivalently 1 - x^2 divides
  N_k - (2x)^k. By partial fractions these are the two leading-coefficient
  statements, and together they are the conjecture T4. Writing
  d(S,S+k) = A(S) + (-1)^S B(S), the pole multiplicities k+1 at x = 1 and k
  at x = -1 are equivalent to deg A = k and deg B = k-1, the same item.
- R_k = (N_k - (2x)^k) / (1 - x^2) has R_k(1)/2^k = 3, 3, 3, 4, 5 for
  k = 1..5 and R_k(-1)/(-2)^k = k - 3 for k = 2..5.
- No bivariate rational closure sum_k N_k z^k = P/D exists with z-degree of D
  at most 3 and x-degree at most 6; each level carries new coefficients.
- The sub-leading ratio of P_even - P_odd fits (k-1)(4k-11)/2 on k = 2..5,
  three parameters on four points, and level 6 refuses; recorded so that it
  is not mistaken for a law.

A test of T4 at k = 6 needs only the two level-6 polynomials, not N_6.

Coefficient structure. P_1 is a census of single defects: one bulk defect
type of weight 1 (the S coefficient is exactly 1) plus 6 or 7 corner
variants. The independence prediction for k = 2 on even S, (S+6)^2/2, differs
from the polynomial by +S - 6: the +S is a weight-2 bulk defect no product of
singles generates, the -6 absorbs collisions and end effects. A defect gas
over the two ground spines caps the degree of P_even - P_odd at floor(k/2),
so the measured k-1 at k = 3 refutes it: further length-free families exist,
the anti-diagonal excursions below. Their derivation is a segment grammar,
not attempted.

### The permutation skeleton and the reversal lemma

n = S cells in an exactly S x S box force one cell per row and one per
column, a permutation matrix sigma. King-connectivity forces
|sigma(i+1) - sigma(i)| = 1 (0 is impossible, 2 or more disconnects), and
injectivity then forces sigma strictly increasing (the main diagonal) or
strictly decreasing (the anti-diagonal). Hence d(S,S) = 2 for S >= 2, and
d(1,1) = 1. An (S+k)-cell animal is a permutation with k repeats read row by
row. A census at k = 1, 2 (S <= 10, `experiments/dm_sym_enum.py`) finds,
besides animals decorating either spine, a growing third class: main spines
with anti-diagonal excursions, for instance {(0,0),(1,1),(2,2),(3,3)} with
the pair {(2,4),(4,2)} at S = 5. The row-reading of a sparse symmetric animal
decomposes into monotone phases, maximal runs where the column trend is +1 or
-1, separated by reversal clusters.

**Lemma (reversal cost).** A diagonal-mirror-symmetric animal with box exactly
S x S and S+k cells has at most 2k strict direction reversals in its row-min
(and row-max) sequence, hence at most 2k+1 monotone phases.

*Proof.* Within a maximal stretch of single-cell rows, consecutive cells must
king-touch, so the cell position moves by {-1, 0, +1} per step. A reversal
inside a stretch immediately revisits a column (the step after the turn
returns to the previous value), costing at least one column surplus; a 0-step
costs the same. Reversals at multi-cell rows are bounded by the number of
multi-cell rows, that is, by row surplus. By mirror symmetry the row and
column surplus pools each hold exactly k: total at most 2k. QED

The bound is tight: the maximum number of runs observed is 1, 3, 5, 7 at
k = 0..3. Each phase class (k, runs) is separately per-parity polynomial of
degree <= k from S >= 2k+2, and the classes partition d(S,S+k) (k <= 2,
S <= 13, `experiments/dm_phase_census.py`); at k = 1 the three classes are
the linear near-spine class (runs = 1), the constant 4 (runs = 2) and the
parity-oscillating 2/4 class (runs = 3), summing to S+6 and S+7. This lemma
is step 1 of `docs/proofs/dm-diagonal-law.md`; the involution frame (a
symmetric permutation is an involution, the main family near the identity,
the anti family near the reversal, paired into half-length chains, the
origin of the period 2) is the frame of its later steps.

### The two families, counted apart

The diagonal has two ground states, since the main diagonal and the
anti-diagonal are both king-connected and both fixed as sets by the
transpose. The transpose fixes every main-diagonal cell but reverses the
anti-diagonal, (i, S-1-i) to (S-1-i, i), fixed only when S is odd; the
anti-spine has a center cell exactly for odd S. That is the mechanism of the
period 2, and of the two bilateral families above.

The split is read off hooks. Hook k is the set of cells with min(i,j) = k,
the corner (k,k) plus the mirror pairs {(k,k+p), (k+p,k)}. The main diagonal
is exactly the set of hook corners, so counting by (n, occupied corners)
separates the spines: a main-spine animal at level k has at least S-k
occupied corners; an anti-spine animal's cells (i, S-1-i) are arm cells at
offset p = S-1-2i, never corners except the center for odd S, so it has at
most k+1. d_main and d_anti are the counts in those two corner ranges.
Measured on every recorded entry:

| regime | result |
|---|---|
| S >= 2k+2 | d_main + d_anti = d exactly |
| S = 2k+1 | the two corner ranges overlap, in 5 entries, for instance (S,k) = (9,4) and (11,5) |
| S <= 2k | the ranges cross; the split is not defined |

The families partition d exactly above the onset; an earlier statement of the
threshold as S > 2k was one step optimistic.

The enumerator is `experiments/dmirror_spine_split.py` in Python and
`cpp/dmirror_spine.cpp` (`build/dmirror_spine`), which traverses hooks under
a cell budget. It shares no code with `cpp/sym/symtm.cpp`, and its totals
over corner counts reproduce all 423 recorded strip entries exactly, so it is
an independent program for the whole strip table. (A mirror pair is one
position but two cells, not adjacent unless p = 1; a version that merged them
gave 5 for d(4,4) = 2.)

| enumerator | S = 14 | S = 17 |
|---|---|---|
| Python | 6 h 38 min | not reached |
| C++ | 19 s | within twenty minutes |

The C++ label field was four bits, and a hook carries more components than
that from S = 17 on (17, 17, 19 at S = 17, 18, 19); re-derived on a six-bit
field, every entry at S = 12..19 was unchanged, since aliasing can only merge
two hooks with 17 or more components and no such hook completes into a
connected animal within n <= S + 6. S = 20 was refused, not corrupted. The
split is checked against the Python enumerator at every S <= 14; at S >= 15
only the totals are independently checked.

d_main(S, S+k), from `build/dmirror_spine`:

| k | S range | values |
|---|---|---|
| 0 | 2..19 | 1 at every S |
| 1 | 8..19 | 4 at every S |
| 2 | 8..19 | 29, 31, 33, 35, 37, 39, 41, 43, 45, 47, 49, 51 |
| 3 | 8..19 | 120, 129, 138, 147, 156, 165, 174, 183, 192, 201, 210, 219 |
| 4 | 10..19 | 704, 780, 860, 944, 1032, 1124, 1220, 1320, 1424, 1532 |
| 5 | 12..19 | 3564, 3943, 4342, 4761, 5200, 5659, 6138, 6637 |
| 6 | 14..19 | 20420, 22956, 25697, 28651, 31826, 35230 |

d_anti(S, S+k):

| k | S range | values |
|---|---|---|
| 0 | 2..19 | 1 at every S |
| 1 | 8..19 | 10, 12, 12, 14, 14, 16, 16, 18, 18, 20, 20, 22 |
| 2 | 8..19 | 71, 77, 99, 105, 131, 137, 167, 173, 207, 213, 251, 257 |
| 3 | 8..19 | 314, 447, 512, 697, 774, 1019, 1108, 1421, 1522, 1911, 2024, 2497 |
| 4 | 10..19 | 2656, 3190, 4516, 5228, 7156, 8070, 10752, 11892, 15496, 16886 |
| 5 | 12..19 | 19094, 27895, 33412, 47197, 54922, 75487, 85920, 115429 |
| 6 | 14..19 | 167220, 206168, 298707, 357249, 503722, 588226 |

Degrees by `experiments/dmirror_spine_degrees.py`, which takes the lowest
degree that fits and requires every remaining entry to be reproduced, on even
S, odd S and both pooled:

| k | 0 | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|---|
| d_main, either parity or pooled | 0 | 0 | 1 | 1 | 2 | 2 | 3 |
| d_anti, per parity | 0 | 1 | 2 | 3 | not fixed | not fixed | not fixed |

d_anti has degree k, one free position per defect, and parity enters it from
k = 1 on (its pooled fit fails). d_main has degree floor(k/2) at seven
consecutive levels, with 2 to 11 reproduced entries per fit, and one
polynomial covers both parities at every level: all of the family's period 2
comes from the anti-spine half. An earlier reading on S <= 11 gave d_main
degree k-1, which agrees with floor(k/2) for k <= 2 and fails at k = 3..5;
the floor(k/2) reading predicted 183 and 1124 at k = 3, 4 before S = 15 was
computed, the degrees at k = 5, 6 before S = 16..19, and 51, 219, 1532 at
k = 2, 3, 4 for S = 19, all exactly.

### The grand form does not transfer

The grand form of the main triangle says T(H+k,H) = [y^k] C(y) mu(y)^H,
equivalently that every cumulant of the level series is linear in the size
parameter. For each parity class form A_S(y) = sum_k P_k(S) y^k and take the
logarithm in Q[[y]] with coefficients polynomial in S
(`experiments/dmirror_grand_form.py`, ayr, 2026-08-22):

| | c_1 | c_2 | c_3 | c_4 | c_5 |
|---|---|---|---|---|---|
| even S, degree in S | 1 | 2 | 2 | 4 | 4 |
| odd S, degree in S | 1 | 2 | 2 | 4 | 4 |

Linear at c_1 and nowhere after, the two classes agreeing exactly. The
pattern deg(c_j) = 2 floor(j/2) for j >= 2 is what a sum of exactly two
exponential families produces. Controls: planted single-family data is
reported linear, planted two-family data with different growth rates
nonlinear, and the polynomials reproduce the leading coefficients 1/k!. So
the summed family has no grand form, and level k does not carry two new
constants over the levels below.

The same test on each family (`experiments/dmirror_spine_cumulants.py` on the
enumerator's output, the same two controls):

| | c_1 | c_2 | c_3 | c_4 | c_5 |
|---|---|---|---|---|---|
| d_main, both parities | deg 0 | deg 1 | deg 1 | deg 1 | deg 1 |
| d_anti, both parities | deg 1 | deg 1 | deg 2 | not reached | not reached |

Both families are linear at c_2, where the sum is not; d_anti fails at c_3,
which needs level 3 on both parities (S = 16 even, S = 17 odd). So the
two-spine sum is not the whole obstruction: d_main is of grand-form shape as
far as five levels reach, and whatever breaks the grand form lives in the
anti-diagonal family, whose cells are only diagonally adjacent and have
slack. With the split, four constants per level fit inside the 7 even and 6
odd entries at k = 6, so what blocks a test of T4 there is only that the
recorded table carries the sum, not the families, at S = 14..17. The source
record's closing section still lists c_4 on d_main as open; its table, the
later measurement, has c_4 and c_5 linear.

### The Burnside tie to the joint box table

Let B(n, W, H) count fixed polyplets with n cells and bounding box exactly
W x H. The transpose acts on the B(n, S, S) animals with exactly d(S, n) fixed
points, so the orbit count (B(n,S,S) + d(S,n))/2 is an integer:

    B(n, S, S) = d(S, n)   (mod 2).

The two sides come from unrelated programs, a row transfer with connectivity
partitions (`experiments/joint_box_probe.py`) against the hook transfer
matrix. `experiments/dmirror_burnside_check.py` (gympie, 2026-09-05, under
four minutes): 44 entries at S <= 12, k <= 3 with both sides enumerated all
agree; the D(33) formula entries d(33,33), d(32,33), d(31,33) and d(30,33)
agree, the d side from the polynomials re-fixed by exact differencing off the
recorded strips; d(29,33) is out of reach because the row transfer's shape
cache blows up at surplus 4. Two controls shift one count by 1 and both fire;
the script refuses on a missing input, a level it cannot fix, a fit with
nothing reproduced, too few entries, or an all-even comparison. Only three of
the 48 comparisons are odd on both sides, at (S,k) = (1,0), (2,2), (3,1), so
most of it is 0 = 0, and it says nothing about the onset.

The joint box table itself (`experiments/joint_box_probe.py`, 2026-07-13,
H <= 11 and n - H <= 2, every marginal matching T(n,H)): B(H,W,H) is the
trinomial walk-range distribution, B(H,2,H) = 2^H - 2 (the Burnside check's
edge control), monotone tail 2, next-to-tail 2(H+1), B(H+1,2,H) = H 2^(H-1),
tail 2(H+2). The k = 0 slice modulo 3 is visibly 3-automatic: row H = 9
reads 100000122, a zero desert carrying row H = 3's skeleton 102 (a
Lucas-type digit product, provable with the mod-3 methods of
`results/arithmetic-structure.md`); the k = 1, 2 slices show parity striping
(020202..., 002222002221), undecoded. The full table at production scale
would cost an a(36)-sized run.

### The diagonal-mirror transfer matrix

The dmirror mode of `cpp/sym/symtm.cpp` counts transpose-invariant polyplets
in a forced-square box, S running to n, by traversing hooks k = 0, 1, ...
inside an outer loop over S (an anti-diagonal traversal would need a
two-layer frontier, since king moves reach two diagonals ahead). The stored
state is the column arm, the row arm being its mirror. Two points carry the
correctness: a column-arm component and its mirror image are either one
component or two exchanged by the mirror, so each label carries a selfPaired
bit, and a single label without it at harvest is two disjoint halves; and the
new corner (k+1,k+1) is king-adjacent to five old hook cells, a +-2 stencil
at that one position, so the mode has its own hook step. The cost is
inverted in the sparse regime, which is why formulas replace the tall strips
in D(33):

| strip | CPU | memory | output |
|---|---|---|---|
| S = 31 at n = 32 | 223000 s | 79 GB | d(31,31) = 2, d(31,32) = 38 |

## Open problems

- The sharp onset S >= 2k+2 is measured on six levels and not proved; until
  it is, D(33) and the four n = 33 values stay formula-assisted. The route
  that proved sharpness for the main triangle needs a below-onset defect
  series with an algebraic equation, and no single functional equation
  covers a sum over two spines.
- T4, equivalently the leading coefficients S^k/k! on both parities and
  (-1)^k/(k-1)! for their difference, is verified for k <= 5 and untested at
  k = 6; the test needs d(27,33) and d(29,35). The degree at k = 6 is itself
  unconfirmed.
- d_main's degree floor(k/2), parity independence and linear cumulants
  through c_5 are measured, not proved. What breaks the grand form in d_anti
  at c_3 is open.
- The coefficients of P_k are not derived; a segment grammar over spine runs,
  anti-diagonal excursions, connectors and defects would derive them.
- Whether B/T tends to a positive limit or to zero is undetermined; T and B
  have never been counted separately. Log-convexity of each parity class is
  observed, not proved.
- The k >= 1 stripes of the joint box table modulo 3 are undecoded, and its
  k = 0 digit law is unproved.
- D(34) was declined; it would rest on the fitted P_5 on odd S unless the
  n = 33 direct strips fix it.
- Per-entry mod 4 at n = 40 needs a bounded-height mode for I_H(<v>) and a
  cheaper r180 on H = 15..19.

## Reproduce

    python3 scripts/derive_related.py runs/sym33.derive
    scripts/dmirror_hybrid_sum.py 33 28 runs/sym33
    scripts/dmirror_sum.py 32
    make gate-bfiles
    scripts/subgroup_mod4.sh 40 8
    make gate-subgroup
    scripts/percell_mod4.sh 32 8
    python3 experiments/bilateral_parity.py
    python3 scripts/dmirror_diagonals.py
    python3 scripts/dmirror_pk_exp.py 6
    python3 experiments/dmirror_onset_probe.py
    python3 experiments/dmirror_grand_form.py
    python3 experiments/dm_sym_enum.py
    python3 experiments/dm_phase_census.py
    build/dmirror_spine --gate
    build/dmirror_spine 17 6
    scripts/dmirror_spine_ladder.sh 15 18 6
    python3 experiments/dmirror_spine_cumulants.py LOG
    python3 experiments/dmirror_spine_degrees.py LOG
    python3 experiments/dmirror_burnside_check.py
    python3 experiments/joint_box_probe.py

The probes on `results/sym_counts.txt` and the b-files are instant; the
subgroup and per-entry runs take 45 and 30 minutes on 8 threads;
`build/dmirror_spine --gate` checks 191 recorded entries. `runs/` is not
tracked; `results/sym_counts.txt` is the tracked copy of its outputs.

## Sources

- `results/subgroup-mod4.md` (deleted 2026-09-06; its content is above)
- `results/percell-mod4.md` (deleted 2026-09-06; its content is above)
- `results/bilateral-parity.md` (deleted 2026-09-06; its content is above)
- `results/related-seqs-n24.md` (deleted 2026-09-06; its content is above)
- `results/related-seqs-n32.md` (deleted 2026-09-06; its content is above)
- `results/related-seqs-n33.md` (deleted 2026-09-06; its content is above)
- `results/dmirror-diagonals.md` (deleted 2026-09-06; its content is above)
- `results/dmirror-grand-form-fails.md` (deleted 2026-09-06; its content is above)
- `results/dmirror-onset-sharp.md` (deleted 2026-09-06; its content is above)
- `results/dmirror-spine-split.md` (deleted 2026-09-06; its content is above)
- `results/dm-diagonal-recon.md` (deleted 2026-09-06; its content is above)
- `results/joint-box-probe.md` (deleted 2026-09-06; its content is above)
- `docs/dmirror-design.md` (deleted 2026-09-06; its content is above)
