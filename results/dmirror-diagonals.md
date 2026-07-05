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

## Coefficient structure (2026-07-05, follow-up)

Probing jasonp's conjecture that the S^(k-1) coefficient decomposes as
A - B (free placements minus a correction for impossible placements):

**Leading orders: confirmed, with a twist.** P_1 is the single-defect
census: one bulk weight-1 defect type (the S coefficient is exactly 1)
plus 6/7 corner variants. The naive independence prediction for k=2 even
is (S+6)^2/2! = S^2/2 + 6S + 18; the pinned polynomial is S^2/2 + 7S + 12.
Residual = +S - 6: the +S term is a genuine weight-2 bulk defect type that
no product of singles generates (the A side, and it is a NEW gadget, not
multinomial bookkeeping), and the -6 absorbs collisions/end effects (the
B side). So A - B is the right first cut at S^(k-1).

**The two-spine defect gas is falsified at k=3.** Exact parity
differences P_even - P_odd have degree 0, 1, 2 at k = 1, 2, 3 -- i.e.,
deg = k-1. A defect gas over the two ground spines (main diagonal:
transpose fixes every site, plain polynomial; anti-diagonal: defects come
in center-mirrored pairs) caps the parity-dependent degree at floor(k/2)
-- degree 1 at k=3, contradicting the measured 2. So additional
length-free families exist. Candidate: anti-diagonal EXCURSIONS -- odd-
length anti-diagonal segments crossing the main spine (transpose-
symmetric as a unit), reconnected by weighted clusters at both ends; the
excursion's length is free, so each one contributes a factor ~S at fixed
weight, and its odd-length constraint carries the parity sign. The full
derivation is a segment grammar (regular language over main-runs,
anti-excursions, connectors, defects), not a one-line gas -- paper-scale,
parked.

**Usable weak law**: deg(P_even - P_odd) = k-1 held at k=1..3; check it
on every future pin as a cheap structural alarm.

## Pattern hunt in the GF basis (2026-07-05, later)

The cumulants u_j, v_j of the exp fit (scripts/dmirror_pk_exp.py) are
messy -- expected, since they are the log of a SUM of families. The
patterns live in the rational-GF basis G_k(x) = sum_S d(S,S+k) x^S:

1. **Denominator law**: G_k = N_k(x) / ((1-x)^(k+1) (1+x)^k), N_k integer,
   deg 2k. Verified exactly k=0..5.
2. **Boundary values**: N_k(1) = 2^k and N_k(-1) = (-2)^k for all k>=1.
   Equivalently N_k - (2x)^k is divisible by (1-x^2). Reading: the
   dominant weight-1 defect family is TWO species per odd footprint
   (2(x+x^3+x^5+...) = 2x/(1-x^2) per defect), which integrates to the
   bulk density 1 seen as P_1's S-coefficient. jasonp's A-B leading
   structure, in closed form across all k.
3. **Second layer**: R_k = (N_k - (2x)^k)/(1-x^2) has R_k(1)/2^k =
   3,3,3,4,5 (k=1..5) and R_k(-1)/(-2)^k = k-3 exactly for k=2..5 --
   linear-in-k laws signalling a double pole at z=1/(2x) in the level
   variable, i.e. interacting defect pairs.
4. **Refusals (exact)**: no bivariate rational closure sum_k N_k z^k =
   P/D with z-deg(D) <= 3, x-deg <= 6 -- overdetermined Gaussian
   elimination contradicts. Each weight level carries genuinely NEW
   gadget species, exactly like the all-polyplet P_k family where every
   level needs its fresh cumulant pair (a_k, b_k). The pattern is the
   FORM (denominator law + boundary values + 2-per-level freshness), not
   a closed form across k.
