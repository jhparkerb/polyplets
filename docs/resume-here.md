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

## Landed overnight — results, and where each is written up

Kept short: each is banked in a results file, and that file is the record.

**Depth-6 K-ladder** (dalby, 2.2 h for four rungs) — `families 21 5` projects to
~36 h and ~74 GB at 8 threads, so the asserted 20–60 h / 50–100 GB holds.
`results/depth6-cost-settled.md`, analysis `experiments/depth6_cost_ladder.py`,
which imports depth 5's extrapolator so the two are priced by the same
arithmetic. Rerun it with `python3 experiments/depth6_cost_ladder.py`.

**n = 11 hole count** (ayr, 4.28 h, 62.7 GB) — returned **5**, the formula's
prediction, and `a(11) = 39,299,408` matching A006770.
`results/maxhole-closed-form.md`.

**Spine split S = 15..19** (dalby) — `d_main` linear at `c_2`..`c_5`, `d_anti`
failing at `c_3`, and the `⌊k/2⌋` degree reading holding at seven consecutive
levels. `results/dmirror-spine-split.md`. To re-derive, concatenate the three
split logs under `~/var/dmirror-spine*/` and run
`experiments/dmirror_spine_cumulants.py` and `experiments/dmirror_spine_degrees.py`
over the result.

**Frontier census H = 14, 15, 16** — 53,763, 136,145, 346,539.
`results/nkey-census.md`.
