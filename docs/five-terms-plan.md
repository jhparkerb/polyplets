# Five terms from one sweep — the a(41)..a(45) proposal

2026-08-20, branch `lastditch`. Not launched. This is the pitch, with the
numbers it rests on and the ones it is still waiting for.

## The claim

With exact below-onset depths through `J` and a real sweep of heights
`H <= Hs` at `Nmax = N`, Undertow (`results/undertow.md`) pins level `k`
whenever two depths `j1 < j2 <= J` satisfy `H' = k+1-j <= Hs`, so

    k_max = Hs + J - 2,     rows complete for   n <= 2*Hs + J - 1.

Depths 1..4 are closed (Severance W3) and the a(40) run already swept
`Hs = 21`. At `J = 4` that reads **`n <= 45`**.

So: one sweep of heights 1..21 at `Nmax = 45` yields rows 41, 42, 43, 44 and
45 — five new terms of A006770 — against the classical rule's one.

## Why it is not the usual 4.4x per term

The ladder's measured 4.4x per term is the cost of raising `Hs` **and** `Nmax`
together. Undertow lowers `Hs`, so what matters here is the cost of raising
`Nmax` alone, at fixed height. Measured on dalby, `scripts/nmax_scaling.sh`,
8 cores, one height at a time:

| height | Nmax 40 | Nmax 42 | Nmax 45 |
|---|---|---|---|
| 14 | 300.6 s | 336.9 s | (running) |
| 15 | (running) | (running) | (running) |

`+2` on `Nmax` costs **1.12x** in wall and 1.14x in CPU at H = 14 — an
exponent near `N^2.3`, so `40 -> 45` should cost about **1.3x**, not 4.4x per
term. The frontier at a fixed height is bounded by that height's own state
space; only the column count, the payload width and the completion prune
follow `Nmax`.

**This table is the whole proposal.** If the H = 15 row disagrees with the
H = 14 row — if the exponent climbs with height — the extrapolation to H = 21
is not safe and this plan reduces to a(41) alone.

## Cost, if the scaling holds

Against the a(40) run (`results/ns_a40/PROVENANCE.md`): phase A (H1-19,
80 cores) 6.3 h, phase B (H20 solo, 48 cores) 9.6 h, phase C (H21 solo,
32 cores) 36.4 h, disk peak 363.4 GB. At 1.3x:

- wall ~68 h across the same three phases, so **3 days on dalby**;
- disk peak ~470 GB against 542 GB free — tight, and the reason this must
  stay phased exactly as a(40) was, not run with full overlap;
- RAM unchanged (kink is RAM-light; rss_max was ~4 GB at the H21 pole).

## What each new level rests on

The sweep supplies every pinning cell, so the tower's new levels are pinned
from real swept data and — this is the part the a(41)-only plan could not do
— most of them get a **real holdout**:

| level | pinning pairs available | predicts, as a holdout | needed for rows |
|---|---|---|---|
| k=20 | 6 (j = 1..4) | in-onset cells of rows <= 42 | 41..45 |
| k=21 | 6 (j = 1..4) | `T(41,20)`, `T(42,21)` | 42..45 |
| k=22 | 3 (j = 2..4) | `T(41,19)` | 43..45 |
| k=23 | **1** (j = 3,4) | nothing | 45 only |

So rows **41 through 44 are solidly founded**; row 45 additionally rests on a
level with a single pin pair and no holdout, and should be reported that way
or held back until depth 5 exists (`families 21 4`, measured ladder ~16 h /
~103 GB).

## What has to be true

1. The `Nmax` scaling exponent must not climb with height — the H = 15 row.
2. Disk must actually fit at the H = 21 pole at `Nmax = 45`. The a(40) log
   (`results/ns_a40/rundir_size.log`) gives 69 GB for H<=19, 172 GB for H=20
   and 363 GB for H=21 at `Nmax = 40`; the same profile at 1.3x is the
   projection, and it is a projection.
3. `runs/a41_low` (~200 GB) has to be harvested and cleared first.
4. The assembly is `experiments/undertow_a41.py`, which reassembled a(40),
   a(39), a(38) and a(37) exactly from short sweeps before being pointed at
   anything new.

## The other target: a(41) TWO-SOURCED FROM BIRTH

Separate from the five-term plan and cheaper. The project's two-algorithm
frontier is n = 22 (`results/redelmeier_row22/`); every term since has been
single-sourced at birth and two-sourced later, if at all. Undertow plus the
parallel Motley makes a(41) two-sourced on the day it lands:

- **source 1**: the kink sweep, heights 1..19 at Nmax 41 (`runs/a41_low`,
  running), plus the tower for H >= 20;
- **source 2**: Motley heights 1..19 at Nmax 41, plus a tower pinned from
  Motley's own cells. With `hmax = 19` and `J = 4`, `k_max = 21`, so rows are
  complete for `n <= 2*19+3 = 41` — exactly reaching row 41, tower covering
  H >= 20 and Motley H <= 19.

Motley's cost at Nmax 41, from the measured parallel engine (H=14/Nmax 40 is
11.8 s at 80 threads; ~3.4x per height; ~1.1x for the Nmax bump): H=19 about
1.2 h per prime, H=18 about 0.35 h, everything below about an hour in total —
call it **15 h for the whole ladder across nine 16-bit primes** on dalby, or
the same split across dalby and ayr since the passes are independent.

Weak point, the same one as everywhere: level 21 pins from `T(40,19)` and
`T(39,18)` and has no third cell until depth 5 exists.

## What it is not

It is not a new counting algorithm — the sweep is the same kink engine that
produced a(30)..a(40). It is a change in **which cells the sweep has to
produce**, and the saving comes entirely from the tower reaching further down
than the onset-anchor rule allowed.
