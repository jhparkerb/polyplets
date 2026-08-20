# Resume here — 2026-08-20, 14:10 EDT

Written to survive a `/clear`. If you are picking this up cold:

1. **`results/confidence.md`** — how far each value of A006770 can be trusted
   and why, in plain terms. Read it first.
2. **`docs/lastditch-campaign.md`** — the campaign record behind it.
3. **`docs/skeletonkey-reprompt.md`** — the kill inventory and the twenty-row
   breadth pass, for the "beat n = 40" mission.
4. This file — the jobs still running and exactly what to do when they land.

---

## Jobs running, at 14:10 EDT

| host | job | pid | started | expect | output |
|---|---|---|---|---|---|
| dalby | Motley ladder H = 1..19 @ Nmax 41 | 2865283 (script), 2867331 (worker) | 10:38 | **~11:30 on 08-21** | `~/var/motley-ladder/` |
| ayr | `cell_sparsity_modp.py 8` | 640243 | 12:11 | overdue, healthy | `~/var/skeletonkey/cellsparse.txt` |
| ayr | `parametric_master.py 4` | 641483 | 13:49 | dies on its own `timeout 1500` at ~14:14 | stdout only, disposable |

Nothing here needs restarting. **Do not restart the ladder** under any
circumstance short of a dead box — see `a21-run-do-not-restart`.

---

## 1. The Motley ladder (dalby) — the important one

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
another 63% of that, which is where the ~25 h total comes from. Prime 2
(65519) was 87 min in at 14:09 and nearly done. `C19.p65521.out` is complete,
41 lines.

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
at 14:09 it was 102 minutes into H = 8 at 4.6 GB and 11.5 cores, on a box with
70 GB free. Slower than predicted, not stuck. Heights 4..7 are already banked
in the file.

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

## 3. `parametric_master.py 4` (ayr) — disposable

A fourth-order re-run of a probe whose K = 3 result is already banked in
`results/skeletonkey-parametric-master.md`. It carries its own
`timeout 1500` and dies at ~14:14 either way. It was launched over ssh rather
than in a tmux window, which was a mistake and is why it is marked disposable:
if the ssh dropped, it took SIGHUP with it.

**If it produced a fourth order**, square `A_4` must equal `-3099/2` — that is
the only k = 4 value banked anywhere — and the "NOT ESTABLISHED: k ≥ 4" bullet
in the results file comes out. **If it did not**, nothing is lost; K = 3 with
gate K is the banked result. Re-run it in a tmux window, not over ssh.

---

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
