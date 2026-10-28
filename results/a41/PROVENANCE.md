# a(41)

    a(41) = 393811462683918679824582849262105

Computed in two enumeration runs on an 80-core server and one assembly. It is
the first term for which the closed forms were fixed from entries below their
onset (the onset of level k = n − H is n = 2k+1; see `docs/glossary.md` for
level, depth, defect and fit), so that height 21 was never enumerated. The
enumeration runs need that server; the assembly, which recomputes a(41) from
the stored per-height output, runs in under a second on a laptop (the
`below_onset_fit_a41.py` command under Checks).

## How

- Heights 1..19, enumerated 2026-08-20 by `scripts/dalby_a41_low.sh`:
  `orchestrate --maxn 41 --kernel kink --counter u128 --cores 40 --ram 1GiB
  --overlap-heights 19 --heights 1-19`; 16,998.7 s of wall on 40 cores,
  605,643 cpu-s, peak RSS 557 MB, run directory under 100 GB. Rows in
  `h*.out`.
- Height 20, enumerated 2026-09-05 by `scripts/dalby_a41_h20.sh` at
  revision `b88b38bc5`, 76 cores, `--max-diag-k -1` (nothing from a closed
  form), 11:41 to 21:19 EDT: wall 34,678.8 s, 1,766,882 cpu-s, peak RSS
  814.7 MB. Row in `h20.out`; per-column profile in `h20_cost_profile.tsv`
  (frontier peak 129,487,745 records at column 7; columns 6-8 about 2300 s
  each). The run directory was cleaned by the orchestrator, so the disk
  peak was not recorded.
- Heights 21..41 from the closed forms of `docs/proofs/diagonal-law.md`,
  assembled by `experiments/below_onset_fit_a41.py`: levels k = 41 − H = 0..20,
  with k ≤ 19 from the wired coefficient table and k = 20 pinned from cells
  below its onset by the depth-j corrections D_j (`results/below-onset-fit.md`).
  T(41,21) is exactly at onset on level 20. Before the H = 20 run the
  assembly also supplied T(41,20), from level 21 at depth 2.

Enumerating H = 21 at Nmax 41 was not done; the a(40) run's H = 20 and
H = 21 phases took 9.6 h on 48 cores and 36.4 h on 32 cores with a 363.4 GB
disk peak. Twenty-one of the forty-one cells are therefore formula. The
rule under which a formula may stand in for an enumeration is in
`results/confidence.md`: the shape of the closed form is a theorem, the
cell is inside the proved onset n ≥ 2k + 1, and the constants are pinned
from enumerated cells with at least one held out. The corrections D_j that
pin levels 20 and 21 from below onset were checked against enumerated cells
only at k ≤ 19; the checks below are about that.

## Checks

- The Nmax-41 enumeration also produces every row n ≤ 40 at every height
  it covers. All 800 positions with n ≤ 40 and H ≤ 20 (610 of them nonzero)
  agree with `results/triangle.txt`. `below_onset_fit_a41.py` refuses the n = 41
  row unless they match and at least 200 cells were compared.
- A separate assembly with row 40 excluded from its own pinning set
  reproduces 21 cells of row 40, 0 wrong, and the row re-sums to a(40).
- T(41,41) = 3^40 and T(41,40) = (25·41 − 45)·3^37.
- a(41)/a(40) = 6.9394, after 6.9212, 6.9261, 6.9308, 6.9352; the
  successive differences 0.0049, 0.0047, 0.0044, 0.0042 shrink.
- The method: 18 levels re-derived exactly from below-onset cells, and 189
  enumerated cells (342 predictions in all, 153 of them formula values)
  reproduced from shorter cells with 0 wrong; a(n) comes
  out independent of the rule for every n ≤ 39 (`results/below-onset-fit.md`).
- Re-assembly with the enumerated height 20
  (`python3 experiments/below_onset_fit_a41.py --jmax 5 --perheight results/a41`):

      heights swept: 1..20;  heights from the tower: 21..41
      sweep vs banked triangle: 800 cells agree, 0 disagree
      a(41) = 393811462683918679824582849262105

## A second implementation of the assembly

`experiments/lane_b_a41_recount.py` rebuilds the term by a route that
differs wherever it can: levels k = 1..19 fitted from their two onset
entries in `results/triangle.txt` rather than read from `diagCoeffTable`;
level 20 fitted from depths (1, 2) with (3, 4) held out; its own polynomial,
product-form, solver and assembly code. It never reads `below_onset_fit_a41.py`.

    anchor-pinned k<=19 predict banked in-onset cells: 342 ok, 0 wrong
    imported D_j vs own empirical extraction at k<=19: 70 ok, 0 wrong
    level 20 pinned from depths (1,2); depths 3 and 4 hold out OK
    T(41,21) = 12639811314502944123098075912198   (level 20, at onset)
    T(41,20) = 18004779862205054677763902712770   (level 21, depth 2)
    a(41) recount = 393811462683918679824582849262105  -- AGREE

Because it never touches the wired table, the agreement also says
`diagCoeffTable` is consistent with a fresh fit to its own onset anchors. This
is a second implementation, not a second source: it retires assembly,
transcription, fencing and arithmetic error across two codebases, but shares
with the main route the D_j at k = 20, 21, the pinning cells T(40,19) and
T(39,18), and the product form (proved in Lean, so a shared theorem
rather than a shared risk).

### A check on D_2(21), modulo one prime power

T(41,20) = P_21(41)·3^(41−1−63) + D_2(21), and D_2(21) =
1534183878653401344302049616588 / 94143178827 with 94143178827 = 3^23.
Integrality of T(41,20) therefore forces P_21(41) + N ≡ 0 mod 3^23. The
assembler asserts this. It is a check modulo one prime power only.

## Level 21 and depth 5

T(41,20) sits on level 21. At depths j ≤ 4, level 21 pins from a single
depth pair with no independent check at its own level:

    level k=20 pinned from [(36,16), (37,17), (38,18), (39,19)], 6 pairs, 5 independent checks
    level k=21 pinned from [(39,18), (40,19)],                   1 pair,  0 independent checks

The congruence check (`gate-below-onset-fit-congruence`) constrains only the
fractional part of D_4(21). A shift Δ in D_4(21) moves T(41,20) by 9Δ, and
every single-entry error in the e = 3 row of
`results/cluster_weight_families_K22_e3.txt` enters D_4(21) with a
coefficient in (1/9)Z, so every error that table can carry is an integer
shift of a(41), invisible to an integrality test. Measured on a shadow copy
of the table: `sig[3][21] + 9` leaves the congruence check green and moves
the depth-4 assembly's a(41) by exactly 9. The exposed entries are three
integers, `sig`, `bb`, `pp` at e = 3, k = 21: the k = 22 row is truncated
away by `D_series(4, 21)` and the k = 20 row is pinned by level 20's pair
agreement.

At depth 5, `results/cluster_weight_families_K21_e4.txt` supplies D_5 and
level 21 gains T(38,17), a cell the coloring recount also covers:

    python3 experiments/below_onset_fit_a41.py --jmax 5 --perheight results/a41
    level k=20 pinned from [(36,16), (37,17), (38,18), (39,19)] (tallest H=19), 6 pair(s), 5 independent check(s)
    level k=21 pinned from [(38,17), (39,18), (40,19)] (tallest H=19), 3 pair(s), 2 independent check(s)
    sweep vs banked triangle: 760 cells agree, 0 disagree
    a(41) = 393811462683918679824582849262105

(That run read heights 1..19 only: 760 = 19 × 40 positions.)

`pp[3][21]` enters D_4(21) but not D_5(21), and `sig`, `bb` enter the two
with different coefficients, so any single-entry error in that row makes
the three pairs disagree and `build()` refuses. Also at depth 5:
`below_onset_fit.py --verify --jmax=5` re-derives 18 levels exactly over 160
depth pairs, 0 wrong; `--audit --jmax=5` predicts 342 cells from shorter
cells, 189 of them enumerated, 0 wrong.

`make gate-below-onset-fit-pairs` (`experiments/below_onset_fit_pairs_gate.py`) rebuilds
the depth-5 assembly with the pin cells and pair counts fixed, requires
a(41) from `h*.out` plus the formulas to equal the value above, and carries
six controls that must each be refused: the +9 mutation above, `bb` and
`pp` at (3, 21), the K21_e4 table's own e = 4 row, a corrupted pin cell,
and the enumerated T(41,20) + 1 in a shadow copy of this directory.

## The enumerated T(41,20)

Three pairs agreeing is agreement between fits that share D_j(20..21) and
the product form, not an enumeration. The H = 20 run above supplies the
enumeration:

    T(41,20) = 18004779862205054677763902712770    enumerated
    T(41,20) = 18004779862205054677763902712770    formula, level 21 depth 2

The run's rows at n ≤ 40 agree with `results/triangle.txt` on all 40 cells
of column H = 20, including T(40,20) (same program at a different Nmax, so
a regression rather than a second source). `gate-below-onset-fit-pairs` also
compares the enumerated T(41,20) with the formula's prediction, built
without that cell among its pins.

With height 20 enumerated, a(41) no longer depends on P_21 (H = 21 is level
20 at onset, pinned ten ways at depth 5 once T(40,20) joins its pins), and
the top level of the assembly has a check that crosses assumption families.
Heights 21..41 are still formula, and the coloring recount stops at H = 19,
so T(41,20) has one enumeration and one formula prediction, not two
enumerations.
