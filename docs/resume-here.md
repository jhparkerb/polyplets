# Resume here — 2026-08-20, mid-morning

Written to survive a `/clear`. If you are picking this up cold:

1. **`results/confidence.md`** — how far each value of A006770 can be trusted
   and why, in plain terms. Read it first.
2. **`docs/lastditch-campaign.md`** — the campaign record behind it.
3. This file — the one job still running and exactly what to do when it lands.

---

## The job

**Motley ladder, heights 1..19, at Nmax 41.** dalby, tmux session 0, window
`ladder`. Script `scripts/motley_ladder.sh` run from the worktree
`~/src/pm-run` (detached at the branch head, so `GIT_REV` is a real rev).
Output in `~/var/motley-ladder/`.

    started   2026-08-20 10:38 EDT
    expect    ~25 h total
    check     tail ~/var/motley-ladder/timings.txt
    done      the line "LADDER COMPLETE H=1..19 Nmax=41"

It runs **tallest height first** on purpose: H = 19 is the one that can fail on
RAM, and discovering that after eighteen cheap heights have run is the wrong
order.

Measured so far: the H = 19 census gives **224,529,648 states** at Nmax 41 —
identical to Nmax 40, as it must be, since the state space depends on height
alone. Predictions to check the run against: **~59 GB** peak and **~1.8 h per
prime** at H = 19, nine primes per height.

**Why it matters.** `T(n,H) = C_H - 2C_{H-1} + C_{H-2}` needs every `C_H` at
the SAME Nmax, and every banked Motley row stops at n = 40. So today a(41) has
no second program anywhere in it. This ladder is what gives it one, and it
closes a(40)'s last cell in the same pass. An earlier launch of the same run at
Nmax 40 would have bought only the second and was killed for it.

## What to do when it finishes

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

**3. Ask the tower what it can now prove.** `--rowdir` points it at the new
set; `--hmax 19` because Motley now reaches that height:

    python3 experiments/undertow_ri.py --hmax 19 --jmax 4 \
            --rowdir results/cutcount_b1/rows41 --rows 39,40,41

**Expected, and the point of the whole exercise:**

- row 40 -> `COMPLETE, sum MATCHES a(40)` — with `GAP []`, not `GAP [19]`.
  That is a(40) confirmed in all forty cells by a second program.
- row 41 -> `COMPLETE`, and the sum must be
  **393811462683918679824582849262105**, the value computed this session by the
  first program alone.

If row 41's sum differs from that number, **stop**: two independent programs
disagree, and that is the most important result the project could have. It
would mean either the sweep or the tower is wrong, and `results/a41/` plus
`results/undertow-review-A.md` are where to start.

**4. Cross-check the one cell that mattered.** `T(40,19)` from the new rows
must equal the incumbent's `results/ns_a40/perheight/h19.out` value at n = 40.

## After that — decisions, not chores

Ordered by what they buy:

- **H = 20 sweep at Nmax 41** (`scripts/dalby_a41_h20.sh`, ~11 h, ~190 GB).
  The one formula the tower relies on that has no redundancy is fixed by two
  data points with nothing left over. This run produces a directly computed
  value it can be tested against. It is the last soft spot in the construction.
- **Depth 5** (`families 21 4`, ~19-30 GB on the measured same-thread slope).
  Gives that formula a second, independent pair of data points — agreement
  rather than a holdout, so weaker in kind than the sweep above, but cheap.
  `experiments/severance_w3_depth5_gate.py` is already written, red-first, and
  joins `GATE_TARGETS` the day the table exists.
- **The five-terms sweep** (`docs/five-terms-plan.md`) — a(41)-a(45) from one
  pass, disk-capped at Nmax 43 as things stand. jasonp's call; not launched.

## Standing rules that came out of this session

- **Code reaches ayr and dalby by `git pull` and nothing else.**
  `docs/engineering-standards.md` §5. No scp of source, no scratch trees. Both
  boxes are clean checkouts; dalby also has the `~/src/pm-run` worktree so a
  run's binary carries a real rev (the main checkout has untracked files that
  make every build there stamp `-dirty`).
- **Push on every commit.** The pre-push hook runs the full gate suite, which
  caught two real defects this session that no amount of local testing had.
- Closed doors, each with a counterexample, are in `docs/lastditch-ideas.md`
  §6 and §2. Do not re-pitch the dual-connectivity transfer matrix, the
  per-level span cap, or depths 8-9.
