# dmirror strip diagonals are quasi-polynomial (P_k for Hall of Mirrors)

2026-07-05. d(S, n) = diagonal-symmetric king-animals with n cells and bbox
exactly SxS (the dmirror strip counts). On the diagonal k = n - S, d(S, S+k)
is quasi-polynomial in S with **period 2** (off-diagonal cells pair under
the mirror), **degree k per parity class** (leading coefficient S^k/k! --
defect placement along the spine), and measured onset S0 ~= 2k+2 (even) /
2k+3 (odd).

Derivation: scripts/dmirror_diagonals.py over the per-strip farm outputs
(runs/sym26 built for this purpose + the n=32 farm's high strips). Exact
integer differencing; degree requires a 4-long constant tail; pinned on the
highest-S points; every point between onset and pin is a holdout hit;
strips computed AFTER pinning (dalby n=32 farm, different machine, hours
later) confirm forward.

| k | parity | P_k(S)                              | holdout | forward-confirmed |
|---|--------|--------------------------------------|---------|-------------------|
| 0 | even   | 2                                    | 12      | S=30, 32          |
| 0 | odd    | 2                                    | 11      | S=29, 31          |
| 1 | even   | S + 6                                | 9       | S=30              |
| 1 | odd    | S + 7                                | 9       | S=29, 31          |
| 2 | even   | S^2/2 + 7S + 12                      | 7       | S=30              |
| 2 | odd    | S^2/2 + 6S + 27/2                    | 6       | S=29              |
| 3 | even   | S^3/6 + 3S^2 + 40S/3 + 50            | 4       | (S=30 pending)    |
| 3 | odd    | S^3/6 + 7S^2/2 + 83S/6 + 93/2        | 4       | S=29              |

k=4 is degree 4 but its constant tail still spans pre-onset points at
S<=26 reach; the n=32 farm's S=26..28 strips (in flight) are the exact
points that clean and pin it.

## Why this matters (the n=33/34 ladder)

The sweep's cost is upside down in the sparse regime: strip S=31 at n=32
burned 223k cpu-s / 79GB (old engine) to produce d(31,31)=2, d(31,32)=38 --
the frontier is huge while the answer is tiny (admissible-but-loose debt
prunes keep doomed states alive). The P_k formulas replace exactly those
strips:

- n=33: strips S>=29 carry only k<=4 -> closed forms once P_4 pins;
  direct compute only S<=28 at maxn=33 (budget k<=5 strips, ~80GB class).
- n=34 bootstrap: the n=33 direct run adds k=5 points at S=26..28,
  pinning P_5; then n=34 = P_0..P_5 for S>=29 + direct S<=28 at maxn=34
  (S=28 budget k<=6, S=27 k<=7 -- the measured ~30-85GB class). No
  out-of-core shuffle, no OOM exposure.

Each new P_k must clear the same bar before use: constant tail, holdout
hits back to onset, and forward confirmation on at least one strip it did
not pin on.
