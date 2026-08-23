# Resume here — 2026-08-23, 09:30 EDT

Written to survive a `/clear`. If you are picking this up cold:

1. **`results/confidence.md`** — how far each value of A006770 can be trusted
   and why, in plain terms. Read it first.
2. **`HANDOFF.md`** — the live state, newest section first.
3. **`docs/time-at-the-bar-report.md`** — what the last full round did, which
   items it struck, and the runs it priced and did not launch.
4. This file — the jobs running right now and exactly what to do when each
   lands.

**All four overnight runs have landed**; their results are in
`docs/state-2026-08-23.md` §4 and in the files named there. Six jobs are running
now: the census three ways, and the three items §5 listed as priced-and-
unlaunched that needed no decision from jasonp.

The previous version of this file described the Motley ladder and two Skeleton
Key probes of 2026-08-20. All three landed; their protocols are in
`results/cutcount_b1/rows41/README.md`, `results/skeletonkey-cell-sparsity.md`
and `results/skeletonkey-parametric-master.md`, and nothing there still needs
doing.

---

## Jobs running, at 09:30 EDT

| host | job | pid | expect | output |
|---|---|---|---|---|
| dalby | `nkey_census 17`, **pre-fix binary** (rev a825ad1) | 2940920 | started 23:45, ~15 h total | `~/var/nkey-census/census.txt` |
| dalby | `nkey_census 17`, post-fix (rev 95fbb6c) | 2943918 | ~15 h from 09:27 | `~/var/nkey-census-postfix/census.txt` |
| dalby | `severance_w3_families families 21 4 8` | 2943921 | 3.1-6.7 h from 09:27, 8.5-16.1 GB | `results/severance_w3_families_K21_e4.txt` (planned, written by the run) |
| dalby | `dmirror_spine_ladder.sh 20 21 6` | 2943897 | S=20 ~6.6 h, S=21 ~23 h from 09:27 | `~/var/dmirror-spine-2021/split.txt` |
| ayr | `nkey_census 16`, re-run under the corrected retirement rule | 699744 | ~3 h from 08:42 | `~/tmp/census16_check.txt` |
| ayr | `exactchange_minauto.py 13` | 700968 | ~2 h from 09:28, ~31 GB | `~/var/minauto-h13/rank.txt` |

Everything below the census pair was launched 2026-08-23 09:27 on jasonp's
"everything you can do on your own that is waiting on me can run".

**When the ayr census lands:** it must return **346,539**. That is the number
the pre-fix binary produced, and this run exists to confirm the retirement fix
did not change it — the fix reproduced H = 14 and H = 15 exactly, and H = 16 is
the one height that had not been re-checked. If it differs, H = 16 and H = 17
are both suspect and `results/nkey-census.md` must be corrected before anything
else.

**When the two dalby censuses land:** they must agree. The in-flight one is
stamped rev `a825ad114`, which **predates the retirement fix `384bd2e`** — so
its H = 17 is a pre-fix number, exactly as unchecked as the pre-fix H = 16.
Rather than kill six hours of it, the post-fix run goes alongside on an idle
core; agreement banks H = 17 from two binaries. On agreement, add H = 17 to
`results/nkey-census.md`'s table and ratio ladder and **stop the ladder there** —
the ladder loop (pid 2935694) was killed 09:26 so no H = 18 follows it, since
H = 18 is three days for one more anchor on a fit already good to a thousandth.
What would actually reach H = 21 is the shared-partial-fill build.

**When the depth-5 table lands:** run
`python3 experiments/severance_w3_depth5_gate.py` — it has been RED in
production for one reason, that no `severance_w3_families_K*_e4.txt` with
K >= 19 exists, and this is that file. Green closes review row B13, which
`docs/state-2026-08-23.md` §5 names as the blocker on the five-terms decision.
Red is the more interesting outcome and stops the depth-5 route where it stands.
The table's arrival does not license using `D_5` at k = 21; the gate does.

**When the spine ladder lands:** `python3
experiments/dmirror_spine_cumulants.py` and `..._degrees.py` over the
concatenated logs, for `c_6` on `d_main`. Note the binary now carries the
4-bit label guard (`1a2ccac`) that the S <= 19 runs did not — if it fires, that
is a finding about the earlier rows, not just about S = 20.

**When the H = 13 rank lands:** A034299 predicts **3643**. The script asserts
every banked rank up to H = 12 before it prints 13, so a wrong build cannot
report one. Whatever it returns it is single-source and
`results/exactchange-probes.md` §7 keeps it at suggestive until a second
implementation reproduces it.

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
