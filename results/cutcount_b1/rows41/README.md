# rows41 — the Motley ladder at Nmax = 41

`C1.out` .. `C19.out`: the cut-count totals `C_H(n)` for n = 1..41, one file
per height, produced by the coloring program (Motley) — the second source
that never decides connectivity.

**Why this set exists alongside `../rows/`.** `T(n,H) = C_H - 2C_{H-1} +
C_{H-2}` needs every `C_H` computed at the *same* Nmax. `../rows/` is
Confetti's Nmax-40 set and is cited throughout the tree; it cannot supply
n = 41. Do not overwrite it, and do not mix the two sets in one difference.

    run       dalby, 2026-08-20 10:38 -> 2026-08-21 08:43 (~22 h)
    script    scripts/motley_ladder.sh from the worktree ~/src/pm-run
    rev       18b90ab6
    method    9 primes near 2^16 per height, CRT to exact
    check     8 primes reconstruct, the 9th is held out and must predict
              every cell; scripts/motley_crt.py exits non-zero if it does not.
              All 19 heights passed. Its --selftest reproduces the banked
              C_18 from 4 primes and has a RED control that corrupts a
              residue and confirms the held-out prime catches it.
    banked    2026-09-05 (AUDIT-2026-09-02 M3): the 171 residue rows are in
              `../residues41/`, the run's own timings.txt, console.H*.log,
              census.H*.log and sizes.H*.N41.txt in `run/`, copied from
              dalby:~/var/motley-ladder with sha256 verified on both sides
              (249 files, 0 mismatches). `make gate-cutcount-assembly` now
              re-derives the held-out verdict at every height from those
              files, and `scripts/motley_crt.py --selftest` covers C_19.

## What these rows settle for the provenance table

These rows raise Motley's rule-independent reach from H <= 18 to **H <= 19**,
which is what `scripts/provenance_table.py` now derives rather than carrying as
a hand-edited constant. The cells with no exact recount and no closed form
drop from six to **three** <!--q:congruence_only.count@19=3-->:

    T(39,20), T(40,20), T(40,21)
    <!--q:congruence_only.cells@19=(39,20),(40,20),(40,21)-->

The three retired are T(38,19), T(39,19) and T(40,19), each now computed
directly by a second program that never decides connectivity.

## What these rows settle

    python3 experiments/undertow_ri.py --hmax 19 --jmax 4 \
            --rowdir results/cutcount_b1/rows41 --rows 39,40,41

    row 39: COMPLETE, sum MATCHES a(39)   (20 cells agree with the incumbent)
    row 40: COMPLETE, sum MATCHES a(40)   (21 cells agree, 0 wrong)
    row 41: COMPLETE, a(41) = 393811462683918679824582849262105

Row 40's last uncovered cell is closed here: `T(40,19)` from these rows is
3247572468599336484342102174163, which is the incumbent's value in
`results/ns_a40/perheight/h19.out`. All nineteen heights agree with the
incumbent at n = 40.

Row 41 shows "0 agree with the incumbent" because `undertow_ri.py` compares
tower cells (H >= 20) against `results/triangle.txt`, which stops at n = 40;
the incumbent's n = 41 data, `results/a41/` h1..h19.out, are the swept heights,
and those nineteen cells are compared against these rows by
`make gate-cutcount-assembly` (19 of 19 agree). The row is built from Motley
cells plus tower formulas fitted to Motley's own data, and it reproduces the
banked a(41) digit for digit. What that is worth: heights 1-19 two-source with
no shared code; heights 20 and up one tower strategy pinned from Motley's data,
sharing `D_j(20..21)` with the incumbent's tower (AUDIT-2026-09-02 M2).
