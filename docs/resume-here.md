# Resume here — 2026-08-23, 09:00 EDT

Written to survive a `/clear`. If you are picking this up cold:

1. **`results/confidence.md`** — how far each value of A006770 can be trusted
   and why, in plain terms. Read it first.
2. **`HANDOFF.md`** — the live state, newest section first.
3. **`docs/time-at-the-bar-report.md`** — what the last full round did, which
   items it struck, and the runs it priced and did not launch.
4. This file — the jobs running right now and exactly what to do when each
   lands.

**Three of the four overnight runs have landed**; their results are in
`docs/state-2026-08-23.md` §4 and in the files named there. What is left running
is the census, twice.

The previous version of this file described the Motley ladder and two Skeleton
Key probes of 2026-08-20. All three landed; their protocols are in
`results/cutcount_b1/rows41/README.md`, `results/skeletonkey-cell-sparsity.md`
and `results/skeletonkey-parametric-master.md`, and nothing there still needs
doing.

---

## Jobs running, at 09:00 EDT

| host | job | pid | expect | output |
|---|---|---|---|---|
| dalby | `nkey_census 17` | 2935694 | ~9 h left as of 08:52 | `~/var/nkey-census/census.txt` |
| ayr | `nkey_census 16`, re-run under the corrected retirement rule | 699744 | ~3 h from 08:42 | `~/tmp/census16_check.txt` |

**When the ayr run lands:** it must return **346,539**. That is the number the
pre-fix binary produced, and this run exists to confirm the retirement fix did
not change it — the fix reproduced H = 14 and H = 15 exactly, and H = 16 is the
one height that had not been re-checked. If it differs, H = 16 and H = 17 are
both suspect and `results/nkey-census.md` must be corrected before anything
else.

**When the dalby run lands:** add H = 17 to `results/nkey-census.md`'s table and
its ratio ladder, and stop the ladder there. H = 18 is three days by the
measured cost ratio and buys one more anchor on a fit that is already good to a
thousandth; the thing that would actually reach H = 21 is the shared-partial-fill
build described in that file.

---

## Landed overnight, kept here for the protocol
## 1. The depth-6 K-ladder (dalby) — the one that changes a plan

**What it settles.** `J = 6` is the only asserted number in the five-terms
table (`docs/time-at-the-bar-report.md` B2), at ~20–60 h and ~50–100 GB, got by
applying a per-excess ratio once to `J = 5`'s projection. Depth 5 was asserted
the same way at 16 h / 103 GB and measured at 3.1 h / 8.5 GB, an order of
magnitude out. Four rungs at fixed 8 threads is what settled depth 5 and this
is the same ladder at `emax = 5`.

**Measured so far**, against the header's predictions:

| K | predicted | measured |
|---|---|---|
| 8 | ~45 s, ~0.8 GB | **40.0 s, 0.42 GB** |
| 10 | ~6 min, ~2.8 GB | **369.5 s, 2.28 GB** |
| 12 | ~25 min, ~7 GB | **1951.1 s, 7.23 GB** |
| 14 | ~1.4 h, ~15 GB | in flight, 12.5 GB at level 7 of 14 |

**When it lands:** fit the K-slope at `emax = 5` the way
`results/depth5-cost-settled.md` did at `emax = 4`, extrapolate to `K = 21`,
and re-run B2's table with `J = 6` measured instead of asserted. The row that
matters is `Hs = 20` with `J = 6` reaching `n ≤ 45` against a 277 GB pole,
versus `Hs = 21` at 580 GB, which does not fit dalby's 563 GB free.
**Whether any of it then runs is jasonp's call, and the write-up should say so
rather than implying a launch.**

Review row B13 is unaffected and still stands: the depth-5 gate must pass at
`k ≤ 19` before `D_5` is used at `k = 21`, and it is correctly RED until the
`emax = 4` table exists.

## 2. The frontier census (dalby)

**Already banked**: H = 14 = 53,763 and H = 15 = 136,145, in
`results/nkey-census.md`, with both gates green.

**When H = 16 lands:** add the row to that file's table and to its ratio
ladder. Do not extend the run past H = 17 without a decision — wall time is
6.7× per height (293 s at 14, 1,960 s at 15), so H = 17 is a day and H = 18 a
week. Reaching H = 21 needs partial fills shared between source states rather
than rebuilt per source, which is what the production engine's carry does. That
is a build.

## 3. The spine split S = 19 (dalby)

**The question is already answered** and S = 19 is a holdout rather than a
decider: `results/dmirror-spine-split.md` has `d_main` linear at `c_2`, `c_3`
and `c_4`, and `d_anti` failing at `c_3`, so A1.3 is closed and the obstruction
is the anti-diagonal family specifically.

**When it lands:** append its rows to the combined log and re-run

    python3 experiments/dmirror_spine_cumulants.py LOG
    python3 experiments/dmirror_spine_degrees.py LOG

The degree readings predict `d_main` at degree `⌊k/2⌋` and `d_anti` at degree
`k` per parity; S = 19 adds an odd-parity point to both. A disagreement there
would be a finding, since those readings have held as predictions twice.

## 4. The n = 11 hole count (ayr)

**Predicts 5.** `results/maxhole-closed-form.md` identifies the maximum number
of holes an n-cell polyplet can enclose as `n − ⌈2√n⌉ + 1`, which is
\oeis{A248333}, matching all ten measured terms with the lower bound proved by
construction and the reverse inequality open. n = 11 is the first term the
formula did not see.

**When it lands:** if it is 5, add the term to that file and to
`results/king-extremal.md`, and the formula has its first real test. If it is
not 5, that is the more interesting outcome and the formula is refuted at the
first opportunity — say so plainly, in the file, before anything else.

The run also re-derives `a(11)` for the king lattice, which A006770's banked
list does not reach in the probe's own table; the RED control now compares only
where the reference reaches and says so.
