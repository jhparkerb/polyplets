# rows41 — the Motley ladder at Nmax = 41

`C1.out` .. `C19.out`: the cut-count totals `C_H(n)` for n = 1..41, one file
per height, produced by the colouring program (Motley) — the second source
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

Row 41 shows "0 agree with the incumbent" because the incumbent has no
per-height data at n = 41 — that is the point. The row is built from Motley
cells plus tower formulas fitted to Motley's own data, and it reproduces the
banked a(41) digit for digit.
