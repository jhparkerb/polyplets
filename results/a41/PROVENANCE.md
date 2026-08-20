# a(41) provenance

    a(41) = 393811462683918679824582849262105

Computed 2026-08-20 on dalby, branch `lastditch`. **The first term of A006770
past a(40)** — and the first computed without sweeping the two tall poles.

## How

Two halves, per `results/undertow.md`:

- **heights 1..19, real sweep**, `scripts/dalby_a41_low.sh`:
  `orchestrate --maxn 41 --kernel kink --counter u128 --cores 40 --ram 1GiB
  --overlap-heights 19 --heights 1-19`. Rows in `results/a41/h*.out`.
  **wall 16,998.7 s (4.72 h) on 40 cores, cpu 605,643 s, rss_max 557 MB**,
  run-dir peak well under 100 GB.
- **heights 20..41, the diagonal tower**, `experiments/undertow_a41.py`:
  levels k = 41-H = 0..21, with k <= 19 from the wired table and k = 20, 21
  pinned from BELOW-onset cells (Undertow). `T(41,20)` is depth 2 on level 21,
  so it carries the exact `D_2(21)` defect; `T(41,21)` is exactly at onset on
  level 20.

The classical rule would have needed a real sweep to H = 21 at Nmax 41 — the
a(40) run's two tall phases were 9.6 h/48c and 36.4 h/32c with a **363.4 GB**
disk peak. Neither was run.

## Checks, all of them

- **The sweep's own regression: 760 banked cells agree, 0 disagree.** A run at
  Nmax 41 also re-produces every row n <= 40 at every height it sweeps, and
  those rows are banked. `undertow_a41.py` refuses to use the n = 41 row unless
  they match and unless at least 200 cells were compared.
- **Row-40 regression, on a separate tower with row 40 excluded from its own
  pinning set**: 21 cells reproduced, 0 wrong, and the banked row re-sums to
  a(40) exactly. Two towers are built deliberately — pointing one at both jobs
  makes the regression either circular or vacuous.
- **Edges exact**: `T(41,41) = 3^40` and `T(41,40) = (25n-45)*3^37`.
- **Growth**: `a(41)/a(40) = 6.9394`, continuing 6.9212, 6.9261, 6.9308,
  6.9352. The successive differences are 0.0049, 0.0047, 0.0044, **0.0042** —
  monotonically shrinking, as a series converging to λ ≈ 7.1 must.
- The method itself: 18 levels re-derived exactly over 100 depth pairs, a
  342-cell audit, and a(40)/a(39)/a(38)/a(37) reassembled exactly from short
  sweeps. `results/undertow.md`.

## Independently recomputed

Lane B of the review (`results/undertow-review-B.md` §5,
`experiments/lane_b_a41_recount.py`) rebuilt the term by a route built to
differ wherever difference was possible: levels k = 1..19 pinned from their two
**onset anchors** in `results/triangle.txt` rather than read from
`diagCoeffTable`, level 20 pinned from depths (1,2) with (3,4) held out — a
different overdetermination cut from the assembler's — and its own polynomial,
grand-form, solver and assembly code throughout. `undertow_a41.py` is never
read or imported.

**AGREE**, and the lead re-ran it rather than taking the report's word:

    anchor-pinned k<=19 predict banked in-onset cells: 342 ok, 0 wrong
    imported D_j vs own empirical extraction at k<=19: 70 ok, 0 wrong
    level 20 pinned from depths (1,2); depths 3 and 4 hold out OK
    T(41,21) = 12639811314502944123098075912198   (level 20, at onset)
    T(41,20) = 18004779862205054677763902712770   (level 21, depth 2)
    a(41) recount = 393811462683918679824582849262105  -- AGREE

Because it never touches the wired table, the agreement additionally says the
wired `diagCoeffTable` is consistent with a fresh fit to its own onset anchors.

**What the agreement is worth, in Lane B's own grading: CLEAN as a second
implementation, NOT a second source.** It retires assembly, transcription,
fencing and arithmetic error across two disjoint codebases — the class that
produced the Zero Harvest incident and the lead's own `hmax` bug tonight. It
does not touch what the two routes share: `D_j` at k = 20, 21, the pinning
cells `T(40,19)`/`T(39,18)`, and the grand-form theorem (Lean-complete, so
shared *theorem* rather than shared *risk*).

### One real, weak check on D_2(21)

`T(41,20) = P_21(41)*3^(41-1-63) + D_2(21)` — the main term carries `3^-23`,
and `D_2(21) = 1534183878653401344302049616588 / 94143178827` with
`94143178827 = 3^23` exactly. Integrality of `T(41,20)` therefore forces
`P_21(41) + N == 0 mod 3^23`. It is weak and it is mod a single prime power,
but it is **the only check `D_2(21)` currently has**, and the assembler's
integrality assert is what enforces it.

## The one weak point, stated plainly

`T(41,20)` sits on level 21, and **level 21 pins from a single depth pair** —
`T(40,19)` and `T(39,18)` — with **no independent check at its own level**:

    level k=20 pinned from [(37,17), (38,18), (39,19)], 3 pairs, 2 independent checks
    level k=21 pinned from [(39,18), (40,19)],          1 pair,  0 independent checks

Every other level in the tower is either wired-and-long-validated or, at
k = 20, overdetermined. Level 21 is not. Two things would fix it, neither run:

- **sweep H = 20 at Nmax 41** (`scripts/dalby_a41_h20.sh`, ~20-30 h, ~450 GB):
  `T(41,20)` becomes a swept value and P_21's prediction of it becomes a real
  holdout against an enumeration;
- **depth 5** (`families 21 4`, ~16 h, ~103 GB): level 21 gains a second pin
  pair from `T(38,17)` — agreement rather than a holdout.

Until one of those runs, a(41) should be quoted as computed-and-checked but
**not** as carrying the validation a(40) does.
