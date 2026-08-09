# Three structural probes of the uncovered middle band (all NEGATIVE, one caution)

2026-08-09, companion to `results/slope-slicings.md`. That file asked whether
the band hides a P_k-analogue (polynomial x exponential) and found nothing.
These three probes ask for structure of a *different kind* — exact p-adic,
exact determinantal, and finite-size-scaling — on the same banked data.
`experiments/band_structure.py`. Every probe carries a control that must be
recognised and a structureless control that must be rejected.

## 1. p-adic valuations — nothing

`v_p(T(2H,H))` for p = 2, 3, 5, 7 over H = 1..20, against the generic
expectation for an unstructured integer sequence (v_p iid geometric, mean
1/(p-1)).

| sequence | v_2 mean | v_3 mean | v_5 mean | v_7 mean |
|---|---|---|---|---|
| generic expectation | 1.00 | 0.50 | 0.25 | 0.17 |
| **slope-2 T(2H,H)** | 0.50 | 0.60 | 0.15 | 0.00 |
| control: Catalan | 1.10 | 0.60 | 0.55 | 0.30 |
| control: s=1 k=2 (quadratic x 3^H) | 1.15 | **6.85** | 0.20 | 0.35 |

The probe works: the s=1 k=2 control's 3-power is unmistakable, its v_3 growing
linearly (0, 3, 0, 0, 0, 2, 4, 3, 5, 6, 6, 10, 9, 9, 11, 13, 12, 14, 15, 15).
The slope-2 slice shows nothing of the kind at any of the four primes. Its
v_7 = 0 throughout is the only oddity and is not significant: P = (6/7)^20 =
0.046 for one prime, and four were tested.

Caveat on the structureless control: it was built as `round(41.85^H H^-0.25)`
in floating point, so its v_2 mean of 16 is an artifact of float mantissas, not
a property of the sequence. Read that row as "not a valid null" rather than as
a signal.

## 2. Hankel determinants — no J-fraction, and a bonus recurrence bound

`det[S(i+j)]_{0..m-1}` computed exactly. A sequence with a Stieltjes/J-fraction
(Catalan, Motzkin, directed animals) has tiny or highly smooth Hankel
determinants; an unstructured one has determinants growing in digit count with
large non-smooth cofactors.

| m | slope-2 det digits | cofactor digits after removing primes < 10^4 | structureless control |
|---|---|---|---|
| 3 | 7 | 1 (smooth) | 11 -> 1 |
| 5 | 21 | 15 | 28 -> 24 |
| 7 | 45 | 43 | 54 -> 51 |
| 9 | 76 | 75 | 87 -> 83 |

Catalan returns det = 1 at every m, as it must. The slope-2 profile is the
structureless one: **no J-fraction, no Stieltjes moment structure.**

Bonus, and worth keeping: the s=1 k=2 control's Hankel determinants **vanish
from m = 6 onward** — the fingerprint of a linear recurrence of order 5, which
is exactly the minimal order measured for that slice in
`results/slope-slicings.md`. The slope-2 determinants are nonzero through m = 9,
which independently proves its minimal C-finite order is **>= 9**, a slightly
stronger statement than the order-8 search there.

## 3. Finite-size scaling of mu_H — a fit that would have misled us

The certified strip growth constants (`results/strip-mu-certificates.md`,
H = 2..17) against `mu_H = lambda - c H^{-x}`, fit on H = 6..15, holdout
H = 16, 17. lambda = 7.110(1) is known independently
(`results/series-analysis-da.md`).

| lambda | x | c | holdout max rel err |
|---|---|---|---|
| 7.108 (pinned) | 1.2043 | 17.63 | 0.303% |
| 7.110 (pinned) | 1.2021 | 17.58 | 0.300% |
| 7.112 (pinned) | 1.2000 | 17.52 | 0.297% |
| **free** | **1.0017** | 13.44 | **0.010%** at **lambda = 7.334** |

Control: on synthetic data generated from the model exactly (x = 1, c = 9), the
fit returns x = 1.0000 with 0.000% holdout, so the machinery is sound.

**The caution.** Letting lambda float buys a 30x better holdout and returns
lambda = 7.334 — 3% away from a value known to 1 part in 7000, and far outside
its error bar. A three-parameter fit with a 1e-4 predictive residual is
therefore capable of being badly wrong here, in the same way the free-theta
fits were in `slope-slicings.md`. With lambda pinned to its true value the
residual is 0.3%, i.e. **the pure power-law correction is not the right form**;
there is further structure in the ladder that this ansatz does not capture.

The honest reading: `x ~ 1.2` at pinned lambda, with a form error large enough
that neither x = 1 nor x = 3/2 can be excluded, and no conclusion at all about
lambda from this route.

## What all three share

None of them found structure in the middle band, and the two that could have
(valuations, Hankel) are exact-integer tests that cannot be talked into a
positive by a good fit. That matters more than another asymptotic null: the
band's cells are not merely hard to summarise asymptotically, they carry no
detectable arithmetic or determinantal structure either.

## 4. q-holonomic recurrences — none (this one closes a real gap)

2026-08-09, `experiments/qholo_automatic.py`. Earlier searches allowed
coefficients polynomial in H only. Note first what is *not* a gap: a global
factor `q^H` is invisible to those searches by design, because C-finite and
P-finite are invariant under geometric rescaling (the factor multiplies
coefficient `c_i` by `q^{-i}` and changes nothing). "3^H times something
P-finite" was therefore already covered by `results/slope-slicings.md`.

The genuine gap is `q^H` *inside* the coefficients:
`sum_i c_i(H, q^H) S(H-i) = 0`. Searched with q in {2,3,5}, r <= 3, degrees in H
and in q^H bounded by the slack rule, onsets 0..3, last two points held out.

| sequence | result |
|---|---|
| control `S(H+1) = (2^H+1) S(H)` (genuinely q-holonomic) | **found**: q=2, r=1, d=0, B=1 |
| control s=1 k=2 | found, B=0 (degenerate to constant coefficients, correct) |
| **slope-2 T(2H,H)** | **none** |

Envelope, set by the 20 points: r=1 permits (d+1)(B+1) <= 7; r=2 permits <= 4;
r=3 permits <= 3.

## 5. Residues mod m — no eventual periodicity, and the test's own limit

Same script. `S(H) mod m` for m = 2,3,4,5,7,8,9,11, asking for eventual
periodicity with period <= 6 starting by index 8 (>= 2 full periods plus a
holdout).

- Control s=1 k=2 fires as it must: period 4 mod 2, and identically 0 mod 3 and
  mod 9 from index 5 — the 3^H factor showing itself.
- Slope-2: **no short period at any modulus tested.**

**The honest limit, and it matters.** The Catalan control ALSO returns "no short
period" — yet Catalan mod 2 is a textbook 2-automatic sequence (nonzero exactly
at n = 2^k - 1). So this test detects periodicity, not automaticity, and a known
automatic sequence passes straight through it. Deciding automaticity needs a
p-kernel test, which needs far more terms than 20. **The automaticity question
raised in `results/slope-slicings.md` is therefore NOT closed by this run**, and
cannot be closed on banked data.
