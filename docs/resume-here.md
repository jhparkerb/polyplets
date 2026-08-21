# Resume here — 2026-08-20, 15:15 EDT

Written to survive a `/clear`. If you are picking this up cold:

1. **`results/confidence.md`** — how far each value of A006770 can be trusted
   and why, in plain terms. Read it first.
2. **`docs/lastditch-campaign.md`** — the campaign record behind it.
3. **`docs/skeletonkey-reprompt.md`** — the kill inventory, the twenty-row
   breadth pass, and **the v2 prompt**, which is the one to use. Do not run
   another breadth pass; v2 replaces it with three triage tests and a
   three-box placement.
4. This file — the jobs still running and exactly what to do when they land.

---

## Jobs running, at 15:15 EDT

| host | job | pid | started | expect | output |
|---|---|---|---|---|---|
| ~~dalby~~ | ~~Motley ladder H = 1..19 @ Nmax 41~~ | — | 08-20 10:38 | **LANDED 08-21 08:43** | banked, see below |
| ayr | `cell_sparsity_modp.py 8` | 640243 | 12:11 | overdue, healthy | `~/var/skeletonkey/cellsparse.txt` |
| ayr | `parametric_master.py 4` | **641839** | 14:28 | king leg, ~2 h on the measured king/hex ratio | `~/var/skeletonkey/parametric_master_k4.txt` |

Nothing here needs restarting. **Do not restart the ladder** under any
circumstance short of a dead box — see `a21-run-do-not-restart`.

---

## 1. The Motley ladder (dalby) — LANDED 2026-08-21 08:43, ~22 h

**Done, and it did what it was launched for.** All nineteen heights, nine
primes each, "LADDER COMPLETE H=1..19 Nmax=41". The four steps below were all
run; the record is `results/cutcount_b1/rows41/README.md` and the rewritten
items 3 and 4 of `results/confidence.md`.

    CRT       19/19 heights exact; held-out prime correct at every cell
    row 40    COMPLETE, sum MATCHES a(40) -- GAP [], all 40 cells
    row 41    COMPLETE, 393811462683918679824582849262105 -- as expected
    T(40,19)  3247572468599336484342102174163 == incumbent h19.out
              (and all 19 heights agree with the incumbent at n = 40)

Nothing below this line still needs doing. It is kept because it is the
protocol, and the next ladder at another Nmax runs the same way.

### The launch record, for reuse

**Heights 1..19 at Nmax 41.** dalby, tmux session 0, window `ladder`. Script
`scripts/motley_ladder.sh` run from the worktree `~/src/pm-run` (detached at
the branch head, so `GIT_REV` is a real rev). Output in `~/var/motley-ladder/`.

    started   2026-08-20 10:38 EDT
    check     tail ~/var/motley-ladder/timings.txt
    done      the line "LADDER COMPLETE H=1..19 Nmax=41"

It runs **tallest height first** on purpose: H = 19 is the one that can fail on
RAM, and discovering that after eighteen cheap heights have run is the wrong
order.

**Measured, not predicted** (the file's earlier estimates were ~59 GB and
~1.8 h per prime; both are now real numbers):

    census H=19 N=41   wall 1824.75 s   rss 22.45 GB
    H=19 p=65521       wall 5622.86 s   rss 63.03 GB      <- prime 1 of 9, DONE
    H=19 states        224,529,648      (Nmax-independent, as it must be)

So H = 19 is ~14.1 h for its nine primes; heights 18 down to 1 add roughly
another 63% of that, which is where the ~25 h total comes from.

**Pacing confirmed at 15:13.** Prime 2 ran 12:43 → 14:16, i.e. ~5,580 s
against prime 1's 5,622 — the per-prime wall is flat, as it must be. Prime 3
started 14:16 and was 3,411 s in at 15:13. Nine primes at ~5,600 s puts H = 19
finishing ~01:15 on 08-21 and the whole ladder ~10:00–11:30, which is what the
table says. Note the **worker pid changes with every prime** — the script pid
2865283 is the stable one; a worker pid from an earlier reading being absent
from `ps` is normal and is not a dead job. Read `timings.txt` heartbeats
instead.

**Why it matters.** `T(n,H) = C_H - 2C_{H-1} + C_{H-2}` needs every `C_H` at
the SAME Nmax, and every banked Motley row stops at n = 40. So today a(41) has
no second program anywhere in it. This ladder is what gives it one, and it
closes a(40)'s last cell in the same pass.

### What to do when it finishes

**1. Reconstruct the exact rows** (each height's nine residue rows -> one exact
row; eight primes reconstruct, the ninth is held out and must predict
correctly, and the tool exits non-zero if it does not):

    cd ~/src/pm-run
    python3 scripts/motley_crt.py --selftest        # against banked C_18 first
    for H in $(seq 1 19); do
      python3 scripts/motley_crt.py --dir ~/var/motley-ladder --height $H \
        --nmax 41 --out ~/var/motley-ladder/C$H.out
    done

**2. Bring them into the repo** as a distinct row set — do NOT overwrite
`results/cutcount_b1/rows/`, which is Confetti's Nmax-40 set and is cited all
over the tree:

    results/cutcount_b1/rows41/C1.out .. C19.out

**3. Ask the tower what it can now prove.**

    python3 experiments/undertow_ri.py --hmax 19 --jmax 4 \
            --rowdir results/cutcount_b1/rows41 --rows 39,40,41

**Expected, and the point of the whole exercise:**

- row 40 -> `COMPLETE, sum MATCHES a(40)` — with `GAP []`, not `GAP [19]`.
  That is a(40) confirmed in all forty cells by a second program.
- row 41 -> `COMPLETE`, and the sum must be
  **393811462683918679824582849262105**.

If row 41's sum differs from that number, **stop**: two independent programs
disagree, and that is the most important result the project could have. It
would mean either the sweep or the tower is wrong, and `results/a41/` plus
`results/undertow-review-A.md` are where to start.

**4. Cross-check the one cell that mattered.** `T(40,19)` from the new rows
must equal the incumbent's `results/ns_a40/perheight/h19.out` value at n = 40.

---

## 2. `cell_sparsity_modp.py` (ayr) — Skeleton Key probe 1

ayr, tmux session 0, window `skelkey`. Appends one line per height to
`~/var/skeletonkey/cellsparse.txt` and flushes, so a kill costs only the height
in flight.

**Overdue but healthy.** Its own header predicted "H=8 ~5-15 min and ~2 GB";
at 15:13 it was 2 h 46 min into H = 8 at **7.1 GB** and climbing (4.6 GB at
14:09), on a box with 70 GB free. Slower and fatter than predicted, not stuck.
Heights 4..7 are already banked in the file. The prediction in its own header
is the thing that was wrong, and the write-up should say so.

**What it settles.** A-S1 (`git show
second-source:results/scaling-exploration-A.md`) rejected the rank-compressed
engine on compute, assuming the compressed transfer is DENSE (`d²`), and named
sparsity as its one unprobed rescue. Exact Change measured that sparsity in
GF(2) only. This is the characteristic-0 measurement.

**The reading, from H ≤ 7 — provisional until H = 8 lands.** Sparsity is real
in char 0: row weights 1.06→1.77 (`A_0`) and 1.75→2.19 (`A_1`) against a dense
`d/2 = 346` at H = 7. But the rescue fails one level up. The compressed
dimension `d_p` runs 32, 99, 249, 692 at H = 4..7 — growth ~2.78×/height —
against the column frontier's ~2.55×, so it starts at ~0.6× the object it would
replace and closes that gap at ~1.09×/height, crossing over near H ≈ 14 and
sitting ~2× worse by H = 21. **A-S1's "crossover: never" survives, but not for
the reason A-S1 gave.**

Note when reading the file: its `cellstates` column is a *presentation* size,
not a live-state count — it is exactly `colstates × (2^H − 1)` at every height
(300/20 = 15, 1550/50 = 31, 7938/126 = 63, 40894/322 = 127). Do not divide by
it to get a speedup ratio; that error was made once in this session and
corrected.

**When it lands:** append the H = 8 row's `d_p` to the growth series above,
confirm or correct the ~2.78× figure, and write
`results/skeletonkey-cell-sparsity.md` — which
`docs/skeletonkey-reprompt.md` already cites as planned, so `gate-citations`
is waiting for it. If H = 8 breaks the trend, the whole reading above is what
changes.

---

## 3. `parametric_master.py 4` (ayr) — relaunched properly at 14:28

The ssh-launched run died inside `solve_H("hex", 4)` having printed only the
square line, with no way to tell which cluster it was on. Relaunched in tmux
window `pm4`, pid **641839**, logging to
`~/var/skeletonkey/parametric_master_k4.txt`; the probe now prints each cluster
weight with its wall time, so progress has a denominator (15 clusters at
K = 4) and a hung run is distinguishable from a slow one.

**Landed already:**

    square  A_k = 4, -19, 472/3, -3099/2      matches the banked table
    hex     A_k = 9, -37/2, 32, 3915/4        first three banked; A_4 new

**Still running: king**, whose four-row clusters are the expensive ones —
measured `hex (2,2,2,2) = 1154 s`, and king runs about 4× hex per cluster
(`king (2,2,2) = 47.3 s` against `hex (2,2,2) = 11.4 s`), so ~2 h for the leg.

**King `A_4` must come out `-22701/4`.** That is not a prediction any more:
`--wired-only` reads the king cumulants straight off the wired `P_k` table,
which shares no code with the cluster weights. If it disagrees, one of the two
routes is wrong and that is the result, not the `A_4` value. Hex `A_4 = 3915/4`
has no such check — there is no wired hex table.

Banked from the wired route while this ran (`results/skeletonkey-parametric-master.md`):
king `A_k`/`B_k` to `k = 19`, and the linearity cancellation as an audit of the
production `P_k` table — 171 coefficient cancellations, RED green, with the
blind spot (constant and `n¹` terms are invisible to it) asserted by its own
control rather than left to be assumed.

---

## Closed since 14:10, so it is not re-derived

- **L3-3 (the fattening bijection) is CLOSED** —
  `results/skeletonkey-l3-3-fattening.md`. It was the one row
  `skeletonkey-reprompt.md` called actually open. The construction turns out to
  be **sound**: under a lex filling convention the image is pinch-free and the
  map injective over all 176,138 king animals to n = 8, with a proof rather
  than a measurement (a block is the lex-larger candidate at its own
  bottom-left corner, never wins that mark, and so is never completed by marks
  — full blocks are exactly the animal). It dies on what the working
  construction costs, and that kill generalised into **the bijection test** now
  at the top of the v2 prompt.
- **Gate K generalised** from k = 3 to every k the wired `P_k` table reaches,
  and the linearity cancellation banked as a 171-condition audit of the
  production table, RED green with its blind spot asserted by its own control.
  King `A_k`/`B_k` to k = 19 are in `results/skeletonkey-parametric-master.md`.
  `--selfcheck` verifies the fit against the moment-cumulant expansion at
  k = 2, 3, 4.
- **The v2 prompt exists** — `docs/skeletonkey-reprompt.md`. Its instruction is
  "do not run another breadth pass"; use the three boxes and three tests.

## After that — decisions, not chores

Ordered by what they buy:

- **H = 20 sweep at Nmax 41** (`scripts/dalby_a41_h20.sh`, ~11 h, ~190 GB).
  The one formula the tower relies on that has no redundancy is fixed by two
  data points with nothing left over. This run produces a directly computed
  value it can be tested against. It is the last soft spot in the construction.
  **Sharpened 2026-08-20**: `docs/lastditch-ideas.md` §1a's correction proves
  that redundancy *cannot* come from another below-onset cell — each brings its
  own unknown `D_j(k)` — so a directly computed value or another ab-initio
  depth is the only way to buy it. That is the argument for this run.
- **Depth 5** (`families 21 4`, ~19-30 GB on the measured same-thread slope).
  Gives that formula a second, independent pair of data points.
  `experiments/severance_w3_depth5_gate.py` is already written, red-first.
- **The five-terms sweep** (`docs/five-terms-plan.md`) — jasonp's call; not
  launched.
- **The reach merge, PARKED** — `results/skeletonkey-nfamily-merge.md`.
  Established and banked, nothing built, parked at jasonp's direction. When
  unparked, cheapest first: a C++ key-space census to H = 18..21; then the
  congruence written down properly; then the build, which is one call in
  `kinkFinalizeColumn`.

## Standing rules that came out of these sessions

- **Code reaches ayr and dalby by `git pull` and nothing else.**
  `docs/engineering-standards.md` §5.
- **Push on every commit.** The pre-push hook runs the full gate suite.
- **Anything over five minutes goes in a tmux window** — `tmux new-window
  -t 0: -n <name>`, with the colon; bare `-t 0` fails with "index 0 in use".
- Closed doors, each with a counterexample, are in `docs/lastditch-ideas.md`
  §6 and §2, and the twenty-row breadth pass with its kills is in
  `docs/skeletonkey-reprompt.md`. Do not re-pitch the dual-connectivity
  transfer matrix, the per-level span cap, depths 8-9, the column-numerator
  audit, or P-finite `D_j` fitted from banked cells.
