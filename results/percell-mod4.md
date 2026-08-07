# Per-cell mod 4: the algebra, checked on 528 cells instead of 78

2026-08-07, gympie. Companion to `results/subgroup-mod4.md`, which ships the
per-cell **mod 2** bit on all 820 cells of the a(40) triangle and explains at
length why the mod-4 refinement is **not** being bought at n=40. This file is
the other half: the refinement's algebra and engines, and the run that checked
them at scale.

**Headline: 528 cells — the entire n ≤ 32 triangle — 0 mod-2 mismatches and
0 mod-4 mismatches, with both `--byheight` tables reproducing the banked
per-element `Fix(g)` exactly at every n ≤ 32.**

This is a validation of the *checker*, not new coverage of a(40). The n=40
decision is unchanged and is not reopened here.

## The identity

`D2ax = {e, h, v, r180}` is exactly the height-preserving subgroup of `D4`, so
it acts on the animals of each fixed height separately and orbit sizes there
divide 4:

```
T(n,H) = m1 + 2 m2 + 4 m4,      m1 = I_H(D2ax)

  ==>  T(n,H) = I_H(D2ax)                                       (mod 2)
  ==>  T(n,H) = I_H(<h>) + I_H(<v>) + I_H(C2) - 2 I_H(D2ax)     (mod 4)
```

The mod-4 line is the three order-2 subgroups of `D2ax` — `<h>`, `<v>` and
`C2 = <r180>` — summed, since `2 m2` is their `I_H` total minus `3 I_H(D2ax)`.

## Why the run exists

The mod-4 refinement was confirmed on **78 cells (n ≤ 12)** and nowhere else.
That is not enough to trust an algebraic identity, and the reason is on the
record: the **mod-8 companion in `subgroup-mod4.md` shipped with both factors
of 2 dropped** and failed on 21 of 33 rows. It was caught only because it was
printed against banked data. The mod-4 line had a gate and was right; the mod-8
line had none and was not.

So this run extends the same check by **6.8x** in cells, over a range where a
sign or coefficient error has room to show up. It was never an attempt to reach
n=40.

## The engines

`symtm` grew a `--byheight` flag on two modes:

- **`hmirror --byheight`** emits `n H W count`. Summing over `W` gives
  `I_H(<h>)`; grouping the **same table** by `W` instead gives `I_W(<v>)`,
  because transposing an h-symmetric `W x H` animal yields a v-symmetric
  `H x W` one. One sweep, two of the three inputs.
- **`r180 --byheight`** emits `n H count` with the **true height**. Its
  transpose weight is split one-at-`H` and one-at-`W` because the strip label
  is *not* the height for this mode — the one place the two modes differ, and
  the reason r180 gets its own emitter rather than reusing hmirror's.

`I_H(D2ax)` is the fourth input and was already banked to n=40 by
`symcount_fast --byheight` (`results/subgroup_d2ax_byheight.txt`, 630 rows).
**No subgroup sweep was rerun for this.**

The gate (`tests/gate_subgroup.py`, section 6) carries a control for the one
mistake the transpose exists to avoid: substituting `I_H(<h>)` for `I_H(<v>)`
— reusing the height grouping for both mirrors — must break the congruence,
and it does.

## The run

`scripts/percell_mod4.sh 32 8`, gympie, 8 threads, 2026-08-07
15:39:03–16:08:49 EDT. Log `results/percell_mod4_20260807.log`. Binary stamp
`git=cd96795-dirty`, built 15:13:18; the `symtm` working tree it was built
from is what landed as `ffd0c2b`.

| phase | wall | CPU | speedup on 8 thr | peak RSS | rows out |
|---|---|---|---|---|---|
| `hmirror --byheight` | 1180.6 s (19.7 min) | 5498.4 s | 4.66x | 3890.1 MB | 4693 |
| `r180 --byheight` | 605.2 s (10.1 min) | 2758.0 s | 4.56x | 3233.1 MB | 408 |
| **total** | **1785.8 s (29.8 min)** | | | | |

**The cost prediction held.** The script header predicted ~20 min / ~8 min /
~30 min by extrapolating measured N=24 and N=28 sweeps over four terms, and
warned that the same style of estimate underpredicted `symcount_fast` by 4.5x.
It did not repeat here: hmirror landed at 19.7 min against 20 predicted, r180
at 10.1 against 8 (1.26x over), total 29.8 against 30. Two-mode transfer-matrix
cost extrapolates over a short range; the DFS engine's did not.

Note the memory contrast with the subgroup census in `subgroup-mod4.md`:
**3.9 GB here against 4.6 MB there**. `symtm` holds a strip frontier;
`symcount_fast` is a DFS over a quotient domain. Same triangle, four orders of
magnitude apart in RSS.

## Results

**Regression, first — the check that would catch a broken emitter:**

```
hmirror byheight sums vs banked flat, n<=32: identical
r180    byheight sums vs banked flat, n<=32: identical
```

Both `--byheight` tables collapse to the per-element `Fix(g)` counts banked in
`results/sym_counts.txt` at every n ≤ 32 (at n=32, `Fix(h) = 2546382907164`
and `Fix(r180) = 7063812264280`). A `--byheight` mode that mis-assigns heights
but conserves totals would pass this and fail the per-cell check below; one
that loses animals fails here first.

**Per cell, against the production a(40) triangle:**

|    band | cells | mod-2 mismatches | mod-4 mismatches |
|---|---|---|---|
|   H1-10 |   275 | 0 | 0 |
|  H11-14 |    82 | 0 | 0 |
|  H15-19 |    80 | 0 | 0 |
|    H20+ |    91 | 0 | 0 |
| **TOTAL** | **528** | **0** | **0** |

528 = 32·33/2, so this is **every cell of the triangle at n ≤ 32**, not a
sample of it.

One asymmetry worth recording because it looks like a bug and is not:
`I_H(<v>)` covers all 528 cells while `I_H(<h>)` and `I_H(C2)` cover only 408.
The missing entries are genuine zeros — there is no h-symmetric or
r180-symmetric animal at those `(n,H)` — and the assembler reads them as 0.
The flat regression above is what pins that reading, since a spuriously absent
nonzero row would break the totals.

## The r180 cost curve, confirmed independently at N=32

`subgroup-mod4.md`'s reason 2 for not buying n=40 is that **r180's cost peaks
on exactly the H=15..19 band that needs covering**, measured from
`results/symtm_strip_profile_n40.txt`. This run reproduces that shape at N=32
without being designed to. Per-strip cost, derived from heartbeat completion
times:

```
r180      slowest: H=21 176s   H=12 86s   H=15 73s   H=20 68s   H=17 42s
          cheapest tall: H=28, H=29, H=30 all under 0.5s
hmirror   slowest: H=31 217s   H=26 204s  H=32 194s  H=27 164s
```

The two modes have **opposite** curves: hmirror is tall-peaked, r180 is
middle-peaked and collapses on tall strips, because the transpose restriction
forces `W >= H` and as `H` approaches `n` every column is pinned to a single
cell. "Cover H ≤ 19 using only the cheap short strips" therefore does not
survive contact with r180, at N=32 as at N=40.

## What this does and does not establish

- **Does:** the mod-4 identity, both `--byheight` emitters, and the transpose
  trick that produces `I_H(<v>)` from the hmirror table are correct on the
  whole n ≤ 32 triangle. The kind of error that killed the mod-8 companion's
  first version would have surfaced here.
- **Does not:** add any coverage of a(40). Every cell here has n ≤ 32 and was
  already second-sourced. The 43.84% band of a(40) still carries exactly the
  one bit per cell that `subgroup-mod4.md` banks, and that remains, per that
  file, realistically the only independent evidence it will ever carry.
- **Does not** reopen the n=40 decision. The third input `I_H(<v>)` still has
  no bounded-height route short of a new vmirror sweep mode, r180 still peaks
  on the band that needs it, and the second bit still hardens only the
  single-cell failure mode this project has never had. See
  `subgroup-mod4.md` §"why it is NOT being bought at n=40".

## Artifacts

- `results/percell_raw/hmirror.byheight.n32.out` — `n H W count`, 4693 rows
- `results/percell_raw/r180.byheight.n32.out` — `n H count`, 408 rows
- `results/percell_mod4_20260807.log` — the run log, both phases
- `scripts/percell_mod4.sh`, `experiments/percell_mod4.py`
- `tests/gate_subgroup.py` §6 — the n ≤ 8 / n ≤ 11 gate and its transpose
  control
- `results/subgroup_d2ax_byheight.txt` — the fourth input, banked to n=40,
  not rerun
