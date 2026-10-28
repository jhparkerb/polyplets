# rows41: the coloring recount at Nmax = 41

`C1.out` .. `C19.out`: the totals `C_H(n)` for n = 1..41, one file per
height, computed by the coloring program (`../PROVENANCE.md`), the second
enumerator that never decides connectivity.

`T(n,H) = C_H − 2C_{H−1} + C_{H−2}` needs every `C_H` at the same Nmax.
`../rows/` is the Nmax-40 set and is cited throughout the tree; it cannot
supply n = 41. Do not overwrite it, and do not mix the two sets in one
difference.

    run       dalby, 2026-08-20 10:38 to 2026-08-21 08:43 (about 22 h)
    script    scripts/motley_ladder.sh
    rev       18b90ab6
    method    9 primes near 2^16 per height, Chinese remainder theorem to exact
    check     8 primes reconstruct; the 9th is held out and must predict
              every cell; scripts/motley_crt.py exits non-zero if it does
              not. All 19 heights passed. Its --selftest reproduces the
              stored C_18 from 4 primes and includes a control that corrupts
              a residue and confirms the held-out prime catches it.
    files     the 171 residue rows in `../residues41/`; the run's
              timings.txt, console.H*.log, census.H*.log and
              sizes.H*.N41.txt in `run/`, copied from dalby with sha256
              verified on both sides (249 files, 0 mismatches).
              `make gate-cutcount-assembly` re-derives the held-out verdict
              at every height from those files, and
              `scripts/motley_crt.py --selftest` covers C_19.

## What these rows settle for the provenance table

These rows extend the coloring recount's reach from H ≤ 18 to H ≤ 19,
which `scripts/provenance_table.py` now derives from the files. The cells
with no exact recount and no closed form drop from six to three
<!--q:congruence_only.count@19=3-->:

    T(39,20), T(40,20), T(40,21)
    <!--q:congruence_only.cells@19=(39,20),(40,20),(40,21)-->

The three retired are T(38,19), T(39,19) and T(40,19), each now computed
directly by the second program.

## What these rows settle for rows 39..41

    python3 experiments/below_onset_fit_ri.py --hmax 19 --jmax 4 \
            --rowdir results/cutcount_b1/rows41 --rows 39,40,41

    row 39: COMPLETE, sum MATCHES a(39)   (20 cells agree with the main computation)
    row 40: COMPLETE, sum MATCHES a(40)   (21 cells agree, 0 wrong)
    row 41: COMPLETE, a(41) = 393811462683918679824582849262105

`T(40,19)` from these rows is 3247572468599336484342102174163, the value in
`results/ns_a40/perheight/h19.out`. All nineteen heights agree with the
main computation at n = 40.

Row 41 shows "0 agree" because `below_onset_fit_ri.py` compares formula cells
(H ≥ 20) against `results/triangle.txt`, which stops at n = 40. The main
computation's n = 41 data, `results/a41/` h1..h19.out, are enumerated
heights, and those nineteen cells are compared against these rows by
`make gate-cutcount-assembly` (19 of 19 agree). Row 41 here is built from
the coloring recount's cells plus the closed forms of
`docs/proofs/diagonal-law.md` with constants fitted to the coloring
recount's own data, and it reproduces a(41) digit for digit. Heights 1..19
therefore have two sources with no shared code; heights 20 and up are one
formula strategy, pinned from this program's data but sharing the depth
tables `D_j(20..21)` with the main computation's formula.
