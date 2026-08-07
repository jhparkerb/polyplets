# Perimeter both-ends campaign — state, written to survive a `/clear`

2026-08-07. Hand this to a fresh session and it can pick up without re-deriving.
Findings live in `results/perimeter-both-ends.md`; this file is only the state.

## What this campaign is

`A(n,p)` has two boundary curves. `results/perimeter-defect-diagonals.md` graded
only from the maximum-perimeter end. This campaign grades from both, and the two
ends turn out to be different kinds of object: **triangular onset law at the max
end, linear at the min end**.

## Jobs in flight at the time of writing

**dalby** (80 cores, 125 GB; repo at `4aa9017f`, binary stamped clean
`6473890c`). tmux session 0, window `pdk6big`:

    ./scripts/dalby_perimeter_defect_pool.sh square8 78 6 456 76 14   <- RUNNING
    ./scripts/dalby_perimeter_defect_pool.sh square4 78 6 456 76 14   <- QUEUED

426/456 king shards done; the last ~30 are the heavy tail. On completion the
driver merges to `results/perimdefect_square8_n78_k6.txt` and **refuses to merge
unless all 456 shards reported `result=ok`**, so a partial run cannot be mistaken
for a complete one. Wait on it with `tail --pid`, never a poll loop
([[no-busywait-completion-loops]]).

**gympie** (10 perf cores): `perimeter_min square8 44 6 --threads 7` (extends the
king min ladder to p<=44, to overdetermine the odd-p columns at i>=2), plus two
`--only 15 15 {0,1}` square4 free-removal probes. All three were at 30-55 min.

## What k=6 buys, and how to read it when it lands

Four live predictions, all testable from `results/perimdefect_square8_n78_k6.txt`:

1. `onset(6) = 24` — the triangular onset law `T_k + 3`.
2. the `Phi_2` leading diagonal's `15/4` (`5(k-2)!/2^(k-1)` at k=6).
3. the `Phi_3` exponent `k-4` — **today that slope rests on a single data point**
   at k=5, so k=6 is what makes it a law or kills it.
4. `Phi_4` absent until k=7 (the `Phi_d first appears at k = 2d-1` law).

Run, in order:

    python3 experiments/perimeter_defect_denominator.py results/perimdefect_square8_n78_k6.txt --k 6
    python3 experiments/perimeter_max_structure.py results/perimdefect_square8_n78_k6.txt --lattice square8 --kmax 6

The denominator script needs far fewer points than a fit and answers 3 and 4 on
its own; it scans the onset too, so it also answers 1 independently of any
interpolation. It was validated against the known k=4 and k=5 answers.

n=78 was chosen because a period-6 degree-6 fit with two holdouts per class needs
54 points above onset 24, i.e. n to 77.

## Open, and NOT gated on dalby

- **Identify `1, 1, 3, 5, 9, 14`.** The per-tip 4th root of square4's diamond
  free-removal series `1, 4, 18, 60, 187, 524`. Its Euler-transform exponents
  come out `1,2,2,1,1` — irregular, so either it is not a clean product or the
  4-fold factorisation is the wrong model. Pure analysis, no compute.
- **tri6 at `PMAX=30`** to firm up `i>=1` (today `i=1` is stable on three points
  only in the `0 mod 6` class and on two points in the others). ~5 h single-core,
  ~30 min on 10 threads. Wants gympie idle.
- **Hexagon free-removals at `j=5,6`**: `--only 11 11 -1 5 15` (r=5, 91 cells)
  and r=6 (127 cells, just inside the 128 limit). Confirms `P(x)^6` past `j=4`.
  Single core each, minutes to ~1 h.
- **square4 free-removals at `j=6`**: needs `W=17`, 145 cells — **over the
  `kMaxCells = 128` u128 limit**, so it needs a wider connectivity mask first.
- **A full `make gates`** has not been run since the tri6 generalisation of
  `cpp/perimeter_min.cpp`. `gate-perimeter-min` and `gate-perimeter-defect` both
  pass; the rest is unverified against these changes. Wants gympie idle.
- **OEIS**: nothing here has been looked up. `1,4,18,60,187,524`,
  `1,6,25,88,272,766`, the per-tip `1,1,3,5,9,14`, `C(p,0) = 1,6,3,2,3,6` on
  tri6, and the stable square4 columns are all unchecked. Deliberately not run —
  external services are jasonp's call ([[publishing-is-jasonps-call]]).

## Gated on dalby

- `k=7`, the direct `Phi_4` test. ~12x k=6 per the measured ratio, so plan it
  only after k=6 lands and the pool driver's tail is understood.
- The bivariate `F(x,y) = sum_k G_k(x) y^k` rationality question, which needs
  `Ntilde_6` before six terms across two denominator regimes become seven.

## Tooling added this campaign (all gated)

| what | where |
|---|---|
| min-end enumerator, 3 lattices, hull = ranges on linear functionals | `cpp/perimeter_min.cpp` |
| its gate (RMAX unbounded vs g2 `--siteperim`, + RED control) | `scripts/perimeter_min_gate.sh`, `make gate-perimeter-min` |
| `--split S K IDX` for the max-end enumerator | `cpp/perimeter_defect.cpp` |
| its gate, check D = shards sum to the unsplit run | `scripts/perimeter_defect_gate.sh`, `make gate-perimeter-defect` |
| sharded production driver with a worker pool | `scripts/dalby_perimeter_defect_pool.sh` |
| onset law / recentred basis / numerator probes | `experiments/perimeter_max_structure.py` |
| denominator finder (few points, scans onset, tests minimality) | `experiments/perimeter_defect_denominator.py` |
| min ladder, both indexings | `experiments/perimeter_min_ladder.py` |
| min-end model vs the partition function | `experiments/perimeter_min_model.py` |
| attainability law + odd-p fits | `experiments/perimeter_min_attainability.py` |

## Two traps already paid for

- **The max-end numerator test is meaningless on the full `G_k`**, which carries
  a polynomial part holding the pre-onset holdouts. It must be run on the tail
  series from the onset. The first answer was noise.
- **(H1)** — every animal's perimeter is at least its own filled hull's — is what
  makes the min-end enumeration complete, and it is a hypothesis. It is checked
  at runtime and, more usefully, from outside by the gate. Do not weaken the
  gate; a violation surfaces only as a *missing* animal.
