---
name: ayr-job
description: Launch and monitor a long-running compute job on the ayr machine (32-core, 78 GB, gcc/x86) in a tmux window of session 0, with logging and a tail --pid waiter so the harness notifies on completion. Use when starting polyomino / hole-count / generating-function jobs on ayr (the big-RAM, cross-ISA partner to local gympie).
---

# Starting a job on ayr

**ayr**: remote Debian box, `ssh ayr` (key auth as `jhparkerb`). 32 cores, 78 GB,
gcc 12 / x86_64 (C++20). Repo at `~/polyominoes` (clone of
`github.com:jhparkerb/polyominoes`). It is the **cross-ISA partner** to local
gympie (clang/ARM) — re-running a computation here independently verifies it.
GPU is busy (`mtsieve` in tmux window 99) but CPU and RAM are free.

## Sync first
ayr pulls code from GitHub (do NOT git-fetch over ssh from gympie — ayr's shell
banner corrupts the git protocol). After committing+pushing from gympie:
```
ssh ayr 'cd ~/polyominoes && git pull -q --ff-only'
```
Rebuild if the engine changed (no -Werror; gcc is stricter than clang):
```
ssh ayr 'cd ~/polyominoes && c++ -std=c++20 -O3 -pthread cpp/tma_main.cpp -o build/tma_holes && c++ -std=c++20 -O3 cpp/gf_modp.cpp -o build/gf_modp'
```

## Launch in a NEW window of session 0
Session 0 (the user's, attached) holds: `0:htop`, `99:srsieve2cl` (GPU), and any
running job windows (e.g. `1:exact18`). **Never disturb existing job windows** —
the user input-locks them; only ever `tmux new-window` at a FREE index, and never
send keys to other panes. Pick a free index `<idx>`:
```
ssh ayr "tmux new-window -t 0:<idx> -n <name> 'cd ~/polyominoes && /usr/bin/time -v <command> > /tmp/<name>.log 2>&1'"
```
Then grab the pane pid (its exit == job done):
```
ssh ayr "tmux list-windows -t 0 -F '#{window_index} #{window_name} #{pane_pid}'"
```

## Completion waiter (no polling)
Launch as a backgrounded Bash task with run_in_background AND
dangerouslyDisableSandbox (network):
```
ssh -o ServerAliveInterval=30 -o ServerAliveCountMax=20 ayr 'tail --pid=<pane_pid> -f /dev/null'; echo "<name> FINISHED"
```
ssh stays open until the pane's process exits, then the task completes and the
harness notifies. **On notification, VERIFY the output file** before trusting it
(an ssh drop also ends the waiter early).

## Engine / recovery facts (avoid wasted runs)
- `tma_holes` MAXN cap is **4096**, and MAXN>64 requires `--modp P` (exact u64
  counts overflow). So large-N runs are mod-p only.
- mod-p GF recovery (`gf/hole_modp_recover.py`, `gf/modp_recover.py`) parallelizes
  the independent per-prime sweeps across cores — set `nprimes ~ order/110 + 12`.
- Hole-GF reach under the 4096 cap (order(H,k) ~ c_H*(k+1), c=6,20,68,185,537 for
  H=3..7): H=8 reaches only k=0; H>=9 / higher-k need a higher cap + long runs.
- `--hdrop` (drop holes>kmax) keeps RAM linear in N for slice recovery.

## After it finishes
Commit/push results from ayr (`git add ... && git commit && git push`) so gympie
can pull, or scp the output back. Reconcile `ledger/ledger.jsonl` if both machines
recorded runs (the old ayr clone is preserved at `~/polyominoes.bak.*`).
