# a(25) static-balance launch plan (turnkey)

A whole-height split across gympie+ayr+dalby that balances wall-clock from the
a(23) cost model. No cross-machine stealing (see border-raid.md — not viable on this
topology). **Not a go — a ready-to-fire plan.** Requires the FIXED binary (k≤7
injection + the 12 fixes) deployed on each box first.

## Inputs (measured at a(23))

Effective throughput (cpu_s/wall_s): **dalby 34.5, ayr 18.6, gympie ~7** cores.
With k≤7 injection a(25) **injects H18–25** (free, closed-form) and **sweeps H1–17**;
peak swept = **H17**. Per-height compute, a(23) measured × g² (g≈1.8 → 3.24):

| Height | a(23) core-h | a(25) est. core-h |
|---|---|---|
| H17 | 113 | **366** |
| H16 | 44.7 | 145 |
| H15 | 15.9 | 52 |
| H14 | 5.5 | 18 |
| H1–13 | ~4 | ~13 |
| **swept total** | 184 | **≈ 590** |

## The split (3-box, recommended) — wall ≈ 10.6 h @ g=1.8

H17 is the indivisible monster; cheapest on dalby (366/34.5 = **10.6 h**) — that sets
the floor. Balance the rest to match:

| Box | `--heights` | cores | work | wall |
|---|---|---|---|---|
| **dalby** | `17-25` | 80 | H17 swept; H18–25 injected (free) | **10.6 h** |
| **ayr** | `15-16` | 30 | 197 core-h | **10.6 h** |
| **gympie** | `1-14` | 10 | 28 core-h | 4.0 h (early) |

dalby and ayr land together at ~10.6 h; gympie clears the cheap tail and idles. The
floor is H17-on-dalby — can't beat it without splitting H17 (whole-height only).

**g-sensitivity:** g∈[1.5, 2.4] → wall **7.4–18.9 h**. Structure is fixed; only the
absolute wall moves.

## Home-only fallback (gympie+ayr, no dalby) — wall ≈ 27–32 h

If dalby is out: H17 → ayr (366/18.6 = 19.7 h), and the mid heights swamp gympie
(7 eff cores). Best balance ≈ ayr `15-25` (~27 h) / gympie `1-14` (~11 h) → ~27 h
(~1.1 days). Feasible but ~2.5× slower — dalby's 80 cores earn their keep on H17.

## Operational params (all boxes)

- Binary: **the fixed `next-system` build** — must include k≤7 injection (commit
  3742f36) + the fix batch. Deploy: cross-compile `orchestrate` on gympie
  (`CGO_ENABLED=0 GOOS=linux GOARCH=amd64`) for ayr/dalby; build workers native on
  each linux box; native build on gympie. (per ayr-newengine-crosscompile note)
- `--counter u64` — a(25) ≈ 6.6e18 < 2^64 (no CRT needed below a26).
- `--ram`: dalby `1073741824` (1 GB/worker), ayr `1073741824`, gympie `536870912`.
- `--unit-mult 4 --steal-grain 0.05` (intra-machine stealing on), `--checkpoint-every
  900`, `--per-height-out runs/ns_a25/perheight`, `--cost-profile-out ...`.
- Run each in a tmux window, foreground+tee, with a `tail --pid` waiter.

## Go commands (after binary deploy)

```
# gympie
orchestrate --maxn 25 --cores 10 --heights 1-14  --ram 536870912  \
  --run-dir runs/ns_a25/gympie --spill-dir runs/ns_a25/gympie/spill \
  --per-height-out runs/ns_a25/perheight --checkpoint runs/ns_a25/gympie/POLYCKPT \
  --checkpoint-every 900 --cost-profile-out runs/ns_a25/gympie/cost_profile.tsv \
  --unit-mult 4 --steal-grain 0.05
# ayr   : --cores 30 --heights 15-16 --ram 1073741824 ...
# dalby : --cores 80 --heights 17-25 --ram 1073741824 ...
```

## Combine → a(25)

Gather `perheight/h1..h25.out` from all three boxes into one dir; assemble
a(n)=Σ_H T(n,H) (as for a(23) in results/ns_a23). Cross-check a(20..23) match the
known values before trusting a(24), a(25).

## Caveats (read before firing)

1. **g is estimated** (no a(21) cost profile to pin it) — wall could be ~2× the
   10.6 h figure.
2. **k≤7 at n=24,25 is EXTRAPOLATION** — the diagonals are validated only through
   a(23); at a(25) the injected k≤7 cells are not swept anywhere, so there is no
   in-run check. This is an explicitly **unverified** push, not a certified record.
   A mod-p shadow run would catch arithmetic faults but not a broken extrapolation.
3. Wall floor is H17-on-dalby; if dalby is unavailable the home-only fallback is
   ~2.5× slower.
4. Confirm disk headroom for spill on each box (dalby had 346 GB free).
