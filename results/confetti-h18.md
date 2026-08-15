# Motley rung 2 (Confetti) — H = 18, pass 1 of 5 done

Run started 2026-08-14 17:56 EDT on dalby, `docs/motley-plan.md` §"Rung 2".
Runner `scripts/dalby_confetti_h18.sh`; rows and logs under `~/var/motley-h18`.

**Status: IN PROGRESS.** Prime 1 of 5 (`p = 2147483647`) finished
2026-08-15 16:20 EDT; the driver started prime 2 two seconds later. Four
passes remain, sequential — nothing is assembled and no T(n,18) is claimed
until all five are in and the held-out check has run.

## Provenance

| | |
|---|---|
| binary | `~/src/pm-halfmeasure/build/cutcount_b1`, stamp `git=4df3fec9`, no `-dirty` |
| binary sha256 | `dd1732399703d5aa786e11c8b450fb2aa3a7af8dfd599906c79fb474193b883e` |
| receipt | `cutcount_b1.confetti-receipt`, `verdict=GREEN`, sha matches the binary as run |
| row | `~/var/motley-h18/C18.p2147483647.out`, 40 lines, n = 1..40 |

## Early check on pass 1 — 23/23

The full RED-D held-out check needs all five primes. What can be checked
today is the incumbent triangle read mod p: for each banked T(n,18) in
`~/var/motley-h17/triangle.txt`, predict

    C_18(n) ≡ T(n,18) + 2 C_17(n) − C_16(n)  (mod p)

against this pass's measured residue, using step-0 `C_16` and Half Measure's
`C_17`. **23 cells checked, 23 match, 0 mismatch.** This is a necessary
condition on one prime, not the product: it does not test the CRT
reconstruction, and it is blind to any error that is a multiple of p.

The `--modp` path prints no per-height `q0_zero` / `q1eval_binomial` lines —
those arithmetic self-checks appear in exact mode only, so `run.log` for this
pass carries the start, heartbeats and done event and nothing else.

## Cost, measured — the H = 18 point the ladder was waiting on

| quantity | H = 17 (u128, 3 streams) | H = 18 (u32, 2 streams, pass 1) |
|---|---|---|
| wall | 39,117 s (10.9 h) | **80,633 s (22.40 h)** |
| cpu | — | 80,584 s (99.94% of wall, one core) |
| peak RSS | 95.0 GB | **65.94 GB** |
| census | 23,681,423 | **72,487,711** |

Against the plan's Rung-2 pricing (~16 h/pass, ~82 h for five, ~83 GB peak):
wall is **×1.40 over** and RAM **×0.79 under**. Five passes now price at
**112 h** of single-core wall; the remaining four finish about
**2026-08-19 10:00 EDT** if pass 1's rate holds.

**Census ratio ×3.0610** over H = 17, against the ladder constant 2.984 and
Half Measure's measured 3.023 — a 2.6% departure. The kill condition
(20% departure stops the ladder before Ticker Tape) does not fire.

**Residue speedup, the number Ticker Tape was blocked on.** Priced at ~0.47×
the u128 wall from H = 12, 13; measured here at **0.645×**
(80,633 s against the 125,096 s an H = 18 u128 pass projects to from H = 17
at the measured ×3.198/height). The speedup is real but 37% smaller than the
small-height timings said.

**Peak RSS per window is 909.7 B**, against the modelled 598 (328 B u32
payload + ~270 B container). The same comparison at H = 17 is 4,012 B
measured against 2,238 modelled. Both heights sit 1.5–1.8× above the model,
so the peak carries something the per-window model does not — the fan-out
transient is the obvious candidate, unmeasured here.

## What this does to Ticker Tape's price

Carrying the measured H = 18 modp wall up one height at ×3.198 gives
**71.6 h per H = 19 pass**; nine passes is **27 days** of single-core wall,
and the ST 3 → 2 check-split the rung cannot do without adds half again:
**~40 days**. That is the bad end of the plan's "2–8 weeks" band, and it
arrives before the flat-arena rewrite, which the 909.7 B/window measurement
says has further to travel than the design note assumed (target ~57 B is a
16× cut from today's measured, not the ~10× modelled).

Neither number is a decision yet — Confetti has four passes to run first.
